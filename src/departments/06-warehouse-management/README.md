# 06 — Warehouse Management System (WMS)

## Overview

The Warehouse Management System (WMS) department governs the physical flow of goods within every storage facility — from inbound receipt at the dock to outbound dispatch. It owns the **warehouse structure** (a 4-level hierarchy: Zone → Aisle → Rack → Bin), **FEFO lot picking** for perishable and regulated goods, **ABC velocity slotting**, and **CPOI (Cube Per Order Index)** optimization to minimize picker travel distance.

The WMS integrates tightly with Inventory Management (movement event log), Logistics (outbound shipment creation), and Quality Management (lot status and hold flags). Storage locations are modelled as **WarehouseLocation** entities with capacity (weight, volume), temperature zone, and hazmat compatibility. Lot availability for picking is always derived from the inventory event log — the WMS does not maintain a separate balance.

GS1 **SSCC** (Serial Shipping Container Code) labels are generated at pallet build, and **GLN** (Global Location Number) identifies each warehouse facility globally for EDI interchange (UN/EDIFACT DESADV, RECADV).

---

## KPIs

| KPI | Definition | World-Class Target |
|-----|------------|--------------------|
| **Pick Accuracy %** | Lines picked without error / Total lines picked | ≥ 99.9% |
| **Order Picking Productivity** | Lines picked / Labor hours | 80–120 lines/hr (manual); 200–400 (voice/RF) |
| **Storage Utilization %** | Occupied locations / Total locations × 100 | 80–85% (optimal); >95% = congestion risk |
| **FEFO Compliance %** | Picks following FEFO sequence / Total lot picks | 100% (pharma/food — zero tolerance) |
| **Dock-to-Stock Time** | Time from truck arrival to putaway complete (hours) | < 4 hours (ambient); < 2 hours (cold chain) |
| **Labor Cost per Shipment** | Total warehouse labor cost / Outbound shipments | Benchmark varies by sector |
| **Order Entry Accuracy — Inbound** (SCOR RL.2.3) | Inbound orders received with zero WMS entry corrections / Total inbound orders × 100 | ≥ 99.5% (EDI ASN); ≥ 97% (manual GR) |

---

## Standards

| Standard | Scope | Implementation |
|----------|-------|----------------|
| **GS1 General Specifications v23.0** | SSCC pallet labels, GLN facility identification, barcode symbology | `domain/Warehouse.ts`; SSCC on `ShipmentLine` |
| **ISO 28000:2022** | Warehouse security management, access control, CCTV, seal integrity | Security zones in `WarehouseLocation` |
| **Frazelle WMS Framework** | CPOI slotting, velocity-based ABC slotting, travel distance minimization | `calculateSlotting()` in `Warehouse.ts` |
| **OSHA 29 CFR 1910.178** | Forklift safety, aisle widths, load limits | `maxWeightKg` on `WarehouseLocation` |
| **EU GDP (Good Distribution Practice)** | Cold chain traceability, temperature logging for pharma | `storageCondition` + lot tracking |

---

## Domain Files

### `domain/Warehouse.ts`

Central domain file for all warehouse structure and slotting logic.

**WarehouseType:**
| Value | Description |
|-------|-------------|
| `AMBIENT` | Dry goods, general merchandise |
| `REFRIGERATED` | 2–8°C; fresh produce, dairy |
| `FROZEN` | ≤ −18°C; frozen foods |
| `HAZMAT` | UN segregation-compliant hazardous materials |
| `BONDED` | Customs bonded — goods not yet cleared |

**WarehouseLocation (4-Level Hierarchy):**
```
Zone  →  Aisle  →  Rack  →  Bin
 e.g.    A          03      R2     B04
```
Each `WarehouseLocation` carries: `maxWeightKg`, `maxVolumeCbm`, `temperatureZone`, `isHazmatCompatible`, `isActive`.

**Key Functions:**

| Function | Description |
|----------|-------------|
| `fefoSort(lots: LotAvailability[])` | Sorts available lots by `expiryDate ASC` — earliest expiry first |
| `calculateSlotting(input: SlottingInput)` | Computes CPOI per SKU, sorts ASC, assigns to golden/primary/secondary/bulk zones |
| `SlottingInput` | `{ skuId, volume, orderFrequency, pickFrequency, currentLocation }` |
| `SlottingRecommendation` | `{ skuId, recommendedZone, cpoi, velocityClass }` |
| `LotAvailability` | `{ lotId, locationId, qty, expiryDate, lotStatus }` |

---

## Business Rules

1. **FEFO is mandatory** for all items with `lotTracked = true` — picks must always consume the earliest-expiring lot first.
2. **Lot status gates picking** — lots with status `QUARANTINE` or `REJECTED` cannot be allocated to outbound orders.
3. **Location capacity** — putaway is blocked if `occupiedWeightKg + incoming > maxWeightKg` or `occupiedVolumeCbm + incoming > maxVolumeCbm`.
4. **Hazmat segregation** — items with `hazmatClass` set can only be stored in `isHazmatCompatible = true` locations.
5. **SSCC generation** — every pallet built triggers SSCC label generation (GS1 AI 00, 18-digit).
6. **Cross-docking** — inbound receipts may bypass putaway if a matching outbound order exists and lot status is `RELEASED`.
7. **Soft-delete** — `WarehouseLocation` deactivation via `isActive = false`; never hard-delete.

