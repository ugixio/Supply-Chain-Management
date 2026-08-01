//! RowBinary encoding for `telemetry.samples`.
//!
//! RowBinary carries no column names and no types — it is the values, back to back, in the order
//! the `INSERT` statement names its columns. That is why it is fast, and it is also the whole risk:
//! nothing in the payload would object to being read as the wrong type.
//!
//! Two consequences worth stating, because they are easy to get backwards:
//!
//! * **Order follows the statement, not the table.** Because [`INSERT_STATEMENT`] names its columns
//!   explicitly, ClickHouse maps them by name and a table-level column reorder cannot corrupt us.
//!   The risk a reorder *would* create is exactly what naming the columns removes.
//! * **A type change is the real hazard**, and it is silent. `DateTime64(3)` widened to
//!   `DateTime64(6)` would read every millisecond value as a microsecond one — a thousandfold
//!   error, in range, in the right column, with nothing failing. That is what [`crate::schema`]
//!   guards at startup, and it is a stronger check than the ordering one it replaced.
//!
//! `ingested_at` is deliberately **not** sent: the table defaults it to `now64(3)`, so arrival time
//! is stamped by the server that receives the row rather than by a client whose clock is unverified.

use scm_ingest::Sample;

/// The columns this encoder writes, with the ClickHouse type each one must have.
///
/// `LowCardinality(String)` is written as a plain `String` on the wire — the dictionary lives in the
/// table, not in the payload — so the encoder treats both identically while the guard still checks
/// the declared type.
pub const COLUMNS: [(&str, &str); 6] = [
    ("project_id", "String"),
    ("metric", "LowCardinality(String)"),
    ("ts", "DateTime64(3, 'UTC')"),
    ("value", "Float64"),
    ("environment", "LowCardinality(String)"),
    ("unit", "LowCardinality(String)"),
];

/// The statement every batch is posted with. Column order here *is* the wire order.
pub const INSERT_STATEMENT: &str = "INSERT INTO telemetry.samples \
    (project_id, metric, ts, value, environment, unit) FORMAT RowBinary";

/// Appends a LEB128 (unsigned varint) length, the encoding ClickHouse uses for `String` sizes.
fn write_varint(out: &mut Vec<u8>, mut value: u64) {
    loop {
        // Low seven bits, with the continuation bit set while more remain.
        let byte = u8::try_from(value & 0x7F).unwrap_or(0);
        value >>= 7;
        if value == 0 {
            out.push(byte);
            return;
        }
        out.push(byte | 0x80);
    }
}

fn write_string(out: &mut Vec<u8>, value: &str) {
    write_varint(out, value.len() as u64);
    out.extend_from_slice(value.as_bytes());
}

/// Encodes one sample. `ts_ms` maps directly onto `DateTime64(3)`, which *is* a millisecond count:
/// scale 3 means the underlying `Int64` is milliseconds, so no conversion is applied and none should
/// be. A negative instant (before 1970) encodes correctly as two's complement.
pub fn encode_sample(out: &mut Vec<u8>, sample: &Sample) {
    write_string(out, &sample.project_id);
    write_string(out, &sample.metric);
    out.extend_from_slice(&sample.ts_ms.to_le_bytes());
    out.extend_from_slice(&sample.value.to_le_bytes());
    write_string(out, &sample.environment);
    write_string(out, &sample.unit);
}

