---
description: >
  S&OP / SIOP planning domain expertise for Department 12. Use when reviewing
  Sales & Operations Planning cycles, consensus forecast, demand-supply balancing,
  S&OP KPIs, demand signal quality, or any code in src/departments/12-sop-planning/.
---

# S&OP Planning — Department 12 Skills Reference

## Supply Chain Domain

**SCOR-DS Mapping**: Plan (P1 — Plan Supply Chain)

**S&OP 5-Step Monthly Cycle** (Wallace & Stahl 2008; Chopra & Meindl Ch.8)
| Step | Activity | Participants | Timing |
|------|---------|-------------|--------|
| 1. Data Gathering | Actual sales vs. plan; inventory; orders | Planning team | Week 1 |
| 2. Demand Review | Statistical forecast + commercial adjustments | Sales, Marketing, Demand Planning | Week 2 |
| 3. Supply Review | Capacity, materials, supplier constraints | Operations, Procurement, Logistics | Week 3 |
| 4. Pre-S&OP | Gap analysis; scenario options; recommendations | All functions | Week 4 Day 1 |
| 5. Executive S&OP | Decision on volume/mix; financial impact | ExCom | Week 4 Day 3 |

**IBP — Integrated Business Planning** (Gartner / Oliver Wight)
- Extension of S&OP: includes financial reconciliation, strategic alignment, product portfolio review
- Horizon: 18–36 months (vs. S&OP 3–18 months)
- Financial integration: P&L impact of demand/supply scenarios

**Key Outputs of S&OP**
- Consensus Demand Plan: unit & revenue by family/period
- Production Plan: output volumes by plant/line
- Inventory Plan: projected inventory vs. target
- Financial Reconciliation: P&L impact; revenue gap vs. budget

**KPIs (APICS CPIM 9.0; Wallace & Stahl)**
| KPI | Target | Formula |
|-----|--------|---------|
| Plan Accuracy (Family MAPE) | < 10% at family level | Σ\|Actual−Consensus\|/Actual × 100 |
| S&OP Meeting On-Time Rate | 100% | Meetings held on schedule / Planned × 100 |
| Demand Signal Quality (SCOR RL.2.3) | ≥ 97% | Correct demand signals / Total × 100 |
| Forecast Value Added (FVA) | Positive | MAPE(statistical) − MAPE(consensus) |
| Plan Horizon Coverage | 18+ months | Periods with approved plan / 18 × 100 |
| Schedule Adherence | ≥ 95% | Executed plan / Committed plan × 100 |
| Supply Constraint Fill | ≥ 98% | Demand filled from supply plan / Total demand × 100 |

**FVA — Forecast Value Added** (Gilliland 2010)
```
FVA = MAPE(naïve/statistical) − MAPE(process step output)
Positive FVA: step adds accuracy; Negative FVA: step hurts accuracy → remove or simplify
```

## Data Analytics

**S&OP Consensus vs. Actuals**
```sql
SELECT period, product_family_id,
       statistical_forecast AS stat_fcst,
       commercial_adjustment AS commercial_adj,
       statistical_forecast + commercial_adjustment AS consensus_fcst,
       actual_sales AS actuals,
       ROUND(ABS(actual_sales - (statistical_forecast + commercial_adjustment))
             / NULLIF(actual_sales, 0) * 100, 2) AS mape_pct,
       ROUND((statistical_forecast + commercial_adjustment - actual_sales)
             / NULLIF(actual_sales, 0) * 100, 2) AS bias_pct
FROM sop_consensus_plans
WHERE period BETWEEN CURRENT_DATE - INTERVAL '12 months' AND CURRENT_DATE
ORDER BY period, product_family_id;
```

**Supply-Demand Gap Analysis**
```sql
SELECT period, product_family_id,
       consensus_demand_units,
       confirmed_supply_units,
       confirmed_supply_units - consensus_demand_units AS gap_units,
       CASE WHEN confirmed_supply_units < consensus_demand_units THEN 'SUPPLY_SHORT'
            WHEN confirmed_supply_units > consensus_demand_units * 1.10 THEN 'OVERPLANNED'
            ELSE 'BALANCED' END AS plan_status
FROM sop_supply_demand_matrix
WHERE period BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '6 months'
ORDER BY ABS(confirmed_supply_units - consensus_demand_units) DESC;
```

**FVA Waterfall**
```sql
SELECT process_step,
       AVG(ABS(forecast_at_step - actual_demand) / NULLIF(actual_demand, 0) * 100) AS mape_at_step,
       LAG(AVG(ABS(forecast_at_step - actual_demand) / NULLIF(actual_demand, 0) * 100))
           OVER (ORDER BY step_sequence) -
           AVG(ABS(forecast_at_step - actual_demand) / NULLIF(actual_demand, 0) * 100) AS fva
FROM sop_forecast_waterfall
GROUP BY process_step, step_sequence ORDER BY step_sequence;
```