---

## Modelos Matemáticos Aplicados

### 1. FEFO — First Expired First Out

The mandatory lot picking sequence for perishable, pharmaceutical, and regulated items:

```
Sort lots by: expiryDate ASC (earliest first), then by lotId ASC (tie-break)

Priority(lot_i) = expiryDate_i   [minimize]

Allocation sequence:
    FOR each unit demanded:
        pick from lot with minimum expiryDate where qty_available > 0
```

FEFO guarantees **zero expired-goods shipment** when applied consistently. Any deviation (picking a later-expiry lot when earlier-expiry stock is available) constitutes a FEFO non-compliance event and must be logged for GDP / GMP audit.

> Reference: EU Commission — *Good Distribution Practice of Medicinal Products for Human Use* (2013/C 68/01). FAO / WHO — *Codex Alimentarius* food storage guidelines.

---

### 2. CPOI — Cube Per Order Index

CPOI drives golden zone assignment — the locations nearest to the dispatch dock:

```
CPOI_i = Volume_i (m³ per unit) / Orders_containing_SKU_i (per month)

Sort all SKUs by CPOI ASC:
    Lowest CPOI  → Golden Zone   (SKUs that are small AND ordered frequently)
    Mid CPOI     → Primary Zone
    High CPOI    → Secondary Zone
    Highest CPOI → Bulk Storage  (large, infrequent)
```

**Interpretation:** A SKU with CPOI = 0.001 m³/order is small and ordered 1,000×/month → place closest to dispatch. A SKU with CPOI = 0.5 m³/order is large and ordered 2×/month → bulk storage.

> Reference: Frazelle, E.H. — *World-Class Warehousing and Material Handling* (McGraw-Hill, 2002), Ch. 5.

---

### 3. ABC Velocity Slotting

Rank SKUs by **pick frequency** (distinct order lines per month):

```
Pick_Frequency_i = order_lines_containing_SKU_i / month

Sorted descending → compute cumulative pick frequency %:

A-velocity:  top 80% of total picks  (~20% of SKUs)  → Primary zone
B-velocity:  next 15% of picks        (~30% of SKUs)  → Secondary zone
C-velocity:  bottom 5% of picks       (~50% of SKUs)  → Bulk / overflow
```

Combined with CPOI: **A-velocity + low CPOI** → golden zone (maximum pick efficiency). This minimizes the travel distance for the majority of picks.

> Reference: Frazelle, E.H. — *World-Class Warehousing and Material Handling* (McGraw-Hill, 2002).

---

### 4. Travel Distance Minimization

For a pick route visiting locations l₁, l₂, ..., lₙ in a single-aisle warehouse:

```
D_route = Σ_{k=1}^{n-1} distance(l_k, l_{k+1}) + distance(l_n, depot)

S-shape routing heuristic:
    Traverse every aisle containing a pick item end-to-end
    Skip aisles with no picks
    Alternate direction per aisle

Nearest-neighbor heuristic:
    next_pick = argmin distance(current_location, remaining_picks)
```

S-shape is optimal for high-density picks (>50% aisle coverage). Nearest-neighbor is better for sparse picks.

> Reference: de Koster, R., Le-Duc, T. & Roodbergen, K.J. — *Design and control of warehouse order picking: a literature review* (European Journal of Operational Research, 182(2), 481–501, 2007).

---

### 5. Storage Utilization

```
Storage_Utilization% = (Occupied_Locations / Total_Active_Locations) × 100

Or by volume:
Storage_Utilization_Vol% = (Σ occupied_volume_i / Σ max_volume_i) × 100
```

| Utilization | Status |
|-------------|--------|
| < 70% | Under-utilized — excess capacity cost |
| 70–85% | Optimal operating range |
| 85–95% | Acceptable — monitor for congestion |
| > 95% | Congestion risk — slotting review required |

---

### 6. Labor Productivity

```
Lines_per_Hour = Total_lines_picked / Total_labor_hours

Or for a single picker shift:
Productivity_shift = Lines_picked_in_shift / Hours_worked
```

| Pick Technology | Benchmark Lines/Hr |
|----------------|-------------------|
| Paper pick list | 60–80 |
| Barcode scan (RF) | 80–120 |
| Voice-directed picking | 120–180 |
| Pick-to-light | 180–300 |
| Goods-to-person (AS/RS) | 300–600 |

> Reference: Frazelle, E.H. — *World-Class Warehousing and Material Handling* (McGraw-Hill, 2002), Ch. 7.

---

## Modelos de Machine Learning Recomendados

### 1. Algoritmos Genéticos para Slotting Optimization

**Problem:** Optimal slot assignment for thousands of SKUs is an NP-hard combinatorial optimization problem — CPOI and velocity alone are heuristics.

