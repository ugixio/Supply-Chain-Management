# Inventory Health & Excess/Obsolete Analytics — Implementation Guide

**Department:** 05 — Inventory Management
**Analytics Topic:** Inventory Health Assessment, Shortage Analysis, Excess and Obsolete Inventory (E&O),
ABC/XYZ Classification, Safety Stock Compliance, Cycle Count Accuracy
**Standard Alignment:** SCOR-DS · ISO 28000:2022 · GS1 Gen. Specs. v23 · ISO 9001:2015 §8.5.2
**Document Status:** Authorised for Implementation
**Last Reviewed:** 2026-06-22
**Audience:** Senior Supply Chain Architects, ERP Programme Managers, Power BI Developers, Data Science Leads
**Business Context:** €50B global multinational, 40 countries, SAP S/4HANA MM/WM, Power BI, Azure SQL, Python.
Daily inventory snapshots. Physical inventory and cycle counts monthly/quarterly.

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

This document defines the complete analytics implementation for Inventory Health and Excess/Obsolete
(E&O) management across the enterprise Supply Chain Management platform. The organisation operates a
global inventory footprint across 40 countries with SAP S/4HANA as the ERP backbone, Power BI as the
reporting layer, Azure SQL as the analytical data warehouse, and Python for statistical modelling.

Inventory typically represents 20–35% of total assets in manufacturing and distribution organisations
(Chopra & Meindl, 2016). For a €50B enterprise, even a 1% reduction in excess inventory translates to
approximately €50M in freed working capital. The analytics programme described here provides the data
infrastructure, KPI framework, and decision-support tools required to achieve three primary outcomes:

**Working capital reduction:** Identify and liquidate excess and obsolete inventory to reduce days
inventory outstanding (DIO) by 10–20 days and free €150–400M in working capital within 18 months
of full deployment.

**Service level protection:** Maintain fill rates above 98.5% and prevent stockouts through early
shortage detection based on coverage day thresholds, safety stock compliance monitoring, and
forward-looking demand-supply gap analysis.

**Cycle count accuracy:** Achieve and sustain inventory accuracy above 99.5% through an ABC-driven
continuous cycle counting programme, anomaly detection on adjustment transactions, and root cause
tracking of discrepancies.

The implementation is structured across 22 sections covering data sourcing from SAP S/4HANA, star
schema design in Azure SQL, Power BI dashboard specifications, KPI formulas, business rules, and a
week-by-week implementation roadmap spanning 16 weeks.

---

## 2. Analysis Objective

The primary objective of this analytics implementation is to establish a single, trusted view of
inventory health across all legal entities, distribution centres, and third-party logistics providers,
enabling proactive management decisions that reduce both stockout risk and excess/obsolete inventory.

Specific analytical objectives:

- **Inventory health assessment:** Classify all active SKUs by coverage days, turnover rate, and
  aging bracket. Flag items approaching critical coverage thresholds before stockouts occur.

- **Shortage detection:** Identify SKUs with zero or critically low on-hand stock relative to open
  demand. Quantify shortage exposure in units and value.

- **Excess and obsolete identification:** Quantify the financial exposure of excess inventory
  (overstocked relative to demand) and obsolete inventory (no movement in 365+ days).

- **ABC/XYZ segmentation:** Classify all active SKUs into the 9-cell ABC-XYZ matrix to enable
  differentiated replenishment policies, service level targets, and management attention allocation.

- **Safety stock compliance:** Compare actual on-hand stock against statistically calculated safety
  stock requirements and flag SKUs below their safety stock level.

- **Cycle count accuracy:** Track count accuracy by location, zone, ABC class, and warehouse to
  identify systemic accuracy gaps and drive corrective action.

---

## 3. Scope

### In Scope

- All active SKUs (status = ACTIVE) across all SAP plants, storage locations, and distribution centres
  within the 40-country footprint
- Raw materials, finished goods, semi-finished goods, maintenance/repair/operations (MRO), and packaging
  materials
- Consignment stock held by the organisation but owned by suppliers (memo tracking only, clearly labelled
  as non-owned in all reports)
- All SAP movement types generating stock movements (GR, GI, transfers, adjustments, scrapping)
- Physical inventory and cycle count results from SAP WM and SAP EWM
- Daily snapshots stored in Azure SQL for trending and aging analysis
- Safety stock levels maintained in SAP MRP (MRP2 view, fields: safety stock, reorder point)

### Out of Scope

- Customer-owned goods held on a bailment basis (tracked in a separate custodial system)
- Project stock (special stock indicator Q) — analysed separately by the Project Management Office
- Vendor-managed inventory (VMI) where ownership has not transferred to the organisation
- Capital assets and fixed assets managed in SAP FI-AA
- Items with status DISCONTINUED or BLOCKED — included in E&O analysis only, not in active health KPIs

### Geographic Scope

All 40 countries. Regional rollout sequence: Europe (Weeks 1–6), Americas (Weeks 7–10),
Asia-Pacific (Weeks 11–14), Middle East and Africa (Weeks 15–16).

---

## 4. Business Questions

The analytics framework is designed to answer the following specific business questions:

**BQ-01:** Which SKUs are at risk of stockout within the next 7, 14, or 30 days based on current
on-hand stock, average daily usage, and open purchase orders?

**BQ-02:** What is the total financial value of excess inventory by country, plant, product category,
and ABC class, and which SKUs represent the highest excess exposure?

**BQ-03:** Which SKUs have had no stock movement in the past 365 days, what is their total value,
and what is the recommended disposition (markdown, return to supplier, scrap, inter-plant transfer)?

**BQ-04:** What is the current inventory turnover ratio and days inventory outstanding by region,
product category, and ABC class, and how does it compare to the prior year and industry benchmarks?

**BQ-05:** Which plants or storage locations have the highest percentage of SKUs below their
calculated safety stock level, and what is the aggregate demand-at-risk in units and value?

**BQ-06:** What is the cycle count accuracy rate by warehouse, zone, and ABC class for the current
month and trailing 12 months, and which locations have repeat discrepancies?

**BQ-07:** What is the E&O ratio (excess plus obsolete value as a percentage of total inventory
value) by business unit, and how does it trend over the past 24 months?

**BQ-08:** Which XYZ-Z class items (high demand variability) have experienced the largest safety
stock violations in the past 90 days, and what is the associated service level impact?

**BQ-09:** Which suppliers are contributing most to excess inventory through over-delivery or
premature shipment, and what is the financial impact by supplier and commodity group?

**BQ-10:** What is the aging profile of the current inventory (0–30 days, 31–90 days, 91–180 days,
181–365 days, >365 days) expressed in units, pallets, and value?

**BQ-11:** How many SKUs are classified as AZ (high value, erratic demand) and what specific
replenishment and safety stock policies are applied to each?

**BQ-12:** What is the projected inventory value at the end of the next quarter based on current
coverage days and demand forecast, and what actions are required to hit the DIO target?

---

## 5. Data Sources

### DS-01: SAP S/4HANA — Daily Inventory Snapshot

| Attribute | Detail |
|---|---|
| Source Name | SAP S/4HANA MM — Material Management |
| Origin System | SAP S/4HANA production client |
| Table/Query | MARD (storage location stock), MBEW (material valuation), MARA (material master), MARC (plant data) |
| Data Owner | Global Inventory Control Manager |
| Frequency | Daily batch extract at 23:00 UTC via SAP RFC / BW extractor |
| Required Fields | MATNR, WERKS, LGORT, LABST (unrestricted stock), EINME (GR blocked), SPEME (blocked stock), UMLME (stock in transfer), MEINS (UOM), VPRSV (price control), VERPR (moving avg price), STPRS (standard price) |
| Critical Fields | MATNR, WERKS, LGORT, LABST — null or negative values constitute a data quality breach |
| Primary Key | MATNR + WERKS + LGORT + snapshot_date |
| Validations | LABST >= 0; MATNR exists in material master (MARA); WERKS in active plant list |
| Possible Errors | Delta extractor gaps if SAP transport applied during extraction window; MBEW valuation missing for new materials; MEINS UOM mismatch vs. GS1 standard |
| Extraction Evidence | SAP job log (SM37): job ZINV_SNAP_DAILY; Azure Data Factory pipeline run ID logged to audit table |

### DS-02: SAP S/4HANA — Stock Movement History

| Attribute | Detail |
|---|---|
| Source Name | SAP S/4HANA — Material Document History |
| Origin System | SAP S/4HANA |
| Table/Query | MSEG (material document segment), MKPF (material document header) |
| Data Owner | Warehouse Operations Manager |
| Frequency | Daily incremental extract (delta via change pointer) |
| Required Fields | MBLNR (document number), MJAHR (year), ZEILE (line), MATNR, WERKS, LGORT, BWART (movement type), MENGE (quantity), MEINS, BUDAT (posting date), BLDAT (document date), BKTXT (reference) |
| Critical Fields | BWART, MENGE, BUDAT — used to compute ADU, turnover, and aging |
| Primary Key | MBLNR + MJAHR + ZEILE |
| Validations | BWART in approved movement type list; BUDAT <= current date; MENGE != 0 |
| Possible Errors | Backdated postings distorting daily ADU; incorrect reversal movements creating phantom demand; movement type 551 (scrapping) posted without NCR reference |
| Extraction Evidence | ADF pipeline ZINV_MVMT_DELTA; row count reconciled against SAP transaction MB51 |

### DS-03: SAP S/4HANA — MRP Safety Stock and Reorder Points

| Attribute | Detail |
|---|---|
| Source Name | SAP S/4HANA MRP — MRP2 Planning View |
| Origin System | SAP S/4HANA |
| Table/Query | MARC (EISBE = safety stock, MINBE = reorder point, MTVFP = checking rule, DISMM = MRP type) |
| Data Owner | Demand Planning Manager |
| Frequency | Weekly extract (Sunday 02:00 UTC) |
| Required Fields | MATNR, WERKS, EISBE (safety stock), MINBE (reorder point), DISMM (MRP type), DZEIT (in-house production time), PLIFZ (planned delivery time) |
| Critical Fields | EISBE — used for safety stock compliance KPI; must be > 0 for all A and B class active SKUs |
| Primary Key | MATNR + WERKS |
| Validations | EISBE >= 0; MINBE >= EISBE; DISMM in (ND, PD, VB, VM) |
| Possible Errors | Safety stock set to 0 for items that should have SS (data entry error); MRP type ND (no planning) for active SKUs |
| Extraction Evidence | ADF pipeline ZMRP_SS_WEEKLY; reconciled against SAP transaction MD04 sample check |

