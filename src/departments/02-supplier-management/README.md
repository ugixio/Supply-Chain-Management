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
