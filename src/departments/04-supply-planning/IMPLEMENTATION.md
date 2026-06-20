# Supply Planning — Enterprise Implementation Playbook

## Executive Summary

Supply planning converts the consensus demand forecast into executable
production schedules, procurement signals, and inventory build plans across
a multi-echelon network. For a €50 B multinational with 40 countries, 80+
plants, and thousands of SKUs, supply planning is the central nervous system
that balances customer service levels against working capital and capacity
constraints.

A world-class supply planning capability — combining classical MRP with
DDMRP buffer management, constrained optimisation, and ML-enhanced lead time
prediction — delivers 15-25 % inventory reduction, 5-10 % improvement in
schedule adherence, and 20-30 % reduction in expediting costs.

This playbook covers every mathematical model, ML/AI pipeline, and operational
process in the `04-supply-planning` module, designed for deployment on
SAP S/4HANA + SAP IBP.

---

## Prerequisites & Dependencies

| Dependency | Detail |
|---|---|
| SAP S/4HANA (PP/MM) | Bills of material, routings, work centres, MRP areas |
| SAP IBP for Supply | Constrained supply planning, IBP integration |
| Demand plan | Consensus forecast from department 03 (daily/weekly buckets) |
| Supplier master | Lead times, MOQ, capacity confirmations per supplier |
| Plant/DC network | Transportation lanes, transit times, transfer costs |
| Capacity data | Rated capacity, efficiency per work centre / production line |
| Python ≥ 3.11 | OR-Tools, SimPy, XGBoost, scipy |
| Historical MRP data | ≥24 months of planned vs. actual for ML training |

---

## Phase 0: AS-IS Assessment (Weeks 1-8)

### 0.1 Supply Network Mapping
1. Document all plants, DCs, and their relationships (make / buy / transfer).
2. Map key materials to their bills of material (BOM depth, phantom items).
3. Identify capacity bottlenecks (utilisation >90 % at any work centre).
4. Measure current schedule adherence (planned vs. actual production).
5. Quantify expediting frequency and cost.

### 0.2 MRP Configuration Audit
- Review MRP types per material (MRP, KANBAN, reorder point, no-planning).
- Identify planning time fences; assess if they reflect true frozen horizons.
- Measure forecast error propagation (bullwhip) through the supply chain.

### 0.3 KPI Baseline

| KPI | Typical Baseline | World-Class Target |
|---|---|---|
| Schedule adherence | 72 % | ≥92 % |
| Bullwhip ratio | 2.8 | ≤1.3 |
| Expediting cost (% of logistics spend) | 8 % | ≤2 % |
| Supplier OTIF | 71 % | ≥92 % |
| Inventory turns (WIP + FG) | 6.2 | ≥10 |
| Planning cycle time | 3 days | ≤4 hours (automated) |
| Forecast bias | ±18 % | ±5 % |

---

## Phase 1: Foundation & Master Data (Weeks 9-20)

### 1.1 Planning Master Data
1. Cleanse and validate BOMs: no phantom loops, accurate component quantities.
2. Set planned delivery times (PDT) per material + supplier combination.
3. Define MRP areas per plant (separate planning for critical vs. standard).
4. Configure safety stock levels per method (Phase 3 will optimise these).
5. Set planning horizons: frozen (2 weeks), slushy (3-8 weeks), liquid (8+ weeks).

### 1.2 Network Model
1. Define supply network in SAP IBP: plants, DCs, lanes, transit times.
2. Map demand nodes (DCs) to supply nodes (plants/suppliers).
3. Set transportation costs and minimum shipment quantities per lane.

### 1.3 Capacity Master Data
1. Enter rated capacity per work centre (shifts × hours × efficiency).
2. Define capacity categories (machine, labour, tool).
3. Set up resource networks for bottleneck work centres.

---

## Phase 2: Process Standardisation (Weeks 21-36)

### 2.1 Weekly Planning Cycle
```
Monday: Demand signal refresh (POS/orders/EDI 830)
Tuesday: MRP/IBP run — generate planned orders and purchase requisitions
Wednesday: Capacity leveling — resolve overloads; exception management
Thursday: Supplier scheduling — send releases; confirm capacities
Friday: Publish plan; update S&OP system
```

