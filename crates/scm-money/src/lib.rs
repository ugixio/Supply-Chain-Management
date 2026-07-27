//! Exact money arithmetic for the SCM core.
//!
//! Money is **integer minor units** (cents). Every computation runs in exact decimal and
//! quantizes with **`ROUND_HALF_EVEN`** at defined boundaries only — never a binary float,
//! never an implicit round mid-calculation (SCM-R8 as rewritten by ADR-0019; ENG-R4).
//!
//! This crate is the single owner of that arithmetic (ADR-0035, ENG-R10): it replaces the
//! mirrored `decimal.js` implementation in `@scm/shared` and the `decimal.Decimal` one in
//! `services/calc/shared`, which existed only because rules and models lived in two
//! languages. Its correctness contract is the shared golden fixture
//! `tests/golden/money.golden.json` (U8) — the same file the Jest and pytest suites read.
//!
//! No I/O, no framework, no async: the core is pure (ENG-R10.1).

use std::error::Error;
use std::fmt;

use rust_decimal::prelude::ToPrimitive;
use rust_decimal::{Decimal, RoundingStrategy};

/// The one rounding mode for money in this system (ADR-0019 / ENG-R4).
///
/// Banker's rounding: ties go to the even neighbour, so a long run of quantizations does
/// not drift upward the way `ROUND_HALF_UP` does.
pub const MONEY_ROUNDING: RoundingStrategy = RoundingStrategy::MidpointNearestEven;

/// Failures that money arithmetic can report. Typed, never stringly — these map onto the
/// gRPC error codes declared in the proto contract (ADR-0035).
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum MoneyError {
    /// A divisor was zero or negative. Division by a non-positive divisor has no
    /// meaningful money interpretation, so it is rejected rather than saturated.
    NonPositiveDivisor,
    /// `allocate_cents` was called with no weights.
    EmptyWeights,
    /// A weight was negative; a negative share of an allocation is not defined.
    NegativeWeight,
    /// The weights summed to zero or less, so no proportion can be formed.
    NonPositiveWeightSum,
    /// Two amounts in different currencies were combined.
    CurrencyMismatch,
    /// The exact result did not fit in the integer minor-unit domain. Reported rather
    /// than wrapped: a silent wrap in money arithmetic is the worst possible outcome.
    Overflow,
}

impl fmt::Display for MoneyError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let message = match self {
            Self::NonPositiveDivisor => "divisor must be greater than zero",
            Self::EmptyWeights => "allocation requires at least one weight",
            Self::NegativeWeight => "allocation weights must be non-negative",
            Self::NonPositiveWeightSum => "allocation weights must sum to a positive value",
            Self::CurrencyMismatch => "currency mismatch",
            Self::Overflow => "amount does not fit in integer minor units",
        };
        f.write_str(message)
    }
}

impl Error for MoneyError {}

/// A monetary amount: integer minor units plus its ISO 4217 currency.
///
/// The amount is `i64` because a credit (a refund, a reversal, a negative adjustment) is a
/// first-class money value in this domain, not an error state.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Money {
    pub amount_cents: i64,
    pub currency: String,
}

impl Money {
    pub fn new(amount_cents: i64, currency: impl Into<String>) -> Self {
        Self {
            amount_cents,
            currency: currency.into(),
        }
    }

    /// Sum of two amounts in the same currency.
    pub fn add(&self, other: &Self) -> Result<Self, MoneyError> {
        self.combine(other, i64::checked_add)
    }

    /// Difference of two amounts in the same currency. May be negative (a credit).
    pub fn subtract(&self, other: &Self) -> Result<Self, MoneyError> {
        self.combine(other, i64::checked_sub)
    }

    fn combine(&self, other: &Self, op: fn(i64, i64) -> Option<i64>) -> Result<Self, MoneyError> {
        if self.currency != other.currency {
            return Err(MoneyError::CurrencyMismatch);
        }
        let amount = op(self.amount_cents, other.amount_cents).ok_or(MoneyError::Overflow)?;
        Ok(Self {
            amount_cents: amount,
            currency: self.currency.clone(),
        })
    }
}

/// Integer minor units × an exact factor, quantized once with [`MONEY_ROUNDING`].
///
/// Use for tax rates, fractional quantities and line extensions. The factor is a
/// [`Decimal`] — parse rates with `Decimal::from_str_exact("0.0825")` so no binary float
/// ever enters the calculation.
pub fn multiply_cents(cents: i64, factor: Decimal) -> Result<i64, MoneyError> {
    quantize(Decimal::from(cents) * factor)
}

/// Integer minor units ÷ a positive divisor, quantized once with [`MONEY_ROUNDING`].
///
/// Use for weighted-average unit cost and per-unit landed cost. A non-positive divisor is
/// an error, not a saturating result.
pub fn divide_cents(cents: i64, divisor: Decimal) -> Result<i64, MoneyError> {
    if divisor <= Decimal::ZERO {
        return Err(MoneyError::NonPositiveDivisor);
    }
    quantize(Decimal::from(cents) / divisor)
}

/// Amount net of a percentage deduction (restocking fee, discount), quantized once.
///
/// The `1 − pct/100` factor is formed in exact decimal, so `fee_pct = 15` deducts exactly
/// fifteen percent of the *stated* gross.
pub fn net_of_fee_cents(cents: i64, fee_pct: Decimal) -> Result<i64, MoneyError> {
    let factor = Decimal::ONE - (fee_pct / Decimal::ONE_HUNDRED);
    multiply_cents(cents, factor)
}

