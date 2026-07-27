---
id: concept-budget-variance-analysis
title: "Budget Variance Analysis (CPT-0108)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-11-finance-controlling }
  - { type: governed-by, target: index-adr }
---
# Budget Variance Analysis (CPT-0108)

> Actual vs budget per cost category with favorability status and the finance-policy
> explanation trigger.

## Formula

    variance = actual − budget          (negative = favorable, cost view)
    variance_pct = variance / budget × 100
    status: |pct| < 2% ON_BUDGET · variance < 0 FAVORABLE · else UNFAVORABLE
    requires_explanation ⇔ |variance_pct| > 10%

| Symbol | Meaning | Unit |
|---|---|---|
| budget / actual | per-category spend | integer cents |

## Inputs and outputs

- **Inputs:** two dicts keyed by category (union of keys is analyzed; a key missing
  on one side reads 0).
- **Output:** per-category rows, a total row, and a summary (favorable/unfavorable/
  on-budget counts + categories needing explanation). Zero budget with actual spend →
- **A zero budget with actual spend has no percentage variance**, and that is the case most worth
  seeing: an unbudgeted category. If the percentage is undefined and the status derives from the
  percentage, the category escapes the report entirely. Handle the absolute variance separately so
  spend outside the budget cannot hide behind an undefined ratio.

## Assumptions and limits

- Cost-view polarity (under-spend favorable); revenue budgets need the sign flipped.
- The band within which a variance counts as on-budget, and the level above which it must be
  explained, are **project-chosen** finance policy — not accounting
  law — governed values, changed by decision.
- Percentage-only triggers miss large-absolute/low-percentage misses on huge
  categories; pair with an absolute-cents threshold for materiality (not
  implemented).
- **Does not apply when:** the budget was re-forecast mid-period — compare against
  the *current* approved version and say which.

## Worked example

Freight: budget 120,000¢, actual 138,000¢ → +15% UNFAVORABLE, explanation required.
Packaging: 50,000 → 49,200 → −1.6% ON_BUDGET.

## Project-chosen inputs

| Input | Why the project must choose it |
|---|---|
| The on-budget band | The width below which a variance is not investigated is finance policy |
| The level requiring explanation | An escalation threshold, not an accounting rule |
| How an unbudgeted category is handled | It has no percentage variance, and that is the case most worth seeing |

## Governing rules

- **SCM-R3** — a variance record and the explanation attached to it are corrected by a further
  entry, never rewritten. **SCM-R14** — the variance is exact money.

## Related

- CPT-0107 SC cost % revenue — the top-down companion.

## References

- Bragg, *Controller's Handbook* 3rd Ed. (Wiley); standard costing practice.
