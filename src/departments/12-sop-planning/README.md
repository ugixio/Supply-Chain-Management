# 12 — Sales & Operations Planning (S&OP) / Integrated Business Planning (IBP)

> **SCOR-DS Process**: Plan (sP1–sP5) | **APICS CPIM 9.0** | **Owner**: S&OP / IBP Manager

The S&OP / IBP department aligns demand, supply, inventory, and financial plans into a single monthly executive-consensus cycle. It coordinates the outputs of Demand Planning (Dept. 03), Supply Planning (Dept. 04), Finance & Controlling (Dept. 11), and Inventory Management (Dept. 05) to produce an approved Operating Plan that the entire organisation executes. The process follows the classic 5-step Wallace S&OP cycle, extended to an Integrated Business Planning (IBP) horizon of 24–36 months with full financial reconciliation.

---

## Table of Contents

1. [S&OP 5-Step Monthly Cycle](#1-sop-5-step-monthly-cycle)
2. [Domain Files](#2-domain-files)
3. [Key Business Rules](#3-key-business-rules)
4. [Mathematical Models](#4-mathematical-models)
5. [Recommended ML Models](#5-recommended-ml-models)
6. [KPIs & Thresholds](#6-kpis--thresholds)
7. [S&OP vs IBP Comparison](#7-sop-vs-ibp-comparison)
8. [Integration Points](#8-integration-points)
9. [Roles](#9-roles)
10. [References](#10-references)

---

## 1. S&OP 5-Step Monthly Cycle

```
Week 1   STEP 1 — Data Review
         ✓ Actuals vs. plan: shipments, production, inventory
         ✓ Update inventory positions and open backorders
         ✓ Refresh data master (new SKUs, price changes, discontinued items)
         ✓ Distribute pre-read package to all participants

Week 2   STEP 2 — Demand Review  [Marketing & Sales]
         ✓ Review statistical forecast (Dept. 03 output)
         ✓ Apply market intelligence adjustments (promotions, new customers, NPD)
         ✓ Reach consensus forecast at product-family level (rolling 24 months)
         ✓ Document assumptions and risk scenarios

Week 2   STEP 3 — Supply Review  [Operations & SC]
         ✓ Validate production and procurement capacity vs. consensus demand
         ✓ Identify demand-supply gaps (over/under-capacity)
         ✓ Propose mitigation options with cost and lead-time implications
         ✓ Confirm inventory target vs. actual trajectory

Week 3   STEP 4 — Pre-S&OP  [Directors]
         ✓ Reconcile unresolved demand-supply gaps
         ✓ Financial bridge: translate operational plan to P&L (revenue, margin, COGS)
         ✓ Evaluate what-if scenarios (P10/P50/P90)
         ✓ Prepare decision package and recommendations for Executive S&OP

Week 4   STEP 5 — Executive S&OP  [C-Suite]
         ✓ Approve the Operating Plan for next 3 months (firm) + 24 months (indicative)
         ✓ Authorise investment decisions arising from capacity gaps
         ✓ Communicate approved plan to the organisation
         ✓ Review S&OP process KPIs and maturity
```

---

## 2. Domain Files

### `domain/SOPCycle.ts`

| Export | Description |
|---|---|
| `SOPCycleStatus` | `DATA_REVIEW` / `DEMAND_REVIEW` / `SUPPLY_REVIEW` / `PRE_SOP` / `EXECUTIVE_SOP` / `APPROVED` |
| `SOPCycle` | Monthly cycle record: `{ cycleMonth, status, demandConsensus, supplyPlan, financialBridge, approvedBy }` |
| `SOPParticipant` | `{ role, department, attendanceRequired }` |
| `createSOPCycle(month)` | Factory; initialises cycle in `DATA_REVIEW` status |
| `advanceCycleStep(cycle)` | State machine transition; validates step completion before advancing |

### `domain/DemandConsensus.ts`

| Export | Description |
|---|---|
| `ConsensusForecast` | `{ skuId, period, statisticalFcst, adjustedFcst, consensusFcst, assumptionsLog[] }` |
| `ForecastSource` | `STATISTICAL` / `MARKET_INTELLIGENCE` / `SALES_TEAM` / `CONSENSUS` |
| `buildConsensusForecast(statistical, market, sales, weights)` | Weighted combination with weight validation (Σ = 1) |

### `domain/FinancialBridge.ts`

| Export | Description |
|---|---|
| `FinancialBridge` | Translates units (consensus demand) to revenue and margin: `{ demandUnits, revenueEUR, COGSCents, grossMarginPct }` |
| `buildFinancialBridge(consensusForecast, priceList, costStandard)` | Revenue = Σ (units × price); COGS = Σ (units × standard_cost) |
| `gapToBudget(bridge, budget)` | `gap = bridge.revenueEUR − budget.revenueEUR`; positive = upside |

### `domain/Scenario.ts`

| Export | Description |
|---|---|
| `ScenarioType` | `OPTIMISTIC` / `BASE` / `PESSIMISTIC` / `DISRUPTION` / `CUSTOM` |
| `Scenario` | `{ type, demandMultiplier, supplyConstraint, financialImpact, probability }` |
| `runScenario(baseplan, scenario)` | Applies multipliers and constraints; returns adjusted financial bridge |

---

## 3. Key Business Rules

1. **Consensus Forecast Ownership** — The consensus forecast is owned by the S&OP Manager, not by Sales or Operations individually. Once approved in Step 2, it is the single authoritative demand signal for all downstream planning.
2. **Step-Gate Completion** — Each step must be formally signed off before the cycle advances. `advanceCycleStep()` validates completion criteria (attendance, gap resolution %) before allowing state transition.
3. **Gap Resolution Target** — ≥ 80 % of identified demand-supply gaps must be resolved at Pre-S&OP (Step 4) before the Executive S&OP (Step 5). Remaining gaps are escalated with clear owner and resolution date.
4. **24-Month Rolling Horizon** — The S&OP plan always extends 24 months forward (rolling). Months 1–3 are firm commitments; months 4–24 are indicative and updated monthly.
5. **Financial Reconciliation Required** — The financial bridge (Step 4) must show that `Revenue_plan ≥ Budget × 0.95` or a corrective action plan must accompany the Executive S&OP package.
6. **One Number Principle** — All departments (Sales, Operations, Finance, SC) work from a single consensus forecast. Shadow forecasts are prohibited after Step 2 approval.

---

## 4. Mathematical Models

### 4.1 Consensus Forecast — Weighted Combination

```
F_consensus = w_statistical × F_statistical
            + w_market      × F_market
            + w_sales       × F_sales

Constraint: w_statistical + w_market + w_sales = 1.0

Weights determined by historical MAPE per source:
  w_i = (1 / MAPE_i) / Σ (1 / MAPE_j)     (inverse-error weighting)

Lower MAPE → higher weight → better forecasters earn more influence
```

Reference: Mentzer, J.T. & Moon, M.A., *Sales Forecasting Management* 2nd Ed., 2005.

### 4.2 Rough Cut Capacity Planning (RCCP)

```
Load_resource_r_period_t = Σ_i (MPS_qty_i_t × hours_per_unit_i_r)

where:
  MPS_qty_i_t   = Master Production Schedule quantity for SKU i in period t
  hours_per_unit_i_r = standard hours on resource r to produce one unit of SKU i

Capacity_available_r_t = Planned_shifts × Hours_per_shift × OEE_factor

Gap: Load > Capacity → schedule adjustment, overtime, or outsource
```

RCCP runs after Step 2 (Demand Review) to validate supply feasibility before Step 3 (Supply Review). Reference: APICS CPIM 9.0.

### 4.3 Inventory Target Setting

```
Target_inventory_i = Safety_stock_i + Cycle_stock_i

Safety_stock_i  = z × σ_D_i × √LT_i            (Method 3; Chopra & Meindl Ch.11)
Cycle_stock_i   = EOQ_i / 2
EOQ_i           = √(2 × D_i × S_i / H_i)

Aggregate target: Target_WH = Σ_i (Target_inventory_i × Unit_cost_i)
vs.               Actual_inventory (from Dept. 05)

Gap = Actual − Target  → excess if positive; shortage if negative
```

### 4.4 Financial Bridge — Revenue Reconciliation

```
Revenue_plan = Σ_i (F_consensus_i × Selling_price_i)

COGS_plan    = Σ_i (F_consensus_i × Standard_cost_i)

Gross_margin_plan = (Revenue_plan − COGS_plan) / Revenue_plan × 100

Gap_to_budget = Revenue_plan − Budget_revenue

Gap > 0  → upside scenario
Gap < 0  → corrective action required (demand stimulation, pricing, cost reduction)
```

### 4.5 Plan Attainment (PA)

```
PA% = Actual_output / MPS_planned_output × 100

Target: PA% ≥ 95 %
< 90 % → root cause analysis mandatory in next Supply Review
< 80 % → escalation to Executive S&OP with corrective plan
```

---

## 5. Recommended ML Models

### 5.1 Hierarchical Forecasting — MinT Reconciliation

Reconciles forecasts across the product hierarchy (SKU → Product Family → Category → Total Business) using the Minimum Trace (MinT) reconciliation method. Ensures that bottom-up SKU forecasts sum to top-down category and total business forecasts consistently, eliminating the "two sets of books" problem.

- **Libraries**: `statsforecast`, `hierarchicalforecast` (Nixtla)
- **Reference**: Hyndman, R.J. et al., "Optimal combination forecasts for hierarchical time series," *Computational Statistics & Data Analysis* 55(9), 2011.

### 5.2 Monte Carlo Scenario Planning — P10/P50/P90

Simulates 10 000+ demand and supply scenarios by sampling from (demand uncertainty, capacity uncertainty, supplier lead-time variability) distributions. Produces P10/P50/P90 revenue and inventory outcome distributions for the Executive S&OP risk discussion.

- **Libraries**: `NumPy`, `SciPy`
- **Output**: Distribution table presented in Executive S&OP deck; CFO approves P50 as operating plan with P10/P90 as risk bounds

### 5.3 ML Ensemble — Optimised Consensus Weights

Machine learning ensemble that dynamically adjusts consensus forecast weights by source (statistical, market intelligence, sales override) based on rolling cross-validation accuracy. Weights updated monthly after Step 1 actuals are loaded.

- **Libraries**: `scikit-learn`, `statsforecast`, LightGBM base learners
- **Benefit**: Prevents sales team from systematically over-riding statistical forecast without accountability

### 5.4 NLP — Market Intelligence Signal Extraction

Scrapes earnings call transcripts, analyst reports, retail POS commentary, and customer CRM notes. Extracts forward-looking demand signals (product sentiment, promotional intent, competitive launches) to adjust statistical forecast before Step 2 demand review meeting.

- **Libraries**: HuggingFace transformers (FinBERT variant), SEC EDGAR API, CRM API connector

### 5.5 Digital Twin — S&OP What-If Simulation

End-to-end supply chain digital twin that simulates the full impact of what-if scenarios before the Executive S&OP session: new product launches, major customer wins/losses, supplier disruptions, capacity expansion decisions. Each scenario produces a fully costed P&L impact within minutes.

- **Libraries / Platforms**: SimPy (Python discrete-event simulation), AnyLogic (commercial)
- **Use case**: "What happens to Gross Margin if Supplier X fails and we switch to Supplier Y at 8 % cost premium?"

---

## 6. KPIs & Thresholds

| KPI | Formula | Target | Alert |
|---|---|---|---|
| Forecast Accuracy (MAPE at family level, M+1) | `Mean(|Actual − Forecast| / Actual) × 100` | MAPE < 10 % | > 20 % |
| Plan Attainment % | `Actual output / MPS planned × 100` | ≥ 95 % | < 85 % |
| Inventory vs. Target | `Actual WH value / Target WH value` | 90–110 % | < 80 % or > 120 % |
| Revenue vs. Plan % | `|Actual Revenue − Plan Revenue| / Plan Revenue × 100` | ≤ 5 % deviation | > 10 % |
| Gap Resolution Rate | `Gaps resolved in Pre-S&OP / Total gaps × 100` | ≥ 80 % | < 60 % |
| S&OP Cycle Adherence | `Steps completed on schedule / 5 steps × 100` | 100 % | Any step missed |
| Executive S&OP Attendance | Key stakeholders present | 100 % C-suite | < 80 % |

---

## 7. S&OP vs IBP Comparison

| Dimension | S&OP (Traditional) | IBP (Integrated Business Planning) |
|---|---|---|
| **Planning horizon** | 6–12 months | 24–36 months rolling |
| **Granularity** | Product family | SKU / customer in near-term |
| **Financial integration** | Operational only | Full P&L, balance sheet, cash flow |
| **Frequency** | Monthly cycle | Monthly cycle + weekly tactical reviews |
| **Technology** | Spreadsheets / ERP | IBP platform (SAP IBP, Kinaxis Maestro) |
| **Ownership** | SC / Operations | Cross-functional: CEO sponsors |
| **Scenario depth** | 2–3 scenarios | P10/P50/P90 + digital twin |

Target state: **IBP** implementation within 18 months, using SAP IBP or equivalent platform.

---

## 8. Integration Points

| Department | Data Flow |
|---|---|
| **03 Demand Planning** | Statistical forecast output (SMA/SES/Holt-Winters) is the baseline for Step 2 |
| **04 Supply Planning** | MPS and capacity constraints validated in Step 3 (Supply Review) |
| **05 Inventory Management** | Actual vs. target inventory gap reviewed in Step 3; safety stock targets set here |
| **11 Finance & Controlling** | Financial bridge built in Step 4; revenue and margin reconciliation |
| **10 Risk Management** | P10 scenarios incorporate risk events from the Risk Register (HHI, BCP) |

---

## 9. Roles

| Role | Responsibility |
|---|---|
| **S&OP / IBP Manager** | Process facilitator; owns the cycle calendar; drives cross-functional alignment |
| **Demand Planning Lead** | Statistical forecast baseline; consensus forecast coordination (Dept. 03 liaison) |
| **Supply Planning Lead** | Capacity validation; supply gap identification and mitigation (Dept. 04 liaison) |
| **Finance Business Partner** | Financial bridge; P&L translation; gap-to-budget analysis |
| **S&OP Analyst** | Data preparation (Step 1); KPI reporting; scenario modelling |

---

## 10. References

1. Wallace, T.F., **Sales and Operations Planning: The How-To Handbook** 3rd Ed., T.F. Wallace & Company, 2004.
2. Palmatier, G. & Crum, C., **Enterprise Sales and Operations Planning**, J. Ross Publishing, 2003.
3. APICS / ASCM, **CPIM 9.0 Exam Content Manual** — Integrated Resource Management, 2024.
4. Hyndman, R.J. et al., "Optimal combination forecasts for hierarchical time series," *Computational Statistics & Data Analysis* 55(9):2579–2589, 2011.
5. Oliver Wight International, **Class A Checklist for Business Excellence** 7th Ed. — S&OP / IBP criteria, 2017.
