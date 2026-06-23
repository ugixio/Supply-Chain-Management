# Department 04 — Supply Planning & Production Scheduling
## Supply Planning and Production Scheduling

### Mission
Translate the demand plan into an executable supply plan that balances
material availability, production capacity, and customer service objectives.

### Main Functions
| Function | Description |
|---------|-------------|
| MRP (Materials Requirements Planning) | BOM explosion, requirement dates |
| MPS (Master Production Schedule) | Master plan per finished product |
| Capacity planning | CRP (Capacity Requirements Planning) |
| Materials management | Expedited purchasing, transfers |
| S&OP Supply side | Input to the monthly S&OP meeting |
| DDMRP | Demand-Driven MRP (buffer positioning) |

### Department KPIs
| KPI | World Benchmark |
|-----|------------------|
| Plan Adherence Rate | ≥ 85% |
| Schedule Stability (changes < 24h) | < 10% of orders |
| Capacity Utilization | 75-85% (optimal) |
| Material Availability Rate | ≥ 98% |
| Lead Time Achievement | ≥ 95% |
| Setup Time Efficiency | Varies by industry |
| Order Entry Accuracy — Demand Signal (SCOR RL.2.3) | ≥ 99% (EDI); ≥ 97% (manual) |

### Simplified MRP Process
```
MPS (finished products)
  ↓ BOM explosion (bill of materials)
  ↓ MRP (gross → net requirements)
  ↓ Netting (available stock + open orders)
  ↓ Firm Planned Orders → POs to Procurement module
```

### Key Files
- `domain/ProductionPlan.ts` — MPS and production plan
- `domain/MaterialRequirement.ts` — MRP: material requirements
- `domain/CapacityPlan.ts` — CRP: capacity planning
- `domain/BillOfMaterials.ts` — Bill of Materials structure (BOM)
- `services/MRPEngine.ts` — MRP calculation engine
- `services/CapacityPlanner.ts` — CRP and RCCP calculation

### Department Roles
- **Supply Planning Manager** — Director of the MRP/S&OP process
- **Production Scheduler** — Daily manufacturing scheduling
- **Materials Planner** — MRP management and planned orders
- **Capacity Planner** — CRP and capacity constraints
- **DDMRP Specialist** — Demand-driven implementation

### References
- Chopra & Meindl Ch.10 "Coordinating Supply and Demand"
- APICS CPIM 9.0 — Plan Supply & Master Scheduling modules
- Orlicky, J. "Material Requirements Planning" (2022 3rd Ed.)
- Ptak & Smith "Demand Driven Material Requirements Planning" (2016)

## Applied Mathematical Models

1. **MRP Netting** — Net_Req_t = max(0, Gross_Req_t - Scheduled_Receipts_t - On_Hand_{t-1}). Converts gross demand into net requirements after available inventory. Ref: Orlicky (2022).

2. **Lot Sizing — Lot-for-Lot (L4L)** — Order exactly what is needed each period. Minimizes inventory, maximizes orders. Best for expensive/perishable items.

3. **Lot Sizing — EOQ Fixed** — Uses EOQ formula: Q* = √(2DS/H). Applied when demand is roughly stable across MRP buckets. Ref: Harris (1913).

4. **Lot Sizing — Part Period Balancing (PPB)** — Accumulate periods until holding cost ≈ ordering cost (Economic Part Period). Dynamic lot sizing. Ref: Silver et al. (1998).

5. **MPS Stability Index** — SI = 1 - (Σ|MPS_revised - MPS_original| / Σ MPS_original). Measures nervousness of master schedule. Target: SI > 0.85. Ref: APICS CPIM.

6. **Planned Order Release with Lead Time Offset** — Release_date = Need_date - Lead_time_periods. Core MRP time-phasing logic. Ref: Orlicky (2022) Ch.4.

## Recommended Machine Learning Models

1. **Reinforcement Learning for Dynamic Lot Sizing** — Agent observes (inventory, demand forecast, holding cost, setup cost) and decides order quantity each period. Learns policy that minimizes total cost over horizon. Libraries: Ray RLlib. Ref: Oroojlooy et al. (2022).

2. **Graph Neural Networks for BOM Explosion** — Models multi-level Bill of Materials as directed acyclic graph. Propagates demand signals through component levels considering shared parts. Libraries: PyTorch Geometric.

3. **Monte Carlo Simulation for MPS Risk** — Simulates 10,000 scenarios of demand variability and supplier lead time distributions. Outputs P90 material requirement for robust planning. Libraries: NumPy, SciPy.

4. **XGBoost for Capacity Prediction** — Predicts bottleneck workstations given MPS. Features: historical throughput, maintenance schedule, shift patterns. Output: capacity utilization forecast. Libraries: XGBoost.

5. **Linear Programming for Master Plan Optimization** — Minimize: Σ(holding_cost×I_t + setup_cost×Y_t + backorder_cost×B_t). Subject to: inventory balance, capacity constraints, demand satisfaction. Libraries: PuLP, scipy.optimize, Google OR-Tools. Ref: Nahmias (2009).
