---
id: rule-supplier-management
title: "Rules — Supplier Management (SUP-R*)"
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
# Rules — Supplier Management

> Invariants enforced in `src/departments/02-supplier-management/`. Know-how lives in the
> allowlisted homes (`README.md`, `IMPLEMENTATION.md`, `.claude/skills/supplier-management/`).
> IDs append-only (family `SUP`). Inherited `SCM-R*` referenced, never restated.

## Invariants (NEVER violated — each verifiable by test)

- **SUP-R1:** A supplier audit cannot be closed while any `MAJOR_NC` finding is open, and
  its outcome cannot be set `APPROVED` when major non-conformances exist
  (`SupplierAudit.ts`).
- **SUP-R2:** The supplier-audit lifecycle is status-guarded — start, add-finding,
  issue-report and close are each valid only from their allowed prior status; no
  transition skips a state.
- **SUP-R3:** Completing an onboarding checklist item requires both a `documentRef` and a
  `verifiedBy`; an onboarding cannot be approved while any required checklist item is
  incomplete (`SupplierOnboarding.ts`).
- **SUP-R4:** Onboarding approval is valid only from `APPROVAL_PENDING` and requires an
  `approvedBy` and a `qualificationScore` within [0, 100].

## Mandatory validations

- Date fields validate `YYYY-MM-DD` format before use.
- `supplierId` is required and non-empty on onboarding creation.

## Anti-states (the system must never allow)

- A closed audit with an unresolved major non-conformance (SUP-R1).
- An approved onboarding with an incomplete required checklist item (SUP-R3).

## Inherited rules (referenced, not restated)

- **SCM-R6** — a supplier with XUAR operations must supply a UFLPA clearance document
  reference before transacting.
- **SCM-R3** — supplier scorecards and audit records are soft-deleted only.
- **SCM-R9** — dates ISO 8601.
