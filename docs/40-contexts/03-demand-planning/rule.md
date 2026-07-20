---
id: rule-demand-planning
title: "Rules — Demand Planning (DMD-R*)"
type: rule
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-contexts }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: rule-scm-core }
---
# Rules — Demand Planning

> Invariants enforced in `src/departments/03-demand-planning/`. Know-how lives in the
> allowlisted homes (`README.md`, `IMPLEMENTATION.md`,
> `.claude/skills/demand-planning/`). IDs append-only (family `DMD`). Inherited `SCM-R*`
> referenced, never restated.

## Invariants (NEVER violated — each verifiable by test)

- **DMD-R1:** A demand plan cannot be submitted with no lines, and an `APPROVED` demand
  plan is never deleted — it is superseded (`DemandPlan.ts`).
- **DMD-R2:** A demand-plan line's `confidencePct` is within [0, 100].
- **DMD-R3:** The demand-plan status machine is strict (draft → submit → approve →
  supersede); each transition is valid only from its allowed prior status.
- **DMD-R4:** A demand-sensing run's forecast values, `mape` and `mae` are all
  non-negative; a failed run carries a non-empty `errorMessage` (`DemandSensingRun.ts`).

> **DMD-R5..R8 are extracted from the department's business-context document**
> (`IMPLEMENTATION.md` §9, ADR-0016). They are **not yet enforced in code** — no guard
> implements them today. They are stated here so they become testable; wiring them is
> backlog U18.

- **DMD-R5:** A SKU enters statistical accuracy reporting only with
  `months_of_history >= 3` **and** `lifecycle_status NOT IN ('NPI','EOL')`. Strategic NPIs
  are reported separately by attach-rate method, never mixed into baseline accuracy.
- **DMD-R6:** APE is **undefined** when the actual is zero — it is recorded as `NULL`,
  never as zero and never as infinity. MAPE is computed over non-zero periods only, the
  count of excluded periods is reported alongside, and intermittent SKUs are scored with
  WMAPE instead (CPT-0009).
- **DMD-R7:** Every consensus override is classified against the statistical baseline:
  `|consensus − actual| < |statistical − actual|` ⇒ `override_improved`, otherwise
  `override_worsened`; exact ties are neutral. An override is never accepted without this
  classification being recorded (feeds FVA, CPT-0024).
- **DMD-R8:** Actual safety stock is flagged against the Method-4 value (CPT-0015):
  `< 0.8 × ss_method4` ⇒ `under-stocked`; `> 1.5 × ss_method4` ⇒ `over-stocked`.
  Deliberate strategic buffers outside the band must carry an annotation, never pass
  silently.

## Mandatory validations

- Period fields validate `YYYY-MM` format before use.
- **Service level → z consistency:** the `z` stored against a safety-stock record must be
  recomputable from its service level. See CPT-0003 — the business-context document
  specifies `scipy.stats.norm.ppf`, while both implementations use interpolated tables
  and disagree with each other. **This validation currently cannot pass against either
  implementation**; resolving which definition is canonical is backlog U15.

## Anti-states (the system must never allow)

- A submitted demand plan with zero lines (DMD-R1).
- A deleted APPROVED demand plan (DMD-R1 — supersede instead).
- A negative forecast, MAPE or MAE (DMD-R4).
- An APE of zero or infinity recorded for a zero-actual period (DMD-R6).
- A consensus override persisted without its value classification (DMD-R7).

## Inherited rules (referenced, not restated)

- **SCM-R9** — dates ISO 8601.
- **SCM-R11** — SKU codes are immutable; lifecycle via status flags.
