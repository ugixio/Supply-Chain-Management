# Order Management & Customer Service (Order-to-Cash)
## Enterprise Implementation Guide — Department 13

**Classification**: Internal — Senior Consultant Grade  
**Standard Alignment**: SCOR-DS v4.0, UN/EDIFACT, ISO 9001:2015, Incoterms 2020  
**Revision**: 1.0  
**Date**: 2026-06-20  

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

Order Management & Customer Service (OM/CS) constitutes the commercial nerve centre of any enterprise supply chain, spanning the full Order-to-Cash (O2C) cycle from customer order capture through delivery confirmation, invoicing, and cash application. Misalignment in this domain directly translates to revenue leakage, working capital erosion, and customer attrition — the three most consequential operational risks in B2B commerce.

This implementation guide provides a structured, phased approach to deploying an enterprise-grade Order Management capability aligned with the SCOR Digital Standard process model (PLAN → SOURCE → MAKE → DELIVER → RETURN → ENABLE), with particular emphasis on the DELIVER macro-process (D1: Stocked Product, D2: Make-to-Order, D3: Engineer-to-Order) and the agility metrics defined under SCOR AG.1.1–1.3.

### Strategic Objectives

The programme targets the following business outcomes over an 18-month horizon:

- Reduce Order Fulfillment Cycle Time (OFCT, SCOR RS.1.1) by 30–40% versus current baseline through ATP/CTP automation and exception-based order management.
- Achieve Perfect Order Index (POI) >= 95% at the enterprise level, disaggregated by customer segment, channel, and product family.
- Compress Days Sales Outstanding (DSO) by 8–12 days through automated invoice generation, dispute routing, and cash application.
- Reduce manual order-entry labour by 60–70% via EDI/API channel automation and intelligent document processing.
- Implement real-time OTIF dashboards meeting Walmart (98%), Target (98.5%), and Amazon (97%) vendor compliance standards.

### Scope Boundary

This guide covers the bounded context of Department 13. Adjacent bounded contexts — Inventory (Dept 02), Procurement (Dept 01), Logistics (Dept 08), Warehouse (Dept 10), Finance/AR — are treated as integration points only and governed by their own implementation guides.

---

## 2. Prerequisites & Dependencies

### 2.1 Upstream Domain Dependencies

Before initiating Phase 1, the following domains must be operational and API-accessible:

| Domain | Department | Required Capability | Integration Contract |
|--------|-----------|---------------------|---------------------|
| Inventory | Dept 02 | Real-time ATP stock query | `GET /inventory/atp/{sku}/{warehouse}` |
| Procurement | Dept 01 | Open PO visibility for CTP | `GET /procurement/po/open` |
| Logistics | Dept 08 | Carrier rate + transit time | `POST /logistics/rate-query` |
| Warehouse | Dept 10 | Pick-pack-ship slot reservation | `POST /warehouse/reservation` |
| Supplier Mgmt | Dept 06 | Supplier lead time actuals | `GET /suppliers/{id}/lead-times` |
| Demand Planning | Dept 05 | Demand signal per SKU | `GET /demand/forecast/{sku}` |

### 2.2 Master Data Prerequisites

The following master data must be cleansed, deduplicated, and loaded before go-live:

- **Customer Master**: Legal entity, billing address, shipping addresses, credit limit, payment terms, currency, tax classification, EDI capability flag, customer tier (A/B/C).
- **Product Master**: SKU, UOM (GS1), lead time, ATP-eligible flag, CTP-eligible flag, lot-tracked flag, hazmat class.
- **Price Book**: List price, customer-specific contract price, volume break thresholds, validity dates.
- **Carrier Master**: Service levels (standard/express/freight), transit time matrices, carrier SCAC codes.
- **Warehouse Master**: GLN per site, storage type, cut-off times by carrier.

### 2.3 Technical Prerequisites

- Event Store (CQRS pattern) operational — all order state transitions must emit domain events.
- Message broker (Apache Kafka, Apache-2.0) available for cross-domain event streaming.
- API Gateway with OAuth 2.0 / mTLS for customer portal and EDI partner connections.
- Idempotency framework in place — order capture must be safe to retry without duplication.

---

## 3. Phase 0: Assessment & AS-IS Analysis

**Duration**: Weeks 1–4  
**Owner**: Programme Management Office + Business Analyst lead

### 3.1 Current-State Mapping

Conduct structured interviews and process observation sessions (Gemba walks) across:

- Customer Service Representatives (CSR): order entry channels, exception handling, escalation paths.
- Order Management team: approval thresholds, credit hold procedures, manual intervention points.
- Warehouse operations: cut-off times, special handling exceptions.
- Finance/AR: invoice dispute categories, DSO root-cause distribution.

Produce a BPMN 2.0 process map of the current O2C flow. Identify all manual handoffs, re-keying steps, and spreadsheet-based workarounds — these constitute the primary automation target list.

### 3.2 Data Quality Baseline

Execute a data quality assessment across:

```
- Customer master duplicate rate (target: < 0.5%)
- Address validation pass rate (target: > 98%)
- SKU/UOM consistency across channels (target: 100%)
- Historical order data completeness for ML training (minimum 24 months)
- OTIF actuals availability at line-item level (required for POI calculation)
```

### 3.3 Key Metrics Baseline

Establish current-state KPI baselines across all metrics listed in Section 12. Document measurement methodology for each. Gaps in measurement capability are first-order remediation items.

### 3.4 Gap Analysis Output

Produce a prioritised gap register with three columns: (1) Gap description, (2) Business impact (High/Medium/Low), (3) Recommended resolution. This register drives Phase 1 and Phase 2 backlog prioritisation.

---

## 4. Phase 1: Foundation & Master Data

**Duration**: Weeks 5–10  
**Owner**: Data Engineering + Business Analysis

### 4.1 Customer Master Data Model

```typescript
// src/departments/13-order-management/domain/Customer.ts

import { Money, ISOTimestamp, ISODate } from '../../../shared/types';

export type CustomerTier = 'TIER_A' | 'TIER_B' | 'TIER_C';
export type PaymentTermsCode = 'NET_30' | 'NET_60' | 'NET_90' | '2_10_NET_30' | 'PREPAID';
export type CustomerStatus = 'ACTIVE' | 'CREDIT_HOLD' | 'INACTIVE' | 'PROSPECT';

export interface CustomerAddress {
  readonly addressId: string;
  readonly type: 'BILLING' | 'SHIPPING' | 'BOTH';
  readonly street1: string;
  readonly street2?: string;
  readonly city: string;
  readonly stateProvince: string;
  readonly postalCode: string;
  readonly countryCode: string; // ISO 3166-1 alpha-2
  readonly gln?: string;        // GS1 Global Location Number
  readonly isDefault: boolean;
}

export interface PriceContractLine {
  readonly skuId: string;
  readonly contractPriceCents: number; // integer cents
  readonly validFrom: ISODate;
  readonly validTo: ISODate;
  readonly minimumQuantity: number;
  readonly uom: string;
}

export interface Customer {
  readonly customerId: string;
  readonly legalName: string;
  readonly tradingName?: string;
  readonly tier: CustomerTier;
  readonly status: CustomerStatus;
  readonly creditLimitCents: number;       // integer cents
  readonly currentExposureCents: number;   // open AR + unshipped orders
  readonly paymentTerms: PaymentTermsCode;
  readonly currencyCode: string;           // ISO 4217
  readonly taxId?: string;
  readonly ediPartnerId?: string;
  readonly addresses: readonly CustomerAddress[];
  readonly priceContracts: readonly PriceContractLine[];
  readonly createdAt: ISOTimestamp;
  readonly updatedAt: ISOTimestamp;
  readonly isDeleted: boolean;
}
```

### 4.2 Sales Order Aggregate

