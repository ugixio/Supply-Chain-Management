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
- ⬜ **U11 · WHAT lane** — Domain dedup & modeling follow-ups surfaced by the toolchain
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

### Phase 1 — Product evolution (owner-defined)
- ⬜ Resolve the open decisions in `10-decisions/README.md` (runtime/persistence, API
  surface, versioning) — they gate any application layer built on these domains.
