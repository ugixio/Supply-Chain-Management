---
id: concept-fifo-valuation
title: "FIFO Valuation — Cost Layers (CPT-0118)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-05-inventory-management }
  - { type: governed-by, target: index-adr }
---
# FIFO Valuation — Cost Layers (CPT-0118)

> Issues consume the oldest cost layers first: the COGS of an issue is the sum of the
> draws it makes from layers in receipt order (IAS 2 §27 FIFO cost formula).

## Formula

    order layers by (receipt_date ↑, input order)
    for each layer: take = min(remaining_issue, layer.remaining_qty)
                    COGS += round(take × unit_cost_cents)
    fully consumed layers drop from the remaining set

| Symbol | Meaning | Unit |
|---|---|---|
| layer | {layer_id, receipt_date, remaining_qty, unit_cost_cents} | mixed |
| issue_qty | quantity to issue (> 0, ≤ total remaining) | units |

## Inputs and outputs

- **Inputs:** cost layers; positive issue quantity — **raises if the issue exceeds
  total remaining** (SCM-R1: no negative inventory).
- **Output:** `{cogs_cents, remaining_layers, layers_consumed}` — the consumed-draws
  list is the journal detail (SCM-R4).
- TS `valuationSnapshot` reports the aggregate's point-in-time summary (method,
  total qty/value, average unit cost, layer count).

## Assumptions and limits

- Rounding happens **per draw** (`round(take × unit_cost)`) — across many fractional
  draws this can drift a cent vs rounding the total; the reconciliation property
  belongs to U8 golden vectors.
- FIFO cost flow need not match physical flow (FEFO picking, CPT-0036, can ship a
  newer lot while FIFO costs the oldest layer) — accounting and logistics are
  deliberately decoupled.
- Layers must carry accurate receipt dates; missing dates sort as empty strings
  (first) — a data-quality hazard worth guarding upstream.
- **Does not apply when:** the item's valuation method is WAC (CPT-0119) or standard
  cost; IFRS prohibits LIFO entirely (IAS 2 §25 allows only FIFO/WAC/specific-id).

## Worked example

Layers: 60 @ 1,000¢ (Jan), 80 @ 1,100¢ (Feb). Issue 90 →
60×1,000 + 30×1,100 = **93,000¢ COGS**; remaining: 50 @ 1,100¢.

## Implementations

- PY: [`fifo_valuation`](../../../services/calc/05_inventory_management/stock_balance.py)
- TS: [`valuationSnapshot`](../../../packages/domain/src/05-inventory-management/domain/InventoryValuation.ts)

## Governing rules

- **SCM-R1** — no over-issue; **SCM-R4** — COGS journals; **SCM-R8** — integer cents;
  **SCM-R3** — valuation records soft-delete.

## Related

- CPT-0119 WAC — the alternative cost formula.
- CPT-0111 Landed cost — sets the layer unit cost on receipt.

## References

- IAS 2 §§25–27 — cost formulas.
