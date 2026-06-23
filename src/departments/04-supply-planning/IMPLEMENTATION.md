# Supply Planning & MRP Analytics — Implementation Specification

> Analytical implementation document for a data / BI / automation team.
> Scope: MRP Exceptions, Production Plan Attainment, Capacity Utilisation,
> DDMRP Buffer Status, Bullwhip Effect.
> Context: €50B multinational, 40 countries, SAP S/4HANA PP/MM + SAP IBP for Supply,
> Apache Superset, PostgreSQL, Python.

---

## 1. Executive Summary

This document specifies the analytical implementation to make the supply planning
process observable, measurable, and continuously improvable. It defines the data,
transformations, KPIs, validations, and dashboards required to triage MRP exception
messages, measure production plan attainment and capacity utilisation, monitor DDMRP
buffer health, and quantify the bullwhip effect across supply links.

The deliverable is a governed Apache Superset solution on PostgreSQL, refreshed daily after
the MRP run, used by Supply Planners, Production Schedulers, and Plant Managers.
Every metric reconciles to SAP PP/MM and IBP source data.

---

## 2. Analysis Objective

- Prioritise and trend MRP exception messages so planners focus on the highest-impact ones.
- Measure production plan attainment (planned vs. actual) by plant, line, and period.
- Quantify capacity utilisation and identify bottleneck work centres.
- Monitor DDMRP buffer status (red/yellow/green penetration) at decoupling points.
- Measure the bullwhip ratio per SKU-supplier link to target demand amplification.
- Provide an auditable basis for planning performance and continuous improvement.

---

## 3. Scope

**In scope**: all MRP-planned materials (make + buy) at plant × material × period
granularity; production orders; work-centre capacity; DDMRP-buffered items; orders
vs. demand for bullwhip; trailing 24 months.

**Out of scope**: KANBAN/reorder-point materials without MRP exceptions (separate view);
phantom assemblies (analysed through parent).

---

## 4. Business Questions

- Which MRP exception messages are open, and which carry the highest value/urgency?
- What is production plan attainment by plant, line, and week?
- Which work centres are bottlenecks (utilisation >90 %) over the planning horizon?
- Which DDMRP buffers are penetrating the red zone, and how often?
- Which SKU-supplier links have the highest bullwhip ratio?
- What is the trend of reschedule-in / reschedule-out messages?
- How much planned production was missed and why (capacity, material, quality)?
- Which materials have lead times consistently breached vs. plan?
- Which buffers are oversized (no red penetration for N weeks)?
- What is the exception message volume per planner (workload balancing)?

---

## 5. Data Sources

### Source 1 — MRP Exception Messages
- **Source Name**: MRP exception messages
- **Origin System**: SAP S/4HANA (PP/MM)
- **Report/Table/Query**: MDKP/MDTB (MRP list) or MD06 export; exception codes
- **Data Owner**: Supply Planning
- **Update Frequency**: Daily (after MRP run)
- **Required Fields**: `MATNR, WERKS, exception_code, exception_text, mrp_element,
  element_date, reschedule_date, quantity, planner_code, run_date`
- **Critical Fields**: `exception_code`, `quantity`, `element_date`, `planner_code`
- **Primary/Logical Key**: MATNR + WERKS + mrp_element + run_date
- **Required Validations**: exception_code in known catalog; quantity numeric
- **Possible Errors**: stale list from failed MRP run; duplicate elements
- **Extraction Evidence**: exception count per plant vs SAP MD06 sample

### Source 2 — Production Orders (Plan vs Actual)
- **Source Name**: Production orders
- **Origin System**: SAP S/4HANA (PP)
- **Report/Table/Query**: AFKO (order header) + AFPO (item) + AFRU (confirmations)
- **Data Owner**: Production Control
- **Update Frequency**: Daily
- **Required Fields**: `AUFNR, MATNR, WERKS, planned_qty, confirmed_qty, planned_start,
  planned_finish, actual_finish, work_center, status`
