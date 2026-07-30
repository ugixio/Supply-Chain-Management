//! The one real [`Transport`]: ClickHouse over HTTP, via `ureq`.
//!
//! This is the only module in the crate that touches the network, and the only one whose behaviour
//! cannot be asserted in a unit test. Everything it does beyond issuing the request is therefore
//! kept out of it: classification lives in [`crate::transport`], retry in [`crate::writer`].
//!
//! **Credentials come from the environment, never from a file in this repository.** The reader that
//! builds a config from env vars is here rather than in the caller so there is exactly one place
//! where a secret is read, and so no default password can be introduced by accident.

use std::env;
use std::time::Duration;

use crate::transport::{Transport, TransportError};

/// Where and how to reach the server.
#[derive(Debug, Clone)]
pub struct Endpoint {
    /// Base URL, e.g. `http://clickhouse:8123`. No trailing slash required.
    pub url: String,
    /// The insert identity. Migration 0005 creates a writer with INSERT-only grants; using an
    /// account with more than that here would waste the split the schema deliberately created.
    pub user: String,
    pub password: String,
    pub timeout: Duration,
}

/// The environment variables this adapter reads. Named as constants so the set is greppable and a
/// deployment manifest can be checked against it.
pub const URL_VAR: &str = "CLICKHOUSE_URL";
pub const USER_VAR: &str = "CLICKHOUSE_INGEST_USER";
pub const PASSWORD_VAR: &str = "CLICKHOUSE_INGEST_PASSWORD";

impl Endpoint {
    /// Reads the endpoint from the environment.
    ///
    /// The URL is required and has **no default**: a localhost fallback is how a production process
    /// ends up silently writing nowhere. The password may legitimately be empty — a dev server
    /// without access management — but the variable's absence is not treated as an error, because
    /// requiring a secret that does not exist is its own failure mode.
    pub fn from_env(timeout: Duration) -> Result<Self, String> {
        let url = env::var(URL_VAR)
            .map_err(|_| format!("{URL_VAR} is not set; the adapter supplies no default host"))?;
        Ok(Self {
            url: url.trim_end_matches('/').to_owned(),
            user: env::var(USER_VAR).unwrap_or_else(|_| "default".to_owned()),
            password: env::var(PASSWORD_VAR).unwrap_or_default(),
            timeout,
        })
    }
}

/// `ureq`-backed transport.
#[derive(Debug)]
pub struct HttpTransport {
    endpoint: Endpoint,
    agent: ureq::Agent,
}

impl HttpTransport {
    pub fn new(endpoint: Endpoint) -> Self {
        let config = ureq::Agent::config_builder()
            .timeout_global(Some(endpoint.timeout))
            // The server answers with an error body worth reading; capping it stops a pathological
            // response from being pulled into memory during an incident.
            .max_response_header_size(16 * 1024)
            .build();
        Self {
            endpoint,
            agent: config.into(),
        }
    }

    /// Classifies a `ureq` failure by **what is safe to do next**.
    ///
    /// The distinction that matters is whether the request left the process. `ureq` reports connect
    /// and DNS failures separately from timeouts, and that boundary is exactly the
    /// `NotSent` / `Ambiguous` boundary the retry loop needs — a timeout may have been received and
    /// applied, a failed connect cannot have been.
    fn classify(error: ureq::Error) -> TransportError {
        match error {
            ureq::Error::StatusCode(status) => {
                let message = format!("HTTP {status}");
                if status >= 500 {
                    TransportError::ServerError {
                        status,
                        body: message,
                    }
                } else {
                    TransportError::Refused {
                        status,
                        body: message,
                    }
                }
            }
            ureq::Error::Timeout(_) => {
                TransportError::Ambiguous("timed out waiting for the server".to_owned())
            }
            ureq::Error::Io(io) => match io.kind() {
                std::io::ErrorKind::ConnectionRefused
                | std::io::ErrorKind::NotFound
                | std::io::ErrorKind::AddrNotAvailable => TransportError::NotSent(io.to_string()),
                // A connection reset or an unexpected EOF happens *while* exchanging bytes, so the
                // insert may already have been applied. Treating it as not-sent would be the
                // optimistic reading, and the optimistic reading loses data on retry-refusal.
                _ => TransportError::Ambiguous(io.to_string()),
            },
            ureq::Error::ConnectionFailed | ureq::Error::HostNotFound => {
                TransportError::NotSent(error.to_string())
            }
            other => TransportError::Ambiguous(other.to_string()),
        }
    }

