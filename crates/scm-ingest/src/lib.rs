//! Telemetry ingestion core: **normalize → validate → deduplicate → batch** (ADR-0036).
//!
//! Ingestion is core work (ENG-R10), so this crate contains **no transport**: no HTTP server, no
//! ClickHouse client, no async runtime. It takes samples in, hands batches out, and takes **time as
//! an input** rather than reading a clock — which is what makes every behaviour here testable
//! without a scheduler and reproducible without a fixture of wall-clock luck.
//!
//! The one decision ADR-0036 calls the most important in ClickHouse ingest is **batching**, and it
//! is the whole reason this crate exists: row-by-row inserts are what turns a working cluster into
//! a broken one.
//!
//! # Policy values
//!
//! Every threshold here — window, batch size, flush interval, accepted clock skew — is a
//! **constructor argument with no default**. A default in a signature is how one deployment's
//! tuning becomes every deployment's inheritance (ADR-0037), and this crate is where that would be
//! easiest to do by accident.

use std::collections::hash_map::DefaultHasher;
use std::collections::{HashSet, VecDeque};
use std::fmt;
use std::hash::{Hash, Hasher};

/// A single telemetry sample, before normalization.
///
/// `ts_ms` is a Unix millisecond instant in **UTC** (SCM-R9). Labels are plain `String` rather than
/// `Option<String>` because ADR-0036 forbids `Nullable` on the hot columns: absence is the empty
/// string, decided once here rather than at every call site.
#[derive(Debug, Clone, PartialEq)]
pub struct Sample {
    pub project_id: String,
    pub metric: String,
    pub ts_ms: i64,
    pub value: f64,
    pub environment: String,
    pub unit: String,
}

/// Why a sample was rejected. Counted per reason, because "we dropped 4,000 samples" is not
/// actionable and "we dropped 4,000 samples for `UnknownMetric`" names the broken emitter.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum RejectReason {
    /// No project identifier after trimming.
    MissingProjectId,
    /// No metric name after trimming.
    MissingMetric,
    /// The metric is not in the governed set (a `CPT-*` node must define it — ADR-0036).
    UnknownMetric,
    /// NaN or infinity. A non-finite value poisons every aggregate downstream.
    NonFiniteValue,
    /// Timestamp further from `now` than the accepted skew, in either direction.
    TimestampOutOfWindow,
    /// Already seen within the deduplication window.
    Duplicate,
}

impl fmt::Display for RejectReason {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        let text = match self {
            Self::MissingProjectId => "missing project_id",
            Self::MissingMetric => "missing metric",
            Self::UnknownMetric => "metric not in the governed set",
            Self::NonFiniteValue => "value is not finite",
            Self::TimestampOutOfWindow => "timestamp outside the accepted skew",
            Self::Duplicate => "duplicate within the dedup window",
        };
        formatter.write_str(text)
    }
}

/// Counts of rejected samples by reason. Monotonic; never reset by the pipeline itself.
#[derive(Debug, Default, Clone, PartialEq, Eq)]
pub struct RejectCounts {
    counts: Vec<(RejectReason, u64)>,
}

impl RejectCounts {
    fn record(&mut self, reason: RejectReason) {
        if let Some(entry) = self.counts.iter_mut().find(|(kind, _)| *kind == reason) {
            entry.1 = entry.1.saturating_add(1);
        } else {
            self.counts.push((reason, 1));
        }
    }

    /// How many samples were rejected for one reason.
    #[must_use]
    pub fn get(&self, reason: RejectReason) -> u64 {
        self.counts
            .iter()
            .find(|(kind, _)| *kind == reason)
            .map_or(0, |(_, count)| *count)
    }

    /// Total rejected, all reasons.
    #[must_use]
    pub fn total(&self) -> u64 {
        self.counts.iter().map(|(_, count)| *count).sum()
    }

    /// Every reason that has occurred, with its count — for emitting as operational metrics.
    pub fn iter(&self) -> impl Iterator<Item = (RejectReason, u64)> + '_ {
        self.counts.iter().copied()
    }
}

/// Trims the label fields and collapses absence to the empty string.
///
/// Normalization is separate from validation on purpose: `"  build.duration  "` is a *valid* metric
/// that needs cleaning, while `""` is invalid. Merging the two steps makes it impossible to tell
/// which of those happened.
#[must_use]
pub fn normalize(mut sample: Sample) -> Sample {
    sample.project_id = sample.project_id.trim().to_owned();
    sample.metric = sample.metric.trim().to_owned();
    sample.environment = sample.environment.trim().to_owned();
    sample.unit = sample.unit.trim().to_owned();
    sample
}

