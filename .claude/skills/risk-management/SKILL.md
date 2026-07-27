---
description: >
  Risk management domain expertise for Department 10. Use when reviewing risk matrices,
  HHI concentration, bullwhip effect, EAL (Expected Annual Loss), supply chain
  disruption models, or the concept nodes and rules of department 10 (risk-management).
---

# Risk Management — Department 10 Skills Reference

## Supply Chain Domain

**SCOR-DS Mapping**: Enable (E6 — Manage Supply Chain Risk)

**Risk Matrix (5×5) — ISO 31000:2018**
| | Very Low (1) | Low (2) | Medium (3) | High (4) | Very High (5) |
|--|-------------|---------|-----------|---------|--------------|
| **Very High (5)** | 5 | 10 | 15 | 20 | 25 |
| **High (4)** | 4 | 8 | 12 | 16 | 20 |
| **Medium (3)** | 3 | 6 | 9 | 12 | 15 |
| **Low (2)** | 2 | 4 | 6 | 8 | 10 |
| **Very Low (1)** | 1 | 2 | 3 | 4 | 5 |

Scoring: 1–5 = Low risk | 6–12 = Medium | 13–20 = High | 21–25 = Critical

**Risk Categories**
| Category | Examples | Mitigation |
|----------|---------|-----------|
| Supply | Single-source, XUAR, geopolitical | Dual-source, safety stock |
| Demand | Bullwhip, forecast error, black swan | Safety stock, flexible contracts |
| Operational | Equipment failure, cyber, fire | BCP, redundancy |
| Regulatory | CSDDD, UFLPA, REACH | Compliance program |
| Financial | FX, commodity price, supplier insolvency | Hedging, insurance |
| Reputational | ESG failures, product recall | Transparency, crisis plan |

**EAL — Expected Annual Loss**
```
EAL = Probability (annual) × Impact (USD)
Risk Priority = EAL × Controllability Score (inverse)
```

**HHI — Herfindahl-Hirschman Index** (DOJ/FTC 2010)
```
HHI = Σ(market_share_i²) × 10,000
HHI < 1,500: competitive | 1,500–2,500: moderate | > 2,500: highly concentrated
```

**Bullwhip Ratio** (Lee, Padmanabhan & Whang 1997)
```
Bullwhip Ratio = Var(Order Quantities) / Var(End-Customer Demand)
A ratio of 1 means demand variability passes through unamplified; above 1 the chain is
amplifying it. Where amplification becomes actionable is a project decision.
```

**KPIs (ISO 31000:2018; APICS)**
| KPI | Target | Formula |
|-----|--------|---------|
| Risk Coverage | 100% of critical risks | Risks assessed / Risks identified × 100 |
| Mitigation Effectiveness | ≥ 80% | Risks with implemented controls / Total high risks × 100 |
| Supply Chain Disruption Frequency | Track trend | Disruptions per year (count) |
| Single-Source Exposure | < 20% of critical SKUs | Single-source critical SKUs / Total critical SKUs × 100 |
| HHI by Category | < 2,500 | Σ(supplier_share²) × 10,000 |

## Data Analytics

**Risk Heat Map Query**
```sql
SELECT risk_id, risk_category, risk_description,
       probability_score, impact_score,
       probability_score * impact_score AS risk_score,
       CASE WHEN probability_score * impact_score >= 20 THEN 'CRITICAL'
            WHEN probability_score * impact_score >= 13 THEN 'HIGH'
            WHEN probability_score * impact_score >= 6  THEN 'MEDIUM'
            ELSE 'LOW' END AS risk_level,
       mitigation_status, risk_owner
FROM supply_chain_risks
ORDER BY risk_score DESC;
```

**HHI by Spend Category**
```sql
WITH category_spend AS (
  SELECT supplier_id, category_id,
         SUM(total_amount_cents) AS supplier_spend,
         SUM(SUM(total_amount_cents)) OVER (PARTITION BY category_id) AS category_total
  FROM po_lines WHERE status != 'CANCELLED'
  GROUP BY supplier_id, category_id
)
SELECT category_id,
       ROUND(SUM(POWER(supplier_spend::float / category_total, 2)) * 10000, 0) AS hhi,
       CASE WHEN SUM(POWER(supplier_spend::float / category_total, 2)) * 10000 > 2500 THEN 'CONCENTRATED'
            WHEN SUM(POWER(supplier_spend::float / category_total, 2)) * 10000 > 1500 THEN 'MODERATE'
            ELSE 'COMPETITIVE' END AS concentration_level
FROM category_spend GROUP BY category_id ORDER BY hhi DESC;
```

**Disruption Impact Simulation**
```sql
SELECT s.supplier_id, s.supplier_name,
       COUNT(DISTINCT pl.material_id) AS unique_materials_supplied,
       SUM(pl.open_qty * i.unit_cost_cents) / 100.0 AS at_risk_value_usd,
       MAX(i.safety_stock_days) AS max_safety_stock_days,
       MIN(i.safety_stock_days) AS min_safety_stock_days
FROM suppliers s
JOIN po_lines pl ON pl.supplier_id = s.supplier_id
JOIN inventory_items i ON i.sku_id = pl.material_id
WHERE pl.status = 'OPEN' AND s.is_sole_source = TRUE
GROUP BY s.supplier_id, s.supplier_name ORDER BY at_risk_value_usd DESC;
```

## Data Science

