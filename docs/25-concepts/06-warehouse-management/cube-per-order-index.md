---
id: concept-cube-per-order-index
title: "Cube-per-Order Index (CPT-0037)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-06-warehouse-management }
  - { type: governed-by, target: index-adr }
---
# Cube-per-Order Index (CPT-0037)

> CPOI ranks SKUs for slotting: how much storage cube a SKU consumes per pick it earns.
> Low CPOI (small, frequently picked) deserves the golden zone nearest dispatch.

## Formula

    CPOI = volume / pick_frequency

| Symbol | Meaning | Unit |
|---|---|---|
| volume | storage volume of one unit | any volume unit, **used consistently** |
| pick_frequency | picks in the measurement period | picks per period |

## Inputs and outputs

- **Inputs:** per-SKU volume `> 0`, pick frequency `≥ 0`.
- **Output:** CPOI, dimensionless ratio (volume-units per order). `pick_frequency = 0` →
  unbounded — a SKU occupying space with no picks at all is the signal, flagged as "consider
  discontinuation" rather than slotted.

## Assumptions and limits

- Assumes travel time dominates picking cost, so the scarce resource is *cube near the
  door*; items that spend little cube per order repay forward locations fastest.
- Volume is per **unit**; if picks draw variable quantities, use cube movement per order
  line instead.
- **Does not apply when:** picks are automated (goods-to-person) — travel is no longer
  the driver; or when weight/ergonomics constraints dominate slot choice.

## Worked example

SKU volume 500 cm³, 250 orders/month → `CPOI = 500 / 250 = 2.0`.
A 10,000 cm³ SKU with 10 orders/month → `CPOI = 1000` — the first SKU outranks it for
the golden zone by 500×.

## Governing rules

- Slotting is advisory: no invariant constrains CPOI itself; placement decisions must
  still respect the project's own task lifecycle when executed as re-slotting moves.

## Related

- CPT-0038 ABC velocity slotting — consumes CPOI/pick-frequency ranking.
- CPT-0039 S-shape travel distance — the cost model slotting tries to minimize.

## References

- Heskett, J.L. (1963), "Cube-per-order index — a key to warehouse stock location",
  *Transportation and Distribution Management* 3 — the original formulation.
- Frazelle (2002), Ch. 5 — modern slotting practice.
