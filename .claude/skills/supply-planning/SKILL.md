---
description: >
  Supply planning domain expertise for Department 04. Use when reviewing MRP/MPS,
  capacity planning, SIOP, demand signal quality, or the concept nodes and rules of department 04 (supply-planning).
---

# Supply Planning — Department 04 Skills Reference

## Supply Chain Domain

**SCOR-DS Mapping**: Plan (P2 — Plan Source, P3 — Plan Make, P4 — Plan Deliver)

**Core Planning Concepts (APICS CPIM 9.0)**
| Concept | Definition |
|---------|-----------|
| MPS — Master Production Schedule | Time-phased plan of end items; drives MRP |
| MRP — Material Requirements Planning | Netting of demand vs. supply; generates planned orders |
| CRP — Capacity Requirements Planning | Verifies resource availability against MPS |
| SIOP / S&OP | Sales, Inventory & Operations Planning — monthly alignment meeting |
| Planning Horizon | Minimum: cumulative lead time of longest-lead item |
| Time Fences | Demand Fence (frozen), Planning Fence (firm), Beyond Fence (tentative) |

**Supply-planning metrics (APICS, SCOR-DS)**

**Metrics — definitions, not levels.** A skill states what a metric measures and what
constrains the answer; the level a project must clear is that project's decision (ADR-0037,
and the inclusion test in `CLAUDE.md`). The right-hand column names the constraint so the
question can be asked properly, and stops.

| Metric | Formula | What constrains the level |
|---|---|---|
| Schedule adherence | Planned orders executed on time / Total × 100 | The frozen-horizon policy. Adherence measured against a plan that is still being revised measures the revisions (CPT-0150). |
| MPS stability | Unchanged MPS lines / Total × 100 | The same frozen horizon, plus the demand's own volatility. The index is bounded at 1 by construction (CPT-0146). |
| Capacity utilization | Actual output / Planned capacity × 100 | **Queueing theory, which is the interesting constraint:** wait time rises non-linearly as utilization approaches 1, so the useful level is well below 100% and follows from variability and the acceptable queue — not from a convention. Little's Law (`L = λW`) is the tool. |
| Bullwhip ratio | Var(orders) / Var(demand) | **An identity, not a target:** 1.0 means variability passes through unamplified, above 1 the chain amplifies it. What amplification a project tolerates is its decision (CPT-0070). |
| Demand signal quality | SCOR-DS RL.2.3 | SCOR fixes the measure; the level follows the channel. |

**Bullwhip Effect** (Lee, Padmanabhan & Whang 1997)
```
Bullwhip Ratio = Var(Order Quantities) / Var(End-Customer Demand)
```
A ratio of 1 means variability passes through unamplified. Above 1 the chain amplifies it;
where that becomes worth acting on is a project decision.

**Net Requirements Formula (MRP)**
```
Net Requirement = Gross Requirement − Projected On-Hand − Scheduled Receipts
Planned Order Release = Net Requirement + Safety Stock − Excess On-Hand
```

## Data Analytics

**Supply Plan vs. Demand Comparison**
```sql
SELECT period, sku_id,
       consensus_forecast AS demand_plan,
       planned_production_qty + scheduled_receipt_qty AS supply_plan,
       (planned_production_qty + scheduled_receipt_qty) - consensus_forecast AS supply_surplus
FROM supply_demand_matrix
WHERE period BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '6 months'
ORDER BY ABS(supply_surplus) DESC;
```

**Bullwhip Ratio by SKU**
```sql
WITH demand_stats AS (
  SELECT sku_id,
         VARIANCE(demand_qty) AS var_demand
  FROM demand_actuals GROUP BY sku_id
),
order_stats AS (
  SELECT sku_id,
         VARIANCE(ordered_qty) AS var_orders
  FROM purchase_orders GROUP BY sku_id
)
SELECT d.sku_id,
       ROUND(o.var_orders / NULLIF(d.var_demand, 0), 3) AS bullwhip_ratio
FROM demand_stats d JOIN order_stats o USING (sku_id)
ORDER BY bullwhip_ratio DESC;
```

**Capacity Bottleneck Identification**
```sql
SELECT work_center_id, period,
       SUM(planned_hours) AS planned_hours,
       available_hours,
       ROUND(SUM(planned_hours) / NULLIF(available_hours, 0) * 100, 1) AS utilization_pct,
       CASE WHEN SUM(planned_hours) > available_hours THEN 'OVERLOADED' ELSE 'OK' END AS status
FROM production_plan p JOIN work_center_capacity c USING (work_center_id, period)
GROUP BY work_center_id, period, available_hours
ORDER BY utilization_pct DESC;
```

## Data Science

**Inventory Optimization (Multi-Echelon)**
- Problem: allocate stock across DC + regional warehouses to minimize total cost
- Method: stochastic dynamic programming or LP relaxation
- Reference: Graves & Willems (2000), *Management Science* 46(11)

**Demand Amplification Mitigation**
- Order Smoothing: `Order_t = α × Net_Req_t + (1−α) × Order_{t-1}`
- Information Sharing: integrate POS data to bypass retailer ordering variance
- VMI (Vendor Managed Inventory): supplier controls replenishment; reduces bullwhip

