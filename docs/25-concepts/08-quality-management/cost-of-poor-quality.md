---
id: concept-cost-of-poor-quality
title: "Cost of Poor Quality — COPQ (CPT-0054)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-08-quality-management }
  - { type: governed-by, target: index-adr }
---
# Cost of Poor Quality — COPQ (CPT-0054)

> What bad quality costs, in Juran's four categories: prevention, appraisal, internal
> failure (scrap/rework) and external failure (customer-facing). Benchmark 5–30% of
> revenue. What level is tolerable is a business decision, not a property of the measure.

## Formula

    COPQ = prevention + appraisal + internal_failure + external_failure
    copq_pct_revenue = COPQ / revenue × 100

Per-NCR mapping (`copq_by_category` / TS `totalCopqCents`):

    internal_failure = scrap_cost + rework_cost
    external_failure = return_freight_cost

| Symbol | Meaning | Unit |
|---|---|---|
| prevention / appraisal | planning, training / inspection, testing | currency, in minor units |
| scrap, rework, return_freight | per-NCR failure costs | integer cents |
| revenue | period revenue | currency, in minor units |

## Inputs and outputs

- **Inputs:** category costs ≥ 0; `copq_by_category` takes NCR records (integer cents,
  validated non-negative) + `revenue_cents: int`; zero revenue → 0% (no division).
- **Outputs:** category totals, grand total, % of revenue (4 dp), and per-NCR breakdown.
- TS `totalCopqCents` is the NCR-level sum: scrap + rework + return freight.

## Assumptions and limits

- Strictly, prevention + appraisal are **Cost of Quality** (the price of conformance);
  many practitioners restrict COPQ to failure costs only. This implementation follows
  Juran's *total* CoQ aggregation — compare like with like across periods.
- Captured NCR costs understate true external failure (lost goodwill, expediting,
  warranty tails are invisible to the NCR record).
- **Money divergence (recorded):** `copq` takes float currency amounts; `copq_by_category`
  integer cents. ADR-0019 Decimal migration covers both.
- **Does not apply when:** revenue is zero/pre-revenue programs — report absolute cents.

## Worked example

NCRs: scrap 120,000¢ + rework 45,000¢ + freight 30,000¢; prevention 20,000¢, appraisal
60,000¢ → COPQ = 275,000¢. Revenue 50,000,000¢ → **0.55%** of revenue.

## Governing rules

- **SCM-R8** — money as integer cents/Decimal; **SCM-R3** — NCR cost records soft-delete
  only.

## Related

- CPT-0059 NCR/SCAR cycle metrics — the records whose costs feed this.
- CPT-0051 PPM — the physical defect rate behind the money.

## References

- Juran & Godfrey, *Juran's Quality Handbook* 5th Ed. §8; ASQ BoK — Cost of Quality.
- Feigenbaum (1956) — original quality-costs framing.
