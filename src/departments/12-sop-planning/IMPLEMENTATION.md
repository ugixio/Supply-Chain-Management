# S&OP / IBP Analytics — Implementation Guide

**Department:** 12 — S&OP / Integrated Business Planning
**Analytics Domain:** S&OP and IBP Analytics
**Standard:** SCOR-DS (PLAN process) | Wallace 5-Step S&OP | Oliver Wight Class A IBP
**Version:** 2.0.0
**Date:** 2026-06-22
**Classification:** Internal — Senior Leadership and S&OP Programme Team
**Systems:** SAP IBP for S&OP | SAP S/4HANA | Apache Superset | PostgreSQL

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

Sales & Operations Planning (S&OP) and its advanced form, Integrated Business Planning (IBP), are the central management processes that align commercial commitments with operational capabilities and financial targets across a 24-to-36-month rolling horizon. When executed with analytical rigour, S&OP/IBP eliminates the chronic misalignment between what Sales promises, what Operations can deliver, and what Finance plans — a gap that costs the median enterprise between 2% and 4% of annual revenue in excess inventory, expediting costs, and lost sales.

This implementation guide defines the complete analytics framework for the S&OP/IBP Planning department, covering five core analytical domains: Plan vs. Actual Analysis (demand, supply, and financial plans), Consensus Forecast Bias and Accuracy, 12-Month Rolling Inventory Projection, Capacity Utilisation across the S&OP planning horizon, and the monthly S&OP Executive Meeting Pack. The framework is built on SAP IBP for S&OP as the planning engine, SAP S/4HANA as the ERP system of record, PostgreSQL as the analytical warehouse, and Apache Superset as the reporting and visualisation layer.

### Strategic Value

| Outcome | Baseline (Typical) | Target | Value Driver |
|---------|-------------------|--------|--------------|
| Forecast Accuracy (MAPE) | 35-50% at SKU level | <15% at product family level | Inventory reduction |
| Forecast Bias (MPE) | +/- 15% systematic | < +/- 2% | Service level improvement |
| Supply Plan Attainment | 75-85% | >92% | OTIF improvement |
| Inventory Projection Accuracy | +/- 15% at month 3 | < +/- 5% at month 3 | Working capital planning accuracy |
| Capacity Utilisation Visibility | None / manual | 100% horizon visibility | CapEx decision quality |
| S&OP Meeting Preparation Time | 3-5 days | <1 day (automated pack) | Planner productivity |

### Key Stakeholders

| Role | Primary Use | Frequency |
|------|-------------|-----------|
| CEO / General Manager | Executive S&OP decision package, revenue plan vs. actual | Monthly S&OP meeting |
| CFO | Financial plan vs. actual, revenue bridge, margin impact | Monthly S&OP + weekly flash |
| VP Sales / Commercial | Demand plan accuracy, bias by region/channel, gap to revenue plan | Monthly S&OP + weekly |
| VP Operations / Supply Chain | Supply plan attainment, capacity utilisation, inventory projection | Monthly S&OP + weekly |
| Demand Planning Manager | Consensus forecast, bias monitoring, statistical baseline vs. adjusted | Weekly |
| Supply Planning Manager | Supply plan exceptions, capacity constraints, 12-month projection | Weekly |
| S&OP Process Owner | Meeting pack, KPI tracking, continuous improvement | Monthly |

---

## 2. Analysis Objective

The primary objective of this analytics implementation is to give the S&OP leadership team a single, integrated, data-driven view of planning performance that enables confident decision-making at the monthly Executive S&OP meeting and supports continuous plan quality improvement between cycles.

### Specific Objectives

**Plan vs. Actual Analysis**
- Quantify the gap between the demand plan locked in the previous cycle, the supply plan committed to operations, and the financial plan approved by Finance — versus what actually occurred.
- Decompose revenue plan vs. actual into volume, price, and mix effects using a waterfall bridge methodology.
- Track these variances at the product family level for executive review and at the SKU/customer level for operational management.

**Consensus Forecast Bias and Accuracy**
- Monitor forecast accuracy (MAPE, RMSE) and systematic bias (MPE/Forecast Bias %) at each planning horizon bucket (M+1 through M+12).
- Differentiate statistical baseline accuracy from adjusted (consensus) accuracy to evaluate the value-add of commercial override.
- Identify which product families, channels, or customers are chronic over-forecasters (positive bias) or under-forecasters (negative bias).

**Inventory Projection**
- Produce a 12-month rolling inventory projection at product family and SKU level, combining the demand plan, supply plan, safety stock policy, and current stock position.
- Generate probabilistic inventory projections at P10 (optimistic), P50 (base), and P90 (conservative) scenarios using demand uncertainty bounds.

**Capacity Utilisation**
- Translate the supply plan into resource load (production lines, warehouse capacity, supplier capacity, logistics capacity) across the full 24-month S&OP horizon.
- Identify capacity bottlenecks and surplus positions enabling proactive capacity decisions.

**S&OP Executive Meeting Pack**
- Automate production of the monthly S&OP executive pack: one integrated document combining demand review, supply review, financial reconciliation, and recommended decisions — generated in < 1 day.

---

## 3. Scope

### In Scope

| Dimension | Detail |
|-----------|--------|
| Planning horizon | M+1 through M+24 (24-month rolling) |
| Reporting horizon | M-12 through current month for actuals; M+1 through M+12 for projections |
| Product aggregation | SKU → Product family → Business unit → Total company |
| Geographic aggregation | Ship-to location → Sales region → Country → Business unit → Total |
| Planning levels | Statistical baseline, adjusted forecast, consensus forecast, supply plan, financial plan |
| S&OP cycle cadence | Monthly cycle (4-week cycle: demand review → supply review → financial reconciliation → executive S&OP) with weekly demand sensing update |
| Inventory projection scope | Finished goods and purchased finished goods; excludes WIP and raw materials (covered in supply planning module) |
| Capacity scope | Internal production capacity (line/cell level); contracted third-party manufacturing; excludes tier-2 supplier capacity |
| Financial plan scope | Revenue plan, COGS plan, gross margin plan; excludes below-the-line P&L |

### Out of Scope

- Detailed MRP/production scheduling (covered in supply planning module)
- SKU-level financial costing (covered in Finance Controlling department 11)
- New product introduction planning (separate NPD process)
- Long-range strategic planning > 36 months (covered in Strategy function)

### System Boundaries

```
SAP IBP for S&OP (Planning Engine)
    |-- Statistical forecast (SES, Holt-Winters, MLR)  →  PostgreSQL [stg_ibp_stat_forecast]
    |-- Adjusted/consensus forecast                     →  PostgreSQL [stg_ibp_consensus_forecast]
    |-- Supply plan                                     →  PostgreSQL [stg_ibp_supply_plan]
    |-- Inventory projection                            →  PostgreSQL [stg_ibp_inventory_projection]
    |-- Capacity plan                                   →  PostgreSQL [stg_ibp_capacity_plan]

SAP S/4HANA (System of Record)
    |-- Actual sales (VBRP billing documents)           →  PostgreSQL [stg_sd_vbrp]
    |-- Actual production (PP orders CO11N)             →  PostgreSQL [stg_pp_aufm]
    |-- Actual inventory (MB52/MMBE)                   →  PostgreSQL [stg_mm_mard]
    |-- Financial plan (CO-PA / BPC)                   →  PostgreSQL [stg_copa_plan]
    |-- Actual financials (FAGLFLEXT / ACDOCA)         →  PostgreSQL [stg_fi_actuals]

PostgreSQL (Analytical Data Warehouse)
    |-- Staging, dimensions, facts, reporting tables

Apache Superset (Reporting Layer)
    |-- S&OP Analytics Hub (7 pages)
    |-- Automated S&OP meeting pack export
    |-- Weekly demand sensing dashboard
    |-- Scheduled refresh: daily at 06:00 UTC; on-demand during S&OP week
```

---

## 4. Business Questions

**BQ-01 — Demand Plan Accuracy Trend**
What is the 12-month trend of demand plan accuracy (MAPE) at M+1, M+3, and M+6 horizon buckets, by product family and sales region, and which families have chronically poor accuracy (MAPE > 30%)?

**BQ-02 — Forecast Bias**
Is the consensus forecast systematically biased? Which product families, channels, or customers show persistent positive bias (over-forecasting) or negative bias (under-forecasting) over the last 6 months?

**BQ-03 — Revenue Plan Bridge**
What drove the gap between last month's revenue plan and actual revenue? How much of the variance is attributable to volume (units), price (realised vs. planned selling price), and mix (product/channel shift)?

**BQ-04 — Supply Plan Attainment**
What percentage of the supply plan committed at the last S&OP cycle was actually delivered this month, broken down by production line and product family? Which gaps exceeded 5% of plan?

**BQ-05 — Inventory Projection**
Based on the current consensus demand forecast and the supply plan, what is the projected closing inventory (units and value) for each product family over the next 12 months, and where are the projected stock-out or excess inventory risk periods?

**BQ-06 — Capacity Utilisation**
Which production resources are projected to exceed 85% utilisation in the next 6 months (S&OP horizon), and what is the estimated financial impact of the projected capacity bottleneck?

**BQ-07 — Statistical vs. Adjusted Forecast Value-Add**
Does commercial adjustment to the statistical baseline improve forecast accuracy? For which product families does the statistical model outperform the adjusted consensus, indicating over-intervention by commercial teams?

**BQ-08 — Financial Reconciliation**
How does the volume plan (consensus demand × standard price) reconcile to the financial revenue plan in the business plan, and what is the dollar gap requiring Finance sign-off at the Executive S&OP meeting?

**BQ-09 — Safety Stock Coverage**
For the 12-month inventory projection, how many months show projected inventory falling below the safety stock target, indicating a service level risk, and what additional supply is required to close the gap?

**BQ-10 — Demand Sensing Weekly Update**
How has the week-1 demand signal (actual orders / POS data) evolved relative to the monthly consensus plan, and should the supply plan be adjusted before the next formal S&OP cycle?

