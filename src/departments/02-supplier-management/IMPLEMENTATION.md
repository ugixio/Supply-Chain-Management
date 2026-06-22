# Supplier Performance Analytics — Implementation Specification

> Analytical implementation document for a data / BI / automation team.
> Scope: Supplier Scorecard (OTD, OTIF, PPM, NCR), Supplier Concentration Risk
> (HHI), Delivery Tracking, and Early Warning System.
> Context: €50B multinational, 40 countries, SAP S/4HANA + SAP Ariba,
> Power BI, Azure SQL, Python, Power Automate. 10,000+ active suppliers.

---

## 1. Executive Summary

This document specifies the end-to-end analytical implementation for monitoring
supplier performance across the global supply base. It defines the data sources,
data model, transformation logic, business rules, KPI formulas, validations, and
dashboard design required to produce a trustworthy, auditable supplier scorecard
and risk early-warning capability.

The deliverable is a Power BI solution backed by an Azure SQL analytical model,
refreshed daily, that allows Supplier Quality Engineers (SQE), Category Managers,
and Procurement leadership to (a) rank supplier performance objectively,
(b) detect deterioration before it impacts production, and (c) quantify
concentration risk per category. All KPIs reconcile to SAP source tables.

---

## 2. Analysis Objective

Provide a single, governed source of truth for supplier performance and risk that:
- Computes the weighted supplier scorecard (Delivery 40 %, Quality 30 %,
  Commercial 20 %, Soft 10 %) consistently for every active supplier.
- Tracks delivery reliability (OTD, OTIF) and quality (PPM, NCR rate) by supplier,
  plant, material group, and period.
- Quantifies supplier concentration risk (HHI) per purchasing category.
- Flags suppliers at risk of falling below the APPROVED threshold (<75) within
  90 days.
- Is fully reconcilable to SAP S/4HANA (MM, QM, FI) source data.

---

## 3. Scope

**In scope**: all active direct-material suppliers in SAP vendor master; goods
receipts, quality notifications, incoming inspection results, invoice matching,
and spend data for the trailing 24 months.

**Out of scope**: indirect/MRO tail suppliers below €10,000 annual spend
(reported separately); one-time vendors; intercompany suppliers (flagged and
excluded from external scorecard).

---

## 4. Business Questions

- Which suppliers are below the APPROVED scorecard threshold (<75) this month?
- What is the OTD and OTIF trend per supplier over the last 12 months?
- Which suppliers contribute the most defective PPM by material group?
- Which purchasing categories have dangerous supplier concentration (HHI ≥ 5,000)?
- Which suppliers show a deteriorating 3-month trend versus their 12-month average?
- How many suppliers moved rating band (e.g., APPROVED → CONDITIONAL) this month?
- What is the on-time delivery performance by plant and by Incoterm?
- Which single-source materials carry the highest supply continuity risk?
- What is the data completeness of scorecard inputs per supplier?
- Which suppliers have open NCRs aging beyond their CAPA due date?

---

## 5. Data Sources

### Source 1 — Goods Receipts (Delivery performance)
- **Source Name**: Goods Receipt history
- **Origin System**: SAP S/4HANA (MM)
- **Report/Table/Query**: MKPF (header) + MSEG (items); movement types 101/102
- **Data Owner**: Logistics / Inbound Operations
- **Update Frequency**: Daily (incremental load by posting date)
- **Required Fields**: `MBLNR, MJAHR, ZEILE, MATNR, LIFNR, WERKS, MENGE, BUDAT,
  EBELN, EBELP`
- **Critical Fields**: `LIFNR` (supplier), `BUDAT` (GR posting date), `EBELN/EBELP`
  (PO reference), `MENGE` (received qty)
- **Primary/Logical Key**: `MBLNR + MJAHR + ZEILE`
- **Required Validations**: every GR line must join to a valid PO line; `MENGE > 0`
  for 101; non-null `LIFNR`
- **Possible Errors**: GR posted without PO reference (free-text); reversal (102)
  not netted; back-dated postings shifting OTD period
- **Extraction Evidence**: row count + sum(MENGE) per posting day logged to
  `etl_audit_log`; reconcile to SAP MB51 report

