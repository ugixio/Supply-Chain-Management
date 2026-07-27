---
id: concept-mrp-netting-run
title: "MRP Netting Run (CPT-0139)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-04-supply-planning }
  - { type: governed-by, target: index-adr }
---
# MRP Netting Run (CPT-0139)

> The core MRP arithmetic per period: net gross requirements against projected
> stock, size the planned order, and offset its release by the lead time.

## Formula

Per period t (Orlicky's logic):

    available_t = projected_on_hand_{t−1} + scheduled_receipt_t
    net_req_t = max(0, gross_req_t + safety_stock − available_t)
    planned_receipt_t = lot_sizing(net_req)           lot-sizing rule is project-chosen
                                                      (see CPT-0142)
    planned_release = receipt offset back by lead_time

| Symbol | Meaning | Unit |
|---|---|---|
| gross_req / scheduled_receipt | demand / firm inbound per period | units |
| safety_stock | floor added into netting | units |
| lead_time | release offset | **the same bucket the plan is timed in** — periods or days, not both |

## Inputs and outputs

- **Inputs:** per-SKU horizons, the lot-sizing rule and the costs →
  `MRPRecord{buckets, total_planned_releases}`.
- **Output:** per-SKU planned orders with their release dates, plus
  ISO-dated buckets; release date = period − leadTimeDays (calendar subtraction).

## Assumptions and limits

- Uncapacitated and single-item: no material or capacity feasibility — RCCP
  (CPT-0147-family, dept 12) checks the load; MRP output is a *plan*, not a
  promise.
- Safety stock inside the netting means MRP replans to restore the floor —
  standard, but it makes safety stock consume lot-sizing attention every run.
- **Multi-level correctness requires low-level-code order** (CPT-0140). A netting routine that
  works one SKU at a time is correct only if something upstream feeds it parents before their
  components — otherwise a component is netted against demand its parent has not yet generated,
  and the plan is quietly short.
- **A release can fall before the horizon starts.** Offsetting an early requirement by its lead
  time produces a past-due release, and whether it is offset in period buckets or in calendar days
  the caller must still surface it: a release scheduled in the past is not a plan, it is a
  shortage that already happened.
- **Does not apply when:** demand is independent and stationary — (r,Q)/(s,S)
  (CPT-0120) is simpler and self-correcting.

## Worked example

OH 50, SS 20, gross [40, 60, 30], receipts [0, 0, 0], L4L, LT 1:
t1: avail 50, net = 40+20−50 = 10 → receipt 10 (release t0), OH 20.
t2: net = 60+20−20 = 60 → receipt 60 (release t1). t3: net 30 → receipt 30.

## Project-chosen inputs

| Input | Why the project must choose it |
|---|---|
| Whether safety stock is netted | Including it makes MRP replan to restore the floor every run — standard, but it changes what a shortage means |
| The planning horizon and bucket size | Weekly buckets hide within-week timing; a horizon shorter than cumulative lead time cannot plan the long-lead items |
| What happens to a past-due release | Expedite, re-plan, or refuse — the arithmetic produces it either way |

## Governing rules

- **SPL-R5** — netting **conserves**: `net = gross − available − scheduled receipts`, which is the
  identity this whole run rests on. **SPL-R1** — the BOM is acyclic, so the explosion terminates.
  A planned order becomes a purchase order only through the project's own approval flow — MRP
  output is a plan, and **PRC-R1** applies the moment it becomes an order.

## Related

- CPT-0140 BOM explosion/LLC · CPT-0141 pegging · CPT-0142..0144 lot sizing.

## References

- Orlicky, *Material Requirements Planning* 3rd Ed. (2022), Ch. 3; APICS CPIM 9.0.
