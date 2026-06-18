# 07 — Logistics & Transportation Management (TMS)

## Overview

The Logistics & Transportation Management department owns the end-to-end physical movement of goods from origin to destination — from carrier booking through customs clearance to final delivery confirmation. It manages **shipments**, **transport legs**, **real-time tracking events**, **customs documents**, and **carrier contracts**.

The module implements the full **Incoterms® 2020** ruleset (11 terms, including DPU which replaces the retired DAT), defining the precise point of **risk transfer** and **cost responsibility** between buyer and seller. All 9 **IMDG hazmat classes** are supported for sea freight (and ADR for European road transport), with UN number, proper shipping name, and packing group enforced on every `ShipmentLine`.

Supply chain security is enforced via **C-TPAT** (US Customs-Trade Partnership Against Terrorism) and **AEO** (EU Authorised Economic Operator) certifications — AEO-certified shippers benefit from reduced customs examinations and priority processing under **WTO TFA Article 7**. The **Basel Convention** governs transboundary movement of hazardous waste — tracked via `hazmatClass` on shipment lines.

CO₂ emissions are calculated per **GHG Protocol Scope 3 Category 4** (upstream transportation) using mode-specific emission factors.

SCOR mapping: **Deliver** process.

---

## KPIs

| KPI | Definition | World-Class Target |
|-----|------------|--------------------|
| **OTD — On-Time Delivery %** | Shipments delivered ≤ promised date / Total shipments × 100 | ≥ 95% |
| **Transit Time Variance** | σ of actual transit time vs. planned | Minimize; P95 < committed date |
| **Freight Cost per Kg/Km** | Total freight cost / (total weight × total distance) | Benchmark varies by mode/lane |
| **CO₂ per Tonne-Km** | GHG emissions per unit of freight transported | Road: 0.062; Sea: 0.010; Air: 0.602 kgCO₂e/t-km |
| **Customs Clearance Time** | Days from shipment arrival to duty payment and release | < 1 day (AEO); < 3 days (standard) |
| **OTIF — On-Time In-Full** | Shipments delivered on time AND in full quantity | ≥ 98% (Walmart standard) |

---

## Standards

| Standard | Scope | Implementation |
|----------|-------|----------------|
| **Incoterms® 2020 (ICC)** | 11 trade terms defining risk/cost transfer points | `INCOTERMS_2020` constant; `Shipment.incoterm` |
| **IMDG Code (IMO, 2022 Ed.)** | International Maritime Dangerous Goods — 9 hazmat classes | `HazmatClass` enum; `ShipmentLine.hazmatClass` |
| **ADR (UNECE, 2023)** | European road transport of dangerous goods | `hazmatClass` validation for ROAD mode |
| **Basel Convention (1989)** | Transboundary movement of hazardous waste | `ShipmentLine.hazmatClass` + `wasteMaterial` flag |
| **WTO TFA Article 7** | Pre-arrival processing, trusted trader expediting | `Shipment.aeoShipperCertified` |
| **C-TPAT (US CBP)** | US Customs-Trade Partnership Against Terrorism | `SecurityCertification.CTPAT` |
| **AEO (EU Reg. 952/2013)** | EU Authorised Economic Operator | `SecurityCertification.AEO` |
| **GS1 SSCC** | Serial Shipping Container Code on all shipment units | `ShipmentLine.sscc` |
| **GHG Protocol Scope 3** | Category 4 upstream transportation emissions | `calculateCO2Emissions()` |

---

## Domain Files

### `domain/Shipment.ts`

Primary aggregate for all logistics operations.

**TransportMode:**
| Value | Description |
|-------|-------------|
| `ROAD` | Truck / LTL / FTL — ADR for hazmat |
| `SEA` | Ocean freight — FCL / LCL — IMDG for hazmat |
| `AIR` | Air freight — IATA DGR for hazmat; chargeable weight rules apply |
| `RAIL` | Rail freight — RID for hazmat in Europe |
| `MULTIMODAL` | Two or more modes — single B/L or multimodal transport document |

