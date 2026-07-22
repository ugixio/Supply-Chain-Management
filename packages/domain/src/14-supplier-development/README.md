# 14 — Supplier Development & ESG / Sustainability

> **SCOR-DS Process**: Enable (sE) | **GHG Protocol** | **ISO 14001:2015** | **ISO 45001:2018** | **Owner**: Supplier Development Manager

The Supplier Development & ESG department develops the capabilities of strategic and critical suppliers to drive continuous performance improvement, joint innovation, and a sustainable supply chain that meets the highest Environmental, Social, and Governance (ESG) standards. It owns the ESG scoring model (E 40 % + S 40 % + G 20 %), GHG Scope 3 Category 1 tracking, EU Deforestation Regulation compliance, EU CSRD reporting support, Science Based Targets (SBTi) alignment, and structured supplier development programs (PDPs).

---

## Table of Contents

1. [ESG Framework](#1-esg-framework)
2. [Domain Files](#2-domain-files)
3. [Key Business Rules](#3-key-business-rules)
4. [Mathematical Models](#4-mathematical-models)
5. [Recommended ML Models](#5-recommended-ml-models)
6. [KPIs & Targets](#6-kpis--targets)
7. [Supplier Development Program (PDP)](#7-supplier-development-program-pdp)
8. [Applicable Standards & Regulations](#8-applicable-standards--regulations)
9. [Integration Points](#9-integration-points)
10. [Roles](#10-roles)
11. [References](#11-references)

---

## 1. ESG Framework

### Environmental (40 % weight)

| Area | Applicable Regulation / Standard | Key Metric |
|---|---|---|
| Climate change / GHG | GHG Protocol Scope 3 Cat. 1; SBTi 1.5°C | tCO₂e per unit produced |
| Renewable energy | RE100 / SBTi | % renewable electricity |
| Chemical substances | EU REACH 1907/2006; Stockholm Convention | SVHCs eliminated |
| Waste management | Basel Convention; ISO 14001 | % waste recycled |
| Biodiversity | Kunming-Montreal GBF 2022 | Sensitive areas impacted |
| Water stewardship | GRI 303; CDP Water Security | m³ per unit produced |
| Deforestation | EU Deforestation Reg. 2023/1115 | % deforestation-free |

### Social (40 % weight)

| Area | Standard | Minimum Requirement |
|---|---|---|
| Forced & child labour | UFLPA; ILO Conventions 29, 105, 138, 182 | Zero tolerance; annual audit |
| Occupational safety | ISO 45001:2018 | LTIFR < 1.0 per million hours |
| Working hours | ILO; local labour law | ≤ 60 hours/week including overtime |
| Living wage | Living Wage Foundation (by country) | Gap to living wage = 0 % |
| Diversity & inclusion | UN Global Compact Principle 6 | Documented program; female mgmt % tracked |
| Worker voice / grievance | CSDDD Art. 9 | Operational grievance mechanism |

### Governance (20 % weight)

| Area | Requirement |
|---|---|
| Anti-corruption | FCPA + UK Bribery Act — zero-tolerance policy; annual training |
| Transparency | Public sustainability disclosure (GRI / CSRD format) |
| Business ethics | Supplier Code of Conduct signed before first PO |
| Conflict of interest | Annual declaration by all senior supplier contacts |
| Data security | ISO 27001 certification for suppliers with data access |

---

## 2. Domain Files

### `domain/SustainabilityRecord.ts`

| Export | Description |
|---|---|
| `EnvironmentalMetrics` | `{ scope1_tCO2e, scope2_tCO2e, scope3Cat1_tCO2e, waterM3, wasteRecycledPct, renewableEnergyPct, deforestationFree, reachSVHCsEliminated }` |
| `SocialMetrics` | `{ forcedLabourAuditPassed, ltifr, avgHoursPerWeek, livingWageGapPct, femaleManagementPct, grievanceMechanismActive }` |
| `GovernanceMetrics` | `{ antiCorruptionPolicyAdopted, codeOfConductSigned, publicSustainabilityReport, conflictOfInterestDeclared }` |
| `SustainabilityRecord` | Composite record: `{ supplierId, assessmentDate, environmental, social, governance, eScore, sScore, gScore, overallESGScore, esgRating }` |
| `createSustainabilityRecord(supplier, metrics)` | Factory: computes E (40 %) + S (40 %) + G (20 %) → overall score → ESG rating AAA–CCC |

---

## 3. Key Business Rules

1. **ESG Rating Gate** — Suppliers rated `CCC` (overall ESG score < 40) are automatically placed on `PROBATION` status in the Supplier Scorecard, regardless of delivery or quality performance. Suppliers rated `BB` or below must have an active Supplier Development Program (PDP).
2. **SBTi Commitment Required** — All `STRATEGIC` suppliers (Kraljic quadrant: high profit impact, high supply risk) must submit a Science Based Target commitment within 12 months of classification. Without it, they cannot advance beyond `CONDITIONAL` status.
3. **Deforestation-Free Documentation** — For the seven regulated commodities (soy, beef, palm oil, wood, cocoa, coffee, rubber), geolocation data and deforestation-free certification are mandatory for EU market supply from 2024.
4. **LTIFR Threshold** — Supplier LTIFR > 5.0 triggers an immediate safety audit. LTIFR > 10.0 triggers supply suspension pending corrective action (ISO 45001).
5. **Living Wage Compliance** — `livingWageGapPct > 20 %` triggers a formal improvement plan. Suppliers with persistent gap > 20 % over two consecutive assessment cycles are escalated to CSDDD adverse impact remediation.
6. **Scope 3 Data Quality** — Primary activity data (quantity purchased × supplier-specific emission factor) is required for all Tier-1 suppliers above €500 K annual spend. Secondary (spend-based) data is acceptable only for Tier-2+.
7. **Soft-Delete Only** — Sustainability records, ESG assessments, and PDP milestones are never hard-deleted. 5-year retention aligned with CSDDD Art. 23 and CSRD documentation requirements.

---

## 4. Mathematical Models

### 4.1 ESG Scoring Model

```
Overall_ESG_score = E_score × 0.40 + S_score × 0.40 + G_score × 0.20

--- Environmental Score (E_score, base 50 points) ---
Base score                                        :  50
+ SBTi commitment submitted and validated         : +15
+ Net-zero target aligned to 1.5°C               : +10
+ Renewable energy ≥ 50 % of electricity          : +10
+ Deforestation-free certification (if applicable): +10
+ Waste recycling ≥ 75 %                          :  +5
+ Full supply chain traceability system           :  +5
+ Zero hazardous waste to landfill                :  +5

--- Social Score (S_score, 0–100) ---
Forced labour audit passed (no critical findings) : +25
LTIFR < 1.0 (world-class)                        : +20
Living wage gap = 0 %                             : +20
Working hours ≤ 48 h/week average                 : +15
Female management ≥ 30 %                          : +10
Active grievance mechanism                        : +10

--- Governance Score (G_score, 0–100) ---
Anti-corruption policy adopted + training         : +30
Code of Conduct signed                            : +25
Public sustainability report published            : +25
Conflict of interest declarations current         : +20

--- ESG Rating Scale ---
AAA : ≥ 90     AA : ≥ 80     A : ≥ 70
BBB : ≥ 60     BB : ≥ 50     B : ≥ 40     CCC : < 40
```

### 4.2 GHG Scope 3 Category 1 (Purchased Goods & Services)

```
Scope3_Cat1_tCO2e = Σ_i (quantity_purchased_i × emission_factor_i)

where:
  quantity_purchased_i  : tonnes or units purchased from supplier i
  emission_factor_i     : kgCO2e per unit (from ecoinvent, GHG Protocol datasets,
                          or supplier-specific primary data)

Preferred data hierarchy:
  1. Supplier-specific primary data (mass balance or life cycle inventory)
  2. Industry-average data (ecoinvent v3.x)
  3. Spend-based ($ spend × EEIO factor) — least preferred

Annual reduction target: −4.2 % per year (SBTi 1.5°C pathway)
```

Reference: GHG Protocol Corporate Value Chain (Scope 3) Standard, WRI/WBCSD, 2011.

### 4.3 Supplier Carbon Intensity Tracking

```
Carbon_Intensity_i = Scope3_Cat1_tCO2e_i / Units_produced_i

Track year-over-year:
  Δ_intensity = (Intensity_t − Intensity_{t-1}) / Intensity_{t-1} × 100

SBTi requires: Δ_intensity ≤ −4.2 % per year (absolute or intensity-based)

Carbon intensity fed into TCO model in Dept. 11 as carbon pricing cost:
  Carbon_cost = Intensity_i × Carbon_price_EUR_per_tCO2e × Volume_purchased
```

### 4.4 LTIFR — Lost Time Injury Frequency Rate (ISO 45001)

```
LTIFR = (Number_of_lost_time_injuries × 1 000 000) / Hours_worked

Example:
  5 LTIs in 2 000 000 hours worked → LTIFR = 2.5

Benchmarks (manufacturing, ISO 45001 framework):
  < 1.0  : World-class
  1.0–3.0: Acceptable — continuous improvement required
  3.0–5.0: Below average — action plan mandatory
  > 5.0  : Critical — immediate audit triggered
```

### 4.5 Deforestation Risk Score (EU Reg. 2023/1115)

```
Risk_score = f(commodity_type, country_risk, geolocation_available,
               deforestation_free_certified, third_party_audit)

PROHIBITED for EU market entry:
  commodity ∈ {soy, beef, palm_oil, wood, cocoa, coffee, rubber}
  AND (geolocation NOT available OR deforestation_free_cert = false)

Low risk:
  commodity ∈ regulated list
  AND geolocation verified
  AND satellite monitoring clear (12-month lookback)
  AND third_party_audit = passed
```

### 4.6 Living Wage Gap

```
Living_wage_gap% = (Living_wage_standard_country − Actual_avg_supplier_wage)
                   / Living_wage_standard_country × 100

Target: gap% = 0  (supplier pays at or above living wage)

Living wage standard: Living Wage Foundation national benchmarks
  Updated annually; country-specific rates used

Gap > 20 % → formal improvement plan
Gap > 0 %  → tracked quarterly; included in ESG S_score calculation
```

---

## 5. Recommended ML Models

### 5.1 Satellite + ML — Deforestation Monitoring (EU Reg. 2023/1115)

Random Forest classifier trained on multispectral Sentinel-2 imagery (10 m resolution, 5-day revisit). Classifies land-cover change (deforestation, degradation, regrowth) within buffered polygons around supplier sourcing locations. Generates monthly deforestation alerts linked to commodity supply chains. Required for mandatory due diligence under EU Deforestation Regulation for all seven regulated commodities.

- **Libraries**: Google Earth Engine Python API, `rasterio`, `scikit-learn RandomForestClassifier`
- **Reference**: Hansen, M.C. et al., "High-Resolution Global Maps of 21st-Century Forest Cover Change," *Science* 342:850–853, 2013.
- **Alert threshold**: > 0.5 ha deforestation within 10 km of sourcing polygon → immediate supplier escalation

### 5.2 NLP — ESG Data Extraction from Sustainability Reports

DistilBERT model fine-tuned on CSRD/GRI-format sustainability reports. Automatically extracts quantitative KPIs (GHG emissions, LTIFR, water usage, diversity metrics), qualitative commitments (SBTi targets, net-zero pledges), and certifications from supplier annual sustainability disclosures. Eliminates manual data entry from hundreds of PDF reports per year.

- **Libraries**: HuggingFace `distilbert-base-uncased`, `pdfplumber` for PDF extraction
- **Accuracy target**: > 90 % field extraction accuracy vs. manual review on test corpus

### 5.3 Graph ML — Scope 3 Emission Attribution

Graph Attention Network (GAT) models the supplier network as a weighted directed graph. Propagates GHG emissions through supply tiers (Tier-1 → Tier-2 → raw material origin) and allocates Scope 3 Category 1 emissions to the purchasing organisation by supplier contribution, accounting for multi-product allocation and co-product credit.

- **Libraries**: PyTorch Geometric, NetworkX (graph construction)
- **Use case**: Identify which Tier-2 commodities contribute most to Scope 3 Cat. 1; prioritise interventions

### 5.4 K-Means Clustering — Supplier ESG Maturity Segmentation

Groups suppliers by ESG maturity profile to design tailored development programs. Features: overall ESG score, individual E/S/G dimension scores, years of sustainability reporting, SBTi status, LTIFR trend.

| Cluster | Profile | PDP Focus |
|---|---|---|
| 1 — Laggards | ESG < 50; no reporting | Basic compliance: Code of Conduct, minimum standards |
| 2 — Developing | ESG 50–70; partial reporting | GHG measurement; ISO 14001; safety improvement |
| 3 — Progressing | ESG 70–85; full reporting | SBTi submission; living wage; renewable energy |
| 4 — Leaders | ESG ≥ 85; SBTi committed | Joint innovation; circular economy; supply chain advocacy |

- **Libraries**: `scikit-learn KMeans`; `silhouette_score` for optimal k; PCA for 2D visualisation

### 5.5 Regression — ESG Program ROI Quantification

Quantifies the financial return of ESG investment: reduced regulatory risk (probability × penalty), access to EU market revenue (EUDR compliance), lower cost of capital (ESG-linked financing spread), and reduced CSDDD remediation cost.

```
ROI = (ΔRevenue_at_risk_avoided + ΔCost_of_capital + ΔPenalty_avoided)
      / Program_investment_EUR

Features: ESG_score_delta, program_cost_EUR, revenue_exposed_to_EU_regs,
          supplier_credit_rating, regulatory_penalty_probability
```

- **Libraries**: `statsmodels OLS`, `scikit-learn ElasticNet` (regularised for small samples)

---

## 6. KPIs & Targets

| KPI | Formula | Target | Alert |
|---|---|---|---|
| **ESG Rating — avg Strategic suppliers** | Mean ESG score, Kraljic Strategic quadrant | ≥ AA (≥ 80) | Any Strategic supplier < BBB |
| **Scope 3 Cat. 1 Reduction %** | `(Emissions_t − Emissions_{t-1}) / Emissions_{t-1} × 100` | −4.2 % per year (SBTi) | < −2 % annual progress |
| **Suppliers with SBTi Commitment %** | `Suppliers with validated SBTi / Strategic suppliers × 100` | ≥ 80 % by 2027 | < 50 % |
| **Deforestation-Free Compliance %** | `Compliant commodity suppliers / Total × 100` | 100 % | Any non-compliant for EU market |
| **LTIFR (avg Tier-1)** | `Mean LTIFR across all Tier-1 supplier assessments` | < 1.5 | > 3.0 |
| **Living Wage Gap % (avg)** | `Mean living_wage_gap_pct across assessed suppliers` | 0 % | > 10 % |
| **Female Management % (avg)** | `Mean female_mgmt_pct across assessed suppliers` | ≥ 30 % | < 20 % |
| **PDP Completion Rate** | `PDPs completed on schedule / PDPs planned × 100` | ≥ 90 % | < 75 % |
| **ESG Audit Coverage — Strategic** | `Audited Strategic suppliers / Total Strategic × 100` | 100 % | < 90 % |
| **Supplier Development ROI** | `(Savings + risk avoided) / PDP investment` | ≥ 5:1 | < 3:1 |

---

## 7. Supplier Development Program (PDP)

```
Phase 1 — Diagnosis (Months 1–2)
  ✓ Initial ESG assessment using createSustainabilityRecord()
  ✓ Supplier Scorecard baseline (OTD, Quality, Commercial, Soft)
  ✓ Gap identification: ESG score vs. target; LTIFR vs. benchmark
  ✓ Shared findings with supplier senior management

Phase 2 — Improvement Plan (Month 2–3)
  ✓ SMART objectives with milestones and accountable owners
  ✓ Resource allocation: technical support, training, co-investment
  ✓ Signed PDP agreement including consequences of non-achievement

Phase 3 — Implementation (Months 3–11)
  ✓ Monthly progress reviews (virtual + quarterly on-site)
  ✓ Training workshops: Lean/Six Sigma, ISO 14001/45001, REACH, GHG Protocol
  ✓ Best-practice sharing with other supplier cohort members
  ✓ KPI tracking against PDP milestones

Phase 4 — Evaluation & Graduation (Month 12)
  ✓ Final ESG assessment and Scorecard evaluation
  ✓ Delta vs. baseline documented for ROI calculation
  ✓ Supplier graduated to target Scorecard rating (APPROVED / PREFERRED)
  ✓ 12-month continuous improvement plan agreed
```

---

## 8. Applicable Standards & Regulations

| Standard / Regulation | Scope | Implementation |
|---|---|---|
| **GRI Standards** (2021) | Global sustainability reporting | Supplier disclosure template |
| **GHG Protocol Scope 3** (WRI/WBCSD 2011) | Value chain emissions | `CarbonCalculator` service |
| **SBTi** (1.5°C pathway) | Science-based emission targets | Commitment tracker in PDP |
| **EU CSRD** Dir. 2022/2464 | Corporate sustainability reporting | Tier-1 data collection for CSRD double materiality |
| **EU Deforestation Reg.** 2023/1115 | 7 commodities deforestation-free | Geolocation + satellite monitoring |
| **ISO 14001:2015** | Environmental management systems | Preferred certification for STRATEGIC suppliers |
| **ISO 45001:2018** | Occupational health & safety | Required for manufacturing suppliers |
| **UN SDGs** 8, 12, 13, 17 | Decent work; responsible consumption; climate; partnerships | KPI alignment in annual reporting |
| **UN Global Compact** (10 Principles) | Human rights, labour, environment, anti-corruption | Supplier Code of Conduct basis |
| **CDP** | Climate and water disclosure | Annual questionnaire for Tier-1 strategic suppliers |
| **TCFD** | Climate-related financial risk disclosure | Risk scenario integration with Dept. 10 |

---

## 9. Integration Points

| Department | Data Flow |
|---|---|
| **02 Supplier Management** | ESG `SustainabilityRecord` feeds 10 % soft-metrics dimension of Supplier Scorecard |
| **09 Compliance** | CSDDD adverse impact findings from Dept. 09 trigger PDP remediation actions here |
| **10 Risk Management** | ESG risk items (deforestation, forced labour, carbon) feed the 5×5 Risk Matrix as `ESG` category |
| **11 Finance** | Carbon cost (Scope 3 × carbon price) included in TCO; ESG-linked financing spread tracked |
| **12 S&OP** | Supplier ESG-driven capacity constraints (e.g., deforestation suspension) shared in Supply Review |

---

## 10. Roles

| Role | Responsibility |
|---|---|
| **Supplier Development Manager** | Program strategy; strategic supplier relationships; PDP governance |
| **Sustainability Manager** | ESG scoring; CSDDD environmental dimension; Scope 3 reporting; CSRD data collection |
| **ESG Analyst** | Data collection, `SustainabilityRecord` maintenance, ESG dashboard |
| **Supplier Development Engineer** | On-site technical assistance; Lean/Six Sigma workshops at supplier facilities |
| **Diversity & Inclusion Specialist** | MBE/WBE/SME supplier programs; diversity spend tracking |
| **Carbon Accounting Specialist** | GHG Protocol Scope 3 Cat. 1 inventory; SBTi target tracking; PCAF alignment |

---

## 11. References

1. GHG Protocol / WRI & WBCSD, **Corporate Value Chain (Scope 3) Accounting and Reporting Standard**, Washington DC, 2011.
2. European Parliament and Council, **Directive (EU) 2022/2464** (CSRD) on corporate sustainability reporting, *OJ L* 322, December 2022.
3. European Parliament and Council, **Regulation (EU) 2023/1115** on deforestation-free supply chains, *OJ L* 150, June 2023.
4. ISO, **ISO 14001:2015** — Environmental management systems: Requirements with guidance for use, Geneva, 2015.
5. Science Based Targets initiative (SBTi), **Corporate Net-Zero Standard v1.2** and **FLAG Guidance v1.0**, 2023.
