---
id: concept-inventory-target
title: "Inventory Target Level (CPT-0149)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-12-sop-planning }
  - { type: governed-by, target: index-adr }
---
# Inventory Target Level (CPT-0149)

> The average inventory an S&OP plan should carry under a continuous-review
> policy: safety stock plus half the order quantity (cycle stock).

## Formula

    target = safety_stock + EOQ / 2

| Symbol | Meaning | Unit |
|---|---|---|
| safety_stock | buffer for the service level (CPT-0012 family) | units |
| EOQ / 2 | average cycle stock | units |

## Inputs and outputs

- **Inputs:** SS ≥ 0, EOQ > 0 (validated).
- **Output:** target average units — the S&OP inventory-plan line and the
  denominator sanity-check for DIO projections.

## Assumptions and limits

- The Q/2 term assumes steady consumption between receipts (the sawtooth
  average) — lumpy demand or (s,S) with variable order sizes shifts the true
  average.
- Pipeline (in-transit) stock is *not* included — add μ·LT separately when the
  plan owns in-transit inventory (Incoterms decide ownership, CPT-0111 note).
- Anticipation stock (pre-builds for seasonality/shutdowns) is an S&OP *decision*
  on top of this floor, not part of the formula.
- Consistency discipline: the SS and EOQ inputs must be the ones the execution
  policies actually use (CPT-0120) or plan and execution diverge silently.
- **Does not apply when:** make-to-order items (no cycle stock by design).

## Worked example

SS 93, EOQ 721 (the CPT-0120 example) → `target = 93 + 360.5 = 453.5 units` —
at 200/week demand ≈ 2.3 weeks of supply; multiply by unit cost for the
working-capital plan (CPT-0104).

## Governing rules

- **SOP-R4** — the inventory target belongs to the same single plan as the demand and supply
  numbers. The target **level** is a project decision (service commitments, cost of capital).

## Related

- CPT-0012 safety stock · CPT-0021 EOQ · CPT-0120 (r,Q) — the inputs' homes.

## References

- Silver, Pyke & Peterson (1998), Ch. 5; Wallace (2004) — S&OP inventory plans.
