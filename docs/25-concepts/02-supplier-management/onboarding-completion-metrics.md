---
id: concept-onboarding-completion-metrics
title: "Supplier Onboarding Completion Metrics (CPT-0070)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-02-supplier-management }
  - { type: governed-by, target: index-adr }
---
# Supplier Onboarding Completion Metrics (CPT-0070)

> Progress arithmetic on the onboarding checklist: percent complete, and which
> *required* items still block approval.

## Formula

    completion_pct = |completed items| / |checklist| × 100      (2 dp)
    pending_required = { i ∈ checklist : i.required ∧ ¬i.completed }

| Symbol | Meaning | Unit |
|---|---|---|
| checklist | onboarding items (certs, banking, compliance docs…) | items |
| required | item blocks approval when incomplete | boolean |

## Inputs and outputs

- **Inputs:** the onboarding aggregate.
- **Outputs:** percentage (empty checklist → 100); the blocking item list (empty means
  approvable).

## Assumptions and limits

- All items weigh equally in the percentage — a missing UFLPA clearance and a missing
  logo file both cost the same points; **gate on `pending_required`, report
  `completion_pct`** — the percentage is progress cosmetics, the required list is law.
- Empty checklist grades 100: templates must guarantee a non-empty checklist or an
  unconfigured supplier auto-passes (recorded caveat; the SUP lifecycle guards
  approval separately).
- **Does not apply when:** items have dependencies (the flat list can show 90% while
  the critical path has barely started).

## Worked example

10 items, 8 complete → 80.0%; the 2 open items are `required` (ISO 28000 cert, bank
verification) → approval blocked despite 80%.

## Implementations

- TS: [`completionPct`](../../../packages/domain/src/02-supplier-management/domain/SupplierOnboarding.ts)
- TS: [`pendingRequiredItems`](../../../packages/domain/src/02-supplier-management/domain/SupplierOnboarding.ts)

## Governing rules

- **SUP-R*** — onboarding approval requires all required items (the state machine
  enforces it; this node only names the arithmetic).
- **SCM-R6** — XUAR clearance is one such required item.

## Related

- CPT-0060 Scorecard — begins once onboarding completes.

## References

- ISO 28000:2022 — supply chain security certification as an onboarding control.