- **Critical Fields**: `planned_qty`, `confirmed_qty`, `planned_finish`, `actual_finish`
- **Primary/Logical Key**: AUFNR (+ item)
- **Required Validations**: confirmed_qty ≤ planned_qty + tolerance; dates consistent
- **Possible Errors**: open orders counted as missed; backflush timing lag
- **Extraction Evidence**: order count and qty per plant vs SAP COOIS

### Source 3 — Work Centre Capacity
- **Source Name**: Work centre capacity & load
- **Origin System**: SAP S/4HANA (PP) / IBP
- **Report/Table/Query**: CRHD (work centre) + capacity (KAKO) + load from CM01
- **Data Owner**: Capacity Planning
- **Update Frequency**: Weekly
- **Required Fields**: `work_center, WERKS, available_capacity_hrs, required_load_hrs,
  efficiency, period, shifts`
- **Critical Fields**: `available_capacity_hrs`, `required_load_hrs`
- **Primary/Logical Key**: work_center + WERKS + period
- **Required Validations**: capacity > 0; load ≥ 0
- **Possible Errors**: missing shift calendar; efficiency not applied
- **Extraction Evidence**: capacity vs SAP CR03; load vs CM01

### Source 4 — DDMRP Buffer Status
- **Source Name**: DDMRP buffer levels & on-hand
- **Origin System**: SAP IBP (or custom DDMRP extension) + S/4HANA stock
- **Report/Table/Query**: buffer parameters (TOR/TOY/TOP) + daily on-hand + net flow position
- **Data Owner**: Supply Planning (DDMRP)
- **Update Frequency**: Daily
- **Required Fields**: `MATNR, WERKS, top_of_red, top_of_yellow, top_of_green, on_hand,
  net_flow_position, ADU, date`
- **Critical Fields**: `net_flow_position`, buffer zone tops, ADU
- **Primary/Logical Key**: MATNR + WERKS + date
- **Required Validations**: TOR ≤ TOY ≤ TOP; ADU ≥ 0
- **Possible Errors**: stale ADU; buffer not recalculated
- **Extraction Evidence**: buffer count vs DDMRP config

### Source 5 — Orders & Demand (Bullwhip)
- **Source Name**: PO order quantities vs end demand
- **Origin System**: SAP S/4HANA (MM purchase orders) + actual demand (from Dept 03)
- **Report/Table/Query**: EKPO/EKET (orders placed) + fact_actuals (demand)
- **Data Owner**: Supply Planning / Procurement
- **Update Frequency**: Monthly
- **Required Fields**: `MATNR, LIFNR, period, order_qty, demand_qty`
- **Critical Fields**: `order_qty`, `demand_qty`
- **Primary/Logical Key**: MATNR + LIFNR + period
- **Required Validations**: both series same UOM; aligned periods
- **Possible Errors**: order qty includes safety build masking demand signal
- **Extraction Evidence**: order/demand series length per link

---

## 6. Data Model

Star schema (PostgreSQL → Apache Superset):

**Fact tables**
- `fact_mrp_exception` — grain: material × plant × mrp_element × run_date.
- `fact_production` — grain: production order (+item).
- `fact_capacity` — grain: work_center × plant × period.
- `fact_ddmrp` — grain: material × plant × date.
- `fact_bullwhip` — grain: material × supplier × period.

**Dimension tables**
- `dim_material` (MATNR, family, type make/buy, planner)
- `dim_plant` (WERKS, name, region)
- `dim_workcenter` (work_center, description, capacity category)
- `dim_date` (date, week, month, period)
- `dim_planner` (planner_code, name)
- `dim_exception` (exception_code, description, severity, action_type)

**Relationships**
- fact_mrp_exception → dim_material, dim_plant, dim_date, dim_planner, dim_exception.
- fact_production → dim_material, dim_plant, dim_workcenter, dim_date.
- fact_capacity → dim_workcenter, dim_plant, dim_date.
- fact_ddmrp → dim_material, dim_plant, dim_date.
- fact_bullwhip → dim_material, dim_date.

