---
description: >
  Supplier development domain expertise for Department 14. Use when reviewing
  supplier capability building, audit programs, corrective action plans,
  dual-sourcing strategy, or the concept nodes and rules of department 14 (supplier-development).
---

# Supplier Development — Department 14 Skills Reference

## Supply Chain Domain

**SCOR-DS Mapping**: Enable (E2 — Manage Supply Chain Performance; E3 — Manage GRC)

**Supplier Development Continuum** (Monczka et al. 2015)
```
Disqualified → Probation → Conditional → Approved → Preferred → Strategic Partner
```

**Development Levers**
| Lever | Description | Target |
|-------|-------------|--------|
| Capability Audit | ISO 9001, process capability, capacity | Baseline score |
| Technical Assistance | On-site kaizen, tooling, SPC training | 20% quality improvement |
| Co-investment | Shared tooling, R&D, certification funding | Strategic suppliers |
| Joint KPIs | Shared OTD/PPM targets + gain sharing | Preferred suppliers |
| Dual Sourcing | Add 2nd source to reduce BOTK risk | < 20% single-source critical |
| Supplier Tiering | Tier classification + development roadmap | Quarterly review |

**Development Program KPIs**
| KPI | Target | Formula |
|-----|--------|---------|
| Supplier Score Improvement | ≥ 10 pts/year | Score end of year − Score start of year |
| CAR On-Time Closure | ≥ 95% in 30 days | CARs closed in 30d / Total CARs × 100 |
| Audit Coverage — Tier 1 | 100% annually | Audited Tier-1 / Total Tier-1 × 100 |
| Dual-Source Coverage | ≥ 80% critical items | Dual-sourced critical SKUs / Total critical × 100 |
| CSDDD Assessment — Tier 1 | 100% by 2027 | Assessed / Total Tier-1 × 100 |
| Development ROI | Track | (Score improvement × spend impact) / Development cost |

**Capability Maturity Levels** (adapted from CMMI)
| Level | Description | Typical Score |
|-------|-------------|--------------|
| 1 — Initial | Ad hoc; reactive | < 45 |
| 2 — Managed | Basic controls; documented processes | 45–59 |
| 3 — Defined | Standardized; SPC; ISO certified | 60–74 |
| 4 — Quantitatively Managed | Statistical control; Cpk ≥ 1.33 | 75–89 |
| 5 — Optimizing | Continuous improvement; co-innovation | ≥ 90 |

## Data Analytics

**Supplier Score Trend Analysis**
```sql
SELECT supplier_id,
       MIN(composite_score) FILTER (WHERE score_period = DATE_TRUNC('year', CURRENT_DATE)) AS score_start,
       MAX(composite_score) FILTER (WHERE score_period = DATE_TRUNC('year', CURRENT_DATE) + INTERVAL '11 months') AS score_end,
       MAX(composite_score) - MIN(composite_score) AS score_improvement,
       COUNT(DISTINCT score_period) AS periods_assessed
FROM supplier_scorecards
WHERE score_period >= DATE_TRUNC('year', CURRENT_DATE)
GROUP BY supplier_id
ORDER BY score_improvement DESC;
```

**CAR Closure Rate**
```sql
SELECT supplier_id,
       COUNT(*) AS total_cars,
       SUM(CASE WHEN closure_date IS NOT NULL
                 AND closure_date <= opened_date + INTERVAL '30 days' THEN 1 ELSE 0 END) AS on_time_closures,
       ROUND(SUM(CASE WHEN closure_date IS NOT NULL
                       AND closure_date <= opened_date + INTERVAL '30 days' THEN 1 ELSE 0 END)::float
             / NULLIF(COUNT(*), 0) * 100, 2) AS closure_rate_pct
FROM corrective_action_reports
WHERE opened_date >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY supplier_id ORDER BY closure_rate_pct ASC;  -- worst performers first
```

**Dual Source Coverage**
```sql
SELECT i.abc_class, i.xyz_class,
       COUNT(DISTINCT i.sku_id) AS total_skus,
       COUNT(DISTINCT CASE WHEN src.source_count >= 2 THEN i.sku_id END) AS dual_sourced,
       ROUND(COUNT(DISTINCT CASE WHEN src.source_count >= 2 THEN i.sku_id END)::float
             / NULLIF(COUNT(DISTINCT i.sku_id), 0) * 100, 2) AS dual_source_pct
FROM inventory_items i
JOIN (SELECT material_id, COUNT(DISTINCT supplier_id) AS source_count
      FROM approved_supplier_list GROUP BY material_id) src ON src.material_id = i.sku_id
WHERE i.abc_class = 'A'  -- focus on critical A-items
GROUP BY i.abc_class, i.xyz_class;
```

## Data Science

**Development Priority Matrix**
- X-axis: Supplier strategic importance (Kraljic score)
- Y-axis: Current performance gap (100 − composite_score)
- Quadrant 1 (High importance, high gap): Urgent development investment
- Quadrant 2 (High importance, low gap): Maintain and co-innovate
- Quadrant 3 (Low importance, high gap): Replace or exit
- Quadrant 4 (Low importance, low gap): Monitor only