### Source 2 — Purchase Order Schedule Lines (Confirmed delivery dates)
- **Source Name**: PO confirmed delivery dates
- **Origin System**: SAP S/4HANA (MM)
- **Report/Table/Query**: EKKO (header) + EKPO (item) + EKET (schedule lines) +
  EKES (confirmations)
- **Data Owner**: Procurement Operations
- **Update Frequency**: Daily
- **Required Fields**: `EBELN, EBELP, ETENR, EINDT, MENGE, LIFNR, MATNR, WERKS`
- **Critical Fields**: `EINDT` (confirmed delivery date — used as OTD baseline),
  `MENGE` (ordered qty)
- **Primary/Logical Key**: `EBELN + EBELP + ETENR`
- **Required Validations**: `EINDT` not null and not in distant past for open lines;
  confirmed qty ≤ ordered qty
- **Possible Errors**: missing supplier confirmation (use requested date as
  fallback — flag); multiple reschedules overwriting original promise
- **Extraction Evidence**: count of PO lines per supplier reconciled to SAP ME2L

### Source 3 — Quality Notifications (NCR)
- **Source Name**: Quality Notifications / NCR
- **Origin System**: SAP S/4HANA (QM)
- **Report/Table/Query**: QMEL (header) + QMFE (items); notification types Q1/Q2
- **Data Owner**: Quality / SQE
- **Update Frequency**: Daily
- **Required Fields**: `QMNUM, QMART, LIFNUM, MATNR, ERDAT, QMDAT, AUSWIRK,
  RKMNG (defect qty)`
- **Critical Fields**: `LIFNUM` (supplier), `ERDAT` (creation date), defect severity
- **Primary/Logical Key**: `QMNUM`
- **Required Validations**: supplier-attributable NCRs only; defect qty ≥ 0
- **Possible Errors**: internal-cause NCRs mis-coded to supplier; missing CAPA link
- **Extraction Evidence**: NCR count per supplier reconciled to SAP QM12

### Source 4 — Incoming Inspection Results (PPM)
- **Source Name**: Incoming inspection lot results
- **Origin System**: SAP S/4HANA (QM)
- **Report/Table/Query**: QALS (inspection lot) + QAMR (results)
- **Data Owner**: Quality
- **Update Frequency**: Daily
- **Required Fields**: `PRUEFLOS, MATNR, LIFNR, LOSMENGE, FEHLER (defects), BUDAT`
- **Critical Fields**: `LOSMENGE` (inspected qty), defect count
- **Primary/Logical Key**: `PRUEFLOS`
- **Required Validations**: `LOSMENGE > 0`; defects ≤ inspected qty
- **Possible Errors**: skip-lot inspections with zero recorded qty distorting PPM
- **Extraction Evidence**: sum(defects), sum(inspected) per supplier per month

### Source 5 — Invoice Matching (Commercial sub-score)
- **Source Name**: Invoice verification / 3-way match
- **Origin System**: SAP S/4HANA (FI/MM)
- **Report/Table/Query**: RBKP (invoice header) + RSEG (items)
- **Data Owner**: Accounts Payable
- **Update Frequency**: Daily
- **Required Fields**: `BELNR, GJAHR, LIFNR, EBELN, EBELP, WRBTR, MENGE,
  match_status`
- **Critical Fields**: price/quantity variance, auto-match flag
- **Primary/Logical Key**: `BELNR + GJAHR + buzei`
- **Required Validations**: invoice references valid PO; variance computed vs PO price
- **Possible Errors**: manual-posted invoices without PO link
- **Extraction Evidence**: invoice count and match-rate per supplier

### Source 6 — Vendor Master & Category
- **Source Name**: Supplier master
- **Origin System**: SAP S/4HANA (MM) + SAP Ariba SLP
- **Report/Table/Query**: LFA1 + LFB1 + LFM1; Ariba SLP supplier profile
- **Data Owner**: Master Data Management (MDM-S)
- **Update Frequency**: Daily
- **Required Fields**: `LIFNR, NAME1, LAND1, purchasing_category, kraljic_segment,
  status (active/blocked), DUNS, GLN`
- **Critical Fields**: `purchasing_category`, `status`, country
- **Primary/Logical Key**: `LIFNR`
- **Required Validations**: no duplicate active records per DUNS; category populated
- **Possible Errors**: blocked suppliers still receiving GRs; missing category
- **Extraction Evidence**: active supplier count reconciled to SAP XK03 list

