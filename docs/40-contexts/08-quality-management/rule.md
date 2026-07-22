---
id: rule-quality-management
title: "Rules — Quality Management (QMS-R*)"
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
# Rules — Quality Management

> Invariants enforced in `src/departments/08-quality-management/` (NCR, SCAR/8D,
> inspection/AQL, SPC). Know-how lives in the allowlisted homes (`README.md`,
> `IMPLEMENTATION.md`, `.claude/skills/quality-management/`). IDs append-only (family
> `QMS`). Inherited `SCM-R*` referenced, never restated.

## Invariants (NEVER violated — each verifiable by test)

- **QMS-R1:** An NCR cannot be closed while any corrective action is marked `INEFFECTIVE`,
  and it closes only from `VERIFICATION_PENDING` (`NCR.ts`).
- **QMS-R2:** The NCR lifecycle is strict (open → investigate → root-cause → disposition
  → corrective-actions → verify → close); each step is valid only from its allowed prior
  status, and a `CLOSED` NCR cannot be voided.
- **QMS-R3:** An NCR requires `affectedQty > 0` and a non-empty defect description; a
  corrective action cannot be completed twice.
- **QMS-R4:** Quality cost values (COPQ) are non-negative integer cents.

## Mandatory validations

- Starting an investigation requires a containment action; setting a root cause requires a
  description; voiding requires a reason.

## Anti-states (the system must never allow)

- A closed NCR with an ineffective corrective action (QMS-R1).
- A voided NCR that was already closed (QMS-R2).

## Inherited rules (referenced, not restated)

- **SCM-R3** — NCRs, SCARs and inspection records are soft-deleted only.
- **SCM-R8** — cost/COPQ money is integer cents.
