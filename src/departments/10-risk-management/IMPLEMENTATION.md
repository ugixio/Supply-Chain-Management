# Supply Chain Risk Analytics — Implementation Playbook
# Department 10 — Risk Management

**Classification:** Internal — Restricted
**Version:** 2.0
**Date:** 2026-06-22
**Standard:** ISO 31000:2018, ISO 28000:2022, SCOR-DS Enable
**Owner:** Chief Supply Chain Officer (CSCO) / Risk Director
**Reporting cadence:** Monthly operational; Quarterly Board Risk Committee

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Analysis Objective](#2-analysis-objective)
3. [Scope](#3-scope)
4. [Business Questions](#4-business-questions)
5. [Data Sources](#5-data-sources)
6. [Data Model](#6-data-model)
7. [Data Dictionary](#7-data-dictionary)
8. [Transformation Rules](#8-transformation-rules)
9. [Business Rules](#9-business-rules)
10. [KPIs and Formulas](#10-kpis-and-formulas)
11. [Analytical Logic](#11-analytical-logic)
12. [Validations and Controls](#12-validations-and-controls)
13. [Required Evidence](#13-required-evidence)
14. [Dashboard Design](#14-dashboard-design)
15. [Use Cases](#15-use-cases)
16. [Recommended Actions](#16-recommended-actions)
17. [Test Cases](#17-test-cases)
18. [Risks and Mitigations](#18-risks-and-mitigations)
19. [Implementation Checklist](#19-implementation-checklist)
20. [Validation Checklist](#20-validation-checklist)
21. [Pending Information](#21-pending-information)
22. [Implementation Roadmap](#22-implementation-roadmap)

---

## 1. Executive Summary

Global supply chains face an accelerating frequency of high-impact disruptions: geopolitical
conflict, climate-related logistics shocks, single-source supplier failures, and commodity
concentration risk. The 2021 Suez Canal blockage demonstrated that a single node failure can
lock up USD 9.6 billion per day in trade. The COVID-19 pandemic exposed the systemic fragility
of just-in-time networks with zero resilience buffers. In this environment, reactive risk
management is no longer acceptable for a €50B multinational operating across 40 countries.

This playbook establishes a quantitative, ISO 31000-compliant Supply Chain Risk Analytics
capability. The programme covers five analytics domains: Supply Risk Register (5×5 matrix with
inherent vs. residual scoring), Supplier Concentration Risk (HHI by procurement category),
Supply Disruption Early Warning (ML-driven, 90-day horizon), Bullwhip Effect measurement per
supply link, and Business Continuity Coverage tracking.

**Technology stack:** SAP S/4HANA (transactional source), custom risk register on Azure SQL /
SharePoint (risk owners), Python with Monte Carlo simulation (quantitative risk models),
Power BI (dashboards).

**Business case:**
- Estimated annual disruption cost (baseline): USD 42M
- Year 2 target disruption cost: USD 18M
- Investment: USD 4–6M over two years
- Payback: one avoided Tier-1 supplier failure event (industry avg disruption cost: USD 184M,
  Allianz AGCS 2023)

---

## 2. Analysis Objective

The Supply Chain Risk Analytics programme addresses five analytical objectives:

1. **Supply Risk Register:** Maintain a living 5×5 risk register for all identified supply chain
   risks. Compute inherent risk score (Likelihood × Impact) and residual risk score (accounting
   for control effectiveness). Prioritise mitigation budget by Expected Annual Loss (EAL).

2. **Supplier Concentration Risk (HHI):** Compute the Herfindahl-Hirschman Index per procurement
   category monthly. Identify categories with HHI > 2500 (highly concentrated) and track progress
   of dual-source programmes.

3. **Supply Disruption Early Warning:** Deploy an ML-driven early warning system combining NLP
   news signals, macro-economic indicators (PMI, BDI, GPR), and supplier financial distress
   signals to generate 90-day forward disruption probability scores by supplier.

4. **Bullwhip Effect Measurement:** Compute the Bullwhip Ratio (Var(orders) / Var(demand)) per
   SKU-supplier link on a rolling 12-month window. Identify links with BWE > 2.0 and decompose
   into four root causes (demand signal processing, rationing gaming, order batching, price
   fluctuation).

5. **Business Continuity Coverage:** Track the percentage of critical business processes with a
   tested and current Business Continuity Plan (BCP). Monitor Time-to-Survive (TTS) and
   Time-to-Recover (TTR) gaps for critical supply nodes.

---

## 3. Scope

### In Scope

| Dimension | Coverage |
|-----------|----------|
| Risk domains | Supply, Demand, Process, Environmental, Geopolitical, Cyber, Regulatory, Financial |
| Supplier tiers | Tier-1 (all), Tier-2 (strategic categories) |
| Geography | 40 countries of operation; all critical supply nodes |
| SKUs | All strategic and bottleneck items (Kraljic: STRATEGIC + BOTTLENECK classification) |
| Systems | SAP S/4HANA, Azure SQL risk register (SharePoint front-end), Python Monte Carlo, Power BI |
| BCP scope | All critical business processes with RTO < 72 hours |
| Reporting | Monthly to CSCO; Quarterly to Board Risk Committee |

### Out of Scope

- Financial market risk (FX, interest rate hedging — handled by Treasury)
- IT infrastructure risk (handled by IT Risk / CISO)
- Reputational risk (handled by Corporate Communications)
- Tier-3+ suppliers (monitored as an aggregate risk flag)

---

## 4. Business Questions

1. Which supply chain risks are currently in the CRITICAL band (score ≥ 15) and what is the
   combined Expected Annual Loss (EAL) of the top-10 risks by EAL?

2. After applying all current mitigation controls, what are the residual risk scores, and are
   there risks where control effectiveness is lower than assumed in the last Board review?

3. Which procurement categories are highly concentrated (HHI > 2500), and what is the annual
   spend and number of sole-source items in each affected category?

4. For the top-3 HHI-concentrated categories, what is the dual-source coverage rate for strategic
   items (Kraljic STRATEGIC classification), and what is the projected HHI reduction if planned
   dual-source programmes are completed?

5. Which suppliers have a disruption probability score > 50% in the next 90 days (ML model
   output), and what early warning signals (news sentiment, financial distress, macro) are
   driving the score?

6. Which SKU-supplier links have a Bullwhip Ratio > 2.0, and what is the dominant cause
   (demand signal processing vs order batching vs rationing vs price fluctuation)?

7. What is the current BCP Coverage percentage for critical processes, and which critical
   processes have no BCP or have a BCP that has not been tested in the past 12 months?

8. For critical supply nodes, what is the Resilience Gap (TTR − TTS), and which nodes have a
   positive gap (i.e., the company cannot survive a disruption without production impact)?

9. What is the trend in the portfolio-level risk score distribution over the past 12 months —
   is the overall risk posture improving or deteriorating?

10. How does our Single-Source Spend % compare to industry benchmark (target: < 20% of total
    spend in sole-source categories), and what are the top-10 single-source items by spend?

11. What is the correlation between Bullwhip Ratio and On-Time Delivery (OTD) performance for
    the affected supplier links, and are high-BWE links also showing OTD degradation?

12. Which risk owners have overdue mitigation actions (action due date < CURRENT_DATE and
    status != COMPLETED), and what is the average age of overdue actions?

---

## 5. Data Sources

### DS-01: SAP S/4HANA Purchase Order and Supplier Data

| Attribute | Value |
|-----------|-------|
| Name | SAP Purchase Orders and Vendor Master |
| System | SAP S/4HANA 2023 |
| Table / View | EKKO (PO header), EKPO (PO line), EKBE (PO history), LFA1 (vendor master), MARA (material master) |
| Owner | Procurement / Master Data Governance |
| Frequency | Daily full extract to analytics layer |
| Fields | PO number, vendor ID, material number, commodity code (material group), quantity ordered, quantity delivered, value EUR cents, document date, delivery date, plant, Incoterm, country of origin |
| Critical Fields | Vendor ID, material group (commodity code), value EUR cents, quantity ordered |
| Primary Key | PO number + line item |
| Validations | Value in integer cents (no floats); vendor ID must exist in vendor master; material group must be in approved commodity taxonomy |
| Known Errors | ~5% of POs have legacy material group codes from pre-SAP systems — mapped to current taxonomy via crosswalk table |
| Evidence | SAP change document log; GR/IR posting log |

---

### DS-02: Risk Register (Azure SQL / SharePoint)

| Attribute | Value |
|-----------|-------|
| Name | Supply Chain Risk Register |
| System | Azure SQL Database (back-end) with SharePoint Power Apps front-end |
| Table / View | dbo.RiskRegister, dbo.MitigationActions, dbo.RiskOwners, dbo.RiskReviews |
| Owner | Risk Director |
| Frequency | Real-time (risk owner updates); daily extract to analytics layer |
| Fields | risk_id (UUID), title, description, risk_category, risk_status, likelihood (1–5), impact (1–5), risk_score (computed), severity_band, control_effectiveness (0–1), residual_risk_score (computed), eal_usd, exposure_factor, aop, risk_owner_id, business_unit, supplier_id, commodity_code, mitigation_actions (JSON), identified_at, last_reviewed_at, next_review_due, is_deleted |
| Critical Fields | likelihood, impact, control_effectiveness, risk_owner_id, next_review_due |
| Primary Key | risk_id (UUID) |
| Validations | likelihood in [1,2,3,4,5]; impact in [1,2,3,4,5]; control_effectiveness in [0,1]; is_deleted = FALSE required for active risks; next_review_due must be populated for all ASSESSED and MITIGATED risks |
| Known Errors | Some legacy risk entries have control_effectiveness = NULL — treated as 0.0 (no control) for conservative residual scoring |
| Evidence | SharePoint audit trail; Risk Review meeting minutes attached as DMS links |

---

### DS-03: Demand and Order History (SAP S/4HANA / BW)

| Attribute | Value |
|-----------|-------|
| Name | Historical Demand and Purchase Order Quantity Series |
| System | SAP S/4HANA + SAP BW/4HANA (time-series extraction) |
| Table / View | MBEW, MSEG, MATDOC (stock movements); custom BW InfoCube for demand history |
| Owner | Demand Planning / Supply Chain Analytics |
| Frequency | Daily extract; 12-month rolling window maintained |
| Fields | Material number, vendor ID, plant, calendar week, quantity ordered (PO), quantity shipped (GR), end-customer demand quantity, demand_date, order_date |
| Critical Fields | Material number, vendor ID, quantity ordered, end-customer demand quantity, dates |
| Primary Key | Material + vendor + plant + calendar week |
| Validations | Quantities must be non-negative integers; demand quantities must be traceable to SO or forecast source; order quantities linked to PO header |
| Known Errors | Statistical forecast vs. actual customer order quantity may diverge — use confirmed SO as demand signal, not statistical forecast |
| Evidence | SAP movement document (MATDOC); sales order confirmation records |

---

### DS-04: Supplier Scorecard and Financial Health Data

| Attribute | Value |
|-----------|-------|
| Name | Supplier Scorecard KPIs + Financial Distress Indicators |
| System | SAP S/4HANA (OTD/OTIF sourced from GR vs. PO schedule), Dun & Bradstreet Paydex (external API) |
| Table / View | ZSM_SCORECARD (custom scorecard table), D&B API response cache |
| Owner | Supplier Management / Procurement Analytics |
| Frequency | Weekly scorecard refresh; monthly D&B financial data |
| Fields | Supplier ID, OTD_pct, OTIF_pct, PPM, NCR_rate, invoice_accuracy_pct, overall_scorecard_score, altman_z_score (D&B), paydex_score, credit_rating, days_beyond_terms, employee_count, annual_revenue_usd, financial_data_date |
| Critical Fields | OTD_pct, altman_z_score, overall_scorecard_score |
| Primary Key | Supplier ID + scorecard_period |
| Validations | OTD_pct in [0,100]; PPM >= 0; Altman Z-score must be from source dated <= 90 days ago; if Altman Z-score unavailable, flag as FINANCIAL_DATA_MISSING |
| Known Errors | Private suppliers may not have D&B data — flagged as FINANCIAL_DATA_UNAVAILABLE; Paydex scores lag by 45–60 days |
| Evidence | D&B API call log with timestamp; GR/IR matching report for OTD calculation |

---

### DS-05: Business Continuity Plans (SharePoint Document Library)

| Attribute | Value |
|-----------|-------|
| Name | Business Continuity Plan (BCP) Registry |
| System | SharePoint Online document library + Azure SQL metadata table |
| Table / View | dbo.BCPRegistry, dbo.BCPTestResults |
| Owner | Business Continuity Manager / Risk Director |
| Frequency | Real-time on BCP upload/update; daily extract to analytics |
| Fields | bcp_id (UUID), process_name, process_category, criticality_level (CRITICAL/HIGH/MEDIUM), rto_hours, rpo_hours, tts_days, ttr_days, resilience_gap_days, bcp_owner, bcp_status (CURRENT/OUTDATED/MISSING), last_test_date, last_test_result (PASS/FAIL/NOT_TESTED), next_test_due, document_url, is_deleted |
| Critical Fields | criticality_level, bcp_status, last_test_date, tts_days, ttr_days |
| Primary Key | bcp_id |
| Validations | For criticality = CRITICAL: bcp_status must not be MISSING; last_test_date not older than 365 days; rto_hours must be populated |
| Known Errors | Some BCP documents are attached as PDF without structured metadata — require manual metadata extraction and entry into Azure SQL registry |
| Evidence | BCP document version history in SharePoint; test exercise reports (post-exercise minutes); BCP owner sign-off |

---

### DS-06: External Risk Signals (API / Web Feeds)

| Attribute | Value |
|-----------|-------|
| Name | External Macro and Disruption Signal Feeds |
| System | Python ETL pipeline consuming external APIs |
| Sources | GDELT 2.0 API (news events), Bloomberg B-PIPE (PMI, BDI, commodity prices), Swiss Re CatNet (natural catastrophe zones), World Bank WGI (country governance), Caldara-Iacoviello GPR Index |
| Owner | Risk Data Engineering |
| Frequency | GDELT: every 15 minutes; Bloomberg: daily; Swiss Re: daily; WB WGI: quarterly; GPR: monthly |
| Fields | Source, event_date, headline, article_url, supplier_entity_match, country, event_category, sentiment_score, pmi_value, bdi_value, gpr_value, cat_loss_estimate_usd, wgi_political_stability |
| Critical Fields | sentiment_score, supplier_entity_match, event_date |
| Primary Key | Composite: source + event_date + headline_hash |
| Validations | sentiment_score in [-1, 1]; supplier_entity_match must be validated against active supplier list; duplicate articles deduplicated by URL hash |
| Known Errors | GDELT may duplicate articles from multiple syndication sources — URL deduplication required before sentiment aggregation |
| Evidence | API call logs with response codes; data quality audit report (monthly) |

---

## 6. Data Model

```
SUPPLY CHAIN RISK ANALYTICS DATA MODEL

[RISK_REGISTER]  ──────────────────────────────────────────────────────────────┐
  risk_id (PK, UUID)                                                           │
  title                                                                        │ 1:N
  risk_category                                                                │
  likelihood (1-5)                                                             ▼
  impact (1-5)                                               [MITIGATION_ACTIONS]
  inherent_risk_score (= L x I)                               action_id (PK, UUID)
  severity_band                                               risk_id (FK)
  control_effectiveness (0-1)                                 description
  residual_risk_score                                         owner
  eal_usd                                                     due_date
  risk_owner_id (FK)                                          status
  supplier_id (FK, optional)                                  cost_estimate_usd
  commodity_code (FK, optional)
  next_review_due
  is_deleted

[SUPPLIER_MASTER]  ────────────────────────────────────────────────────────────┐
  supplier_id (PK)                                                             │
  legal_name                                                       1:N         │
  country                                                                      ▼
  tier                                                  [HHI_SCORING_LOG]
  altman_z_score                                          hhi_id (PK, UUID)
  overall_scorecard_score                                 commodity_code (FK)
  otd_pct                                                 snapshot_date
  disruption_probability_90d (ML output)                  hhi_score
  financial_data_date                                     concentration_band
  is_active                                               supplier_count
                                                          top_supplier_id
                                                          top_supplier_share_pct
                                                          dual_source_trigger

[PO_HISTORY]  ─────────────────────────────────────────────────────────────────┐
  po_number + line_item (PK)                                                   │
  supplier_id (FK)                                             N:1             │
  material_number (FK)                                                         ▼
  commodity_code (FK)                               [BULLWHIP_ANALYSIS_LOG]
  quantity_ordered                                    bwe_id (PK, UUID)
  value_eur_cents                                     material_number (FK)
  document_date                                       supplier_id (FK)
  delivery_date                                       plant
                                                      window_start
                                                      window_end
[DEMAND_HISTORY]                                      bullwhip_ratio
  material_number + plant + week (PK)                 demand_signal_component
  demand_quantity                                     order_batching_component
  order_quantity                                      price_fluctuation_component
  demand_date                                         rationing_gaming_component
  order_date                                          alert_triggered (bool)
                                                      scored_at

[BCP_REGISTRY]  ───────────────────────────────────────────────────────────────┐
  bcp_id (PK, UUID)                                                            │
  process_name                                              1:N                │
  criticality_level                                                            ▼
  rto_hours                                         [BCP_TEST_RESULTS]
  rpo_hours                                           test_id (PK, UUID)
  tts_days                                            bcp_id (FK)
  ttr_days                                            test_date
  resilience_gap_days                                 test_result
  bcp_status                                          test_type (TABLETOP/LIVE)
  last_test_date                                      findings_summary
  next_test_due                                       corrective_actions
  bcp_owner

[DISRUPTION_SIGNAL_LOG]
  signal_id (PK, UUID)
  supplier_id (FK)
  signal_date
  signal_source
  headline
  sentiment_score
  risk_keywords_matched
  alert_level (HIGH/MEDIUM/LOW)
  disruption_probability_90d (at time of signal)
  acknowledged (bool)
  analyst_id
```

---

## 7. Data Dictionary

### Table: RISK_REGISTER (analytical layer)

| Field | Data Type | Granularity | Description | PK | Relationships |
|-------|-----------|-------------|-------------|----|-|
| risk_id | UUID | Risk event | Surrogate key | YES | FK in MITIGATION_ACTIONS |
| title | VARCHAR(255) | Risk event | Short descriptive title | NO | Displayed in dashboard risk table |
| risk_category | ENUM | Risk event | SUPPLY / DEMAND / PROCESS / ENVIRONMENTAL / GEOPOLITICAL / CYBER / REGULATORY / FINANCIAL | NO | Used in heat map category filter |
| likelihood | TINYINT | Risk event | 1-5 scale per ISO 31000 calibrated definitions | NO | Input to inherent_risk_score |
| impact | TINYINT | Risk event | 1-5 scale per revenue impact definitions | NO | Input to inherent_risk_score |
| inherent_risk_score | TINYINT | Risk event | likelihood x impact (1-25) | NO | Derived; determines severity_band |
| severity_band | ENUM | Risk event | CRITICAL / HIGH / MEDIUM / LOW | NO | Derived from inherent_risk_score |
| control_effectiveness | DECIMAL(3,2) | Risk event | [0,1] — assessed effectiveness of current controls | NO | Input to residual_risk_score |
| residual_risk_score | DECIMAL(5,2) | Risk event | inherent_risk_score x (1 - control_effectiveness) | NO | Derived; used in Board reporting |
| eal_usd | DECIMAL(18,2) | Risk event | Expected Annual Loss in USD | NO | EAL = AOP x impact_value x exposure_factor |
| aop | DECIMAL(5,4) | Risk event | Annual Occurrence Probability [0,1] | NO | Input to EAL |
| exposure_factor | DECIMAL(3,2) | Risk event | Fraction of asset value lost if event occurs [0,1] | NO | Input to EAL |
| risk_owner_id | VARCHAR(50) | Risk event | Employee ID of accountable risk owner | NO | FK to HR master |
| supplier_id | VARCHAR(20) | Risk event | Linked supplier (if supply risk) | NO | Optional FK to SUPPLIER_MASTER |
| commodity_code | VARCHAR(10) | Risk event | Linked commodity (if category risk) | NO | Optional FK to commodity taxonomy |
| next_review_due | DATE | Risk event | Date when risk must be formally reviewed | NO | Used in overdue review alert |
| is_deleted | BOOLEAN | Risk event | Soft-delete flag — never hard-deleted per business rules | NO | — |

---

### Table: HHI_SCORING_LOG

| Field | Data Type | Granularity | Description | PK | Relationships |
|-------|-----------|-------------|-------------|----|-|
| hhi_id | UUID | HHI snapshot | Surrogate key | YES | — |
| commodity_code | VARCHAR(10) | Commodity | Procurement commodity taxonomy code | NO | FK to commodity taxonomy |
| snapshot_date | DATE | HHI snapshot | Date of HHI calculation | NO | Used in trend chart |
| hhi_score | DECIMAL(8,2) | Commodity | HHI value (0-10,000) | NO | Drives concentration_band |
| concentration_band | ENUM | Commodity | COMPETITIVE / MODERATE / HIGHLY_CONCENTRATED / MONOPOLY | NO | Derived from hhi_score |
| supplier_count | SMALLINT | Commodity | Number of active suppliers in category | NO | Context for HHI interpretation |
| top_supplier_id | VARCHAR(20) | Commodity | Supplier with largest spend share | NO | FK to SUPPLIER_MASTER |
| top_supplier_share_pct | DECIMAL(5,2) | Commodity | Top supplier percentage of category spend | NO | Single-source risk indicator |
| dual_source_trigger | BOOLEAN | Commodity | TRUE if hhi_score > 2500 | NO | Drives dual-source programme alert |
| total_category_spend_eur | BIGINT | Commodity | Total spend in category EUR cents | NO | Materiality weighting |

---

### Table: BULLWHIP_ANALYSIS_LOG

| Field | Data Type | Granularity | Description | PK | Relationships |
|-------|-----------|-------------|-------------|----|-|
| bwe_id | UUID | BWE snapshot | Surrogate key | YES | — |
| material_number | VARCHAR(18) | SKU | SAP material number | NO | FK to MATERIAL_MASTER |
| supplier_id | VARCHAR(20) | Supplier | FK to SUPPLIER_MASTER | NO | FK |
| plant | VARCHAR(4) | Plant | SAP plant code | NO | — |
| window_start | DATE | Time window | Start of 12-month rolling window | NO | — |
| window_end | DATE | Time window | End of 12-month rolling window | NO | — |
| bullwhip_ratio | DECIMAL(8,4) | Link | Var(orders) / Var(demand) | NO | Alert threshold: > 2.0 |
| chen_lower_bound | DECIMAL(8,4) | Link | Theoretical minimum BWE (Chen 2000) | NO | Comparison benchmark |
| demand_signal_component | DECIMAL(6,4) | Link | Bullwhip attributed to forecast error amplification | NO | Root cause decomposition |
| order_batching_component | DECIMAL(6,4) | Link | Bullwhip attributed to periodic order batching | NO | Root cause decomposition |
| price_fluctuation_component | DECIMAL(6,4) | Link | Bullwhip attributed to price-driven forward buying | NO | Root cause decomposition |
| rationing_gaming_component | DECIMAL(6,4) | Link | Residual — attributed to shortage gaming | NO | Root cause decomposition |
| alert_triggered | BOOLEAN | Link | TRUE if bullwhip_ratio > 2.0 | NO | Drives communication protocol |
| scored_at | TIMESTAMP | Snapshot | UTC timestamp of computation | NO | Freshness monitoring |

---

### Table: BCP_REGISTRY

| Field | Data Type | Granularity | Description | PK | Relationships |
|-------|-----------|-------------|-------------|----|-|
| bcp_id | UUID | BCP process | Surrogate key | YES | FK in BCP_TEST_RESULTS |
| process_name | VARCHAR(255) | Process | Name of critical business process | NO | — |
| process_category | ENUM | Process | PROCUREMENT / MANUFACTURING / LOGISTICS / FINANCE / IT | NO | — |
| criticality_level | ENUM | Process | CRITICAL / HIGH / MEDIUM | NO | CRITICAL = included in BCP Coverage KPI |
| rto_hours | SMALLINT | Process | Recovery Time Objective in hours | NO | Must be <= 72 for CRITICAL |
| rpo_hours | SMALLINT | Process | Recovery Point Objective in hours | NO | — |
| tts_days | DECIMAL(5,1) | Process | Time to Survive in days before operational impact | NO | From resilience model |
| ttr_days | DECIMAL(5,1) | Process | Time to Recover in days to restore supply | NO | From resilience model |
| resilience_gap_days | DECIMAL(5,1) | Process | ttr_days minus tts_days | NO | Derived; positive = vulnerable |
| bcp_status | ENUM | Process | CURRENT / OUTDATED / MISSING | NO | OUTDATED if > 12 months since test |
| last_test_date | DATE | Process | Date of most recent BCP test exercise | NO | Alert if > 365 days ago |
| next_test_due | DATE | Process | Next scheduled test exercise | NO | — |
| bcp_owner | VARCHAR(100) | Process | Name of accountable BCP owner | NO | — |
| is_deleted | BOOLEAN | Process | Soft-delete flag | NO | — |

---

### Table: DISRUPTION_SIGNAL_LOG

| Field | Data Type | Granularity | Description | PK | Relationships |
|-------|-----------|-------------|-------------|----|-|
| signal_id | UUID | Signal event | Surrogate key | YES | — |
| supplier_id | VARCHAR(20) | Supplier | Matched supplier | NO | FK to SUPPLIER_MASTER |
| signal_date | TIMESTAMP | Signal event | UTC timestamp of article or signal | NO | — |
| signal_source | ENUM | Signal | GDELT / BLOOMBERG / INTERNAL / MANUAL | NO | — |
| headline | VARCHAR(500) | Signal event | News headline or risk description | NO | Displayed in EWS dashboard |
| sentiment_score | DECIMAL(4,3) | Signal event | [-1, 1] — negative = adverse signal | NO | Threshold: < -0.60 triggers alert |
| risk_keywords_matched | VARCHAR(500) | Signal event | Comma-separated matched keywords | NO | — |
| alert_level | ENUM | Signal event | HIGH / MEDIUM / LOW | NO | HIGH if sentiment < -0.80 |
| disruption_probability_90d | DECIMAL(4,3) | Signal event | ML model P(disruption in 90 days) at signal time | NO | [0,1] |
| acknowledged | BOOLEAN | Signal event | Analyst has reviewed this signal | NO | Unacknowledged signals flagged |
| analyst_id | VARCHAR(50) | Signal event | Acknowledging analyst | NO | Audit trail |

---

## 8. Transformation Rules

### TR-01: Inherent Risk Score Computation

Source: `RISK_REGISTER.likelihood`, `RISK_REGISTER.impact`

```
inherent_risk_score = likelihood x impact   (integer, range 1-25)

severity_band =
  CASE
    WHEN inherent_risk_score >= 15 THEN 'CRITICAL'
    WHEN inherent_risk_score >= 10 THEN 'HIGH'
    WHEN inherent_risk_score >= 5  THEN 'MEDIUM'
    ELSE                                'LOW'
  END
```

---

### TR-02: Residual Risk Score Computation

Source: `RISK_REGISTER.inherent_risk_score`, `RISK_REGISTER.control_effectiveness`

```
residual_risk_score = inherent_risk_score x (1 - control_effectiveness)

Note: If control_effectiveness IS NULL (legacy records), default to 0.0 (no control applied).
residual_severity_band uses same threshold logic as inherent (TR-01) applied to residual_risk_score.
```

---

### TR-03: Expected Annual Loss (EAL)

Source: `RISK_REGISTER.aop`, `RISK_REGISTER.impact_value_usd`, `RISK_REGISTER.exposure_factor`

```
eal_usd = aop x impact_value_usd x exposure_factor

Where:
  aop                = annual_occurrence_probability [0,1]
  impact_value_usd   = revenue or asset value at risk (USD, provided by risk owner)
  exposure_factor    = fraction of impact_value_usd lost if event occurs [0,1]
```

---

### TR-04: HHI Calculation per Commodity Category

Source: `PO_HISTORY` — rolling 12-month spend by supplier x commodity

```
For each commodity_code:
  total_spend = SUM(value_eur_cents WHERE commodity_code = C AND document_date >= NOW() - 365)

  For each supplier i in commodity_code C:
    share_i = supplier_spend_i / total_spend

  hhi = SUM(share_i ^ 2) x 10000   (range: 0-10000)

concentration_band =
  CASE
    WHEN hhi = 10000             THEN 'MONOPOLY'
    WHEN hhi > 2500              THEN 'HIGHLY_CONCENTRATED'
    WHEN hhi > 1500              THEN 'MODERATE'
    ELSE                              'COMPETITIVE'
  END

dual_source_trigger = (hhi > 2500)
```

---

### TR-05: Single-Source Spend Percentage

Source: `PO_HISTORY` aggregated by commodity

```
single_source_categories =
  SELECT commodity_code, total_spend
  FROM HHI_SCORING_LOG
  WHERE snapshot_date = (most recent month-end)
    AND supplier_count = 1   (sole-source category)

single_source_spend_pct =
  SUM(single_source_categories.total_spend) / SUM(all_categories.total_spend) x 100
```

---

### TR-06: Bullwhip Ratio Computation (Rolling 12-Month Window)

Source: `DEMAND_HISTORY` and `PO_HISTORY` — matched by material + supplier + plant

```python
import numpy as np

def compute_bullwhip_ratio(order_series: np.ndarray,
                           demand_series: np.ndarray) -> float:
    """
    Compute empirical Bullwhip Ratio for a 12-month rolling window.
    Both series must have equal length and >= 10 observations.
    Weekly granularity recommended (52 observations per 12-month window).
    """
    if len(order_series) != len(demand_series):
        raise ValueError("Series length mismatch")
    if len(order_series) < 10:
        raise ValueError("Minimum 10 observations required")

    var_orders = np.var(order_series, ddof=1)
    var_demand = np.var(demand_series, ddof=1)

    if var_demand == 0:
        raise ValueError("Demand variance is zero — BWE undefined")

    return round(var_orders / var_demand, 4)
```

---

### TR-07: Resilience Gap Calculation

Source: `BCP_REGISTRY.tts_days`, `BCP_REGISTRY.ttr_days`

```
resilience_gap_days = ttr_days - tts_days

is_resilient = (resilience_gap_days <= 0)
buffer_uplift_required_days = MAX(0, resilience_gap_days x 1.2)   (20% safety margin)

Where:
  tts_days = (buffer_inventory_units / avg_daily_demand) + contractual_buffer_days
  ttr_days = detection_days + decision_days + alternate_supplier_ramp_days
```

---

### TR-08: BCP Coverage Calculation

Source: `BCP_REGISTRY`

```
bcp_covered_count =
  COUNT(bcp_id WHERE criticality_level = 'CRITICAL'
                 AND bcp_status = 'CURRENT'
                 AND last_test_date >= CURRENT_DATE - 365
                 AND last_test_result = 'PASS')

total_critical_count =
  COUNT(bcp_id WHERE criticality_level = 'CRITICAL'
                 AND is_deleted = FALSE)

bcp_coverage_pct = bcp_covered_count / total_critical_count x 100
```

---

### TR-09: Dual-Source Coverage for Strategic Items

Source: `PO_HISTORY` + Kraljic classification from `MATERIAL_MASTER` extension

```
strategic_items_with_2plus_suppliers =
  COUNT(DISTINCT material_number
        WHERE kraljic_classification = 'STRATEGIC'
          AND (SELECT COUNT(DISTINCT supplier_id)
               FROM PO_HISTORY p
               WHERE p.material_number = m.material_number
                 AND p.document_date >= CURRENT_DATE - 365) >= 2)

total_strategic_items =
  COUNT(DISTINCT material_number WHERE kraljic_classification = 'STRATEGIC')

dual_source_coverage_pct =
  strategic_items_with_2plus_suppliers / total_strategic_items x 100
```

---

## 9. Business Rules

### BR-01: CRITICAL Risk Escalation Protocol

| Attribute | Value |
|-----------|-------|
| Name | CRITICAL Risk Immediate Escalation |
| Condition | inherent_risk_score >= 15 OR residual_risk_score >= 15 |
| Result | Automated notification to CSCO + Board Risk Committee within 1 hour; BCP activation check within 4 hours; war-room convened within 24 hours; weekly status updates via GRC task |
| Example | Sole-source semiconductor supplier with factory fire (Likelihood=5, Impact=4, score=20) triggers escalation within 1 hour of risk identification in register |
| Exception | Risk already MITIGATED with control_effectiveness >= 0.70 — escalation goes to Risk Director only (not Board) |
| Evidence | Risk Register entry timestamp; escalation notification log; BCP activation record |

---

### BR-02: HHI Dual-Source Programme Trigger

| Attribute | Value |
|-----------|-------|
| Name | Mandatory Dual-Source Programme for Highly Concentrated Categories |
| Condition | hhi_score > 2500 AND total_category_annual_spend > EUR 5M |
| Result | Board-approved dual-source plan required with 12-month implementation timeline; monthly progress at Procurement Risk Review; Category Manager assigned as programme owner |
| Example | Category "Electronic Control Units" (HHI=4800, spend=EUR 32M) triggers dual-source programme approval; target HHI < 2500 within 12 months |
| Exception | HHI > 2500 but supplier_count >= 3 with approximately equal share AND category is NON_CRITICAL (Kraljic) — monitoring only, no mandatory dual-source plan required |
| Evidence | Board Risk Committee minutes; dual-source programme charter; monthly progress report |

---

### BR-03: Risk Register Annual Review Obligation

| Attribute | Value |
|-----------|-------|
| Name | Annual Risk Review Mandatory for All Active Risks |
| Condition | risk_status != 'CLOSED' AND next_review_due <= CURRENT_DATE |
| Result | Risk owner receives automated reminder 30 days before due date; if not reviewed by next_review_due, risk status set to REVIEW_OVERDUE and CSCO notified |
| Example | Risk "Single-source supplier in earthquake zone" last reviewed 2025-12-01; next_review_due = 2026-12-01; reminder sent 2026-11-01 |
| Exception | CRITICAL risks are reviewed monthly regardless of annual review schedule |
| Evidence | Risk Register last_reviewed_at timestamp; Risk Review meeting minutes |

---

### BR-04: Bullwhip Alert and Communication Protocol

| Attribute | Value |
|-----------|-------|
| Name | Bullwhip Ratio Alert and Root-Cause Response |
| Condition | bullwhip_ratio > 2.0 for any material-supplier link on 12-month rolling window |
| Result | Alert to Demand Planning Manager and Procurement Category Manager; root-cause decomposition attached; if rationing_gaming_component > 0.5, open-book forecasting protocol initiated with supplier |
| Example | SKU "Compressor Unit A" / Supplier B: BWE=3.4, rationing_gaming=1.2 triggers weekly open-book demand sharing |
| Exception | BWE > 2.0 explained entirely by a confirmed seasonal pattern — alert downgraded to MEDIUM with seasonal note |
| Evidence | BULLWHIP_ANALYSIS_LOG entry; Demand Planning meeting notes; supplier communication record |

---

### BR-05: BCP Mandatory Test Schedule

| Attribute | Value |
|-----------|-------|
| Name | CRITICAL BCP Mandatory Annual Test |
| Condition | criticality_level = 'CRITICAL' AND (last_test_date IS NULL OR last_test_date < CURRENT_DATE - 365) |
| Result | bcp_status set to 'OUTDATED'; process no longer counts toward BCP Coverage KPI; Business Continuity Manager receives GRC task; test must be scheduled within 30 days |
| Example | BCP for "SAP S/4HANA procurement module" — last tested 2025-01-15; OUTDATED flag fires 2026-01-15; test rescheduled 2026-02-01 |
| Exception | Actual BCP activation during the year counts as a live test; test_result = PASS if operations recovered within RTO |
| Evidence | BCP_TEST_RESULTS entry; test exercise report; Business Continuity Manager sign-off |

---

### BR-06: Disruption Probability Alert Threshold

| Attribute | Value |
|-----------|-------|
| Name | High Disruption Probability Supplier Alert |
| Condition | disruption_probability_90d > 0.50 for any active TIER1 supplier |
| Result | MEDIUM alert: Category Manager + Risk Analyst notified; contingency sourcing reviewed within 5 business days. If > 0.75: HIGH alert; CSCO notified; BCP activation review within 24 hours |
| Example | Supplier C (sole source, semiconductors): PMI drop + negative sentiment triggers P=0.68; Procurement reviews alternate sourcing; buffer stock reviewed |
| Exception | Signal driven entirely by price volatility (not supply constraint) — alert category downgraded to FINANCIAL |
| Evidence | DISRUPTION_SIGNAL_LOG entry; ML model inference log; analyst acknowledgement |

---

### BR-07: Control Effectiveness Conservative Default

| Attribute | Value |
|-----------|-------|
| Name | Conservative Default for Unassessed Controls |
| Condition | control_effectiveness IS NULL OR control_effectiveness last validated > 12 months ago |
| Result | control_effectiveness defaulted to 0.0; risk appears in "Control Gap" report; residual_risk_score equals inherent_risk_score |
| Example | Risk "Supplier financial insolvency" — control_effectiveness last assessed 2024-06-01; now 25 months ago — default 0.0 applied |
| Exception | None — all risks must have validated control_effectiveness assessed annually |
| Evidence | Risk Register validation date; Risk Review meeting minutes |

---

## 10. KPIs and Formulas

### KPI-01: Inherent Risk Score (per risk event)

```
Inherent_Risk_Score = Likelihood (1-5) x Impact (1-5)

Range: [1, 25]
Severity bands:
  CRITICAL : >= 15
  HIGH     : >= 10 and < 15
  MEDIUM   : >= 5  and < 10
  LOW      : < 5

Portfolio metrics:
  CRITICAL_risk_count = COUNT(risk_id WHERE severity_band = 'CRITICAL' AND is_deleted = FALSE)
  Portfolio_avg_inherent_score = AVG(inherent_risk_score WHERE is_deleted = FALSE)
```

---

### KPI-02: Residual Risk Score (per risk event)

```
Residual_Risk_Score = Inherent_Risk_Score x (1 - Control_Effectiveness)

Control_Effectiveness in [0, 1]:
  0.0 = no control in place
  0.5 = partially effective control
  1.0 = fully effective control (risk fully mitigated)

Control_Effectiveness_Gap =
  COUNT(risk_id WHERE control_effectiveness IS NULL
                   OR last_control_assessment_date < CURRENT_DATE - 365)
```

---

### KPI-03: Expected Annual Loss (EAL) — Portfolio

```
EAL_per_risk = AOP x impact_value_usd x exposure_factor

Portfolio_EAL_usd = SUM(EAL_per_risk WHERE is_deleted = FALSE AND risk_status != 'CLOSED')

Top_10_EAL_concentration =
  SUM(EAL top 10 risks by EAL) / Portfolio_EAL_usd x 100

Target: Top_10_EAL_concentration < 70% (diversified risk posture)
Alert: Any single risk with EAL > USD 10M must have CRITICAL or HIGH severity band assigned
```

---

### KPI-04: HHI by Category

```
HHI_category = SUM(spend_share_i ^ 2) x 10,000
               for all suppliers i in category

Concentration tiers:
  HHI < 1,500         : COMPETITIVE      — no action required
  HHI 1,500-2,500     : MODERATE         — monitor quarterly
  HHI > 2,500         : HIGHLY_CONCENTRATED — mandatory dual-source programme
  HHI = 10,000        : MONOPOLY         — immediate escalation to CSCO

Portfolio metrics:
  Categories_highly_concentrated = COUNT(commodity WHERE hhi > 2500 AND spend > EUR 5M)
  Pct_spend_highly_concentrated  = SUM(spend WHERE hhi > 2500) / Total_spend x 100
```

---

### KPI-05: Single-Source Spend Percentage

```
Single_Source_Spend_Pct (%) =
  SUM(annual_spend WHERE supplier_count_per_category = 1)
  / SUM(total_annual_spend)
  x 100

Target: < 20%
Alert threshold: > 30% triggers CSCO review
Review item: Any single-source category with annual spend > EUR 10M receives Board attention
Frequency: Monthly
```

---

### KPI-06: Dual-Source Coverage (Strategic Items)

```
Dual_Source_Coverage_Strategic (%) =
  COUNT(DISTINCT material WHERE kraljic = 'STRATEGIC'
                            AND active_supplier_count >= 2)
  / COUNT(DISTINCT material WHERE kraljic = 'STRATEGIC')
  x 100

Target: >= 85%
Alert threshold: < 60% triggers CSCO review
Frequency: Monthly
Owner: Procurement Strategy
```

---

### KPI-07: Supply Disruption Risk Score (ML Model Output)

```
P_disruption_90d = LSTM model output (see Section 11 for model architecture)

Scoring tiers:
  HIGH   : P_disruption_90d > 0.75
  MEDIUM : P_disruption_90d > 0.50
  LOW    : P_disruption_90d <= 0.50

Portfolio metrics:
  Suppliers_HIGH_disruption     = COUNT(supplier WHERE P_disruption_90d > 0.75)
  Spend_at_HIGH_disruption_risk = SUM(annual_spend WHERE P_disruption_90d > 0.75)
```

---

### KPI-08: Bullwhip Ratio (per SKU-Supplier Link)

```
Bullwhip_Ratio = VAR(PO_quantity_t) / VAR(Demand_t)
                 [rolling 12-month window, weekly granularity, ddof=1]

Target: approximately 1.0 (no amplification)
Alert threshold: > 2.0 triggers root-cause investigation and BR-04 protocol
Critical threshold: > 5.0 triggers CSCO notification

Portfolio metric:
  Links_with_BWE_above_2 = COUNT(material-supplier links WHERE bullwhip_ratio > 2.0)
  Pct_links_above_2 = Links_with_BWE_above_2 / Total_active_links x 100
```

---

### KPI-09: BCP Coverage

```
BCP_Coverage (%) =
  COUNT(bcp_id WHERE criticality_level = 'CRITICAL'
                 AND bcp_status = 'CURRENT'
                 AND last_test_date >= CURRENT_DATE - 365
                 AND last_test_result = 'PASS')
  / COUNT(bcp_id WHERE criticality_level = 'CRITICAL'
                   AND is_deleted = FALSE)
  x 100

Target: 100%
Alert threshold: < 90% triggers Board Risk Committee notification
Frequency: Monthly
Owner: Business Continuity Manager
```

---

### KPI-10: Resilience Gap (Critical Supply Nodes)

```
Resilience_Gap_days = TTR - TTS

  TTR (Time to Recover) = detection_days + decision_days + alternate_supplier_ramp_days
  TTS (Time to Survive) = buffer_inventory_days + contractual_buffer_days

  Gap > 0: Vulnerable — production impact expected for (Gap) days during disruption
  Gap <= 0: Resilient — buffer absorbs disruption before recovery completes

Portfolio metrics:
  Nodes_with_positive_gap = COUNT(bcp_id WHERE resilience_gap_days > 0
                                           AND criticality_level = 'CRITICAL')
  Max_resilience_gap_days = MAX(resilience_gap_days WHERE criticality_level = 'CRITICAL')
```

---

### KPI-11: Mitigation Action Overdue Rate

```
Overdue_Actions_Count =
  COUNT(action_id WHERE due_date < CURRENT_DATE
                    AND status NOT IN ('COMPLETED')
                    AND risk_status != 'CLOSED')

Overdue_Action_Pct (%) = Overdue_Actions_Count / Total_open_actions x 100

Target: 0% CRITICAL risk mitigation actions overdue
Alert: Any CRITICAL risk with overdue action triggers CSCO notification
Frequency: Weekly monitoring; monthly reporting
```

---

## 11. Analytical Logic

### 5x5 Risk Heat Map — Detailed Logic

The 5x5 heat map operationalises ISO 31000:2018 clause 6.4.3. Each risk is scored on two
calibrated dimensions:

**Likelihood Scale:**
```
5 — Almost Certain : P > 50% per year        (at least once every 2 years)
4 — Likely         : P 25-50% per year        (once every 2-4 years)
3 — Possible       : P 10-25% per year        (once every 4-10 years)
2 — Unlikely       : P 1-10% per year         (once every 10-100 years)
1 — Rare           : P < 1% per year          (once per century or less)
```

**Impact Scale (calibrated to revenue):**
```
5 — Catastrophic   : Revenue impact > USD 50M  OR  company-threatening event
4 — Major          : Revenue impact USD 10-50M OR  production halt > 30 days
3 — Significant    : Revenue impact USD 2-10M  OR  production halt 7-30 days
2 — Minor          : Revenue impact USD 0.1-2M OR  production halt 1-7 days
1 — Negligible     : Revenue impact < USD 100K OR  production delay < 1 day
```

**Heat Map (textual representation):**
```
              Impact 1   Impact 2   Impact 3   Impact 4   Impact 5
Likelihood 5    5 (M)     10 (H)     15 (C)     20 (C)     25 (C)
Likelihood 4    4 (L)      8 (M)     12 (H)     16 (C)     20 (C)
Likelihood 3    3 (L)      6 (M)      9 (M)     12 (H)     15 (C)
Likelihood 2    2 (L)      4 (L)      6 (M)      8 (M)     10 (H)
Likelihood 1    1 (L)      2 (L)      3 (L)      4 (L)      5 (M)

Legend: C=CRITICAL(>=15), H=HIGH(>=10), M=MEDIUM(>=5), L=LOW(<5)
```

**Dual-position plotting:** Each risk is plotted twice — inherent score (filled circle, before
controls) and residual score (hollow circle, after controls). The movement between positions
visualises control effectiveness for Board presentations.

---

### HHI Concentration Tiers — Decision Logic

```
HHI < 1,500     COMPETITIVE
  Action: Monitor quarterly; no structural intervention required
  Dashboard indicator: Green

HHI 1,500-2,500   MODERATE
  Action: Semi-annual review; develop contingency sourcing list
  If HHI trending toward 2,500: proactive dual-source evaluation
  Dashboard indicator: Amber

HHI > 2,500     HIGHLY CONCENTRATED
  Action: Board-approved dual-source programme; 12-month implementation timeline
  Monthly progress reporting; interim buffer stock assessment
  For categories > EUR 20M annual spend: CSCO escalation required
  Dashboard indicator: Red

HHI = 10,000    MONOPOLY (single-source)
  Action: Immediate BCP review; emergency alternate source identification
  Dual-source programme SLA accelerated to 6 months (not 12)
  Dashboard indicator: Critical alert
```

**Dual-Source Priority Scoring:** When multiple concentrated categories compete for dual-source
investment resources, prioritise by weighted score:

```
dual_source_priority_score =
  (0.40 x normalised_spend_rank)
  + (0.30 x normalised_hhi_rank)
  + (0.20 x normalised_risk_score_rank)
  + (0.10 x (1 - normalised_alternate_supplier_availability))

Rationale:
  Spend rank:                    higher spend = more financial exposure
  HHI rank:                      higher HHI = more structural concentration risk
  Risk score rank:               higher risk register score = more immediate concern
  Alternate availability factor: if no alternates exist, priority is higher
```

---

### Bullwhip Ratio — Root Cause Decomposition Logic

```python
# python/10_risk_management/models/bullwhip.py

import numpy as np
import pandas as pd

def decompose_bullwhip(
    orders: pd.Series,
    demand: pd.Series,
    prices: pd.Series,
    lead_time_weeks: int = 2,
    review_period_weeks: int = 1,
) -> dict:
    """
    Decompose total Bullwhip Ratio into four attributable components.
    Uses Chen (2000) theoretical lower bound as baseline.

    Args:
        orders: Weekly order quantity series (12-month window, 52 observations).
        demand: Weekly end-customer demand series (same period).
        prices: Weekly unit price series (same period).
        lead_time_weeks: Replenishment lead time in weeks (L).
        review_period_weeks: Order review period in weeks (p).

    Returns:
        Dict with keys: total_bwe, chen_lower_bound,
        demand_signal_processing, order_batching,
        price_fluctuation, rationing_gaming.
    """
    var_orders = np.var(orders, ddof=1)
    var_demand = np.var(demand, ddof=1)

    if var_demand == 0:
        raise ValueError("Demand variance is zero — BWE undefined")

    total_bwe = var_orders / var_demand

    # Chen (2000) lower bound: 1 + 2(L/p) + 2(L/p)^2
    ratio = 2 * lead_time_weeks / review_period_weeks
    chen_lb = 1 + ratio + ratio ** 2

    # Demand signal processing component
    demand_signal = chen_lb - 1.0

    # Price fluctuation: correlation between price pct change and order pct change
    price_chg = prices.pct_change().fillna(0)
    order_chg = orders.pct_change().fillna(0)
    price_corr = abs(price_chg.corr(order_chg))
    price_component = (total_bwe - chen_lb) * price_corr * 0.40

    # Order batching: excess coefficient of variation of orders vs demand
    cv_orders = orders.std() / orders.mean() if orders.mean() > 0 else 0
    cv_demand = demand.std() / demand.mean() if demand.mean() > 0 else 0
    batching_component = max(0.0, (cv_orders - cv_demand) * 0.50)

    # Rationing gaming: residual unexplained component
    explained = demand_signal + price_component + batching_component
    rationing = max(0.0, total_bwe - 1.0 - explained)

    return {
        "total_bwe":                round(total_bwe, 4),
        "chen_lower_bound":         round(chen_lb, 4),
        "demand_signal_processing": round(demand_signal, 4),
        "price_fluctuation":        round(price_component, 4),
        "order_batching":           round(batching_component, 4),
        "rationing_gaming":         round(rationing, 4),
    }
```

**Intervention mapping by dominant component:**

| Dominant Component | Recommended Intervention |
|---|---|
| demand_signal_processing | Switch from MA to SES/Holt forecasting; reduce forecast error via better data sharing |
| order_batching | Move to continuous replenishment; reduce order review period to weekly |
| price_fluctuation | Renegotiate to fixed annual contracts; eliminate promotional forward buying incentives |
| rationing_gaming | Implement open-book demand sharing; provide supplier with 13-week forward forecast weekly |

---

## 12. Validations and Controls

### VC-01: Risk Register Completeness

- All active risks (is_deleted = FALSE, risk_status != 'CLOSED') must have all mandatory fields
  populated: likelihood, impact, risk_owner_id, next_review_due.
- Daily completeness check: any risk with NULL mandatory field generates a data quality alert
  to the Risk Director.

### VC-02: HHI Data Completeness

- HHI computation requires >= 12 months of PO history per commodity category.
- Categories with < 12 months of PO history are flagged as INSUFFICIENT_HISTORY and excluded
  from the concentration ranking. Excluded categories listed in dashboard footnotes.

### VC-03: Bullwhip Series Length Validation

- Minimum 52 weekly observations required for a valid BWE calculation.
- Material-supplier links with insufficient history are excluded from BWE ranking.
- SKUs with demand_variance = 0 (perfectly stable demand) are excluded — BWE undefined.

### VC-04: BCP Currency Check

- All CRITICAL BCPs must have last_test_date within 365 days. Daily check generates alert if
  any CRITICAL BCP test is overdue.
- A BCP with last_test_result = 'FAIL' must have a corrective action plan with a completion
  date no more than 90 days from test date.

### VC-05: ML Model Freshness

- disruption_probability_90d must be refreshed within 24 hours for all active Tier-1 suppliers.
- If the ML pipeline has not run within 24 hours (model_last_run_at check), all P_disruption_90d
  scores are flagged as STALE; disruption alerts are suppressed until model reruns.

### VC-06: EAL Reasonableness Check

- Any risk with EAL_usd > 20% of company annual net profit triggers a reasonableness flag
  requiring CFO sign-off before publishing in Board pack.
- EAL_usd = 0 for any risk with inherent_risk_score >= 10 is flagged as INCOMPLETE — a
  quantified financial impact is required for all HIGH and CRITICAL risks.

### VC-07: Supplier Spend Share Sum

- The sum of all supplier spend shares within a commodity must equal 1.0 (within floating-point
  tolerance of 0.001). Discrepancies indicate PO data extraction gaps.

---

## 13. Required Evidence

| Evidence Item | Retention Period | Owner | Storage Location |
|---|---|---|---|
| Risk Register full version history | 7 years | Risk Director | Azure SQL with version timestamps |
| Risk Review meeting minutes | 7 years | Risk Analyst | SharePoint document library |
| Board Risk Committee papers | 10 years | Company Secretary | Board portal (secure) |
| Mitigation action completion records | 7 years | Risk Owner | Azure SQL MITIGATION_ACTIONS table |
| HHI scoring log (monthly snapshots) | 5 years | Procurement Analytics | Data warehouse (Parquet, Apache Iceberg) |
| Dual-source programme progress reports | 5 years | Category Manager | SharePoint |
| Bullwhip analysis log (12-month windows) | 3 years | Demand Planning Analytics | Data warehouse |
| ML model inference logs (disruption scoring) | 2 years | ML Engineering | MLflow tracking server (OSI-licensed) |
| BCP documents and test reports | 7 years | Business Continuity Manager | SharePoint document library |
| Disruption signal log (news + macro signals) | 2 years | Risk Data Engineering | Data lake (Parquet) |
| Monte Carlo simulation results (annual run) | 5 years | Risk Analyst | Data warehouse + PDF archive |

---

## 14. Dashboard Design

### Dashboard 1: Supply Risk Register (Power BI)

**Audience:** Risk Director, Risk Analysts, CSCO
**Refresh:** Daily (risk register changes); weekly (KPI trend)

**Page 1 — Risk Heat Map:**
- 5x5 matrix visualisation: each cell shaded by severity band (red/orange/yellow/green)
- Bubble overlay: each risk plotted as a circle (size proportional to EAL_usd)
- Dual display: inherent score position (filled circle) and residual score position (hollow circle)
- Filter panel: risk_category, business_unit, supplier_id, severity_band

**Page 2 — Risk Register Table:**
- Table columns: Title, Category, Likelihood, Impact, Inherent Score, Band, Control Effectiveness,
  Residual Score, EAL (USD), Risk Owner, Next Review Date, Days Until Overdue
- Conditional formatting: CRITICAL = red background; HIGH = orange; overdue review = bold red date
- Export to Excel for monthly Board pack preparation

**Page 3 — EAL Portfolio:**
- Pareto chart: top-20 risks sorted by EAL (bars) with cumulative EAL% line
- KPI cards: Total Portfolio EAL | CRITICAL count | HIGH count | Overdue actions count
- Trend: Portfolio average inherent risk score — 12 months rolling (line chart)

---

### Dashboard 2: Supplier Concentration Risk (HHI)

**Audience:** Procurement Strategy, CSCO, CPO
**Refresh:** Monthly

**Page 1 — Concentration Overview:**
- Horizontal bar chart: top-20 commodity categories by HHI (colour-coded by concentration band)
- KPI tiles: Categories HIGHLY_CONCENTRATED | Spend in HIGHLY_CONCENTRATED (EUR) |
  Single-Source Spend % | Dual-Source Coverage (Strategic) %
- Table: highly concentrated categories — columns: Category, HHI, Band, Supplier Count,
  Top Supplier, Top Supplier Share %, Annual Spend (EUR), Dual-Source Programme Status

**Page 2 — Dual-Source Progress:**
- Gantt-style chart: dual-source programmes per category (planned vs actual completion date)
- KPI: Strategic items with >= 2 active suppliers / total strategic items
- Table: Strategic items still single-sourced (sorted by annual spend descending)

**Page 3 — HHI Trend:**
- Line chart: HHI trend for top-10 concentrated categories (18-month history)
- Category drill-down: click category to see spend split by supplier over time

---

### Dashboard 3: Supply Disruption Early Warning

**Audience:** Risk Analyst, Procurement Category Managers, CSCO
**Refresh:** Daily (ML score); news signals updated every 15 minutes

**Page 1 — Disruption Probability Heat:**
- World map: supplier locations — bubble colour by P_disruption_90d (green/amber/red)
- Table: Top-20 suppliers by disruption probability — Supplier, Country, Tier,
  P(disruption), Alert Level, Top Signal Driver, Annual Spend (EUR)

**Page 2 — Signal Feed:**
- Table: most recent HIGH and MEDIUM disruption signals (most recent 7 days) —
  Headline, Supplier, Sentiment Score, Keywords Matched, Alert Level, Date, Acknowledged
- Filter: by alert level, supplier, country, signal_source

**Page 3 — Trend:**
- Line chart: % of Tier-1 suppliers with P_disruption > 0.50, rolling 12 months
- Scatter plot: P_disruption_90d (x-axis) vs OTD_pct (y-axis) — top-left quadrant = high risk
  and already underperforming

---

### Dashboard 4: Bullwhip Effect Monitor

**Audience:** Demand Planning, Procurement, Supply Chain Operations
**Refresh:** Weekly

**Page 1 — Portfolio Overview:**
- KPI tiles: Links with BWE > 2.0 | Links with BWE > 5.0 | Pct Links with BWE > 2.0 | Avg BWE
- Histogram: BWE distribution across all links (bins: 0-1, 1-2, 2-3, 3-5, >5)

**Page 2 — Worst Links:**
- Table: Top-30 links by BWE — Material, Supplier, Plant, BWE Ratio, Dominant Component,
  Alert Level, Recommended Intervention
- Stacked bar: root-cause decomposition for top-10 BWE links (4 components stacked)

**Page 3 — Link Drill-Down:**
- Selected link: time series of demand (blue line) vs orders placed (orange line), 52 weeks
- Variance ratio trend chart (quarterly) for selected material-supplier link

---

### Dashboard 5: Business Continuity Coverage

**Audience:** Business Continuity Manager, CSCO, Board Risk Committee
**Refresh:** Weekly

**Page 1 — Coverage Summary:**
- Gauge: BCP Coverage % vs 100% target
- KPI tiles: Total CRITICAL processes | CURRENT BCPs | OUTDATED BCPs | MISSING BCPs |
  Processes with Positive Resilience Gap
- Table: CRITICAL processes with bcp_status = MISSING or OUTDATED (sorted by rto_hours ascending)

**Page 2 — Resilience Gap Analysis:**
- Scatter plot: TTR (y-axis) vs TTS (x-axis) per CRITICAL process —
  points above the 45-degree diagonal line are vulnerable (TTR > TTS)
- Table: Processes with positive resilience_gap_days — Process, TTS, TTR, Gap (days),
  Buffer Uplift Required (days), BCP Owner

**Page 3 — Test Schedule:**
- Calendar view: upcoming BCP test exercise dates (next 12 months)
- Table: Tests overdue (last_test_date > 365 days ago) with days overdue and BCP owner contact

---

## 15. Use Cases

### UC-01: Monthly CSCO Risk Briefing Preparation

**Actor:** Risk Analyst
**Trigger:** First Monday of each month

**Flow:**
1. Export Risk Register Dashboard Page 2 — filter to CRITICAL and HIGH risks only
2. Check for any risk with next_review_due < CURRENT_DATE (overdue reviews)
3. Review EAL Pareto: has any new risk entered the top-10 by EAL since last month?
4. Export HHI Dashboard: identify any new categories crossing HHI 2500 threshold this month
5. Check BCP Coverage: any CRITICAL process now OUTDATED?
6. Compile CSCO briefing pack using PowerPoint template: cover page KPI summary + top-5 risk
   narratives + recommended actions
7. CSCO reviews and approves; Risk Director presents at Board Risk Committee (quarterly)

**Outcome:** CSCO has current-month risk posture; Board pack prepared on time.

---

### UC-02: New Supplier Sole-Source Risk Assessment

**Actor:** Procurement Category Manager
**Trigger:** Procurement team proposes sourcing from a new sole-source supplier for a strategic item

**Flow:**
1. Category Manager inputs proposed supplier and spend into HHI model — recomputes category HHI
2. If post-award HHI > 2500: automatic dual-source programme requirement is generated
3. Risk Analyst creates new Risk Register entry: "Sole-source dependency — Supplier X, Category Y"
4. Scores Likelihood and Impact per calibrated scale; inherent_risk_score computed
5. If CRITICAL (>= 15): escalation to CSCO required before contract signature is authorised
6. Dual-source programme charter drafted as a condition of contract award proceeding

**Outcome:** Sole-source risk is visible, scored, and managed before the contract is signed.

---

### UC-03: Bullwhip Root-Cause Investigation

**Actor:** Demand Planning Manager + Procurement Category Manager
**Trigger:** Weekly BWE alert — SKU "Compressor Unit A" / Supplier B has BWE = 4.2

**Flow:**
1. Open Bullwhip Dashboard Page 2 — drill into "Compressor Unit A" / Supplier B link
2. Root-cause decomposition: rationing_gaming = 1.9 (dominant component at 45% of excess BWE)
3. Review time series on Page 3: orders show spike pattern vs smooth customer demand
4. Conclusion: Supplier B capacity constraint last quarter triggered over-ordering behaviour
5. Action: Demand Planning Manager initiates weekly open-book forecast sharing with Supplier B;
   provides rolling 13-week confirmed demand signal starting next week
6. Follow-up in 4 weeks: BWE re-measured; target < 2.0 within 8 weeks

**Outcome:** BWE root cause identified; corrective action taken; improvement tracked weekly.

---

### UC-04: Disruption Early Warning — Supplier Factory Fire

**Actor:** Risk Analyst + Procurement Category Manager
**Trigger:** GDELT high-sentiment alert — "Factory fire at Supplier C plant, Taiwan"

**Flow:**
1. DISRUPTION_SIGNAL_LOG entry created: sentiment = -0.91, alert_level = HIGH
2. ML model reruns for Supplier C: P_disruption_90d jumps from 0.32 to 0.78
3. GRC task created: Risk Analyst + Category Manager; SLA 24 hours
4. Risk Analyst reviews: Supplier C is sole source for electronic control boards (HHI = 10000)
5. BCP review: TTS = 18 days (buffer stock); TTR = 35 days (alternate supplier ramp)
6. Resilience gap = +17 days — emergency buffer stock procurement authorised by CSCO
7. Category Manager contacts Supplier C directly; alternate source (Supplier D) pre-qualified
8. CSCO notified; monitoring cadence: daily until P_disruption_90d returns below 0.50

**Outcome:** 17-day potential production gap avoided through early detection and emergency action.

---

### UC-05: Annual BCP Testing Exercise

**Actor:** Business Continuity Manager
**Trigger:** next_test_due date reached for "Semiconductor Procurement Disruption" BCP

**Flow:**
1. Business Continuity Manager schedules tabletop exercise with Procurement, Finance, Operations
2. Exercise scenario: Tier-1 semiconductor supplier declares force majeure; 45-day lead time gap
3. BCP reviewed during exercise: current TTS = 22 days, TTR = 30 days (gap = +8 days assumed)
4. Exercise findings: alternate supplier ramp-up actually takes 45 days (not 30 as documented)
5. BCP updated: TTR corrected to 45 days; resilience_gap = +23 days; buffer uplift = 28 days
6. BCP_TEST_RESULTS entry: test_result = FAIL; corrective action: increase safety stock target
7. BCP Coverage dashboard: process moves to OUTDATED until corrective action complete (90-day SLA)
8. Corrective action completed; BCP re-tested 60 days later; test_result = PASS; status = CURRENT

**Outcome:** BCP gap identified and corrected proactively before an actual disruption occurs.

---

## 16. Recommended Actions

### Immediate Actions (Month 1–3)

1. **Baseline HHI scan:** Extract 12 months of PO data from SAP S/4HANA and compute HHI for all
   commodity categories with annual spend > EUR 1M. Publish ranked list to CSCO and CPO. Initiate
   dual-source programmes for all categories with HHI > 2500 and spend > EUR 5M.

2. **Risk Register migration to Azure SQL:** Migrate the risk register from Excel or SharePoint
   lists to Azure SQL with structured schema. This enables automated KPI computation, trend
   analysis, and control effectiveness tracking. Target: all active risks migrated within 8 weeks.

3. **BCP audit:** Identify all CRITICAL business processes and verify that current BCPs exist and
   have been tested within 12 months. Any CRITICAL process with a missing or untested BCP receives
   a BCP development or retest task with 90-day SLA.

4. **Bullwhip baseline:** Run BWE analysis for all Tier-1 supplier-SKU links with >= 52 weekly
   observations. Publish initial ranking of links with BWE > 2.0 to Demand Planning team.

### Medium-Term Actions (Month 4–12)

5. **Deploy ML disruption early warning:** Train LSTM model on 3+ years of macro indicator data
   (PMI, BDI, GPR) and labeled supplier disruption events. Deploy as daily batch scoring.
   Target: all active Tier-1 suppliers receive a daily P_disruption_90d score.

6. **TTS/TTR analysis for critical supply nodes:** Run resilience gap analysis for all CRITICAL-
   classified supply processes. For nodes with positive gap: compute required buffer stock uplift
   and present investment request to CSCO with cost-benefit analysis.

7. **Dual-source programme dashboarding:** For all categories with HHI > 2500, create a
   dual-source programme tracking dashboard in Power BI. Monthly progress at Procurement Risk Review.

8. **Monte Carlo portfolio EAL:** Run first annual Monte Carlo simulation for portfolio-level EAL
   distribution. Output: VaR(95%), VaR(99%), CVaR(95%) — feed into insurance captive sizing model.

### Strategic Actions (Year 2–3)

9. **GNN cascade risk model:** Deploy Graph Neural Network to model supply network cascade risk.
   Identify critical nodes by betweenness centrality whose failure would cascade across processes.

10. **RL for dynamic buffer stock:** Deploy reinforcement learning agent to dynamically adjust
    safety stock targets based on real-time P_disruption_90d scores and HHI levels.

11. **Tier-2 HHI extension:** Extend HHI analysis to Tier-2 suppliers in STRATEGIC and BOTTLENECK
    categories. Requires Tier-2 supplier mapping (coordinated with Department 09 CSDDD programme).

---

## 17. Test Cases

### TC-01: Risk Score Boundary Tests

| Scenario | Likelihood | Impact | Expected Score | Expected Band |
|---|---|---|---|---|
| Maximum inherent | 5 | 5 | 25 | CRITICAL |
| Minimum inherent | 1 | 1 | 1 | LOW |
| CRITICAL threshold — exact | 3 | 5 | 15 | CRITICAL |
| HIGH threshold — exact | 2 | 5 | 10 | HIGH |
| MEDIUM threshold — exact | 1 | 5 | 5 | MEDIUM |
| Just below CRITICAL | 3 | 4 | 12 | HIGH |
| Invalid likelihood | 6 | 3 | — | ValueError raised |

---

### TC-02: Residual Risk Score Tests

| Scenario | Inherent Score | Control Effectiveness | Expected Residual |
|---|---|---|---|
| No controls | 20 | 0.0 | 20.0 |
| Partially effective | 20 | 0.5 | 10.0 |
| Highly effective | 20 | 0.8 | 4.0 |
| Fully effective | 20 | 1.0 | 0.0 |
| NULL controls (default) | 20 | NULL → 0.0 | 20.0 |

---

### TC-03: HHI Calculation Tests

| Scenario | Supplier Spend Distribution | Expected HHI | Expected Band |
|---|---|---|---|
| Perfect monopoly | 1 supplier: 100% | 10,000 | MONOPOLY |
| Perfect duopoly (equal) | 2 suppliers: 50% each | 5,000 | HIGHLY_CONCENTRATED |
| 4 suppliers equal | 25% each | 2,500 | HIGHLY_CONCENTRATED (boundary) |
| 5 suppliers equal | 20% each | 2,000 | MODERATE |
| 10 suppliers equal | 10% each | 1,000 | COMPETITIVE |
| Dominant + 9 small | 70% + 9 x 3.33% | 4,933 | HIGHLY_CONCENTRATED |

---

### TC-04: Bullwhip Ratio Tests

| Scenario | Order Variance | Demand Variance | Expected BWE |
|---|---|---|---|
| No amplification | 100 | 100 | 1.0000 |
| Moderate amplification | 200 | 100 | 2.0000 |
| High amplification | 500 | 100 | 5.0000 |
| Demand variance = 0 | 100 | 0 | ValueError raised |
| Insufficient observations | 8 obs | 8 obs | ValueError raised |

---

### TC-05: BCP Coverage Tests

| Scenario | CRITICAL BCPs Total | CURRENT and Tested | Expected Coverage |
|---|---|---|---|
| Full coverage | 10 | 10 | 100.0% |
| 1 OUTDATED | 10 | 9 | 90.0% |
| 2 MISSING | 10 | 8 | 80.0% |
| 1 FAILED test | 10 | 8 (FAIL excluded) | 80.0% |
| No CRITICAL BCPs | 0 | 0 | N/A — display warning |

---

### TC-06: EAL Calculation Tests

| Scenario | AOP | Impact Value (USD) | Exposure Factor | Expected EAL (USD) |
|---|---|---|---|---|
| Standard | 0.10 | 5,000,000 | 0.50 | 250,000 |
| High probability, low impact | 0.80 | 100,000 | 1.00 | 80,000 |
| Low probability, catastrophic | 0.01 | 100,000,000 | 0.90 | 900,000 |
| Zero AOP | 0.00 | 10,000,000 | 1.00 | 0 |
| Invalid AOP > 1 | 1.10 | — | — | ValueError raised |
| Invalid exposure factor > 1 | 0.20 | 1,000,000 | 1.50 | ValueError raised |

---

### TC-07: Resilience Gap Tests

| Scenario | Buffer (units) | Daily Demand | Contract Buffer (days) | Detection | Decision | Ramp | Expected TTS | Expected TTR | Expected Gap |
|---|---|---|---|---|---|---|---|---|---|
| Resilient | 1000 | 100 | 5 | 2 | 1 | 7 | 15.0 | 10.0 | -5.0 |
| Vulnerable | 500 | 100 | 0 | 2 | 2 | 30 | 5.0 | 34.0 | +29.0 |
| Borderline | 700 | 100 | 0 | 2 | 1 | 4 | 7.0 | 7.0 | 0.0 |

---

## 18. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Risk Register data quality — subjective likelihood and impact scores varying across risk owners | High | High | Calibrated scoring scales with numerical revenue anchors; quarterly calibration workshop with all risk owners; Risk Director reviews outlier scores before publishing |
| HHI data gap — legacy PO data with unmapped commodity codes skews category HHI | Medium | High | Commodity code crosswalk table maintained by MDG; dual-source trigger only fires for categories with >= 6 months of clean PO history; unmapped POs listed in data quality report |
| ML model false alarms — high disruption probability with no actual disruption | High | Medium | Model confidence score filter; analyst acknowledgement required before escalation; track false positive rate monthly; retrain model quarterly |
| Bullwhip measurement noise — small-volume SKUs with naturally high order variance | Medium | Medium | Minimum 52-week observation window; exclude SKUs with < 10 order events per year; flag low-volume SKUs separately in dashboard |
| BCP documents not updated after organisational changes (new suppliers, new plants, restructuring) | High | High | Annual BCP review obligation built into risk owner performance KPIs; auto-flag BCPs not updated within 12 months; BCM team owns review calendar |
| Azure SQL risk register performance under concurrent Power BI queries | Low | Medium | Read replica for Power BI; daily snapshot table for analytics; direct query only for real-time KRI monitoring |
| Risk owner turnover — risks assigned to departed employees become unmonitored | Medium | High | Monthly sweep: identify risks with risk_owner_id not in active HR roster; reassign to Risk Director as interim owner until replacement designated |
| Monte Carlo parameter uncertainty — AOP and exposure factor are subjective estimates | High | Medium | Sensitivity analysis at plus or minus 50% on AOP and EF; present range not point estimate to Board; document all assumptions explicitly in model notes |
| Simultaneous multi-region disruption (geopolitical escalation, pandemic) | Low | Critical | Annual multi-node scenario planning using SimPy digital twin; Board-level geopolitical war-game exercise annually |
| Power BI licensing cost escalation as user base grows across 40 countries | Medium | Low | Evaluate open-source alternative (Apache Superset, Apache-2.0) if per-seat costs exceed budget threshold at 200+ users |

---

## 19. Implementation Checklist

### Phase 1: Data Foundation and Risk Register (Weeks 1–8)

- [ ] Migrate risk register from Excel to Azure SQL using defined schema from Section 7
- [ ] Load all historical risks (minimum 3 years) with data quality review by Risk Analyst
- [ ] Configure SharePoint Power Apps front-end for risk owner data entry (no Excel interface)
- [ ] Extract 12 months of PO data from SAP S/4HANA for HHI baseline calculation
- [ ] Map all commodity codes in PO data to current commodity taxonomy via crosswalk table
- [ ] Identify all CRITICAL business processes (first BCP audit across all BUs)
- [ ] Populate BCP_REGISTRY with all CRITICAL processes (including bcp_status = MISSING entries)
- [ ] Extract 52-week demand and order history for all active Tier-1 supplier-SKU links
- [ ] Configure daily GDELT API pull and ETL pipeline into DISRUPTION_SIGNAL_LOG

### Phase 2: KPI Computation and Scoring (Weeks 9–16)

- [ ] Compute first HHI scores across all commodity categories with >= 6 months PO history
- [ ] Run first Bullwhip Ratio calculation for all links with >= 52 weekly observations
- [ ] Compute all BCP Coverage metrics from BCP_REGISTRY (including OUTDATED and MISSING counts)
- [ ] Compute resilience gaps (TTS and TTR) for all CRITICAL processes
- [ ] Compute inherent and residual risk scores for all Risk Register entries
- [ ] Run first EAL calculation for all ASSESSED risks with impact_value_usd populated
- [ ] Establish Python scoring pipelines: HHI (monthly), BWE (weekly), BCP coverage (daily)
- [ ] Begin ML model training: collect labeled disruption event history for LSTM

### Phase 3: Dashboards (Weeks 17–24)

- [ ] Deploy all 5 Power BI dashboards connected to Azure SQL and SAP data warehouse
- [ ] Configure daily and weekly refresh schedules for each dashboard
- [ ] Configure automated alert emails: new CRITICAL risk, HHI > 2500, BWE > 2.0, BCP OUTDATED
- [ ] User acceptance testing with Risk Analyst team, Procurement, CSCO office
- [ ] Train Risk Analysts and Category Managers on dashboard use (4-hour session)
- [ ] Train risk owners on risk register data entry in SharePoint (2-hour session)

### Phase 4: ML and Advanced Analytics (Weeks 25–36)

- [ ] Deploy LSTM disruption prediction model (daily batch scoring for all Tier-1 suppliers)
- [ ] Deploy NLP news signal pipeline (GDELT + DistilBERT sentiment, hourly refresh)
- [ ] Run Monte Carlo portfolio EAL simulation (annual baseline, 10,000 simulations)
- [ ] Integrate ML disruption scores into SUPPLIER_MASTER.disruption_probability_90d
- [ ] Configure high disruption probability alerts per BR-06 thresholds
- [ ] Configure MLflow model tracking and versioning for governance (OSI-licensed)

---

## 20. Validation Checklist

### Data Quality

- [ ] HHI commodity code coverage >= 95% of total PO spend by value
- [ ] BWE analysis covers >= 80% of annual Tier-1 supplier spend by spend weight
- [ ] BCP_REGISTRY includes 100% of processes meeting the CRITICAL definition
- [ ] Risk Register: zero active HIGH or CRITICAL risks with NULL control_effectiveness
- [ ] Risk Register: zero risks with next_review_due NULL

### KPI Accuracy

- [ ] HHI scores validated against manual calculation for 5 randomly selected commodity categories
- [ ] BWE validated against manual variance calculation for 3 randomly selected SKU-supplier links
- [ ] BCP Coverage percentage validated against manual count of CURRENT and tested BCPs
- [ ] Portfolio EAL total validated against manual sum from Risk Register Excel export

### Dashboard

- [ ] Heat map cell colours match severity band logic for all 25 cells (spot check all cells)
- [ ] HHI band colours: red > 2500, amber 1500-2500, green < 1500 (spot check 5 categories)
- [ ] Bullwhip alert indicator fires correctly for BWE > 2.0 (UAT test with synthetic data)
- [ ] Disruption probability world map updates within 2 hours of ML model run completion
- [ ] PDF export for Board Risk Committee pack — no truncated tables or missing data

### Controls

- [ ] CRITICAL risk escalation notification fires within 1 hour for a test risk entry (UAT)
- [ ] BCP OUTDATED flag fires correctly when last_test_date > 365 days (UAT)
- [ ] BWE > 2.0 alert email delivered to correct Demand Planning Manager and Category Manager
- [ ] ML model STALE flag fires correctly when model has not run in > 24 hours (UAT)

---

## 21. Pending Information

| Item | Required From | Impact if Missing | Target Date |
|---|---|---|---|
| Complete Tier-2 supplier mapping with commodity linkage | Procurement / Department 09 | HHI cannot be computed for Tier-2 concentration risk | 2026-09-30 |
| Altman Z-score and Paydex data for private suppliers | D&B subscription (Finance approval pending) | Financial distress signal incomplete for approximately 40% of suppliers | 2026-08-31 |
| Impact value (USD) for all HIGH and CRITICAL risk register entries | Risk Owners (facilitated by Risk Analyst team) | EAL computation incomplete; portfolio EAL understated in Board reports | 2026-08-15 |
| BCP documents for 12 CRITICAL processes currently listed as MISSING | Business Unit BCM leads | BCP Coverage KPI below 75% until resolved; Board escalation required | 2026-09-30 |
| Labeled disruption event history (5 years) for LSTM model training | Risk Analyst + external provider (Riskmethods or Resilinc) | ML model training data insufficient; deployment target delayed by 1 quarter | 2026-10-31 |
| SAP material master Kraljic classification for dual-source coverage KPI | Category Management team | Dual-Source Coverage (Strategic Items) KPI unavailable until populated | 2026-08-31 |
| Board-approved risk appetite statement with quantitative thresholds | Board Risk Committee | Escalation thresholds for residual risk score cannot be confirmed or published | 2026-07-31 |

---

## 22. Implementation Roadmap

```
QUARTER       Q3 2026              Q4 2026              Q1 2027              Q2 2027
              Jul   Aug   Sep      Oct   Nov   Dec      Jan   Feb   Mar      Apr   May   Jun

PHASE 1       ████████████████████
Data          Risk register migration to Azure SQL
Foundation    HHI baseline (12 months PO data)
              BCP audit (all CRITICAL processes)
              BWE history extraction (52 weeks)
              GDELT disruption signal feed live

PHASE 2                      ████████████████████
KPI           First HHI scores published to CSCO
Computation   First BWE ranking published to Demand Planning
              BCP Coverage baseline computed
              TTS/TTR resilience gaps calculated
              EAL computed for all assessed risks

PHASE 3                                   ████████████████████
Dashboards                               Dashboards 1-5 deployed in Power BI
                                         Automated alert emails configured
                                         UAT completed with Risk and Procurement
                                         Training sessions completed

PHASE 4                                                ████████████████████
ML and                                                LSTM disruption model deployed
Advanced                                              NLP news signal pipeline (hourly)
Analytics                                             Monte Carlo EAL simulation live
                                                      ML disruption alerts operational

PHASE 5                                                             ████████████
Year 2+                                                            GNN cascade risk model
Continuous                                                         RL buffer optimisation
Improvement                                                        Tier-2 HHI extension
                                                                   Annual geopolitical war-game

MILESTONES
2026-07-31   Risk Register fully migrated to Azure SQL; all active risks scored
2026-08-31   HHI baseline published; dual-source programmes initiated for HHI > 2500 categories
2026-09-30   All 5 Power BI dashboards live; BCP audit complete with gap plan
2026-12-31   LSTM model deployed; disruption signal alerts live; Monte Carlo EAL baseline
2027-03-31   BWE root-cause automation complete; BCP Coverage >= 90%
2027-06-30   GNN cascade model in production; Tier-2 HHI analysis available
```

**Budget:**
- Phase 1–4 (Year 1–2): USD 4.0M (Azure SQL, Power BI, Python platform, ML engineering, data)
- Phase 5 (Year 3+): USD 1.5M/year (GNN, RL, Tier-2 extension, ongoing platform operations)
- External data subscriptions: USD 0.4M/year (D&B, Riskmethods or Resilinc, Bloomberg B-PIPE)
- Estimated annual disruption cost reduction (Year 2 target): USD 24M vs USD 42M baseline

---

## References

1. ISO 31000:2018 Risk management — Guidelines, International Organization for Standardization
2. ISO 28000:2022 Security and resilience — Supply chain security management systems
3. ASCM, SCOR Digital Standard (SCOR-DS), Association for Supply Chain Management, 2019
4. Lee, H.L., Padmanabhan, V., Whang, S., "The Bullwhip Effect in Supply Chains,"
   Sloan Management Review 38(3), 1997
5. Chen, F., Drezner, Z., Ryan, J.K., Simchi-Levi, D., "Quantifying the Bullwhip Effect
   in a Simple Supply Chain," Management Science 46(3), 2000
6. Sheffi, Y., Rice, J.B., "A Supply Chain View of the Resilient Enterprise,"
   MIT Sloan Management Review, Fall 2005
7. Herfindahl, O.C., Concentration in the Steel Industry, Columbia University PhD
   Dissertation, 1950
8. US Department of Justice / Federal Trade Commission, Horizontal Merger Guidelines,
   August 2010 (HHI concentration thresholds: 1500/2500)
9. Chopra, S., Meindl, P., Supply Chain Management, 6th Ed., Pearson, 2016
10. Allianz Global Corporate and Specialty (AGCS), Supply Chain Disruption: The Hidden Cost,
    AGCS Risk Barometer 2023
11. Caldara, D., Iacoviello, M., "Measuring Geopolitical Risk,"
    American Economic Review 112(4), 2022
12. Altman, E.I., "Financial Ratios, Discriminant Analysis and the Prediction of Corporate
    Bankruptcy," Journal of Finance 23(4), 1968
13. Hochreiter, S., Schmidhuber, J., "Long Short-Term Memory,"
    Neural Computation 9(8), 1997
14. Kipf, T.N., Welling, M., "Semi-Supervised Classification with Graph Convolutional
    Networks," ICLR 2017, arXiv:1609.02907
15. GDELT Project, https://www.gdeltproject.org — open dataset (CC0 / public domain)
16. World Bank, Worldwide Governance Indicators (WGI), 2023
17. Swiss Re Institute, Natural Catastrophe Database, 2024
18. McKinsey Global Institute, "Risk, resilience, and rebalancing in global value chains," 2020