---

## 7. Data Dictionary

### Table: fact_mrp_exception
- **Description**: Open MRP exception messages with value and priority.
- **Granularity**: material × plant × mrp_element × run_date.
- **Required Fields**:
  | Field | Type | Description |
  |---|---|---|
  | matnr | varchar | Material |
  | werks | varchar | Plant |
  | exception_code | varchar | SAP exception code |
  | mrp_element | varchar | Order/PR/planned order id |
  | element_date | date | Element due date |
  | reschedule_date | date | Proposed new date |
  | quantity | decimal(18,3) | Element qty |
  | unit_cost | decimal(18,2) | Std cost |
  | exposure_value | decimal(18,2) | quantity × unit_cost |
  | planner_code | varchar | Owning planner |
  | run_date | date | MRP run date |
- **Primary Key**: matnr+werks+mrp_element+run_date
- **Relationships**: → dim_material, dim_plant, dim_date, dim_planner, dim_exception
- **Required Transformations**: join exception catalog → severity; compute exposure_value
- **Cleaning Rules**: dedupe elements; drop closed exceptions
- **Validations**: exception_code valid; quantity numeric
- **Use in Analysis**: exception rate, prioritisation, planner workload

### Table: fact_production
- **Description**: Production orders with plan vs actual.
- **Granularity**: production order item.
- **Required Fields**: aufnr, matnr, werks, work_center, planned_qty, confirmed_qty,
  planned_finish, actual_finish, on_time_flag, attainment_qty, status
- **Primary Key**: aufnr + item
- **Relationships**: → dim_material, dim_plant, dim_workcenter, dim_date
- **Required Transformations**: on_time_flag = actual_finish ≤ planned_finish;
  attainment_qty = MIN(confirmed_qty, planned_qty)
- **Validations**: confirmed_qty ≥ 0; dates consistent
- **Use in Analysis**: plan attainment, schedule adherence

### Table: fact_capacity
- **Description**: Capacity vs load per work centre/period.
- **Granularity**: work_center × plant × period.
- **Required Fields**: work_center, werks, period, available_hrs, required_hrs,
  utilisation_pct, overload_flag
- **Primary Key**: work_center+werks+period
- **Relationships**: → dim_workcenter, dim_plant, dim_date
- **Required Transformations**: utilisation = required/available*100; overload if >100
- **Validations**: available_hrs > 0
- **Use in Analysis**: capacity utilisation, bottleneck detection

### Table: fact_ddmrp
- **Description**: Daily DDMRP buffer position and zone.
- **Granularity**: material × plant × date.
- **Required Fields**: matnr, werks, date, top_of_red, top_of_yellow, top_of_green,
  on_hand, net_flow_position, zone (RED/YELLOW/GREEN/OVER), adu
- **Primary Key**: matnr+werks+date
- **Relationships**: → dim_material, dim_plant, dim_date
- **Required Transformations**: classify zone from net_flow_position vs tops (see §8)
- **Validations**: TOR ≤ TOY ≤ TOP
- **Use in Analysis**: red-zone penetration, buffer sizing

### Table: fact_bullwhip
- **Description**: Order vs demand variance per supply link.
- **Granularity**: material × supplier × period.
- **Required Fields**: matnr, lifnr, period, order_qty, demand_qty
- **Primary Key**: matnr+lifnr+period
- **Relationships**: → dim_material, dim_date
- **Required Transformations**: compute rolling variance ratio (see §10)
- **Validations**: same UOM; aligned periods
- **Use in Analysis**: bullwhip ratio

---

## 8. Transformation Rules

1. **Exposure value**: `exposure_value = quantity * unit_cost` (std cost from MBEW).
2. **Exception severity**: join `exception_code` → dim_exception.severity
   (Critical / High / Medium / Low) and action_type (reschedule-in/out/open/cancel).
