---
id: concept-risk-matrix-5x5
title: "5×5 Risk Matrix & Risk Level (CPT-0071)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-10-risk-management }
  - { type: governed-by, target: index-adr }
---
# 5×5 Risk Matrix & Risk Level (CPT-0071)

> The qualitative risk grid: probability (1–5) × impact (1–5) → a score 1–25 mapped to
> LOW / MEDIUM / HIGH / CRITICAL. The standard triage tool of ISO 31000-style registers.

## Formula

    score = probability × impact       (1..25)
    score = likelihood × impact          each on an ordinal 1–5 scale → score ∈ [1, 25]

Where the score bands sit, and what each band obliges, are **project-chosen** — they express
risk appetite. Note the arithmetic trap they must respect: the product of two ordinal scales is
not itself an interval scale, so a score of 20 is not "twice as bad" as 10, and several
distinct likelihood/impact pairs collapse onto the same number (4×5 and 5×4 both give 20 while
demanding different responses).

| Symbol | Meaning | Unit |
|---|---|---|
| probability / likelihood | 1 rare … 5 almost certain | ordinal |
| impact | 1 negligible … 5 catastrophic | ordinal |

## Inputs and outputs

- **Inputs:** two integers in [1,5] (validated; PY raises outside range).
- **Output:** the level literal; TS `createRiskItem` stamps `riskScore` and `riskLevel`
  at creation from the same mapping.

## Assumptions and limits

- Ordinal × ordinal multiplication is a *convention*, not measurement — a 5×1 and a
  1×5 both score 5 but mean different things (frequent trivia vs rare catastrophe);
  keep the raw pair visible next to the level.
- **CRITICAL divergence (recorded):** the two languages disagree materially — a score
  of 15 is HIGH in Python but CRITICAL in TypeScript; a 8 is LOW in Python (≤8) but
  HIGH in TypeScript (≥8). The same risk item classifies two levels apart. This is a
  U15b-class owner decision; until resolved, the TS thresholds govern the domain
  records (they stamp `RiskItem`), the PY ones the analytics.
- **Does not apply when:** quantitative loss data exists — prefer EAL (CPT-0072) /
  VaR (CPT-0077) over matrix positioning.

## Worked example

probability 4, impact 4 → score 16 → PY **HIGH**, TS **CRITICAL** (the divergence in
action).

## Governing rules

- **RSK-R*** — risk items carry score, level, strategy and owner; registers are
  soft-deleted (SCM-R3).

## Related

- CPT-0072 EAL — the quantitative next step.
- CPT-0080 BCP readiness — the mitigation-side scorecard.

## References

- ISO 31000:2018 — risk assessment; ISO/IEC 31010 — risk matrix technique (with its
  known criticisms: Cox (2008), *Risk Analysis* 28(2)).
