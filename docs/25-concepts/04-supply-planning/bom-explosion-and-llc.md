---
id: concept-bom-explosion-and-llc
title: "BOM Explosion & Low-Level Coding (CPT-0140)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-04-supply-planning }
  - { type: governed-by, target: index-adr }
---
# BOM Explosion & Low-Level Coding (CPT-0140)

> Turning end-item demand into component demand: walk the bill of materials
> multiplying quantities (with scrap inflation), and assign each part the deepest
> level it appears at so MRP nets it only once, after all its parents.

## Formula

    component_req = parent_req × qty_per × (1 + scrap_pct/100)     (recursive)
    LLC(sku) = max depth at which sku appears anywhere in the tree
               (end items never used as components → 0)

| Symbol | Meaning | Unit |
|---|---|---|
| qty_per | child units per parent unit | units |
| scrap_pct | expected loss allowance | percent |

## Inputs and outputs

- **Inputs:** `bom_tree: {parent: [{component_sku, qty_per, scrap_pct?}]}`;
  a parent quantity for explosion.
- **Outputs:** exploded gross requirements per component (all levels); the LLC map
  `{sku: level}` — process SKUs in ascending LLC order in MRP.

## Assumptions and limits

- Scrap inflates at **every level it is declared** — compounding through deep BOMs
  is correct and easy to double-declare; put scrap on the operation *or* the BOM
  line, never both.
- The LLC rule is exactly why shared components (a screw at levels 1 and 3) must
  wait: netting at level 1 would miss level-3 dependent demand (Orlicky's
  low-level coding).
- No cycle detection — a recursive BOM (A→B→A) recurses forever; guard upstream
  (BOM validation belongs to the aggregate lifecycle).
- Phantom assemblies and by-products are not modelled.
- **Does not apply when:** configurable products (planning BOMs with option
  percentages) — a different explosion.

## Worked example

100 bikes; frame qty 1 (scrap 2%) → 102 frames; each frame: 4 welds of tube
qty 0.5 m (scrap 5%) → 102 × 2 × 1.05 = 214.2 m tube. Tube also used at level 1
elsewhere → LLC(tube) = 2; net it after frames.

## Governing rules

- **SPL-R*** — BOM master data governed on the aggregate (`BillOfMaterials.ts`).

## Related

- CPT-0139 MRP run — consumes exploded requirements in LLC order.

## References

- Orlicky (2022), Ch. 3 & 5; APICS CPIM — product structure.
