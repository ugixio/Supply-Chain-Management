---
id: risk-register
title: "Risk Register"
type: governance
owner: orchestrator
status: draft
since: 2026-07-19
updated: 2026-07-29
relations:
  - { type: part-of, target: index-governance }
  - { type: governed-by, target: knowledge-architecture }
---
# Risk Register

> The single home for **identified risks** — technical, security, delivery and knowledge
> risks that are accepted-for-now rather than fixed-now (ADR-0012). A row makes the
> exposure visible, owned and reviewable; it never substitutes for fixing what a hard
> rule forbids. Rows are appended and updated in status; closed risks stay listed
> (mitigated / retired), never deleted.

## How to use

- Anyone may PROPOSE a risk; the owner accepts it into the register.
- Every risk has exactly one owner and a **review trigger** (an event or date that forces
  a re-look). A risk without a trigger is a worry, not a register entry.
- A risk that hardens into policy becomes a rule (`rule.md`) or a decision (ADR), and the
  row links to it. A risk deliberately left open cites the reasoning.
- Score likelihood and impact coarsely (`low | medium | high`) — the register ranks
  exposures; it does not pretend precision.

## Register

| # | Risk | Likelihood | Impact | Owner | Mitigation / response | Status | Review trigger |
|---|---|---|---|---|---|---|---|
| 1 | Zero Python test files while `python/` holds half the estate's logic (the mirror-coverage bar, since retired) | high | high | orchestrator | **CLOSED by ADR-0037** — the Python tree was deleted, so there is no mirrored logic left to test. The generalized lesson (a gate must exercise what CI does) is improvement-register #6. | closed | U7 done |
| 2 | Formulas duplicated across TS and Python have already diverged once (commit `a12c114`) and can diverge again | medium | high | orchestrator | **CLOSED by ADR-0037** — the duplicated formulas were deleted with the two implementations that carried them. The golden-vector mechanism survives for the one calculation that remains (`crates/scm-money`). | closed | U8 done |
| 3 | Default branch on GitHub is `claude/bold-cannon-l7wtso`, not a stable main line | high | medium | human | set `main` as default and protect it when the unification branch merges (ADR-0011) | open | branch merge |
| 4 | `python/` contains two order-management packages (`07_order_management/` and `13_order_management/`) with overlapping names — numbering collision with `07_logistics_transportation` | medium | medium | orchestrator | **CLOSED by ADR-0037** — both packages were deleted. The department *keys* were never the problem and are unaffected. | closed | first task touching either package |
| 5 | Gate G8 (English-only) is not machine-checked; prose drift can enter unnoticed | medium | low | orchestrator | manual review at merge; automate if drift is observed | open | first observed violation |
| 6 | Heavy ML dependencies (`torch`, `tensorflow`, `ray`) make the Python toolchain unrunnable in CI for now | medium | medium | orchestrator | **CLOSED by ADR-0037** — no Python code remains, so nothing heavy is pulled. It returns as a live risk when Phase M adds model tooling; the CI-light split is the known answer. | closed | U7 done |
| 7 | **150,322 words (84% of repo prose) sit outside the governed tree** — 14 `IMPLEMENTATION.md` (128,240) + 14 dept `README.md` (22,082) vs 29,522 governed. Allowlisted, so invisible to every gate: no front-matter, no IDs, no link checking, no orphan detection | high | high | orchestrator | **CLOSED by ADR-0037** — the ungoverned prose was deleted with the code it described. Worth remembering *why* it was a risk: 84% of the repository's words sat outside the governed tree, so the gates were certifying a minority of the content. | closed | U18 done |
| 8 | `IMPLEMENTATION.md` files specify a **different system** — SAP S/4HANA · SAP Ariba · PostgreSQL · Superset · Airflow star-schema BI (195 Superset / 178 PostgreSQL / 117 SAP refs) — with no counterpart in `src/`. An agent reading them for guidance would build toward the wrong architecture | high | high | orchestrator | **CLOSED by ADR-0037** — those documents specified a different system entirely, which was itself evidence that the estate had drifted into inventing a product. Deleted. | closed | U18 done |
| 9 | Spec/code contradiction found on the first extraction: `IMPLEMENTATION.md` §10 mandates `z = scipy.stats.norm.ppf(service_level)` while TS and Python both use interpolated tables and disagree with each other (PY up to +1.57% off exact at 92%). The §12 validation "recompute z and compare" **cannot pass today** | high | medium | human | **CLOSED at Phase C1a** — the specification was right and both implementations were wrong; the exact inverse-normal is now the only statement, in CPT-0003, with no implementation to contradict it. | closed | U15 decided |
| 10 | Gate G10 is structurally blind to concepts that exist in the domain but in no code — the extraction already found two required KPIs (FVA, safety-stock adequacy) with zero implementation. A green G10 can be misread as "the domain is covered" | medium | medium | orchestrator | **SUPERSEDED by ADR-0037** — G10 no longer maps concepts to code, so the blindness is moot. The residual risk is real and now named in `25-concepts/_index.md`: no gate can tell a standard from a plausible-looking invention. | closed | U18 done |
| 11 | **No gate can tell a standard from a plausible-looking invention.** G10 checks that a source is *cited*, not that the content matches it — a number copied from a textbook example reads exactly like a regulation. This is the residual of ADR-0037, and it is how the original problem started. | medium | high | orchestrator | the inclusion test at the head of `CLAUDE.md`; the anti-states in `30-foundation/scm-core/rule.md` as the reviewer's checklist; every node names its source so a claim can be checked against it | open | any new rule or concept node; any citation that cannot be followed to a published document |
| 12 | **A citation can stop matching its source without anything changing in this repository.** The law moves; the document does not. C5 found `REGULATORY_FRAMEWORK.md` publishing the superseded CSDDD phase-in, a penalty cap that had been reduced from 5% to 3%, and no record that the EU-wide civil liability regime had been deleted — all while every gate stayed green, because a gate can check that a source is *cited*, never that the source still says it. | high | high | orchestrator | a **verification date per entry** in `docs/standards/REGULATORY_FRAMEWORK.md`, so staleness is visible rather than invisible; the EU entries flagged as the shortest half-life; regulatory nodes carry their own verified-on date | open | any entry older than a year; any EU sustainability instrument, which have changed three times in eighteen months |
| 13 | **The agent and skill layer states policy as law, and no gate reads it.** `.claude/skills/**` publishes KPI *target* tables — `OTD ≥ 95%`, `Fill Rate ≥ 98%`, `Inventory Accuracy ≥ 99.5%`, `CoPQ < 2% of revenue`, `NCR closure ≥ 95% in 30 days` — and `.claude/commands/**` instructs a review of application code that ADR-0037 deleted. This is the same defect ADR-0037 corrected in `docs/`, in the one place that is loaded into every session's working set rather than read on demand. Two files show a sweep started there and stopped (`procurement` row 28, `quality-management` row 30), which is how it survived. | high | high | orchestrator | found and scoped by the 2026-07-29 file-by-file review; G8/G11/G12/G13 now read every tracked Markdown file including `.claude/**`, so the *citation* classes are covered — **swept 2026-07-29**: all fourteen department KPI tables rewritten from a level column into the decision plus what constrains it, the retired approval-threshold rule removed from the procurement code sample, the invented status vocabulary named as a project's own, the XYZ CV bands and the CMMI score bands removed, and all four commands reframed to review a *project's* code against this context. The residual is the class, not the instances: no gate can distinguish a target from a definition, so the next skill file added can reintroduce it. | mitigated | any new skill file; any KPI table anywhere in the estate; the next session that loads a department skill |

