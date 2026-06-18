# 06 — Warehouse Management (WMS)

## Overview

Gestiona la operación física de almacenes: estructura de ubicaciones (zona→pasillo→rack→bin), recepción, slotting, picking (FEFO), y despacho. Implementa **CPOI slotting** para minimizar distancia de recorrido y **FEFO** para cumplimiento de vida útil en alimentos y farmacéutica.

---

## KPIs del Departamento

| KPI | Benchmark | Fuente |
|-----|-----------|--------|
| Pick Accuracy % | ≥ 99.9% | Frazelle (2002) |
| Líneas pickeadas/hora | 80-120 manual; 200-400 RF/voz | Frazelle (2002) |
| Storage Utilization % | 85% óptimo | Interno |
| FEFO Compliance % | 100% | Regulatorio (farma/alimentos) |
| Dock-to-Stock Time | < 2 horas (A-items) | Benchmark WMS |
| Order Cycle Time | < 24h B2B | Christopher (2022) |

---

## Estándares

| Estándar | Alcance |
|----------|---------|
| GS1 Gen. Specs. v23.0 | SSCC, GLN, GS1-128 labels |
| ISO 28000:2022 | Seguridad física de almacén |
| GMP (FDA 21 CFR Part 211) | Farma: temperatura, FEFO |
| HACCP | Alimentos: control de temperatura |

---

## Archivos del Departamento

| Archivo | Responsabilidad |
|---------|----------------|
| `domain/Warehouse.ts` | WarehouseType, WarehouseLocation (4 niveles), fefoSort(), calculateSlotting() CPOI, SlottingInput/Recommendation, LotAvailability |

---

## Modelos Matemáticos Aplicados

### 1. FEFO — First Expired First Out

```
Priority(lot_i) = expiryDate_i  (orden ascendente)
Pick lot con min(expiryDate) primero
```

Garantiza cero despacho de productos vencidos. Obligatorio en farma (FDA), alimentos (HACCP), y cualquier item con `shelfLifeDays` definido.

### 2. CPOI — Cube Per Order Index

```
CPOI_i = Volume_i (cm³) / Orders_containing_item_i (mes)

Menor CPOI → ubicación más cercana a despacho (golden zone)
```

Minimiza distancia recorrida para ítems de alto volumen de picking. Ref: Frazelle (2002) *World-Class Warehousing and Material Handling*.

### 3. ABC Velocity Slotting

```
Pick_frequency_i = Orders_per_month_i

A-items (top 80% picks) → Zona Primaria (floor level, near dock)
B-items (15%)           → Zona Secundaria (mid-height)
C-items (5%)            → Zona Bulk/Overflow
```

Combina con CPOI para slotting multi-criterio. Ref: Frazelle (2002).

### 4. Ruteo S-Shape (Pick Path)

```
Para cada pasillo: recorre completamente si contiene picks
Distance_aisle = 2 × depth_aisle  (entrada y salida)
Total_distance = Σ Distance_aisle_i  (pasillos visitados)
```

Heurística simple. Reduce distancia vs. random. Ref: de Koster et al. (2007) *Eur. Journal of OR*.

### 5. Storage Utilization

```
Utilization% = Occupied_locations / Total_locations × 100

Target: 85%  (deja 15% para reorganización y recepciones)
>95% → congestión operativa
<70% → sobrecapacidad (revisar red de almacenes)
```

### 6. Productividad de Picking

```
Lines_per_hour = Total_lines_picked / Total_labor_hours

Benchmark:
  Manual paper:  40-60 lines/h
  RF scanner:    80-120 lines/h
  Voice picking: 120-180 lines/h
  Light-directed: 200-400 lines/h
```

---

## Modelos de Machine Learning Recomendados

### 1. Algoritmos Genéticos — Slotting Optimization

**Tipo**: Optimización metaheurística  
**Funcionamiento**: Cromosoma = asignación de SKU a ubicación para todos los ítems. Fitness = distancia total de travel para todos los pedidos del mes. Se evoluciona durante 500+ generaciones (selección, crossover, mutación) hasta convergencia. Supera CPOI puro en almacenes con alta correlación entre SKUs.  
**Output**: mapa óptimo de asignación SKU→ubicación.  
**Librería**: DEAP (Python), PyGAD  
**Ref**: Öncan (2015) *OR Spectrum*.

### 2. Deep RL — Routing Dinámico de Picking

**Tipo**: Reinforcement Learning (DQN/PPO)  
**Funcionamiento**: Agente aprende rutas de picking dinámicas conforme cambia el estado del almacén (nuevas recepciones, reubicaciones, congestión). Estado: `(picker_location, remaining_picks_list)`. Acción: `next_location`. Recompensa: `-travel_time - congestion_penalty`.  
**Output**: ruta óptima en tiempo real por order batch.  
**Librería**: Ray RLlib, Stable-Baselines3  
**Ref**: Waschneck et al. (2018) CIRP.

### 3. Computer Vision (YOLOv8) — Cycle Counting Automático

**Tipo**: Detección de objetos  
**Funcionamiento**: Modelo YOLOv8 desplegado en cámaras fijas o robots autónomos. Cuenta pallets y cajas por ubicación. Compara con sistema WMS. Flags discrepancias para ajuste de inventario.  
**Output**: conteo por ubicación + `{location_id, wms_qty, cv_count, discrepancy}`.  
**Librería**: Ultralytics YOLOv8, OpenCV  
**Ref**: Redmon et al. (2016) CVPR.

### 4. K-Means — Dynamic Slotting por Co-Ocurrencia

**Tipo**: Clustering no supervisado  
**Funcionamiento**: Agrupa SKUs que frecuentemente aparecen en el mismo pedido. SKUs en el mismo cluster se ubican en zonas adyacentes, reduciendo picks multi-zona.  
**Features**: matriz de co-ocurrencia de ítems en órdenes del último mes.  
**Output**: grupos de SKUs para slotting contiguo.  
**Librería**: scikit-learn `KMeans`, scipy `linkage`  
**Ref**: Brynzér & Johansson (1996) *Int. J. Production Economics*.

### 5. LSTM — Predicción de Workload

**Tipo**: Serie temporal  
**Funcionamiento**: Predice volumen de recepciones y despachos por hora y turno. Input: histórico 12 meses + calendario (festivos, promociones). Output: forecast de líneas/hora para planificación de personal.  
**Output**: `{date, shift, predicted_inbound_lines, predicted_outbound_lines, recommended_headcount}`  
**Librería**: TensorFlow, Prophet  
**Ref**: Hochreiter & Schmidhuber (1997) *Neural Computation*.

---

## Referencias

- Frazelle, E. (2002) *World-Class Warehousing and Material Handling*, McGraw-Hill
- de Koster, R., Le-Duc, T. & Roodbergen, K.J. (2007) *Eur. Journal of Operational Research*
- GS1 General Specifications v23.0
- Chopra & Meindl (2016) *Supply Chain Management*, 6th Ed.
- Redmon et al. (2016) *You Only Look Once*, CVPR
