# Supply Chain Finance Analytics — Implementation Guide

**Department:** 11 — Finance & Supply Chain Controlling
**Analytics Domain:** Supply Chain Finance Analytics
**Standard:** SCOR-DS | ISO 28000:2022 | IFRS (IAS 2, IAS 7, IAS 36) | US GAAP (ASC 330)
**Version:** 2.0.0
**Date:** 2026-06-22
**Classification:** Internal — Restricted (Finance Controllers + Supply Chain Leadership)
**Systems:** SAP S/4HANA FI/CO/MM | Power BI | Azure SQL | SAP Analytics Cloud

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

Supply chain finance analytics is the discipline of translating physical goods flows — purchase orders, receipts, shipments, stock movements — into financial signals that drive working capital optimisation, cost control, and procurement governance. This implementation guide defines the complete analytical framework for the Finance & Supply Chain Controlling department, covering six core analytical domains: Purchase Price Variance (PPV), Working Capital (CCC/DIO/DSO/DPO), Inventory Valuation (FIFO vs. Moving Average), Landed Cost, 3-Way Match Exception Tracking, and Freight Cost Allocation.

The framework is built on SAP S/4HANA FI/CO/MM as the system of record, with Azure SQL as the analytical data warehouse layer and Power BI as the front-end reporting and alerting platform. The monthly close cycle drives the primary reporting cadence, with near-real-time alerting for exception conditions (invoice mismatches, PPV spikes, freight cost anomalies).

### Strategic Value

| Outcome | Baseline | Target | Financial Impact |
|---------|----------|--------|-----------------|
| PPV Unfavorable Rate | Unknown / manual | <2% of total spend | Procurement savings visibility |
| 3-Way Match Auto-Rate | 60-70% | >90% | -70% manual processing cost |
| CCC (days) | 65-80 days | <50 days | Working capital release $15-25M |
| Landed Cost Accuracy | +/-8% variance | +/-2% variance | Margin protection |
| Freight Cost % of COGS | 6-8% | <5% | 1-2% COGS reduction |
| Monthly Close Time | 8-10 days | <5 days | Faster decision cycle |

### Key Stakeholders

| Role | Primary Use | Frequency |
|------|-------------|-----------|
| CFO / VP Finance | CCC trend, working capital position, PPV summary | Monthly |
| Finance Controllers | 3-way match exceptions, month-end close pack | Weekly / Monthly |
| Chief Procurement Officer | PPV by supplier/category, landed cost variances | Monthly |
| Supply Chain Director | Inventory valuation, freight cost allocation | Monthly |
| AP / AR Managers | Exception queue, aging analysis | Daily |
| Treasury | DSO/DPO for cash flow forecasting | Weekly |

---

## 2. Analysis Objective

The primary objective of this analytics implementation is to provide Finance Controllers, Procurement leadership, and Supply Chain executives with a fully integrated, data-driven view of supply chain financial performance across six analytical domains.

### Specific Objectives

**Purchase Price Variance (PPV)**
- Quantify the financial gap between standard (budgeted) prices and actual invoiced prices at line-item level.
- Decompose PPV into three effects: price effect (pure rate change), volume effect (quantity driven), and mix effect (category/supplier shift).
- Enable root-cause routing: commodity price movement vs. supplier negotiation outcome vs. specification change.

**Working Capital Analysis**
- Track Cash Conversion Cycle (CCC) at entity, business unit, and consolidated group level with daily granularity during close and monthly trend reporting.
- Identify DIO, DSO, and DPO drivers and establish sensitivity analysis showing the impact of a 1-day improvement in each component.

**Inventory Valuation**
- Maintain dual-method valuation (FIFO and Moving Average) for parallel reporting under IFRS/US GAAP and for management reporting.
- Automate Lower of Cost or Net Realisable Value (LCNRV) write-down detection per IAS 2.

**Landed Cost Analysis**
- Compute true unit cost inclusive of all supply chain cost components: purchase price, ocean/air freight, customs duties, insurance, and last-mile handling.
- Identify hidden cost leakage in the procurement-to-receipt cycle.

**3-Way Match Exception Tracking**
- Automate matching of Purchase Order (PO), Goods Receipt (GR), and Supplier Invoice (IR) to a configurable tolerance.
- Route unmatched documents to the correct exception queue with aging and financial exposure tracking.

**Freight Cost Allocation**
- Allocate total freight spend to cost objects (product, lane, supplier, business unit) using rule-based and ML-assisted allocation logic.
- Track freight cost as a percentage of COGS and compare against budget and market benchmarks.

---

## 3. Scope

### In Scope

| Dimension | Detail |
|-----------|--------|
| Legal entities | All entities under group consolidation reporting to Group Finance |
| Geographies | All operating regions: Americas, EMEA, APAC |
| Procurement types | Direct materials, indirect spend, capital expenditure (CapEx POs) |
| Inventory methods | FIFO (IFRS/US GAAP), Moving Average (management) |
| Incoterms coverage | All 11 Incoterms 2020 rules; landed cost scope defined per Incoterm |
| Match types | 2-way (PO-Invoice), 3-way (PO-GR-Invoice), 4-way (PO-GR-QI-Invoice) |
| Freight modes | Ocean FCL/LCL, Air freight, Road FTL/LTL, Rail, Parcel/courier |
| Reporting currency | Functional currency + group consolidation currency (USD/EUR) |
| Time horizon | Rolling 24 months historical; current month in-progress |
| Close cycle | Monthly, with interim weekly flash for PPV and exceptions |

### Out of Scope

- Intercompany eliminations (handled by Group Consolidation team)
- Transfer pricing adjustments (separate TP workstream)
- Revenue recognition (Order-to-Cash module)
- Fixed asset depreciation (separate FA module)
- Tax provisioning (Tax department)

### System Boundaries

```
SAP S/4HANA (MM/FI/CO)
    |-- Purchase Orders (ME21N/ME22N)  →  Azure SQL [stg_mm_ekko, stg_mm_ekpo]
    |-- Goods Receipts (MIGO)          →  Azure SQL [stg_mm_mseg, stg_mm_mkpf]
    |-- Invoice Receipts (MIRO/FB60)   →  Azure SQL [stg_fi_rbkp, stg_fi_rseg]
    |-- Material Ledger (CKMLCR)       →  Azure SQL [stg_co_ckmlcr]
    |-- Cost Centers (KSB1)            →  Azure SQL [stg_co_cost_centers]
    |-- Freight/Conditions (EKKO/EKPO) →  Azure SQL [stg_mm_konv]

Azure SQL (Data Warehouse)
    |-- Staging tables (stg_*)
    |-- Conformed dimension tables (dim_*)
    |-- Fact tables (fact_*)
    |-- Aggregated reporting tables (rpt_*)

Power BI (Reporting Layer)
    |-- Semantic model (DirectQuery on Azure SQL)
    |-- Dashboard: Finance Supply Chain Analytics Hub
    |-- Scheduled refresh: 4x daily (06:00, 12:00, 18:00, 23:00 UTC)
    |-- Alert engine: PPV threshold, match exception aging
```

---

## 4. Business Questions

The following business questions drive the analytical requirements and dashboard design for this implementation.

**BQ-01 — PPV Root Cause**
What is the total unfavorable Purchase Price Variance this month by commodity category and supplier, and what percentage is attributable to market price movement versus negotiation outcomes versus specification changes?

**BQ-02 — Working Capital Position**
What is the current Cash Conversion Cycle in days, broken down by DIO, DSO, and DPO, and how does it compare to the same period last year and the industry benchmark of 45 days?

**BQ-03 — Inventory Valuation Gap**
What is the difference between FIFO and Moving Average inventory valuation at period end, and which SKUs have a LCNRV write-down exposure greater than $10,000?

**BQ-04 — True Landed Cost**
What is the fully loaded landed cost per unit for the top 50 purchased SKUs, and which cost component (freight, duty, insurance, handling) shows the largest adverse variance versus budget this period?

**BQ-05 — 3-Way Match Health**
What percentage of invoices this month were auto-matched within tolerance, and what is the total financial exposure ($) in the unmatched exception queue aged greater than 30 days?

**BQ-06 — Freight Cost Trend**
What is freight cost as a percentage of COGS by transportation mode (ocean, air, road) for the last 12 months, and which lanes show the highest cost-per-kg versus the contracted rate?

**BQ-07 — Supplier Payment Performance**
Which suppliers have DPO below the contracted payment terms, indicating early payment leakage, and what is the annualised value of that early payment?

**BQ-08 — PPV Forecast vs. Actual**
How does this month's PPV compare to the forecast PPV communicated during the monthly S&OP cycle, and what are the top 3 commodity categories driving the variance?

