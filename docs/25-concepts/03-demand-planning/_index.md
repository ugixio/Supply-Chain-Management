---
id: index-concepts-demand-planning
title: "Concepts — Demand Planning (03)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-27
relations:
  - { type: part-of, target: index-concepts }
  - { type: governed-by, target: index-adr }
  - { type: traces-to, target: rule-demand-planning }
---
# Concepts — Demand Planning (03)

> The concept catalogue for **Demand Planning (03)**: what each concept *means*,
> the formula where one is canonical, its assumptions and limits, and the standard or
> regulation that fixes it. Nodes **define**; they hold no threshold, target, weighting or
> mandated method, and they own no code (ADR-0037). Values a project must choose are named
> as project-chosen inputs and left unset.
>
> Departmental law lives in [40-contexts/03-demand-planning/rule.md](../../40-contexts/03-demand-planning/rule.md).

## Catalogue

### Time-series forecasting

| ID | Concept | Use when |
|---|---|---|
| [CPT-0001](simple-moving-average.md) | Simple Moving Average | Stable demand, no trend or season |
| [CPT-0002](single-exponential-smoothing.md) | Single Exponential Smoothing | Stationary demand, recent data weighted |
| [CPT-0004](holts-linear-method.md) | Holt's Linear Method | Trend, no seasonality |
| [CPT-0005](holt-winters.md) | Holt-Winters | Trend **and** seasonality (≥ 2 seasons of history) |
| [CPT-0011](algorithm-selection.md) | Algorithm selection | Choosing among the above from the series itself |

### Intermittent demand

| ID | Concept | Use when |
|---|---|---|
| [CPT-0006](crostons-method.md) | Croston's Method | Frequent zeros — spare parts, slow movers |
| [CPT-0007](syntetos-boylan-approximation.md) | Syntetos-Boylan Approximation | Croston, bias-corrected (preferred) |

### Forecast quality

| ID | Concept | Use when |
|---|---|---|
| [CPT-0008](forecast-accuracy-metrics.md) | MAE · MAPE · RMSE | Standard accuracy reporting |
| [CPT-0009](scale-free-accuracy-metrics.md) | WMAPE · sMAPE · Theil's U | Intermittent or cross-SKU comparison |
| [CPT-0010](tracking-signal-and-bias.md) | Tracking Signal · Forecast Bias | Detecting systematic drift |

### Inventory policy parameters

| ID | Concept | Use when |
|---|---|---|
| [CPT-0003](service-level-z-score.md) | Service-level Z-score | Converting a target service level to a multiplier |
| [CPT-0012](safety-stock-days-of-supply.md) | Safety stock — days of supply | Quick rule of thumb |
| [CPT-0013](safety-stock-average-max.md) | Safety stock — Average-Max | No reliable standard deviations available |
| [CPT-0014](safety-stock-statistical.md) | Safety stock — statistical | Demand varies, lead time is stable |
| [CPT-0015](safety-stock-combined.md) | Safety stock — combined variability | Demand **and** lead time vary (most accurate) |
| [CPT-0016](reorder-point.md) | Reorder Point | Triggering replenishment |
| [CPT-0017](economic-order-quantity.md) | Economic Order Quantity | Sizing the replenishment |

### Classification and inventory performance

| ID | Concept | Use when |
|---|---|---|
| [CPT-0018](coefficient-of-variation-xyz.md) | Coefficient of Variation · XYZ | Segmenting by demand predictability |
| [CPT-0019](inventory-turnover-ratio.md) | Inventory Turnover Ratio | Measuring inventory efficiency |
| [CPT-0020](days-inventory-outstanding.md) | Days Inventory Outstanding | Expressing turnover in days |

### Measures of the planning process itself

> These judge the planning function rather than the demand: whether forecasting adds value over a
> naive baseline, and whether the buffer a project holds matches the buffer its own method calls
> for. Both are commonly skipped, which is why they are catalogued.

| ID | Concept | Use when |
|---|---|---|
| [CPT-0024](forecast-value-added.md) | Forecast Value Added | Asking whether the forecasting effort beats a naive baseline at all |
| [CPT-0025](safety-stock-coverage.md) | Safety-stock coverage & adequacy | Comparing the buffer actually held against the buffer the method requires |

### Machine-learning demand sensing

| ID | Concept | Use when |
|---|---|---|
| [CPT-0021](demand-sensing-ensemble.md) | Demand sensing ensemble | Short-horizon signals, exogenous drivers |
| [CPT-0022](demand-anomaly-detection.md) | Demand anomaly detection | Cleansing history before fitting |
| [CPT-0023](probabilistic-deep-forecasting.md) | Probabilistic deep forecasting | Quantiles / service-level-aware forecasts |
