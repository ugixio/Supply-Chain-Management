---
id: index-concepts-13-order-management
title: "Concepts — Order Management (13)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts }
  - { type: governed-by, target: index-adr }
  - { type: traces-to, target: rule-order-management }
---
# Concepts — Order Management (13)

> The calculation catalogue for `packages/domain/src/13-order-management/` and
> `services/calc/13_order_management/`. Coverage is `enforced`. Law lives in
> [40-contexts/13-order-management/rule.md](../../40-contexts/13-order-management/rule.md)
> (`ORD-R*`); these nodes carry meaning and mathematics only.

## What counts as a public calculation symbol

`createSalesOrder`/`markDelivered` are lifecycle transitions (the latter stamps the
perfect-order component flags) and `canShip` is a credit-status domain query — all
excluded. The promising (ATP/CTP), service metrics (OTIF, perfect order, fill),
allocation, returns and SCOR agility mathematics are catalogued. ADR-0029 dissolved
the misplaced `07_order_management` dir into this namespace.

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

## Not concepts (excluded from G10)

> Lifecycle transitions and domain queries — governed by `rule.md` (ORD-R*), not
> calculations. Listed so G10 coverage is exact.

`createSalesOrder` · `markDelivered` · `canShip`

## Divergences surfaced (for the backlog)

- ✅ **RESOLVED 2026-07-22 (U8) — refund rounding (CPT-0091).** TS did one `Math.round`
  (float, half-up); PY did two `round()` steps. Canonical = **two-step quantization with
  ROUND_HALF_EVEN** (the gross line extension is document-visible, so it quantizes first;
  the fee applies to that stated gross). Both sides converged and pinned by the golden
  vectors in `tests/golden/money.golden.json`.
- **Empty-population semantics** — `perfect_order_rate` (PY) raises on empty input;
  TS `calculatePerfectOrderRate` returns 0. Align (U8).
- **Two on-time bases** — CPT-0082 measures promise compliance (confirmed-else-
  requested); CPT-0089 measures against requested date only. Both are legitimate;
  reporting must label which.
- **CTP checks lead time, not capacity** (CPT-0087) — a schedule-feasible promise may
  still be capacity-infeasible; wire to RCCP (dept 12) when the app layer lands.
- **AG agility functions** remain here pending the U11 fine split to dept 10
  (ADR-0029 note).