### Source 7 — Spend (for HHI)
- **Source Name**: Supplier spend (12-month trailing)
- **Origin System**: SAP S/4HANA (FI/MM) or BW
- **Report/Table/Query**: aggregated invoice spend by supplier × category
- **Data Owner**: Procurement Analytics
- **Update Frequency**: Monthly
- **Required Fields**: `LIFNR, purchasing_category, spend_amount, currency, period`
- **Critical Fields**: `spend_amount` (in group currency), category
- **Primary/Logical Key**: `LIFNR + category + period`
- **Required Validations**: spend converted to group currency at month-end rate
- **Possible Errors**: FX conversion gaps; credit memos not netted
- **Extraction Evidence**: total spend reconciled to AP ledger control total

---

## 6. Data Model

Star schema (Azure SQL → Power BI import model):

**Fact tables**
- `fact_delivery` — grain: one GR line matched to its PO schedule line.
- `fact_quality_ncr` — grain: one NCR item.
- `fact_inspection` — grain: one inspection lot.
- `fact_invoice_match` — grain: one invoice line.
- `fact_scorecard_monthly` — grain: one supplier × month (computed output).
- `fact_spend` — grain: one supplier × category × month.

**Dimension tables**
- `dim_supplier` (LIFNR, name, country, category, kraljic_segment, status)
- `dim_material` (MATNR, description, material_group)
- `dim_plant` (WERKS, name, region, country)
- `dim_date` (date, month, quarter, year, fiscal_period)
- `dim_category` (category code, category name, category manager)

**Relationships**
- All facts → `dim_supplier` via `LIFNR` (many-to-one, single direction).
- `fact_delivery`, `fact_quality_ncr`, `fact_inspection` → `dim_material` via MATNR.
- All facts → `dim_date` via posting/creation date.
- `fact_delivery` → `dim_plant` via WERKS.
- `fact_spend`, `fact_scorecard_monthly` → `dim_category` via category.

---

## 7. Data Dictionary

### Table: fact_delivery
- **Description**: Each goods receipt line matched to its confirmed PO schedule line,
  with on-time and in-full flags.
- **Granularity**: one row per GR line (`MBLNR+MJAHR+ZEILE`).
- **Required Fields**:
  | Field | Type | Description |
  |---|---|---|
  | gr_doc_key | varchar | MBLNR+MJAHR+ZEILE |
  | lifnr | varchar | Supplier number |
  | matnr | varchar | Material |
  | werks | varchar | Plant |
  | po_key | varchar | EBELN+EBELP+ETENR |
  | confirmed_date | date | EINDT (promise) |
  | gr_date | date | BUDAT (actual receipt) |
  | ordered_qty | decimal(18,3) | Schedule line qty |
  | received_qty | decimal(18,3) | GR qty (101 minus 102) |
  | on_time_flag | bit | 1 if gr_date ≤ confirmed_date + grace |
  | in_full_flag | bit | 1 if received_qty ≥ 0.98 × ordered_qty |
- **Primary Key**: `gr_doc_key`
- **Relationships**: → dim_supplier, dim_material, dim_plant, dim_date
- **Required Transformations**: net 102 reversals; compute flags (see §8)
- **Cleaning Rules**: drop GR lines with no PO link to a separate exception table
- **Validations**: received_qty ≥ 0; confirmed_date not null
- **Use in Analysis**: OTD, OTIF KPIs; delivery tracking

### Table: fact_quality_ncr
- **Description**: Supplier-attributable non-conformance records.
- **Granularity**: one row per NCR item (`QMNUM`+item).
- **Required Fields**: ncr_key, lifnr, matnr, created_date, severity (Critical/Major/Minor),
  defect_qty, capa_due_date, capa_closed_date, status
- **Primary Key**: ncr_key
- **Relationships**: → dim_supplier, dim_material, dim_date
- **Required Transformations**: map QM codes → severity; compute NCR age
- **Cleaning Rules**: exclude internal-cause NCRs (cause code filter)
- **Validations**: defect_qty ≥ 0; severity in allowed list
- **Use in Analysis**: NCR rate, quality sub-score, CAPA aging

