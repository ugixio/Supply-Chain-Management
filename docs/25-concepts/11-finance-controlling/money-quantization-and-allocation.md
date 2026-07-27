---
id: concept-money-quantization-and-allocation
title: "Money Quantization & Sum-Preserving Allocation (CPT-0154)"
type: concept
owner: orchestrator
status: active
since: 2026-07-26
updated: 2026-07-26
relations:
  - { type: part-of, target: index-concepts-11-finance-controlling }
  - { type: governed-by, target: index-adr }
---
# Money Quantization & Sum-Preserving Allocation (CPT-0154)

> The two primitives under every money calculation: **when** an exact decimal becomes an
> integer cent amount, and **how** a whole splits into parts that still add up to it.

## Formula

    quantize(x)              = round_half_even(x, 0)          # ties → even neighbour

    multiply_cents(c, f)     = quantize(c × f)
    divide_cents(c, d)       = quantize(c ÷ d),        d > 0
    net_of_fee_cents(c, p)   = quantize(c × (1 − p/100))

    allocate(A, w₁..wₙ):                                       # largest remainder
      raw_i   = A × w_i / Σw
      part_i  = ⌊raw_i⌋
      L       = A − Σ part_i                                   # 0 ≤ L < n
      hand one extra unit to the L largest (raw_i − part_i), ties by position
      ⇒ Σ part_i = A  exactly

| Symbol | Meaning | Unit |
|---|---|---|
| c, A | amount | integer minor units (cents) |
| f, p, d | factor, percentage, divisor | exact decimal, never a float |
| w_i | allocation basis for part i | exact decimal, ≥ 0, Σw > 0 |
| L | leftover units after flooring | integer cents |

## Inputs and outputs

- **Inputs:** integer minor units; rates and factors as **exact decimals** — written as text
  (`"0.0825"`), so the value used is the value written.
- **Outputs:** integer minor units; negative amounts are first-class (credits, reversals).
- **Errors are typed, never silent:** non-positive divisor · empty weights · negative weight ·
  non-positive weight sum · currency mismatch · overflow (reported, never wrapped).

## Assumptions and limits

- **One rounding mode, at boundaries only.** `ROUND_HALF_EVEN`: ties go to the even neighbour,
  so a long run of quantizations does not drift upward the way half-up does. Intermediate
  values are never rounded (SCM-R8 per ADR-0019, ENG-R4).
- **Quantization order is part of the definition.** Where a document states a gross and then
  deducts a fee, the gross quantizes first (**two-step**); one-step
  `qty × price × (1 − fee)` differs and is wrong wherever the gross is externally visible —
  the CPT-0091 divergence the golden vectors resolved.
- **Independent rounding of shares does not reconcile.** Largest-remainder is the cheapest
  exactly sum-preserving method — not uniquely *fair*: it favours the earliest of tied
  remainders, hence ties break by position and are reproducible.
- **Does not apply to:** non-monetary ratios and statistics (Python's lane, full precision),
  or currency conversion (its own concept, with rate provenance).

## Worked example

`2.5 × 1299¢` at a 15% fee, **two-step**: gross `= quantize(3247.5) = 3248` (tie → even),
then `3248 × 0.85 = 2760.8 → 2761`. One-step gives `2760` — one cent apart, and reproducibly
wrong on the credit note.

Allocation of `1,172,000¢` by value over `600k / 300k / 100k` → `703,200 / 351,600 / 117,200`
(exact). Allocation of `−10¢` over three equal weights → `−3 / −3 / −4`.

## Governing rules

- **SCM-R8** — money is arbitrary-precision decimal, integer minor units at rest (ADR-0019).
- **ENG-R4** — no float holds or computes money; rounding explicit, at boundaries only.
  **ENG-R5** — money crosses the wire as a string.
- **ENG-R10** — the Rust core is the single owner; ports pass these vectors unchanged.

## Related

- CPT-0111 Landed cost & allocation — its BY_VALUE spread is this primitive.
- CPT-0091 Refund — where the two-step rule originates.
- Inventory valuation (05), goods receipt (01) — call sites migrated off `Math.round`.

## References

- IEEE 754-2019 §4.3.3 (roundTiesToEven) — the rounding rule used here.
- Balinski & Young, *Fair Representation* (Yale, 1982) — largest-remainder apportionment.
- IAS 2 *Inventories* §§10–11 (what capitalizes, hence what gets allocated).
