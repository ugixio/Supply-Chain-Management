//! Behaviour tests for the ingestion core.
//!
//! Every one of these passes a `now_ms` explicitly. Nothing here reads a clock, so nothing here is
//! flaky, and the batch-age tests do not sleep.

#![allow(clippy::unwrap_used, clippy::expect_used)]

use scm_ingest::{Batcher, Deduplicator, Pipeline, RejectReason, Sample, normalize};

const NOW: i64 = 1_800_000_000_000; // a fixed UTC instant; the value is irrelevant, its fixedness is not

fn sample(project: &str, metric: &str, ts_ms: i64, value: f64) -> Sample {
    Sample {
        project_id: project.to_owned(),
        metric: metric.to_owned(),
        ts_ms,
        value,
        environment: "prod".to_owned(),
        unit: "count".to_owned(),
    }
}

fn governed() -> Vec<String> {
    // The CPT-0155..0160 metric names — ADR-0036: a metric with no concept node is ungoverned.
    [
        "deployment_frequency",
        "lead_time_for_changes",
        "change_failure_rate",
    ]
    .iter()
    .map(|name| (*name).to_owned())
    .collect()
}

fn pipeline(max_samples: usize, max_age_ms: i64) -> Pipeline {
    Pipeline::new(
        governed(),
        60_000,
        Deduplicator::new(30_000, 1_000),
        Batcher::new(max_samples, max_age_ms),
    )
}

#[test]
fn normalize_trims_but_does_not_invent() {
    let cleaned = normalize(sample("  proj-a  ", "  deployment_frequency ", NOW, 1.0));
    assert_eq!(cleaned.project_id, "proj-a");
    assert_eq!(cleaned.metric, "deployment_frequency");
    // Normalization must not turn an empty field into a placeholder: that is validation's call.
    let empty = normalize(sample("   ", "   ", NOW, 1.0));
    assert!(empty.project_id.is_empty());
    assert!(empty.metric.is_empty());
}

#[test]
fn one_invalid_sample_does_not_reject_the_batch() {
    let mut pipeline = pipeline(4, 10_000);

    assert!(
        pipeline
            .offer(sample("p", "deployment_frequency", NOW, 1.0), NOW)
            .is_ok()
    );
    // A non-finite value must never reach an aggregate: it poisons sum, min, max and the quantile.
    assert_eq!(
        pipeline.offer(sample("p", "deployment_frequency", NOW, f64::NAN), NOW),
        Err(RejectReason::NonFiniteValue)
    );
    assert!(
        pipeline
            .offer(sample("p", "deployment_frequency", NOW + 1, 2.0), NOW)
            .is_ok()
    );

    assert_eq!(
        pipeline.accepted(),
        2,
        "the good samples survived the bad one"
    );
    assert_eq!(pipeline.rejects().get(RejectReason::NonFiniteValue), 1);
    assert_eq!(pipeline.rejects().total(), 1);
}

#[test]
fn an_ungoverned_metric_is_refused() {
    let mut pipeline = pipeline(4, 10_000);
    assert_eq!(
        pipeline.offer(sample("p", "some_metric_nobody_defined", NOW, 1.0), NOW),
        Err(RejectReason::UnknownMetric)
    );
    assert_eq!(pipeline.accepted(), 0);
}

#[test]
fn a_future_timestamp_is_as_wrong_as_a_stale_one() {
    let mut pipeline = pipeline(4, 10_000);
    // Accepting a future instant would write into a monthly partition that has not happened yet.
    assert_eq!(
        pipeline.offer(sample("p", "deployment_frequency", NOW + 120_000, 1.0), NOW),
        Err(RejectReason::TimestampOutOfWindow)
    );
    assert_eq!(
        pipeline.offer(sample("p", "deployment_frequency", NOW - 120_000, 1.0), NOW),
        Err(RejectReason::TimestampOutOfWindow)
    );
    assert_eq!(
        pipeline.rejects().get(RejectReason::TimestampOutOfWindow),
        2
    );
}

#[test]
fn a_retried_sample_is_deduplicated_but_a_new_instant_is_not() {
    let mut pipeline = pipeline(16, 10_000);

    assert!(
        pipeline
            .offer(sample("p", "deployment_frequency", NOW, 1.0), NOW)
            .is_ok()
    );
    // The same (project, metric, ts) arriving again is a retry, not a second observation.
    assert_eq!(
        pipeline.offer(sample("p", "deployment_frequency", NOW, 1.0), NOW + 500),
        Err(RejectReason::Duplicate)
    );
    // A different millisecond is a different observation, even with an identical value.
    assert!(
        pipeline
            .offer(sample("p", "deployment_frequency", NOW + 1, 1.0), NOW)
            .is_ok()
    );
    // A different project reporting the same metric at the same instant is not a duplicate.
    assert!(
        pipeline
            .offer(sample("q", "deployment_frequency", NOW, 1.0), NOW)
            .is_ok()
    );

    assert_eq!(pipeline.accepted(), 3);
    assert_eq!(pipeline.rejects().get(RejectReason::Duplicate), 1);
}

