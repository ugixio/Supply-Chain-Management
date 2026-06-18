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
