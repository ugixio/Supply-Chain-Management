---
id: concept-contract-price-escalation
title: "Contract Price Escalation (CPT-0034)"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-concepts-01-procurement }
  - { type: governed-by, target: index-adr }
---
# Contract Price Escalation (CPT-0034)

> How a long-term contract price adjusts to inflation via an index-linked clause, so
> neither party absorbs all commodity/labour swings.

## Formula

    adjusted = base · ( 1 + CPI_change · w_material + PPI_change · w_labour )

| Symbol | Meaning | Unit |
|---|---|---|
| base | contracted base price | currency |
| CPI_change | consumer-price-index change (e.g. 0.03 = 3%) | fraction |
| PPI_change | producer-price-index change | fraction |
| w_material / w_labour | shares attributed to material / labour | fractions, sum to 1.0 |

## Inputs and outputs

- **Output:** the escalated price (currency).
- **Guard (fail fast):** `w_material + w_labour` must equal 1.0 (±0.001) or it raises —
  the split must be exhaustive.

## Assumptions and limits

- **Index choice matters:** material cost is escalated by CPI, labour by PPI in this
  implementation. That pairing is a modelling choice — in practice material is often the
  PPI-linked component; the clause's index assignment must match the contract's actual
  wording. Documented as-implemented; verify against the signed clause.
- **Money-precision:** float today; Decimal under ADR-0019 (P5) — an escalation feeds real
  payable prices, so exactness matters. **Flagged.**
- Symmetric by construction: a negative index change lowers the price (de-escalation),
  unless the contract caps/floors it — caps are not modelled here.
- **Does not apply when:** the contract uses a fixed-price or firm-fixed clause (no
  escalation) or a different index basket.

## Worked example

`base=100, CPI_change=0.03, PPI_change=0.05, w_material=0.6, w_labour=0.4`:

    adjusted = 100 · (1 + 0.03·0.6 + 0.05·0.4)
             = 100 · (1 + 0.018 + 0.020) = 100 · 1.038 = 103.80

A 3.8% escalation — the blended effect of 3% CPI on 60% material and 5% PPI on 40% labour.

## Implementations

- PY: [`adjusted_price`](../../../services/calc/01_procurement/kraljic.py)

> **Coverage gap:** no TypeScript implementation. Contract lifecycle (activate/expire) is
> TS-side (CPT-0035), but the escalation arithmetic is Python-only.

## Governing rules

- **PRC-R8** — a contract carries valid effective/expiry dates and lines; an escalation
  applies within the contract's active window.
- **SCM-R8** — Decimal money (ADR-0019).

## Related

- CPT-0035 Certification & contract validity — the temporal window escalation applies in.
- CPT-0033 TCO — escalated prices feed the ongoing cost of ownership.

## References

- APICS Dictionary 16th Ed. — *price escalation clause*, *economic price adjustment*.
