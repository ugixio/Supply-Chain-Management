---
description: >
  Cross-department supply chain core expertise. Use when the task spans multiple
  departments, involves SCOR-DS mapping, shared KPIs, CQRS/Event Sourcing patterns,
  Money/UOM/Incoterms shared types, or global architecture decisions for this repo.
---

# Supply Chain Core — Cross-Department Skills Reference

## Supply Chain Domain

**SCOR Digital Standard (ASCM 2019) — Process Hierarchy**
| Level | Processes |
|-------|-----------|
| 1 — Strategic | Plan, Source, Make, Deliver, Return, Enable |
| 2 — Configuration | P1–P5, S1–S3, D1–D4, R1–R5, E1–E8 |
| 3 — Activity | D1.1 Process Inquiry, D1.2 Receive/Validate Order … |
| 4 — Implementation | Company-specific tasks |

**SCOR-DS → Department Mapping**
| SCOR | Department |
|------|-----------|
| Plan (P1–P5) | 03-demand-planning, 04-supply-planning, 12-sop-planning |
| Source (S1–S3) | 01-procurement |
| Deliver (D1–D4) | 07-logistics-transportation, 13-order-management |
| Return (R1–R5) | 05-inventory-management |
| Enable (E1–E8) | 02-supplier-management, 06-warehouse-management, 08-quality-management, 09-compliance-regulatory, 10-risk-management, 11-finance-controlling, 14-supplier-development |

**Shared Types (src/shared/types.ts)**
```typescript
// Money: always integer cents — NEVER float
type Money = { amount: number; currency: string };  // amount is integer cents

// Dates: ISO 8601 UTC
type ISOTimestamp = string;  // "2024-01-15T09:30:00Z"
type ISODate = string;       // "2024-01-15"

// UOM: GS1 codes
const UOM = { EA: 'EA', KG: 'KG', L: 'L', M: 'M', M2: 'M2', M3: 'M3', PCS: 'PCS' } as const;

// Incoterms 2020
const INCOTERMS_2020 = ['EXW','FCA','CPT','CIP','DAP','DPU','DDP','FAS','FOB','CFR','CIF'] as const;
```

**Architecture Patterns**
| Pattern | Use | Location |
|---------|-----|---------|
| Event Sourcing | Inventory movements, GL entries | `src/shared/EventStore.ts` |
| CQRS | Write: domain aggregates; Read: projections | All domain layers |
| Saga | Multi-step order fulfilment, returns | Saga-ready aggregates |
| DDD Bounded Contexts | Each department = one bounded context | `src/departments/` |
| Soft-Delete | `isDeleted: boolean` on all financial records | All domains |
| Idempotency | `idempotencyKey: string` on all mutations | Inventory, PO, Orders |

**Critical Business Rules (All Departments)**
1. Money: integer cents only — `Math.round(x * 100)`, never `parseFloat`
2. Dates: ISO 8601 UTC — `new Date().toISOString()`
3. No negative inventory without `backorderAllowed = true`
4. POs > `PO_APPROVAL_THRESHOLD_CENTS` ($5,000) → `PENDING_APPROVAL`
5. Soft-delete only — never `DELETE FROM` financial tables
6. All stock movements → GL journal entry (balanced debits = credits)
7. Lot tracking for non-AMBIENT storage or `reachSVHC = true`
8. UFLPA: `xuarOperations = true` requires `clearanceDocumentRef`
9. CSDDD: document retention ≥ 5 years from assessment date (Art. 23)
10. English-only: all code, comments, docs, commit messages

**World-Class KPI Benchmarks (cross-department)**
| KPI | World-Class | Standard |
|-----|------------|---------|
| OTIF | ≥ 98% | Walmart; APICS |
| OTD | ≥ 95% | APICS CPIM |
| Perfect Order Fulfillment | ≥ 95% | SCOR RL.1.1 |
| Forecast Accuracy (MAPE A-items) | < 15% | APICS CPIM |
| Inventory Accuracy | ≥ 99.5% | APICS |
| PPM (Automotive) | < 500 | IATF 16949 |
| Supplier Score PREFERRED | ≥ 90 | Dept 02 scorecard |
| Fill Rate | ≥ 98% | Chopra & Meindl |
| Bullwhip Ratio | ≈ 1.0 | Lee et al. 1997 |
| Cash-to-Cash Cycle | Minimize | Chopra & Meindl Ch.2 |

