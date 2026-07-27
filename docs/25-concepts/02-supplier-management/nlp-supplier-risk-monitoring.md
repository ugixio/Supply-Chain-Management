---
id: concept-nlp-supplier-risk-monitoring
title: "NLP Supplier Risk Monitoring — FinBERT + NER (CPT-0068)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-02-supplier-management }
  - { type: governed-by, target: index-adr }
---
# NLP Supplier Risk Monitoring — FinBERT + NER (CPT-0068)

> Early-warning pipeline over news text: FinBERT sentiment + entity extraction +
> rule-based risk categories are fused into a per-article signal and aggregated into a
> supplier alert level.

## Formula

Per article (`score_article`):

    base = {NEGATIVE: 0.5, NEUTRAL: 0.2, POSITIVE: 0.0}[sentiment]
    risk = min(1, base·confidence + Σ category_weights)
    weights: SANCTION 0.25 · GEOPOLITICAL 0.15 · FORCE_MAJEURE 0.10 ·
             LABOUR_DISRUPTION 0.08 · SHORTAGE 0.07 · QUALITY_RECALL 0.05

Per supplier (`monitor_supplier`), over the article window:

    alert = CRITICAL if avg_risk ≥ 0.70 ∨ neg_rate ≥ 0.80
          · HIGH ≥ 0.50/0.60 · MEDIUM ≥ 0.30/0.40 · else LOW

## Inputs and outputs

- **Pipeline symbols:** `load_finbert` (ProsusAI/finbert tokenizer+model),
  `analyse_article_batch` (batched sentiment `{label, score}`), `extract_entities`
  (spaCy ORG/GPE/PRODUCT/EVENT), `score_article`, `monitor_supplier`
  (aggregate → `SupplierRiskMonitor`), `quick_risk_scan` (rule-only fast pre-filter,
  no ML deps, priority by keyword count: ≥3 HIGH, ≥1 MEDIUM).
- Empty article list → LOW alert with zeroed metrics (no news ≠ good news — see limits).

## Assumptions and limits

- News coverage is biased toward large suppliers; a quiet small supplier can be riskier
  than a noisy large one — treat LOW-on-zero-articles as *unknown*, not safe.
- Category detection is keyword/regex-based: language drift and euphemism evade it;
  the FinBERT leg only reads *financial* tone (Araci 2019), not operational risk.
- Alert thresholds are heuristics "calibrated to minimize false positives" — recall is
  sacrificed; pair with CPT-0065's structural score rather than replacing it.
- Model weights download at first use; `quick_risk_scan` is the offline path.
- **Does not apply when:** text is non-English (models are English-tuned).

## Worked example

Article "Sanctions hit <supplier> smelter; force majeure declared" → NEGATIVE (0.93),
categories {SANCTION, FORCE_MAJEURE} → `risk = min(1, 0.5·0.93 + 0.25 + 0.10) = 0.815`.
Ten such articles, neg_rate 0.9 → **CRITICAL** alert.

## Governing rules

- OSI-only stack (ADR-0002): FinBERT Apache-2.0, spaCy MIT.
- Alerts are advisory; supplier status changes go through governed lifecycles.

## Related

- CPT-0065 Composite risk score — the structural counterpart this stream updates.
- CPT-0069 GNN network risk — propagates confirmed risk through the graph.

## References

- Araci (2019), *FinBERT*, arXiv:1908.10063; Malo et al. (2014), *JASIST*.
