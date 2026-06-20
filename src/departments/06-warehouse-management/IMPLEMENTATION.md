# Warehouse Management System — Implementation Guide

**Document Classification:** Internal — Restricted Distribution
**Version:** 1.0.0
**Effective Date:** 2026-06-20
**Owner:** Supply Chain Centre of Excellence
**Applicable Standard:** SCOR-DS · ISO 28000:2022 · GS1 General Specifications v23.0 · ISO 9001:2015

---

## Table of Contents

1. Executive Summary
2. Prerequisites and Dependencies
3. Phase 0: Assessment and AS-IS Analysis
4. Phase 1: Foundation and Master Data
5. Phase 2: Process Standardisation and Core Analytics
6. Phase 3: Mathematical Models
7. Phase 4: ML/AI Pipeline
8. Phase 5: Integration and Automation
9. Phase 6: Continuous Improvement
10. Technology Stack and Architecture
11. Change Management and Training
12. Implementation KPIs
13. Risk and Mitigation
14. Timeline Summary
15. References

---

## 1. Executive Summary

This document defines the full-lifecycle implementation programme for the Warehouse Management System (WMS) module within the enterprise Supply Chain Management platform. The implementation targets global distribution centres operating under ISO 28000:2022, SCOR-DS, and GS1 compliance requirements, serving a multinational corporation with complex inventory profiles including temperature-controlled, REACH-regulated, and lot-tracked stock-keeping units.

The programme is structured across six sequential phases spanning approximately 52 weeks. Phases 0 through 2 establish the analytical baseline, master data governance, and core process standardisation. Phase 3 deploys mathematical optimisation models for slotting, labour, dock operations, and wave planning. Phase 4 overlays a machine learning and computer vision pipeline to enable predictive slotting, automated receiving inspection, and intelligent pick routing. Phases 5 and 6 complete the integration to upstream ERP and downstream carrier systems and embed continuous improvement governance.

Expected outcomes upon full deployment:
- Pick productivity improvement: 18 to 25 percent
- Dock-to-stock cycle time reduction to under two hours for standard receipts
- Slotting travel distance ratio reduction of 20 to 30 percent
- Inventory accuracy at 99.8 percent or above via cycle counting and event-sourced audit trail
- Full FEFO compliance for all temperature-controlled and REACH SVHC lots
- Zero-defect GS1 SSCC label compliance across all outbound pallets

This guide is intended for programme managers, solution architects, domain engineers, and warehouse operations leadership. All formulas, code patterns, and decision tables included herein are authoritative and must be implemented as specified. Deviations require Change Advisory Board approval and updated variance documentation.

---

## 2. Prerequisites and Dependencies

### 2.1 Organisational Prerequisites

| Prerequisite | Owner | Due Before Phase |
|---|---|---|
| Executive sponsor identified and formally appointed | COO | Phase 0 |
| Change Management lead assigned | HR/COE | Phase 0 |
| Warehouse operations SMEs allocated (minimum 0.5 FTE per DC) | Operations | Phase 0 |
| IT infrastructure baseline documented (servers, network, RF coverage) | IT | Phase 0 |
| Data governance policy ratified | CDO | Phase 1 |
| Master data stewards assigned per domain | Data Office | Phase 1 |

### 2.2 Technical Prerequisites

**Runtime Environment**
- Node.js >= 20 LTS (TypeScript domain logic)
- Python >= 3.11 (mathematical models and ML pipeline)
- PostgreSQL >= 15 (event store and operational database)
- Redis >= 7 (distributed locks, idempotency cache)
- Message broker: Apache Kafka 3.x (event streaming)

**Python Library Dependencies**

All libraries must be OSI-licensed. Install via `requirements.txt`:

```
numpy>=1.26.0
scipy>=1.12.0
pandas>=2.2.0
scikit-learn>=1.4.0
xgboost>=2.0.0
torch>=2.2.0
ultralytics>=8.1.0
pytesseract>=0.3.10
pdfplumber>=0.11.0
opencv-python>=4.9.0
ortools>=9.9.0
statsmodels>=0.14.0
simpy>=4.1.0
networkx>=3.3
```

**TypeScript Dependencies**

All dependencies in `package.json` must remain OSI-compliant (MIT, BSD, Apache-2.0).

### 2.3 Domain Dependencies

The warehouse module has runtime dependencies on the following bounded contexts:

| Dependency | Interface | Data Consumed |
|---|---|---|
| `01-procurement` | Event subscription | Purchase Order receipts (ASN events) |
| `02-inventory` | Shared event store | Stock movements, lot master, InventoryItem master |
| `03-logistics` | REST + event | Shipment schedules, carrier assignments, Incoterms |
| `04-supplier-management` | Read model | Supplier reliability scores (OTD, OTIF) |
| `05-quality` | Event subscription | Inspection hold and release events |
| `07-compliance` | Synchronous query | UFLPA and REACH status per lot |

### 2.4 Data Prerequisites

The following master data sets must be clean and loaded before Phase 1 cut-over:

- SKU master: UOM, dimensions (L x W x H in mm), gross weight (kg), storage condition, `reachSVHC` flag, `lotTracked` flag, ABC-XYZ classification
- Lot master: lot number, manufacture date, expiry date, supplier lot reference
- Location master: warehouse, zone, aisle, rack, bin — with cubic dimensions
- Equipment master: fork trucks, reach trucks, conveyor line IDs
- Carrier master: SCAC codes, SLA windows, dock door assignments

---

## 3. Phase 0: Assessment and AS-IS Analysis

**Duration:** Weeks 1 to 4
**Objective:** Establish baseline performance metrics, identify gap between current state and target operating model, and build business case for investment.

### 3.1 Site Survey Protocol

Each distribution centre under scope must complete a structured survey covering:

1. **Physical layout audit:** Number of dock doors (inbound / outbound / cross-dock), aisle widths, rack height, mezzanine structures, ambient / cold / freezer zone demarcation, fire suppression zones, and hazmat segregation areas.
2. **IT infrastructure audit:** RF coverage heat map (2.4 GHz and 5 GHz bands), wired network drops at pack stations, label printer models and firmware, WMS terminal hardware (handheld, vehicle-mounted, voice headset).
3. **Labour time study:** Direct observation of minimum 200 pick lines per shift across three shifts. Record travel time, pick dwell time, pack time, exception handling time. Apply MOST (Maynard Operation Sequence Technique) or MTM-UAS if available.
4. **Current slotting analysis:** Export full location master with velocity data (picks per SKU per week for trailing 13 weeks). Calculate current travel distance index.
5. **Process documentation review:** Receive, putaway, replenishment, pick, pack, ship, returns, cycle count, cross-dock.

### 3.2 AS-IS KPI Baseline

Capture the following metrics at each site for the trailing 12 months:

| KPI | Formula | Baseline Target |
|---|---|---|
| Lines per person-hour (LPPH) | Total lines picked / total direct labour hours | Establish site baseline |
| Dock-to-stock time (mean) | Time from dock door open to system receipt confirmed | Establish site baseline |
| Inventory accuracy | (Counted locations matching system / total locations counted) x 100 | >= 98% |
| Order fill rate | Orders shipped complete and on time / orders released | >= 97% |
| Slotting compliance | Locations per golden zone plan / total active locations | Establish site baseline |
| FEFO compliance | Lots picked in expiry order / lots picked requiring FEFO | 100% |
| Pallet SSCC label error rate | Labels with defects detected at scan gate / total labels | < 0.1% |

### 3.3 Gap Analysis Output

Produce a structured gap analysis document per site with prioritised remediation actions, mapped to programme phases. The gap analysis must explicitly address:

- Negative inventory risk (business rule: negative inventory must not occur unless `backorderAllowed = true`)
- Lot tracking gaps (business rule: lot tracking mandatory for `storageCondition !== AMBIENT` or `reachSVHC = true`)
- Soft-delete compliance (business rule: no hard deletes on any stock movements, shipments, or location records)
- GS1 SSCC label compliance for all outbound pallets

---

## 4. Phase 1: Foundation and Master Data

**Duration:** Weeks 5 to 12
**Objective:** Establish location master, item-location assignments, GS1 label configuration, event store schema, and idempotent stock movement framework.

### 4.1 Location Hierarchy Design

The warehouse location hierarchy follows a five-level model:

```
Warehouse
  └── Zone (AMBIENT / COLD_CHAIN / FREEZER / HAZMAT / RETURNS / QUARANTINE / BULK)
        └── Aisle (alphanumeric: A01 ... Z99)
              └── Rack (01 ... 99, left-to-right when facing rack)
                    └── Bin (01 ... 99, bottom-to-top)
```

Location code format: `{WH_CODE}-{ZONE}-{AISLE}{RACK}-{BIN}`
Example: `DC01-AMB-A0312-04`

Each bin record in the location master must carry:

```typescript
interface WarehouseLocation {
  locationId: string;              // Primary key, immutable
  warehouseCode: string;
  zone: StorageZone;
  aisle: string;
  rack: string;
  bin: string;
  cubicCapacityMm3: number;        // Internal cubic volume in cubic millimetres
  maxWeightGrams: number;          // Maximum gross weight capacity
  isPickLocation: boolean;
  isReserveLocation: boolean;
  isDockStaging: boolean;
  isActive: boolean;
  isDeleted: boolean;              // Soft-delete only — never hard-delete
  goldenZone: GoldenZone;          // PRIMARY / SECONDARY / TERTIARY / BULK
  assignedSku?: string;            // Dedicated location, if applicable
  createdAt: ISOTimestamp;
  updatedAt: ISOTimestamp;
}
```

### 4.2 GS1 SSCC Label Compliance

