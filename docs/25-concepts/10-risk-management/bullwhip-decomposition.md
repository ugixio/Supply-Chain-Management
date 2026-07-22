---
id: concept-bullwhip-decomposition
title: "Bullwhip Decomposition — Lee's Four Causes (CPT-0076)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-10-risk-management }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: concept-bullwhip-theoretical-lower-bound }
---
# Bullwhip Decomposition — Lee's Four Causes (CPT-0076)

> Splits an observed bullwhip ratio into estimated contributions from Lee's causes —
> demand-signal processing, order batching, shortage gaming (price promotions proxied
> at 0) — so the intervention targets the dominant cause.

## Formula

    observed  = BWE(orders, demand)                     (CPT-0074)
    structural = LB(L, α) − 1                            (CPT-0075)
    excess    = max(0, observed − LB)
    batching_proxy = excess × periodicity_ratio × 0.5    (FFT non-DC power share)
    gaming_proxy   = excess × max(0, −corr(orders, demand)) × 0.3

| Symbol | Meaning | Unit |
|---|---|---|
| periodicity_ratio | AC power / total power of de-meaned orders (rFFT) | 0–1 |
| corr | Pearson correlation orders↔demand | −1..1 |

## Inputs and outputs

- **Inputs:** equal-length order/demand histories (≥ 4 points), lead time, α
  (default 0.2).
- **Output:** `{observed_ratio, theoretical_lower_bound, excess_amplification,
  demand_signal_processing, batching_proxy, shortage_gaming_proxy, n_periods}`.

## Assumptions and limits

- The proxies are **heuristics, not identification**: FFT periodicity reads weekly/
  monthly batching as spectral power; negative order↔demand correlation reads
  order-ahead-of-shortage behavior. The 0.5/0.3 attribution weights are conventions —
  treat the split as directional, not accounting.
- Contributions do not sum to the observed ratio by construction; the residual is
  unattributed (price-fluctuation cause has no proxy here).
- Needs the same stationarity discipline as CPT-0074.
- **Does not apply when:** history is short (< ~12 periods) — FFT and correlation are
  noise at that length.

## Worked example

Observed 3.2, LB(L=2, α=0.2) = 1.96 → excess 1.24. Orders show strong monthly spikes
(periodicity 0.6) → batching ≈ 0.37; corr = −0.4 → gaming ≈ 0.15; structural = 0.96 —
batching is the lead suspect: attack order cycles before forecasting.

## Implementations

- PY: [`bullwhip_decomposition`](../../../services/calc/10_risk_management/risk_model.py)

## Governing rules

- Advisory; interventions (VMI, batch-size changes) are planning/procurement decisions.

## Related

- CPT-0074 Ratio · CPT-0075 Lower bound — the inputs.

## References

- Lee, Padmanabhan & Whang (1997) — the four causes; Chen et al. (2000) — measurement.
