---
id: risk-register-archive
title: "Risk Register — closed rows (archive)"
type: archive
owner: orchestrator
status: archived
since: 2026-08-03
updated: 2026-08-03
relations:
  - { type: part-of, target: index-governance }
  - { type: governed-by, target: knowledge-architecture }
---
# Risk Register — closed rows

> **Why this file exists, and it is not tidiness.** `docs/program/load-sets.md` prices what a session
> reads *together*, and the `reviewing-the-estate` set reached its ceiling on 2026-08-03. That ceiling
> came with a declared structural answer — *archive closed rows to a dated file, do not raise the
> number* — and this is that answer being honoured rather than re-argued. Raising it would have been
> the fourth instance of a rule written and not applied (improvement #28).
>
> **Nothing is deleted.** The register's own discipline is that a closed risk stays listed, never
> removed, so old references resolve and the history of what was feared stays readable. These eight
> rows are exactly as they were; only their address changed. A reviewer wanting *live* exposure reads
> the register, and a reviewer wanting *what was already survived* reads this.
>
> **All eight closed on the same axis:** ADR-0037 deleted the invented application, and with it the
> code that seven of these risks were about. That is worth seeing in one place — it is the clearest
> single record of how much risk was carried by something that turned out not to belong.

| # | Risk | Likelihood | Impact | Owner | Mitigation / response | Status | Review trigger |
|---|---|---|---|---|---|---|---|
| 1 | Zero Python test files while `python/` holds half the estate's logic (the mirror-coverage bar, since retired) | high | high | orchestrator | **CLOSED by ADR-0037** — the Python tree was deleted, so there is no mirrored logic left to test. The generalized lesson (a gate must exercise what CI does) is improvement-register #6. | closed | U7 done |
| 2 | Formulas duplicated across TS and Python have already diverged once (commit `a12c114`) and can diverge again | medium | high | orchestrator | **CLOSED by ADR-0037** — the duplicated formulas were deleted with the two implementations that carried them. The golden-vector mechanism survives for the one calculation that remains (`crates/scm-money`). | closed | U8 done |
| 4 | `python/` contains two order-management packages (`07_order_management/` and `13_order_management/`) with overlapping names — numbering collision with `07_logistics_transportation` | medium | medium | orchestrator | **CLOSED by ADR-0037** — both packages were deleted. The department *keys* were never the problem and are unaffected. | closed | first task touching either package |
| 6 | Heavy ML dependencies (`torch`, `tensorflow`, `ray`) make the Python toolchain unrunnable in CI for now | medium | medium | orchestrator | **CLOSED by ADR-0037** — no Python code remains, so nothing heavy is pulled. It returns as a live risk when Phase M adds model tooling; the CI-light split is the known answer. | closed | U7 done |
| 7 | **150,322 words (84% of repo prose) sit outside the governed tree** — 14 `IMPLEMENTATION.md` (128,240) + 14 dept `README.md` (22,082) vs 29,522 governed. Allowlisted, so invisible to every gate: no front-matter, no IDs, no link checking, no orphan detection | high | high | orchestrator | **CLOSED by ADR-0037** — the ungoverned prose was deleted with the code it described. Worth remembering *why* it was a risk: 84% of the repository's words sat outside the governed tree, so the gates were certifying a minority of the content. | closed | U18 done |
| 8 | `IMPLEMENTATION.md` files specify a **different system** — SAP S/4HANA · SAP Ariba · PostgreSQL · Superset · Airflow star-schema BI (195 Superset / 178 PostgreSQL / 117 SAP refs) — with no counterpart in `src/`. An agent reading them for guidance would build toward the wrong architecture | high | high | orchestrator | **CLOSED by ADR-0037** — those documents specified a different system entirely, which was itself evidence that the estate had drifted into inventing a product. Deleted. | closed | U18 done |
| 9 | Spec/code contradiction found on the first extraction: `IMPLEMENTATION.md` §10 mandates `z = scipy.stats.norm.ppf(service_level)` while TS and Python both use interpolated tables and disagree with each other (PY up to +1.57% off exact at 92%). The §12 validation "recompute z and compare" **cannot pass today** | high | medium | human | **CLOSED at Phase C1a** — the specification was right and both implementations were wrong; the exact inverse-normal is now the only statement, in CPT-0003, with no implementation to contradict it. | closed | U15 decided |
| 10 | Gate G10 is structurally blind to concepts that exist in the domain but in no code — the extraction already found two required KPIs (FVA, safety-stock adequacy) with zero implementation. A green G10 can be misread as "the domain is covered" | medium | medium | orchestrator | **SUPERSEDED by ADR-0037** — G10 no longer maps concepts to code, so the blindness is moot. The residual risk is real and now named in `25-concepts/_index.md`: no gate can tell a standard from a plausible-looking invention. | closed | U18 done |