All pallets built within the warehouse must carry a compliant GS1 Serial Shipping Container Code (SSCC) label in accordance with GS1 General Specifications v23.0.

**SSCC structure (18 digits):**

```
Extension digit (1) + Company GS1 prefix (7-10) + Serial reference + Check digit (1)
```

**Required Application Identifiers (AIs) on label:**

| AI | Field | Mandatory |
|---|---|---|
| (00) | SSCC-18 | Yes |
| (02) | GTIN of contained items | Yes |
| (37) | Quantity of items | Yes |
| (10) | Batch / lot number | Yes if lot-tracked |
| (17) | Expiry date (YYMMDD) | Yes if perishable |
| (21) | Serial number | If serialised |
| (310n) | Net weight (kg) | Recommended |

TypeScript SSCC generation must use the `shared/types.ts` GS1 utilities and enforce check-digit validation using the standard GS1 Mod-10 algorithm.

### 4.3 Event Store Schema for Stock Movements

All inventory transactions must be persisted to the event store as immutable, append-only events. The schema follows the CQRS pattern established in `src/inventory/`.

Each movement event carries an `idempotencyKey` (UUID v4) to prevent double-posting on retry. The projection function `projectStockBalance()` must never allow the resulting balance to go negative for items where `backorderAllowed = false`.

```typescript
// Movement types relevant to warehouse operations
type WarehouseMovementType =
  | 'GOODS_RECEIPT'            // ASN receipt at dock
  | 'PUTAWAY'                  // Dock staging to reserve location
  | 'REPLENISHMENT'            // Reserve to pick location
  | 'PICK'                     // Pick location decrement
  | 'PACK'                     // Pack station consolidation
  | 'SHIP'                     // Outbound load confirmation
  | 'RETURN_FROM_CUSTOMER'     // Inbound returns
  | 'QUARANTINE_HOLD'          // Quality hold
  | 'QUARANTINE_RELEASE'       // Quality release
  | 'CYCLE_COUNT_ADJUSTMENT'   // Variance reconciliation
  | 'TRANSFER_BETWEEN_LOCATIONS';
```

---

## 5. Phase 2: Process Standardisation and Core Analytics

**Duration:** Weeks 13 to 20
**Objective:** Deploy standardised SOPs for all warehouse processes, configure core analytics dashboards, and establish cycle counting programme.

### 5.1 Standardised Process Map

**Inbound Process (Receive to Stock):**

```
ASN Receipt (EDI 856 / DESADV) --> Dock Door Assignment --> Unload & Count
--> GS1 SSCC Scan (GOODS_RECEIPT event) --> Quality Inspection Gate
--> Inspection Hold? [Yes --> QUARANTINE_HOLD event --> Hold location]
                     [No  --> PUTAWAY task generation]
--> Directed Putaway (PUTAWAY event) --> Stock Available
```

**Outbound Process (Wave to Ship):**

```
Order Release --> Wave Planning (clustering algorithm) --> Pick Task Generation
--> FEFO Lot Assignment (if required) --> Directed Pick (RF / Voice)
--> PICK event (idempotent) --> Pack Station --> Carton Build
--> Outbound SSCC Label --> Ship Confirmation (SHIP event) --> EDI DESADV
```

### 5.2 Cycle Counting Programme

Implement an ABC-driven cycle counting schedule:

| ABC Class | Frequency | Counts per Year | Accuracy Target |
|---|---|---|---|
| A | Weekly | 52 | >= 99.9% |
| B | Monthly | 12 | >= 99.5% |
| C | Quarterly | 4 | >= 98.0% |
| Lot-tracked | With each cycle | Per class | 100% lot integrity |

All count variances must generate a `CYCLE_COUNT_ADJUSTMENT` event. Variances above the threshold (default: 5 units or 2% of on-hand, whichever is lower) must require a recount and supervisor authorisation before posting.

### 5.3 Core Analytics Dashboard — Tier 1 KPIs

The following metrics must be computed daily and published to the operations dashboard:

| Metric | Computation | Alert Threshold |
|---|---|---|
| Lines per person-hour | Total lines picked / total direct hours | < 80% of site benchmark |
| Dock-to-stock mean (minutes) | Mean of (stock confirmation timestamp - dock open timestamp) | > 120 minutes |
| Order fill rate (%) | Complete on-time shipments / total orders released | < 97% |
| Inventory accuracy (%) | Correct count locations / total counted | < 99.5% |
| FEFO compliance (%) | FEFO-compliant picks / total lot-tracked picks | < 100% |
| SSCC defect rate (ppm) | Defective labels / total labels x 1,000,000 | > 1,000 PPM |

---

## 6. Phase 3: Mathematical Models

**Duration:** Weeks 21 to 30
**Objective:** Deploy and validate all quantitative optimisation models governing slotting, labour, dock operations, and wave planning.

### 6.1 ABC Velocity Slotting

#### 6.1.1 Slot Score Formula

The slot score for each SKU-location candidate pair is computed as a weighted index combining pick velocity and ergonomic penalty:

```
SlotScore(i) = w_v * V_norm(i) + w_w * (1 - W_norm(i)) + w_e * E_norm(i)
```

Where:
- `V_norm(i)` = normalised pick velocity of SKU i (picks per day, min-max scaled to [0,1])
- `W_norm(i)` = normalised average pick weight of SKU i (kg, min-max scaled to [0,1])
- `E_norm(i)` = normalised ergonomic score of target location (golden zone = 1.0, eye level = 0.9, floor = 0.5, above head = 0.4)
- `w_v = 0.60`, `w_w = 0.25`, `w_e = 0.15` (weights sum to 1.0; tuneable per site)

High-scoring SKUs are assigned to PRIMARY golden zone locations (waist-to-shoulder height, closest to pick aisle). Low-scoring SKUs are assigned to BULK reserve.

```python
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler

def compute_slot_scores(
    velocity_df: pd.DataFrame,
    w_v: float = 0.60,
    w_w: float = 0.25,
    w_e: float = 0.15
) -> pd.DataFrame:
    """
    Compute ABC velocity slot scores for each SKU.

    Parameters
    ----------
    velocity_df : pd.DataFrame
        Columns: sku_id, picks_per_day, avg_weight_kg, ergonomic_score
    w_v, w_w, w_e : float
        Weights for velocity, weight, ergonomic dimensions.

    Returns
    -------
    pd.DataFrame
        Original DataFrame with added column 'slot_score' and 'golden_zone'.
    """
    df = velocity_df.copy()
    scaler = MinMaxScaler()

    df["v_norm"] = scaler.fit_transform(df[["picks_per_day"]])
    df["w_norm"] = scaler.fit_transform(df[["avg_weight_kg"]])
    # Higher weight = lower desirability for primary zone (ergonomic penalty)
    df["slot_score"] = (
        w_v * df["v_norm"]
        + w_w * (1.0 - df["w_norm"])
        + w_e * df["ergonomic_score"]
    )

    # Golden zone assignment thresholds (percentile-based)
    p75 = df["slot_score"].quantile(0.75)
    p50 = df["slot_score"].quantile(0.50)
    p25 = df["slot_score"].quantile(0.25)

    conditions = [
        df["slot_score"] >= p75,
        (df["slot_score"] >= p50) & (df["slot_score"] < p75),
        (df["slot_score"] >= p25) & (df["slot_score"] < p50),
    ]
    choices = ["PRIMARY", "SECONDARY", "TERTIARY"]
    df["golden_zone"] = np.select(conditions, choices, default="BULK")

    return df[["sku_id", "slot_score", "golden_zone"]].sort_values(
        "slot_score", ascending=False
    )
```

#### 6.1.2 Golden Zone Assignment Decision Table

| Slot Score Percentile | Zone Assignment | Height Range (cm) | Distance from Aisle Entry |
|---|---|---|---|
| >= P75 | PRIMARY | 75 to 135 (waist to shoulder) | <= 5 m |
| P50 to P75 | SECONDARY | 45 to 75 or 135 to 165 | 5 to 15 m |
| P25 to P50 | TERTIARY | 20 to 45 or 165 to 190 | 15 to 30 m |
| < P25 | BULK | Floor pallet or high rack | > 30 m or reserve aisle |

### 6.2 CPOI — Cube Per Order Index

CPOI measures the cubic volume of each SKU per order line, used to optimise slot assignment so that high-cube, low-velocity items do not consume primary pick locations.

#### 6.2.1 Formula

```
CPOI(i) = (L_i x W_i x H_i) / OL_i
```

Where:
- `L_i, W_i, H_i` = dimensions of selling unit in mm
- `OL_i` = average order lines per week containing SKU i (trailing 13-week average)

A high CPOI indicates large physical size relative to order frequency. Such SKUs should be assigned to bulk or reserve locations, not primary pick slots, to maximise cubic utilisation of golden zone.

#### 6.2.2 Order Profile Analysis and Slot Assignment Optimisation