```typescript
// src/departments/13-order-management/domain/SalesOrder.ts

import { Money, ISOTimestamp, ISODate } from '../../../shared/types';

export type OrderChannel = 'EDI' | 'API' | 'PORTAL' | 'MANUAL' | 'SHOPIFY' | 'MAGENTO' | 'SALESFORCE';
export type OrderStatus =
  | 'DRAFT'
  | 'CREDIT_CHECK_PENDING'
  | 'CREDIT_HOLD'
  | 'CONFIRMED'
  | 'ATP_COMMITTED'
  | 'IN_PICKING'
  | 'SHIPPED'
  | 'INVOICED'
  | 'PAID'
  | 'CANCELLED'
  | 'DISPUTED';

export type FulfillmentType = 'D1_STOCKED' | 'D2_MTO' | 'D3_ETO';

export interface OrderLine {
  readonly lineId: string;
  readonly skuId: string;
  readonly orderedQty: number;
  readonly confirmedQty: number;  // set by ATP/CTP engine
  readonly uom: string;
  readonly unitPriceCents: number;    // integer cents — determined by price engine
  readonly requestedDeliveryDate: ISODate;
  readonly committedDeliveryDate?: ISODate;  // set by ATP/CTP
  readonly fulfillmentType: FulfillmentType;
  readonly warehouseId?: string;
  readonly lotNumber?: string;
  readonly shipmentLineId?: string;
  readonly isDeleted: boolean;
}

export interface SalesOrder {
  readonly orderId: string;
  readonly orderNumber: string;     // human-readable, sequential
  readonly customerId: string;
  readonly channel: OrderChannel;
  readonly status: OrderStatus;
  readonly lines: readonly OrderLine[];
  readonly totalAmountCents: number;
  readonly currencyCode: string;
  readonly requestedDeliveryDate: ISODate;
  readonly shipToAddressId: string;
  readonly billToAddressId: string;
  readonly incoterm: string;        // from INCOTERMS_2020 constant
  readonly purchaseOrderRef?: string;  // customer's PO number
  readonly ediMessageRef?: string;
  readonly idempotencyKey: string;
  readonly creditCheckPassed?: boolean;
  readonly createdAt: ISOTimestamp;
  readonly updatedAt: ISOTimestamp;
  readonly isDeleted: boolean;
}
```

### 4.3 Event Schema

All state transitions emit domain events to the Event Store:

```typescript
export type OrderEventType =
  | 'ORDER_CREATED'
  | 'ORDER_CREDIT_CHECKED'
  | 'ORDER_CREDIT_HELD'
  | 'ORDER_CONFIRMED'
  | 'ATP_COMMITTED'
  | 'ORDER_SHIPPED'
  | 'ORDER_INVOICED'
  | 'ORDER_PAID'
  | 'ORDER_CANCELLED'
  | 'ORDER_DISPUTED';

export interface OrderEvent {
  readonly eventId: string;
  readonly eventType: OrderEventType;
  readonly orderId: string;
  readonly occurredAt: ISOTimestamp;
  readonly payload: Record<string, unknown>;
  readonly correlationId: string;
}
```

---

## 5. Phase 2: Process Standardisation & Core Analytics

**Duration**: Weeks 11–18  
**Owner**: Business Process team + Analytics Engineering

### 5.1 O2C Process Standardisation

Define standard operating procedures (SOPs) for each subprocess:

1. **Order Entry** — SLA: < 15 minutes from receipt to system entry for EDI; < 2 hours for manual.
2. **Credit Check** — automated for orders below 80% of available credit; manual review above.
3. **ATP/CTP Confirmation** — SLA: < 5 minutes for standard SKUs; < 4 hours for MTO.
4. **Pick-Pack-Ship** — governed by Warehouse (Dept 10); order management owns the reservation handoff.
5. **Invoice Generation** — automated trigger on `ORDER_SHIPPED` event; SLA: within 2 hours.
6. **Dispute Resolution** — SLA: acknowledgement < 24 hours; resolution < 10 business days.
7. **Cash Application** — automated for EDI 820/REMADV; manual for unmatched payments.

### 5.2 Exception Management Framework

Define exception categories and escalation paths:

| Exception Type | Auto-Resolve Eligible | Escalation SLA | Owner |
|---------------|----------------------|----------------|-------|
| Credit hold — within tolerance | No | 4 hours | Credit Manager |
| ATP shortfall < 10% | Yes — partial ship | Immediate | System |
| ATP shortfall > 10% | No | 2 hours | Order Manager |
| Carrier cut-off miss | Partial | 1 hour | Logistics |
| Price discrepancy | No | 24 hours | Commercial |
| Duplicate order (idempotency) | Yes — suppress | Immediate | System |

### 5.3 OTIF Dashboard Architecture

The OTIF pipeline aggregates events from four domains: Order Management, Warehouse, Logistics, and Finance. Each domain publishes events to Kafka topics; a stream processor (Apache Flink, Apache-2.0) computes OTIF at shipment-line granularity and rolls up to order, customer, and period levels.

---

## 6. Phase 3: Mathematical Models

**Duration**: Weeks 11–22 (runs parallel to Phase 2)  
**Owner**: Supply Chain Analytics team  

---

### 6.1 ATP — Available-to-Promise

ATP answers the question: "Can I promise this customer this quantity of this SKU for delivery by this date, given what is currently uncommitted in stock?"

**Algorithm**:

```
ATP(sku, date) = On-Hand Inventory
              + Confirmed Inbound (POs + production orders due before date)
              - All existing committed demand due before date
              - Safety stock buffer (configurable by SKU policy)
```

The key distinction: ATP operates on *committed* demand only — confirmed orders already in the system. It does not consume safety stock unless the policy flag `allowSafetyStockPromising` is true.

```typescript
// src/departments/13-order-management/algorithms/ATP.ts

export interface ATPInput {
  skuId: string;
  warehouseId: string;
  requestedQty: number;
  requestedDeliveryDate: string; // ISO date
}

export interface ATPResult {
  available: boolean;
  confirmableQty: number;
  earliestAvailableDate: string;
  onHandQty: number;
  committedQty: number;
  inboundQty: number;
  safetyStockBuffer: number;
}

export function calculateATP(
  input: ATPInput,
  onHand: number,
  committedDemand: number,
  scheduledInbound: number,
  safetyStockBuffer: number
): ATPResult {
  const uncommitted = onHand + scheduledInbound - committedDemand - safetyStockBuffer;
  const confirmableQty = Math.max(0, Math.min(uncommitted, input.requestedQty));

  return {
    available: confirmableQty >= input.requestedQty,
    confirmableQty,
    earliestAvailableDate: input.requestedDeliveryDate, // simplified; production uses horizon scan
    onHandQty: onHand,
    committedQty: committedDemand,
    inboundQty: scheduledInbound,
    safetyStockBuffer,
  };
}
```

**Horizon Scan**: When insufficient stock is available for the requested date, the system scans forward up to `ATP_HORIZON_DAYS` (default: 90) to find the earliest date when `uncommitted >= requestedQty`, incorporating scheduled inbound receipts from open POs.

---

### 6.2 CTP — Capable-to-Promise

CTP extends ATP for Make-to-Order (D2) and Engineer-to-Order (D3) fulfillment types. Instead of checking on-hand stock, it checks production capacity.

**Algorithm**:

```
CTP(sku, qty, date) =
  Step 1: Determine raw material availability (via ATP on components)
  Step 2: Check open production capacity in the required time window
  Step 3: Calculate earliest completion date = max(RM_ready_date, capacity_slot_date) + production_lead_time
  Step 4: Add outbound transit time from production site to customer
  Step 5: If completion_date + transit <= requested_date → CTP = YES
```

