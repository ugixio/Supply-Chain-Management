---
id: rule-supplier-development
title: "Rules — Supplier Development (SDV-R*)"
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
# Rules — Supplier Development

> **A rule lives here only if something outside this repository fixes it** — a standards body, a
> regulator, or an arithmetic identity (ADR-0037). Anything an organization can reasonably choose
> is a **project decision** and is listed as such, never as an invariant. IDs are append-only
> (family `SDV`); a retired ID stays listed so old citations resolve. Cross-department rules
> (`SCM-R*`) are inherited, referenced never restated.

## Invariants (externally fixed — NEVER violated)

- **SDV-R4:** A due-diligence claim about a supplier records **the evidence it rests on and the
  date of that evidence**. An unevidenced assertion of compliance is the specific thing the
  disclosure regimes were written to stop. *Source:* CSDDD Art. 16/23 documentation and reporting
  duties.
- **SDV-R5:** **Absence of evidence is not evidence of compliance.** A supplier that has submitted
  nothing scores as *unknown*, never as average or acceptable. A composite that floors an
  unevidenced supplier at a mid-range value converts silence into adequacy — which is how
  due-diligence scoring fails in practice.
- **SDV-R6:** **EUDR** — for an in-scope commodity, the operator holds geolocation of the plots of
  production and a risk assessment, and files a due-diligence statement. Country risk
  classification is **read from the Commission's published benchmark**, which is revised: a
  hardcoded country list is wrong the moment the benchmark changes. *Source:* Regulation (EU)
  2023/1115, with application deferred to 30 Dec 2026.

## Retired rules

> Retired because they stated **project policy or an implementation detail** of code this
> repository no longer contains (ADR-0037). Listed permanently so citations resolve.

| ID | Was | Why retired |
|---|---|---|
| **SDV-R1** | "An ESG score is within [0, 100]" | A scale convention on an invented field. |
| **SDV-R2** | "A cascade record requires `tier1SupplierId` and provenance fields" | The durable duty — evidence and dating — is **SDV-R4**; the field names were implementation. |
| **SDV-R3** | "An EUDR assessment requires a `supplierId`, an `assessmentDate` and…" | Restated as **SDV-R6** against the regulation's actual obligations rather than one implementation's required fields. |

## Project decisions (the questions this department must answer for itself)

- The **development programme**: which suppliers are developed rather than replaced, and what
  investment each tier justifies.
- **Scoring criteria and weights** for supplier capability and ESG, and what an *unknown* resolves
  to in a portfolio view (SDV-R5 forbids only treating it as adequate).
- **Audit depth and frequency**, and how far beyond tier 1 due diligence reaches — CSDDD requires
  risk-based prioritization; the risk model is the project's.
- **Emission factors** and their source, and the unit every reported figure is stated in.
- **Corrective-action timelines** and what constitutes exit.

## Inherited rules (referenced, not restated)

- **SCM-R6** — UFLPA: the forced-labour presumption reaches supplier qualification.
- **SCM-R7** — due-diligence documentation retained at least five years.
- **SCM-R3** — assessments are superseded, never erased.
