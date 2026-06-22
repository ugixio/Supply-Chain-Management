# Demand Planning Analytics — Implementation Specification

> Analytical implementation document for a data / BI / automation team.
> Scope: Demand Variation Analysis, Forecast Accuracy (MAPE/MAE/RMSE/Bias),
> Statistical Baseline vs. Actual, Safety Stock Analysis, ABC/XYZ Segmentation.
> Context: €50B multinational, 40 countries, SAP S/4HANA + SAP IBP for Demand,
> Power BI, Azure SQL, Python. Data updated daily; planning monthly + weekly sensing.

---

## 1. Executive Summary

This document specifies the analytical implementation for measuring and improving
demand plan quality across the global portfolio. It defines the data, transformations,
KPIs, validations, and dashboards required to quantify forecast accuracy and bias,
characterise demand variability, validate safety-stock adequacy, and segment SKUs
(ABC/XYZ) to drive the right planning policy.

The deliverable is a governed Power BI solution on Azure SQL, refreshed daily, used
by Demand Planners, Supply Planners, and S&OP leadership. Every accuracy figure
reconciles to SAP IBP key figures and SAP S/4HANA actual sales.

---

## 2. Analysis Objective

- Measure forecast accuracy (MAPE, MAE, RMSE) and bias at multiple levels and lags.
- Characterise demand variability (CV) and classify SKUs into ABC/XYZ.
- Compare statistical baseline vs. consensus forecast vs. actual to quantify the
  value (or harm) of manual overrides.
- Validate safety-stock coverage against demand variability and service targets.
- Provide an auditable, drillable basis for planner accountability and continuous
  improvement of the forecasting process.

---

## 3. Scope

**In scope**: all forecasted finished goods and saleable SKUs at item × location ×
month granularity (and item × week for sensing), trailing 24 months of actuals and
the corresponding forecast snapshots by lag.

**Out of scope**: phase-out SKUs with <3 months history (reported separately); spare
parts with intermittent demand handled by a dedicated Croston/intermittent model.

---

## 4. Business Questions

- What is the forecast accuracy (MAPE) by product family, region, and planner?
- Is the forecast systematically biased (over- or under-forecasting)?
- How does accuracy degrade by forecast lag (lag-1 vs lag-3 vs lag-6)?
- Which SKUs are high-variability (XYZ = Z) and therefore hard to forecast?
- Did manual consensus overrides improve or worsen accuracy vs. statistical baseline?
- Which SKUs have safety stock misaligned with their demand variability?
- What share of demand value falls in each ABC class?
- Which planners/regions are driving the largest absolute forecast error in value?
- What is the fill-rate impact of forecast error by SKU?
- Which new products lack sufficient history for statistical forecasting?

---

## 5. Data Sources

### Source 1 — Actual Sales / Consumption
- **Source Name**: Actual sales (billed) / consumption
- **Origin System**: SAP S/4HANA (SD billing) — VBRK/VBRP; or BW DSO
- **Report/Table/Query**: billing documents aggregated to item × location × period
- **Data Owner**: Commercial / Order Management
- **Update Frequency**: Daily (incremental by billing date)
- **Required Fields**: `MATNR, location, billing_date, qty, net_value, currency, customer`
- **Critical Fields**: `qty`, `billing_date`, `MATNR`, `location`
- **Primary/Logical Key**: billing_doc + item
- **Required Validations**: returns netted; qty in base UOM; no negative net qty after netting
- **Possible Errors**: intercompany sales double-counted; returns posted to wrong period;
  UOM mismatch
- **Extraction Evidence**: sum(qty), sum(net_value) per period vs SAP VF05 / BW report

