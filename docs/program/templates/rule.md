---
id: program-rule-template
title: "rule.md Template (hard rules per area)"
type: program
owner: orchestrator
status: draft
since: 2026-07-19
updated: 2026-07-19
relations:
  - { type: part-of, target: index-program }
  - { type: governed-by, target: governance-root }
---
# rule.md template

> The area's **law**: checkable, testable, citable. Lives at
> `docs/{40-contexts/<context>,30-foundation/<axis>}/rule.md` with `type: rule`
> front-matter. Allocate the `<CTX>` prefix in the ID registry. IDs are append-only:
> existing IDs are frozen, new ones are appended, none is ever renumbered. Rules from
> other areas are **referenced by ID, never restated**.

```markdown
# Rules — <Area Name>

## Invariants (NEVER violated — each verifiable by test)
- <CTX>-R1: <hard rule stated so a test can fail it>
- <CTX>-R2: …

## Mandatory validations
- <input/action> must <condition> and requires permission <perm>.

## Policies
- <default behaviors and their change procedure — e.g. "changing the policy is an audited
  event and does not apply retroactively without approval">

## Anti-states (what the system must never allow)
- <forbidden state 1 — e.g. an orphan record referencing a nonexistent master>
- <forbidden state 2 — e.g. a critical change without an audit trail>

## Inherited rules (referenced, not restated)
- <OTHER>-Rx — <one line on why it applies here>
```
