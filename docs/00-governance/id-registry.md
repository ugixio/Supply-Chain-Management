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

| Prefix | Area | Owning doc | Highest allocated |
|---|---|---|---|
| SCM | Cross-department core rules | `docs/30-foundation/scm-core/rule.md` | SCM-R13 |

## 2. Rule-ID families — RESERVED (one per department; allocated when its `rule.md` is created)

| Prefix | Department | Prefix | Department |
|---|---|---|---|
| PRC | 01-procurement | QMS | 08-quality-management |
| SUP | 02-supplier-management | CMP | 09-compliance-regulatory |
| DMD | 03-demand-planning | RSK | 10-risk-management |
| SPL | 04-supply-planning | FIN | 11-finance-controlling |
| INV | 05-inventory-management | SOP | 12-sop-planning |
| WHS | 06-warehouse-management | ORD | 13-order-management |
| LOG | 07-logistics-transportation | SDV | 14-supplier-development |

## 3. Decision (ADR) numbers

- Format: `ADR-NNNN`, strictly increasing, allocated at proposal time.
- Allocated: **ADR-0001 … ADR-0011** (see `docs/10-decisions/README.md`).
  0001–0009 retroactive; 0010–0011 proposed at skeleton adoption.

## 4. Department / module keys

The 14 department keys are fixed by the existing tree (`src/departments/NN-<key>/`,
mirrored in `python/NN_<key>/` and `.claude/skills/<key>/`). They are stable IDs: never
renumbered, never reused. New departments append (15+) via an ADR.

## 5. Doc `id` conventions

`<type-slug>-<kebab-name>`: `index-<area>`, `rule-<area>`, `spec-<key>`,
`glossary`, `adr` entries cited by number. Unique estate-wide (gate G3).

## 6. Gate-invariant IDs (fixed)

`G1`–`G8` name the knowledge-architecture §11 invariants. New gates append (G9+).
