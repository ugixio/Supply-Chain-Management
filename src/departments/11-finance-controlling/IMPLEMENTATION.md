# Finance & Supply Chain Controlling — Implementation Guide

**Department:** 11 — Finance & Supply Chain Controlling
**Standard:** SCOR-DS | ISO 28000:2022 | IFRS | US GAAP
**Version:** 1.0.0
**Date:** 2026-06-20
**Classification:** Internal — Restricted

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Prerequisites and Dependencies](#2-prerequisites-and-dependencies)
3. [Phase 0: Assessment and AS-IS Analysis](#3-phase-0-assessment-and-as-is-analysis)
4. [Phase 1: Foundation and Master Data](#4-phase-1-foundation-and-master-data)
5. [Phase 2: Process Standardisation and Core Analytics](#5-phase-2-process-standardisation-and-core-analytics)
6. [Phase 3: Mathematical Models](#6-phase-3-mathematical-models)
7. [Phase 4: ML/AI Pipeline](#7-phase-4-mlai-pipeline)
8. [Phase 5: Integration and Automation](#8-phase-5-integration-and-automation)
9. [Phase 6: Continuous Improvement](#9-phase-6-continuous-improvement)
10. [Technology Stack and Architecture](#10-technology-stack-and-architecture)
11. [Change Management and Training](#11-change-management-and-training)
12. [Implementation KPIs](#12-implementation-kpis)
13. [Risk and Mitigation](#13-risk-and-mitigation)
14. [Timeline Summary](#14-timeline-summary)
15. [References](#15-references)

---

## 1. Executive Summary

The Finance and Supply Chain Controlling department serves as the financial intelligence hub of the enterprise supply chain, translating physical goods flows into financial signals, enforcing fiscal governance across all procurement-to-payment (P2P) and order-to-cash (O2C) cycles, and delivering the decision-grade analytics required by the C-suite and Board.

This implementation guide is designed for a global multinational corporation (MNC) operating across multiple jurisdictions with complex intercompany structures, multi-currency reporting under IFRS and US GAAP, and a supply chain spanning hundreds of tier-1 and tier-2 suppliers. It targets full SCOR-DS alignment across the Enable and Plan process categories, with particular emphasis on the Asset Management (AM) and Financial Flows (FF) performance attributes.

### Strategic Objectives

- Achieve a 3-way invoice match automation rate of greater than 90 percent, reducing manual exception handling by 70 percent within 12 months.
- Compress the Cash-to-Cash (C2C) cycle by 8 to 12 days through dynamic discounting, supply chain finance, and payables optimisation.
- Deliver real-time working capital visibility across all legal entities within a single controlling layer.
- Implement IFRS-compliant inventory valuation (IAS 2) with automated LCNRV write-down detection.
- Establish a transfer pricing framework compliant with OECD BEPS Actions 8-10 for all intercompany supply chain transactions.
- Deploy ML-driven invoice fraud detection achieving a precision of greater than 95 percent at a recall threshold of 0.7.

### Scope

| Dimension | Scope |
|-----------|-------|
| Legal entities | All subsidiary entities under the MNC group consolidation |
| Currencies | Functional currency per entity + USD/EUR group reporting |
| Accounting standards | IFRS (primary) + US GAAP (dual-reporting for US entities) |
| ERP systems | SAP S/4HANA FI/CO, Oracle Financials Cloud |
| Supply chain finance | Coupa Pay, Taulia SCF |
| Reconciliation | BlackLine |
| Payments | SWIFT MT940 / SEPA CAMT.053 |

---

## 2. Prerequisites and Dependencies

### 2.1 Organisational Prerequisites

- Chief Financial Officer sponsorship and Supply Chain Finance Director ownership.
- Completed SCOR-DS maturity assessment (minimum Level 2 in Plan and Enable processes).
- Active Chart of Accounts (CoA) rationalisation project closed or in final phase.
- Legal entity master data governance model in place (GLN codes per GS1 assigned).
- Transfer pricing policy reviewed by tax counsel within the last 24 months.

### 2.2 Technical Prerequisites

| Requirement | Minimum Version | Status Check |
|-------------|----------------|--------------|
| Node.js | 20 LTS | `node --version` |
| TypeScript | 5.4 | `tsc --version` |
| Python | 3.11 | `python --version` |
| PostgreSQL | 15 | `psql --version` |
| Redis | 7.2 | `redis-cli --version` |
| Apache Kafka | 3.6 | broker metadata check |
| SAP S/4HANA | 2023 FPS02 | BASIS team verification |

### 2.3 Python Dependencies (OSI-Licensed)

```bash
pip install numpy scipy pandas statsmodels scikit-learn xgboost lightgbm \
            torch tensorflow transformers pytesseract pdfplumber \
            networkx pulp shap imbalanced-learn
```

### 2.4 TypeScript/Node.js Dependencies

```json
{
  "dependencies": {
    "decimal.js": "^10.4.3",
    "date-fns": "^3.6.0",
    "zod": "^3.23.0",
    "uuid": "^9.0.0",
    "ioredis": "^5.3.2",
    "kafkajs": "^2.2.4",
    "pg": "^8.12.0",
    "axios": "^1.7.2"
  }
}
```

### 2.5 Upstream Module Dependencies

This department consumes events from:

- `01-procurement` — PurchaseOrder APPROVED, GoodsReceiptPosted events
- `03-demand-planning` — ForecastRevised events (for cash flow forecasting)
- `05-inventory-management` — StockMovement events (for inventory valuation)
- `06-warehouse-management` — GoodsIssued events (for COGS recognition)
- `07-logistics-transportation` — ShipmentDelivered events (for landed cost capture)
- `09-compliance-regulatory` — ComplianceClearance events (for duty cost booking)

---

## 3. Phase 0: Assessment and AS-IS Analysis

**Duration:** 4 weeks
**Deliverables:** AS-IS process maps, gap analysis report, business case, programme charter

### 3.1 Financial Process Inventory

Conduct a structured inventory of all existing financial processes using the SCOR-DS process reference model. For each process, document: current state, pain points, technology, cycle time, and FTE effort.

| Process Area | SCOR Reference | AS-IS State | Target State |
|-------------|---------------|-------------|--------------|
| Invoice matching | EP.07 | Manual 3-way match, 40% auto | 90%+ automated |
| Working capital reporting | EP.08 | Monthly, T+5 days | Daily, T+0 |
| Inventory valuation | EP.06 | AVCO batch monthly | Real-time FIFO/AVCO |
| Transfer pricing | EP.10 | Spreadsheet-based | Rule engine + audit trail |
| Variance analysis | EP.09 | Manual ERP extract | Automated with root cause |
| Landed cost | sD2.3 | Partial allocation | Full multi-leg allocation |

### 3.2 Data Quality Assessment

Run the following Python diagnostic to profile source data quality before any transformation:

```python
# python/11_finance_controlling/data_quality/assess_source_data.py

import pandas as pd
import numpy as np
from typing import Dict, Any


def assess_invoice_data_quality(df_invoices: pd.DataFrame) -> Dict[str, Any]:
    """
    Assess data quality of source invoice data prior to 3-way match implementation.

    Args:
        df_invoices: Raw invoice DataFrame from ERP extract.

    Returns:
        Dictionary of quality metrics with pass/fail thresholds.
    """
    total = len(df_invoices)
    report = {}

    # Completeness checks
    mandatory_fields = [
        "invoice_number", "vendor_id", "invoice_date",
        "gross_amount_cents", "currency_code", "po_number"
    ]
    for field in mandatory_fields:
        null_pct = df_invoices[field].isna().sum() / total * 100
        report[f"{field}_null_pct"] = round(null_pct, 2)

    # Duplicate detection
    dup_count = df_invoices.duplicated(
        subset=["vendor_id", "invoice_number", "gross_amount_cents"]
    ).sum()
    report["duplicate_invoice_count"] = int(dup_count)
    report["duplicate_rate_pct"] = round(dup_count / total * 100, 3)

    # Currency code validation (ISO 4217)
    valid_currencies = {"USD", "EUR", "GBP", "JPY", "CHF", "CAD", "AUD", "CNY"}
    invalid_ccy = (~df_invoices["currency_code"].isin(valid_currencies)).sum()
    report["invalid_currency_count"] = int(invalid_ccy)

    # Amount range sanity
    report["negative_amount_count"] = int(
        (df_invoices["gross_amount_cents"] < 0).sum()
    )
    report["zero_amount_count"] = int(
        (df_invoices["gross_amount_cents"] == 0).sum()
    )

    # PO linkage rate
    po_linked = df_invoices["po_number"].notna().sum()
    report["po_linkage_rate_pct"] = round(po_linked / total * 100, 2)

    return report
```

### 3.3 Gap Analysis Matrix

| Capability | Current Maturity (1-5) | Target Maturity | Gap | Priority |
|------------|----------------------|-----------------|-----|----------|
| 3-way invoice matching | 2 | 5 | 3 | Critical |
| C2C cycle measurement | 1 | 4 | 3 | High |
| Landed cost allocation | 2 | 4 | 2 | High |
| Transfer pricing automation | 1 | 4 | 3 | Critical |
| ABC costing | 2 | 4 | 2 | Medium |
| Working capital forecasting (ML) | 1 | 5 | 4 | High |
| Invoice fraud detection (ML) | 1 | 5 | 4 | Critical |
| IFRS inventory valuation | 3 | 5 | 2 | High |

---

## 4. Phase 1: Foundation and Master Data

**Duration:** 6 weeks
**Deliverables:** GL master, cost centre hierarchy, vendor master, currency tables, event store schema

### 4.1 Chart of Accounts Design

Define a SCOR-aligned CoA that maps financial accounts to supply chain cost categories. All amounts stored as integer cents (no floating-point arithmetic).

```typescript
// src/departments/11-finance-controlling/domain/ChartOfAccounts.ts

export const SC_GL_ACCOUNTS = {
  // Assets
  INVENTORY_RAW_MATERIAL:        { code: "13100", type: "ASSET",   scor: "sS" },
  INVENTORY_WIP:                 { code: "13200", type: "ASSET",   scor: "sM" },
  INVENTORY_FINISHED_GOODS:      { code: "13300", type: "ASSET",   scor: "sD" },
  ACCOUNTS_RECEIVABLE:           { code: "12000", type: "ASSET",   scor: "sD" },
  PREPAID_CUSTOMS_DUTIES:        { code: "13500", type: "ASSET",   scor: "sD" },

  // Liabilities
  ACCOUNTS_PAYABLE:              { code: "21000", type: "LIABILITY", scor: "sS" },
  ACCRUED_FREIGHT:               { code: "21100", type: "LIABILITY", scor: "sD" },
  GOODS_RECEIPT_CLEARING:        { code: "21200", type: "LIABILITY", scor: "sS" },

  // COGS and SC Costs
  COGS_MATERIAL:                 { code: "50100", type: "EXPENSE",  scor: "sS" },
  COGS_FREIGHT_INBOUND:          { code: "50200", type: "EXPENSE",  scor: "sS" },
  COGS_CUSTOMS_DUTY:             { code: "50300", type: "EXPENSE",  scor: "sS" },
  WAREHOUSE_OPERATING_COST:      { code: "51100", type: "EXPENSE",  scor: "sD" },
  QUALITY_INSPECTION_COST:       { code: "51200", type: "EXPENSE",  scor: "sS" },
  INTERCOMPANY_CLEARING:         { code: "19000", type: "ASSET",   scor: "Enable" },
} as const;

export type GLAccountCode = keyof typeof SC_GL_ACCOUNTS;
```

### 4.2 Cost Centre Hierarchy

```typescript
// src/departments/11-finance-controlling/domain/CostCentre.ts

export interface CostCentre {
  readonly id: string;
  readonly code: string;               // e.g., "CC-WH-EU-001"
  readonly name: string;
  readonly parentId: string | null;
  readonly legalEntityId: string;      // maps to GLN
  readonly scorProcess: string;        // sS, sM, sD, sP, Enable
  readonly budgetOwnerEmail: string;
  readonly currency: string;           // ISO 4217 functional currency
  readonly isActive: boolean;
}

export function buildCostCentreHierarchy(centres: CostCentre[]): Map<string, CostCentre[]> {
  const hierarchy = new Map<string, CostCentre[]>();
  for (const cc of centres) {
    const parentKey = cc.parentId ?? "ROOT";
    if (!hierarchy.has(parentKey)) hierarchy.set(parentKey, []);
    hierarchy.get(parentKey)!.push(cc);
  }
  return hierarchy;
}
```

### 4.3 Event Store Schema for Financial Events

```sql
-- Financial journal entries stored as immutable events
CREATE TABLE finance_journal_events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type      VARCHAR(64) NOT NULL,
    aggregate_id    VARCHAR(128) NOT NULL,
    aggregate_type  VARCHAR(64) NOT NULL,
    sequence_number BIGINT NOT NULL,
    occurred_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    payload         JSONB NOT NULL,
    idempotency_key VARCHAR(256) UNIQUE NOT NULL,
    created_by      VARCHAR(128) NOT NULL,
    CONSTRAINT uq_aggregate_seq UNIQUE (aggregate_id, sequence_number)
);

CREATE INDEX idx_fin_events_aggregate ON finance_journal_events(aggregate_id, sequence_number);
CREATE INDEX idx_fin_events_type ON finance_journal_events(event_type);
CREATE INDEX idx_fin_events_occurred ON finance_journal_events(occurred_at);
```

---

## 5. Phase 2: Process Standardisation and Core Analytics

**Duration:** 8 weeks
**Deliverables:** Standard operating procedures, reconciliation workflows, KPI dashboards

### 5.1 P2P (Procure-to-Pay) Cycle Standardisation

The P2P cycle must be fully instrumented with event-driven state transitions. Every state change emits an immutable event.

```typescript
// src/departments/11-finance-controlling/domain/PaymentDocument.ts

export type PaymentStatus =
  | "PENDING_MATCH"
  | "MATCHED"
  | "EXCEPTION"
  | "APPROVED_FOR_PAYMENT"
  | "PAYMENT_INITIATED"
  | "PAYMENT_CONFIRMED"
  | "CANCELLED";

export interface PaymentDocument {
  readonly id: string;
  readonly invoiceId: string;
  readonly purchaseOrderId: string;
  readonly goodsReceiptId: string;
  readonly vendorId: string;
  readonly grossAmountCents: number;
  readonly currency: string;
  readonly paymentDueDate: string;         // ISO 8601
  readonly paymentTermCode: string;        // e.g., "NET30", "2/10NET30"
  readonly status: PaymentStatus;
  readonly matchResult?: ThreeWayMatchResult;
  readonly approvedBy?: string;
  readonly approvedAt?: string;
}
```

### 5.2 O2C (Order-to-Cash) Cycle Standardisation

Define DSO tracking at invoice line level to support real-time C2C calculation:

```typescript
// src/departments/11-finance-controlling/domain/ReceivableDocument.ts

export interface ReceivableDocument {
  readonly id: string;
  readonly customerId: string;
  readonly salesOrderId: string;
  readonly invoiceNumber: string;
  readonly invoiceDate: string;
  readonly dueDate: string;
  readonly grossAmountCents: number;
  readonly outstandingAmountCents: number;
  readonly currency: string;
  readonly agingBucket: "CURRENT" | "1_30" | "31_60" | "61_90" | "OVER_90";
  readonly isDeleted: boolean;
}
```

---

## 6. Phase 3: Mathematical Models

**Duration:** 10 weeks
**Deliverables:** Validated Python implementations, TypeScript business rule layer, unit test suite

### 6.1 Three-Way Invoice Match

The 3-way match is the foundational control in the P2P cycle. It compares purchase order quantity and price against the goods receipt note (GRN) quantity and the supplier invoice, applying configurable tolerances.

**Business Rules:**
- Price tolerance: +/- 2 percent of PO unit price.
- Quantity tolerance: +/- 0.5 percent of GRN quantity.
- Auto-approve when both variances are within tolerance.
- Route to exception queue when either variance exceeds tolerance.
- All amounts in integer cents; no floating-point division before multiplication.

```typescript
// src/departments/11-finance-controlling/domain/ThreeWayMatch.ts

export interface MatchInput {
  poUnitPriceCents: number;       // agreed price per unit
  poQuantity: number;             // ordered quantity
  grnQuantity: number;            // received quantity (GRN)
  invoiceUnitPriceCents: number;  // billed price per unit
  invoiceQuantity: number;        // billed quantity
}

export interface ThreeWayMatchResult {
  priceVariancePct: number;
  quantityVariancePct: number;
  priceVarianceCents: number;
  quantityVarianceCents: number;
  totalVarianceCents: number;
  decision: "AUTO_APPROVE" | "EXCEPTION";
  exceptionReasons: string[];
}

const PRICE_TOLERANCE_PCT = 2.0;
const QTY_TOLERANCE_PCT = 0.5;

export function runThreeWayMatch(input: MatchInput): ThreeWayMatchResult {
  const {
    poUnitPriceCents, poQuantity, grnQuantity,
    invoiceUnitPriceCents, invoiceQuantity
  } = input;

  const reasons: string[] = [];

  // Price variance: (invoice price - PO price) / PO price * 100
  const priceVarianceCents = (invoiceUnitPriceCents - poUnitPriceCents) * invoiceQuantity;
  const priceVariancePct = poUnitPriceCents === 0
    ? 0
    : ((invoiceUnitPriceCents - poUnitPriceCents) / poUnitPriceCents) * 100;

  // Quantity variance: (invoice qty - GRN qty) / GRN qty * 100
  const quantityVarianceCents = (invoiceQuantity - grnQuantity) * poUnitPriceCents;
  const quantityVariancePct = grnQuantity === 0
    ? 0
    : ((invoiceQuantity - grnQuantity) / grnQuantity) * 100;

  if (Math.abs(priceVariancePct) > PRICE_TOLERANCE_PCT) {
    reasons.push(
      `Price variance ${priceVariancePct.toFixed(2)}% exceeds ±${PRICE_TOLERANCE_PCT}% tolerance`
    );
  }

  if (Math.abs(quantityVariancePct) > QTY_TOLERANCE_PCT) {
    reasons.push(
      `Quantity variance ${quantityVariancePct.toFixed(2)}% exceeds ±${QTY_TOLERANCE_PCT}% tolerance`
    );
  }

  return {
    priceVariancePct,
    quantityVariancePct,
    priceVarianceCents,
    quantityVarianceCents,
    totalVarianceCents: priceVarianceCents + quantityVarianceCents,
    decision: reasons.length === 0 ? "AUTO_APPROVE" : "EXCEPTION",
    exceptionReasons: reasons,
  };
}
```

**Step-by-Step Implementation:**

1. Subscribe to `InvoiceReceived`, `GoodsReceiptPosted`, and `PurchaseOrderApproved` Kafka topics.
2. Build an in-memory correlation store (Redis) keyed on `po_number` to join all three documents.
3. When all three documents are present, invoke `runThreeWayMatch()`.
4. Persist the `ThreeWayMatchResult` to the event store with idempotency key = `invoice_id + grn_id + po_id`.
5. Emit `InvoiceAutoApproved` or `InvoiceMatchException` event downstream.
6. Exception events trigger a BlackLine task creation via the BlackLine API.

### 6.2 Cash-to-Cash (C2C) Cycle

The C2C cycle measures the number of days between paying for raw materials and collecting cash from customers. It is the primary working capital efficiency metric.

```
C2C = DIO + DSO - DPO

DIO = (Average Inventory / COGS) x 365
DSO = (Average Accounts Receivable / Revenue) x 365
DPO = (Average Accounts Payable / COGS) x 365
```

```python
# python/11_finance_controlling/working_capital/c2c_cycle.py

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Optional


@dataclass
class C2CComponents:
    """Cash-to-Cash cycle decomposition."""
    dio_days: float          # Days Inventory Outstanding
    dso_days: float          # Days Sales Outstanding
    dpo_days: float          # Days Payable Outstanding
    c2c_days: float          # Net C2C cycle
    period_label: str        # e.g., "2026-Q1"


def compute_c2c(
    avg_inventory_cents: int,
    avg_accounts_receivable_cents: int,
    avg_accounts_payable_cents: int,
    cogs_cents: int,
    revenue_cents: int,
    days_in_period: int = 365,
    period_label: str = "",
) -> C2CComponents:
    """
    Compute the Cash-to-Cash cycle and its components.

    All monetary inputs are in integer cents to avoid floating-point errors.
    Division is performed only at the final step.

    Args:
        avg_inventory_cents: Average inventory value over the period (cents).
        avg_accounts_receivable_cents: Average AR balance (cents).
        avg_accounts_payable_cents: Average AP balance (cents).
        cogs_cents: Cost of goods sold for the period (cents).
        revenue_cents: Net revenue for the period (cents).
        days_in_period: 365 for annual, 91 for quarterly, 30 for monthly.
        period_label: Human-readable period identifier.

    Returns:
        C2CComponents with DIO, DSO, DPO, and net C2C days.

    Raises:
        ValueError: If COGS or revenue is zero (division guard).
    """
    if cogs_cents <= 0:
        raise ValueError("COGS must be positive to compute DIO and DPO.")
    if revenue_cents <= 0:
        raise ValueError("Revenue must be positive to compute DSO.")

    dio = (avg_inventory_cents / cogs_cents) * days_in_period
    dso = (avg_accounts_receivable_cents / revenue_cents) * days_in_period
    dpo = (avg_accounts_payable_cents / cogs_cents) * days_in_period
    c2c = dio + dso - dpo

    return C2CComponents(
        dio_days=round(dio, 1),
        dso_days=round(dso, 1),
        dpo_days=round(dpo, 1),
        c2c_days=round(c2c, 1),
        period_label=period_label,
    )


def benchmark_c2c(c2c: float, industry: str) -> str:
    """
    Benchmark a C2C value against industry world-class targets.

    Args:
        c2c: Computed C2C cycle days.
        industry: One of 'retail', 'manufacturing', 'food'.

    Returns:
        Performance tier: 'WORLD_CLASS' | 'GOOD' | 'AVERAGE' | 'LAGGARD'.
    """
    benchmarks = {
        "retail":        {"world_class": 20, "good": 35, "average": 55},
        "manufacturing": {"world_class": 30, "good": 50, "average": 75},
        "food":          {"world_class": 15, "good": 30, "average": 50},
    }
    thresholds = benchmarks.get(industry, benchmarks["manufacturing"])
    if c2c <= thresholds["world_class"]:
        return "WORLD_CLASS"
    elif c2c <= thresholds["good"]:
        return "GOOD"
    elif c2c <= thresholds["average"]:
        return "AVERAGE"
    return "LAGGARD"
```

**Step-by-Step Implementation:**

1. Build a daily financial snapshot table populated from ERP GL extracts via the SAP BAPI `BAPI_GL_GETGLACCBALANCE`.
2. Compute rolling 90-day averages for inventory, AR, and AP using `pandas.DataFrame.rolling(90).mean()`.
3. Schedule the `compute_c2c()` function nightly and publish results to the KPI dashboard event stream.
4. Configure alert rules: if C2C deteriorates by more than 3 days week-over-week, trigger a CFO notification.
5. Store historical C2C series for trend analysis and LSTM forecasting input (Phase 4).

### 6.3 Working Capital Optimisation

#### Dynamic Discounting Formula

Early payment discounts enable buyers to earn annualised returns on surplus cash. The discount rate must exceed the buyer's cost of capital for the transaction to be value-accretive.

```
discount_rate_pct = APR_pct x (days_early / 365)

Where days_early = payment_due_date - early_payment_date
```

```python
# python/11_finance_controlling/working_capital/dynamic_discounting.py

from dataclasses import dataclass
from datetime import date


@dataclass
class DynamicDiscountOffer:
    invoice_id: str
    gross_amount_cents: int
    payment_due_date: date
    early_payment_date: date
    apr_pct: float               # Annualised Percentage Rate offered
    discount_amount_cents: int
    net_payment_cents: int
    effective_yield_pct: float   # Annualised return for the buyer
    is_value_accretive: bool     # True if yield > WACC


def compute_dynamic_discount(
    invoice_id: str,
    gross_amount_cents: int,
    payment_due_date: date,
    early_payment_date: date,
    apr_pct: float,
    wacc_pct: float,
) -> DynamicDiscountOffer:
    """
    Compute the discount amount and effective yield for an early payment offer.

    The discount rate is prorated from APR based on the number of days early.
    All monetary amounts remain in integer cents; rounding applied only at output.

    Args:
        invoice_id: Unique invoice identifier.
        gross_amount_cents: Full invoice face value in cents.
        payment_due_date: Contractual due date (ISO 8601).
        early_payment_date: Proposed early settlement date.
        apr_pct: Annualised discount rate offered by the platform (e.g., 8.0 for 8%).
        wacc_pct: Buyer's weighted average cost of capital (e.g., 6.5 for 6.5%).

    Returns:
        DynamicDiscountOffer with discount amount and value-accretive flag.
    """
    days_early = (payment_due_date - early_payment_date).days
    if days_early <= 0:
        raise ValueError("early_payment_date must be before payment_due_date.")

    # Prorated discount rate for this specific period
    period_discount_rate = apr_pct * (days_early / 365) / 100

    discount_cents = round(gross_amount_cents * period_discount_rate)
    net_payment_cents = gross_amount_cents - discount_cents

    # Effective annualised yield: discount / net_payment * (365 / days_early)
    effective_yield_pct = (discount_cents / net_payment_cents) * (365 / days_early) * 100

    return DynamicDiscountOffer(
        invoice_id=invoice_id,
        gross_amount_cents=gross_amount_cents,
        payment_due_date=payment_due_date,
        early_payment_date=early_payment_date,
        apr_pct=apr_pct,
        discount_amount_cents=discount_cents,
        net_payment_cents=net_payment_cents,
        effective_yield_pct=round(effective_yield_pct, 4),
        is_value_accretive=effective_yield_pct > wacc_pct,
    )
```

#### Supply Chain Finance (SCF) Yield Calculation

For reverse factoring programmes (Taulia), the SCF yield represents the annualised return earned by the financing bank or institutional investor:

```
SCF_yield = (face_value - purchase_price) / purchase_price x (365 / days_to_maturity)
```

**Optimal Payment Timing Algorithm:**

1. Rank all outstanding invoices by `(effective_yield_pct - wacc_pct)` descending.
2. Allocate available cash to highest-yield invoices first until cash balance threshold is reached.
3. Route remaining invoices to the Taulia SCF marketplace for supplier-initiated financing.
4. Re-run ranking daily as new invoices arrive and cash position changes.

### 6.4 Inventory Valuation (IAS 2)

IAS 2 (Inventories) requires measurement at the lower of cost and net realisable value (LCNRV). The cost formula must be either FIFO or AVCO (LIFO is prohibited under IFRS).

```python
# python/11_finance_controlling/inventory_valuation/ias2_valuation.py

from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class CostLayer:
    """A single inventory cost layer (FIFO bucket)."""
    receipt_date: str       # ISO 8601
    quantity: float
    unit_cost_cents: int    # per unit, integer cents
    remaining_quantity: float = field(init=False)

    def __post_init__(self) -> None:
        self.remaining_quantity = self.quantity


def fifo_cost_of_goods_sold(
    cost_layers: List[CostLayer],
    units_to_issue: float,
) -> Tuple[int, List[CostLayer]]:
    """
    Consume inventory using FIFO (First In, First Out) cost layer depletion.

    Args:
        cost_layers: Ordered list of cost layers (oldest first).
        units_to_issue: Number of units to consume.

    Returns:
        Tuple of (total COGS in cents, updated cost_layers with depleted quantities).

    Raises:
        ValueError: If insufficient inventory exists across all layers.
    """
    available = sum(layer.remaining_quantity for layer in cost_layers)
    if units_to_issue > available:
        raise ValueError(
            f"Insufficient inventory: requested {units_to_issue}, available {available}"
        )

    total_cogs_cents = 0
    remaining_to_issue = units_to_issue

    for layer in cost_layers:
        if remaining_to_issue <= 0:
            break
        consumed = min(layer.remaining_quantity, remaining_to_issue)
        total_cogs_cents += round(consumed * layer.unit_cost_cents)
        layer.remaining_quantity -= consumed
        remaining_to_issue -= consumed

    return total_cogs_cents, cost_layers


def compute_avco(cost_layers: List[CostLayer]) -> int:
    """
    Compute Average Cost (AVCO) per unit across all layers.

    Returns:
        AVCO unit cost in integer cents.
    """
    total_cost = sum(
        round(layer.remaining_quantity * layer.unit_cost_cents)
        for layer in cost_layers
    )
    total_qty = sum(layer.remaining_quantity for layer in cost_layers)
    if total_qty == 0:
        return 0
    return round(total_cost / total_qty)


def apply_lcnrv(
    cost_per_unit_cents: int,
    net_realisable_value_cents: int,
    quantity: float,
) -> Tuple[int, int]:
    """
    Apply the Lower of Cost or Net Realisable Value rule per IAS 2.34.

    NRV = estimated selling price less estimated costs of completion and selling.

    Args:
        cost_per_unit_cents: Historical cost per unit.
        net_realisable_value_cents: Estimated NRV per unit.
        quantity: Number of units on hand.

    Returns:
        Tuple of (carrying_value_cents, write_down_cents).
        write_down_cents is positive when NRV < cost (impairment required).
    """
    lower_per_unit = min(cost_per_unit_cents, net_realisable_value_cents)
    carrying_value_cents = round(lower_per_unit * quantity)
    cost_value_cents = round(cost_per_unit_cents * quantity)
    write_down_cents = max(0, cost_value_cents - carrying_value_cents)
    return carrying_value_cents, write_down_cents
```

**Step-by-Step Implementation:**

1. On each `StockMovement` event with type `GOODS_ISSUE`, call `fifo_cost_of_goods_sold()` to deplete the oldest layers first.
2. Persist updated cost layers to the `inventory_cost_layers` table with sequence number for event sourcing.
3. Run `apply_lcnrv()` at each month-end for all SKUs with market data available.
4. Where NRV < cost, post a journal entry: Debit `Inventory Write-Down Expense`, Credit `Inventory Reserve`.
5. Reverse write-downs in subsequent periods if NRV recovers (IAS 2.33).

### 6.5 Landed Cost Model

The total landed cost (TLC) captures all costs from the supplier's factory gate to the buyer's warehouse, providing true cost visibility for make-vs-buy and sourcing decisions.

```
TLC = EXW price
    + Freight (ocean/air/road)
    + Insurance (CIF = 0.5% x CIF value)
    + Customs Duty (HS tariff rate x CIF value)
    + Port handling charges
    + Inland freight (last mile)
    + Compliance costs (REACH, UFLPA clearance)
```

```typescript
// src/departments/11-finance-controlling/domain/LandedCostModel.ts

export interface LandedCostInput {
  exwPriceCents: number;           // EXW factory price
  freightCents: number;            // Ocean/air/road freight
  hsTariffRatePct: number;         // Customs duty rate from HS code lookup
  portHandlingCents: number;       // Terminal handling charges
  inlandFreightCents: number;      // Last-mile delivery cost
  complianceCostCents: number;     // REACH, UFLPA, AEO compliance
  insuranceBasisOverride?: number; // Optional: override CIF basis if known
}

export interface LandedCostResult {
  exwPriceCents: number;
  freightCents: number;
  cifValueCents: number;           // EXW + freight (CIF basis)
  insuranceCents: number;          // 0.5% of CIF
  customsDutyCents: number;        // HS rate x CIF
  portHandlingCents: number;
  inlandFreightCents: number;
  complianceCostCents: number;
  totalLandedCostCents: number;
  landedCostMultiplier: number;    // TLC / EXW — useful for supplier comparisons
}

const INSURANCE_RATE = 0.005; // 0.5% of CIF value

export function computeLandedCost(input: LandedCostInput): LandedCostResult {
  const cifValueCents = input.exwPriceCents + input.freightCents;
  const insuranceCents = Math.round(cifValueCents * INSURANCE_RATE);
  const customsDutyCents = Math.round(cifValueCents * (input.hsTariffRatePct / 100));

  const totalLandedCostCents =
    input.exwPriceCents +
    input.freightCents +
    insuranceCents +
    customsDutyCents +
    input.portHandlingCents +
    input.inlandFreightCents +
    input.complianceCostCents;

  const landedCostMultiplier =
    input.exwPriceCents > 0
      ? totalLandedCostCents / input.exwPriceCents
      : 0;

  return {
    exwPriceCents: input.exwPriceCents,
    freightCents: input.freightCents,
    cifValueCents,
    insuranceCents,
    customsDutyCents,
    portHandlingCents: input.portHandlingCents,
    inlandFreightCents: input.inlandFreightCents,
    complianceCostCents: input.complianceCostCents,
    totalLandedCostCents,
    landedCostMultiplier: Math.round(landedCostMultiplier * 10000) / 10000,
  };
}
```

### 6.6 Supply Chain Cost Benchmarking

SC cost as a percentage of revenue is a primary Gartner Supply Chain Top 25 benchmark metric.

```python
# python/11_finance_controlling/benchmarking/sc_cost_benchmarking.py

from dataclasses import dataclass
from typing import Dict, Tuple

INDUSTRY_BENCHMARKS: Dict[str, Dict[str, Tuple[float, float]]] = {
    "retail": {
        "sc_cost_pct_revenue": (4.0, 8.0),    # (world_class, laggard)
        "inventory_turns":     (12.0, 4.0),
        "otif_pct":            (98.0, 88.0),
    },
    "manufacturing": {
        "sc_cost_pct_revenue": (6.0, 12.0),
        "inventory_turns":     (8.0, 3.0),
        "otif_pct":            (97.0, 85.0),
    },
    "food": {
        "sc_cost_pct_revenue": (8.0, 15.0),
        "inventory_turns":     (20.0, 8.0),
        "otif_pct":            (98.5, 90.0),
    },
}


@dataclass
class BenchmarkResult:
    metric: str
    actual_value: float
    world_class: float
    laggard: float
    percentile_estimate: float    # 0-100, higher is better
    gap_to_world_class: float


def benchmark_sc_cost(
    total_sc_cost_cents: int,
    revenue_cents: int,
    industry: str,
) -> BenchmarkResult:
    """
    Benchmark SC cost as a percentage of revenue against industry peers.

    Args:
        total_sc_cost_cents: Fully loaded SC cost (procurement + logistics + WH + quality).
        revenue_cents: Net revenue for the same period.
        industry: 'retail' | 'manufacturing' | 'food'.

    Returns:
        BenchmarkResult with peer comparison and gap to world class.
    """
    if revenue_cents <= 0:
        raise ValueError("Revenue must be positive.")

    actual_pct = (total_sc_cost_cents / revenue_cents) * 100
    benchmarks = INDUSTRY_BENCHMARKS.get(industry, INDUSTRY_BENCHMARKS["manufacturing"])
    wc, laggard = benchmarks["sc_cost_pct_revenue"]

    # Lower cost % is better; invert scale for percentile
    if laggard == wc:
        percentile = 50.0
    else:
        raw = (laggard - actual_pct) / (laggard - wc)
        percentile = max(0.0, min(100.0, raw * 100))

    return BenchmarkResult(
        metric="sc_cost_pct_revenue",
        actual_value=round(actual_pct, 2),
        world_class=wc,
        laggard=laggard,
        percentile_estimate=round(percentile, 1),
        gap_to_world_class=round(actual_pct - wc, 2),
    )
```

### 6.7 ROPA and ROWC (SCOR Asset Management Metrics)

Per SCOR-DS performance attribute AM (Asset Management):

```
ROPA (AM.1.2) = EBIT / Gross PP&E
ROWC (AM.1.3) = EBIT / Working Capital
Working Capital = Current Assets - Current Liabilities
```

```python
# python/11_finance_controlling/asset_management/scor_am_metrics.py

from dataclasses import dataclass


@dataclass
class SCORAssetMetrics:
    ropa_pct: float       # Return on Physical Assets (AM.1.2)
    rowc_pct: float       # Return on Working Capital (AM.1.3)
    working_capital_cents: int
    ebit_cents: int


def compute_scor_am_metrics(
    ebit_cents: int,
    gross_ppe_cents: int,
    current_assets_cents: int,
    current_liabilities_cents: int,
) -> SCORAssetMetrics:
    """
    Compute SCOR-DS Asset Management metrics ROPA (AM.1.2) and ROWC (AM.1.3).

    Args:
        ebit_cents: Earnings Before Interest and Tax for the period.
        gross_ppe_cents: Gross Property, Plant and Equipment (before depreciation).
        current_assets_cents: Total current assets.
        current_liabilities_cents: Total current liabilities.

    Returns:
        SCORAssetMetrics with ROPA and ROWC expressed as percentages.
    """
    working_capital = current_assets_cents - current_liabilities_cents

    ropa = (ebit_cents / gross_ppe_cents * 100) if gross_ppe_cents > 0 else 0.0
    rowc = (ebit_cents / working_capital * 100) if working_capital != 0 else 0.0

    return SCORAssetMetrics(
        ropa_pct=round(ropa, 2),
        rowc_pct=round(rowc, 2),
        working_capital_cents=working_capital,
        ebit_cents=ebit_cents,
    )
```

**Industry Targets:**

| Metric | World Class | Good | Average |
|--------|------------|------|---------|
| ROPA | > 25% | 15-25% | 5-15% |
| ROWC | > 40% | 25-40% | 10-25% |
| C2C days | < 20 | 20-45 | 45-75 |

### 6.8 Transfer Pricing

Transfer pricing governs intercompany transactions (e.g., a procurement hub entity purchasing from suppliers and selling to operating entities at an intercompany price). OECD BEPS Actions 8-10 require that transfer prices reflect the arm's length principle.

**Supported Methods:**

| Method | Code | Best Used For |
|--------|------|--------------|
| Comparable Uncontrolled Price (CUP) | CUP | Commodities, standard products |
| Cost Plus | CP | Manufacturing entities, toll manufacturers |
| Transactional Net Margin Method (TNMM) | TNMM | Distribution entities, routine services |

```typescript
// src/departments/11-finance-controlling/domain/TransferPricing.ts

export type TPMethod = "CUP" | "COST_PLUS" | "TNMM";

export interface TPTransaction {
  readonly id: string;
  readonly sellingEntityId: string;      // GLN of selling legal entity
  readonly buyingEntityId: string;       // GLN of buying legal entity
  readonly productCode: string;          // GS1 GTIN
  readonly method: TPMethod;
  readonly transactionDateISO: string;
  readonly quantityUnits: number;
  readonly unitCostCents: number;        // Seller's cost basis
  readonly markupPct: number;            // Arm's length markup
  readonly intercompanyPriceCents: number;
  readonly bepsDocumentationRef: string; // Country-file / master-file reference
  readonly fiscalYearBenchmarkRef: string; // Benchmarking study reference
}

export function computeCostPlusPrice(
  unitCostCents: number,
  armLengthMarkupPct: number,
): number {
  // Cost Plus: intercompany price = cost x (1 + markup%)
  // Store as integer cents; round half-up
  return Math.round(unitCostCents * (1 + armLengthMarkupPct / 100));
}

export function validateTPArmLengthRange(
  intercompanyPriceCents: number,
  comparablePrices: number[],   // Array of arm's length comparables in cents
  confidenceInterquartileRange: [number, number],  // [25th, 75th] percentile
): { withinRange: boolean; variance: string } {
  const [p25, p75] = confidenceInterquartileRange;
  const withinRange = intercompanyPriceCents >= p25 && intercompanyPriceCents <= p75;
  const midpoint = (p25 + p75) / 2;
  const variancePct = ((intercompanyPriceCents - midpoint) / midpoint) * 100;
  return {
    withinRange,
    variance: `${variancePct > 0 ? "+" : ""}${variancePct.toFixed(1)}% from IQR midpoint`,
  };
}
```

**BEPS Documentation Requirements (OECD 3-Tier Approach):**

1. **Master File** — group-wide TP policy, value chain analysis, intangible assets register.
2. **Local File** — entity-level intercompany transactions, functional analysis, benchmarking study.
3. **Country-by-Country Report (CbCR)** — revenue, profit, tax, and employees by jurisdiction (required for groups with consolidated revenue > EUR 750 million).

### 6.9 Variance Analysis

Variance analysis decomposes the difference between standard and actual COGS into actionable components.

```python
# python/11_finance_controlling/variance_analysis/cogs_variance.py

from dataclasses import dataclass


@dataclass
class COGSVariance:
    """Full COGS variance decomposition."""
    price_variance_cents: int      # (Std Price - Act Price) x Actual Qty
    quantity_variance_cents: int   # (Std Qty - Act Qty) x Std Price
    mix_variance_cents: int        # Product mix shift vs. standard
    total_variance_cents: int      # Sum of all components
    is_favourable: bool            # Negative total = favourable (cost < standard)


def compute_purchase_price_variance(
    standard_price_cents: int,
    actual_price_cents: int,
    actual_quantity: float,
) -> int:
    """
    Price Variance = (Standard Price - Actual Price) x Actual Quantity.

    A positive result is favourable (paid less than standard).

    Args:
        standard_price_cents: Budgeted/standard unit price in cents.
        actual_price_cents: Actual invoiced unit price in cents.
        actual_quantity: Actual units purchased.

    Returns:
        Price variance in cents (positive = favourable).
    """
    return round((standard_price_cents - actual_price_cents) * actual_quantity)


def compute_quantity_variance(
    standard_quantity: float,
    actual_quantity: float,
    standard_price_cents: int,
) -> int:
    """
    Quantity Variance = (Standard Qty - Actual Qty) x Standard Price.

    A positive result is favourable (used less than standard).

    Args:
        standard_quantity: Expected/budgeted quantity.
        actual_quantity: Actual quantity consumed.
        standard_price_cents: Budgeted/standard unit price in cents.

    Returns:
        Quantity variance in cents (positive = favourable).
    """
    return round((standard_quantity - actual_quantity) * standard_price_cents)


def decompose_cogs_variance(
    std_price_cents: int,
    act_price_cents: int,
    std_qty: float,
    act_qty: float,
) -> COGSVariance:
    """Full COGS variance decomposition."""
    pv = compute_purchase_price_variance(std_price_cents, act_price_cents, act_qty)
    qv = compute_quantity_variance(std_qty, act_qty, std_price_cents)
    total = pv + qv
    return COGSVariance(
        price_variance_cents=pv,
        quantity_variance_cents=qv,
        mix_variance_cents=0,   # Extended in multi-SKU version
        total_variance_cents=total,
        is_favourable=total >= 0,
    )
```

### 6.10 Activity-Based Costing (ABC)

ABC allocates overhead costs to products based on the activities that consume resources, replacing the distortions of volume-based absorption costing.

```python
# python/11_finance_controlling/abc_costing/activity_based_costing.py

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class CostPool:
    name: str
    total_cost_cents: int
    cost_driver: str        # e.g., "pick_lines", "po_lines", "inspection_hours"
    total_driver_units: float


@dataclass
class ABCAllocation:
    product_id: str
    cost_pool_name: str
    driver_units_consumed: float
    allocated_cost_cents: int
    abc_rate_cents_per_unit: float


def compute_abc_rate(pool: CostPool) -> float:
    """
    Compute the ABC overhead rate for a cost pool.

    ABC Rate = Total Cost Pool / Total Cost Driver Units

    Args:
        pool: CostPool with total cost and driver volumes.

    Returns:
        Rate in cents per driver unit.
    """
    if pool.total_driver_units <= 0:
        raise ValueError(f"Cost pool '{pool.name}' has zero driver units.")
    return pool.total_cost_cents / pool.total_driver_units


def allocate_abc_costs(
    cost_pools: List[CostPool],
    product_driver_consumption: Dict[str, Dict[str, float]],
) -> List[ABCAllocation]:
    """
    Allocate cost pools to products based on driver consumption.

    Args:
        cost_pools: List of cost pools with rates.
        product_driver_consumption: {product_id: {cost_driver: units_consumed}}.

    Returns:
        List of ABCAllocation records with allocated costs per product per pool.
    """
    allocations = []
    for pool in cost_pools:
        rate = compute_abc_rate(pool)
        for product_id, drivers in product_driver_consumption.items():
            consumed = drivers.get(pool.cost_driver, 0.0)
            allocated = round(consumed * rate)
            allocations.append(ABCAllocation(
                product_id=product_id,
                cost_pool_name=pool.name,
                driver_units_consumed=consumed,
                allocated_cost_cents=allocated,
                abc_rate_cents_per_unit=round(rate, 4),
            ))
    return allocations
```

**Standard SC Cost Drivers:**

| Cost Pool | Driver | Typical Rate |
|-----------|--------|-------------|
| Procurement overhead | PO lines processed | $12-25 per PO line |
| Inbound quality inspection | Inspection hours | $45-80 per hour |
| Warehouse pick-and-pack | Pick lines | $1.50-3.50 per line |
| Outbound logistics | Shipments dispatched | $15-40 per shipment |
| Supplier management | Supplier scorecards | $200-500 per scorecard |

---

## 7. Phase 4: ML/AI Pipeline

**Duration:** 12 weeks
**Deliverables:** Trained models, inference API, explainability reports, monitoring dashboards

### 7.1 XGBoost Invoice Fraud Detection

Invoice fraud costs global enterprises approximately 1 percent of annual revenues. The XGBoost classifier enables real-time scoring of incoming invoices before payment approval.

**Feature Engineering:**

| Feature | Type | Description |
|---------|------|-------------|
| `duplicate_hash_flag` | Binary | SHA-256 hash match against past 180 days |
| `amount_vs_vendor_zscore` | Float | Z-score of amount vs. vendor 12-month baseline |
| `days_since_last_invoice` | Integer | Invoice frequency anomaly detection |
| `is_new_vendor` | Binary | First invoice within 90 days of vendor creation |
| `new_vendor_high_amount` | Binary | New vendor AND amount > 95th percentile |
| `payment_term_mismatch` | Binary | Invoice terms differ from PO master terms |
| `weekend_submission` | Binary | Invoice received Saturday or Sunday |
| `bank_account_changed` | Binary | Vendor bank details changed within 30 days |
| `round_number_amount` | Binary | Amount is exact round number (fraud signal) |

```python
# python/11_finance_controlling/ml/invoice_fraud_detection.py

import hashlib
import numpy as np
import pandas as pd
import xgboost as xgb
import shap
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.preprocessing import StandardScaler
from typing import Tuple, Dict, Any


FRAUD_THRESHOLD = 0.7   # Classification threshold per business rule


def create_invoice_hash(
    vendor_id: str,
    invoice_number: str,
    amount_cents: int,
    currency: str,
) -> str:
    """Create a deterministic hash for duplicate invoice detection."""
    raw = f"{vendor_id}|{invoice_number}|{amount_cents}|{currency}"
    return hashlib.sha256(raw.encode()).hexdigest()


def engineer_fraud_features(
    df: pd.DataFrame,
    vendor_baselines: pd.DataFrame,
    past_hashes: set,
) -> pd.DataFrame:
    """
    Engineer fraud detection features from raw invoice data.

    Args:
        df: Raw invoice DataFrame with columns: vendor_id, invoice_number,
            gross_amount_cents, currency_code, invoice_date, payment_term_code,
            po_payment_term_code, vendor_created_date, bank_account_changed_date.
        vendor_baselines: Historical vendor-level stats (mean, std of amounts).
        past_hashes: Set of known invoice SHA-256 hashes.

    Returns:
        Feature DataFrame ready for XGBoost inference.
    """
    features = pd.DataFrame()

    # Duplicate hash detection
    features["duplicate_hash_flag"] = df.apply(
        lambda r: int(create_invoice_hash(
            r["vendor_id"], r["invoice_number"],
            r["gross_amount_cents"], r["currency_code"]
        ) in past_hashes),
        axis=1,
    )

    # Amount vs vendor baseline z-score
    merged = df.merge(vendor_baselines, on="vendor_id", how="left")
    std_safe = merged["amount_std_cents"].replace(0, np.nan)
    features["amount_vs_vendor_zscore"] = (
        (merged["gross_amount_cents"] - merged["amount_mean_cents"]) / std_safe
    ).fillna(0)

    # New vendor flag (vendor created within 90 days of invoice date)
    df["invoice_date"] = pd.to_datetime(df["invoice_date"])
    df["vendor_created_date"] = pd.to_datetime(df["vendor_created_date"])
    features["is_new_vendor"] = (
        (df["invoice_date"] - df["vendor_created_date"]).dt.days < 90
    ).astype(int)

    # New vendor + high amount
    p95 = df["gross_amount_cents"].quantile(0.95)
    features["new_vendor_high_amount"] = (
        (features["is_new_vendor"] == 1) & (df["gross_amount_cents"] > p95)
    ).astype(int)

    # Payment term mismatch
    features["payment_term_mismatch"] = (
        df["payment_term_code"] != df["po_payment_term_code"]
    ).astype(int)

    # Weekend submission
    features["weekend_submission"] = (
        df["invoice_date"].dt.dayofweek >= 5
    ).astype(int)

    # Bank account recently changed
    df["bank_account_changed_date"] = pd.to_datetime(
        df["bank_account_changed_date"], errors="coerce"
    )
    features["bank_account_changed"] = (
        (df["invoice_date"] - df["bank_account_changed_date"]).dt.days < 30
    ).fillna(False).astype(int)

    # Round number amount (multiple of 10,000 cents = $100)
    features["round_number_amount"] = (
        df["gross_amount_cents"] % 10000 == 0
    ).astype(int)

    return features


def train_fraud_detector(
    X: pd.DataFrame,
    y: pd.Series,
) -> Tuple[xgb.XGBClassifier, shap.Explainer]:
    """
    Train XGBoost fraud classifier with 5-fold cross-validation and SHAP explainability.

    Args:
        X: Feature matrix from engineer_fraud_features().
        y: Binary label (1 = fraud, 0 = legitimate).

    Returns:
        Tuple of (trained classifier, SHAP TreeExplainer).
    """
    model = xgb.XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=(y == 0).sum() / (y == 1).sum(),  # handle class imbalance
        use_label_encoder=False,
        eval_metric="auc",
        random_state=42,
    )

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    auc_scores = []
    for fold, (train_idx, val_idx) in enumerate(skf.split(X, y)):
        X_tr, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_tr, y_val = y.iloc[train_idx], y.iloc[val_idx]
        model.fit(X_tr, y_tr, eval_set=[(X_val, y_val)], verbose=False)
        preds = model.predict_proba(X_val)[:, 1]
        auc = roc_auc_score(y_val, preds)
        auc_scores.append(auc)

    print(f"CV AUC: {np.mean(auc_scores):.4f} ± {np.std(auc_scores):.4f}")

    # Retrain on full dataset
    model.fit(X, y)
    explainer = shap.TreeExplainer(model)
    return model, explainer


def score_invoice(
    model: xgb.XGBClassifier,
    explainer: shap.Explainer,
    features: pd.DataFrame,
) -> Dict[str, Any]:
    """
    Score a single invoice and return fraud probability with SHAP explanation.

    Args:
        model: Trained XGBoost classifier.
        explainer: SHAP TreeExplainer for the model.
        features: Single-row feature DataFrame.

    Returns:
        Dict with fraud_score, decision, and top SHAP contributors.
    """
    fraud_prob = float(model.predict_proba(features)[0, 1])
    decision = "HOLD_FOR_REVIEW" if fraud_prob >= FRAUD_THRESHOLD else "CLEAR"

    shap_values = explainer.shap_values(features)
    feature_names = features.columns.tolist()
    contributions = sorted(
        zip(feature_names, shap_values[0]),
        key=lambda x: abs(x[1]),
        reverse=True,
    )

    return {
        "fraud_score": round(fraud_prob, 4),
        "decision": decision,
        "threshold": FRAUD_THRESHOLD,
        "top_contributors": [
            {"feature": f, "shap_value": round(v, 4)}
            for f, v in contributions[:5]
        ],
    }
```

**Step-by-Step Deployment:**

1. Extract 24 months of confirmed fraud labels from accounts payable audit records.
2. Run `engineer_fraud_features()` to build the training dataset.
3. Train with `train_fraud_detector()` — target CV AUC > 0.92.
4. Wrap the model in a FastAPI inference endpoint, containerised with Docker.
5. Subscribe the inference service to the Kafka topic `invoice.received`.
6. For each invoice: if `fraud_score >= 0.7`, emit `InvoiceFraudAlert` and create a BlackLine task.
7. Retrain monthly on labelled feedback from the AP exception queue.

### 7.2 LSTM for Working Capital Forecasting

A Long Short-Term Memory (LSTM) network captures the temporal dependencies in AR, AP, and inventory balances to generate a 90-day rolling cash requirement forecast.

```python
# python/11_finance_controlling/ml/working_capital_lstm.py

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, TensorDataset
from typing import Tuple


class WorkingCapitalLSTM(nn.Module):
    """
    LSTM model for 90-day working capital forecasting.

    Input: 24-month rolling window of [AR, AP, Inventory, Revenue, COGS] daily values.
    Output: 90-day forward cash requirement in cents.
    """

    def __init__(
        self,
        input_size: int = 5,
        hidden_size: int = 128,
        num_layers: int = 2,
        dropout: float = 0.2,
        forecast_horizon: int = 90,
    ) -> None:
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_size,
            hidden_size=hidden_size,
            num_layers=num_layers,
            dropout=dropout,
            batch_first=True,
        )
        self.fc = nn.Linear(hidden_size, forecast_horizon)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        lstm_out, _ = self.lstm(x)
        # Take the last time step hidden state for forecasting
        return self.fc(lstm_out[:, -1, :])


def prepare_sequences(
    df: pd.DataFrame,
    sequence_length: int = 720,  # 24 months x 30 days
    forecast_horizon: int = 90,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Prepare sliding-window sequences for LSTM training.

    Args:
        df: Daily DataFrame with columns [ar_cents, ap_cents, inventory_cents,
            revenue_cents, cogs_cents].
        sequence_length: Look-back window in days (720 = 24 months).
        forecast_horizon: Forecast horizon in days (90).

    Returns:
        Tuple of (X sequences, y targets) as numpy arrays.
    """
    feature_cols = ["ar_cents", "ap_cents", "inventory_cents", "revenue_cents", "cogs_cents"]
    data = df[feature_cols].values

    # Normalise to [0, 1] per column (store scaler parameters for inverse transform)
    col_maxes = data.max(axis=0)
    col_maxes[col_maxes == 0] = 1   # avoid division by zero
    data_norm = data / col_maxes

    X, y = [], []
    for i in range(len(data_norm) - sequence_length - forecast_horizon + 1):
        X.append(data_norm[i : i + sequence_length])
        # Target: cash requirement = AR - AP - Inventory (working capital need)
        future_ar = data[i + sequence_length : i + sequence_length + forecast_horizon, 0]
        future_ap = data[i + sequence_length : i + sequence_length + forecast_horizon, 1]
        future_inv = data[i + sequence_length : i + sequence_length + forecast_horizon, 2]
        cash_req = (future_ar - future_ap - future_inv) / col_maxes[0]
        y.append(cash_req)

    return np.array(X, dtype=np.float32), np.array(y, dtype=np.float32)
```

**Step-by-Step Implementation:**

1. Load 36 months of daily GL balance extracts (AR, AP, Inventory, Revenue, COGS).
2. Impute missing days using forward-fill; flag weekends and public holidays as features.
3. Train the LSTM with AdamW optimiser, learning rate 1e-3, early stopping on validation MAE.
4. Deploy the model as a scheduled inference job running nightly.
5. Each morning, publish a `WorkingCapitalForecast90D` event to the finance event stream.
6. The CFO dashboard displays the P10/P50/P90 confidence intervals for the 90-day forecast.
7. Retrain quarterly with the latest actuals to prevent concept drift.

### 7.3 NLP for Invoice Data Extraction

Automated invoice data extraction eliminates manual keying errors and accelerates the 3-way match cycle.

```python
# python/11_finance_controlling/ml/invoice_nlp_extraction.py

import re
import pdfplumber
import pytesseract
from PIL import Image
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification


@dataclass
class ExtractedInvoice:
    """Structured invoice data extracted from an unstructured PDF."""
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None        # ISO 8601
    vendor_name: Optional[str] = None
    vendor_vat_number: Optional[str] = None
    gross_amount_str: Optional[str] = None    # String before currency parsing
    currency_code: Optional[str] = None
    po_number: Optional[str] = None
    line_items: List[dict] = field(default_factory=list)
    extraction_confidence: float = 0.0
    validation_errors: List[str] = field(default_factory=list)


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a PDF invoice using pdfplumber (native) with
    pytesseract OCR fallback for scanned documents.

    Args:
        pdf_path: Absolute path to the PDF file.

    Returns:
        Extracted plain text from all pages.
    """
    text_parts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text and len(page_text.strip()) > 50:
                text_parts.append(page_text)
            else:
                # Fallback to OCR for scanned pages
                img = page.to_image(resolution=300).original
                ocr_text = pytesseract.image_to_string(img, config="--psm 6")
                text_parts.append(ocr_text)
    return "\n".join(text_parts)


def validate_extraction(invoice: ExtractedInvoice, po_master: dict) -> ExtractedInvoice:
    """
    Validate extracted invoice fields against the PO master record.

    Args:
        invoice: Extracted invoice data.
        po_master: PO master data dict with keys: po_number, vendor_id, amount_cents.

    Returns:
        ExtractedInvoice with validation_errors populated.
    """
    errors = []

    if not invoice.invoice_number:
        errors.append("Invoice number not extracted.")

    if not invoice.invoice_date:
        errors.append("Invoice date not extracted.")
    else:
        if not re.match(r"\d{4}-\d{2}-\d{2}", invoice.invoice_date):
            errors.append(f"Invoice date format invalid: {invoice.invoice_date}")

    if invoice.po_number and invoice.po_number != po_master.get("po_number"):
        errors.append(
            f"PO number mismatch: extracted '{invoice.po_number}', "
            f"master '{po_master.get('po_number')}'."
        )

    invoice.validation_errors = errors
    invoice.extraction_confidence = max(0.0, 1.0 - len(errors) * 0.2)
    return invoice
```

**Step-by-Step Implementation:**

1. Configure an S3-compatible object store (MinIO) to receive uploaded invoice PDFs.
2. On upload, trigger the `extract_text_from_pdf()` pipeline via a Kafka consumer.
3. Apply a fine-tuned LayoutLM model (Hugging Face `microsoft/layoutlmv3-base`) for structured field extraction.
4. Run `validate_extraction()` against the PO master database.
5. Confidence >= 0.85: route to 3-way match pipeline automatically.
6. Confidence < 0.85: route to manual review queue with pre-filled fields.
7. Capture human corrections as labelled training data for quarterly model fine-tuning.

### 7.4 Anomaly Detection for GL Posting Errors

Isolation Forest detects statistically anomalous journal entries that may indicate control failures, posting errors, or fraud.

```python
# python/11_finance_controlling/ml/gl_anomaly_detection.py

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder, StandardScaler
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class GLAnomalyResult:
    journal_entry_id: str
    anomaly_score: float        # Negative: more anomalous; positive: normal
    is_anomaly: bool            # True if score < contamination threshold
    anomalous_features: List[str]


def engineer_gl_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineer features for GL journal entry anomaly detection.

    Expected input columns: journal_entry_id, amount_cents, gl_account_code,
        user_id, posted_at (timestamp), posting_frequency_30d.

    Args:
        df: Raw journal entry DataFrame.

    Returns:
        Numeric feature matrix for Isolation Forest.
    """
    features = pd.DataFrame()

    # Amount features
    features["log_abs_amount"] = np.log1p(df["amount_cents"].abs())
    features["is_negative"] = (df["amount_cents"] < 0).astype(int)
    features["is_round_amount"] = (df["amount_cents"] % 100000 == 0).astype(int)

    # Temporal features
    df["posted_at"] = pd.to_datetime(df["posted_at"])
    features["hour_of_day"] = df["posted_at"].dt.hour
    features["day_of_week"] = df["posted_at"].dt.dayofweek
    features["is_weekend"] = (df["posted_at"].dt.dayofweek >= 5).astype(int)
    features["is_month_end"] = (df["posted_at"].dt.day >= 28).astype(int)

    # User behaviour
    user_enc = LabelEncoder()
    features["user_encoded"] = user_enc.fit_transform(df["user_id"].astype(str))
    features["posting_frequency_30d"] = df["posting_frequency_30d"].fillna(0)

    # GL account encoding
    acct_enc = LabelEncoder()
    features["account_encoded"] = acct_enc.fit_transform(
        df["gl_account_code"].astype(str)
    )

    return features


def train_gl_anomaly_detector(
    features: pd.DataFrame,
    contamination: float = 0.02,   # Expected 2% error rate in GL postings
) -> IsolationForest:
    """
    Train Isolation Forest for GL anomaly detection.

    Args:
        features: Numeric feature matrix from engineer_gl_features().
        contamination: Expected proportion of anomalies in the training data.

    Returns:
        Fitted IsolationForest model.
    """
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(features)

    model = IsolationForest(
        n_estimators=200,
        contamination=contamination,
        max_samples="auto",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X_scaled)
    return model


def score_journal_entries(
    model: IsolationForest,
    features: pd.DataFrame,
    journal_entry_ids: List[str],
) -> List[GLAnomalyResult]:
    """Score journal entries and flag anomalies for controller review."""
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(features)

    scores = model.decision_function(X_scaled)
    predictions = model.predict(X_scaled)   # -1 = anomaly, 1 = normal

    results = []
    for i, jeid in enumerate(journal_entry_ids):
        is_anomaly = predictions[i] == -1
        # Identify which features are most anomalous
        anomalous = []
        if is_anomaly:
            feature_values = features.iloc[i]
            for col in features.columns:
                col_mean = features[col].mean()
                col_std = features[col].std()
                if col_std > 0 and abs((feature_values[col] - col_mean) / col_std) > 2.5:
                    anomalous.append(col)
        results.append(GLAnomalyResult(
            journal_entry_id=jeid,
            anomaly_score=round(float(scores[i]), 4),
            is_anomaly=is_anomaly,
            anomalous_features=anomalous,
        ))
    return results
```

---

## 8. Phase 5: Integration and Automation

**Duration:** 10 weeks
**Deliverables:** Certified integration adapters, reconciliation automation, payment execution

### 8.1 SAP FI/CO Integration

SAP S/4HANA is the system of record for all statutory financial data. Integration uses SAP OData APIs and RFC BAPIs.

```typescript
// src/departments/11-finance-controlling/integrations/SAPFIAdapter.ts

import axios, { AxiosInstance } from "axios";

export interface SAPJournalEntry {
  companyCode: string;
  postingDate: string;          // YYYYMMDD (SAP format)
  documentType: string;         // "SA" = GL posting, "KR" = vendor invoice
  reference: string;
  headerText: string;
  lineItems: SAPLineItem[];
}

export interface SAPLineItem {
  glAccount: string;
  debitCreditIndicator: "S" | "H";   // S = debit (Soll), H = credit (Haben)
  amountInDocCurrency: number;        // SAP uses decimal; we convert from cents
  currency: string;
  costCenter: string;
  profitCenter: string;
  assignment: string;                 // PO number / cost reference
  itemText: string;
}

export class SAPFIAdapter {
  private readonly client: AxiosInstance;
  private readonly baseUrl: string;

  constructor(baseUrl: string, username: string, password: string) {
    this.baseUrl = baseUrl;
    this.client = axios.create({
      baseURL: baseUrl,
      auth: { username, password },
      headers: { "Content-Type": "application/json", "sap-client": "100" },
      timeout: 30_000,
    });
  }

  async postJournalEntry(entry: SAPJournalEntry): Promise<string> {
    // Convert cent amounts to SAP decimal format
    const payload = {
      ...entry,
      lineItems: entry.lineItems.map(li => ({
        ...li,
        amountInDocCurrency: li.amountInDocCurrency / 100,
      })),
    };
    const response = await this.client.post(
      "/sap/opu/odata/sap/API_JOURNALENTRYCREATEREQUEST_BATCH_SRV/",
      payload,
    );
    return response.data.documentNumber;
  }

  async getCostCenterActuals(
    costCenter: string,
    fiscalYear: string,
    period: string,
  ): Promise<{ totalActualCents: number }> {
    const response = await this.client.get(
      `/sap/opu/odata/sap/API_COSTCENTER_SRV/CostCenterActuals`,
      { params: { costCenter, fiscalYear, period } },
    );
    const amountDecimal = response.data.d.results[0]?.totalActual ?? 0;
    return { totalActualCents: Math.round(amountDecimal * 100) };
  }
}
```

### 8.2 Oracle Financials Integration

Oracle Financials Cloud is used for AP/AR subledger management in specific regional entities.

**Integration points:**
- AP Invoice Import: REST API `POST /fscmRestApi/resources/11.13.18.05/payablesInvoices`
- AR Invoice Query: REST API `GET /fscmRestApi/resources/11.13.18.05/receivablesInvoices`
- Asset Accounting: Fixed asset addition via Oracle Assets REST API.

### 8.3 Coupa Pay Dynamic Discounting

Coupa Pay provides a marketplace for buyer-funded dynamic discounting. Suppliers opt in to early payment in exchange for a discount calculated using the formula in Section 6.3.

**Integration flow:**
1. 3-way match clears with `AUTO_APPROVE` decision.
2. Compute `DynamicDiscountOffer` via `compute_dynamic_discount()`.
3. If `is_value_accretive`, push offer to Coupa Pay via REST API: `POST /api/dynamic_discounts`.
4. Supplier accepts or declines in Coupa Pay supplier portal.
5. On acceptance, trigger payment instruction to the bank with reduced net amount.
6. Post discount to GL: Debit `AP`, Credit `Cash`, Credit `Discount Income`.

### 8.4 Taulia Supply Chain Finance

Taulia enables supplier-initiated early payment by connecting institutional funders. Unlike dynamic discounting (buyer-funded), SCF is funder-funded, releasing the buyer's cash.

**SCF yield calculation:**

```python
def compute_scf_yield(
    face_value_cents: int,
    purchase_price_cents: int,
    days_to_maturity: int,
) -> float:
    """
    Compute the annualised SCF yield for an investor on the Taulia marketplace.

    SCF Yield = (face_value - purchase_price) / purchase_price x (365 / days_to_maturity)
    """
    if purchase_price_cents <= 0 or days_to_maturity <= 0:
        raise ValueError("Purchase price and days to maturity must be positive.")
    discount = face_value_cents - purchase_price_cents
    yield_pct = (discount / purchase_price_cents) * (365 / days_to_maturity) * 100
    return round(yield_pct, 4)
```

### 8.5 BlackLine Account Reconciliation

BlackLine automates GL account reconciliation and intercompany matching, replacing spreadsheet-driven month-end closes.

**Automated reconciliation rules:**
- Bank reconciliation: Match SWIFT MT940/CAMT.053 bank statements against GL cash accounts daily.
- Intercompany matching: Auto-match intercompany transactions via `INTERCOMPANY_CLEARING` account (GL 19000).
- Variance threshold: Auto-certify reconciliations with unexplained variance < $500 and < 0.01%.

### 8.6 SWIFT/SEPA Payment Execution

All high-value payments use SWIFT; EU domestic payments use SEPA Credit Transfer.

**MT940 Bank Statement Reconciliation:**

```typescript
// src/departments/11-finance-controlling/integrations/SWIFTAdapter.ts

export interface MT940Statement {
  accountNumber: string;
  statementDate: string;     // ISO 8601
  openingBalanceCents: number;
  closingBalanceCents: number;
  transactions: MT940Transaction[];
}

export interface MT940Transaction {
  valueDate: string;
  entryDate: string;
  debitCredit: "D" | "C";
  amountCents: number;
  swiftCode: string;         // e.g., "NCHGD" for charges
  reference: string;
  counterpartyName: string;
}

export function parseMT940(rawMT940: string): MT940Statement {
  // Parse SWIFT MT940 format into structured TypeScript object.
  // Full parsing implementation omitted for brevity — use swift-parser library.
  throw new Error("Implement MT940 parser or use swift-parser npm package.");
}

export function reconcileBankStatement(
  statement: MT940Statement,
  glTransactions: { amountCents: number; reference: string; date: string }[],
): { matched: number; unmatched: MT940Transaction[] } {
  const matched = new Set<string>();
  const unmatched: MT940Transaction[] = [];

  for (const bankTxn of statement.transactions) {
    const glMatch = glTransactions.find(
      gl =>
        gl.amountCents === (bankTxn.debitCredit === "C" ? bankTxn.amountCents : -bankTxn.amountCents) &&
        gl.reference === bankTxn.reference
    );
    if (glMatch) {
      matched.add(bankTxn.reference);
    } else {
      unmatched.push(bankTxn);
    }
  }

  return { matched: matched.size, unmatched };
}
```

### 8.7 IFRS/GAAP Reporting

| Standard | Requirement | Implementation |
|----------|-------------|---------------|
| IAS 2 | Inventory at LCNRV, FIFO or AVCO | `ias2_valuation.py` (Section 6.4) |
| IAS 7 | Cash flow statement, operating/investing/financing | GL classification tags on all accounts |
| IFRS 15 | Revenue recognised when performance obligation satisfied | SOB (Statement of Balance) trigger on delivery event |
| ASC 330 | US GAAP LIFO reserve disclosure (US entities only) | Separate LIFO layer tracking in US sub-ledger |
| IAS 21 | Foreign currency translation at closing rate | Nightly FX rate feed from ECB/Bloomberg |
| IAS 36 | Impairment of non-financial assets | Annual PP&E impairment test pipeline |

---

## 9. Phase 6: Continuous Improvement

**Duration:** Ongoing (post-implementation)
**Deliverables:** Monthly Kaizen reviews, model drift reports, KPI trend dashboards

### 9.1 Financial Close Acceleration Roadmap

| Milestone | Current State | 6-Month Target | 12-Month Target |
|-----------|-------------|----------------|-----------------|
| Month-end close duration | 8 days | 5 days | 3 days |
| 3-way match automation rate | 40% | 75% | 92% |
| Reconciliation items auto-certified | 30% | 65% | 85% |
| Intercompany eliminations manual effort | 40 hours | 15 hours | 4 hours |

### 9.2 Model Monitoring and Retraining

```python
# python/11_finance_controlling/monitoring/model_drift.py

import pandas as pd
import numpy as np
from scipy import stats


def detect_feature_drift(
    reference_df: pd.DataFrame,
    production_df: pd.DataFrame,
    psi_threshold: float = 0.2,
) -> dict:
    """
    Detect feature drift using Population Stability Index (PSI).

    PSI < 0.1: No significant drift.
    PSI 0.1-0.2: Moderate drift — monitor.
    PSI > 0.2: Significant drift — retrain required.
    """
    psi_results = {}
    for col in reference_df.columns:
        ref_vals = reference_df[col].dropna()
        prod_vals = production_df[col].dropna()
        bins = np.percentile(ref_vals, np.linspace(0, 100, 11))
        bins = np.unique(bins)
        ref_pct, _ = np.histogram(ref_vals, bins=bins)
        prod_pct, _ = np.histogram(prod_vals, bins=bins)
        ref_pct = ref_pct / ref_pct.sum() + 1e-8
        prod_pct = prod_pct / prod_pct.sum() + 1e-8
        psi = np.sum((prod_pct - ref_pct) * np.log(prod_pct / ref_pct))
        psi_results[col] = {
            "psi": round(float(psi), 4),
            "action": "RETRAIN" if psi > psi_threshold else "MONITOR" if psi > 0.1 else "OK",
        }
    return psi_results
```

---

## 10. Technology Stack and Architecture

### 10.1 Architecture Overview

```
                        Event Bus (Apache Kafka)
                               |
          +--------------------+---------------------+
          |                    |                     |
   Procurement Events    Inventory Events     Logistics Events
   (PO, GRN, Invoice)   (Movements, Lots)   (Shipments, Duty)
          |                    |                     |
          +--------------------+---------------------+
                               |
                  Finance Controlling Domain
                               |
          +--------------------+---------------------+
          |                    |                     |
   3-Way Match Engine    Working Capital       Landed Cost
   (TypeScript)          (Python LSTM)         (TypeScript)
          |                    |                     |
          +--------------------+---------------------+
                               |
               Financial Event Store (PostgreSQL)
                               |
          +--------------------+---------------------+
          |                    |                     |
     SAP FI/CO           Oracle Financials      BlackLine
     (ERP system)        (Subledger)            (Reconciliation)
          |                    |                     |
          +--------------------+---------------------+
                               |
               IFRS/GAAP Reporting Layer
```

### 10.2 Data Flow Architecture

All financial events are immutable. The event store supports full audit trail replay, which is mandatory for IFRS and SOX compliance.

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Event ingestion | Apache Kafka 3.6 | Real-time financial event streaming |
| Domain logic | TypeScript 5.4 | Business rules, validation, aggregates |
| Mathematical models | Python 3.11 | C2C, LCNRV, variance, ABC |
| ML inference | PyTorch + XGBoost | Fraud detection, WC forecasting |
| Event store | PostgreSQL 15 JSONB | Immutable financial audit log |
| Cache / state | Redis 7.2 | 3-way match correlation store |
| ERP integration | SAP OData / Oracle REST | Bi-directional GL posting |
| Reconciliation | BlackLine API | Automated account certification |
| Payments | SWIFT / SEPA | Payment execution and reconciliation |
| Reporting | Grafana + dbt | KPI dashboards and financial reports |

---

## 11. Change Management and Training

### 11.1 Stakeholder Matrix

| Stakeholder Group | Impact | Engagement Strategy | Training Format |
|------------------|--------|--------------------|--------------------|
| AP/AR Clerks | High | Process redesign workshops | Hands-on system training (8h) |
| Financial Controllers | High | Co-design sessions | Advanced analytics training (16h) |
| Procurement Managers | Medium | Integration briefings | PO-to-payment process training (4h) |
| CFO / Treasury | High | Executive steering committee | KPI dashboard walkthrough (2h) |
| IT / Basis Team | High | Technical design reviews | System administration training (24h) |
| Internal Audit | Medium | Control framework review | Audit trail and evidence packs (4h) |
| External Auditors | Low | Observation sessions | Model documentation review |

### 11.2 Training Curriculum

| Module | Duration | Audience | Delivery |
|--------|----------|----------|----------|
| P2P Process Redesign | 4 hours | AP Team | Instructor-led |
| 3-Way Match Exception Handling | 2 hours | AP Team | E-learning |
| Working Capital Dashboard | 3 hours | Finance Controllers | Workshop |
| Transfer Pricing Documentation | 4 hours | Tax & Finance | Instructor-led |
| ML Model Interpretation (SHAP) | 2 hours | Finance Analytics | Workshop |
| BlackLine Reconciliation | 4 hours | Close Team | Hands-on lab |
| IFRS Reporting Module | 6 hours | Reporting Team | Instructor-led |

### 11.3 Resistance Management

Common resistance patterns and mitigations:

1. **"The system doesn't understand our exceptions."** — Mitigation: exception queue with human override capability; every auto-decision is explainable and reversible.
2. **"Transfer pricing rules are too rigid."** — Mitigation: parameterisable markup tables per method and country; TP policy engine separate from enforcement engine.
3. **"We don't trust the ML fraud score."** — Mitigation: SHAP explainability for every score; 90-day parallel-run period with human override tracking.

---

## 12. Implementation KPIs

### 12.1 Financial Process KPIs

| KPI | Baseline | 6-Month Target | 12-Month Target | SCOR Reference |
|-----|---------|----------------|-----------------|----------------|
| 3-way match automation rate | 40% | 75% | 92% | EP.07 |
| Invoice processing cost per invoice | $12.50 | $8.00 | $4.50 | EP.07 |
| Cash-to-Cash cycle (days) | 52 days | 44 days | 38 days | AM.1.1 |
| Days Payable Outstanding | 32 days | 42 days | 50 days | AM.1.3 |
| Days Sales Outstanding | 48 days | 40 days | 35 days | AM.1.3 |
| Days Inventory Outstanding | 36 days | 32 days | 28 days | AM.1.2 |
| Invoice fraud detection precision | N/A | 88% | 95% | EP.07 |
| Month-end close duration | 8 days | 5 days | 3 days | EP.08 |
| Working capital forecast MAPE | N/A | 15% | 8% | EP.08 |
| Intercompany elimination errors | 45/month | 15/month | < 3/month | EP.10 |
| Transfer pricing documentation coverage | 60% | 85% | 100% | EP.10 |
| SC cost as % of revenue | 9.8% | 8.5% | 7.2% | AM.1.1 |
| ROPA (Return on Physical Assets) | 12% | 16% | 20% | AM.1.2 |
| ROWC (Return on Working Capital) | 18% | 26% | 34% | AM.1.3 |
| GL anomaly false positive rate | N/A | < 15% | < 8% | EP.09 |

### 12.2 Technical KPIs

| KPI | Target |
|-----|--------|
| Invoice fraud model CV AUC | > 0.92 |
| Working capital LSTM MAPE | < 10% at 30 days, < 18% at 90 days |
| NLP invoice extraction accuracy | > 95% for mandatory fields |
| GL anomaly Isolation Forest AUC | > 0.85 |
| 3-way match engine latency | < 200ms p99 |
| SAP integration uptime | > 99.5% |
| Event store replay capability | Full replay in < 4 hours |

---

## 13. Risk and Mitigation

### 13.1 Risk Register

| Risk ID | Risk Description | Probability | Impact | Score | Mitigation | Owner |
|---------|----------------|-------------|--------|-------|-----------|-------|
| R-01 | SAP integration delays due to BASIS resource constraints | High | High | 16 | Engage SAP partner for dedicated BASIS support; pre-book installation windows | IT Director |
| R-02 | Data quality issues prevent 3-way match automation | High | High | 16 | Phase 0 data quality assessment; mandatory data cleansing sprint before go-live | Data Governance Lead |
| R-03 | Transfer pricing model challenged by tax authority | Medium | Critical | 15 | Engage Big-4 TP specialist; contemporaneous documentation from Day 1 | CFO / Tax Director |
| R-04 | ML fraud model generates high false positive rate | Medium | High | 12 | Parallel-run period; SHAP explainability; manual override tracking | Finance Analytics Lead |
| R-05 | IFRS 15 revenue recognition timing errors | Low | Critical | 12 | Automated performance obligation checklist tied to delivery events | Financial Controller |
| R-06 | SWIFT connectivity disruption | Low | High | 8 | Redundant SWIFT Service Bureau; SEPA fallback for EUR payments | Treasury Manager |
| R-07 | Taulia SCF programme take-up lower than forecast | Medium | Medium | 9 | Supplier onboarding campaign; dedicated supplier success manager | Procurement Director |
| R-08 | LSTM model concept drift in economic downturn | Low | Medium | 6 | Quarterly retraining; PSI drift monitoring; manual override capability | Finance Analytics Lead |

### 13.2 Control Framework

All financial controls must be documented in the Internal Control Matrix (ICM) per SOX 302/404 and COSO 2013 Framework:

| Control ID | Control Description | Control Type | Frequency | Evidence |
|-----------|--------------------|-----------|-----------| ---------|
| FC-01 | 3-way match auto-approve threshold review | Preventive | Monthly | Exception report |
| FC-02 | GL anomaly flagging and review | Detective | Daily | Anomaly review log |
| FC-03 | Transfer pricing arm's length validation | Preventive | Per transaction | TP documentation |
| FC-04 | LCNRV write-down computation and approval | Preventive | Monthly | Write-down register |
| FC-05 | Intercompany balance reconciliation | Detective | Daily | BlackLine certification |
| FC-06 | Segregation of duties: posting vs. approval | Preventive | Continuous | SAP authorisation log |
| FC-07 | Vendor bank detail change control | Preventive | Per change | Dual-approval log |

---

## 14. Timeline Summary

| Phase | Description | Duration | Start | End | Key Deliverables |
|-------|-------------|----------|-------|-----|-----------------|
| Phase 0 | Assessment and AS-IS Analysis | 4 weeks | Week 1 | Week 4 | Gap analysis, business case, programme charter |
| Phase 1 | Foundation and Master Data | 6 weeks | Week 5 | Week 10 | CoA, cost centres, event store schema |
| Phase 2 | Process Standardisation | 8 weeks | Week 11 | Week 18 | Standard P2P/O2C workflows, KPI framework |
| Phase 3 | Mathematical Models | 10 weeks | Week 13 | Week 22 | 3-way match, C2C, LCNRV, landed cost, ABC, TP |
| Phase 4 | ML/AI Pipeline | 12 weeks | Week 15 | Week 26 | Fraud detection, LSTM, NLP, GL anomaly |
| Phase 5 | Integration and Automation | 10 weeks | Week 19 | Week 28 | SAP, Oracle, Coupa, Taulia, BlackLine, SWIFT |
| Phase 6 | Continuous Improvement | Ongoing | Week 29 | Ongoing | Monthly Kaizen, model retraining, close acceleration |

**Total elapsed time to steady-state:** 28 weeks (7 months)

**Note:** Phases 3, 4, and 5 run in parallel from Week 13-22 to compress the critical path. The Programme Management Office (PMO) must maintain a daily dependency log to prevent blocking between tracks.

### Milestone Gates

| Gate | Week | Go/No-Go Criteria |
|------|------|-------------------|
| G1: Foundation ready | Week 10 | CoA approved, event store deployed, SAP access granted |
| G2: Model validation | Week 22 | All Phase 3 models unit-tested; CV AUC > 0.90 for ML models |
| G3: Integration UAT | Week 26 | All integrations pass end-to-end UAT; zero P1 defects |
| G4: Parallel run | Week 27 | 2-week parallel run with legacy system; variances < 0.1% |
| G5: Go-live | Week 28 | All gates cleared; rollback plan approved by CFO |

---

## 15. References

### Academic and Professional Standards

1. Kaplan, R.S. and Anderson, S.R. (2007). *Time-Driven Activity-Based Costing*. Harvard Business Press.
2. ASCM (2019). *SCOR Digital Standard v12.0*. Association for Supply Chain Management.
3. IASB (2023). *IAS 2 Inventories*. International Financial Reporting Standards Foundation.
4. IASB (2016). *IAS 7 Statement of Cash Flows*. International Financial Reporting Standards Foundation.
5. IASB (2014). *IFRS 15 Revenue from Contracts with Customers*. IASB.
6. OECD (2022). *Transfer Pricing Guidelines for Multinational Enterprises and Tax Administrations*. OECD Publishing.
7. OECD (2015). *BEPS Actions 8-10: Aligning Transfer Pricing Outcomes with Value Creation*. OECD/G20.
8. COSO (2013). *Internal Control — Integrated Framework*. Committee of Sponsoring Organisations.
9. Chopra, S. and Meindl, P. (2016). *Supply Chain Management: Strategy, Planning, and Operation*. 6th ed. Pearson.
10. Fabozzi, F.J. and Drake, P.P. (2009). *Finance: Capital Markets, Financial Management, and Investment Management*. Wiley.

### Regulatory References

11. EU Directive 2024/1760 (CSDDD) — Supply Chain Due Diligence.
12. US Pub.L. 117-78 (UFLPA) — Uyghur Forced Labor Prevention Act.
13. ISO 28000:2022 — Security and resilience: Supply chain security management systems.
14. ISO 9001:2015 — Quality management systems.
15. GS1 General Specifications v23.0 — GLN, GTIN, UOM codes.
16. Incoterms 2020 — International Chamber of Commerce.
17. SWIFT Standards Release Guide — MT940, CAMT.053.
18. FASB ASC 330 — Inventory (US GAAP counterpart to IAS 2).
19. PCAOB AS 2201 — An Audit of Internal Control Over Financial Reporting (SOX 404).

### Technology References

20. Chen, T. and Guestrin, C. (2016). XGBoost: A Scalable Tree Boosting System. *KDD 2016*.
21. Hochreiter, S. and Schmidhuber, J. (1997). Long Short-Term Memory. *Neural Computation*, 9(8).
22. Liu, F.T., Ting, K.M. and Zhou, Z.H. (2008). Isolation Forest. *ICDM 2008*.
23. Lundberg, S.M. and Lee, S.I. (2017). A Unified Approach to Interpreting Model Predictions. *NeurIPS 2017* (SHAP).
24. Xu, Y. et al. (2020). LayoutLM: Pre-training of Text and Layout for Document Image Understanding. *KDD 2020*.

---

*End of Implementation Guide — Finance and Supply Chain Controlling*

*Document Owner: Supply Chain Finance Director*
*Review Cycle: Annually or upon material regulatory change*
*Next Review Date: 2027-06-20*
