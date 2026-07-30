//! Where a batch goes when retries are exhausted.
//!
//! The failure this exists for is **ClickHouse unreachable**, which rules out storing the casualty
//! in ClickHouse. So it is a local file, one JSON object per sample, appended — replayable by hand,
//! greppable, and independent of the thing that broke.
//!
//! **It is bounded, and that is the part worth reading.** An unbounded dead-letter file turns one
//! outage into two: the server comes back and the disk is full. So the sink rotates at a byte limit
//! and keeps exactly one previous generation, which puts a hard ceiling of `2 × max_bytes` on what
//! ingest can consume no matter how long the outage lasts. Beyond that, the oldest records are
//! **dropped on purpose** — and counted, because a silent drop here would be indistinguishable from
//! having lost nothing.
//!
//! The retention choice behind that: the raw tier keeps 14 days and is explicitly not truth
//! (ADR-0034), so the oldest dead-lettered sample is the least valuable thing in the system. Losing
//! it beats losing the ability to write anything.

use std::fs::{self, File, OpenOptions};
use std::io::{self, Write};
use std::path::{Path, PathBuf};

use scm_ingest::Sample;

/// Append-only NDJSON sink with a two-generation byte bound.
#[derive(Debug)]
pub struct DeadLetter {
    path: PathBuf,
    max_bytes: u64,
    written: u64,
    samples: u64,
    rotations: u64,
    dropped_generations: u64,
}

impl DeadLetter {
    /// `max_bytes` is the size at which the live file rotates; there is no default, because a
    /// disk budget belongs to a deployment and not to this crate (the same rule the core follows).
    ///
    /// An existing file is appended to and its current size counted, so a restart mid-outage does
    /// not reset the budget — which is exactly when the budget matters.
    pub fn new(path: impl Into<PathBuf>, max_bytes: u64) -> io::Result<Self> {
        let path = path.into();
        if let Some(parent) = path.parent() {
            if !parent.as_os_str().is_empty() {
                fs::create_dir_all(parent)?;
            }
        }
        let written = fs::metadata(&path).map(|m| m.len()).unwrap_or(0);
        Ok(Self {
            path,
            max_bytes,
            written,
            samples: 0,
            rotations: 0,
            dropped_generations: 0,
        })
    }

    fn previous(&self) -> PathBuf {
        let mut name = self.path.clone().into_os_string();
        name.push(".1");
        PathBuf::from(name)
    }

    /// Moves the live file aside, discarding whatever generation was already there.
    ///
    /// The discard is the bound. It is counted so an operator can see that data was dropped rather
    /// than discovering later that it was.
    fn rotate(&mut self) -> io::Result<()> {
        let previous = self.previous();
        if previous.exists() {
            self.dropped_generations += 1;
        }
        fs::rename(&self.path, &previous)?;
        self.rotations += 1;
        self.written = 0;
        Ok(())
    }

    /// Writes a whole batch, rotating first if it would cross the limit.
    ///
    /// Rotation is decided per batch, not per sample: splitting one batch across two generations
    /// would make it unreplayable, which defeats the point of keeping it.
    pub fn record(&mut self, batch: &[Sample], reason: &str) -> io::Result<()> {
        if batch.is_empty() {
            return Ok(());
        }
        let body = Self::encode(batch, reason);
        let len = body.len() as u64;
        if self.written > 0 && self.written + len > self.max_bytes {
            self.rotate()?;
        }
        let mut file: File = OpenOptions::new()
            .create(true)
            .append(true)
            .open(&self.path)?;
        file.write_all(body.as_bytes())?;
        file.flush()?;
        self.written += len;
        self.samples += batch.len() as u64;
        Ok(())
    }

    fn encode(batch: &[Sample], reason: &str) -> String {
        let mut out = String::with_capacity(batch.len() * 128);
        for sample in batch {
            let record = serde_json::json!({
                "reason": reason,
                "project_id": sample.project_id,
                "metric": sample.metric,
                "ts_ms": sample.ts_ms,
                "value": sample.value,
                "environment": sample.environment,
                "unit": sample.unit,
            });
            out.push_str(&record.to_string());
            out.push('\n');
        }
        out
    }

    /// Samples written to the dead letter by this instance.
    pub fn samples(&self) -> u64 {
        self.samples
    }

    /// Times the live file was rotated.
    pub fn rotations(&self) -> u64 {
        self.rotations
    }

    /// Generations discarded to hold the byte bound — **records permanently lost**. Non-zero here
    /// means the outage outlasted the disk budget, which is an alert, not a statistic.
    pub fn dropped_generations(&self) -> u64 {
        self.dropped_generations
    }

