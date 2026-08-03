---
id: id-registry
title: "ID Registry — stable identifier namespace"
type: governance
owner: orchestrator
status: active
since: 2026-07-19
updated: 2026-08-03
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
> **Reclassified at Phase C2 (2026-07-27, ADR-0037):** every family was swept with the inclusion
> test. Of the original **70** department rules, **45 are retired** — they stated an invented
> workflow, a field check, or a policy value belonging to code this repository no longer contains —
> and **25 survived**. **13 new IDs** were allocated for statements that *are* externally fixed but
> had never been written down: the IAS 2 measurement and non-recoverable-tax rules, the Incoterms
> sea-only restriction, the ISO 2859-1 table discipline, EUDR's benchmark-read obligation, and
> several conservation and measurement identities (allocation conserves, an ordinal product stays
> ordinal, a defect rate needs its opportunity base). Total now **38 live**.
>
> A retired ID is **never redefined**. Where a retired rule gestured at something durable, the
> durable form took a **new** ID — SUP-R2 → SUP-R5, CMP-R1 → CMP-R4, SDV-R3 → SDV-R6 — so a stale
> citation resolves to the retirement note and its reason rather than silently to different law.

| Prefix | Area | Owning doc | Highest allocated |
|---|---|---|---|
| SCM | Cross-department core rules (externally-fixed only) | `docs/30-foundation/scm-core/rule.md` | SCM-R14 |
| PRC | 01-procurement | `docs/40-contexts/01-procurement/rule.md` | PRC-R8 |
| SUP | 02-supplier-management | `docs/40-contexts/02-supplier-management/rule.md` | SUP-R5 |
| DMD | 03-demand-planning | `docs/40-contexts/03-demand-planning/rule.md` | DMD-R9 |
| SPL | 04-supply-planning | `docs/40-contexts/04-supply-planning/rule.md` | SPL-R5 |
| INV | 05-inventory-management | `docs/40-contexts/05-inventory-management/rule.md` | INV-R5 |
| WHS | 06-warehouse-management | `docs/40-contexts/06-warehouse-management/rule.md` | WHS-R6 |
| LOG | 07-logistics-transportation | `docs/40-contexts/07-logistics-transportation/rule.md` | LOG-R4 |
| QMS | 08-quality-management | `docs/40-contexts/08-quality-management/rule.md` | QMS-R8 |
| CMP | 09-compliance-regulatory | `docs/40-contexts/09-compliance-regulatory/rule.md` | CMP-R4 |
| RSK | 10-risk-management | `docs/40-contexts/10-risk-management/rule.md` | RSK-R6 |
| FIN | 11-finance-controlling | `docs/40-contexts/11-finance-controlling/rule.md` | FIN-R6 |
| SOP | 12-sop-planning | `docs/40-contexts/12-sop-planning/rule.md` | SOP-R5 |
| ORD | 13-order-management | `docs/40-contexts/13-order-management/rule.md` | ORD-R7 |
| SDV | 14-supplier-development | `docs/40-contexts/14-supplier-development/rule.md` | SDV-R6 |
| ENG | Engineering (build-time, cross-cutting) | `docs/50-engineering/rule.md` | ENG-R11 |
| PLT | Platform / workspace (above the 14 depts) | `docs/30-foundation/platform/rule.md` | PLT-R7 |
| MSR | Measurement identities (how a measure aggregates, cross-department) | `docs/30-foundation/measurement/rule.md` | MSR-R2 |

### Concept IDs — LIVE (ADR-0015)

> One estate-wide family: concepts cross department boundaries (EOQ is cited by planning,
> inventory and finance), so IDs are **not** per-department. Append-only.

| Prefix | Area | Owning doc | Highest allocated |
|---|---|---|---|
| CPT | Concepts — supply-chain and platform (definitions, no parameters — ADR-0037) | `docs/25-concepts/` (per-node files) | CPT-0167 |

Allocated so far: **CPT-0001 … CPT-0167**. CPT-0001..0025 = dept 03 (demand-planning);
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
sum-preserving allocation** (dept 11 catalogue);
**CPT-0155..0160 = platform delivery metrics** for the monitoring application (group
`00-platform`, Phase M1) — one estate-wide family rather than a second catalogue, as the product
statement fixes. See [25-concepts/_index.md](../25-concepts/_index.md);
**CPT-0161..0166 = dept 06 throughput, backlog and event-rate indicators** (owner-requested
2026-08-01). Allocated to **dept 06, not to `00-platform`**, and the distinction is the point: the
platform catalogue admits a metric only if *a project's development* produces the signal, and these
are warehouse operations. They are **definitions only** — no ingestion, no schema and no connector
were built for them, and the operational-telemetry question is recorded as open in
[program/WORKFLOW.md](../program/WORKFLOW.md);
**CPT-0167 = deployment rework rate**, the fifth DORA delivery metric, added 2026-08-03 when the
platform catalogue was checked against the current published grouping and found to carry four of five.

