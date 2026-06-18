# Supply Chain Management — Claude Code Guide

## Project Overview
Enterprise Supply Chain Management system aligned with **SCOR Digital Standard (SCOR-DS)**,
**ISO 28000:2022**, **Incoterms® 2020**, and major international regulations.

Covers: Procurement · Inventory (event-sourced) · Logistics · Demand Forecasting ·
Supplier Management · Quality Control · Warehouse Management · Compliance · Risk

---

## Architecture

```
src/
├── shared/           # Types (Money, UOM, Incoterms), Event Store (CQRS/Event Sourcing)
├── procurement/      # Purchase Orders (approval workflow), Supplier master (Kraljic)
├── inventory/        # Inventory Item master (ABC-XYZ), Stock Movements (event log)
├── demand-planning/  # Forecasting (SMA/SES/Holt/Holt-Winters), Safety Stock, EOQ
├── supplier-management/ # Supplier Scorecard (OTD/OTIF/PPM/DPMO)
├── logistics/        # Shipments, Incoterms 2020, Customs, Hazmat (IMDG/ADR)
├── quality/          # Incoming Inspection (AQL ISO 2859-1), NCR, DPMO
├── warehouse/        # WMS, FEFO lot picking, ABC Velocity Slotting, CPOI
├── compliance/       # CSDDD 2024, UFLPA 2021, EU REACH 1907/2006
└── risk/             # Risk matrix (5×5), HHI, Bullwhip effect, EAL
```

**Patterns**: Event Sourcing + CQRS (inventory movements) · Saga-ready aggregates ·
Domain-Driven Design bounded contexts · Immutable domain objects

---

## Domain Context

### Key KPIs to Track
- **OTD** (On-Time Delivery) — world-class ≥ 95%
- **OTIF** (On-Time In-Full) — Walmart standard: 98%
- **PPM/DPMO** — automotive <500 PPM; food ≤1000 PPM
- **Inventory Turnover Ratio** = COGS / Avg Inventory
- **DIO** (Days Inventory Outstanding) = 365 / Turnover Ratio
- **Fill Rate** — orders fulfilled without backorder
- **Bullwhip Ratio** = Var(orders) / Var(demand) — target ≈ 1.0

### SCOR-DS Process Mapping
| SCOR | Module |
|------|--------|
| Plan | `demand-planning/`, `risk/` |
| Source | `procurement/` |
| Deliver | `logistics/`, `warehouse/` |
| Return | `inventory/` (RETURN_FROM_CUSTOMER) |
| Enable | `compliance/`, `supplier-management/` |

---

## Code Standards
- **Money**: integer cents only — `Money.amount` is always `number` (integer). No floats.
- **Dates**: ISO 8601 (YYYY-MM-DD); timestamps in UTC (`ISOTimestamp`)
- **Quantities**: UOM codes per GS1 — see `UOM` constant in `shared/types.ts`
- **SKU codes**: immutable once created — use `status` flags (ACTIVE/DISCONTINUED/BLOCKED)
- **Inventory transactions**: idempotent via `idempotencyKey` — safe to retry
- **Deletes**: soft-delete only (`isDeleted: boolean`) — never hard-delete financial records

---

## Critical Business Rules
1. **Never allow negative inventory** without `backorderAllowed = true`
2. **POs above threshold** (`PO_APPROVAL_THRESHOLD_CENTS`, default $5,000) → `PENDING_APPROVAL`
3. **Soft-delete only** on POs, Invoices, Stock Movements, Shipments, Scorecards
4. **All stock movements** generate a journal entry (debit/credit GL accounts)
5. **Lot tracking** required for `storageCondition !== AMBIENT` or `reachSVHC = true`
6. **UFLPA**: suppliers with XUAR operations must provide `clearanceDocumentRef`
7. **CSDDD**: document retention minimum 5 years from assessment date (Art.23)

---

## International Standards & Regulations

| Standard / Law | Scope | Code Location |
|---------------|-------|---------------|
| ISO 28000:2022 | Supply chain security management | `Supplier.certifications` |
| ISO 9001:2015 | Quality management (§8.4, §8.5.2, §8.6, §8.7) | `InspectionRecord.ts` |
| GS1 Gen. Specs. v23 | GTIN, GLN, SSCC, UOM codes | `shared/types.ts`, all domains |
| Incoterms® 2020 | Trade terms (11 rules, DPU replaces DAT) | `INCOTERMS_2020` constant |
| UN/EDIFACT | ORDERS, DESADV, INVOIC, RECADV | Domain object mapping |
| ISO 2859-1 | AQL sampling for incoming inspection | `InspectionRecord.ts` |
| EU CSDDD 2024/1760 | Supply chain due diligence (phased from 2027) | `compliance/CSDDD.ts` |
| LkSG (Germany 2023) | ≥1,000 employees in Germany | `CSDDDDueDiligence` fields |
| UK Modern Slavery Act 2015 §54 | ≥£36m turnover, annual statement | `Supplier.modernSlaveryStatements` |
| US UFLPA (Pub.L. 117-78) | Xinjiang forced labour presumption | `compliance/UFLPA.ts` |
| EU REACH 1907/2006 | Chemical substance management | `compliance/REACH.ts` |
| C-TPAT (US CBP) | Customs supply chain security | `SecurityCertification` type |
| AEO (EU) | Authorised Economic Operator | `SecurityCertification` type |
| WTO TFA Art.7 | Pre-arrival processing, trusted traders | `Shipment.aeoShipperCertified` |
| Basel Convention | Hazardous waste transboundary movement | `ShipmentLine.hazmatClass` |
| US UCC Article 2 | Sale of goods — quantity required | `POLineItem.quantity` |