**BQ-09 — Exception Aging**
What is the average age of open 3-way match exceptions, and which AP processors / purchasing groups have the highest exception backlog measured in days and dollar value?

**BQ-10 — Inventory Days vs. Industry**
How does Days Inventory Outstanding (DIO) by product category compare to industry peers, and which categories represent the top working capital improvement opportunity?

**BQ-11 — Freight Carrier Performance**
Which freight carriers have the highest cost-per-shipment variance versus contracted rates, and what is the cumulative overcharge exposure in the current quarter?

**BQ-12 — Month-End Close Pack**
Are all financial sub-ledger reconciliations complete (AP, AR, Inventory), and what is the outstanding accruals value requiring manual posting to close the period on time?

---

## 5. Data Sources

### DS-01: SAP MM Purchase Orders

| Attribute | Detail |
|-----------|--------|
| Name | SAP MM Purchase Order Header and Line Items |
| System | SAP S/4HANA MM module |
| Tables | EKKO (header), EKPO (line items), EKET (schedule lines) |
| Azure SQL Staging | stg_mm_ekko, stg_mm_ekpo, stg_mm_eket |
| Owner | Procurement Master Data team |
| Extraction Frequency | Near-real-time via SAP CDC (Change Data Capture); full reload nightly |
| Critical Fields | EBELN (PO number), EBELP (line), MATNR (material), LIFNR (vendor), NETPR (net price), MENGE (quantity), MEINS (UOM), WERKS (plant), EKGRP (purchasing group), BSART (PO type), LOEKZ (deletion flag) |
| Primary Key | EBELN + EBELP |
| Validations | LOEKZ = '' (not deleted); BSTYP = 'F' (standard PO); NETPR > 0; MENGE > 0 |
| Known Data Errors | Legacy POs with NETPR = 0 (free-of-charge items — exclude from PPV); duplicate EBELN from system migrations — deduplicate by MAX(AEDAT) |
| Evidence Required | PO extract count reconciles to SAP ME2N report total for the period |

### DS-02: SAP MM Goods Receipts

| Attribute | Detail |
|-----------|--------|
| Name | SAP MM Material Document (Goods Receipts) |
| System | SAP S/4HANA MM module |
| Tables | MKPF (material document header), MSEG (material document line items) |
| Azure SQL Staging | stg_mm_mkpf, stg_mm_mseg |
| Owner | Warehouse / Inventory Management team |
| Extraction Frequency | Near-real-time CDC; full reload nightly |
| Critical Fields | MBLNR (material document), MJAHR (year), ZEILE (item), MATNR (material), EBELN (PO reference), EBELP (PO line reference), MENGE (GR quantity), MEINS (UOM), WERKS (plant), BWART (movement type), BUDAT (posting date), DMBTR (amount local currency) |
| Primary Key | MBLNR + MJAHR + ZEILE |
| Validations | BWART IN ('101', '102', '161', '162') for PO-based movements; BUDAT within open posting periods; MENGE > 0 for receipts |
| Known Data Errors | Backdated GRs from prior fiscal period — flag with BUDAT < period open date; reversal documents (BWART = '102') must net against original |
| Evidence Required | GR quantity sum per PO line must not exceed PO quantity (MENGE in EKPO); reconcile DMBTR to FI document BSEG |

### DS-03: SAP FI Supplier Invoices

| Attribute | Detail |
|-----------|--------|
| Name | SAP FI Invoice Receipts (Logistics Invoice Verification) |
| System | SAP S/4HANA FI/MM module |
| Tables | RBKP (invoice header), RSEG (invoice line items), BKPF (FI document header), BSEG (FI document line items) |
| Azure SQL Staging | stg_fi_rbkp, stg_fi_rseg, stg_fi_bkpf, stg_fi_bseg |
| Owner | Accounts Payable team |
| Extraction Frequency | Near-real-time CDC; full reload nightly |
| Critical Fields | BELNR (invoice document), GJAHR (fiscal year), BUZEI (line), LIFNR (vendor), MATNR (material), EBELN (PO), EBELP (PO line), MENGE (invoiced quantity), MEINS (UOM), WRBTR (gross amount), WAERS (currency), ZFBDT (baseline date), ZBD1T (payment terms days), RBSTAT (invoice status) |
| Primary Key | BELNR + GJAHR + BUZEI |
| Validations | RBSTAT NOT IN ('A', 'S') to exclude cancelled/storno; currency conversion applied for non-functional currency invoices; duplicate invoice check on LIFNR + XBLNR (vendor invoice number) + WRBTR |
| Known Data Errors | Credit memos with negative WRBTR — handle separately in match logic; invoices without PO reference (non-PO invoices) — route to separate non-PO spend report |
| Evidence Required | Sum of WRBTR by posting period must reconcile to AP sub-ledger trial balance in FAGLFLEXT |

### DS-04: SAP CO Material Ledger

| Attribute | Detail |
|-----------|--------|
| Name | SAP CO-PC Material Ledger (Actual Costing) |
| System | SAP S/4HANA CO-PC module |
| Tables | CKMLCR (material ledger header), CKMVFM (material ledger movements), MBEWH (material valuation history) |
| Azure SQL Staging | stg_co_ckmlcr, stg_co_ckmvfm, stg_co_mbewh |
| Owner | Controlling / Cost Accounting team |
| Extraction Frequency | Monthly (period close trigger) + interim snapshot on demand |
| Critical Fields | MATNR (material), BWKEY (valuation area), PEINH (price unit), STPRS (standard price), VERPR (moving average price), LBKUM (total valuated stock), SALK3 (total stock value), VPRSV (price control indicator: S=standard, V=moving average), LFGJA (fiscal year), LFMON (period) |
| Primary Key | MATNR + BWKEY + LFGJA + LFMON |
| Validations | LBKUM >= 0 (no negative valuation stock); SALK3 / LBKUM = VERPR (unit price consistency check); VPRSV must be consistent with material type configuration |
| Known Data Errors | Materials with split valuation (batch-level) require aggregation across BWTAR; price control changes mid-period require restatement logic |
| Evidence Required | SALK3 sum by plant must reconcile to FI inventory balance sheet account (GL account 300000-399999 range) |

### DS-05: SAP MM Condition Records (Freight / Pricing Conditions)

| Attribute | Detail |
|-----------|--------|
| Name | SAP MM Pricing Conditions (Freight and Surcharges) |
| System | SAP S/4HANA MM module |
| Tables | KONV (conditions per document), KONP (condition item), T685T (condition types) |
| Azure SQL Staging | stg_mm_konv, stg_mm_konp |
| Owner | Procurement / Logistics Controlling team |
| Extraction Frequency | Daily delta extraction |
| Critical Fields | KNUMV (condition document number), KPOSN (condition item), KAPPL (application: M=purchasing), KSCHL (condition type: FRB1=freight, ZFR1=custom freight), KWERT (condition value in document currency), WAERS (currency), KBETR (condition rate), KMEIN (condition UOM), EBELN (PO reference via EKKO.KNUMV) |
| Primary Key | KNUMV + KPOSN + KSCHL |
| Validations | KAPPL = 'M' (purchasing application only); KWERT != 0; condition type in approved freight condition type list (FRB1, FRB2, ZFR1, ZFR2, ZIN1, ZHD1) |
| Known Data Errors | Freight conditions sometimes booked as header conditions (KPOSN = 0) — allocate to lines by quantity weight; missing freight conditions for legacy POs created before condition type activation |
| Evidence Required | Total KWERT for freight conditions reconciles to freight cost GL accounts (e.g., GL 520000-529999) in KSB1 cost center report |

### DS-06: Logistics / Freight Invoices (External TMS or Forwarder Portal)

| Attribute | Detail |
|-----------|--------|
| Name | Freight Carrier and Forwarder Invoice Data |
| System | External TMS (e.g., SAP TM, Blue Yonder, Transplace) or manual upload |
| Tables | Azure SQL: stg_freight_invoices, stg_freight_shipment_lines |
| Owner | Logistics Controlling / Transport Management team |
| Extraction Frequency | Daily file-based upload (EDI 210 / EDIFACT INVOIC) or API pull |
| Critical Fields | freight_invoice_id, carrier_id, shipment_id, origin_port, destination_port, transport_mode, weight_kg, volume_cbm, contracted_rate_usd, actual_rate_usd, surcharge_type, surcharge_amount_usd, invoice_date, payment_due_date, po_reference |
| Primary Key | freight_invoice_id |
| Validations | actual_rate_usd > 0; weight_kg > 0; transport_mode IN ('OCEAN_FCL', 'OCEAN_LCL', 'AIR', 'ROAD_FTL', 'ROAD_LTL', 'RAIL', 'PARCEL'); carrier_id exists in carrier master; po_reference linkable to SAP PO |
| Known Data Errors | Surcharge codes not standardised across carriers — requires carrier-specific mapping table; shipment split across multiple invoices requiring consolidation by shipment_id |
| Evidence Required | Total freight spend per carrier per month reconciles to AP invoice postings for freight vendor accounts |

