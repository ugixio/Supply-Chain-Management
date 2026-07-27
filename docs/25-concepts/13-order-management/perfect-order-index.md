---
id: concept-perfect-order-index
title: "Perfect Order Index & Gap Analysis (CPT-0084)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-13-order-management }
  - { type: governed-by, target: index-adr }
---
# Perfect Order Index & Gap Analysis (CPT-0084)

> SCOR's four-factor multiplicative estimate of flawless fulfillment — on-time ×
> in-full × damage-free × correct-documentation — plus the gap analysis that names the
> factor to fix first.

## Formula

    POI = (on_time/n) × (in_full/n) × (damage_free/n) × (correct_docs/n)
    gap = target − POI       (target default 0.95)
    required_worst = target / (POI / worst_factor_rate)

| Symbol | Meaning | Unit |
|---|---|---|
| n | total orders in period | count |
| factor counts | orders passing each factor | count ≤ n |

## Inputs and outputs

- **Inputs:** the four factor counts (validated 0 ≤ count ≤ n) and n > 0.
- **Outputs:** `PerfectOrderResult` (POI + factor rates, 6 dp; `perfect_orders` is the
  rounded POI×n estimate); gap analysis `{gap, on_target, worst_factor,
  required_worst_factor_rate, factor_rates}`.

## Assumptions and limits

- **Independence assumption:** multiplying rates estimates the intersection as if
  factors fail independently. Real failures cluster, so POI typically *understates*
  the true AND-counted rate (CPT-0083) — useful as a conservative bound and for factor
  attribution, not as the audited POR.
- `perfect_orders` is an estimate, not a count — never reconcile it against order
  records.
- Gap analysis holds other factors constant when computing the required worst-factor
  rate — a first-order prioritization, recompute after each improvement.
- **Does not apply when:** per-order component flags exist — count the intersection
  directly (CPT-0083) and keep POI for factor diagnostics.

## Worked example

n = 500: on-time 470 (94%), in-full 480 (96%), damage-free 495 (99%), docs 490 (98%)
→ POI = 0.94×0.96×0.99×0.98 = **0.8755**. Worst factor on-time; to hit 0.95 target it
would need 0.95/(0.8755/0.94) = 1.02 — impossible alone ⇒ multiple factors must move.

## Governing rules

- ADR-0029 — these metrics live in dept 13 (the old `07_order_management` dir is
  dissolved).

## Related

- CPT-0083 Perfect order — the exact intersection on real orders.
- CPT-0092 SCOR agility — the same SCOR family, flexibility side.

## References

- SCOR-DS RL.1.1 and RL.2.* components; Aberdeen Group (2006) — 95% world-class.
