# 05 — Inventory Management (Event-Sourced)

## Overview

Custodio del inventario físico y financiero de la cadena de suministro. Implementa **Event Sourcing**: cada movimiento es un evento inmutable; el balance se proyecta reproduciendo el log. Cubre clasificación ABC-XYZ, contabilidad de doble entrada por movimiento, y el proceso SCOR Return (RETURN_FROM_CUSTOMER).

---

## KPIs del Departamento

| KPI | Benchmark | Fuente |
|-----|-----------|--------|
| Inventory Turnover | ≥ 8-12× (FMCG) | Chopra & Meindl Ch.11 |
| DIO | < 45 días | APICS CPIM |
| Fill Rate | ≥ 98% | Walmart standard |
| Stockout Rate | < 2% | Christopher (2022) |
| Shrinkage % | < 0.5% | NRF benchmark |
| Dead Stock % | < 3% portfolio | Interno |

---

## Estándares

| Estándar | Alcance |
|----------|---------|
| GS1 Gen. Specs. v23.0 | GTIN, SSCC, UOM, lot tracking |
| IFRS IAS 2 | Valoración de inventarios |
| GAAP ASC 330 | Capitalización de costos |
| ISO 28000:2022 | Seguridad en almacén |
| US UCC Article 2 | Quantity in goods |

---

## Archivos del Departamento

| Archivo | Responsabilidad |
|---------|----------------|
| `domain/InventoryItem.ts` | Item master: ABC/XYZ class, lot tracking, REACH SVHC, storageCondition, ABC_XYZ_MATRIX (9 estrategias) |
| `domain/StockMovement.ts` | 15 MovementType, GL doble entrada, idempotencyKey, projectStockBalance() |

---

## Reglas de Negocio Críticas

1. **Nunca inventario negativo** sin `backorderAllowed = true`
2. **Soft-delete únicamente** — eventos inmutables, jamás se eliminan
3. **Idempotencia** via `idempotencyKey` — reintentos seguros
4. **Lot tracking obligatorio** para `storageCondition !== AMBIENT` o `reachSVHC = true`
5. **Doble entrada contable**: cada movimiento genera Dr/Cr en `GL_ACCOUNTS`
6. **Balance por replay**: no existe campo `onHandQty` mutable — se calcula desde eventos

---

## MovementTypes (15)

`PURCHASE_RECEIPT` · `SALE_SHIPMENT` · `TRANSFER_IN` · `TRANSFER_OUT` · `ADJUSTMENT_POSITIVE` · `ADJUSTMENT_NEGATIVE` · `RETURN_FROM_CUSTOMER` · `RETURN_TO_SUPPLIER` · `PRODUCTION_CONSUMPTION` · `PRODUCTION_OUTPUT` · `SCRAP` · `WRITE_OFF` · `CYCLE_COUNT_ADJUSTMENT` · `QUARANTINE_IN` · `QUARANTINE_RELEASE`

---

## Modelos Matemáticos Aplicados

### 1. Proyección de Stock (Event Sourcing)

```
Balance_t = Σ qty_i [type ∈ INBOUND] − Σ qty_j [type ∈ OUTBOUND]
```

Replay completo del log garantiza auditoría total. Ref: Vernon (2013) *Implementing DDD*.

### 2. Clasificación ABC por Valor (Pareto)

```
ACV_i = Demand_i × Unit_cost_i

A = top 80% valor (~20% SKUs)
B = siguiente 15% valor (~30% SKUs)
C = último 5% valor (~50% SKUs)
```

Ref: Silver, Pyke & Peterson (1998).

### 3. Clasificación XYZ por Coeficiente de Variación

```
CV_i = σ_demand_i / μ_demand_i

X: CV < 0.10  → estable       → EOQ fijo
Y: 0.10–0.25  → moderado      → revisión periódica
Z: CV ≥ 0.25  → alta variab.  → MTO / reposición dinámica
```

Ref: Chopra & Meindl (2016) Ch.11.

### 4. Inventory Turnover Ratio

```
ITR = COGS / Average_Inventory_Value
Average_Inventory = (Opening + Closing) / 2
```

