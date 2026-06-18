# Departamento 04 — Supply Planning & Production Scheduling
## Planificación del Suministro y Programación de Producción

### Misión
Traducir el plan de demanda en un plan de suministro ejecutable que equilibre
disponibilidad de materiales, capacidad productiva y objetivos de servicio al cliente.

### Funciones principales
| Función | Descripción |
|---------|-------------|
| MRP (Materials Requirements Planning) | Explosión de BOM, fechas de necesidad |
| MPS (Master Production Schedule) | Plan maestro por producto terminado |
| Planificación de capacidad | CRP (Capacity Requirements Planning) |
| Gestión de materiales | Compras urgentes, transferencias |
| S&OP Supply side | Input a la reunión mensual de S&OP |
| DDMRP | Demand-Driven MRP (posicionamiento de buffers) |

### KPIs del departamento
| KPI | Benchmark mundial |
|-----|------------------|
| Plan Adherence Rate | ≥ 85% |
| Schedule Stability (cambios < 24h) | < 10% de órdenes |
| Capacity Utilization | 75-85% (óptimo) |
| Material Availability Rate | ≥ 98% |
| Lead Time Achievement | ≥ 95% |
| Setup Time Efficiency | Varía por industria |

### Proceso MRP simplificado
```
MPS (productos terminados)
  ↓ Explosión de BOM (lista de materiales)
  ↓ MRP (necesidades brutas → netas)
  ↓ Netting (stock disponible + pedidos abiertos)
  ↓ Firm Planned Orders → POs al módulo Procurement
```

### Archivos clave
- `domain/ProductionPlan.ts` — MPS y plan de producción
- `domain/MaterialRequirement.ts` — MRP: necesidades de materiales
- `domain/CapacityPlan.ts` — CRP: planificación de capacidad
- `domain/BillOfMaterials.ts` — Estructura de materiales (BOM)
- `services/MRPEngine.ts` — Motor de cálculo MRP
- `services/CapacityPlanner.ts` — Cálculo CRP y RCCP

### Roles del departamento
- **Supply Planning Manager** — Director del proceso MRP/S&OP
- **Production Scheduler** — Programación diaria de manufactura
- **Materials Planner** — Gestión MRP y órdenes planificadas
- **Capacity Planner** — CRP y restricciones de capacidad
- **DDMRP Specialist** — Implementación demand-driven

### Referencias
- Chopra & Meindl Ch.10 "Coordinating Supply and Demand"
- APICS CPIM 9.0 — Plan Supply & Master Scheduling modules
- Orlicky, J. "Material Requirements Planning" (2022 3rd Ed.)
- Ptak & Smith "Demand Driven Material Requirements Planning" (2016)

## Modelos Matemáticos Aplicados

1. **MRP Netting** — Net_Req_t = max(0, Gross_Req_t - Scheduled_Receipts_t - On_Hand_{t-1}). Converts gross demand into net requirements after available inventory. Ref: Orlicky (2022).

2. **Lot Sizing — Lot-for-Lot (L4L)** — Order exactly what is needed each period. Minimizes inventory, maximizes orders. Best for expensive/perishable items.

3. **Lot Sizing — EOQ Fixed** — Uses EOQ formula: Q* = √(2DS/H). Applied when demand is roughly stable across MRP buckets. Ref: Harris (1913).

4. **Lot Sizing — Part Period Balancing (PPB)** — Accumulate periods until holding cost ≈ ordering cost (Economic Part Period). Dynamic lot sizing. Ref: Silver et al. (1998).

5. **MPS Stability Index** — SI = 1 - (Σ|MPS_revised - MPS_original| / Σ MPS_original). Measures nervousness of master schedule. Target: SI > 0.85. Ref: APICS CPIM.

6. **Planned Order Release with Lead Time Offset** — Release_date = Need_date - Lead_time_periods. Core MRP time-phasing logic. Ref: Orlicky (2022) Ch.4.

## Modelos de Machine Learning Recomendados

1. **Reinforcement Learning para Dynamic Lot Sizing** — Agent observes (inventory, demand forecast, holding cost, setup cost) and decides order quantity each period. Learns policy that minimizes total cost over horizon. Libraries: Ray RLlib. Ref: Oroojlooy et al. (2022).

2. **Graph Neural Networks para BOM Explosion** — Models multi-level Bill of Materials as directed acyclic graph. Propagates demand signals through component levels considering shared parts. Libraries: PyTorch Geometric.

3. **Monte Carlo Simulation para MPS Risk** — Simulates 10,000 scenarios of demand variability and supplier lead time distributions. Outputs P90 material requirement for robust planning. Libraries: NumPy, SciPy.

4. **XGBoost para Predicción de Capacidad** — Predicts bottleneck workstations given MPS. Features: historical throughput, maintenance schedule, shift patterns. Output: capacity utilization forecast. Libraries: XGBoost.

5. **Linear Programming para Optimización de Plan Maestro** — Minimize: Σ(holding_cost×I_t + setup_cost×Y_t + backorder_cost×B_t). Subject to: inventory balance, capacity constraints, demand satisfaction. Libraries: PuLP, scipy.optimize, Google OR-Tools. Ref: Nahmias (2009).