```python
# python/13_order_management/ctp_engine.py

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional


@dataclass
class CTPInput:
    sku_id: str
    quantity: float
    requested_delivery_date: date
    customer_ship_to_country: str


@dataclass
class CTPResult:
    feasible: bool
    earliest_delivery_date: Optional[date]
    raw_material_ready_date: Optional[date]
    production_completion_date: Optional[date]
    capacity_bottleneck: Optional[str]
    transit_days: int


def calculate_ctp(
    input_data: CTPInput,
    rm_atp_date: date,           # earliest date all raw materials are available
    capacity_available_date: date,  # earliest production slot start
    production_lead_days: int,
    transit_days: int,
) -> CTPResult:
    """
    Determine CTP feasibility for a Make-to-Order fulfillment.

    Parameters
    ----------
    input_data : CTPInput
        Order line requirements.
    rm_atp_date : date
        Earliest date all BOM components pass ATP check.
    capacity_available_date : date
        Earliest production capacity slot for this SKU/routing.
    production_lead_days : int
        Calendar days from production start to completion.
    transit_days : int
        Transit days from production site to customer (from carrier matrix).

    Returns
    -------
    CTPResult
        Feasibility flag and date decomposition.
    """
    production_start = max(rm_atp_date, capacity_available_date)
    production_complete = production_start + timedelta(days=production_lead_days)
    delivery_date = production_complete + timedelta(days=transit_days)
    feasible = delivery_date <= input_data.requested_delivery_date

    return CTPResult(
        feasible=feasible,
        earliest_delivery_date=delivery_date,
        raw_material_ready_date=rm_atp_date,
        production_completion_date=production_complete,
        capacity_bottleneck=None if feasible else "CAPACITY" if capacity_available_date > rm_atp_date else "RAW_MATERIAL",
        transit_days=transit_days,
    )
```

---

### 6.3 Perfect Order Index (POI)

The Perfect Order Index is the single most comprehensive measure of order fulfillment quality. It is computed as the product of four binary compliance dimensions at the order-line level, then aggregated.

**Formula**:

```
POI = (On-Time %) × (In-Full %) × (Damage-Free %) × (Correct-Docs %)
```

Each factor is binary per order line (1 = compliant, 0 = non-compliant), then averaged across the period.

```python
# python/13_order_management/perfect_order_index.py

import pandas as pd
import numpy as np
from typing import Tuple


def calculate_poi(orders_df: pd.DataFrame) -> Tuple[float, pd.DataFrame]:
    """
    Calculate Perfect Order Index and factor decomposition.

    Expected columns in orders_df:
    - order_line_id: str
    - on_time: bool (actual delivery <= committed_delivery_date)
    - in_full: bool (delivered_qty / ordered_qty >= fill_rate_threshold)
    - damage_free: bool (no damage claim filed within 5 business days)
    - correct_docs: bool (invoice, packing list, CoA match — zero discrepancies)
    - order_value_cents: int (for weighted POI)
    - customer_tier: str (A/B/C for segmentation)
    """
    required_cols = {"order_line_id", "on_time", "in_full", "damage_free", "correct_docs"}
    missing = required_cols - set(orders_df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    df = orders_df.copy()

    # Each dimension as float for aggregation
    for col in ["on_time", "in_full", "damage_free", "correct_docs"]:
        df[col] = df[col].astype(float)

    # Line-level perfect order flag
    df["perfect_order"] = (
        df["on_time"] * df["in_full"] * df["damage_free"] * df["correct_docs"]
    )

    # Aggregate metrics
    summary = {
        "poi": df["perfect_order"].mean(),
        "on_time_pct": df["on_time"].mean(),
        "in_full_pct": df["in_full"].mean(),
        "damage_free_pct": df["damage_free"].mean(),
        "correct_docs_pct": df["correct_docs"].mean(),
        "total_lines": len(df),
        "perfect_lines": int(df["perfect_order"].sum()),
    }

    # Segment by customer tier if available
    if "customer_tier" in df.columns:
        tier_breakdown = df.groupby("customer_tier")["perfect_order"].mean().reset_index()
        tier_breakdown.columns = ["customer_tier", "poi"]
    else:
        tier_breakdown = pd.DataFrame()

    return summary["poi"], pd.DataFrame([summary])
```

**World-class benchmarks**:  
- FMCG/CPG: POI >= 95%  
- Automotive (Tier-1 OEM): POI >= 98.5%  
- Pharma (GDP-compliant): POI >= 99%  

---

### 6.4 OTIF Calculation Pipeline

OTIF (On-Time In-Full) is a vendor compliance standard. Unlike POI, it is typically measured at shipment level (not line level) and uses the *retailer's* definition of the delivery window.

```python
# python/13_order_management/otif_pipeline.py

import pandas as pd
from datetime import date


def calculate_otif(
    shipments_df: pd.DataFrame,
    fill_rate_threshold: float = 1.0,  # Walmart: 100% of ordered qty
) -> pd.DataFrame:
    """
    Calculate OTIF at shipment and customer level.

    Columns required in shipments_df:
    - shipment_id, customer_id, customer_name, retailer_standard (str)
    - ordered_qty, delivered_qty (numeric)
    - required_delivery_date (date), actual_delivery_date (date)
    """
    df = shipments_df.copy()
    df["on_time"] = df["actual_delivery_date"] <= df["required_delivery_date"]
    df["in_full"] = (df["delivered_qty"] / df["ordered_qty"]) >= fill_rate_threshold
    df["otif"] = df["on_time"] & df["in_full"]

    summary = df.groupby(["customer_id", "customer_name"]).agg(
        total_shipments=("shipment_id", "count"),
        on_time_count=("on_time", "sum"),
        in_full_count=("in_full", "sum"),
        otif_count=("otif", "sum"),
    ).reset_index()

    summary["on_time_pct"] = summary["on_time_count"] / summary["total_shipments"]
    summary["in_full_pct"] = summary["in_full_count"] / summary["total_shipments"]
    summary["otif_pct"] = summary["otif_count"] / summary["total_shipments"]

    return summary
```

**Retailer OTIF thresholds**:

| Retailer | OTIF Target | Penalty Threshold | Charge |
|----------|------------|-------------------|--------|
| Walmart | 98% | < 98% | 3% of invoice value |
| Target | 98.5% | < 95% | 5% of invoice value |
| Amazon Vendor | 97% | < 90% | Non-compliance letter |
| Kroger | 96% | < 93% | 2.5% of invoice value |

---

### 6.5 Order-to-Cash Cycle Time Decomposition

O2C cycle time is the elapsed time from `ORDER_CREATED` to `PAYMENT_RECEIVED`. Decompose into sub-intervals using event timestamps:

```
O2C Total = T_entry + T_credit + T_atp + T_pick + T_transit + T_invoice + T_collection
```

Where:
- `T_entry` = ORDER_CREATED → ORDER_CONFIRMED (entry and validation lag)
- `T_credit` = ORDER_CONFIRMED → CREDIT_CHECK_PASSED (credit processing time)
- `T_atp` = CREDIT_CHECK_PASSED → ATP_COMMITTED (availability confirmation)
- `T_pick` = ATP_COMMITTED → ORDER_SHIPPED (warehouse processing)
- `T_transit` = ORDER_SHIPPED → DELIVERY_CONFIRMED (carrier transit)
- `T_invoice` = DELIVERY_CONFIRMED → INVOICE_SENT (billing lag)
- `T_collection` = INVOICE_SENT → PAYMENT_RECEIVED (DSO component)

