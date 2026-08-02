---
id: index-concepts-06-warehouse-management
title: "Concepts — Warehouse Management (06)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-08-02
relations:
  - { type: part-of, target: index-concepts }
  - { type: governed-by, target: index-adr }
  - { type: traces-to, target: rule-warehouse-management }
---
# Concepts — Warehouse Management (06)

> The concept catalogue for **Warehouse Management (06)**: what each concept *means*,
> the formula where one is canonical, its assumptions and limits, and the standard or
> regulation that fixes it. Nodes **define**; they hold no threshold, target, weighting or
> mandated method, and they own no code (ADR-0037). Values a project must choose are named
> as project-chosen inputs and left unset.
>
> Departmental law lives in [40-contexts/06-warehouse-management/rule.md](../../40-contexts/06-warehouse-management/rule.md).

## Catalogue

### Picking & slotting

| ID | Concept | Use when |
|---|---|---|
| [CPT-0036](fefo-picking.md) | FEFO picking order | Sequencing lots for expiry-controlled items |
| [CPT-0037](cube-per-order-index.md) | Cube-per-Order Index | Ranking SKUs for forward locations |
| [CPT-0038](abc-velocity-slotting.md) | ABC velocity slotting | Assigning SKUs to zones |
| [CPT-0039](s-shape-routing.md) | S-shape pick routing | Estimating/sequencing picker travel |
| [CPT-0040](wave-optimization.md) | Wave optimization (FFD) | Batching orders into capacity-bound waves |

### Queueing & dock sizing

| ID | Concept | Use when |
|---|---|---|
| [CPT-0041](single-server-queues.md) | M/M/1, M/D/1, M/G/1 queues | Congestion at a single station |
| [CPT-0042](erlang-c-queue.md) | M/M/c Erlang-C queue | Congestion at parallel servers |
| [CPT-0043](dock-door-sizing.md) | Dock door sizing | Choosing the number of doors |

### Space, productivity & yard KPIs

| ID | Concept | Use when |
|---|---|---|
| [CPT-0044](warehouse-space-utilization.md) | Space utilization | Grading building/rack fullness |
| [CPT-0045](warehouse-labour-productivity.md) | Labour productivity (LPH/UPH) | Grading pick/receive rates |
| [CPT-0046](labour-cost-per-line.md) | Labour cost per line | Money-comparable pick output |
| [CPT-0047](dock-to-stock-time.md) | Dock-to-stock time | Inbound velocity |
| [CPT-0048](yard-dwell-and-trailer-turns.md) | Yard dwell & trailer turns | Yard/dock capacity health |
| [CPT-0049](labour-staffing-forecast.md) | Labour staffing forecast | Shift headcount planning |

### Throughput, backlog and event-rate indicators

> **Read the Kind column before the number.** Which aggregations are valid follows from it, and the
> arithmetic is stated once in [30-foundation/measurement/rule.md](../../30-foundation/measurement/rule.md)
> — **MSR-R2** for flow versus level, **MSR-R1** for ratios.

| ID | Concept | Kind | Use when |
|---|---|---|---|
| [CPT-0161](goods-receipt-throughput.md) | Goods-receipt throughput | flow | Grading inbound output per period |
| [CPT-0162](return-to-vendor-discrepancy-rate.md) | Return-to-vendor rate by discrepancy | flow (ratio) | Finding the cause behind inbound rework |
| [CPT-0163](outbound-shipment-backlog.md) | Outbound shipment backlog | **level** | Seeing waiting outbound work, and the wait it implies |
| [CPT-0164](sequence-readiness.md) | Sequence readiness — prepared and pending | flow + **level** | Supplying a line just-in-sequence |
| [CPT-0165](pull-list-completion.md) | Pull-list completion | flow (+ ratio) | Grading material call-off fulfilment |
| [CPT-0166](security-event-rate.md) | Warehouse security-event rate | flow | Reviewing site security incidents (ISO 28000) |

Two of these carry a **vocabulary warning** rather than a standard: *sequence* (CPT-0164) and *pull
list* (CPT-0165) are industry terms defined in the APICS Dictionary, and **no standards body fixes
what one of them contains**. Counts are not comparable between operations, or across a change in how
the unit is cut. The definition travels with the number.
