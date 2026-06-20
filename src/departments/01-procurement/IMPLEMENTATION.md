# Procurement — Enterprise Implementation Playbook

## Executive Summary

Procurement is the largest single controllable cost lever in a €50B global multinational.
Direct and indirect spend typically represents 50–70% of revenue, meaning even a 2%
efficiency gain delivers €500M–€700M in bottom-line impact. This playbook provides a
structured, phased roadmap to transform procurement from a transactional function into a
strategic value engine, covering the full Source-to-Pay (S2P) cycle across 40 countries,
10,000+ suppliers, and a multi-ERP landscape anchored on SAP S/4HANA with SAP Ariba as
the procurement front-end.

The strategic case rests on four pillars. First, spend visibility: without a unified spend
cube, category managers cannot negotiate leverage, maverick spend remains invisible, and
savings targets are set without baseline. Second, process standardisation: a harmonised
PR-to-PO workflow with 3-way matching eliminates duplicate payments, reduces cycle time,
and enables straight-through processing (STP) rates above 80%. Third, supplier base
rationalisation: applying Kraljic segmentation and TCO modelling allows consolidation of
the long tail (typically the bottom 80% of suppliers by spend account for less than 20%
of value) while deepening strategic partnerships with top-tier partners. Fourth, advanced
analytics and ML: NLP-based contract analysis, commodity price forecasting, and fraud
detection move procurement from reactive to predictive, protecting margin.

Expected ROI across a 3-year horizon: 3–5% addressable spend reduction (€750M–€1.25B on
€25B addressable spend), 40% reduction in PO cycle time, 60% reduction in invoice
exceptions, and a fraud detection coverage rate above 95% of invoice volume. The
implementation runs 72 weeks from kick-off to steady-state continuous improvement, with
quick wins (spend visibility dashboard, e-auction rollout) delivered by Week 20 to
demonstrate early value to the CFO and CPO.

The programme requires a dedicated team of 25–35 FTEs including category managers,
data engineers, SAP functional consultants, data scientists, and change management
specialists. External consulting support is recommended for Phases 0–2 (AS-IS, foundation,
standardisation), with internal teams taking full ownership from Phase 3 onward. A Centre
of Excellence (CoE) structure is established in Phase 6 to sustain and extend capability.

---

## Prerequisites & Dependencies

### Systems
- SAP S/4HANA 2023 (or later) — Materials Management (MM), Finance (FI), Controlling (CO)
- SAP Ariba Procurement (Buying & Invoicing, Sourcing, Contracts, Supplier Lifecycle)
- SAP Business Network (formerly Ariba Network) for supplier connectivity
- SAP Analytics Cloud (SAC) or equivalent BI platform (Power BI, Tableau)
- Master Data Governance (SAP MDG or equivalent) for vendor and material master
- Data lake / lakehouse (Apache Iceberg on object storage, or Databricks Delta Lake)
- ML platform (MLflow for experiment tracking, seldon or BentoML for serving)
- EDI gateway (OpenText, Seeburger, or IBM Sterling) for EDIFACT message exchange
- Identity & Access Management (IAM) — LDAP/Active Directory integration

### Data Prerequisites
- Vendor master cleansed and deduplicated (golden record per DUNS number)
- Material master with UNSPSC commodity codes assigned to ≥90% of line items
- 3 years of historical PO, invoice, and GR data migrated to data lake
- Contract repository scanned to PDF/A and OCR-processed
- Open PO and outstanding invoice backlog reconciled before go-live

### Teams Required
- CPO sponsorship (mandatory executive champion)
- Category management leads (direct materials, indirect, services, capex)
- SAP MM/FI functional consultants (minimum 4 FTEs)
- Data engineering team (minimum 3 FTEs)
- Data science / ML team (minimum 2 FTEs)
- Change management & training lead
- Legal / contract management (contract templates, T&Cs, GDPR compliance)
- Finance (AP, controlling, treasury for FX and payment terms)
- IT security (API gateway, credential management, penetration testing)

### Skills Required
- SAP S/4HANA MM configuration (ME21N, MIGO, MIRO transaction flows)
- Python ≥ 3.11 with scikit-learn, XGBoost, LightGBM, HuggingFace Transformers, Prophet
- TypeScript domain modelling (this codebase)
- SQL and dbt for spend analytics transformations
- EDIFACT message standards: ORDERS (850), DESADV (856), INVOIC (810), RECADV (861)
- Ariba APIs (REST, cXML) and SAP Business Network connectivity
- Statistical process control for quality and lead-time variance analysis

---

## Phase 0: AS-IS Assessment (Weeks 1–8)

### Week 1–2: Stakeholder Mapping & Programme Governance

1. Identify all stakeholder groups: CPO, CFO, CIO, category managers, AP team, plant
   managers, legal, IT, and top-20 strategic suppliers.
2. Conduct 45-minute structured interviews with each stakeholder group using a standard
   questionnaire covering: current pain points, system landscape, process maturity, data
   availability, and change readiness.