### 2.2 Exception Management
- MRP exception messages reviewed daily by planner.
- Auto-resolve: reschedule messages within ±3 days (system action).
- Manual resolve: capacity overloads, new orders outside horizon.
- KPI: exception message volume; target <5 % of planned orders.

---

## Phase 3: Mathematical Models

### 3.1 MRP Net Requirements Calculation

**Business problem**: determine what needs to be produced or procured, and when,
to satisfy demand without excess inventory.

**Formulation**:
```
For each period t, each material m:

  GrossRequirements_t   = dependent demand (from parent BOM) + independent demand
  ScheduledReceipts_t   = confirmed POs / production orders due in t
  ProjectedOnHand_{t-1} = inventory carried from prior period
  NetRequirements_t     = max(0, GrossRequirements_t - ScheduledReceipts_t - ProjectedOnHand_{t-1})
  PlannedOrderReceipts_t = NetRequirements_t (or rounded to lot size)
  PlannedOrderRelease_{t-LT} = PlannedOrderReceipts_t (offset by lead time)
```

**Implementation steps**:
1. Run MRP in SAP S/4HANA (transaction MD01N / MD02) or IBP.
2. Validate GrossRequirements match demand plan from department 03.
3. Confirm ScheduledReceipts include all open POs and production orders.
4. Review ProjectedOnHand matches physical inventory (cycle count aligned).
5. Check lot-sizing rules: EX (exact), FX (fixed), WB (weekly), PK (pack size).
6. Validate lead times for critical materials (compare planned vs. actual LT).
7. Review low-level codes — ensure MRP runs bottom-up through BOM levels.
8. Generate exception messages; address reschedule-in/out per period.
9. Convert planned orders: production orders (make) or purchase requisitions (buy).
10. Communicate confirmed production schedule to shop floor.

---

### 3.2 Capacity Requirements Planning (CRP)

**Business problem**: validate that available capacity can absorb the planned
production schedule; identify and resolve bottlenecks.

**Formulation**:
```
For work centre w in period t:
  Required_load_{w,t} = Σ_m (planned_qty_{m,t} × std_run_time_{m,w} / efficiency_w)

  Available_cap_{w,t} = shifts × hours_per_shift × (1 - downtime_rate) × efficiency_w

  Utilisation_{w,t}   = Required_load_{w,t} / Available_cap_{w,t} × 100

  Overload if Utilisation > 100 % → resolve by:
    a) Overtime (capacity increase)
    b) Outsourcing (subcontracting order)
    c) Demand deferral (negotiate with sales)
    d) Alternative work centre routing
```

**Implementation steps**:
1. Run CRP in SAP PP (transaction CM01/CM21) after MRP.
2. Identify all work centres with utilisation >90 % in any week.
3. For bottlenecks: display load profile; identify root material/order.
4. Finite scheduling: move orders earlier/later within planning fence.
5. Evaluate overtime: cost < expediting cost? → approve.
6. For chronic overloads (>3 consecutive weeks): escalate to capital investment.
7. Publish capacity-confirmed plan to production supervisors.

---

### 3.3 DDMRP Buffer Sizing

**Business problem**: protect throughput at decoupling points in the supply chain
by maintaining dynamic, self-adjusting buffers.

**Formulation**:
```
For each decoupled item i:

ADU_i  = Average Daily Usage (units/day, 30-day rolling)
DLT_i  = Decoupled Lead Time (days)
LTF_i  = Lead Time Factor (0.5 for purchased items; varies by variability)
MOQ_i  = Minimum Order Quantity

TOP_i (Top of Green)  = max(ADU_i × DLT_i × LTF_i, MOQ_i)
TOY_i (Top of Yellow) = ADU_i × DLT_i
TOR_i (Top of Red)    = ADU_i × DLT_i × LTF_i × Variability_Factor_i

Buffer zones:
  Green  = TOY_i to TOP_i   (supply generation zone)
  Yellow = TOR_i to TOY_i   (consumption coverage zone)
  Red    = 0 to TOR_i       (safety zone — order immediately if penetrated)

Dynamic adjustment:
  ADU recalculated weekly.
  If 3 consecutive weeks: buffer too large (no red penetration) → reduce LTF by 20%.
  If 3 consecutive weeks: buffer too small (red penetrated) → increase LTF by 20%.
```

