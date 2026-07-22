# 13 — Order Management & Customer Service (Order-to-Cash)

> **SCOR-DS Process**: Deliver (sD1–sD4) | **UN/EDIFACT** | **Owner**: Order Management Manager

The Order Management department owns the complete Order-to-Cash (O2C) cycle from sales order capture through delivery, invoicing, and collection. It is responsible for OTIF (On-Time In-Full) performance, ATP (Available-to-Promise) accuracy, Perfect Order Rate, and all customer-facing EDI integrations (UN/EDIFACT ORDERS, ORDRSP, DESADV, INVOIC). The Walmart OTIF standard of ≥ 98 % is the primary external benchmark.

---

## Table of Contents

1. [Order-to-Cash Process](#1-order-to-cash-process)
2. [Domain Files](#2-domain-files)
3. [Key Business Rules](#3-key-business-rules)
4. [Mathematical Models](#4-mathematical-models)
5. [Recommended ML Models](#5-recommended-ml-models)
6. [KPIs & Benchmarks](#6-kpis--benchmarks)
7. [EDI Message Standards](#7-edi-message-standards)
8. [Integration Points](#8-integration-points)
9. [Roles](#9-roles)
10. [References](#10-references)

---

## 1. Order-to-Cash Process

```
1. Order Receipt
   ├── EDI ORDERS (UN/EDIFACT)
   ├── Portal / eCommerce API
   └── Manual entry (email / phone)

2. Order Validation
   ├── Customer active & credit-approved
   ├── Pricing and discount validation
   └── Terms and conditions check

3. ATP Check (Available-to-Promise)
   ├── Real-time inventory availability query
   ├── Confirmed delivery date calculated
   └── Order Acknowledgement issued (EDI ORDRSP)

4. Fulfilment Trigger → Dept. 06 Warehouse
   ├── Pick list released to WMS
   ├── FEFO lot picking for lot-tracked items
   └── Pack and label (GS1 SSCC barcode)

5. Despatch
   ├── Carrier booking (Dept. 07 Logistics)
   ├── Advance Ship Notice issued (EDI DESADV)
   └── Proof of Delivery (POD) captured

6. Delivery Confirmation
   ├── EDI RECADV from customer (receipt confirmation)
   ├── OTIF flags computed: isOnTime, isInFull, isOTIF
   └── isPerfectOrder flag computed

7. Invoicing & Collection
   ├── Commercial invoice issued (EDI INVOIC)
   ├── 3-Way Match in Dept. 11 (customer-side: SO ↔ ASN ↔ POD)
   └── Cash collected → O2C cycle closed
```

---

## 2. Domain Files

### `domain/SalesOrder.ts`

| Export | Description |
|---|---|
| `SalesOrderStatus` | 9-state lifecycle: `DRAFT` → `CONFIRMED` → `ALLOCATED` → `PICKING` → `PACKED` → `SHIPPED` → `DELIVERED` → `INVOICED` → `CLOSED` |
| `SalesOrder` | `{ orderId, customerId, lines[], requestedDeliveryDate, confirmedDeliveryDate, status, isOTIF, isPerfectOrder }` |
| `SalesOrderLine` | `{ skuId, orderedQty, confirmedQty, deliveredQty, atpDate, unitPriceCents }` |
| `createSalesOrder(customerId, lines, requestedDate)` | Factory; runs ATP check; sets `confirmedDeliveryDate`; issues ORDRSP |
| `markDelivered(order, deliveredLines, actualDate)` | Computes `isOnTime`, `isInFull`, `isOTIF`, `isPerfectOrder`; updates order status |
| `calculatePerfectOrderRate(orders[])` | `POR = (perfect orders / total orders) × 100` over a period |

---

## 3. Key Business Rules

1. **OTIF Definition** — `isOTIF = isOnTime AND isInFull`. `isOnTime`: `actualDeliveryDate ≤ confirmedDeliveryDate`. `isInFull`: `deliveredQty ≥ orderedQty` for **all** order lines. Both conditions must be true simultaneously.
2. **ATP Promise Integrity** — Orders are promised only when `ATP_t ≥ order_quantity`. Never over-promise. If ATP is insufficient, `confirmedDeliveryDate` is set to the first date ATP becomes available.
3. **Negative Inventory Prevention** — ATP check interfaces with Dept. 05 (Inventory). If `backorderAllowed = false` on the SKU, the system will not confirm delivery on a date where inventory is insufficient. Reference: CLAUDE.md Rule #1.
4. **Backorder Communication SLA** — Any line that cannot be fulfilled on the confirmed date must be communicated to the customer within 2 business hours of the constraint being identified, with a revised ATP date.
5. **Perfect Order Criteria** — All four conditions must hold: (1) On-Time, (2) In-Full, (3) Damage-Free (from Dept. 06 QC at despatch), (4) Invoice Accurate (no quantity or price discrepancy vs. the delivered order).
6. **Soft-Delete Only** — Sales orders, order lines, and fulfilment records are never hard-deleted (`isDeleted: boolean`). Required for OTIF audit trails and customer dispute resolution.
7. **EDI Acknowledgement Within 2 Hours** — ORDRSP (order acknowledgement) must be sent to the customer within 2 hours of receiving an EDI ORDERS message, per standard trading partner agreements.

---

## 4. Mathematical Models

### 4.1 OTIF — On-Time In-Full

```
isOnTime   = (actualDeliveryDate ≤ confirmedDeliveryDate)
isInFull   = ∀ line_i: deliveredQty_i ≥ orderedQty_i
isOTIF     = isOnTime AND isInFull

OTIF%      = (Count of OTIF orders / Total delivered orders) × 100

Walmart standard: ≥ 98 %
Penalty trigger:  < 98 % → supplier financial penalty (Walmart OTIF Policy 2018)
```

### 4.2 Perfect Order Rate (POR)

```
POR = OTD%  ×  InFull%  ×  DamageFree%  ×  InvoiceAccurate%

Numerical example:
  OTD%             = 97.5 %
  InFull%          = 99.0 %
  DamageFree%      = 99.5 %
  InvoiceAccurate% = 99.0 %
  POR              = 0.975 × 0.990 × 0.995 × 0.990 = 95.1 %

World-class target: POR ≥ 95 %
Ref: Chopra & Meindl, Supply Chain Management 6th Ed., Ch. 3
```

### 4.2b Order Entry Accuracy (SCOR-DS RL.2.3 — leading indicator)

```
Order Entry Accuracy% = (Orders entered without post-entry amendment / Total orders entered) × 100

Standard: ASCM/APICS SCOR Digital Standard — Documentation Accuracy (RL.2.3),
          a mandatory component of Perfect Order Fulfillment (RL.1.1):

  Perfect Order Fulfillment% = (Total Perfect Orders / Total Orders) × 100
  Order is "perfect" only if ALL four Level-2 components = 1:
    RL.2.1 % Orders Delivered In Full
    RL.2.2 Delivery Performance to Customer Commit Date
    RL.2.3 Documentation Accuracy  ← order entry operationalises this at capture
    RL.2.4 Perfect Condition

Channel targets: EDI ≥ 99.5 % | Portal ≥ 98.0 % | Manual (CSR) ≥ 96.0 %
Ref: ASCM SCOR Digital Standard (2020); APICS Dictionary 16th Ed. — "Perfect Order"
```

Full implementation (SQL, T_entry companion, alert thresholds): see `IMPLEMENTATION.md` §10.9.

### 4.3 ATP — Available to Promise

```
ATP_t = On_hand_inventory_t
      + Σ Supply_receipts_{t..T}           (confirmed POs, production orders)
      − Σ Committed_demand_{t..T}          (confirmed but not yet shipped orders)
      − Safety_stock_reserve               (min level from Dept. 05)

Promise rule: Confirm delivery in period t only if ATP_t ≥ order_quantity_requested

Cumulative ATP (CATP) is used for multi-period promising:
  CATP_t = CATP_{t-1} + Supply_receipts_t − Confirmed_demand_t
```

Reference: APICS CPIM 9.0 — Master Scheduling and ATP.

### 4.4 Order Fill Rate

```
Fill_Rate% = (Units_shipped_complete_on_first_attempt / Units_ordered) × 100

Note: Fill Rate measures quantity completeness only (not timing).
      OTIF measures both timing AND quantity.
      Both KPIs are required; neither substitutes for the other.

Line Fill Rate: (Order lines shipped complete / Total order lines) × 100
```

### 4.5 Order Cycle Time (OCT)

```
OCT = Timestamp_shipment_departure − Timestamp_order_receipt   (hours)

Components:
  Order processing time   (validation + ATP + ORDRSP)
  Warehouse pick time     (from Dept. 06 WMS pick-to-pack)
  Packing & labelling     (GS1 SSCC, carrier label)
  Carrier collection      (despatch to departure)

Benchmarks:
  B2B standard goods: 24–48 hours
  B2C e-commerce    : same-day to next-day
```

### 4.6 Backorder Ratio

```
Backorder_Rate% = (Order lines in backorder / Total order lines) × 100

> 2 %  → triggers safety stock review in Dept. 03 (Demand Planning)
> 5 %  → escalation to S&OP (Dept. 12) Supply Review
> 10 % → executive escalation; emergency supply actions
```

---

## 5. Recommended ML Models

### 5.1 XGBoost — OTIF Risk Prediction at Order Entry

Predicts which orders are at risk of missing OTIF at the moment of order entry, before any fulfilment actions are taken. Early identification enables proactive reallocation, expediting, or customer communication.

| Feature | Source |
|---|---|
| Customer delivery location | Customer Master |
| SKU inventory level vs. ATP | Dept. 05 Inventory |
| Carrier on-time history (route) | Dept. 07 Logistics |
| Requested date vs. ATP date gap | `SalesOrder.atpDate` |
| Historical OTIF by customer-SKU-carrier | `SalesOrder` history |

- **Output**: `P(OTIF_fail)` ∈ [0, 1]; threshold 0.25 → proactive alert to customer service
- **Libraries**: XGBoost, `scikit-learn` pipeline
- **Accuracy target**: AUC-ROC > 0.85 on held-out test set

### 5.2 Deep Learning — Dynamic ATP Across Multi-Warehouse Network

Neural network learns complex ATP availability rules across multi-warehouse, multi-product, multi-channel scenarios with allocation priority rules (key accounts, contract customers, spot orders). Replaces the static ATP formula when supply is severely constrained or when allocation optimisation is required.

- **Libraries**: TensorFlow / Keras; served as REST microservice for real-time ATP queries
- **Latency target**: < 100 ms per ATP query

### 5.3 K-Means Clustering — Customer Segmentation for Differentiated Service Levels

Groups customers by order behaviour: order frequency, average order value, OTIF sensitivity (penalty clauses), payment reliability (DSO from Dept. 11). Enables tiered SLA policies: Tier-1 (key accounts) → dedicated ATP reservation; Tier-2 → standard ATP; Tier-3 → best-effort.

- **Libraries**: `scikit-learn KMeans`; `silhouette_score` for optimal k selection
- **Output**: Customer tier assignment stored in `CustomerMaster.serviceTier`

### 5.4 NLP — Automated EDI Order Processing

Parses UN/EDIFACT ORDERS messages from multiple trading partners, extracts all mandatory and conditional fields (BGMLIN, DTM, QTY, PRI, NAD segments), validates against business rules, and auto-creates `SalesOrder` records. Handles format variations and version differences across trading partners without manual mapping.

- **Libraries**: `pydifact` (Python EDIFACT parser), spaCy for unstructured order emails
- **Automation target**: > 95 % of EDI ORDERS processed without human touch

### 5.5 Reinforcement Learning — Order Promising Under Scarcity

RL agent learns the optimal ATP promising strategy when inventory is scarce and multiple customers are competing for the same stock. Balances: maximise total fulfilled revenue vs. avoid over-promising vs. protect key account OTIF commitments.

```
State  : (available_stock_by_SKU, pending_order_queue, demand_forecast_horizon)
Action : (accept_order_at_date_t, defer_to_date_t+k, partial_fill, decline)
Reward : fulfilled_revenue − penalty_for_OTIF_fail − cost_of_customer_churn
```

- **Libraries**: Ray RLlib; OpenAI Gym-compatible SC simulation environment

---

## 6. KPIs & Benchmarks

| KPI | Formula | World-Class Target | Alert |
|---|---|---|---|
| **OTIF %** | `OTIF orders / Total orders × 100` | ≥ 98 % (Walmart standard) | < 95 % |
| **Perfect Order Rate** | `OTD% × InFull% × DamageFree% × InvoiceAcc%` | ≥ 95 % | < 90 % |
| **Order Fill Rate** | `Units shipped complete / Units ordered × 100` | ≥ 99 % | < 97 % |
| **Order Entry Accuracy** (SCOR RL.2.3) | `Orders entered without amendment / Total entered × 100` | ≥ 99.5 % (EDI) | < 99 % |
| **Order Cycle Time** | `Shipment departure − Order receipt` | ≤ 48 h (B2B) | > 72 h |
| **Backorder Rate** | `Backorder lines / Total lines × 100` | < 2 % | > 5 % |
| **ATP Accuracy** | `Deliveries on ATP-promised date / Total × 100` | ≥ 97 % | < 93 % |
| **CSAT (post-delivery)** | Customer satisfaction survey | ≥ 90 % | < 80 % |
| **First Contact Resolution** | `Issues resolved on first contact / Total × 100` | ≥ 80 % | < 70 % |
| **Claim Resolution Time** | `Mean(claim_close_date − claim_open_date)` | < 5 business days | > 10 days |

---

## 7. EDI Message Standards

| UN/EDIFACT Message | Direction | Function |
|---|---|---|
| **ORDERS** | Customer → Us | Customer purchase order |
| **ORDRSP** | Us → Customer | Order acknowledgement / modification |
| **DESADV** | Us → Customer | Advance Ship Notice (ASN) |
| **RECADV** | Customer → Us | Receipt advice (goods received confirmation) |
| **INVOIC** | Us → Customer | Commercial invoice |
| **REMADV** | Customer → Us | Remittance advice (payment notification) |

All messages validated against UN/EDIFACT D.96A syntax. GS1 GLN (Global Location Number) used for all party identification. SSCC (Serial Shipping Container Code) on all despatch units.

---

## 8. Integration Points

| Department | Data Flow |
|---|---|
| **05 Inventory** | ATP queries against real-time stock positions; backorder flag triggers safety stock review |
| **06 Warehouse** | Pick list released to WMS on order allocation; packing confirmation triggers ASN |
| **07 Logistics** | Carrier booking triggered at despatch; tracking number linked to `SalesOrder` |
| **08 Quality** | Damage-free flag at despatch comes from QC sign-off in WMS |
| **11 Finance** | Delivered orders trigger invoice creation; 3-way match on SO ↔ ASN ↔ POD |
| **12 S&OP** | OTIF and backorder KPIs feed Step 1 (Data Review) of monthly S&OP cycle |

---

## 9. Roles

| Role | Responsibility |
|---|---|
| **Order Management Manager** | O2C strategy, OTIF governance, trading partner SLA management |
| **Customer Service Representative** | Direct customer contact; backorder communication; claim handling |
| **Order Analyst** | Order validation, ATP review, exception management |
| **Backorder Coordinator** | Tracks all open backorders; communicates revised ATP dates to customers |
| **EDI Specialist** | Trading partner EDI onboarding; message mapping; error resolution |

---

## 10. References

1. Chopra, S. & Meindl, P., **Supply Chain Management** 6th Ed., Ch. 3 "Customer Value in Supply Chains," Pearson, 2016.
2. APICS / ASCM, **CPIM 9.0 Exam Content Manual** — Order Management and Customer Service, 2024.
3. GS1, **GS1 General Specifications v23.0** — SSCC, GLN, GTIN, DESADV mapping, 2023.
4. Walmart Inc., **OTIF Supplier Guide and Penalty Policy**, 2018 (updated annually at supplier.walmart.com).
5. UN/CEFACT, **UN/EDIFACT Message Implementation Guides** — ORDERS, ORDRSP, DESADV, INVOIC (D.96A), United Nations, Geneva.