3. **On-time production flag**: `on_time_flag = 1 IF actual_finish <= planned_finish`.
4. **Attainment qty**: `attainment_qty = MIN(confirmed_qty, planned_qty)` (no over-credit).
5. **Capacity utilisation**: `utilisation_pct = required_hrs / available_hrs * 100`,
   where `available_hrs = shifts * hrs_per_shift * (1-downtime) * efficiency`.
6. **DDMRP zone classification**:
   ```
   IF net_flow_position <= top_of_red THEN 'RED'
   ELIF net_flow_position <= top_of_yellow THEN 'YELLOW'
   ELIF net_flow_position <= top_of_green THEN 'GREEN'
   ELSE 'OVER'
   ```
7. **Bullwhip variance**: per link compute `VAR(order_qty)` and `VAR(demand_qty)` over a
   rolling 12-period window.
8. **Reschedule horizon bucket**: classify reschedule delta into buckets (≤3d auto, 4–14d,
   >14d) for triage.
9. **Planner workload**: count open exceptions per planner_code per run_date.
10. **ADU refresh check**: flag DDMRP rows where ADU older than 7 days.

---

## 9. Business Rules

### Rule: Exception in scope
- **Description**: Only open, MRP-relevant exceptions are reported.
- **Logic Condition**: `status='OPEN' AND exception_code IN dim_exception AND
  material.mrp_type='PD'`.
- **Expected Result**: exception included in triage.
- **Example**: KANBAN material exception excluded.
- **Exception**: critical safety-stock breach always included.
- **Required Evidence**: in-scope exception count.

### Rule: Plan attainment counting
- **Description**: Attainment credited only for confirmed-on-time output.
- **Logic Condition**: `attainment = SUM(MIN(confirmed_qty, planned_qty) WHERE
  actual_finish <= period_end) / SUM(planned_qty)`.
- **Expected Result**: attainment % per plant/period.
- **Example**: planned 100, confirmed 90 on time → 90 % for that order.
- **Exception**: rework orders excluded from denominator.
- **Required Evidence**: order-level attainment table.

### Rule: Bottleneck flag
- **Description**: Flag chronic capacity overloads.
- **Logic Condition**: `utilisation_pct > 90 for >= 3 consecutive periods`.
- **Expected Result**: work centre flagged bottleneck.
- **Example**: WC 4711 at 96/93/91 % three weeks → bottleneck.
- **Exception**: planned ramp-up periods annotated.
- **Required Evidence**: utilisation trend per WC.

### Rule: Red-zone penetration alert
- **Description**: Buffer breaching red signals supply urgency.
- **Logic Condition**: `zone='RED'` on any day → generate supply order alert.
- **Expected Result**: alert + penetration count increment.
- **Example**: net flow below TOR → RED.
- **Exception**: planned phase-out buffers ignored.
- **Required Evidence**: daily zone log.

### Rule: Buffer oversizing
- **Description**: Detect oversized buffers.
- **Logic Condition**: `no RED penetration for >= 8 weeks AND min(zone)='GREEN/OVER'`.
- **Expected Result**: candidate for buffer reduction (reduce LTF 20 %).
- **Example**: buffer always in green 10 weeks → reduce.
- **Exception**: seasonal pre-build periods.
- **Required Evidence**: 8-week zone history.

---

## 10. KPIs and Formulas

### KPI: MRP Exception Rate
- **Objective**: share of planned items with open exceptions.
- **Formula (SQL)**: `SELECT COUNT(DISTINCT matnr) / NULLIF((SELECT COUNT(*) FROM dim_material),0) * 100 AS exception_rate_pct FROM fact_mrp_exception`
- **Data Source**: fact_mrp_exception
- **Calculation Level**: plant / planner / period
- **Frequency**: daily
- **Owner**: Supply Planner
- **Interpretation**: lower is better; spikes = planning instability.
- **Thresholds**: Green <5 %, Yellow 5–10 %, Red >10 %
- **Recommended Action**: Red → root-cause top exception codes.
- **Validation vs Source**: distinct material count vs SAP MD06.