### Table: fact_inspection
- **Description**: Incoming inspection lots with defect counts for PPM.
- **Granularity**: one row per inspection lot (`PRUEFLOS`).
- **Required Fields**: lot_key, lifnr, matnr, inspected_qty, defect_qty, inspection_date
- **Primary Key**: lot_key
- **Relationships**: → dim_supplier, dim_material, dim_date
- **Required Transformations**: exclude skip-lot zero-qty rows
- **Validations**: inspected_qty > 0; defect_qty ≤ inspected_qty
- **Use in Analysis**: PPM calculation

### Table: fact_scorecard_monthly
- **Description**: Computed monthly supplier scorecard with sub-scores and rating.
- **Granularity**: one row per supplier × month.
- **Required Fields**: lifnr, period, otd_pct, otif_pct, rft_pct, ppm, ncr_rate,
  invoice_accuracy_pct, po_variance_pct, soft_score, delivery_sub, quality_sub,
  commercial_sub, soft_sub, composite_score, rating, data_completeness_pct
- **Primary Key**: lifnr + period
- **Relationships**: → dim_supplier, dim_date
- **Required Transformations**: full scoring pipeline (see §10)
- **Validations**: composite_score in [0,100]; rating matches threshold table
- **Use in Analysis**: scorecard dashboard, rating-band movement, early warning input

### Table: fact_spend
- **Description**: Supplier spend by category for concentration (HHI).
- **Granularity**: supplier × category × month.
- **Required Fields**: lifnr, category, period, spend_group_ccy
- **Primary Key**: lifnr + category + period
- **Relationships**: → dim_supplier, dim_category, dim_date
- **Validations**: spend ≥ 0; FX rate applied
- **Use in Analysis**: HHI per category

---

## 8. Transformation Rules

1. **Net GR reversals**: for each PO line, `received_qty = SUM(101 qty) − SUM(102 qty)`.
2. **OTD flag**: `on_time_flag = 1 IF gr_date <= DATEADD(day, grace_days, confirmed_date)`,
   where `grace_days = 0` (automotive plants) or `1` (general). Parameterised per plant.
3. **In-full flag**: `in_full_flag = 1 IF received_qty >= 0.98 * ordered_qty`.
4. **OTIF flag** (order level): aggregate to PO; `otif = 1 IF MIN(on_time_flag)=1 AND
   MIN(in_full_flag)=1 across all lines of the PO`.
5. **Confirmed-date fallback**: if `EINDT` (confirmation) is null, use requested
   delivery date and set `date_source = 'REQUESTED'` (flag for transparency).
6. **PPM aggregation**: monthly per supplier `PPM = SUM(defect_qty)/SUM(inspected_qty)
   * 1,000,000`.
7. **NCR severity mapping**: QM catalog code → {Critical, Major, Minor} via lookup table.
8. **NCR age**: `NCR_age_days = DATEDIFF(day, created_date, COALESCE(capa_closed_date, TODAY()))`.
9. **Invoice accuracy**: monthly per supplier `= COUNT(auto_matched)/COUNT(invoices)*100`.
10. **PO price variance**: `avg_price_deviation_pct = AVG(ABS(invoice_price - po_price)/po_price)*100`.
11. **Spend FX conversion**: convert to group currency using month-end ECB rate from
    `dim_fx_rate`.
12. **Data completeness**: per supplier-month, `completeness = COUNT(non-null KPI inputs)/
    COUNT(expected inputs)*100`; flag scorecards with <80 % as provisional.

---

## 9. Business Rules

### Rule: Supplier in scope for scorecard
- **Description**: Only active external direct suppliers with minimum activity.
- **Logic Condition**: `dim_supplier.status = 'ACTIVE' AND is_intercompany = 0 AND
  trailing_12m_GR_lines >= 6`
- **Expected Result**: supplier appears in `fact_scorecard_monthly`.
- **Example**: supplier with 3 GRs in 12 months is excluded (insufficient data).
- **Exception**: strategic new suppliers with NPI agreements included from month 1.
- **Required Evidence**: in-scope supplier list with inclusion reason logged.

### Rule: OTD grace period by plant
- **Description**: On-time tolerance varies by plant criticality.
- **Logic Condition**: `grace_days = lookup(plant_grace_table, werks)`
- **Expected Result**: consistent OTD flag computation per plant.
- **Example**: Plant DE10 grace=0; Plant BR40 grace=1.
- **Exception**: customer-directed drop-ship uses customer-required date.
- **Required Evidence**: plant grace configuration table version-controlled.

