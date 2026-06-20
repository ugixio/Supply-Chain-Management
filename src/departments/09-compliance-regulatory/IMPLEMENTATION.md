# Compliance & Regulatory — Enterprise Implementation Playbook

## Executive Summary

This playbook governs the end-to-end implementation of the Compliance & Regulatory department for a
€50B global multinational operating across 40 countries and managed on SAP S/4HANA. The scope
covers six primary regulatory frameworks — EU CSDDD 2024/1760, US UFLPA (Pub.L. 117-78),
EU REACH 1907/2006, UK Modern Slavery Act 2015 §54, German LkSG (Supply Chain Due Diligence Act
2023), and the Basel Convention on hazardous waste — plus horizontal obligations under GDPR as they
apply to supply chain data processing.

The implementation is structured across six phases spanning 80+ weeks. At full maturity the system
will deliver automated regulatory screening for 100% of Tier-1 suppliers and ≥80% of Tier-2
suppliers, real-time UFLPA exposure classification, NLP-driven contract compliance scanning, and a
Board-ready regulatory risk dashboard integrated with SAP GRC.

Estimated total cost of ownership: €8–12M over three years. Estimated penalty avoidance value:
€200–400M (based on CSDDD Art.22 civil liability exposure and US Customs seizure risk).

---

## Prerequisites & Dependencies

### Organisational Prerequisites
- Executive sponsor at Chief Compliance Officer (CCO) or General Counsel level
- Dedicated Compliance Centre of Excellence (CoE) team: minimum 6 FTE (2 legal, 2 data, 2 tech)
- Budget approved for Year 1 (€3–4M) covering software licences, data feeds, and consulting
- Data Privacy Officer (DPO) sign-off on supplier personal data processing under GDPR Art.6(1)(c)
  (legal obligation) and Art.6(1)(f) (legitimate interest for risk screening)

### Technical Prerequisites
- SAP S/4HANA 2023 or later with SAP GRC (Governance, Risk & Compliance) module active
- SAP Business Partner master data cleansed: DUNS numbers, country of origin, material group codes
- Python 3.11+ runtime environment with GPU access for NLP inference (NVIDIA A100 recommended)
- OpenSearch cluster (Apache-2.0) for sanctions list indexing and fuzzy matching
- Internal data lake (e.g., Apache Iceberg on MinIO) for regulatory document storage
- API connectivity to: UN Comtrade, EU ECHA SVHC Candidate List, OFAC SDN feed, EU Consolidated
  Sanctions List, BIS Entity List, UN Security Council Consolidated List

### Data Prerequisites
- Supplier master: BP number, legal name, registration country, ultimate parent DUNS
- Material master: chemical composition declarations (SDS), HS codes, country of origin
- Contract repository: accessible via document management system (ideally SAP DMS or OpenText)
- Historical PO data: last 5 years minimum (CSDDD Art.23 5-year retention requirement)

### Integration Dependencies
- SAP MM → compliance screening trigger on vendor creation/change (BAdI MM_VENDOR_MASTER)
- SAP EWM → REACH SVHC flag propagation to warehouse storage conditions
- SAP GTS (Global Trade Services) → Incoterms, HS code, country of origin synchronisation
- SAP MDG (Master Data Governance) → supplier data quality governance
- EDI partner onboarding → compliance gate before EDI activation

---

## Phase 0: AS-IS Assessment (Weeks 1–8)

### Week 1–2: Regulatory Landscape Mapping
- Inventory all applicable regulations by country of operation (40 countries × regulatory matrix)
- Create a Regulatory Applicability Matrix: rows = regulations, columns = countries/BUs, cells =
  APPLICABLE / PARTIAL / EXEMPT with effective dates
- Key regulations to map: CSDDD (EU member states, phased 2027–2029), UFLPA (US imports),
  REACH (EU + UK post-Brexit REACH), LkSG (German operations ≥1,000 employees), Modern Slavery
  Act (UK operations with ≥£36M turnover), Basel Convention (waste exporting countries)
- Identify regulatory conflicts (e.g., GDPR vs UFLPA information-sharing requirements)
- Deliverable: Regulatory Applicability Matrix v1.0 (Excel + SAP GRC upload)

### Week 3–4: Supplier Portfolio Assessment
- Extract full supplier list from SAP S/4HANA: target ~5,000–15,000 active vendors
- Classify by tier: Tier-1 (direct contracts), Tier-2 (known sub-suppliers), Tier-3 (unknown)
- Map to CSDDD in-scope criteria: Tier-1 companies with >500 employees and >€150M net turnover
  (Art.2, phased to SMEs from 2028)
- Flag all suppliers with ANY of: registered in XUAR adjacent provinces, materials in UFLPA
  priority sectors (cotton, polysilicon, aluminium, tomatoes, gloves), or chemicals with SVHC above
  threshold
- Run preliminary OFAC/EU sanctions screen (manual or via existing SAP GTS screen)
- Deliverable: Supplier Risk Pre-Classification Report

### Week 5–6: Process Gap Analysis
- Interview all regional compliance teams (Legal, Procurement, Quality, Logistics)
- Document current state: how is each regulation currently tracked? (Excel, email, manual?)
- Identify process gaps: missing UFLPA clearance documentation, expired REACH declarations,
  no CSDDD due diligence process for Tier-2+, no automated sanctions re-screening trigger
- Map data gaps: which supplier fields are missing in SAP BP master?
- Deliverable: AS-IS Process Map + Gap Analysis Report

