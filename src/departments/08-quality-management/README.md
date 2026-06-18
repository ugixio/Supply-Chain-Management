# Departamento 08 — Quality Management (QMS)
## Gestión de Calidad

### Misión
Asegurar que todos los productos y servicios cumplan con los estándares definidos
a través de sistemas de inspección, control preventivo y gestión de no conformidades,
alineados con ISO 9001:2015 y los requisitos específicos del cliente/industria.

### Funciones principales
| Función | Descripción |
|---------|-------------|
| Inspección de entrada | AQL sampling per ISO 2859-1 en cada GRN |
| Control de proceso | SPC, límites de control, Cp/Cpk |
| Gestión de NCR | Non-Conformance Reports y disposición |
| SCAR | Supplier Corrective Action Request |
| Auditorías internas | ISO 9001, HACCP, GMP por sector |
| Gestión de devoluciones | Returns de clientes, RMA |
| Calibración de equipos | MSA — Measurement System Analysis |

### KPIs del departamento
| KPI | Benchmark por sector |
|-----|---------------------|
| Incoming Defect Rate (PPM) | Automotive <500, Food ≤1000, Electrónica <200 |
| DPMO | < 3,4 (Six Sigma); < 1,000 típico |
| First Pass Yield (FPY) | ≥ 99.5% |
| NCR Closure Time | < 30 días (critical) |
| Cost of Quality (CoQ) | < 3% de ventas (world-class) |
| Customer Complaints | Tendencia decreciente |
| SCAR Recurrence Rate | < 5% |
| AQL Lot Rejection Rate | < 2% |

### AQL Sampling — ISO 2859-1
**Niveles de inspección normal (Nivel II)**:

| Tamaño de lote | Muestra | Acepta (AQL 1.5) | Rechaza |
|----------------|---------|-----------------|---------|
| 2-8 | 2 | 0 | 1 |
| 91-150 | 20 | 1 | 2 |
| 281-500 | 50 | 2 | 3 |
| 501-1200 | 80 | 3 | 4 |
| 3201-10000 | 200 | 7 | 8 |

**Clasificación de defectos**:
- **CRITICAL** → Cualquier defecto = RECHAZO inmediato
- **MAJOR** → Impacto funcional → tabla AQL 1.5
- **MINOR** → Cosmético → tabla AQL 4.0

### Disposición de lotes
| Disposición | Acción |
|-------------|--------|
| ACCEPT | Liberar a stock |
| CONDITIONAL_ACCEPT | Usar con restricciones / selección |
| HOLD | Cuarentena hasta decisión MRB |
| REJECT | Devolver proveedor / destruir |

### DPMO y equivalencia Sigma
| DPMO | Nivel Sigma | Rendimiento |
|------|------------|------------|
| 691,462 | 1σ | 30.9% |
| 308,537 | 2σ | 69.1% |
| 66,807 | 3σ | 93.3% |
| 6,210 | 4σ | 99.4% |
| 233 | 5σ | 99.98% |
| 3.4 | 6σ | 99.9997% |

### Archivos clave
- `domain/InspectionRecord.ts` — GRN inspection, AQL, DPMO, NCR
- `domain/NonConformanceReport.ts` — NCR completo con 8D corrective actions
- `domain/CorrectiveAction.ts` — CAPA (Corrective and Preventive Actions)
- `domain/AuditRecord.ts` — Auditorías internas y de proveedor
- `domain/Calibration.ts` — Maestro de equipos de medición
- `services/NCRService.ts` — Generación automática de NCRs
- `services/SCARService.ts` — Envío y seguimiento de SCARs
- `reports/QualityDashboard.ts` — KPIs en tiempo real

### ISO 9001:2015 — Cláusulas implementadas
| Cláusula | Descripción | Archivo |
|----------|-------------|---------|
| §8.4 | Control proveedores externos | Supplier scorecard |
| §8.5.2 | Identificación y trazabilidad | InventoryItem (lot tracking) |
| §8.6 | Liberación de productos | InspectionRecord (disposition) |
| §8.7 | Control de no conformidades | NonConformanceReport |
| §9.1.3 | Análisis y evaluación | SupplierScorecard KPIs |
| §10.2 | No conformidades y acciones | CAPA records |

### Roles del departamento
- **Quality Manager** — Sistema de gestión y auditorías
- **Incoming Quality Inspector** — Inspección física de recepción
- **Supplier Quality Engineer (SQE)** — Auditorías y SCAR
- **Quality Analyst** — SPC, DPMO, reporting
- **NCR Coordinator** — Gestión de no conformidades

### Referencias
- ISO 9001:2015 (transición a 2026 en progreso)
- ISO 2859-1:1999 / ANSI ASQ Z1.4-2008 — AQL sampling
- Six Sigma DPMO methodology — Motorola/GE
- Juran, J.M. "Quality Control Handbook" (2010)
- Crosby, P.B. "Quality Is Free" (1979)
