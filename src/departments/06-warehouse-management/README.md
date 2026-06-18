# Departamento 06 — Warehouse Management (WMS)
## Gestión de Almacenes

### Misión
Ejecutar con excelencia operativa todas las actividades de recepción, almacenamiento,
preparación de pedidos y despacho, maximizando la productividad del personal y la
exactitud de inventario en cada instalación.

### Funciones principales
| Función | Descripción |
|---------|-------------|
| Recepción (Inbound) | Descarga, verificación, put-away según slotting |
| Almacenamiento | Gestión de ubicaciones, FEFO, cross-docking |
| Preparación de pedidos | Picking por wave, batch o discreta |
| Empaque y etiquetado | Packing, GS1 labels, SSCC |
| Despacho (Outbound) | Carga, manifiestos, ASN a compradores |
| Conteos cíclicos | Verificación continua de exactitud |
| Gestión de devoluciones | Returns processing, disposición |

### KPIs del departamento
| KPI | Benchmark |
|-----|-----------|
| Picking Accuracy | ≥ 99.9% |
| On-Time Shipping | ≥ 98% |
| Warehouse Utilization | 80-85% |
| Labor Productivity | Líneas/hora vs target |
| Receiving Accuracy | ≥ 99.5% |
| Dock-to-Stock Time | < 4 horas |
| Safety Incidents | 0 LTI (meta) |
| Inventory Accuracy (bin level) | ≥ 99.5% |

### Algoritmos de slotting implementados
**1. ABC Velocity Slotting**
- A items (50% de picks) → Zona dorada (< 10 m del muelle)
- B items (25% de picks) → Zona plata (10-25 m)
- C items (25% de picks) → Zona bronce (> 25 m)
- Beneficio esperado: **10-20% reducción costo laboral**

**2. CPOI (Cube-Per-Order-Index)**
```
CPOI = Volumen (m³) / Líneas de pedido por período
```
- Menor CPOI → mejor ubicación (más picks por m³)
- Optimiza simultáneamente espacio y distancia de picking

**3. FEFO (First Expired First Out)**
- Obligatorio para farmacéuticos, alimentos, cosméticos
- Sistema ordena lotes por fecha de vencimiento ascendente
- GS1 AI (17) en etiquetas para captura automática de expiry

### Jerarquía de ubicaciones
```
Almacén (GLN) → Zona → Pasillo → Bahía → Nivel → Bin
   WH-MEX-001    A      A-01     A-01-02   B    A-01-02-B
```

### Tipos de almacén soportados
- DISTRIBUTION_CENTER — distribución general
- MANUFACTURING_STORE — punto de uso en planta
- BONDED — almacén fiscal/aduanal
- CROSS_DOCK — sin almacenamiento, solo transferencia
- COLD_STORAGE — cadena de frío (2-8°C o -18°C)
- HAZMAT — mercancías peligrosas IMDG/ADR

### Archivos clave
- `domain/Warehouse.ts` — Maestro de almacenes y ubicaciones
- `domain/PickingWave.ts` — Agrupación de órdenes para picking eficiente
- `domain/PutAwayRule.ts` — Reglas de almacenamiento por tipo de producto
- `domain/CrossDock.ts` — Gestión de cross-docking
- `services/SlottingEngine.ts` — Motor de slotting ABC-CPOI
- `services/FEFOPicking.ts` — Lógica de picking FEFO/FIFO
- `services/CycleCount.ts` — Programación y ejecución de conteos
- `operations/ReceivingFlow.ts` — Flujo completo de recepción

### Roles del departamento
- **Warehouse Manager** — Dirección operativa y KPIs
- **Inbound Supervisor** — Recepción y put-away
- **Outbound Supervisor** — Picking, packing y despacho
- **Inventory Controller (WMS)** — Exactitud y conciliación
- **Slotting Analyst** — Optimización de ubicaciones
- **WMS Administrator** — Sistema WMS y configuración

### Referencias
- Frazelle, E.H. "World-Class Warehousing and Material Handling" (2002)
- Chopra & Meindl Ch.13 — Warehouse and distribution
- APICS CPIM 9.0 — Warehouse operations
- GS1 General Specifications v23.0 — SSCC, labels
