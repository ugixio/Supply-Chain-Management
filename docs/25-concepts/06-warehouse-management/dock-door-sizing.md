---
id: concept-dock-door-sizing
title: "Dock Door Sizing (CPT-0043)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-06-warehouse-management }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: concept-erlang-c-queue }
---
# Dock Door Sizing (CPT-0043)

> Answers "how many dock doors do we need?" — the smallest door count that keeps both
> utilisation and truck waiting time inside targets, found by iterating the M/M/c model.

## Formula

    μ = 1 / E[S]
    c_min = ⌈ λ / (μ · ρ_target) ⌉
    c* = min { c ≥ c_min : ρ(c) ≤ ρ_target ∧ Wq(c) ≤ Wq_max }   (search window c_min..c_min+20)

| Symbol | Meaning | Unit |
|---|---|---|
| λ | truck arrivals | trucks/hour |
| E[S] | mean unload/load time per truck | hours |
| ρ_target | max acceptable door utilisation (default 0.80) | fraction |
| Wq_max | max acceptable mean wait (default 0.5) | hours |
| c* | recommended door count | doors |

## Inputs and outputs

- **Inputs:** `trucks_per_hour > 0`, `avg_unload_hours > 0`, optional targets, optional
  `service_cv` (declared but the search currently always evaluates M/M/c — see limits).
- **Output:** `DockRecommendation(recommended_doors, utilisation, avg_wait_hours,
  avg_queue_length, rationale)`. If nothing in the window satisfies both targets, the
  best feasible `c_min + 20` is returned with a review-your-assumptions rationale.

## Assumptions and limits

- Inherits every M/M/c assumption (CPT-0042): Poisson walk-in arrivals, one shared
  queue, exponential service.
- **Known gap:** the `service_cv` parameter is accepted and documented (M/G/1-per-door
  approximation intended for cv ≠ 1) but the loop only ever calls `mmc_queue` — cv is
  currently ignored. Recorded for the backlog; treat outputs as cv = 1.
- The 0.80 default utilisation target reflects the queueing knee: beyond it, Wq grows
  hyperbolically in 1/(1−ρ).
- **Does not apply when:** an appointment system levels arrivals (deterministic arrival
  models or simulation fit better).

## Worked example

λ = 8/h, E[S] = 0.4 h → μ = 2.5/h, `c_min = ⌈8/(2.5×0.8)⌉ = 4`.
c = 4 → ρ = 0.8 ≤ 0.8 but Wq ≈ 0.30 h ≤ 0.5 ✓ → **4 doors**, ~18 min mean wait.

## Implementations

- PY: [`dock_door_recommendation`](../../../services/calc/06_warehouse_management/queueing.py)

## Governing rules

- Sizing is advisory; individual appointments follow the DockAppointment state machine
  (WHS-R2).

## Related

- CPT-0042 Erlang-C — the evaluated model.
- CPT-0048 Yard dwell & trailer turns — the KPIs that reveal undersized docks.

## References

- Gross & Harris 4th Ed.; Chen & Askin (2009), *Warehouse Management*.
