---
id: concept-scorecard-smoothing
title: "Scorecard Exponential Smoothing (CPT-0062)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-02-supplier-management }
  - { type: governed-by, target: index-adr }
---
# Scorecard Exponential Smoothing (CPT-0062)

> Damps single-period noise in supplier scores so ratings react to trends, not
> accidents: this period's grade is blended with the running history.

## Formula

    S_t = α·score_t + (1 − α)·S_{t−1}

| Symbol | Meaning | Unit |
|---|---|---|
| score_t | current-period overall score (CPT-0060) | 0–100 |
| S_{t−1} | previous smoothed score | 0–100 |
| α | responsiveness (default **0.3**) | 0–1 |

## Inputs and outputs

- **Inputs:** current and previous scores; optional α.
- **Output:** smoothed score, rounded 2 dp.

## Assumptions and limits

- Same mathematics as single exponential smoothing over demand (CPT-0002 family) —
  α = 0.3 means a one-off bad month moves the rating basis by only 30% of the shock,
  and a sustained change reaches ~92% of its level after 7 periods.
- Smoothing delays detection by design — pair with the CAP trigger on the *raw* score
  for catastrophic single-period failures (e.g. a critical recall) so smoothing never
  hides an emergency.
- First period has no S_{t−1}: seed with the first raw score.
- **Does not apply when:** re-baselining after a supplier's process change — carrying
  pre-change history misgrades the new process.

## Worked example

Previous smoothed 82.0, this period 61.0 (bad month), α = 0.3 →
`S_t = 0.3×61 + 0.7×82 = 76.3` — still APPROVED; two more such months would cross into
CONDITIONAL, correctly distinguishing trend from accident.

## Implementations

- PY: [`smooth_score`](../../../services/calc/02_supplier_management/scorecard.py)

## Governing rules

- **SUP-R*** — rating decisions use governed scores; smoothing parameters are decision-
  recorded, not per-analyst.

## Related

- CPT-0060 Scorecard · CPT-0061 Rating — the pipeline around it.
- CPT-0002 Single exponential smoothing — the same estimator over demand.

## References

- Brown (1956) / Holt (1957) — exponential smoothing lineage.