**ShipmentStatus lifecycle:**
```
DRAFT → BOOKED → IN_TRANSIT → CUSTOMS_HOLD → DELIVERED
                             ↘ EXCEPTION → IN_TRANSIT (re-routed)
                                         ↘ LOST
```

**HazmatClass (9 IMDG classes):**
| Class | Description |
|-------|-------------|
| `CLASS_1` | Explosives |
| `CLASS_2` | Gases |
| `CLASS_3` | Flammable liquids |
| `CLASS_4` | Flammable solids |
| `CLASS_5` | Oxidizing substances & organic peroxides |
| `CLASS_6` | Toxic & infectious substances |
| `CLASS_7` | Radioactive material |
| `CLASS_8` | Corrosive substances |
| `CLASS_9` | Miscellaneous dangerous goods |

**Key Fields on Shipment:**

| Field | Description |
|-------|-------------|
| `incoterm` | One of 11 Incoterms® 2020 rules |
| `aeoShipperCertified` | AEO status → WTO TFA Art.7 benefits |
| `customsDocuments` | Array of `CustomsDocument` (CI, packing list, BoL, CO, EUR.1) |
| `transportLegs` | Array of `TransportLeg` for multimodal routing |

**Key Functions:**

| Function | Description |
|----------|-------------|
| `createShipment()` | Factory — validates incoterm, carrier, dangerous goods declaration |
| `addTrackingEvent()` | Appends immutable tracking event (location, timestamp, status) |
| `isOnTimeDelivery()` | Returns `actualDeliveryDate ≤ estimatedDeliveryDate` |

---

## Business Rules

1. **Incoterms® 2020 enforcement** — `incoterm` field is mandatory on every shipment; drives who pays freight, insurance, and customs duties.
2. **Hazmat declaration** — any `ShipmentLine` with `hazmatClass` set must include `unNumber`, `properShippingName`, `packingGroup`, and `emergencyContactPhone`.
3. **AEO/C-TPAT flag** — `aeoShipperCertified = true` enables expedited customs processing; must be re-validated annually.
4. **Tracking events are immutable** — once appended, a tracking event cannot be edited or deleted (audit trail).
5. **Customs documents** — shipments crossing international borders require at minimum: Commercial Invoice (CI), Packing List, and Bill of Lading / Air Waybill.
6. **Soft-delete only** — shipment records are never hard-deleted; cancelled shipments use `status: CANCELLED`.
7. **UFLPA** — shipments originating from or transiting XUAR must carry `clearanceDocumentRef` on the customs document.

---

## Modelos Matemáticos Aplicados

### 1. OTD — On-Time Delivery

```
OTD% = (Shipments where actualDeliveryDate ≤ promisedDeliveryDate) / Total_Shipments × 100

isOnTimeDelivery() = (actualDelivery ≤ estimatedDelivery)  → Boolean
```

World-class benchmark: ≥ 95%. Calculated per carrier, per lane, per transport mode for root cause analysis. OTD degradation by carrier triggers scorecard penalty per `supplier-management/` module.

> Reference: ASCM — *SCOR Digital Standard* (ASCM, 2019), Deliver metrics.

---

### 2. Transit Time Distribution

Model transit time per lane as a normal distribution for ATP (Available-to-Promise) commitments:

```
Transit_Time ~ N(μ_tt, σ²_tt)

where:
    μ_tt = mean observed transit time (days) for lane × carrier × mode
    σ_tt = standard deviation of observed transit times

For customer ATP commitment at service level SL:
    Committed_date = ship_date + μ_tt + z_SL × σ_tt

    z_90% = 1.282  (P90 guarantee)
    z_95% = 1.645  (P95 guarantee)
    z_99% = 2.326  (P99 guarantee)
```

> Reference: Ballou, R.H. — *Business Logistics / Supply Chain Management*, 5th Ed. (Pearson, 2004), Ch. 6.

---

### 3. Freight Cost Modeling

**Road / LTL / FTL:**
```
Cost_road = Base_Rate(weight_break) × chargeable_weight_kg
           + Fuel_Surcharge% × Base_Rate
           + Accessorial_charges (liftgate, residential, hazmat)
```

