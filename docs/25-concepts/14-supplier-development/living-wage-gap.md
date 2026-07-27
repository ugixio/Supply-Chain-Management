---
id: concept-living-wage-gap
title: "Living Wage Gap (CPT-0136)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-14-supplier-development }
  - { type: governed-by, target: index-adr }
---
# Living Wage Gap (CPT-0136)

> How far a supplier's actual average wage falls below the local living-wage
> standard — positive gap = workers earn less than a decent-living threshold.

## Formula

    gap% = (living_wage_standard − actual_avg_wage) / living_wage_standard × 100

| Symbol | Meaning | Unit |
|---|---|---|
| living_wage_standard | local benchmark (Anker methodology / Fair Wage Network) | currency/period |
| actual_avg_wage | supplier's average paid wage, same basis | currency/period |

## Inputs and outputs

- **Inputs:** standard > 0 (validated); wage on the same period/currency basis.
- **Output:** signed percentage — 0 or negative = met/exceeded; target 0%.

## Assumptions and limits

- **Averages hide the tail:** an average above the standard can coexist with many
  workers below it — the Anker methodology assesses *lowest-paid* worker
  categories; use percentile wages where data allows.
- The standard is location- and family-composition-specific (Anker: local food,
  housing, essentials + margin) and differs from *minimum* wage — a legal wage can
  still gap 30%.
- Wage basis must match (gross vs net, incl./excl. in-kind and bonuses — Anker
  counts guaranteed cash + fair in-kind).
- Feeds the S pillar bonus (CPT-0132, `pay_living_wage`) and CSDDD/LkSG living-wage
  duties (adequate wage duty).
- **Does not apply when:** piece-rate work without hour tracking — convert to
  effective hourly first.

## Worked example

Standard 2,400/month, actual average 2,050 → `gap = (2400−2050)/2400 = 14.6%` —
remediation plan territory; re-measure at the lowest job grade before declaring
closure.

## Governing rules

- **SDV-R*** — remediation tracked on the record; CSDDD adequate-wage duty
  (dept 09 scope).

## Related

- CPT-0132 S pillar — the boolean it informs.

## References

- Anker & Anker, *Living Wages Around the World* (2017); Global Living Wage
  Coalition; GRI 202.