/// Split integer minor units across weights so the parts sum **exactly** to the whole.
///
/// Largest-remainder method: every part is floored, then the leftover units are handed out
/// one at a time in order of descending remainder (ties by position). This is why the
/// result is sum-preserving where independent rounding of each share is not — the property
/// that matters for landed-cost allocation, refund splits and journal lines.
///
/// Credits allocate too: `-10` across three equal weights yields `[-3, -3, -4]`.
pub fn allocate_cents(amount_cents: i64, weights: &[Decimal]) -> Result<Vec<i64>, MoneyError> {
    if weights.is_empty() {
        return Err(MoneyError::EmptyWeights);
    }
    if weights.iter().any(|w| *w < Decimal::ZERO) {
        return Err(MoneyError::NegativeWeight);
    }
    let total: Decimal = weights.iter().sum();
    if total <= Decimal::ZERO {
        return Err(MoneyError::NonPositiveWeightSum);
    }

    let amount = Decimal::from(amount_cents);
    let raw: Vec<Decimal> = weights.iter().map(|w| amount * w / total).collect();
    let floored: Vec<Decimal> = raw.iter().map(|r| r.floor()).collect();

    let allocated: Decimal = floored.iter().sum();
    let leftover = (amount - allocated).to_i64().ok_or(MoneyError::Overflow)?;

    let mut order: Vec<usize> = (0..raw.len()).collect();
    order.sort_by(|a, b| {
        let remainder_a = raw[*a] - floored[*a];
        let remainder_b = raw[*b] - floored[*b];
        remainder_b.cmp(&remainder_a).then(a.cmp(b))
    });

    let mut parts: Vec<i64> = floored
        .iter()
        .map(|f| f.to_i64().ok_or(MoneyError::Overflow))
        .collect::<Result<_, _>>()?;
    // Flooring can never allocate more than the whole, so the leftover is non-negative and
    // strictly smaller than the number of parts; `cycle` is defensive, not load-bearing.
    let leftover = usize::try_from(leftover).map_err(|_| MoneyError::Overflow)?;
    for index in order.iter().copied().cycle().take(leftover) {
        parts[index] = parts[index].checked_add(1).ok_or(MoneyError::Overflow)?;
    }
    Ok(parts)
}

/// The single quantization boundary: exact decimal in, integer minor units out.
fn quantize(value: Decimal) -> Result<i64, MoneyError> {
    value
        .round_dp_with_strategy(0, MONEY_ROUNDING)
        .to_i64()
        .ok_or(MoneyError::Overflow)
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::str::FromStr;

    fn dec(text: &str) -> Decimal {
        Decimal::from_str_exact(text).unwrap_or_else(|_| panic!("not an exact decimal: {text}"))
    }

    #[test]
    fn multiply_rounds_ties_to_even() {
        assert_eq!(multiply_cents(5, dec("0.5")), Ok(2));
        assert_eq!(multiply_cents(7, dec("0.5")), Ok(4));
        assert_eq!(multiply_cents(-5, dec("0.5")), Ok(-2));
    }

    #[test]
    fn multiply_avoids_the_binary_float_trap() {
        // 70 * 0.1 is 7.000000000000001 in binary floating point.
        assert_eq!(multiply_cents(70, dec("0.1")), Ok(7));
    }

    #[test]
    fn divide_rejects_a_non_positive_divisor() {
        assert_eq!(
            divide_cents(100, Decimal::ZERO),
            Err(MoneyError::NonPositiveDivisor)
        );
        assert_eq!(
            divide_cents(100, dec("-2")),
            Err(MoneyError::NonPositiveDivisor)
        );
    }

    #[test]
    fn allocation_is_sum_preserving() {
        let weights = [Decimal::ONE, Decimal::ONE, Decimal::ONE];
        let parts = allocate_cents(100, &weights).unwrap_or_default();
        assert_eq!(parts, vec![34, 33, 33]);
        assert_eq!(parts.iter().sum::<i64>(), 100);
    }

    #[test]
    fn allocation_rejects_degenerate_weights() {
        assert_eq!(allocate_cents(100, &[]), Err(MoneyError::EmptyWeights));
        assert_eq!(
            allocate_cents(100, &[dec("-1")]),
            Err(MoneyError::NegativeWeight)
        );
        assert_eq!(
            allocate_cents(100, &[Decimal::ZERO, Decimal::ZERO]),
            Err(MoneyError::NonPositiveWeightSum)
        );
    }

    #[test]
    fn money_add_and_subtract_guard_the_currency() {
        let usd = Money::new(500, "USD");
        let eur = Money::new(500, "EUR");
        assert_eq!(usd.add(&usd), Ok(Money::new(1000, "USD")));
        assert_eq!(usd.subtract(&usd), Ok(Money::new(0, "USD")));
        assert_eq!(usd.add(&eur), Err(MoneyError::CurrencyMismatch));
    }

    #[test]
    fn overflow_is_reported_not_wrapped() {
        assert_eq!(
            multiply_cents(i64::MAX, dec("1000")),
            Err(MoneyError::Overflow)
        );
        let max = Money::new(i64::MAX, "USD");
        assert_eq!(max.add(&Money::new(1, "USD")), Err(MoneyError::Overflow));
    }

    #[test]
    fn from_str_and_from_str_exact_agree_on_the_fixture_rates() {
        // Guards the parse boundary: a rate written in the fixture must be exact.
        assert_eq!(Decimal::from_str("0.0825"), Ok(dec("0.0825")));
    }
}
