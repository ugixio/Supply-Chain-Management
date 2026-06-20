# Risk Management — Enterprise Implementation Guide

**Department:** 10 — Risk Management
**Standard:** ISO 31000:2018, ISO 28000:2022, SCOR-DS Enable
**Classification:** Internal — Restricted
**Version:** 1.0
**Date:** 2026-06-20

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Prerequisites and Dependencies](#2-prerequisites-and-dependencies)
3. [Phase 0: Assessment and AS-IS Analysis](#3-phase-0-assessment-and-as-is-analysis)
4. [Phase 1: Foundation and Master Data](#4-phase-1-foundation-and-master-data)
5. [Phase 2: Process Standardisation and Core Analytics](#5-phase-2-process-standardisation-and-core-analytics)
6. [Phase 3: Mathematical Models](#6-phase-3-mathematical-models)
7. [Phase 4: ML/AI Pipeline](#7-phase-4-mlai-pipeline)
8. [Phase 5: Integration and Automation](#8-phase-5-integration-and-automation)
9. [Phase 6: Continuous Improvement](#9-phase-6-continuous-improvement)
10. [Technology Stack and Architecture](#10-technology-stack-and-architecture)
11. [Change Management and Training](#11-change-management-and-training)
12. [Implementation KPIs](#12-implementation-kpis)
13. [Risk and Mitigation](#13-risk-and-mitigation)
14. [Timeline Summary](#14-timeline-summary)
15. [References](#15-references)

---

## 1. Executive Summary

Global supply chains face an accelerating frequency of high-impact disruptions: geopolitical conflict, climate-related logistics shocks, single-source supplier failures, and commodity concentration risk. The 2021 Suez Canal blockage demonstrated that a single node failure can lock up USD 9.6 billion per day in trade. The COVID-19 pandemic exposed the systemic fragility of just-in-time networks with zero resilience buffers. In this environment, reactive risk management is no longer acceptable.

This implementation guide establishes a quantitative, ISO 31000-compliant Enterprise Risk Management (ERM) capability for the Supply Chain Risk Management (SCRM) domain. The programme covers seven mathematical risk models, five ML/AI pipelines, and seven external data integrations. The end state is a continuously operating risk intelligence platform that converts early warning signals into automated Business Continuity Plan (BCP) triggers and recovery actions.

### Business Case

| Metric | Baseline (Year 0) | Target (Year 2) |
|--------|------------------|----------------|
| Mean Time to Detect disruption | 14 days | 2 days |
| Supplier visibility (Tier 1) | 60% | 100% |
| Supplier visibility (Tier 2) | 10% | 70% |
| HHI-driven dual-source coverage | 20% | 85% |
| BCP test frequency | Annual | Quarterly |
| Annual disruption cost (est.) | USD 42M | USD 18M |
| Risk-adjusted EBITDA improvement | — | USD 8–12M |

The programme pays back in 18 months assuming a single avoided Tier-1 supplier failure event (industry average disruption cost: USD 184M for Fortune 500, Allianz AGCS 2023).

---

## 2. Prerequisites and Dependencies

### 2.1 Organisational Prerequisites

- Executive sponsorship at CPO / CSCO level
- Dedicated SCRM team: 1x Risk Director, 2x Risk Analysts, 1x Data Engineer, 1x ML Engineer
- Risk appetite statement approved by Board Risk Committee
- Data sharing agreements with Tier-1 suppliers (minimum: site location, capacity, alternate source)

### 2.2 Technical Prerequisites

```
Python >= 3.11
Node.js >= 20.x (TypeScript 5.x)
PostgreSQL >= 15 (event store)
Redis >= 7 (pub/sub, cache)
Apache Kafka >= 3.5 (streaming pipeline)
Docker + Kubernetes (deployment)
```

### 2.3 Python Library Dependencies

```bash
pip install numpy scipy pandas statsmodels scikit-learn \
            torch torch-geometric \
            ray[rllib] stable-baselines3 \
            simpy networkx \
            pgmpy \
            transformers spacy \
            xgboost lightgbm \
            pulp ortools \
            requests httpx pydantic \
            pytest pytest-cov
```

### 2.4 Internal Module Dependencies

| Module | Dependency Reason |
|--------|------------------|
| `src/shared/` | Money, UOM, Event Store types |
| `src/departments/01-procurement/` | PO data, supplier contracts |
| `src/departments/02-supplier-management/` | Scorecard KPIs, supplier master |
| `src/departments/04-inventory/` | Stock levels, safety stock |
| `src/departments/06-logistics/` | Shipment ETAs, carrier risk |
| `src/departments/09-compliance/` | UFLPA / CSDDD risk flags |

### 2.5 External Data Feeds

| Feed | Purpose | Frequency |
|------|---------|-----------|
| Resilinc API | Supplier site mapping, disruption events | Real-time |
| Riskmethods API | Risk event scoring, supplier risk index | Hourly |
| Bloomberg B-PIPE | Commodity prices, macro indicators | Real-time |
| GDELT 2.0 API | Global news, conflict / disaster signals | 15 minutes |
| Swiss Re CatNet | Natural catastrophe exposure layers | Daily |
| US FEMA Disaster Declarations | US hazard events | Daily |
| Baltic Exchange BDI | Baltic Dry Index for freight cost | Daily |

---

## 3. Phase 0: Assessment and AS-IS Analysis

**Duration:** 4 weeks
**Owner:** Risk Director + external SCRM consultant

### 3.1 Supply Network Mapping

Conduct a complete Tier 1 through Tier 3 supplier mapping using the n-tier visibility methodology (Bode and Wagner 2015). For each node, capture:

- Legal entity name, DUNS / GLN
- Physical site GPS coordinates
- Annual spend (USD)
- Commodities supplied (GS1 classification)
- Single-source flag
- Country risk score (World Bank WGI)
- Natural hazard exposure (Swiss Re CatNet zone)

```python
# python/10_risk_management/as_is/network_mapping.py

import networkx as nx
import pandas as pd
from typing import Optional

def build_supply_network(
    supplier_csv: str,
    relationship_csv: str,
) -> nx.DiGraph:
    """
    Build directed supply network graph from supplier master and relationship data.

    Args:
        supplier_csv: Path to supplier master CSV with columns:
                      node_id, name, country, lat, lon, tier, annual_spend_usd
        relationship_csv: Path to relationship CSV with columns:
                          source_node, target_node, commodity, annual_volume_usd

    Returns:
        Directed graph where edges flow from supplier to buyer.
    """
    suppliers = pd.read_csv(supplier_csv)
    relationships = pd.read_csv(relationship_csv)

    G = nx.DiGraph()

    for _, row in suppliers.iterrows():
        G.add_node(
            row["node_id"],
            name=row["name"],
            country=row["country"],
            lat=row["lat"],
            lon=row["lon"],
            tier=row["tier"],
            annual_spend_usd=row["annual_spend_usd"],
        )

    for _, row in relationships.iterrows():
        G.add_edge(
            row["source_node"],
            row["target_node"],
            commodity=row["commodity"],
            annual_volume_usd=row["annual_volume_usd"],
        )

    return G
```

### 3.2 Risk Inventory

Enumerate all risk categories per ISO 31000 Annex A taxonomy:

| Category | Sub-category | Examples |
|----------|-------------|---------|
| Supply | Concentration, quality | Single-source, supplier insolvency |
| Demand | Volatility, bullwhip | Demand signal distortion |
| Process | Operational, capacity | Plant fire, labour strike |
| Environmental | Climate, natural hazard | Hurricane, earthquake, flood |
| Geopolitical | Trade policy, conflict | Tariffs, sanctions, war |
| Cyber | Data breach, ransomware | ERP attack, logistics platform breach |
| Regulatory | Compliance, enforcement | UFLPA detention, REACH violation |
| Financial | FX, commodity price | USD/EUR swing, lithium price spike |

### 3.3 Gap Analysis Deliverable

Produce a scored gap matrix comparing current state against ISO 31000:2018 requirements across all 6.x clauses. Score each clause 0–4 (0 = not implemented, 4 = optimised). Any clause scoring below 2 becomes a Phase 1 or Phase 2 workstream.

---

## 4. Phase 1: Foundation and Master Data

**Duration:** 6 weeks
**Owner:** Data Engineer + Risk Analyst

### 4.1 Risk Register Schema (TypeScript)

```typescript
// src/departments/10-risk-management/domain/RiskRegister.ts

import { ISOTimestamp, Money } from "../../../shared/types";

export type RiskCategory =
  | "SUPPLY"
  | "DEMAND"
  | "PROCESS"
  | "ENVIRONMENTAL"
  | "GEOPOLITICAL"
  | "CYBER"
  | "REGULATORY"
  | "FINANCIAL";

export type RiskStatus =
  | "IDENTIFIED"
  | "ASSESSED"
  | "MITIGATED"
  | "ACCEPTED"
  | "CLOSED";

export type RiskSeverityBand = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";

export interface RiskRegisterEntry {
  readonly riskId: string;              // UUID
  readonly title: string;
  readonly description: string;
  readonly category: RiskCategory;
  readonly status: RiskStatus;

  // ISO 31000 scoring
  readonly likelihood: 1 | 2 | 3 | 4 | 5;
  readonly impact: 1 | 2 | 3 | 4 | 5;
  readonly riskScore: number;           // likelihood × impact
  readonly severityBand: RiskSeverityBand;

  // Financial quantification
  readonly expectedAnnualLoss: Money;   // EAL in cents
  readonly exposureFactor: number;      // 0.0–1.0
  readonly annualOccurrenceProbability: number; // 0.0–1.0

  // Ownership
  readonly riskOwnerId: string;
  readonly businessUnit: string;
  readonly supplierId?: string;
  readonly commodityCode?: string;

  // Mitigation
  readonly mitigationActions: MitigationAction[];
  readonly residualLikelihood?: 1 | 2 | 3 | 4 | 5;
  readonly residualImpact?: 1 | 2 | 3 | 4 | 5;

  // Audit fields
  readonly identifiedAt: ISOTimestamp;
  readonly lastReviewedAt: ISOTimestamp;
  readonly nextReviewDue: ISOTimestamp;
  readonly isDeleted: boolean;
}

export interface MitigationAction {
  readonly actionId: string;
  readonly description: string;
  readonly owner: string;
  readonly dueDate: string;             // ISO 8601
  readonly status: "OPEN" | "IN_PROGRESS" | "COMPLETED" | "OVERDUE";
  readonly costEstimate: Money;
}

export function computeRiskScore(
  likelihood: number,
  impact: number
): { score: number; band: RiskSeverityBand } {
  const score = likelihood * impact;
  let band: RiskSeverityBand;

  if (score >= 15) band = "CRITICAL";
  else if (score >= 10) band = "HIGH";
  else if (score >= 5) band = "MEDIUM";
  else band = "LOW";

  return { score, band };
}
```

### 4.2 Event-Sourced Risk Domain

All risk state changes are immutable domain events appended to the event store:

```typescript
// src/departments/10-risk-management/domain/RiskEvents.ts

export type RiskEvent =
  | RiskIdentifiedEvent
  | RiskScoredEvent
  | RiskMitigatedEvent
  | RiskAcceptedEvent
  | RiskClosedEvent
  | RiskEscalatedEvent;

export interface RiskIdentifiedEvent {
  readonly type: "RISK_IDENTIFIED";
  readonly riskId: string;
  readonly category: RiskCategory;
  readonly identifiedBy: string;
  readonly occurredAt: ISOTimestamp;
}

export interface RiskEscalatedEvent {
  readonly type: "RISK_ESCALATED";
  readonly riskId: string;
  readonly riskScore: number;
  readonly escalationTarget: string;   // email / team
  readonly trigger: "SCORE_THRESHOLD" | "VELOCITY" | "MANUAL";
  readonly occurredAt: ISOTimestamp;
}
```

### 4.3 Master Data Governance

Establish a Risk Data Dictionary covering:
- Likelihood scale definitions (1 = < 1% annual probability, 5 = > 50%)
- Impact scale definitions aligned to revenue thresholds (1 = < USD 100K, 5 = > USD 50M)
- Review cadence by severity: CRITICAL = weekly, HIGH = monthly, MEDIUM = quarterly, LOW = annual

---

## 5. Phase 2: Process Standardisation and Core Analytics

**Duration:** 8 weeks
**Owner:** Risk Analyst + Procurement leads

### 5.1 SCRM Process Framework (SCOR Enable)

Map every risk process to a SCOR-DS Enable (sE) process reference:

| SCOR Process | Activity | Owner | Frequency |
|-------------|---------|-------|-----------|
| sE1 — Manage Rules | Risk policy, appetite | CPO | Annual |
| sE2 — Manage Performance | KPI dashboards, OKRs | Risk Director | Monthly |
| sE3 — Manage Information | Risk register, event feed | Risk Analyst | Weekly |
| sE4 — Manage HR | Training, certification | L&D | Quarterly |
| sE5 — Manage Assets | BCP assets, buffer stock | SCM Ops | As triggered |
| sE6 — Manage Knowledge | Lessons learned, AAR | Risk Director | Post-event |

### 5.2 Escalation Protocol

```
Risk Score >= 15 (CRITICAL): Immediate escalation to CPO + Board Risk Committee
                              BCP activated within 4 hours
                              War-room convened within 24 hours

Risk Score >= 10 (HIGH):     Escalation to Risk Director + Category Manager
                              Mitigation plan required within 5 business days
                              Status update weekly

Risk Score >= 5 (MEDIUM):    Assigned to Risk Owner
                              Mitigation plan required within 30 days
                              Status update monthly

Risk Score < 5 (LOW):        Logged, accepted or monitored
                              Annual review
```

### 5.3 Key Risk Indicators (KRIs)

| KRI | Trigger Threshold | Data Source | Frequency |
|----|-----------------|------------|-----------|
| Supplier on-time delivery (OTD) | < 85% rolling 30-day | ERP/scorecard | Daily |
| Commodity HHI | > 2500 | Procurement master | Weekly |
| Bullwhip ratio | > 2.0 | Order/demand data | Weekly |
| Single-source spend % | > 40% per category | Procurement | Monthly |
| Geopolitical Risk Index (GPR) | > 150 (Caldara-Iacoviello) | Bloomberg | Daily |
| Baltic Dry Index 30-day delta | < -25% | Bloomberg | Daily |
| Supplier financial distress | Altman Z-score < 1.8 | Credit bureau | Monthly |
| Tier-1 country WGI Political Stability | < -0.5 | World Bank | Quarterly |

---

## 6. Phase 3: Mathematical Models

**Duration:** 10 weeks
**Owner:** Data Engineer + Risk Analyst

---

### 6.1 5x5 Risk Matrix (ISO 31000)

#### Theory

The risk matrix operationalises ISO 31000:2018 clause 6.4.3 (risk assessment). Each risk is scored on two orthogonal dimensions: Likelihood (L) and Impact (I), each on a 1–5 integer scale.

```
Risk Score = Likelihood (1–5) × Impact (1–5)
Range: 1 (minimum) to 25 (maximum)

Severity Bands:
  CRITICAL : score >= 15
  HIGH     : score >= 10
  MEDIUM   : score >= 5
  LOW      : score <  5
```

#### Implementation

```python
# python/10_risk_management/models/risk_matrix.py

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Literal

SeverityBand = Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"]

@dataclass
class RiskScore:
    likelihood: int      # 1–5
    impact: int          # 1–5
    score: int
    band: SeverityBand

def score_risk(likelihood: int, impact: int) -> RiskScore:
    """
    Compute ISO 31000 risk score and assign severity band.

    Escalation triggers:
      score >= 15 -> CRITICAL
      score >= 10 -> HIGH
      score >= 5  -> MEDIUM
      score <  5  -> LOW
    """
    if not (1 <= likelihood <= 5):
        raise ValueError(f"Likelihood must be 1–5, got {likelihood}")
    if not (1 <= impact <= 5):
        raise ValueError(f"Impact must be 1–5, got {impact}")

    score = likelihood * impact

    if score >= 15:
        band: SeverityBand = "CRITICAL"
    elif score >= 10:
        band = "HIGH"
    elif score >= 5:
        band = "MEDIUM"
    else:
        band = "LOW"

    return RiskScore(likelihood=likelihood, impact=impact, score=score, band=band)


def build_heat_map() -> pd.DataFrame:
    """
    Construct 5x5 heat map matrix with severity band labels.
    Rows = Likelihood (5 down to 1), Columns = Impact (1 to 5).
    """
    data = {}
    for impact in range(1, 6):
        col = []
        for likelihood in range(5, 0, -1):
            r = score_risk(likelihood, impact)
            col.append(f"{r.score} ({r.band[0]})")
        data[f"Impact {impact}"] = col

    index = [f"Likelihood {i}" for i in range(5, 0, -1)]
    return pd.DataFrame(data, index=index)


def filter_risks_by_band(
    risk_df: pd.DataFrame,
    min_band: SeverityBand,
) -> pd.DataFrame:
    """Filter risk register to risks at or above the specified band."""
    band_rank = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
    threshold = band_rank[min_band]

    scored = risk_df.copy()
    scored["_rank"] = scored["band"].map(band_rank)
    return scored[scored["_rank"] >= threshold].drop(columns=["_rank"])
```

#### Heat Map (Textual Representation)

```
             Impact 1   Impact 2   Impact 3   Impact 4   Impact 5
Likelihood 5    5 M       10 H       15 C       20 C       25 C
Likelihood 4    4 L        8 M       12 H       16 C       20 C
Likelihood 3    3 L        6 M        9 M       12 H       15 C
Likelihood 2    2 L        4 L        6 M        8 M       10 H
Likelihood 1    1 L        2 L        3 L        4 L        5 M

Legend: C=CRITICAL (>=15), H=HIGH (>=10), M=MEDIUM (>=5), L=LOW (<5)
```

---

### 6.2 EAL — Expected Annual Loss

#### Theory

EAL quantifies the annualised financial exposure of a risk event, combining frequency, severity, and the fraction of asset value at risk.

```
EAL = Annual Occurrence Probability (AOP) × Impact Value (IV) × Exposure Factor (EF)

Where:
  AOP = probability of the event occurring at least once per year (0.0–1.0)
  IV  = total asset / revenue value at risk (USD)
  EF  = fraction of IV that would be lost if the event occurs (0.0–1.0)
```

#### Implementation

```python
# python/10_risk_management/models/eal.py

import numpy as np
import pandas as pd
from typing import NamedTuple

class EALResult(NamedTuple):
    risk_id: str
    aop: float
    impact_value_usd: float
    exposure_factor: float
    eal_usd: float
    priority_rank: int

def compute_eal(
    risk_id: str,
    annual_occurrence_probability: float,
    impact_value_usd: float,
    exposure_factor: float,
) -> float:
    """
    Compute Expected Annual Loss (EAL).

    Args:
        annual_occurrence_probability: AOP in range [0, 1]
        impact_value_usd: Total asset or revenue value at risk (USD)
        exposure_factor: Fraction of impact_value_usd lost on occurrence [0, 1]

    Returns:
        EAL in USD (float)
    """
    if not (0.0 <= annual_occurrence_probability <= 1.0):
        raise ValueError("AOP must be between 0 and 1")
    if not (0.0 <= exposure_factor <= 1.0):
        raise ValueError("Exposure factor must be between 0 and 1")
    if impact_value_usd < 0:
        raise ValueError("Impact value must be non-negative")

    return annual_occurrence_probability * impact_value_usd * exposure_factor


def rank_portfolio_by_eal(risks: list[dict]) -> pd.DataFrame:
    """
    Rank a portfolio of risks by EAL for budget prioritisation.

    Args:
        risks: List of dicts with keys:
               risk_id, aop, impact_value_usd, exposure_factor

    Returns:
        DataFrame sorted descending by eal_usd with cumulative % column.
    """
    rows = []
    for r in risks:
        eal = compute_eal(
            r["risk_id"],
            r["aop"],
            r["impact_value_usd"],
            r["exposure_factor"],
        )
        rows.append({
            "risk_id": r["risk_id"],
            "aop": r["aop"],
            "impact_value_usd": r["impact_value_usd"],
            "exposure_factor": r["exposure_factor"],
            "eal_usd": eal,
        })

    df = pd.DataFrame(rows).sort_values("eal_usd", ascending=False).reset_index(drop=True)
    df["priority_rank"] = df.index + 1
    total_eal = df["eal_usd"].sum()
    df["cumulative_eal_pct"] = (df["eal_usd"].cumsum() / total_eal * 100).round(1)
    return df
```

**Portfolio Decision Rule:** Allocate mitigation budget to risks in EAL rank order until the top-ranked risks collectively represent 80% of total portfolio EAL (Pareto principle applied to risk financing).

---

### 6.3 HHI — Herfindahl-Hirschman Index per Commodity

#### Theory

The HHI measures supplier concentration per commodity category. A high HHI signals that spend is concentrated in few suppliers, creating single-source risk. The US Department of Justice merger guidelines define markets with HHI > 2500 as "highly concentrated."

```
HHI = sum( market_share_i ^ 2 ) × 10000

Where market_share_i = supplier_i_spend / total_commodity_spend

Range: 0 (perfect competition) to 10000 (monopoly)

Thresholds:
  HHI <  1500  : Competitive — no action required
  HHI 1500–2500: Moderately concentrated — monitor
  HHI > 2500   : Highly concentrated — initiate dual-source programme
```

#### Implementation

```python
# python/10_risk_management/models/hhi.py

import pandas as pd
import numpy as np

def compute_hhi(spend_by_supplier: dict[str, float]) -> float:
    """
    Compute Herfindahl-Hirschman Index for a commodity category.

    Args:
        spend_by_supplier: Dict mapping supplier_id to annual spend (USD).
                           All values must be non-negative.

    Returns:
        HHI score (0–10000). Higher = more concentrated.
    """
    total = sum(spend_by_supplier.values())
    if total <= 0:
        raise ValueError("Total spend must be positive")

    shares = [v / total for v in spend_by_supplier.values()]
    hhi = sum(s ** 2 for s in shares) * 10000
    return round(hhi, 2)


def classify_concentration(hhi: float) -> str:
    """Return concentration classification and recommended action."""
    if hhi > 2500:
        return "HIGHLY_CONCENTRATED — initiate dual-source programme"
    elif hhi > 1500:
        return "MODERATELY_CONCENTRATED — monitor quarterly"
    else:
        return "COMPETITIVE — no action required"


def hhi_portfolio_scan(
    procurement_df: pd.DataFrame,
    supplier_col: str = "supplier_id",
    commodity_col: str = "commodity_code",
    spend_col: str = "annual_spend_usd",
) -> pd.DataFrame:
    """
    Scan entire procurement portfolio for concentration risk.

    Args:
        procurement_df: DataFrame of procurement lines.

    Returns:
        DataFrame with one row per commodity, HHI score, classification,
        leading supplier, and leading supplier share %.
    """
    results = []

    for commodity, group in procurement_df.groupby(commodity_col):
        spend_map = group.groupby(supplier_col)[spend_col].sum().to_dict()
        hhi = compute_hhi(spend_map)
        total = sum(spend_map.values())
        top_supplier = max(spend_map, key=spend_map.get)
        top_share_pct = round(spend_map[top_supplier] / total * 100, 1)

        results.append({
            "commodity_code": commodity,
            "hhi": hhi,
            "concentration": classify_concentration(hhi),
            "supplier_count": len(spend_map),
            "top_supplier_id": top_supplier,
            "top_supplier_share_pct": top_share_pct,
            "dual_source_trigger": hhi > 2500,
        })

    return pd.DataFrame(results).sort_values("hhi", ascending=False)
```

**Governance Rule:** Any commodity with HHI > 2500 must have a Board-approved dual-source plan with a 12-month implementation timeline. Progress is tracked monthly at the Procurement Risk Review.

---

### 6.4 Bullwhip Ratio

#### Theory

The Bullwhip Effect (Lee, Padmanabhan, Whang 1997) describes how demand variability amplifies upstream through supply chain tiers. Chen et al. (2000) derived a theoretical lower bound for the bullwhip ratio under a moving-average demand signal processing policy.

```
Bullwhip Ratio = Var(orders) / Var(demand)

Chen 2000 Theoretical Lower Bound (MA forecasting, lead time L, review period p):
  BWE >= 1 + (2L/p) + (2L/p)^2

Four-Cause Decomposition (Lee 1997):
  1. Demand Signal Processing  — forecast errors amplify orders
  2. Rationing and Shortage Gaming — buyers inflate orders expecting rationing
  3. Order Batching — periodic ordering creates artificial spikes
  4. Price Fluctuation — forward buying during promotions distorts signal
```

#### Implementation

```python
# python/10_risk_management/models/bullwhip.py

import numpy as np
import pandas as pd
from scipy import stats

def compute_bullwhip_ratio(
    order_series: np.ndarray,
    demand_series: np.ndarray,
) -> float:
    """
    Compute empirical Bullwhip Ratio.

    Args:
        order_series: Time series of orders placed by a supply chain node.
        demand_series: Time series of downstream demand seen by that node.

    Returns:
        Bullwhip ratio (>1 indicates amplification, target ~1.0).
    """
    if len(order_series) != len(demand_series):
        raise ValueError("Order and demand series must have equal length")
    if len(order_series) < 10:
        raise ValueError("Minimum 10 observations required")

    var_orders = np.var(order_series, ddof=1)
    var_demand = np.var(demand_series, ddof=1)

    if var_demand == 0:
        raise ValueError("Demand variance is zero; cannot compute ratio")

    return round(var_orders / var_demand, 4)


def chen_2000_lower_bound(lead_time: float, review_period: float) -> float:
    """
    Compute Chen (2000) theoretical lower bound for bullwhip ratio.

    Args:
        lead_time: Replenishment lead time in periods (L).
        review_period: Order review period (p).

    Returns:
        Theoretical minimum bullwhip ratio under MA forecasting.
    """
    ratio = 2 * lead_time / review_period
    return 1 + ratio + ratio ** 2


def decompose_bullwhip(
    orders: pd.Series,
    demand: pd.Series,
    prices: pd.Series,
    review_period_days: int = 7,
    lead_time_days: int = 14,
) -> dict[str, float]:
    """
    Decompose total bullwhip ratio into four attributable causes.

    Returns dict with keys:
      total_bwe, demand_signal, rationing_gaming,
      order_batching, price_fluctuation, unexplained
    """
    total_bwe = compute_bullwhip_ratio(orders.values, demand.values)
    theoretical_lb = chen_2000_lower_bound(lead_time_days, review_period_days)

    # Demand signal processing: excess variance from forecast error
    demand_signal_component = theoretical_lb - 1.0

    # Price fluctuation: correlation between price changes and order spikes
    price_change = prices.pct_change().fillna(0)
    order_change = orders.pct_change().fillna(0)
    price_corr = abs(price_change.corr(order_change))
    price_component = (total_bwe - theoretical_lb) * price_corr * 0.4

    # Order batching: coefficient of variation ratio
    cv_orders = orders.std() / orders.mean() if orders.mean() > 0 else 0
    cv_demand = demand.std() / demand.mean() if demand.mean() > 0 else 0
    batching_component = max(0, (cv_orders - cv_demand) * 0.5)

    # Rationing gaming: residual
    explained = demand_signal_component + price_component + batching_component
    rationing_component = max(0, total_bwe - 1.0 - explained)

    return {
        "total_bwe": round(total_bwe, 3),
        "chen_lower_bound": round(theoretical_lb, 3),
        "demand_signal_processing": round(demand_signal_component, 3),
        "price_fluctuation": round(price_component, 3),
        "order_batching": round(batching_component, 3),
        "rationing_gaming": round(rationing_component, 3),
    }
```

**Alert Threshold:** Bullwhip ratio > 2.0 triggers a root-cause investigation. Rationing gaming component > 0.5 triggers a supplier communication protocol (open-book forecasting sharing).

---

### 6.5 Monte Carlo Loss Distribution

#### Theory

Monte Carlo simulation generates an empirical loss distribution by sampling from probability distributions of loss frequency and severity. Value at Risk (VaR) at the 95th and 99th percentile bounds the unexpected loss. Conditional Value at Risk (CVaR), also called Expected Shortfall, captures the average loss beyond the VaR threshold — the tail risk measure required under BASEL III and preferred in supply chain risk finance.

```
VaR(95%) = 95th percentile of simulated annual loss distribution
VaR(99%) = 99th percentile of simulated annual loss distribution
CVaR(95%) = E[Loss | Loss > VaR(95%)]
```

#### Implementation

```python
# python/10_risk_management/models/monte_carlo.py

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Optional

N_SIMULATIONS = 10_000
RANDOM_SEED = 42

@dataclass
class MonteCarloResult:
    n_simulations: int
    mean_loss_usd: float
    std_loss_usd: float
    var_95_usd: float
    var_99_usd: float
    cvar_95_usd: float
    cvar_99_usd: float
    max_loss_usd: float
    percentile_distribution: pd.Series


def run_monte_carlo_loss(
    annual_frequency_mean: float,
    loss_severity_mean_usd: float,
    loss_severity_std_usd: float,
    frequency_distribution: str = "poisson",
    severity_distribution: str = "lognormal",
    n_simulations: int = N_SIMULATIONS,
    seed: int = RANDOM_SEED,
) -> MonteCarloResult:
    """
    Run Monte Carlo simulation to generate annual loss distribution.

    Args:
        annual_frequency_mean: Expected number of loss events per year (lambda for Poisson).
        loss_severity_mean_usd: Mean single-event loss in USD.
        loss_severity_std_usd: Std deviation of single-event loss in USD.
        frequency_distribution: 'poisson' or 'negative_binomial'.
        severity_distribution: 'lognormal' or 'gamma'.
        n_simulations: Number of Monte Carlo trials (default 10,000).
        seed: Random seed for reproducibility.

    Returns:
        MonteCarloResult with VaR and CVaR metrics.
    """
    rng = np.random.default_rng(seed)
    annual_losses = np.zeros(n_simulations)

    # Lognormal parameters from mean and std
    ln_mean = np.log(
        loss_severity_mean_usd ** 2 /
        np.sqrt(loss_severity_mean_usd ** 2 + loss_severity_std_usd ** 2)
    )
    ln_sigma = np.sqrt(
        np.log(1 + (loss_severity_std_usd / loss_severity_mean_usd) ** 2)
    )

    for i in range(n_simulations):
        # Sample number of events this year
        if frequency_distribution == "poisson":
            n_events = rng.poisson(annual_frequency_mean)
        else:
            # Negative binomial: overdispersed count data
            n_events = rng.negative_binomial(
                n=annual_frequency_mean, p=0.5
            )

        if n_events == 0:
            continue

        # Sample loss severity for each event
        if severity_distribution == "lognormal":
            severities = rng.lognormal(mean=ln_mean, sigma=ln_sigma, size=n_events)
        else:
            # Gamma distribution
            shape = (loss_severity_mean_usd / loss_severity_std_usd) ** 2
            scale = loss_severity_std_usd ** 2 / loss_severity_mean_usd
            severities = rng.gamma(shape=shape, scale=scale, size=n_events)

        annual_losses[i] = severities.sum()

    var_95 = float(np.percentile(annual_losses, 95))
    var_99 = float(np.percentile(annual_losses, 99))
    cvar_95 = float(annual_losses[annual_losses > var_95].mean())
    cvar_99 = float(annual_losses[annual_losses > var_99].mean())

    percentiles = pd.Series(
        [float(np.percentile(annual_losses, p)) for p in range(0, 101, 5)],
        index=[f"p{p}" for p in range(0, 101, 5)],
    )

    return MonteCarloResult(
        n_simulations=n_simulations,
        mean_loss_usd=float(annual_losses.mean()),
        std_loss_usd=float(annual_losses.std()),
        var_95_usd=var_95,
        var_99_usd=var_99,
        cvar_95_usd=cvar_95,
        cvar_99_usd=cvar_99,
        max_loss_usd=float(annual_losses.max()),
        percentile_distribution=percentiles,
    )
```

**Practical Use:** Run Monte Carlo annually per risk category and in aggregate. The CVaR(99%) figure feeds the company's insurance captive sizing model and the Board's risk appetite statement.

---

### 6.6 TTR / TTS Resilience Metrics

#### Theory

Sheffi and Rice (2005) define supply chain resilience through two complementary time-based metrics:

- **TTS (Time to Survive):** The duration a company can continue normal operations from its current inventory and contractual buffers before a disruption causes a material business impact.
- **TTR (Time to Recover):** The elapsed time from disruption onset to restoration of pre-disruption supply capacity.

The **Resilience Gap** = TTR − TTS. A positive gap means the business will suffer a performance degradation period. Resilience investment should target TTR < TTS.

```
TTS = buffer_inventory_units / average_daily_demand_units
      + contractual_buffer_days (e.g., safety stock from alternate source)

TTR = detection_time + decision_time + ramp_up_time (alternate supplier)

Resilience Gap = TTR - TTS
  Gap > 0: Performance degradation expected (duration = gap in days)
  Gap <= 0: Resilient — buffer absorbs disruption
```

#### Implementation

```python
# python/10_risk_management/models/resilience.py

import pandas as pd
from dataclasses import dataclass

@dataclass
class ResilienceProfile:
    node_id: str
    commodity: str
    tts_days: float
    ttr_days: float
    resilience_gap_days: float
    is_resilient: bool
    recommended_buffer_uplift_days: float

def compute_tts(
    buffer_inventory_units: float,
    average_daily_demand_units: float,
    contractual_buffer_days: float = 0.0,
) -> float:
    """
    Compute Time to Survive (TTS) in days.

    Args:
        buffer_inventory_units: On-hand + pipeline inventory available as buffer.
        average_daily_demand_units: Average daily consumption rate.
        contractual_buffer_days: Additional days covered by supply contracts
                                 or vendor-managed inventory agreements.

    Returns:
        TTS in days.
    """
    if average_daily_demand_units <= 0:
        raise ValueError("Average daily demand must be positive")

    inventory_cover = buffer_inventory_units / average_daily_demand_units
    return inventory_cover + contractual_buffer_days


def compute_ttr(
    detection_days: float,
    decision_days: float,
    alternate_supplier_ramp_days: float,
) -> float:
    """
    Compute Time to Recover (TTR) in days.

    Args:
        detection_days: Time from disruption onset to confirmed detection.
        decision_days: Time from detection to BCP activation decision.
        alternate_supplier_ramp_days: Time for alternate supplier to reach
                                      required supply volume.

    Returns:
        TTR in days.
    """
    return detection_days + decision_days + alternate_supplier_ramp_days


def resilience_gap_analysis(
    nodes: list[dict],
) -> pd.DataFrame:
    """
    Run resilience gap analysis across all supply nodes.

    Each dict in nodes must contain:
      node_id, commodity, buffer_inventory_units, avg_daily_demand,
      contractual_buffer_days, detection_days, decision_days, ramp_days

    Returns:
        DataFrame with TTR, TTS, gap, and buffer uplift recommendation.
    """
    profiles = []

    for n in nodes:
        tts = compute_tts(
            n["buffer_inventory_units"],
            n["avg_daily_demand"],
            n.get("contractual_buffer_days", 0.0),
        )
        ttr = compute_ttr(
            n["detection_days"],
            n["decision_days"],
            n["ramp_days"],
        )
        gap = ttr - tts
        is_resilient = gap <= 0
        # Recommended buffer uplift: cover the gap + 20% safety margin
        uplift = max(0, gap * 1.2)

        profiles.append(ResilienceProfile(
            node_id=n["node_id"],
            commodity=n["commodity"],
            tts_days=round(tts, 1),
            ttr_days=round(ttr, 1),
            resilience_gap_days=round(gap, 1),
            is_resilient=is_resilient,
            recommended_buffer_uplift_days=round(uplift, 1),
        ))

    return pd.DataFrame([p.__dict__ for p in profiles]).sort_values(
        "resilience_gap_days", ascending=False
    )
```

---

### 6.7 SimPy Discrete-Event Disruption Simulation

#### Theory

A SimPy-based digital twin of the supply network models node failures, cascade propagation, and recovery. Each supplier node is a SimPy `Resource`. A disruption is injected as a capacity reduction event. Downstream nodes deplete their buffers (TTS countdown), and alternate routes are activated if available. The simulation outputs a time series of production capacity at the focal firm.

#### Implementation

```python
# python/10_risk_management/models/disruption_simulation.py

import simpy
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class SupplyNode:
    node_id: str
    name: str
    daily_capacity: float
    buffer_days: float
    alternate_node_id: Optional[str] = None
    alternate_ramp_days: float = 14.0

@dataclass
class DisruptionEvent:
    node_id: str
    start_day: float
    duration_days: float
    capacity_reduction_pct: float   # 0.0–1.0

@dataclass
class SimulationResult:
    timeline_df: pd.DataFrame        # columns: day, node_id, capacity_pct
    total_lost_output_units: float
    max_consecutive_zero_days: int
    recovery_day: float

class SupplyNetworkSimulation:
    """
    SimPy discrete-event simulation of supply network disruption and recovery.
    Models: node failure injection, buffer depletion, cascade to downstream,
    alternate source activation.
    """

    def __init__(
        self,
        nodes: list[SupplyNode],
        disruptions: list[DisruptionEvent],
        sim_duration_days: int = 180,
        daily_demand: float = 1000.0,
        seed: int = 42,
    ):
        self.nodes = {n.node_id: n for n in nodes}
        self.disruptions = disruptions
        self.sim_duration = sim_duration_days
        self.daily_demand = daily_demand
        self.rng = np.random.default_rng(seed)
        self.timeline: list[dict] = []

    def run(self) -> SimulationResult:
        env = simpy.Environment()
        node_capacities = {nid: n.daily_capacity for nid, n in self.nodes.items()}
        node_buffers = {nid: n.daily_capacity * n.buffer_days for nid, n in self.nodes.items()}

        def disruption_process(env: simpy.Environment):
            for disruption in sorted(self.disruptions, key=lambda d: d.start_day):
                yield env.timeout(disruption.start_day)

                node = self.nodes[disruption.node_id]
                original_cap = node_capacities[disruption.node_id]
                reduced_cap = original_cap * (1 - disruption.capacity_reduction_pct)
                node_capacities[disruption.node_id] = reduced_cap

                # Schedule recovery
                env.process(self._recovery_process(
                    env, disruption, original_cap, node_capacities
                ))

        def _supply_process(env: simpy.Environment):
            while True:
                day = env.now
                total_supply = sum(node_capacities.values())
                # Buffer depletion / refill logic
                for nid, node in self.nodes.items():
                    cap = node_capacities[nid]
                    if cap < node.daily_capacity:
                        # Draw from buffer
                        gap = node.daily_capacity - cap
                        node_buffers[nid] = max(0, node_buffers[nid] - gap)

                self.timeline.append({
                    "day": day,
                    "total_supply": min(total_supply, self.daily_demand),
                    "unmet_demand": max(0, self.daily_demand - total_supply),
                })
                yield env.timeout(1)

        env.process(disruption_process(env))
        env.process(_supply_process(env))
        env.run(until=self.sim_duration)

        timeline_df = pd.DataFrame(self.timeline)
        total_lost = timeline_df["unmet_demand"].sum()

        # Max consecutive days of zero supply
        zero_days = (timeline_df["total_supply"] == 0).astype(int)
        max_consec = self._max_consecutive(zero_days.tolist())

        # Recovery day: first day supply returns to >= 90% demand
        recovered = timeline_df[
            timeline_df["total_supply"] >= 0.9 * self.daily_demand
        ]
        recovery_day = float(recovered["day"].min()) if len(recovered) > 0 else float(self.sim_duration)

        return SimulationResult(
            timeline_df=timeline_df,
            total_lost_output_units=total_lost,
            max_consecutive_zero_days=max_consec,
            recovery_day=recovery_day,
        )

    def _recovery_process(self, env, disruption, original_cap, capacities):
        yield env.timeout(disruption.duration_days)
        capacities[disruption.node_id] = original_cap

    @staticmethod
    def _max_consecutive(bits: list[int]) -> int:
        max_run = cur_run = 0
        for b in bits:
            cur_run = cur_run + 1 if b else 0
            max_run = max(max_run, cur_run)
        return max_run
```

---

## 7. Phase 4: ML/AI Pipeline

**Duration:** 14 weeks
**Owner:** ML Engineer + Data Engineer

---

### 7.1 LSTM Disruption Prediction

#### Architecture

Input: 90-day sliding window of daily macro indicators
- PMI (Purchasing Managers Index) — manufacturing output signal
- BDI (Baltic Dry Index) — global shipping cost / freight capacity
- GPR (Geopolitical Risk Index, Caldara-Iacoviello 2022) — conflict / policy uncertainty

Output: 30-day ahead disruption probability (binary classification)

#### Step-by-Step Implementation

**Step 1: Data Pipeline**

```python
# python/10_risk_management/ml/lstm_disruption/data_pipeline.py

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

SEQUENCE_LENGTH = 90   # days of history
FORECAST_HORIZON = 30  # days ahead to predict

def build_lstm_dataset(
    macro_df: pd.DataFrame,  # columns: date, pmi, bdi, gpr
    disruption_labels: pd.Series,  # index: date, value: 0/1
) -> tuple[np.ndarray, np.ndarray]:
    """
    Build X (sequences) and y (disruption label for next 30 days).

    Returns:
        X: shape (n_samples, SEQUENCE_LENGTH, n_features)
        y: shape (n_samples,) — 1 if any disruption in next 30 days
    """
    features = ["pmi", "bdi", "gpr"]
    scaler = StandardScaler()
    scaled = scaler.fit_transform(macro_df[features].values)

    X, y = [], []
    aligned_labels = disruption_labels.reindex(macro_df["date"]).fillna(0)

    for i in range(SEQUENCE_LENGTH, len(macro_df) - FORECAST_HORIZON):
        X.append(scaled[i - SEQUENCE_LENGTH:i])
        # Label = 1 if any disruption event in next 30 days
        future_labels = aligned_labels.iloc[i:i + FORECAST_HORIZON]
        y.append(1 if future_labels.sum() > 0 else 0)

    return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32)
```

**Step 2: Model Definition**

```python
# python/10_risk_management/ml/lstm_disruption/model.py

import torch
import torch.nn as nn

class DisruptionLSTM(nn.Module):
    """
    Bidirectional LSTM for supply chain disruption prediction.
    Input: (batch, seq_len=90, features=3)
    Output: disruption probability in next 30 days
    """

    def __init__(
        self,
        input_size: int = 3,
        hidden_size: int = 128,
        num_layers: int = 2,
        dropout: float = 0.3,
    ):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout,
        )
        self.attention = nn.Linear(hidden_size * 2, 1)
        self.classifier = nn.Sequential(
            nn.Linear(hidden_size * 2, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 1),
            nn.Sigmoid(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        lstm_out, _ = self.lstm(x)                  # (B, T, H*2)
        attn_weights = torch.softmax(
            self.attention(lstm_out), dim=1
        )                                            # (B, T, 1)
        context = (lstm_out * attn_weights).sum(dim=1)  # (B, H*2)
        return self.classifier(context).squeeze(-1)
```

**Step 3: Training Loop**

```python
# python/10_risk_management/ml/lstm_disruption/train.py

import torch
from torch.utils.data import DataLoader, TensorDataset
from sklearn.metrics import roc_auc_score

def train_disruption_lstm(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    epochs: int = 50,
    lr: float = 1e-3,
    batch_size: int = 64,
) -> DisruptionLSTM:

    model = DisruptionLSTM()
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    # Weighted BCE for class imbalance (disruptions are rare)
    pos_weight = torch.tensor([(y_train == 0).sum() / max((y_train == 1).sum(), 1)])
    criterion = torch.nn.BCEWithLogitsLoss(pos_weight=pos_weight)

    train_ds = TensorDataset(
        torch.from_numpy(X_train),
        torch.from_numpy(y_train),
    )
    loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True)

    for epoch in range(epochs):
        model.train()
        for X_batch, y_batch in loader:
            optimizer.zero_grad()
            preds = model(X_batch)
            loss = criterion(preds, y_batch)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

        # Validation AUC
        model.eval()
        with torch.no_grad():
            val_preds = model(torch.from_numpy(X_val)).numpy()
        auc = roc_auc_score(y_val, val_preds)
        if epoch % 10 == 0:
            print(f"Epoch {epoch:3d} | Val AUC: {auc:.4f}")

    return model
```

---

### 7.2 NLP Early Warning System

#### Architecture

- Source: GDELT 2.0 API (15-minute update) + Reuters Eikon news wire
- NLP Pipeline: spaCy NER for entity extraction (supplier names, countries, commodities) → HuggingFace DistilBERT for sentiment classification → keyword relevance scoring
- Alert logic: sentiment score < -0.6 AND entity matches Tier-1 supplier → generate RISK_SIGNAL event

```python
# python/10_risk_management/ml/nlp_ews/pipeline.py

import spacy
from transformers import pipeline
from typing import Optional
import requests

nlp = spacy.load("en_core_web_sm")
sentiment_model = pipeline(
    "text-classification",
    model="distilbert-base-uncased-finetuned-sst-2-english",
)

RISK_KEYWORDS = {
    "disruption", "strike", "fire", "flood", "earthquake", "shortage",
    "bankrupt", "insolvency", "tariff", "sanction", "export ban",
    "port closure", "factory closure", "force majeure", "contamination",
}

def fetch_gdelt_articles(
    query: str,
    max_records: int = 250,
) -> list[dict]:
    """Fetch recent GDELT articles matching query."""
    url = (
        f"https://api.gdeltproject.org/api/v2/doc/doc"
        f"?query={query}&mode=artlist&maxrecords={max_records}&format=json"
    )
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json().get("articles", [])


def analyse_article(
    article: dict,
    supplier_entity_list: list[str],
) -> Optional[dict]:
    """
    Extract risk signals from a news article.

    Returns alert dict if risk signal detected, else None.
    """
    title = article.get("title", "")
    url = article.get("url", "")

    # Keyword relevance filter
    title_lower = title.lower()
    if not any(kw in title_lower for kw in RISK_KEYWORDS):
        return None

    # Named entity recognition for supplier / country matching
    doc = nlp(title)
    entities = {ent.text.lower() for ent in doc.ents if ent.label_ in ("ORG", "GPE", "LOC")}
    matched_suppliers = [s for s in supplier_entity_list if s.lower() in entities]

    if not matched_suppliers:
        return None

    # Sentiment scoring
    result = sentiment_model(title[:512])[0]
    sentiment_score = (
        result["score"] if result["label"] == "POSITIVE" else -result["score"]
    )

    if sentiment_score < -0.6:
        return {
            "title": title,
            "url": url,
            "matched_suppliers": matched_suppliers,
            "sentiment_score": round(sentiment_score, 3),
            "risk_keywords_matched": [kw for kw in RISK_KEYWORDS if kw in title_lower],
            "alert_level": "HIGH" if sentiment_score < -0.8 else "MEDIUM",
        }

    return None
```

---

### 7.3 GNN Cascade Risk

#### Architecture

- Graph: supply network as directed graph (PyG HeteroData)
- Node features: HHI, TTR, EAL, country risk, tier
- Edge features: annual spend, commodity, Incoterm
- Task: node-level disruption probability + edge-level cascade probability
- Method: Graph Convolutional Network (GCN) with message passing, betweenness centrality for critical node identification

```python
# python/10_risk_management/ml/gnn_cascade/model.py

import torch
import torch.nn.functional as F
from torch_geometric.nn import GCNConv
from torch_geometric.data import Data
import networkx as nx
import numpy as np

class CascadeGNN(torch.nn.Module):
    """
    Graph Convolutional Network for supply chain cascade risk prediction.
    Node-level classification: P(node disrupted | source failure).
    """

    def __init__(self, node_features: int, hidden_dim: int = 64):
        super().__init__()
        self.conv1 = GCNConv(node_features, hidden_dim)
        self.conv2 = GCNConv(hidden_dim, hidden_dim)
        self.conv3 = GCNConv(hidden_dim, 1)

    def forward(self, x: torch.Tensor, edge_index: torch.Tensor) -> torch.Tensor:
        x = F.relu(self.conv1(x, edge_index))
        x = F.dropout(x, p=0.3, training=self.training)
        x = F.relu(self.conv2(x, edge_index))
        x = torch.sigmoid(self.conv3(x, edge_index))
        return x.squeeze(-1)


def identify_critical_nodes(G: nx.DiGraph, top_n: int = 10) -> list[tuple[str, float]]:
    """
    Identify critical supply network nodes by betweenness centrality.

    High betweenness nodes are choke points: their failure maximises cascade damage.

    Args:
        G: Directed supply network graph.
        top_n: Number of top critical nodes to return.

    Returns:
        List of (node_id, betweenness_centrality) tuples, sorted descending.
    """
    centrality = nx.betweenness_centrality(G, normalized=True, weight="annual_volume_usd")
    sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
    return sorted_nodes[:top_n]


def simulate_failure_cascade(
    G: nx.DiGraph,
    failed_node: str,
    cascade_depth: int = 3,
) -> set[str]:
    """
    Simulate cascade failure propagation from a single failed node.

    Uses BFS up to cascade_depth hops. Returns set of affected downstream nodes.
    """
    affected = set()
    queue = [(failed_node, 0)]
    visited = {failed_node}

    while queue:
        node, depth = queue.pop(0)
        if depth >= cascade_depth:
            continue
        for successor in G.successors(node):
            if successor not in visited:
                visited.add(successor)
                affected.add(successor)
                queue.append((successor, depth + 1))

    return affected
```

---

### 7.4 Bayesian Network for Risk Interdependency

#### Architecture

- Library: pgmpy (BSD-3-Clause)
- Nodes: categorical risk variables (e.g., SupplierFinancialHealth, GeopoliticalRisk, DeliveryRisk, QualityRisk)
- Edges: causal dependencies informed by domain expertise and historical data
- Inference: Variable Elimination for P(outcome | evidence)
- Use case: What-if scenario — "If geopolitical risk escalates to HIGH, what is the probability that Tier-1 delivery is disrupted?"

```python
# python/10_risk_management/ml/bayesian_network/model.py

from pgmpy.models import BayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
import pandas as pd

def build_supply_risk_bn() -> BayesianNetwork:
    """
    Build Bayesian Network for supply chain risk interdependency modelling.

    Variables (all binary: 0=LOW, 1=HIGH):
      GeopoliticalRisk -> SupplierAccess
      SupplierFinancialHealth -> SupplierAccess
      SupplierAccess -> DeliveryDisruption
      NaturalHazardExposure -> DeliveryDisruption
      DeliveryDisruption -> ProductionImpact
    """
    model = BayesianNetwork([
        ("GeopoliticalRisk", "SupplierAccess"),
        ("SupplierFinancialHealth", "SupplierAccess"),
        ("SupplierAccess", "DeliveryDisruption"),
        ("NaturalHazardExposure", "DeliveryDisruption"),
        ("DeliveryDisruption", "ProductionImpact"),
    ])

    # Prior probabilities
    cpd_geo = TabularCPD("GeopoliticalRisk", 2, [[0.75], [0.25]])
    cpd_fin = TabularCPD("SupplierFinancialHealth", 2, [[0.85], [0.15]])
    cpd_nat = TabularCPD("NaturalHazardExposure", 2, [[0.90], [0.10]])

    # P(SupplierAccess | GeopoliticalRisk, SupplierFinancialHealth)
    cpd_access = TabularCPD(
        "SupplierAccess", 2,
        [[0.95, 0.60, 0.50, 0.10],
         [0.05, 0.40, 0.50, 0.90]],
        evidence=["GeopoliticalRisk", "SupplierFinancialHealth"],
        evidence_card=[2, 2],
    )

    # P(DeliveryDisruption | SupplierAccess, NaturalHazardExposure)
    cpd_delivery = TabularCPD(
        "DeliveryDisruption", 2,
        [[0.98, 0.70, 0.40, 0.05],
         [0.02, 0.30, 0.60, 0.95]],
        evidence=["SupplierAccess", "NaturalHazardExposure"],
        evidence_card=[2, 2],
    )

    # P(ProductionImpact | DeliveryDisruption)
    cpd_prod = TabularCPD(
        "ProductionImpact", 2,
        [[0.90, 0.15],
         [0.10, 0.85]],
        evidence=["DeliveryDisruption"],
        evidence_card=[2],
    )

    model.add_cpds(cpd_geo, cpd_fin, cpd_nat, cpd_access, cpd_delivery, cpd_prod)
    assert model.check_model(), "Bayesian Network is invalid"
    return model


def what_if_query(
    model: BayesianNetwork,
    evidence: dict[str, int],
    target: str = "ProductionImpact",
) -> dict:
    """
    Run inference query on the Bayesian Network.

    Args:
        evidence: Dict of observed variable states, e.g. {"GeopoliticalRisk": 1}
        target: Variable to query.

    Returns:
        Dict with P(target=LOW) and P(target=HIGH).
    """
    infer = VariableElimination(model)
    result = infer.query([target], evidence=evidence, show_progress=False)
    return {
        f"P({target}=LOW)": round(float(result.values[0]), 4),
        f"P({target}=HIGH)": round(float(result.values[1]), 4),
    }
```

---

### 7.5 RL for BCP Response Optimisation

#### Architecture

- Framework: Ray RLlib + SimPy environment
- Algorithm: PPO (Proximal Policy Optimisation)
- State space: current supply gap %, buffer inventory days, TTR estimate, active disruption severity
- Action space (discrete, 4 actions):
  1. Activate buffer stock (draw down safety stock)
  2. Reroute shipments (alternate carrier / port)
  3. Dual-source activation (onboard second supplier)
  4. Air freight upgrade (expedite at premium cost)
- Reward: negative recovery cost (minimise total cost: lost revenue + mitigation spend)

```python
# python/10_risk_management/ml/rl_bcp/environment.py

import gymnasium as gym
import numpy as np
import simpy
from typing import Any

class BCPResponseEnv(gym.Env):
    """
    Gymnasium environment wrapping a SimPy supply chain disruption simulation.
    Used to train a PPO agent for optimal BCP response selection.
    """

    metadata = {"render_modes": []}

    ACTION_NAMES = [
        "activate_buffer_stock",
        "reroute_shipments",
        "dual_source_activation",
        "air_freight_upgrade",
    ]

    ACTION_COSTS_USD = [50_000, 200_000, 500_000, 350_000]
    ACTION_RECOVERY_REDUCTION_DAYS = [3, 5, 14, 7]

    def __init__(self, daily_revenue_usd: float = 500_000.0):
        super().__init__()
        self.daily_revenue_usd = daily_revenue_usd

        # State: [supply_gap_pct, buffer_days, ttr_estimate, disruption_severity]
        self.observation_space = gym.spaces.Box(
            low=np.array([0.0, 0.0, 0.0, 0.0], dtype=np.float32),
            high=np.array([1.0, 90.0, 180.0, 1.0], dtype=np.float32),
        )
        self.action_space = gym.spaces.Discrete(4)

        self._state = None
        self._ttr_remaining = 0.0
        self._total_cost = 0.0
        self._step_count = 0

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        # Random disruption scenario initialisation
        rng = self.np_random
        self._supply_gap = rng.uniform(0.3, 1.0)
        self._buffer_days = rng.uniform(5.0, 30.0)
        self._ttr_remaining = rng.uniform(14.0, 90.0)
        self._disruption_severity = rng.uniform(0.3, 1.0)
        self._total_cost = 0.0
        self._step_count = 0

        return self._get_obs(), {}

    def step(self, action: int):
        action_cost = self.ACTION_COSTS_USD[action]
        recovery_reduction = self.ACTION_RECOVERY_REDUCTION_DAYS[action]

        # Apply action effects
        self._ttr_remaining = max(0, self._ttr_remaining - recovery_reduction)
        self._buffer_days = max(0, self._buffer_days - 1)   # consume one day

        # Daily revenue loss from supply gap
        daily_loss = self._supply_gap * self.daily_revenue_usd
        step_cost = daily_loss + action_cost
        self._total_cost += step_cost

        # Recovery: reduce gap proportional to actions taken
        self._supply_gap = max(0, self._supply_gap - 0.05 * (action + 1))
        self._step_count += 1

        terminated = self._ttr_remaining <= 0 or self._supply_gap <= 0
        truncated = self._step_count >= 90

        # Reward: negative cost (agent minimises cost)
        reward = -step_cost / 1_000_000  # scale to [-1, 0] range

        return self._get_obs(), reward, terminated, truncated, {}

    def _get_obs(self) -> np.ndarray:
        return np.array([
            self._supply_gap,
            self._buffer_days / 90.0,          # normalised
            self._ttr_remaining / 180.0,        # normalised
            self._disruption_severity,
        ], dtype=np.float32)
```

**Training Configuration (Ray RLlib):**

```python
# python/10_risk_management/ml/rl_bcp/train_ppo.py

import ray
from ray.rllib.algorithms.ppo import PPOConfig

def train_bcp_agent(n_iterations: int = 200):
    ray.init(ignore_reinit_error=True)

    config = (
        PPOConfig()
        .environment(BCPResponseEnv)
        .training(
            lr=3e-4,
            gamma=0.99,
            lambda_=0.95,
            clip_param=0.2,
            train_batch_size=4000,
        )
        .rollouts(num_rollout_workers=4)
    )

    algo = config.build()
    for i in range(n_iterations):
        result = algo.train()
        if i % 20 == 0:
            mean_reward = result["episode_reward_mean"]
            print(f"Iteration {i:4d} | Mean Reward: {mean_reward:.3f}")

    checkpoint = algo.save()
    print(f"Checkpoint saved at: {checkpoint}")
    ray.shutdown()
    return checkpoint
```

---

## 8. Phase 5: Integration and Automation

**Duration:** 8 weeks
**Owner:** Data Engineer + Enterprise Architect

### 8.1 SAP GRC Integration

Connect the risk register to SAP GRC Process Control for automated control testing results and SAP Risk Management for risk register synchronisation.

```typescript
// src/departments/10-risk-management/services/SAPGRCAdapter.ts

import { RiskRegisterEntry } from "../domain/RiskRegister";

interface SAPGRCRisk {
  RISK_ID: string;
  RISK_NAME: string;
  GROSS_SCORE: number;
  NET_SCORE: number;
  CATEGORY: string;
  OWNER: string;
  STATUS: string;
}

export class SAPGRCAdapter {
  private readonly baseUrl: string;
  private readonly apiKey: string;

  constructor(baseUrl: string, apiKey: string) {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
  }

  async syncRiskToGRC(entry: RiskRegisterEntry): Promise<void> {
    const payload: SAPGRCRisk = {
      RISK_ID: entry.riskId,
      RISK_NAME: entry.title,
      GROSS_SCORE: entry.riskScore,
      NET_SCORE: (entry.residualLikelihood ?? entry.likelihood) *
                 (entry.residualImpact ?? entry.impact),
      CATEGORY: entry.category,
      OWNER: entry.riskOwnerId,
      STATUS: entry.status,
    };

    const response = await fetch(`${this.baseUrl}/api/v1/risks`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": this.apiKey,
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`SAP GRC sync failed: ${response.status} ${response.statusText}`);
    }
  }
}
```

### 8.2 Resilinc Integration

Resilinc provides sub-tier supplier site mapping and real-time disruption event webhooks. Ingest site-level events and create `RISK_IDENTIFIED` domain events automatically.

```python
# python/10_risk_management/integrations/resilinc_client.py

import httpx
import asyncio
from typing import AsyncGenerator

class ResilincClient:
    """
    Client for Resilinc Supplier Intelligence API.
    Streams disruption events for registered supplier sites.
    """

    BASE_URL = "https://api.resilinc.com/v3"

    def __init__(self, api_key: str, organisation_id: str):
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "X-Organisation-ID": organisation_id,
        }

    async def get_disruption_events(
        self,
        since_timestamp: str,
        severity_min: str = "MEDIUM",
    ) -> list[dict]:
        """Fetch disruption events since a given ISO 8601 timestamp."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/events",
                headers=self._headers,
                params={
                    "since": since_timestamp,
                    "severity_min": severity_min,
                    "limit": 500,
                },
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()["events"]

    async def get_supplier_site_mapping(
        self,
        supplier_duns: str,
    ) -> dict:
        """Retrieve all known sites for a supplier DUNS number."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/suppliers/{supplier_duns}/sites",
                headers=self._headers,
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()
```

### 8.3 Swiss Re CatNet Integration

Query natural catastrophe exposure for a geographic coordinate (supplier site location) to populate the `NaturalHazardExposure` node in the Bayesian Network.

```python
# python/10_risk_management/integrations/catnet_client.py

import httpx

HAZARD_CLASSES = ["earthquake", "flood", "windstorm", "hail", "wildfire", "tsunami"]

class CatNetClient:
    BASE_URL = "https://catnet-cr.swissre.com/api/v1"

    def __init__(self, api_key: str):
        self._headers = {"X-API-Key": api_key}

    def get_hazard_exposure(self, lat: float, lon: float) -> dict[str, str]:
        """
        Get natural hazard exposure classification for a GPS coordinate.

        Returns:
            Dict mapping hazard class to exposure level (LOW/MEDIUM/HIGH/VERY_HIGH).
        """
        with httpx.Client() as client:
            resp = client.get(
                f"{self.BASE_URL}/hazards",
                headers=self._headers,
                params={"lat": lat, "lon": lon},
                timeout=15.0,
            )
            resp.raise_for_status()
            data = resp.json()

        return {h: data.get(h, {}).get("level", "UNKNOWN") for h in HAZARD_CLASSES}
```

### 8.4 FEMA Disaster Data Integration

```python
# python/10_risk_management/integrations/fema_client.py

import httpx
import pandas as pd

FEMA_BASE = "https://www.fema.gov/api/open/v2"

def fetch_fema_disaster_declarations(
    state: str,
    disaster_type: str = "DR",  # DR = Major Disaster, EM = Emergency
    days_back: int = 365,
) -> pd.DataFrame:
    """
    Fetch FEMA major disaster declarations for a US state.

    Args:
        state: Two-letter US state code (e.g., 'TX', 'CA').
        disaster_type: FEMA disaster declaration type.
        days_back: Number of days of history to retrieve.

    Returns:
        DataFrame of disaster declarations with columns:
        disasterNumber, state, declarationDate, incidentType, title
    """
    from datetime import datetime, timedelta
    since = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%dT%H:%M:%SZ")

    with httpx.Client() as client:
        resp = client.get(
            f"{FEMA_BASE}/DisasterDeclarationsSummaries",
            params={
                "$filter": f"state eq '{state}' and declarationType eq '{disaster_type}' and declarationDate ge '{since}'",
                "$select": "disasterNumber,state,declarationDate,incidentType,declarationTitle",
                "$orderby": "declarationDate desc",
                "$top": 100,
            },
            timeout=30.0,
        )
        resp.raise_for_status()

    records = resp.json().get("DisasterDeclarationsSummaries", [])
    return pd.DataFrame(records)
```

### 8.5 Kafka Event Streaming Pipeline

All risk signals from external feeds publish to a Kafka topic. A consumer service processes them, runs the risk scoring pipeline, and emits domain events to the event store.

```
Topic: risk.signals.raw
  Partitioned by: signal_source (resilinc, gdelt, fema, catnet, bloomberg)

Topic: risk.events.assessed
  Partitioned by: risk_id

Topic: risk.escalations
  Partitioned by: severity_band
```

---

## 9. Phase 6: Continuous Improvement

**Duration:** Ongoing (from Month 18)

### 9.1 Model Drift Monitoring

| Model | Drift Metric | Monitoring Frequency | Retrain Trigger |
|-------|-------------|---------------------|----------------|
| LSTM Disruption | AUC-ROC on rolling 90-day holdout | Weekly | AUC < 0.70 |
| NLP EWS | Precision/Recall on labeled alerts | Monthly | Precision < 0.60 |
| GNN Cascade | Node prediction accuracy | Monthly | Accuracy < 0.75 |
| Bayesian Network | KL divergence on CPT updates | Quarterly | KL > 0.15 |
| RL BCP Agent | Mean episode reward | Monthly | Reward degrades > 15% |

### 9.2 After Action Reviews (AARs)

For every supply chain disruption event (regardless of severity), conduct a structured AAR within 10 business days:

1. Timeline reconstruction (event log from Kafka)
2. Detection time vs. target (KRI breach to alert)
3. Model performance: did LSTM predict the event?
4. BCP effectiveness: did RL agent recommendation match actual optimal action?
5. TTR vs. predicted TTR: model accuracy
6. Action items with owners and due dates

### 9.3 Risk Appetite Review Cadence

| Horizon | Review | Outcome |
|---------|--------|---------|
| Annual | Board Risk Committee | Update risk appetite statement, KRI thresholds |
| Semi-annual | Executive Risk Committee | Portfolio EAL review, major model retraining |
| Quarterly | Risk Director + CPO | HHI scan, supplier resilience review |
| Monthly | Risk Analyst | KRI dashboard, escalation report |
| Weekly | Automated | GDELT/Resilinc signal processing, LSTM inference |
| Daily | Automated | KRI computation, SAP GRC sync |

---

## 10. Technology Stack and Architecture

### 10.1 Architecture Diagram (Textual)

```
External Data Feeds
  [Resilinc] [Riskmethods] [Bloomberg] [GDELT] [Swiss Re CatNet] [FEMA]
        |
        v
  Kafka Topic: risk.signals.raw
        |
        v
  Signal Processing Service (Python)
    - NLP EWS pipeline
    - LSTM inference
    - GNN cascade scoring
    - Bayesian Network inference
        |
        v
  Risk Scoring Engine (Python)
    - 5x5 Risk Matrix
    - EAL computation
    - HHI scan
    - Bullwhip ratio
    - Monte Carlo
    - TTR/TTS analysis
        |
        v
  Kafka Topic: risk.events.assessed
        |
        v
  Risk Domain Event Store (PostgreSQL / Event Sourcing)
    - RiskIdentifiedEvent
    - RiskScoredEvent
    - RiskEscalatedEvent
        |
        v
  Read Models (CQRS Query Side)
    - Risk Register dashboard
    - Heat map view
    - KRI dashboard
    - Supplier concentration report
        |
        v
  [SAP GRC Sync]  [Alert/Email]  [BCP Trigger]
```

### 10.2 Deployment Architecture

| Component | Technology | Scaling |
|-----------|-----------|--------|
| Signal processors | Python FastAPI + Kafka Consumer | Horizontal (Kubernetes) |
| ML inference | PyTorch Serve / TorchScript | GPU node pool |
| Event store | PostgreSQL 15 + partitioning | Vertical + read replicas |
| Cache | Redis 7 (risk scores, KRI) | Redis Cluster |
| Streaming | Apache Kafka 3.5 | 3-broker cluster |
| Orchestration | Kubernetes 1.30 | Managed (EKS/GKE/AKS) |
| Monitoring | Prometheus + Grafana | Standard observability stack |

---

## 11. Change Management and Training

### 11.1 Stakeholder Impact Map

| Stakeholder | Change Impact | Engagement Strategy |
|------------|--------------|-------------------|
| CPO / CSCO | New risk reporting cadence, board escalation | Executive briefing, monthly dashboard |
| Category Managers | HHI alerts, dual-source mandates | Training workshop, KPI linkage |
| Procurement Analysts | Risk scoring in PO workflow | System training, SOP update |
| Supplier Managers | Resilinc data sharing requirements | Supplier communication template |
| Finance | EAL inputs for insurance captive sizing | Finance workshop |
| IT / Data Engineering | New Kafka pipelines, ML infrastructure | Technical design review |

### 11.2 Training Programme

| Module | Audience | Duration | Format |
|--------|---------|---------|--------|
| ISO 31000 Fundamentals | All SCM staff | 4 hours | e-learning |
| Risk Matrix and EAL | Risk Analysts | 1 day | instructor-led |
| KRI Dashboard Usage | Category Managers | 2 hours | e-learning |
| BCP Activation Protocol | All SCM leads | 4 hours | tabletop exercise |
| LSTM/GNN Model Interpretation | Risk Analysts, Data Engineers | 1 day | workshop |
| SAP GRC Risk Module | Risk Analysts | 2 days | vendor-led |

### 11.3 Communication Plan

- Month 1: Programme kick-off communication (CPO to all SCM staff)
- Month 3: Phase 1 go-live announcement; KRI dashboard access granted
- Month 6: Phase 2 go-live; risk scoring embedded in PO approval workflow
- Month 12: ML/AI models go live; town hall briefing with Q&A
- Monthly: Risk newsletter (top 5 risks, KRI trends, mitigation status)

---

## 12. Implementation KPIs

### Programme Delivery KPIs

| KPI | Baseline | Month 6 Target | Month 12 Target | Month 18 Target |
|----|---------|---------------|----------------|----------------|
| Risk register coverage (% of Tier-1 suppliers scored) | 30% | 80% | 100% | 100% |
| KRI monitoring coverage | 0 KRIs | 8 KRIs live | 12 KRIs live | 15 KRIs live |
| Mean time to detect disruption (days) | 14 | 7 | 3 | 2 |
| LSTM model AUC-ROC | N/A | N/A | 0.78 | 0.82 |
| Commodities with HHI scan | 0% | 60% | 100% | 100% |
| Commodities with HHI > 2500 dual-sourced | 0% | 20% | 60% | 85% |
| BCP test frequency | Annual | Quarterly | Monthly (automated) | Continuous (RL) |
| Risk-adjusted disruption cost reduction | 0% | 10% | 30% | 55% |

### Operational Risk KPIs (Steady State)

| KPI | Target | Measurement |
|----|--------|------------|
| Risk register currency (% reviewed on schedule) | >= 95% | Monthly |
| KRI breach-to-alert latency | < 4 hours | Automated |
| CRITICAL risk escalation compliance | 100% within 4 hours | Event log |
| SAP GRC sync success rate | >= 99.5% | Integration monitoring |
| Model uptime (LSTM, GNN inference) | >= 99.9% | Kubernetes health |
| Supplier visibility Tier 1 | 100% | Resilinc |
| Supplier visibility Tier 2 | >= 70% | Resilinc |

---

## 13. Risk and Mitigation

### Programme Risks

| Risk | Likelihood | Impact | Score | Mitigation |
|-----|-----------|--------|-------|-----------|
| Supplier data sharing refusal (Tier-1) | Medium | High | 12 | Include data sharing in supplier contract renewal; use Resilinc for passive mapping |
| ML model poor performance (AUC < 0.70) | Medium | Medium | 9 | Maintain rule-based fallback; human-in-the-loop review for all HIGH alerts |
| Kafka pipeline failure during disruption | Low | Critical | 10 | Multi-AZ deployment; dead letter queue; daily health check |
| SAP GRC API deprecation | Low | Medium | 6 | Vendor SLA clause; maintain manual sync fallback |
| GDELT API rate limiting | Medium | Low | 6 | Implement exponential backoff; cache 15-minute windows |
| RL agent unstable policy (reward hacking) | Low | High | 10 | Constrained PPO; human override always available |
| Data quality issues in procurement master | High | High | 20 | Data quality sprint in Phase 0; automated HHI re-computation daily |
| Organisational change resistance | Medium | Medium | 9 | Executive sponsorship visible; KPI linkage to category manager bonuses |

### Residual Risk Acceptance

The Board Risk Committee must formally accept residual risks where mitigation cost exceeds expected benefit. EAL analysis (Section 6.2) provides the financial basis for this decision. All accepted risks with score >= 10 must be re-assessed within 90 days.

---

## 14. Timeline Summary

| Phase | Name | Duration | Start | End | Key Deliverables |
|-------|------|---------|-------|-----|-----------------|
| 0 | Assessment and AS-IS | 4 weeks | Month 0 | Month 1 | Supply network map, gap analysis, risk inventory |
| 1 | Foundation and Master Data | 6 weeks | Month 1 | Month 2.5 | Risk register schema, event store, data dictionary |
| 2 | Process Standardisation | 8 weeks | Month 2.5 | Month 4.5 | SCOR process map, KRI framework, escalation protocol |
| 3 | Mathematical Models | 10 weeks | Month 4 | Month 6.5 | 5x5 matrix, EAL, HHI, Bullwhip, Monte Carlo, TTR/TTS, SimPy |
| 4 | ML/AI Pipeline | 14 weeks | Month 6 | Month 9.5 | LSTM, NLP EWS, GNN, Bayesian Network, RL BCP agent |
| 5 | Integration and Automation | 8 weeks | Month 9 | Month 11 | SAP GRC, Resilinc, Riskmethods, GDELT, CatNet, FEMA |
| 6 | Continuous Improvement | Ongoing | Month 12 | Ongoing | Drift monitoring, AARs, risk appetite review |

**Total programme duration to steady state:** 18 months
**Team size:** 6 FTE (Risk Director, 2x Risk Analyst, Data Engineer, ML Engineer, SCM Change Manager)
**Estimated programme cost:** USD 2.8M (Year 1), USD 1.2M (Year 2 run cost)
**Estimated annual benefit:** USD 8–12M (disruption cost avoidance + insurance captive optimisation)
**Payback period:** 18 months

---

## 15. References

- ISO 31000:2018, *Risk Management — Guidelines*. Geneva: International Organization for Standardization.
- ISO 28000:2022, *Security and Resilience — Supply Chain Security Management Systems*. Geneva: ISO.
- ASCM. *SCOR Digital Standard*. Chicago: Association for Supply Chain Management, 2019.
- Chopra, S. and Meindl, P. *Supply Chain Management: Strategy, Planning, and Operation*, 6th ed. Pearson, 2016.
- Sheffi, Y. and Rice, J.B. "A Supply Chain View of the Resilient Enterprise." *MIT Sloan Management Review*, 47(1), 2005.
- Lee, H.L., Padmanabhan, V. and Whang, S. "Information Distortion in a Supply Chain: The Bullwhip Effect." *Management Science*, 43(4), 546–558, 1997.
- Chen, F., Drezner, Z., Ryan, J.K. and Simchi-Levi, D. "Quantifying the Bullwhip Effect in a Simple Supply Chain." *Management Science*, 46(3), 436–443, 2000.
- Caldara, D. and Iacoviello, M. "Measuring Geopolitical Risk." *American Economic Review*, 112(4), 1194–1225, 2022.
- Herfindahl, O.C. *Concentration in the Steel Industry*. Columbia University PhD thesis, 1950.
- US Department of Justice. *Horizontal Merger Guidelines*, 2010. Section 5.3: Market Concentration.
- Allianz Global Corporate and Specialty. *AGCS Safety and Shipping Review*, 2023.
- Bode, C. and Wagner, S.M. "Structural Drivers of Upstream Supply Chain Complexity." *Journal of Purchasing and Supply Management*, 21(3), 2015.
- Baltic Exchange. *Baltic Dry Index Methodology*, 2023.
- GDELT Project. *GDELT 2.0 API Documentation*, https://blog.gdeltproject.org/gdelt-2-0-our-global-world-in-realtime/.
- Swiss Re. *CatNet API Technical Reference*, 2024.
- US FEMA. *OpenFEMA API Documentation*, https://www.fema.gov/about/openfema/api.
- Vaswani, A. et al. "Attention Is All You Need." *NeurIPS*, 2017. (Attention mechanism used in LSTM variant.)
- Schulman, J. et al. "Proximal Policy Optimization Algorithms." *arXiv:1707.06347*, 2017.
- Koller, D. and Friedman, N. *Probabilistic Graphical Models: Principles and Techniques*. MIT Press, 2009.
- Leskovec, J., Sosic, R. "SNAP: A General-Purpose Network Analysis and Graph Mining Library." *ACM TIST*, 8(1), 2016.
- McKinsey and Company. "Supply Chain Resilience: Seven Action Items for Boards." McKinsey Operations Practice, 2022.
- Gartner. "Supply Chain Risk Management Technology Guide." Gartner Research G00764831, 2023.
