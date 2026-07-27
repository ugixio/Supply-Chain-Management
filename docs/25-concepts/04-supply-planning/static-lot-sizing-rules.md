---
id: concept-static-lot-sizing-rules
title: "Static Lot-Sizing Rules — L4L/EOQ/Fixed-Period/PPB (CPT-0142)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-04-supply-planning }
  - { type: governed-by, target: index-adr }
---
# Static Lot-Sizing Rules — L4L/EOQ/Fixed-Period/PPB (CPT-0142)

> The in-MRP lot-sizing dispatcher: convert per-period net requirements into
> planned order quantities under one of four rules.

## Formula

    L4L:          order_t = net_req_t                    (order exactly, each period)
    EOQ:          place an EOQ-sized order whenever uncovered net req appears;
                  carry the excess forward
    FIXED_PERIOD: every k periods, order the window's summed net reqs
    PPB:          extend the order while cumulative part-periods ≤ EPP = A/h
                  (part-periods = qty × periods held)

| Symbol | Meaning | Unit |
|---|---|---|
| net_req_t | from CPT-0139 netting | units |
| EOQ / k / A / h | policy parameters | units / periods / currency |

## Inputs and outputs

- **Inputs:** net-requirement vector + rule name (`L4L | EOQ | FIXED_PERIOD |
  PPB`) with its parameters (defaults: ordering 100, holding 1).
- **Output:** planned-order vector aligned to periods.

## Assumptions and limits

- Trade-off in one line: L4L minimizes holding and maximizes orders; EOQ the
  reverse; FIXED_PERIOD is calendar-convenient; PPB balances the two costs
  per-order.
- **One EOQ per trigger under-covers a large bucket.** If a single period's net requirement exceeds
  the EOQ, ordering exactly one EOQ leaves the balance short; covering it needs ⌈net/EOQ⌉ multiples.
  Whether the rule rounds up to lot multiples is a design decision that must be stated, because
  both behaviours look reasonable in a table of order quantities.
- Static rules ignore the *future* demand pattern; the dynamic programs
  (CPT-0143/0144) exploit it — use those when demand is lumpy.
- L4L transmits demand noise straight into orders — the bullwhip's friend
  upstream (CPT-0074); EOQ/PPB batching *creates* bullwhip periodicity. No free
  lunch; measure.
- **Does not apply when:** capacity or supplier MOQs bind — apply MOQ/multiple
  constraints after sizing.

## Worked example

Net reqs [10, 0, 60, 30], EOQ 50: t1 order 50 (excess 40); t3: excess 40 < 60 →
order 50 (excess 30); t4: 30 ≤ 30 → covered. Orders [50, 0, 50, 0] — 10 fewer
than L4L's three orders, more holding.

## Governing rules

- **SPL-R5** — netting conserves, whatever the lot rule then does with the net requirement. The
  choice of rule is item policy, changed by decision, and no rule mandates one.

## Related

- CPT-0143 Wagner–Whitin (optimal) · CPT-0144 Silver–Meal/PPB (heuristics) ·
  CPT-0021 EOQ (the quantity source).

## References

- Orlicky (2022), Ch. 6; Silver, Pyke & Peterson §5.4.