```python
# python/13_order_management/o2c_cycle_time.py

import pandas as pd
from typing import Dict


EVENT_SEQUENCE = [
    "ORDER_CREATED",
    "ORDER_CONFIRMED",
    "CREDIT_CHECK_PASSED",
    "ATP_COMMITTED",
    "ORDER_SHIPPED",
    "DELIVERY_CONFIRMED",
    "INVOICE_SENT",
    "PAYMENT_RECEIVED",
]

INTERVAL_LABELS = {
    ("ORDER_CREATED", "ORDER_CONFIRMED"): "T_entry",
    ("ORDER_CONFIRMED", "CREDIT_CHECK_PASSED"): "T_credit",
    ("CREDIT_CHECK_PASSED", "ATP_COMMITTED"): "T_atp",
    ("ATP_COMMITTED", "ORDER_SHIPPED"): "T_pick",
    ("ORDER_SHIPPED", "DELIVERY_CONFIRMED"): "T_transit",
    ("DELIVERY_CONFIRMED", "INVOICE_SENT"): "T_invoice",
    ("INVOICE_SENT", "PAYMENT_RECEIVED"): "T_collection",
}


def decompose_o2c(events_df: pd.DataFrame) -> pd.DataFrame:
    """
    Pivot order events to compute per-interval cycle times in hours.

    events_df columns: order_id, event_type, occurred_at (datetime, UTC)
    """
    pivoted = events_df.pivot_table(
        index="order_id",
        columns="event_type",
        values="occurred_at",
        aggfunc="first",
    )

    for (start, end), label in INTERVAL_LABELS.items():
        if start in pivoted.columns and end in pivoted.columns:
            pivoted[label] = (
                pivoted[end] - pivoted[start]
            ).dt.total_seconds() / 3600  # hours

    interval_cols = list(INTERVAL_LABELS.values())
    existing = [c for c in interval_cols if c in pivoted.columns]
    pivoted["T_total_o2c"] = pivoted[existing].sum(axis=1)

    return pivoted[existing + ["T_total_o2c"]].reset_index()
```

---

### 6.6 Credit Limit Check Algorithm

The credit check must execute in < 200ms to avoid blocking order confirmation. It computes *current exposure* as the sum of all open AR (unpaid invoices) plus the value of all open orders not yet invoiced.

```typescript
// src/departments/13-order-management/algorithms/CreditCheck.ts

export interface CreditCheckInput {
  customerId: string;
  newOrderValueCents: number;
  creditLimitCents: number;
  openARCents: number;           // sum of unpaid invoices
  openOrderValueCents: number;   // confirmed orders not yet invoiced
  overdueARCents: number;        // AR past due date
  gracePeriodDays: number;       // configurable per customer tier
}

export type CreditDecision = 'APPROVED' | 'APPROVED_WITH_WARNING' | 'HOLD' | 'BLOCKED';

export interface CreditCheckResult {
  decision: CreditDecision;
  currentExposureCents: number;
  exposureAfterOrderCents: number;
  utilizationPct: number;
  reason?: string;
  requiresManualReview: boolean;
}

export function checkCredit(input: CreditCheckInput): CreditCheckResult {
  const currentExposure = input.openARCents + input.openOrderValueCents;
  const exposureAfterOrder = currentExposure + input.newOrderValueCents;
  const utilizationPct = (exposureAfterOrder / input.creditLimitCents) * 100;

  // Overdue AR is a hard block regardless of limit headroom
  if (input.overdueARCents > 0) {
    return {
      decision: 'BLOCKED',
      currentExposureCents: currentExposure,
      exposureAfterOrderCents: exposureAfterOrder,
      utilizationPct,
      reason: `Overdue AR of ${input.overdueARCents} cents outstanding`,
      requiresManualReview: true,
    };
  }

  if (utilizationPct > 100) {
    return {
      decision: 'HOLD',
      currentExposureCents: currentExposure,
      exposureAfterOrderCents: exposureAfterOrder,
      utilizationPct,
      reason: `Credit limit exceeded: ${utilizationPct.toFixed(1)}% utilization`,
      requiresManualReview: true,
    };
  }

  if (utilizationPct > 80) {
    return {
      decision: 'APPROVED_WITH_WARNING',
      currentExposureCents: currentExposure,
      exposureAfterOrderCents: exposureAfterOrder,
      utilizationPct,
      reason: `High credit utilization: ${utilizationPct.toFixed(1)}%`,
      requiresManualReview: false,
    };
  }

  return {
    decision: 'APPROVED',
    currentExposureCents: currentExposure,
    exposureAfterOrderCents: exposureAfterOrder,
    utilizationPct,
    requiresManualReview: false,
  };
}
```

---

### 6.7 Price Determination Engine

The price engine evaluates a customer's applicable price in a deterministic waterfall:

```
Priority 1: Customer-specific contract price (with validity date check)
Priority 2: Customer tier volume discount (break table)
Priority 3: Promotional price (campaign code, date-bound)
Priority 4: List price (standard price book)
```

All prices are stored and returned in integer cents. No floating-point arithmetic.

```typescript
// src/departments/13-order-management/algorithms/PriceDetermination.ts

export interface VolumeTier {
  minQty: number;
  discountPct: number; // e.g. 5 = 5%
}

export interface PriceInput {
  skuId: string;
  customerId: string;
  orderedQty: number;
  requestDate: string;
  listPriceCents: number;
  contractPriceCents?: number;   // null if no contract
  contractValidTo?: string;
  volumeTiers: VolumeTier[];
  promotionalPriceCents?: number;
  promotionValidTo?: string;
}

export interface PriceResult {
  unitPriceCents: number;
  appliedRule: 'CONTRACT' | 'VOLUME_DISCOUNT' | 'PROMOTIONAL' | 'LIST';
  discountPct: number;
  discountCents: number;
}

export function determinePrice(input: PriceInput): PriceResult {
  const today = input.requestDate;

  // Priority 1: Contract price
  if (
    input.contractPriceCents !== undefined &&
    input.contractValidTo !== undefined &&
    input.contractValidTo >= today
  ) {
    const discountCents = input.listPriceCents - input.contractPriceCents;
    return {
      unitPriceCents: input.contractPriceCents,
      appliedRule: 'CONTRACT',
      discountPct: Math.round((discountCents / input.listPriceCents) * 100 * 100) / 100,
      discountCents,
    };
  }

  // Priority 2: Volume discount (highest applicable tier)
  const sortedTiers = [...input.volumeTiers].sort((a, b) => b.minQty - a.minQty);
  const applicableTier = sortedTiers.find((t) => input.orderedQty >= t.minQty);
  if (applicableTier) {
    // Integer arithmetic: round half-up
    const discountCents = Math.round(input.listPriceCents * applicableTier.discountPct / 100);
    return {
      unitPriceCents: input.listPriceCents - discountCents,
      appliedRule: 'VOLUME_DISCOUNT',
      discountPct: applicableTier.discountPct,
      discountCents,
    };
  }

  // Priority 3: Promotional
  if (
    input.promotionalPriceCents !== undefined &&
    input.promotionValidTo !== undefined &&
    input.promotionValidTo >= today
  ) {
    const discountCents = input.listPriceCents - input.promotionalPriceCents;
    return {
      unitPriceCents: input.promotionalPriceCents,
      appliedRule: 'PROMOTIONAL',
      discountPct: Math.round((discountCents / input.listPriceCents) * 100 * 100) / 100,
      discountCents,
    };
  }

  // Priority 4: List price
  return {
    unitPriceCents: input.listPriceCents,
    appliedRule: 'LIST',
    discountPct: 0,
    discountCents: 0,
  };
}
```

---

### 6.8 SCOR RS.1.1 — Order Fulfillment Cycle Time (OFCT)

OFCT measures the time from customer order receipt to customer delivery. Under SCOR-DS, it is defined as:

```
OFCT = Order Entry Time
     + Order Processing Time
     + Transportation Time (from ship date to delivery date)
```

SCOR benchmarks (APQC Open Standards Benchmarking, 2024):

| Percentile | OFCT (days) — B2B Discrete Mfg |
|------------|-------------------------------|
| Top 10% (best) | <= 2.1 |
| Median | 4.8 |
| Bottom 25% | >= 9.2 |

```python
# python/13_order_management/scor_ofct.py

import pandas as pd
import numpy as np


def calculate_ofct(orders_df: pd.DataFrame) -> pd.DataFrame:
    """
    SCOR RS.1.1 Order Fulfillment Cycle Time.

    Required columns:
    - order_id, order_received_at (datetime), delivery_confirmed_at (datetime)
    - channel (str), fulfillment_type (str), customer_tier (str)
    """
    df = orders_df.copy()
    df["ofct_hours"] = (
        df["delivery_confirmed_at"] - df["order_received_at"]
    ).dt.total_seconds() / 3600
    df["ofct_days"] = df["ofct_hours"] / 24

    summary = df.groupby(["channel", "fulfillment_type"])["ofct_days"].agg(
        count="count",
        mean="mean",
        p50=lambda x: np.percentile(x, 50),
        p90=lambda x: np.percentile(x, 90),
        p95=lambda x: np.percentile(x, 95),
    ).reset_index()

    return summary
```

