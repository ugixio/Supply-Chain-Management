---
description: >
  Finance and controlling domain expertise for Department 11. Use when reviewing
  GL journal entries, inventory valuation (FIFO/WAC), landed cost, COGS, DIO,
  working capital, or the concept nodes and rules of department 11 (finance-controlling).
---

# Finance & Controlling — Department 11 Skills Reference

## Supply Chain Domain

**SCOR-DS Mapping**: Enable (E8 — Manage Supply Chain Finance)

**Inventory Valuation Methods** (IAS 2 / US GAAP ASC 330)
| Method | Standard | Formula | Use Case |
|--------|---------|---------|---------|
| FIFO | IAS 2 / ASC 330 | First unit in = first unit costed out | Most common; matches physical flow |
| WAC (Weighted Average Cost) | IAS 2 | New WAC = (OH value + Receipt value) / (OH qty + Receipt qty) | Stable commodity prices |
| LIFO | US GAAP only (ASC 330) | Last unit in = first out | US tax deferral; NOT allowed under IFRS |
| Standard Cost | IAS 2 / ASC 330 | Predetermined cost + variance | Manufacturing; variance analysis |

**Key Finance Metrics (APICS; Chopra & Meindl Ch.2)**
| KPI | World-Class | Formula |
|-----|------------|---------|
| Inventory Turnover | 8–12× (FMCG) | COGS / Avg Inventory (book value) |
| DIO (Days Inventory Outstanding) | < 45 days | (Avg Inventory / COGS) × 365 |
| DSO (Days Sales Outstanding) | < 30 days | (Avg AR / Revenue) × 365 |
| DPO (Days Payable Outstanding) | 30–60 days | (Avg AP / COGS) × 365 |
| Cash-to-Cash Cycle | Minimize | DIO + DSO − DPO |
| GMROI | > 2.0 | Gross Margin / Avg Inventory Cost |
| Inventory Carrying Cost | 20–30% per year | (Holding + Opportunity + Obsolescence) / Avg Inventory |

**Cash-to-Cash Cycle** (Chopra & Meindl, Ch.2)
```
C2C = DIO + DSO − DPO
Target: minimize; negative C2C = company receives cash before paying suppliers (e.g., Amazon, Dell)
```

**GL Journal Entries (all in integer cents)**
| Event | Debit | Credit |
|-------|-------|--------|
| Purchase receipt | Inventory (1310) | GR/IR Clearing (2101) |
| Invoice matching | GR/IR Clearing (2101) | Accounts Payable (2100) |
| Sales issue | COGS (5000) | Inventory (1310) |
| Inventory adjustment | Inventory (1310) or Variance (5100) | Variance (5100) or Inventory |
| Scrap | Scrap Expense (5200) | Inventory (1310) |

**Landed Cost Components**
```
Landed Cost = Unit Purchase Price + Freight + Insurance + Customs Duties + Port Fees + Brokerage
```
All in integer cents. Never float arithmetic.

## Data Analytics

**Cash-to-Cash Cycle Trend**
```sql
WITH inventory_metrics AS (
  SELECT DATE_TRUNC('month', period_date) AS period,
         AVG(inventory_value_cents) / 100.0 AS avg_inventory_usd,
         SUM(cogs_cents) / 100.0 AS monthly_cogs_usd
  FROM financial_snapshots GROUP BY period
),
ar_ap AS (
  SELECT DATE_TRUNC('month', transaction_date) AS period,
         AVG(ar_balance_cents) / 100.0 AS avg_ar_usd,
         AVG(ap_balance_cents) / 100.0 AS avg_ap_usd,
         SUM(revenue_cents) / 100.0 AS revenue_usd
  FROM gl_balances GROUP BY period
)
SELECT i.period,
       ROUND(i.avg_inventory_usd / NULLIF(i.monthly_cogs_usd * 12, 0) * 365, 1) AS dio,
       ROUND(a.avg_ar_usd / NULLIF(a.revenue_usd * 12, 0) * 365, 1) AS dso,
       ROUND(a.avg_ap_usd / NULLIF(i.monthly_cogs_usd * 12, 0) * 365, 1) AS dpo
FROM inventory_metrics i JOIN ar_ap a USING (period)
ORDER BY i.period;
```

**Inventory Write-Down Exposure**
```sql
SELECT abc_class, xyz_class,
       COUNT(*) AS sku_count,
       SUM(on_hand_qty * unit_cost_cents) / 100.0 AS book_value_usd,
       SUM(CASE WHEN last_movement_date < CURRENT_DATE - INTERVAL '180 days'
               THEN on_hand_qty * unit_cost_cents ELSE 0 END) / 100.0 AS potential_writedown_usd
FROM inventory_items i
JOIN stock_balances s ON s.sku_id = i.sku_id
GROUP BY abc_class, xyz_class ORDER BY potential_writedown_usd DESC;
```

## Data Science

**Inventory Carrying Cost Optimization**
- Components: capital cost (WACC × inventory value), storage cost, insurance, obsolescence, shrinkage
- Target: minimize total carrying cost subject to service level constraints
- Method: sensitivity analysis on reorder point and order quantity
- Trade-off: higher ROP → higher service level but higher holding cost

**Working Capital Forecasting**
- Input: demand forecast, PO schedule, payment terms
- Model: pro-forma cash flow; AR/AP/inventory projection
- Method: Excel/Python cash flow model with 13-week horizon
- Output: projected C2C, liquidity gap identification

## Machine Learning

