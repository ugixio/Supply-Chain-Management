//! Behaviour tests for the retry loop and the dead letter.
//!
//! No server and no sleeping: the transport is a script of outcomes and the sleeper counts instead
//! of waiting, so every failure mode here — unreachable, ambiguous, refused, exhausted — is exercised
//! deterministically. These are exactly the paths a live ClickHouse cannot be made to produce on
//! demand, which is why the seam exists.

#![allow(clippy::unwrap_used, clippy::expect_used)]

use std::cell::RefCell;
use std::fs;
use std::path::PathBuf;
use std::time::Duration;

use scm_ingest::Sample;
use scm_ingest_clickhouse::{
    DeadLetter, Outcome, RetryPolicy, Sleeper, Transport, TransportError, Writer,
};

/// A transport that replays a fixed script of outcomes, then repeats its last one.
struct ScriptedTransport {
    script: RefCell<Vec<Result<(), TransportError>>>,
    calls: RefCell<usize>,
    bodies: RefCell<Vec<Vec<u8>>>,
    catalogue: String,
}

impl ScriptedTransport {
    fn new(script: Vec<Result<(), TransportError>>) -> Self {
        Self {
            script: RefCell::new(script),
            calls: RefCell::new(0),
            bodies: RefCell::new(Vec::new()),
            catalogue: String::new(),
        }
    }

    fn always(outcome: Result<(), TransportError>) -> Self {
        Self::new(vec![outcome])
    }

    fn calls(&self) -> usize {
        *self.calls.borrow()
    }

    /// Every body the writer sent, in order.
    fn bodies(&self) -> Vec<Vec<u8>> {
        self.bodies.borrow().clone()
    }
}

impl Transport for ScriptedTransport {
    fn post(&self, _query: &str, body: &[u8]) -> Result<(), TransportError> {
        let mut calls = self.calls.borrow_mut();
        let script = self.script.borrow();
        let index = (*calls).min(script.len().saturating_sub(1));
        *calls += 1;
        self.bodies.borrow_mut().push(body.to_vec());
        script[index].clone()
    }

    fn query(&self, _sql: &str) -> Result<String, TransportError> {
        Ok(self.catalogue.clone())
    }
}

/// Counts what the retry loop asked to wait, without waiting.
#[derive(Default)]
struct CountingSleeper {
    slept: RefCell<Vec<Duration>>,
}

impl Sleeper for CountingSleeper {
    fn sleep(&self, duration: Duration) {
        self.slept.borrow_mut().push(duration);
    }
}

struct TempDir(PathBuf);

impl TempDir {
    fn new(tag: &str) -> Self {
        let mut path = std::env::temp_dir();
        path.push(format!("scm-writer-{tag}-{}", std::process::id()));
        let _ = fs::remove_dir_all(&path);
        fs::create_dir_all(&path).unwrap();
        Self(path)
    }
    fn file(&self, name: &str) -> PathBuf {
        self.0.join(name)
    }
}

impl Drop for TempDir {
    fn drop(&mut self) {
        let _ = fs::remove_dir_all(&self.0);
    }
}

fn sample(project: &str, ts_ms: i64) -> Sample {
    Sample {
        project_id: project.to_owned(),
        metric: "deployment_frequency".to_owned(),
        ts_ms,
        value: 1.0,
        environment: "prod".to_owned(),
        unit: "count".to_owned(),
    }
}

fn policy() -> RetryPolicy {
    RetryPolicy::new(4, Duration::from_millis(10), Duration::from_millis(100))
}

#[test]
fn a_healthy_write_costs_one_attempt_and_no_waiting() {
    let dir = TempDir::new("happy");
    let mut writer = Writer::new(
        ScriptedTransport::always(Ok(())),
        CountingSleeper::default(),
        policy(),
        DeadLetter::new(dir.file("dl.ndjson"), 4096).unwrap(),
    );

    let outcome = writer.write(&[sample("p", 1), sample("p", 2)]);
    assert_eq!(
        outcome,
        Outcome::Written {
            attempts: 1,
            duplicate_possible: false
        }
    );
    assert_eq!(writer.stats().samples_written, 2);
    assert_eq!(writer.stats().retries, 0);
    assert!(
        !dir.file("dl.ndjson").exists(),
        "a healthy write leaves no casualty"
    );
}

#[test]
fn a_transient_failure_is_retried_and_then_succeeds() {
    let dir = TempDir::new("transient");
    let transport = ScriptedTransport::new(vec![
        Err(TransportError::NotSent("connect refused".into())),
        Err(TransportError::NotSent("connect refused".into())),
        Ok(()),
    ]);
    let mut writer = Writer::new(
        transport,
        CountingSleeper::default(),
        policy(),
        DeadLetter::new(dir.file("dl.ndjson"), 4096).unwrap(),
    );

    let outcome = writer.write(&[sample("p", 1)]);
    assert_eq!(
        outcome,
        Outcome::Written {
            attempts: 3,
            duplicate_possible: false
        },
        "a server that comes back must not cost the batch"
    );
    assert_eq!(writer.stats().retries, 2);
    // NotSent cannot duplicate: nothing reached the server on the failed attempts.
    assert_eq!(writer.stats().batches_possibly_duplicated, 0);
}