---

### 6.9 SCOR Agility Metrics AG.1.1–AG.1.3

SCOR agility measures the supply chain's ability to respond to marketplace changes:

- **AG.1.1 — Upside Adaptability**: Maximum sustainable percentage increase in delivered quantities achievable within 30 days with no additional cost premium.
- **AG.1.2 — Downside Adaptability**: Maximum sustainable percentage decrease in ordered quantities achievable within 30 days without incurring unplanned costs.
- **AG.1.3 — Overall Value at Risk (VaR)**: Probability-weighted financial exposure from supply chain disruptions.

```python
# python/13_order_management/scor_agility.py

import numpy as np
from scipy import stats
from dataclasses import dataclass
from typing import List


@dataclass
class AgilityMetrics:
    upside_adaptability_pct: float    # AG.1.1
    downside_adaptability_pct: float  # AG.1.2
    value_at_risk_cents: float        # AG.1.3 (95th percentile)
    confidence_level: float


def calculate_agility(
    historical_order_volumes: List[float],
    max_capacity_units: float,
    fixed_cost_per_period_cents: float,
    disruption_probabilities: List[float],
    disruption_impact_cents: List[float],
    confidence_level: float = 0.95,
) -> AgilityMetrics:
    """
    Calculate SCOR AG.1.1, AG.1.2, and AG.1.3 metrics.

    AG.1.1: How much can we scale up within 30 days?
    AG.1.2: How much can we scale down without stranded cost?
    AG.1.3: Value at Risk from disruptions at given confidence level.
    """
    baseline_volume = np.mean(historical_order_volumes[-12:])  # 12-period average

    # AG.1.1: Upside — constrained by max capacity
    upside_max_units = max_capacity_units
    upside_adaptability_pct = (
        (upside_max_units - baseline_volume) / baseline_volume
    ) * 100

    # AG.1.2: Downside — constrained by fixed cost floor (break-even volume)
    # Break-even: below this volume, fixed costs generate a loss
    avg_revenue_per_unit = np.mean(historical_order_volumes)  # simplified
    downside_floor = fixed_cost_per_period_cents / max(avg_revenue_per_unit, 1)
    downside_adaptability_pct = (
        (baseline_volume - downside_floor) / baseline_volume
    ) * 100

    # AG.1.3: VaR — Monte Carlo simulation of disruption scenarios
    n_simulations = 10_000
    rng = np.random.default_rng(seed=42)
    losses = np.zeros(n_simulations)

    for prob, impact in zip(disruption_probabilities, disruption_impact_cents):
        events = rng.binomial(1, prob, n_simulations)
        losses += events * impact

    value_at_risk = np.percentile(losses, confidence_level * 100)

    return AgilityMetrics(
        upside_adaptability_pct=max(0.0, upside_adaptability_pct),
        downside_adaptability_pct=max(0.0, downside_adaptability_pct),
        value_at_risk_cents=value_at_risk,
        confidence_level=confidence_level,
    )
```

---

## 7. Phase 4: ML/AI Pipeline

**Duration**: Weeks 19–32  
**Owner**: Data Science team  
**Governance**: All models require documented accuracy benchmarks, drift monitoring, and human-in-the-loop override for decisions exceeding $50,000 order value.

---

### 7.1 XGBoost — Order Delay Prediction

Predicts probability of delay for each order line before shipment, enabling proactive customer communication and exception prioritisation.

**Features**:

| Feature Group | Features |
|--------------|---------|
| Customer | tier, country, historical OTIF, payment behaviour score |
| Lane | origin warehouse, destination country, carrier SCAC, average historical transit variability |
| Seasonal | day of week, week of year, quarter, proximity to retailer peak periods |
| SKU | ABC class, storage condition, weight/volume, hazmat flag, average pick accuracy |
| Order | channel, total value, line count, number of SKUs on credit watch |
| External | carrier capacity index (if available via API), weather event flag |

```python
# python/13_order_management/ml/order_delay_prediction.py

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import roc_auc_score, precision_recall_curve
from sklearn.preprocessing import LabelEncoder
from typing import Tuple


CATEGORICAL_COLS = [
    "customer_tier", "origin_warehouse", "destination_country",
    "carrier_scac", "sku_abc_class", "order_channel",
]

NUMERIC_COLS = [
    "customer_historical_otif", "lane_transit_variance_days",
    "sku_weight_kg", "order_value_cents", "order_line_count",
    "week_of_year", "day_of_week",
]


def prepare_features(df: pd.DataFrame) -> pd.DataFrame:
    """Encode categoricals and return feature matrix."""
    result = df.copy()
    for col in CATEGORICAL_COLS:
        if col in result.columns:
            le = LabelEncoder()
            result[col] = le.fit_transform(result[col].astype(str))
    return result[CATEGORICAL_COLS + NUMERIC_COLS]


def train_delay_model(
    train_df: pd.DataFrame,
    label_col: str = "delayed",
    n_splits: int = 5,
) -> Tuple[xgb.XGBClassifier, dict]:
    """
    Train XGBoost classifier for order delay prediction.

    Uses TimeSeriesSplit to prevent data leakage.
    Target: binary (1 = delayed, 0 = on-time).
    """
    X = prepare_features(train_df)
    y = train_df[label_col].astype(int)

    tscv = TimeSeriesSplit(n_splits=n_splits)
    auc_scores = []

    model = xgb.XGBClassifier(
        n_estimators=500,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=(y == 0).sum() / (y == 1).sum(),  # class imbalance
        eval_metric="auc",
        early_stopping_rounds=50,
        random_state=42,
        n_jobs=-1,
    )

    for fold, (train_idx, val_idx) in enumerate(tscv.split(X)):
        X_tr, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_tr, y_val = y.iloc[train_idx], y.iloc[val_idx]

        model.fit(
            X_tr, y_tr,
            eval_set=[(X_val, y_val)],
            verbose=False,
        )
        preds = model.predict_proba(X_val)[:, 1]
        auc_scores.append(roc_auc_score(y_val, preds))

    metrics = {
        "mean_auc": float(np.mean(auc_scores)),
        "std_auc": float(np.std(auc_scores)),
        "feature_importance": dict(zip(
            CATEGORICAL_COLS + NUMERIC_COLS,
            model.feature_importances_.tolist(),
        )),
    }

    return model, metrics
```

**Deployment**: Model scores are computed at `ORDER_CONFIRMED` event and stored as order attributes. Orders with delay probability > 0.4 are flagged for proactive customer notification and CSR review.

---

### 7.2 NLP — Customer Complaint Classification

Automatically classifies inbound customer complaints (email, portal, EDI 824) into routing categories to eliminate manual triage.

**Classes**:

| Class | Routing Target | SLA |
|-------|---------------|-----|
| LATE_DELIVERY | Logistics team | 2 hours |
| SHORT_SHIPMENT | Warehouse ops | 4 hours |
| WRONG_ITEM | Warehouse ops | 4 hours |
| DAMAGED_GOODS | Quality team | 24 hours |
| INVOICE_DISPUTE | Finance/AR | 24 hours |
| PRICE_DISCREPANCY | Commercial | 24 hours |
| QUALITY_DEFECT | Quality team | 8 hours |
| CANCELLATION_REQUEST | Order Management | 1 hour |

