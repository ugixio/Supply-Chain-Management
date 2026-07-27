---
id: concept-fair-share-allocation
title: "Fair-Share Order Allocation (CPT-0090)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-13-order-management }
  - { type: governed-by, target: index-adr }
---
# Fair-Share Order Allocation (CPT-0090)

> Rationing scarce stock across competing orders under four policies: pro-rata,
> priority, water-filling fair-share, and first-come-first-served.

## Formula

    PRO_RATA:   alloc_i = requested_i / Σ requested × available
    PRIORITY:   fill ascending priority number (1 = highest), ties by input order
    FAIR_SHARE: water-filling — equalize fill rate; requests below the equal share
                are fully filled and the freed supply re-spreads over the rest
    FCFS:       fill in input order until exhausted
    Invariants: Σ alloc ≤ available · alloc_i ≤ requested_i

| Symbol | Meaning | Unit |
|---|---|---|
| available | quantity to distribute (≥ 0) | units |
| requested_i > 0 | demand per order | units |
| priority | 1 = highest (default 1) | ordinal |

## Inputs and outputs

- **Inputs:** available, demand dicts `{order_id, requested_qty, priority?}`, method
  name (unknown method raises).
- **Output:** input records + `allocated_qty` + `fill_rate_pct`, order preserved.
  Edge cases: full supply ⇒ everyone filled; `available ≤ 0` ⇒ all zero.

## Assumptions and limits

- **PRO_RATA vs FAIR_SHARE differ:** pro-rata gives everyone the same *percentage*
  including huge orders; water-filling first satisfies small orders fully, equalizing
  the *residual* fill of the rest — small-customer-friendly.
- Fractional allocations (floats) — case-pack rounding is the caller's problem and can
  break the Σ ≤ available invariant if done naively (round down, then redistribute).
- Priority ties resolve by input order — the caller controls the queue discipline.
- **Does not apply when:** allocation must respect contractual minimums or service
  tiers — model those as pre-carved reservations before rationing the rest.

## Worked example

Available 100; requests A = 80, B = 30, C = 10 (Σ = 120), so the fill ratio is 100/120 = 0.833.

**Pro-rata** gives every order the same fraction: A 66.7, B 25, C 8.3.

**Small-order protection** first fills any request that is *already* below its pro-rata share, then
re-rates the rest. Here C asks for 10 and its share is 8.3 — it is not below, so nothing changes and
the result equals pro-rata. Had C asked for **5**, it would be filled in full, leaving 95 across
requests of 110 → A 69.1, B 25.9.

Both allocations conserve the 100 available (ORD-R5); they differ only in who absorbs the shortfall.
Note the fractional shares: units are indivisible, so the rounding remainder needs a stated owner.

## Project-chosen inputs

| Input | Why the project must choose it |
|---|---|
| The fairness definition | Pro-rata, priority-ordered and minimum-viable-quantity are each fair by a different standard |
| The minimum useful allocation | A share too small to ship helps nobody and still consumes stock |
| Rounding direction on the shares | The total must still conserve (ORD-R5), so the remainder needs an owner |

## Governing rules

- **ORD-R5** — an allocation **conserves** the available stock: the sum of what is allocated equals
  what there was to allocate, so no unit is created or lost by rounding the shares independently
  (the same sum-preservation requirement as SCM-R14, applied to units rather than money).
- **Which allocation policy applies is a project decision** — pro-rata, priority-ordered, or a
  minimum-viable-quantity rule are all legitimate, and each is fair by a different definition.

## Related

- CPT-0088 Fill rate — the outcome metric of the rationing choice.

## References

- Silver, Pyke & Peterson — rationing; APICS CPIM 9.0 — allocation;
  Chopra & Meindl, Ch. 11.