### Source 2 — Statistical Baseline Forecast
- **Source Name**: Statistical baseline forecast
- **Origin System**: SAP IBP for Demand
- **Report/Table/Query**: IBP key figure `STAT_FCST` by item × location × period × snapshot
- **Data Owner**: Demand Planning (statistical models)
- **Update Frequency**: Monthly (snapshot at planning lock) + weekly sensing
- **Required Fields**: `product_id, location_id, period, lag, stat_forecast_qty, snapshot_date`
- **Critical Fields**: `stat_forecast_qty`, `lag`, `snapshot_date`
- **Primary/Logical Key**: product + location + period + snapshot_date
- **Required Validations**: forecast ≥ 0; snapshot uniqueness per period
- **Possible Errors**: missing snapshots (broken lag analysis); model fallback to naive
- **Extraction Evidence**: IBP key-figure export count vs reconciliation

### Source 3 — Consensus / Final Forecast
- **Source Name**: Consensus demand plan
- **Origin System**: SAP IBP for Demand
- **Report/Table/Query**: IBP key figure `CONSENSUS_FCST`
- **Data Owner**: Demand Planning / S&OP
- **Update Frequency**: Monthly snapshot + weekly
- **Required Fields**: `product_id, location_id, period, lag, consensus_qty, snapshot_date,
  override_qty (consensus − stat)`
- **Critical Fields**: `consensus_qty`, `snapshot_date`
- **Primary/Logical Key**: product + location + period + snapshot_date
- **Required Validations**: consensus ≥ 0; override = consensus − stat computed
- **Possible Errors**: overrides applied after lock (data integrity); unit mismatch
- **Extraction Evidence**: consensus total vs IBP planning view

### Source 4 — Safety Stock & Service Parameters
- **Source Name**: Safety stock and service level parameters
- **Origin System**: SAP S/4HANA (MM material master) / IBP
- **Report/Table/Query**: MARC (MRP views) + IBP inventory key figures
- **Data Owner**: Inventory Planning
- **Update Frequency**: Weekly
- **Required Fields**: `MATNR, location, safety_stock_qty, target_service_level,
  lead_time_days, lead_time_std`
- **Critical Fields**: `safety_stock_qty`, `target_service_level`, `lead_time_days`
- **Primary/Logical Key**: MATNR + location
- **Required Validations**: SS ≥ 0; service level in (0,1)
- **Possible Errors**: stale SS not recalculated; missing lead-time variability
- **Extraction Evidence**: SS value count reconciled to SAP MM03

### Source 5 — Product & Location Master
- **Source Name**: Product / location master
- **Origin System**: SAP S/4HANA (MM)
- **Report/Table/Query**: MARA + MAKT + product hierarchy; plant/DC master
- **Data Owner**: MDM
- **Update Frequency**: Daily
- **Required Fields**: `MATNR, description, product_family, brand, base_uom,
  lifecycle_status, planner_code, location_id, region`
- **Critical Fields**: `product_family`, `lifecycle_status`, `planner_code`
- **Primary/Logical Key**: MATNR (+ location for location attributes)
- **Required Validations**: family and planner populated; UOM consistent with actuals
- **Possible Errors**: missing hierarchy; planner unassigned
- **Extraction Evidence**: SKU count vs SAP MM60

---

## 6. Data Model

Star schema (Azure SQL → Power BI import):

**Fact tables**
- `fact_actuals` — grain: product × location × period (month) [+ week variant].
- `fact_forecast` — grain: product × location × period × snapshot_date × forecast_type
  (STAT / CONSENSUS), carrying lag.
- `fact_accuracy` — grain: product × location × period × lag (computed errors).
- `fact_safety_stock` — grain: product × location (current parameters + computed need).

**Dimension tables**
- `dim_product` (MATNR, family, brand, lifecycle, planner, base_uom)
- `dim_location` (location_id, name, region, country)
- `dim_date` (date, week, month, quarter, year, fiscal_period)
- `dim_planner` (planner_code, planner_name, region)
- `dim_abcxyz` (product × location → ABC class, XYZ class, combined)

**Relationships**
- All facts → dim_product (MATNR), dim_location (location_id), dim_date (period).
- fact_forecast.forecast_type is a column dimension (STAT vs CONSENSUS).
- dim_abcxyz → dim_product+dim_location (computed segmentation).

---

## 7. Data Dictionary