```python
# python/13_order_management/ml/complaint_classifier.py

from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
from typing import List, Dict


COMPLAINT_CLASSES = [
    "LATE_DELIVERY", "SHORT_SHIPMENT", "WRONG_ITEM", "DAMAGED_GOODS",
    "INVOICE_DISPUTE", "PRICE_DISCREPANCY", "QUALITY_DEFECT", "CANCELLATION_REQUEST",
]

ROUTING_MAP = {
    "LATE_DELIVERY": "logistics",
    "SHORT_SHIPMENT": "warehouse",
    "WRONG_ITEM": "warehouse",
    "DAMAGED_GOODS": "quality",
    "INVOICE_DISPUTE": "finance",
    "PRICE_DISCREPANCY": "commercial",
    "QUALITY_DEFECT": "quality",
    "CANCELLATION_REQUEST": "order_management",
}


class ComplaintClassifier:
    """
    Multi-class complaint classifier using a fine-tuned DistilBERT model.
    Runs locally (no external API calls). Model weights stored in /models/.
    """

    def __init__(self, model_path: str = "models/complaint-classifier"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self.model.eval()

    def classify(
        self,
        complaint_text: str,
        confidence_threshold: float = 0.70,
    ) -> Dict:
        """
        Classify a complaint and determine routing.

        Parameters
        ----------
        complaint_text : str
            Raw complaint text (email body, portal message, parsed EDI 824).
        confidence_threshold : float
            Below this, the complaint is routed to MANUAL_REVIEW.

        Returns
        -------
        dict
            predicted_class, confidence, routing_target, requires_manual_review
        """
        inputs = self.tokenizer(
            complaint_text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        )

        with torch.no_grad():
            logits = self.model(**inputs).logits
            probs = torch.softmax(logits, dim=-1).squeeze().tolist()

        top_idx = int(torch.argmax(logits))
        predicted_class = COMPLAINT_CLASSES[top_idx]
        confidence = probs[top_idx]

        return {
            "predicted_class": predicted_class,
            "confidence": round(confidence, 4),
            "routing_target": ROUTING_MAP[predicted_class],
            "requires_manual_review": confidence < confidence_threshold,
            "all_probabilities": dict(zip(COMPLAINT_CLASSES, probs)),
        }
```

**Fine-tuning**: The model must be fine-tuned on a minimum of 2,000 labelled historical complaints (supervised by CS team leads). Re-train quarterly or when accuracy drops below 85% on the validation holdout.

---

### 7.3 Demand Disaggregation for ATP Allocation

When aggregate demand forecasts are available from Dept 05 (Demand Planning) but ATP allocation must be made at the customer×SKU×warehouse level, a disaggregation model is required.

```python
# python/13_order_management/ml/demand_disaggregation.py

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from typing import Dict


def disaggregate_demand(
    aggregate_forecast: Dict[str, float],  # {sku_id: forecast_units}
    historical_customer_shares: pd.DataFrame,
    # columns: sku_id, customer_id, warehouse_id, historical_share (0-1)
    smoothing_alpha: float = 0.3,
) -> pd.DataFrame:
    """
    Disaggregate SKU-level forecasts to customer×warehouse allocations.

    Method: Exponentially smoothed historical share proportions.
    Shares are normalised to sum to 1.0 per SKU.
    This allocation informs ATP reservation limits per customer.
    """
    result_rows = []

    for sku_id, total_forecast in aggregate_forecast.items():
        sku_shares = historical_customer_shares[
            historical_customer_shares["sku_id"] == sku_id
        ].copy()

        if sku_shares.empty:
            continue

        # Normalise shares to ensure they sum to 1
        share_sum = sku_shares["historical_share"].sum()
        if share_sum == 0:
            sku_shares["normalised_share"] = 1 / len(sku_shares)
        else:
            sku_shares["normalised_share"] = sku_shares["historical_share"] / share_sum

        sku_shares["allocated_units"] = np.floor(
            sku_shares["normalised_share"] * total_forecast
        )

        result_rows.append(sku_shares[["sku_id", "customer_id", "warehouse_id", "allocated_units"]])

    return pd.concat(result_rows, ignore_index=True) if result_rows else pd.DataFrame()
```

---

### 7.4 Reinforcement Learning for Order Promising Under Constraints

When multiple customer orders compete for limited inventory, an RL agent learns the optimal acceptance/deferral policy to maximise total margin while respecting inventory, capacity, and service-level constraints.

**Environment definition**:

- **State**: current ATP per SKU×warehouse, open order queue (by tier and value), time to next replenishment.
- **Action**: for each incoming order, choose ACCEPT (full), ACCEPT_PARTIAL, DEFER_TO_DATE, or DECLINE.
- **Reward**: margin earned from accepted orders minus penalty for broken commitments and OTIF violations.

```python
# python/13_order_management/ml/rl_order_promising.py

import numpy as np
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class OrderPromiseState:
    atp_by_sku: np.ndarray        # shape: (n_skus,) — available units
    queue_by_tier: np.ndarray     # shape: (n_tiers,) — pending order count
    days_to_replenishment: float  # float days


@dataclass
class OrderPromiseAction:
    order_id: str
    decision: str  # ACCEPT | ACCEPT_PARTIAL | DEFER | DECLINE
    confirmed_qty: float
    promised_date: str


def reward_function(
    accepted_margin_cents: float,
    commitment_breach_penalty_cents: float,
    otif_violation_penalty_cents: float,
    tier_a_sla_breach_penalty_cents: float,
) -> float:
    """
    Reward signal for the RL agent.
    Penalties are subtracted; margin is the positive signal.
    Tier A customer SLA breaches incur the highest penalty (retention risk).
    """
    return (
        accepted_margin_cents
        - commitment_breach_penalty_cents
        - otif_violation_penalty_cents
        - tier_a_sla_breach_penalty_cents
    )
```

**Training**: Use `stable-baselines3` (MIT) with PPO algorithm. Train on 24 months of historical order data in simulation mode (using `simpy` to replay order arrival sequences). Minimum 1 million simulation steps before production deployment.

**Guardrails**:
- RL decisions are logged with full state for auditability.
- All DECLINE decisions above $10,000 require CSR confirmation before execution.
- Model is retrained monthly on rolling 12-month data.

---

## 8. Phase 5: Integration & Automation

**Duration**: Weeks 22–36  
**Owner**: Integration Architecture team

### 8.1 SAP SD / Order-to-Cash Integration

SAP SD remains the system of record for legal invoicing in most enterprise deployments. The integration pattern is event-driven:

- **Outbound (SAP → OM)**: IDOC ORDERS05 (inbound SO), INVOIC02 (invoice confirmation), PAYMENT01 (payment posting).
- **Inbound (OM → SAP)**: REST API via SAP BTP or direct RFC call for delivery confirmation, credit status updates.
- All SAP calls are wrapped in a saga pattern with compensating transactions for rollback.

### 8.2 UN/EDIFACT EDI Pipeline

Support for the following EDIFACT messages:

| Message | Direction | Use |
|---------|-----------|-----|
| ORDERS D.96A | Inbound | Customer purchase order |
| ORDRSP D.96A | Outbound | Order acknowledgement / confirmation |
| DESADV D.96A | Outbound | Despatch advice (ASN — Advanced Ship Notice) |
| INVOIC D.96A | Outbound | Commercial invoice |
| RECADV D.96A | Inbound | Receiving advice (goods receipt confirmation) |
| REMADV D.96A | Inbound | Remittance advice (payment notification) |
| CONTRL | Both | Functional acknowledgement |

```typescript
// src/departments/13-order-management/integrations/EDIAdapter.ts

export interface EDIMessage {
  readonly messageType: 'ORDERS' | 'ORDRSP' | 'DESADV' | 'INVOIC' | 'RECADV' | 'REMADV';
  readonly interchangeRef: string;
  readonly senderId: string;      // GLN of sender
  readonly recipientId: string;   // GLN of recipient
  readonly messageDate: string;   // ISO datetime
  readonly rawContent: string;    // EDIFACT segment string
  readonly parsedPayload: Record<string, unknown>;
}

export interface EDIOrdersPayload {
  customerOrderRef: string;
  orderDate: string;
  requestedDeliveryDate: string;
  lines: Array<{
    lineNumber: number;
    gtin: string;
    orderedQty: number;
    uom: string;
    unitPriceCents?: number;
  }>;
}

export function parseORDERS(raw: string): EDIOrdersPayload {
  // Production implementation uses a certified EDIFACT parser (e.g. node-edifact, MIT)
  // This is a structural placeholder showing the contract
  throw new Error('Not implemented — use EDI parser library');
}
```

