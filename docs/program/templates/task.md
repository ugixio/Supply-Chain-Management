---
id: program-task-template
title: "Task Template for an Agent"
type: program
owner: orchestrator
status: draft
since: 2026-07-19
updated: 2026-07-19
relations:
  - { type: part-of, target: index-program }
  - { type: governed-by, target: governance-root }
---
# Task template for an agent

> Copy this block when assigning work to an agent. Keep the task **bounded** (one unit /
> use case). A task without a spec input is a spec task for the WHAT lane, not an
> implementation task.

```
Agent: <agent id>
Context: unit <key>, layer <domain|application|infrastructure|interface|api|ui|...>.
Task: <concrete and single objective>.
Inputs: <relevant spec / manifest / API contract / rule.md>.
Constraints: respect CLAUDE.md (hard rules) + ADRs + the area's rule.md.
Done when:
  - builds and `<run> lint` clean
  - `<run> test` green (incl. invariant tests <CTX>-Rx and boundary tests)
  - <audit trail/event if it is a critical action>
  - coherent contract/manifest (if it touches one)
  - commit message (Conventional Commits) proposed
Git branch: feat/<unit-or-case>
```

## Example

```
Agent: <how-lane-agent>
Context: unit <key>, layer domain.
Task: implement the <Entity> entity and the <ValueObject> value object with their invariants.
Inputs: docs/40-contexts/<context>/specs/<key>.md §4, docs/40-contexts/<context>/rule.md (<CTX>-R1, <CTX>-R4).
Constraints: pure domain (no IO/framework imports); <ValueObject> validates its invariant on construction.
Done when: <CTX>-R1 and <CTX>-R4 tests green; lint clean; commit proposed.
Git branch: feat/<key>
```
