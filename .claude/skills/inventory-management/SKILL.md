---
description: >
  Inventory management domain expertise for Department 05. Use when reviewing
  stock movements, ABC-XYZ classification, lot tracking, FEFO, event sourcing,
  negative inventory guards, or the concept nodes and rules of department 05 (inventory-management).
---

# Inventory Management — Department 05 Skills Reference

## Supply Chain Domain

**SCOR-DS Mapping**: Enable (E5 — Manage Inventory); Return (R1, R3)

**Movement Types (Event-Sourced)**
| Type | GL Debit | GL Credit |
|------|---------|---------|
| PURCHASE_RECEIPT | Inventory Asset | GR/IR Clearing |
| SALES_ISSUE | COGS | Inventory Asset |
| TRANSFER | Target Location | Source Location |
| PRODUCTION_ISSUE | WIP | Inventory Asset |
| PRODUCTION_RECEIPT | Inventory Asset | WIP |
| CYCLE_COUNT_ADJUSTMENT | Inventory / COGS | Variance Account |
| RETURN_FROM_CUSTOMER | Inventory Asset | Accounts Receivable |
| SCRAP | Scrap Expense | Inventory Asset |

**ABC Classification (Pareto)**
| Class | Share of items | Share of value | Control |
|-------|----------------|----------------|---------|
| A | smallest | largest | Tightest |
| B | middle | middle | Moderate |
| C | largest | smallest | Lightest |

The **ordering** is what Pareto fixes: few items carry most of the value. The cut points
(where A becomes B), the review cadence and the accuracy expectation per class are **project
decisions** — no percentage in this table is a standard.

**XYZ segmentation — the CV boundaries are the project's**

The classes are a standard idea; the cut-offs are not. CPT-0018 states the coefficient of
variation and names the boundaries as a project decision, because they depend on the history
length and the demand process — a short series inflates CV through its small denominator, and an
intermittent item can land in Z for a reason that is not volatility at all.

| Class | Meaning | Typical forecast policy |
|---|---|---|
| X | low variability, below the project's lower cut-off | statistical methods carry it (SES/Holt) |
| Y | between the two cut-offs | statistical plus commercial adjustment (consensus) |
| Z | above the upper cut-off | scenario planning; more buffer, and question the method |

Set the two cut-offs once, record them where the project's parameters live, and re-derive the
classification whenever the history window changes.

**Critical Business Rules**
1. **No negative inventory** without `backorderAllowed = true`
2. **All movements** generate a GL journal entry (debit/credit)
3. **Lot tracking** required for non-ambient storage or SVHC substances
4. **Soft-delete only** on stock movements — never hard-delete
5. **Idempotency** via `idempotencyKey` — safe to retry
6. **FEFO** (First Expired First Out) for lot-tracked items

**Inventory metrics (APICS CPIM 9.0; Ballou Ch.9)**

**Metrics — definitions, not levels.** A skill states what a metric measures and what
constrains the answer; the level a project must clear is that project's decision (ADR-0037,
and the inclusion test in `CLAUDE.md`). The right-hand column names the constraint so the
question can be asked properly, and stops.

| Metric | Formula | What constrains the level |
|---|---|---|
| Inventory turnover | COGS / Avg inventory | Industry and product class only (CPT-0016). |
| DIO | 365 / Turnover | As above; watch the annualization. |
| Inventory accuracy | Correct count locations / Total × 100 | **The count tolerance the project defines** — "correct" is not self-evident, and a ±1-each tolerance and an exact-match rule produce different accuracy from identical counts. Decide the tolerance before the target. |
| Shrinkage rate | (Book − Physical) / Book × 100 | The goods' own shrink exposure and the controls in place. High-value small items and bulk raw material are different problems. |
| Cycle-count coverage | A-items counted / Total A-items × 100 | The ABC classification (project-chosen boundaries, CPT-0018) and, where the goods are regulated, the traceability law. |
| Obsolescence rate | Slow/dead stock value / Total inventory value × 100 | The project's definition of "slow" and "dead" — this metric is mostly a restatement of that definition, so publish it alongside. |

## Data Analytics

