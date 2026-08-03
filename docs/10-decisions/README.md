---
id: index-adr
title: "Architecture Decision Records (ADR-0001..0046)"
type: adr
owner: orchestrator
status: active
since: 2026-07-19
updated: 2026-08-03
relations:
  - { type: part-of, target: index-docs }
  - { type: governed-by, target: governance-root }
---
# Architecture Decision Records — Supply Chain Management

> Format: each ADR records a decision, its context, consequences and alternatives
> (template: `docs/program/templates/adr.md`). An accepted ADR **is not reverted without
> a new ADR that supersedes it**. Statuses: `Proposed` · `Accepted` ·
> `Accepted (retroactive)` · `Superseded by ADR-XXXX` · `Deprecated`.
> ADR-0001..0009 are **retroactive**: they record decisions this repo had already made
> (evidence cited); the owner should review and ratify them.
>
> **Ratification log — 2026-07-20:** the owner authorized proceeding on all proposed
> decisions; **ADR-0010..0027 are Accepted (owner-authorized 2026-07-20)**. ADR-0028/0029
> (below) are accepted under the same authorization. Retroactive 0001..0009 stand as the
> repo's de-facto record.

---

## Decision index (the always-loaded layer — one line per ADR, full text on demand)

> The AI loads THIS index as part of the global rules (operating-model §1); a full ADR
> body below is read only when the task touches that decision (ADR-0012). Every new ADR
> adds its line here — gate G9 fails a missing one.

