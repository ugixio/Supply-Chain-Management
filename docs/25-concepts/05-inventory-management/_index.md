---
id: index-concepts-05-inventory-management
title: "Concepts — Inventory Management (05)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts }
  - { type: governed-by, target: index-adr }
  - { type: traces-to, target: rule-inventory-management }
---
# Concepts — Inventory Management (05)

> The calculation catalogue for `packages/domain/src/05-inventory-management/` and
> `services/calc/05_inventory_management/`. Coverage is `enforced`. Law lives in
> [40-contexts/05-inventory-management/rule.md](../../40-contexts/05-inventory-management/rule.md)
> (`INV-R*`); these nodes carry meaning and mathematics only.

## What counts as a public calculation symbol

`createStockMovement`, `createInventoryItem`, `discontinueItem` and `updateABCXYZ`
are lifecycle transitions/setters on the event-sourced aggregates (ADR-0005) —
excluded. Projections, classifications, valuation, replenishment policies and the RL
agent are catalogued.

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

## Not concepts (excluded from G10)

> Lifecycle transitions / governed setters — `rule.md` (INV-R*) territory.

`createStockMovement` · `createInventoryItem` · `discontinueItem` · `updateABCXYZ`

## Divergences surfaced (for the backlog)

- **Negative-stock semantics (CPT-0113)** — PY replay raises on negative balance;
  TS projection reports it. Writer-guard vs reader-projection: document as intended,
  or align (U8).
- **Turnover/DIO triplicated** across depts 03/05/11 (CPT-0116) — dedup candidate.
- **(r,Q) hardcodes 52 periods/year** in EOQ annualization (CPT-0120).
- **FIFO rounds per draw** (CPT-0118) — cent-drift property needs a golden vector.
- **RL PPO env factory** reuses one env instance — vectorization is nominal
  (CPT-0122).
