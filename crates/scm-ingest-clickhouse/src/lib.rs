//! ClickHouse transport for the telemetry ingester (ADR-0036, Phase M3b).
//!
//! [`scm_ingest`] takes samples in and hands batches out; this crate is the other half — it puts a
//! batch in `telemetry.samples` and it is the only place in the Rust lane that opens a socket. The
//! split is a rule, not a preference: **ENG-R10.1 forbids an I/O framework in a core crate**, so the
//! deterministic pipeline stays testable without a server and the messy part is confined here.
//!
//! # What is decided here, and by whom
//!
//! Four decisions shape this crate, all taken by the owner on 2026-07-29 rather than guessed:
//!
//! 1. **`ureq` + rustls** as the client — blocking, because a flush is one discrete operation and
//!    there is no server here to keep responsive; rustls, because memory-safe TLS without an OpenSSL
//!    C dependency is the cheaper risk. 41 transitive crates, every one permissive OSI (ADR-0002).
//! 2. **RowBinary** on the wire, with a **startup schema guard** ([`schema`]) — the format carries no
//!    types, so the guard is what makes it safe rather than merely fast.
//! 3. **At-least-once delivery**: an ambiguous failure is retried even though it may duplicate a
//!    row. See [`writer`] for what that means for whoever reads the data.
//! 4. **A bounded dead-letter file** ([`deadletter`]) for batches that outlive the retry budget.
//!
//! # Policy values
//!
//! As in the core: every threshold — attempts, backoff, timeout, dead-letter size — is a constructor
//! argument with **no default**. A default in a signature is how one deployment's tuning becomes
//! every deployment's inheritance (ADR-0037), and the numbers here are all deployment shape.
//!
//! # What this crate does not do
//!
//! It does not read a clock to decide *when* to flush — that is the core's [`scm_ingest::Batcher`],
//! which takes time as an input. It does not create the schema; `db/clickhouse` owns the migrations
//! and its own gate. It does not deduplicate: the core does that within its window, and anything
//! surviving a process restart is handled by reading the rollups, per decision 3.
//!
//! # Wiring it up
//!
//! ```no_run
//! use std::time::Duration;
//! use scm_ingest::{Batcher, Deduplicator, MetricKind, MetricRegistry, Pipeline};
//! use scm_ingest_clickhouse::{
//!     DeadLetter, Endpoint, HttpTransport, RetryPolicy, ThreadSleeper, Writer,
//! };
//!
//! # fn main() -> Result<(), Box<dyn std::error::Error>> {
//! // One registry, shared: the pipeline decides whether a metric is governed and the writer
//! // stamps the `kind` column from the same answer. Two registries would be two answers.
//! let registry = MetricRegistry::new(vec![
//!     ("deployment_frequency".to_owned(), MetricKind::Flow),
//!     ("open_work_orders".to_owned(), MetricKind::Level),
//! ]);
//!
//! let endpoint = Endpoint::from_env(Duration::from_secs(10))?;
//! let writer = Writer::new(
//!     HttpTransport::new(endpoint),
//!     ThreadSleeper,
//!     RetryPolicy::new(5, Duration::from_millis(200), Duration::from_secs(5)),
//!     DeadLetter::new("/var/lib/scm/dead-letter.ndjson", 64 * 1024 * 1024)?,
//!     registry.clone(),
//! );
//!
//! // Refuse to start on a schema the encoder does not match: under RowBinary a successful insert
//! // proves nothing about the values that landed.
//! writer.verify_schema()?;
//! # Ok(())
//! # }
//! ```

pub mod deadletter;
pub mod http;
pub mod rowbinary;
pub mod schema;
pub mod transport;
pub mod writer;

pub use deadletter::DeadLetter;
pub use http::{Endpoint, HttpTransport};
pub use rowbinary::{COLUMNS, INSERT_STATEMENT, encode_batch};
pub use schema::SchemaError;
pub use transport::{Sleeper, ThreadSleeper, Transport, TransportError, backoff_delay};
pub use writer::{Outcome, RetryPolicy, Stats, Writer};