### Week 7–8: Technology Assessment
- Assess SAP GRC current configuration: active modules, workflow capabilities, custom objects
- Evaluate current contract management tool for NLP readiness (API access to contract text)
- Assess data lake readiness for ML model training data storage
- Identify integration touchpoints: SAP GTS ↔ SAP MM ↔ SAP GRC ↔ external sanctions feeds
- Define data retention architecture aligned with CSDDD Art.23 (5 years), GDPR (purpose limitation)
- Deliverable: Technology Gap Assessment + Architecture Decision Record (ADR-001)

---

## Phase 1: Foundation & Master Data (Weeks 9–20)

### Week 9–10: SAP GRC Configuration — Compliance Objects
- Define custom risk object types in SAP GRC: UFLPA_RISK, CSDDD_DD, REACH_SUBSTANCE,
  SANCTIONS_SCREEN, MODERN_SLAVERY_RISK
- Configure regulatory control catalogue: map controls to SCOR-DS Enable processes
- Set up organisational hierarchy in SAP GRC mirroring the 40-country operating structure
- Configure role-based access: Compliance Analyst, Compliance Manager, CCO read-only dashboard

### Week 11–12: Supplier Master Data Enrichment
- Define mandatory compliance fields in SAP BP master (custom namespace ZCO_):
  - ZCO_UFLPA_RISK_SCORE (decimal 0–1)
  - ZCO_CSDDD_DD_STATUS (ENUM: NOT_STARTED / IN_PROGRESS / COMPLETED / REMEDIATION)
  - ZCO_REACH_DECLARATION_DATE (date)
  - ZCO_SANCTIONS_LAST_SCREEN (timestamp)
  - ZCO_MODERN_SLAVERY_STATEMENT_URL (string 255)
  - ZCO_LKSG_RISK_COUNTRY (boolean)
  - ZCO_XUAR_EXPOSURE (boolean)
- Configure SAP MDG workflow: any change to ZCO_ fields requires Compliance Analyst approval
- Initiate bulk enrichment campaign: send questionnaires to all Tier-1 suppliers (target: 100%
  response within 12 weeks)

### Week 13–14: Regulatory Data Feed Integration
- OFAC SDN List: automated daily download (US Treasury XML feed, Apache-2.0 tooling)
- EU Consolidated Sanctions List (CFSP): automated daily download (EUR-Lex API)
- BIS Entity List: automated weekly sync
- UN Security Council Consolidated List: automated daily sync
- EU ECHA SVHC Candidate List: automated sync on publication (typically 2× per year)
- US CBP UFLPA Entity List: automated daily sync
- Store all lists in OpenSearch with version history for audit trail
- Configure alerting: any list update triggers re-screen of affected vendor accounts

### Week 15–16: GDPR Data Processing Framework
- Document all supplier personal data processing in the Record of Processing Activities (RoPA)
- Legal basis per processing activity:
  - Sanctions screening: Art.6(1)(c) — legal obligation
  - UFLPA due diligence: Art.6(1)(c) — legal obligation (US trade law compliance)
  - CSDDD due diligence: Art.6(1)(c) — legal obligation (EU directive transposition)
  - Supplier risk scoring: Art.6(1)(f) — legitimate interest (supply chain risk management)
- Implement data minimisation: only collect supplier representative contact data necessary for DD
- Configure GDPR retention periods: sanctions screen logs = 7 years; DD records = 5 years (CSDDD)
- Draft and obtain DPA (Data Processing Agreement) templates for sub-processors (e.g., screening
  data providers)

### Week 17–18: REACH SVHC Master Data Setup
- Load EU ECHA SVHC Candidate List (currently 240+ substances) into material master extension
- For each finished good / semi-finished material: load Bill of Materials (BOM) substance data
- Configure SAP MM material classification: assign REACH_SVHC_FLAG, CAS_NUMBER, CONCENTRATION_PPW
- Build REACH substance roll-up report: for each article, sum SVHC concentration across all
  components (see Mathematical Models section for formula)
- Establish process for supplier SDS (Safety Data Sheet) upload and version control

### Week 19–20: Baseline KPI Measurement
- Run first UFLPA risk scoring pass across full supplier portfolio
- Compute CSDDD due diligence coverage ratio (baseline — expected: 5–20% for large companies)
- Run baseline sanctions screening: document all confirmed / potential matches
- Document all REACH SVHCs currently above 0.1% w/w threshold
- Publish baseline compliance scorecard to CCO and Board Audit Committee
- Deliverable: Compliance Baseline Report v1.0

---

## Phase 2: Process Standardisation (Weeks 21–36)

### Week 21–23: UFLPA Compliance Process
- Implement UFLPA Rebuttable Presumption workflow in SAP GRC:
  1. Trigger: material HS code in priority sectors AND supplier country includes CN province
  2. Auto-generate UFLPA clearance documentation checklist (CBP guidance dated Jan 2023)
  3. Required documents: supply chain map to raw material origin, traceability records, importer
     certifications, third-party audit reports
  4. Assign to Import Compliance team with 30-day SLA
  5. Block goods receipt in SAP EWM if UFLPA clearance not completed
- Configure SAP GTS customs procedure: UFLPA_HOLD status propagated to shipment documents
- Train Import Compliance team (8 hours): UFLPA statute, CBP enforcement priorities, documentation
  standards, Withhold Release Orders (WRO) process