### DS-04: SAP WM / EWM — Cycle Count Results

| Attribute | Detail |
|---|---|
| Source Name | SAP WM Inventory Management / SAP EWM Physical Inventory |
| Origin System | SAP WM (legacy) and SAP EWM (modern DCs) |
| Table/Query | LINV (inventory document), LQUA (WM quant), /SCWM/QUAN (EWM quant) |
| Data Owner | Physical Inventory Controller |
| Frequency | Daily extract of completed count documents |
| Required Fields | IVNR (inventory document), MATNR, LGNUM (warehouse number), LGTYP (storage type), LGPLA (storage bin), ANZLI (system book stock), ANZPH (counted quantity), IDATU (count date), KZDIF (difference indicator), BUDAT (posting date) |
| Critical Fields | ANZLI, ANZPH — delta = adjustment quantity; KZDIF flag indicates whether recount was performed |
| Primary Key | IVNR + LGPLA + MATNR |
| Validations | ANZPH >= 0; count date within current fiscal year; ANZLI reconciles to inventory snapshot for same date |
| Possible Errors | Double-counting if count document posted before snapshot extract; EWM and WM data arriving in different pipelines creating duplication |
| Extraction Evidence | ADF pipeline ZINV_CYCLE_COUNT; count document numbers logged in audit table |

### DS-05: Azure SQL — Demand History (Cleaned)

| Attribute | Detail |
|---|---|
| Source Name | Azure SQL — Demand History Fact Table |
| Origin System | Downstream from SAP SD (sales orders) and SAP MM (internal consumption) via ADF |
| Table/Query | fact_demand_daily (Azure SQL DW) |
| Data Owner | Demand Planning Analytics Lead |
| Frequency | Daily refresh |
| Required Fields | sku_id, plant_code, demand_date, demand_units, demand_value_cents, demand_source (CUSTOMER_ORDER / INTERNAL_CONSUMPTION / FORECAST) |
| Critical Fields | demand_units — used for ADU calculation; must exclude returns and cancellations |
| Primary Key | sku_id + plant_code + demand_date + demand_source |
| Validations | demand_units >= 0; no future dates; demand_source in approved list |
| Possible Errors | SAP cancellation reversals creating negative demand rows; promotional spikes inflating ADU |
| Extraction Evidence | ADF pipeline ZDEM_DAILY; row count and sum reconciled daily against SAP MB52 |

### DS-06: SAP S/4HANA — Material Master (Classification)

| Attribute | Detail |
|---|---|
| Source Name | SAP S/4HANA — Material Master Classification |
| Origin System | SAP S/4HANA |
| Table/Query | MARA (general data), MAKT (descriptions), KLAH/KSSK/AUSP (classification) |
| Data Owner | Master Data Steward |
| Frequency | Weekly full extract |
| Required Fields | MATNR, MBRSH (industry sector), MTART (material type), MATKL (material group), BRGEW (gross weight), NTGEW (net weight), VOLUM (volume), VOLEH (volume unit), MEINS (base UOM), BISMT (old material number) |
| Critical Fields | MATKL — used for product hierarchy in all reports; MTART — determines material category |
| Primary Key | MATNR |
| Validations | MATNR not null; MATKL in approved material group list; MEINS is a valid GS1 UOM code |
| Possible Errors | Material group (MATKL) not maintained; duplicate materials created due to no BISMT cross-reference |
| Extraction Evidence | ADF pipeline ZMARA_WEEKLY |

---

## 6. Data Model

The analytics solution uses a star schema deployed in Azure SQL with one central fact table and six
dimension tables. All monetary values are stored as integer cents (BIGINT) per the project Money
convention. All dates are ISO 8601 (YYYY-MM-DD).

### Fact Tables

**fact_inventory_snapshot** — Grain: one row per SKU + plant + storage location + snapshot date.
Captures the end-of-day on-hand inventory position, valuation, coverage days, and health classification.
Partitioned by snapshot_date (monthly partitions in Azure SQL) for query performance.

**fact_stock_movements** — Grain: one row per SAP material document line.
Captures all stock movement events with movement type, quantity, value, and GL accounts.
Used for ADU calculation, turnover computation, and aging analysis. Retained rolling 36 months.

**fact_cycle_counts** — Grain: one row per count document per storage bin per SKU.
Captures system book stock, counted quantity, variance, and accuracy flag.
Used for cycle count accuracy KPI and discrepancy trending.

### Dimension Tables

**dim_material** — SKU master with GS1 attributes, material type, product hierarchy, lot tracking flags,
ABC/XYZ classification, safety stock level, and REACH/UFLPA compliance flags.

**dim_plant** — Plant and storage location master with country, region, currency, and DC manager.

**dim_date** — Calendar dimension with fiscal week, fiscal period, fiscal year, holiday flags, peak
season flag, and planning horizon attributes.

**dim_movement_type** — SAP movement type classification mapping BWART codes to analytical categories
(GOODS_RECEIPT, GOODS_ISSUE, TRANSFER, ADJUSTMENT, SCRAP, RETURN).

**dim_abc_xyz** — ABC-XYZ 9-cell classification with policy attributes (review cycle, SS method,
service level target, count frequency).

**dim_safety_stock** — Current safety stock and reorder point by SKU and plant, refreshed weekly
from SAP MRP.

### Key Relationships

```
fact_inventory_snapshot.sku_id         --> dim_material.sku_id          (many-to-one)
fact_inventory_snapshot.plant_code     --> dim_plant.plant_code          (many-to-one)
fact_inventory_snapshot.snapshot_date  --> dim_date.date_id              (many-to-one)
fact_inventory_snapshot.abc_xyz_cell   --> dim_abc_xyz.cell_code         (many-to-one)
fact_stock_movements.sku_id            --> dim_material.sku_id           (many-to-one)
fact_stock_movements.movement_type_code--> dim_movement_type.bwart_code  (many-to-one)
fact_cycle_counts.sku_id               --> dim_material.sku_id           (many-to-one)
dim_safety_stock.sku_id                --> dim_material.sku_id           (one-to-one per plant)
```

---

## 7. Data Dictionary

### Table: fact_inventory_snapshot

| Field | Type | Description | PK |
|---|---|---|---|
| snapshot_id | BIGINT IDENTITY | Surrogate primary key | Yes |
| snapshot_date | DATE | ISO 8601 date of snapshot | No |
| sku_id | NVARCHAR(40) | SAP material number (MATNR) | No |
| plant_code | NVARCHAR(4) | SAP plant code (WERKS) | No |
| storage_location | NVARCHAR(4) | SAP storage location (LGORT) | No |
| on_hand_units | DECIMAL(18,3) | Unrestricted stock quantity (LABST) | No |
| blocked_units | DECIMAL(18,3) | Quality-blocked stock (SPEME) | No |
| in_transfer_units | DECIMAL(18,3) | Stock in transfer (UMLME) | No |
| unit_cost_cents | BIGINT | Moving average or standard price in integer cents | No |
| on_hand_value_cents | BIGINT | on_hand_units x unit_cost_cents rounded to integer | No |
| adu_90d | DECIMAL(18,3) | Average daily usage — 90-day rolling | No |
| coverage_days | DECIMAL(10,2) | on_hand_units / adu_90d; NULL if adu_90d = 0 | No |
| coverage_bucket | NVARCHAR(20) | CRITICAL / WARNING / HEALTHY / EXCESS / ZERO_DEMAND | No |
| coverage_target_days | INT | Policy target: A=30, B=45, C=60 days | No |
| safety_stock_units | DECIMAL(18,3) | From SAP MRP (MARC.EISBE) | No |
| ss_compliant | BIT | 1 if on_hand_units >= safety_stock_units | No |
| last_movement_date | DATE | Date of most recent stock movement (any type) | No |
| days_since_movement | INT | DATEDIFF(snapshot_date, last_movement_date) | No |
| is_obsolete | BIT | 1 if days_since_movement > 365 | No |
| is_excess | BIT | 1 if coverage_days > coverage_target_days | No |
| excess_value_cents | BIGINT | MAX(0, excess_days x adu_90d x unit_cost_cents) | No |
| has_open_demand | BIT | 1 if open sales order or demand forecast > 0 in next 30 days | No |
| abc_class | CHAR(1) | A / B / C from ABC classification engine | No |
| xyz_class | CHAR(1) | X / Y / Z from XYZ classification engine | No |
| abc_xyz_cell | NVARCHAR(2) | AX / AY / AZ / BX / BY / BZ / CX / CY / CZ | No |

**Granularity:** One row per MATNR + WERKS + LGORT + snapshot_date
**Partitioning:** By snapshot_date (monthly)
**Transformations:** coverage_days capped at 999 for display; NULL when adu_90d = 0
**Cleaning:** Negative LABST values set to 0 with error logged to dq_error_log
**Validations:** on_hand_value_cents = ROUND(on_hand_units x unit_cost_cents, 0), tolerance ±1 cent

---

### Table: fact_stock_movements

| Field | Type | Description | PK |
|---|---|---|---|
| movement_id | BIGINT IDENTITY | Surrogate primary key | Yes |
| doc_number | NVARCHAR(10) | SAP material document (MBLNR) | No |
| doc_year | CHAR(4) | Material document year (MJAHR) | No |
| doc_line | NVARCHAR(4) | Document line (ZEILE) | No |
| posting_date | DATE | SAP posting date (BUDAT) | No |
| sku_id | NVARCHAR(40) | SAP material number (MATNR) | No |
| plant_code | NVARCHAR(4) | SAP plant (WERKS) | No |
| storage_location | NVARCHAR(4) | SAP storage location (LGORT) | No |
| movement_type_code | NVARCHAR(3) | SAP movement type (BWART) | No |
| movement_category | NVARCHAR(30) | Analytical category: GOODS_RECEIPT / GOODS_ISSUE / TRANSFER / ADJUSTMENT / SCRAP / RETURN | No |
| quantity_units | DECIMAL(18,3) | Always positive; direction from movement_category | No |
| unit_cost_cents | BIGINT | Unit cost at time of movement (integer cents) | No |
| total_value_cents | BIGINT | quantity_units x unit_cost_cents (integer cents) | No |
| reference_doc | NVARCHAR(20) | PO number, SO number, or internal reference | No |
| is_reversal | BIT | 1 if this movement reverses a prior document | No |
| reversal_doc | NVARCHAR(10) | Original document number if is_reversal = 1 | No |