### Table: fact_actuals
- **Description**: Actual demand by item/location/period in base UOM.
- **Granularity**: product × location × month (and × week).
- **Required Fields**:
  | Field | Type | Description |
  |---|---|---|
  | product_id | varchar | MATNR |
  | location_id | varchar | Plant/DC |
  | period | date | First day of month |
  | actual_qty | decimal(18,3) | Net demand in base UOM |
  | actual_value | decimal(18,2) | Net value (group ccy) |
- **Primary Key**: product_id + location_id + period
- **Relationships**: → dim_product, dim_location, dim_date
- **Required Transformations**: net returns; convert UOM; aggregate to period
- **Cleaning Rules**: exclude intercompany; floor negative netted to 0 with flag
- **Validations**: actual_qty ≥ 0; UOM consistent
- **Use in Analysis**: accuracy denominator; CV; ABC value

### Table: fact_forecast
- **Description**: Forecast snapshots (statistical and consensus) with lag.
- **Granularity**: product × location × period × snapshot_date × forecast_type.
- **Required Fields**: product_id, location_id, period, snapshot_date, forecast_type,
  forecast_qty, lag (= months between snapshot and period)
- **Primary Key**: product_id+location_id+period+snapshot_date+forecast_type
- **Relationships**: → dim_product, dim_location, dim_date
- **Required Transformations**: compute lag; align UOM
- **Cleaning Rules**: drop snapshots after planning lock
- **Validations**: forecast_qty ≥ 0; lag ≥ 1
- **Use in Analysis**: accuracy, bias, baseline-vs-consensus

### Table: fact_accuracy
- **Description**: Computed error metrics per item/location/period/lag.
- **Granularity**: product × location × period × lag × forecast_type.
- **Required Fields**: product_id, location_id, period, lag, forecast_type, actual_qty,
  forecast_qty, abs_error, ape, signed_error
- **Primary Key**: product+location+period+lag+forecast_type
- **Relationships**: → dim_product, dim_location, dim_date
- **Required Transformations**: join actuals to forecast by (item,location,period); compute
  abs_error, ape, signed_error (see §8)
- **Validations**: ape computed only where actual_qty>0
- **Use in Analysis**: MAPE, MAE, RMSE, Bias

### Table: fact_safety_stock
- **Description**: Current SS parameters and computed theoretical need.
- **Granularity**: product × location.
- **Required Fields**: product_id, location_id, safety_stock_qty, target_service_level,
  z_value, demand_std, lead_time_days, lead_time_std, ss_method3, ss_method4, ss_gap
- **Primary Key**: product_id + location_id
- **Relationships**: → dim_product, dim_location
- **Required Transformations**: compute SS Method 3 & 4 (see §10); gap vs actual SS
- **Validations**: SS ≥ 0; service level in (0,1)
- **Use in Analysis**: safety stock adequacy

---

## 8. Transformation Rules

1. **Net returns**: `actual_qty = billed_qty − returned_qty` per item/location/period.
2. **UOM normalisation**: convert all quantities to base UOM via MARM conversion factors.
3. **Period bucketing**: map dates to fiscal month/week using `dim_date`.
4. **Lag computation**: `lag = DATEDIFF(month, snapshot_date_period, target_period)`.
5. **Absolute error**: `abs_error = ABS(actual_qty − forecast_qty)`.
6. **APE (absolute percent error)**: `ape = abs_error / NULLIF(actual_qty,0)` — null where
   actual=0 (excluded from MAPE; reported via alternative WMAPE).
7. **Signed error (for bias)**: `signed_error = forecast_qty − actual_qty`.
8. **Override magnitude**: `override_qty = consensus_qty − stat_forecast_qty`.
9. **Demand CV**: per item/location over trailing 12 months, `CV = STDEV(actual_qty)/
   AVG(actual_qty)`.
10. **ABC value share**: annualised `value = AVG(actual_value)*12`; rank descending,
    cumulative share → A ≤80 %, B ≤95 %, C rest.
11. **XYZ class**: from CV — X (<0.10), Y (0.10–0.25), Z (>0.25).
12. **WMAPE** (volume-weighted, robust to zeros): `WMAPE = SUM(abs_error)/SUM(actual_qty)`.

