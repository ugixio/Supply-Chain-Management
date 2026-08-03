---
description: >
  Order management domain expertise for Department 13. Use when reviewing customer
  orders, order entry accuracy (SCOR RL.2.3), projected order intake, Holt-Winters
  demand forecast, backlog identity, book-to-bill, or the concept nodes and rules of department 13 (order-management).
---

# Order Management — Department 13 Skills Reference

## Supply Chain Domain

**SCOR-DS Mapping**: Deliver (D1.1–D1.5); RL.1.1 Perfect Order Fulfillment

**Perfect Order Fulfillment** (SCOR-DS RL.1.1)
```
POF = RL.2.1 (Delivery In Full) ∩ RL.2.2 (Delivery On Time)
    ∩ RL.2.3 (Documentation Accuracy) ∩ RL.2.4 (Perfect Condition)
```

**Order Entry Accuracy** (SCOR-DS RL.2.3 leading indicator)
```
OEA = Orders entered without post-entry amendment / Total orders entered × 100
```

**First-Pass Field-Match Order Entry Accuracy** (8 controlled fields)
```
FP-OEA = Open order lines where all 8 fields match PO of record AND zero pre-confirmation
          changes in CDHDR/CDPOS / Total open order lines entered × 100
```
8 Controlled Fields: Sold-to ID, Ship-to ID, Material ID, Quantity, UoM, Net Price, Required Delivery Date, Customer PO Reference

**SAP SD Tables**
| Table | Content |
|-------|---------|
| VBAK | Sales order header (Sold-to, PO ref, order date) |
| VBAP | Sales order line items (Material, qty, NETWR = net value) |
| CDHDR/CDPOS | Change documents — pre-confirmation corrections |
| VBUP | Delivery and billing status per line |
| KNA1 | Customer master (Sold-to → Ship-to mapping) |

**Projected Order Intake** (APICS/ASCM Dict. 17th ed.; Chopra & Meindl Ch.7)
```
Projected Intake = Open Order Value (firm backlog) + ŷₜ₊ₕ × avg_net_price − backlog_due_to_ship
```

**Backlog Identity** (audit control — must hold every period)
```
Ending Backlog = Beginning Backlog + Order Intake − Shipments
```

**Book-to-Bill Ratio** (APICS; semiconductor / capital goods standard)
```
Book-to-Bill = Order Intake / Shipments
> 1.0: demand growing; < 1.0: orders declining; = 1.0: steady state
```

**Order metrics (SCOR-DS RL.1.1, RL.2.3; APICS CPIM)**

**Metrics — definitions, not levels.** A skill states what a metric measures and what
constrains the answer; the level a project must clear is that project's decision (ADR-0037,
and the inclusion test in `CLAUDE.md`). The right-hand column names the constraint so the
question can be asked properly, and stops.

| Metric | Formula / source | What constrains the level |
|---|---|---|
| Order entry accuracy | SCOR RL.2.3, formula above | **SCOR fixes the measure**; the level is the project's, and it depends on the channel — an EDI feed and manual entry are different processes measured the same way, not one process with two targets. |
| First-pass field match | FP-OEA over the 8 fields | Which fields are in scope. Change the field set and the metric is no longer comparable with its own history. |
| Perfect order fulfilment | SCOR RL.1.1 | **The arithmetic is the constraint worth knowing:** it is the *product* of the component rates, so four rates of 99% give 96%, not 99%. The level itself is a service commitment. |
| Order cycle time | Order confirmed → shipped | The fulfilment model and the channel promise. A make-to-order cycle and a from-stock cycle are not comparable (CPT-0060). |
| Backlog accuracy | The backlog identity holds to the cent | **Not a target — an identity.** It either holds or the ledger is wrong (SCM-R14 for the exact arithmetic that makes it checkable). |
| Book-to-bill | Intake / Shipments | Nothing external. A ratio above 1 means the backlog is growing; whether that is good depends on capacity. |

## Data Analytics