### KPI: Exception Exposure Value
- **Objective**: prioritise exceptions by financial impact.
- **Formula (SQL)**: `SELECT SUM(exposure_value) AS exposure FROM fact_mrp_exception`
- **Calculation Level**: exception / planner / plant
- **Interpretation**: focus highest value first.
- **Thresholds**: ranked (top decile = priority).
- **Recommended Action**: action top-value exceptions same day.
- **Validation vs Source**: qty×cost sample recompute.

### KPI: Production Plan Attainment
- **Objective**: how much of the plan was actually produced on time.
- **Formula (SQL)**: `SELECT SUM(attainment_qty) / NULLIF(SUM(planned_qty),0) * 100 AS attainment_pct FROM fact_production`
- **Calculation Level**: plant / line / week
- **Frequency**: daily/weekly
- **Owner**: Production Control
- **Interpretation**: higher is better.
- **Thresholds**: Green ≥92 %, Yellow 85–92 %, Red <85 %
- **Recommended Action**: Red → loss-reason analysis.
- **Validation vs Source**: confirmed qty vs SAP COOIS.

### KPI: Schedule Adherence
- **Objective**: orders finished on time.
- **Formula (SQL)**: `SELECT COUNT(*) FILTER (WHERE on_time_flag = 1) / NULLIF(COUNT(*),0) * 100 AS schedule_adherence_pct FROM fact_production`
- **Thresholds**: Green ≥92 %, Yellow 85–92 %, Red <85 %
- **Recommended Action**: Red → scheduling/capacity review.
- **Validation vs Source**: date comparison sample.

### KPI: Capacity Utilisation
- **Objective**: load vs available capacity.
- **Formula (SQL)**: `SELECT SUM(required_hrs) / NULLIF(SUM(available_hrs),0) * 100 AS utilisation_pct FROM fact_capacity`
- **Calculation Level**: work centre / plant / period
- **Interpretation**: >100 % = overload; <60 % = underutilised.
- **Thresholds**: Green 70–90 %, Yellow 90–100 %, Red >100 % (or <60 %)
- **Recommended Action**: Red overload → overtime/outsource; underload → consolidate.
- **Validation vs Source**: load vs SAP CM01.

### KPI: DDMRP Red-Zone Penetration Rate
- **Objective**: buffer health at decoupling points.
- **Formula (SQL)**: `SELECT COUNT(*) FILTER (WHERE zone = 'RED') / NULLIF(COUNT(*),0) * 100 AS red_penetration_pct FROM fact_ddmrp`
- **Calculation Level**: material / plant / month
- **Thresholds**: Green <10 %, Yellow 10–20 %, Red >20 %
- **Recommended Action**: Red → increase buffer / expedite; investigate ADU.
- **Validation vs Source**: zone classification sample vs net flow.

### KPI: Bullwhip Ratio
- **Objective**: demand amplification per supply link.
- **Formula**: `Bullwhip = VAR(order_qty) / VAR(demand_qty)` over rolling 12 periods.
  (Python / SQL `VAR_POP`.)
- **Calculation Level**: material × supplier
- **Interpretation**: ≈1 ideal; >1 amplification.
- **Thresholds**: Green ≤1.3, Yellow 1.3–2.0, Red >2.0
- **Recommended Action**: Red → order smoothing / VMI / DDMRP.
- **Validation vs Source**: variance recompute on sample link.

### KPI: Production Variance
- **Objective**: actual vs planned production gap.
- **Formula**: `Variance % = (SUM(confirmed_qty) − SUM(planned_qty)) / SUM(planned_qty) * 100`
- **Thresholds**: Green |var|<5 %, Yellow 5–10 %, Red >10 %
- **Recommended Action**: Red → capacity/material root cause.
- **Validation vs Source**: qty sums vs SAP.

### KPI-Supply-08: Order Entry Accuracy Rate (Supply Signal)