---

## 6. Data Model

### Conceptual Entity Relationship

```
dim_material ─────────────────────────────────────────────────┐
dim_vendor ───────────────────────────────────────────────────┤
dim_plant ────────────────────────────────────────────────────┤
dim_purchasing_group ─────────────────────────────────────────┤
dim_date ─────────────────────────────────────────────────────┤
                                                               │
fact_po_line ──────────────────────────────────────────────►  │
    (EBELN, EBELP, MATNR, LIFNR, WERKS, EKGRP,               │
     standard_price, po_price, po_quantity,                    │
     ordered_value, posting_date)                              │
        │                                                      │
        ▼                                                      │
fact_goods_receipt ──────────────────────────────────────────►│
    (MBLNR, MJAHR, ZEILE, EBELN, EBELP, MATNR,               │
     gr_quantity, gr_value, posting_date, movement_type)       │
        │                                                      │
        ▼                                                      │
fact_invoice_receipt ────────────────────────────────────────►│
    (BELNR, GJAHR, BUZEI, EBELN, EBELP, LIFNR, MATNR,        │
     invoiced_quantity, invoiced_value, currency,              │
     baseline_date, payment_terms_days, status)                │
        │                                                      │
        ▼                                                      │
fact_three_way_match ─────────────────────────────────────────┘
    (match_id, EBELN, EBELP, MATNR, LIFNR,
     po_quantity, gr_quantity, ir_quantity,
     po_value, gr_value, ir_value,
     qty_variance, price_variance,
     match_status, exception_type, aging_days)

fact_ppv ──── (po_line FK, material FK, vendor FK, period FK,
               standard_price, actual_price, quantity,
               ppv_amount, ppv_pct, price_effect,
               volume_effect, mix_effect, ppv_category)

fact_inventory_valuation ──── (material FK, plant FK, period FK,
                                fifo_value, moving_avg_value,
                                standard_value, lcnrv_nrv,
                                write_down_required, write_down_amount)

fact_landed_cost ──── (po_line FK, material FK, vendor FK, period FK,
                        unit_purchase_price, freight_unit,
                        customs_duty_unit, insurance_unit,
                        handling_unit, total_landed_cost,
                        budget_landed_cost, variance_amount)

fact_freight_cost ──── (freight_invoice FK, shipment FK, carrier FK,
                         material FK, lane FK, period FK,
                         contracted_rate, actual_rate, surcharge_total,
                         weight_kg, cost_per_kg, freight_pct_cogs)

fact_working_capital ──── (entity FK, period FK,
                            avg_inventory, avg_ar, avg_ap,
                            cogs, revenue,
                            dio, dso, dpo, ccc,
                            working_capital_value)
```

### Star Schema Design (Azure SQL)

The data model follows a Kimball-style star schema with conformed dimensions shared across all fact tables. Each fact table is partitioned by fiscal_year_period (YYYYMM) for query performance.

```sql
-- Conformed Dimensions
dim_date           -- Calendar + fiscal calendar (SAP fiscal year variant K4)
dim_material       -- Material master (MARA + MARC + MAKT)
dim_vendor         -- Vendor master (LFA1 + LFB1 + LFM1)
dim_plant          -- Plant + storage location (T001W + T001L)
dim_purchasing_group -- Purchasing group master (T024)
dim_cost_center    -- CO cost centers (CSKS)
dim_gl_account     -- GL account master (SKA1 + SKAT)
dim_carrier        -- Freight carrier master (from TMS)
dim_incoterm       -- Incoterms 2020 (11 rules + risk transfer point)
```

---

## 7. Data Dictionary

### DD-01: fact_ppv

| Attribute | Detail |
|-----------|--------|
| Name | fact_ppv |
| Granularity | One row per PO line item per fiscal period |
| Primary Key | ppv_id (surrogate), natural key: EBELN + EBELP + fiscal_period |
| Relationships | FK to dim_material (MATNR), dim_vendor (LIFNR), dim_plant (WERKS), dim_date (fiscal_period), dim_purchasing_group (EKGRP) |

**Fields:**

| Field Name | Type | Description |
|------------|------|-------------|
| ppv_id | BIGINT | Surrogate primary key |
| ebeln | NVARCHAR(10) | SAP Purchase Order number |
| ebelp | NVARCHAR(5) | PO line item number |
| fiscal_period | CHAR(6) | Fiscal year + period (YYYYMM) |
| matnr | NVARCHAR(18) | Material number |
| lifnr | NVARCHAR(10) | Vendor account number |
| werks | NVARCHAR(4) | Plant code |
| ekgrp | NVARCHAR(3) | Purchasing group |
| standard_price | DECIMAL(18,4) | Standard cost price per UOM from material ledger (STPRS) |
| actual_price | DECIMAL(18,4) | Actual invoiced price per UOM from LIV (IR unit price) |
| po_price | DECIMAL(18,4) | Contracted PO price per UOM (NETPR/PEINH from EKPO) |
| quantity_purchased | DECIMAL(18,3) | Quantity received and invoiced in the period |
| uom | NVARCHAR(3) | Unit of measure (GS1 UOM code) |
| ppv_amount_lc | DECIMAL(18,2) | PPV in local currency: (standard_price - actual_price) x quantity |
| ppv_amount_gc | DECIMAL(18,2) | PPV in group consolidation currency (USD) |
| ppv_pct | DECIMAL(10,4) | PPV as % of standard price |
| price_effect | DECIMAL(18,2) | Pure price change effect vs. prior period |
| volume_effect | DECIMAL(18,2) | Volume-driven PPV change vs. prior period |
| mix_effect | DECIMAL(18,2) | Category/supplier mix shift effect |
| ppv_category | NVARCHAR(50) | Classification: COMMODITY_PRICE / NEGOTIATION / SPEC_CHANGE / FX / OTHER |
| is_favorable | BIT | 1 = favorable (paid less than standard), 0 = unfavorable |
| etl_load_datetime | DATETIME2 | ETL load timestamp (UTC) |

**Transformations:** standard_price sourced from dim_material.standard_price at period start snapshot; actual_price = RSEG.WRBTR / RSEG.MENGE (invoice value / invoiced quantity); FX conversion applied using ECB rate at invoice posting date.

**Cleaning:** Exclude POs with NETPR = 0 (free-of-charge); exclude internal STO (stock transport orders) where BSART IN ('UB', 'NB' with internal supplying plant).

**Validations:** ppv_amount_lc + price_effect + volume_effect + mix_effect = 0 (decomposition must sum to zero); ABS(ppv_pct) < 50% — flag records > 50% for data quality review.

---

### DD-02: fact_three_way_match

| Attribute | Detail |
|-----------|--------|
| Name | fact_three_way_match |
| Granularity | One row per PO line item with match status per invoice |
| Primary Key | match_id (surrogate) |
| Relationships | FK to dim_material, dim_vendor, dim_plant, dim_date, fact_po_line, fact_goods_receipt, fact_invoice_receipt |

**Fields:**

| Field Name | Type | Description |
|------------|------|-------------|
| match_id | BIGINT | Surrogate primary key |
| ebeln | NVARCHAR(10) | Purchase Order number |
| ebelp | NVARCHAR(5) | PO line item |
| belnr_ir | NVARCHAR(10) | Invoice document number |
| gjahr_ir | NVARCHAR(4) | Invoice fiscal year |
| match_type | NVARCHAR(10) | '2WAY', '3WAY', '4WAY' |
| po_quantity | DECIMAL(18,3) | Quantity on PO line |
| gr_quantity | DECIMAL(18,3) | Total GR quantity posted |
| ir_quantity | DECIMAL(18,3) | Total invoiced quantity |
| po_value_lc | DECIMAL(18,2) | PO line value (local currency) |
| gr_value_lc | DECIMAL(18,2) | GR posted value (local currency) |
| ir_value_lc | DECIMAL(18,2) | Invoice value (local currency) |
| qty_variance_pct | DECIMAL(10,4) | (ir_quantity - gr_quantity) / gr_quantity x 100 |
| price_variance_pct | DECIMAL(10,4) | (ir_value/ir_quantity - po_value/po_quantity) / (po_value/po_quantity) x 100 |
| match_status | NVARCHAR(20) | MATCHED / PRICE_EXCEPTION / QTY_EXCEPTION / MISSING_GR / DUPLICATE / BLOCKED |
| exception_type | NVARCHAR(50) | Specific exception code for routing |
| exception_owner | NVARCHAR(50) | AP processor or purchasing group responsible |
| created_date | DATE | Date exception was first identified |
| aging_days | INT | Calendar days since created_date |
| financial_exposure_lc | DECIMAL(18,2) | Unresolved financial exposure |
| is_resolved | BIT | 1 = resolved, 0 = open |
| resolution_date | DATE | Date exception was resolved |
| etl_load_datetime | DATETIME2 | ETL load timestamp (UTC) |