---

## 9. Business Rules

### Rule: SKU forecastability
- **Description**: Only SKUs with sufficient history get statistical accuracy KPIs.
- **Logic Condition**: `months_of_history >= 3 AND lifecycle_status NOT IN ('NPI','EOL')`.
- **Expected Result**: SKU included in accuracy reporting.
- **Example**: SKU launched 6 weeks ago → excluded; reported in NPI view.
- **Exception**: strategic NPIs reported separately with attach-rate method.
- **Required Evidence**: in-scope SKU list with history count.

### Rule: MAPE exclusion of zero-actual periods
- **Description**: APE undefined when actual=0.
- **Logic Condition**: `IF actual_qty = 0 THEN ape = NULL`.
- **Expected Result**: MAPE computed on non-zero periods; WMAPE reported alongside.
- **Example**: promo SKU with zero baseline month excluded from MAPE.
- **Exception**: intermittent SKUs use WMAPE only.
- **Required Evidence**: count of excluded periods reported.

### Rule: Override value classification
- **Description**: Classify whether consensus override helped or hurt.
- **Logic Condition**: `IF ABS(consensus_qty−actual) < ABS(stat_qty−actual) THEN
  'override_improved' ELSE 'override_worsened'`.
- **Expected Result**: each SKU-period flagged.
- **Example**: stat=100, consensus=120, actual=118 → override improved.
- **Exception**: ties → neutral.
- **Required Evidence**: FVA (Forecast Value Added) summary.

### Rule: Safety stock adequacy flag
- **Description**: Flag SS misaligned with variability.
- **Logic Condition**: `IF actual_SS < 0.8 * ss_method4 THEN 'under-stocked';
  IF actual_SS > 1.5 * ss_method4 THEN 'over-stocked'`.
- **Expected Result**: SS alignment flag.
- **Example**: actual SS 50, method4 100 → under-stocked.
- **Exception**: strategic buffers by policy → annotate.
- **Required Evidence**: SS gap table.

---

## 10. KPIs and Formulas

### KPI: MAPE
- **Objective**: average percentage forecast error.
- **Formula (DAX)**: `MAPE = AVERAGEX(FILTER(fact_accuracy, fact_accuracy[actual_qty]>0),
  fact_accuracy[ape]) * 100`
- **Data Source**: fact_accuracy
- **Calculation Level**: item/family/region/planner × lag
- **Frequency**: monthly
- **Owner**: Demand Planner
- **Interpretation**: lower is better; demand-pattern dependent.
- **Thresholds**: Green <20 %, Yellow 20–40 %, Red >40 %
- **Recommended Action**: Red → model review / segmentation change.
- **Validation vs Source**: recompute one family vs IBP accuracy key figure.

### KPI: WMAPE (volume-weighted)
- **Objective**: error robust to intermittent/zero demand.
- **Formula (DAX)**: `WMAPE = DIVIDE(SUM(fact_accuracy[abs_error]),
  SUM(fact_accuracy[actual_qty])) * 100`
- **Thresholds**: Green <15 %, Yellow 15–30 %, Red >30 %
- **Recommended Action**: Red → review high-volume error drivers.
- **Validation vs Source**: SUM(abs_error)/SUM(actual) cross-check.

### KPI: MAE
- **Objective**: average absolute error in units.
- **Formula (DAX)**: `MAE = AVERAGE(fact_accuracy[abs_error])`
- **Interpretation**: unit error magnitude; compare across similar SKUs.
- **Thresholds**: relative to SKU volume — *Pending to confirm targets*.
- **Recommended Action**: rank top absolute-error SKUs for review.
- **Validation vs Source**: manual recompute sample.

### KPI: RMSE
- **Objective**: error metric penalising large misses.
- **Formula (DAX)**: `RMSE = SQRT(AVERAGEX(fact_accuracy, fact_accuracy[abs_error]^2))`
- **Interpretation**: high vs MAE indicates large outlier errors.
- **Recommended Action**: investigate outlier periods (promos, events).
- **Validation vs Source**: sample recompute.

