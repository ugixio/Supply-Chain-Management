---
id: index-concepts-10-risk-management
title: "Concepts — Risk Management (10)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-27
relations:
  - { type: part-of, target: index-concepts }
  - { type: governed-by, target: index-adr }
  - { type: traces-to, target: rule-risk-management }
---
# Concepts — Risk Management (10)

> The concept catalogue for **Risk Management (10)**: what each concept *means*,
> the formula where one is canonical, its assumptions and limits, and the standard or
> regulation that fixes it. Nodes **define**; they hold no threshold, target, weighting or
> mandated method, and they own no code (ADR-0037). Values a project must choose are named
> as project-chosen inputs and left unset.
>
> Departmental law lives in [40-contexts/10-risk-management/rule.md](../../40-contexts/10-risk-management/rule.md).

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
