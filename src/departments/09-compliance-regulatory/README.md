# 09 — Compliance & Regulatory

## Overview

Gestiona el cumplimiento de regulaciones internacionales de cadena de suministro: EU CSDDD (diligencia debida), US UFLPA (trabajo forzado Xinjiang), EU REACH (sustancias químicas), LkSG (Alemania), UK Modern Slavery Act, y sanciones globales. Aplica la retención documental obligatoria de 5 años (CSDDD Art.23) y el screening continuo de entidades sancionadas.

---

## KPIs del Departamento

| KPI | Objetivo | Fuente |
|-----|----------|--------|
| Cobertura de due diligence | 100% proveedores Tier-1 | CSDDD Art.5 |
| Acciones de remediación abiertas | 0 críticas pendientes | CSDDD Art.8 |
| Auditorías completadas / plan | ≥ 95% | LkSG §4 |
| Días promedio a remediación | < 90 días | Interno |
| Documentos con retención vigente | 100% (5 años) | CSDDD Art.23 |
| Proveedores UFLPA screened | 100% con operaciones XUAR | UFLPA §3(d) |

---

## Regulaciones Implementadas

| Regulación | Jurisdicción | Umbral / Alcance |
|-----------|-------------|-----------------|
| EU CSDDD Dir.2024/1760 | UE | 3 fases: 2027-2029 (>1,000 empleados) |
| US UFLPA Pub.L.117-78 | EE.UU. | Presunción rebatible — productos XUAR |
| EU REACH 1907/2006 | UE | SVHC >0.1% w/w → notificación Art.7 |
| LkSG Alemania 2023 | Alemania | ≥ 1,000 empleados en Alemania |
| UK Modern Slavery Act §54 | UK | Volumen ≥ £36M → declaración anual |
| EU Deforestation Reg. 2023/1115 | UE | 7 commodities de alto riesgo |

---

## Archivos del Departamento

| Archivo | Responsabilidad |
|---------|----------------|
| `regulations/CSDDD.ts` | CSDDDPhase (3 fases), CompanyProfile, determineCSDDDPhase(), DueDiligenceRecord (retención 5 años), AdverseImpactType |
| `regulations/UFLPA.ts` | UFLPA_HIGH_RISK_REGIONS, UFLPA_HIGH_PRIORITY_HS_PREFIXES, assessUFLPARisk() → PROHIBITED / HIGH / MEDIUM / LOW |
| `regulations/REACH.ts` | SVHCCategory, REACHSubstance, ArticleREACHAssessment, assessREACHCompliance() Art.7/31/33 |

---

## Modelos Matemáticos Aplicados

### 1. Determinación de Fase CSDDD (Dir.2024/1760 Art.2)

```
Fase 1 (2027): employees > 5,000 AND (turnover_EU > €1.5B OR turnover_global > €1.5B)
               OR non-EU company con net_turnover_EU > €1.5B

Fase 2 (2028): employees > 3,000 AND turnover > €900M

Fase 3 (2029): employees > 1,000 AND turnover > €450M
               OR empresas con "high impact sectors" (textil, agro, extractivas)
```

Implementado en `determineCSDDDPhase(profile: CompanyProfile): CSDDDPhase`.

---

### 2. UFLPA Risk Score (Pub.L.117-78 §3)

```
Risk = PROHIBITED  si entity_list_match = true
                   O (xuar_operations = true AND clearance_docs = null)

Risk = HIGH        si hs_code ∈ HIGH_PRIORITY_PREFIXES AND xuar_operations = true

Risk = MEDIUM      si xuar_supplier_tier2 = true

Risk = LOW         en otro caso
```

Implementado en `assessUFLPARisk()`. La presunción PROHIBITED es **rebatible** con `clearanceDocumentRef`.

---

### 3. REACH SVHC — Concentración (1907/2006 Art.7)

```
Notificación ECHA requerida si:
  concentration_ww > 0.1%   AND
  quantity_per_year > 1 tonne

SDS obligatoria (Art.31) si:
  concentration_ww > 0.1%

Ref: REACH Art.7(2) y Art.31
```

---

### 4. Supplier Due Diligence Score (CSDDD Art.5-11)