### KPI: Forecast Bias
- **Objective**: detect systematic over/under-forecasting.
- **Formula (DAX)**: `Bias % = DIVIDE(SUM(fact_accuracy[signed_error]),
  SUM(fact_accuracy[actual_qty])) * 100`
- **Interpretation**: + = over-forecast, − = under-forecast.
- **Thresholds**: Green |bias|<5 %, Yellow 5–15 %, Red >15 %
- **Recommended Action**: Red → de-bias model / planner coaching.
- **Validation vs Source**: signed-error sum cross-check.

### KPI: Forecast Value Added (FVA)
- **Objective**: did consensus beat statistical baseline?
- **Formula**: `FVA = MAPE_stat − MAPE_consensus` (positive = override added value).
- **Interpretation**: negative FVA → overrides are harming accuracy.
- **Thresholds**: Green >0, Red <0
- **Recommended Action**: negative → reduce manual intervention.
- **Validation vs Source**: compare both forecast types same periods.

### KPI: Demand CV
- **Objective**: quantify demand variability.
- **Formula (DAX)**: `CV = DIVIDE(STDEVX.P(...actual_qty), AVERAGE(...actual_qty))`
- **Interpretation**: drives XYZ class and forecastability.
- **Thresholds**: X<0.10, Y 0.10–0.25, Z>0.25
- **Recommended Action**: Z → consider safety stock over forecast accuracy.
- **Validation vs Source**: recompute on sample.

### KPI: Safety Stock Coverage (days)
- **Objective**: how many days of demand the SS covers.
- **Formula**: `SS_coverage_days = safety_stock_qty / ADU` where `ADU = trailing 90-day
  avg daily demand`.
- **Thresholds**: *Pending to confirm by category*.
- **Recommended Action**: align under/over-stocked SKUs.
- **Validation vs Source**: SS vs SAP MM03.

### KPI: Safety Stock (Method 3 & 4)
- **Formula**:
  ```
  Method 3: SS = z * demand_std * SQRT(lead_time_days)
  Method 4: SS = z * SQRT(lead_time_days*demand_std^2 + ADU^2*lead_time_std^2)
  z = NORM.S.INV(target_service_level)
  ```
- **Interpretation**: Method 4 accounts for lead-time variability (recommended).
- **Recommended Action**: align actual SS to Method 4 ±tolerance.
- **Validation vs Source**: recompute z from service level.

---

## 11. Analytical Logic

- **Segmentations**: product family, brand, region, planner, lifecycle, lag.
- **ABC/XYZ matrix**: 9-box (AX..CZ); policy mapping (AX/AY → tight forecast + low SS;
  CZ → SS-driven, simple model).
- **Lag analysis**: accuracy by lag-1/3/6 to set planning horizon expectations.
- **Priority logic**: improvement focus = `actual_value_share * MAPE` (worst value-weighted
  error first).
- **Alert logic**:
  - Family MAPE Red 2 months → model review ticket.
  - |Bias| Red → planner coaching alert.
  - FVA negative for a planner → S&OP escalation.
  - SS gap >50 % vs Method 4 → inventory planning alert.

---

## 12. Validations and Controls

### Validation: Actuals reconciliation
- **Field/Table**: fact_actuals.actual_qty
- **Validation Rule**: sum per period = SAP billing total (netted) ±0.5 %.
- **Validation Method**: compare to SAP VF05/BW.
- **Expected Result**: within tolerance.
- **Action if Fails**: investigate returns/intercompany.
- **Verifiable Evidence**: reconciliation report.

### Validation: Snapshot completeness
- **Field/Table**: fact_forecast.snapshot_date
- **Validation Rule**: every planning month has a locked snapshot.
- **Validation Method**: snapshot count per period.
- **Expected Result**: no missing snapshots.
- **Action if Fails**: backfill from IBP; flag broken lag.
- **Verifiable Evidence**: snapshot calendar.