**Granularity:** One row per SAP material document line
**Retention:** 36 months rolling
**Transformations:** movement_category derived from BWART mapping table; reversals flagged by SAP reversal indicator
**Cleaning:** Zero-quantity movements filtered out; backdated postings (> 90 days prior) flagged in dq_error_log

---

### Table: dim_material

| Field | Type | Description |
|---|---|---|
| sku_id | NVARCHAR(40) | SAP MATNR — primary key, immutable |
| gtin | NVARCHAR(14) | GS1 GTIN-14 with validated check digit |
| description | NVARCHAR(200) | Material description (English) |
| material_type | NVARCHAR(4) | SAP MTART: ROH, FERT, HALB, HIBE, VERP |
| material_group | NVARCHAR(9) | SAP MATKL — product hierarchy node |
| base_uom | NVARCHAR(3) | GS1 UOM code: EA, KG, LT, M, etc. |
| gross_weight_kg | DECIMAL(12,3) | SAP BRGEW in KG |
| volume_m3 | DECIMAL(12,6) | SAP VOLUM converted to cubic metres |
| storage_condition | NVARCHAR(20) | AMBIENT / CHILLED / FROZEN / CONTROLLED |
| lot_tracked | BIT | 1 if lot tracking required |
| reach_svhc | BIT | 1 if EU REACH Art.57 SVHC |
| hazmat_class | NVARCHAR(10) | IMDG/ADR class or NULL |
| abc_class | CHAR(1) | A / B / C — refreshed monthly |
| xyz_class | CHAR(1) | X / Y / Z — refreshed monthly |
| coverage_target_days | INT | Policy target: A=30, B=45, C=60 days |
| status | NVARCHAR(15) | ACTIVE / DISCONTINUED / BLOCKED |
| is_deleted | BIT | Soft-delete flag — never physically removed |
| created_date | DATE | Date material master created in SAP |
| last_updated_date | DATE | Date of last master data change |

---

### Table: fact_cycle_counts

| Field | Type | Description | PK |
|---|---|---|---|
| count_id | BIGINT IDENTITY | Surrogate primary key | Yes |
| count_doc | NVARCHAR(10) | SAP inventory document (IVNR) | No |
| count_date | DATE | Physical count date (IDATU) | No |
| sku_id | NVARCHAR(40) | SAP MATNR | No |
| warehouse_code | NVARCHAR(3) | SAP warehouse number (LGNUM) | No |
| storage_type | NVARCHAR(3) | SAP storage type (LGTYP) | No |
| storage_bin | NVARCHAR(10) | SAP storage bin (LGPLA) | No |
| system_qty | DECIMAL(18,3) | Book stock at time of count (ANZLI) | No |
| counted_qty | DECIMAL(18,3) | Physical count result (ANZPH) | No |
| variance_qty | DECIMAL(18,3) | counted_qty - system_qty | No |
| variance_value_cents | BIGINT | variance_qty x unit_cost_cents (integer cents) | No |
| accuracy_flag | BIT | 1 if ABS(variance_qty) = 0 | No |
| recount_performed | BIT | 1 if a blind recount was triggered | No |
| adjustment_posted | BIT | 1 if adjustment movement was posted | No |
| abc_class | CHAR(1) | ABC class at time of count | No |

---

### Table: dim_safety_stock

| Field | Type | Description |
|---|---|---|
| ss_id | BIGINT IDENTITY | Surrogate primary key |
| sku_id | NVARCHAR(40) | SAP MATNR |
| plant_code | NVARCHAR(4) | SAP WERKS |
| safety_stock_units | DECIMAL(18,3) | SAP MARC.EISBE |
| reorder_point_units | DECIMAL(18,3) | SAP MARC.MINBE |
| mrp_type | NVARCHAR(2) | SAP MARC.DISMM |
| planned_delivery_days | INT | SAP MARC.PLIFZ |
| valid_from_date | DATE | Date of extract (weekly) |
| ss_method | NVARCHAR(10) | Method 1 / Method 3 / Method 4 per ABC class policy |

---

## 8. Transformation Rules

**TR-01 — ADU Calculation (90-Day Rolling Average Daily Usage)**
Extract all GOODS_ISSUE, SCRAP, and RETURN_TO_SUPPLIER movements from fact_stock_movements for each
SKU-plant combination over the 90 calendar days preceding the snapshot date. Sum total quantity issued.
Divide by 90. Exclude reversal movements (is_reversal = 1). Store in fact_inventory_snapshot.adu_90d.

**TR-02 — Coverage Days Calculation**
coverage_days = on_hand_units / adu_90d. If adu_90d = 0, set coverage_days = NULL and flag
is_zero_demand = 1. Cap display value at 999 for readability. Do not cap the stored value.

**TR-03 — Coverage Bucket Assignment**
Assign coverage_bucket based on coverage_days thresholds and ABC class:
- coverage_days < 7: CRITICAL (all classes)
- coverage_days 7–13: WARNING (all classes)
- A class: 14–30 = HEALTHY, > 30 = EXCESS
- B class: 14–45 = HEALTHY, > 45 = EXCESS
- C class: 14–60 = HEALTHY, > 60 = EXCESS
- coverage_days NULL: ZERO_DEMAND

**TR-04 — On-Hand Value Calculation**
on_hand_value_cents = ROUND(on_hand_units x unit_cost_cents, 0). Use moving average price (VERPR)
for materials with price control V; use standard price (STPRS) for price control S. Store as BIGINT.

**TR-05 — Excess Inventory Value Calculation**
excess_value_cents = MAX(0, (coverage_days - coverage_target_days) x adu_90d x unit_cost_cents).
Apply only where coverage_days is not NULL and is_obsolete = 0. For zero-demand items with on-hand
stock and days_since_movement < 365, classify as excess with coverage_days = 999 sentinel value.

**TR-06 — Obsolete Inventory Flag**
is_obsolete = 1 where last_movement_date < snapshot_date - 365 AND on_hand_units > 0.
last_movement_date = MAX(posting_date) from fact_stock_movements for the SKU-plant-location,
considering all movement types including adjustments and transfers.

**TR-07 — Safety Stock Compliance Flag**
ss_compliant = 1 where on_hand_units >= safety_stock_units. Load safety_stock_units from
dim_safety_stock (weekly refresh from SAP MARC.EISBE). Where EISBE = 0 for an A or B class
item, flag as SS_NOT_MAINTAINED in a separate data quality report.

**TR-08 — ABC Classification (Monthly Refresh)**
Compute Annual Consumption Value (ACV) = adu_90d x 365 x unit_cost_cents for each active SKU-plant.
Rank descending by ACV. Compute cumulative value share. Assign A (0–80%), B (80–95%), C (95–100%).
Run monthly on the first calendar day of each month. Write results to dim_material.abc_class.

**TR-09 — XYZ Classification (Monthly Refresh)**
Compute 12 weekly demand buckets for each active SKU-plant from fact_stock_movements. Calculate
CV = std_dev(weekly_demand) / mean(weekly_demand). Assign X (CV < 0.10), Y (0.10 <= CV < 0.25),
Z (CV >= 0.25). For SKUs with fewer than 12 weeks of demand history, assign Z and flag as
INSUFFICIENT_HISTORY. Run concurrently with ABC refresh.

**TR-10 — E&O Ratio Calculation**
E&O_ratio_pct = (SUM(excess_value_cents WHERE is_excess = 1) + SUM(on_hand_value_cents WHERE
is_obsolete = 1)) / SUM(on_hand_value_cents WHERE status = 'ACTIVE') x 100.
Calculated at plant, region, and enterprise level.

**TR-11 — Cycle Count Accuracy Rate**
accuracy_rate_pct = COUNT(*) WHERE accuracy_flag = 1 / COUNT(*) x 100. Calculated by warehouse,
storage_type, abc_class, and count_date for daily, weekly, and monthly aggregations.

**TR-12 — Shortage Rate Calculation**
shortage_rate_pct = COUNT(DISTINCT sku_id) WHERE on_hand_units = 0 AND status = 'ACTIVE' AND
has_open_demand = 1 / COUNT(DISTINCT sku_id WHERE status = 'ACTIVE') x 100.
Open demand loaded daily from SAP MD04 stock requirements list.

**TR-13 — Inventory Turnover Ratio (Trailing 12 Months)**
turnover_ratio = SUM(total_value_cents WHERE movement_category IN ('GOODS_ISSUE','SCRAP') AND
posting_date >= snapshot_date - 365) / AVG(on_hand_value_cents aggregated by month for prior 12
months). Calculated at enterprise, region, plant, and material group levels.

**TR-14 — DIO (Days Inventory Outstanding)**
DIO = 365 / turnover_ratio. Where turnover_ratio = 0, set DIO = NULL. DIO is the primary
working capital KPI for executive reporting.

**TR-15 — Last Movement Date Derivation**
last_movement_date = MAX(posting_date) from fact_stock_movements for sku_id + plant_code +
storage_location. Includes all movement types. Refreshed daily with each snapshot load.

---

## 9. Business Rules

### BR-01: No Negative Inventory

| Attribute | Detail |
|---|---|
| Name | No Negative Inventory |
| Description | On-hand stock quantity must never be negative for items where backorder is not explicitly allowed |
| Logic Condition | IF on_hand_units < 0 AND backorder_allowed = FALSE THEN raise data quality error |
| Expected Result | on_hand_units >= 0 for all active SKUs where backorder_allowed = FALSE |
| Example | SKU MAT-00123, Plant DE01: LABST = -5 EA triggers data quality alert; record excluded from health KPIs pending investigation |
| Exception | Items with backorder_allowed = TRUE may show negative stock during the replenishment pipeline; these are flagged separately as BACKORDER not SHORTAGE |
| Evidence | CLAUDE.md Critical Business Rule #1; SAP configuration: negative stock check active in plant parameters |

