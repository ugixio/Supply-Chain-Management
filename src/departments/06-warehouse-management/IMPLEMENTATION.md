# Warehouse Operations Analytics — Implementation Guide

**Department:** 06 — Warehouse Management
**Analytics Topic:** Inbound/Outbound Performance, Space Utilisation and Slotting Efficiency,
FEFO Compliance Tracking, Labour Productivity, Warehouse KPI Dashboard
**Standard Alignment:** SCOR-DS · ISO 28000:2022 · GS1 Gen. Specs. v23 · ISO 9001:2015 §8.5.2
**Document Status:** Authorised for Implementation
**Last Reviewed:** 2026-06-22
**Audience:** Warehouse Operations Managers, Supply Chain Architects, Power BI Developers, Industrial Engineers
**Business Context:** SAP EWM + Power BI. Warehouse transactions captured in real time via RF devices,
voice picking, and dock management system. Multi-site global distribution network, 40 countries.

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

This document defines the complete analytics implementation for Warehouse Operations management
within the enterprise Supply Chain Management platform. The solution is built on SAP Extended
Warehouse Management (SAP EWM) as the operational system of record, with Power BI as the reporting
and analytics layer. Warehouse transactions — goods receipts, putaway tasks, pick confirmations,
pack completions, and shipments — are captured in real time by SAP EWM and delivered to the
analytics layer via Azure Data Factory pipelines into Azure SQL Data Warehouse.

Warehouse operations represent a critical cost and service lever in the supply chain. Labour cost
is typically the largest controllable cost in a distribution centre, accounting for 50–65% of total
operating cost (Frazelle, 2002). Space utilisation directly determines the capital expenditure
profile for future DC network capacity. FEFO compliance is a non-negotiable regulatory requirement
for temperature-controlled, pharmaceutical, and REACH SVHC products.

This analytics programme delivers five core capabilities:

**Inbound performance measurement:** Dock-to-stock time from truck arrival to system goods receipt,
broken down by dock, supplier, carrier, and material category. Identifies bottlenecks across the
receive-inspect-putaway pipeline.

**Outbound performance measurement:** Pick accuracy, order fill rate, lines per person-hour, and
wave completion compliance. Identifies labour productivity gaps and fulfilment service failures.

**Space utilisation and slotting efficiency:** Space utilisation by zone, aisle, and rack level;
CPOI (Cube Per Order Index) analysis; ABC velocity slotting compliance; travel distance ratio (TDR).

**FEFO compliance tracking:** Lot picking sequence compliance for all temperature-controlled and
REACH SVHC items; expiry date aging alerts; FEFO deviation root cause attribution.

**Labour productivity analytics:** Lines per person-hour (LPPH) by shift, team, and picking method;
labour cost per pick line; productivity trend and benchmark comparison.

Expected outcomes upon full deployment:
- Pick productivity improvement: 18–25% vs. baseline
- Dock-to-stock cycle time: <= 120 minutes for standard receipts
- FEFO compliance: 100% for all lot-tracked picks
- Space utilisation: 60–75% zone-level utilisation (headroom for peak surge)
- Labour cost per line reduction: 15% vs. baseline within 12 months

---

## 2. Analysis Objective

The primary objective of this analytics implementation is to provide warehouse managers, industrial
engineers, and supply chain leaders with accurate, timely, and actionable intelligence across all
warehouse operations processes, enabling data-driven decisions that improve throughput, reduce cost,
and ensure regulatory compliance.

Specific analytical objectives:

- **Inbound performance:** Measure and decompose dock-to-stock time by stage (unload, count,
  inspect, putaway), supplier, carrier, and dock door to identify and eliminate receiving bottlenecks.

- **Outbound performance:** Track pick accuracy, order fill rate, and carton build accuracy at
  operator, shift, and warehouse levels to identify training and process improvement needs.

- **Space utilisation:** Monitor cubic space utilisation at bin, rack, aisle, zone, and warehouse
  levels; identify over-dense and under-utilised areas; support slotting optimisation decisions.

- **Slotting efficiency:** Measure compliance of current SKU locations with the ABC velocity slotting
  plan (CPOI and slot score) and quantify the travel distance reduction opportunity from reslotting.

- **FEFO compliance:** Track lot picking sequence compliance for every lot-tracked pick; alert on
  FEFO deviations in real time; support regulatory audit requirements under ISO 9001:2015 §8.5.2.

- **Labour productivity:** Measure LPPH, labour cost per line, and operator-level productivity
  to support workforce planning, incentive schemes, and continuous improvement targeting.

---

## 3. Scope

### In Scope

- All SAP EWM-managed distribution centres and warehouses within the global network (40 countries)
- Inbound process: from advance shipment notice (ASN) receipt to goods receipt posting and putaway
  confirmation in SAP EWM
- Outbound process: from wave release to pick confirmation, pack completion, and shipment posting
- Cycle counting and inventory adjustment transactions in SAP EWM
- Cross-docking operations where goods are received and immediately directed to outbound staging
- Lot-tracked picks for items with storage_condition != AMBIENT or reach_svhc = TRUE
- Labour time reporting integrated from SAP EWM task management (timestamps on transfer orders)
- Space utilisation from SAP EWM location master and quant occupancy data

### Out of Scope

- Transport management and carrier rate analytics (covered by Department 03 — Logistics)
- Supplier performance scoring (OTD, OTIF, PPM) — covered by Department 02 — Supplier Management
- Yard management system (YMS) at sites without SAP EWM yard module (tracked via separate system)
- Returns processing (reverse logistics analytics) — covered by Department 05 — Inventory Management
- Manual picking at sites not yet on SAP EWM — include in roadmap after EWM rollout

### Geographic Scope

All 40 countries in scope at the same rollout sequence as the broader SCM platform.
Sites on SAP EWM (target state): priority. Sites on SAP WM (legacy): partial data available from
WM transfer order tables; full feature set requires EWM upgrade.

---

## 4. Business Questions

**BQ-01:** What is the dock-to-stock time by warehouse, dock door, supplier, and carrier for the
current week, and which combinations are exceeding the 120-minute SLA target?

**BQ-02:** What is the pick accuracy rate (correct picks / total picks) by warehouse, shift, picking
method (RF batch, voice, pick-to-light), and operator for the current month?

**BQ-03:** What percentage of active locations are currently occupied, what is the average cubic fill
rate by zone, and which zones are at or above the 80% over-dense alert threshold?

**BQ-04:** What percentage of current SKU-location assignments comply with the ABC velocity slotting
plan (A-class in primary golden zone, B in secondary, C in tertiary/bulk)?

**BQ-05:** What is the FEFO compliance rate for all lot-tracked picks in the current month, and
which SKUs, operators, or shifts are responsible for FEFO deviations?

**BQ-06:** What is the lines per person-hour (LPPH) by shift and picking method vs. world-class
benchmarks, and which shifts are below the 80% performance threshold?

**BQ-07:** What is the order fill rate (lines shipped complete / total order lines) by business unit,
customer priority class (SAME_DAY, NEXT_DAY, STANDARD), and warehouse for the current week?

**BQ-08:** Which SKUs have the highest CPOI (cube per order index) and are currently assigned to
primary golden zone locations, creating space inefficiency?

**BQ-09:** What is the travel distance ratio (TDR) for each warehouse, and which aisles or zones
are contributing most to travel inefficiency relative to the optimal slotting plan?

**BQ-10:** What is the labour cost per pick line by warehouse and shift, and how does it compare to
the standard cost per line target, expressed in integer cents?

**BQ-11:** What is the dock damage rate (damaged pallets detected / total pallets received), and
which suppliers or carriers have the highest damage rates?

**BQ-12:** Which lots currently on hand are within 30 days of expiry and have not yet been assigned
to an outbound pick task, creating a risk of expired stock write-off?

---

## 5. Data Sources

### DS-01: SAP EWM — Transfer Order History (Pick, Putaway, Replenishment)

| Attribute | Detail |
|---|---|
| Source Name | SAP EWM — Warehouse Task History |
| Origin System | SAP EWM (SCWM module) |
| Table/Query | /SCWM/TOCO (transfer order header), /SCWM/TOCI (transfer order item), /SCWM/ORDIM (warehouse order) |
| Data Owner | DC Operations Manager |
| Frequency | Near-real-time: 15-minute incremental extract via SAP Change Data Capture (CDC) |
| Required Fields | TANUM (TO number), MANDT (client), LGNUM (warehouse), MATNR (material), LENUM (handling unit), NLTYP (destination type), NLPLA (destination bin), VLTYP (source type), VLPLA (source bin), VSOLM (quantity), VERSKZ (confirmation status), LMNUM (resource/operator), ANFZ (start time), ENQZ (end time), BWLVS (movement type) |
| Critical Fields | ANFZ, ENQZ — used for dock-to-stock time and LPPH calculations; LMNUM — operator productivity attribution |
| Primary Key | TANUM + MANDT + LGNUM |
| Validations | ENQZ >= ANFZ (end time >= start time); VERSKZ = confirmed status for completed tasks; MATNR exists in material master |
| Possible Errors | Tasks abandoned without confirmation creating open tasks that inflate active task count; LMNUM null for voice-picked tasks on some EWM configurations |
| Extraction Evidence | ADF pipeline ZEWM_TO_CDC; reconciled against EWM report /SCWM/TOREP daily |

### DS-02: SAP EWM — Goods Receipt and Dock Management

| Attribute | Detail |
|---|---|
| Source Name | SAP EWM — Inbound Delivery and Dock Management |
| Origin System | SAP EWM |
| Table/Query | /SCWM/AVIS (advance shipment notice), /SCWM/PDOCK (dock door assignment), /SCWM/VERI (goods receipt verification), MKPF/MSEG (material document for GR posting) |
| Data Owner | Receiving Supervisor |
| Frequency | Near-real-time: 15-minute incremental extract |
| Required Fields | VBELN (ASN delivery number), LGNUM, MATNR, LENUM (pallet SSCC), ANLDATUM (arrival date/time), UEZDATUM (dock door open time), WBSTATUS (goods receipt status), BUDAT (posting date), CHARG (batch/lot number), MHD_DATE (shelf life expiry date) |
| Critical Fields | ANLDATUM (truck arrival) and WBSTATUS = GR_POSTED (goods receipt confirmed) — used for dock-to-stock time T0 to T5 |
| Primary Key | VBELN + LGNUM + MATNR |
| Validations | ANLDATUM <= BUDAT; LENUM matches a valid SSCC-18 format; CHARG not null for lot-tracked materials |
| Possible Errors | ANLDATUM not captured if gate reader is offline; LENUM missing on supplier pallets with non-GS1-compliant labels |
| Extraction Evidence | ADF pipeline ZEWM_GR_CDC; reconciled against SAP MB52 daily total |

### DS-03: SAP EWM — Outbound Delivery and Shipment

