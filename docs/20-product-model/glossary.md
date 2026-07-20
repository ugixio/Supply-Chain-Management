---
id: glossary
title: "Glossary — controlled vocabulary"
type: product-model
owner: orchestrator
status: active
since: 2026-07-19
updated: 2026-07-19
relations:
  - { type: part-of, target: index-product-model }
  - { type: governed-by, target: index-adr }
---
# Glossary

> One term, one meaning, one spelling — everywhere. Seeded from the estate (README,
> CLAUDE.md, department docs); terminology authority for definitions beyond this table:
> APICS Dictionary 16th Ed. (ASCM 2024). Owner column = the department whose docs hold
> the full treatment.

| Term | Definition | Owner |
|---|---|---|
| OTD | On-Time Delivery — orders delivered by promised date / total. World-class ≥ 95%. | 07-logistics |
| OTIF | On-Time In-Full — delivered on time AND complete. Walmart standard 98%. | 13-order-management |
| Perfect Order Rate | Orders with no error across delivery, documentation, damage, invoicing. ≥ 95%. | 13-order-management |
| Fill Rate | Orders fulfilled without backorder / total orders. | 05-inventory |
| ITR | Inventory Turnover Ratio = COGS / average inventory value. | 05-inventory |
| DIO | Days Inventory Outstanding = 365 / ITR. | 05-inventory |
| C2C | Cash-to-Cash cycle = DIO + DSO − DPO. Target < 30 days. | 11-finance |
| MAPE | Mean Absolute Percentage Error — forecast accuracy metric (with MAE, RMSE). | 03-demand-planning |
| PPM / DPMO | Defective parts per million / defects per million opportunities. | 08-quality |
| Bullwhip Ratio | Var(orders) / Var(demand); target ≈ 1.0. | 10-risk |
| ABC-XYZ | 9-box classification: consumption value (ABC) × demand variability (XYZ, by CV). | 05-inventory |
| EOQ | Economic Order Quantity = √(2DS/H) (Harris 1913). | 03-demand-planning |
| ROP | Reorder Point — stock level triggering replenishment. | 03-demand-planning |
| Safety Stock | Buffer against demand/lead-time variability; methods incl. z·σ_D·√LT. | 03-demand-planning |
| MRP / MPS | Material Requirements Planning / Master Production Schedule. | 04-supply-planning |
| ATP | Available-to-Promise — uncommitted supply available for new orders. | 13-order-management |
| S&OP | Sales & Operations Planning — the consensus planning cycle. | 12-sop-planning |
| FEFO | First-Expired-First-Out lot picking. | 06-warehouse |
| AQL | Acceptable Quality Limit sampling per ISO 2859-1. | 08-quality |
| NCR / SCAR | Non-Conformance Report / Supplier Corrective Action Request. | 08-quality |
| SPC | Statistical Process Control (control charts). | 08-quality |
| Kraljic Matrix | Supplier segmentation: profit impact × supply risk → strategic/leverage/bottleneck/non-critical. | 01-procurement |
| RFQ | Request for Quotation with multi-criteria evaluation. | 01-procurement |
| 3-Way Match | Invoice ↔ PO ↔ goods receipt reconciliation before payment. | 11-finance |
| Landed Cost | Full acquisition cost incl. freight, duty, insurance, handling. | 11-finance |
| HHI | Herfindahl-Hirschman Index — supplier concentration risk. | 10-risk |
| EAL | Expected Annual Loss — probability × impact, annualized. | 10-risk |
| SCOR-DS | SCOR Digital Standard (ASCM 2019) — Plan/Source/Make/Deliver/Return/Enable. | cross (ADR-0004) |
| Incoterms® 2020 | ICC delivery terms, 11 rules (DPU replaces DAT). | 01-procurement / 07-logistics |
| GTIN / GLN / SSCC | GS1 identifiers: trade item / location / logistic unit. | cross (GS1 v23) |
| SVHC | Substance of Very High Concern (EU REACH). | 09-compliance |
| UFLPA | US Uyghur Forced Labor Prevention Act — XUAR rebuttable presumption. | 09-compliance |
| CSDDD | EU Corporate Sustainability Due Diligence Directive 2024/1760. | 09-compliance |
| EUDR / CBAM | EU Deforestation Regulation / Carbon Border Adjustment Mechanism. | 14-supplier-dev / 09-compliance |
| ESG Scoring | Environment + Social + Governance composite supplier score. | 14-supplier-development |
| Idempotency Key | Client-supplied key making a transaction safe to retry (SCM-R12). | cross (scm-core) |
