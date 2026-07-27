---
id: index-concepts-13-order-management
title: "Concepts — Order Management (13)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-27
relations:
  - { type: part-of, target: index-concepts }
  - { type: governed-by, target: index-adr }
  - { type: traces-to, target: rule-order-management }
---
# Concepts — Order Management (13)

> The concept catalogue for **Order Management (13)**: what each concept *means*,
> the formula where one is canonical, its assumptions and limits, and the standard or
> regulation that fixes it. Nodes **define**; they hold no threshold, target, weighting or
> mandated method, and they own no code (ADR-0037). Values a project must choose are named
> as project-chosen inputs and left unset.
>
> Departmental law lives in [40-contexts/13-order-management/rule.md](../../40-contexts/13-order-management/rule.md).

## Catalogue

### Service metrics

| ID | Concept | Use when |
|---|---|---|
| [CPT-0082](otif-components-and-rate.md) | OTIF components & rate | Delivery-promise compliance |
| [CPT-0083](perfect-order.md) | Perfect order & rate | Flawless-execution counting |
| [CPT-0084](perfect-order-index.md) | Perfect Order Index + gap | Factor attribution (SCOR) |
| [CPT-0088](fill-rate-and-backorder-ratio.md) | Fill rate & backorder ratio | Quantity service levels |
| [CPT-0089](order-cycle-time-summary.md) | Order cycle time summary | Delivery-speed analysis |

### Order promising & allocation

| ID | Concept | Use when |
|---|---|---|
| [CPT-0085](cumulative-atp.md) | Cumulative ATP | Availability at order entry |
| [CPT-0086](discrete-atp.md) | Discrete ATP | MPS ATP row per supply bucket |
| [CPT-0087](capable-to-promise.md) | Capable-to-Promise | Stock-else-production promising |
| [CPT-0090](fair-share-allocation.md) | Fair-share allocation | Rationing scarce stock |

### Returns & agility

| ID | Concept | Use when |
|---|---|---|
| [CPT-0091](returns-economics.md) | Returns economics | RMA rates, refunds, reverse cost |
| [CPT-0092](scor-agility-metrics.md) | SCOR agility (AG.1.x) | Flex up/down and VaR |
