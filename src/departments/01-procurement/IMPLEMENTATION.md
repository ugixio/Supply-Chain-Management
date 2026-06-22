# Procurement Analytics — Data & Analytics Implementation Document

**Department**: Procurement  
**Workstream**: Purchase Order Follow-up, Open Orders Risk, Spend Analysis, Supplier Compliance  
**Organization**: €50B Global Multinational | 40 Countries | 10,000+ Active Suppliers  
**Technology Stack**: SAP S/4HANA · SAP Ariba · PostgreSQL · Apache Superset · Python · Apache Airflow  
**Document Version**: 1.0  
**Last Updated**: 2026-06-22  
**Classification**: Internal — Restricted

---

## 1. Executive Summary

Procurement is the largest single controllable cost lever in a €50B global multinational. Direct and indirect spend typically represents 50–70% of total revenue, meaning even a 2% efficiency gain generates €500M–€700M in measurable bottom-line impact. This implementation document provides a rigorous, technically complete specification for the Procurement Analytics workstream, translating raw transactional data from SAP S/4HANA and SAP Ariba into actionable intelligence across four analytical domains: Purchase Order (PO) Follow-up, Open Orders Risk, Spend Analysis, and Supplier Compliance (UFLPA and CSDDD).

The analytics architecture is built on a PostgreSQL data warehouse feeding Apache Superset dashboards, with Python-based transformation pipelines orchestrated via Apache Airflow and monitored through Apache Airflow alerts. The data model follows a star schema optimized for slice-and-dice analysis across 40 countries, 14 commodity categories, and the full supplier base.

Regulatory compliance coverage spans the US Uyghur Forced Labor Prevention Act (UFLPA, Pub.L. 117-78, effective June 2022), the EU Corporate Sustainability Due Diligence Directive (CSDDD, Directive 2024/1760, phased enforcement from 2027), and EU REACH Regulation 1907/2006. Non-compliance exposure at this revenue scale represents fines up to 5% of global turnover (CSDDD Art. 22) and US import bans with seizure of goods.

The primary deliverable is an Apache Superset solution with five report pages, automated daily data refresh, and Apache Airflow alerts for high-risk purchase orders, overdue deliveries, and compliance flags.

---

## 2. Analysis Objective

The Procurement Analytics workstream has the following measurable objectives:

1. **Reduce PO Cycle Time**: Achieve full visibility into PO status from creation to goods receipt, targeting a 15% reduction in average PO cycle time within 6 months of go-live.
2. **Open Order Risk Quantification**: Identify, score, and escalate at-risk open purchase orders (overdue, no confirmation, high-value, single-sourced) before they cause supply disruptions.
3. **Spend Under Management (SUM)**: Increase the percentage of total spend routed through approved channels (Ariba catalogue or PO-based) from a baseline to a ≥90% target.
4. **Supplier Compliance Monitoring**: Maintain 100% UFLPA screening coverage for high-risk country-of-origin suppliers and achieve CSDDD Art. 7 due diligence documentation for Tier-1 suppliers before the 2027 enforcement deadline.
5. **Maverick Spend Elimination**: Detect and quantify off-contract spend (invoices with no prior PO) and route correction actions to category managers within 48 hours.

---

## 3. Scope

### In Scope

- All purchase orders created in SAP S/4HANA (company codes: all 40 country entities)
- Ariba Network sourcing events linked to S/4HANA POs via integration
- PO types: standard (NB), framework orders (MK), consignment (KO), subcontracting (LB), service (DIEN)
- Spend categories: Direct Materials, Indirect MRO, Logistics & Freight, Professional Services, IT
- Supplier master data maintained in SAP S/4HANA (LFA1/LFB1) and Ariba SLP
- UFLPA risk screening: suppliers with manufacturing or sourcing operations in Xinjiang (XUAR), China
- CSDDD: all Tier-1 suppliers with annual spend ≥ €1M per legal entity
- Countries in scope: all 40 operating countries; reporting currency: EUR

### Out of Scope

- Inter-company purchase orders (document type UB)
- Capital expenditure orders (account assignment category A) — handled by Finance CapEx module
- Emergency credit card purchases below €500 (P-Card) — handled by Accounts Payable
- Tier-2 and Tier-3 CSDDD mapping (Phase 2, post-2028)

### Reporting Period

- Historical load: 3 years (2023-01-01 to present) for trend analysis
- Operational window: rolling 12 months for open order management
- CSDDD retention: 5 years minimum per Art. 23

---

## 4. Business Questions

This analytics implementation answers the following specific business questions:

- Which purchase orders are overdue (confirmed delivery date passed, no goods receipt posted) and what is the total value at risk by commodity and country?
- What percentage of total company spend is routed through approved procurement channels (PO-backed or catalogue), and which cost centers have the highest maverick spend rate?
- Which suppliers have not confirmed purchase orders within the standard 48-hour confirmation window, and what is the downstream delivery risk if no action is taken?
- What is the spend concentration by supplier (top-10 supplier as % of total spend) and how has it trended over the past 3 years by category?
- Which suppliers in our active base have manufacturing operations in Xinjiang and have not provided the required UFLPA clearance documentation?
- Which Tier-1 suppliers (spend ≥ €1M/year) lack a valid CSDDD human rights risk assessment as required by Directive 2024/1760 Art. 7?
- What is the total value of purchase orders pending approval beyond the standard SLA (24 hours for <€5,000; 48 hours for €5,000–€50,000; 72 hours for >€50,000)?
- Which commodity categories show the highest price variance between PO unit price and the contracted price in SAP condition records?
- What is the PO-to-invoice matching rate (2-way vs. 3-way match) by supplier and country, and where are the highest rates of invoice exceptions?
- Which open purchase orders are single-sourced for a critical item (ABC classification A) with lead time >60 days and no safety stock coverage?
- How has the early payment discount capture rate trended, and what is the annualized value of uncaptured discounts by payment term bucket?
- What is the average PO cycle time (requisition approval date to first goods receipt) by commodity category and buyer, and where are the process bottlenecks?

---

## 5. Data Sources

### Source 1: SAP S/4HANA — Purchase Order Header

- **Source Name**: SAP S/4HANA Purchase Order Header
- **Origin System**: SAP S/4HANA 2023 (on-premise)
- **Report/Table/Query**: Table EKKO (Purchasing Document Header); extracted via Apache Airflow SAP connector or SAP BW/4HANA ODP extraction
- **Data Owner**: Global Procurement Operations — Director of Procurement Systems
- **Update Frequency**: Daily batch at 01:00 UTC; near-real-time CDC available via SAP LT Replication Server (SLT) for P1 use cases
- **Required Fields**: EBELN (PO Number), BUKRS (Company Code), BSART (PO Type), LIFNR (Vendor Number), EKGRP (Purchasing Group), EKORG (Purchasing Organization), WAERS (Currency), BEDAT (PO Date), AEDAT (Last Change Date), FRGKE (Release Indicator), LOEKZ (Deletion Flag)
- **Critical Fields**: EBELN (unique identifier), FRGKE (approval status — must = 'R' for released), LOEKZ (soft delete flag — exclude 'L')
- **Primary/Logical Key**: EBELN (10-digit alphanumeric, unique per client)
- **Required Validations**: EBELN must be 10 characters; BUKRS must exist in company code master (T001); WAERS must be a valid ISO 4217 currency code; BEDAT must be ≥ 2023-01-01; LOEKZ ≠ 'L'
- **Possible Errors**: Duplicate EBELN records due to SLT replication lag; NULL LIFNR for plan-driven POs (handle by joining to EBAN for source of supply); currency conversion errors when WAERS ≠ EUR
- **Extraction Evidence**: Apache Airflow pipeline run log (Pipeline: SAP_EKKO_Daily_Extract); row count reconciliation report comparing SAP SE16N transaction count vs. PostgreSQL staging table count, signed off by SAP Basis team

### Source 2: SAP S/4HANA — Purchase Order Line Items

- **Source Name**: SAP S/4HANA Purchase Order Line Items
- **Origin System**: SAP S/4HANA 2023
- **Report/Table/Query**: Table EKPO (Purchasing Document Item)
- **Data Owner**: Global Procurement Operations
- **Update Frequency**: Daily batch at 01:00 UTC (same pipeline as EKKO)
- **Required Fields**: EBELN, EBELP (PO Item), MATNR (Material Number), TXZ01 (Short Text), MENGE (PO Quantity), MEINS (Unit of Measure), NETPR (Net Price), PEINH (Price Unit), NETWR (Net Value), MWSKZ (Tax Code), WERKS (Plant), LGORT (Storage Location), MATKL (Material Group), PSTYP (Item Category), KNTTP (Account Assignment Category), EINDT (Scheduled Delivery Date), WEPOS (Goods Receipt Indicator), REPOS (Invoice Receipt Indicator), LOEKZ (Deletion Flag at Item Level)
- **Critical Fields**: NETWR (Net Value in PO currency — used for spend aggregation), EINDT (delivery date — used for overdue calculation), WEPOS (must = 'X' for items requiring GR)
- **Primary/Logical Key**: EBELN + EBELP (composite key)
- **Required Validations**: NETWR ≥ 0 (no negative PO values in scope); MEINS must be a valid GS1 UOM code; EINDT must be ≥ PO creation date (EKKO.BEDAT); MENGE > 0 for standard items
- **Possible Errors**: MATNR = blank for text-based service POs (expected — use TXZ01 as description); EINDT = NULL for framework orders without schedule lines (join EKET for schedule lines); LOEKZ = 'L' at item level while header LOEKZ is blank (must filter at both levels)
- **Extraction Evidence**: Row count and NETWR sum reconciliation between SAP ME2M report output and PostgreSQL fact_po_line staging table, signed by Category Management lead

### Source 3: SAP S/4HANA — PO Schedule Lines and Confirmations

- **Source Name**: SAP S/4HANA PO Schedule Lines
- **Origin System**: SAP S/4HANA 2023
- **Report/Table/Query**: Table EKET (Scheduling Agreement Schedule Lines) and EKAB (PO Release Orders)
- **Data Owner**: Procurement Operations
- **Update Frequency**: Daily batch
- **Required Fields**: EBELN, EBELP, ETENR (Schedule Line Counter), EINDT (Delivery Date), MENGE (Scheduled Quantity), WEMNG (Quantity of Goods Received), REMNG (Remaining Quantity), GLMNG (Total Goods Received Quantity)
- **Critical Fields**: EINDT (committed delivery date), WEMNG (confirmed received quantity — for open quantity calculation)
- **Primary/Logical Key**: EBELN + EBELP + ETENR
- **Required Validations**: MENGE must equal sum of WEMNG + REMNG (tolerance ±0.001 for rounding); EINDT must be populated for all non-framework PO schedule lines
- **Possible Errors**: Multiple schedule lines per PO item (correct — aggregate by EBELN + EBELP); WEMNG may lag 24 hours vs. MKPF goods movement postings
- **Extraction Evidence**: Reconciliation of EKET REMNG totals vs. MB52 open stock report for a sample of 100 PO items