/// Deduplicates on `(project_id, metric, ts_ms)` within a bounded time window.
///
/// # Why a window, and why it is bounded
///
/// Duplicates come from **retries**: a sender that did not see the acknowledgement sends again,
/// seconds later. So the window only has to outlive the worst retry, and an unbounded set would
/// grow forever to catch duplicates that in practice never arrive.
///
/// Memory is bounded by construction: `window_ms / bucket_ms` buckets, each holding the hashes seen
/// in that slice of time. Eviction drops a whole bucket at once, which is why it is O(1) amortized
/// rather than a scan for expired entries.
///
/// # The hash trade-off, stated rather than hidden
///
/// Keys are stored as a **`u64` hash**, not as the original strings: eight bytes instead of roughly
/// sixty, which at tens of thousands of series is the difference between a bounded worker and a
/// memory problem. The cost is a false-positive rate — two different keys hashing alike would drop
/// one real sample. At a million live keys that probability is about `2.7e-8` per key pair
/// (birthday bound over 2⁶⁴), and the consequence is one missing telemetry point.
///
/// **That trade is acceptable here and would not be for money.** A dropped sample perturbs an
/// average; a dropped ledger entry is a wrong balance. `scm-money` therefore stores no hashes.
#[derive(Debug)]
pub struct Deduplicator {
    window_ms: i64,
    bucket_ms: i64,
    /// Ordered oldest → newest. Each entry is (bucket index, hashes seen in that bucket).
    buckets: VecDeque<(i64, HashSet<u64>)>,
    newest_bucket: Option<i64>,
}

impl Deduplicator {
    /// `window_ms` must outlive the worst expected retry; `bucket_ms` trades eviction granularity
    /// against bucket count. Neither has a default — see the crate note on policy values.
    ///
    /// # Panics
    /// If either duration is not positive, or the window is shorter than one bucket. These are
    /// programming errors at construction, not runtime conditions.
    #[must_use]
    pub fn new(window_ms: i64, bucket_ms: i64) -> Self {
        assert!(window_ms > 0, "dedup window must be positive");
        assert!(bucket_ms > 0, "dedup bucket must be positive");
        assert!(
            bucket_ms <= window_ms,
            "a bucket cannot be longer than the whole window"
        );
        Self {
            window_ms,
            bucket_ms,
            buckets: VecDeque::new(),
            newest_bucket: None,
        }
    }

    fn key_hash(project_id: &str, metric: &str, ts_ms: i64) -> u64 {
        let mut hasher = DefaultHasher::new();
        project_id.hash(&mut hasher);
        metric.hash(&mut hasher);
        ts_ms.hash(&mut hasher);
        hasher.finish()
    }

    /// Returns `true` if this sample is a duplicate; otherwise records it and returns `false`.
    ///
    /// A sample older than the window is **not** reported as a duplicate — it is simply not
    /// tracked, because claiming "duplicate" about something we can no longer know would be a lie.
    /// Rejecting stale data is the validator's job, which keeps the two answers separable.
    pub fn is_duplicate(&mut self, sample: &Sample) -> bool {
        let bucket = sample.ts_ms.div_euclid(self.bucket_ms);
        let newest = self
            .newest_bucket
            .map_or(bucket, |current| current.max(bucket));

        // Evict whole buckets that fall outside the window relative to the newest instant seen.
        let oldest_kept = newest - (self.window_ms / self.bucket_ms);
        while let Some((index, _)) = self.buckets.front() {
            if *index < oldest_kept {
                self.buckets.pop_front();
            } else {
                break;
            }
        }
        self.newest_bucket = Some(newest);

        if bucket < oldest_kept {
            return false; // beyond memory; the validator decides whether it is acceptable at all
        }

        let hash = Self::key_hash(&sample.project_id, &sample.metric, sample.ts_ms);
        if let Some((_, seen)) = self.buckets.iter_mut().find(|(index, _)| *index == bucket) {
            return !seen.insert(hash);
        }
        let mut seen = HashSet::new();
        seen.insert(hash);
        // Buckets arrive in near-order, so pushing back and sorting only on the rare out-of-order
        // insert keeps the common path free of comparisons.
        self.buckets.push_back((bucket, seen));
        if self.buckets.len() > 1 {
            let last = self.buckets.len() - 1;
            if self.buckets[last - 1].0 > self.buckets[last].0 {
                self.buckets
                    .make_contiguous()
                    .sort_by_key(|(index, _)| *index);
            }
        }
        false
    }

    /// Buckets currently retained — the memory bound, observable for operational metrics.
    #[must_use]
    pub fn bucket_count(&self) -> usize {
        self.buckets.len()
    }
}

/// Accumulates accepted samples and flushes on **size or age, whichever comes first**.
///
/// Size alone starves a low-traffic project: its samples sit unsent until enough accumulate, which
/// may be never. Age alone lets a batch grow without limit under load, and an enormous `INSERT` is
/// what ClickHouse handles worst. Both together bound each failure the other allows.
#[derive(Debug)]
pub struct Batcher {
    max_samples: usize,
    max_age_ms: i64,
    pending: Vec<Sample>,
    oldest_pending_ms: Option<i64>,
}

impl Batcher {
    /// # Panics
    /// If `max_samples` is zero or `max_age_ms` is not positive — a batcher that can never flush,
    /// or one that flushes on every sample, is a configuration error rather than a runtime state.
    #[must_use]
    pub fn new(max_samples: usize, max_age_ms: i64) -> Self {
        assert!(max_samples > 0, "a batch must be able to hold a sample");
        assert!(max_age_ms > 0, "batch age limit must be positive");
        Self {
            max_samples,
            max_age_ms,
            pending: Vec::with_capacity(max_samples),
            oldest_pending_ms: None,
        }
    }

