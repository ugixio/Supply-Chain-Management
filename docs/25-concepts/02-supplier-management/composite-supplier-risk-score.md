---
id: concept-composite-supplier-risk-score
title: "Composite Supplier Risk Score (CPT-0065)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-02-supplier-management }
  - { type: governed-by, target: index-adr }
---
# Composite Supplier Risk Score (CPT-0065)

> One 0–100 risk number per supplier from five weighted exposures — financial health,
> geography, sourcing concentration, capacity strain and open compliance issues.

## Formula

    risk = 0.35·(100 − financial_score)
         + 0.25·geographic_risk
         + 0.15·(100 if single_source else 0)
         + 0.15·max(0, (util − 85)/15 · 100)      (capacity strain above 85%)
         + 0.10·min(100, flags/5 · 100)
    ≥75 CRITICAL · ≥50 HIGH · ≥25 MEDIUM · else LOW

| Symbol | Meaning | Unit |
|---|---|---|
| financial_score | financial health (higher = healthier) | 0–100 |
| geographic_risk | country/region index (higher = riskier) | 0–100 |
| util | capacity utilisation | percent |
| flags | open CSDDD/UFLPA/REACH issues | count (5 caps at 100) |

## Inputs and outputs

- **Inputs:** all components clamped to [0,100] defensively.
- **Output:** `{risk_score, risk_level, components}` — the per-component contribution
  breakdown makes the driver visible (2 dp).

## Assumptions and limits

- Additive-linear model: components are treated as independent; a supplier that is
  simultaneously single-source *and* financially weak is riskier than the sum
  suggests — treat CRITICAL as a floor, not a ceiling.
- Where capacity strain starts to count, and how steeply it rises, are **project-chosen** —
  below the knee, utilisation is considered healthy.
- The compliance component **counts** open flags; severity lives in the compliance
  department (CPT-0091-family); a single UFLPA detention order still only moves this
  score by ≤ 10 points — compliance vetoes are separate (CPT-0061 note).
- **Does not apply when:** scoring the *network* effect of upstream fragility — that is
  the GNN's job (CPT-0069).

## Worked example

financial 60, geo 70, single-source, util 95%, 2 flags →
`0.35·40 + 0.25·70 + 0.15·100 + 0.15·(10/15·100) + 0.10·40 = 14 + 17.5 + 15 + 10 + 4 = 60.5`
→ **HIGH**, driven by geography + single-source (visible in `components`).

## Governing rules

- **SCM-R6** — XUAR suppliers need clearance documentation regardless of this score.

## Related

- CPT-0069 GNN network risk — propagates risk through the supply graph.
- CPT-0068 NLP news monitoring — the event-driven early-warning companion.

## References

- ISO 31000 — risk management framework; Chopra & Meindl (2016), Ch. 6.
