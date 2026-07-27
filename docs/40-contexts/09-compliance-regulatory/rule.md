---
id: rule-compliance-regulatory
title: "Rules — Compliance & Regulatory (CMP-R*)"
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
# Rules — Compliance & Regulatory

> **A rule lives here only if something outside this repository fixes it** — a standards body, a
> regulator, or an arithmetic identity (ADR-0037). Anything an organization can reasonably choose
> is a **project decision** and is listed as such, never as an invariant. IDs are append-only
> (family `CMP`); a retired ID stays listed so old citations resolve. Cross-department rules
> (`SCM-R*`) are inherited, referenced never restated.

## Invariants (externally fixed — NEVER violated)

- **CMP-R2:** Every compliance record carries its **provenance** — what was assessed, the
  evidence relied on, who assessed it, and when. Compliance is demonstrated to a regulator by the
  record, so an assertion without its basis has no value at the moment it is needed. *Source:* the
  documentation and reporting duties of CSDDD Art. 16/23, UFLPA's clear-and-convincing evidence
  standard, and REACH's duty to supply information on request.
- **CMP-R3:** **REACH** — an article containing a Candidate List substance above **0.1% w/w**
  triggers duties: information to recipients down the supply chain (Art. 33), and notification to
  ECHA where the tonnage threshold is met (Art. 7(2)). *Source:* Regulation (EC) 1907/2006. The
  concentration is fixed by the regulation; nothing about it is configurable.
- **CMP-R4:** A compliance **exception has an expiry**. A waiver without an end date is a
  permanent removal of the obligation, which no regulator grants and no auditor accepts.
  *An identity of what an exception is.*

## Retired rules

> Retired because they stated **project policy or an implementation detail** of code this
> repository no longer contains (ADR-0037). Listed permanently so citations resolve.

| ID | Was | Why retired |
|---|---|---|
| **CMP-R1** | "A compliance exception requires a `validUntil` date in the future" | The durable half — that an exception expires — is restated as **CMP-R4**; the field name and the future-date check were implementation. |

## Project decisions (the questions this department must answer for itself)

- **Which regimes apply**, which follows from the goods, the markets and the entity's own size —
  and the size thresholds are set by the regulations, not chosen (see CPT-0093, CPT-0100).
- The **evidence standard** the organization holds itself to, above the legal minimum.
- **Retention beyond the statutory minimum** (SCM-R7 fixes the floor at five years for CSDDD).
- **Screening frequency** and how far down the supply chain due diligence reaches — CSDDD requires
  risk-based prioritization; the risk model is the project's.
- Whether an exception process exists at all, and who may grant one.

## Inherited rules (referenced, not restated)

- **SCM-R6** — UFLPA: the Xinjiang forced-labour presumption.
- **SCM-R7** — due-diligence documentation retained at least five years.
- **SCM-R3** — a compliance record is never destroyed; superseding it leaves the original readable.

> **Regulatory content has the shortest half-life in this repository.** CSDDD scope was rewritten
> by Directive (EU) 2026/470, CBAM by the 2025 Omnibus, and EUDR's application date moved. See the
> drift notes in [25-concepts/09-compliance-regulatory/_index.md](../../25-concepts/09-compliance-regulatory/_index.md).
