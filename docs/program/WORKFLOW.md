---
id: program-workflow
title: "Development Workflow (orchestrator playbook + backlog)"
type: program
owner: orchestrator
status: active
since: 2026-07-19
updated: 2026-07-19
relations:
  - { type: part-of, target: index-program }
  - { type: governed-by, target: governance-root }
---
# Development workflow (orchestrator playbook + backlog)

> The **human orchestrates**; the AI executes bounded tasks from
> `templates/task.md`. Before each task the AI loads: `CLAUDE.md` + ADRs → the relevant
> department SKILL (`.claude/skills/<dept>/`) + README → the unit spec (when specs
> exist). Never the whole repo.

## Standing rules (checked on every task)

- **Plan⇄context check (ADR-0010):** any change that introduces or renames a product
  concept lands in the model/ADR/rules FIRST, then in code.
- Every rule touched must keep its test (SCM-Rx and future department families).
- Follow-ups surfaced by a task are recorded HERE — never silently dropped.
- A task ends with green `typecheck`/`lint`/`test` + a proposed commit; the owner decides
  the merge.

## State of the estate (adoption audit, 2026-07-19)

**Strong:** 14 departments of domain logic (TS) + models (Python) grounded in named
standards; per-department README/IMPLEMENTATION/SKILL; regulatory framework doc;
English-only enforced; OSI-only policy with named substitutes.

**Gaps found (now the backlog below):** no decision log (→ retroactive ADRs landed,
review pending) · rules had no stable IDs (→ SCM-R1..R13 landed; per-department pending)
· no LICENSE file despite `package.json` "MIT" · no lockfile · no CI / no `verify` gate ·
no git tags · thin tests (4 TS unit files; **zero Python test files** vs the SCM-R13
mirror-coverage bar) · duplicated formulas across TS/Python with one past divergence
(commit `a12c114`) · no runtime/persistence/API decision recorded.

## Ordered backlog

> Status: ⬜ pending · 🟦 in progress · ✅ done. Entries are appended and annotated,
> never rewritten. A 🟦 entry ALWAYS records current state + next step, so a fresh
> session resumes without re-derivation (ADR-0012).

### Phase U — Unification (context-skeleton adoption)
- ✅ **U1 · orchestrator** — Skeleton added on branch `feat/context-skeleton`: tier tree,
  knowledge-architecture (instantiated allowlist), id-registry (SCM live; 14 families
  reserved), out-of-scope (seeded from the prohibited-tech policy), ADR-0001..0009
  retroactive + 0010/0011 proposed, glossary (seeded), scm-core rule.md (SCM-R1..R13),
  40-contexts knowledge map, program area + 6 templates, additive `CLAUDE.md` governance
  section. **Nothing existing was moved, renamed or rewritten.**
- ⬜ **U2 · human** — Review & ratify ADR-0001..0009 (retroactive), decide ADR-0010/0011,
  and merge the branch.
- ⬜ **U3 · orchestrator** — Dedup pass: `CLAUDE.md` §Critical Business Rules /
  §Code Standards cite SCM-R1..R13 instead of restating (SSOT).
- ✅ **U4 · WHAT lane** — Per-department `rule.md` × 14: extract each department's
  invariants from its code/README into its reserved family (PRC, SUP, DMD, …).
  **Landed 2026-07-20 (branch `feat/per-department-rules`):** all 14 `rule.md` created
  under `docs/40-contexts/NN-<dept>/`, invariants extracted from real domain code (throw
  guards, state machines, thresholds), inherited `SCM-R*` referenced never restated;
  id-registry §1 families moved to LIVE; 40-contexts map marked done; doc gates green.
  Branch also cherry-picks the rule-ID regex fix (`fix/verify-rule-id-regex`) it depends
  on. **Surfaced follow-ups → U13, and U7 (each new rule ID still needs its test).**
- ✅ **U5 · human** — LICENSE file + license decision (open decision; note the AGPL
  dependency flag in ADR-0002).
  **Resolved 2026-07-19: MIT (ADR-0014)** — LICENSE file committed matching the
  `package.json` declaration; owner instructed. AGPL re-evaluation stays conditional on
  commercial distribution.