```python
def optimise_slot_by_cpoi(
    order_profile_df: pd.DataFrame,
    location_df: pd.DataFrame,
    max_primary_cube_mm3: float
) -> pd.DataFrame:
    """
    Assign SKUs to locations balancing CPOI and slot score.

    Parameters
    ----------
    order_profile_df : pd.DataFrame
        Columns: sku_id, length_mm, width_mm, height_mm, avg_order_lines_per_week,
                 slot_score, golden_zone
    location_df : pd.DataFrame
        Columns: location_id, golden_zone, cubic_capacity_mm3, is_available
    max_primary_cube_mm3 : float
        Maximum cubic volume threshold for primary zone eligibility.

    Returns
    -------
    pd.DataFrame
        Columns: sku_id, assigned_location_id, zone
    """
    df = order_profile_df.copy()
    df["unit_volume_mm3"] = df["length_mm"] * df["width_mm"] * df["height_mm"]
    df["cpoi"] = df["unit_volume_mm3"] / df["avg_order_lines_per_week"].clip(lower=0.01)

    # Demote high-CPOI SKUs from primary even if velocity is high
    df.loc[
        (df["golden_zone"] == "PRIMARY") & (df["unit_volume_mm3"] > max_primary_cube_mm3),
        "golden_zone"
    ] = "SECONDARY"

    primary_skus = df[df["golden_zone"] == "PRIMARY"].sort_values(
        "slot_score", ascending=False
    )
    primary_locs = location_df[
        (location_df["golden_zone"] == "PRIMARY") & (location_df["is_available"])
    ].sort_values("cubic_capacity_mm3", ascending=True)

    assignments = []
    loc_iter = iter(primary_locs.itertuples())
    current_loc = next(loc_iter, None)

    for _, sku_row in primary_skus.iterrows():
        if current_loc is None:
            break
        assignments.append({
            "sku_id": sku_row["sku_id"],
            "assigned_location_id": current_loc.location_id,
            "zone": "PRIMARY"
        })
        current_loc = next(loc_iter, None)

    return pd.DataFrame(assignments)
```

### 6.3 FEFO Lot Picking

#### 6.3.1 Business Rule

FEFO (First Expiry First Out) lot picking is **mandatory** for any SKU where:
- `storageCondition !== 'AMBIENT'`, OR
- `reachSVHC === true`

Violation of FEFO constitutes a regulatory compliance failure under ISO 9001:2015 §8.5.2 (traceability) and EU REACH 1907/2006.

#### 6.3.2 Lot Selection Algorithm

```python
from datetime import date, timedelta
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class LotRecord:
    lot_id: str
    sku_id: str
    expiry_date: date
    quantity_on_hand: float
    location_id: str
    storage_condition: str  # AMBIENT | COLD_CHAIN | FREEZER | CONTROLLED
    reach_svhc: bool

def select_fefo_lots(
    available_lots: List[LotRecord],
    required_quantity: float,
    pick_date: date,
    min_remaining_shelf_life_days: int = 30
) -> List[dict]:
    """
    Select lots using FEFO algorithm with minimum shelf-life threshold.

    Parameters
    ----------
    available_lots : List[LotRecord]
        All available lots for the SKU, unsorted.
    required_quantity : float
        Total quantity to fulfil.
    pick_date : date
        Date of pick operation.
    min_remaining_shelf_life_days : int
        Minimum acceptable remaining shelf life at time of pick.
        Default 30 days; override per customer SLA or product policy.

    Returns
    -------
    List[dict]
        Ordered list of {lot_id, location_id, quantity_to_pick} records.

    Raises
    ------
    ValueError
        If required quantity cannot be fulfilled with FEFO-compliant lots.
    """
    fefo_required = any(
        lot.storage_condition != "AMBIENT" or lot.reach_svhc
        for lot in available_lots
    )

    eligible_lots = [
        lot for lot in available_lots
        if (lot.expiry_date - pick_date).days >= min_remaining_shelf_life_days
    ]

    if fefo_required:
        sorted_lots = sorted(eligible_lots, key=lambda x: x.expiry_date)
    else:
        # FIFO fallback for ambient, non-SVHC items
        sorted_lots = sorted(eligible_lots, key=lambda x: x.expiry_date)

    picks = []
    remaining = required_quantity

    for lot in sorted_lots:
        if remaining <= 0:
            break
        pick_qty = min(lot.quantity_on_hand, remaining)
        picks.append({
            "lot_id": lot.lot_id,
            "location_id": lot.location_id,
            "quantity_to_pick": pick_qty,
            "expiry_date": lot.expiry_date.isoformat(),
            "days_remaining": (lot.expiry_date - pick_date).days
        })
        remaining -= pick_qty

    if remaining > 0:
        raise ValueError(
            f"Insufficient FEFO-eligible stock: shortfall of {remaining} units. "
            f"Check lots expiring within {min_remaining_shelf_life_days} days."
        )

    return picks
```

#### 6.3.3 Shelf-Life Threshold Policy

| Storage Condition | Minimum Remaining Shelf Life at Pick | Rationale |
|---|---|---|
| AMBIENT (non-SVHC) | 30 days | Customer delivery buffer |
| COLD_CHAIN | 45 days | Cold chain transit time buffer |
| FREEZER | 60 days | Extended transit and retailer dwell |
| CONTROLLED (pharma) | 90 days | Regulatory dossier requirement |
| REACH SVHC (any condition) | 60 days | EU REACH downstream user notification window |

### 6.4 Cubic Space Utilisation

#### 6.4.1 Zone-Aisle-Rack-Bin Hierarchy Fill Rate Targets

Cubic utilisation is tracked at each level of the hierarchy. The fill rate is computed as:

```
FillRate(level) = SUM(volume_occupied_mm3 at level) / SUM(cubic_capacity_mm3 at level)
```

| Hierarchy Level | Target Fill Rate | Alert Threshold |
|---|---|---|
| Bin | 75 to 85% | > 90% (over-dense) or < 50% (under-utilised) |
| Rack | 70 to 80% | > 88% or < 45% |
| Aisle | 65 to 75% | > 85% or < 40% |
| Zone | 60 to 70% | > 82% or < 35% |
| Warehouse | 55 to 65% | > 80% (triggers expansion review) |

The 5 to 10 percentage point buffer below maximum at each level reserves capacity for peak season surge, returns processing, and quarantine overflow.

```python
def compute_cubic_utilisation(
    inventory_df: pd.DataFrame,
    location_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Compute cubic space utilisation at each hierarchy level.

    Parameters
    ----------
    inventory_df : pd.DataFrame
        Columns: location_id, occupied_volume_mm3
    location_df : pd.DataFrame
        Columns: location_id, warehouse_code, zone, aisle, rack, bin,
                 cubic_capacity_mm3

    Returns
    -------
    pd.DataFrame
        Fill rates aggregated at bin, rack, aisle, zone, warehouse levels.
    """
    merged = location_df.merge(
        inventory_df.groupby("location_id")["occupied_volume_mm3"].sum().reset_index(),
        on="location_id",
        how="left"
    ).fillna({"occupied_volume_mm3": 0})

    results = {}
    for level in ["bin", "rack", "aisle", "zone", "warehouse_code"]:
        group_cols = ["warehouse_code", "zone", "aisle", "rack", "bin"][
            :["bin", "rack", "aisle", "zone", "warehouse_code"].index(level) + 1
        ]
        agg = merged.groupby(group_cols).agg(
            total_capacity=("cubic_capacity_mm3", "sum"),
            total_occupied=("occupied_volume_mm3", "sum")
        ).reset_index()
        agg["fill_rate_pct"] = (agg["total_occupied"] / agg["total_capacity"]) * 100
        results[level] = agg

    return results
```

### 6.5 Slotting Effectiveness — Travel Distance Ratio

#### 6.5.1 Travel Distance Ratio (TDR)

TDR measures how efficiently the current slotting plan routes pickers relative to a theoretical optimum (all items in nearest location to dispatch):

```
TDR = Actual_mean_pick_travel_distance_m / Optimal_mean_pick_travel_distance_m
```

- TDR = 1.00: Perfect slotting (unachievable in practice)
- TDR < 1.30: Excellent
- TDR 1.30 to 1.50: Acceptable
- TDR > 1.50: Triggers reslotting review
- TDR > 1.75: Mandatory reslotting within 30 days

Actual travel distance is measured from RF device location data or warehouse control system (WCS) pick path logs. Optimal distance is computed from location coordinates assuming direct travel (no aisle constraints).

#### 6.5.2 Reslotting Trigger Policy

Reslotting must be initiated when any of the following conditions is met:

| Trigger Condition | Measurement Period | Action |
|---|---|---|
| TDR > 1.50 | Rolling 4-week average | Schedule reslotting within 14 days |
| TDR > 1.75 | Rolling 2-week average | Mandatory reslotting within 7 days |
| Velocity rank change > 20 positions for >= 5% of SKUs | Monthly review | Partial reslot of affected zones |
| New product launches > 10 SKUs | At launch | Incremental slotting insertion |
| Seasonal peak start (4 weeks pre-peak) | Annual calendar | Full golden zone review |
| Post-peak velocity reset (2 weeks post-peak) | Annual calendar | Restore base slotting plan |

### 6.6 Labour Cost Per Pick Line

#### 6.6.1 Direct Labour Allocation Formula

```
Cost_per_line(i) = (Hourly_rate + Benefits_rate) x (Travel_time_i + Pick_dwell_i + Exception_time_i) / 3600
```

Where:
- `Hourly_rate` = direct wage rate in local currency per hour (integer cents)
- `Benefits_rate` = employer contributions as a fraction of hourly rate (typically 0.25 to 0.35)
- `Travel_time_i` = seconds per pick line for order i (from time study or WCS log)
- `Pick_dwell_i` = seconds at pick face (scan, pick, confirm)
- `Exception_time_i` = seconds for shorts, damage notations, lot scans (FEFO-tracked SKUs add ~8 to 12 seconds)

All monetary values stored as integer cents per the project Money convention.

#### 6.6.2 Efficiency Benchmarking

| Picking Method | World-Class LPPH | Acceptable LPPH | Intervention Required |
|---|---|---|---|
| Batch pick (RF) | 180 to 220 | 140 to 180 | < 120 |
| Voice-directed pick | 200 to 240 | 160 to 200 | < 135 |
| Pick-to-light | 300 to 400 | 220 to 300 | < 180 |
| Goods-to-person (AS/RS) | 400 to 600 | 300 to 400 | < 250 |
| Paper-based | 80 to 110 | 60 to 80 | < 50 |