| Attribute | Detail |
|---|---|
| Source Name | SAP EWM — Outbound Delivery and Wave Management |
| Origin System | SAP EWM |
| Table/Query | /SCWM/WAVE (wave header), /SCWM/WAOR (wave order assignment), /SCWM/VELI (delivery item), LIKP (delivery header), LIPS (delivery item) |
| Data Owner | Outbound Supervisor |
| Frequency | Near-real-time: 15-minute incremental extract |
| Required Fields | VBELN (delivery number), POSNR (item), MATNR, LGNUM, VRKME (delivery quantity), LFIMG (actual picked quantity), CHARG (lot), ERDAT (creation date), LFDAT (delivery date), TRATY (transport type), LGTOR (door), WAVE_ID |
| Critical Fields | VRKME (ordered qty) vs. LFIMG (picked qty) — used for pick accuracy and order fill rate; CHARG — used for FEFO compliance |
| Primary Key | VBELN + POSNR |
| Validations | LFIMG <= VRKME (no over-pick without approval); CHARG not null for lot-tracked items; delivery date <= system date + 5 days |
| Possible Errors | Partial picks creating incomplete deliveries counted as full in some SAP configurations; WAVE_ID missing for ad-hoc picks outside wave management |
| Extraction Evidence | ADF pipeline ZEWM_OBD_CDC; reconciled against VL06O report daily |

### DS-04: SAP EWM — Location Master and Quant Occupancy

| Attribute | Detail |
|---|---|
| Source Name | SAP EWM — Location Master and Storage Quant |
| Origin System | SAP EWM |
| Table/Query | /SCWM/LGPLA (storage bin master), /SCWM/QUAN (storage quant — current occupancy) |
| Data Owner | Warehouse Systems Administrator |
| Frequency | Daily full extract at 23:30 UTC (quants) + weekly full extract for location master changes |
| Required Fields | LGNUM, LGTYP (storage type), LGPLA (bin), MAXGE (max gross weight g), MAXVOL (max volume mm3), ABFER (putaway type), ABNUM (putaway sequence), MATNR (from quant), CHARG, VFDAT (expiry date), VERME (quant quantity), MEINH (UOM), LGPLA_ZONE (zone code) |
| Critical Fields | MAXVOL, VERME — used for cubic space utilisation; VFDAT — used for FEFO expiry alerting |
| Primary Key | LGNUM + LGTYP + LGPLA (location); LGNUM + LGTYP + LGPLA + MATNR + CHARG (quant) |
| Validations | MAXVOL > 0; VERME >= 0; VFDAT >= GETDATE() for any lot currently in an active pick location |
| Possible Errors | MAXVOL = 0 for locations not yet dimensioned in EWM; quant records without VFDAT for lot-tracked items (master data gap) |
| Extraction Evidence | ADF pipeline ZEWM_LOC_DAILY; location count reconciled against EWM report /SCWM/BINSRCH |

### DS-05: SAP EWM — Labour Resource Management

| Attribute | Detail |
|---|---|
| Source Name | SAP EWM — Resource Management (Operator Time Tracking) |
| Origin System | SAP EWM |
| Table/Query | /SCWM/RSRC (resource master), /SCWM/LGQUA (labour qualification), /SCWM/TOCO with LMNUM join |
| Data Owner | DC HR Manager / Workforce Planning |
| Frequency | Daily extract |
| Required Fields | LMNUM (operator resource number), LGNUM, SCHICHT (shift), KSTAR (cost type), TANUM (linked task), ANFZ (task start), ENQZ (task end), BWLVS (activity type: pick, putaway, replenishment, count) |
| Critical Fields | ANFZ, ENQZ — used for LPPH; SCHICHT — used for shift-level productivity breakdown |
| Primary Key | LMNUM + TANUM + LGNUM |
| Validations | ENQZ > ANFZ; SCHICHT in approved shift codes; LMNUM exists in resource master |
| Possible Errors | LMNUM null for tasks completed on shared terminals; SCHICHT not populated for split-shift workers |
| Extraction Evidence | ADF pipeline ZEWM_LABOUR_DAILY; task count reconciled against operator productivity report in EWM |

### DS-06: SAP EWM — Lot (Batch) Master and Expiry Dates

| Attribute | Detail |
|---|---|
| Source Name | SAP EWM — Batch / Lot Master |
| Origin System | SAP S/4HANA (MCH1 batch master) synced to SAP EWM |
| Table/Query | MCH1 (batch master header), MCH7 (batch where-used), MCHA (batch classification) |
| Data Owner | Inventory Control Manager |
| Frequency | Daily full extract |
| Required Fields | MATNR, CHARG (lot number), VFDAT (expiry date), HSDAT (manufacture date), LICHA (supplier lot), LGNUM (warehouse), EINLKZ (restricted use flag) |
| Critical Fields | VFDAT — used for FEFO logic validation and expiry alerting; EINLKZ — blocked lots must not be picked |
| Primary Key | MATNR + CHARG |
| Validations | VFDAT not null for lot-tracked materials; VFDAT > GETDATE() for lots in active pick locations (expired lots must be in quarantine) |
| Possible Errors | VFDAT null for lot-tracked items where supplier did not provide shelf life on ASN; CHARG duplicated across plants if batch management not configured at plant level |
| Extraction Evidence | ADF pipeline ZBATCH_DAILY; lot count reconciled against MB56 batch where-used list |

---

## 6. Data Model

The analytics solution uses a star schema deployed in Azure SQL DW with two central fact tables and
seven dimension tables. All monetary values stored as integer cents (BIGINT). All timestamps in UTC,
all dates in ISO 8601 (YYYY-MM-DD).

### Fact Tables

**fact_warehouse_tasks** — Grain: one row per SAP EWM transfer order item (confirmed).
Contains task type, operator, timestamps (start/end), quantity, source and destination locations.
Used for LPPH, dock-to-stock time, pick accuracy, and FEFO compliance.

**fact_location_occupancy** — Grain: one row per warehouse location per daily snapshot.
Contains cubic capacity, occupied volume, current quant, and fill rate.
Used for space utilisation and slotting efficiency analytics.

### Dimension Tables

**dim_warehouse** — Warehouse master: code, name, country, region, DC manager, EWM/WM flag.

**dim_location** — Location master: warehouse, zone, storage type, aisle, rack, bin, cubic capacity,
golden zone assignment, is_pick_location, is_reserve_location, is_active.

**dim_material** — Shared with Department 05: SKU master with ABC/XYZ class, lot_tracked,
reach_svhc, storage_condition, coverage_target_days.

**dim_operator** — Operator resource master: resource ID, name, shift, qualification, cost rate.

**dim_date** — Calendar dimension with fiscal week, shift date, peak_season flag.

**dim_task_type** — Task type classification: GOODS_RECEIPT, PUTAWAY, PICK, PACK, SHIP,
REPLENISHMENT, CYCLE_COUNT, TRANSFER, FEFO indicator.

**dim_lot** — Lot master: lot number, material, expiry date, manufacture date, restricted use flag.

### Key Relationships

```
fact_warehouse_tasks.task_type_code   --> dim_task_type.task_type_code  (many-to-one)
fact_warehouse_tasks.sku_id           --> dim_material.sku_id            (many-to-one)
fact_warehouse_tasks.operator_id      --> dim_operator.operator_id       (many-to-one)
fact_warehouse_tasks.destination_bin  --> dim_location.location_id       (many-to-one)
fact_warehouse_tasks.lot_number       --> dim_lot.lot_number             (many-to-one)
fact_warehouse_tasks.task_date        --> dim_date.date_id               (many-to-one)
fact_location_occupancy.location_id   --> dim_location.location_id       (many-to-one)
fact_location_occupancy.snapshot_date --> dim_date.date_id               (many-to-one)
```

---

## 7. Data Dictionary

### Table: fact_warehouse_tasks

| Field | Type | Description | PK |
|---|---|---|---|
| task_id | BIGINT IDENTITY | Surrogate primary key | Yes |
| tanum | NVARCHAR(20) | SAP EWM transfer order number (TANUM) | No |
| warehouse_code | NVARCHAR(3) | SAP warehouse number (LGNUM) | No |
| task_type_code | NVARCHAR(20) | GOODS_RECEIPT / PUTAWAY / PICK / PACK / SHIP / REPLENISHMENT / CYCLE_COUNT | No |
| sku_id | NVARCHAR(40) | SAP material number (MATNR) | No |
| lot_number | NVARCHAR(20) | SAP batch number (CHARG); NULL for non-lot-tracked items | No |
| lot_expiry_date | DATE | Lot expiry date (VFDAT); NULL for non-lot-tracked items | No |
| source_location_id | NVARCHAR(30) | Source bin (VLTYP + VLPLA) | No |
| destination_location_id | NVARCHAR(30) | Destination bin (NLTYP + NLPLA) | No |
| operator_id | NVARCHAR(20) | Operator resource number (LMNUM) | No |
| shift_code | NVARCHAR(10) | Shift identifier (SCHICHT): EARLY / LATE / NIGHT | No |
| quantity_confirmed | DECIMAL(18,3) | Confirmed quantity (VSOLM) | No |
| quantity_requested | DECIMAL(18,3) | Requested quantity at task creation | No |
| task_start_utc | DATETIME2 | Task start timestamp UTC (ANFZ) | No |
| task_end_utc | DATETIME2 | Task end timestamp UTC (ENQZ) | No |
| task_duration_seconds | INT | DATEDIFF(SECOND, task_start_utc, task_end_utc) | No |
| task_date | DATE | Date portion of task_start_utc | No |
| is_fefo_task | BIT | 1 if task_type = PICK AND lot-tracked item (requires FEFO compliance) | No |
| fefo_compliant | BIT | 1 if lot picked was earliest expiry available; NULL for non-FEFO tasks | No |
| fefo_deviation_reason | NVARCHAR(100) | Reason code if fefo_compliant = 0; NULL otherwise | No |
| pick_accuracy_flag | BIT | 1 if quantity_confirmed = quantity_requested; NULL for non-pick tasks | No |
| dock_arrival_utc | DATETIME2 | Truck arrival timestamp for GOODS_RECEIPT tasks (ANLDATUM) | No |
| dock_to_stock_minutes | INT | Minutes from dock_arrival_utc to task_end_utc for PUTAWAY tasks | No |
| damage_flag | BIT | 1 if pallet damage detected at inbound inspection (from YOLOv8 or manual flag) | No |

**Granularity:** One row per SAP EWM transfer order item (confirmed)
**Partitioning:** By task_date (monthly)
**Transformations:** task_duration_seconds computed from ANFZ/ENQZ; fefo_compliant set by FEFO evaluation logic; dock_to_stock_minutes set only on final PUTAWAY task for each ASN

---

### Table: fact_location_occupancy

| Field | Type | Description | PK |
|---|---|---|---|
| occupancy_id | BIGINT IDENTITY | Surrogate primary key | Yes |
| snapshot_date | DATE | Daily snapshot date | No |
| location_id | NVARCHAR(30) | Warehouse + storage type + bin | No |
| warehouse_code | NVARCHAR(3) | SAP warehouse number | No |
| zone_code | NVARCHAR(10) | Zone: AMBIENT / COLD_CHAIN / FREEZER / HAZMAT / RETURNS | No |
| golden_zone | NVARCHAR(10) | PRIMARY / SECONDARY / TERTIARY / BULK | No |
| cubic_capacity_mm3 | BIGINT | Maximum cubic volume of the bin in mm3 | No |
| occupied_volume_mm3 | BIGINT | Current occupied volume from quant records | No |
| fill_rate_pct | DECIMAL(6,2) | occupied_volume_mm3 / cubic_capacity_mm3 x 100 | No |
| is_over_dense | BIT | 1 if fill_rate_pct > 90 |  No |
| is_under_utilised | BIT | 1 if fill_rate_pct < 50 | No |
| current_sku_id | NVARCHAR(40) | Current resident SKU (if single-SKU location) | No |
| current_abc_class | CHAR(1) | ABC class of current resident SKU | No |
| slotting_compliant | BIT | 1 if current_abc_class matches expected class for golden_zone assignment | No |
| cpoi | DECIMAL(18,4) | Cube Per Order Index = unit_volume_mm3 / avg_order_lines_per_week | No |