**BQ-11 — Scenario Comparison**
Under the P90 (conservative demand) scenario, which product families generate excess inventory > $1M by month 6, and what is the holding cost exposure?

**BQ-12 — S&OP Cycle Discipline**
Are all required data submissions (statistical forecast, commercial overrides, supply plan confirmation, financial reconciliation) received on time for each step of the S&OP cycle, and which functions are chronic late submitters?

---

## 5. Data Sources

### DS-01: SAP IBP Statistical Forecast

| Attribute | Detail |
|-----------|--------|
| Name | SAP IBP Statistical Baseline Forecast |
| System | SAP Integrated Business Planning for S&OP |
| Tables / API | SAP IBP OData API: ForecastResultSet; PostgreSQL staging: stg_ibp_stat_forecast |
| Owner | Demand Planning team |
| Extraction Frequency | Daily delta (IBP planning run results); full reload at each monthly statistical run |
| Critical Fields | planning_level_id, product_id, location_id, customer_group_id, fiscal_period (YYYYMM), horizon_bucket, stat_forecast_qty, stat_forecast_value, algorithm_used (SES/HW/MLR/ARIMA), mape_in_sample, bias_in_sample, model_version |
| Primary Key | product_id + location_id + fiscal_period + horizon_bucket + model_version |
| Validations | stat_forecast_qty >= 0; horizon_bucket IN (1..24); algorithm_used is a valid IBP algorithm code; model_version is the latest approved model run |
| Known Data Errors | IBP sometimes generates negative forecasts for slow-moving SKUs — floor to zero; double-export from IBP if planning run triggered twice intraday — deduplicate by MAX(run_timestamp) |
| Evidence Required | Statistical forecast record count reconciles to IBP forecast key figure report (KEYFIG_STAT) |

### DS-02: SAP IBP Consensus / Adjusted Forecast

| Attribute | Detail |
|-----------|--------|
| Name | SAP IBP Consensus Demand Plan (after commercial override) |
| System | SAP IBP for S&OP — Demand Review step |
| Tables / API | SAP IBP OData API: ConsensusKeyFigure; PostgreSQL staging: stg_ibp_consensus_forecast |
| Owner | Demand Planning Manager (process owner); Commercial / Sales teams (contributors) |
| Extraction Frequency | Daily (captures incremental overrides); locked version snapshot at Demand Review gate |
| Critical Fields | product_id, location_id, customer_group_id, fiscal_period, horizon_bucket, consensus_forecast_qty, consensus_forecast_value, commercial_override_qty, commercial_override_reason_code, override_by_user, override_timestamp, is_locked (1 at demand review gate), lock_version |
| Primary Key | product_id + location_id + fiscal_period + horizon_bucket + lock_version |
| Validations | consensus_forecast_qty >= 0; commercial_override_reason_code must be in approved reason code list; is_locked = 1 only after demand review gate timestamp |
| Known Data Errors | Users sometimes override at wrong planning level (SKU instead of family) — validate against planning hierarchy; reason code missing for overrides > 10% of statistical baseline — reject with error |
| Evidence Required | Locked consensus forecast total (sum of consensus_forecast_value) reconciles to demand review sign-off document signed by VP Sales |

### DS-03: SAP IBP Supply Plan

| Attribute | Detail |
|-----------|--------|
| Name | SAP IBP Supply Plan (after supply review) |
| System | SAP IBP for S&OP — Supply Review step |
| Tables / API | SAP IBP OData API: SupplyPlanKeyFigure; PostgreSQL staging: stg_ibp_supply_plan |
| Owner | Supply Planning Manager |
| Extraction Frequency | Daily delta; locked version snapshot at Supply Review gate |
| Critical Fields | product_id, location_id, resource_id, fiscal_period, horizon_bucket, supply_plan_qty, supply_plan_value, confirmed_capacity_qty, capacity_utilisation_pct, supply_gap_qty (consensus_forecast_qty - supply_plan_qty), is_locked, lock_version |
| Primary Key | product_id + location_id + fiscal_period + horizon_bucket + lock_version |
| Validations | supply_plan_qty >= 0; supply_gap_qty = consensus_forecast_qty - supply_plan_qty (computed check); capacity_utilisation_pct between 0 and 150% (> 100% = overtime scenario) |
| Known Data Errors | Supply plan not updated after demand review lock — check if supply_plan run_timestamp > demand_review_lock_timestamp; resource_id mapping gaps for new production lines |
| Evidence Required | Supply plan attainment for prior month: actual_production / supply_plan_qty reconciles to PP module actual output |

### DS-04: SAP S/4HANA Actual Sales

| Attribute | Detail |
|-----------|--------|
| Name | SAP SD Billing Documents (Actual Revenue) |
| System | SAP S/4HANA SD module |
| Tables | VBRK (billing document header), VBRP (billing document line items), VBAK (sales order header), VBAP (sales order items) |
| PostgreSQL Staging | stg_sd_vbrk, stg_sd_vbrp |
| Owner | Sales / Order-to-Cash team |
| Extraction Frequency | Near-real-time CDC; full period reload nightly |
| Critical Fields | VBELN (billing document), POSNR (line), MATNR (material), KUNAG (sold-to customer), FKDAT (billing date), FKIMG (billed quantity), VRKME (sales UOM), NETWR (net value), WAERS (currency), AUBEL (sales order reference), WERKS (plant), VTWEG (distribution channel), SPART (division) |
| Primary Key | VBELN + POSNR |
| Validations | FKART IN ('F2', 'ZF2', 'ZRE') for standard invoices and returns; FKDAT within reporting period; NETWR != 0; exclude credit/debit memos (FKART = 'G2', 'L2') unless analysing price corrections |
| Known Data Errors | Inter-company billing (FKART = 'IV') must be excluded from customer-facing demand actuals; backdated billing corrections create period attribution issues — assign to billing date, not service date |
| Evidence Required | Sum of NETWR for period reconciles to FI Revenue GL account (FAGLFLEXT or ACDOCA) for the same period |

### DS-05: SAP S/4HANA Actual Inventory

| Attribute | Detail |
|-----------|--------|
| Name | SAP MM Stock Overview (Period-End Inventory Snapshot) |
| System | SAP S/4HANA MM module |
| Tables | MARD (storage location stock), MARC (plant-level MRP data), MBEWH (material valuation history by period) |
| PostgreSQL Staging | stg_mm_mard, stg_mm_mbewh |
| Owner | Inventory Management / Supply Planning team |
| Extraction Frequency | Daily snapshot (MARD); Monthly period-end snapshot (MBEWH) |
| Critical Fields | MATNR (material), WERKS (plant), LGORT (storage location), LABST (unrestricted stock), EINME (GR blocked), SPEME (blocked stock), UMLME (in-transfer), LFGJA (fiscal year), LFMON (period), LBKUM (total valuated stock qty from MBEWH), SALK3 (total stock value) |
| Primary Key | MATNR + WERKS + LGORT (MARD daily); MATNR + BWKEY + LFGJA + LFMON (MBEWH monthly) |
| Validations | LABST >= 0; SALK3 / LBKUM = standard or moving average price (unit price consistency); period-end snapshot taken after all GIs/GRs posted for the period |
| Known Data Errors | In-transit stock (UMLME) sometimes excluded from period-end snapshot if STO not yet received — include in projection logic; consignment stock requires separate extraction from MKOL |
| Evidence Required | Sum of LBKUM by plant reconciles to MM inventory report (MB52) for the same period |

### DS-06: Financial Plan (SAP BPC / CO-PA)

| Attribute | Detail |
|-----------|--------|
| Name | Financial Plan — Revenue, COGS, Gross Margin by Product Family |
| System | SAP BPC (Business Planning and Consolidation) or SAP CO-PA |
| Tables | PostgreSQL staging: stg_copa_plan (extracted from CO-PA CE1XXXX planning version) |
| Owner | Finance Business Partners / FP&A team |
| Extraction Frequency | Monthly (updated at each financial planning cycle); locked version at S&OP financial reconciliation gate |
| Critical Fields | product_family_id, region_id, channel_id, fiscal_period, plan_version, plan_revenue, plan_cogs, plan_gross_margin, plan_volume_units, plan_avg_selling_price, plan_gross_margin_pct, created_by, lock_timestamp |
| Primary Key | product_family_id + region_id + channel_id + fiscal_period + plan_version |
| Validations | plan_revenue = plan_volume_units × plan_avg_selling_price (within rounding tolerance); plan_gross_margin = plan_revenue - plan_cogs; plan_gross_margin_pct = plan_gross_margin / plan_revenue × 100; plan_version is current approved version |
| Known Data Errors | Volume plans submitted in different UOMs across regions — normalise to base UOM; plan sometimes missing for new product families launched after annual plan — require Finance to submit interim plan |
| Evidence Required | Financial plan total reconciles to Board-approved annual operating plan (AOP) revenue target |

---

## 6. Data Model

### Conceptual Entity Relationship

