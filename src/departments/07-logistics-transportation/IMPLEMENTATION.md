# Logistics & Transportation Analytics — Implementation Guide

**Department**: 07 — Logistics & Transportation
**Analytics Domain**: Delivery Performance, Freight Cost, Carrier Scorecard, Customs Risk, Carbon Footprint
**Standard Alignment**: Incoterms® 2020, GLEC Framework v3, ISO 28000:2022, WCO HS Nomenclature 2022,
EU CBAM Regulation 2023/956, C-TPAT, AEO, WTO TFA Art. 7, IMO/IMDG, IATA DGR
**Systems**: SAP S/4HANA, SAP TM (Transportation Management), SAP GTS (Global Trade Services),
Power BI, Azure SQL, EDI DESADV / IFTSTA
**Author**: Supply Chain Centre of Excellence
**Version**: 3.0 — 2026-06-22
**Status**: Approved for Implementation
**Scope**: 40 countries, multi-carrier, multi-modal, multi-freight-forwarder

---

## Table of Contents

1. Executive Summary
2. Analysis Objective
3. Scope
4. Business Questions
5. Data Sources
6. Data Model
7. Data Dictionary
8. Transformation Rules
9. Business Rules
10. KPIs and Formulas
11. Analytical Logic
12. Validations and Controls
13. Required Evidence
14. Dashboard Design
15. Use Cases
16. Recommended Actions
17. Test Cases
18. Risks and Mitigations
19. Implementation Checklist
20. Validation Checklist
21. Pending Information
22. Implementation Roadmap

---

## 1. Executive Summary

The Logistics & Transportation Analytics module delivers end-to-end visibility into the physical
movement of goods across the enterprise supply chain — from origin supplier facilities through
international transit to final delivery destinations. Operating across 40 countries with a
multi-modal network (ocean, air, road, rail, intermodal), the analytical capability described
in this document transforms raw shipment events, freight invoices, customs declarations, and
carrier EDI feeds into actionable intelligence for logistics managers, trade compliance teams,
and senior supply chain leadership.

### Strategic Context

Logistics cost represents typically 8–12% of total revenue in consumer goods and industrial
manufacturing sectors. Carrier OTD performance directly drives downstream customer service
levels; a single percentage point improvement in OTD at the carrier level translates to a
measurable reduction in expediting cost, customer penalty chargebacks, and safety stock
requirements. Carbon reporting obligations under EU CBAM (effective October 2023) and the
voluntary GLEC Framework create new data requirements that must be integrated into the
core shipment data model.

### Key Objectives

- Achieve and sustain carrier OTD of 95% or above across all lanes and modes
- Reduce blended freight cost per kg-km by 12% in Year 1 through lane consolidation,
  modal shift optimisation, and carrier rate renegotiation
- Deliver full Incoterms 2020 compliance on all international purchase orders, eliminating
  DDP mis-classification that exposes the company to customs liability and penalties
- Establish real-time shipment visibility across 100% of active shipments
- Produce accurate CO2 per shipment reporting aligned with GLEC Framework v3 for
  EU CBAM compliance and ESG disclosure
- Build a carrier scorecard that drives quarterly business reviews and annual RFP decisions

### Expected Business Value

| Benefit | Year 1 | Year 2 |
|---------|--------|--------|
| Freight cost reduction (lane optimisation) | 8% | 12% |
| Carrier penalty recovery improvement | +25% recovery rate | +40% |
| Customs delay reduction | -30% clearance days | -50% |
| CO2 reporting compliance | 100% CBAM coverage | GLEC certified |
| OTD improvement | +4 pp to 95% | +2 pp to 97% |

---

## 2. Analysis Objective

The primary objective of this analytics implementation is to provide the Logistics &
Transportation department with a robust, governed, and automated analytical layer that:

1. **Measures delivery performance** at granular levels — by carrier, lane, transport mode,
   origin country, destination country, and shipment type — against contractual and
   operational targets.

2. **Controls freight spend** by comparing actual invoiced freight costs against budgeted
   rates, quoted rates, and benchmark market rates, segmented by cost-per-kg, cost-per-km,
   and cost-per-unit.

3. **Scores carrier performance** through a weighted multi-dimensional scorecard
   (OTIF, transit time adherence, documentation accuracy, claims rate, sustainability),
   driving carrier tiering decisions (Preferred / Approved / Watch / Disqualified).

4. **Identifies customs and trade compliance risk** at the shipment level, flagging
   shipments with missing documentation, HS code inconsistencies, denied party screening
   hits, or UFLPA exposure.

5. **Quantifies carbon emissions** per shipment using GLEC Framework v3 methodology,
   enabling CO2 reporting by business unit, product category, Incoterm, and trade lane
   for EU CBAM compliance and voluntary ESG disclosure.

6. **Automates alerts and escalations** so that exception management is proactive rather
   than reactive — late shipments, cost overruns, customs holds, and high-emission lanes
   are surfaced automatically to responsible owners.

---

## 3. Scope

### In Scope

- All outbound shipments from supplier to company warehouses (inbound logistics)
- All outbound shipments from company warehouses to customers (outbound logistics)
- Inter-company / inter-warehouse stock transfer orders with logistics cost allocation
- Ocean freight (FCL and LCL), air freight, road transport (FTL and LTL), rail, and parcel
- All 40 operational countries across Europe, North America, LATAM, Asia-Pacific, Middle East
- All contracted carriers and freight forwarders in the approved vendor list
- Customs entries managed through SAP GTS (import and export)
- Freight invoices processed through SAP TM freight settlement
- EDI DESADV (Despatch Advice) and IFTSTA (Multimodal Status Report) message feeds
- CO2 calculation per shipment leg using GLEC Framework v3 emission factors

### Out of Scope

- Last-mile B2C parcel delivery managed by third-party logistics providers without EDI feed
- Informal couriers and hand-carry shipments below EUR 200 customs value threshold
- Internal plant-to-plant movements within the same legal entity and same customs territory
  (unless specific cost allocation is requested by Finance)
- Passenger air cargo booking analytics (handled by the Travel Management team)

### Geographic Boundaries

Primary trade lanes: Europe–Asia (ocean), Europe–North America (ocean and air),
Intra-Europe (road and rail), North America domestic (road and rail).
Secondary lanes: LATAM, Middle East, Africa (limited carrier EDI availability — manual
reconciliation required for these lanes until EDI onboarding is complete).

---

## 4. Business Questions

The following business questions define the analytical agenda for this implementation.
Each question maps to one or more KPIs defined in Section 10.

**BQ-01** — Which carriers are consistently missing their ETA commitments, and on which
specific trade lanes does the worst OTD performance occur? Is the root cause carrier
operational failure or systemic port congestion and customs delay outside carrier control?

**BQ-02** — What is our total freight cost per kg, per km, and per unit by transport mode
and trade lane for the current fiscal year? How does this compare to the budgeted rate,
the contracted rate, and the market spot rate? Where are the largest cost overruns?

**BQ-03** — Which freight invoices deviate from quoted rates by more than the agreed
tolerance (typically ±5%)? Are there systematic billing errors by specific carriers or
freight forwarders, and what is the total financial exposure from unrecovered overbilling?

**BQ-04** — What is the modal split (ocean vs. air vs. road vs. rail) by trade lane,
and is air freight being used for non-emergency shipments where ocean would suffice?
What is the premium cost of air versus ocean on lanes where both modes are available?

**BQ-05** — What is the customs clearance lead time by country, commodity, and customs
broker? Which shipments are experiencing clearance delays above the country-specific
threshold? What are the most frequent causes of customs holds (documentation, valuation,
classification disputes)?

**BQ-06** — Which shipments carry the highest customs compliance risk score, combining
factors such as UFLPA supplier exposure, HS code mismatch probability, missing preferential
origin documentation, and denied party screening alerts?

**BQ-07** — What is the CO2 footprint per shipment, per trade lane, and per transport mode?
Which lanes and carriers are driving the highest absolute and intensity emissions?
What would the CO2 impact of modal shift from air to ocean be on the top 20 air lanes?

**BQ-08** — How is carrier OTIF (on-time and in-full) trending over the last 12 rolling
months? Are there seasonal patterns? Which carriers show consistent improvement or
deterioration versus their contractual OTIF commitment?

**BQ-09** — What is the claims rate (damaged, lost, or short-delivered shipments) by
carrier and commodity category? What is the financial value of open cargo claims, and
what is the average claim resolution time by carrier?

**BQ-10** — Which freight forwarders are providing accurate and timely documentation
(commercial invoice, packing list, bill of lading, certificate of origin) within the
agreed cut-off windows? What is the documentation error rate by forwarder?

**BQ-11** — What is the dwell time at major hub ports and consolidation centres, and
how does excessive dwell time correlate with final delivery delay and incremental
storage cost?

**BQ-12** — For the EU CBAM-covered commodities (steel, aluminium, cement, fertilisers,
electricity, hydrogen), what is the total verified CO2 content per import shipment,
and are all required CBAM declarant certificates in place?

---

