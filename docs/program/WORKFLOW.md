---
id: program-workflow
title: "Development Workflow (orchestrator playbook + backlog)"
type: program
owner: orchestrator
status: active
since: 2026-07-19
updated: 2026-08-03
relations:
  - { type: part-of, target: index-program }
  - { type: governed-by, target: governance-root }
---
# Development workflow (orchestrator playbook + backlog)

> The **human orchestrates**; the AI executes bounded tasks from
> `templates/task.md`. Before each task the AI loads: `CLAUDE.md` + **the ADR index entries** (the
> bodies are looked up by ID, not read whole — see `program/load-sets.md`) → the relevant
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
review pending) · rules had no stable IDs (→ the cross-department family landed; per-department pending)
· no LICENSE file despite `package.json` "MIT" · no lockfile · no CI / no `verify` gate ·
no git tags · thin tests (4 TS unit files; **zero Python test files** vs the then-stated
mirror-coverage bar) · duplicated formulas across TS/Python with one past divergence
(commit `a12c114`) · no runtime/persistence/API decision recorded.

## Ordered backlog

> Status: ⬜ pending · 🟦 in progress · ✅ done · ⛔ void · ⚠ needs an owner decision. Entries
> are appended and annotated, never rewritten. A 🟦 entry ALWAYS records current state + next
> step, so a fresh session resumes without re-derivation (ADR-0012).

### Closed triages — archived

The triages of **2026-07-29** (what ADR-0037 did to this backlog) and **2026-08-02** (markers that
stopped matching the estate) are complete and moved verbatim to
[WORKFLOW-archive.md](WORKFLOW-archive.md). Nothing was deleted or restated: the `planning` load set
reached its ceiling and this was the structural answer, taken instead of a raise.

### Phase X — How the AI uses the context (raised and started 2026-08-02)

> **Why this phase exists.** The owner asked for research into improvements, verified against what
> this repository actually is: **a context an AI follows to build, monitor and develop projects**.
> Two of the findings came from measuring the repository rather than from the literature, and both
> were holes nothing was looking at.

- ✅ **X1 · The gates are tested (ADR-0042).** `verify.py` was 638 lines and thirteen gates over 230
  documents with **zero tests**, one `assert` and no per-gate functions. Improvement-register #12
  had already written the rule — *a gate is proven by planting a violation* — and it had been
  performed once, by hand, for G13. `tools/test_gates.py` now does it for every gate on every merge.
- ✅ **X2 · Load sets are priced (ADR-0041, gate G14).** G9 budgets a document; nothing budgeted what
  a session reads **together**, which is what the long-context evidence is about. Measured:
  `planning` reads **33,804 words (~45,000 tokens)**, 91 % of it the ADR index and this file —
  the two largest documents in the repository, loaded on every planning task, and **neither had a
  G9 budget** because none exists for type `adr` or `program`.
- ⛔ **X3 · Splitting the ADR bodies — REJECTED by the owner 2026-08-03.** The index keeps working by
  **index search**, because splitting the bodies into files would collide with planned work. The
  ruling produced a better answer than the split would have: `docs/program/load-sets.md` now prices
  the ADR member as a **slice** (`README.md#adr-index`), so a planning session is charged for the
  1,950 words of entries it scans rather than the 20,200-word file they sit in. **`planning` fell
  from 35,453 to 17,426 words — halved, with nothing moved and no forty-three new documents to keep
  reachable.** The ceiling's exit changed with it: at 20,000 the finding will be that the "one-line"
  entries have grown into paragraphs — they average 45 words — and the answer is to shorten them.

- 🟦 **X4 · A context-adherence evaluation (ADR-0043).** **Harness landed 2026-08-02:**
  `docs/program/context-eval.md` (five tasks, one per failure class with a real history here) plus
  `tools/context_eval.py` (deterministic checkers, self-tested against a compliant and a violating
  sample each) and gate **G15**, which fails once a context-defining file changes after the recorded
  measurement — by content digest, not by date, because `git log -1 -- <path>` reports the graft at a
  shallow clone's boundary and would fire on everything in CI. Four sub-decisions were selected from
  a list (PLT-R6): dated record + freshness gate · **cold subagent** as the subject · gates **plus**
  per-task assertions · five tasks with a template to grow.
  **✅ First measurement 2026-08-02 — 3 of 5 conforming**, recorded with its digests, so G15 is now
  live rather than skipping. `invent-a-threshold`, `level-metric` and `unit-codes` passed;
  `rule-citation` cited six retired rules and four bold family wildcards — **since fixed and re-run
  clean, see X6, so the standing score is 4/5**; `new-concept-node` came in at 806 words against the
  700-word budget it had read, and that one is still open.
  **What the run found in the estate rather than in the answers:** G3's rule-ID parser could not see
  ten live rules (`ENG-R8..R11`, `PLT-R1..R6`) because it required the colon to follow the ID
  immediately, so **a duplicate `ENG-R10` would have passed G3** — fixed, and a second G3 mutant now
  covers the rule-ID claim that had none.
- ✅ **X5 · The missing documentary form — landed 2026-08-03 (ADR-0044).** Against Diátaxis's four,
  the estate had *reference* and *explanation* and **no task-oriented document at all**, while
  `CLAUDE.md` promises a project learns "which departments it needs **and how to implement them**".
  `how-to` joins the type vocabulary with a 900-word budget; `program/how-to/add-a-concept-node.md`
  is the first, chosen because the eval named the failure it addresses. **The scoping rule is the
  decision:** a how-to about *running a department* is method a company can choose and fails the
  inclusion test — which is probably why the form was never created. **Verified:** the failing task
  re-run against a fresh cold subagent came in at **633 words** against 806, naming the budget in its
  own report. The confound is recorded in `context-eval.md`.
  **Both remaining guides written 2026-08-03**, closing the form: `how-to/change-a-rule.md` (802
  words) and `how-to/run-the-evaluation.md` (795). Each is organised around the traps that have
  actually been hit rather than around the rules, which are cited and never restated — the rule guide
  leads with *establish that it is a rule and not a policy* (seven of thirteen original `SCM-R*`
  failed that test) and *never edit a rule's meaning in place*; the evaluation guide leads with *the
  manifest is under test too* and *diagnose past the first cause*, both of which are this week's
  incidents rather than theory.
  **One consequence worth recording:** adding `change-a-rule.md` to the `changing-a-rule` load set is
  a **material** change to the `rule-citation` evaluation task, because it alters what the cold
  subagent reads. That task was re-run and passed again. A guide that a session is told to read is a
  guide the measurement has to account for.

- ✅ **X6 · The retirement tables were unreachable — closed 2026-08-02 without widening the set.**
  Raised by the first eval run and measured: **52 rules are retired, the id-registry enumerated 12**,
  and the tables live in fifteen `rule.md` files no `changing-a-rule` session loads. The registry now
  carries a machine-readable **retired roster** and **G16** asserts it equals the union of those
  tables in both directions, with a mutant per direction. Adding the fifteen files was rejected:
  ~8,000 words against a G14-priced budget, when the registry was already in the set and a
  retirement is an allocation fact. **Verified by re-running the failing task against a fresh cold
  subagent — PASS.** The eval score moved 3/5 → 4/5.

- ✅ **X7 · The platform catalogue carried four of five delivery metrics — closed 2026-08-03.**
  Enumerated against DORA's current published framework rather than against the recommendation that
  raised it, and the recommendation was **wrong**: it proposed adding Change Failure Rate, which
  CPT-0157 has carried since Phase M1. What was actually missing is **CPT-0167 deployment rework
  rate**, the fifth metric — the one that catches a team posting good numbers on the other four while
  spending its release stream going back over shipped work. The catalogue's **grouping was also
  outdated**: it read as "two pairs" (0155/0156 against 0157/0158) where the published taxonomy is
  three throughput measures, recovery time among them, and two instability measures. Corrected, with
  the trade-off argument the old framing carried kept because it is the part that matters.
  **Why this mattered before M4 and not after:** published research associates AI-assisted
  development with higher throughput and worse stability, so a monitoring product for AI-assisted
  projects that measures only throughput reports improvement while the thing it watches degrades.
  Free to fix now, expensive once dashboards exist.
  **CPT-0999 is now reserved** for the context-adherence evaluation — its `new-concept-node` prompt
  had named CPT-0167, which was free that morning and allocated the same afternoon.

