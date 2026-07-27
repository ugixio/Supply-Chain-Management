---
id: rule-scm-core
title: "Rules — SCM Core (externally-fixed standards) SCM-R1..R13"
type: rule
owner: orchestrator
status: active
since: 2026-07-19
updated: 2026-07-27
relations:
  - { type: part-of, target: index-foundation }
  - { type: governed-by, target: index-adr }
---
# Rules — SCM Core (externally-fixed standards)

> **A rule lives here only if something outside this repository fixes it** — a standards body,
> a regulator, or an arithmetic identity (ADR-0037). Anything an organization can reasonably
> choose is **project policy** and is stated as such in §Project decisions, never as an
> invariant. IDs are append-only: frozen once allocated, never renumbered, and a **retired ID
> stays listed as retired** so citations elsewhere resolve.

## Invariants (externally fixed — NEVER violated)

- **SCM-R3:** A financial record — an order, an invoice, a stock movement, a shipment — is
  **never destroyed**. Corrections are made by a further entry (reversal, credit note,
  adjustment) that leaves the original readable. *Source:* the audit-trail requirement common to
  IFRS/IAS record-keeping, tax law and SOX §802; the technique (soft-delete flag, append-only
  log) is a project's choice, the prohibition is not.
- **SCM-R4:** Every inventory movement has a **double-entry** accounting consequence: what is
  debited equals what is credited. *Source:* double-entry bookkeeping; IAS 2 for what
  capitalizes into inventory cost. Which GL accounts a movement maps to is a project's chart of
  accounts, not a standard.
- **SCM-R6:** Goods with any tie to Xinjiang (XUAR) are **presumed made with forced labour** and
  may not enter US commerce without clear-and-convincing rebuttal evidence. *Source:* UFLPA,
  US Pub. L. 117-78. What evidence a project collects and how it stores it is its own design.
- **SCM-R7:** In-scope due-diligence documentation is retained **at least 5 years** from the
  assessment date. *Source:* EU CSDDD, Directive (EU) 2024/1760 Art. 23 (as amended by Omnibus I,
  Directive (EU) 2026/470). Longer retention is a project's choice; shorter is unlawful.
- **SCM-R9:** Dates are **ISO 8601** (`YYYY-MM-DD`) and instants are **UTC**. *Source:*
  ISO 8601-1:2019.
- **SCM-R10:** Quantities carry a **GS1 unit-of-measure code**, and a quantity without its unit
  is not a quantity. *Source:* GS1 General Specifications v23 / UN/ECE Rec. 20.
- **SCM-R14:** An apportionment of a monetary total across parts **sums exactly to the total** —
  no cent is created or lost by rounding the parts independently. Rounding of money is
  **explicit, at defined boundaries only, and ties resolve to even** (`roundTiesToEven`).
  *Source:* IEEE 754-2019 §4.3.3 for the tie rule; the sum-preservation requirement is an
  arithmetic identity, not a preference. *(See CPT-0154.)*

## Retired rules

> Retired because they stated **company policy or an implementation convention** as though it
> were a supply-chain standard (ADR-0037). Listed permanently so old citations resolve, and so
> the mistake is not repeated by re-allocating the ID.

| ID | Was | Why retired |
|---|---|---|
| **SCM-R1** | "Inventory never negative unless `backorderAllowed`" | The physical truth (you cannot ship what you do not have) is real, but the flag, the exception and where the check sits are design choices. A project that models allocation or consignment stock reasonably differs. → §Project decisions. |
| **SCM-R2** | "A PO at or above `PO_APPROVAL_THRESHOLD_CENTS` (default $5,000) enters `PENDING_APPROVAL`" | Pure policy: the amount, the existence of an approval step, and the status names are each a company's choice. → §Project decisions. |
| **SCM-R5** | "Lot tracking mandatory when `storageCondition !== AMBIENT` or `reachSVHC`" | The *obligation* to trace comes from law (EU 178/2002 for food, REACH for SVHC, GDP/GMP for pharma) and is stated per department; this particular trigger condition was invented. |
| **SCM-R8** | "Money is arbitrary-precision Decimal, `ROUND_HALF_EVEN`, string over gRPC" | An engineering standard, not a supply-chain one. The externally-fixed part is now **SCM-R14**; the implementation obligations are **ENG-R4/ENG-R5**. |
| **SCM-R11** | "SKU codes immutable; lifecycle via status flags" | A sound data-modelling convention, but a convention. → §Project decisions. |
| **SCM-R12** | "Inventory transactions carry an `idempotencyKey`" | Retry safety belongs to the write path (`ENG` family), not to supply-chain law. |
| **SCM-R13** | "Python type hints and docstrings; pytest mirrors Jest" | A code standard, and for a codebase this repository no longer has. |

## Project decisions (recorded as examples, never as law)

> These are the questions a project **must answer for itself**. The context's job is to make the
> question explicit and name the standard that constrains the answer — not to answer it.

| Decision | Constrained by | Typical range (illustrative only) |
|---|---|---|
| Purchase-order approval threshold and levels | internal control policy; SOX for listed filers | varies by spend and delegation of authority |
| Over- and under-receipt tolerance | the supply contract | commonly a low single-digit percentage |
| Negative-stock policy (allow backorder, allocate, refuse) | fulfilment model | — |
| Cycle service level and safety-stock method | service commitments, cost of capital | — |
| Inventory carrying rate | cost of capital, storage, obsolescence | — |
| Supplier-scorecard criteria, weights and rating bands | the sourcing strategy | — |
| Quality target (PPM/DPMO) and AQL level | the customer contract; **the plan** then follows ISO 2859-1 | — |
| Lot/serial granularity | the traceability law that applies to the goods | — |

**Nothing in the table above is a default this context supplies.** Where a project needs a
starting point, it takes it from its own contracts and its own regulator, not from here.

## Anti-states (the context must never allow)

- A **threshold, target, weighting or rating band** stated as an invariant anywhere in `docs/`.
- A rule whose source is "this is how we did it" rather than a citable standard, regulation or
  identity.
- A concept node that mandates *which* method a project must use, where more than one is
  legitimate (EOQ vs. periodic order quantity vs. dynamic lot-sizing).
- Money apportioned so the parts no longer sum to the whole (SCM-R14).
- A financial record destroyed rather than reversed (SCM-R3).