## 5. Data Sources

### DS-01: SAP TM — Transportation Orders

| Attribute | Detail |
|-----------|--------|
| Source Name | SAP Transportation Management — Transportation Orders |
| System | SAP TM 9.6 (integrated with SAP S/4HANA 2023) |
| Table / Report | /SCMTMS/D_TOR (Transportation Order), /SCMTMS/D_TORITEM (Order Items) |
| Owner | Global Logistics Operations — TM System Administrator |
| Frequency | Real-time via RFC/iDoc; Power BI refresh every 4 hours |
| Required Fields | TOR_ID, CARRIER_ID, ORIGIN_LOC, DEST_LOC, PLANNED_DEP_DATE, PLANNED_ARR_DATE, ACTUAL_DEP_DATE, ACTUAL_ARR_DATE, FREIGHT_COST_LC, FREIGHT_COST_GC, WEIGHT_KG, VOLUME_CBM, DISTANCE_KM, TRANSPORT_MODE, INCOTERM_CODE, CURRENCY, STATUS |
| Critical Fields | ACTUAL_ARR_DATE (null = in-transit), FREIGHT_COST_GC (must not be zero for settled orders), CARRIER_ID (must resolve to approved carrier master) |
| Primary Key | TOR_ID |
| Validations | ACTUAL_ARR_DATE >= ACTUAL_DEP_DATE; FREIGHT_COST_GC > 0 when status = SETTLED; WEIGHT_KG > 0; INCOTERM_CODE in approved Incoterms 2020 list |
| Known Errors | Duplicate TOR records created during system cutover periods (filter by CREATED_ON > go-live date); DISTANCE_KM occasionally NULL for short-haul road — requires geocoding fill |
| Evidence Required | SAP TM configuration document, carrier master extract, TOR field mapping document |

### DS-02: SAP GTS — Customs Declarations

| Attribute | Detail |
|-----------|--------|
| Source Name | SAP Global Trade Services — Customs Declarations |
| System | SAP GTS 14.0 |
| Table / Report | /SAPSLL/CUHD (Customs Header), /SAPSLL/CUITEM (Customs Item), /SAPSLL/DOCFLOW |
| Owner | Trade Compliance Manager |
| Frequency | Daily batch extract at 06:00 UTC; supplemented by real-time status events |
| Required Fields | CUSTOMS_DECL_ID, TOR_ID, HS_CODE, COUNTRY_OF_ORIGIN, COUNTRY_OF_IMPORT, CUSTOMS_VALUE_GC, DUTY_AMOUNT, VAT_AMOUNT, CUSTOMS_ENTRY_DATE, RELEASE_DATE, DECLARATION_STATUS, BROKER_ID, REGIME_CODE |
| Critical Fields | HS_CODE (8-digit minimum for EU, 10-digit for US HTS), RELEASE_DATE (null = pending clearance), CUSTOMS_VALUE_GC |
| Primary Key | CUSTOMS_DECL_ID |
| Validations | HS_CODE length >= 8; CUSTOMS_VALUE_GC > 0; RELEASE_DATE >= CUSTOMS_ENTRY_DATE; COUNTRY_OF_ORIGIN is a valid ISO 3166-1 alpha-2 code |
| Known Errors | RELEASE_DATE not populated for informal entries below de minimis threshold — these must be excluded from clearance lead time calculations |
| Evidence Required | GTS configuration guide, HS code master extract, customs broker agreement |

### DS-03: EDI DESADV — Despatch Advice (EDIFACT D.96A)

| Attribute | Detail |
|-----------|--------|
| Source Name | EDI DESADV — Supplier Despatch Advice Messages |
| System | EDI middleware (Azure Integration Services) mapped to Azure SQL staging table |
| Table / Report | stg.EDI_DESADV, stg.EDI_DESADV_LINE |
| Owner | Supplier Integration Team / EDI Operations |
| Frequency | Real-time on despatch; processed within 15 minutes of receipt |
| Required Fields | DESADV_ID, PO_NUMBER, SUPPLIER_ID, DESPATCH_DATE, ESTIMATED_ARRIVAL, CARRIER_SCAC, TRACKING_NUMBER, GROSS_WEIGHT_KG, PACKAGE_COUNT, LINE_ITEM_QTY, UNIT_OF_MEASURE |
| Critical Fields | DESPATCH_DATE, TRACKING_NUMBER (null = no carrier visibility), CARRIER_SCAC |
| Primary Key | DESADV_ID + LINE_NUMBER |
| Validations | DESPATCH_DATE <= today + 5 days (reject future-dated by >5 days as likely error); GROSS_WEIGHT_KG > 0; PO_NUMBER resolves to active PO in SAP |
| Known Errors | Some suppliers send DESADV after goods already in transit — DESPATCH_DATE post-dated; handle with tolerance window |
| Evidence Required | EDI partner agreement, DESADV message specification, carrier SCAC code master |

### DS-04: EDI IFTSTA — Multimodal Status Report (EDIFACT D.00B)

| Attribute | Detail |
|-----------|--------|
| Source Name | EDI IFTSTA — Carrier Status Updates |
| System | Azure Integration Services → Azure SQL stg.EDI_IFTSTA |
| Table / Report | stg.EDI_IFTSTA, stg.EDI_IFTSTA_EVENT |
| Owner | Carrier Integration Team |
| Frequency | Real-time event streaming; carriers transmit at each status milestone |
| Required Fields | IFTSTA_MSG_ID, TRACKING_NUMBER, EVENT_CODE, EVENT_DATETIME, EVENT_LOCATION, VESSEL_NAME, VOYAGE_NUMBER, CONTAINER_NUMBER, ETA_UPDATED |
| Critical Fields | EVENT_CODE (maps to milestone: DEPARTED, ARRIVED, CUSTOMS_CLEARED, DELIVERED), EVENT_DATETIME, ETA_UPDATED |
| Primary Key | IFTSTA_MSG_ID |
| Validations | EVENT_DATETIME <= current UTC time (no future events except ETA); EVENT_CODE in approved event code master; TRACKING_NUMBER resolves to active TOR |
| Known Errors | Carriers occasionally send duplicate IFTSTA events with same event code and datetime — deduplicate on TRACKING_NUMBER + EVENT_CODE + EVENT_DATETIME |
| Evidence Required | IFTSTA message guide per carrier, event code mapping table |

### DS-05: SAP TM — Freight Settlement (Freight Invoices)

| Attribute | Detail |
|-----------|--------|
| Source Name | SAP TM Freight Settlement — Freight Cost Documents |
| System | SAP TM / SAP S/4HANA FI |
| Table / Report | /SCMTMS/D_FSD (Freight Settlement Document), RSEG (Invoice Line Items) |
| Owner | Freight Audit & Payment Team |
| Frequency | Daily batch; invoice matching runs nightly |
| Required Fields | FSD_ID, TOR_ID, CARRIER_ID, INVOICE_NUMBER, INVOICE_DATE, QUOTED_RATE_GC, ACTUAL_INVOICE_GC, SURCHARGE_AMOUNT, CURRENCY, SETTLEMENT_STATUS, DISPUTE_FLAG, DISPUTE_REASON |
| Critical Fields | ACTUAL_INVOICE_GC, QUOTED_RATE_GC (both required for variance calculation), SETTLEMENT_STATUS |
| Primary Key | FSD_ID |
| Validations | ACTUAL_INVOICE_GC > 0; QUOTED_RATE_GC > 0 for contracted carriers; variance abs((ACTUAL - QUOTED)/QUOTED) > 0.05 triggers dispute flag |
| Known Errors | Spot market shipments may lack QUOTED_RATE_GC — use market benchmark rate from freight rate management system |
| Evidence Required | Freight rate cards, carrier contract extracts, SAP TM settlement configuration |

### DS-06: Carbon Emission Factor Reference Table

| Attribute | Detail |
|-----------|--------|
| Source Name | GLEC Framework v3 Emission Factors — Reference Table |
| System | Azure SQL ref.GLEC_EMISSION_FACTORS (manually maintained, version-controlled) |
| Table / Report | ref.GLEC_EMISSION_FACTORS |
| Owner | Sustainability / ESG Analytics Team |
| Frequency | Annual update aligned with GLEC Framework release cycle |
| Required Fields | MODE, VESSEL_TYPE, FUEL_TYPE, LADEN_FACTOR, EMISSION_FACTOR_gCO2e_PER_TKM, VALID_FROM, VALID_TO, GLEC_VERSION |
| Critical Fields | EMISSION_FACTOR_gCO2e_PER_TKM, LADEN_FACTOR, VALID_FROM (use version valid at shipment date) |
| Primary Key | MODE + VESSEL_TYPE + FUEL_TYPE + VALID_FROM |
| Validations | No gaps in VALID_FROM / VALID_TO coverage; EMISSION_FACTOR > 0; LADEN_FACTOR between 0.4 and 1.0 |
| Known Errors | N/A — manually maintained reference table; changes require change request and dual approval |
| Evidence Required | GLEC Framework v3 publication, internal ESG team sign-off on factor selection |