/// Encodes a whole batch into one contiguous body.
///
/// Capacity is reserved from a per-sample estimate rather than grown repeatedly: the batch size is
/// known, and a reallocation partway through a flush is pure waste on the hot path.
pub fn encode_batch(batch: &[Sample]) -> Vec<u8> {
    const ESTIMATED_BYTES_PER_SAMPLE: usize = 64;
    let mut out = Vec::with_capacity(batch.len() * ESTIMATED_BYTES_PER_SAMPLE);
    for sample in batch {
        encode_sample(&mut out, sample);
    }
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn varint_matches_leb128() {
        let cases: [(u64, &[u8]); 5] = [
            (0, &[0x00]),
            (1, &[0x01]),
            (127, &[0x7F]),
            (128, &[0x80, 0x01]),
            (300, &[0xAC, 0x02]),
        ];
        for (value, expected) in cases {
            let mut out = Vec::new();
            write_varint(&mut out, value);
            assert_eq!(out, expected, "varint({value})");
        }
    }

    #[test]
    fn a_sample_encodes_to_exactly_the_bytes_clickhouse_expects() {
        let sample = Sample {
            project_id: "p".to_owned(),
            metric: "deployment_frequency".to_owned(),
            ts_ms: 1_000,
            value: 1.0,
            environment: "prod".to_owned(),
            unit: "count".to_owned(),
        };
        let mut out = Vec::new();
        encode_sample(&mut out, &sample);

        let mut expected = Vec::new();
        expected.extend_from_slice(&[1, b'p']);
        expected.push(20);
        expected.extend_from_slice(b"deployment_frequency");
        expected.extend_from_slice(&1_000_i64.to_le_bytes());
        expected.extend_from_slice(&1.0_f64.to_le_bytes());
        expected.extend_from_slice(&[4, b'p', b'r', b'o', b'd']);
        expected.extend_from_slice(&[5, b'c', b'o', b'u', b'n', b't']);
        assert_eq!(out, expected);
    }

    #[test]
    fn an_empty_label_is_a_zero_length_string_not_a_null() {
        // ADR-0036 forbids Nullable on the hot columns: absence is the empty string, and on the
        // wire that is a single zero byte. Sending nothing at all would desynchronize the stream.
        let sample = Sample {
            project_id: "p".to_owned(),
            metric: "m".to_owned(),
            ts_ms: 0,
            value: 0.0,
            environment: String::new(),
            unit: String::new(),
        };
        let mut out = Vec::new();
        encode_sample(&mut out, &sample);
        assert_eq!(out[out.len() - 2..], [0, 0]);
    }

    #[test]
    fn multi_byte_utf8_is_counted_in_bytes_not_characters() {
        // A length prefix in characters would truncate the value server-side. Two-byte characters
        // are the cheapest way to catch that inversion.
        let sample = Sample {
            project_id: "ÿÿ".to_owned(),
            metric: "m".to_owned(),
            ts_ms: 0,
            value: 0.0,
            environment: String::new(),
            unit: String::new(),
        };
        let mut out = Vec::new();
        encode_sample(&mut out, &sample);
        assert_eq!(out[0], 4, "two 2-byte characters are four bytes");
    }

    #[test]
    fn a_pre_epoch_instant_survives_as_twos_complement() {
        let sample = Sample {
            project_id: "p".to_owned(),
            metric: "m".to_owned(),
            ts_ms: -1,
            value: -0.5,
            environment: String::new(),
            unit: String::new(),
        };
        let mut out = Vec::new();
        encode_sample(&mut out, &sample);
        let ts = &out[4..12];
        assert_eq!(ts, (-1_i64).to_le_bytes());
    }

    #[test]
    fn a_batch_is_the_concatenation_of_its_rows() {
        let one = Sample {
            project_id: "a".to_owned(),
            metric: "m".to_owned(),
            ts_ms: 1,
            value: 1.0,
            environment: String::new(),
            unit: String::new(),
        };
        let two = Sample {
            project_id: "b".to_owned(),
            ..one.clone()
        };
        let mut expected = Vec::new();
        encode_sample(&mut expected, &one);
        encode_sample(&mut expected, &two);
        assert_eq!(encode_batch(&[one, two]), expected);
    }

    #[test]
    fn an_empty_batch_encodes_to_nothing() {
        // Posting an empty body would be a valid but pointless request; the writer must not send it.
        assert!(encode_batch(&[]).is_empty());
    }
}
