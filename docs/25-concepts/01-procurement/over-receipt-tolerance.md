---
id: concept-over-receipt-tolerance
title: "Goods-Receipt Over-Receipt Tolerance (CPT-0027)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-concepts-01-procurement }
  - { type: governed-by, target: index-adr }
---
# Goods-Receipt Over-Receipt Tolerance (CPT-0027)

> How much more than the ordered quantity a warehouse may receive before the line stops
> posting silently and requires a buyer's approval.

## Formula

    variancePct = (received − ordered) / ordered · 100
    requiresApproval  ⇔  received > ordered · (1 + overTol/100)

| Symbol | Meaning | Unit |
|---|---|---|
| ordered | PO-line ordered quantity (`> 0`) | units |
| received | quantity physically received (`≥ 0`) | units |
| overTol | over-receipt tolerance — **project-chosen**, a term of the supply contract | percent |
| underTol | under-receipt tolerance — **project-chosen**, often not symmetric with overTol | percent |

**This node supplies no tolerance value.** It states the arithmetic a tolerance is applied to; the
number comes from the agreement with the supplier, per supplier or per category.

## Inputs and outputs

- **Inputs:** the ordered and received quantities for one line, plus the tolerances that apply
  to it.
- **Output:** the signed variance, and which side of the band the receipt falls on.
- `ordered > 0` is required — it is the denominator. A receipt against a zero-quantity line is a
  data error, not a 0% variance.
- **Report the variance even when it is inside the band.** A receipt that is always "within
  tolerance" tells you nothing about whether it was 1% or 4.9% over, and the drift is what
  eventually renegotiates the contract.

## Assumptions and limits

- **Over- and under-receipt are separate decisions.** Modelling only the over side leaves a short
  shipment indistinguishable from an exact one, which is the more expensive omission: an unflagged
  shortfall becomes an open commitment nobody is chasing. If the two bands differ, say so
  explicitly rather than reusing one number for both directions.
- **Whether a shortfall closes the line or leaves it open is a project decision**, and it changes
  what the number means: under one policy a 3% short delivery is complete, under another it is 97%
  delivered with a balance outstanding.
- **Does not apply when:** the mismatch is a value/price dispute rather than a quantity one
  — use the three-way match (CPT-0030).

## Worked example

*Illustrative only — the 5% below is an example, not a recommendation.*

`ordered = 100`, `received = 106`, and a contract allowing 5% over:

    upper = 100 · 1.05 = 105
    106 > 105  ⇒  outside the band
    variancePct = (106 − 100)/100 · 100 = +6.00

At `received = 104` the same contract reports inside the band (104 ≤ 105) — and the variance is
still `+4%`, which is worth recording.

## Project-chosen inputs

| Input | Why the project must choose it |
|---|---|
| The over-receipt tolerance | A term of the supply contract, often per supplier or category |
| The under-receipt tolerance | Frequently not symmetric with the over side; state it separately |
| Whether a shortfall closes the line | Under one policy a short delivery is complete; under another the balance stays outstanding |

## Governing rules

- **PRC-R1** — a purchase-order line states a quantity; the tolerance it is judged against is a
  contract term, not part of the order's validity.
- **PRC-R4** — inspection conserves what arrived: `accepted + rejected = received`. A tolerance
  decides whether to accept, never how much arrived.

## Related

- CPT-0029 Receipt completeness — uses received-vs-ordered from the other direction.
- CPT-0030 Three-way match — the quantity leg reuses the same tolerance idea.

## References

- UN/EDIFACT RECADV (Receiving Advice); ISO 9001:2015 §8.6.
- APICS/ASCM Dictionary, 17th Ed. — *receiving tolerance*.