**Air freight (IATA chargeable weight):**
```
Volume_Weight_kg = (length_cm × width_cm × height_cm) / 6,000
Chargeable_Weight_kg = max(actual_weight_kg, Volume_Weight_kg)
Cost_air = Rate_per_kg × Chargeable_Weight_kg + Fuel_surcharge + Security_surcharge
```

**Sea freight:**
```
Cost_sea = TEU_rate × number_of_TEUs  (FCL)
         or
Cost_sea = CBM_rate × total_CBM + Weight_rate × total_tonnes  (LCL, W/M basis)
```

---

### 4. CO₂ Emissions — GHG Protocol Scope 3 Category 4

```
Emissions_kgCO2e = Distance_km × Weight_tonnes × EF_mode

Emission Factors (GLEC Framework / GHG Protocol):
    EF_road   = 0.062 kgCO2e / tonne-km  (diesel truck, Euro VI)
    EF_sea    = 0.010 kgCO2e / tonne-km  (container vessel)
    EF_air    = 0.602 kgCO2e / tonne-km  (belly freight, long-haul)
    EF_rail   = 0.028 kgCO2e / tonne-km  (electric rail, EU avg)

Total_Shipment_Emissions = Σ (Distance_leg_k × Weight_tonnes × EF_mode_k)
    for each transport leg k in multimodal route
```

> Reference: GHG Protocol — *Corporate Value Chain (Scope 3) Accounting and Reporting Standard* (WRI/WBCSD, 2011).

---

### 5. Vehicle Routing Problem (VRP) — Clarke-Wright Savings Algorithm

For last-mile delivery routing with multiple stops:

```
Savings_ij = d(depot, i) + d(depot, j) − d(i, j)

Algorithm:
1. Start with n direct routes (depot → customer_i → depot)
2. Rank all pairs (i,j) by Savings_ij descending
3. Merge routes for pair with highest saving if:
   - Neither i nor j is interior stop in existing route
   - Combined load ≤ vehicle_capacity
4. Repeat until no feasible merges remain

Objective: Minimize Σ distance(all routes)
Subject to: Σ demand_i ≤ vehicle_capacity per route
```

> Reference: Toth, P. & Vigo, D. — *Vehicle Routing: Problems, Methods, and Applications*, 2nd Ed. (SIAM, 2014).

---

### 6. Customs Duty Calculation

```
CIF_value = FOB_value + Insurance + Freight_cost

Duty_payable = CIF_value × Tariff_rate(HS_code, origin_country, destination_country)

Tariff rate selection hierarchy:
    1. Preferential FTA rate (if valid FTA exists and origin certificate presented)
    2. GSP rate (if origin qualifies as developing country)
    3. WTO MFN (Most Favoured Nation) rate
    4. General rate (non-MFN country)

VAT (EU import):
    VAT_base = CIF_value + Duty_payable
    VAT_payable = VAT_base × VAT_rate
```

---

## Modelos de Machine Learning Recomendados

### 1. Graph Neural Networks para VRP Dinámico (VRPTW)

**Problem:** Clarke-Wright is a greedy heuristic — poor performance for Vehicle Routing with Time Windows (VRPTW) and dynamic order insertions.

**Architecture:** Attention Model (Transformer-based Pointer Network)
- **Input:** Graph of customer nodes (coordinates, demand, time window) + depot
- **Model:** Multi-head attention encodes node embeddings; decoder selects next node autoregressively
- **Training:** Reinforcement learning (REINFORCE) on random VRPTW instances
- **Inference:** Beam search for near-optimal routes

**Benefit:** Within 1–3% of optimal solutions on 100-node instances; runs in milliseconds vs. hours for exact solvers.

**Libraries:** PyTorch, OR-Tools (for comparison baseline).

> Reference: Kool, W., van Hoof, H. & Welling, M. — *Attention, Learn to Solve Routing Problems!* (ICLR, 2019).

---

### 2. LSTM para Predicción de ETD (Estimated Time of Delivery)