**Granularity:** One row per warehouse location per daily snapshot

---

### Table: dim_location

| Field | Type | Description |
|---|---|---|
| location_id | NVARCHAR(30) | Warehouse + LGTYP + LGPLA — primary key, immutable |
| warehouse_code | NVARCHAR(3) | SAP warehouse number (LGNUM) |
| zone_code | NVARCHAR(10) | AMBIENT / COLD_CHAIN / FREEZER / HAZMAT / BULK / QUARANTINE / RETURNS |
| storage_type | NVARCHAR(3) | SAP storage type (LGTYP) |
| aisle | NVARCHAR(5) | Aisle identifier |
| rack | NVARCHAR(3) | Rack number |
| bin_level | INT | Vertical level (1 = floor, higher = elevated) |
| bin_position | INT | Horizontal position within rack |
| cubic_capacity_mm3 | BIGINT | Internal cubic volume in cubic millimetres (MAXVOL from EWM) |
| max_weight_grams | BIGINT | Maximum gross weight capacity in grams |
| is_pick_location | BIT | 1 if this is a forward pick face |
| is_reserve_location | BIT | 1 if this is a reserve/bulk storage location |
| is_dock_staging | BIT | 1 if this is a dock staging area |
| golden_zone | NVARCHAR(10) | PRIMARY / SECONDARY / TERTIARY / BULK — from ABC velocity slotting plan |
| ergonomic_score | DECIMAL(4,2) | 1.0 = optimal (waist-to-shoulder); 0.4 = poor (above head / floor) |
| is_active | BIT | 1 if location is active |
| is_deleted | BIT | Soft-delete flag — never physically removed |

---

### Table: dim_operator

| Field | Type | Description |
|---|---|---|
| operator_id | NVARCHAR(20) | SAP EWM resource number (LMNUM) — primary key |
| warehouse_code | NVARCHAR(3) | Primary warehouse |
| shift_code | NVARCHAR(10) | EARLY / LATE / NIGHT |
| picking_method | NVARCHAR(20) | RF_BATCH / VOICE / PICK_TO_LIGHT / GOODS_TO_PERSON / PAPER |
| hourly_rate_cents | BIGINT | Direct wage rate in integer cents per hour |
| benefits_rate | DECIMAL(5,4) | Employer benefits as fraction of hourly rate (e.g. 0.28) |
| qualification_level | NVARCHAR(10) | JUNIOR / STANDARD / SENIOR / LEAD |
| is_active | BIT | 1 if operator currently employed |
| hire_date | DATE | Employment start date |

---

### Table: dim_lot

| Field | Type | Description |
|---|---|---|
| lot_id | BIGINT IDENTITY | Surrogate primary key |
| lot_number | NVARCHAR(20) | SAP batch number (CHARG) |
| sku_id | NVARCHAR(40) | SAP MATNR |
| expiry_date | DATE | SAP VFDAT — shelf life expiry date |
| manufacture_date | DATE | SAP HSDAT — manufacture date |
| supplier_lot_ref | NVARCHAR(40) | Supplier's own lot reference (LICHA) |
| restricted_use | BIT | 1 if lot is restricted (EINLKZ = X) — must not be picked |
| days_to_expiry | INT | Computed: DATEDIFF(DAY, GETDATE(), expiry_date) — refreshed daily |
| expiry_alert_tier | NVARCHAR(10) | CRITICAL / WARNING / NORMAL — based on storage condition thresholds |

---

## 8. Transformation Rules

**TR-01 — Dock-to-Stock Time Calculation**
For each inbound ASN (advance shipment notice), identify the truck arrival timestamp (ANLDATUM from
DS-02) as T0. Identify the timestamp of the final PUTAWAY task confirmation (task_end_utc WHERE
task_type_code = 'PUTAWAY' AND tanum is the last putaway task for the ASN) as T7.
dock_to_stock_minutes = DATEDIFF(MINUTE, T0, T7). Store on the final PUTAWAY task record.
If T0 is not available (gate reader offline), use dock_door_open_utc as fallback and flag
estimated_arrival = TRUE.

**TR-02 — Pick Accuracy Flag**
pick_accuracy_flag = 1 WHERE quantity_confirmed = quantity_requested AND task_type_code = 'PICK'.
pick_accuracy_flag = 0 WHERE quantity_confirmed != quantity_requested AND task_type_code = 'PICK'.
NULL for all non-pick task types. Short picks (quantity_confirmed < quantity_requested) must trigger
an exception record in the outbound delivery with reason code SHORT_PICK.

**TR-03 — FEFO Compliance Evaluation**
For each PICK task where is_fefo_task = 1 (lot-tracked item), retrieve all available lots for the
SKU at the source location at the time of task creation. Sort by expiry_date ascending. The lot
selected (lot_number on the task) must be the lot with the earliest expiry_date among available lots
with quantity > 0 and restricted_use = 0 and days_to_expiry >= min_shelf_life threshold.
fefo_compliant = 1 if correct lot was selected; fefo_compliant = 0 if a later-expiring lot was
picked when an earlier-expiring lot was available. fefo_deviation_reason populated from EWM exception
log or set to OPERATOR_OVERRIDE if the picker bypassed the system-directed lot.

**TR-04 — Order Fill Rate Calculation**
For each outbound delivery line (DS-03), compare LFIMG (shipped quantity) to VRKME (ordered quantity).
fill_rate_flag = 1 if LFIMG >= VRKME. Order-level fill rate: all lines on a delivery must have
fill_rate_flag = 1 for the order to be counted as COMPLETE. Line-level fill rate: individual line
flag used for line-level KPI. Both are computed.

**TR-05 — Space Utilisation (Cubic Fill Rate)**
For each location in dim_location, compute occupied_volume_mm3 = SUM(/SCWM/QUAN.VERME x SKU_volume_mm3)
where SKU_volume_mm3 = dim_material.volume_m3 x 1e9 (convert m3 to mm3).
fill_rate_pct = occupied_volume_mm3 / cubic_capacity_mm3 x 100.
is_over_dense = 1 if fill_rate_pct > 90. is_under_utilised = 1 if fill_rate_pct < 50.

**TR-06 — CPOI (Cube Per Order Index)**
cpoi = unit_volume_mm3 / avg_order_lines_per_week where unit_volume_mm3 =
dim_material.volume_m3 x 1e9. avg_order_lines_per_week = COUNT(delivery lines containing sku_id
in the trailing 13 weeks) / 13. Computed weekly. High CPOI (above 90th percentile) items should
not occupy PRIMARY golden zone locations.

**TR-07 — Slotting Compliance Flag**
slotting_compliant = 1 if the current ABC class of the resident SKU matches the expected ABC class
for the golden zone:
- A-class SKU in PRIMARY zone: compliant
- B-class SKU in SECONDARY zone: compliant
- C-class SKU in TERTIARY or BULK zone: compliant
- Any mismatch (A-class in BULK, C-class in PRIMARY, etc.): non-compliant
Computed daily as part of fact_location_occupancy load.

**TR-08 — LPPH (Lines Per Person-Hour)**
For each shift-warehouse combination, aggregate all confirmed PICK task records:
total_lines_picked = COUNT(tasks WHERE task_type_code = 'PICK' AND shift_code = X AND task_date = Y)
total_labour_hours = SUM(task_duration_seconds) / 3600 for same cohort.
LPPH = total_lines_picked / total_labour_hours. Exclude idle time (gaps > 15 minutes between tasks
for same operator) from total_labour_hours denominator.

**TR-09 — Labour Cost Per Pick Line**
cost_per_line_cents = (hourly_rate_cents x (1 + benefits_rate)) x
(travel_time_seconds + pick_dwell_seconds + exception_seconds) / 3600.
travel_time_seconds = time between completion of prior task and start of current pick task for same
operator (approximation; exact travel time requires WCS path tracking data).
pick_dwell_seconds = task_duration_seconds minus travel_time_seconds.

**TR-10 — Dock Damage Rate**
damage_rate_pct = COUNT(GOODS_RECEIPT tasks WHERE damage_flag = 1) /
COUNT(all GOODS_RECEIPT tasks) x 100. Computed daily, weekly, and monthly. Grouped by
supplier_id and carrier_scac to support supplier/carrier performance reporting.

**TR-11 — Lot Expiry Alerting**
For each lot in dim_lot, compute expiry_alert_tier based on days_to_expiry and storage_condition:
AMBIENT (non-SVHC): CRITICAL < 30 days, WARNING 30–60 days, NORMAL > 60 days.
COLD_CHAIN: CRITICAL < 45 days, WARNING 45–90 days.
FREEZER: CRITICAL < 60 days, WARNING 60–90 days.
CONTROLLED (pharma): CRITICAL < 90 days, WARNING 90–120 days.
REACH SVHC (any): CRITICAL < 60 days, WARNING 60–90 days.

**TR-12 — Travel Distance Ratio (TDR)**
TDR = actual_mean_pick_travel_distance_m / optimal_mean_pick_travel_distance_m.
Actual travel distance estimated from aisle/rack/bin coordinate differences between consecutive
pick tasks for the same operator in a wave. Optimal distance assumes all picks from nearest possible
locations to dispatch point using Manhattan distance. Computed monthly per warehouse.

---

## 9. Business Rules

### BR-01: FEFO Compliance Mandatory for Lot-Tracked Items

| Attribute | Detail |
|---|---|
| Name | FEFO Compliance Mandatory |
| Description | All pick tasks for lot-tracked items must select the lot with the earliest expiry date among available eligible lots. FEFO supersedes all other lot selection criteria including FIFO, location, or operator preference |
| Logic Condition | IF is_fefo_task = 1 AND lot selected is NOT the earliest-expiry eligible lot THEN fefo_compliant = 0 AND alert raised |
| Expected Result | fefo_compliant = 1 for 100% of is_fefo_task = 1 pick records |
| Example | Two lots of SKU MAT-05511 available: lot A expiry 2026-09-01, lot B expiry 2026-12-01. Operator must pick from lot A first. If lot B is picked while lot A is available with adequate quantity, FEFO deviation recorded |
| Exception | System may override FEFO to skip a lot if days_to_expiry < min_remaining_shelf_life threshold AND no customer will accept the lot — documented in fefo_deviation_reason as INSUFFICIENT_SHELF_LIFE_FOR_CUSTOMER |
| Evidence | ISO 9001:2015 §8.5.2; EU REACH 1907/2006; BR-07 from Inventory Management module |

### BR-02: No Negative Inventory at Pick

