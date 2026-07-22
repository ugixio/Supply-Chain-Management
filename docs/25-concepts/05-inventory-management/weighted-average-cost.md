---
id: concept-weighted-average-cost
title: "Weighted Average Cost (CPT-0119)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-05-inventory-management }
  - { type: governed-by, target: index-adr }
---
# Weighted Average Cost (CPT-0119)

> One blended unit cost across all remaining layers — the IAS 2 weighted-average
> alternative to FIFO.

## Formula

    WAC = round( Σ(remaining_qty × unit_cost_cents) / Σ remaining_qty )

| Symbol | Meaning | Unit |
|---|---|---|
| layers | {remaining_qty, unit_cost_cents} | units, integer cents |
| WAC | blended unit cost | integer cents |

## Inputs and outputs

- **Inputs:** the current layer set; zero total quantity → 0.
- **Output:** integer cents (banker's-adjacent single rounding at the end).

## Assumptions and limits

- Computed over the current layers = **moving average** behavior when recomputed
  after every receipt; a *periodic* WAC (recompute at month-end over all receipts)
  gives different COGS — say which regime applies (this implementation is
  layer-state-driven → moving).
- WAC smooths price volatility into margins; FIFO (CPT-0118) shows it sooner. Method
  choice is per item class and sticky (IAS 2 §25–26: same formula for similar
  inventories; changes are accounting-policy changes).
- One rounding at the end (good for SCM-R8); issuing at the rounded WAC then
  re-deriving value can drift a cent per issue — the valuation aggregate should carry
  value, not re-multiply.
- **Does not apply when:** items are specifically identified (serialized high-value —
  IAS 2 §23 specific identification).

## Worked example

Layers: 50 @ 1,000¢ + 150 @ 1,200¢ → WAC = (50,000 + 180,000)/200 = **1,150¢**.

## Implementations

- PY: [`weighted_average_cost`](../../../services/calc/05_inventory_management/stock_balance.py)

## Governing rules

- **SCM-R8** money; **SCM-R4** — revaluation/issue journals.

## Related

- CPT-0118 FIFO — the alternative formula; CPT-0111 landed cost — layer costs.

## References

- IAS 2 §§25–27 — weighted average cost formula.
