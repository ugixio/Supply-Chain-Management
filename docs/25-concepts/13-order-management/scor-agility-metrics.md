---
id: concept-scor-agility-metrics
title: "SCOR Agility Metrics — AG.1.1/1.2/1.3 (CPT-0092)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-13-order-management }
  - { type: governed-by, target: index-adr }
---
# SCOR Agility Metrics — AG.1.1/1.2/1.3 (CPT-0092)

> How fast the chain flexes: days to sustain a +20% volume ramp (upside flexibility),
> the penalty-free volume reduction at 30 days notice (downside adaptability), and the
> mitigation-netted value at risk.

## Formula

    AG.1.1  upside:   uplift% = (max − base)/base × 100, achievable within a stated
                      response window (the window itself is project-chosen)
    AG.1.2  downside: reduction% = (base − reduced)/base × 100;
                      penalty_free ⇔ unrecoverable_cost = 0
    AG.1.3  VaR:      expected_loss = P × revenue_at_risk
                      net_var = max(0, expected_loss − mitigation_cost)

A **negative** net figure means the mitigation costs more than the exposure it removes, which is a
finding worth acting on. Any band that turns `net_var` into a recommendation is the project's risk
appetite, not part of the metric (RSK-R6: expectation is not exposure).

| Symbol | Meaning | Unit |
|---|---|---|
| base / max / reduced volume | planned vs achievable volumes | units/period |
| response_days / notice_days | ramp time / notice given | days |
| revenue_at_risk / mitigation_cost | money | integer cents |

## Inputs and outputs

- **Outputs:** AG.1.1 `{upside_flexibility_days, achievable_uplift_pct, benchmark_met,
  gap_days}`; AG.1.2 `{reduction_pct, penalty_free, unrecoverable_cost_cents}`;
  AG.1.3 `{expected_loss_cents, net_var_cents, recommendation}` (probability
  validated ∈ [0,1]).

## Assumptions and limits

- SCOR defines upside flexibility against a **sustainable, unplanned 20%** increase —
  the uplift% output verifies the 20% is actually achievable; a fast ramp to +10%
  does not qualify.
- Baseline volumes must be > 0 (division; not guarded — recorded caveat).
- AG.1.3 is the SCOR-flavored EAL (CPT-0072) netted for mitigation spend; its
  recommendation thresholds (2×, 5%) are heuristics, not standardsed values.
- **Does not apply when:** flex is constrained by a single supplier — measure at the
  constraint, not the average.

## Worked example

Base 10,000/mo, max in 30 days 12,300 (+23%), achieved in 24 days → AG.1.1 met,
gap 0. Downside: reduced to 7,000 penalty-free → 30%. VaR: P 0.15 × 40M¢ = 6M¢
expected; mitigation 2.5M¢ → net 3.5M¢, 6M > 5M ⇒ INCREASE_MITIGATION.

## Governing rules

- ADR-0029 notes the fine split of these agility/VaR functions to dept 10 remains a
  pending backlog item (U11) — they are catalogued where they live today.

## Related

- CPT-0072 EAL / CPT-0077 Monte Carlo VaR — the risk-department quantifications.
- CPT-0084 POI — SCOR reliability side.

## References

- SCOR Digital Standard (ASCM, 2019) — AG.1.1/1.2/1.3.