| Attribute | Detail |
|---|---|
| Name | No Negative Inventory at Pick |
| Description | A pick task must never confirm a quantity that would result in negative stock at the source location |
| Logic Condition | IF quantity_confirmed > current_bin_stock THEN reject pick confirmation AND raise SHORT_PICK exception |
| Expected Result | Zero pick tasks with quantity_confirmed > stock at source location at time of confirmation |
| Example | Bin A01-002-03 contains 10 EA of SKU MAT-00123. Pick task of 15 EA is rejected; system reduces to 10 EA and raises a SHORT_PICK exception for the remaining 5 EA |
| Exception | Cross-docking flows where stock is in transit between locations may show a transient negative balance in one location — these are permitted for <= 15 minutes until the corresponding inbound transfer is confirmed |
| Evidence | CLAUDE.md Critical Business Rule #1 |

### BR-03: GS1 SSCC Label Compliance on All Outbound Pallets

| Attribute | Detail |
|---|---|
| Name | GS1 SSCC Label Compliance |
| Description | Every outbound pallet must carry a valid GS1 SSCC-18 label with mandatory application identifiers before shipment is posted |
| Logic Condition | IF shipment_posted = TRUE AND pallet_sscc_valid = FALSE THEN block shipment posting AND raise label defect exception |
| Expected Result | 100% of outbound pallets have a valid, scanned SSCC label; defect rate <= 500 PPM |
| Example | Pallet built at pack station — ZPL label printed with AI(00) SSCC-18, AI(02) GTIN-14, AI(37) quantity, AI(10) lot number. Label scanned at ship door. If scan fails, shipment is blocked |
| Exception | Emergency direct-to-consumer parcels (parcel carrier labels only) do not require SSCC; these are flagged with shipment_type = PARCEL |
| Evidence | GS1 General Specifications v23.0; Incoterms 2020 documentation requirements |

### BR-04: Soft-Delete Only on Warehouse Records

| Attribute | Detail |
|---|---|
| Name | Soft-Delete Only |
| Description | No warehouse location records, transfer order records, lot records, or occupancy snapshots may be physically deleted |
| Logic Condition | is_deleted = TRUE is the only permitted mechanism; hard DELETE blocked at database layer |
| Expected Result | All historical records preserved; all active queries filter is_deleted = FALSE |
| Example | Bin A01-002-03 decommissioned due to rack repair — is_active = FALSE, is_deleted = FALSE. All historical tasks referencing this bin remain accessible for audit |
| Exception | Test data in non-production environments may be hard-deleted by IT administrators only |
| Evidence | CLAUDE.md Critical Business Rule #3 |

### BR-05: Lot Tracking Required for Non-Ambient and REACH SVHC Items

| Attribute | Detail |
|---|---|
| Name | Lot Tracking at Pick Mandatory |
| Description | All pick tasks for items with storage_condition != AMBIENT or reach_svhc = TRUE must have a non-null lot_number |
| Logic Condition | IF dim_material.lot_tracked = TRUE AND fact_warehouse_tasks.lot_number IS NULL AND task_type_code = 'PICK' THEN compliance breach |
| Expected Result | Zero lot-tracked pick tasks with null lot_number |
| Example | SKU MAT-05511 (CHILLED): all pick tasks must reference a specific lot number. If EWM task is created without a lot assignment, the task cannot be confirmed until lot is assigned |
| Exception | None permitted |
| Evidence | EU REACH 1907/2006; ISO 9001:2015 §8.5.2; CLAUDE.md Critical Business Rule #5 |

### BR-06: Dock-to-Stock SLA

| Attribute | Detail |
|---|---|
| Name | Dock-to-Stock Time SLA |
| Description | Standard receipts must be fully stocked (putaway confirmed) within 120 minutes of truck arrival. Temperature-controlled receipts must be stocked within 90 minutes to preserve cold chain |
| Logic Condition | dock_to_stock_minutes <= 120 for AMBIENT receipts; <= 90 for CHILLED/FROZEN/CONTROLLED receipts |
| Expected Result | >= 95% of receipts meet the SLA for their storage condition category |
| Example | Frozen goods arrive at 10:00 UTC. Putaway confirmed at 11:35 UTC = 95 minutes. SLA breached for frozen (> 90 minutes). Alert raised to receiving supervisor |
| Exception | Force majeure events (system outages, power failures) may be excluded from SLA measurement if documented within 4 hours via the exception logging tool |
| Evidence | Cold chain regulatory requirements; Incoterms 2020 CIP/CIF insurance implications |

### BR-07: Minimum Remaining Shelf Life at Pick

| Attribute | Detail |
|---|---|
| Name | Minimum Remaining Shelf Life |
| Description | Lots must have sufficient remaining shelf life at time of pick to satisfy customer delivery SLA plus minimum acceptance threshold |
| Logic Condition | REJECT pick IF days_to_expiry < min_remaining_shelf_life_days per storage condition policy (see TR-11 thresholds) |
| Expected Result | Zero lots picked that do not meet the minimum remaining shelf life threshold |
| Example | SKU MAT-08820 (CONTROLLED / pharma): lot expiry 2026-08-01; pick date 2026-06-22; days_to_expiry = 40 days. Min threshold = 90 days. Pick is rejected; lot flagged CRITICAL in expiry alerts |
| Exception | Written customer acceptance of short-dated stock (with documented VFDAT communicated to customer and customer sign-off recorded) permits the pick |
| Evidence | Pharmaceutical GDP guidelines; customer SLA agreements |

### BR-08: Wave Release Compliance

| Attribute | Detail |
|---|---|
| Name | Wave Release Must Respect Carrier Collection Window |
| Description | Waves must be released with sufficient time to complete picking, packing, and staging before the carrier collection window minus the 90-minute buffer |
| Logic Condition | wave_release_time <= carrier_collection_time - 90 minutes |
| Expected Result | >= 95% of waves completed and staged before carrier arrival |
| Example | Carrier DHL scheduled for 15:00 UTC. Wave must be released no later than 13:30 UTC and all picks confirmed by 14:30 UTC (allowing 30 minutes for packing and 30 minutes for staging) |
| Exception | Emergency same-day orders may require wave release closer to collection time with supervisor approval; these are flagged rush_wave = TRUE |
| Evidence | Customer SLA agreements; Incoterms 2020 FCA delivery obligations |

---

## 10. KPIs and Formulas

### KPI-01: Dock-to-Stock Time

**Definition:** Total elapsed time in minutes from truck arrival at dock to final putaway confirmation
in SAP EWM for the last pallet of the receipt.

**Formula:**
```
Dock_to_Stock_minutes = task_end_utc (last PUTAWAY task for ASN)
                        - dock_arrival_utc (ANLDATUM from ASN)
                        expressed in minutes
```

**DAX:**
```dax
Dock to Stock (min) =
AVERAGEX(
    FILTER(
        fact_warehouse_tasks,
        fact_warehouse_tasks[task_type_code] = "PUTAWAY"
        && NOT ISBLANK(fact_warehouse_tasks[dock_to_stock_minutes])
    ),
    fact_warehouse_tasks[dock_to_stock_minutes]
)
```

**SQL:**
```sql
SELECT
    warehouse_code,
    CAST(task_start_utc AS DATE)    AS task_date,
    AVG(dock_to_stock_minutes)      AS avg_dock_to_stock_min,
    MAX(dock_to_stock_minutes)      AS max_dock_to_stock_min,
    PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY dock_to_stock_minutes)
                                    AS p90_dock_to_stock_min,
    COUNT(*)                        AS receipt_count,
    SUM(CASE WHEN dock_to_stock_minutes > 120 THEN 1 ELSE 0 END) AS sla_breach_count
FROM fact_warehouse_tasks
WHERE task_type_code = 'PUTAWAY'
  AND dock_to_stock_minutes IS NOT NULL
  AND task_date >= DATEADD(DAY, -30, GETDATE())
GROUP BY warehouse_code, CAST(task_start_utc AS DATE)
ORDER BY avg_dock_to_stock_min DESC;
```

**Target:** Mean <= 90 minutes. P90 <= 120 minutes. SLA breach rate < 5%.

---

### KPI-02: Pick Accuracy

**Definition:** Percentage of pick tasks where confirmed quantity equals requested quantity.

**Formula:**
```
Pick_Accuracy_pct = COUNT(PICK tasks WHERE pick_accuracy_flag = 1)
                    / COUNT(all PICK tasks) x 100
```

**DAX:**
```dax
Pick Accuracy % =
DIVIDE(
    CALCULATE(
        COUNTROWS(fact_warehouse_tasks),
        fact_warehouse_tasks[task_type_code] = "PICK",
        fact_warehouse_tasks[pick_accuracy_flag] = 1
    ),
    CALCULATE(
        COUNTROWS(fact_warehouse_tasks),
        fact_warehouse_tasks[task_type_code] = "PICK"
    ),
    0
) * 100
```

**Target:** >= 99.9%. Alert: < 99.5% for any warehouse or shift triggers investigation.

---

### KPI-03: Order Fill Rate

**Definition:** Percentage of outbound delivery lines shipped at full requested quantity.

**Formula:**
```
Order_Fill_Rate_pct = COUNT(delivery lines WHERE LFIMG >= VRKME)
                      / COUNT(all delivery lines) x 100
```

**DAX:**
```dax
Order Fill Rate % =
DIVIDE(
    CALCULATE(
        COUNTROWS(fact_warehouse_tasks),
        fact_warehouse_tasks[task_type_code] = "SHIP",
        fact_warehouse_tasks[pick_accuracy_flag] = 1
    ),
    CALCULATE(
        COUNTROWS(fact_warehouse_tasks),
        fact_warehouse_tasks[task_type_code] = "SHIP"
    ),
    0
) * 100
```

**Target:** >= 97.5% line fill rate. Alert: < 95% triggers same-day escalation to outbound supervisor.

---

### KPI-04: Space Utilisation

**Definition:** Percentage of total cubic capacity of a zone/warehouse that is currently occupied.

**Formula:**
```
Space_Utilisation_pct = SUM(occupied_volume_mm3) / SUM(cubic_capacity_mm3) x 100
```

**DAX:**
```dax
Space Utilisation % =
DIVIDE(
    SUM(fact_location_occupancy[occupied_volume_mm3]),
    SUM(fact_location_occupancy[cubic_capacity_mm3]),
    0
) * 100
```

**Target by zone:** PRIMARY 75–85%. SECONDARY 65–75%. BULK 55–70%.
Alert: > 90% in any zone triggers capacity review.

---

### KPI-05: FEFO Compliance Rate

**Definition:** Percentage of lot-tracked pick tasks where the correct FEFO-sequenced lot was selected.

**Formula:**
```
FEFO_Compliance_pct = COUNT(PICK tasks WHERE is_fefo_task = 1 AND fefo_compliant = 1)
                      / COUNT(PICK tasks WHERE is_fefo_task = 1) x 100
```

**DAX:**
```dax
FEFO Compliance % =
DIVIDE(
    CALCULATE(
        COUNTROWS(fact_warehouse_tasks),
        fact_warehouse_tasks[is_fefo_task] = 1,
        fact_warehouse_tasks[fefo_compliant] = 1
    ),
    CALCULATE(
        COUNTROWS(fact_warehouse_tasks),
        fact_warehouse_tasks[is_fefo_task] = 1
    ),
    0
) * 100
```

**Target:** 100%. Any FEFO deviation = non-compliant and must be investigated within 4 hours.

---

### KPI-06: Lines Per Person-Hour (LPPH)

**Definition:** Number of pick lines confirmed per direct labour hour, by shift and picking method.

