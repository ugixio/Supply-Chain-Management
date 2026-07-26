//! U8 golden vectors — the **third** reader of `tests/golden/money.golden.json`.
//!
//! The same fixture is read by `tests/unit/golden-money.test.ts` (Jest) and
//! `services/calc/tests/test_golden_money.py` (pytest). One file, three languages: a
//! disagreement between the Rust core, the TypeScript that is being retired and the Python
//! tools becomes a red build instead of a divergence discovered months later
//! (ADR-0035 §5, ENG-R10.6).
//!
//! **These vectors must pass unchanged.** Editing the fixture to make this suite green is a
//! rule violation, not a fix.

#![allow(clippy::unwrap_used, clippy::expect_used)]

use std::fs;
use std::path::PathBuf;

use rust_decimal::Decimal;
use scm_money::{allocate_cents, divide_cents, multiply_cents, net_of_fee_cents};
use serde_json::Value;

/// The fixture lives at the repository root, shared by every language's test suite.
fn fixture() -> Value {
    let path =
        PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../tests/golden/money.golden.json");
    let text = fs::read_to_string(&path)
        .unwrap_or_else(|error| panic!("cannot read {}: {error}", path.display()));
    serde_json::from_str(&text).expect("golden fixture is not valid JSON")
}

/// A JSON number or string becomes an **exact** decimal via its textual form.
///
/// Going through the text is the point: parsing `2.5` as `f64` first and converting would
/// re-introduce the binary-float ingress the fixture exists to rule out (ENG-R4).
fn exact(value: &Value) -> Decimal {
    let text = match value {
        Value::String(s) => s.clone(),
        Value::Number(n) => n.to_string(),
        other => panic!("expected a number or numeric string, got {other}"),
    };
    Decimal::from_str_exact(&text).unwrap_or_else(|_| panic!("not an exact decimal: {text}"))
}

fn int(value: &Value) -> i64 {
    value
        .as_i64()
        .unwrap_or_else(|| panic!("expected an integer, got {value}"))
}

fn cases(fixture: &Value, section: &str) -> Vec<Value> {
    fixture[section]
        .as_array()
        .unwrap_or_else(|| panic!("fixture has no '{section}' array"))
        .clone()
}

#[test]
fn golden_multiply_cents() {
    let fixture = fixture();
    let vectors = cases(&fixture, "multiply_cents");
    assert!(
        !vectors.is_empty(),
        "fixture must carry multiply_cents vectors"
    );
    for case in vectors {
        let actual = multiply_cents(int(&case["cents"]), exact(&case["factor"]));
        assert_eq!(
            actual,
            Ok(int(&case["expected"])),
            "multiply_cents({}, {}) — {}",
            case["cents"],
            case["factor"],
            case["why"],
        );
    }
}

#[test]
fn golden_divide_cents() {
    let fixture = fixture();
    let vectors = cases(&fixture, "divide_cents");
    assert!(
        !vectors.is_empty(),
        "fixture must carry divide_cents vectors"
    );
    for case in vectors {
        let actual = divide_cents(int(&case["cents"]), exact(&case["divisor"]));
        assert_eq!(
            actual,
            Ok(int(&case["expected"])),
            "divide_cents({}, {}) — {}",
            case["cents"],
            case["divisor"],
            case["why"],
        );
    }
}

#[test]
fn golden_net_of_fee_cents() {
    let fixture = fixture();
    let vectors = cases(&fixture, "net_of_fee_cents");
    assert!(
        !vectors.is_empty(),
        "fixture must carry net_of_fee_cents vectors"
    );
    for case in vectors {
        let actual = net_of_fee_cents(int(&case["cents"]), exact(&case["fee_pct"]));
        assert_eq!(
            actual,
            Ok(int(&case["expected"])),
            "net_of_fee_cents({}, {}) — {}",
            case["cents"],
            case["fee_pct"],
            case["why"],
        );
    }
}

#[test]
fn golden_allocate_cents() {
    let fixture = fixture();
    let vectors = cases(&fixture, "allocate_cents");
    assert!(
        !vectors.is_empty(),
        "fixture must carry allocate_cents vectors"
    );
    for case in vectors {
        let weights: Vec<Decimal> = case["weights"]
            .as_array()
            .expect("weights must be an array")
            .iter()
            .map(exact)
            .collect();
        let expected: Vec<i64> = case["expected"]
            .as_array()
            .expect("expected must be an array")
            .iter()
            .map(int)
            .collect();
        let amount = int(&case["amount"]);
        let parts = allocate_cents(amount, &weights)
            .unwrap_or_else(|error| panic!("allocate_cents failed: {error}"));

        assert_eq!(
            parts, expected,
            "allocate_cents({amount}, …) — {}",
            case["why"]
        );
        // The property the vectors exist to protect, asserted independently of the values.
        assert_eq!(
            parts.iter().sum::<i64>(),
            amount,
            "allocation must sum EXACTLY to the whole — {}",
            case["why"],
        );
    }
}

/// The refund vectors pin the **two-step quantization** that resolved the CPT-0091
/// divergence: the gross line extension is quantized first (it is a document-visible cent
/// amount), then the fee applies to that stated gross. Composing the core primitives in
/// that order must reproduce the fixture exactly — one round of `qty × price × (1 − fee)`
/// would not.
#[test]
fn golden_refund_lines_two_step() {
    let fixture = fixture();
    let vectors = cases(&fixture, "refund_lines");
    assert!(
        !vectors.is_empty(),
        "fixture must carry refund_lines vectors"
    );
    for case in vectors {
        let fee_pct = exact(&case["fee_pct"]);
        let lines = case["lines"].as_array().expect("lines must be an array");
        let expected_by_line: Vec<i64> = case["expected_by_line"]
            .as_array()
            .expect("expected_by_line must be an array")
            .iter()
            .map(int)
            .collect();

        let mut by_line = Vec::with_capacity(lines.len());
        let mut gross_total = 0_i64;
        for line in lines {
            let gross = multiply_cents(int(&line["unit_price_cents"]), exact(&line["qty"]))
                .unwrap_or_else(|error| panic!("gross extension failed: {error}"));
            let net = net_of_fee_cents(gross, fee_pct)
                .unwrap_or_else(|error| panic!("net of fee failed: {error}"));
            gross_total += gross;
            by_line.push(net);
        }

        assert_eq!(
            by_line, expected_by_line,
            "refund by line — {}",
            case["why"]
        );
        assert_eq!(
            by_line.iter().sum::<i64>(),
            int(&case["expected_total"]),
            "refund total — {}",
            case["why"],
        );
        assert_eq!(
            gross_total - by_line.iter().sum::<i64>(),
            int(&case["expected_fees"]),
            "withheld fees — {}",
            case["why"],
        );
    }
}
