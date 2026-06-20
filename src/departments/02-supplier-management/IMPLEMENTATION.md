# Supplier Management — Enterprise Implementation Playbook

## Executive Summary

Supplier management transforms transactional vendor relationships into a
structured, data-driven partnership model. For a €50 B multinational with
10,000+ active suppliers across 40 countries, a rigorous supplier management
function is the primary lever for quality, continuity, and cost performance.
World-class programmes deliver 15-25 % reduction in supplier-related quality
costs, 20-40 % improvement in OTD, and full CSDDD/UFLPA regulatory coverage.

This playbook covers every mathematical model, ML/AI pipeline, and operational
process in the `02-supplier-management` module — from initial scorecard design
through GraphSAGE network risk scoring in production.

Expected ROI: 12-18 month payback through quality cost reduction, avoided
supply disruptions (typically €2-15 M per avoided critical event), and
regulatory fine avoidance.

---

## Prerequisites & Dependencies

| Dependency | Detail |
|---|---|
| SAP S/4HANA / Ariba SLP | Vendor master, PO/GR/invoice history |
| Quality system data | NCR records, incoming inspection results |
| Logistics data | Delivery confirmations with actual vs. requested dates |
| Python ≥ 3.11 | GNN (PyTorch + torch-geometric), NLP (transformers) |
| Supplier master (MDM) | Cleaned, DUNS/GLN enriched, Tier-1 mapping complete |
| External data feeds | News API, sanctions lists, UFLPA entity list |
| Network topology | Tier-1 to Tier-2 mapping (at minimum strategic categories) |
| Historical scorecard data | ≥24 months for trend analysis and ML training |

---

## Phase 0: AS-IS Assessment (Weeks 1-8)

### 0.1 Supplier Portfolio Analysis
1. Extract full active supplier list from ERP; tag by category, spend tier, country.
2. Compute current OTD, OTIF, PPM per supplier using 12-month trailing data.
3. Identify suppliers with no performance data (data gap = high unmanaged risk).
4. Map Tier-1 suppliers to their critical sub-suppliers (Tier-2) for top 20 % spend.
5. Screen all suppliers against OFAC, EU, UN, UFLPA entity lists.

### 0.2 Scorecard Baseline
- Calculate current weighted scorecard for all active strategic/preferred suppliers.
- Identify suppliers in PROBATION or DISQUALIFIED territory (score <60).
- Document top 10 suppliers by risk exposure (spend × inverse scorecard).

### 0.3 KPI Baseline

| KPI | Typical Baseline | World-Class Target |
|---|---|---|
| Supplier OTD | 78 % | ≥95 % |
| OTIF | 71 % | ≥92 % |
| Incoming PPM | 3,200 | <500 (automotive) / <1,000 (general) |
| Scorecard coverage (% of spend) | 45 % | ≥90 % |
| Dual-source coverage (strategic) | 30 % | ≥80 % |
| Supplier-induced line stoppages | 8/year | 0 |
| Average scorecard rating | 68 | ≥80 |

---

## Phase 1: Foundation & Master Data (Weeks 9-20)

### 1.1 Supplier Segmentation
1. Apply Kraljic Matrix segmentation to all suppliers:
   - X-axis: supply risk (HHI + single-source + country risk + sub availability).
   - Y-axis: profit impact (% of COGS + margin criticality + substitutability).
   - Segment: STRATEGIC / LEVERAGE / BOTTLENECK / NON_CRITICAL.
2. Assign relationship manager per STRATEGIC and BOTTLENECK supplier.
3. Automate segmentation refresh quarterly using `assessKraljicSegment()` in
   `Supplier.ts`.

### 1.2 Scorecard Framework Design
Define the scoring formula per `src/departments/02-supplier-management/`:

```
Composite Score = 40 % × Delivery + 30 % × Quality + 20 % × Commercial + 10 % × Soft

Delivery sub-score  = 35 % × OTD_score + 45 % × OTIF_score + 20 % × RFT_score
Quality sub-score   = 60 % × PPM_score + 40 % × NCR_rate_score
Commercial sub-score = 70 % × Invoice_accuracy + 30 % × PO_variance_score
Soft sub-score      = manual assessment (responsiveness, innovation, sustainability)
```

Rating thresholds:
- PREFERRED:     ≥ 90
- APPROVED:      ≥ 75
- CONDITIONAL:   ≥ 60
- PROBATION:     ≥ 45
- DISQUALIFIED:  < 45