### BR-02: Soft-Delete Only

| Attribute | Detail |
|---|---|
| Name | Soft-Delete Only |
| Description | No inventory records, stock movements, cycle count documents, or material master records may be physically deleted |
| Logic Condition | is_deleted = TRUE is the only permitted deletion mechanism; hard DELETE statements blocked at database layer |
| Expected Result | All historical records preserved; reports filter on is_deleted = FALSE by default |
| Example | Obsolete material MAT-99999 is discontinued: MARC.MMSTA set to X (blocked); is_deleted = FALSE until physical scrapping is complete |
| Exception | Test data in non-production environments may be hard-deleted by IT administrators only |
| Evidence | CLAUDE.md Critical Business Rule #3; Azure SQL row-level security policy |

### BR-03: Coverage Target Days by ABC Class

| Attribute | Detail |
|---|---|
| Name | Coverage Target Days by ABC Class |
| Description | Maximum acceptable coverage days varies by ABC classification; excess is defined as coverage above target |
| Logic Condition | A class: target = 30 days; B class: target = 45 days; C class: target = 60 days |
| Expected Result | SKUs with coverage_days > target are flagged is_excess = TRUE and excess_value_cents calculated |
| Example | SKU MAT-00456 (Class A): coverage_days = 65; excess_days = 35; excess_value_cents = 35 x adu x unit_cost |
| Exception | Items with seasonal demand may have target days extended by 30% during pre-season buffer build (controlled by seasonal_flag in dim_material) |
| Evidence | Chopra & Meindl, Supply Chain Management 6th Ed., Chapter 11 |

### BR-04: Obsolete Inventory Threshold

| Attribute | Detail |
|---|---|
| Name | Obsolete Inventory Threshold |
| Description | Inventory with no stock movement for 365+ calendar days is classified as obsolete regardless of ABC class or value |
| Logic Condition | is_obsolete = 1 WHERE last_movement_date < TODAY() - 365 AND on_hand_units > 0 |
| Expected Result | Obsolete items flagged in dashboard with disposition workflow triggered |
| Example | SKU MAT-07890, Plant FR01: last movement 2024-12-15; snapshot date 2026-06-22; days_since_movement = 554; is_obsolete = TRUE |
| Exception | Items on long-term strategic reserve approved by VP Supply Chain with documented business justification may have threshold extended to 730 days |
| Evidence | GAAP/IFRS IAS 2 inventory write-down requirements; Financial Control Policy §7.3 |

### BR-05: Safety Stock Maintenance Mandatory for A and B Class

| Attribute | Detail |
|---|---|
| Name | Safety Stock Maintenance Mandatory |
| Description | All A and B class active SKUs must have a non-zero safety stock level maintained in SAP MRP |
| Logic Condition | IF abc_class IN ('A','B') AND status = 'ACTIVE' AND EISBE = 0 THEN flag SS_NOT_MAINTAINED |
| Expected Result | Zero SS_NOT_MAINTAINED flags for A and B class items in steady state |
| Example | SKU MAT-00321 (Class A, Plant GB01): EISBE = 0; flagged in weekly data quality report; owner assigned to update within 5 business days |
| Exception | Items with MRP type ND (no planning) are exempt but must have an approved documented rationale |
| Evidence | SCOR-DS Plan process; Chopra & Meindl Ch.11 |

### BR-06: Cycle Count Frequency by ABC Class

| Attribute | Detail |
|---|---|
| Name | Cycle Count Frequency |
| Description | Minimum cycle count frequency enforced by ABC class |
| Logic Condition | A class: weekly (7 days); B class: monthly (31 days); C class: quarterly (92 days) |
| Expected Result | All active SKU-locations counted at required frequency; overdue counts flagged in dashboard |
| Example | SKU MAT-00789 (Class A, Bin A01-001-02): last count date 2026-05-15; today 2026-06-22; overdue by 3 weeks; alert raised to warehouse manager |
| Exception | Items in quarantine status are counted at time of release, not on standard schedule |
| Evidence | ISO 9001:2015 §8.5.2; internal Inventory Control Procedure ICP-001 |

### BR-07: Lot Tracking Mandatory for Non-Ambient and REACH SVHC

| Attribute | Detail |
|---|---|
| Name | Lot Tracking Mandatory |
| Description | Lot tracking is mandatory for all items where storage condition is not AMBIENT or where reach_svhc = TRUE |
| Logic Condition | IF (storage_condition != 'AMBIENT' OR reach_svhc = TRUE) AND lot_tracked = FALSE THEN compliance breach |
| Expected Result | Zero items failing this rule in production |
| Example | SKU MAT-05511 (CHILLED, reach_svhc = FALSE): lot_tracked must = TRUE; if FALSE, blocked from GOODS_RECEIPT posting |
| Exception | None permitted — this is a regulatory requirement under EU REACH 1907/2006 and ISO 9001:2015 §8.5.2 |
| Evidence | CLAUDE.md Critical Business Rule #5; EU REACH 1907/2006 |

### BR-08: All Stock Movements Generate GL Journal Entry

| Attribute | Detail |
|---|---|
| Name | GL Journal Generation Mandatory |
| Description | Every stock movement must generate a corresponding debit/credit GL journal entry |
| Logic Condition | IF StockMovement posted AND GL journal NOT generated THEN error; retry within 60 seconds |
| Expected Result | 100% of movements have a corresponding GL journal posted to ERP |
| Example | GOODS_RECEIPT movement: debit GL 1310 (Inventory), credit GL 2100 (GR-IR clearing) |
| Exception | Transfers between storage locations within the same GL cost centre may generate zero-value journals (still required) |
| Evidence | CLAUDE.md Critical Business Rule #4; internal Financial Control Policy §5.1 |

---

## 10. KPIs and Formulas

All KPIs are calculated daily unless otherwise noted. DAX formulas are for Power BI Desktop.
SQL formulas target Azure SQL DW.

### KPI-01: Inventory Coverage Days

**Definition:** Number of days of supply available given current on-hand stock and 90-day ADU.

**Formula:**
```
Coverage_Days = On_Hand_Units / ADU_90d
ADU_90d = SUM(goods_issue_units, trailing 90 days) / 90
```

**DAX:**
```dax
Coverage Days =
VAR ADU =
    DIVIDE(
        CALCULATE(
            SUM(fact_stock_movements[quantity_units]),
            fact_stock_movements[movement_category] IN {"GOODS_ISSUE","SCRAP"},
            DATESINPERIOD(dim_date[date_id], MAX(dim_date[date_id]), -90, DAY)
        ),
        90
    )
RETURN DIVIDE([On Hand Units], ADU, BLANK())
```

**SQL:**
```sql
SELECT
    s.sku_id, s.plant_code, s.snapshot_date,
    s.on_hand_units,
    COALESCE(m.total_issued / 90.0, 0)                         AS adu_90d,
    CASE
        WHEN COALESCE(m.total_issued, 0) = 0 THEN NULL
        ELSE s.on_hand_units / (m.total_issued / 90.0)
    END                                                         AS coverage_days
FROM fact_inventory_snapshot s
LEFT JOIN (
    SELECT sku_id, plant_code,
           SUM(quantity_units) AS total_issued
    FROM fact_stock_movements
    WHERE movement_category IN ('GOODS_ISSUE','SCRAP')
      AND posting_date >= DATEADD(DAY, -90, GETDATE())
      AND is_reversal = 0
    GROUP BY sku_id, plant_code
) m ON s.sku_id = m.sku_id AND s.plant_code = m.plant_code
WHERE s.snapshot_date = CAST(GETDATE() AS DATE);
```

---

### KPI-02: Inventory Turnover Ratio

**Definition:** Number of times inventory is consumed in a trailing 12-month period.

**Formula:**
```
Turnover_Ratio = COGS_trailing_12m_cents / Avg_Inventory_Value_12m_cents
```

**DAX:**
```dax
Inventory Turnover =
VAR COGS =
    CALCULATE(
        SUM(fact_stock_movements[total_value_cents]),
        fact_stock_movements[movement_category] IN {"GOODS_ISSUE","SCRAP"},
        DATESINPERIOD(dim_date[date_id], MAX(dim_date[date_id]), -365, DAY)
    )
VAR AvgInv =
    AVERAGEX(
        VALUES(dim_date[fiscal_month]),
        CALCULATE(SUM(fact_inventory_snapshot[on_hand_value_cents]))
    )
RETURN DIVIDE(COGS, AvgInv, BLANK())
```

---

### KPI-03: Days Inventory Outstanding (DIO)

**Formula:**
```
DIO = 365 / Inventory_Turnover_Ratio
```

**DAX:**
```dax
DIO Days = DIVIDE(365, [Inventory Turnover], BLANK())
```

**Target:** DIO < 45 days for finished goods. Alert threshold: DIO > 60 days triggers working capital review.

---

### KPI-04: Excess Inventory Value

**Formula:**
```
Excess_Value_cents = MAX(0,
    (Coverage_Days - Coverage_Target_Days) x ADU_90d x Unit_Cost_cents)
```

**DAX:**
```dax
Excess Inventory Value EUR =
SUMX(
    fact_inventory_snapshot,
    VAR ExcessDays =
        MAX(0,
            fact_inventory_snapshot[coverage_days]
            - RELATED(dim_material[coverage_target_days])
        )
    RETURN
        ExcessDays
        * fact_inventory_snapshot[adu_90d]
        * DIVIDE(fact_inventory_snapshot[unit_cost_cents], 100)
)
```

---

### KPI-05: Obsolete Inventory Value

**Formula:**
```
Obsolete_Value_cents = SUM(on_hand_value_cents) WHERE is_obsolete = 1
```

**DAX:**
```dax
Obsolete Inventory EUR =
CALCULATE(
    SUMX(
        fact_inventory_snapshot,
        DIVIDE(fact_inventory_snapshot[on_hand_value_cents], 100)
    ),
    fact_inventory_snapshot[is_obsolete] = 1
)
```

