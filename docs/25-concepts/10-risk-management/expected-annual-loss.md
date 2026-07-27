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

    EAL = P_annual × impact                          single risk
    EAL = Σᵢ Pᵢ × impactᵢ                            a portfolio of independent risks

Where the impact itself is uncertain, a three-point estimate stands in for it:

    PERT_mean = (min + 4·mode + max) / 6

| Symbol | Meaning | Unit |
|---|---|---|
| P_annual | annualized probability of the event | fraction, 0–1 |
| impact | loss if the event occurs | currency — or a fraction of revenue, stated explicitly |
| min/mode/max | three-point impact estimate | percent |

## Inputs and outputs

- **Inputs:** a probability in `[0, 1]` and an impact. Every scenario's impact must be in the
  **same** unit — all in currency, or all as a fraction of the same revenue base. Mixing the two
  is the error this node exists to prevent.
- **Output:** an expected loss per year, in that unit.
- **Independent scenarios add.** Correlated ones do not: two risks that share a root cause
  (one port, one supplier, one region) cannot simply be summed, and doing so understates the
  joint exposure.

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

A single scenario at probability 0.15 with an impact of 2,000,000 gives an EAL of
300,000 per year. With a three-point impact estimate — say 2%, 5% and 12% of revenue →
PERT mean = (2+20+12)/6 = 5.67% → EAL = 0.10 × 0.0567 × 100M = 566,667¢.

## Governing rules

- **SCM-R8** — TS output in integer cents context (Decimal at P5).

## Related

- CPT-0078 Scenario impact analysis — the cents-typed scenario engine.
- CPT-0077 Monte Carlo VaR — the distributional upgrade.

## References

- FAIR (Factor Analysis of Information Risk) — annualized loss expectancy;
  ISO 31000:2018; Malcolm et al. (1959) — PERT.
