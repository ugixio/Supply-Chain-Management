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
- 🟦 **U7 · HOW lane** — Test debt: Python test suite (SCM-R13 currently unmet); extend
  TS unit coverage beyond the 4 existing files; every SCM-Rx gets its test.
  **Started 2026-07-22 (with P5 slice 3):** the pytest suite is now real and **enforced** —
  `services/calc/tests/test_money.py` runs in `make verify-full` and CI via `make test-py`
  (CI-light `requirements-dev.txt` = pytest only). First Python module under test is the
  money core. **Next:** extend pytest to the calc models (needs a heavier CI lane or mocked
  deps — risk #6), and add a test per SCM-Rx / department rule.
- 🟦 **U8 · HOW lane** — Cross-language consistency mechanism (golden test vectors shared
  by TS and Python — prevents another `a12c114`).
  **MECHANISM LANDED 2026-07-22:** `tests/golden/money.golden.json` is **one fixture file
  read by both languages** — `tests/unit/golden-money.test.ts` (Jest) and
  `services/calc/tests/test_golden_money.py` (pytest). 26 money vectors (multiply/divide/
  net-of-fee/allocate/refund) with a `why` on each; if TS and PY ever disagree, one suite
  goes red. Both suites run in `make verify-full`.
  **First divergence closed with it — refund rounding (CPT-0091, was U15b-class):** TS did
  one `Math.round` (float, half-up), PY two `round()` steps. **Canonical = two-step
  quantization, ROUND_HALF_EVEN at each step** (the gross line extension is
  document-visible so it quantizes first; the fee applies to that stated gross —
  e.g. `2.5 × 1299 @ 15%` → **2761**, not 2760). TS `calculateRefundCents` converged +
  exported (now catalogued in CPT-0091 — G10 correctly demanded it); PY `refund_amount`
  moved to exact `Decimal`. Concept node + dept-13 index updated.
  **Finding recorded:** the numbered calc dirs (`13_order_management`) are not importable
  packages and pull numpy/pandas, so a department function cannot be unit-tested in the
  CI-light lane — the golden test asserts the canonical structure always and the
  department implementation only when the full stack is present (`importorskip`).
  Fix is packaging at P6 (risk #6).
  **Next:** extend the fixture pattern to the remaining U15b divergences (service-level
  z-scores, safety-stock variants, MAPE units, CV estimator, ABC break-points, HHI input
  units, risk-matrix thresholds) — each becomes a vector set + a convergence decision.
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

- ✅ **U14 · WHAT lane** — Concept-node catalogue rollout (ADR-0015). **Landed
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
  **✅ ROLLOUT COMPLETE 2026-07-22 (branch `claude/supply-chain-framework-m6r3g6`):**
  all 12 remaining departments catalogued in census order — CPT-0036..0153 (118 new
  nodes across 06/08/02/10/13/09/11/05/07/14/04/12); every public calculation symbol
  now has a concept node or an explicit exclusion; **all 14 departments `enforced`,
  G10 census empty** (210 governed docs green). Regulatory facts were re-verified
  against 2026 sources during cataloguing; **drift recorded on the nodes**: CSDDD
  scope rewritten by Omnibus I (Directive (EU) 2026/470 — single >5,000-emp/€1.5B
  band from 26 Jul 2029); CBAM Omnibus (Oct 2025 — 50 t de-minimis, certificate sales
  from Feb 2027, 50% quarterly holding confirmed); EUDR delayed to 30 Dec 2026 with
  the official May-2025 country benchmark contradicting the hardcoded list.
  **Surfaced follow-ups → U15b grows:** per-department "Divergences surfaced" sections
  in each `25-concepts/<NN>/_index.md` record ~30 new TS/PY divergences and fidelity
  gaps (risk-matrix thresholds two levels apart; log-vs-linear PPM scoring; duplicate
  CO₂ factor tables; three 3WM tolerance policies; turnover/DIO triplicated; EUDR
  country list vs official benchmark; dock sizing ignoring `service_cv`; etc.) — each
  needs an owner call, feeding U8 golden vectors.
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
- 🟦 **P5 · WHAT+HOW** — Money → Decimal migration (ADR-0019). **Sliced (L/high-risk):**
  (1) `@scm/shared` Decimal money core · (2) domain call-site migration by department ·
  (3) Python `Decimal` context · (4) `NUMERIC` columns + string-over-gRPC · (5) golden
  vectors (U8) prove TS==PY==SQL.
  **Slice 1 LANDED 2026-07-22:** `decimal.js` added to `@scm/shared` (the ADR-0019-decided
  lib); `multiplyMoney` rewritten to compute in exact Decimal and round **ROUND_HALF_EVEN**
  (retires the live `Math.round(amount*factor)` float bug); added `subtractMoney` and
  `allocateMoney` (largest-remainder, sum-preserving — no lost/invented minor units) +
  `MONEY_ROUNDING` constant; `tests/unit/money.test.ts` (14 cases: banker's rounding, exact
  string rates, no-float-drift, sum-preserving allocation incl. negatives). Non-breaking:
  `Money.amount` stays integer-cents this slice (type→Decimal is slice 2+). verify-full green
  (54 tests).
  **Slice 2 LANDED 2026-07-22:** added shared `multiplyCents` / `divideCents` (Decimal +
  ROUND_HALF_EVEN; `multiplyMoney` now delegates to `multiplyCents`, DRY) and migrated the
  **4 unambiguous scalar money sites** off `Math.round(...)` float math: GoodsReceipt
  `totalReceivedValueCents` (01), LandedCost unit cost (11), InventoryValuation WAC (05),
  RiskItem EAL (10). `PurchaseOrder.calculatePOTotal` was already correct (it routes through
  the slice-1 `multiplyMoney`). +5 core tests (59 total), verify-full green.
  **Deferred (needs a convergence decision, not a mechanical change):**
  `ReturnAuthorization` refund (13) — its single-round structure diverges from Python
  `refund_amount`'s double-round (CPT-0091 divergence); resolve under U8/U15b. Upstream
  float *accumulation* in InventoryValuation `totalValueCents` (Σ qty×cost) noted for a
  later slice.
  **Slice 3 LANDED 2026-07-22:** the Python money core in `services/calc/shared/types.py`
  (`multiply_cents` / `divide_cents` / `allocate_cents` / `money_subtract` + `MONEY_ROUNDING`)
  using `decimal.Decimal` + ROUND_HALF_EVEN, **mirroring the TS core value-for-value** (float
  factors go via `str()` to match decimal.js). `services/calc/tests/test_money.py` asserts the
  **same inputs → same outputs as `money.test.ts`** (TS == PY confirmed) — the U8 seed. This
  also **starts U7**: `make test-py` (pytest on `services/calc/tests`, stdlib-only) joins
  `verify-full`; CI installs a CI-light `requirements-dev.txt` (pytest only; heavy ML stack
  stays out, risk #6). verify-full green (TS 59 + PY 5).
  **Next:** slice 4 — `NUMERIC` columns already exist in `schema.sql`; wire string-over-gRPC
  when P6 lands. Slice 5 / **U8** — promote the mirrored money cases into shared golden-vector
  fixtures and extend to the deferred `ReturnAuthorization` refund convergence (CPT-0091).
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

### Phase W — Tech-company operating model: Global Context + Workspace/Projects (ADR-0030/0031/0032; Accepted, owner-directed)

> Owner direction 2026-07-22: this is a **project/workspace modeled as a tech company** where
> **SCM is the operating discipline** (the Global Context) governing a **portfolio of Projects
> spanning all tech branches**; a **prompt-refinement gate** (ADR-0032) sits on every input; a
> future **Monitoring** connector adds real-time dashboards + metrics. Consolidated first as
> ADR-0030/0031/0032 + product-statement (plan⇄context, ADR-0010). Assumptions **A1/A2/A3
> RESOLVED**; **A4** (prompt-gate surface) owner-confirmable. Build is disciplined: per-branch
> practice and platform rules materialize **only per justified task**.

- ✅ **W0 · orchestrator** — Consolidate the direction into governance. **Landed 2026-07-22
  (branch `claude/supply-chain-framework-m6r3g6`, restarted from the merged default):**
  ADR-0030 (tech-company operating model — reframed from "platform"; A1 = SCM-as-operating-
  context, A2 = reference+overlay), ADR-0031 (monitoring connector; A3 = both, internal-first),
  ADR-0032 (prompt-refinement gate), `20-product-model/product-statement.md` +8 glossary rows,
  id-registry ADR→0032 + reserved platform family `PLT` (§2), decision-index one-liners (G9).
  Doc gates green.
- 🟦 **W2 · WHAT lane** — Model the platform bounded contexts. **Landed 2026-07-22:** the
  **Node Model** (`20-product-model/node-model.md`) — the workspace as a typed node+edge graph
  with **Regions** (Global Context + one per Project), grounded in the C4 model / arc42 so a
  developer can interpret every part; the **`PLT` rule family is now LIVE**
  (`30-foundation/platform/rule.md`, id-registry §1): PLT-R1 prompt-refinement gate (ADR-0032),
  PLT-R2 read-only project reference, PLT-R3 everything-connected (via G4/G5/G6), PLT-R4
  node/edge typing, PLT-R5 one-branch-per-project; glossary +Node/Edge/Region; platform rule
  home = `30-foundation/platform/` (cross-cutting axis above the 14 depts). Doc gates green.
  **Still open in W2 (next):** the `workspace`/`projects` **concept nodes** + the tech-branch
  taxonomy as an open data-driven set, and concept nodes for the refinement-value / project-
  progress metrics (feed W3/W4).
- ⬜ **W3 · HOW lane (Stage B)** — Build the workspace/projects bounded context: Postgres schema
  for the mutable project data domain (separate from the ADR-0024 knowledge read model),
  tenancy/auth, NestJS code-first GraphQL resolvers, project→context reference resolution +
  overlay, and the **prompt-refinement gate** (refine → show diff / opt-out → execute; retain
  original+improved). Reads the knowledge read model, never writes it.
- ⬜ **W4 · HOW lane (Stage C, ADR-0031)** — Monitoring connector: emit progress events from the
  W3 data model; connectors (internal-first, then external dev tools: GitHub/CI/issue-trackers);
  delivery metrics as `CPT-*` nodes; dashboards. Deferred until W3 lands.
- ⬜ **W5 · WHAT lane (as branches are onboarded)** — Per-tech-branch practice knowledge
  (AI/ML/Data/Backend/Frontend/DevOps/…): materialize a branch's standards/skills **only when a
  real project in that branch needs them** (no speculative pre-build — knowledge-architecture).

### Phase L — Exclusive lanes, Rust core & scale tier (ADR-0033/0034/0035/0036; owner-directed 2026-07-22)

> The owner set **exclusive technology lanes** (ENG-R8) and the **best-option verification gate**
> (ENG-R9), adopted **ClickHouse**, **Docker** and **Kubernetes** (ADR-0034), and then made the
> load-bearing call: **Rust is the complete core and Python is the tools layer** (ADR-0035) —
> TypeScript leaves the core entirely and survives only inside NestJS and Next.js. Monitoring
> scale is fixed at **tens of thousands of continuous telemetry series for project supervision**
> (ADR-0036).
>
> **Shape of the work.** L2–L3 are one **strangler migration**, not a rewrite: the Rust core grows
> department by department behind unchanged public behaviour, each ported unit proves itself
> against its existing tests **and** the U8 golden vectors before the TypeScript original is
> deleted, and `main` stays green throughout (**ENG-R10.6**; no long-lived rewrite branch).
> Nothing is built before its lane and its six ENG-R9 checks are stated.

- ✅ **L0 · orchestrator** — Consolidate the lane direction into governance. **Landed 2026-07-22:**
  ADR-0033 (exclusive lane map + communication rule), ADR-0034 (ClickHouse/Docker/Kubernetes;
  broker + cache still gated on measured volume), **ENG-R8** (lanes) and **ENG-R9** (six-check
  best-option gate) in `50-engineering/rule.md` with lane-trespassing anti-states, ENG-R9 wired
  into `evaluation.md` §1.5 so it runs *before* code, product-statement §3 lane table,
  id-registry (ADR→0034, ENG→R9).
- ✅ **L1 · orchestrator** — Consolidate the **core + telemetry** direction. **Resolved by the
  owner (2026-07-22) and landed:** volume = **tens of thousands, telemetry only, for project
  supervision** → **ADR-0036** (raw table + sort key `(project_id, metric, ts)`, monthly
  partitions, `Delta`/`ZSTD` + `Gorilla` codecs, `LowCardinality` labels, `AggregatingMergeTree`
  rollup cascade raw→1m→1h→1d, short raw TTL + long rollup retention, batched async inserts);
  core = **Rust complete** → **ADR-0035** (supersedes ADR-0001's TS-domain clause, narrows
  ADR-0033) plus **ENG-R10** (Rust core boundary), ENG-R1/R2 annotated as narrowed,
  product-statement §3 rewritten (TypeScript is no longer a lane owner), id-registry
  (ADR→0036, ENG→R10). *The old L1 question — event-vs-telemetry and order of magnitude — is
  answered; no schema tuning is left blocked.*
- 🟦 **L2 · WHAT+HOW** — **Rust core, slice 1: the money core** (the first port ADR-0035 names).
  **L2a landed 2026-07-26:** `crates/scm-money` — one `rust_decimal` implementation
  (`ROUND_HALF_EVEN` quantization at boundaries only; `multiply_cents` · `divide_cents` ·
  `net_of_fee_cents` · sum-preserving largest-remainder `allocate_cents` · `Money` with a
  currency guard), typed `MoneyError` (overflow **reported, never wrapped**), `unsafe_code`
  forbidden and clippy denying truncating casts, floats and `unwrap`. **Acceptance met:
  `tests/golden/money.golden.json` passes unchanged from a third reader (`cargo test`)**
  alongside Jest and pytest — 13 Rust tests. Toolchain landed: Cargo workspace, `make test-rs`
  in the FAST gate + `make lint-rs` (fmt + `clippy -D warnings`) in the merge gate, cargo cache
  in CI. `tools/verify.py` now parses `RS:` implementation bullets, resolves `pub fn`/`pub
  const`/`pub struct`/`pub enum` and scans `crates/*/src/NN-*` for department coverage, so
  **G10 protects the catalogue across the port** (ENG-R10.7). The primitives are catalogued as
  **CPT-0154** with all twelve RS/TS/PY links verified.
  **L2b remaining:** the **napi-rs** binding plus its cross-compilation matrix, `@scm/shared`
  and `services/calc/shared` delegating to the core, then deleting the two mirrors (107 + 70
  lines) once every call site is on the binding.
- 🟦 **L3 · WHAT+HOW** — **Collapse the duplication as the core absorbs it** (the 49 concepts
  implemented twice — source of ~30 documented divergences). Two directions, one lane map:
  *(a)* the **703 lines of TypeScript mathematics** (`Forecasting.ts` 207, `SafetyStock.ts` 140,
  `SPCChart.ts` 356) are **deleted, not ported** — mathematics is Python's lane; *(b)* the
  **314 invariant guards** across the 14 departments are **ported into the Rust core** and their
  Python duplicates deleted (stock-balance guard, FEFO, risk matrix, three-way match,
  UFLPA/REACH/CSDDD, OTD). Department by department, each with its tests and golden vectors green
  before deletion. Each removal updates its `CPT-*` node in the same commit (G10 enforces it).
  Blocks on P6 for the paths the core must still reach.
  **L3a landed 2026-07-26 — the safety-stock family (140 lines):** the surviving lane was
  covered *first* (`services/calc/tests/test_safety_stock.py`, 37 tests; `numpy` + `scipy`
  joined the CI-light requirements so Python's mathematics is testable in the merge gate), the
  **ADR-0028 z-score resolution landed** (`get_z_score` is now the exact `norm.ppf`; the coarse
  lookup table is deleted), and only then were `algorithms/SafetyStock.ts`, its barrel export
  and its 12 Jest tests removed. Ten `CPT-*` nodes repointed to the single owner in the same
  commit. **Order matters and was corrected here:** deleting the duplicate first would have left
  the surviving implementation with no CI coverage at all.
  **L3b started 2026-07-26 — `crates/scm-core`, department 01, PurchaseOrder (194 lines):**
  the first rules in the Rust core. `PurchaseOrder.ts`, its barrel exports and its 12 Jest tests
  are deleted; 19 Rust tests replace them. The port **strengthened** the aggregate rather than
  transliterating it: status is an `enum` (illegal transitions are exhaustive matches, not string
  comparisons), line currencies are checked against the order currency (the TS node documented
  mixed currency as "a data error the aggregate does not detect"), quantities must be positive
  (UCC Art. 2), and creation is **pure** — identity and timestamps are inputs, so opening the
  same order twice yields the same value. The total flows through `scm-money`, retiring the last
  `Math.round` money path in dept 01. Two gate improvements landed with it: G10 attributes
  `crates/*/src/dNN_*` to its department, and **G10 now fails on two nodes claiming one `CPT-*`
  number** — which is how the duplicate CPT-0026 node was found and deleted.
  Convention recorded: **calculations are free functions, lifecycle transitions are `impl`
  methods**, mirroring the existing TypeScript split so G10 stays pointed at calculations.
  **L3 remaining:** `Forecasting.ts` (207 lines — needs `statsmodels` in CI-light first) ·
  `SPCChart.ts` (356) · the other 13 departments' rule guards, department by department ·
  then **L2b** (napi-rs) once `apps/api` needs the core.
- ⬜ **L4 · HOW** — **ClickHouse telemetry tier (ADR-0034/0036).** The ADR-0036 schema exactly:
  raw `MergeTree` on `(project_id, metric, ts)` partitioned `toYYYYMM(ts)`, per-column codecs,
  the four-level `AggregatingMergeTree` rollup cascade as **ingest-time materialized views**,
  raw TTL + rollup retention, **split-privilege users** (INSERT-only ingest vs SELECT-only queries
  with row/memory/time quotas), TLS, rebuild-from-truth procedure + a drift check. Read path
  exclusively through NestJS; every supervision metric documented as a `CPT-*` node
  (ADR-0031/0015) matching the view that computes it.
- ⬜ **L5 · HOW** — **Rust ingestion workers** — the connector path (normalize → validate →
  deduplicate → **batch** insert; `async_insert` or client-side batching, never row-by-row).
  Ingestion is core work (ADR-0035): NestJS may only serve the frontend and Python's lane is
  mathematics. OpenTelemetry spans propagate from the gateway through the core (ADR-0035).
- ⬜ **L6 · HOW** — **Docker** images for every service (non-root, minimal base, pinned digests,
  no secrets in layers; multi-stage for the Rust core so only the artefact ships) + Compose for
  local composition. **Kubernetes** afterwards, once ≥2 long-running services exist: ClickHouse
  via an operator with persistent volumes, config/secrets, network policy restricting the frontend
  to NestJS only.

### Phase 1 — Product evolution (owner-defined)
- ⬜ Resolve the open decisions in `10-decisions/README.md` (runtime/persistence, API
  surface, versioning) — they gate any application layer built on these domains.
