# Supplier Development & ESG Analytics — Implementation Specification

> Analytical implementation document for a data / BI / automation team.
> Scope: Supplier Development Program Tracking, CAPA Tracking, ESG Score Monitoring,
> Development ROI, Audit Finding Trends.
> Context: €50B multinational, 40 countries, SAP S/4HANA QM + Ariba SLP +
> custom ESG database, Power BI, Azure SQL, Python. Quarterly business reviews.

---

## 1. Executive Summary

This document specifies the analytical implementation for monitoring supplier
development programmes and ESG performance across the strategic supply base. It
defines the data, transformations, KPIs, validations, and dashboards required to
track scorecard improvement trajectories, manage CAPA closure and recurrence,
monitor ESG composite scores, quantify development ROI, and trend audit findings.

The deliverable is a governed Power BI solution on Azure SQL, refreshed daily (CAPA,
audit) and quarterly (ESG, ROI), used by Supplier Development Engineers (SDE),
Sustainability, and Procurement leadership. Metrics reconcile to SAP QM, Ariba SLP,
and the ESG database.

---

## 2. Analysis Objective

- Track each development supplier's scorecard improvement trajectory vs. its target.
- Manage CAPA lifecycle: on-time closure, recurrence, and aging.
- Monitor ESG composite (E/S/G) scores and flag deterioration or greenwashing risk.
- Quantify development ROI (savings vs. investment) per supplier and programme.
- Trend audit findings by theme to drive systemic improvement.

---

## 3. Scope

**In scope**: all suppliers enrolled in an active development programme; all CAPAs
(supplier-attributable); ESG assessments for Tier-1 strategic suppliers; audit reports;
trailing 24 months.

**Out of scope**: non-enrolled suppliers (monitored via Dept 02 scorecard); internal
CAPAs; ESG self-declarations without supporting evidence (flagged, not scored).

---

## 4. Business Questions

- Which development suppliers are on track to reach their target score by milestone?
- Which suppliers are stalled or regressing despite development investment?
- What is the CAPA on-time closure rate and recurrence rate by supplier?
- Which CAPAs are aging beyond their due date (and by how long)?
- What is each supplier's ESG composite score and its trend?
- Which suppliers show ESG declaration vs. evidence gaps (greenwashing risk)?
- What is the ROI of each development programme?
- Which audit finding themes recur across the supply base?
- How many suppliers were promoted (PROBATION→APPROVED, →PREFERRED) this period?
- Which strategic suppliers lack a current ESG assessment?

---

## 5. Data Sources

### Source 1 — Supplier Scorecard History
- **Source Name**: Supplier scorecard monthly history
- **Origin System**: Dept 02 analytics model (fact_scorecard_monthly) / Ariba SLP
- **Report/Table/Query**: fact_scorecard_monthly
- **Data Owner**: Supplier Quality / SDE
- **Update Frequency**: Monthly
- **Required Fields**: `lifnr, period, composite_score, rating, delivery_sub, quality_sub`
- **Critical Fields**: `composite_score`, `rating`, `period`
- **Primary/Logical Key**: lifnr + period
- **Required Validations**: score in [0,100]; continuous monthly series
- **Possible Errors**: missing months breaking trajectory slope
- **Extraction Evidence**: supplier-month count vs Dept 02 model

### Source 2 — CAPA Records
- **Source Name**: Corrective & Preventive Actions
- **Origin System**: SAP S/4HANA (QM) Quality Notifications + tasks (QMSM)
- **Report/Table/Query**: QMEL + QMSM (tasks) + QMUR (causes)
- **Data Owner**: SDE / Quality
- **Update Frequency**: Daily
- **Required Fields**: `capa_id, lifnr, opened_date, due_date, closed_date, root_cause_code,
  status, finding_ref, effectiveness_verified_flag`
- **Critical Fields**: `due_date`, `closed_date`, `root_cause_code`
- **Primary/Logical Key**: capa_id
- **Required Validations**: closed_date ≥ opened_date; due_date present
- **Possible Errors**: CAPA closed without effectiveness verification; missing root cause
- **Extraction Evidence**: CAPA count per supplier vs SAP QM12