### 6.7 Dock-to-Stock Time

#### 6.7.1 Timestamp Pipeline

Each stage in the receiving process must be system-timestamped to enable end-to-end dock-to-stock time computation:

| Timestamp Event | System Source | Field |
|---|---|---|
| T0: ASN arrival confirmed at gate | Gate reader / WMS | `asnGateTimestamp` |
| T1: Dock door opened and assigned | WMS door assignment | `dockOpenTimestamp` |
| T2: Unload complete (last pallet off truck) | RF scan confirmation | `unloadCompleteTimestamp` |
| T3: Count verification complete | RF count entry | `countVerifiedTimestamp` |
| T4: Quality inspection gate cleared | Quality module event | `inspectionClearTimestamp` |
| T5: GOODS_RECEIPT event posted | Event store | `goodsReceiptTimestamp` |
| T6: Putaway task generated | WMS task engine | `putawayTaskTimestamp` |
| T7: Last unit stocked to location | RF putaway confirm | `putawayCompleteTimestamp` |

**Dock-to-stock time = T7 - T0** (expressed in minutes).

Benchmark: <= 120 minutes for standard palletised goods. Temperature-controlled receipts: <= 90 minutes (cold chain integrity requirement).

#### 6.7.2 Benchmark Decision Table

| Dock-to-Stock Time | Status | Action |
|---|---|---|
| <= 60 min | Excellent | No action |
| 61 to 90 min | Good | Monitor |
| 91 to 120 min | Acceptable | Review bottleneck stage |
| 121 to 150 min | At-risk | Immediate supervisor intervention |
| > 150 min | Breach | Escalate to operations manager; root cause within 24h |

### 6.8 Queueing Theory for Dock Sizing — M/M/c Model

#### 6.8.1 Model Definition

The dock is modelled as a multi-server queueing system where:
- Arrivals follow a Poisson process with rate lambda (trucks per hour)
- Service times (unload + inspection + staging) follow an exponential distribution with mean 1/mu (hours per truck)
- Number of dock doors = c (servers)

The system is stable when: `lambda < c * mu` (i.e., traffic intensity rho < 1)

Traffic intensity per server: `rho = lambda / (c * mu)`

#### 6.8.2 Erlang C Application

The Erlang C formula gives the probability that an arriving truck must wait (all doors busy):

```
C(c, a) = (a^c / (c! * (1 - rho))) / [SUM_{k=0}^{c-1} (a^k / k!) + (a^c / (c! * (1 - rho)))]
```

Where `a = lambda / mu` (offered traffic in Erlangs).

Expected waiting time in queue:

```
Wq = C(c, a) / (c * mu - lambda)
```

Target: `Wq <= 15 minutes` for inbound docks, `Wq <= 10 minutes` for outbound docks.

```python
import math
from scipy.special import factorial

def erlang_c(c: int, lam: float, mu: float) -> dict:
    """
    Compute Erlang C probability and key M/M/c metrics for dock sizing.

    Parameters
    ----------
    c : int
        Number of dock doors (servers).
    lam : float
        Mean truck arrival rate (trucks per hour).
    mu : float
        Mean service rate per dock door (trucks per hour).

    Returns
    -------
    dict
        Keys: rho, erlang_c_prob, Wq_minutes, Lq, recommended_doors
    """
    if lam >= c * mu:
        return {"error": "System unstable: lambda >= c * mu. Add more dock doors."}

    rho = lam / (c * mu)
    a = lam / mu  # Offered traffic in Erlangs

    # Sum term: sum_{k=0}^{c-1} (a^k / k!)
    sum_term = sum((a ** k) / math.factorial(k) for k in range(c))
    # Queue term: a^c / (c! * (1 - rho))
    queue_term = (a ** c) / (math.factorial(c) * (1 - rho))

    ec_prob = queue_term / (sum_term + queue_term)

    # Expected wait time in queue (hours), converted to minutes
    Wq_hours = ec_prob / (c * mu - lam)
    Wq_minutes = Wq_hours * 60

    # Expected queue length
    Lq = ec_prob * rho / (1 - rho)

    # Find minimum c such that Wq <= target
    target_Wq_minutes = 15.0
    recommended_c = c
    for test_c in range(1, 30):
        if lam >= test_c * mu:
            continue
        test_rho = lam / (test_c * mu)
        test_sum = sum((a ** k) / math.factorial(k) for k in range(test_c))
        test_queue = (a ** test_c) / (math.factorial(test_c) * (1 - test_rho))
        test_ec = test_queue / (test_sum + test_queue)
        test_Wq = (test_ec / (test_c * mu - lam)) * 60
        if test_Wq <= target_Wq_minutes:
            recommended_c = test_c
            break

    return {
        "rho": round(rho, 4),
        "erlang_c_prob": round(ec_prob, 4),
        "Wq_minutes": round(Wq_minutes, 2),
        "Lq": round(Lq, 2),
        "recommended_doors": recommended_c
    }
```

#### 6.8.3 Dock Sizing Decision Table

| Peak Arrival Rate (trucks/hour) | Service Rate per Door (trucks/hour) | Minimum Doors for Wq <= 15 min |
|---|---|---|
| 2 | 1.0 | 3 |
| 4 | 1.0 | 5 |
| 6 | 1.0 | 8 |
| 8 | 1.5 | 7 |
| 10 | 1.5 | 8 |
| 12 | 2.0 | 8 |

Always round up to the next even integer (operational constraint: doors allocated in pairs for bi-directional flow).

### 6.9 Yard Dwell Time and Detention Fee Calculation

#### 6.9.1 Definitions

- **Free time:** The contractually agreed period during which a carrier's trailer may occupy a dock or yard position without incurring detention charges. Standard: 2 hours for inbound, 1 hour for outbound.
- **Detention fee:** Penalty charged per hour (or part-hour) beyond free time. Standard rate per carrier SLA.
- **Yard dwell time:** Total elapsed time from yard check-in scan to yard check-out scan.

#### 6.9.2 Detention Fee Calculation

```
DetentionFee(carrier, trailer) = MAX(0, YardDwellTime - FreeTimeHours) x HourlyRate_cents
```

All fees stored as integer cents. Partial hours rounded up to the next full hour.

```typescript
function calculateDetentionFee(
  yardCheckInTimestamp: ISOTimestamp,
  yardCheckOutTimestamp: ISOTimestamp,
  freeTimeHours: number,
  hourlyRateCents: number
): number {
  const dwellMs =
    new Date(yardCheckOutTimestamp).getTime() -
    new Date(yardCheckInTimestamp).getTime();
  const dwellHours = dwellMs / (1000 * 60 * 60);
  const billableHours = Math.max(0, Math.ceil(dwellHours - freeTimeHours));
  return billableHours * hourlyRateCents;
}
```

#### 6.9.3 Carrier SLA Enforcement Policy

| Dwell Time Overage | Action |
|---|---|
| 0 to 30 min over free time | Log only; courtesy notification to carrier |
| 31 to 60 min over free time | Automated detention fee accrual; carrier portal notification |
| > 60 min over free time | Detention fee accrual + carrier scorecard debit (OTD penalty) |
| Repeat offender (3+ incidents in 30 days) | Escalate to carrier account manager; schedule performance review |
| > 4 hours dwell (inbound) | Notify customs broker if international shipment; document for Incoterms liability |

### 6.10 Wave Planning — Order Clustering

Wave planning groups released orders into discrete processing waves to maximise pick path efficiency and synchronise packing and despatch with carrier collection windows.

#### 6.10.1 Clustering Dimensions

Orders are clustered by the intersection of three dimensions:

1. **Zone affinity:** Orders with picks concentrated in the same warehouse zone are grouped to minimise cross-zone travel.
2. **Carrier / time window:** Orders must be packed and staged before the carrier's scheduled collection time minus a configurable buffer (default: 90 minutes).
3. **Priority class:** Same-day, next-day, and standard orders must not be mixed in the same wave unless capacity planning requires it.

#### 6.10.2 Wave Planning Algorithm

