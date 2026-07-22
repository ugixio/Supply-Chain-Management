---
id: concept-single-server-queues
title: "Single-Server Queues — M/M/1, M/D/1, M/G/1 (CPT-0041)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-06-warehouse-management }
  - { type: governed-by, target: index-adr }
---
# Single-Server Queues — M/M/1, M/D/1, M/G/1 (CPT-0041)

> Predicts congestion at a single processing point (one dock door, one pack station):
> Poisson arrivals at rate λ served at rate μ. M/G/1 is the general case; M/M/1
> (exponential service) and M/D/1 (constant service) are its two classic extremes.

## Formula

Utilisation `ρ = λ/μ` (must be < 1). Pollaczek–Khinchine mean queue length:

    Lq = ρ²(1 + C²ₛ) / (2(1 − ρ))
    M/M/1: C²ₛ = 1 → Lq = ρ²/(1−ρ)   ·   M/D/1: C²ₛ = 0 → Lq = ρ²/(2(1−ρ))
    L = Lq + ρ · Wq = Lq/λ · W = Wq + 1/μ (Little's Law) · P0 = 1 − ρ

| Symbol | Meaning | Unit |
|---|---|---|
| λ, μ | arrival / service rate | events/hour |
| ρ | server utilisation | fraction |
| C²ₛ | squared CV of service time | dimensionless |
| Lq, L | mean number in queue / in system | count |
| Wq, W | mean wait in queue / in system | hours |

## Inputs and outputs

- **Inputs:** `arrival_rate > 0`, `service_rate > 0`; `mg1_queue` additionally
  `service_cv ≥ 0`.
- **Output:** frozen `QueueMetrics(rho, Lq, L, Wq, W, P0, servers=1)`.
- **Guards:** `ρ ≥ 1` raises — the queue grows without bound; the error suggests adding
  capacity.

## Assumptions and limits

- Poisson arrivals (memoryless), steady state, infinite queue room, FIFO discipline.
- Note M/M/1 exposes `L = ρ/(1−ρ)` directly and `W = L/λ`; the M/D/1 and M/G/1
  implementations build `L = Lq + ρ` and `W = Wq + 1/μ` — algebraically identical.
- **Does not apply when:** arrivals are scheduled (dock appointments smooth arrivals —
  the model then overstates waits) or the queue has finite capacity (blocking models).

## Worked example

λ = 4 trucks/h, μ = 5/h → ρ = 0.8. M/M/1: `Lq = 0.64/0.2 = 3.2`, `Wq = 0.8 h`.
Same rates M/D/1: `Lq = 1.6`, `Wq = 0.4 h` — constant service halves the queue.

## Implementations

- PY: [`mm1_queue`](../../../services/calc/06_warehouse_management/queueing.py)
- PY: [`md1_queue`](../../../services/calc/06_warehouse_management/queueing.py)
- PY: [`mg1_queue`](../../../services/calc/06_warehouse_management/queueing.py)

## Governing rules

- Advisory sizing mathematics; no domain invariant attaches until a recommendation is
  executed as dock scheduling (WHS-R2 lifecycle).

## Related

- CPT-0042 M/M/c Erlang-C — the multi-server generalization.
- CPT-0043 Dock door sizing — the applied search over these models.

## References

- Gross & Harris, *Fundamentals of Queueing Theory* 4th Ed.; Kleinrock (1975) Vol. 1.
- Pollaczek (1930) / Khinchine (1932) — the P-K mean-value formula.
