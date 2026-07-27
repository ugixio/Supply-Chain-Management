---
id: rule-sop-planning
title: "Rules — S&OP Planning (SOP-R*)"
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
# Rules — S&OP Planning

> **A rule lives here only if something outside this repository fixes it** — a standards body, a
> regulator, or an arithmetic identity (ADR-0037). Anything an organization can reasonably choose
> is a **project decision** and is listed as such, never as an invariant. IDs are append-only
> (family `SOP`); a retired ID stays listed so old citations resolve. Cross-department rules
> (`SCM-R*`) are inherited, referenced never restated.

## Invariants (externally fixed — NEVER violated)

- **SOP-R4:** A consensus plan is **one plan**. If demand, supply and finance leave the cycle with
  different numbers, no consensus was reached and the artefact is a set of parallel forecasts
  wearing one name. *An identity of what consensus means,* and the failure mode S&OP exists to
  prevent.
- **SOP-R5:** Plan attainment is measured against the plan **as it stood when it was committed**,
  not against the plan as later revised. Measuring against a revised plan makes attainment
  unfalsifiable — the target moves to wherever the outcome landed. *A measurement identity.*

## Retired rules

> Retired because they stated **project policy or an implementation detail** of code this
> repository no longer contains (ADR-0037). Listed permanently so citations resolve.

| ID | Was | Why retired |
|---|---|---|
| **SOP-R1** | "The S&OP cycle status machine is strict — approved only from…" | An invented workflow. The S&OP *process* (demand review, supply review, reconciliation, management review) is well established; these particular states were not. |
| **SOP-R2** | "A consensus forecast quantity is strictly positive" | A field check, and wrong in general: a planned reduction, a return flow or a phase-out can be zero or negative. |
| **SOP-R3** | "Plan-attainment computation requires a positive plan quantity" | Division by zero restated. A period with no plan has no attainment — that is undefined, not an error to guard. |

## Project decisions (the questions this department must answer for itself)

- The **cycle cadence** (monthly is common, weekly and quarterly both exist) and the **horizon**.
- Who **participates** in each review and who **arbitrates** a disagreement.
- The **aggregation level** at which the plan is agreed — family, brand, or SKU.
- What an **override** must record, and whether overrides are measured against the statistical
  baseline afterwards.
- **Attainment expectations**, and the tolerance within which a plan counts as met.

## Inherited rules (referenced, not restated)

- **SCM-R9** — periods and dates ISO 8601.
- **SCM-R3** — a committed plan is superseded by a new version, and the committed version stays
  readable (which is what makes SOP-R5 possible).