---

### KPI-06: E&O Ratio

**Formula:**
```
E&O_Ratio_pct = (Excess_Value_cents + Obsolete_Value_cents)
                / Total_Active_Inventory_Value_cents x 100
```

**DAX:**
```dax
E&O Ratio % =
DIVIDE(
    [Excess Inventory Value EUR] + [Obsolete Inventory EUR],
    DIVIDE(
        CALCULATE(
            SUM(fact_inventory_snapshot[on_hand_value_cents]),
            dim_material[status] = "ACTIVE"
        ),
        100
    ),
    0
) * 100
```

**Target:** E&O Ratio < 5%. Alert: > 8% triggers executive review. World-class: < 2%.

---

### KPI-07: Shortage Rate

**Formula:**
```
Shortage_Rate_pct =
    COUNT(DISTINCT sku_id WHERE on_hand_units = 0 AND has_open_demand = 1)
    / COUNT(DISTINCT sku_id WHERE status = 'ACTIVE') x 100
```

**DAX:**
```dax
Shortage Rate % =
VAR ShortageSKUs =
    CALCULATE(
        DISTINCTCOUNT(fact_inventory_snapshot[sku_id]),
        fact_inventory_snapshot[on_hand_units] = 0,
        fact_inventory_snapshot[has_open_demand] = 1
    )
VAR TotalActive =
    CALCULATE(
        DISTINCTCOUNT(fact_inventory_snapshot[sku_id]),
        dim_material[status] = "ACTIVE"
    )
RETURN DIVIDE(ShortageSKUs, TotalActive, 0) * 100
```

**Target:** Shortage Rate < 0.5%. Alert: > 2% for A-class items.

---

### KPI-08: Cycle Count Accuracy

**Formula:**
```
Cycle_Count_Accuracy_pct =
    COUNT(counts WHERE ABS(variance_qty) = 0)
    / COUNT(all counts) x 100
```

**DAX:**
```dax
Cycle Count Accuracy % =
DIVIDE(
    CALCULATE(COUNTROWS(fact_cycle_counts), fact_cycle_counts[accuracy_flag] = 1),
    COUNTROWS(fact_cycle_counts),
    0
) * 100
```

**SQL:**
```sql
SELECT
    warehouse_code,
    abc_class,
    COUNT(*)                                                           AS total_counts,
    SUM(CAST(accuracy_flag AS INT))                                    AS accurate_counts,
    100.0 * SUM(CAST(accuracy_flag AS INT)) / COUNT(*)                AS accuracy_rate_pct
FROM fact_cycle_counts
WHERE count_date >= DATEADD(MONTH, -1, GETDATE())
GROUP BY warehouse_code, abc_class
ORDER BY accuracy_rate_pct ASC;
```

**Target:** Overall >= 99.5%. A-class >= 99.9%. Alert: < 98% for any warehouse triggers investigation.

---

### KPI-09: Safety Stock Compliance Rate

**Formula:**
```
SS_Compliance_pct =
    COUNT(DISTINCT sku_id WHERE on_hand_units >= safety_stock_units)
    / COUNT(DISTINCT sku_id WHERE safety_stock_units > 0) x 100
```

**DAX:**
```dax
Safety Stock Compliance % =
VAR Compliant =
    CALCULATE(
        DISTINCTCOUNT(fact_inventory_snapshot[sku_id]),
        fact_inventory_snapshot[ss_compliant] = 1,
        fact_inventory_snapshot[safety_stock_units] > 0
    )
VAR WithSS =
    CALCULATE(
        DISTINCTCOUNT(fact_inventory_snapshot[sku_id]),
        fact_inventory_snapshot[safety_stock_units] > 0
    )
RETURN DIVIDE(Compliant, WithSS, 0) * 100
```

**Target:** >= 90% overall. >= 97% for A-class items.

---

## 11. Analytical Logic

### Coverage Day Buckets

Coverage days determine the health classification of each SKU-location. Thresholds:

| Bucket | Coverage Days | Colour | Action |
|---|---|---|---|
| CRITICAL | < 7 days | Red | Immediate replenishment; escalate to planner same day |
| WARNING | 7–13 days | Amber | Expedite open PO or raise emergency order |
| HEALTHY (A) | 14–30 days | Green | No action required |
| HEALTHY (B) | 14–45 days | Green | No action required |
| HEALTHY (C) | 14–60 days | Green | No action required |
| EXCESS (A) | > 30 days | Blue | Investigate; defer next PO |
| EXCESS (B) | > 45 days | Blue | Investigate; defer next PO |
| EXCESS (C) | > 60 days | Blue | Investigate; defer next PO |
| ZERO_DEMAND | NULL (ADU = 0) | Grey | Review for obsolescence or discontinuation |

For items with seasonal demand profile, the HEALTHY upper threshold is extended by 50% during the
4-week pre-season buffer build period (controlled by dim_date.pre_season_flag = 1).

### ABC Velocity Segmentation

ABC classification based on Annual Consumption Value (ACV) from 90-day ADU projected to 365 days:

| Class | Cumulative ACV Share | Typical SKU Count | Policy |
|---|---|---|---|
| A | 0–80% | ~15–20% of SKUs | Continuous review, Method 4 SS, weekly count |
| B | 80–95% | ~25–30% of SKUs | Periodic review (2 weeks), Method 3 SS, monthly count |
| C | 95–100% | ~50–60% of SKUs | Periodic review (4 weeks), Method 1 SS, quarterly count |

### XYZ Demand Variability Segmentation

XYZ classification uses the 12-week coefficient of variation (CV):

| Class | CV Range | Demand Pattern | Forecasting Method |
|---|---|---|---|
| X | CV < 0.10 | Stable, predictable | SMA or SES sufficient |
| Y | 0.10 <= CV < 0.25 | Moderate variability | Holt or Holt-Winters |
| Z | CV >= 0.25 | Erratic, intermittent | Newsvendor or min-max |

### ABC-XYZ 9-Cell Policy Matrix

| | X (Stable) | Y (Variable) | Z (Erratic) |
|---|---|---|---|
| **A (High Value)** | Continuous review, Method 4 SS, 99% CSL | Continuous review, Holt forecast, Method 4, 99% CSL | Continuous review, Newsvendor, dual-source, 98% CSL |
| **B (Medium Value)** | Periodic 2-week, Method 3 SS, EOQ, 97% CSL | Periodic 2-week, SES forecast, Method 3, 97% CSL | Min-max wide bands, manual oversight, 95% CSL |
| **C (Low Value)** | Periodic 4-week, Method 1 SS, bulk buy, 95% CSL | Periodic 4-week, min-max replenishment, 95% CSL | On-demand or kanban; review for rationalisation |

### Inventory Aging Buckets

All on-hand inventory is assigned to an aging bucket based on days since last goods receipt:

| Aging Bucket | Days Since Last Receipt | Financial Risk | Action |
|---|---|---|---|
| FRESH | 0–30 days | None | Normal management |
| RECENT | 31–90 days | Low | Monitor |
| AGING | 91–180 days | Medium | Demand review |
| OLD | 181–365 days | High | Disposition review required |
| OBSOLETE | > 365 days | Critical | Write-down assessment; mandatory disposition |

### E&O Disposition Alert Logic

When a SKU is flagged as excess or obsolete the following disposition workflow is triggered:

1. **Day 1:** Automatic email alert to plant inventory controller and regional demand planner
2. **Day 7:** If no disposition entered, second alert with financial exposure highlighted
3. **Day 14:** No disposition escalates to Supply Chain Director
4. **Day 30:** Finance Controller accrues provision: 50% of obsolete value, 20% of excess value
5. **Day 90:** Automatic write-down recommendation raised to CFO for IFRS IAS 2 compliance

### Safety Stock Violation Alert Priority

| ABC Class | SS Violation Duration | Priority | Alert Recipient |
|---|---|---|---|
| A | Same day | P1 — Critical | Planner + Plant Manager + SC Director |
| B | > 2 consecutive days | P2 — High | Planner + Inventory Controller |
| C | > 7 consecutive days | P3 — Medium | Inventory Controller |
| Any class | > 14 consecutive days | P2 — Escalated | Regional Supply Chain Manager |

---

## 12. Validations and Controls

### VC-01: Non-Negative On-Hand Stock

| Attribute | Detail |
|---|---|
| Name | Non-Negative On-Hand Stock |
| Field/Table | fact_inventory_snapshot.on_hand_units |
| Rule | on_hand_units >= 0 for all rows |
| Method | Pre-load SQL CHECK constraint + ADF pipeline data quality activity |
| Expected Result | Zero rows with on_hand_units < 0 in production load |
| Action if Fails | Row quarantined to dq_error_log; SAP inventory controller notified; excluded from KPIs |
| Evidence | BR-01; CLAUDE.md Critical Business Rule #1 |

### VC-02: On-Hand Value Reconciliation

| Attribute | Detail |
|---|---|
| Name | On-Hand Value Reconciliation |
| Field/Table | fact_inventory_snapshot.on_hand_value_cents |
| Rule | ABS(on_hand_value_cents - ROUND(on_hand_units x unit_cost_cents, 0)) <= 1 cent |
| Method | Post-load SQL validation query; daily reconciliation report |
| Expected Result | < 0.01% of rows with value discrepancy > 1 cent |
| Action if Fails | Investigate price control mismatch (V vs S); restate value using correct price |
| Evidence | Financial Control Policy §4.2; IFRS IAS 2 |

### VC-03: ADU Non-Zero for A-Class Active SKUs

| Attribute | Detail |
|---|---|
| Name | ADU Reasonableness for A-Class |
| Field/Table | fact_inventory_snapshot.adu_90d |
| Rule | A-class items must have adu_90d > 0 |
| Method | Post-load validation query; A-class zero-ADU flagged in DQ report |
| Expected Result | Zero A-class items with ADU = 0 in steady state |
| Action if Fails | Review if item was recently reclassified or demand ceased; reclassify to C if confirmed |
| Evidence | TR-01; BR-05 |

