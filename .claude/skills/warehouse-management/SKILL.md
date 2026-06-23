---
description: >
  Warehouse management domain expertise for Department 06. Use when reviewing WMS
  operations, FEFO lot picking, ABC velocity slotting, CPOI, inbound quality,
  order entry accuracy for inbound, or any code in src/departments/06-warehouse-management/.
---

# Warehouse Management — Department 06 Skills Reference

## Supply Chain Domain

**SCOR-DS Mapping**: Deliver (D1.6 — Pick Product, D1.7 — Pack Product); Enable (E5)

**Core WMS Operations**
| Process | Description | Standard |
|---------|------------|---------|
| Receiving (GR) | ASN/PO matching, dock scheduling, label printing | GS1 SSCC, ASN |
| Putaway | Location assignment by ABC velocity, temperature zone | Slotting logic |
| Picking | FEFO lot selection, wave/batch planning, pick-confirm | ISO 9001 §8.5.2 |
| Packing | Cartonization, weight check, label (SSCC, GS1-128) | GS1 Gen. Specs. v23 |
| Shipping | Load confirmation, BOL, customs docs | Incoterms® 2020 |
| Cycle Count | ABC-priority counting schedule | ISO 9001 §8.5.2 |

**KPIs (APICS CPIM; Ballou Ch.12; WERC DC Measures)**
| KPI | World-Class | Formula |
|-----|------------|---------|
| Order Fill Rate | ≥ 99% | Orders filled complete / Total orders × 100 |
| Pick Accuracy | ≥ 99.9% | Correct picks / Total picks × 100 |
| On-Time Shipment | ≥ 98% | Shipments on time / Total shipments × 100 |
| Dock-to-Stock Cycle Time | < 4 hours (FMCG) | GR timestamp → putaway confirmed |
| Inventory Accuracy | ≥ 99.5% | Accurate locations / Total locations × 100 |
| CPOI (Cases Per Operator Hour) | Benchmark varies | Cases picked / Operator-hours |
| Order Entry Accuracy — Inbound (SCOR RL.2.3) | ≥ 99.5% (EDI) | GR lines entered without correction / Total GR lines × 100 |
| Lines Picked per Hour | 100–150 (manual); > 250 (voice) | Lines / Labor hours |

**ABC Velocity Slotting**
- A-items: golden zone (waist to shoulder height, nearest to packing)
- B-items: mid-zone (accessible)
- C-items: top/floor shelves, remote locations
- Re-slot trigger: ABC reclassification or velocity change > 30%

**Storage Conditions**
| Code | Condition | Lot Tracking Required |
|------|-----------|----------------------|
| AMBIENT | 15–25°C | Only if SVHC/hazmat |
| CHILLED | 2–8°C | Yes (mandatory) |
| FROZEN | ≤ −18°C | Yes (mandatory) |
| CONTROLLED | Pharma GDP | Yes (mandatory) |

## Data Analytics

**Inbound Order Entry Accuracy by Source**
```sql
SELECT source_channel,
       COUNT(*) AS total_gr_lines,
       SUM(CASE WHEN entry_correction_count = 0 THEN 1 ELSE 0 END) AS first_pass_correct,
       ROUND(SUM(CASE WHEN entry_correction_count = 0 THEN 1 ELSE 0 END)::float
             / NULLIF(COUNT(*), 0) * 100, 3) AS entry_accuracy_pct
FROM fact_goods_receipt
WHERE gr_date >= CURRENT_DATE - INTERVAL '4 weeks'
GROUP BY source_channel;
-- Targets: EDI_ASN ≥ 99.5% | MANUAL ≥ 97.0% | STO ≥ 99.8%
```

**Pick Accuracy Trend**
```sql
SELECT DATE_TRUNC('week', pick_date) AS week,
       COUNT(*) AS total_picks,
       SUM(CASE WHEN error_flag THEN 1 ELSE 0 END) AS errors,
       ROUND((1 - SUM(error_flag::int)::float / NULLIF(COUNT(*), 0)) * 100, 4) AS accuracy_pct
FROM pick_confirmations
GROUP BY week ORDER BY week;
```

**CPOI — Cases Per Operator Hour**
```sql
SELECT operator_id, DATE_TRUNC('day', pick_date) AS day,
       SUM(cases_picked) AS total_cases,
       SUM(duration_minutes) / 60.0 AS hours_worked,
       ROUND(SUM(cases_picked) / NULLIF(SUM(duration_minutes) / 60.0, 0), 1) AS cpoi
FROM pick_sessions GROUP BY operator_id, day ORDER BY cpoi DESC;
```

## Data Science

**Wave Planning Optimization**
- Goal: minimize travel distance while respecting dock-ship window
- Input: open orders, SKU locations, dock availability windows
- Output: wave assignment (orders per wave); pick sequence
- Method: nearest-neighbor heuristic; Clarke-Wright savings algorithm; OR-Tools VRP

**Slotting Optimization**
- Objective: minimize total travel distance = Σ(order_frequency × distance_to_location)
- Data: picks per SKU per day (30-day rolling), location distances from pack station
- Algorithm: assignment problem (Hungarian method via `scipy.optimize.linear_sum_assignment`)
- Re-slot frequency: monthly for top-50 velocity movers

**Labor Forecasting**
- Input: wave plan, CPOI baseline, order volume forecast
- Output: headcount per shift per day
- Model: `hours_needed = total_lines / expected_lpoh`, with safety buffer

## Machine Learning

