---
id: index-concepts-10-risk-management
title: "Concepts — Risk Management (10)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts }
  - { type: governed-by, target: index-adr }
  - { type: traces-to, target: rule-risk-management }
---
# Concepts — Risk Management (10)

> The calculation catalogue for `packages/domain/src/10-risk-management/` and
> `services/calc/10_risk_management/`. Coverage is `enforced`. Law lives in
> [40-contexts/10-risk-management/rule.md](../../40-contexts/10-risk-management/rule.md)
> (`RSK-R*`); these nodes carry meaning and mathematics only.

## What counts as a public calculation symbol

The BCP/drill aggregates are **state machines** (create → start → complete/fail;
findings add/resolve; test results append) — their transitions are excluded, as is
`createRiskItem` (a constructor that stamps the CPT-0071 mapping). Everything else —
matrices, concentration, bullwhip, loss models, continuity scoring and anomaly
detection — is catalogued.

## Catalogue

### Risk assessment & quantification

| ID | Concept | Use when |
|---|---|---|
| [CPT-0071](risk-matrix-5x5.md) | 5×5 risk matrix | Triaging register entries |
| [CPT-0072](expected-annual-loss.md) | Expected Annual Loss | Ranking/budgeting risks |
| [CPT-0077](monte-carlo-var.md) | Monte Carlo VaR | Sizing tail reserves |
| [CPT-0078](scenario-impact-analysis.md) | Scenario impact analysis | Named-scenario revenue at risk |

### Structural exposure

| ID | Concept | Use when |
|---|---|---|
| [CPT-0073](herfindahl-hirschman-index.md) | HHI concentration | Detecting supply concentration |
| [CPT-0074](bullwhip-ratio.md) | Bullwhip ratio & severity | Measuring demand amplification |
| [CPT-0075](bullwhip-theoretical-lower-bound.md) | Bullwhip lower bound | Separating structural amplification |
| [CPT-0076](bullwhip-decomposition.md) | Bullwhip decomposition | Attributing amplification causes |

### Continuity & monitoring

| ID | Concept | Use when |
|---|---|---|
| [CPT-0079](bcp-objectives-validation.md) | RTO/RPO/MTPD validation | Checking BCP coherence |
| [CPT-0080](bcp-readiness-score.md) | BCP readiness score | Grading drill evidence |
| [CPT-0081](lstm-autoencoder-anomaly-detection.md) | LSTM autoencoder anomaly detection | Signal-drift early warning |

## Not concepts (excluded from G10)

> Aggregate lifecycle / state-machine transitions — governed by `rule.md` (RSK-R*), not
> calculations. Listed so G10 coverage is exact.

`start` · `complete` · `fail` · `addFinding` · `resolveFinding` · `createBCP` ·
`addTestResult` · `createRiskItem`

## Divergences surfaced (for the backlog)

- **Risk-level thresholds (CPT-0071)** — PY (LOW ≤ 8 … CRITICAL ≥ 20) vs TS
  (MEDIUM ≥ 4, HIGH ≥ 8, CRITICAL ≥ 15): the same probability×impact classifies up to
  two levels apart. Owner decision required; TS currently stamps domain records.
- **HHI input units (CPT-0073)** — PY fractions (normalized) vs TS percents; PY-style
  input into TS silently yields ≈ 0.
- **Bullwhip degenerate (CPT-0074)** — zero demand variance: PY raises, TS returns
  `{ratio: 0, NONE}`; severity band edge differs (1.1 vs 1.2).
- **`bullwhip_ratio` defined twice** in `risk_model.py` (float version shadowed by the
  rich-dict version) — cleanup candidate.
- **TS `expectedAnnualLoss`** types a PERT duration distribution it never uses
  (CPT-0072 scaffold gap).
