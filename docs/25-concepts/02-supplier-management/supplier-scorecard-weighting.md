---
id: concept-supplier-scorecard-weighting
title: "Supplier Scorecard Weighted Scoring (CPT-0060)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-02-supplier-management }
  - { type: governed-by, target: index-adr }
---
# Supplier Scorecard Weighted Scoring (CPT-0060)

> The periodic supplier grade: delivery, quality and commercial performance blended
> with a manually assessed soft score into one 0–100 number.

## Formula

    delivery   = 0.35·OTD + 0.45·OTIF + 0.20·RFT                  (×100)
    quality    = 0.60·PPM_score + 0.40·NCR_score
    commercial = 0.70·invoice_accuracy + 0.30·PO_variance_score
    overall    = 0.40·delivery + 0.30·quality + 0.20·commercial + 0.10·soft

| Symbol | Meaning | Unit |
|---|---|---|
| OTD / OTIF / RFT | on-time, on-time-in-full, right-first-time rates | fraction (PY) / % (TS) |
| PPM_score | PPM inverted to 0–100 (see divergence) | score |
| NCR_score | PY: (1 − ncr_rate)·100; TS: % of deliveries without NCR | score |
| soft | manual assessment | 0–100 |

## Inputs and outputs

- **PY inputs:** rates as fractions 0–1 (`DeliveryMetrics`, `QualityMetrics`,
  `CommercialMetrics` dataclasses) + soft score 0–100. Each dimension clamps to [0,100],
  rounds 2 dp.
- **TS inputs (`calculateKPIs`):** raw counts (deliveries, defects, invoices, PO value);
  it derives the rates itself (zero denominators grade 100) and returns the full KPI
  record with rating attached.

## Assumptions and limits

- Weights are the repo's contractual standard (CLAUDE.md §Scorecard); change them only
  via decision, not per supplier.
- OTIF carries the largest delivery weight (0.45) — a supplier can hit 100% OTD and
  still score poorly by short-shipping.
- Zero-activity periods grade 100 in TS (`d === 0 → 100`) — no exposure reads as no
  failure; suppress scorecards for dormant suppliers instead of ranking them.
- **Does not apply when:** the period has unrepresentative volume (single-delivery
  periods swing the score; smooth with CPT-0062).

## Worked example (PY)

OTD 0.96, OTIF 0.92, RFT 0.98 → delivery = (0.336 + 0.414 + 0.196)·100 = 94.6.
PPM 400 → PPM_score = 100 − log₁₀(401)/log₁₀(10001)·100 ≈ 34.9; NCR rate 0.02 →
NCR_score 98 → quality = 0.60×34.9 + 0.40×98 = 60.2. Invoice accuracy 0.99, PO variance
0.03 → commercial = (0.693 + 0.291)·100 = 98.4. Soft 85 →
overall = 0.4·94.6 + 0.3·60.2 + 0.2·98.4 + 0.1·85 = **84.1** (APPROVED).

## Divergence (recorded)

- **PPM_score:** PY uses a log curve (500 PPM → ~32.5, hard floor at 10,000 PPM; note
  the code docstring claims "500 → ~85", which its own formula contradicts); TS uses
  linear `100 − ppm/100` (500 PPM → 95). The same defect rate produces very different
  quality scores per language.
- **PO variance:** TS multiplies variance% by 10 before inverting; PY expects a 0–1 rate.
- **TS `dpmo` = `ppm`** (1 opportunity/unit simplification).

## Governing rules

- **SUP-R*** (scorecard invariants) · **SCM-R3** — scorecards soft-delete only.

## Related

- CPT-0061 Rating classification — consumes the overall score.
- CPT-0051 PPM / CPT-0052 DPMO — the quality inputs.

## References

- APICS CPIM — supplier evaluation; Chopra & Meindl (2016), Ch. 15.
