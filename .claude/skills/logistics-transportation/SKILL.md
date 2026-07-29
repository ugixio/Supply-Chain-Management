---
description: >
  Logistics and transportation domain expertise for Department 07. Use when reviewing
  shipments, Incoterms 2020, customs declarations, hazmat (IMDG/ADR), carrier
  selection, freight cost, or the concept nodes and rules of department 07 (logistics-transportation).
---

# Logistics & Transportation — Department 07 Skills Reference

## Supply Chain Domain

**SCOR-DS Mapping**: Deliver (D1.8 Ship Product, D1.9 Receive Product at Customer)

**Incoterms® 2020 (ICC, 2019) — 11 Rules**
| Rule | Risk Transfer | Who Arranges Main Carriage |
|------|-------------|---------------------------|
| EXW | At seller's door | Buyer |
| FCA | Named place | Buyer (rail/road/air/sea) |
| CPT | Destination port | Seller |
| CIP | Destination (insured) | Seller |
| DAP | Named destination | Seller |
| DPU | Unloaded at destination | Seller (replaces DAT) |
| DDP | Seller delivers duty paid | Seller (maximum obligation) |
| FAS | Alongside vessel | Buyer |
| FOB | On board vessel | Buyer |
| CFR | Destination port | Seller (no insurance) |
| CIF | Destination port (insured) | Seller |

**Customs & Trade Compliance**
- HS Code (Harmonized System): 6-digit worldwide; 8–10 digit national
- AES filing: US exports > $2,500 (EEI via AES); Canadian B13A
- Import: CBP Form 7501; EU SAD (Single Administrative Document)
- AEO (EU) / C-TPAT (US): trusted trader; reduced inspection rates
- WTO TFA Art.7: pre-arrival processing; single window

**Hazmat Regulations**
| Mode | Regulation | Classification |
|------|-----------|---------------|
| Sea | IMDG Code (IMO) | 9 hazard classes |
| Road (EU) | ADR | 9 hazard classes |
| Air | IATA DGR | 9 hazard classes |
| Rail | RID | 9 hazard classes |
| US Road | DOT 49 CFR | 9 hazard classes |

**Transport metrics (APICS CPIM; Christopher Ch.5)**

**Metrics — definitions, not levels.** A skill states what a metric measures and what
constrains the answer; the level a project must clear is that project's decision (ADR-0037,
and the inclusion test in `CLAUDE.md`). The right-hand column names the constraint so the
question can be asked properly, and stops.

| Metric | Formula | What constrains the level |
|---|---|---|
| On-time delivery | On-time deliveries / Total × 100 | **First, which date counts** — requested, confirmed or promised — because the same shipments score differently against each (CPT-0082). Then the service commitment. Note: *"world-class OTD ≥ 95%"* is the textbook illustration `CLAUDE.md` names as the anti-pattern. |
| Transit-time adherence | Actual ≤ quoted transit / Total × 100 | The carrier's quoted transit and the tolerance the contract allows around it. |
| Freight cost per unit | Total freight spend / Total units | The lane mix, mode and fuel market. Comparable across periods only if the mix is held constant. |
| Carrier OTD | Carrier on-time / Carrier total × 100 | The carrier agreement. How heavily OTD weighs against cost and damage in a carrier scorecard is the sourcing strategy's call (CPT-0102 family). |
| Claims rate | Freight claims / Total shipments × 100 | Product fragility, packaging and the claim threshold — a low-value claim often goes unfiled, which biases the metric. |
| CO₂ per shipment | kg CO₂ / tonne-km | **The GHG Protocol fixes the method**, not the trajectory. Any reduction path is a corporate commitment; the metric's honesty depends on using the *actual routed* distance, not great-circle. |

## Data Analytics

**Carrier Performance Scorecard**
```sql
SELECT carrier_id,
       COUNT(*) AS total_shipments,
       SUM(CASE WHEN actual_delivery_date <= promised_date THEN 1 ELSE 0 END)::float
         / NULLIF(COUNT(*), 0) * 100 AS otd_pct,
       AVG(EXTRACT(DAY FROM actual_delivery_date - shipped_date)) AS avg_transit_days,
       SUM(freight_cost_cents) / 100.0 AS total_spend_usd,
       SUM(claim_amount_cents) / 100.0 AS total_claims_usd,
       ROUND(SUM(claim_amount_cents)::float / NULLIF(SUM(freight_cost_cents), 0) * 100, 3) AS claim_rate_pct
FROM shipments
WHERE shipped_date >= CURRENT_DATE - INTERVAL '12 months'
GROUP BY carrier_id ORDER BY otd_pct DESC;
```

**Freight Cost Analysis by Mode**
```sql
SELECT transport_mode, incoterm_rule,
       COUNT(*) AS shipments,
       ROUND(AVG(freight_cost_cents / 100.0), 2) AS avg_cost_usd,
       ROUND(AVG(freight_cost_cents::float / NULLIF(gross_weight_kg, 0)), 2) AS cost_per_kg,
       ROUND(AVG(EXTRACT(DAY FROM actual_delivery_date - shipped_date)), 1) AS avg_transit_days
FROM shipments GROUP BY transport_mode, incoterm_rule ORDER BY avg_cost_usd DESC;
```

## Data Science

**Route Optimization (VRP)**
- Problem: multi-stop delivery route for fleet vehicles
- Objective: minimize total distance (or cost or CO₂)
- Constraints: vehicle capacity, time windows, driver hours
- Method: OR-Tools CVRPTW solver (Clarke-Wright + local search)

**Mode Selection Model**
- Features: weight, volume, urgency, distance, commodity value, hazmat flag
- Decision: road/rail/sea/air selection
- Rule-based + ML: LightGBM classifier trained on 3 years historical mode choices
- Agreement with expert decisions is the validation measure; the level that counts as usable is
  a project decision

