---
id: rule-demand-planning
title: "Rules — Demand Planning (DMD-R*)"
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
# Rules — Demand Planning

> **A rule lives here only if something outside this repository fixes it** — a standards body, a
> regulator, or an arithmetic identity (ADR-0037). Anything an organization can reasonably choose
> is a **project decision** and is listed as such, never as an invariant. IDs are append-only
> (family `DMD`); a retired ID stays listed so old citations resolve. Cross-department rules
> (`SCM-R*`) are inherited, referenced never restated.

## Invariants (externally fixed — NEVER violated)

- **DMD-R6:** Absolute percentage error is **undefined when the actual is zero** — the
  denominator vanishes. It is recorded as undefined and excluded from the mean, never substituted
  with a zero or a large sentinel, both of which corrupt the aggregate. *An arithmetic identity;*
  a series with zeros needs a scale-free measure instead (CPT-0009).
- **DMD-R9:** A forecast is stated **with its horizon and its bucket**. The same series forecast
  daily and monthly are different numbers, and comparing accuracy across buckets is meaningless.
  *A measurement identity:* an error metric without its bucket has no interpretation.

## Retired rules

> Retired because they stated **project policy or an implementation detail** of code this
> repository no longer contains (ADR-0037). Listed permanently so citations resolve.

| ID | Was | Why retired |
|---|---|---|
| **DMD-R1** | "A demand plan cannot be submitted with no lines; an `APPROVED` plan is immutable" | Immutability of an approved plan is good discipline and a design choice; the states are invented. |
| **DMD-R2** | "`confidencePct` is within [0, 100]" | A field-range check on an invented field. |
| **DMD-R3** | "The demand-plan status machine is strict (draft → submit → approve → …)" | An invented workflow. |
| **DMD-R4** | "A run's forecast values, `mape` and `mae` are all non-negative" | True of the metrics by construction (they are means of absolute values), so it restated arithmetic; the rest was a field check. |
| **DMD-R5** | "A SKU enters statistical accuracy reporting only with ≥ N observations" | The minimum history is a project's judgement about when a statistic is trustworthy. |
| **DMD-R7** | "Every consensus override is classified against the statistical baseline" | Whether overrides are classified, and into what, is an S&OP process design. |
| **DMD-R8** | "Actual safety stock is flagged against the Method-4 value" | Mandates one safety-stock method as the reference. Several are legitimate (CPT-0012..0015) and the choice is the project's. |

## Project decisions (the questions this department must answer for itself)

- The **forecasting method** per series, and how it is selected (CPT-0011 defines selection as a
  concept; it does not mandate an outcome).
- The **service level** and therefore `z` (CPT-0003), and the **safety-stock method** (CPT-0012..0015).
- The **minimum history** before a statistic is reported, and how outliers are treated.
- The **accuracy measure** that governs — MAPE, WMAPE, RMSE and sMAPE answer different questions
  and rank forecasts differently (CPT-0008/0009).
- The **bucket and horizon** the plan is stated in.
- Whether an approved plan is **immutable**, and what an override must record.

## Inherited rules (referenced, not restated)

- **SCM-R9 / R10** — ISO 8601 dates and periods; GS1 units.
- **SCM-R3** — an approved plan is superseded by a new version, not overwritten in place.
