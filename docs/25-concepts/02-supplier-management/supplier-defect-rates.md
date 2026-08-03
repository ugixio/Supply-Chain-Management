---
id: concept-supplier-defect-rates
title: "Supplier Defect Rates — PPM/DPMO on Received Material (CPT-0063)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-08-03
relations:
  - { type: part-of, target: index-concepts-02-supplier-management }
  - { type: governed-by, target: index-adr }
  - { type: traces-to, target: concept-ppm-defect-rate }
  - { type: traces-to, target: concept-dpmo-sigma-level }
---
# Supplier Defect Rates — PPM/DPMO on Received Material (CPT-0063)

> **The arithmetic is CPT-0051 (PPM) and CPT-0052 (DPMO), not restated here.** This node fixes the
> **population**: rates over material *received from a supplier*, not *produced internally*. Same
> formula, different denominator — and that is what makes the number say something about a supplier
> rather than about a process.

## Formula

As CPT-0051 and CPT-0052. This node changes no term of either.

## Inputs and outputs

The counts come from the **incoming inspection record**, not from production:

| Symbol | Meaning at this measurement point |
|---|---|
| defective units | Units rejected at receipt, by the disposition recorded for the lot |
| total units | Units **received and inspected** — not units ordered, not units later consumed |
| defects | Non-conformities found at receipt; one unit may carry several |
| opportunities per unit | Fixed by the inspection specification for the received item |

## Assumptions and limits

- **The denominator must be the inspected quantity.** Where inspection is by sample rather than
  100% (CPT-0050, ISO 2859-1), the rate describes the **sample**, and extends to the lot only under
  that plan's assumptions. Counting defects found in a sample while dividing by the received
  quantity overstates quality, and does so silently.
- **Attribution requires the defect to be the supplier's.** Transit damage under an Incoterms® 2020
  rule where risk had already passed to the buyer is a received defect but not a supplier defect.
  The eleven rules fix where risk passes; the contract fixes which rule applies.
- **A rate over too few units is arithmetic, not measurement.** PPM is a rate per million; two
  hundred received units cannot yield a meaningful one. Sufficient exposure is a project's decision.
- All assumptions of CPT-0051 and CPT-0052 carry over unchanged.

## Project-chosen inputs

| Decision | Why the context cannot fix it |
|---|---|
| Which dispositions count as defective — reject, return, rework, use-as-is under concession | Each is a legitimate treatment of a non-conforming lot; whether a concession counts as a defect is quality policy. |
| The minimum received quantity below which a rate is not reported | A statistical-confidence choice, not a standard. |
| Whether transit damage is attributed to the supplier | Follows the project's Incoterms position and its supply agreement. |
| The window over which receipts are aggregated | A management-cadence choice. MSR-R1 fixes only that the ratio aggregates from its components. |

## Worked example

The arithmetic is at CPT-0051 and CPT-0052. The example that belongs *here* is the trap: a lot of
10,000 units is inspected to a sample of 200, and 2 defectives are found. The rate the sample
supports is 2 / 200 × 10⁶ = **10,000 PPM**. Reporting 2 / 10,000 × 10⁶ = 200 PPM — dividing by the
received quantity instead of the inspected quantity — understates it fiftyfold.

## Governing rules

- **MSR-R1** — the rate aggregates from its components across receipts, never as a mean of rates.
- **SUP-R5** — an evaluation of an external provider records what was assessed and on what basis;
  the measurement point above is part of that basis.
- Feeds the quality dimension of **CPT-0060** (supplier scorecard weighted composite).

## Related

- CPT-0051 · CPT-0052 (semantics) · CPT-0050 (sampling) · CPT-0060 (consumer).

## References

- Formula and units: cited at CPT-0051 and CPT-0052 (SSOT — not restated).
- ISO 2859-1:1999 — sampling procedures by attributes; the plan fixes what a sample supports.
- ICC Incoterms® 2020 — the eleven rules and the point at which risk passes.
- APICS Dictionary 16th Ed. (ASCM, 2024) — *defect*, *non-conformity*.
