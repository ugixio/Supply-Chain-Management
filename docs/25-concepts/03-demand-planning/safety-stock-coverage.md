---
id: concept-safety-stock-coverage
title: "Safety Stock Coverage and Adequacy (CPT-0025)"
type: concept
owner: orchestrator
status: draft
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-concepts-demand-planning }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: concept-safety-stock-combined }
---
# Safety Stock Coverage and Adequacy (CPT-0025)

> Two questions about the buffer actually on the shelf: **how many days does it cover**,
> and **is it the right size** compared with what the model says it should be.

## Why this node exists

Computing a target safety stock (CPT-0012..0015) is the easy half. The half that gets skipped is
comparing that target against the buffer **actually held** — and without it, the calculation is
advice nobody checked. A project can be running a textbook-correct safety-stock method and holding
a completely different quantity, indefinitely, with no signal that the two have parted company.

## Formula

**Coverage:**

    SS_coverage_days = safety_stock_qty / ADU

where `ADU` is the **trailing 90-day** average daily demand.

**Adequacy** (against the Method-4 target, CPT-0015):

| Condition | Flag |
|---|---|
| `actual_SS < 0.8 × ss_method4` | `under-stocked` |
| `0.8 × ss_method4 ≤ actual_SS ≤ 1.5 × ss_method4` | aligned |
| `actual_SS > 1.5 × ss_method4` | `over-stocked` |

| Symbol | Meaning | Unit |
|---|---|---|
| safety_stock_qty | Buffer actually held | units |
| ADU | Trailing 90-day average daily demand | units/day |
| ss_method4 | Modelled target from CPT-0015 | units |

## Assumptions and limits

- **The band is deliberately asymmetric** — 0.8× below, 1.5× above. Under-stocking causes
  stockouts immediately, so the tolerance is tight; over-stocking costs carrying cost
  slowly, so the tolerance is loose. The numbers are policy, not derived optima, and
  changing them is a policy decision applied forward.
- **ADU's 90-day window fights seasonality.** For a seasonal SKU the coverage figure swings
  by the seasonal ratio without the buffer changing at all, so coverage days are not
  comparable across the year. Compare against a seasonally-matched ADU where it matters.
- Adequacy inherits every CPT-0015 assumption — normality, independence of demand and lead
  time. Where the model is wrong, the flag is confidently wrong.
- **Strategic buffers are legitimate exceptions.** Pre-build for a plant shutdown, a
  pre-Brexit stockpile or a single-source hedge will read `over-stocked`. These
  must be annotated, not silently normalised — and never auto-corrected.
- Coverage is undefined at ADU = 0; a dead SKU shows infinite days of cover.

## Worked example

Continuing CPT-0015 (ss_method4 = 193 units, D̄ = 50 units/day), with 120 units actually
held:

- coverage = 120 / 50 = **2.4 days**
- lower bound = 0.8 × 193 = 154.4 → 120 < 154.4 → **`under-stocked`**
- gap to target = 193 − 120 = **73 units** to reach the 95% service level

## Governing rules

- **DMD-R9** — a forecast, and any comparison against it, is stated with its horizon and bucket.8× / 1.5× adequacy bands and the annotation requirement.
- **INV-R5** — a physical balance cannot be negative; a persistent
  `under-stocked` flag is the leading indicator that this rule is about to be tested.

## Related

- CPT-0015 Combined-variability safety stock — the target this measures against.
- CPT-0020 Days Inventory Outstanding — total days of stock; coverage is the safety-stock
  component of it.
- CPT-0018 XYZ — Z items routinely read `over-stocked` against a model that fits them poorly.

## References

- Chopra & Meindl, 6th Ed., Ch. 11; APICS CPIM 9.0, Inventory Management.
