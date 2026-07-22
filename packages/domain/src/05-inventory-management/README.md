# 05 — Inventory Management

## Overview

The Inventory Management department owns the **item master** and the **stock movement event log** — the authoritative, append-only ledger of every unit entering or leaving the system. Built on **Event Sourcing + CQRS**, current stock balances are never stored as mutable fields; instead they are derived by replaying the ordered sequence of `StockMovement` events. This guarantees a complete, tamper-evident audit trail compliant with **GAAP / IFRS IAS 2** and **US UCC Article 2**.

Every movement type — from purchase receipts to customer returns — generates a **double-entry GL journal entry** (debit / credit), ensuring the inventory sub-ledger reconciles with the general ledger at all times. Items are classified using the **9-box ABC-XYZ matrix**: ABC ranks SKUs by annual consumption value (Pareto 80/20); XYZ ranks by demand variability (Coefficient of Variation). The intersection drives replenishment strategy, safety stock policy, and warehouse slotting priority.

SCOR mapping: **Return** (RETURN_FROM_CUSTOMER movement type).

---

## KPIs

| KPI | Definition | World-Class Target |
|-----|------------|--------------------|
| **Inventory Turnover Ratio (ITR)** | COGS / Average Inventory Value | ≥ 8–12× (FMCG) |
| **DIO — Days Inventory Outstanding** | 365 / ITR | < 45 days (fast-moving) |
| **Fill Rate** | Orders fulfilled without backorder / Total orders | ≥ 98% |
| **Stockout Rate** | SKUs stocked-out at any point / Total active SKUs | < 2% |
| **Shrinkage %** | (Book inventory − Physical count) / Book inventory | < 0.5% (retail) |
| **Dead Stock %** | Zero-movement SKUs >90 days / Total active SKUs | < 3% |

---

## Standards

| Standard | Scope | Implementation |
|----------|-------|----------------|
| **GS1 General Specifications v23.0** | GTIN (item identification), SSCC (pallet/lot), UOM codes | `shared/types.ts` — `UOM` constant; all domain objects |
| **ISO 28000:2022** | Supply chain security management system | `Supplier.certifications`; lot-tracked items |
| **US UCC Article 2** | Sale of goods — quantity must be specified | `POLineItem.quantity`; movement quantity validation |
| **GAAP / IFRS IAS 2** | Inventory valuation (FIFO / weighted avg), disclosure | Double-entry GL mapping in `StockMovement.ts` |

---

## Domain Files

### `domain/InventoryItem.ts` — Item Master

The central master record for every stockkeeping unit. Key fields and logic:

| Field | Type | Description |
|-------|------|-------------|
| `sku` | `string` | Immutable once created. Status flags used instead of deletion. |
| `gtin` | `string` | GS1 GTIN-14 global trade item number |
| `abcClass` | `'A' \| 'B' \| 'C'` | Pareto classification by annual consumption value |
| `xyzClass` | `'X' \| 'Y' \| 'Z'` | Variability classification by CV of demand |
| `lotTracked` | `boolean` | Required when `storageCondition !== AMBIENT` or `reachSVHC = true` |
| `reachSVHC` | `boolean` | EU REACH 1907/2006 — Substance of Very High Concern flag |
| `storageCondition` | `AMBIENT \| REFRIGERATED \| FROZEN \| CONTROLLED` | Drives lot tracking requirement |
| `status` | `ACTIVE \| DISCONTINUED \| BLOCKED` | Soft-delete via status; never hard-delete |
| `unitCost` | `Money` | Integer cents only — no floats |

**9-box ABC-XYZ Strategy Matrix:**

| | X (stable) | Y (moderate) | Z (volatile) |
|--|-----------|-------------|-------------|
| **A** | Lean replenishment, min safety stock | SES forecasting, moderate SS | Holt-Winters, high SS buffer |
| **B** | Periodic review, standard SS | Balanced approach | Review cycle + contingency stock |
| **C** | Infrequent reorder, min space | Low priority, batch order | Evaluate discontinuation |

### `domain/StockMovement.ts` — Event Log

Append-only movement record. Every record is immutable after creation.

**MovementType union (15 types):**

