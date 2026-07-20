---
id: index-adr
title: "Architecture Decision Records (ADR-0001..0029)"
type: adr
owner: orchestrator
status: active
since: 2026-07-19
updated: 2026-07-19
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
- ADR-0019 — Money becomes **arbitrary-precision Decimal** end-to-end (`decimal.js` / `decimal.Decimal` / `NUMERIC(19,4)`); **supersedes the integer-cent clause of ADR-0006 and rewrites SCM-R8**. (accepted 2026-07-20)
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

---

## ADR-0001 — Two-language split: TypeScript domain logic + Python analytics/ML

**Status:** Accepted (retroactive)

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

**Status:** Accepted (retroactive)

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

**Status:** Accepted (retroactive) · **money clause superseded by ADR-0019**

> **Superseded in part:** the integer-cent `Money` clause below is replaced by ADR-0019
> (arbitrary-precision Decimal). The other three conventions — ISO 8601/UTC dates, GS1
> UOM, immutable SKU — remain in force, unchanged.

**Decision:** `Money.amount` is always integer cents (no floats); dates ISO 8601 with UTC
timestamps; quantity UOM codes per GS1 (`shared/types.ts`); SKU codes immutable once
created (lifecycle via status flags ACTIVE/DISCONTINUED/BLOCKED).

**Evidence:** `CLAUDE.md` §Code Standards; `src/shared/types.ts`.

**Consequences:** (+) no floating-point money bugs; interoperable identifiers. (−) all
arithmetic must round at defined points. Now citable as SCM-R8..R11
(`30-foundation/scm-core/rule.md`).

---

## ADR-0007 — Soft-delete for financial records + idempotent inventory transactions

**Status:** Accepted (retroactive)

**Decision:** POs, invoices, stock movements, shipments and scorecards are **never
hard-deleted** (`isDeleted` flag); inventory transactions carry an `idempotencyKey` and
are safe to retry.

**Evidence:** `CLAUDE.md` §Critical Business Rules #3, §Code Standards.

**Consequences:** (+) audit integrity + safe retries. (−) queries must filter soft-deleted
rows. Citable as SCM-R3 / SCM-R12.

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

**Status:** Accepted (retroactive)

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

**Status:** Accepted (owner-authorized 2026-07-20)

**Context:** History mixes styles (`feat(wave-d): …` vs `Add … files`). No tags exist;
`package.json` says 1.0.0 with no tagged release. No branch protection convention is
recorded.

**Decision (proposed):** Conventional Commits with department/area scope; short branches
per unit of work merged green; annotated SemVer tags for demonstrable states; the default
branch always builds with green tests; secrets never committed.

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

- [ ] **Runtime & persistence architecture.** Per-department `schema.sql` files exist but
      no engine choice, migration runner or application layer is recorded. What executes
      this domain logic, and against what store?
- [ ] **API/product surface.** Library? Service? UI? Nothing is recorded.
- [x] **Package manager + lockfile.** → **ADR-0013** (npm + `package-lock.json`).
- [x] **Repository LICENSE file.** → **ADR-0014** (MIT, matching `package.json`; the
      AGPL note in ADR-0002 re-applies only on future commercial distribution).
- [x] **CI + verify green-gate.** → **ADR-0012** (`make verify` / `make verify-full`,
      doc gates G1–G7+G9, CI workflow). Still pending inside it: eslint flat config
      (lint) and the pytest gate (U7) — tracked in `program/WORKFLOW.md`.
- [ ] **Versioning scheme.** First annotated tag; what 1.0.0 means (ADR-0011 pending).
- [x] **Agent lanes.** ~~Formalize WHAT/HOW/SPECIALTY lanes and profiles or keep
      single-orchestrator mode.~~ **Resolved by ADR-0027** (2026-07-20): formalized — 7
      least-privilege agent profiles + 7 technology skills; main session orchestrates.
- [ ] **Cross-language consistency policy.** TS and Python implement overlapping formulas
      (e.g. risk bands — see fix `a12c114`); decide the single-source mechanism (shared
      spec, golden tests, or codegen). **Concept nodes (ADR-0015) now make each
      divergence visible** — the first census already surfaced the service-level
      z-score tables (`CPT-0003`); they do not resolve it.

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
**Rewrites:** SCM-R8

**Context:** Three incompatible money representations coexist: `Money.amount: number`
(integer cents, SCM-R8), Python `float64` (numpy), and `NUMERIC` in `schema.sql`. Worse,
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

**SCM-R8 is rewritten** from "Money is integer cents" to "Money is arbitrary-precision
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

> **File map:** this README is the canonical ADR index. New decisions are appended here
> as `## ADR-NNNN — Title` (or as `docs/10-decisions/NNNN-title.md` when extensive).
> Numbers come from `00-governance/id-registry.md` §3.
