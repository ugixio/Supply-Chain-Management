---
id: concept-turnover-and-dio
title: "Inventory Turnover & DIO — Inventory View (CPT-0116)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-05-inventory-management }
  - { type: governed-by, target: index-adr }
  - { type: traces-to, target: concept-inventory-turnover-ratio }
---
# Inventory Turnover & DIO — Inventory View (CPT-0116)

> The department-05 copies of the turnover pair. Semantics are owned by the
> demand-planning catalogue (CPT-0017 turnover, CPT-0016 DIO); this node marks the
> local implementations so G10 stays exact.

## Formula

    ITR = COGS / avg_inventory_value        (zero inventory → 0.0)
    DIO = 365 / ITR                          (zero ITR → ∞)

## Inputs and outputs

- Floats; ITR rounded 4 dp, DIO 2 dp. Benchmarks echoed: FMCG 8–12×; DIO < 45 days.

## Assumptions and limits

- See CPT-0016/CPT-0017 — all semantics carry over.
- **Duplication (recorded):** turnover/DIO now exist in depts 03, 05 and (balance-
  sheet form) 11 — three homes for one fact pair; dedup is a U8/U11b-class item.
- The zero-inventory → 0.0 convention here differs from raising; a 0 ITR then maps
  to DIO = ∞ — dashboards must handle the infinity.

## Worked example

COGS 25.1M / avg inventory 4.0M → ITR 6.275 → DIO 58.2 days (same numbers as the
CPT-0105 worked example, by construction).

## Implementations

- PY: [`inventory_turnover_ratio`](../../../services/calc/05_inventory_management/stock_balance.py)
- PY: [`days_inventory_outstanding`](../../../services/calc/05_inventory_management/stock_balance.py)

## Governing rules

- SSOT: semantics at CPT-0016/0017; referenced, not restated.

## Related

- CPT-0105 DIO/DSO/DPO — the finance balance-sheet form.

## References

- Cited at CPT-0016/CPT-0017.