### DS-07: Carrier and Lane Master

| Attribute | Detail |
|-----------|--------|
| Source Name | Carrier Master and Trade Lane Configuration |
| System | Azure SQL ref.CARRIER_MASTER, ref.TRADE_LANE |
| Table / Report | ref.CARRIER_MASTER, ref.TRADE_LANE, ref.CARRIER_CONTRACT |
| Owner | Procurement — Logistics Category Manager |
| Frequency | Updated on contract changes; at minimum quarterly review |
| Required Fields | CARRIER_ID, CARRIER_NAME, CARRIER_SCAC, CARRIER_TYPE (OCEAN/AIR/ROAD/RAIL/PARCEL), CONTRACT_OTD_TARGET_PCT, CONTRACT_OTIF_TARGET_PCT, TIER (PREFERRED/APPROVED/WATCH/DISQUALIFIED), COUNTRY_OF_REGISTRATION, IS_ACTIVE |
| Critical Fields | CARRIER_ID, CONTRACT_OTD_TARGET_PCT (defaults to 95% if no contract), TIER |
| Primary Key | CARRIER_ID |
| Validations | CARRIER_SCAC is unique; CONTRACT_OTD_TARGET_PCT between 85 and 100; TIER in (PREFERRED, APPROVED, WATCH, DISQUALIFIED) |
| Known Errors | Legacy carriers in SAP with deprecated SCAC codes — must be mapped to current SCAC via alias table |
| Evidence Required | Approved vendor list extract, carrier contract summaries, logistics category strategy document |

---

## 6. Data Model

The logistics analytics data model follows a star schema optimised for Power BI DirectQuery
and Azure SQL analytical queries. The central fact table is FACT_SHIPMENT, joined to seven
dimension tables.

```
                    DIM_CARRIER
                        |
DIM_DATE -------- FACT_SHIPMENT -------- DIM_LOCATION
                        |
                   DIM_TRANSPORT_MODE
                        |
                   DIM_INCOTERM
                        |
                   FACT_FREIGHT_INVOICE (related via TOR_ID)
                        |
                   FACT_CUSTOMS_DECLARATION (related via TOR_ID)
                        |
                   FACT_SHIPMENT_CO2 (related via TOR_ID)
                        |
                   FACT_CARRIER_EVENTS (related via TRACKING_NUMBER)
```

### Central Fact Tables

**FACT_SHIPMENT** — one row per transportation order. Contains planned and actual dates,
weights, volumes, distances, Incoterm, carrier, origin and destination.

**FACT_FREIGHT_INVOICE** — one row per freight invoice line. Contains quoted rate, actual
invoice amount, surcharges, settlement status, and dispute flag.

**FACT_CUSTOMS_DECLARATION** — one row per customs declaration. Contains HS code, declared
value, duty, VAT, entry date, release date, and compliance risk flags.

**FACT_SHIPMENT_CO2** — one row per shipment leg. Contains distance, weight, laden factor,
emission factor applied, CO2e calculated, and GLEC version used.

**FACT_CARRIER_EVENTS** — one row per carrier milestone event. Contains event code, timestamp,
location, and delta versus planned schedule.

### Dimension Tables

**DIM_DATE** — standard date dimension with fiscal year, quarter, week, and holiday flags.

**DIM_CARRIER** — carrier master with tier, mode, contract targets, country of registration,
and sustainability certifications (ISO 14001, SmartWay, Clean Cargo).

**DIM_LOCATION** — port, airport, warehouse, and customer site master with country, region,
UN/LOCODE, lat/lon, and customs office code.

**DIM_TRANSPORT_MODE** — ocean FCL, ocean LCL, air, road FTL, road LTL, rail, intermodal,
parcel. Includes GLEC mode code for CO2 calculation lookup.

**DIM_INCOTERM** — 11 Incoterms 2020 rules with risk transfer point, cost responsibility,
insurance obligation, and typical usage by mode.

---

## 7. Data Dictionary

### FACT_SHIPMENT

| Field | Description | Type | Nullable | Validation |
|-------|-------------|------|----------|------------|
| TOR_ID | Transportation order unique identifier (PK) | VARCHAR(20) | No | Must be unique; format TOR-YYYYNNNNNNN |
| CARRIER_ID | Foreign key to DIM_CARRIER | VARCHAR(10) | No | Must exist in DIM_CARRIER.CARRIER_ID |
| ORIGIN_LOC_ID | Foreign key to DIM_LOCATION (origin) | VARCHAR(10) | No | Must be a valid UN/LOCODE |
| DEST_LOC_ID | Foreign key to DIM_LOCATION (destination) | VARCHAR(10) | No | Must be a valid UN/LOCODE |
| MODE_ID | Foreign key to DIM_TRANSPORT_MODE | VARCHAR(10) | No | Must exist in DIM_TRANSPORT_MODE |
| INCOTERM_CODE | Incoterms 2020 rule (3-letter code) | CHAR(3) | No | Must be in (EXW,FCA,CPT,CIP,DAP,DPU,DDP,FAS,FOB,CFR,CIF) |
| PLANNED_DEP_DATE | Contractual planned departure date | DATE | No | Must be <= PLANNED_ARR_DATE |
| PLANNED_ARR_DATE | Contractual planned arrival / ETA at destination | DATE | No | Must be >= PLANNED_DEP_DATE |
| ACTUAL_DEP_DATE | Actual gate-out / departure date | DATE | Yes | If populated: >= PLANNED_DEP_DATE - 3 days (early departures flagged) |
| ACTUAL_ARR_DATE | Actual delivery / arrival confirmed date | DATE | Yes | NULL = shipment still in transit; if populated: >= ACTUAL_DEP_DATE |
| GROSS_WEIGHT_KG | Total gross weight of shipment in kilograms | DECIMAL(12,3) | No | > 0; <= physical transport mode capacity |
| VOLUME_CBM | Total volume in cubic metres | DECIMAL(10,3) | Yes | > 0 if populated |
| DISTANCE_KM | Great-circle or routed distance in kilometres | DECIMAL(10,1) | Yes | > 0; geocoding fill for NULL values |
| FREIGHT_COST_GC | Total freight cost in group currency (EUR) | DECIMAL(14,2) | Yes | >= 0; NULL only for pre-settlement orders |
| PO_NUMBER | Related purchase order number | VARCHAR(20) | Yes | Resolves to active PO in SAP MM |
| TRACKING_NUMBER | Carrier tracking reference (B/L, AWB, CMR) | VARCHAR(50) | Yes | Must be unique per carrier |
| SHIPMENT_STATUS | Current status of the transportation order | VARCHAR(20) | No | In (PLANNED, IN_TRANSIT, CUSTOMS_HOLD, DELIVERED, CANCELLED) |
| IS_ON_TIME | Delivery on or before PLANNED_ARR_DATE | BIT | Yes | Calculated: ACTUAL_ARR_DATE <= PLANNED_ARR_DATE |
| IS_IN_FULL | Delivered quantity equals ordered quantity | BIT | Yes | Calculated from DESADV vs. GR quantity |
| DATE_KEY | Foreign key to DIM_DATE (planned arrival date) | INT | No | Standard YYYYMMDD integer key |

### FACT_FREIGHT_INVOICE

| Field | Description | Type | Nullable | Validation |
|-------|-------------|------|----------|------------|
| FSD_ID | Freight settlement document ID (PK) | VARCHAR(20) | No | Unique |
| TOR_ID | Parent transportation order | VARCHAR(20) | No | FK to FACT_SHIPMENT |
| CARRIER_ID | Carrier billing the invoice | VARCHAR(10) | No | FK to DIM_CARRIER |
| INVOICE_NUMBER | Carrier invoice reference number | VARCHAR(30) | No | Unique per carrier |
| INVOICE_DATE | Date of carrier invoice | DATE | No | <= today |
| QUOTED_RATE_GC | Agreed contracted or quoted rate (EUR) | DECIMAL(14,2) | Yes | > 0 for contracted carriers |
| ACTUAL_INVOICE_GC | Actual invoiced amount (EUR) | DECIMAL(14,2) | No | > 0 |
| SURCHARGE_AMOUNT_GC | Total surcharges billed (BAF, CAF, PSS, etc.) | DECIMAL(14,2) | Yes | >= 0 |
| RATE_VARIANCE_PCT | (ACTUAL_INVOICE_GC - QUOTED_RATE_GC) / QUOTED_RATE_GC | DECIMAL(8,4) | Yes | Calculated field |
| SETTLEMENT_STATUS | Invoice processing status | VARCHAR(20) | No | In (PENDING, APPROVED, DISPUTED, PAID) |
| DISPUTE_FLAG | Invoice sent to dispute workflow | BIT | No | Default 0 |
| DISPUTE_REASON | Reason code for dispute | VARCHAR(100) | Yes | Required when DISPUTE_FLAG = 1 |

### FACT_CUSTOMS_DECLARATION