```
dim_product ──────────────────────────────────────────────────────────┐
dim_product_family ────────────────────────────────────────────────────┤
dim_location ──────────────────────────────────────────────────────────┤
dim_customer_group ────────────────────────────────────────────────────┤
dim_channel ───────────────────────────────────────────────────────────┤
dim_resource ──────────────────────────────────────────────────────────┤
dim_date ──────────────────────────────────────────────────────────────┤
dim_sop_cycle_version ─────────────────────────────────────────────────┤
                                                                        │
fact_demand_plan ────────────────────────────────────────────────────►│
    (product_family FK, location FK, channel FK, customer_group FK,   │
     fiscal_period FK, sop_cycle_version FK,                          │
     stat_forecast_qty, consensus_forecast_qty, actual_qty,           │
     demand_plan_accuracy, forecast_bias, mape, rmse, horizon_bucket) │
                                                                        │
fact_supply_plan ────────────────────────────────────────────────────►│
    (product FK, location FK, resource FK, fiscal_period FK,          │
     sop_cycle_version FK,                                            │
     supply_plan_qty, actual_production_qty,                          │
     supply_attainment_pct, supply_gap_qty,                           │
     capacity_utilisation_pct, horizon_bucket)                        │
                                                                        │
fact_financial_plan ─────────────────────────────────────────────────►│
    (product_family FK, region FK, channel FK, fiscal_period FK,      │
     plan_version, plan_revenue, actual_revenue,                      │
     plan_cogs, actual_cogs, plan_gross_margin, actual_gross_margin,  │
     volume_effect, price_effect, mix_effect, revenue_variance_pct)   │
                                                                        │
fact_inventory_projection ───────────────────────────────────────────►│
    (product_family FK, location FK, fiscal_period FK,                │
     sop_cycle_version FK,                                            │
     opening_stock, supply_plan_inflow, demand_plan_outflow,          │
     projected_closing_stock, safety_stock_target,                    │
     actual_closing_stock, projection_accuracy_pct,                   │
     stockout_risk_flag, excess_flag,                                 │
     p10_closing_stock, p50_closing_stock, p90_closing_stock)         │
                                                                        │
fact_capacity_utilisation ───────────────────────────────────────────►│
    (resource FK, location FK, fiscal_period FK, sop_cycle_version FK,│
     available_capacity_hrs, planned_load_hrs,                        │
     capacity_utilisation_pct, overtime_hrs_required,                 │
     bottleneck_flag, horizon_bucket)                                 │
                                                                        │
fact_sop_cycle_kpi ──────────────────────────────────────────────────►│
    (sop_cycle_version FK, fiscal_period FK,                          │
     demand_plan_accuracy_m1, demand_plan_accuracy_m3, demand_plan_accuracy_m6,
     forecast_bias_m1, forecast_bias_m3,                              │
     supply_attainment_pct, financial_revenue_variance_pct,           │
     inventory_projection_accuracy_m3, avg_capacity_utilisation)      │
```

### Star Schema Design (PostgreSQL)

```sql
-- Conformed Dimensions
dim_date                -- Calendar + fiscal calendar
dim_product             -- SKU master (from SAP MARA + MAKT)
dim_product_family      -- Product family hierarchy (from IBP planning levels)
dim_location            -- Plant + DC + sales region
dim_customer_group      -- Customer segmentation (A/B/C + channel)
dim_channel             -- Sales channel (modern trade, e-commerce, wholesale, direct)
dim_resource            -- Production resource / work center (SAP CR03)
dim_sop_cycle_version   -- S&OP cycle version master (one row per monthly cycle)
dim_plan_version        -- Plan version master (IBP version + BPC financial version)
```

---

## 7. Data Dictionary

### DD-01: fact_demand_plan

| Attribute | Detail |
|-----------|--------|
| Name | fact_demand_plan |
| Granularity | One row per product family, location, channel, fiscal period, horizon bucket, and S&OP cycle version |
| Primary Key | demand_plan_id (surrogate) |
| Relationships | FK to dim_product_family, dim_location, dim_channel, dim_date, dim_sop_cycle_version |

**Fields:**

| Field Name | Type | Description |
|------------|------|-------------|
| demand_plan_id | BIGINT | Surrogate primary key |
| product_family_id | NVARCHAR(20) | Product family code (IBP planning level) |
| location_id | NVARCHAR(10) | Plant or DC code |
| channel_id | NVARCHAR(10) | Sales channel code |
| fiscal_period | CHAR(6) | YYYYMM — the period being planned (target period) |
| cycle_period | CHAR(6) | YYYYMM — the S&OP cycle in which this plan was created (source cycle) |
| sop_cycle_version_id | INT | FK to dim_sop_cycle_version |
| horizon_bucket | TINYINT | 1-24 (months ahead from cycle_period to fiscal_period) |
| stat_forecast_qty | DECIMAL(18,3) | Statistical baseline forecast quantity |
| commercial_override_qty | DECIMAL(18,3) | Quantity of commercial adjustment (positive = upward, negative = downward) |
| consensus_forecast_qty | DECIMAL(18,3) | Final consensus forecast after all adjustments (stat + commercial) |
| actual_qty | DECIMAL(18,3) | Actual sales quantity (from SD billing; NULL for future periods) |
| stat_forecast_value | DECIMAL(18,2) | Statistical forecast x standard selling price |
| consensus_forecast_value | DECIMAL(18,2) | Consensus forecast x standard selling price |
| actual_value | DECIMAL(18,2) | Actual billed revenue (from VBRP) |
| demand_plan_accuracy | DECIMAL(10,4) | (1 - ABS(actual_qty - consensus_forecast_qty) / actual_qty) x 100 |
| forecast_bias | DECIMAL(10,4) | (consensus_forecast_qty - actual_qty) / actual_qty x 100 (+ = over, - = under) |
| mape | DECIMAL(10,4) | Mean Absolute Percentage Error for this period at this horizon |
| override_value_add | DECIMAL(10,4) | Accuracy improvement from commercial override (stat_mape - consensus_mape) |
| uom | NVARCHAR(3) | Planning unit of measure (GS1 UOM code) |
| etl_load_datetime | DATETIME2 | ETL load timestamp (UTC) |

---

### DD-02: fact_financial_plan

| Attribute | Detail |
|-----------|--------|
| Name | fact_financial_plan |
| Granularity | One row per product family, region, channel, fiscal period, and plan version |
| Primary Key | financial_plan_id (surrogate) |
| Relationships | FK to dim_product_family, dim_location (region), dim_channel, dim_date, dim_plan_version |

**Fields:**

| Field Name | Type | Description |
|------------|------|-------------|
| financial_plan_id | BIGINT | Surrogate primary key |
| product_family_id | NVARCHAR(20) | Product family code |
| region_id | NVARCHAR(10) | Sales region code |
| channel_id | NVARCHAR(10) | Sales channel code |
| fiscal_period | CHAR(6) | YYYYMM |
| plan_version | NVARCHAR(20) | Plan version identifier (e.g., AOP_2026, IBP_CY_202606) |
| plan_revenue | DECIMAL(18,2) | Planned revenue (in group currency) |
| actual_revenue | DECIMAL(18,2) | Actual billed revenue (NULL for future periods) |
| plan_volume_units | DECIMAL(18,3) | Planned volume in units |
| actual_volume_units | DECIMAL(18,3) | Actual volume sold in units |
| plan_avg_selling_price | DECIMAL(18,4) | Planned average selling price per unit |
| actual_avg_selling_price | DECIMAL(18,4) | Actual realised average selling price per unit |
| plan_cogs | DECIMAL(18,2) | Planned cost of goods sold |
| actual_cogs | DECIMAL(18,2) | Actual COGS |
| plan_gross_margin | DECIMAL(18,2) | Planned gross margin |
| actual_gross_margin | DECIMAL(18,2) | Actual gross margin |
| plan_gross_margin_pct | DECIMAL(10,4) | Planned gross margin % |
| actual_gross_margin_pct | DECIMAL(10,4) | Actual gross margin % |
| revenue_variance | DECIMAL(18,2) | actual_revenue - plan_revenue |
| revenue_variance_pct | DECIMAL(10,4) | revenue_variance / plan_revenue x 100 |
| volume_effect | DECIMAL(18,2) | Revenue variance attributable to volume: (actual_vol - plan_vol) x plan_price |
| price_effect | DECIMAL(18,2) | Revenue variance attributable to price: (actual_price - plan_price) x actual_vol |
| mix_effect | DECIMAL(18,2) | Residual variance = revenue_variance - volume_effect - price_effect |
| etl_load_datetime | DATETIME2 | ETL load timestamp (UTC) |

---

### DD-03: fact_inventory_projection

| Attribute | Detail |
|-----------|--------|
| Name | fact_inventory_projection |
| Granularity | One row per product family, location, fiscal period, and S&OP cycle version |
| Primary Key | inv_proj_id (surrogate) |
| Relationships | FK to dim_product_family, dim_location, dim_date, dim_sop_cycle_version |

**Fields:**

| Field Name | Type | Description |
|------------|------|-------------|
| inv_proj_id | BIGINT | Surrogate primary key |
| product_family_id | NVARCHAR(20) | Product family code |
| location_id | NVARCHAR(10) | Plant or DC code |
| fiscal_period | CHAR(6) | YYYYMM — the projected period |
| cycle_period | CHAR(6) | YYYYMM — the S&OP cycle that produced this projection |
| sop_cycle_version_id | INT | FK to dim_sop_cycle_version |
| opening_stock_units | DECIMAL(18,3) | Projected or actual opening stock for the period |
| supply_plan_inflow | DECIMAL(18,3) | Planned production or purchase receipts in the period |
| demand_plan_outflow | DECIMAL(18,3) | Projected demand outflow (consensus forecast) |
| projected_closing_stock | DECIMAL(18,3) | opening_stock + supply_inflow - demand_outflow (P50 base case) |
| p10_closing_stock | DECIMAL(18,3) | P10 optimistic scenario (demand at P10 = lower demand uncertainty bound) |
| p90_closing_stock | DECIMAL(18,3) | P90 conservative scenario (demand at P90 = upper demand uncertainty bound) |
| safety_stock_target | DECIMAL(18,3) | Safety stock target for the period (from SafetyStock module) |
| dos_projected | DECIMAL(10,2) | Days of Supply = projected_closing_stock / (demand_plan_outflow / 30) |
| stockout_risk_flag | BIT | 1 if projected_closing_stock < safety_stock_target |
| excess_flag | BIT | 1 if projected_closing_stock > safety_stock_target * 3.0 (configurable multiplier) |
| actual_closing_stock | DECIMAL(18,3) | Actual closing stock (from MBEWH; NULL for future periods) |
| projection_accuracy_pct | DECIMAL(10,4) | ABS(projected - actual) / actual x 100 (computed when actuals available) |
| projected_inv_value | DECIMAL(18,2) | projected_closing_stock x standard_cost_per_unit |
| excess_inv_value | DECIMAL(18,2) | MAX(0, projected_closing_stock - safety_stock_target * 3.0) x standard_cost |
| etl_load_datetime | DATETIME2 | ETL load timestamp (UTC) |

