---
id: rule-supply-planning
title: "Rules — Supply Planning (SPL-R*)"
type: rule
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-27
relations:
  - { type: part-of, target: index-contexts }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: rule-scm-core }
---
# Rules — Supply Planning

> **A rule lives here only if something outside this repository fixes it** — a standards body, a
> regulator, or an arithmetic identity (ADR-0037). Anything an organization can reasonably choose
> is a **project decision** and is listed as such, never as an invariant. IDs are append-only
> (family `SPL`); a retired ID stays listed so old citations resolve. Cross-department rules
> (`SCM-R*`) are inherited, referenced never restated.

## Invariants (externally fixed — NEVER violated)

- **SPL-R1:** A bill of materials is **acyclic** — no component is its own ancestor. A cycle makes
  the requirement explosion non-terminating and the lead-time roll-up undefined. *A structural
  identity of a directed acyclic graph,* not a preference.
- **SPL-R2:** A structure's validity interval ends **after** it begins, and a BOM in effect has at
  least one component — a parent with no children explodes to nothing. *Identities.*
- **SPL-R5:** Netting **conserves**: `net requirement = gross requirement − available − scheduled
  receipts`, floored at zero. Requirements already covered are not re-ordered. *An arithmetic
  identity.*

## Retired rules

> Retired because they stated **project policy or an implementation detail** of code this
> repository no longer contains (ADR-0037). Listed permanently so citations resolve.

| ID | Was | Why retired |
|---|---|---|
| **SPL-R3** | "A capacity plan cannot be approved while `INFEASIBLE`" | An approval gate over invented states. Whether an infeasible plan may be approved deliberately — with the shortfall documented — is a planning-process decision, and sometimes the right one. |
| **SPL-R4** | "`planningHorizonWeeks` is within [1, 52]" | An arbitrary bound. A horizon follows the longest cumulative lead time in the supply chain, which for some industries exceeds a year. |

## Project decisions (the questions this department must answer for itself)

- The **planning horizon** and the **bucket** (day, week, month) — set by cumulative lead time and
  by how often the plan is regenerated, not by convention.
- The **lot-sizing rule**: lot-for-lot, fixed quantity, period order quantity, EOQ, or a dynamic
  method (Wagner–Whitin, Silver–Meal). Several are legitimate.
- **Firm and frozen zones** — how far out the plan may change, and who may change it.
- Whether **infeasible** plans can be approved, and what must be recorded when they are.
- **Safety lead time versus safety stock** — which buffer absorbs supply variability.

## Inherited rules (referenced, not restated)

- **SCM-R9 / R10** — dates and periods ISO 8601; quantities carry GS1 units.
- **SCM-R14** — where a requirement is apportioned across sources, the parts sum to the whole.