**Putaway Location Recommendation**
```python
from sklearn.neighbors import KNeighborsClassifier
import pandas as pd

def recommend_putaway_location(item_features: pd.DataFrame,
                                location_history: pd.DataFrame) -> pd.Series:
    """
    Recommend putaway location based on item attributes and historical picks.
    Features: abc_class, xyz_class, weight_kg, volume_l, temperature_zone,
              hazmat_class, avg_picks_per_day.
    Ref: Roodbergen & Vis (2006), EJOR 170(2).
    License: scikit-learn BSD-3.
    """
    knn = KNeighborsClassifier(n_neighbors=5, metric='euclidean')
    knn.fit(location_history.drop('location_id', axis=1),
            location_history['location_id'])
    return pd.Series(knn.predict(item_features), name='recommended_location')
```

**Forklift Route Optimization (OR-Tools VRP)**
```python
from ortools.constraint_solver import routing_enums_pb2, pywrapcp

def optimize_pick_route(distance_matrix: list[list[int]],
                         pick_locations: list[int]) -> list[int]:
    """
    Vehicle Routing Problem for optimal pick path in warehouse.
    Minimizes total travel distance across pick locations.
    Ref: Google OR-Tools VRP (Apache-2.0).
    """
    manager = pywrapcp.RoutingIndexManager(len(distance_matrix), 1, 0)
    routing = pywrapcp.RoutingModel(manager)
    def distance_callback(from_idx, to_idx):
        return distance_matrix[manager.IndexToNode(from_idx)][manager.IndexToNode(to_idx)]
    transit_idx = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_idx)
    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    solution = routing.SolveWithParameters(params)
    index, route = routing.Start(0), []
    while not routing.IsEnd(index):
        route.append(manager.IndexToNode(index))
        index = solution.Value(routing.NextVar(index))
    return route
```

## Python

| Library | Use | License |
|---------|-----|---------|
| `pandas` | Pick/GR DataFrames, productivity metrics | BSD-3 |
| `numpy` | Distance calculations, CPOI stats | BSD-3 |
| `scipy.optimize` | Slotting optimization (assignment problem) | BSD-3 |
| `ortools` | Wave planning VRP, dock scheduling | Apache-2.0 |
| `scikit-learn` | Putaway recommendation, labor clustering | BSD-3 |
| `simpy` | Warehouse throughput simulation | MIT |
| `networkx` | Warehouse layout graph | BSD-3 |

**FEFO Lot Selection (Python)**
```python
from datetime import date
import pandas as pd

def select_fefo_lots(lots_df: pd.DataFrame, qty_needed: float) -> pd.DataFrame:
    """
    FEFO lot selection: pick from earliest-expiring lot first.
    Input: lots_df with columns [lot_id, expiry_date, available_qty].
    Returns: allocation DataFrame with [lot_id, allocated_qty].
    Ref: ISO 9001:2015 §8.5.2 — Traceability.
    """
    eligible = lots_df[lots_df['expiry_date'] > date.today()].sort_values('expiry_date')
    allocations = []
    remaining = qty_needed
    for _, lot in eligible.iterrows():
        if remaining <= 0:
            break
        take = min(lot['available_qty'], remaining)
        allocations.append({'lot_id': lot['lot_id'], 'allocated_qty': take})
        remaining -= take
    if remaining > 0:
        raise ValueError(f"Insufficient stock: {qty_needed - remaining} of {qty_needed} available")
    return pd.DataFrame(allocations)
```

## TypeScript

**Domain Objects**
- `domain/WarehouseLocation.ts` — Location master; zone; ABC slot; capacity
- `domain/GoodsReceipt.ts` — GR aggregate; ASN match; lot creation; correction count
- `operations/PickTask.ts` — Pick instruction; FEFO lot; quantity; status
- `services/WMSService.ts` — Wave creation; putaway engine; FEFO picker

**GR Entry Accuracy Guard**
```typescript
function validateGoodsReceipt(gr: GoodsReceiptLine, po: POLine): ValidationResult {
  const mismatches: string[] = [];
  if (gr.supplierId !== po.supplierId) mismatches.push('supplier_id');
  if (gr.materialId !== po.materialId) mismatches.push('material_id');
  if (Math.abs(gr.receivedQty - po.openQty) > po.toleranceQty) mismatches.push('quantity');
  if (gr.unitOfMeasure !== po.unitOfMeasure) mismatches.push('uom');
  return { isFirstPassCorrect: mismatches.length === 0, mismatches };
}
```

## OSI / Commercial

| Tool | License | Use |
|------|---------|-----|
| PostgreSQL | PostgreSQL (OSI) | Location master, GR events, pick history |
| Apache Superset | Apache-2.0 | WMS KPI dashboards, CPOI trends |
| Apache Airflow | Apache-2.0 | Daily wave planning pipeline |
| `ortools` | Apache-2.0 | Route optimization, dock scheduling |
| `simpy` | MIT | Warehouse digital twin |

**References**
- Ballou, R.H., *Business Logistics/Supply Chain Management* 5th Ed., Ch.12 (Pearson, 2004)
- Chopra & Meindl, Ch.13 — Warehouse Management (Pearson, 2016)
- Roodbergen, K.J. & Vis, I.F.A. (2006). "A survey of literature on automated storage and retrieval systems." *EJOR* 194(2).
- WERC DC Measures — DC Metrics and Benchmarking Study (annual)
- GS1 General Specifications v23.0 — SSCC, GLN, GTIN
- ISO 9001:2015 §8.5.2 — Identification and traceability
- APICS/ASCM Dictionary, 17th ed. (2024) — *FEFO*, *putaway*, *slotting*, *cycle count*
