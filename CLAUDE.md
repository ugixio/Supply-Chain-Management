# Supply Chain Management — Claude Code Guide

## Project Overview
Supply Chain Management system covering procurement, inventory, logistics, demand forecasting, and supplier management.

## Domain Context
When working on this project, apply supply chain domain knowledge:
- **Procurement**: Purchase orders, RFQs, vendor selection, contract management
- **Inventory**: Stock levels, reorder points, ABC analysis, cycle counting, warehouse management
- **Logistics**: Shipment tracking, carrier management, last-mile delivery, incoterms
- **Demand Planning**: Forecasting algorithms (MA, exponential smoothing, ML-based), safety stock calculations
- **Supplier Management**: Supplier scorecards, lead times, risk assessment, multi-sourcing strategies
- **Quality**: Inspection workflows, defect tracking, supplier quality metrics (DPMO, OTD, OTIF)

## Key Metrics to Track
- OTD (On-Time Delivery)
- OTIF (On-Time In-Full)
- Inventory Turnover Ratio
- Days Inventory Outstanding (DIO)
- Fill Rate
- Order Cycle Time
- Supplier Lead Time Variance

## Code Standards
- All monetary values in cents (integer) to avoid floating point errors
- Dates in ISO 8601 (YYYY-MM-DD); timestamps in UTC
- Quantities use unit-of-measure (UOM) codes (EA, KG, L, M, BOX…)
- SKU/item codes are immutable once created; use status flags (ACTIVE/DISCONTINUED/BLOCKED)
- All inventory transactions must be idempotent (support safe retries)

## Critical Business Rules
- Never allow negative inventory without explicit backorder flag
- Purchase orders require approval workflow above configurable threshold
- Soft-delete only — no hard deletes on financial records
- All stock movements must have a corresponding journal entry
- Lot/batch tracking required for regulated products

## Skills to Use

| Task | Skill |
|------|-------|
| Research supply chain patterns, algorithms, standards | `/deep-research` |
| Review code before merging | `/code-review` |
| Security audit (auth, data access, APIs) | `/security-review` |
| Verify a feature works end-to-end | `/verify` |
| Simplify complex logistics/inventory logic | `/simplify` |
| Set up project environment | `/session-start-hook` |

## Recommended Workflows

### Adding a new inventory transaction type
1. Define the transaction type enum
2. Implement the journal entry logic (debit/credit accounts)
3. Add idempotency key handling
4. Write integration test covering rollback scenario
5. Run `/code-review` before merging

### Adding a new supplier integration
1. Research the supplier's EDI/API standard with `/deep-research`
2. Implement adapter following the existing supplier interface
3. Add retry logic with exponential backoff
4. Run `/security-review` on auth/credential handling

### Demand forecasting changes
1. Use `/deep-research` to validate the algorithm choice
2. Backtest against historical data before deploying
3. Document accuracy metrics (MAE, MAPE, RMSE) in the PR

## Architecture Decisions
- Event-driven for inventory movements (append-only event log)
- CQRS recommended for read-heavy reporting queries
- Async processing for large batch imports (PO imports, inventory reconciliation)
- Webhooks for supplier/carrier integrations over polling

## Testing Requirements
- Unit tests for all business rule validations
- Integration tests for inventory transaction flows (always test rollback)
- Load tests before deploying to high-volume warehouses
- Contract tests for supplier/carrier API integrations