### Source 3 — ESG Assessments
- **Source Name**: ESG assessment results
- **Origin System**: Custom ESG database (Azure SQL) / third-party (EcoVadis-style) feed
- **Report/Table/Query**: esg_assessment table
- **Data Owner**: Sustainability / Procurement
- **Update Frequency**: Quarterly (or per assessment cycle)
- **Required Fields**: `lifnr, assessment_date, e_score, s_score, g_score,
  evidence_completeness_pct, declared_vs_evidence_gap, assessor, valid_until`
- **Critical Fields**: `e_score, s_score, g_score, evidence_completeness_pct`
- **Primary/Logical Key**: lifnr + assessment_date
- **Required Validations**: scores in [0,100]; valid_until ≥ assessment_date
- **Possible Errors**: expired assessments treated as current; self-declared without evidence
- **Extraction Evidence**: assessment count vs ESG DB

### Source 4 — Development Programme & Investment
- **Source Name**: Development programme master & cost
- **Origin System**: Custom programme tracker (SharePoint/Azure SQL) + FI cost postings
- **Report/Table/Query**: dev_program table + FI internal orders
- **Data Owner**: SDE
- **Update Frequency**: Monthly
- **Required Fields**: `program_id, lifnr, start_date, target_score, target_date,
  investment_cost, baseline_score, strategic_importance, improvement_potential`
- **Critical Fields**: `target_score, target_date, investment_cost, baseline_score`
- **Primary/Logical Key**: program_id
- **Required Validations**: target_score > baseline_score; cost ≥ 0
- **Possible Errors**: investment not fully captured; missing baseline
- **Extraction Evidence**: programme cost vs FI internal order total

### Source 5 — Audit Findings
- **Source Name**: Supplier audit findings
- **Origin System**: Ariba SLP audits / custom audit log
- **Report/Table/Query**: audit_finding table
- **Data Owner**: Supplier Quality Audit team
- **Update Frequency**: Per audit (event-driven) + daily load
- **Required Fields**: `finding_id, lifnr, audit_date, theme, severity, status,
  closure_date, capa_ref`
- **Critical Fields**: `theme, severity, status`
- **Primary/Logical Key**: finding_id
- **Required Validations**: severity in allowed list; theme mapped to taxonomy
- **Possible Errors**: free-text themes not normalised; findings without CAPA link
- **Extraction Evidence**: finding count per audit vs audit report

### Source 6 — Benefit / Savings Data (for ROI)
- **Source Name**: Realised benefits from development
- **Origin System**: Dept 02 (PPM/NCR/OTD deltas) + Dept 11 (cost savings)
- **Report/Table/Query**: derived benefit table
- **Data Owner**: Procurement Analytics
- **Update Frequency**: Quarterly
- **Required Fields**: `program_id, lifnr, ppm_savings_value, ncr_cost_savings,
  otd_improvement_value, period`
- **Critical Fields**: benefit values
- **Primary/Logical Key**: program_id + period
- **Required Validations**: benefits attributable to programme window
- **Possible Errors**: benefits double-counted across programmes
- **Extraction Evidence**: benefit reconciliation to source KPI deltas

---

## 6. Data Model

Star schema (Azure SQL → Power BI):

**Fact tables**
- `fact_dev_trajectory` — grain: program × supplier × month (score vs target curve).
- `fact_capa` — grain: one CAPA.
- `fact_esg` — grain: supplier × assessment_date.
- `fact_audit_finding` — grain: one finding.
- `fact_dev_roi` — grain: program × period (benefit vs investment).

**Dimension tables**
- `dim_supplier` (lifnr, name, country, category, kraljic_segment)
- `dim_program` (program_id, lifnr, start_date, target_score, target_date, investment)
- `dim_date` (date, month, quarter, year)
- `dim_theme` (theme code, theme name, category — taxonomy)
- `dim_rootcause` (root_cause_code, description, category)

**Relationships**
- All facts → dim_supplier via lifnr.
- fact_dev_trajectory, fact_dev_roi → dim_program via program_id.
- fact_capa → dim_rootcause; fact_audit_finding → dim_theme.
- All facts → dim_date.

---

## 7. Data Dictionary

