---
id: rule-compliance-regulatory
title: "Rules — Compliance & Regulatory (CMP-R*)"
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
# Rules — Compliance & Regulatory

> Invariants enforced in `src/departments/09-compliance-regulatory/` (CSDDD, UFLPA, REACH,
> CBAM, conflict minerals). Know-how lives in the allowlisted homes (`README.md`,
> `IMPLEMENTATION.md`, `.claude/skills/compliance-regulatory/`). IDs append-only (family
> `CMP`). This department is the enforcement point for the estate's regulatory `SCM-R*`.

## Invariants (NEVER violated — each verifiable by test)

- **CMP-R1:** A compliance exception requires a `validUntil` date that is in the future
  and a recorded `approvedBy`; it never grants an open-ended or back-dated waiver
  (`ComplianceException.ts`).
- **CMP-R2:** Every compliance record (evidence, exception) carries its provenance —
  `supplierId`, a document/justification reference and the acting user; no anonymous or
  undocumented compliance record is accepted (`ComplianceEvidence.ts`).
- **CMP-R3:** REACH — an article containing an SVHC above 0.1% w/w triggers SDS,
  ECHA-notification (Art. 7(2)) and supply-chain-communication (Art. 33) obligations; a
  required-but-unrecorded ECHA notification is treated as **not compliant**
  (`regulations/REACH.ts`; conservative reading — modeling the notification record is a
  follow-up, `program/WORKFLOW.md` U11).

## Mandatory validations

- Date fields (`validUntil`, `assessmentDate`) validate `YYYY-MM-DD` and, where a waiver,
  must be a future date.

## Anti-states (the system must never allow)

- A compliance exception with no expiry or no approver (CMP-R1).
- An article shipped with an unaddressed SVHC obligation (CMP-R3).

## Inherited rules (referenced, not restated)

- **SCM-R6** — a supplier with XUAR operations must supply a UFLPA clearance document
  reference before transacting.
- **SCM-R7** — CSDDD due-diligence documents are retained ≥ 5 years from assessment date.
- **SCM-R5** — a REACH SVHC article requires lot tracking.