In supply planning, order entry accuracy measures the integrity of demand signals entering the planning system — specifically, the percentage of customer sales orders and replenishment orders that are correctly transmitted from the Order Management module (SAP SD) to the planning engine (SAP IBP / MRP) without requiring manual planner correction. Erroneous order entry corrupts the demand signal, inflates safety stock calculations, and triggers unnecessary planned orders.

```
Order Entry Accuracy Rate — Supply Signal (%) =
    Demand signals received by planning engine without correction
    ─────────────────────────────────────────────────────────── × 100
                 Total demand signals received
```

**SQL (PostgreSQL):**

```sql
-- Order entry accuracy as seen by the supply planning layer
SELECT
    DATE_TRUNC('week', d.signal_date)                    AS week,
    d.signal_type,                                        -- SALES_ORDER | REPLENISHMENT | FORECAST_ADJ
    d.plant,
    COUNT(*)                                             AS total_signals,
    COUNT(*) FILTER (WHERE d.planner_correction_flag = FALSE) AS clean_signals,
    ROUND(
        COUNT(*) FILTER (WHERE d.planner_correction_flag = FALSE)::numeric
        / NULLIF(COUNT(*), 0) * 100,
    2)                                                   AS signal_accuracy_pct,
    SUM(d.qty_corrected_abs)                             AS total_qty_corrected_units
FROM fact_demand_signal d
WHERE d.signal_date >= CURRENT_DATE - INTERVAL '13 weeks'
GROUP BY 1, 2, 3
ORDER BY 1 DESC, signal_accuracy_pct ASC;
```

- **Target**: ≥ 99% for EDI-sourced signals; ≥ 97% for manually entered orders
- **Frequency**: Weekly; included in Supply Review gate scorecard
- **Owner**: Supply Planning / Demand Management
- **Linkage**: Low order entry accuracy → increase safety stock buffer temporarily (Method 4 safety stock with inflated σ_D) until root cause resolved

---

## 11. Analytical Logic

- **Segmentations**: plant, work centre, planner, material family, make/buy, exception code.
- **Exception triage classification**: by severity × exposure value (4-box priority).
- **DDMRP zone classification**: RED/YELLOW/GREEN/OVER.
- **Priority logic**: exception priority = `severity_weight * exposure_value`.
- **Alert logic**:
  - Exception rate Red per plant → planning review.
  - Any RED buffer → supply order alert (daily).
  - Bottleneck (3-week >90 %) → capacity escalation.
  - Bullwhip Red → ordering-policy review ticket.
  - Buffer oversize (8-week green) → reduction candidate.

---

## 12. Validations and Controls

### Validation: MRP run freshness
- **Field/Table**: fact_mrp_exception.run_date
- **Validation Rule**: run_date = latest scheduled MRP date.
- **Validation Method**: compare max(run_date) to MRP calendar.
- **Expected Result**: current.
- **Action if Fails**: block report; alert that MRP did not run.
- **Verifiable Evidence**: run_date vs calendar.

### Validation: Buffer zone ordering
- **Field/Table**: fact_ddmrp (TOR/TOY/TOP)
- **Validation Rule**: TOR ≤ TOY ≤ TOP.
- **Validation Method**: range check.
- **Expected Result**: zero violations.
- **Action if Fails**: exclude row; fix buffer config.
- **Verifiable Evidence**: violation count = 0.

### Validation: Attainment bounds
- **Field/Table**: fact_production.attainment_qty
- **Validation Rule**: 0 ≤ attainment_qty ≤ planned_qty.
- **Validation Method**: range check.
- **Expected Result**: no over-credit.
- **Action if Fails**: fix MIN logic.
- **Verifiable Evidence**: query result.

### Validation: Capacity reconciliation
- **Field/Table**: fact_capacity.required_hrs
- **Validation Rule**: load = SAP CM01 within ±2 %.
- **Validation Method**: compare to SAP.
- **Expected Result**: within tolerance.
- **Action if Fails**: investigate routing/efficiency.
- **Verifiable Evidence**: reconciliation report.

