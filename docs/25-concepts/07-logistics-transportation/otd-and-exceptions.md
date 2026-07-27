---
id: concept-otd-and-exceptions
title: "On-Time Delivery Rate & Exception Flag (CPT-0126)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-07-logistics-transportation }
  - { type: governed-by, target: index-adr }
---
# On-Time Delivery Rate & Exception Flag (CPT-0126)

> The shipment-level delivery KPI: was each shipment delivered by the requested
> date, what share were, and which tracking events signal trouble.

## Formula

    on_time(shipment) ⇔ actual_delivery_date ≤ requested_delivery_date
                        (null actual → null: not yet delivered, not counted)
    OTD% = on_time_count / total_shipments × 100     (0 shipments → 0.0)
    is_exception(event) ⇔ milestone = EXCEPTION

| Symbol | Meaning | Unit |
|---|---|---|
| requested_delivery_date | the customer-request basis | ISO date |

## Inputs and outputs

- **TS `isOnTimeDelivery`:** tri-state boolean (`null` = in transit) — undelivered
  shipments are excluded rather than failed, the opposite of CPT-0082's OTIF
  treatment (recorded divergence: shipment-level OTD is measured on completions;
  order-level OTIF punishes pending).
- **PY `otd_rate`:** pre-counted numerator/denominator → percentage (4 dp).

## Assumptions and limits

- Basis is the **requested** date; contractual OTD is often against the *promised*
  date — the CPT-0082/CPT-0089 two-bases note applies here identically.
- The acceptable level, and how heavily OTD weighs against cost and damage in a carrier
  scorecard, are commercial decisions — the delivery contract sets them, not this node
  (CPT-0131).
- Same-day granularity — no delivery-window (AM/PM slot) precision.
- EXCEPTION is a milestone value on the tracking event stream; counting exceptions
  per shipment is upstream aggregation, not modelled here.
- **Does not apply when:** measuring order completeness — OTD says *when*, not
  *how much* (that is OTIF/fill, CPT-0082/0088).

## Worked example

184 of 195 delivered shipments on time → `94.36%` — just under the 95% bar; the 11
misses join the exception review queue.

## Governing rules

- **LOG-R*** — shipment lifecycle stamps the dates; SCM-R9 ISO dates.

## Related

- CPT-0131 Carrier performance — consumes OTD as one input among several; the weighting is
  project-chosen.
- CPT-0082 OTIF — the order-level composite.

## References

- SCOR RL.2.1 (delivery to commit date); CLAUDE.md KPI table.