#[test]
fn dedup_memory_is_bounded_by_the_window_not_by_the_sample_count() {
    let mut dedup = Deduplicator::new(10_000, 1_000); // 10 buckets of one second

    // Twenty seconds of samples, one per 100ms — far more samples than buckets.
    for step in 0..200 {
        let ts = NOW + step * 100;
        dedup.is_duplicate(&sample("p", "deployment_frequency", ts, 1.0));
    }

    assert!(
        dedup.bucket_count() <= 11,
        "buckets must stay bounded by window/bucket, got {}",
        dedup.bucket_count()
    );
}

#[test]
fn a_sample_older_than_the_dedup_window_is_not_called_a_duplicate() {
    let mut dedup = Deduplicator::new(5_000, 1_000);

    dedup.is_duplicate(&sample("p", "deployment_frequency", NOW, 1.0));
    // Advance well beyond the window so the original bucket is evicted.
    dedup.is_duplicate(&sample("p", "deployment_frequency", NOW + 60_000, 1.0));

    // The first sample is no longer remembered. Claiming "duplicate" here would assert knowledge
    // the deduplicator has deliberately discarded; deciding staleness is the validator's job.
    assert!(!dedup.is_duplicate(&sample("p", "deployment_frequency", NOW, 1.0)));
}

#[test]
fn out_of_order_arrival_still_deduplicates() {
    let mut dedup = Deduplicator::new(30_000, 1_000);

    // Samples that arrive newest-first — normal when two emitters interleave.
    assert!(!dedup.is_duplicate(&sample("p", "deployment_frequency", NOW + 5_000, 1.0)));
    assert!(!dedup.is_duplicate(&sample("p", "deployment_frequency", NOW, 1.0)));
    // Both must still be remembered.
    assert!(dedup.is_duplicate(&sample("p", "deployment_frequency", NOW + 5_000, 1.0)));
    assert!(dedup.is_duplicate(&sample("p", "deployment_frequency", NOW, 1.0)));
}

#[test]
fn a_batch_flushes_on_size() {
    let mut pipeline = pipeline(3, 60_000);

    assert!(
        pipeline
            .offer(sample("p", "deployment_frequency", NOW, 1.0), NOW)
            .unwrap()
            .is_none()
    );
    assert!(
        pipeline
            .offer(sample("p", "deployment_frequency", NOW + 1, 2.0), NOW)
            .unwrap()
            .is_none()
    );
    let batch = pipeline
        .offer(sample("p", "deployment_frequency", NOW + 2, 3.0), NOW)
        .unwrap()
        .expect("the third sample completes the batch");
    assert_eq!(batch.len(), 3);
}

#[test]
fn a_batch_flushes_on_age_so_a_quiet_project_is_not_starved() {
    let mut pipeline = pipeline(1_000, 5_000);

    pipeline
        .offer(sample("p", "deployment_frequency", NOW, 1.0), NOW)
        .unwrap();
    // Not yet due: age alone must not flush early.
    assert!(pipeline.flush_if_due(NOW + 4_999).is_none());
    let batch = pipeline
        .flush_if_due(NOW + 5_000)
        .expect("a lone sample must not wait for a batch that will never fill");
    assert_eq!(batch.len(), 1);
    // And the age clock resets: an empty batcher has nothing to flush.
    assert!(pipeline.flush_if_due(NOW + 100_000).is_none());
}

#[test]
fn batch_age_runs_from_arrival_not_from_the_sample_timestamp() {
    let mut batcher = Batcher::new(1_000, 5_000);

    // A backfill of samples an hour old, arriving now. If age were measured from `ts_ms` the batch
    // would look permanently overdue and flush one sample at a time.
    batcher.push(
        sample("p", "deployment_frequency", NOW - 3_600_000, 1.0),
        NOW,
    );
    assert!(batcher.flush_if_due(NOW + 1_000).is_none());
    assert!(batcher.flush_if_due(NOW + 5_000).is_some());
}

#[test]
fn drain_does_not_lose_accepted_samples_at_shutdown() {
    let mut pipeline = pipeline(1_000, 60_000);
    pipeline
        .offer(sample("p", "deployment_frequency", NOW, 1.0), NOW)
        .unwrap();
    pipeline
        .offer(sample("p", "deployment_frequency", NOW + 1, 2.0), NOW)
        .unwrap();

    let batch = pipeline
        .drain()
        .expect("accepted samples must survive shutdown");
    assert_eq!(batch.len(), 2);
    assert!(
        pipeline.drain().is_none(),
        "draining twice yields nothing the second time"
    );
}

#[test]
fn reject_reasons_are_counted_separately() {
    let mut pipeline = pipeline(100, 60_000);

    let _ = pipeline.offer(sample("", "deployment_frequency", NOW, 1.0), NOW);
    let _ = pipeline.offer(sample("p", "", NOW, 1.0), NOW);
    let _ = pipeline.offer(sample("p", "nope", NOW, 1.0), NOW);
    let _ = pipeline.offer(sample("p", "deployment_frequency", NOW, f64::INFINITY), NOW);

    assert_eq!(pipeline.rejects().get(RejectReason::MissingProjectId), 1);
    assert_eq!(pipeline.rejects().get(RejectReason::MissingMetric), 1);
    assert_eq!(pipeline.rejects().get(RejectReason::UnknownMetric), 1);
    assert_eq!(pipeline.rejects().get(RejectReason::NonFiniteValue), 1);
    assert_eq!(pipeline.rejects().total(), 4);
    // Four distinct reasons, so a report can name the broken emitter rather than a bare total.
    assert_eq!(pipeline.rejects().iter().count(), 4);
}