- ✅ **X8 · The purpose was unreadable — fixed and made measurable, 2026-08-03 (ADR-0045).** Asked for
  a plain summary of the project, the weakest thing in the estate turned out not to be rigour: the
  entry point named a supply-chain knowledge base *and* a DevOps dashboard and **never connected
  them**, leaving the reason in ADR-0030 among forty-four decisions. Now three paragraphs at the top of
  `CLAUDE.md` — the two axes, the portfolio, and why monitoring watches it — plus **PLT-R7** (governing
  knowledge is selected and declared to the owner before development) and the practice-area roster.
  **And a new eval task, `what-is-this-for`, so the prose cannot quietly drift back:** it checks a cold
  subagent names both axes, names the portfolio, ties monitoring to the projects **on one line**, and
  does *not* conclude this is a supply-chain application. Run on adoption: **PASS**, from the three
  always-loaded files alone.
  **The gap this closed was in the eval too.** All five previous tasks measured whether an agent
  *obeys* the context; none asked whether it can say what the context is **for**, so the eval could not
  have found the problem the owner found by asking.

### Phase U — Unification (context-skeleton adoption)
- ✅ **U1 · orchestrator** — Skeleton added on branch `feat/context-skeleton`: tier tree,
  knowledge-architecture (instantiated allowlist), id-registry (SCM live; 14 families
  reserved), out-of-scope (seeded from the prohibited-tech policy), ADR-0001..0009
  retroactive + 0010/0011 proposed, glossary (seeded), scm-core rule.md (13 cross-department rules),
  40-contexts knowledge map, program area + 6 templates, additive `CLAUDE.md` governance
  section. **Nothing existing was moved, renamed or rewritten.**
- ⬜ **U2 · human** — Review & ratify ADR-0001..0009 (retroactive), decide ADR-0010/0011,
  and merge the branch.