## Data Science

**Scenario Planning Framework**
- Base Case: statistical forecast (Holt-Winters) + committed orders
- Upside Scenario: +15% demand; capacity constraint check
- Downside Scenario: −20% demand; inventory risk assessment
- Black Swan: supply disruption (lose top supplier 60 days); EAL calculation

**Financial Reconciliation Model**
- Revenue projection: consensus units × ASP (average selling price)
- COGS projection: consensus units × standard cost
- Gross margin gap: actual vs. budget; root cause by family

## Machine Learning

**S&OP Automation — Demand Consensus**
```python
from statsforecast import StatsForecast
from statsforecast.models import ETS, AutoARIMA, HoltWinters

def generate_statistical_baseline(df_long: 'pd.DataFrame', horizon: int = 18) -> 'pd.DataFrame':
    """
    Generate statistical baseline for S&OP demand review using multiple models.
    Input: long-format DataFrame with columns [unique_id, ds, y].
    Output: forecast with model selection (lowest MAPE in backtest).
    Ref: Hyndman & Athanasopoulos, FPP3 §8; statsforecast Apache-2.0.
    """
    sf = StatsForecast(
        models=[HoltWinters(season_length=12, error_type='A'),
                ETS(season_length=12),
                AutoARIMA(season_length=12)],
        freq='MS', n_jobs=-1
    )
    sf.fit(df_long)
    return sf.predict(h=horizon, level=[80, 95])
```

**Constraint Detection (Capacity)**
```python
import pandas as pd
import numpy as np

def detect_capacity_constraints(demand_plan: pd.DataFrame,
                                 capacity_df: pd.DataFrame) -> pd.DataFrame:
    """
    Identify periods and work centers where demand plan exceeds capacity.
    Returns: constraint flags with severity (% overload).
    """
    merged = demand_plan.merge(capacity_df, on=['period', 'resource_id'])
    merged['overload_pct'] = np.where(
        merged['required_hours'] > merged['available_hours'],
        (merged['required_hours'] - merged['available_hours']) / merged['available_hours'] * 100,
        0
    )
    merged['constraint_flag'] = merged['overload_pct'] > 0
    return merged[['period', 'resource_id', 'required_hours', 'available_hours',
                    'overload_pct', 'constraint_flag']].sort_values('overload_pct', ascending=False)
```

## Python

| Library | Use | License |
|---------|-----|---------|
| `statsforecast` | ETS, ARIMA, Holt-Winters at scale | Apache-2.0 |
| `prophet` | Seasonal baseline with holidays | MIT |
| `pandas` | S&OP DataFrames, plan consolidation | BSD-3 |
| `numpy` | Gap analysis, scenario math | BSD-3 |
| `scipy.optimize` | Resource allocation LP | BSD-3 |
| `pulp` | Multi-period production LP | MIT |
| `statsmodels` | FVA trend, regression | BSD-3 |

## TypeScript

**Domain Objects**
- `domain/SOPCycle.ts` — S&OP monthly cycle; inputs/outputs; approval state
- `domain/ConsensusForecast.ts` — Statistical + commercial adjustment; FVA tracking
- `domain/SupplyPlanCommit.ts` — Committed supply by family/period
- `services/SOPService.ts` — Gap analysis; scenario generation; financial reconciliation

**FVA Computation**
```typescript
function computeFVA(statisticalMAPE: number, consensusMAPE: number): number {
  return statisticalMAPE - consensusMAPE;  // positive = adjustment added value
}

function isAdjustmentWorthwhile(fva: number, threshold: number = 1.0): boolean {
  return fva >= threshold;  // only keep adjustments that improve MAPE by ≥ 1pp
}
```

## OSI / Commercial

| Tool | License | Use |
|------|---------|-----|
| PostgreSQL | PostgreSQL (OSI) | S&OP plan history, FVA tracking |
| Apache Superset | Apache-2.0 | S&OP dashboards, scenario waterfall |
| Apache Airflow | Apache-2.0 | Monthly S&OP pipeline automation |
| `statsforecast` | Apache-2.0 | Scalable statistical baseline |

**References**
- Wallace, T.F. & Stahl, R.A. (2008). *Sales and Operations Planning*, 3rd ed.
- Chopra & Meindl, Ch.8 — Aggregate Planning in a Supply Chain (Pearson, 2016)
- Gilliland, M. (2010). *The Business Forecasting Deal.* Wiley.
- APICS/ASCM Dictionary, 17th ed. (2024) — *S&OP*, *IBP*, *consensus forecast*, *FVA*
- APICS CPIM 9.0 — Module 5: Master Planning of Resources
- Hyndman, R.J. & Athanasopoulos, G. (2021). *Forecasting: Principles and Practice*, 3rd ed.
