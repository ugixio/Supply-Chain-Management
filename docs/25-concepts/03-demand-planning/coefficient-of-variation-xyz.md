---
id: concept-coefficient-of-variation-xyz
title: "Coefficient of Variation and XYZ Classification (CPT-0018)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-26
relations:
  - { type: part-of, target: index-concepts-demand-planning }
  - { type: governed-by, target: index-adr }
---
# Coefficient of Variation and XYZ Classification (CPT-0018)

> CV measures demand **variability** on a scale-free basis, so a fast mover and a slow mover can
> be compared. XYZ turns that continuous measure into classes; crossed with ABC (consumption
> value) it gives the grid many organizations use to pick a replenishment policy.

## Formula

    CV = σ / μ

where `σ` is the standard deviation of demand over the measurement period and `μ` its mean.
XYZ then partitions the CV range into classes, ordered from most to least predictable.

| Symbol | Meaning | Unit |
|---|---|---|
| σ | standard deviation of demand | same unit as demand |
| μ | mean demand | same unit as demand |
| CV | coefficient of variation | dimensionless |

## Project-chosen inputs

- **The class boundaries.** Common convention puts the first cut near 0.1 and the second near
  0.25, but these are conventions, not derived optima — they were chosen because they sort a
  typical assortment usefully, and a different assortment sorts better at different cuts.
- **The number of classes and what each obliges** — which replenishment policy follows from
  which class is a planning decision.
- **The bucketing period** (see the limits below — it changes the answer).
- **The estimator for σ:** population (`ddof = 0`) or sample (`ddof = 1`). This is not a
  technicality. On a short history the sample estimator is materially larger — with ten
  observations, by roughly 5% — which is enough to move a borderline SKU across a class
  boundary. Whichever is chosen must be used consistently, because two SKUs measured with
  different estimators are not comparable.

## Inputs and outputs

- **Inputs:** a demand history over a stated period, or its moments if computed elsewhere.
- **Output:** the CV, and the class it falls into. CV is **undefined at μ = 0** — a SKU with no
  demand has no variability to speak of, and reporting an infinite CV is a way of saying the
  measure does not apply rather than a value to classify.

## Assumptions and limits

- CV is undefined at μ = 0 and unstable at small μ — for slow movers a large CV reflects
  the small denominator, not genuine volatility. Intermittent items should be routed to
  Croston (CPT-0006) rather than judged by CV alone.
- **CV depends on the bucketing period.** Daily demand almost always shows a higher CV
  than the same demand aggregated weekly. A SKU can be "Z" daily and "X" monthly, so the
  classification is only comparable across SKUs measured on the same calendar.
- **Changing a boundary reclassifies history.** Because the classes drive replenishment policy,
  a boundary change is applied forward deliberately rather than retroactively — otherwise past
  decisions look wrong against a rule that did not exist when they were made.
- Assumes the history is representative — a promotion or a one-off outage inflates σ and
  misclassifies an otherwise stable item.

## Worked example

`demand = [100, 105, 95, 110, 90]` — μ = 100:

- population σ (`ddof = 0`) = 7.07 → CV = **0.0707**
- sample σ (`ddof = 1`) = 7.91 → CV = **0.0791**

The two estimators differ by 12% on five observations. Here both fall well inside the most
predictable class either way; a series sitting near a boundary would not, which is why the
estimator is part of the definition and not an implementation detail.

## Governing rules

- None. Classification is a planning aid, not an invariant — the department's `rule.md` governs
  what may be done with the result.

## Related

- CPT-0014 Statistical safety stock — X items justify the statistical method.
- CPT-0017 EOQ — appropriate for X, misleading for Z.
- CPT-0006 Croston — where Z items with many zeros should go instead.

## References

- Silver, Pyke & Peterson (1998), Ch. 3; APICS Dictionary 16th Ed.