**Inventory Obsolescence Prediction**
```python
from lightgbm import LGBMClassifier
import pandas as pd

def predict_obsolescence(df: pd.DataFrame) -> pd.DataFrame:
    """
    Predict probability that a SKU becomes obsolete within 12 months.
    Features: days_since_last_sale, abc_class_enc, xyz_class_enc,
              product_lifecycle_stage, demand_trend_slope_6m,
              substitution_flag, sku_age_days, on_hand_qty.
    Target: obsolete_within_12m (bool).
    License: LightGBM MIT.
    """
    features = ['days_since_last_sale', 'abc_class_enc', 'xyz_class_enc',
                'demand_trend_slope_6m', 'substitution_flag',
                'sku_age_days', 'on_hand_qty']
    model = LGBMClassifier(n_estimators=200, learning_rate=0.05, random_state=42)
    model.fit(df[features].dropna(), df.loc[df[features].notna().all(axis=1), 'obsolete_within_12m'])
    df['obsolescence_probability'] = model.predict_proba(df[features])[:, 1]
    return df
```

**GMROI Optimization**
```python
import pandas as pd
from scipy.optimize import minimize

def optimize_inventory_mix(skus_df: pd.DataFrame) -> pd.DataFrame:
    """
    Optimize inventory allocation to maximize portfolio GMROI.
    GMROI = Gross Margin $ / Average Inventory Investment $.
    Ref: Frazier (2010), Retail Merchandising. APICS CPIM §3.
    """
    def neg_portfolio_gmroi(alloc_fracs):
        gmrois = skus_df['gross_margin_cents'] / (alloc_fracs * skus_df['unit_cost_cents'])
        return -float((gmrois * alloc_fracs).sum() / alloc_fracs.sum())

    n = len(skus_df)
    x0 = [1.0/n] * n
    bounds = [(0.01, 1.0)] * n
    constraints = [{'type': 'eq', 'fun': lambda x: sum(x) - 1.0}]
    result = minimize(neg_portfolio_gmroi, x0, bounds=bounds, constraints=constraints)
    skus_df['optimal_allocation_fraction'] = result.x
    return skus_df
```

## Python

| Library | Use | License |
|---------|-----|---------|
| `pandas` | GL DataFrames, financial period analysis | BSD-3 |
| `numpy` | Inventory valuation, cost calculations | BSD-3 |
| `scipy.optimize` | Working capital optimization | BSD-3 |
| `lightgbm` | Obsolescence prediction | MIT |
| `statsmodels` | Cash flow trend regression | BSD-3 |
| `pulp` | LP for inventory cost minimization | MIT |

**WAC Update (Python)**
```python
def update_wac(current_qty: int, current_wac_cents: int,
               receipt_qty: int, receipt_unit_cost_cents: int) -> int:
    """
    Update Weighted Average Cost on each receipt.
    Returns: new WAC in integer cents.
    IMPORTANT: always integer cents — never float division without rounding.
    Ref: IAS 2 — Inventories.
    """
    total_value = current_qty * current_wac_cents + receipt_qty * receipt_unit_cost_cents
    total_qty = current_qty + receipt_qty
    if total_qty == 0:
        return 0
    return round(total_value / total_qty)  # always round to nearest cent
```

## TypeScript

**Domain Objects**
- `domain/JournalEntry.ts` — GL posting; debit/credit pairs; always balance to zero
- `domain/LandedCost.ts` — Landed cost components; duty rates; total in cents
- `domain/InventoryValuation.ts` — FIFO/WAC layer management; cost rollup
- `reports/FinancialReport.ts` — C2C, DIO, DSO, DPO, GMROI computation

**Money Rule (Critical)**
```typescript
// ALL monetary values in integer cents — never float
const inventoryValueCents: number = Math.round(unitCostCents * quantity);  // integer
const gmroi: number = Math.round((grossMarginCents / avgInventoryCents) * 100) / 100;  // ratio only
// Landed cost: sum of integer cent components
const landedCostCents = purchasePriceCents + freightCents + insuranceCents + dutiesCents + portFeesCents;
```

**Journal Entry Balance Validation**
```typescript
function validateJournalEntry(entry: JournalEntry): void {
  const totalDebits = entry.lines.filter(l => l.side === 'DEBIT').reduce((sum, l) => sum + l.amountCents, 0);
  const totalCredits = entry.lines.filter(l => l.side === 'CREDIT').reduce((sum, l) => sum + l.amountCents, 0);
  if (totalDebits !== totalCredits) {
    throw new AccountingError(`Journal entry ${entry.id} does not balance: DR ${totalDebits} ≠ CR ${totalCredits}`);
  }
}
```

## OSI / Commercial

| Tool | License | Use |
|------|---------|-----|
| PostgreSQL | PostgreSQL (OSI) | GL, financial snapshots, WAC history |
| Apache Superset | Apache-2.0 | C2C, DIO, GMROI dashboards |
| Apache Airflow | Apache-2.0 | Month-end close pipeline |
| `pulp` | MIT | Inventory cost LP optimization |

**References**
- IAS 2 — Inventories (IASB, 2003, revised 2023)
- US GAAP ASC 330 — Inventory (FASB)
- ASC 606 / IFRS 15 — Revenue from Contracts with Customers
- Chopra & Meindl, Ch.2 — Supply Chain Performance: Financial Metrics (Pearson, 2016)
- APICS/ASCM Dictionary, 17th ed. (2024) — *DIO*, *C2C*, *GMROI*, *carrying cost*, *landed cost*
- APICS CPIM 9.0 — Module 3: Inventory Management (financial metrics)