### 8.3 Salesforce CRM Integration

Salesforce is the customer-facing CRM. Order Management integrates via Salesforce Platform Events (real-time) and Bulk API 2.0 (batch reconciliation):

- **Order created in portal** → Salesforce Opportunity updated to Closed Won → Platform Event fires → OM receives order.
- **Order status change** → OM publishes event → Salesforce Case/Opportunity updated via outbound message.
- **Customer complaint logged in Salesforce** → Platform Event → NLP classifier routes to OM team queue.

### 8.4 B2C Channel Integration (Magento/Shopify)

For B2C channels, orders arrive via webhook (Shopify) or REST API poll (Magento). Key requirements:

- Idempotency key = `{channel}_{external_order_id}` — prevent duplicate processing on webhook retry.
- Price recalculation must NOT occur after order capture — honour the B2C checkout price.
- ATP check must complete within the B2C checkout session (< 3 seconds SLA).
- DESADV/tracking number must push back to Shopify/Magento within 30 minutes of carrier pickup scan.

### 8.5 Carrier Tracking API Integration

Real-time delivery confirmation drives the OTIF calculation and POI "on-time" dimension:

```typescript
// src/departments/13-order-management/integrations/CarrierTrackingAdapter.ts

export interface TrackingEvent {
  readonly shipmentId: string;
  readonly trackingNumber: string;
  readonly carrierScac: string;
  readonly eventCode: string;  // standard carrier event codes
  readonly eventDescription: string;
  readonly eventTimestamp: string;
  readonly locationCity?: string;
  readonly locationCountry?: string;
  readonly estimatedDeliveryDate?: string;
  readonly isDelivered: boolean;
  readonly requiresSignature: boolean;
}

export interface CarrierTrackingAdapter {
  getTrackingEvents(trackingNumber: string): Promise<TrackingEvent[]>;
  subscribeToUpdates(trackingNumber: string, callbackUrl: string): Promise<void>;
}
```

Carrier integrations are implemented per carrier using their published REST APIs. A normalisation layer maps carrier-specific event codes to a canonical internal taxonomy.

---

## 9. Phase 6: Continuous Improvement

**Duration**: Week 36 onwards (steady state)  
**Cadence**: Monthly operational review; quarterly strategic review

### 9.1 PDCA Cycle for Order Management

- **Plan**: Monthly review of OTIF, POI, OFCT vs targets. Identify top 3 gap categories.
- **Do**: Root-cause analysis using 5-why or Fishbone for each gap. Implement countermeasures.
- **Check**: 4-week post-implementation measurement to confirm improvement.
- **Act**: Standardise successful countermeasures; update SOPs; re-train ML models if applicable.

### 9.2 Model Drift Monitoring

All ML models are monitored for concept drift using Population Stability Index (PSI):

```python
# python/13_order_management/monitoring/model_drift.py

import numpy as np
from typing import List


def population_stability_index(expected: np.ndarray, actual: np.ndarray, bins: int = 10) -> float:
    """
    PSI < 0.1: No significant change
    PSI 0.1–0.25: Moderate change — investigate
    PSI > 0.25: Significant shift — retrain required
    """
    expected_pct, bin_edges = np.histogram(expected, bins=bins, density=True)
    actual_pct, _ = np.histogram(actual, bins=bin_edges, density=True)

    # Avoid log(0)
    expected_pct = np.where(expected_pct == 0, 1e-6, expected_pct)
    actual_pct = np.where(actual_pct == 0, 1e-6, actual_pct)

    psi = np.sum((actual_pct - expected_pct) * np.log(actual_pct / expected_pct))
    return float(psi)
```

### 9.3 Voice of Customer (VoC) Programme

Deploy quarterly NPS surveys to Tier A customers. Automatically correlate NPS responses with OTIF and POI data to identify service quality drivers. Feed qualitative complaint themes into the NLP classifier retraining pipeline.

---

## 10. Technology Stack & Architecture

### 10.1 Component Architecture

```
[Customer Channels]
    EDI (EDIFACT)  |  B2B Portal  |  Shopify/Magento  |  Salesforce  |  SAP SD
          |                |               |                  |              |
          +----------------+---------------+------------------+--------------+
                                     [API Gateway / EDI Hub]
                                           |
                              [Order Management Service]
                              +---------------------------+
                              | Order Capture & Validation|
                              | Credit Check Engine       |
                              | ATP/CTP Engine            |
                              | Price Determination       |
                              | Event Store (CQRS)        |
                              +---------------------------+
                                     |         |
                          [Kafka Event Bus]   [ML Scoring Service]
                               |                    |
               +---------------+          +---------+-------+
               |               |          |                 |
        [Inventory]     [Warehouse]  [Delay Predictor]  [Complaint NLP]
        (Dept 02)       (Dept 10)   (XGBoost)          (DistilBERT)
               |               |
         [Logistics]   [Carrier Tracking]
         (Dept 08)
```

### 10.2 Technology Decisions

| Component | Technology | License | Rationale |
|-----------|-----------|---------|-----------|
| Domain logic | TypeScript / Node.js | — | Type safety, existing codebase |
| Math models | Python 3.11+ | — | Scientific computing ecosystem |
| Message broker | Apache Kafka | Apache-2.0 | Event streaming at scale |
| Stream processing | Apache Flink | Apache-2.0 | OTIF real-time aggregation |
| ML serving | FastAPI + Uvicorn | MIT | Lightweight Python API |
| EDI parsing | node-edifact | MIT | EDIFACT UN/D.96A support |
| Job scheduler | Apache Airflow | Apache-2.0 | ML pipeline orchestration |
| Observability | OpenTelemetry + Jaeger | Apache-2.0 | Distributed tracing |

---

## 11. Change Management & Training

### 11.1 Stakeholder Impact Matrix

| Stakeholder Group | Impact Level | Primary Change | Training Required |
|------------------|-------------|----------------|------------------|
| Customer Service Reps | High | Exception-based work; AI-assisted routing | 16 hours |
| Order Management team | High | ATP/CTP automation replaces manual check | 24 hours |
| Credit Controllers | Medium | Automated credit decisions; manual review queue | 8 hours |
| Sales / Account Managers | Medium | Real-time OTIF visibility; customer portal | 8 hours |
| Finance / AR | Medium | Automated invoice triggering; dispute workflow | 12 hours |
| IT / Integration team | High | EDI hub, API gateway, Kafka configuration | 40 hours |
| Supply Chain Directors | Low | Executive dashboards | 4 hours |

### 11.2 Training Programme

- **Wave 1** (Weeks 28–32): IT and integration team — technical configuration and testing.
- **Wave 2** (Weeks 34–36): Order Management and CS power users — UAT participation.
- **Wave 3** (Week 38): All end users — role-based training; job aids distributed.
- **Hypercare** (Weeks 39–46): Daily drop-in support sessions; escalation hotline.

### 11.3 Communication Plan

Issue programme communications at the following cadence:
- Monthly progress newsletter to all affected departments.
- Bi-weekly steering committee update (programme sponsor, IT director, CS director, Supply Chain VP).
- Weekly operational team stand-up during UAT and hypercare phases.

---

## 12. Implementation KPIs

### 12.1 Leading Indicators (measured during implementation)

| KPI | Target | Measurement Frequency |
|-----|--------|----------------------|
| Master data completeness (customer) | >= 99% | Weekly |
| EDI automation rate (orders processed without manual touch) | >= 85% | Weekly |
| ATP auto-confirmation rate | >= 90% | Weekly |
| Credit check auto-approval rate | >= 75% | Weekly |
| System uptime (order capture service) | >= 99.9% | Daily |