3. Map stakeholders on a power/interest grid. CPO and CFO are high-power/high-interest
   and must be engaged weekly. Plant managers are high-power/low-interest and need
   monthly briefings with clear WIIFM (what's in it for me) messaging.
4. Establish Programme Steering Committee (PSC): CPO (chair), CFO representative, CIO,
   and implementation lead. Cadence: bi-weekly.
5. Stand up project management tooling: Jira for task tracking, Confluence for
   documentation, SharePoint for deliverable repository.
6. Define RACI matrix covering all 14 procurement sub-processes (PR creation,
   approval, sourcing, RFQ, award, PO issuance, GR, invoice receipt, 3-way match,
   payment, contract management, supplier onboarding, performance review, dispute
   resolution).

### Week 3–4: Current State Process Documentation

1. Shadow the PR-to-PO process in 3 representative business units (high-volume
   manufacturing, indirect services, capex). Document every step, system touchpoint,
   approval escalation, and manual workaround.
2. Map all existing systems by country: identify ERP instances (SAP, Oracle, legacy),
   procurement portals, e-mail-based PO processes, and paper-based approvals.
3. Document approval authority matrix (Delegation of Authority — DoA) per country
   and spend category. Note: the codebase enforces PO_APPROVAL_THRESHOLD_CENTS
   ($5,000 / ~€4,600) as the baseline; actual DoA tiers are typically 5 levels
   (buyer, senior buyer, category manager, CPO, board).
4. Photograph and document all paper-based workflows. Estimate volume of transactions
   that bypass the ERP (shadow spend / P-card spend / petty cash procurement).
5. Collect existing KPI reports (if any): PO cycle time, invoice exception rate,
   supplier OTD, contract coverage %, maverick spend %.

### Week 5–6: Data Quality Audit

1. Extract vendor master from SAP: run deduplication analysis using fuzzy matching on
   vendor name + bank account + DUNS. Target: ≤2% duplicate rate before go-live.
2. Audit material master: % of materials with UNSPSC L4 codes, % with valid UOM,
   % with active price conditions. Flag materials with >12 months no movement.
3. Pull 3-year PO history. Compute: average lines per PO, % single-line POs,
   % POs raised after goods receipt (retrospective POs — a control weakness), and
   % POs with no GR ever posted.
4. Invoice quality audit: % invoices requiring manual intervention, % with price
   variance >2%, % with quantity variance, average days to approve, % duplicate
   invoices (same vendor + amount + date).
5. Contract repository audit: total contracts by category, % with expiry dates in
   system, % with scanned PDF available, % with structured data (pricing schedules,
   SLA terms) extracted.
6. Produce data quality scorecard with RAG (Red/Amber/Green) status per data domain.
   Any domain Red (>15% error rate) requires a dedicated data remediation sprint
   before Phase 1 can proceed.

### Week 7–8: Gap Analysis & KPI Baseline

1. Benchmark current state KPIs against world-class targets (see KPIs & Success
   Metrics section). Document the gap for each KPI.
2. Apply APQC (American Productivity & Quality Center) procurement benchmarking
   framework. Identify which quartile the organisation currently sits in across:
   cost to procure per PO, PO cycle time, contract coverage, and STP rate.
3. Perform spend analysis on the 3-year extract using the 80/20 (Pareto) rule:
   identify the top 20% of suppliers by spend, top 20% of categories by spend,
   and any single-supplier concentration above 30% in a critical category (supply
   concentration risk — see HHI in supplier management module).
4. Conduct a compliance audit: % of spend under contract, % of invoices matched to PO,
   % of POs raised without approved supplier, % of payments outside agreed terms.
5. Produce AS-IS Assessment Report (mandatory PSC deliverable). Include: process maps,
   data quality scorecard, KPI baseline, gap analysis, and prioritised list of
   quick wins. Present to PSC for approval before Phase 1 kick-off.

---

## Phase 1: Foundation & Master Data (Weeks 9–20)

### Master Data Model Design (Weeks 9–11)

The master data foundation is the most critical and most often underestimated phase.
Errors here propagate through every downstream process.

**Vendor Master (SAP Vendor Account Group)**

Each vendor record must carry:
- DUNS number (mandatory for strategic and bottleneck suppliers)
- UNSPSC category codes (up to 5 per vendor, representing their supply scope)
- Incoterms® 2020 default (one of 11 rules: EXW, FCA, CPT, CIP, DAP, DPU, DDP,
  FAS, FOB, CFR, CIF)
- Payment terms code (mapped to SAP payment term key)
- Withholding tax classification per country
- Bank account (encrypted, IBAN-validated)
- ISO 28000:2022 certification flag and expiry
- Sanction screening status (OFAC, EU, UN) — auto-refreshed weekly
- UFLPA risk flag (see compliance module)
- Supplier tier (1 = direct contract, 2 = sub-tier, 3 = sub-sub-tier)
- Kraljic segment (STRATEGIC / LEVERAGE / BOTTLENECK / NON_CRITICAL)

**Material / Service Master**

- UNSPSC Level 4 code (mandatory)
- GS1 GTIN (for physical goods)
- Base UOM (GS1 UOM code)
- Order UOM and conversion factor
- Valuation class (for FI integration)
- Price control (S = standard, V = moving average)
- ABC classification (A/B/C by spend or volume)
- Lead time (planned delivery time in days)
- Minimum order quantity and order increment

**Contract Master (SAP CLM / Ariba Contracts)**

- Contract ID (UUID)
- Effective date, expiry date, auto-renewal flag
- Commodity scope (UNSPSC list)
- Pricing schedule (structured — not PDF only)
- Index linkage (commodity index, base period, adjustment formula)
- SLA terms (OTD target, OTIF target, PPM limit)
- Penalty and bonus clauses (structured fields, not free text)
- Governing law and dispute resolution jurisdiction

### ERP Integration: SAP S/4HANA (Weeks 9–14)

**PR-to-PO Integration**

1. Configure SAP document types: ZPR (purchase requisition), ZPO (standard PO),
   ZBL (blanket/release order), ZFPO (framework PO).
2. Map approval workflows in SAP (using SAP Business Workflow or SAP BTP Process
   Automation) to the DoA matrix established in Phase 0. The codebase
   PO_APPROVAL_THRESHOLD_CENTS constant must match the SAP approval condition value.
3. Enable Ariba Buying integration via SAP Business Network: configure cXML PunchOut
   catalogs for all indirect categories (IT, office supplies, MRO). This alone
   typically reduces maverick spend by 30–40% in indirect categories.
4. Configure 3-way matching tolerance rules in SAP MIRO:
   - Price variance tolerance: ±2% or ±€50 (whichever is greater) — auto-post
   - Quantity variance tolerance: ±1% or ±1 EA — auto-post
   - Outside tolerance: route to buyer queue for manual review
5. Enable evaluated receipt settlement (ERS) for strategic suppliers: auto-generate
   MIRO documents from GR posts, eliminating invoice entirely for top-tier partners.
6. Configure output determination for PO output: EDI ORDERS (EDIFACT D.01B or
   D.96A) for EDI-capable suppliers, PDF e-mail for others, cXML for Ariba Network.

**Finance Integration**

1. Map each procurement document type to a commitment item and funds center (for
   budget control / Funds Management module if applicable).
2. Configure GR/IR clearing account (SAP account 19300000 typically) and accrual
   rules: goods receipted but not invoiced must accrue at period-end.
3. Enable real-time COGS posting from GR for direct materials (movement type 101).
4. Configure intercompany purchasing (STO — Stock Transfer Order) for the 40-country
   intercompany supply chain. Transfer pricing rules must be configured per country
   pair per tax authority requirements.

### Data Migration (Weeks 12–16)

Data migration follows the standard ETL-validate-load-reconcile pattern:

1. **Extract**: Pull vendor master, material master, open POs, open contracts, and
   3-year transactional history from all legacy systems. Use SAP BAPI
   (BAPI_VENDOR_GETLIST, BAPI_PO_GETDETAIL) or SAP IDOC outbound for structured
   extract.
2. **Transform**: Apply cleansing rules (deduplication, DUNS enrichment, UNSPSC
   tagging, IBAN validation). All transformations documented in dbt models, version-
   controlled in Git.
3. **Load (pilot)**: Load 10% sample into SAP development system. Run automated
   reconciliation: record count, spend total, open commitment total must match
   source within 0.01%.
4. **UAT load**: Full load into UAT system. Category managers and AP team perform
   parallel running: raise 50 test POs, process 20 test invoices, verify 3-way
   match outcomes match expected.
5. **Cutover**: Freeze legacy systems 48 hours before go-live. Load delta (new
   transactions in freeze window) using fast-track LSMW or LTMC (SAP LTMC = Legacy
   System Migration Cockpit). Post-load reconciliation must complete within 4 hours.
6. **Day-1 support**: 10-person hypercare team on-site for 2 weeks post go-live.
   Dedicated SAP OSS (Online Support System) priority queue for P1/P2 issues.

### User Roles & Access Control (Weeks 15–17)

Define SAP authorisation concept following the principle of least privilege:

| Role | SAP Transaction Access | Ariba Access | Spend Limit |
|------|----------------------|--------------|-------------|
| Requisitioner | ME51N (create PR) | Self-service catalog | Per DoA |
| Buyer | ME21N, ME22N, ME23N, ME2N | Sourcing (view) | Per DoA |
| Senior Buyer | All buyer + source selection | Sourcing (full) | Per DoA |
| Category Manager | All + contract creation | Sourcing + Contracts | Per DoA |
| AP Specialist | MIRO, MR8M, F-44 | Invoice management | N/A |
| Procurement Manager | All + reports | Full access | Full |
| Auditor | Display only (ME23N, FB03) | Read-only | None |

Segregation of duties (SoD) controls — mandatory:
- Cannot create vendor AND create PO (prevents fictitious vendor fraud)
- Cannot approve own PO (prevents self-approval)
- Cannot post GR AND approve invoice for same PO (prevents collusion)
- AP team cannot access vendor master creation

### Core Process Mapping (Weeks 17–20)

Document all 8 core procurement processes as swimlane diagrams (BPMN 2.0):

1. **Purchase Requisition to Purchase Order**: Requestor → Budget check → Approval
   routing → Buyer sourcing decision → PO issue → Supplier acknowledgement
2. **Request for Quotation (RFQ) to Award**: Scope definition → Supplier shortlist
   → RFQ issue → Bid receipt → TCO evaluation → Award decision → Contract / PO
3. **Contract Lifecycle Management**: Negotiation → Execution → Obligation tracking
   → Price adjustment triggers → Renewal / termination
4. **Supplier Onboarding**: Registration → Document collection → Risk assessment
   → UFLPA / sanctions check → Quality audit → Approval → Activation in ERP
5. **3-Way Match & Invoice Processing**: GR post → Invoice receipt → System match
   → Exception handling → Approval → Payment run (F110)
6. **Blanket Order / Scheduling Agreement**: Framework negotiation → Release order
   issuance → Delivery schedule (JIT) → Cumulative quantity reconciliation
7. **e-Auction / Reverse Auction**: Event setup → Supplier briefing → Live event
   → Bid evaluation → Award → Savings documentation
8. **Procurement Performance Review**: Monthly scorecard → Supplier development →
   Corrective action tracking → Annual strategy review

---

## Phase 2: Process Standardisation (Weeks 21–36)

### Standard Operating Procedures

Produce SOPs for each of the 8 core processes. Each SOP must include: purpose, scope,
roles, inputs, process steps with system screenshots, outputs, KPIs, and escalation path.
SOPs are stored in Confluence and linked from SAP transaction help text.

Critical SOPs for compliance:
- **SOP-PROC-001**: Vendor master creation and maintenance (SoD controls, DUNS
  mandatory, sanctions screening)
- **SOP-PROC-002**: Emergency/off-contract purchase (limited to genuine emergencies;
  requires CPO approval and post-hoc competitive justification within 30 days)
- **SOP-PROC-003**: Retrospective PO (forbidden except for utilities/telecom; must
  be flagged for internal audit review)
- **SOP-PROC-004**: Payment term negotiation (standard: Net 30; strategic partners:
  Net 45; extended supply chain finance: up to Net 90 with SCF programme)

### Reporting & Dashboards (Weeks 28–33)

Build the following dashboards in SAP Analytics Cloud (or equivalent):

**Executive Dashboard** (CPO / CFO audience):
- Total addressable spend by category and region (drill-down to L4 UNSPSC)
- Savings pipeline: identified → committed → realised
- Contract coverage % (target: >85% of addressable spend)
- STP rate (target: >80%)
- Maverick spend % (target: <10%)
- Supplier diversity spend (target per policy)

**Operational Dashboard** (Category Manager audience):
- Open POs by status (issued, acknowledged, overdue)
- PO cycle time distribution (PR approval + sourcing + PO issue)
- Invoice exception queue by reason code
- Expiring contracts (next 90 days)
- Supplier performance by category (OTD, OTIF, PPM)

**AP Dashboard** (Accounts Payable audience):
- Invoice exception rate and ageing
- Early payment discount capture rate
- Days Payable Outstanding (DPO) vs target
- Duplicate invoice alerts
- GRIR (Goods Receipt / Invoice Receipt) open items ageing

### Training & Change Management (Weeks 30–36)

Training curriculum by role group:

**Requisitioners (estimated 2,000 users across 40 countries)**:
- E-learning module: 45 minutes, multilingual (English mandatory per CLAUDE.md;
  local language supplementary materials permitted)
- Topics: how to raise a PR in Ariba, catalog shopping, approval status tracking,
  when to contact the buyer
- Certification: pass rate ≥80% on 20-question assessment

**Buyers & Category Managers (estimated 150 users)**:
- 3-day instructor-led workshop (virtual)
- Day 1: S2P process, SAP ME transactions, Ariba Sourcing
- Day 2: TCO modelling, e-auction mechanics, contract setup
- Day 3: Spend analytics, KPI interpretation, supplier performance management
- Hands-on exercises in UAT system

**AP Specialists (estimated 80 users)**:
- 2-day instructor-led workshop
- Day 1: MIRO processing, 3-way match logic, exception handling
- Day 2: ERS, payment runs, GRIR clearing, month-end close
- Shadowing sessions with experienced AP leads post-training

**Change management communications plan**:
- Week 18: "What's changing and why" video message from CPO (2 minutes)
- Week 22: Department-level town halls (category managers present to business units)
- Week 30: Go-live countdown newsletter (bi-weekly)
- Week 36: Go-live day: helpdesk activated, floor-walkers in key sites
- Week 38–40: Post go-live pulse survey (target: >70% satisfaction)

---

## Phase 3: Mathematical Models — Step-by-Step

### Model 1: Economic Order Quantity (EOQ)

**Business Problem Solved**

Determines the optimal purchase quantity Q* that minimises total inventory cost
(ordering cost + holding cost). Without EOQ, buyers order too frequently (high
ordering cost) or in excess (high holding cost). For a €50B company with 50,000+ SKUs,
a 5% reduction in total inventory cost can free €200M+ in working capital.

**Mathematical Formulation**

Basic EOQ (Harris, 1913):

    Q* = √(2 · D · S / H)

Where:
- D = annual demand (units/year)
- S = ordering cost per order (€/order) — includes buyer time, system cost, freight
  fixed element
- H = annual holding cost per unit (€/unit/year) = unit cost × holding cost rate
  (typically 20–30% per annum including capital cost, storage, obsolescence, insurance)

Total Cost:

    TC(Q) = (D/Q) · S + (Q/2) · H + D · P

Where P = unit purchase price.

**Extension: EOQ with All-Units Quantity Discounts**

Suppliers often offer tiered pricing: P1 for Q < Q_break1, P2 for Q ≥ Q_break1, etc.

    For each price tier i:
      Q*_i = √(2 · D · S / H_i)   where H_i = h · P_i
      If Q*_i is feasible in tier i, compute TC(Q*_i)
      Otherwise, evaluate TC at the tier break-point

Select the Q that yields the minimum feasible TC across all tiers.

**Input Data Requirements**

| Input | Source | Update Frequency |
|-------|--------|-----------------|
| D (annual demand) | SAP MMBE / consumption history | Monthly |
| S (ordering cost) | Finance time study + SAP system cost allocation | Annual |
| h (holding cost rate) | Treasury (WACC) + warehouse cost per pallet | Annual |
| P (unit price) | SAP info record / contract pricing | Per contract change |
| Q_break (quantity discount tiers) | Supplier price lists / contracts | Per contract change |

**Step-by-Step Implementation**

1. Extract 24 months of GI (goods issue) postings from SAP (movement type 261/201)
   per material-plant combination. Compute D = annualised consumption.
2. Conduct ordering cost study: time-track a sample of 50 POs across categories.
   Include: buyer time to source (hours × hourly rate), SAP transaction time,
   supplier acknowledgement follow-up, freight booking (fixed element). Typical
   range: €50–€250 per PO depending on complexity.
3. Compute holding cost rate h: h = WACC + physical storage rate + obsolescence
   write-off rate + insurance rate. Example: 12% WACC + 5% storage + 3%
   obsolescence + 1% insurance = 21% per annum.
4. Extract unit prices from SAP ME1M (list of info records) or contract conditions
   (ME33K).
5. Collect quantity discount tiers from contract management system or supplier
   price lists.
6. Implement EOQ calculation in Python (see `python/01_procurement/eoq.py`).
   Use numpy for vectorised computation across all SKUs simultaneously.
7. Apply feasibility check: Q* must be ≥ minimum order quantity (MOQ) and a
   multiple of the order increment. Round up to the nearest valid quantity.
8. Compute reorder point: ROP = D_daily · LT + safety_stock. Where LT is the
   vendor-material planned delivery time from SAP info record.
9. Load Q* back to SAP as the "rounding value" or "lot size" in the MRP view of
   the material master (MM02, MRP1 tab, field "Fixed lot size" or "Maximum lot size"
   depending on MRP type).
10. Schedule monthly batch re-computation: demand is not static. A Δ>20% in
    annualised demand triggers automatic recalculation and buyer notification.
11. Document savings: compare pre-EOQ average order quantity vs Q* for each SKU.
    Report total inventory cost reduction and ordering cost reduction in the
    procurement savings tracker.

**Validation Approach**

- Back-test: apply EOQ to 12 months of historical data, simulate inventory levels,
  and compare total cost to actual total cost. Target: ≥5% cost reduction vs actuals.
- Sensitivity analysis: compute ∂TC/∂Q at Q=Q*. The EOQ cost function is relatively
  flat near the optimum (±20% of Q* changes TC by <2%), so MOQ rounding is safe.
- Pilot: select 200 SKUs in one plant, implement EOQ lot sizes, measure actual
  inventory turns and order frequency over 6 months vs control group.

**Example Calculation**

    D = 10,000 units/year
    S = €120 per order
    P = €50 per unit
    h = 25% → H = €50 × 0.25 = €12.50 per unit/year

    Q* = √(2 × 10,000 × 120 / 12.50) = √192,000 = 438 units

    TC(Q*) = (10,000/438) × 120 + (438/2) × 12.50 = 2,740 + 2,738 = €5,478/year

    With quantity discount: P2 = €47 for Q ≥ 500
    H2 = €47 × 0.25 = €11.75
    TC(500) = (10,000/500) × 120 + (500/2) × 11.75 + 10,000 × 47
             = 2,400 + 2,938 + 470,000 = €475,338/year (vs €505,478 at P1)
    Discount saves €30,140/year → take the 500-unit break quantity.

---

### Model 2: Supplier Scoring — Weighted Average

**Business Problem Solved**

Provides a single, objective numerical score for each supplier enabling ranking, tier
assignment, and qualification decisions. Without a consistent scoring model, buyer
preferences dominate, favourable incumbent suppliers are retained despite declining
performance, and cost reduction initiatives lack objective supplier selection criteria.

**Mathematical Formulation**

    Score_total = Σ (w_i × norm_i(KPI_i))

Where:
- w_i = weight of dimension i (sum to 1.0)
- KPI_i = raw KPI value for dimension i
- norm_i = normalisation function mapping KPI_i to [0, 100]

Standard normalisation for "higher is better" KPIs:

    norm(x) = min(100, (x / x_target) × 100)

Standard normalisation for "lower is better" KPIs (e.g., PPM):

    norm(x) = max(0, 100 - (x / x_max_acceptable) × 100)

The full weight structure (from CLAUDE.md):

    Delivery (40%):
      OTD score × 0.35
      OTIF score × 0.45
      RFT (Right First Time) score × 0.20

    Quality (30%):
      PPM score × 0.60
      NCR rate score × 0.40

    Commercial (20%):
      Invoice accuracy score × 0.70
      PO variance score × 0.30

    Soft metrics (10%):
      Manual assessment by category manager (innovation, responsiveness, ESG)

Rating thresholds: PREFERRED ≥90 | APPROVED ≥75 | CONDITIONAL ≥60 |
                   PROBATION ≥45 | DISQUALIFIED <45

**Step-by-Step Implementation**

1. Define KPI data sources: OTD and OTIF from SAP GR timestamps vs PO delivery dates
   (EKPO-EINDT vs EKBE-BUDAT); PPM from QM module (QA32); NCR rate from Quality
   Notification (QM01); invoice accuracy from MIRO exception log; PO variance from
   MIRO price variance posting (WE19 tolerance exceeded events).
2. Build the KPI extraction SQL/ABAP query. Run monthly on the last business day.
   Group by vendor number and rolling 12-month window.
3. Apply normalisation. Define target values per category (automotive: PPM target
   500, food: PPM target 1000, general industrial: PPM target 2000).
4. Compute sub-scores for each dimension. Validate that sub-scores are in [0, 100].
5. Apply weights and compute total score. Round to 1 decimal place.
6. Assign rating label based on threshold table.
7. Persist scorecard to the `SupplierScorecard` aggregate in the event store
   (see `src/departments/02-supplier-management/`). Each scorecard is an immutable
   event; never overwrite — append new monthly scorecard events.
8. Generate automated email notification to supplier for scores below 75 (CONDITIONAL
   or worse). Email includes score breakdown, trend chart (last 6 months), and
   a 30-day corrective action request.
9. Trigger automated Ariba Supplier Lifecycle workflow for PROBATION suppliers:
   assign 90-day improvement plan with bi-weekly check-ins.
10. Trigger DISQUALIFIED flag in SAP vendor master (block for new PO creation via
    vendor block code) and notify category manager and legal.
11. Publish quarterly aggregate to executive dashboard: average score by category,
    score distribution histogram, number of suppliers per rating tier.

**Example Calculation**

    Supplier ABC, Q3 data:
    OTD = 93.2% → norm = min(100, 93.2/95×100) = 98.1
    OTIF = 89.1% → norm = min(100, 89.1/98×100) = 90.9
    RFT = 96.0% → norm = min(100, 96.0/98×100) = 98.0

    Delivery score = 98.1×0.35 + 90.9×0.45 + 98.0×0.20 = 34.3 + 40.9 + 19.6 = 94.8

    PPM = 320 → norm = max(0, 100 - 320/500×100) = 36.0
    NCR rate = 0.8% → norm = max(0, 100 - 0.8/2.0×100) = 60.0

    Quality score = 36.0×0.60 + 60.0×0.40 = 21.6 + 24.0 = 45.6

    Invoice accuracy = 98.5% → norm = min(100, 98.5/99×100) = 99.5
    PO variance = 1.2% → norm = max(0, 100 - 1.2/2.0×100) = 40.0

    Commercial score = 99.5×0.70 + 40.0×0.30 = 69.7 + 12.0 = 81.7
    Soft = 72.0 (category manager assessment)

    Total = 94.8×0.40 + 45.6×0.30 + 81.7×0.20 + 72.0×0.10
          = 37.9 + 13.7 + 16.3 + 7.2 = 75.1 → APPROVED

---

### Model 3: Spend Analysis Clustering — Spend Cube & Pareto

**Business Problem Solved**

Creates a structured, searchable spend cube (Category × Supplier × Business Unit × Country)
enabling category managers to identify savings opportunities, consolidation targets, and
maverick spend. Without spend classification, procurement operates blind.

**Mathematical Formulation**

Spend Cube dimensions:

    Spend(c, s, b, t) = Σ PO_line_value
        where category = c, supplier = s, business_unit = b, time_period = t

Pareto (80/20) Analysis:

    Sort suppliers by cumulative spend descending.
    Identify S_80 = smallest set of suppliers whose cumulative spend ≥ 80% of total.
    Typically: |S_80| / |S_total| ≈ 0.20 (20% of suppliers = 80% of spend).

Category Concentration (HHI-equivalent for categories):

    HHI_cat = Σ (spend_i / total_spend)²   for all suppliers i in category
    HHI_cat > 0.25 → high concentration risk; consider dual-sourcing.

**Step-by-Step Implementation**

1. Extract 3-year PO line data from SAP (table EKPO joined to EKKO, EKBE). Fields:
   MATNR (material), LIFNR (vendor), WERKS (plant), MENGE, NETPR, WAERS, BEDAT.
2. Enrich with UNSPSC L4 code from material master (MARA-MATKL mapped to UNSPSC
   via a maintained mapping table). Target: 95%+ coverage.
3. FX normalisation: convert all spend to EUR using ECB rates at the PO date.
   Maintain a daily FX rate table (source: ECB SDMX API, free and open).
4. Build dbt model: `fct_spend_cube` with grain = (UNSPSC_L4, vendor, plant,
   fiscal_period). Aggregate net PO value and PO line count.
5. Compute Pareto analysis: rank suppliers by total 12-month spend. Calculate
   cumulative % of spend. Tag each supplier as Top-20%, Next-30%, Long-Tail.
6. Run K-Means clustering (k=10–20) on supplier spend profile vector
   [spend_by_category_1, ..., spend_by_category_N] to identify supplier segments
   (broad-line generalists, specialists, niche). Use scikit-learn KMeans.
7. Compute HHI per L4 category. Flag categories with HHI > 0.25 for dual-sourcing
   review.
8. Publish spend cube as interactive Power BI / SAC dashboard with drill-down from
   L1 UNSPSC → L4, region → country → plant, and supplier group → individual.
9. Export top-50 savings opportunities: categories with HHI > 0.25, low contract
   coverage (<60%), or large long-tail (>40 suppliers in same L4 code).
10. Schedule quarterly spend refresh. Annual deep-cleanse to re-validate UNSPSC
    classifications as product ranges and suppliers evolve.

---

### Model 4: Tender TCO Model

**Business Problem Solved**

Purchase price is a poor proxy for true supplier cost. A supplier 15% cheaper on
unit price but with 3× higher quality defect rate, 2× longer lead time, and
unreliable delivery can be more expensive in total. TCO quantifies all cost elements
enabling objective, apples-to-apples comparison in tenders.

**Mathematical Formulation**

    TCO = P_purchase + C_transaction + C_quality + C_logistics + C_risk

Where:

    P_purchase = unit_price × annual_volume
    C_transaction = (PO_cost + invoice_cost + payment_cost) × annual_order_frequency
    C_quality = (PPM_rate / 1,000,000) × annual_volume × rework_cost_per_unit
                + NCR_rate × annual_volume × NCR_avg_cost
                + warranty_return_rate × annual_volume × warranty_cost_per_unit
    C_logistics = freight_rate × annual_weight + customs_duty × annual_value
                  + lead_time_days × daily_inventory_carry_cost × safety_stock_multiplier
    C_risk = (probability_of_disruption × expected_disruption_cost)
             + (concentration_premium: add 5% if single source in critical category)

**Step-by-Step Implementation**

1. Build TCO template in Excel (for buyer use during RFQ) and Python (for
   batch comparison of multiple bidders). The Python version uses pandas DataFrames
   with one row per bidder × one column per cost element.
2. Standardise cost assumptions: rework cost per unit is set by Engineering and
   Finance annually. NCR average cost (including buyer/supplier time, logistics
   return, corrective action administration) is costed by Quality. These are fixed
   inputs — buyers do not adjust them.
3. Collect bid data from RFQ: unit price, MOQ, lead time, freight terms (Incoterms),
   payment terms, and quality certifications.
4. Pull historical PPM and NCR data for incumbent suppliers from QM module. For new
   suppliers, use industry benchmark PPM adjusted for certification level.
5. Compute logistics cost: for EXW/FCA terms, add freight quote. For DDP, freight
   is included — ensure the freight component is visible (request unbundled pricing).
6. Compute risk premium: use the supplier risk score from the risk module (EAL —
   Expected Annual Loss). Add concentration premium if award would create >50%
   single-source dependency.
7. Rank bidders by TCO, not by unit price. Present TCO waterfall chart to sourcing
   committee (shows how each cost element contributes).
8. Document TCO savings vs incumbent / vs budget in the savings tracker.
   "Savings" = (TCO_baseline - TCO_awarded) × annual_volume.
9. Include TCO model as a mandatory attachment to the Award Recommendation memo.
   This is an audit trail requirement under CSDDD and most corporate governance
   frameworks.

---

### Model 5: Contract Index-Linked Pricing

**Business Problem Solved**

Commodity-linked contracts (steel, aluminium, resins, energy) must have structured
price adjustment mechanisms. Without them, either the supplier absorbs cost increases
(creating distress and supply risk) or the buyer pays spot prices through renegotiation
(losing price certainty).

**Mathematical Formulation**

    P_adjusted = P_base × [α + β × (I_current / I_base) + γ × (E_current / E_base)]

Where:
- P_base = contract base price at execution date
- α = fixed component (not index-linked) — typically 30–50% for labour/overhead
- β = commodity index weight — e.g., LME Aluminium
- γ = energy index weight — e.g., TTF Natural Gas (Europe)
- α + β + γ = 1.0
- I_current = current index value (monthly average)
- I_base = index value at contract base date
- E_current = current energy index
- E_base = energy index at base date

Price escalation cap (common clause): maximum ±10% per 12-month period regardless
of index movement.

**Step-by-Step Implementation**

1. Define the index mix at contract negotiation. Benchmarks: injection-moulded
   plastics — 40% resin index + 20% energy + 40% fixed. Steel fabrications —
   50% HRC steel index + 10% energy + 40% fixed.
2. Select publicly available, verifiable indices only: LME (London Metal Exchange),
   Platts, ICIS, Eurostat energy price index, CRU. Avoid proprietary indices.
3. Specify base period: typically the monthly average for the month of contract
   signature, or an average of 3 months centred on signature date.
4. Implement automated price adjustment calculation in Python. Source current index
   values via API (LME has a REST API; ICIS requires subscription; Eurostat is
   free via SDMX API).
5. Load adjusted prices to SAP contract conditions (ME33K → condition record update
   via BAPI_CONTRACT_CHANGE or IDOCtype ORDERS05) on a monthly or quarterly
   cadence per contract terms.
6. Generate price change notification to supplier and buyer 10 business days before
   effective date.
7. Maintain audit trail: every price change event logged with index values used,
   formula output, effective date, and the user/system that triggered the update.

---

### Model 6: e-Auction Reverse Auction Mathematics

**Business Problem Solved**

Reverse auctions create real-time competitive tension among pre-qualified suppliers,
driving prices toward market equilibrium. Academic research (Jap, 2002; Emiliani,
2000) shows average savings of 15–25% vs negotiated price. Most effective for
commodity/standardised products with ≥3 qualified bidders.

**Mathematical Formulation**

**Rank Score (for multi-attribute auctions):**

    Score_i = w_price × (P_min / P_i) × 100 + Σ_{j} w_j × Q_{i,j}

Where:
- P_i = bid price from supplier i
- P_min = current lowest bid price
- Q_{i,j} = normalised quality score for attribute j (delivery, payment terms, etc.)
- w_price + Σ w_j = 1.0

**Reserve price (minimum acceptable bid):**

    P_reserve = TCO_target - C_non_price_elements
    (Set based on should-cost model; never disclosed to suppliers)

**Step-by-Step Implementation**

1. Pre-qualify suppliers: minimum 3 bidders mandatory. Fewer than 3 creates
   pseudo-competition and is likely to be challenged by internal audit.
2. Build should-cost model for the product/service to establish the reserve price.
   Should-cost = material cost + labour + overhead + reasonable margin (8–12%
   for industrial goods).
3. Configure event in Ariba Sourcing: define bid line items, lot structure,
   opening prices (typically last price paid), decrement rules (minimum bid
   improvement: 0.5% of lot value or €500, whichever is greater), event duration
   (60–90 minutes standard, with automatic 5-minute extension if a bid arrives
   in final 5 minutes — the "overtime" rule).
4. Conduct supplier briefing: explain rules, test connectivity, confirm
   Incoterms for the lot (Incoterms® 2020 — ensure all bidders quote on the
   same basis, e.g., all DDP destination warehouse).
5. Run the event. Monitor in real-time. Capture all bids with timestamps (audit
   log mandatory).
6. Post-event: extract bid history. Compute final TCO for each bidder at their
   closing bid price. Confirm reserve price was met.
7. Award within 5 business days. Send award/non-award notifications to all
   participants simultaneously.
8. Document savings: baseline = (P_baseline - P_awarded) × volume × contract term.
   Enter in savings tracker with event ID reference.

---

## Phase 4: ML/AI Pipeline — Step-by-Step

### ML Model 1: NLP Risk Classification (DistilBERT)

**Business Problem Solved**

Procurement teams cannot manually monitor news and regulatory filings for 10,000+
suppliers. NLP models continuously scan structured and unstructured text (news,
sanctions lists, court filings, NGO reports) and classify suppliers by risk type
(financial distress, ESG violation, sanctions, quality recall, geopolitical).

**Model Architecture**

DistilBERT (Sanh et al., 2019) fine-tuned for multi-label classification:
- Base: `distilbert-base-uncased` from HuggingFace (Apache-2.0 licence)
- Task: multi-label classification (each text can trigger multiple risk labels)
- Labels: FINANCIAL_DISTRESS, SANCTIONS_ALERT, ESG_VIOLATION, QUALITY_RECALL,
  GEOPOLITICAL_RISK, LABOUR_VIOLATION, ENVIRONMENTAL_INCIDENT, NONE
- Output: probability score per label; threshold 0.60 triggers alert

**Training Data Requirements**

| Attribute | Specification |
|-----------|--------------|
| Volume | Minimum 5,000 labelled examples per class (40,000+ total) |
| Sources | Reuters, Bloomberg (licensed), NGO reports, SEC/EDGAR filings, court records |
| Labelling | Dual-annotator agreement required; Cohen's Kappa ≥ 0.80 |
| Language | English only (per CLAUDE.md language policy) |
| Date range | 5 years minimum for temporal coverage |
| Balance | Oversample minority classes (SANCTIONS_ALERT typically rare) |

**Feature Engineering**

1. Text preprocessing: lowercase, remove HTML tags, normalise Unicode,
   truncate to 512 tokens (DistilBERT maximum).
2. Entity linking: use spaCy NER to extract organisation names. Map to vendor
   master using fuzzy string matching (rapidfuzz library, MIT licence).
   Only score articles where confidence of supplier mention ≥ 0.85.
3. Temporal features: days since article publication (recent articles weighted
   higher in risk score aggregation).
4. Source credibility weight: Reuters/AP = 1.0, specialised trade press = 0.8,
   social media = 0.4 (use with caution).

**Model Training Procedure**

1. Split dataset: 70% train, 15% validation, 15% test. Stratify by label combination.
2. Tokenise with `AutoTokenizer.from_pretrained("distilbert-base-uncased")`.
3. Define model: `AutoModelForSequenceClassification` with `num_labels=8`,
   `problem_type="multi_label_classification"`.
4. Loss function: `BCEWithLogitsLoss` (binary cross-entropy per label).
5. Optimizer: AdamW, learning rate 2e-5, weight decay 0.01.
6. Training: 5 epochs, batch size 32, linear warmup for first 10% of steps.
7. Checkpoint best model on validation macro-F1.
8. Apply label-specific probability thresholds (tuned on validation set to
   maximise F1 per class — higher-stakes classes like SANCTIONS_ALERT use
   threshold 0.45 to favour recall over precision).

**Hyperparameter Tuning**

Use Optuna (MIT licence) for hyperparameter search:
- Learning rate: log-uniform [1e-5, 5e-5]
- Batch size: {16, 32}
- Warmup ratio: uniform [0.05, 0.20]
- Max epochs: {3, 5, 7}

Run 50 trials. Select based on macro-F1 on validation set.

**Validation Metrics & Thresholds**

| Metric | Minimum Threshold | Target |
|--------|------------------|--------|
| Macro-F1 | 0.75 | ≥ 0.85 |
| SANCTIONS_ALERT Recall | 0.90 | ≥ 0.95 |
| Precision (all) | 0.70 | ≥ 0.80 |
| False Positive Rate | < 0.15 | < 0.08 |

**Deployment to Production**

1. Serialise model with `model.save_pretrained()` and tokeniser with
   `tokenizer.save_pretrained()`. Store in MLflow Model Registry.
2. Serve via BentoML (Apache-2.0): expose REST endpoint
   `POST /api/v1/supplier-risk/classify` accepting `{text: str, supplier_id: str}`.
3. Input validation: reject requests with text < 20 tokens or > 600 tokens.
4. Batch inference: news feed ingestion runs every 4 hours via Apache Airflow DAG.
   Batch up to 10,000 articles per run.
5. Output persisted to risk event store. High-confidence alerts (top label > 0.80)
   trigger real-time notification via webhook to Ariba Supplier Lifecycle.

**Monitoring & Drift Detection**

1. Log all predictions with timestamps, article IDs, and confidence scores.
2. Weekly: compute production macro-F1 on a sample of 200 human-reviewed
   predictions. Alert if macro-F1 drops below 0.72 (5-point deterioration from
   baseline).
3. Monthly: run concept drift test (population stability index — PSI) on the
   input text embedding distribution. PSI > 0.25 triggers retraining flag.
4. Monitor false positive rate via buyer feedback: add "Was this alert useful?"
   button in the risk dashboard. Track thumbs-down rate; alert if > 25%.

**Retraining Cadence**

- Scheduled retraining: quarterly, incorporating 3 months of new labelled data.
- Event-triggered retraining: when PSI > 0.25 or macro-F1 < 0.72 on production
  monitoring.
- Emergency retraining: after a major geopolitical event (e.g., new sanctions
  regime) — within 5 business days, with priority labelling of event-related articles.

---

### ML Model 2: Spend Categorisation (XGBoost / LightGBM)

**Business Problem Solved**

Manually classifying invoices and PO line items to UNSPSC codes is expensive and
inconsistent. Auto-classification at ≥90% accuracy with a human-review queue for
the remaining 10% reduces classification cost by 80% and enables real-time spend
visibility.

**Model Architecture**

Two-stage classification:
- Stage 1: LightGBM classifier for UNSPSC Level 2 (family) — fast, high accuracy
- Stage 2: XGBoost classifier for UNSPSC Level 4 (commodity) within the predicted family

**Training Data Requirements**

| Attribute | Specification |
|-----------|--------------|
| Volume | 100,000+ labelled invoice line items (description → UNSPSC L4) |
| Sources | 3 years of SAP EKPO/MARA data with validated UNSPSC codes |
| Quality | Exclude records with manually overridden or corrected UNSPSC codes <6 months ago |
| Coverage | Minimum 200 examples per UNSPSC L4 code in scope |

**Feature Engineering**

1. Text features from line item description: TF-IDF (top 5,000 n-gram features,
   n=1,2,3) using scikit-learn `TfidfVectorizer`.
2. Vendor features: vendor UNSPSC category codes (one-hot or multi-hot), vendor
   country, vendor Kraljic segment.
3. Numerical features: unit price, quantity, UOM code (GS1 code as integer),
   PO document type.
4. Context features: business unit, plant, GL account (existing, even if wrong —
   it carries signal), cost centre.
5. Feature scaling: not needed for tree-based models, but normalise for any
   neural network layer.

**Model Training Procedure**

1. Split: 70/15/15 train/validation/test stratified by UNSPSC L4 code.
2. Train LightGBM Stage 1 (L2 classification):
   - `lgb.LGBMClassifier(num_leaves=127, learning_rate=0.05, n_estimators=500,
     objective='multiclass', metric='multi_logloss')`
   - Early stopping on validation log-loss with patience=50.
3. Generate L2 predictions as additional features for Stage 2.
4. Train XGBoost Stage 2 (L4 classification, within predicted L2):
   - `xgb.XGBClassifier(max_depth=8, learning_rate=0.05, n_estimators=500,
     objective='multi:softprob', eval_metric='mlogloss')`
5. Calibrate probabilities using `CalibratedClassifierCV` (isotonic regression)
   for reliable confidence scores.
6. Set confidence threshold: if max probability < 0.70, route to human review queue
   instead of auto-accepting.

**Hyperparameter Tuning**

Optuna with 100 trials for each stage. Key search space:
- LightGBM: num_leaves [31, 255], min_child_samples [10, 100], subsample [0.6, 1.0]
- XGBoost: max_depth [4, 12], subsample [0.6, 1.0], colsample_bytree [0.5, 1.0]

**Validation Metrics**

| Metric | Threshold |
|--------|-----------|
| Top-1 accuracy (L4) | ≥ 85% |
| Top-3 accuracy (L4) | ≥ 95% |
| Auto-acceptance rate | ≥ 80% (confidence ≥ 0.70) |
| Human review queue | ≤ 20% of volume |

**Deployment**

1. Batch inference: run nightly on all new PO lines and invoice lines posted that day.
2. Write UNSPSC prediction + confidence to EKPO custom field ZZ_UNSPSC and ZZ_CONF.
3. Route low-confidence items to SAP workflow task assigned to category manager.
4. Category manager approves/corrects → feedback stored and used in quarterly
   retraining.

---

### ML Model 3: Fraud Detection (Isolation Forest)

**Business Problem Solved**

Invoice fraud (duplicate invoices, fictitious vendors, inflated amounts, split
invoicing to avoid approval thresholds) costs companies 0.5–5% of revenue. An
unsupervised anomaly detection model flags suspicious patterns without requiring
labelled fraud examples (which are scarce and biased).

**Model Architecture**

Isolation Forest (Liu et al., 2008) — ensemble of random isolation trees.
Anomaly score ∈ [-1, +1]: scores near -1 = anomaly; scores near +1 = normal.

**Training Data Requirements**

- 24 months of invoice-level data (RBKP + RSEG tables in SAP)
- Features: vendor, invoice amount, invoice date, PO reference, GR reference,
  bank account, payment terms, payment amount, days between invoice and GR

**Feature Engineering**

1. Invoice amount deviation: `amount / vendor_12m_median_invoice_amount`
2. Timing anomalies: days between GR date and invoice date (flag if > 90 or < 0)
3. Round number flag: `amount % 1000 == 0` (round numbers are a fraud signal)
4. Duplicate detection features: same vendor + same amount within 30 days (count)
5. Threshold proximity: `amount / approval_threshold` — values in [0.85, 0.99]
   indicate potential split-invoice to avoid approval (Benford's Law extension)
6. Benford's Law first-digit distribution: compute χ² statistic for vendor's
   invoice amount first-digit distribution vs Benford expected distribution.
   High χ² = suspicious distribution.
7. Velocity features: invoices per day from this vendor (rolling 7-day average),
   deviation from vendor's historical mean velocity.

**Model Training Procedure**

1. Train IsolationForest on 18 months of "clean" historical data (exclude any
   known fraud cases if labelled):
   `IsolationForest(n_estimators=200, contamination=0.01, random_state=42)`
2. Tune `contamination` parameter: start at 1% (expected fraud rate), adjust based
   on precision of flagged cases after human review in first 90 days.
3. Save model with joblib. Retrain monthly on rolling 18-month window.
4. Threshold: flag if anomaly_score < -0.3 (tune empirically).

**Validation**

- Precision@100 on analyst-reviewed cases: target ≥ 40% (i.e., ≥ 40 of top-100
  flagged invoices are confirmed suspicious by AP team).
- Recall on known historical fraud cases: ≥ 80%.

**Deployment**

1. Inference: run on every invoice batch (3× per day in MIRO posting run).
2. High-risk flags (score < -0.5): automatic payment hold; route to AP Manager.
3. Medium-risk flags (score -0.5 to -0.3): add to daily review queue.
4. All flags logged in fraud audit trail with feature contributions
   (SHAP values computed using the `shap` library, MIT licence).

---

### ML Model 4: Commodity Price Forecasting (Prophet)

**Business Problem Solved**

Procurement teams need a 3–12 month forward view on commodity prices (steel, copper,
aluminium, polypropylene, energy) to time purchasing decisions, hedge exposure, and
set realistic budgets. Prophet (Taylor & Letham, 2018) handles multiple seasonalities,
holiday effects, and changepoints — common in commodity markets.

**Model Architecture**

Facebook Prophet (MIT licence):

    y(t) = trend(t) + seasonality(t) + holidays(t) + ε(t)
    trend: piecewise linear or logistic growth
    seasonality: Fourier series (annual, monthly)

**Training Data Requirements**

- Minimum 5 years of monthly average price data per commodity
- Sources: LME (metals), Platts (energy), ICIS (chemicals), World Bank Commodity Data
- All prices in EUR/USD with FX normalisation

**Step-by-Step Training**

1. Download historical price series via API or manual export. Validate: no gaps
   > 3 months; impute short gaps with linear interpolation.
2. Format for Prophet: DataFrame with columns `ds` (date, monthly frequency) and
   `y` (price in EUR).
3. Define changepoints: major market events (COVID-19 March 2020, Ukraine invasion
   February 2022) as known changepoints via `changepoints` parameter.
4. Add regressors: USD/EUR exchange rate, relevant demand index (e.g., Chinese PMI
   for base metals), energy price as regressor for energy-intensive commodities.
5. Fit: `model = Prophet(changepoint_prior_scale=0.3, seasonality_prior_scale=10)`
6. Generate forecast: `future = model.make_future_dataframe(periods=12, freq='M')`
7. Validate: walk-forward cross-validation using `cross_validation(model, horizon='90 days',
   period='90 days', initial='365 days')`. Compute MAPE, MAE, RMSE.

**Validation Thresholds**

| Commodity | Acceptable MAPE (12-month horizon) |
|-----------|-----------------------------------|
| LME Copper | ≤ 18% |
| LME Aluminium | ≤ 15% |
| Brent Crude | ≤ 25% |
| Polypropylene | ≤ 20% |

**Deployment**

1. Run monthly (1st business day). Produce 12-month forecast with 80% and 95%
   prediction intervals.
2. Publish to procurement dashboard: price trend chart with forecast band.
3. Trigger alerts: if forecast for next quarter is > 10% above current contract
   price, notify category manager to consider forward-buying or hedging.
4. Integrate with budget process: provide commodity price assumptions for annual
   budget submission (September each year).

---

### ML Model 5: PO Approval Prediction (LightGBM)

**Business Problem Solved**

Predicts whether a purchase order will be approved, approved with changes, or rejected
before submission. Buyers can proactively correct likely rejections, reducing cycle time
by 20–30% and improving first-time-right approval rates.

**Model Architecture**

LightGBM multi-class classifier (3 classes: APPROVED / APPROVED_WITH_CHANGES / REJECTED)

**Features**

- PO amount vs DoA limit for the submitter (ratio)
- Supplier rating (current scorecard score)
- Category (UNSPSC L2 — one-hot encoded)
- Budget availability (% of budget consumed YTD at time of submission)
- Time of year (month, fiscal quarter)
- Requestor seniority (approver level)
- Time since last approved PO from same requestor
- Number of line items
- Presence of supporting documentation (binary flag)
- Contract reference available (binary flag)
- Preferred / approved / conditional supplier flag

**Training Data**

- 3 years of PO approval workflow history from Ariba
- Minimum 1,000 examples of each outcome class
- Exclude emergency POs and system-generated release orders (not representative)

**Training & Deployment**

1. Standard LightGBM training with 5-fold stratified cross-validation.
2. SHAP explainability: compute SHAP values for each prediction.
3. Deploy as a pre-submission check in Ariba: when a buyer clicks "Submit for
   Approval," the model runs in < 200ms and displays:
   - Predicted outcome with confidence
   - Top-3 factors influencing the prediction (from SHAP)
   - Suggested remediation if REJECTED is predicted (e.g., "Add contract reference")
4. Do not block submission — this is advisory only. Buyers retain authority.
5. Monitor: track predicted vs actual approval outcomes weekly. Alert if accuracy
   drops below 75%.

---

## Phase 5: Integration & Automation (Weeks 53–72)

### SAP S/4HANA Integration Points

| Integration | Method | Direction | Frequency |
|-------------|--------|-----------|-----------|
| Vendor master sync | SAP MDG → S/4HANA IDOC | Outbound | Real-time on change |
| PO output to supplier | S/4HANA → Ariba Network (cXML) | Outbound | On PO release |
| GR confirmation | Ariba Network → S/4HANA IDOC | Inbound | On supplier ASN |
| Invoice from supplier | Ariba Network → S/4HANA MIRO | Inbound | On supplier submission |
| Scorecard data pull | S/4HANA API → Python ML pipeline | Outbound | Monthly batch |
| Price conditions update | Python → S/4HANA BAPI_CONTRACT_CHANGE | Inbound | Monthly (index-linked) |
| Spend data to lake | S/4HANA → data lake (EKKO/EKPO extract) | Outbound | Nightly |
| Anomaly alerts | ML service → Ariba workflow | Inbound | Real-time |

### EDI / EDIFACT Messages

| Message | EDIFACT Type | Direction | Trigger |
|---------|-------------|-----------|---------|
| Purchase Order | ORDERS D.01B | Outbound | PO release in SAP |
| Order Acknowledgement | ORDRSP | Inbound | Supplier confirms |
| Advance Shipping Notice | DESADV | Inbound | Supplier ships |
| Invoice | INVOIC | Inbound | Supplier invoices |
| Remittance Advice | REMADV | Outbound | Payment run F110 |
| Goods Receipt Confirmation | RECADV | Outbound | MIGO goods receipt |

All EDI messages routed through the EDI gateway (OpenText/Seeburger). Fallback:
PDF e-mail for non-EDI-capable suppliers (target: all top-200 suppliers EDI-enabled
by end of Phase 5).

### API Design

Base URL: `https://api.internal.company.com/procurement/v1`

```
GET  /purchase-orders?status=OPEN&vendor={vendorId}
POST /purchase-orders
GET  /purchase-orders/{poId}
PUT  /purchase-orders/{poId}/approve
PUT  /purchase-orders/{poId}/reject

GET  /vendors?category={unspsc}&country={iso2}
POST /vendors/onboard
GET  /vendors/{vendorId}/scorecard

POST /sourcing/rfq
GET  /sourcing/rfq/{rfqId}/bids
POST /sourcing/auctions

POST /spend-analysis/classify   ← ML spend categorisation
POST /risk/classify-news        ← ML NLP risk classification
GET  /commodities/{code}/forecast ← Prophet price forecast
```

All endpoints: OAuth 2.0 (client credentials flow), TLS 1.3, rate-limited to 1,000
requests/minute per client. Response format: JSON with `data`, `meta`, `errors` envelope.

---

## Phase 6: Continuous Improvement & Centre of Excellence

### CoE Structure

The Procurement CoE operates as a shared service embedded in the CPO organisation:

**CoE Director**: reports to CPO, owns the digital procurement roadmap.

**Capability Towers**:
1. Category Excellence: category strategy templates, market intelligence, benchmarking
2. Process & Technology: SAP/Ariba configuration, new feature rollout, STP rate
3. Analytics & ML: model maintenance, new model development, KPI reporting
4. Supplier Development: scorecard governance, development plans, disqualification
5. Compliance & Risk: UFLPA, CSDDD, REACH, sanctions, ESG reporting

**Governance Model**

- Monthly Procurement Operations Review: CoE Director + all Category Managers
  Review: savings delivery, STP rate, exception queue, model performance
- Quarterly Supplier Review Board: CPO + top-20 strategic suppliers (joint review
  of scorecard trends, development plans, and innovation pipeline)
- Annual Category Strategy Review: full spend re-segmentation, Kraljic re-assessment,
  supplier rationalisation targets for next fiscal year
- Semi-annual Model Review: data science team presents model performance metrics,
  drift statistics, and retaining outcomes to CPO and CIO

### Model Refresh Cadence

| Model | Scheduled Retrain | Event-Triggered |
|-------|------------------|-----------------|
| DistilBERT risk classification | Quarterly | New sanctions regime |
| Spend categorisation | Semi-annual | New UNSPSC version release |
| Isolation Forest fraud | Monthly (rolling window) | >20% alert precision drop |
| Prophet commodity | Monthly | Major market disruption |
| PO approval LightGBM | Quarterly | DoA policy change |
| EOQ parameters | Monthly (demand) / Annual (cost rates) | >20% demand shift |

---

## Technology Stack & Architecture

### Architecture Overview

```
Data Sources          Integration Layer        Platform              Consumers
──────────────────    ────────────────────     ──────────────────    ──────────
SAP S/4HANA     ─→                            Data Lake             SAC Dashboard
SAP Ariba       ─→   SAP Business Network  →  (Apache Iceberg)  →  Power BI
Supplier EDI    ─→   EDI Gateway           →  dbt Transforms    →  ML APIs
News feeds      ─→   Airflow DAGs          →  MLflow Registry   →  Ariba Workflows
Market indices  ─→   REST APIs             →  BentoML Serving   →  SAP S/4HANA
```

### Technology Justification

| Component | Technology | Licence | Justification |
|-----------|-----------|---------|---------------|
| Data lake format | Apache Iceberg | Apache-2.0 | ACID, time-travel, schema evolution |
| Orchestration | Apache Airflow | Apache-2.0 | Mature, SAP connector ecosystem |
| Transform | dbt-core | Apache-2.0 | SQL-first, version-controlled lineage |
| ML platform | MLflow | Apache-2.0 | Experiment tracking, model registry |
| Model serving | BentoML | Apache-2.0 | OSI-licensed, containerised |
| NLP | HuggingFace Transformers | Apache-2.0 | Best-in-class, DistilBERT available |
| Gradient boosting | LightGBM + XGBoost | MIT + Apache-2.0 | Speed and accuracy at scale |
| Forecasting | Prophet | MIT | Handles seasonality and changepoints |
| Graph analysis | NetworkX | BSD-3 | Python-native, no licence cost |
| Message queue | Apache Kafka | Apache-2.0 | High-throughput event streaming |

---

## Change Management & Training

### Stakeholder Groups & Approach

| Group | Size | Key Concern | Engagement Strategy |
|-------|------|-------------|---------------------|
| CPO & leadership | 5 | ROI, risk | Monthly steering; quarterly wins roadshow |
| Category managers | 50 | Job change | Co-design workshops; elevated strategic role |
| Buyers | 100 | Automation replacing jobs | Re-skill to analytical roles; clear career path |
| Requisitioners | 2,000 | System complexity | Self-service catalog; simplified UX; helpdesk |
| AP team | 80 | Workload shift | Automation reduces exceptions; re-deploy to value-add |
| Suppliers (top 200) | 200 | Scorecard pressure | Transparent criteria; development support |
| IT | 30 | Integration risk | Architecture forums; joint test team |
| Internal Audit | 10 | Control adequacy | SoD controls documented; audit trail complete |

### Communication Plan

- **Week 0**: Programme launch announcement from CPO via all-hands video
- **Week 8**: AS-IS findings shared with all stakeholders (transparency builds trust)
- **Week 20**: First dashboard demo — show spend visibility in action
- **Week 36**: Go-live countdown communication series (4 weekly newsletters)
- **Week 37**: Go-live day communications (site managers, help desk activation)
- **Week 52**: 6-month review: savings delivered, STP rate, lessons learned
- **Ongoing**: Monthly "Procurement Pulse" newsletter from CoE

---

## KPIs & Success Metrics

| KPI | Baseline | Year 1 Target | Year 2 Target | Measurement Method |
|-----|----------|--------------|--------------|-------------------|
| STP Rate (% POs auto-posted) | 35% | 65% | 80% | SAP workflow stats |
| PO Cycle Time (days) | 8.5 days | 4 days | 2.5 days | PR creation to PO issue date |
| Contract Coverage (% spend) | 58% | 75% | 85% | Contracted PO value / total PO value |
| Maverick Spend % | 22% | 12% | 8% | Off-contract PO value / total |
| Invoice Exception Rate | 18% | 8% | 4% | Exceptions / total invoices |
| Duplicate Invoice Rate | 0.8% | 0.2% | 0.1% | Duplicate invoices / total |
| Supplier OTD | 87% | 91% | 95% | GR date vs PO delivery date |
| Cost Savings (% addressable spend) | 1.2% | 3.0% | 4.5% | Savings tracker vs baseline |
| Spend Classification Accuracy | 71% | 88% | 93% | Sample audit vs ML auto-class |
| Fraud Alerts (Precision@100) | N/A | 35% | 50% | AP team review of flags |
| Commodity Forecast MAPE | N/A | ≤ 20% | ≤ 15% | Walk-forward validation |
| Supplier Scorecard Coverage | 40% | 80% | 95% | Suppliers scored / total active |

---

## Risk & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Data quality too poor for ML models | High | High | Phase 0 data audit; remediation sprint before ML training |
| Supplier resistance to Ariba Network | Medium | High | Dedicated supplier enablement team; phased onboarding |
| SAP integration delays (IDOC/BAPI errors) | Medium | High | Dedicated SAP integration consultant; mock environment testing |
| Change resistance from buyers (job fear) | High | Medium | Re-skilling programme; communicate elevated role |
| DistilBERT false positives damage supplier relationships | Medium | High | Human review gate before supplier notification |
| Commodity forecast accuracy insufficient for hedging | Medium | Medium | Use as directional guidance only; combine with trader expert judgement |
| Isolation Forest high false-positive rate | Medium | Medium | Tune contamination parameter; 2-tier alert system |
| GDPR: processing supplier personal data in ML models | Low | High | DPA with all data processors; anonymise personal data in training sets |
| Budget overrun on implementation | Medium | Medium | Fixed-price contracts for Phase 0–2; CoE internalised from Phase 3 |
| DoA matrix not aligned across 40 countries | High | Medium | Standardise globally with local legal approval process |

---

## Implementation Timeline

| Phase | Weeks | Key Deliverables | Owner |
|-------|-------|-----------------|-------|
| Phase 0: AS-IS Assessment | 1–8 | Stakeholder map, data quality audit, KPI baseline, gap analysis report | External consultant + CoE Director |
| Phase 1: Foundation | 9–20 | Master data model, SAP configuration, data migration, user roles | SAP consultants + IT |
| Phase 2: Standardisation | 21–36 | SOPs, dashboards, training, go-live | CoE + Category Managers |
| Phase 3: Math Models | 37–44 | EOQ deployed, TCO template, scorecard model live | Data Engineering + CoE Analytics |
| Phase 4: ML/AI Pipeline | 45–60 | All 5 ML models trained, validated, and in production | Data Science team |
| Phase 5: Integration | 53–72 | Full EDI coverage top-200 suppliers, all APIs live, event-driven workflows | IT + SAP + Data Engineering |
| Phase 6: CoE | 73+ | CoE operational, governance cadence, continuous improvement | CoE Director (permanent) |

Note: Phases 3, 4, and 5 overlap intentionally. Math model deployment (Phase 3)
can begin while Phase 2 training is completing. ML model development (Phase 4) can
begin in parallel with Phase 3.

---

## References

### Standards & Regulations
- GS1 General Specifications v23.0 — GTIN, GLN, SSCC, UOM codes
- ISO 28000:2022 — Supply Chain Security Management Systems
- ISO 9001:2015 §8.4 — Control of externally provided processes, products and services
- Incoterms® 2020 — ICC Publication 723E
- UN/EDIFACT D.01B — ORDERS, INVOIC, DESADV, RECADV, REMADV message standards
- EU Directive 2024/1760 (CSDDD) — Corporate Sustainability Due Diligence
- US Pub.L. 117-78 (UFLPA) — Uyghur Forced Labor Prevention Act
- APQC Open Standards Benchmarking — Procurement Process Framework
- SCOR Digital Standard (ASCM, 2019) — Source process model

### Academic & Industry Sources
- Chopra, S. & Meindl, P. (2016). *Supply Chain Management*, 6th ed. Pearson.
- Ballou, R.H. (2004). *Business Logistics/Supply Chain Management*, 5th ed. Pearson.
- Harris, F.W. (1913). "How Many Parts to Make at Once." *Factory: The Magazine of Management* 10(2):135–136.
- Sanh, V., et al. (2019). "DistilBERT, a distilled version of BERT." arXiv:1910.01108.
- Liu, F.T., Ting, K.M., & Zhou, Z.H. (2008). "Isolation Forest." *ICDM 2008.*
- Taylor, S.J., & Letham, B. (2018). "Forecasting at scale." *The American Statistician* 72(1):37–45.
- Jap, S.D. (2002). "Online reverse auctions: Issues, themes, and prospects for the future." *Journal of the Academy of Marketing Science* 30(4):506–525.
- APICS Dictionary, 16th ed. (ASCM, 2024).
- ICC Incoterms® 2020. International Chamber of Commerce, Publication 723E.
- UNSPSC Codeset v26.0 — United Nations Standard Products and Services Code.
- ECB Statistical Data Warehouse — Euro foreign exchange reference rates (free, SDMX API).
- World Bank Commodity Markets — monthly commodity price data (open access).
- Chen, T., & Guestrin, C. (2016). "XGBoost: A Scalable Tree Boosting System." *KDD 2016.*
- Ke, G., et al. (2017). "LightGBM: A Highly Efficient Gradient Boosting Decision Tree." *NeurIPS 2017.*