### Rule: Rating band assignment
- **Description**: Map composite score to rating band.
- **Logic Condition**: PREFERRED ≥90; APPROVED ≥75; CONDITIONAL ≥60; PROBATION ≥45;
  DISQUALIFIED <45.
- **Expected Result**: `rating` column populated per band.
- **Example**: composite 71.3 → APPROVED.
- **Exception**: manual quality hold overrides to PROBATION regardless of score.
- **Required Evidence**: rating distribution reconciled to threshold logic.

### Rule: Concentration risk flag
- **Description**: Flag categories with dangerous supplier concentration.
- **Logic Condition**: `HHI_category >= 5000` → flag = HIGH; `>=2500` → MEDIUM.
- **Expected Result**: category risk flag for dual-source action.
- **Example**: category with one supplier at 80 % share → HHI ≈ 6,800 → HIGH.
- **Exception**: strategic single-source by design (board-approved) → annotate.
- **Required Evidence**: HHI per category recomputed and stored monthly.

### Rule: Early-warning trigger
- **Description**: Flag suppliers likely to drop below APPROVED.
- **Logic Condition**: `composite_3m_avg < composite_12m_avg - 8 OR
  ml_deterioration_prob >= 0.6`
- **Expected Result**: supplier added to watch list; SQE notified.
- **Example**: 12m avg 82, 3m avg 73 → −9 → triggered.
- **Exception**: one-off event with documented containment.
- **Required Evidence**: watch-list entry with trigger reason + timestamp.

---

## 10. KPIs and Formulas

### KPI: On-Time Delivery (OTD)
- **Objective**: measure supplier delivery reliability against promise.
- **Formula (DAX)**:
  `OTD % = DIVIDE( CALCULATE(COUNTROWS(fact_delivery), fact_delivery[on_time_flag]=1),
  COUNTROWS(fact_delivery) ) * 100`
- **Data Source**: fact_delivery
- **Calculation Level**: supplier / plant / material group / month
- **Frequency**: daily refresh, monthly reporting
- **Owner**: SQE
- **Interpretation**: % of GR lines received on or before confirmed date.
- **Thresholds**: Green ≥95 %, Yellow 90–95 %, Red <90 %
- **Traffic Light**: per thresholds
- **Recommended Action**: Red → delivery improvement plan; expedite review.
- **Validation vs Source**: reconcile flagged-on-time count to SAP MB51 sample.

### KPI: On-Time In-Full (OTIF)
- **Objective**: measure complete and on-time order fulfilment.
- **Formula (DAX)**:
  `OTIF % = DIVIDE( CALCULATE(DISTINCTCOUNT(fact_delivery[po_key]),
  fact_delivery[otif_order_flag]=1), DISTINCTCOUNT(fact_delivery[po_key]) ) * 100`
- **Data Source**: fact_delivery (order-level aggregation)
- **Calculation Level**: supplier / month
- **Frequency**: monthly
- **Owner**: SQE
- **Interpretation**: % of orders delivered on time AND in full.
- **Thresholds**: Green ≥92 %, Yellow 85–92 %, Red <85 %
- **Recommended Action**: Red → root-cause split vs. quantity shortfall.
- **Validation vs Source**: order-level recompute vs SAP ME2L sample.

### KPI: Defective PPM
- **Objective**: quality of incoming material per million units.
- **Formula (SQL)**:
  `PPM = SUM(defect_qty) * 1000000.0 / NULLIF(SUM(inspected_qty),0)`
- **Data Source**: fact_inspection
- **Calculation Level**: supplier / material group / month
- **Frequency**: monthly
- **Owner**: Quality
- **Interpretation**: defect concentration; lower is better.
- **Thresholds**: Green <500, Yellow 500–1,000, Red >1,000 (general industry)
- **Recommended Action**: Red → containment + 8D + supplier audit.
- **Validation vs Source**: sum(defects)/sum(inspected) vs SAP QGA3.

### KPI: NCR Rate
- **Objective**: frequency of non-conformances per receipt.
- **Formula (DAX)**:
  `NCR Rate % = DIVIDE(COUNTROWS(fact_quality_ncr), COUNTROWS(fact_delivery)) * 100`
