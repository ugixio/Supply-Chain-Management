# Departamento 05 — Inventory Management
## Gestión de Inventarios

### Misión
Mantener niveles de inventario óptimos que maximicen el nivel de servicio al cliente
mientras minimizan el capital de trabajo y los costos de obsolescencia.

### Funciones principales
| Función | Descripción |
|---------|-------------|
| Control de inventarios | Registro de todos los movimientos (event-sourced) |
| Clasificación ABC-XYZ | Priorización de SKUs por valor y variabilidad |
| Gestión de lotes/series | Trazabilidad completa — FEFO para productos regulados |
| Conciliación de inventarios | Ciclos de conteo, ajustes GL |
| Inventario en tránsito | Seguimiento goods-in-transit |
| Gestión de obsoletos | Identificación y disposición de slow-movers |

### KPIs del departamento
| KPI | Fórmula | Benchmark |
|-----|---------|-----------|
| Inventory Accuracy | Conteo físico / Sistema | ≥ 99.5% |
| Inventory Turnover | COGS / Inventario promedio | ≥ 8-12× (FMCG) |
| Days Inventory Outstanding (DIO) | 365 / Turnover | < 45 días |
| Slow-Mover % | SKUs sin movimiento 90d | < 5% |
| Obsolescence Write-off | Ajustes negativos / Inventario | < 1% |
| Fill Rate | Órdenes cumplidas sin backorder | ≥ 98% |

### Matriz ABC-XYZ (9 casillas)
|  | X (CV<10%) | Y (CV 10-25%) | Z (CV>25%) |
|--|-----------|--------------|-----------|
| **A** | MRP continuo + bajo SS | MRP + buffer medio | Min-Max + alto SS |
| **B** | Revisión semanal | Revisión semanal + buffer | Min-Max |
| **C** | Revisión mensual | Two-bin/Kanban | Consignación |

### Arquitectura event-sourced
```
StockMovement (inmutable append-only)
  ├── GOODS_RECEIPT      → débito 1300/crédito 1310
  ├── GOODS_ISSUE        → débito 5000/crédito 1300
  ├── SCRAP              → débito 5200/crédito 1300
  ├── PRODUCTION_INPUT   → débito 1320/crédito 1300
  └── INVENTORY_ADJ_*    → débito/crédito 5100

projectStockBalance(movements[]) → Map<sku::warehouse, qty>
```

### Archivos clave
- `domain/InventoryItem.ts` — Maestro de artículos con ABC-XYZ, EOQ, REACH
- `domain/StockMovement.ts` — Log event-sourced, doble entrada GL
- `domain/LotRecord.ts` — Maestro de lotes con fechas de vencimiento
- `services/ABCAnalysis.ts` — Reclasificación periódica ABC-XYZ
- `services/SlowMoverReport.ts` — Identificación de artículos sin movimiento
- `services/CycleCountScheduler.ts` — Programación de conteos cíclicos

### Reglas de negocio críticas
1. **Nunca inventario negativo** sin `backorderAllowed = true`
2. **Idempotencia**: `idempotencyKey` en cada movimiento
3. **Soft-delete**: ningún movimiento se elimina (solo se ajusta)
4. **Journal entry**: todo movimiento genera asiento contable
5. **Lot tracking**: obligatorio si `storageCondition !== AMBIENT`

### Roles del departamento
- **Inventory Manager** — Control y estrategia global
- **Inventory Controller** — Supervisión diaria de exactitud
- **Inventory Analyst** — ABC-XYZ, slow-movers, reporting
- **Cycle Count Coordinator** — Planificación y ejecución de conteos

### Referencias
- Chopra & Meindl Ch.11 "Managing Uncertainty — Safety Inventory"
- Silver, Pyke & Peterson "Inventory Management" (1998)
- APICS CPIM 9.0 — Inventory Management module
- GS1 Global Traceability Standard 2.0