### Week 24–26: CSDDD Due Diligence Process
- Implement CSDDD due diligence workflow aligned with EU Directive 2024/1760:
  - Art.5: integrate DD into company policies (link to Corporate Code of Conduct in SAP GRC)
  - Art.6: risk identification — map to supplier risk scoring (see Mathematical Models)
  - Art.7: risk prevention — contractual assurances, supplier questionnaire, on-site audits
  - Art.8: risk remediation — corrective action plans, supplier suspension workflow
  - Art.10: complaints mechanism — configure whistleblower intake in GRC (ISO 37002 aligned)
  - Art.11: monitoring — annual DD review cycle, triggered by risk score change >0.15
  - Art.23: documentation retention — 5-year archive in SAP DMS with legal hold capability
- Prioritise Tier-1 suppliers first (mandatory by 2027 for companies >€450M turnover)
- Deliverable: CSDDD Due Diligence Standard Operating Procedure (SOP-COMP-001)

### Week 27–28: REACH Compliance Process
- Implement REACH Article 33 duty-to-communicate process:
  - Trigger: any article leaving the facility where SVHC concentration > 0.1% w/w
  - Auto-generate Article 33 notification letter from SAP template
  - Send to downstream customers within 45 days of their request (Art.33(2))
- Implement REACH Article 7(2) registration notification:
  - Trigger: SVHC substance in article > 1 tonne/year AND concentration > 0.1% w/w
  - Notify ECHA within 6 months of threshold breach
- Configure import compliance: REACH applies to imports — require SDS from non-EU suppliers for
  all substances > 1 tonne/year
- Annual SVHC declaration renewal process: supplier questionnaire with digital signature

### Week 29–30: Modern Slavery Act & LkSG Process
- UK Modern Slavery Act §54:
  - Annual statement workflow: collect input from all UK operating entities, consolidate, obtain
    Board approval, publish on UK government registry by 30 September each year
  - Supplier questionnaire: modern slavery indicators per ILO forced labour indicators (11 items)
  - Risk assessment triggers: garment/textile, agriculture, construction, electronics sectors
- LkSG (German Supply Chain Act, effective since Jan 2023):
  - Applies to German operations ≥1,000 employees
  - Annual risk analysis: human rights + environmental risks in own operations + direct suppliers
  - Preventive measures: Code of Conduct, training, contractual assurances
  - Remediation: immediately effective corrective measures if violations identified
  - Reporting: annual report to BAFA (Federal Office for Economic Affairs and Export Control)
  - Complaints procedure: accessible to affected persons (not just employees)
- Configure SAP GRC: LkSG_RISK_STATUS field on supplier BP with annual review workflow

### Week 31–32: Basel Convention Process
- Identify all cross-border hazardous waste movements (Basel Convention, 1989)
- Configure SAP EWM waste classification: assign Basel waste codes to materials
- Prior Informed Consent (PIC) procedure workflow:
  - Notify competent authority in exporting country
  - Obtain written consent from importing country competent authority
  - Obtain consent from transit countries
  - Block shipment creation in SAP TM until PIC documentation complete
- Integrate with SAP DG (Dangerous Goods) module for hazmat classification
- Annual reporting to national competent authority (trans-boundary movement notifications)

### Week 33–34: Supplier Onboarding Compliance Gate
- Implement mandatory compliance gate in SAP MDG vendor creation workflow:
  1. Sanctions screening (automated, real-time via OpenSearch): BLOCK if confirmed match
  2. UFLPA entity list check (automated): FLAG if on CBP list
  3. CSDDD in-scope assessment: assign DD_REQUIRED flag if Tier-1 and above CSDDD threshold
  4. REACH declaration request: trigger if any procured material has chemical components
  5. Modern Slavery questionnaire: trigger if high-risk country or sector
  - Compliance gate SLA: 5 business days for standard vendors, 15 for high-risk
  - No purchase orders can be raised until compliance gate APPROVED status achieved

### Week 35–36: Regulatory Reporting Framework
- Configure automated regulatory reporting outputs:
  - CSDDD annual due diligence report (Art.11): structured data extraction from SAP GRC
  - LkSG BAFA annual report: German-language template auto-populated from GRC data
  - UK Modern Slavery statement: structured template with Board signature workflow
  - REACH SVHC notifications to ECHA: automated submission via ECHA REACH-IT API
  - US CBP UFLPA clearance documentation package: auto-assembled PDF from GRC attachments
- Configure Board Audit Committee dashboard: monthly compliance KPI pack (PowerPoint/SAP Analytics
  Cloud)

---

## Phase 3: Mathematical Models — Step-by-Step

### Model 1: UFLPA Risk Scoring

**Formula:**
```
uflpa_risk_score = (0.40 × country_risk) + (0.30 × material_risk)
                 + (0.20 × tier2_exposure) + (0.10 × cert_gap)
```

**Variable definitions:**
- `country_risk` (0–1): 1.0 = supplier registered in XUAR or known XUAR-adjacent province
  (Xinjiang, Gansu, Qinghai, Ningxia, Inner Mongolia); 0.7 = mainland China other province;
  0.3 = third country with known XUAR sourcing; 0.0 = no China nexus
- `material_risk` (0–1): mapped from HS code to UFLPA priority sector list:
  - Cotton (HS 52): 1.0
  - Polysilicon / solar (HS 2804.61, 8541.40): 1.0
  - Aluminium (HS 76): 0.9
  - Tomatoes (HS 0702): 0.8
  - Gloves / PPE (HS 4015): 0.8
  - Electronics with unknown component origin: 0.5
  - Non-priority sector: 0.0
