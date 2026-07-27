---
id: concept-safety-stock-average-max
title: "Safety Stock — Average-Max Method (CPT-0013)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-26
relations:
  - { type: part-of, target: index-concepts-demand-planning }
  - { type: governed-by, target: index-adr }
---
# Safety Stock — Average-Max Method (CPT-0013)

> Cover the gap between the **worst plausible** lead-time demand and the **average** one.
> Uses observed extremes instead of standard deviations.

## Formula

    ss = (D_max · LT_max) − (D̄ · LT_avg)

| Symbol | Meaning | Unit |
|---|---|---|
| D_max, D̄ | Maximum and average daily demand | units/day |
| LT_max, LT_avg | Maximum and average lead time | days |
| ss | Safety stock | units |

Four arguments of two kinds, all positive and easy to transpose. **Pass them by name.** A
demand/lead-time swap produces a plausible number rather than an error — `D_max · LT_max` is
symmetric in appearance but not in meaning — so the mistake survives review and shows up as a
buffer that is wrong in the wrong direction.

## Inputs and outputs

- **Output:** units. Whether the result is rounded, and when, is the caller's decision — but round
  **once, at the end**: rounding the two products separately before subtracting can shift the
  buffer by a unit in either direction.
- No guard rejects `D_max < D̄` or `LT_max < LT_avg`; either produces a negative safety
  stock that the function returns without complaint.

## Assumptions and limits

- **Sensitive to outliers by construction.** A single freak demand spike or one delayed
  shipment permanently inflates the buffer, because the maximum never decays. Review the
  history window deliberately — an "all time" maximum is rarely the right input.
- Implicitly targets roughly a 100% service level against *observed* history, which is
  not the same as a stated service-level target and cannot be tuned to one.
- Requires no distributional assumption, which is its real advantage over CPT-0014 when
  history is short or clearly non-normal.
- **Does not apply when:** you need to hit a specific service level, or when maxima are
  unreliable (few observations, known data-entry errors).

## Worked example

D̄ = 50, D_max = 80 units/day; LT_avg = 7, LT_max = 10 days:

    ss = (80 × 10) − (50 × 7) = 800 − 350 = 450 units

Compare CPT-0014 on the same SKU (σ_D = 20, 95%): ⌈1.65 × 20 × √7⌉ = **88 units**. The
Average-Max buffer is 5× larger — the price of covering the joint worst case of both
demand and lead time with no probability weighting at all.

## Governing rules

- **INV-R5** — a physical balance cannot be negative; whether a shortfall is refused or recorded for investigation is the project's decision.

## Related

- CPT-0012 Days of supply — simpler still.
- CPT-0015 Combined variability — the statistical way to cover both demand and lead-time
  uncertainty, at a fraction of the stock.

## References

- Silver, Pyke & Peterson (1998), §7.3.
