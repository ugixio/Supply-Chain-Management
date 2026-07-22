---
id: index-concepts-11-finance-controlling
title: "Concepts — Finance & Controlling (11)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts }
  - { type: governed-by, target: index-adr }
  - { type: traces-to, target: rule-finance-controlling }
---
# Concepts — Finance & Controlling (11)

> The calculation catalogue for `packages/domain/src/11-finance-controlling/` and
> `services/calc/11_finance_controlling/`. Coverage is `enforced`. Law lives in
> [40-contexts/11-finance-controlling/rule.md](../../40-contexts/11-finance-controlling/rule.md)
> (`FIN-R*`); these nodes carry meaning and mathematics only.

## What counts as a public calculation symbol

`createInvoice` is a lifecycle constructor and `completionPct` (PeriodClose) is the
close-checklist progress ratio — same arithmetic as CPT-0070, attached to the
period-close state machine — both excluded. Matching, working-capital, costing,
FX and investment mathematics are catalogued.

## Catalogue

### AP & working capital

| ID | Concept | Use when |
|---|---|---|
| [CPT-0103](ap-three-way-match.md) | AP three-way match | Releasing supplier invoices |
| [CPT-0104](cash-to-cash-cycle.md) | Cash-to-cash cycle | Working-capital clock |
| [CPT-0105](dio-dso-dpo.md) | DIO / DSO / DPO | The C2C components |
| [CPT-0106](dynamic-discounting-ear.md) | Dynamic discounting EAR | Early-payment decisions |

### Costing & control

| ID | Concept | Use when |
|---|---|---|
| [CPT-0107](sc-cost-as-pct-revenue.md) | SC cost as % revenue | Top-down cost health |
| [CPT-0108](budget-variance-analysis.md) | Budget variance analysis | Actual-vs-plan control |
| [CPT-0109](cost-to-serve.md) | Cost-to-serve | Customer/SKU profitability |
| [CPT-0111](landed-cost-and-allocation.md) | Landed cost & allocation (IAS 2) | True import unit cost |

### Treasury & investment

| ID | Concept | Use when |
|---|---|---|
| [CPT-0110](fx-revaluation.md) | FX revaluation (IAS 21) | Period-end retranslation |
| [CPT-0112](npv-and-irr.md) | NPV & IRR | Capital project evaluation |

## Not concepts (excluded from G10)

> Lifecycle constructors / state-machine progress — governed by `rule.md` (FIN-R*).

`createInvoice` · `completionPct`

## Divergences surfaced (for the backlog)

- **Three 3WM tolerance policies** (CPT-0103): PY dept 11 1%, TS invoice 2%, dept 01
  0%/2% — one AP policy should govern (U8).
- **C2C classification bands differ** (CPT-0104): PY GOOD ≤ 30 vs TS GOOD < 20;
  zero denominators raise in PY, return 0 in TS.
- **DIO duplicated** across depts 03 and 11 (CPT-0105 note) — dedup candidate.
- **Cost-to-serve taxonomies differ** (CPT-0109): PY 5 elements vs TS 7
  (customer support, credit risk).
- **Unbudgeted spend escapes the explanation trigger** (CPT-0108) when budget = 0.
