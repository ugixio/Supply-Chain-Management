---
description: >
  Supplier management domain expertise for Department 02. Use when reviewing supplier
  scorecards, OTD/OTIF/PPM/DPMO metrics, scorecard weighting, performance rating,
  or any code in src/departments/02-supplier-management/.
---

# Supplier Management — Department 02 Skills Reference

## Supply Chain Domain

**SCOR-DS Mapping**: Enable (E2 — Manage Supply Chain Performance)

**Scorecard Weighting (APICS CPIM / Chopra & Meindl Ch.14)**
```
40% Delivery  → OTD 35% + OTIF 45% + Right-First-Time 20%
30% Quality   → PPM score 60% + NCR rate 40%
20% Commercial→ Invoice accuracy 70% + PO price variance 30%
10% Soft      → Responsiveness, sustainability, compliance (manual)
```

**Rating Thresholds**
| Rating | Score | Action |
|--------|-------|--------|
| PREFERRED | ≥ 90 | Preferred source list; volume incentives |
| APPROVED | ≥ 75 | Standard source; annual review |
| CONDITIONAL | ≥ 60 | 90-day corrective action plan required |
| PROBATION | ≥ 45 | 30-day CAR; dual-source mandatory |
| DISQUALIFIED | < 45 | Remove from AVL; escalate to Procurement |

**KPIs (APICS, ISO 9001:2015 §8.4.1)**
| KPI | World-Class | Formula |
|-----|------------|---------|
| OTD | ≥ 95% | On-time deliveries / Total deliveries × 100 |
| OTIF | ≥ 98% (Walmart std.) | Deliveries on-time AND in-full / Total × 100 |
| PPM | < 500 (automotive) | Defective parts / Total parts × 1,000,000 |
| DPMO | < 3,400 (6σ) | Defects / (Units × Opportunities) × 1,000,000 |
| Fill Rate | ≥ 98% | Units delivered in full / Units ordered × 100 |

**Approved Vendor List (AVL) Governance**
- Annual qualification audit per ISO 9001:2015 §8.4.1
- Disqualification triggers: 3 consecutive CONDITIONAL ratings, any PROBATION rating + missed CAR
- Re-qualification: minimum 6-month performance period after corrective action

## Data Analytics

**Supplier Scorecard SQL**
```sql
WITH delivery AS (
  SELECT supplier_id,
         SUM(CASE WHEN actual_delivery_date <= promised_date THEN 1 ELSE 0 END)::float
           / NULLIF(COUNT(*), 0) * 100 AS otd_pct,
         SUM(CASE WHEN actual_delivery_date <= promised_date
                   AND received_qty >= ordered_qty THEN 1 ELSE 0 END)::float
           / NULLIF(COUNT(*), 0) * 100 AS otif_pct
  FROM supplier_deliveries
  WHERE delivery_date >= CURRENT_DATE - INTERVAL '12 months'
  GROUP BY supplier_id
),
quality AS (
  SELECT supplier_id,
         SUM(defective_units)::float / NULLIF(SUM(inspected_units), 0) * 1e6 AS ppm,
         COUNT(CASE WHEN ncr_raised THEN 1 END) AS ncr_count
  FROM incoming_inspections GROUP BY supplier_id
)
SELECT d.supplier_id,
       ROUND(0.40 * (d.otd_pct*0.35 + d.otif_pct*0.45 + 100*0.20)  -- delivery sub-score
           + 0.30 * GREATEST(0, 100 - q.ppm/10) * 0.60              -- PPM score
           + 0.30 * (100 - q.ncr_count) * 0.40, 2) AS composite_score
FROM delivery d JOIN quality q USING (supplier_id);
```

**Pareto on Supplier Defects**
```sql
SELECT supplier_id, defect_category,
       SUM(defective_units) AS total_defects,
       SUM(SUM(defective_units)) OVER () AS grand_total,
       ROUND(SUM(defective_units)::numeric /
             SUM(SUM(defective_units)) OVER () * 100, 2) AS pct,
       ROUND(SUM(SUM(defective_units)) OVER
             (ORDER BY SUM(defective_units) DESC) /
             SUM(SUM(defective_units)) OVER () * 100, 2) AS cumulative_pct
FROM incoming_inspections GROUP BY supplier_id, defect_category
ORDER BY total_defects DESC;
```

## Data Science

**Supplier Risk Scoring**
- Features: financial stability (Altman Z-score), geopolitical exposure (country risk),
  concentration ratio, UFLPA flag, certification currency
- Composite: weighted sum normalized 0–100; lower = higher risk
- Re-score quarterly or on trigger event (financial distress signal, news alert)

**Lead Time Variability Prediction**
- Input: 24-month delivery history per SKU-supplier pair
- Model: XGBoost regressor; features: order volume, season, commodity index, distance
- Target: expected lead time + prediction interval (P10/P50/P90)
- Use P90 for safety stock calculation (conservative mode)

## Machine Learning