**Formula:**
```
LPPH = COUNT(confirmed PICK tasks in period)
       / (SUM(task_duration_seconds for PICK tasks in period) / 3600)
```

**DAX:**
```dax
LPPH =
VAR TotalLines =
    CALCULATE(
        COUNTROWS(fact_warehouse_tasks),
        fact_warehouse_tasks[task_type_code] = "PICK"
    )
VAR TotalHours =
    DIVIDE(
        CALCULATE(
            SUM(fact_warehouse_tasks[task_duration_seconds]),
            fact_warehouse_tasks[task_type_code] = "PICK"
        ),
        3600
    )
RETURN DIVIDE(TotalLines, TotalHours, BLANK())
```

**Target by method:** RF Batch: >= 160 LPPH. Voice: >= 180 LPPH. Pick-to-Light: >= 280 LPPH.
Alert: < 80% of method-specific target triggers supervisor intervention.

---

### KPI-07: Labour Cost Per Pick Line

**Definition:** Total direct labour cost (wages + benefits) per confirmed pick line, in integer cents.

**Formula:**
```
Cost_per_line_cents =
    (hourly_rate_cents x (1 + benefits_rate))
    x task_duration_seconds / 3600
```

**DAX:**
```dax
Cost Per Line (cents) =
DIVIDE(
    SUMX(
        FILTER(fact_warehouse_tasks, fact_warehouse_tasks[task_type_code] = "PICK"),
        RELATED(dim_operator[hourly_rate_cents])
            * (1 + RELATED(dim_operator[benefits_rate]))
            * DIVIDE(fact_warehouse_tasks[task_duration_seconds], 3600)
    ),
    CALCULATE(
        COUNTROWS(fact_warehouse_tasks),
        fact_warehouse_tasks[task_type_code] = "PICK"
    ),
    BLANK()
)
```

**Target:** Site-specific standard cost per line established in baseline (Phase 0). Improvement
target: 15% reduction within 12 months. All values stored and displayed in integer cents.

---

### KPI-08: Dock Damage Rate

**Definition:** Percentage of inbound pallets identified as damaged at receiving.

**Formula:**
```
Damage_Rate_pct = COUNT(GOODS_RECEIPT tasks WHERE damage_flag = 1)
                  / COUNT(all GOODS_RECEIPT tasks) x 100
```

**DAX:**
```dax
Damage Rate % =
DIVIDE(
    CALCULATE(
        COUNTROWS(fact_warehouse_tasks),
        fact_warehouse_tasks[task_type_code] = "GOODS_RECEIPT",
        fact_warehouse_tasks[damage_flag] = 1
    ),
    CALCULATE(
        COUNTROWS(fact_warehouse_tasks),
        fact_warehouse_tasks[task_type_code] = "GOODS_RECEIPT"
    ),
    0
) * 100
```

**Target:** < 0.5%. Alert: > 1% for any supplier or carrier triggers NCR (Non-Conformance Report).

---

## 11. Analytical Logic

### ABC Velocity Slotting Logic

ABC velocity slotting assigns pick locations to SKUs based on a weighted slot score combining
pick velocity, pick weight, and location ergonomics. The slot score determines golden zone assignment:

**Slot Score Formula:**
```
SlotScore(i) = 0.60 x V_norm(i) + 0.25 x (1 - W_norm(i)) + 0.15 x E_norm(i)
```

Where:
- V_norm = normalised pick velocity (picks per day, min-max scaled to 0–1)
- W_norm = normalised average pick weight (kg, min-max scaled to 0–1; inverted: heavier = lower score)
- E_norm = location ergonomic score (1.0 = waist-to-shoulder; 0.9 = eye level; 0.5 = floor; 0.4 = above head)

**Golden Zone Assignment:**

| Slot Score Percentile | Zone | Height Range | Distance from Dispatch | Typical ABC Class |
|---|---|---|---|---|
| >= P75 | PRIMARY | 75–135 cm (waist to shoulder) | <= 5 m | A-class |
| P50–P75 | SECONDARY | 45–75 cm or 135–165 cm | 5–15 m | B-class |
| P25–P50 | TERTIARY | 20–45 cm or 165–190 cm | 15–30 m | C-class |
| < P25 | BULK | Floor pallet or high rack | > 30 m | C-class or reserve |

**CPOI Override:** High-CPOI SKUs (unit volume > 80th percentile of all SKUs) are demoted from
PRIMARY to SECONDARY regardless of slot score, to prevent large items from blocking primary pick faces.

**Slotting Compliance Definition:**
- A-class SKU in PRIMARY zone: compliant
- B-class SKU in SECONDARY zone: compliant
- C-class SKU in TERTIARY or BULK zone: compliant
- Any other combination: non-compliant (slotting_compliant = 0)

**Slotting Compliance Target:** >= 85% of active pick locations compliant with the current
ABC velocity plan. Alert: < 75% triggers quarterly reslotting review.

**TDR Alert Thresholds:**

| TDR Value | Status | Action |
|---|---|---|
| <= 1.20 | Excellent | No action |
| 1.21–1.30 | Good | Monitor |
| 1.31–1.50 | Acceptable | Review within 30 days |
| 1.51–1.75 | At-risk | Schedule reslotting within 14 days |
| > 1.75 | Breach | Mandatory reslotting within 7 days |

### Dock-to-Stock Stage Breakdown

Dock-to-stock time is decomposed into five measurable stages for root cause analysis:

| Stage | Definition | Timestamp Pair | Target |
|---|---|---|---|
| Stage 1: Gate to Dock | Truck arrival at gate to dock door assignment | T0 (ANLDATUM) to T1 (dock assignment) | <= 15 min |
| Stage 2: Unload | Dock door open to unload complete | T1 to T2 (unload_complete) | <= 30 min |
| Stage 3: Count and Inspect | Unload complete to inspection clearance | T2 to T3 (inspect_clear) | <= 20 min |
| Stage 4: GR Posting | Inspection clearance to GOODS_RECEIPT posted | T3 to T4 (gr_posted_utc) | <= 10 min |
| Stage 5: Putaway | GR posted to final putaway confirmation | T4 to T7 (putaway_complete) | <= 45 min |

Total target: <= 120 minutes standard; <= 90 minutes for cold chain.

### FEFO Deviation Classification

FEFO deviations are classified by root cause to support targeted corrective action:

| Deviation Type | Root Cause | Corrective Action |
|---|---|---|
| OPERATOR_OVERRIDE | Picker scanned wrong lot and confirmed manually | Retraining; alert to shift supervisor |
| SYSTEM_ERROR | EWM directed wrong lot due to configuration error | IT investigation; EWM configuration fix |
| INSUFFICIENT_QTY | Earlier lot has insufficient quantity; second lot supplemented without documenting | Process fix: require supervisor approval for lot splits |
| QUARANTINE_BYPASS | Earlier lot was restricted but restriction not in EWM | Master data fix: update EINLKZ in MCH1 |
| INSUFFICIENT_SHELF_LIFE | Customer requires minimum shelf life exceeding earlier lot | Accepted deviation: document customer approval |

### Labour Productivity Tiers

| Performance Tier | LPPH as % of World-Class Benchmark | Action |
|---|---|---|
| Elite | >= 110% of benchmark | Recognition; best practice documentation |
| World-Class | 90–110% of benchmark | No action |
| Acceptable | 75–90% of benchmark | Coach; identify improvement opportunity |
| Below Standard | 60–75% of benchmark | Formal performance plan; daily LPPH tracking |
| Intervention Required | < 60% of benchmark | Immediate supervisor involvement; task reassignment |

**World-Class Benchmarks by Method:**
- RF Batch pick: 200 LPPH
- Voice-directed: 220 LPPH
- Pick-to-Light: 350 LPPH
- Goods-to-Person (AS/RS): 500 LPPH
- Paper-based: 90 LPPH

### Lot Expiry Alert Escalation

| Alert Tier | Action |
|---|---|
| NORMAL | No action; normal FEFO picking |
| WARNING | Email alert to inventory controller and demand planner; review outbound plan |
| CRITICAL | Same-day alert to Warehouse Manager + Inventory Controller; expedite pick or initiate markdown; consider inter-plant transfer |
| EXPIRED (days_to_expiry <= 0) | Immediate QUARANTINE_IN movement in SAP EWM; blocked from all pick tasks; NCR raised |

---

## 12. Validations and Controls

### VC-01: Task Timestamp Integrity

| Attribute | Detail |
|---|---|
| Name | Task Timestamp Integrity |
| Field/Table | fact_warehouse_tasks: task_start_utc, task_end_utc |
| Rule | task_end_utc > task_start_utc; task_duration_seconds > 0 and < 28800 (8 hours) for any single task |
| Method | Pre-load ADF validation; post-load SQL check COUNT WHERE task_duration_seconds <= 0 |
| Expected Result | Zero tasks with end before start; < 0.1% of tasks with duration > 8 hours (suspected abandoned tasks) |
| Action if Fails | Quarantine to dq_error_log; exclude from LPPH and dock-to-stock KPIs; EWM system admin notified |
| Evidence | TR-01; TR-08 |

### VC-02: FEFO Coverage for Lot-Tracked Picks

| Attribute | Detail |
|---|---|
| Name | FEFO Evaluation Completeness |
| Field/Table | fact_warehouse_tasks: is_fefo_task, fefo_compliant |
| Rule | All rows with is_fefo_task = 1 must have fefo_compliant NOT NULL |
| Method | Post-load SQL: COUNT WHERE is_fefo_task = 1 AND fefo_compliant IS NULL |
| Expected Result | Zero rows with is_fefo_task = 1 and fefo_compliant = NULL |
| Action if Fails | FEFO evaluation logic error; investigate TR-03 pipeline; block FEFO compliance dashboard from displaying until resolved |
| Evidence | BR-01; ISO 9001:2015 §8.5.2 |

### VC-03: Space Utilisation Sum Reconciliation

| Attribute | Detail |
|---|---|
| Name | Occupied Volume Reconciliation |
| Field/Table | fact_location_occupancy |
| Rule | SUM(occupied_volume_mm3) across all active locations should reconcile to SAP EWM total quant volume within 1% |
| Method | Daily post-load reconciliation query vs. SAP /SCWM/BINSRCH total |
| Expected Result | Discrepancy < 1% daily |
| Action if Fails | Investigate missing quant records; check if ADF pipeline captured all quant updates during the 15-minute CDC window |
| Evidence | TR-05; DS-04 |

### VC-04: Pick Accuracy Null Check

| Attribute | Detail |
|---|---|
| Name | Pick Accuracy Flag Completeness |
| Field/Table | fact_warehouse_tasks: pick_accuracy_flag |
| Rule | All PICK task rows must have pick_accuracy_flag NOT NULL |
| Method | Post-load SQL: COUNT WHERE task_type_code = 'PICK' AND pick_accuracy_flag IS NULL |
| Expected Result | Zero null pick_accuracy_flag for PICK tasks |
| Action if Fails | Data pipeline gap; investigate DS-03 quantity fields LFIMG and VRKME for null values |
| Evidence | TR-02; KPI-02 |

### VC-05: Lot Expiry Date Completeness for Lot-Tracked Items