---

### DD-04: fact_capacity_utilisation

| Attribute | Detail |
|-----------|--------|
| Name | fact_capacity_utilisation |
| Granularity | One row per resource, location, fiscal period, and S&OP cycle version |
| Primary Key | cap_util_id (surrogate) |
| Relationships | FK to dim_resource, dim_location, dim_date, dim_sop_cycle_version |

**Fields:**

| Field Name | Type | Description |
|------------|------|-------------|
| cap_util_id | BIGINT | Surrogate primary key |
| resource_id | NVARCHAR(20) | Production resource / work center ID (SAP CRP resource) |
| location_id | NVARCHAR(10) | Plant code |
| fiscal_period | CHAR(6) | YYYYMM |
| sop_cycle_version_id | INT | FK to dim_sop_cycle_version |
| horizon_bucket | TINYINT | Months ahead from S&OP cycle to this period (1-24) |
| available_capacity_hrs | DECIMAL(10,2) | Total available production hours (shifts x days x line efficiency) |
| planned_load_hrs | DECIMAL(10,2) | Total planned load from supply plan (supply_plan_qty x time_per_unit) |
| capacity_utilisation_pct | DECIMAL(10,4) | planned_load_hrs / available_capacity_hrs x 100 |
| overtime_hrs_required | DECIMAL(10,2) | MAX(0, planned_load_hrs - available_capacity_hrs) |
| capacity_gap_units | DECIMAL(18,3) | Units that cannot be produced within available capacity |
| bottleneck_flag | BIT | 1 if capacity_utilisation_pct > 85% threshold |
| critical_bottleneck_flag | BIT | 1 if capacity_utilisation_pct > 100% |
| actual_capacity_hrs_used | DECIMAL(10,2) | Actual hours confirmed (from PP CO11N; NULL for future) |
| actual_utilisation_pct | DECIMAL(10,4) | actual_capacity_hrs_used / available_capacity_hrs x 100 |
| etl_load_datetime | DATETIME2 | ETL load timestamp (UTC) |

---

## 8. Transformation Rules

### TR-01: Demand Plan Accuracy Calculation

Accuracy is calculated only for periods where both forecast and actuals are available (closed periods). The forecast used is the consensus forecast locked at the demand review gate for the cycle N months prior to the actual period.

```sql
-- For horizon_bucket = 1: use the consensus forecast from the cycle immediately before the actual period
-- For horizon_bucket = 3: use the consensus forecast from 3 cycles before the actual period

demand_plan_accuracy =
    CASE WHEN actual_qty > 0
         THEN (1 - ABS(consensus_forecast_qty - actual_qty) / actual_qty) * 100
         ELSE NULL  -- exclude zero-actual periods from accuracy calculation
    END

-- Floor at 0 (accuracy cannot be negative in this representation)
demand_plan_accuracy = GREATEST(0, demand_plan_accuracy)
```

### TR-02: Forecast Bias Calculation

```sql
-- Per period bias
period_bias_pct = (consensus_forecast_qty - actual_qty) / NULLIF(actual_qty, 0) * 100

-- Rolling N-period bias (e.g., 6-month rolling)
rolling_bias_pct = SUM(consensus_forecast_qty - actual_qty) / NULLIF(SUM(actual_qty), 0) * 100
-- Positive = systematic over-forecast; Negative = systematic under-forecast

-- Statistical vs. consensus bias comparison
stat_bias_pct = (stat_forecast_qty - actual_qty) / NULLIF(actual_qty, 0) * 100
override_value_add = ABS(stat_bias_pct) - ABS(period_bias_pct)
-- Positive = commercial override improved accuracy; Negative = override worsened accuracy
```

### TR-03: Revenue Bridge Decomposition (Waterfall)

```sql
-- Volume Effect: what would revenue be if only volume changed?
volume_effect = (actual_volume_units - plan_volume_units) * plan_avg_selling_price

-- Price Effect: what is the revenue impact of price deviation?
price_effect = (actual_avg_selling_price - plan_avg_selling_price) * actual_volume_units

-- Mix Effect: residual = actual revenue - plan revenue - volume effect - price effect
-- Mix captures the shift between high-margin and low-margin products within the family
mix_effect = actual_revenue - plan_revenue - volume_effect - price_effect

-- Validation: volume_effect + price_effect + mix_effect = revenue_variance
```

### TR-04: 12-Month Rolling Inventory Projection

```sql
-- Month-by-month rolling calculation:
-- For month T:
opening_stock[T] = actual_closing_stock[T-1]  -- for T = current month
opening_stock[T] = projected_closing_stock[T-1]  -- for T > current month

projected_closing_stock[T] = opening_stock[T]
                            + supply_plan_inflow[T]
                            - demand_plan_outflow[T]

-- Days of Supply
dos_projected[T] = projected_closing_stock[T]
                   / NULLIF(demand_plan_outflow[T] / 30.0, 0)

-- P10/P90 scenarios using demand uncertainty band
-- Demand uncertainty: apply MAPE at each horizon bucket as +/- band
p10_demand_outflow[T] = demand_plan_outflow[T] * (1 - mape_at_horizon[T] / 100)
p90_demand_outflow[T] = demand_plan_outflow[T] * (1 + mape_at_horizon[T] / 100)

p10_closing_stock[T] = opening_stock[T] + supply_plan_inflow[T] - p10_demand_outflow[T]
p90_closing_stock[T] = opening_stock[T] + supply_plan_inflow[T] - p90_demand_outflow[T]
```

### TR-05: Capacity Utilisation Calculation

```sql
-- Available capacity: plant calendar x shifts x line efficiency factor
available_capacity_hrs = working_days_in_period
                       * shifts_per_day
                       * hours_per_shift
                       * line_efficiency_factor  -- typically 0.85 OEE

-- Planned load: sum of supply plan quantities x unit production time
planned_load_hrs = SUM(supply_plan_qty * production_time_hrs_per_unit)
                  -- aggregated across all products routed through the resource

capacity_utilisation_pct = planned_load_hrs / NULLIF(available_capacity_hrs, 0) * 100

-- Overtime required when > 100% utilisation
overtime_hrs_required = GREATEST(0, planned_load_hrs - available_capacity_hrs)

-- Capacity gap in units (at bottleneck resource)
capacity_gap_units = overtime_hrs_required / NULLIF(avg_production_time_hrs_per_unit, 0)
```

### TR-06: Supply Plan Attainment

```sql
-- Calculated once actuals are available (following month)
supply_attainment_pct = actual_production_qty / NULLIF(supply_plan_qty, 0) * 100

-- Gap quantity
supply_gap_qty = actual_production_qty - supply_plan_qty
-- Negative = under-attainment (supply fell short of plan)
-- Positive = over-attainment (produced more than planned)
```

---

## 9. Business Rules

### BR-01: Forecast Lock and Version Control
The consensus forecast is locked at the end of the Demand Review step (Week 2 of the 4-week S&OP cycle). Once locked, the locked version must not be modified — any subsequent revisions create a new version in SAP IBP. Only the locked version is used for official accuracy/bias KPI measurement.

### BR-02: Override Reason Code Mandatory
Any commercial override to the statistical baseline that changes the forecast by more than 10% in absolute terms for a given product family and horizon bucket requires a mandatory reason code from the approved list:
- NEW_BUSINESS: New customer or distribution gain
- LOST_BUSINESS: Customer loss or distribution reduction
- PROMO_EVENT: Confirmed promotional activity
- PRICE_CHANGE: Planned selling price change
- MARKET_INTEL: Competitor or market intelligence
- SUPPLY_CONSTRAINED: Demand is supply-limited
- MANAGEMENT_DIRECTION: Management input

Overrides without a valid reason code are rejected by the IBP system validation and flagged in the analytics.

### BR-03: Financial Reconciliation Gate
The volume plan (sum of consensus_forecast_value at product family level) must reconcile to the financial revenue plan (plan_revenue from BPC/CO-PA) within a tolerance of +/- 2%. Gaps larger than 2% must be explained and agreed between the Demand Planning Manager and Finance Business Partner before the Executive S&OP meeting.

### BR-04: Safety Stock Target Integration
The safety stock target used in inventory projection is sourced from the SafetyStock module (Department 03 — Demand Planning). For ABC-XYZ classification:
- A-X items: Method 4 safety stock (accounts for demand and lead time variability)
- B-Y, A-Y: Method 3 safety stock
- C-Z, slow-moving: Fixed coverage policy (N weeks of forward demand)

Safety stock targets are refreshed monthly as part of the S&OP planning run.

### BR-05: Capacity Bottleneck Escalation
Resources projected above 85% utilisation for 3 or more consecutive months in the S&OP horizon are flagged as CAPACITY_ALERT and escalated to the Executive S&OP meeting for decision. Resources projected above 100% utilisation for any month in the next 3 months trigger an IMMEDIATE escalation outside the normal monthly cadence.

### BR-06: Inventory Risk Thresholds
- Stockout risk: projected_closing_stock < safety_stock_target → stockout_risk_flag = 1. Requires supply plan adjustment.
- Excess inventory risk: projected_closing_stock > safety_stock_target × 3.0 for 2+ consecutive months → excess_flag = 1. Requires demand or supply plan adjustment.
- Obsolescence risk: projected_closing_stock > safety_stock_target × 5.0 AND product_status IN ('PHASE_OUT', 'DISCONTINUED') → escalate to Marketing for markdown plan.

### BR-07: S&OP Cycle Discipline
Each S&OP cycle step has a defined submission deadline. Late submissions (> 2 business days past deadline) are tracked and reported to the S&OP Process Owner. Chronic late submitters (> 2 months in a quarter) are escalated to the VP-level owner of the submitting function.