**First-Pass Field-Match SQL (Open Orders)**
```sql
WITH controlled AS (
  SELECT
    l.order_id, l.order_line_id, l.channel,
    (l.sold_to_id IS NOT DISTINCT FROM p.sold_to_id)::int          AS m_sold_to,
    (l.ship_to_id IS NOT DISTINCT FROM p.ship_to_id)::int          AS m_ship_to,
    (l.material_id IS NOT DISTINCT FROM p.material_id)::int        AS m_material,
    (l.ordered_qty IS NOT DISTINCT FROM p.ordered_qty)::int        AS m_qty,
    (l.unit_of_measure IS NOT DISTINCT FROM p.unit_of_measure)::int AS m_uom,
    (ROUND(l.net_price_cents::numeric, 0)
      IS NOT DISTINCT FROM ROUND(p.agreed_price_cents::numeric, 0))::int AS m_price,
    (l.requested_delivery_date IS NOT DISTINCT FROM p.requested_delivery_date)::int AS m_reqdate,
    (l.customer_po_ref IS NOT DISTINCT FROM p.customer_po_ref)::int AS m_po_ref,
    COALESCE(c.preconf_change_count, 0) AS preconf_changes
  FROM fact_order_line l
  JOIN ref_customer_po p ON p.order_id = l.order_id AND p.line_id = l.order_line_id
  LEFT JOIN (
    SELECT objectid AS order_line_id,
           COUNT(*) AS preconf_change_count
    FROM cdpos WHERE tabname = 'VBAP' AND udate <= l.confirmation_date
    GROUP BY objectid
  ) c ON c.order_line_id = l.order_line_id::text
  WHERE l.order_status NOT IN ('DELIVERED_COMPLETE','INVOICED','CLOSED','CANCELLED','REJECTED')
    AND l.open_quantity > 0
)
SELECT channel,
       COUNT(*) AS open_lines_entered,
       SUM(CASE WHEN (m_sold_to+m_ship_to+m_material+m_qty+m_uom+m_price+m_reqdate+m_po_ref) = 8
                 AND preconf_changes = 0 THEN 1 ELSE 0 END) AS first_pass_correct,
       ROUND(SUM(CASE WHEN (m_sold_to+m_ship_to+m_material+m_qty+m_uom+m_price+m_reqdate+m_po_ref) = 8
                       AND preconf_changes = 0 THEN 1 ELSE 0 END)::numeric
             / NULLIF(COUNT(*), 0) * 100, 3) AS first_pass_accuracy_pct
FROM controlled GROUP BY channel;
```

**Backlog Identity Audit**
```sql
SELECT period,
       beginning_backlog_cents,
       order_intake_cents,
       shipments_cents,
       ending_backlog_cents,
       (beginning_backlog_cents + order_intake_cents - shipments_cents) AS computed_ending,
       ending_backlog_cents - (beginning_backlog_cents + order_intake_cents - shipments_cents) AS discrepancy_cents
FROM backlog_snapshots
ORDER BY period;
-- discrepancy_cents MUST be zero; any non-zero value = data error
```

**Projected Order Intake SQL**
```sql
SELECT period,
       SUM(vbap_netwr_cents) AS firm_backlog_cents,
       ROUND(SUM(forecast_units * avg_net_price_cents)) AS forecast_value_cents,
       SUM(vbap_netwr_cents) + ROUND(SUM(forecast_units * avg_net_price_cents))
         - SUM(backlog_due_to_ship_cents) AS projected_intake_cents
FROM order_intake_view
WHERE period BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '6 months'
GROUP BY period ORDER BY period;
```

## Data Science

**Holt-Winters for Order Intake Forecasting**
- Level:    ℓₜ = α(yₜ − sₜ₋ₘ) + (1−α)(ℓₜ₋₁ + bₜ₋₁)
- Trend:    bₜ = β(ℓₜ − ℓₜ₋₁) + (1−β)bₜ₋₁
- Seasonal: sₜ = γ(yₜ − ℓₜ₋₁ − bₜ₋₁) + (1−γ)sₜ₋ₘ
- Forecast: ŷₜ₊ₕ = ℓₜ + h·bₜ + sₜ₊ₕ₋ₘ
- Minimum history: 24 months (2 full seasons, m=12)
- Backtest: walk-forward holdout h=12. **Whether the result is deployable is the project's bar** —
  set it against the naive benchmark (is FVA positive?) rather than against an absolute MAPE,
  since achievable MAPE is a property of the demand, not of the method

**Order Intake Forecast with Backtesting**
```python
import pandas as pd
import numpy as np
from statsmodels.tsa.holtwinters import ExponentialSmoothing

def project_order_intake(ts_monthly: pd.Series, open_order_value_cents: int,
                          avg_price_cents: float, backlog_to_ship_cents: int,
                          horizon: int = 6) -> dict:
    """
    Projected Order Intake = firm backlog + Holt-Winters forecast × avg price − backlog to ship.
    Requires ≥ 24 months of order intake history.
    Ref: APICS/ASCM Dictionary, 17th ed. (2024); Chopra & Meindl Ch.7.
    """
    assert len(ts_monthly) >= 24, "Need at least 24 months of history"
    # Backtest
    ts_train, ts_test = ts_monthly.iloc[:-12], ts_monthly.iloc[-12:]
    bt_model = ExponentialSmoothing(ts_train, trend="add", seasonal="add", seasonal_periods=12).fit(optimized=True)
    bt_fc = bt_model.forecast(12)
    errors = ts_test.values - bt_fc.values
    mape = float(np.mean(np.abs(errors / np.where(ts_test.values != 0, ts_test.values, np.nan))) * 100)
    bias = float(np.mean(errors / np.where(ts_test.values != 0, ts_test.values, np.nan)) * 100)
    # Full fit
    final_model = ExponentialSmoothing(ts_monthly, trend="add", seasonal="add", seasonal_periods=12).fit(optimized=True)
    fc_units = final_model.forecast(horizon)
    fc_value_cents = fc_units * avg_price_cents
    projected_intake = open_order_value_cents + int(fc_value_cents.sum()) - backlog_to_ship_cents
    return {
        'forecast_units': fc_units.tolist(),
        'projected_intake_cents': projected_intake,
        'backtest_mape': round(mape, 2),
        'backtest_bias': round(bias, 2),
        'deployable': mape < 15.0 and abs(bias) < 2.0
    }
```