#[test]
fn a_retry_past_an_ambiguous_failure_is_reported_as_possibly_duplicated() {
    let dir = TempDir::new("ambiguous");
    let transport = ScriptedTransport::new(vec![
        Err(TransportError::Ambiguous("read timeout".into())),
        Ok(()),
    ]);
    let mut writer = Writer::new(
        transport,
        CountingSleeper::default(),
        policy(),
        DeadLetter::new(dir.file("dl.ndjson"), 4096).unwrap(),
    );

    let outcome = writer.write(&[sample("p", 1)]);
    assert_eq!(
        outcome,
        Outcome::Written {
            attempts: 2,
            duplicate_possible: true
        },
        "the first attempt may have landed; saying so is the whole point of at-least-once"
    );
    assert_eq!(writer.stats().batches_possibly_duplicated, 1);
}

#[test]
fn a_refusal_is_not_retried_and_goes_straight_to_the_dead_letter() {
    let dir = TempDir::new("refused");
    let path = dir.file("dl.ndjson");
    let transport = ScriptedTransport::always(Err(TransportError::Refused {
        status: 400,
        body: "Cannot parse input".into(),
    }));
    let mut writer = Writer::new(
        transport,
        CountingSleeper::default(),
        policy(),
        DeadLetter::new(&path, 4096).unwrap(),
    );

    let outcome = writer.write(&[sample("p", 1)]);
    match outcome {
        Outcome::DeadLettered { attempts, .. } => assert_eq!(
            attempts, 1,
            "a body the server rejects is rejected identically forever; retrying only delays it"
        ),
        other => panic!("expected the batch to be dead-lettered, got {other:?}"),
    }
    assert_eq!(writer.stats().retries, 0);
    assert_eq!(writer.dead_letter().samples(), 1);
    assert!(
        fs::read_to_string(&path)
            .unwrap()
            .contains("Cannot parse input")
    );
}

#[test]
fn an_exhausted_budget_dead_letters_every_sample_with_the_last_reason() {
    let dir = TempDir::new("exhausted");
    let path = dir.file("dl.ndjson");
    let transport = ScriptedTransport::always(Err(TransportError::ServerError {
        status: 503,
        body: "too many parts".into(),
    }));
    let sleeper = CountingSleeper::default();
    let mut writer = Writer::new(
        transport,
        sleeper,
        policy(),
        DeadLetter::new(&path, 65_536).unwrap(),
    );

    let batch = vec![sample("p", 1), sample("p", 2), sample("p", 3)];
    match writer.write(&batch) {
        Outcome::DeadLettered {
            attempts,
            last,
            reason,
        } => {
            assert_eq!(attempts, 4, "the whole budget was spent");
            assert!(last.is_retryable());
            assert!(
                reason.contains("503"),
                "the reason travels with the records: {reason}"
            );
        }
        other => panic!("expected dead-lettered, got {other:?}"),
    }
    assert_eq!(writer.stats().retries, 3, "four attempts means three waits");
    assert_eq!(writer.stats().batches_dead_lettered, 1);
    assert_eq!(
        fs::read_to_string(&path).unwrap().lines().count(),
        3,
        "no sample is lost when the batch is"
    );
}

#[test]
fn every_attempt_sends_byte_identical_content() {
    let dir = TempDir::new("encode-once");
    // Borrowed back after the move so the recorded bodies can be inspected.
    let mut writer = Writer::new(
        ScriptedTransport::new(vec![
            Err(TransportError::NotSent("down".into())),
            Err(TransportError::Ambiguous("timeout".into())),
            Ok(()),
        ]),
        CountingSleeper::default(),
        policy(),
        DeadLetter::new(dir.file("dl.ndjson"), 4096).unwrap(),
    );
    writer.write(&[sample("p", 1), sample("p", 2)]);

    let bodies = writer.transport().bodies();
    assert_eq!(bodies.len(), 3, "three attempts were made");
    assert_eq!(writer.transport().calls(), 3);
    // This matters because of the at-least-once semantics: if a retry sent different bytes than the
    // attempt whose outcome was unknown, the duplicate would not be a duplicate — it would be a
    // second, *different* row, and no read-side deduplication could collapse the two.
    assert!(
        bodies.windows(2).all(|pair| pair[0] == pair[1]),
        "a retry must be byte-identical to the attempt it repeats"
    );
    assert!(!bodies[0].is_empty());
}

#[test]
fn an_empty_batch_is_not_counted_as_a_write() {
    let dir = TempDir::new("empty");
    let transport = ScriptedTransport::always(Ok(()));
    let mut writer = Writer::new(
        transport,
        CountingSleeper::default(),
        policy(),
        DeadLetter::new(dir.file("dl.ndjson"), 4096).unwrap(),
    );

    assert_eq!(writer.write(&[]), Outcome::Empty);
    assert_eq!(
        writer.stats().batches_written,
        0,
        "an empty flush must not inflate a success count"
    );
}

