//! The retry loop: batch in, row in ClickHouse or a line in the dead letter, never nothing.
//!
//! The delivery guarantee here is **at-least-once, deliberately**. `telemetry.samples` is a plain
//! `MergeTree`, so ClickHouse's `insert_deduplication_token` does not apply to it, and a request that
//! times out after being sent may well have succeeded. Retrying it can therefore duplicate a row.
//! That trade was made knowingly (owner decision, 2026-07-29): the raw tier is a 14-day buffer and
//! never truth (ADR-0034), so a duplicate costs a slightly wrong count on the raw table while the
//! alternative — discarding a batch that is probably absent — costs real data.
//!
//! **What that means for a reader of the data**, stated here because it is invisible from the schema:
//! a duplicate inflates additive metrics (a count, a sum) and barely moves order statistics (a
//! quantile, a min, a max). A dashboard that must not double-count reads the rollups with an
//! explicit deduplication, or reads a metric that is not additive.

use std::time::Duration;

use scm_ingest::{MetricRegistry, Sample};

use crate::deadletter::DeadLetter;
use crate::rowbinary::{INSERT_STATEMENT, encode_batch};
use crate::schema::{self, SchemaError};
use crate::transport::{Sleeper, Transport, TransportError, backoff_delay};

/// How hard to try before giving up on a batch. No defaults: an attempt budget is a deployment's
/// decision, and a default here would become every deployment's (ADR-0037).
#[derive(Debug, Clone, Copy)]
pub struct RetryPolicy {
    pub max_attempts: u32,
    pub base_delay: Duration,
    pub max_delay: Duration,
}

impl RetryPolicy {
    pub fn new(max_attempts: u32, base_delay: Duration, max_delay: Duration) -> Self {
        Self {
            max_attempts: max_attempts.max(1),
            base_delay,
            max_delay,
        }
    }
}

/// What happened to one batch.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Outcome {
    /// Accepted by the server. `duplicate_possible` is true when the batch was retried past an
    /// ambiguous failure — surfaced rather than hidden, so an operator can explain a doubled count
    /// instead of investigating it.
    Written {
        attempts: u32,
        duplicate_possible: bool,
    },
    /// Every attempt failed. `reason` is what was recorded alongside the samples — and if the dead
    /// letter could not be written either, it says so, because there is nowhere further to escalate
    /// and a counter that reported "dead-lettered" for records that never landed would be a lie.
    DeadLettered {
        attempts: u32,
        last: TransportError,
        reason: String,
    },
    /// Nothing to do. Kept distinct from `Written` so an empty flush cannot inflate a success count.
    Empty,
}

/// Counters an operator reads to tell a healthy ingester from a limping one.
#[derive(Debug, Default, Clone, Copy, PartialEq, Eq)]
pub struct Stats {
    pub batches_written: u64,
    pub samples_written: u64,
    pub retries: u64,
    pub batches_dead_lettered: u64,
    /// Batches that succeeded only after an ambiguous failure — the ones that may have duplicated.
    pub batches_possibly_duplicated: u64,
}

/// Writes batches to ClickHouse, retrying and dead-lettering as configured.
#[derive(Debug)]
pub struct Writer<T: Transport, S: Sleeper> {
    transport: T,
    sleeper: S,
    policy: RetryPolicy,
    dead_letter: DeadLetter,
    stats: Stats,
    /// The same registry the pipeline validated against, used to stamp the `kind` column.
    ///
    /// Held here rather than passed per write because it is fixed for the process's life, and
    /// because a second registry supplied at call time is a second answer to "is this a level".
    registry: MetricRegistry,
}

impl<T: Transport, S: Sleeper> Writer<T, S> {
    pub fn new(
        transport: T,
        sleeper: S,
        policy: RetryPolicy,
        dead_letter: DeadLetter,
        registry: MetricRegistry,
    ) -> Self {
        Self {
            transport,
            sleeper,
            policy,
            dead_letter,
            stats: Stats::default(),
            registry,
        }
    }

    /// Checks the live table against what the encoder writes. **Call this before the first write**
    /// and refuse to start if it fails — see [`crate::schema`] for why a passing insert proves
    /// nothing about correctness under RowBinary.
    pub fn verify_schema(&self) -> Result<(), SchemaError> {
        schema::verify(&self.transport)
    }

    /// Sends one batch, retrying per the policy, dead-lettering if the budget runs out.
    ///
    /// The body is encoded **once** and reused across attempts: re-encoding per attempt would burn
    /// CPU during exactly the incident where the process is already struggling.
    pub fn write(&mut self, batch: &[Sample]) -> Outcome {
        if batch.is_empty() {
            return Outcome::Empty;
        }
        let body = encode_batch(batch, &self.registry);
        let mut duplicate_possible = false;
        let mut last: Option<TransportError> = None;
        let mut used = 0_u32;

        for attempt in 1..=self.policy.max_attempts {
            used = attempt;
            match self.transport.post(INSERT_STATEMENT, &body) {
                Ok(()) => {
                    self.stats.batches_written += 1;
                    self.stats.samples_written += batch.len() as u64;
                    if duplicate_possible {
                        self.stats.batches_possibly_duplicated += 1;
                    }
                    return Outcome::Written {
                        attempts: attempt,
                        duplicate_possible,
                    };
                }
                Err(err) => {
                    duplicate_possible |= err.may_duplicate();
                    let retryable = err.is_retryable();
                    last = Some(err);
                    // A refusal breaks here, so `used` is the attempt it happened on — not the
                    // budget. Reporting the budget would make a fast, terminal failure look like a
                    // long struggle.
                    if !retryable || attempt == self.policy.max_attempts {
                        break;
                    }
                    self.stats.retries += 1;
                    self.sleeper.sleep(backoff_delay(
                        attempt,
                        self.policy.base_delay,
                        self.policy.max_delay,
                    ));
                }
            }
        }

        let last = last.unwrap_or(TransportError::NotSent("no attempt was made".to_owned()));
        // The dead-letter write can itself fail — a full disk, a read-only mount. There is nowhere
        // further to escalate, so the failure travels in the reason instead of being swallowed.
        let reason = match self.dead_letter.record(batch, &last.to_string()) {
            Ok(()) => last.to_string(),
            Err(io_err) => format!("{last}; and the dead letter could not be written: {io_err}"),
        };
        self.stats.batches_dead_lettered += 1;
        Outcome::DeadLettered {
            attempts: used,
            last,
            reason,
        }
    }

    pub fn stats(&self) -> Stats {
        self.stats
    }

    pub fn dead_letter(&self) -> &DeadLetter {
        &self.dead_letter
    }

    /// The transport, so a caller (or a test) can inspect what was actually sent.
    pub fn transport(&self) -> &T {
        &self.transport
    }
}