---

## 13. Required Evidence

- MRP run log (run_date, exception count) per day.
- Production attainment reconciliation to SAP COOIS.
- Capacity load reconciliation to SAP CM01.
- DDMRP zone classification sample verification.
- Bullwhip variance recompute for a sample link.

---

## 14. Dashboard / Report Design (Apache Superset)

**Page 1 — Planning Health Overview**: exception rate, attainment, top bottlenecks,
red-buffer count.
**Page 2 — MRP Exception Triage**: 4-box (severity × exposure); exception table with
drill-through to element detail; planner workload.
**Page 3 — Production Attainment**: attainment & adherence by plant/line/week; loss reasons.
**Page 4 — Capacity**: utilisation heat map by work centre/period; bottleneck trend.
**Page 5 — DDMRP & Bullwhip**: buffer status board; red-penetration trend; bullwhip ranking.
**Slicers**: period, plant, planner, work centre, material family, exception code.
**Drill-through**: exception → MRP element; work centre → order load; buffer → daily history.

---

## 15. Use Cases

1. **Daily exception triage**: planner opens 4-box, actions top-value/critical exceptions,
   reschedules within fence.
2. **Attainment review**: plant manager finds Red attainment, drills to loss reasons,
   sees material shortage root cause.
3. **Bottleneck resolution**: scheduler sees WC at 96 % three weeks, approves overtime.
4. **Buffer tuning**: planner sees red penetration >20 %, increases buffer LTF.
5. **Bullwhip remediation**: link with ratio 3.1 → moves to weekly smoothing / VMI.

---

## 16. Recommended Actions

| Result / Condition | Recommended Action | Owner | Timeline |
|---|---|---|---|
| Exception rate >10 % | Root-cause top codes | Supply Planner | 1 week |
| Attainment <85 % | Loss-reason analysis | Production Control | 1 week |
| WC utilisation >100 % | Overtime / outsource | Capacity Planner | Same cycle |
| Red penetration >20 % | Increase buffer / expedite | DDMRP Planner | 2 weeks |
| Bullwhip >2.0 | Order smoothing / VMI | Supply Planner | 1 month |
| Buffer oversize 8 wks | Reduce buffer LTF | DDMRP Planner | Next review |

---

## 17. Test Cases

### TC-01 — Exception exposure ranking
- **Scenario**: two exceptions, qty 10×€500 vs 100×€10.
- **Input Data**: two rows.
- **Expected Result**: first exposure=€5,000 ranks above €1,000.
- **Result to Avoid**: ranking by qty (100 first).
- **Required Validation**: exposure compute test.
- **Evidence**: exposure values.

### TC-02 — Attainment no over-credit
- **Scenario**: planned 100, confirmed 120.
- **Input Data**: order row.
- **Expected Result**: attainment_qty=100 (capped).
- **Result to Avoid**: 120 (>100 %).
- **Required Validation**: MIN test.
- **Evidence**: attainment_qty.

### TC-03 — DDMRP zone boundary
- **Scenario**: net_flow=top_of_red exactly.
- **Input Data**: ddmrp row.
- **Expected Result**: zone=RED (≤ rule).
- **Result to Avoid**: YELLOW.
- **Required Validation**: boundary test.
- **Evidence**: zone value.

### TC-04 — Capacity overload flag
- **Scenario**: required 110 hrs, available 100 hrs.
- **Input Data**: capacity row.
- **Expected Result**: utilisation=110 %; overload_flag=1.
- **Result to Avoid**: flag=0.
- **Required Validation**: utilisation test.
- **Evidence**: utilisation, flag.

### TC-05 — Bullwhip ratio
- **Scenario**: VAR(orders)=400, VAR(demand)=100.
- **Input Data**: two series.
- **Expected Result**: ratio=4.0; Red.
- **Result to Avoid**: ratio inverted (0.25).
- **Required Validation**: variance ratio test.
- **Evidence**: ratio value.