### Validation: APE zero-handling
- **Field/Table**: fact_accuracy.ape
- **Validation Rule**: ape null when actual=0.
- **Validation Method**: check no infinite/error values.
- **Expected Result**: zero divide-by-zero.
- **Action if Fails**: fix NULLIF logic.
- **Verifiable Evidence**: query result.

### Validation: Service-level → z consistency
- **Field/Table**: fact_safety_stock.z_value
- **Validation Rule**: z = NORM.S.INV(service_level).
- **Validation Method**: recompute and compare.
- **Expected Result**: match within rounding.
- **Action if Fails**: correct z mapping.
- **Verifiable Evidence**: comparison table.

---

## 13. Required Evidence

- ETL audit log per load (actuals, forecast snapshots).
- Monthly accuracy reconciliation to IBP key figures.
- Manual recompute of MAPE/Bias for one product family signed off by planner.
- ABC/XYZ classification snapshot per month.
- SS gap report with method 3/4 values.

---

## 14. Dashboard / Report Design (Power BI)

**Page 1 — Accuracy Overview**: MAPE/WMAPE/Bias cards; trend; accuracy by family/region.
**Page 2 — Lag Analysis**: accuracy by lag (1/3/6); waterfall of error sources.
**Page 3 — FVA / Baseline vs Consensus**: stat vs consensus MAPE; override impact.
**Page 4 — ABC/XYZ Segmentation**: 9-box matrix with value share; SKU table.
**Page 5 — Safety Stock Adequacy**: actual SS vs Method 4; under/over-stocked SKUs.
**Slicers**: period, family, region, planner, lag, ABC/XYZ class, lifecycle.
**Drill-through**: family → SKU-level error detail; planner → SKU override list.

---

## 15. Use Cases

1. **Planner review**: planner sees family MAPE Red, drills to SKUs, finds promo-driven
   error, adds causal regressor.
2. **FVA governance**: S&OP sees negative FVA for a region → reduces manual overrides.
3. **Bias correction**: persistent +12 % bias → model de-biased; SS reduced.
4. **Segmentation**: AX SKUs prioritised for accuracy; CZ moved to SS-buffer policy.
5. **SS realignment**: under-stocked Z SKUs identified → SS increased to Method 4.

---

## 16. Recommended Actions

| Result / Condition | Recommended Action | Owner | Timeline |
|---|---|---|---|
| Family MAPE >40 % | Model review / new method | Demand Planner | 2 weeks |
| Bias >15 % | De-bias model / coaching | Planning Lead | 1 cycle |
| FVA negative | Reduce manual overrides | S&OP | 1 cycle |
| SS gap >50 % vs M4 | Recalculate safety stock | Inventory Planner | 2 weeks |
| CZ high-value SKU | Switch to SS-driven policy | Planner | 1 cycle |

---

## 17. Test Cases

### TC-01 — MAPE zero-actual exclusion
- **Scenario**: period with actual=0, forecast=10.
- **Input Data**: one accuracy row.
- **Expected Result**: ape=NULL; excluded from MAPE; included in WMAPE.
- **Result to Avoid**: divide-by-zero error.
- **Required Validation**: NULLIF test.
- **Evidence**: query output.

### TC-02 — Bias sign
- **Scenario**: forecast=120, actual=100.
- **Input Data**: accuracy row.
- **Expected Result**: signed_error=+20; bias positive (over-forecast).
- **Result to Avoid**: sign inverted.
- **Required Validation**: sign test.
- **Evidence**: bias value.

### TC-03 — Lag computation
- **Scenario**: snapshot for May taken in February.
- **Input Data**: snapshot_date=Feb, period=May.
- **Expected Result**: lag=3.
- **Result to Avoid**: lag=2 or 4.
- **Required Validation**: DATEDIFF test.
- **Evidence**: lag value.

### TC-04 — XYZ boundary
- **Scenario**: CV=0.10 exactly.
- **Input Data**: computed CV.
- **Expected Result**: class=Y (per X<0.10 rule).
- **Result to Avoid**: class=X.
- **Required Validation**: boundary test.
- **Evidence**: class output.

