---
id: index-concepts
title: "Concepts — the supply-chain standards catalogue"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-08-03
relations:
  - { type: part-of, target: index-docs }
  - { type: governed-by, target: index-adr }
  - { type: refines, target: glossary }
---
# Concepts — the supply-chain standards catalogue

- **Belongs here:** one node per **concept** (ADR-0015, narrowed by ADR-0037) — the fourteen
  supply-chain departments, plus **platform delivery metrics (00)** for the monitoring application.
  One catalogue, not two: a project consults one place for what a number means. A node carries what the concept *means*, the
  formula where one is canonical, its named symbols and units, its assumptions and the cases
  where it does not apply, and **the standard, regulation or identity that fixes it**.
- **Never here (ADR-0037):** thresholds, targets, tolerances, weightings, rating bands, a
  mandated method where several are legitimate, or a link to an implementation. Those are each
  project's decision. Where a calculation needs values, the node names them under
  **Project-chosen inputs** and leaves them unset.
- **Authority (Tier 3):** these nodes define **what a term means**. They do not state
  law — invariants live in the Tier 4 `rule.md` of the owning department and are cited
  here by ID, never restated.
- **Relation to the glossary:** [20-product-model/glossary.md](../20-product-model/glossary.md)
  stays the one-line controlled vocabulary (one term, one spelling). A concept node is
  the long form the glossary row points to. The glossary remains authoritative for
  spelling; the concept node is authoritative for meaning and mathematics.
- **IDs:** a single estate-wide family `CPT-NNNN` (id-registry §1). Concepts cross
  department boundaries — EOQ is cited by planning, inventory and finance — so IDs are
  not per-department.
- **Template:** [program/templates/concept.md](../program/templates/concept.md).


## Who consumes this catalogue

**Both** (owner, 2026-08-03): the company administering *itself*, where a definition read is a
definition used and no code is needed; and a project whose product is in this domain, which selects
and declares the nodes that apply (**PLT-R7**).

Recorded because **160 of 167 nodes have no consumer in code** and a reader could not tell a reference
library from an abandoned one. **A node nothing references is not unfinished** — ADR-0037 settled that
the context defines and never implements.

## Measurement identities every node inherits

Two pieces of arithmetic constrain how any measure in this catalogue may be aggregated, and they are
stated once rather than in each node — [30-foundation/measurement/rule.md](../30-foundation/measurement/rule.md):

- **MSR-R1** — a ratio aggregates from its components (`Σnumerator ÷ Σdenominator`), never by
  averaging ratios. Numerator and denominator share one population and one period.
- **MSR-R2** — a flow sums across intervals; a level never does.

A node that publishes a ratio or a level **cites the rule**; it does not restate it (ADR-0039).

## What the gate does and does not check

**G10 checks provenance, not coverage.** It asserts that each node claims a unique `CPT-*`
number, cites a source under `## References`, and carries no `## Implementations` section.
Until ADR-0037 it asserted the opposite thing — that every public symbol in the application
code had a node — which stopped meaning anything when that application was deleted.

What no gate can check is whether a node's *content* is genuinely externally fixed. A number
copied out of a textbook example reads exactly like a standard. That judgement stays with the
reviewer, and the anti-states in
[30-foundation/scm-core/rule.md](../30-foundation/scm-core/rule.md) are the checklist for it.

## Groups

| # | Group | |
|---|---|---|
| 00 | [00-platform](00-platform/_index.md) | delivery metrics — the monitoring application |
| 03 | [03-demand-planning](03-demand-planning/_index.md)  |
| 01 | [01-procurement](01-procurement/_index.md)  |
| 02 | [02-supplier-management](02-supplier-management/_index.md)  |
| 04 | [04-supply-planning](04-supply-planning/_index.md)  |
| 05 | [05-inventory-management](05-inventory-management/_index.md)  |
| 06 | [06-warehouse-management](06-warehouse-management/_index.md)  |
| 07 | [07-logistics-transportation](07-logistics-transportation/_index.md)  |
| 08 | [08-quality-management](08-quality-management/_index.md)  |
| 09 | [09-compliance-regulatory](09-compliance-regulatory/_index.md)  |
| 10 | [10-risk-management](10-risk-management/_index.md)  |
| 11 | [11-finance-controlling](11-finance-controlling/_index.md)  |
| 12 | [12-sop-planning](12-sop-planning/_index.md)  |
| 13 | [13-order-management](13-order-management/_index.md)  |
| 14 | [14-supplier-development](14-supplier-development/_index.md)  |

## How to extend

1. Allocate the next `CPT-NNNN` in [id-registry §1](../00-governance/id-registry.md).
2. Copy the template into `docs/25-concepts/<NN-group>/<slug>.md`.
3. Add its row to that group's `_index.md`.
4. Run `make verify` — G10 checks the CPT number is unique and the source is cited.

- **Governing refs:** `CLAUDE.md` · [ADR-0015](../10-decisions/README.md) ·
  [00-governance/knowledge-architecture.md](../00-governance/knowledge-architecture.md).