## Data Analytics

**Universal SQL Patterns**
```sql
-- Money: always work in cents; divide by 100 only for display
SELECT SUM(amount_cents) / 100.0 AS amount_usd FROM financial_table;

-- Soft-delete filter: always exclude deleted records
SELECT * FROM purchase_orders WHERE is_deleted = FALSE;

-- Idempotency check pattern
INSERT INTO orders (...) ON CONFLICT (idempotency_key) DO NOTHING RETURNING *;

-- Period comparison with proper null handling
ROUND(value / NULLIF(denominator, 0) * 100, 2) AS percentage;

-- Pareto / ABC running total
SUM(metric) OVER (ORDER BY metric DESC) / SUM(metric) OVER () * 100 AS cum_pct;
```

## Data Science

**Algorithm Selection Matrix**
| Task | Recommended Model | Library |
|------|-----------------|---------|
| Demand forecasting (trend+season) | Holt-Winters | `statsmodels` |
| Short-term demand sensing | LightGBM | `lightgbm` |
| Multi-SKU scale forecasting | AutoARIMA/ETS | `statsforecast` |
| Supplier risk scoring | LightGBM | `lightgbm` |
| Anomaly detection | Isolation Forest | `scikit-learn` |
| Route optimization | OR-Tools VRP | `ortools` |
| Supply scheduling | CP-SAT | `ortools` |
| Risk simulation | Monte Carlo | `numpy` |
| Network analysis (HHI) | Graph analysis | `networkx` |
| NLP (contracts, docs) | DistilBERT | `transformers` |
| Visual defect detection | YOLOv8 | `ultralytics` |
| Digital twin | DES | `simpy` |

## Machine Learning

**OSI Python Stack by Category**
```python
# Forecasting
from statsmodels.tsa.holtwinters import ExponentialSmoothing  # Holt-Winters
from statsforecast import StatsForecast  # ETS, AutoARIMA at scale (Apache-2.0)
from prophet import Prophet  # seasonality + holidays (MIT)

# ML — tabular
from lightgbm import LGBMClassifier, LGBMRegressor  # MIT
from xgboost import XGBClassifier, XGBRegressor  # Apache-2.0
from sklearn.ensemble import RandomForestClassifier, IsolationForest  # BSD-3

# Optimization
from ortools.constraint_solver import pywrapcp  # VRP (Apache-2.0)
from ortools.sat.python import cp_model  # scheduling (Apache-2.0)
from pulp import LpProblem, lpSum  # LP (MIT)

# RL
from stable_baselines3 import PPO, DQN  # MIT

# NLP
from transformers import pipeline  # Apache-2.0
import spacy  # MIT

# Graph
import networkx as nx  # BSD-3

# Simulation
import simpy  # MIT

# CV
from ultralytics import YOLO  # AGPL-3.0
import cv2  # Apache-2.0
```

**Standard Forecast Metrics**
```python
import numpy as np

def all_forecast_metrics(actuals: np.ndarray, forecasts: np.ndarray) -> dict:
    """
    Always compute all four metrics when evaluating a forecast model.
    Ref: Hyndman & Koehler (2006), IJF 22(4).
    """
    errors = actuals - forecasts
    mask = actuals != 0
    return {
        'mae':  float(np.mean(np.abs(errors))),
        'mape': float(np.mean(np.abs(errors[mask] / actuals[mask])) * 100),
        'rmse': float(np.sqrt(np.mean(errors**2))),
        'bias': float(np.mean(errors[mask] / actuals[mask]) * 100),
        'wmape': float(np.sum(np.abs(errors)) / np.sum(np.abs(actuals)) * 100),
    }
```

## Python

**Required Type Annotations**
```python
# Type hints mandatory on all public functions (CLAUDE.md requirement)
def compute_safety_stock(sigma_demand: float, avg_lead_time: float,
                          service_level: float = 0.98) -> float:
    """One-line docstring for public functions."""
    from scipy.stats import norm
    import numpy as np
    z = norm.ppf(service_level)
    return z * sigma_demand * np.sqrt(avg_lead_time)
```

