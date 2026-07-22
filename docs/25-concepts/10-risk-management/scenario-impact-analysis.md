---
id: concept-scenario-impact-analysis
title: "Disruption Scenario Impact Analysis (CPT-0078)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-10-risk-management }
  - { type: governed-by, target: index-adr }
---
# Disruption Scenario Impact Analysis (CPT-0078)

> Probability-weighted revenue-at-risk per named disruption scenario, in integer
> cents — the register view that names the top risk.

## Formula

Per scenario:

    worst_case = revenue × impact%/100 × duration_days/365
    expected_loss = worst_case × probability
    top_risk = argmax(expected_loss)

| Symbol | Meaning | Unit |
|---|---|---|
| revenue | annual baseline | integer cents |
| impact% | share of daily revenue lost while disrupted | 0–100 |
| duration_days | expected disruption length | days |
| probability | annual occurrence probability | 0–1 |

## Inputs and outputs

- **Inputs:** non-negative integer revenue; non-empty scenario list with
  `{name, probability, revenue_impact_pct, duration_days}` (each validated with named
  errors).
- **Output:** per-scenario `{expected_loss_cents, worst_case_cents}` (int-truncated),
  the portfolio total, and `top_risk`.

## Assumptions and limits

- Linear revenue loss over the disruption window — no recovery ramp, no demand
  backlog recapture (post-disruption catch-up sales would reduce true loss; customer
  defection would raise it).
- Same independence caveat as CPT-0077 when summing the total.
- Integer truncation (`int(...)`) loses sub-cent remainders — accepted for register
  reporting; ADR-0019 Decimal applies at P5.
- **Does not apply when:** a scenario halts *margin* rather than revenue (cost
  disruptions) — model impact on contribution, not turnover.

## Worked example

Revenue 500,000,000¢; scenario "port strike": p = 0.2, impact 40%, 14 days →
worst case = 500M × 0.4 × 14/365 = 7,671,232¢; expected = 1,534,246¢/year.

## Implementations

- PY: [`scenario_impact_analysis`](../../../services/calc/10_risk_management/risk_model.py)

## Governing rules

- **SCM-R8** — integer-cent money; **RSK-R*** — scenarios live in the governed
  register with owners.

## Related

- CPT-0072 EAL — the single-risk primitive.
- CPT-0079/0080 BCP — the mitigation planning the top risk should trigger.

## References

- ISO 31000:2018 §6.4 — risk analysis; ISO 22301 — BIA linkage.
