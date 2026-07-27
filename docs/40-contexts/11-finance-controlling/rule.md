---
id: rule-finance-controlling
title: "Rules — Finance & Controlling (FIN-R*)"
type: rule
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-27
relations:
  - { type: part-of, target: index-contexts }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: rule-scm-core }
---
# Rules — Finance & Controlling

> **A rule lives here only if something outside this repository fixes it** — a standards body, a
> regulator, or an arithmetic identity (ADR-0037). Anything an organization can reasonably choose
> is a **project decision** and is listed as such, never as an invariant. IDs are append-only
> (family `FIN`); a retired ID stays listed so old citations resolve. Cross-department rules
> (`SCM-R*`) are inherited, referenced never restated.

## Invariants (externally fixed — NEVER violated)

- **FIN-R4:** Inventory is measured at the **lower of cost and net realisable value**, and cost
  comprises purchase price, conversion, and the costs of bringing the item to its present location
  and condition. **LIFO is not permitted.** *Source:* IAS 2 §§9–11, 25 (and IAS 2 §16 for what is
  excluded — abnormal waste, most storage, most selling costs).
- **FIN-R5:** Only **non-recoverable** taxes capitalize into inventory cost. Recoverable VAT or
  GST is a receivable, not a cost of the goods, and capitalizing it overstates both inventory and
  later cost of sales. *Source:* IAS 2 §11.
- **FIN-R6:** An apportionment of a cost across lines **sums exactly to the cost apportioned** —
  no currency unit is created or destroyed by rounding the parts. *An arithmetic identity;* see
  SCM-R14 and CPT-0154.

## Retired rules

> Retired because they stated **project policy or an implementation detail** of code this
> repository no longer contains (ADR-0037). Listed permanently so citations resolve.

| ID | Was | Why retired |
|---|---|---|
| **FIN-R1** | "Every monetary input across finance is non-negative integer cents" | Money representation is an engineering concern (**ENG-R4**), and non-negativity is false in general: credits, reversals and adjustments are legitimately negative. |
| **FIN-R2** | "Landed-cost quantity is strictly positive and each component is non-negative" | Field checks. The durable part is that per-unit cost needs a positive quantity, which is division, not policy. |
| **FIN-R3** | "Period close is guarded — transitions validate the period status" | An invented lifecycle. |

## Project decisions (the questions this department must answer for itself)

- The **cost formula** among those IAS 2 permits: FIFO or weighted average, specific
  identification where items are not interchangeable — applied consistently for similar items.
- The **allocation basis** for landed cost: by value, by quantity, by weight, or mixed per
  component (duty by value, freight by weight is often the accurate answer).
- The **chart of accounts** and which accounts a movement maps to.
- **Variance bands** — what counts as on-budget, and what must be explained.
- The **close calendar** and its checklist.
- **Standard cost revision frequency**, where standard costing is used.

## Inherited rules (referenced, not restated)

- **SCM-R4** — every inventory movement has its double-entry consequence.
- **SCM-R14** — exact money, apportionment sums to the whole, ties to even.
- **SCM-R3** — a posted entry is reversed, never deleted.