| Field | Description | Type | Nullable | Validation |
|-------|-------------|------|----------|------------|
| CUSTOMS_DECL_ID | Customs declaration unique ID (PK) | VARCHAR(20) | No | Unique |
| TOR_ID | Parent transportation order | VARCHAR(20) | No | FK to FACT_SHIPMENT |
| HS_CODE | Harmonised System commodity code | VARCHAR(10) | No | Minimum 8 digits; 10 digits for US HTS |
| COUNTRY_OF_ORIGIN | ISO 3166-1 alpha-2 country code | CHAR(2) | No | Valid ISO country code |
| COUNTRY_OF_IMPORT | ISO 3166-1 alpha-2 country code | CHAR(2) | No | Valid ISO country code |
| CUSTOMS_VALUE_GC | CIF customs value in group currency (EUR) | DECIMAL(14,2) | No | > 0 |
| DUTY_AMOUNT_GC | Total duty assessed (EUR) | DECIMAL(14,2) | No | >= 0 |
| CUSTOMS_ENTRY_DATE | Date customs declaration filed | DATE | No | <= today |
| RELEASE_DATE | Date goods released by customs authority | DATE | Yes | NULL = pending; >= CUSTOMS_ENTRY_DATE if populated |
| CLEARANCE_DAYS | RELEASE_DATE - CUSTOMS_ENTRY_DATE | INT | Yes | >= 0; calculated |
| BROKER_ID | Customs broker identifier | VARCHAR(10) | No | FK to ref.CUSTOMS_BROKER_MASTER |
| COMPLIANCE_RISK_SCORE | Composite risk score 0–100 | DECIMAL(5,2) | Yes | Calculated; see Section 11 |
| UFLPA_FLAG | Supplier has XUAR operations flag | BIT | No | Default 0 |
| DENIED_PARTY_HIT | Screening match against denied party lists | BIT | No | Default 0 |

### FACT_SHIPMENT_CO2

| Field | Description | Type | Nullable | Validation |
|-------|-------------|------|----------|------------|
| CO2_RECORD_ID | Surrogate primary key | BIGINT | No | Auto-increment |
| TOR_ID | Parent transportation order | VARCHAR(20) | No | FK to FACT_SHIPMENT |
| LEG_SEQUENCE | Leg number within multi-leg shipment | TINYINT | No | >= 1 |
| MODE_ID | Transport mode for this leg | VARCHAR(10) | No | FK to DIM_TRANSPORT_MODE |
| DISTANCE_KM | Distance of this leg in kilometres | DECIMAL(10,1) | No | > 0 |
| WEIGHT_KG | Cargo weight on this leg in kilograms | DECIMAL(12,3) | No | > 0 |
| LADEN_FACTOR | Load utilisation factor (0.4–1.0) | DECIMAL(4,3) | No | Between 0.4 and 1.0 |
| EMISSION_FACTOR_gCO2e_PER_TKM | GLEC factor for this mode and fuel type | DECIMAL(8,3) | No | > 0 |
| CO2e_KG | Calculated CO2 equivalent in kilograms | DECIMAL(12,3) | No | Calculated |
| GLEC_VERSION | GLEC Framework version used | VARCHAR(10) | No | e.g., '3.0' |
| CBAM_COVERED | Commodity is within EU CBAM scope | BIT | No | Default 0 |

---

## 8. Transformation Rules

### TR-01: OTD Flag Calculation

```sql
-- Applied in Azure SQL transformation layer
UPDATE FACT_SHIPMENT
SET IS_ON_TIME = CASE
    WHEN ACTUAL_ARR_DATE IS NULL THEN NULL  -- in transit; cannot determine yet
    WHEN ACTUAL_ARR_DATE <= PLANNED_ARR_DATE THEN 1
    ELSE 0
END;
```

### TR-02: OTIF Flag Calculation

OTIF requires both on-time AND in-full. The in-full determination joins DESADV line quantities
against SAP MM Goods Receipt quantities per PO line.

```sql
UPDATE FACT_SHIPMENT fs
SET IS_IN_FULL = CASE
    WHEN gr.RECEIVED_QTY >= (gr.ORDERED_QTY * 0.995) THEN 1  -- 99.5% tolerance
    ELSE 0
END
FROM FACT_SHIPMENT fs
JOIN stg.GR_QUANTITIES gr ON fs.TOR_ID = gr.TOR_ID;

UPDATE FACT_SHIPMENT
SET IS_OTIF = CASE
    WHEN IS_ON_TIME = 1 AND IS_IN_FULL = 1 THEN 1
    ELSE 0
END
WHERE ACTUAL_ARR_DATE IS NOT NULL;
```

### TR-03: Freight Cost per kg and per km

```sql
-- Applied as calculated columns in the Azure SQL analytical view
ALTER VIEW analytics.v_shipment_cost AS
SELECT
    TOR_ID,
    FREIGHT_COST_GC,
    GROSS_WEIGHT_KG,
    DISTANCE_KM,
    CASE WHEN GROSS_WEIGHT_KG > 0 THEN FREIGHT_COST_GC / GROSS_WEIGHT_KG ELSE NULL END AS COST_PER_KG,
    CASE WHEN DISTANCE_KM > 0 THEN FREIGHT_COST_GC / DISTANCE_KM ELSE NULL END AS COST_PER_KM,
    CASE WHEN GROSS_WEIGHT_KG > 0 AND DISTANCE_KM > 0
         THEN FREIGHT_COST_GC / (GROSS_WEIGHT_KG * DISTANCE_KM / 1000)
         ELSE NULL END AS COST_PER_TKM
FROM FACT_SHIPMENT
WHERE FREIGHT_COST_GC IS NOT NULL;
```

### TR-04: CO2 Calculation per Shipment Leg (GLEC Framework v3)

```sql
-- Applied in FACT_SHIPMENT_CO2 population procedure
INSERT INTO FACT_SHIPMENT_CO2 (TOR_ID, LEG_SEQUENCE, MODE_ID, DISTANCE_KM,
                                WEIGHT_KG, LADEN_FACTOR, EMISSION_FACTOR_gCO2e_PER_TKM,
                                CO2e_KG, GLEC_VERSION, CBAM_COVERED)
SELECT
    sl.TOR_ID,
    sl.LEG_SEQUENCE,
    sl.MODE_ID,
    sl.DISTANCE_KM,
    sl.WEIGHT_KG,
    ef.LADEN_FACTOR,
    ef.EMISSION_FACTOR_gCO2e_PER_TKM,
    -- CO2e_kg = Distance_km * (Weight_kg / 1000) * Laden_Factor * EmissionFactor_gCO2ePertKm / 1000
    (sl.DISTANCE_KM * (sl.WEIGHT_KG / 1000.0) * ef.LADEN_FACTOR
     * ef.EMISSION_FACTOR_gCO2e_PER_TKM / 1000.0) AS CO2e_KG,
    ef.GLEC_VERSION,
    CASE WHEN hs.CBAM_COVERED = 1 THEN 1 ELSE 0 END
FROM stg.SHIPMENT_LEGS sl
JOIN ref.GLEC_EMISSION_FACTORS ef
    ON sl.MODE_ID = ef.MODE
    AND sl.VESSEL_TYPE = ef.VESSEL_TYPE
    AND sl.FUEL_TYPE = ef.FUEL_TYPE
    AND sl.SHIPMENT_DATE BETWEEN ef.VALID_FROM AND ef.VALID_TO
JOIN FACT_CUSTOMS_DECLARATION cd ON sl.TOR_ID = cd.TOR_ID
JOIN ref.HS_CBAM_SCOPE hs ON LEFT(cd.HS_CODE, 4) = hs.HS4_CODE;
```

### TR-05: Freight Invoice Variance Calculation

```sql
UPDATE FACT_FREIGHT_INVOICE
SET
    RATE_VARIANCE_PCT = CASE
        WHEN QUOTED_RATE_GC IS NOT NULL AND QUOTED_RATE_GC > 0
        THEN (ACTUAL_INVOICE_GC - QUOTED_RATE_GC) / QUOTED_RATE_GC
        ELSE NULL
    END,
    DISPUTE_FLAG = CASE
        WHEN QUOTED_RATE_GC IS NOT NULL AND QUOTED_RATE_GC > 0
             AND ABS((ACTUAL_INVOICE_GC - QUOTED_RATE_GC) / QUOTED_RATE_GC) > 0.05
        THEN 1
        ELSE 0
    END;
```

### TR-06: Customs Clearance Lead Time

```sql
UPDATE FACT_CUSTOMS_DECLARATION
SET CLEARANCE_DAYS = DATEDIFF(DAY, CUSTOMS_ENTRY_DATE, RELEASE_DATE)
WHERE RELEASE_DATE IS NOT NULL;
```

### TR-07: Distance Geocoding Fill (for NULL DISTANCE_KM)

When DISTANCE_KM is NULL in SAP TM (typically for short-haul road movements), the
transformation applies a geocoded distance lookup based on origin and destination UN/LOCODE
coordinates stored in DIM_LOCATION, using the Haversine formula:

```python
# python/07_logistics/geocoding_fill.py
import math

def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate great-circle distance in km between two coordinates."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.asin(math.sqrt(a))
```

A road-distance correction factor of 1.25 is applied to Haversine distance for road mode
(to account for non-straight road routing); 1.10 for rail; 1.0 for ocean and air.

---

## 9. Business Rules

**BR-01: OTD Window**
A shipment is considered on-time if the actual arrival date is on or before the planned
arrival date. No grace period is applied by default. Where carrier contracts specify a
±1 day tolerance window, the CARRIER_OTD_TOLERANCE_DAYS field in DIM_CARRIER is used:
`IS_ON_TIME = ACTUAL_ARR_DATE <= PLANNED_ARR_DATE + CARRIER_OTD_TOLERANCE_DAYS`

**BR-02: Incoterms 2020 Compliance**
All INCOTERM_CODE values must be from the 11 valid Incoterms 2020 rules. The discontinued
DAT term (Incoterms 2010) must be migrated to DPU. Shipments with INCOTERM_CODE = 'DAT'
generate a data quality alert and are excluded from compliance reporting until corrected.

**BR-03: Freight Invoice Dispute Threshold**
An invoice is automatically flagged for dispute when the absolute variance between actual
invoiced amount and quoted rate exceeds 5% (±5%). The Finance and Logistics teams jointly
approve any variance above 10% before payment. Variances below 5% are auto-approved.

**BR-04: Carrier Tier Assignment**
Carrier tier is reviewed quarterly based on rolling 6-month OTD, OTIF, claims rate, and
documentation accuracy. Tier thresholds are defined in BR-09 (Carrier Scorecard section).
A carrier cannot move from DISQUALIFIED to APPROVED without a 90-day probation period at
WATCH tier with minimum 90% OTD demonstrated.

**BR-05: Customs Clearance SLA**
Country-specific clearance SLA targets are defined in ref.COUNTRY_CLEARANCE_SLA. Default
SLA: import declarations must be released within 3 business days. Shipments exceeding the
country SLA generate a customs delay alert to the Trade Compliance team and the relevant
logistics coordinator.

**BR-06: UFLPA Screening Mandatory**
All suppliers shipping goods that include raw materials, components, or finished goods from
the Xinjiang Uyghur Autonomous Region (XUAR) must have UFLPA clearance documentation
attached to the customs declaration. Shipments with UFLPA_FLAG = 1 and no clearance
document reference are blocked from GTS release.

**BR-07: CO2 Calculation Mandatory for Air Shipments**
All air freight shipments with FREIGHT_COST_GC > EUR 500 must have a CO2 calculation
record in FACT_SHIPMENT_CO2. Air shipments without a CO2 record are excluded from the
carrier sustainability scorecard and flagged in the ESG dashboard.

**BR-08: Modal Shift Justification**
Air freight used for non-emergency replenishment (i.e., where stock is not below reorder
point) requires a modal shift justification code entered in SAP TM. Valid codes:
EMERGENCY_STOCK, CUSTOMER_EXPEDITE, SUPPLIER_DELAY, QUALITY_REPLACEMENT, APPROVED_EXCEPTION.
Unjustified air shipments are reported to the Logistics Director monthly.

**BR-09: Carrier Scorecard Minimum Data**
A carrier scorecard record can only be generated when the carrier has completed a minimum
of 10 shipments in the scoring period. Carriers below this threshold are marked as
INSUFFICIENT_DATA and excluded from tier ranking calculations.

---

## 10. KPIs and Formulas

### KPI-01: On-Time Delivery (OTD) by Carrier

```
OTD (%) = (Shipments with ACTUAL_ARR_DATE <= PLANNED_ARR_DATE) / Total Completed Shipments × 100
```

World-class target: >= 95%
Minimum acceptable: >= 85% (triggers WATCH tier)
Below 75%: DISQUALIFIED tier

Segmentations: by Carrier, by Mode, by Trade Lane (Origin Country → Destination Country),
by Month, by Incoterm.

### KPI-02: On-Time In-Full (OTIF) by Carrier

```
OTIF (%) = Shipments where IS_ON_TIME = 1 AND IS_IN_FULL = 1 / Total Completed Shipments × 100
```

Walmart standard: >= 98% (for suppliers shipping to Walmart DCs)
Internal target: >= 94%

### KPI-03: Freight Cost per Kilogram

```
Cost per kg (EUR/kg) = Total Freight Cost GC / Total Gross Weight KG
```

Benchmarks by mode (illustrative — update with actual contracted benchmarks):
- Ocean FCL Europe–Asia: EUR 0.30–0.60 / kg
- Air Europe–Asia: EUR 3.50–6.00 / kg
- Road intra-Europe FTL: EUR 0.05–0.15 / kg

### KPI-04: Freight Cost per Kilometre

```
Cost per km (EUR/km) = Total Freight Cost GC / Total Distance KM
```

Used for cross-modal comparability on the same trade lane.

### KPI-05: Freight Cost per Tonne-Kilometre

```
Cost per tKm (EUR/tKm) = Total Freight Cost GC / (Total Weight Tonnes × Total Distance KM)
```

The tonne-kilometre metric enables true cross-modal cost comparison independent of shipment
size and distance.

### KPI-06: Modal Split Percentage

```
Modal Split % (by mode) = Shipments by Mode / Total Shipments × 100
Also calculated by: Freight Cost by Mode / Total Freight Cost × 100
And by: CO2e by Mode / Total CO2e × 100
```

Monitor air freight modal split: target < 15% of shipment volume (cost-based).

### KPI-07: Freight Invoice vs. Quote Variance

```
Rate Variance (%) = (Actual Invoice GC - Quoted Rate GC) / Quoted Rate GC × 100
```

Target: < ±5% for all contracted carriers
Alert threshold: > ±10% triggers automatic dispute flag

Aggregate: Total Overbilling EUR = SUM(MAX(0, ACTUAL_INVOICE_GC - QUOTED_RATE_GC * 1.05))

### KPI-08: Customs Clearance Lead Time

```
Clearance Days = RELEASE_DATE - CUSTOMS_ENTRY_DATE (calendar days)
```

SLA by import country (examples):
- EU countries: target <= 2 business days
- US (CBP entry): target <= 3 business days
- China: target <= 5 business days
- India: target <= 7 business days

KPI: % shipments meeting country clearance SLA = Shipments cleared within SLA / Total Import Shipments × 100

### KPI-09: CO2 per Shipment (GLEC Framework v3)

```
CO2e per shipment (kg) = SUM over all legs of:
    Distance_km × (Weight_kg / 1000) × Laden_Factor × EmissionFactor_gCO2ePertKm / 1000

CO2e intensity (gCO2e/tKm) = Total_CO2e_kg × 1000 / (Total_Weight_Tonnes × Total_Distance_km)
```

GLEC emission factors (illustrative, from GLEC v3 Table A1):
- Ocean Container (HFO): 10–12 gCO2e/tKm (laden factor 0.7)
- Air freight (kerosene): 500–600 gCO2e/tKm (laden factor 0.7)
- Road FTL (diesel Euro VI): 80–100 gCO2e/tKm (laden factor 0.7)
- Rail electric (EU grid): 25–35 gCO2e/tKm (laden factor 0.7)

### KPI-10: Carrier Claims Rate

```
Claims Rate (%) = Shipments with Cargo Claim Filed / Total Completed Shipments × 100
Claims Value Rate (%) = Total Open Claims Value GC / Total Freight Cost GC × 100
```

Target: < 0.5% shipment claims rate
Critical: > 2% triggers WATCH tier escalation

### KPI-11: Documentation Accuracy Rate

```
Doc Accuracy (%) = Shipments with Zero Documentation Errors / Total Shipments × 100
```

Documentation errors include: incorrect HS code, missing certificate of origin, incorrect
commercial invoice value, missing packing list, incorrect Incoterm.

### KPI-12: Carrier Sustainability Score

Weighted composite of:
- CO2e intensity vs. fleet average: 40%
- ISO 14001 certification: 20%
- Biofuel / low-carbon fuel usage: 20%
- Clean Cargo / SmartWay membership: 20%

---

## 11. Analytical Logic

### Carrier Tier Classification

Carrier tier is computed quarterly using the following multi-dimensional scoring model.
Each dimension is scored 0–100 and the weighted composite determines tier.

| Dimension | Weight | Metric | Source |
|-----------|--------|--------|--------|
| OTD | 35% | % shipments on-time (rolling 6 months) | FACT_SHIPMENT |
| OTIF | 20% | % shipments on-time and in-full | FACT_SHIPMENT |
| Claims Rate | 15% | 1 - (claims/shipments) × 100 | FACT_CARGO_CLAIMS |
| Invoice Accuracy | 15% | % invoices within ±5% of quoted rate | FACT_FREIGHT_INVOICE |
| Documentation Accuracy | 10% | % shipments with zero doc errors | FACT_SHIPMENT |
| Sustainability | 5% | CO2e intensity vs. mode average | FACT_SHIPMENT_CO2 |

**Tier Thresholds:**

