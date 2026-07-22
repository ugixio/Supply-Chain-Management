---
id: rule-supplier-development
title: "Rules — Supplier Development (SDV-R*)"
type: rule
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-contexts }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: rule-scm-core }
---
# Rules — Supplier Development

> Invariants enforced in `src/departments/14-supplier-development/` (ESG scoring, Tier-2
> cascade, EUDR/EU deforestation). Know-how lives in the allowlisted homes (`README.md`,
> `IMPLEMENTATION.md`, `.claude/skills/supplier-development/`). IDs append-only (family
> `SDV`). Inherited `SCM-R*` referenced, never restated.

## Invariants (NEVER violated — each verifiable by test)

- **SDV-R1:** An ESG score is within [0, 100] (`Tier2ESGCascade.ts`).
- **SDV-R2:** A Tier-2 ESG cascade record requires its provenance — `tier1SupplierId`,
  `tier2SupplierName` and `tier2Country`; no anonymous cascade entry.
- **SDV-R3:** An EUDR assessment requires a `supplierId`, an `assessmentDate`, and a
  `countryOfOrigin` that is a valid ISO 3166-1 alpha-2 code; a closed assessment cannot be
  re-verified (`EUDRAssessment.ts`).

## Anti-states (the system must never allow)

- An ESG score outside [0, 100] (SDV-R1).
- An EUDR assessment with an invalid or missing country of origin (SDV-R3).

## Inherited rules (referenced, not restated)

- **SCM-R7** — due-diligence documents retained ≥ 5 years.
- **SCM-R9** — assessment dates ISO 8601.
