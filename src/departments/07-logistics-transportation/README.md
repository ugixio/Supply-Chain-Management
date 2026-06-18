# 07 — Logistics & Transportation (TMS)

## Overview

Gestiona el movimiento físico de mercancías: embarques, legs de transporte, eventos de tracking, Incoterms® 2020 (11 reglas), clasificación Hazmat (IMDG 9 clases), documentación aduanera, certificación AEO/C-TPAT, y cumplimiento WTO TFA Art.7. Responsable del KPI OTD ≥ 95% y la huella de CO₂ Scope 3 Categoría 4.

---

## KPIs del Departamento

| KPI | Benchmark | Fuente |
|-----|-----------|--------|
| OTD (On-Time Delivery) | ≥ 95% | Ballou (2004) |
| Transit Time Variance (días) | < 1 día σ | Interno |
| Freight Cost / Revenue % | < 3-5% | Benchmark sector |
| CO₂ / Tonne-Km (road) | 0.062 kgCO₂e | GHG Protocol |
| Customs Clearance Time | < 24h (AEO) | WTO TFA |
| Carrier On-Time Rate | ≥ 95% | Chopra & Meindl |

---

## Estándares e Incoterms® 2020

| Regla | Modo | Responsabilidad vendedor |
|-------|------|--------------------------|
| EXW | Todos | Mínima (ex works) |
| FCA | Todos | Entrega a carrier designado |
| CPT | Todos | Paga flete hasta destino |
| CIP | Todos | CPT + seguro mínimo 110% |
| DAP | Todos | Entrega en destino (sin descarga) |
| DPU | Todos | Entrega descargada (reemplaza DAT) |
| DDP | Todos | Máxima (derechos pagados) |
| FAS | Marítimo | Al costado del buque |
| FOB | Marítimo | A bordo del buque |
| CFR | Marítimo | FOB + flete |
| CIF | Marítimo | CFR + seguro mínimo |

Otras regulaciones: IMDG Code (IMO), ADR (carretera Europa), Basel Convention, C-TPAT (US CBP), AEO (EU), WTO TFA Art.7, GS1 SSCC.

---

## Archivos del Departamento

| Archivo | Responsabilidad |
|---------|----------------|
| `domain/Shipment.ts` | TransportMode (5), ShipmentStatus, HazmatClass (9 IMDG), ShipmentLine con SSCC/HS code, CustomsDocument, TransportLeg, createShipment(), addTrackingEvent(), isOnTimeDelivery() |

---

## Modelos Matemáticos Aplicados

### 1. OTD — On-Time Delivery

```
OTD% = (Shipments donde actualDelivery ≤ estimatedDelivery) / Total_shipments × 100

isOnTimeDelivery() = actualDelivery ≤ estimatedDelivery
```

World-class ≥ 95%. Ref: Ballou (2004) Ch.6.

### 2. Distribución del Transit Time

```
Transit_time ~ N(μ, σ²)

μ = media histórica por ruta/carrier
σ = desviación estándar histórica

Promesa ATP = μ + 1.65σ  (P95 de entrega puntual)
```

### 3. Flete Aéreo — Chargeable Weight

```
Chargeable_weight = max(actual_kg, volume_m³ × 167)

Volumen equivalente: 167 kg/m³ (IATA estándar)
Flete = Chargeable_weight × rate_per_kg
```

### 4. Emisiones CO₂ (GHG Protocol Scope 3 Cat.4)

```
Emissions_kgCO2e = Distance_km × Weight_tonnes × EF_mode

Factores de emisión:
  Road:  0.062 kgCO2e/tonne-km
  Sea:   0.010 kgCO2e/tonne-km
  Air:   0.602 kgCO2e/tonne-km
  Rail:  0.028 kgCO2e/tonne-km
```

Ref: GHG Protocol (2011) *Corporate Value Chain Scope 3 Standard*.

### 5. Duty de Aduana

