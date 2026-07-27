---
description: >
  Cross-department supply-chain expertise — SCOR-DS process mapping, the standards this
  context carries (ISO/GS1/Incoterms), the cross-cutting invariants, and the OSI analytics
  stack. Use when a task spans multiple departments, maps to SCOR, touches the shared
  standards module, or needs a cross-department architecture decision.
---

# Supply Chain Core — Cross-Department Reference

> **This repository is a context, not a product** (ADR-0037). A statement belongs here only if a
> standards body, a regulator or an arithmetic identity fixes it. Anything an organization can
> reasonably choose — a threshold, a target, a weighting, a rating band, a service level — is
> project policy and is named as a question, never answered. The one application built here is
> monitoring.

## SCOR Digital Standard (ASCM 2019) — process hierarchy

| Level | Processes |
|-------|-----------|
| 1 — Strategic | Plan, Source, Make, Deliver, Return, Enable |
| 2 — Configuration | P1–P5, S1–S3, D1–D4, R1–R5, E1–E8 |
| 3 — Activity | D1.1 Process Inquiry, D1.2 Receive/Validate Order … |
| 4 — Implementation | Company-specific tasks — outside this context by definition |

**SCOR-DS → department mapping**
| SCOR | Department |
|------|-----------|
| Plan (P1–P5) | 03-demand-planning, 04-supply-planning, 12-sop-planning |
| Source (S1–S3) | 01-procurement |
| Deliver (D1–D4) | 07-logistics-transportation, 13-order-management |
| Return (R1–R5) | 05-inventory-management |
| Enable (E1–E8) | 02-supplier-management, 06-warehouse-management, 08-quality-management, 09-compliance-regulatory, 10-risk-management, 11-finance-controlling, 14-supplier-development |

A department **is** its concept nodes (`docs/25-concepts/NN-<key>/`), its rules
(`docs/40-contexts/NN-<key>/rule.md`) and its practice skill (`.claude/skills/<key>/`). There is
no department code tree here — a project implements the department in its own repository.

## The standards module (`packages/shared`)

Reference data only: ISO 4217 currencies and minor units, ISO 3166-1 countries, UN/ECE Rec 20
units, Incoterms 2020 with the four sea-only rules, GS1 key validation. It holds no money type,
no status vocabulary and no policy value.

```typescript
// UN/ECE Rec 20 codes — three letters, not the intuitive abbreviation.
// KGM not KG · LTR not L · MTR not M. The short forms were an invented shorthand that
// silently failed conformance for months; this is the standard's spelling.
import { UOM, INCOTERMS_2020, INCOTERMS_SEA_ONLY, isValidGS1Key } from '@scm/shared';
```

**Money never appears as a `number`.** Exact monetary arithmetic is Rust (`crates/scm-money`):
banker's rounding per IEEE 754-2019 §4.3.3 and sum-preserving apportionment (SCM-R14). A
TypeScript money type would be a second implementation of the one thing that must have exactly
one (ENG-R4/R5, ENG-R10).

## Cross-cutting invariants (externally fixed — `SCM-R*`)

Cited, never restated — the text is in `docs/30-foundation/scm-core/rule.md`:

- **SCM-R3** a financial record is corrected by a further entry, never destroyed · **SCM-R4**
  every inventory movement balances (debits = credits) · **SCM-R6** UFLPA Xinjiang presumption ·
  **SCM-R7** CSDDD retention ≥ 5 years · **SCM-R9** ISO 8601 dates, UTC instants ·
  **SCM-R10** a quantity carries its GS1 unit · **SCM-R14** exact money, ties to even.

**What is *not* here.** Negative-stock policy, approval thresholds, receipt tolerances, service
levels, AQL levels, scorecard weights, lot granularity and every KPI target are project
decisions. `docs/30-foundation/scm-core/rule.md` §Project decisions lists them with the standard
that constrains each — and supplies no default. A published "world-class" figure is a textbook
illustration, not a requirement; quoting one as a target is how policy gets laundered into law.

**Engineering law** lives in `ENG-R*`: inward dependencies, exact money, generated artefacts,
exclusive technology lanes, the Rust core boundary. Also English-only in code, comments, docs,
configuration and commit messages.

## Analytics that generalize

**SQL patterns** — safe against the failure modes, free of policy:
```sql
-- Never divide by a possibly-zero denominator.
value / NULLIF(denominator, 0) AS ratio
-- Pareto / ABC running share.
SUM(metric) OVER (ORDER BY metric DESC) / SUM(metric) OVER () * 100 AS cum_pct
-- A correction appends; it does not delete (SCM-R3).
INSERT INTO ledger (..., reverses_id) VALUES (..., $1);
-- Retry safety at the write boundary.
INSERT INTO movements (...) ON CONFLICT (idempotency_key) DO NOTHING RETURNING *;
```
Money in SQL is `NUMERIC`, never `float8`, and display scaling happens at the presentation edge.

**Model selection** (Python tools lane — ADR-0033/0035):
| Task | Common choice | Library |
|------|---------------|---------|
| Demand with trend + season | Holt-Winters | `statsmodels` |
| Many series at scale | AutoARIMA / ETS | `statsforecast` |
| Short-horizon demand sensing | Gradient boosting | `lightgbm` |
| Anomaly detection | Isolation Forest | `scikit-learn` |
| Routing · scheduling | VRP · CP-SAT | `ortools` |
| Risk simulation | Monte Carlo | `numpy` |
| Concentration / network analysis | Graph metrics | `networkx` |
| Discrete-event simulation | DES | `simpy` |

Every library above is OSI-licensed, commercially usable and modifiable (ADR-0002); check the
licence before adding a new one — `ultralytics` (YOLO) is AGPL-3.0 and needs a decision, not an
import.

**Forecast metrics** — definitions (Hyndman & Koehler 2006, IJF 22(4)), no acceptance bands:
```python
def forecast_metrics(actuals: np.ndarray, forecasts: np.ndarray) -> dict[str, float]:
    """MAE, MAPE, RMSE, bias and WMAPE. Report all of them: MAPE alone hides sign,
    and it is undefined wherever an actual is zero — hence the mask and WMAPE."""
    errors = actuals - forecasts
    mask = actuals != 0
    return {
        "mae": float(np.mean(np.abs(errors))),
        "rmse": float(np.sqrt(np.mean(errors**2))),
        "mape": float(np.mean(np.abs(errors[mask] / actuals[mask])) * 100),
        "bias": float(np.mean(errors[mask] / actuals[mask]) * 100),
        "wmape": float(np.sum(np.abs(errors)) / np.sum(np.abs(actuals)) * 100),
    }
```
Whether a given MAPE is good enough depends on the decision the forecast feeds. **Never give a
parameter a default in a signature** — `service_level: float = 0.98` gets inherited without
anyone deciding, which is worse than a named constant.

## Known pitfalls

<!-- Fed by orchestrator corrections (docs/program/operating-model.md §4.7). Read before writing. -->

- **A plausible-looking invention passes every gate.** `KG` looks like a GS1 unit; the code is
  `KGM`. No check can tell a standard from a confident-sounding fabrication — verify against the
  standard's own text, and cite where it says so.
- **A textbook number read as a specification.** "World-class OTD ≥ 95%" is an illustration.
  Once it is written in a table headed "target", every project inherits it.
- **A default hidden in a signature.** See above; this is the quietest way policy enters.
- **Rounding money half-up.** Ties resolve to **even** (SCM-R14). A test asserting half-up pins
  the wrong behaviour and looks authoritative doing it.
