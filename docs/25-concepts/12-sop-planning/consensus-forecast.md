---
id: concept-consensus-forecast
title: "Consensus Forecast (CPT-0147)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-12-sop-planning }
  - { type: governed-by, target: index-adr }
---
# Consensus Forecast (CPT-0147)

> The S&OP "one number": blending competing demand views into the plan everyone
> executes. Two mechanisms exist in the estate — statistical combination and
> human-override.

## Formula

    PY (combination — Bates & Granger):
      w_i = (1/MAPE_i) / Σ_j (1/MAPE_j)
      consensus_t = Σ_i w_i × forecast_i,t
    TS (override — S&OP meeting mechanics):
      consensus = (salesOverride ?? statistical) + marketingLift    (must be > 0)

| Symbol | Meaning | Unit |
|---|---|---|
| MAPE_i | source's historical accuracy (must be > 0) | fraction/% (consistent) |
| salesOverride / marketingLift | human adjustments per SKU-period | units |

## Inputs and outputs

- **Inputs:** one forecast per participating source, over equal horizons
  enforced; returns the blended vector.
- **Override semantics matter:** a management override *replaces* the
  statistical baseline (it does not average with it), then the lift adds.

## Assumptions and limits

- **Same concept, two different algorithms (recorded divergence):** PY implements
  forecast *combination* (weight by inverse historical error); TS implements
  S&OP *override* flow. Both are legitimate stages — combination builds the
  baseline, the meeting overrides it — but the shared name invites confusion;
  the TS record keeps `overrideReason`, which is what CPT-0024 (Forecast Value
  Added) needs to judge whether overrides help.
- Inverse-MAPE weighting assumes past accuracy predicts future accuracy and
  sources are unbiased; correlated sources get double-counted (Timmermann 2006 —
  simple averages are hard to beat).
- MAPE units must be consistent across sources (the U15b #4 percent-vs-fraction
  trap applies here too).
- **Does not apply when:** a source has no track record (no MAPE) — hold it out
  or assign a conservative prior.

## Worked example

Sources: stats (MAPE 0.10), sales (0.20), customer (0.25) →
weights 0.526/0.263/0.211; forecasts for June [1000, 1200, 900] →
consensus = 526 + 316 + 190 = **1,032**. In the meeting, sales overrides to
1,100 + launch lift 150 → TS consensus 1,250 (reason logged).

## Governing rules

- **SOP-R*** — consensus items carry override reasons
  classification feeds FVA (CPT-0024).

## Related

- CPT-0024 Forecast Value Added — judges the overrides.
- CPT-0153 MinT — makes the consensus coherent across the hierarchy.

## References

- Bates & Granger (1969); Timmermann (2006), *Handbook of Economic Forecasting*;
  Wallace, *Sales & Operations Planning* (2004).