### Source 4: SAP S/4HANA — Goods Receipt (Material Documents)

- **Source Name**: SAP S/4HANA Material Documents (Goods Receipts)
- **Origin System**: SAP S/4HANA 2023
- **Report/Table/Query**: Tables MKPF (Material Document Header) and MSEG (Material Document Segment), filtered on BWART IN ('101','102') for GR against PO
- **Data Owner**: Warehouse / Receiving Operations
- **Update Frequency**: Real-time posting; daily batch extract
- **Required Fields**: MBLNR (Material Document), MJAHR (Year), ZEILE (Item), EBELN (Reference PO), EBELP (Reference PO Item), MATNR, WERKS, LGORT, MENGE (GR Quantity), MEINS, BUDAT (Posting Date), BLDAT (Document Date), BWART (Movement Type)
- **Critical Fields**: BUDAT (used for on-time delivery calculation: BUDAT vs. EKET.EINDT), BWART (101 = GR, 102 = GR Reversal — must handle reversals in net quantity calculation)
- **Primary/Logical Key**: MBLNR + MJAHR + ZEILE
- **Required Validations**: Every MBLNR + MJAHR + ZEILE must reference a valid EBELN + EBELP in EKPO; BUDAT must be ≤ system date; reversals (BWART=102) must subtract from net GR quantity
- **Possible Errors**: GR posted to wrong PO item (requires correction via MBST); delayed GR postings (warehouse posts GR 1-3 days after physical receipt — noted in OTD calculation methodology)
- **Extraction Evidence**: Reconciliation of total GR quantity in MSEG vs. MIGO display for top-20 PO items by volume

### Source 5: SAP Ariba — Sourcing and Supplier Data

- **Source Name**: SAP Ariba Network — Supplier Profile and Compliance Data
- **Origin System**: SAP Ariba (cloud, integrated with S/4HANA via Ariba Integration Toolkit)
- **Report/Table/Query**: Ariba Analytical Reporting API v2 — Reports: "Supplier Registration Status", "Compliance Questionnaire Responses", "Sourcing Event Summary"
- **Data Owner**: Supplier Lifecycle & Performance (SLP) team — Global Procurement
- **Update Frequency**: Daily API pull at 02:00 UTC
- **Required Fields**: SupplierId (Ariba ANID), SupplierName, RegistrationStatus, ComplianceStatus, QuestionnaireId, QuestionnaireResponse, LastUpdatedDate, RiskScore, CountryOfOrigin, CertificationList
- **Critical Fields**: ComplianceStatus (must = 'APPROVED' for active suppliers), UFLPA_Flag (custom field: boolean, populated from XUAR screening questionnaire), CSDDD_Assessment_Date (must be ≤ 3 years old per CSDDD Art. 10)
- **Primary/Logical Key**: SupplierId (Ariba ANID, 16-character alphanumeric)
- **Required Validations**: SupplierId must have a matching LIFNR in SAP S/4HANA vendor master (LFA1) via cross-reference table; ComplianceStatus cannot be NULL for active suppliers; CSDDD_Assessment_Date must be populated for all Tier-1 suppliers
- **Possible Errors**: Ariba API rate limit (429 errors — implement exponential backoff); supplier name mismatches between Ariba and S/4HANA (use SupplierId-LIFNR mapping table as authoritative join); questionnaire responses in multiple languages (normalize to English)
- **Extraction Evidence**: Ariba API call log in Apache Airflow with HTTP response codes; row count comparison between Ariba SLP portal supplier count and PostgreSQL staging table

### Source 6: UFLPA Entity List (US CBP)