---

### DD-03: fact_landed_cost

| Attribute | Detail |
|-----------|--------|
| Name | fact_landed_cost |
| Granularity | One row per PO line item per shipment |
| Primary Key | landed_cost_id (surrogate) |
| Relationships | FK to dim_material, dim_vendor, dim_plant, dim_incoterm, dim_date |

**Fields:**

| Field Name | Type | Description |
|------------|------|-------------|
| landed_cost_id | BIGINT | Surrogate primary key |
| ebeln | NVARCHAR(10) | Purchase Order number |
| ebelp | NVARCHAR(5) | PO line item |
| shipment_id | NVARCHAR(20) | Logistics shipment reference |
| incoterm_code | NVARCHAR(3) | Incoterms 2020 rule (EXW, FCA, CPT, CIP, DAP, DPU, DDP, FAS, FOB, CFR, CIF) |
| unit_purchase_price | DECIMAL(18,4) | Net purchase price per unit (from EKPO.NETPR) |
| freight_unit | DECIMAL(18,4) | Allocated freight cost per unit |
| customs_duty_unit | DECIMAL(18,4) | Customs duty per unit (ad valorem or specific) |
| insurance_unit | DECIMAL(18,4) | Marine/cargo insurance per unit |
| handling_unit | DECIMAL(18,4) | Port handling + last-mile cost per unit |
| other_costs_unit | DECIMAL(18,4) | Demurrage, inspection fees, other supply chain costs |
| total_landed_cost | DECIMAL(18,4) | Sum of all components per unit |
| budget_landed_cost | DECIMAL(18,4) | Budgeted landed cost from annual plan |
| variance_amount | DECIMAL(18,4) | total_landed_cost - budget_landed_cost |
| variance_pct | DECIMAL(10,4) | variance_amount / budget_landed_cost x 100 |
| quantity | DECIMAL(18,3) | Quantity received |
| total_landed_value | DECIMAL(18,2) | total_landed_cost x quantity |
| currency | NVARCHAR(3) | ISO 4217 currency code |
| etl_load_datetime | DATETIME2 | ETL load timestamp (UTC) |

---

### DD-04: fact_working_capital

| Attribute | Detail |
|-----------|--------|
| Name | fact_working_capital |
| Granularity | One row per legal entity per fiscal period |
| Primary Key | wc_id (surrogate), natural key: entity_id + fiscal_period |

**Fields:**

| Field Name | Type | Description |
|------------|------|-------------|
| wc_id | BIGINT | Surrogate primary key |
| entity_id | NVARCHAR(4) | SAP company code |
| fiscal_period | CHAR(6) | YYYYMM |
| avg_inventory_lc | DECIMAL(18,2) | Average of opening + closing inventory value (local currency) |
| avg_ar_lc | DECIMAL(18,2) | Average accounts receivable balance |
| avg_ap_lc | DECIMAL(18,2) | Average accounts payable balance |
| cogs_period_lc | DECIMAL(18,2) | Cost of goods sold for the period |
| revenue_period_lc | DECIMAL(18,2) | Net revenue for the period |
| dio | DECIMAL(10,2) | Days Inventory Outstanding |
| dso | DECIMAL(10,2) | Days Sales Outstanding |
| dpo | DECIMAL(10,2) | Days Payables Outstanding |
| ccc | DECIMAL(10,2) | Cash Conversion Cycle = DIO + DSO - DPO |
| working_capital_lc | DECIMAL(18,2) | Inventory + AR - AP |
| working_capital_gc | DECIMAL(18,2) | Working capital in group currency (USD) |
| etl_load_datetime | DATETIME2 | ETL load timestamp (UTC) |

---

## 8. Transformation Rules

### TR-01: Standard Price Determination

The standard price for PPV calculation is sourced from the SAP Material Ledger period opening standard price (CKMLCR.STPRS), NOT the current material master price. This ensures the variance is calculated against the price in effect at the start of the reporting period.

```sql
-- Rule: Standard price at period start
SELECT
    matnr,
    bwkey,
    lfgja,
    lfmon,
    stprs / peinh AS standard_price_per_uom
FROM stg_co_ckmlcr
WHERE lfgja = :fiscal_year
  AND lfmon = :fiscal_period_start
  AND vprsv = 'S'  -- Standard price indicator
```

### TR-02: PPV Calculation

```sql
-- PPV Amount (positive = favorable, negative = unfavorable)
ppv_amount = (standard_price - actual_price) * quantity_received

-- Actual price derived from invoice
actual_price = ir.wrbtr / NULLIF(ir.menge, 0)  -- Invoice value / invoiced quantity

-- PPV % relative to standard
ppv_pct = (standard_price - actual_price) / NULLIF(standard_price, 0) * 100
```

### TR-03: Three-Way Match Tolerance Logic

```sql
-- Price tolerance: default +/- 2% or $50 absolute (whichever is greater)
price_variance_pct = ABS((ir_unit_price - po_unit_price) / NULLIF(po_unit_price, 0) * 100)
price_tolerance_met = CASE
    WHEN price_variance_pct <= 2.0 THEN 1
    WHEN ABS(ir_unit_price - po_unit_price) * ir_quantity <= 50.0 THEN 1
    ELSE 0
END

-- Quantity tolerance: default +/- 5%
qty_variance_pct = ABS((ir_quantity - gr_quantity) / NULLIF(gr_quantity, 0) * 100)
qty_tolerance_met = CASE WHEN qty_variance_pct <= 5.0 THEN 1 ELSE 0 END

-- Match status determination
match_status = CASE
    WHEN gr_quantity IS NULL OR gr_quantity = 0 THEN 'MISSING_GR'
    WHEN price_tolerance_met = 1 AND qty_tolerance_met = 1 THEN 'MATCHED'
    WHEN price_tolerance_met = 0 AND qty_tolerance_met = 1 THEN 'PRICE_EXCEPTION'
    WHEN price_tolerance_met = 1 AND qty_tolerance_met = 0 THEN 'QTY_EXCEPTION'
    ELSE 'PRICE_QTY_EXCEPTION'
END
```

### TR-04: Landed Cost Allocation Rules

Freight and ancillary costs are allocated to PO line items using the following hierarchy:

1. **Direct assignment**: If the freight invoice references a specific PO line (po_reference + line), assign 100% to that line.
2. **Weight-based allocation**: If freight covers multiple lines in a shipment, allocate proportionally by net weight (EKPO.NTGEW x EKPO.MENGE).
3. **Value-based allocation (fallback)**: If weight is unavailable, allocate proportionally by PO line value (NETPR x MENGE).

```sql
-- Weight-based freight allocation
freight_per_line = total_freight_cost * (line_weight / shipment_total_weight)

-- Per-unit freight
freight_unit = freight_per_line / NULLIF(gr_quantity, 0)
```

### TR-05: Customs Duty Calculation

```sql
-- Ad valorem duty
customs_duty_unit = unit_purchase_price * tariff_rate_pct / 100

-- Add customs value uplift (CIF basis for EU/UK imports):
-- Customs value = Invoice value + freight to port of entry + insurance
customs_value_unit = unit_purchase_price + freight_to_port_unit + insurance_unit
customs_duty_unit_cif = customs_value_unit * tariff_rate_pct / 100
```

### TR-06: Working Capital Calculation

```sql
-- DIO: Average inventory / COGS * 365
dio = (avg_inventory_lc / NULLIF(cogs_period_lc * 12, 0)) * 365
-- Note: cogs_period_lc is monthly; annualise by multiplying by 12

-- DSO: Average AR / Revenue * 365
dso = (avg_ar_lc / NULLIF(revenue_period_lc * 12, 0)) * 365

-- DPO: Average AP / COGS * 365
dpo = (avg_ap_lc / NULLIF(cogs_period_lc * 12, 0)) * 365

-- CCC
ccc = dio + dso - dpo
```

### TR-07: FIFO vs. Moving Average Valuation Gap

```sql
-- Moving average (from material ledger)
moving_avg_value = ckmlcr.verpr * ckmlcr.lbkum

-- FIFO value (computed via lot-level FIFO layer — requires stock aging)
-- Layer logic: consume oldest lots first at their receipt price
fifo_value = SUM(lot_quantity * lot_receipt_price)  -- from stg_inventory_lots

-- Valuation gap
valuation_gap = fifo_value - moving_avg_value

-- LCNRV write-down check (IAS 2.9)
lcnrv_adjustment = CASE
    WHEN MIN(nrv_per_unit) < COALESCE(standard_price, moving_avg_price) * quantity
    THEN (standard_price - MIN(nrv_per_unit)) * quantity
    ELSE 0
END
```

