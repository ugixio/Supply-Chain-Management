---
id: concept-document-retention-deadlines
title: "Compliance Document Retention Deadlines (CPT-0096)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-09-compliance-regulatory }
  - { type: governed-by, target: index-adr }
---
# Compliance Document Retention Deadlines (CPT-0096)

> How long due-diligence evidence must be kept, per regulation, and how many days
> remain — the arithmetic behind SCM-R7.

## Formula

    retention years: CSDDD / EUDR / LkSG → 5 · UK_MSA → 3 · other → 2 (internal floor)
    deadline = assessment_date + years          (Feb 29 → Mar 1 rollover)
    days_remaining = expiry − today             (negative = already expired)

| Symbol | Meaning | Unit |
|---|---|---|
| assessment_date | date the assessment/evidence was created | ISO 8601 |
| regulation | CSDDD, EUDR, LKSG, UK_MSA, … (case-insensitive) | enum-ish |

## Inputs and outputs

- `retention_date(str, str) → str` — calendar-year addition (leap-day safe);
- `retention_expiry_date(date) → date` — CSDDD-specific, **day-count method**
  (5×365 + counted leap days);
- `days_to_retention_expiry(date, today?) → int`.

## Assumptions and limits

- **Two dating methods coexist (recorded divergence):** `retention_date` adds calendar
  years; `retention_expiry_date` adds counted days — they disagree by ±1 day around
  leap boundaries. Since Art. 23 CSDDD says *at least* 5 years, the later date is
  always safe; unify on calendar-year + safety margin.
- These are *minimums* — litigation holds, tax law (often 6–10 years) or member-state
  gold-plating can extend; the "other → 2 years" default is internal policy, not law.
- Retention runs from the assessment date, not from contract end — long programs need
  per-document deadlines, not per-supplier ones.
- **Does not apply when:** personal data is involved — GDPR minimization can *cap*
  retention; the longer-keeps-wins logic must reconcile with deletion duties.

## Worked example

CSDDD assessment 2024-01-15 → retention to **2029-01-15**; on 2026-07-22 →
915 days remaining.

## Implementations

- PY: [`retention_date`](../../../services/calc/09_compliance_regulatory/compliance.py)
- PY: [`retention_expiry_date`](../../../services/calc/09_compliance_regulatory/compliance.py)
- PY: [`days_to_retention_expiry`](../../../services/calc/09_compliance_regulatory/compliance.py)

## Governing rules

- **SCM-R7** — CSDDD retention ≥ 5 years is the codified invariant this computes.

## Related

- CPT-0093 CSDDD scope — the trigger for the 5-year duty.

## References

- CSDDD Art. 23 (as adopted 2024/1760); EUDR 2023/1115 Art. 9; LkSG §10;
  UK Modern Slavery Act 2015 §54 guidance.
