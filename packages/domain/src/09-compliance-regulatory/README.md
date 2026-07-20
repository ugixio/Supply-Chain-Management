# 09 — Compliance & Regulatory

## Overview

Manages compliance with international supply chain regulations: EU CSDDD (due diligence), US UFLPA (Xinjiang forced labour), EU REACH (chemical substances), LkSG (Germany), UK Modern Slavery Act, and global sanctions. Enforces the mandatory 5-year document retention requirement (CSDDD Art.23) and continuous screening of sanctioned entities.

---

## Department KPIs

| KPI | Target | Source |
|-----|--------|--------|
| Due diligence coverage | 100% Tier-1 suppliers | CSDDD Art.5 |
| Open remediation actions | 0 critical pending | CSDDD Art.8 |
| Audits completed / plan | ≥ 95% | LkSG §4 |
| Average days to remediation | < 90 days | Internal |
| Documents with active retention | 100% (5 years) | CSDDD Art.23 |
| UFLPA-screened suppliers | 100% with XUAR operations | UFLPA §3(d) |

---

## Implemented Regulations

| Regulation | Jurisdiction | Threshold / Scope |
|-----------|-------------|-----------------|
| EU CSDDD Dir.2024/1760 | EU | 3 phases: 2027-2029 (>1,000 employees) |
| US UFLPA Pub.L.117-78 | USA | Rebuttable presumption — XUAR products |
| EU REACH 1907/2006 | EU | SVHC >0.1% w/w → Art.7 notification |
| LkSG Germany 2023 | Germany | ≥ 1,000 employees in Germany |
| UK Modern Slavery Act §54 | UK | Turnover ≥ £36M → annual statement |
| EU Deforestation Reg. 2023/1115 | EU | 7 high-risk commodities |

---

## Department Files

| File | Responsibility |
|------|---------------|
| `regulations/CSDDD.ts` | CSDDDPhase (3 phases), CompanyProfile, determineCSDDDPhase(), DueDiligenceRecord (5-year retention), AdverseImpactType |
| `regulations/UFLPA.ts` | UFLPA_HIGH_RISK_REGIONS, UFLPA_HIGH_PRIORITY_HS_PREFIXES, assessUFLPARisk() → PROHIBITED / HIGH / MEDIUM / LOW |
| `regulations/REACH.ts` | SVHCCategory, REACHSubstance, ArticleREACHAssessment, assessREACHCompliance() Art.7/31/33 |

---

## Applied Mathematical Models

### 1. CSDDD Phase Determination (Dir.2024/1760 Art.2)

```
Phase 1 (2027): employees > 5,000 AND (turnover_EU > €1.5B OR turnover_global > €1.5B)
               OR non-EU company with net_turnover_EU > €1.5B

Phase 2 (2028): employees > 3,000 AND turnover > €900M

Phase 3 (2029): employees > 1,000 AND turnover > €450M
               OR companies in "high impact sectors" (textile, agri, extractives)
```

Implemented in `determineCSDDDPhase(profile: CompanyProfile): CSDDDPhase`.

---

### 2. UFLPA Risk Score (Pub.L.117-78 §3)

```
Risk = PROHIBITED  if entity_list_match = true
                   OR (xuar_operations = true AND clearance_docs = null)

Risk = HIGH        if hs_code ∈ HIGH_PRIORITY_PREFIXES AND xuar_operations = true

Risk = MEDIUM      if xuar_supplier_tier2 = true

Risk = LOW         otherwise
```

Implemented in `assessUFLPARisk()`. The PROHIBITED presumption is **rebuttable** with `clearanceDocumentRef`.

---

### 3. REACH SVHC — Concentration (1907/2006 Art.7)

```
ECHA notification required if:
  concentration_ww > 0.1%   AND
  quantity_per_year > 1 tonne

SDS mandatory (Art.31) if:
  concentration_ww > 0.1%

Ref: REACH Art.7(2) and Art.31
```