| Attribute | Detail |
|---|---|
| Name | Lot Expiry Date Completeness |
| Field/Table | dim_lot.expiry_date |
| Rule | expiry_date NOT NULL for all lots where dim_material.lot_tracked = TRUE |
| Method | Weekly validation query; join dim_lot to dim_material on sku_id |
| Expected Result | Zero lot-tracked items with missing expiry date |
| Action if Fails | Master data steward alerted; lot flagged EINLKZ = restricted use until expiry date is provided by supplier or determined by QC |
| Evidence | BR-05; BR-07 |

### VC-06: Dock-to-Stock Anomaly Detection

| Attribute | Detail |
|---|---|
| Name | Dock-to-Stock Anomaly |
| Field/Table | fact_warehouse_tasks: dock_to_stock_minutes |
| Rule | dock_to_stock_minutes between 1 and 480 (8 hours) for all valid records |
| Method | Post-load SQL: COUNT WHERE dock_to_stock_minutes > 480 OR dock_to_stock_minutes <= 0 |
| Expected Result | < 0.5% of records outside the 1–480 minute range |
| Action if Fails | Flag as anomalous; investigate whether dock_arrival_utc (T0) was captured correctly; exclude from KPI until verified |
| Evidence | TR-01; BR-06 |

### VC-07: Slotting Compliance Flag Consistency

| Attribute | Detail |
|---|---|
| Name | Slotting Compliance Flag Consistency |
| Field/Table | fact_location_occupancy: slotting_compliant, current_abc_class, golden_zone |
| Rule | If current_abc_class = 'A' AND golden_zone = 'PRIMARY' then slotting_compliant = 1; any A-class SKU in BULK or TERTIARY = 0; any C-class in PRIMARY = 0 |
| Method | Daily validation query checking consistency of slotting_compliant with the classification-zone mapping logic |
| Expected Result | 100% consistency between slotting_compliant flag and the classification-zone matrix |
| Action if Fails | Rerun TR-07 transformation; investigate if ABC classification was updated without triggering slotting compliance recalculation |
| Evidence | TR-07; BR-01 |

---

## 13. Required Evidence

The following evidence artefacts must be produced and stored in the project SharePoint repository
before each phase milestone is signed off by the Data Governance Board:

1. **SAP EWM CDC pipeline validation:** Screenshot of all five ADF pipelines (DS-01 through DS-06)
   showing successful 15-minute incremental extracts with row counts matching EWM audit totals for
   3 consecutive days.

2. **FEFO compliance baseline report:** First month's FEFO compliance rate by warehouse and material
   category, reconciled against SAP EWM lot tracking records. Zero deviations from 100% target must
   be investigated and documented.

3. **Dock-to-stock time baseline:** First week's dock-to-stock times by warehouse, dock door, and
   supplier, showing stage breakdown (TR-01). Baseline agreed by DC Operations Manager.

4. **Space utilisation baseline:** First day's cubic fill rate by zone and warehouse, reconciled to
   SAP EWM /SCWM/BINSRCH report within 1% per VC-03.

5. **Slotting compliance baseline:** Initial slotting compliance rate by warehouse and zone,
   reviewed by the Industrial Engineering team. Non-compliant locations catalogued for reslotting plan.

6. **LPPH baseline by shift and picking method:** First month's LPPH report by shift, warehouse,
   and picking method, agreed by DC Operations Manager as the baseline for the 15% improvement target.

7. **Power BI UAT sign-off:** User acceptance testing evidence from at least two warehouse managers
   and one DC operations director confirming KPI accuracy against SAP EWM source reports.

8. **GS1 SSCC label compliance test:** Evidence that 1,000 test labels scanned at simulated ship
   gate show 0 defects (BR-03 compliance test per Phase 11 go-live readiness criterion).

---

## 14. Dashboard Design

### Power BI Report Structure

**Report File:** Warehouse_Operations_Analytics.pbix
**Refresh Schedule:** Near-real-time via DirectQuery for operational pages; daily Import for
historical trend pages (to manage query load)
**Row-Level Security:** Warehouse-level RLS; DC managers see own warehouse; regional ops sees region;
global ops sees all
**Data Source:** Azure SQL DW (DirectQuery for fact tables; Import for dim tables)

---

### Page 1: Warehouse Operations Command Centre

**Purpose:** Real-time operational overview for DC managers and shift supervisors.

**Visuals:**
- KPI cards (top row, 6 cards): Dock-to-Stock mean (min), Pick Accuracy (%), FEFO Compliance (%), LPPH, Order Fill Rate (%), Space Utilisation (%)
- Multi-row card: Today's SLA breaches — dock-to-stock > 120 min (count), FEFO deviations (count), orders at risk (count)
- Bar chart: Active inbound ASNs by stage (Stage 1: Gate to Dock / Stage 2: Unload / Stage 3: Inspect / Stage 4: GR Posting / Stage 5: Putaway) — dwell time highlighted in red for SLA risk
- Line chart: LPPH by hour for current shift (trailing 8 hours) vs. target reference line
- Gauge: Order fill rate % vs. 97.5% target

**Slicers:** Warehouse, Shift Date (defaults to today), Shift Code
**Refresh:** Near-real-time (DirectQuery); auto-refresh every 5 minutes on command centre page

---

### Page 2: Inbound Performance (Dock-to-Stock)

**Purpose:** Deep-dive into receiving performance for receiving managers and process improvement teams.

**Visuals:**
- Box plot: Dock-to-stock time distribution (min) by warehouse — showing median, P75, P90, and outliers
- Stacked bar chart: Average time per stage (Stage 1–5) by warehouse (colour = stage)
- Bar chart: Top 10 suppliers by average dock-to-stock time (descending)
- Bar chart: Dock damage rate (%) by supplier and carrier — sorted descending
- Table: SLA breach incidents (last 7 days) — ASN, supplier, warehouse, dock, breach minutes, root cause
- Line chart: Dock-to-stock time trend (rolling 13-week average) with 120-minute target line

**Slicers:** Warehouse, Supplier, Carrier, Date Range, Storage Condition
**Drill-through:** Click supplier to supplier scorecard detail

---

### Page 3: Outbound Performance and Pick Accuracy

**Purpose:** Outbound fulfilment and pick accuracy view for outbound supervisors and planners.

**Visuals:**
- KPI cards: Order Fill Rate (%), Pick Accuracy (%), Wave Completion Rate (%), Short Pick Count (today)
- Bar chart: Pick accuracy rate by shift, sorted ascending (worst shift on left, in red below 99.5%)
- Bar chart: Order fill rate by customer priority class (SAME_DAY / NEXT_DAY / STANDARD)
- Scatter plot: Pick accuracy (Y-axis) vs. LPPH (X-axis) per operator — identify high-accuracy/high-speed operators
- Table: Short pick incidents — delivery number, SKU, ordered qty, picked qty, shortage qty, shortage value (€), reason code
- Waterfall chart: Fill rate breakdown — orders complete vs. short-picked vs. not yet picked

**Slicers:** Warehouse, Shift, Date Range, Customer Priority Class, Picking Method

---

### Page 4: Space Utilisation and Slotting Efficiency

**Purpose:** Space and slotting analytics for industrial engineers and warehouse systems teams.

**Visuals:**
- Heatmap: Zone-level cubic fill rate by warehouse and zone (colour gradient: green < 70%, amber 70–85%, red > 85%)
- Bar chart: Over-dense locations (fill_rate > 90%) by zone and warehouse — sorted descending
- Bar chart: Under-utilised locations (fill_rate < 50%) by zone and warehouse
- Gauge: Overall slotting compliance rate (%) vs. 85% target
- Scatter plot: CPOI (Y-axis) vs. current slot score (X-axis); colour = golden_zone; flag high-CPOI items in PRIMARY zone
- Bar chart: Travel Distance Ratio (TDR) by warehouse vs. 1.30 excellent threshold

**Slicers:** Warehouse, Zone, Snapshot Date (date picker), ABC Class
**Drill-down:** Click zone to rack level; click rack to bin level

---

### Page 5: FEFO Compliance Tracking

**Purpose:** Regulatory compliance view for compliance officers, QA managers, and warehouse managers.

**Visuals:**
- Gauge: FEFO compliance rate (%) vs. 100% target (red if < 100%)
- Bar chart: FEFO deviations by warehouse and shift (sorted descending — highest deviation warehouse first)
- Pareto chart: Top 10 SKUs by FEFO deviation count (trailing 90 days)
- Table: FEFO deviation incidents — date, warehouse, SKU, lot picked, correct lot, fefo_deviation_reason, operator_id
- Heatmap: Operator-level FEFO compliance rate by shift (identify systemic training gaps)
- Lot expiry alert table: Lots with expiry_alert_tier = CRITICAL — columns: SKU, lot number, expiry date, days_to_expiry, warehouse, current quantity, open outbound tasks

**Slicers:** Warehouse, Date Range, Material Group, Storage Condition
**Actions:** Export FEFO deviation log (for regulatory audit evidence)

---

### Page 6: Labour Productivity

**Purpose:** Workforce analytics for DC managers, HR, and supply chain finance.

**Visuals:**
- KPI cards: LPPH (current shift), Labour Cost Per Line (cents), Total Direct Hours (today), Short-Paid Hours (gaps > 15 min, today)
- Bar chart: LPPH by shift and warehouse vs. world-class benchmark lines by picking method
- Line chart: LPPH trend by week (trailing 26 weeks) with target and alert reference lines
- Box plot: LPPH distribution by operator — median, P25, P75; operators below P25 flagged
- Bar chart: Labour cost per line (cents) by shift and warehouse (sorted descending — highest cost first)
- Scatter plot: LPPH vs. pick accuracy by operator — quadrant chart (high accuracy/high speed = target)

**Slicers:** Warehouse, Shift, Picking Method, Date Range, Qualification Level

---

## 15. Use Cases

### UC-01: Dock-to-Stock Bottleneck Resolution

**Scenario:** Warehouse NL01 is averaging 148-minute dock-to-stock time, well above the 120-minute SLA.
The DC Manager needs to identify and eliminate the primary bottleneck.

**Steps:**
1. Open Page 2 — Inbound Performance; filter Warehouse = NL01; Date Range = last 30 days
2. Stacked bar chart shows Stage 3 (Inspect) averaging 55 minutes vs. 20-minute target
3. Drill to Stage 3: quality inspection team of 2 inspectors is insufficient for current inbound volume
4. Identify peak arrival times from dock scheduling data (07:00–10:00 UTC Monday-Wednesday)
5. Recommend: add 1 temporary inspector Monday-Wednesday 07:00–12:00; stagger supplier collection windows

**Outcome:** Stage 3 time reduced from 55 to 22 minutes within 2 weeks; dock-to-stock mean reduced
from 148 to 102 minutes.

---

### UC-02: FEFO Deviation Root Cause Analysis

**Scenario:** June 2026 FEFO compliance = 98.7% at warehouse DE01 — below 100% target.
QA Manager needs to identify root cause and implement corrective action.

**Steps:**
1. Open Page 5 — FEFO Compliance; filter Warehouse = DE01; June 2026
2. Pareto chart shows 80% of deviations concentrated in 3 SKUs (all in COLD_CHAIN zone)
3. Heatmap shows NIGHT shift has FEFO compliance of 96.2% vs. 99.8% for EARLY and LATE shifts
4. Table shows deviations occurred primarily on one operator (ID LMNUM-04521)
5. Root cause: LMNUM-04521 completed refresher FEFO training in April but voice system not updated;
   voice prompts not reading lot number clearly for COLD_CHAIN zone due to EWM configuration gap

