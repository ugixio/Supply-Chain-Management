# Quality Management Analytics — Implementation Guide

**Department**: 08 — Quality Management
**Analytics Domain**: IQC, PPM/DPMO, NCR Analysis, CAPA Effectiveness, SPC, Supplier Quality Scorecard
**Standard Alignment**: ISO 9001:2015 (§8.4, §8.5.2, §8.6, §8.7), ISO 2859-1:1999 (AQL),
IATF 16949:2016, AIAG FMEA 4th Ed., Six Sigma DMAIC, ASQ Body of Knowledge
**Systems**: SAP S/4HANA QM, SAP Quality Notifications, Apache Superset, Python (SPC calculations), PostgreSQL
**Author**: Supply Chain Centre of Excellence
**Version**: 3.0 — 2026-06-22
**Status**: Approved for Implementation

---

## Table of Contents

1. Executive Summary
2. Analysis Objective
3. Scope
4. Business Questions
5. Data Sources
6. Data Model
7. Data Dictionary
8. Transformation Rules
9. Business Rules
10. KPIs and Formulas
11. Analytical Logic
12. Validations and Controls
13. Required Evidence
14. Dashboard Design
15. Use Cases
16. Recommended Actions
17. Test Cases
18. Risks and Mitigations
19. Implementation Checklist
20. Validation Checklist
21. Pending Information
22. Implementation Roadmap

---

## 1. Executive Summary

Quality management is a strategic differentiator and a compliance obligation. Organisations
that achieve and sustain Six Sigma capability across their supplier base and internal operations
command 15–25% lower cost of poor quality (COPQ), maintain fewer regulatory recalls, and
earn preferred supplier status from major retailers demanding OTIF >= 98% and defect rates
<= 200 PPM. In food and beverage, pharmaceutical, and automotive sectors, quality failures
carry direct regulatory consequences including product recalls, FDA warning letters, IATF
16949 de-certification, and loss of customer contracts.

This implementation guide provides the complete analytics architecture, data model, KPI
definitions, transformation rules, and dashboard design for the Quality Management
Analytics capability within the Supply Chain Management platform. The scope covers five
interconnected quality analytics domains:

1. **Incoming Quality Control (IQC)** — AQL sampling plan results by supplier, lot, and
   inspection level, with acceptance/rejection decisions and disposition tracking.
2. **PPM and DPMO Tracking** — defect rate monitoring at the supplier and commodity level,
   with Sigma level calculation and trend analysis versus automotive, food, and general
   manufacturing targets.
3. **Non-Conformance Report (NCR) Analysis** — NCR volume, severity classification,
   root-cause pareto, financial impact, and open versus closed rate tracking.
4. **CAPA Effectiveness Tracking** — corrective and preventive action on-time closure,
   recurrence rate, and effectiveness verification scores.
5. **Statistical Process Control (SPC)** — X-bar/R charts, CUSUM, Cp and Cpk indices
   calculated in Python from SAP QM inspection characteristic results.

### Expected Business Value

| Benefit | Year 1 | Year 2 |
|---------|--------|--------|
| COPQ reduction | -20% | -35% |
| Incoming PPM improvement | -30% | -50% |
| CAPA on-time closure rate | +25 pp | +40 pp |
| Supplier quality scorecard coverage | 80% of spend | 95% of spend |
| IQC inspection cycle time | -40% (sampling optimisation) | -60% |
| Regulatory audit findings (quality) | -50% | -75% |

---

## 2. Analysis Objective

The primary objective of the Quality Management Analytics implementation is to convert raw
inspection results, quality notifications, and process parameter data from SAP QM into a
structured, governed analytical layer that enables:

1. **Real-time quality status visibility** — incoming lots pending inspection, accepted,
   rejected, and under disposition are tracked in a live operational view accessible to
   QC supervisors and warehouse teams.

2. **Supplier quality benchmarking** — incoming PPM, AQL rejection rate, and NCR rate are
   calculated per supplier and commodity, enabling objective performance comparisons and
   driving the supplier quality scorecard component of the overall supplier scorecard
   (30% weight per the CLAUDE.md specification).

3. **Process capability monitoring** — Cp, Cpk, Pp, and Ppk indices are calculated per
   part number and control plan characteristic from inspection results, identifying
   characteristics approaching the control limit before non-conformances occur.

4. **NCR and CAPA lifecycle management** — open, overdue, and recently closed NCRs and
   CAPAs are tracked with aging, financial impact, and effectiveness verification, providing
   the Quality Manager with a complete action item dashboard.

5. **Cost of Poor Quality quantification** — internal failure costs (rework, scrap, re-
   inspection), external failure costs (returns, warranty, customer chargebacks), appraisal
   costs (inspection labour, equipment), and prevention costs are aggregated and reported
   by supplier, product category, and business unit.

6. **Predictive quality alerting** — statistical signals (Western Electric rules violations,
   Cpk < 1.33 threshold breaches) are surfaced automatically to QC engineers before
   production batches fail final inspection, reducing scrap and rework costs.

---

## 3. Scope

### In Scope

- Incoming inspection results for all externally sourced materials and components,
  governed by ISO 2859-1 AQL sampling plans configured in SAP QM
- In-process inspection results for internal manufacturing or value-adding operations
  with control plan characteristics managed in SAP QM
- All Quality Notifications (QM notification types: F1 — customer complaint, F2 — internal
  defect, F3 — supplier defect) created in SAP S/4HANA QM
- NCR lifecycle from creation through disposition, CAPA assignment, CAPA implementation,
  effectiveness verification, and closure
- CAPA records linked to NCRs, FMEA risk items, or regulatory findings
- Supplier PPM and DPMO calculation for all suppliers with >= 10 inspection lots per
  rolling 12-month period
- SPC calculations for critical-to-quality (CTQ) characteristics flagged in the
  SAP QM control plan as requiring SPC monitoring
- COPQ cost collection from SAP MM (scrap postings), SAP SD (return credit notes),
  SAP FI (quality-related cost centre postings)

### Out of Scope

- Customer satisfaction surveys and Net Promoter Score (handled by Sales Analytics)
- Regulatory drug product quality (pharmaceutical GMP — separate validated system)
- Environmental quality (ISO 14001 environmental non-conformances — handled by EHS)
- Calibration management records (handled by Maintenance module)
- Design quality (DFMEA, design verification testing — handled by R&D)

---

## 4. Business Questions

**BQ-01** — Which suppliers are delivering materials above our incoming PPM threshold
(500 PPM automotive, 1,000 PPM food, 2,000 PPM general), and what is the trend over the
past 12 months? Are specific commodity categories driving most of the incoming defects?

**BQ-02** — What is the overall AQL acceptance rate by supplier and inspection level?
Which suppliers are consistently failing AQL sampling at Level II (normal inspection),
and have they been escalated to Level III (tightened inspection) as required by ISO 2859-1?

**BQ-03** — What is the average NCR severity distribution (Critical / Major / Minor) by
supplier and product category? What are the top five root cause categories driving NCRs
in the current fiscal year (Pareto analysis)?

**BQ-04** — What percentage of CAPAs are being closed by the agreed due date? Which
suppliers and internal owners have the highest CAPA overdue rates? Are verified effective
CAPAs actually preventing recurrence (recurrence rate within 12 months of CAPA closure)?

**BQ-05** — What is the total Cost of Poor Quality (COPQ) for the current fiscal year,
broken down by internal failure, external failure, appraisal, and prevention? Which
supplier and product category contributes most to COPQ? How does COPQ trend versus
revenue (COPQ as % of revenue)?

**BQ-06** — Which critical-to-quality (CTQ) characteristics are showing Cpk < 1.33
(minimum acceptable) or Cpk < 1.0 (unstable process)? Which part numbers and suppliers
are responsible, and what is the trend — improving, stable, or deteriorating?

**BQ-07** — Are SPC control charts showing out-of-control signals (Western Electric rules
violations) on active production lines or incoming inspection lots? How many signals have
been generated in the past 30 days, and how many triggered corrective action?

**BQ-08** — What is the First Pass Yield (FPY) by supplier, material group, and inspection
stage? How many lots are being conditionally accepted (re-inspected or sorted) versus
unconditionally accepted on first inspection?

**BQ-09** — What is the total financial exposure from open NCRs — value of stock on
quality hold, potential scrap value, and cost of sorting / rework if disposition is
approved? How long has stock been on hold by NCR?

**BQ-10** — Which quality inspectors or inspection teams have the highest detection rate
of defects per lot inspected? Is there variability in rejection rates between inspectors
that might suggest measurement system inconsistency (gage R&R requirement)?

**BQ-11** — Are supplier quality improvements sustained after CAPA closure, or do
suppliers revert to prior defect rates within 6–12 months? What is the recurrence rate
by supplier tier (PREFERRED / APPROVED / CONDITIONAL)?

**BQ-12** — What is the sigma level of our supplier base as a whole, and how has it
trended over the past three years? Are we on track to achieve the Six Sigma aspirational
targets defined in our quality strategy?

---

## 5. Data Sources

### DS-01: SAP QM — Inspection Lots and Results

| Attribute | Detail |
|-----------|--------|
| Source Name | SAP QM Inspection Lots and Inspection Results |
| System | SAP S/4HANA 2023, QM module |
| Table / Report | QMEL (Inspection Lot), QMFE (Defect Item), QMUR (Inspection Characteristic Result), QMZR (Inspection Sample) |
| Owner | Quality Control Manager / SAP QM System Administrator |
| Frequency | Real-time via RFC; Superset refresh every 2 hours |
| Required Fields | QMEL: PRUEFLOS (lot number), LIEFNR (vendor), MATNR (material), CHARG (batch), MENGE (quantity), EINHEIT (UOM), STAT (status), CREATED_ON. QMUR: PRUEFLOS, MERKMAL (characteristic), SOLLWERT (target), ISTWERT (actual), FEHLERZAHL (defect count). QMFE: PRUEFLOS, FEHLART (defect type), FEHLZAHL (defect count), SCHWERE (severity) |
| Critical Fields | PRUEFLOS (PK), LIEFNR, MATNR, STAT (status determines if inspection is complete), FEHLZAHL |
| Primary Key | PRUEFLOS (inspection lot number) |
| Validations | STAT must be in valid SAP QM status codes; MENGE > 0; FEHLZAHL >= 0; ISTWERT must be numeric for variable characteristics |
| Known Errors | Historical lots pre-2022 may have incomplete QMUR records (paper-based inspection). Flag CREATED_ON < 2022-01-01 as LEGACY and exclude from SPC calculations |
| Evidence Required | SAP QM inspection plan configuration, control plan extract, AQL table configuration in SAP |

