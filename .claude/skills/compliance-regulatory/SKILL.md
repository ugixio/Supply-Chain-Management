---
description: >
  Compliance and regulatory domain expertise for Department 09. Use when reviewing
  CSDDD, UFLPA, EU REACH, human rights due diligence, forced labour screening,
  SVHC substances, or the concept nodes and rules of department 09 (compliance-regulatory).
---

# Compliance & Regulatory — Department 09 Skills Reference

## Supply Chain Domain

**SCOR-DS Mapping**: Enable (E7 — Manage Regulatory Compliance)

**Key Regulations Implemented**

| Regulation | Jurisdiction | Scope | Implementation |
|-----------|-------------|-------|----------------|
| EU CSDDD 2024/1760 | EU | Supply chain due diligence (phased from 2027) | `compliance/CSDDD.ts` |
| LkSG (Lieferkettensorgfaltspflichtengesetz) | Germany | ≥ 1,000 employees from 2024 | `CSDDDDueDiligence` fields |
| UK Modern Slavery Act 2015 §54 | UK | ≥ £36m turnover; annual statement | `Supplier.modernSlaveryStatements` |
| US UFLPA (Pub.L. 117-78) | US | Xinjiang forced labour presumption | `compliance/UFLPA.ts` |
| EU REACH 1907/2006 | EU | Chemical substance management | `compliance/REACH.ts` |
| Basel Convention | International | Hazardous waste transboundary | `ShipmentLine.hazmatClass` |
| US FCPA | US | Anti-bribery (suppliers/agents) | `Supplier.fcpaRiskScore` |

**CSDDD 2024 Phasing** (EU Directive 2024/1760)
| Phase | Year | Companies in scope |
|-------|------|--------------------|
| 1 | 2027 | > 5,000 employees AND > €1.5bn turnover |
| 2 | 2028 | > 3,000 employees AND > €900m turnover |
| 3 | 2029 | > 1,000 employees AND > €450m turnover |
- Document retention: minimum **5 years** from assessment date (Art. 23)
- Annual due diligence report: mandatory public disclosure

**UFLPA Rebuttable Presumption**
- All goods produced in whole or in part in Xinjiang Uyghur Autonomous Region (XUAR) presumed to be made with forced labour
- Rebuttal requires: (1) clear and convincing evidence; (2) full supply chain traceability; (3) CBP approval
- Supplier field: `xuarOperations: boolean` + `clearanceDocumentRef: string`

**EU REACH 1907/2006 — SVHC**
- SVHC (Substances of Very High Concern): >0.1% w/w requires notification to ECHA
- SVHCs in articles > 1 tonne/year: registration required
- Field: `reachSVHC: boolean` on `InventoryItem` triggers lot tracking

**Compliance metrics (GRI, CSDDD, APICS)**

**Metrics — definitions, not levels.** A skill states what a metric measures and what
constrains the answer; the level a project must clear is that project's decision (ADR-0037,
and the inclusion test in `CLAUDE.md`). The right-hand column names the constraint so the
question can be asked properly, and stops.

| Metric | Formula | What constrains the level |
|---|---|---|
| CSDDD assessment coverage | Assessed suppliers / Total in-scope × 100 | **The directive itself, and not as a percentage.** CSDDD 2024/1760 (amended by 2026/470) requires *risk-based* due diligence with a phase-in by company size — it does not mandate a coverage figure. A project that promises "100% of Tier-1" has chosen a policy stronger than the law and must be able to keep it (SCM-R7 for the ≥ 5-year retention). |
| UFLPA-cleared shipments | Cleared / Total XUAR-linked × 100 | **Nothing to choose.** The rebuttable presumption is absolute (Pub. L. 117-78, SCM-R6): an uncleared XUAR-linked shipment is not admissible. This is a count of exceptions, not a target to approach. |
| REACH SVHC communication rate | Communicated / Total SVHC articles × 100 | **The regulation.** Article 33 duty triggers above 0.1% w/w (CMP-R3) and is per article — there is no partial compliance and therefore no level to set. |
| Modern-slavery statement currency | Current-year statements / In-scope × 100 | Which statutes apply (UK MSA s.54, AU MSA, CA SB-657, and their differing thresholds) — the *scope* is legal, the internal refresh cadence is the project's. |
| Compliance audit closure rate | Findings closed / Total findings × 100 | The project's own escalation policy, weighted by finding severity. ISO 19011 fixes how an audit is conducted, not how fast a finding must close. |

