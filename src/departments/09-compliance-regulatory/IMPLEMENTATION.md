# Regulatory Compliance Analytics — Implementation Playbook
# Department 09 — Compliance & Regulatory

**Classification:** Internal — Restricted
**Version:** 2.0
**Date:** 2026-06-22
**Owner:** Chief Compliance Officer (CCO) / Chief Legal Officer (CLO)
**Reporting cadence:** Monthly to CSCO and CLO; Quarterly to Board Audit Committee

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Analysis Objective](#2-analysis-objective)
3. [Scope](#3-scope)
4. [Business Questions](#4-business-questions)
5. [Data Sources](#5-data-sources)
6. [Data Model](#6-data-model)
7. [Data Dictionary](#7-data-dictionary)
8. [Transformation Rules](#8-transformation-rules)
9. [Business Rules](#9-business-rules)
10. [KPIs and Formulas](#10-kpis-and-formulas)
11. [Analytical Logic](#11-analytical-logic)
12. [Validations and Controls](#12-validations-and-controls)
13. [Required Evidence](#13-required-evidence)
14. [Dashboard Design](#14-dashboard-design)
15. [Use Cases](#15-use-cases)
16. [Recommended Actions](#16-recommended-actions)
17. [Test Cases](#17-test-cases)
18. [Risks and Mitigations](#18-risks-and-mitigations)
19. [Implementation Checklist](#19-implementation-checklist)
20. [Validation Checklist](#20-validation-checklist)
21. [Pending Information](#21-pending-information)
22. [Implementation Roadmap](#22-implementation-roadmap)

---

## 1. Executive Summary

This playbook governs the Regulatory Compliance Analytics capability for a €50B multinational
operating across 40 countries. The analytics programme covers five core compliance domains:
UFLPA forced-labour risk exposure, CSDDD due-diligence coverage, REACH SVHC substance tracking,
sanctions screening, and compliance document expiry monitoring.

The system integrates SAP S/4HANA (supplier and material master), SAP GTS (Global Trade Services,
customs classification), and a compliance document management platform. Outputs are published
monthly to the Legal/Compliance team and Procurement, with executive summary packs delivered to
the CSCO and CLO.

**Business case summary:**
- Estimated penalty exposure (CSDDD Art.20 + UFLPA seizure + REACH Art.126): €200–400M over five years
- Estimated cost of analytics programme: €8–12M over three years
- Payback trigger: one avoided US Customs detention or one CSDDD civil liability suit

**Maturity targets:**
- Year 1: Tier-1 CSDDD coverage ≥60%, UFLPA scoring for 100% of high-risk HS codes
- Year 2: Tier-1 coverage 100%, Tier-2 coverage ≥40%, fully automated document expiry alerts
- Year 3: Tier-2 coverage ≥80%, NLP contract scanning live, real-time sanctions re-screening

---

## 2. Analysis Objective

The Regulatory Compliance Analytics programme addresses five analytical objectives:

1. **UFLPA Risk Exposure Dashboard:** Quantify and rank supplier-level Xinjiang forced-labour risk
   using a four-factor weighted score. Enable proactive CBP clearance preparation before goods
   arrive at US ports of entry.

2. **CSDDD Due Diligence Coverage:** Track the percentage of Tier-1 and Tier-2 suppliers for whom
   a complete EU CSDDD due-diligence process has been executed. Monitor progress against phased
   regulatory deadlines (2027/2028/2029).

3. **REACH SVHC Substance Tracking:** Calculate SVHC concentration at finished-article level
   (% w/w) across the full BOM. Track declaration completeness and ECHA notification obligations.

4. **Sanctions Screening Tracking:** Monitor screening coverage, queue age, false-positive rate,
   and confirmation-to-block SLA for all active suppliers across OFAC, EU Consolidated List, UN
   Security Council, and BIS Entity List.

5. **Compliance Document Expiry Monitoring:** Identify and escalate compliance certifications,
   declarations, and due-diligence records approaching or past their expiry date, segmented by
   document type, supplier tier, and urgency band.

---

## 3. Scope

### In Scope

| Dimension | Coverage |
|-----------|----------|
| Regulations | EU CSDDD 2024/1760, US UFLPA Pub.L.117-78, EU REACH 1907/2006, LkSG (Germany), UK Modern Slavery Act 2015 §54, Basel Convention |
| Supplier tiers | Tier-1 (direct contracts), Tier-2 (known sub-suppliers) |
| Geography | 40 countries of operation; all importing-into-US shipments |
| Materials | All purchased materials and components; SVHC-relevant articles |
| Systems | SAP S/4HANA, SAP GTS, compliance document management platform |
| Reporting cadence | Monthly operational reporting; quarterly Board pack |
| Stakeholders | Legal/Compliance, Procurement, Import Compliance, CSCO, CLO |

### Out of Scope

- Tier-3 and beyond (tracked as a risk flag, not in primary KPIs until Year 3)
- Export control / ITAR (handled by separate Export Controls workstream)
- Tax compliance and transfer pricing
- Environmental reporting (Scope 1/2/3 emissions — separate ESG programme)

---

## 4. Business Questions

The following twelve questions drive the analytical design:

1. What percentage of our Tier-1 suppliers have completed CSDDD due diligence, and which
   procurement categories are most exposed against the 2027 deadline?

2. Which suppliers carry the highest UFLPA risk score, and what specific factors (country risk,
   material risk, Tier-2 exposure, certification gap) drive their score?

3. How many of our finished articles contain SVHC substances above the 0.1% w/w threshold, and
   have all Art.33 downstream customer notifications been issued?

4. What is the current sanctions screening queue depth, and what is the average age of unresolved
   potential matches?

5. How many compliance documents (ISO certifications, REACH declarations, CSDDD questionnaires,
   modern slavery statements) expire within the next 30, 60, and 90 days?

6. What is the trend in CSDDD Tier-2 coverage over the past 12 months, and are we on track to
   reach ≥40% by end of Year 2?

7. Which supplier categories have the lowest sanctions clear rate, indicating data quality issues
   or genuine risk concentration?

8. What is the UFLPA high-risk supplier rate by commodity group (cotton, polysilicon, aluminium,
   gloves), and which commodity groups require immediate sourcing diversification?

9. How does our CSDDD due-diligence cost per supplier correlate with the inherent risk score, and
   where are we over- or under-investing in due-diligence effort?

10. What proportion of our import spend by value passes through countries with UFLPA priority-sector
    exposure, and what is the US CBP seizure exposure in EUR?

11. Are there patterns in compliance document expiry clustering (e.g., annual renewals for a
    specific supplier group all expiring in the same month), and how can renewal be staggered?

12. Which suppliers are flagged as HIGH risk on UFLPA scoring but have not yet provided any
    clearance documentation, and what is the combined annual import value at risk?

---

## 5. Data Sources

### DS-01: SAP S/4HANA Business Partner Master

| Attribute | Value |
|-----------|-------|
| Name | SAP Business Partner (BP) Master |
| System | SAP S/4HANA 2023 |
| Table / View | BUT000, BUT020, LFA1, LFAS, ZCO_BP_COMPLIANCE (custom extension) |
| Owner | Master Data Governance (MDG) team |
| Frequency | Real-time (change documents); daily full extract to analytics layer |
| Fields | BP number, legal name, registration country, DUNS, ultimate parent DUNS, tier classification, ZCO_UFLPA_RISK_SCORE, ZCO_CSDDD_DD_STATUS, ZCO_REACH_DECLARATION_DATE, ZCO_SANCTIONS_LAST_SCREEN, ZCO_XUAR_EXPOSURE flag, ZCO_LKSG_RISK_COUNTRY flag |
| Critical Fields | BP number (PK), ZCO_UFLPA_RISK_SCORE, ZCO_CSDDD_DD_STATUS |
| Primary Key | BP number (10-digit SAP internal) |
| Validations | ZCO_UFLPA_RISK_SCORE in [0,1]; ZCO_CSDDD_DD_STATUS in allowed ENUM; ZCO_SANCTIONS_LAST_SCREEN not null for active vendors |
| Known Errors | ~8% of BP records missing DUNS number (MDG remediation in progress); registration country blank for historical vendors |
| Evidence Required | SAP change document log; MDG governance workflow approval records |

---

### DS-02: SAP GTS Customs Classification

| Attribute | Value |
|-----------|-------|
| Name | SAP Global Trade Services — Material Classification |
| System | SAP GTS 13.0 |
| Table / View | /SAPSLL/PROD, /SAPSLL/PRODCL, /SAPSLL/CUSDECL |
| Owner | Trade Compliance team |
| Frequency | Daily sync from GTS to analytics layer |
| Fields | Material number, HS code (10-digit), country of origin (COO), UFLPA priority sector flag, REACH SVHC flag, export control classification (ECCN), Incoterm |
| Critical Fields | HS code, COO, UFLPA priority sector flag |
| Primary Key | Material number + HS code + COO |
| Validations | HS code must be 10 digits; COO must be valid ISO 3166-1 alpha-2; UFLPA priority sector flag must match HS code lookup table |
| Known Errors | ~3% of materials have generic COO = "XX" (unknown) — triggers conservative HIGH risk default |
| Evidence Required | GTS audit log; HS code reclassification workflow records |

---

### DS-03: Compliance Document Management Platform

| Attribute | Value |
|-----------|-------|
| Name | Compliance Document Repository (SAP DMS or OpenText) |
| System | SAP Document Management System (DMS) / OpenText |
| Table / View | DRAW, DRAD, SDOKDLINK (SAP DMS); custom document registry table ZCO_DOCREG |
| Owner | Compliance team |
| Frequency | Real-time upload; daily extract for analytics |
| Fields | Document ID, document type (ENUM: UFLPA_CLEARANCE, CSDDD_QUESTIONNAIRE, REACH_SDS, REACH_SVHC_DECL, SANCTIONS_SCREEN_LOG, MODERN_SLAVERY_STMT, ISO_CERT, SA8000_CERT, LKSG_ASSESSMENT), supplier BP, effective date, expiry date, version, uploaded by, approval status |
| Critical Fields | Document type, expiry date, supplier BP, approval status |
| Primary Key | Document ID (UUID) |
| Validations | Expiry date > effective date; approval status in [PENDING, APPROVED, REJECTED, EXPIRED]; document type in allowed ENUM |
| Known Errors | ~12% of legacy documents have null expiry date (treated as expiry = effective + 365 days by default rule) |
| Evidence Required | Document upload timestamp; digital signature of approving Compliance Analyst; version history |

---

### DS-04: Sanctions Screening Engine (OpenSearch)

| Attribute | Value |
|-----------|-------|
| Name | Sanctions Screening Result Log |
| System | OpenSearch 2.x (Apache-2.0) |
| Table / View | Index: sanctions_screen_results |
| Owner | Trade Compliance / Compliance Data Engineering |
| Frequency | Real-time on new vendor creation; daily batch for full portfolio re-screen; real-time trigger on list update |
| Fields | Screen ID (UUID), BP number, screen date, list screened (OFAC/EU/UN/BIS/UFLPA), match status (NO_MATCH / POTENTIAL_MATCH / CONFIRMED_MATCH / CLEARED), match score (0–1), analyst ID (if reviewed), resolution date, resolution notes, allowlist flag |
| Critical Fields | Match status, resolution date, list screened |
| Primary Key | Screen ID |
| Validations | match status must transition legally (NO_MATCH cannot move to CONFIRMED_MATCH without POTENTIAL_MATCH step); resolution date must be populated for CLEARED or CONFIRMED_MATCH statuses |
| Known Errors | Duplicate BP numbers from legacy ERP migration may generate duplicate screens — deduplication by BP + screen date |
| Evidence Required | Screen log with list version timestamp; analyst name and resolution rationale for CLEARED decisions |

---

### DS-05: REACH SVHC Material Data

| Attribute | Value |
|-----------|-------|
| Name | REACH SVHC Substance Registry and BOM Linkage |
| System | SAP MM (material master classification) + ECHA SVHC Candidate List (external feed) |
| Table / View | MARA, MARD, MLAN, KLAH, AUSP, ZCO_SVHC_BOM (custom BOM extension) |
| Owner | Chemical Compliance Specialist |
| Frequency | ECHA list: synced on publication (approx. 2× per year); BOM data: daily |
| Fields | Material number, CAS number, substance name, SVHC candidate list entry date, concentration_ppw (decimal fraction), component weight (grams), article total weight (grams), BOM level, Art.33 notification flag, Art.7(2) notification flag, annual volume (kg), SDS document ID |
| Critical Fields | CAS number, concentration_ppw, article total weight, Art.33 notification flag |
| Primary Key | Material number + CAS number |
| Validations | concentration_ppw in [0,1]; article total weight > 0; CAS number format valid (###-##-#) |
| Known Errors | Purchased components without supplier-provided SDS default to concentration_ppw = NULL (treated as worst-case 0.5 for risk scoring) |
| Evidence Required | Supplier SDS version date; ECHA SVHC Candidate List version; Art.33 notification letter sent timestamp |

---

### DS-06: SAP S/4HANA Purchase Order History

| Attribute | Value |
|-----------|-------|
| Name | Purchase Order Master and Line Items |
| System | SAP S/4HANA |
| Table / View | EKKO, EKPO, EKBE |
| Owner | Procurement |
| Frequency | Daily extract |
| Fields | PO number, vendor BP, material number, quantity, net value (EUR cents), COO, HS code, plant, document date, delivery date, goods receipt flag |
| Critical Fields | Vendor BP, material number, net value |
| Primary Key | PO number + line item |
| Validations | Net value in integer cents (no decimals); vendor BP must exist in BP master; material number must be active in material master |
| Known Errors | Historical POs pre-ERP migration may have legacy vendor codes not linked to current BP master |
| Evidence Required | SAP change document log; approval workflow records for POs above threshold |

---

## 6. Data Model

```
┌───────────────────────────────────────────────────────────────────────────────┐
│                        COMPLIANCE ANALYTICS DATA MODEL                        │
└───────────────────────────────────────────────────────────────────────────────┘

[BP_MASTER]  ─────────────────────────────────────────────────┐
  bp_number (PK)                                              │
  legal_name                                                  │ 1:N
  registration_country                                        │
  duns_number                                                 ▼
  tier_classification (TIER1/TIER2/TIER3)          [COMPLIANCE_DOCUMENT_REGISTRY]
  uflpa_risk_score (0–1)                             doc_id (PK, UUID)
  csddd_dd_status                                    bp_number (FK)
  reach_declaration_date                             doc_type
  sanctions_last_screen                              effective_date
  xuar_exposure (bool)                               expiry_date
  lksg_risk_country (bool)                           approval_status
  is_active (bool)                                   doc_version
  is_deleted (bool)                                  uploaded_by
                                                     approved_by
[BP_MASTER]  ─────────────────────────────────────────────────┐
  bp_number (FK)                                    │
                                                    │ 1:N
                                                    ▼
                                        [SANCTIONS_SCREEN_LOG]
                                          screen_id (PK, UUID)
                                          bp_number (FK)
                                          screen_date
                                          list_screened
                                          match_status
                                          match_score
                                          resolution_date
                                          analyst_id

[MATERIAL_MASTER] ────────────────────────────────────────────┐
  material_number (PK)                                        │
  hs_code                                          1:N        │
  country_of_origin                                           ▼
  uflpa_priority_sector (bool)              [SVHC_BOM_DETAIL]
  reach_svhc_flag (bool)                     record_id (PK)
  annual_volume_kg                           material_number (FK)
                                             cas_number (FK)
[SVHC_SUBSTANCE_LIST]                        concentration_ppw
  cas_number (PK)                            component_weight_g
  substance_name                             article_total_weight_g
  echa_candidate_list_date                   art33_notification_flag
  svhc_threshold_ppw (= 0.001)              art72_notification_flag
                                             sds_doc_id

[PO_HISTORY] ─────────────────────────────────────────────────┐
  po_number + line_item (PK)                                  │ N:1
  bp_number (FK)                            │
  material_number (FK)                      ▼
  net_value_eur_cents               [UFLPA_RISK_SCORING_LOG]
  document_date                      score_id (PK, UUID)
  hs_code                            bp_number (FK)
  country_of_origin                  material_number (FK)
                                     country_risk
                                     material_risk
                                     tier2_exposure
                                     cert_gap
                                     uflpa_score
                                     classification
                                     scored_at
                                     model_version

[CSDDD_DUE_DILIGENCE_REGISTER]
  dd_id (PK, UUID)
  bp_number (FK)
  tier (TIER1/TIER2)
  questionnaire_received (bool)
  risk_assessment_completed (bool)
  cap_agreed (bool)
  contractual_clauses_signed (bool)
  evidence_archived (bool)
  dd_status (NOT_STARTED/IN_PROGRESS/COMPLETED/REMEDIATION)
  completion_date
  next_review_date
  phase_applicability (PHASE1/PHASE2/PHASE3)
```

---

## 7. Data Dictionary

### Table: BP_COMPLIANCE_MASTER (analytical layer — merged view)

| Field | Data Type | Granularity | Description | PK | Relationships |
|-------|-----------|-------------|-------------|----|-|
| bp_number | VARCHAR(10) | Supplier | SAP Business Partner number | YES | FK in all compliance tables |
| legal_name | VARCHAR(255) | Supplier | Registered legal name | NO | Used in sanctions fuzzy match |
| registration_country | CHAR(2) | Supplier | ISO 3166-1 alpha-2 country code | NO | Used in UFLPA country_risk lookup |
| duns_number | VARCHAR(9) | Supplier | D&B DUNS number for parent linkage | NO | Ultimate parent DUNS for group screening |
| tier_classification | ENUM | Supplier | TIER1 / TIER2 / TIER3 | NO | CSDDD scope determination |
| uflpa_risk_score | DECIMAL(4,4) | Supplier | Weighted UFLPA score [0,1] | NO | Computed by Python scorer nightly |
| uflpa_classification | ENUM | Supplier | HIGH_RISK / MEDIUM_RISK / LOW_RISK | NO | Derived from uflpa_risk_score |
| csddd_dd_status | ENUM | Supplier | NOT_STARTED / IN_PROGRESS / COMPLETED / REMEDIATION | NO | Source for CSDDD coverage KPI |
| reach_declaration_date | DATE | Supplier | Date of most recent valid REACH/SDS declaration | NO | Used in document expiry alerts |
| sanctions_last_screen | TIMESTAMP | Supplier | UTC timestamp of most recent screen | NO | Used in screen age KPI |
| xuar_exposure | BOOLEAN | Supplier | TRUE if any Tier-1 or Tier-2 link to XUAR region | NO | Input to UFLPA tier2_exposure factor |
| lksg_risk_country | BOOLEAN | Supplier | TRUE if supplier operates in LkSG high-risk country | NO | LkSG scope flag |
| is_active | BOOLEAN | Supplier | FALSE = soft-deleted / inactive | NO | Exclude from denominator in coverage KPIs |
| is_deleted | BOOLEAN | Supplier | Soft-delete flag | NO | Never hard-deleted per business rules |

---

### Table: COMPLIANCE_DOCUMENT_REGISTRY

| Field | Data Type | Granularity | Description | PK | Relationships |
|-------|-----------|-------------|-------------|----|-|
| doc_id | UUID | Document | Surrogate key | YES | Referenced in CSDDD and UFLPA logs |
| bp_number | VARCHAR(10) | Document | Linked supplier | NO | FK to BP_COMPLIANCE_MASTER |
| doc_type | ENUM | Document | Document type code (see DS-03 for ENUM values) | NO | Drives expiry alert logic |
| effective_date | DATE | Document | Date from which document is valid | NO | Used in age calculation |
| expiry_date | DATE | Document | Date after which document is no longer valid | NO | Primary field for expiry KPI |
| days_to_expiry | INTEGER | Document | Computed: expiry_date - CURRENT_DATE | NO | Derived field; negative = already expired |
| approval_status | ENUM | Document | PENDING / APPROVED / REJECTED / EXPIRED | NO | Only APPROVED docs count toward coverage |
| uploaded_by | VARCHAR(50) | Document | User ID of uploader | NO | Audit trail |
| approved_by | VARCHAR(50) | Document | User ID of Compliance Analyst who approved | NO | Audit trail |

---

### Table: SANCTIONS_SCREEN_LOG

| Field | Data Type | Granularity | Description | PK | Relationships |
|-------|-----------|-------------|-------------|----|-|
| screen_id | UUID | Screen event | Surrogate key | YES | — |
| bp_number | VARCHAR(10) | Screen event | Screened supplier | NO | FK to BP_COMPLIANCE_MASTER |
| screen_date | TIMESTAMP | Screen event | UTC timestamp of screen execution | NO | Used in screen age and SLA KPIs |
| list_screened | ENUM | Screen event | OFAC / EU_CONSOLIDATED / UN_SC / BIS / UFLPA_ENTITY | NO | Multi-value (one row per list per screen) |
| match_status | ENUM | Screen event | NO_MATCH / POTENTIAL_MATCH / CONFIRMED_MATCH / CLEARED | NO | Drives the Sanctions Clear Rate KPI |
| match_score | DECIMAL(3,2) | Screen event | Fuzzy match confidence [0,1] | NO | Threshold: ≥0.60 triggers human review |
| resolution_date | TIMESTAMP | Screen event | UTC timestamp of analyst resolution | NO | Used in SLA compliance calculation |
| analyst_id | VARCHAR(50) | Screen event | Resolving analyst | NO | Audit trail |
| allowlist_flag | BOOLEAN | Screen event | TRUE = entity confirmed clear and added to allowlist | NO | Monthly re-screen required for allowlisted |

---

### Table: SVHC_BOM_DETAIL

| Field | Data Type | Granularity | Description | PK | Relationships |
|-------|-----------|-------------|-------------|----|-|
| record_id | BIGINT | Material × Substance | Surrogate key | YES | — |
| material_number | VARCHAR(18) | Material | SAP material number | NO | FK to MATERIAL_MASTER |
| cas_number | VARCHAR(12) | Substance | Chemical Abstracts Service number | NO | FK to SVHC_SUBSTANCE_LIST |
| concentration_ppw | DECIMAL(8,6) | Material × Substance | Mass fraction of substance in component (0–1) | NO | Threshold: > 0.001 triggers flags |
| component_weight_g | DECIMAL(12,3) | Material × Substance | Weight of component in finished article (grams) | NO | Used in rolled-up concentration calc |
| article_total_weight_g | DECIMAL(12,3) | Material | Total weight of finished article (grams) | NO | Denominator for concentration roll-up |
| svhc_conc_article_ppw | DECIMAL(8,6) | Material | Rolled-up SVHC concentration in finished article | NO | Derived field |
| art33_notification_flag | BOOLEAN | Material | TRUE = Art.33 duty-to-communicate triggered | NO | Drives declaration completeness KPI |
| art72_notification_flag | BOOLEAN | Material | TRUE = Art.7(2) ECHA registration triggered | NO | Annual volume check required |
| sds_doc_id | UUID | Material × Substance | FK to SDS document in COMPLIANCE_DOCUMENT_REGISTRY | NO | Validates declaration completeness |

---

### Table: CSDDD_DUE_DILIGENCE_REGISTER

| Field | Data Type | Granularity | Description | PK | Relationships |
|-------|-----------|-------------|-------------|----|-|
| dd_id | UUID | DD process | Surrogate key | YES | — |
| bp_number | VARCHAR(10) | Supplier | FK to BP_COMPLIANCE_MASTER | NO | FK |
| tier | ENUM | Supplier | TIER1 / TIER2 | NO | Determines coverage KPI denominator |
| questionnaire_received | BOOLEAN | DD process | All five DD completion criteria are checked separately | NO | Part of DD_COMPLETED logic |
| risk_assessment_completed | BOOLEAN | DD process | Inherent risk score has been computed | NO | Part of DD_COMPLETED logic |
| cap_agreed | BOOLEAN | DD process | Corrective action plan agreed (if risk above threshold) | NO | Conditional — only required if risk > 0.4 |
| contractual_clauses_signed | BOOLEAN | DD process | CSDDD contractual clauses executed | NO | Part of DD_COMPLETED logic |
| evidence_archived | BOOLEAN | DD process | Evidence stored in DMS with timestamp | NO | CSDDD Art.23 requirement |
| dd_status | ENUM | DD process | NOT_STARTED / IN_PROGRESS / COMPLETED / REMEDIATION | NO | Drives CSDDD coverage KPI |
| phase_applicability | ENUM | DD process | PHASE1 / PHASE2 / PHASE3 (regulatory deadline group) | NO | Used for trend-to-deadline tracking |
| completion_date | DATE | DD process | Date when dd_status became COMPLETED | NO | Used in trend charts |
| next_review_date | DATE | DD process | Annual review trigger date | NO | Alert generated 90 days before |

---

### Table: UFLPA_RISK_SCORING_LOG

| Field | Data Type | Granularity | Description | PK | Relationships |
|-------|-----------|-------------|-------------|----|-|
| score_id | UUID | Scoring event | Surrogate key | YES | — |
| bp_number | VARCHAR(10) | Supplier | FK to BP_COMPLIANCE_MASTER | NO | FK |
| material_number | VARCHAR(18) | Material | FK to MATERIAL_MASTER | NO | FK |
| country_risk | DECIMAL(3,2) | Scoring event | Country risk factor [0,1] | NO | See score formula |
| material_risk | DECIMAL(3,2) | Scoring event | Material / HS risk factor [0,1] | NO | See score formula |
| tier2_exposure | DECIMAL(3,2) | Scoring event | Tier-2 XUAR exposure fraction [0,1] | NO | Default 0.5 if unknown |
| cert_gap | DECIMAL(3,2) | Scoring event | Certification gap [0,1] = 1 - (docs_provided / docs_required) | NO | See score formula |
| uflpa_score | DECIMAL(4,4) | Scoring event | Final weighted score [0,1] | NO | Written back to BP master |
| classification | ENUM | Scoring event | HIGH_RISK / MEDIUM_RISK / LOW_RISK | NO | Drives dashboard red/amber/green |
| scored_at | TIMESTAMP | Scoring event | UTC timestamp of scoring run | NO | Used in model freshness monitoring |
| model_version | VARCHAR(20) | Scoring event | Version string of scoring model | NO | Model governance audit trail |

---

## 8. Transformation Rules

### TR-01: UFLPA Country Risk Mapping

Source: `BP_COMPLIANCE_MASTER.registration_country` + `GTS_CLASSIFICATION.country_of_origin`

```
country_risk =
  CASE
    WHEN country IN ('CN') AND province IN ('XJ','GS','QH','NX','NM') THEN 1.0  -- XUAR / adjacent
    WHEN country = 'CN' AND province NOT IN ('XJ','GS','QH','NX','NM') THEN 0.7
    WHEN country IN third_country_known_xuar_sourcing_list THEN 0.3
    ELSE 0.0
  END
```

Note: Province data is mapped from SAP GTS country-of-origin field using a lookup table maintained
by the Trade Compliance team. Where province is unknown, default = 0.5 (conservative).

---

### TR-02: UFLPA Material Risk Mapping

Source: `GTS_CLASSIFICATION.hs_code` (10-digit)

```
material_risk =
  CASE
    WHEN hs_code STARTS WITH '52'           THEN 1.0   -- Cotton
    WHEN hs_code IN ('2804.61','8541.40')   THEN 1.0   -- Polysilicon / solar cells
    WHEN hs_code STARTS WITH '76'           THEN 0.9   -- Aluminium
    WHEN hs_code = '0702'                   THEN 0.8   -- Tomatoes
    WHEN hs_code STARTS WITH '4015'         THEN 0.8   -- Gloves / PPE
    WHEN hs_code STARTS WITH '85' AND coo_unknown THEN 0.5   -- Electronics, unknown origin
    ELSE 0.0
  END
```

---

### TR-03: Certification Gap Calculation

Source: `COMPLIANCE_DOCUMENT_REGISTRY`

```
docs_required = ['UFLPA_SUPPLY_CHAIN_MAP', 'UFLPA_TRACEABILITY_RECORD',
                 'UFLPA_IMPORTER_CERT', 'UFLPA_THIRD_PARTY_AUDIT']

docs_provided = COUNT(doc_type IN docs_required
                      AND approval_status = 'APPROVED'
                      AND expiry_date >= CURRENT_DATE)

cert_gap = 1 - (docs_provided / 4)
```

---

### TR-04: REACH SVHC Article-Level Concentration Roll-Up

Source: `SVHC_BOM_DETAIL` — all BOM levels for a finished article

```
svhc_conc_article_ppw =
  SUM(concentration_ppw_i × component_weight_g_i) / article_total_weight_g

Art.33 trigger: svhc_conc_article_ppw > 0.001 (0.1% w/w)
Art.7(2) trigger: svhc_conc_article_ppw > 0.001 AND annual_volume_kg > 1000
```

---

### TR-05: CSDDD DD_COMPLETED Logic

Source: `CSDDD_DUE_DILIGENCE_REGISTER`

```
DD_COMPLETED =
  questionnaire_received = TRUE
  AND risk_assessment_completed = TRUE
  AND (cap_agreed = TRUE OR inherent_risk_score <= 0.40)   -- CAP only required if high risk
  AND contractual_clauses_signed = TRUE
  AND evidence_archived = TRUE
```

---

### TR-06: Document Expiry Days Calculation

Source: `COMPLIANCE_DOCUMENT_REGISTRY`

```
days_to_expiry = expiry_date - CURRENT_DATE   -- integer days; negative = already expired

urgency_band =
  CASE
    WHEN days_to_expiry < 0              THEN 'EXPIRED'
    WHEN days_to_expiry BETWEEN 0 AND 29 THEN 'CRITICAL'
    WHEN days_to_expiry BETWEEN 30 AND 59 THEN 'HIGH'
    WHEN days_to_expiry BETWEEN 60 AND 89 THEN 'MEDIUM'
    ELSE 'OK'
  END
```

---

### TR-07: Sanctions Clear Rate Denominator

Source: `SANCTIONS_SCREEN_LOG`

The denominator is ALL distinct active suppliers screened at least once in the past 90 days.
Suppliers not screened within 90 days are flagged as SCREENING_LAPSED (separate alert).

```
screened_count = COUNT(DISTINCT bp_number WHERE screen_date >= CURRENT_DATE - 90
                       AND bp.is_active = TRUE)

cleared_count = COUNT(DISTINCT bp_number WHERE match_status IN ('NO_MATCH','CLEARED')
                      AND screen_date >= CURRENT_DATE - 90
                      AND bp.is_active = TRUE)

sanctions_clear_rate = cleared_count / screened_count × 100
```

---

### TR-08: CSDDD Phase Scope Determination

Source: `BP_COMPLIANCE_MASTER`

```
phase_applicability =
  CASE
    WHEN employees > 5000 AND net_turnover_eur > 1500000000 THEN 'PHASE1'  -- deadline 2027
    WHEN employees > 3000 AND net_turnover_eur > 900000000  THEN 'PHASE2'  -- deadline 2028
    WHEN employees > 1000 AND net_turnover_eur > 450000000  THEN 'PHASE3'  -- deadline 2029
    ELSE 'OUT_OF_SCOPE'
  END
```

Note: employee and turnover data sourced from Dun & Bradstreet API (refreshed annually).

---

## 9. Business Rules

### BR-01: UFLPA Clearance Block

| Attribute | Value |
|-----------|-------|
| Name | UFLPA Clearance Block on Goods Receipt |
| Condition | Supplier uflpa_classification = 'HIGH_RISK' AND cert_gap > 0 (any required document missing or expired) |
| Result | Block goods receipt in SAP EWM; generate GRC workflow task for Import Compliance team |
| Example | Supplier A (polysilicon, Xinjiang, cert_gap = 0.75) → EWM block triggered; Import Compliance assigned with 5-day SLA |
| Exception | Emergency import with CPO approval + risk acceptance record in GRC; bond posted per CBP requirement |
| Evidence | SAP EWM block record; GRC workflow task ID; CBP documentation package |

---

### BR-02: New Vendor Sanctions Screen SLA

| Attribute | Value |
|-----------|-------|
| Name | New Vendor Sanctions Screen SLA |
| Condition | New BP created in SAP MDG workflow |
| Result | Automated screening must complete within 4 hours; no PO can be raised until status = NO_MATCH or CLEARED |
| Example | Vendor XYZ created at 09:00 → screening completed 09:47 → NO_MATCH → PO creation enabled 10:05 |
| Exception | System downtime: manual screen performed by Trade Compliance team; screen result manually logged |
| Evidence | SAP MDG workflow log; OpenSearch screen log with timestamps |

---

### BR-03: CSDDD Annual Review Trigger

| Attribute | Value |
|-----------|-------|
| Name | Annual CSDDD Due Diligence Review |
| Condition | DD_COMPLETED = TRUE AND next_review_date <= CURRENT_DATE |
| Result | Generate GRC review task; dd_status reset to IN_PROGRESS until review actions completed |
| Example | Supplier B completed DD 2026-01-15; next_review_date = 2027-01-15; GRC alert fires 90 days before |
| Exception | Supplier risk score has increased by > 0.15 since last DD → triggered immediately, not waiting for annual cycle |
| Evidence | GRC task record; CSDDD Art.11 monitoring documentation |

---

### BR-04: REACH Art.33 Notification Obligation

| Attribute | Value |
|-----------|-------|
| Name | REACH Art.33 Downstream Customer Notification |
| Condition | svhc_conc_article_ppw > 0.001 AND article is sold to downstream industrial customer |
| Result | Generate Art.33 notification letter from template; send within 45 days of customer request; record in DMS |
| Example | Article "Electronic Module X" — SVHC (lead compound, CAS 7439-92-1) at 0.18% w/w → notification sent to all downstream B2B customers |
| Exception | Article sold solely to end consumers (B2C): notification sent within 45 days of consumer request only |
| Evidence | Art.33 notification letter; DMS timestamp; customer acknowledgement receipt |

---

### BR-05: Compliance Document Expiry Escalation

| Attribute | Value |
|-----------|-------|
| Name | Document Expiry Escalation Protocol |
| Condition | days_to_expiry < 30 for any APPROVED document linked to an active TIER1 or TIER2 supplier |
| Result | Email alert to Compliance Analyst + Procurement Category Manager; GRC task created |
| Example | ISO 9001 certificate for Supplier C expires in 22 days → alert generated; renewal workflow initiated |
| Exception | Supplier has confirmed certificate renewal in progress (renewal_in_progress flag = TRUE in DMS) → alert severity downgraded to MEDIUM |
| Evidence | DMS expiry date field; GRC alert log; email audit trail |

---

### BR-06: Sanctions Allowlist Monthly Re-Screen

| Attribute | Value |
|-----------|-------|
| Name | Monthly Re-Screen of Allowlisted Entities |
| Condition | allowlist_flag = TRUE AND (CURRENT_DATE - last_screen_date) > 30 days |
| Result | Automated re-screen triggered; if new POTENTIAL_MATCH detected, allowlist flag cleared and analyst review required |
| Example | Entity "ACME Trading" confirmed clear 2026-05-01; re-screen due 2026-06-01; re-screens clean → allowlist maintained |
| Exception | None — all allowlisted entities must be re-screened monthly regardless of other activity |
| Evidence | OpenSearch re-screen log; list version timestamp |

---

### BR-07: SVHC Unknown Composition Conservative Default

| Attribute | Value |
|-----------|-------|
| Name | Unknown Composition Conservative Default |
| Condition | Purchased component with concentration_ppw = NULL (SDS not received from supplier) |
| Result | Default concentration_ppw = 0.5 for risk scoring purposes; procurement hold generated after 30 days if SDS not received |
| Example | Component "Adhesive Z" — SDS requested 2026-05-15; not received by 2026-06-15 → procurement hold on PO |
| Exception | Component is classified as non-chemical (e.g., pure metal, glass) → default = 0.0 (no SVHC exposure) |
| Evidence | SDS request log; procurement hold record; supplier response timestamp |

---

## 10. KPIs and Formulas

### KPI-01: UFLPA High-Risk Supplier Rate

```
UFLPA_High_Risk_Rate (%) =
  COUNT(bp WHERE uflpa_classification = 'HIGH_RISK' AND is_active = TRUE)
  / COUNT(bp WHERE uflpa_score IS NOT NULL AND is_active = TRUE)
  × 100

Target: < 5% of screened suppliers classified HIGH_RISK
Alert threshold: > 10%
Frequency: Monthly
Owner: Trade Compliance
```

---

### KPI-02: UFLPA Risk Score (Supplier-Level)

```
UFLPA_Risk_Score =
  (0.40 × country_risk)
  + (0.30 × material_risk)
  + (0.20 × tier2_exposure)
  + (0.10 × cert_gap)

Range: [0, 1]
  > 0.70 = HIGH_RISK   (full CBP clearance package required before import)
  > 0.40 = MEDIUM_RISK (enhanced due diligence, annual audit)
  ≤ 0.40 = LOW_RISK    (standard monitoring)

Frequency: Nightly batch recompute + triggered on master data change
Owner: Compliance Data Engineering
```

---

### KPI-03: CSDDD Tier-1 Due Diligence Coverage

```
CSDDD_Tier1_Coverage (%) =
  COUNT(bp WHERE tier = 'TIER1'
                AND csddd_dd_status = 'COMPLETED'
                AND phase_applicability != 'OUT_OF_SCOPE'
                AND is_active = TRUE)
  / COUNT(bp WHERE tier = 'TIER1'
                AND phase_applicability != 'OUT_OF_SCOPE'
                AND is_active = TRUE)
  × 100

Targets: Year 1 ≥60%; Year 2 100% for PHASE1; Year 3 100% for PHASE1+2+3
Alert threshold: Month-over-month decline OR < 10 percentage points below trajectory
Frequency: Monthly
Owner: ESG Compliance Lead
```

---

### KPI-04: CSDDD Tier-2 Due Diligence Coverage

```
CSDDD_Tier2_Coverage (%) =
  COUNT(bp WHERE tier = 'TIER2'
                AND csddd_dd_status = 'COMPLETED'
                AND is_active = TRUE)
  / COUNT(bp WHERE tier = 'TIER2'
                AND is_active = TRUE)
  × 100

Targets: Year 1 ≥10%; Year 2 ≥40%; Year 3 ≥80%
Frequency: Monthly
Owner: ESG Compliance Lead
```

---

### KPI-05: REACH Declaration Completeness

```
REACH_Declaration_Completeness (%) =
  COUNT(material_number WHERE
        art33_notification_flag = TRUE
        AND sds_doc_id IS NOT NULL
        AND (SELECT approval_status FROM COMPLIANCE_DOCUMENT_REGISTRY
             WHERE doc_id = sds_doc_id) = 'APPROVED'
        AND (SELECT expiry_date FROM COMPLIANCE_DOCUMENT_REGISTRY
             WHERE doc_id = sds_doc_id) >= CURRENT_DATE)
  / COUNT(material_number WHERE art33_notification_flag = TRUE)
  × 100

Target: ≥95%
Alert threshold: < 80%
Frequency: Monthly
Owner: Chemical Compliance Specialist
```

---

### KPI-06: SVHC Presence Rate

```
SVHC_Presence_Rate (%) =
  COUNT(DISTINCT material_number WHERE svhc_conc_article_ppw > 0.001)
  / COUNT(DISTINCT material_number WHERE article_total_weight_g IS NOT NULL)
  × 100

Note: Tracks the proportion of finished articles triggering REACH Art.33 obligations.
Frequency: Monthly (refreshed on BOM change or ECHA list update)
Owner: Chemical Compliance Specialist
```

---

### KPI-07: Compliance Document Expiry — Critical Count

```
Doc_Expiry_Critical_Count =
  COUNT(doc_id WHERE urgency_band IN ('EXPIRED','CRITICAL')
                 AND approval_status = 'APPROVED'
                 AND bp.is_active = TRUE)

Breakdown required by: doc_type, supplier tier, urgency band
Target: 0 EXPIRED documents for active TIER1 suppliers
Alert threshold: Any EXPIRED document for TIER1 supplier
Frequency: Daily monitoring; monthly reporting
Owner: Compliance Analyst
```

---

### KPI-08: Sanctions Clear Rate

```
Sanctions_Clear_Rate (%) =
  COUNT(DISTINCT bp_number WHERE match_status IN ('NO_MATCH','CLEARED')
                              AND screen_date >= CURRENT_DATE - 90)
  / COUNT(DISTINCT bp_number WHERE screen_date >= CURRENT_DATE - 90
                               AND bp.is_active = TRUE)
  × 100

Target: ≥99.9% (CONFIRMED_MATCH → procurement block is the correct outcome, not a failure)
Alert threshold: > 0.1% CONFIRMED_MATCH rate (investigate for name data quality issues)
Frequency: Daily monitoring; monthly reporting
Owner: Trade Compliance
```

---

### KPI-09: Sanctions Screening SLA Compliance

```
Sanctions_Screen_SLA (%) =
  COUNT(screen_id WHERE match_status IN ('NO_MATCH','CLEARED','CONFIRMED_MATCH')
                    AND resolution_date - screen_date <= 4 hours  -- for auto NO_MATCH
                    OR (match_status IN ('CLEARED','CONFIRMED_MATCH')
                        AND resolution_date - screen_date <= 2 business days))
  / COUNT(screen_id WHERE screen_date >= CURRENT_DATE - 30)
  × 100

Target: ≥99% for auto NO_MATCH; ≥95% for manual resolution within 2 business days
Frequency: Monthly
Owner: Trade Compliance
```

---

### KPI-10: UFLPA Import Value at Risk

```
UFLPA_Import_Value_at_Risk (EUR) =
  SUM(po.net_value_eur_cents WHERE
      supplier.uflpa_classification = 'HIGH_RISK'
      AND po.document_date >= CURRENT_DATE - 365)
  / 100   -- convert cents to EUR

Interpretation: Total annual spend flowing through HIGH_RISK suppliers.
If goods are detained by CBP, the importer must post a bond of ~20% of cargo value.
Frequency: Monthly
Owner: Trade Compliance + Procurement Finance
```

---

## 11. Analytical Logic

### UFLPA Risk Scoring — Detailed Logic

The UFLPA Risk Score is a four-factor weighted sum:

```python
# python/09_compliance/uflpa_risk_scorer.py

from dataclasses import dataclass
from typing import Literal

@dataclass
class UFLPARiskInput:
    country_risk: float      # 0.0 – 1.0 (see TR-01 mapping)
    material_risk: float     # 0.0 – 1.0 (see TR-02 mapping)
    tier2_exposure: float    # 0.0 – 1.0 (fraction of known Tier-2 with XUAR link)
    cert_gap: float          # 0.0 – 1.0 (see TR-03 formula)

WEIGHTS = {
    "country_risk":   0.40,
    "material_risk":  0.30,
    "tier2_exposure": 0.20,
    "cert_gap":       0.10,
}

def compute_uflpa_score(inp: UFLPARiskInput) -> dict:
    """
    Compute UFLPA weighted risk score per CBP guidance (Jan 2023).
    All inputs must be in [0,1]. Returns score and risk classification.
    """
    for field, value in vars(inp).items():
        if not 0.0 <= value <= 1.0:
            raise ValueError(f"{field} must be in [0,1], got {value}")

    score = sum(WEIGHTS[k] * v for k, v in vars(inp).items())

    if score > 0.70:
        classification: Literal["HIGH_RISK","MEDIUM_RISK","LOW_RISK"] = "HIGH_RISK"
    elif score > 0.40:
        classification = "MEDIUM_RISK"
    else:
        classification = "LOW_RISK"

    return {
        "score": round(score, 4),
        "classification": classification,
        "factor_contributions": {
            k: round(WEIGHTS[k] * v, 4) for k, v in vars(inp).items()
        },
    }
```

**Trigger logic:**
- HIGH_RISK (> 0.70): Full CBP clearance package required before goods enter US commerce.
  SAP EWM goods receipt blocked. Import Compliance SLA: 5 business days to assemble package.
- MEDIUM_RISK (0.40–0.70): Enhanced due diligence. Annual third-party audit required.
  Procurement Category Manager notified. No EWM block but flagged in GRC.
- LOW_RISK (≤ 0.40): Standard monitoring. Annual UFLPA questionnaire suffices.

---

### CSDDD Phased Scope and Deadline Logic

```
Phase 1 (deadline: 26 July 2027):
  EU companies: employees > 5,000 AND net_turnover_eur > €1.5B
  Non-EU companies: EU net turnover > €1.5B

Phase 2 (deadline: 26 July 2028):
  EU companies: employees > 3,000 AND net_turnover_eur > €900M
  Non-EU companies: EU net turnover > €900M

Phase 3 (deadline: 26 July 2029):
  EU companies: employees > 1,000 AND net_turnover_eur > €450M
  Non-EU companies: EU net turnover > €450M

Progress tracking against deadline:
  months_remaining = (phase_deadline - CURRENT_DATE) / 30
  required_monthly_run_rate =
    (phase_target_coverage - current_coverage) / months_remaining
  projected_coverage_at_deadline =
    current_coverage + (months_remaining × actual_monthly_run_rate_last_3months)
```

RAG status:
- GREEN: projected_coverage_at_deadline ≥ target
- AMBER: projected_coverage within 10 percentage points below target
- RED: projected_coverage more than 10 percentage points below target

---

### Document Expiry Alert Tiers

| Urgency Band | Days to Expiry | Alert Recipient | Alert Channel | Action SLA |
|---|---|---|---|---|
| EXPIRED | < 0 | Compliance Analyst + Category Manager + CCO | Email + GRC task + dashboard RED flag | Immediate suspension of supplier activity |
| CRITICAL | 0–29 days | Compliance Analyst + Category Manager | Email + GRC task | 5 business days to initiate renewal |
| HIGH | 30–59 days | Compliance Analyst | Email + GRC task | 15 business days to initiate renewal |
| MEDIUM | 60–89 days | Compliance Analyst | GRC task only | 30 business days to initiate renewal |
| OK | ≥ 90 days | — | Dashboard green indicator | No action required |

Special rule: For UFLPA_CLEARANCE documents linked to HIGH_RISK suppliers, CRITICAL band starts at
60 days (not 30), because CBP clearance assembly takes 4–8 weeks.

---

## 12. Validations and Controls

### VC-01: Referential Integrity

- All `bp_number` values in SANCTIONS_SCREEN_LOG and CSDDD_DUE_DILIGENCE_REGISTER must exist
  in BP_COMPLIANCE_MASTER. Orphaned records generate a data quality alert.
- All `material_number` values in SVHC_BOM_DETAIL must exist in MATERIAL_MASTER with
  `is_active = TRUE` or `is_deleted = FALSE`.

### VC-02: UFLPA Score Freshness

- Any active supplier with `uflpa_score IS NULL` or `scored_at < CURRENT_DATE - 7 days`
  is flagged as STALE_SCORE and excluded from KPI denominators with a warning banner on dashboard.
- Scoring pipeline must complete within 6 hours of the nightly batch start.

### VC-03: CSDDD Denominator Stability

- Month-over-month change in the CSDDD in-scope denominator (total_inscope_suppliers) of > ±5%
  triggers a validation review. Changes must be explained in the monthly compliance pack.

### VC-04: Sanctions Screen Completeness

- Any active supplier with `sanctions_last_screen IS NULL` or
  `CURRENT_DATE - sanctions_last_screen_date > 90 days` is flagged as UNSCREENED.
- UNSCREENED suppliers must not have active POs. A daily check blocks new PO creation if
  supplier is UNSCREENED.

### VC-05: REACH BOM Completeness

- Any finished article with `article_total_weight_g = 0` or `article_total_weight_g IS NULL`
  is excluded from the SVHC Presence Rate KPI denominator.
- A separate alert lists all finished articles with incomplete BOM SVHC data (partial BOM explosion).

### VC-06: Document Approval Chain

- Only documents with `approval_status = 'APPROVED'` count toward coverage KPIs.
- PENDING documents do not count; this prevents gaming the KPI by uploading unapproved documents.

### VC-07: Idempotency of Scoring Runs

- The UFLPA scoring pipeline writes to UFLPA_RISK_SCORING_LOG with a unique (bp_number +
  material_number + model_version + scored_at) composite key.
- Re-runs of the same model version on the same day are deduplicated. Only the latest score
  per (bp_number + material_number) is used for current-state KPIs.

---

## 13. Required Evidence

| Evidence Item | Retention Period | Owner | Storage Location |
|---|---|---|---|
| UFLPA scoring log (all versions) | 7 years | Compliance Data Engineering | Data lake (Parquet, Apache Iceberg) |
| CBP clearance documentation packages | 7 years (CBP requirement) | Trade Compliance | SAP DMS + secure document archive |
| CSDDD due diligence records (Art.23) | 5 years from assessment | ESG Compliance | SAP DMS with legal hold |
| REACH Art.33 notification letters | 5 years | Chemical Compliance | SAP DMS |
| Sanctions screening logs + resolution rationale | 7 years | Trade Compliance | OpenSearch index + cold archive |
| SVHC SDS versions | 5 years | Chemical Compliance | SAP DMS |
| Modern Slavery statements | 6 years (UK registry + internal) | Legal | the Git document repository + UK Gov registry URL |
| LkSG BAFA annual reports | 7 years (LkSG §24) | ESG Compliance | SAP DMS |
| Compliance document approval chain | 5 years | Compliance | SAP DMS workflow log |
| GDPR RoPA entries for screening activities | Duration of processing + 3 years | DPO | GDPR tool |

---

## 14. Dashboard Design

### Dashboard 1: UFLPA Risk Exposure Dashboard

**Audience:** Trade Compliance team, Procurement Category Managers, CSCO
**Refresh:** Daily

**Page 1 — Executive Summary:**
- KPI tiles (row): High-Risk Supplier Count | High-Risk Rate % | Import Value at Risk (EUR) | Avg UFLPA Score (portfolio)
- Trend chart: Monthly UFLPA high-risk count over 12 months (line chart)
- Bar chart: UFLPA score distribution (histogram — bins: 0–0.2, 0.2–0.4, 0.4–0.6, 0.6–0.8, 0.8–1.0)

**Page 2 — Supplier Drill-Down:**
- Table: Top 20 highest-scoring suppliers — columns: Supplier Name, UFLPA Score, Classification, Country Risk, Material Risk, Tier-2 Exposure, Cert Gap, Import Value (EUR), Action Required
- Filter panel: by commodity group, country of origin, HS chapter, classification band

**Page 3 — Certification Status:**
- Stacked bar chart: HIGH_RISK suppliers — documents provided vs missing (4 document types)
- List: Suppliers with cert_gap > 0 AND classification = HIGH_RISK (with days since SLA breach)

---

### Dashboard 2: CSDDD Due Diligence Coverage

**Audience:** ESG Compliance Lead, Procurement, CLO, CSCO
**Refresh:** Monthly

**Page 1 — Coverage Overview:**
- Gauge chart: Tier-1 Coverage % vs target
- Gauge chart: Tier-2 Coverage % vs target
- Line chart: Coverage trend (monthly, 18 months) — Tier-1 and Tier-2 on same chart
- RAG status card: Phase 1 trajectory (2027), Phase 2 trajectory (2028), Phase 3 trajectory (2029)

**Page 2 — Pipeline:**
- Funnel chart: DD stages — NOT_STARTED → IN_PROGRESS → COMPLETED (with counts at each stage)
- Table: Suppliers in REMEDIATION status (corrective action plans outstanding)

**Page 3 — Category Analysis:**
- Heat map: CSDDD coverage % by procurement category × supplier tier
- Bar chart: Average DD completion time (days) by procurement category

---

### Dashboard 3: REACH SVHC Tracking

**Audience:** Chemical Compliance Specialist, Product Management, Legal
**Refresh:** Monthly (triggered on ECHA list update)

**KPI tiles:** SVHC Presence Rate % | Articles with Art.33 Obligation | Declaration Completeness % | Articles with Art.7(2) Obligation

**Chart 1:** Articles by SVHC concentration band (bar: 0, 0–0.1%, >0.1%)
**Chart 2:** Declaration completeness trend (12 months)
**Table:** Articles with Art.33 obligation and missing or expired SDS (sorted by annual volume descending)

---

### Dashboard 4: Sanctions Screening Tracker

**Audience:** Trade Compliance, Legal
**Refresh:** Daily

**KPI tiles:** Clear Rate % | Unresolved Potential Matches | Avg Resolution Time (hours) | Unscreened Suppliers Count

**Chart:** Screen results by status (donut: NO_MATCH / POTENTIAL_MATCH / CONFIRMED_MATCH / CLEARED)
**Table:** Open POTENTIAL_MATCH items — columns: Supplier, Screen Date, List, Match Score, Age (days), Assigned Analyst
**Alert panel:** Suppliers with `sanctions_last_screen > 90 days` ago

---

### Dashboard 5: Document Expiry Monitor

**Audience:** Compliance Analyst team, Category Managers
**Refresh:** Daily

**Heatmap:** Document type × urgency band (cell = count of documents)
**Table:** EXPIRED and CRITICAL documents — columns: Supplier, Doc Type, Expiry Date, Days Overdue/Remaining, Tier, Action Owner
**Trend chart:** Documents by urgency band — monthly stack bar (last 12 months)
**Filter:** by doc_type, supplier tier, urgency band, procurement category

---

## 15. Use Cases

### UC-01: Pre-Shipment UFLPA Risk Clearance

**Actor:** Import Compliance Analyst
**Trigger:** US-bound shipment created in SAP TM with supplier uflpa_classification = HIGH_RISK

**Flow:**
1. Analyst opens UFLPA Dashboard → filters to specific supplier
2. Reviews cert_gap breakdown: which of 4 required documents are missing
3. Contacts supplier to request missing traceability records and supply chain map
4. Uploads received documents to SAP DMS → triggers approval workflow
5. Once cert_gap = 0 → SAP EWM goods receipt block automatically lifted
6. CBP clearance package auto-assembled as PDF for customs entry filing

**Outcome:** Shipment clears US Customs without detention. UFLPA_CLEARANCE document archived.

---

### UC-02: Monthly CSDDD Coverage Reporting to CLO

**Actor:** ESG Compliance Lead
**Trigger:** First working day of each month

**Flow:**
1. Open CSDDD Coverage Dashboard → export current coverage % for Tier-1 and Tier-2
2. Review Phase trajectory chart: are we on track for 2027 deadline?
3. Drill into NOT_STARTED suppliers — assign DD questionnaires in GRC
4. Prepare CLO pack: coverage trend + pipeline + remediation list
5. CLO reviews and approves; pack filed as board communication

**Outcome:** CLO has current-month compliance posture; corrective actions assigned.

---

### UC-03: ECHA SVHC List Update Impact Assessment

**Actor:** Chemical Compliance Specialist
**Trigger:** ECHA publishes new SVHC Candidate List addition (2× per year)

**Flow:**
1. Automated sync: new CAS numbers added to SVHC_SUBSTANCE_LIST
2. ETL reruns SVHC concentration roll-up across all articles using new substances
3. REACH Dashboard flags: new articles with svhc_conc_article_ppw > 0.001
4. Specialist reviews list: confirms Art.33 notification list, assigns SDS requests to procurement
5. For new Art.7(2) triggers: drafts ECHA notification and submits via ECHA REACH-IT API

**Outcome:** All new SVHC obligations captured within 5 business days of ECHA publication.

---

### UC-04: Supplier Sanctions Positive Match Resolution

**Actor:** Trade Compliance Analyst + Legal
**Trigger:** OpenSearch screening generates match_status = POTENTIAL_MATCH for Supplier XYZ

**Flow:**
1. GRC alert generated; analyst reviews match_score (0.73), entity context, country, industry
2. Compares against OFAC SDN list entry: different country of registration → likely false positive
3. Documents resolution rationale in OpenSearch screen log + GRC notes field
4. Updates match_status = CLEARED; allowlist_flag = TRUE; approved by Legal Counsel
5. Monthly re-screen scheduled; if clean → allowlist maintained

**Outcome:** False positive resolved within 2 business days; audit trail complete for external review.

---

### UC-05: Compliance Document Renewal Campaign

**Actor:** Compliance Analyst
**Trigger:** Monday morning automated email listing all documents in CRITICAL and HIGH urgency bands

**Flow:**
1. Analyst reviews expiry monitor dashboard: 14 documents in CRITICAL, 23 in HIGH
2. Sorts by supplier tier — TIER1 CRITICAL documents addressed first
3. For each: sends renewal request to supplier contact (template from GRC)
4. Sets renewal_in_progress flag in DMS → urgency band display downgraded on dashboard
5. Tracks receipt of renewed documents; re-approves and updates expiry date in DMS

**Outcome:** Zero EXPIRED documents for TIER1 suppliers at month-end.

---

## 16. Recommended Actions

### Immediate Actions (Month 1–3)

1. **Remediate BP master data gaps:** Launch MDG data quality campaign to populate missing DUNS
   numbers and registration countries for the ~8% of BP records currently incomplete. Without
   these fields, UFLPA country_risk and sanctions matching accuracy are degraded.

2. **Establish UFLPA baseline:** Run the UFLPA scoring model across all active Tier-1 suppliers
   and publish the first HIGH_RISK supplier list to the Trade Compliance team. Initiate clearance
   document collection for all HIGH_RISK suppliers.

3. **Prioritise CSDDD questionnaire campaign:** Send CSDDD due diligence questionnaires to all
   Tier-1 PHASE1 suppliers (companies > 5,000 employees / > €1.5B turnover). 2027 deadline gives
   18 months — starting immediately is essential for adequate coverage.

4. **Deploy document expiry alerts:** Configure the daily CRITICAL/HIGH expiry alert emails before
   next quarter-end. Multiple ISO 9001 certificates are likely in the CRITICAL band already.

### Medium-Term Actions (Month 4–12)

5. **Extend UFLPA scoring to Tier-2:** Once Tier-2 supplier mapping is complete, apply UFLPA
   scoring with default tier2_exposure = 0.5 and refine as Tier-2 data is collected.

6. **Automate REACH SVHC BOM roll-up:** Implement the article-level SVHC concentration calculation
   for the top 500 articles by annual revenue. Prioritise articles with chemical components sourced
   from countries with SVHC disclosure gaps.

7. **Sanctions screening SLA enforcement:** Implement daily SLA breach report — any POTENTIAL_MATCH
   unresolved after 2 business days triggers CCO notification.

8. **CSDDD Tier-2 mapping:** Commission Tier-2 supplier mapping exercise using procurement data and
   supplier questionnaire responses. Without Tier-2 identification, the Tier-2 coverage KPI cannot
   be computed.

### Strategic Actions (Year 2–3)

9. **NLP contract clause scanning:** Deploy DistilBERT contract scanner to check all supplier
   contracts for mandatory CSDDD clauses. Target: 100% of Tier-1 contracts scanned by Year 2 end.

10. **LkSG BAFA reporting automation:** Integrate GRC data with the annual LkSG report template.
    First fully automated BAFA report target: calendar year 2027.

11. **CSDDD Tier-2 DD programme:** Launch structured Tier-2 due diligence programme with a
    risk-proportionate approach. Focus on high-spend Tier-2 suppliers in high-risk categories
    (garment, electronics, agricultural inputs).

---

## 17. Test Cases

### TC-01: UFLPA Score Boundary Test

| Scenario | Inputs | Expected Output |
|---|---|---|
| Maximum score | country_risk=1.0, material_risk=1.0, tier2_exposure=1.0, cert_gap=1.0 | score=1.0000, classification=HIGH_RISK |
| Minimum score | All inputs = 0.0 | score=0.0000, classification=LOW_RISK |
| Exact HIGH threshold | Score = 0.7001 | classification=HIGH_RISK |
| Exact MEDIUM-HIGH boundary | Score = 0.7000 | classification=MEDIUM_RISK |
| Exact LOW-MEDIUM boundary | Score = 0.4000 | classification=LOW_RISK |
| Invalid input | country_risk=1.5 | ValueError raised |
| Default tier2_exposure | Tier-2 data unavailable | tier2_exposure=0.5 applied |

---

### TC-02: CSDDD Coverage Calculation Test

| Scenario | Tier-1 Total In-Scope | Tier-1 Completed | Expected Coverage |
|---|---|---|---|
| Baseline | 200 | 10 | 5.0% |
| Year 1 target | 200 | 120 | 60.0% |
| Full coverage | 200 | 200 | 100.0% |
| Supplier becomes out-of-scope | 201 → 200 | 120 | 60.0% (denominator decreases) |
| IN_PROGRESS not counted | 200 | 100 complete + 50 in progress | 50.0% |

---

### TC-03: REACH SVHC Roll-Up Test

| Scenario | Component Weights | SVHC Concentrations | Expected Article % w/w | Art.33 Flag |
|---|---|---|---|---|
| Single SVHC below threshold | 100g article, 10g component at 0.05% | 0.0005 × 10 / 100 = 0.005% | FALSE |
| Single SVHC above threshold | 100g article, 10g component at 2.0% | 0.02 × 10 / 100 = 0.2% | TRUE |
| Multiple SVHCs cumulative | 50g + 50g, both at 0.08% | (0.0008×50 + 0.0008×50)/100 = 0.08% | FALSE |
| Missing SDS (NULL) | 100g article, 10g component with NULL | Default 50% → 0.5×10/100 = 5% | TRUE |

---

### TC-04: Document Expiry Urgency Band Test

| Scenario | Expiry Date | CURRENT_DATE | Expected Band |
|---|---|---|---|
| Already expired | 2026-05-01 | 2026-06-22 | EXPIRED |
| Expires today | 2026-06-22 | 2026-06-22 | CRITICAL (days_to_expiry=0) |
| 29 days remaining | 2026-07-21 | 2026-06-22 | CRITICAL |
| 30 days remaining | 2026-07-22 | 2026-06-22 | HIGH |
| 89 days remaining | 2026-09-19 | 2026-06-22 | MEDIUM |
| 90 days remaining | 2026-09-20 | 2026-06-22 | OK |

---

### TC-05: Sanctions Screen SLA Test

| Scenario | Screen Date | Resolution Date | Expected SLA Status |
|---|---|---|---|
| Auto NO_MATCH in 2 hours | 2026-06-22 09:00 | 2026-06-22 11:00 | WITHIN SLA |
| Manual resolution in 1 day | 2026-06-22 09:00 | 2026-06-23 09:00 | WITHIN SLA |
| Manual resolution in 3 days | 2026-06-22 09:00 | 2026-06-25 09:00 | SLA BREACH |
| Unresolved after 5 days | 2026-06-22 09:00 | NULL | ESCALATION TRIGGERED |

---

### TC-06: Certification Gap Test

| Scenario | Docs Provided | Expected cert_gap |
|---|---|---|
| All 4 docs approved and current | 4 | 0.00 |
| 3 of 4 docs provided | 3 | 0.25 |
| 2 of 4 docs provided | 2 | 0.50 |
| 0 docs provided | 0 | 1.00 |
| 1 doc expired (not counted) | 1 approved + 1 expired | 0.50 (only 2 of 4 count) |

---

## 18. Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| CSDDD national transposition delays (27 EU member states may transpose late) | Medium | Medium | Apply strictest standard proactively; do not wait for national law; use EU Directive text directly |
| UFLPA enforcement expansion — CBP adds new priority sectors | High | High | Quarterly CBP guidance review; score recalculation triggered by HS lookup table update |
| ML false negatives on sanctions screening (confirmed match missed) | Low | Critical | Multi-list redundancy (5 lists screened independently); conservative 0.60 threshold; quarterly manual audit of NO_MATCH records |
| Supplier data quality too poor for UFLPA scoring (missing registration country / HS code) | High | High | MDG data quality programme; until remediated, apply worst-case default (country_risk=0.5, material_risk=0.5) |
| GDPR conflict with UFLPA information sharing (supplier individual data) | Medium | Medium | DPO sign-off documented; Art.6(1)(c) legal obligation basis covers sanctions and UFLPA screening |
| REACH SVHC list expansion affects major product lines | Medium | High | ECHA horizon scanning; automated re-run of BOM roll-up on list update; proactive supplier substitution programme |
| SAP GTS HS code data quality (generic codes blocking material_risk scoring) | High | Medium | GTS HS code audit; for generic codes, apply material_risk = 0.5 and generate data quality alert |
| Supplier refusal to provide CSDDD documentation | Medium | High | Contractual obligation in standard T&Cs; escalation path to supplier discontinuation; document refusal in GRC |
| Document expiry not noticed due to null expiry_date in legacy records | Medium | Medium | TR-06 default rule: null expiry = effective + 365 days; legacy document audit to back-populate expiry dates |
| UFLPA entity list sync delay (CBP updates not reflected in OpenSearch within 24 hours) | Low | High | Monitor sync lag; alert if UFLPA entity list not refreshed within 25 hours |

---

## 19. Implementation Checklist

### Phase 1: Data Foundation (Weeks 1–8)

- [ ] Extract full active BP master from SAP S/4HANA; assess data quality (missing DUNS, COO)
- [ ] Configure custom BP extension fields (ZCO_ namespace) via SAP MDG
- [ ] Load UFLPA priority sector HS code lookup table into GTS
- [ ] Set up OpenSearch index for sanctions lists (OFAC, EU, UN, BIS, UFLPA entity list)
- [ ] Configure automated daily download of all 5 sanctions lists
- [ ] Create COMPLIANCE_DOCUMENT_REGISTRY table in analytics layer
- [ ] Migrate existing compliance documents to document registry with correct metadata
- [ ] Configure SVHC_SUBSTANCE_LIST table and load current ECHA Candidate List
- [ ] Define all 6 analytical tables in data warehouse (Parquet on Apache Iceberg)

### Phase 2: KPI and Scoring (Weeks 9–16)

- [ ] Deploy Python UFLPA risk scoring microservice
- [ ] Run first nightly batch UFLPA scoring across all active suppliers
- [ ] Implement CSDDD DD_COMPLETED logic in ETL
- [ ] Compute first CSDDD Tier-1 coverage baseline
- [ ] Implement REACH BOM roll-up for top 500 articles
- [ ] Configure daily document expiry calculation and urgency band assignment
- [ ] Build CSDDD phase scope determination logic using D&B employee/revenue data

### Phase 3: Dashboards (Weeks 17–22)

- [ ] Deploy all 5 dashboards in SAP Analytics Cloud (or Apache Superset as fallback)
- [ ] Configure daily data refresh pipelines
- [ ] Configure email alert workflows for CRITICAL document expiry
- [ ] Configure GRC task creation for new HIGH_RISK UFLPA suppliers
- [ ] User acceptance testing with Compliance team, Trade Compliance, CLO office
- [ ] Train Compliance Analysts on dashboard use (4-hour session)

### Phase 4: Controls and Automation (Weeks 23–28)

- [ ] Implement SAP EWM goods receipt block for HIGH_RISK UFLPA suppliers with cert_gap > 0
- [ ] Configure MDG vendor creation block until sanctions screen complete
- [ ] Implement monthly re-screen trigger for allowlisted entities
- [ ] Configure CSDDD annual review trigger (GRC workflow)
- [ ] Configure REACH Art.33 notification letter template in SAP correspondence
- [ ] Implement GDPR retention purge schedule for screening logs > 7 years

---

## 20. Validation Checklist

### Data Quality

- [ ] Zero active TIER1 suppliers with uflpa_score IS NULL after first scoring run
- [ ] Zero active suppliers with sanctions_last_screen IS NULL
- [ ] CSDDD coverage denominator matches agreed Tier-1 in-scope count (±2%)
- [ ] SVHC concentration roll-up validated for 10 test articles against manual BOM calculation
- [ ] Document expiry urgency bands validated against 20 sample documents

### KPI Accuracy

- [ ] UFLPA High-Risk Rate % matches manual count from scoring log (spot check)
- [ ] CSDDD Tier-1 Coverage matches manual count from CSDDD register (spot check)
- [ ] Sanctions Clear Rate % is confirmed by Trade Compliance team as accurate
- [ ] REACH Declaration Completeness % validated against SVHC BOM extract

### Dashboard

- [ ] All 5 dashboards rendering correctly in target browsers / devices
- [ ] Drill-down from summary KPI to supplier-level detail works on all charts
- [ ] Export to PDF for monthly CLO pack validated (no truncated tables)
- [ ] Access controls: Compliance Analysts see all data; Procurement sees own category only

### Controls

- [ ] EWM goods receipt block fires correctly for a test HIGH_RISK supplier (UAT test)
- [ ] Sanctions screen block on new vendor creation fires correctly (UAT test)
- [ ] CRITICAL document expiry email alert received by correct recipients (UAT test)
- [ ] Monthly re-screen of allowlisted entity executes on schedule (UAT test)

---

## 21. Pending Information

| Item | Required From | Impact if Missing | Target Date |
|---|---|---|---|
| Tier-2 supplier mapping (complete list with BP cross-reference) | Procurement / Strategic Sourcing | Tier-2 CSDDD Coverage KPI cannot be computed | 2026-09-30 |
| D&B employee and revenue data for CSDDD phase scope | D&B subscription / Finance | Phase applicability flags cannot be set accurately | 2026-08-31 |
| GTS province-level COO data (for XUAR province mapping) | Trade Compliance / GTS admin | country_risk defaults to 0.5 for all CN suppliers | 2026-08-15 |
| Supplier SDS documents for all components with concentration_ppw = NULL | Procurement (per supplier) | SVHC scoring defaults to worst-case 0.5 | Rolling — 30-day SLA per supplier |
| LkSG high-risk country list (aligned to LkSG Annex) | Legal / ESG Compliance | lksg_risk_country flag cannot be set | 2026-07-31 |
| Confirmation of document management system (SAP DMS vs OpenText) | IT Architecture | Document registry table schema depends on DMS API | 2026-07-15 |
| Budget approval for D&B third-party data subscription | Finance | Employee / revenue data unavailable for CSDDD scoping | 2026-07-31 |

---

## 22. Implementation Roadmap

```
QUARTER       Q3 2026              Q4 2026              Q1 2027              Q2 2027
              Jul   Aug   Sep      Oct   Nov   Dec      Jan   Feb   Mar      Apr   May   Jun

PHASE 1       ████████████████████
Data          Data quality audit
Foundation    BP enrichment campaign
              Sanctions list setup
              Document registry migration

PHASE 2                      ████████████████████
KPI Scoring                  UFLPA scoring live
                             CSDDD baseline computed
                             REACH BOM roll-up (top 500)
                             Expiry calc + urgency bands

PHASE 3                                   ████████████████████
Dashboards                               Dashboard 1-5 deployed
                                         Email alerts configured
                                         GRC task automation

PHASE 4                                                ████████████████████
Controls                                              EWM block live
                                                      MDG vendor creation gate
                                                      Monthly re-screen automation
                                                      CSDDD annual review trigger

PHASE 5                                                             ████████████
Continuous                                                         NLP contract scanner
Improvement                                                        Tier-2 DD programme
                                                                   LkSG BAFA automation

MILESTONES
2026-07-31   First UFLPA scoring batch complete; HIGH_RISK supplier list published
2026-09-30   CSDDD Tier-1 baseline coverage computed and reported to CLO
2026-12-31   All 5 dashboards live; document expiry alerts operational
2027-03-31   REACH BOM roll-up complete for all articles; Art.33 backlog cleared
2027-06-30   EWM block live; CSDDD Tier-1 coverage ≥60%; Tier-2 mapping complete
2027-07-26   CSDDD Phase 1 regulatory deadline — 100% Tier-1 PHASE1 coverage required
```

**Budget:**
- Phase 1–4: €4.5M (SAP configuration, data engineering, Python platform, dashboards)
- Phase 5 (Year 3+): €1.5M/year (NLP models, Tier-2 DD programme, ongoing operations)
- External data subscriptions: €0.3M/year (D&B, ECHA, sanctions list feeds)

---

## References

1. European Parliament and Council, Directive 2024/1760 on Corporate Sustainability Due Diligence
   (CSDDD), OJ L 2024/1760, 5 July 2024
2. US Congress, Uyghur Forced Labor Prevention Act, Pub.L. 117-78, enacted 23 December 2021
3. US Customs and Border Protection, UFLPA Operational Guidance for Importers, January 2023
4. European Parliament and Council, Regulation (EC) No 1907/2006 concerning REACH,
   OJ L 396, 30 December 2006
5. EU ECHA, Guidance on requirements for substances in articles under REACH, Version 4.0, 2017
6. UK Parliament, Modern Slavery Act 2015, Chapter 30
7. German Federal Government, Lieferkettensorgfaltspflichtengesetz (LkSG), BGBl. I S. 2959,
   16 July 2021
8. OFAC, Specially Designated Nationals and Blocked Persons List (SDN), US Treasury, updated daily
9. EU External Action Service, EU Consolidated Financial Sanctions List, updated daily
10. ISO 31000:2018 Risk management — Guidelines, International Organization for Standardization
11. ISO 28000:2022 Security and resilience — Supply chain security management systems
12. Sanh et al., DistilBERT: a distilled version of BERT, arXiv:1910.01108, 2019
13. Devlin et al., BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding,
    arXiv:1810.04805, 2018
14. Walk Free Foundation, Global Slavery Index 2023
15. ICC Incoterms 2020, International Chamber of Commerce, 2019
