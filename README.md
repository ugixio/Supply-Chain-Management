# Supply Chain Management System
## Enterprise SCM — SCOR-DS Aligned | ISO 28000:2022 | Incoterms® 2020

---

## Departmental Structure

The system is organized into **14 departments** that represent the complete
organizational structure of an enterprise supply chain.

```
src/departments/
├── 01-procurement/            # Procurement & Strategic Sourcing
├── 02-supplier-management/    # Supplier Management & Evaluation
├── 03-demand-planning/        # Demand Planning & Forecasting
├── 04-supply-planning/        # Supply Planning (MRP/MPS)
├── 05-inventory-management/   # Inventory Management (Event-Sourced)
├── 06-warehouse-management/   # Warehouse Management (WMS)
├── 07-logistics-transportation/ # Logistics & Transportation (TMS)
├── 08-quality-management/     # Quality Management (QMS / ISO 9001)
├── 09-compliance-regulatory/  # International Regulatory Compliance
├── 10-risk-management/        # SC Risk Management
├── 11-finance-controlling/    # SC Finance & Management Control
├── 12-sop-planning/           # S&OP / Integrated Business Planning
├── 13-order-management/       # Order Management (Order-to-Cash)
└── 14-supplier-development/   # Supplier Development & ESG Sustainability
```

---

## SCOR-DS Map → Departments

| SCOR Process | Departments |
|-------------|--------------|
| **Plan** | 03-demand-planning, 04-supply-planning, 12-sop-planning |
| **Source** | 01-procurement, 02-supplier-management, 14-supplier-development |
| **Make** | 04-supply-planning (MRP/MPS) |
| **Deliver** | 06-warehouse-management, 07-logistics-transportation, 13-order-management |
| **Return** | 05-inventory-management (RETURN_FROM_CUSTOMER) |
| **Enable** | 08-quality-management, 09-compliance-regulatory, 10-risk-management, 11-finance-controlling |

---

## Quick Start

```bash
npm install
npm run typecheck   # TypeScript validation
npm test            # All unit tests
npm run test:unit   # Unit tests only
npm run build       # Compile TypeScript
```

---

## Global Supply Chain KPIs

| KPI | World Benchmark | Owner Department |
|-----|------------------|-------------------|
| **OTIF** | ≥ 98% (Walmart) | 13-order-management |
| **OTD** | ≥ 95% | 07-logistics-transportation |
| **Perfect Order Rate** | ≥ 95% | 13-order-management |
| **Inventory Turnover** | ≥ 8-12× (FMCG) | 05-inventory-management |
| **Cash-to-Cash Cycle** | < 30 days | 11-finance-controlling |
| **Forecast MAPE** | < 15% (A items) | 03-demand-planning |
| **Supplier OTD** | ≥ 95% | 02-supplier-management |
| **PPM** | < 500 (auto) | 08-quality-management |
| **SC Cost / Revenue** | < 10-12% | 11-finance-controlling |
| **Bullwhip Ratio** | ≈ 1.0 | 10-risk-management |

---

## International Regulations Implemented

| Regulation | Country/Bloc | Department |
|-----------|-------------|-------------|
| **EU CSDDD** (Dir. 2024/1760) | EU | 09-compliance-regulatory |
| **US UFLPA** (Pub.L.117-78) | USA | 09-compliance-regulatory |
| **EU REACH** (1907/2006) | EU | 09-compliance-regulatory |
| **UK Modern Slavery Act** §54 | UK | 01-procurement / 14-supplier-development |
| **LkSG** (Germany 2023) | Germany | 09-compliance-regulatory |
| **Basel Convention** | Global | 07-logistics-transportation |
| **ISO 28000:2022** | Global | 01-procurement / 02-supplier-management |
| **ISO 9001:2015** | Global | 08-quality-management |
| **ISO 2859-1** (AQL) | Global | 08-quality-management |
| **GS1 v23.0** | Global | 05-inventory, 06-warehouse, 07-logistics |
| **Incoterms® 2020** | Global | 01-procurement / 07-logistics |
| **UN/EDIFACT** | Global | 13-order-management |
| **WTO TFA Art.7** | Global | 07-logistics-transportation |
| **US UCC Article 2** | USA | 01-procurement |
| **EU Deforestation Reg.** (2023/1115) | EU | 14-supplier-development |
| **EU CSRD** (Dir. 2022/2464) | EU | 14-supplier-development |
| **GHG Protocol Scope 3** | Global | 14-supplier-development |

