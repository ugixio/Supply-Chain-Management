# 10 — Risk Management

## Overview

Manages supply chain risks through a 5×5 matrix (probability × impact), supplier concentration (HHI), bullwhip effect, expected annual loss (EAL), and business continuity plans (BCP) aligned with ISO 22301:2019 (RTO/RPO/MTPD).

---

## Department KPIs

| KPI | Target | Source |
|-----|--------|--------|
| Bullwhip Ratio | ≈ 1.0 (target) | Lee et al. (1997) |
| HHI per commodity | < 1,500 (competitive) | US DOJ |
| Unmitigated CRITICAL risks | 0 | ISO 31000 |
| BCP tests completed / year | ≥ 1 per active BCP | ISO 22301 |
| RTO achievement % | 100% vs. commitments | ISO 22301 |
| Total portfolio EAL | Quarterly monitoring | Internal |

---

## Standards

| Standard | Scope |
|----------|-------|
| ISO 31000:2018 | Risk management framework |
| ISO 22301:2019 | Business Continuity Management |
| McKinsey SC Resilience Framework (2021) | Resilience playbook |
| MIT CTL Supply Chain Resilience | Academic research |

---

## Department Files

| File | Responsibility |
|------|---------------|
| `models/RiskModel.ts` | RiskCategory (9 types), calculateRiskLevel() 5×5, RiskItem, herfindahlHirschmanIndex(), bullwhipRatio(), expectedAnnualLoss(), DisruptionScenario |
| `domain/BusinessContinuityPlan.ts` | ISO 22301: RTO/RPO/MTPD, BCPAction (sequenced with dependencies), BCPTest (TABLETOP/FUNCTIONAL/FULL_SCALE), createBCP(), addTestResult() |

---

## Risk Categories (9)

`SUPPLIER_DISRUPTION` · `DEMAND_VOLATILITY` · `LOGISTICS_DISRUPTION` · `GEOPOLITICAL` · `NATURAL_DISASTER` · `CYBER_SECURITY` · `REGULATORY_COMPLIANCE` · `FINANCIAL_CREDIT` · `QUALITY_FAILURE`

---

## Applied Mathematical Models

### 1. Risk Matrix 5×5 (ISO 31000)

```
Risk_Score = Probability(1-5) × Impact(1-5)

Levels:
   1 –  8 → LOW      (green)
   9 – 14 → MEDIUM   (yellow)
  15 – 19 → HIGH     (orange)
  20 – 25 → CRITICAL (red)

Probability: 1=Rare(<5%), 2=Unlikely(5-20%), 3=Possible(20-50%),
             4=Likely(50-80%), 5=Almost_certain(>80%)
Impact: 1=Negligible, ..., 5=Catastrophic
```

Ref: ISO 31000:2018 Annex A.

---

### 2. EAL — Expected Annual Loss

```
EAL_i = P_annual_i × Financial_impact_i

EAL_total = Σ EAL_i  (all risks in the portfolio)

Mitigation priority = EAL_i / Mitigation_cost_i  (control ROI)
```

---

### 3. HHI — Herfindahl-Hirschman Index

```
HHI = Σ (market_share_i)² × 10,000    [i = supplier of commodity X]

HHI < 1,500   → low concentration (competitive)
1,500–2,500   → moderate concentration
HHI > 2,500   → high concentration → supplier monopoly risk
```

Used to detect excessive dependency on a single supplier per commodity. Ref: US DOJ Merger Guidelines.

---

### 4. Bullwhip Effect Ratio (Lee, Padmanabhan & Whang 1997)

```
BWE = Var(orders_upstream) / Var(demand_downstream)

BWE ≈ 1.0 → efficient SC (no amplification)
BWE > 1.5 → warning signal
BWE > 2.0 → severe distortion → order policy review

Causes: batching, price fluctuation, shortage gaming, forecast error
```

Ref: Lee, Padmanabhan & Whang (1997) *MIT Sloan Management Review*.

---

### 5. RTO / RPO / MTPD (ISO 22301)