- **Source Name**: UFLPA Entity List — US Customs and Border Protection
- **Origin System**: External — US CBP public dataset (https://www.cbp.gov/trade/forced-labor/UFLPA)
- **Report/Table/Query**: CSV download from CBP website; updated irregularly (typically monthly)
- **Data Owner**: Global Trade Compliance team
- **Update Frequency**: Manual check weekly; automated web scrape with Python (requests + BeautifulSoup) monitoring CBP page for file hash change
- **Required Fields**: EntityName, EntityType, CountryOfOperation, DateAdded, DateRevised, BasisForListing
- **Critical Fields**: EntityName (fuzzy-matched against SAP LFA1.NAME1 and Ariba SupplierName), DateAdded (for determining when risk was first identified)
- **Primary/Logical Key**: EntityName + DateAdded (no unique numeric ID in CBP dataset)
- **Required Validations**: File hash must change from prior download before reprocessing; EntityName must be normalized (remove legal suffixes: Ltd, Co., LLC, GmbH) before fuzzy matching; confidence threshold for match ≥ 85% (RapidFuzz library)
- **Possible Errors**: False positives in fuzzy matching (common company names); supplier name in SAP recorded in local script (Chinese characters) — requires transliteration; CBP list may include holding companies not directly in our supply base (require manual review)
- **Extraction Evidence**: Python script execution log with file hash comparison; list of matched EntityNames with confidence scores reviewed and signed off by Trade Compliance Manager

### Source 7: EUR/FX Exchange Rates (ECB)

- **Source Name**: European Central Bank — Daily Reference Exchange Rates
- **Origin System**: External — ECB Statistical Data Warehouse API (https://data-api.ecb.europa.eu)
- **Report/Table/Query**: ECB SDMX API: `/service/data/EXR/D.{currency}.EUR.SP00.A`
- **Data Owner**: Finance — Treasury Operations
- **Update Frequency**: Daily at 16:00 CET (ECB publication time)
- **Required Fields**: CURRENCY, DATE, EUR_RATE (units of currency per 1 EUR)
- **Critical Fields**: DATE (must match PO posting date for historical FX conversion), EUR_RATE (must not be NULL or 0)
- **Primary/Logical Key**: CURRENCY + DATE
- **Required Validations**: All 40 country currencies must be present for each business day; weekends/holidays use prior business day rate (Friday rate); EUR_RATE > 0; no rate older than 3 business days should be used as current rate
- **Possible Errors**: ECB API downtime (fallback to prior day rate with alert); exotic currencies for certain operating countries may not be available from ECB (use Bloomberg terminal extract via Finance)
- **Extraction Evidence**: Apache Airflow pipeline log; Finance sign-off that ECB rates match SAP TCURR table rates for the same date (reconciliation tolerance: ±0.01%)

---

## 6. Data Model

The Procurement Analytics data model follows a **star schema** hosted in PostgreSQL Database (with read replicas for Apache Superset live SQL query (SQLAlchemy connection)).

### Fact Tables

**fact_po_line** — Grain: one row per PO line item (EBELN + EBELP). Contains all measurable quantities and amounts: PO quantity, net value in PO currency, net value in EUR, open quantity, GR quantity, invoice quantity. Foreign keys to all dimension tables. Partitioned by fiscal year for query performance.

**fact_gr_receipt** — Grain: one row per goods receipt line (MBLNR + MJAHR + ZEILE). Contains GR quantity, GR date, reference PO/item, plant. Used for on-time delivery calculation and PO completion tracking. Linked to fact_po_line via EBELN + EBELP.

**fact_compliance_assessment** — Grain: one row per supplier per compliance framework per assessment period. Contains UFLPA screening result, CSDDD assessment date and status, REACH classification. Updated from Ariba SLP data. Foreign key to dim_supplier.

### Dimension Tables

**dim_supplier** — Grain: one row per supplier (LIFNR). Contains vendor name, country, Ariba ANID, Kraljic classification (STRATEGIC / LEVERAGE / BOTTLENECK / NON_CRITICAL), UFLPA flag, CSDDD tier designation, ISO 28000 certification status, payment terms.

**dim_material** — Grain: one row per material number (MATNR). Contains material description, material group (MATKL), ABC classification, XYZ classification, storage condition, REACH SVHC flag, lot tracking requirement, base unit of measure.

**dim_purchasing_org** — Grain: one row per purchasing organization (EKORG). Contains org name, lead buyer, region, associated company codes.

**dim_company_code** — Grain: one row per company code (BUKRS). Contains company name, country, ISO country code, local currency, fiscal year variant.

**dim_plant** — Grain: one row per plant (WERKS). Contains plant name, country, address, plant type (production / distribution / warehouse).

**dim_date** — Standard date dimension with fiscal year, fiscal period, calendar week, quarter, year, holiday flag, working day flag. Fiscal year variant aligned to SAP T009 configuration.

**dim_commodity** — Grain: one row per commodity category. Maps SAP MATKL (material group) codes to standardized UNSPSC commodity codes and internal category hierarchy (Level 1 → Level 2 → Level 3).

### Key Relationships

- fact_po_line → dim_supplier (LIFNR = dim_supplier.vendor_id)
- fact_po_line → dim_material (MATNR = dim_material.material_id)
- fact_po_line → dim_date on BEDAT (PO date), EINDT (delivery date), and AEDAT (change date — role-playing dimension)
- fact_po_line → dim_company_code (BUKRS)
- fact_po_line → dim_plant (WERKS)
- fact_po_line → dim_purchasing_org (EKORG)
- fact_gr_receipt → fact_po_line (EBELN + EBELP — many-to-one, multiple GR lines per PO item)
- fact_compliance_assessment → dim_supplier (vendor_id)
- dim_material → dim_commodity (material_group_code)

---

## 7. Data Dictionary

### Table: fact_po_line

- **Table Name**: fact_po_line
- **Description**: Central fact table containing one row per purchase order line item, capturing all procurement transactional measures
- **Granularity**: One row per SAP PO line (EBELN + EBELP)
- **Required Fields**:
  - po_number | VARCHAR(10) | SAP PO number (EKKO.EBELN)
  - po_item | VARCHAR(5) | PO line item number (EKPO.EBELP)
  - po_date | DATE | PO creation date (EKKO.BEDAT)
  - vendor_id | VARCHAR(10) | SAP vendor number (EKKO.LIFNR)
  - material_id | VARCHAR(18) | SAP material number (EKPO.MATNR)
  - plant_id | VARCHAR(4) | Plant (EKPO.WERKS)
  - company_code | VARCHAR(4) | Company code (EKKO.BUKRS)
  - purchasing_org | VARCHAR(4) | Purchasing organization (EKKO.EKORG)
  - commodity_code | VARCHAR(9) | Material group mapped to UNSPSC
  - po_quantity | DECIMAL(13,3) | PO ordered quantity (EKPO.MENGE)
  - uom | VARCHAR(3) | Unit of measure GS1 code (EKPO.MEINS)
  - net_price | DECIMAL(11,2) | Net price per price unit in PO currency (EKPO.NETPR)
  - price_unit | DECIMAL(5,0) | Price unit quantity (EKPO.PEINH)
  - net_value_loc | DECIMAL(15,2) | Net value in PO/local currency (EKPO.NETWR)
  - currency_code | VARCHAR(3) | PO currency ISO code (EKKO.WAERS)
  - net_value_eur | DECIMAL(15,2) | Net value converted to EUR using ECB rate on PO date
  - scheduled_delivery_date | DATE | Committed delivery date (EKET.EINDT, earliest open line)
  - gr_quantity | DECIMAL(13,3) | Total GR quantity posted (sum from MSEG BWART 101 minus 102)
  - open_quantity | DECIMAL(13,3) | po_quantity minus gr_quantity (floored at 0)
  - open_value_eur | DECIMAL(15,2) | open_quantity * net_price_eur
  - po_status | VARCHAR(20) | Derived: OPEN / PARTIALLY_DELIVERED / DELIVERED / CANCELLED
  - is_overdue | BIT | 1 if scheduled_delivery_date < GETDATE() AND open_quantity > 0
  - days_overdue | INT | DATEDIFF(day, scheduled_delivery_date, GETDATE()) when is_overdue=1, else 0
  - approval_status | VARCHAR(20) | Derived from EKKO.FRGKE: RELEASED / PENDING / BLOCKED
  - po_type | VARCHAR(4) | SAP document type (EKKO.BSART)
  - account_assignment | VARCHAR(1) | Account assignment category (EKPO.KNTTP)
  - deletion_flag | BIT | 1 if EKKO.LOEKZ='L' OR EKPO.LOEKZ='L'
  - load_date | DATETIME | ETL load timestamp (UTC)
  - source_system | VARCHAR(20) | 'SAP_S4H' constant
- **Primary Key**: po_number + po_item
- **Relationships**: FK to dim_supplier (vendor_id), dim_material (material_id), dim_plant (plant_id), dim_company_code (company_code), dim_purchasing_org (purchasing_org), dim_date (po_date, scheduled_delivery_date)
- **Required Transformations**: Convert NETWR from PO currency to EUR using dim_fx_rate; derive po_status from gr_quantity vs. po_quantity; calculate is_overdue and days_overdue at load time; map MATKL to UNSPSC via commodity mapping table
- **Cleaning Rules**: Exclude rows where deletion_flag = 1; exclude inter-company POs (BSART = 'UB'); exclude CapEx POs (KNTTP = 'A'); set gr_quantity = 0 when no MSEG records exist for the PO item; handle NULL MATNR (text-based service items) by setting material_id = 'NOMAT' and populating short_text field
- **Validations**: net_value_eur must not be NULL; open_quantity must be ≥ 0; po_date must be ≤ load_date; scheduled_delivery_date must be ≥ po_date
- **Use in Analysis**: Primary fact table for all spend analysis, PO follow-up, open order risk, overdue KPIs, price variance analysis, and buyer performance metrics

### Table: dim_supplier

- **Table Name**: dim_supplier
- **Description**: Supplier master dimension combining SAP vendor master (LFA1/LFB1) with Ariba SLP profile and compliance data
- **Granularity**: One row per active supplier (LIFNR)
- **Required Fields**:
  - vendor_id | VARCHAR(10) | SAP vendor number (LFA1.LIFNR)
  - ariba_anid | VARCHAR(16) | Ariba Network ID (from cross-reference table)
  - vendor_name | VARCHAR(100) | Vendor name (LFA1.NAME1)
  - vendor_name_2 | VARCHAR(100) | Additional name (LFA1.NAME2)
  - country_code | VARCHAR(3) | ISO 3166-1 alpha-3 country code (LFA1.LAND1 mapped)
  - country_name | VARCHAR(50) | Full country name
  - city | VARCHAR(35) | City (LFA1.ORT01)
  - postal_code | VARCHAR(10) | Postal code (LFA1.PSTLZ)
  - payment_terms | VARCHAR(4) | SAP payment terms (LFB1.ZTERM)
  - currency | VARCHAR(3) | Vendor currency (LFB1.WAERS)
  - kraljic_classification | VARCHAR(20) | STRATEGIC / LEVERAGE / BOTTLENECK / NON_CRITICAL
  - uflpa_flag | BIT | 1 = identified as potential XUAR operations risk
  - uflpa_screening_date | DATE | Date of last UFLPA screening
  - uflpa_clearance_doc | VARCHAR(200) | Reference to clearance document (URL or doc ID)
  - csddd_tier | VARCHAR(10) | TIER1 (≥€1M spend) / TIER2 / OUT_OF_SCOPE
  - csddd_assessment_date | DATE | Date of last CSDDD Art. 7 human rights assessment
  - csddd_status | VARCHAR(20) | COMPLIANT / NON_COMPLIANT / PENDING / NOT_ASSESSED
  - iso28000_certified | BIT | 1 = holds valid ISO 28000:2022 certification
  - iso28000_expiry | DATE | ISO 28000 certificate expiry date
  - is_active | BIT | 1 = active vendor (LFA1.SPRAS not blocked)
  - is_blocked | BIT | 1 = purchasing block (LFM1.SPERM = 'X')
  - load_date | DATETIME | ETL load timestamp
- **Primary Key**: vendor_id
- **Relationships**: Referenced by fact_po_line, fact_gr_receipt, fact_compliance_assessment
- **Required Transformations**: Join LFA1 + LFB1 + LFM1 in SAP; merge with Ariba SLP data on ANID cross-reference; apply UFLPA entity list fuzzy match (RapidFuzz ≥85% threshold); map LFA1.LAND1 (2-char SAP code) to ISO 3166-1 alpha-3
- **Cleaning Rules**: Exclude one-time vendors (LFA1.XCPDK = 'X'); normalize vendor name (strip leading/trailing spaces, convert to title case); deduplicate where same legal entity has multiple LIFNR (flag with parent_vendor_id)
- **Validations**: vendor_id must be unique; country_code must exist in ISO 3166-1; payment_terms must exist in SAP T052 table; if csddd_tier = 'TIER1' then csddd_assessment_date must not be NULL
- **Use in Analysis**: UFLPA compliance dashboard, CSDDD status tracking, spend by supplier country, supplier block monitoring, Kraljic portfolio view

### Table: fact_compliance_assessment

- **Table Name**: fact_compliance_assessment
- **Description**: Tracks the compliance status of each supplier against each regulatory framework (UFLPA, CSDDD, REACH, ISO 28000)
- **Granularity**: One row per supplier per compliance framework per assessment period
- **Required Fields**:
  - assessment_id | BIGINT IDENTITY | Surrogate key
  - vendor_id | VARCHAR(10) | SAP vendor number
  - framework | VARCHAR(20) | 'UFLPA' / 'CSDDD' / 'REACH' / 'ISO28000'
  - assessment_date | DATE | Date assessment was completed
  - assessment_result | VARCHAR(20) | COMPLIANT / NON_COMPLIANT / PENDING / WAIVED
  - risk_score | DECIMAL(5,2) | Numeric risk score 0–100 (higher = higher risk)
  - assessor_id | VARCHAR(50) | User ID of assessor (from Ariba or manual input)
  - document_ref | VARCHAR(500) | Reference to supporting document (the Git document repository URL or Ariba doc ID)
  - next_review_date | DATE | Scheduled next assessment date
  - notes | VARCHAR(2000) | Free-text notes from assessor
  - load_date | DATETIME | ETL timestamp
- **Primary Key**: assessment_id
- **Relationships**: FK to dim_supplier (vendor_id); FK to dim_date (assessment_date)
- **Required Transformations**: CSDDD next_review_date = assessment_date + 3 years (Art. 10 periodicity for Tier-1); UFLPA next_review_date = assessment_date + 1 year; auto-set assessment_result = 'PENDING' when next_review_date < GETDATE() and no newer assessment exists
- **Cleaning Rules**: One active record per vendor per framework (use assessment_date DESC to identify current); archive superseded assessments with is_current = 0 flag
- **Validations**: document_ref must not be NULL for COMPLIANT or NON_COMPLIANT results; assessment_date must not be in the future; risk_score must be in range [0, 100]
- **Use in Analysis**: CSDDD compliance dashboard, UFLPA risk heat map, audit evidence package for regulatory inspectors

---

## 8. Transformation Rules

1. **Currency Conversion**: Join fact_po_line to dim_fx_rate on currency_code and po_date. Compute net_value_eur = net_value_loc / EUR_RATE. For dates with no ECB rate (weekends, public holidays), use the most recent prior business day rate. Log any PO where conversion was performed with a non-current-day rate.

2. **PO Status Derivation**: After aggregating GR quantities from MSEG, apply: IF open_quantity = 0 THEN 'DELIVERED'; ELSE IF gr_quantity > 0 AND open_quantity > 0 THEN 'PARTIALLY_DELIVERED'; ELSE IF EKKO.LOEKZ = 'L' THEN 'CANCELLED'; ELSE 'OPEN'.

3. **Overdue Calculation**: Set is_overdue = 1 when scheduled_delivery_date < CAST(GETDATE() AS DATE) AND open_quantity > 0 AND po_status NOT IN ('DELIVERED', 'CANCELLED'). Calculate days_overdue = DATEDIFF(day, scheduled_delivery_date, GETDATE()). Set days_overdue = 0 for non-overdue lines.

4. **Delivery Date Resolution**: When multiple EKET schedule lines exist per EBELP, select the earliest EINDT with REMNG > 0 (earliest outstanding delivery commitment). If no EKET records exist, use EKPO.EINDT as fallback.

5. **UNSPSC Commodity Mapping**: Apply lookup table (matkl_to_unspsc) joining on EKPO.MATKL to assign UNSPSC Level-3 code. Where no mapping exists, assign UNSPSC = '00000000' and flag for manual classification. Mapping coverage must be ≥ 95% of PO value.

6. **Vendor Name Normalization**: Apply Python pipeline step: strip() to remove whitespace; title case conversion; remove legal suffixes (GmbH, S.A., Ltd, Co., Inc., BV, SAS, AG) for UFLPA fuzzy matching only (retain original name in display field).

7. **UFLPA Fuzzy Match**: Python script using RapidFuzz token_sort_ratio between normalized vendor names and normalized CBP entity list names. Matches ≥ 85% score → set uflpa_flag = 1 and record match details in uflpa_match log table. Matches 70–84% → set uflpa_flag = 0 with manual_review_required = 1. Matches < 70% → no flag.

8. **Approval Status Mapping**: Map EKKO.FRGKE values: blank = 'RELEASED' (no approval needed, below threshold); '1' = 'PENDING' (partial approval); '2' = 'PENDING' (full release pending); 'R' = 'RELEASED'; 'B' = 'BLOCKED'. Derive approval_sla_breached = 1 when approval_status = 'PENDING' AND DATEDIFF(hour, po_date, GETDATE()) > SLA_hours (SLA_hours = 24 for <€5K; 48 for €5K–€50K; 72 for >€50K).

9. **Spend Aggregation**: For spend analysis, aggregate fact_po_line by (vendor_id, commodity_code, company_code, fiscal_year, fiscal_period). Sum net_value_eur where po_status NOT IN ('CANCELLED') and deletion_flag = 0. Compute running totals using window functions for trend analysis.

10. **Maverick Spend Flag**: Join Accounts Payable invoice table (RBKP/RSEG) to fact_po_line on EBELN. Invoices with no matching EBELN (no PO reference) are classified as maverick spend. Compute maverick_spend_eur = SUM(invoice_amount_eur) for unmatched invoices by cost center and GL account.

11. **PO-to-Invoice Match Rate**: For each PO line with WEPOS = 'X' (GR-based), compute 3-way match rate = (count of invoices matched on PO + GR) / (total invoices for PO). For POs with WEPOS = blank (PO-based matching only), compute 2-way match rate. Report separately.

12. **Price Variance Calculation**: Join EKPO.NETPR to SAP condition records (KONP table, condition type PB00 or PBXX) for the same material, vendor, plant, and validity date range. Compute price_variance_pct = (EKPO.NETPR - KONP.KBETR) / KONP.KBETR * 100. Flag items where ABS(price_variance_pct) > 5% for buyer review.

13. **Spend Under Management Calculation**: Classify each spend transaction as 'MANAGED' (has valid PO reference in approved system) or 'UNMANAGED' (no PO or PO created after invoice). Compute SUM_rate = SUM(net_value_eur WHERE managed='MANAGED') / SUM(net_value_eur) * 100 by company code and fiscal period.

14. **ABC Classification at PO Level**: For inventory items (account assignment category blank or K), join to inventory master ABC classification (dim_material.abc_class). Propagate ABC class to PO line. For service/CapEx items without material number, assign ABC = 'C' as default.

15. **Historical Load Deduplication**: During initial 3-year historical load, deduplicate MSEG records where the same MBLNR + MJAHR + ZEILE appears multiple times due to SLT replication (keep latest CPUDT + CPUTM). Apply SHA-256 hash of key fields to detect true duplicates vs. legitimate reversals.

---

## 9. Business Rules

### Rule 1: PO Approval Threshold

- **Rule Name**: PO_APPROVAL_THRESHOLD
- **Description**: Purchase orders above defined thresholds require manager approval before release to supplier
- **Logic Condition**: IF net_value_eur < 5,000 → no approval required (auto-release); IF 5,000 ≤ net_value_eur < 50,000 → Category Manager approval required; IF net_value_eur ≥ 50,000 → Director of Procurement approval required; IF net_value_eur ≥ 500,000 → CPO approval required
- **Expected Result**: POs above threshold show approval_status = 'PENDING' until approved; released POs show 'RELEASED'; SLA breach alert fired when approval not completed within SLA window
- **Example**: PO 4500012345 for €75,000 for metal components requires Director approval within 48 hours of PO creation
- **Exception**: Emergency POs (PO type 'FO' — Framework Call-off) are pre-approved under the framework agreement; BSART = 'FO' bypasses individual approval workflow
- **Required Evidence**: SAP release strategy configuration screenshot (transaction OME9); approval log from SAP workflow (SWWL); Apache Airflow flow run history showing escalation alert sent after SLA breach

### Rule 2: UFLPA Mandatory Clearance

- **Rule Name**: UFLPA_CLEARANCE_REQUIRED
- **Description**: Any active supplier with uflpa_flag = 1 must provide CBP-accepted clearance documentation before new POs can be released
- **Logic Condition**: IF dim_supplier.uflpa_flag = 1 AND dim_supplier.uflpa_clearance_doc IS NULL THEN block PO release AND generate compliance alert
- **Expected Result**: POs referencing UFLPA-flagged suppliers without clearance docs are blocked; alert sent to Trade Compliance team and Category Manager
- **Example**: Supplier "Xinjiang Textile Co." (LIFNR: 1000567) matched CBP entity list with 92% confidence; all open POs totaling €2.3M flagged; buyer notified within 24 hours
- **Exception**: Suppliers with CBP-issued "rebuttal of presumption" letter on file (clearance_doc_type = 'CBP_REBUTTAL') are exempt from blocking; must be renewed annually
- **Required Evidence**: UFLPA entity list match log with confidence scores; Ariba compliance questionnaire response showing clearance document upload; Trade Compliance Manager sign-off email

### Rule 3: CSDDD Assessment Currency

- **Rule Name**: CSDDD_ASSESSMENT_CURRENCY
- **Description**: CSDDD Tier-1 suppliers (≥€1M annual spend per legal entity) must have a human rights and environmental risk assessment not older than 3 years
- **Logic Condition**: IF csddd_tier = 'TIER1' AND (csddd_assessment_date IS NULL OR DATEDIFF(year, csddd_assessment_date, GETDATE()) ≥ 3) THEN csddd_status = 'NON_COMPLIANT' AND generate escalation alert
- **Expected Result**: Non-compliant Tier-1 suppliers shown in red on CSDDD dashboard; automated email sent to SLP team with supplier name, last assessment date, and days until compliance breach
- **Example**: Supplier with LIFNR 1001234, annual spend €4.2M, last assessment 2022-03-15 → assessment is 4+ years old → NON_COMPLIANT → alert to SLP team
- **Exception**: New suppliers onboarded within the past 6 months have a 180-day grace period before assessment is mandatory (CSDDD_GRACE_PERIOD flag in dim_supplier)
- **Required Evidence**: Ariba SLP assessment record with date and assessor; document retention log confirming 5-year storage per CSDDD Art. 23; SLP team confirmation email

### Rule 4: Single-Source Critical Item Risk

- **Rule Name**: SINGLE_SOURCE_CRITICAL_RISK
- **Description**: Open PO lines for ABC-A classified items from a single active supplier with lead time > 60 days and no safety stock coverage are classified as HIGH supply risk
- **Logic Condition**: IF dim_material.abc_class = 'A' AND COUNT(DISTINCT vendor_id) per material = 1 AND avg_lead_time_days > 60 AND safety_stock_qty = 0 AND open_quantity > 0 THEN risk_level = 'HIGH'
- **Expected Result**: HIGH-risk PO lines appear on Open Orders Risk dashboard with red flag; alert to Category Manager and Supply Planning
- **Example**: Material 1000567 (A-class electronic component), sole supplier LIFNR 2001234, lead time 90 days, safety stock = 0, open PO quantity 5,000 units due in 45 days
- **Exception**: Items with confirmed production allocation from supplier (po_confirmation_status = 'CONFIRMED') downgrade from HIGH to MEDIUM risk
- **Required Evidence**: ABC classification report from inventory module; lead time data from MARC table (WEBAZ field); safety stock from MRP data (MINBE in MARC)

### Rule 5: Soft Delete on PO Lines

- **Rule Name**: PO_SOFT_DELETE_ONLY
- **Description**: Purchase order lines must never be physically deleted from the analytics data warehouse; cancellation must be reflected via deletion_flag = 1 and po_status = 'CANCELLED'
- **Logic Condition**: When EKPO.LOEKZ = 'L' is detected in delta load, set deletion_flag = 1 and po_status = 'CANCELLED' on the existing fact_po_line record; do NOT delete the row from PostgreSQL
- **Expected Result**: Cancelled POs remain in fact_po_line with deletion_flag = 1; excluded from active spend and open order calculations; retained for audit trail and spend history
- **Exception**: Test POs created in SAP QAS (quality assurance system) system — these are excluded entirely during initial load by filtering on system ID; they are never loaded into production PostgreSQL
- **Required Evidence**: Row count comparison before and after delta load showing existing PO rows updated (not deleted); PostgreSQL audit log confirming no DELETE statements executed on fact_po_line

### Rule 6: 3-Way Match Mandatory for GR-Based POs

- **Rule Name**: THREE_WAY_MATCH_GR_POS
- **Description**: All PO lines with WEPOS = 'X' (goods receipt indicator active) must complete 3-way match (PO → GR → Invoice) before invoice is released for payment
- **Logic Condition**: Invoice for WEPOS='X' PO items flagged as MATCH_EXCEPTION if invoice_quantity > gr_quantity OR invoice_unit_price > po_unit_price * 1.05 (5% tolerance)
- **Expected Result**: Matched invoices proceed to payment; exceptions routed to buyer for review and approval within 5 business days
- **Example**: Invoice for PO 4500099001, item 10, for 100 units at €50 each; GR posted for only 80 units → exception flagged; buyer contacts supplier to hold invoice pending remaining GR
- **Exception**: Service POs (PSTYP = 'D') use 2-way match (PO → Invoice); no GR required
- **Required Evidence**: SAP MRBR report (blocked invoice list) vs. Apache Superset match exception count; Finance AP team sign-off on reconciliation

---

## 10. KPIs and Formulas

### KPI 1: Purchase Order On-Time Delivery Rate (PO OTD)

- **KPI Name**: PO On-Time Delivery Rate
- **Objective**: Measure the percentage of PO lines where goods receipt date ≤ committed delivery date, indicating supplier delivery reliability at the purchase order level
- **Formula**:
  ```sql
  SELECT
    COUNT(*) FILTER (WHERE is_overdue = 0 AND po_status = 'DELIVERED')
    / NULLIF(COUNT(*) FILTER (WHERE po_status = 'DELIVERED'), 0) AS po_otd_rate
  FROM fact_po_line;
  ```
  SQL equivalent: `COUNT(CASE WHEN gr_date <= scheduled_delivery_date THEN 1 END) / COUNT(*) WHERE po_status = 'DELIVERED'`
- **Data Source**: fact_po_line joined to fact_gr_receipt (first GR posting date per PO item)
- **Calculation Level**: Supplier, commodity, plant, company code, fiscal period
- **Frequency**: Daily refresh; reported weekly to Category Management, monthly to CPO
- **Owner**: Procurement Operations Manager
- **Interpretation**: Measures delivery punctuality against committed dates; excludes open and cancelled POs; counts first GR date vs. earliest scheduled delivery date
- **Thresholds**: Green ≥ 95% | Yellow 90–94% | Red < 90%
- **Traffic Light**: Green = world-class; Yellow = improvement required; Red = escalation to Supplier Performance team
- **Recommended Action**: Red suppliers: initiate formal supplier performance improvement plan (PIP) within 10 business days; root cause analysis (carrier delay vs. production delay vs. incorrect EINDT in SAP)
- **Validation vs Source**: Cross-validate monthly PO OTD from Apache Superset against ME2M report exported from SAP; tolerance ±0.5 percentage points

### KPI 2: Spend Under Management (SUM) Rate

- **KPI Name**: Spend Under Management Rate
- **Objective**: Quantify the percentage of total addressable spend routed through approved procurement channels (PO-based or catalogue), indicating procurement compliance and control effectiveness
- **Formula**:
  ```sql
  SELECT
    SUM(net_value_eur) FILTER (WHERE spend_channel = 'MANAGED')
    / NULLIF(SUM(net_value_eur) + (SELECT Maverick_Spend_EUR), 0) AS sum_rate
  FROM fact_po_line;
  ```
  Where Maverick_Spend_EUR = sum of invoice amounts with no PO reference, sourced from AP invoice table
- **Data Source**: fact_po_line (managed spend) + fact_ap_invoice (total AP spend including maverick)
- **Calculation Level**: Company code, cost center, GL account, fiscal period
- **Frequency**: Monthly; trend reported quarterly to CFO
- **Owner**: CPO / Head of Procurement Governance
- **Interpretation**: SUM rate of 90% means 90 cents of every €1 spent is controlled through procurement channels; the remaining 10% is maverick or uncontrolled
- **Thresholds**: Green ≥ 90% | Yellow 80–89% | Red < 80%
- **Traffic Light**: Target is ≥ 90%; below 80% indicates systemic procurement bypass that requires process controls or system enforcement (SAP SRM mandatory PO requirement)
- **Recommended Action**: For Red cost centers: enforce mandatory PO policy via SAP FI blocking of non-PO invoices; review with Finance Controller; training for cost center owners
- **Validation vs Source**: Total managed spend in Apache Superset must reconcile to SAP ME2N total PO value within ±1%; maverick spend must reconcile to SAP MRBR non-PO invoices

### KPI 3: Open Order Overdue Value

- **KPI Name**: Open Order Overdue Value (EUR)
- **Objective**: Quantify the total EUR value of purchase orders that are past their committed delivery date and have not been fully received, representing immediate supply chain risk
- **Formula**:
  ```sql
  SELECT SUM(open_value_eur) AS overdue_open_value_eur
  FROM fact_po_line
  WHERE is_overdue = 1
    AND po_status IN ('OPEN', 'PARTIALLY_DELIVERED')
    AND deletion_flag = 0;
  ```
- **Data Source**: fact_po_line
- **Calculation Level**: Supplier, commodity, plant, buyer, company code
- **Frequency**: Daily; alert triggered when total overdue value > €500,000 for a single commodity or supplier
- **Owner**: Procurement Operations / Category Managers
- **Interpretation**: Every euro in this KPI represents committed spend with no delivery; high values indicate supply risk, potential production stoppages, or unreliable suppliers
- **Thresholds**: Green < €1M total | Yellow €1M–€5M | Red > €5M (thresholds adjustable by category)
- **Traffic Light**: Red threshold triggers automatic escalation to Supply Chain Risk committee
- **Recommended Action**: Contact top-5 overdue suppliers within 24 hours; evaluate expediting options (air freight); activate alternative suppliers if lead time for recovery > 30 days
- **Validation vs Source**: Sum of open_value_eur in Apache Superset must reconcile to ME2M report "PO Value Not Yet Delivered" field in SAP ±€10,000

### KPI 4: UFLPA Compliance Coverage Rate

- **KPI Name**: UFLPA Compliance Coverage Rate
- **Objective**: Ensure 100% screening of active suppliers against the UFLPA entity list and track clearance documentation completion for flagged suppliers
- **Formula**:
  ```sql
  -- UFLPA_Coverage_Rate
  SELECT
    COUNT(*) FILTER (WHERE is_active = 1 AND uflpa_screening_date >= DATE_TRUNC('year', CURRENT_DATE))
    / NULLIF(COUNT(*) FILTER (WHERE is_active = 1), 0) AS uflpa_coverage_rate
  FROM dim_supplier;

  -- UFLPA_Clearance_Rate
  SELECT
    COUNT(*) FILTER (WHERE uflpa_flag = 1 AND uflpa_clearance_doc IS NOT NULL)
    / NULLIF(COUNT(*) FILTER (WHERE uflpa_flag = 1), 0) AS uflpa_clearance_rate
  FROM dim_supplier;
  ```
- **Data Source**: dim_supplier, fact_compliance_assessment
- **Calculation Level**: Supplier, country, commodity category
- **Frequency**: Weekly screening refresh; monthly reporting to General Counsel and CPO
- **Owner**: Global Trade Compliance Manager
- **Interpretation**: Coverage must be 100%; clearance rate for flagged suppliers must reach 100% before any new POs are issued; gaps represent legal and reputational exposure
- **Thresholds**: Coverage: Green = 100% | Yellow 95–99% | Red < 95%. Clearance (for flagged): Green = 100% | Yellow 80–99% | Red < 80%
- **Traffic Light**: Any Red on either metric triggers legal escalation
- **Recommended Action**: Uncovered suppliers: run immediate screening; flagged without clearance: suspend new PO issuance within 5 business days pending clearance document receipt
- **Validation vs Source**: Supplier count in Apache Superset vs. SAP LFA1 active vendor count (SPERR ≠ 'X') within ±5 records; UFLPA flag count vs. Trade Compliance manual list

### KPI 5: PO Approval SLA Compliance Rate

- **KPI Name**: PO Approval SLA Compliance Rate
- **Objective**: Measure the percentage of purchase orders that received required approvals within the defined SLA window, indicating procurement process efficiency and internal control health
- **Formula**:
  ```sql
  SELECT
    COUNT(*) FILTER (WHERE approval_sla_breached = 0 AND requires_approval = 1)
    / NULLIF(COUNT(*) FILTER (WHERE requires_approval = 1), 0) AS approval_sla_rate
  FROM fact_po_line;
  ```
- **Data Source**: fact_po_line (requires_approval, approval_sla_breached flags derived from EKKO.FRGKE and approval workflow timestamps)
- **Calculation Level**: Purchasing group, approver, company code, PO value bucket
- **Frequency**: Daily
- **Owner**: Head of Procurement Operations
- **Interpretation**: SLA breaches delay supplier confirmation, increase overdue risk, and indicate approver bottlenecks (holiday coverage gaps, understaffing)
- **Thresholds**: Green ≥ 95% | Yellow 85–94% | Red < 85%
- **Traffic Light**: Red triggers review of approval delegation rules in SAP
- **Recommended Action**: Top breaching approvers receive weekly SLA report; sustained Red → review delegation authority settings and add backup approvers
- **Validation vs Source**: SAP workflow transaction SWI1 approval log vs. Apache Superset approval timestamps; reconcile breach count ±2%

### KPI 6: CSDDD Tier-1 Assessment Coverage

- **KPI Name**: CSDDD Tier-1 Supplier Assessment Coverage
- **Objective**: Track the percentage of Tier-1 suppliers (annual spend ≥€1M) with a valid, current (≤3 years old) CSDDD Art. 7 human rights and environmental risk assessment
- **Formula**:
  ```dax
  CSDDD_Coverage =
  DIVIDE(
    COUNTROWS(FILTER(dim_supplier,
      dim_supplier[csddd_tier] = "TIER1" &&
      dim_supplier[csddd_status] = "COMPLIANT" &&
      DATEDIFF(dim_supplier[csddd_assessment_date], TODAY(), YEAR) < 3
    )),
    COUNTROWS(FILTER(dim_supplier, dim_supplier[csddd_tier] = "TIER1")),
    0
  )
  ```
- **Data Source**: dim_supplier, fact_compliance_assessment
- **Calculation Level**: Company, region, commodity category
- **Frequency**: Monthly; annual regulatory reporting
- **Owner**: Head of Sustainability & Compliance / CPO
- **Interpretation**: EU CSDDD enforcement begins 2027; companies must demonstrate systematic assessment of all Tier-1 suppliers; gap now = compliance risk at enforcement date
- **Thresholds**: Green ≥ 90% | Yellow 70–89% | Red < 70% (2026 target); Green = 100% (2027 mandatory)
- **Traffic Light**: Red = material regulatory risk; requires immediate program acceleration
- **Recommended Action**: Prioritize assessments by spend value; use Ariba SLP assessment questionnaire; engage third-party ESG assessment provider for complex suppliers
- **Validation vs Source**: Ariba SLP portal Tier-1 supplier count vs. Apache Superset CSDDD dashboard supplier count; reconcile monthly

---

## 11. Analytical Logic

### PO Risk Scoring

Each open PO line receives a composite Risk Score (0–100) computed as:

```
risk_score = (w1 * overdue_score) + (w2 * value_score) + (w3 * source_risk_score) + (w4 * compliance_score)

where:
  w1 = 0.35 (overdue weight)
  w2 = 0.25 (value weight)
  w3 = 0.25 (single-source weight)
  w4 = 0.15 (compliance weight)

overdue_score:
  0 days overdue = 0
  1-7 days = 25
  8-30 days = 50
  31-60 days = 75
  >60 days = 100

value_score:
  < €10K = 10
  €10K–€100K = 30
  €100K–€500K = 60
  €500K–€2M = 80
  > €2M = 100

source_risk_score:
  Multiple approved sources = 0
  Single approved source, alt identified = 40
  Single approved source, no alt = 80
  Unapproved source = 100

compliance_score:
  UFLPA clearance complete, CSDDD compliant = 0
  Minor compliance gap = 30
  UFLPA flag active without clearance = 80
  Multiple compliance failures = 100
```

POs with risk_score ≥ 70 are classified HIGH; 40–69 MEDIUM; < 40 LOW.

### Spend Segmentation

Apply Pareto analysis to spend data:
- **Tier A** (top 20% of suppliers by spend = ~80% of value): Strategic focus, CSDDD Tier-1, quarterly reviews
- **Tier B** (next 30% of suppliers = ~15% of value): Leverage category, semi-annual reviews
- **Tier C** (remaining 50% of suppliers = ~5% of value): Transactional, automated management

Apply commodity-level spend clustering using Python K-means (k=5) on dimensions: annual spend EUR, number of suppliers, price volatility index, criticality score. Output feeds Kraljic matrix positioning.

### Alert Priority Logic

Apache Airflow alerts are tiered:
- **P1 — Immediate** (within 2 hours): UFLPA-flagged supplier with new PO > €50K; PO approval SLA breach > 72 hours; overdue critical-item PO (ABC-A) > 30 days
- **P2 — Same Day**: New overdue PO line (days_overdue = 1); CSDDD assessment expiring within 60 days; price variance > 10% on PO vs. contract
- **P3 — Weekly Digest**: Spend Under Management rate below Yellow threshold; approval SLA trending Yellow; supplier with decreasing delivery score for 3 consecutive months

---

## 12. Validations and Controls

### Validation 1: PO Line Row Count Reconciliation

- **Validation Name**: EKPO_ROW_COUNT_RECONCILIATION
- **Field or Table Validated**: fact_po_line row count vs. SAP EKPO
- **Validation Rule**: COUNT(*) in fact_po_line (excluding test POs and cancelled lines) must equal COUNT(*) in SAP EKPO for the same date range and filter criteria ±0.1%
- **Validation Method**: Automated Python script in Apache Airflow post-load activity; pulls EKPO count via SAP RFC function module; compares to PostgreSQL count; logs result to audit table
- **Expected Result**: Variance ≤ 0.1% of total row count; zero variance for current fiscal year
- **Action if Fails**: Stop downstream Apache Superset refresh; alert data engineering team; hold report publication until reconciled; investigate missing or duplicate records
- **Verifiable Evidence**: Apache Airflow pipeline run log showing row count comparison; audit_reconciliation table in PostgreSQL with timestamp, source count, target count, variance

### Validation 2: Spend Value Reconciliation

- **Validation Name**: SPEND_EUR_RECONCILIATION
- **Field or Table Validated**: fact_po_line.net_value_eur SUM vs. SAP ME2N report
- **Validation Rule**: Total SUM(net_value_eur) in Apache Superset for any given fiscal period must match SAP ME2N "Net Order Value" (converted to EUR) ±1%
- **Validation Method**: Monthly manual reconciliation by Procurement Controller; SAP ME2N exported to CSV; compared to Apache Superset KPI card value
- **Expected Result**: Variance ≤ 1% for any fiscal period
- **Action if Fails**: Investigate FX rate discrepancies (most common cause); recheck LOEKZ filter; rerun currency conversion with corrected ECB rates
- **Verifiable Evidence**: Signed reconciliation worksheet (CSV) stored in the Git document repository: Procurement Analytics / Monthly Reconciliation / [YYYY-MM]

### Validation 3: Supplier Count Completeness

- **Validation Name**: SUPPLIER_MASTER_COMPLETENESS
- **Field or Table Validated**: dim_supplier row count vs. SAP LFA1
- **Validation Rule**: All active vendors in SAP LFA1 with at least one PO in the past 24 months and SPERR ≠ 'X' must appear in dim_supplier
- **Validation Method**: Automated script comparing SAP LFA1 active vendor count to dim_supplier is_active=1 count; tolerance ±10 records (accounts for new vendors created same day as extract)
- **Expected Result**: 100% of active vendors with recent PO activity present in dim_supplier
- **Action if Fails**: Identify missing LIFNR values; check ETL join logic on LFA1/LFB1; rerun vendor master extract
- **Verifiable Evidence**: vendor_completeness_check table in PostgreSQL showing missing LIFNRs; data engineer sign-off

### Validation 4: FX Rate Coverage

- **Validation Name**: FX_RATE_DAILY_COVERAGE
- **Field or Table Validated**: dim_fx_rate completeness for all 40 country currencies
- **Validation Rule**: For every business day in the reporting period, dim_fx_rate must contain a rate for all 40 currencies used by active company codes; no NULL EUR_RATE values
- **Validation Method**: Automated check in Apache Airflow: for each business day, count distinct CURRENCY values in dim_fx_rate; alert if count < 40 for any business day
- **Expected Result**: 40 currencies present for every business day; weekend/holiday rates copied from prior business day
- **Action if Fails**: Trigger fallback ECB API retry; if ECB rate unavailable after 3 retries, use Bloomberg rate from Finance Treasury (manual upload to PostgreSQL); block currency conversion until resolved
- **Verifiable Evidence**: dim_fx_rate audit log; Apache Airflow pipeline monitoring dashboard screenshot

### Validation 5: UFLPA Screening Completeness

- **Validation Name**: UFLPA_SCREENING_100PCT
- **Field or Table Validated**: dim_supplier.uflpa_screening_date
- **Validation Rule**: All active suppliers (is_active=1) must have uflpa_screening_date within the current calendar year; any supplier with NULL or outdated screening date triggers alert
- **Validation Method**: Weekly automated SQL query: SELECT COUNT(*) FROM dim_supplier WHERE is_active=1 AND (uflpa_screening_date IS NULL OR uflpa_screening_date < DATEADD(year,-1,GETDATE())); count must = 0
- **Expected Result**: Zero suppliers with missing or outdated UFLPA screening
- **Action if Fails**: Run immediate screening for unscreened suppliers via Python UFLPA script; notify Trade Compliance Manager; suspend new PO issuance to unscreened suppliers until complete
- **Verifiable Evidence**: uflpa_screening_log table; Trade Compliance Manager sign-off email

---

## 13. Required Evidence

The following evidence items must be collected, reviewed, and signed off before the analytics solution is considered production-ready:

1. **Row Count Reconciliation Report**: Signed comparison of SAP EKPO row count vs. fact_po_line row count for a full fiscal year, signed by Procurement Data Engineer and Procurement Controller
2. **Spend Value Reconciliation Report**: Month-by-month comparison of SAP ME2N totals vs. Apache Superset spend KPIs for the past 12 months, signed by Finance Controller
3. **UFLPA Screening Log**: Complete audit trail of CBP entity list fuzzy match runs, including all match confidence scores ≥70%, signed by Global Trade Compliance Manager
4. **CSDDD Tier-1 Supplier List**: Approved list of CSDDD Tier-1 suppliers (≥€1M annual spend) with current assessment status, signed by Head of Sustainability
5. **FX Rate Source Confirmation**: Written confirmation from Finance Treasury that ECB rates used in Apache Superset match SAP TCURR table rates, with monthly reconciliation tolerance documented
6. **Apache Superset UAT Sign-off**: User Acceptance Testing sign-off from at least 3 Category Managers and 1 Procurement Director, confirming KPI values match their manual calculations
7. **Data Governance Approval**: Data Classification and Ownership sign-off confirming PostgreSQL database contains no PII beyond business contact names, compliant with GDPR Art. 6 and company data policy
8. **SAP Authorization Concept**: Documentation confirming Apache Airflow service account has minimum required SAP authorizations (read-only on EKKO, EKPO, EKET, MSEG, LFA1, LFB1) without access to HR or FI documents
9. **Apache Airflow Alert Testing Evidence**: Screenshots of test alert runs for each P1/P2 alert scenario, confirming correct recipients and message content
10. **Dashboard Screenshots**: Production Apache Superset screenshots with real data (data masked for external sharing) showing all 5 report pages functioning correctly

---

## 14. Dashboard / Report Design

### Apache Superset Solution Structure

The Procurement Analytics Apache Superset solution consists of 5 report pages accessed via a shared workspace with Row-Level Security (RLS) enforced by purchasing organization and company code.

### Page 1: Executive Procurement Overview

**Purpose**: CPO and senior leadership summary — one-page view of procurement health  
**Visuals**:
- KPI Cards (top row): Total PO Value (EUR), Spend Under Management %, PO OTD Rate, Open Overdue Value, CSDDD Coverage Rate
- Line Chart: Monthly spend trend (rolling 24 months) vs. budget line
- Donut Chart: Spend by commodity category (top 10 + other)
- Bar Chart: Top 10 suppliers by PO value with OTD indicator (green/yellow/red dot)
- Gauge: SUM rate vs. 90% target
- Map Visual (Superset map): Spend bubble map by supplier country with UFLPA country heat overlay

**Filters/Slicers**: Fiscal Year, Fiscal Period, Company Code (multi-select), Commodity Category  
**Drill-down**: Click supplier bar → drill to Supplier Detail page; click overdue value → drill to PO Follow-up page  
**Refresh**: Daily at 06:00 UTC; refresh timestamp displayed on page

### Page 2: PO Follow-up and Open Orders

**Purpose**: Operational daily management tool for buyers and procurement operations  
**Visuals**:
- Table: Open PO lines with columns (PO Number, Supplier, Material, Commodity, Plant, PO Quantity, Open Quantity, Open Value EUR, Scheduled Delivery Date, Days Overdue, Risk Score, Risk Level). Conditional formatting: Red rows for HIGH risk, Yellow for MEDIUM.
- Bar Chart: Overdue PO value by supplier (top 15)
- Bar Chart: Overdue PO count by days overdue bucket (1-7, 8-30, 31-60, >60)
- KPI Cards: Total Open Value, Total Overdue Value, % Overdue, Avg Days Overdue
- Scatter Plot: Supplier OTD rate (x-axis) vs. Open PO Value (y-axis) — bubble size = PO count; color = risk level

**Filters/Slicers**: Risk Level, Days Overdue Range, Buyer/Purchasing Group, Commodity, Plant, Company Code  
**Drill-down**: Click PO number → tooltip showing full PO details, last GR date, supplier contact  
**Export**: CSV export button for buyer action lists

### Page 3: Spend Analysis

**Purpose**: Category management spend intelligence and maverick spend monitoring  
**Visuals**:
- Treemap: Spend by Commodity L1 → L2 → L3 hierarchy (drill-down enabled)
- Stacked Bar: Managed vs. Maverick spend by cost center (top 20 cost centers)
- Line Chart: Price variance trend by commodity (monthly average price variance %)
- Table: Top 50 suppliers by spend with year-over-year comparison
- Waterfall Chart: Spend change analysis (volume effect vs. price effect vs. mix effect)
- Bar Chart: New supplier spend vs. incumbent supplier spend (sourcing effectiveness)

**Filters/Slicers**: Fiscal Year (current + prior 2), Commodity, Company Code, Country, Supplier Tier  
**Drill-down**: Click commodity → supplier list; click supplier → PO line details

### Page 4: Supplier Compliance Dashboard

**Purpose**: UFLPA and CSDDD compliance monitoring for Trade Compliance and Legal teams  
**Visuals**:
- Status Matrix: Grid of active suppliers (rows) vs. compliance frameworks (columns: UFLPA, CSDDD, ISO28000, REACH); color-coded cells (Green/Yellow/Red)
- KPI Cards: UFLPA Coverage %, UFLPA Flagged Count, CSDDD Tier-1 Coverage %, Days Until CSDDD Enforcement (2027 countdown)
- Bar Chart: CSDDD assessment status by commodity category (Compliant / Non-Compliant / Pending / Not Assessed)
- Timeline: Upcoming CSDDD assessment renewal dates (next 90 days)
- Map: UFLPA-flagged supplier locations (country of manufacturing)
- Table: UFLPA-flagged suppliers with open PO value, clearance document status, days since flagged

**Filters/Slicers**: Framework (UFLPA / CSDDD / ISO28000), Compliance Status, Country, Commodity, Tier  
**Alerts**: Red banner displayed on page when any Tier-1 supplier is NON_COMPLIANT

### Page 5: PO Approval and Process Health

**Purpose**: Internal controls monitoring for Procurement Governance and Internal Audit  
**Visuals**:
- KPI Cards: Approval SLA Compliance Rate, Avg Approval Cycle Time (hours), POs Pending > SLA, 3-Way Match Rate
- Bar Chart: SLA breach count by approver (anonymized for general users; full names for audit users with elevated RLS)
- Funnel: PO cycle stages — Requisition → PO Created → Released → Confirmed → GR Posted → Invoice Paid — with avg cycle time per stage
- Table: POs currently pending approval beyond SLA with escalation status
- Line Chart: Weekly 3-way match rate trend vs. target

**Filters/Slicers**: PO Value Bucket, Company Code, Purchasing Group, Approval Level  
**RLS**: Approver names visible only to Procurement Director and Internal Audit roles

---

## 15. Use Cases

### Use Case 1: Critical Component Supply Disruption Alert

**Scenario**: Production planning team identifies that a key electronic component (Material 1000567, ABC-A classification) has only 5 days of safety stock remaining. The open PO for 10,000 units is 15 days overdue from a single-source supplier in Taiwan.

**Analysis Steps**:
1. Open PO Follow-up page; filter by Material 1000567 and Risk Level = HIGH
2. Identify PO 4500088991 — open quantity 10,000 units, 15 days overdue, supplier "Taiwan Electronics Ltd" (LIFNR 1000890)
3. Review supplier OTD history on scatter plot: 78% OTD for past 12 months (Yellow threshold)
4. Check compliance dashboard: UFLPA coverage complete (no flag); CSDDD compliant
5. Drill to supplier contact details; initiate escalation call
6. Evaluate air freight cost vs. production stoppage cost in spend analysis page

**Decision**: Approve air freight expedite for 2,000 units (priority shipment); maintain sea freight for remaining 8,000 units. Category Manager to initiate secondary source qualification within 90 days.

### Use Case 2: Maverick Spend Investigation — Finance Cost Center

**Scenario**: CFO reports that IT Finance cost center CC-4501 has exceeded its indirect budget by 18% for Q1. Procurement governance audit finds low SUM rate for this cost center.

**Analysis Steps**:
1. Open Spend Analysis page; filter by cost center CC-4501 and fiscal period Q1 current year
2. Managed vs. Maverick chart shows 62% managed spend (Red threshold) — €820,000 maverick spend
3. Drill to maverick spend detail: 5 invoices from software vendor "CloudSoft GmbH" totaling €620,000 with no PO reference
4. Cross-check: CloudSoft GmbH is an approved vendor (not UFLPA/CSDDD flagged) but invoices bypassed procurement
5. Root cause: IT Director signed contracts directly without routing through procurement; invoices submitted by vendor directly to AP

**Decision**: Finance Controller rejects 2 pending CloudSoft invoices until POs are retroactively created and approved. IT Director notified of mandatory PO policy. Procurement governance team adds cost center CC-4501 to enhanced monitoring for 6 months. SAP MM configured to block non-PO invoices for GL account range used by software subscriptions.

### Use Case 3: UFLPA Pre-Shipment Compliance Check

**Scenario**: Trade Compliance team receives US CBP notification that a textile shipment is being held at Los Angeles port due to UFLPA reasonable cause determination. The shipment references PO 4500099123.

**Analysis Steps**:
1. Open Compliance Dashboard; search supplier by PO number 4500099123
2. Identify supplier "Xinjiang Apparel Manufacturing Co." — uflpa_flag = 1 (set 3 months ago via fuzzy match), uflpa_clearance_doc = NULL
3. Verify: PO was created 4 months ago; UFLPA flag was set 3 months ago; PO was not blocked because Apache Airflow alert was dismissed without action (P2 alert, not P1)
4. Total open exposure: 3 additional POs from this supplier totaling €1.8M (not yet shipped)

**Decision**: Immediate suspension of all POs to this supplier. Trade Compliance team engages CBP broker to prepare rebuttal documentation. CPO notified. Category Manager tasked with identifying alternative approved supplier within 30 days. Alert logic updated to escalate UFLPA-flagged POs to P1 regardless of value.

---

## 16. Recommended Actions

| Result / Condition | Recommended Action | Owner | Timeline |
|---|---|---|---|
| PO OTD < 90% for supplier (Red) | Issue formal Performance Improvement Notice; initiate monthly review meeting | Category Manager | Within 10 business days |
| Open overdue value > €5M | Escalate to Supply Chain Risk Committee; evaluate alternative sourcing | CPO / Supply Chain Director | Within 24 hours |
| UFLPA flag active, no clearance doc, new PO | Block PO release in SAP; contact Trade Compliance for clearance process | Trade Compliance Manager | Immediate (same day) |
| CSDDD Tier-1 supplier assessment expired | Issue assessment questionnaire via Ariba SLP; engage third-party ESG auditor if self-assessment refused | SLP Team / Head of Sustainability | Within 30 days of expiry |
| SUM rate < 80% for cost center (Red) | Enforce mandatory PO policy via SAP MM; retrain cost center owner | Procurement Governance + Finance Controller | Within 30 days |
| PO approval SLA breach > 72 hours | Escalate to approver's manager; activate delegation of authority for backup approver | Head of Procurement Operations | Within 24 hours of breach |
| Price variance > 10% vs. contract | Issue price dispute to supplier; review contract conditions record in SAP | Category Manager / Legal | Within 5 business days |
| 3-way match rate < 85% | Review PO quantity accuracy; training for buyers on GR posting timeliness | Procurement Operations | Monthly review |
| Single-source critical item, lead time > 90 days | Initiate dual-source qualification; consider safety stock increase | Category Manager + Supply Planning | Within 60 days |
| Supplier CSDDD status NON_COMPLIANT | Suspend new contract renewals; engage supplier in remediation plan; escalate to CPO if no progress in 60 days | Head of Sustainability + Legal | Within 30 days of identification |

---

## 17. Test Cases

### TC-001: Overdue PO Calculation Accuracy

- **Test ID**: TC-001
- **Scenario**: Verify that is_overdue flag and days_overdue calculation are correct for PO lines past their scheduled delivery date
- **Input Data**: PO 4500099999, Item 10, scheduled_delivery_date = 2026-06-01, gr_quantity = 0, po_quantity = 100, po_status = 'OPEN', load_date = 2026-06-22
- **Expected Result**: is_overdue = 1, days_overdue = 21, po_status = 'OPEN', open_value_eur = 100 * net_price_eur
- **Result to Avoid**: is_overdue = 0 (incorrect — would miss a real overdue order); days_overdue = NULL or negative
- **Required Validation**: SQL SELECT on fact_po_line for this PO confirms is_overdue=1 and days_overdue=21; confirm in Apache Superset PO Follow-up page table
- **Evidence**: Screenshot of Apache Superset table row for PO 4500099999; SQL query result exported to CSV

### TC-002: Currency Conversion EUR Calculation

- **Test ID**: TC-002
- **Scenario**: Verify EUR conversion for a PO in USD correctly applies the ECB rate for the PO creation date
- **Input Data**: PO 4500088001, net_value_loc = 100,000 USD, currency = 'USD', po_date = 2026-06-15; ECB EUR/USD rate on 2026-06-15 = 1.0780 (USD per EUR)
- **Expected Result**: net_value_eur = 100,000 / 1.0780 = 92,764.38 EUR (rounded to 2 decimal places)
- **Result to Avoid**: net_value_eur = 100,000 (no conversion applied); net_value_eur using today's rate instead of PO date rate
- **Required Validation**: Check dim_fx_rate for USD on 2026-06-15; verify net_value_eur in fact_po_line matches manual calculation ±€0.01
- **Evidence**: dim_fx_rate query result; fact_po_line query result; Finance sign-off on FX rate used

### TC-003: UFLPA Fuzzy Match Threshold

- **Test ID**: TC-003
- **Scenario**: Verify that fuzzy matching correctly flags suppliers above the 85% confidence threshold and creates manual review flags for 70-84% matches
- **Input Data**: CBP Entity "Xinjiang Textile Manufacturing Co. Ltd"; SAP Vendor "Xinjiang Textile Manufacturing Company" (should match >85%); SAP Vendor "Xinjiang Apparel Corp" (should score 70-84%); SAP Vendor "Shanghai Electronics Ltd" (should score <70%)
- **Expected Result**: Vendor 1 → uflpa_flag=1, match_score≥85; Vendor 2 → uflpa_flag=0, manual_review_required=1, match_score 70-84; Vendor 3 → uflpa_flag=0, manual_review_required=0
- **Result to Avoid**: False negative (Vendor 1 not flagged); false positive (Vendor 3 flagged); NULL scores for any comparison
- **Required Validation**: Run Python UFLPA script against test dataset; review uflpa_match log table; Trade Compliance Manager reviews Vendor 2 manually
- **Evidence**: Python script output CSV with match scores; uflpa_match log table screenshot; Trade Compliance Manager review email

### TC-004: Soft Delete Retention

- **Test ID**: TC-004
- **Scenario**: Verify that a cancelled PO line (LOEKZ set to 'L' in SAP) is updated to deletion_flag=1 in PostgreSQL but the row is NOT deleted
- **Input Data**: PO 4500077001 Item 10, currently in fact_po_line with deletion_flag=0; simulate SAP delta showing LOEKZ='L' for this item
- **Expected Result**: Row remains in fact_po_line with deletion_flag=1, po_status='CANCELLED'; row count in fact_po_line unchanged
- **Result to Avoid**: Row physically deleted from fact_po_line (audit trail lost); deletion_flag remains 0 after delta load
- **Required Validation**: COUNT(*) from fact_po_line before and after delta load (counts must be equal); SELECT on specific PO item confirming deletion_flag=1
- **Evidence**: PostgreSQL audit log confirming no DELETE DML executed; SQL query results before/after showing flag update only

### TC-005: CSDDD Non-Compliant Alert Trigger

- **Test ID**: TC-005
- **Scenario**: Verify that a Tier-1 supplier with an expired CSDDD assessment (> 3 years old) triggers the compliance alert and appears as NON_COMPLIANT in the dashboard
- **Input Data**: dim_supplier row: csddd_tier='TIER1', csddd_assessment_date='2022-06-01', csddd_status='COMPLIANT' (as-was); current date = 2026-06-22 (assessment is 4 years old)
- **Expected Result**: csddd_status updated to 'NON_COMPLIANT' in nightly ETL run; supplier appears in Red on CSDDD dashboard; Apache Airflow alert sent to SLP Team
- **Result to Avoid**: csddd_status remains 'COMPLIANT' despite expired assessment; no alert sent; supplier not highlighted in dashboard
- **Required Validation**: Check dim_supplier after ETL run for this LIFNR; verify Apache Superset CSDDD page shows this supplier in red; check Apache Airflow run history for alert execution
- **Evidence**: dim_supplier query before/after ETL; Apache Superset screenshot; Apache Airflow flow run log with recipient confirmation

---

## 18. Risks and Mitigations

| Risk | Probability | Impact | Preventive Control | Corrective Control |
|---|---|---|---|---|
| SAP data extraction failure (Airflow pipeline) | Medium | High | Daily pipeline health monitoring with Grafana alerts; retry logic (3 attempts with 15-min backoff) | Manual SAP ME2M report export as fallback; notify users of data staleness via Superset banner |
| FX rate API downtime (ECB) | Low | Medium | Fallback to prior business day rate automatically; Finance backup Bloomberg rate file | Manual rate upload to dim_fx_rate by Finance Treasury within 4 hours |
| UFLPA entity list false positive (reputation risk) | Medium | High | 85% confidence threshold with manual review for 70-84% matches; Trade Compliance sign-off required | Vendor dispute process; re-screening within 5 business days; legal review for high-spend suppliers |
| Apache Superset RLS misconfiguration (data leak) | Low | Critical | RLS unit tested with each user role; annual RLS audit by IT Security | Immediate workspace take-down; IT Security incident response; user notification per GDPR breach requirements |
| Vendor master data quality (duplicate LIFNRs) | High | Medium | Automated deduplication check in ETL; parent_vendor_id mapping for same legal entity | Data cleansing sprint; SAP vendor merge (MK06) for confirmed duplicates; MDM governance process |
| CSDDD assessment data incomplete in Ariba | High | High | SLP team trained on mandatory fields; Ariba form validation rules enforced | Manual data entry fallback via PostgreSQL; SLP team chased weekly until 100% complete |
| PostgreSQL performance degradation (large data volumes) | Medium | Medium | Fact table partitioning by fiscal year; materialized SQL views for common aggregations; provisioned read replicas | Scale up database instance temporarily; optimize slow queries; add appropriate indexes |
| GDPR compliance risk (supplier contact data in Apache Superset) | Low | High | PII review of all fields loaded to PostgreSQL; limit to business contacts only; data retention policy enforced | Remove PII fields immediately; notify DPO; conduct DPIA review |

---

## 19. Implementation Checklist

1. Confirm SAP S/4HANA system access for Apache Airflow service account (read-only RFC user) — signed off by SAP Basis team
2. Configure Apache Airflow pipelines for EKKO, EKPO, EKET, MSEG, LFA1, LFB1, LFM1 extraction with incremental delta load logic
3. Build PostgreSQL star schema (fact_po_line, fact_gr_receipt, fact_compliance_assessment, dim_supplier, dim_material, dim_date, dim_company_code, dim_plant, dim_purchasing_org, dim_commodity, dim_fx_rate)
4. Implement MATKL → UNSPSC commodity mapping table; achieve ≥95% mapping coverage by PO value; residual unmapped items assigned for manual classification
5. Configure ECB FX rate daily extract pipeline; test fallback mechanism for weekends and API downtime
6. Develop and test Python UFLPA fuzzy matching script; set 85% threshold; build uflpa_match audit log table; test against CBP entity list current version
7. Set up Ariba SLP API connection via an API gateway; implement rate limit handling and exponential backoff; schedule daily pull at 02:00 UTC
8. Build LIFNR ↔ Ariba ANID cross-reference table; coordinate with Ariba admin for ANID extraction; handle unmatched records
9. Implement PO risk scoring logic in PostgreSQL computed columns or Python ETL step; validate risk_score distribution against Category Manager expert judgment
10. Build Apache Superset data model with star schema relationships; configure RLS roles (Global, Company Code, Purchasing Organization); test RLS with 5 user profiles
11. Develop all 5 Apache Superset report pages (Executive Overview, PO Follow-up, Spend Analysis, Compliance Dashboard, Process Health); apply company brand template
12. Configure all KPI SAP metrics; validate each KPI against SAP source system (ME2N, ME2M reports); sign off with Finance Controller
13. Build Apache Airflow flows for P1, P2, P3 alerts; test each alert scenario with real data; confirm recipient lists with Category Management and Trade Compliance
14. Conduct User Acceptance Testing (UAT) with 3 Category Managers, 1 Procurement Director, 1 Trade Compliance Manager, 1 Finance Controller
15. Resolve all UAT defects (Severity 1 and 2 must be zero before go-live)
16. Configure Apache Superset workspace data refresh schedule (daily 06:00 UTC); confirm PostgreSQL firewall rules allow Apache Superset service IP ranges
17. Publish Apache Superset solution to production workspace; distribute access per authorization matrix
18. Train end users: 2-hour training session for buyers (PO Follow-up + Spend Analysis); 1-hour session for Compliance team (Compliance Dashboard); 30-min executive briefing
19. Complete documentation: data dictionary finalized, ETL design document signed, data lineage diagram approved
20. Hypercare support period: 4 weeks post go-live with data engineer on-call for pipeline issues; weekly check-in with key users

---

## 20. Validation Checklist

1. Confirm fact_po_line row count matches SAP EKPO count for at least 3 fiscal periods (tolerance ±0.1%)
2. Confirm total SUM(net_value_eur) in Apache Superset matches SAP ME2N value for current fiscal year (tolerance ±1%)
3. Confirm all 40 company code currencies have FX rates in dim_fx_rate for each business day in the past 12 months
4. Confirm UFLPA screening coverage = 100% for all active suppliers (no NULL screening dates)
5. Confirm CSDDD Tier-1 supplier list has been agreed and signed off by Head of Sustainability and Legal Counsel
6. Confirm all 6 KPI SQL formulas produce results that reconcile to SAP source reports (ME2N, ME2M, MRBR) within stated tolerances
7. Confirm Apache Superset RLS restricts user access correctly: test with 3 users from different purchasing organizations; verify each sees only their authorized data
8. Confirm all 5 Apache Airflow alert flows trigger correctly in UAT: test each with synthetic trigger data; confirm email delivery within defined SLA (P1 ≤ 2 hours)
9. Confirm soft delete logic is working: cancel a test PO in SAP QAS; run ETL; verify deletion_flag=1 and row count unchanged in PostgreSQL
10. Confirm 3-year historical data load is complete: spot-check 10 POs per fiscal year for 2023, 2024, 2025; verify accuracy of all fields
11. Confirm commodity UNSPSC mapping coverage ≥ 95% by PO value; residual unmapped items documented and assigned for manual classification
12. Confirm dim_supplier is_active flag correctly excludes blocked vendors (SAP LFM1.SPERM = 'X'); verify with 5 known blocked vendors
13. Confirm days_overdue = 0 for non-overdue POs and correctly computed positive integer for overdue POs (test with 10 known overdue POs from SAP ME2M)
14. Confirm Apache Superset report refresh completes within 30 minutes for full dataset load; performance test with simulated peak usage (20 concurrent users)
15. Confirm all evidence documents (reconciliation reports, sign-offs, UAT results) are filed in the Git document repository audit folder before go-live approval

---

## 21. Pending Information to Confirm

1. **SAP Company Code List**: Confirm the complete list of all 40 active company codes (BUKRS) to be included in scope; Finance must confirm which codes are dormant or in wind-down
2. **PO Approval Threshold by Country**: Confirm whether €5,000 / €50,000 / €500,000 approval thresholds are uniform across all 40 countries or vary by entity (local delegation of authority policies may differ)
3. **CSDDD Tier-1 Spend Threshold**: Confirm whether the €1M per legal entity annual spend threshold for CSDDD Tier-1 classification is correct or if the business uses a different grouping (e.g., €1M at group level consolidated across entities)
4. **Ariba ANID Cross-Reference Table**: Confirm availability of LIFNR ↔ Ariba ANID mapping table from Ariba admin team; if not maintained, confirm process for manual creation
5. **Maverick Spend Data Source**: Confirm which SAP table or report is the authoritative source for non-PO invoices (AP invoices without PO reference) — RBKP/RSEG or a custom Z-table maintained by Finance
6. **UFLPA Screening Frequency**: Confirm with Trade Compliance whether annual screening is sufficient or if quarterly re-screening of flagged suppliers is required
7. **Apache Airflow Alert Recipients**: Confirm named recipients (email addresses and distribution lists) for each P1, P2, P3 alert type by commodity category and country
8. **Historical Load Period**: Confirm whether 3-year history (2023–2025) is the agreed scope or whether a longer period (5 years) is required for trend analysis and CSDDD document retention
9. **Data Retention Policy**: Confirm with IT Security and Legal the agreed data retention period for PostgreSQL (proposed: 7 years aligned with UK Modern Slavery Act and CSDDD Art. 23 minimum 5 years)
10. **Price Variance Tolerance**: Confirm with Finance Controller whether 5% price variance tolerance for PO-vs-contract comparison is the agreed threshold or if it varies by commodity (e.g., commodities with volatile spot pricing may need 10-15%)
11. **PostgreSQL Tier Confirmation**: Confirm with IT Infrastructure that the PostgreSQL instance is pre-approved and provisioned; confirm backup and DR configuration
12. **Apache Superset Access**: Confirm all end users have Apache Superset accounts and role assignments; estimated 50 report users + 5 admin users

---

## 22. Implementation Roadmap

| Week | Activity | Deliverable | Owner | Status |
|---|---|---|---|---|
| Week 1 | SAP access provisioning; ADF environment setup; commodity mapping table build | ADF service account active; PostgreSQL schema created; 95% UNSPSC mapping achieved | Data Engineer + Procurement Ops | Not Started |
| Week 2 | EKKO/EKPO/EKET extraction pipelines; historical 3-year load; row count reconciliation | fact_po_line populated with 3 years of data; reconciliation report signed | Data Engineer | Not Started |
| Week 3 | MSEG (GR) extraction; GR quantities aggregated to PO line; overdue flags derived | fact_gr_receipt populated; is_overdue and days_overdue computed and validated | Data Engineer | Not Started |
| Week 4 | LFA1/LFB1 vendor master load; Ariba API connection; LIFNR-ANID mapping | dim_supplier populated; Ariba data merged; ANID cross-reference confirmed | Data Engineer + Ariba Admin | Not Started |
| Week 5 | UFLPA fuzzy matching Python script; CBP entity list integration; UFLPA audit log | uflpa_flag set for all active suppliers; 100% screening coverage achieved; Trade Compliance sign-off | Data Engineer + Trade Compliance | Not Started |
| Week 6 | CSDDD assessment data from Ariba SLP; fact_compliance_assessment load; CSDDD logic | fact_compliance_assessment populated; Tier-1 list confirmed; CSDDD status derived | SLP Team + Data Engineer | Not Started |
| Week 7 | ECB FX rate pipeline; currency conversion logic; spend value reconciliation | dim_fx_rate complete for 3 years; net_value_eur populated; Finance reconciliation signed | Data Engineer + Finance Controller | Not Started |
| Week 8 | Apache Superset data model build; star schema relationships; RLS configuration | Apache Superset dataset published to dev workspace; RLS tested with 3 roles | BI Developer | Not Started |
| Week 9 | Apache Superset Page 1 (Executive Overview) + Page 2 (PO Follow-up) build; KPI SQL metrics | Pages 1-2 complete with all visuals and KPIs; validated against SAP ME2N/ME2M | BI Developer | Not Started |
| Week 10 | Apache Superset Page 3 (Spend Analysis) + Page 4 (Compliance Dashboard) + Page 5 (Process Health) | Pages 3-5 complete; all 6 KPIs reconciled to source; company branding applied | BI Developer | Not Started |
| Week 11 | Apache Airflow alert flows (P1, P2, P3); test all alert scenarios | All alert flows active and tested; recipient lists confirmed; test run logs saved | BI Developer + Procurement Ops | Not Started |
| Week 12 | User Acceptance Testing (UAT) with Category Managers, Trade Compliance, Finance | Signed UAT sign-off from all 6 testers; defect log with zero S1/S2 open items | All stakeholders | Not Started |
| Week 13 | UAT defect resolution; final reconciliation reports; documentation completion | All defects resolved; data dictionary finalized; go-live approval from CPO | Data Engineer + BI Developer | Not Started |
| Week 14 | Production go-live; user training sessions; hypercare begins | Solution live in production workspace; 50 users trained; hypercare schedule active | Project Manager + Data Engineer | Not Started |
| Week 15–18 | Hypercare: weekly pipeline monitoring; user feedback; performance tuning | Weekly hypercare report; performance within SLA (refresh < 30 min); zero P1 incidents | Data Engineer + BI Developer | Not Started |
| Week 19 | Post-implementation review; lessons learned; Phase 2 scope definition | PIR document signed; Phase 2 scope (Tier-2 CSDDD, predictive overdue model) approved by CPO | Project Manager + CPO | Not Started |