### 1.3 Data Collection Automation
1. Connect GR (goods receipt) timestamps to PO confirmed delivery date for OTD.
2. Pull NCR data from quality module (department 08).
3. Pull incoming inspection defect counts for PPM.
4. Pull invoice discrepancy data from AP module.
5. Automate monthly scorecard computation via Airflow DAG.

---

## Phase 2: Process Standardisation (Weeks 21-36)

### 2.1 Quarterly Business Reviews (QBR)
- Cadence: quarterly for STRATEGIC/BOTTLENECK; semi-annual for APPROVED.
- Agenda: scorecard review, issue log, development plan progress, forward outlook.
- Output: signed performance improvement plan (PIP) if score <75.

### 2.2 Supplier Onboarding Process
```
Registration (Ariba SLP) → Document collection (certs, bank, insurance) →
Sanctions screening → UFLPA risk assessment → Qualification audit (if strategic) →
Approved → Initial scorecard baseline set
```

### 2.3 Disqualification Process
1. Three consecutive months below PROBATION threshold (score <45) → escalation.
2. Supply continuity plan activated (dual source or safety stock build).
3. Formal disqualification letter + 90-day wind-down plan.
4. New supplier qualified in parallel before first supplier removed.

---

## Phase 3: Mathematical Models

### 3.1 Supplier Scorecard (Weighted Composite)

**Business problem**: objectively rank supplier performance on a consistent,
auditable scale for supplier development prioritisation and award decisions.

**Formulation**:
```
OTD_score  = (deliveries_on_time / total_deliveries) × 100
OTIF_score = (orders_on_time_and_in_full / total_orders) × 100
RFT_score  = (shipments_right_first_time / total_shipments) × 100

PPM        = (defective_units / total_units_received) × 1,000,000
PPM_score  = max(0, 100 - PPM / target_PPM × 100)
  e.g. target_PPM = 500 → PPM_score = max(0, 100 - actual_PPM/5)

NCR_rate   = NCR_count / total_receipts × 100
NCR_score  = max(0, 100 - NCR_rate × 10)

Invoice_accuracy = (invoices_matched_auto / total_invoices) × 100
PO_variance_score = max(0, 100 - avg_price_deviation_pct × 5)

Delivery  = 0.35 × OTD_score + 0.45 × OTIF_score + 0.20 × RFT_score
Quality   = 0.60 × PPM_score + 0.40 × NCR_score
Commercial = 0.70 × Invoice_accuracy + 0.30 × PO_variance_score
Soft      = manual_score (0-100)

Composite = 0.40 × Delivery + 0.30 × Quality + 0.20 × Commercial + 0.10 × Soft
```

**Implementation steps**:
1. Pull data from SAP S/4HANA: MM/LE for OTD/OTIF; QM for PPM/NCR; FI for invoices.
2. Compute sub-metrics for each supplier per calendar month.
3. Apply scoring formulas above; store results in scorecard table.
4. Compute trailing-12-month composite and trailing-3-month composite (trend).
5. Classify supplier rating per threshold table.
6. Trigger automated alerts: score drop >10 points month-on-month → email to SQE.
7. Generate PDF scorecard per supplier (quarterly distribution to supplier).
8. Store all scorecard versions immutably (soft-delete only).
9. Feed scorecard into Kraljic re-segmentation quarterly.
10. Use in ML early warning system (Phase 4).

**Worked example**:
```
Supplier ABC — Month of April:
  OTD = 48/50 = 96.0 %, OTIF = 45/50 = 90.0 %, RFT = 49/50 = 98.0 %
  Delivery = 0.35×96 + 0.45×90 + 0.20×98 = 33.6 + 40.5 + 19.6 = 93.7

  PPM = (3/2400)×1e6 = 1,250 → PPM_score = max(0, 100-1250/5) = max(0,-150) = 0
  NCR_rate = 2/50 = 4.0 % → NCR_score = max(0, 100-40) = 60
  Quality = 0.60×0 + 0.40×60 = 24.0

  Invoice_accuracy = 48/50 = 96.0 %, PO_variance = 1.2 % → PO_score = 94
  Commercial = 0.70×96 + 0.30×94 = 67.2 + 28.2 = 95.4

  Soft = 75 (analyst assessment)

  Composite = 0.40×93.7 + 0.30×24.0 + 0.20×95.4 + 0.10×75
             = 37.48 + 7.20 + 19.08 + 7.50 = 71.26 → APPROVED
  Action: quality development plan required (PPM far above target)
```

