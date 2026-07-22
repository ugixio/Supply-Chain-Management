---
id: concept-supplier-defect-rates
title: "Supplier Defect Rates — PPM/DPMO Inputs (CPT-0063)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-02-supplier-management }
  - { type: governed-by, target: index-adr }
  - { type: traces-to, target: concept-ppm-defect-rate }
  - { type: traces-to, target: concept-dpmo-sigma-level }
---
# Supplier Defect Rates — PPM/DPMO Inputs (CPT-0063)

> The scorecard's local copies of PPM and DPMO. The semantics are owned by
> CPT-0051 (PPM) and CPT-0052 (DPMO) in quality management — this node exists because
> the supplier-management module ships its own implementations of the same formulas.

## Formula

Identical to CPT-0051/CPT-0052:

    PPM  = defective_units / total_units × 10⁶
    DPMO = defects / (units × opportunities_per_unit) × 10⁶

## Inputs and outputs

- Counts ≥ 0; zero denominator → 0.0. **Unlike the dept-08 versions, these return raw
  floats (no 4-dp rounding).**

## Assumptions and limits

- See CPT-0051/CPT-0052 — all assumptions carry over.
- **Duplication (recorded):** `calculate_ppm`/`calculate_dpmo` exist in both
  `02_supplier_management/scorecard.py` and `08_quality_management/quality.py` with a
  rounding difference. One should import the other (U8/U11b-class dedup candidate);
  until then this node marks the copy so G10 stays exact.

## Worked example

See CPT-0051/CPT-0052 — same arithmetic.

## Implementations

- PY: [`calculate_ppm`](../../../services/calc/02_supplier_management/scorecard.py)
- PY: [`calculate_dpmo`](../../../services/calc/02_supplier_management/scorecard.py)

## Governing rules

- Same as CPT-0051/0052; feeds the quality dimension of CPT-0060.

## Related

- CPT-0051 PPM · CPT-0052 DPMO — the authoritative semantics.

## References

- Cited at CPT-0051/CPT-0052 (SSOT — references not restated).
