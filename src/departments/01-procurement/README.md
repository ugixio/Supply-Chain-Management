# Department 01 — Procurement & Strategic Sourcing
## Procurement and Strategic Sourcing

### Mission
Ensure timely supply at the right quality and lowest total cost of ownership (TCO),
aligning purchasing decisions with the company's strategic objectives.

### Core Functions
| Function | Description |
|---------|-------------|
| Strategic sourcing | Supplier selection and qualification through competitive bids, RFQ/RFP |
| Tactical purchasing | Issuance and tracking of purchase orders (PO) |
| Contract management | Negotiation, administration, and renewal of framework contracts |
| Category management | Strategy by product family (Kraljic Matrix) |
| Spend analysis | Spend analytics, consolidation, and optimization |
| Supplier compliance | UFLPA, CSDDD, C-TPAT, ISO 28000 |

### Department KPIs
| KPI | Global Benchmark | Source |
|-----|------------------|--------|
| Purchase Order Cycle Time | < 3 days | APICS CPIM 9.0 |
| Procurement Cost Savings | ≥ 3-5% annual | Gartner SCM Top 25 |
| Supplier OTD | ≥ 95% | Chopra & Meindl Ch.14 |
| Contract Compliance Rate | ≥ 90% | CIPS Best Practice |
| Spend Under Management | ≥ 80% | McKinsey Procurement |
| PO Approval Lead Time | < 24 h (automatic) | Internal |

### Applicable Standards
- **ISO 20400:2017** — Sustainable procurement
- **US UCC Article 2** — Quantity in contracts
- **EU Directive 2014/24/EU** — Public procurement (reference)
- **Incoterms® 2020** — Delivery terms on each PO

### Order-to-PO Process
```
Need → Requisition → Supplier selection (Kraljic) →
RFQ/RFP → Quote evaluation → Negotiation → PO Draft →
Approval (workflow) → Supplier dispatch → Tracking → GRN
```

### Key Files
- `domain/PurchaseOrder.ts` — PO aggregate with approval workflow
- `domain/Supplier.ts` — Supplier master with Kraljic Matrix
- `domain/Contract.ts` — Framework contracts and supply agreements
- `domain/RFQ.ts` — Requests for quotation and quote evaluation
- `services/ApprovalWorkflow.ts` — Approval workflow engine
- `services/SpendAnalysis.ts` — Spend analysis and savings
- `config/thresholds.ts` — Approval thresholds by level

### Department Roles
- **CPO** (Chief Procurement Officer) — Strategy and governance
- **Category Manager** — Category strategy, Kraljic
- **Strategic Sourcing Manager** — Competitive bids and contracts
- **Buyer / Procurement Officer** — PO issuance and tracking
- **Contract Manager** — Contract drafting and administration
- **Procurement Analyst** — Spend analytics and reporting

### Academic and Professional References
- Chopra & Meindl, *Supply Chain Management* 6th Ed., Ch.14 "Sourcing Decisions"
- Kraljic, P. "Purchasing Must Become Supply Management" HBR (1983)
- CIPS (Chartered Institute of Procurement & Supply) — Professional standards
- APICS CPIM 9.0 — Plan Supply module

## Applied Mathematical Models

1. **Kraljic Matrix** — 2×2 segmentation: axes = Supply Risk (low/high) × Profit Impact (low/high). Quadrants: NON_CRITICAL, LEVERAGE, BOTTLENECK, STRATEGIC. Used to set negotiation strategy per supplier. Ref: Kraljic (1983), HBR "Purchasing Must Become Supply Management".

2. **RFQ Multi-Criteria Weighted Scoring** — Score_supplier = Σ(weight_i × normalized_score_i) where weights sum to 100%. Criteria: price, quality, delivery, sustainability. Used in `evaluateQuotes()`. Ref: Chopra & Meindl Ch.14.

3. **TCO — Total Cost of Ownership** — TCO = Purchase Price + Ordering Cost + Transport + Inspection + Risk Premium + Supplier Dev Cost. Used to compare suppliers beyond unit price. Ref: Ellram (1993).

4. **Price Escalation Formula** — Adjusted_Price = Base_Price × (1 + CPI_change × weight_material + PPI_change × weight_labor). Used in Contract.ts price escalation clause. Ref: APICS Dictionary.

5. **PO Approval Threshold Rule (SCM-R2)** — if PO_total ≥ PO_APPROVAL_THRESHOLD_CENTS (at or above) → status = PENDING_APPROVAL. Binary decision rule to enforce internal controls (SOX compliance).

## Recommended Machine Learning Models

1. **Random Forest for Supplier Classification** — Supervised classification. Features: historical OTD, PPM, financial stability score, country risk index, ESG score. Output: automatic Kraljic classification (STRATEGIC/LEVERAGE/BOTTLENECK/NON_CRITICAL). Libraries: scikit-learn, XGBoost. Ref: Breiman (2001).

2. **NLP / BERT for Contract Analysis** — Transformer-based NLP. Reads contract text, extracts key clauses (penalty terms, SLA, price escalation triggers), flags anomalies. Output: clause risk score per contract. Libraries: HuggingFace Transformers, spaCy. Ref: Devlin et al. (2018).

3. **Logistic Regression / XGBoost for PO Risk** — Binary classifier. Predicts probability that a PO will be delayed or rejected by supplier. Features: supplier history, item complexity, lead time, order size. Output: risk_score 0-1. Libraries: scikit-learn.

4. **K-Means Clustering for Spend Segmentation** — Unsupervised. Groups spend categories by volume, frequency, supplier concentration. Output: spend categories for strategic sourcing focus. Libraries: scikit-learn.

5. **Reinforcement Learning for Automated Negotiation** — Agent learns optimal bid/ask strategies in repeated procurement negotiations. Output: recommended counter-offer price. Libraries: Ray RLlib, Stable-Baselines3. Ref: Baarslag et al. (2017).
