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

- **PY:** the three components (already computed) → C2C float; classification of the
  result.
- **TS:** raw period-end balances in cents → `WorkingCapitalSnapshot`; zero
  denominators produce 0 (PY components raise instead — recorded divergence).

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

DIO 58, DSO 32, DPO 45 → **C2C = 45 days** → AVERAGE (PY) / POOR (TS band edge —
the divergence in action).

## Governing rules

- **FIN-R*** — snapshots are period records (soft-delete, SCM-R3).

## Related

- CPT-0105 DIO/DSO/DPO — the components.
- CPT-0067 ROWC — return on the same working capital.

## References

- Stewart (1995) — C2C benchmarking; Chopra & Meindl, Ch. 7; SCOR AM.2.2.