### TC-06 — MRP run freshness
- **Scenario**: MRP failed, list from yesterday.
- **Input Data**: max(run_date)=yesterday.
- **Expected Result**: report blocked + alert.
- **Result to Avoid**: stale data shown as current.
- **Required Validation**: freshness check.
- **Evidence**: alert log.

---

## 18. Risks and Mitigations

| Risk | Probability | Impact | Preventive Control | Corrective Control |
|---|---|---|---|---|
| Stale MRP run | Medium | High | Run-date freshness gate | Block report + alert |
| Open orders counted as missed | Medium | Medium | Status filter | Restate attainment |
| Capacity routing inaccurate | Medium | High | Routing audit | Reconcile to CM01 |
| Stale ADU in DDMRP | Medium | Medium | ADU age flag | Recalculate buffers |
| Order qty masks demand (bullwhip) | Medium | Medium | Use net demand series | Adjust series |
| Duplicate exception elements | Low | Medium | Dedupe key | Re-extract |

---

## 19. Implementation Checklist

1. Confirm exception code catalog + severity mapping with Planning.
2. Build PostgreSQL staging for Sources 1–5.
3. Extract MRP list, production orders, capacity, DDMRP, orders/demand.
4. Build fact/dim model per §6.
5. Implement transformations §8 (exposure, zone, utilisation, variance).
6. Build exception triage + production attainment computes.
7. Build capacity utilisation + bottleneck logic.
8. Build DDMRP zone + penetration logic.
9. Build bullwhip variance computation.
10. Build Apache Superset model + relationships.
11. Author KPI measures.
12. Build 5 dashboard pages.
13. Configure Apache Superset row-level security (RLS) (plant/planner).
14. Set daily refresh after MRP run; add freshness gate.
15. Implement validations §12.
16. Build reconciliation pack to SAP.
17. UAT with planners & plant managers.
18. Go-live + hypercare.

---

## 20. Validation Checklist

1. MRP run freshness gate verified.
2. Exception count vs SAP MD06 sample.
3. Attainment vs SAP COOIS sample.
4. Capacity load vs SAP CM01 ±2 %.
5. DDMRP zone boundaries correct.
6. Attainment bounded 0..planned.
7. Bullwhip ratio recomputed on sample.
8. Buffer ordering TOR≤TOY≤TOP enforced.
9. Apache Superset row-level security (RLS) verified.
10. Refresh schedule confirmed.

---

## 21. Pending Information to Confirm

- Exception code → severity/action mapping table. — *Pending to confirm*
- Standard cost source for exposure value. — *Pending to confirm*
- Plant shift calendars and efficiency factors. — *Pending to confirm*
- DDMRP buffer parameter source (IBP vs custom). — *Pending to confirm*
- Net-demand series definition for bullwhip. — *Pending to confirm*
- MRP run schedule/calendar. — *Pending to confirm*
- Apache Superset row-level security (RLS) groups (plant/planner). — *Pending to confirm*

---

## 22. Implementation Roadmap

| Week | Activity | Deliverable | Owner | Status |
|---|---|---|---|---|
| 1–2 | Requirements + code catalog | Signed scope | BI Lead | Pending |
| 3–5 | Staging + extraction | Loaded staging | Data Eng | Pending |
| 6–8 | Fact/dim + transforms | Model v1 | Data Eng | Pending |
| 9–10 | Exception/attainment/capacity | Computed facts | Analytics | Pending |
| 11–12 | DDMRP + bullwhip | Computed facts | Analytics | Pending |
| 13–14 | Apache Superset + KPIs | Dashboard draft | BI Dev | Pending |
| 15–16 | Validations + reconciliation | Recon pack | Data Quality | Pending |
| 17 | UAT | Sign-off | Planning | Pending |
| 18 | Go-live + hypercare | Production report | BI Lead | Pending |
