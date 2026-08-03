---
description: >
  Procurement domain expertise for Department 01. Use when reviewing purchase orders,
  supplier contracts, RFQs, approval workflows, Kraljic matrix classification,
  spend analysis, or the concept nodes and rules of department 01 (procurement).
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

**Procurement metrics (APICS/ASCM Dictionary 17th ed., 2024)**

**Metrics — definitions, not levels.** A skill states what a metric measures and what
constrains the answer; the level a project must clear is that project's decision (ADR-0037,
and the inclusion test in `CLAUDE.md`). The right-hand column names the constraint so the
question can be asked properly, and stops.

| Metric | Formula | What constrains the level |
|---|---|---|
| PO cycle time | Date PO issued − Date PR raised | The approval chain the project designs. A short cycle and a strong control are in tension, and that trade-off is the decision this metric reports on. |
| PO accuracy rate | Correct POs / Total POs × 100 | What counts as an error — price, quantity, terms, ship-to — must be listed before a level means anything. |
| Supplier on-time delivery | On-time receipts / Total receipts × 100 | Which date counts (requested / confirmed / promised), then the supply agreement. |
| Spend under management | Managed spend / Total addressable × 100 | The project's own definition of *addressable*, which is where most of the variation lives. |
| Cost savings vs budget | (Budget price − Actual price) × Qty | The budget, which the project sets — so this metric partly measures the budget's realism. |
| PO approval threshold and levels | — | **The delegation of authority**, and for listed filers the SOX control environment. Named as a project decision in `SCM-R*` §Project decisions; an amount stated here would be inherited by every project that read it, which is exactly what happened before ADR-0037. |

**Kraljic Matrix** (Kraljic 1983, Harvard Business Review)
| | Low Supply Risk | High Supply Risk |
|--|----------------|-----------------|
| **High Profit Impact** | LEVERAGE — competitive bidding | STRATEGIC — long-term partnership |
| **Low Profit Impact** | NON_CRITICAL — automate/catalog | BOTTLENECK — safety stock, dual source |

**Approval workflow states — a project's vocabulary, not a standard.** A chain such as
`DRAFT → PENDING_APPROVAL → APPROVED → SENT → ACKNOWLEDGED → PARTIALLY_RECEIVED → RECEIVED → CLOSED`
is one reasonable design; nothing external fixes the names, the count or the transitions. What *is*
externally fixed is narrower: UCC Article 2 requires a stated quantity, and the three-way match
below must precede payment. Model the states the business actually has.

**Three-Way Match** (ISO 9001:2015 §8.4)
PO quantity + price = GR quantity = Supplier invoice → mandatory before AP payment

## Data Analytics

**Spend Analysis (Pareto / ABC)**
- Pareto behaviour is the *reason* to segment, not a figure to expect: spend concentration is
  empirical, and the actual split is what the analysis measures
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
- Silhouette score assesses cluster separation and the elbow method suggests k; neither has a
  universal cut-off — inspect the clusters, do not trust a number

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

## What a procurement implementation typically needs

*Shapes, not code — ADR-0037 deleted the reference implementation. A project builds these in
its own repository, with its own policy values and its own layout. The names below are the
responsibilities that need a home, not paths in this repository.*

- `PurchaseOrder.ts` — PO aggregate; `POStatus` union; approval workflow; three-way match
- `Supplier.ts` — Supplier master; `KraljicQuadrant`; certifications (ISO 28000, C-TPAT, AEO)
- `Contract.ts` — Framework agreements; price schedules; Incoterms 2020
- `RFQ.ts` — Request for Quotation; bid comparison; award logic

**Invariants worth carrying — and which of them this context may state**

Only the second is supply-chain law. The others are sound engineering or sound control design,
and a project adopts them for its own reasons:

- **Exact money, never floats** — **SCM-R14** and **ENG-R4/R5**. An amount is minor units with
  explicit quantization at defined boundaries, ties to even (IEEE 754-2019 §4.3.3). This one is
  fixed outside the repository and is stated as law.
- **Approval above a threshold** — the *existence* of an approval step, the amount and the state
  names are each the project's decision (the rule that once stated an amount here is retired,
  see `SCM-R*` §Retired rules). What survives is a warning: pin the boundary comparison with a
  test at the exact limit, because `>` and `>=` were confused here once already.
- **Preserve the audit trail rather than deleting** — a control design, and where records are
  retained by law the period is fixed (**SCM-R7**, ≥ 5 years under CSDDD). Soft-delete is one
  implementation of it, not the requirement.
- **Idempotent creation** — retry safety on the write path, an engineering concern (`ENG` family),
  not supply-chain law.

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

## Known pitfalls (wrong → right)

<!-- Fed by orchestrator corrections (docs/program/operating-model.md §4.7). Read before writing. -->

- **Boundary direction on any threshold.** Whether a limit means "above" (`>`) or "at or above"
  (`>=`) is part of the policy a project sets, and the order sized *exactly* to the limit is the
  one an approver most wants to see. State the comparison in the rule text, and pin it with a
  test at the boundary value — reading it the other way was a real defect here.
