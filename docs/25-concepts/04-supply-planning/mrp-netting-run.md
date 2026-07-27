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
    planned_receipt_t = lot_sizing(net_req)           (PY: CPT-0142 rules;
                                                       TS: ceil to lot-size multiple)
    planned_release = receipt offset back by lead_time

| Symbol | Meaning | Unit |
|---|---|---|
| gross_req / scheduled_receipt | demand / firm inbound per period | units |
| safety_stock | floor added into netting | units |
| lead_time | release offset | periods (PY) / days (TS) |

## Inputs and outputs

- **PY:** `MRPInput` list (per-SKU horizons, lot rule, costs) →
  `MRPRecord{buckets, total_planned_releases}`.
- **TS:** per-SKU scalars + dated requirement/receipt lists → `MRPRecord` with
  ISO-dated buckets; release date = period − leadTimeDays (calendar subtraction).

## Assumptions and limits

- Uncapacitated and single-item: no material or capacity feasibility — RCCP
  (CPT-0147-family, dept 12) checks the load; MRP output is a *plan*, not a
  promise.
- Safety stock inside the netting means MRP replans to restore the floor —
  standard, but it makes safety stock consume lot-sizing attention every run.
- Multi-level correctness requires processing in low-level-code order
  (CPT-0140) — the PY runner nets per SKU; the orchestration must feed parents
  before components.
- **Release-offset boundary:** an early-horizon requirement can demand a release
  *before period 0* (past-due); PY offsets within the bucket array, TS subtracts
  calendar days — both need the caller to catch releases in the past.
- **Does not apply when:** demand is independent and stationary — (r,Q)/(s,S)
  (CPT-0120) is simpler and self-correcting.

## Worked example

OH 50, SS 20, gross [40, 60, 30], receipts [0, 0, 0], L4L, LT 1:
t1: avail 50, net = 40+20−50 = 10 → receipt 10 (release t0), OH 20.
t2: net = 60+20−20 = 60 → receipt 60 (release t1). t3: net 30 → receipt 30.

## Governing rules

- **SPL-R*** — MRP records lifecycle; planned orders become POs only through the
  PRC approval flow (SCM-R2).

## Related

- CPT-0140 BOM explosion/LLC · CPT-0141 pegging · CPT-0142..0144 lot sizing.

## References

- Orlicky, *Material Requirements Planning* 3rd Ed. (2022), Ch. 3; APICS CPIM 9.0.