### Table: fact_dev_trajectory
- **Description**: Monthly actual score vs. target trajectory for each programme.
- **Granularity**: program × supplier × month.
- **Required Fields**:
  | Field | Type | Description |
  |---|---|---|
  | program_id | varchar | Programme |
  | lifnr | varchar | Supplier |
  | period | date | Month |
  | actual_score | decimal(5,2) | Scorecard composite |
  | target_curve_score | decimal(5,2) | Expected score this month |
  | gap_to_target | decimal(5,2) | actual − target_curve |
  | on_track_flag | bit | 1 if actual ≥ target_curve − tolerance |
- **Primary Key**: program_id + period
- **Relationships**: → dim_program, dim_supplier, dim_date
- **Required Transformations**: compute target curve (see §8); gap; on_track flag
- **Cleaning Rules**: interpolate single missing month; flag >1 missing
- **Validations**: scores in [0,100]
- **Use in Analysis**: trajectory tracking, stalled-supplier detection

### Table: fact_capa
- **Description**: CAPA lifecycle records.
- **Granularity**: one CAPA.
- **Required Fields**: capa_id, lifnr, opened_date, due_date, closed_date, root_cause_code,
  status, on_time_flag, age_days, recurrence_flag, effectiveness_verified_flag
- **Primary Key**: capa_id
- **Relationships**: → dim_supplier, dim_rootcause, dim_date
- **Required Transformations**: on_time_flag, age_days, recurrence_flag (see §8)
- **Validations**: closed_date ≥ opened_date
- **Use in Analysis**: CAPA closure, recurrence, aging

### Table: fact_esg
- **Description**: ESG assessment scores per supplier.
- **Granularity**: supplier × assessment_date.
- **Required Fields**: lifnr, assessment_date, e_score, s_score, g_score, esg_composite,
  evidence_completeness_pct, greenwashing_risk_flag, valid_until, is_current
- **Primary Key**: lifnr + assessment_date
- **Relationships**: → dim_supplier, dim_date
- **Required Transformations**: composite (weighted); is_current (valid_until ≥ today);
  greenwashing flag (see §8)
- **Validations**: scores in [0,100]
- **Use in Analysis**: ESG monitoring, gap detection

### Table: fact_audit_finding
- **Description**: Audit findings with theme and status.
- **Granularity**: one finding.
- **Required Fields**: finding_id, lifnr, audit_date, theme, severity, status, closure_date,
  age_days, capa_ref
- **Primary Key**: finding_id
- **Relationships**: → dim_supplier, dim_theme, dim_date
- **Required Transformations**: normalise theme to taxonomy; age_days
- **Validations**: severity in list; theme mapped
- **Use in Analysis**: finding trends, closure rate

### Table: fact_dev_roi
- **Description**: Programme benefit vs investment by period.
- **Granularity**: program × period.
- **Required Fields**: program_id, lifnr, period, total_benefit, cumulative_investment,
  roi_ratio, payback_flag
- **Primary Key**: program_id + period
- **Relationships**: → dim_program, dim_supplier, dim_date
- **Required Transformations**: total_benefit sum; roi_ratio (see §10)
- **Validations**: benefit ≥ 0; investment > 0
- **Use in Analysis**: development ROI

---

## 8. Transformation Rules

1. **Target curve (improvement trajectory)**:
   `target_curve_score(t) = baseline + (target_score − baseline) * (1 − EXP(−k*t))`,
   where `t` = months since start, `k` calibrated so curve reaches target at target_date.
2. **Gap to target**: `gap_to_target = actual_score − target_curve_score`.
3. **On-track flag**: `on_track_flag = 1 IF gap_to_target >= −tolerance` (tolerance default 3 pts).
4. **CAPA on-time flag**: `on_time_flag = 1 IF closed_date <= due_date`.
5. **CAPA age**: `age_days = DATEDIFF(day, opened_date, COALESCE(closed_date, TODAY()))`.
6. **CAPA recurrence**: `recurrence_flag = 1 IF same (lifnr, root_cause_code) appears in a
   prior closed CAPA within 12 months`.
7. **ESG composite**: `esg_composite = w_E*e_score + w_S*s_score + w_G*g_score`
   (weights *Pending to confirm*; default 1/3 each).