> **CPT-0999 is RESERVED and never allocated to a real node.** The context-adherence evaluation
> (ADR-0043) asks a cold subagent to author a node with a stated number, and its answer is scored by
> running the gates over a throwaway worktree. If that number were a live allocation the task would
> fail on a duplicate CPT — a spurious failure, in the one place the estate measures itself. The
> reservation is the fix, and it is recorded here because this file is the collision authority.

> **Swept under ADR-0037 (Phases C1a/C1b, 2026-07-27):** implementation links removed from all
> nodes; every numeric threshold, target, weighting and rating band removed or attributed to the
> regulator that fixes it; per-language annotations resolved to one canonical answer each. What no
> gate can check remains true — a number copied from a textbook example reads exactly like a
> standard — so the anti-states in
> [30-foundation/scm-core/rule.md](../30-foundation/scm-core/rule.md) stay the reviewer's
> checklist. **Phase C1c/C1d complete:** 58 of 154 nodes carry a `Project-chosen inputs` table (the
> rest are pure identities with no free parameter), and the per-language divergence sections — which
> had been concealing rating bands and tolerances — are gone.

## 2. Rule-ID families — RESERVED (future areas)

- **PLT — now LIVE** (materialized at W2, 2026-07-22, in `docs/30-foundation/platform/rule.md`;
  see §1). PLT-R1 prompt-refinement gate (ADR-0032) · PLT-R2 read-only project reference ·
  PLT-R3 everything-connected · PLT-R4 node/edge typing · PLT-R5 one-branch-per-project ·
  **PLT-R6 improvement-recommendation gate (ADR-0038, 2026-07-27)** — the standing search for a
  better implementation, and the rule that a missing detail is chosen from a selectable list rather
  than guessed · **PLT-R7 selected-and-declared knowledge (ADR-0045, 2026-08-03)** — no project uses
  the whole context, so the parts that apply are chosen and reported to the owner before development.
- *(no other reserved families — a 15th SCM department appends via its own ADR)*

## 3. Decision (ADR) numbers