**Supplier Churn / Disqualification Prediction**
```python
from lightgbm import LGBMClassifier
import pandas as pd

def train_supplier_risk_model(df: pd.DataFrame) -> LGBMClassifier:
    """
    Predict supplier disqualification risk (binary: 0=healthy, 1=at-risk).
    Features: rolling_otd_3m, rolling_ppm_3m, ncr_count_ytd, score_trend_6m,
              days_since_audit, financial_risk_flag, uflpa_flag.
    Ref: APICS CPIM 9.0 — Supplier Performance Management.
    License: LightGBM MIT.
    """
    features = ['rolling_otd_3m', 'rolling_ppm_3m', 'ncr_count_ytd',
                'score_trend_6m', 'days_since_audit', 'financial_risk_flag']
    X, y = df[features], df['disqualified_within_90d']
    model = LGBMClassifier(n_estimators=200, learning_rate=0.05, random_state=42)
    model.fit(X, y)
    return model
```

**Concentration Risk (HHI)**
```python
import networkx as nx
import numpy as np

def compute_hhi(spend_by_supplier: dict[str, float]) -> float:
    """
    Herfindahl-Hirschman Index for supplier concentration.
    HHI = Σ(market_share_i²) × 10000.
    HHI > 2500: highly concentrated (DOJ/FTC guideline).
    Ref: DOJ/FTC Horizontal Merger Guidelines (2010).
    """
    total = sum(spend_by_supplier.values())
    shares = [v / total for v in spend_by_supplier.values()]
    return sum(s**2 for s in shares) * 10000
```

## Python

| Library | Use | License |
|---------|-----|---------|
| `pandas` | Scorecard DataFrames, rolling KPI windows | BSD-3 |
| `scipy.stats` | Statistical significance of score trends | BSD-3 |
| `scikit-learn` | Clustering suppliers, anomaly detection | BSD-3 |
| `lightgbm` | Disqualification risk prediction | MIT |
| `networkx` | Supplier graph, concentration (HHI) | BSD-3 |
| `statsmodels` | OTD trend regression, Granger causality | BSD-3 |

**Rolling KPI Window**
```python
import pandas as pd

def rolling_supplier_kpi(df: pd.DataFrame, window: int = 13) -> pd.DataFrame:
    """
    Compute rolling 13-week OTD, OTIF, PPM per supplier.
    Input df columns: supplier_id, delivery_date, on_time, in_full, defective_units, inspected_units.
    """
    df = df.sort_values(['supplier_id', 'delivery_date'])
    g = df.groupby('supplier_id')
    df['rolling_otd'] = g['on_time'].transform(lambda x: x.rolling(window).mean() * 100)
    df['rolling_otif'] = g.apply(lambda x: (x['on_time'] & x['in_full'])
                                  .rolling(window).mean() * 100).reset_index(0, drop=True)
    df['rolling_ppm'] = (g['defective_units'].transform(lambda x: x.rolling(window).sum())
                         / g['inspected_units'].transform(lambda x: x.rolling(window).sum()) * 1e6)
    return df
```

## TypeScript

**Domain Objects**
- `SupplierScorecard.ts` — Composite score; sub-scores; `SupplierRating` enum
- `CorrectionActionReport.ts` — CAR lifecycle; due dates; closure verification
- `SupplierAudit.ts` — ISO 9001 §8.4.1 audit record; findings; re-audit schedule

**Score Computation**
```typescript
function computeCompositeScore(delivery: DeliveryScore, quality: QualityScore,
                                commercial: CommercialScore, soft: SoftScore): number {
  return (
    0.40 * (delivery.otd * 0.35 + delivery.otif * 0.45 + delivery.rft * 0.20) +
    0.30 * (quality.ppmScore * 0.60 + quality.ncrScore * 0.40) +
    0.20 * (commercial.invoiceAccuracy * 0.70 + commercial.poVarianceScore * 0.30) +
    0.10 * soft.manualScore
  );
}

function toRating(score: number): SupplierRating {
  if (score >= 90) return 'PREFERRED';
  if (score >= 75) return 'APPROVED';
  if (score >= 60) return 'CONDITIONAL';
  if (score >= 45) return 'PROBATION';
  return 'DISQUALIFIED';
}
```

## OSI / Commercial

| Tool | License | Use |
|------|---------|-----|
| PostgreSQL | PostgreSQL (OSI) | Scorecard history, KPI time-series |
| Apache Superset | Apache-2.0 | Supplier performance dashboards |
| OpenSearch | Apache-2.0 | Supplier document search |
| networkx | BSD-3 | Supplier dependency mapping |

**References**
- Chopra & Meindl, *Supply Chain Management* 6th Ed., Ch.14 (Pearson, 2016)
- ISO 9001:2015 §8.4 — Control of externally provided processes
- APICS/ASCM Dictionary, 17th ed. (2024) — *OTD*, *OTIF*, *PPM*, *DPMO*
- APICS CPIM 9.0 — Module 4: Supplier Performance Management
- Walmart OTIF Compliance Standards (2023)
- US DOJ/FTC Horizontal Merger Guidelines (2010) — HHI thresholds