```
DD_score = Σ (criterion_weight_i × compliance_status_i)

Criterios (ejemplo):
  forced_labour_policy:      20%
  env_impact_assessment:     20%
  grievance_mechanism:       20%
  third_party_audit:         20%
  remediation_plan_active:   20%

DD_score < 60 → acción correctiva obligatoria
```

---

### 5. Calendario de Retención Documental (CSDDD Art.23)

```
retention_end = assessment_date + 5 years
alert_date    = retention_end − 90 days  (renovación anticipada)

Alerta automática en createDueDiligenceRecord() cuando:
  today > alert_date AND today < retention_end
```

---

## Modelos de Machine Learning Recomendados

### 1. NLP / BERT — Screening de Entidades Sancionadas

**Tipo**: NLP + fuzzy matching  
**Funcionamiento**: Coteja nombres de proveedores contra OFAC SDN list, EU Consolidated Sanctions, UN Security Council list usando embeddings BERT + similitud coseno. Maneja variantes de nombre, transliteraciones y aliases.  
**Output**: `{supplier_id, match_score, matched_entity, list_source}`. Alert si score > 0.85.  
**Librería**: HuggingFace Transformers, Elasticsearch fuzzy  
**Ref**: Devlin et al. (2018) *BERT*, NAACL 2019.

---

### 2. Knowledge Graph — Mapeo de Cadena de Suministro Multi-Tier

**Tipo**: Graph database + ML  
**Funcionamiento**: Modela la SC como grafo dirigido (Tier1 → Tier2 → Tier3 → commodity origin). Algoritmos de propagación de grafos detectan exposición oculta a regiones XUAR o entidades sancionadas en tiers profundos no declarados.  
**Output**: mapa de exposición con paths de riesgo identificados.  
**Librería**: Neo4j, NetworkX, PyTorch Geometric  
**Ref**: Galkin et al. (2022) *Knowledge Graph Embeddings*, ICLR.

---

### 3. Random Forest — Priorización de Auditorías CSDDD

**Tipo**: Clasificación supervisada  
**Features**: country_risk_index (WB Governance Indicators), sector, annual_spend, audit_history, ESG_rating, employee_count_supplier.  
**Output**: `due_diligence_priority_score` por proveedor. Focaliza recursos de auditoría en los de mayor riesgo.  
**Librería**: scikit-learn  
**Ref**: Breiman (2001) *Machine Learning*.

---

### 4. DistilBERT — Clasificación de Documentos de Compliance

**Tipo**: NLP supervisado (transfer learning)  
**Funcionamiento**: Fine-tuned en documentos de compliance (informes de auditoría, certificaciones, SDS, declaraciones de esclavitud moderna). Extrae automáticamente: fecha de expiración, hallazgos críticos, ítems de remediación.  
**Output**: `{document_type, expiry_date, critical_findings[], remediation_items[]}`.  
**Librería**: HuggingFace `distilbert-base-uncased`, pdfplumber  
**Ref**: Sanh et al. (2019) *DistilBERT*, EMC².

---

### 5. Satellite ML — Detección de Deforestación (EU Reg.2023/1115)

**Tipo**: Computer Vision multiespectral  
**Funcionamiento**: Random Forest entrenado en imágenes Sentinel-2 (13 bandas espectrales) clasifica cobertura de suelo. Compara mosaicos de 2020 (baseline EU Reg.) vs. actuales. Detecta pérdida de masa forestal en zonas georreferenciadas de proveedores de los 7 commodities de riesgo.  
**Output**: `deforestation_alert` con polígono, área afectada ha, fecha detección.  
**Librería**: Google Earth Engine, rasterio, scikit-learn  
**Ref**: Hansen et al. (2013) *High-Resolution Global Maps of 21st-Century Forest Cover Change*, Science 342.

---

## Referencias

- EU Directiva 2024/1760 (CSDDD) — Corporate Sustainability Due Diligence
- US Pub.L.117-78 (UFLPA) — Uyghur Forced Labor Prevention Act
- EU REACH Regulation 1907/2006 — Art.7, 31, 33
- Devlin et al. (2018) *BERT: Pre-training of Deep Bidirectional Transformers*, arXiv
- Hansen et al. (2013) Science 342(6160): 850-853