| Tier | Composite Score | Action |
|------|----------------|--------|
| PREFERRED | >= 90 | Annual contract renewal preferred; priority allocation |
| APPROVED | 75–89 | Standard carrier; eligible for tenders |
| WATCH | 60–74 | Quarterly review required; no new volume allocation |
| DISQUALIFIED | < 60 | No new bookings; existing shipments completed then suspended |

### Lane Risk Scoring

Each trade lane (Origin Country → Destination Country → Mode) receives a risk score
calculated monthly from:

```
Lane Risk Score = (0.30 × Customs_Delay_Risk) + (0.25 × Port_Congestion_Index)
                + (0.20 × Geopolitical_Risk_Score) + (0.15 × UFLPA_Supplier_Exposure)
                + (0.10 × Hazmat_Complexity)
```

- **Customs Delay Risk**: Avg clearance days / Country SLA target (normalised 0–100)
- **Port Congestion Index**: Average dwell time at origin and destination port vs. baseline
- **Geopolitical Risk Score**: Derived from OECD country risk classification (0–7 scale)
- **UFLPA Supplier Exposure**: % of shipments on this lane with UFLPA_FLAG = 1
- **Hazmat Complexity**: % of shipments requiring IMDG/ADR/IATA DGR documentation

Risk tiers: LOW (0–30), MEDIUM (31–60), HIGH (61–80), CRITICAL (> 80)

### Alert Triggers

| Alert | Trigger Condition | Recipient | Escalation |
|-------|-------------------|-----------|------------|
| Shipment Late Alert | IN_TRANSIT and current date > PLANNED_ARR_DATE | Logistics Coordinator | +2 days: Logistics Manager |
| Carrier OTD Alert | Carrier rolling 30-day OTD drops below 85% | Category Manager | If persistent 60 days: Director |
| Invoice Dispute Alert | RATE_VARIANCE_PCT > 5% | Freight Audit Team | > 10%: Finance Controller |
| Customs Hold Alert | Shipment in CUSTOMS_HOLD > country SLA days | Trade Compliance | +2 days over SLA: VP Supply Chain |
| CO2 Air Alert | Air shipment without modal shift justification code | Logistics Planner | Monthly report to Director |
| UFLPA Alert | UFLPA_FLAG = 1 and no clearance document | Trade Compliance | Immediate: Legal |
| High Cost Lane Alert | Cost per tKm > 2× mode average for that lane | Category Manager | Quarterly review |

### Segmentation Framework

Delivery performance and cost analytics are segmented across six dimensions:
1. **Carrier dimension**: Individual carrier, carrier group, carrier tier
2. **Mode dimension**: Ocean FCL, Ocean LCL, Air, Road FTL, Road LTL, Rail, Parcel
3. **Geography dimension**: Origin country, destination country, trade lane, region
4. **Time dimension**: Day, week, month, quarter, fiscal year, rolling 12 months
5. **Product dimension**: Business unit, product category, HS chapter
6. **Incoterm dimension**: 11 Incoterms 2020 rules grouped by risk transfer point

---

## 12. Validations and Controls

### Data Quality Controls

| Control ID | Control Description | Severity | Action |
|------------|---------------------|----------|--------|
| DQC-01 | TOR_ID unique in FACT_SHIPMENT | Critical | Block load; alert data steward |
| DQC-02 | ACTUAL_ARR_DATE >= ACTUAL_DEP_DATE | Critical | Reject record; quarantine to error table |
| DQC-03 | FREIGHT_COST_GC = NULL only for unsettled orders | High | Flag for settlement review |
| DQC-04 | INCOTERM_CODE in valid Incoterms 2020 list | High | Reject; alert trade compliance |
| DQC-05 | CARRIER_ID resolves to active carrier in DIM_CARRIER | High | Reject; map to unknown carrier placeholder |
| DQC-06 | HS_CODE minimum 8 digits | High | Reject customs record; alert broker |
| DQC-07 | GROSS_WEIGHT_KG > 0 | Medium | Warn; use estimated weight from DESADV |
| DQC-08 | DISTANCE_KM > 0 (geocoding fill applied) | Medium | Fill with geocoded estimate; log fill |
| DQC-09 | EMISSION_FACTOR joined on date range — no gap | High | Alert ESG team; hold CO2 record |
| DQC-10 | Carrier has >= 10 shipments before scorecard calc | Low | Mark as INSUFFICIENT_DATA |

### Reconciliation Controls

- Daily reconciliation: Count of TOR records in Azure SQL vs. SAP TM report S_ALR_87013570.
  Tolerance: zero unmatched records.
- Weekly reconciliation: Total FREIGHT_COST_GC in FACT_FREIGHT_INVOICE vs. SAP FI cost
  centre report. Tolerance: < EUR 500 rounding difference.
- Monthly reconciliation: Total CO2e_KG per business unit reconciled against ESG team's
  independent calculation. Tolerance: < 1% variance.

---

## 13. Required Evidence

| Evidence Item | Description | Owner | Required By |
|---------------|-------------|-------|-------------|
| EV-01 | SAP TM transportation order field mapping | SAP Basis / TM Consultant | Implementation Phase 1 |
| EV-02 | SAP GTS customs declaration field mapping | Trade Compliance / GTS Consultant | Phase 1 |
| EV-03 | Carrier SCAC code master extract | Logistics Operations | Phase 1 |
| EV-04 | Approved Incoterms 2020 configuration in SAP | Trade Compliance | Phase 1 |
| EV-05 | GLEC Framework v3 emission factors — selected table | ESG / Sustainability Team | Phase 1 |
| EV-06 | Country clearance SLA targets signed off by Trade Compliance | Trade Compliance Manager | Phase 2 |
| EV-07 | Carrier contract rate cards (all active carriers) | Logistics Category Manager | Phase 2 |
| EV-08 | UFLPA supplier list — XUAR exposure mapping | Compliance Officer | Phase 1 |
| EV-09 | EDI DESADV message specification per supplier | EDI Operations | Phase 2 |
| EV-10 | Power BI workspace and Azure SQL connection approved | IT Security | Phase 1 |
| EV-11 | HS code to CBAM commodity mapping table | Trade Compliance | Phase 3 |
| EV-12 | Cargo claims data extract from insurance system | Risk Management | Phase 3 |

---

## 14. Dashboard Design

### Dashboard 1: Executive Logistics KPI Summary

**Audience**: VP Supply Chain, Logistics Director, CFO
**Refresh**: Daily at 07:00 local time
**Layout**: Single-page executive summary

Key visuals:
- KPI cards: OTD %, OTIF %, Freight Cost vs. Budget, CO2e YTD
- OTD trend line chart: rolling 12 months, with target reference line at 95%
- Freight cost variance waterfall: budget vs. actual by mode
- Top 5 late carriers: table with OTD%, shipment count, financial impact
- Modal split donut chart: by shipment count and by freight cost
- World map: delivery performance heatmap by destination country

### Dashboard 2: Carrier Performance Scorecard

**Audience**: Logistics Category Manager, Procurement Director
**Refresh**: Weekly (Mondays 08:00)

Key visuals:
- Carrier tier matrix: bubble chart (OTD% vs. OTIF%, sized by volume)
- Carrier scorecard table: all active carriers with composite score, tier, trend vs. prior quarter
- OTD trend by carrier: small multiples line chart, top 20 carriers
- Invoice accuracy by carrier: clustered bar chart
- Carrier performance vs. contract target: heatmap (green/amber/red)

### Dashboard 3: Freight Cost Analysis

**Audience**: Logistics Controller, Category Manager
**Refresh**: Daily

Key visuals:
- Cost per kg by mode: bar chart with budget and prior year reference lines
- Cost per tKm by trade lane: ranked bar chart
- Freight invoice variance: scatter plot (shipment count vs. average variance %)
- Budget vs. actual by trade lane: table with traffic light RAG status
- Air vs. ocean cost premium by lane: comparison table with modal shift opportunity value
- Disputed invoice aging: stacked bar by dispute age bucket (< 30d, 30-60d, > 60d)

### Dashboard 4: Customs & Compliance Risk

**Audience**: Trade Compliance Manager, Customs Broker Manager
**Refresh**: Daily

Key visuals:
- Shipments in customs hold: live count with average hold days
- Clearance lead time by country: box plot
- Compliance risk score distribution: histogram
- UFLPA flagged shipments: table with supplier, HS code, clearance status
- Denied party screening hits: alert panel (red badge count)
- HS code mismatch alerts: ranked by financial exposure

### Dashboard 5: Carbon Footprint

**Audience**: ESG Team, Sustainability Director, Finance (CBAM reporting)
**Refresh**: Monthly (1st business day)

Key visuals:
- CO2e YTD by mode: stacked bar chart
- CO2e intensity (gCO2e/tKm) by carrier: ranking bar chart vs. mode average
- CBAM-covered shipment CO2 content: table by commodity and origin country
- Modal shift opportunity: air lanes where ocean viable — CO2 saving potential
- CO2e trend: rolling 12-month line chart vs. science-based target trajectory
- Carrier sustainability tier: table with ISO 14001 status, Clean Cargo membership

