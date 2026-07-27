---
id: rule-quality-management
title: "Rules — Quality Management (QMS-R*)"
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
# Rules — Quality Management

> **A rule lives here only if something outside this repository fixes it** — a standards body, a
> regulator, or an arithmetic identity (ADR-0037). Anything an organization can reasonably choose
> is a **project decision** and is listed as such, never as an invariant. IDs are append-only
> (family `QMS`); a retired ID stays listed so old citations resolve. Cross-department rules
> (`SCM-R*`) are inherited, referenced never restated.

## Invariants (externally fixed — NEVER violated)

- **QMS-R5:** A sampling plan is taken from the **ISO 2859-1 table** for the lot size, inspection
  level and AQL — sample size and the accept/reject numbers are read from it, never interpolated
  or rounded to a convenient figure. The plan's statistical properties (its operating
  characteristic curve) hold only for the tabulated combinations. *Source:* ISO 2859-1.
- **QMS-R6:** **Accepting a sample is not accepting a lot's quality.** An acceptance sampling plan
  bounds the probability of accepting a lot worse than the AQL; it does not certify the lot. A
  passed inspection is evidence, not a guarantee. *A property of the method,* stated because it is
  the most common misreading of an AQL result.
- **QMS-R8:** A corrective action is not complete until its **effectiveness has been reviewed**.
  Taking the action and recording it is not the requirement; determining whether the nonconformity
  can still recur is. *Source:* ISO 9001:2015 §10.2.1 — the organization shall review the
  effectiveness of any corrective action taken, and §10.2.2 requires the results retained as
  documented information. *What* evidence counts as proof of effectiveness, how long the
  observation window is, and who signs it off are the project's design.
- **QMS-R7:** Defect rates are stated **with their opportunity base**. PPM counts defective units
  per million units; DPMO counts defects per million *opportunities*, so a product with several
  inspection points has more opportunities than units and the two numbers are not comparable.
  *A measurement identity.*

## Retired rules

> Retired because they stated **project policy or an implementation detail** of code this
> repository no longer contains (ADR-0037). Listed permanently so citations resolve.

| ID | Was | Why retired |
|---|---|---|
| **QMS-R1** | "An NCR cannot be closed while any corrective action is `INEFFECTIVE`" | The named states were an invented lifecycle. The durable part is not: ISO 9001:2015 §10.2.1 requires the **effectiveness** of a corrective action to be reviewed, so that obligation is restated free of any lifecycle as **QMS-R8**. What remains a project decision is which states exist and what closes a record. |
| **QMS-R2** | "The NCR lifecycle is strict (open → investigate → root-cause → disposition…)" | An invented workflow. 8D, DMAIC and a two-step disposition are all legitimate. |
| **QMS-R3** | "An NCR requires `affectedQty > 0` and a non-empty description" | Field checks. |
| **QMS-R4** | "Quality cost values are non-negative integer cents" | An engineering concern — **ENG-R4**. |

## Project decisions (the questions this department must answer for itself)

- The **AQL level** and **inspection level** — a contract term with the customer or supplier.
  ISO 2859-1 fixes the plan once they are chosen; it does not choose them.
- Whether **normal, tightened or reduced** inspection applies, and the switching rules.
- The **defect classification** (critical / major / minor) and what each obliges.
- The **corrective-action process** — 8D, DMAIC or another — and what closes a finding.
- **Quality targets** (PPM, DPMO, first-pass yield) — set by the customer contract, never by this
  context.

## Inherited rules (referenced, not restated)

- **SCM-R3** — nonconformity records are corrected by further entries, never deleted.
- **SCM-R10** — inspected quantities carry their units.
- **SCM-R14** — cost of quality apportioned across causes sums to the total.