Full regulatory reference: `docs/standards/REGULATORY_FRAMEWORK.md`

---

## Key Algorithms Implemented

### Demand Forecasting (`src/demand-planning/algorithms/Forecasting.ts`)
| Algorithm | Use Case | Parameters |
|-----------|----------|-----------|
| SMA | Stable, no trend/season | period |
| SES (Holt 1957) | Stationary demand | α |
| Holt's Method | Trending demand | α, β |
| Holt-Winters (1960) | Trend + seasonal | α, β, γ, m |

Accuracy metrics: **MAE**, **MAPE**, **RMSE** — always compute when evaluating.

### Safety Stock (`src/demand-planning/algorithms/SafetyStock.ts`)
- **Method 3** (recommended): `ss = z · σ_D · √LT` (Holt/Chopra & Meindl Ch.11)
- **Method 4** (most accurate): `ss = z · √(LT·σ_D² + D̄²·σ_LT²)` — accounts for lead time variability
- **EOQ**: `√(2·D·S/H)` — Harris (1913)
- **XYZ classification**: CV < 10% = X, 10-25% = Y, > 25% = Z

### Supplier Scorecard Weighting
```
40% Delivery  (OTD 35% + OTIF 45% + RFT 20%)
30% Quality   (PPM score 60% + NCR rate 40%)
20% Commercial (Invoice accuracy 70% + PO variance 30%)
10% Soft metrics (manually assessed)
```
Rating: PREFERRED ≥90 | APPROVED ≥75 | CONDITIONAL ≥60 | PROBATION ≥45 | DISQUALIFIED <45

### Kraljic Matrix (`src/procurement/domain/Supplier.ts`)
| | Low Supply Risk | High Supply Risk |
|--|----------------|-----------------|
| **High Profit Impact** | LEVERAGE (bid) | STRATEGIC (partner) |
| **Low Profit Impact** | NON_CRITICAL (automate) | BOTTLENECK (stockpile) |

---

## Skills to Use

| Task | Skill |
|------|-------|
| Research SCM patterns, algorithms, regulation updates | `/deep-research` |
| Domain-aware SCM code review (money, idempotency, soft-deletes) | `/scm-review` |
| Demand forecasting help (algorithm selection, accuracy metrics) | `/forecast` |
| Inventory logic audit (negative stock, locking, lot tracking) | `/inventory-audit` |
| Supplier integration review (auth, retry, EDI compliance) | `/supplier-check` |
| General code quality review before merging | `/code-review` |
| Security audit (auth, APIs, credential handling) | `/security-review` |
| Verify feature works end-to-end | `/verify` |

---

## Recommended Workflows

### Adding a new inventory transaction type
1. Add to `MovementType` union in `StockMovement.ts`
2. Add GL account mapping in `getJournalAccounts()`
3. Update `projectStockBalance()` INBOUND array if applicable
4. Write integration test covering rollback scenario
5. Run `/scm-review` and `/code-review`

### Adding a new supplier integration (EDI/API)
1. `/deep-research` — research supplier EDI standard (UN/EDIFACT message type)
2. Check `SecurityCertification` for AEO/C-TPAT status
3. Run `assessUFLPARisk()` for XUAR supply chain mapping
4. Implement adapter with exponential backoff + idempotency
5. Run `/supplier-check` + `/security-review`

### Onboarding a new regulated product
1. Set `lotTracked: true`, `shelfLifeDays` in `InventoryItem`
2. Run `assessREACHCompliance()` for chemical content
3. Assign `storageCondition` appropriately
4. Set `reachSVHC: true` if SVHC identified
5. Update FEFO picking in warehouse module

### Demand forecasting changes
1. `/deep-research` to validate algorithm selection
2. Run `holtWinters()` or appropriate algorithm
3. Compute MAE, MAPE, RMSE — document in PR
4. Backtest: need ≥2 years history for seasonal models (Holt-Winters)
5. Flag SKUs with CV > 0.5 as high-variance

---

## Testing Requirements
- Unit tests for all business rule validations (`tests/unit/`)
- Integration tests for inventory transaction flows — always test rollback
- Load tests before deploying to high-volume warehouses
- Contract tests for supplier/carrier API integrations

Run tests: `npm test` | Unit only: `npm run test:unit`

---

## References
- Chopra & Meindl, *Supply Chain Management* 6th Ed. (Pearson, 2016)
- Ballou, R.H., *Business Logistics/Supply Chain Management* 5th Ed. (Pearson, 2004)
- Christopher, M., *Logistics and Supply Chain Management* 6th Ed. (FT Publishing, 2022)
- APICS Dictionary 16th Ed. (ASCM, 2024)
- ICC Incoterms® 2020 (ICC, 2019)
- ISO 28000:2022, ISO 9001:2015, ISO 2859-1:1999
- GS1 General Specifications v23.0
- SCOR Digital Standard (ASCM, 2019)
- EU Directive 2024/1760 (CSDDD) | US Pub.L. 117-78 (UFLPA) | EU REACH 1907/2006
