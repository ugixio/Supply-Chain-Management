# Regulatory & Standards Framework

## International Standards Implemented

### ISO 28000:2022 — Supply Chain Security Management
**Status**: Current (published 15 March 2022, replaces ISO 28000:2007)
**Scope**: Security management systems for ALL organisation types, any supply chain.
**Implementation in SCM system**:
- `Supplier.certifications` field tracks ISO 28000 certification per supplier
- `isCertificationValid()` function enforces expiry checking
- Security audit trails via `StockMovement` idempotency keys

### ISO 9001:2015 — Quality Management Systems
**Transition**: ISO 9001:2026 expected Sep–Nov 2026 (3-year transition)
**Key clauses implemented**:
- §8.4 — Control of externally provided processes (Supplier scorecard)
- §8.5.2 — Identification and traceability (lot/serial tracking in `InventoryItem`)
- §8.6 — Release of products (`InspectionRecord` disposition logic)
- §8.7 — Control of nonconforming outputs (NCR generation)
- §9.1.3 — Analysis and evaluation (`SupplierScorecard` KPIs)

### GS1 General Specifications v23.0
- **GTIN** (Global Trade Item Number): `InventoryItem.gtin` — 14-digit
- **GLN** (Global Location Number): `Warehouse.gln` — 13-digit
- **SSCC** (Serial Shipping Container Code): `ShipmentLine.sscc` — 18-digit
- **UOM codes**: `UOM` constants in `shared/types.ts`
- **Sunrise 2027**: System ready for GS1 Digital Link / QR code transition

### UN/EDIFACT message mapping
| EDIFACT Message | SCM Domain Object |
|----------------|-------------------|
| ORDERS | `PurchaseOrder` |
| ORDRSP | `PurchaseOrder` (supplier acknowledgement) |
| DESADV | `Shipment` (advance ship notice) |
| RECADV | `InspectionRecord` (goods receipt advice) |
| INVOIC | `CommercialMetrics` (invoice) |

### Incoterms® 2020 (ICC, effective 01 Jan 2020)
All 11 rules implemented in `INCOTERMS_2020` constant:
- DPU replaces DAT (key 2020 change — any place, not just terminals)
- Security costs now explicitly allocated to seller
- Applied in `PurchaseOrder.incoterm` and `Shipment.incoterm`

---

## International Laws & Regulations

### EU Corporate Sustainability Due Diligence Directive (CSDDD)
**Reference**: Directive (EU) 2024/1760, OJ L 2024/1760
**In force**: 25 July 2024 | **Transposition deadline**: 26 July 2026

| Phase | Date | EU Companies | Non-EU Turnover |
|-------|------|-------------|-----------------|
| 1 | 26 Jul 2027 | >5,000 employees + €1.5bn | >€1.5bn EU |
| 2 | 26 Jul 2028 | >3,000 employees + €900m | >€900m EU |
| 3 | 26 Jul 2029 | >1,000 employees + €450m | >€450m EU |

**Penalties**: Up to 5% of worldwide net annual turnover (Art.27)
**Document retention**: Minimum 5 years (Art.23) — enforced in `DueDiligenceRecord`
**Implementation**: `src/compliance/regulations/CSDDD.ts`

### German Supply Chain Act (LkSG — Lieferkettensorgfaltspflichtengesetz)
**In force**: 1 January 2023
**Scope**: Companies with ≥1,000 employees in Germany (from Jan 2024)
**Relationship to CSDDD**: LkSG compliance provides a head-start; CSDDD supersedes at EU level

### UK Modern Slavery Act 2015 — Section 54
**Threshold**: Companies with turnover ≥ £36m conducting business in UK
**Obligation**: Annual transparency statement — approved by board, signed by director
**Fields**: `Supplier.modernSlaveryStatements` tracks per financial year

### US Uyghur Forced Labor Prevention Act (UFLPA)
**Reference**: Pub.L. 117-78, signed 23 Dec 2021 | **Enforcement**: 21 Jun 2022
**Core**: Rebuttable presumption — ALL goods from Xinjiang (XUAR) deemed forced-labor-made
**No de minimis** — even trace XUAR content triggers presumption
**CBP deadline**: Importer has 30 days from detention notice to provide rebuttal evidence
**Implementation**: `src/compliance/regulations/UFLPA.ts`
**Risk assessment**: `assessUFLPARisk()` scores supply chain tier by tier