---

### 4. Supplier Due Diligence Score (CSDDD Art.5-11)

```
DD_score = Σ (criterion_weight_i × compliance_status_i)

Criteria (example):
  forced_labour_policy:      20%
  env_impact_assessment:     20%
  grievance_mechanism:       20%
  third_party_audit:         20%
  remediation_plan_active:   20%

DD_score < 60 → corrective action mandatory
```

---

### 5. Document Retention Schedule (CSDDD Art.23)

```
retention_end = assessment_date + 5 years
alert_date    = retention_end − 90 days  (early renewal)

Automatic alert in createDueDiligenceRecord() when:
  today > alert_date AND today < retention_end
```

---

## Recommended Machine Learning Models

### 1. NLP / BERT — Sanctioned Entity Screening

**Type**: NLP + fuzzy matching  
**How it works**: Matches supplier names against the OFAC SDN list, EU Consolidated Sanctions, and UN Security Council list using BERT embeddings + cosine similarity. Handles name variants, transliterations, and aliases.  
**Output**: `{supplier_id, match_score, matched_entity, list_source}`. Alert if score > 0.85.  
**Library**: HuggingFace Transformers, Elasticsearch fuzzy  
**Ref**: Devlin et al. (2018) *BERT*, NAACL 2019.

---

### 2. Knowledge Graph — Multi-Tier Supply Chain Mapping

**Type**: Graph database + ML  
**How it works**: Models the SC as a directed graph (Tier1 → Tier2 → Tier3 → commodity origin). Graph propagation algorithms detect hidden exposure to XUAR regions or sanctioned entities in undisclosed deep tiers.  
**Output**: exposure map with identified risk paths.  
**Library**: Neo4j, NetworkX, PyTorch Geometric  
**Ref**: Galkin et al. (2022) *Knowledge Graph Embeddings*, ICLR.

---

### 3. Random Forest — CSDDD Audit Prioritisation

**Type**: Supervised classification  
**Features**: country_risk_index (WB Governance Indicators), sector, annual_spend, audit_history, ESG_rating, employee_count_supplier.  
**Output**: `due_diligence_priority_score` per supplier. Focuses audit resources on the highest-risk suppliers.  
**Library**: scikit-learn  
**Ref**: Breiman (2001) *Machine Learning*.

---

### 4. DistilBERT — Compliance Document Classification

**Type**: Supervised NLP (transfer learning)  
**How it works**: Fine-tuned on compliance documents (audit reports, certifications, SDS, modern slavery statements). Automatically extracts: expiry date, critical findings, remediation items.  
**Output**: `{document_type, expiry_date, critical_findings[], remediation_items[]}`.  
**Library**: HuggingFace `distilbert-base-uncased`, pdfplumber  
**Ref**: Sanh et al. (2019) *DistilBERT*, EMC².

---

### 5. Satellite ML — Deforestation Detection (EU Reg.2023/1115)

**Type**: Multispectral Computer Vision  
**How it works**: Random Forest trained on Sentinel-2 imagery (13 spectral bands) classifies land cover. Compares 2020 mosaics (EU Reg. baseline) against current imagery. Detects forest cover loss in georeferenced supply zones for the 7 high-risk commodities.  
**Output**: `deforestation_alert` with polygon, affected area in ha, detection date.  
**Library**: Google Earth Engine, rasterio, scikit-learn  
**Ref**: Hansen et al. (2013) *High-Resolution Global Maps of 21st-Century Forest Cover Change*, Science 342.

---

## References

- EU Directive 2024/1760 (CSDDD) — Corporate Sustainability Due Diligence
- US Pub.L.117-78 (UFLPA) — Uyghur Forced Labor Prevention Act
- EU REACH Regulation 1907/2006 — Art.7, 31, 33
- Devlin et al. (2018) *BERT: Pre-training of Deep Bidirectional Transformers*, arXiv
- Hansen et al. (2013) Science 342(6160): 850-853