### DS-02: SAP QM — Quality Notifications (NCR)

| Attribute | Detail |
|-----------|--------|
| Source Name | SAP QM Quality Notifications — NCR, Customer Complaints, Internal Defects |
| System | SAP S/4HANA 2023, QM module |
| Table / Report | QMEL (Notification Header), QMFE (Defect Items), QMMA (Tasks / CAPA), QMSM (Activities) |
| Owner | Quality Manager |
| Frequency | Real-time event trigger on notification creation and status change |
| Required Fields | QMEL: QMNUM (notification number), QMART (notification type: F1/F2/F3), QMTXT (short text), LIEFNR, MATNR, CHARG, MENGE, ERDAT (creation date), ADDAT (completion date), STAT. QMMA: QMNUM, MNGRP (task group), MNCOD (task code), FAEDN (due date), ERDAT, ADDAT, VERAN (responsible person) |
| Critical Fields | QMNUM (PK), QMART (type), STAT (status), FAEDN (CAPA due date), ADDAT (actual closure date) |
| Primary Key | QMNUM |
| Validations | FAEDN >= ERDAT; ADDAT >= ERDAT; QMART in (F1, F2, F3); severity code must be in (CRITICAL, MAJOR, MINOR) |
| Known Errors | Some older F3 notifications lack LIEFNR (vendor) — cross-reference to PO via CHARG/MATNR lookup |
| Evidence Required | Quality notification type configuration, severity code master, task code master |

### DS-03: SAP MM / WM — Goods Receipt and Stock Quality Hold

| Attribute | Detail |
|-----------|--------|
| Source Name | SAP MM Goods Receipt and Quality Hold Stock |
| System | SAP S/4HANA MM / WM |
| Table / Report | MSEG (Material Document Segment), MKPF (Material Document Header), MCHB (Batch Stock), LGPLA (Warehouse Management Stock) |
| Owner | Warehouse / Inventory Management Team |
| Frequency | Real-time posting; batch extract for quality hold stock report |
| Required Fields | MSEG: MBLNR (document), MATNR, CHARG, MENGE, WEMPF (receiving plant), MVTYP (movement type), KOSTL. MCHB: MATNR, CHARG, CLABS (unrestricted), CEINM (quality inspection stock), CSPEM (blocked stock) |
| Critical Fields | CEINM (quantity in quality inspection stock), CHARG (batch links to inspection lot) |
| Primary Key | MBLNR + MBLPO (document + line item) |
| Validations | CEINM >= 0; MATNR must resolve to active material master; CHARG must link to QMEL inspection lot |
| Known Errors | Partial GR postings may create multiple MSEG records per PO line — aggregate by MATNR+CHARG |
| Evidence Required | Movement type configuration, quality inspection stock configuration |

### DS-04: SAP FI / CO — COPQ Cost Postings

| Attribute | Detail |
|-----------|--------|
| Source Name | SAP FI/CO — Quality-Related Cost Centre and GL Postings |
| System | SAP S/4HANA FI/CO |
| Table / Report | BSEG (FI Document Segment), COEP (CO Line Items), AUFK (Internal Order Master for quality orders) |
| Owner | Finance Controller / QM Cost Accountant |
| Frequency | Daily close; monthly COPQ report |
| Required Fields | BSEG: BELNR (document), BUKRS (company code), HKONT (GL account), WRBTR (amount), KOSTL (cost centre), AUFNR (order). COEP: AUFNR, KSTAR (cost element), WOG001 (actual cost) |
| Critical Fields | HKONT (GL account — must map to COPQ category: scrap, rework, warranty, appraisal), WRBTR, KOSTL |
| Primary Key | BELNR + BUZEI |
| Validations | GL accounts must resolve to COPQ category mapping table; WRBTR != 0; KOSTL resolves to active cost centre |
| Known Errors | Some rework costs posted to general production cost centre rather than quality cost centre — requires mapping table maintained by Finance |
| Evidence Required | COPQ GL account mapping table, cost centre hierarchy, Finance sign-off on COPQ classification |

### DS-05: Python SPC Engine — Calculated Control Chart Metrics

| Attribute | Detail |
|-----------|--------|
| Source Name | Python SPC Engine output — control limits, Cp, Cpk, Pp, Ppk, OOC signals |
| System | Python 3.11 scheduled job writing to PostgreSQL |
| Table / Report | analytics.SPC_CONTROL_LIMITS, analytics.SPC_OOC_SIGNALS, analytics.PROCESS_CAPABILITY |
| Owner | Quality Analytics Engineer |
| Frequency | Triggered on each new inspection lot completion; also nightly batch for bulk recalculation |
| Required Fields | MATNR, CHARG, PRUEFLOS, MERKMAL, UCL, LCL, XBAR, RBAR, CP, CPK, PP, PPK, SIGMA_EST, OOC_FLAG, OOC_RULE, CALC_TIMESTAMP |
| Critical Fields | CP, CPK (process capability indices), OOC_FLAG (out-of-control signal), UCL, LCL |
| Primary Key | PRUEFLOS + MERKMAL + CALC_TIMESTAMP |
| Validations | UCL > XBAR > LCL; CP > 0; CPK <= CP; OOC_RULE in valid rule codes (WE1–WE8 for Western Electric) |
| Known Errors | Insufficient sample size (n < 25 subgroups) produces unreliable control limits — flag as PRELIMINARY |
| Evidence Required | SPC engine code review, Python unit test results, validation against manual Minitab calculation for 5 test cases |

### DS-06: Supplier Quality Master

| Attribute | Detail |
|-----------|--------|
| Source Name | Supplier Quality Master — Inspection Level and AQL Configuration |
| System | PostgreSQL ref.SUPPLIER_QUALITY_CONFIG (maintained by Quality team) |
| Table / Report | ref.SUPPLIER_QUALITY_CONFIG, ref.AQL_SAMPLING_PLAN |
| Owner | Supplier Quality Engineer |
| Frequency | Updated on supplier performance review; minimum quarterly |
| Required Fields | LIEFNR, INSPECTION_LEVEL (I/II/III per ISO 2859-1), AQL_ACCEPTABLE (acceptable quality level %), SAMPLING_TYPE (NORMAL/TIGHTENED/REDUCED), SECTOR (AUTOMOTIVE/FOOD/GENERAL), PPM_TARGET, LAST_REVIEW_DATE |
| Critical Fields | INSPECTION_LEVEL (drives sample size calculation), AQL_ACCEPTABLE, SAMPLING_TYPE |
| Primary Key | LIEFNR + MATNR_GROUP |
| Validations | INSPECTION_LEVEL in (I, II, III); AQL_ACCEPTABLE in standard AQL values (0.065, 0.1, 0.15, 0.25, 0.4, 0.65, 1.0, 1.5, 2.5, 4.0, 6.5); SAMPLING_TYPE in (NORMAL, TIGHTENED, REDUCED) |
| Known Errors | Suppliers not yet configured default to Level II, AQL 1.0 — log these as UNCLASSIFIED |
| Evidence Required | AQL sampling plan master (ISO 2859-1 Table I and II-A), supplier quality agreement extract |

---

## 6. Data Model

The Quality Management analytics data model follows a star schema with three central fact
tables (inspections, quality notifications, and COPQ costs) connected by shared dimension
tables.

```
DIM_DATE -----+--------+--------+
              |        |        |
DIM_SUPPLIER  |        |        |
              v        v        v
DIM_MATERIAL FACT_IQC FACT_NCR  FACT_COPQ
              |        |        |
DIM_DEFECT_TYPE        |
              |        |
              v        v
         FACT_SPC_CAPABILITY (related via MATNR + MERKMAL)
              |
         FACT_CAPA (related via QMNUM from FACT_NCR)
```

### Central Fact Tables

**FACT_IQC** — one row per inspection lot. Contains sample size, defect count, AQL decision
(accept/reject), inspection level, disposition, and calculated PPM.

**FACT_NCR** — one row per quality notification. Contains notification type, severity,
material, supplier, financial impact, status, and age.

**FACT_COPQ** — one row per cost posting in a quality-related GL account. Contains COPQ
category (internal failure, external failure, appraisal, prevention), amount, cost centre,
and period.

**FACT_SPC_CAPABILITY** — one row per part number and control plan characteristic per
calculation period. Contains UCL, LCL, Xbar, Rbar, Cp, Cpk, Pp, Ppk, and out-of-control
signals from the Python SPC engine.

**FACT_CAPA** — one row per CAPA task linked to a quality notification. Contains due date,
responsible owner, actual closure date, effectiveness score, and recurrence flag.

### Dimension Tables

**DIM_DATE** — standard date dimension with fiscal year, quarter, month, week.

**DIM_SUPPLIER** — supplier master with tier, commodity category, sector, country,
ISO certifications, and current quality scorecard score.

**DIM_MATERIAL** — material master with material group, description, unit of measure,
lot size, storage condition, and sector classification.

**DIM_DEFECT_TYPE** — defect type master with defect code, description, severity,
detection method, and Ishikawa root-cause category (Man, Machine, Material, Method,
Measurement, Environment).

**DIM_INSPECTOR** — quality inspector master with team, shift, plant, and certification level.

---

## 7. Data Dictionary

### FACT_IQC