### VC-04: Safety Stock Maintained for A/B Class

| Attribute | Detail |
|---|---|
| Name | Safety Stock Completeness |
| Field/Table | dim_safety_stock.safety_stock_units |
| Rule | safety_stock_units > 0 for all active A and B class SKUs |
| Method | Weekly validation query post-SAP extract |
| Expected Result | Zero A/B class items with safety_stock_units = 0 after Week 4 of implementation |
| Action if Fails | Alert to Demand Planning team; SLA: corrected within 5 business days |
| Evidence | BR-05; CLAUDE.md |

### VC-05: Cycle Count Coverage Completeness

| Attribute | Detail |
|---|---|
| Name | Cycle Count Coverage |
| Field/Table | fact_cycle_counts |
| Rule | All A-class SKU-locations counted within 7 days; B within 31 days; C within 92 days |
| Method | Daily query: days since last count vs. frequency threshold per ABC class |
| Expected Result | < 1% of A-class locations overdue at any time |
| Action if Fails | Warehouse manager notified; count added to next-day schedule |
| Evidence | BR-06; ISO 9001:2015 §8.5.2 |

### VC-06: Lot Tracking Flag Completeness

| Attribute | Detail |
|---|---|
| Name | Lot Tracking Flag Completeness |
| Field/Table | dim_material.lot_tracked |
| Rule | lot_tracked = TRUE for all active SKUs where storage_condition != 'AMBIENT' OR reach_svhc = TRUE |
| Method | Weekly validation query against dim_material |
| Expected Result | Zero non-compliant items |
| Action if Fails | Master data steward alerted; item blocked from receipt until corrected |
| Evidence | BR-07; EU REACH 1907/2006; ISO 9001:2015 §8.5.2 |

### VC-07: Movement Type Mapping Completeness

| Attribute | Detail |
|---|---|
| Name | SAP Movement Type Mapping |
| Field/Table | fact_stock_movements.movement_category |
| Rule | All SAP BWART codes present in the movement type mapping table; movement_category must not be NULL |
| Method | Post-load check: COUNT(*) WHERE movement_category IS NULL |
| Expected Result | Zero unmapped movement types |
| Action if Fails | New movement type identified in SAP; add to mapping table and reprocess affected records |
| Evidence | TR-01; DS-02 |

---

## 13. Required Evidence

The following evidence artefacts must be produced and stored in the project SharePoint repository
before each phase milestone is signed off by the Data Governance Board:

1. **Data source connection test results:** Screenshot of successful ADF pipeline runs for all six
   data sources with row counts and checksums matching SAP control totals for 3 consecutive days.

2. **Data quality baseline report:** Results of VC-01 through VC-07 validations against the first
   30 days of production data, showing pass/fail rates and open remediation items with owners.

3. **ABC/XYZ classification audit:** Excel export of all active SKUs with ABC and XYZ classifications
   for the first monthly run, reviewed and signed off by the Inventory Control Manager.

4. **E&O financial exposure report:** First E&O report showing excess and obsolete values reconciled
   to SAP financial statements (MBEW values), reviewed and signed off by the Finance Controller.

5. **Safety stock compliance baseline:** Report showing SS compliance rate by plant and ABC class
   for the first week of data, with action log for items failing BR-05.

6. **Cycle count accuracy baseline:** First month's cycle count accuracy report by warehouse and
   ABC class, reconciled against SAP transaction MI23 summary report within 0.5%.

7. **Power BI UAT sign-off:** User acceptance testing evidence from at least three inventory
   controllers and one regional supply chain manager confirming KPI accuracy against source system.

8. **CSDDD data retention evidence:** Confirmation that E&O and inventory adjustment records are
   retained for minimum 5 years per Article 23 of EU Directive 2024/1760 (CSDDD).

---

## 14. Dashboard Design

### Power BI Report Structure

**Report File:** Inventory_Health_Analytics.pbix
**Refresh Schedule:** Daily at 06:00 CET (after ADF pipeline completion at 05:30 CET)
**Row-Level Security:** Plant-level RLS; regional managers see their plants only; Global SCM team sees all
**Data Source:** Azure SQL DW via DirectQuery (fact tables) + Import (dim tables)

---

### Page 1: Executive Inventory Health Overview

**Purpose:** Single-page senior leadership view of inventory health and E&O exposure.

**Visuals:**
- KPI cards (top row, 5 cards): Total Inventory Value (€M), DIO (days), Turnover Ratio, E&O Ratio (%), Shortage Rate (%)
- Clustered bar chart: On-hand value by coverage bucket (CRITICAL / WARNING / HEALTHY / EXCESS) per region
- Treemap: E&O value by product category and plant (size = value, colour = E&O ratio)
- Line chart: DIO trend — current month vs. prior 12 months with target reference line at 45 days
- Table: Top 20 excess inventory SKUs — columns: SKU, description, plant, excess value (€), coverage days, last movement date

**Slicers:** Region, Country, Plant, Material Group, ABC Class, Snapshot Date (date picker)
**Drill-down:** Click region bar to plant breakdown; click plant to SKU detail

---

### Page 2: Coverage and Shortage Analysis

**Purpose:** Operational view for inventory planners to manage shortage risk.

**Visuals:**
- Matrix: Coverage bucket count by plant x ABC class (conditional formatting: red = CRITICAL, amber = WARNING)
- Scatter plot: Coverage days (Y-axis) vs. ADU units/day (X-axis); bubble size = on_hand_value; colour = coverage bucket
- Table: CRITICAL and WARNING SKUs — columns: SKU, description, plant, on_hand_units, ADU, coverage_days, open_PO_qty, open_PO_ETA, shortage_risk_value_eur
- KPI card: Count of A-class SKUs in CRITICAL bucket (target = 0)
- Bar chart: Shortage rate % by week (trailing 13 weeks)

**Slicers:** Plant, ABC Class, Material Group, Supplier
**Actions:** Export button for shortage list (CSV for planner action in SAP MD04)

---

### Page 3: Excess and Obsolete Inventory

**Purpose:** Working capital management view for supply chain finance and planners.

**Visuals:**
- Gauge: E&O Ratio % vs. target 5% and alert 8%
- Clustered bar chart: Excess value by plant and ABC class (stacked: excess vs. obsolete)
- Bar chart: Obsolete value by aging bucket (181–365 days, > 365 days) and plant
- Waterfall chart: E&O value change month-over-month (green bars = dispositions actioned, red bars = new additions)
- Table: Top 50 E&O items — SKU, description, plant, ABC class, excess_value (€), obsolete_value (€), last_movement_date, days_since_movement, disposition_status
- KPI cards: Total Excess Value (€M), Total Obsolete Value (€M), Items Pending Disposition (count), Items Overdue for Disposition (> 14 days)

**Slicers:** Region, Plant, Material Group, ABC Class, Days Since Movement Range
**Drill-through:** Click SKU to movement history detail page

---

### Page 4: ABC/XYZ Segmentation

**Purpose:** Classification governance and policy compliance view.

**Visuals:**
- 9-cell matrix heatmap: Count and total value of SKUs in each ABC-XYZ cell (colour intensity = concentration risk)
- Dual-axis bar chart: Turnover ratio (bar) and E&O ratio (line) by ABC class
- Donut chart: Inventory value distribution by ABC class (A/B/C segments)
- Table: AZ class items (highest risk) — columns: SKU, plant, on_hand_value, coverage_days, ss_compliant, shortage_flag, last_review_date
- Line chart: ABC classification stability — % of SKUs that changed class in current month vs. prior 3 months

**Slicers:** Region, Plant, Material Type

---

### Page 5: Safety Stock Compliance

**Purpose:** Replenishment policy compliance monitoring.

**Visuals:**
- Gauge: Overall SS compliance rate % vs. target 90%
- Bar chart: SS compliance rate by plant and ABC class (sorted ascending — worst first in red)
- Table: SS violations — SKU, plant, on_hand_units, safety_stock_units, deficit_units, deficit_value (€), days_below_SS, abc_class, xyz_class
- Trend line: Weekly SS compliance rate by ABC class (trailing 13 weeks)
- KPI card: Count of A-class SKUs below SS (target = 0)

**Slicers:** Plant, ABC Class, Region, Week

---

### Page 6: Cycle Count Accuracy

**Purpose:** Inventory accuracy governance view for warehouse managers and inventory controllers.

**Visuals:**
- KPI cards: Overall accuracy %, A-class accuracy %, count variance value (€), overdue locations (count)
- Bar chart: Accuracy rate by warehouse (sorted ascending — worst first); red line at 99.5% target
- Heatmap matrix: Accuracy rate by storage_type (Y) x warehouse (X); colour gradient red–green
- Pareto chart: Top 20 SKUs by cumulative adjustment value (trailing 12 months)
- Table: Recent count variances — doc number, date, SKU, bin, system_qty, counted_qty, variance_qty, variance_value, recount_flag, adjustment_posted
- Line chart: Accuracy rate trend by week (trailing 26 weeks) with 99.5% and 99.9% reference lines

**Slicers:** Warehouse, ABC Class, Storage Type, Date Range

---

## 15. Use Cases

### UC-01: Pre-Quarter Working Capital Target Setting

**Scenario:** The CFO sets a target to reduce DIO from 58 days to 48 days by end of Q3 FY2026.
The Supply Chain Finance Director uses the analytics to identify which plants and SKUs to prioritise.

**Steps:**
1. Open Page 1 — Executive Overview; set snapshot date to current quarter start; all regions
2. Identify plants with DIO > 60 days on the scatter plot (bubble size = opportunity size)
3. Drill to Page 3 — Excess and Obsolete; filter by these plants
4. Export top 50 excess SKUs; assign to plant inventory controllers for disposition
5. Track weekly DIO trend on Page 1 against the 48-day quarterly target

**Outcome:** €180M excess inventory identified across 8 plants; disposition plan covering 60% of
excess agreed within 3 weeks; DIO reduced to 51 days by end of Q3.

---

### UC-02: Shortage Prevention for A-Class SKUs

**Scenario:** A production planner in Germany identifies that 12 A-class raw materials are entering
WARNING coverage bucket. Three are key active pharmaceutical ingredients with 45-day supplier lead time.