- `tier2_exposure` (0–1): fraction of known Tier-2 suppliers with XUAR exposure > 0.5;
  if Tier-2 unknown: default 0.5 (conservative)
- `cert_gap` (0–1): 1 - (certifications_provided / certifications_required); certifications
  required = [supply_chain_map, traceability_records, importer_cert, third_party_audit]

**Flagging rule:**
```
if uflpa_risk_score > 0.70:
    status = "HIGH_RISK"  # require full CBP clearance package before import
elif uflpa_risk_score > 0.40:
    status = "MEDIUM_RISK"  # enhanced due diligence, annual audit
else:
    status = "LOW_RISK"  # standard monitoring
```

**Implementation (Python):**
```python
# python/09_compliance/uflpa_risk_scorer.py
import numpy as np
from dataclasses import dataclass
from typing import Literal

@dataclass
class UFLPARiskInput:
    country_risk: float      # 0.0 – 1.0
    material_risk: float     # 0.0 – 1.0
    tier2_exposure: float    # 0.0 – 1.0
    cert_gap: float          # 0.0 – 1.0

WEIGHTS = {
    "country_risk":   0.40,
    "material_risk":  0.30,
    "tier2_exposure": 0.20,
    "cert_gap":       0.10,
}

def compute_uflpa_score(inp: UFLPARiskInput) -> dict:
    """
    Compute UFLPA weighted risk score per CBP guidance (Jan 2023).
    Returns score (0–1) and risk classification.
    """
    score = (
        WEIGHTS["country_risk"]   * inp.country_risk +
        WEIGHTS["material_risk"]  * inp.material_risk +
        WEIGHTS["tier2_exposure"] * inp.tier2_exposure +
        WEIGHTS["cert_gap"]       * inp.cert_gap
    )
    if score > 0.70:
        classification = "HIGH_RISK"
    elif score > 0.40:
        classification = "MEDIUM_RISK"
    else:
        classification = "LOW_RISK"
    return {"score": round(score, 4), "classification": classification}
```

**SAP Integration:** Score written to ZCO_UFLPA_RISK_SCORE on BP master via RFC call from Python
microservice. Refresh triggered nightly and on any master data change event (SAP Change Document).

---

### Model 2: CSDDD Due Diligence Coverage Ratio

**Formula:**
```
dd_coverage_ratio = (DDs_completed / total_in_scope_suppliers) × 100
```

**In-scope supplier definition (Art.2, Dir. 2024/1760):**
- Phase 1 (2027): EU companies > 5,000 employees AND > €1.5B net turnover
- Phase 2 (2028): EU companies > 3,000 employees AND > €900M net turnover
- Phase 3 (2029): EU companies > 1,000 employees AND > €450M net turnover
- Non-EU companies with EU-generated net turnover exceeding the same thresholds

**DD completion criteria (all must be TRUE):**
1. Supplier questionnaire received and validated
2. Risk assessment completed (inherent risk score computed)
3. If risk > threshold: corrective action plan agreed
4. Contractual DD clauses signed
5. Evidence archived with date stamp

**Minimum targets:**
- Tier-1 suppliers: 100% coverage by applicable phase deadline
- Tier-2 suppliers: ≥60% of spend-weighted portfolio by 2029
- Board reporting: monthly trend chart with RAG status vs target

---

### Model 3: REACH SVHC Substance Tracking

**Formula (per finished article):**
```
svhc_concentration_article = ∑(substance_concentration_i × component_weight_i) / article_total_weight
```

**Flagging rule:**
```
if svhc_concentration_article > 0.001 (0.1% w/w):
    trigger_art33_notification = True   # duty to communicate
if svhc_annual_volume_kg > 1000 AND svhc_concentration_article > 0.001:
    trigger_echa_notification = True    # Art.7(2) registration
```

**Data model:**
- `substance_concentration_i`: SVHC mass fraction in component i (decimal, e.g., 0.005 = 0.5%)
- `component_weight_i`: weight of component i in the finished article (grams)
- `article_total_weight`: sum of all component weights (grams)

**Implementation note:** BOM must be fully exploded to raw material level. For purchased components
with unknown compositions, default to conservative assumption: request SDS from supplier and hold
procurement if SDS not received within 30 days.

---

### Model 4: Compliance Cost-Benefit NPV

**Formula:**
```
NPV_compliance = -C₀ + ∑_{t=1}^{T} [P(violation_t) × penalty_t - operating_cost_t] / (1+r)^t
```

**Where:**
- `C₀`: upfront compliance investment (system implementation, training, FTE)
- `P(violation_t)`: estimated probability of regulatory violation in year t if NOT compliant
- `penalty_t`: expected penalty amount (€) if violation occurs
- `operating_cost_t`: annual operating cost of compliance programme in year t
- `r`: discount rate (WACC, typically 8–10% for large multinationals)
- `T`: planning horizon (typically 7–10 years for regulatory investments)

**Reference penalty amounts (2024):**
- CSDDD Art.22: civil liability + Art.20 administrative fines up to 5% global net turnover
- REACH Art.126: member-state fines (Germany: up to €50,000 per substance breach)
- UK Modern Slavery Act: unlimited fine for non-publication of statement
- LkSG §24: fines up to €800,000; for revenues >400M, up to 2% of global annual turnover
- UFLPA: seizure of goods + 20% bond of value + reputational damage (unquantified)

