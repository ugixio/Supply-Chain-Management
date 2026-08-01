---
id: glossary
title: "Glossary — controlled vocabulary"
type: product-model
owner: orchestrator
status: active
since: 2026-07-19
updated: 2026-08-01
relations:
  - { type: part-of, target: index-product-model }
  - { type: governed-by, target: index-adr }
---
# Glossary

> One term, one meaning, one spelling — everywhere. Terminology authority for definitions beyond
> this table: APICS Dictionary 16th Ed. (ASCM 2024). Owner column = the department whose docs hold
> the full treatment.
>
> **Definitions only — no levels.** A glossary entry says what a term *means*; what value counts as
> good is the project's decision (ADR-0037, and the inclusion test in `CLAUDE.md`). This table once
> read *"OTD … World-class ≥ 95%"*, *"OTIF … Walmart standard 98%"* and *"C2C … Target < 30 days"* —
> one textbook illustration and two companies' policies, published here as vocabulary. Every project
> that read this file would have inherited them. Removed 2026-07-29; the concept node named in each
> row carries the meaning, the formula and the source.

| Term | Definition | Owner |
|---|---|---|
| OTD | On-Time Delivery — orders delivered by the promised date / total delivered. | 07-logistics |
| OTIF | On-Time In-Full — delivered on time AND complete; both conditions, one metric. | 13-order-management |
| Perfect Order Rate | Orders with no error across delivery, documentation, damage and invoicing — the product of the four rates, not their average. | 13-order-management |
| Fill Rate | Orders fulfilled without backorder / total orders. | 05-inventory |
| ITR | Inventory Turnover Ratio = COGS / average inventory value. | 05-inventory |
| DIO | Days Inventory Outstanding = 365 / ITR. | 05-inventory |
| C2C | Cash-to-Cash cycle = DIO + DSO − DPO, in days; negative is possible and is not by itself a goal. | 11-finance |
| MAPE | Mean Absolute Percentage Error — forecast accuracy metric (with MAE, RMSE). | 03-demand-planning |
| PPM / DPMO | Defective parts per million / defects per million opportunities. | 08-quality |
| Bullwhip Ratio | Var(orders) / Var(demand). By construction 1.0 = no amplification and > 1 = amplification; the ratio is an identity, the acceptable level is not. | 10-risk |
| ABC-XYZ | 9-box classification: consumption value (ABC) × demand variability (XYZ, by CV). | 05-inventory |
| EOQ | Economic Order Quantity = √(2DS/H) (Harris 1913). | 03-demand-planning |
| ROP | Reorder Point — stock level triggering replenishment. | 03-demand-planning |
| Safety Stock | Buffer against demand/lead-time variability; methods incl. z·σ_D·√LT. | 03-demand-planning |
| MRP / MPS | Material Requirements Planning / Master Production Schedule. | 04-supply-planning |
| ATP | Available-to-Promise — uncommitted supply available for new orders. | 13-order-management |
| S&OP | Sales & Operations Planning — the consensus planning cycle. | 12-sop-planning |
| FEFO | First-Expired-First-Out lot picking. | 06-warehouse |
| GR | Goods Receipt — the recorded arrival of ordered material; UN/EDIFACT RECADV is its message. | 06-warehouse / 01-procurement |
| Pull List | A material call-off in a pull system: demand signalled by consumption. Industry vocabulary — what one list contains is not standardized (CPT-0165). | 06-warehouse |
| Sequence (JIS) | Material staged in the exact order a consuming line will consume it. Industry vocabulary; what one sequence contains is not standardized (CPT-0164). | 06-warehouse |
| Flow vs Level | A **flow** counts events over an interval and sums across intervals; a **level** is read at an instant and must never be summed. Adding six readings of a backlog of 40 gives 240, which does not exist. Arithmetic, not convention. | cross (CPT-0163) |
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
| Idempotency Key | Client-supplied key making a transaction safe to retry. Retry safety belongs to the write path, so this is an engineering concern, not supply-chain law (ADR-0037). | cross (engineering) |
| Global Context | The read-only, versioned SCM knowledge substrate (`docs/` SSOT + `CPT-*` + rules) surfaced as a wiki; consumed by projects. | platform (ADR-0030) |
| Workspace | Top-level tenant space that contains Projects. | platform (ADR-0030) |
| Project | A unit of work that references the Global Context by stable ID and owns its transactional data; never mutates the context. | platform (ADR-0030) |
| Project Overlay | A project's local layer of project-scoped concepts + parameter overrides referencing (never rewriting) global nodes; reads resolve global-then-override. | platform (ADR-0030) |
| Connector | Ingests a project's development/progress signals (external dev tools and/or internal project data). | platform (ADR-0031) |
| Delivery Metric | A progress/velocity calculation over project signals, defined as a `CPT-*` concept node. | platform (ADR-0031) |
| Tech Branch | The technical discipline a Project belongs to (AI, ML, Data, Backend, Frontend, UI/UX, DevOps, …); open, materialized incrementally. | platform (ADR-0030) |
| Prompt-Refinement Gate | A user prompt is improved first, then the improved prompt is executed; original + improved retained. Incoming-quality control on instructions. | platform (ADR-0032) |
| Node | Any addressable workspace unit with a stable `id` and declared `type` (concept, rule, ADR, …); the atom of the workspace graph. | platform (node-model) |
| Edge | A typed relation between nodes (`part-of`/`governed-by`/`refines`/`depends-on`/`traces-to`/`supersedes`); authority edges point up the tier ladder. | platform (node-model) |
| Region | A connected subgraph of the workspace: the Global Context region, or one Project region per project. | platform (node-model) |
