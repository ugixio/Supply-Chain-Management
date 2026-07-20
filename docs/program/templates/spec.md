---
id: program-spec-template
title: "Unit-of-Work Spec Template (16 sections)"
type: program
owner: orchestrator
status: draft
since: 2026-07-19
updated: 2026-07-19
relations:
  - { type: part-of, target: index-program }
  - { type: governed-by, target: governance-root }
---
# Unit-of-work spec template

> One spec per unit of work (module / feature family), at
> `docs/40-contexts/<context>/specs/<key>.md` with `type: context-spec` front-matter.
> The 16 sections are the checklist; a section that does not apply says so explicitly
> ("N/A — <why>") instead of disappearing. The WHAT lane writes it; the HOW lane turns
> §14 into tests.

```markdown
# Spec — `<key>`

## 1. Identity
Key, context, owner lane, status/maturity, decisions it traces to.

## 2. Purpose and business context
What this unit solves and for whom; where it sits in the product model.

## 3. Scope
In-scope / out-of-scope for THIS unit (out-of-scope items link to §15 or the register).

## 4. Domain model (pure)
### 4.1 Entities and aggregates
### 4.2 Value objects
### 4.3 Domain invariants — cite `<CTX>-Rx` from the context rule.md, never restate

## 5. Use cases / operations
One subsection per operation: actor, required permission, input, rules applied, output,
events emitted, error cases. Include read/query operations.

## 6. Contract / manifest
Machine-readable declaration: depends_on, provides, consumes (+ the file it lives in).

## 7. Provided / consumed capabilities
What this unit offers other units and what it needs from them — by contract, never by
reading internals.

## 8. Events
Published / subscribed, with payload sketch and when each fires.

## 9. Permissions
The permissions this unit introduces and who holds them by default.

## 10. Data model / persistence
Tables/collections and migrations owned by this unit (created only when the unit is
activated/justified — contract §2.5).

## 11. Derived metrics / rollups (if any)
What aggregates upward, and how.

## 12. UI surface (if any)
Screens derived from this spec; states (loading/empty/error/data); no business rules in
the UI.

## 13. Dependencies and activation
What must exist first; what happens on activation/enablement; idempotency of the process.

## 14. Definition of Done (acceptance criteria → tests)
Numbered, testable criteria. Every §4.3 invariant appears here as a test.

## 15. Out of scope / future
Deliberate deferrals with their revisit trigger.

## 16. Traceability
Decisions, rules, product-model sections and catalog rows this spec implements/refines.
```
