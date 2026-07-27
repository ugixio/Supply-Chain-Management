---
id: index-concepts-09-compliance-regulatory
title: "Concepts — Compliance & Regulatory (09)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-27
relations:
  - { type: part-of, target: index-concepts }
  - { type: governed-by, target: index-adr }
  - { type: traces-to, target: rule-compliance-regulatory }
---
# Concepts — Compliance & Regulatory (09)

> The concept catalogue for **Compliance & Regulatory (09)**: what each concept *means*,
> the formula where one is canonical, its assumptions and limits, and the standard or
> regulation that fixes it. Nodes **define**; they hold no threshold, target, weighting or
> mandated method, and they own no code (ADR-0037). Values a project must choose are named
> as project-chosen inputs and left unset.
>
> Departmental law lives in [40-contexts/09-compliance-regulatory/rule.md](../../40-contexts/09-compliance-regulatory/rule.md).

## Catalogue

### Due-diligence regimes

| ID | Concept | Use when |
|---|---|---|
| [CPT-0093](csddd-applicability-phase.md) | CSDDD applicability phase | EU due-diligence scoping (see drift note) |
| [CPT-0094](uflpa-risk-assessment.md) | UFLPA risk assessment | US forced-labour import exposure |
| [CPT-0095](reach-svhc-compliance.md) | REACH SVHC compliance | Chemical obligations per substance |
| [CPT-0096](document-retention-deadlines.md) | Retention deadlines | Evidence keep-until dates (SCM-R7) |
| [CPT-0097](grievance-resolution-sla.md) | Grievance SLA | Complaints-mechanism clocks |
| [CPT-0098](composite-compliance-risk-score.md) | Composite compliance score | Cross-regulation supplier grade |
| [CPT-0099](conflict-minerals-compliance.md) | Conflict minerals (3TG) | Dodd-Frank/SEC 13p-1 toolchain |

### CBAM (EU 2023/956)

| ID | Concept | Use when |
|---|---|---|
| [CPT-0100](cbam-embedded-emissions.md) | Embedded emissions | Quantifying import CO₂e |
| [CPT-0101](cbam-certificates-and-holding.md) | Certificates & quarterly holding | Surrender/holding obligations |
| [CPT-0102](cbam-cost-and-sector-scope.md) | Cost & HS sector scope | Pricing the liability; scoping goods |

## Divergences & regulatory drift (for the backlog)

- **CSDDD (CPT-0093)** — the implemented 3-phase model follows the original
  2024/1760; **Directive (EU) 2026/470 (Omnibus I)** replaced it with a single
  >5,000-employee / >€1.5B band applying 26 Jul 2029. Code update required.
- **CBAM (CPT-0100..0102)** — Omnibus Regulation (Oct 2025): 50 t/yr de-minimis
  (not modelled), certificate sales from Feb 2027, declaration due 30 Sep; the
  50% quarterly holding default matches the amended rate.
- **Two retention dating methods (CPT-0096)** disagree by ±1 day at leap boundaries.
- **REACH (CPT-0095)** — Art. 31 SDS applied to articles is a conservative
  simplification; ECHA-notification tracking still open (U11b).
- **`ipsa_required` (CPT-0099)** tests a claim literal the classifier never emits —
  wire it to the product-claim decision, not the screening result.