---

### Model 5: Supplier Compliance Score

**Formula:**
```
compliance_score = gate_score × 100 × weighted_sub_score
```

**Binary gates (all must pass; any FAIL → score = 0, vendor BLOCKED):**
- `no_uflpa_entity_list`: supplier NOT on CBP UFLPA Entity List
- `no_sanctions_match`: confirmed CLEAR on OFAC/EU/UN sanctions screens
- `no_cites_violation`: no CITES (wildlife trade) violation flags
- `no_active_debarment`: not debarred from US Federal procurement

**Weighted sub-scores (only computed if all gates PASS):**
```
weighted_sub_score =
    0.30 × csddd_dd_completion    +  # 0=not started, 0.5=in progress, 1=complete
    0.25 × reach_declaration_current +  # 1=valid, 0.5=expired <1yr, 0=missing
    0.20 × modern_slavery_score   +  # 0–1 from ML model (see Phase 4)
    0.15 × lksg_risk_score        +  # 0–1 inverse of LkSG risk
    0.10 × audit_recency           # 1=audit <1yr, 0.5=1-3yr, 0=none
```

**Rating scale:**
- COMPLIANT_PREFERRED: ≥90
- COMPLIANT_STANDARD: ≥70
- COMPLIANT_CONDITIONAL: ≥50 (remediation plan required)
- NON_COMPLIANT: <50 (procurement hold)
- BLOCKED: any binary gate failure

---

## Phase 4: ML/AI Pipeline — Step-by-Step

### Model 1: NLP Contract Clause Compliance (DistilBERT)

**Objective:** Automatically scan all supplier contracts (PDF/Word) and flag contracts missing
mandatory CSDDD and UFLPA clauses.

**Architecture:**
```
Contract PDF → OCR (pytesseract) → text chunking (512 tokens) →
DistilBERT fine-tuned classifier → clause presence probability per clause type →
SAP GRC annotation + alert if P(clause_present) < 0.85
```

**Training data:**
- Positive examples: contracts with confirmed CSDDD/UFLPA clauses (label per clause type)
- Negative examples: contracts without these clauses
- Recommended minimum: 2,000 labelled contracts (can start with 200 using active learning)
- Clause types to detect:
  - `CSDDD_AUDIT_RIGHT`: right to audit supplier operations
  - `CSDDD_CODE_OF_CONDUCT`: reference to binding Code of Conduct
  - `CSDDD_REMEDIATION_OBLIGATION`: obligation to remediate identified violations
  - `UFLPA_DISCLOSURE`: disclosure obligation for XUAR supply chain links
  - `UFLPA_TRACEABILITY`: traceability record-keeping obligation
  - `SANCTIONS_REPRESENTATION`: rep & warranty on non-sanctioned status
  - `MODERN_SLAVERY_CERTIFICATION`: annual modern slavery self-certification

**Implementation path:**
```bash
# python/09_compliance/contract_nlp/
# 1. Install dependencies (all OSI-licensed)
pip install transformers torch pytesseract pdfplumber

# 2. Fine-tune DistilBERT (huggingface/transformers, Apache-2.0)
# Base model: distilbert-base-uncased (MIT)
# Fine-tune on labelled clause dataset (multi-label classification)
# Training: ~2 hours on A100 GPU for 2,000 contracts

# 3. Deploy as FastAPI microservice (MIT)
# Endpoint: POST /api/v1/contract/scan
# Input: {contract_id, text_content}
# Output: {clauses_detected: [...], clauses_missing: [...], confidence_scores: {...}}

# 4. SAP integration: DMS trigger on contract upload → call microservice → write results to GRC
```

**Monitoring:** Track precision/recall on monthly holdout set. Retrain quarterly or when F1 drops
below 0.85. Log all inference results with model version for audit trail.

---

### Model 2: UFLPA Exposure Classifier (BERT)

**Objective:** Classify supplier descriptions, certifications, and questionnaire responses by
degree of Xinjiang exposure risk.

**Input features:**
- Free-text supplier description (company website scrape, questionnaire responses)
- Certificate text (ISO, SA8000, sedex, etc.)
- Product descriptions and HS code descriptions
- Geographic mentions in unstructured text

**Model:** BERT (bert-base-uncased, Apache-2.0 licence) fine-tuned as 3-class classifier:
- Class 0: NO_XUAR_NEXUS
- Class 1: POTENTIAL_XUAR_NEXUS (requires manual review)
- Class 2: LIKELY_XUAR_NEXUS (trigger full UFLPA clearance)

**Training data sources:**
- US CBP UFLPA Entity List companies (positive class 2)
- Publicly available Xinjiang supplier lists (Sheffield Hallam University research, BCI data)
- Known clean supplier certifications (negative class 0)
- Use data augmentation: back-translation to increase training size

**Deployment:** Batch scoring nightly across all active suppliers. Real-time scoring on new
supplier onboarding. Results written to ZCO_UFLPA_BERT_CLASS on BP master.

---

### Model 3: Sanctions Screening (Fuzzy Matching + BERT NER)

**Objective:** Screen supplier legal names (and key individuals) against OFAC, EU, UN sanctions
lists with high recall and manageable false positive rate.