8. **Greenwashing risk flag**: `greenwashing_risk_flag = 1 IF declared_vs_evidence_gap > 20
   OR evidence_completeness_pct < 60`.
9. **ESG currency**: `is_current = 1 IF valid_until >= TODAY()`.
10. **Audit theme normalisation**: map free-text theme → dim_theme taxonomy
    (Labour, Environment, Ethics, Health & Safety, Quality System, Sub-tier).
11. **ROI ratio**: `roi_ratio = cumulative_benefit / cumulative_investment`.
12. **Promotion event**: detect rating band upgrade between consecutive periods.

---

## 9. Business Rules

### Rule: Programme in scope
- **Description**: Only active development programmes are tracked.
- **Logic Condition**: `dev_program.status='ACTIVE' AND baseline_score IS NOT NULL`.
- **Expected Result**: programme appears in trajectory.
- **Example**: programme without baseline excluded until set.
- **Exception**: paused programmes annotated, not dropped.
- **Required Evidence**: in-scope programme list.

### Rule: Stalled supplier flag
- **Description**: Flag suppliers not progressing.
- **Logic Condition**: `gap_to_target < −5 for >= 3 consecutive months`.
- **Expected Result**: supplier flagged STALLED → escalation.
- **Example**: 3 months 6–8 pts below curve → stalled.
- **Exception**: documented external disruption.
- **Required Evidence**: trajectory chart + flag log.

### Rule: CAPA recurrence
- **Description**: Repeated root cause indicates ineffective CAPA.
- **Logic Condition**: same (lifnr, root_cause_code) within 12 months.
- **Expected Result**: recurrence_flag=1; effectiveness review.
- **Example**: same solder defect cause twice in 8 months → recurrence.
- **Exception**: different sub-cause documented.
- **Required Evidence**: CAPA history.

### Rule: ESG assessment validity
- **Description**: Only current ESG assessments score the supplier.
- **Logic Condition**: `is_current = 1`.
- **Expected Result**: expired assessments excluded from current ESG KPI.
- **Example**: assessment valid_until last quarter → not current.
- **Exception**: grace window during reassessment annotated.
- **Required Evidence**: validity check log.

### Rule: Greenwashing risk
- **Description**: Detect declaration-evidence mismatch.
- **Logic Condition**: `gap > 20 OR evidence_completeness < 60 %`.
- **Expected Result**: flag for evidence audit.
- **Example**: declared 90, evidence supports 60 → flag.
- **Exception**: pending evidence upload within grace.
- **Required Evidence**: gap report.

---

## 10. KPIs and Formulas

### KPI: Scorecard Improvement Rate
- **Objective**: progress vs. baseline.
- **Formula (DAX)**: `Improvement % = DIVIDE([Current Score] − [Score 6m Ago],
  [Score 6m Ago]) * 100`
- **Data Source**: fact_dev_trajectory
- **Calculation Level**: supplier / programme
- **Frequency**: monthly
- **Owner**: SDE
- **Interpretation**: positive = improving.
- **Thresholds**: Green ≥+10 %, Yellow 0–10 %, Red <0 %
- **Recommended Action**: Red → escalate / revise plan.
- **Validation vs Source**: scores vs Dept 02 model.

### KPI: On-Track Rate
- **Objective**: share of programmes meeting trajectory.
- **Formula (DAX)**: `On-Track % = DIVIDE(CALCULATE(DISTINCTCOUNT(program_id),
  on_track_flag=1), DISTINCTCOUNT(program_id)) * 100`
- **Thresholds**: Green ≥80 %, Yellow 60–80 %, Red <60 %
- **Recommended Action**: Red → portfolio review.
- **Validation vs Source**: trajectory recompute.

### KPI: CAPA On-Time Closure Rate
- **Objective**: timeliness of corrective actions.
- **Formula (DAX)**: `CAPA OnTime % = DIVIDE(CALCULATE(COUNTROWS(fact_capa),
  on_time_flag=1, status="CLOSED"), CALCULATE(COUNTROWS(fact_capa), status="CLOSED")) * 100`