| Field | Description | Type | Nullable | Validation |
|-------|-------------|------|----------|------------|
| PRUEFLOS | Inspection lot number (PK, from SAP QM QMEL) | VARCHAR(12) | No | Unique; matches SAP QMEL.PRUEFLOS |
| LIEFNR | Supplier number (FK to DIM_SUPPLIER) | VARCHAR(10) | No | Must resolve to active supplier |
| MATNR | Material number (FK to DIM_MATERIAL) | VARCHAR(18) | No | Must resolve to active material master |
| CHARG | Batch/lot number | VARCHAR(10) | Yes | Required for batch-managed materials |
| PO_NUMBER | Purchase order reference | VARCHAR(10) | Yes | Resolves to active PO if populated |
| MENGE | Total quantity received in inspection lot | DECIMAL(13,3) | No | > 0 |
| EINHEIT | Unit of measure (GS1 UOM code) | VARCHAR(3) | No | Valid GS1 UOM code |
| SAMPLE_SIZE_N | Number of units sampled per AQL plan | INT | No | > 0; must match AQL table for lot size |
| DEFECT_COUNT_D | Number of defective units found in sample | INT | No | >= 0; <= SAMPLE_SIZE_N |
| DEFECT_UNITS_TOTAL | Estimated total defective units in lot | INT | Yes | Calculated: DEFECT_COUNT_D / SAMPLE_SIZE_N * MENGE |
| AQL_DECISION | Lot disposition decision | VARCHAR(10) | No | In (ACCEPT, REJECT, CONDITIONAL) |
| INSPECTION_LEVEL | ISO 2859-1 inspection level | CHAR(3) | No | In (I, II, III) |
| AQL_VALUE | AQL percentage applied | DECIMAL(5,3) | No | Standard AQL values per ISO 2859-1 |
| ACCEPT_NUMBER_AC | Acceptance number (Ac) from sampling plan | INT | No | >= 0 |
| REJECT_NUMBER_RE | Rejection number (Re) from sampling plan | INT | No | > ACCEPT_NUMBER_AC |
| INCOMING_PPM | Calculated PPM for this lot | DECIMAL(10,2) | Yes | >= 0; DEFECT_COUNT_D / SAMPLE_SIZE_N * 1,000,000 |
| INSPECTION_START | Inspection start date | DATE | No | <= INSPECTION_END |
| INSPECTION_END | Inspection completion date | DATE | Yes | NULL = inspection in progress |
| DISPOSITION_CODE | Final disposition of rejected lot | VARCHAR(20) | Yes | In (SCRAP, REWORK, RETURN_TO_SUPPLIER, CONDITIONAL_USE, PENDING) |
| INSPECTOR_ID | FK to DIM_INSPECTOR | VARCHAR(10) | Yes | Must resolve if populated |
| DATE_KEY | FK to DIM_DATE (inspection end date) | INT | Yes | YYYYMMDD integer |

### FACT_NCR

| Field | Description | Type | Nullable | Validation |
|-------|-------------|------|----------|------------|
| QMNUM | Quality notification number (PK) | VARCHAR(12) | No | Unique; from SAP QMEL.QMNUM |
| QMART | Notification type | CHAR(2) | No | In (F1, F2, F3) |
| LIEFNR | Supplier number (FK to DIM_SUPPLIER) | VARCHAR(10) | Yes | Required for F3; optional for F1/F2 |
| MATNR | Material number (FK to DIM_MATERIAL) | VARCHAR(18) | Yes | Recommended for all types |
| CHARG | Batch involved in NCR | VARCHAR(10) | Yes | |
| NCR_SEVERITY | Severity classification | VARCHAR(10) | No | In (CRITICAL, MAJOR, MINOR) |
| DEFECT_QTY | Quantity of defective units in NCR | DECIMAL(13,3) | Yes | >= 0 |
| FINANCIAL_IMPACT_GC | Estimated financial impact in group currency (EUR) | DECIMAL(14,2) | Yes | >= 0 |
| CREATION_DATE | NCR creation date | DATE | No | <= today |
| TARGET_CLOSURE_DATE | Required closure date | DATE | Yes | >= CREATION_DATE |
| ACTUAL_CLOSURE_DATE | Actual closure date | DATE | Yes | NULL = open |
| NCR_STATUS | Current status | VARCHAR(20) | No | In (OPEN, IN_PROGRESS, PENDING_VERIFICATION, CLOSED) |
| ROOT_CAUSE_CODE | Primary root cause category | VARCHAR(20) | Yes | In (MAN, MACHINE, MATERIAL, METHOD, MEASUREMENT, ENVIRONMENT) |
| ROOT_CAUSE_TEXT | Detailed root cause description | NVARCHAR(500) | Yes | Free text |
| RECURRENCE_FLAG | Is this NCR a recurrence of a prior NCR? | BIT | No | Default 0; set by matching logic |
| PRIOR_QMNUM | Reference to prior NCR if recurrence | VARCHAR(12) | Yes | Required when RECURRENCE_FLAG = 1 |
| AGE_DAYS | Calendar days since creation (if open) | INT | Yes | Calculated: DATEDIFF(today, CREATION_DATE) |
| DATE_KEY | FK to DIM_DATE (creation date) | INT | No | YYYYMMDD integer |

### FACT_CAPA

| Field | Description | Type | Nullable | Validation |
|-------|-------------|------|----------|------------|
| CAPA_ID | Surrogate CAPA identifier (PK) | BIGINT | No | Auto-increment |
| QMNUM | Parent NCR notification number | VARCHAR(12) | No | FK to FACT_NCR |
| CAPA_TYPE | Corrective or Preventive | CHAR(1) | No | In (C, P) |
| CAPA_DESCRIPTION | Description of the action | NVARCHAR(500) | No | Free text; minimum 20 characters |
| RESPONSIBLE_PERSON | Person / team responsible for closure | VARCHAR(50) | No | Must be a valid HR employee or supplier contact |
| DUE_DATE | Agreed CAPA due date | DATE | No | >= FACT_NCR.CREATION_DATE |
| ACTUAL_CLOSURE_DATE | Actual date CAPA was implemented and verified | DATE | Yes | NULL = open |
| IS_ON_TIME | Closed on or before DUE_DATE | BIT | Yes | Calculated |
| EFFECTIVENESS_SCORE | Verified effectiveness score (0–100) | DECIMAL(5,2) | Yes | Between 0 and 100; populated after verification |
| EFFECTIVENESS_VERIFIED | Effectiveness verification completed | BIT | No | Default 0 |
| RECURRENCE_WITHIN_12M | Same defect recurred within 12 months of CAPA closure | BIT | Yes | Calculated after 12 months |
| AGE_DAYS | Days open (if not closed) | INT | Yes | Calculated |

### FACT_COPQ

| Field | Description | Type | Nullable | Validation |
|-------|-------------|------|----------|------------|
| COPQ_RECORD_ID | Surrogate PK | BIGINT | No | Auto-increment |
| BELNR | SAP FI document number | VARCHAR(10) | No | Resolves to FI document |
| BUKRS | Company code | CHAR(4) | No | Valid SAP company code |
| PERIOD_YYYYMM | Fiscal period YYYYMM | CHAR(6) | No | Valid fiscal period |
| COPQ_CATEGORY | Top-level COPQ category | VARCHAR(20) | No | In (INTERNAL_FAILURE, EXTERNAL_FAILURE, APPRAISAL, PREVENTION) |
| COPQ_SUBCATEGORY | Subcategory of cost | VARCHAR(30) | Yes | e.g., SCRAP, REWORK, WARRANTY, INSPECTION_LABOUR |
| LIEFNR | Supplier if external failure | VARCHAR(10) | Yes | |
| MATNR | Material | VARCHAR(18) | Yes | |
| AMOUNT_GC | Cost amount in group currency (EUR) | DECIMAL(14,2) | No | != 0 |
| KOSTL | Cost centre | VARCHAR(10) | No | Active cost centre |
| QMNUM | Linked NCR if applicable | VARCHAR(12) | Yes | FK to FACT_NCR |

### FACT_SPC_CAPABILITY

| Field | Description | Type | Nullable | Validation |
|-------|-------------|------|----------|------------|
| SPC_RECORD_ID | Surrogate PK | BIGINT | No | Auto-increment |
| MATNR | Material number | VARCHAR(18) | No | FK to DIM_MATERIAL |
| MERKMAL | Inspection characteristic code | VARCHAR(10) | No | Matches SAP QM inspection plan characteristic |
| CALC_PERIOD | Calculation period YYYYMM | CHAR(6) | No | Valid period |
| N_SUBGROUPS | Number of subgroups in calculation | INT | No | >= 25 for stable control limits |
| SUBGROUP_SIZE | Subgroup size (n) | INT | No | >= 2 |
| XBAR | Grand mean (process centre) | DECIMAL(14,6) | No | Numeric |
| RBAR | Average range | DECIMAL(14,6) | No | > 0 |
| UCL | Upper control limit | DECIMAL(14,6) | No | > XBAR |
| LCL | Lower control limit | DECIMAL(14,6) | No | < XBAR |
| USL | Upper specification limit | DECIMAL(14,6) | Yes | From engineering drawing / control plan |
| LSL | Lower specification limit | DECIMAL(14,6) | Yes | From engineering drawing / control plan |
| CP | Process capability (Cp) | DECIMAL(8,4) | Yes | Calculated; >= 0 |
| CPK | Process capability index (Cpk) | DECIMAL(8,4) | Yes | Calculated; <= Cp |
| PP | Preliminary process performance (Pp) | DECIMAL(8,4) | Yes | Uses total standard deviation |
| PPK | Preliminary performance index (Ppk) | DECIMAL(8,4) | Yes | Uses total standard deviation |
| SIGMA_EST | Estimated process standard deviation | DECIMAL(14,6) | Yes | > 0 |
| OOC_FLAG | Out-of-control signal present | BIT | No | Default 0 |
| OOC_RULE | Western Electric rule violated (if OOC) | VARCHAR(10) | Yes | In (WE1, WE2, WE3, WE4, WE5, WE6, WE7, WE8) |
| STATUS | Calculation status | VARCHAR(20) | No | In (STABLE, PRELIMINARY, INSUFFICIENT_DATA, OOC) |

---

## 8. Transformation Rules

### TR-01: Incoming PPM Calculation per Inspection Lot