---

### 3.2 Herfindahl-Hirschman Index (HHI) for Concentration Risk

**Business problem**: measure supplier concentration risk per category to identify
single-source vulnerabilities.

**Formulation**:
```
For each supply category c:
  share_i = spend_i / total_category_spend    (for each supplier i in category c)
  HHI_c   = Σ (share_i × 100)²

Interpretation:
  HHI < 1,500     : competitive (low concentration risk)
  1,500 ≤ HHI < 2,500 : moderately concentrated
  HHI ≥ 2,500     : highly concentrated (dual-source strategy required)
  HHI = 10,000    : single source (critical risk — safety stock + backup qualification)
```

**Implementation steps**:
1. Aggregate spend by (category, supplier) for trailing 12 months.
2. Compute share and HHI per category.
3. Rank categories by HHI descending.
4. For all HHI ≥ 5,000: trigger dual-source action plan.
5. Track HHI trend quarterly; alert if any category crosses 5,000.
6. Link to supply planning module for safety stock uplift recommendations.
7. Report to CPO and CFO as supply risk KPI.

---

### 3.3 OTD / OTIF Calculation

**OTD (On-Time Delivery)**:
```
OTD = (shipments_delivered_on_or_before_confirmed_date / total_shipments) × 100

Confirmed date = supplier-acknowledged PO delivery date
Grace period   = ±0 days (automotive) or ±1 day (general industry)
```

**OTIF (On-Time In-Full)**:
```
OTIF = (orders_where_OTD=1 AND qty_received ≥ 0.98 × qty_ordered) / total_orders × 100

Note: Walmart/retail standard = 98 %; general industry = 92 %
```

**PPM**:
```
PPM = (total_defective_units_received / total_units_received) × 1,000,000

Automotive target: < 500 PPM
Food/pharma target: < 100 PPM
General manufacturing: < 3,000 PPM
```

---

### 3.4 Lead Time Coefficient of Variation

**Business problem**: quantify supplier delivery unpredictability to set safety
stock levels and flag unreliable suppliers.

**Formulation**:
```
μ_LT = mean(lead_time_observations)
σ_LT = std(lead_time_observations)
CV_LT = σ_LT / μ_LT

Classification:
  CV_LT < 0.10  : X — very reliable
  CV_LT 0.10-0.25: Y — moderate variability
  CV_LT > 0.25  : Z — high variability (flag for supplier development)
```

Feed CV_LT into Safety Stock Method 4 in the Inventory module.

---

## Phase 4: ML/AI Pipeline

### 4.1 GraphSAGE Supplier Network Risk (GNN)

**File**: `python/02_supplier_management/gnn_risk.py`
**Business problem**: propagate risk signals through the multi-tier supply network
so that a Tier-1 supplier's risk score reflects its own KPIs AND its upstream
Tier-2/3 fragility.

**Architecture**: 2-layer GraphSAGE (Hamilton et al. 2017); inductive — scores
new suppliers without full retraining.

**Node features** (8 dimensions per supplier):
```
[OTD, PPM_score, lead_time_CV, single_source_flag,
 country_risk_index, UFLPA_exposure_score, audit_score, revenue_share]
```

**Edge features** (3 dimensions per flow):
```
[spend_fraction, volume_CV, substitutability_score]
```

**Training data requirements**:
- Minimum 200 labelled nodes (1 = high-risk, 0 = normal).
- Labels from audit findings, supply incidents, financial distress events.
- Graph topology: Tier-1 → OEM edges at minimum; Tier-2 → Tier-1 preferred.

**Training steps** (using `train_gnn()` in gnn_risk.py):
1. Build `SupplierGraph` dataclass from supplier master + network topology table.
2. Normalise all 8 node features to [0,1] using train-set statistics.
3. Create `train_mask` (labelled nodes, 80 %) and `val_mask` (20 %).
4. Instantiate `SupplierRiskGNN(n_node_features=8, hidden_size=64, dropout=0.2)`.
5. Call `train_gnn(model, graph, labels, train_mask, val_mask, epochs=200, lr=5e-3)`.
6. Early stopping patience=20 epochs; restore best val-loss checkpoint.
7. Evaluate val AUC-ROC — target ≥ 0.80.
8. Save model weights to `models/gnn_supplier_risk_vYYYYMM.pt`.
9. Run `score_supplier_network()` monthly; output `combined_risk` score per node.
10. Flag suppliers with `combined_risk ≥ 0.6` as HIGH risk → SQE investigation.