- **Calculation Level**: supplier / programme
- **Frequency**: daily/monthly
- **Owner**: SDE
- **Interpretation**: higher is better.
- **Thresholds**: Green ≥90 %, Yellow 75–90 %, Red <75 %
- **Recommended Action**: Red → CAPA governance review.
- **Validation vs Source**: CAPA dates vs SAP QM.

### KPI: CAPA Recurrence Rate
- **Objective**: detect ineffective corrective actions.
- **Formula (DAX)**: `Recurrence % = DIVIDE(CALCULATE(COUNTROWS(fact_capa),
  recurrence_flag=1), COUNTROWS(fact_capa)) * 100`
- **Thresholds**: Green <5 %, Yellow 5–15 %, Red >15 %
- **Recommended Action**: Red → root-cause depth review.
- **Validation vs Source**: recurrence logic sample.

### KPI: Audit Finding Closure Rate
- **Objective**: closure of audit findings.
- **Formula (DAX)**: `Closure % = DIVIDE(CALCULATE(COUNTROWS(fact_audit_finding),
  status="CLOSED"), COUNTROWS(fact_audit_finding)) * 100`
- **Thresholds**: Green ≥90 %, Yellow 75–90 %, Red <75 %
- **Recommended Action**: Red → escalate open findings.
- **Validation vs Source**: finding status vs audit report.

### KPI: ESG Composite Score
- **Objective**: sustainability performance.
- **Formula**: `esg_composite = w_E*e_score + w_S*s_score + w_G*g_score`
- **Calculation Level**: supplier
- **Interpretation**: higher is better; trend matters.
- **Thresholds**: Green ≥70, Yellow 50–70, Red <50
- **Recommended Action**: Red → ESG improvement plan; CSDDD due diligence.
- **Validation vs Source**: scores vs ESG DB.

### KPI: Development ROI
- **Objective**: financial return of development.
- **Formula**: `ROI = (ppm_savings_value + ncr_cost_savings + otd_improvement_value)
  / cumulative_investment`
- **Calculation Level**: programme
- **Interpretation**: >1 = positive return.
- **Thresholds**: Green ≥2.0, Yellow 1.0–2.0, Red <1.0
- **Recommended Action**: Red → reassess programme viability.
- **Validation vs Source**: benefit reconciliation to KPI deltas + FI cost.

### KPI: Supplier Promotion Count
- **Objective**: programme outcome (band upgrades).
- **Formula (DAX)**: count of suppliers with rating upgrade in period.
- **Interpretation**: higher = effective development.
- **Thresholds**: tracked vs target (*Pending to confirm*).
- **Recommended Action**: celebrate / replicate playbook.
- **Validation vs Source**: rating change vs scorecard history.

---

## 11. Analytical Logic

- **Segmentations**: Kraljic segment, category, region, programme phase, theme.
- **Development priority score**: `0.4*strategic_importance + 0.4*performance_gap +
  0.2*improvement_potential`.
- **CAPA aging buckets**: 0–30 / 30–60 / 60–90 / >90 days.
- **ESG band classification**: Leader / Good / At-risk / Critical.
- **Priority logic**: focus = highest priority score with worst trajectory gap.
- **Alert logic**:
  - Stalled supplier (3-month gap <−5) → escalation.
  - CAPA overdue → daily aging alert.
  - CAPA recurrence → effectiveness review.
  - ESG composite Red or greenwashing flag → sustainability review.
  - ROI Red at mid-programme → viability review.

---

## 12. Validations and Controls

### Validation: Trajectory continuity
- **Field/Table**: fact_dev_trajectory.actual_score
- **Validation Rule**: monthly series with ≤1 interpolated gap.
- **Validation Method**: gap count per programme.
- **Expected Result**: continuous series.
- **Action if Fails**: flag programme; fix source.
- **Verifiable Evidence**: gap report.

### Validation: CAPA date integrity
- **Field/Table**: fact_capa.closed_date
- **Validation Rule**: closed_date ≥ opened_date; closed CAPAs have closed_date.
- **Validation Method**: logic check.
- **Expected Result**: zero violations.
- **Action if Fails**: correct source record.
- **Verifiable Evidence**: violation count.