**Implementation steps**:
1. Identify decoupling points: where demand variability should be absorbed.
2. Compute ADU per item from last 30 days' actual consumption.
3. Set DLT = supplier confirmed lead time (not planned lead time).
4. Set LTF by item category: purchased long-lead = 0.8; standard = 0.5.
5. Compute all three buffer zones.
6. Configure DDMRP in SAP IBP (or custom extension) with buffer parameters.
7. Daily: check on-hand against buffer zones; generate supply orders when in green.
8. Weekly: review ADU trend; adjust buffers via dynamic adjustment rules.
9. Monitor red zone penetrations as KPI (target: <10 % of planning days).
10. Review buffer parameters quarterly for structural demand changes.

---

### 3.4 Bullwhip Effect Quantification

**Business problem**: measure and reduce demand amplification as orders move
upstream through the supply chain.

**Formulation**:
```
Bullwhip_Ratio = Var(Orders_t) / Var(Demand_t)

Where:
  Orders_t  = purchase orders placed to supplier in period t
  Demand_t  = actual end-customer demand in period t

BWE > 1.0  : amplification exists (orders more variable than demand)
BWE > 2.0  : significant bullwhip — review ordering policy
BWE > 5.0  : severe — likely due to fear-ordering or batch ordering

Dampening actions:
  1. Reduce order batch sizes (move toward EOQ or DDMRP flow)
  2. Share POS data with suppliers (vendor-managed inventory)
  3. Reduce supply lead times (closer suppliers, safety stock)
  4. Stabilise order frequency (weekly cadence vs. monthly lumps)
```

**Implementation steps**:
1. Pull 24 months of orders vs. demand by SKU and supply tier.
2. Compute variance ratio per SKU-supplier link.
3. Rank links by BWE descending; focus on top 20 %.
4. Root-cause high BWE links: batch ordering? promotional lumps? fear-ordering?
5. Implement remediation (DDMRP, VMI, order smoothing rules).
6. Re-measure BWE monthly; target reduction to <1.5 within 12 months.

---

### 3.5 Multi-Echelon Safety Stock (Clark-Scarf)

**Business problem**: optimise safety stock placement across supplier → plant →
DC → store tiers to minimise total inventory investment for a given service level.

**Formulation**:
```
For a 2-echelon system (plant feeds DC):
  SS_DC    = z × σ_D_DC × √(LT_plant_to_DC)
  SS_plant = z × σ_D_plant × √(LT_supplier_to_plant)

Where σ_D is demand std dev at that node.

Multi-echelon: Clark-Scarf theorem — optimise from downstream to upstream:
  For each stage n (from demand end):
    SS_n = z_n × √(LT_n × σ²_D + demand̄² × σ²_LT_n)
    where z_n is chosen to achieve target fill rate at stage n
```

**Implementation steps**:
1. Map supply network: nodes (plant, DC, store) and arcs (LT, variability).
2. Calculate demand mean and std dev at each node from 12 months data.
3. Run Clark-Scarf optimisation (scipy.optimize or OR-Tools) to allocate SS.
4. Compare total SS investment vs. current actual (quantify excess/deficit).
5. Upload optimised SS to SAP MM material master (safety stock field).
6. Review quarterly as demand variability and lead times change.

---

## Phase 4: ML/AI Pipeline

### 4.1 Supplier Lead Time Prediction (XGBoost)

**Business problem**: improve MRP accuracy by predicting actual supplier delivery
time rather than relying on static planned lead times.

