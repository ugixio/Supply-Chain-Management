---
id: concept-composite-compliance-risk-score
title: "Composite Compliance Risk Score (CPT-0098)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-09-compliance-regulatory }
  - { type: governed-by, target: index-adr }
---
# Composite Compliance Risk Score (CPT-0098)

> One weighted 0–100 compliance grade per supplier across regulations, plus the
> generic weighted-criteria due-diligence scorer beneath it.

## Formula

    weights: CSDDD 0.30 · UFLPA 0.25 · REACH 0.20 · EUDR 0.15 ·
             others share a 0.10 pool equally
    overall = Σ score_r · w_r / Σ w_r         (normalized over regulations present)
    bands: ≥80 LOW · ≥60 MEDIUM · ≥40 HIGH · <40 CRITICAL

    due_diligence_score = Σ (compliant_i · w_i) / Σ w_i × 100
    (weights need not sum to 1 — normalized internally; missing weight defaults 1.0)

| Symbol | Meaning | Unit |
|---|---|---|
| score_r | per-regulation compliance score (100 = fully compliant) | 0–100 |
| criteria | {criterion: bool} checklist | booleans |

## Inputs and outputs

- **Inputs:** non-empty assessment list `{regulation, score}` (scores validated
  0–100); criteria/weights dicts.
- **Output:** `{overall_score, by_regulation, risk_level, assessed_regulations}`;
  due-diligence score 0–100 (empty criteria → 0).

## Assumptions and limits

- Weight **renormalization over present regulations** means a supplier assessed only
  on REACH is graded 100% on REACH — absence of assessment silently drops the other
  duties. Pair with a coverage check (which regulations *should* apply — CPT-0093 for
  CSDDD, HS-based scoping for CBAM) before trusting LOW risk.
- The banding inverts the score (high score = low risk) — opposite polarity to
  CPT-0065's supplier risk score; don't mix the two scales in one dashboard column
  without labelling.
- A binary PROHIBITED condition (UFLPA entity list) must **veto**, not average: a 95
  overall with a UFLPA import bar is still unshippable (CPT-0061 note applies).
- **Does not apply when:** regulations demand pass/fail evidence (a weighted 74% on
  REACH notification duty has no legal meaning) — use it for prioritization, not
  attestation.

## Worked example

CSDDD 80, UFLPA 60, REACH 90, LKSG 70 → weights 0.30/0.25/0.20/0.10 (Σ = 0.85) →
overall = (24 + 15 + 18 + 7)/0.85 = **75.3 → MEDIUM**.

## Governing rules

- **CMP-R2** — every component of the composite carries its own provenance, or the composite has
  none. **SCM-R7** — retention per CPT-0096; **SCM-R6** — UFLPA documentation.

## Related

- CPT-0093/0094/0095 — the per-regulation inputs.
- CPT-0065 Supplier composite risk — the opposite-polarity operational score.

## References

- ISO 28000:2022 / ISO 31000 — weighted assessment practice; regulation-specific
  references at the input nodes.