### Validation: ESG currency
- **Field/Table**: fact_esg.is_current
- **Validation Rule**: is_current reflects valid_until vs today.
- **Validation Method**: recompute and compare.
- **Expected Result**: correct flag.
- **Action if Fails**: fix flag logic.
- **Verifiable Evidence**: comparison.

### Validation: ROI benefit attribution
- **Field/Table**: fact_dev_roi.total_benefit
- **Validation Rule**: benefits not double-counted across programmes.
- **Validation Method**: cross-programme benefit overlap check.
- **Expected Result**: no overlap.
- **Action if Fails**: re-attribute benefits.
- **Verifiable Evidence**: attribution log.

---

## 13. Required Evidence

- ETL audit log per load.
- CAPA reconciliation to SAP QM12.
- ESG assessment reconciliation to ESG DB.
- Programme investment reconciliation to FI internal orders.
- Manual trajectory + ROI recompute for one programme, signed off by SDE.

---

## 14. Dashboard / Report Design (Power BI)

**Page 1 — Development Portfolio Overview**: on-track rate, promotions, stalled suppliers,
ESG band distribution.
**Page 2 — Trajectory Detail**: supplier selector; actual vs target curve; gap trend.
**Page 3 — CAPA Management**: on-time closure, recurrence, aging buckets; CAPA table.
**Page 4 — ESG Monitoring**: E/S/G radar; composite trend; greenwashing-risk flags;
suppliers lacking current assessment.
**Page 5 — Audit & ROI**: finding theme Pareto; closure rate; programme ROI ranking.
**Slicers**: period, category, region, Kraljic segment, programme phase, theme.
**Drill-through**: supplier → CAPA/finding detail; programme → benefit breakdown.

---

## 15. Use Cases

1. **Stalled supplier escalation**: SDE sees 3-month negative gap, drills to CAPA recurrence
   as cause, revises plan.
2. **CAPA governance**: quality lead finds recurrence >15 %, mandates deeper root-cause.
3. **ESG review**: sustainability sees greenwashing flag, triggers evidence audit.
4. **ROI decision**: programme ROI 0.7 mid-cycle → viability review, reallocate budget.
5. **Audit trend**: recurring "sub-tier labour" theme → systemic supplier-base action.

---

## 16. Recommended Actions

| Result / Condition | Recommended Action | Owner | Timeline |
|---|---|---|---|
| Stalled (3-mo gap <−5) | Revise development plan / escalate | SDE | 2 weeks |
| CAPA on-time <75 % | CAPA governance review | Quality | 1 month |
| Recurrence >15 % | Deepen root-cause analysis | SDE | 1 cycle |
| ESG composite <50 | ESG improvement plan / CSDDD DD | Sustainability | Quarter |
| Greenwashing flag | Evidence audit | Sustainability | 30 days |
| ROI <1.0 mid-programme | Viability review | Procurement | 1 month |

---

## 17. Test Cases

### TC-01 — Target curve value
- **Scenario**: baseline=60, target=80, target in 12 months, t=6.
- **Input Data**: programme params.
- **Expected Result**: target_curve between 60 and 80 (monotonic increasing).
- **Result to Avoid**: curve above target before target_date.
- **Required Validation**: curve formula test.
- **Evidence**: curve value.

### TC-02 — CAPA on-time
- **Scenario**: due=2026-06-10, closed=2026-06-09.
- **Input Data**: CAPA row.
- **Expected Result**: on_time_flag=1.
- **Result to Avoid**: flag=0.
- **Required Validation**: date comparison.
- **Evidence**: flag.

### TC-03 — CAPA recurrence
- **Scenario**: same supplier+root cause 8 months apart.
- **Input Data**: two CAPAs.
- **Expected Result**: recurrence_flag=1 on second.
- **Result to Avoid**: flag=0.
- **Required Validation**: recurrence lookback test.
- **Evidence**: flag.

### TC-04 — ESG currency
- **Scenario**: valid_until in the past.
- **Input Data**: ESG row.
- **Expected Result**: is_current=0; excluded from current KPI.
- **Result to Avoid**: counted as current.
- **Required Validation**: validity test.
- **Evidence**: flag.

