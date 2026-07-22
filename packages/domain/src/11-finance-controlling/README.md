# 11 — Finance & Supply Chain Controlling

> **SCOR-DS Process**: Enable (sE) | **APICS CPIM 9.0** | **Owner**: SC Finance Director

The Finance & Supply Chain Controlling department provides complete financial visibility across the supply chain, optimises working capital, controls logistics and inventory costs, and ensures every SC decision has a quantified value basis. It owns the 3-Way Invoice Match (PO ↔ GRN ↔ Invoice), Cash-to-Cash Cycle (C2C = DIO + DSO − DPO), working capital optimisation, and SC cost-as-percentage-of-revenue benchmarking.

---

## Table of Contents

1. [Core Responsibilities](#1-core-responsibilities)
2. [Domain Files](#2-domain-files)
3. [Key Business Rules](#3-key-business-rules)
4. [Mathematical Models](#4-mathematical-models)
5. [Recommended ML Models](#5-recommended-ml-models)
6. [KPIs & Benchmarks](#6-kpis--benchmarks)
7. [GL Account Structure](#7-gl-account-structure)
8. [Integration Points](#8-integration-points)
9. [Roles](#9-roles)
10. [References](#10-references)

---

## 1. Core Responsibilities

| Function | Description |
|---|---|
| **3-Way Invoice Match** | Automated PO ↔ GRN ↔ Invoice match with 1 % tolerance; blocks payment on mismatch |
| **Cash-to-Cash Cycle** | Tracks DIO + DSO − DPO in real time; targets negative C2C (supplier-financed model) |
| **Inventory Controlling** | FIFO / standard cost valuation; price and volume variance analysis |
| **Accounts Payable (DPO)** | Payment term discipline; dynamic discounting evaluation (2/10 Net 30) |
| **SC Cost as % Revenue** | Full cost transparency: procurement + carrying + logistics + warehousing + order mgmt |
| **Total Cost of Ownership** | TCO per supplier: price + freight + duties + quality cost + inventory cost + risk cost |
| **Cost of Quality (CoQ)** | Juran model: prevention + appraisal + internal failure + external failure |
| **SC Budget & Forecast** | CAPEX (equipment, WMS, TMS) and OPEX (labour, freight, storage) |

---

## 2. Domain Files

### `domain/Invoice.ts`

| Export | Description |
|---|---|
| `SupplierInvoice` | `{ invoiceNumber, supplierId, poId, lines[], totalAmountCents, currency, status }` |
| `InvoiceLine` | `{ poLineId, grnLineId, quantity, unitPriceCents, totalCents }` |
| `createInvoice(po, grn, invoiceData)` | Factory; links invoice to PO and GRN for 3-way match |
| `performThreeWayMatch(invoice)` | Validates qty and price within 1 % tolerance; returns `InvoiceMatchResult` |
| `InvoiceMatchResult` | `{ matched: boolean, qtyVariancePct, priceVariancePct, recommendation }` |

### `domain/CashFlowMetrics.ts`

| Export | Description |
|---|---|
| `WorkingCapitalSnapshot` | `{ inventoryValueCents, accountsReceivableCents, accountsPayableCents, date }` |
| `calculateWorkingCapitalMetrics(snapshot, cogs, revenue)` | Computes DIO, DSO, DPO, C2C, WC |
| `classifyCashCycle(c2cDays)` | `NEGATIVE` (best) / `ZERO_TO_30` / `ABOVE_30` / `CRITICAL` |

---

## 3. Key Business Rules

1. **3-Way Match Required** — Every supplier invoice must pass `performThreeWayMatch()` before payment is authorised. Invoices with `matched = false` are placed in a `DISPUTE` status and routed to the AP Specialist.
2. **1 % Tolerance** — Quantity and unit price deviations up to 1 % are auto-approved. Deviations > 1 % require manual review and supplier communication.
3. **Money as Integer Cents** — All monetary values are stored as integer cents (`number`). No floating-point arithmetic. Rounding follows banker's rounding (round half to even).
4. **Soft-Delete Only** — Invoices, payment records, and GL journal entries are never hard-deleted (`isDeleted: boolean`). This preserves the audit trail for statutory accounts.
5. **GL Journal on Every Movement** — All inventory stock movements generate a corresponding GL journal entry (debit/credit) per the account mapping in `getJournalAccounts()`. Finance and Inventory ledgers must always reconcile.
6. **DPO Floor** — Supplier payment terms must not fall below 30 days without CFO approval. Target range: 45–60 days to support positive working capital contribution.

---

## 4. Mathematical Models

### 4.1 3-Way Match (PO ↔ GRN ↔ Invoice)

```
Quantity match:
  |Invoice_qty − GRN_qty| / GRN_qty  ≤  0.01  (1 % tolerance)
  AND
  |GRN_qty − PO_qty| / PO_qty        ≤  0.01

Price match:
  |Invoice_unit_price − PO_unit_price| / PO_unit_price  ≤  0.01

All conditions true  → MATCHED → auto-approve payment
Any condition false  → DISPUTE → manual review
```

Prevents overpayment, duplicate payment, and procurement fraud. Reference: APICS CPIM 9.0.

### 4.2 Cash-to-Cash Cycle (C2C)

```
C2C   = DIO + DSO − DPO               (days)

DIO   = (Average_Inventory_Value / COGS) × 365
DSO   = (Accounts_Receivable / Revenue) × 365
DPO   = (Accounts_Payable / COGS) × 365

Best-in-class example (Amazon-style negative C2C):
  DIO = 25 days   (high inventory turnover)
  DSO = 10 days   (rapid customer collection)
  DPO = 60 days   (extended supplier payment terms)
  C2C = 25 + 10 − 60 = −25 days   → supplier-financed working capital
```

Reference: Chopra & Meindl, *Supply Chain Management* 6th Ed., Ch. 1 & Ch. 7.

### 4.3 SC Cost as % of Revenue

```
SC_Cost% = (Procurement_cost
           + Inventory_carrying_cost
           + Logistics_cost
           + Warehousing_cost
           + Order_management_cost) / Revenue × 100

Benchmarks (CSCMP 2025):
  Consumer goods  : 10–12 %
  Electronics     :  5– 8 %
  Pharmaceuticals :  8–10 %
  Automotive      :  6– 9 %
```

### 4.4 Inventory Carrying Cost (ICC)

```
ICC = Inventory_Value × Carrying_Rate

Carrying_Rate = Capital_cost% + Storage_cost% + Obsolescence%
              + Insurance% + Shrinkage%

Typical range: 20–30 % per year

ICC feeds into:  EOQ calculation (Dept. 03)
                 ABC classification cost justification
                 Make-or-buy analysis
                 Safety stock optimisation
```

### 4.5 Dynamic Discounting — Early Payment Analysis

```
Effective_Annual_Rate = (Discount% / (1 − Discount%)) × (365 / Days_Saved)

Example — 2/10 Net 30  (pay in 10 days, get 2% discount):
  EAR = (0.02 / 0.98) × (365 / 20) = 37.2% annualised

Decision rule: Accept early payment discount if EAR > WACC (Weighted Avg Cost of Capital).
Typical WACC ~10% → 2/10 Net 30 almost always worth accepting.
```

### 4.6 Total Cost of Ownership (TCO) per Supplier

```
TCO = Purchase_price × Volume
    + Inbound_freight + Insurance + Customs_duties
    + Quality_cost          (= PPM_i × Defect_cost_per_unit)
    + Inventory_carry_cost  (= Safety_stock_i × ICC_rate)
    + Disruption_risk_cost  (= EAL_i from Risk Register)
    + Procurement_overhead  (= FTE_time × hourly_rate)
```

TCO is the standard basis for supplier selection decisions (replaces unit-price-only comparison).

### 4.7 Cost of Quality — Juran Model

```
CoQ = Prevention + Appraisal + Internal_Failure + External_Failure

Prevention  (cheapest): supplier training, SPC, quality engineering
Appraisal              : incoming inspection, testing, audits
Internal failure        : scrap, rework, re-inspection
External failure (most expensive): customer returns, warranty, reputation loss

World-class CoQ target: < 3 % of revenue
Typical industry:        4–6 % of revenue
```

---

## 5. Recommended ML Models

### 5.1 Gradient Boosting — DPO/DSO Payment Behaviour Prediction

Predicts customer payment timing risk (DSO risk) and identifies optimal windows for supplier payment (DPO extension without relationship damage).

| Feature | Description |
|---|---|
| Customer credit score | External bureau + internal history |
| Order pattern regularity | CV of inter-order intervals |
| Seasonal payment effects | Q4 collection compression |
| Dispute frequency | Historical invoice dispute rate |

- **Libraries**: XGBoost, LightGBM
- **Output**: `P(late_payment)` per invoice; triggers early collection workflow if > 0.3

### 5.2 Anomaly Detection — Invoice Fraud Prevention

Isolation Forest and Autoencoder models detect anomalous invoice patterns: duplicate invoice amounts, unusual supplier-amount combinations, round-number fraud, and split invoices below the PO approval threshold (`PO_APPROVAL_THRESHOLD_CENTS` = $5 000).

- **Libraries**: `scikit-learn IsolationForest`, `PyOD AutoEncoder`
- **Sensitivity target**: Detect > 90 % of known fraud patterns in back-test

### 5.3 NLP + OCR — Automated Invoice Data Extraction

Extracts PO number, line quantities, unit prices, and totals from PDF and EDI invoices (UN/EDIFACT INVOIC) using OCR + Named Entity Recognition. Maps extracted data to PO and GRN records for fully automated 3-way match without manual data entry.

- **Libraries**: AWS Textract (primary), Tesseract + spaCy (fallback)
- **Accuracy target**: > 98 % field-level extraction accuracy on structured invoices

### 5.4 Time Series — 13-Week Rolling Cash Flow Forecast (Prophet)

Forecasts weekly cash inflows (AR collections) and outflows (AP payments, freight, payroll) with 13-week visibility. Enables proactive working capital management and credit facility utilisation planning.

- **Libraries**: `prophet`, `statsmodels`
- **Output**: P10/P50/P90 weekly cash balance scenarios

### 5.5 Linear Programming — Working Capital Optimisation

Maximises NPV of cash flows subject to payment term constraints, minimum cash balance requirements, and early-payment discount opportunities across all active suppliers.

```
Maximise:  NPV(cash_flows)
Subject to:
  cash_balance_t ≥ minimum_cash_reserve   ∀t
  payment_date_i ≥ invoice_due_date_i     ∀i
  early_pay_i ∈ {0, 1}                   ∀i with discount offer
```

- **Libraries**: `PuLP`, `scipy.optimize.linprog`

---

## 6. KPIs & Benchmarks

| KPI | Formula | World-Class Target | Alert |
|---|---|---|---|
| **C2C Cycle Time** | `DIO + DSO − DPO` | < 30 days (negative = best-in-class) | > 45 days |
| **DIO** | `(Avg Inventory / COGS) × 365` | < 45 days (FMCG) | > 60 days |
| **DSO** | `(AR / Revenue) × 365` | < 35 days | > 50 days |
| **DPO** | `(AP / COGS) × 365` | 45–60 days | < 30 days |
| **Invoice Match Rate** | `Auto-matched invoices / Total × 100` | > 98 % | < 95 % |
| **SC Cost / Revenue** | `Total SC Cost / Revenue × 100` | < 10–12 % | > 15 % |
| **Inventory Write-off %** | `Write-offs / Avg Inventory × 100` | < 1 % | > 2 % |
| **Procurement Savings %** | `Negotiated savings / Total spend × 100` | ≥ 3–5 % annual | < 2 % |
| **CoQ % Revenue** | `Total CoQ / Revenue × 100` | < 3 % | > 5 % |
| **ROLA** | `EBIT(SC) / Logistics Assets` | > 15 % | < 10 % |

---

## 7. GL Account Structure

| Account Code | Account Name | Type |
|---|---|---|
| 1300 | Inventory — Finished Goods | Balance Sheet (Asset) |
| 1310 | Goods in Transit | Balance Sheet (Asset) |
| 1320 | Work in Process (WIP) | Balance Sheet (Asset) |
| 2100 | Accounts Payable | Balance Sheet (Liability) |
| 5000 | Cost of Goods Sold (COGS) | P&L |
| 5100 | Inventory Price Variance | P&L |
| 5200 | Inventory Shrinkage & Obsolescence | P&L |
| 5300 | Inbound Freight | P&L |
| 5400 | Warehousing & Storage | P&L |

All stock movements must generate a balanced debit/credit journal entry. Reconciliation between inventory sub-ledger and GL is performed nightly.

---

## 8. Integration Points

| Department | Data Flow |
|---|---|
| **01 Procurement** | PO data (quantities, prices, payment terms) feeds `performThreeWayMatch()` |
| **05 Inventory** | Stock movement journal entries post to GL accounts 1300–1320 |
| **06 Warehouse** | GRN records from WMS feed into 3-way match as the receipt leg |
| **07 Logistics** | Freight invoices matched against shipment records; freight cost in SC Cost % |
| **08 Quality** | PPM and defect data feed CoQ internal/external failure costs |
| **12 S&OP** | Financial bridge: operational plan translated to P&L in Step 4 (Pre-S&OP) |

---

## 9. Roles

| Role | Responsibility |
|---|---|
| **SC Finance Director** | Financial strategy for the supply chain; CFO liaison |
| **Cost Controller** | Logistics and warehousing cost analysis; variance reporting |
| **AP Specialist** | Supplier invoice processing; DPO management; dispute resolution |
| **Inventory Accountant** | FIFO/standard cost valuation; GL reconciliation |
| **Spend Analyst** | Spend cube management; procurement savings tracking |
| **Budget Analyst** | SC CAPEX/OPEX budgeting; 13-week cash flow forecast |

---

## 10. References

1. Chopra, S. & Meindl, P., **Supply Chain Management** 6th Ed., Ch. 1 & Ch. 7, Pearson, 2016.
2. Ballou, R.H., **Business Logistics / Supply Chain Management** 5th Ed., Ch. 3 "Logistics Cost Measurement," Pearson, 2004.
3. Juran, J.M. & Godfrey, A.B. (eds.), **Juran's Quality Handbook** 5th Ed. — Cost of Quality model, McGraw-Hill, 1999.
4. APICS / ASCM, **CPIM 9.0 Exam Content Manual** — Supply Chain Costing and Financial Management, 2024.
5. CSCMP, **Annual State of Logistics Report 2025** — SC cost benchmarks by industry sector.