---

## 15. Use Cases

### UC-01: Monthly Carrier Business Review Preparation

**User**: Logistics Category Manager
**Trigger**: First week of each month
**Process**:
1. Export carrier scorecard from Dashboard 2 for carriers with composite score < 80
2. Pull OTD root-cause analysis: late shipments breakdown (carrier fault vs. port/customs delay)
3. Review freight invoice disputes outstanding > 30 days
4. Prepare QBR slide deck with trend data and contractual penalty calculation
5. Send carrier performance letter to WATCH and DISQUALIFIED carriers

**Analytical Output**: Carrier scorecard PDF, root-cause pareto, financial exposure from late deliveries

### UC-02: Annual Freight RFP Lane Analysis

**User**: Logistics Category Manager, Procurement Director
**Trigger**: Q3 annually (RFP preparation for next fiscal year)
**Process**:
1. Extract 12-month lane volume: shipment count, weight, cost per tKm by lane
2. Identify top 50 lanes by freight spend (Pareto)
3. Benchmark current rate vs. spot market rate (Xeneta / Freightos data integration)
4. Model modal shift scenarios: air to ocean on qualifying lanes
5. Prepare RFP volume data packages per lane cluster

### UC-03: Customs Delay Root Cause Investigation

**User**: Trade Compliance Manager
**Trigger**: Country clearance SLA breach alert
**Process**:
1. Filter FACT_CUSTOMS_DECLARATION by CLEARANCE_DAYS > country SLA
2. Group by BROKER_ID, DELAY_REASON_CODE, HS_CODE chapter
3. Identify systemic patterns (e.g., specific broker repeatedly missing deadlines,
   specific HS chapters with valuation disputes)
4. Escalate to broker or initiate pre-clearance process improvement

### UC-04: CBAM Monthly CO2 Reporting

**User**: ESG Analytics Team, Finance (Tax & Trade)
**Trigger**: Monthly, by 10th working day
**Process**:
1. Extract FACT_SHIPMENT_CO2 filtered by CBAM_COVERED = 1 for prior month
2. Aggregate CO2e_KG by HS_CODE (4-digit chapter), COUNTRY_OF_ORIGIN
3. Reconcile against customs entry values in FACT_CUSTOMS_DECLARATION
4. Produce CBAM declarant report in EU registry format
5. Archive report with version-controlled emission factors used

### UC-05: Emergency Air Freight Justification Audit

**User**: Logistics Director, Finance Controller
**Trigger**: Monthly, or triggered when air freight spend > budget by > 15%
**Process**:
1. Extract all air shipments in period with MODAL_SHIFT_JUSTIFICATION_CODE
2. Identify shipments without a valid justification code (BR-08 violation)
3. For justified air shipments: verify that stock position at destination justified expedite
4. Calculate the ocean-equivalent cost and quantify the premium paid
5. Report to VP Supply Chain with breakdown by business unit and product category

---

## 16. Recommended Actions

### RA-01: Carrier Consolidation on Low-Volume Lanes

Analyse lanes where three or more carriers are used with < 10 shipments per carrier per
quarter. Consolidate to one or two preferred carriers per lane to improve negotiating power,
increase volume commitments, and improve carrier accountability. Expected benefit: 5–8%
freight cost reduction on consolidated lanes.

### RA-02: Modal Shift Programme (Air to Ocean)

Identify the top 20 air lanes where the lead time difference between air and ocean is within
customer or production planning tolerance. Build a business case for each lane showing
CO2 reduction, cost saving, and required safety stock increase. Present to Supply Chain
Director for approval. Target: reduce air freight share from current level to < 15% of
freight cost within 24 months.

### RA-03: Carrier EDI Onboarding for IFTSTA

Carriers without EDI IFTSTA feeds (particularly on LATAM and Africa lanes) should be
prioritised for EDI onboarding or connection via a freight visibility platform (project44
or FourKites). Without real-time events, OTD can only be measured at final delivery,
preventing proactive exception management. Target: 95% EDI coverage within 12 months.

### RA-04: Freight Invoice Audit Automation

Implement automated freight audit rules in SAP TM Freight Settlement to flag invoices
exceeding the ±5% tolerance before payment. Current manual audit process catches only
60% of billing errors. Automation target: 100% invoice coverage, < 48-hour dispute
resolution cycle. Estimated annual recovery: EUR 150k–300k based on industry benchmarks.

### RA-05: UFLPA Pre-Clearance Documentation Process

Suppliers with XUAR_FLAG = 1 should be required to submit UFLPA clearance packages
(supply chain mapping, forced labour audit certificates, import certifications) 30 days
before shipment arrival. Current process is reactive (documentation collected after
customs hold). Pre-clearance process will reduce UFLPA-related customs hold time
from average 14 days to < 3 days.

### RA-06: CO2 Intensity Target by Carrier Mode

Establish CO2e intensity targets per transport mode aligned with Science Based Targets
initiative (SBTi) FLAG pathway. Incorporate CO2e intensity (gCO2e/tKm) as a 5% weighted
factor in carrier scorecard (already built into scoring model). Publish carrier CO2
rankings in annual ESG report.

---

## 17. Test Cases

### TC-01: OTD Calculation Accuracy

**Scenario**: 100 shipments; 80 arrive on or before planned date; 15 arrive 1 day late;
5 arrive 2+ days late.
**Expected OTD**: 80 / 100 = 80.0%
**Test Method**: Insert synthetic records into FACT_SHIPMENT; execute OTD measure;
verify Power BI KPI card displays 80.0%.
**Pass Criteria**: OTD = 80.0% ± 0.1%; late shipments appear in drill-through.

### TC-02: CO2 Calculation Accuracy

**Scenario**: Ocean FCL shipment, 10,000 kg, 18,000 km, laden factor 0.7,
emission factor 10.0 gCO2e/tKm.
**Expected CO2e**: 18,000 × (10,000/1,000) × 0.7 × 10.0 / 1,000 = 1,260 kg CO2e
**Test Method**: Insert record into FACT_SHIPMENT_CO2 with above parameters;
verify CO2e_KG = 1,260.0.
**Pass Criteria**: CO2e_KG = 1,260.0 ± 0.1.

### TC-03: Freight Invoice Dispute Auto-Flag

**Scenario**: Quoted rate EUR 5,000; actual invoice EUR 5,350 (7% over).
**Expected**: DISPUTE_FLAG = 1; RATE_VARIANCE_PCT = 0.07.
**Test Method**: Insert freight invoice record; run transformation TR-05;
verify DISPUTE_FLAG and RATE_VARIANCE_PCT.
**Pass Criteria**: DISPUTE_FLAG = 1; RATE_VARIANCE_PCT = 0.0700 ± 0.0001.

### TC-04: Carrier Tier Assignment

**Scenario**: Carrier with OTD = 92%, OTIF = 88%, claims rate = 0.3%,
invoice accuracy = 96%, doc accuracy = 98%, sustainability = 75.
**Composite**: (0.35×92) + (0.20×88) + (0.15×97) + (0.15×96) + (0.10×98) + (0.05×75)
= 32.2 + 17.6 + 14.55 + 14.4 + 9.8 + 3.75 = 92.3 → PREFERRED
**Pass Criteria**: Carrier tier = PREFERRED in quarterly scorecard output.

### TC-05: UFLPA Block Validation

**Scenario**: Customs declaration with UFLPA_FLAG = 1 and no CLEARANCE_DOCUMENT_REF.
**Expected**: COMPLIANCE_RISK_SCORE = 100 (maximum); alert generated; GTS release blocked.
**Pass Criteria**: Alert record exists in alert log; GTS release status = BLOCKED.

### TC-06: Null ACTUAL_ARR_DATE Handling

**Scenario**: Shipment with ACTUAL_ARR_DATE = NULL (in transit).
**Expected**: IS_ON_TIME = NULL; shipment appears in "In Transit" view; not counted in OTD denominator.
**Pass Criteria**: OTD denominator excludes in-transit shipments; IS_ON_TIME = NULL.

### TC-07: Incoterm Validation

**Scenario**: Shipment with INCOTERM_CODE = 'DAT' (deprecated Incoterms 2010 term).
**Expected**: DQC-04 fires; record rejected; alert sent to trade compliance.
**Pass Criteria**: Record in error table with DQC_04 error code; not in FACT_SHIPMENT.

---

## 18. Risks and Mitigations

