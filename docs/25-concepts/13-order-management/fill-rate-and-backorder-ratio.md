---
id: concept-fill-rate-and-backorder-ratio
title: "Fill Rate & Backorder Ratio (CPT-0088)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-13-order-management }
  - { type: governed-by, target: index-adr }
---
# Fill Rate & Backorder Ratio (CPT-0088)

> The quantity-service pair: what fraction of demanded units shipped from stock, and
> what fraction of order lines could not be served.

## Formula

    fill_rate% = units_shipped / units_ordered × 100
    backorder% = backorder_lines / total_lines × 100

| Symbol | Meaning | Unit |
|---|---|---|
| units_shipped/ordered | quantities in the period | units |
| backorder_lines / total_lines | lines unservable / all lines | count |

## Inputs and outputs

- **Inputs:** positive denominators (raise otherwise); non-negative numerators.
- **Outputs:** percentages. What fill rate is acceptable follows from the service commitment
  the project has made — it is not a property of the metric.

## Assumptions and limits

- Fill rate here is **unit-based**; the two metrics are complements only at the same
  granularity (unit fill vs *line* backorder here — a line missing 1 of 100 units hits
  unit fill by 1% but line backorder by a whole line).
- Fill rate is the demand-weighted service level (Type-2 / β service) — the quantity
  that safety-stock β-optimization targets; do not conflate with cycle service level
  (Type-1 α, CPT-0003 z-scores).
- Measure against original ordered quantities — order-line rewrites to match stock
  ("demand shaping") launder the metric.
- **Does not apply when:** substitution is allowed and counted as filled — define the
  substitution policy first.

## Worked example

Ordered 12,400 units, shipped 12,090 → fill 97.5%. Of 3,100 lines, 87 backordered →
2.81%.

## Project-chosen inputs

| Input | Why the project must choose it |
|---|---|
| The fill-rate target | A service commitment, weighed against the inventory it takes to hold |
| Line, unit or order fill | The same shipments give three different rates; an order-fill figure is always the harshest |
| Whether a late-but-complete delivery counts as filled | Fill and timeliness are separable, and conflating them hides which one failed |

## Governing rules

- **INV-R5** — a physical balance cannot be negative; whether unmet demand becomes a backorder is the project's fulfilment policy
  are lost sales (measure separately).

## Related

- CPT-0082 OTIF — the order-level composite.
- Safety stock (CPT-0012 family) — the lever that moves fill rate.

## References

- Chopra & Meindl, Ch. 13; Silver, Pyke & Peterson — service measures.