**Deployment**:
- Monthly batch job (Airflow); results written to supplier master table.
- Dashboard: top-20 highest combined_risk suppliers with upstream_exposure detail.
- Alert: any Tier-1 supplier risk score increases >0.15 in one month → email CPO.

**Monitoring**:
- Monthly: compare model HIGH/LOW classifications to known incidents (precision).
- Quarterly: retrain if AUC drops below 0.75 or supplier network changes >20 %.

---

### 4.2 NLP Supplier Risk from News (DistilBERT)

**File**: `python/02_supplier_management/nlp_risk.py`
**Business problem**: detect early warning signals from supplier news (financial
distress, regulatory violations, geopolitical exposure) before they appear in
scorecard data.

**Architecture**: `distilbert-base-uncased` fine-tuned for multi-label risk
classification. Labels: `{financial_distress, labour_violation, environmental,
geopolitical, operational_disruption}`.

**Training data**:
- 8,000+ news articles and press releases about suppliers, labelled by analysts.
- Balance classes; augment minority classes with paraphrase.

**Training steps**:
1. Tokenise with `DistilBertTokenizerFast(max_length=256, truncation=True)`.
2. Fine-tune for 5 epochs: `lr=2e-5, batch_size=16, weight_decay=0.01`.
3. Multi-label sigmoid output; threshold=0.45 per label.
4. Evaluate: target AUC-ROC ≥ 0.82 per label on held-out test set.
5. Save model to `models/nlp_risk_distilbert_vYYYYMM/`.

**Deployment**:
1. Nightly job: fetch news via NewsAPI/RSS for all STRATEGIC + BOTTLENECK suppliers.
2. Score each article; aggregate max risk label per supplier per day.
3. Update `SupplierNewsRiskScore` in supplier master.
4. Risk score >0.7 on any label → alert relationship manager within 2 hours.
5. Feed news risk score as additional node feature into GNN (Phase 4.1).

---

### 4.3 Supplier Early Warning System (XGBoost)

**Business problem**: predict which suppliers will fall below APPROVED threshold
(score <75) within the next 3 months, enabling proactive development.

**Features** (per supplier, 3-month window):
- Scorecard trend (slope of last 6 months)
- OTD trend, PPM trend, NCR trend
- Country risk index (World Bank)
- Supplier financial health proxy (Dun & Bradstreet PAYDEX or similar)
- News risk score (from 4.2)
- Number of open corrective actions (CAPA)
- Days since last audit

**Training**:
1. Historical dataset: all suppliers with ≥12 months scorecard history.
2. Label: `deteriorated = 1` if score dropped below 75 within 3 months.
3. Split 70/15/15 train/val/test; stratify by supplier segment.
4. Train XGBoost binary classifier: `n_estimators=300, max_depth=6,
   learning_rate=0.05, scale_pos_weight=ratio_neg/ratio_pos`.
5. Tune via Optuna; target AUC-ROC ≥ 0.78.
6. Monthly inference: rank all active suppliers by P(deteriorate in 90 days).
7. Top 10 % → proactive development plan initiated by SQE team.

---

### 4.4 UFLPA Exposure Classifier (BERT)

**Business problem**: classify suppliers by Xinjiang forced labour exposure risk
to ensure UFLPA compliance and avoid US Customs holds.

**Architecture**: `bert-base-uncased` fine-tuned for 3-class classification:
`{LOW, MEDIUM, HIGH}` exposure.

**Features**: supplier description, product categories, country of manufacture,
sub-supplier countries, certifications (or lack thereof).

**Training**: ~3,000 labelled supplier profiles (labelled by trade compliance team
using UFLPA entity list and known exposure indicators).

**Deployment**:
- Run on every new supplier during onboarding.
- Quarterly re-screen existing supplier base.
- HIGH classification → mandatory `clearanceDocumentRef` before any PO can be
  raised (enforced in `Supplier.ts` business rule).
- MEDIUM → enhanced monitoring; request third-party audit within 6 months.

---

## Phase 5: Integration & Automation (Weeks 37-52)

### 5.1 SAP S/4HANA Integration
- Pull PO/GR data from MM module via BAPI/OData API daily.
- Push scorecard results back to vendor master (custom InfoRecord extension).
- NCR data from SAP QM QN (Quality Notification) via RFC.

