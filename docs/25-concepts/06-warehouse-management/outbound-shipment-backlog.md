---
id: concept-outbound-shipment-backlog
title: "Outbound Shipment Backlog (CPT-0163)"
type: concept
owner: orchestrator
status: active
since: 2026-08-01
updated: 2026-08-01
relations:
  - { type: part-of, target: index-concepts-06-warehouse-management }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: concept-littles-law }
---
# Outbound Shipment Backlog (CPT-0163)

> How much outbound work is waiting. A **level**, not a flow — and that distinction decides which
> arithmetic on it is valid and which is nonsense.

## Formula

The backlog is read, not computed: it is the count of shipments in a waiting state at an instant.
What *is* an identity is its relationship to throughput and waiting time — **Little's Law**
(CPT-0159):

    L = λ · W        ⇒        W = L / λ

| Symbol | Meaning | Unit |
|---|---|---|
| L | backlog: shipments waiting at the instant of reading | count |
| λ | throughput: shipments completed per period | count/period |
| W | the wait a shipment joining now can expect | period |

## Inputs and outputs

- **Inputs:** the count of shipments in the waiting state, at an instant; and for the derived wait,
  the completion throughput over a comparable period.
- **Output:** a level, integer, **stamped with the instant it was read**. A backlog without its
  timestamp is not a measurement.

## Assumptions and limits

- **A level must never be summed over time, and this is arithmetic, not preference.** Reading a
  backlog of 40 six times in a minute and adding them gives 240, which is not a quantity that
  exists. Valid aggregations over an interval are the **last** value, the maximum, the minimum, or
  the time-weighted average — never the sum, and never the count of readings. A telemetry rollup
  built for flows will silently produce the 240.
- **`W = L / λ` needs a system in steady state.** During a surge, arrivals exceed completions and
  the ratio understates the wait — exactly when someone is looking at it. Read it as an estimate
  that degrades precisely under load (CPT-0159 states the condition).
- **"Waiting" must be one defined state.** Released-not-picked, picked-not-packed and
  packed-not-loaded are three backlogs. Summing them counts a shipment up to three times.
- **Does not apply as a workload forecast.** The backlog says what is here now; what is coming is
  the order profile, and a backlog trend is a lagging signal of it.

## Project-chosen inputs

| Input | Why the project must choose it |
|---|---|
| Which state counts as "pending" | Follows from where the operation's constraint actually is; it is not self-evident and it changes the number severalfold. |
| The reading cadence | Follows from how fast the operation can react — a level sampled slower than its own change rate hides the peak. |
| The granule: shipment, order, line or handling unit | Follows from how labour is planned. |
| The level that triggers action | Follows from dock and labour capacity, and from the service promise. Nothing external fixes it. |

## Worked example

*Illustrative only.* 40 shipments pending; completions run 20 per hour. Then `W = 40 / 20 = 2 hours`
for a shipment joining the queue now. If the same 40 is read every ten minutes and a dashboard sums
the six readings in the hour, it displays **240** — a backlog six times reality, with nothing
failing. That is the failure mode this node exists to prevent.

## Governing rules

- **SCM-R9** — the reading instant is an ISO 8601 UTC timestamp; a level without its instant cannot
  be ordered, compared or aggregated correctly.

## Related

- CPT-0159 Little's Law — the identity that turns this level into an expected wait.
- CPT-0164 Sequence readiness — the same level-versus-flow pairing, applied to sequences.
- CPT-0048 Yard dwell and trailer turns — the level's consequence outside the building.
- CPT-0040 Wave optimization — how the waiting work is batched into releases.

## References

- Little, J. D. C. (1961). "A Proof for the Queuing Formula L = λW." *Operations Research* 9(3).
- APICS/ASCM Supply Chain Dictionary, 16th Ed. (2024) — *backlog*, *work in process*.