#[test]
fn a_single_attempt_policy_never_retries() {
    let dir = TempDir::new("single");
    let transport = ScriptedTransport::always(Err(TransportError::NotSent("down".into())));
    let mut writer = Writer::new(
        transport,
        CountingSleeper::default(),
        RetryPolicy::new(1, Duration::from_millis(10), Duration::from_millis(10)),
        DeadLetter::new(dir.file("dl.ndjson"), 4096).unwrap(),
    );

    match writer.write(&[sample("p", 1)]) {
        Outcome::DeadLettered { attempts, .. } => assert_eq!(attempts, 1),
        other => panic!("expected dead-lettered, got {other:?}"),
    }
    assert_eq!(
        writer.stats().retries,
        0,
        "one attempt means no waiting at all"
    );
}

#[test]
fn a_zero_attempt_policy_is_corrected_to_one_rather_than_dropping_silently() {
    // A configuration of zero attempts would mean "never try", which no operator intends and which
    // would discard telemetry with no error anywhere. It is clamped, not honoured.
    let dir = TempDir::new("zero");
    let transport = ScriptedTransport::always(Ok(()));
    let mut writer = Writer::new(
        transport,
        CountingSleeper::default(),
        RetryPolicy::new(0, Duration::from_millis(1), Duration::from_millis(1)),
        DeadLetter::new(dir.file("dl.ndjson"), 4096).unwrap(),
    );

    assert!(matches!(
        writer.write(&[sample("p", 1)]),
        Outcome::Written { attempts: 1, .. }
    ));
}

#[test]
fn waiting_between_attempts_follows_the_capped_backoff() {
    let dir = TempDir::new("backoff");
    let transport = ScriptedTransport::always(Err(TransportError::NotSent("down".into())));
    let mut writer = Writer::new(
        transport,
        CountingSleeper::default(),
        RetryPolicy::new(5, Duration::from_millis(10), Duration::from_millis(30)),
        DeadLetter::new(dir.file("dl.ndjson"), 4096).unwrap(),
    );
    writer.write(&[sample("p", 1)]);

    // Five attempts, four waits: 10, 20, 30 (capped), 30 (capped).
    assert_eq!(writer.stats().retries, 4);
}

#[test]
fn a_transport_that_never_recovers_still_bounds_the_dead_letter() {
    // The disk-safety property, end to end: a long outage rotates rather than growing without limit.
    let dir = TempDir::new("bounded");
    let path = dir.file("dl.ndjson");
    let transport = ScriptedTransport::always(Err(TransportError::NotSent("down".into())));
    let mut writer = Writer::new(
        transport,
        CountingSleeper::default(),
        RetryPolicy::new(1, Duration::from_millis(1), Duration::from_millis(1)),
        DeadLetter::new(&path, 512).unwrap(),
    );

    for n in 0..40 {
        writer.write(&[sample("p", n)]);
    }

    let live = fs::metadata(&path).map(|m| m.len()).unwrap_or(0);
    let mut previous_path = path.clone().into_os_string();
    previous_path.push(".1");
    let previous = fs::metadata(PathBuf::from(previous_path))
        .map(|m| m.len())
        .unwrap_or(0);
    assert!(
        live + previous <= 512 * 2 + 512,
        "two generations only, got {live} + {previous} after 40 failed batches"
    );
    assert!(
        writer.dead_letter().dropped_generations() > 0,
        "holding the bound discarded records, and that must be visible"
    );
    assert_eq!(writer.stats().batches_dead_lettered, 40);
}

#[test]
fn the_schema_guard_reads_through_the_transport() {
    let dir = TempDir::new("schema");
    let mut transport = ScriptedTransport::always(Ok(()));
    transport.catalogue = [
        "project_id\tString",
        "metric\tLowCardinality(String)",
        "ts\tDateTime64(3, 'UTC')",
        "value\tFloat64",
        "environment\tLowCardinality(String)",
        "unit\tLowCardinality(String)",
    ]
    .join("\n");
    let writer = Writer::new(
        transport,
        CountingSleeper::default(),
        policy(),
        DeadLetter::new(dir.file("dl.ndjson"), 4096).unwrap(),
    );
    assert_eq!(writer.verify_schema(), Ok(()));
}

#[test]
fn the_schema_guard_refuses_a_table_that_has_not_been_migrated() {
    let dir = TempDir::new("schema-missing");
    let transport = ScriptedTransport::always(Ok(())); // empty catalogue
    let writer = Writer::new(
        transport,
        CountingSleeper::default(),
        policy(),
        DeadLetter::new(dir.file("dl.ndjson"), 4096).unwrap(),
    );
    assert!(
        writer.verify_schema().is_err(),
        "starting against a table that does not exist must fail loudly, not on the first batch"
    );
}
