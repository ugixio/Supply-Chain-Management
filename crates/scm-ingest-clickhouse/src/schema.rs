//! The startup guard that makes RowBinary safe to use.
//!
//! RowBinary sends values with no types attached, so the *only* thing standing between a schema
//! change and silently wrong data is a check like this one. It runs once, before the first insert,
//! and it refuses to start rather than writing something plausible.
//!
//! What it checks is the **declared type of each column this adapter writes**, by name. Two notes on
//! why that is the right check and not the obvious one:
//!
//! * Column *order* needs no guarding, because [`crate::rowbinary::INSERT_STATEMENT`] names its
//!   columns and ClickHouse maps named columns by name. A table reorder cannot reach us.
//! * Column *type* needs guarding badly. `DateTime64(3)` widened to `DateTime64(6)` would read
//!   every millisecond as a microsecond — a thousandfold error, in range, in the right column, and
//!   nothing anywhere would fail. `Float64` narrowed to `Float32` would misread all eight bytes.
//!
//! The query reads `system.columns`, which is ClickHouse's own catalogue: the check compares the
//! encoder against the server's truth rather than against the migration file, so a table that drifted
//! from the DDL is caught too.

use std::collections::HashMap;
use std::fmt;

use crate::rowbinary::COLUMNS;
use crate::transport::{Transport, TransportError};

/// Reads the columns of the target table, name and declared type, one per line.
const CATALOGUE_QUERY: &str = "SELECT name, type FROM system.columns \
    WHERE database = 'telemetry' AND table = 'samples' FORMAT TabSeparated";

/// Why the adapter refused to start.
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum SchemaError {
    /// The catalogue could not be read at all.
    Unreachable(TransportError),
    /// A column this adapter writes does not exist. Either the migration has not run or the column
    /// was renamed; both mean the insert would fail on every batch.
    MissingColumn { column: &'static str },
    /// The column exists with a different type. This is the case worth the whole module.
    TypeMismatch {
        column: &'static str,
        expected: &'static str,
        found: String,
    },
}

impl fmt::Display for SchemaError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Self::Unreachable(err) => {
                write!(
                    f,
                    "could not read telemetry.samples from system.columns: {err}"
                )
            }
            Self::MissingColumn { column } => write!(
                f,
                "telemetry.samples has no column '{column}' — the migrations in db/clickhouse have \
                 not been applied to this server, or the column was renamed"
            ),
            Self::TypeMismatch {
                column,
                expected,
                found,
            } => write!(
                f,
                "telemetry.samples.{column} is {found}, this adapter encodes {expected}. RowBinary \
                 carries no types, so writing anyway would store wrong values that nothing rejects"
            ),
        }
    }
}

/// A caller should be able to bubble this with `?` into whatever error type it already has: a
/// schema mismatch is a start-up failure, and start-up failures travel upward.
impl std::error::Error for SchemaError {
    fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
        match self {
            Self::Unreachable(err) => Some(err),
            _ => None,
        }
    }
}

/// Normalizes a declared type for comparison.
///
/// ClickHouse reports what the DDL declared, and two spellings of the same type are equivalent:
/// `DateTime64(3, 'UTC')` and `DateTime64(3, \'UTC\')` differ only in quoting, and whitespace inside
/// the parentheses is not meaningful. Nothing else is normalized — in particular the **scale is
/// not**, because the scale is the thing being protected.
fn normalize_type(declared: &str) -> String {
    declared
        .chars()
        .filter(|c| !c.is_whitespace() && *c != '\'' && *c != '"')
        .collect::<String>()
        .to_ascii_lowercase()
}

/// Verifies the live table against what the encoder writes. Call once, before the first insert.
pub fn verify<T: Transport>(transport: &T) -> Result<(), SchemaError> {
    let body = transport
        .query(CATALOGUE_QUERY)
        .map_err(SchemaError::Unreachable)?;
    verify_catalogue(&body)
}

