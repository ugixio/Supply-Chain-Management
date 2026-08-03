---
id: concept-safety-stock-coverage
title: "Safety Stock Coverage and Adequacy (CPT-0025)"
type: concept
owner: orchestrator
status: draft
since: 2026-07-20
updated: 2026-08-03
relations:
  - { type: part-of, target: index-concepts-demand-planning }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: concept-safety-stock-combined }
---
# Safety Stock Coverage and Adequacy (CPT-0025)

> Two questions about the buffer actually on the shelf: **how many days does it cover**, and **is it
> the right size** against what the model says it should be.

## Why this node exists

Computing a target safety stock (CPT-0012..0015) is the easy half; comparing it against the buffer
**actually held** is the half that gets skipped. Without it a project runs a textbook-correct method
while holding a different quantity, with no signal that the two have parted company.

## Formula

**Coverage:**

    SS_coverage_days = safety_stock_qty / ADU

where `ADU` is the average daily demand over a **stated trailing window**.

**Adequacy** — the comparison, against the modelled target (CPT-0015):

| Condition | Flag |
|---|---|
| `actual_SS < k_low × ss_target` | `under-stocked` |
| `k_low × ss_target ≤ actual_SS ≤ k_high × ss_target` | aligned |
| `actual_SS > k_high × ss_target` | `over-stocked` |

**Only the shape is fixed:** a held buffer is compared against a modelled one through a band, with
`0 < k_low ≤ 1 ≤ k_high`. The multipliers are the project's — a band copied from elsewhere imports
that organization's tolerance for stockout against carrying cost.

| Symbol | Meaning | Unit |
|---|---|---|
| safety_stock_qty | Buffer actually held | units |
| ADU | Average daily demand over the stated window | units/day |
| ss_target | Modelled target from CPT-0015 | units |
| k_low / k_high | Lower / upper band multiplier | fraction |

## Project-chosen inputs

| Decision | Why the context cannot fix it |
|---|---|
| `k_low` and `k_high` | The band expresses how the organization trades an immediate stockout against slow carrying cost. Nothing external fixes either multiplier. |
| The ADU trailing window | A short window tracks change and is noisy; a long one is stable and lags. Follows the demand pattern and the review cadence. |
| Whether a seasonal SKU uses a seasonally-matched ADU | A modelling choice; the alternative is knowingly incomparable figures across the year. |
| How a strategic buffer is annotated so it is not read as `over-stocked` | The exception exists in every estate; handling it is the project's process. |

## Assumptions and limits

- **An asymmetric band is usually the right shape; the widths are still policy.** A stockout bites
  immediately, carrying cost accrues slowly — that argues for a tighter lower bound than upper, and
  produces no number. Changing the multipliers re-bases every historical flag, so it applies forward.
- Adequacy inherits every CPT-0015 assumption — normality, independence of demand and lead time.
  Where the model is wrong, the flag is confidently wrong.
- Coverage is undefined at ADU = 0; a dead SKU shows infinite cover.

## Worked example

Continuing CPT-0015 (ss_target = 193 units, D̄ = 50 units/day), 120 units held, with
`k_low = 0.8` and `k_high = 1.5` **chosen for the illustration**:

- coverage = 120 / 50 = **2.4 days**
- lower bound = 0.8 × 193 = 154.4 → 120 < 154.4 → **`under-stocked`**
- gap = 193 − 120 = **73 units**, against the service level CPT-0015's example assumed

## Governing rules

- **DMD-R9** — a forecast, and any comparison against it, is stated with its horizon and its
  bucket. The band multipliers and the annotation requirement are project decisions, named above.
- **INV-R5** — a physical balance cannot be negative; a persistent
  `under-stocked` flag is the leading indicator that this rule is about to be tested.

## Related

- CPT-0015 Combined-variability safety stock — the target this measures against.
- CPT-0020 Days Inventory Outstanding — total days of stock; coverage is the safety-stock
  component of it.
- CPT-0018 XYZ — Z items routinely read `over-stocked` against a model that fits them poorly.

## References

- Chopra & Meindl, 6th Ed., Ch. 11; APICS CPIM 9.0, Inventory Management.
