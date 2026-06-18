# Supply Chain Management System
## Enterprise SCM — SCOR-DS Aligned | ISO 28000:2022 | Incoterms® 2020

---

## Estructura departamental

El sistema está organizado en **14 departamentos** que representan la estructura
organizacional completa de una cadena de suministro empresarial.

```
src/departments/
├── 01-procurement/            # Adquisiciones y Abastecimiento Estratégico
├── 02-supplier-management/    # Gestión y Evaluación de Proveedores
├── 03-demand-planning/        # Planificación de Demanda y Pronósticos
├── 04-supply-planning/        # Planificación del Suministro (MRP/MPS)
├── 05-inventory-management/   # Gestión de Inventarios (Event-Sourced)
├── 06-warehouse-management/   # Gestión de Almacenes (WMS)
├── 07-logistics-transportation/ # Logística y Transporte (TMS)
├── 08-quality-management/     # Gestión de Calidad (QMS / ISO 9001)
├── 09-compliance-regulatory/  # Cumplimiento Normativo Internacional
├── 10-risk-management/        # Gestión de Riesgos SC
├── 11-finance-controlling/    # Finanzas y Control de Gestión SC
├── 12-sop-planning/           # S&OP / Integrated Business Planning
├── 13-order-management/       # Gestión de Pedidos (Order-to-Cash)
└── 14-supplier-development/   # Desarrollo de Proveedores y Sostenibilidad ESG
```

---

## Mapa SCOR-DS → Departamentos

| SCOR Proceso | Departamentos |
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

## KPIs globales de la cadena

| KPI | Benchmark mundial | Departamento dueño |
|-----|------------------|-------------------|
| **OTIF** | ≥ 98% (Walmart) | 13-order-management |
| **OTD** | ≥ 95% | 07-logistics-transportation |
| **Perfect Order Rate** | ≥ 95% | 13-order-management |
| **Inventory Turnover** | ≥ 8-12× (FMCG) | 05-inventory-management |
| **Cash-to-Cash Cycle** | < 30 días | 11-finance-controlling |
| **Forecast MAPE** | < 15% (A items) | 03-demand-planning |
| **Supplier OTD** | ≥ 95% | 02-supplier-management |
| **PPM** | < 500 (auto) | 08-quality-management |
| **SC Cost / Revenue** | < 10-12% | 11-finance-controlling |
| **Bullwhip Ratio** | ≈ 1.0 | 10-risk-management |

---

## Regulaciones internacionales implementadas

| Regulación | País/Bloque | Departamento |
|-----------|-------------|-------------|
| **EU CSDDD** (Dir. 2024/1760) | UE | 09-compliance-regulatory |
| **US UFLPA** (Pub.L.117-78) | EE.UU. | 09-compliance-regulatory |
| **EU REACH** (1907/2006) | UE | 09-compliance-regulatory |
| **UK Modern Slavery Act** §54 | UK | 01-procurement / 14-supplier-development |
| **LkSG** (Alemania 2023) | Alemania | 09-compliance-regulatory |
| **Basel Convention** | Global | 07-logistics-transportation |
| **ISO 28000:2022** | Global | 01-procurement / 02-supplier-management |
| **ISO 9001:2015** | Global | 08-quality-management |
| **ISO 2859-1** (AQL) | Global | 08-quality-management |
| **GS1 v23.0** | Global | 05-inventory, 06-warehouse, 07-logistics |
| **Incoterms® 2020** | Global | 01-procurement / 07-logistics |
| **UN/EDIFACT** | Global | 13-order-management |
| **WTO TFA Art.7** | Global | 07-logistics-transportation |
| **US UCC Article 2** | EE.UU. | 01-procurement |
| **EU Deforestation Reg.** (2023/1115) | UE | 14-supplier-development |
| **EU CSRD** (Dir. 2022/2464) | UE | 14-supplier-development |
| **GHG Protocol Scope 3** | Global | 14-supplier-development |

---

## Algoritmos implementados

| Algoritmo | Módulo | Departamento |
|-----------|--------|-------------|
| SMA, SES, Holt, Holt-Winters | `Forecasting.ts` | 03-demand-planning |
| Safety Stock (4 métodos) | `SafetyStock.ts` | 03-demand-planning |
| EOQ, ROP, DIO, Inventory Turnover | `SafetyStock.ts` | 03-demand-planning |
| MRP Netting | `MaterialRequirement.ts` | 04-supply-planning |
| ABC-XYZ (9 casillas) | `InventoryItem.ts` | 05-inventory-management |
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

## Referencias bibliográficas

| Obra | Autor | Año | Aplicación |
|------|-------|-----|-----------|
| *Supply Chain Management: Strategy, Planning & Operation* (6th Ed.) | Chopra & Meindl | 2016 | Framework general |
| *Business Logistics/Supply Chain Management* (5th Ed.) | Ballou | 2004 | Logística y transporte |
| *Logistics and Supply Chain Management* (6th Ed.) | Christopher | 2022 | Estrategia SC |
| *Material Requirements Planning* (3rd Ed.) | Orlicky | 2022 | MRP/MPS |
| *World-Class Warehousing and Material Handling* | Frazelle | 2002 | WMS y slotting |
| *Sales and Operations Planning* | Wallace | 2004 | S&OP |
| APICS Dictionary (16th Ed.) | ASCM | 2024 | Terminología |
| SCOR Digital Standard | ASCM | 2019 | Framework de procesos |
| ICC Incoterms® 2020 | ICC | 2019 | Términos de entrega |
| GRI Standards | GRI | 2021 | Reporte sostenibilidad |
| GHG Protocol Scope 3 | WRI/WBCSD | 2011 | Huella de carbono |
| "Purchasing Must Become Supply Management" HBR | Kraljic | 1983 | Matriz Kraljic |
| "The Bullwhip Effect in Supply Chains" MIT Sloan | Lee et al. | 1997 | Bullwhip effect |
| *Inventory Management and Production Planning* | Silver, Pyke & Peterson | 1998 | Safety stock |

---

## Claude Code Skills disponibles

| Skill | Comando | Uso |
|-------|---------|-----|
| SCM Code Review | `/scm-review` | Revisión domain-aware (money, idempotencia, soft-delete) |
| Demand Forecasting | `/forecast` | Ayuda con algoritmos y métricas |
| Inventory Audit | `/inventory-audit` | Auditoría de lógica de inventario |
| Supplier Check | `/supplier-check` | Revisión de integraciones EDI/API |
| Code Review | `/code-review` | Revisión general antes de merge |
| Security Review | `/security-review` | Auditoría de seguridad |
| Deep Research | `/deep-research` | Investigación de estándares SCM |
