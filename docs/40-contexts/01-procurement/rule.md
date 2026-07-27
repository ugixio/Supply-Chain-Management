---
id: rule-procurement
title: "Rules — Procurement (PRC-R*)"
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
# Rules — Procurement

> **A rule lives here only if something outside this repository fixes it** — a standards body, a
> regulator, or an arithmetic identity (ADR-0037). Anything an organization can reasonably choose
> is a **project decision** and is listed as such, never as an invariant. IDs are append-only
> (family `PRC`); a retired ID stays listed so old citations resolve. Cross-department rules
> (`SCM-R*`) are inherited, referenced never restated.

## Invariants (externally fixed — NEVER violated)

- **PRC-R1:** A purchase order states a **quantity** for every line. An order without a stated
  quantity is not an enforceable agreement to buy. *Source:* US UCC Article 2 (§2-201 requires the
  quantity term; the others may be supplied by the code).
- **PRC-R4:** Inspection **conserves** what arrived: for each received line,
  `accepted + rejected = received`. Nothing evaporates between the dock and the ledger, and a
  difference is missing information rather than a smaller receipt. *An arithmetic identity.*
- **PRC-R7:** Evaluation weights in a quotation comparison are **normalized** — they sum to one
  whole. Without that, two bids scored under differently-scaled weightings are not comparable.
  *An arithmetic identity;* the scale (1.0 or 100) and the criteria are the project's.
- **PRC-R8:** A contract's expiry is strictly **after** its effective date. An interval that ends
  before it starts has no duration. *An identity.*

## Retired rules

> Retired because they stated **project policy or an implementation detail** of code this
> repository no longer contains (ADR-0037). Listed permanently so citations resolve.

| ID | Was | Why retired |
|---|---|---|
| **PRC-R2** | "The PO status machine is strict — approved only from `DRAFT`/`PENDING_APPROVAL`…" | The named states and the transitions between them were one company's workflow. Whether an order needs approval at all, and what its states are called, is a project's design. |
| **PRC-R3** | "Receiving beyond `OVER_RECEIPT_TOLERANCE_PCT` (default 5%) is flagged" | The tolerance is a contract term, and the default was invented. What survives is the *question*, below. |
| **PRC-R5** | "A GRN cannot be `POSTED` while any line is uninspected" | Whether receipt requires inspection at all depends on the goods and the supplier relationship — many organizations post on receipt and inspect by sample. |
| **PRC-R6** | "Only `POSTED` GRNs can be reversed or closed…" | A lifecycle guard over invented states. The durable part — a financial record is corrected by a further entry, never erased — is **SCM-R3**. |

## Project decisions (the questions this department must answer for itself)

- The **approval threshold** and its levels, or whether purchase approval exists as a step.
- The **over- and under-receipt tolerance** — a term of the supply contract, per supplier or per
  category.
- Whether receipt requires **inspection** before it posts, and on what sampling basis.
- The **document lifecycle**: which states exist, and which transitions are legal.
- The **evaluation criteria** for comparing quotations, and their weights (PRC-R7 fixes only that
  they normalize).

## Inherited rules (referenced, not restated)

- **SCM-R3** — orders, receipts and contracts are financial records: corrected by reversal, never
  destroyed.
- **SCM-R6** — UFLPA: goods with a Xinjiang nexus are presumed made with forced labour.
- **SCM-R9 / R10 / R14** — ISO 8601 dates; GS1 units; exact money with sum-preserving
  apportionment.
