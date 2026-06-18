# Departamento 02 — Supplier Management & Development
## Gestión y Desarrollo de Proveedores

### Misión
Construir y mantener una base de proveedores competitiva, resiliente y sostenible
que maximice el valor entregado midiendo objetivamente el desempeño y desarrollando
capacidades en los socios estratégicos.

### Funciones principales
| Función | Descripción |
|---------|-------------|
| Evaluación de desempeño | Scorecards OTD/OTIF/PPM/DPMO por período |
| Desarrollo de proveedores | Programas de mejora y capacitación |
| Auditorías de proveedores | ISO 9001, C-TPAT, AEO, CSDDD |
| Gestión de relaciones (SRM) | Revisiones Business Review trimestrales |
| Sostenibilidad y ESG | Due diligence ambiental y de DDHH |
| Diversidad de proveedores | Programas de inclusión (MBE/WBE) |

### KPIs del departamento
| KPI | Benchmark mundial | Fuente |
|-----|------------------|--------|
| Supplier OTD | ≥ 95% | Industry standard |
| OTIF | ≥ 98% | Walmart standard |
| PPM (automotive) | < 500 | AIAG |
| PPM (food & bev.) | ≤ 1,000 | GFSI standard |
| Supplier Sustainability Score | ≥ 75/100 | Gartner ESG |
| Diversity Spend | ≥ 15% | McKinsey Diversity |
| Supplier Development ROI | ≥ 5:1 | CIPS research |

### Clasificación de proveedores (Scorecard Rating)
| Rating | Score | Acciones |
|--------|-------|---------|
| PREFERRED | ≥ 90 | Acuerdos largo plazo, VMI, innovación conjunta |
| APPROVED | 75–89 | Relación estándar, revisión semestral |
| CONDITIONAL | 60–74 | Plan de acción correctiva 90 días |
| PROBATION | 45–59 | Revisión mensual, doble fuente activada |
| DISQUALIFIED | < 45 | Descalificación, búsqueda alternativa inmediata |

### Pesos del Scorecard
```
40% Entrega    → OTD (35%) + OTIF (45%) + RFT (20%)
30% Calidad    → PPM score (60%) + Tasa NCR (40%)
20% Comercial  → Exactitud factura (70%) + Variación PO (30%)
10% Soft       → Capacidad de respuesta, cooperación, sostenibilidad
```

### Archivos clave
- `domain/SupplierScorecard.ts` — Cálculo de KPIs y calificación
- `domain/SupplierAudit.ts` — Registros de auditoría ISO/CSDDD/C-TPAT
- `domain/CorrectiveAction.ts` — SCAR (Supplier Corrective Action Request)
- `domain/SupplierDevelopment.ts` — Programas de mejora y capacitación
- `services/ScorecardService.ts` — Servicio de generación periódica
- `reports/` — Reportes trimestrales de desempeño

### Roles del departamento
- **Supplier Relationship Manager (SRM)** — Gestión estratégica de cuentas clave
- **Supplier Quality Engineer (SQE)** — Auditorías y SCAR
- **Supplier Development Specialist** — Programas de mejora
- **ESG / Sustainability Analyst** — CSDDD, UFLPA, carbono

### Referencias
- Chopra & Meindl Ch.14 — Sourcing and supplier relationships
- APICS CPIM 9.0 — Supplier performance management
- ISO 9001:2015 §9.1.3 — Analysis and evaluation
- EU CSDDD Art.26 — Monitoring effectiveness

## Modelos Matemáticos Aplicados

1. **Supplier Scorecard Ponderado** — Score = 0.40×Delivery + 0.30×Quality + 0.20×Commercial + 0.10×Soft. Delivery sub-score = 0.35×OTD + 0.45×OTIF + 0.20×RFT. Quality sub-score = 0.60×PPM_score + 0.40×NCR_rate_score. Ref: APICS CPIM.

2. **PPM (Parts Per Million)** — PPM = (Defective_Units / Total_Units_Inspected) × 1,000,000. Benchmark: <500 automotive (IATF 16949), <1000 food. Ref: ISO 9001:2015.

3. **DPMO (Defects Per Million Opportunities)** — DPMO = (Defects / (Units × Opportunities_per_unit)) × 1,000,000. Six Sigma target: DPMO < 3.4 (6σ). Ref: Montgomery, *Introduction to Statistical Quality Control*.

4. **OTD Rate** — OTD = (Orders_delivered_on_time / Total_orders) × 100. World-class ≥95%. Ref: Chopra & Meindl Ch.3.

5. **Exponential Smoothing para Tendencia de Desempeño** — Score_t = α×Score_actual + (1-α)×Score_{t-1}. Smooths supplier score over time to avoid over-reaction to single-period outliers. α=0.3 recommended.

## Modelos de Machine Learning Recomendados

1. **LSTM para Predicción de Desempeño de Proveedores** — Time-series RNN. Input: 24 months of OTD/PPM/OTIF history per supplier. Output: predicted score next quarter. Flags suppliers trending toward PROBATION. Libraries: TensorFlow/Keras, PyTorch.

2. **Isolation Forest para Detección de Anomalías** — Unsupervised anomaly detection. Detects sudden drops in quality or delivery metrics that may indicate supplier financial distress or capacity issues. Libraries: scikit-learn.

3. **Gradient Boosting (XGBoost) para Riesgo de Quiebra Proveedor** — Supervised classifier. Features: D&B score, payment days, PPM trend, order fill rate. Output: P(supplier_failure) in next 12 months. Libraries: XGBoost, LightGBM.

4. **Graph Neural Networks para Red de Proveedores** — Models supplier-tier relationships as a graph. Detects systemic risk (single-source Tier-2 supplier shared by multiple Tier-1). Output: supply chain concentration risk map. Libraries: PyTorch Geometric, DGL.

5. **NLP Sentiment Analysis para Noticias de Proveedores** — Monitors news/ESG databases for negative signals (strikes, sanctions, disasters). Real-time risk alert. Libraries: HuggingFace, NewsAPI.
