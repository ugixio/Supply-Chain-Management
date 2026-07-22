---
id: concept-western-electric-rules
title: "Western Electric Run Rules (CPT-0058)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-08-quality-management }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: concept-xbar-r-control-limits }
---
# Western Electric Run Rules (CPT-0058)

> Pattern tests that catch out-of-control behavior *before* a point crosses 3σ: shifts,
> trends and stratification show up as improbable runs inside the limits.

## Formula

Standardize each plotted point `z_i = (x_i − CL) / σ`; test the **latest** point:

    Rule 1: |z| > 3                       (1 point beyond 3σ)
    Rule 2: ≥2 of last 3 beyond 2σ, same side
    Rule 3: ≥4 of last 5 beyond 1σ, same side
    Rule 4: 8 consecutive on one side of CL

| Symbol | Meaning | Unit |
|---|---|---|
| CL | centre line | measurement |
| σ | one-sigma band width ((UCL − CL)/3) | measurement |

## Inputs and outputs

- **Inputs:** ordered plotted statistics (e.g. subgroup means), CL, σ > 0.
- **Output:** list of violation records `{rule, description, point_index}` — empty when
  in control. Only the *last* point is judged (streaming usage: call after each new
  subgroup, as the TS `addSubgroup` does).

## Assumptions and limits

- Each rule has a false-alarm probability tuned to roughly match Rule 1 (~0.3%);
  running all four together raises the combined false-alarm rate to ~1 in 91 points
  in-control — expect occasional false signals on long charts.
- Rules assume approximately normal, independent plotted points; autocorrelated
  processes fire Rule 4 constantly (use time-series-aware charts instead).
- Implements the classic WE zone tests 1–4; the extended Nelson trend/oscillation tests
  (6 points trending, 14 alternating…) are not implemented.
- **Does not apply when:** fewer points exist than a rule's window (rules 2–4 silently
  skip until n ≥ 3/5/8).

## Worked example

CL = 10, σ = 0.2; last 3 means: 10.45, 10.05, 10.5 → z = 2.25, 0.25, 2.5 →
two of last three beyond +2σ ⇒ **Rule 2 violation** at the last index (mean shift
suspected) while no single point breaches 3σ.

## Implementations

- PY: [`western_electric_rules`](../../../services/calc/08_quality_management/quality.py)

## Governing rules

- An out-of-control signal obliges investigation before capability is quoted
  (CPT-0053) — process-control discipline per ISO 9001 §8.5.1(c).

## Related

- CPT-0056 X̄-R limits / CPT-0057 p-chart — supply CL and σ.

## References

- Western Electric Co. (1956), *Statistical Quality Control Handbook*.
- Nelson (1984), *JQT* 16(4) — the extended rule set.