**Monte Carlo Supply Disruption Simulation**
```python
import numpy as np

def monte_carlo_supply_disruption(
    daily_demand_mean: float,
    daily_demand_std: float,
    lead_time_mean: float,
    lead_time_std: float,
    safety_stock: float,
    disruption_prob: float,
    disruption_duration_days: float,
    n_simulations: int = 10_000
) -> dict:
    """
    Monte Carlo simulation for supply disruption impact.
    Returns: stockout probability, expected lost sales, 95th percentile impact.
    Ref: Chopra & Meindl Ch.12; ISO 31000:2018 §6.5.2.
    """
    np.random.seed(42)
    stockouts = 0
    lost_sales = []
    for _ in range(n_simulations):
        demand = np.random.normal(daily_demand_mean, daily_demand_std)
        lead_time = max(1, np.random.normal(lead_time_mean, lead_time_std))
        disruption = np.random.random() < disruption_prob
        extra_days = disruption_duration_days if disruption else 0
        total_demand = demand * (lead_time + extra_days)
        available = safety_stock
        shortage = max(0, total_demand - available)
        if shortage > 0:
            stockouts += 1
            lost_sales.append(shortage)
        else:
            lost_sales.append(0)
    return {
        'stockout_probability': stockouts / n_simulations,
        'expected_lost_units': np.mean(lost_sales),
        'p95_lost_units': np.percentile(lost_sales, 95),
    }
```

## Machine Learning

**Supply Disruption Early Warning**
```python
from lightgbm import LGBMClassifier
import pandas as pd

def train_disruption_warning_model(df: pd.DataFrame) -> LGBMClassifier:
    """
    Predict supply disruption 30 days ahead.
    Features: supplier_financial_score, country_geopolitical_risk,
              port_congestion_index, commodity_price_volatility,
              weather_severity_index, lead_time_trend_30d, ncr_count_30d.
    Target: disruption_within_30d (bool).
    License: LightGBM MIT.
    """
    features = ['supplier_financial_score', 'country_geopolitical_risk',
                'port_congestion_index', 'commodity_price_volatility',
                'weather_severity_index', 'lead_time_trend_30d', 'ncr_count_30d']
    model = LGBMClassifier(n_estimators=300, learning_rate=0.03, class_weight='balanced')
    model.fit(df[features], df['disruption_within_30d'])
    return model
```

**Supply Network Graph Analysis**
```python
import networkx as nx
import pandas as pd

def analyze_supply_network(edges_df: pd.DataFrame) -> dict:
    """
    Graph analysis of supply network: centrality, single points of failure.
    edges_df: [source_supplier, target_buyer, material_id, spend_usd].
    Ref: Newman, M.E.J. (2010). Networks: An Introduction. Oxford.
    License: networkx BSD-3.
    """
    G = nx.DiGraph()
    for _, row in edges_df.iterrows():
        G.add_edge(row['source_supplier'], row['target_buyer'],
                   weight=row['spend_usd'], material=row['material_id'])
    betweenness = nx.betweenness_centrality(G, weight='weight')
    # High betweenness = single point of failure
    critical_nodes = {n: v for n, v in betweenness.items() if v > 0.3}
    hhi = sum(s**2 for s in
              [e['weight']/sum(d['weight'] for _,_,d in G.edges(data=True))
               for _,_,e in G.edges(data=True)]) * 10000
    return {'critical_suppliers': critical_nodes, 'network_hhi': hhi,
            'single_source_count': sum(1 for n in G.nodes if G.in_degree(n) == 1)}
```

## Python

| Library | Use | License |
|---------|-----|---------|
| `numpy` | Monte Carlo simulations | BSD-3 |
| `scipy.stats` | Risk distribution fitting | BSD-3 |
| `pandas` | Risk register DataFrames | BSD-3 |
| `networkx` | Supply network topology, HHI | BSD-3 |
| `lightgbm` | Disruption prediction | MIT |
| `simpy` | Discrete event risk simulation | MIT |
| `scikit-learn` | Clustering, anomaly detection | BSD-3 |

## TypeScript

**Domain Objects**
- `domain/RiskEvent.ts` — Risk register entry; probability; impact; EAL; mitigation status
- `models/BullwhipAnalysis.ts` — Order variance / demand variance; per-SKU ratio
- `models/HHICalculator.ts` — Supplier concentration; category-level HHI
- `services/RiskService.ts` — Risk scoring; heat map generation; early warning triggers

**EAL Calculation**
```typescript
function computeEAL(probabilityPerYear: number, impactCents: number): number {
  return probabilityPerYear * impactCents;  // result in cents
}

function computeBullwhipRatio(orderVariance: number, demandVariance: number): number {
  if (demandVariance === 0) throw new Error('Demand variance cannot be zero');
  return orderVariance / demandVariance;
}
```

## OSI / Commercial

| Tool | License | Use |
|------|---------|-----|
| PostgreSQL | PostgreSQL (OSI) | Risk register, EAL history |
| Apache Superset | Apache-2.0 | Risk heat map, HHI dashboard |
| `networkx` | BSD-3 | Supply network topology |
| `simpy` | MIT | Disruption scenario simulation |

**References**
- ISO 31000:2018 — Risk management — Guidelines
- Lee, H.L., Padmanabhan, V. & Whang, S. (1997). "The Bullwhip Effect in Supply Chains." *Sloan Management Review* 38(3).
- Chopra & Meindl, Ch.12 — Managing Uncertainty in a Supply Chain (Pearson, 2016)
- US DOJ/FTC Horizontal Merger Guidelines (2010) — HHI thresholds (1,500/2,500)
- APICS/ASCM Dictionary, 17th ed. (2024) — *risk management*, *supply chain disruption*, *bullwhip effect*
- Newman, M.E.J. (2010). *Networks: An Introduction.* Oxford University Press.