```python
from datetime import datetime, timedelta
from typing import List, Dict
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans

def plan_waves(
    orders_df: pd.DataFrame,
    locations_df: pd.DataFrame,
    carrier_windows_df: pd.DataFrame,
    wave_capacity_lines: int = 500,
    pack_buffer_minutes: int = 90
) -> pd.DataFrame:
    """
    Cluster orders into pick waves by zone affinity, carrier window, and priority.

    Parameters
    ----------
    orders_df : pd.DataFrame
        Columns: order_id, priority_class, carrier_id, collection_time (ISO),
                 order_lines (list of {sku_id, location_id})
    locations_df : pd.DataFrame
        Columns: location_id, zone, aisle_x_coord, rack_y_coord
    carrier_windows_df : pd.DataFrame
        Columns: carrier_id, scheduled_collection_time
    wave_capacity_lines : int
        Maximum pick lines per wave.
    pack_buffer_minutes : int
        Minutes before collection time by which packing must complete.

    Returns
    -------
    pd.DataFrame
        Columns: wave_id, order_id, zone_cluster, carrier_id, wave_start_time
    """
    # Explode order lines and join location coordinates
    lines = orders_df.explode("order_lines")
    lines["location_id"] = lines["order_lines"].apply(lambda x: x["location_id"])
    lines = lines.merge(locations_df[["location_id", "zone", "aisle_x_coord", "rack_y_coord"]],
                        on="location_id", how="left")

    # Compute zone centroid per order
    order_centroids = (
        lines.groupby("order_id")
        .agg(
            mean_x=("aisle_x_coord", "mean"),
            mean_y=("rack_y_coord", "mean"),
            dominant_zone=("zone", lambda x: x.mode()[0]),
            priority_class=("priority_class", "first"),
            carrier_id=("carrier_id", "first"),
            collection_time=("collection_time", "first"),
            line_count=("location_id", "count")
        )
        .reset_index()
    )

    # Determine deadline for wave release (collection - buffer)
    order_centroids["wave_deadline"] = pd.to_datetime(
        order_centroids["collection_time"]
    ) - timedelta(minutes=pack_buffer_minutes)

    # Sort by priority then deadline
    priority_order = {"SAME_DAY": 0, "NEXT_DAY": 1, "STANDARD": 2}
    order_centroids["priority_rank"] = order_centroids["priority_class"].map(priority_order)
    order_centroids = order_centroids.sort_values(["priority_rank", "wave_deadline"])

    # Greedy wave assignment
    waves = []
    wave_id = 1
    current_wave_lines = 0
    current_wave_orders = []

    for _, row in order_centroids.iterrows():
        if current_wave_lines + row["line_count"] > wave_capacity_lines:
            waves.append((wave_id, current_wave_orders.copy()))
            wave_id += 1
            current_wave_lines = 0
            current_wave_orders = []

        current_wave_orders.append(row["order_id"])
        current_wave_lines += row["line_count"]

    if current_wave_orders:
        waves.append((wave_id, current_wave_orders))

    # Flatten to output DataFrame
    wave_records = []
    for wid, order_list in waves:
        for oid in order_list:
            wave_records.append({"wave_id": wid, "order_id": oid})

    return pd.DataFrame(wave_records).merge(
        order_centroids[["order_id", "carrier_id", "dominant_zone", "wave_deadline"]],
        on="order_id"
    )
```

---

## 7. Phase 4: ML/AI Pipeline

**Duration:** Weeks 31 to 42
**Objective:** Deploy machine learning models for predictive slotting, automated receiving inspection, document digitisation, and optimised pick routing.

### 7.1 Demand-Based Slotting with XGBoost

#### 7.1.1 Architecture

The XGBoost slotting model predicts future pick velocity for each SKU over a 4-week horizon, enabling proactive slotting adjustments before velocity shifts are visible in trailing averages.

**Input features:**
- Trailing 4-, 8-, 13-week pick velocity (picks per day)
- Seasonality index (week-of-year, month, pre-peak flag)
- Promotional calendar flags (active promotion, promo type)
- ABC-XYZ classification (encoded)
- Product lifecycle stage (LAUNCH, GROWTH, MATURE, DECLINE)
- Inventory coverage days (days of supply at current velocity)
- Supplier lead time (days) and variability coefficient

**Target variable:** Predicted picks per day for the upcoming 4 weeks.

**Output:** Updated slot score via `compute_slot_scores()` using predicted velocity, triggering reslotting recommendation if zone changes.

#### 7.1.2 Training Pipeline

```python
import xgboost as xgb
import pandas as pd
import numpy as np
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import LabelEncoder

def train_velocity_predictor(
    features_df: pd.DataFrame,
    target_col: str = "picks_per_day_fwd4w",
    n_splits: int = 5
) -> tuple:
    """
    Train XGBoost model for pick velocity prediction with time-series CV.

    Parameters
    ----------
    features_df : pd.DataFrame
        Feature matrix with target column. Must be sorted by date ascending.
    target_col : str
        Name of the target column.
    n_splits : int
        Number of time-series cross-validation folds.

    Returns
    -------
    tuple
        (trained_model, feature_importance_df, cv_metrics_dict)
    """
    cat_cols = ["abc_class", "xyz_class", "lifecycle_stage", "storage_condition"]
    le = LabelEncoder()
    df = features_df.copy()
    for col in cat_cols:
        if col in df.columns:
            df[col] = le.fit_transform(df[col].astype(str))

    feature_cols = [c for c in df.columns if c not in [target_col, "date", "sku_id"]]
    X = df[feature_cols].values
    y = df[target_col].values

    tscv = TimeSeriesSplit(n_splits=n_splits)
    cv_maes, cv_rmses = [], []

    best_model = None
    for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
        X_train, X_val = X[train_idx], X[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]

        dtrain = xgb.DMatrix(X_train, label=y_train)
        dval = xgb.DMatrix(X_val, label=y_val)

        params = {
            "objective": "reg:squarederror",
            "learning_rate": 0.05,
            "max_depth": 6,
            "n_estimators": 500,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "min_child_weight": 5,
            "tree_method": "hist",
            "seed": 42
        }

        model = xgb.train(
            params,
            dtrain,
            num_boost_round=500,
            evals=[(dval, "val")],
            early_stopping_rounds=30,
            verbose_eval=False
        )

        preds = model.predict(dval)
        mae = mean_absolute_error(y_val, preds)
        rmse = np.sqrt(mean_squared_error(y_val, preds))
        cv_maes.append(mae)
        cv_rmses.append(rmse)
        best_model = model  # Retain last fold model; in production use ensemble

    feature_importance = pd.DataFrame({
        "feature": feature_cols,
        "importance": best_model.get_score(importance_type="gain").values()
    }).sort_values("importance", ascending=False)

    cv_metrics = {
        "mean_mae": np.mean(cv_maes),
        "std_mae": np.std(cv_maes),
        "mean_rmse": np.mean(cv_rmses),
        "std_rmse": np.std(cv_rmses)
    }

    return best_model, feature_importance, cv_metrics


def recompute_slot_scores_from_model(
    model: xgb.Booster,
    current_features_df: pd.DataFrame,
    threshold_zone_change: float = 0.20
) -> pd.DataFrame:
    """
    Predict velocity, recompute slot scores, flag SKUs needing reslotting.

    Parameters
    ----------
    model : xgb.Booster
        Trained XGBoost model.
    current_features_df : pd.DataFrame
        Current feature values (one row per SKU).
    threshold_zone_change : float
        Minimum relative change in slot score to flag reslotting (default 20%).

    Returns
    -------
    pd.DataFrame
        Columns: sku_id, predicted_velocity, new_slot_score, current_zone,
                 recommended_zone, reslot_flag
    """
    feature_cols = [c for c in current_features_df.columns
                    if c not in ["sku_id", "current_slot_score", "current_zone"]]
    dmatrix = xgb.DMatrix(current_features_df[feature_cols].values)
    predicted_velocity = model.predict(dmatrix)

    result = current_features_df[["sku_id", "current_slot_score", "current_zone"]].copy()
    result["predicted_velocity"] = predicted_velocity

    # Recompute slot score using predicted velocity as V_norm input
    # (simplified; full recomputation uses compute_slot_scores())
    result["velocity_change_ratio"] = (
        result["predicted_velocity"] / result["predicted_velocity"].max()
    )
    result["new_slot_score"] = result["current_slot_score"] * result["velocity_change_ratio"]

    p75 = result["new_slot_score"].quantile(0.75)
    p50 = result["new_slot_score"].quantile(0.50)
    p25 = result["new_slot_score"].quantile(0.25)

    conditions = [
        result["new_slot_score"] >= p75,
        (result["new_slot_score"] >= p50) & (result["new_slot_score"] < p75),
        (result["new_slot_score"] >= p25) & (result["new_slot_score"] < p50),
    ]
    result["recommended_zone"] = np.select(
        conditions, ["PRIMARY", "SECONDARY", "TERTIARY"], default="BULK"
    )
    result["reslot_flag"] = result["recommended_zone"] != result["current_zone"]

    return result[["sku_id", "predicted_velocity", "new_slot_score",
                   "current_zone", "recommended_zone", "reslot_flag"]]
```

### 7.2 Computer Vision for Receiving — YOLOv8 (Ultralytics)

#### 7.2.1 Architecture

A YOLOv8 instance segmentation model is deployed at inbound dock stations on camera-equipped RF terminals or fixed overhead cameras. The model performs two tasks simultaneously:

1. **Pallet damage detection:** Identifies visual defects — torn wrap, crushed corners, leaning stack, open cartons, visible product exposure.
2. **Label readability check:** Validates that GS1 SSCC barcodes and human-readable fields are unobscured and correctly oriented.

#### 7.2.2 Model Training and Deployment

