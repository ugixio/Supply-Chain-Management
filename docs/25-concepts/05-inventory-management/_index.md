---
id: index-concepts-05-inventory-management
title: "Concepts — Inventory Management (05)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-27
relations:
  - { type: part-of, target: index-concepts }
  - { type: governed-by, target: index-adr }
  - { type: traces-to, target: rule-inventory-management }
---
# Concepts — Inventory Management (05)

> The concept catalogue for **Inventory Management (05)**: what each concept *means*,
> the formula where one is canonical, its assumptions and limits, and the standard or
> regulation that fixes it. Nodes **define**; they hold no threshold, target, weighting or
> mandated method, and they own no code (ADR-0037). Values a project must choose are named
> as project-chosen inputs and left unset.
>
> Departmental law lives in [40-contexts/05-inventory-management/rule.md](../../40-contexts/05-inventory-management/rule.md).

## Catalogue

### Event sourcing & classification

| ID | Concept | Use when |
|---|---|---|
| [CPT-0113](stock-balance-projection.md) | Stock balance projection | Deriving balance from the event log |
| [CPT-0114](abc-classification.md) | ABC classification | Value-ranking SKUs |
| [CPT-0115](abc-xyz-matrix.md) | ABC-XYZ 9-box | Control-policy segmentation |
| [CPT-0116](turnover-and-dio.md) | Turnover & DIO (local copies) | Inventory health KPIs |
| [CPT-0117](inventory-carrying-cost.md) | Carrying cost | Pricing the holding decision |

### Valuation (IAS 2)

| ID | Concept | Use when |
|---|---|---|
| [CPT-0118](fifo-valuation.md) | FIFO cost layers | Cost of goods issued |
| [CPT-0119](weighted-average-cost.md) | Weighted average cost | Blended unit cost |

### Replenishment

| ID | Concept | Use when |
|---|---|---|
| [CPT-0120](rq-and-ss-policies.md) | (r,Q) & (s,S) policies | Continuous/periodic replenishment |
| [CPT-0121](newsvendor-models.md) | Newsvendor (+ price-setting) | Single-period buys |
| [CPT-0122](rl-replenishment-policy.md) | RL policy (PPO/DQN) | Learned ordering, benchmarked |