## Machine Learning

**Order Delay Prediction**
```python
from lightgbm import LGBMClassifier
import pandas as pd

def predict_order_delay(df: pd.DataFrame) -> pd.DataFrame:
    """
    Predict probability that a customer order will be delayed at entry time.
    Features: customer_id_enc, channel_enc, order_value_cents, sku_count,
              avg_sku_lead_time_days, has_backordered_sku, season_enc,
              supplier_otd_30d, carrier_otd_30d.
    Target: delayed (bool) — actual ship date > committed date.
    """
    features = ['customer_id_enc', 'channel_enc', 'order_value_cents', 'sku_count',
                'avg_sku_lead_time_days', 'has_backordered_sku',
                'supplier_otd_30d', 'carrier_otd_30d']
    model = LGBMClassifier(n_estimators=300, learning_rate=0.05, random_state=42)
    model.fit(df[features], df['delayed'])
    df['delay_probability'] = model.predict_proba(df[features])[:, 1]
    return df
```

## Python

| Library | Use | License |
|---------|-----|---------|
| `statsmodels` | Holt-Winters, backtesting, ETS | BSD-3 |
| `pandas` | Order DataFrames, backlog tracking | BSD-3 |
| `numpy` | Forecast metrics (MAPE, RMSE, Bias) | BSD-3 |
| `lightgbm` | Order delay prediction | MIT |
| `scipy.stats` | Confidence intervals for forecasts | BSD-3 |
| `statsforecast` | AutoARIMA, ETS at scale | Apache-2.0 |

## What an order-management implementation typically needs

*Shapes, not code — ADR-0037 deleted the reference implementation. A project builds these in
its own repository, with its own policy values and its own layout. The names below are the
responsibilities that need a home, not paths in this repository.*

- `CustomerOrder.ts` — Order aggregate; 8-field validation; status lifecycle
- `OrderLine.ts` — Line-level detail; open qty; NETWR (integer cents)
- `OrderManagementService.ts` — Order entry; FP-OEA check; backlog identity
- `IntakeProjectionService.ts` — Projected Order Intake; Holt-Winters call

**8-Field Entry Validation**
```typescript
interface OrderEntryCheck {
  soldToMatch: boolean;
  shipToMatch: boolean;
  materialMatch: boolean;
  quantityMatch: boolean;
  uomMatch: boolean;
  priceMatch: boolean;
  deliveryDateMatch: boolean;
  customerPoRefMatch: boolean;
}

function isFirstPassCorrect(check: OrderEntryCheck, preConfChanges: number): boolean {
  return Object.values(check).every(v => v === true) && preConfChanges === 0;
}
```

**Money Rule**
```typescript
// NETWR from SAP VBAP: always store as integer cents
const netValueCents: number = Math.round(saNetwr * 100);  // SAP amount × 100, rounded
```

## OSI / Commercial

| Tool | License | Use |
|------|---------|-----|
| PostgreSQL | PostgreSQL (OSI) | Order events, backlog snapshots |
| Apache Superset | Apache-2.0 | OEA, backlog, book-to-bill dashboards |
| Apache Airflow | Apache-2.0 | Daily order intake pipeline |
| `statsmodels` | BSD-3 | Holt-Winters order intake model |

**References**
- SCOR Digital Standard (ASCM, 2019) — RL.1.1 Perfect Order Fulfillment; RL.2.3 Documentation Accuracy
- APICS/ASCM Dictionary, 17th ed. (2024) — *order backlog*, *demand forecast*, *book-to-bill*
- Chopra & Meindl, Ch.7 — Demand Forecasting in a Supply Chain (Pearson, 2016)
- Hyndman, R.J. & Athanasopoulos, G. (2021). *Forecasting: Principles and Practice*, 3rd ed. OTexts.
- Winters, P.R. (1960). "Forecasting Sales by Exponentially Weighted Moving Averages." *Management Science* 6(3).
- ASC 606 / IFRS 15 — Revenue recognition; order backlog definition