**Algorithm:** Genetic Algorithm (GA)
```
Chromosome: slot_assignment[SKU_1, SKU_2, ..., SKU_n] → location vector
Fitness function: F = Σ_all_orders Σ_all_lines distance(slot_assignment[SKU], depot)
  (minimize total travel distance across all historical orders)

Operators:
    Selection: Tournament selection
    Crossover: Order crossover (OX) for permutation encoding
    Mutation:  Random swap of two SKU slot assignments
Generations: 500–1,000; population: 200
```

**Benefit:** 15–30% reduction in total travel distance vs. pure CPOI heuristic.

**Libraries:** DEAP (`deap.algorithms.eaSimple`), PyGAD.

> Reference: Öncan, T. — *A survey of the generalized assignment problem and its applications* (INFOR, 2007).

---

### 2. Deep Reinforcement Learning para Routing de Picking

**Problem:** Pick routes are planned statically at wave release; warehouse occupancy and pick priorities change dynamically during the shift.

**Formulation:** MDP for dynamic pick routing
```
State  s_t = (picker_location, remaining_picks_set, aisle_occupancy)
Action a_t = next_location to visit
Reward r_t = −travel_time(current → next)
Terminal: all picks completed → episode ends
```

**Algorithm:** PPO (Proximal Policy Optimization) or DQN with graph representation.

**Benefit:** Adapts to real-time aisle blockages, priority order insertions, and partial picks — outperforms static S-shape by up to 20%.

**Libraries:** Ray RLlib (`rllib.algorithms.ppo`), OpenAI Gym (custom warehouse environment).

---

### 3. Computer Vision para Inventory Cycle Counting

**Problem:** Manual cycle counting is labor-intensive, infrequent, and error-prone. Physical count discrepancies are discovered too late.

**Architecture:** YOLOv8 object detection model
- **Deployment:** IP cameras on rack ends + mobile robots navigating aisles
- **Input:** RGB image of rack bay
- **Output:** Detected pallets/cases count + SKU identification (barcode OCR)
- **Integration:** Discrepancy between vision count and event-sourced balance → automatic cycle count adjustment request

**Training data:** Labeled warehouse images (pallet count ground truth).
**Accuracy:** >99% pallet detection in controlled lighting conditions.

**Libraries:** Ultralytics YOLOv8 (`ultralytics`), OpenCV, Tesseract OCR.

> Reference: Redmon, J. et al. — *You Only Look Once: Unified, Real-Time Object Detection* (CVPR, 2016).

---

### 4. Demand Clustering para Dynamic Slotting

**Problem:** Items frequently ordered together should be stored adjacent to minimize multi-zone picks — CPOI alone ignores co-occurrence patterns.

**Algorithm:** K-Means or DBSCAN on order co-occurrence matrix
```
Co-occurrence_matrix[i][j] = number of orders containing both SKU_i and SKU_j

Embed each SKU as a vector of co-occurrence frequencies
Apply K-Means (k = number of zones): cluster = zone assignment
Assign clusters to physical zones to minimize inter-zone picks
```

**Benefit:** Reduces multi-zone picks by 20–35% for stores with high basket correlation (grocery, MRO).

**Libraries:** scikit-learn (`sklearn.cluster.KMeans`, `sklearn.cluster.DBSCAN`), NumPy sparse matrix.

---

### 5. LSTM para Predicción de Workload por Turno

**Problem:** Overstaffing wastes labor; understaffing causes late shipments. Need shift-level inbound/outbound volume forecast.

**Architecture:** LSTM sequence model
- **Input features:** Historical daily/hourly receipt + shipment volumes, day-of-week, promotions calendar, supplier schedule, open order backlog
- **Sequence length:** 28 days of daily history
- **Output:** Predicted lines for next 3 shifts (inbound, outbound, returns separately)

**Use:** Feed output to staffing algorithm (target: actual_lines / productivity_benchmark = FTE required).

**Libraries:** TensorFlow/Keras (`tf.keras.layers.LSTM`), pandas for time-series feature engineering.

---

## References

1. Frazelle, E.H. — *World-Class Warehousing and Material Handling* (McGraw-Hill, 2002)
2. de Koster, R., Le-Duc, T. & Roodbergen, K.J. — *Design and control of warehouse order picking: a literature review* (European Journal of Operational Research, 182(2), 2007)
3. Chopra, S. & Meindl, P. — *Supply Chain Management*, 6th Ed. (Pearson, 2016)
4. GS1 — *General Specifications v23.0* (GS1, 2023)
5. ISO 28000:2022 — *Security and resilience — Supply chain security management systems*
6. Redmon, J. et al. — *You Only Look Once: Unified, Real-Time Object Detection* (CVPR, 2016)
7. Öncan, T. — *A survey of the generalized assignment problem and its applications* (INFOR, 45(3), 2007)
8. EU Commission — *Guidelines on Good Distribution Practice* (2013/C 68/01)
9. Mnih, V. et al. — *Human-level control through deep reinforcement learning* (Nature, 518, 2015)