| Movement Type | Direction | GL Entry |
|--------------|-----------|----------|
| `PURCHASE_RECEIPT` | INBOUND | Dr Inventory / Cr Accounts Payable |
| `RETURN_FROM_CUSTOMER` | INBOUND | Dr Inventory / Cr Customer Returns |
| `PRODUCTION_OUTPUT` | INBOUND | Dr Inventory / Cr WIP |
| `POSITIVE_ADJUSTMENT` | INBOUND | Dr Inventory / Cr Inventory Adjustment |
| `TRANSFER_IN` | INBOUND | Dr Inventory (destination) / Cr Inventory (source) |
| `SALE_SHIPMENT` | OUTBOUND | Dr COGS / Cr Inventory |
| `RETURN_TO_SUPPLIER` | OUTBOUND | Dr Accounts Payable / Cr Inventory |
| `PRODUCTION_CONSUMPTION` | OUTBOUND | Dr WIP / Cr Inventory |
| `NEGATIVE_ADJUSTMENT` | OUTBOUND | Dr Inventory Adjustment / Cr Inventory |
| `WRITE_OFF` | OUTBOUND | Dr Inventory Adjustment / Cr Inventory |
| `TRANSFER_OUT` | OUTBOUND | Dr Inventory (destination) / Cr Inventory (source) |
| `SCRAPPED` | OUTBOUND | Dr Scrap Expense / Cr Inventory |
| `SAMPLE_ISSUE` | OUTBOUND | Dr Sample Expense / Cr Inventory |
| `CONSIGNMENT_OUT` | OUTBOUND | Dr Consignment Asset / Cr Inventory |
| `CYCLE_COUNT_ADJUSTMENT` | INBOUND/OUTBOUND | Dr/Cr Inventory Adjustment |

Key fields: `idempotencyKey` (UUID) prevents duplicate processing on retry. `projectStockBalance()` replays the full event log for a given SKU+location and sums INBOUND movements minus OUTBOUND. Negative balance is blocked unless `backorderAllowed = true` on the item.

---

## Business Rules

1. **Never allow negative inventory** without `backorderAllowed = true` on the `InventoryItem`.
2. **All stock movements** generate a double-entry GL journal entry (debit/credit) — no movement without a journal entry.
3. **Lot tracking is mandatory** for items where `storageCondition !== AMBIENT` or `reachSVHC = true`.
4. **Idempotency key** (`idempotencyKey: UUID`) must be provided by the caller; duplicate keys are rejected — safe to retry on network failure.
5. **Soft-delete only** — `StockMovement` records are never deleted; `InventoryItem` uses `status: DISCONTINUED | BLOCKED` flags.
6. **SKU codes are immutable** once created — name/description changes allowed, SKU code is not.
7. **RETURN_FROM_CUSTOMER** movements must reference the originating `SalesOrderId` for SCOR Return process traceability.

---

## Applied Mathematical Models

### 1. Stock Projection via Event Sourcing

Current balance is derived entirely from the event log — there is no mutable balance field:

```
Balance(SKU, Location, t) = Σ qty_i  for all movements i where:
    - movementType ∈ INBOUND_TYPES  → +qty
    - movementType ∈ OUTBOUND_TYPES → -qty
    - timestamp_i ≤ t
```

**INBOUND_TYPES** = { PURCHASE_RECEIPT, RETURN_FROM_CUSTOMER, PRODUCTION_OUTPUT, POSITIVE_ADJUSTMENT, TRANSFER_IN, CYCLE_COUNT_ADJUSTMENT(+) }

Replaying the entire event log to any point in time guarantees a complete audit trail. Time-travel queries ("what was the stock on date X?") are native to the model.

> Reference: Fowler, M. — *Event Sourcing* pattern (martinfowler.com, 2005); Vernon, V. — *Implementing Domain-Driven Design* (Addison-Wesley, 2013).

---

### 2. ABC by Value (Pareto 80/20)

Rank all active SKUs by **Annual Consumption Value**:

```
ACV_i = Annual_Demand_i × Unit_Cost_i

Sorted descending: ACV_1 ≥ ACV_2 ≥ ... ≥ ACV_n

Cumulative_Value_% up to rank k = Σ(ACV_1..k) / Σ(ACV_all) × 100

A-class:  Cumulative_Value_% ≤ 80%   (~20% of SKUs)
B-class:  80% < Cumulative_Value_% ≤ 95%  (~30% of SKUs)
C-class:  Cumulative_Value_% > 95%   (~50% of SKUs)
```

