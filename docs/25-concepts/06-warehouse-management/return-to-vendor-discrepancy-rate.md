---
id: concept-return-to-vendor-discrepancy-rate
title: "Return-to-Vendor Rate by Receiving Discrepancy (CPT-0162)"
type: concept
owner: orchestrator
status: active
since: 2026-08-01
updated: 2026-08-02
relations:
  - { type: part-of, target: index-concepts-06-warehouse-management }
  - { type: governed-by, target: index-adr }
---
# Return-to-Vendor Rate by Receiving Discrepancy (CPT-0162)

> How much of what arrived went back out because receiving found it wrong. A **flow**, and the one
> inbound indicator that points at a cause rather than a symptom.

## Formula

    RTV_discrepancy_rate = returned_for_discrepancy / received × 100

| Symbol | Meaning | Unit |
|---|---|---|
| returned_for_discrepancy | receipts or lines returned because receiving recorded a discrepancy | count |
| received | receipts or lines received in the same period, same granule | count |
| RTV_discrepancy_rate | output | percentage |

## Inputs and outputs

- **Inputs:** the returned set with its **discrepancy reason**, and the received set over the same
  period and the same granule.
- **Output:** a percentage, plus — and this is the part that makes it actionable — **the breakdown by
  reason**. A single number tells an operation it has a problem; the breakdown tells it whose.

## Assumptions and limits

- **The reason taxonomy is the whole value.** UN/EDIFACT **RECADV** carries the condition and
  discrepancy codes for a receipt, and ISO 9001:2015 §8.7 requires nonconforming output to be
  identified and controlled. That fixes *that* a reason must be recorded, not what the code set is.
  Quantity short, quantity over, wrong item, damaged, expired, documentation missing and
  specification mismatch are different problems with different owners; collapsed into one rate they
  are unactionable.
- **A discrepancy is not a return.** Many discrepancies are accepted — over-receipt inside the
  contract's tolerance (CPT-0027), a short shipment closed as complete. Only the ones that leave
  count here, so this rate is always lower than the discrepancy rate and the two are not
  substitutes.
- **Returns lag receipts, so MSR-R1's same-population requirement bites here.** A receipt in one
  week can be returned the next; dividing this week's returns by this week's receipts compares two
  populations. Either cohort the returns to their receipt period, or say plainly that the figure is a
  period ratio and not a cohort rate.
- **Does not apply to customer returns.** Those are reverse logistics with their own economics
  (CPT-0091); the cause, the counterparty and the remedy all differ.

## Project-chosen inputs

| Input | Why the project must choose it |
|---|---|
| The discrepancy reason code set | RECADV supplies codes; which ones an operation distinguishes, and how it maps its own, follows from what it intends to act on. |
| Which discrepancies trigger a return rather than acceptance | The supply contract decides — tolerance, remedy, and who pays freight back. |
| Cohort or period ratio | Follows from whether the question is supplier quality (cohort) or current workload (period). |
| The level that counts as acceptable | The supply agreement and the cost of the alternative. Nothing external fixes it. |

## Worked example

*Illustrative only.* 310 lines received; 12 returned — 5 damaged, 4 wrong item, 3 expired. Rate
**3.9%**. The number that changes behaviour is not 3.9%: it is that 4 wrong-item returns point at a
supplier's picking and 3 expired point at its stock rotation, which are two different conversations.

## Governing rules

- **MSR-R1** — the rate aggregates from pooled counts, over one population and one period.
- **SCM-R3** — a return is a reversing movement, never an erasure of the receipt; the audit trail
  keeps both or the rate cannot be reconstructed.
- **SCM-R4** — the physical return carries its accounting consequence.
- **SCM-R10** — returned quantities carry their GS1 unit, as received quantities do.

## Related

- CPT-0161 Goods-receipt throughput — the denominator.
- CPT-0029 Receipt completeness — whether what arrived matched the order.
- CPT-0027 Over-receipt tolerance — the contract term that decides acceptance versus return.
- CPT-0091 Returns economics — customer-side reverse cost, a different population.

## References

- UN/EDIFACT RECADV (Receiving Advice) — receipt condition and discrepancy codes.
- ISO 9001:2015 §8.7 — control of nonconforming outputs.
- APICS/ASCM Supply Chain Dictionary, 16th Ed. (2024) — *return to vendor*, *discrepancy*.