/// The pure half, split out so the comparison is testable without a server.
pub fn verify_catalogue(body: &str) -> Result<(), SchemaError> {
    let mut found: HashMap<&str, &str> = HashMap::new();
    for line in body.lines() {
        let line = line.trim_end_matches('\r');
        if line.is_empty() {
            continue;
        }
        if let Some((name, declared)) = line.split_once('\t') {
            found.insert(name, declared);
        }
    }

    for (column, expected) in COLUMNS {
        let Some(declared) = found.get(column) else {
            return Err(SchemaError::MissingColumn { column });
        };
        if normalize_type(declared) != normalize_type(expected) {
            return Err(SchemaError::TypeMismatch {
                column,
                expected,
                found: (*declared).to_owned(),
            });
        }
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn live_table() -> String {
        // Exactly what `system.columns` reports for the table 0001 creates, including the column
        // this adapter deliberately does not write.
        [
            "project_id\tString",
            "metric\tLowCardinality(String)",
            "ts\tDateTime64(3, 'UTC')",
            "value\tFloat64",
            "environment\tLowCardinality(String)",
            "unit\tLowCardinality(String)",
            "ingested_at\tDateTime64(3, 'UTC')",
        ]
        .join("\n")
    }

    #[test]
    fn the_shipped_schema_passes() {
        assert_eq!(verify_catalogue(&live_table()), Ok(()));
    }

    #[test]
    fn a_widened_datetime_scale_is_refused() {
        // The defect this module exists for: milliseconds read as microseconds, a thousandfold
        // error with every value in range and nothing failing.
        let drifted = live_table().replace("ts\tDateTime64(3, 'UTC')", "ts\tDateTime64(6, 'UTC')");
        assert_eq!(
            verify_catalogue(&drifted),
            Err(SchemaError::TypeMismatch {
                column: "ts",
                expected: "DateTime64(3, 'UTC')",
                found: "DateTime64(6, 'UTC')".to_owned(),
            })
        );
    }

    #[test]
    fn a_narrowed_float_is_refused() {
        let drifted = live_table().replace("value\tFloat64", "value\tFloat32");
        assert!(matches!(
            verify_catalogue(&drifted),
            Err(SchemaError::TypeMismatch {
                column: "value",
                ..
            })
        ));
    }

    #[test]
    fn a_missing_column_names_the_likely_cause() {
        let empty = "";
        assert_eq!(
            verify_catalogue(empty),
            Err(SchemaError::MissingColumn {
                column: "project_id"
            })
        );
    }

    #[test]
    fn quoting_and_spacing_of_a_timezone_do_not_matter() {
        // The same type, spelled three ways the server may report. Rejecting these would be a
        // false alarm that trains an operator to ignore the gate.
        for spelling in [
            "ts\tDateTime64(3,'UTC')",
            "ts\tDateTime64(3, \"UTC\")",
            "ts\tDateTime64( 3 , 'UTC' )",
        ] {
            let variant = live_table().replace("ts\tDateTime64(3, 'UTC')", spelling);
            assert_eq!(verify_catalogue(&variant), Ok(()), "{spelling}");
        }
    }

    #[test]
    fn an_extra_column_on_the_table_is_not_an_error() {
        // The adapter names its columns, so a column it does not write is none of its business —
        // `ingested_at` is exactly that, and a future additive migration must not break ingest.
        let extended = format!("{}\nregion\tLowCardinality(String)", live_table());
        assert_eq!(verify_catalogue(&extended), Ok(()));
    }

    #[test]
    fn a_lowcardinality_column_may_not_silently_become_plain() {
        // Not a correctness bug on the wire — LowCardinality(String) and String encode identically —
        // but it is a real schema drift with a large storage cost, and the guard is where it shows.
        let drifted = live_table().replace("metric\tLowCardinality(String)", "metric\tString");
        assert!(matches!(
            verify_catalogue(&drifted),
            Err(SchemaError::TypeMismatch {
                column: "metric",
                ..
            })
        ));
    }
}
