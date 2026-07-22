---
id: concept-mint-reconciliation
title: "MinT Hierarchical Forecast Reconciliation (CPT-0153)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-12-sop-planning }
  - { type: governed-by, target: index-adr }
---
# MinT Hierarchical Forecast Reconciliation (CPT-0153)

> Makes hierarchical forecasts coherent — SKU forecasts that sum exactly to the
> family and total forecasts — by optimally combining the base forecasts at every
> level instead of forcing top-down or bottom-up.

## Formula

    ŷ_reconciled = S · (SᵀW⁻¹S)⁻¹ SᵀW⁻¹ · ŷ_base
    S: summing matrix (rows = all series [aggregate…bottom], cols = bottom series)
    W: forecast-error covariance — approximated here as diag(residual variances)
       (all equal → OLS; unequal → WLS variant of MinT)

| Symbol | Meaning | Unit |
|---|---|---|
| ŷ_base | (n_series × horizon) incoherent base forecasts | units |
| residual_variances | per-series in-sample error variances | units² |

## Inputs and outputs

- **Inputs:** shape-validated base-forecast matrix, S, variance vector;
  zero variances floored at 1e-10.
- **Output:** reconciled (n_series × horizon) — bottom estimates via
  P = (SᵀW⁻¹S)⁻¹SᵀW⁻¹, then S·bottom, so every level sums exactly.

## Assumptions and limits

- The diagonal-W shortcut ignores error *correlations* between series — the full
  MinT uses a shrunk covariance (Wickramasuriya et al. 2019); the WLS variant here
  trades a little accuracy for robustness at S&OP scale (52-week horizons,
  documented in the code).
- Reconciliation redistributes toward series with **lower** error variance —
  noisy SKUs get adjusted, stable aggregates barely move; that is the point.
- Coherence is a *structural* property the S matrix must encode correctly —
  wrong hierarchy in S reconciles to the wrong totals with full confidence.
- Negative reconciled values are possible (no non-negativity constraint) —
  clip-and-redistribute for planning use (recorded caveat).
- **Does not apply when:** the hierarchy is temporal (weeks→months) — temporal
  reconciliation is a sibling method, not this implementation.

## Worked example

Two SKUs forecast 60 and 55; the total series independently forecasts 100 —
incoherent (115 ≠ 100). With equal variances, MinT lands total ≈ 110, SKUs
≈ 57.5/52.5 — every level moved toward the evidence, and the sum is exact.

## Implementations

- PY: [`mint_reconcile`](../../../services/calc/12_sop_planning/sop.py)

## Governing rules

- **SOP-R*** — the published S&OP numbers are the reconciled set (one-number
  principle).

## Related

- CPT-0147 Consensus — produces the base forecasts.
- CPT-0011 algorithm selection — the per-series base forecasting.

## References

- Hyndman, Ahmed, Athanasopoulos & Shang (2011), *CSDA* 55(9);
  Wickramasuriya, Athanasopoulos & Hyndman (2019), *JASA* 114(526) — MinT.
