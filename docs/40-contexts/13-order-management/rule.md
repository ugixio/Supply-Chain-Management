---
id: rule-order-management
title: "Rules — Order Management (ORD-R*)"
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
# Rules — Order Management

> **A rule lives here only if something outside this repository fixes it** — a standards body, a
> regulator, or an arithmetic identity (ADR-0037). Anything an organization can reasonably choose
> is a **project decision** and is listed as such, never as an invariant. IDs are append-only
> (family `ORD`); a retired ID stays listed so old citations resolve. Cross-department rules
> (`SCM-R*`) are inherited, referenced never restated.

## Invariants (externally fixed — NEVER violated)

- **ORD-R5:** Allocation **conserves**: the sum of quantities allocated across orders cannot
  exceed the quantity available. Over-allocation promises the same unit twice and is discovered by
  the customer, not by the system. *An arithmetic identity.*
- **ORD-R6:** A **perfect-order** measure is the conjunction of its elements — on time **and**
  complete **and** damage-free **and** correctly documented. Because it multiplies, a perfect-order
  rate is always at most the worst of its components, and reporting a component rate as the
  perfect-order rate overstates performance. *An identity of the definition* (SCOR RL.1.1).
- **ORD-R7:** A return **credits no more than was charged**. A refund exceeding the original
  consideration is not a return but a payment, and it needs a different authorization. *An
  identity;* the fee deducted from it is a project decision.

## Retired rules

> Retired because they stated **project policy or an implementation detail** of code this
> repository no longer contains (ADR-0037). Listed permanently so citations resolve.

| ID | Was | Why retired |
|---|---|---|
| **ORD-R1** | "Order allocation never allocates from negative availability" | The durable statement is conservation, **ORD-R5**; a negative-availability check was one implementation's guard. |
| **ORD-R2** | "An RMA must have at least one line; every line has `returnQty > 0`" | Field checks over an invented document. |
| **ORD-R3** | "The RMA lifecycle is strict (approve → receive → inspect → close)" | An invented workflow — returns handling differs sharply between retail, distribution and industrial supply. |
| **ORD-R4** | "Credit-check monetary inputs are non-negative integer cents" | An engineering concern (**ENG-R4**), and outstanding balances can legitimately be negative. |

## Project decisions (the questions this department must answer for itself)

- The **allocation policy**: first-come, priority-based, fair-share, or reserved stock — and
  whether allocation is committed at order entry or at picking.
- Whether **backorders** are permitted, and how they are prioritized when stock arrives.
- The **elements of the perfect order** for this business, and how each is evidenced (SCOR names
  the components; which ones apply is contextual).
- **Return eligibility windows** and any **restocking fee** — bounded by consumer-protection law
  where it applies, which forbids a fee for faulty goods.
- **Credit limits** and what happens when an order breaches one.

## Inherited rules (referenced, not restated)

- **SCM-R3** — orders and credit notes are financial records: reversed, never deleted.
- **SCM-R14** — a refund apportioned across lines sums exactly to the credit issued.
- **SCM-R10** — ordered and returned quantities carry their units.
