# Departamento 01 — Procurement & Strategic Sourcing
## Adquisiciones y Abastecimiento Estratégico

### Misión
Garantizar el suministro oportuno, con calidad y al mejor costo total de propiedad (TCO),
alineando las decisiones de compra con los objetivos estratégicos de la empresa.

### Funciones principales
| Función | Descripción |
|---------|-------------|
| Abastecimiento estratégico | Selección y calificación de proveedores mediante licitaciones, RFQ/RFP |
| Compras tácticas | Emisión y seguimiento de órdenes de compra (PO) |
| Gestión de contratos | Negociación, administración y renovación de contratos marco |
| Gestión de categorías | Estrategia por familia de producto (Matriz Kraljic) |
| Análisis de gasto | Spend analytics, consolidación y optimización |
| Cumplimiento de proveedores | UFLPA, CSDDD, C-TPAT, ISO 28000 |

### KPIs del departamento
| KPI | Benchmark mundial | Fuente |
|-----|------------------|--------|
| Purchase Order Cycle Time | < 3 días | APICS CPIM 9.0 |
| Procurement Cost Savings | ≥ 3-5% anual | Gartner SCM Top 25 |
| Supplier OTD | ≥ 95% | Chopra & Meindl Ch.14 |
| Contract Compliance Rate | ≥ 90% | CIPS Best Practice |
| Spend Under Management | ≥ 80% | McKinsey Procurement |
| PO Approval Lead Time | < 24 h (automático) | Interna |

### Estándares aplicables
- **ISO 20400:2017** — Sustainable procurement
- **US UCC Article 2** — Quantity in contracts
- **EU Directive 2014/24/EU** — Public procurement (referencia)
- **Incoterms® 2020** — Términos de entrega en cada PO

### Proceso Order-to-PO
```
Necesidad → Requisición → Selección proveedor (Kraljic) →
RFQ/RFP → Evaluación ofertas → Negociación → PO Draft →
Aprobación (workflow) → Envío proveedor → Seguimiento → GRN
```

### Archivos clave
- `domain/PurchaseOrder.ts` — Agregado PO con workflow de aprobación
- `domain/Supplier.ts` — Maestro de proveedores con Matriz Kraljic
- `domain/Contract.ts` — Contratos marco y acuerdos de suministro
- `domain/RFQ.ts` — Solicitudes de cotización y evaluación de ofertas
- `services/ApprovalWorkflow.ts` — Motor de flujos de aprobación
- `services/SpendAnalysis.ts` — Análisis de gasto y ahorros
- `config/thresholds.ts` — Umbrales de aprobación por nivel

### Roles del departamento
- **CPO** (Chief Procurement Officer) — Estrategia y gobierno
- **Category Manager** — Estrategia por categoría, Krajlic
- **Strategic Sourcing Manager** — Licitaciones y contratos
- **Buyer / Procurement Officer** — Emisión y seguimiento de POs
- **Contract Manager** — Redacción y administración de contratos
- **Procurement Analyst** — Spend analytics y reporting

### Referencias académicas y profesionales
- Chopra & Meindl, *Supply Chain Management* 6th Ed., Ch.14 "Sourcing Decisions"
- Kraljic, P. "Purchasing Must Become Supply Management" HBR (1983)
- CIPS (Chartered Institute of Procurement & Supply) — Professional standards
- APICS CPIM 9.0 — Plan Supply module

## Modelos Matemáticos Aplicados

1. **Kraljic Matrix** — 2×2 segmentation: axes = Supply Risk (low/high) × Profit Impact (low/high). Quadrants: NON_CRITICAL, LEVERAGE, BOTTLENECK, STRATEGIC. Used to set negotiation strategy per supplier. Ref: Kraljic (1983), HBR "Purchasing Must Become Supply Management".

2. **RFQ Multi-Criteria Weighted Scoring** — Score_supplier = Σ(weight_i × normalized_score_i) where weights sum to 100%. Criteria: price, quality, delivery, sustainability. Used in `evaluateQuotes()`. Ref: Chopra & Meindl Ch.14.

3. **TCO — Total Cost of Ownership** — TCO = Purchase Price + Ordering Cost + Transport + Inspection + Risk Premium + Supplier Dev Cost. Used to compare suppliers beyond unit price. Ref: Ellram (1993).

4. **Price Escalation Formula** — Adjusted_Price = Base_Price × (1 + CPI_change × weight_material + PPI_change × weight_labor). Used in Contract.ts price escalation clause. Ref: APICS Dictionary.

5. **PO Approval Threshold Rule** — if PO_total > PO_APPROVAL_THRESHOLD_CENTS → status = PENDING_APPROVAL. Binary decision rule to enforce internal controls (SOX compliance).

## Modelos de Machine Learning Recomendados

1. **Random Forest para Clasificación de Proveedores** — Supervised classification. Features: OTD histórico, PPM, financial stability score, country risk index, ESG score. Output: clasificación automática Kraljic (STRATEGIC/LEVERAGE/BOTTLENECK/NON_CRITICAL). Libraries: scikit-learn, XGBoost. Ref: Breiman (2001).

2. **NLP / BERT para Análisis de Contratos** — Transformer-based NLP. Reads contract text, extracts key clauses (penalty terms, SLA, price escalation triggers), flags anomalies. Output: clause risk score per contract. Libraries: HuggingFace Transformers, spaCy. Ref: Devlin et al. (2018).

3. **Regresión Logística / XGBoost para Riesgo de PO** — Binary classifier. Predicts probability that a PO will be delayed or rejected by supplier. Features: supplier history, item complexity, lead time, order size. Output: risk_score 0-1. Libraries: scikit-learn.

4. **Clustering K-Means para Segmentación de Gasto** — Unsupervised. Groups spend categories by volume, frequency, supplier concentration. Output: spend categories for strategic sourcing focus. Libraries: scikit-learn.

5. **Reinforcement Learning para Negociación Automatizada** — Agent learns optimal bid/ask strategies in repeated procurement negotiations. Output: recommended counter-offer price. Libraries: Ray RLlib, Stable-Baselines3. Ref: Baarslag et al. (2017).
