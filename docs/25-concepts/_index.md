---
id: index-concepts
title: "Concepts — the supply-chain calculation catalogue"
type: concept
owner: orchestrator
status: active
since: 2026-07-20
updated: 2026-07-20
relations:
  - { type: part-of, target: index-docs }
  - { type: governed-by, target: index-adr }
  - { type: refines, target: glossary }
---
# Concepts — the supply-chain calculation catalogue

- **Belongs here:** one node per supply-chain **calculation or concept** (ADR-0015),
  grouped by the department that owns its implementation. Each node carries the formula
  with named symbols and units, its assumptions and non-applicability, a worked numeric
  example, and verified links to the TypeScript and Python that compute it.
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

## What G10 cannot see

G10 answers **"which code lacks a concept node"**. It is structurally blind to the
opposite question — **"which domain concept lacks code"** — because it enumerates symbols
found in `src/` and `python/`, and a concept nobody implemented has no symbol to find.

That second gap is real and material: extracting `03-demand-planning`'s business-context
document (ADR-0016) surfaced **Forecast Value Added** (CPT-0024) and **safety-stock
adequacy** (CPT-0025) — both required KPIs, neither implemented anywhere. A green G10 says
the catalogue covers the code; it never says the code covers the domain. Concept nodes
with `status: draft` and a `## Status — specified, NOT implemented` section carry that
second kind of gap, and the U18 extraction is what finds them.

## Coverage status (read by gate G10)

> `enforced` = every public calculation symbol in that department must have a concept
> node or an explicit exclusion; G10 fails otherwise. `census` = G10 only reports the
> gap, it does not fail. A department moves to `enforced` when its catalogue is complete.
> The status keyword is parsed from the third column — keep the table shape.

| # | Department | Coverage |
|---|---|---|
| 03 | [03-demand-planning](03-demand-planning/_index.md) | enforced |
| 01 | [01-procurement](01-procurement/_index.md) | enforced |
| 02 | [02-supplier-management](02-supplier-management/_index.md) | enforced |
| 04 | 04-supply-planning | census |
| 05 | [05-inventory-management](05-inventory-management/_index.md) | enforced |
| 06 | [06-warehouse-management](06-warehouse-management/_index.md) | enforced |
| 07 | [07-logistics-transportation](07-logistics-transportation/_index.md) | enforced |
| 08 | [08-quality-management](08-quality-management/_index.md) | enforced |
| 09 | [09-compliance-regulatory](09-compliance-regulatory/_index.md) | enforced |
| 10 | [10-risk-management](10-risk-management/_index.md) | enforced |
| 11 | [11-finance-controlling](11-finance-controlling/_index.md) | enforced |
| 12 | 12-sop-planning | census |
| 13 | [13-order-management](13-order-management/_index.md) | enforced |
| 14 | 14-supplier-development | census |

## How to extend

1. Allocate the next `CPT-NNNN` in [id-registry §1](../00-governance/id-registry.md).
2. Copy the template into `docs/25-concepts/<NN-dept>/<slug>.md`.
3. Add its row to that department's `_index.md`.
4. Run `make verify` — G10 checks the symbol links resolve and reprints the census.

- **Governing refs:** `CLAUDE.md` · [ADR-0015](../10-decisions/README.md) ·
  [00-governance/knowledge-architecture.md](../00-governance/knowledge-architecture.md).
