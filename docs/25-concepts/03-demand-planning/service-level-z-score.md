---
id: concept-service-level-z-score
title: "Service-Level Z-Score (CPT-0003)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-27
relations:
  - { type: part-of, target: index-concepts-demand-planning }
  - { type: governed-by, target: index-adr }
---
# Service-Level Z-Score (CPT-0003)

> Converts a target cycle service level into the standard-normal multiplier that every
> statistical safety-stock formula needs.

## Definition

    z = Φ⁻¹(SL)

where `Φ⁻¹` is the inverse standard normal cumulative distribution function (the quantile
function), and `SL` is the target **cycle service level** expressed as a fraction in `(0, 1)`.

| Symbol | Meaning | Unit |
|---|---|---|
| SL | target cycle service level | fraction, `0 < SL < 1` |
| z | standard-normal multiplier | dimensionless |

## Project-chosen inputs

- **The service level itself.** `SL` is a commercial decision — it follows from service
  commitments and the cost of holding stock against the cost of a stockout. The context does not
  supply a value, and a number seen in a textbook example is not a default.

## Assumptions and limits

- **Assumes demand is normally distributed.** For skewed, lumpy or intermittent demand the
  normal quantile understates the tail, and `z` is the wrong instrument — a distribution fitted
  to the actual demand pattern is required instead.
- **This is cycle service level**, the probability of not stocking out within a replenishment
  cycle. It is **not** fill rate, which measures the fraction of demand served. Sizing to a
  fill-rate target needs the loss-function approach, which is a different calculation.
- **`Φ⁻¹` is convex above the median.** Two consequences worth stating because both have caused
  real errors: interpolating between entries of a coarse z-table always *overstates* z (a chord
  lies above a convex curve), and the cost of service rises steeply at the top — the step from
  98% to 99.9% costs roughly half again as much safety stock for under two points of service.
- **Approximation is a choice with a measurable error.** `Φ⁻¹` has no closed form. A rational
  approximation (Acklam, Moro) or an `erf⁻¹`-based routine is exact enough for planning; a
  hand-typed lookup table is not, and rounding z to two decimals biases every stock figure
  derived from it upward.
- **Undefined at the boundaries:** `SL ≤ 0` or `SL ≥ 1` has no finite quantile.

## Related

- CPT-0014 Statistical safety stock · CPT-0015 Combined-variability safety stock — the consumers
  of `z`.

## References

- ISO 3534-1:2006 — statistics vocabulary: quantile, distribution function.
- Chopra & Meindl, *Supply Chain Management*, 6th Ed., Ch. 11 (safety inventory and the cycle
  service level).
- Silver, Pyke & Peterson, *Inventory Management and Production Planning and Scheduling*, 3rd
  Ed., Ch. 7.
- Acklam, P. J., *An algorithm for computing the inverse normal cumulative distribution
  function* — the standard rational approximation, absolute error < 1.15 × 10⁻⁹.
