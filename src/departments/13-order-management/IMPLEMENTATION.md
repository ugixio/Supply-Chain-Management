# Order Management Analytics — Implementation Guide
## Department 13: Order-to-Cash Analytics

**Classification**: Internal — Senior Consultant Grade
**Standard Alignment**: SCOR-DS v4.0, SAP S/4HANA SD/MM, EDI X12 850/856/810, ISO 9001:2015, Incoterms 2020
**Systems**: SAP S/4HANA SD/MM · Azure SQL · Power BI · EDI 850/856/810
**Revision**: 2.0
**Date**: 2026-06-22

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Analysis Objective](#2-analysis-objective)
3. [Scope](#3-scope)
4. [Business Questions](#4-business-questions)
5. [Data Sources](#5-data-sources)
6. [Data Model](#6-data-model)
7. [Data Dictionary](#7-data-dictionary)
8. [Transformation Rules](#8-transformation-rules)
9. [Business Rules](#9-business-rules)
10. [KPIs and Formulas](#10-kpis-and-formulas)
11. [Analytical Logic](#11-analytical-logic)
12. [Validations and Controls](#12-validations-and-controls)
13. [Required Evidence](#13-required-evidence)
14. [Dashboard Design](#14-dashboard-design)
15. [Use Cases](#15-use-cases)
16. [Recommended Actions](#16-recommended-actions)
17. [Test Cases](#17-test-cases)
18. [Risks and Mitigations](#18-risks-and-mitigations)
19. [Implementation Checklist](#19-implementation-checklist)
20. [Validation Checklist](#20-validation-checklist)
21. [Pending Information](#21-pending-information)
22. [Implementation Roadmap](#22-implementation-roadmap)

---

## 1. Executive Summary

Order Management Analytics constitutes the commercial nerve centre of enterprise supply chain performance measurement. In a B2B environment driven by SAP S/4HANA SD/MM and daily EDI interchange with retail and distribution customers, the ability to track open order risk in real time, measure Perfect Order Rate at line-item granularity, and decompose Order-to-Cash cycle time into actionable sub-intervals separates organisations that retain strategic accounts from those that lose them to chargebacks, deductions, and attrition.

This implementation guide delivers a complete Order Management Analytics capability covering five analytical domains: Open Order Risk Analysis, Order Fill Rate and Perfect Order Rate, Customer Service Level by segment, ATP/CTP promise accuracy, and Order-to-Cash Cycle Time decomposition. The analytical output feeds daily Power BI dashboards consumed by Customer Service Representatives, Order Management leads, and VP-level customer-facing KPI reviews.

The business case rests on three measurable outcomes: (1) reducing open-order late-risk exposure through proactive exception management, targeting a 35% reduction in unplanned backorders within 90 days of go-live; (2) improving Perfect Order Rate from a typical industry baseline of 88–92% toward a world-class target of 95%+; and (3) compressing Order-to-Cash cycle time by 8–12 days through ATP promise accuracy improvement and automated invoice generation, directly reducing Days Sales Outstanding (DSO).

Retailer OTIF vendor compliance is a primary driver: Walmart penalties at 3% of invoice value below 98% OTIF, Target penalties at 5% below 95%, and Amazon non-compliance notifications below 97% represent material financial exposure that accurate daily order tracking directly mitigates. This guide provides the data model, KPI definitions, business rules, analytical logic, dashboard specifications, and roadmap required to deliver this capability in a 13-week implementation cycle.

---

## 2. Analysis Objective

The primary objective of this analytics implementation is to provide daily, actionable visibility into the full Order-to-Cash cycle with sufficient granularity to enable intervention before customer commitments are missed.

Specific objectives are:

1. **Open Order Risk**: Classify every open order line daily as Critical / High / Medium / Low risk based on available stock versus committed quantity and days remaining to promise date. Surface at-risk lines to the responsible CSR before the ship window closes.

2. **Order Fill Rate and Perfect Order Rate**: Measure fulfillment quality at order-line level across four independent dimensions — On-Time, In-Full, Damage-Free, Correct Documents — and aggregate to order, customer, channel, and period levels with Power BI drill-down.

3. **Customer Service Level by Segment**: Disaggregate all service metrics by customer tier (A/B/C by revenue), channel (EDI / API / Portal / Manual), and retailer standard (Walmart / Target / Amazon / Other) to enable targeted improvement by segment.

4. **ATP/CTP Promise Accuracy**: Track whether delivery dates confirmed through the ATP/CTP engine were subsequently met, identify systematic over-promising patterns by SKU or warehouse, and feed accuracy findings back to the ATP configuration team.

5. **Order-to-Cash Cycle Time**: Decompose the full O2C cycle into seven sub-intervals from order receipt through payment, identify the dominant bottleneck intervals, and provide trend analysis against targets to drive DSO reduction.

---

## 3. Scope

### In Scope

- All sales orders captured in SAP S/4HANA SD (VA01/VA02/VA03 and BAPI SALESORDER equivalents)
- EDI 850 (Purchase Order from customer), EDI 856 (Advance Ship Notice), EDI 810 (Invoice) inbound and outbound transactions
- All order channels: EDI, API, Customer Portal, Manual entry, Shopify, Salesforce
- Fulfillment types: D1 (Stocked Product), D2 (Make-to-Order), D3 (Engineer-to-Order)
- Customer segments: Tier A (top 20% by revenue), Tier B (next 30%), Tier C (bottom 50%)
- Shipment tracking from warehouse goods issue through carrier delivery scan confirmation
- Invoice generation and payment receipt events from SAP FI/AR (accounts receivable)
- ATP/CTP promise commits from the available-to-promise engine
- All open orders with status between CONFIRMED and INVOICED
- Historical closed orders: minimum 24 months for trend analysis and baseline establishment

### Out of Scope

- Procurement purchase orders (Department 01)
- Supplier-side delivery performance (Department 06)
- Warehouse internal operations beyond goods issue date (Department 10)
- Returns and reverse logistics
- Financial statement consolidation and revenue recognition accounting

### Geographic Scope

All operating countries in the SAP client. Currency consolidation to USD for KPI reporting using SAP-sourced exchange rates.

---

## 4. Business Questions

The following business questions drive the analytical design. Each maps to one or more KPIs defined in Section 10.

1. **What percentage of open order lines are at risk of shipping late today, and which customer accounts are most exposed?**
   Maps to: Open Order At-Risk Rate; customer tier segmentation; daily CSR work queue.

2. **What is our Perfect Order Rate for the current month versus last month, and which of the four dimensions — On-Time, In-Full, Damage-Free, or Correct Documents — is the primary drag?**
   Maps to: Perfect Order Rate; factor decomposition waterfall.

3. **Which customer tier is receiving the best and worst service levels, and does the gap justify differentiated fulfillment priority allocation?**
   Maps to: Order Fill Rate by tier; Customer Service Level segmentation.

4. **How accurate is our ATP/CTP promise engine? For orders where we committed a delivery date, what percentage was actually delivered on or before that date?**
   Maps to: ATP Accuracy; over-promise pattern by SKU and warehouse.

5. **What is our current Order-to-Cash cycle time, and which sub-interval — entry, credit, ATP, pick, transit, invoicing, or collection — is the largest bottleneck?**
   Maps to: Order-to-Cash Cycle Time decomposition; bottleneck interval identification.

6. **What is our backorder rate by SKU and product family, and how is it trending over the past 13 weeks?**
   Maps to: Backorder Rate; 13-week rolling trend by SKU.

7. **Are we meeting Walmart, Target, and Amazon OTIF vendor compliance standards, and what is the current financial exposure from penalty risk?**
   Maps to: Order Fill Rate by retailer standard; penalty exposure calculation.

8. **What is our Customer Complaint Rate, and what are the top three complaint categories driving manual intervention and credit memo volume?**
   Maps to: Customer Complaint Rate; complaint category distribution.

9. **For orders that missed their committed delivery date, what was the root cause — stock shortage, carrier delay, warehouse miss, or documentation error?**
   Maps to: Late order root cause classification; factor attribution in Perfect Order Rate.

10. **What is the average Order Cycle Time by channel, and do EDI orders consistently outperform manual-entry orders in speed and accuracy?**
    Maps to: Order Cycle Time by channel; channel mix analysis.

11. **Which SKUs have the highest ATP promise shortfall rate — meaning ATP committed but the order was ultimately short-shipped?**
    Maps to: ATP Accuracy by SKU; fill rate gap analysis; safety buffer calibration.

12. **What is the Days Sales Outstanding trend by customer segment, and which customers are extending payment beyond contract terms?**
    Maps to: O2C cycle T_collection interval; DSO trend; AR aging.

---

## 5. Data Sources

### 5.1 SAP S/4HANA SD — Sales Orders

| Attribute | Detail |
|-----------|--------|
| Name | SAP S/4HANA Sales and Distribution — Order Master |
| System | SAP S/4HANA (on-premise or BTP-connected) |
| Table | VBAK (order header), VBAP (order lines), VBEP (schedule lines), VBFA (document flow) |
| Owner | IT Order Management team |
| Frequency | Real-time via SAP ODP delta extraction; Azure SQL staging refresh every 15 minutes |
| Fields | VBELN (order number), POSNR (line item), MATNR (material/SKU), KUNNR (customer), KDAUF (customer PO reference), VRKME (sales unit), KWMENG (ordered quantity), WAERK (currency), NETPR (net price), EDATU (requested delivery date), LPEIN (ATP committed delivery date), ABGRU (rejection reason code), GBSTK (overall processing status), LFSTK (delivery status), FKSTK (billing status) |
| Critical Fields | VBELN, POSNR, MATNR, KUNNR, KWMENG, EDATU, LPEIN, GBSTK |
| Primary Key | VBELN + POSNR |
| Validations | KWMENG > 0; EDATU >= order creation date; LPEIN not null for CONFIRMED status; WAERK is valid ISO 4217 code |
| Known Errors | Duplicate VBELN across client splits; LPEIN null for MTO orders before CTP confirmation; ABGRU codes inconsistently applied across plants |
| Evidence | SAP SD configuration document; ABAP data dictionary SE11; Azure SQL extraction log |

### 5.2 SAP S/4HANA SD — Deliveries and Shipments

| Attribute | Detail |
|-----------|--------|
| Name | SAP Delivery and Shipment Records |
| System | SAP S/4HANA |
| Table | LIKP (delivery header), LIPS (delivery lines), VTTK (shipment header), VTTP (shipment items) |
| Owner | Logistics / Warehouse IT |
| Frequency | Real-time ODP delta; Azure SQL refresh every 15 minutes |
| Fields | VBELN (delivery number), POSNR (delivery line), MATNR, LGORT (storage location), LFIMG (delivered quantity), VGBEL (reference sales order), KODAT (pick date), WADAT (goods issue date — actual ship date), TDLNR (carrier ID), VSTEL (shipping point) |
| Critical Fields | VBELN, VGBEL (link to sales order), LFIMG, WADAT |
| Primary Key | LIKP.VBELN + LIPS.POSNR |
| Validations | LFIMG >= 0; WADAT >= KODAT; VGBEL must exist in VBAK |
| Known Errors | Late goods issue posting — WADAT stamped T+1 when physical ship occurred same-day evening; zero-quantity delivery lines for cancelled items not marked deleted |
| Evidence | SAP WM/EWM configuration document; outbound delivery process SOP |

### 5.3 SAP FI/AR — Invoice and Payment

| Attribute | Detail |
|-----------|--------|
| Name | SAP Accounts Receivable — Invoice and Payment |
| System | SAP S/4HANA FI |
| Table | VBRK (billing header), VBRP (billing lines), BSID (open AR items), BSAD (cleared AR items) |
| Owner | Finance / AR team |
| Frequency | Daily batch load to Azure SQL at 06:00 UTC |
| Fields | VBELN (invoice number), FKDAT (billing date), NETWR (net value), WAERK (currency), AUGDT (payment clearing date), ZTERM (payment terms code), KUNNR (customer), VGBEL (reference delivery), FKART (billing type — distinguish invoices from credit memos) |
| Critical Fields | VBELN, FKDAT, AUGDT, NETWR, KUNNR, FKART |
| Primary Key | VBRK.VBELN |
| Validations | FKDAT >= delivery goods issue date; NETWR > 0 for standard invoices; AUGDT >= FKDAT; FKART must be mapped to INVOICE or CREDIT_MEMO |
| Known Errors | AUGDT null for partially cleared items; credit memos (FKART = 'G2') must be excluded from fill rate calculation but included in O2C cycle time analysis |
| Evidence | SAP FI configuration; month-end AR aging report from Finance |

### 5.4 EDI Transaction Log

| Attribute | Detail |
|-----------|--------|
| Name | EDI Transaction Archive |
| System | Azure SQL (EDI middleware — Sterling Commerce or Boomi) |
| Table | EDI_TRANSACTIONS (custom), EDI_ACKNOWLEDGEMENTS |
| Owner | IT Integration team |
| Frequency | Real-time append; read for analytics daily |
| Fields | transaction_id, transaction_type (850/856/810/824), partner_id (customer EDI partner ID), direction (INBOUND/OUTBOUND), received_at (UTC timestamp), processed_at (UTC timestamp), order_reference, edi_status (ACCEPTED/REJECTED/PENDING), error_code, error_description |
| Critical Fields | transaction_id, transaction_type, partner_id, received_at, processed_at, edi_status |
| Primary Key | transaction_id |
| Validations | processed_at >= received_at; edi_status not null; partner_id must exist in customer master EDI partner table |
| Known Errors | Missing processed_at for rejected transactions; duplicate transaction_id for middleware retries |
| Evidence | EDI partner connectivity documentation; middleware integration log |

### 5.5 ATP/CTP Commitment Log

| Attribute | Detail |
|-----------|--------|
| Name | ATP/CTP Promise Log |
| System | Azure SQL (domain service log) |
| Table | ATP_COMMITMENTS (custom domain service table) |
| Owner | Order Management IT |
| Frequency | Real-time insert on each ATP/CTP invocation; daily read for accuracy reporting |
| Fields | commitment_id, order_id, order_line_id, sku_id, warehouse_id, promised_delivery_date, committed_qty, atp_run_timestamp, method (ATP/CTP), on_hand_at_commit, committed_demand_at_commit, inbound_scheduled_at_commit, safety_stock_buffer_at_commit |
| Critical Fields | commitment_id, order_id, order_line_id, promised_delivery_date, committed_qty |
| Primary Key | commitment_id |
| Validations | committed_qty <= ordered_qty; promised_delivery_date >= atp_run_timestamp date; on_hand_at_commit >= 0 |
| Known Errors | Stale commitments not voided on order cancellation; CTP records missing raw_material_ready_date when MRP run was skipped |
| Evidence | ATP engine configuration document; domain service API specification |

### 5.6 Customer Master (SAP KNA1/KNB1)

| Attribute | Detail |
|-----------|--------|
| Name | Customer Master |
| System | SAP S/4HANA |
| Table | KNA1 (general data), KNB1 (company code data), KNVV (sales area data) |
| Owner | Master Data Management team |
| Frequency | Daily refresh to Azure SQL |
| Fields | KUNNR (customer ID), NAME1 (name), LAND1 (country), VKORG (sales org), KDKG (customer group / tier code), WAERS (currency), ZTERM (payment terms), KLIMK (credit limit cents), KNKLI (credit account group) |
| Critical Fields | KUNNR, KDKG (tier), KLIMK, ZTERM |
| Primary Key | KUNNR + VKORG |
| Validations | KLIMK > 0 for active customers; KDKG must map to Tier A/B/C classification table; ZTERM must exist in payment terms reference table |
| Known Errors | Duplicate customer records across legacy company codes; KDKG blank for new customers pending classification |
| Evidence | MDM governance policy; customer master cleanse project log |

---

## 6. Data Model

### 6.1 Conceptual Entity Relationship

```
CUSTOMER ──< SALES_ORDER >── ORDER_LINE ──< DELIVERY_LINE
                                  |               |
                             ATP_COMMIT      SHIPMENT_LINE
                                                   |
                             INVOICE_LINE <─────────┘
                                  |
                             AR_PAYMENT
```

### 6.2 Star Schema for Power BI

**Fact table: FACT_ORDER_LINE**

Each row represents one sales order line captured as a daily snapshot. Grain: order_number + line_number + snapshot_date.

| Column | Type | Description |
|--------|------|-------------|
| order_line_key | INT (surrogate) | Surrogate primary key |
| snapshot_date | DATE | Date of daily snapshot |
| order_id | VARCHAR(20) | SAP VBELN |
| line_id | VARCHAR(6) | SAP POSNR |
| customer_key | INT | FK to DIM_CUSTOMER |
| sku_key | INT | FK to DIM_SKU |
| warehouse_key | INT | FK to DIM_WAREHOUSE |
| date_key_order | INT | FK to DIM_DATE (order creation date) |
| date_key_requested | INT | FK to DIM_DATE (customer requested delivery) |
| date_key_committed | INT | FK to DIM_DATE (ATP committed delivery) |
| date_key_shipped | INT | FK to DIM_DATE (goods issue date) |
| date_key_delivered | INT | FK to DIM_DATE (carrier confirmed delivery) |
| date_key_invoiced | INT | FK to DIM_DATE (invoice date) |
| date_key_paid | INT | FK to DIM_DATE (payment cleared date) |
| ordered_qty | DECIMAL(18,3) | Ordered quantity in sales UOM |
| confirmed_qty | DECIMAL(18,3) | ATP-confirmed quantity |
| shipped_qty | DECIMAL(18,3) | Actual shipped quantity |
| delivered_qty | DECIMAL(18,3) | Carrier-confirmed delivered quantity |
| unit_price_cents | BIGINT | Unit price in integer cents — no floats |
| line_value_cents | BIGINT | ordered_qty * unit_price_cents |
| currency_code | VARCHAR(3) | ISO 4217 original transaction currency |
| line_value_usd_cents | BIGINT | Converted to USD using SAP exchange rate at order date |
| channel | VARCHAR(20) | EDI / API / PORTAL / MANUAL |
| fulfillment_type | VARCHAR(10) | D1 / D2 / D3 |
| order_status | VARCHAR(30) | Current order status code |
| in_full_threshold_pct | DECIMAL(5,2) | Retailer-specific threshold applied (95–100) |
| on_time_flag | BIT | 1 = delivered on or before committed date |
| in_full_flag | BIT | 1 = delivered_qty / ordered_qty >= in_full_threshold_pct |
| damage_free_flag | BIT | 1 = no damage claim within 5 business days of delivery |
| correct_docs_flag | BIT | 1 = invoice and packing list match with zero discrepancy |
| perfect_order_flag | BIT | on_time_flag * in_full_flag * damage_free_flag * correct_docs_flag |
| at_risk_level | VARCHAR(10) | CRITICAL / HIGH / MEDIUM / LOW / NONE |
| shortage_qty | DECIMAL(18,3) | max(0, ordered_qty - on_hand_available - confirmed_inbound_qty) |
| atp_promise_kept | BIT | 1 = actual delivery <= ATP promised date |
| backorder_flag | BIT | 1 = line currently on backorder (shipped=0, current_date > committed_date) |
| complaint_flag | BIT | 1 = complaint filed against this order line |
| force_majeure_flag | BIT | 1 = delivery delay due to documented force-majeure event |
| idempotency_key | VARCHAR(64) | Deduplication key for EDI resubmissions |
| is_deleted | BIT | Soft-delete flag — never hard-delete |

**Dimension: DIM_CUSTOMER**

| Column | Type | Description |
|--------|------|-------------|
| customer_key | INT | Surrogate PK |
| customer_id | VARCHAR(20) | SAP KUNNR |
| customer_name | VARCHAR(100) | Legal name |
| tier | VARCHAR(10) | TIER_A / TIER_B / TIER_C |
| country_code | VARCHAR(2) | ISO 3166-1 alpha-2 |
| retailer_standard | VARCHAR(20) | WALMART / TARGET / AMAZON / KROGER / OTHER |
| payment_terms | VARCHAR(20) | NET_30 / NET_60 / NET_90 / 2_10_NET_30 |
| credit_limit_cents | BIGINT | Integer cents |
| last_tier_review_date | DATE | Date of last tier classification review |
| is_active | BIT | Active flag |

**Dimension: DIM_SKU**

| Column | Type | Description |
|--------|------|-------------|
| sku_key | INT | Surrogate PK |
| sku_id | VARCHAR(40) | SAP MATNR |
| description | VARCHAR(200) | Product description |
| product_family | VARCHAR(50) | Product category grouping |
| abc_class | VARCHAR(1) | A / B / C (value-based) |
| xyz_class | VARCHAR(1) | X / Y / Z (demand variability) |
| uom | VARCHAR(10) | GS1 UOM code |
| lead_time_days | INT | Standard lead time in calendar days |
| atp_safety_buffer | DECIMAL(18,3) | Safety stock buffer used in ATP calculation |
| lot_tracked | BIT | Lot tracking required flag |
| hazmat_flag | BIT | Hazardous material flag |

**Dimension: DIM_DATE** — Standard date dimension; one row per calendar day from 2020-01-01 to 2030-12-31. Includes: calendar_date, year, quarter, month, week, day_of_week, is_weekend, is_working_day (from SAP factory calendar), fiscal_period.

**Dimension: DIM_WAREHOUSE** — warehouse_id, name, country_code, plant_code, shipping_point, carrier_cut_off_time_local, timezone.

---

## 7. Data Dictionary

### 7.1 MART_ORDER_FILL_RATE

| Attribute | Detail |
|-----------|--------|
| Name | Order Fill Rate Mart |
| Granularity | One row per customer + period (week or month) + channel |
| Fields | customer_id, period_start, period_end, channel, total_lines, shipped_complete_on_time_lines, fill_rate_pct, backorder_lines, backorder_rate_pct |
| Primary Key | customer_id + period_start + channel |
| Relationships | DIM_CUSTOMER, DIM_DATE |
| Transformations | Aggregated from FACT_ORDER_LINE; shipped_complete_on_time = rows where on_time_flag = 1 AND in_full_flag = 1; excludes is_deleted = 1 |
| Cleaning | Exclude cancelled lines (order_status = CANCELLED); exclude credit memo references; exclude test orders |
| Validations | fill_rate_pct between 0 and 100; total_lines > 0 |
| Use | Order Fill Rate KPI tile and trend chart; Walmart/Target OTIF compliance report |

### 7.2 MART_PERFECT_ORDER

| Attribute | Detail |
|-----------|--------|
| Name | Perfect Order Rate Mart |
| Granularity | One row per customer + period + fulfillment_type |
| Fields | customer_id, period_start, period_end, fulfillment_type, total_lines, on_time_pct, in_full_pct, damage_free_pct, correct_docs_pct, poi_rate, poi_delta_vs_prior_period |
| Primary Key | customer_id + period_start + fulfillment_type |
| Relationships | DIM_CUSTOMER, DIM_DATE |
| Transformations | poi_rate = on_time_pct * in_full_pct * damage_free_pct * correct_docs_pct (all as decimals 0–1, then multiplied); poi_delta uses LAG() window function partitioned by customer_id and fulfillment_type |
| Cleaning | Exclude test orders; exclude lines with line_value_cents = 0 |
| Validations | Each dimension percentage in [0, 1]; poi_rate equals product of four dimensions within epsilon = 0.001 |
| Use | Perfect Order Rate KPI; factor waterfall chart; executive monthly review |

### 7.3 MART_O2C_CYCLE_TIME

| Attribute | Detail |
|-----------|--------|
| Name | Order-to-Cash Cycle Time Mart |
| Granularity | One row per completed order (status = PAID) |
| Fields | order_id, customer_id, channel, fulfillment_type, t_entry_hours, t_credit_hours, t_atp_hours, t_pick_hours, t_transit_days, t_invoice_hours, t_collection_days, t_total_o2c_days |
| Primary Key | order_id |
| Relationships | DIM_CUSTOMER |
| Transformations | Each interval computed from event timestamps; working hours for internal intervals (T_entry through T_invoice); calendar days for T_collection; T_total expressed in calendar days |
| Cleaning | Exclude orders with any null event timestamp in the sequence; cap T_collection_days at 180 to exclude aged/disputed outliers from mean |
| Validations | All interval values >= 0; t_total_o2c_days in [0, 180]; event timestamps must be monotonically increasing |
| Use | O2C decomposition waterfall; DSO trend; bottleneck identification |

### 7.4 MART_ATP_ACCURACY

| Attribute | Detail |
|-----------|--------|
| Name | ATP Promise Accuracy Mart |
| Granularity | One row per ATP commitment |
| Fields | commitment_id, order_id, line_id, sku_id, warehouse_id, promised_date, actual_delivery_date, days_variance, promise_kept_flag, atp_method, commit_timestamp, force_majeure_excluded |
| Primary Key | commitment_id |
| Relationships | DIM_SKU, DIM_WAREHOUSE |
| Transformations | days_variance = actual_delivery_date - promised_delivery_date (positive = late vs. promise); promise_kept_flag = 1 when days_variance <= 0 |
| Cleaning | Exclude commitments for cancelled orders; exclude rows where actual_delivery_date is null (order still open); exclude force_majeure_excluded = 1 from accuracy rate denominator |
| Validations | days_variance must be numeric; promised_date >= commit_timestamp date |
| Use | ATP Accuracy KPI; over-promise pattern detection by SKU and warehouse |

### 7.5 MART_OPEN_ORDER_RISK

| Attribute | Detail |
|-----------|--------|
| Name | Open Order Risk Mart |
| Granularity | One row per open order line, refreshed daily at 06:00 UTC |
| Fields | order_id, line_id, customer_id, sku_id, warehouse_id, ordered_qty, committed_qty, on_hand_available, confirmed_inbound_qty, days_to_promise, shortage_qty, shortage_pct, at_risk_level, assigned_csr_id, snapshot_date |
| Primary Key | order_id + line_id |
| Relationships | DIM_CUSTOMER, DIM_SKU |
| Transformations | shortage_qty = max(0, ordered_qty - on_hand_available - confirmed_inbound_qty); shortage_pct = shortage_qty / ordered_qty; at_risk_level derived per Section 11.1 classification logic |
| Cleaning | Exclude fully delivered lines; exclude is_deleted = 1; exclude order_status in (CANCELLED, PAID, CREDIT_HOLD) |
| Validations | on_hand_available >= 0; days_to_promise >= 0 for open orders; at_risk_level must be one of CRITICAL / HIGH / MEDIUM / LOW / NONE |
| Use | Daily CSR work queue; open order risk heatmap; Tier A critical alert trigger |

---

## 8. Transformation Rules

### 8.1 Currency Normalisation

All monetary values are stored and processed as integer cents in the original transaction currency. For cross-currency KPI roll-ups, apply the SAP-sourced exchange rate from table TCURR at the order creation date. Store both original-currency cents and USD-equivalent cents as separate columns. Never store or compute floating-point monetary values.

```sql
-- Azure SQL transformation: currency normalisation
SELECT
    ol.order_id,
    ol.line_value_cents                                               AS line_value_original_cents,
    ol.currency_code,
    CAST(ol.line_value_cents * er.exchange_rate AS BIGINT)           AS line_value_usd_cents
FROM staging.order_lines ol
LEFT JOIN staging.exchange_rates er
    ON  er.from_currency = ol.currency_code
    AND er.to_currency   = 'USD'
    AND er.rate_date     = CAST(ol.order_created_at AS DATE);
```

### 8.2 Delivery Date Determination

For OTIF and fill rate calculations, the "required delivery date" is the date committed by the ATP/CTP engine (SAP VBEP.LPEIN), not the customer's original requested date (VBEP.EDATU). For Walmart OTIF specifically, the expected delivery date is derived from the ASN (EDI 856) ship date plus the carrier routing guide transit days — this is distinct from the SAP committed date and requires a separate calculation path stored in a dedicated WALMART_OTIF column.

### 8.3 In-Full Threshold by Retailer

| Retailer | In-Full Threshold | Source |
|----------|-----------------|--------|
| Walmart | 100.0% of ordered quantity | Walmart Supplier Manual 2025 |
| Target | 98.0% of ordered quantity | Target Vendor Guide 2025 |
| Amazon | 97.0% of ordered quantity | Amazon Vendor Central 2025 |
| Kroger | 96.0% of ordered quantity | Kroger Supplier Standards |
| Default (non-retail) | 95.0% of ordered quantity | Internal policy |

Store the threshold applied as `in_full_threshold_pct` in FACT_ORDER_LINE for full auditability of OTIF calculations.

### 8.4 Working Days Calculation

Order Cycle Time (OCT) between ship_date and order_confirmed_date must be expressed in working days, excluding weekends and public holidays. Use the factory calendar from SAP transaction SCAL. In Azure SQL, maintain a DIM_WORKING_DAY table populated from the SAP calendar export. Do not approximate using division by 5.

### 8.5 Backorder Flag Logic

A line is flagged backorder (backorder_flag = 1) when all three conditions hold:
- Order status is CONFIRMED or ATP_COMMITTED (not yet shipped)
- current_date > committed_delivery_date (LPEIN)
- shipped_qty = 0 for the line

Do not flag as backorder if the line is status IN_PICKING — warehouse has the item but has not yet completed goods issue.

### 8.6 Damage Claim Lookback Window

`damage_free_flag` is set to 0 if a customer complaint record with complaint_category in ('DAMAGED_GOODS', 'CONCEALED_DAMAGE') is filed within 5 business days of the confirmed delivery date. After 5 business days with no claim, the flag defaults to 1 and is locked. Claims filed after 5 business days are tracked for quality management but do not retroactively adjust the historical Perfect Order Rate.

### 8.7 EDI Idempotency

EDI 850 resubmissions are deduplicated using the compound key (partner_id, customer_PO_number, PO_date). The idempotency_key column in FACT_ORDER_LINE stores this concatenated key as a SHA-256 hash. Duplicate submissions trigger an update to the existing order record, not a new row insertion.

---

## 9. Business Rules

1. **Never count cancelled lines in fill rate or Perfect Order Rate denominators.** A cancelled line is a commercial decision, not a fulfillment failure. Filter ABGRU-coded cancellations and order_status = CANCELLED before any fill rate computation.

2. **PO split deliveries count as one order for OTIF.** If a single customer PO generates multiple deliveries due to ATP partial commits, the OTIF assessment uses the final delivery date of the last partial shipment and the original PO requested delivery date as the benchmark.

3. **Tier A customer lines take priority in ATP allocation during shortage.** When total available stock is insufficient, Tier A lines are allocated first, then Tier B, then Tier C. This rule is enforced in the ATP engine and reflected in the risk classification: a Tier C shortage with Tier A lines fully covered does not escalate to CRITICAL.

4. **ATP Accuracy measurement excludes documented force-majeure events.** Deliveries delayed by carrier force-majeure events are excluded from the ATP Accuracy denominator when a force_majeure_flag is set by the Logistics team within 48 hours of the event. The excluded count is reported separately as a transparency metric.

5. **Order-to-Cash cycle time uses working hours for internal intervals, calendar days for collection.** T_entry through T_invoice are expressed in working hours (internal process SLAs). T_collection (invoice to payment) is measured in calendar days (contractual payment terms).

6. **Soft-delete only.** Order lines, ATP commitments, and complaint records must never be hard-deleted. Set is_deleted = 1 and exclude via standard filter. Historical audit trail must be preserved in full.

7. **Idempotency on EDI 850 ingestion.** The second EDI 850 submission with the same idempotency key triggers an update to the existing order, not duplicate order creation.

8. **Credit hold orders are excluded from the open order at-risk analysis.** An order on credit hold is blocked by a commercial decision, not a supply constraint. Exclude status = CREDIT_HOLD from MART_OPEN_ORDER_RISK and surface it separately in a credit exposure report.

9. **Invoice accuracy is binary.** An invoice is correct (zero discrepancies between invoice, packing list, and customer PO) or incorrect. Any price discrepancy, quantity variance, or missing certificate of analysis sets correct_docs_flag = 0.

10. **Complaint rate denominator is shipped orders, not total orders.** A complaint can only arise from a shipped order. Denominator = count of distinct orders with status SHIPPED or beyond.

---

## 10. KPIs and Formulas

### 10.1 Order Fill Rate

```
Order Fill Rate (%) =
    Lines shipped complete and on time
    ─────────────────────────────────────── × 100
    Total order lines (excluding cancelled)
```

- "Complete" = shipped_qty / ordered_qty >= retailer-specific in_full_threshold_pct
- "On time" = actual delivery date <= ATP committed delivery date (LPEIN)
- Computed at line level; rolled to order, customer, and period
- Targets: >= 95% internal; retailer-specific targets per Section 8.3
- Frequency: Daily; 4-week and 13-week rolling averages reported

### 10.2 Perfect Order Rate

```
Perfect Order Rate =
    OTD_rate × OTIF_rate × Order_Accuracy_rate × No_Damage_rate
```

All four factors as decimals (0.0 to 1.0), then multiplied:

```
OTD_rate         = mean(on_time_flag)        across all lines in period
OTIF_rate        = mean(in_full_flag)        across all lines in period
Order_Accuracy   = mean(correct_docs_flag)   across all lines in period
No_Damage_rate   = mean(damage_free_flag)    across all lines in period

Perfect Order Rate = OTD_rate × OTIF_rate × Order_Accuracy × No_Damage_rate
```

Example: OTD=0.96, OTIF=0.97, Accuracy=0.99, No_Damage=0.995
Perfect Order Rate = 0.96 × 0.97 × 0.99 × 0.995 = 0.9186 = **91.9%**

- Target: >= 95% enterprise-wide
- Benchmarks: FMCG >= 95%; Automotive Tier-1 >= 98.5%; Pharma GDP >= 99%
- Frequency: Weekly calculation; monthly executive reporting

### 10.3 Order Cycle Time (OCT)

```
OCT (working days) = Ship date − Order confirmed date
```

- Ship date: goods issue date from SAP LIKP.WADAT
- Order confirmed date: ORDER_CONFIRMED event timestamp
- Expressed in working days (factory calendar)
- Target: <= 2 working days for D1 stocked products via EDI
- Alert threshold: OCT > 5 working days any channel

### 10.4 ATP Accuracy

```
ATP Accuracy (%) =
    Orders promised and delivered on or before ATP promise date
    ──────────────────────────────────────────────────────────── × 100
                     Total ATP promises (delivered, non-force-majeure)
```

- Numerator: ATP commitments where actual_delivery_date <= promised_delivery_date
- Denominator: all commitments for delivered orders excluding force-majeure exclusions
- Target: >= 92%
- Sub-metric: mean days_variance (positive = late vs. promise)

### 10.5 Open Order At-Risk Rate

```
Open Order At-Risk Rate (%) =
    Open order lines classified CRITICAL or HIGH risk
    ─────────────────────────────────────────────────── × 100
              Total open order lines
```

Risk classification logic defined in Section 11.1.

- Target: < 5% of open lines at CRITICAL or HIGH risk at any daily snapshot
- Alert: Any Tier A customer line classified CRITICAL triggers immediate CSR escalation notification

### 10.6 Order-to-Cash Cycle Time

```
O2C Total (calendar days) = Invoice paid date − Customer PO receipt date
```

Decomposed into seven sub-intervals:

```
O2C = T_entry + T_credit + T_atp + T_pick + T_transit + T_invoice + T_collection
```

| Interval | Description | Unit |
|----------|-------------|------|
| T_entry | Order receipt to order confirmed | Working hours |
| T_credit | Order confirmed to credit check passed | Working hours |
| T_atp | Credit passed to ATP committed | Working hours |
| T_pick | ATP committed to order shipped (goods issue) | Working days |
| T_transit | Order shipped to carrier delivery confirmed | Calendar days |
| T_invoice | Delivery confirmed to invoice sent | Working hours |
| T_collection | Invoice sent to payment received | Calendar days |

- Target total: <= 35 calendar days (NET 30 terms baseline)
- Internal process target (T_entry through T_invoice): <= 5 working days
- Frequency: Monthly trend; bottleneck interval highlighted each period

### 10.7 Backorder Rate

```
Backorder Rate (%) =
    Lines currently on backorder
    ────────────────────────────── × 100
     Total open order lines
```

- Target: < 3%
- 13-week rolling trend to identify seasonal patterns by SKU family

### 10.8 Customer Complaint Rate

```
Customer Complaint Rate (%) =
    Distinct complaints filed
    ────────────────────────── × 100
     Total orders shipped
```

- Target: < 1%
- Frequency: Weekly; rolling 4-week average

---

## 11. Analytical Logic

### 11.1 Open Order Risk Classification

Risk classification runs daily over all open order lines (status in CONFIRMED, ATP_COMMITTED, IN_PICKING). Each line receives one of four risk levels.

**Input variables per line:**

| Variable | Source |
|----------|--------|
| days_to_promise | calendar days from today to committed_delivery_date |
| on_hand_available | current uncommitted on-hand quantity from inventory ATP service |
| confirmed_inbound_qty | confirmed PO or production order qty arriving before promised delivery |
| ordered_qty | quantity still to be shipped on this line |
| customer_tier | TIER_A / TIER_B / TIER_C from DIM_CUSTOMER |

**Classification logic:**

```
shortage_qty = max(0, ordered_qty - on_hand_available - confirmed_inbound_qty)

CRITICAL:
  shortage_qty > 0
  AND supply will not arrive within days_to_promise
  AND (days_to_promise <= 2 OR customer_tier = 'TIER_A')

HIGH:
  shortage_qty > 0
  AND supply will not arrive within days_to_promise
  AND days_to_promise <= 5
  AND not already classified CRITICAL

MEDIUM:
  shortage_qty > 0
  AND supply will not arrive within days_to_promise
  AND days_to_promise > 5
  AND shortage_qty / ordered_qty > 0.10

LOW:
  shortage_qty > 0
  AND shortage_qty / ordered_qty <= 0.10
  OR supply arriving in time (supply_arrival_date <= committed_delivery_date)

NONE:
  shortage_qty = 0 (fully covered by on-hand + confirmed inbound)
```

**Priority escalation override:** Any Tier A customer line upgrades one risk level (LOW to MEDIUM, MEDIUM to HIGH, HIGH to CRITICAL) if days_to_promise <= 3, regardless of shortage quantity.

### 11.2 Order-to-Cash Sub-Interval Bottleneck Identification

For each customer segment and channel, compute the mean and 90th-percentile value for each interval. The bottleneck is the interval with the highest ratio of (P90 / Target SLA). This ratio drives improvement prioritisation.

| Interval | Target SLA | Bottleneck Signal |
|----------|-----------|------------------|
| T_entry | < 2h EDI; < 4h Manual | P90 > 3x target |
| T_credit | < 1h auto; < 4h manual | P90 > 3x target |
| T_atp | < 30min standard; < 4h MTO | P90 > 3x target |
| T_pick | 1 day D1; 3 days D2 | P90 > 2x target |
| T_transit | Per routing guide | P90 > 1.5x target |
| T_invoice | < 4h automated | P90 > 3x target |
| T_collection | Per payment terms | Mean > terms + 3 days |

### 11.3 Customer Tier Priority Logic

Customer tier is computed quarterly from 12-month rolling net revenue:

- **Tier A**: Top 20% of customers by revenue (typically represents 70–80% of total revenue)
- **Tier B**: Next 30% of customers by revenue (~15% of total revenue)
- **Tier C**: Bottom 50% of customers by revenue (~5–10% of total revenue)

Tier classification is stored in DIM_CUSTOMER and recalculated quarterly. Mid-quarter reclassification is blocked. New customers default to Tier C for their first full quarter, then reclassify based on actual revenue.

Tier A service differentiators:
- First-priority ATP allocation during shortage (Business Rule 3)
- Same-day CSR response SLA for complaints
- Automatic CRITICAL risk alert notifications
- Weekly OTIF performance review with account manager

---

## 12. Validations and Controls

### 12.1 Daily Automated Data Quality Checks

| Check | Logic | Alert Threshold | Owner |
|-------|-------|-----------------|-------|
| Orders without customer mapping | COUNT FACT_ORDER_LINE WHERE customer_key IS NULL | > 0 | MDM team |
| ATP commitments with null promised date | COUNT ATP_COMMITMENTS WHERE promised_delivery_date IS NULL AND order_status = 'CONFIRMED' | > 0 | Order Mgmt IT |
| Negative line values (excluding credit memos) | COUNT FACT_ORDER_LINE WHERE line_value_cents < 0 AND fkart != 'G2' | > 0 | Finance |
| Fill rate out of range | MART_ORDER_FILL_RATE WHERE fill_rate_pct NOT BETWEEN 0 AND 100 | Any row | Analytics |
| O2C interval reversal | MART_O2C_CYCLE_TIME WHERE any interval column < 0 | Any row | Analytics |
| Orphaned delivery lines | LIPS rows with no matching VBAK sales order | > 5 per day | IT Integration |
| EDI 810 without matching order | EDI_TRANSACTIONS type='810' with order_reference not in VBAK | > 0 | EDI team |
| Stale ATP commitments | ATP_COMMITMENTS for orders with order_status = CANCELLED | > 0 | Order Mgmt IT |

### 12.2 Monthly KPI Reconciliation Controls

Reconcile monthly between:
- Power BI fill rate (MART_ORDER_FILL_RATE) vs. SAP S/4HANA standard OTIF report (VL06O or equivalent). Tolerance: < 0.5 percentage points.
- O2C mean days average vs. DSO from SAP FI aging report. Tolerance: < 1 day.
- Complaint count vs. SAP QM notification count (if QM module active). Tolerance: exact match.

Discrepancies exceeding tolerance must be investigated and resolved before month-close reporting is distributed to VP level.

### 12.3 Access Controls

- FACT_ORDER_LINE: read-only for Analytics team and Power BI service account
- ATP_COMMITMENTS: write access only for ATP service account; read for Analytics
- Customer credit data (KLIMK, credit exposure): restricted to Finance and Order Management leads; masked in CSR-facing Power BI views
- MART_OPEN_ORDER_RISK: CSR access scoped to assigned customer portfolio via Power BI row-level security

---

## 13. Required Evidence

The following evidence items must be documented and signed off before go-live:

1. **SAP data extraction test**: Extract 3 months of VBAK, VBAP, LIKP, LIPS to Azure SQL staging. Validate row counts and critical field completeness against SAP standard reports. Sign-off by IT lead.

2. **Fill rate baseline calculation**: Run MART_ORDER_FILL_RATE for the most recent complete quarter. Validate against the manually computed fill rate from the existing Customer Service spreadsheet. Difference must be < 1 percentage point. Sign-off by Order Management Lead.

3. **Customer tier classification approval**: Present Tier A/B/C customer list to VP of Sales. Confirm that revenue-based classification aligns with commercial segmentation intent.

4. **ATP Accuracy baseline**: For orders shipped in the last 90 days, compute ATP Accuracy from ATP_COMMITMENTS log. Present to Order Management lead. Document any result below 85% with root-cause explanation.

5. **O2C event timestamp completeness audit**: For a 30-day sample of paid orders, verify all seven event timestamps are populated and in chronological sequence. Target: >= 90% of orders with complete event chains before go-live.

6. **Retailer OTIF calculation validation**: For Walmart and Target accounts, run the OTIF calculation for the last complete month. Cross-validate against the retailer's vendor scorecard portal. Resolve any discrepancies with the retailer's vendor relations team before publishing the KPI.

---

## 14. Dashboard Design

### 14.1 Page 1 — Daily Order Risk Command Centre

**Audience**: Customer Service Representatives; Order Management Lead (daily use)

**Layout:**
- Top bar: Four KPI summary tiles — Open Order At-Risk Rate (CRITICAL + HIGH %); Total lines at risk (count); Tier A lines at CRITICAL risk (count — red alert badge if > 0); Today's promised shipments (count due today)
- Centre: Risk heatmap table — rows = CSR owner; columns = risk level; cells = line count with conditional formatting (CRITICAL = red, HIGH = amber, MEDIUM = yellow, LOW = green)
- Right panel: Drill-down to individual at-risk lines — Order Number, Customer Name, SKU, Ordered Qty, Shortage Qty, Days to Promise, Risk Level, Assigned CSR
- Bottom: 30-day At-Risk Rate trend sparkline with target reference line at 5%

**Slicers**: Customer Tier; Warehouse; Risk Level (multi-select); Assigned CSR

### 14.2 Page 2 — Perfect Order Rate and Fill Rate

**Audience**: Order Management Lead; VP Supply Chain (weekly)

**Layout:**
- Top: Perfect Order Rate gauge (current month vs. 95% target) and four factor metric cards (OTD%, In-Full%, Accuracy%, No Damage%)
- Centre left: Waterfall chart — factor decomposition showing each dimension's contribution to POI gap vs. 95% target
- Centre right: 13-week line chart — Perfect Order Rate trend with 95% target reference line
- Bottom: Table by customer tier — Tier A / B / C performance on each dimension vs. prior period delta

**Slicers**: Period (week / month / quarter); Channel; Fulfillment Type; Customer Tier

### 14.3 Page 3 — Order-to-Cash Cycle Time

**Audience**: Finance/AR; VP Order Management (monthly)

**Layout:**
- Top: Summary metrics — Average O2C days; Median O2C; P90 O2C; T_collection mean (DSO proxy)
- Centre: Stacked bar chart — mean days per interval (T_entry through T_collection) by channel and fulfillment type
- Right: Bottleneck highlight card — interval with highest P90/Target SLA ratio, with colour-coded severity
- Bottom: Top 20 customers by T_collection (descending) — payment terms vs. actual collection days; highlight customers exceeding terms by > 5 days

**Slicers**: Period; Channel; Customer Tier; Fulfillment Type

### 14.4 Page 4 — ATP Promise Accuracy

**Audience**: Order Management IT; Demand Planning; VP Operations (weekly)

**Layout:**
- Top: ATP Accuracy % (current period); Mean days_variance; % promises late by > 3 days; Force-majeure exclusion count
- Centre: Scatter plot — SKU vs. ATP Accuracy % with bubble size = order volume; flag SKUs below 85% in red
- Bottom left: Warehouse-level accuracy comparison table
- Bottom right: 13-week rolling ATP Accuracy trend by commitment method (ATP vs. CTP)

### 14.5 Page 5 — Customer Service Level by Segment

**Audience**: Account Management; VP Sales; Customer Experience lead (weekly)

**Layout:**
- Top: Fill rate cards by tier — Tier A / B / C with month-over-month delta arrows
- Centre: Retailer OTIF compliance matrix — rows = retailer; columns = current OTIF%, compliance threshold, penalty exposure (USD cents converted from line value exposure)
- Bottom: Complaint category distribution bar chart and Customer Complaint Rate 13-week trend

---

## 15. Use Cases

### 15.1 Daily At-Risk Order Intervention

**Trigger**: Morning daily batch updates MART_OPEN_ORDER_RISK at 06:00 UTC. Power BI refreshes at 06:30 UTC. CSR team begins shift at 07:00 UTC.

**Workflow**: CSR opens Page 1. Reviews all CRITICAL lines in their portfolio. For each CRITICAL line: (a) checks if additional supply can be expedited from an alternate warehouse; (b) contacts carrier for expedite routing if goods issue is imminent; (c) if delay is unavoidable, contacts customer proactively before the ship window closes and commits a revised delivery date. All actions logged in SAP CRM activity.

**Expected business impact**: Proactive contact before a miss reduces customer complaint rate by 8–15 CSAT points. Complaint rate target reduction: 25% within 90 days of go-live.

### 15.2 Walmart OTIF Compliance Monitoring

**Trigger**: Weekly, Monday morning, after SAP SD weekly close.

**Workflow**: Order Management Lead filters Page 2 to retailer_standard = WALMART. Reviews current 4-week OTIF against 98% threshold. Identifies contributing order lines. Root-cause analysis: late delivery (carrier) vs. short shipment (supply) vs. documentation (ASN/invoice mismatch). Escalates to Procurement for safety stock review or to Logistics for carrier routing guide adjustment.

**Financial impact**: At $10M annual Walmart account revenue, a sustained 2-point OTIF miss = $600K annual penalty exposure (3% of invoice).

### 15.3 Month-End O2C Cycle Time Review

**Trigger**: First Monday of each month, covering the prior calendar month.

**Workflow**: Finance lead opens Page 3. Compares actual mean O2C vs. 35-day target. Identifies bottleneck interval (highest P90/Target ratio). Presents findings in Operations Review with VP. For T_collection outliers, triggers AR follow-up and potential credit term renegotiation with the customer.

### 15.4 ATP Configuration Tuning

**Trigger**: Weekly, when ATP Accuracy falls below 90% for two consecutive weeks.

**Workflow**: Order Management IT opens Page 4. Identifies SKUs with accuracy below 85%. Investigates common pattern — one warehouse, one SKU family, one time of day? Adjusts ATP safety buffer parameters or lead time assumptions. Re-measures accuracy the following week.

---

## 16. Recommended Actions

### 16.1 Immediate (Days 1–30)

1. Deploy MART_OPEN_ORDER_RISK daily refresh and publish Page 1 to CSR team. Eliminate manual Excel-based open order tracking immediately.
2. Establish ATP Accuracy baseline from 90 days of ATP_COMMITMENTS history. Identify top 10 under-performing SKUs.
3. Align Walmart and Target OTIF calculation methodology with retailer vendor relations teams. Document agreed delivery date definition before publishing compliance KPIs.

### 16.2 Short-Term (Days 31–90)

4. Implement O2C event timestamps across all channels. Achieve >= 90% timestamp completeness before proceeding to MART_O2C_CYCLE_TIME production use.
5. Automate Tier A CRITICAL alert — push notification to CSR and Order Management Lead when any Tier A line is classified CRITICAL during the daily batch.
6. Complete fill rate baseline reconciliation against SAP VL06O standard OTIF report. Resolve discrepancies and obtain sign-off from Order Management Lead.

### 16.3 Medium-Term (Days 91–180)

7. Deploy XGBoost order delay prediction model. Integrate delay probability score into Page 1 risk display as a forward-looking signal alongside the stock-based at-risk classification.
8. Implement automated ATP buffer recalibration — weekly adjustment of safety buffer for SKUs where ATP Accuracy falls below 90% for two consecutive weeks.
9. Build EDI 856 ASN accuracy tracking — measure rate at which ASN data matches actual delivery within 1% quantity tolerance. Target: >= 99% ASN accuracy.

---

## 17. Test Cases

### 17.1 Fill Rate Calculation

**TC-FILL-001**
Input: 100 order lines; 88 shipped complete and on time; 5 on backorder; 7 cancelled.
Expected: Fill rate = 88 / (100 - 7) × 100 = 94.6%.
Validation: Cancelled lines excluded from denominator.

**TC-FILL-002**
Input: Walmart order; ordered_qty = 1000 units; shipped_qty = 999 units.
Expected: in_full_flag = 0 (Walmart requires 100%; 999/1000 = 99.9% fails).
Validation: Retailer-specific threshold applied correctly.

**TC-FILL-003**
Input: Non-retail customer; ordered_qty = 1000 units; shipped_qty = 952 units.
Expected: in_full_flag = 1 (952/1000 = 95.2% >= 95.0% default threshold).
Validation: Default threshold applied when retailer_standard = OTHER.

### 17.2 Perfect Order Rate

**TC-POI-001**
Input: OTD=0.96, OTIF=0.97, Accuracy=0.99, NoDamage=0.995.
Expected: POI = 0.96 × 0.97 × 0.99 × 0.995 = 0.91862 ≈ 91.9%.
Validation: Multiplicative model; result in [0, 1].

**TC-POI-002**
Input: Any single dimension = 0.
Expected: POI = 0 regardless of other dimensions.
Validation: Multiplicative model — one zero eliminates POI.

### 17.3 Open Order Risk Classification

**TC-RISK-001**
Input: ordered_qty=100; on_hand_available=30; confirmed_inbound_qty=40; days_to_promise=4; customer_tier=TIER_B.
Expected: shortage_qty=30; at_risk_level=HIGH.

**TC-RISK-002**
Input: ordered_qty=100; on_hand_available=30; confirmed_inbound_qty=40; days_to_promise=2; customer_tier=TIER_A.
Expected: at_risk_level=CRITICAL (shortage + Tier A + days_to_promise <= 2).

**TC-RISK-003**
Input: ordered_qty=100; on_hand_available=100; confirmed_inbound_qty=0; days_to_promise=3.
Expected: shortage_qty=0; at_risk_level=NONE.

**TC-RISK-004**
Input: ordered_qty=100; on_hand_available=95; confirmed_inbound_qty=0; days_to_promise=10; customer_tier=TIER_C.
Expected: shortage_qty=5; shortage_pct=0.05 (5%); at_risk_level=LOW (shortage <= 10%).

### 17.4 ATP Accuracy

**TC-ATP-001**
Input: promised_delivery_date=2026-07-01; actual_delivery_date=2026-07-01.
Expected: days_variance=0; promise_kept_flag=1.

**TC-ATP-002**
Input: promised_delivery_date=2026-07-01; actual_delivery_date=2026-07-03.
Expected: days_variance=2; promise_kept_flag=0.

**TC-ATP-003**
Input: promised_delivery_date=2026-07-01; actual_delivery_date=2026-06-30; force_majeure_flag=0.
Expected: days_variance=-1; promise_kept_flag=1 (delivered early).

### 17.5 O2C Cycle Time

**TC-O2C-001**
Input: Seven event timestamps with T_total span of 32 calendar days; T_collection=28 days; NET_30 payment terms.
Expected: t_total_o2c_days=32; t_collection_days=28; within contract terms.

**TC-O2C-002**
Input: Any interval where end_timestamp < start_timestamp.
Expected: Validation error raised; record excluded from MART_O2C_CYCLE_TIME with error_flag = 1.

**TC-O2C-003**
Input: T_collection_days = 185 (aged/disputed order).
Expected: Row excluded from mean calculation per cap rule (max 180 days); included in aged AR report.

---

## 18. Risks and Mitigations

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| SAP ODP extraction latency exceeds 15-minute target during month-end peaks | Medium | High | Implement queue-based extraction with priority ordering; add dedicated Azure SQL reader instance; alert at > 30 minutes extraction lag |
| Goods issue posting date in SAP lags actual physical ship by up to 24 hours | High | Medium | Document date-adjustment rule: if WADAT posted between 17:00 and 23:59 local time, treat ship date as WADAT; align with warehouse operations |
| ATP commitment log missing for pre-system-migration historical orders | High | Medium | For pre-migration orders, use VBEP.LPEIN as proxy promised date; flag as LEGACY_PROXY in atp_method column; exclude from ATP Accuracy KPI if volume exceeds 10% of denominator |
| Retailer OTIF calculation discrepancy (internal definition vs. retailer portal) | Medium | High | Formal alignment session with each retailer before publishing retailer-specific OTIF; document agreed rules in a Retailer OTIF Methodology register; validate monthly against portal |
| Customer master tier classification stale between quarterly updates | Low | Medium | Add last_tier_review_date to DIM_CUSTOMER; flag customers where last_tier_review_date > 95 days in data quality check |
| Power BI row-level security misconfiguration exposes Tier A customer data to other CSRs | Low | High | Implement RLS on CSR-customer assignment table; include in pre-go-live penetration test; separate test case in UAT script |
| EDI 850 resubmission creates duplicate sales orders before idempotency validation | Medium | High | Validate idempotency key in EDI middleware before creating SAP sales order; maintain deduplication log with 90-day retention |
| XGBoost delay model underperforms on new customer segments not in training data | Low | Medium | Flag predictions with confidence < 0.60 for manual CSR review; retrain quarterly with rolling 12-month data |

---

## 19. Implementation Checklist

### Phase 1: Data Foundation (Weeks 1–4)

- [ ] SAP S/4HANA ODP extraction configured for VBAK, VBAP, VBEP, VBFA, LIKP, LIPS, VBRK, VBRP, BSID, BSAD, KNA1, KNB1, KNVV, MARA, TCURR
- [ ] Azure SQL staging schema created with all source tables and correct data types
- [ ] DIM_CUSTOMER loaded with tier classification and retailer_standard field
- [ ] DIM_SKU loaded with ABC/XYZ class, lead_time_days, atp_safety_buffer
- [ ] DIM_DATE populated 2020-01-01 to 2030-12-31 with working day flag from SAP SCAL
- [ ] Exchange rate (TCURR) daily refresh configured
- [ ] EDI transaction log connected and validated
- [ ] ATP_COMMITMENTS table accessible and populated with 90-day history

### Phase 2: Fact Tables and Marts (Weeks 5–8)

- [ ] FACT_ORDER_LINE daily snapshot pipeline built and running; row count validation passing
- [ ] All binary flags (on_time, in_full, damage_free, correct_docs, perfect_order, backorder, at_risk) computed and spot-checked
- [ ] MART_ORDER_FILL_RATE built and reconciled against SAP VL06O report (< 1pp difference)
- [ ] MART_PERFECT_ORDER built and validated on 90-day sample
- [ ] MART_O2C_CYCLE_TIME built; event timestamp completeness > 90%
- [ ] MART_ATP_ACCURACY built; baseline accuracy computed for 90-day history
- [ ] MART_OPEN_ORDER_RISK built; daily refresh at 06:00 UTC configured and tested
- [ ] All automated data quality checks (Section 12.1) deployed with alerting

### Phase 3: Dashboard and User Acceptance (Weeks 9–13)

- [ ] All five Power BI pages built per Section 14 specifications
- [ ] Row-level security implemented and tested for CSR portfolio scope
- [ ] Tier A CRITICAL alert push notification configured
- [ ] Retailer OTIF methodology validated with Walmart and Target
- [ ] Fill rate baseline reconciliation completed and signed off by Order Management Lead
- [ ] User acceptance testing with CSR team, Order Management Lead, Finance lead
- [ ] Training delivered to all CSR users (minimum 60 minutes hands-on)
- [ ] Go-live approval signed off by VP Order Management

---

## 20. Validation Checklist

### Data Validation

- [ ] FACT_ORDER_LINE row count matches SAP line count for the same period within 0.1%
- [ ] Sum of line_value_cents matches SAP S/4HANA revenue report within 0.5%
- [ ] Zero rows with negative on_hand_available, ordered_qty, or shipped_qty
- [ ] All at_risk_level values are one of: CRITICAL / HIGH / MEDIUM / LOW / NONE
- [ ] All ATP promised dates >= order creation date
- [ ] All O2C sub-interval values are non-negative
- [ ] No cancelled lines appearing in fill rate denominator
- [ ] Credit memo lines (FKART = 'G2') excluded from fill rate calculation

### KPI Validation

- [ ] Fill rate for last complete month matches Customer Service existing report within 1 percentage point
- [ ] Perfect Order Rate factor decomposition: product of four factors matches directly computed POI within epsilon = 0.001
- [ ] Backorder rate for last week validated against SAP backorder report (VL06O or equivalent)
- [ ] O2C mean days within 2 calendar days of Finance DSO estimate for the same period
- [ ] ATP Accuracy cross-validated against at least 3 months of actual vs. promised delivery date pairs

### Dashboard Validation

- [ ] All five Power BI pages render within 5 seconds at full production data volume
- [ ] All slicers and drill-downs function correctly
- [ ] RLS: CSR users cannot access customers outside their assigned portfolio
- [ ] Tier A CRITICAL alert fires correctly in UAT environment for a simulated CRITICAL line
- [ ] All KPI results match expected outputs in test cases from Section 17

---

## 21. Pending Information

| Item | Required From | Needed By | Blocking Component |
|------|--------------|-----------|-------------------|
| Walmart OTIF delivery date definition (retailer DC receipt vs. carrier last scan) | VP Customer Service + Walmart vendor relations | Week 3 | MART_ORDER_FILL_RATE Walmart segment |
| Force-majeure event type list qualifying for ATP Accuracy exclusion | VP Logistics | Week 4 | MART_ATP_ACCURACY force_majeure_excluded logic |
| Customer tier boundary revenue thresholds for current fiscal year | VP Sales | Week 2 | DIM_CUSTOMER tier classification |
| SAP factory calendar code (SCAL identifier) for working days calculation | IT SAP Basis team | Week 1 | DIM_WORKING_DAY |
| EDI partner IDs for all active retail customers | IT EDI team | Week 2 | EDI transaction source table mapping |
| In-full threshold for non-retail customers (internal policy confirmation) | VP Order Management | Week 3 | FACT_ORDER_LINE in_full_flag business rule |
| Credit memo inclusion/exclusion rule for fill rate denominator | Finance Director | Week 3 | Business Rule 1 implementation |
| CSR-to-customer portfolio assignment table for Power BI RLS | Customer Service Manager | Week 8 | Dashboard row-level security |

---

## 22. Implementation Roadmap

### Quarter 1 (Weeks 1–13): Data Foundation and Core KPIs

| Week | Milestone | Owner |
|------|-----------|-------|
| 1–2 | SAP ODP extraction live; Azure SQL staging operational | IT Data Engineering |
| 3–4 | All dimension tables loaded; FACT_ORDER_LINE daily pipeline live | Analytics Engineering |
| 5–6 | MART_ORDER_FILL_RATE and MART_PERFECT_ORDER built and validated | Analytics Engineering |
| 7–8 | MART_O2C_CYCLE_TIME and MART_ATP_ACCURACY built | Analytics Engineering |
| 9 | MART_OPEN_ORDER_RISK daily refresh live; all data quality alerts deployed | Analytics Engineering |
| 10–11 | Power BI Pages 1–3 built and in UAT with CSR and Order Management lead | Analytics + Business |
| 12 | Pages 4–5 built; retailer OTIF validated with Walmart and Target | Analytics + Customer Service |
| 13 | Go-live: all five pages published to production; CSR team trained | Programme Manager |

### Quarter 2 (Weeks 14–26): Advanced Analytics and Automation

| Week | Milestone | Owner |
|------|-----------|-------|
| 14–16 | Retailer OTIF compliance report validated and signed off with all retailers | Customer Service + IT |
| 17–18 | Tier A CRITICAL automated push notification deployed (Power BI + email) | Analytics Engineering |
| 19–22 | XGBoost order delay prediction model trained; delay probability score added to FACT_ORDER_LINE | Data Science |
| 23–24 | ATP buffer auto-recalibration logic built and tested | Order Mgmt IT |
| 25–26 | Month 6 KPI review: baselines established; improvement targets set for next 6 months | VP Order Management |

### Quarter 3 (Weeks 27–39): Optimisation and Continuous Improvement

| Week | Milestone | Owner |
|------|-----------|-------|
| 27–30 | EDI 856 ASN accuracy tracking deployed; ASN match rate KPI added to Page 5 | IT EDI + Analytics |
| 31–33 | NLP complaint classifier integrated with CSR routing system | Data Science + CS IT |
| 34–36 | RL order promising model pilot (non-Tier A orders, single warehouse) | Data Science |
| 37–39 | Full analytics suite transitioned to BAU ownership; IT Ops SLA signed | Programme Manager |

### Success Criteria at Programme Close (Week 39)

| KPI | Baseline (Week 1) | Target (Week 39) |
|-----|-------------------|------------------|
| Open Order At-Risk Rate (CRITICAL + HIGH) | Measured at go-live | < 5% |
| Perfect Order Rate | Measured at go-live | >= 95% |
| ATP Accuracy | Measured at go-live | >= 92% |
| O2C Cycle Time | Measured at go-live | Reduce by >= 5 calendar days |
| Customer Complaint Rate | Measured at go-live | < 1% |
| CSR daily active Power BI users | 0 | >= 90% of CSR team |

---

## References

- SCOR Digital Standard v4.0, ASCM (2023) — RS.1.1 Order Fulfillment Cycle Time; AG.1.1–1.3 Agility metrics
- SAP S/4HANA SD Configuration Guide, SAP SE (2025)
- Walmart Supplier Manual — Transportation and Routing Guide (2025)
- Target Vendor Guide — Supplier Standards and Expectations (2025)
- Amazon Vendor Central — Fill Rate and OTIF Requirements (2025)
- Chopra, S. and Meindl, P., *Supply Chain Management: Strategy, Planning, and Operation*, 6th Ed. (Pearson, 2016) — Chapter 3: Supply Chain Drivers and Metrics
- Christopher, M., *Logistics and Supply Chain Management*, 6th Ed. (FT Publishing, 2022) — Customer service and order cycle time
- APICS Dictionary 16th Ed. (ASCM, 2024) — Perfect Order Index; Order Fill Rate; DSO definitions
- GS1 General Specifications v23.0 — UOM codes, GTIN, GLN, SSCC
- Incoterms 2020, ICC (2019)
- ISO 9001:2015, §8.2 — Requirements for products and services
- US GAAP ASC 606 — Revenue from Contracts with Customers
- IFRS 15 — Revenue from Contracts with Customers
- `src/departments/02-inventory/` — Event-sourced inventory; ATP stock query
- `src/departments/08-logistics/` — Shipment domain, carrier integration
- `src/departments/10-warehouse/` — FEFO picking, WMS reservation, goods issue
- `src/shared/types.ts` — Money, UOM, ISOTimestamp, INCOTERMS_2020

---

*End of Implementation Guide — Department 13: Order Management Analytics*

*Classification: Internal — Senior Consultant Grade. All amendments must be reviewed by the Supply Chain Programme Director.*
