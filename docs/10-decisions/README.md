---
id: index-adr
title: "Architecture Decision Records (ADR-0001..0013)"
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
- ADR-0010 — The ugixio context skeleton governs knowledge (tiers, SSOT, append-only ADRs). (proposed)
- ADR-0011 — Conventional Commits, SemVer annotated tags, main always green. (proposed)
- ADR-0012 — Context economics + executable gates: verify fast/full (G1–G7+G9), exemplar-unit rule, known-pitfalls feedback, evaluation protocol, risk/improvement registers, communication contract. (proposed)
- ADR-0013 — npm is the single package manager; `package-lock.json` is the only lockfile. (proposed)

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

**Status:** Accepted (retroactive)

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

**Status:** Proposed (accepted when this branch merges)

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

**Status:** Proposed

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

**Status:** Proposed
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

**Status:** Proposed
**Extends:** ADR-0001, ADR-0009

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

---

## Open decisions (starter backlog — each answer becomes an ADR)

- [ ] **Runtime & persistence architecture.** Per-department `schema.sql` files exist but
      no engine choice, migration runner or application layer is recorded. What executes
      this domain logic, and against what store?
- [ ] **API/product surface.** Library? Service? UI? Nothing is recorded.
- [x] **Package manager + lockfile.** → **ADR-0013** (npm + `package-lock.json`).
- [ ] **Repository LICENSE file.** `package.json` declares MIT but no LICENSE file
      exists; if commercial distribution is intended, revisit (and the AGPL note in
      ADR-0002).
- [x] **CI + verify green-gate.** → **ADR-0012** (`make verify` / `make verify-full`,
      doc gates G1–G7+G9, CI workflow). Still pending inside it: eslint flat config
      (lint) and the pytest gate (U7) — tracked in `program/WORKFLOW.md`.
- [ ] **Versioning scheme.** First annotated tag; what 1.0.0 means (ADR-0011 pending).
- [ ] **Agent lanes.** Formalize WHAT/HOW/SPECIALTY lanes and profiles
      (`program/operating-model.md`) or keep single-orchestrator mode.
- [ ] **Cross-language consistency policy.** TS and Python implement overlapping formulas
      (e.g. risk bands — see fix `a12c114`); decide the single-source mechanism (shared
      spec, golden tests, or codegen).

---

> **File map:** this README is the canonical ADR index. New decisions are appended here
> as `## ADR-NNNN — Title` (or as `docs/10-decisions/NNNN-title.md` when extensive).
> Numbers come from `00-governance/id-registry.md` §3.