```sql
-- Applied in the PostgreSQL analytical layer
UPDATE FACT_IQC
SET INCOMING_PPM = CASE
    WHEN SAMPLE_SIZE_N > 0
    THEN CAST(DEFECT_COUNT_D AS FLOAT) / CAST(SAMPLE_SIZE_N AS FLOAT) * 1000000.0
    ELSE NULL
END;
```

### TR-02: AQL Decision Flag (Accept / Reject / Conditional)

The AQL decision is determined by comparing DEFECT_COUNT_D against the acceptance number
(Ac) and rejection number (Re) from the ISO 2859-1 sampling plan table, stored in
ref.AQL_SAMPLING_PLAN.

```sql
UPDATE fi
SET fi.AQL_DECISION = CASE
    WHEN fi.DEFECT_COUNT_D <= asp.AC THEN 'ACCEPT'
    WHEN fi.DEFECT_COUNT_D >= asp.RE THEN 'REJECT'
    ELSE 'CONDITIONAL'
END
FROM FACT_IQC fi
JOIN ref.AQL_SAMPLING_PLAN asp
    ON fi.SAMPLE_LETTER = asp.SAMPLE_LETTER
    AND fi.AQL_VALUE = asp.AQL_VALUE;
```

### TR-03: NCR Age Calculation

```sql
UPDATE FACT_NCR
SET AGE_DAYS = CASE
    WHEN NCR_STATUS = 'CLOSED' THEN DATEDIFF(DAY, CREATION_DATE, ACTUAL_CLOSURE_DATE)
    ELSE DATEDIFF(DAY, CREATION_DATE, CAST(GETDATE() AS DATE))
END;
```

### TR-04: CAPA On-Time Flag

```sql
UPDATE FACT_CAPA
SET IS_ON_TIME = CASE
    WHEN ACTUAL_CLOSURE_DATE IS NULL THEN NULL  -- still open
    WHEN ACTUAL_CLOSURE_DATE <= DUE_DATE THEN 1
    ELSE 0
END;
```

### TR-05: Supplier Rolling PPM Calculation (12-Month Rolling)

```python
# python/08_quality/rolling_ppm.py
import pandas as pd

def calculate_rolling_ppm(df: pd.DataFrame, window_months: int = 12) -> pd.DataFrame:
    """
    Calculate rolling PPM per supplier and material group over a sliding window.

    Args:
        df: DataFrame with columns LIEFNR, MATNR_GROUP, PERIOD_YYYYMM,
            DEFECT_COUNT_D, SAMPLE_SIZE_N
        window_months: Rolling window in months (default 12)

    Returns:
        DataFrame with ROLLING_PPM, ROLLING_DEFECTS, ROLLING_INSPECTED added
    """
    df = df.copy()
    df['PERIOD_DATE'] = pd.to_datetime(df['PERIOD_YYYYMM'], format='%Y%m')
    result_rows = []
    for (supplier, mat_grp), grp in df.groupby(['LIEFNR', 'MATNR_GROUP']):
        grp = grp.sort_values('PERIOD_DATE')
        for idx, row in grp.iterrows():
            window_start = row['PERIOD_DATE'] - pd.DateOffset(months=window_months - 1)
            window_data = grp[grp['PERIOD_DATE'] >= window_start]
            total_defects = window_data['DEFECT_COUNT_D'].sum()
            total_inspected = window_data['SAMPLE_SIZE_N'].sum()
            rolling_ppm = (total_defects / total_inspected * 1_000_000) if total_inspected > 0 else None
            result_rows.append({
                'LIEFNR': supplier,
                'MATNR_GROUP': mat_grp,
                'PERIOD_YYYYMM': row['PERIOD_YYYYMM'],
                'ROLLING_PPM': rolling_ppm,
                'ROLLING_DEFECTS': int(total_defects),
                'ROLLING_INSPECTED': int(total_inspected)
            })
    return pd.DataFrame(result_rows)
```

### TR-06: Process Capability (Cp, Cpk) Calculation in Python

```python
# python/08_quality/spc_engine.py
import numpy as np
from scipy import stats

def calculate_process_capability(
    values: list[float],
    usl: float,
    lsl: float,
    subgroup_size: int = 5
) -> dict:
    """
    Calculate Cp, Cpk, Pp, Ppk for a set of measurement values.

    Args:
        values: List of individual measurement values
        usl: Upper specification limit
        lsl: Lower specification limit
        subgroup_size: Size of each rational subgroup for R-bar method

    Returns:
        Dictionary with Cp, Cpk, Pp, Ppk, Sigma_est, Mean
    """
    arr = np.array(values)
    n = len(arr)
    mean = np.mean(arr)

    # Control chart sigma estimate (from average range — Xbar/R method)
    d2_constants = {2: 1.128, 3: 1.693, 4: 2.059, 5: 2.326, 6: 2.534,
                    7: 2.704, 8: 2.847, 9: 2.970, 10: 3.078}
    d2 = d2_constants.get(subgroup_size, 2.326)
    subgroups = [arr[i:i+subgroup_size] for i in range(0, n - subgroup_size + 1, subgroup_size)]
    ranges = [np.ptp(sg) for sg in subgroups if len(sg) == subgroup_size]
    r_bar = np.mean(ranges) if ranges else np.std(arr, ddof=1)
    sigma_est = r_bar / d2

    # Process capability (uses sigma_est — within-subgroup variation)
    cp = (usl - lsl) / (6 * sigma_est) if sigma_est > 0 else None
    cpu = (usl - mean) / (3 * sigma_est) if sigma_est > 0 else None
    cpl = (mean - lsl) / (3 * sigma_est) if sigma_est > 0 else None
    cpk = min(cpu, cpl) if (cpu is not None and cpl is not None) else None

    # Process performance (uses total standard deviation — overall variation)
    sigma_total = np.std(arr, ddof=1)
    pp = (usl - lsl) / (6 * sigma_total) if sigma_total > 0 else None
    ppu = (usl - mean) / (3 * sigma_total) if sigma_total > 0 else None
    ppl = (mean - lsl) / (3 * sigma_total) if sigma_total > 0 else None
    ppk = min(ppu, ppl) if (ppu is not None and ppl is not None) else None

    return {
        'mean': float(mean),
        'sigma_est': float(sigma_est),
        'sigma_total': float(sigma_total),
        'cp': float(cp) if cp is not None else None,
        'cpk': float(cpk) if cpk is not None else None,
        'pp': float(pp) if pp is not None else None,
        'ppk': float(ppk) if ppk is not None else None,
        'n_values': n,
        'n_subgroups': len(subgroups)
    }
```

### TR-07: Western Electric Rules (Out-of-Control Detection)

```python
# python/08_quality/western_electric_rules.py
import numpy as np
from typing import list

def detect_ooc_signals(values: list[float], ucl: float, lcl: float,
                        xbar: float, sigma: float) -> list[dict]:
    """
    Detect Western Electric out-of-control signals in a control chart data series.

    Args:
        values: Ordered list of subgroup means
        ucl: Upper control limit (xbar + 3*sigma)
        lcl: Lower control limit (xbar - 3*sigma)
        xbar: Grand mean (centre line)
        sigma: Process sigma (sigma_est / sqrt(n))

    Returns:
        List of OOC signal records with index, rule code, and description
    """
    signals = []
    arr = np.array(values)
    n = len(arr)
    zone_a_upper = xbar + 2 * sigma
    zone_a_lower = xbar - 2 * sigma
    zone_b_upper = xbar + sigma
    zone_b_lower = xbar - sigma

    for i in range(n):
        v = arr[i]
        # WE1: Any point beyond 3-sigma control limits
        if v > ucl or v < lcl:
            signals.append({'index': i, 'rule': 'WE1', 'desc': 'Point beyond 3-sigma limit'})

        # WE2: 2 of 3 consecutive points in Zone A or beyond (same side)
        if i >= 2:
            seg = arr[i-2:i+1]
            above_A = np.sum(seg > zone_a_upper)
            below_A = np.sum(seg < zone_a_lower)
            if above_A >= 2 or below_A >= 2:
                signals.append({'index': i, 'rule': 'WE2', 'desc': '2 of 3 in Zone A'})

        # WE3: 4 of 5 consecutive points in Zone B or beyond (same side)
        if i >= 4:
            seg = arr[i-4:i+1]
            above_B = np.sum(seg > zone_b_upper)
            below_B = np.sum(seg < zone_b_lower)
            if above_B >= 4 or below_B >= 4:
                signals.append({'index': i, 'rule': 'WE3', 'desc': '4 of 5 in Zone B'})

        # WE4: 8 consecutive points on same side of centreline
        if i >= 7:
            seg = arr[i-7:i+1]
            if np.all(seg > xbar) or np.all(seg < xbar):
                signals.append({'index': i, 'rule': 'WE4', 'desc': '8 points same side'})

    return signals
```

### TR-08: COPQ Category Assignment

```sql
-- GL account to COPQ category mapping
UPDATE FACT_COPQ
SET COPQ_CATEGORY = cm.COPQ_CATEGORY,
    COPQ_SUBCATEGORY = cm.COPQ_SUBCATEGORY
FROM FACT_COPQ fc
JOIN ref.COPQ_GL_MAPPING cm ON fc.HKONT = cm.HKONT;
-- Records without a mapping are flagged as UNCLASSIFIED
UPDATE FACT_COPQ
SET COPQ_CATEGORY = 'UNCLASSIFIED'
WHERE COPQ_CATEGORY IS NULL;
```

---

## 9. Business Rules

**BR-01: AQL Sampling Plan Mandatory**
All incoming lots must be inspected under an AQL sampling plan configured in SAP QM.
Skip-lot inspection is only permitted for PREFERRED suppliers (supplier quality scorecard
>= 90) with a minimum 12-month clean record (zero rejected lots). Skip-lot activation
requires Quality Manager sign-off and is documented in ref.SUPPLIER_QUALITY_CONFIG.

