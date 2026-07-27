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

## Regulatory drift to watch

> Compliance nodes carry the shortest half-life in this catalogue: the law moves, and a node
> stating superseded law is worse than no node. Each entry names what changed and when it
> applies, so a re-check has somewhere to start.

- **CSDDD (CPT-0093)** — **Directive (EU) 2026/470 (Omnibus I)** replaced the original
  three-phase scope of 2024/1760 with a single band, **>5,000 employees ∧ >€1.5B net turnover,
  applying 26 Jul 2029**. A project scoping itself reads the amended text; the phase-in is
  history.
- **CBAM (CPT-0100..0102)** — the Omnibus Regulation (Oct 2025) introduced a 50 t/yr de-minimis,
  moved certificate sales to Feb 2027, and set the declaration deadline at 30 Sep. The 50%
  quarterly holding requirement is the amended rate.
- **REACH (CPT-0095)** — applying the Art. 31 safety-data-sheet duty to articles is a
  conservative reading; the Art. 33 communication duty and ECHA notification are the provisions
  that actually bind for articles, and they differ in trigger and timing.
- **Retention dating (CPT-0096)** — counting a retention period in years versus days differs by
  a day across a leap boundary. Which method applies is a legal-interpretation question, and the
  answer should be recorded rather than left to whichever function ran.