- ADR-0001 — TypeScript owns domain logic; Python owns analytics/ML. (retroactive)
- ADR-0002 — Dependencies must be OSI open source; prohibited tech listed with substitutes. (retroactive)
- ADR-0003 — English-only for all repo artifacts. (retroactive)
- ADR-0004 — 14-department structure aligned to SCOR-DS is the module taxonomy. (retroactive)
- ADR-0005 — Inventory is event-sourced; every other department is state-based. (retroactive)
- ADR-0006 — Integer-cent Money, ISO 8601/UTC, GS1 UOM, immutable SKU. (retroactive)
- ADR-0007 — Soft-delete for financial records; idempotent inventory transactions. (retroactive)
- ADR-0008 — Named standards/regulations (SCOR, ISO 28000, CSDDD, UFLPA, REACH…) are first-class product features. (retroactive)
- ADR-0009 — Jest for TS, pytest for Python. (retroactive)
- ADR-0010 — The ugixio context skeleton governs knowledge (tiers, SSOT, append-only ADRs). (accepted 2026-07-20)
- ADR-0011 — Conventional Commits, SemVer annotated tags, main always green. (accepted 2026-07-20)
- ADR-0012 — Context economics + executable gates: verify fast/full (G1–G7+G9), exemplar-unit rule, known-pitfalls feedback, evaluation protocol, risk/improvement registers, communication contract. (accepted 2026-07-20)
- ADR-0013 — npm is the single package manager; `package-lock.json` is the only lockfile. (**superseded by ADR-0022**)
- ADR-0014 — The repository is licensed MIT (LICENSE file matches `package.json`). (accepted)
- ADR-0015 — A concept-node layer (`docs/25-concepts/`, type `concept`, family `CPT`) makes every SCM calculation individually citable; gate G10 enforces symbol-link accuracy and reports coverage. (accepted 2026-07-20)
- ADR-0016 — Department `IMPLEMENTATION.md` files are **business context, not target architecture**: their SAP/Superset stack is non-normative; their rules, KPIs and formulas are extracted into governed nodes and the originals archived. (accepted 2026-07-20)
- ADR-0017 — The product is a full-stack app (Next.js · NestJS/GraphQL · PostgreSQL · Python), staged **wiki-of-concepts first**, transactional SCM later; the existing `src/departments` domain is preserved as the core. (accepted 2026-07-20)
- ADR-0018 — Backend follows **Clean Architecture** (entities → use-cases → interface-adapters → frameworks), deployed as a **modular monolith** with one module per department. (accepted 2026-07-20)
- ADR-0019 — Money becomes **arbitrary-precision Decimal** end-to-end (`decimal.js` / `decimal.Decimal` / `NUMERIC(19,4)`); **supersedes the integer-cent clause of ADR-0006 and rewrites SCM-R14**. (accepted 2026-07-20)
- ADR-0020 — The Python calculation core is a separate service reached over **gRPC** with a protobuf contract; decimals cross the wire as strings to preserve precision. (accepted 2026-07-20)
- ADR-0021 — The Context Engineering layer the enterprise prompt asks for is **already instantiated** by the docs/ tier tree, gates and program area; it is mapped and gap-filled, never rebuilt in parallel. (accepted 2026-07-20)
- ADR-0022 — **pnpm + Turborepo** is the monorepo toolchain; **supersedes ADR-0013** (npm). pnpm workspaces manage dependencies, Turbo orchestrates and caches tasks. (accepted 2026-07-20)
- ADR-0023 — Repository is a monorepo with **Clean-Architecture layers as packages** (`domain`/`application`/`infrastructure`/`shared`), each organized by department inside; the modular-monolith boundary lives at the NestJS app (one module per department). (accepted 2026-07-20)
- ADR-0024 — Stage A serves the knowledge graph from a **Postgres read model rebuilt one-way from `docs/`**; `docs/` stays the single source of truth, the projection is disposable and never hand-edited. (accepted 2026-07-20)
- ADR-0025 — GraphQL is **code-first** (NestJS decorators generate the SDL); the schema is a build artifact, not a hand-maintained file. (accepted 2026-07-20)
- ADR-0026 — The wiki front end is a **node-graph of octagons**: SCM core centre, 14 departments as a connected circuit, CPT sub-nodes on expand; LED-cyan stroke on transparent fill; node click opens a right sidebar. (accepted 2026-07-20)
- ADR-0027 — The **agent layer is formalized** (resolves the open "Agent lanes" decision): 7 least-privilege subagent profiles (`.claude/agents/`) over WHAT/HOW/SPECIALTY lanes + 7 technology/practice skills; the main session is the orchestrator; agents reference the governance, never restate it. (accepted 2026-07-20)
- ADR-0028 — The **canonical service-level z-score is the exact inverse-normal** Φ⁻¹ (Python `scipy.stats.norm.ppf`; TypeScript a high-accuracy rational approximation). Resolves U15; the lookup tables are retired. (accepted 2026-07-20)
- ADR-0029 — The misplaced `07_order_management` calc dir is dissolved: perfect-order metrics belong to dept 13, SCOR-agility + VaR to dept 10. Resolves the numbering collision (U11/risk #4). (accepted 2026-07-20)
- ADR-0030 — The workspace is a **tech-company operating model**: SCM is the read-only versioned **Global Context** (operating discipline + engineering practice, wiki premise + `docs/` SSOT preserved) that governs a **portfolio of Projects spanning all tech branches**; projects reference global nodes by stable ID + a local overlay, never mutate them. Extends ADR-0017/0021/0024/0026/0008. (Accepted — owner-directed 2026-07-22; A1 = SCM-as-operating-context, A2 = reference+overlay)
- ADR-0031 — A complementary **monitoring-connector** layer adds real-time project development/progress **Dashboards** and **Metrics** (metrics defined as `CPT-*` concept nodes); connectors unify external dev tools + internal project data, internal-first. Build deferred/reserved. (Accepted — owner-directed 2026-07-22; A3 = both, internal-first)
- ADR-0032 — **Prompt-refinement gate:** a user prompt is first improved, then the improved prompt is executed — the company's incoming-quality control on instructions (SCM incoming-inspection analogue). (Accepted — owner-directed 2026-07-22)
- ADR-0033 — **Exclusive technology lanes:** every technology owns exactly one responsibility and **no other technology may enter it** — Next.js presentation only · **NestJS is the sole technology the frontend talks to** · TypeScript owns business rules and **leaves the calculation lane** · **Rust joins Python** in calculation (Rust: exact arithmetic, hot path, ingestion; Python: models, statistics, optimization, ML). Rewrites `ENG-R8`; moves the money core to a single Rust implementation. (Accepted — owner-directed 2026-07-22)
- ADR-0034 — **Scale tier for monitoring:** **ClickHouse** owns analytics/time-series at scale (never the source of truth — rebuildable, one-way like ENG-R7) · **Docker** owns images · **Kubernetes** owns orchestration. Broker and cache stay gated on measured volume. (Accepted — owner-directed 2026-07-22)
- ADR-0035 — **Rust is the complete core; it replaces the TypeScript domain.** Business rules, invariants, state machines, exact arithmetic, the hot path and ingestion all move to Rust; **Python is the tools layer** (models, statistics, optimization, ML) reached over the schema-first gRPC contract; TypeScript survives **only inside NestJS and Next.js** as framework code, never as core logic. **Supersedes the TypeScript-domain clause of ADR-0001**, narrows ADR-0033. Migration is incremental (strangler), guarded by the U8 golden vectors. (Accepted — owner-directed 2026-07-22)
- ADR-0036 — **Telemetry data model at tens-of-thousands scale:** continuous project-supervision telemetry in ClickHouse — `(project_id, metric, ts)` sort key, monthly partitions, `Delta`+`ZSTD` / `Gorilla` codecs, `LowCardinality` labels, `AggregatingMergeTree` rollup cascade (raw→1m→1h→1d), short raw TTL with long rollup retention, batched async inserts from the Rust ingester. Resolves the L1 volume question. (Accepted — owner-directed 2026-07-22)
- ADR-0038 — **Improvement-recommendation gate:** every task carries a search for a better implementation *inside the existing lanes* — algorithmic cost, compute and memory, data-structure and boundary choice, clean code and structure, security. When a request lacks a detail whose absence would change what gets built, the detail is **never guessed and never asked in prose**: it is presented as a **selectable list of recommended options**, each naming its trade-off, recommendation first. Selected options are implemented in the same turn under the normal gates; declined ones are recorded with their reason so they are not re-proposed. **Adopting a new technology is out of scope by construction** — that remains ADR-0002/ENG-R8 and takes its own decision. Materializes as **PLT-R6**; extends PLT-R1 (ADR-0032) from refining the prompt to resolving what the prompt left open. (Accepted — owner-directed 2026-07-27)
- ADR-0039 — **A measurement-identity axis (`MSR-R*`):** arithmetic that constrains how a measure may be computed and aggregated, cited once instead of restated per department. Opens with **MSR-R1** (a ratio aggregates from its components — `Σnum ÷ Σden`, never the mean of ratios) and **MSR-R2** (a level is never summed; valid aggregations are last, max, min or time-weighted average). Both are identities, so both pass the inclusion test. Motivated by finding the same identities already scattered as QMS-R7, RSK-R5, PRC-R4, SPL-R5, WHS-R5 and ORD-R5 — each a special case restated for want of a general home. The department rules stay where they are. (Accepted — owner-directed 2026-08-01)
- ADR-0040 — **One long-lived line, named `main`, and nothing left hanging:** the integration model becomes **ENG-R11** — every pull request bases on `main`; a work branch is short-lived and restarted from `main` after each merge; a merged branch is deleted with the merge, because a branch with zero unmerged commits is a defect and not an archive; a turn ends with the pull request merged or with the reason written into its report; the base is current at merge time or the gate is re-run; and the merge is a **merge commit**, because G13 diffs `HEAD` against its parent and a squash would fail `updated:` on every file it carries. Resolves risk #3, open since 2026-07-19. (Accepted — owner-directed 2026-08-02)
- ADR-0041 — **A load set is priced as a whole, not document by document:** G9 has always budgeted single documents, but the long-context evidence is about **total input read together** — degradation is continuous rather than a cliff (Chroma, 18 frontier models), and past roughly half a full window the U-shaped position curve gives way to distance-from-the-end (Liu et al. 2024; Veseli et al. 2025). Load sets are declared in `docs/program/load-sets.md` and priced by gate **G14**, which fails over budget, fails on a member matching no file, and prints the largest set every run. Measured on adoption: `planning` reads **32,009 words (~42,571 tokens)**, 91 % of it the ADR index and `WORKFLOW.md` — the two largest documents in the repository, both loaded on every planning task, and **neither had a G9 budget** because none exists for `adr` or `program`. Budgets are a ratchet a few percent above measurement, and are this repository's engineering decision, not a number the research fixes. (Accepted — owner-directed 2026-08-02)
- ADR-0042 — **The gates are proven by mutation, on every merge:** improvement-register #12 already required that a gate be proven by planting a violation in the environment CI uses — and that proof had been performed exactly once, by hand, for G13. `verify.py` was 638 lines and thirteen gates over 230 documents with **zero tests**. `tools/test_gates.py` now plants one violation per gate and asserts the gate fires **and no other does**, end-to-end against a real worktree populated from the index, wired into `make verify-full`. It contradicted its own author on its first green run — a predicted G3→G5 collateral that does not happen — which is the argument for running mutants rather than reasoning about them. (Accepted — owner-directed 2026-08-02)
- ADR-0043 — **The premise is measured: a context-adherence evaluation, decided by programs.** Fifteen gates verified that the estate is internally consistent; none verified that an agent *reading* it complies. Five tasks — one per failure class with a real history here — are answered by a **cold subagent loaded only with the declared load set** (self-evaluation would measure the conversation, not the context), scored by **deterministic programs and never a judge model**, and recorded with a digest per context-defining file. Gate **G15** fails once any of those files changes after the measurement, and *notes that it cannot check* while none exists. Gates alone were rejected as the check surface: an invented threshold with correct front-matter and a cited source passes all fifteen — ADR-0037's defect exactly. (Accepted — owner-directed 2026-08-02, four options selected from a list per PLT-R6)
- ADR-0044 — **A fourth documentary form, `how-to`, and only about using this context:** against Diátaxis's four forms the estate had *reference* (182 concept nodes, 20 rule files) and *explanation* (the ADRs) and **no task-oriented document at all**, while `CLAUDE.md` promises a project learns "which departments it needs **and how to implement them**". The first eval run priced the gap: a node structurally perfect at **806 words against a 700-word budget it had read** — nothing missing from its inputs, no document turning the stated rule into an order of operations. **The scoping constraint is the whole decision:** a how-to about *running a department* would be method an organization can reasonably choose, so it fails the inclusion test — which is likely why the form was never created. The ones that belong are about the context itself. Verified by re-running the failing task: **633 words**, budget named in the answer. (Accepted — owner-directed 2026-08-03)
- ADR-0045 — **The Global Context has two axes, and no project uses all of it:** asked for a plain summary, the estate's weakest point turned out not to be rigour — `CLAUDE.md` named a supply-chain knowledge base *and* a DevOps dashboard and **never connected them**, leaving the reason buried in ADR-0030 among forty-four decisions. The model: supply chain is **how a company is run**, alongside **how software is engineered**, both serving a **portfolio of projects** inside this workspace and beyond, which the monitoring application watches so a company selling technology can decide from evidence. Three parts: the purpose stated at the entry point; **`practice-areas.md`** listing thirty-five engineering areas each with the external authority that would make a statement admissible — **roster, not content**, because W5 forbids speculative pre-build and the anchor is the thing that cannot be improvised later; and **PLT-R7**, governing knowledge is selected and **declared to the owner before development**. Verified by a cold subagent on the new `what-is-this-for` eval task: PASS. (Accepted — owner-directed 2026-08-03)
- ADR-0046 — **The context is versioned per node by digest, and tagged by calendar:** ADR-0030 promised a "versioned substrate" and ADR-0011 proposed SemVer tags; **zero tags existed** and this was the last open decision. SemVer is rejected on substance — a retired ID is never reassigned and stays listed (G11/G16), so every prior citation resolves and **the corpus cannot produce a breaking change by construction**, leaving the major component with nothing to encode. Instead: a **per-node `sha256:12`** recorded by the project (what it relied on, not which repo state — the mechanism G15 already proves) plus an annotated **`YYYY.MM`** tag as a legible human reference that claims nothing about compatibility. The declaration is the project's artefact and the form is `templates/knowledge-selection.md`, because PLT-R2 keeps project material out of the context — **so no gate here can check a project declared anything**, which is stated rather than hidden. Narrows ADR-0011. (Accepted — owner-directed 2026-08-03)
- ADR-0037 — **The Global Context holds only externally-fixed standards; the fictitious SCM application is retired.** The context is the source a project consults to learn *which departments it needs and how to implement them* — nothing more. It carries what a standards body, a regulator or an arithmetic identity fixes; it never carries what an organization chooses (thresholds, targets, weightings, rating bands, method mandates). Consequently **~25,700 lines of invented application code are deleted** (`packages/domain`, `services/calc`, `crates/scm-core`), concept nodes become **definitions without parameters**, and the **only application built here is the monitoring project**. Supersedes the two-language-SCM-application premise of ADR-0001; narrows ADR-0015 (nodes define, they do not own code) and ADR-0035 (the Rust core serves the monitoring platform, not 14 departments of invented rules). (Accepted — owner-directed 2026-07-27)

- ADR-0047 — **Money in the Rust core: integer minor units, exact decimal computation:** ADR-0019 decided "arbitrary-precision Decimal end-to-end" and named an estate — TypeScript `Money { amount: Decimal }`, Python `decimal`, `NUMERIC(19,4)`, gRPC strings — of which **nothing survives**; `crates/scm-money` instead represents money as `i64` minor units and uses `Decimal` as the computation medium, a reversal never recorded, so the accepted decision and the shipped code had disagreed since the crate was written. Separates the two roles: **representation** is integer minor units (`i64`, because a credit is a first-class value), **computation** is exact decimal quantizing once with `roundTiesToEven` (IEEE 754-2019 §4.3.3) through the single `MONEY_ROUNDING` constant, and apportionment is largest-remainder because its sum-preserving property is the identity **SCM-R14**. The precision gain over ADR-0019 is in the failure modes it left open: every operation total, a typed `MoneyError`, **overflow reported and never wrapped** (`checked_add`/`checked_sub`), a non-positive divisor refused rather than saturated. `tests/golden/money.golden.json` stays as the canonical-answer fixture a second implementation must read. Carries no policy, which is why it survived ADR-0037 — and should be deleted outright if monitoring never handles money. Open follow-up: a currency type instead of `String`, owned by the standards module. (Accepted — owner-directed 2026-08-03)

---

## ADR-0001 — Two-language split: TypeScript domain logic + Python analytics/ML

**Status:** **Superseded by ADR-0033/ADR-0035** (owner-directed 2026-08-03)

> **Both halves of the split are gone.** ADR-0035 moved the core to **Rust** — rules, invariants,
> exact arithmetic, the hot path, ingestion — and confined **TypeScript to NestJS and Next.js** plus
> the standards module, where it is no longer a lane owner. ADR-0033 fixed that as exclusive lanes
> (ENG-R8). Python survives as the **tools layer** (models, statistics, optimization, ML) and as this
> repository's gate scripts, not as "analytics" beside a TypeScript domain. ADR-0037 then deleted the
> domain logic this ADR was describing: two TypeScript files remain and they are reference data.

**Context:** The system needs both auditable business-rule logic (aggregates, validations,
state machines) and heavy mathematical/ML models (forecasting, optimization, deep
learning). One language serving both poorly fits either.

**Decision:** **TypeScript** owns all domain logic, aggregates and business rules
(`src/departments/`); **Python ≥ 3.11** owns all mathematical models, algorithms and ML
(`python/`), mirroring the same 14-department structure. Python type hints are mandatory.

**Evidence:** `CLAUDE.md` §Tech Stack; the parallel `src/departments/NN-*` and
`python/NN_*` trees.

**Consequences:** (+) each side uses its best ecosystem; the department key is the shared
spine. (−) two toolchains and duplicated domain constants to keep in sync (see the
cross-language consistency risk in `program/WORKFLOW.md`).

**Alternatives considered:** all-TypeScript (weak ML ecosystem); all-Python (weaker typing
discipline for domain aggregates at the time of adoption).

---

## ADR-0002 — OSI open-source-only dependency policy

**Status:** Accepted (retroactive)

**Context:** The repo must remain buildable and distributable without proprietary
services or non-OSI licenses.

**Decision:** Every dependency must carry an **OSI-approved license**. Proprietary SaaS
and source-available (SSPL/commercial) components are forbidden; each has a named OSI
substitute (registered in `00-governance/out-of-scope.md` #1–6). The license is verified
before adding any dependency.

**Evidence:** `CLAUDE.md` §Tech Stack (per-library license table + Prohibited list).

**Consequences:** (+) self-hostable, auditable stack; no vendor lock-in. (−) some
conveniences require assembling OSI parts.
**Note for review:** `ultralytics` (YOLOv8) is AGPL-3.0 — OSI-approved, but if this
product is ever distributed under a proprietary/commercial license, AGPL obligations must
be re-evaluated (a future ADR).

**Alternatives considered:** "best tool regardless of license" (rejected: lock-in +
redistribution risk).

---

## ADR-0003 — English-only for all repo artifacts

**Status:** Accepted (retroactive)

**Context:** The repo was partially written in Spanish; international standards, external
collaboration and consistency demand one working language.

**Decision:** All code, comments, docstrings, commit messages, READMEs and docs are
written in **English**. Existing Spanish content was migrated.

**Evidence:** `CLAUDE.md` §Language Policy; commits `737bf08` (translate all Spanish
READMEs), `7d0b75e` (enforce English-only policy).

**Consequences:** (+) one language across the estate; gate-checkable (G8). (−) one-time
migration cost (already paid).

---

## ADR-0004 — 14-department structure aligned to SCOR-DS

**Status:** Accepted (retroactive)

**Context:** The domain needs an organizing principle that scales and maps to how real
enterprises structure supply chains.

**Decision:** Organize the entire system into **14 numbered departments** (procurement …
supplier-development), each mapped to a SCOR-DS process (Plan/Source/Make/Deliver/Return/
Enable), replicated across `src/departments/`, `python/`, `.claude/skills/`. Department
keys are stable IDs (id-registry §4).

**Evidence:** `README.md` §Departmental Structure + §SCOR-DS Map; the three parallel trees.

**Consequences:** (+) every artifact has an obvious home; SCOR gives external validity.
(−) cross-department concerns need a declared shared home (`shared/`, `scm-core` rules).

**Alternatives considered:** layer-first organization (rejected: scatters domain
knowledge); ad-hoc module growth (rejected: no external grounding).

---

## ADR-0005 — Event-sourced inventory; state-based elsewhere

**Status:** **Superseded by ADR-0037** (owner-directed 2026-08-03)

> **A persistence choice for an application this repository no longer contains.** ADR-0037 deleted
> the invented estate and established that the context holds **no company's data** — so there is no
> inventory to source, event-wise or otherwise. Nothing here is retained as law: whether to
> event-source a store is exactly the kind of design decision a *project* makes and declares, and the
> context names the decision without answering it. The durable fragment ADR-0007 shared with it —
> that a financial record is corrected, never erased — lives on as **SCM-R3**.

**Context:** Inventory demands a tamper-evident audit trail (GAAP/IFRS IAS 2); most other
aggregates only need current state.

**Decision:** **Stock movements are an append-only event log**; current balances are
derived by replay (`projectStockBalance()`), never stored as mutable fields. Every
movement generates a double-entry GL journal mapping. Other departments persist
state-based aggregates.

**Evidence:** `src/departments/05-inventory-management/` (README + `StockMovement.ts`);
`CLAUDE.md` §Architecture (Event Sourcing + CQRS scoped to inventory movements).

**Consequences:** (+) complete auditability where it matters; no ES ceremony where it
does not. (−) replay cost management (snapshots) is a future concern.

**Alternatives considered:** full-estate Event Sourcing (rejected: unneeded complexity);
mutable stock balance column (rejected: no audit trail).

---

## ADR-0006 — Data conventions: integer-cent Money, ISO 8601/UTC, GS1 UOM, immutable SKU

**Status:** **Superseded** (owner-directed 2026-08-03) — clause by clause, below

> **Its four clauses went four different ways, which is why a single supersession note is the honest
> form and a partial one was not.**
>
> - **Money** → ADR-0019 replaced the integer-cent clause with Decimal-everywhere, and **ADR-0047**
>   has now replaced *that* for the Rust core: representation is integer minor units after all, with
>   exact decimal as the computation medium. The clause ends where it started and the route matters,
>   because ADR-0047 fixes the failure modes neither earlier statement addressed.
> - **ISO 8601 / UTC** → survives as **SCM-R9**, and is externally fixed, so it is law rather than
>   convention.
> - **GS1 / UN/ECE units** → survives as **SCM-R10**, likewise externally fixed. This is the clause
>   whose invented shorthand (`KG` for `KGM`) `CLAUDE.md` still names as an anti-pattern.
> - **Immutable SKU** → **retired, not inherited.** It was a sound data-modelling convention and a
>   convention is a choice; it left with **SCM-R11** under ADR-0037.

> **Superseded in part:** the integer-cent `Money` clause below is replaced by ADR-0019
> (arbitrary-precision Decimal). The other three conventions — ISO 8601/UTC dates, GS1
> UOM, immutable SKU — remain in force, unchanged.

**Decision:** `Money.amount` is always integer cents (no floats); dates ISO 8601 with UTC
timestamps; quantity UOM codes per GS1 (`shared/types.ts`); SKU codes immutable once
created (lifecycle via status flags ACTIVE/DISCONTINUED/BLOCKED).

**Evidence:** `CLAUDE.md` §Code Standards; `src/shared/types.ts`.

**Consequences:** (+) no floating-point money bugs; interoperable identifiers. (−) all
arithmetic must round at defined points. Now citable as SCM-R14..R11
(`30-foundation/scm-core/rule.md`).

---

## ADR-0007 — Soft-delete for financial records + idempotent inventory transactions

**Status:** **Superseded by ADR-0037** (owner-directed 2026-08-03)

> **One clause was law wearing an implementation's clothes; the other was the implementation.**
> The duty not to erase a financial record is real and externally grounded — retention under CSDDD
> (**SCM-R7**), and a record corrected rather than deleted (**SCM-R3**) — but *soft-delete* is one
> mechanism for it among several, and naming the mechanism as the decision is what made this ADR
> project policy. **Idempotent inventory transactions** went further: `SCM-R12` (an
> `idempotencyKey` on every transaction) was **retired** by ADR-0037 as belonging to the write path,
> i.e. the `ENG` family, not to supply-chain law. Retry safety is a project's engineering decision.

**Decision:** POs, invoices, stock movements, shipments and scorecards are **never
hard-deleted** (`isDeleted` flag); inventory transactions carry an `idempotencyKey` and
are safe to retry.

**Evidence:** `CLAUDE.md` §Critical Business Rules #3, §Code Standards.

**Consequences:** (+) audit integrity + safe retries. (−) queries must filter soft-deleted
rows. Citable as SCM-R3; retry safety is an engineering concern (`ENG-R*`).

---

## ADR-0008 — Standards & regulatory grounding as a first-class feature

**Status:** Accepted (retroactive)

**Context:** The product's differentiator is that KPIs, algorithms and compliance logic
are grounded in **named, versioned external standards**, not invented.

**Decision:** Every KPI/algorithm/compliance rule cites its standard (SCOR-DS, ISO
28000:2022, ISO 9001:2015, ISO 2859-1, GS1 v23, Incoterms® 2020, UN/EDIFACT) or
regulation (CSDDD, UFLPA, REACH, LkSG, EUDR, CBAM, Dodd-Frank §1502 …). The consolidated
reference is `docs/standards/REGULATORY_FRAMEWORK.md` (grandfathered home,
knowledge-architecture §3).

**Evidence:** `README.md` §Regulations/§References; commits `2035217`, `0e024ff`,
`087c351`; per-department IMPLEMENTATION.md headers.

**Consequences:** (+) externally defensible logic; clear update trigger when a standard
revs. (−) standards versions must be reviewed periodically.

---

## ADR-0009 — Testing stack: Jest (TS) + pytest (Python)

**Status:** **Superseded by ADR-0035/ADR-0037** (owner-directed 2026-08-03)

> **The stack went with the code it tested,** and the `Makefile` header says so in as many words.
> ADR-0037 deleted the application; ADR-0035 made **Rust the core**, so the tests that matter are
> `cargo test` (71 today) plus the doc gates, the gate mutation harness (ADR-0042) and the
> context-adherence checkers (ADR-0043). **TypeScript now lives only inside NestJS and Next.js** and
> the standards module, so its test framework is a decision that belongs with **M4**, when there is
> TypeScript worth testing — not a retroactive one to ratify now. The one cross-language artefact
> that survived is `tests/golden/money.golden.json`, kept for the reason ADR-0047 gives.

**Decision:** TypeScript tests run under **Jest** (`tests/unit`, `--runInBand`); Python
under **pytest**, with the stated goal that Python mirrors TS test coverage.

**Evidence:** `jest.config.js`, `package.json` scripts, `python/conftest.py`,
`CLAUDE.md` §Code Standards / §Testing Requirements.

**Consequences:** (+) standard runners per ecosystem. (−) coverage is currently far below
the stated bar (4 TS unit files; no Python test files) — tracked as a WORKFLOW gap, not
resolved by this ADR.

---

## ADR-0010 — Adopt the ugixio context skeleton (knowledge architecture + governance)

**Status:** Accepted (owner-authorized 2026-07-20)

**Context:** The repo had strong domain knowledge but no decision log, no stable rule
IDs, no tiered knowledge tree, no workflow/backlog, and knowledge lived scattered
(contract restates rules; no glossary home; no exclusions register).

**Decision:** Adopt the context skeleton (`context-template`): the tiered `docs/` tree,
the knowledge-architecture rules (SSOT, front-matter graph, append-only decisions, gates
G1–G8), the ID registry, the retroactive-ADR record, the program area (WORKFLOW,
operating model, templates), and the plan⇄context discipline (spec/model first, then
implementation). Existing knowledge homes stay where they are (allowlisted): department
README/IMPLEMENTATION files, `.claude/skills`, `docs/standards/`.

**Consequences:** (+) every future decision/rule has a home and an ID; drift becomes
detectable; the AI works from a bounded, layered context. (−) front-matter and registry
discipline on every new doc; a dedup pass on `CLAUDE.md` is now owed (WORKFLOW U3).

---

## ADR-0011 — Git discipline: Conventional Commits, SemVer tags, main always green

**Status:** Accepted (owner-authorized 2026-07-20) · **tag clause narrowed by ADR-0046**

**Context:** History mixes styles (`feat(wave-d): …` vs `Add … files`). No tags exist;
`package.json` says 1.0.0 with no tagged release. No branch protection convention is
recorded.

**Decision:** Conventional Commits with department/area scope; short branches
per unit of work merged green; annotated SemVer tags for demonstrable states; the default
branch always builds with green tests; secrets never committed.

> **The tag clause did not survive.** ADR-0046 rejects SemVer for this corpus on substance — a
> retired ID is never reassigned, so no citation can break and the major component has nothing to
> encode — and replaces it with a per-node digest plus a `YYYY.MM` calendar tag. Everything else in
> this decision stands, and ADR-0040 later gave the branch discipline its enforceable form (ENG-R11).

**Consequences:** (+) walkable history, releasable states. (−) requires consistency from
every contributor (including AI sessions).

---

## ADR-0012 — Context economics + executable gates (skeleton v0.2 mechanisms)

**Status:** Accepted (owner-authorized 2026-07-20)
**Extends:** ADR-0010

**Context:** The adoption (ADR-0010) landed the knowledge structure but left its
enforcement as prose, and four mechanisms that measurably shape AI output had no rule
here: models imitate concrete examples more reliably than they follow prose; adherence
degrades as always-loaded context grows (the ADR log grows without bound inside layer 1);
a correction not recorded where the next session loads it gets repeated; a slow gate
stops being run mid-task. Meanwhile the first real run of the toolchain (this unification)
found it had never worked: uninstallable dev dependencies, a tsconfig broken by the
department reorganization, all four test suites failing, and two genuine type bugs.

**Decision:**
1. **Executable gates.** `tools/verify.py` (Python 3 stdlib) implements doc gates G1–G7
   + G9 over the tracked tree; `make verify` (fast: doc gates + typecheck + unit tests,
   run after every layer) and `make verify-full` (merge/CI gate) are the only entry
   points; CI runs `make verify-full`.

   > **Both specifics have since moved, and the decision's shape has not.** The gate roster is now
   > **G1–G17** (each addition carries its own ADR and its own mutant, ADR-0042), and CI runs
   > **`make verify-full` *and* `make verify-schema`** — the split was forced by the telemetry
   > schema needing a real ClickHouse, and is recorded in WORKFLOW M2. What stands is the rule that
   > the Makefile targets are the *only* entry points and that CI runs what a developer runs.
2. **Context budgets — gate G9.** Always-loaded docs carry word budgets (CLAUDE.md 2600,
   shrinking with the U3 dedup; skills 1500; rules 1000; program protocol docs 1200).
   Layer 1 loads the **decision index** above; full ADR text on demand. G9 fails a
   budget overrun or a missing index line.
3. **Exemplar unit.** The first department completed to full satisfaction is declared
   the exemplar by an ADR naming it (candidate: `01-procurement`); siblings copy its
   shape. Always real code, never fabricated samples.
4. **Known pitfalls.** Each `.claude/skills/<dept>/SKILL.md` carries a "wrong → right"
   pitfall list; every owner correction lands one entry (operating-model §4.7). First
   entry: the SCM-R2 at-or-above boundary (procurement).
5. **New homes:** `program/evaluation.md` (reasoning + self-review),
   `00-governance/risk-register.md`, `program/improvement-register.md`,
   `program/templates/manifest.md`; communication contract as operating-model §4.
6. **Session handoff.** A 🟦 in-progress backlog entry always records current state +
   next step.

**Consequences:**
- (+) Governance is machine-enforced; the context the AI attends to stays small,
  concrete and self-correcting.
- (−) Python 3 becomes a dev requirement (already mandated by ADR-0001); budgets will
  eventually force tightening a doc — accepted, that pressure is the feature.

**Alternatives considered:** keeping gates as prose (the audit showed prose rules had
already silently rotted — the toolchain itself was broken); unbounded context growth
(silent degradation of rule adherence); a fictional exemplar (imitating fabricated
patterns misleads).

## ADR-0013 — npm is the single package manager; package-lock.json the only lockfile

**Status:** Superseded by ADR-0022
**Extends:** ADR-0001, ADR-0009

> **Superseded:** the monorepo build (ADR-0017) adopts pnpm workspaces + Turborepo
> (ADR-0022). ADR-0013's underlying requirement — one reproducible lockfile, CI installs
> from it — carries forward unchanged; only the tool changes (npm → pnpm,
> `package-lock.json` → `pnpm-lock.yaml`).

**Context:** `package.json` existed with no lockfile — builds were unreproducible — and
the declared dev tooling was mutually uninstallable (`eslint ^9` requires
`@typescript-eslint` v8; the repo pinned `^7`), proving no install had ever been
verified. The open-decisions backlog required picking a manager and committing its
lockfile.

**Decision:** npm (bundled with Node, no extra tooling) is the single package manager
for the TS ecosystem; `package-lock.json` is committed and is the only valid lockfile;
CI installs with `npm ci`. `@typescript-eslint/*` is bumped to `^8` to make the declared
toolchain installable. Python stays on `requirements.txt` (ADR-0001) until U7 revisits
its packaging.

**Consequences:**
- (+) Reproducible installs; CI possible; the ERESOLVE conflict cannot silently return.
- (−) npm is slower than pnpm/bun — accepted: zero extra tooling wins for a repo with no
  deployment story yet (open decision).

**Alternatives considered:** pnpm (faster, but adds a tool and a different lockfile for
no current need); yarn (same, plus version-family fragmentation); leaving it open (the
reproducibility gap already bit — see improvement register #2).

## ADR-0014 — The repository is licensed MIT

**Status:** Accepted
**Extends:** ADR-0002

**Context:** `package.json` has declared `"license": "MIT"` since the repo's creation,
but no LICENSE file existed — the declaration was legally ineffective (open decision
"Repository LICENSE file"; backlog U5). The owner instructed adding the license file.

**Decision:** A standard MIT LICENSE file (copyright ugixio) is committed at the repo
root, matching the existing `package.json` declaration.

**Consequences:**
- (+) The declared license is now effective; contributions and reuse have clear terms.
- (−) MIT permits proprietary reuse by third parties — accepted (it was already the
  declared intent).
- ADR-0002's note stands: `ultralytics` (AGPL-3.0, Python requirements) imposes no
  obligation on this open-source distribution, but any future proprietary/commercial
  distribution must re-evaluate AGPL obligations in a superseding ADR.

**Alternatives considered:** Apache-2.0 (adds an explicit patent grant, but contradicts
the long-standing MIT declaration and no patent concern was raised); leaving it absent
(the gap already existed and blocked nothing except legal clarity — rejected as it makes
every fork's status ambiguous).

---

## Open decisions (starter backlog — each answer becomes an ADR)

- [x] **Runtime & persistence architecture.** ~~Per-department `schema.sql` files exist but no
      engine choice, migration runner or application layer is recorded.~~ **Answered, and the
      question dissolved with its premise.** Those `schema.sql` files were deleted by ADR-0037
      along with the domain logic they stored: this repository executes no supply-chain logic, so
      there is nothing to persist for a department. What *is* recorded, for the one application
      built here: PostgreSQL owns transactional truth and ClickHouse owns telemetry at scale and
      never truth (**ADR-0033/0034**), the telemetry schema and its forward-only migration runner
      are **ADR-0036** (`db/clickhouse/`), and the lane map is **ENG-R8**.
- [x] **API/product surface.** ~~Library? Service? UI? Nothing is recorded.~~ **Recorded:** the
      context is consumed as a read-only versioned substrate (**ADR-0030**), and the one
      application is monitoring — NestJS + GraphQL as the only counterpart the frontend has, with
      Next.js above it (**ADR-0031/0034/0036**, **ENG-R8**).
- [x] **Package manager + lockfile.** → **ADR-0013** (npm + `package-lock.json`).
- [x] **Repository LICENSE file.** → **ADR-0014** (MIT, matching `package.json`; the
      AGPL note in ADR-0002 re-applies only on future commercial distribution).
- [x] **CI + verify green-gate.** → **ADR-0012** (`make verify` / `make verify-full`, CI
      workflow). The gate set has grown since: G1–G13, plus `make verify-schema` against a real
      ClickHouse. The two items still listed as pending inside it were triaged on 2026-07-29 —
      the pytest gate is void (its code is deleted) and eslint waits for the Phase M4 TypeScript
      (`program/WORKFLOW.md` §Triage).
- [x] **Versioning scheme.** ~~First annotated tag; what 1.0.0 means (ADR-0011 pending).~~ → **ADR-0046**: per-node content digest for the machine, calendar tag for the human. **SemVer was rejected on a substantive ground, not a stylistic one** — a retired rule ID is never reassigned and stays listed, so every old citation still resolves and the corpus cannot produce a breaking change by construction; the major component would never legitimately increment. **This was the last open decision in this index.**
- [x] **Agent lanes.** ~~Formalize WHAT/HOW/SPECIALTY lanes and profiles or keep
      single-orchestrator mode.~~ **Resolved by ADR-0027** (2026-07-20): formalized — 7
      least-privilege agent profiles + 7 technology skills; main session orchestrates.
- [x] **Cross-language consistency policy.** ~~TS and Python implement overlapping formulas;
      decide the single-source mechanism.~~ **Answered twice over.** The mechanism was chosen and
      built — shared golden vectors (`tests/golden/money.golden.json`, U8) — and then the problem
      was removed at the root: ADR-0037 left one implementation of anything exact, in Rust. The
      concept nodes did the work they were added for first, though: the census surfaced seven
      divergences, including the `CPT-0003` z-score tables, and ADR-0028 settled which side was
      right by making the exact statement canonical and neither implementation authoritative.

---

## ADR-0029 — Dissolve the misplaced order-management calc directory

**Status:** Accepted (owner-authorized 2026-07-20)
**Extends:** ADR-0004
**Resolves:** U11 / risk register #4

**Context:** `services/calc/07_order_management/` is triply wrong: numbered 07 (which is
logistics-transportation), named order-management (dept 13), and its contents mix two
concerns — `perfect_order_index` / `poi_gap_analysis` / `PerfectOrderResult` (order
metrics, SCOR RL) and `upside_supply_flexibility` / `downside_supply_adaptability` /
`overall_value_at_risk` (SCOR Agility AG.1/AG.2 + Value-at-Risk — risk, dept 10). The
census (G10 `DEPT_NUMBER`) miscounts all six symbols under dept 07. Nothing imports the
module (verified) and there are no name collisions with the destinations.

**Decision:** The directory is dissolved and its symbols return to the departments that own
their concepts:
- **Perfect-order metrics → dept 13** (`13_order_management`).
- **SCOR-agility + VaR → dept 10** (`10_risk_management`).

**Execution note (environment constraint):** this repo's local environment has no
numpy/scipy, so Python cannot be executed here and a surgical 3-way function split cannot
be pytest-verified in place. The **collision is fixed now** by relocating the whole module
into the correct department namespace (a git mv, which the doc-gate census verifies);
the finer split of the three agility/VaR functions into dept 10 is a **tracked refinement**
(U11 stays open at that granularity, now blocked only on a Python environment), not a
silent omission.

**Consequences:** (+) the numbering collision that skewed the census is gone; the symbols
count under a correct department. (+) nothing broke — no importers, no collisions. (−) until
the refinement lands, three risk/agility functions sit in the order-management module;
recorded, not hidden. (−) pytest verification of the moved module awaits a Python env (risk
#1/#6 — the standing Python-toolchain gap).

**Alternatives considered:** *Surgical 3-way split now* — correct taxonomy but ships
untested Python across three files in an environment that cannot run it; rejected as
unverifiable. *Leave it* — rejected: the census miscount is a live defect and the owner
asked to resolve it.

---

## ADR-0028 — Canonical service-level z-score is the exact inverse-normal

**Status:** Accepted (owner-authorized 2026-07-20)
**Extends:** ADR-0001, ADR-0016
**Resolves:** U15

**Context:** Three definitions of the service-level z-score coexist (recorded in CPT-0003):
the department business-context document specifies `z = scipy.stats.norm.ppf(SL)` (the
exact inverse standard-normal CDF); the Python implementation uses an 8-point lookup table
+ linear interpolation; the TypeScript implementation uses a different, coarser table. They
disagree — Python overshoots the exact value by up to +1.57% at interpolated service levels
(convexity of Φ⁻¹). z feeds safety stock across demand-planning, inventory and finance, so
the divergence is cross-department.

**Decision:** The **canonical z-score is the exact inverse standard-normal CDF** Φ⁻¹(SL),
the value the business-context document already specifies (ADR-0016 makes its *formulas*
authoritative even though its *stack* is not):
- **Python:** `scipy.stats.norm.ppf(service_level)` — `scipy` is already a declared
  dependency; the lookup table + `np.interp` are retired.
- **TypeScript:** a high-accuracy rational approximation of Φ⁻¹ (Acklam's algorithm,
  absolute error < 1.15e-9 over the open interval) — the standard library has no inverse
  normal; the lookup table is retired.
- **Consistency:** the shared golden vectors (U8) assert TS ≈ Python to a tolerance of
  1e-6 (both approximate the same exact function; the residual is far below one unit of
  safety stock).
- **Scale:** service level is a fraction in (0,1) everywhere (Python's convention); the TS
  percent input is normalized at the boundary.

**Execution note (environment constraint):** the decision is recorded now; the code change
(TS `getZScore` → Acklam, Python `get_z_score` → `norm.ppf`, updated safety-stock test
expectations, golden vectors) is a **bounded follow-up** (P-lane), because it shifts
existing asserted safety-stock values (e.g. 1.65 → 1.6449) and the Python side cannot be
run/verified in this environment. CPT-0003 is updated to state the resolved canonical.

**Consequences:** (+) one exact, defensible definition; the cross-department divergence has
an answer; no third variant survives. (+) exactness at every service level, not just the
tabulated ones. (−) a code migration touching both languages + tests (tracked); slightly
different safety-stock numbers than today (more correct). (−) TS gains a small numerical
routine (Acklam) to maintain — justified: the alternative is an inexact table.

**Alternatives considered:** *Standardize on one shared lookup table* — simpler but keeps a
tabulated approximation with interpolation error; rejected in favour of the exact function
the spec already names. *Keep tables, just align them* — rejected: still inexact, and it
preserves two maintenance points instead of one formula.

---

## ADR-0027 — The agent layer is formalized (WHAT/HOW/SPECIALTY, least privilege)

**Status:** Accepted (owner-authorized 2026-07-20)
**Extends:** ADR-0010, ADR-0012, ADR-0018, ADR-0021
**Resolves:** open decision "Agent lanes"

**Context:** The operating model (ADR-0010, `operating-model.md` §1) reserves a second
knowledge layer — the **agent profile** — as "not yet formalized", and the lanes
(WHAT/HOW/SPECIALTY, §2) are a "default pending the owner's decision". The product is now a
multi-technology build (Next.js · NestJS/GraphQL · PostgreSQL · Python/gRPC), and the owner
asked for a real, justified set of agents that understand the full context, carry the
technology skills, and work together. Building this must not create a second knowledge root
(ADR-0021) nor restate the protocols the repo already owns (`evaluation.md`,
`operating-model.md` §4).

**Decision:** Formalize the agent layer as **7 subagent profiles** in `.claude/agents/`
(allowlisted tooling) plus **7 technology/practice skills** in `.claude/skills/` (parallel
to the 15 domain skills, which stay the WHAT-lane area layer). The **main Claude Code
session is the orchestrator** — it decomposes, assigns and gates; there is no orchestrator
agent (that would duplicate the coordinating thread).

Every profile follows `templates/agent.md` and obeys three non-negotiables:
1. **References, never restates.** A profile cites `CLAUDE.md`, the ADR index, the relevant
   `rule.md`/`CPT` nodes, `evaluation.md` (reasoning protocol, decision ladder) and
   `operating-model.md` §4 (communication contract). It copies none of them.
2. **Least privilege (secure-by-default, PoLP).** Each agent declares the narrowest tool
   set for its job. The critic (quality-reviewer) has **no write access** — the
   generator/critic separation is deliberate.
3. **Lane boundary.** Each agent names, explicitly, the work it never does (the other
   lanes'), per the template's "What I NEVER do".

Roster (each justified by a distinct lane role or technology surface — per-node
justification, knowledge-architecture §1):

| Agent | Lane | Owns | Never |
|---|---|---|---|
| `architect` | WHAT/plan | ADRs, specs, decomposition, design | writes app code |
| `domain-knowledge` | WHAT | `docs/25-concepts` (CPT), `rule.md`, extraction (ADR-0016) | writes app code / invents business rules from thin air |
| `backend-engineer` | HOW | `apps/api`, `packages/{application,infrastructure}` (NestJS, code-first GraphQL, Clean Arch) | changes the domain ring / frontend |
| `frontend-engineer` | HOW | `apps/web` (Next.js, the octagon graph, a11y) | backend/domain logic |
| `data-engineer` | HOW | Postgres schema, migrations, the read-model ingester (ADR-0024) | business rules / UI |
| `calc-engineer` | HOW/SPECIALTY | `services/calc` (Python, Decimal precision, gRPC/proto) | TS domain / business-rule decisions |
| `quality-reviewer` | verify | gates, `evaluation.md` self-review, security, cross-language golden vectors | writes/edits code (read-only critic) |

The reasoning techniques encoded across the profiles are the **proven** ones, and they are
the repo's existing protocols made explicit for agents: read-before-write (context loading,
`operating-model.md` §1), plan⇄context check (ADR-0010), plan→act→verify with a gate after
every layer (ADR-0012), test-first with a test per rule ID (SCM-R13), decision ladder
(`evaluation.md` §2), generator/critic separation (quality-reviewer), grounding/citation
(conversation is never the source of truth), explicit-uncertainty reporting
(`operating-model.md` §4), and known-pitfalls memory (§4.7).

**Consequences:** (+) parallelizable, role-scoped work with hard boundaries; each agent
loads a small, correct context instead of the whole repo; the critic is independent of the
author. (+) the technology skills give every HOW agent the stack's best practices without
copying them into each profile. (−) a roster to maintain as the stack evolves; mitigated by
`templates/agent.md` and by keeping practice in skills (one home), identity in profiles. (−)
agent profiles are `.claude/` tooling (allowlisted, ungated) — drift risk; mitigated by the
"references, never restates" rule so the gated docs stay the source.

**Alternatives considered:** *Keep single-orchestrator mode* — simplest, but forfeits
parallelism and the critic-separation benefit the owner explicitly asked for. *One agent per
department (14+)* — rejected: the 15 domain skills already carry department specificity;
agents are role/technology-scoped and load the relevant domain skill, avoiding 14× profile
duplication. *Fold review into each engineer* — rejected: self-review by the author is
weaker than an independent critic (the separation is the point).

---

## ADR-0026 — The wiki front end is an octagon node-graph

**Status:** Accepted (owner-authorized 2026-07-20)
**Extends:** ADR-0017, ADR-0015

**Context:** Stage A's front end (Next.js) visualizes the governed knowledge graph. The
owner specified the visual language: Supply Chain Management at the centre, the 14
departments arranged around it as a connected circuit, each department expanding into its
concept sub-nodes (the `CPT-*` catalogue); every node an **octagon** drawn as an outline
only — no fill — with **LED cyan** strokes on a transparent/dark background, as if the
nodes were glowing cores; a click on any node opens a **right-hand sidebar** with that
node's detail.

**Decision:** The front end is a three-tier node-graph:
- **Core node** — "Supply Chain Management", centre.
- **Department nodes** — the 14 departments, placed radially and connected to the core and
  to each other as a circuit (edges follow the SCOR-DS process flow where one exists).
- **Concept sub-nodes** — a department expands to reveal its `CPT-*` nodes; these are the
  leaves the sidebar renders in full (formula, units, worked example, links).

Visual spec (the seed for a future `50-engineering/frontend/` token set):
- Octagon geometry, **stroke only**, no background fill; stroke = LED cyan
  (`#22d3ee`-family), with a soft outer glow; page background transparent over a dark base.
- Interaction states — idle / hover (brighter stroke + glow) / selected (filled stroke
  weight, persistent glow) / dimmed (non-neighbours fade when one node is focused).
- **Sidebar** slides in from the right; renders the selected node's content from the
  GraphQL read model (ADR-0024/0025); closes without losing graph state.
- **Accessibility:** the graph is keyboard-navigable (tab/arrows between nodes, Enter to
  open), every node has an accessible name and role, focus states meet WCAG contrast, and
  the cyan-on-dark palette is checked for contrast (the glow is decorative, never the only
  affordance). A reduced-motion setting disables the glow pulse. Light and dark themes both
  supported (the transparent-fill octagon reads on both).

**Consequences:** (+) a distinctive, legible entry surface that mirrors the graph the
gates already validate — the visual is a view of real governed data, not a mock. (−) an
outline-glow aesthetic needs care to stay accessible (contrast, motion, keyboard); the
a11y clauses above are load-bearing, not optional. (−) radial circuit layout for 14 + N
nodes needs a real layout strategy (force-directed or fixed radial) — a P4 design task.

**Alternatives considered:** *Conventional sidebar tree / list* — accessible and trivial,
but discards the graph structure that is the point. *Filled cards* — easier contrast but
not the specified visual language. The octagon-outline node-graph is the owner's explicit
choice; this ADR fixes its accessibility floor so the aesthetic cannot regress usability.

---

## ADR-0025 — GraphQL is code-first

**Status:** Accepted (owner-authorized 2026-07-20)
**Extends:** ADR-0018

**Context:** `apps/api` (NestJS) exposes the domain and, in Stage A, the knowledge graph
over GraphQL. NestJS supports two modes: code-first (TS classes + decorators generate the
SDL) and schema-first (hand-written SDL generates TS types).

**Decision:** **Code-first.** Resolvers, object types and inputs are TS classes decorated
with `@ObjectType`/`@Field`/`@Resolver`; NestJS emits `schema.gql` as a **build artifact**,
committed for review and contract tests but never hand-edited. Types live once, beside the
use-cases they serve (Clean Architecture interface-adapters ring, ADR-0018).

**Consequences:** (+) one source for type and schema — no TS/SDL drift; refactors are
type-checked end to end; fastest path in the NestJS idiom (convention over configuration).
(−) the SDL is generated, so a pure schema-review workflow reads an artifact rather than an
authored file — mitigated by committing `schema.gql` and diffing it in CI. (−) very complex
federated schemas are sometimes clearer schema-first — not this surface.

**Alternatives considered:** *Schema-first* — the SDL is an explicit, reviewable contract
(the prompt's "API first"), but it duplicates every type as hand-maintained SDL + generated
TS, reintroducing exactly the two-places-to-sync problem the estate keeps eliminating.

---

## ADR-0024 — The knowledge graph is served from a one-way Postgres read model

**Status:** Accepted (owner-authorized 2026-07-20)
**Extends:** ADR-0015, ADR-0017

**Context:** Stage A (ADR-0017) is a read-only wiki over the governed knowledge graph
(`docs/25-concepts`, `rule.md`, `40-contexts`). The owner chose to serve it from PostgreSQL
rather than parse markdown per request. This risks a **second source of truth** — a
database copy that drifts from `docs/`, which knowledge-architecture §1/§4 forbid.

**Decision:** Postgres holds a **projection**, not a source. The invariants:
1. **`docs/` remains the single source of truth.** The gates (G1–G10) run on `docs/`, never
   on the database.
2. **Ingestion is one-way and rebuildable.** A build step (`tools/ingest` / a workspace
   task) reads the governed files and (re)populates the read-model tables. The tables are
   dropped-and-rebuilt, never hand-edited; by construction they cannot diverge.
3. **The read model is disposable.** It carries only what the wiki renders (node id, type,
   title, body, edges) — no authored content originates there.
4. **A drift guard** (future gate G11, backlog) asserts the ingested node/edge counts match
   what the gates see in `docs/`, failing CI if an ingestion is stale.

**Consequences:** (+) fast queries, full-text search, and the same Postgres that Stage C
will need for transactional data — introduced once. (+) SSOT preserved by making the DB a
derivative that is rebuilt, not maintained. (−) an ingestion step to build and keep in the
pipeline; (−) until G11 lands, staleness is caught by rebuild discipline, not mechanically.

**Alternatives considered:** *Resolver parses `docs/` in memory per request* — simplest and
SSOT-trivial, but forecloses the Postgres that Stage C needs and scales poorly for search;
rejected by the owner in favour of introducing the database once. *Author content in
Postgres, generate docs from it* — inverts the SSOT the whole governance model rests on;
rejected outright.

---

## ADR-0023 — Monorepo structure: Clean-Architecture layers as packages

**Status:** Accepted (owner-authorized 2026-07-20)
**Extends:** ADR-0018, ADR-0022

**Context:** ADR-0018 chose Clean Architecture as a modular monolith. Two organizing axes
are possible — by **layer** (domain/application/infrastructure) or by **feature**
(department). The owner chose layers-as-packages. Left unstated, "layers as packages" and
"one module per department" read as a contradiction; this ADR reconciles them.

**Decision:** The repository is a pnpm/Turbo monorepo (ADR-0022) laid out as:
```
apps/
  web/            Next.js — the octagon node-graph wiki (Stage A)
  api/            NestJS + GraphQL (code-first, ADR-0025); ONE module per department
packages/
  domain/         entities — today's src/departments/*, unchanged, the innermost ring
  application/    use-cases + ports, organized by department inside
  infrastructure/ repository impls, event-store adapter, gRPC client, persistence
  shared/         Money, events, cross-cutting types — today's src/shared
services/
  calc/           Python gRPC calculation core — today's python/
proto/            scm.calc.v1 contracts (ADR-0020)
docs/  tools/  .claude/    UNCHANGED — repo-wide governance stays at root
```
**Reconciliation of the two axes:** the **packages are horizontal layers**, and inside each
package the code is **organized by department** (`packages/application/src/03-demand-planning/…`).
The **modular-monolith boundary lives at `apps/api`**: one NestJS module per department wires
that department's use-cases. So Clean-Architecture rings are the *package* structure;
department modularity is the *composition* structure. Cross-department calls go through
published application ports, never into another department's domain.

The dependency rule is enforced, not just documented (backlog P1, `ENG-*` rules): allowed
direction is `apps → infrastructure → application → domain`; `domain` imports nothing;
`shared` is imported by all and imports nothing. A boundary linter (dependency-cruiser or
eslint-plugin-boundaries) fails a violating import.

**Consequences:** (+) faithful to ADR-0018's dependency rule; the domain package needs zero
change; the seam to split into services later (Stage C) is the package boundary. (−) more
packages to wire than a flat layout, and use-cases for one department are split across two
packages (domain vs application) — the cost of the layered axis, accepted for its
enforceable dependency direction.

**Alternatives considered:** *Feature-vertical (one package per department, all layers
inside)* — strongest boundaries but 14× the package boilerplate on day one; the layered axis
was chosen. *Flat `src/` with folders* — the status quo; cannot express or enforce the ring
dependency rule.

---

## ADR-0022 — pnpm + Turborepo is the monorepo toolchain

**Status:** Accepted (owner-authorized 2026-07-20)
**Supersedes:** ADR-0013
**Extends:** ADR-0017

**Context:** Building a multi-workspace product (web, api, packages, python service) needs a
workspace-aware toolchain. ADR-0013 fixed npm + `package-lock.json` for a single-package
library; that constraint no longer fits.

**Decision:** **pnpm** manages workspaces and dependencies; **Turborepo** orchestrates and
caches tasks across them. `pnpm-workspace.yaml` declares the workspaces; `pnpm-lock.yaml`
is the single lockfile (replacing `package-lock.json`); CI installs with
`pnpm install --frozen-lockfile`. `make verify-full` delegates cross-workspace build/test to
`turbo run`. The Python service (`services/calc`) keeps `requirements.txt` (ADR-0001).

**Consequences:** (+) content-addressed store (fast, disk-efficient), strict dependency
isolation (no phantom deps), and Turbo's cached task graph keep the growing monorepo fast.
(−) supersedes ADR-0013 — a lockfile migration and a one-line CI change; (−) contributors
need pnpm installed (via corepack, bundled with Node 22 — low friction).

**Alternatives considered:** *npm workspaces (+ Turbo)* — keeps ADR-0013 intact and is
simpler, but pnpm's stricter isolation and store efficiency were preferred for a monorepo
expected to grow through Stages B/C. *Nx* — more powerful (generators, project graph) but
heavier configuration than this stage warrants. The lockfile/CI change is the only cost of
superseding ADR-0013; its reproducibility requirement is preserved.

---

## ADR-0021 — Context Engineering is mapped onto the existing tree, not rebuilt

**Status:** Accepted (owner-authorized 2026-07-20)
**Extends:** ADR-0010, ADR-0012

**Context:** An enterprise "Context Engineering integration" prompt asked for ~30 context
types (Identity, Roles, Rules, Knowledge, Decisions, Planning, Evaluation, Quality,
Memory, Governance, Continuous Improvement, …). Building these as a new subsystem would
create a **second knowledge root**, which knowledge-architecture §1 forbids ("there are no
parallel or competing knowledge roots").

**Decision:** The context system is **already instantiated** by this repo and is mapped,
not rebuilt. The mapping is the authority:

| Prompt context | Existing home |
|---|---|
| Identity · Roles · AI behaviour | `CLAUDE.md`; `.claude/skills/*/SKILL.md` (area-skill layer) |
| Objective · Planning | `docs/program/WORKFLOW.md` (backlog); `templates/task.md` |
| Knowledge | the tier tree `docs/` (contract→decisions→product-model→concepts→foundation→contexts) |
| Rules · Constraints | `rule.md` (SCM-R*/dept families); `out-of-scope.md` |
| Decisions · Reasoning | `10-decisions/README.md`; `docs/program/evaluation.md` (decision ladder) |
| Evaluation · Quality | `tools/verify.py` gates G1–G10; `evaluation.md` §3 self-review |
| Memory | `.claude/…/memory/` + `MEMORY.md` index |
| Governance · Risk · Continuous Improvement | `00-governance/`; `risk-register.md`; `improvement-register.md` |

Genuine gaps this ADR opens as backlog (not new roots — new tiers/nodes in the existing
tree): a `50-engineering/` tier (materialized when app code lands, per the reserved slot);
per-layer engineering rules (`ENG-*` family); an ADR for the frontend node-graph UX.

**Consequences:** (+) no duplication; the prompt's requirements become a coverage
checklist against a system that already passes its own gates. (−) the answer to "build
context engineering" is partly "it exists" — deliberately, and evidenced by the map above.

**Alternatives considered:** *Build a parallel `/context` tree* — rejected: violates §1
and the SSOT principle; would immediately drift from `docs/`.

---

## ADR-0020 — The Python calculation core is a gRPC service

**Status:** Accepted (owner-authorized 2026-07-20)
**Extends:** ADR-0001, ADR-0019

**Context:** ADR-0001 puts all math in Python; the app is TypeScript (NestJS). The two must
talk, and the payloads are **financial** — serialization must not lose precision (ADR-0019).

**Decision:** Python exposes the calculation core as a **gRPC service** with a protobuf
contract in `proto/`. NestJS is the client. **All monetary and rate values cross the wire
as `string`, not `double`** — protobuf's `double` is IEEE-754 and would reintroduce the
float error ADR-0019 exists to eliminate. Each RPC is stateless and idempotent; the
contract is versioned (`scm.calc.v1`).

**Consequences:** (+) strong typed contract, binary efficiency, independent scaling and
testing of the calc core, language boundary that matches the ADR-0001 split. (+) string
decimals keep end-to-end exactness. (−) two deployables, protobuf tooling, harder ad-hoc
debugging than JSON.

**Alternatives considered:** *REST/JSON (FastAPI)* — simpler and more debuggable, but
weaker contract and JSON numbers are doubles (precision risk unless also stringified);
viable fallback if gRPC tooling proves heavy. *Python subprocess from Node* — poor fault
isolation, per-call startup cost, no horizontal scaling. *Precompute to Postgres* —
rejected: forecloses the interactive-calculator stage of ADR-0017.

---

## ADR-0019 — Money is arbitrary-precision Decimal end-to-end

**Status:** Accepted (owner-authorized 2026-07-20)
**Supersedes (in part):** ADR-0006 (its integer-cent Money clause only)
**Rewrites:** SCM-R14

**Context:** Three incompatible money representations coexist: `Money.amount: number`
(integer cents, SCM-R14), Python `float64` (numpy), and `NUMERIC` in `schema.sql`. Worse,
`multiplyMoney` computes `Math.round(m.amount * factor)` — a float multiply **before**
rounding — so landed-cost allocation, FX and tax already lose exactness. The owner
requires exact financial precision and the product will carry FX, duties and pro-rata
allocations, where integer cents force lossy division. `decimal.js` is already a declared
dependency, unused.

**Decision:** One representation, arbitrary-precision **Decimal**, everywhere:
- TypeScript: `decimal.js` (already in `package.json`); `Money` becomes
  `{ amount: Decimal, currency: string }`.
- Python: `decimal.Decimal` with an explicit `Context` (precision, `ROUND_HALF_EVEN`); the
  numpy `float` path is barred for money (analytics on quantities may stay float).
- PostgreSQL: `NUMERIC(19,4)` for amounts, higher scale for rates.
- Across gRPC: **string**, never `double` (ADR-0020).
- **Rounding is explicit and banker's (`ROUND_HALF_EVEN`)** at defined boundaries
  (persistence, display, allocation remainder), never implicit.

**SCM-R14 is rewritten** from "Money is integer cents" to "Money is arbitrary-precision
Decimal; float money arithmetic is forbidden; rounding is explicit `ROUND_HALF_EVEN` at
defined boundaries." The rule ID is retained (append-only registry); its 8 department
citations reference it by ID and stay valid.

**Consequences:** (+) exactness across multiply, divide, FX, tax and allocation — the
owner's hard requirement. (+) retires a live float-precision bug. (−) touches every
monetary code path in `src/` and `python/`; a migration with tests (backlog). (−) Decimal
is slower than integer add — irrelevant at this domain's volumes. (−) supersedes an
accepted retroactive ADR, so ADR-0006's other clauses (ISO 8601, GS1 UOM, immutable SKU)
must be explicitly retained — they are, unchanged.

**Alternatives considered:** *Keep integer cents (bigint)* — exact for add/subtract but
forces rounding rules on every division and reparto; awkward for rates/tax; retains the
representation mismatch with `NUMERIC`. *Hybrid cents+Decimal* — mirrors real ERP systems
but multiplies conversion boundaries, each a reinjection point for the very bug being
removed. Decimal-everywhere is the single-source-of-truth choice.

---

## ADR-0018 — Clean Architecture as a modular monolith

**Status:** Accepted (owner-authorized 2026-07-20)
**Extends:** ADR-0004, ADR-0005

**Context:** The repo is a domain library — only `domain/` layers exist, no application,
infrastructure or delivery layer, and `EventStore` is an in-memory array. Building a
full-stack product needs delivery (GraphQL), persistence (Postgres) and the Python
boundary added **without rewriting** the standards-anchored domain, which is a genuine
asset precisely because it depends on no framework.

**Decision:** **Clean Architecture**, dependencies pointing inward:
```
frameworks/drivers   NestJS · GraphQL · TypeORM/Prisma · gRPC client · Next.js
interface-adapters   controllers · resolvers · repository impls · presenters · mappers
use-cases            application services (one per operation), orchestration, ports
entities             src/departments/*/domain  ← preserved as-is, the innermost ring
```
Deployed as a **modular monolith**: one NestJS module per department (14), each owning its
bounded context, talking across modules only through published application ports — never
by reaching into another module's domain. This keeps a clean seam to split into services
later (ADR-0017's transactional stage) without committing to microservices now.

**Consequences:** (+) the domain stays the dependency sink and needs no change; testability
by ring; a deployment simple to run and later simple to split. (−) more ceremony than the
current flat layout — explicit use-case classes and ports; justified by the app surface
now being real. (−) the in-memory `EventStore` becomes an infrastructure adapter over a
Postgres event table (ADR-0005 finally realized in durable form).

**Alternatives considered:** *Hexagonal/Onion* — same dependency-inversion core; Clean was
chosen for its prescriptive use-case ring, which suits a team-scale codebase. *Vertical
Slice* — great DX but cross-cuts the established 14-department structure (ADR-0004).
*Microservices now* — premature; operational cost with no scaling need yet. The modular
monolith is the reversible middle.

---

## ADR-0017 — The product is a staged full-stack SCM application

**Status:** Accepted (owner-authorized 2026-07-20)
**Extends:** ADR-0004

**Context:** The repo has been a domain/analytics library. The owner's target is a
full-stack SCM system whose entry surface is a **node-graph wiki**: Supply Chain Management
at the centre, the 14 departments as connected nodes, each expanding into its concept
sub-nodes (the `CPT-*` catalogue), rendered as octagonal "core" outlines in LED cyan on a
transparent background, a node click opening a right-hand sidebar. Stack: **Next.js**
(frontend), **NestJS + GraphQL** (backend), **PostgreSQL** (data), **Python** (calculations).

**Decision:** Build in stages, each shippable, without breaking existing functionality:
- **Stage A — Wiki of concepts (now).** Read-only. GraphQL serves the governed knowledge
  graph (`docs/25-concepts` + department/rule nodes) to the Next.js octagon UI. Python
  renders the worked examples already documented. **No transactional persistence, no auth
  beyond read access.** This is the only stage authorized to start.
- **Stage B — Interactive calculator.** The user supplies inputs; the Python core computes
  live over gRPC (ADR-0020) with exact Decimal (ADR-0019). Still no business persistence.
- **Stage C — Transactional SCM.** The `src/departments` domain is wired through Clean
  Architecture (ADR-0018) to durable event-sourced Postgres, with auth/RBAC and audit.
  Planned, not scheduled.

The knowledge graph is the **single source** for both the wiki (Stage A) and, later, the
in-app domain help — the docs/ tree becomes queryable product data, not a parallel copy.

**Consequences:** (+) value ships early; each stage validates the one after; the graph
investment (ADR-0015) becomes the product's content spine. (−) Stage A must expose docs/
as an API without letting the API become a second source of truth — the resolver reads the
governed files, it does not fork them. (−) commits the repo to a much larger surface;
mitigated by staging and by every stage gated on `make verify-full`.

**Alternatives considered:** *Build the full SCM app directly* — rejected by staging: 10×
the surface with no early validation. *Wiki as a static site generator* — rejected: cannot
grow into Stages B/C, and re-implements the graph the gates already validate.

---

## ADR-0016 — Department IMPLEMENTATION.md files are business context, not target architecture

**Status:** Accepted (owner-authorized 2026-07-20)
**Extends:** ADR-0002, ADR-0010, ADR-0015

**Context:** The 14 `src/departments/*/IMPLEMENTATION.md` files total **128,240 words** —
with the department READMEs (22,082), **150,322 words sit outside the governed tree,
against 29,522 inside it. The governed tree is 16% of the repo's prose.** The allowlist
(knowledge-architecture §3) exempts these files as "component docs living next to the code
they document", and that exemption was inherited at skeleton adoption without anyone
reading the content.

Reading it shows the files do **not** document this codebase. They specify a different
system: an analytics/BI workstream on **SAP S/4HANA · SAP Ariba · PostgreSQL · Apache
Superset · Apache Airflow**, with a star-schema warehouse, dashboard page designs and DAG
schedules. Across the 14 files: 195 references to Superset, 178 to PostgreSQL, 117 to SAP
S/4HANA, 7 to SAP Ariba. None of this exists in `src/`, which is a pure TypeScript domain
layer with no application, infrastructure or persistence layer at all.

The exemption is therefore worse than cosmetic. These documents are **invisible to every
gate** — no front-matter, so G1 skips them, G3 never sees their identifiers, G4 never
checks their links, G5 cannot detect them as orphans — and they contain normative
statements that **contradict the code**. The first concrete instance was found while
cataloguing CPT-0003: `03-demand-planning/IMPLEMENTATION.md` §10 specifies
`z = scipy.stats.norm.ppf(target_service_level)`, the exact quantile function, while
*both* the TypeScript and Python implementations use table lookup with linear
interpolation, and disagree with each other as well. Three definitions of one quantity,
none reconciled, the authoritative-by-intent one unimplemented.

**Decision:** These files are classified as **business context, not target architecture**.

1. **The technology stack in them is non-normative.** SAP, Superset, Airflow and the star
   schema describe an illustrative enterprise setting, not a commitment of this repo.
   ADR-0002 (OSI-only) is **not** violated by their mention, because they name no
   dependency of this project — but no work item may cite them as architectural authority.
2. **Their normative content is extracted into governed nodes:** business rules and
   validations into the department's `rule.md` (Tier 4, stable IDs); KPIs, formulas and
   metric definitions into `docs/25-concepts/` nodes (Tier 3, `CPT-*`) per ADR-0015.
   Extraction **references, never copies** (knowledge-architecture §4).
3. **Originals are archived, not deleted** — knowledge-architecture's total-conservation
   principle. Once a department is extracted, its `IMPLEMENTATION.md` is stamped
   `status: archived` and points to the governed nodes that superseded it.
4. **The allowlist narrows** as extraction completes: an archived `IMPLEMENTATION.md` is
   no longer a knowledge home, only a historical record.

**Consequences:**
- (+) The largest body of knowledge in the repo stops being invisible to the gates.
- (+) Contradictions between spec, TypeScript and Python surface as extraction findings
  rather than as production surprises — the z-score case is the proof.
- (+) Removes a standing trap: an agent reading `IMPLEMENTATION.md` for guidance would
  have built toward SAP and Superset.
- (−) Substantial extraction work across 14 departments (backlog U18), and much of the
  128k words is dashboard/DAG design that will archive without extraction.
- (−) Until extraction completes, the repo holds two descriptions of each department. The
  archival stamp is what prevents ambiguity in the interim.

**Alternatives considered:**
- *Stamp front-matter and pull them in whole* — rejected: it would admit 128k words of
  non-normative BI design into the governed tree, blow every G9 budget, and grant
  architectural authority to a stack the repo does not use.
- *Treat them as the target architecture* — rejected by the owner: it would redefine the
  project as an SAP-sourced analytics warehouse and orphan the entire `src/` domain layer.
- *Leave the allowlist as-is and note the risk* — rejected: it preserves the invisibility
  that let a spec/code contradiction survive unnoticed.

---

## ADR-0015 — A concept-node layer makes every SCM calculation individually citable

**Status:** Accepted (owner-authorized 2026-07-20)
**Extends:** ADR-0004, ADR-0010, ADR-0012

**Context:** The estate implements roughly 250 public Python functions and 350 TypeScript
types spanning Wagner-Whitin, Croston/SBA, newsvendor, Clarke-Wright, queueing models,
Monte Carlo VaR, CBAM and EUDR — a body of supply-chain knowledge far broader than the
documentation admits. That knowledge is **undiscoverable**: the controlled vocabulary is a
35-row one-line glossary table, and every formula, assumption, unit and boundary
condition lives only in code comments. A reader cannot ask "what does this system know
about safety stock, and where is it computed" without reading TypeScript and Python. The
existing `docs/` tree is already a validated node graph (`id` + `relations`, gates
G4/G5/G6), so the gap is not graph infrastructure — it is the absence of a node class for
the domain's concepts. There was also no mechanical answer to "what is missing": gap
analysis was manual and therefore stale on arrival.

**Decision:** Introduce a **concept-node layer** at `docs/25-concepts/`, one node per
calculation or concept, with a new document `type: concept` at authority **Tier 3**,
beside the glossary it expands. The tiering is deliberate and follows the existing
semantics of the tree: Tier 3 **defines what a term means**, Tier 4 `rule.md` **states
what must hold**. A concept node therefore owns semantics (formula, units, assumptions)
and never restates an invariant — it cites the rule ID, keeping `rule.md` the single
source of truth for law.

- Nodes are grouped by owning department: `docs/25-concepts/<NN-dept>/<slug>.md`.
- Stable IDs come from a single estate-wide family **`CPT-NNNN`** (id-registry §1) —
  concepts cross department boundaries (EOQ is cited by planning, inventory and finance),
  so per-department prefixes would force arbitrary ownership.
- Each node carries: definition · formula with named symbols and **units** · inputs and
  outputs · assumptions and *when it does not apply* · the standard or literature
  reference · a worked numeric example · links to its TypeScript and Python
  implementations · the rule IDs it is governed by · related concepts.
- Concept nodes **reference** rules by ID and never restate them (knowledge-architecture
  §SSOT). Related-concept links use `refines`/`traces-to`; `depends-on` is reserved for
  true mathematical prerequisites, because G6 enforces acyclicity over it.
- **Gate G10** (new) does two things: it verifies every `## Implementations` bullet points
  at a symbol that genuinely exists in the linked file — so the map cannot rot — and it
  reports a coverage census of code symbols with no concept node. Coverage is enforced
  per department via a status table, letting the estate adopt incrementally instead of
  failing red on day one.

**Consequences:**
- (+) Every calculation becomes individually citable, teachable and reviewable without
  reading the implementation.
- (+) "What is missing" becomes a CI output rather than an audit: the census is recomputed
  on every run and cannot go stale.
- (+) Symbol links are verified, so refactors that rename a function fail the gate instead
  of silently orphaning the documentation.
- (+) Cross-language divergences surface as a side effect of documenting one formula twice
  — the first census already caught the z-score tables.
- (−) A real authoring cost (~250 nodes) and a standing obligation: a new public
  calculation now needs its node before the owning department can stay `enforced`.
- (−) A third place that mentions a formula (code, concept node, rule). Mitigated by
  authority tiering: rules state law, concept nodes state semantics, code computes.

**Alternatives considered:**
- *Expand the glossary in place* — rejected: a single table cannot carry formulas,
  units, worked examples or per-symbol traceability, and it would blow the G9 budget.
- *Generate the catalogue from docstrings* — rejected: it would document what the code
  says, not what the domain means (assumptions, non-applicability, standard lineage), and
  the divergences that matter are invisible from inside one language.
- *Per-department concept families (`PRC-C*`, `DMD-C*`)* — rejected: forces a single
  owner onto genuinely shared concepts and renumbers when ownership moves.

---

---

## ADR-0030 — The workspace is a tech-company operating model: SCM is the Global Context governing a portfolio of multi-branch tech Projects

**Status:** Accepted (owner-directed 2026-07-22)
**Extends:** ADR-0017 (staged full-stack app), ADR-0021 (context-engineering layer already
instantiated), ADR-0024 (one-way knowledge read model, `docs/` SSOT), ADR-0026 (octagon
node-graph wiki), ADR-0018/0023 (Clean Architecture / monorepo), ADR-0008 (named standards
are first-class), and the `50-engineering` tier + `.claude/skills` practice layer.

**Context:** To date the estate (ADR-0017) is a full-stack app that surfaces the SCM knowledge
as a wiki. The owner has now set the direction and resolved the gating questions
(conversation, 2026-07-22). **This is not a commercial product; it is a project/workspace
modeled as a technology company.** The insight: **supply-chain management is used as the
operating discipline of the company itself** — the same plan → source → make → deliver →
return → enable flow, its KPIs, quality control, risk and procurement logic, applied not to
physical goods but to **the flow of technical work**. That operating discipline is the
**Global Context** that plans, governs, produces, delivers and monitors a **portfolio of
Projects**, where each project is a deliverable in **any branch of technology**. Recorded
before any build (ADR-0010 plan⇄context; §5 conversation is never the source of truth).

**Decision:**
- The **Global Context** is the company's operating context: (a) the SCM discipline — the 14
  SCOR-DS departments, `CPT-*` concept catalogue and `SCM-R*`/department rules — reused as the
  **operating system** for running work; plus (b) the **engineering & professional-practice
  knowledge** already in the estate (`50-engineering` ENG-R* rules, and the `.claude/skills`
  practice layer: clean-architecture, engineering-standards, testing-quality, nestjs-graphql,
  nextjs-frontend, postgresql-data, python-precision-grpc). It is exposed as a **read-only,
  versioned substrate** with the wiki front end (ADR-0026), keeping the one-way SSOT
  (ADR-0024: `docs/` is the single source of truth; the served graph is a projection, never
  hand-edited).
- The Global Context's remit is **best practices, technical concepts, applied professionalism,
  design, processes, organization and structure** (non-exhaustive) — the standards the company
  applies to every project.
- A **Workspace** is the company space that contains **Projects**. A **Project** is a unit of
  technical work in some **tech branch** — non-exhaustive: AI, Machine Learning, Data Science,
  Data Analysis, Data Engineering, software development, Backend, Frontend / web design,
  UI/UX, Databases, DevOps, MLOps, Cloud & Infrastructure / SRE, Security, QA & testing,
  Mobile, Systems / embedded, Product & Project management, Technical writing. A project
  **references** the Global Context by stable ID and carries its own transactional data; it
  **never mutates** the Global Context.
- **A1 — context scope (RESOLVED, owner 2026-07-22):** the Global Context is **SCM-specific as
  the operating discipline** (supply chain is the company's OS). The *projects it governs* span
  all tech branches; that breadth lives in project data + per-branch practice knowledge, not in
  a generalized domain engine. A **domain-agnostic** context engine stays **reserved** for a
  future ADR — not built toward yet (no speculative generalization).
- **A2 — project relationship (RESOLVED = reference + overlay, owner 2026-07-22):** a project
  holds a **local overlay** (project-scoped concepts + parameter/threshold overrides) that
  references but never rewrites global nodes. Reads resolve *global node, then project
  override* — preserving the SSOT while letting each project tune practice to its branch.
- **Architecture placement (ADR-0018/0023):** `workspace` / `projects` are **new bounded
  contexts outside the 14-department SCM taxonomy** — company/platform concerns, not SCM
  departments. Per-tech-branch practice knowledge is materialized **only as justified by a
  build task** (no speculative directories/skills for every branch up front).
- **Prompt-refinement operating rule:** every user prompt is first improved, then the improved
  prompt is executed — recorded as a distinct decision in **ADR-0032** and treated as the
  company's incoming-quality gate on instructions.
- **Staging:** **extends** ADR-0017 — Stage A (wiki / Global Context) stands; Stage B is the
  workspace+projects layer on the same stack (Next.js · NestJS/GraphQL · PostgreSQL · Python
  calc); real-time monitoring is ADR-0031 (Stage C).

**Consequences:**
- (+) The knowledge investment (154 concept nodes, rules, ADRs, engineering practice) becomes
  the company's reusable operating context, not one app's content.
- (+) A coherent metaphor: SCM's incoming inspection, quality control, risk, KPIs and S&OP map
  directly onto governing technical delivery — the discipline transfers.
- (+) SSOT preserved: projects reference, never mutate; ADR-0024's one-way projection holds.
- (+) Breadth (all tech branches) is expressed as data + incrementally-materialized practice
  knowledge, keeping the model bounded rather than speculative.
- (−) A new mutable application-data domain (workspace/projects) with schema, auth/tenancy and
  lifecycle — real build scope beyond the read-only wiki.
- (−) The overlay (A2) adds global+override resolution complexity at every read.
- (−) "All tech branches" is an open-ended remit; disciplined materialization (per justified
  task) is the standing guard against scope sprawl.

**Alternatives considered:**
- *Treat it as a commercial SCM product* — rejected: the owner reframed it as an internal
  project/workspace where SCM is the operating discipline, not the sold good.
- *Generalize to a domain-agnostic engine now (A1 alt)* — rejected: premature generalization of
  a model with one real operating domain; reserved for a future ADR.
- *Projects fork/snapshot the whole context (A2 alt)* — rejected: breaks the one-way SSOT
  (editable copies drift), multiplies storage, blocks global-correction propagation.
- *Materialize a rule family + skill per tech branch now* — rejected: speculative; branches are
  catalogued as they are actually built (knowledge-architecture "only justified nodes").

---

## ADR-0031 — A monitoring-connector layer adds real-time project development metrics (future, complementary)

**Status:** Accepted (owner-directed 2026-07-22 — A3 resolved = both sources, internal-first; build deferred)
**Extends:** ADR-0030 (workspace/projects), ADR-0015 (concept-node catalogue), ADR-0025
(code-first GraphQL), ADR-0002 (OSI-only).

**Context:** Alongside the workspace/projects direction, the owner wants a future **connector**
for **real-time monitoring of a project's development and progress** — dashboards and metric
calculations that show, live, how a project under development advances. The owner framed it as
**complementary** to the current objective, to be added later, but recorded now so the platform
is designed with it in mind (plan⇄context).

**Decision:**
- A **Connector** ingests development/progress signals for a project; a **Monitoring** module
  computes **Metrics** over them; **Dashboards** render them in near-real-time.
- **A3 — metric source (RESOLVED = both, internal-first, owner 2026-07-22):** the connector
  unifies **both** sources — external development tools (GitHub/CI/issue-trackers) and the
  platform's own internal project data — behind one metrics model. Delivery is
  **internal-project-data first** (dashboards over the platform's own tasks/milestones/progress),
  with external connectors added incrementally.
- Metrics reuse the estate's discipline: each progress/velocity metric is **defined as a concept
  node** (`CPT-*`) with formula, units and worked example, so a delivery metric is as governed and
  citable as a supply-chain KPI — one catalogue, not a parallel one.
- **OSI-only (ADR-0002):** connectors and dashboard tooling must be OSI-licensed; no proprietary
  observability SaaS as a hard dependency.
- **Scope guard:** this layer is **deferred / reserved, not scheduled**. It is recorded so the
  ADR-0030 project data model is designed to **emit the progress events** monitoring will consume,
  avoiding a retrofit; no monitoring code is built until a dedicated task is scoped and this ADR is
  ratified.

**Consequences:**
- (+) Recording it now lets the project data model emit progress events from day one.
- (+) Metrics-as-concept-nodes keeps one calculation catalogue and one review discipline for SCM
  KPIs and delivery metrics alike.
- (−) Real-time ingestion + time-series storage + a dashboard UI is a substantial subsystem,
  explicitly out of the near-term build.
- (−) A3 (source unification) is unresolved; the ADR stays **Proposed**.

**Alternatives considered:**
- *Adopt an existing observability stack* — deferred: Grafana (AGPL) is OSI-admissible, Datadog is
  not; the buy-vs-build call is left to the scoped task, but the metric *definitions* stay in the
  concept catalogue regardless of the render tool.
- *Treat progress metrics as ad-hoc queries* — rejected: it would create ungoverned calculations
  outside the catalogue, exactly what ADR-0015 exists to prevent.

---

---

## ADR-0032 — Prompt-refinement gate: improve a user prompt before executing it

**Status:** Accepted (owner-directed 2026-07-22)
**Extends:** ADR-0030 (the company operating context), ADR-0008 (SCM standards are first-class),
ADR-0015 (governed nodes over ad-hoc behavior).

**Context:** The owner added an operating rule (conversation, 2026-07-22): when a user submits a
prompt, the system must **first improve/refine the prompt, then send the improved prompt** to
the executing model/agent. In the tech-company operating metaphor (ADR-0030) this is the natural
analogue of **incoming inspection / quality control** (dept 08) applied to the *instruction* as
the raw material entering the flow — a bad instruction, like a defective input, is caught and
corrected before it consumes downstream work.

**Decision:**
- Every user prompt passes a **Prompt-Refinement Gate** before execution: the raw prompt is
  transformed into an **improved prompt** (clarified intent, resolved ambiguity, added missing
  constraints/context, aligned to the Global Context's standards), and only the improved prompt
  is executed. The original and the improved prompt are both retained (traceability, like an
  inspection record).
- It is an **operating rule of the Global Context** (ADR-0030), applied across all projects and
  tech branches — not project-specific.
- **[ASSUMPTION A4 — enforcement surface, owner to confirm]:** the gate is a **platform runtime
  feature** (the app refines end-user prompts before dispatching them to a model). It also reads
  as guidance for how agents work on this repo; the two are compatible, and the platform-runtime
  reading is taken as primary. Owner may narrow it.
- Its stable **rule ID and the refinement criteria** are materialized in the platform rule
  family when the W2 task creates it (id-registry §2); the refinement quality metric, if
  measured, is a `CPT-*` node (ADR-0015). Not built until Stage B (W3).

**Consequences:**
- (+) Higher-quality execution and fewer wasted downstream cycles — quality-at-the-source applied
  to instructions.
- (+) Metaphor coherence: the SCM incoming-inspection discipline governs the company's own inputs.
- (+) Retaining original+improved prompts gives an auditable trail (and data for a
  forecast-value-added-style "did refinement help?" metric later).
- (−) Latency and cost of an extra refinement step on every prompt; must be fast and, ideally,
  skippable for already-precise prompts.
- (−) A refinement step can drift from user intent if over-eager — needs a visible diff / opt-out
  so the user sees what changed (design constraint for W3).

**Alternatives considered:**
- *Refine only on request / low-confidence prompts* — reasonable optimization, folded into the
  design as the "skippable for precise prompts" note rather than a separate decision.
- *No refinement (execute prompts verbatim)* — rejected: the owner explicitly wants
  quality-control on inputs; verbatim execution is the status quo being improved.

---

---

## ADR-0033 — Exclusive technology lanes: one responsibility per technology, no trespassing

**Status:** Accepted (owner-directed 2026-07-22)
**Extends / refines:** ADR-0001 (two-language split), ADR-0017/0018/0023 (staging, Clean
Architecture, monorepo), ADR-0020 (gRPC contract), ADR-0025 (code-first GraphQL), ADR-0030
(company operating model). **Rewrites the ENG-R8 slot** and narrows ADR-0001.

**Context:** ADR-0001 split TypeScript (domain) from Python (analytics), but in practice both
languages implemented the same calculations — measured: **49 of 154 concept nodes exist in both
TS and Python**, which is the documented source of the ~30 cross-language divergences. The owner
set a stricter principle (conversation, 2026-07-22): **each technology has one exclusive
responsibility and no other technology may do its job**, even to save an implementation. Two
consequences were directed explicitly: **only NestJS may communicate with the frontend**, and
**TypeScript leaves the calculation lane** — Rust joins Python there so the two split
calculation responsibilities between them. Recorded before code (ADR-0010 plan⇄context).

**Decision — the lane map. Each row has exactly ONE owner; no other technology may perform it:**

| Lane | Exclusive owner | Owns | Must never |
|---|---|---|---|
| Presentation | **Next.js** | UI, rendering, interaction, a11y, design tokens | Hold business rules or calculations; talk to anything except NestJS |
| Frontend gateway | **NestJS + GraphQL** | **The only technology the frontend talks to**: resolvers, input validation, authN/authZ, subscriptions/SSE, orchestration of internal calls | Compute business results itself; be an ingestion firehose; act as a scheduler |
| Business rules | **TypeScript (framework-free)** | Invariants, guards, state machines, lifecycle, identity | **Any mathematics or statistics** — it is out of the calculation lane |
| Exact arithmetic · hot path · ingestion | **Rust** | The single money/Decimal core, per-event transforms, connector ingestion workers, deterministic high-throughput work | Model fitting, statistical inference, optimization solving |
| Models · statistics · optimization · ML | **Python** | statsmodels/scipy/sklearn/prophet/ortools/simpy work: fitting, inference, solving, simulation, training | Serve the frontend; own the hot per-event path; do rollups the analytics store does at ingest |
| Transactional state | **PostgreSQL** | OLTP, event store, knowledge read model (one-way from `docs/`) | Be a message queue or a high-volume time-series store |
| Analytics at scale | **ClickHouse** (ADR-0034) | Columnar time-series, ingest-time aggregation, dashboard queries | Be a source of truth |
| Images | **Docker** (ADR-0034) | Reproducible images, local composition | Encode environment secrets |
| Orchestration | **Kubernetes** (ADR-0034) | Scheduling, scaling, config/secrets, network policy | Hold application logic |

- **Communication rule (load-bearing):** the frontend has exactly one counterpart — NestJS.
  Rust, Python, ClickHouse and PostgreSQL are reached **only** through it (Rust/Python over the
  gRPC contract, ADR-0020; the stores through infrastructure adapters). No other technology
  exposes an endpoint the browser may call.
- **Calculation split inside the shared lane:** Rust takes work that is *exact, deterministic and
  hot* (money arithmetic, per-event evaluation, streaming transforms); Python takes work whose
  value is the *scientific library* (fitting, inference, optimization, ML, simulation). Neither
  duplicates the other; the boundary is recorded per `CPT-*` node.
- **Consequence for the money core (supersedes the P5 slice-1/3 shape):** money moves from two
  mirrored implementations (TS + Python) to **one Rust implementation** exposed to TypeScript
  (napi-rs) and Python (PyO3). The P5 work is not discarded — its semantics, ROUND_HALF_EVEN
  decisions and the U8 golden vectors become the **specification and acceptance tests** for the
  Rust port.
- **Every technology is held to its own current best practices** — enforced as `ENG-R9`
  (best-option verification gate) in `50-engineering/rule.md`.

**Consequences:**
- (+) The 49 duplicated calculations get a single owner each; the divergence class disappears
  structurally rather than being detected after the fact.
- (+) One money implementation instead of two mirrors, in a memory-safe language with exact
  decimals — and TypeScript stops doing arithmetic it should not own.
- (+) The ingestion path finally has a legitimate owner: since NestJS may only serve the
  frontend and Python's lane is mathematics, Rust owns it. The rule created the clarity.
- (+) A single frontend counterpart shrinks the attack surface to one audited gateway.
- (−) **More technologies to build, operate and secure** (Rust toolchain and cross-compilation
  join CI). This is the accepted price of the rule.
- (−) A cross-language boundary appears inside calculation (Rust ↔ Python); the split must be
  recorded per concept node or it becomes a grey zone.
- (−) Work already landed (P5 money in TS/Python) is re-homed rather than reused as-is.

**Alternatives considered:**
- *Pragmatic shared lanes (let whoever is convenient compute)* — rejected by the owner: it is
  exactly how the 49 duplicates appeared.
- *All calculation in Python* — rejected: the interpreter and the GIL are wrong for the exact
  hot path (per-event, per-write arithmetic).
- *All calculation in Rust* — rejected: loses statsmodels/ortools/prophet/sklearn, which are the
  reason Python is in the stack.
- *Keep TypeScript in the calculation lane* — rejected by the owner directive; it is also what
  made the duplication possible.

---

## ADR-0034 — Scale tier: ClickHouse for analytics, Docker for images, Kubernetes for orchestration

**Status:** Accepted (owner-directed 2026-07-22)
**Extends:** ADR-0031 (monitoring connector), ADR-0033 (exclusive lanes), ADR-0024 (one-way
projection discipline), ADR-0002 (OSI-only).

**Context:** The monitoring layer (ADR-0031) must observe **many projects at once with large data
volumes**, in real time, without losing speed or security. Under ADR-0033 the existing
technologies may not be stretched to absorb this: PostgreSQL may not become a high-volume
time-series store or a queue, and NestJS may not become an ingestion firehose. The owner directed
adopting **ClickHouse**, **Docker** and **Kubernetes**.

**Decision:**
- **ClickHouse** (Apache-2.0) owns analytics and time-series at scale: columnar storage,
  **ingest-time aggregation via materialized views** (cost moves from query time to insert time),
  and dashboard queries with high concurrency and multi-tenant fan-out.
- **ClickHouse is never a source of truth.** It is **rebuildable** from the durable event record
  (PostgreSQL event store / the connector stream) — the same one-way discipline ENG-R7 imposes on
  the knowledge read model. Dropping and rebuilding it must always be safe.
- **Write path:** only the **Rust ingestion workers** (ADR-0033) insert into ClickHouse, in
  **batches** (row-by-row inserts are an anti-pattern there). **Read path:** only **NestJS**
  queries it, and only NestJS serves the result to the frontend.
- **Least privilege:** separate ClickHouse users — an **INSERT-only** identity for ingestion and a
  **SELECT-only** identity for queries, the latter constrained by row/time/memory quotas so a
  dashboard query cannot exhaust the cluster. TLS in transit. No direct browser access, ever.
- **Docker** owns reproducible images and local composition; **Kubernetes** owns orchestration
  (scheduling, scaling, config/secrets, network policy). ClickHouse is stateful: in Kubernetes it
  requires persistent volumes and an operator rather than a plain Deployment.
- **Deliberately still gated on measured volume (not adopted here):** the **event broker**
  (NATS vs Kafka, both Apache-2.0) and the **cache** (Valkey, BSD-3). They are adopted only when
  measurements show ingestion or fan-out that the Rust workers plus ClickHouse cannot absorb —
  YAGNI as recorded in `engineering-standards`.
- **Sequencing guard:** Kubernetes is justified once there are multiple long-running services to
  orchestrate; Docker Compose covers the interim. Building the cluster before the services exist
  is explicitly out of order.
- **License note (ADR-0002):** ClickHouse, Docker Engine and Kubernetes are OSI-licensed
  (Apache-2.0). Rejected on licensing grounds for this tier: **TimescaleDB** (its advanced
  features are proprietary TSL — and it would also violate ADR-0033 by making PostgreSQL do the
  analytics job) and **Redpanda** (BSL restricts managed-service use).

**Consequences:**
- (+) Dashboard queries stay sub-second at volume without touching the OLTP database.
- (+) Rebuildability keeps the analytics store disposable — a corrupted or re-modelled ClickHouse
  is a rebuild, never a data-loss incident.
- (+) Split-privilege access and a single query gateway keep the attack surface small.
- (−) A real operational surface arrives: a stateful cluster, volumes, an operator, backups,
  upgrades — plus Kubernetes itself. Each is a new thing to patch and secure.
- (−) Two stores must be kept coherent (PostgreSQL truth vs ClickHouse projection); a drift check
  is required, analogous to the ingest drift guard planned for the knowledge read model.

**Alternatives considered:**
- *PostgreSQL alone (or with TimescaleDB)* — rejected: violates ADR-0033's lane rule, and
  TimescaleDB's useful features are proprietary.
- *A managed analytics service* — rejected: ADR-0002 self-hostable, modifiable OSI policy.
- *Defer analytics entirely until volume is proven* — the honest minimal option, and it remains
  correct for the **broker and cache** (still gated); the owner directed adopting ClickHouse now
  so the monitoring data model is designed against its shape from the start rather than retrofitted.

---

---

## ADR-0035 — Rust is the complete core; Python is the tools layer; TypeScript leaves the core

**Status:** Accepted (owner-directed 2026-07-22)
**Supersedes:** the TypeScript-owns-domain-logic clause of **ADR-0001** (the two-language split
becomes Rust core + Python tools). **Narrows:** ADR-0033 (the "business rules" lane changes owner
from framework-free TypeScript to Rust). **Rewrites in part:** ENG-R1/ENG-R2 (see ENG-R10).
**Depends on:** ADR-0020 (gRPC contract), ADR-0019 (exact decimal money), ADR-0002 (OSI-only).

**Context:** ADR-0033 established exclusive lanes with framework-free TypeScript owning business
rules and Rust owning exact arithmetic, the hot path and ingestion. The owner then directed a
stronger arrangement (conversation, 2026-07-22): **Rust replaces TypeScript entirely as the
core** — "que Rust sea el núcleo completo y Python las herramientas" — with the explicit
requirement that Rust and Python **converge** on best practices, speed, security and
scalability. The estate today holds **12,388 lines of TypeScript domain code** (14 departments,
314 invariant guards) and **12,771 lines of Python** calculation code.

**Decision:**
- **The core is Rust.** It owns business rules, invariants, state machines, lifecycle and
  identity; exact arithmetic (the single money/Decimal implementation); the per-event hot path;
  and connector ingestion. No I/O framework enters it.
- **Python is the tools layer.** Stateless model services: fitting, statistical inference,
  optimization solving, simulation, ML — the work whose value is the scientific library
  (statsmodels, scipy, sklearn, prophet, ortools, simpy). Python holds **no business rules** and
  never serves the frontend.
- **TypeScript survives only as framework code** — inside **NestJS** (the sole frontend gateway)
  and **Next.js** (presentation). It carries no core logic, no business rules and no mathematics.
  `packages/domain` and the domain half of `packages/shared` are retired into the Rust core.
- **How the two converge (the owner's explicit requirement):**
  1. **Schema-first contract.** The `.proto` files (`scm.calc.v1`, ADR-0020) are the single
     source of the wire contract; **Rust types are generated with `prost`/`tonic` and Python
     types with `grpcio-tools` from the same schema.** Hand-written DTOs on either side are a
     defect. Money and rates cross as **strings** (ENG-R5).
  2. **Call direction.** NestJS → Rust core; the **Rust core** orchestrates and calls Python
     tools over gRPC when a model is needed. Python never calls the core; the gateway never
     calls Python directly.
  3. **Transport choice, justified.** Core↔Python is **gRPC**, not PyO3 embedding — isolation,
     independent scaling of model workers, and the GIL stays out of the core process (decisive
     at the telemetry scale of ADR-0036). NestJS↔core is **in-process via `napi-rs`**, because
     a network hop between the gateway and the core buys nothing and costs latency on every
     request; gRPC remains the escape hatch if the core ever needs independent scaling.
  4. **One error taxonomy.** Rust `Result` with typed error enums and Python typed exceptions
     both map to the **same gRPC status/error codes declared in the proto**, which NestJS maps to
     GraphQL errors. No stringly-typed errors across the boundary.
  5. **Shared correctness fixtures.** The U8 golden vectors (`tests/golden/*.json`) become the
     **Rust↔Python** contract tests — the Rust suite reads the same file the Python suite does.
     The fixtures are the acceptance criterion for every ported calculation.
  6. **Distributed tracing.** OpenTelemetry context propagates NestJS → Rust → Python so one
     request is traceable end to end; without it, a three-technology path is undebuggable at
     scale.
- **Migration is incremental (strangler), never a freeze.** The Rust core grows department by
  department behind the same public behaviour; each ported unit must make its existing tests and
  golden vectors pass **unchanged** before the TypeScript original is deleted. Order: money core
  → the departments already dedup-targeted → the remaining rule sets. `main` stays green
  throughout; no long-lived rewrite branch.
- **Tooling consequences:** a Cargo workspace joins the monorepo; CI gains a Rust toolchain,
  `cargo test`, `clippy` (warnings as errors) and cross-compilation for the `napi-rs` artefact;
  `tools/verify.py` must learn Rust symbols (`pub fn`) and crate paths so **G10 keeps the concept
  catalogue honest** across the port.

**Consequences:**
- (+) One core language for rules *and* arithmetic: the 49 duplicated calculations collapse to a
  single owner, and the money mirrors become one implementation.
- (+) Memory safety, exhaustive matching and compiler-forced error handling on the code that
  enforces financial and compliance invariants — the strongest security posture available for
  that surface.
- (+) Predictable latency with no GC pauses on the hot path, and fearless concurrency for
  ingestion at the ADR-0036 scale.
- (+) Python keeps exactly what justifies it (the scientific ecosystem) and nothing else.
- (−) **The largest change in the project: ~12,400 lines of working TypeScript are retired and
  re-expressed in Rust, along with their 85 passing tests.** It produces no new user-facing
  capability by itself. This is accepted deliberately by the owner.
- (−) The concept catalogue's TypeScript implementation links must be repointed, and the gate
  extended, or G10 silently stops protecting the catalogue.
- (−) A compiled toolchain, cross-compilation matrix and native artefact enter CI and every
  developer machine; build times rise.
- (−) Two boundaries now exist inside what used to be one process (napi-rs and gRPC); both need
  tracing and typed errors to stay debuggable.

**Alternatives considered:**
- *Keep framework-free TypeScript for rules (ADR-0033 as written)* — rejected by the owner
  directive; it also leaves rules and arithmetic in different languages.
- *Rust for new surface only, TypeScript rules left in place indefinitely* — rejected as an end
  state, but **adopted as the migration path**: it is the strangler pattern, and it is why no
  freeze is needed.
- *Move rules into Python instead* — rejected earlier and again: interpreter and GIL are wrong
  for per-write rule evaluation, and it would put rules in the tools lane.
- *Big-bang rewrite on a long-lived branch* — rejected: it would park the estate's green state
  for months and merge as one unreviewable change.

---

## ADR-0036 — Telemetry data model: continuous project-supervision telemetry at tens-of-thousands scale

**Status:** Accepted (owner-directed 2026-07-22)
**Extends:** ADR-0034 (ClickHouse tier), ADR-0031 (monitoring), ADR-0035 (Rust owns ingestion).
**Resolves:** the L1 volume question in `program/WORKFLOW.md`.

**Context:** The owner specified the monitoring workload (conversation, 2026-07-22): **tens of
thousands**, **telemetry only, for project supervision** — i.e. continuous numeric series rather
than bursty development events. That is a **high-cardinality, sustained-ingest** time-series
workload, which fixes several ClickHouse design choices that were left open in ADR-0034.

**Decision:**
- **Shape.** One wide raw table of telemetry samples: `project_id`, `metric` (name), `ts`,
  `value`, plus `LowCardinality(String)` label columns. No `Nullable` on hot columns (it costs a
  second column and blocks some optimizations) — absence is encoded explicitly.
- **Sort key `(project_id, metric, ts)`.** Supervision queries always scope to a project (and
  usually a metric) before a time range, so the leading high-cardinality column is correct here
  and prunes the most data. **Partition by `toYYYYMM(ts)`** — monthly parts keep the part count
  manageable at tens of thousands of series; daily partitions would fragment it.
- **Codecs, chosen per column type:** `ts` → `Delta` + `ZSTD`; float metrics → `Gorilla` or
  `DoubleDelta` + `ZSTD`; labels → `LowCardinality`. Telemetry is highly regular, so these are
  the difference between reasonable and ruinous storage.
- **Rollup cascade with `AggregatingMergeTree`:** raw → **1 minute → 1 hour → 1 day**, built as
  **ingest-time materialized views** so dashboard cost is paid on insert, not on query
  (ADR-0034). Dashboards read the coarsest table that answers the question.
- **Retention.** Short **TTL on raw** samples (weeks), long retention on rollups (months to
  years). Supervision needs recent detail and historical trend, not historical detail.
- **Write path.** The **Rust ingester** (ADR-0035) batches — client-side batches or
  `async_insert` — never row-by-row. Batching is the single most important ingest decision in
  ClickHouse.
- **Read path.** Only NestJS queries, only through the SELECT-only identity, with row/memory/time
  quotas so no dashboard can exhaust the cluster (ADR-0034 least privilege).
- **Metrics are governed.** Every supervision metric is a `CPT-*` concept node (ADR-0015/0031)
  whose definition matches the materialized view that computes it; a rollup without its node is
  an ungoverned calculation.
- **Still gated (unchanged).** The broker (NATS/Kafka) and cache (Valkey) enter only when
  measurement shows the Rust ingester plus ClickHouse cannot absorb the rate — telemetry that is
  batched directly usually does not need a broker until multiple independent consumers appear.

**Consequences:**
- (+) Sub-second dashboards over tens of thousands of series, because the aggregation already
  happened at insert time.
- (+) Storage stays proportionate: regular telemetry compresses extremely well with these codecs.
- (+) The raw-TTL/rollup split bounds growth without losing the trend history supervision needs.
- (−) The rollup cascade is schema that must be migrated carefully: changing a materialized view
  requires a backfill plan, and ClickHouse will not do it implicitly.
- (−) Choosing the sort key for project-scoped queries makes cross-project "top N metrics
  everywhere" queries more expensive; those need their own projection or a separate view.
- (−) The design assumes numeric telemetry; if bursty development events (commits, PRs, builds)
  are added later, they belong in their own table with its own sort key, not in this one.

**Alternatives considered:**
- *PostgreSQL / TimescaleDB* — rejected in ADR-0034 on lane and licence grounds; at tens of
  thousands of continuous series the row-store cost is also the wrong shape.
- *Daily partitions and no rollups* — rejected: part explosion plus full scans at query time is
  exactly the failure mode ClickHouse materialized views exist to avoid.
- *Store only rollups, discard raw immediately* — rejected: incident investigation needs recent
  raw detail; the short raw TTL is the compromise.

---

## ADR-0037 — The Global Context holds only externally-fixed standards

**Status:** Accepted (owner-directed 2026-07-27)
**Supersedes:** the premise of **ADR-0001** that this repository builds a two-language SCM
application (TypeScript domain + Python calculation) across 14 departments.
**Narrows:** **ADR-0015** — concept nodes are *definitions*, not owners of implementations ·
**ADR-0035** — the Rust core serves the monitoring platform, not 14 departments of invented
rules · **ADR-0016** — business context extracted from `IMPLEMENTATION.md` is reference
material, never law.
**Unaffected:** ADR-0002 (OSI-only), ADR-0010/0012 (knowledge architecture, gates),
ADR-0024/0026 (one-way read model, wiki front end), ADR-0031/0034/0036 (monitoring, its
scale tier and its data model), ADR-0033 (lanes) as applied to the monitoring platform.

**Context.** The estate had drifted into building a *fictitious supply-chain company*: 12,058
lines of invented aggregates in `packages/domain`, 12,958 in `services/calc`, and a starting
port of both into `crates/scm-core`. Their content was not standards but **policy** — a
USD 5,000 purchase-order approval threshold, a 5% over-receipt tolerance, a 0.25 carrying rate,
a 0.95 risk confidence level, a Kraljic axis threshold of 5.0, supplier-scorecard weightings of
40/30/20/10 with rating bands at 90/75/60/45. Every one of those is a number a company picks and
a different project picks differently. Several were stated as law in `CLAUDE.md` and in
`SCM-R*`, which made a single company's habits binding on every future project.

The owner's direction (2026-07-27) settles what this repository is: **the context a project
consults to learn which supply-chain departments it needs and how to implement them.** It must
contain no invented data and no rule that could constrain a future project wrongly. The only
application built here is the **monitoring** project; the context supports development, it does
not simulate a business.

**Decision.**

1. **The inclusion test.** The Global Context carries a statement only if it is fixed **outside**
   this repository — by a standards body (GS1, ISO, ICC, UN/CEFACT, ASCM/SCOR), by a regulator
   (CSDDD, UFLPA, REACH, UCC), or by an arithmetic/accounting identity (double-entry, an
   apportionment that must sum to the whole). If an organization can reasonably choose it, it is
   **project policy** and does not belong here.
2. **Concept nodes define; they do not parameterize.** A `CPT-*` node states what a concept *is* —
   its meaning, its formula where one is canonical, its units, its assumptions and limits, and the
   source that fixes it. It states **no** threshold, target, band, weighting or mandated method.
   Where a calculation needs values, the node names them as **project-chosen inputs** and stops.
3. **Nodes stop owning code.** The `## Implementations` section is removed from every node: the
   context does not ship the implementation, and a link into a project's code would make the
   context depend on a project (violating the one-way rule, ADR-0024).
4. **The fictitious application is deleted**, not archived and not ported: `packages/domain`,
   `services/calc`, `crates/scm-core`, their tests, the `proto/` contract that existed to connect
   them, and the TypeScript money mirror. Keeping it as "reference" would leave invented policy
   inside the context wearing a disclaimer, which is exactly the failure mode being corrected.
5. **`crates/scm-money` is kept, deliberately and narrowly.** It contains no policy: banker's
   rounding is IEEE 754 `roundTiesToEven`, and sum-preserving largest-remainder apportionment is a
   fixed method. Exact money arithmetic with no float ingress is an engineering standard that does
   not vary between projects. If the monitoring platform turns out never to handle money, it
   should be deleted too rather than kept for its own sake.
6. **`SCM-R*` is reclassified.** The family had three kinds of statement mixed together: genuine
   external standards, engineering conventions misfiled as supply-chain law, and company policy.
   Only the first kind survives as `SCM-R*`; engineering conventions move to `ENG-R*`; policy is
   deleted from the rules and, where it is instructive, recorded as an **example of a decision a
   project makes** — never as an invariant.
7. **The gates follow.** G10 stops asserting that every public code symbol has a concept node —
   there is no application code for it to police. It now asserts what matters for a standards
   context: **every concept node cites its external source, and no node claims an
   implementation.**

**Consequences.**
- (+) The context can no longer impose one company's policy on a future project. That was the
  concrete risk the owner named, and it is removed at the root rather than documented.
- (+) ~25,700 lines stop needing maintenance, tests, CI time and cross-language reconciliation.
  The ~30 documented TS/PY divergences disappear with the duplicated code that produced them.
- (+) What remains is honest about its own authority: standards and definitions, with provenance.
- (−) **The largest deletion in the project's history**, including work landed in this session
  (the `crates/scm-core` port) and the U7/U8 Python and cross-language test mechanisms, which had
  nothing left to guard. Accepted deliberately: the work was in the wrong direction, and carrying
  it forward would cost more than discarding it.
- (−) The concept catalogue must be swept for policy numbers node by node — 153 nodes, a
  judgement pass that cannot be scripted. Tracked as the immediate follow-up; until it completes,
  the catalogue still contains parameters this decision forbids.
- (−) `make verify` temporarily has no TypeScript tests to run, because the only TypeScript left
  is the standards reference module and two app scaffolds.

**Alternatives considered.**
- *Keep the application as a reference implementation, marked non-authoritative* — rejected by the
  owner and on the merits: a disclaimer does not stop a future reader from copying a threshold, and
  the estate has already shown that documented caveats get read as specifications.
- *Keep the formulas, drop only the numbers* — this is what **is** being done for the nodes, but it
  does not save the code: an implementation with its parameters removed is not usable by a project
  that must choose them anyway.
- *Move the application into a separate project inside the workspace* — rejected: it would still be
  invented data with no real requirement behind it, and the workspace's projects are meant to be
  real work.

---

## ADR-0038 — Improvement-recommendation gate: what the request left open is chosen, not guessed

**Status:** Accepted (owner-directed 2026-07-27)
**Extends:** ADR-0032 / PLT-R1 (prompt-refinement gate) · ADR-0012 (the improvement register).
**Bounded by:** ADR-0002 (OSI licences) · ENG-R8 (exclusive lanes) · ADR-0037 (the inclusion test).

**Context.** PLT-R1 already refines an incoming prompt before executing it. It does not say what
happens when the refined prompt is still **underspecified** — when a detail the owner never stated
would change what gets built. The default failure modes are both bad: guess silently and produce
something plausible that nobody chose, or ask in prose and bury the decision in a paragraph the
owner has to parse. This estate has evidence for the first: a USD 5,000 threshold, a 5% tolerance
and a 40/30/20/10 weighting all entered as *reasonable-looking guesses* and were inherited as law
until ADR-0037 removed them.

**Decision.**
- **The search is always on.** Every task carries a search for a better implementation **within the
  lanes already adopted** — algorithmic complexity, compute and memory cost, data-structure and
  boundary choice, clean-code and structural quality, and security. Finding nothing is a valid
  result; **not looking is not**.
- **The gate fires on missing detail only** — not on every message, and not on a schedule. The
  trigger is: *a detail is absent whose two plausible readings would produce different work.*
- **When it fires, the options are presented as a selectable list**, not as prose. Each option
  states what it means **and what it costs**; the recommended option comes first and says why it is
  recommended. An option nobody could honestly take does not belong in the list.
- **Selected options are implemented in the same turn**, under the normal gates (ENG-R9 six checks,
  `make verify-full`). The owner's selection is the decision; it does not become a backlog item.
- **Declined options are recorded** in `program/improvement-register.md` as `accepted-as-is` with
  the reason — the mechanism that register already defines — so the same recommendation is not
  re-proposed in a later session.
- **New technology is out of scope by construction.** A recommendation may propose a better
  algorithm, a better structure, a cheaper computation or a tighter boundary. It may **not** propose
  a new language, framework, service or dependency outside an adopted lane: that is ADR-0002 and
  ENG-R8 territory and requires its own decision, asked as such.

**Consequences.**
- (+) The moment of highest ambiguity becomes the moment of an explicit, recorded choice.
- (+) Improvement work stops depending on whether anyone remembered to look for it.
- (+) A declined recommendation is remembered, so the owner is not asked the same thing twice.
- (−) **Gated on ambiguity, the gate can go quiet.** If requests are consistently well-specified,
  high-impact improvements found during clear work have no channel: they must be raised in the
  handoff report instead. This is the owner's chosen trade-off, recorded here so the limitation is
  visible rather than discovered.
- (−) No gate can check this mechanically. Like **G8** (English-only) it is a review discipline; the
  anti-states below are the checklist.
- (−) A list is a real cost to the owner's attention, which is why the trigger is narrow.

**Alternatives considered.**
- *Fire at the end of every unit of work* — rejected by the owner: predictable, but it adds an
  interruption per unit whether or not anything is genuinely open.
- *Fire on any detected high-impact improvement, ambiguity or not* — rejected by the owner. It is
  what would make the search continuously visible; the cost is interruptions during work that was
  already clear.
- *Ask in prose* — rejected: it reads as narration, and the decision it contains gets skimmed.
- *Selected options become backlog entries* — rejected: mechanically tidier, but improvements chosen
  and then deferred go stale, and the owner has already said yes.

---

## ADR-0039 — A measurement-identity axis: aggregation rules are cited once, not restated per department

**Status:** Accepted (owner-directed 2026-08-01)
**Extends:** ADR-0037 (only externally-fixed statements belong here), ADR-0015 (concept nodes).

**Context.** Modelling a warehouse shift scorecard surfaced two arithmetic facts that the catalogue
relies on everywhere and states nowhere:

1. **A ratio must be aggregated from its components.** Dozens of nodes define ratios — OTD, OTIF,
   fill rate, PPM, perfect order rate, bin accuracy, receipt rejection. None says how to aggregate
   one, and the intuitive way is wrong: three periods of 2/100, 3/10 and 1/90 give 3.0 % pooled and
   11.0 % averaged. The error grows with the spread of the denominators.
2. **A level is not a flow.** Summing a backlog over time produces a quantity that never existed.
   Valid aggregations for a level are last, max, min or time-weighted average.

Both are identities, so both pass the inclusion test — nothing an organization could choose. The
question was where they go.

**What the estate already showed.** The identities are not new to the repository; they are *scattered*.
**QMS-R7** fixes the opportunity base for defect rates. **RSK-R5** keeps an ordinal score ordinal.
**PRC-R4, SPL-R5, WHS-R5** and **ORD-R5** each state a conservation for one process. Every one is a
special case of something general, restated because there was no general place to put it. That is the
same duplication in rule form that ADR-0038 addressed in prose.

**Decision.** Create a cross-cutting axis **`docs/30-foundation/measurement/`** with the family
**`MSR-R*`**, holding arithmetic that constrains how a measure may be computed and aggregated,
independent of what it measures. It opens with **MSR-R1** (ratio aggregation) and **MSR-R2**
(flow versus level). Concept nodes **cite** the rule; they do not restate the arithmetic. The
department rules above stay where they are — they carry domain detail the axis deliberately does not.

**Alternatives considered.**
- *Add them to `scm-core/rule.md`.* The natural first choice, and the file is at 963 of its 1,000-word
  budget. Two rules do not fit, and the only trimmable text there is legal citation. Raising the budget
  to make room would have been tuning a gate to fit a change rather than choosing where the change
  belongs.
- *State them in each node.* This is what happened by accident: the flow/level argument was written out
  in three warehouse nodes before this axis existed. It does not scale and it drifts.
- *A concept node instead of a rule.* A concept node states meaning; these state a constraint on what
  may be done with a value. That is law, and it is the same shape as SCM-R14 — an arithmetic identity
  already carried as a rule.

**Consequences.**
- (+) A node cites one ID instead of carrying a paragraph; three warehouse nodes shrink immediately.
- (+) The remaining identities found in the same review — net versus absolute variance, measurement
  coverage, averaging an ordinal scale — have somewhere to land without another structural decision.
- (+) `MSR-R1`'s design consequence is stated where a builder will read it: a system storing only the
  computed ratio cannot comply afterwards. That is a schema decision, not a reporting one.
- (−) A seventeenth rule family. Justified by the scattering evidence, but it is one more prefix to
  know, and the `30-foundation` index gains an axis that was not on its candidate list.
- (−) The special cases stay duplicated in spirit. Consolidating QMS-R7 and RSK-R5 into the axis would
  be a bigger change with retirement notes and citation sweeps; it is deliberately **not** done here,
  and it is the obvious follow-up if the axis proves useful.

---

## ADR-0040 — One long-lived line: the integration model, and why nothing is left hanging

**Status:** Accepted (owner-directed 2026-08-02)
**Resolves:** risk #3 (open since 2026-07-19); the owner directive "fix the branches so everything
is in order, and make the next movements continuous rather than disordered"

**Context — measured, not assumed.** The repository has produced 22 pull requests and every one of
them targets `claude/bold-cannon-l7wtso`. That name was generated by a session; it became the
default branch by accident and has been the trunk ever since. **There is no `main`.** Alongside it
sit three branches — `feat/context-skeleton` (PR #1), `fix/verify-rule-id-regex` (#2) and
`feat/per-department-rules` (#3) — merged in July and never deleted. Each carries **0 commits that
are not already in the base**, verified by `git rev-list --count`: they are not history, because the
history is in the trunk. They are an invitation for a fresh session to branch from a July snapshot.

The working branch has been reused across nineteen pull requests. That is not itself a defect — it
works *because* it is restarted from the base after each merge. It stops working silently the first
time it is not: the next pull request then carries the previous one's commits, and its diff stops
being reviewable. Nothing in the repository said so, so nothing would have caught it.

**Decision.** The integration model becomes law as **ENG-R11**, with six clauses:

1. **One long-lived line, named `main`**, and it is the default branch. Every pull request bases on
   it. A second long-lived line is not created "temporarily".
2. **A work branch is short-lived.** It is restarted from `main` immediately after its pull request
   merges — reusing the name is fine — and it never carries a commit that is already in `main`.
3. **Merged means deleted.** A branch with zero unmerged commits that still exists is a defect, not
   an archive. Deletion happens with the merge, not on a later cleanup pass.
4. **Nothing is left open across a turn boundary.** A turn ends with the pull request merged, or
   with the reason it is not written into the turn's report. *Hanging* is the failure this rule
   names, and reporting it is the mitigation.
5. **The base must be current at merge time.** If `main` moved, the branch is updated and the gate
   is re-run. A green run against a stale base proves nothing about the merge result.
6. **The merge is a merge commit** — not a squash, not a rebase-merge. This is a technical
   requirement, not a taste: **G13** determines a file's true last change by diffing `HEAD` against
   its parent, and skips when `HEAD` is a merge commit precisely because a merge stamps no file of
   its own. A squash merge would present the whole squashed tree as `HEAD`'s own change and fail
   `updated:` on every file in it. The gate and the merge method are coupled.

**The check commands**, kept here because ENG-R11 states the law and this file carries the evidence:

    git rev-list --count main..HEAD                      # clause 2: only this change's commits
    git rev-list --count origin/<branch> ^origin/main    # clause 3: zero ⇒ the branch is dead
    git rev-list --left-right --count origin/main...HEAD # clause 5: right-hand 0 ⇒ base is current

**Alternatives considered.**
- *Rename `claude/bold-cannon-l7wtso` to `main`.* Tidier in one respect — GitHub retargets open pull
  requests automatically — but a rename rewrites the ref every existing clone tracks, and the branch
  carries 22 merged pull requests' worth of references in prose. Creating `main` at the identical
  tip costs nothing and leaves the old name resolvable while it is retired.
- *Trunk-based with direct pushes to `main`.* Removes the review point and runs the gate after the
  fact rather than before. The pull request is where `verify-full` is proven, and CI triggers on
  both `push` and `pull_request` with no branch filter, so nothing needs reconfiguring to keep it.
- *Long-lived feature branches per phase.* The nineteen-pull-request history is the evidence
  against it: small branches merged within the turn have kept every merge conflict-free so far.
- *Leave the branch names alone and just write the rule.* Rejected because the disorder is not a
  habit, it is a state: three dead refs and a trunk named after nothing.

**Consequences.**
- (+) Risk #3 gets an owner and a shape instead of a note. It closes when the default flips.
- (+) A fresh session reads one rule and knows which branch is the line, that its own branch is
  disposable, and that leaving a pull request open is something it must report.
- (+) Clause 6 records *why* the merge method is fixed, so nobody "modernises" it to squash and
  spends a day on G13 failures.
- (−) **Two steps of this cannot be done from a session and are the owner's**: flipping the default
  branch is a repository setting with no API surface here, and branch deletion is refused by this
  environment's git proxy with HTTP 403. Both are named in the handoff rather than silently skipped.
- (−) Until the default flips, `main` and `claude/bold-cannon-l7wtso` both exist at the same commit.
  That is the one moment this decision creates the condition clause 1 forbids; it is bounded by a
  single setting change, and `main` is created **after** the last merge into the old trunk so the
  two never diverge.

---

## ADR-0041 — A load set is priced as a whole, not document by document

**Status:** Accepted (owner-directed 2026-08-02)
**Materializes as:** gate **G14**, manifest `docs/program/load-sets.md`

**Context.** G9 has priced documents individually since ADR-0012 — 700 words for a concept, 1,000
for a rule, 2,600 for `CLAUDE.md`. Nothing has ever priced **what a session opens together**, and
that is the quantity the evidence is about.

The 2025 long-context work is consistent on the shape of the problem, and it is not the shape G9
assumes. Degradation is **continuous in total input** rather than a cliff at the window limit:
Chroma's evaluation of eighteen frontier models found accuracy falling at every increment tested, so
a 200K window can be measurably worse at 50K than at 5K. Liu et al. (TACL 2024) established the
U-shaped position curve — primacy and recency preserved, the middle degraded — and Veseli et al.
(2025) sharpened it: the U holds while a context is under about half full, and past that point
performance tracks **distance from the end** instead. Both findings say the same thing for this
repository: the risk is not one oversized document, it is **many compliant ones arriving together**.

Measured on the day this was written, the estate says so plainly. The `planning` load set — what a
session reads to answer *"what should I do next?"* — is **32,009 words (~42,571 tokens)**, and 91 %
of it is two files: the ADR index at 17,422 words and `WORKFLOW.md` at 11,679. **Neither carries a
G9 budget**, because G9 budgets by `type` and there is no budget for `adr` or `program`. The two
largest documents in the repository are the two `CLAUDE.md` instructs a session to load on every
planning task, and they are the two nothing bounded.

**Decision.** Load sets are **declared** in `docs/program/load-sets.md` and **priced** by G14. A set
names a budget in words and the files a session actually opens for that kind of task; the gate sums
them, fails over budget, fails on a member that matches no file, and prints the largest set's total
on every run whether or not it passes.

Four of the five budgets are a **ratchet, not an endorsement**: a few percent above today's
measurement, so nothing grows quietly. `planning` is not, and the gate is the reason.

**G14 went red on the commit that introduced it.** `planning` measured 32,009 words; the budget was
set at 33,000; writing this ADR and ADR-0042 added 1,674 words to the ADR index and the gate failed.
The change was not wrong — the ratchet was. The ADR index is **append-only by design** (ADR-0011),
so a budget a few percent above it turns red the next time anyone records a decision, and a gate
that punishes the practice it protects gets disabled rather than obeyed. `planning` therefore
carries a **ceiling with a structural answer attached**: 36,000, and when it is next reached the
answer is the split, not another raise. The other four sets contain no append-only document and stay
ratcheted.

**Why the budget is not derived from the research.** The evidence says degradation is continuous and
begins early. It does **not** fix a safe number, and no standards body does either — so a number
presented as though the literature fixed it would be exactly the anti-pattern in `CLAUDE.md`, a
textbook figure read as a specification. These budgets are **this repository's own engineering
decision**, in the same category as G9's, and they are labelled that way in the manifest.

**Alternatives considered.**
- *Give `adr` and `program` a G9 type budget.* The obvious move, and it fails immediately: the ADR
  index is 17× a rule's budget and cannot be trimmed to it — it is forty decision bodies. A budget
  that can only be met by deleting history is not a budget.
- *Count tokens with a real tokenizer.* More accurate and it adds a dependency to a lane that has
  none. Words × 1.33 is the approximation ADR-0012 already uses; consistency beats precision here.
- *Infer the load set from what a session actually read.* No mechanism exists to observe that, and
  inventing one would measure a transcript rather than the instructions. The manifest binds the
  **instructions**: if `CLAUDE.md` says to read something, it belongs in a set and gets priced.
- *Do nothing until a model demonstrably fails.* The failure mode is silent degradation, not an
  error, so waiting means never noticing.

**Consequences.**
- (+) The number is visible on every run. `G14 largest load set is 'planning' at 32,009 words` is
  printed by the gate, so growth is seen rather than discovered.
- (+) A new instruction that tells a session to read another document now has a price attached.
- (−) **`planning` is over any comfortable reading of the evidence and the budget blesses it.** The
  honest fix is structural and is recorded as backlog, not hidden: the ADR index is an index *and*
  forty bodies in one file, and its own footer already anticipates the split
  (`NNNN-title.md` "when extensive"). Until that split, a lower budget would only mean a red gate.
- (−) The manifest is a declaration of intent, not an observation. It can be honest and still be
  incomplete; it is only as good as the instructions it mirrors.

---

## ADR-0042 — The gates are proven by mutation, on every merge

**Status:** Accepted (owner-directed 2026-08-02)
**Materializes as:** `tools/test_gates.py`, wired into `make verify-full`

**Context.** Improvement-register #12 already stated the rule, in these words: *a new gate is proven
by planting a violation in the environment CI uses, not by reading its code.* It was learned the
expensive way — G13 was green locally and RED in CI three times.

The rule was written down and then performed **exactly once, by hand, for one gate**. Measured
before this decision: `verify.py` was 638 lines implementing thirteen gates over 230 documents with
**zero tests**, no per-gate functions and one `assert`. The next edit could break G4 in silence and
every run would still print GREEN — the same shape as ADR-0037, where green gates certified that
invented policy was well-organised.

**Decision.** `tools/test_gates.py` plants **one violation per gate** and asserts that the gate
fires **and that no other does**. It runs in `make verify-full`, at the merge boundary, not in the
`make verify` loop a session runs after every layer.

Three properties are deliberate:

1. **End-to-end, not unit.** `verify.py` is executed as a subprocess against a real git worktree,
   because that is what CI does. The one time this repository trusted a gate's code over its
   behaviour it went red three times.
2. **The worktree is populated from the index**, so the harness tests the gates *about to be
   committed*. A gate added in a change would otherwise be tested in its absence — precisely the
   failure being guarded against.
3. **Silence is a failure too.** A mutant caught by nobody is a hole; a mutant that trips a gate it
   should not is a false positive. Both fail, and expected collateral must be declared per mutant.

**This already paid for itself before it was merged.** The first version declared that a duplicated
document id would also trip G5 — reasoning that the losing document's `part-of` chain would resolve
to a node no longer answering to that name. Plausible, and wrong: both documents carry `part-of` to
the same index, so the chain resolves either way and G5 stays quiet. The harness contradicted its
own author on its first green run, which is the entire argument for running mutants instead of
reasoning about them.

**Alternatives considered.**
- *Refactor `verify.py` into one function per gate and unit-test them.* Cleaner to read, and it
  tests the functions rather than the program — losing exactly the environment coupling (shallow
  clones, merge refs, `git ls-files`) that produced every real failure so far. Worth doing later for
  readability; it is not a substitute.
- *Synthesise a minimal repository to mutate.* Faster, and it would need scaffolding that passes
  fourteen gates — a second estate to maintain, drifting from the real one.
- *Trust the review.* This is what was being done. It held for one gate.

**Consequences.**
- (+) Every future gate arrives with its mutant, or `verify-full` is not green. The drift guard P3
  needs and the metric-`kind` check M2b needs are both covered before they are written.
- (+) The rule from improvement #12 stops depending on someone remembering it.
- (−) `verify-full` gets slower: fifteen full gate runs, about twenty seconds. Acceptable at a merge
  boundary, which is why it is not in `verify`.
- (−) The mutants know the shape of the documents they edit. Renaming
  `goods-receipt-throughput.md` breaks the harness — a maintenance coupling, made explicit in the
  `TOUCHABLE` list rather than left to be discovered.

---

## ADR-0043 — The premise is measured: a context-adherence evaluation, decided by programs

**Status:** Accepted (owner-directed 2026-08-02, four options selected from a list per PLT-R6)
**Materializes as:** `docs/program/context-eval.md`, `tools/context_eval.py`, gate **G15**

**Context.** Fifteen gates verify that this estate is **internally consistent**. Not one verified
that an agent **reading** it produces something conforming to it — so the premise of the repository,
that a context makes an AI build correctly, was never measured. The only "golden" fixture in the
tree proves money arithmetic.

**Decision.** Five tasks, one per failure class that actually occurred here, scored by deterministic
programs. Four sub-decisions were put to the owner as a selectable list; all four recommendations
were taken.

**1. When it runs — a dated record plus a freshness gate.** The result is written into
`docs/program/context-eval.md` and **G15** fails once any context-defining file changes after the
recorded measurement. *Rejected:* a non-blocking CI job (needs an API key as a CI secret and a
model callable from the runner — a dependency and a per-run cost in a lane that has neither); a
blocking gate in `verify-full` (puts network and non-determinism in the merge gate, so an
unavailable model reddens unrelated changes, contradicting the other fifteen gates); running it
manually (improvement-register #15 had just named that shape — *if the mechanism is a person
remembering, the entry is not done* — and adopting it here would repeat the mistake in the same
week it was recorded).

**G15 compares digests, not dates.** `git log -1 -- <path>` is the obvious way to ask when a file
last changed, and it is wrong here for the reason G13 already paid for three red CI runs: at a
shallow clone's boundary git reports the graft, every file looks freshly changed, and the gate fires
on everything. A content hash needs no history at all. While a digest reads `(unmeasured)` the gate
**notes that it cannot check** rather than passing — a skip that reads as a pass is how a gate
reports success for work it never did.

**2. The subject is a cold subagent** loaded with the task's declared load set and nothing else.
*Rejected, and this is the one that decides whether the exercise means anything:* self-evaluation by
the session. A session that just wrote a rule cites it from memory and scores a meaningless 100 % —
it measures the conversation, not the context. The cold subagent also puts the ADR-0041 manifest
under test: if a task fails because the declared load set lacked what the task needed, **the
manifest is what is wrong**. Also rejected: an external API call (key, dependency, cost, a new lane
decision) and recorded fixtures (they age into measuring the *previous* context).

**3. The checks are the gates plus per-task deterministic assertions.** Gates alone were tempting —
zero new code, fifteen checks reused — and they miss the class that matters: **an invented threshold
with correct front-matter, a cited source and a compliant word count passes all fifteen.** That is
ADR-0037's defect exactly: well-structured and false. The per-task assertions add the semantic layer
without adding a judge — *did it cite MSR-R2? did it put a number next to a normative word? are the
unit codes in UN/ECE Rec 20?* — and each is a program.

**4. Five tasks plus a template.** One per failure class with a real history here: policy dressed as
law, a level aggregated as a flow, invented data wearing a standard's name (`KG` for `KGM`), a
family-wildcard citation, structural non-conformance. The corpus grows from incidents, as the
improvement register does — a task is added when a **new class appears**, never to raise a score.

**Never a judge model.** Position bias reaching **75 %** for the first-placed answer, with judgments
inverting when positions are swapped; verbosity bias; **10–25 %** self-preference, correlated with
self-recognition. GPT-4-class agreement with humans (>80 %) matches human–human agreement and
supports use as a **calibrated screening tool**, not as the thing that decides whether this context
works. Human raters are not clean either — they score assertive-but-wrong output 15–20 % above
cautious-but-right — which is the argument for preferring the deterministic option wherever one
exists, not for trusting either.

**Consequences.**
- (+) The repository's premise stops being an assumption. A regression in the context shows up as a
  failing task rather than as a defect discovered months later.
- (+) The load-set manifest gains a consumer that can contradict it.
- (+) The checkers are themselves tested: `--self-test` runs a compliant and a violating sample past
  each and requires it to pass one and fail the other. An untested checker would be ADR-0042's hole
  in a new place.
- (−) **The tasks are authored by the same process they evaluate.** Deterministic checks make the
  *verdict* objective; they do not make the *question set* impartial. A blind spot in the author is
  a blind spot in the corpus, and only a new incident reveals it — which is why the corpus is
  incident-driven rather than designed up front.
- (−) `level-metric` deliberately carries **no** check for "did it sum?" — no reliable regex exists,
  and a false accusation costs more here than a miss.
- (−) The measurement needs a subagent run; it cannot be produced by `make` alone. G15 makes its
  *absence* visible, which is the most a gate can do about work that requires a model.

---

## ADR-0044 — A fourth documentary form: `how-to`, and only about using this context

**Status:** Accepted (owner-directed 2026-08-03)
**Materializes as:** the `how-to` type, `docs/program/how-to/`, budget 900 words

**Context.** Against the four forms Diátaxis distinguishes — tutorial, how-to, reference,
explanation — this estate had **two**. The 182 concept nodes and 20 rule files are *reference*; the
ADRs are *explanation*. There was **no task-oriented document anywhere**, while the first line of
`CLAUDE.md` promises a project can learn "which supply-chain departments it needs **and how to
implement them**". The second half of that promise had no documentary form.

The first context-adherence run (ADR-0043) put a number on the cost. `new-concept-node` produced a
node that was structurally perfect and **806 words against a 700-word budget** — a budget stated
plainly in a file the agent had loaded. Nothing was missing from its inputs. What was missing was a
document that turns a stated rule into an **order of operations**.

**Decision.** `how-to` joins the closed `type` vocabulary. A how-to in this repository is about
**using this context** — adding a concept node, changing a rule, running the evaluation. Budget 900
words, and it lives under `docs/program/how-to/`.

**The scoping constraint is the whole decision, and it is why none existed before.** A how-to about
*running a department* — how to receive goods, how to score a supplier — would be **method an
organization can reasonably choose**, which is policy, which fails the inclusion test. That is very
likely why the form was never created: the obvious how-tos are forbidden, so the category looked
forbidden. It is not. The how-tos that belong are about the **context itself**, whose procedures are
this repository's own to fix.

**Verification, not assertion.** The guide was written, added to the `authoring-a-concept` load set
so G14 prices it, and the failing task was re-run against a fresh cold subagent: **633 words**, with
the answer naming the budget in its own report. The confound is recorded in
`program/context-eval.md` — the prompt also gained the CPT number and the `part-of` target — so the
result is stated as "the failing dimension moved and the answer explained why", not as a controlled
experiment.

**Alternatives considered.**
- *Use the existing `program` type.* No vocabulary change and no ADR needed. Rejected: `program`
  already holds the backlog, the evaluation protocol and the registers, which are neither
  task-oriented nor budgeted; a form whose whole point is being a distinct kind of document should be
  a distinct type, and G9 can then budget it.
- *Restate the budget more loudly in `knowledge-architecture.md`.* Cheapest of all, and it treats the
  problem as insufficient emphasis. The agent had read the number. Repetition was not the gap.
- *Write how-tos for the departments too.* The inclusion test forbids it, and the attempt is how a
  context re-acquires one company's habits.

**Consequences.**
- (+) The `CLAUDE.md` promise acquires a form, and the estate has three of Diátaxis's four.
- (+) A rule that keeps being broken now has somewhere to become operational, without the rule file
  growing prose that its budget cannot hold.
- (−) A twelfth `type`, and one more thing for a session to classify correctly.
- (−) **The forbidden how-to is one slip away.** "How to add a concept node" is legitimate; "how to
  set a receipt tolerance" is the ADR-0037 defect wearing this new form. The scoping rule is written
  into `knowledge-architecture.md` §8 next to the type itself rather than left in this ADR.
- (−) One guide is not a set. `changing-a-rule` and `running-the-evaluation` are the obvious next two
  and are recorded in the backlog, not written here.

## ADR-0045 — The Global Context has two axes, and no project uses all of it

**Status:** Accepted (owner-directed 2026-08-03)
**Materializes as:** the purpose section in `CLAUDE.md`; `docs/50-engineering/practice-areas.md`;
**PLT-R7**; the `what-is-this-for` context-adherence task

**Context.** Asked for a plain summary of the project, the estate's weakest point turned out not to
be rigour. Sixteen gates, a mutation harness and a context-adherence evaluation were all green, and
`CLAUDE.md` still named two things — a supply-chain knowledge base **and** a DevOps monitoring
dashboard — and **never said how they were connected**. The reason existed, buried in ADR-0030 among
forty-four decisions. No mechanism could have found this: every gate checks whether statements are
consistent, and none asks whether the estate says what it is *for*.

**Decision.** The Global Context carries **two axes**, stated at the entry point rather than derived:

- **How a company is run** — the fourteen supply-chain departments, which are the operating
  disciplines of any firm that buys, builds, delivers and accounts for things.
- **How software is engineered** — the practice areas a professional build rests on.

Neither axis describes *this* repository. Both exist for the **portfolio of projects** the context
governs, inside this workspace and beyond it. The monitoring application watches that portfolio, so
a company selling technology can decide from evidence rather than from impression — which is why a
knowledge repository ships a dashboard and nothing else.

**Three parts, and the third is the load-bearing one.**

1. The purpose stated in `CLAUDE.md`, at the top, where a reader arrives.
2. **`practice-areas.md`** — thirty-five engineering areas, each with the **external authority** that
   would make a statement in it admissible. A **roster, not content**: W5 forbids speculative
   pre-build, and the anchor is the part that cannot be improvised later, so the anchor is what gets
   recorded now.
3. **PLT-R7** — governing knowledge is **selected and declared to the owner before development
   begins**, never assumed. No project uses all of this context, and which parts apply is a
   declaration, not a default.

**Verified, not asserted.** A `what-is-this-for` task was added to the context-adherence evaluation
and answered by a cold subagent loaded with the `every-task` set: **PASS**. The claim being tested is
precisely the one no gate can make — that a reader of the entry point can state what the repository
is for.

**Alternatives considered.**
- *Explain the connection in ADR-0030.* Where it already was, and where it was found to be
  unreadable. A decision buried among forty-four is not an entry point.
- *Write the engineering axis out in full now.* Rejected by W5 and by the inclusion test: thirty-five
  areas of invented content is the ADR-0037 defect at a larger scale. The roster names the authority
  and stops.
- *Drop the monitoring application and be purely a knowledge base.* Coherent, and it discards the
  instrument that makes the portfolio visible. Rejected on the owner's direction; the two-axis model
  is what makes the dashboard follow from the purpose instead of sitting beside it.

**Consequences.**
- (+) The first thing a reader meets is why the repository exists, and the two halves are one thing.
- (+) PLT-R7 converts "which knowledge applies" from an assumption into a declared artefact.
- (−) `practice-areas.md` is a roster that will tempt someone to fill it in. The authority column is
  the guard: an area with no admissible source stays empty.
- (−) The purpose section is prose, and prose degrades. The `what-is-this-for` eval task is what
  stops it degrading again, and it is watched by G15.

## ADR-0046 — The context is versioned per node by digest, and tagged by calendar

**Status:** Accepted (owner-directed 2026-08-03) · **Narrows ADR-0011**
**Materializes as:** `docs/program/templates/knowledge-selection.md`; the `YYYY.MM` annotated tag

**Context.** ADR-0030 promised a "versioned substrate" and ADR-0011 proposed annotated **SemVer**
tags. **Zero tags existed**, and this was the last open decision in the estate.

**Decision, and the rejection is the substance of it.** **SemVer is rejected on a substantive
ground, not on effort.** A retired ID in this corpus is never reassigned and stays listed forever
(G11, G16), so **every prior citation resolves by construction** — the corpus cannot produce a
breaking change. That leaves SemVer's major component with nothing to encode, and a version scheme
whose principal signal is always zero is worse than none: it invites readers to infer compatibility
guarantees from a number that never moves.

Instead, two mechanisms for two different readers:

- **For the machine: a per-node content digest, `sha256:12`**, recorded **by the project** in its
  declaration — what it actually relied on, not which state the whole repository was in. This is the
  mechanism G15 already proves works, applied to a project's own artefact.
- **For the human: an annotated `YYYY.MM` tag**, a legible reference that claims nothing about
  compatibility because there is nothing to claim.

**The form is a template, and the honest consequence is stated rather than hidden.** The declaration
is the **project's** artefact, and PLT-R2 keeps project material out of the context — so the form
lives at `templates/knowledge-selection.md` and **no gate here can check that a project declared
anything**. That limit is written into the template itself.

**Alternatives considered.**
- *SemVer as ADR-0011 proposed.* Rejected above, on the ground that the major component is
  unreachable by construction.
- *A single repository-wide digest.* Simpler to produce and wrong for the consumer: a project relies
  on a handful of nodes, and a whole-repo digest changes when anything moves, so it reports drift the
  project does not have.
- *Version each node with a monotonic integer.* Requires the context to track per-node history it
  does not keep, and re-creates the compatibility promise the digest deliberately avoids.

**Consequences.**
- (+) The last open decision closes, and a project can state exactly what it consulted.
- (+) A digest is checkable by the project without asking this repository anything.
- (−) `YYYY.MM` says nothing about content, by design — a reader wanting "what changed" must read the
  ADR index, which is the honest answer.
- (−) The declaration is unenforceable from here. Stated in the template, and it is the price of
  PLT-R2.

## ADR-0047 — Money in the Rust core: integer minor units, exact decimal computation

**Status:** Accepted (owner-directed 2026-08-03) · **Supersedes ADR-0019**
**Materializes as:** `crates/scm-money`; **SCM-R14**; **ENG-R4/R5**; `tests/golden/money.golden.json`

**Context.** ADR-0019 decided *"arbitrary-precision Decimal end-to-end"* and named the estate it
applied to: `Money { amount: Decimal }` in TypeScript, `decimal.Decimal` in Python, `NUMERIC(19,4)`
in `schema.sql`, strings over gRPC. **Every one of those is gone** — ADR-0037 deleted the
application and ADR-0035 moved the core to Rust. What survived is `crates/scm-money`, and it does
**not** implement ADR-0019's decision: the representation is `i64` minor units, with `Decimal` used
as the *computation medium* rather than as the stored type. That reversal was never recorded, so the
accepted decision and the shipped code have disagreed since the crate was written.

**Decision — the two roles are separated, and that is the whole point.**

- **Representation is integer minor units** (`i64`). A stored amount carries no scale ambiguity, no
  trailing-zero question and no parse step; `Money { amount_cents: i64, currency: String }`.
  `i64` and not an unsigned type because a **credit** — a refund, a reversal, a negative
  adjustment — is a first-class value in this domain, not an error state.
- **Computation is exact decimal.** Every multiply, divide and allocation runs in `Decimal`, never a
  binary float, and quantizes **once**, at the boundary, with `roundTiesToEven` — IEEE 754-2019
  §4.3.3, exposed as the single named constant `MONEY_ROUNDING`. A rate enters through
  `Decimal::from_str_exact("0.0825")`, so no float ever reaches the calculation.
- **Apportionment is largest-remainder**, whose defining property is the arithmetic identity
  **SCM-R14**: the parts sum exactly to the whole. Independent rounding of each share does not have
  that property, which is why the method is fixed rather than chosen.

**Where this is more precise than ADR-0019, since that is the reason to replace it.** ADR-0019 fixed
the *type* and left the failure modes open. This fixes the failures:

- **Every operation is total.** `MoneyError` is a typed enum, so a caller matches a cause instead of
  parsing a message: `CurrencyMismatch`, `NonPositiveDivisor`, `EmptyWeights`, `NegativeWeight`,
  `NonPositiveWeightSum`, `Overflow`.
- **Overflow is reported, never wrapped.** Addition and subtraction go through `checked_add` /
  `checked_sub`. A silent wrap in money arithmetic is the worst available outcome, so it is an error
  value and not a possibility.
- **A non-positive divisor is an error, not a saturating result** — division by zero has no money
  interpretation, and returning something plausible is worse than refusing.
- **One rounding mode, one constant.** ADR-0019 said "explicit and banker's at defined boundaries";
  here the boundaries are the four public functions and the mode is a `const` they all share, so
  there is nowhere for a second convention to appear.

**The cross-language mechanism is the reason the golden file survives.**
`tests/golden/money.golden.json` was built when TypeScript and Python both had to agree; both are
gone, and the fixture stays because it encodes the *canonical answers* — including the two-step
refund quantization that a single round gets wrong by one minor unit. Today the Rust crate is its
only consumer. **When the NestJS gateway or the Python tools layer next handle money they read this
same file**, which is what keeps a second implementation from inventing its own rounding.

**Why this carries no policy, and therefore belongs here at all.** Banker's rounding is fixed by
IEEE 754; largest-remainder is a fixed method; the sum-preserving property is an identity. There is
no threshold, tolerance or target anywhere in the crate, which is precisely why it survived the sweep
that deleted ~25,700 lines. **If the monitoring application turns out never to handle money, the
crate should be deleted rather than kept for its own sake** — a lane owner with no caller is not an
asset.

**Alternatives considered.**
- *Keep ADR-0019 as written — `Decimal` as the stored representation.* Rejected on the ground that
  killed it in practice: a stored `Decimal` needs a scale convention at every boundary it crosses
  (DB column, wire format, telemetry row), and each convention is a place for the exactness to be
  renegotiated. Integer minor units have one meaning everywhere.
- *`i128` minor units.* Removes the overflow class outright. Rejected as unearned: `i64` minor units
  reach ±9.2 × 10¹⁶, `checked_*` makes overflow an explicit error rather than a corruption, and the
  wider type costs every downstream boundary a conversion. Revisit if a real amount approaches it.
- *A dedicated currency type instead of `String`.* Genuinely better — ISO 4217 is a closed list and a
  string admits `"EURO"`. Not adopted here because it belongs with the standards module that owns the
  ISO 4217 table, and inventing a second source for it is the defect this repository exists to avoid.
  **Recorded as the open follow-up**, not silently dropped.

**Consequences.**
- (+) The accepted decision and the shipped crate agree for the first time.
- (+) Failure modes are typed and total; overflow cannot corrupt an amount.
- (−) ADR-0019's estate-specific clauses (Postgres `NUMERIC`, gRPC strings) die with it. When those
  surfaces return in M4 they need their own statement, and it must derive from this one.
- (−) `currency: String` stays unvalidated until the follow-up above lands.

> **File map:** this README is the canonical ADR index. New decisions are appended here
> as `## ADR-NNNN — Title` (or as `docs/10-decisions/NNNN-title.md` when extensive).
> Numbers come from `00-governance/id-registry.md` §3.