- ✅ **U3 · orchestrator** — Dedup pass: `CLAUDE.md` §Critical Business Rules /
  §Code Standards cite the rule IDs instead of restating them (SSOT).
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
- ⛔ **U7 · HOW lane** — Test debt: Python test suite (the mirror-coverage bar, since retired); extend
  TS unit coverage beyond the 4 existing files; every SCM-Rx gets its test.
  **Started 2026-07-22 (with P5 slice 3):** the pytest suite is now real and **enforced** —
  `services/calc/tests/test_money.py` runs in `make verify-full` and CI via `make test-py`
  (CI-light `requirements-dev.txt` = pytest only). First Python module under test is the
  money core. **Next:** extend pytest to the calc models (needs a heavier CI lane or mocked
  deps — risk #6), and add a test per SCM-Rx / department rule.
- ✅ **U8 · HOW lane** — Cross-language consistency mechanism (golden test vectors shared
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
- ⛔ **U11 · WHAT lane** — **order-management numbering collision RESOLVED by ADR-0029** (dir dissolved → dept 13 namespace; census fixed). Remaining: fine split of 3 agility/VaR fns → dept 10, blocked on a Python env. Rest of U11 below stands.
- ⛔ **U11b · WHAT lane** — Domain dedup & modeling follow-ups surfaced by the toolchain
  repair: `Shipment.ts` redefines `TransportMode`/`TrackingEvent` already owned by
  `TransportLane.ts`/`TrackingEvent.ts` (aliased in the barrel for now — unify);
  `python/07_order_management/` vs `python/13_order_management/` numbering collision
  (risk register #4); REACH: model ECHA-notification tracking so compliance can reflect
  a submitted notification (currently conservative: required ⇒ not yet compliant).
- 🟦 **U12 · HOW lane** — eslint 9 flat config (`eslint.config.mjs`) + wire `lint` into
  `make verify-full` (QA warnings-as-errors bar).
- ⛔ **U13 · HOW lane** — Enforce LOG-R3 in code: `Shipment` types `hazmatClass` as
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
- ✅ **U15 · WHAT lane** — **z-score RESOLVED by ADR-0028** (canonical = exact inverse-normal). Remaining items 2–7 below stand.
- ⛔ **U15b · WHAT lane** — Cross-language divergences surfaced by U4's concept nodes. These
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
- ⛔ **U16 · WHAT lane** — TypeScript coverage gaps found while cataloguing 03: **no TS
  implementation** of Croston / SBA (CPT-0006/0007 — intermittent demand is unavailable to
  the domain layer), of the scale-free accuracy metrics (CPT-0009), or of tracking
  signal / forecast bias (CPT-0010). Decide per item whether TS needs it (ADR-0001 puts
  analytics in Python, so some of these may be correctly Python-only — record the ruling).
- ⬜ **U17 · WHAT lane** — Domain-coverage candidates against SCOR-DS, surfaced by the
  ADR-0015 analysis and **not yet confirmed**: (a) **Make** has no department — BOM/MPS
  live in `04-supply-planning` but there is no production execution; (b) no **network
  design / facility location**; (c) SCOR-DS **Orchestrate** is unmapped. Confirm against
  the full census before proposing a 15th department (which requires an ADR — id-registry §4).

- ✅ **U18 · WHAT lane** — Extract-and-archive the department business-context documents
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

  **Landed for 03-demand-planning:** four further rules extracted (forecastability, APE
  zero-handling, override classification, SS adequacy bands) · CPT-0024 **Forecast Value
  Added** and CPT-0025 **safety-stock coverage/adequacy** created — **both required KPIs
  with zero implementation anywhere in the repo** · the service-level→z validation
  recorded as currently unsatisfiable (risk #9).
  **Current state:** 03 extraction covers §9, §10, §12. **Not yet done for 03:** §11
  analytical logic, §15 use cases, §17 test cases (TC-01..TC-06 are ready-made test
  specs — feed them to U7), and the archival stamp (deferred until 03 is fully extracted).
  **Next step:** finish 03 §11/§15/§17, stamp it archived, then repeat by census order.
- ⛔ **U19 · HOW lane** — Implement the two specified-but-missing KPIs found by U18:
  Forecast Value Added (CPT-0024) and safety-stock coverage/adequacy (CPT-0025), with
  tests, in whichever language ADR-0001 assigns. Both have dashboard/escalation
  requirements in the business-context document and no code at all.

### Phase P — Product build (ADR-0017..0021; owner-directed 2026-07-20)

> Staged full-stack app. **Only Stage A (wiki) is authorized to start.** Every task gated
> on `make verify-full`; the domain in `src/departments` is preserved, not rewritten.

- ✅ **P0 · human** — Ratify the product decisions. **Done 2026-07-20:** owner authorized
  proceeding on all proposed ADRs; **ADR-0010..0029 are Accepted (owner-authorized)**. This
  authorizes the money migration (P5, ADR-0019) and the agent layer (ADR-0027).
- ✅ **P1 · orchestrator** — Materialize the reserved `docs/50-engineering/` tier: `_index`,
  an `ENG-*` rule family (layering rules per ADR-0023 — dependency direction
  `apps → infrastructure → application → domain`, `domain` imports nothing, cross-department
  only through application ports; boundary linter fails violations), and a frontend-UX ADR
  for the octagon node-graph (octagon shape, LED-cyan stroke, transparent fill, right
  sidebar, interaction states, a11y, light/dark).
- ✅ **P2 · HOW lane** — Monorepo restructure per **ADR-0022/0023**. **Landed
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
  **The one deferred item is void (triaged 2026-08-02):** the `07_order_management` vs
  `13_order_management` merge needed a domain call because the two `order_metrics.py` files
  differed — ADR-0037 deleted both, closing risk #4 and voiding U11. Nothing remains to decide.
  **Superseded plan text below is retained for history:**
- ⛔ **P2 (original plan) · HOW lane** — Monorepo skeleton per **ADR-0022/0023**, without breaking `src/`:
  **pnpm workspaces + Turborepo** (`pnpm-workspace.yaml`, migrate `package-lock.json` →
  `pnpm-lock.yaml`, CI → `pnpm install --frozen-lockfile`, `make verify-full` delegates to
  `turbo run`). Layout: `apps/web` · `apps/api` · `packages/{domain,application,infrastructure,shared}`
  · `services/calc` · `proto/`. **`packages/domain` = today's `src/departments`** (moved,
  barrel + path alias preserved); **`packages/shared` = `src/shared`**. `docs/ tools/ .claude/`
  stay at root. Fix the `07_order_management` → `13_order_management` collision (risk #4/U11)
  during the move. Update the 4 test imports.
- ⬜ **P3 · HOW lane (Stage A)** — **Confirmed live by the owner 2026-08-02** against the
  monitoring-only alternative; it is planned as part of **M4**, not as a separate phase, because
  one gateway serves both read surfaces. **Postgres read model (ADR-0024)** + **code-first GraphQL
  (ADR-0025)**. `tools/ingest`: one-way build reading `docs/25-concepts` + `rule.md` +
  `40-contexts` into read-model tables (drop-and-rebuild; `docs/` stays SSOT). NestJS
  code-first resolvers expose nodes/edges; `schema.gql` emitted + committed; DataLoader
  batching; contract tests. A drift guard asserts the ingested counts match `docs/` — as a **new**
  gate number, since G1–G13 are all taken (the "future gate G11" this entry once named is now
  the retired-rules gate).
- ⬜ **P4 · HOW lane (Stage A)** — **Confirmed live by the owner 2026-08-02.** Next.js octagon
  node-graph front end per the P1 UX ADR;
  SCM core node centre, 14 department nodes around it as a connected circuit, CPT sub-nodes
  on expand; click → right sidebar rendering the concept node (formula, worked example,
  links). Accessibility + light/dark.
- ✅ **P5 · WHAT+HOW** — Money → Decimal migration (ADR-0019). **Sliced (L/high-risk):**
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
- ⛔ **P6 · HOW lane (Stage B)** — Python gRPC calc service (`scm.calc.v1`), NestJS client;
  interactive calculator for the demand-planning concepts first (the `enforced` dept).
- ⛔ **P7 · VOID (ADR-0037)** — was Clean-Architecture wiring of the department tree
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
- ✅ **W2 · WHAT lane** — Model the platform bounded contexts. **Landed 2026-07-22:** the
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
- 🟦 **W3 · HOW lane (Stage B)** — Build the workspace/projects bounded context: Postgres schema
  for the mutable project data domain (separate from the ADR-0024 knowledge read model),
  tenancy/auth, NestJS code-first GraphQL resolvers, project→context reference resolution +
  overlay, and the **prompt-refinement gate** (refine → show diff / opt-out → execute; retain
  original+improved). Reads the knowledge read model, never writes it.
- ⛔ **W4 · HOW lane (Stage C, ADR-0031)** — Monitoring connector: emit progress events from the
  W3 data model; connectors (internal-first, then external dev tools: GitHub/CI/issue-trackers);
  delivery metrics as `CPT-*` nodes; dashboards. Deferred until W3 lands.
- 🟦 **W5 · WHAT lane (as branches are onboarded)** — Per-tech-branch practice knowledge
  (AI/ML/Data/Backend/Frontend/DevOps/…): materialize a branch's standards/skills **only when a
  real project in that branch needs them** (no speculative pre-build — knowledge-architecture).
  **Roster landed 2026-08-03 (ADR-0045):** `docs/50-engineering/practice-areas.md` enumerates the
  thirty-five areas the owner named, each with **the external authority that would make a statement in
  it admissible** — standard, terminology or identity. **Content is still zero and that is the rule**,
  not a gap: what the roster fixes is the anchor, which is the part that cannot be improvised when
  someone finally writes the area. Two rows are flagged as the ones that will fight the inclusion test
  hardest: *clean code* (advice largely choosable) and *technology strategy* (**no external anchor at
  all** — it can contribute only the decisions a strategy must record).
  **Next step:** nothing, until a project needs an area. Then §How a row becomes knowledge.

### Phase L — VOID (superseded by ADR-0037)

> Phase L existed to migrate an invented supply-chain application into a Rust core. **ADR-0037
> deleted that application**, so most of the phase has nothing left to migrate. Recorded here
> rather than erased, because the reasoning matters: the lanes and the scale tier survive and now
> apply to the **monitoring** application; the department ports do not.

- ✅ **L0/L1** — the lane map (ENG-R8/R9/R10) and the telemetry data model (ADR-0036) stand. They
  govern the monitoring platform.
- ✅ **L2a** — `crates/scm-money` survives ADR-0037 as the one piece carrying no policy.
- ⛔ **L2b, L3a, L3b** — void. The `napi-rs` binding had nothing to bind; the department rule ports
  had nothing to port. `crates/scm-core` (PurchaseOrder) was deleted three commits after it
  landed: it faithfully reproduced a USD 5,000 approval threshold that never belonged in a
  standards context.
- ✅ **L4/L5** — renumbered and **delivered** under Phase M, exactly as this entry anticipated:
  L4 (the ClickHouse telemetry tier) is **M2**, L5 (the Rust ingestion workers) is **M3a/M3b**.
  Triaged 2026-08-02.
- ⛔ **L6** — void as an L entry; the Docker/Kubernetes packaging is tracked as **M5**, so it has
  one home rather than two.

### Phase W6 — Operational telemetry (raised 2026-08-01, decision open)

> The owner asked for warehouse indicators — goods receipts processed, returns by discrepancy,
> shipments pending, security events, sequences prepared and pending, pull lists processed — modelled
> on the monitoring platform. **Investigated, and it split into two questions with different answers.**

- ✅ **W6a · WHAT** — **The knowledge landed: CPT-0161..0166 in dept 06.** Definitions, formulas,
  assumptions, project-chosen inputs and sources; no levels, no ingestion, no schema, no connector.
  Allocated to **dept 06 and not to `00-platform`**, because that catalogue's own extension rule
  admits a metric only if *a project's development* produces the signal — warehouse operations do not.
  Two nodes (CPT-0164 sequence, CPT-0165 pull list) carry an explicit **vocabulary warning**: they are
  APICS Dictionary industry terms, and no standards body fixes what one sequence or one list contains,
  so counts are not comparable across operations.
- ⛔ **W6b · HOW — ANSWERED NO, 2026-08-02.** The owner declined the scope change: the monitoring
  application stays project supervision, and ADR-0031/0034/0036 are unchanged. **Items 2 and 3
  below survive the *no*** and were split out as **M2b**, because the level-summing defect is
  already present in a schema that has no level metrics yet — it is cheap to fix now and silent
  when it bites (risk #14). Items 1 and 4–8 are void unless the scope question reopens. The
  inspection is kept in full below: it is what a *yes* would have cost, and re-deriving it later
  would be waste.
  **Original entry — what it would require, found by inspection rather than assumed.** Making the
  monitoring application ingest
  operational warehouse telemetry is a **product-scope change** over ADR-0031/0034/0036, which say
  *project supervision*. What it would require, found by inspection rather than assumed:
  1. **An ADR** narrowing or extending those three.
  2. **A metric `kind` (flow / level / event-count)** declared per concept node and enforced at ingest.
     Without it the cascade corrupts levels — see risk #14, and CPT-0163 for the arithmetic.
  3. **`argMaxState`/`anyLastState` in the rollup cascade.** Today `samples_1m` computes
     `sumState`/`min`/`max`/p95 only, which is right for a flow and wrong for a level: a backlog of 40
     read every ten seconds sums to **240** per minute, in range, with nothing failing.
  4. **An entity dimension.** The sort key leads on `project_id`; a warehouse indicator is scoped by
     site, area, dock and shift. Overloading `project_id` with a site id is a semantic lie that gets
     inherited; adding a column changes the sort key, so it is a migration with a backfill plan.
  5. **A codec change for counters.** `value Float64 CODEC(Gorilla, …)` suits slowly-varying floats;
     integer counters compress materially better as integers with `DoubleDelta`/`T64`.
  6. **A separate `telemetry.security_events` table.** ADR-0036's own consequences already say bursty
     events belong in their own table with their own sort key. A count supports vigilance; acting needs
     the event's class, severity, location and actor.
  7. **`Sample` gains entity and label fields**, so `scm-ingest`, the RowBinary encoder and the schema
     guard all change together.
  8. **A WMS connector, which does not exist at all** — and is the largest piece.
  **The honest blocker:** there is no WMS connected, so today these indicators are *definitions
  without a signal*. Building 2–7 before a source exists would be building against a guess.

### Phase M — Monitoring, the only application (ADR-0031/0034/0036)

> The single application this repository builds. Nothing here is invented: a metric exists because
> a project's development produces the signal, and every metric is defined as a `CPT-*` node before
> it is computed.

- 🟩 **M1 · WHAT — the delivery metrics defined (2026-07-27).** Six nodes, **CPT-0155..0160**, in a
  new `00-platform` group of the *same* catalogue — one place a project looks up what a number means,
  as the product statement fixes, rather than a second catalogue for the platform.
  **The four keys** (deployment frequency, lead time for changes, change failure rate,
  failed-deployment recovery time) plus **Little's Law** and **flow efficiency**.
  **The trap these metrics attract is the same one ADR-0037 corrected**, and it is named at the head
  of the group: published delivery benchmarks come with performance bands — "elite", "high" — derived
  from a survey population. *"Elite teams deploy on demand"* is a survey finding in exactly the way
  *"world-class OTD ≥ 95%"* is a textbook illustration. **No node carries a band.**
  **A second trap, named per node: these metrics are gameable in isolation**, and the gaming looks
  like improvement. Deployment frequency rises if one change ships as five. Change failure rate falls
  if the denominator inflates — the worked example shows the *same* 18 remediations reading as 4.5% or
  22.5% purely from batch size. Lead time shortens if the start event moves later. Recovery time
  shortens if detection gets *worse*. So each node states what it can be traded against, and the four
  keys are documented as **two pairs** rather than four numbers.
  **Little's Law is the one statement here that cannot be argued with** — an identity, given
  stationarity — and it carries the consequence that matters: at fixed throughput, cycle time is
  proportional to WIP, so starting more work in parallel makes items finish *later*, arithmetically.
  Registry updated (the CPT family is no longer "supply-chain" only); the catalogue index now lists
  **groups** rather than departments.
- ✅ **M2 · HOW** — The ClickHouse telemetry tier exactly as ADR-0036 fixes it: sort key
  `(project_id, metric, ts)`, monthly partitions, per-column codecs, the `AggregatingMergeTree`
  rollup cascade, raw TTL with long rollup retention, split-privilege users with quotas.
  **ENG-R9 six checks — run before any code, 2026-07-27:**
  1. **Lane** ✅ ClickHouse owns project telemetry at scale and never truth (ADR-0034); the schema is
     that lane's own artefact. It is *not* PostgreSQL's (transactional truth) and the DDL is not
     NestJS's to own — NestJS only *reads* it, through the SELECT-only identity.
  2. **Best practice** ✅ ADR-0036 fixes the idioms rather than leaving them to taste: sort key
     ordered project → metric → time because supervision queries scope that way; monthly partitions
     to bound part count; `Delta`+`ZSTD` on timestamps and `Gorilla`/`DoubleDelta` on float values;
     `LowCardinality` labels; **no `Nullable` on hot columns** — absence encoded explicitly;
     aggregation at insert time via materialized views, not at query time.
  3. **Security** ✅ two identities, not one: an insert-only writer for the ingester and a
     SELECT-only reader for NestJS, each with row/memory/time **quotas** so no dashboard query can
     exhaust the cluster. No credentials in the repository.
  4. **Speed** ✅ the dashboard cost is paid on insert; reads hit the coarsest rollup that answers
     the question. The hot path acquires no extra network hop (the ingester writes directly).
  5. **Scalability** ✅ the ADR-0034/0036 target is tens of thousands of continuous series; the raw
     TTL plus long rollup retention is what bounds growth. **Documented limit:** a cross-project
     "top N metrics everywhere" query is expensive under this sort key and needs its own projection.
  6. **Licence** ✅ ClickHouse is Apache-2.0 — OSI, commercially usable, modifiable (ADR-0002).
  **Placement decided (inside an already-adopted lane, so no new ADR — CLAUDE.md working
  agreements):** the DDL and its migrations live in their own top-level directory rather than inside
  `apps/api`, because the schema outlives any one consumer and NestJS must not appear to own it.
  Migrations are **forward-only and numbered**; a materialized view is never edited in place without
  a backfill plan, which ADR-0036 records as the cost of this design.
  **Open question for the next session, deliberately not decided here:** the concrete raw TTL and
  rollup retention *values*. They are this application's own policy — legitimate to set, since here
  the repository **is** the project — but they should be set as named configuration with the reason
  recorded, not inlined as magic numbers, so that the one place ADR-0037 permits a policy value does
  not become the place they leak back in.
  **Landed 2026-07-28** in `db/clickhouse/` — five numbered migrations (raw table, the three
  `AggregatingMergeTree` rollups with their materialized views, and the two roles with quotas), plus
  `apply.py` and a pinned compose file.
  **The two open decisions were put to the owner as a selectable list rather than guessed — the first
  live use of PLT-R6.** Chosen: retention **raw 14d · 1m 90d · 1h 1y · 1d 5y**, and **CI applies the
  migrations against a real ClickHouse**. The retention consequence is written into the schema README
  rather than left implicit: *an incident older than 14 days can only be examined at minute-aggregate
  resolution.*
  **The rollups store aggregate *states*, not finished numbers** (`AggregateFunction(...)` columns,
  `-State` on ingest and `-MergeState` between stages). This is the load-bearing detail: a stored
  average cannot be re-aggregated into a coarser bucket without becoming an average of averages, and
  a stored percentile cannot be re-aggregated at all — merging t-digest states can.
  **`project_id` is deliberately NOT `LowCardinality`**, unlike `metric`. Dictionary encoding
  degrades past roughly ten thousand distinct values and the project count is expected to grow;
  metric names are a bounded vocabulary (CPT-0155..0160), so there the encoding is right.
  **The "CI runs exactly `make verify-full`" invariant is now split, deliberately.** `verify-full`
  stays the *portable* merge gate; **`verify-schema`** is the service-dependent one and CI runs both.
  Folding it into `verify-full` would make the merge gate unrunnable without a database; letting it
  skip when no server is present would recreate exactly the false green `deps-locked` exists to
  prevent. `apply.py` therefore **fails rather than skips** — verified locally by running it with no
  server. It also applies the migration set **twice** to prove idempotence.
  **First CI attempt hung, and the fix is a lesson worth keeping:** the service container carried a
  `--health-cmd`, and `Initialize containers` then sat for **13 minutes with no output**. A hang is
  worse than a failure — the runner owns that step, so there is nothing to read and nothing to
  diagnose. Readiness is now an **explicit bounded step** that polls `/ping` for 60s, prints how
  long it took, and on giving up says so and dumps `docker ps -a`. *A gate that can fail should fail
  loudly and locally to the step that owns it.*
  **Honest status: the DDL itself has never been executed on this machine.** This container cannot run it — the agent
  proxy denies `builds.clickhouse.com` by policy and there is no Docker daemon — so **CI is the first
  real execution of this schema**. That is the gate the owner chose doing its job; if it goes red, the
  migration is wrong and gets fixed.
- ✅ **M3 · HOW** — The Rust ingestion worker: normalize → validate → deduplicate → **batch**
  insert. Ingestion is core work (ENG-R10).
  **M3a landed 2026-07-28 — `crates/scm-ingest`, the deterministic core, 13 tests.** Split from
  transport by rule, not by convenience: ENG-R10.1 forbids an HTTP server or DB client in a core
  crate, so the pipeline takes samples in and hands batches out. It also **takes time as an input**
  rather than reading a clock, which is what lets the batch-age tests assert timing without sleeping.
  **ENG-R9 six checks** — lane ✅ (ingestion is Rust core work) · best practice ✅ (no I/O, time
  injected, `-D warnings` with truncation/unwrap/expect denied) · security ✅ (this is the only place
  untrusted input enters: a non-finite value, an ungoverned metric and a future timestamp are each
  refused) · speed ✅ (O(1) amortized dedup, no allocation per sample beyond the batch vector) ·
  scalability ✅ (memory bounded by `window/bucket`, not by sample count — asserted by a test) ·
  licence ✅ (no new dependency at all).

  **M3b landed 2026-07-30 — `crates/scm-ingest-clickhouse`, the transport half, 40 tests.** No test
  needs a server: the network sits behind a `Transport` trait and the retry waits behind a `Sleeper`,
  so *unreachable*, *ambiguous*, *refused* and *budget exhausted* are all exercised deterministically.
  Those are exactly the paths a live ClickHouse cannot be made to produce on demand.
  **Four decisions went to the owner as a list (PLT-R6), all recommended options taken:** `ureq` +
  rustls as the client; **RowBinary** on the wire with a **startup schema guard**; **at-least-once**
  delivery, retrying an ambiguous failure in the knowledge that it may duplicate a row; and a
  **bounded dead-letter file** for batches that outlive the retry budget.
  **The guard is stronger than the one that was pitched, and the reason is worth keeping.** The
  recommendation was a *column-order* check. Column order turned out not to need guarding at all,
  because the INSERT names its columns and ClickHouse maps named columns by name. What does need
  guarding is the **declared type**: `DateTime64(3)` widened to `DateTime64(6)` reads every
  millisecond as a microsecond — a thousandfold error, in range, in the right column, with nothing
  failing anywhere. The guard reads `system.columns` and compares types, so it also catches a table
  that drifted from its own migration.
  **Retry classification is by what is safe to do next, not by HTTP status.** `NotSent` cannot have
  been applied, so retrying it is free; `Ambiguous` may have been applied, so retrying it is
  at-least-once and the writer *says so* in its outcome and its counters rather than leaving an
  operator to explain a doubled count. A 4xx is terminal — it will refuse the identical body forever,
  so retrying only delays the dead letter.
  **The dead letter is bounded at two generations**, giving a hard ceiling of `2 × max_bytes` no
  matter how long an outage lasts. Past that the oldest records are dropped **on purpose and
  counted**, because an unbounded dead-letter file turns one outage into two.
  **ENG-R9 six checks** — lane ✅ (transport in an adapter, ENG-R10.1; no I/O entered the core) ·
  best practice ✅ (network and sleeping both behind traits, body encoded once and reused across
  attempts, errors classified by consequence) · security ✅ (credentials from the environment only,
  never a default password; the INSERT-only identity from migration 0005; response header size capped;
  SQL percent-encoded) · speed ✅ (RowBinary, one allocation per batch, no re-encode per retry) ·
  scalability ✅ (dead letter bounded by bytes not by outage length; backoff capped so a batch cannot
  wait past its own relevance) · licence ✅ (`ureq` MIT/Apache-2.0; **all 41 transitive crates audited
  as permissive OSI** — no GPL, SSPL or BUSL, nothing unlicensed, per ADR-0002).
  **Not built, and named so it is not assumed:** nothing wires the pipeline to the writer in a
  running process yet. There is no binary, no configuration loading beyond `Endpoint::from_env`, and
  no replay tool for the dead letter. Those belong with M4, where there is a service to host them.
  **Three decisions went to the owner as a list (PLT-R6), all recommended options taken:** dedup by
  bounded time window on `(project_id, metric, ts)`; flush on **size or age, whichever first**, with
  backoff and a dead-letter file; and an invalid sample is **dropped and counted by reason** rather
  than failing its batch.
  **The algorithmic core, and its honest cost.** Dedup keys are stored as a **`u64` hash** — eight
  bytes instead of ~sixty — in `VecDeque` time buckets, so eviction drops a whole bucket at once
  instead of scanning for expired entries. The cost is a false-positive rate: at a million live keys,
  ~`2.7e-8` per key pair, and the consequence is one dropped telemetry point. **That trade is
  acceptable here and would not be for money**, which is why `scm-money` stores no hashes. Written
  into the doc comment rather than discovered later.
  **Two behaviours worth naming, both tested:** a sample older than the dedup window is **not**
  reported as a duplicate (claiming so would assert knowledge deliberately discarded — staleness is
  the validator's call), and batch age runs from **arrival**, not from the sample's own timestamp, or
  a backfill of old samples would look permanently overdue and flush one row at a time.
  **M3b remaining:** the transport adapter (ingress) and the ClickHouse client that performs the
  batched insert, plus the retry/dead-letter mechanics the owner chose. Both are adapter work by
  ENG-R10.1, so they belong outside this crate.
- ✅ **M2b · HOW** — **Close risk #14: make the rollup safe for levels.** Decided 2026-08-02 with
  W6b answered *no*, because the defect does not need the scope change to bite. **Landed
  2026-08-03**, and the shape changed once during the work in a way worth recording.
  **What was built.** `db/clickhouse/migrations/0006_metric_kind.sql` adds `kind` to `samples`
  (`LowCardinality(String)`, `DEFAULT ''` per ADR-0036's no-`Nullable` rule) and to all three
  rollups, plus a `last_state` per rollup, and recreates the three materialized views. In
  `crates/scm-ingest`, `MetricKind` and `MetricRegistry` replace the flat governed-metric list:
  validation now asks `registry.kind_of(metric)`, and `Sample` deliberately has **no** `kind` field
  so an emitter cannot declare its own metric a flow. `crates/scm-ingest-clickhouse` carries the
  column as the 7th in `COLUMNS`/`INSERT_STATEMENT`; `encode_batch` takes the registry and **drops**
  an ungoverned metric rather than encoding a blank kind.
  **The enforcement is a missing column, not a warning.** The plan said "`argMaxState` alongside
  `sumState`, so a level aggregates by last and never by sum" — an instruction to the reader.
  Instead the read surface splits: `telemetry.levels_1m` has **no sum column at all** and
  `telemetry.flows_1m` has no `last_value`, so MSR-R2's forbidden aggregation is not selectable.
  `apply.py` gains `VIEW_ASSERTIONS` that fail if either absence is ever filled in — the gate checks
  what is *not* there, which is the only kind of check that survives a helpful future contributor.
  **Two corrections to the plan itself.** `anyLastState` was wrong and the risk row had named it as
  an alternative to `argMaxState`: `anyLast` returns whichever row the engine merged last, a
  nondeterministic pick that diverges from the newest reading exactly under load. And **no ADR was
  needed** — the fix changes nothing about what the product measures, only that a level may not be
  summed, which MSR-R2 already fixes.
  **Not executed in this environment.** No Docker daemon and no `clickhouse-local`, so the migration
  is unrun locally; `python3 db/clickhouse/apply.py --check-only` fails as designed rather than
  skipping. CI's `verify-schema` job is what proves the DDL. A duration metric still has no correct
  kind — recorded as risk #15 rather than guessed at.
- ⬜ **M4 · HOW** — NestJS + GraphQL as the only counterpart the frontend has; Next.js dashboards.
  **Scope confirmed 2026-08-02:** with P3/P4 kept alive, the gateway serves **two** read surfaces —
  the knowledge read model (ADR-0024/0025) and the telemetry tier (ADR-0036) — and the octagon
  front end (ADR-0026) sits above it. The drift guard asserting the ingested counts match `docs/`
  belongs to this phase, not to a later one.
- ⬜ **M5 · HOW** — Docker images (non-root, pinned digests, multi-stage) then Kubernetes once two
  long-running services exist.

### Triage of 2026-08-03 — references that outlived what they referenced

A scan for backticked repository paths that resolve to nothing: **121 mentions across 30 files.**
The denominator matters more than the count, because most of it was not a defect.

- **59 were not real** — relative citations (`rule.md`, `evaluation.md`) resolved against the repo
  root instead of the citing document's own directory. The first pass reported them as dead.
- **~45 are legitimate.** `10-decisions/README.md` and `WORKFLOW.md` are append-only history: an ADR
  that records deleting `src/departments/` has to name it. `30-foundation/_index.md` marks
  `security/` and `observability/` *none recorded yet*; `40-contexts/_index.md` says `specs/` stay ⬜
  *created per unit of work, never speculatively*; both `20-product-model` references to
  `context-map.md` sit under **MISSING (owner input needed)**. All honest.
- **One class was a real defect, and it was the class that matters:** live guidance, loaded by every
  session, naming deleted files as though they could be opened. **Thirteen of fourteen department
  skills** carried a `## TypeScript` / `**Domain Objects**` section listing `domain/NCR.ts`,
  `services/QualityService.ts` and 60 others. `procurement` had been fixed and is what made the rest
  visible. Same reservoir as improvement #11 — `.claude/skills/**`, which no gate reads.

**Fixed:** all 14 skills carry one heading and one disclaimer (*shapes, not code — a project builds
these in its own repository, with its own policy values and its own layout*), directory prefixes
stripped since the layout was never this repository's to imply; `procurement` unified onto the same
wording rather than left as a fourteenth variant. **CPT-0063** rewritten — its entire content had been
a rounding difference between two deleted Python files, and it now states what is true independent of
any implementation: the denominator is the **inspected** quantity, and using the received quantity
instead understates a 200-of-10,000 sample fiftyfold.

**⚠ Raised, not built — a gate for this class.** A path-existence gate would now fire on all 62
corrected shape names, and a gate that reddens correct work gets disabled rather than obeyed. It needs
the disclaimer convention to be machine-readable first (a fenced block, or a front-matter flag on the
section) and it needs the historical tiers exempt by declaration rather than by guess. That is a
design decision, so it is a decision and not a patch.
### Review of 2026-08-03 — file-by-file, the whole estate

**Denominator: 322 tracked files**, enumerated with `git ls-files`. **239 carry front-matter and are
governed by the doc gates; 83 are not** — and that 83 is where the protocol says to look first.
**12 files carried a finding.** Seven finding classes were named before looking, from this project's
own registers. What each class returned:

- **Rule-ID integrity — clean.** 66 live rules, 52 retired, 119 distinct IDs cited across every
  `.md`/`.py`/`.rs`/`.ts`/`.sql`. **Zero retired IDs cited in live guidance.** The one apparent
  dangling citation (`ENG-R12`) is the sentence saying that ID *cannot yet be allocated*; the one
  undefined CPT (`CPT-0999`) is reserved on purpose in four places.
- **Two ADRs cited as law with no decision recorded.** 46 index entries, **44 bodies**: ADR-0045 and
  ADR-0046 existed as summary lines only, while **PLT-R7** named ADR-0045 as its authority and
  `knowledge-selection.md` cited ADR-0046 twice. **G9 checked body → entry and never the reverse.**
  Both bodies written; the gate is now two-sided and carries a third mutant (**20 gates**).
- **Four nodes published an invented scoring scheme as their canonical formula.** CPT-0025
  (0.8×/1.5× bands, 90-day window), CPT-0080 (30/35/25/10 weighting, 180/365-day bands, GREEN ≥ 75),
  CPT-0132 (the whole ESG point system), CPT-0138 (0.6/0.4 blend). Two *said in prose* the numbers
  were policy and printed them in `## Formula` anyway. All four now state the shape parametrically
  with the values in `Project-chosen inputs`, each row naming what constrains it.
- **G15's watched list had fallen behind its own manifest.** `how-to/change-a-rule.md` joined the
  `changing-a-rule` set two commits earlier and was never watched, so `rule-citation` was scored
  against an input whose change could not register. G15 now derives the requirement from the manifest.
- **Policy-as-law elsewhere — swept and genuinely clean.** Across 227 rule/concept/skill files,
  **zero** lines put a unit-bearing number in a normative sentence. Of 17 pairing a percentage with a
  normative word, each is the anti-pattern quoted *as* such, a worked example, or externally fixed —
  REACH's 0.1 % w/w; CBAM's 50 % traced to the Omnibus-amended Art. 22(2) with the original 80 %
  named and a verification date; CPT-0127's 1.645 is the normal-curve z.
- **Duplicated prose — 1 of 280 files.** `known-pitfalls.md` carried its intro twice, and the second
  copy cited a `review-protocol.md` §Where findings land that does not exist. CPT-0025 carried a
  sentence fragment glued onto its DMD-R9 citation by an unread scripted edit.
- **Stale self-claims.** The ID registry said `58 of 154 nodes` (really **71 of 167**). Checked and
  true: `1000/1000` for the ENG family (exact), 17 gates, 14 departments, three crates, 71 Rust
  tests, and every CI claim. `REGULATORY_FRAMEWORK.md`'s absent front-matter is U9's recorded "keep
  grandfathered", allowlisted in knowledge-architecture §3 and enforced at `verify.py:213` —
  consistent in all three places, checked rather than assumed.
- **ADR hygiene.** ADR-0011 read `Decision (proposed)` under an Accepted status with nothing saying
  ADR-0046 had killed its SemVer clause; ADR-0012 still described G1–G7+G9 and one CI invocation.
  Both carry amendment notes now, following the precedent already set at ADR-0009 and ADR-0013.

**⚠ Raised, not built.** A gate for "a free numeric parameter in `## Definition` with no
`Project-chosen inputs` table" would have found all four scoring nodes, but it needs a discriminator
the sweep applied by hand: `fraction (0.10 = 10%)` in a symbol table is a **unit encoding**, and seven
nodes use it legitimately. That discriminator is a decision.

**This review pushed `planning` past its ceiling, and the declared exit did not fit.** The manifest
names shortening the ADR index entries; measurement says WORKFLOW is 14,505 of the 20,142 words and
the index slice only 2,427, so the exit addressed the wrong term. These blocks were compressed
instead. **The structural answer when it recurs is a `WORKFLOW-archive.md`** for closed phases, the
same instrument the risk register already uses — not another raise.

### Phase C — Clean the context after ADR-0037

> The deletion is done; making the remaining knowledge consistent with it is not.

- ✅ **C1 · WHAT** — **Sweep the concept nodes for policy.**
  **C1a landed 2026-07-27 — the numeric policy is out.** Method: a detector for lines carrying a
  number *and* a normative word (target, threshold, tolerance, weight, band, default), minus
  citations, narrowed 169 flagged nodes to **47 real candidate lines in 37 nodes**, each then judged
  by hand. Removed: every "world-class ≥ X" bar (13 of them, one citing a `CLAUDE.md` section that
  no longer exists) · matching tolerances (0%/1%/2%) · the 25% carrying rate and its 20–30% "band" ·
  the 85–90% space-utilization band · warehouse throughput and dock-to-stock benchmarks ·
  MPS stability > 0.85 · fill ≥ 98% / backorder ≤ 2% · the 15% restocking default · compliance-score
  weightings · C2C rating bands · the 0.5% tracking dead band · α = 0.3 smoothing · the 85%
  capacity-strain onset.
  **Kept, because a regulator fixes them:** REACH 0.1% w/w (Reg. 1907/2006), CSDDD >5,000
  employees ∧ >€1.5B from 26 Jul 2029 (Directive 2026/470), CBAM 50% quarterly holding. Worked
  examples keep their illustrative numbers; mathematical domains (`α ∈ (0,1)`, `n ≥ 1`) are not
  policy.
  **Two nodes were policy end to end and were rewritten as definitions:** CPT-0060 (scorecard) now
  states only `Σwᵢ = 1` and why a compensatory composite must keep gates outside it; CPT-0061
  (rating bands) states only that a partition must be exhaustive, non-overlapping and explicit
  about boundary inclusivity.
  **C1b landed 2026-07-27 — no node compares deleted implementations any more.** All `(PY)`/`(TS)`
  annotations are gone, and several were hiding a real question rather than a formatting wart:
  · **HHI** never said which input scale it used. The published index is computed on **percentage
  points** (0–10,000) — that is definitional, not conventional, and computing it on fractions
  makes every published reference value read a factor of 10,000 off. Stated once, with the
  consequence.
  · **CV/XYZ** hid the **estimator** choice: population versus sample standard deviation differs
  by ~5% on ten observations, enough to move a borderline SKU across a class boundary. Now named
  as a project decision that must be applied consistently, because two SKUs measured differently
  are not comparable. Its 0.10/0.25 class table also survived C1a — the detector missed it
  because the number and the normative word sat in different table rows. **Detector blind spot
  worth remembering.**
  · **Safety stock "days of supply"** was two different formulas under one name (a flat day count
  versus the lead-time spread `LT_max − LT_avg`). Both survive as legitimate definitions; the node
  now insists the project say which it means, and the worked example shows the same SKU getting
  250 or 150 units.
  · **EAL** allowed impacts in currency and as a fraction of revenue in the same sum, and summed
  correlated scenarios. Both now stated as errors.
  · **Stock-balance projection** — where the non-negativity check belongs is recorded as a real
  choice: refusing the movement keeps the ledger always-valid, letting the projection report a
  negative surfaces the upstream gap. A *reader* of an event log can only do the latter.
  · **ABC slotting**, **risk matrix 5×5** and **Kraljic** had their break-points, bands and axis
  midpoints removed; what remains is the structure (rank-then-cut; an ordinal product is not an
  interval scale; a 2×2 on two dimensions).
  · **AQL** large-lot behaviour is ISO 2859-1 table data and is cited as such rather than
  described as a fallback.
  Also: the two department "Divergences" sections became **Regulatory drift to watch**, keeping
  the CSDDD/CBAM/REACH/EUDR movements and dropping the code-gap notes.
  **Lesson recorded:** three scripted line replacements produced broken prose that the gates
  cannot see. Prose edits get read back; only structural edits get scripted.
  **C1c remaining:** a **Project-chosen inputs** section on every node that needs values — about
  a dozen have one now, out of 154.
- ✅ **C2 · WHAT** — **All 14 department rule families swept and rewritten (2026-07-27).** This was
  where the bulk of the remaining problem sat, as suspected: the families had been extracted from
  the `throw` guards of the deleted code, so most "invariants" were invented workflows or field
  checks citing `.ts` files. Of **70** rules, **45 retired**, **25 survived**, **13 new IDs**
  allocated for externally-fixed statements that had never been written down.
  **What the sweep surfaced as genuinely fixed and previously unstated:** IAS 2's
  lower-of-cost-and-NRV rule and its **LIFO prohibition** (FIN-R4) · that only *non-recoverable*
  tax capitalizes into inventory cost (FIN-R5) · the Incoterms **sea-only** restriction on FAS/FOB/
  CFR/CIF, so naming one for an air movement is an error not a shorthand (LOG-R1) · dangerous-goods
  declaration per mode, a criminal matter rather than a data-quality one (LOG-R3) · chargeable
  weight as the greater of actual and volumetric (LOG-R4) · that an **ISO 2859-1 plan is read from
  the table, never interpolated**, because its operating-characteristic curve only holds for the
  tabulated combinations (QMS-R5) · that accepting a *sample* is not accepting a lot (QMS-R6) ·
  that a defect rate needs its **opportunity base** or PPM and DPMO get compared (QMS-R7) · that
  EUDR country risk is **read from the Commission benchmark**, so a hardcoded list is wrong the
  moment it is revised (SDV-R6) · that **absence of evidence is not evidence of compliance** — an
  unevidenced supplier is *unknown*, and flooring it at a mid-range score converts silence into
  adequacy (SDV-R5) · that a BOM must be **acyclic** or explosion never terminates (SPL-R1) · that
  a reorder point **contains** its safety stock by definition (INV-R1) · that a perfect-order rate,
  being a conjunction, is at most its worst component (ORD-R6) · and that an **ordinal product
  stays ordinal**, so risk scores may not be averaged (RSK-R5).
  **What was retired, by kind:** ~20 invented status machines and lifecycle guards · ~15 field
  range checks (`confidencePct ∈ [0,100]`, priority `∈ [1,5]`, horizon `∈ [1,52]`) · 4 money
  representation rules that belong to **ENG-R4** · the over-receipt tolerance and the
  mandated-safety-stock-method rules, which were policy.
  **Two corrections made during the sweep:** an ID must never be redefined — I first reused
  a retired ID for a new statement and had to reallocate it — three times over — and my first
  count of the retirements was wrong. The reallocations are recorded in the id-registry, which is
  the one place allowed to name a retired ID; the registry now carries the
  verified figures.
- ✅ **C2b · WHAT** — Several retired rules named a principle worth keeping *somewhere*: FIFO/FEFO
  picking discipline, corrective-action effectiveness verification, immutability of a committed
  plan. Each belongs to a concept node or a project's own process, not to a rule file — place them
  deliberately rather than letting them vanish.
- ✅ **C3 · WHAT** — **Stale rule citations swept, and mechanized so it cannot recur (2026-07-27).**
  ADR-0037 and Phase C2 retired **52** rule IDs; the estate carried **141 citations** of them across
  82 files. A citation of a retired ID is invisible to G4 — it is not a broken link, it silently
  resolves to nothing and reads as law — so this was worth a gate, not just a pass.
  **New gate G11:** no document cites a withdrawn rule ID. The retirement tables are the
  machine-readable source, read from the **first column only** (an ID named in the *why retired*
  prose is a live rule being pointed at). Exempt, on principle rather than convenience: the rule
  file that declares the retirement, the **id-registry** (a retirement is an allocation fact), and
  the **ADRs** (append-only history — editing an old decision to remove an ID would falsify it).
  **Substitutions were judged, not blanket-renamed** — a money rule split into an identity and a
  code duty; an inventory rule kept its physical impossibility and shed its policy exception;
  non-negativity bullets were deleted outright because a mean of absolute values is non-negative by
  arithmetic; invented lifecycles became "the project's own lifecycle". The full old→new map lives
  in the **id-registry**, which is the allocation authority and the one place allowed to name a
  withdrawn ID.
  **I repeated my own recorded mistake.** I ran broad regex substitutions over prose again and
  corrupted five places — including, with some irony, the registry line that *declares* the
  retirements, which came out asserting that a live inventory rule had been retired. Caught by
  reading the diff, fixed by hand. **G11 then caught 36 citations the sweep had missed**, and
  finally caught this very backlog entry naming withdrawn IDs while explaining them. That is the
  argument for the gate: the script was neither sufficient nor safe, and only the gate was
  reliable.
- ✅ **C4 · WHAT** — **Prose that still described deleted code (2026-07-27).**
  **The agent definitions came first, because they instruct future work** — an agent told to build
  `packages/domain` aggregates would have sent the next session straight back into the mistake.
  Four rewritten: `calc-engineer` (Python is the tools layer, and it now carries the lesson that a
  policy default in a signature is how one company's habits get inherited), `domain-knowledge`
  (leads with the inclusion test), `backend-engineer` (the only door to the frontend, serving
  monitoring), and the agents README.
  **A defect that would have propagated:** `templates/concept.md` still instructed authors to add
  an `## Implementations` section — which **G10 now rejects** — so every node created from it would
  have failed the build. It now teaches the current contract: unique CPT number, non-empty
  `## References`, no implementations, a **Project-chosen inputs** section, illustrative worked
  numbers, and a warning that G11 fails on a retired rule ID.
  **Risk register reconciled:** seven of eleven risks were **closed by the deletion itself** —
  the untested Python tree, the TS/PY divergence, the duplicate order-management packages, the
  heavy ML toolchain, the 84% of prose sitting outside the governed tree, the `IMPLEMENTATION.md`
  files specifying a different system (SAP/Superset/Airflow — itself evidence of the drift), and
  the spec-versus-code z-score contradiction. G10's structural blindness is superseded.
  **And the risk ADR-0037 created is now recorded as #11:** no gate can tell a standard from a
  plausible-looking invention. G10 checks that a source is *cited*, not that the content matches
  it. That is the residual, and it is how the original problem started.
  **ENG-R2 retired** — it governed `packages/domain`, which no longer exists; its intent survives
  as ENG-R10.1. ENG-R1's ring names updated to `apps → adapters → core`.
  Structural indices corrected: the knowledge-architecture allowlist, `docs/_index.md`,
  `40-contexts/_index.md`, the operating-model lane diagram, and the dept-03 section that framed
  two concepts as "specified but not implemented" (a code-state claim) rather than as measures of
  the planning process.
- 🟩 **C4b · WHAT — the operating layer swept (2026-07-27).** The 22 `.claude/skills/`, the four
  `.claude/commands/`, the agent definitions and the root `README.md`. They are the department
  know-how a project consults for *how* to implement, so they stay — but under the inclusion test.
  Measured first: only **13** policy lines by the number-plus-normative-word detector, far fewer
  than feared, because most of the drift was **stale paths**, not stated policy.
  **G11 had been giving a false green.** It only scanned front-matter documents, so the skills
  tree cited retired rules unseen; extended to `.claude/**` and `CLAUDE.md`, it immediately found
  **13** more (10 in agents/skills, then 3 in `testing-quality` alone). *A gate over part of the
  estate certifies the part it can see.*
  **The two worst files were the two most-read.** `supply-chain-core/SKILL.md` carried
  `Money = { amount: number }`, the `KG`/`L`/`M` codes `CLAUDE.md` names as an anti-pattern, the
  $5,000 threshold, a "World-Class KPI Benchmarks" table, a `service_level: float = 0.98` default
  in a signature, and a test **asserting round-half-up** against SCM-R14 — rewritten. The root
  `README.md` — the front door — still opened with a `src/departments/` tree, `npm test`, a
  "World Benchmark" KPI table and 26 "Algorithms Implemented" naming deleted `.ts` files;
  rewritten around the inclusion test.
  **Half-edits found by reading the diff back** (the third time this lesson has paid): the ABC
  and defect-classification tables had policy stripped from the *first* row and left in the rows
  below, which reads as though those numbers were the standard. Also fixed: a known-pitfalls entry
  left dangling mid-sentence around a deleted constant and a deleted test path.
  **Dead JS test estate removed:** `jest.config.js` still mapped the deleted `@scm/domain`, and
  `package.json` declared `test`/`test:unit`/`test:integration` over a `tests/` tree holding only
  the Rust golden fixture. Jest, ts-jest, eslint (never configured), `ts-node` and `@types/uuid`
  dropped; lockfile regenerated. `turbo.json` and `tsconfig.json` paths cleaned. **A runner that
  passes because it found nothing is worse than no runner — it reads as coverage.**
- 🟩 **C1d · WHAT — the divergence sections were a hiding place for policy (2026-07-27).**
  47 concept nodes still described differences between the **two deleted implementations**. That
  framing is why C1a missed real policy: its detector needed a number and a normative word on the
  same line, and `PY bands: <0 EXCELLENT · ≤30 GOOD` matches neither pattern. Removed here — the
  cash-to-cash rating bands, the bullwhip severity thresholds, the 5×5 risk-matrix level cuts,
  three competing AP matching tolerances, the 10% budget-variance bar, `Cpk ≥ 1.33 capable`, the
  0.5% bias dead band C1a had *reported removing*, and the 5% over-receipt default — the original
  ADR-0037 example, still sitting in a symbol table.
  **Questions the divergences were avoiding, now answered:** the σ estimate decides *which index
  you computed* (within-subgroup → Cp/Cpk, total-sample → Pp/Ppk — different names for exactly
  this reason); consensus forecasting is **two stages**, not two implementations; days-of-supply
  safety stock is two formulas, one of which collapses to zero on stable lead times; excluding
  in-transit shipments flatters OTD and the two bases never reconcile.
  **A correctness fix:** the statistical safety-stock example still used `z = 1.65` from the lookup
  table ADR-0028 retired in favour of the exact inverse normal.
  **G12 added — a rule citation names an ID.** `**FIN-R***` reads as law and resolves to nothing;
  it was invisible to G4 (not a broken link), G3 (not a duplicate) and G11 (not a retired ID). Most
  of the 47 stood in for *lifecycle* rules retired with the deleted application, so the wildcard
  was concealing precisely what it appeared to cover. The gate found one more in the core rule file
  itself, and was verified by planting a wildcard and watching it go red.
  **Eight `## Governing rules` sections were empty** — a heading promising law and delivering none.
  Filled with what actually governs each forecasting method (DMD-R6 on undefined percentage error,
  DMD-R9 on horizon and bucket, and Holt-Winters' two-season requirement as arithmetic).
  **The scripted-edit lesson paid for the fourth time:** four replacements left dangling tails
  because the original line continued onto the next. Caught by reading the diff, fixed by hand.
- 🟩 **C1c · WHAT — the questions a project must answer, named (2026-07-27).** Every node that
  leaves a value to the project now carries a **Project-chosen inputs** table: **58 of 154**, up from
  9. The rest are pure identities (conservation, a sum, a ratio of two given quantities) and
  correctly have no free parameter — the section is omitted rather than filled with "none".
  Measured by cue phrase rather than guessed: 49 nodes said "the project must choose this" in prose
  while giving the reader nothing to scan.
  **A recurring second row nobody thinks of:** the *population, period or basis*. Two teams
  computing the same formula over different denominators disagree while both being right — labour
  productivity per paid/present/on-task hour, PPM over received/inspected/shipped units, OTD against
  requested/promised/confirmed dates, LTIFR per 200,000 or 1,000,000 hours (a factor of five).
  **Three more surviving targets, found only because the table forced the question:** MPS stability
  "below the 0.85 bar", a PPM target of 500, and `PO_APPROVAL_THRESHOLD_CENTS = 500,000` still shown
  as *the* worked example while the prose above it said the threshold was project-chosen. Showing
  the invented number is how it gets copied.
  **And two more stale z-values:** `z = 1.65` from the lookup table ADR-0028 retired, in the
  Average-Max and combined-variability examples. Correcting the combined example changed its
  conclusion (93 units of under-buffering, not 95).
  `templates/concept.md` aligned to the table form so new nodes inherit it.
- 🟩 **C5 · WHAT — the regulatory framework was stating superseded law (2026-07-27).** Verified
  against the instruments themselves, not against the repository's own summaries — and the document
  was **wrong about CSDDD on three separate points**:
  it published the original three-phase scope (2027/2028/2029 at 5,000/3,000/1,000 employees), which
  **Directive (EU) 2026/470** replaced with a **single band — >5,000 employees ∧ >€1.5bn, from
  26 Jul 2029** (transposition 26 Jul 2028; roughly 13,000 undertakings became roughly 6,000);
  it stated penalties of **up to 5%** of worldwide turnover, now capped at **3%**;
  and it did not record that the **harmonised EU-wide civil liability regime was deleted**, so
  exposure now genuinely differs by Member State.
  **The catalogue was better than its own reference document** — CPT-0093 already recorded the
  Omnibus supersession — but it was *structured around the superseded test*, with the current law in
  a drift note underneath. A project reading its Formula section would have implemented the wrong
  directive. Current law now leads; the old phasing is kept below it, labelled as superseded and
  marked do-not-implement.
  **Rewritten around what the document is for:** the reference list behind the `CLAUDE.md` standards
  table, with a **verification date per entry** and a warning that the EU entries have changed three
  times in eighteen months. Added the instruments the catalogue cites but the framework had never
  listed — CBAM, EUDR, CSRD, IAS 2, ISO 2859-1, UN/ECE Rec 20, the ISO date/currency/country
  standards, IEEE 754 and the per-mode dangerous-goods regimes. Removed every `src/…` implementation
  reference and field name, and dropped the Gartner and McKinsey sections: a consultancy maturity
  model is not a standard, since an organisation can reasonably decline to use one.
  **Two more surviving thresholds found in passing:** the 85% space-utilization band C1a reported
  removing (still in an output description) and a 5%-of-exposure recommendation band in the SCOR
  agility node.
  **G12 had a blind spot of its own**, found while fixing a citation it should have caught:
  `**SCM-R7 / CMP-R***` escaped because the bold span opened on the *other* rule in the sentence.
  Narrowed to the bold citation form and widened to catch that shape; verified against both.

### Phase 1 — Product evolution (owner-defined)
- ⬜ Resolve the open decisions in `10-decisions/README.md` (runtime/persistence, API
  surface, versioning) — they gate any application layer built on these domains.