    /// Adds a sample. Returns a batch when the size limit is reached.
    ///
    /// `now_ms` is the arrival instant, kept separately from the sample's own `ts_ms`: a batch ages
    /// by when it was *received*, not by the timestamps inside it, or a backfill of old samples
    /// would look permanently overdue.
    pub fn push(&mut self, sample: Sample, now_ms: i64) -> Option<Vec<Sample>> {
        if self.pending.is_empty() {
            self.oldest_pending_ms = Some(now_ms);
        }
        self.pending.push(sample);
        if self.pending.len() >= self.max_samples {
            return self.take();
        }
        None
    }

    /// Returns a batch if the pending one has aged past the limit. Call on a timer tick.
    pub fn flush_if_due(&mut self, now_ms: i64) -> Option<Vec<Sample>> {
        let oldest = self.oldest_pending_ms?;
        if now_ms.saturating_sub(oldest) >= self.max_age_ms {
            return self.take();
        }
        None
    }

    /// Returns whatever is pending regardless of size or age — for shutdown, where the alternative
    /// is silently discarding accepted samples.
    pub fn drain(&mut self) -> Option<Vec<Sample>> {
        self.take()
    }

    fn take(&mut self) -> Option<Vec<Sample>> {
        if self.pending.is_empty() {
            return None;
        }
        self.oldest_pending_ms = None;
        Some(std::mem::replace(
            &mut self.pending,
            Vec::with_capacity(self.max_samples),
        ))
    }

    /// Samples currently held and not yet flushed.
    #[must_use]
    pub fn pending_len(&self) -> usize {
        self.pending.len()
    }
}

/// The ingestion pipeline: normalize, validate, deduplicate, batch.
///
/// One invalid sample never rejects a batch. It is dropped, counted by reason, and the rest of the
/// batch proceeds — because a single malformed emitter must not blind a whole project, and a
/// silent drop is only acceptable when it is counted.
#[derive(Debug)]
pub struct Pipeline {
    governed_metrics: Vec<String>,
    max_skew_ms: i64,
    deduplicator: Deduplicator,
    batcher: Batcher,
    rejects: RejectCounts,
    accepted: u64,
}

impl Pipeline {
    /// `governed_metrics` is the set every accepted metric must belong to: ADR-0036 requires each
    /// supervision metric to be a `CPT-*` concept node, so an unrecognized name is an ungoverned
    /// calculation entering through the ingest door.
    #[must_use]
    pub fn new(
        governed_metrics: Vec<String>,
        max_skew_ms: i64,
        deduplicator: Deduplicator,
        batcher: Batcher,
    ) -> Self {
        assert!(max_skew_ms > 0, "accepted clock skew must be positive");
        Self {
            governed_metrics,
            max_skew_ms,
            deduplicator,
            batcher,
            rejects: RejectCounts::default(),
            accepted: 0,
        }
    }

    /// Offers one raw sample. `Ok(Some(batch))` means the batch is ready to insert.
    pub fn offer(&mut self, raw: Sample, now_ms: i64) -> Result<Option<Vec<Sample>>, RejectReason> {
        let sample = normalize(raw);

        if sample.project_id.is_empty() {
            return Err(self.reject(RejectReason::MissingProjectId));
        }
        if sample.metric.is_empty() {
            return Err(self.reject(RejectReason::MissingMetric));
        }
        if !self.governed_metrics.contains(&sample.metric) {
            return Err(self.reject(RejectReason::UnknownMetric));
        }
        if !sample.value.is_finite() {
            return Err(self.reject(RejectReason::NonFiniteValue));
        }
        if (now_ms - sample.ts_ms).abs() > self.max_skew_ms {
            // Both directions: a timestamp from the future is as wrong as a stale one, and
            // accepting it would put a sample in a partition that has not happened yet.
            return Err(self.reject(RejectReason::TimestampOutOfWindow));
        }
        if self.deduplicator.is_duplicate(&sample) {
            return Err(self.reject(RejectReason::Duplicate));
        }

        self.accepted = self.accepted.saturating_add(1);
        Ok(self.batcher.push(sample, now_ms))
    }

    fn reject(&mut self, reason: RejectReason) -> RejectReason {
        self.rejects.record(reason);
        reason
    }

    /// Flushes on age. Call on a timer tick.
    pub fn flush_if_due(&mut self, now_ms: i64) -> Option<Vec<Sample>> {
        self.batcher.flush_if_due(now_ms)
    }

    /// Flushes unconditionally — shutdown path.
    pub fn drain(&mut self) -> Option<Vec<Sample>> {
        self.batcher.drain()
    }

    /// Rejections by reason.
    #[must_use]
    pub fn rejects(&self) -> &RejectCounts {
        &self.rejects
    }

    /// Samples accepted into a batch.
    #[must_use]
    pub fn accepted(&self) -> u64 {
        self.accepted
    }
}