**BR-02: Tightened Inspection Trigger**
Per ISO 2859-1 Clause 9.3, a supplier is moved to tightened inspection (Level III) when
5 consecutive lots are rejected under normal inspection. The system automatically updates
the SAMPLING_TYPE in ref.SUPPLIER_QUALITY_CONFIG and generates a supplier quality alert.
Tightened inspection remains active until 5 consecutive lots are accepted.

**BR-03: NCR Severity Classification**
NCR severity is classified by the Quality Engineer at creation time using the following
criteria:
- CRITICAL: Safety risk, regulatory non-compliance, potential for product recall, or defects
  that cause injury. Requires immediate containment within 24 hours.
- MAJOR: Functional non-conformance that renders product unusable or out of specification.
  Containment required within 72 hours. CAPA due within 30 days.
- MINOR: Cosmetic or packaging non-conformance; product meets functional specification.
  CAPA due within 60 days.

**BR-04: CAPA Due Date Enforcement**
CAPAs overdue by > 7 days generate an automatic escalation from the responsible person's
manager. CAPAs overdue by > 30 days are escalated to the Quality Director and flagged in
the monthly supplier performance review.

**BR-05: Recurrence Detection**
A new NCR is flagged as a recurrence (RECURRENCE_FLAG = 1) when the same supplier, material
group, and root-cause code combination has had a prior NCR with a closed CAPA within the
preceding 12 months. Recurrence triggers automatic inspection level escalation.

**BR-06: Process Capability Minimum Threshold**
Production processes and incoming inspection characteristics must achieve Cpk >= 1.33 for
critical dimensions (safety-critical or functional) and Cpk >= 1.0 for non-critical
dimensions. Characteristics with Cpk < 1.0 require immediate engineering review and CAPA.
Characteristics with Cpk < 1.33 but >= 1.0 are placed on enhanced monitoring (100%
inspection until Cpk >= 1.33 sustained over 20 consecutive subgroups).

**BR-07: Minimum Sample for SPC Reliability**
SPC control limits are marked as PRELIMINARY until a minimum of 25 subgroups are available.
Preliminary limits are displayed with a dashed line in dashboards and cannot be used for
automated OOC alerts. Once 25 subgroups are reached, limits are promoted to STABLE.

**BR-08: COPQ Mandatory Classification**
All quality-related cost postings to monitored GL accounts must be classified by COPQ
category. Unclassified postings generate a weekly exception report to the Finance Quality
Cost Accountant for manual classification review.

**BR-09: Supplier Quality Scorecard Contribution**
The quality dimension contributes 30% of the overall supplier scorecard (per CLAUDE.md).
Within the quality dimension:
- PPM score: 60% weight (benchmarked against sector target — automotive 500 PPM,
  food 1,000 PPM, general 2,000 PPM)
- NCR rate: 40% weight (NCRs per 100 lots inspected; target < 2.0)

Scoring:
- PPM score = MAX(0, 100 - (Actual_PPM / Sector_Target_PPM) * 50)
- NCR rate score = MAX(0, 100 - (NCR_Rate / 2.0) * 100)

---

## 10. KPIs and Formulas

### KPI-01: Incoming PPM

```
Incoming PPM = (Total Defective Units in Sample / Total Units Inspected) × 1,000,000

Rolling 12-month Incoming PPM =
    SUM(DEFECT_COUNT_D, last 12 months) / SUM(SAMPLE_SIZE_N, last 12 months) × 1,000,000
```

Sector targets (world-class benchmarks):
- Automotive (IATF 16949): < 500 PPM
- Food & Beverage: < 1,000 PPM
- General Manufacturing: < 2,000 PPM
- Critical Medical Device: < 100 PPM

### KPI-02: DPMO (Defects Per Million Opportunities)

```
DPMO = (Total Defects Found / (Total Units Inspected × Opportunities per Unit)) × 1,000,000
```

The "Opportunities per Unit" value must be defined in the inspection plan for each material.
Default = 1 opportunity per unit when not explicitly defined (conservative assumption).

### KPI-03: Sigma Level

```
Sigma Level = NORM.S.INV(1 - DPMO / 1,000,000) + 1.5
```

Python implementation:
```python
from scipy.stats import norm
def dpmo_to_sigma(dpmo: float) -> float:
    """Convert DPMO to Sigma Level using standard 1.5-sigma shift."""
    if dpmo <= 0:
        return 6.0
    if dpmo >= 1_000_000:
        return 0.0
    return norm.ppf(1 - dpmo / 1_000_000) + 1.5
```

Sigma level benchmarks:
- 6 Sigma: 3.4 DPMO (world-class)
- 5 Sigma: 233 DPMO
- 4 Sigma: 6,210 DPMO
- 3 Sigma: 66,807 DPMO

### KPI-04: AQL Acceptance Rate

```
AQL Acceptance Rate (%) = Lots Accepted (ACCEPT decision) / Total Lots Inspected × 100
```

Target: >= 95% at Level II normal inspection (i.e., < 5% rejection rate)
Trigger for tightened inspection: < 90% acceptance over 5 consecutive lots (ISO 2859-1 §9.3)

### KPI-05: NCR Open Rate

```
NCR Open Rate (%) = Open NCRs (NCR_STATUS in (OPEN, IN_PROGRESS)) / Total NCRs × 100
```

Target: < 20% open rate (80% of NCRs should be closed within SLA)

NCR Rate per 100 Lots = Total NCRs / Total Lots Inspected × 100
Target: < 2.0 NCRs per 100 lots

### KPI-06: CAPA On-Time Closure Rate

```
CAPA On-Time Closure (%) = CAPAs closed on or before DUE_DATE / Total Closed CAPAs × 100
```

Target: >= 90% on-time closure
Critical threshold: < 70% triggers Quality Director escalation

### KPI-07: CAPA Effectiveness Rate

```
CAPA Effectiveness (%) = CAPAs with EFFECTIVENESS_SCORE >= 80 / Total Verified CAPAs × 100
```

Effectiveness verification is completed 3–6 months after CAPA implementation by re-inspecting
the same defect characteristic on new lots from the same supplier.

### KPI-08: CAPA Recurrence Rate

```
CAPA Recurrence Rate (%) = CAPAs where same defect recurred within 12 months / Total Closed CAPAs × 100
```

Target: < 10% recurrence rate
High recurrence suggests root cause was not correctly identified or CAPA was not effective.

### KPI-09: Cost of Poor Quality (COPQ)

```
COPQ Total = Internal_Failure + External_Failure + Appraisal + Prevention

COPQ as % of Revenue = COPQ_Total / Net_Revenue × 100
```

Typical COPQ benchmarks:
- Best-in-class: 1–3% of revenue
- Average manufacturers: 5–10% of revenue
- Poor performers: > 15% of revenue

COPQ subcategories:
- Internal Failure: scrap, rework, re-inspection, downtime from defects
- External Failure: returns, warranty claims, customer chargebacks, recall costs
- Appraisal: incoming inspection labour, test equipment calibration, supplier audits
- Prevention: quality training, SPC systems, design reviews, supplier development

### KPI-10: First Pass Yield (FPY)

```
FPY (%) = Units passing inspection on first attempt / Total units inspected × 100

Also: Lots with ACCEPT decision on first inspection / Total Lots × 100
```

Target: >= 95% FPY
FPY < 90% on a specific supplier/material combination triggers a formal supplier quality
improvement plan (SQIP).

### KPI-11: Process Capability Index (Cp and Cpk)

```
Cp = (USL - LSL) / (6 × sigma_est)

Cpk = MIN((USL - mean) / (3 × sigma_est), (mean - LSL) / (3 × sigma_est))
```

Interpretation:
- Cpk >= 1.67: Excellent — Six Sigma process
- Cpk >= 1.33: Capable — minimum acceptable for critical characteristics
- Cpk >= 1.0: Marginal — requires enhanced monitoring
- Cpk < 1.0: Incapable — immediate corrective action required

### KPI-12: Gage R&R (Measurement System Capability)

```
%R&R = (Measurement System Variation / Total Observed Variation) × 100
```

Acceptance criteria (AIAG MSA 4th Ed.):
- %R&R < 10%: Excellent measurement system
- %R&R 10–30%: Marginal (may be acceptable based on application)
- %R&R > 30%: Unacceptable — measurement system must be improved

---

## 11. Analytical Logic

### AQL Inspection Level Management

ISO 2859-1 defines three inspection levels (I, II, III) and three switching rules:

**Normal to Tightened**: 2 of 5 consecutive lots rejected under normal inspection.
System action: Update SAMPLING_TYPE = TIGHTENED in ref.SUPPLIER_QUALITY_CONFIG;
send alert to Supplier Quality Engineer.

**Tightened to Discontinue**: 5 consecutive lots rejected under tightened inspection.
System action: Set SAMPLING_TYPE = DISCONTINUE; escalate to Quality Manager;
block future PO releases for this supplier/material combination pending quality review.

**Normal to Reduced**: 10 consecutive lots accepted, production rate steady, no quality
concerns. System action: Update SAMPLING_TYPE = REDUCED; log reduction date.

**Reduced to Normal**: Any lot rejected, or lot is conditionally accepted, or production
is irregular. System action: Immediate revert to NORMAL.

All switching events are logged in audit table audit.AQL_SWITCHING_LOG with timestamp,
trigger condition, and responsible approver.

### NCR Severity Classification and Response Times

| Severity | Definition | Containment SLA | CAPA Due | Escalation |
|----------|------------|-----------------|----------|------------|
| CRITICAL | Safety / regulatory / recall risk | 24 hours | 14 days | Quality Director + Legal + VP Supply Chain |
| MAJOR | Functional non-conformance | 72 hours | 30 days | Quality Manager |
| MINOR | Cosmetic / packaging non-conformance | 5 business days | 60 days | Supplier Quality Engineer |

### NCR Pareto Analysis (Root Cause)

Root causes are classified using the Ishikawa (5M+E) framework:
- MAN: Operator error, insufficient training, procedure not followed
- MACHINE: Equipment failure, tooling wear, calibration drift
- MATERIAL: Raw material non-conformance, incorrect specification
- METHOD: Incorrect process parameter, missing or inadequate SOP
- MEASUREMENT: Measurement system error, gage out of calibration
- ENVIRONMENT: Temperature, humidity, contamination