## Data Analytics

**UFLPA Risk Screening**
```sql
SELECT s.supplier_id, s.supplier_name, s.country_of_origin,
       s.xuar_operations, s.clearance_document_ref,
       COUNT(pl.po_line_id) AS open_po_lines,
       SUM(pl.total_amount_cents) / 100.0 AS exposure_usd
FROM suppliers s
JOIN po_lines pl ON pl.supplier_id = s.supplier_id
WHERE s.xuar_operations = TRUE
  AND pl.status NOT IN ('RECEIVED', 'CANCELLED')
  AND (s.clearance_document_ref IS NULL OR s.clearance_document_ref = '')
GROUP BY s.supplier_id, s.supplier_name, s.country_of_origin,
         s.xuar_operations, s.clearance_document_ref
ORDER BY exposure_usd DESC;
```

**CSDDD Due Diligence Coverage**
```sql
SELECT assessment_year,
       COUNT(DISTINCT supplier_id) AS assessed_suppliers,
       (SELECT COUNT(*) FROM suppliers WHERE tier = 1 AND is_active = TRUE) AS total_tier1,
       ROUND(COUNT(DISTINCT supplier_id)::float /
             (SELECT COUNT(*) FROM suppliers WHERE tier = 1 AND is_active = TRUE) * 100, 2) AS coverage_pct
FROM csddd_assessments
WHERE assessment_date >= DATE_TRUNC('year', CURRENT_DATE)
GROUP BY assessment_year;
```

**REACH SVHC Inventory Exposure**
```sql
SELECT i.sku_id, i.description, i.reach_svhc_substance,
       SUM(sm.quantity * i.unit_weight_kg) AS total_kg_on_hand,
       CASE WHEN SUM(sm.quantity * i.unit_weight_kg) > 1000 THEN 'REGISTRATION_REQUIRED'
            WHEN i.svhc_concentration_pct > 0.1 THEN 'NOTIFICATION_REQUIRED'
            ELSE 'MONITORING' END AS compliance_status
FROM inventory_items i
JOIN stock_movements sm ON sm.sku_id = i.sku_id
WHERE i.reach_svhc = TRUE
GROUP BY i.sku_id, i.description, i.reach_svhc_substance, i.svhc_concentration_pct;
```

## Data Science

**Supply Chain Mapping (N-tier)**
- Problem: map beyond Tier-1 to identify UFLPA/CSDDD exposure
- Method: graph traversal (BFS/DFS) from brand → Tier-1 → Tier-2 → Tier-N
- Data: supplier disclosure, trade data (UN Comtrade), shipping records
- Output: cascade risk score per node; highlight XUAR-linked nodes

**Forced Labour Risk Scoring**
- Features: country risk score (US DoS TIP Report), ILO indicators, audit findings,
  UFLPA entity list match, Xinjiang connection in supply chain
- Model: rule-based weighted score (0–100); flag > 60 for enhanced due diligence
- Reference: ILO (2014) — 11 Indicators of Forced Labour

## Machine Learning

**Supplier Due Diligence NLP (Contract/Report Extraction)**
```python
from transformers import pipeline
import re

def extract_csddd_risks(document_text: str) -> dict:
    """
    Extract CSDDD-relevant risk indicators from supplier documents.
    Targets: child labour, forced labour, safety violations, environmental harm.
    Model: distilbert-base-uncased (Apache-2.0, HuggingFace).
    Ref: EU CSDDD 2024/1760, Art.3 (adverse impacts definition).
    """
    classifier = pipeline("zero-shot-classification",
                          model="facebook/bart-large-mnli")
    labels = ["forced_labour", "child_labour", "safety_violation",
              "environmental_harm", "anti_corruption", "no_risk"]
    result = classifier(document_text[:512], candidate_labels=labels)
    return dict(zip(result['labels'], result['scores']))
```