**Development ROI Model**
```
ROI = [(Projected score gain × spend_at_risk_usd × risk_factor)
       − Development investment] / Development investment × 100
```
Score risk factor: each 10-point improvement → ~5% reduction in supply disruption probability.

## Machine Learning

**Supplier Capability Classification**
```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import pandas as pd

def classify_supplier_maturity(df: pd.DataFrame) -> pd.DataFrame:
    """
    Classify supplier maturity level (1–5) based on audit and performance data.
    Features: composite_score, cpk_avg, iso_certified, spc_deployed,
              car_closure_rate, on_time_delivery_12m, ncr_rate_12m,
              innovation_index, csddd_assessed.
    Target: maturity_level (1–5).
    License: scikit-learn BSD-3.
    """
    features = ['composite_score', 'cpk_avg', 'iso_certified', 'spc_deployed',
                'car_closure_rate', 'on_time_delivery_12m', 'ncr_rate_12m']
    model = RandomForestClassifier(n_estimators=200, random_state=42)
    model.fit(df[features], df['maturity_level'])
    df['predicted_maturity'] = model.predict(df[features])
    df['maturity_confidence'] = model.predict_proba(df[features]).max(axis=1)
    return df
```

**Development Intervention Recommendation (NLP)**
```python
from transformers import pipeline

def recommend_development_actions(audit_findings: str) -> list[dict]:
    """
    Extract actionable development recommendations from audit findings text.
    Zero-shot classification against standard intervention categories.
    License: transformers Apache-2.0; facebook/bart-large-mnli.
    """
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
    interventions = ["spc_training", "iso_certification_support", "capacity_expansion",
                     "process_redesign", "technology_upgrade", "management_coaching",
                     "financial_restructuring", "dual_sourcing"]
    result = classifier(audit_findings[:512], candidate_labels=interventions, multi_label=True)
    return [{'intervention': l, 'score': round(s, 3)}
            for l, s in zip(result['labels'], result['scores']) if s > 0.4]
```

## Python

| Library | Use | License |
|---------|-----|---------|
| `pandas` | Development program DataFrames | BSD-3 |
| `numpy` | Score trends, ROI calculations | BSD-3 |
| `scikit-learn` | Maturity classification, clustering | BSD-3 |
| `transformers` | Audit finding NLP, recommendation | Apache-2.0 |
| `networkx` | Supplier network, tiering graph | BSD-3 |
| `scipy.stats` | Score improvement significance tests | BSD-3 |
| `lightgbm` | Disqualification risk scoring | MIT |

**Development ROI Calculation**
```python
def supplier_development_roi(score_before: float, score_after: float,
                              annual_spend_usd: float, development_cost_usd: float,
                              disruption_risk_factor: float = 0.005) -> dict:
    """
    Calculate ROI of supplier development investment.
    disruption_risk_factor: each score point ≈ 0.5% risk reduction.
    """
    score_gain = score_after - score_before
    risk_reduction = score_gain * disruption_risk_factor
    avoided_loss_usd = annual_spend_usd * risk_reduction
    roi_pct = (avoided_loss_usd - development_cost_usd) / development_cost_usd * 100
    return {'score_gain': score_gain, 'avoided_loss_usd': round(avoided_loss_usd, 2),
            'roi_pct': round(roi_pct, 1), 'payback_months': round(development_cost_usd / (avoided_loss_usd / 12), 1)}
```

## TypeScript

**Domain Objects**
- `domain/DevelopmentProgram.ts` — Development plan; milestones; KPI targets; sponsor
- `domain/SupplierAudit.ts` — Audit record; findings; maturity score; re-audit date
- `domain/CorrectiveActionReport.ts` — CAR; root cause; corrective action; closure verification
- `services/DevelopmentService.ts` — Program enrollment; milestone tracking; ROI calculation

**Development Milestone Tracking**
```typescript
type MilestoneStatus = 'NOT_STARTED' | 'IN_PROGRESS' | 'COMPLETED' | 'OVERDUE' | 'WAIVED';

interface DevelopmentMilestone {
  milestoneId: string;
  description: string;
  targetDate: ISOTimestamp;
  status: MilestoneStatus;
  evidenceRef?: string;   // URL or document reference proving completion
  verifiedBy?: string;    // auditor who verified completion
}
```

## OSI / Commercial

| Tool | License | Use |
|------|---------|-----|
| PostgreSQL | PostgreSQL (OSI) | Development program records, audit history |
| Apache Superset | Apache-2.0 | Development ROI, maturity dashboards |
| `transformers` | Apache-2.0 | Audit NLP, recommendation engine |
| OpenSearch | Apache-2.0 | Audit findings search |

**References**
- Monczka, R.M. et al. (2015). *Purchasing and Supply Chain Management*, 6th ed. Cengage.
- APICS/ASCM Dictionary, 17th ed. (2024) — *supplier development*, *approved vendor list*
- ISO 9001:2015 §8.4 — Control of externally provided processes
- CMMI Institute (2018). *CMMI for Development*, v2.0.
- EU Directive 2024/1760 (CSDDD) — Supply chain due diligence
- Chopra & Meindl, Ch.14 — Sourcing Decisions (Pearson, 2016)