The top three root cause categories by NCR count and by financial impact are reported
monthly. Root cause Pareto drives the annual Quality Improvement Plan focus areas.

### CAPA Aging Buckets

Open CAPAs are classified by age from creation date:
- GREEN: 0–30 days (within normal working period)
- AMBER: 31–60 days (approaching or at due date)
- RED: 61–90 days (overdue — manager escalated)
- CRITICAL_OVERDUE: > 90 days (escalated to Quality Director)

CAPA aging distribution is monitored weekly. Any business unit or supplier with > 20%
of CAPAs in RED or CRITICAL_OVERDUE bucket triggers a management review.

### SPC Alert Trigger Logic

Out-of-control signals trigger the following automated workflow:

| OOC Rule | Signal Description | Immediate Action |
|----------|-------------------|------------------|
| WE1 | Point beyond 3-sigma limit | Auto-hold production batch; notify QC Engineer |
| WE2 | 2 of 3 in Zone A | Alert QC Engineer; review last 10 subgroups |
| WE3 | 4 of 5 in Zone B | Alert QC Engineer; schedule process review |
| WE4 | 8 consecutive on same side | Alert Process Engineer; trend investigation |
| WE5–WE8 | Patterns suggesting systematic shift | Alert; schedule formal process review |

All OOC signals are logged in analytics.SPC_OOC_SIGNALS. Unacknowledged signals
older than 4 hours escalate to the QC Supervisor.

### Supplier Quality Score Calculation

The quality dimension of the supplier scorecard (30% of total) is calculated as follows:

```
Quality_Score = (PPM_Score × 0.60) + (NCR_Rate_Score × 0.40)

PPM_Score = MAX(0, 100 - (Rolling_12M_PPM / Sector_PPM_Target) × 50)
NCR_Rate_Score = MAX(0, 100 - (NCR_per_100_lots / 2.0) × 100)
```

A supplier with zero defects in 12 months achieves PPM_Score = 100.
A supplier at exactly the sector PPM target achieves PPM_Score = 50.
A supplier at 2× the sector target achieves PPM_Score = 0 (floor).

---

## 12. Validations and Controls

### Data Quality Controls

| Control ID | Description | Severity | Action |
|------------|-------------|----------|--------|
| DQC-01 | PRUEFLOS unique in FACT_IQC | Critical | Block load; alert QM administrator |
| DQC-02 | DEFECT_COUNT_D <= SAMPLE_SIZE_N | Critical | Reject record; quarantine to error table |
| DQC-03 | SAMPLE_SIZE_N matches AQL table for lot size | High | Flag mismatch; alert Supplier Quality Engineer |
| DQC-04 | AQL_VALUE is a standard ISO 2859-1 value | High | Reject if non-standard; default to AQL 1.0 with alert |
| DQC-05 | NCR QMNUM unique in FACT_NCR | Critical | Block load; alert QM administrator |
| DQC-06 | NCR_SEVERITY populated for all F3 notifications | High | Reject; return to Quality Engineer for classification |
| DQC-07 | CAPA DUE_DATE >= parent NCR CREATION_DATE | High | Reject CAPA record; alert responsible person |
| DQC-08 | Cp >= Cpk (mathematical constraint) | Critical | Flag calculation error; rerun SPC engine |
| DQC-09 | SPC UCL > XBAR > LCL (control limit order) | Critical | Flag; do not publish until resolved |
| DQC-10 | COPQ_CATEGORY is not UNCLASSIFIED after 7 days | Medium | Weekly exception report to Finance |

### Reconciliation Controls

- Daily: Count of inspection lots in FACT_IQC vs. SAP QM transaction QA03 (lot count by
  creation date). Tolerance: zero unmatched.
- Weekly: Count of open NCRs in FACT_NCR vs. SAP QM notification list IW29 filtered to
  quality notification types F1/F2/F3. Tolerance: zero unmatched.
- Monthly: Total COPQ_AMOUNT in FACT_COPQ vs. SAP CO report for quality cost centres.
  Tolerance: < EUR 100 rounding difference.
- Quarterly: Supplier rolling PPM in analytics layer reviewed and confirmed by Supplier
  Quality Engineers against their independently maintained records. Tolerance: < 5% variance.

---

## 13. Required Evidence

| Evidence Item | Description | Owner | Required By |
|---------------|-------------|-------|-------------|
| EV-01 | SAP QM inspection lot field mapping (QMEL, QMFE, QMUR) | SAP QM Consultant | Phase 1 |
| EV-02 | SAP QM Quality Notification field mapping (all types) | Quality Manager | Phase 1 |
| EV-03 | AQL sampling plan configuration extract from SAP QM | QM System Admin | Phase 1 |
| EV-04 | Supplier sector classification (automotive/food/general) | Supplier Quality Engineer | Phase 1 |
| EV-05 | COPQ GL account mapping table signed off by Finance | Finance Controller | Phase 2 |
| EV-06 | Control plan extract — CTQ characteristics requiring SPC | Quality Engineering | Phase 2 |
| EV-07 | SPC engine Python code review and test results | Quality Analytics Engineer | Phase 2 |
| EV-08 | SPC validation against Minitab for 5 test cases | Quality Manager | Phase 3 |
| EV-09 | NCR severity classification guidelines (written procedure) | Quality Manager | Phase 1 |
| EV-10 | CAPA due date policy document | Quality Director | Phase 1 |
| EV-11 | Sector PPM targets approved by Quality Director | Quality Director | Phase 1 |
| EV-12 | Opportunities-per-unit value for top 50 materials by spend | Quality Engineering | Phase 2 |

---

## 14. Dashboard Design

### Dashboard 1: Quality Executive Summary

**Audience**: Quality Director, VP Supply Chain, CPO
**Refresh**: Daily at 06:00
**Layout**: Single-page executive KPI summary

Key visuals:
- KPI cards: Incoming PPM (rolling 12M), DPMO, Sigma Level, COPQ YTD, CAPA On-Time %
- PPM trend: Rolling 12-month line chart by month vs. sector target
- Supplier quality heatmap: matrix of suppliers vs. months with PPM colour-coded
- NCR severity distribution: stacked bar (CRITICAL / MAJOR / MINOR) by month
- COPQ waterfall: breakdown by Internal Failure, External Failure, Appraisal, Prevention
- Top 5 suppliers by NCR count: ranked bar chart with financial impact

### Dashboard 2: Incoming Inspection (IQC) Detail

**Audience**: QC Supervisor, Incoming QC Team, Supplier Quality Engineers
**Refresh**: Every 2 hours (near real-time)

Key visuals:
- Lots pending inspection: operational count with age indicator
- AQL acceptance rate by supplier: ranked bar chart with tightened inspection flags
- PPM by supplier and material group: heat matrix
- Inspection level distribution: pie chart (NORMAL / TIGHTENED / REDUCED / SKIP-LOT)
- Lot disposition breakdown: stacked bar (ACCEPT / REJECT / CONDITIONAL / SCRAP / REWORK)
- First Pass Yield trend: line chart by month with 95% target reference line

### Dashboard 3: NCR and CAPA Management

**Audience**: Quality Manager, Quality Engineers, Supplier Quality Engineers
**Refresh**: Daily

Key visuals:
- Open NCR aging: stacked bar by CRITICAL/MAJOR/MINOR × age bucket (green/amber/red)
- NCR root cause Pareto: horizontal bar chart (Man/Machine/Material/Method/Measurement/Environment)
- CAPA on-time closure: gauge chart vs. 90% target
- CAPA overdue list: table with supplier, NCR number, days overdue, responsible person
- NCR financial impact: treemap by supplier with total EUR value of open NCRs
- Recurrence rate trend: line chart by quarter vs. 10% target

### Dashboard 4: SPC and Process Capability

**Audience**: Quality Engineers, Process Engineers, Manufacturing Supervisors
**Refresh**: Triggered on each new inspection lot; displayed in near real-time

Key visuals:
- X-bar/R control chart: for selected material and characteristic — interactive slicer
- Cpk distribution: histogram of all monitored characteristics vs. 1.33 threshold
- Capability summary table: MATNR, MERKMAL, Cp, Cpk, Pp, Ppk, OOC status — RAG coded
- OOC signal log: table of recent Western Electric rule violations with rule code and date
- Preliminary vs. stable limits: flag indicators for characteristics still in PRELIMINARY status
- Process trend: Cpk trend over 6 months for selected characteristic

### Dashboard 5: Supplier Quality Scorecard Contribution

**Audience**: Supplier Quality Manager, Category Manager, Procurement Director
**Refresh**: Monthly (1st business day)

Key visuals:
- Supplier quality score table: all active suppliers with PPM Score, NCR Rate Score,
  composite Quality Score, trend vs. prior quarter
- Sector benchmarking: supplier PPM vs. sector target — scatter plot
- CAPA effectiveness by supplier: bar chart with effectiveness score and recurrence rate
- Suppliers on tightened inspection: alert panel with supplier, trigger date, lots remaining
- Quality improvement trajectory: 12-month Cpk and PPM trend for top 10 development suppliers
- COPQ attribution by supplier: pie chart of external failure costs by supplier

---

## 15. Use Cases

### UC-01: Incoming Lot Disposition Decision Support

**User**: QC Inspector / QC Supervisor
**Trigger**: New inspection lot created in SAP QM after GR posting
**Process**:
1. Inspector retrieves lot from Dashboard 2 (Lots Pending Inspection)
2. System displays: sample size from AQL table, acceptance number, rejection number,
   supplier historical PPM, prior NCRs for this material
3. Inspector records defect count and defect types in SAP QM
4. System automatically determines AQL decision (TR-02) and proposes disposition
5. For REJECT decision: system pre-populates NCR creation form with supplier, material, batch
6. Quality Engineer reviews and confirms disposition; lot moves to ACCEPTED, RETURNED, or SCRAP

**Analytical Output**: AQL decision, lot PPM, disposition recommendation

### UC-02: Supplier Quality Review — Monthly Business Review