> Reference: Silver, E.A., Pyke, D.F. & Peterson, R. — *Inventory Management and Production Planning and Scheduling*, 3rd Ed. (Wiley, 1998), Ch. 3.

---

### 3. XYZ by Coefficient of Variation

Classify SKUs by demand predictability over a rolling 12-month window:

```
μ_demand = mean(monthly_demand_1..12)
σ_demand = std_dev(monthly_demand_1..12)

CV = σ_demand / μ_demand

X-class:  CV < 0.10   → very stable, highly predictable
Y-class:  0.10 ≤ CV < 0.25  → moderate variability
Z-class:  CV ≥ 0.25   → highly variable, difficult to forecast
```

> Reference: Chopra, S. & Meindl, P. — *Supply Chain Management*, 6th Ed. (Pearson, 2016), Ch. 11.

---

### 4. Inventory Turnover Ratio (ITR)

```
ITR = COGS / Average_Inventory_Value

Average_Inventory_Value = (Opening_Balance + Closing_Balance) / 2
```

| Sector | World-Class ITR |
|--------|----------------|
| FMCG / Grocery | 8–12× |
| Automotive | 12–20× |
| Electronics | 6–10× |
| Industrial MRO | 3–6× |

High ITR indicates efficient capital deployment; excessively high ITR (>20×) signals stockout risk.

> Reference: Ballou, R.H. — *Business Logistics / Supply Chain Management*, 5th Ed. (Pearson, 2004), Ch. 9.

---

### 5. DIO — Days Inventory Outstanding

```
DIO = 365 / ITR

or equivalently:

DIO = (Average_Inventory_Value / COGS) × 365
```

DIO measures how many days of COGS are tied up in inventory. Lower is better for working capital. Target: < 45 days for fast-moving consumer goods.

---

### 6. Double-Entry Accounting for Inventory Movements

Every `StockMovement` record generates an immutable GL journal entry per **GAAP / IFRS IAS 2**:

```
PURCHASE_RECEIPT:
    Dr  Inventory Asset (1400)         qty × unit_cost
    Cr  Accounts Payable (2100)                      qty × unit_cost

SALE_SHIPMENT:
    Dr  Cost of Goods Sold (5000)      qty × unit_cost
    Cr  Inventory Asset (1400)                       qty × unit_cost

WRITE_OFF / SCRAPPED:
    Dr  Inventory Adjustment Expense (5200)  qty × unit_cost
    Cr  Inventory Asset (1400)                           qty × unit_cost

RETURN_FROM_CUSTOMER:
    Dr  Inventory Asset (1400)         qty × unit_cost
    Cr  Customer Returns Reserve (4800)              qty × unit_cost
```

All amounts in integer cents (`Money.amount: number`). No floating-point arithmetic.

> Reference: International Accounting Standards Board — *IAS 2 Inventories* (IFRS Foundation, 2003); FASB ASC 330 Inventory.

---

## Recommended Machine Learning Models

### 1. CNN + LSTM for Dynamic ABC-XYZ Classification

**Problem:** Static ABC-XYZ classification done quarterly misses mid-quarter demand shifts (promotions, seasonality, new product launches).

**Architecture:** Hybrid CNN-LSTM model.
- **Input:** 52-week rolling demand time series per SKU (1D signal, shape `[52, 1]`)
- **CNN layers:** Extract local temporal patterns (e.g., weekly seasonality peaks)
- **LSTM layers:** Capture long-range dependencies and trend
- **Output:** Softmax over 9 ABC-XYZ classes (A-X, A-Y, A-Z, B-X, ..., C-Z)

**Training:** Supervised — historical ABC-XYZ labels computed from ground truth.
**Benefit:** Enables dynamic weekly reclassification; proactive replenishment policy adjustment.

```python
# Pseudocode
model = Sequential([
    Conv1D(64, kernel_size=4, activation='relu'),
    MaxPooling1D(2),
    LSTM(128, return_sequences=False),
    Dense(64, activation='relu'),
    Dense(9, activation='softmax')  # 9 ABC-XYZ classes
])
```

**Libraries:** TensorFlow / Keras, scikit-learn (label encoding).

