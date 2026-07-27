---
id: rule-supplier-management
title: "Rules — Supplier Management (SUP-R*)"
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
# Rules — Supplier Management

> **A rule lives here only if something outside this repository fixes it** — a standards body, a
> regulator, or an arithmetic identity (ADR-0037). Anything an organization can reasonably choose
> is a **project decision** and is listed as such, never as an invariant. IDs are append-only
> (family `SUP`); a retired ID stays listed so old citations resolve. Cross-department rules
> (`SCM-R*`) are inherited, referenced never restated.

## Invariants (externally fixed — NEVER violated)

- **SUP-R5:** An evaluation of an external provider records **what was assessed, against which
  criteria, and when**. An assessment whose basis is not recorded cannot be reviewed or repeated.
  *Source:* ISO 9001:2015 §8.4.1 (evaluation, selection, monitoring and re-evaluation, with
  retained documented information); the criteria themselves are the project's.

## Retired rules

> Retired because they stated **project policy or an implementation detail** of code this
> repository no longer contains (ADR-0037). Listed permanently so citations resolve.

| ID | Was | Why retired |
|---|---|---|
| **SUP-R1** | "An audit cannot be closed while any `MAJOR_NC` finding is open" | The finding severities and the closure gate are an audit programme's design. The principle — a nonconformity is closed on evidence, not on elapsed time — belongs to the quality department's own definition of its process. |
| **SUP-R2** | "The supplier-audit lifecycle is status-guarded — start, add-finding, close…" | An invented lifecycle. The durable duty it gestured at — that an evaluation records its basis — is stated freshly as **SUP-R5** rather than by reusing this ID, since an ID is never redefined. |
| **SUP-R3** | "Completing an onboarding checklist item requires a `documentRef` and a date" | A sound practice, and a design choice: what evidence an onboarding step demands is the project's. |
| **SUP-R4** | "Onboarding approval is valid only from `APPROVAL_PENDING`" | A guard over invented states. |

## Project decisions (the questions this department must answer for itself)

- The **evaluation criteria** for suppliers, their **weights** and any **rating bands**
  (see CPT-0060/CPT-0061 — the context defines the structure and refuses to supply values).
- The **audit programme**: frequency, scope, finding severities, and what closes a finding.
- The **onboarding steps** and the evidence each requires.
- **Re-evaluation cadence** — ISO 9001 requires re-evaluation; how often is the project's.

## Inherited rules (referenced, not restated)

- **SCM-R3** — scorecards and audit records are corrected, not deleted.
- **SCM-R6** — UFLPA applies to supplier qualification, not only to shipments.
- **SCM-R7** — due-diligence documentation is retained at least five years (CSDDD Art. 23).