### 5.2 Ariba Supplier Lifecycle & Performance (SLP)
- Supplier self-service: update certifications, banking, contacts.
- Automated qualification workflow: document collection → approval → activation.
- Performance scorecards published to supplier portal quarterly.

### 5.3 EDI Integration
- UN/EDIFACT DESADV (Despatch Advice) for real-time shipment notifications.
- ASN (Advanced Shipment Notice) mapped to GR to compute actual OTD.

---

## Phase 6: Continuous Improvement & CoE

- **Monthly**: automated scorecard refresh; early warning alerts actioned.
- **Quarterly**: QBR with STRATEGIC/BOTTLENECK suppliers; GNN model inference.
- **Annually**: Kraljic re-segmentation; full supplier base UFLPA re-screen.
- **CoE roles**: Supplier Quality Engineers (SQE), Supplier Development Engineers,
  Data Analyst (scorecard & ML), Category Manager liaison.
- **GNN retrain**: semi-annually or when network topology changes >20 %.
- **NLP models**: retrain quarterly with new labelled news articles.

---

## Technology Stack

| Layer | Technology |
|---|---|
| ERP | SAP S/4HANA (MM, QM, FI) |
| Supplier portal | SAP Ariba SLP |
| GNN | PyTorch 2.x + torch-geometric |
| NLP | HuggingFace transformers (DistilBERT, BERT) |
| ML | XGBoost, scikit-learn |
| Graph analytics | networkx (HHI, cascade analysis) |
| Data warehouse | Snowflake |
| Orchestration | Apache Airflow |
| Monitoring | MLflow + Grafana |

---

## KPIs & Success Metrics

| KPI | Baseline | 18-Month Target | Measurement |
|---|---|---|---|
| Supplier OTD | 78 % | ≥95 % | Monthly scorecard |
| OTIF | 71 % | ≥92 % | Monthly scorecard |
| Incoming PPM | 3,200 | <800 | QM inspection data |
| Scorecard coverage (% spend) | 45 % | ≥90 % | Scorecard report |
| Early warning detection rate | 0 % | ≥70 % of deteriorations flagged 90d early | Model tracking |
| GNN AUC-ROC | N/A | ≥0.80 | MLflow |
| HHI >5,000 categories | 12 | ≤3 | Quarterly review |
| Supplier-induced stoppages | 8/yr | 0 | Incident log |

---

## Risk & Mitigation

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Incomplete Tier-2 mapping | High | High | Start with top 50 strategic; expand iteratively |
| GNN training data scarce | Medium | High | Active labelling programme; transfer learning |
| Supplier resistance to transparency | Medium | Medium | Frame as partnership; share scorecard draft before publish |
| Model drift (GNN) | Low | Medium | Quarterly validation vs. known incidents |
| UFLPA false positives | Low | High | Human review for all HIGH classifications |

---

## Implementation Timeline

| Phase | Weeks | Key Deliverables | Owner |
|---|---|---|---|
| 0: Assessment | 1-8 | Portfolio analysis, KPI baseline, Tier-2 mapping start | SQE Lead |
| 1: Foundation | 9-20 | Scorecard framework live, segmentation, data feeds | IT + SQE |
| 2: Standardisation | 21-36 | QBR cadence, SOPs, Ariba SLP live | Supplier Mgmt |
| 3: Math models | 21-36 | Automated scorecard, HHI, OTD/OTIF/PPM live | Analytics |
| 4: ML pipeline | 37-52 | GNN, NLP, early warning, UFLPA classifier | Data Science |
| 5: Integration | 37-52 | SAP/Ariba/EDI integration | IT |
| 6: CoE | 53+ | CoE operational, continuous improvement | CoE Lead |

---

## References

- Hamilton et al., "Inductive Representation Learning on Large Graphs" (NeurIPS 2017)
- Kim & Rhee, "Proactive Supply Chain Risk Assessment with GNN" (EJOR 2023)
- Chopra & Meindl, *Supply Chain Management* 6th Ed., Ch. 13 (Pearson, 2016)
- CIPS, *Supplier Relationship Management* Guide (2022)
- US Pub.L. 117-78 (UFLPA); EU Directive 2024/1760 (CSDDD)
- Monczka et al., *Purchasing and Supply Chain Management* 7th Ed. (Cengage, 2020)
- ISO 28000:2022 — Supply chain security management systems
