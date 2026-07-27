---
id: concept-abc-xyz-matrix
title: "ABC-XYZ 9-Box Matrix (CPT-0115)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-05-inventory-management }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: concept-abc-classification }
---
# ABC-XYZ 9-Box Matrix (CPT-0115)

> Crosses value (ABC) with demand variability (XYZ) into nine control segments:
> AX (high value, stable → automate tightly) through CZ (low value, erratic →
> simple rules or make-to-order).

## Formula

    CV = σ(demand) / μ(demand)
    X: CV < 0.10 · Y: 0.10 ≤ CV < 0.25 · Z: CV ≥ 0.25   (zero mean → Z)
    label = ABC(ACV) + XYZ(CV)         (e.g. 'AX', 'BZ')

| Symbol | Meaning | Unit |
|---|---|---|
| CV | coefficient of variation of the demand history | dimensionless |

## Inputs and outputs

- **Inputs:** `SKUMetrics` records (ACV + demand history).
- **Output:** `{sku_id: 'AX'…'CZ'}`. TS `updateABCXYZ` writes the result to the item
  master (a governed setter, excluded from the catalogue).

## Assumptions and limits

- CV here uses **population σ** (NumPy default `ddof=0`) — the same estimator caveat
  recorded at CPT-0018 (U15b #6): short histories move SKUs across X/Y/Z with ddof
  choice.
- CV thresholds mirror the repo's XYZ convention (CLAUDE.md; CPT-0018 is the
  authoritative CV semantics — this node owns the *9-box combination*, not the CV).
- CV is meaningless for intermittent demand (many zeros → huge CV, all Z);
  Croston-family classification (CPT-0006) is the right lens there.
- Policy mapping is the point: AX → tight (r,Q)/(s,S) automation (CPT-0120), CZ →
  manual/MTO; the matrix without a policy map is decoration.
- **Does not apply when:** demand history is shorter than a season — classify
  provisionally.

## Worked example

SKU: ACV ranks A; history μ = 100, σ = 8 → CV 0.08 → X → **AX**: automate
replenishment, cycle-count frequently, safety stock from CPT-0012.

## Governing rules

- **INV-R*** — item-master classification changes flow through `updateABCXYZ`
  (an identifier's stability is a data-modelling decision; the classification is a field).

## Related

- CPT-0114 ABC · CPT-0018 CV/XYZ semantics · CPT-0120 policies per segment.

## References

- Silver, Pyke & Peterson §3; Errasti — ABC/XYZ practice; CLAUDE.md XYZ bands.
