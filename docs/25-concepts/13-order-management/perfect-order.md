---
id: concept-perfect-order
title: "Perfect Order & Perfect Order Rate (CPT-0083)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-13-order-management }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: concept-otif-components-and-rate }
---
# Perfect Order & Perfect Order Rate (CPT-0083)

> The flawless-execution test: OTIF *and* damage-free *and* invoice-accurate — and the
> share of orders that pass. World-class ≥ 95%.

## Formula

    perfect(order) ⇔ OTIF(order) ∧ damage_free ∧ invoice_accurate
    POR% = |perfect orders| / |orders| × 100

TS (`calculatePerfectOrderRate`) evaluates over **delivered/closed** orders only,
reading the `isPerfectOrder` flag stamped by `markDelivered`.

| Symbol | Meaning | Unit |
|---|---|---|
| damage_free | no damage/quality claim on receipt | boolean |
| invoice_accurate | billing matched the order | boolean |

## Inputs and outputs

- **PY:** order objects with the two flags; empty list raises.
- **TS:** filters to DELIVERED/CLOSED; empty basis returns 0 (divergence: PY raises,
  TS returns 0).

## Assumptions and limits

- This is the **intersection (AND) model** on actual orders — each order individually
  flawless. Contrast the *multiplicative index* (CPT-0084) which estimates the rate
  from factor rates assuming independence; on the same data the two differ whenever
  failures correlate (they usually do — a chaotic week fails several factors at once,
  making AND-counted POR *higher* than the multiplied index).
- Documentation accuracy is folded into `invoice_accurate` here; SCOR's four-factor
  version tracks docs separately (CPT-0084).
- **Does not apply when:** orders are open — TS correctly excludes them; PY expects
  the caller to pass a closed population.

## Worked example

100 orders: 92 OTIF, of which 90 damage-free and 89 also invoice-accurate →
POR = 89%. Factor rates (92%, ~96%, ~97%) multiplied would predict ≈ 85.7% — the
gap is failure correlation.

## Implementations

- PY: [`is_perfect_order`](../../../services/calc/13_order_management/order_metrics.py)
- PY: [`perfect_order_rate`](../../../services/calc/13_order_management/order_metrics.py)
- TS: [`calculatePerfectOrderRate`](../../../packages/domain/src/13-order-management/domain/SalesOrder.ts)

## Governing rules

- **ORD-R*** — `markDelivered` stamps the component flags; ADR-0029 places
  perfect-order metrics in dept 13.

## Related

- CPT-0084 Perfect Order Index — the SCOR multiplicative estimator.
- CPT-0082 OTIF — the delivery core.

## References

- Hausman (2004); APICS CPIM; SCOR-DS RL.1.1 (perfect order fulfillment).