**ABC-XYZ Matrix SQL**
```sql
WITH spend AS (
  SELECT sku_id,
         SUM(unit_cost_cents * quantity) AS annual_spend,
         SUM(SUM(unit_cost_cents * quantity)) OVER () AS total_spend
  FROM stock_movements WHERE movement_type = 'SALES_ISSUE'
    AND movement_date >= CURRENT_DATE - INTERVAL '12 months'
  GROUP BY sku_id
),
abc AS (
  SELECT sku_id,
         annual_spend,
         SUM(annual_spend) OVER (ORDER BY annual_spend DESC) / total_spend * 100 AS cum_pct,
         CASE WHEN SUM(annual_spend) OVER (ORDER BY annual_spend DESC)
                   / total_spend * 100 <= 80 THEN 'A'
              WHEN SUM(annual_spend) OVER (ORDER BY annual_spend DESC)
                   / total_spend * 100 <= 95 THEN 'B'
              ELSE 'C' END AS abc_class
  FROM spend
),
xyz AS (
  SELECT sku_id,
         STDDEV(demand) / NULLIF(AVG(demand), 0) AS cv,
         CASE WHEN STDDEV(demand)/NULLIF(AVG(demand),0) < 0.10 THEN 'X'
              WHEN STDDEV(demand)/NULLIF(AVG(demand),0) < 0.25 THEN 'Y'
              ELSE 'Z' END AS xyz_class
  FROM (SELECT sku_id, DATE_TRUNC('month', movement_date) AS period,
               SUM(quantity) AS demand
        FROM stock_movements WHERE movement_type = 'SALES_ISSUE'
        GROUP BY sku_id, period) m
  GROUP BY sku_id
)
SELECT a.sku_id, a.abc_class, x.xyz_class, a.abc_class || x.xyz_class AS matrix_cell
FROM abc a JOIN xyz x USING (sku_id);
```

**Inventory Accuracy by Location**
```sql
SELECT location_id, location_type,
       COUNT(*) AS total_locations,
       SUM(CASE WHEN ABS(book_qty - counted_qty) <= tolerance_qty THEN 1 ELSE 0 END) AS accurate,
       ROUND(SUM(CASE WHEN ABS(book_qty - counted_qty) <= tolerance_qty THEN 1 ELSE 0 END)
             ::float / COUNT(*) * 100, 2) AS accuracy_pct
FROM cycle_count_results
WHERE count_date >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY location_id, location_type;
```

## Data Science

**Dead Stock Identification**
- Dead stock: no movement in 180 days (configurable per category)
- Slow-moving: turns < 2× per year
- Cohort analysis: inflow date → last movement date → days since last touch
- Action: markdown pricing, redistribution, donation, write-off

**Inventory Optimization**
- Multi-echelon: base stock policy `S_i = d_i × L_i + z × σ_i × √L_i`
- Service level → z-score: 95% → 1.645; 98% → 2.054; 99% → 2.326
- Review period impact: `SS = z × σ_D × √(LT + R/2)` for periodic review

## Machine Learning

**Demand Forecast for Replenishment (scikit-learn pipeline)**
```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingRegressor
import pandas as pd

def build_replenishment_model(df: pd.DataFrame) -> Pipeline:
    """
    Predict weekly demand per SKU for replenishment trigger.
    Features: lag_1..4, rolling_mean_8, abc_class_enc, xyz_class_enc,
              month, week_of_year, promo_flag.
    Ref: Hastie, Tibshirani & Friedman — ESL, Ch.10 (Springer, 2009).
    License: scikit-learn BSD-3.
    """
    pipe = Pipeline([
        ('scaler', StandardScaler()),
        ('model', GradientBoostingRegressor(n_estimators=200, max_depth=4, random_state=42))
    ])
    feature_cols = [c for c in df.columns if c not in ('demand', 'sku_id', 'date')]
    pipe.fit(df[feature_cols], df['demand'])
    return pipe
```

**Anomaly Detection on Stock Movements**
```python
from sklearn.ensemble import IsolationForest
import pandas as pd

def flag_unusual_movements(df: pd.DataFrame) -> pd.DataFrame:
    """
    Flag unusual stock movements (theft, data entry errors, system glitches).
    Features: quantity, unit_cost_cents, time_since_last_movement, movement_type_enc.
    Contamination: 1% (expected fraud/error rate).
    """
    feats = ['quantity', 'unit_cost_cents', 'time_since_last_movement_hours']
    model = IsolationForest(contamination=0.01, random_state=42)
    df['anomaly'] = model.fit_predict(df[feats]) == -1
    return df
```