**Two-stage pipeline:**
```
Stage 1 — Candidate generation (high recall):
  - Levenshtein distance ≤ 2 on tokenised name (opensearch fuzzy query)
  - Phonetic matching (Metaphone / Double Metaphone)
  - Abbreviation expansion (Ltd→Limited, GmbH→Gesellschaft mit beschränkter Haftung)
  Output: candidate set (target recall > 99.9%)

Stage 2 — Entity disambiguation (high precision):
  - BERT NER extracts person/org/country from surrounding context
  - Rule-based deconfliction: country mismatch, industry mismatch, DOB mismatch
  - XGBoost binary classifier: P(true_match) from name similarity features + context features
  - Threshold: flag if P(true_match) > 0.60 for human review; auto-block if > 0.95
```

**False positive management:**
- Maintain allowlist of confirmed clear matches (with analyst initials, date, evidence)
- Re-screen allowlisted entities monthly (sanctions lists change)
- All blocks are logged with reason code (OFAC / EU / UN / BIS / UFLPA) for audit

**SLA:** New suppliers: screen within 4 hours. List update: re-screen full portfolio within 24h.

---

### Model 4: Modern Slavery Risk Scoring (XGBoost)

**Objective:** Predict probability of modern slavery risk in supplier operations, enabling
risk-proportionate due diligence.

**Features (all available from SAP BP master + external data):**
- `country_of_registration`: one-hot encoded; ILO 2022 forced labour prevalence index
- `industry_sector_code`: NACE Rev.2 code; high-risk sectors = garment, agriculture, construction
- `number_of_employees`: proxy for audit visibility
- `has_sa8000_cert`: binary (Social Accountability International)
- `has_sedex_membership`: binary
- `has_fair_trade_cert`: binary
- `migrant_worker_proportion_declared`: numeric (from questionnaire)
- `recruitment_fee_policy`: binary (no fee charging = 1)
- `freedom_of_association_policy`: binary
- `grievance_mechanism_exists`: binary
- `country_ilo_convention_ratifications`: count of ratified ILO core conventions

**Target variable:** Modern slavery confirmed incident (from audit reports, NGO databases,
court records) — binary label

**Training data:** Minimum 5,000 labelled supplier records. Source from: Business & Human Rights
Resource Centre database, Walk Free Foundation datasets, internal audit findings.

**Model performance target:** AUC ≥ 0.80, Precision@top_10% ≥ 0.60

**Explainability:** SHAP values computed for each prediction. Top-3 risk drivers shown to
Compliance Analyst in SAP GRC risk detail screen.

---

### Model 5: Regulatory Change Monitoring (NLP News Classifier)

**Objective:** Detect new regulations, enforcement actions, and regulatory guidance that affect
supply chain compliance. Auto-update risk registry when new requirements detected.

**Data sources (all open access):**
- EUR-Lex new legislation feed (RSS + API)
- Federal Register (US): daily XML feed
- UK Legislation.gov.uk: new statutory instruments feed
- OFAC press releases RSS
- EU ECHA press releases
- Financial Times, Reuters, Bloomberg Law: web scrape via BeautifulSoup (MIT)
- UN press releases

**Pipeline:**
```
Raw text feed → language detection (langdetect, LGPL) →
translation to English (Helsinki-NLP/opus-mt models, MIT) →
DistilBERT classifier → relevance_score (0–1) per supply chain domain →
if relevance_score > 0.80: create GRC risk item (REGULATORY_CHANGE type) →
notify Compliance team → human review within 5 business days
```

**Domain taxonomy for classification:**
- FORCED_LABOUR (UFLPA, LkSG, CSDDD human rights)
- CHEMICAL_SUBSTANCE (REACH, RoHS, PFAS)
- SANCTIONS (OFAC, EU, UN)
- TRADE_COMPLIANCE (customs, tariffs, export control)
- ENVIRONMENTAL (Basel, CBAM, SEC climate disclosure)
- DATA_PROTECTION (GDPR, national implementations)

**Monitoring cadence:** Hourly fetch for sanctions and enforcement actions;
daily for legislative sources.

---

## Phase 5: Integration & Automation (Weeks 53–72)

### Week 53–56: SAP GRC ↔ ML Model Integration
- Deploy all 5 ML microservices on Kubernetes cluster (Apache-2.0 tooling)
- Implement event-driven integration: SAP ABAP publishes events to Apache Kafka
  (Apache-2.0) → Python consumers → results written back via SAP OData API
- Implement circuit breaker pattern (Resilience4j concept in Python): if ML service unavailable,
  fall back to rule-based scoring with alert
- Configure dead-letter queue: failed scoring requests retried up to 3×, then escalate

### Week 57–60: SAP GTS Integration (Trade Compliance)
- Integrate UFLPA risk score into SAP GTS customs procedure determination
- Configure SAP GTS licence management for REACH restricted substances
- Automate HS code validation: flag HS codes in UFLPA priority sectors for enhanced screening
- Configure dual-use export control check (EAR/ITAR for US exports): auto-check on outbound
  shipment creation in SAP TM

### Week 61–64: Automated Compliance Reporting
- Build SAP Analytics Cloud (SAC) compliance dashboard:
  - Real-time UFLPA risk portfolio heatmap by supplier/commodity/country
  - CSDDD DD coverage trend (% complete by Tier, by phase deadline)
  - REACH SVHC exposure map (articles at risk by product line)
  - Sanctions screening queue (pending reviews, avg resolution time)
  - Modern Slavery risk distribution by supplier tier
- Configure automated Board pack: monthly PDF export from SAC with prior period comparison
- Configure regulatory deadline calendar: auto-remind 90/60/30/7 days before each deadline

