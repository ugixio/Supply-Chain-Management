# Demand Planning & Forecasting — Implementation Playbook

**Organisation:** Global Multinational Manufacturing Corporation  
**Scale:** €50B revenue · 40 countries · SAP S/4HANA backbone  
**Version:** 1.0  
**Date:** 2026-06-20  
**Classification:** Internal — Confidential  
**Prepared for:** Chief Supply Chain Officer / SVP Demand Planning  

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Prerequisites & Dependencies](#2-prerequisites--dependencies)
3. [Phase 0: Assessment & AS-IS Analysis](#3-phase-0-assessment--as-is-analysis)
4. [Phase 1: Foundation & Master Data](#4-phase-1-foundation--master-data)
5. [Phase 2: Process Standardisation & Core Analytics](#5-phase-2-process-standardisation--core-analytics)
6. [Phase 3: Mathematical Models](#6-phase-3-mathematical-models)
7. [Phase 4: ML/AI Pipeline](#7-phase-4-mlai-pipeline)
8. [Phase 5: Integration & Automation](#8-phase-5-integration--automation)
9. [Phase 6: Continuous Improvement & Centre of Excellence](#9-phase-6-continuous-improvement--centre-of-excellence)
10. [Technology Stack & Architecture](#10-technology-stack--architecture)
11. [Change Management & Training](#11-change-management--training)
12. [KPIs to Measure Implementation Success](#12-kpis-to-measure-implementation-success)
13. [Risk & Mitigation](#13-risk--mitigation)
14. [Timeline Summary Table](#14-timeline-summary-table)
15. [References](#15-references)

---

## 1. Executive Summary

### Business Imperative

This organisation operates across 40 countries with a €50B revenue base, managing tens of thousands of active SKUs across manufacturing, distribution, and retail channels. Current demand planning processes are fragmented: each regional planning team operates independently with inconsistent methodologies, producing forecast accuracy variance of 15–30 percentage points across business units. The consequence is a dual burden — excess safety stock in slow-moving categories (estimated €1.2B in trapped working capital) while simultaneously experiencing service failures (fill rate 88–91%, versus world-class target of 97.5%+) in fast-moving, seasonally volatile segments.

The global S&OP process lacks a unified statistical baseline, forcing planners to spend 60–70% of their time on data preparation rather than insight generation. Promotional uplift is estimated manually with no systematic lift modelling, and new product introductions rely entirely on planner intuition rather than analogous SKU transfer learning.

### Strategic Objective

Implement a fully integrated, enterprise-grade Demand Planning & Forecasting capability that delivers:

- **Forecast accuracy improvement:** +12–18 percentage points in WMAPE across all planning horizons
- **Working capital reduction:** €200–400M through right-sized safety stock
- **Service level improvement:** Fill rate from ~90% to ≥97.5% (OTIF ≥ 95%)
- **Planner productivity:** Shift planner time allocation from 60% data work / 40% judgement to 20% data work / 80% judgement and exception management
- **Standardisation:** Single forecasting methodology hierarchy deployed across all 40 countries, governed by a Centre of Excellence (CoE)

### Implementation Approach

A six-phase programme spanning 18 months, executed by a joint team of internal supply chain professionals and external implementation partners. The approach is deliberately phased to derisk execution: mathematical statistical models are implemented and validated before ML/AI models are introduced, and integration with SAP S/4HANA / IBP is hardened before automation is activated.

### Investment Summary

| Component | Estimated Investment |
|-----------|---------------------|
| Software licences (IBP, data platform) | €8–12M over 3 years |
| Implementation services (SI partner) | €6–9M |
| Internal resource commitment (FTEs) | 12–18 FTE over 18 months |
| Training & change management | €1.5–2.5M |
| Infrastructure (cloud, data pipelines) | €2–4M |
| **Total (3-year TCO)** | **€18–28M** |
| **Expected NPV (5-year)** | **€120–180M** |

---

## 2. Prerequisites & Dependencies

### 2.1 Organisational Prerequisites

Before any technical implementation begins, the following organisational conditions must be verified and, where absent, remediated:

**Executive Sponsorship (Non-Negotiable)**
- CSCO or equivalent C-suite executive must be named as programme sponsor with formal charter authority
- Steering committee meeting cadence: monthly at minimum, with escalation path to CEO for cross-functional blockers
- Dedicated programme budget approved and ring-fenced — do not proceed without budget commitment in writing

**S&OP Process Maturity**
- An S&OP process must already exist, even if immature. If no S&OP exists, implement the process skeleton (demand review, supply review, executive S&OP) in parallel — minimum 2 monthly cycles before Phase 1 go-live
- Sales and Finance must commit to providing promotional calendars, new product launch plans, and financial targets as structured data inputs — not ad hoc emails

**Data Governance**
- A named Data Owner for each master data domain (SKU, customer, location, calendar) must be identified
- Data quality SLAs defined: completeness, accuracy, timeliness targets per domain
- GDPR / data residency requirements mapped for all 40 countries — particularly relevant for customer POS data (Phase 5)

### 2.2 Technical Prerequisites

**SAP S/4HANA Landscape**
- S/4HANA release: minimum 2020 (FPS01) for IBP integration; 2022 or later recommended
- SAP Integration Suite (formerly CPI) licensed and operational — required for IBP ↔ S/4HANA data flows
- Material Master data completeness: minimum 95% completeness on MRP-relevant fields (MRP type, lot size, safety stock, lead time) before Phase 1 begins
- SAP Business Warehouse (BW/4HANA) or equivalent data warehouse operational — demand history extraction depends on this

**Data History Requirements**
- Minimum 24 months of daily/weekly sales history per SKU × Location combination for seasonal model training
- 36 months preferred; 48 months required for Holt-Winters cross-validation (see Phase 3)
- History must be cleaned: returns, intercompany transfers, and extraordinary one-time sales (disaster restocking, plant closures) must be flagged and available for exclusion

**Infrastructure**
- Cloud platform tenancy established (Azure, AWS, or GCP — technology stack section details preferred architecture)
- Data lake / lakehouse layer available (Azure Data Lake Gen2 or AWS S3 + Glue) for ML feature store
- Python 3.11+ runtime environment with GPU access for LSTM / TFT training (minimum: 4x NVIDIA A10G or equivalent)
- MLflow or equivalent experiment tracking tool deployed before Phase 4

**Team Resourcing**
| Role | FTE | Phase Active |
|------|-----|-------------|
| Programme Director | 1.0 | All |
| Demand Planning Lead (Process) | 1.0 | All |
| SAP IBP Functional Lead | 2.0 | 1–5 |
| Data Engineer | 3.0 | 0–5 |
| Data Scientist / ML Engineer | 3.0 | 3–6 |
| Change Manager | 1.0 | 0–6 |
| Regional Planning Champions (40 countries) | 40 × 0.2 FTE | 1–6 |
| Business Analyst | 2.0 | 0–3 |

### 2.3 Dependency Map

```
[SAP S/4HANA data extraction]
        |
        v
[Data Lake / Cleansed History]  <-- [POS feeds] [Weather API] [Promo calendar]
        |
        v
[Phase 1: Master Data Foundation]
        |
        v
[Phase 2: Statistical Baseline]  -->  [Phase 3: Math Models]
                                              |
                                              v
                                    [Phase 4: ML/AI Pipeline]
                                              |
                                              v
                                    [Phase 5: SAP IBP Integration]
                                              |
                                              v
                                    [Phase 6: CoE + Continuous Improvement]
```

---

## 3. Phase 0: Assessment & AS-IS Analysis

**Duration:** 6–8 weeks  
**Owner:** Programme Director + Business Analyst team  
**Gate criterion:** AS-IS assessment report signed off by CSCO; data quality score ≥ 60% (proceed with remediation plan if below)

### 3.1 Demand History Audit

**Step 1 — Extract and profile demand history**

Pull a minimum 36-month daily sales history from SAP S/4HANA (SD module, billing documents) for every active SKU × Ship-to Location combination. Profile the extract across the following dimensions:

| Dimension | Metric | Acceptable Threshold |
|-----------|--------|---------------------|
| Completeness | % SKUs with ≥ 24 months history | ≥ 80% |
| Zero-demand periods | % weeks with zero sales (per SKU) | Flag if > 40% (intermittent) |
| Outlier rate | % data points > 3σ from rolling mean | Document; do not delete yet |
| Return/credit note netting | % lines with credit memos included | Must be ≤ 5% unneted |
| Intercompany transfer exclusion | % lines from intercompany customers | Must be excluded from baseline |

**Step 2 — Classify the demand portfolio**

Before choosing any forecasting model, classify every SKU on two axes:
- **Volume:** Annual units sold (H = high, M = medium, L = low)
- **Volatility:** Coefficient of Variation (CV = σ/μ) over the history period

This produces the ABC-XYZ matrix (detailed in Phase 3). The AS-IS classification provides the baseline against which Phase 3 outcomes are measured.

**Step 3 — Identify intermittent / lumpy demand**

Apply Syntetos-Boylan classification:
- Compute average inter-demand interval (ADI): average number of periods between non-zero demand
- Compute squared CV (CV²) of non-zero demand sizes
- Classify:
  - ADI < 1.32 AND CV² < 0.49 → **Smooth** (use SES/SMA)
  - ADI ≥ 1.32 AND CV² < 0.49 → **Intermittent** (use Croston's method)
  - ADI < 1.32 AND CV² ≥ 0.49 → **Erratic** (use SBA or bootstrapping)
  - ADI ≥ 1.32 AND CV² ≥ 0.49 → **Lumpy** (use Teunter-Syntetos-Babai / simulation)

Record the percentage of portfolio in each quadrant — this drives model selection architecture in Phase 3 and Phase 4.

### 3.2 Current Process Assessment

**Structured interviews** (1.5 hours each) with the following stakeholder groups per region:
- Demand Planners (individual contributors)
- S&OP facilitators / Planning Managers
- Sales / Commercial leads responsible for forecast input
- Finance BP responsible for demand reconciliation to financial plan
- Supply Planning leads who consume the demand plan

**Assessment dimensions (rate 1–5 for each):**

| Dimension | Questions to Probe |
|-----------|--------------------|
| Process standardisation | Are forecasting methods documented? Are they consistent across planners? |
| Statistical baseline usage | Do planners start from a statistical forecast, or build manually? |
| Consensus process | How are commercial overrides documented and tracked? |
| Forecast accuracy measurement | Is MAPE/WMAPE measured? At what granularity? |
| New product introduction | What process governs NPI forecasting? Analogous SKU used? |
| Promotional planning | Are promotion uplifts modelled or estimated manually? |
| Exception management | What triggers a planner to review a SKU? Volume or accuracy threshold? |
| System landscape | What tools are used today? (Excel, APO DP, custom Python, etc.) |

**Output:** AS-IS Process Maturity Score (Gartner IBP Maturity Model, Levels 1–5). Most organisations at this scale score Level 2–3. Target post-implementation: Level 4 (Integrated Business Planning with statistical and ML baseline).

### 3.3 System Landscape Mapping

Document every system that currently produces, consumes, or transforms demand data:

```
Data Sources:           SAP S/4HANA (SD) | ERP legacy systems | Excel workbooks
                               |
Transformation:         BW/4HANA extractors | Manual CSV exports
                               |
Forecasting Tools:      SAP APO DP (if existing) | Excel | Tableau
                               |
Consumption:            SAP S/4HANA (MRP) | SAP IBP (if existing) | APS tools
```

Flag integration gaps, manual handoffs, and data latency issues. These gaps become the remediation backlog for Phase 5.

### 3.4 Baseline Forecast Accuracy Benchmarking

Before any improvement initiative begins, establish the true AS-IS forecast accuracy. This is frequently understated by planning teams because:
1. Accuracy is measured at an aggregate level (total company) rather than SKU × Location
2. Accuracy measurement excludes zero-demand periods (inflates apparent accuracy)
3. Overrides are not tracked, so planner "improvement" to statistical forecasts is invisible

**Correct measurement protocol:**
1. Extract last 12 months of consensus forecasts (M+1 through M+12 buckets) from the planning system or archived spreadsheets
2. Match to actual sales at SKU × Ship-to × Week granularity
3. Compute WMAPE (weighted MAPE) where weight = actual sales volume (see Phase 3 for formula)
4. Decompose by: product family, region, demand volatility class, horizon (M+1, M+3, M+6)

**Benchmark targets (world-class, Gartner 2024):**

| Horizon | World-Class WMAPE | Good | Acceptable |
|---------|------------------|------|------------|
| M+1 | < 15% | < 20% | < 30% |
| M+3 | < 20% | < 28% | < 40% |
| M+6 | < 30% | < 40% | < 55% |

Document AS-IS performance against these benchmarks. The gap defines the value case.

### 3.5 Phase 0 Deliverables

- [ ] AS-IS Demand History Quality Report (per region, per BU)
- [ ] Demand Portfolio Classification (Smooth / Intermittent / Erratic / Lumpy %)
- [ ] Process Maturity Assessment Report
- [ ] System Landscape Map with integration gaps identified
- [ ] Baseline Forecast Accuracy Report (WMAPE by horizon, by region)
- [ ] Data Remediation Backlog (prioritised, with owners and deadlines)
- [ ] Business Case Update (refined based on actual AS-IS performance gap)

---

## 4. Phase 1: Foundation & Master Data

**Duration:** 8–10 weeks (partially overlaps Phase 0 weeks 6–8)  
**Owner:** SAP IBP Functional Lead + Data Engineering  
**Gate criterion:** Data quality score ≥ 85% on all master data domains; SAP IBP Planning Area activated; ABC-XYZ classification complete and loaded

### 4.1 Demand History Cleansing Pipeline

Raw history extracted from SAP SD must pass through a deterministic cleansing pipeline before any model training. This pipeline must be reproducible, auditable, and re-runnable on each monthly planning cycle.

**Pipeline steps (execute in order):**

```python
# Pseudocode — implement as Pandas pipeline with full audit trail

def cleanse_demand_history(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleanse raw SAP SD billing document history for demand planning use.
    All exclusions must be logged to an audit table, not silently dropped.
    """
    # Step 1: Exclude intercompany sales (customer account group = 0012 in SAP)
    df = exclude_intercompany(raw_df)

    # Step 2: Net returns against forward sales (match by material + period)
    df = net_returns(df)

    # Step 3: Exclude extraordinary events (flag in SAP using a Z-field or manual input table)
    df = exclude_flagged_extraordinary(df)

    # Step 4: Outlier detection and replacement
    # Method: IQR-based per SKU × Location per calendar month
    # Replace outliers with median of ±3 surrounding periods (NOT zero, NOT blank)
    df = replace_outliers_iqr(df, multiplier=2.5)

    # Step 5: Disaggregate to planning granularity (weekly buckets if daily source)
    df = aggregate_to_planning_bucket(df, freq='W-MON')

    # Step 6: Fill structural zeros vs true zeros
    # True zero: product was listed and available, demand = 0
    # Structural zero: product was not listed (delisted, pre-launch) — exclude from history
    df = mark_structural_zeros(df, listing_calendar)

    return df
```

**Audit requirement:** Every row exclusion or modification must write to a `demand_cleansing_audit` table recording: SKU, Location, Period, Original Value, Adjusted Value, Reason Code, Timestamp, Pipeline Version.

### 4.2 Master Data Governance

**SKU Master (Material Master in SAP)**

The following fields must be populated with validated data for every active SKU before the planning system can generate a statistical forecast:

| SAP Field | Planning Purpose | Governance Rule |
|-----------|-----------------|-----------------|
| Base Unit of Measure | Forecast unit alignment | Cannot be changed after SKU activation |
| MRP Type | Determines if IBP forecast is consumed | Set PD (MRP) or VB (reorder point) — not blank |
| Planning Horizon | How far forward IBP plans | Minimum 12 weeks; set by product family |
| ABC Indicator | Drives review frequency | Auto-calculated monthly by classification engine |
| Shelf Life (MHDRZ) | FEFO picking, expiry demand adjustment | Mandatory for food, pharma, cosmetics |
| Procurement Lead Time | Safety stock calculation input | Review quarterly with Procurement |
| Lot Size (LOSGR) | EOQ or minimum order quantity | Review annually |

**Location Hierarchy**

SAP IBP planning is driven by a Supply Chain Network (SCN) model. The location hierarchy must reflect the physical supply chain, not the legal entity / cost centre hierarchy used in Finance:

```
Global
└── Region (Europe / Americas / APAC / MEA)
    └── Country
        └── Distribution Centre / Plant
            └── Ship-to Customer (for retail / key account level forecasting)
```

Verify that every DC and plant has a geocoded location in the master data (required for weather API integration in Phase 5).

**Planning Calendar**

Establish a global fiscal calendar and map it to the ISO 8601 week standard:
- Define fiscal week start day (recommend Monday for global consistency)
- Map all 40 country public holiday calendars — these are inputs to Prophet model in Phase 4
- Define planning bucket: weekly buckets for operational horizon (0–13 weeks), monthly for tactical (M+3 to M+18)

### 4.3 ABC-XYZ Classification Engine

The ABC-XYZ matrix is the foundation for all downstream decisions: which forecasting model to apply, what safety stock method to use, what review frequency to set, and which SKUs receive ML model attention.

**ABC Classification (by value/volume contribution)**

Sort all active SKUs descending by annual revenue (or units — define one metric and apply consistently):

| Class | Cumulative % of Revenue | Typical % of SKUs | Review Frequency |
|-------|------------------------|-------------------|-----------------|
| A | 0–80% | ~20% | Weekly |
| B | 80–95% | ~30% | Bi-weekly |
| C | 95–100% | ~50% | Monthly |

**XYZ Classification (by demand volatility)**

Compute Coefficient of Variation (CV = σ / μ) using the last 12 months of cleansed weekly demand:

| Class | CV Threshold | Demand Pattern | Forecasting Approach |
|-------|-------------|----------------|---------------------|
| X | CV < 0.10 | Very stable | SMA or SES with high alpha |
| Y | 0.10 ≤ CV < 0.25 | Moderate variability | Holt / Holt-Winters |
| Z | CV ≥ 0.25 | High variability | ML models / safety stock buffer |

**Policy matrix (combined ABC-XYZ):**

| | X (Stable) | Y (Moderate) | Z (Volatile) |
|--|-----------|-------------|-------------|
| **A (High Value)** | AX: Tight control, low SS, SES | AY: Holt-Winters, medium SS | AZ: ML model, high SS, weekly review |
| **B (Mid Value)** | BX: SES, standard SS | BY: Holt or SMA, standard SS | BZ: Holt-Winters or ML |
| **C (Low Value)** | CX: SMA, min-max | CY: SMA or reorder point | CZ: Lumpy demand model or manual |

Load the ABC-XYZ classification into SAP IBP as a custom attribute on the product master. Configure IBP to automatically assign forecasting models based on this classification (see Phase 2).

### 4.4 Demand Segmentation Beyond ABC-XYZ

ABC-XYZ is necessary but insufficient for a portfolio of this size and complexity. Overlay the following additional segmentation dimensions:

**Life Cycle Stage**
- INTRODUCTION: < 6 months since launch — use analogous SKU transfer or ARIMA on sparse data
- GROWTH: 6–18 months — build history, transition from analogue to statistical
- MATURITY: > 18 months, stable — full statistical / ML model applicable
- DECLINE: sales trending down > 15% YoY for 2 consecutive quarters — apply trend dampening
- PHASEOUT: formally flagged for discontinuation — freeze replenishment, run down stock

**Channel Segmentation**
- Retail/Grocery (high volume, promotional, seasonal)
- Foodservice (contract-driven, less volatile but event-dependent)
- Industrial B2B (lumpy, project-driven)
- E-commerce DTC (high frequency, long-tail SKUs, returns-adjusted)
- Export / Regulated (Incoterms-sensitive, longer lead times)

Each channel requires different promotional lift models, different safety stock parameters, and different forecast horizon priorities.

### 4.5 Phase 1 Deliverables

- [ ] Cleansed demand history database (36 months, all SKUs × Locations, audit trail)
- [ ] Master data completeness report: ≥ 95% on all planning-critical fields
- [ ] ABC-XYZ classification loaded into SAP IBP
- [ ] Life cycle stage classification for all active SKUs
- [ ] Channel segmentation applied
- [ ] SAP IBP Planning Area and Supply Chain Network model activated
- [ ] Planning calendar (52-week ISO fiscal) configured in IBP
- [ ] Data quality dashboard live (monitored weekly)

---

## 5. Phase 2: Process Standardisation & Core Analytics

**Duration:** 8 weeks  
**Owner:** Demand Planning Lead + Regional Planning Champions  
**Gate criterion:** Global S&OP process design signed off; statistical baseline running in IBP for ≥ 1 pilot region; forecast accuracy measurement dashboard live

### 5.1 Global S&OP Process Design

Define a single, globally consistent S&OP process that all 40 countries follow. Allow regional customisation only within defined guardrails.

**Standard Monthly S&OP Calendar (weeks within the month):**

| Week | Activity | Owner | Output |
|------|----------|-------|--------|
| W1 (days 1–5) | Statistical baseline generation | System (IBP automated) | Unconstrained statistical forecast |
| W1 (days 3–5) | Data review: outliers, new launches flagged | Demand Planner | Cleansed baseline |
| W2 (days 1–3) | Commercial input: promotions, NPIs, account wins/losses | Sales / Commercial | Demand assumptions loaded into IBP |
| W2 (days 4–5) | Demand Review meeting | Planning Manager + Sales | Consensus demand plan |
| W3 (days 1–3) | Supply review: capacity constraints, supplier constraints | Supply Planning | Constrained supply plan |
| W3 (days 4–5) | Pre-S&OP: gap analysis, scenarios | Planning Director | Scenario options for leadership |
| W4 (days 1–2) | Executive S&OP: approve plan, resolve gaps | CSCO + CFO + Sales VP | Approved demand/supply plan |
| W4 (days 3–5) | Plan release to MRP / procurement | System (IBP → S/4HANA) | Production/purchase orders generated |

**Override governance rules (mandatory, enforced in IBP workflow):**
1. Every override to the statistical forecast requires a Reason Code from a controlled list
2. Override magnitude limits by role: Planner ≤ ±20%, Manager ≤ ±40%, Director unlimited
3. All overrides are logged with user ID, timestamp, justification, and original statistical value
4. Retrospective override accuracy tracked: if planner systematically worsens the statistical forecast (negative override value-add), this triggers a coaching review

### 5.2 Forecast Accuracy Measurement Framework

Implement a standardised accuracy measurement methodology before deploying any models. Measurement must be:
- Automated (not manual) — extracted from IBP actuals vs forecast comparison
- At the correct granularity — SKU × Ship-to × Week (not aggregated)
- Using WMAPE as primary KPI (not simple MAPE — see Phase 3 for formulas)
- Measured at multiple horizons: M+1, M+3, M+6, M+12

**Accuracy waterfall dashboard (implement in Power BI or SAP Analytics Cloud):**

```
Total WMAPE
├── By Region
│   ├── By Country
│   │   └── By Product Family
├── By Demand Class (A/B/C)
├── By Volatility Class (X/Y/Z)
├── By Life Cycle Stage
├── Statistical Forecast Accuracy (pre-override)
└── Consensus Forecast Accuracy (post-override)
```

The gap between statistical and consensus accuracy is **Override Value-Add** — a critical metric for coaching and governance. Positive value-add justifies the override; negative value-add means the statistical model should have been trusted.

### 5.3 Exception Management Configuration

In a portfolio of this scale (potentially 50,000+ active SKU × Location combinations), planners cannot review every line. Configure IBP exception management to surface only lines requiring human attention:

**Exception triggers (configure in IBP Alert Management):**

| Exception Type | Trigger Condition | Priority | Action |
|---------------|-------------------|----------|--------|
| Forecast spike | Forecast > 3σ above 13-week rolling average | High | Planner review and confirm/override |
| Accuracy deterioration | WMAPE > 40% for 3 consecutive weeks | High | Model re-fit trigger |
| New product (no history) | SKU < 8 weeks of sales history | High | Manual forecast or analogue assignment |
| Promotion not captured | Promo planned in calendar but not reflected in forecast | High | Promotional lift model run |
| Phase-out risk | Sales declining > 20% MoM for 2 months | Medium | Life cycle flag review |
| Slow mover | CV² > 1.0 AND ADI > 2.0 (lumpy) | Medium | Switch to spare parts model |
| Model drift | Forecast bias (ME) > 15% for 4 consecutive weeks | Medium | Re-calibrate alpha/beta parameters |
| Inventory mismatch | Statistical SS < current physical stock × 0.5 | Low | SS policy review |

### 5.4 Phase 2 Deliverables

- [ ] Global S&OP process design document (RACI, calendar, escalation paths)
- [ ] IBP S&OP workflow configured with override governance
- [ ] Forecast accuracy dashboard live (WMAPE by dimension, updated weekly)
- [ ] Exception management rules configured in IBP
- [ ] Override tracking report operational
- [ ] Pilot region (recommend largest European market) running live S&OP cycle

---

## 6. Phase 3: Mathematical Models

**Duration:** 10–12 weeks  
**Owner:** Data Science Lead + Demand Planning Lead  
**Gate criterion:** All statistical models validated in backtesting (WMAPE improvement vs. AS-IS); safety stock policy deployed for at least one pilot DC; models running in production for 2 consecutive monthly cycles

### 6.1 Simple Moving Average (SMA)

**When to use:** CX and BX SKUs (high volume, very stable demand, CV < 0.10). Also used as a benchmark/baseline against which all other models are compared. If a model cannot beat SMA on your data, it should not be used.

**Mathematical definition:**

```
F(t+1) = (1/N) × Σ[i=0 to N-1] D(t-i)

Where:
  F(t+1) = forecast for period t+1
  N       = window length (number of periods)
  D(t-i)  = actual demand i periods ago
```

**Window selection criteria:**

The optimal window length N depends on demand characteristics. Use the following decision process:

1. **Test candidate windows:** N ∈ {4, 8, 13, 26} weeks
2. **For each N, perform time-series cross-validation:**
   - Use expanding window: train on periods 1–24, test on period 25; train on 1–25, test on 26; etc.
   - Compute WMAPE for each test step
   - Average WMAPE across all test steps = CV score for that N
3. **Select N with minimum average WMAPE**
4. **Default recommendation by demand class:**
   - AX: N = 4 (responsive to recent demand, high value so freshness matters)
   - BX: N = 8
   - CX: N = 13 (stable, less sensitive to noise)

**Cold-start protocol (< N periods of history):**

When a SKU has fewer periods of history than the selected window length:
- Weeks 1–3: Return 0 (system cannot forecast, flag as manual)
- Weeks 4–7: Use all available periods (e.g., N=4 for week 5 means use 4 actual periods)
- Week N+: Switch to full SMA window
- Assign analogue SKU if available (see Phase 4 NPI section) to use analogue history as proxy

**Update cadence:**

SMA is a rolling calculation — it updates automatically each period as new actuals arrive. No re-fitting required. Monitor accuracy weekly; if WMAPE exceeds threshold for 3 consecutive periods, trigger model review (possible demand pattern shift from X to Y or Z class).

**Implementation note:**

```typescript
// src/departments/03-demand-planning/algorithms/Forecasting.ts
export function sma(history: number[], window: number): number {
  if (history.length < window) {
    // Cold-start: use available periods with warning
    const available = history.length;
    if (available < 4) return 0; // Insufficient history
    const partial = history.slice(-available);
    return partial.reduce((a, b) => a + b, 0) / available;
  }
  const relevant = history.slice(-window);
  return relevant.reduce((a, b) => a + b, 0) / window;
}
```

### 6.2 Simple Exponential Smoothing (SES)

**When to use:** AX, AY, BX, BY SKUs with stationary demand (no trend, no seasonality). SES gives more weight to recent observations — appropriate when demand can shift without a sustained trend.

**Mathematical definition:**

```
F(t+1) = α × D(t) + (1 - α) × F(t)

Equivalently (error-correction form, more intuitive for practitioners):
F(t+1) = F(t) + α × [D(t) - F(t)]
        = F(t) + α × e(t)

Where:
  α    = smoothing parameter (0 < α < 1)
  D(t) = actual demand in period t
  F(t) = forecast for period t
  e(t) = forecast error in period t
```

**Interpretation of alpha:** High α (→ 1.0) means the model reacts quickly to recent demand but is noisy. Low α (→ 0.0) means the model is stable but slow to adapt. α = 0.2–0.3 is typical for moderate-stability demand.

**Alpha parameter calibration — Nelder-Mead optimisation:**

Do NOT set alpha manually or use arbitrary defaults. Optimise per SKU × Location:

```python
from scipy.optimize import minimize
import numpy as np

def ses_forecast(alpha: float, history: np.ndarray) -> np.ndarray:
    """Generate SES one-step-ahead forecasts for given alpha."""
    n = len(history)
    forecasts = np.zeros(n)
    forecasts[0] = history[0]  # initialisation: F(1) = D(1)
    for t in range(1, n):
        forecasts[t] = alpha * history[t-1] + (1 - alpha) * forecasts[t-1]
    return forecasts

def ses_sse(alpha_arr: np.ndarray, history: np.ndarray) -> float:
    """Sum of squared errors — objective function for minimisation."""
    alpha = alpha_arr[0]
    if not (0.01 <= alpha <= 0.99):
        return 1e10  # penalty for out-of-bounds
    forecasts = ses_forecast(alpha, history)
    errors = history - forecasts
    return np.sum(errors ** 2)

def optimise_alpha(history: np.ndarray) -> float:
    """Optimise SES alpha via Nelder-Mead (gradient-free, robust)."""
    result = minimize(
        ses_sse,
        x0=[0.2],          # initial guess
        args=(history,),
        method='Nelder-Mead',
        options={'xatol': 1e-6, 'fatol': 1e-6, 'maxiter': 1000}
    )
    return float(np.clip(result.x[0], 0.01, 0.99))
```

**Alternatively — grid search** (simpler, parallelisable at scale):

```python
def grid_search_alpha(history: np.ndarray, 
                      grid: np.ndarray = np.arange(0.05, 1.0, 0.05)) -> float:
    """Grid search over alpha values, minimise SSE."""
    best_alpha, best_sse = 0.2, np.inf
    for alpha in grid:
        sse = ses_sse([alpha], history)
        if sse < best_sse:
            best_sse = sse
            best_alpha = alpha
    return best_alpha
```

Grid search is preferred at scale (10,000+ SKUs) because it is embarrassingly parallel and produces reproducible results. Use Nelder-Mead only when higher precision is needed (A-class SKUs).

**Initialisation:**

The initial forecast F(1) significantly impacts the first N periods of accuracy. Three options:
1. **F(1) = D(1):** Simple but vulnerable to first-period outliers
2. **F(1) = mean(D(1:M)):** Use mean of first M periods (recommended M = min(6, len/4))
3. **Backcasting (most rigorous):** Run SES backwards through history, use convergence point as F(1)

For operational use, method 2 with M = 6 is the recommended default.

### 6.3 Holt's Linear Exponential Smoothing (Double Exponential Smoothing)

**When to use:** AY, BY SKUs with a clear linear trend but no seasonality. Also appropriate for newly growing product categories. If trend is detected (linear regression slope significantly non-zero at p < 0.05), use Holt over SES.

**Mathematical definition:**

```
Level:   L(t) = α × D(t) + (1 - α) × [L(t-1) + T(t-1)]
Trend:   T(t) = β × [L(t) - L(t-1)] + (1 - β) × T(t-1)
Forecast: F(t+h) = L(t) + h × T(t)

Where:
  α = level smoothing parameter (0 < α < 1)
  β = trend smoothing parameter (0 < β < 1)
  h = forecast horizon (periods ahead)
  L(t) = smoothed level at period t
  T(t) = smoothed trend at period t
```

**Joint alpha/beta optimisation:**

Optimise α and β simultaneously. The parameter space is 2-dimensional, so grid search becomes O(n²):

```python
def holt_sse(params: list, history: np.ndarray) -> float:
    alpha, beta = params
    if not (0.01 <= alpha <= 0.99 and 0.01 <= beta <= 0.99):
        return 1e10
    n = len(history)
    # Initialisation: L(0) = D(0), T(0) = D(1) - D(0)
    L = history[0]
    T = history[1] - history[0] if len(history) > 1 else 0.0
    sse = 0.0
    for t in range(1, n):
        F_t = L + T
        e_t = history[t] - F_t
        sse += e_t ** 2
        L_new = alpha * history[t] + (1 - alpha) * (L + T)
        T = beta * (L_new - L) + (1 - beta) * T
        L = L_new
    return sse

def optimise_holt(history: np.ndarray) -> tuple[float, float]:
    result = minimize(
        holt_sse,
        x0=[0.2, 0.1],
        args=(history,),
        method='Nelder-Mead',
        options={'xatol': 1e-6, 'fatol': 1e-6, 'maxiter': 2000}
    )
    alpha, beta = np.clip(result.x, 0.01, 0.99)
    return float(alpha), float(beta)
```

**Trend damping for long horizons:**

Holt's unconstrained trend can produce unrealistic extrapolations at horizons of M+6 or beyond (a product cannot grow at the same rate indefinitely). Apply Gardner-McKenzie (1985) trend dampening:

```
F(t+h) = L(t) + (φ + φ² + ... + φʰ) × T(t)
        = L(t) + φ(1 - φʰ)/(1 - φ) × T(t)

Where:
  φ = damping parameter (0.80 ≤ φ ≤ 0.98 recommended)
  φ close to 1.0 → minimal damping (trusts long-term trend)
  φ = 0.80 → strong damping (trend reverting toward flat by M+6)
```

Recommended default: φ = 0.90. Optimise jointly with α and β for A-class SKUs. For operational use, set φ = 0.90 globally and monitor trend forecast vs actuals at M+6 horizon monthly.

**Trend detection test (before applying Holt):**

```python
from scipy.stats import linregress

def has_significant_trend(history: np.ndarray, p_threshold: float = 0.05) -> bool:
    """Return True if demand shows a statistically significant linear trend."""
    x = np.arange(len(history))
    slope, intercept, r_value, p_value, std_err = linregress(x, history)
    return p_value < p_threshold and abs(slope) > 0.01 * np.mean(history)
```

If `has_significant_trend` returns False, fall back to SES.

### 6.4 Holt-Winters Seasonal Exponential Smoothing

**When to use:** SKUs with both trend AND seasonality. Mandatory for food & beverage, retail consumer goods, seasonal industrial products (HVAC, agricultural inputs), and any SKU with known annual promotional patterns. Requires minimum 2 full seasonal cycles of history.

**Mathematical definition (additive seasonality):**

```
Level:   L(t) = α × [D(t) - S(t-m)] + (1 - α) × [L(t-1) + T(t-1)]
Trend:   T(t) = β × [L(t) - L(t-1)] + (1 - β) × T(t-1)
Season:  S(t) = γ × [D(t) - L(t)] + (1 - γ) × S(t-m)
Forecast: F(t+h) = L(t) + h × T(t) + S(t-m+h_mod_m)

Where:
  m = seasonal period (e.g., 52 for weekly data with annual cycle)
  γ = seasonal smoothing parameter (0 < γ < 1)
```

**Multiplicative seasonality** (use when seasonal amplitude scales with the trend level — most consumer goods):

```
Level:   L(t) = α × [D(t) / S(t-m)] + (1 - α) × [L(t-1) + T(t-1)]
Trend:   T(t) = β × [L(t) - L(t-1)] + (1 - β) × T(t-1)
Season:  S(t) = γ × [D(t) / L(t)] + (1 - γ) × S(t-m)
Forecast: F(t+h) = [L(t) + h × T(t)] × S(t-m+h_mod_m)
```

**Additive vs multiplicative choice decision tree:**

```
1. Compute seasonal indices: I(j) = mean(D in season j) / overall mean, for j = 1..m
2. If max(I) / min(I) > 1.5 AND the ratio changes with the trend level:
   → Use MULTIPLICATIVE
3. If seasonal swings are roughly constant in absolute value:
   → Use ADDITIVE
4. If demand includes zeros:
   → ADDITIVE only (multiplicative undefined with zeros)
5. When in doubt: fit both, compare WMAPE in backtest — use the better one
```

**Seasonal period detection using FFT:**

Before fitting Holt-Winters, detect the dominant seasonal period from the data rather than assuming it:

```python
import numpy as np
from scipy.signal import periodogram

def detect_seasonal_period(history: np.ndarray, 
                            max_period: int = 104) -> int:
    """
    Detect dominant seasonal period using periodogram (FFT-based).
    Returns the period with maximum spectral power.
    
    Args:
        history: time series of demand values
        max_period: maximum period to consider (104 = 2 years of weekly data)
    
    Returns:
        Dominant seasonal period in periods
    """
    # Detrend first (remove linear trend to isolate seasonality)
    x = np.arange(len(history))
    from scipy.stats import linregress
    slope, intercept, *_ = linregress(x, history)
    detrended = history - (slope * x + intercept)
    
    # Compute periodogram
    freqs, power = periodogram(detrended)
    
    # Convert frequencies to periods, filter to plausible range
    periods = 1.0 / (freqs[1:] + 1e-10)  # avoid division by zero
    power = power[1:]
    
    # Filter to [4, max_period]
    valid = (periods >= 4) & (periods <= max_period)
    if not valid.any():
        return 52  # default to annual
    
    periods_valid = periods[valid]
    power_valid = power[valid]
    
    # Return period with maximum power
    dominant_period = periods_valid[np.argmax(power_valid)]
    
    # Round to nearest integer and snap to known periods
    rounded = int(round(dominant_period))
    known_periods = [4, 12, 13, 26, 52]  # monthly, quarterly, 4-week, 26-week, annual
    snapped = min(known_periods, key=lambda p: abs(p - rounded))
    
    return snapped
```

**Backtest protocol (minimum 2 years of data required):**

```
1. Obtain at least 104 weeks (2 years) of cleansed weekly demand history
2. Reserve last 52 weeks as test set (do NOT use for parameter fitting)
3. Train Holt-Winters on first 52 weeks (minimum 1 full seasonal cycle)
4. Generate 1-step-ahead forecasts for weeks 53–104
5. Compute WMAPE and bias (Mean Error) for the test period
6. If WMAPE > 35% OR bias > ±20%: investigate — consider multiplicative vs additive switch, or remove seasonality and use Holt
7. If pass: optimise α, β, γ on full 104-week history, deploy for production
8. Re-fit annually or when drift detected (3 consecutive months of bias > 15%)
```

**Seasonal initialisation:**

For the seasonal component, use the average ratio method:
1. Compute overall mean demand: μ = mean(all history)
2. For each season j (j = 1 to m): S_init(j) = mean(all observations in season j) / μ
3. For additive: S_init(j) = mean(all observations in season j) - μ
4. Verify: Σ S_init(j) = 0 (additive) or m (multiplicative) — adjust if not

### 6.5 Safety Stock Methods 1–4

Safety stock is the buffer inventory held against demand and supply variability. The correct method depends on available data quality and the degree of lead time variability.

**Common notation:**
```
D̄   = average demand per period
σ_D  = standard deviation of demand per period
LT   = average lead time (in same units as demand period)
σ_LT = standard deviation of lead time
z    = z-score for desired service level (from standard normal table)
```

**Z-score reference table:**

| Service Level | z |
|--------------|---|
| 90.0% | 1.282 |
| 95.0% | 1.645 |
| 97.5% | 1.960 |
| 98.0% | 2.054 |
| 99.0% | 2.326 |
| 99.5% | 2.576 |
| 99.9% | 3.090 |

Recommended service level by ABC class: A = 98.5% (z=2.17), B = 95.0% (z=1.645), C = 90.0% (z=1.282).

**Method 1 — Fixed Days of Supply (simplest, least accurate):**

```
SS = D̄ × k

Where k = fixed number of days/weeks of supply (set by policy, not data)
```

Use only for: C-class / Z-class SKUs where analytical methods would waste effort, or when no demand variability history exists (new products in first 4 weeks).

**Method 2 — Demand variability only (ignores lead time variability):**

```
SS = z × σ_D × √LT
```

Assumes lead time is constant (no variability). Use for: BX, BY SKUs with highly reliable suppliers where lead time variability is empirically < 5%.

**Method 3 — Demand variability over lead time (recommended standard):**

This is the Holt-Chopra & Meindl standard (Chopra & Meindl Ch.11):

```
SS = z × σ_DLT

Where σ_DLT = σ_D × √LT (standard deviation of demand during lead time)
```

This is equivalent to Method 2 and is the most commonly implemented method. Use for: AX, AY, BX, BY with moderately reliable supply.

**Method 4 — Combined demand AND lead time variability (most accurate):**

```
SS = z × √(LT × σ_D² + D̄² × σ_LT²)

Components:
  LT × σ_D²    = demand uncertainty during lead time
  D̄² × σ_LT²  = supply timing uncertainty
```

Use for: AX, AY, AZ SKUs where both demand and lead time are variable. Requires at least 12 historical lead time observations per supplier × SKU combination to estimate σ_LT reliably.

**Sigma estimation from history:**

```python
def estimate_demand_sigma(weekly_demand: np.ndarray, 
                           method: str = 'rolling') -> float:
    """
    Estimate demand standard deviation for safety stock calculation.
    
    method='rolling': Use rolling 13-week window std — captures recent variability
    method='historical': Use full history std — more stable, less responsive
    method='forecast_error': Use RMSE of forecast errors — most rigorous
    """
    if method == 'rolling':
        return float(pd.Series(weekly_demand).rolling(13).std().iloc[-1])
    elif method == 'historical':
        return float(np.std(weekly_demand, ddof=1))
    elif method == 'forecast_error':
        # Requires parallel array of forecast errors
        raise NotImplementedError("Pass forecast errors array separately")
    else:
        raise ValueError(f"Unknown method: {method}")
```

**Recommendation by SKU class:**
- AX, BX: Method 3 with `method='rolling'` sigma (recent variability most relevant)
- AY, BY: Method 4 with `method='forecast_error'` sigma (most accurate)
- AZ, BZ: Method 4 with forecast error sigma from ML model P90-P50 spread (DeepAR output — see Phase 4)
- CX: Method 2 with fixed z=1.282
- CY, CZ: Method 1 with k = 2–4 weeks

### 6.6 Economic Order Quantity (EOQ)

**When to use:** SKUs with relatively stable demand that are replenished against purchase orders (not make-to-order). EOQ minimises total ordering + holding cost.

**Mathematical definition (Harris 1913):**

```
EOQ = √(2 × D × S / H)

Where:
  D = annual demand (units)
  S = ordering / setup cost per order (€)
  H = annual holding cost per unit (€/unit/year)
    = unit_cost × holding_rate
    where holding_rate ≈ 20–30% of unit cost per year (includes capital, storage, obsolescence)
```

**Total annual cost at order quantity Q:**

```
TC(Q) = (D/Q) × S + (Q/2) × H

At EOQ: TC is minimised, and ordering cost = holding cost = √(D × S × H / 2)
```

**Parameter estimation:**

| Parameter | Source | Update Frequency |
|-----------|--------|-----------------|
| D | Average of last 12 months demand (annualised) | Monthly |
| S | Finance / Procurement: include PO processing, receiving, inspection costs | Annually |
| H | Finance: WACC × unit cost + warehousing cost per unit | Annually |

Typical values in manufacturing: S = €50–200 per order, holding rate = 20–25%/year.

**Parameter sensitivity analysis:**

EOQ is robust — it is relatively insensitive to errors in S and H due to the square root. A 50% error in S or H produces only a ~22% error in EOQ. However, D (demand rate) errors propagate more directly. Perform sensitivity analysis:

```python
def eoq_sensitivity(D: float, S: float, H: float,
                    D_range: tuple = (0.5, 1.5),
                    S_range: tuple = (0.5, 2.0)) -> dict:
    """
    Compute EOQ across a range of D and S multipliers.
    Shows how sensitive the EOQ recommendation is to parameter uncertainty.
    """
    import itertools
    results = {}
    for d_mult, s_mult in itertools.product(
        np.linspace(*D_range, 5), np.linspace(*S_range, 5)
    ):
        q = np.sqrt(2 * D * d_mult * S * s_mult / H)
        results[(round(d_mult, 2), round(s_mult, 2))] = round(q)
    return results
```

Rule of thumb: if EOQ varies by < 30% across the plausible parameter range, the recommendation is stable. If it varies by > 50%, refine the parameter estimates before using EOQ operationally.

**Quantity discount extension (all-units discount):**

When suppliers offer tiered pricing (e.g., unit cost drops at 500, 1000, 2000 units), the standard EOQ does not account for the cost change. Evaluate total annual cost at each break point:

```python
def eoq_with_quantity_discounts(
    D: float, S: float, holding_rate: float,
    price_breaks: list[tuple[int, float]]  # [(qty_min, unit_price), ...]
) -> tuple[int, float]:
    """
    Solve EOQ with all-units quantity discounts.
    Returns optimal order quantity and total annual cost.
    """
    # price_breaks sorted ascending by quantity
    price_breaks = sorted(price_breaks, key=lambda x: x[0])
    
    candidates = []
    for i, (qty_min, unit_price) in enumerate(price_breaks):
        H_i = unit_price * holding_rate
        eoq_i = np.sqrt(2 * D * S / H_i)
        qty_max = price_breaks[i+1][0] - 1 if i+1 < len(price_breaks) else np.inf
        
        # Clamp EOQ to valid range for this break
        q = max(qty_min, min(eoq_i, qty_max))
        
        # Total cost: purchasing + ordering + holding
        tc = D * unit_price + (D / q) * S + (q / 2) * H_i
        candidates.append((int(q), tc))
    
    # Select minimum total cost
    return min(candidates, key=lambda x: x[1])
```

### 6.7 Error Metrics: MAE, MAPE, RMSE, WMAPE, sMAPE

Selecting the correct accuracy metric is not a technical detail — it determines what the organisation optimises for and what behaviours it incentivises. Use the wrong metric and you will improve it while actual business outcomes worsen.

**MAE — Mean Absolute Error:**
```
MAE = (1/n) × Σ |A(t) - F(t)|

Units: same as demand (units, €)
Best for: comparing models on the same SKU/dataset
Limitation: not scale-invariant — cannot compare across SKUs of different magnitudes
```

**MAPE — Mean Absolute Percentage Error:**
```
MAPE = (100/n) × Σ |A(t) - F(t)| / A(t)

Units: percentage
Best for: single-SKU model comparison, reporting to business stakeholders
Limitation: undefined when A(t) = 0; asymmetric (over-forecast errors bounded at 100%, under-forecast unbounded); inflated for low-volume SKUs
```

**RMSE — Root Mean Squared Error:**
```
RMSE = √[(1/n) × Σ (A(t) - F(t))²]

Units: same as demand
Best for: penalising large errors (outlier forecasts); used in model training loss functions
Limitation: not scale-invariant; sensitive to outliers; hard to interpret for business users
```

**WMAPE — Weighted Mean Absolute Percentage Error (PRIMARY KPI):**
```
WMAPE = Σ |A(t) - F(t)| / Σ A(t) × 100%

Equivalently: total absolute error / total actual demand × 100%
Units: percentage
Best for: portfolio-level accuracy measurement; A-class SKUs dominate (high volume = high weight)
Advantage over MAPE: naturally handles zero actuals (denominator uses aggregate); consistent with business value
```

WMAPE is the recommended primary KPI for this implementation because it weights accuracy by business importance (high-volume SKUs contribute more) and avoids the division-by-zero problem of simple MAPE.

**sMAPE — Symmetric Mean Absolute Percentage Error:**
```
sMAPE = (200/n) × Σ |A(t) - F(t)| / (|A(t)| + |F(t)|)

Units: percentage (0–200%)
Best for: balanced treatment of over- and under-forecasts; ML model competition benchmarks
Limitation: not purely symmetric despite the name; unusual scaling confuses practitioners
```

**Bias decomposition:**

Beyond accuracy, measure forecast bias (systematic over- or under-forecasting):

```python
def forecast_bias_metrics(actuals: np.ndarray, 
                           forecasts: np.ndarray) -> dict:
    """Compute comprehensive bias and accuracy metrics."""
    errors = actuals - forecasts  # positive = under-forecast
    abs_errors = np.abs(errors)
    
    metrics = {
        'MAE': float(np.mean(abs_errors)),
        'RMSE': float(np.sqrt(np.mean(errors ** 2))),
        'ME': float(np.mean(errors)),           # Mean Error (bias)
        'MPE': float(np.mean(errors / (actuals + 1e-10) * 100)),  # Mean % Error
        'WMAPE': float(np.sum(abs_errors) / np.sum(actuals) * 100),
        'sMAPE': float(np.mean(200 * abs_errors / (actuals + forecasts + 1e-10))),
        'tracking_signal': float(np.sum(errors) / np.mean(abs_errors)),  # Trigg's signal
    }
    
    # Trigg's tracking signal: |TS| > 4 indicates systematic bias requiring investigation
    metrics['bias_flag'] = abs(metrics['tracking_signal']) > 4
    
    return metrics
```

**When to use each metric:**

| Metric | Use Case | Do NOT Use When |
|--------|----------|-----------------|
| WMAPE | Portfolio KPI, executive dashboard | Evaluating individual low-volume SKUs |
| MAPE | Single SKU model comparison | Any zero actuals in period |
| MAE | Model training objective, same-scale comparisons | Cross-SKU benchmarking |
| RMSE | Penalising large errors, ML loss function | Business reporting (hard to interpret) |
| sMAPE | ML competition benchmarks, symmetric comparison | Daily business reporting |
| ME (bias) | Detecting systematic over/under-forecast | Measuring accuracy (can cancel out) |

### 6.8 ABC-XYZ Matrix Construction and Policy Assignment

**Full construction algorithm:**

```python
import pandas as pd
import numpy as np

def build_abc_xyz_matrix(
    demand_df: pd.DataFrame,  # columns: sku, period, demand_units, revenue
    abc_metric: str = 'revenue',  # or 'units'
    xyz_lookback_weeks: int = 52
) -> pd.DataFrame:
    """
    Construct ABC-XYZ classification for full portfolio.
    
    Returns DataFrame with columns:
      sku, annual_revenue, cumulative_pct, abc_class, 
      mean_demand, cv, xyz_class, combined_class, 
      recommended_model, safety_stock_method, review_freq
    """
    # --- ABC Classification ---
    sku_summary = demand_df.groupby('sku').agg(
        annual_revenue=('revenue', 'sum'),
        mean_demand=('demand_units', 'mean'),
        std_demand=('demand_units', 'std')
    ).reset_index()
    
    sku_summary = sku_summary.sort_values('annual_revenue', ascending=False)
    total_revenue = sku_summary['annual_revenue'].sum()
    sku_summary['cumulative_pct'] = (
        sku_summary['annual_revenue'].cumsum() / total_revenue * 100
    )
    
    def assign_abc(cum_pct: float) -> str:
        if cum_pct <= 80: return 'A'
        elif cum_pct <= 95: return 'B'
        else: return 'C'
    
    sku_summary['abc_class'] = sku_summary['cumulative_pct'].apply(assign_abc)
    
    # --- XYZ Classification ---
    sku_summary['cv'] = sku_summary['std_demand'] / (sku_summary['mean_demand'] + 1e-10)
    
    def assign_xyz(cv: float) -> str:
        if cv < 0.10: return 'X'
        elif cv < 0.25: return 'Y'
        else: return 'Z'
    
    sku_summary['xyz_class'] = sku_summary['cv'].apply(assign_xyz)
    sku_summary['combined_class'] = sku_summary['abc_class'] + sku_summary['xyz_class']
    
    # --- Policy assignment ---
    policy_map = {
        'AX': ('SES', 'Method_3', 'Weekly', 0.985),
        'AY': ('Holt_Winters', 'Method_4', 'Weekly', 0.985),
        'AZ': ('LightGBM', 'Method_4', 'Weekly', 0.990),
        'BX': ('SES', 'Method_3', 'Biweekly', 0.950),
        'BY': ('Holt_Winters', 'Method_3', 'Biweekly', 0.950),
        'BZ': ('Holt_Winters', 'Method_4', 'Biweekly', 0.970),
        'CX': ('SMA', 'Method_2', 'Monthly', 0.900),
        'CY': ('SMA', 'Method_2', 'Monthly', 0.900),
        'CZ': ('Method_1', 'Method_1', 'Monthly', 0.900),
    }
    
    sku_summary[['recommended_model', 'safety_stock_method', 
                 'review_freq', 'target_service_level']] = pd.DataFrame(
        sku_summary['combined_class'].map(policy_map).tolist(),
        index=sku_summary.index
    )
    
    return sku_summary
```

### 6.9 Demand Sensing: POS Signal Integration & Bullwhip De-amplification

**Demand sensing** is the practice of using high-frequency, downstream demand signals (POS scan data, e-commerce orders, call centre data) to update the short-horizon (0–4 weeks) forecast with near-real-time intelligence, rather than waiting for the monthly planning cycle.

**POS signal integration architecture:**

```
Retailer POS Systems
      |
      | (daily EDI 852 / SFTP / API)
      v
Landing Zone (Azure Data Lake)
      |
      | Data quality checks (completeness, schema, range validation)
      v
Cleansed POS Table (daily sell-out by SKU × Store × Day)
      |
      | Aggregation to planning location level
      v
Demand Signal Repository (DSR)
      |
      | Demand sensing model (LightGBM — see Phase 4)
      v
Updated W+1 to W+4 Forecast (replaces statistical forecast for near-horizon)
      |
      v
SAP IBP (consumed into constrained supply plan)
```

**Bullwhip de-amplification:**

The bullwhip effect occurs when order variability amplifies up the supply chain — each echelon (retailer → distributor → manufacturer) inflates orders due to demand uncertainty and local safety stock behaviour. Measure and actively manage this:

```
Bullwhip Ratio (per echelon) = Var(Orders issued) / Var(Demand received)

Target: ≤ 1.2 (some amplification is inevitable due to batching)
Alert threshold: > 1.5 (investigate ordering behaviour)
Crisis threshold: > 2.0 (systematic over-ordering, requires process intervention)
```

**De-amplification techniques:**

1. **Shared demand visibility:** Provide upstream suppliers with direct access to POS data (vendor-managed inventory, VMI). Removes the need for each echelon to add its own safety buffer.

2. **Order smoothing:** In IBP, configure order smoothing to prevent week-on-week order swings > 15% without planner override. This requires overriding the unconstrained MRP output.

3. **Synchronised replenishment cycles:** Align replenishment cadence across echelons. If retailers order weekly on Mondays, manufacture to a weekly production cycle — avoid the batch distortion from monthly PO consolidation.

4. **Forecast sharing upstream:** Publish the 13-week rolling consensus forecast to Tier 1 suppliers via EDI 830 (Planning Schedule with Release Capability). This allows suppliers to pre-build without waiting for a hard PO.

5. **Lead time reduction:** Every week of lead time reduction allows safety stock reduction by √(LT_new/LT_old) factor, reducing the incentive to over-order.

---

## 7. Phase 4: ML/AI Pipeline

**Duration:** 12–14 weeks (runs partially in parallel with Phase 3)  
**Owner:** Data Science Lead + ML Engineers  
**Gate criterion:** At minimum one ML model (LightGBM or Prophet) validated in backtesting with WMAPE improvement ≥ 5pp vs. best statistical baseline; MLflow experiment tracking operational; model governance framework established

**Prerequisite checklist before starting Phase 4:**
- [ ] Phase 3 statistical models deployed and running (provides baseline to beat)
- [ ] Feature store (cleansed demand history + exogenous variables) loaded into data lake
- [ ] MLflow or equivalent experiment tracking deployed
- [ ] GPU compute environment provisioned (for LSTM/TFT training)
- [ ] Model governance policy approved (who can promote a model to production, how often models are retrained)

### 7.1 Prophet (by Meta / Facebook)

**What it is:** A decomposable additive time series model:
```
y(t) = g(t) + s(t) + h(t) + ε(t)

Where:
  g(t) = trend component (piecewise linear or logistic growth)
  s(t) = seasonality component (Fourier series)
  h(t) = holiday / special event effects
  ε(t) = error term
```

**When to use:** AY, AZ SKUs with annual seasonality and multiple known event effects (holidays, promotions, price changes). Excellent for planners who need interpretable outputs and the ability to add custom seasonal components.

**Step-by-step implementation:**

**Step 1 — Holiday calendar construction per country:**

```python
import pandas as pd
from prophet import Prophet

def build_country_holiday_calendar(countries: list[str],
                                    years: list[int]) -> pd.DataFrame:
    """
    Build a Prophet-compatible holidays DataFrame for all countries.
    
    Prophet expects: columns ['ds', 'holiday'] where ds is the date.
    We extend with lower_window and upper_window to capture pre/post effects.
    """
    from workalendar.europe import Germany, France, UnitedKingdom
    from workalendar.america import UnitedStates, Brazil
    # ... import per country
    
    calendar_map = {
        'DE': Germany(),
        'FR': France(),
        'GB': UnitedKingdom(),
        'US': UnitedStates(),
        # ... map all 40 countries
    }
    
    all_holidays = []
    for country in countries:
        cal = calendar_map.get(country)
        if cal is None:
            continue
        for year in years:
            for date, name in cal.holidays(year):
                all_holidays.append({
                    'ds': pd.Timestamp(date),
                    'holiday': f"{country}_{name.replace(' ', '_')}",
                    'lower_window': -1,   # capture pre-holiday effect
                    'upper_window': 1,    # capture post-holiday effect
                })
    
    return pd.DataFrame(all_holidays)

# Add promotional events as custom holidays
def add_promotion_events(holidays_df: pd.DataFrame,
                          promo_calendar: pd.DataFrame) -> pd.DataFrame:
    """
    Add promotional events from the commercial promo calendar as holidays.
    promo_calendar: columns [start_date, end_date, promo_name, sku_group]
    """
    promo_events = []
    for _, row in promo_calendar.iterrows():
        dates = pd.date_range(row['start_date'], row['end_date'])
        for date in dates:
            promo_events.append({
                'ds': date,
                'holiday': f"PROMO_{row['promo_name']}",
                'lower_window': -2,
                'upper_window': 2,
            })
    
    return pd.concat([holidays_df, pd.DataFrame(promo_events)], ignore_index=True)
```

**Step 2 — Changepoint prior scale tuning (controls trend flexibility):**

The `changepoint_prior_scale` parameter is the most impactful Prophet hyperparameter. It controls how aggressively the model fits trend changes in historical data:
- Low value (0.001–0.05): trend changes slowly, model assumes stable trend
- High value (0.1–0.5): trend is highly flexible, captures every local fluctuation (risk: overfitting)

Tune via cross-validation:

```python
from prophet.diagnostics import cross_validation, performance_metrics

def tune_prophet_changepoint(
    df: pd.DataFrame,  # Prophet format: columns ['ds', 'y']
    holidays: pd.DataFrame,
    candidate_scales: list = [0.001, 0.01, 0.05, 0.1, 0.3, 0.5]
) -> float:
    """Find optimal changepoint_prior_scale via Prophet cross-validation."""
    best_scale, best_wmape = 0.05, np.inf
    
    for scale in candidate_scales:
        model = Prophet(
            changepoint_prior_scale=scale,
            holidays=holidays,
            seasonality_mode='multiplicative',
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False
        )
        model.fit(df)
        
        # Cross-validate: 1 year initial, 3-month cutoffs, 3-month horizon
        cv_df = cross_validation(
            model,
            initial='365 days',
            period='91 days',
            horizon='91 days',
            parallel='processes'
        )
        
        perf = performance_metrics(cv_df)
        wmape = perf['mdape'].mean()  # use mape or custom metric
        
        if wmape < best_wmape:
            best_wmape = wmape
            best_scale = scale
    
    return best_scale
```

**Step 3 — Production fitting and forecast generation:**

```python
def fit_prophet_production(
    df: pd.DataFrame,
    holidays: pd.DataFrame,
    horizon_weeks: int = 52,
    changepoint_prior_scale: float = 0.05
) -> pd.DataFrame:
    """Fit production Prophet model and generate forecast with uncertainty intervals."""
    model = Prophet(
        changepoint_prior_scale=changepoint_prior_scale,
        holidays=holidays,
        seasonality_mode='multiplicative',
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        interval_width=0.90,  # 90% prediction interval → P5/P95
        mcmc_samples=0        # MAP estimation (fast); use mcmc_samples=300 for full Bayesian
    )
    
    # Add custom regressors (weather, price)
    model.add_regressor('temperature_index', standardize=True)
    model.add_regressor('promotional_flag', standardize=False)
    
    model.fit(df)
    
    future = model.make_future_dataframe(periods=horizon_weeks, freq='W')
    # Add regressor values for future periods (requires forward-looking data)
    # ... populate temperature_index, promotional_flag for future dates
    
    forecast = model.predict(future)
    
    # Clip negative forecasts (demand cannot be negative)
    forecast['yhat'] = forecast['yhat'].clip(lower=0)
    forecast['yhat_lower'] = forecast['yhat_lower'].clip(lower=0)
    
    return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper', 
                       'trend', 'yearly', 'weekly', 'holidays']]
```

### 7.2 LSTM / Seq2Seq (Long Short-Term Memory)

**When to use:** AZ, BZ SKUs with complex non-linear patterns, multiple external drivers (weather, events, economic indicators), or when statistical models show persistent poor accuracy (WMAPE > 35%). Also for new product introduction when analogue SKU patterns are used as input features.

**Architecture (Seq2Seq with attention):**

```
Encoder: LSTM stack processing input sequence (past T_in weeks)
Decoder: LSTM stack generating output sequence (future T_out weeks)
Attention: Bahdanau-style attention allowing decoder to query encoder hidden states

Input features (T_in = 52 weeks):
  - Demand history (target variable, lagged)
  - Promotional flags (binary: 0/1)
  - Day-of-week / week-of-year cyclical encodings
  - Fourier features for seasonality (sin/cos transforms)
  - Rolling statistics: mean-4w, mean-13w, std-13w
  - Weather index (temperature, precipitation)
  - Price index (relative to category average)

Output: T_out = 13 weeks of point forecasts + prediction intervals
```

**Feature engineering in detail:**

```python
def engineer_lstm_features(
    demand: pd.Series,  # DatetimeIndex, weekly frequency
    weather: pd.DataFrame,
    promotions: pd.DataFrame,
    price: pd.Series
) -> pd.DataFrame:
    """Engineer features for LSTM input."""
    df = pd.DataFrame({'demand': demand})
    
    # Lag features
    for lag in [1, 2, 3, 4, 8, 13, 26, 52]:
        df[f'lag_{lag}w'] = df['demand'].shift(lag)
    
    # Rolling statistics
    for window in [4, 8, 13, 26]:
        df[f'roll_mean_{window}w'] = df['demand'].rolling(window).mean()
        df[f'roll_std_{window}w'] = df['demand'].rolling(window).std()
        df[f'roll_max_{window}w'] = df['demand'].rolling(window).max()
    
    # Cyclical time encodings (avoid ordinal encoding of week number)
    week_of_year = df.index.isocalendar().week.astype(int)
    df['sin_week'] = np.sin(2 * np.pi * week_of_year / 52)
    df['cos_week'] = np.cos(2 * np.pi * week_of_year / 52)
    df['sin_month'] = np.sin(2 * np.pi * df.index.month / 12)
    df['cos_month'] = np.cos(2 * np.pi * df.index.month / 12)
    
    # Fourier features for seasonality (k=3 harmonics captures most annual patterns)
    for k in range(1, 4):
        df[f'fourier_sin_{k}'] = np.sin(2 * np.pi * k * week_of_year / 52)
        df[f'fourier_cos_{k}'] = np.cos(2 * np.pi * k * week_of_year / 52)
    
    # Exogenous features
    df = df.merge(weather[['week', 'temperature_zscore', 'precip_zscore']], 
                  left_index=True, right_on='week', how='left')
    df = df.merge(promotions[['week', 'promo_flag', 'discount_pct']], 
                  left_index=True, right_on='week', how='left')
    df['price_index'] = price.reindex(df.index)
    
    return df.dropna()
```

**Training protocol:**

```python
import torch
import torch.nn as nn

class Seq2SeqLSTM(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, 
                 num_layers: int, output_horizon: int):
        super().__init__()
        self.encoder = nn.LSTM(input_size, hidden_size, num_layers, 
                                batch_first=True, dropout=0.2)
        self.decoder = nn.LSTM(1, hidden_size, num_layers, 
                                batch_first=True, dropout=0.2)
        self.attention = nn.MultiheadAttention(hidden_size, num_heads=4, 
                                                batch_first=True)
        self.output_layer = nn.Linear(hidden_size, 1)
        self.output_horizon = output_horizon
    
    def forward(self, x_enc: torch.Tensor, 
                x_dec: torch.Tensor) -> torch.Tensor:
        # Encode
        enc_out, (h_n, c_n) = self.encoder(x_enc)
        
        # Decode with attention
        dec_out, _ = self.decoder(x_dec, (h_n, c_n))
        
        # Attention: decoder queries encoder hidden states
        attn_out, _ = self.attention(dec_out, enc_out, enc_out)
        
        # Project to scalar output
        return self.output_layer(attn_out).squeeze(-1)

# Training hyperparameters
BATCH_SIZE = 64
LEARNING_RATE = 1e-3
MAX_EPOCHS = 100
EARLY_STOPPING_PATIENCE = 10
TEACHER_FORCING_RATIO = 0.5  # Curriculum learning
```

**Backtesting protocol:**

Use expanding-window walk-forward validation:
- Minimum training window: 104 weeks (2 years)
- Step size: 4 weeks (re-evaluate monthly)
- Forecast horizon per step: 13 weeks
- Report WMAPE at W+1, W+4, W+8, W+13 horizons
- Model passes validation if WMAPE at W+4 ≤ (best statistical baseline WMAPE × 0.95)

### 7.3 LightGBM for Demand Sensing

**When to use:** Near-horizon demand sensing (W+1 to W+4), leveraging POS data, promotional calendars, and causal drivers. LightGBM is preferred over XGBoost for large-scale demand sensing due to faster training and lower memory consumption at scale.

**Feature importance and SHAP analysis:**

```python
import lightgbm as lgb
import shap
import optuna

def train_lightgbm_demand_sensor(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: pd.DataFrame,
    y_val: pd.Series
) -> lgb.Booster:
    """Train LightGBM demand sensing model with Optuna hyperparameter tuning."""
    
    def objective(trial: optuna.Trial) -> float:
        params = {
            'objective': 'regression_l1',  # MAE objective for demand sensing
            'metric': 'mape',
            'num_leaves': trial.suggest_int('num_leaves', 20, 150),
            'learning_rate': trial.suggest_float('learning_rate', 1e-3, 0.1, log=True),
            'n_estimators': trial.suggest_int('n_estimators', 200, 2000),
            'min_child_samples': trial.suggest_int('min_child_samples', 10, 100),
            'subsample': trial.suggest_float('subsample', 0.6, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.6, 1.0),
            'reg_alpha': trial.suggest_float('reg_alpha', 1e-4, 10.0, log=True),
            'reg_lambda': trial.suggest_float('reg_lambda', 1e-4, 10.0, log=True),
            'verbose': -1,
        }
        
        dtrain = lgb.Dataset(X_train, label=y_train)
        dval = lgb.Dataset(X_val, label=y_val, reference=dtrain)
        
        model = lgb.train(
            params,
            dtrain,
            valid_sets=[dval],
            callbacks=[lgb.early_stopping(50), lgb.log_evaluation(0)]
        )
        
        preds = model.predict(X_val)
        wmape = np.sum(np.abs(y_val - preds)) / np.sum(y_val) * 100
        return wmape
    
    study = optuna.create_study(direction='minimize')
    study.optimize(objective, n_trials=100, timeout=3600)
    
    best_params = study.best_params
    best_params['verbose'] = -1
    
    dtrain = lgb.Dataset(X_train, label=y_train)
    dval = lgb.Dataset(X_val, label=y_val, reference=dtrain)
    
    final_model = lgb.train(
        best_params,
        dtrain,
        valid_sets=[dval],
        callbacks=[lgb.early_stopping(50), lgb.log_evaluation(0)]
    )
    
    return final_model

def explain_with_shap(model: lgb.Booster, 
                       X: pd.DataFrame) -> pd.DataFrame:
    """Generate SHAP feature importance for model interpretability."""
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)
    
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'mean_abs_shap': np.abs(shap_values).mean(axis=0)
    }).sort_values('mean_abs_shap', ascending=False)
    
    return feature_importance
```

**SHAP for planner trust:** The single biggest barrier to ML model adoption is planner distrust. SHAP explanations allow planners to see, in business terms, why the model is producing a particular forecast. For example: "This week's forecast is 23% higher than last week primarily because: (1) temperature forecast +8°C [+12% effect], (2) promotional event week 14 [+8% effect], (3) approaching Easter holiday [+3% effect]." This transparency is essential for change management (see Phase 11).

### 7.4 Temporal Fusion Transformer (TFT)

**What it is:** A state-of-the-art attention-based architecture (Lim et al., 2019, Google) specifically designed for multi-horizon time series forecasting with heterogeneous inputs. TFT combines:
- LSTM encoder for processing past observations
- Variable selection networks (learnable feature importance)
- Multi-head attention for long-range dependencies
- Quantile regression outputs (P10, P50, P90)

**When to use:** A-class SKUs with complex causal structures, multiple exogenous variables, and requirement for calibrated prediction intervals (for safety stock calibration). Best-in-class accuracy on retail and consumer goods benchmarks.

**Variable selection (key differentiator of TFT):**

TFT learns which variables are important via a Gating Linear Unit (GLU):

```python
from pytorch_forecasting import TemporalFusionTransformer, TimeSeriesDataSet
from pytorch_forecasting.metrics import QuantileLoss

def configure_tft_dataset(df: pd.DataFrame) -> TimeSeriesDataSet:
    """Configure TFT dataset with variable categories."""
    return TimeSeriesDataSet(
        df,
        time_idx='week_idx',
        target='demand',
        group_ids=['sku_id', 'location_id'],
        max_encoder_length=52,  # 1 year of history
        max_prediction_length=13,  # 13-week forecast horizon
        
        # Static categoricals (do not change over time)
        static_categoricals=['sku_id', 'location_id', 'abc_class', 
                              'product_family', 'country'],
        
        # Static reals (numeric, don't change over time)
        static_reals=['annual_revenue', 'unit_weight'],
        
        # Time-varying categoricals (known in future — can be planned)
        time_varying_known_categoricals=['holiday_flag', 'promo_flag', 
                                          'month_of_year', 'week_of_year'],
        
        # Time-varying reals known in future
        time_varying_known_reals=['temperature_forecast', 'week_idx',
                                   'price_index', 'relative_humidity'],
        
        # Time-varying reals NOT known in future (can only be used in encoder)
        time_varying_unknown_reals=['demand', 'pos_sellout', 'inventory_level'],
        
        target_normalizer=GroupNormalizer(groups=['sku_id', 'location_id'],
                                           transformation='softplus'),
        add_relative_time_idx=True,
        add_target_scales=True,
    )
```

**Attention interpretation:**

TFT's multi-head attention weights reveal which past time steps the model focuses on when making a prediction. This is invaluable for demand planners:
- If the model consistently attends to the same week-of-year in prior years → seasonal pattern confirmed
- If the model attends to recent weeks only → demand is driven by recent trends not seasonal cycles
- Unexpected attention patterns → data quality issue or model mis-specification

```python
def extract_attention_weights(model: TemporalFusionTransformer,
                               dataloader) -> dict:
    """Extract and summarise TFT attention weights for interpretation."""
    interpretation = model.interpret_output(
        model.predict(dataloader, mode='raw', return_x=True)[0],
        reduction='sum'
    )
    return {
        'encoder_variables': interpretation['encoder_variables'],
        'decoder_variables': interpretation['decoder_variables'],
        'static_variables': interpretation['static_variables'],
        'attention_patterns': interpretation['attention'],
    }
```

**Multi-horizon output:**

TFT natively produces quantile forecasts (P10, P50, P90) for each of the 13 forecast weeks. These quantiles are directly usable for safety stock calibration:
- P50 = median forecast → use as statistical baseline
- P90 = upper bound → use to size safety stock (if target service level = 90%)
- P10 = lower bound → use for downside scenario planning

### 7.5 DeepAR (Probabilistic Forecasting)

**What it is:** Amazon Research's autoregressive RNN model for probabilistic time series forecasting. Trains a single global model across thousands of SKUs simultaneously, learning cross-SKU patterns that improve accuracy for sparse/intermittent SKUs that have insufficient individual history.

**When to use:**
- Large portfolio of related SKUs (same product category, similar demand patterns)
- Intermittent / sparse demand (SKUs where individual models fail due to insufficient history)
- Where calibrated P10/P50/P90 outputs are required for safety stock calibration
- New product introductions where the global model can transfer patterns from similar mature SKUs

**Global model training across SKUs:**

```python
# Using GluonTS (Apache-2.0) or pytorch-forecasting DeepAR implementation
from gluonts.model.deepar import DeepAREstimator
from gluonts.mx.trainer import Trainer
from gluonts.dataset.pandas import PandasDataset

def train_deepar_global(
    demand_df: pd.DataFrame,  # columns: item_id, date, demand
    prediction_length: int = 13,
    num_skus: int = None
) -> object:
    """
    Train a global DeepAR model across all SKUs simultaneously.
    
    Key advantage: DeepAR learns a single set of parameters shared across all SKUs,
    which regularises the model and helps with sparse/intermittent items.
    """
    dataset = PandasDataset.from_long_dataframe(
        demand_df,
        target='demand',
        item_id='item_id',
        timestamp='date',
        freq='W'
    )
    
    estimator = DeepAREstimator(
        freq='W',
        prediction_length=prediction_length,
        context_length=52,          # use 1 year of history as context
        num_layers=2,
        num_cells=40,
        cell_type='lstm',
        dropout_rate=0.1,
        num_parallel_samples=100,   # Monte Carlo samples for probability distribution
        trainer=Trainer(
            epochs=50,
            learning_rate=1e-3,
            patience=5,             # early stopping
        )
    )
    
    predictor = estimator.train(training_data=dataset)
    return predictor

def generate_deepar_forecasts(
    predictor,
    test_dataset,
    quantiles: list = [0.1, 0.5, 0.9]
) -> pd.DataFrame:
    """
    Generate probabilistic forecasts with P10/P50/P90 outputs.
    
    P10: 10th percentile — use for pessimistic supply planning scenario
    P50: median — use as point forecast in S&OP
    P90: 90th percentile — use for safety stock sizing (90% service level)
    """
    forecasts = list(predictor.predict(test_dataset))
    
    results = []
    for forecast in forecasts:
        item_id = forecast.item_id
        for q in quantiles:
            q_forecast = forecast.quantile(q)
            for t, value in enumerate(q_forecast):
                results.append({
                    'item_id': item_id,
                    'horizon_week': t + 1,
                    'quantile': q,
                    'forecast': max(0, float(value))  # floor at 0
                })
    
    return pd.DataFrame(results)
```

**P10/P50/P90 outputs for safety stock calibration:**

Rather than using a separate safety stock formula, DeepAR's quantile outputs can directly drive safety stock:

```
Safety Stock = (P90 forecast for week LT+1) - (P50 forecast for week LT+1)

Where LT = supplier lead time in weeks.

This approach is superior to formula-based safety stock because:
1. It reflects the actual forecast uncertainty (not a parametric assumption)
2. It is automatically wider for AZ/BZ SKUs (high uncertainty)
3. It is automatically narrower for AX SKUs (low uncertainty)
4. It updates every week as new data arrives
```

**MLflow experiment tracking (mandatory for all ML models):**

```python
import mlflow
import mlflow.lightgbm

with mlflow.start_run(run_name=f"DeepAR_global_v{version}"):
    mlflow.log_params({
        'model_type': 'DeepAR',
        'num_skus_trained': num_skus,
        'context_length': 52,
        'prediction_length': 13,
        'num_epochs': 50,
        'training_date': pd.Timestamp.now().isoformat()
    })
    
    # Train and evaluate
    predictor = train_deepar_global(demand_df, prediction_length=13)
    forecasts_df = generate_deepar_forecasts(predictor, test_dataset)
    
    # Log metrics
    wmape = compute_wmape(actuals, forecasts_df[forecasts_df.quantile == 0.5])
    mlflow.log_metrics({
        'wmape_p50': wmape,
        'p90_coverage': coverage_metric,  # % of actuals below P90
        'pinball_loss_p10': pinball_10,
        'pinball_loss_p90': pinball_90,
    })
    
    # Log model artifact
    mlflow.pyfunc.log_model('model', python_model=predictor)
    
    mlflow.set_tags({
        'environment': 'production',
        'model_family': 'deepar',
        'approved_by': 'data_science_lead'
    })
```

---

## 8. Phase 5: Integration & Automation

**Duration:** 10–12 weeks  
**Owner:** SAP IBP Functional Lead + Data Engineering + SI Partner  
**Gate criterion:** SAP IBP ↔ S/4HANA roundtrip validated (forecast in → MRP run → PO out); at least 2 external integrations live (POS feed + one external data source); automated monthly planning cycle running without manual trigger

### 8.1 SAP IBP Integration

**SAP IBP (Integrated Business Planning) is the primary demand planning system of record.** All statistical and ML models feed into IBP as key figures on the demand planning area. IBP then runs the S&OP process, merges with supply constraints, and releases the constrained plan to SAP S/4HANA for MRP execution.

**IBP Key Figure Architecture:**

| Key Figure | Source | Description |
|------------|--------|-------------|
| STATISTICAL_FORECAST | Python batch job → IBP API | SES / Holt-Winters / SMA output |
| ML_FORECAST_P50 | Python ML pipeline → IBP API | LightGBM / TFT median forecast |
| ML_FORECAST_P90 | Python ML pipeline → IBP API | TFT/DeepAR P90 — for SS sizing |
| DEMAND_SENSING | POS pipeline → IBP API | LightGBM demand sensing (W+1 to W+4) |
| CONSENSUS_FORECAST | IBP (planner overrides) | Final agreed demand plan |
| CONSTRAINED_PLAN | IBP (supply heuristic) | After capacity/supply constraints applied |
| STATISTICAL_SS | Python → IBP API | Safety stock recommendation (Method 3/4) |
| PROMO_UPLIFT | Promo model → IBP API | Modelled promotional lift |

**SAP Integration Suite (API integration pattern):**

```
Python Forecasting Jobs (Azure Functions / Databricks)
        |
        | REST API calls (IBP OData API v4)
        | Authentication: OAuth 2.0 (client credentials)
        v
SAP IBP Planning Area
        |
        | IBP S&OP Workflow
        v
Approved Consensus Plan
        |
        | CIF (Core Interface) / IBP Supply Planning
        v
SAP S/4HANA (MRP Live)
        |
        | MRP run generates procurement proposals
        v
Purchase Requisitions → Purchase Orders (buyer approval workflow)
```

**IBP OData API integration (TypeScript client):**

```typescript
// src/departments/03-demand-planning/integrations/IBPClient.ts
import axios, { AxiosInstance } from 'axios';

interface IBPForecastPayload {
  sku: string;
  location: string;
  period: string; // ISO 8601 week: "2026-W03"
  keyFigure: string;
  value: number;
  unit: string;
}

export class IBPDemandPlanningClient {
  private client: AxiosInstance;

  constructor(
    private readonly baseUrl: string,
    private readonly clientId: string,
    private readonly clientSecret: string
  ) {
    this.client = axios.create({ baseURL: baseUrl });
  }

  async uploadForecast(payloads: IBPForecastPayload[]): Promise<void> {
    const token = await this.getOAuthToken();
    
    // IBP accepts batch requests — chunk into batches of 1000
    const chunks = this.chunk(payloads, 1000);
    
    for (const chunk of chunks) {
      await this.client.post(
        '/sap/opu/odata/IBP/PLANNING_OD_SRV/KeyFigureValueSet',
        { d: { results: chunk.map(this.toIBPFormat) } },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
            'x-csrf-token': await this.getCsrfToken(token)
          }
        }
      );
    }
  }

  private async getOAuthToken(): Promise<string> {
    const response = await axios.post(
      `${this.baseUrl}/oauth/token`,
      new URLSearchParams({
        grant_type: 'client_credentials',
        client_id: this.clientId,
        client_secret: this.clientSecret
      })
    );
    return response.data.access_token;
  }

  private chunk<T>(array: T[], size: number): T[][] {
    return Array.from({ length: Math.ceil(array.length / size) },
      (_, i) => array.slice(i * size, i * size + size));
  }
}
```

### 8.2 External System Integrations

**SAP APO/DP (Legacy — for phased migration)**

Many sites may still run SAP APO Demand Planning. During the transition period, maintain a read-only integration from APO to the new data lake for comparison purposes:
- Extract APO forecast via SAP BW infocube or direct APO extraction via CIF
- Load into data lake alongside new forecasts
- Run accuracy comparison for minimum 3 months before decommissioning APO DP

**Blue Yonder (JDA) Demand Management**

For sites running Blue Yonder as their planning tool (common in consumer goods and retail):
- Blue Yonder exposes a REST API for plan upload/download
- Map Blue Yonder planning segments to SAP IBP planning groups
- Synchronise weekly via scheduled API batch (not real-time — planning is a batch process)
- Conflict resolution: SAP IBP is the system of record; Blue Yonder is a satellite

**Oracle Demantra**

Oracle Demantra (common in high-tech and pharma supply chains):
- Demantra uses a database-level integration (Oracle DB schema)
- Extract via Oracle Data Integrator (ODI) to data lake
- Do not attempt direct DB writes from Python — use Demantra's published API

**POS Data Feeds (Retail Partners)**

POS integration is the highest-value external data source for consumer-facing businesses:

```
Integration by partner type:
├── Large retail chains (Walmart, Carrefour, Tesco)
│   ├── EDI 852 (Product Activity Data) via AS2/SFTP — daily
│   ├── Retail Link / Supplier Portal API (Walmart-specific) — daily
│   └── GS1 ECom XML (SLSRPT message) — for European retailers
├── E-commerce (Amazon Vendor Central)
│   └── Selling Partner API (SP-API) — daily sales velocity by ASIN
├── Foodservice distributors
│   └── EDI 867 (Product Transfer and Resale) — weekly
└── Small independents
    └── Manual upload template (Excel → SharePoint → ETL) — monthly
```

**Weather API Integration**

Weather data is a proven demand driver for temperature-sensitive categories (beverages, seasonal HVAC, agricultural chemicals, ice cream, outdoor leisure):

```python
import requests

def fetch_weather_forecast(
    location_lat: float,
    location_lon: float,
    forecast_weeks: int = 13,
    api_key: str = None
) -> pd.DataFrame:
    """
    Fetch weekly weather forecast for demand planning use.
    
    Recommended provider: Open-Meteo (open-source, no API key for basic use)
    API docs: https://open-meteo.com/en/docs
    """
    base_url = "https://api.open-meteo.com/v1/forecast"
    
    params = {
        'latitude': location_lat,
        'longitude': location_lon,
        'daily': ['temperature_2m_max', 'temperature_2m_min', 
                   'precipitation_sum', 'windspeed_10m_max'],
        'forecast_days': min(forecast_weeks * 7, 92),  # max 92 days
        'timezone': 'UTC',
    }
    
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    
    daily = response.json()['daily']
    df = pd.DataFrame({
        'date': pd.to_datetime(daily['time']),
        'temp_max': daily['temperature_2m_max'],
        'temp_min': daily['temperature_2m_min'],
        'precipitation': daily['precipitation_sum'],
    })
    
    # Aggregate to weekly
    df['week'] = df['date'].dt.to_period('W')
    weekly = df.groupby('week').agg({
        'temp_max': 'mean',
        'temp_min': 'mean',
        'precipitation': 'sum'
    }).reset_index()
    
    # Compute temperature index (z-score vs historical seasonal mean)
    # Historical baseline must be pre-loaded from climatology database
    weekly['temperature_index'] = compute_temperature_index(weekly, location_lat, location_lon)
    
    return weekly
```

**Promotion Calendar Integration**

The promotional calendar is the single highest-impact causal variable for consumer goods demand planning. Integrate it as structured data, not as free-text email attachments:

```
Commercial team → Promotion Planning Tool (custom or SAP Trade Promotion Management)
        |
        | Automated export (daily at 06:00 UTC)
        v
Promotion Calendar Table (in data lake):
  Fields: sku_id, location_id, promo_start, promo_end, promo_type, 
          expected_discount_pct, expected_volume_uplift_pct, 
          channel, key_account, approved_flag
        |
        | Consumed by
        v
Prophet (holiday events) + LightGBM (as feature) + TFT (time-varying known)
```

### 8.3 Automation Architecture

**Automated monthly planning cycle (no manual trigger required):**

```yaml
# Azure Data Factory or Airflow DAG (simplified)

dag_id: monthly_demand_planning_cycle
schedule: "0 5 * * 1"  # Every Monday at 05:00 UTC

tasks:
  1_extract_actuals:
    type: SAP_S4HANA_extraction
    source: SD billing documents, week T-1
    target: data_lake/raw/demand_actuals/

  2_cleanse_history:
    type: Python_batch
    script: cleanse_demand_history.py
    depends_on: [1_extract_actuals]

  3_run_statistical_models:
    type: Python_batch
    script: run_statistical_baseline.py  # SES, Holt-Winters, SMA
    depends_on: [2_cleanse_history]
    parallelism: 16  # 16 parallel SKU batches

  4_run_ml_models:
    type: Python_batch
    script: run_ml_forecasts.py  # LightGBM, TFT
    depends_on: [2_cleanse_history]
    gpu_required: true

  5_generate_safety_stock:
    type: Python_batch
    script: compute_safety_stock.py
    depends_on: [3_run_statistical_models, 4_run_ml_models]

  6_upload_to_ibp:
    type: IBP_API_upload
    depends_on: [3_run_statistical_models, 4_run_ml_models, 5_generate_safety_stock]

  7_trigger_exception_alerts:
    type: IBP_alert_management
    depends_on: [6_upload_to_ibp]

  8_update_accuracy_dashboard:
    type: Power_BI_dataset_refresh
    depends_on: [6_upload_to_ibp]
```

---

## 9. Phase 6: Continuous Improvement & Centre of Excellence

**Duration:** Ongoing (commences month 16)  
**Owner:** VP Demand Planning / CoE Director  
**Gate criterion:** CoE formally chartered, staffed, and operating; model governance cadence established; first annual forecast accuracy improvement cycle completed

### 9.1 Centre of Excellence (CoE) Structure

The CoE is the institutional capability that prevents the implementation from degrading over time. Without it, model parameters drift, planner overrides erode statistical discipline, and the organisation reverts to Excel-based planning within 18–24 months of go-live.

**CoE Organisational Model:**

```
CoE Director (VP/Director level, reports to CSCO)
├── Process Excellence Lead (S&OP design, KPI governance)
├── Data Science Lead (model governance, retraining, new model research)
├── Data Engineering Lead (pipeline reliability, data quality SLAs)
├── Change & Training Lead (onboarding new planners, capability building)
└── Regional Planning Champions (40 countries, dotted-line to CoE)
    ├── Europe Hub (covering EMEA)
    ├── Americas Hub
    └── APAC / MEA Hub
```

**CoE operating cadence:**

| Forum | Frequency | Agenda |
|-------|-----------|--------|
| Model Performance Review | Monthly | WMAPE by model/region, drift alerts, retraining decisions |
| Data Quality Review | Monthly | Completeness scores, pipeline failures, master data exceptions |
| Process Governance | Quarterly | S&OP process adherence, override value-add analysis |
| Technology Roadmap | Quarterly | New model evaluation, tool upgrades, feature requests |
| Annual Capability Review | Annual | Benchmark vs. industry peers (Gartner, APICS survey data) |

### 9.2 Model Governance and Retraining Policy

**Mandatory retraining triggers (any one of the following):**
1. WMAPE deteriorates > 5 percentage points vs. baseline for 2 consecutive months
2. Forecast bias (tracking signal) exceeds ±4 for 6 consecutive weeks
3. Major structural demand change: new channel launch, competitor exit, significant price change
4. Annual scheduled refit (regardless of accuracy — prevents silent parameter staleness)

**Model promotion workflow (four-eyes principle):**

```
Data Scientist trains new model version
        |
        | MLflow experiment logged
        v
Automated backtesting on hold-out data (last 13 weeks, never used in training)
        |
        | Must beat champion model by ≥ 2% WMAPE on hold-out
        v
Peer review by second Data Scientist (code review + results review)
        |
        | Approval in model registry
        v
Shadow run: new model runs in parallel with champion for 4 weeks (no business impact)
        |
        | Shadow performance validated
        v
Champion model replaced — previous version archived in MLflow (not deleted)
```

### 9.3 Continuous Capability Building

**Forecasting literacy programme (all 40 countries):**

- **Level 1 (all planners, 4 hours):** What is WMAPE? How to read the accuracy dashboard. How to log overrides correctly. When to trust the statistical model vs. override.
- **Level 2 (senior planners, 2 days):** Statistical model mechanics. How to configure exception alerts. Promotional lift interpretation. Demand sensing signals.
- **Level 3 (CoE members, 5 days):** ML model interpretation. SHAP analysis. Model governance. Python scripting for ad hoc demand analysis.

---

## 10. Technology Stack & Architecture

### 10.1 Architecture Overview

```
Data Sources
├── SAP S/4HANA (SD, MM, PP) — primary ERP
├── POS feeds (EDI 852, SFTP, API)
├── Weather API (Open-Meteo)
├── Promotion Calendar (SAP TPM or custom)
└── Supplier lead time data (SAP MM / Ariba)
          |
          | Azure Data Factory (ingestion pipelines)
          v
Azure Data Lake Storage Gen2 (raw + cleansed zones)
          |
          | Azure Databricks (PySpark for large-scale transformation)
          v
Feature Store (Delta Lake format)
          |
          |----> Statistical Models (Python, statsmodels, scipy) — Azure Functions
          |----> ML Models (PyTorch, LightGBM, Prophet) — Azure ML / Databricks GPU
          |
          v
SAP IBP (demand planning, S&OP workflow, supply planning)
          |
          | SAP Integration Suite (CIF)
          v
SAP S/4HANA (MRP, purchase requisitions, production orders)
          |
          v
Power BI (forecast accuracy dashboard, exception reports)
          |
          v
Planners (web UI: SAP IBP Fiori / Power BI embedded)
```

### 10.2 Technology Selection Rationale

| Component | Selected Technology | Rationale |
|-----------|--------------------|-|
| Cloud platform | Microsoft Azure | Consistent with SAP IBP (Azure-hosted); Office 365 integration |
| ERP | SAP S/4HANA | Existing backbone — no change |
| Demand Planning | SAP IBP | Native S/4HANA integration; IBP supply planning included |
| Data orchestration | Azure Data Factory + Databricks | Enterprise-grade; PySpark for 10M+ row processing |
| ML platform | Azure ML + MLflow | Experiment tracking, model registry, deployment |
| Statistical models | Python (statsmodels, scipy) | OSI-licensed; team proficiency |
| ML models | LightGBM, PyTorch, Prophet | OSI-licensed (MIT/BSD/Apache) |
| Visualisation | Power BI + SAP Analytics Cloud | BI for planners; SAC for SAP-native users |
| Model serving | Azure ML Online Endpoints | Low-latency demand sensing (W+1 to W+4) |
| Feature store | Databricks Feature Store | Consistent feature computation across training and inference |

### 10.3 Python Environment

All Python code must run in a controlled virtual environment with pinned dependency versions:

```toml
# pyproject.toml (excerpt)
[tool.poetry.dependencies]
python = ">=3.11,<3.13"
numpy = "^1.26"
pandas = "^2.2"
scipy = "^1.13"
statsmodels = "^0.14"
scikit-learn = "^1.5"
lightgbm = "^4.4"
torch = "^2.3"
prophet = "^1.1"
optuna = "^3.6"
shap = "^0.45"
mlflow = "^2.14"
gluonts = "^0.15"
pytorch-forecasting = "^1.0"
```

---

## 11. Change Management & Training

### 11.1 Stakeholder Map and Engagement Strategy

The most common failure mode in demand planning implementations is not technical — it is organisational. Planners who distrust the model, sales teams who refuse to provide structured promotional input, and finance teams who insist on reconciling to budget rather than statistical forecast will undermine the investment regardless of model accuracy.

**Stakeholder map:**

| Stakeholder | Concern | Engagement Strategy |
|-------------|---------|---------------------|
| Demand Planners | Fear of automation replacing their role | Reframe: model handles routine SKUs, planner focuses on exceptions and commercial insight |
| Sales/Commercial | "My forecast is better; I know my customers" | Track override value-add; use data to show where model beats commercial overrides |
| Supply Planning | Need reliable 13-week horizon | Show WMAPE improvement at M+3; tie forecast to supply plan improvements |
| Finance | Demand plan must reconcile to financial budget | Build reconciliation report; show demand plan as best estimate, budget as target |
| CSCO / Leadership | ROI and timeline risk | Monthly steering committee; phased go-live reduces risk; clear value milestones |
| IT / SAP Team | Integration complexity; system stability | Involve IT from Phase 0; use standard SAP integration patterns; clear test protocols |

### 11.2 Communication Plan

**Key messages by phase:**

- **Phase 0–1:** "We are building the foundation — don't expect immediate forecast improvement. Expect data quality improvement and a cleaner process." Manage expectations actively.
- **Phase 2–3:** "Statistical baseline is live. We are measuring for the first time. Results will be mixed initially — this is expected and normal."
- **Phase 4–5:** "ML models are outperforming statistical baseline in pilot. We are validating before broader rollout."
- **Phase 6:** "We are now in continuous improvement mode. The CoE is the permanent home of this capability."

### 11.3 Training Curriculum

**Module 1: Demand Planning Fundamentals (all planners — 4 hours)**
- What is a statistical forecast and why it is better than intuition for stable SKUs
- How to read the IBP demand planning screen
- Override logging: mandatory fields and reason codes
- Escalation path for data quality issues

**Module 2: S&OP Process (planners + commercial team — 1 day)**
- Monthly S&OP calendar — roles, responsibilities, deliverables
- How to load promotional assumptions in IBP
- How to interpret and act on forecast exceptions
- Consensus forecast vs. statistical baseline — when to override and when to trust

**Module 3: Advanced Analytics (senior planners + CoE — 2 days)**
- Interpreting SHAP outputs from LightGBM demand sensing
- ABC-XYZ classification — how to challenge or escalate reclassifications
- Safety stock formula mechanics — how to validate IBP recommendations
- How to run an ad hoc forecast scenario in IBP (what-if analysis)

---

## 12. KPIs to Measure Implementation Success

### 12.1 Forecast Accuracy KPIs

| KPI | Definition | Baseline (AS-IS) | Year 1 Target | Year 2 Target |
|-----|-----------|-----------------|---------------|---------------|
| WMAPE M+1 | Weighted MAE / Total Actual × 100 | Measure in Phase 0 | Baseline −8pp | Baseline −14pp |
| WMAPE M+3 | As above, 3-month horizon | Measure in Phase 0 | Baseline −6pp | Baseline −10pp |
| WMAPE M+6 | As above, 6-month horizon | Measure in Phase 0 | Baseline −4pp | Baseline −8pp |
| Forecast Bias | Mean Error / Mean Actual × 100% | Measure in Phase 0 | ±5% | ±3% |
| Override Value-Add | (Consensus WMAPE − Statistical WMAPE) | Not measured | > 0% (positive) | > +2% |
| A-class SKU accuracy | WMAPE for A-class only (M+1) | Measure in Phase 0 | < 12% | < 10% |

### 12.2 Supply Chain Performance KPIs

| KPI | Definition | Baseline | Year 1 | Year 2 |
|-----|-----------|---------|--------|--------|
| Fill Rate | Orders shipped complete / Orders received | ~90% | 95% | 97.5% |
| OTIF | On-Time In-Full delivery rate | Measure | 93% | 95% |
| Inventory Turnover | COGS / Average Inventory | Measure | +10% improvement | +20% improvement |
| Days Inventory Outstanding | 365 / Inventory Turnover | Measure | −5 days | −10 days |
| Safety Stock € | Total € value in safety stock | Measure | −10% | −20% |
| Excess & Obsolete % | Inventory aged > 180 days / Total | Measure | −15% | −25% |

### 12.3 Process Efficiency KPIs

| KPI | Definition | Target |
|-----|-----------|--------|
| Planner time on data prep | % of planning time spent on data collection/cleaning | < 20% (from ~60%) |
| Exceptions reviewed per week | % of IBP exceptions actioned within SLA | > 95% |
| S&OP cycle adherence | % of months S&OP completed on schedule | > 90% |
| Override documentation rate | % of overrides with complete reason code | 100% (mandatory) |
| Model retrain adherence | % of scheduled retrains completed on time | > 95% |

### 12.4 ROI KPIs (Financial)

| KPI | Definition | Year 1 Target | Year 2 Target | Year 3 Target |
|-----|-----------|--------------|--------------|--------------|
| Working Capital Reduction | Reduction in average inventory × WACC | €50M | €150M | €250M |
| Revenue Protected | Revenue saved from reduced stockouts | €20M | €60M | €100M |
| Expediting Cost Reduction | Reduction in air freight / premium logistics | €5M | €15M | €25M |
| Obsolescence Reduction | Reduction in write-offs | €10M | €30M | €50M |

---

## 13. Risk & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Data quality insufficient for ML models | High | High | Phase 0 data audit mandatory gate; ML deferred if data quality < 80% |
| SAP IBP go-live delayed (licence, infra) | Medium | High | Parallel-run Python models independently; IBP integration Phase 5 can be deferred without blocking Phase 3 accuracy improvement |
| Planner resistance to statistical forecast | High | Medium | Override value-add tracking; SHAP explanations; coaching programme; management reinforcement |
| ML model accuracy worse than statistical baseline | Medium | Medium | Model evaluation gate: ML only promoted if it beats statistical baseline by ≥ 2% WMAPE in backtesting |
| Key data scientist turnover | Medium | High | Knowledge documentation in MLflow and Confluence; team of minimum 3 DS (no single point of failure); CoE embedded in organisation |
| POS data feed quality (retailer cooperation) | Medium | Medium | Start with 2–3 key accounts as pilot; demonstrate value to expand; fallback to EDI 867 if POS unavailable |
| Scope creep (adding new features before baseline stable) | High | Medium | Strict phase gates; change control board; CoE Director as gatekeeper |
| Regulatory change (GDPR applied to customer POS data) | Low | High | Legal review of POS data processing agreements before Phase 5; anonymisation pipeline for individual-level POS data |
| SAP S/4HANA upgrade incompatibility | Low | Medium | Freeze S/4HANA release during Phase 1–5 integration (minimum 12-month moratorium on major upgrades); test in dev client first |
| Bullwhip amplification from ML model instability | Low | High | Production rollout limited to 20% of A-class SKUs initially; monitor bullwhip ratio weekly post-rollout |

---

## 14. Timeline Summary Table

| Phase | Activity | Duration | Start | End | Key Milestone |
|-------|----------|----------|-------|-----|---------------|
| 0 | Assessment & AS-IS Analysis | 8 weeks | Month 1 | Month 2 | AS-IS report signed off; data quality scored |
| 1 | Foundation & Master Data | 10 weeks | Month 2 | Month 4 | ABC-XYZ loaded in IBP; cleansed history available |
| 2 | Process Standardisation | 8 weeks | Month 3 | Month 5 | Global S&OP process live; accuracy measurement active |
| 3 | Mathematical Models | 12 weeks | Month 4 | Month 7 | Statistical baseline live in IBP; SS policy deployed |
| 4 | ML/AI Pipeline | 14 weeks | Month 6 | Month 9 | LightGBM demand sensing live; TFT in shadow mode |
| 5 | Integration & Automation | 12 weeks | Month 8 | Month 11 | Full IBP automation; POS feeds integrated |
| 6 | CoE & Continuous Improvement | Ongoing | Month 13 | Ongoing | CoE chartered; first annual model refit complete |
| — | Stabilisation & Handover | 4 weeks | Month 14 | Month 15 | All models in production; SI partner exits; CoE operational |
| — | First Annual Review | 2 weeks | Month 18 | Month 18 | WMAPE improvement vs. baseline documented; ROI confirmed |

**Note on phasing overlaps:** Phases 3 and 4 overlap deliberately (Phase 4 begins in month 6 while Phase 3 runs until month 7). This allows ML model development to begin on the cleaned data while statistical models are being validated. However, Phase 4 models cannot enter production until Phase 3 statistical baseline is confirmed — statistical models serve as the evaluation benchmark for ML model gate criteria.

**Dependency constraint:** Phase 5 (Integration & Automation) cannot begin before Phase 3 models are running in IBP (the integration is designed to serve statistical baseline first, ML models second). Phase 6 (CoE) begins in month 13, overlapping with the end of Phase 5, to ensure knowledge transfer before SI partner exit.

---

## 15. References

### Academic & Foundational

1. **Holt, C.C. (1957).** Forecasting seasonals and trends by exponentially weighted moving averages. *ONR Memorandum 52*, Carnegie Institute of Technology. (Reprinted in *International Journal of Forecasting*, 20(1), 5–10, 2004.)

2. **Winters, P.R. (1960).** Forecasting sales by exponentially weighted moving averages. *Management Science*, 6(3), 324–342.

3. **Gardner, E.S. & McKenzie, E. (1985).** Forecasting trends in time series. *Management Science*, 31(10), 1237–1246. *(Trend dampening)*

4. **Harris, F.W. (1913).** How many parts to make at once. *Factory: The Magazine of Management*, 10(2), 135–136, 152. *(EOQ)*

5. **Syntetos, A.A. & Boylan, J.E. (2005).** The accuracy of intermittent demand estimates. *International Journal of Forecasting*, 21(2), 303–314.

6. **Lim, B., Arık, S.Ö., Loeff, N. & Pfister, T. (2021).** Temporal Fusion Transformers for interpretable multi-horizon time series forecasting. *International Journal of Forecasting*, 37(4), 1748–1764.

7. **Salinas, D., Flunkert, V., Gasthaus, J. & Januschowski, T. (2020).** DeepAR: Probabilistic forecasting with autoregressive recurrent networks. *International Journal of Forecasting*, 36(3), 1181–1191.

### Books

8. **Chopra, S. & Meindl, P. (2016).** *Supply Chain Management: Strategy, Planning and Operation*, 6th Edition. Pearson.

9. **Makridakis, S., Wheelwright, S.C. & Hyndman, R.J. (1998).** *Forecasting: Methods and Applications*, 3rd Edition. Wiley.

10. **Hyndman, R.J. & Athanasopoulos, G. (2021).** *Forecasting: Principles and Practice*, 3rd Edition. OTexts. Available free at: https://otexts.com/fpp3/

11. **Christopher, M. (2022).** *Logistics and Supply Chain Management*, 6th Edition. FT Publishing / Pearson.

12. **Ballou, R.H. (2004).** *Business Logistics / Supply Chain Management*, 5th Edition. Pearson.

### Standards & Regulations

13. **ASCM (2019).** *SCOR Digital Standard (SCOR-DS)*. Association for Supply Chain Management.

14. **ISO 28000:2022.** *Security and resilience — Security management systems — Requirements*. ISO.

15. **ISO 9001:2015.** *Quality management systems — Requirements*. ISO.

16. **GS1 (2023).** *GS1 General Specifications Version 23.0*. GS1.

17. **ICC (2019).** *Incoterms® 2020*. International Chamber of Commerce.

### Industry & Practitioner Sources

18. **Gartner (2024).** *Supply Chain Planning Magic Quadrant*. Gartner Research.

19. **APICS Dictionary, 16th Edition (2024).** ASCM.

20. **Prophet documentation (Meta / Facebook AI).** https://facebook.github.io/prophet/

21. **LightGBM documentation.** https://lightgbm.readthedocs.io/ (Microsoft, MIT License)

22. **PyTorch Forecasting documentation.** https://pytorch-forecasting.readthedocs.io/ (MIT License)

23. **GluonTS documentation (Amazon Research).** https://ts.gluon.ai/ (Apache-2.0)

24. **Optuna documentation.** https://optuna.readthedocs.io/ (MIT License)

25. **Open-Meteo API documentation.** https://open-meteo.com/en/docs (Open-source weather API)

---

*Document Owner: VP Demand Planning / CoE Director*  
*Next Review Date: 2026-12-20*  
*Classification: Internal — Confidential*  
*Distribution: CSCO, VP Demand Planning, VP Supply Chain, CFO, Regional Planning Directors*
