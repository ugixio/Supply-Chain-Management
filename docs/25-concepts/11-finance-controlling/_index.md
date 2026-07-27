---
id: index-concepts-11-finance-controlling
title: "Concepts — Finance & Controlling (11)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-27
relations:
  - { type: part-of, target: index-concepts }
  - { type: governed-by, target: index-adr }
  - { type: traces-to, target: rule-finance-controlling }
---
# Concepts — Finance & Controlling (11)

> The concept catalogue for **Finance & Controlling (11)**: what each concept *means*,
> the formula where one is canonical, its assumptions and limits, and the standard or
> regulation that fixes it. Nodes **define**; they hold no threshold, target, weighting or
> mandated method, and they own no code (ADR-0037). Values a project must choose are named
> as project-chosen inputs and left unset.
>
> Departmental law lives in [40-contexts/11-finance-controlling/rule.md](../../40-contexts/11-finance-controlling/rule.md).

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
| [CPT-0154](money-quantization-and-allocation.md) | Money quantization & sum-preserving allocation | Any cent amount or split — the primitive under every other money node |

### Treasury & investment

| ID | Concept | Use when |
|---|---|---|
| [CPT-0110](fx-revaluation.md) | FX revaluation (IAS 21) | Period-end retranslation |
| [CPT-0112](npv-and-irr.md) | NPV & IRR | Capital project evaluation |