| Risk ID | Risk Description | Likelihood | Impact | Mitigation |
|---------|-----------------|------------|--------|------------|
| R-01 | SAP TM DISTANCE_KM field sparsely populated for road shipments | High | Medium | Geocoding fill algorithm (TR-07); track fill rate monthly |
| R-02 | Carriers without EDI IFTSTA — OTD only measurable at final delivery | High | High | Manual milestone upload portal for non-EDI carriers; EDI onboarding roadmap |
| R-03 | GLEC emission factors not updated annually by ESG team | Medium | Medium | Change management process; annual review task in ESG calendar |
| R-04 | SAP GTS RELEASE_DATE not populated for informal entries | Medium | Medium | Exclude de minimis entries from KPI; document exclusion in methodology |
| R-05 | Carrier SCAC code inconsistency between SAP TM and EDI messages | High | High | SCAC alias mapping table maintained by EDI Operations; automated reconciliation |
| R-06 | UFLPA supplier list not kept current | High | Critical | Monthly refresh from compliance database; blocking rule in SAP GTS |
| R-07 | Air freight modal shift justification codes not used by logistics planners | Medium | Medium | Mandatory field in SAP TM booking workflow; training; monthly exception report |
| R-08 | CO2 calculation methodology challenged in CBAM audit | Low | High | GLEC certification; full audit trail of emission factors and versions used |
| R-09 | Power BI DirectQuery performance on large FACT_SHIPMENT table | Medium | Medium | Partitioning by year-month; pre-aggregated summary tables for executive views |
| R-10 | Currency conversion errors in multi-currency freight invoices | Medium | High | Daily FX rates from ECB; all costs converted to EUR at invoice date rate |

---

## 19. Implementation Checklist

### Phase 1: Data Foundation (Weeks 1–8)

- [ ] SAP TM field mapping document completed and signed off
- [ ] SAP GTS customs declaration field mapping completed
- [ ] Azure SQL database schemas created (FACT, DIM, stg, ref tables)
- [ ] Carrier master extract loaded into DIM_CARRIER
- [ ] DIM_LOCATION populated with UN/LOCODE and geocoordinates
- [ ] GLEC emission factor reference table loaded (ref.GLEC_EMISSION_FACTORS)
- [ ] Country clearance SLA targets loaded (ref.COUNTRY_CLEARANCE_SLA)
- [ ] HS code CBAM scope table loaded (ref.HS_CBAM_SCOPE)
- [ ] EDI DESADV staging table created and tested with 3 pilot suppliers
- [ ] EDI IFTSTA staging table created and tested with 3 pilot carriers
- [ ] UFLPA supplier flag data loaded from compliance database
- [ ] SAP TM → Azure SQL ETL pipeline deployed (initial load)

### Phase 2: KPI Layer (Weeks 9–16)

- [ ] Transformation TR-01 through TR-07 implemented and unit-tested
- [ ] OTD, OTIF calculated and reconciled against SAP TM standard reports
- [ ] CO2 calculation validated against manual GLEC calculation for 10 sample shipments
- [ ] Freight invoice variance calculation tested (TC-03 pass)
- [ ] Customs clearance lead time calculation validated against GTS
- [ ] UFLPA block logic validated (TC-05 pass)
- [ ] Alert engine deployed for all 7 alert trigger conditions
- [ ] Power BI data model connected and relationships validated
- [ ] All 5 dashboards built and reviewed by business users

### Phase 3: Carrier Scorecard and Lane Risk (Weeks 17–22)

- [ ] Carrier scorecard model implemented and back-tested on 6 months of history
- [ ] Carrier tier assignments reviewed and approved by Category Manager
- [ ] Lane risk scoring model implemented and calibrated
- [ ] QBR reporting pack template built in Power BI
- [ ] Training delivered to Logistics team (8 hours)
- [ ] User acceptance testing completed with sign-off from Logistics Director

---

## 20. Validation Checklist

- [ ] OTD calculation matches SAP TM standard OTD report within ±0.5 percentage points
- [ ] Total freight cost in analytics layer matches SAP FI cost centre report within EUR 500
- [ ] CO2e per shipment for 10 test cases matches manual GLEC calculation within 1%
- [ ] Customs clearance lead time distribution matches GTS aging report
- [ ] Carrier tier assignments reviewed and confirmed by Category Manager for all PREFERRED carriers
- [ ] All 7 alert triggers tested and confirmed firing correctly in test environment
- [ ] UFLPA block validated: blocked shipments do not appear in approved shipment list
- [ ] Dashboard refresh SLA met: daily dashboards updated by 07:00 on next business day
- [ ] Data retention policy confirmed: 7 years for customs records, 5 years for freight invoices
- [ ] GDPR/data privacy review completed for any PII in shipment records

---

## 21. Pending Information

| Item ID | Information Required | From Whom | Impact if Missing | Target Date |
|---------|---------------------|-----------|-------------------|-------------|
| PI-01 | Complete carrier rate card extract for all 40 countries | Logistics Category Manager | Cannot compute invoice variance for spot carriers | Week 3 |
| PI-02 | Confirmation of GLEC v3 emission factor selection for ocean HFO vs. LNG carriers | ESG Team | CO2 calculation will use default factors pending confirmation | Week 4 |
| PI-03 | Country clearance SLA targets for LATAM and Africa regions | Trade Compliance Manager | Default 5-day SLA applied; alerts may be inaccurate | Week 6 |
| PI-04 | EDI partner agreement list — carriers not yet onboarded | EDI Operations | Manual upload required for non-EDI carriers | Week 2 |
| PI-05 | CBAM-covered HS code mapping for company's product portfolio | Trade Compliance / Finance | CBAM reporting scope incomplete | Week 8 |
| PI-06 | Cargo claims data source — insurance system API or manual extract | Risk Management | Claims rate KPI unavailable until resolved | Week 10 |
| PI-07 | Geopolitical risk score source for lane risk model | SCM Risk Team | Lane risk model incomplete; country risk defaults applied | Week 12 |
| PI-08 | Confirmation of Power BI Premium workspace allocation | IT | Dashboard publishing blocked | Week 1 |

---

## 22. Implementation Roadmap

### Phase 1: Data Foundation and Infrastructure (Months 1–2)

**Objective**: Establish all data pipelines, master data, and reference tables.

Week 1–2: Environment setup — Azure SQL provisioning, Power BI workspace, ETL tooling
Week 3–4: SAP TM and SAP GTS extraction development and initial load
Week 5–6: EDI DESADV and IFTSTA staging pipelines; carrier master and location master loaded
Week 7–8: Reference tables loaded (GLEC, country SLA, CBAM scope, UFLPA supplier list)

**Milestone**: Full historical load of 24 months of shipment data in Azure SQL validated.

### Phase 2: KPI Implementation and Analytics Layer (Months 3–4)

**Objective**: Implement all transformation rules and KPI calculations; validate against source systems.

Week 9–10: Transformation rules TR-01 through TR-05 developed and tested
Week 11–12: CO2 calculation (TR-04) validated; customs lead time calculated (TR-06)
Week 13–14: Alert engine built and tested; Power BI data model connected
Week 15–16: All 5 dashboards built; initial UAT with 3 business users

**Milestone**: OTD, OTIF, Cost per kg, CO2, and Clearance Lead Time KPIs validated and signed off.

### Phase 3: Carrier Scorecard and Advanced Analytics (Months 5–6)

**Objective**: Deliver carrier scoring, lane risk model, and use case workflows.

Week 17–18: Carrier scorecard model implemented; tier assignments back-tested
Week 19–20: Lane risk scoring model; modal shift analysis tool
Week 21–22: Training delivery; UAT completion; production go-live
Week 23–24: Hypercare period; issue resolution; first monthly CBAM report produced

**Milestone**: Production go-live signed off by Logistics Director and Trade Compliance Manager.

### Phase 4: Continuous Improvement (Months 7–12)

**Objective**: Optimise, expand scope, and drive business outcomes.

Month 7–8: Freight invoice automation (RA-04 implementation); LATAM/Africa EDI onboarding
Month 9–10: Modal shift programme analysis (RA-02); carrier consolidation recommendations (RA-01)
Month 11–12: Annual carrier RFP lane analysis; first full-year OTD review; CO2 target setting

**Milestone**: 12-month OTD improvement of +4 percentage points vs. baseline; freight cost reduction of 8%.

---

## References

- ICC Incoterms® 2020 (International Chamber of Commerce, 2019)
- GLEC Framework for Logistics Emissions Accounting and Reporting, Version 3.0 (Smart Freight Centre, 2023)
- EU CBAM Regulation 2023/956 (Carbon Border Adjustment Mechanism)
- WCO Harmonised System Nomenclature 2022 (World Customs Organization)
- ISO 28000:2022 — Security and resilience — Supply chain security management systems
- SAP TM 9.6 Configuration Guide (SAP SE)
- SAP GTS 14.0 Customs Management Configuration Guide (SAP SE)
- UN/EDIFACT Message Type DESADV D.96A (United Nations)
- UN/EDIFACT Message Type IFTSTA D.00B (United Nations)
- SCOR Digital Standard — Deliver Process Category (ASCM, 2019)
- Chopra & Meindl, Supply Chain Management, 6th Ed. (Pearson, 2016), Chapter 14 — Transportation
- Christopher, M., Logistics and Supply Chain Management, 6th Ed. (FT Publishing, 2022)
- Smart Freight Centre, Clean Cargo Working Group (2024)
- US CBP UFLPA Entity List (updated quarterly)
- C-TPAT Program Requirements (US CBP, 2023)