---

## 9. Business Rules

### BR-01: PPV Classification
PPV must be classified into one of five categories for root-cause analysis. Classification logic uses the following hierarchy:
- If ABS(commodity_index_change_pct) > ABS(ppv_pct) * 0.5: COMMODITY_PRICE
- Else if vendor_negotiation_event_flag = 1 in the period: NEGOTIATION
- Else if spec_change_flag = 1 (engineering change order linked): SPEC_CHANGE
- Else if ABS(fx_impact_pct) > 1.0% and po_currency != functional_currency: FX
- Else: OTHER

### BR-02: 3-Way Match Tolerance Configuration
Tolerances are configurable by vendor category and material type. Default tolerances:
- Standard materials: Price +/-2%, Quantity +/-5%
- Precious metals / commodities: Price +/-5% (high market volatility)
- Services: Quantity tolerance not applicable (not GR-based)
- Minimum absolute tolerance: $50 per invoice line (prevents micro-exception noise)

### BR-03: Exception Escalation
Open 3-way match exceptions are escalated based on age and financial exposure:
- Age > 15 days AND exposure > $1,000: Alert to AP Supervisor
- Age > 30 days AND exposure > $5,000: Escalate to Finance Controller
- Age > 45 days AND exposure > $10,000: Escalate to CFO / Controller Director
- Age > 60 days (any amount): Flag for period-end accrual consideration

### BR-04: LCNRV Write-Down Trigger
A Lower of Cost or Net Realisable Value (LCNRV) write-down must be recorded when:
- NRV (latest selling price - estimated cost to complete and sell) < Carrying cost
- Threshold for mandatory write-down: NRV < Cost * 0.95 (5% buffer per company policy)
- Materials with REACH SVHC flag and no confirmed sales orders: NRV = 0 if disposal required

### BR-05: Freight Cost Allocation Mandatory Fields
Freight invoices must have a valid shipment reference (shipment_id) before allocation. Freight invoices without shipment reference (orphan freight) are accrued to a freight-in-transit suspense account and reviewed weekly.

### BR-06: Currency Conversion
All financial amounts are converted to the group reporting currency (USD) using the ECB/FRB exchange rate on the invoice posting date. Month-end balance sheet items (inventory, AR, AP) use the period closing rate. P&L items (PPV, freight) use the average rate for the period.

### BR-07: Soft-Delete and Audit
All cancelled or reversed documents retain their records in the data warehouse with a is_cancelled flag. PPV and working capital calculations net out reversals. Exception records are never hard-deleted — resolved exceptions retain resolution_date and resolution_reason.

---

## 10. KPIs and Formulas

### KPI-01: Purchase Price Variance (PPV)

```
PPV_Amount = (Standard_Price - Actual_Price) × Quantity_Purchased
```
- Positive = FAVORABLE (company paid less than standard)
- Negative = UNFAVORABLE (company paid more than standard)
- Standard: Annual budgeted standard cost (from SAP CK11N standard cost estimate)
- Actual: Effective price per unit from supplier invoice (LIV posting)

```
PPV_Pct = (Standard_Price - Actual_Price) / Standard_Price × 100
```
- Target: PPV% within +/- 2% for managed spend categories
- Alert threshold: PPV% < -5% (unfavorable) for any category > $100K spend

**PPV Decomposition:**
```
Total PPV Change vs. Prior Period =
    Price Effect  +  Volume Effect  +  Mix Effect

Price Effect = (Current_Price - Prior_Price) × Current_Quantity
Volume Effect = (Current_Quantity - Prior_Quantity) × Prior_Price
Mix Effect = Total_PPV - Price_Effect - Volume_Effect
```

### KPI-02: Cash Conversion Cycle (CCC)

```
CCC = DIO + DSO - DPO

DIO = (Average_Inventory_Value / COGS) × 365
DSO = (Average_Accounts_Receivable / Revenue) × 365
DPO = (Average_Accounts_Payable / COGS) × 365
```
- Average = (Opening Balance + Closing Balance) / 2
- COGS and Revenue annualised from monthly figures
- World-class CCC target: < 35 days (retail), < 50 days (manufacturing), < 60 days (complex industrial)
- 1-day CCC improvement = Working Capital Release = Annual_COGS / 365

### KPI-03: Working Capital Value

```
Working_Capital = Inventory_Value + Accounts_Receivable - Accounts_Payable
Working_Capital_as_Pct_Revenue = Working_Capital / Annual_Revenue × 100
```
- Target: Working Capital % Revenue < 15% for efficient operations

### KPI-04: Landed Cost per Unit

```
Landed_Cost_Unit = Unit_Purchase_Price
                 + Freight_per_Unit
                 + Customs_Duty_per_Unit
                 + Insurance_per_Unit
                 + Handling_per_Unit
                 + Other_Supply_Chain_Costs_per_Unit

Landed_Cost_vs_Budget_Pct = (Landed_Cost - Budget_Landed_Cost) / Budget_Landed_Cost × 100
```
- Freight share of landed cost target: < 8% for ocean, < 15% for air
- Customs duty as % of landed cost varies by HS code and trade lane

### KPI-05: 3-Way Match Metrics

```
Auto_Match_Rate = Auto_Matched_Invoices / Total_Invoices × 100
Exception_Rate = Exception_Invoices / Total_Invoices × 100
Exception_Exposure = SUM(ABS(ir_value - po_value)) for all open exceptions

Target: Auto_Match_Rate > 90%
Alert: Exception_Rate > 10% or Exposure > $500,000
```

### KPI-06: Freight Cost Metrics

```
Freight_Cost_Pct_COGS = Total_Freight_Cost / COGS × 100
Target: < 5% of COGS

Freight_Cost_per_Kg = Total_Freight_Cost / Total_Weight_Kg (by mode/lane)
Carrier_Rate_Variance = (Actual_Rate - Contracted_Rate) / Contracted_Rate × 100
```

### KPI-07: Inventory Valuation Metrics

```
FIFO_vs_MovAvg_Gap = FIFO_Inventory_Value - Moving_Avg_Inventory_Value
FIFO_vs_MovAvg_Gap_Pct = Gap / Moving_Avg_Inventory_Value × 100

LCNRV_Exposure = SUM(MAX(0, Carrying_Cost - NRV)) for all materials
Write_Down_Rate = LCNRV_Write_Downs / Total_Inventory_Value × 100
```

---

## 11. Analytical Logic

### PPV Decomposition Analysis

PPV analysis follows a three-level decomposition to move from "what happened" to "why it happened":

**Level 1 — Aggregate PPV**
Total PPV for the period vs. prior period and vs. budget. Split by favorable/unfavorable.

**Level 2 — Category and Supplier Drill-Down**
PPV decomposed by: Commodity category (L1/L2/L3 from material group hierarchy), Supplier (top 20 by spend), Purchasing group, Plant/region.

**Level 3 — Effect Decomposition**
For each category or supplier, the change in PPV vs. prior period is split into:
- **Price Effect**: How much of the change is due to the actual price changing? `Price_Effect = (P_current - P_prior) × Q_current`
- **Volume Effect**: How much is due to buying more or less? `Volume_Effect = (Q_current - Q_prior) × P_prior`
- **Mix Effect**: How much is due to shifting between materials or suppliers within the category? `Mix_Effect = Total_PPV_Change - Price_Effect - Volume_Effect`

This decomposition enables the Procurement team to isolate whether an unfavorable PPV is driven by commodity market moves (external, limited control) versus negotiation outcomes (internal, controllable).

### Cash Conversion Cycle Trend Analysis

CCC is tracked with 24-month rolling trend. Sensitivity analysis quantifies the working capital cash impact of improving each component by 1 day:
```
1-Day DIO Improvement = COGS / 365 (inventory cash release)
1-Day DSO Improvement = Revenue / 365 (AR cash collection)
1-Day DPO Improvement = COGS / 365 (AP cash outflow — negative impact)
```

Waterfall chart shows CCC bridge: Prior Month → DIO change → DSO change → DPO change → Current Month CCC.

### Landed Cost Waterfall

For each SKU or supplier, a waterfall chart breaks down the total landed cost per unit:
```
Base Price (EXW/FOB)
  + Origin Handling (loading, inland freight to port of export)
  + Ocean/Air Freight
  + Port Charges (destination)
  + Customs Duty
  + Insurance
  + Last-Mile Delivery
  = Total Landed Cost
```
Variance vs. budget waterfall shows which component drove the landed cost overrun. Components sourced from: EKPO (base price), KONV (freight/insurance conditions), customs declaration data (duty), logistics actual costs.