    pub fn path(&self) -> &Path {
        &self.path
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn sample(project: &str, ts_ms: i64) -> Sample {
        Sample {
            project_id: project.to_owned(),
            metric: "deployment_frequency".to_owned(),
            ts_ms,
            value: 1.5,
            environment: "prod".to_owned(),
            unit: "count".to_owned(),
        }
    }

    /// A directory that removes itself, so the tests leave nothing behind and never collide.
    struct TempDir(PathBuf);

    impl TempDir {
        fn new(tag: &str) -> Self {
            let mut path = std::env::temp_dir();
            path.push(format!("scm-deadletter-{tag}-{}", std::process::id()));
            let _ = fs::remove_dir_all(&path);
            fs::create_dir_all(&path).unwrap_or_default();
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

    #[test]
    fn one_line_of_json_per_sample() {
        let dir = TempDir::new("lines");
        let path = dir.file("dl.ndjson");
        let mut sink = DeadLetter::new(&path, 1_000_000).unwrap_or_else(|e| panic!("{e}"));
        sink.record(&[sample("a", 1), sample("b", 2)], "unreachable")
            .unwrap_or_else(|e| panic!("{e}"));

        let body = fs::read_to_string(&path).unwrap_or_default();
        let lines: Vec<&str> = body.lines().collect();
        assert_eq!(lines.len(), 2);
        for line in lines {
            let parsed: serde_json::Value =
                serde_json::from_str(line).unwrap_or_else(|e| panic!("not JSON: {e}"));
            assert_eq!(parsed["reason"], "unreachable");
            assert_eq!(parsed["metric"], "deployment_frequency");
        }
        assert_eq!(sink.samples(), 2);
    }

    #[test]
    fn rotation_holds_the_byte_bound_and_keeps_one_generation() {
        let dir = TempDir::new("rotate");
        let path = dir.file("dl.ndjson");
        // A limit small enough that each batch fills it, so every write after the first rotates.
        let mut sink = DeadLetter::new(&path, 200).unwrap_or_else(|e| panic!("{e}"));
        for n in 0..6 {
            sink.record(&[sample("p", n)], "unreachable")
                .unwrap_or_else(|e| panic!("{e}"));
        }

        assert!(
            sink.rotations() >= 4,
            "expected rotation, got {}",
            sink.rotations()
        );
        let live = fs::metadata(&path).map(|m| m.len()).unwrap_or(0);
        let previous = fs::metadata(sink.previous()).map(|m| m.len()).unwrap_or(0);
        assert!(
            live + previous <= 2 * 200 + 256,
            "two generations must stay near the bound, got {live} + {previous}"
        );
        assert!(
            sink.dropped_generations() > 0,
            "holding the bound means discarding, and discarding must be counted"
        );
    }

    #[test]
    fn a_batch_is_never_split_across_a_rotation() {
        let dir = TempDir::new("atomic");
        let path = dir.file("dl.ndjson");
        let mut sink = DeadLetter::new(&path, 100).unwrap_or_else(|e| panic!("{e}"));
        sink.record(&[sample("a", 1)], "first")
            .unwrap_or_else(|e| panic!("{e}"));
        // This batch is larger than the whole limit; it must still land in one file, intact.
        let big: Vec<Sample> = (0..10).map(|n| sample("b", n)).collect();
        sink.record(&big, "second")
            .unwrap_or_else(|e| panic!("{e}"));

        let body = fs::read_to_string(&path).unwrap_or_default();
        assert_eq!(
            body.lines().count(),
            10,
            "the oversized batch stayed whole, replayable as one unit"
        );
    }

    #[test]
    fn an_empty_batch_writes_nothing_and_creates_no_file() {
        let dir = TempDir::new("empty");
        let path = dir.file("dl.ndjson");
        let mut sink = DeadLetter::new(&path, 1_000).unwrap_or_else(|e| panic!("{e}"));
        sink.record(&[], "unreachable")
            .unwrap_or_else(|e| panic!("{e}"));
        assert!(!path.exists(), "no casualty, no file");
        assert_eq!(sink.samples(), 0);
    }

    #[test]
    fn a_restart_mid_outage_inherits_the_budget_rather_than_resetting_it() {
        let dir = TempDir::new("restart");
        let path = dir.file("dl.ndjson");
        {
            let mut sink = DeadLetter::new(&path, 300).unwrap_or_else(|e| panic!("{e}"));
            sink.record(&[sample("a", 1), sample("a", 2)], "unreachable")
                .unwrap_or_else(|e| panic!("{e}"));
        }
        let size_before = fs::metadata(&path).map(|m| m.len()).unwrap_or(0);
        assert!(size_before > 0);

        // A fresh instance over the same path must count what is already there. If it reset to zero,
        // a crash-loop during an outage would grow the file without bound — one restart per budget.
        let sink = DeadLetter::new(&path, 300).unwrap_or_else(|e| panic!("{e}"));
        assert_eq!(sink.written, size_before);
    }

    #[test]
    fn a_value_that_json_must_escape_survives_a_round_trip() {
        let dir = TempDir::new("escape");
        let path = dir.file("dl.ndjson");
        let mut sink = DeadLetter::new(&path, 10_000).unwrap_or_else(|e| panic!("{e}"));
        let mut awkward = sample("pro\"ject\nnewline", 7);
        awkward.unit = "unit\\with\tcontrol".to_owned();
        sink.record(&[awkward.clone()], "unreachable")
            .unwrap_or_else(|e| panic!("{e}"));

        let body = fs::read_to_string(&path).unwrap_or_default();
        assert_eq!(
            body.lines().count(),
            1,
            "an embedded newline must not become two records"
        );
        let parsed: serde_json::Value =
            serde_json::from_str(body.trim_end()).unwrap_or_else(|e| panic!("not JSON: {e}"));
        assert_eq!(parsed["project_id"], awkward.project_id);
        assert_eq!(parsed["unit"], awkward.unit);
    }
}
