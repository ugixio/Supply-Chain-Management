---
id: id-registry
title: "ID Registry — stable identifier namespace"
type: governance
owner: orchestrator
status: active
since: 2026-07-19
updated: 2026-07-19
relations:
  - { type: part-of, target: index-governance }
  - { type: governed-by, target: knowledge-architecture }
---
# ID Registry

> The collision authority for every stable identifier. Identifiers are **allocated here
> first**, then used — never invented inline, never renumbered, never reused.

## Allocation rules

1. Take the next free number/key from the family table.
2. Record the allocation in the same commit that uses it.
3. Retired IDs stay listed as retired — never reassigned.

## 1. Rule-ID families — LIVE

> All 14 department families materialized at U4 (2026-07-20); IDs append-only per file.

| Prefix | Area | Owning doc | Highest allocated |
|---|---|---|---|
| SCM | Cross-department core rules | `docs/30-foundation/scm-core/rule.md` | SCM-R13 |
| PRC | 01-procurement | `docs/40-contexts/01-procurement/rule.md` | PRC-R8 |
| SUP | 02-supplier-management | `docs/40-contexts/02-supplier-management/rule.md` | SUP-R4 |
| DMD | 03-demand-planning | `docs/40-contexts/03-demand-planning/rule.md` | DMD-R4 |
| SPL | 04-supply-planning | `docs/40-contexts/04-supply-planning/rule.md` | SPL-R4 |
| INV | 05-inventory-management | `docs/40-contexts/05-inventory-management/rule.md` | INV-R3 |
| WHS | 06-warehouse-management | `docs/40-contexts/06-warehouse-management/rule.md` | WHS-R4 |
| LOG | 07-logistics-transportation | `docs/40-contexts/07-logistics-transportation/rule.md` | LOG-R3 |
| QMS | 08-quality-management | `docs/40-contexts/08-quality-management/rule.md` | QMS-R4 |
| CMP | 09-compliance-regulatory | `docs/40-contexts/09-compliance-regulatory/rule.md` | CMP-R3 |
| RSK | 10-risk-management | `docs/40-contexts/10-risk-management/rule.md` | RSK-R4 |
| FIN | 11-finance-controlling | `docs/40-contexts/11-finance-controlling/rule.md` | FIN-R3 |
| SOP | 12-sop-planning | `docs/40-contexts/12-sop-planning/rule.md` | SOP-R3 |
| ORD | 13-order-management | `docs/40-contexts/13-order-management/rule.md` | ORD-R4 |
| SDV | 14-supplier-development | `docs/40-contexts/14-supplier-development/rule.md` | SDV-R3 |

## 2. Rule-ID families — RESERVED (future areas)

*(none — all 14 department families are LIVE above; a 15th department appends via ADR)*

## 3. Decision (ADR) numbers

- Format: `ADR-NNNN`, strictly increasing, allocated at proposal time.
- Allocated: **ADR-0001 … ADR-0014** (see `docs/10-decisions/README.md`).
  0001–0009 retroactive; 0010–0013 proposed at skeleton adoption; 0014 (MIT) accepted.

## 4. Department / module keys

The 14 department keys are fixed by the existing tree (`src/departments/NN-<key>/`,
mirrored in `python/NN_<key>/` and `.claude/skills/<key>/`). They are stable IDs: never
renumbered, never reused. New departments append (15+) via an ADR.

## 5. Doc `id` conventions

`<type-slug>-<kebab-name>`: `index-<area>`, `rule-<area>`, `spec-<key>`,
`glossary`, `adr` entries cited by number. Unique estate-wide (gate G3).

## 6. Gate-invariant IDs (fixed)

`G1`–`G8` name the knowledge-architecture §11 invariants. New gates append (G9+).