**Python File Structure (python/ directory)**
```
python/
├── shared/           # common utilities, money helpers, logging
├── 01_procurement/
├── 02_supplier_management/
├── 03_demand_planning/
├── 04_supply_planning/
├── 05_inventory_management/
├── 06_warehouse_management/
├── 07_logistics_transportation/
├── 08_quality_management/
├── 09_compliance_regulatory/
├── 10_risk_management/
├── 11_finance_controlling/
├── 12_sop_planning/
├── 13_order_management/
└── 14_supplier_development/
```

**Testing (pytest)**
```python
import pytest
from python.shared.money import cents_to_usd, usd_to_cents

def test_money_no_float_errors():
    """Money operations must never lose cents to float rounding."""
    assert usd_to_cents(1.005) == 101  # round half-up
    assert usd_to_cents(0.994) == 99
    assert cents_to_usd(1234) == 12.34
```

## TypeScript

**Event Store Pattern**
```typescript
// All inventory mutations go through EventStore
interface DomainEvent<T> {
  id: string;
  aggregateId: string;
  aggregateType: string;
  type: string;
  payload: T;
  occurredAt: ISOTimestamp;
  idempotencyKey: string;
}

// Projection: current balance from event log
function projectStockBalance(events: StockMovementEvent[]): number {
  return events.reduce((balance, event) => {
    if (INBOUND_TYPES.includes(event.type)) return balance + event.payload.quantity;
    if (OUTBOUND_TYPES.includes(event.type)) return balance - event.payload.quantity;
    return balance;
  }, 0);
}
```

**Testing (Jest)**
```typescript
// Run: npm test | Unit only: npm run test:unit
describe('InventoryItem', () => {
  it('throws InsufficientStockError on negative balance when backorderAllowed is false', () => {
    const item = createInventoryItem({ backorderAllowed: false, currentStockQty: 10 });
    expect(() => applyMovement(item, 15, 'SALES_ISSUE')).toThrow(InsufficientStockError);
  });
});
```

## OSI / Commercial

**Complete OSI Stack**
| Layer | Tool | License |
|-------|------|---------|
| Runtime | Node.js (TypeScript) | MIT |
| Runtime | Python ≥ 3.11 | PSF |
| Database | PostgreSQL | PostgreSQL (OSI) |
| Message Bus | Apache Kafka | Apache-2.0 |
| Workflow | Apache Airflow | Apache-2.0 |
| BI | Apache Superset | Apache-2.0 |
| Search | OpenSearch | Apache-2.0 |
| Container | Docker | Apache-2.0 |
| Orchestration | Kubernetes | Apache-2.0 |
| ML Platform | MLflow | Apache-2.0 |
| Monitoring | Prometheus + Grafana | Apache-2.0 |

**Strictly Prohibited**
- ❌ AWS Textract → use `pytesseract` + `pdfplumber`
- ❌ Google Earth Engine → use `rasterio` + Copernicus open API
- ❌ AnyLogic → use `simpy`
- ❌ Neo4j v4+ (SSPL) → use `networkx` + `torch-geometric`
- ❌ Elasticsearch v7.11+ (SSPL) → use `opensearch-py`
- ❌ SageMaker → use local PyTorch / TensorFlow
- ❌ Power BI / DAX (commercial) → use Apache Superset
- ❌ Snowflake (commercial) → use PostgreSQL + DuckDB
- ❌ Tableau → use Apache Superset

**References**
- ASCM/APICS, *SCOR Digital Standard* (2019)
- APICS/ASCM Dictionary, 17th ed. (2024)
- APICS CPIM 9.0 — All modules
- Chopra & Meindl, *Supply Chain Management*, 6th Ed. (Pearson, 2016)
- Ballou, R.H., *Business Logistics/Supply Chain Management*, 5th Ed. (Pearson, 2004)
- Christopher, M., *Logistics and Supply Chain Management*, 6th Ed. (FT Publishing, 2022)
- ISO 28000:2022, ISO 9001:2015, ISO 2859-1:1999, ISO 31000:2018
- GS1 General Specifications v23.0
- ICC Incoterms® 2020