**Problem:** Carrier-provided ETD is often unreliable; port congestion, weather, and customs delays are predictable from historical data.

**Features per shipment-leg:**
| Feature | Source |
|---------|--------|
| Carrier historical OTD on lane | Internal TMS data |
| Port congestion index | MarineTraffic / port authority |
| Weather severity forecast | OpenWeatherMap API |
| Day-of-week, month | Calendar |
| HS code customs complexity | Historical clearance times |
| Vessel utilization % | Carrier API |

**Output:** P50 / P90 delivery date distribution (regression head with quantile loss).

**Libraries:** TensorFlow/Keras (`LSTM`, `Dense`), `quantile_regression` loss.

---

### 3. Random Forest para Clasificación de Riesgo Aduanero

**Problem:** Customs authorities hold a small % of shipments for physical examination — but which ones? Predicting this enables pre-clearance action.

**Features:**
- Country of origin / destination pair
- HS code chapter
- Declared value vs. market value ratio
- Carrier / freight forwarder history
- Shipper AEO/C-TPAT status
- Days since last inspection by this customs office
- Hazmat class present (binary)

**Output:** `HIGH_RISK | MEDIUM_RISK | LOW_RISK` → drives whether to pre-file additional documentation.

**Libraries:** scikit-learn (`RandomForestClassifier`), SHAP for explainability.

---

### 4. Reinforcement Learning para Modal Split Optimization

**Problem:** Choosing road vs. rail vs. sea vs. air for each shipment involves trade-offs between cost, lead time, and CO₂ budget that change dynamically.

**Formulation:** MDP
```
State  s_t = (origin, destination, weight_kg, urgency_days, CO2_budget_remaining, current_spot_rates)
Action a_t = {ROAD, SEA, AIR, RAIL, MULTIMODAL}
Reward r_t = −(freight_cost × cost_weight + transit_time_penalty × urgency_weight
              + CO2_emissions × carbon_price_eur_per_tonne)
```

**Algorithm:** PPO with continuous state space.

**Libraries:** Ray RLlib, OR-Tools for constraint enforcement.

---

### 5. Computer Vision via Satellite para Monitoreo de Congestión Portuaria

**Problem:** Port congestion (e.g., LA/Long Beach, Rotterdam, Shanghai) causes 5–30 day delays — but the signal appears in carrier data 7–14 days after onset. Satellite imagery detects it first.

**Architecture:**
- **Data source:** Sentinel-2 / Planet Labs satellite imagery of major ports (daily/weekly)
- **Model:** Object detection (YOLOv8) to count vessels at anchor and at berth
- **Congestion score:** (vessels_at_anchor / historical_average) × 100
- **Output:** Port congestion alert → trigger modal switch or buffer stock increase

**Libraries:** Sentinel Hub API (ESA), Ultralytics YOLOv8, GeoPandas.

> Reference: Stopford, M. — *Maritime Economics*, 3rd Ed. (Routledge, 2009).

---

## References

1. ICC — *Incoterms® 2020* (International Chamber of Commerce, 2019)
2. IMO — *International Maritime Dangerous Goods Code (IMDG)*, 2022 Amendment
3. Toth, P. & Vigo, D. — *Vehicle Routing: Problems, Methods, and Applications*, 2nd Ed. (SIAM, 2014)
4. Ballou, R.H. — *Business Logistics / Supply Chain Management*, 5th Ed. (Pearson, 2004)
5. GHG Protocol — *Corporate Value Chain (Scope 3) Accounting and Reporting Standard* (WRI/WBCSD, 2011)
6. Kool, W., van Hoof, H. & Welling, M. — *Attention, Learn to Solve Routing Problems!* (ICLR, 2019)
7. Stopford, M. — *Maritime Economics*, 3rd Ed. (Routledge, 2009)
8. ASCM — *SCOR Digital Standard* (ASCM, 2019)
9. WCO — *Customs Guidelines on Integrated Supply Chain Management* (WCO, 2004)
10. US CBP — *C-TPAT Program Overview* (US Customs and Border Protection, 2023)
