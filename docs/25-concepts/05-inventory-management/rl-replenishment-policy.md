---
id: concept-rl-replenishment-policy
title: "RL Replenishment Policy — PPO/DQN (CPT-0122)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-05-inventory-management }
  - { type: governed-by, target: index-adr }
---
# RL Replenishment Policy — PPO/DQN (CPT-0122)

> A reinforcement-learning agent that learns order quantities from a simulated
> inventory environment — the learned alternative to (s,S), benchmarked against it
> before it is allowed to order anything.

## Formula

Markov decision process on `InventoryEnv`: observation (8 features incl. on-hand,
pipeline, demand stats, fill rate) → action = order quantity → reward = −(holding +
stockout + ordering costs). Training: PPO (vectorized, robust default) or DQN
(discrete, sample-efficient), MLP `[128, 64]`, lr 3e-4, budget 200k steps (500k+ for
intermittent/seasonal). Inference: `predict_action` greedy (`deterministic=True`).
Evaluation: `benchmark_vs_classical` runs RL vs an (s,S) baseline over n episodes and
compares mean episode cost/service.

## Inputs and outputs

- **Inputs:** an `InventoryEnv`; algorithm name (PPO/DQN validated); optional network
  and rate; benchmark takes the trained model, (s, S) parameters, episode count.
- **Outputs:** trained stable-baselines3 model; integer order action; benchmark dict
  of comparative episode statistics.

## Assumptions and limits

- **The policy is only as real as the simulator:** demand process, lead times and
  cost coefficients in `InventoryEnv` must be calibrated to the SKU, or the agent
  optimizes a fiction. Benchmark-vs-(s,S) (CPT-0120) is the mandatory gate — if the
  learned policy cannot beat the heuristic *in its own simulator*, it certainly
  won't in production.
- 200k timesteps is a floor for stable behavior; no seed is fixed → run-to-run
  variance (recorded testing caveat).
- PPO's vectorized env factory reuses the same env instance (the `_make_env`
  fallback) — parallelism is nominal, not true independent envs (recorded
  implementation quirk).
- Actions are unconstrained by business rules — SCM-R1/SCM-R2 checks live outside
  the agent; never wire `predict_action` directly to purchase orders.
- **Does not apply when:** demand history is too thin to calibrate a simulator —
  classical policies with conservative parameters win.

## Worked example

Env calibrated to μ = 200/wk, L = 2; PPO 200k steps; benchmark over 10 episodes vs
(s = 493, S = 1435): report mean cost per episode and fill rate for both — adopt RL
only on a consistent cost win at equal-or-better service.

## Governing rules

- OSI-only (ADR-0002): stable-baselines3 MIT; advisory — orders flow through
  governed PO/inventory lifecycles (SCM-R1/R2).

## Related

- CPT-0120 (r,Q)/(s,S) — the baseline and the safety net.

## References

- Schulman et al. (2017) PPO; Mnih et al. (2015) DQN; Gijsbrechts et al. (2022),
  *M&SOM* — deep RL for inventory.