---

## 10. KPIs and Formulas

### KPI-01: Demand Plan Accuracy

```
Demand_Plan_Accuracy = (1 - ABS(Actual_Sales - Demand_Plan) / Actual_Sales) × 100
```
- Expressed as a percentage (higher = better; 100% = perfect)
- Calculated at product family level (not SKU level for executive reporting)
- Reported at three horizon buckets: M+1 (one month ahead), M+3 (three months), M+6 (six months)
- Target: > 85% at M+1, > 75% at M+3, > 65% at M+6
- World-class: > 90% at M+1, > 85% at M+3

**Note:** Zero-actual months excluded from MAPE calculation to avoid division-by-zero distortion.

### KPI-02: Forecast Bias

```
Forecast_Bias = SUM(Demand_Plan - Actual_Sales) / SUM(Actual_Sales) × 100
```
- Positive = systematic over-forecasting (supply risk: excess inventory)
- Negative = systematic under-forecasting (service risk: stockouts)
- Target: < +/- 2% on a rolling 6-month basis
- Alert threshold: > +/- 5% for any product family over 3 consecutive months (systematic bias requiring investigation)

### KPI-03: Supply Plan Attainment

```
Supply_Plan_Attainment = Actual_Supply / Supply_Plan × 100
```
- Target: > 92% (world-class > 95%)
- Measured for the period closing: compare supply plan locked at Supply Review gate vs. actual production/receipts
- Reported by production line, plant, and product family

### KPI-04: Revenue Plan vs. Actual

```
Revenue_Plan_vs_Actual = (Actual_Revenue - Revenue_Plan) / Revenue_Plan × 100
```
- Positive = favorable (exceeded plan)
- Negative = unfavorable (below plan)
- Decomposed into: Volume Effect + Price Effect + Mix Effect (waterfall)

### KPI-05: Inventory Projection Accuracy

```
Inventory_Projection_Accuracy = ABS(Projected_Closing_Stock - Actual_Closing_Stock) / Actual_Closing_Stock × 100
```
- Lower = better (measures how accurate the S&OP projection was)
- Measured at M+1 and M+3 horizons (when actuals become available)
- Target: < 5% at M+1, < 10% at M+3

### KPI-06: Capacity Utilisation (S&OP Horizon)

```
Capacity_Utilisation = Planned_Load / Available_Capacity × 100
```
- Reported for each resource and plant across the full 24-month S&OP horizon
- Targets: Green < 80%, Amber 80-95%, Red > 95%
- Bottleneck resources (> 85% for 3+ months) flagged for Executive S&OP agenda

### KPI-07: Service Level Plan vs. Actual

```
Service_Level_Gap = Actual_Fill_Rate - Planned_Fill_Rate  (in percentage points)
```
- Negative = service level underperformance vs. plan (requires root-cause analysis)
- Planned Fill Rate comes from supply plan committed to at Supply Review gate
- Actual Fill Rate from Order-to-Delivery fulfillment data (SD module OTIF/Fill Rate)
- Target: Service Level Gap within +/- 1 percentage point

### KPI-08: Order Entry Accuracy Rate (S&OP Demand Signal)

At the S&OP level, order entry accuracy tracks the fidelity of customer demand signals feeding the monthly consensus demand plan. Errors in order entry (wrong customer, incorrect material, mismatched quantities) distort the demand baseline used at the Demand Review and Executive S&OP gates, causing revenue plan vs. actual variances that are actually data quality issues — not true demand changes.

```
Order Entry Accuracy Rate — S&OP (%) =
    Orders feeding the consensus plan with zero data corrections
    ─────────────────────────────────────────────────────────── × 100
              Total orders in the planning period
```

**SQL (PostgreSQL):**

```sql
-- Order entry accuracy by business unit and S&OP planning period
SELECT
    DATE_TRUNC('month', o.order_date)                    AS sop_month,
    o.sales_org,
    o.business_unit,
    COUNT(DISTINCT o.order_id)                           AS total_orders,
    COUNT(DISTINCT o.order_id)
        FILTER (WHERE o.amendment_count = 0
                  AND o.data_correction_flag = FALSE)    AS clean_orders,
    ROUND(
        COUNT(DISTINCT o.order_id)
            FILTER (WHERE o.amendment_count = 0
                      AND o.data_correction_flag = FALSE)::numeric
        / NULLIF(COUNT(DISTINCT o.order_id), 0) * 100,
    2)                                                   AS entry_accuracy_pct,
    -- Impact on revenue plan: value of corrected orders
    SUM(CASE WHEN o.data_correction_flag THEN o.net_value_eur ELSE 0 END)
                                                         AS corrected_order_value_eur
FROM fact_orders o
WHERE o.order_date >= DATE_TRUNC('month', CURRENT_DATE) - INTERVAL '6 months'
  AND o.order_status <> 'CANCELLED'
GROUP BY 1, 2, 3
ORDER BY 1 DESC, entry_accuracy_pct ASC;
```

- **Target**: ≥ 98% overall; failure cascades into Forecast Bias and Plan vs. Actual variances
- **Frequency**: Monthly (Demand Review gate); week-1 flash available
- **Owner**: Demand Management / S&OP Process Owner
- **S&OP gate use**: If entry accuracy < 96%, the Demand Review chair must flag the baseline as unreliable and apply a data-quality adjustment factor before consensus

---

## 11. Analytical Logic

### Waterfall Bridge: Revenue Plan vs. Actual

The revenue bridge analysis is the central tool at the Executive S&OP financial reconciliation. A month-over-month waterfall chart displays the following sequential effects:

```
Prior Month Actual Revenue
  + / - New Business: Revenue from new customers or distribution gains
  + / - Lost Business: Revenue lost from customer attrition or delisting
  + / - Volume (Existing): Volume change on existing customers vs. plan
  + / - Price: Realised price vs. planned average selling price
  + / - Mix: Shift between product families (higher/lower margin products)
  = Current Month Revenue Plan
  + / - Demand Variance: Actual demand vs. consensus plan
  = Current Month Actual Revenue
```

This decomposition is produced at the product family and region level, enabling Sales leadership to explain plan vs. actual with specificity rather than aggregated variance.

### 12-Month Rolling Inventory Projection

The inventory projection is a forward-looking waterfall:

```
For each product family and each month T in [current+1, current+12]:

Projected_Closing[T] = Opening[T]
                      + Supply_Plan_Inflow[T]   (from supply plan, adjusted for capacity)
                      - Demand_Outflow[T]        (from consensus forecast)
                      - Safety_Stock_Adjustment  (if safety stock policy changes in period)

Opening[T] = Projected_Closing[T-1]   (previous projected period)
Opening[current+1] = Actual_Closing[current]  (anchored to actual stock)
```

Three scenario bands are overlaid:
- **P10 (Optimistic)**: Demand at the lower uncertainty band → higher projected stock
- **P50 (Base Case)**: Demand at consensus → central projection
- **P90 (Conservative)**: Demand at the upper uncertainty band → lower projected stock

The uncertainty band at each horizon is derived from the historical MAPE at that horizon bucket, applied as a symmetric +/- percentage around the consensus forecast.

Stockout risk periods (where P50 projected stock < safety stock) and excess risk periods (where P10 projected stock > 3× safety stock) are highlighted with colour-coded flags on the chart, directly surfacing supply-demand decisions for the S&OP team.

### Bias Root-Cause Analysis

For product families with persistent forecast bias (> +/- 5% for 3+ months), the analytics system applies the following diagnostic logic:

1. **Commercial override contribution**: Is the bias driven by the statistical model or by commercial overrides? Compare stat_bias_pct vs. consensus_bias_pct. If consensus_bias_pct > stat_bias_pct in absolute terms, commercial overrides are worsening the bias.
2. **Customer concentration**: Is the bias driven by one or two large customers? Drill down to customer_group level.
3. **New/lost business**: Is the bias explained by unforecasted new or lost distribution? Flag if new_business_revenue or lost_business_revenue > 3% of product family revenue in the period.
4. **Seasonal alignment**: Is the bias seasonal (occurs at the same horizon bucket in consecutive years)? Compare the same horizon bucket in the prior year.

### S&OP Meeting Pack Generation

The automated S&OP executive pack is generated from the following analytical components, assembled into a single Apache Superset bookmarked report exported to PDF:

1. **Cover page**: S&OP cycle month, key decisions required, pre-read summary
2. **Demand review summary**: Accuracy and bias KPIs by product family; top 5 upside and downside demand risks
3. **Supply review summary**: Supply plan attainment; top 3 supply gaps; capacity utilisation heat map (resources × months)
4. **Inventory projection**: 12-month rolling projection chart with P10/P50/P90 bands; stockout and excess flags
5. **Financial reconciliation**: Revenue waterfall (plan vs. actual); gross margin bridge; rolling 3-month revenue trend
6. **Recommended decisions**: System-generated list of decisions required, ranked by financial exposure
7. **KPI scorecard**: All 7 core KPIs vs. target, RAG-rated

---

## 12. Validations and Controls

### VC-01: Forecast Consistency Checks

| Check | Rule | Action |
|-------|------|--------|
| No negative forecasts | consensus_forecast_qty >= 0 for all periods | Floor to 0; alert Demand Planning Manager |
| Horizon continuity | No gaps in horizon_bucket sequence 1-12 | Alert IBP data feed; block projection calculation |
| Lock integrity | is_locked = 1 records have matching lock_timestamp | Flag if locked records modified after lock_timestamp |
| Reason code completeness | ABS(override%) > 10% requires override_reason_code | Reject override; return to submitter |
| Statistical model freshness | stat_forecast last model run < 7 days before demand review | Alert: stale statistical model — re-run required |

### VC-02: Supply Plan Checks