**UFLPA Entity List Matching (Fuzzy NLP)**
```python
from difflib import SequenceMatcher
import pandas as pd

def match_uflpa_entities(supplier_names: list[str],
                          entity_list: list[str],
                          threshold: float = 0.85) -> pd.DataFrame:
    """
    Fuzzy match supplier names against UFLPA entity list.
    Returns matches above similarity threshold.
    UFLPA entity list source: US CBP (updated regularly).
    """
    matches = []
    for supplier in supplier_names:
        for entity in entity_list:
            ratio = SequenceMatcher(None, supplier.lower(), entity.lower()).ratio()
            if ratio >= threshold:
                matches.append({'supplier': supplier, 'entity': entity, 'similarity': ratio})
    return pd.DataFrame(matches).sort_values('similarity', ascending=False)
```

## Python

| Library | Use | License |
|---------|-----|---------|
| `pandas` | Compliance DataFrames, audit reports | BSD-3 |
| `networkx` | N-tier supply chain mapping | BSD-3 |
| `transformers` | Document NLP, risk extraction | Apache-2.0 |
| `spacy` | Named entity recognition (NER) | MIT |
| `scikit-learn` | Risk scoring, clustering | BSD-3 |
| `pytesseract` | OCR for scanned compliance docs | Apache-2.0 |
| `rasterio` | Satellite imagery for site verification | BSD-3 |
| `geopandas` | Geospatial supplier mapping | BSD-3 |

**CSDDD Document Retention Check**
```python
from datetime import date, timedelta

def check_csddd_retention(assessment_date: date, retention_years: int = 5) -> dict:
    """
    Verify CSDDD document retention compliance (Art.23: min 5 years).
    Ref: EU Directive 2024/1760, Art.23.
    """
    expiry = assessment_date + timedelta(days=365 * retention_years)
    days_remaining = (expiry - date.today()).days
    return {
        'assessment_date': assessment_date.isoformat(),
        'retention_expiry': expiry.isoformat(),
        'days_remaining': days_remaining,
        'compliant': days_remaining > 0
    }
```

## What a compliance implementation typically needs

*Shapes, not code — ADR-0037 deleted the reference implementation. A project builds these in
its own repository, with its own policy values and its own layout. The names below are the
responsibilities that need a home, not paths in this repository.*

- `CSDDDAssessment.ts` — Due diligence assessment; adverse impact findings; remediation plan
- `UFLPA.ts` — XUAR operations flag; clearance document ref; risk score
- `REACH.ts` — SVHC substance; concentration; notification/registration status
- `ModernSlaveryStatement.ts` — Annual statement; approval date; public URL

**Critical Guards**
```typescript
// UFLPA — must have clearance document if XUAR operations
function validateUFLPACompliance(supplier: Supplier, po: PurchaseOrder): void {
  if (supplier.xuarOperations && !supplier.clearanceDocumentRef) {
    throw new ComplianceError(
      `UFLPA: Supplier ${supplier.id} has XUAR operations but no clearance document. PO blocked.`
    );
  }
}

// CSDDD — document retention minimum 5 years
function validateRetentionPeriod(assessmentDate: Date): void {
  const minRetention = new Date(assessmentDate);
  minRetention.setFullYear(minRetention.getFullYear() + 5);
  if (new Date() > minRetention) {
    throw new ComplianceError('CSDDD Art.23: Document retention period exceeded. Archive required.');
  }
}
```

## OSI / Commercial

| Tool | License | Use |
|------|---------|-----|
| PostgreSQL | PostgreSQL (OSI) | Compliance records, assessment history |
| OpenSearch | Apache-2.0 | Full-text search of compliance docs |
| `pytesseract` | Apache-2.0 | OCR for scanned supplier certificates |
| `rasterio` | BSD-3 | Satellite verification of supplier sites |
| Apache Superset | Apache-2.0 | Compliance coverage dashboards |

**References**
- EU Directive 2024/1760 (CSDDD) — Corporate Sustainability Due Diligence
- Germany LkSG (2023) — Lieferkettensorgfaltspflichtengesetz
- UK Modern Slavery Act 2015, §54 — Transparency in supply chains
- US Pub.L. 117-78 (UFLPA 2021) — Uyghur Forced Labor Prevention Act
- EU REACH Regulation 1907/2006 — Annex XVII SVHC substances; ECHA SVHC Candidate List
- ILO (2014). *Hard to see, harder to count: Survey guidelines to estimate forced labour.* Geneva.
- Basel Convention (1989) — Control of Transboundary Movements of Hazardous Wastes
- GRI 408/409/414 — Child Labour, Forced Labour, Supplier Social Assessment
