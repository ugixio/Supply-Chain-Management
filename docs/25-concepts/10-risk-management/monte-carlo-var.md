---
id: concept-monte-carlo-var
title: "Monte Carlo Value-at-Risk (CPT-0077)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-10-risk-management }
  - { type: governed-by, target: index-adr }
---
# Monte Carlo Value-at-Risk (CPT-0077)

> The tail of the annual loss distribution for a portfolio of supply-chain risks:
> simulate each risk firing (Bernoulli) with a lognormal loss when it does, and read
> the 95th/99th percentile of total loss.

## Formula

Per trial, per risk i: fire ~ Bernoulli(p_i); if fired, loss ~ LogNormal(μ_ln, σ_ln)
with method-of-moments parameters from the arithmetic mean/std:

    σ²_ln = ln(1 + (σ/μ)²) · μ_ln = ln μ − σ²_ln/2
    VaR_q = percentile_q( Σ_i loss_i )       over n_simulations trials

| Symbol | Meaning | Unit |
|---|---|---|
| p_i | annual probability of risk i | 0–1 |
| μ, σ | impact mean / std (arithmetic) | currency |
| n_simulations | trials (default 100,000; seed 42) | count |

## Inputs and outputs

- **Inputs:** three equal-length lists (probabilities, impact means, impact stds);
  optional confidence level (default 0.95).
- **Output:** `{VaR_95, VaR_99, mean_loss, std_loss}`. `VaR_95` is computed at the
  *given* confidence level (the key name is fixed even if 0.90 is passed — recorded
  naming caveat); VaR_99 always at 99%.
- Zero mean/std impacts degrade to a constant loss of e⁰ = 1 unit when fired (guarded
  parameterization) — pass genuine positive impacts.

## Assumptions and limits

- **Independence across risks** — the biggest lie in supply-chain tails: one typhoon
  fires the port, the supplier and the freight-rate risks together. Correlated
  scenarios need copulas or joint scenarios (not implemented); read VaR here as a
  lower bound on tail severity.
- Lognormal severity is right-skewed and positive — reasonable for disruption costs,
  poor for bounded losses (capped contracts).
- At most one occurrence per risk per year (Bernoulli, not Poisson).
- Fixed seed makes runs reproducible; vary the seed for sensitivity.
- **Does not apply when:** you need expected loss only — that is EAL (CPT-0072),
  no simulation required.

## Worked example

Two risks: (p=0.1, μ=1M, σ=0.5M), (p=0.05, μ=5M, σ=3M). Expected loss ≈ 0.35M, but
VaR_95 lands near 2.5M and VaR_99 near 8M — the reserve question EAL cannot answer.

## Implementations

- PY: [`monte_carlo_var`](../../../services/calc/10_risk_management/risk_model.py)

## Governing rules

- Advisory quantification for the risk register (RSK-R*).

## Related

- CPT-0072 EAL — the mean of this distribution.
- CPT-0078 Scenario impact — deterministic per-scenario view in integer cents.

## References

- Jorion, *Value at Risk* 3rd Ed.; ISO 31010 — Monte Carlo technique;
  MIT CTL supply-chain risk quantification research.