### 3-Way Match Exception Routing

```
Exception received
    │
    ├─ MISSING_GR → Route to Warehouse team (GR confirmation required)
    ├─ PRICE_EXCEPTION → Route to Purchasing (PO amendment or invoice dispute)
    ├─ QTY_EXCEPTION → Route to AP + Warehouse (quantity reconciliation)
    ├─ DUPLICATE → Route to AP (hold payment, investigate duplicate)
    └─ BLOCKED → Route to QM team (goods blocked for quality inspection)
```

Each exception displays: PO number, supplier, material, dollar exposure, age in days, assigned owner, last action taken, SLA status (Green < 15 days, Amber 15-30 days, Red > 30 days).

### Freight Cost Allocation Logic

1. **Direct match**: Freight invoice line directly references PO → 1:1 allocation.
2. **Shipment consolidation**: Multiple POs on one shipment → allocate by net weight (primary), then by value (fallback).
3. **Period accrual**: Freight invoices received after period close but relating to goods receipted in the period → accrue based on contracted rate × weight.
4. **Mode comparison**: For each lane, compare actual vs. contracted rate by carrier. Flag overcharges > 2% for dispute resolution.

---

## 12. Validations and Controls

### VC-01: PPV Control Checks

| Check | Rule | Action |
|-------|------|--------|
| Price reasonableness | ABS(ppv_pct) < 50% | Flag for manual review; exclude from automated reports |
| Standard price exists | standard_price > 0 for all active materials | Block PPV calculation; alert master data team |
| No double-counting | One PPV record per IR document line per period | Deduplication query in ETL |
| FX rate availability | Exchange rate exists for all invoice currencies | Fallback to prior day rate; alert FX data feed team |
| Period alignment | PPV posting period = IR posting period | Reject records with cross-period posting |

### VC-02: 3-Way Match Control Checks

| Check | Rule | Action |
|-------|------|--------|
| No unmatched blocking | Invoices in BLOCKED status < 5% of total | Alert AP Manager; escalate if > 7 days |
| Duplicate invoice prevention | LIFNR + XBLNR + WRBTR unique per period | Reject duplicate; send to AP for investigation |
| GR date before IR date | MKPF.BUDAT <= RBKP.BLDAT | Flag IR posted before GR (3-way match violation) |
| Quantity over-invoicing | ir_quantity <= po_quantity + GR_tolerance | Block payment; escalate to AP Supervisor |
| Currency match | IR currency = PO currency | Reject; require currency amendment |

### VC-03: Working Capital Checks

| Check | Rule | Action |
|-------|------|--------|
| Balance sheet reconciliation | avg_inventory = (GL inventory balance opening + closing) / 2 | Reject if variance > $1,000 |
| AR/AP sub-ledger tie | avg_ar matches AR aging report; avg_ap matches AP aging report | Alert if variance > $5,000 |
| DIO/DSO/DPO reasonableness | DIO < 365; DSO < 180; DPO < 180 | Flag outliers; investigate balance sheet anomalies |
| Negative working capital alert | working_capital < 0 | Immediate alert to CFO; treasury notification |

### VC-04: Period Close Readiness Gates

Before the monthly period close report is published:
1. All 3-way match exceptions aged > 45 days must have a resolution note or accrual posted.
2. FIFO vs. Moving Average gap reconciliation must be signed off by Cost Accounting.
3. LCNRV review completed and write-downs approved by Finance Director.
4. Freight accruals posted for all GRs without freight invoice as of period close.
5. PPV report reviewed and signed off by CPO and Finance Controller.

---

## 13. Required Evidence

### EV-01: For PPV Reporting
- SAP Material Ledger standard cost estimate (CK13N) showing approved standard prices for the period.
- Commodity index source (e.g., LME copper price, oil price index) used for COMMODITY_PRICE classification.
- Signed-off PPV report from Finance Controller and CPO for each monthly close.

### EV-02: For 3-Way Match
- SAP tolerance configuration screenshot (OMR6 — invoice verification tolerances) for audit purposes.
- Exception aging report snapshot at period close showing total open exposure.
- Evidence that escalations were performed per BR-03 for exceptions > 30 days.

### EV-03: For Inventory Valuation
- FIFO layer calculation workbook or database query confirming lot-level cost assignment.
- LCNRV assessment workbook signed by Finance Controller per IAS 2.9 requirements.
- Prior period restatement approval if LCNRV write-downs were reversed.

### EV-04: For Landed Cost
- Freight invoice copies for top 10 lanes by spend (audit sample).
- Customs declaration (SAD/Entry Summary) confirming duty rate applied.
- Insurance certificate confirming premium rate.

### EV-05: For Working Capital
- GL trial balance extract reconciling inventory, AR, and AP balances.
- Treasury sign-off on CCC calculation for group cash flow reporting.

---

## 14. Dashboard Design

### Power BI Report Structure

**Page 1: Finance Supply Chain Executive Summary**
- KPI cards: CCC (current vs. prior month vs. benchmark), PPV total ($, favorable vs. unfavorable), 3-Way Match Auto Rate, Freight % COGS
- CCC waterfall: DIO + DSO - DPO with prior month comparison
- PPV trend: 12-month line chart by category (favorable/unfavorable stacked bar)
- Working capital bridge: Opening → Inventory change → AR change → AP change → Closing

**Page 2: Purchase Price Variance Detail**
- Top 10 unfavorable PPV by supplier (bar chart, $)
- Top 10 unfavorable PPV by commodity category (bar chart, $)
- PPV decomposition: Price / Volume / Mix effects (waterfall)
- PPV % distribution: Histogram of PPV% across all PO lines
- Drillthrough: Supplier → All PO lines with PPV detail

**Page 3: Working Capital Analysis**
- DIO / DSO / DPO trend: 24-month line chart per entity
- CCC by entity: Bar chart comparison across legal entities
- Working capital sensitivity: Table showing $impact of +/- 1 day in each metric
- Inventory days by product category: Heatmap (Category × Month)

**Page 4: Inventory Valuation**
- FIFO vs. Moving Average gap: Bar chart by plant
- LCNRV write-down exposure: List of materials at risk with exposure ($)
- Inventory aging: Bucket analysis (0-30, 31-60, 61-90, 91-180, 180+ days)
- Slow-moving inventory flag: Materials with DIO > 2× category average

**Page 5: Landed Cost Analysis**
- Landed cost waterfall: By top 10 SKUs (base price + each cost component)
- Landed cost variance: Budget vs. actual by component (100% stacked bar)
- Duty rate heatmap: HS code × country of origin
- Freight cost per kg by mode: Trend chart (12 months)

**Page 6: 3-Way Match Exception Dashboard**
- Exception funnel: Total invoices → Auto-matched → Exceptions by type
- Exception aging buckets: 0-15 / 15-30 / 30-45 / 45+ days with exposure ($)
- Open exception table: Sortable by age, exposure, owner, exception type
- SLA compliance: % of exceptions resolved within 15 days (target > 80%)

**Page 7: Freight Cost Analysis**
- Freight % COGS: 12-month trend by transport mode
- Carrier rate variance: Actual vs. contracted by carrier (bar chart)
- Top 10 lanes by freight spend (map + table)
- Surcharge analysis: BAF, PSS, peak season surcharge trend

**Filters Available Across All Pages**
- Fiscal Year / Period (single or range)
- Legal Entity / Company Code
- Plant / Region
- Commodity Category / Material Group
- Vendor / Supplier
- Purchasing Group

---

## 15. Use Cases

### UC-01: Month-End Close Pack Preparation
**Actor:** Finance Controller
**Trigger:** Last working day of fiscal period
**Process:**
1. Controller opens Page 1 Executive Summary — validates all KPI cards show current period data.
2. Reviews PPV report (Page 2) — exports top 10 unfavorable items for CPO commentary.
3. Reviews 3-way match exception queue (Page 6) — confirms all exceptions > 45 days have accruals.
4. Signs off working capital position (Page 3) and sends to Treasury.
5. Exports LCNRV write-down list (Page 4) for Finance Director approval.
6. Close pack PDF auto-generated and distributed to CFO/CPO by D+1 of month close.

### UC-02: Procurement Negotiation Preparation
**Actor:** Category Manager / CPO
**Trigger:** Quarterly supplier review preparation
**Process:**
1. Filter Page 2 by supplier and 12-month period.
2. Review PPV trend — identify suppliers with consistently unfavorable PPV (paid more than standard).
3. Export PPV decomposition — separate commodity price exposure from negotiation outcomes.
4. Use landed cost analysis (Page 5) to understand total cost of ownership vs. cheaper apparent suppliers.
5. Prepare supplier negotiation brief with 12-month PPV data as supporting evidence.

