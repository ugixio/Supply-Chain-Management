---
id: concept-returns-economics
title: "Returns Economics — Rate, Refund, Reverse Cost (CPT-0091)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-13-order-management }
  - { type: governed-by, target: index-adr }
---
# Returns Economics — Rate, Refund, Reverse Cost (CPT-0091)

> The SCOR Return-process arithmetic: how often orders come back, what to credit the
> customer (restocking-fee aware), and what the return event truly costs.

## Formula

    return_rate% = returns / total_orders × 100
    refund_line  = round(qty × unit_price × (1 − fee%/100))
      fee% = 0 for fault-based reasons (DEFECTIVE, DAMAGED_IN_TRANSIT, WRONG_ITEM,
             QUALITY_ISSUE, NEAR_EXPIRY); else per-line override or default 15%
    reverse_cost = shipment + inspection + disposition + refund
    as_pct_of_refund = reverse_cost / refund × 100

| Symbol | Meaning | Unit |
|---|---|---|
| unit_price / costs / refund | money | integer cents |
| fee% | restocking fee | percent |

## Inputs and outputs

- **Inputs:** integer-cent money (validated non-negative integers); quantities ≥ 0.
- **Outputs:** rate %; `{by_line, total_refund_cents, restocking_fees_cents}`;
  `{total_cents, as_pct_of_refund}` (0 when refund = 0).

## Assumptions and limits

- **Fault-based returns always refund in full** — the fee override is ignored for the
  five fault reasons, mirroring EU Consumer Rights Directive 2011/83/EU obligations;
  the 15% default applies to change-of-mind/excess only (and jurisdictions differ —
  parametrize per market).
- `as_pct_of_refund > 100%` = the return costs more than the credit — the flag for
  "refund without return" policies on low-value items.
- Return rate counts RMAs against orders shipped in the same period — mismatched
  lags distort short windows (returns arrive weeks after shipping).
- Recovery value (restock/resale/refurb proceeds) is not netted — the cost is gross.
- **Does not apply when:** partial-quantity acceptance per line differs from the RMA —
  pass accepted quantities, not requested.

## Worked example

Return: 2 × 4,500¢, reason CUSTOMER_CHANGED_MIND, default fee →
refund = round(9,000 × 0.85) = 7,650¢; fees withheld 1,350¢.
Reverse cost: 800 + 300 + 250 + 7,650 = 9,000¢ → 117.6% of the refund — this return
destroyed more value than it credited.

## Implementations

- PY: [`return_rate`](../../../services/calc/13_order_management/order_metrics.py)
- PY: [`refund_amount`](../../../services/calc/13_order_management/order_metrics.py)
- PY: [`reverse_logistics_cost`](../../../services/calc/13_order_management/order_metrics.py)

## Governing rules

- **SCM-R8** — integer-cent money (Decimal at P5); **SCM-R3** — return records
  soft-delete; SCM-R4 — credit notes hit the GL.

## Related

- CPT-0083 Perfect order — damage-driven returns feed both.
- Inventory RETURN_FROM_CUSTOMER movement (dept 05) — the physical leg.

## References

- SCOR-DS Return (SR) process; EU Directive 2011/83/EU; Chopra & Meindl, Ch. 13.
