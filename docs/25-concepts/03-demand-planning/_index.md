---
id: index-concepts-demand-planning
title: "Concepts — Demand Planning (03)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-concepts }
  - { type: governed-by, target: index-adr }
  - { type: traces-to, target: rule-demand-planning }
---
# Concepts — Demand Planning (03)

> The calculation catalogue for `src/departments/03-demand-planning/` and
> `python/03_demand_planning/`. This is the **exemplar** department for ADR-0015:
> coverage is `enforced`, so every public calculation symbol below has a node.
> Law lives in [40-contexts/03-demand-planning/rule.md](../../40-contexts/03-demand-planning/rule.md)
> (`DMD-R*`); these nodes carry meaning and mathematics only.

## What counts as a public calculation symbol

G10 reads **top-level `export function`** in TypeScript and **module-level `def`** in
Python (leading-underscore names excluded). This is a deliberate convention, not an
accident of the regex: domain aggregates in this repo publish their lifecycle through a
namespace object (`export const DemandPlan = { create, approve, … }`), so state
transitions stay out of the catalogue while the algorithm modules — `Forecasting.ts`,
`SafetyStock.ts` — are fully in it. Lifecycle transitions are governed by `rule.md`, not
by a concept node.

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

### Specified but NOT implemented (ADR-0016 extraction)

> Extracted from `IMPLEMENTATION.md`; no code computes these. Invisible to G10 — see
> [_index](../_index.md) "What G10 cannot see". Implementing them is backlog U18.

| ID | Concept | Gap |
|---|---|---|
| [CPT-0024](forecast-value-added.md) | Forecast Value Added | Required KPI with an S&OP escalation path; nothing computes it |
| [CPT-0025](safety-stock-coverage.md) | Safety-stock coverage & adequacy | Targets are computed, but never compared against stock actually held |

### Machine-learning demand sensing

| ID | Concept | Use when |
|---|---|---|
| [CPT-0021](demand-sensing-ensemble.md) | Demand sensing ensemble | Short-horizon signals, exogenous drivers |
| [CPT-0022](demand-anomaly-detection.md) | Demand anomaly detection | Cleansing history before fitting |
| [CPT-0023](probabilistic-deep-forecasting.md) | Probabilistic deep forecasting | Quantiles / service-level-aware forecasts |