- **Data Source**: fact_quality_ncr, fact_delivery
- **Calculation Level**: supplier / month
- **Frequency**: monthly
- **Owner**: SQE
- **Interpretation**: lower is better; spikes indicate process loss of control.
- **Thresholds**: Green <2 %, Yellow 2–5 %, Red >5 %
- **Recommended Action**: Red → CAPA review; scorecard quality sub-score impact.
- **Validation vs Source**: NCR count vs SAP QM12.

### KPI: Composite Scorecard
- **Objective**: single weighted performance index per supplier.
- **Formula**:
  ```
  Delivery   = 0.35*OTD_score + 0.45*OTIF_score + 0.20*RFT_score
  Quality    = 0.60*PPM_score + 0.40*NCR_score
  Commercial = 0.70*Invoice_accuracy + 0.30*PO_variance_score
  Composite  = 0.40*Delivery + 0.30*Quality + 0.20*Commercial + 0.10*Soft
  where PPM_score = MAX(0, 100 - PPM/target_PPM*100)
        NCR_score = MAX(0, 100 - NCR_rate*10)
  ```
- **Data Source**: fact_scorecard_monthly
- **Calculation Level**: supplier / month
- **Frequency**: monthly
- **Owner**: SQE
- **Interpretation**: ≥90 PREFERRED … <45 DISQUALIFIED.
- **Thresholds**: Green ≥75, Yellow 60–75, Red <60
- **Recommended Action**: <60 → escalation + development plan.
- **Validation vs Source**: recompute one supplier by hand vs source tables.

### KPI: HHI (Concentration)
- **Objective**: supplier concentration risk per category.
- **Formula (SQL)**:
  `HHI = SUM( POWER(spend_share*100, 2) )` grouped by category, where
  `spend_share = supplier_spend / category_total_spend`.
- **Data Source**: fact_spend
- **Calculation Level**: category / quarter
- **Frequency**: monthly (trailing 12m spend)
- **Owner**: Category Manager
- **Interpretation**: higher = more concentrated.
- **Thresholds**: Green <1,500, Yellow 1,500–5,000, Red ≥5,000
- **Recommended Action**: Red → dual-source qualification programme.
- **Validation vs Source**: category total spend vs AP ledger.

### KPI: Data Completeness
- **Objective**: trust indicator for each scorecard.
- **Formula**: `completeness % = non_null_inputs / expected_inputs * 100`
- **Thresholds**: Green ≥95 %, Yellow 80–95 %, Red <80 %
- **Recommended Action**: Red → mark scorecard provisional; fix data gap.
- **Validation vs Source**: input availability check per supplier.

---

## 11. Analytical Logic

- **Segmentations**: by Kraljic segment (Strategic/Leverage/Bottleneck/Non-critical),
  by region, by material group, by category.
- **Classifications**: rating band (5 levels); LT variability class X/Y/Z from
  `CV_LT = stddev(LT)/mean(LT)` (X<0.10, Y 0.10–0.25, Z>0.25).
- **Priority logic**: watch-list priority = `spend_weight * (100 - composite_score)`;
  highest spend × worst score first.
- **Alert logic**:
  - Composite drop >10 points month-on-month → email SQE.
  - Any category HHI crossing 5,000 → alert Category Manager.
  - NCR aging beyond CAPA due date → daily escalation.
  - PPM Red two consecutive months → mandatory supplier audit trigger.

---

## 12. Validations and Controls

### Validation: GR-to-PO referential integrity
- **Field/Table**: fact_delivery.po_key
- **Validation Rule**: every GR line must match a PO schedule line.
- **Validation Method**: anti-join GR vs EKET; count orphans.
- **Expected Result**: orphan rate <1 %.
- **Action if Fails**: route orphans to exception table; notify ETL owner.
- **Verifiable Evidence**: daily orphan count in `etl_audit_log`.

### Validation: Scorecard score bounds
- **Field/Table**: fact_scorecard_monthly.composite_score
- **Validation Rule**: 0 ≤ composite_score ≤ 100.
- **Validation Method**: range check post-compute.
- **Expected Result**: zero out-of-bounds rows.
- **Action if Fails**: halt publish; investigate scoring pipeline.
- **Verifiable Evidence**: validation query result = 0 rows.

### Validation: Spend reconciliation
- **Field/Table**: fact_spend.spend_group_ccy
- **Validation Rule**: total spend = AP ledger control total ±0.5 %.
- **Validation Method**: compare sum to FI control total.
- **Expected Result**: within tolerance.
- **Action if Fails**: investigate FX / credit-memo gaps.
- **Verifiable Evidence**: reconciliation report stored per month.

