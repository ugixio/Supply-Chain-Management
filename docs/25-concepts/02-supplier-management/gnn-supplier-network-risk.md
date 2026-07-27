---
id: concept-gnn-supplier-network-risk
title: "GNN Supplier Network Risk — GraphSAGE (CPT-0069)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-02-supplier-management }
  - { type: governed-by, target: index-adr }
---
# GNN Supplier Network Risk — GraphSAGE (CPT-0069)

> Scores every supplier's risk *including its upstream fragility*: a GraphSAGE network
> propagates node KPIs along material-flow edges so a healthy tier-1 with fragile
> tier-2s scores accordingly.

## Formula

GraphSAGE (mean aggregation) node classification. Node features:
`[OTD, PPM_score, lead_time_cv, single_source_flag, country_risk, UFLPA_exposure,
audit_score, revenue_share]`. Training (`train_gnn`): semi-supervised BCE on labelled
nodes, Adam (lr 5e-3, weight decay 1e-4), early stopping (patience 20), reports val AUC.
Scoring (`score_supplier_network`):

    risk_tier: ≥0.6 HIGH · ≥0.35 MEDIUM · else LOW
    upstream_exposure = fraction of direct upstream neighbours with score > 0.6
    combined_risk = 0.7·own_score + 0.3·upstream_exposure

## Inputs and outputs

- **Inputs:** `SupplierGraph` (node features N×8, directed `edge_index` 2×E,
  supplier→customer), binary labels (1 = high-risk, from audit/incident history) with
  train/val masks.
- **Outputs:** training curves + best epoch + val AUC; per-supplier
  `{risk_score, risk_tier, upstream_exposure, combined_risk}` ranked descending.

## Assumptions and limits

- Labels come from audits/incidents — scarce and lagging; semi-supervised setup exists
  precisely because most nodes are unlabelled. Validate AUC before trusting scores.
- GraphSAGE is **inductive**: new suppliers score without retraining — the reason it
  was chosen over GCN (transductive) per the module's design note; GAT is the upgrade
  path past ~500 nodes.
- Upstream exposure looks one tier up only; deeper cascades reach a node only through
  learned propagation, not the explicit exposure term.
- Small graphs overfit quickly (hence weight decay + early stopping); a fixed seed is
  not set in training — runs vary (recorded testing caveat).
- **Does not apply when:** the supply graph is unknown beyond tier-1 — feeding a
  tier-1-only star graph reduces this to a slower CPT-0065.

## Worked example

A tier-1 with strong own KPIs (raw score 0.2) but 3 of 4 upstream nodes above 0.6 →
`upstream_exposure = 0.75`, `combined = 0.7·0.2 + 0.3·0.75 = 0.365` → MEDIUM — invisible
to a per-supplier scorecard.

## Governing rules

- OSI-only (ADR-0002): PyTorch BSD-3; PyG optional (`torch-geometric` MIT).
- UFLPA exposure is a node feature — SCM-R6 documentation duties are unaffected by a
  low score.

## Related

- CPT-0065 Composite risk — the single-node baseline.
- HHI concentration (dept 10 catalogue) — the portfolio-level concentration measure.

## References

- Hamilton et al. (2017), *GraphSAGE*, NeurIPS; Kim & Rhee (2023), *EJOR*.