**Outcome:** EWM voice template updated for COLD_CHAIN zone; LMNUM-04521 retrained; FEFO compliance
returned to 100% within 1 week.

---

### UC-03: Slotting Optimisation Campaign

**Scenario:** Quarterly slotting review reveals TDR = 1.62 at warehouse FR01, triggering mandatory
reslotting within 14 days. The Industrial Engineering team uses the dashboard to plan reslotting.

**Steps:**
1. Open Page 4 — Space Utilisation; filter Warehouse = FR01
2. Slotting compliance rate = 67%; 142 A-class SKUs are in SECONDARY or BULK zones
3. Scatter plot shows 38 high-CPOI items occupying PRIMARY zone locations
4. Export non-compliant locations; generate reslotting plan: move 38 high-CPOI to SECONDARY;
   move top 38 A-class by slot score from SECONDARY to freed PRIMARY locations
5. Execute reslotting over one weekend; confirm new location assignments in SAP EWM

**Outcome:** Slotting compliance improved from 67% to 88%; TDR reduced from 1.62 to 1.24 within
2 weeks of reslotting completion; LPPH increased from 162 to 196.

---

### UC-04: Lot Expiry Management — CRITICAL Alert Response

**Scenario:** Page 5 shows 3 lots of SKU MAT-08820 (pharma, CONTROLLED storage) with expiry_alert_tier
= CRITICAL (days_to_expiry < 90 days). Total value: €340,000. No outbound tasks assigned.

**Steps:**
1. Open Page 5 — FEFO Compliance; filter expiry_alert_tier = CRITICAL
2. Confirm lots are in pick locations at warehouse GB01; current quantity = 580 units
3. Check open demand: Page 2 in Inventory Health report shows no open orders for MAT-08820
4. Escalate to Demand Planner: generate emergency sales promotion; contact 3 alternate customers
5. Parallel track: check inter-plant transfer feasibility — PL01 has pending demand for similar product

**Outcome:** 320 units transferred to PL01 (customer demand confirmed); 180 units sold via emergency
promotion at 15% discount; 80 units returned to supplier under quality agreement. Net write-off
avoided: €294,000.

---

### UC-05: Shift Productivity Benchmarking and Labour Planning

**Scenario:** DC Manager at warehouse ES01 needs to justify a capital investment in pick-to-light
technology. Current RF batch picking LPPH = 145. Must demonstrate ROI vs. pick-to-light target of 280 LPPH.

**Steps:**
1. Open Page 6 — Labour Productivity; filter Warehouse = ES01; Picking Method = RF_BATCH
2. Current LPPH = 145; labour cost per line = 87 cents; daily pick volume = 4,200 lines
3. Daily labour cost = 4,200 x 87 cents = €3,654
4. With pick-to-light at 280 LPPH: same volume requires 4,200/280 = 15 hours vs. current 4,200/145 = 29 hours
5. Labour saving = 14 hours x weighted hourly rate = €322/day = €83,000/year
6. Capital cost pick-to-light (150 positions): ~€210,000. Payback period: 2.5 years

**Outcome:** Business case approved; pick-to-light installation scheduled for Q4 2026.

---

## 16. Recommended Actions

| Result | Recommended Action | Owner | Timeline |
|---|---|---|---|
| Dock-to-stock time > 120 minutes mean | Decompose by stage; identify bottleneck stage; add resource or adjust scheduling | Receiving Supervisor | Within 48 hours of detection |
| FEFO deviation (any) | Investigate root cause within 4 hours; retrain operator if OPERATOR_OVERRIDE; fix EWM config if SYSTEM_ERROR | QA Manager | Within 4 hours |
| Pick accuracy < 99.5% for any shift | Root cause analysis within 24 hours; check mis-scan rate; assess voice template accuracy; operator coaching | Outbound Supervisor | Within 24 hours |
| Space utilisation > 90% in any zone | Inventory health review: identify excess items in that zone for disposition; review putaway strategy | DC Manager | Within 5 business days |
| TDR > 1.50 | Schedule reslotting review within 14 days; execute reslotting within 30 days | Industrial Engineer | Within 14 days |
| LPPH < 80% of method benchmark for a shift | Supervisor coaching session; review task mix for that shift; check if equipment issues are present | Shift Supervisor | Within 24 hours |
| FEFO compliance < 100% for month | Escalate to QA Manager; audit all FEFO deviation incidents; implement systemic corrective action | QA Manager | Within 2 business days |
| Lot expiry_alert_tier = CRITICAL | Escalate to Inventory Controller and Demand Planner; initiate disposition or expedited fulfilment | Inventory Controller | Same business day |
| Order fill rate < 95% | Identify short-pick root causes; check if shortage (inventory issue) or pick process issue; escalate if demand > supply | Outbound Supervisor | Within 24 hours |
| Slotting compliance < 75% | Initiate full slotting review; generate reslotting plan; execute within 30 days | Industrial Engineer | Within 5 business days |

---

## 17. Test Cases

### TC-01: Dock-to-Stock Time Calculation

Create a test GOODS_RECEIPT task with dock_arrival_utc = 2026-06-22 08:00:00 UTC and a corresponding
PUTAWAY task with task_end_utc = 2026-06-22 09:45:00 UTC. Expected dock_to_stock_minutes = 105.
Verify pipeline computes 105 minutes. Tolerance: 0 minutes.

### TC-02: FEFO Compliance Evaluation

Insert two lots for SKU MAT-05511: lot A (expiry 2026-09-01, qty = 50), lot B (expiry 2026-12-01,
qty = 50). Create a PICK task selecting lot B. Expected: fefo_compliant = 0 (lot A available with
earlier expiry). Create a second PICK task selecting lot A. Expected: fefo_compliant = 1.

### TC-03: Pick Accuracy Flag

PICK task with quantity_requested = 10 and quantity_confirmed = 10: pick_accuracy_flag = 1.
PICK task with quantity_requested = 10 and quantity_confirmed = 8: pick_accuracy_flag = 0.
PUTAWAY task (non-pick): pick_accuracy_flag = NULL. Verify all three cases.

### TC-04: Space Utilisation Calculation

Location with cubic_capacity_mm3 = 1,000,000. Quant occupying 600,000 mm3.
Expected fill_rate_pct = 60.0%. is_over_dense = 0 (< 90%). is_under_utilised = 0 (>= 50%).
Test second location with fill_rate = 92%: is_over_dense = 1. Third at 45%: is_under_utilised = 1.

### TC-05: Slotting Compliance Flag

A-class SKU in PRIMARY zone: slotting_compliant = 1.
A-class SKU in BULK zone: slotting_compliant = 0.
B-class SKU in SECONDARY zone: slotting_compliant = 1.
C-class SKU in PRIMARY zone: slotting_compliant = 0.
C-class SKU in TERTIARY zone: slotting_compliant = 1.
Verify all five cases.

### TC-06: LPPH Calculation

Shift with 150 confirmed PICK tasks; total task_duration_seconds = 3,600 seconds (1 hour).
Expected LPPH = 150 / (3600/3600) = 150.0. Verify DAX measure returns 150.0.

### TC-07: Labour Cost Per Line

Operator with hourly_rate_cents = 1500 (€15.00/hr), benefits_rate = 0.28. PICK task duration = 60
seconds (1/60 hour). Expected cost = 1500 x 1.28 x (60/3600) = 33.33 cents (round to 33).
Verify pipeline returns 33 cents. Tolerance: 1 cent (rounding).

### TC-08: Damage Rate Calculation

10 GOODS_RECEIPT tasks; 2 with damage_flag = 1. Expected damage_rate = 20.0%. Verify DAX measure.

### TC-09: Lot Expiry Alert Tier Assignment

Lot with storage_condition = CONTROLLED, days_to_expiry = 45: expiry_alert_tier = CRITICAL (< 90 days).
Lot with storage_condition = AMBIENT (non-SVHC), days_to_expiry = 20: CRITICAL (< 30 days).
Lot with storage_condition = COLD_CHAIN, days_to_expiry = 60: WARNING (45–90 days).
Lot with storage_condition = AMBIENT, days_to_expiry = 90: NORMAL (> 60 days).
Verify all four cases per TR-11 thresholds.

### TC-10: Negative Inventory Rejection at Pick

Bin with 10 units of SKU MAT-00123. Create PICK task for 15 units. Verify: (a) pick confirmation
rejected by EWM; (b) SHORT_PICK exception created; (c) confirmed quantity capped at 10 units;
(d) pick_accuracy_flag = 0.

---

## 18. Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| SAP EWM CDC pipeline lag (> 15 minutes) during peak volume | Medium | Medium | Monitor CDC lag metric in Azure Monitor; alert at 20-minute lag; Operations Command Centre page shows data freshness timestamp |
| FEFO deviation due to EWM lot selection configuration error | Low | Critical | Monthly EWM FEFO configuration audit; automated FEFO compliance alert fires within 1 hour of any deviation; immediate IT investigation |
| Missing dock_arrival_utc (ANLDATUM) when gate reader is offline | Medium | Medium | Fallback to dock door open time (T1) with estimated_arrival flag; root cause: gate reader redundancy via 4G backup |
| YOLOv8 pallet damage model false negative rate > 2% | Medium | High | Manual inspection backstop during first 90 days; monthly model retraining with new damage image samples |
| Operator-level LPPH data missing when LMNUM is null (shared terminals) | High | Medium | Tag shared terminals with a team LMNUM; LPPH computed at shift-team level, not individual operator, for these cases |
| Space utilisation overestimated due to missing quant volume data (MAXVOL = 0) | High | Medium | Flag locations with cubic_capacity_mm3 = 0 as NOT_DIMENSIONED; exclude from utilisation KPI until EWM master data is corrected |
| Pick-to-light or voice system integration gap causing FEFO bypass | Low | Critical | Integration test: 100 test picks with lot-tracked items before go-live; verify EWM directs correct lot in all cases |
| Cold chain temperature excursion during prolonged dock-to-stock time | Low | Critical | Temperature monitoring alert at 60 minutes for CHILLED/FROZEN receipts (separate from dock-to-stock KPI); product QA quarantine if excursion detected |

---

## 19. Implementation Checklist

