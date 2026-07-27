---
id: concept-cash-to-cash-cycle
title: "Cash-to-Cash Cycle & Classification (CPT-0104)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-11-finance-controlling }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: concept-dio-dso-dpo }
---
# Cash-to-Cash Cycle & Classification (CPT-0104)

> Days between paying suppliers and collecting from customers — the working-capital
> clock of the supply chain. Negative C2C means suppliers finance the business.

## Formula

    C2C = DIO + DSO − DPO      (days)
    PY bands:  <0 EXCELLENT · ≤30 GOOD · ≤60 AVERAGE · >60 POOR
    TS bands:  <0 EXCELLENT · <20 GOOD · <45 AVERAGE · ≥45 POOR

TS `calculateWorkingCapitalMetrics` derives the full snapshot from period balances:
DSO, DIO (via inventory turnover = COGS/inventory), DPO, C2C, turnover, gross margin%.

| Symbol | Meaning | Unit |
|---|---|---|
| DIO / DSO / DPO | component day metrics (CPT-0105) | days |

## Inputs and outputs

- **Inputs:** the three component durations, or the balances they are computed from.
- **Output:** the cycle in days. It can legitimately be **negative** — that means suppliers are
  financing the operation, which is a business model rather than an error.
- **A zero denominator is a real case, not an edge case.** A period with no cost of sales or no
  revenue has no meaningful days-outstanding figure. Whether that reports as zero, as undefined,
  or refuses to compute is a project decision — but reporting zero is the one option that reads
  as excellent performance, so it is the one to choose deliberately rather than by default.

## Assumptions and limits

- Components must share the **same period and basis** (all annualized on 365, AR
  against revenue, inventory/AP against COGS) — mixing quarterly AR with annual COGS
  breaks the sum.
- **Band divergence (recorded):** a 25-day cycle is GOOD in Python, AVERAGE in
  TypeScript. Owner alignment pending (U15b-class).
- C2C rewards stretching DPO — beyond contractual terms that is supplier financing
  with relationship and CSDDD-adjacent costs; read with the supplier lens
  (CPT-0067 ROWC).
- **Does not apply when:** comparing across business models (retail vs make-to-order)
  without segment benchmarks.

## Worked example

DIO 58, DSO 32, DPO 45 → **C2C = 45 days**. Whether 45 days is good is not a property of the
identity: it depends entirely on the industry and the business model, and a negative cycle —
normal for some retailers — means suppliers are financing the operation.

## Governing rules

- **FIN-R*** — snapshots are period records (soft-delete, SCM-R3).

## Related

- CPT-0105 DIO/DSO/DPO — the components.
- CPT-0067 ROWC — return on the same working capital.

## References

- Stewart (1995) — C2C benchmarking; Chopra & Meindl, Ch. 7; SCOR AM.2.2.