```python
from ultralytics import YOLO
import cv2
import numpy as np
from pathlib import Path

def train_pallet_inspection_model(
    data_yaml_path: str,
    pretrained_weights: str = "yolov8m.pt",
    epochs: int = 100,
    image_size: int = 640,
    batch_size: int = 16,
    output_dir: str = "/models/pallet_inspection"
) -> str:
    """
    Fine-tune YOLOv8 for pallet damage and label detection.

    Parameters
    ----------
    data_yaml_path : str
        Path to dataset YAML defining train/val/test splits and class names.
        Required classes: [undamaged_pallet, damaged_pallet, sscc_label_ok,
                           sscc_label_obscured, sscc_label_missing]
    pretrained_weights : str
        YOLOv8 checkpoint (use 'yolov8m.pt' for production accuracy balance).
    epochs : int
        Training epochs. Minimum 100 for adequate convergence on domain data.
    output_dir : str
        Directory for saving model weights.

    Returns
    -------
    str
        Path to best model weights file.
    """
    model = YOLO(pretrained_weights)

    results = model.train(
        data=data_yaml_path,
        epochs=epochs,
        imgsz=image_size,
        batch=batch_size,
        project=output_dir,
        name="pallet_v1",
        patience=20,
        save=True,
        device="cuda",        # Fall back to "cpu" if GPU unavailable
        augment=True,
        mosaic=1.0,
        degrees=10.0,         # Rotation augmentation for label orientation variance
        hsv_s=0.7,            # Saturation variance for lighting conditions
        fliplr=0.5
    )

    best_weights = Path(output_dir) / "pallet_v1" / "weights" / "best.pt"
    return str(best_weights)


def inspect_pallet_image(
    model_path: str,
    image_path: str,
    confidence_threshold: float = 0.65
) -> dict:
    """
    Run pallet inspection inference on a single image frame.

    Parameters
    ----------
    model_path : str
        Path to trained YOLOv8 weights (.pt file).
    image_path : str
        Path to captured image from dock camera.
    confidence_threshold : float
        Minimum detection confidence for a positive finding.

    Returns
    -------
    dict
        Keys: pallet_damaged (bool), label_status (str: OK|OBSCURED|MISSING),
              detections (list of {class, confidence, bbox}), action_required (bool)
    """
    model = YOLO(model_path)
    img = cv2.imread(image_path)

    results = model.predict(img, conf=confidence_threshold, verbose=False)

    detections = []
    pallet_damaged = False
    label_status = "OK"

    for result in results:
        for box in result.boxes:
            cls_name = result.names[int(box.cls)]
            conf = float(box.conf)
            bbox = box.xyxy[0].tolist()

            detections.append({"class": cls_name, "confidence": conf, "bbox": bbox})

            if cls_name == "damaged_pallet" and conf >= confidence_threshold:
                pallet_damaged = True
            if cls_name == "sscc_label_obscured":
                label_status = "OBSCURED"
            if cls_name == "sscc_label_missing":
                label_status = "MISSING"

    action_required = pallet_damaged or label_status != "OK"

    return {
        "pallet_damaged": pallet_damaged,
        "label_status": label_status,
        "detections": detections,
        "action_required": action_required
    }
```

#### 7.2.3 Integration with Receiving Process

When `action_required = True`:
1. GOODS_RECEIPT event is withheld; a `QUARANTINE_HOLD` event is generated automatically.
2. A damage notice is created in the quality module (`InspectionRecord`) with photo evidence attached.
3. The RF device displays a hold message to the warehouse operator.
4. The procurement module triggers a supplier NCR if `damaged_pallet = True`.

### 7.3 OCR Pipeline — BOL and POD Digitisation

#### 7.3.1 Pipeline Architecture

```
Scanned document (PDF or image JPEG/PNG)
  --> pdfplumber (PDF text extraction — structured tables)
  --> pytesseract (OCR for image-embedded text)
  --> Field extraction (regex + NLP patterns)
  --> Structured BOL/POD record (JSON)
  --> WMS event store (GOODS_RECEIPT linkage)
```

#### 7.3.2 Implementation

```python
import pdfplumber
import pytesseract
import cv2
import numpy as np
import re
from pathlib import Path
from datetime import datetime
from typing import Optional

def extract_bol_fields(document_path: str) -> dict:
    """
    Extract structured fields from a Bill of Lading or Proof of Delivery document.

    Supports PDF (with embedded text) and scanned image formats (PNG, JPEG, TIFF).

    Parameters
    ----------
    document_path : str
        File path to the BOL or POD document.

    Returns
    -------
    dict
        Extracted fields: bol_number, shipper_name, consignee_name, carrier_scac,
        ship_date, delivery_date, sscc_list, pro_number, total_weight_kg,
        piece_count, extraction_confidence
    """
    path = Path(document_path)
    raw_text = ""

    if path.suffix.lower() == ".pdf":
        with pdfplumber.open(document_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    raw_text += page_text + "\n"
                # If page has image-embedded content, fallback to OCR
                if len(raw_text.strip()) < 50:
                    img = page.to_image(resolution=300).original
                    img_np = np.array(img)
                    raw_text += pytesseract.image_to_string(
                        img_np,
                        config="--oem 3 --psm 6"
                    )
    else:
        # Image file: apply pre-processing for OCR quality improvement
        img = cv2.imread(document_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        denoised = cv2.fastNlMeansDenoising(gray, h=10)
        _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        raw_text = pytesseract.image_to_string(binary, config="--oem 3 --psm 6")

    # Field extraction via regex patterns
    fields = {
        "bol_number": _extract_pattern(raw_text, r"B(?:OL|ill of Lading)[:\s#]*([A-Z0-9\-]{6,20})"),
        "pro_number": _extract_pattern(raw_text, r"PRO[:\s#]*([A-Z0-9\-]{6,20})"),
        "carrier_scac": _extract_pattern(raw_text, r"SCAC[:\s]*([A-Z]{4})"),
        "ship_date": _extract_date(raw_text, r"Ship(?:ped)?\s*Date[:\s]*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})"),
        "delivery_date": _extract_date(raw_text, r"Deliver(?:y|ed)?\s*Date[:\s]*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})"),
        "sscc_list": _extract_all_patterns(raw_text, r"\b00(\d{17})\b"),  # SSCC-18 without AI
        "total_weight_kg": _extract_number(raw_text, r"(?:Total\s*)?Weight[:\s]*([\d,\.]+)\s*[Kk][Gg]"),
        "piece_count": _extract_number(raw_text, r"(?:Total\s*)?(?:Pieces?|Pallets?)[:\s]*([\d,]+)"),
    }

    # Confidence: ratio of non-None fields
    extracted = sum(1 for v in fields.values() if v is not None and v != [])
    fields["extraction_confidence"] = round(extracted / (len(fields) - 1), 2)

    return fields


def _extract_pattern(text: str, pattern: str) -> Optional[str]:
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else None


def _extract_date(text: str, pattern: str) -> Optional[str]:
    raw = _extract_pattern(text, pattern)
    if not raw:
        return None
    for fmt in ("%m/%d/%Y", "%d/%m/%Y", "%m-%d-%Y", "%d-%m-%Y", "%m/%d/%y"):
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return raw


def _extract_number(text: str, pattern: str) -> Optional[float]:
    raw = _extract_pattern(text, pattern)
    return float(raw.replace(",", "")) if raw else None


def _extract_all_patterns(text: str, pattern: str) -> list:
    return re.findall(pattern, text)
```

#### 7.3.3 Validation and Reconciliation

After extraction, the BOL fields are reconciled against the WMS ASN record:

| BOL Field | WMS Field | Mismatch Action |
|---|---|---|
| `bol_number` | `asn.bolReference` | Log discrepancy; require manual confirmation |
| `sscc_list` | `asn.expectedSsccList` | Highlight unlisted SSCCs for exception processing |
| `total_weight_kg` | `asn.expectedWeightKg` | Flag variance > 2% for reweigh |
| `carrier_scac` | `shipment.carrierScac` | Alert if mismatch (potential wrong carrier) |
| `delivery_date` | `shipment.confirmedDeliveryDate` | Update WMS; trigger OTD KPI recalculation |

### 7.4 Route Optimisation within Warehouse — OR-Tools TSP

#### 7.4.1 Problem Definition

The picker routing problem within a warehouse is a Travelling Salesman Problem (TSP) variant where:
- Nodes are pick locations (bin coordinates)
- The picker starts and ends at the dispatch staging area
- Distance metric is Manhattan distance (aisle-based travel, no diagonal)
- Constraint: FEFO lot assignments are fixed before routing; routing only optimises traversal order

#### 7.4.2 OR-Tools TSP Implementation

```python
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import numpy as np
from typing import List

def optimise_pick_path(
    locations: List[dict],
    depot_coords: tuple = (0, 0),
    time_limit_seconds: int = 5
) -> List[dict]:
    """
    Optimise pick sequence using OR-Tools TSP with Manhattan distance.

    Parameters
    ----------
    locations : List[dict]
        Each dict: {pick_task_id, location_id, x_coord_m, y_coord_m, quantity, sku_id}
        Coordinates in metres from warehouse origin.
    depot_coords : tuple
        (x, y) coordinates of dispatch staging / picker start point in metres.
    time_limit_seconds : int
        Maximum solver time. For real-time wave pick tasks: 5 seconds.

    Returns
    -------
    List[dict]
        Ordered list of pick tasks with optimised sequence and estimated travel distance.
    """
    if not locations:
        return []

    all_points = [depot_coords] + [(loc["x_coord_m"], loc["y_coord_m"]) for loc in locations]
    n = len(all_points)

    # Manhattan distance matrix
    distance_matrix = np.zeros((n, n), dtype=int)
    for i in range(n):
        for j in range(n):
            distance_matrix[i][j] = int(
                abs(all_points[i][0] - all_points[j][0]) +
                abs(all_points[i][1] - all_points[j][1])
            ) * 100  # Convert to centimetres for integer precision

    manager = pywrapcp.RoutingIndexManager(n, 1, 0)  # 1 vehicle, depot = node 0
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return distance_matrix[from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    search_params = pywrapcp.DefaultRoutingSearchParameters()
    search_params.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    search_params.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_params.time_limit.seconds = time_limit_seconds

    solution = routing.SolveWithParameters(search_params)

    if not solution:
        # Fallback: return locations in original order
        return locations

    # Extract route
    route = []
    index = routing.Start(0)
    total_distance_m = 0.0

    while not routing.IsEnd(index):
        node = manager.IndexToNode(index)
        if node > 0:  # Skip depot (node 0)
            loc = locations[node - 1]
            next_index = solution.Value(routing.NextVar(index))
            next_node = manager.IndexToNode(next_index)
            arc_distance = distance_matrix[node][next_node] / 100  # Back to metres
            route.append({
                **loc,
                "pick_sequence": len(route) + 1,
                "travel_distance_to_next_m": arc_distance
            })
        index = solution.Value(routing.NextVar(index))
        total_distance_m += arc_distance if node > 0 else 0

    return route
```

---

## 8. Phase 5: Integration and Automation