**User**: Supplier Quality Engineer
**Trigger**: First week of each month
**Process**:
1. Extract supplier rolling 12-month PPM, NCR rate, AQL acceptance rate from Dashboard 5
2. Compare against sector PPM target; identify suppliers in top 10% worst performers
3. Pull CAPA status for all open NCRs for prioritised suppliers
4. Check AQL switching status: any suppliers on TIGHTENED or at DISCONTINUE threshold
5. Prepare supplier quality letter and 8D root cause request for suppliers > 2× sector PPM
6. Update supplier quality scorecard component; feed into overall scorecard

### UC-03: CAPA Overdue Escalation Management

**User**: Quality Manager
**Trigger**: Daily automated alert; weekly management review
**Process**:
1. Filter FACT_CAPA where AGE_DAYS > DUE_DATE and IS_ON_TIME IS NULL (open and overdue)
2. Group by responsible person and by severity of linked NCR
3. Generate escalation letters for CAPAs overdue > 30 days
4. Update CAPA management tracker and report to Quality Director
5. For critical-severity CAPAs overdue > 14 days: escalate to VP Supply Chain

### UC-04: SPC Out-of-Control Response

**User**: QC Engineer / Process Engineer
**Trigger**: OOC signal detected by Python SPC engine
**Process**:
1. SPC engine writes OOC record to analytics.SPC_OOC_SIGNALS
2. Alert sent to QC Engineer via email and displayed on Dashboard 4 OOC signal log
3. QC Engineer investigates: reviews recent subgroups, production log, machine parameters
4. If assignable cause found: log in SAP QM as a quality notification (F2 — internal defect)
5. Production may continue if OOC is WE2/WE3/WE4 (trend) with documented justification
6. For WE1 (beyond 3-sigma): batch on hold pending investigation

### UC-05: COPQ Annual Budget Review

**User**: Quality Controller, Finance Business Partner
**Trigger**: Quarterly and annual budget review cycle
**Process**:
1. Extract COPQ by category from FACT_COPQ for fiscal year-to-date
2. Calculate COPQ as % of revenue; compare against prior year and industry benchmark
3. Decompose External Failure by supplier: identify top 3 suppliers driving warranty / return costs
4. Build COPQ reduction business case: CAPA investments vs. projected failure cost reduction
5. Present to Quality Director and CFO for annual quality budget approval

---

## 16. Recommended Actions

### RA-01: Skip-Lot Programme for Top-Performing Suppliers

Implement a formal skip-lot programme (ISO 2859-3) for PREFERRED suppliers that have
demonstrated zero rejections over 12 consecutive months and Cpk >= 1.67 on all critical
characteristics. Skip-lot reduces incoming inspection cost by 60–80% for these suppliers.
Estimated annual inspection labour saving: EUR 80k–150k based on current inspection volume.

### RA-02: Automated NCR Creation from AQL Rejection

Currently, NCR creation after an AQL rejection is a manual step taken by the QC Inspector.
This creates a gap: rejected lots are sometimes not formally NCR'd, resulting in dispositions
not being tracked. Implement an automated SAP QM workflow that creates a draft F3 notification
automatically upon REJECT decision, requiring only the Quality Engineer to confirm severity
and root cause before activation.

### RA-03: Supplier Self-Service Quality Portal

Implement a supplier-facing quality portal where suppliers can view their real-time PPM
dashboard, open NCRs, overdue CAPAs, and current inspection level. Self-service transparency
reduces inbound enquiries to the Supplier Quality team by an estimated 40% and accelerates
CAPA response times by making overdue items visible to the supplier without waiting for a
formal letter.

### RA-04: SPC Real-Time Monitoring at Receiving Dock

Deploy SPC monitoring at the receiving dock for the top 20 incoming materials by inspection
volume. Use Python SPC engine integrated with a tablet-based inspection data entry tool
(replacing paper-based inspection forms) to capture measurement data in real-time. This
enables immediate OOC detection during the inspection process rather than retrospectively.

### RA-05: COPQ Reduction via Supplier Development Programme

The top 5 suppliers by external failure COPQ contribution should be enrolled in a formal
Supplier Development Programme (SDP). The SDP includes:
- On-site process audit within 30 days
- IATF-style production part approval process (PPAP) for critical components
- Assigned Supplier Quality Engineer for 6-month improvement partnership
- Monthly PPM review with CAPA tracking
- Contractual PPM improvement targets with commercial consequence clauses

### RA-06: Gage R&R Study Programme

Commission a Gage R&R study for the top 15 critical inspection characteristics where
measurement system capability has not been formally verified. Unqualified measurement
systems contribute to false acceptance and false rejection decisions, inflating both COPQ
(false rejections leading to scrap) and customer risk (false acceptances passing non-conforming
product). Target: all CTQ characteristics verified with %R&R < 10% within 12 months.

---

## 17. Test Cases

### TC-01: PPM Calculation Accuracy

**Scenario**: Inspection lot with SAMPLE_SIZE_N = 200; DEFECT_COUNT_D = 3.
**Expected PPM**: 3 / 200 × 1,000,000 = 15,000 PPM
**Test Method**: Insert record into FACT_IQC; execute TR-01; verify INCOMING_PPM = 15000.0.
**Pass Criteria**: INCOMING_PPM = 15000.0 ± 0.1.

### TC-02: AQL Decision — Accept

**Scenario**: Lot size 500 units; Level II; AQL 1.0. ISO 2859-1 → sample letter H →
n = 50; Ac = 1; Re = 2. DEFECT_COUNT_D = 1.
**Expected AQL_DECISION**: ACCEPT (1 <= 1)
**Pass Criteria**: AQL_DECISION = 'ACCEPT'.

### TC-03: AQL Decision — Reject

**Same scenario but DEFECT_COUNT_D = 2.**
**Expected AQL_DECISION**: REJECT (2 >= 2)
**Pass Criteria**: AQL_DECISION = 'REJECT'; NCR draft auto-created (RA-02 implemented).

### TC-04: Cpk Calculation Accuracy

**Scenario**: 30 measurements with mean = 50.2, sigma_est = 1.5, USL = 55.0, LSL = 45.0.
**Expected**:
- Cp = (55 - 45) / (6 × 1.5) = 10 / 9 = 1.111
- Cpu = (55 - 50.2) / (3 × 1.5) = 4.8 / 4.5 = 1.067
- Cpl = (50.2 - 45) / (3 × 1.5) = 5.2 / 4.5 = 1.156
- Cpk = MIN(1.067, 1.156) = 1.067
**Pass Criteria**: Cp = 1.111 ± 0.001; Cpk = 1.067 ± 0.001. STATUS = STABLE.

### TC-05: CAPA On-Time Flag

**Scenario**: CAPA due 2026-06-15; actual closure 2026-06-20 (5 days late).
**Expected**: IS_ON_TIME = 0; AGE_DAYS = 5 past due.
**Pass Criteria**: IS_ON_TIME = 0; record appears in overdue CAPA list in Dashboard 3.

### TC-06: Western Electric Rule WE1

**Scenario**: Control chart with UCL = 105.0; LCL = 95.0; XBAR = 100.0.
Point value = 106.5 (beyond UCL).
**Expected**: OOC_FLAG = 1; OOC_RULE = 'WE1'.
**Pass Criteria**: OOC record in analytics.SPC_OOC_SIGNALS; alert triggered to QC Engineer.

### TC-07: Tightened Inspection Trigger

**Scenario**: Supplier S001, material group MG01. 2 of last 5 consecutive lots rejected.
**Expected**: SAMPLING_TYPE updated to TIGHTENED in ref.SUPPLIER_QUALITY_CONFIG;
AQL_SWITCHING_LOG record created with trigger = '2OF5_REJECTED'.
**Pass Criteria**: SAMPLING_TYPE = 'TIGHTENED'; switching log entry exists; supplier quality alert sent.

### TC-08: DPMO and Sigma Level

**Scenario**: DPMO = 3,400.
**Expected Sigma Level**: norm.ppf(1 - 3400/1,000,000) + 1.5 ≈ 4.5 sigma
**Pass Criteria**: Sigma Level output = 4.5 ± 0.05.

### TC-09: Recurrence Flag Detection

**Scenario**: Supplier S002, material group MG05, root cause = MATERIAL. Prior NCR closed
with CAPA on 2025-12-01. New NCR same supplier/material/root cause created 2026-05-15
(within 12 months).
**Expected**: RECURRENCE_FLAG = 1; PRIOR_QMNUM populated.
**Pass Criteria**: RECURRENCE_FLAG = 1; inspection level escalated to TIGHTENED.

### TC-10: COPQ Category Assignment

**Scenario**: GL account 500100 maps to INTERNAL_FAILURE / SCRAP per ref.COPQ_GL_MAPPING.
FI posting EUR 1,250 to GL 500100.
**Expected**: COPQ_CATEGORY = 'INTERNAL_FAILURE'; COPQ_SUBCATEGORY = 'SCRAP'.
**Pass Criteria**: FACT_COPQ record with correct categories; not marked UNCLASSIFIED.

---

## 18. Risks and Mitigations

| Risk ID | Risk Description | Likelihood | Impact | Mitigation |
|---------|-----------------|------------|--------|------------|
| R-01 | SAP QM inspection results incomplete — inspectors record accept/reject but not individual defect counts | High | High | Training; mandatory defect count field in SAP QM inspection cockpit; daily completeness report |
| R-02 | Python SPC engine calculation discrepancy vs. SAP QM native SPC | Medium | High | Validation test cases (TC-04); parallel running period with manual spot-checks |
| R-03 | Opportunities-per-unit not defined for all materials — DPMO calculation inaccurate | High | Medium | Default to 1 opportunity; flag as ESTIMATED; Quality Engineering to define for top 100 materials |
| R-04 | COPQ GL account mapping incomplete — significant costs unclassified | Medium | High | Weekly exception report; Finance sign-off on mapping before go-live |
| R-05 | NCR severity under-classification — critical NCRs downgraded to avoid escalation | Medium | Critical | Severity definition embedded in SAP QM notification form; random audit of F3 severity by Quality Manager |
| R-06 | SPC sample size insufficient for reliable control limits (< 25 subgroups) | High | Medium | PRELIMINARY flag on dashboard; alert when nearing 25 subgroup threshold |
| R-07 | Supplier quality data — 12-month rolling window crosses SAP go-live date; history unavailable | High | Medium | Load historical inspection results from legacy QMS or paper records for top 20 suppliers |
| R-08 | AQL switching rule not enforced — suppliers remain on normal inspection despite trigger | Medium | High | Automated switching rule in transformation job; weekly audit of SAMPLING_TYPE vs. lot history |
| R-09 | CAPA due dates not set consistently — some CAPAs have arbitrary dates reducing KPI value | Medium | Medium | Standard due date policy (BR-04) embedded in SAP QM workflow; mandatory field validation |
| R-10 | Apache Superset SPC chart performance — large volume of inspection results causes slow refresh | Medium | Medium | Pre-aggregate control chart data in Python job; store computed limits in PostgreSQL |