### Validation: Rating band logic
- **Field/Table**: fact_scorecard_monthly.rating
- **Validation Rule**: rating matches composite per threshold table.
- **Validation Method**: recompute band from score, compare.
- **Expected Result**: 100 % match (except manual overrides flagged).
- **Action if Fails**: correct mapping; re-publish.
- **Verifiable Evidence**: mismatch count = 0.

---

## 13. Required Evidence

- ETL audit log (row counts, sums, orphan counts) per daily load.
- Monthly reconciliation pack: OTD/PPM/NCR/spend vs SAP standard reports.
- Manual recompute of one supplier scorecard signed off by SQE lead.
- Power BI dataset refresh history screenshot.
- Watch-list change log with trigger reasons.

---

## 14. Dashboard / Report Design (Power BI)

**Page 1 — Executive Summary**: rating distribution donut, % suppliers ≥APPROVED,
top 10 declining suppliers, category HHI heat map.
**Page 2 — Supplier Scorecard Detail**: supplier selector; sub-score breakdown;
12-month composite trend; OTD/OTIF/PPM/NCR sparklines; data completeness gauge.
**Page 3 — Delivery Tracking**: OTD/OTIF by plant, Incoterm, material group;
late-delivery line-level table with drill-through.
**Page 4 — Quality**: PPM Pareto by supplier/material; NCR aging; CAPA status.
**Page 5 — Concentration Risk**: HHI per category; single-source materials table.
**Slicers**: period, region, category, Kraljic segment, rating band.
**Drill-through**: supplier → line-level GR/NCR detail; category → supplier spend split.

---

## 15. Use Cases

1. **Monthly scorecard review**: SQE filters to declining suppliers, opens detail
   page, identifies PPM as the driver, launches 8D.
2. **Dual-source decision**: Category Manager sees category HHI=6,800, reviews
   single-source material list, initiates qualification of second supplier.
3. **QBR preparation**: relationship manager exports supplier scorecard PDF for
   quarterly business review.
4. **Early warning**: watch-list flags supplier with −9 trend; SQE engages before
   APPROVED breach.
5. **Plant delivery escalation**: plant manager filters OTD by plant, finds carrier
   pattern, escalates to logistics.

---

## 16. Recommended Actions

| Result / Condition | Recommended Action | Owner | Timeline |
|---|---|---|---|
| Composite <60 | Formal development plan + escalation | SQE | 2 weeks |
| PPM Red 2 months | Supplier audit + containment | Quality | 30 days |
| HHI ≥5,000 | Dual-source qualification | Category Mgr | Quarter |
| OTD <90 % | Delivery improvement plan | SQE | 2 weeks |
| Early-warning trigger | Proactive QBR + watch-list | SQE | 1 week |
| Data completeness <80 % | Fix data gap; provisional scorecard | Data team | 1 week |

---

## 17. Test Cases

### TC-01 — OTD flag boundary
- **Scenario**: GR posted exactly on confirmed date, grace=0.
- **Input Data**: confirmed_date=2026-06-10, gr_date=2026-06-10.
- **Expected Result**: on_time_flag=1.
- **Result to Avoid**: flag=0 (off-by-one date error).
- **Required Validation**: boundary unit test on flag logic.
- **Evidence**: test query output.

### TC-02 — GR reversal netting
- **Scenario**: 101 of 100 units then 102 of 100 units.
- **Input Data**: two MSEG rows.
- **Expected Result**: received_qty=0; line excluded from in-full numerator.
- **Result to Avoid**: received_qty=100 (reversal ignored).
- **Required Validation**: net-qty test.
- **Evidence**: computed received_qty.

### TC-03 — PPM with skip-lot
- **Scenario**: inspection lot with inspected_qty=0.
- **Input Data**: one QALS row qty=0.
- **Expected Result**: excluded from PPM denominator (no divide-by-zero).
- **Result to Avoid**: PPM = error / infinity.
- **Required Validation**: NULLIF denominator test.
- **Evidence**: PPM query result.

### TC-04 — Rating band assignment
- **Scenario**: composite=74.9.
- **Input Data**: scorecard row.
- **Expected Result**: rating=CONDITIONAL.
- **Result to Avoid**: rating=APPROVED (≥75 boundary wrong).
- **Required Validation**: band boundary test.
- **Evidence**: rating output.