```
RTO  = Recovery Time Objective   (maximum time to restore operations)
RPO  = Recovery Point Objective  (maximum acceptable data loss)
MTPD = Maximum Tolerable Period of Disruption

BCP constraint: recovery_time ≤ RTO ≤ MTPD
```

---

### 6. Monte Carlo for Loss Distribution

```
For each simulation s (1..100,000):
  1. Sample p_i ~ Beta(α_i, β_i)          [probability of disruption i]
  2. Sample impact_i ~ LogNormal(μ_i, σ_i) [financial impact]
  3. loss_s = Σ p_i × impact_i

VaR_95 = percentile(losses, 95)
VaR_99 = percentile(losses, 99)
```

Ref: Chopra & Meindl (2016) Ch.12.

---

## Recommended Machine Learning Models

### 1. LSTM — Disruption Prediction

**Type**: Supervised time series  
**How it works**: Input: 36 months of macro indicators (manufacturing PMI, Baltic Dry Index, commodity prices, geopolitical GPR indices, climate events). Output: P(disruption) per risk category over the next 30/90 days.  
**Output**: `{risk_category, horizon_days, probability, confidence_interval}`  
**Library**: TensorFlow, Prophet, FRED API (macro data)  
**Ref**: Hochreiter & Schmidhuber (1997).

---

### 2. NLP — Early Warning System

**Type**: NLP + text classification  
**How it works**: Monitors 50+ sources (Reuters/Bloomberg news, Twitter/X, GDELT, regulatory filings). Detects contextualised keywords: strike, flood, sanction, factory fire, port closure. Calculates severity score per supplier/region.  
**Output**: real-time alert with `{supplier_id, risk_type, severity, source_url}`.  
**Library**: HuggingFace, GDELT API, spaCy  
**Ref**: Radford et al. (2019) GPT-2, OpenAI.

---

### 3. Graph Neural Networks — Cascade Risk

**Type**: GNN (Message Passing)  
**How it works**: Models the SC as a directed graph. Message propagation simulates how a failure in Tier-2 cascades to Tier-1 and final assembly. Identifies single points of failure (nodes with high betweenness centrality).  
**Output**: node criticality map; `cascade_risk_score` per supplier.  
**Library**: PyTorch Geometric, NetworkX  
**Ref**: Kipf & Welling (2017) ICLR *Semi-Supervised Classification with GCN*.

---

### 4. Bayesian Networks — Risk Interdependency

**Type**: Probabilistic graphical model  
**How it works**: Models conditional dependencies between risks (a geopolitical event simultaneously raises P(supplier_failure) and P(logistics_disruption)). Computes the joint probability distribution of the risk portfolio.  
**Output**: P(combined scenario) — informs hedging decisions and buffer stock levels.  
**Library**: pgmpy, pomegranate, bnlearn (R)  
**Ref**: Pearl (1988) *Probabilistic Reasoning in Intelligent Systems*, Morgan Kaufmann.

---

### 5. RL — BCP Response Optimisation

**Type**: Reinforcement Learning (simulation)  
**How it works**: An agent executes BCP actions in a simulated disruption environment. State: `(disruption_type, severity, time_elapsed, resources_remaining)`. Action: next `BCPAction` to execute. Reward: `-downtime - cost + customer_satisfaction`. Learns the optimal response sequence that minimises RTO.  
**Output**: optimised response policy per disruption type.  
**Library**: Ray RLlib, SimPy (discrete event simulation)  
**Ref**: Ambulkar, Blackhurst & Grawe (2015) *Journal of Operations Management*.

---

## References

- ISO 31000:2018 *Risk Management — Guidelines*
- ISO 22301:2019 *Business Continuity Management Systems*
- Lee, H.L., Padmanabhan, V. & Whang, S. (1997) *The Bullwhip Effect in Supply Chains*, MIT Sloan Management Review
- Chopra, S. & Meindl, P. (2016) *Supply Chain Management*, 6th Ed. Ch.12
- US DOJ/FTC (2010) *Horizontal Merger Guidelines*
