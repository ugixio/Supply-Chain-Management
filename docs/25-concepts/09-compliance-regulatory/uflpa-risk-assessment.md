---
id: concept-uflpa-risk-assessment
title: "UFLPA Risk Assessment (CPT-0094)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-09-compliance-regulatory }
  - { type: governed-by, target: index-adr }
---
# UFLPA Risk Assessment (CPT-0094)

> Classifies a supplier's exposure under the US Uyghur Forced Labor Prevention Act's
> rebuttable presumption: goods with Xinjiang (XUAR) nexus are presumed made with
> forced labour and barred from US entry unless clear and convincing evidence rebuts it.

## Formula

    PROHIBITED: on the CBP UFLPA Entity List, OR XUAR operations without a
                clearance document reference
    HIGH:       XUAR ∧ high-priority-sector HS codes ∧ clearance doc (enhanced scrutiny)
    MEDIUM:     XUAR without priority HS
    LOW:        no XUAR nexus detected

| Symbol | Meaning | Unit |
|---|---|---|
| regions_of_operation | matched against {Xinjiang, XUAR, 新疆} | strings |
| hs_codes | matched against high-priority set (cotton 5201/5203, apparel 6109/6205, …) | HS-6 |
| clearance_document_ref | evidence reference (SCM-R6) | id |

## Inputs and outputs

- **Input:** `SupplierUFLPA` record.
- **Output:** the risk level, and the ladder step that produced it. A level with no stated basis
  cannot be defended to a customs officer, which is the only audience that matters here.

## Assumptions and limits

- **Tier-1 visibility only:** the statute reaches *any* input made wholly or in part
  in XUAR — tier-2/3 exposure (e.g. XUAR cotton in Vietnamese garments) requires
  chain-of-custody mapping this record-level check cannot see (the GNN feature
  `UFLPA_exposure`, CPT-0069, is the network-level complement).
- The Entity List and the high-priority sectors (cotton, tomatoes, polysilicon —
  since expanded, e.g. aluminium, seafood, and 2025-26 additions) **grow by DHS/FLETF
  updates** — the hardcoded HS set is a snapshot; refresh against the current UFLPA
  Strategy list.
- A `clearance_document_ref` prevents PROHIBITED but never grants LOW — documentation
  is a rebuttal *attempt*, judged by CBP, not by this function.
- **Does not apply when:** goods never enter US commerce (the presumption is an import
  bar; EU forced-labour Regulation 2024/3015 is separate law with its own test).

## Worked example

Supplier operates in XUAR, ships HS 610910 (T-shirts), holds clearance docs → HIGH:
importable only with the evidence package ready for CBP detention review.

## Governing rules

- **SCM-R6** — XUAR suppliers must provide `clearanceDocumentRef` (the rule this
  classification enforces).

## Related

- CPT-0098 Composite compliance score — UFLPA is one of its inputs; the weighting is
  project-chosen.
- CPT-0069 GNN network risk — propagates UFLPA exposure upstream.

## References

- UFLPA, Pub. L. 117-78 (2021); CBP UFLPA Entity List & FLETF Strategy (updated
  continuously); CBP operational guidance on detentions.