### EU REACH Regulation (EC) No 1907/2006
**Registration threshold**: >1 metric tonne/year per substance
**SVHC threshold**: >0.1% w/w in articles triggers communication (Art.33) + ECHA notification (Art.7)
**Candidate List**: Updated bi-annually by ECHA
**Implementation**: `src/compliance/regulations/REACH.ts`

### C-TPAT (US Customs-Trade Partnership Against Terrorism)
- Voluntary; CBP-managed; benefits: fewer inspections, expedited clearance
- Tracked in `Supplier.certifications` (type: `CTPAT`)
- `Shipment.aeoShipperCertified` flag triggers expedited customs lane

### AEO (Authorised Economic Operator) — EU
- AEO-C: Customs simplifications
- AEO-S: Security and safety
- Tracked in `Supplier.certifications`
- WTO TFA Art.7 — trusted trader benefits

### WTO Trade Facilitation Agreement (TFA)
**In force**: 22 February 2017
- Art.7 pre-arrival processing → `Shipment.exportDeclarationRef`
- Art.7 authorized operators → `Shipment.aeoShipperCertified`
- Art.10 formalities → `ShipmentLine.hsCode` (HS tariff classification)

### Basel Convention on Hazardous Wastes
**Applies when**: Shipping hazmat waste across borders
- Prior Informed Consent (PIC) → `ShipmentLine.hazmatClass` + documentation
- `CustomsDocument` type SDS covers safety data sheet requirement

### US Uniform Commercial Code (UCC) Article 2
- Quantity must be specified in enforceable contracts — enforced in `POLineItem.quantity`
- UCC §2-615 Force Majeure → map to `RiskItem` category GEOPOLITICAL/OPERATIONAL

---

## Frameworks & Methodologies

### SCOR Digital Standard (SCOR-DS) — ASCM 2019
Six process types: Plan → Source → Make → Deliver → Return → Enable
Mapped to SCM modules:
- **Plan**: `demand-planning/` + `risk/`
- **Source**: `procurement/`
- **Make**: (manufacturing ERP — out of scope)
- **Deliver**: `logistics/` + `warehouse/`
- **Return**: `inventory/domain/StockMovement` (RETURN_FROM_CUSTOMER)
- **Enable**: `compliance/` + `supplier-management/`

### APICS CPIM 9.0 (2026 edition)
Key domains covered:
- Fundamentals of Demand Management → `Forecasting.ts`
- Inventory Management → `SafetyStock.ts`, `InventoryItem.ts`, ABC-XYZ matrix
- Plan Supply → `PurchaseOrder.ts`, EOQ
- Quality Management → `InspectionRecord.ts`, DPMO

### Gartner SCM Top 25 Methodology (2026)
ESG criteria (25% of ranking score) → tracked via:
- `CSDDDDueDiligence` on each supplier
- `UFLPARiskAssessment` for human rights compliance
- `REACHSubstance` for environmental compliance

### McKinsey Supply Chain Resilience Framework
Maturity levels: Basic → Managed → Advanced → Leading
- **Multi-tier visibility**: `UFLPARiskAssessment.supplyChainTiers`
- **Scenario planning**: `DisruptionScenario` + `expectedAnnualLoss()`
- **HHI concentration risk**: `herfindahlHirschmanIndex()`
- **Bullwhip effect monitoring**: `bullwhipRatio()`

---

## Key References

| Author(s) | Work | Year | Applied In |
|-----------|------|------|-----------|
| Chopra & Meindl | Supply Chain Management: Strategy, Planning, and Operation (6th Ed.) | 2016 | All modules |
| Ballou, R.H. | Business Logistics/Supply Chain Management (5th Ed.) | 2004 | Inventory, Logistics |
| Christopher, M. | Logistics and Supply Chain Management (6th Ed.) | 2022 | Logistics, Risk |
| Holt, C.C. | Forecasting seasonals and trends by exponentially weighted averages | 1957 | Forecasting.ts |
| Winters, P.R. | Forecasting sales by exponentially weighted moving averages | 1960 | holtWinters() |
| Harris, F.W. | How many parts to make at once (EOQ) | 1913 | economicOrderQuantity() |
| Kraljic, P. | Purchasing Must Become Supply Management (HBR) | 1983 | Supplier.ts Krajlic |
| Lee, Padmanabhan & Whang | The Bullwhip Effect in Supply Chains (MIT Sloan) | 1997 | RiskModel.ts |
| Silver, Pyke & Peterson | Inventory Management and Production Planning | 1998 | SafetyStock.ts |
| Vernon, V. | Implementing Domain-Driven Design | 2013 | events.ts, aggregates |
