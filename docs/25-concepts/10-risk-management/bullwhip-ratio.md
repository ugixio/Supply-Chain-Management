---
id: concept-bullwhip-ratio
title: "Bullwhip Ratio & Severity (CPT-0074)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-10-risk-management }
  - { type: governed-by, target: index-adr }
---
# Bullwhip Ratio & Severity (CPT-0074)

> Measures demand-signal amplification up the chain: the variance of the orders you
> place divided by the variance of the demand you see. A ratio of 1 means variability passes
> through unamplified — that is arithmetic, not a target. Above 1, the excess is inventory and
> capacity bought to serve noise the chain created itself.

## Formula

    BWE = Var(orders) / Var(demand)

Use the **same variance estimator on both series** — sample (`ddof = 1`) or population, but not
one of each: on short windows the two differ enough to move the ratio either side of 1.

**Severity bands over the ratio are project-chosen.** Where amplification becomes worth acting
on depends on what the chain can absorb, so this node states what the number means and stops.

| Symbol | Meaning | Unit |
|---|---|---|
| orders | order quantities placed upstream | units/period |
| demand | downstream demand observations | units/period |

## Inputs and outputs

- **Inputs:** the two series, or the variances computed from them, over identical periods. A
  handful of observations is not enough for a variance ratio to mean anything; state the minimum
  window and report `n`.
- **Output:** the ratio, and the two variances alongside it — the ratio alone hides whether it
  moved because orders got noisier or because demand got calmer.
- **Zero demand variance has no ratio.** Perfectly flat demand makes the denominator zero, so the
  honest results are "undefined" or a refusal. Returning `0` is the one option that reads as
  *no amplification* — the opposite of what a flat demand with lumpy orders actually shows.

## Assumptions and limits

- Series must cover identical periods at identical granularity — weekly orders vs
  daily demand fabricates amplification.
- Stationarity: trend/seasonality inflates both variances unevenly; de-trend or use
  matched windows (Chen et al. 2000 measurement guidance).
- A ratio < 1 means *smoothing* (orders steadier than demand) — usually deliberate
  (order levelling), not an error.
- **Does not apply when:** demand is intermittent (variance-of-zeros dominates; use
  the Croston-family view, CPT-0006).

## Worked example

Var(orders) = 3,600, Var(demand) = 1,600 → `BWE = 2.25`: the orders carry more than twice the
variability of the demand that caused them. The structural share of that comes first
(CPT-0075) — the remainder is what demand-signal sharing, batch sizes and lead times can
address, and it is cheaper to remove than to buffer.

## Project-chosen inputs

| Input | Why the project must choose it |
|---|---|
| The severity bands, if any | What amplification is worth acting on depends on what the chain can absorb |
| The variance estimator and window | The same estimator on both series, or the ratio moves for no real reason |
| How a zero-variance denominator is reported | Undefined or refused; returning zero reads as no amplification |

## Governing rules

- **SCM-R9** — the periods being compared are ISO 8601 intervals. No rule fixes an acceptable
  ratio; Lee et al. explain the causes, not a limit.

## Related

- CPT-0075 Theoretical lower bound — how much of the ratio is structural.
- CPT-0076 Decomposition — which of Lee's four causes dominates.

## References

- Lee, Padmanabhan & Whang (1997), *Management Science* 43(4).
- Chen, Drezner, Ryan & Simchi-Levi (2000), *Management Science* 46(3).
