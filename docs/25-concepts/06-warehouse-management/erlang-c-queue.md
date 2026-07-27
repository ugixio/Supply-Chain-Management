---
id: concept-erlang-c-queue
title: "M/M/c Erlang-C Queue (CPT-0042)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-06-warehouse-management }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: concept-single-server-queues }
---
# M/M/c Erlang-C Queue (CPT-0042)

> Congestion at a bank of c parallel servers (dock doors, pack stations) sharing one
> queue: Poisson arrivals, exponential service, and the Erlang-C probability that an
> arrival must wait.

## Formula

Offered load `a = λ/μ` (Erlangs), utilisation `ρ = a/c` (must be < 1):

    P0 = 1 / ( Σₙ₌₀^{c−1} aⁿ/n!  +  a^c / (c!(1−ρ)) )
    C(c,a) = a^c / (c!(1−ρ)) · P0          (Erlang-C wait probability)
    Lq = C·ρ/(1−ρ) · L = Lq + a · Wq = Lq/λ · W = Wq + 1/μ

| Symbol | Meaning | Unit |
|---|---|---|
| λ, μ | arrival rate / per-server service rate | events/hour |
| c | parallel servers | count |
| a | offered load | Erlangs |
| ρ | per-server utilisation | fraction |
| C(c,a) | probability an arrival waits | probability |

## Inputs and outputs

- **Inputs:** `arrival_rate > 0`, `service_rate > 0`, `c ≥ 1`.
- **Output:** `QueueMetrics(rho, Lq, L, Wq, W, P0, servers=c)`.
- **Guards:** `ρ ≥ 1` raises with the minimum stable server count.

## Assumptions and limits

- Single shared queue with FIFO discipline — not one queue per door; identical servers;
  steady state.
- Exponential service. For low-variability unloading, M/M/c *overstates* waits — the
  pooled-door recommendation stays conservative (see CPT-0043 for the cv ≠ 1 route).
- Factorials overflow for very large c; fine at warehouse scale (c ≤ ~30).
- **Does not apply when:** arrivals are appointment-scheduled, or jockeying/dedicated
  lanes break the single-queue assumption.

## Worked example

λ = 8 trucks/h, μ = 2.5/h, c = 4 → a = 3.2, ρ = 0.8.
P0 = 1/(1 + 3.2 + 5.12 + 5.4613 + 21.8453) ≈ 0.02729.
C = 21.8453 × 0.02729 ≈ 0.5962 → `Lq = 0.5962×0.8/0.2 ≈ 2.38` trucks,
`Wq ≈ 0.298 h ≈ 18 min`.

## Governing rules

- Advisory; executed door assignments follow the dock-appointment lifecycle (WHS-R2).

## Related

- CPT-0041 Single-server queues — the c = 1 special cases.
- CPT-0043 Dock door sizing — searches c using this model.

## References

- Erlang, A.K. (1917) — delay formula; Gross & Harris 4th Ed., Ch. 2.
- Kleinrock (1975), *Queueing Systems* Vol. 1.