---

## Algorithms Implemented

| Algorithm | Module | Department |
|-----------|--------|-------------|
| SMA, SES, Holt, Holt-Winters | `Forecasting.ts` | 03-demand-planning |
| Safety Stock (4 methods) | `SafetyStock.ts` | 03-demand-planning |
| EOQ, ROP, DIO, Inventory Turnover | `SafetyStock.ts` | 03-demand-planning |
| MRP Netting | `MaterialRequirement.ts` | 04-supply-planning |
| ABC-XYZ (9 cells) | `InventoryItem.ts` | 05-inventory-management |
| Event-sourced stock balance | `StockMovement.ts` | 05-inventory-management |
| ABC Velocity Slotting | `Warehouse.ts` | 06-warehouse-management |
| CPOI Slotting | `Warehouse.ts` | 06-warehouse-management |
| FEFO Picking | `Warehouse.ts` | 06-warehouse-management |
| AQL Sampling ISO 2859-1 | `InspectionRecord.ts` | 08-quality-management |
| DPMO / PPM calculation | `InspectionRecord.ts` | 08-quality-management |
| Supplier Scorecard (OTD/OTIF/PPM) | `SupplierScorecard.ts` | 02-supplier-management |
| Kraljic Matrix | `Supplier.ts` | 01-procurement |
| RFQ Multi-criteria evaluation | `RFQ.ts` | 01-procurement |
| 3-Way Invoice Match | `Invoice.ts` | 11-finance-controlling |
| Cash-to-Cash Cycle (C2C) | `CashFlowMetrics.ts` | 11-finance-controlling |
| Risk Matrix 5×5 | `RiskModel.ts` | 10-risk-management |
| HHI Concentration | `RiskModel.ts` | 10-risk-management |
| Bullwhip Effect Ratio | `RiskModel.ts` | 10-risk-management |
| Expected Annual Loss (EAL) | `RiskModel.ts` | 10-risk-management |
| ESG Scoring (E+S+G) | `SustainabilityRecord.ts` | 14-supplier-development |
| Perfect Order Rate | `SalesOrder.ts` | 13-order-management |
| CSDDD Phase Determination | `CSDDD.ts` | 09-compliance-regulatory |
| UFLPA Risk Assessment | `UFLPA.ts` | 09-compliance-regulatory |
| REACH Article Assessment | `REACH.ts` | 09-compliance-regulatory |

---

## Bibliographic References

| Work | Author | Year | Application |
|------|-------|-----|-----------|
| *Supply Chain Management: Strategy, Planning & Operation* (6th Ed.) | Chopra & Meindl | 2016 | General framework |
| *Business Logistics/Supply Chain Management* (5th Ed.) | Ballou | 2004 | Logistics and transportation |
| *Logistics and Supply Chain Management* (6th Ed.) | Christopher | 2022 | SC strategy |
| *Material Requirements Planning* (3rd Ed.) | Orlicky | 2022 | MRP/MPS |
| *World-Class Warehousing and Material Handling* | Frazelle | 2002 | WMS and slotting |
| *Sales and Operations Planning* | Wallace | 2004 | S&OP |
| APICS Dictionary (16th Ed.) | ASCM | 2024 | Terminology |
| SCOR Digital Standard | ASCM | 2019 | Process framework |
| ICC Incoterms® 2020 | ICC | 2019 | Delivery terms |
| GRI Standards | GRI | 2021 | Sustainability reporting |
| GHG Protocol Scope 3 | WRI/WBCSD | 2011 | Carbon footprint |
| "Purchasing Must Become Supply Management" HBR | Kraljic | 1983 | Kraljic Matrix |
| "The Bullwhip Effect in Supply Chains" MIT Sloan | Lee et al. | 1997 | Bullwhip effect |
| *Inventory Management and Production Planning* | Silver, Pyke & Peterson | 1998 | Safety stock |

---

## Available Claude Code Skills

| Skill | Command | Use |
|-------|---------|-----|
| SCM Code Review | `/scm-review` | Domain-aware review (money, idempotency, soft-delete) |
| Demand Forecasting | `/forecast` | Help with algorithms and metrics |
| Inventory Audit | `/inventory-audit` | Inventory logic audit |
| Supplier Check | `/supplier-check` | EDI/API integration review |
| Code Review | `/code-review` | General review before merge |
| Security Review | `/security-review` | Security audit |
| Deep Research | `/deep-research` | SCM standards research |