| Check | Rule | Action |
|-------|------|--------|
| Supply plan >= demand plan (M+1) | supply_plan_qty >= consensus_forecast_qty for M+1 | Flag supply gap; escalate to Supply Review |
| Capacity consistency | SUM(supply_plan_qty x time_per_unit) <= available_capacity_hrs * 1.2 (max 20% overtime) | Flag capacity overload; require supply plan revision |
| Supply plan freshness | supply_plan lock_timestamp > demand_review lock_timestamp | Reject stale supply plan; require refresh after demand lock |

### VC-03: Financial Reconciliation Controls

| Check | Rule | Action |
|-------|------|--------|
| Volume-to-value reconciliation | consensus_forecast_value within +/- 2% of plan_revenue | Flag gap; require Finance sign-off before exec meeting |
| COGS consistency | plan_gross_margin = plan_revenue - plan_cogs (check) | Reject if margin arithmetic inconsistent |
| Prior period actual locked | actual_revenue matches FI ACDOCA for closed fiscal periods | Reject if revenue source data differs from FI sub-ledger |

### VC-04: Inventory Projection Controls

| Check | Rule | Action |
|-------|------|--------|
| Opening stock anchor | Opening_stock[M+1] = Actual_closing_stock[current] | Reject projection if opening stock not anchored to confirmed actual |
| Projection continuity | No period gaps in 12-month projection | Alert if any month in horizon 1-12 is missing |
| Safety stock source | safety_stock_target sourced from current approved Safety Stock calculation run | Alert if safety stock data is > 45 days old |
| Negative projection floor | projected_closing_stock floored at 0 (cannot project negative physical stock) | Apply floor; flag product family for expedite action |

---

## 13. Required Evidence

### EV-01: For Demand Plan Accuracy Reporting
- SAP IBP locked forecast version extract (with lock_timestamp) for each S&OP cycle, retained for 24 months for retrospective accuracy measurement.
- SD billing data reconciliation confirming actual sales figures match FI revenue for the same period.
- Demand Review sign-off document (email or IBP workflow approval) confirming VP Sales approval of locked consensus forecast.

### EV-02: For Supply Plan Attainment
- SAP IBP locked supply plan version (post Supply Review gate) for each cycle.
- SAP PP production confirmation data (CO11N) for the corresponding period as the actuals source.
- Supply Review meeting minutes or IBP workflow approval from VP Operations.

### EV-03: For Financial Reconciliation
- BPC / CO-PA plan version extract with plan_revenue and plan_gross_margin reconciling to Board AOP.
- Finance Business Partner sign-off email confirming financial reconciliation is complete before Executive S&OP.
- Revenue bridge workbook showing volume, price, and mix effects signed off by CFO.

### EV-04: For S&OP Cycle Discipline KPI
- S&OP calendar with defined deadlines for each step.
- Data submission timestamps from IBP (for demand and supply plan submissions) and BPC (for financial reconciliation).
- Audit log of late submissions by function and S&OP cycle.

---

## 14. Dashboard Design

### Apache Superset Report Structure

**Page 1: S&OP Executive Summary**
- KPI scorecard: All 7 KPIs in RAG (Red/Amber/Green) card format
- Revenue plan vs. actual: Single-number card with variance $M and %
- Forecast accuracy trend: 12-month line chart (M+1, M+3, M+6 accuracy lines)
- Inventory risk heatmap: Product family × Month — Red = stockout, Orange = excess, Green = healthy
- Top 3 decisions required: Dynamic text cards generated from system logic

**Page 2: Demand Plan Accuracy and Bias**
- Accuracy trend: 24-month line chart by horizon bucket (M+1 / M+3 / M+6), overlaid with target line
- Bias waterfall: Monthly bias by product family — over/under split (stacked bar)
- Statistical vs. consensus comparison: Paired bar chart showing value-add of commercial override by family
- Bias heatmap: Product family × Month — colour intensity = magnitude of bias %
- Override reason code analysis: Treemap of override $ by reason code

**Page 3: Revenue Bridge and Financial Plan**
- Revenue waterfall: New business + Lost business + Volume + Price + Mix = Plan vs. Actual
- Gross margin bridge: Revenue effect + COGS effect + Mix effect on margin %
- Rolling 12-month revenue: Actual (bar) + Plan (line) + Prior year (dashed line)
- Financial reconciliation status: Volume plan vs. financial plan gap gauge (target < 2%)

**Page 4: Supply Plan Attainment**
- Attainment scorecard: Current month % with trend (12 months)
- Supply gap analysis: Product families where supply_gap_qty < 0 in M+1 to M+3
- Weekly demand sensing: Actual orders week-to-date vs. monthly plan — pace indicator
- Supply plan vs. consensus demand: Grouped bar chart by product family (M+1 to M+3)

**Page 5: 12-Month Inventory Projection**
- Projection chart: 12-month area chart with P10/P50/P90 bands per product family (selector)
- Stockout risk calendar: Matrix of product families × months — Red = stockout risk
- Excess inventory calendar: Matrix — Orange = excess risk with projected $ value
- Days of Supply trend: 12-month DOS projection with safety stock line and target range

**Page 6: Capacity Utilisation**
- Capacity heat map: Resource × Month — colour from Green (<80%) to Red (>100%)
- Bottleneck resource detail: Top 5 constrained resources with utilisation % and gap units
- Capacity decision timeline: Month when capacity investment is needed (based on current trajectory)
- Overtime cost projection: Estimated overtime cost for 12-month horizon

**Page 7: S&OP Cycle Discipline and Pack**
- Cycle health scorecard: Submission compliance % by function and step
- Late submission tracker: Table of late submissions with days late and function owner
- Meeting pack status: Automated readiness indicator (all data loaded? all reconciliations complete?)
- S&OP pack export button: One-click PDF generation of Executive S&OP Pack (Pages 1-6 exported as PDF)

**Filters Available Across All Pages**
- S&OP Cycle Version (current + prior 3 cycles)
- Product Family (single or multi-select)
- Business Unit / Division
- Region / Country
- Channel
- Horizon Bucket (M+1, M+3, M+6, M+12)

---

## 15. Use Cases

### UC-01: Executive S&OP Monthly Meeting
**Actor:** S&OP Process Owner, CEO, CFO, VP Sales, VP Operations
**Trigger:** Executive S&OP meeting (Week 4 of monthly cycle, typically Day 22-24)
**Process:**
1. S&OP Process Owner opens Page 7 — confirms all data is loaded and reconciliations are complete (green readiness indicator).
2. Exports S&OP Meeting Pack PDF (Page 7 export button) — one document combining all 6 pages.
3. CEO reviews Page 1 — top 3 decisions (e.g., accept capacity investment for bottleneck resource, approve demand upside, authorise excess stock markdown).
4. CFO reviews Page 3 — revenue bridge: explains $2.5M revenue shortfall as -$3.0M volume + $0.5M price.
5. VP Operations reviews Page 6 — capacity heat map: Line 3 at 98% in Month 4 requires overtime decision.
6. Decisions documented in S&OP meeting minutes with owners and deadlines.

### UC-02: Weekly Demand Sensing Review
**Actor:** Demand Planning Manager, Commercial team
**Trigger:** Every Monday morning (weekly demand sensing update)
**Process:**
1. Demand Planning Manager opens Page 4 (Supply Plan Attainment) — checks week-to-date actual orders vs. monthly plan for each product family.
2. Identifies families pacing significantly ahead of or behind plan (> 10% deviation by Week 2).
3. Opens Page 5 (Inventory Projection) — checks if demand deviation changes stockout/excess risk within the planning horizon.
4. Submits demand sensing alert to supply planning team if any product family shows a projected stockout risk within 8 weeks.
5. Commercial team reviews override reason codes for any forecast changes submitted since last week.

### UC-03: Bias Investigation
**Actor:** Demand Planning Manager
**Trigger:** Monthly — after actual sales data is loaded post-period close
**Process:**
1. Open Page 2 — filter to current period vs. prior 6 months.
2. Identify product families with Forecast_Bias > +5% for 3 consecutive months.
3. Drill into bias heatmap — identify if bias is driven by a specific region or customer group.
4. Review override reason codes for the biased family — is commercial team consistently adding volume that does not materialise?
5. Schedule bias correction workshop with the relevant commercial team.
6. Document corrective action in S&OP monthly performance review.

### UC-04: Capacity Investment Decision
**Actor:** VP Operations, Supply Chain Director, CFO
**Trigger:** S&OP cycle showing Resource X > 85% utilisation for 4+ months in horizon
**Process:**
1. Open Page 6 — identify Resource X as a bottleneck.
2. Review capacity gap in units and estimated overtime cost over the 12-month horizon.
3. Run scenario: what is the revenue at risk if capacity is not expanded? (Page 5 excess demand vs. supply plan).
4. CFO reviews financial case: capital cost of new line vs. NPV of revenue at risk.
5. Decision tabled at Executive S&OP: approve capital expenditure or commercial demand management action.

### UC-05: Month-End S&OP Performance Review
**Actor:** S&OP Process Owner
**Trigger:** End of each month, before next S&OP cycle starts
**Process:**
1. Open Page 2 — record Demand Plan Accuracy and Bias for the closing period (M+1 horizon).
2. Open Page 4 — record Supply Plan Attainment.
3. Open Page 3 — record Revenue Plan vs. Actual and financial bridge.
4. Update S&OP KPI scorecard (Page 1).
5. Prepare Continuous Improvement action log: which KPIs missed target? What is the root cause? What is the corrective action?
6. Present improvement actions at next S&OP cycle kick-off with cross-functional team.

---

## 16. Recommended Actions

### RA-01: Forecast Accuracy Improvement
- Implement statistical model benchmarking: run Holt-Winters, SES, ARIMA, and Prophet models in parallel; select best model per product family based on 12-month backtesting MAPE.
- Reduce commercial over-intervention: for families where statistical model outperforms consensus, restrict commercial overrides to > 20% changes with mandatory reason code (override only when compelling market intelligence exists).
- Segment forecast process by ABC-XYZ: apply different review intensity — A-X families reviewed weekly, C-Z families reviewed monthly.