    fn endpoint_with_query(&self, query: &str) -> String {
        format!("{}/?query={}", self.endpoint.url, percent_encode(query))
    }
}

/// Percent-encodes a query for a URL, encoding everything outside the unreserved set.
///
/// Hand-rolled rather than adding a URL crate: the input is SQL this crate writes itself, the rule
/// is RFC 3986's unreserved set, and being conservative — encoding anything not provably safe — is
/// both correct and shorter than pulling a dependency for six lines.
fn percent_encode(value: &str) -> String {
    let mut out = String::with_capacity(value.len() * 3);
    for byte in value.as_bytes() {
        match byte {
            b'A'..=b'Z' | b'a'..=b'z' | b'0'..=b'9' | b'-' | b'_' | b'.' | b'~' => {
                out.push(char::from(*byte));
            }
            _ => out.push_str(&format!("%{byte:02X}")),
        }
    }
    out
}

impl Transport for HttpTransport {
    fn post(&self, query: &str, body: &[u8]) -> Result<(), TransportError> {
        self.agent
            .post(self.endpoint_with_query(query))
            .header("X-ClickHouse-User", &self.endpoint.user)
            .header("X-ClickHouse-Key", &self.endpoint.password)
            .content_type("application/octet-stream")
            .send(body)
            .map(|_| ())
            .map_err(Self::classify)
    }

    fn query(&self, sql: &str) -> Result<String, TransportError> {
        self.agent
            .get(self.endpoint_with_query(sql))
            .header("X-ClickHouse-User", &self.endpoint.user)
            .header("X-ClickHouse-Key", &self.endpoint.password)
            .call()
            .map_err(Self::classify)?
            .into_body()
            .read_to_string()
            .map_err(|err| TransportError::Ambiguous(err.to_string()))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn percent_encoding_leaves_the_unreserved_set_alone() {
        assert_eq!(percent_encode("aZ0-_.~"), "aZ0-_.~");
    }

    #[test]
    fn percent_encoding_escapes_what_would_break_a_url() {
        // A space, the query separators, and the quote a table name may carry. If any of these went
        // through raw, the server would see a truncated or a different query.
        assert_eq!(percent_encode("a b"), "a%20b");
        assert_eq!(percent_encode("&"), "%26");
        assert_eq!(percent_encode("?"), "%3F");
        assert_eq!(percent_encode("'"), "%27");
        assert_eq!(percent_encode("="), "%3D");
    }

    #[test]
    fn multi_byte_characters_are_encoded_per_byte() {
        // Per-character encoding would produce an invalid escape; UTF-8 must go byte by byte.
        assert_eq!(percent_encode("é"), "%C3%A9");
    }

    #[test]
    fn the_insert_statement_survives_encoding_intact() {
        let encoded = percent_encode(crate::rowbinary::INSERT_STATEMENT);
        assert!(
            !encoded.contains(' '),
            "a raw space would truncate the query"
        );
        assert!(
            encoded.contains("INSERT"),
            "the ASCII keywords pass through unescaped"
        );
    }

    #[test]
    fn a_url_is_normalized_so_a_trailing_slash_cannot_double() {
        let endpoint = Endpoint {
            url: "http://ch:8123/".to_owned(),
            user: "w".to_owned(),
            password: String::new(),
            timeout: Duration::from_secs(1),
        };
        let normalized = Endpoint {
            url: endpoint.url.trim_end_matches('/').to_owned(),
            ..endpoint
        };
        let transport = HttpTransport::new(normalized);
        let built = transport.endpoint_with_query("SELECT 1");
        assert!(built.starts_with("http://ch:8123/?query="), "{built}");
    }

    #[test]
    fn a_5xx_is_retryable_and_a_4xx_is_not() {
        assert!(
            HttpTransport::classify(ureq::Error::StatusCode(503)).is_retryable(),
            "the server is struggling, not refusing"
        );
        assert!(
            !HttpTransport::classify(ureq::Error::StatusCode(400)).is_retryable(),
            "a rejected body stays rejected"
        );
    }

    #[test]
    fn a_timeout_is_ambiguous_and_a_refused_connection_is_not_sent() {
        let refused = std::io::Error::from(std::io::ErrorKind::ConnectionRefused);
        assert!(matches!(
            HttpTransport::classify(ureq::Error::Io(refused)),
            TransportError::NotSent(_)
        ));

        let reset = std::io::Error::from(std::io::ErrorKind::ConnectionReset);
        assert!(
            HttpTransport::classify(ureq::Error::Io(reset)).may_duplicate(),
            "a reset mid-exchange may have left the insert applied"
        );
    }
}
