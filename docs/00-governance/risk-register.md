---
id: risk-register
title: "Risk Register"
type: governance
owner: orchestrator
status: draft
since: 2026-07-19
updated: 2026-07-19
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
| 1 | Zero Python test files while `python/` holds half the estate's logic (SCM-R13 mirror-coverage bar unmet) | high | high | orchestrator | backlog U7 (pytest suite); until then Python changes need reviewer scrutiny | open | U7 done |
| 2 | Formulas duplicated across TS and Python have already diverged once (commit `a12c114`) and can diverge again | medium | high | orchestrator | golden test vectors shared by both languages (backlog U8); evaluation.md §1.4 both-or-neither rule | open | U8 done |
| 3 | Default branch on GitHub is `claude/bold-cannon-l7wtso`, not a stable main line | high | medium | human | set `main` as default and protect it when the unification branch merges (ADR-0011) | open | branch merge |
| 4 | `python/` contains two order-management packages (`07_order_management/` and `13_order_management/`) with overlapping names — numbering collision with `07_logistics_transportation` | medium | medium | orchestrator | WHAT-lane review: consolidate or rename to match the 14-department taxonomy (ADR-0004) | open | first task touching either package |
| 5 | Gate G8 (English-only) is not machine-checked; prose drift can enter unnoticed | medium | low | orchestrator | manual review at merge; automate if drift is observed | open | first observed violation |
| 6 | Heavy ML dependencies (`torch`, `tensorflow`, `ray`) make the Python toolchain unrunnable in CI for now | medium | medium | orchestrator | CI runs TS + doc gates only; Python gate lands with U7 (split a light requirements file for CI) | open | U7 done |
| 7 | **150,322 words (84% of repo prose) sit outside the governed tree** — 14 `IMPLEMENTATION.md` (128,240) + 14 dept `README.md` (22,082) vs 29,522 governed. Allowlisted, so invisible to every gate: no front-matter, no IDs, no link checking, no orphan detection | high | high | orchestrator | ADR-0016 extract-and-archive; backlog U18. Until extracted, these files are **not** architectural authority and must not be cited as such | open | U18 done |
| 8 | `IMPLEMENTATION.md` files specify a **different system** — SAP S/4HANA · SAP Ariba · PostgreSQL · Superset · Airflow star-schema BI (195 Superset / 178 PostgreSQL / 117 SAP refs) — with no counterpart in `src/`. An agent reading them for guidance would build toward the wrong architecture | high | high | orchestrator | ADR-0016 declares the stack non-normative; archival stamp on each file as its department is extracted | open | U18 done |
| 9 | Spec/code contradiction found on the first extraction: `IMPLEMENTATION.md` §10 mandates `z = scipy.stats.norm.ppf(service_level)` while TS and Python both use interpolated tables and disagree with each other (PY up to +1.57% off exact at 92%). The §12 validation "recompute z and compare" **cannot pass today** | high | medium | human | CPT-0003 records all three definitions; canonical choice is U15, feeding U8 golden vectors. No code changed pending that decision | open | U15 decided |
| 10 | Gate G10 is structurally blind to concepts that exist in the domain but in no code — the extraction already found two required KPIs (FVA, safety-stock adequacy) with zero implementation. A green G10 can be misread as "the domain is covered" | medium | medium | orchestrator | Documented in `25-concepts/_index.md` ("What G10 cannot see"); unimplemented concepts carry `status: draft` + an explicit Status section | open | U18 done |