### RA-02: Bias Elimination
- Implement automatic bias penalty: product families with > 5% bias for 2 consecutive months are flagged and their statistical baseline is given priority at the next Demand Review (commercial override requires Head of Sales sign-off).
- Separate sales targets from demand forecast: ensure the demand plan reflects expected demand, not sales ambition. Establish a separate "aspiration scenario" for bonus/incentive tracking.
- Provide bias performance scorecards to commercial managers: bias is a visible KPI in their monthly performance review.

### RA-03: Supply Plan Attainment Improvement
- Root-cause the top 3 supply plan misses each month: categorise as (a) demand signal late change, (b) production execution failure, (c) material shortage, (d) capacity failure.
- Address category (b) failures: implement SAP PP constraint-based planning to avoid uncommittable supply plans.
- Address category (c) failures: integrate supplier delivery performance data from Supplier Management module into the supply planning process.

### RA-04: Inventory Risk Management
- Implement an automated excess inventory alert: when excess_flag = 1 for any product family in the 12-month projection, automatically trigger a review with Sales for demand acceleration options and with Finance for markdown provision.
- Integrate safety stock policy with S&OP: update safety stock targets monthly as part of the planning run, reflecting changes in demand uncertainty and lead times.

### RA-05: S&OP Meeting Efficiency
- Target S&OP meeting duration: 90 minutes maximum for Executive S&OP (enabled by automated pack).
- Focus meeting on decisions, not data review: the automated pack provides pre-read data; the meeting agenda is limited to decisions and exception management.
- Implement digital decision log: capture decisions, owners, and deadlines in a structured database (linked to the S&OP dashboard for tracking).

---

## 17. Test Cases

### TC-01: Demand Plan Accuracy Calculation

**Scenario:** Product Family PF-01, M+1 horizon. Consensus forecast locked at 1,000 units. Actual sales = 950 units.

**Expected:**
- Demand_Plan_Accuracy = (1 - ABS(950 - 1000) / 950) × 100 = (1 - 50/950) × 100 = (1 - 0.0526) × 100 = 94.74%
- Forecast_Bias = (1000 - 950) / 950 × 100 = +5.26% (over-forecast)

**Test steps:**
1. Insert test records for PF-01 with consensus_forecast_qty = 1000, actual_qty = 950.
2. Run demand accuracy ETL.
3. Assert: demand_plan_accuracy = 94.74 (tolerance ±0.01), forecast_bias = 5.26 (tolerance ±0.01).

### TC-02: Revenue Bridge Decomposition

**Scenario:** Product Family PF-02, fiscal period 2026-05.
- Plan: 500 units at $200 ASP = $100,000 planned revenue
- Actual: 480 units at $210 ASP = $100,800 actual revenue

**Expected:**
- Revenue variance = $100,800 - $100,000 = +$800 (favorable, but small)
- Volume effect = (480 - 500) × $200 = -20 × $200 = -$4,000 (unfavorable volume)
- Price effect = ($210 - $200) × 480 = $10 × 480 = +$4,800 (favorable price)
- Mix effect = $800 - (-$4,000) - $4,800 = $800 + $4,000 - $4,800 = $0
- Validation: -$4,000 + $4,800 + $0 = +$800 = revenue_variance ✓

**Test steps:**
1. Insert test financial plan and actuals records.
2. Run financial bridge ETL.
3. Assert: volume_effect = -4000, price_effect = 4800, mix_effect = 0, revenue_variance = 800.

### TC-03: 12-Month Inventory Projection

**Scenario:** Product Family PF-03. Current actual closing stock = 500 units. Month M+1: supply_plan_inflow = 800 units, demand_plan_outflow = 900 units. Month M+2: supply = 900, demand = 850. Safety stock target = 200 units throughout.

**Expected M+1:**
- Opening[M+1] = 500 (actual closing)
- Projected_Closing[M+1] = 500 + 800 - 900 = 400 units
- DOS = 400 / (900 / 30) = 400 / 30 = 13.3 days
- stockout_risk_flag = 0 (400 > 200 safety stock)

**Expected M+2:**
- Opening[M+2] = 400 (from M+1 projection)
- Projected_Closing[M+2] = 400 + 900 - 850 = 450 units
- stockout_risk_flag = 0 (450 > 200)

**Test steps:**
1. Insert opening stock and supply/demand plan records.
2. Run projection ETL (ensure month-by-month sequential computation).
3. Assert all four values for M+1 and M+2 within tolerance of ±0.001 units.

### TC-04: Capacity Utilisation Calculation

**Scenario:** Resource LINE-A, Plant P001, Period 2026-07.
- Available capacity: 20 working days × 2 shifts × 8 hours × 0.85 OEE = 272 hours
- Planned load: 5,000 units of PF-A (0.04 hrs/unit) + 3,000 units of PF-B (0.03 hrs/unit) = 200 + 90 = 290 hours

**Expected:**
- capacity_utilisation_pct = 290 / 272 × 100 = 106.6%
- overtime_hrs_required = MAX(0, 290 - 272) = 18 hours
- critical_bottleneck_flag = 1 (> 100%)

**Test steps:**
1. Insert resource capacity and supply plan records.
2. Run capacity ETL.
3. Assert: capacity_utilisation_pct = 106.6 (tolerance ±0.1), overtime_hrs_required = 18.0, critical_bottleneck_flag = 1.

### TC-05: Forecast Bias — Rolling 6-Month

**Scenario:** Product Family PF-04. Last 6 months consensus vs. actual (units):
- Month 1: Plan 1000, Actual 900
- Month 2: Plan 1050, Actual 950
- Month 3: Plan 1100, Actual 1000
- Month 4: Plan 1000, Actual 880
- Month 5: Plan 1050, Actual 940
- Month 6: Plan 1100, Actual 970

**Expected 6-month rolling bias:**
- SUM(Plan - Actual) = 100 + 100 + 100 + 120 + 110 + 130 = 660
- SUM(Actual) = 900 + 950 + 1000 + 880 + 940 + 970 = 5640
- Rolling_Bias = 660 / 5640 × 100 = +11.70% (systematic over-forecast → escalation required per BR-02)

**Test steps:**
1. Insert 6 months of forecast and actual records.
2. Run rolling bias calculation.
3. Assert: rolling_bias_pct = 11.70 (tolerance ±0.01); bias alert should be triggered.

---

## 18. Risks and Mitigations

| Risk ID | Risk Description | Probability | Impact | Mitigation |
|---------|-----------------|-------------|--------|------------|
| R-01 | SAP IBP forecast extract fails during S&OP week, blocking pack generation | Medium | High | Implement daily automated extraction with email alert on failure; maintain T-1 day snapshot as fallback |
| R-02 | Actual sales data from SD module not available at period close due to billing backlog | Medium | High | Implement accrual logic using confirmed orders as proxy; reconcile within 5 days of period end |
| R-03 | S&OP process discipline low — commercial teams submit overrides without reason codes | High | Medium | Enforce in IBP workflow: system blocks submission without reason code; track override compliance as a visible KPI |
| R-04 | Financial plan and volume plan not reconciled — two versions of truth in Executive meeting | Medium | High | Gate: Apache Superset shows financial reconciliation gap status; Executive S&OP pack not marked as ready until gap < 2% |
| R-05 | Capacity data not available for third-party manufacturers — blind spots in capacity plan | Medium | Medium | Request monthly capacity confirmation from CMOs; use historical utilisation as proxy where not available; flag as estimated |
| R-06 | Safety stock targets not refreshed monthly — stale targets distort stockout/excess flags | Medium | Medium | Automate safety stock calculation trigger as part of monthly S&OP planning run; alert if safety stock data > 30 days old |
| R-07 | S&OP at product family level masks SKU-level risks — executive decision made on aggregated data may miss critical SKU constraints | High | Medium | Maintain SKU-level detail in backend; Surface top-3 SKU-level exceptions in the executive pack as supporting data |
| R-08 | Apache Superset performance degrades with 24-month rolling projection × all product families | Medium | Low | Pre-aggregate 12-month projections at product family level; use materialized SQL views for historical data; live SQL query (SQLAlchemy connection) only for current cycle |

---

## 19. Implementation Checklist

### Data Foundation
- [ ] SAP IBP OData API connection configured and tested; stg_ibp_stat_forecast and stg_ibp_consensus_forecast staging tables loaded
- [ ] SAP IBP supply plan and capacity plan extracts configured
- [ ] SAP S/4HANA SD billing data (VBRK/VBRP) extracted to stg_sd_vbrk/vbrp
- [ ] SAP S/4HANA inventory snapshots (MARD/MBEWH) configured for daily and monthly extraction
- [ ] BPC / CO-PA financial plan data extracted to stg_copa_plan
- [ ] ACDOCA / FAGLFLEXT actual financial data extraction configured
- [ ] Product family hierarchy confirmed and loaded to dim_product_family
- [ ] Resource master (production lines) loaded to dim_resource with capacity parameters
- [ ] S&OP cycle version master (dim_sop_cycle_version) created and populated for rolling 24 months

### Data Model and ETL
- [ ] All staging tables (stg_*) created with indexes and partitioning
- [ ] All conformed dimension tables (dim_*) created and populated
- [ ] fact_demand_plan ETL built and tested (including accuracy and bias calculations)
- [ ] fact_supply_plan ETL built and tested (including attainment calculation)
- [ ] fact_financial_plan ETL built (including revenue bridge decomposition — volume/price/mix)
- [ ] fact_inventory_projection ETL built (sequential 12-month rolling projection with P10/P50/P90)
- [ ] fact_capacity_utilisation ETL built (including bottleneck flag logic)
- [ ] fact_sop_cycle_kpi ETL built (aggregated KPI summary per S&OP cycle)
- [ ] Safety stock integration: safety stock targets loaded from Department 03 module