**Duration:** Weeks 43 to 48
**Objective:** Complete bidirectional integrations with ERP systems, warehouse control systems, and carrier networks.

### 8.1 ERP Integration — SAP EWM

SAP Extended Warehouse Management (EWM) is the primary ERP interface for this programme. Integration uses SAP's standard IDocs and REST OData APIs.

| WMS Event | SAP EWM Interface | Direction | Protocol |
|---|---|---|---|
| Goods Receipt (GOODS_RECEIPT) | GR posting (MIGO equivalent) | WMS -> SAP | IDoc MBGMCR01 |
| Transfer Order creation (PUTAWAY) | Warehouse Task (WT) creation | WMS -> SAP | OData /API_WHSE_TASK |
| Pick confirmation (PICK) | Pick Denial / Confirmation | WMS -> SAP | OData /API_WHSE_TASK |
| Outbound Delivery (SHIP) | Post Goods Issue (PGI) | WMS -> SAP | IDoc SHPCON01 |
| Inventory Adjustment (CYCLE_COUNT_ADJUSTMENT) | MI01/MI07 equivalents | WMS -> SAP | IDoc INVPLA01 |
| ASN inbound (from SAP) | Inbound Delivery (DESADV) | SAP -> WMS | IDoc DESADV01 |

**Retry and idempotency:** All IDoc and OData calls must implement exponential backoff with jitter (initial delay 1 s, max 60 s, max 5 retries). Each call carries the WMS `idempotencyKey` mapped to the SAP `XBLNR` (external reference) field.

### 8.2 Integration — Manhattan Associates and Korber

For sites using Manhattan Active Warehouse Management or Korber WMS as the legacy system:

- **Manhattan Associates:** Integration via Manhattan's published REST APIs (MAWM 2023.x). Map WMS domain events to Manhattan's `Task`, `Container`, and `Shipment` resources.
- **Korber:** Integration via Korber's EDI gateway (EDIFACT WAREHOUSING messages) or REST API (Korber WMS 4.x). Korber uses warehouse orders (WO) and transfer orders (TO) natively aligned with WMS PUTAWAY and PICK events.

Both integrations must include:
- Heartbeat health check every 60 seconds
- Circuit breaker pattern (trip after 5 consecutive failures, half-open after 30 seconds)
- Dead letter queue for undeliverable events (Kafka DLQ topic `wms.integration.dlq`)

### 8.3 Conveyor and Sorter Systems

Integration with conveyor and sorter WCS (Warehouse Control System) uses standard TCP/IP socket communication or OPC-UA where supported.

| WCS Event | WMS Action |
|---|---|
| Sorter scan (barcode at induct point) | Match to open pick task; confirm carton identity |
| Sort assignment confirmed | Update carton-to-lane assignment in WMS |
| Pack station weight capture | Compare to expected carton weight; flag > ±5% variance |
| Merge point jam detected | Suspend wave; alert supervisor; log exception |

### 8.4 RF Devices and Voice Picking

**RF devices (handheld and vehicle-mounted):**
- Communicate with WMS via 802.11ax (Wi-Fi 6) using the WMS REST API over HTTPS/TLS 1.3.
- Scan events (GS1-128 barcodes) decoded device-side; raw barcode data sent to WMS for parsing.
- Session timeout: 15 minutes idle; reauthentication required.

**Voice picking (Honeywell Vocollect, Zebra WT6300):**
- Voice templates define pick task workflow: "Go to location A03-12-04. Pick 5 units of GTIN 0614141999996. Check digit 5. Confirm."
- WMS generates voice task XML conforming to Vocollect TaskBuilder or Zebra VoiceConsole format.
- FEFO confirmation: voice prompt includes lot number and expiry date for operator verbal confirmation before pick.

### 8.5 GS1 SSCC Label Generation — Integration Point

All outbound pallet SSCC labels must be generated by the WMS at the pack or palletise station and printed via ZPL-compatible label printers (Zebra ZT series). The label generation service must:

1. Allocate SSCC serial number from the internal serial number pool (organisation-specific, seeded from GS1 company prefix).
2. Compose GS1-128 barcode data with mandatory AIs.
3. Render ZPL template and send to assigned printer via TCP port 9100.
4. Register SSCC in event store for shipment traceability.
5. Confirm label print success; retry on failure (max 3 attempts); escalate to supervisor if all attempts fail.

---

## 9. Phase 6: Continuous Improvement

**Duration:** Weeks 49 to 52 (ongoing thereafter)
**Objective:** Embed structured continuous improvement governance, model refresh cadence, and KPI-driven intervention protocols.

### 9.1 Weekly Operations Review Cadence

| Review | Participants | KPIs Reviewed | Outputs |
|---|---|---|---|
| Daily Shift Huddle (15 min) | Shift manager, team leads | LPPH, dock-to-stock, fill rate | Immediate corrective actions |
| Weekly Operations Review (60 min) | DC manager, all team leads | Full Tier 1 KPI set | Weekly action register |
| Monthly Performance Review (90 min) | Regional SC Director, DC manager | KPI trends, slotting TDR, labour cost | Strategic decisions |
| Quarterly Slotting Review | IE team, operations, planning | TDR, velocity rank changes, CPOI | Reslotting execution plan |

### 9.2 Model Refresh Cadence

| Model | Refresh Frequency | Trigger Conditions |
|---|---|---|
| XGBoost velocity predictor | Monthly (automated) | MAE drift > 15% vs. baseline |
| ABC velocity slotting | Quarterly (minimum) | TDR > 1.50 or significant velocity shifts |
| Wave planning parameters | Monthly review | Fill rate < 97% or carrier SLA misses |
| Erlang C dock sizing | Bi-annual | Volume growth > 10% or facility changes |
| YOLOv8 pallet inspection | Quarterly (or new defect type found) | False negative rate > 2% |

### 9.3 Inventory Accuracy Programme

Maintain 99.8% inventory accuracy through:
- Continuous cycle counting (ABC-stratified schedule per Phase 2)
- Exception-based recounts triggered by any pick short (zero-balance scan or quantity mismatch)
- FEFO exception log review daily: any FEFO deviation must be investigated within 4 hours
- Annual full physical count (at year-end or fiscal year-end per entity)

---

## 10. Technology Stack and Architecture

### 10.1 Application Architecture Diagram (Textual)

```
[RF Devices / Voice Headsets / Dock Cameras]
        |
        v
[WMS API Gateway (Node.js / TypeScript)]
        |
    +---+---+
    |       |
    v       v
[Domain   [Python Mathematical Model Services]
 Logic     - Slotting Engine (Flask/FastAPI)
 (TS)]     - Wave Planning Service
           - ML Inference Service (XGBoost, YOLOv8)
           - OCR Service (pytesseract + pdfplumber)
           - Route Optimiser (OR-Tools)
        |
        v
[Apache Kafka — Event Streaming]
        |
    +---+---+---+
    |           |
    v           v
[Event Store   [Integration Layer]
 PostgreSQL]    - SAP EWM Adapter
                - Manhattan/Korber Adapter
                - Carrier EDI (DESADV, RECADV)
                - WCS Connector
```

### 10.2 Key Architectural Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Domain logic language | TypeScript | Type safety, shared types with rest of SCM platform |
| Mathematical models language | Python >= 3.11 | OSI library ecosystem (numpy, scipy, xgboost) |
| Event store | PostgreSQL (append-only table + projections) | ACID compliance, no hard-delete capability |
| Message broker | Apache Kafka 3.x | Durable, replayable event log; saga pattern support |
| ML serving | FastAPI + uvicorn | Lightweight, async, Python-native |
| CV inference hardware | NVIDIA GPU (T4 or A10) | YOLOv8 inference latency < 200 ms per frame |
| Label printing | ZPL over TCP port 9100 | Universal Zebra compatibility |
| RF device protocol | HTTPS REST over Wi-Fi 6 | Secure, standard; no proprietary middleware |

---

## 11. Change Management and Training

### 11.1 Stakeholder Map

| Stakeholder Group | Impact Level | Change Required | Engagement Strategy |
|---|---|---|---|
| Warehouse Associates (pick, pack, receive) | High | New RF / voice workflows | Hands-on training, buddy system, floor champions |
| Shift Supervisors | High | New KPI dashboards, exception management | Workshop training, process certification |
| DC Managers | Medium | New reporting cadence, ML model outputs | Executive briefings, monthly review protocol |
| IT Operations | High | System integrations, infrastructure | Technical deep-dives, runbook creation |
| Finance | Medium | New cost-per-line reporting, detention fees | Finance briefing on money/cents data model |
| Procurement | Low-Medium | ASN compliance, SSCC requirements | Supplier communication package |

### 11.2 Training Curriculum

**Warehouse Associates (8 hours total):**
- Module 1 (2h): WMS navigation, RF device operation, barcode scanning fundamentals
- Module 2 (2h): FEFO lot picking — why it matters, how to respond to system prompts
- Module 3 (2h): GS1 SSCC label compliance — what a valid label looks like, escalation path for defects
- Module 4 (2h): Exception handling — shorts, damage, quarantine holds, cycle count procedures

**Shift Supervisors (16 hours total):**
- All associate modules (8h)
- Module 5 (4h): KPI dashboard interpretation, wave release, labour allocation
- Module 6 (4h): ML model outputs — how to interpret slotting recommendations and velocity predictions

**System Administrators (24 hours total):**
- Technical runbook for all integrations (SAP EWM, Kafka, RF infrastructure)
- ML model refresh procedures
- Backup and recovery procedures for event store
- Incident response playbook

### 11.3 Go-Live Readiness Criteria

