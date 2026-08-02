---
id: concept-goods-receipt-throughput
title: "Goods-Receipt Throughput (CPT-0161)"
type: concept
owner: orchestrator
status: active
since: 2026-08-01
updated: 2026-08-02
relations:
  - { type: part-of, target: index-concepts-06-warehouse-management }
  - { type: governed-by, target: index-adr }
---
# Goods-Receipt Throughput (CPT-0161)

> How many goods receipts an inbound operation completed in a period. A **flow**: it counts
> events over an interval, so it is meaningless without the interval attached.

## Formula

    GR_throughput = completed_receipts / period

| Symbol | Meaning | Unit |
|---|---|---|
| completed_receipts | receipts reaching the state the operation calls complete | count |
| period | the interval counted over | hours, shifts or days |
| GR_throughput | output | receipts per period |

## Inputs and outputs

- **Inputs:** the set of receipts completed in the period, and the period itself. A receipt is the
  unit of work UN/EDIFACT names **RECADV** (Receiving Advice) and SCOR names *Receive Product*.
- **Output:** a count per period, integer. Never a bare count: `40` is not an answer, `40 per shift`
  is.

## Assumptions and limits

- **This is a flow (MSR-R2), so consecutive periods add** — unlike CPT-0163, where they must not.
- **Choose the granule and keep it.** A receipt, a receipt *line* and a pallet are three different
  denominators, and the same day yields three different numbers. Mixing them across periods is the
  most common way this indicator becomes uncomparable with its own history.
- **A receipt is not "processed" at one obvious moment.** Arrival, unload, count, quality release
  and putaway are distinct states; where the count is taken decides what the number means.
  CPT-0047 measures the *elapsed time* across that same span — read the two together, because
  throughput can rise while dock-to-stock worsens if work is being started and not finished.
- **Does not apply as a productivity measure.** Throughput divided by hours worked is CPT-0045;
  this node counts output, not rate per person, and using it to compare crews of different sizes is
  a misreading.

## Project-chosen inputs

| Input | Why the project must choose it |
|---|---|
| Which state counts as "processed" | It follows from where the operation's accountability sits — quality release and putaway confirmation are different commitments. Nothing external fixes it. |
| The granule: receipt, line or handling unit | Follows from how the operation plans labour. |
| The period and the shift calendar | Follows from the operation's own working pattern. |
| The level that counts as healthy | Follows from inbound volume, dock capacity and the service promise — a published figure is another operation's sample. |

## Worked example

*Illustrative only.* A shift completes 40 receipts covering 310 lines. Reported as a receipt count,
throughput is **40 per shift**; as a line count, **310 per shift**. Both are correct and they are
not interchangeable — which is why the granule travels with the number.

## Governing rules

- **MSR-R2** — a flow; it sums across adjacent periods.
- **SCM-R10** — quantities carry their GS1 unit; a received quantity without its unit is not a
  quantity, and a throughput built on unit-less quantities inherits that defect.
- **SCM-R9** — the period boundaries are ISO 8601 instants in UTC, or two sites in different
  time zones cannot be added.
- **WHS-R5** — what a task reports completed cannot exceed what it was given, which is what makes
  a completion count auditable rather than self-reported.

## Related

- CPT-0047 Dock-to-stock time — the elapsed time over the same span; throughput without it can hide
  work started and not finished.
- CPT-0029 Receipt completeness — whether what arrived matched what was ordered.
- CPT-0162 Return-to-vendor rate — the share of this throughput that came back out.

## References

- UN/EDIFACT RECADV (Receiving Advice) — the message that defines a receipt as a unit of work.
- SCOR Digital Standard (ASCM, 2019) — *Receive Product* process step.
- APICS/ASCM Supply Chain Dictionary, 16th Ed. (2024) — *goods receipt*, *throughput*.