- ✅ **U6 · HOW lane** — Reproducibility & gates: package-manager ADR + committed
  lockfile; `verify` script (typecheck + lint + jest + pytest + doc gates G1..G4 to
  start); CI.
  **Landed 2026-07-19 (branch `feat/context-skeleton`, ADR-0012/0013):** `tools/verify.py`
  (doc gates G1–G7+G9) · `Makefile` (`verify` fast / `verify-full` merge gate) · CI
  workflow (`npm ci` + `make verify-full`) · `package-lock.json` committed ·
  `@typescript-eslint` bumped to `^8` (the declared `^7` was uninstallable next to
  `eslint ^9` — improvement register #2). First real toolchain run also repaired:
  dead `tsconfig` path aliases (pre-reorg layout), 4 test suites importing the pre-reorg
  paths, 2 ambiguous domain barrels (07, 08), and 2 genuine type bugs (SupplierScorecard
  `ncrRate` using the wrong metrics group; REACH compliance reading an excluded input
  field — now conservative, see U11). Result: typecheck 0 errors, 40/40 tests green.
  **Still open inside U6 → follow-ups:** eslint flat config (U12) · pytest gate (U7).
- ⬜ **U7 · HOW lane** — Test debt: Python test suite (SCM-R13 currently unmet); extend
  TS unit coverage beyond the 4 existing files; every SCM-Rx gets its test.
- ⬜ **U8 · HOW lane** — Cross-language consistency mechanism (golden test vectors shared
  by TS and Python — see open decision; prevents another `a12c114`).
- ✅ **U9 · orchestrator** — Stamp front-matter on `docs/standards/REGULATORY_FRAMEWORK.md`
  (or keep grandfathered — record which).
  **Resolved 2026-07-19: keep grandfathered** (allowlisted in knowledge-architecture §3
  and enforced as such by `tools/verify.py`); typing it would shoehorn the closed `type`
  vocabulary. Revisit only if a standards/ document class is ever justified.
- ⬜ **U10 · human** — Review & ratify ADR-0012 (context economics + gates) and ADR-0013
  (npm + lockfile) together with U2; ratifying ADR-0012 includes declaring the exemplar
  department (candidate: `01-procurement`).
- 🟦 **U11 · WHAT lane** — **order-management numbering collision RESOLVED by ADR-0029** (dir dissolved → dept 13 namespace; census fixed). Remaining: fine split of 3 agility/VaR fns → dept 10, blocked on a Python env. Rest of U11 below stands.
- ⬜ **U11b · WHAT lane** — Domain dedup & modeling follow-ups surfaced by the toolchain
  repair: `Shipment.ts` redefines `TransportMode`/`TrackingEvent` already owned by
  `TransportLane.ts`/`TrackingEvent.ts` (aliased in the barrel for now — unify);
  `python/07_order_management/` vs `python/13_order_management/` numbering collision
  (risk register #4); REACH: model ECHA-notification tracking so compliance can reflect
  a submitted notification (currently conservative: required ⇒ not yet compliant).
- ⬜ **U12 · HOW lane** — eslint 9 flat config (`eslint.config.mjs`) + wire `lint` into
  `make verify-full` (QA warnings-as-errors bar).
- ⬜ **U13 · HOW lane** — Enforce LOG-R3 in code: `Shipment` types `hazmatClass` as
  optional and does not reject an `isHazmat` line missing its IMDG/ADR class, UN number,
  proper shipping name or packing group, though the README mandates it. Add the guard +
  its test (surfaced by U4 while writing `40-contexts/07-logistics-transportation/rule.md`).

- 🟦 **U14 · WHAT lane** — Concept-node catalogue rollout (ADR-0015). **Landed
  2026-07-20:** `docs/25-concepts/` tier, `type: concept` (Tier 3), family `CPT`,
  template, gate **G10** (verifies every `## Implementations` symbol link resolves to a
  real definition; reports/enforces coverage per department). **Exemplar
  `03-demand-planning` is `enforced` and complete: CPT-0001..0023 cover all 57 public
  calculation symbols (392 estate-wide).** G10 was negative-tested — it fails on a renamed symbol and on a
  deleted node.
  **Current state:** 13 departments in `census` mode. **Next step:** catalogue them in
  descending census order — 06 (51 symbols) · 08 (44) · 01 (33) · 02 (33) · 10 (28) ·
  09 (25) · 11 (24) · 05 (22) · 07 (22) · 13 (20) · 14 (13) · 04 (12) · 12 (8);
  **335 symbols outstanding**. Flip each to `enforced` in `25-concepts/_index.md` as it
  completes. Run `python3 tools/verify.py` for the live census.
- 🟦 **U15 · WHAT lane** — **z-score RESOLVED by ADR-0028** (canonical = exact inverse-normal). Remaining items 2–7 below stand.
- ⬜ **U15b · WHAT lane** — Cross-language divergences surfaced by U4's concept nodes. These
  are **findings, not fixes**: each needs an owner decision on which side is canonical
  (feeds U8's golden-vector mechanism).
  1. **Service-level z-scores (CPT-0003)** — TS takes **percent** (`95`), Python takes a
     **fraction** (`0.95`); TS rounds to 2 dp (95% → 1.65) vs Python 3 dp (1.645); the TS
     table carries 91–94% and 96%, Python jumps 90 → 95. Different safety stock from the
     same inputs.
  2. **`safetyStockByDays` vs `safety_stock_days` (CPT-0012)** — **different formulas**,
     not a port. TS: `D̄ × safetyDays` (planner-chosen cover). PY:
     `D̄ × (LT_max − LT_avg)` (lead-time overrun only, collapses to 0 when lead time is
     stable). Same name, different method.
  3. **`selectAlgorithm` vs `select_algorithm` (CPT-0011)** — TS is a rule-based
     dispatcher returning an algorithm **name** from caller-supplied flags; Python runs an
     **80/20 holdout backtest** and returns a fitted `ForecastResult`. Different inputs,
     different outputs, same name.
  4. **MAPE units (CPT-0008)** — `mape()` returns a **percentage** (×100) but
     `accuracy_suite()` reports `MAPE` as a **fraction**. A caller mixing them is off 100×.
  5. **Argument order** — `safetyStockAverageMax` / `safety_stock_combined` take their
     parameters in substantially different orders across the two languages.
  6. **CV estimator (CPT-0018)** — Python uses NumPy's `ddof=0` (population) σ; the TS
     caller chooses. On short history this moves SKUs across the X/Y/Z thresholds.
  7. **Return typing** — TS safety-stock functions `Math.ceil` to integers; Python returns
     floats. Decide whether rounding is a domain rule or a presentation concern.
- ⬜ **U16 · WHAT lane** — TypeScript coverage gaps found while cataloguing 03: **no TS
  implementation** of Croston / SBA (CPT-0006/0007 — intermittent demand is unavailable to
  the domain layer), of the scale-free accuracy metrics (CPT-0009), or of tracking
  signal / forecast bias (CPT-0010). Decide per item whether TS needs it (ADR-0001 puts
  analytics in Python, so some of these may be correctly Python-only — record the ruling).
- ⬜ **U17 · WHAT lane** — Domain-coverage candidates against SCOR-DS, surfaced by the
  ADR-0015 analysis and **not yet confirmed**: (a) **Make** has no department — BOM/MPS
  live in `04-supply-planning` but there is no production execution; (b) no **network
  design / facility location**; (c) SCOR-DS **Orchestrate** is unmapped. Confirm against
  the full census before proposing a 15th department (which requires an ADR — id-registry §4).

- 🟦 **U18 · WHAT lane** — Extract-and-archive the department business-context documents
  (ADR-0016). **The problem:** 14 `IMPLEMENTATION.md` (128,240 words) + 14 dept
  `README.md` (22,082) = **150,322 words outside the governed tree, vs 29,522 inside —
  the governed tree is 16% of the repo's prose.** Allowlisted ⇒ invisible to every gate.
  They specify a **different system** (SAP S/4HANA · Ariba · PostgreSQL · Superset ·
  Airflow star-schema BI) with no counterpart in `src/`. Risk register #7, #8.

  **Method (proven on 03, 2026-07-20):**
  1. Read §Business Rules → append to the department's `rule.md` as new stable IDs,
     marked explicitly when **not yet enforced in code**.
  2. Read §KPIs and Formulas → one `CPT-*` concept node each. A KPI with no implementation
     gets `status: draft` + a `## Status — specified, NOT implemented` section.
  3. Read §Validations → `## Mandatory validations` in `rule.md`.
  4. Discard: data model, star schema, dashboard pages, DAG schedules, roadmaps — all
     non-normative per ADR-0016 §1.
  5. When a department is fully extracted, stamp its `IMPLEMENTATION.md` as archived with
     a pointer to the governed nodes, and narrow the allowlist.

  **Landed for 03-demand-planning:** DMD-R5..R8 extracted (forecastability, APE
  zero-handling, override classification, SS adequacy bands) · CPT-0024 **Forecast Value
  Added** and CPT-0025 **safety-stock coverage/adequacy** created — **both required KPIs
  with zero implementation anywhere in the repo** · the service-level→z validation
  recorded as currently unsatisfiable (risk #9).
  **Current state:** 03 extraction covers §9, §10, §12. **Not yet done for 03:** §11
  analytical logic, §15 use cases, §17 test cases (TC-01..TC-06 are ready-made test
  specs — feed them to U7), and the archival stamp (deferred until 03 is fully extracted).
  **Next step:** finish 03 §11/§15/§17, stamp it archived, then repeat by census order.
- ⬜ **U19 · HOW lane** — Implement the two specified-but-missing KPIs found by U18:
  Forecast Value Added (CPT-0024) and safety-stock coverage/adequacy (CPT-0025), with
  tests, in whichever language ADR-0001 assigns. Both have dashboard/escalation
  requirements in the business-context document and no code at all.

### Phase P — Product build (ADR-0017..0021; owner-directed 2026-07-20)

> Staged full-stack app. **Only Stage A (wiki) is authorized to start.** Every task gated
> on `make verify-full`; the domain in `src/departments` is preserved, not rewritten.

- ✅ **P0 · human** — Ratify the product decisions. **Done 2026-07-20:** owner authorized
  proceeding on all proposed ADRs; **ADR-0010..0029 are Accepted (owner-authorized)**. This
  authorizes the money migration (P5, ADR-0019) and the agent layer (ADR-0027).
- ⬜ **P1 · orchestrator** — Materialize the reserved `docs/50-engineering/` tier: `_index`,
  an `ENG-*` rule family (layering rules per ADR-0023 — dependency direction
  `apps → infrastructure → application → domain`, `domain` imports nothing, cross-department
  only through application ports; boundary linter fails violations), and a frontend-UX ADR
  for the octagon node-graph (octagon shape, LED-cyan stroke, transparent fill, right
  sidebar, interaction states, a11y, light/dark).
- 🟦 **P2 · HOW lane** — Monorepo restructure per **ADR-0022/0023**. **Landed
  2026-07-20 (structure + wiring, verify-full green):** `git mv src/departments →
  packages/domain/src`, `src/shared → packages/shared/src`, `python → services/calc`; old
  top-level barrel removed; `@scm/shared` / `@scm/domain` path aliases (tsconfig `paths` +
  jest `moduleNameMapper`) so typecheck (0 errors) and jest (40/40) resolve without pnpm
  linking; 61 domain imports + 4 test imports rewritten; concept-node links, `verify.py`
  (`is_allowlisted`, `DEPT_NUMBER`) and the knowledge-architecture allowlist repointed;
  scaffolds for `apps/{web,api}`, `packages/{application,infrastructure}`, `proto/` with
  READMEs; `pnpm-workspace.yaml`, `turbo.json`, `@scm/{domain,shared}` package.json.
  **Activation sub-step — LANDED 2026-07-20 (verify-full green under pnpm):** `pnpm
  install` run, **`package-lock.json` → `pnpm-lock.yaml`** migrated, root manifest reduced
  to dev-tooling + `turbo` (unused `date-fns`/`zod`/`decimal.js` dropped — YAGNI;
  `decimal.js` returns to `@scm/shared` at P5), honest per-package manifests
  (`@scm/domain` → `uuid` + `@scm/shared` workspace:*; `@scm/shared` → none external),
  `Makefile` switched to `pnpm -s exec`, **CI switched to `pnpm/action-setup@v4` +
  `pnpm install --frozen-lockfile`**, `.turbo/` git-ignored. `turbo run build` is wired in
  the root `build` script but not yet in the gate (no per-package build configs exist until
  apps land — P3+); typecheck/jest still run once at root over all packages, which is
  correct for the current surface.
  **NOT done (deferred, own decision):** the `07_order_management` vs `13_order_management`
  merge — the two `order_metrics.py` files **differ**, so it needs a domain call, not a
  mechanical move (stays U11/risk #4; both preserved under `services/calc/` for now).
  **Superseded plan text below is retained for history:**
- ⬜ **P2 (original plan) · HOW lane** — Monorepo skeleton per **ADR-0022/0023**, without breaking `src/`:
  **pnpm workspaces + Turborepo** (`pnpm-workspace.yaml`, migrate `package-lock.json` →
  `pnpm-lock.yaml`, CI → `pnpm install --frozen-lockfile`, `make verify-full` delegates to
  `turbo run`). Layout: `apps/web` · `apps/api` · `packages/{domain,application,infrastructure,shared}`
  · `services/calc` · `proto/`. **`packages/domain` = today's `src/departments`** (moved,
  barrel + path alias preserved); **`packages/shared` = `src/shared`**. `docs/ tools/ .claude/`
  stay at root. Fix the `07_order_management` → `13_order_management` collision (risk #4/U11)
  during the move. Update the 4 test imports.
- ⬜ **P3 · HOW lane (Stage A)** — **Postgres read model (ADR-0024)** + **code-first GraphQL
  (ADR-0025)**. `tools/ingest`: one-way build reading `docs/25-concepts` + `rule.md` +
  `40-contexts` into read-model tables (drop-and-rebuild; `docs/` stays SSOT). NestJS
  code-first resolvers expose nodes/edges; `schema.gql` emitted + committed; DataLoader
  batching; contract tests. Drift guard (future gate G11) asserts ingested counts match
  `docs/`.
- ⬜ **P4 · HOW lane (Stage A)** — Next.js octagon node-graph front end per the P1 UX ADR;
  SCM core node centre, 14 department nodes around it as a connected circuit, CPT sub-nodes
  on expand; click → right sidebar rendering the concept node (formula, worked example,
  links). Accessibility + light/dark.
- ⬜ **P5 · WHAT+HOW (blocks on P0)** — Money → Decimal migration (ADR-0019): `Money` type,
  `multiplyMoney`/allocation with `ROUND_HALF_EVEN`, Python `Decimal` context, `NUMERIC`
  columns, string-over-gRPC. Golden vectors (U8) prove TS==PY==SQL. Retires the live
  `Math.round(amount*factor)` precision bug.
- ⬜ **P6 · HOW lane (Stage B)** — Python gRPC calc service (`scm.calc.v1`), NestJS client;
  interactive calculator for the demand-planning concepts first (the `enforced` dept).
- ⬜ **P7 · HOW lane (Stage C, planned)** — Clean-Architecture wiring of `src/departments`
  to durable event-sourced Postgres (`EventStore` → adapter over an event table, ADR-0005
  realized), use-case ring, auth/RBAC, audit. Not scheduled.

- ✅ **P1a · orchestrator** — Agent layer formalized (ADR-0027; resolves the open
  "Agent lanes" decision). **Landed 2026-07-20:** 7 least-privilege agent profiles in
  `.claude/agents/` (architect, domain-knowledge, backend-/frontend-/data-/calc-engineer,
  quality-reviewer) + 7 technology/practice skills in `.claude/skills/`
  (engineering-standards, clean-architecture, nestjs-graphql, nextjs-frontend,
  postgresql-data, python-precision-grpc, testing-quality) + `.claude/agents/README.md`
  index. Profiles reference the governance (never restate it), declare least-privilege
  tools (quality-reviewer read-only), and encode the repo's proven protocols
  (`evaluation.md`, `operating-model.md` §4). Main session stays the orchestrator.
  `operating-model.md` §1 layer 2 + §2 updated; open decision closed. `.claude/**` is
  allowlisted (ungated) — the "references, never restates" rule keeps the gated docs the
  source. **Note:** the frontend-UX `ENG-*`/`50-engineering/frontend` tokens and the
  boundary linter (ENG-R1 enforcement) are still P1 proper.

### Phase 1 — Product evolution (owner-defined)
- ⬜ Resolve the open decisions in `10-decisions/README.md` (runtime/persistence, API
  surface, versioning) — they gate any application layer built on these domains.