### Week 65–68: Contract Lifecycle Management Integration
- Integrate NLP contract scanner with CLM system (e.g., SAP Ariba Contracts)
- Trigger NLP scan on every new/renewed contract before signature workflow reaches CCO
- Flag missing clauses as amendment requirements before execution
- Build clause library: standard CSDDD/UFLPA/REACH contract language templates

### Week 69–72: End-to-End Testing & Go-Live Preparation
- Parallel run: automated screening vs manual process for 8 weeks
- Measure: false positive rate (target <5% on sanctions screening)
- Measure: false negative rate (critical — target 0% on confirmed sanctions matches)
- User acceptance testing with Compliance, Legal, Procurement, and Audit teams
- Penetration testing of all API endpoints (supplier data is GDPR personal data)
- Go-live cutover plan: phased by region (EU first, then US, then APAC)

---

## Phase 6: Continuous Improvement & CoE

### Compliance Centre of Excellence (CoE) Structure
- **CCO** (Executive Sponsor, 20% time)
- **Head of Trade Compliance** (1.0 FTE, manages UFLPA/sanctions/GTS)
- **Head of ESG Compliance** (1.0 FTE, manages CSDDD/LkSG/Modern Slavery)
- **REACH/Chemical Specialist** (1.0 FTE)
- **Compliance Data Analyst** (2.0 FTE, model monitoring, data quality)
- **ML Engineer** (1.0 FTE, model retraining, pipeline maintenance)

### Ongoing Model Governance
- Monthly model performance review: AUC, precision/recall, false positive rate per model
- Quarterly retraining: incorporate new labelled data, regulatory list updates
- Annual model audit: third-party review of algorithmic bias and accuracy
- Model cards maintained (following Hugging Face model card standard): document training data,
  intended use, limitations, performance metrics

### Regulatory Horizon Scanning
- Quarterly regulatory horizon scan report published to CCO and Board
- Topics to monitor: EU CSDDD secondary legislation (delegated acts), CBAM (Carbon Border
  Adjustment Mechanism), US PROVE IT Act, EU Ecodesign for Sustainable Products Regulation (ESPR),
  UK CSDDD equivalent (currently voluntary, may become mandatory)

### Supplier Development Programme
- Top 50 suppliers by spend: annual compliance clinic (half-day workshop)
- Compliance scorecard included in annual supplier business review
- Remediation support: provide template corrective action plans, connect suppliers with
  approved third-party auditors (SA8000, Better Work, Sedex)

---

## Technology Stack & Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    SAP S/4HANA Core                                  │
│  SAP MM (vendor master)  │  SAP GRC (risk/compliance)               │
│  SAP GTS (trade)         │  SAP DMS (document archive)              │
│  SAP MDG (master data)   │  SAP Analytics Cloud (dashboards)        │
└────────────────┬────────────────────────────────────────────────────┘
                 │ OData / RFC / iDoc / Kafka events