---

### 2. Isolation Forest for Anomalous Shrinkage Detection

**Problem:** Shrinkage (theft, damage, counting errors) is detected only at periodic physical counts — often months late.

**Architecture:** Unsupervised anomaly detection on stock movement sequences.
- **Features per location/period:** movement frequency, average quantity, variance ratio, time-between-movements, adjustment ratio
- **Isolation Forest:** Anomaly score based on path length in random tree ensembles
- **Output:** Anomaly score per location × week; alert if score > threshold

**Benefit:** Real-time shrinkage detection — flag suspicious locations for cycle count before loss accumulates.

**Libraries:** `scikit-learn.ensemble.IsolationForest`

---

### 3. Autoencoder for Obsolete Stock Detection

**Problem:** Dead stock (zero movement >90 days) consumes warehouse space and ties up capital; often not caught until year-end.

**Architecture:** Undercomplete autoencoder trained on **normal** (active) item movement patterns.
- **Input:** Encoded movement vector per SKU over 12 weeks (frequency, recency, monetary value)
- **Encoder:** Compresses to latent representation
- **Decoder:** Reconstructs expected movement pattern
- **Anomaly signal:** High reconstruction error (MSE) → item moving abnormally slowly → dead stock candidate

**Output:** Ranked list of SKUs by obsolescence risk score.

**Libraries:** PyTorch (`nn.Module`); can also use TensorFlow Keras `Autoencoder`.

---

### 4. Gradient Boosting for Stockout Prediction

**Problem:** Stockouts cause lost sales, emergency procurement, and customer dissatisfaction. Need 7/14/30-day early warning.

**Features:**
| Feature | Source |
|---------|--------|
| Current stock level (units) | Event sourcing balance |
| Demand forecast (SMA/SES/Holt) | `demand-planning/` |
| Lead time (days, mean + σ) | Supplier scorecard |
| Supplier OTD reliability | `supplier-management/` |
| ABC-XYZ class | Item master |
| Days since last receipt | Movement log |

**Output:** P(stockout within 7 / 14 / 30 days) — triggers reorder alert.

**Libraries:** LightGBM (`lgb.LGBMClassifier`), XGBoost (`xgb.XGBClassifier`).
**Calibration:** Platt scaling or isotonic regression for probability calibration.

---

### 5. Reinforcement Learning for Dynamic Replenishment Policy

**Problem:** Fixed (s, S) reorder policies cannot adapt to changing demand patterns and supply variability.

**Formulation:** Markov Decision Process (MDP)
```
State  s_t = (inventory_level_t, demand_obs_t, lead_time_obs_t, forecast_t)
Action a_t = order_quantity ∈ {0, EOQ, 2×EOQ, ...}
Reward r_t = −(holding_cost × inventory_t + stockout_penalty × max(0, demand_t − inventory_t))
```

**Algorithm:** Proximal Policy Optimization (PPO) or Deep Q-Network (DQN).
**Benefit:** Learns a non-stationary reorder policy that outperforms static (s, S) by 10–20% in holding cost reduction.

**Libraries:** Ray RLlib (`rllib.algorithms.ppo`), Stable-Baselines3 (`sb3.PPO`).

---

## References

1. Chopra, S. & Meindl, P. — *Supply Chain Management*, 6th Ed. (Pearson, 2016)
2. Silver, E.A., Pyke, D.F. & Peterson, R. — *Inventory Management and Production Planning and Scheduling*, 3rd Ed. (Wiley, 1998)
3. Ballou, R.H. — *Business Logistics / Supply Chain Management*, 5th Ed. (Pearson, 2004)
4. Fowler, M. — *Patterns of Enterprise Application Architecture* (Addison-Wesley, 2002)
5. Vernon, V. — *Implementing Domain-Driven Design* (Addison-Wesley, 2013)
6. IFRS Foundation — *IAS 2 Inventories* (2003)
7. GS1 — *General Specifications v23.0* (GS1, 2023)
8. ISO 28000:2022 — *Security and resilience — Supply chain security management systems*
9. Mnih, V. et al. — *Human-level control through deep reinforcement learning* (Nature, 2015)
10. Liu, F.T., Ting, K.M. & Zhou, Z.H. — *Isolation Forest* (IEEE ICDM, 2008)
