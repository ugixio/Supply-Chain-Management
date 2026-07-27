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

> The S&OP "one number": the single demand plan everyone executes. Reaching it takes **two
> distinct stages**, and they are often confused because they share the word *consensus*.

## Formula

**Stage 1 — statistical combination** (Bates & Granger): several forecasts become one, weighted
by past accuracy.

    w_i = (1/MAPE_i) / Σ_j (1/MAPE_j)
    combined_t = Σ_i w_i × forecast_i,t

**Stage 2 — judgemental override**: the S&OP meeting adjusts that baseline with knowledge the
history cannot contain (a launch, a promotion, a lost customer).

    consensus = override_or_baseline + named_adjustments

**These are not two implementations of one function.** Stage 1 is arithmetic over forecasts;
stage 2 is a decision recorded against one. A system that offers only stage 1 cannot represent
what the meeting decided; one that offers only stage 2 has no baseline to override. Keep both,
and keep them distinguishable — the *difference* between them is exactly what Forecast Value
Added measures (CPT-0024).

| Symbol | Meaning | Unit |
|---|---|---|
| MAPE_i | source's historical accuracy (must be > 0) | fraction or %, **consistently one** |
| named_adjustments | judgemental changes, each with a stated reason | units |

## Inputs and outputs

- **Inputs:** one forecast per participating source, over identical horizons and buckets.
- **Output:** the plan, plus the trail that produced it — the baseline, each adjustment, and the
  reason given. **An override with no recorded reason is unauditable and unmeasurable**: nobody
  can later ask whether that class of adjustment helped.
- **Override semantics must be stated:** an override that *replaces* the baseline and one that
  *averages* with it give different plans from the same meeting. Replacement is the usual reading.

## Assumptions and limits

- Inverse-error weighting assumes past accuracy predicts future accuracy and that sources are
  independent; correlated sources get double-counted. A simple average is a hard benchmark to beat
  (Timmermann 2006), so weighting must earn its complexity.
- **The accuracy units must match across sources.** One source reported as a fraction and another
  as a percentage differ by a factor of 100, and the weights come out dominated by whichever
  convention looked smaller — silently, since every weight still sums to one.
- **Does not apply when:** a source has no track record (no MAPE) — hold it out
  or assign a conservative prior.

## Worked example

Sources: statistical (MAPE 0.10), sales (0.20), customer (0.25) → weights 0.526 / 0.263 / 0.211.
Forecasts for June `[1000, 1200, 900]` → **combined = 526 + 316 + 190 = 1,032**.

The meeting then overrides to 1,100 and adds a launch lift of 150 → **consensus = 1,250**, with
both adjustments named. The judgement moved the plan 21% above the statistical baseline: that gap
is not an error, it is the claim being made — and CPT-0024 is how it gets checked afterwards.

## Governing rules

- **SOP-R4** — the consensus is **one** plan: demand, supply and finance execute the same numbers,
  or it is not a consensus. **SOP-R5** — attainment is measured against the plan as committed
  (CPT-0150), which is why the committed version must be identifiable after the fact.

## Related

- CPT-0024 Forecast Value Added — judges the overrides.
- CPT-0153 MinT — makes the consensus coherent across the hierarchy.

## References

- Bates & Granger (1969); Timmermann (2006), *Handbook of Economic Forecasting*;
  Wallace, *Sales & Operations Planning* (2004).
