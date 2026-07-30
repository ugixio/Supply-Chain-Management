//! The seam between this adapter and the network.
//!
//! Everything interesting in this crate — retry classification, dead-lettering, the schema guard —
//! is logic that must be testable without a server, so the network sits behind a trait with one
//! real implementation. That is not indirection for its own sake: the failure modes being handled
//! are *unreachable server* and *ambiguous response*, and neither can be exercised reliably against
//! a live ClickHouse.

use std::fmt;
use std::time::Duration;

/// Why a request did not succeed, classified by **what is safe to do next** rather than by HTTP
/// status. That is the only classification the retry loop can act on.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum TransportError {
    /// The request never reached the server: DNS, connect, or TLS failure. Retrying cannot
    /// duplicate anything, because nothing arrived.
    NotSent(String),
    /// The request was sent and the outcome is **unknown** — a timeout or a dropped connection
    /// while waiting. The insert may well have succeeded. Retrying is at-least-once by definition,
    /// which is the semantics chosen for this tier (the raw table is a 14-day buffer, never truth).
    Ambiguous(String),
    /// The server answered and refused. A 4xx will refuse the identical body forever, so this is
    /// terminal: retrying it only delays the dead-letter.
    Refused { status: u16, body: String },
    /// The server answered 5xx. It arrived, so the outcome is as unknown as `Ambiguous`, but it is
    /// worth distinguishing in logs: this one is the server's problem, not the network's.
    ServerError { status: u16, body: String },
}

impl TransportError {
    /// Whether the retry loop should try again.
    ///
    /// `Refused` is the only terminal case. `Ambiguous` and `ServerError` are retried in full
    /// knowledge that a duplicate is possible — the alternative is discarding data that is probably
    /// absent, and for this tier that trade was decided deliberately.
    pub fn is_retryable(&self) -> bool {
        !matches!(self, Self::Refused { .. })
    }

    /// Whether a retry of this error can produce a duplicate row. Reported so an operator can tell
    /// a clean retry from an at-least-once one instead of inferring it.
    pub fn may_duplicate(&self) -> bool {
        matches!(self, Self::Ambiguous(_) | Self::ServerError { .. })
    }
}

impl fmt::Display for TransportError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::NotSent(why) => write!(f, "request not sent: {why}"),
            Self::Ambiguous(why) => write!(f, "outcome unknown after sending: {why}"),
            Self::Refused { status, body } => write!(f, "refused with {status}: {body}"),
            Self::ServerError { status, body } => write!(f, "server error {status}: {body}"),
        }
    }
}

impl std::error::Error for TransportError {}

/// A ClickHouse HTTP endpoint.
pub trait Transport {
    /// Posts a body against a query. Used for `INSERT … FORMAT RowBinary`.
    fn post(&self, query: &str, body: &[u8]) -> Result<(), TransportError>;

    /// Runs a read query and returns its body. Used by the schema guard.
    fn query(&self, sql: &str) -> Result<String, TransportError>;
}

/// Waiting between attempts, injected so the retry tests neither sleep nor flake.
///
/// The core crate refuses to read a clock at all; an adapter legitimately must, so the discipline
/// here is narrower — the *decision* about how long to wait is pure, and only the waiting itself is
/// behind this trait.
pub trait Sleeper {
    fn sleep(&self, duration: Duration);
}

/// The real one.
#[derive(Debug, Default, Clone, Copy)]
pub struct ThreadSleeper;

impl Sleeper for ThreadSleeper {
    fn sleep(&self, duration: Duration) {
        std::thread::sleep(duration);
    }
}

/// Delay before attempt `attempt` (1-based), doubling from `base` and capped at `max`.
///
/// Pure, and deliberately **without jitter here**: jitter belongs to the caller that owns a source
/// of randomness, and a pure backoff is a function a test can assert. The cap matters more than the
/// curve — an uncapped doubling reaches hours, which for a 14-day retention tier means the batch is
/// worthless long before the next attempt.
pub fn backoff_delay(attempt: u32, base: Duration, max: Duration) -> Duration {
    let shift = attempt.saturating_sub(1).min(16);
    base.saturating_mul(1_u32 << shift).min(max)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn backoff_doubles_then_holds_at_the_cap() {
        let base = Duration::from_millis(100);
        let max = Duration::from_secs(2);
        assert_eq!(backoff_delay(1, base, max), Duration::from_millis(100));
        assert_eq!(backoff_delay(2, base, max), Duration::from_millis(200));
        assert_eq!(backoff_delay(3, base, max), Duration::from_millis(400));
        assert_eq!(backoff_delay(5, base, max), Duration::from_millis(1_600));
        assert_eq!(backoff_delay(6, base, max), max, "capped, not 3.2s");
        assert_eq!(
            backoff_delay(40, base, max),
            max,
            "a large attempt cannot overflow"
        );
    }

    #[test]
    fn only_a_refusal_is_terminal() {
        assert!(TransportError::NotSent("dns".into()).is_retryable());
        assert!(TransportError::Ambiguous("timeout".into()).is_retryable());
        assert!(
            TransportError::ServerError {
                status: 503,
                body: String::new()
            }
            .is_retryable()
        );
        assert!(
            !TransportError::Refused {
                status: 400,
                body: "bad type".into()
            }
            .is_retryable(),
            "a body the server rejects will be rejected identically forever"
        );
    }

    #[test]
    fn duplicate_risk_is_reported_separately_from_retryability() {
        // Both are retryable; only one can double a row. Collapsing them would hide the trade.
        assert!(!TransportError::NotSent("connect refused".into()).may_duplicate());
        assert!(TransportError::Ambiguous("read timeout".into()).may_duplicate());
    }
}
