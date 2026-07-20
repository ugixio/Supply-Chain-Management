---
id: risk-register
title: "Risk Register"
type: governance
owner: orchestrator
status: draft
since: 2026-07-19
updated: 2026-07-19
relations:
  - { type: part-of, target: index-governance }
  - { type: governed-by, target: knowledge-architecture }
---
# Risk Register

> The single home for **identified risks** — technical, security, delivery and knowledge
> risks that are accepted-for-now rather than fixed-now (ADR-0012). A row makes the
> exposure visible, owned and reviewable; it never substitutes for fixing what a hard
> rule forbids. Rows are appended and updated in status; closed risks stay listed
> (mitigated / retired), never deleted.

## How to use

- Anyone may PROPOSE a risk; the owner accepts it into the register.
- Every risk has exactly one owner and a **review trigger** (an event or date that forces
  a re-look). A risk without a trigger is a worry, not a register entry.
- A risk that hardens into policy becomes a rule (`rule.md`) or a decision (ADR), and the
  row links to it. A risk deliberately left open cites the reasoning.
- Score likelihood and impact coarsely (`low | medium | high`) — the register ranks
  exposures; it does not pretend precision.

## Register

| # | Risk | Likelihood | Impact | Owner | Mitigation / response | Status | Review trigger |
|---|---|---|---|---|---|---|---|
| 1 | Zero Python test files while `python/` holds half the estate's logic (SCM-R13 mirror-coverage bar unmet) | high | high | orchestrator | backlog U7 (pytest suite); until then Python changes need reviewer scrutiny | open | U7 done |
| 2 | Formulas duplicated across TS and Python have already diverged once (commit `a12c114`) and can diverge again | medium | high | orchestrator | golden test vectors shared by both languages (backlog U8); evaluation.md §1.4 both-or-neither rule | open | U8 done |
| 3 | Default branch on GitHub is `claude/bold-cannon-l7wtso`, not a stable main line | high | medium | human | set `main` as default and protect it when the unification branch merges (ADR-0011) | open | branch merge |
| 4 | `python/` contains two order-management packages (`07_order_management/` and `13_order_management/`) with overlapping names — numbering collision with `07_logistics_transportation` | medium | medium | orchestrator | WHAT-lane review: consolidate or rename to match the 14-department taxonomy (ADR-0004) | open | first task touching either package |
| 5 | Gate G8 (English-only) is not machine-checked; prose drift can enter unnoticed | medium | low | orchestrator | manual review at merge; automate if drift is observed | open | first observed violation |
| 6 | Heavy ML dependencies (`torch`, `tensorflow`, `ray`) make the Python toolchain unrunnable in CI for now | medium | medium | orchestrator | CI runs TS + doc gates only; Python gate lands with U7 (split a light requirements file for CI) | open | U7 done |