### TC-05 — SS Method 4
- **Scenario**: z=1.65, LT=9, demand_std=10, ADU=20, LT_std=2.
- **Input Data**: parameters.
- **Expected Result**: SS = 1.65*sqrt(9*100 + 400*4) = 1.65*sqrt(2500)=82.5.
- **Result to Avoid**: using Method 3 (≈49.5).
- **Required Validation**: formula test.
- **Evidence**: SS value.

### TC-06 — Actuals reconciliation
- **Scenario**: monthly load.
- **Input Data**: fact_actuals vs SAP billing.
- **Expected Result**: within ±0.5 %.
- **Result to Avoid**: gap unflagged.
- **Required Validation**: reconciliation query.
- **Evidence**: report.

---

## 18. Risks and Mitigations

| Risk | Probability | Impact | Preventive Control | Corrective Control |
|---|---|---|---|---|
| Missing forecast snapshots | High | High | Automated snapshot capture | Backfill from IBP |
| Returns mis-period | Medium | High | Posting-date netting | Restate period |
| Zero-actual distorting MAPE | High | Medium | WMAPE + exclusion rule | Report both metrics |
| Stale safety stock | Medium | Medium | Weekly SS recompute | Inventory alert |
| UOM mismatch | Low | High | MARM conversion control | Re-extract |
| Intercompany double count | Medium | High | Exclusion filter | Reconciliation |

---

## 19. Implementation Checklist

1. Confirm forecast hierarchy and lag definition with Demand Planning.
2. Build Azure SQL staging for Sources 1–5.
3. Extract IBP snapshots (STAT + CONSENSUS) with snapshot_date.
4. Build fact/dim model per §6.
5. Implement transformations §8 (netting, lag, errors, CV).
6. Build fact_accuracy compute.
7. Build ABC/XYZ segmentation.
8. Compute SS Method 3 & 4 and gaps.
9. Build Power BI model + relationships.
10. Author KPI measures (MAPE, WMAPE, Bias, FVA, CV, SS).
11. Build 5 dashboard pages.
12. Configure RLS (region/planner).
13. Set daily refresh + monthly snapshot.
14. Implement validations §12 as ETL gates.
15. Build reconciliation pack to IBP.
16. UAT with planners.
17. Document lineage.
18. Go-live + hypercare.

---

## 20. Validation Checklist

1. Actuals reconciled to SAP billing ±0.5 %.
2. Snapshot completeness verified per period.
3. APE zero-handling correct.
4. MAPE/Bias recomputed on a family vs IBP.
5. ABC value share sums to 100 %.
6. XYZ boundaries correct.
7. SS Method 4 matches manual test case.
8. z-value consistent with service level.
9. RLS verified.
10. Refresh schedule confirmed.
11. FVA logic validated (improved/worsened).

---

## 21. Pending Information to Confirm

- Forecast hierarchy levels and aggregation rules. — *Pending to confirm*
- MAE/RMSE target thresholds by category. — *Pending to confirm*
- Safety-stock coverage-day targets by category. — *Pending to confirm*
- Intermittent-demand SKU list (Croston handling). — *Pending to confirm*
- Snapshot lock calendar from IBP. — *Pending to confirm*
- Planner-to-product assignment source. — *Pending to confirm*
- RLS security groups. — *Pending to confirm*

---

## 22. Implementation Roadmap

| Week | Activity | Deliverable | Owner | Status |
|---|---|---|---|---|
| 1–2 | Requirements + hierarchy | Signed scope | BI Lead | Pending |
| 3–5 | Staging + IBP extraction | Loaded snapshots | Data Eng | Pending |
| 6–8 | Fact/dim + transforms | Model v1 | Data Eng | Pending |
| 9–10 | Accuracy + ABC/XYZ + SS | Computed facts | Analytics | Pending |
| 11–13 | Power BI + KPIs | Dashboard draft | BI Dev | Pending |
| 14–15 | Validations + reconciliation | Recon pack | Data Quality | Pending |
| 16–17 | UAT | Sign-off | Demand Planning | Pending |
| 18 | Go-live + hypercare | Production report | BI Lead | Pending |