## Python

| Library | Use | License |
|---------|-----|---------|
| `pandas` | Stock movement DataFrames, ABC pivot | BSD-3 |
| `numpy` | Safety stock, EOQ, DIO calculations | BSD-3 |
| `scipy.stats` | Confidence intervals for SS | BSD-3 |
| `scikit-learn` | ABC clustering, anomaly detection | BSD-3 |
| `statsmodels` | Seasonal decomposition, trend analysis | BSD-3 |
| `simpy` | Inventory simulation (continuous review) | MIT |

**Safety Stock Calculation**
```python
import numpy as np
from scipy.stats import norm

def safety_stock_method4(sigma_demand: float, avg_demand: float,
                          sigma_lt: float, avg_lt: float,
                          service_level: float = 0.98) -> float:
    """
    Method 4 (most accurate): SS = z × √(LT×σ_D² + D̄²×σ_LT²).
    Accounts for both demand AND lead time variability.
    Ref: Chopra & Meindl Ch.11; Silver, Pyke & Peterson (1998).
    """
    z = norm.ppf(service_level)
    return z * np.sqrt(avg_lt * sigma_demand**2 + avg_demand**2 * sigma_lt**2)
```

## TypeScript

**Domain Objects**
- `domain/InventoryItem.ts` — Item master; ABC/XYZ; `storageCondition`; `reachSVHC`
- `domain/StockMovement.ts` — Movement aggregate; GL accounts; idempotency
- `domain/LotRecord.ts` — Lot master; expiry date; FEFO sort key
- `services/InventoryService.ts` — Balance projection; negative inventory guard

**Negative Inventory Guard**
```typescript
function applyMovement(item: InventoryItem, qty: number, type: MovementType): void {
  const newBalance = item.currentStockQty - (isOutbound(type) ? qty : -qty);
  if (newBalance < 0 && !item.backorderAllowed) {
    throw new InsufficientStockError(item.sku, qty, item.currentStockQty);
  }
  item.currentStockQty = newBalance;
}
```

**FEFO Lot Selection**
```typescript
function selectFefoLots(lots: LotRecord[], qtyNeeded: number): LotAllocation[] {
  const sorted = lots
    .filter(l => l.remainingQty > 0 && l.expiryDate > new Date())
    .sort((a, b) => a.expiryDate.getTime() - b.expiryDate.getTime());
  // allocate from soonest-to-expire first
  const allocations: LotAllocation[] = [];
  let remaining = qtyNeeded;
  for (const lot of sorted) {
    if (remaining <= 0) break;
    const take = Math.min(lot.remainingQty, remaining);
    allocations.push({ lotId: lot.id, qty: take });
    remaining -= take;
  }
  if (remaining > 0) throw new InsufficientStockError('FEFO', qtyNeeded, qtyNeeded - remaining);
  return allocations;
}
```

## OSI / Commercial

| Tool | License | Use |
|------|---------|-----|
| PostgreSQL | PostgreSQL (OSI) | Event store for stock movements |
| Apache Superset | Apache-2.0 | Inventory KPI dashboards |
| Apache Airflow | Apache-2.0 | Daily cycle count scheduling |
| `simpy` | MIT | Inventory policy simulation |

**References**
- Ballou, R.H., *Business Logistics/Supply Chain Management* 5th Ed., Ch.9 (Pearson, 2004)
- Chopra & Meindl, Ch.11 — Managing Uncertainty in a Supply Chain (Pearson, 2016)
- Silver, E.A., Pyke, D.F. & Peterson, R. (1998). *Inventory Management and Production Planning and Scheduling*, 3rd ed. Wiley.
- APICS/ASCM Dictionary, 17th ed. (2024) — *ABC analysis*, *cycle counting*, *FEFO*, *safety stock*
- APICS CPIM 9.0 — Module 3: Inventory Management
- GS1 General Specifications v23.0 — GTIN, lot/batch traceability
