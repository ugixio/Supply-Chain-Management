---
id: concept-cumulative-atp
title: "Cumulative Available-to-Promise (CPT-0085)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-13-order-management }
  - { type: governed-by, target: index-adr }
---
# Cumulative Available-to-Promise (CPT-0085)

> What can still be promised in each period, counting all future supply against all
> future firm commitments — the order-entry availability check.

## Formula

    balance_0 = on_hand · balance_t = balance_{t−1} + supply_{t−1} − demand_{t−1}
    ATP_t = balance_t + Σ_{k≥t} supply_k − Σ_{k≥t} demand_k

| Symbol | Meaning | Unit |
|---|---|---|
| on_hand | opening stock | units |
| supply_k | scheduled receipts per period | units |
| demand_k | firm (committed) orders per period | units |

## Inputs and outputs

- **Inputs:** equal-length supply and committed-demand schedules (raises otherwise);
  opening on-hand.
- **Output:** ATP per period (list of floats). Negative ATP_t = that period is
  over-committed; no promise without a supply action.

## Assumptions and limits

- **Firm commitments only** in the demand leg — forecasts do not consume ATP (that is
  the planning distinction between ATP and projected available balance).
- The "look-ahead to horizon" form means late-horizon supply can mask an early-period
  shortage in ATP_0 while intermediate periods still go negative — read the whole
  vector, not one bucket; the *discrete* form (CPT-0086) avoids borrow-ahead by
  construction.
- No lot sizing, no yields, no substitution.
- **Does not apply when:** promising against capacity rather than inventory — that is
  CTP (CPT-0087).

## Worked example

on_hand 100; supply [0, 150, 0]; committed [80, 60, 40].
Balances: [100, 20, 110]. ATP: [100+150−180, 20+150−100, 110+0−40] = **[70, 70, 70]** —
70 units promisable in any bucket.

## Implementations

- PY: [`cumulative_atp`](../../../services/calc/13_order_management/order_metrics.py)

## Governing rules

- **SCM-R1** — a promise that would drive projected stock negative needs backorder
  authority; ORD lifecycle consumes the result at order entry.

## Related

- CPT-0086 Discrete ATP — the per-supply-bucket variant.
- CPT-0087 CTP — the production-fallback extension.

## References

- APICS CPIM — master scheduling/ATP; Vollmann, Berry & Whybark, *Manufacturing
  Planning and Control*.