**Features**:
- Historical LT for (supplier, material, order_quantity) from 24 months of GR data
- Order quantity (log-transformed)
- Supplier current load (# open POs to supplier)
- Days of year / week (seasonality — holidays, year-end rush)
- Commodity category
- Country of origin
- Port congestion index (if available)
- Supplier scorecard OTD trailing 3 months

**Training steps**:
1. Prepare dataset: one row per PO line; target = actual_LT_days.
2. Split 70/15/15 train/val/test.
3. Train XGBoost regressor: `n_estimators=400, max_depth=6, learning_rate=0.05,
   subsample=0.8, colsample_bytree=0.8`.
4. Evaluate: target MAPE ≤ 15 %, RMSE ≤ 3 days.
5. Feature importance analysis: confirm top features are reasonable.
6. Predict LT at PO creation time; feed to MRP as dynamic lead time.
7. Alert if predicted LT > planned LT by >3 days: buyer action required.

**Retraining**: monthly with 30 new days of actual GR data.

---

### 4.2 Constrained Supply Optimisation (OR-Tools / PuLP)

**Business problem**: given multiple demand nodes, multiple supply sources, and
capacity constraints, find the optimal allocation that maximises service level
at minimum cost.

**Formulation (LP)**:
```
Variables: x_{s,d,t} = units shipped from supply node s to demand node d in period t

Minimise: Σ_{s,d,t} (unit_cost_{s,d} + transport_cost_{s,d}) × x_{s,d,t}
          + Σ_{d,t} shortage_penalty × max(0, demand_{d,t} - Σ_s x_{s,d,t})

Subject to:
  Σ_d x_{s,d,t} ≤ capacity_{s,t}        (supply capacity)
  Σ_s x_{s,d,t} ≤ demand_{d,t}          (demand constraint)
  x_{s,d,t} ≥ 0
```

**Implementation steps**:
1. Build supply network model: nodes, capacities, costs, demand.
2. Formulate LP using `pulp` or `ortools.linear_solver`.
3. Add constraint: minimum sourcing share per strategic supplier (SLA).
4. Solve: typically <30 seconds for 50 nodes × 26 weeks horizon.
5. Extract allocation plan: x_{s,d,t} matrix.
6. Convert to SAP planned orders / purchase requisitions.
7. Run weekly after MRP; constrained plan overrides unconstrained MRP output.

---

### 4.3 Supply Disruption Simulation (SimPy)

**Business problem**: quantify the impact of supply disruptions (port closure,
supplier fire, tariff shock) before they happen — enabling contingency planning.

**Architecture**: discrete-event simulation of the supply network using SimPy.

**Steps**:
1. Model each supply node as a SimPy resource with capacity and lead time.
2. Implement disruption scenarios: node unavailability for X days.
3. Run 1,000 Monte Carlo replications per scenario.
4. Measure: P(stockout), expected lost sales, days to recovery.
5. Compare scenarios: single-source vs. dual-source; DDMRP vs. standard SS.
6. Output: risk-adjusted inventory strategy recommendation.
7. Run quarterly or before major contract renewals.

---

### 4.4 CPFR Bias Correction (XGBoost)

**Business problem**: supplier planning releases (EDI 830) often have systematic
bias vs. actual firm orders; correct the bias to improve production planning.

**Model**: XGBoost regressor predicting `actual_order / planning_release` ratio
per (customer, SKU, horizon_week).

**Steps**:
1. Collect 24 months of EDI 830 planning releases vs. actual firm orders.
2. Compute bias ratio per customer × SKU × horizon week.
3. Features: customer segment, SKU category, horizon week (1-26), season,
   recent demand trend.
4. Train XGBoost; target MAPE ≤ 12 % on bias ratio.
5. Apply correction factor to customer planning releases before feeding MRP.
6. Retrain quarterly.

---

## Phase 5: Integration & Automation (Weeks 37-52)

### 5.1 SAP IBP Integration
- IBP for Demand feeds consensus forecast to IBP for Supply.
- IBP for Supply generates constrained plan; pushes planned orders to S/4HANA.
- Real-time ATP check: IBP Response & Supply for order promising.

### 5.2 EDI Integration
- EDI 830 (Planning Release) from customers → demand signal.
- EDI 862 (Shipping Schedule) to suppliers → supplier scheduling.
- SAP Integration Suite as middleware.

### 5.3 Supplier Scheduling Automation
- Automated release of blanket PO call-offs based on MRP output.
- Supplier capacity confirmation via Ariba or EDI 855.
- Exception: confirm delivery promises within 24 hours or auto-escalate.

---

## Phase 6: Continuous Improvement & CoE

- **Weekly**: MRP run + exception review; capacity leveling; supplier releases.
- **Monthly**: DDMRP buffer review; bullwhip measurement; ML model scoring.
- **Quarterly**: multi-echelon SS optimisation; LP allocation model re-run.
- **Annually**: supply network design review; LT prediction model retrain.
- **CoE**: Supply Planning Analysts (MRP/IBP), Data Scientist, Network Designer.

---

## Technology Stack

| Layer | Technology |
|---|---|
| MRP / Supply planning | SAP S/4HANA PP/MM + SAP IBP for Supply |
| Constrained optimisation | OR-Tools (Google), PuLP |
| Simulation | SimPy (discrete event) |
| ML | XGBoost, scikit-learn |
| Data warehouse | Snowflake / Azure Synapse |
| Orchestration | Apache Airflow |
| Monitoring | MLflow + Grafana |
| Integration | SAP Integration Suite |

---

## KPIs & Success Metrics

| KPI | Baseline | 18-Month Target | Measurement |
|---|---|---|---|
| Schedule adherence | 72 % | ≥92 % | PP production order report |
| Bullwhip ratio | 2.8 | ≤1.3 | Weekly variance analysis |
| Inventory turns (FG+WIP) | 6.2 | ≥10 | FI-CO / MM report |
| DDMRP red-zone penetration | N/A | <10 % of days | DDMRP dashboard |
| LT prediction MAPE | N/A | ≤15 % | MLflow |
| Expediting cost | 8 % | ≤2 % | Cost centre report |
| Planning cycle time | 3 days | ≤4 hours | Process timing log |

---

## Risk & Mitigation

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| BOM data quality issues | High | High | BOM audit sprint before MRP cutover |
| IBP integration complexity | Medium | High | SAP certified integration partner |
| Capacity data inaccurate | Medium | High | Work centre audit; time-study update |
| LP solver infeasibility | Low | Medium | Add slack variables; review capacity constraints |
| DDMRP adoption resistance | Medium | Medium | Pilot on 20 SKUs; prove results; then scale |

---

## Implementation Timeline

| Phase | Weeks | Key Deliverables | Owner |
|---|---|---|---|
| 0: Assessment | 1-8 | Network map, capacity audit, KPI baseline | Supply Planning Lead |
| 1: Foundation | 9-20 | Planning master data, IBP config, horizons | IT + Planning |
| 2: Standardisation | 21-36 | Weekly planning cadence, exception process | Planners |
| 3: Math models | 21-36 | MRP, CRP, DDMRP, Bullwhip live | Analytics |
| 4: ML pipeline | 37-52 | LT prediction, LP optimisation, SimPy | Data Science |
| 5: Integration | 37-52 | IBP-S/4HANA, EDI, supplier scheduling | IT |
| 6: CoE | 53+ | CoE operational, continuous improvement | CoE Lead |

---

## References

- Chopra & Meindl, *Supply Chain Management* 6th Ed., Ch. 9-11 (Pearson, 2016)
- Clark & Scarf, "Optimal Policies for a Multi-Echelon Inventory Problem" (1960)
- Ptak & Smith, *Demand Driven Material Requirements Planning (DDMRP)* (2016)
- Lee, Padmanabhan & Whang, "The Bullwhip Effect in Supply Chains" (HBR, 1997)
- SAP IBP for Supply — Configuration Guide (SAP Help Portal)
- Google OR-Tools Documentation — Vehicle Routing and LP Solver
- Hamilton et al., "Inductive Representation Learning on Large Graphs" (NeurIPS 2017)