**Constraint-Based Planning (Theory of Constraints)**
- Identify: bottleneck work center (highest utilization)
- Exploit: maximize throughput at the constraint (no idle time)
- Subordinate: all other resources feed the constraint
- Elevate: invest to increase constraint capacity

## Machine Learning

**Demand Signal Smoothing (Kalman Filter)**
```python
from filterpy.kalman import KalmanFilter
import numpy as np

def smooth_demand_signal(demand: np.ndarray) -> np.ndarray:
    """
    Kalman filter to reduce demand signal noise before MPS generation.
    Reduces bullwhip amplification. Ref: Welch & Bishop (1995), UNC Tech Report.
    """
    kf = KalmanFilter(dim_x=2, dim_z=1)
    kf.x = np.array([[demand[0]], [0.]])          # initial state
    kf.F = np.array([[1., 1.], [0., 1.]])          # state transition
    kf.H = np.array([[1., 0.]])                    # measurement
    kf.P *= 1000.; kf.R = 5.; kf.Q = 0.01
    smoothed = []
    for z in demand:
        kf.predict(); kf.update([[z]])
        smoothed.append(float(kf.x[0]))
    return np.array(smoothed)
```

**Capacity Planning with Reinforcement Learning**
```python
from stable_baselines3 import PPO
import gymnasium as gym

# RL agent learns optimal production scheduling policy
# State: backlog, inventory, capacity, demand forecast
# Action: production quantity per period
# Reward: -cost (holding + backorder + changeover)
# Ref: Silver et al. (2016) — AlphaGo; adapted to scheduling
# License: stable-baselines3 MIT
```

**Constraint Optimization (OR-Tools)**
```python
from ortools.sat.python import cp_model

def solve_production_schedule(demands: list[int], capacity: list[int],
                               holding_cost: int, backorder_cost: int) -> list[int]:
    """
    CP-SAT solver for production scheduling.
    Minimizes total holding + backorder costs over planning horizon.
    Ref: Google OR-Tools (Apache-2.0).
    """
    model = cp_model.CpModel()
    T = len(demands)
    production = [model.NewIntVar(0, capacity[t], f'prod_{t}') for t in range(T)]
    inventory = [model.NewIntVar(0, 10000, f'inv_{t}') for t in range(T)]
    # Inventory balance constraint
    for t in range(T):
        prev_inv = inventory[t-1] if t > 0 else 0
        model.Add(inventory[t] == prev_inv + production[t] - demands[t])
    # Minimize cost
    total_cost = sum(holding_cost * inventory[t] for t in range(T))
    model.Minimize(total_cost)
    solver = cp_model.CpSolver()
    solver.Solve(model)
    return [solver.Value(production[t]) for t in range(T)]
```

## Python

| Library | Use | License |
|---------|-----|---------|
| `pandas` | Supply-demand matrix, MPS DataFrames | BSD-3 |
| `numpy` | Net requirements, array operations | BSD-3 |
| `scipy.optimize` | LP relaxation, EOQ variants | BSD-3 |
| `pulp` | Multi-period production LP | MIT |
| `ortools` | CP-SAT for scheduling, VRP | Apache-2.0 |
| `stable-baselines3` | RL for adaptive production policy | MIT |
| `networkx` | Supply network graph, critical path | BSD-3 |
| `simpy` | Discrete event simulation of supply plan | MIT |

## TypeScript

**Domain Objects**
- `domain/MasterProductionSchedule.ts` — MPS aggregate; time fences; freeze logic
- `domain/MaterialRequirement.ts` — MRP netting; planned order release
- `domain/CapacityPlan.ts` — CRP; work center utilization; bottleneck flags
- `services/SIOPService.ts` — S&OP alignment; consensus commit

**MRP Netting**
```typescript
function computeNetRequirement(
  grossRequirement: number,
  projectedOnHand: number,
  scheduledReceipts: number,
  safetyStock: number
): number {
  const available = projectedOnHand + scheduledReceipts;
  const net = grossRequirement + safetyStock - available;
  return Math.max(0, net);  // net requirement cannot be negative
}
```

## OSI / Commercial

| Tool | License | Use |
|------|---------|-----|
| PostgreSQL | PostgreSQL (OSI) | Supply plan, MPS tables |
| Apache Airflow | Apache-2.0 | Weekly MRP run pipeline |
| Apache Superset | Apache-2.0 | Supply-demand gap dashboards |
| `ortools` | Apache-2.0 | Constraint-based scheduling |
| `simpy` | MIT | Supply chain digital twin |

**References**
- APICS CPIM 9.0 — Module 5: Master Planning of Resources
- Chopra & Meindl, Ch.8 — Aggregate Planning (Pearson, 2016)
- Lee, H.L., Padmanabhan, V. & Whang, S. (1997). "The Bullwhip Effect in Supply Chains." *Sloan Management Review* 38(3).
- Graves, S.C. & Willems, S.P. (2000). "Optimizing Strategic Safety Stock Placement." *Management Science* 46(11).
- Wallace, T.F. & Stahl, R.A. (2008). *Sales and Operations Planning*, 3rd ed.
- APICS/ASCM Dictionary, 17th ed. (2024) — *MPS*, *MRP*, *CRP*, *bullwhip effect*
