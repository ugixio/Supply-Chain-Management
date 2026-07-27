---
id: concept-littles-law
title: "Little's Law — WIP, Throughput, Cycle Time (CPT-0159)"
type: concept
owner: orchestrator
status: active
since: 2026-07-27
updated: 2026-07-27
relations:
  - { type: part-of, target: index-concepts-00-platform }
  - { type: governed-by, target: index-adr }
---
# Little's Law — WIP, Throughput, Cycle Time (CPT-0159)

> The identity tying the three flow quantities together. **It is not a model and not a heuristic** —
> given its conditions it is arithmetically true, which makes it the one statement in this group that
> cannot be argued with.

## Formula

    L = λ · W

    work in progress = throughput × cycle time

| Symbol | Meaning | Unit |
|---|---|---|
| L | average work in progress over the window | items |
| λ | average throughput — items completed per unit time | items/time |
| W | average cycle time — time an item spends in the system | time |

Any two determine the third. Rearranged, the useful forms are `W = L / λ` (how long work takes,
given how much is in flight) and `L = λ · W`.

## Inputs and outputs

- **Inputs:** two of the three quantities, **averaged over the same window**, with items entering
  and leaving the same defined system boundary.
- **Output:** the third quantity.
- **The boundary is part of the measurement.** "In progress" across a pipeline and "in progress" in
  code review are different systems with different `L`; mixing them yields nonsense that still looks
  arithmetic.

## Assumptions and limits

- **Conditions for the equality:** averages over the **same** period, a roughly **stationary** system
  (arrivals ≈ departures, no unbounded queue growth), and items counted consistently. Under those
  conditions it is exact for *any* arrival distribution — no exponential or independence assumption.
- **A growing backlog breaks it.** If work enters faster than it leaves, `L` is rising and no average
  describes the window: the *stationarity* premise fails, and applying it anyway understates cycle
  time.
- **It is an average relationship, not a per-item prediction.** It cannot say how long a *particular*
  change will take — for that, the cycle-time distribution (CPT-0156) is the honest answer.
- **The operational consequence is the whole point:** at fixed throughput, cycle time is proportional
  to WIP. Faster delivery comes from raising throughput (hard) or **lowering WIP** (available
  immediately). Starting more work in parallel cannot make items finish sooner — it makes them
  slower, arithmetically.
- **Does not apply when:** items are not comparable units of work. Counting a one-line fix and a
  quarter-long migration as one item each keeps the arithmetic valid and the interpretation useless.

## Project-chosen inputs

| Input | Why the project must choose it |
|---|---|
| The system boundary | Where an item enters and leaves; the identity is only true within one boundary |
| The unit of work | Change, ticket, story or deployment — consistency matters more than the choice |
| The averaging window | Long enough that arrivals and departures roughly balance |

## Worked example

*Illustrative.* 10 changes completed per week, 25 in flight on average → `W = 25/10 = **2.5 weeks**`.

Halving WIP to 12 gives `W = 1.2 weeks` at the *same* throughput: nothing about the team changed, the
queue got shorter. This is why WIP limits precede process improvement rather than follow it.

## Governing rules

- No rule fixes a WIP limit, a throughput or a cycle time: those are the project's operating
  decisions. **The identity itself is not a decision** — it holds whatever a project chooses, which
  is why it belongs in this catalogue (ADR-0037).

## Related

- CPT-0156 Lead time for changes — the `W` term, reported as a distribution.
- CPT-0155 Deployment frequency — a throughput measure, though of deployments rather than items.
- CPT-0160 Flow efficiency — decomposes `W` into working and waiting time.

## References

- Little, J.D.C. (1961) *A proof for the queuing formula L = λW*, Operations Research 9(3).
- Little, J.D.C. & Graves, S.C. (2008) *Little's Law*, in **Building Intuition** — the conditions
  under which the identity holds, stated precisely.
- Reinertsen, D., *The Principles of Product Development Flow* (2009) — the WIP consequence.