### UC-03: Exception Queue Management
**Actor:** AP Processor / AP Supervisor
**Trigger:** Daily exception queue review
**Process:**
1. AP Processor opens Page 6 — filters to own exception queue by owner field.
2. Sorts by aging days descending — addresses oldest exceptions first.
3. For MISSING_GR exceptions: contacts warehouse team to confirm receipt.
4. For PRICE_EXCEPTION: raises dispute with supplier or requests PO amendment.
5. Supervisor monitors SLA compliance — escalates Red exceptions (> 30 days) per BR-03.

### UC-04: Working Capital Improvement Program
**Actor:** Supply Chain Director + Treasury + Finance Controller
**Trigger:** Quarterly working capital review
**Process:**
1. Review CCC trend (Page 3) — identify which component (DIO/DSO/DPO) is deteriorating.
2. Run sensitivity analysis — calculate $ impact of 5-day DIO reduction.
3. Drill into inventory aging (Page 4) — identify slow-moving stock categories.
4. For DPO improvement: identify suppliers where actual payment < contracted terms (early payment leakage).
5. Design targeted improvement initiatives with measurable CCC impact.

---

## 16. Recommended Actions

### RA-01: PPV Management
- Establish a PPV owner in each commodity category (category manager) with monthly accountability.
- Set PPV budget targets by category at the start of each fiscal year aligned with the annual operating plan.
- For COMMODITY_PRICE classified PPV > 3% unfavorable: consider hedging instruments (forward contracts, fixed-price agreements).
- For NEGOTIATION classified unfavorable PPV: initiate supplier negotiation within 60 days; escalate to CPO if unresolved.

### RA-02: 3-Way Match Automation
- Target 95% auto-match rate within 12 months by: (a) cleaning up PO price accuracy at creation, (b) implementing EDI-based invoice receipt (eliminating paper/manual entry), (c) training suppliers on e-invoicing via supplier portal.
- Implement SAP Invoice Management (OpenText or SAP Fiori) for exception workflow automation.
- Set up daily exception SLA monitoring with automated email alerts to exception owners.

### RA-03: Working Capital Optimisation
- For DIO reduction: implement ABC analysis-driven reorder points; excess stock > DIO threshold triggers markdown or return-to-vendor.
- For DPO optimisation: review all supplier payment terms; negotiate 60-day terms for strategic suppliers (Kraljic STRATEGIC quadrant) while maintaining 30-day for BOTTLENECK suppliers.
- For DSO reduction: implement dynamic discounting for early customer payment.

### RA-04: Landed Cost Transparency
- Mandate that all new POs for imported materials include estimated landed cost breakdown in SAP (via condition types).
- Implement customs classification (HS code) governance: quarterly review to ensure correct duty rates applied.
- Negotiate all-inclusive (DDU/DDP) pricing with suppliers for high-volume lanes to simplify landed cost tracking.

### RA-05: Freight Cost Control
- Implement carrier rate audit: automated comparison of invoiced rate vs. contracted rate for every freight invoice.
- Dispute process: Any carrier invoice > 2% above contracted rate automatically triggers dispute; payment withheld until resolved.
- Quarterly lane optimisation review: consolidate LTL to FTL where volume justifies; shift air to ocean for non-urgent shipments.

---

## 17. Test Cases

### TC-01: PPV Calculation Correctness

**Scenario:** PO line for 1,000 units of SKU-A with PO price $10.00/unit. Standard price $10.50/unit. Invoice received for 950 units at $10.20/unit.

**Expected PPV:**
- Actual price = $10.20
- Standard price = $10.50
- Quantity invoiced = 950 units
- PPV = ($10.50 - $10.20) × 950 = $285.00 FAVORABLE
- PPV% = ($10.50 - $10.20) / $10.50 × 100 = 2.86%

**Test steps:**
1. Insert test PO, GR, and IR records with above values into staging tables.
2. Run ETL transformation pipeline.
3. Query fact_ppv for the test EBELN.
4. Assert: ppv_amount = 285.00 (tolerance ±$0.01), ppv_pct = 2.857% (tolerance ±0.01%), is_favorable = 1.

### TC-02: 3-Way Match — Price Exception

**Scenario:** PO price = $100.00/unit, GR = 100 units, Invoice = 100 units at $103.50/unit. Price variance = 3.5% > 2% tolerance.

**Expected match_status:** PRICE_EXCEPTION
**Expected financial_exposure:** ABS(($103.50 - $100.00) × 100) = $350.00

**Test steps:**
1. Create test PO, GR, IR with above values.
2. Run match ETL.
3. Assert: match_status = 'PRICE_EXCEPTION', financial_exposure_lc = 350.00, aging_days = 0 on day of creation.

### TC-03: CCC Calculation

**Scenario:** Entity ABC, Period 2026-03.
- Average Inventory: $5,000,000
- Average AR: $3,000,000
- Average AP: $2,500,000
- Monthly COGS: $4,000,000 → Annual: $48,000,000
- Monthly Revenue: $6,000,000 → Annual: $72,000,000

**Expected:**
- DIO = ($5,000,000 / $48,000,000) × 365 = 38.02 days
- DSO = ($3,000,000 / $72,000,000) × 365 = 15.21 days
- DPO = ($2,500,000 / $48,000,000) × 365 = 19.01 days
- CCC = 38.02 + 15.21 - 19.01 = 34.22 days

**Test steps:**
1. Insert test working capital records.
2. Run working capital ETL.
3. Assert all four calculated fields within ±0.1 days of expected.

### TC-04: LCNRV Write-Down Detection

**Scenario:** Material X has moving average cost $50.00/unit, stock 200 units. Current NRV (estimated selling price $55 - estimated selling costs $8) = $47.00/unit.

**Expected:** Write-down required because NRV ($47) < Cost ($50).
**Write-down amount** = ($50 - $47) × 200 = $600.

**Test steps:**
1. Insert material valuation and NRV data.
2. Run LCNRV check procedure.
3. Assert: write_down_required = 1, write_down_amount = 600.00.

### TC-05: Freight Allocation — Weight-Based

**Scenario:** Shipment with two PO lines: Line 1 = 100 kg, Line 2 = 400 kg. Total freight = $2,500.

**Expected:**
- Line 1 freight = $2,500 × (100/500) = $500
- Line 2 freight = $2,500 × (400/500) = $2,000

**Test steps:**
1. Insert shipment and PO line weight data.
2. Run freight allocation ETL.
3. Assert allocation amounts match expected values within $0.01.

---

## 18. Risks and Mitigations

| Risk ID | Risk Description | Probability | Impact | Mitigation |
|---------|-----------------|-------------|--------|------------|
| R-01 | SAP standard prices not maintained timely → PPV calculations incorrect | Medium | High | Automate standard price freeze notification at period start; block PPV report publication if > 5% materials missing standard price |
| R-02 | Freight invoices received after period close → Landed cost understated | High | Medium | Implement accrual model using contracted rates × GR quantities for all uninvoiced freight; review and reverse next period |
| R-03 | FX rate feed failure → Incorrect currency conversion for PPV/Working Capital | Low | High | Fallback to prior business day rate; alert monitoring; daily data quality check |
| R-04 | SAP material ledger not activated → FIFO valuation not available | Medium | Medium | Confirm ML activation scope with SAP team pre-implementation; define manual FIFO calculation procedure as interim |
| R-05 | Poor supplier data quality → High orphan invoice rate degrading 3-way match | Medium | High | Supplier portal onboarding with data quality validation; reject invoices without PO reference after 90-day grace period |
| R-06 | Multiple ERP instances across entities → Data inconsistency in consolidated reports | Medium | High | Establish golden record hierarchy; master data governance council; SAP MDG implementation roadmap |
| R-07 | LCNRV assessment depends on NRV estimates which may be subjective | High | Medium | Define NRV methodology in accounting policy; require Finance Controller sign-off; external audit sampling |
| R-08 | Power BI DirectQuery performance degradation on large exception table | Medium | Low | Implement aggregation tables in Azure SQL; partition fact tables by YYYYMM; limit default date range to 3 months |

---

## 19. Implementation Checklist

### Data Foundation
- [ ] SAP S/4HANA EKKO, EKPO, MKPF, MSEG, RBKP, RSEG, CKMLCR tables extracted to Azure SQL staging
- [ ] SAP CDC (Change Data Capture) configured for near-real-time delta loads
- [ ] Material Ledger activated and standard cost estimates created for all active materials
- [ ] FX rate data feed configured (ECB/FRB daily rates loaded to Azure SQL dim_exchange_rate)
- [ ] Freight invoice data source connected (TMS API or EDI 210 file ingestion)
- [ ] Carrier master table populated with contracted rate data
- [ ] Customs duty/tariff rate table loaded with HS code classifications

