# Departamento 12 — S&OP / Integrated Business Planning (IBP)
## Planificación de Ventas y Operaciones

### Misión
Alinear mensualmente las funciones de ventas, marketing, operaciones, supply chain
y finanzas en un único plan operativo consensuado que equilibre demanda, suministro
y objetivos financieros de la empresa.

### Funciones principales
| Función | Descripción |
|---------|-------------|
| Proceso S&OP mensual | Ciclo de 5 reuniones: datos → demanda → suministro → pre-S&OP → ejecutivo |
| Integrated Business Planning | Horizonte 24-36 meses, granularidad familia de producto |
| Gestión de restricciones | Identificación y resolución de gaps demanda-suministro |
| Escenarios y what-if | Modelado de escenarios optimista/base/pesimista |
| KPI de proceso | Métricas de adherencia al plan |
| Conexión con financiero | Traducción del plan operativo a P&L |

### Ciclo S&OP mensual (proceso de 5 pasos)
```
Semana 1: STEP 1 — Data Review
          ✓ Cierre ventas reales vs. plan
          ✓ Actualización de inventarios y backorders
          ✓ Actualización de datos maestros

Semana 2: STEP 2 — Demand Review (Marketing & Ventas)
          ✓ Revisión pronóstico estadístico
          ✓ Ajustes cualitativos (promociones, lanzamientos)
          ✓ Consensus forecast aprobado

Semana 2: STEP 3 — Supply Review (Operations & SC)
          ✓ Capacidad productiva vs. plan
          ✓ Gaps de inventario y compras
          ✓ Propuestas de mitigación

Semana 3: STEP 4 — Pre-S&OP (Directors)
          ✓ Reconciliación demanda-suministro
          ✓ Resolución de gaps no resueltos
          ✓ Análisis financiero de opciones
          ✓ Recomendaciones al Comité Ejecutivo

Semana 4: STEP 5 — Executive S&OP
          ✓ Decisiones de alto nivel
          ✓ Aprobación del Plan Operativo Mensual
          ✓ Comunicación a toda la organización
```

### KPIs del proceso S&OP
| KPI | Objetivo |
|-----|---------|
| Forecast Accuracy (familia producto, M+1) | MAPE < 10% |
| Plan Adherence (producción vs. plan) | ≥ 90% |
| Inventory vs. Target | ±10% de objetivo |
| Revenue vs. Plan | ≤ 5% desviación |
| S&OP Meeting Attendance | 100% stakeholders clave |
| Gaps Resueltos en Pre-S&OP | > 80% |

### IBP vs S&OP
| Dimensión | S&OP tradicional | IBP (Integrated Business Planning) |
|-----------|-----------------|-------------------------------------|
| Horizonte | 6-12 meses | 24-36 meses |
| Granularidad | Familia producto | SKU/cliente en near-term |
| Integración | Operativa | Financiera completa |
| Herramienta | Hojas de cálculo | IBP platform (SAP IBP, Kinaxis) |
| Frecuencia | Mensual | Mensual + revisiones semanales |

### Archivos clave
- `domain/SOPCycle.ts` — Ciclo mensual S&OP, estados, participantes
- `domain/DemandConsensus.ts` — Forecast consensuado por período
- `domain/SupplyPlan.ts` — Plan de suministro consolidado
- `domain/FinancialBridge.ts` — Traducción plan operativo → P&L
- `domain/Scenario.ts` — Escenarios what-if con impacto financiero
- `services/SOPOrchestrator.ts` — Motor del ciclo mensual
- `services/GapAnalysis.ts` — Identificación y resolución de gaps

### Roles del departamento
- **S&OP / IBP Manager** — Facilitador del proceso
- **Demand Planning Lead** — Pronóstico consensuado
- **Supply Planning Lead** — Plan de suministro
- **Finance Business Partner** — Traducción financiera
- **S&OP Analyst** — Datos, reportes y KPIs

### Referencias
- Wallace, T.F. "Sales and Operations Planning" (2004)
- Palmatier, G. & Crum, C. "Enterprise Sales and Operations Planning" (2003)
- APICS CPIM 9.0 — S&OP process
- Oliver Wight "Class A S&OP" framework
- Gartner — "IBP: The Next Evolution of S&OP"