┌────────────────▼────────────────────────────────────────────────────┐
│              Integration Middleware (Apache Kafka, Apache-2.0)       │
└────────────────┬────────────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────────────┐
│              ML Microservices (Python 3.11, FastAPI MIT)             │
│  /contract-nlp   (DistilBERT)    │  /uflpa-classifier  (BERT)       │
│  /sanctions-screen (fuzzy+BERT)  │  /modern-slavery    (XGBoost)    │
│  /reg-monitor    (DistilBERT)    │                                   │
└────────────────┬────────────────────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────────────────────┐
│              Data Layer                                              │
│  OpenSearch (sanctions lists)    │  Apache Iceberg (document lake)  │
│  PostgreSQL (model outputs)      │  MinIO (model artefacts)         │
└─────────────────────────────────────────────────────────────────────┘
External feeds: OFAC XML, EUR-Lex API, ECHA REACH-IT, CBP UFLPA list, BIS Entity List
```

**All components OSI-licensed.** No proprietary screening vendors unless explicitly approved by
Architecture Review Board with OSI-equivalent SLA commitments.

---

## Change Management & Training

### Stakeholder Communication Plan
- **Board/Audit Committee**: quarterly compliance dashboard presentation (30 min)
- **CEO/CFO**: penalty exposure NPV briefing at project kickoff and annually
- **Procurement**: new supplier onboarding compliance gate training (mandatory, 4 hours)
- **Legal**: CSDDD due diligence methodology training (mandatory, 8 hours)
- **Finance**: GDPR data processing obligations for supplier data (2 hours)
- **Warehouse/Logistics**: REACH SVHC labelling and Basel Convention waste handling (3 hours)

### Training Curriculum
| Audience | Module | Duration | Delivery | Frequency |
|----------|--------|----------|----------|-----------|
| All procurement staff | UFLPA basics + compliance gate | 4h | e-Learning | Onboarding + annual |
| Legal team | CSDDD due diligence deep-dive | 8h | Instructor-led | Annual |
| Compliance analysts | ML model interpretation + GRC | 16h | Instructor-led | Once + quarterly |
| Warehouse staff | REACH SVHC + hazmat handling | 3h | e-Learning | Annual |
| Finance staff | Compliance cost tracking | 2h | e-Learning | Annual |
| Senior management | Regulatory liability overview | 2h | Briefing | Annual |

### Resistance Management
- Anticipated resistance: procurement teams perceiving compliance gate as deal-blocker
- Mitigation: fast-track SLA (4-hour screening for urgent POs), dedicated compliance hotline,
  show penalty avoidance ROI, involve procurement champions in design sprints

---

## KPIs & Success Metrics

| KPI | Definition | Baseline | Year 1 Target | Year 3 Target |
|-----|-----------|----------|--------------|--------------|
| UFLPA Clearance Rate | % shipments with complete clearance docs | <20% | 80% | 100% |
| CSDDD DD Coverage — Tier-1 | % Tier-1 suppliers with completed DD | <10% | 60% | 100% |
| CSDDD DD Coverage — Tier-2 | % Tier-2 suppliers with completed DD | <5% | 30% | 60% |
| Sanctions Screen SLA | % screens completed within 4 hours | Unknown | 95% | 99% |
| Sanctions False Positive Rate | False alerts / total alerts | Unknown | <10% | <5% |
| REACH SVHC Declarations Current | % materials with valid SDS | <50% | 80% | 100% |
| Compliance Gate Pass Rate | % new vendors cleared within 5 days | Unknown | 85% | 95% |
| Contract Clause Coverage | % contracts with mandatory CSDDD clauses | <30% | 70% | 100% |
| Regulatory Deadline Compliance | % deadlines met on time | <80% | 95% | 100% |
| Modern Slavery Statement Published | Annual statement on UK registry | Manual | Automated | Automated |
| LkSG BAFA Report Submitted | Annual report on time | Manual | On time | On time |
| Compliance Score — Portfolio Avg | Average supplier compliance score 0–100 | Unknown | 65 | 80 |
| Penalty Exposure Reduction | € reduction in estimated penalty exposure | €0 | €50M | €200M |

---

## Risk & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| CSDDD transposition delays across 27 EU member states | Medium | Medium | Monitor national transposition; apply strictest standard proactively |
| UFLPA enforcement escalation (more priority sectors added) | High | High | Quarterly CBP guidance review; expand screening scope proactively |
| ML model false negatives on sanctions screening | Low | Critical | Multi-list redundancy; conservative threshold; manual quarterly audit |
| Supplier data quality too poor for UFLPA scoring | High | High | MDG data quality programme; penalise incomplete data in scorecard |
| GDPR conflict with UFLPA information sharing | Medium | Medium | DPO sign-off; Art.6(1)(c) legal obligation basis documented |
| Contract NLP model missing novel clause language | Medium | Medium | Quarterly retraining; human review fallback for low-confidence outputs |
| LkSG BAFA enforcement action (fines up to 2% revenue) | Low | Critical | Prioritise German supply chain DD; engage BAFA directly for guidance |
| REACH SVHC list expansion affecting major product lines | Medium | High | Horizon scanning model; proactive supplier substitution programme |
| SAP GRC customisation scope creep | High | Medium | Strict change control; freeze configuration at Phase 2 exit |
| Supplier refusal to provide CSDDD documentation | Medium | High | Contractual obligation; escalation path to supplier discontinuation |

---

## Implementation Timeline

| Phase | Weeks | Key Deliverables | Budget (€M) |
|-------|-------|-----------------|-------------|
| 0 — AS-IS Assessment | 1–8 | Regulatory Matrix, Gap Analysis, Tech Assessment | 0.3 |
| 1 — Foundation & Master Data | 9–20 | SAP GRC config, BP enrichment, data feeds live | 1.2 |
| 2 — Process Standardisation | 21–36 | All 6 regulatory processes live, reporting framework | 1.5 |
| 3 — Mathematical Models | 37–44 | UFLPA scorer, CSDDD ratio, REACH tracker, NPV model | 0.5 |
| 4 — ML/AI Pipeline | 45–52 | All 5 ML models trained and deployed | 2.0 |
| 5 — Integration & Automation | 53–72 | Full SAP integration, automated dashboards, UAT, go-live | 2.5 |
| 6 — CoE & Continuous Improvement | 73+ | Ongoing (quarterly retraining, horizon scanning, audits) | 1.5/yr |

**Total Year 1–2 investment: ~€8M. Estimated penalty avoidance over 5 years: €200–400M.**

---

## References

1. European Parliament and Council, Directive 2024/1760 on Corporate Sustainability Due Diligence
   (CSDDD), OJ L 2024/1760, 5 July 2024
2. US Congress, Uyghur Forced Labor Prevention Act, Pub.L. 117-78, enacted 23 December 2021
3. European Parliament and Council, Regulation (EC) No 1907/2006 concerning Registration,
   Evaluation, Authorisation and Restriction of Chemicals (REACH), OJ L 396, 30 December 2006
4. UK Parliament, Modern Slavery Act 2015, Chapter 30
5. German Federal Government, Lieferkettensorgfaltspflichtengesetz (LkSG), BGBl. I S. 2959,
   16 July 2021
6. United Nations, Basel Convention on the Control of Transboundary Movements of Hazardous Wastes
   and Their Disposal, 22 March 1989
7. European Parliament and Council, Regulation (EU) 2016/679 (GDPR), OJ L 119, 4 May 2016
8. US Customs and Border Protection, UFLPA Strategy and Operational Guidance, January 2023
9. EU ECHA, Guidance on requirements for substances in articles under REACH, Version 4.0, 2017
10. Walk Free Foundation, Global Slavery Index 2023
11. Sheffield Hallam University, In Broad Daylight: Uyghur Forced Labour and Global Solar Supply
    Chains, 2021
12. Devlin et al., BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding,
    arXiv:1810.04805, 2018
13. Sanh et al., DistilBERT: a distilled version of BERT, arXiv:1910.01108, 2019