### TC-05 — ROI ratio
- **Scenario**: benefit=€300k, investment=€150k.
- **Input Data**: ROI row.
- **Expected Result**: roi_ratio=2.0; Green.
- **Result to Avoid**: inverted (0.5).
- **Required Validation**: ratio test.
- **Evidence**: ratio.

### TC-06 — Greenwashing flag
- **Scenario**: declared 90, evidence supports 60 (gap=30).
- **Input Data**: ESG row.
- **Expected Result**: greenwashing_risk_flag=1.
- **Result to Avoid**: flag=0.
- **Required Validation**: gap threshold test.
- **Evidence**: flag.

---

## 18. Risks and Mitigations

| Risk | Probability | Impact | Preventive Control | Corrective Control |
|---|---|---|---|---|
| Missing scorecard months | Medium | High | Interpolation + gap flag | Backfill source |
| CAPA closed w/o effectiveness | Medium | High | Effectiveness flag required | Reopen CAPA |
| Expired ESG treated current | Medium | High | is_current validity logic | Reassessment trigger |
| Benefit double-counting | Medium | Medium | Attribution check | Re-attribute |
| Free-text audit themes | High | Medium | Taxonomy normalisation | Manual remap |
| Investment under-captured | Medium | Medium | FI internal-order link | Reconcile cost |

---

## 19. Implementation Checklist

1. Confirm ESG weighting and programme master with Sustainability/SDE.
2. Build Azure SQL staging for Sources 1–6.
3. Extract scorecard history, CAPA, ESG, programme, audit, benefit data.
4. Build fact/dim model per §6.
5. Implement transformations §8 (target curve, CAPA flags, ESG composite, ROI).
6. Build trajectory + stalled-supplier logic.
7. Build CAPA aging/recurrence logic.
8. Build ESG currency + greenwashing logic.
9. Build ROI computation with attribution control.
10. Normalise audit theme taxonomy.
11. Build Power BI model + relationships.
12. Author KPI measures.
13. Build 5 dashboard pages.
14. Configure RLS (category/region).
15. Set daily (CAPA/audit) + quarterly (ESG/ROI) refresh.
16. Implement validations §12.
17. Build reconciliation pack (QM, ESG DB, FI).
18. UAT with SDE & Sustainability.
19. Go-live + hypercare.

---

## 20. Validation Checklist

1. Trajectory continuity verified.
2. CAPA reconciled to SAP QM12.
3. CAPA date integrity enforced.
4. Recurrence logic validated.
5. ESG reconciled to ESG DB.
6. ESG currency flag correct.
7. Greenwashing threshold validated.
8. ROI benefit attribution non-overlapping.
9. Investment reconciled to FI.
10. RLS verified.
11. Refresh schedules confirmed.
12. Manual programme recompute signed off.

---

## 21. Pending Information to Confirm

- ESG weighting (w_E, w_S, w_G). — *Pending to confirm*
- Greenwashing gap/evidence thresholds. — *Pending to confirm*
- Improvement-curve rate constant k / milestone definition. — *Pending to confirm*
- Benefit attribution methodology (avoid double count). — *Pending to confirm*
- Audit theme taxonomy. — *Pending to confirm*
- Promotion-count targets per period. — *Pending to confirm*
- RLS security groups. — *Pending to confirm*

---

## 22. Implementation Roadmap

| Week | Activity | Deliverable | Owner | Status |
|---|---|---|---|---|
| 1–2 | Requirements + ESG weighting | Signed scope | BI Lead | Pending |
| 3–5 | Staging + extraction | Loaded staging | Data Eng | Pending |
| 6–8 | Fact/dim + transforms | Model v1 | Data Eng | Pending |
| 9–10 | Trajectory + CAPA + ESG | Computed facts | Analytics | Pending |
| 11–12 | ROI + audit taxonomy | Computed facts | Analytics | Pending |
| 13–14 | Power BI + KPIs | Dashboard draft | BI Dev | Pending |
| 15–16 | Validations + reconciliation | Recon pack | Data Quality | Pending |
| 17 | UAT | Sign-off | SDE / Sustainability | Pending |
| 18 | Go-live + hypercare | Production report | BI Lead | Pending |