- [ ] **1.** Confirm SAP EWM is the active WM system for all sites in scope; document which sites remain on SAP WM legacy and plan partial data availability handling
- [ ] **2.** Configure SAP EWM Change Data Capture (CDC) with 15-minute incremental extract windows; validate CDC does not miss tasks created and confirmed within the same 15-minute window
- [ ] **3.** Deploy ADF pipeline DS-01 (transfer order history); validate row count against EWM report /SCWM/TOREP for 3 consecutive days
- [ ] **4.** Deploy ADF pipelines DS-02 (goods receipt / dock), DS-03 (outbound delivery), DS-04 (location / quant), DS-05 (labour resource), DS-06 (lot master); validate each pipeline individually
- [ ] **5.** Create all fact and dimension tables in Azure SQL per Section 6 data model; apply monthly partitioning on fact_warehouse_tasks; apply daily partitioning on fact_location_occupancy
- [ ] **6.** Implement TR-01 (dock-to-stock) and TR-02 (pick accuracy); unit test with 20 test tasks per TC-01 and TC-03
- [ ] **7.** Implement TR-03 (FEFO compliance evaluation); unit test with lot-tracked SKU scenarios per TC-02; confirm 0% false-positive rate on non-lot-tracked tasks
- [ ] **8.** Implement TR-04 (order fill rate), TR-05 (space utilisation), TR-06 (CPOI), TR-07 (slotting compliance); unit test each per test cases TC-04, TC-05
- [ ] **9.** Implement TR-08 (LPPH), TR-09 (labour cost per line), TR-10 (dock damage rate), TR-11 (lot expiry alerting), TR-12 (TDR); unit test per TC-06, TC-07, TC-09
- [ ] **10.** Load dim_location from SAP EWM location master; validate cubic_capacity_mm3 > 0 for all active pick locations; resolve NOT_DIMENSIONED locations with EWM system admin
- [ ] **11.** Load dim_lot from SAP batch master (MCH1); validate expiry_date completeness for all lot-tracked SKUs per VC-05
- [ ] **12.** Implement all seven validation controls (VC-01 through VC-07); run against first 3 days of production data; document results
- [ ] **13.** Build Power BI report with all six pages per Section 14 specifications; configure DirectQuery for operational pages; configure daily Import for trend pages
- [ ] **14.** Configure row-level security at warehouse level; test with DC manager accounts (own warehouse only visible); test global ops account (all visible)
- [ ] **15.** Conduct UAT with two warehouse managers and one DC operations director per Section 13 evidence item 7; obtain written sign-off
- [ ] **16.** Configure Operations Command Centre page (Page 1) for 5-minute auto-refresh; test on representative shift with live EWM data
- [ ] **17.** Execute GS1 SSCC label compliance test: 1,000 test labels scanned at simulated ship gate; confirm 0 defects (BR-03)
- [ ] **18.** Execute FEFO negative inventory test (TC-10) in UAT environment; confirm EWM rejects the pick and system records SHORT_PICK exception
- [ ] **19.** Train warehouse managers, shift supervisors, and QA managers (workshop per role per Section 11 of the broader WMS Implementation Guide)
- [ ] **20.** Document data lineage from SAP EWM source tables to Power BI visuals in the Data Governance Catalogue; obtain Data Governance Board sign-off

---

## 20. Validation Checklist

- [ ] **1.** ADF pipeline task counts for all six sources reconcile to SAP EWM audit reports within 0.1% for 5 consecutive business days
- [ ] **2.** Dock-to-stock time calculations for 10 randomly selected ASNs manually verified against SAP EWM task timestamps; tolerance 0 minutes
- [ ] **3.** FEFO compliance evaluation tested with 20 lot-tracked picks; fefo_compliant flag matches expected value for all 20 (including 5 intentional deviations)
- [ ] **4.** Space utilisation fill rates for 10 randomly selected zones reconcile to SAP EWM /SCWM/BINSRCH report within 1%
- [ ] **5.** Slotting compliance flags verified for 50 randomly selected locations; expected flag matches actual flag for all 50
- [ ] **6.** LPPH calculated for 3 shifts manually from EWM task logs; result matches Power BI measure within 0.5 lines/hour
- [ ] **7.** Labour cost per line spot-checked for 5 operators with known hourly rates; result within 1 cent of manual calculation
- [ ] **8.** Order fill rate for 1 week's outbound deliveries verified against SAP VL06O report within 0.1%
- [ ] **9.** Row-level security tested: DC manager account for NL01 cannot see DE01 data in any visual or exported file
- [ ] **10.** Operations Command Centre page (Page 1) confirmed to refresh within 5 minutes of a test PICK task being confirmed in SAP EWM
- [ ] **11.** Lot expiry alert tiers validated for 10 lots with known expiry dates and storage conditions; tier assignments match TR-11 thresholds for all 10
- [ ] **12.** Damage rate calculation verified: 5 test GOODS_RECEIPT tasks with damage_flag = 1 out of 20 total; expected damage_rate = 25.0%; Power BI returns 25.0%
- [ ] **13.** FEFO deviation alert email received by QA Manager within 1 hour of a test FEFO deviation inserted in the test environment
- [ ] **14.** TDR calculation for warehouse FR01 cross-checked against manual travel distance estimation by Industrial Engineer; result within 5%

---

## 21. Pending Information

**PI-01 — SAP EWM vs. SAP WM site list:** Confirm which of the 40 countries are live on SAP EWM vs.
SAP WM. The transfer order extract pipeline uses different source tables (/SCWM/TOCO for EWM;
LTAP for WM). WM sites will have limited FEFO and location dimension data until EWM upgrade.

**PI-02 — Gate reader availability and ANLDATUM capture:** Confirm whether all DC sites have a gate
management reader that populates ANLDATUM in SAP EWM. Sites without gate readers will use dock door
open time as the dock-to-stock start timestamp (T1 fallback instead of T0 per TR-01).

**PI-03 — LMNUM null handling for shared terminals:** Confirm the policy for shared picking terminals
where multiple operators share the same device without individual login. LPPH at the individual
operator level will not be available for these sites; shift-level LPPH only.

**PI-04 — Cubic dimensions availability in EWM location master:** Confirm that MAXVOL is populated
in the SAP EWM /SCWM/LGPLA location master for all active pick and reserve locations. Sites where
MAXVOL = 0 require an engineering survey to measure and load cubic dimensions before space utilisation
KPIs can be activated.

**PI-05 — YOLOv8 dock camera hardware:** Confirm availability and specification of dock-mounted cameras
at inbound receiving stations for the pallet damage detection model (Section 7 of the broader WMS
Implementation Guide, Phase 4). Sites without cameras will rely on manual damage flag entry only.

**PI-06 — Picking method identification in EWM task records:** Confirm whether the SAP EWM task record
distinguishes between RF batch, voice, and pick-to-light picking methods in the BWLVS field or
through a linked resource qualification. Required for method-specific LPPH benchmarking.

**PI-07 — Minimum remaining shelf life policy by customer:** Confirm whether individual customers
have contractual minimum remaining shelf life requirements that override the standard storage
condition thresholds in TR-11. If so, the lot expiry alert model must be parameterised by
customer-material combination.

---

## 22. Implementation Roadmap

| Week | Phase | Deliverable | Owner | Dependencies |
|---|---|---|---|---|
| 1 | Infrastructure | Azure SQL DW provisioned; EWM CDC access configured; network connectivity validated | IT Infrastructure | SAP EWM RFC authorisation granted |
| 1–2 | Infrastructure | SAP EWM CDC change pointers enabled for all target tables; 15-minute extract schedule tested | SAP Basis + Data Engineering | PI-01 resolved: EWM vs WM site list |
| 2 | Data Ingestion | ADF pipeline DS-01 (transfer order history) deployed; 3-month backfill complete | Data Engineering | Azure SQL ready |
| 2–3 | Data Ingestion | ADF pipelines DS-02 (goods receipt), DS-03 (outbound), DS-04 (location/quant) deployed | Data Engineering | PI-02 resolved: gate reader availability |
| 3 | Data Ingestion | ADF pipelines DS-05 (labour resource) and DS-06 (lot master) deployed | Data Engineering | PI-03 resolved: LMNUM shared terminal policy |
| 4 | Data Model | All fact and dimension tables created in Azure SQL per Section 6; indexes and partitioning applied | Data Engineering | All pipelines delivering data |
| 4–5 | Transformation | TR-01 to TR-06 implemented and unit tested | Data Engineering | fact_warehouse_tasks populated |
| 5 | Transformation | TR-07 to TR-12 implemented and unit tested | Data Engineering | dim_location cubic dimensions loaded (PI-04) |
| 5 | Validation | VC-01 to VC-07 implemented; first validation report produced for Data Governance Board | Data Quality Lead | All transformations complete |
| 6 | Validation | FEFO compliance evaluation (VC-02) tested with 20 lot-tracked picks including 5 intentional deviations | QA Manager + Data Engineering | TR-03 complete; lot-tracked SKUs in test data |
| 7 | Dashboard | Power BI Page 1 (Command Centre) and Page 2 (Inbound) built; DirectQuery configured | Power BI Developer | fact_warehouse_tasks with dock_to_stock_minutes |
| 7–8 | Dashboard | Power BI Pages 3 (Outbound), 4 (Space/Slotting), 5 (FEFO), 6 (Labour) built | Power BI Developer | All fact tables populated |
| 8 | Dashboard | Row-level security configured; 5-minute auto-refresh enabled on Page 1 | Power BI Developer + IT | |
| 9 | UAT | UAT executed with 2 warehouse managers and 1 DC operations director | Analytics Lead | All 6 pages complete |
| 10 | UAT | UAT defects resolved; retest; sign-off obtained | Analytics Lead | |
| 10 | Testing | GS1 SSCC label compliance test: 1,000 labels; 0 defects required | DC Operations Manager | Label printer config complete |
| 11 | Testing | FEFO negative test (TC-10), damage rate test (TC-08), TDR cross-check with IE team | QA Manager + IE Team | |
| 12 | Training | Warehouse manager and QA manager training sessions (dashboard navigation, alert protocols) | Analytics Lead | Dashboard final |
| 13 | Automation | Daily and near-real-time ADF schedule confirmed; Azure Monitor alerts configured | Data Engineering | UAT sign-off |
| 14 | Go-Live | Production go-live: all in-scope EWM sites (phased by region) | Programme Manager | All checklists complete |
| 14 | Go-Live | Post go-live monitoring: daily KPI review and pipeline health check for first 5 business days | Analytics Lead | |
| 15 | Hypercare | Active support for all warehouse managers; same-day resolution of data issues | Analytics Lead | Go-live stable |
| 16 | Handover | Runbook delivered; data governance catalogue updated; quarterly slotting review cadence agreed | Analytics Lead | Hypercare complete |

---

## References

- Chopra, S. & Meindl, P. (2016). *Supply Chain Management*, 6th Ed. Pearson.
- Ballou, R.H. (2004). *Business Logistics/Supply Chain Management*, 5th Ed. Pearson.
- Christopher, M. (2022). *Logistics and Supply Chain Management*, 6th Ed. FT Publishing.
- Frazelle, E.H. (2002). *World-Class Warehousing and Material Handling*. McGraw-Hill.
- ASCM (2024). *APICS Dictionary*, 16th Ed.
- ASCM (2019). *SCOR Digital Standard*.
- ISO 9001:2015 §8.5.2 — Identification and Traceability.
- ISO 28000:2022 — Supply Chain Security Management Systems.
- GS1 General Specifications v23.0.
- EU Regulation 1907/2006 (REACH).
- SAP SE (2024). *SAP Extended Warehouse Management (EWM) Configuration Guide*. SAP Help Portal.
- Google (2024). *OR-Tools Vehicle Routing and Combinatorial Optimization*. Apache-2.0.
- Jocher, G. et al. (2023). *Ultralytics YOLOv8*. AGPL-3.0.
- Chen, T. & Guestrin, C. (2016). XGBoost: A Scalable Tree Boosting System. *KDD 2016*, 785–794.
- Erlang, A.K. (1909). The theory of probabilities and telephone conversations.
  *Nyt Tidsskrift for Matematik B*, 20, 33–39.