**Carbon Footprint Calculation** (GHG Protocol — Scope 3, Category 4)
```
CO₂e = Distance (km) × Weight (tonnes) × Emission Factor (kg CO₂e / tonne-km)
```
| Mode | Emission Factor (avg) |
|------|----------------------|
| Road (truck) | 0.062 kg CO₂e/tkm |
| Rail | 0.028 kg CO₂e/tkm |
| Sea (container) | 0.011 kg CO₂e/tkm |
| Air | 0.602 kg CO₂e/tkm |

## Machine Learning

**Delivery Delay Prediction**
```python
from lightgbm import LGBMClassifier
import pandas as pd

def train_delay_predictor(df: pd.DataFrame) -> LGBMClassifier:
    """
    Predict shipment delay probability at order-of-departure time.
    Features: carrier_id, origin_country, dest_country, transport_mode,
              gross_weight_kg, hazmat_flag, days_to_promised, weather_index,
              port_congestion_index, carrier_historical_otd.
    Target: delayed (bool) — actual > promised.
    License: LightGBM MIT.
    """
    features = ['carrier_enc', 'origin_country_enc', 'dest_country_enc',
                'mode_enc', 'gross_weight_kg', 'hazmat_flag',
                'days_to_promised', 'carrier_historical_otd']
    model = LGBMClassifier(n_estimators=300, learning_rate=0.05, random_state=42)
    model.fit(df[features], df['delayed'])
    return model
```

**Fleet Route Optimization (OR-Tools)**
```python
from ortools.constraint_solver import routing_enums_pb2, pywrapcp

def solve_cvrp(distance_matrix: list[list[int]], demands: list[int],
               vehicle_capacity: int, num_vehicles: int) -> list[list[int]]:
    """
    Capacitated VRP — optimize delivery routes for a fleet.
    Ref: Dantzig & Ramser (1959), Management Science 6(1).
    License: OR-Tools Apache-2.0.
    """
    manager = pywrapcp.RoutingIndexManager(len(distance_matrix), num_vehicles, 0)
    routing = pywrapcp.RoutingModel(manager)
    def dist_cb(from_idx, to_idx):
        return distance_matrix[manager.IndexToNode(from_idx)][manager.IndexToNode(to_idx)]
    transit_idx = routing.RegisterTransitCallback(dist_cb)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_idx)
    # Capacity constraint
    def demand_cb(idx): return demands[manager.IndexToNode(idx)]
    demand_idx = routing.RegisterUnaryTransitCallback(demand_cb)
    routing.AddDimensionWithVehicleCapacity(demand_idx, 0, [vehicle_capacity]*num_vehicles, True, 'Capacity')
    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    solution = routing.SolveWithParameters(params)
    routes = []
    for v in range(num_vehicles):
        idx, route = routing.Start(v), []
        while not routing.IsEnd(idx):
            route.append(manager.IndexToNode(idx))
            idx = solution.Value(routing.NextVar(idx))
        routes.append(route)
    return routes
```

## Python

| Library | Use | License |
|---------|-----|---------|
| `pandas` | Shipment DataFrames, carrier analysis | BSD-3 |
| `numpy` | Cost/distance calculations | BSD-3 |
| `ortools` | VRP, routing, scheduling | Apache-2.0 |
| `lightgbm` | Delay prediction, mode selection | MIT |
| `networkx` | Transport network graph | BSD-3 |
| `geopandas` | Geospatial route mapping | BSD-3 |
| `scipy.optimize` | Cost minimization, carrier allocation | BSD-3 |

## TypeScript

**Domain Objects**
- `domain/Shipment.ts` — Shipment aggregate; Incoterms; carrier; hazmat class
- `domain/CustomsDeclaration.ts` — HS codes; duties; AES/SAD filing
- `customs/HazmatManifest.ts` — IMDG/ADR classification; emergency contacts
- `services/LogisticsService.ts` — Carrier selection; rate shopping; booking

**Incoterms Validation**
```typescript
const INCOTERMS_2020 = ['EXW','FCA','CPT','CIP','DAP','DPU','DDP','FAS','FOB','CFR','CIF'] as const;
type Incoterm2020 = typeof INCOTERMS_2020[number];

function validateIncoterm(term: string): Incoterm2020 {
  if (!INCOTERMS_2020.includes(term as Incoterm2020)) {
    throw new Error(`Invalid Incoterm: ${term}. DAT was replaced by DPU in Incoterms® 2020.`);
  }
  return term as Incoterm2020;
}
```

## OSI / Commercial

| Tool | License | Use |
|------|---------|-----|
| PostgreSQL | PostgreSQL (OSI) | Shipment events, carrier rates |
| Apache Superset | Apache-2.0 | Freight cost, OTD dashboards |
| `ortools` | Apache-2.0 | Route optimization |
| `geopandas` | BSD-3 | Route mapping, distance calc |
| OpenSearch | Apache-2.0 | Customs document search |

**References**
- ICC, *Incoterms® 2020* (ICC, 2019) — official 11 rules with DPU replacing DAT
- IMO IMDG Code (2022 Ed., Amendment 41-22) — sea hazardous goods
- ADR 2023 — European Agreement on Dangerous Goods by Road (UNECE)
- GHG Protocol, *Corporate Value Chain (Scope 3) Accounting and Reporting Standard* (WRI/WBCSD, 2011)
- Christopher, M., *Logistics and Supply Chain Management*, 6th Ed., Ch.5 (FT Publishing, 2022)
- APICS/ASCM Dictionary, 17th ed. (2024) — *freight*, *carrier*, *transit time*, *customs*
- WTO TFA (2017) — Trade Facilitation Agreement, Article 7
