---
id: concept-expected-annual-loss
title: "Expected Annual Loss (CPT-0072)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-10-risk-management }
  - { type: governed-by, target: index-adr }
---
# Expected Annual Loss (CPT-0072)

> The money-per-year cost of a risk: annualized probability times financial impact —
> the number that lets risks compete with each other and with mitigation budgets.

## Formula

    EAL = P_annual × impact                                  (PY, single risk)
    EAL = Σ_scenarios P_i × PERT_mean(impact%_i) × revenue    (TS, portfolio)
    PERT_mean = (min + 4·mode + max) / 6

| Symbol | Meaning | Unit |
|---|---|---|
| P_annual | annualized event probability | 0–1 (TS input: percent) |
| impact | loss if the event occurs | currency (TS: % of annual revenue) |
| min/mode/max | three-point impact estimate | percent |

## Inputs and outputs

- **PY:** `P ∈ [0,1]` (validated) × impact → float loss.
- **TS:** scenario list (`probabilityPct`, PERT triple of `revenueImpactPct`) ×
  `annualRevenueCents` → summed portfolio EAL in cents. Duration distribution is typed
  but **not used** (scaffold — recorded gap).

## Assumptions and limits

- Expectation hides dispersion: two risks with equal EAL can differ 100× in tail loss —
  EAL ranks and budgets; VaR (CPT-0077) sizes reserves.
- Annualization assumes at most ~one occurrence/year; for high-frequency events use
  frequency × severity instead of probability × impact.
- The PERT mean weights the mode 4× — a deliberately optimistic-robust three-point
  estimate (classic PERT), not a fitted distribution.
- **Does not apply when:** impacts compound across scenarios (correlated disruptions) —
  the additive portfolio EAL understates joint events.

## Worked example

PY: P = 0.15, impact 2,000,000 → EAL = 300,000/year.
TS: scenario 10% probability, impact (2%, 5%, 12%) of 100M¢ revenue →
PERT mean = (2+20+12)/6 = 5.67% → EAL = 0.10 × 0.0567 × 100M = 566,667¢.

## Governing rules

- **SCM-R8** — TS output in integer cents context (Decimal at P5).

## Related

- CPT-0078 Scenario impact analysis — the cents-typed scenario engine.
- CPT-0077 Monte Carlo VaR — the distributional upgrade.

## References

- FAIR (Factor Analysis of Information Risk) — annualized loss expectancy;
  ISO 31000:2018; Malcolm et al. (1959) — PERT.