### Data Model and ETL
- [ ] All staging tables (stg_*) created with correct schema and indexes
- [ ] All conformed dimension tables (dim_*) created and populated
- [ ] All fact tables (fact_ppv, fact_three_way_match, fact_landed_cost, fact_working_capital, fact_freight_cost, fact_inventory_valuation) created
- [ ] ETL pipelines built and tested for each fact table
- [ ] PPV decomposition logic (price/volume/mix effects) implemented and tested
- [ ] Three-way match tolerance configuration table created (configurable by vendor/material type)
- [ ] Freight allocation logic implemented (direct/weight/value hierarchy)
- [ ] LCNRV check procedure implemented
- [ ] FIFO layer calculation implemented (or confirmed from SAP Material Ledger)
- [ ] Working capital calculation procedure implemented

### Reporting and Dashboards
- [ ] Power BI semantic model created with all fact and dimension tables
- [ ] All 7 dashboard pages designed and implemented
- [ ] Scheduled refresh configured (4x daily)
- [ ] Row-level security (RLS) configured by entity/region
- [ ] Alert rules configured for PPV thresholds and exception aging
- [ ] Exception routing logic implemented (by exception type to owner)
- [ ] Month-end close pack auto-export configured

### Governance and Controls
- [ ] Business rules documented and signed off by Finance Controller and CPO
- [ ] Tolerance configuration approved by AP Manager and Finance Director
- [ ] LCNRV accounting policy documented and approved
- [ ] Data quality checks implemented in ETL (per VC-01 to VC-04)
- [ ] Period close readiness gate checklist automated in Power BI
- [ ] Audit trail configured for exception resolution actions

---

## 20. Validation Checklist

### Pre-Go-Live Validation

- [ ] PPV calculation spot-checked for 10 PO lines against manual SAP ME2M report — all match within $0.01
- [ ] 3-way match status for 20 invoices validated against SAP MIRO display — all statuses match
- [ ] CCC for 3 legal entities validated against manually calculated working capital from trial balance — within 0.5 days
- [ ] Landed cost for top 5 SKUs validated against manual cost build-up — within $0.05/unit
- [ ] FIFO vs. Moving Average gap validated against SAP MBGR report — within $100 per plant
- [ ] Freight allocation validated for 3 consolidated shipments — allocated amounts sum to total invoice
- [ ] LCNRV write-down list validated against Finance Controller manual assessment — all high-risk items included
- [ ] All ETL pipelines complete without error for one full fiscal period (parallel run)
- [ ] Power BI data matches Azure SQL queries for all 7 dashboard pages
- [ ] Exception escalation alerts tested (inserted aging test records — confirmed alert emails received)

### Monthly Ongoing Validation (First 3 Months)

- [ ] PPV total reconciles to CO settlement report (month-end actual vs. standard cost variance)
- [ ] Working capital values reconcile to CFO monthly reporting pack
- [ ] 3-way match exception count reconciles to AP open items report
- [ ] Freight cost total reconciles to GL freight account (520000-529999 range)
- [ ] Inventory valuation total reconciles to balance sheet inventory line
- [ ] Period close pack signed off by Finance Controller by D+2 of month close

---

## 21. Pending Information

| Item | Owner | Required By | Impact if Missing |
|------|-------|-------------|------------------|
| Confirmed list of SAP company codes in scope | SAP Basis / Finance | 2026-07-15 | Cannot configure entity dimension |
| Freight carrier contracted rate schedule | Logistics Director | 2026-07-15 | Cannot compute carrier rate variance |
| Invoice tolerance configuration values by vendor category | AP Manager + Finance Controller | 2026-07-22 | Cannot implement match tolerance logic |
| NRV estimation methodology and responsible team | Finance Controller | 2026-07-22 | Cannot automate LCNRV check |
| HS code classification for top 200 purchased materials | Trade Compliance / Procurement | 2026-08-01 | Cannot compute customs duty in landed cost |
| SAP Material Ledger activation status per plant | SAP CO Team | 2026-07-15 | Determines FIFO calculation approach (ML-based vs. manual FIFO) |
| Commodity index data feeds (LME, oil, etc.) for PPV classification | Finance / Treasury | 2026-08-01 | Cannot classify COMMODITY_PRICE PPV automatically |
| Power BI workspace and Azure SQL connection approval | IT Security | 2026-07-10 | Blocks all dashboard development |
| Confirmed fiscal year variant (K4 or custom) for all entities | SAP Finance | 2026-07-15 | Affects period alignment in all ETL logic |

---

## 22. Implementation Roadmap

### Phase 1: Foundation (Weeks 1-4)

**Objective:** Establish data infrastructure and validate source system connectivity.

| Week | Activities |
|------|-----------|
| 1 | SAP extraction configuration: CDC setup for EKKO, EKPO, MKPF, MSEG, RBKP, RSEG, CKMLCR; Azure SQL environment provisioning |
| 2 | Staging table creation; initial full-load data extraction; data quality assessment (record counts, null rates, key violations) |
| 3 | Conformed dimension tables created (dim_material, dim_vendor, dim_plant, dim_date, dim_gl_account); master data quality remediation |
| 4 | Freight invoice ingestion configured; carrier master loaded; FX rate feed operational; first data quality report shared with Finance Controller |

**Gate:** All source systems extracted, staging tables populated, data quality baseline established.

### Phase 2: Core Analytics (Weeks 5-10)

**Objective:** Build and validate all six core analytical models.

| Week | Activities |
|------|-----------|
| 5 | fact_ppv ETL built and tested; PPV decomposition (price/volume/mix) implemented; PPV classification logic implemented |
| 6 | fact_three_way_match ETL built; tolerance configuration loaded; match status logic implemented; exception routing table created |
| 7 | fact_landed_cost ETL built; freight allocation (direct/weight/value) implemented; customs duty logic implemented |
| 8 | fact_working_capital ETL built; DIO/DSO/DPO/CCC procedures implemented; entity-level aggregation validated |
| 9 | fact_inventory_valuation ETL built; FIFO layer calculation implemented; LCNRV check procedure built and tested |
| 10 | fact_freight_cost ETL built; carrier rate variance logic implemented; freight allocation to cost objects complete |

**Gate:** All six fact tables populated and validated against manual calculations (per TC-01 to TC-05).

### Phase 3: Dashboard and Reporting (Weeks 11-14)

**Objective:** Deliver Power BI dashboards and reporting layer.

| Week | Activities |
|------|-----------|
| 11 | Power BI semantic model built; Page 1 (Executive Summary) and Page 2 (PPV Detail) developed; stakeholder review |
| 12 | Pages 3-4 (Working Capital, Inventory Valuation) developed; RLS security model implemented |
| 13 | Pages 5-7 (Landed Cost, 3-Way Match, Freight) developed; alert rules configured; scheduled refresh operational |
| 14 | User acceptance testing (UAT) with Finance Controllers and AP team; defect resolution; dashboard sign-off |

**Gate:** UAT sign-off from Finance Controller, CPO representative, and AP Manager.

### Phase 4: Parallel Run and Go-Live (Weeks 15-18)

**Objective:** Validate analytics against existing reports for one full fiscal period.

| Week | Activities |
|------|-----------|
| 15-16 | Parallel run: new analytics run alongside existing manual processes for Month 1; discrepancies investigated and resolved |
| 17 | Month-end close pack generated from new dashboard for first time; Finance Controller comparison vs. manual pack |
| 18 | Go-live decision gate; training delivered to all users; hypercare support plan activated |

**Gate:** Finance Controller confirms month-end close pack from dashboard is equivalent to or better than manual pack. CFO sign-off for go-live.

### Phase 5: Continuous Improvement (Month 5 onwards)

- Monthly: PPV root-cause report reviewed by CPO; exception SLA compliance reviewed by AP Manager.
- Quarterly: CCC improvement initiatives tracked; freight lane optimisation reviewed; tolerance thresholds recalibrated.
- Annually: Standard prices updated; LCNRV policy reviewed; dashboard design updated for new business requirements.
- Ongoing: Supplier portal onboarding to increase e-invoice rate and improve auto-match performance.

---

**Document Control**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-06-20 | Finance Analytics Team | Initial document |
| 2.0.0 | 2026-06-22 | Senior Supply Chain Analytics Consultant | Full rewrite with 22-section analytics framework |

**References**
- SAP S/4HANA Finance Documentation — FI/CO/MM Integration (SAP Help Portal)
- IAS 2 Inventories (IFRS Foundation, 2003, amended 2023)
- ASC 330 Inventory (FASB, US GAAP)
- Chopra & Meindl, Supply Chain Management, 6th Ed., Chapter 14 (Working Capital)
- SCOR Digital Standard — Asset Management and Financial Flows performance attributes
- Incoterms 2020 (ICC, 2019)