---

## 19. Implementation Checklist

### Phase 1: Data Foundation (Weeks 1–8)

- [ ] SAP QM inspection lot field mapping completed and validated
- [ ] SAP QM quality notification field mapping completed
- [ ] PostgreSQL quality analytics schema created (FACT, DIM, stg, ref, analytics, audit tables)
- [ ] DIM_SUPPLIER loaded with quality sector classification (automotive/food/general)
- [ ] DIM_MATERIAL loaded with control plan CTQ flags
- [ ] DIM_DEFECT_TYPE loaded from SAP QM defect code master
- [ ] ref.AQL_SAMPLING_PLAN table loaded from ISO 2859-1 (Table II-A for all AQL levels)
- [ ] ref.SUPPLIER_QUALITY_CONFIG loaded with current inspection level per supplier
- [ ] ref.COPQ_GL_MAPPING loaded and signed off by Finance Controller
- [ ] SAP QM → PostgreSQL ETL pipeline deployed (FACT_IQC, FACT_NCR, FACT_CAPA, FACT_COPQ)
- [ ] Sector PPM targets loaded and approved by Quality Director
- [ ] Historical inspection lots loaded (minimum 24 months where available)

### Phase 2: KPI and SPC Layer (Weeks 9–16)

- [ ] TR-01 through TR-08 transformation rules implemented and unit-tested
- [ ] Python SPC engine (python/08_quality/spc_engine.py) deployed to Python compute
- [ ] Western Electric rule detection (python/08_quality/western_electric_rules.py) deployed
- [ ] SPC engine validated against Minitab for 5 test cases (TC-04)
- [ ] Rolling PPM calculation (TR-05) implemented and back-tested on 12-month history
- [ ] CAPA on-time flag and age calculation tested (TC-05)
- [ ] Tightened inspection trigger logic tested (TC-07)
- [ ] Recurrence detection logic tested (TC-09)
- [ ] All 10 alert triggers implemented and tested in non-production environment
- [ ] Apache Superset data model connected to PostgreSQL; all 5 dashboards built

### Phase 3: Scorecard and Workflows (Weeks 17–22)

- [ ] Supplier quality scorecard calculation implemented and back-tested
- [ ] AQL switching audit job deployed and scheduled
- [ ] COPQ monthly report automated
- [ ] NCR auto-creation from AQL reject implemented (RA-02)
- [ ] Training delivered to Quality team, QC Inspectors, Supplier Quality Engineers
- [ ] User acceptance testing with Quality Manager sign-off
- [ ] Production go-live and hypercare period

---

## 20. Validation Checklist

- [ ] Incoming PPM for top 10 suppliers matches independent QM team calculation within 5%
- [ ] AQL decisions for 50 test lots reviewed and confirmed correct by Quality Engineer
- [ ] Cpk for 10 characteristics matches Minitab output within ±0.01
- [ ] Open NCR count in analytics matches SAP QM IW29 report — zero discrepancy
- [ ] CAPA on-time closure rate matches Quality Manager's manual tracker within ±2 pp
- [ ] COPQ total in analytics matches SAP CO quality cost centre report within EUR 100
- [ ] All 7 AQL switching trigger scenarios tested and correct outcomes verified
- [ ] All 8 Western Electric OOC rules produce alerts in test environment
- [ ] UFLPA-blocked supplier materials reflected in supplier quality config restrictions
- [ ] Dashboard refresh SLA: daily dashboards available by 07:00; SPC triggered within 15 min of lot closure
- [ ] Data retention policy confirmed: 10 years for inspection records (medical/food grade); 7 years general
- [ ] GDPR/data privacy review completed — no PII in quality inspection records

---

## 21. Pending Information

| Item ID | Information Required | From Whom | Impact if Missing | Target Date |
|---------|---------------------|-----------|-------------------|-------------|
| PI-01 | Opportunities-per-unit definition for top 100 materials by inspection volume | Quality Engineering | DPMO uses default of 1; underestimates true DPMO | Week 4 |
| PI-02 | Historical inspection results for top 20 suppliers (pre-SAP go-live) | Quality Manager / Legacy QMS | Rolling PPM will be < 12 months for Year 1 | Week 2 |
| PI-03 | Sector classification for all active suppliers (automotive / food / general) | Supplier Quality Engineers | Default sector PPM target (general 2,000) applied; may be wrong | Week 3 |
| PI-04 | COPQ GL account list and category mapping | Finance Controller | COPQ reporting unavailable until mapping complete | Week 5 |
| PI-05 | Control plan extract — CTQ characteristics requiring SPC per material | Quality Engineering | SPC engine will not know which characteristics to calculate | Week 6 |
| PI-06 | Specification limits (USL / LSL) for all CTQ characteristics | Engineering / R&D | Cannot calculate Cp or Cpk without specification limits | Week 6 |
| PI-07 | CAPA due date policy document — standard due dates by severity | Quality Director | CAPA on-time KPI may be calculated inconsistently | Week 2 |
| PI-08 | Gage R&R study results for top CTQ characteristics | Quality Engineering | Cannot flag measurement system issues; %R&R KPI unavailable | Week 12 |

---

## 22. Implementation Roadmap

### Phase 1: Data Foundation and Infrastructure (Months 1–2)

**Objective**: Establish all data pipelines, master data, reference tables, and base ETL.

Week 1–2: PostgreSQL schema creation; SAP QM field mapping documents; Apache Superset workspace
Week 3–4: SAP QM ETL pipeline deployed (inspection lots, quality notifications, CAPA tasks)
Week 5–6: Reference tables loaded (AQL plan, COPQ mapping, sector targets, supplier config)
Week 7–8: Historical data load (24 months inspection history); DIM tables populated

**Milestone**: 24 months of inspection history in PostgreSQL; zero ETL errors on daily reconciliation.

### Phase 2: KPI and Analytics Layer (Months 3–4)

**Objective**: Implement all KPI calculations, SPC engine, and Apache Superset dashboards.

Week 9–10: TR-01 through TR-05 implemented; PPM, AQL decision, CAPA flags validated
Week 11–12: Python SPC engine deployed; Cpk and OOC calculation validated vs. Minitab
Week 13–14: Supplier quality scorecard calculation back-tested; alert engine deployed
Week 15–16: All 5 dashboards built; initial UAT with Quality Manager and 3 QC Engineers

**Milestone**: All KPIs validated; OOC alerts firing correctly in test environment.

### Phase 3: Advanced Analytics and Workflow Automation (Months 5–6)

**Objective**: Deliver automated workflows, supplier quality portal, and production go-live.

Week 17–18: NCR auto-creation from AQL reject (RA-02); CAPA escalation workflow
Week 19–20: AQL switching rule automation deployed and tested; COPQ monthly report automated
Week 21–22: Training delivery (QC team, Supplier Quality Engineers, Quality Manager)
Week 23–24: Production go-live; hypercare period; first monthly quality KPI review

**Milestone**: Production go-live signed off by Quality Director; first monthly Supplier Quality Review produced from analytics platform.

### Phase 4: Continuous Improvement (Months 7–12)

**Objective**: Expand SPC coverage, launch skip-lot programme, and drive measurable COPQ reduction.

Month 7–8: Skip-lot programme for PREFERRED suppliers (RA-01); Gage R&R study programme (RA-06)
Month 9–10: Supplier Development Programme launched for top 5 COPQ contributors (RA-05)
Month 11–12: 12-month performance review; PPM improvement vs. baseline; COPQ reduction vs. target

**Milestone**: 30% incoming PPM reduction vs. baseline for enrolled SDP suppliers;
CAPA on-time closure rate >= 90%; Cpk >= 1.33 on all monitored CTQ characteristics.

---

## References

- ISO 9001:2015 — Quality management systems — Requirements (Clauses 8.4, 8.5.2, 8.6, 8.7)
- ISO 2859-1:1999 — Sampling procedures for inspection by attributes (AQL sampling plans)
- IATF 16949:2016 — Quality management system requirements for automotive production
- AIAG Measurement System Analysis (MSA) Reference Manual, 4th Ed. (Automotive Industry Action Group, 2010)
- AIAG Failure Mode and Effects Analysis (FMEA), 4th Ed. (Automotive Industry Action Group, 2008)
- Montgomery, D.C., Introduction to Statistical Quality Control, 8th Ed. (Wiley, 2020)
- Pyzdek, T. & Keller, P., The Six Sigma Handbook, 5th Ed. (McGraw-Hill, 2018)
- Western Electric Company, Statistical Quality Control Handbook (Western Electric, 1956)
- SAP S/4HANA 2023 — Quality Management Configuration Guide (SAP SE)
- SAP QM Inspection Planning and Processing User Guide (SAP SE)
- Chopra & Meindl, Supply Chain Management, 6th Ed. (Pearson, 2016), Chapter 5 — Sourcing
- SCOR Digital Standard — Enable Process Category (ASCM, 2019)
- ASQ Body of Knowledge for Quality Engineer Certification (ASQ, 2022)
- GS1 General Specifications v23.0 — Unit of Measure codes
- EU Good Manufacturing Practice (GMP) Annex 11 — Computerised Systems (EMA, 2011)
