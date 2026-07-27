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

- **Inputs:** two integers on the 1–5 ordinal scales. A value outside the scale is an error,
  not a value to clamp — clamping silently turns an unrated risk into a rated one.
- **Output:** the score, and the band it falls in under the project's own mapping. Keep the
  **pair** stored alongside, not only the product: the product is lossy (see below), so a
  register that keeps just the score cannot be re-banded later without re-assessing.

## Assumptions and limits

- Ordinal × ordinal multiplication is a *convention*, not measurement — a 5×1 and a
  1×5 both score 5 but mean different things (frequent trivia vs rare catastrophe);
  keep the raw pair visible next to the level.
- **One mapping, applied everywhere.** Two systems banding the same score differently is not a
  disagreement about risk, it is two different scales sharing one word — a register and its
  analytics that disagree by two bands on the same item make the register unusable as evidence.
  The mapping is chosen once and applied by every consumer.
- **Does not apply when:** quantitative loss data exists — prefer EAL (CPT-0072) /
  VaR (CPT-0077) over matrix positioning.

## Project-chosen inputs

| Input | Why the project must choose it |
|---|---|
| The band boundaries over 1–25, and their inclusivity | They express risk appetite; the boundary case is the one that gets argued about, so state whether a boundary score falls in the higher band or the lower one |
| What each band obliges (escalation, treatment, acceptance) | A band with no consequence is a label |
| The wording of each 1–5 anchor | "Likely" means nothing until the scale says what it means; unanchored scales are not comparable between assessors |

## Worked example

Likelihood 4, impact 4 → **score 16**. Whether that is the top band or the one below is the
project's mapping, and 16 also arises as 2×8 — impossible on a 1–5 scale — which is a reminder
that the product loses information the pair carries.

## Governing rules

- **RSK-R5** — an ordinal product stays ordinal: scores are not averaged, and equal scores do
  not mean equal risk. **SCM-R3** — a risk register entry is corrected, never destroyed.

## Related

- CPT-0072 EAL — the quantitative next step.
- CPT-0080 BCP readiness — the mitigation-side scorecard.

## References

- ISO 31000:2018 — risk assessment; ISO/IEC 31010 — risk matrix technique (with its
  known criticisms: Cox (2008), *Risk Analysis* 28(2)).