**Steps:**
1. Open Page 2 — Coverage and Shortage Analysis; filter Plant = DE01; ABC Class = A
2. Sort table by coverage_days ascending; identify 12 SKUs with coverage_days < 14
3. Check open_PO_qty and open_PO_ETA columns — 3 API items have no open PO
4. Escalate 3 API items to procurement for emergency order; export list to SAP MD04

**Outcome:** Emergency POs raised for 3 API items; premium freight cost €45K avoided production
stoppage valued at €2.1M. Demand-at-risk reduced from €2.3M to €0.2M within 5 days.

---

### UC-03: Cycle Count Discrepancy Root Cause Analysis

**Scenario:** Warehouse DE01 shows A-class cycle count accuracy of 97.2% in June 2026, below the
99.9% target. The Warehouse Manager needs to identify root cause.

**Steps:**
1. Open Page 6 — Cycle Count Accuracy; filter Warehouse = DE01; June 2026
2. Review Pareto chart: top discrepancy SKUs are concentrated in storage type 001 (high-bay racking)
3. Review heatmap: storage type 001, bins at levels 6+ show 89% accuracy vs. 99.5% at levels 1–4
4. Hypothesise: reach truck driver error at high levels; partial pallets in incorrect bins
5. Implement: visual bin labelling at levels 5–6; refresher training for 3 operators

**Outcome:** Accuracy for storage type 001 improved to 99.4% within 4 weeks after corrective action.

---

### UC-04: E&O Disposition Campaign

**Scenario:** Global Inventory Health Review (quarterly) identifies €85M in E&O inventory.
Supply Chain Director initiates a 90-day disposition campaign.

**Steps:**
1. Export Page 3 — Excess and Obsolete: full item list with recommended_disposition pre-populated
2. Assign items to regional inventory controllers via disposition workflow tool
3. Track weekly: waterfall chart shows disposition progress (green bars = items actioned)
4. Week 4: 30% actioned — markdown €15M, inter-plant transfer €8M, return to supplier €5M
5. Week 8: 65% actioned; remaining escalated to Supply Chain Director
6. Week 12: provision raised for remaining 35% (€30M) per financial control policy

**Outcome:** €58M of E&O liquidated within 90 days; E&O ratio reduced from 8.2% to 4.1%.

---

### UC-05: Monthly ABC/XYZ Reclassification Review

**Scenario:** Monthly ABC/XYZ refresh completes. 340 SKUs changed classification. 15 moved from C to A
(significant velocity increase). 28 moved from A to C (demand decline). Replenishment policies must
be updated for all reclassified items.

**Steps:**
1. Open Page 4 — ABC/XYZ Segmentation; review classification stability chart
2. Filter: changed_class_current_month = YES; export list
3. For 15 new A-class items: SS method changed to Method 4; count frequency changed to weekly
4. For 28 items moved to C: SS method changed to Method 1; count frequency changed to quarterly
5. SAP MRP parameters updated within 3 business days per SLA

**Outcome:** 340 SKUs realigned to correct replenishment policy; estimated €3.2M SS reduction
from former A-class items now correctly classified as C.

---

## 16. Recommended Actions

| Result | Recommended Action | Owner | Timeline |
|---|---|---|---|
| SKU in CRITICAL coverage bucket (< 7 days) | Raise emergency PO or expedite open PO; confirm supplier availability same day | Inventory Planner | Same business day |
| E&O Ratio > 8% | Initiate E&O disposition campaign; assign items to regional controllers; escalate to SC Director | Inventory Control Manager | Within 5 business days |
| A-class SKU below safety stock > 2 consecutive days | Review demand forecast accuracy; recalculate SS using Method 4; check supplier lead time variability | Demand Planner | Within 2 business days |
| Cycle count accuracy < 99% for A-class warehouse | Root cause analysis within 48 hours; implement corrective action plan within 5 days | Warehouse Manager | Within 48 hours |
| DIO > 60 days | Identify top 20 excess value SKUs; initiate disposition; defer next PO for excess items | SC Finance Director | Within 10 business days |
| Obsolete inventory > 5% of total value | Escalate to Finance Controller for IFRS IAS 2 write-down assessment; initiate disposition | SC Director | Within 15 days |
| SS_NOT_MAINTAINED flag for A/B class item | Calculate and enter safety stock in SAP MRP; use Method 4 for A-class, Method 3 for B-class | Demand Planner | Within 5 business days |
| 15+ SKUs change ABC class from C to A in monthly refresh | Update replenishment policy (SS method, count frequency, review cycle) in SAP and APS within SLA | Inventory Control Manager | Within 3 business days |
| Shortage Rate > 2% for A-class | Convene emergency S&OP meeting; review demand forecast; assess supplier capacity | VP Supply Chain | Within 24 hours |
| E&O item with no disposition after 14 days | Automatic escalation to SC Director with financial exposure; Finance provision alert triggered | System automated alert | Day 14 |

---

## 17. Test Cases

### TC-01: ADU Calculation Validation

Create a test SKU with 90 days of known GOODS_ISSUE movements: 10 units/day for 30 days, 20 units/day
for 30 days, 0 units for 30 days. Expected ADU = (300 + 600 + 0) / 90 = 10.0 units/day. Compare
pipeline output to expected. Tolerance: 0.001 units.

### TC-02: Coverage Bucket Assignment

Load 5 test SKUs with coverage_days and ABC class: 3 days (any class) = CRITICAL; 10 days (any) =
WARNING; 25 days (A class) = HEALTHY; 25 days (C class) = HEALTHY; 80 days (A class) = EXCESS.
Verify all 5 assigned correctly.

### TC-03: Excess Value Calculation

SKU class A, on_hand = 100 units, ADU = 2 units/day, unit_cost = €5.00, coverage_days = 50,
target = 30. Excess days = 20; excess_value = 20 x 2 x €5.00 = €200.00. Pipeline should return
excess_value_cents = 20000. Tolerance: 0 cents.

### TC-04: Obsolete Flag

Insert snapshot record with last_movement_date = 2024-12-01 and snapshot_date = 2026-06-22.
days_since_movement = 568. is_obsolete should = 1. Insert second record with last_movement_date =
2025-12-01; days_since_movement = 203; is_obsolete should = 0. Verify both records.

### TC-05: Safety Stock Compliance

SKU with on_hand_units = 50, safety_stock_units = 60: ss_compliant = 0.
SKU with on_hand_units = 60, safety_stock_units = 60: ss_compliant = 1.
SKU with on_hand_units = 75, safety_stock_units = 60: ss_compliant = 1.
Verify all three.

### TC-06: Cycle Count Accuracy

Load 10 count records: 8 with counted_qty = system_qty (accuracy_flag = 1); 2 with variance.
Expected accuracy_rate = 80.0%. Verify DAX measure and SQL query both return 80.0%.

### TC-07: E&O Ratio

Total inventory value = €1,000,000. Excess value = €60,000. Obsolete value = €30,000.
Expected E&O Ratio = (60,000 + 30,000) / 1,000,000 x 100 = 9.0%.
Verify Power BI measure returns 9.0%.

### TC-08: Negative Inventory Rejection

Attempt to load a snapshot row with on_hand_units = -5. Verify: (a) ADF pipeline validation
activity rejects the row; (b) row appears in dq_error_log; (c) KPI calculations exclude the row;
(d) alert is sent to the assigned data owner within 1 hour.

### TC-09: ABC Classification Monthly Refresh

Load 100 test SKUs with known ACV values. Top 15 SKUs represent exactly 80% of total ACV; next 25
represent 15%; bottom 60 represent 5%. Expected: 15 A-class, 25 B-class, 60 C-class. Verify output.

### TC-10: DIO Calculation

COGS over 365 days = €500M. Average monthly inventory value = €100M (12-month average).
Turnover = 500/100 = 5.0. DIO = 365/5 = 73 days. Verify DAX and SQL both return 73.0 days.

---

## 18. Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| SAP delta extractor misses movements during maintenance window | Medium | High | Daily full reconciliation count vs. SAP MB52; alert if delta count < 95% of expected; fallback to full extract |
| ADU distortion from promotional demand spikes | High | Medium | Exclude top-5% ADU days from rolling average; maintain separate promotional_demand flag; planner can override |
| ABC classification instability (frequent reclassification) | Medium | Medium | Implement 2-month smoothing rule: SKU must qualify for new class for 2 consecutive months before reclassifying |
| Power BI daily refresh failure | Low | High | Azure Monitor alerting; automatic retry 3x; fallback to prior-day dataset with warning banner in report |
| Missing safety stock for new materials (< 30 days in system) | High | Medium | New materials assigned default SS = 7 x ADU for A/B class until formal SS calculation completed within 30 days |
| Incorrect plant currency conversion causing value discrepancies | Medium | High | All values stored in local currency cents; EUR conversion applied in report layer via dim_exchange_rate (ECB daily rates) |
| Obsolete inventory financial exposure not accrued in time | Low | High | Automated 30-day provision reminder to Finance Controller; escalation to CFO if not actioned |
| Cycle count schedule gaps during peak season | High | Medium | Increase B-class count frequency to weekly during peak season (dim_date.peak_season = 1) |

---

## 19. Implementation Checklist

