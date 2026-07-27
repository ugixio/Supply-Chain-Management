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

Available 100; requests A=80, B=30, C=10 (Σ=120).
PRO_RATA: A 66.7, B 25, C 8.3. FAIR_SHARE: ratio 100/120 = 0.833 → C's share 8.3 < 10?
No — C requested 10, share 8.33 < 10 ⇒ C not auto-filled; no request below its share ⇒
all get ratio: A 66.7, B 25, C 8.3 (equals pro-rata here). With C=5: C filled 5, then
95/110 ratio for A, B → A 69.1, B 25.9.

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
