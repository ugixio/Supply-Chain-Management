---
id: concept-rl-replenishment-policy
title: "RL Replenishment Policy — PPO/DQN (CPT-0122)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-29
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
intermittent/seasonal). Inference: greedy (deterministic) action selection.
Evaluation: run the learned policy against an (s,S) baseline over n episodes and compare mean
episode cost and service.

## Inputs and outputs

- **Inputs:** a calibrated inventory simulation environment; the algorithm; the network shape and
  learning rate; for the comparison, the trained policy, the (s,S) parameters and an episode count.
- **Outputs:** a trained policy; an integer order quantity per state; the comparative episode
  statistics.
- **Project-chosen inputs:** the cost coefficients in the reward, the training budget, and the
  margin by which the learned policy must beat the heuristic before it is trusted.

## Assumptions and limits

- **The policy is only as real as the simulator:** the demand process, lead times and cost
  coefficients must be calibrated to the SKU, or the agent optimizes a fiction. Comparison against
  (s,S) (CPT-0120) is the gate that catches it — if the learned policy cannot beat the heuristic
  *in its own simulator*, it certainly will not in production.
- 200k timesteps is a floor for stable behavior; no seed is fixed → run-to-run
  variance (recorded testing caveat).
- A vectorized environment that reuses one instance across workers (the
  fallback) — parallelism is nominal, not true independent envs (recorded
  implementation quirk).
- Actions are unconstrained by business rules — rule checks live outside
  the agent; never wire `predict_action` directly to purchase orders.
- **Does not apply when:** demand history is too thin to calibrate a simulator —
  classical policies with conservative parameters win.

## Worked example

Env calibrated to μ = 200/wk, L = 2; PPO 200k steps; benchmark over 10 episodes vs
(s = 493, S = 1435): report mean cost per episode and fill rate for both — adopt RL
only on a consistent cost win at equal-or-better service.

## Governing rules

- OSI-only (ADR-0002): stable-baselines3 MIT; advisory — orders flow through
  governed PO/inventory lifecycles (the project's own order and inventory rules).

## Related

- CPT-0120 (r,Q)/(s,S) — the baseline and the safety net.

## References

- Schulman et al. (2017) PPO; Mnih et al. (2015) DQN; Gijsbrechts et al. (2022),
  *M&SOM* — deep RL for inventory.