### TC-05 — HHI single source
- **Scenario**: one supplier = 100 % of category.
- **Input Data**: single spend row.
- **Expected Result**: HHI=10,000; flag=HIGH.
- **Result to Avoid**: HHI≠10,000.
- **Required Validation**: HHI formula test.
- **Evidence**: HHI value.

### TC-06 — Spend reconciliation
- **Scenario**: monthly spend load.
- **Input Data**: fact_spend total vs AP control total.
- **Expected Result**: within ±0.5 %.
- **Result to Avoid**: >0.5 % gap unflagged.
- **Required Validation**: reconciliation query.
- **Evidence**: reconciliation report.

---

## 18. Risks and Mitigations

| Risk | Probability | Impact | Preventive Control | Corrective Control |
|---|---|---|---|---|
| Missing PO confirmation dates | High | High | Fallback to requested date + flag | Chase supplier confirmations |
| Internal NCRs mis-attributed | Medium | High | Cause-code filter | Monthly NCR audit |
| FX gaps in spend | Medium | Medium | Month-end rate table | Reconciliation control |
| Skip-lot distorting PPM | Medium | Medium | Exclude zero-qty lots | Inspection policy review |
| Back-dated GR shifting OTD | Low | Medium | Posting-date cutoff control | Restate affected period |
| Duplicate supplier records | Low | High | MDM dedup on DUNS | Merge + restate |

---

## 19. Implementation Checklist

1. Confirm in-scope supplier definition with Procurement.
2. Build Azure SQL staging for Sources 1–7.
3. Implement incremental extraction (CDC by posting/creation date).
4. Build fact/dim tables per §6.
5. Implement transformation rules §8 (flags, PPM, NCR age, FX).
6. Implement scoring pipeline §10; store fact_scorecard_monthly.
7. Configure plant grace-period table.
8. Build HHI computation by category.
9. Build Power BI model with relationships §6.
10. Author all KPI measures (DAX) §10.
11. Build 5 dashboard pages §14.
12. Configure RLS (region/category).
13. Set daily refresh + monthly snapshot.
14. Implement validations §12 as ETL gates.
15. Build reconciliation pack to SAP reports.
16. UAT with SQE and Category Managers.
17. Document data lineage.
18. Go-live + hypercare 2 weeks.

---

## 20. Validation Checklist

1. Orphan GR rate <1 % verified.
2. OTD/OTIF reconciled to SAP MB51/ME2L sample.
3. PPM reconciled to SAP QGA3 sample.
4. NCR count reconciled to SAP QM12.
5. Spend reconciled to AP control total ±0.5 %.
6. Composite scores within [0,100].
7. Rating bands match threshold logic.
8. HHI verified on single-source test case.
9. Data completeness flag working.
10. RLS verified per persona.
11. Refresh schedule confirmed.
12. Manual scorecard recompute signed off.

---

## 21. Pending Information to Confirm

- Plant-level OTD grace-period values (per-plant table). — *Pending to confirm*
- Target PPM per material group (automotive vs general). — *Pending to confirm*
- Soft-score input source and methodology. — *Pending to confirm*
- Intercompany supplier exclusion list. — *Pending to confirm*
- ML deterioration model availability for early warning (Phase 2). — *Pending to confirm*
- Group currency and FX rate source table. — *Pending to confirm*
- RLS security groups per region/category. — *Pending to confirm*

---

## 22. Implementation Roadmap

| Week | Activity | Deliverable | Owner | Status |
|---|---|---|---|---|
| 1–2 | Requirements + source confirmation | Signed scope | BI Lead | Pending |
| 3–5 | Staging + extraction | Loaded staging | Data Eng | Pending |
| 6–8 | Fact/dim + transformations | Model v1 | Data Eng | Pending |
| 9–10 | Scoring pipeline + HHI | fact_scorecard_monthly | Analytics | Pending |
| 11–13 | Power BI model + KPIs | Dashboard draft | BI Dev | Pending |
| 14–15 | Validations + reconciliation | Recon pack | Data Quality | Pending |
| 16–17 | UAT | Sign-off | SQE / Category | Pending |
| 18 | Go-live + hypercare | Production report | BI Lead | Pending |