Benchmark: FMCG 8-12×, Automotive 15-20×.

### 5. DIO — Days Inventory Outstanding

```
DIO = 365 / ITR  =  (Avg_Inventory / COGS) × 365
```

Componente C2C Cycle (Dept 11). Target: < 45 días.

### 6. Contabilidad de Doble Entrada (IAS 2)

| Movimiento | Débito | Crédito |
|-----------|--------|---------|
| PURCHASE_RECEIPT | Inventory (1300) | Accounts Payable (2000) |
| SALE_SHIPMENT | COGS (5000) | Inventory (1300) |
| RETURN_FROM_CUSTOMER | Inventory (1300) | Sales Returns (4100) |
| SCRAP / WRITE_OFF | Inv. Adjustment (5100) | Inventory (1300) |

### 7. Inventory Carrying Cost

```
ICC = Inventory_Value × Carrying_Rate
Carrying_Rate ≈ 20–30%/año (capital + storage + obsolescence + insurance)
```

---

## Modelos de Machine Learning Recomendados

### 1. CNN + LSTM — Reclasificación ABC-XYZ Dinámica

**Tipo**: Clasificación supervisada híbrida  
**Funcionamiento**: CNN extrae patrones locales en 52 semanas de demanda; LSTM captura dependencias temporales. Predice clase ABC-XYZ del próximo trimestre y activa reclasificación automática sin intervención humana.  
**Output**: `{sku_id, predicted_class: "AX"|"BZ"|..., confidence}`  
**Librería**: TensorFlow/Keras — `tf.keras.layers.Conv1D + LSTM`  
**Ref**: Goodfellow et al. (2016) *Deep Learning*, MIT Press.

### 2. Isolation Forest — Detección de Shrinkage

**Tipo**: Anomalía no supervisada  
**Funcionamiento**: Aprende patrones normales de movimiento por ubicación. Aisla puntos anómalos (ajustes negativos excesivos sin justificación) indicativos de robo o error de conteo.  
**Output**: `anomaly_score` por ubicación y turno. Flag automático para auditoría.  
**Librería**: `sklearn.ensemble.IsolationForest`  
**Ref**: Liu, Ting & Zhou (2008) ICDM.

### 3. Autoencoder — Dead Stock

**Tipo**: Representación no supervisada  
**Funcionamiento**: Entrenado sobre SKUs activos. Alta pérdida de reconstrucción en un SKU = patrón de movimiento anormal (muy bajo) → candidato a obsolescencia.  
**Output**: `reconstruction_error` ranking por SKU.  
**Librería**: PyTorch, Keras  
**Ref**: Hinton & Salakhutdinov (2006) Science.

### 4. LightGBM — Predicción de Stockout

**Tipo**: Clasificación supervisada  
**Features**: stock actual, forecast 14 días, lead time, CV histórico, clase ABC-XYZ, días sin movimiento.  
**Output**: `P(stockout_7d)`, `P(stockout_14d)`, `P(stockout_30d)` — activa reorden automático.  
**Librería**: LightGBM, XGBoost  
**Ref**: Chen & Guestrin (2016) KDD.

### 5. Reinforcement Learning — Política de Reabastecimiento

**Tipo**: RL (MDP)  
**Funcionamiento**: Estado `(I_t, D̂_t, LT_t, costs)`. Acción `q_t ∈ [0, Q_max]`. Recompensa `-(h·I_t + p·max(0, D_t−I_t))`. Aprende política (s,S) dinámica que supera reglas estáticas en demanda no estacionaria.  
**Output**: política adaptativa por SKU.  
**Librería**: Ray RLlib, Stable-Baselines3  
**Ref**: Oroojlooy et al. (2022) Transportation Research Part E.

---

## Referencias

- Silver, Pyke & Peterson (1998) *Inventory Management and Production Planning*, 3rd Ed.
- Chopra & Meindl (2016) *Supply Chain Management*, 6th Ed. Ch.11
- IAS 2 — Inventories (IFRS Foundation)
- GS1 General Specifications v23.0
- Liu, Ting & Zhou (2008) *Isolation Forest*, ICDM
