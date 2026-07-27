---
id: id-registry
title: "ID Registry — stable identifier namespace"
type: governance
owner: orchestrator
status: active
since: 2026-07-19
updated: 2026-07-27
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
3. Retired IDs stay listed as retired — never reassigned. **SCM-R1, R2, R5, R8, R11, R12 and
   R13 are retired** (ADR-0037): they stated company policy or an engineering convention as
   supply-chain law. They remain listed in their owning file so old citations resolve.

## 1. Rule-ID families — LIVE

> All 14 department families materialized at U4 (2026-07-20); IDs append-only per file.

| Prefix | Area | Owning doc | Highest allocated |
|---|---|---|---|
| SCM | Cross-department core rules (externally-fixed only) | `docs/30-foundation/scm-core/rule.md` | SCM-R14 |
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
| ENG | Engineering (build-time, cross-cutting) | `docs/50-engineering/rule.md` | ENG-R10 |
| PLT | Platform / workspace (above the 14 depts) | `docs/30-foundation/platform/rule.md` | PLT-R5 |

### Concept IDs — LIVE (ADR-0015)

> One estate-wide family: concepts cross department boundaries (EOQ is cited by planning,
> inventory and finance), so IDs are **not** per-department. Append-only.

| Prefix | Area | Owning doc | Highest allocated |
|---|---|---|---|
| CPT | Supply-chain concepts (definitions, no parameters — ADR-0037) | `docs/25-concepts/` (per-node files) | CPT-0154 |

Allocated so far: **CPT-0001 … CPT-0154**. CPT-0001..0025 = dept 03 (demand-planning);
CPT-0026..0035 = dept 01 (procurement); CPT-0036..0049 = dept 06 (warehouse management);
CPT-0050..0059 = dept 08 (quality management);
CPT-0060..0070 = dept 02 (supplier management);
CPT-0071..0081 = dept 10 (risk management);
CPT-0082..0092 = dept 13 (order management);
CPT-0093..0102 = dept 09 (compliance & regulatory);
CPT-0103..0112 = dept 11 (finance & controlling);
CPT-0113..0122 = dept 05 (inventory management);
CPT-0123..0131 = dept 07 (logistics & transportation);
CPT-0132..0138 = dept 14 (supplier development);
CPT-0139..0146 = dept 04 (supply planning);
**CPT-0147..0153 = dept 12 (S&OP planning)**; **CPT-0154 = money quantization &
sum-preserving allocation** (dept 11 catalogue). See
[25-concepts/_index.md](../25-concepts/_index.md).

> **Pending under ADR-0037:** the catalogue was written when nodes were allowed to carry
> parameters and link to implementations. The implementation links are gone; the **parameter
> sweep is outstanding** — nodes may still state a threshold, target or weighting that the
> inclusion test forbids. Each node is corrected as it is next touched, and no gate can detect
> this for you (see 25-concepts/_index.md "What the gate does and does not check").

## 2. Rule-ID families — RESERVED (future areas)

- **PLT — now LIVE** (materialized at W2, 2026-07-22, in `docs/30-foundation/platform/rule.md`;
  see §1). PLT-R1 prompt-refinement gate (ADR-0032) · PLT-R2 read-only project reference ·
  PLT-R3 everything-connected · PLT-R4 node/edge typing · PLT-R5 one-branch-per-project.
- *(no other reserved families — a 15th SCM department appends via its own ADR)*

## 3. Decision (ADR) numbers

- Format: `ADR-NNNN`, strictly increasing, allocated at proposal time.
- Allocated: **ADR-0001 … ADR-0037** (see `docs/10-decisions/README.md`).
  0001–0009 retroactive; 0010–0013 proposed at skeleton adoption; 0014 (MIT) accepted;
  0015 (concepts) / 0016 (business-context extraction) proposed; **0017–0021 proposed —
  the full-stack product decisions** (staging, Clean Architecture, Decimal money, gRPC
  calc core, Context-Engineering mapping); **0022–0026 proposed — the build toolchain,
  structure & UX** (pnpm+Turbo, monorepo layout, Postgres read model, GraphQL code-first,
  octagon node-graph front end); **0027 — the agent layer** (7 profiles + 7
  technology skills; resolves the open "Agent lanes" decision); **0028/0029 — domain
  resolutions** (canonical z-score = exact inverse-normal, resolves U15; order-management
  calc dir dissolved, resolves the U11 numbering collision). **All 0010..0029 ratified
  Accepted (owner-authorized 2026-07-20).** **0030/0031/0032 — the tech-company operating
  direction** (SCM as the Global Context governing a multi-branch tech-project portfolio;
  monitoring connector; prompt-refinement gate), **Accepted (owner-directed 2026-07-22)** —
  assumptions A1 (context scope = SCM-as-operating-context) and A2 (reference+overlay)
  resolved on ADR-0030; A3 (both sources, internal-first) on ADR-0031; A4 (prompt-gate
  enforcement surface) on ADR-0032 still owner-confirmable.
  **0033/0034 — the lane & scale direction** (exclusive technology lanes; ClickHouse
  analytics tier + Docker/Kubernetes), **Accepted (owner-directed 2026-07-22)**.
  **0035/0036 — the core & telemetry direction** (Rust is the complete core with Python as
  the tools layer; telemetry data model at tens-of-thousands scale), **Accepted
  (owner-directed 2026-07-22)**.
  Supersession chain: **ADR-0019** supersedes the ADR-0006 money clause and rewrites
  SCM-R8; **ADR-0022** supersedes ADR-0013 (npm → pnpm); **ADR-0035** supersedes the
  TypeScript-owns-domain-logic clause of **ADR-0001** and **narrows ADR-0033**'s
  business-rules lane (owner: framework-free TypeScript → Rust), rewriting ENG-R1/ENG-R2 in
  part via **ENG-R10**. ADR-0030 **extends** (does not supersede) ADR-0017's staging;
  ADR-0036 **extends** ADR-0034/0031/0035; **ADR-0037** supersedes the two-language
  SCM-application premise of **ADR-0001** and narrows ADR-0015/0016/0035 — the context carries
  only externally-fixed standards, so the invented application was deleted.

## 4. Department / module keys

The 14 department keys are fixed by `docs/25-concepts/NN-<key>/`,
`docs/40-contexts/NN-<key>/` and `.claude/skills/<key>/`. They are stable IDs: never
renumbered, never reused. New departments append (15+) via an ADR. *(The code trees they once
mirrored — `packages/domain/src/NN-<key>/`, `services/calc/NN_<key>/` — were deleted by
ADR-0037; the keys are unaffected.)*

## 5. Doc `id` conventions

`<type-slug>-<kebab-name>`: `index-<area>`, `rule-<area>`, `spec-<key>`,
`concept-<kebab-name>`, `glossary`, `adr` entries cited by number. Unique estate-wide
(gate G3).

## 6. Gate-invariant IDs (fixed)

`G1`–`G8` name the knowledge-architecture §11 invariants. New gates append (G9+).
Allocated: **G1–G10** (G9 context budget, ADR-0012; G10 **standards provenance** — was concept
coverage under ADR-0015, rewritten by ADR-0037 when the code it policed was deleted).
