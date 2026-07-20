---
id: rule-scm-core
title: "Rules — SCM Core (cross-department) SCM-R1..R13"
type: rule
owner: orchestrator
status: active
since: 2026-07-19
updated: 2026-07-19
relations:
  - { type: part-of, target: index-foundation }
  - { type: governed-by, target: index-adr }
---
# Rules — SCM Core (cross-department)

> The stable-ID home for the rules previously stated only in `CLAUDE.md` (§Critical
> Business Rules, §Code Standards). Extracted at skeleton adoption (ADR-0010) with intent
> preserved; from now on THIS file is the single edit point and other docs cite the IDs
> (`CLAUDE.md` dedup = WORKFLOW U3). IDs are append-only: frozen once allocated, new ones
> appended, never renumbered. Skill counterpart:
> `.claude/skills/supply-chain-core/SKILL.md`.

## Invariants (NEVER violated — each verifiable by test)

- **SCM-R1:** Inventory balance never goes negative unless the item has
  `backorderAllowed = true`.
- **SCM-R2:** A purchase order at or above the approval threshold
  (`PO_APPROVAL_THRESHOLD_CENTS`, default $5,000) enters `PENDING_APPROVAL` and cannot
  bypass approval.
- **SCM-R3:** Financial records (POs, invoices, stock movements, shipments, scorecards)
  are soft-deleted only (`isDeleted`); a hard delete never happens (ADR-0007).
- **SCM-R4:** Every stock movement generates its double-entry GL journal mapping
  (debit/credit accounts) — no movement without a journal entry (ADR-0005).
- **SCM-R5:** Lot tracking is mandatory when `storageCondition !== AMBIENT` or
  `reachSVHC = true`.

## Mandatory validations (compliance)

- **SCM-R6:** A supplier with XUAR operations must provide `clearanceDocumentRef`
  before transacting (UFLPA).
- **SCM-R7:** CSDDD due-diligence documents are retained ≥ 5 years from assessment date
  (Art. 23).

## Data conventions (ADR-0006; SCM-R8 rewritten by ADR-0019)

- **SCM-R8:** Money is **arbitrary-precision Decimal** (`decimal.js` in TS,
  `decimal.Decimal` in Python, `NUMERIC(19,4)` in Postgres, **string** across gRPC).
  Float arithmetic never touches a monetary value. Rounding is **explicit and banker's
  (`ROUND_HALF_EVEN`)**, applied only at defined boundaries (persistence, display,
  allocation remainder) — never implicitly mid-calculation. *(Was "integer cents" under
  ADR-0006; rewritten by ADR-0019. The ID is retained; department citations by ID stay
  valid. Migration is backlog — until it lands, `Money.amount: number` remains in code and
  this rule states the target, so a reviewer treats new float-money paths as violations.)*
- **SCM-R9:** Dates are ISO 8601 (`YYYY-MM-DD`); timestamps are UTC (`ISOTimestamp`).
- **SCM-R10:** Quantity units use GS1 UOM codes (`UOM` constant, `shared/types.ts`).
- **SCM-R11:** SKU codes are immutable once created; lifecycle is expressed via status
  flags (ACTIVE / DISCONTINUED / BLOCKED), never by editing the code.
- **SCM-R12:** Inventory transactions carry an `idempotencyKey` and are safe to retry —
  a retry never duplicates (ADR-0007).

## Engineering conventions

- **SCM-R13:** Python code carries mandatory type hints and docstrings on public
  functions; Python tests (pytest) mirror TypeScript test coverage (ADR-0009).

## Anti-states (the system must never allow)

- Negative stock without backorder authorization (violates SCM-R1).
- A stock movement without its journal entry or outside the event log (SCM-R4, ADR-0005).
- A hard-deleted financial record (SCM-R3).
- A retried transaction that duplicated its effect (SCM-R12).
- Monetary drift from float arithmetic (SCM-R8).
