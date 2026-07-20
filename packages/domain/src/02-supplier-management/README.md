# Department 02 — Supplier Management & Development
## Supplier Management and Development

### Mission
Build and maintain a competitive, resilient, and sustainable supplier base
that maximizes delivered value by objectively measuring performance and developing
capabilities in strategic partners.

### Core Functions
| Function | Description |
|---------|-------------|
| Performance evaluation | OTD/OTIF/PPM/DPMO scorecards by period |
| Supplier development | Improvement programs and training |
| Supplier audits | ISO 9001, C-TPAT, AEO, CSDDD |
| Relationship management (SRM) | Quarterly Business Review sessions |
| Sustainability and ESG | Environmental and human rights due diligence |
| Supplier diversity | Inclusion programs (MBE/WBE) |

### Department KPIs
| KPI | Global Benchmark | Source |
|-----|------------------|--------|
| Supplier OTD | ≥ 95% | Industry standard |
| OTIF | ≥ 98% | Walmart standard |
| PPM (automotive) | < 500 | AIAG |
| PPM (food & bev.) | ≤ 1,000 | GFSI standard |
| Supplier Sustainability Score | ≥ 75/100 | Gartner ESG |
| Diversity Spend | ≥ 15% | McKinsey Diversity |
| Supplier Development ROI | ≥ 5:1 | CIPS research |

### Supplier Classification (Scorecard Rating)
| Rating | Score | Actions |
|--------|-------|---------|
| PREFERRED | ≥ 90 | Long-term agreements, VMI, joint innovation |
| APPROVED | 75–89 | Standard relationship, semi-annual review |
| CONDITIONAL | 60–74 | 90-day corrective action plan |
| PROBATION | 45–59 | Monthly review, dual sourcing activated |
| DISQUALIFIED | < 45 | Disqualification, immediate alternative search |

### Scorecard Weights
```
40% Delivery    → OTD (35%) + OTIF (45%) + RFT (20%)
30% Quality     → PPM score (60%) + NCR rate (40%)
20% Commercial  → Invoice accuracy (70%) + PO variance (30%)
10% Soft        → Responsiveness, cooperation, sustainability
```

### Key Files
- `domain/SupplierScorecard.ts` — KPI calculation and rating
- `domain/SupplierAudit.ts` — ISO/CSDDD/C-TPAT audit records
- `domain/CorrectiveAction.ts` — SCAR (Supplier Corrective Action Request)
- `domain/SupplierDevelopment.ts` — Improvement and training programs
- `services/ScorecardService.ts` — Periodic scorecard generation service
- `reports/` — Quarterly performance reports

### Department Roles
- **Supplier Relationship Manager (SRM)** — Strategic management of key accounts
- **Supplier Quality Engineer (SQE)** — Audits and SCAR
- **Supplier Development Specialist** — Improvement programs
- **ESG / Sustainability Analyst** — CSDDD, UFLPA, carbon

### References
- Chopra & Meindl Ch.14 — Sourcing and supplier relationships
- APICS CPIM 9.0 — Supplier performance management
- ISO 9001:2015 §9.1.3 — Analysis and evaluation
- EU CSDDD Art.26 — Monitoring effectiveness

## Applied Mathematical Models

1. **Weighted Supplier Scorecard** — Score = 0.40×Delivery + 0.30×Quality + 0.20×Commercial + 0.10×Soft. Delivery sub-score = 0.35×OTD + 0.45×OTIF + 0.20×RFT. Quality sub-score = 0.60×PPM_score + 0.40×NCR_rate_score. Ref: APICS CPIM.

2. **PPM (Parts Per Million)** — PPM = (Defective_Units / Total_Units_Inspected) × 1,000,000. Benchmark: <500 automotive (IATF 16949), <1000 food. Ref: ISO 9001:2015.

3. **DPMO (Defects Per Million Opportunities)** — DPMO = (Defects / (Units × Opportunities_per_unit)) × 1,000,000. Six Sigma target: DPMO < 3.4 (6σ). Ref: Montgomery, *Introduction to Statistical Quality Control*.

4. **OTD Rate** — OTD = (Orders_delivered_on_time / Total_orders) × 100. World-class ≥95%. Ref: Chopra & Meindl Ch.3.

5. **Exponential Smoothing for Performance Trend** — Score_t = α×Score_actual + (1-α)×Score_{t-1}. Smooths supplier score over time to avoid over-reaction to single-period outliers. α=0.3 recommended.

## Recommended Machine Learning Models

1. **LSTM for Supplier Performance Prediction** — Time-series RNN. Input: 24 months of OTD/PPM/OTIF history per supplier. Output: predicted score next quarter. Flags suppliers trending toward PROBATION. Libraries: TensorFlow/Keras, PyTorch.

2. **Isolation Forest for Anomaly Detection** — Unsupervised anomaly detection. Detects sudden drops in quality or delivery metrics that may indicate supplier financial distress or capacity issues. Libraries: scikit-learn.

3. **Gradient Boosting (XGBoost) for Supplier Bankruptcy Risk** — Supervised classifier. Features: D&B score, payment days, PPM trend, order fill rate. Output: P(supplier_failure) in next 12 months. Libraries: XGBoost, LightGBM.

4. **Graph Neural Networks for Supplier Network** — Models supplier-tier relationships as a graph. Detects systemic risk (single-source Tier-2 supplier shared by multiple Tier-1). Output: supply chain concentration risk map. Libraries: PyTorch Geometric, DGL.

5. **NLP Sentiment Analysis for Supplier News** — Monitors news/ESG databases for negative signals (strikes, sanctions, disasters). Real-time risk alert. Libraries: HuggingFace, NewsAPI.
