---
id: rule-risk-management
title: "Rules — Risk Management (RSK-R*)"
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
# Rules — Risk Management

> **A rule lives here only if something outside this repository fixes it** — a standards body, a
> regulator, or an arithmetic identity (ADR-0037). Anything an organization can reasonably choose
> is a **project decision** and is listed as such, never as an invariant. IDs are append-only
> (family `RSK`); a retired ID stays listed so old citations resolve. Cross-department rules
> (`SCM-R*`) are inherited, referenced never restated.

## Invariants (externally fixed — NEVER violated)

- **RSK-R2:** Residual risk **cannot exceed** inherent risk. Residual is what remains *after*
  controls, so a control that raised the score was mis-scored or introduced a new risk that
  belongs in its own entry. *An identity of the definition.*
- **RSK-R5:** A **risk score built from ordinal scales is ordinal**. Multiplying a likelihood rank
  by an impact rank yields a rank, not a quantity: a 20 is not twice a 10, distinct pairs collapse
  onto one number (4×5 and 5×4 both give 20 while demanding different responses), and averaging
  such scores across a portfolio is meaningless. *A measurement-theory fact,* stated because
  the arithmetic is trivial to perform and the conclusion is wrong.
- **RSK-R6:** **Expectation is not exposure.** Expected annual loss is a mean; two risks with the
  same mean can differ by orders of magnitude in the tail. EAL ranks and budgets, a tail measure
  sizes reserves. *A property of the statistic.*

## Retired rules

> Retired because they stated **project policy or an implementation detail** of code this
> repository no longer contains (ADR-0037). Listed permanently so citations resolve.

| ID | Was | Why retired |
|---|---|---|
| **RSK-R1** | "Probability and impact are each integers within [1, 5]" | The 5×5 matrix is a widely-used **convention**, not a standard: 3×3 and 4×4 are equally legitimate, and ISO 31000 prescribes no scale. What survives is the arithmetic warning, **RSK-R5**. |
| **RSK-R3** | "Accepting a risk requires a non-empty justification; the status machine…" | The justification is good governance and a project's requirement; the states were invented. |
| **RSK-R4** | "BCP drill `rtoTargetHours` and `rpoTargetHours` are strictly positive" | A field check on invented fields. The targets themselves are business decisions about tolerable downtime and data loss. |

## Project decisions (the questions this department must answer for itself)

- The **scale** of the risk matrix and every **band boundary** on the score — these express risk
  appetite (CPT-0072 defines the structure and supplies no values).
- What each band **obliges**: acceptance, mitigation, escalation, or exit.
- **Recovery time and recovery point objectives** — a judgement about tolerable downtime and data
  loss, priced against the cost of resilience.
- The **confidence level** for any value-at-risk measure.
- **Which risks are in scope**, and how far into the supply base risk assessment reaches.

## Inherited rules (referenced, not restated)

- **SCM-R7** — where risk assessment is part of due diligence, its documentation is retained at
  least five years.
- **SCM-R14** — a risk budget apportioned across categories sums to the budget.