### Reporting and Dashboards
- [ ] Apache Superset semantic model created with all fact and dimension tables
- [ ] All 7 dashboard pages designed and implemented
- [ ] RAG thresholds configured for all KPI scorecards (configurable)
- [ ] S&OP pack PDF export configured (bookmarks + export automation)
- [ ] Row-level security (RLS) configured (product family by region owner)
- [ ] Scheduled refresh configured (daily 06:00 UTC; on-demand during S&OP week)
- [ ] Alerts configured (bias > 5%, stockout risk flag, critical capacity bottleneck)

### Process and Governance
- [ ] S&OP calendar configured in dim_sop_cycle_version for 12 months
- [ ] IBP submission deadlines and owners documented
- [ ] Override reason code list confirmed and loaded to IBP and PostgreSQL reference table
- [ ] Financial reconciliation tolerance (2%) confirmed with CFO
- [ ] Safety stock threshold multipliers for excess/stockout flags confirmed with Supply Planning Manager
- [ ] Capacity bottleneck thresholds (85% amber, 100% red) confirmed with VP Operations

---

## 20. Validation Checklist

### Pre-Go-Live Validation

- [ ] Demand plan accuracy (M+1) for prior 6 months calculated and manually spot-checked against spreadsheet (CSV) export-based tracking: all values within 0.5 percentage points
- [ ] Revenue bridge decomposition for 3 prior months validated against Finance manual bridge: all effects reconcile within $1,000
- [ ] 12-month inventory projection for 5 product families validated: projected closing stock for M+1 matches actual opening stock of next month (continuity check)
- [ ] Capacity utilisation for 3 production lines validated against PP CRP report in SAP for the prior month: within 2% of SAP CRP output
- [ ] Rolling 6-month forecast bias for top 10 product families manually verified against IBP key figure report
- [ ] Financial reconciliation gap (volume plan vs. financial plan) validated against Finance BP reconciliation spreadsheet
- [ ] S&OP cycle discipline tracker validated: submission timestamps match IBP audit log
- [ ] P10/P50/P90 inventory bands validated: P10 always >= P50 (lower demand = higher stock), P90 always <= P50
- [ ] All ETL pipelines complete without error for two full monthly S&OP cycles (parallel run)
- [ ] Apache Superset Executive S&OP Pack PDF export tested and confirmed readable by CFO

### Monthly Ongoing Validation (First 3 Months)

- [ ] M+1 forecast accuracy matches value previously communicated to VP Sales (no retroactive data revision)
- [ ] Revenue bridge total (volume + price + mix effects) = revenue_variance to the cent
- [ ] Inventory projection for M+1 (now closing) compared to actual: projection_accuracy_pct < 10%
- [ ] Supply plan attainment matches PP department's own production performance report
- [ ] S&OP pack generated and distributed at least 1 business day before Executive S&OP meeting date

---

## 21. Pending Information

| Item | Owner | Required By | Impact if Missing |
|------|-------|-------------|------------------|
| Confirmed SAP IBP planning levels and hierarchy mapping (product family definition) | IBP Configuration team | 2026-07-15 | Cannot populate dim_product_family; all analytics blocked |
| Production resource master (work centers with shift model and OEE factors) | VP Operations / IE team | 2026-07-15 | Cannot compute capacity utilisation |
| SAP IBP OData API credentials and endpoint URL | SAP IBP Admin | 2026-07-10 | Blocks all IBP data extraction |
| Financial plan export format from BPC (table structure, version naming) | FP&A / Finance BP | 2026-07-15 | Cannot implement financial reconciliation |
| Override reason code approved list | Demand Planning Manager | 2026-07-22 | Cannot validate IBP override submissions |
| Safety stock targets from Department 03 (confirmed data source and refresh frequency) | Demand Planning / Supply Planning | 2026-07-22 | Cannot compute stockout/excess flags in projection |
| S&OP calendar for next 12 months (cycle start dates, gate deadlines per step) | S&OP Process Owner | 2026-07-10 | Cannot populate dim_sop_cycle_version or track cycle discipline |
| Financial reconciliation tolerance confirmed by CFO | CFO / Finance Director | 2026-07-22 | Cannot implement financial gate check |
| Excess inventory multiplier threshold (currently 3.0×) confirmed by Supply Planning | Supply Planning Manager | 2026-07-22 | Cannot implement excess flag in projection |
| Apache Superset workspace provisioning and PostgreSQL connection approval | IT Security / Database Admin | 2026-07-10 | Blocks all dashboard development |

---

## 22. Implementation Roadmap

### Phase 1: Foundation (Weeks 1-4)

**Objective:** Establish data infrastructure, validate SAP IBP and S/4HANA connectivity, and populate master data.

| Week | Activities |
|------|-----------|
| 1 | SAP IBP OData API connection and authentication; SAP S/4HANA CDC configured for VBRK/VBRP and MARD/MBEWH; PostgreSQL environment provisioned |
| 2 | Staging tables created; initial data extraction for IBP forecast, SD sales actuals, inventory snapshots; data quality assessment |
| 3 | Conformed dimension tables populated: dim_product_family, dim_location, dim_resource, dim_sop_cycle_version, dim_channel, dim_date; product family hierarchy validated with IBP team |
| 4 | BPC/CO-PA financial plan extraction configured; FX rate feed operational; S&OP calendar loaded; data quality baseline report shared with S&OP Process Owner |

**Gate:** All six source systems extracting to PostgreSQL; data quality baseline established; product family hierarchy confirmed.

### Phase 2: Core Analytics (Weeks 5-10)

**Objective:** Build and validate all five core analytical models.

| Week | Activities |
|------|-----------|
| 5 | fact_demand_plan ETL: statistical forecast + consensus forecast + actual sales alignment; accuracy and bias calculations implemented |
| 6 | fact_supply_plan ETL: supply plan + actual production alignment; attainment calculation implemented; demand-supply gap logic |
| 7 | fact_financial_plan ETL: financial plan + actuals alignment; revenue bridge decomposition (volume/price/mix) implemented |
| 8 | fact_inventory_projection ETL: 12-month rolling sequential projection; P10/P50/P90 scenario bands; stockout/excess flags; safety stock integration |
| 9 | fact_capacity_utilisation ETL: resource load calculation; utilisation %; bottleneck flags; overtime computation |
| 10 | fact_sop_cycle_kpi ETL: aggregated cycle-level KPI summary; cycle discipline tracking (submission timestamps) |

**Gate:** All five fact tables populated; TC-01 through TC-05 test cases pass; parallel comparison with manual S&OP spreadsheet (CSV) tracker for prior 3 cycles.

### Phase 3: Dashboard and Reporting (Weeks 11-14)

**Objective:** Deliver Apache Superset dashboards and automate S&OP meeting pack.

| Week | Activities |
|------|-----------|
| 11 | Apache Superset semantic model built; Page 1 (Executive Summary) and Page 2 (Demand Accuracy/Bias) developed; stakeholder review with Demand Planning Manager |
| 12 | Pages 3-4 (Revenue Bridge, Supply Attainment) developed; RLS security model by region configured |
| 13 | Pages 5-7 (Inventory Projection, Capacity, S&OP Discipline) developed; PDF export automation configured; alert rules activated |
| 14 | UAT with S&OP Process Owner, VP Sales representative, VP Operations representative, Finance BP; defect resolution |

**Gate:** UAT sign-off from S&OP Process Owner and at least one VP-level stakeholder.

### Phase 4: Parallel Run and Go-Live (Weeks 15-18)

**Objective:** Run one full S&OP cycle end-to-end on the new platform alongside existing processes.

| Week | Activities |
|------|-----------|
| 15-16 | Parallel run: S&OP cycle Month 1 run on both new platform and legacy spreadsheet (CSV); all KPIs compared; discrepancies resolved |
| 17 | Executive S&OP meeting pack generated from new platform for first time (presented alongside legacy pack for comparison); executive feedback incorporated |
| 18 | Go-live decision gate; user training delivered to all S&OP participants; hypercare plan activated (dedicated support for first 3 live cycles) |

**Gate:** CEO and CFO confirm new S&OP pack is complete and accurate. S&OP Process Owner signs off go-live.

### Phase 5: Maturity and Continuous Improvement (Month 5 onwards)

- **Month 5-6**: Introduce weekly demand sensing dashboard (Page 4 weekly view); connect POS/sell-out data if available.
- **Month 6**: First quarterly S&OP maturity assessment vs. Oliver Wight Class A checklist.
- **Month 7-9**: Statistical model selection optimisation — run automated model selection per product family (SES vs. Holt-Winters vs. Prophet) based on 12-month backtesting; deploy winning model in IBP.
- **Month 9-12**: Integrate supplier capacity confirmation data from Department 02 (Supplier Management) into capacity utilisation view; extend coverage to CMOs.
- **Annual**: Full S&OP process review; KPI targets recalibrated; dashboard design updated; user satisfaction survey.

---

**Document Control**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-06-20 | S&OP Analytics Team | Initial document |
| 2.0.0 | 2026-06-22 | Senior Supply Chain Analytics Consultant | Full rewrite with 22-section analytics framework |

**References**
- Wallace, T.F. and Stahl, R.A., Sales and Operations Planning: The How-To Handbook, T.F. Wallace & Company, 2008
- Oliver Wight International, Class A Standard for Business Excellence, 6th Ed., Wiley, 2017
- Chopra, S. and Meindl, P., Supply Chain Management, 6th Ed., Pearson, 2016 — Chapters 7-9 (Demand Forecasting, Aggregate Planning)
- APICS Dictionary, 16th Ed., ASCM, 2024
- SCOR Digital Standard — PLAN process group metrics (ASCM, 2019)
- SAP IBP for S&OP Documentation — SAP Help Portal
- Hyndman, R.J. and Athanasopoulos, G., Forecasting: Principles and Practice, 3rd Ed., OTexts, 2021
