---
description: >
  Procurement domain expertise for Department 01. Use when reviewing purchase orders,
  supplier contracts, RFQs, approval workflows, Kraljic matrix classification,
  spend analysis, or any procurement TypeScript code in src/departments/01-procurement/.
---

# Procurement — Department 01 Skills Reference

## Supply Chain Domain

**Core Standards & Frameworks**
- SCOR-DS Process: **Source** (S1 Make-to-Stock, S2 Make-to-Order, S3 Engineer-to-Order)
- ISO 28000:2022 — Supply chain security management
- UN/EDIFACT: ORDERS (850), ORDRSP, INVOIC, RECADV messages
- Incoterms® 2020 — 11 rules; DPU replaces DAT; EXW/FCA (seller's premises) vs DDP (delivered)
- US UCC Article 2 — quantity is mandatory in all purchase contracts
- C-TPAT (US CBP) and AEO (EU) security certifications

**Procurement KPIs (APICS/ASCM Dictionary 17th ed., 2024)**
| KPI | World-Class Target | Formula |
|-----|-------------------|---------|
| PO Cycle Time | < 3 days (e-procurement) | Date PO issued − Date PR raised |
| PO Accuracy Rate | ≥ 99% | Correct POs / Total POs × 100 |
| Supplier On-Time Delivery (OTD) | ≥ 95% | On-time receipts / Total receipts × 100 |
| Spend Under Management | ≥ 80% | Managed spend / Total addressable spend × 100 |
| Cost Savings vs. Budget | ≥ 3% annual | (Budget price − Actual price) × Qty |
| PO Approval Threshold | $5,000 (configurable) | `PO_APPROVAL_THRESHOLD_CENTS` constant |

**Kraljic Matrix** (Kraljic 1983, Harvard Business Review)
| | Low Supply Risk | High Supply Risk |
|--|----------------|-----------------|
| **High Profit Impact** | LEVERAGE — competitive bidding | STRATEGIC — long-term partnership |
| **Low Profit Impact** | NON_CRITICAL — automate/catalog | BOTTLENECK — safety stock, dual source |

**Approval Workflow States**
`DRAFT → PENDING_APPROVAL → APPROVED → SENT_TO_SUPPLIER → ACKNOWLEDGED → PARTIALLY_RECEIVED → FULLY_RECEIVED → CLOSED`

**Three-Way Match** (ISO 9001:2015 §8.4)
PO quantity + price = GR quantity = Supplier invoice → mandatory before AP payment

## Data Analytics

**Spend Analysis (Pareto / ABC)**
- 80/20 rule: top 20% of suppliers typically represent 80% of spend
- Segment by: category, supplier, geography, Kraljic quadrant
- Metrics: spend concentration index, price variance vs. market index, savings pipeline
- SQL pattern: window functions for running totals, rank by spend descending

**Procurement Dashboard KPIs**
```sql
-- PO approval cycle time by category
SELECT category,
       AVG(EXTRACT(EPOCH FROM (approved_at - created_at))/3600) AS avg_approval_hours,
       PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (approved_at - created_at))/3600) AS p90_hours
FROM purchase_orders
WHERE status = 'APPROVED'
GROUP BY category;
```

**Price Variance Analysis**
```sql
-- Actual vs. budget price by supplier
SELECT supplier_id,
       SUM((unit_price_cents - budget_price_cents) * quantity) / 100.0 AS variance_usd,
       ROUND(AVG((unit_price_cents - budget_price_cents)::float / NULLIF(budget_price_cents,0) * 100), 2) AS pct_variance
FROM po_line_items GROUP BY supplier_id ORDER BY variance_usd DESC;
```

## Data Science

**Demand-Driven Procurement**
- Link procurement triggers to demand forecast output from Dept 03
- Reorder Point (ROP) = Average Daily Demand × Lead Time + Safety Stock
- Dynamic safety stock recalculation when CV > 0.25 (XYZ = Y/Z items)

**Supplier Price Prediction**
- Features: commodity index (LME, CRB), lead time trend, order volume, exchange rate
- Model: LightGBM regression on 24-month price history; retrain quarterly
- Target: next-quarter unit price per SKU/supplier pair; use for budget setting

**Spend Clustering (Strategic Sourcing)**
- K-means on: annual spend, supplier count, criticality score, lead time variability
- Output: cluster assignment → Kraljic quadrant recommendation
- Silhouette score target > 0.4; elbow method for k selection

## Machine Learning

**Anomaly Detection on PO Data**
```python
from sklearn.ensemble import IsolationForest
import pandas as pd

def detect_po_anomalies(df: pd.DataFrame, contamination: float = 0.02) -> pd.DataFrame:
    """
    Detect anomalous purchase orders (price spikes, unusual quantities).
    Features: unit_price_cents, quantity, lead_time_days, supplier_risk_score.
    Ref: Liu et al. (2008) — Isolation Forest, ICDM.
    """
    features = ['unit_price_cents', 'quantity', 'lead_time_days', 'supplier_risk_score']
    X = df[features].fillna(df[features].median())
    model = IsolationForest(contamination=contamination, random_state=42)
    df['anomaly_score'] = model.fit_predict(X)
    df['is_anomalous'] = df['anomaly_score'] == -1
    return df
```

**Supplier Selection (Multi-Criteria)**
```python
from scipy.optimize import linprog
import numpy as np

def supplier_selection_lp(costs: np.ndarray, capacities: np.ndarray,
                          demand: float) -> np.ndarray:
    """
    Linear programming for optimal supplier allocation.
    Minimizes total cost subject to capacity and demand constraints.
    Ref: Weber et al. (1991), European Journal of Operational Research.
    """
    # costs: [cost_per_unit per supplier]; capacities: max units per supplier
    result = linprog(costs, A_ub=-np.eye(len(costs)), b_ub=-capacities,
                     A_eq=[np.ones(len(costs))], b_eq=[demand], bounds=[(0, None)]*len(costs))
    return result.x
```

**NLP for Contract Risk Extraction**
```python
from transformers import pipeline

def extract_contract_risks(contract_text: str) -> list[dict]:
    """
    Extract risk clauses from supplier contracts using NER.
    Identifies: penalty clauses, force majeure, delivery terms, IP ownership.
    Model: distilbert-base-uncased-finetuned (HuggingFace, Apache-2.0).
    """
    ner = pipeline("ner", model="distilbert-base-uncased", aggregation_strategy="simple")
    return ner(contract_text[:512])
```

## Python

**Key Libraries for Procurement**
| Library | Use | OSI License |
|---------|-----|-------------|
| `pandas` | Spend DataFrames, pivot tables, price history | BSD-3 |
| `scipy.optimize` | Supplier allocation LP, EOQ optimization | BSD-3 |
| `scikit-learn` | Anomaly detection, clustering (K-means) | BSD-3 |
| `lightgbm` | Price forecasting, supplier risk scoring | MIT |
| `pulp` | Multi-source LP (minimize cost, constraints) | MIT |
| `networkx` | Supplier dependency graph, HHI concentration | BSD-3 |
| `transformers` | Contract NLP, risk clause extraction | Apache-2.0 |
| `spacy` | Named entity recognition on PO documents | MIT |

**EOQ & ROP Calculation**
```python
import numpy as np

def eoq(annual_demand: float, ordering_cost: float, holding_cost: float) -> float:
    """EOQ — Harris (1913). Q* = sqrt(2DS/H)."""
    return np.sqrt(2 * annual_demand * ordering_cost / holding_cost)

def reorder_point(avg_daily_demand: float, lead_time_days: float,
                  safety_stock: float) -> float:
    """ROP = D̄ × LT + SS. Ref: Chopra & Meindl Ch.11."""
    return avg_daily_demand * lead_time_days + safety_stock
```

## TypeScript

**Domain Objects in `src/departments/01-procurement/`**
- `PurchaseOrder.ts` — PO aggregate; `POStatus` union; approval workflow; three-way match
- `Supplier.ts` — Supplier master; `KraljicQuadrant`; certifications (ISO 28000, C-TPAT, AEO)
- `Contract.ts` — Framework agreements; price schedules; Incoterms 2020
- `RFQ.ts` — Request for Quotation; bid comparison; award logic

**Critical Business Rules to Enforce**
```typescript
// Rule 1: PO above threshold requires approval
if (totalAmountCents > PO_APPROVAL_THRESHOLD_CENTS) {
  status = 'PENDING_APPROVAL';  // never auto-approve above threshold
}

// Rule 2: Money is always integer cents — never floats
const totalCents: number = Math.round(unitPriceCents * quantity);  // integer

// Rule 3: Soft-delete only — never hard-delete POs
po.isDeleted = true;  // preserve audit trail for AP reconciliation

// Rule 4: Idempotency on PO creation
if (await repo.findByIdempotencyKey(idempotencyKey)) return existing;
```

**PO Approval Event Pattern (CQRS)**
```typescript
type POEvent =
  | { type: 'PO_CREATED'; payload: POCreatedPayload }
  | { type: 'PO_APPROVED'; payload: { approvedBy: string; approvedAt: ISOTimestamp } }
  | { type: 'PO_SENT'; payload: { sentAt: ISOTimestamp; channel: 'EDI' | 'EMAIL' | 'PORTAL' } }
  | { type: 'GR_POSTED'; payload: GRPostedPayload };
```

## OSI / Commercial

**OSI-Compliant Tools for Procurement**
| Tool | License | Purpose |
|------|---------|---------|
| Apache OFBiz | Apache-2.0 | Open-source ERP with procurement module |
| Odoo Community | LGPL-3 | PO workflow, supplier management |
| PostgreSQL | PostgreSQL (OSI) | Relational DB for PO/supplier master |
| Apache Superset | Apache-2.0 | Spend analytics dashboards |
| Apache Airflow | Apache-2.0 | Procurement workflow orchestration |
| OpenSearch | Apache-2.0 | PO/contract full-text search |

**Prohibited in This Repository**
- ❌ SAP Ariba API (proprietary) → use EDI ORDERS/ORDRSP adapters
- ❌ Coupa (SaaS/proprietary) → use OFBiz or Odoo CE
- ❌ Salesforce CPQ → use custom RFQ domain object

**References**
- Chopra & Meindl, *Supply Chain Management* 6th Ed., Ch.14 (Pearson, 2016)
- Kraljic, P. (1983). "Purchasing Must Become Supply Management." *Harvard Business Review* 61(5), 109–117.
- Weber, C.A., Current, J.R., & Benton, W.C. (1991). "Vendor selection criteria and methods." *EJOR* 50(1), 2–18.
- APICS/ASCM Supply Chain Dictionary, 17th ed. (2024) — *purchase order*, *three-way match*, *spend analysis*
- ISO 28000:2022 — Security management systems for the supply chain
- UN/EDIFACT D.96A — ORDERS, ORDRSP, INVOIC message standards