### 12.2 Lagging Indicators (business outcomes post go-live)

| KPI | Current Baseline | 6-Month Target | 12-Month Target | World Class |
|-----|-----------------|----------------|-----------------|-------------|
| Perfect Order Index (POI) | TBD | >= 90% | >= 95% | >= 98% |
| OTIF (overall) | TBD | >= 93% | >= 97% | >= 98% |
| OFCT (days) SCOR RS.1.1 | TBD | <= 5.5 | <= 3.5 | <= 2.1 |
| Order-to-Cash cycle (days) | TBD | -15% vs baseline | -30% vs baseline | <= 28 days |
| DSO (Days Sales Outstanding) | TBD | -5 days | -10 days | 25-30 days |
| Manual order entry rate | TBD | <= 20% | <= 10% | <= 5% |
| Complaint auto-routing accuracy | N/A | >= 80% | >= 90% | >= 95% |
| Order delay prediction AUC-ROC | N/A | >= 0.75 | >= 0.82 | >= 0.88 |
| Credit hold resolution time (hours) | TBD | <= 6 | <= 4 | <= 2 |
| POI — Correct Documentation factor | TBD | >= 97% | >= 99% | >= 99.5% |

---

## 13. Risk & Mitigation

| # | Risk | Probability | Impact | Risk Score | Mitigation | Owner |
|---|------|------------|--------|------------|-----------|-------|
| R1 | SAP SD integration delay due to basis configuration | High | High | Critical | Start SAP design in Week 6; dedicated SAP functional resource | IT Director |
| R2 | EDI partner onboarding slower than planned | Medium | Medium | Medium | Parallel-run manual entry for slow adopters; EDI mandate date for Tier A | Integration Lead |
| R3 | Customer master data quality insufficient for credit automation | High | High | Critical | Data quality sprint in Phase 0; credit team manual review until DQ >= 95% | Data Governance |
| R4 | XGBoost model under-performs on new customer segments | Low | Medium | Low | Flag low-confidence predictions for manual review; retrain with new data quarterly | Data Science Lead |
| R5 | RL order promising agent produces sub-optimal outcomes in rare scenarios | Medium | High | High | Maintain rule-based fallback; RL decisions > $50K require human approval | Order Mgmt Director |
| R6 | Carrier tracking API latency impacts OTIF real-time accuracy | Low | Medium | Low | Cache last-known event; batch reconcile every 15 minutes | Integration Lead |
| R7 | Retailer OTIF penalty triggers during cutover period | Medium | High | High | Negotiate cutover window; notify Tier A customers 6 weeks in advance | Account Management |
| R8 | NLP complaint classifier biased toward training data language patterns | Low | Medium | Low | Multilingual fine-tuning; human review queue for low-confidence outputs | Data Science Lead |
| R9 | Kafka broker outage causes order event loss | Low | High | High | Kafka replication factor >= 3; consumer offset monitoring; dead-letter queue | IT Infrastructure |
| R10 | Change resistance from CSR team (automation displacing tasks) | Medium | Medium | Medium | Co-design workshops; re-skill to exception management; transparent communication | HR + CS Director |

---

## 14. Timeline Summary

| Phase | Weeks | Key Deliverables | Gate Criteria |
|-------|-------|-----------------|---------------|
| Phase 0: Assessment | 1–4 | AS-IS process maps, data quality baseline, gap register | Gap register approved by steering committee |
| Phase 1: Foundation | 5–10 | Customer master cleansed, order domain model live, event store integrated | Master data completeness >= 99% |
| Phase 2: Process Std | 11–18 | SOPs documented, OTIF dashboard live (historical), exception framework active | OTIF dashboard validated against manual calculations |
| Phase 3: Math Models | 11–22 | ATP, CTP, POI, OFCT, credit check, price engine live | ATP auto-confirmation >= 85% accuracy vs manual |
| Phase 4: ML/AI | 19–32 | XGBoost delay predictor, NLP complaint classifier, RL promising agent | AUC-ROC >= 0.75; complaint routing accuracy >= 80% |
| Phase 5: Integration | 22–36 | SAP SD, EDI ORDERS/ORDRSP/DESADV/INVOIC, Salesforce, Shopify/Magento live | EDI order processing end-to-end tested with 3 pilot customers |
| UAT & Go-Live | 34–40 | Full UAT with business users, parallel run, cutover | POI >= 88% in parallel run; zero P1 defects open |
| Phase 6: Improvement | 41+ | Monthly PDCA, model retraining, VoC programme active | POI >= 90% sustained for 8 consecutive weeks |

**Total programme duration**: 40–44 weeks to full production go-live.

---

## 15. References

### Standards & Frameworks

- ASCM/APICS, *SCOR Digital Standard v4.0* (ASCM, 2022). Process definitions for RS.1.1 (OFCT), AG.1.1–1.3 (Agility).
- APICS Dictionary, 16th Edition (ASCM, 2024). Definitions: OTIF, POI, ATP, CTP, DSO.
- UN/CEFACT, *UN/EDIFACT Directory D.96A*. Messages: ORDERS, ORDRSP, DESADV, INVOIC, RECADV, REMADV, CONTRL.
- ICC, *Incoterms® 2020* (ICC, 2019). Trade terms applicable to Incoterm field in SalesOrder.
- ISO 9001:2015, §8.2 (Requirements for products and services), §8.5 (Production and service provision).
- GS1, *General Specifications v23.0*. GTIN, GLN, SSCC, UOM codes.
- US GAAP ASC 606, *Revenue from Contracts with Customers*. Governs revenue recognition timing tied to O2C events.
- IFRS 15, *Revenue from Contracts with Customers*. International equivalent to ASC 606.

### Academic & Industry References

- Chopra, S. & Meindl, P., *Supply Chain Management: Strategy, Planning, and Operation*, 6th Ed. (Pearson, 2016). Chapters 11–13: Demand management, order fulfillment.
- Christopher, M., *Logistics and Supply Chain Management*, 6th Ed. (FT Publishing, 2022). Customer service and order cycle time.
- Chen, T. & Guestrin, C., "XGBoost: A Scalable Tree Boosting System," *KDD 2016*. Foundation for order delay prediction model.
- Devlin, J. et al., "BERT: Pre-training of Deep Bidirectional Transformers," *NAACL 2019*. Basis for complaint NLP classifier.
- Silver, D. et al., "Mastering the game of Go without human knowledge," *Nature 550* (2017). PPO foundations for RL order promising.
- APQC, *Order Management Benchmarks: Open Standards Benchmarking* (2024 edition). OFCT and DSO benchmarks.
- Gartner, *Magic Quadrant for Warehouse Management Systems* (2024). Technology reference for adjacent WMS integration.
- McKinsey Global Institute, *The Age of Analytics: Competing in a Data-Driven World* (2016). Business case framework for O2C analytics investment.
- Walmart Supplier Manual, *Transportation & Routing Guide* (2024). OTIF standard: 98%, penalty structure.
- Target Corporation, *Supplier Standards and Expectations* (2024). OTIF standard: 98.5%.

### Internal Cross-References

- `src/departments/02-inventory/` — Event-sourced inventory; ATP stock query contracts.
- `src/departments/05-demand-planning/` — Forecasting algorithms (SMA, SES, Holt, Holt-Winters); safety stock.
- `src/departments/08-logistics/` — Shipment domain, Incoterms, carrier integration, transit time matrices.
- `src/departments/10-warehouse/` — FEFO picking, WMS reservation API, slot cut-off times.
- `src/shared/types.ts` — `Money`, `UOM`, `ISOTimestamp`, `INCOTERMS_2020` constants.
- `docs/standards/REGULATORY_FRAMEWORK.md` — Full regulatory reference including Incoterms 2020, GS1.

---

*End of Implementation Guide — Department 13: Order Management & Customer Service*

*This document is subject to version control. All amendments must be reviewed by the Supply Chain Programme Director and recorded in the document revision history.*
