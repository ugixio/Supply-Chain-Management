# Inventory Management — Enterprise Implementation Guide

**Department:** 05 — Inventory Management
**Standard Alignment:** SCOR-DS · ISO 28000:2022 · GS1 Gen. Specs. v23 · ISO 9001:2015 §8.5.2
**Document Status:** Authorised for Implementation
**Last Reviewed:** 2026-06-20
**Audience:** Senior Supply Chain Architects, ERP Programme Managers, Data Science Leads

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Prerequisites & Dependencies](#2-prerequisites--dependencies)
3. [Phase 0: Assessment & AS-IS Analysis](#3-phase-0-assessment--as-is-analysis)
4. [Phase 1: Foundation & Master Data](#4-phase-1-foundation--master-data)
5. [Phase 2: Process Standardisation & Core Analytics](#5-phase-2-process-standardisation--core-analytics)
6. [Phase 3: Mathematical Models](#6-phase-3-mathematical-models)
7. [Phase 4: ML/AI Pipeline](#7-phase-4-mlai-pipeline)
8. [Phase 5: Integration & Automation](#8-phase-5-integration--automation)
9. [Phase 6: Continuous Improvement](#9-phase-6-continuous-improvement)
10. [Technology Stack & Architecture](#10-technology-stack--architecture)
11. [Change Management & Training](#11-change-management--training)
12. [Implementation KPIs](#12-implementation-kpis)
13. [Risk & Mitigation](#13-risk--mitigation)
14. [Timeline Summary](#14-timeline-summary)
15. [References](#15-references)

---

## 1. Executive Summary

This implementation guide governs the end-to-end deployment of the Inventory Management module within the enterprise Supply Chain Management platform. The module covers item master governance, stock movement event sourcing, multi-echelon replenishment policy optimisation, warehouse execution (FEFO lot control), ERP GL integration, and a production-grade ML/AI pipeline for anomaly detection, stockout prediction, and reinforcement-learning-driven replenishment.

### Strategic Objectives

The primary objective is to establish a single version of inventory truth across all legal entities, distribution centres, and third-party logistics providers. The system must eliminate manual reconciliation, enforce regulatory lot-tracking obligations (EU REACH 1907/2006; FSMA 204; GS1 SSCC traceability), and provide real-time financial visibility through automatic GL journal generation.

Secondary objectives include: reducing total inventory carrying cost by 18-25% through statistically grounded safety-stock rightsizing; improving service levels to Fill Rate >= 98.5% and OTIF >= 97%; achieving cycle-count accuracy of >= 99.5% within 12 months of go-live; and deploying predictive ML models that reduce stockout events by at least 40% relative to the baseline rule-based replenishment engine.

### Scope

The scope encompasses all raw materials, work-in-progress, finished goods, maintenance/repair/operations (MRO) items, and packaging materials managed within the corporate ERP landscape. The domain boundary excludes consignment stock owned by suppliers (tracked as memo items only) and customer-owned goods held on a bailment basis.

### Investment Thesis

Inventory typically represents 20-35% of total assets in manufacturing and distribution organisations (Chopra & Meindl, 2016). A structured, analytically rigorous inventory management programme consistently delivers 15-30% reduction in working capital tied up in stock, 10-20% reduction in obsolescence write-offs, and 5-12% reduction in expediting and premium freight costs. The ROI horizon is 14-18 months post go-live for a mid-size deployment and 10-14 months for large-scale rollouts with high SKU velocity.

---

## 2. Prerequisites & Dependencies

### 2.1 Upstream Module Dependencies

| Dependency | Module | Consumed Artefact | Criticality |
|---|---|---|---|
| Item master (SKU) | 01-Procurement | `InventoryItem` aggregate | Blocking |
| Supplier lead time | 02-Supplier Management | `SupplierScorecard.leadTimeDays` | Blocking |
| Demand forecasts | 04-Demand Planning | `ForecastResult` (SMA/SES/Holt/Holt-Winters) | Blocking |
| Purchase Orders | 01-Procurement | `PurchaseOrder` (APPROVED status) | Blocking |
| Quality inspection results | 07-Quality | `InspectionRecord` (AQL ISO 2859-1) | Required |
| Shipment receipts | 06-Logistics | `Shipment` (DELIVERED status) | Required |
| GL chart of accounts | Finance (ERP) | Account codes for COGS, inventory asset | Required |
| Compliance flags | 10-Compliance | `reachSVHC`, `uflpaRisk` | Required |

### 2.2 Infrastructure Prerequisites

- **Event Store**: append-only log (PostgreSQL with advisory locks or Apache Kafka) supporting idempotent writes via `idempotencyKey` (UUID v4).
- **Read-model projections**: materialised views rebuilt from event stream; must support eventual consistency with < 500 ms lag under normal load.
- **Node.js runtime**: >= 20 LTS; TypeScript >= 5.3.
- **Python runtime**: >= 3.11; virtualenv or conda environment pinned via `requirements.txt`.
- **ERP connectivity**: SAP RFC/BAPI gateway or Oracle Integration Cloud adapter (REST/SOAP); credentials stored in Vault (HashiCorp), never in source.
- **RFID/barcode middleware**: GS1-128 scanner drivers; RFID middleware (Impinj Octane SDK or equivalent open-source wrapper) capable of publishing SSCC reads to internal message bus.
- **Object storage**: S3-compatible bucket (MinIO for on-premises) for ML artefact versioning and training datasets.
- **Container orchestration**: Kubernetes >= 1.28 for ML training jobs; Helm charts version-controlled alongside application code.

### 2.3 Data Quality Prerequisites

Before Phase 1 begins, a data quality gate must be passed:

- >= 95% of active SKUs have a valid GTIN (GS1 Gen. Specs. v23 check digit validated).
- >= 90% of SKUs have a confirmed primary supplier with `quotedLeadTimeDays > 0`.
- All financial accounts referenced by `getJournalAccounts()` exist in the ERP chart of accounts.
- Historical demand data spans >= 24 months for all A-class SKUs (required for seasonal Holt-Winters fitting and XGBoost lag features).

---

## 3. Phase 0: Assessment & AS-IS Analysis

### 3.1 Objectives

Phase 0 produces a quantified baseline of the current inventory operation. Without an accurate baseline, improvement claims cannot be validated and business case commitments cannot be honoured. This phase takes 4-6 weeks and is conducted by a joint team of supply chain consultants, IT architects, and finance controllers.

### 3.2 Inventory Health Diagnostic

Execute the following diagnostic queries against the current system (or manual export) to establish baseline KPIs:

**Inventory Accuracy Rate (IAR)**
```
IAR = (Count of locations where system qty = physical qty) / (Total locations counted) x 100
```
Target baseline expectation: 85-92% for organisations without automated counting. World-class: >= 99.5%.

**Inventory Turnover Ratio**
```
Turnover = COGS (12 months rolling) / Average Inventory Value (12 months)
```
Benchmark by industry: Retail 8-12x; Automotive OEM 15-25x; Industrial distribution 4-6x.

**Days Inventory Outstanding (DIO)**
```
DIO = 365 / Turnover Ratio
```

**Obsolescence Rate**
```
Obsolescence Rate = (Value of stock > 12 months with no movement) / Total Inventory Value x 100
```
Trigger corrective action if > 5%.

### 3.3 Process Mapping

Conduct value-stream mapping (VSM) workshops across receiving, putaway, replenishment, picking, packing, and shipping. Document:

- Cycle times at each step (median and 90th percentile).
- Touchpoints where paper-based or spreadsheet reconciliation occurs — these are primary automation targets.
- Exception handling procedures for shorts, overages, and damaged goods receipts.
- Current lot-tracking procedures for temperature-controlled and REACH SVHC items.

### 3.4 Data Gap Analysis

| Data Element | Required By | Gap Severity | Remediation |
|---|---|---|---|
| Historical demand by SKU/DC | XGBoost, Holt-Winters | Critical | Extract from ERP sales orders; minimum 24 months |
| Lead time distribution per supplier | Safety Stock Methods 3-4 | Critical | Pull from PO history; flag if N < 30 |
| Unit cost (FIFO/WAC) | ABC value ranking, EOQ H | High | Align with finance valuation policy |
| Lot expiry dates | FEFO picking | High | Mandatory for lot-tracked items |
| Physical dimension (L/W/H, weight) | Warehouse slotting, CPOI | Medium | Source from supplier or measure during receiving |
| Hazmat class (IMDG/ADR) | FEFO override, storage zoning | High | Review safety data sheets |

### 3.5 AS-IS Scorecard

Produce a one-page scorecard with red/amber/green (RAG) ratings across five dimensions: Data Quality, Process Maturity, Technology Capability, Organisational Capability, and Compliance Readiness. This scorecard forms the baseline against which Phase 6 continuous improvement tracks progress.

---

## 4. Phase 1: Foundation & Master Data

### 4.1 Item Master Governance

The `InventoryItem` aggregate is the authoritative source of record for all stock-keeping unit attributes. It is immutable after creation — changes are applied via domain events, never direct mutation.

**Core attributes required at item creation:**

```typescript
// src/departments/05-inventory-management/domain/InventoryItem.ts (excerpt)
interface InventoryItem {
  sku: string;                       // GS1 GTIN-14 or internal code; immutable
  gtin: string;                      // 14-digit GTIN with validated check digit
  description: string;
  uom: UOM;                          // GS1 UOM code (EA, KG, LT, M, etc.)
  unitCostCents: number;             // Integer cents — FIFO or WAC per finance policy
  storageCondition: StorageCondition; // AMBIENT | CHILLED | FROZEN | CONTROLLED_ATMOSPHERE
  lotTracked: boolean;               // true when storageCondition !== AMBIENT or reachSVHC
  shelfLifeDays: number | null;      // null for non-perishable
  reachSVHC: boolean;                // EU REACH Art.57 Substance of Very High Concern
  hazmatClass: string | null;        // IMDG/ADR class (e.g. "3", "8", "6.1")
  abcClass: 'A' | 'B' | 'C' | null; // Set by classification engine
  xyzClass: 'X' | 'Y' | 'Z' | null; // Set by classification engine
  status: 'ACTIVE' | 'DISCONTINUED' | 'BLOCKED';
  isDeleted: boolean;                // Soft-delete only — never hard delete
}
```

**Business rule enforcement:**
- `lotTracked` must be `true` if `storageCondition !== 'AMBIENT'` or `reachSVHC === true`.
- `sku` is immutable once created. Status transitions use the `status` field.
- `unitCostCents` must be a positive integer. Fractional cents must be rounded using banker's rounding before storage.

### 4.2 Event-Sourced Stock Movement

All inventory transactions are recorded as immutable events in the event store. The current on-hand balance is a projection derived by replaying events — it is never stored as mutable state.

```typescript
type MovementType =
  | 'GOODS_RECEIPT'         // Inbound from supplier (PO-referenced)
  | 'GOODS_ISSUE'           // Outbound to production or customer
  | 'TRANSFER_IN'           // Inter-location transfer (receiving side)
  | 'TRANSFER_OUT'          // Inter-location transfer (issuing side)
  | 'ADJUSTMENT_POSITIVE'   // Cycle count surplus
  | 'ADJUSTMENT_NEGATIVE'   // Cycle count shortage
  | 'RETURN_FROM_CUSTOMER'  // Reverse logistics
  | 'RETURN_TO_SUPPLIER'    // Quality rejection return
  | 'SCRAP'                 // Write-off (damage, expiry)
  | 'QUARANTINE_IN'         // Move to quality hold
  | 'QUARANTINE_OUT';       // Release from quality hold

interface StockMovement {
  movementId: string;         // UUID v4
  idempotencyKey: string;     // UUID v4; unique constraint prevents double-posting
  sku: string;
  locationId: string;         // Warehouse location (aisle-bay-level-position)
  lotNumber: string | null;   // Required when InventoryItem.lotTracked = true
  expiryDate: string | null;  // ISO 8601 date; required when shelfLifeDays set
  movementType: MovementType;
  quantityUnits: number;      // Always positive; direction encoded in type
  unitCostCents: number;
  totalValueCents: number;    // quantityUnits * unitCostCents
  referenceDocType: 'PO' | 'SO' | 'TRANSFER' | 'MANUAL' | 'INSPECTION';
  referenceDocId: string;
  glDebitAccount: string;     // Populated by getJournalAccounts()
  glCreditAccount: string;
  postedAt: ISOTimestamp;     // UTC
  isDeleted: boolean;
}
```

**GL journal generation** is mandatory for every movement. The mapping function:

```typescript
function getJournalAccounts(type: MovementType): { debit: string; credit: string } {
  const map: Record<MovementType, { debit: string; credit: string }> = {
    GOODS_RECEIPT:        { debit: '1310',  credit: '2100' }, // Inventory / GR-IR
    GOODS_ISSUE:          { debit: '5000',  credit: '1310' }, // COGS / Inventory
    TRANSFER_IN:          { debit: '1310',  credit: '1310' }, // Inventory-to / Inventory-from
    TRANSFER_OUT:         { debit: '1310',  credit: '1310' },
    ADJUSTMENT_POSITIVE:  { debit: '1310',  credit: '7800' }, // Inventory / Inv Adj. P&L
    ADJUSTMENT_NEGATIVE:  { debit: '7800',  credit: '1310' },
    RETURN_FROM_CUSTOMER: { debit: '1310',  credit: '5000' },
    RETURN_TO_SUPPLIER:   { debit: '2100',  credit: '1310' },
    SCRAP:                { debit: '7900',  credit: '1310' }, // Scrap loss / Inventory
    QUARANTINE_IN:        { debit: '1315',  credit: '1310' }, // Quarantine stock / Inventory
    QUARANTINE_OUT:       { debit: '1310',  credit: '1315' },
  };
  return map[type];
}
```

### 4.3 Preventing Negative Inventory

The stock balance projection must enforce the no-negative-inventory business rule before any GOODS_ISSUE, TRANSFER_OUT, or SCRAP movement is accepted:

```typescript
function projectStockBalance(events: StockMovement[], sku: string, locationId: string): number {
  const INBOUND: MovementType[] = ['GOODS_RECEIPT', 'TRANSFER_IN', 'ADJUSTMENT_POSITIVE',
    'RETURN_FROM_CUSTOMER', 'QUARANTINE_OUT'];
  return events
    .filter(e => e.sku === sku && e.locationId === locationId && !e.isDeleted)
    .reduce((balance, e) => {
      return INBOUND.includes(e.movementType)
        ? balance + e.quantityUnits
        : balance - e.quantityUnits;
    }, 0);
}

function validateIssue(sku: string, locationId: string, qty: number,
    backorderAllowed: boolean, currentBalance: number): void {
  if (!backorderAllowed && currentBalance - qty < 0) {
    throw new DomainError(
      `NEGATIVE_INVENTORY_BLOCKED: SKU ${sku} at ${locationId} — ` +
      `balance ${currentBalance}, requested ${qty}. Set backorderAllowed=true to proceed.`
    );
  }
}
```

### 4.4 Location Master

Warehouse locations follow the GS1 GLN standard extended with sub-location codes:

```
{GLN-13}.{AISLE:2}.{BAY:3}.{LEVEL:2}.{POSITION:2}
```

Each location record carries: `storageCondition`, `maxWeightKg`, `maxVolumeM3`, `pickZone`, `putawayZone`, `abcZone` (A/B/C velocity zone for slotting), and `isActive`.

---

## 5. Phase 2: Process Standardisation & Core Analytics

### 5.1 Receiving Process

**Step 1 — Advance Shipment Notice (ASN) matching**: Incoming `Shipment` records (status `DELIVERED`) are matched to open PO lines. Quantity tolerances: over-delivery <= 5%, under-delivery <= 10% without buyer approval.

**Step 2 — Quality gate**: Every receipt triggers an `InspectionRecord` per AQL ISO 2859-1. Items failing inspection are moved to quarantine via `QUARANTINE_IN` event. GOODS_RECEIPT is only posted for accepted quantities.

**Step 3 — Lot assignment**: For lot-tracked items, the system auto-generates a lot number using the format `{YYYYMMDD}-{SUPPLIER_CODE}-{SEQUENCE_5}` and assigns `expiryDate = receivedDate + shelfLifeDays`.

**Step 4 — GS1 SSCC label printing**: A Serial Shipping Container Code (SSCC-18) is generated per pallet and printed in GS1-128 format. The SSCC is linked to the movement event and the originating ASN.

**Step 5 — Putaway**: The WMS slotting engine assigns a putaway location based on ABC velocity zone, storage condition, and current utilisation (CPOI algorithm — see Phase 3).

### 5.2 Cycle Counting Programme

Replace annual wall-to-wall physical inventories with a continuous cycle counting programme:

| ABC Class | Count Frequency | Annual Counts per SKU |
|---|---|---|
| A | Weekly | 52 |
| B | Monthly | 12 |
| C | Quarterly | 4 |

Discrepancies above threshold (A: > 0.1%; B/C: > 1%) trigger blind recount before posting `ADJUSTMENT_POSITIVE` or `ADJUSTMENT_NEGATIVE` events. All adjustments require authorisation:

- Adjustments <= $500: Warehouse supervisor
- Adjustments $500 - $5,000: Inventory controller
- Adjustments > $5,000: Finance controller + VP Supply Chain

### 5.3 Core Analytics Dashboard

The following metrics are computed daily from the event stream projection:

- **Inventory Turnover Ratio** = COGS (rolling 365 days) / Average Inventory Value
- **Days Inventory Outstanding (DIO)** = 365 / Turnover Ratio
- **Fill Rate (line-item)** = Lines shipped complete on first attempt / Total order lines x 100
- **Inventory Accuracy Rate** = Locations matching system balance / Locations counted x 100
- **Obsolescence Exposure** = Value of stock with zero movement > 180 days

---

## 6. Phase 3: Mathematical Models

### 6.1 ABC Classification (Pareto Analysis)

**Principle**: 80% of inventory value is typically concentrated in 20% of SKUs (Pareto, 1896). ABC classification allocates management attention and policy rigour in proportion to financial significance.

**Value-Velocity Matrix**

Each SKU is scored on two dimensions:
1. **Annual Consumption Value (ACV)** = Average Unit Cost x Annual Demand Units
2. **Velocity** = Annual movement transactions (frequency of picks/issues)

```python
# python/05_inventory_management/abc_classification.py
import pandas as pd
import numpy as np

def classify_abc(df: pd.DataFrame,
                 value_col: str = 'annual_value_cents',
                 a_threshold: float = 0.80,
                 b_threshold: float = 0.95) -> pd.DataFrame:
    """
    Classify SKUs into ABC categories using cumulative value share.

    Parameters
    ----------
    df : DataFrame with columns [sku, annual_value_cents]
    a_threshold : cumulative value share for A cutoff (default 80%)
    b_threshold : cumulative value share for B cutoff (default 95%)

    Returns
    -------
    DataFrame with added columns: value_rank, cum_value_share, abc_class
    """
    df = df.copy()
    df = df.sort_values(value_col, ascending=False).reset_index(drop=True)
    total_value = df[value_col].sum()
    df['cum_value_share'] = df[value_col].cumsum() / total_value
    df['value_rank'] = df.index + 1

    def assign_class(cum_share: float) -> str:
        if cum_share <= a_threshold:
            return 'A'
        elif cum_share <= b_threshold:
            return 'B'
        return 'C'

    df['abc_class'] = df['cum_value_share'].apply(assign_class)
    return df
```

**Policy Assignment Table by ABC Class**

| Dimension | A | B | C |
|---|---|---|---|
| Replenishment review | Continuous (r,Q) | Periodic (s,S) — 2-week cycle | Periodic (s,S) — 4-week cycle |
| Safety stock method | Method 4 (joint variability) | Method 3 (demand sigma) | Method 1 (fixed days cover) |
| Service level target (CSL) | 99.0% | 97.0% | 95.0% |
| Cycle count frequency | Weekly | Monthly | Quarterly |
| Supplier dual-sourcing | Mandatory if HHI > 0.25 | Recommended | Optional |
| Obsolescence review | Quarterly | Semi-annual | Annual |
| Lot tracking | Required if controlled | Recommended | Optional |

### 6.2 XYZ Classification (Demand Variability)

**Coefficient of Variation (CV)**

XYZ classification measures demand predictability over the trailing 12 months:

```
CV = sigma_D / mu_D
```

Where `sigma_D` is the standard deviation of periodic demand (weekly or monthly buckets) and `mu_D` is the arithmetic mean.

**Z-score thresholds** (industry standard, consistent with Chopra & Meindl Ch.11):

| Class | CV Range | Interpretation |
|---|---|---|
| X | CV < 0.10 | Highly stable, predictable demand |
| Y | 0.10 <= CV < 0.25 | Moderate variability; seasonal or trend-affected |
| Z | CV >= 0.25 | Erratic, lumpy, or intermittent demand |

```python
def classify_xyz(demand_series: pd.Series) -> str:
    """
    Classify a single SKU demand series into X, Y, or Z.

    Parameters
    ----------
    demand_series : weekly or monthly demand quantities (minimum 12 periods)

    Returns
    -------
    'X', 'Y', or 'Z'
    """
    if len(demand_series) < 12:
        raise ValueError("Minimum 12 periods required for XYZ classification")
    mu = demand_series.mean()
    if mu == 0:
        return 'Z'  # No demand — treat as highly erratic
    cv = demand_series.std(ddof=1) / mu
    if cv < 0.10:
        return 'X'
    elif cv < 0.25:
        return 'Y'
    return 'Z'
```

**Combined ABC-XYZ 9-Cell Policy Matrix**

| | X (Stable) | Y (Variable) | Z (Erratic) |
|---|---|---|---|
| **A (High Value)** | AX: Continuous review, tight safety stock, Method 4 | AY: Continuous review, Holt forecasting, Method 4 | AZ: Continuous review, Newsvendor model, dual source |
| **B (Medium Value)** | BX: Periodic review (2wk), Method 3, EOQ | BY: Periodic review (2wk), SES forecast, Method 3 | BZ: Min-max with wide bands, manual oversight |
| **C (Low Value)** | CX: Periodic review (4wk), Method 1, bulk purchase | CY: Periodic review (4wk), min-max replenishment | CZ: On-demand / kanban; consider rationalisation |

**Policy notes:**
- AZ items require human escalation when the ML anomaly model flags unusual consumption — the combination of high value and unpredictable demand represents maximum financial risk.
- CZ items should trigger SKU rationalisation review annually. If < 3 picks/year and no strategic reason, recommend discontinuation.

### 6.3 Safety Stock Methods 1-4

All methods use the standard normal z-score lookup for cycle service level (CSL):

| CSL | z |
|---|---|
| 90.0% | 1.282 |
| 95.0% | 1.645 |
| 97.0% | 1.881 |
| 98.0% | 2.054 |
| 99.0% | 2.326 |
| 99.5% | 2.576 |
| 99.9% | 3.090 |

**Implementation order**: Start with Method 1 for all items at go-live (data minimisation). Migrate to Method 3 once 12 months of demand history accumulates. Migrate A-class items to Method 4 once lead time distribution data has >= 30 PO observations per supplier.

---

**Method 1 — Fixed Days Cover (Baseline)**

```
SS_1 = D_daily * days_cover
```

Where `D_daily` is average daily demand and `days_cover` is set by ABC class policy (A: 7 days; B: 14 days; C: 21 days). Simple but ignores variability — use only as a temporary bootstrap.

---

**Method 2 — Demand Variability, Fixed Lead Time**

```
SS_2 = z * sigma_D * sqrt(LT)
```

Where `sigma_D` is the standard deviation of demand per unit time period and `LT` is lead time expressed in the same unit. Assumes lead time is deterministic.

---

**Method 3 — Recommended Standard (Holt/Chopra & Meindl Ch.11)**

```
SS_3 = z * sigma_D * sqrt(LT)
```

Functionally the same formula as Method 2 but applied with statistically fitted `sigma_D` from the demand forecasting module. The key distinction is using the residual standard error from the forecasting model (SES or Holt) rather than the raw historical standard deviation, which reduces bias from trend or seasonal effects.

---

**Method 4 — Most Accurate: Joint Demand and Lead Time Variability**

```
SS_4 = z * sqrt(LT * sigma_D^2 + D_bar^2 * sigma_LT^2)
```

Where:
- `LT` = mean lead time (days or weeks)
- `sigma_D` = standard deviation of demand per unit time
- `D_bar` = mean demand per unit time
- `sigma_LT` = standard deviation of lead time

This is the Chopra & Meindl recommended formula when both demand and supply variability are material. It must be used for all A-class items once sufficient lead time data is available.

```python
import numpy as np
from scipy.stats import norm

def safety_stock_method4(mean_demand: float,
                          std_demand: float,
                          mean_lead_time: float,
                          std_lead_time: float,
                          service_level: float) -> float:
    """
    Safety stock using joint demand and lead time variability (Method 4).

    Parameters
    ----------
    mean_demand    : average demand per unit time (same unit as lead time)
    std_demand     : standard deviation of demand per unit time
    mean_lead_time : mean supplier lead time (same unit as demand period)
    std_lead_time  : standard deviation of lead time
    service_level  : cycle service level (e.g. 0.99 for 99%)

    Returns
    -------
    Safety stock quantity (same unit as demand)
    """
    z = norm.ppf(service_level)
    variance = (mean_lead_time * std_demand**2) + (mean_demand**2 * std_lead_time**2)
    return z * np.sqrt(variance)
```

### 6.4 Economic Order Quantity (EOQ) with Extensions

**Basic EOQ** (Harris, 1913; Wilson, 1934):

```
EOQ = sqrt(2 * D * S / H)
```

Where:
- `D` = annual demand (units)
- `S` = order setup/ordering cost per order ($ per order)
- `H` = annual holding cost per unit ($ per unit per year) = unit cost * carrying cost rate

Carrying cost rate benchmark: 18-25% of unit cost per annum (includes capital, storage, insurance, obsolescence).

**Quantity Discount Extension**

When suppliers offer tiered pricing, evaluate total annual cost (TAC) at each price break:

```
TAC(Q) = D * P + (D / Q) * S + (Q / 2) * H(P)
```

Where `P` is the unit price at a given tier and `H(P) = P * carrying_rate`. The optimal `Q*` is the quantity minimising `TAC` across all feasible tiers.

**Imputed Cost (Total Cost of Ownership)**

For strategic items, `S` should include imputed costs: buyer time, supplier qualification, quality inspection, system processing. A typical imputed ordering cost for complex direct materials is $150-$400 per PO line.

**Sensitivity Bands (+/- 20%)**

EOQ is robust to input errors — total cost is relatively flat near the optimum. Compute the total annual cost at Q = 0.8 * EOQ and Q = 1.2 * EOQ to confirm the cost penalty of rounding to standard pack sizes is acceptable (typically < 2% cost increase within +/-20% band).

```python
def eoq_with_extensions(demand_annual: float,
                         ordering_cost: float,
                         unit_cost_cents: int,
                         carrying_rate: float = 0.20) -> dict:
    """
    Compute EOQ and sensitivity analysis.

    Parameters
    ----------
    demand_annual   : annual demand in units
    ordering_cost   : cost per order in dollars
    unit_cost_cents : unit cost in integer cents
    carrying_rate   : annual carrying cost as fraction of unit cost

    Returns
    -------
    Dictionary with eoq, total_annual_cost, sensitivity at +/-20%
    """
    unit_cost = unit_cost_cents / 100.0
    H = unit_cost * carrying_rate
    eoq = np.sqrt(2 * demand_annual * ordering_cost / H)
    def tac(q: float) -> float:
        return (demand_annual * unit_cost) + (demand_annual / q) * ordering_cost + (q / 2) * H

    return {
        'eoq': round(eoq, 2),
        'tac_at_eoq': round(tac(eoq), 2),
        'tac_at_80pct': round(tac(eoq * 0.8), 2),
        'tac_at_120pct': round(tac(eoq * 1.2), 2),
        'cost_penalty_80pct_pct': round((tac(eoq * 0.8) / tac(eoq) - 1) * 100, 3),
        'cost_penalty_120pct_pct': round((tac(eoq * 1.2) / tac(eoq) - 1) * 100, 3),
    }
```

### 6.5 (r, Q) Continuous Review Policy

The (r, Q) policy places a fixed order of size Q whenever on-hand inventory plus on-order drops to or below the reorder point r.

**Reorder Point (ROP)**

```
r = D_bar * LT + SS
```

Where `D_bar * LT` is the expected demand during lead time (cycle stock depletion) and `SS` is the safety stock buffer.

**Service Level Setting by ABC Class**

| ABC Class | Target CSL | z-score | Rationale |
|---|---|---|---|
| A | 99.0% | 2.326 | High value; stockout cost exceeds holding cost |
| B | 97.0% | 1.881 | Balanced; moderate stockout consequence |
| C | 95.0% | 1.645 | Low value; holding cost dominates |

Q is set to EOQ (optionally rounded up to supplier minimum order quantity or pack size).

**Continuous review** requires real-time inventory visibility — mandatory RFID or scanner confirmation at point of issue. Without accurate real-time balances, the (r, Q) system degrades to periodic effective behaviour.

### 6.6 (s, S) Periodic Review Policy

The (s, S) policy is applied at each review period R: if on-hand inventory falls below the trigger level `s` (order-up-to point minus buffer), order sufficient stock to raise the position to the order-up-to level `S`.

**Effective Lead Time**

```
Effective LT = L + R
```

Where `L` is the supplier lead time and `R` is the review period. Safety stock must cover variability over the entire effective lead time.

```
SS_(s,S) = z * sigma_D * sqrt(L + R)
S = D_bar * (L + R) + SS_(s,S)
s = D_bar * L + SS_minimum  (trigger if position drops to expected demand during lead time)
```

**Review Period Selection by ABC Class**

| ABC Class | Review Period R | Rationale |
|---|---|---|
| A | Continuous (r,Q) preferred | Highest attention warranted |
| B | 2 weeks | Weekly MRP run covers replenishment cycle |
| C | 4 weeks | Batch replenishment reduces transaction cost |

Organisations with SAP MRP may align review periods to MRP planning horizons (daily for A; weekly for B; bi-weekly for C).

### 6.7 Newsvendor Model

The Newsvendor model applies to perishable goods, make-to-stock items with short lifecycle, and single-period procurement decisions (seasonal buys, promotional stock, fashion items).

**Critical Ratio and Optimal Quantity Q***

```
Critical Ratio (CR) = (p - c) / (p - v)
```

Where:
- `p` = selling price per unit
- `c` = unit cost per unit
- `v` = salvage/residual value per unit (could be negative for disposal costs)

The critical ratio equals the optimal service level. The optimal order quantity Q* satisfies:

```
F(Q*) = CR
```

Where `F` is the CDF of demand. For normally distributed demand:

```
Q* = mu_D + z_CR * sigma_D
```

Where `z_CR = norm.ppf(CR)`.

For Poisson-distributed demand (low-volume, discrete items):

```
Q* = smallest Q such that Poisson_CDF(Q; lambda) >= CR
```

```python
from scipy.stats import norm, poisson

def newsvendor_normal(mu: float, sigma: float,
                       price: float, cost: float, salvage: float) -> dict:
    """
    Newsvendor solution under normal demand.
    """
    cr = (price - cost) / (price - salvage)
    z = norm.ppf(cr)
    q_star = mu + z * sigma
    expected_sales = mu - sigma * norm.pdf(z) + (mu - q_star) * norm.cdf(-z)
    expected_profit = (price - salvage) * expected_sales - (cost - salvage) * q_star
    return {'critical_ratio': cr, 'z': z, 'q_star': q_star,
            'expected_profit': expected_profit}

def newsvendor_poisson(lam: float, price: float, cost: float, salvage: float) -> dict:
    """
    Newsvendor solution under Poisson demand.
    """
    cr = (price - cost) / (price - salvage)
    q_star = poisson.ppf(cr, mu=lam)
    return {'critical_ratio': cr, 'q_star': int(q_star)}
```

### 6.8 Newsvendor with Price Optimisation (Petruzzi-Dada)

Petruzzi and Dada (1999) extend the Newsvendor model to jointly optimise price `p` and quantity `Q` when demand is price-sensitive.

**Demand model:**

```
D(p) = a - b * p + epsilon
```

Where `a` and `b` are market parameters estimated from historical price-demand data and `epsilon` is a zero-mean error term.

**Grid search procedure:**

1. Fit demand model: regress historical demand on price to estimate `a` and `b`.
2. Define price grid: `p in [c * (1 + min_margin), p_max]` with step size 0.01 * c.
3. For each `p` in the grid:
   a. Compute `mu_D(p) = a - b * p`
   b. Apply standard Newsvendor formula to get `Q*(p)`
   c. Compute expected profit `Pi(p, Q*(p))`
4. Select `p*` and `Q*` that maximise `Pi`.

This is particularly relevant for perishable food, fashion, and short-lifecycle electronics where markdown pricing is common.

### 6.9 FEFO Picking Logic

First-Expired First-Out (FEFO) is mandatory for all lot-tracked items. FEFO supersedes FIFO in every picking scenario. The algorithm:

**Lot Selection Algorithm:**

```python
from datetime import date, timedelta
from typing import List, Dict, Optional

def fefo_lot_selection(available_lots: List[Dict],
                        qty_required: float,
                        today: date,
                        alert_days: int = 30) -> List[Dict]:
    """
    Select lots for picking using FEFO logic with expiry alerting.

    Parameters
    ----------
    available_lots : list of dicts with keys: lot_number, expiry_date, qty_available
    qty_required   : quantity to pick
    today          : current date
    alert_days     : flag lots expiring within this many days

    Returns
    -------
    List of picking instructions: [{'lot_number': ..., 'qty_pick': ..., 'expiry_warning': bool}]
    """
    # Filter out expired lots — never pick
    eligible = [
        lot for lot in available_lots
        if lot['expiry_date'] is not None and lot['expiry_date'] > today
    ]
    # Sort by ascending expiry date (earliest first)
    eligible.sort(key=lambda x: x['expiry_date'])

    picks = []
    remaining = qty_required

    for lot in eligible:
        if remaining <= 0:
            break
        pick_qty = min(lot['qty_available'], remaining)
        days_to_expiry = (lot['expiry_date'] - today).days
        picks.append({
            'lot_number': lot['lot_number'],
            'qty_pick': pick_qty,
            'expiry_date': lot['expiry_date'].isoformat(),
            'expiry_warning': days_to_expiry <= alert_days,
            'days_to_expiry': days_to_expiry,
        })
        remaining -= pick_qty

    if remaining > 0:
        raise ValueError(
            f"Insufficient stock: {qty_required - remaining} available, {qty_required} required"
        )
    return picks
```

**Expiry Alert Thresholds by Storage Condition:**

| Storage Condition | Warning Alert | Critical Alert | Auto-markdown Trigger |
|---|---|---|---|
| AMBIENT (non-perishable) | N/A | N/A | N/A |
| AMBIENT (food/pharma) | 60 days | 30 days | 45 days |
| CHILLED | 14 days | 7 days | 10 days |
| FROZEN | 30 days | 14 days | 21 days |
| CONTROLLED_ATMOSPHERE | 7 days | 3 days | 5 days |

Warning alerts notify inventory planners. Critical alerts trigger automatic transfer to markdown/clearance bin and raise a `QUARANTINE_IN` event pending QC review. Auto-markdown triggers integrate with the pricing engine.

### 6.10 Inventory Turnover, DIO, and Fill Rate

These KPIs are computed from the event store projection using the data pipeline below.

**Inventory Turnover Ratio**
```
Turnover = Sum(COGS movements, 365 days) / Average(daily_inventory_value, 365 days)
```

**Days Inventory Outstanding (DIO)**
```
DIO = 365 / Turnover
```

**Fill Rate (Line-Item Level)**
```
Fill_Rate = Count(order lines shipped complete on first attempt) / Count(total order lines) * 100
```

**Data Pipeline (Python):**

```python
def compute_inventory_kpis(movements_df: pd.DataFrame,
                             orders_df: pd.DataFrame,
                             period_days: int = 365) -> dict:
    """
    Compute Turnover, DIO, and Fill Rate from movement history.

    movements_df columns: movement_type, total_value_cents, posted_at, sku
    orders_df columns: order_line_id, qty_ordered, qty_shipped, shipped_at
    """
    cutoff = pd.Timestamp.utcnow() - pd.Timedelta(days=period_days)
    recent = movements_df[movements_df['posted_at'] >= cutoff]

    cogs_types = ['GOODS_ISSUE', 'SCRAP', 'RETURN_TO_SUPPLIER']
    cogs = recent[recent['movement_type'].isin(cogs_types)]['total_value_cents'].sum()

    # Daily inventory value (simplified: snapshot at end of each day)
    daily_vals = recent.groupby(recent['posted_at'].dt.date)['total_value_cents'].sum()
    avg_inventory = daily_vals.mean() if len(daily_vals) > 0 else 1

    turnover = (cogs / avg_inventory) if avg_inventory > 0 else 0
    dio = 365 / turnover if turnover > 0 else float('inf')

    recent_orders = orders_df[orders_df['shipped_at'] >= cutoff]
    complete_lines = (recent_orders['qty_shipped'] >= recent_orders['qty_ordered']).sum()
    fill_rate = (complete_lines / len(recent_orders) * 100) if len(recent_orders) > 0 else 0

    return {
        'turnover_ratio': round(turnover, 2),
        'dio_days': round(dio, 1),
        'fill_rate_pct': round(fill_rate, 2),
        'cogs_cents': int(cogs),
        'avg_inventory_value_cents': int(avg_inventory),
    }
```

### 6.11 Wagner-Whitin and Silver-Meal Lot Sizing

Wagner-Whitin (1958) provides the globally optimal lot-sizing solution for time-varying deterministic demand over a finite horizon using dynamic programming.

**When to switch from EOQ fixed lots:**
- EOQ is appropriate when demand is approximately stationary (CV < 0.15) and holding cost is low relative to ordering cost.
- Switch to Silver-Meal when demand is moderately time-varying (CV 0.15-0.35) — Silver-Meal provides near-optimal solutions (within 1-2% of Wagner-Whitin) at much lower computational cost.
- Use Wagner-Whitin when: (a) demand is highly time-varying (CV > 0.35); (b) the planning horizon is finite and known (seasonal product); (c) the cost of non-optimality is material (high-value A-class items).

**Silver-Meal Heuristic:**

Order quantity covers periods 1..k where average cost per period is minimised:

```
C(k) = [S + H * sum_{t=2}^{k}(t-1)*d_t] / k

Stop when C(k+1) > C(k)
```

```python
def silver_meal(demand: list, S: float, H: float) -> list:
    """
    Silver-Meal heuristic for lot-sizing with time-varying demand.

    Parameters
    ----------
    demand : list of demand quantities per period
    S      : ordering cost per order
    H      : holding cost per unit per period

    Returns
    -------
    List of order quantities aligned to demand periods
    """
    n = len(demand)
    orders = [0] * n
    t = 0
    while t < n:
        best_k = 1
        min_cost = S
        cumulative_holding = 0
        for k in range(2, n - t + 1):
            cumulative_holding += (k - 1) * demand[t + k - 1] * H
            total_cost = S + cumulative_holding
            avg_cost = total_cost / k
            prev_avg = (S + sum((j - 1) * demand[t + j - 1] * H for j in range(2, k))) / (k - 1) if k > 2 else S
            if avg_cost > prev_avg:
                break
            best_k = k
        order_qty = sum(demand[t:t + best_k])
        orders[t] = order_qty
        t += best_k
    return orders
```

---

## 7. Phase 4: ML/AI Pipeline

### 7.1 Architecture Overview

The ML pipeline follows a three-layer architecture:

1. **Feature Store** (offline): daily batch job reads from the event store projection, computes features, and writes Parquet files to object storage (versioned by date).
2. **Training Layer**: PyTorch and scikit-learn training jobs run in Kubernetes pods. Model artefacts (`.pt` weights, `joblib` pickles, metadata YAML) are versioned in object storage.
3. **Inference Layer**: REST microservice (FastAPI) wraps loaded model artefacts. Each inference request is logged with input hash, prediction, and model version for auditability.

All models are retrained monthly (minimum) or on data drift trigger (KS-test p-value < 0.05 on key feature distributions).

### 7.2 LSTM Autoencoder for Anomaly Detection

**Purpose**: Detect anomalous stock movement patterns that may indicate shrinkage, data entry errors, process deviations, or fraud. Trained exclusively on normal (non-anomalous) data; anomalies are identified as sequences with high reconstruction error.

**Window Construction**

Each training/inference sample is a sliding window of T consecutive days of movement features per SKU:

```python
import torch
import numpy as np
from torch import nn
from torch.utils.data import Dataset, DataLoader

WINDOW_SIZE = 14  # 14-day rolling window

def build_windows(df: pd.DataFrame, sku: str, window: int = WINDOW_SIZE) -> np.ndarray:
    """
    Build sliding windows from daily movement summary for a given SKU.

    Features per day: [qty_issued, qty_received, adj_positive, adj_negative,
                       transaction_count, avg_cost_cents]
    """
    sku_data = df[df['sku'] == sku].sort_values('date')
    features = sku_data[['qty_issued', 'qty_received', 'adj_positive',
                           'adj_negative', 'transaction_count', 'avg_cost_cents']].values
    # Normalise per-feature using training set statistics
    windows = []
    for i in range(len(features) - window + 1):
        windows.append(features[i:i + window])
    return np.array(windows, dtype=np.float32)
```

**LSTM Autoencoder Architecture**

```python
class LSTMAutoencoder(nn.Module):
    def __init__(self, input_size: int = 6, hidden_size: int = 32, num_layers: int = 2):
        super().__init__()
        self.encoder = nn.LSTM(input_size, hidden_size, num_layers,
                                batch_first=True, dropout=0.2)
        self.decoder = nn.LSTM(hidden_size, hidden_size, num_layers,
                                batch_first=True, dropout=0.2)
        self.output_layer = nn.Linear(hidden_size, input_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Encode
        _, (h_n, c_n) = self.encoder(x)
        # Repeat last hidden state across sequence length
        seq_len = x.size(1)
        decoder_input = h_n[-1].unsqueeze(1).repeat(1, seq_len, 1)
        # Decode
        decoded, _ = self.decoder(decoder_input)
        return self.output_layer(decoded)
```

**Training on Normal-Only Data**

```python
def train_autoencoder(normal_windows: np.ndarray,
                       epochs: int = 50,
                       lr: float = 1e-3) -> LSTMAutoencoder:
    """
    Train LSTM Autoencoder on normal movement windows only.
    Anomalous periods must be excluded from training data.
    """
    dataset = torch.tensor(normal_windows)
    loader = DataLoader(dataset, batch_size=64, shuffle=True)
    model = LSTMAutoencoder()
    optimiser = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MSELoss()

    model.train()
    for epoch in range(epochs):
        total_loss = 0.0
        for batch in loader:
            optimiser.zero_grad()
            reconstructed = model(batch)
            loss = criterion(reconstructed, batch)
            loss.backward()
            optimiser.step()
            total_loss += loss.item()
    return model
```

**Threshold Calibration at Target FPR**

After training, calibrate the reconstruction error threshold at the desired false positive rate (FPR) using a held-out normal validation set:

```python
def calibrate_threshold(model: LSTMAutoencoder,
                          val_windows: np.ndarray,
                          target_fpr: float = 0.05) -> float:
    """
    Set reconstruction error threshold so that false positive rate on
    normal validation data equals target_fpr.
    """
    model.eval()
    with torch.no_grad():
        val_tensor = torch.tensor(val_windows)
        recon = model(val_tensor)
        errors = ((val_tensor - recon) ** 2).mean(dim=(1, 2)).numpy()
    # Threshold at (1 - target_fpr) quantile of normal error distribution
    threshold = np.quantile(errors, 1.0 - target_fpr)
    return float(threshold)
```

Recommended target FPR: 0.05 (5%) — balance between sensitivity to real anomalies and alert fatigue. For high-value A-class items, reduce to 0.02.

### 7.3 Reinforcement Learning Inventory Policy (PPO)

**Purpose**: Learn a replenishment ordering policy that minimises total cost (holding + ordering + stockout penalty) without requiring explicit demand distribution assumptions. Benchmark against the analytical (s, S) policy.

**InventoryEnv Design (OpenAI Gym interface)**

```python
import gymnasium as gym
from gymnasium import spaces
from scipy.stats import nbinom
import numpy as np

class InventoryEnv(gym.Env):
    """
    Single-SKU inventory environment with negative-binomial demand.

    State space: [inventory_on_hand, open_orders_arriving_t1, open_orders_arriving_t2,
                  days_since_last_order, demand_last_7_days (rolling)]
    Action space: order quantity in [0, max_order_qty]
    """

    def __init__(self, config: dict):
        super().__init__()
        self.mean_demand = config['mean_demand']         # mu
        self.demand_dispersion = config['dispersion']    # r parameter for neg-binomial
        self.lead_time = config['lead_time_days']
        self.holding_cost = config['holding_cost_per_unit_per_day']
        self.stockout_penalty = config['stockout_penalty_per_unit']
        self.ordering_cost = config['ordering_cost_per_order']
        self.max_order = config.get('max_order_qty', 500)
        self.episode_length = config.get('episode_length', 365)

        # Negative-binomial parameterisation: mean=mu, var=mu + mu^2/r
        p = self.demand_dispersion / (self.demand_dispersion + self.mean_demand)
        self.demand_dist = nbinom(n=self.demand_dispersion, p=p)

        self.observation_space = spaces.Box(
            low=0, high=10000, shape=(self.lead_time + 4,), dtype=np.float32
        )
        self.action_space = spaces.Discrete(self.max_order + 1)

    def reset(self, seed=None):
        super().reset(seed=seed)
        self.inventory = self.mean_demand * self.lead_time * 2  # Start with ample stock
        self.pipeline = [0] * self.lead_time  # Open orders by arrival day
        self.day = 0
        return self._get_obs(), {}

    def step(self, action: int):
        order_qty = int(action)
        cost = 0.0

        # Ordering cost
        if order_qty > 0:
            cost += self.ordering_cost

        # Place order into pipeline
        self.pipeline.append(order_qty)

        # Receive arriving order
        arriving = self.pipeline.pop(0)
        self.inventory += arriving

        # Realise demand (negative binomial)
        demand = int(self.demand_dist.rvs())
        fulfilled = min(demand, max(0, int(self.inventory)))
        unmet = demand - fulfilled
        self.inventory = max(0, self.inventory - demand)

        # Costs
        cost += self.inventory * self.holding_cost
        cost += unmet * self.stockout_penalty

        self.day += 1
        done = self.day >= self.episode_length

        return self._get_obs(), -cost, done, False, {'unmet_demand': unmet}

    def _get_obs(self) -> np.ndarray:
        return np.array(
            [self.inventory] + list(self.pipeline) + [self.day % 7, self.day % 30],
            dtype=np.float32
        )
```

**Reward Shaping**

The reward is the negative total period cost (negative because PPO maximises reward and we want to minimise cost). Additional reward shaping:
- Penalty multiplier of 3x on stockout cost for A-class items (strategic importance).
- Small positive reward (+0.1) for maintaining inventory within [SS, SS + EOQ] band to guide early training.
- Zero penalty for intentional stockout when `backorderAllowed = true` (use backorder cost instead).

**Training Configuration (Stable-Baselines3 PPO)**

```python
from stable_baselines3 import PPO

def train_rl_policy(env: InventoryEnv, total_timesteps: int = 1_000_000) -> PPO:
    """
    Train PPO agent on InventoryEnv.
    Benchmark against analytical (s,S) policy after training.
    """
    model = PPO(
        policy='MlpPolicy',
        env=env,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.01,      # Entropy regularisation for exploration
        verbose=1,
    )
    model.learn(total_timesteps=total_timesteps)
    return model
```

**Benchmarking vs (s, S)**

After training, run 100 independent episodes comparing PPO and the analytical (s, S) policy. Report: mean total cost per episode, fill rate, average inventory level, and number of stockout events. PPO should achieve >= 5% cost reduction vs (s, S) to justify deployment overhead.

### 7.4 Isolation Forest for Anomaly Detection

**Purpose**: Complement the LSTM Autoencoder with an interpretable, fast tree-based anomaly detector that operates on engineered features from the movement history. Isolation Forest is effective for tabular feature vectors where the LSTM temporal approach may be resource-constrained.

**Feature Engineering from Movement History**

```python
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

def engineer_features(movements_df: pd.DataFrame,
                       sku: str,
                       lookback_days: int = 30) -> pd.DataFrame:
    """
    Build daily anomaly detection features for a single SKU.

    Features: rolling means, standard deviations, ratios, and spikes.
    """
    df = movements_df[movements_df['sku'] == sku].copy()
    df['date'] = pd.to_datetime(df['posted_at']).dt.date
    daily = df.groupby(['date', 'movement_type'])['quantity_units'].sum().unstack(fill_value=0)

    # Core features
    daily['net_movement'] = daily.get('GOODS_RECEIPT', 0) - daily.get('GOODS_ISSUE', 0)
    daily['adj_total'] = (daily.get('ADJUSTMENT_POSITIVE', 0) +
                          daily.get('ADJUSTMENT_NEGATIVE', 0))
    daily['scrap_units'] = daily.get('SCRAP', 0)

    # Rolling statistics (7-day and 30-day)
    for col in ['net_movement', 'adj_total', 'GOODS_ISSUE']:
        if col in daily.columns:
            daily[f'{col}_roll7_mean'] = daily[col].rolling(7, min_periods=1).mean()
            daily[f'{col}_roll7_std'] = daily[col].rolling(7, min_periods=1).std().fillna(0)
            daily[f'{col}_roll30_mean'] = daily[col].rolling(30, min_periods=1).mean()

    # Spike ratio: today's issue vs 30-day mean
    if 'GOODS_ISSUE' in daily.columns:
        daily['issue_spike_ratio'] = daily['GOODS_ISSUE'] / (
            daily['GOODS_ISSUE_roll30_mean'].replace(0, 1)
        )

    return daily.fillna(0)

def train_isolation_forest(features_df: pd.DataFrame,
                             contamination: float = 0.05) -> tuple:
    """
    Train Isolation Forest. Returns fitted model and scaler.
    contamination: expected proportion of outliers in training data.
    """
    scaler = StandardScaler()
    X = scaler.fit_transform(features_df.values)
    model = IsolationForest(
        n_estimators=200,
        max_samples='auto',
        contamination=contamination,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X)
    return model, scaler
```

**Alert Routing**

Isolation Forest anomaly scores are routed as follows:
- Score < -0.2 (strong anomaly): immediate alert to warehouse manager + inventory controller.
- Score in [-0.2, -0.1]: logged to anomaly dashboard for daily review.
- Score >= -0.1: no alert.

For A-class items, alert thresholds are tightened by 0.05 (i.e., strong anomaly at < -0.15).

### 7.5 XGBoost for Stockout Prediction

**Purpose**: Predict probability of stockout in the next 7 and 14 days for each SKU-location combination. Early prediction enables proactive replenishment orders before the (r, Q) system ROP is breached, reducing stockout frequency.

**Lag Features and Rolling Demand**

```python
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import roc_auc_score

def build_stockout_features(movements_df: pd.DataFrame,
                              pos_df: pd.DataFrame,
                              forecast_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build training features for stockout prediction.

    movements_df : daily movement aggregates per SKU
    pos_df       : purchase orders with lead time actuals
    forecast_df  : demand forecasts from planning module
    """
    df = movements_df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values(['sku', 'date'])

    feature_cols = []

    # Lag features (1, 3, 7, 14, 28 days of net stock change)
    for lag in [1, 3, 7, 14, 28]:
        col = f'net_change_lag{lag}'
        df[col] = df.groupby('sku')['net_movement'].shift(lag)
        feature_cols.append(col)

    # Rolling demand statistics
    for window in [7, 14, 28]:
        col_mean = f'demand_roll{window}_mean'
        col_std = f'demand_roll{window}_std'
        df[col_mean] = df.groupby('sku')['qty_issued'].transform(
            lambda x: x.rolling(window, min_periods=1).mean()
        )
        df[col_std] = df.groupby('sku')['qty_issued'].transform(
            lambda x: x.rolling(window, min_periods=1).std().fillna(0)
        )
        feature_cols.extend([col_mean, col_std])

    # Lead time variance feature (from PO history)
    lt_stats = pos_df.groupby('supplier_id')['actual_lead_time_days'].agg(['mean', 'std'])
    lt_stats.columns = ['lt_mean', 'lt_std']
    df = df.merge(lt_stats, on='supplier_id', how='left')
    feature_cols.extend(['lt_mean', 'lt_std'])

    # Forecast error (actual vs forecast, 7-day rolling MAE)
    df = df.merge(forecast_df[['sku', 'date', 'forecast_qty']], on=['sku', 'date'], how='left')
    df['forecast_error'] = (df['qty_issued'] - df['forecast_qty']).abs()
    df['forecast_mae_7d'] = df.groupby('sku')['forecast_error'].transform(
        lambda x: x.rolling(7, min_periods=1).mean()
    )
    feature_cols.extend(['forecast_qty', 'forecast_mae_7d'])

    # Calendar features
    df['day_of_week'] = df['date'].dt.dayofweek
    df['week_of_year'] = df['date'].dt.isocalendar().week.astype(int)
    df['month'] = df['date'].dt.month
    feature_cols.extend(['day_of_week', 'week_of_year', 'month'])

    # Current inventory balance (from projection)
    feature_cols.append('current_balance')

    return df[['sku', 'date'] + feature_cols + ['stockout_7d', 'stockout_14d']].dropna()

def train_xgboost_stockout(df: pd.DataFrame, target: str = 'stockout_7d') -> xgb.XGBClassifier:
    """
    Train XGBoost stockout predictor with time-series cross-validation.

    target : 'stockout_7d' or 'stockout_14d'
    """
    feature_cols = [c for c in df.columns if c not in ['sku', 'date', 'stockout_7d', 'stockout_14d']]
    X = df[feature_cols].values
    y = df[target].values

    tscv = TimeSeriesSplit(n_splits=5)
    model = xgb.XGBClassifier(
        n_estimators=400,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=(y == 0).sum() / (y == 1).sum(),  # Handle class imbalance
        eval_metric='auc',
        use_label_encoder=False,
        random_state=42,
        n_jobs=-1,
    )

    auc_scores = []
    for train_idx, val_idx in tscv.split(X):
        model.fit(X[train_idx], y[train_idx],
                  eval_set=[(X[val_idx], y[val_idx])],
                  verbose=False)
        preds = model.predict_proba(X[val_idx])[:, 1]
        auc_scores.append(roc_auc_score(y[val_idx], preds))

    print(f"Mean AUC ({target}): {np.mean(auc_scores):.4f} (+/- {np.std(auc_scores):.4f})")

    # Final fit on all data
    model.fit(X, y)
    return model
```

**Deployment Decision Rule**

XGBoost stockout predictions feed a replenishment escalation queue:
- P(stockout_7d) >= 0.70: immediate emergency replenishment order, flag for planner review.
- P(stockout_7d) in [0.40, 0.70): accelerated replenishment (reduce review period to 1 day for this SKU).
- P(stockout_7d) < 0.40: standard replenishment cycle.

---

## 8. Phase 5: Integration & Automation

### 8.1 SAP WM/EWM Integration

**Goods Receipt posting (SAP BAPI)**

```
BAPI_GOODSMVT_CREATE
  - Movement Type: 101 (GR for PO), 261 (GI for production order), 551 (Scrapping)
  - Plant / Storage Location mapped from internal locationId
  - Batch (Lot) number passed in MATERIALDOCUMENT_ITEM-BATCH
  - Idempotency: check MATERIALDOCUMENT table for matching reference doc + item before posting
```

Every BAPI call result is written to the internal event store audit log regardless of success or failure. Retry with exponential backoff (base 2s, max 5 retries) for transient SAP RFC errors (RFC_EXCEPTION class).

**SAP EWM Transfer Order integration**

For warehouse execution (putaway and picking), transfer orders are created in EWM via:
- `/SCWM/PRDI_TOC_CREATE_V2` for putaway
- `/SCWM/TO_CREATE_PICK` for picking

Transfer order status callbacks (confirmed/cancelled) are received via SAP outbound IDocs (WMMBXY.WMMBXY01) routed through the internal message bus.

### 8.2 Oracle WMS Integration

Oracle WMS Cloud exposes REST APIs (JSON/OAuth 2.0). Key endpoints consumed:

| Operation | Oracle WMS Endpoint | Internal Event |
|---|---|---|
| ASN creation | `POST /inventory/asn` | Triggered by GOODS_RECEIPT movement |
| Lot inquiry | `GET /inventory/lots/{lotNumber}` | Used in FEFO picking |
| Outbound shipment confirmation | `POST /outbound/shipments/{id}/confirm` | Triggers GOODS_ISSUE |
| Cycle count results | `POST /inventory/cycle-count-results` | Triggers ADJUSTMENT events |

All Oracle WMS API calls use idempotency headers (`Idempotency-Key: {uuid}`) to prevent duplicate postings.

### 8.3 RFID and Barcode Scanner Integration

**GS1-128 barcode scanning**

Receiving dock scanners decode GS1-128 labels containing:
- Application Identifier (AI) 01: GTIN-14
- AI 10: Batch/Lot number
- AI 17: Expiry date (YYMMDD)
- AI 37: Quantity
- AI 00: SSCC-18 (pallet level)

The middleware layer (Node.js) decodes AI structures and maps them to `StockMovement` event fields, ensuring the idempotencyKey is derived from the SSCC + movement type to prevent duplicate scans creating duplicate movements.

**RFID integration**

RFID reads at dock doors (conveyor or portal readers) trigger real-time inventory updates. Each RFID tag encodes GTIN and serial number (GS1 SGTIN-96 EPC encoding). The RFID middleware:
1. Deduplicates reads within a 2-second time window per EPC.
2. Correlates EPC to internal `sku`, `lotNumber`, and `locationId`.
3. Publishes a `RFID_READ` event to the internal bus.
4. The inventory service consumes `RFID_READ` events and triggers TRANSFER_IN/TRANSFER_OUT movements when the location transition is confirmed.

### 8.4 ERP GL Posting Automation

The GL posting service subscribes to all `StockMovement` events and generates journal entries asynchronously:

```typescript
async function postGLJournal(movement: StockMovement): Promise<void> {
  const accounts = getJournalAccounts(movement.movementType);
  const journalEntry = {
    externalReference: movement.movementId,
    idempotencyKey: `GL-${movement.idempotencyKey}`,
    debitAccount: accounts.debit,
    creditAccount: accounts.credit,
    amountCents: movement.totalValueCents,
    currency: 'USD',
    postingDate: movement.postedAt.split('T')[0],
    description: `${movement.movementType} / SKU ${movement.sku} / ${movement.quantityUnits} ${movement.sku}`,
    costCenter: movement.locationId,
  };
  await erpGLAdapter.post(journalEntry);
}
```

The GL posting service must be idempotent: if the ERP returns a duplicate-key error for a given `idempotencyKey`, it is treated as success (the posting already exists).

---

## 9. Phase 6: Continuous Improvement

### 9.1 Model Governance and Retraining Cadence

| Model | Retrain Trigger | Minimum Frequency | Validation Gate |
|---|---|---|---|
| LSTM Autoencoder | KS-test drift p < 0.05 on movement features | Monthly | Recall >= 80% on labelled anomaly test set |
| RL Policy (PPO) | Mean episode reward drops > 10% vs baseline | Quarterly | Cost reduction >= 5% vs (s,S) benchmark |
| Isolation Forest | Contamination estimate shifts > 2pp | Monthly | FPR <= 7% on normal validation set |
| XGBoost Stockout | AUC drops below 0.75 on holdout | Monthly | AUC >= 0.78 on rolling 90-day test set |

### 9.2 ABC-XYZ Reclassification

Reclassify all SKUs quarterly:
1. Recompute ACV using last 12 months of COGS movements.
2. Recompute CV from last 12 months of weekly demand.
3. Reassign ABC and XYZ classes.
4. Trigger policy parameter updates (safety stock method, service level target, review period).
5. Communicate changes to affected planning teams.

### 9.3 Supplier Lead Time Review

Update `sigma_LT` inputs to Method 4 safety stock calculations:
- Monthly: compute lead time statistics from last 6 months of PO receipts per supplier.
- Flag any supplier whose `sigma_LT / mean_LT` (CV of lead time) exceeds 0.30 for supplier management escalation.

### 9.4 Kaizen Event Programme

Schedule quarterly inventory kaizen events:
- Focus on top-10 highest DIO SKUs: investigate root causes (demand forecast accuracy, supplier reliability, over-purchasing).
- Focus on top-10 highest obsolescence exposure SKUs: develop disposal or repurposing plans.
- Review fill rate miss events: trace each miss to root cause (stockout, partial fulfillment, quality hold) and implement countermeasures.

### 9.5 SCOR-DS Maturity Progression

| Maturity Level | Capability | Target Timeline |
|---|---|---|
| Level 1 | Manual, reactive inventory management | AS-IS baseline |
| Level 2 | Standardised processes, ERP-integrated | End of Phase 2 (Month 6) |
| Level 3 | Analytically driven replenishment (EOQ, safety stock) | End of Phase 3 (Month 10) |
| Level 4 | Predictive ML models, RL policy in production | End of Phase 4 (Month 16) |
| Level 5 | Autonomous, self-optimising inventory with closed-loop learning | End of Phase 6 (Month 24) |

---

## 10. Technology Stack & Architecture

### 10.1 Domain Layer (TypeScript)

| Component | Technology | Pattern |
|---|---|---|
| Aggregates | TypeScript 5.3 | Domain-Driven Design |
| Event store | PostgreSQL 16 (append-only) | CQRS / Event Sourcing |
| Read projections | PostgreSQL materialised views | Eventual consistency |
| API layer | Node.js 20 LTS + Fastify | REST + JSON Schema validation |
| Message bus | Apache Kafka 3.7 | Domain event streaming |
| GL adapter | SAP RFC gateway / Oracle REST | Adapter pattern |

### 10.2 ML/AI Layer (Python)

| Component | Library | Version |
|---|---|---|
| Numerical computation | numpy | >= 1.26 |
| Scientific computation | scipy | >= 1.12 |
| Data manipulation | pandas | >= 2.2 |
| Statistical models | statsmodels | >= 0.14 |
| Classical ML | scikit-learn | >= 1.4 |
| Gradient boosting | xgboost | >= 2.0 |
| Deep learning | torch (PyTorch) | >= 2.2 |
| RL framework | stable-baselines3 | >= 2.2 |
| RL environment | gymnasium | >= 0.29 |
| API serving | fastapi | >= 0.110 |
| Experiment tracking | mlflow (Apache-2.0) | >= 2.11 |

### 10.3 Infrastructure

```
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway (Nginx)                       │
├───────────────────────┬─────────────────────────────────────┤
│  Inventory Service    │    ML Inference Service              │
│  (Node.js / TS)       │    (FastAPI / Python)               │
├───────────────────────┴─────────────────────────────────────┤
│              Apache Kafka (Domain Events)                    │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL 16       │  Object Storage (MinIO)              │
│  (Event Store +      │  (ML Artefacts, Feature Parquet)     │
│   Read Models)       │                                      │
├──────────────────────┴─────────────────────────────────────-┤
│  Kubernetes 1.28 (Training Jobs, Services, CronJobs)        │
└─────────────────────────────────────────────────────────────┘
```

### 10.4 Security Architecture

- All inter-service communication uses mTLS (certificates managed by cert-manager).
- ERP credentials (SAP RFC, Oracle OAuth) stored in HashiCorp Vault; injected as environment variables at pod startup.
- ML model artefacts signed with SHA-256 checksum; checksum verified at inference service startup.
- All API endpoints require JWT authentication (RS256); role-based access control enforced at gateway.
- Sensitive stock adjustment events are immutable in the event store — no delete capability exposed via API.

---

## 11. Change Management & Training

### 11.1 Stakeholder Engagement Plan

| Stakeholder Group | Key Concern | Engagement Approach |
|---|---|---|
| Warehouse Operations | Disruption to daily pick/pack workflow | Early involvement in UAT; super-user champions per shift |
| Inventory Planners | Loss of spreadsheet control; model transparency | Training on parameter tuning; dashboard access |
| Finance Controllers | GL accuracy; audit trail completeness | Joint design of journal entry schema; parallel run for 1 month |
| Procurement | Lead time data quality; safety stock changes | Data validation workshops in Phase 0; regular recalibration reviews |
| IT / ERP Team | Integration complexity; data governance | Detailed interface specifications; dedicated integration team |
| Senior Leadership | ROI timeline; KPI improvement | Monthly executive dashboard; milestone reporting |

### 11.2 Training Curriculum

**Role: Warehouse Operator**
- Duration: 4 hours
- Topics: RFID/barcode scanning procedures, FEFO picking compliance, cycle count process, how to handle discrepancy exceptions
- Format: Hands-on simulation in UAT environment

**Role: Inventory Planner**
- Duration: 2 days
- Topics: ABC-XYZ classification logic, safety stock policy interpretation, replenishment parameter review, ML dashboard interpretation, manual override procedures
- Format: Classroom + system walkthrough

**Role: Inventory Controller / Analyst**
- Duration: 3 days
- Topics: Event sourcing model overview, GL journal structure, reconciliation procedures, Python model parameter tuning (safety stock, EOQ inputs), anomaly alert triage
- Format: Technical workshop

**Role: Finance Controller**
- Duration: 1 day
- Topics: Inventory valuation methods (FIFO/WAC), GL account mapping, month-end closing procedures, audit trail queries
- Format: Workshop with finance team

### 11.3 Cutover Strategy

**Parallel run period**: 4 weeks minimum before legacy system decommission. During parallel run:
- All movements posted to both old system and new event store.
- Daily reconciliation report comparing closing balances; discrepancies > 0.1% investigated immediately.
- No ML model predictions acted on until parallel run achieves >= 99% balance agreement for 10 consecutive days.

**Cutover sequence**:
1. Freeze legacy inventory balances at end of business on cutover date.
2. Load opening balances as `ADJUSTMENT_POSITIVE` events with reference doc `MIGRATION_OPENING_BALANCE_{date}`.
3. Activate Kafka consumers for ERP movement feeds.
4. Enable ML inference service in shadow mode (predictions logged but not actioned) for 30 days.
5. Enable ML action mode (replenishment recommendations acted on) after shadow mode validation.

---

## 12. Implementation KPIs

### 12.1 Programme Health KPIs

These KPIs track implementation progress and are reported weekly to the programme steering committee.

| KPI | Measurement Method | Green Threshold | Red Threshold |
|---|---|---|---|
| Data migration completeness | % of active SKUs with complete master data | >= 98% | < 90% |
| Balance reconciliation accuracy | System vs physical match | >= 99.5% | < 97% |
| Integration uptime | ERP GL posting success rate (30-day rolling) | >= 99.9% | < 99% |
| Cycle count compliance | % of planned counts completed on schedule | >= 95% | < 85% |
| ML model AUC (XGBoost) | Holdout set AUC | >= 0.78 | < 0.70 |
| Stockout incident rate | Stockouts per 1,000 order lines (weekly) | <= 2.0 | >= 8.0 |
| User adoption | % of planners using system (not spreadsheet) for decisions | >= 90% | < 70% |

### 12.2 Business Outcome KPIs

Measured at 6, 12, and 24 months post go-live against baseline established in Phase 0:

| KPI | Baseline (typical) | 12-Month Target | 24-Month Target |
|---|---|---|---|
| Inventory Turnover Ratio | Benchmark varies by industry | +15% vs baseline | +25% vs baseline |
| DIO (Days Inventory Outstanding) | Benchmark varies | -10 days vs baseline | -18 days vs baseline |
| Fill Rate (line-item) | ~94% | >= 98.0% | >= 98.5% |
| OTIF | ~91% | >= 96.0% | >= 97.5% |
| Inventory Accuracy Rate | ~88% | >= 99.0% | >= 99.5% |
| Obsolescence write-offs | 3-6% of inventory value | <= 2.0% | <= 1.5% |
| Stockout incidents | Baseline count | -35% | -50% |
| Working capital reduction | — | -12% of inventory value | -20% of inventory value |

---

## 13. Risk & Mitigation

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| ERP GL posting failures create reconciliation gaps | Medium | High | Idempotent posting with dead-letter queue; daily reconciliation report; manual repost SOP within 24 hours |
| Negative inventory during cutover (data migration timing gap) | Medium | High | Enforce `backorderAllowed=false` at go-live; load opening balances before activating movement feeds; reconciliation freeze window |
| LSTM Autoencoder high false-positive rate causing alert fatigue | Medium | Medium | Threshold calibration at 5% FPR on held-out normal data; tiered alert routing; weekly alert quality review in first 3 months |
| FEFO non-compliance by warehouse staff (picking by FIFO habit) | High | High | System-enforced lot selection (WMS sends specific lot pick instruction); audit report on lot sequence deviations |
| Poor demand history quality for XGBoost training (< 24 months) | Medium | Medium | Bootstrap with phase-in: deploy rule-based (r,Q) first; accumulate data; train XGBoost when 18+ months available |
| RL policy (PPO) underperforms (s,S) in live environment | Low | Medium | Deploy as shadow recommendation only; human planner approval required for RL-generated orders in first 6 months; promote to auto-approve after demonstrated 5% cost reduction |
| Lead time distribution data insufficient for Method 4 (< 30 PO observations) | High | Medium | Default to Method 3 until N >= 30; flag affected SKU-supplier combinations for tracking in Phase 6 review |
| SAP/Oracle integration latency causes stale inventory balances | Low | High | Real-time posting with 15-second maximum lag SLA; circuit breaker; fallback to manual posting queue |
| REACH/UFLPA compliance data missing at go-live | Medium | High | Block goods receipt for affected suppliers until compliance data uploaded; legal/compliance team escalation path |
| Lot tracking omitted for controlled storage items | Low | Critical | System-enforced: `lotTracked` validation on GOODS_RECEIPT rejects event if null lot number for controlled items |

---

## 14. Timeline Summary

| Phase | Activities | Duration | Start Month | End Month | Dependencies |
|---|---|---|---|---|---|
| Phase 0 | AS-IS assessment, data gap analysis, baseline KPIs | 5 weeks | M1 | M2 | None |
| Phase 1 | Item master governance, event store, GL integration design | 8 weeks | M2 | M4 | Phase 0 complete |
| Phase 2 | Process standardisation, cycle counting, core analytics | 8 weeks | M4 | M6 | Phase 1 complete |
| Phase 3 | Mathematical models (ABC/XYZ, safety stock, EOQ, FEFO) | 10 weeks | M6 | M8.5 | Phase 2 complete; 12+ months demand history |
| Phase 4 | ML/AI pipeline (LSTM, RL, IF, XGBoost) | 14 weeks | M8 | M11.5 | Phase 3 running; 18+ months demand history |
| Phase 5 | SAP/Oracle integration, RFID, GS1, GL automation | 8 weeks | M6 | M9 | Phase 1 complete; ERP access confirmed |
| Phase 6 | Continuous improvement, model governance, kaizen | Ongoing | M12 | M24+ | All prior phases complete |
| Parallel Run | Legacy + new system simultaneous operation | 4 weeks | M9 | M10 | Phase 5 complete |
| Go-Live | Full production cutover | 1 week | M10 | M10 | Parallel run >= 99% accuracy |
| Post Go-Live Stabilisation | Hypercare, daily KPI review | 8 weeks | M10 | M12 | Go-live complete |

**Total programme duration (Phase 0 through Go-Live + Stabilisation)**: approximately 12 months.
**Full SCOR-DS Level 5 maturity (including ML production)**: approximately 24 months.

---

## 15. References

### Academic References

- Chopra, S. & Meindl, P. (2016). *Supply Chain Management: Strategy, Planning, and Operation* (6th ed.). Pearson. — Chapters 11 (Safety Stock), 12 (Sourcing), 13 (Transportation).
- Ballou, R.H. (2004). *Business Logistics/Supply Chain Management* (5th ed.). Pearson.
- Christopher, M. (2022). *Logistics and Supply Chain Management* (6th ed.). FT Publishing International.
- Harris, F.W. (1913). How Many Parts to Make at Once. *Factory, The Magazine of Management*, 10(2), 135-136.
- Wagner, H.M. & Whitin, T.M. (1958). Dynamic Version of the Economic Lot Size Model. *Management Science*, 5(1), 89-96.
- Silver, E.A. (1976). A Simple Method of Determining Order Quantities in Joint Replenishments Under Deterministic Demand. *Management Science*, 22(12), 1351-1361.
- Petruzzi, N.C. & Dada, M. (1999). Pricing and the Newsvendor Problem: A Review with Extensions. *Operations Research*, 47(2), 183-194.
- Hochreiter, S. & Schmidhuber, J. (1997). Long Short-Term Memory. *Neural Computation*, 9(8), 1735-1780.
- Schulman, J., Wolski, F., Dhariwal, P., Radford, A., & Klimov, O. (2017). Proximal Policy Optimization Algorithms. *arXiv:1707.06347*.
- Liu, F.T., Ting, K.M., & Zhou, Z-H. (2008). Isolation Forest. *ICDM 2008*, 413-422.
- Chen, T. & Guestrin, C. (2016). XGBoost: A Scalable Tree Boosting System. *KDD 2016*, 785-794.

### Standards and Regulations

- ASCM (2019). *SCOR Digital Standard*. Association for Supply Chain Management.
- ISO (2022). *ISO 28000:2022 — Security and Resilience: Supply Chain Security Management Systems*. International Organization for Standardization.
- ISO (1999). *ISO 2859-1:1999 — Sampling Procedures for Inspection by Attributes*. International Organization for Standardization.
- ISO (2006). *EU REACH Regulation No 1907/2006*. European Parliament.
- GS1 (2023). *GS1 General Specifications Version 23.0*. GS1 Global.
- ICC (2019). *Incoterms® 2020*. International Chamber of Commerce.
- US Congress (2021). *Uyghur Forced Labor Prevention Act (UFLPA) — Public Law 117-78*.
- European Parliament (2024). *Directive 2024/1760 on Corporate Sustainability Due Diligence (CSDDD)*.

### Software and Framework Documentation

- PyTorch (2024). *PyTorch Documentation v2.2*. Meta AI. https://pytorch.org/docs/
- Stable-Baselines3 (2024). *SB3 Documentation v2.2*. https://stable-baselines3.readthedocs.io/
- scikit-learn (2024). *scikit-learn Documentation v1.4*. https://scikit-learn.org/stable/
- XGBoost (2024). *XGBoost Documentation v2.0*. https://xgboost.readthedocs.io/
- SAP SE (2024). *SAP Extended Warehouse Management (EWM) — Configuration Guide*. SAP Help Portal.
- Oracle (2024). *Oracle WMS Cloud REST API Reference*. Oracle Documentation.
- GS1 (2023). *GS1 Application Identifiers Standard*. GS1 Global Office.

### Internal References

- `src/departments/01-procurement/domain/PurchaseOrder.ts` — PO approval workflow
- `src/departments/02-supplier-management/domain/SupplierScorecard.ts` — OTD/OTIF/PPM metrics
- `src/departments/04-demand-planning/algorithms/Forecasting.ts` — SMA/SES/Holt/Holt-Winters
- `src/departments/04-demand-planning/algorithms/SafetyStock.ts` — Methods 1-4 implementation
- `src/departments/10-compliance/UFLPA.ts` — XUAR risk assessment
- `src/departments/10-compliance/REACH.ts` — SVHC substance tracking
- `src/shared/types.ts` — Money, UOM, Incoterms shared types
- `python/05_inventory_management/` — All Python models referenced in Phase 3 and Phase 4
- `docs/standards/REGULATORY_FRAMEWORK.md` — Full regulatory reference matrix

---

*This document is subject to annual review or upon material change to regulatory requirements, organisational structure, or technology platform. All changes must be approved by the VP Supply Chain and Chief Data Officer before implementation.*

*Document Owner: Supply Chain Architecture Office*
*Review Cycle: Annual (next review: 2027-06-20)*