```
Duty = CIF_value × Tariff_rate(HS_code, origin_country)
CIF  = FOB_value + Insurance + Freight

Aplica: WTO MFN rates o preferencial (FTA/GSP)
```

### 6. Clarke-Wright Savings (VRP)

```
Saving_ij = d(depot, i) + d(depot, j) − d(i, j)

Merge rutas con mayor saving hasta capacidad del vehículo.
Minimiza: Σ distancias recorridas por flota.
```

Ref: Clarke & Wright (1964) *Operations Research*.

---

## Modelos de Machine Learning Recomendados

### 1. Pointer Network / GNN — VRP Dinámico

**Tipo**: Deep RL + Graph Neural Networks  
**Funcionamiento**: Modela el VRP con ventanas de tiempo (VRPTW) como grafo. Red de atención aprende política de routing near-óptima para flotas dinámicas (nuevas paradas, cancelaciones en tiempo real). Supera Clarke-Wright en fleets complejas.  
**Output**: secuencia de paradas óptima por vehículo.  
**Librería**: PyTorch, OR-Tools (Google), `neuopt`  
**Ref**: Kool, van Hoof & Welling (2019) ICLR.

### 2. LSTM — Predicción de ETD

**Tipo**: Serie temporal  
**Funcionamiento**: Predice Estimated Time of Delivery dado: carrier, ruta, congestión portuaria, clima, día de semana, tipo de carga. Actualiza predicción con cada evento de tracking recibido.  
**Output**: `P50_ETA`, `P90_ETA` por embarque. Alerta proactiva cuando P90 excede SLA.  
**Librería**: TensorFlow, Prophet  
**Ref**: Hochreiter & Schmidhuber (1997).

### 3. Random Forest — Riesgo Aduanero

**Tipo**: Clasificación supervisada  
**Funcionamiento**: Clasifica embarques como HIGH_RISK para retención aduanera antes de llegada. Features: par origen-destino, código HS, valor declarado, carrier, historial importador, entidad lista OFAC.  
**Output**: `risk_level: LOW|MEDIUM|HIGH` + documentos requeridos para pre-clearance.  
**Librería**: scikit-learn  
**Ref**: WTO TFA Art.7 (pre-arrival processing).

### 4. RL — Modal Split Optimization

**Tipo**: Reinforcement Learning  
**Funcionamiento**: Agente aprende cuándo cambiar de road→rail→sea basado en: costo, urgencia, presupuesto CO₂, congestión. Estado: `(origin, dest, weight, urgency, CO2_budget, cost_budget)`. Acción: `mode ∈ {ROAD, SEA, AIR, RAIL, MULTIMODAL}`. Recompensa: `-cost - CO2_penalty - lateness_penalty`.  
**Output**: modo óptimo de transporte por embarque.  
**Librería**: Ray RLlib  
**Ref**: Bektaş & Laporte (2011) *Transportation Research Part B*.

### 5. Imágenes Satelitales + CV — Monitoreo de Puertos

**Tipo**: Computer Vision sobre datos satelitales  
**Funcionamiento**: Analiza imágenes Sentinel-2/Planet de puertos clave. Cuenta buques en rada, detecta congestión, predice delays antes de que aparezcan en datos AIS del carrier. Feed de inteligencia a ETA predictor.  
**Output**: `port_congestion_index` por puerto, actualización diaria.  
**Librería**: Sentinel Hub API, rasterio, Ultralytics  
**Ref**: Stopford (2009) *Maritime Economics*, 3rd Ed.

---

## Referencias

- Ballou, R.H. (2004) *Business Logistics/Supply Chain Management*, 5th Ed. Pearson
- ICC (2019) *Incoterms® 2020*, International Chamber of Commerce
- GHG Protocol (2011) *Corporate Value Chain Scope 3 Standard*, WRI/WBCSD
- Clarke & Wright (1964) *Operations Research* 12(4): 568-581
- IMO IMDG Code, 2022 Edition