| Criterion | Measurement | Minimum Pass |
|---|---|---|
| Associate training completion | % certified | >= 95% |
| Integration test pass rate | Automated integration tests | 100% |
| Performance test pass (peak volume) | Lines per hour at 150% normal volume | System stable, < 2s response |
| FEFO logic validation | Test scenarios with lot-tracked SKUs | 100% correct |
| SSCC label compliance test | 1,000 test labels scanned at gate | 0 defects |
| Failover test | Kafka broker failure, API gateway restart | Recovery < 5 minutes |

---

## 12. Implementation KPIs

### 12.1 Programme KPIs (Tracked by PMO)

| KPI | Baseline (Pre-Implementation) | Target (12 Months Post Go-Live) |
|---|---|---|
| Lines per person-hour | Site-specific (captured Phase 0) | +20% vs. baseline |
| Dock-to-stock time (mean minutes) | Site-specific | <= 120 minutes |
| Inventory accuracy (%) | Site-specific | >= 99.8% |
| Order fill rate (%) | Site-specific | >= 97.5% |
| FEFO compliance (%) | Site-specific | 100% |
| SSCC label defect rate (PPM) | Site-specific | <= 500 PPM |
| Slotting TDR | Site-specific | <= 1.30 |
| Labour cost per pick line (cents) | Site-specific | -15% vs. baseline |
| Yard detention fees (monthly) | Site-specific | -50% vs. baseline |
| XGBoost velocity prediction MAE | N/A (new) | <= 2.0 picks/day |
| YOLOv8 pallet damage detection accuracy | N/A (new) | >= 95% precision, >= 90% recall |
| OCR BOL extraction confidence | N/A (new) | >= 85% on clean documents |

### 12.2 Operational KPIs (Tracked by DC Management)

All Tier 1 KPIs from Phase 2 section 5.3 plus:

| KPI | Formula | Target |
|---|---|---|
| Replenishment cycle time (min) | Time from pick-below-min trigger to pick location replenished | <= 30 min |
| Pallet build accuracy (%) | Correct pallet content vs. pick list | >= 99.9% |
| Wave release compliance (%) | Waves released within planned window | >= 95% |
| Carrier on-time collection (%) | Carriers arriving within ±30 min of scheduled window | Target from carrier SLA |

---

## 13. Risk and Mitigation

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Master data quality insufficient at Phase 1 cutover | High | High | Data profiling in Phase 0; data cleanse sprint before Phase 1 |
| RF coverage gaps causing scan failures at new locations | Medium | High | Wi-Fi 6 survey in Phase 0; access point upgrades before Phase 1 |
| SAP EWM integration delays (SAP basis resource contention) | High | High | Dedicate SAP basis resource to programme; mock integration stubs for parallel WMS testing |
| FEFO compliance failure during parallel run | Low | Critical | Dual-pick validation during 2-week parallel run; mandatory recount on any FEFO exception |
| YOLOv8 model false negative rate > 2% (damaged pallets not detected) | Medium | High | Manual inspection as backstop during first 90 days; retrain model quarterly |
| OCR extraction failure on handwritten or damaged BOLs | Medium | Medium | Human-in-the-loop fallback; extraction confidence < 70% triggers manual review |
| Pick productivity regression during learning curve | High | Medium | Floor champions, buddy system, daily LPPH tracking for first 8 weeks |
| Kafka broker outage causing event backlog | Low | High | Multi-broker Kafka cluster (minimum 3 nodes); consumer lag monitoring with automated alert at 10,000 messages |
| Detention fee disputes with carriers | Medium | Low | Automated yard dwell timestamps with carrier self-service portal visibility; contractual grace period pre-agreed |
| Negative inventory occurrence | Low | Critical | Event store projection enforces non-negative check; alert fires on any attempt; daily reconciliation report |

---

## 14. Timeline Summary

| Phase | Weeks | Key Deliverables |
|---|---|---|
| Phase 0: Assessment and AS-IS Analysis | 1 to 4 | Site survey reports, AS-IS KPI baselines, gap analysis per DC, business case confirmed |
| Phase 1: Foundation and Master Data | 5 to 12 | Location hierarchy built and validated, GS1 SSCC configuration complete, event store schema deployed, master data cleansed and loaded |
| Phase 2: Process Standardisation and Core Analytics | 13 to 20 | SOPs published, core analytics dashboard live, cycle counting programme running, Tier 1 KPIs reporting |
| Phase 3: Mathematical Models | 21 to 30 | ABC velocity slotting deployed, CPOI model validated, FEFO logic unit-tested 100%, dock Erlang C model calibrated, wave planning algorithm live |
| Phase 4: ML/AI Pipeline | 31 to 42 | XGBoost velocity predictor trained and validated (MAE target met), YOLOv8 pallet inspection deployed at all inbound docks, OCR pipeline live for BOL digitisation, OR-Tools pick routing integrated |
| Phase 5: Integration and Automation | 43 to 48 | SAP EWM integration end-to-end tested, Manhattan/Korber adapters validated, WCS conveyor integration live, RF/voice devices fully connected |
| Phase 6: Continuous Improvement | 49 to 52 + ongoing | CI governance active, quarterly slotting review cadence established, model refresh schedules running, KPI targets achieved and tracked |

**Total programme duration:** 52 weeks from Phase 0 kick-off to steady-state operations.

**Critical path:** Master data quality (Phase 1) -> FEFO logic validation (Phase 3) -> SAP EWM integration (Phase 5). Delays in any of these three workstreams will compress the go-live date.

---

## 15. References

### Academic and Professional References

1. Chopra, S. and Meindl, P. (2016). *Supply Chain Management: Strategy, Planning, and Operation*, 6th edition. Pearson Education.
2. Ballou, R.H. (2004). *Business Logistics / Supply Chain Management*, 5th edition. Pearson Education.
3. Christopher, M. (2022). *Logistics and Supply Chain Management*, 6th edition. FT Publishing International.
4. Frazelle, E.H. (2002). *World-Class Warehousing and Material Handling*. McGraw-Hill.
5. Erlang, A.K. (1909). The theory of probabilities and telephone conversations. *Nyt Tidsskrift for Matematik B*, 20, pp. 33-39.
6. Harris, F.W. (1913). How many parts to make at once. *Factory: The Magazine of Management*, 10(2), pp. 135-136. (EOQ origin)
7. Holt, C.C. (1957). Forecasting seasonals and trends by exponentially weighted moving averages. *ONR Memorandum* 52. Carnegie Institute of Technology.
8. Winters, P.R. (1960). Forecasting sales by exponentially weighted moving averages. *Management Science*, 6(3), pp. 324-342.

### Standards and Regulations

9. ISO 28000:2022. *Security and resilience — Security management systems — Requirements*. International Organization for Standardization.
10. ISO 9001:2015. *Quality management systems — Requirements*. International Organization for Standardization. Sections 8.4, 8.5.2, 8.6, 8.7.
11. ISO 2859-1:1999. *Sampling procedures for inspection by attributes — Part 1: Sampling schemes indexed by acceptance quality limit (AQL) for lot-by-lot inspection*. ISO.
12. GS1 General Specifications, Version 23.0 (2023). GS1 Global Office, Brussels.
13. ICC Incoterms 2020. International Chamber of Commerce, Paris, 2019.
14. EU Directive 2024/1760 (CSDDD). Corporate Sustainability Due Diligence Directive. European Parliament and Council.
15. US Public Law 117-78. Uyghur Forced Labor Prevention Act (UFLPA), 2021.
16. EU REACH Regulation 1907/2006. Registration, Evaluation, Authorisation and Restriction of Chemicals. European Parliament and Council.
17. SCOR Digital Standard (SCOR-DS). ASCM (Association for Supply Chain Management), 2019.
18. APICS Dictionary, 16th edition. ASCM, 2024.

### Software and Library Documentation

19. Chen, T. and Guestrin, C. (2016). XGBoost: A scalable tree boosting system. *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining*, pp. 785-794.
20. Jocher, G. et al. (2023). Ultralytics YOLOv8. Available at: https://github.com/ultralytics/ultralytics (Apache-2.0 / AGPL-3.0).
21. Google OR-Tools. (2024). *OR-Tools: Vehicle Routing and Combinatorial Optimization*. Apache-2.0. Available at: https://github.com/google/or-tools.
22. Smith, R. (2007). An overview of the Tesseract OCR engine. *Ninth International Conference on Document Analysis and Recognition (ICDAR 2007)*, Vol. 2, pp. 629-633.
23. Hunter, J.D. (2007). Matplotlib: A 2D graphics environment. *Computing in Science and Engineering*, 9(3), pp. 90-95.
24. Pedregosa, F. et al. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research*, 12, pp. 2825-2830.
25. Harris, C.R. et al. (2020). Array programming with NumPy. *Nature*, 585, pp. 357-362.
26. Virtanen, P. et al. (2020). SciPy 1.0: Fundamental algorithms for scientific computing in Python. *Nature Methods*, 17, pp. 261-272.

### Internal References

27. `src/shared/types.ts` — Money, UOM, GS1, Incoterms 2020 type definitions
28. `src/inventory/StockMovement.ts` — Event-sourced stock movement domain aggregate
29. `src/compliance/REACH.ts` — EU REACH 1907/2006 compliance logic
30. `src/compliance/UFLPA.ts` — UFLPA risk assessment and clearance document logic
31. `src/quality/InspectionRecord.ts` — ISO 2859-1 AQL inspection record domain object
32. `docs/standards/REGULATORY_FRAMEWORK.md` — Full regulatory reference index

---

*This document is subject to version control. All amendments must be approved by the Supply Chain Centre of Excellence and the responsible domain architect. Effective date of each revision must be recorded in the document header.*

*All code, comments, and documentation in this repository must be in English per the project Language Policy defined in CLAUDE.md.*