- [ ] **1.** Confirm Azure SQL DW environment provisioned with sufficient storage (estimated 500 GB for 36 months of movements at the current movement volume) and appropriate vCores for daily batch processing
- [ ] **2.** Configure SAP RFC connections for all six data source extractors; validate authorisation objects S_RFC and S_TABU_DIS are granted for the ADF service account
- [ ] **3.** Deploy ADF pipelines for all six data sources; run first full load and validate row counts against SAP control totals (MB52, MB51, MI23)
- [ ] **4.** Create and validate all fact and dimension tables in Azure SQL per the Section 6 data model; apply monthly partitioning on fact_inventory_snapshot and fact_stock_movements
- [ ] **5.** Implement all 15 transformation rules (TR-01 through TR-15) as Azure SQL stored procedures or ADF data flows; unit test each rule with test data per Section 17
- [ ] **6.** Load dim_movement_type mapping table covering all SAP BWART codes used by the organisation; validate 100% mapping coverage via VC-07
- [ ] **7.** Execute first ABC classification run (TR-08); review output with Inventory Control Manager; sign off per Section 13 evidence item 3
- [ ] **8.** Execute first XYZ classification run (TR-09); review output with Demand Planning team; confirm at least 12 weeks of history per SKU
- [ ] **9.** Load dim_safety_stock from SAP MRP (TR-07); validate completeness for A/B class items per VC-04; generate SS_NOT_MAINTAINED report
- [ ] **10.** Implement all seven validation controls (VC-01 through VC-07); run against first 7 days of production data; document pass/fail rates
- [ ] **11.** Build Power BI report with all six pages per Section 14 specifications; apply row-level security at plant level
- [ ] **12.** Configure row-level security in Power BI: plant controllers see own plants; regional managers see region; global team sees all
- [ ] **13.** Conduct UAT with three inventory controllers and one regional manager per Section 13 evidence item 7; obtain written sign-off
- [ ] **14.** Configure daily ADF pipeline schedule (23:00 UTC extract; 05:30 UTC transformation; 06:00 UTC Power BI refresh)
- [ ] **15.** Set up Azure Monitor alerts for ADF pipeline failures, Power BI refresh failures, and critical data quality breaches (VC-01 failures)
- [ ] **16.** Implement E&O disposition workflow notifications (email alerts per Section 11 alert logic for Day 1, 7, 14, 30, 90)
- [ ] **17.** Train inventory controllers and demand planners (2-hour session per role covering dashboard navigation, KPI interpretation, and action protocols)
- [ ] **18.** Document data lineage from SAP source tables to Power BI visuals in the Data Governance Catalogue
- [ ] **19.** Obtain Finance Controller sign-off on E&O valuation methodology and financial exposure reporting (Section 13 evidence item 4)
- [ ] **20.** Schedule monthly ABC/XYZ refresh job; confirm execution on first calendar day of each month; add Azure Monitor monitoring alert

---

## 20. Validation Checklist

- [ ] **1.** ADF pipeline row counts for all six sources reconcile to SAP control totals within 0.1% for the first 5 consecutive business days
- [ ] **2.** fact_inventory_snapshot total on_hand_value_cents reconciles to SAP transaction MB52 valuation report within €10,000 (rounding tolerance) daily
- [ ] **3.** ADU values for 20 randomly selected A-class SKUs manually verified against SAP MB51 movement history for the 90-day period; tolerance 0.001 units
- [ ] **4.** Coverage day buckets spot-checked for 50 SKUs across all ABC classes; expected bucket matches actual bucket for all 50
- [ ] **5.** ABC classification output for first monthly run agrees with manual ACV calculation for top 10 and bottom 10 SKUs by value; tolerance 0 misclassifications
- [ ] **6.** E&O ratio reported in Power BI matches manual calculation from the exported data file within 0.01%
- [ ] **7.** Safety stock compliance rate matches manual count of SS violations from SAP MD04 for one plant within 1%
- [ ] **8.** Cycle count accuracy rate for first month matches SAP transaction MI23 summary report within 0.5%
- [ ] **9.** Row-level security confirmed: test user with Plant DE01 access cannot see Plant FR01 data in any Power BI visual or exported dataset
- [ ] **10.** Power BI daily refresh completes by 07:00 CET on 5 consecutive business days without failure
- [ ] **11.** CRITICAL coverage bucket alert emails received by correct recipients within 1 hour of data load completion on test day
- [ ] **12.** Negative inventory test case (TC-08) executed: rejected records appear in dq_error_log; KPIs exclude them; alert received within 1 hour
- [ ] **13.** DIO measure verified: turnover ratio and DIO for two business units match Finance Controller's independent calculation within 0.1 day
- [ ] **14.** E&O disposition alerts triggered correctly for 3 test SKUs with last_movement_date > 365 days ago inserted in test environment

---

## 21. Pending Information

The following items require clarification before full implementation can be completed:

**PI-01 — Currency conversion source:** Confirm whether EUR exchange rates should come from ECB daily
rates (publicly available) or the internal SAP TCURR table. If SAP, confirm TCURR is included in the
RFC authorisation profile.

**PI-02 — Coverage target days for pharmaceutical materials:** Confirm whether pharmaceutical materials
require a different coverage target (regulatory minimum stock levels may require higher coverage than
the standard A=30, B=45, C=60 day policy).

**PI-03 — Seasonal demand flag definition:** Confirm the list of material groups and calendar periods
that qualify for the 50% coverage threshold extension during pre-season buffer build.

**PI-04 — E&O disposition workflow tool:** Confirm the target tool for disposition workflow management
(SAP QM workflow, ServiceNow, or a bespoke SharePoint list). The Power BI report link-out on Page 3
depends on the chosen tool URL.

**PI-05 — Historical demand history availability:** For XYZ classification, 12 weeks of weekly demand
history is required per SKU. Confirm the earliest date to which SAP MSEG data is available in the
production client (some organisations archive movements older than 2 years).

**PI-06 — Approval thresholds for cycle count adjustments:** Confirm the financial thresholds for
adjustment authorisation levels (warehouse supervisor vs. inventory controller vs. finance controller)
as these vary by plant per local financial control policies.

**PI-07 — SAP EWM deployment status:** Confirm which of the 40 countries are live on SAP EWM vs.
SAP WM. The cycle count extract pipeline must handle both source tables (/SCWM/QUAN for EWM;
LQUA for WM).

---

## 22. Implementation Roadmap

| Week | Phase | Deliverable | Owner | Dependencies |
|---|---|---|---|---|
| 1 | Infrastructure | Azure SQL DW provisioned; resource group and security configured | IT Infrastructure | Cloud subscription confirmed |
| 1–2 | Infrastructure | SAP RFC connections validated for all 6 data sources | SAP Basis + IT | SAP authorisation objects granted |
| 2 | Data Ingestion | ADF pipeline DS-01 (daily snapshot) deployed and tested | Data Engineering | Azure SQL ready |
| 2–3 | Data Ingestion | ADF pipeline DS-02 (movement history) deployed; 36-month backfill complete | Data Engineering | Sufficient Azure SQL storage |
| 3 | Data Ingestion | ADF pipeline DS-03 (safety stock) deployed | Data Engineering | SAP MARC authorisation |
| 3 | Data Ingestion | ADF pipeline DS-04 (cycle counts) deployed; EWM and WM handled separately | Data Engineering | PI-07 resolved: EWM vs WM plant list |
| 4 | Data Ingestion | ADF pipelines DS-05 (demand history) and DS-06 (material master) deployed | Data Engineering | |
| 4 | Data Model | Star schema tables created in Azure SQL; primary keys and indexes applied | Data Engineering | All pipelines delivering data |
| 5 | Transformation | TR-01 to TR-05 implemented and unit tested | Data Engineering | fact_stock_movements populated |
| 5–6 | Transformation | TR-06 to TR-10 implemented and unit tested; TR-11 to TR-15 implemented | Data Engineering | fact_inventory_snapshot populated |
| 6 | Classification | First ABC classification run (TR-08); first XYZ classification run (TR-09) | Analytics Lead | 12+ weeks demand history confirmed |
| 6 | Validation | VC-01 to VC-07 implemented; first validation report produced | Data Quality Lead | All transformations complete |
| 7 | Dashboard | Power BI Pages 1 and 2 (Executive Overview, Shortage Analysis) built and tested | Power BI Developer | fact_inventory_snapshot with all fields |
| 8 | Dashboard | Power BI Pages 3 and 4 (E&O, ABC/XYZ) built and tested | Power BI Developer | |
| 8 | Dashboard | Power BI Pages 5 and 6 (Safety Stock, Cycle Count) built and tested | Power BI Developer | fact_cycle_counts populated |
| 9 | Dashboard | Row-level security configured and tested; UAT user accounts provisioned | Power BI Developer + IT | |
| 10 | UAT | UAT executed with 3 inventory controllers and 1 regional manager | Analytics Lead | All 6 dashboard pages complete |
| 11 | UAT | UAT defects resolved; retest completed; sign-off obtained | Analytics Lead | UAT findings documented |
| 12 | Finance Review | E&O financial exposure report reconciled to Finance Controller (Section 13 item 4) | Finance Controller | Page 3 validated |
| 13 | Automation | Daily ADF schedule confirmed; Power BI refresh configured; Azure Monitor alerts active | Data Engineering | UAT sign-off |
| 14 | Training | Inventory controller training (2-hour session, all regions); demand planner training | Analytics Lead | Dashboard final |
| 15 | Go-Live | Production go-live: all 40 countries (phased by region per Section 3) | Programme Manager | All checklists complete |
| 15 | Go-Live | Post go-live monitoring: daily pipeline and KPI review for first 5 business days | Analytics Lead | |
| 16 | Handover | Runbook delivered; data governance catalogue updated; hypercare period begins (4 weeks) | Analytics Lead | Go-live stable |

---

## References

- Chopra, S. & Meindl, P. (2016). *Supply Chain Management*, 6th Ed. Pearson.
- Ballou, R.H. (2004). *Business Logistics/Supply Chain Management*, 5th Ed. Pearson.
- Christopher, M. (2022). *Logistics and Supply Chain Management*, 6th Ed. FT Publishing.
- ASCM (2024). *APICS Dictionary*, 16th Ed.
- ASCM (2019). *SCOR Digital Standard*.
- ISO 9001:2015 §8.5.2 — Identification and Traceability.
- ISO 28000:2022 — Specification for Security Management Systems for the Supply Chain.
- GS1 General Specifications v23.0.
- EU Regulation 1907/2006 (REACH).
- EU Directive 2024/1760 (CSDDD) — Article 23 (Data Retention).
- IFRS IAS 2 — Inventories.
- Harris, F.W. (1913). How Many Parts to Make at Once. *Factory, The Magazine of Management*, 10(2).
- Holt, C.C. (1957). Forecasting Seasonals and Trends by Exponentially Weighted Moving Averages.
  Carnegie Institute of Technology.
- Silver, E.A. & Meal, H.C. (1973). A Heuristic for Selecting Lot Size Quantities.
  *Production and Inventory Management*, 14(2), 64–74.