- Format: `ADR-NNNN`, strictly increasing, allocated at proposal time.
- Allocated: **ADR-0001 … ADR-0038** (see `docs/10-decisions/README.md`).
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
  SCM-R14; **ADR-0022** supersedes ADR-0013 (npm → pnpm); **ADR-0035** supersedes the
  TypeScript-owns-domain-logic clause of **ADR-0001** and **narrows ADR-0033**'s
  business-rules lane (owner: framework-free TypeScript → Rust), rewriting ENG-R1/ENG-R2 in
  part via **ENG-R10**. ADR-0030 **extends** (does not supersede) ADR-0017's staging;
  ADR-0036 **extends** ADR-0034/0031/0035; **ADR-0037** supersedes the two-language
  SCM-application premise of **ADR-0001** and narrows ADR-0015/0016/0035 — the context carries
  only externally-fixed standards, so the invented application was deleted. **ADR-0038 extends
  ADR-0032/PLT-R1** from refining the prompt to resolving what the prompt left open, and is bounded
  by ADR-0002/ENG-R8 — an improvement recommendation may never introduce a new technology.

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
Allocated: **G1–G16** (G9 context budget, ADR-0012; G10 **standards provenance** — was concept
coverage under ADR-0015, rewritten by ADR-0037 when the code it policed was deleted; **G11
retired rules stay retired**, added at Phase C3 because a citation of a retired ID is invisible to
G4 — it is not a broken link, it silently resolves to nothing and reads as law; **G12 a rule
citation names an ID**, added at Phase C1d after 47 nodes were found citing family wildcards like
`**FIN-R***` — invisible for the same reason, and most of them stood in for lifecycle rules
retired with the deleted application; **G13** `updated:` truthfulness, **G14** load-set budgets, **G15** context-adherence freshness, **G16** this file's retired roster).

### The retired roster — complete, and gated

> **Why this block exists.** The first context-adherence run (ADR-0043) failed its citation task by
> naming six retired rules, and the agent could not have known: its load set carries this registry
> and the engineering rules, and **the retirement tables live in the fifteen `rule.md` files, none
> of which it had**. The narrative map below covers most of them, but in grouped prose
> (`WHS-R1 / R2 / R3 / R4`) that no reader can trust for *completeness* and no gate could check.
>
> This roster is the complete set, and **G16 asserts it equals the union of the retirement tables**
> — in both directions, so it cannot silently fall behind or claim a retirement that never
> happened. A roster that drifts is worse than none, because it would be believed.

```retired-roster
# family: retired numbers — the complete set, asserted against the rule files by G16.
CMP: 1
DMD: 1 2 3 4 5 7 8
FIN: 1 2 3
INV: 2 3
LOG: 2
ORD: 1 2 3 4
PRC: 2 3 5 6
QMS: 1 2 3 4
RSK: 1 3 4
SCM: 1 2 5 8 11 12 13
SDV: 1 2 3
SOP: 1 2 3
SPL: 3 4
SUP: 1 2 3 4
WHS: 1 2 3 4
```

**Fifty-two retired IDs.** None is ever reassigned; a citation of one resolves to nothing and reads
as law, which is what G11 exists to catch after the fact and what this roster exists to prevent
before it.

### What replaced a retired rule (Phase C3)

> A retired ID is never reassigned, so a reader who meets an old citation needs to know where the
> durable part went. This table is that map — the *narrative* companion to the roster above. It
> lives here because the registry is the allocation authority and one of G11's three exempt homes.

| Retired | Where the durable part went |
|---|---|
| SCM-R8 | Split: **SCM-R14** carries the arithmetic identity (apportionment sums to the whole, ties to even); **ENG-R4/R5** carry the code duty (no float, string on the wire). |
| SCM-R1 | **INV-R5** — a physical balance cannot be negative. The `backorderAllowed` exception was policy and is now a project decision. |
| SCM-R2 | Nothing. An approval threshold is policy; **PRC-R1** (a line states its quantity) is what remains. |
| SCM-R5 | **CMP-R3** for the REACH trigger; the traceability obligation otherwise follows the law that applies to the goods. |
| SCM-R11 | Nothing — identifier stability is a data-modelling decision. |
| SCM-R12 | The `ENG-R*` family — retry safety is an engineering concern. |
| SCM-R13 | The `ENG-R*` family — a code standard for a codebase this repository no longer has. |
| DMD-R4 | Nothing. A mean of absolute values is non-negative by arithmetic; the rule restated it. |
| DMD-R5 / R7 / R8 | Project decisions (minimum history, override classification, safety-stock method). **DMD-R9** states what survives: a forecast carries its horizon and bucket. |
| PRC-R3 | A project decision (the tolerance is a contract term). |
| PRC-R5 / R6 | **PRC-R4** — inspection conserves what arrived. |
| WHS-R1 / R2 / R3 / R4 | **WHS-R5** — task quantities conserve. The lifecycles and scales were the project's. |
| SUP-R2 | **SUP-R5** — an evaluation records its basis (ISO 9001 §8.4.1). |
| CMP-R1 | **CMP-R4** — an exception has an expiry. |
| SDV-R1 / R2 / R3 | **SDV-R4/R5/R6** — evidence and dating, unknown ≠ compliant, and EUDR's benchmark-read duty. |
| FIN-R1 / R2 / R3 | **FIN-R4/R5/R6** (IAS 2 measurement, non-recoverable tax, apportionment) and **ENG-R4**. |
| QMS-R1..R4 | **QMS-R5/R6/R7** (ISO 2859-1 table, sample ≠ lot, opportunity base) and **ENG-R4**. QMS-R1's durable half returned at Phase C2b as **QMS-R8** — ISO 9001:2015 §10.2.1 requires a corrective action's *effectiveness* to be reviewed, which is an obligation the invented lifecycle had been carrying. |
| RSK-R1 / R3 / R4 | Project decisions (scale, justification, recovery objectives). **RSK-R5/R6** state the measurement facts. |
| ORD-R1..R4 | **ORD-R5/R6/R7** (allocation conserves, perfect order is a conjunction, a credit cannot exceed the charge). |
| SOP-R1 / R2 / R3 | **SOP-R4/R5** (consensus is one plan; attainment is measured against the committed plan). |
| SPL-R3 / R4 | Project decisions (approving an infeasible plan, the horizon). **SPL-R5** states netting conservation. |
| INV-R2 / R3 | **INV-R4** — a balance is the sum of its movements. Sign conventions are the project's. |
| LOG-R2 | The OTD concept node (CPT-0123) — it is a measurement definition, not an invariant. |

**G11's exemptions are principled, not conveniences.** Three homes may name a retired ID, because
naming it there is the opposite of citing it as law: the rule file that **declares** the
retirement, **this registry** (a retirement is an allocation fact), and the **ADRs** (append-only
history — editing an old decision to remove an ID would falsify the record).
