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
| DMD | 03-demand-planning | `docs/40-contexts/03-demand-planning/rule.md` | DMD-R8 |
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
| ENG | Engineering (build-time, cross-cutting) | `docs/50-engineering/rule.md` | ENG-R7 |

### Concept IDs — LIVE (ADR-0015)

> One estate-wide family: concepts cross department boundaries (EOQ is cited by planning,
> inventory and finance), so IDs are **not** per-department. Append-only.

| Prefix | Area | Owning doc | Highest allocated |
|---|---|---|---|
| CPT | Supply-chain concepts & calculations | `docs/25-concepts/` (per-node files) | CPT-0025 |

Allocated so far: **CPT-0001 … CPT-0025** — all in `docs/25-concepts/03-demand-planning/`
(the exemplar department; remaining 13 departments are in `census` mode, see
[25-concepts/_index.md](../25-concepts/_index.md)). CPT-0024/0025 are `draft`: specified
in the department's business-context document but **not implemented** (ADR-0016).

## 2. Rule-ID families — RESERVED (future areas)

*(none — all 14 department families are LIVE above; a 15th department appends via ADR)*

## 3. Decision (ADR) numbers

- Format: `ADR-NNNN`, strictly increasing, allocated at proposal time.
- Allocated: **ADR-0001 … ADR-0029** (see `docs/10-decisions/README.md`).
  0001–0009 retroactive; 0010–0013 proposed at skeleton adoption; 0014 (MIT) accepted;
  0015 (concepts) / 0016 (business-context extraction) proposed; **0017–0021 proposed —
  the full-stack product decisions** (staging, Clean Architecture, Decimal money, gRPC
  calc core, Context-Engineering mapping); **0022–0026 proposed — the build toolchain,
  structure & UX** (pnpm+Turbo, monorepo layout, Postgres read model, GraphQL code-first,
  octagon node-graph front end); **0027 — the agent layer** (7 profiles + 7
  technology skills; resolves the open "Agent lanes" decision); **0028/0029 — domain
  resolutions** (canonical z-score = exact inverse-normal, resolves U15; order-management
  calc dir dissolved, resolves the U11 numbering collision). **All 0010..0029 ratified
  Accepted (owner-authorized 2026-07-20).**
  Supersession chain: **ADR-0019** supersedes the ADR-0006 money clause and rewrites
  SCM-R8; **ADR-0022** supersedes ADR-0013 (npm → pnpm).

## 4. Department / module keys

The 14 department keys are fixed by the existing tree (`src/departments/NN-<key>/`,
mirrored in `python/NN_<key>/` and `.claude/skills/<key>/`). They are stable IDs: never
renumbered, never reused. New departments append (15+) via an ADR.

## 5. Doc `id` conventions

`<type-slug>-<kebab-name>`: `index-<area>`, `rule-<area>`, `spec-<key>`,
`concept-<kebab-name>`, `glossary`, `adr` entries cited by number. Unique estate-wide
(gate G3).

## 6. Gate-invariant IDs (fixed)

`G1`–`G8` name the knowledge-architecture §11 invariants. New gates append (G9+).
Allocated: **G1–G10** (G9 context budget, ADR-0012; G10 concept coverage, ADR-0015).
