---
id: program-improvement-register
title: "Improvement Register — continuous improvement log"
type: program
owner: orchestrator
status: draft
since: 2026-07-19
updated: 2026-07-19
relations:
  - { type: part-of, target: index-program }
  - { type: governed-by, target: governance-root }
---
# Improvement Register

> The continuous-improvement loop, made a register (ADR-0012): when a task, incident or
> review teaches a **structural** lesson (about the process, the templates, the rules —
> not about one bug), it lands here and drives a change: a template edit, a new rule, an
> ADR, a gate. Rows are appended, never rewritten; a lesson without a resulting change is
> explicitly marked `accepted-as-is` with the reason.

## How to use

- A row is appended at task end (the self-review's "estimate honesty" and backlog
  follow-ups feed this register).
- The owner reviews open rows when planning; a row is closed only by the change it
  produced (link it) or by an explicit decision not to act.
- Lessons that change governing knowledge go through their normal path (ADR for
  decisions, supersession for rules) — this register points at the change, it is never
  the change itself.

## Register

| # | Date | Source | Lesson | Structural change | Status |
|---|---|---|---|---|---|
| 1 | 2026-07-19 | commit `a12c114` (pre-adoption) | the same formula duplicated in TS and Python silently diverged — duplicated logic without a shared oracle WILL drift | golden test vectors shared by both languages (backlog U8) | open |
| 2 | 2026-07-19 | first `npm install` of the repo (skeleton unification) | declared dev tooling was mutually uninstallable (`eslint ^9` + `@typescript-eslint ^7`) — nothing had ever verified the toolchain itself | dependency fix + committed lockfile + CI running the real commands (ADR-0013, U6) | done |
| 3 | 2026-07-19 | v0.2 skeleton audit | structural completeness ≠ model impact: exemplars, context budgets, recorded corrections and a fast gate move AI results more than added rules | ADR-0012 (exemplar, G9 budgets, pitfalls, verify split, handoff) | done |
