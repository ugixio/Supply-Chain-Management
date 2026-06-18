# Departamento 10 — Supply Chain Risk Management
## Gestión de Riesgos de la Cadena de Suministro

### Misión
Identificar, cuantificar y mitigar los riesgos que puedan interrumpir el flujo de
materiales, información o capital en la cadena de suministro, construyendo resiliencia
proactiva alineada con el marco de McKinsey: Basic → Managed → Advanced → Leading.

### Funciones principales
| Función | Descripción |
|---------|-------------|
| Mapeo de riesgos | Identificación por categoría (supply, demand, ESG, cyber) |
| Evaluación cuantitativa | Matriz 5×5, HHI concentración, pérdida anual esperada |
| Business Continuity (BCP) | Planes de continuidad por escenario |
| Monitoreo Bullwhip | Ratio Var(pedidos)/Var(demanda) |
| Risk intelligence | Seguimiento geopolítico, clima, proveedores |
| Crisis management | Respuesta y comunicación en disrupciones |

### KPIs del departamento
| KPI | Objetivo |
|-----|---------|
| Supplier Concentration Risk (HHI) | < 1,500 (no concentrado) |
| Bullwhip Ratio | ≈ 1.0 (target) |
| MTTR (Mean Time To Recover) | < 72 h para disrupciones menores |
| Supply Chain Resilience Score | ≥ 70/100 (Gartner framework) |
| BCP Test Success Rate | ≥ 95% |
| Risk Mitigation Coverage | ≥ 80% de riesgos HIGH/CRITICAL |
| EAL (Expected Annual Loss) | Tendencia decreciente |

### Taxonomía de riesgos
| Categoría | Ejemplos | Estrategia base |
|-----------|---------|----------------|
| SUPPLY | Quiebra proveedor, escasez MP, single-source | Dual sourcing, safety stock estratégico |
| DEMAND | Bullwhip effect, error de pronóstico, Black Swan | Hedging, flex capacity |
| OPERATIONAL | Falla calidad, capacidad, proceso | SPC, mantenimiento preventivo |
| LOGISTICS | Congestión portuaria, huelgas | Rutas alternativas, modos alternativos |
| GEOPOLITICAL | Aranceles, sanciones UFLPA, conflictos | Reshoring, diversificación regional |
| REGULATORY | CSDDD, REACH, UFLPA incumplimiento | Due diligence, compliance dept. |
| CYBER | Ransomware, fraude EDI, phishing | Zero-trust, MFA, incident response |
| ESG | Trabajo forzado, deforestación, carbono | Auditorías, CSDDD, descarbonización |
| FINANCIAL | Insolvencia proveedor, FX, commodities | Seguro crédito, hedging FX |

### Matriz de Riesgo 5×5
```
Impacto →      1           2           3           4           5
               Negligible  Menor       Moderado    Mayor       Catastrófico
Probabilidad ↓
5 Casi cierto  MEDIO(5)   ALTO(10)    ALTO(15)    CRIT(20)    CRIT(25)
4 Probable     BAJO(4)    MEDIO(8)    ALTO(12)    CRIT(16)    CRIT(20)
3 Posible      BAJO(3)    MEDIO(6)    MEDIO(9)    ALTO(12)    ALTO(15)
2 Improbable   BAJO(2)    BAJO(4)     MEDIO(6)    MEDIO(8)    ALTO(10)
1 Raro         BAJO(1)    BAJO(2)     BAJO(3)     BAJO(4)     MEDIO(5)
```
Score: BAJO<4 | MEDIO 4-7 | ALTO 8-14 | CRÍTICO ≥15

### HHI — Concentración de proveedores
```
HHI = Σ(participación_i²)   donde participación en % de compra
```
| HHI | Concentración | Recomendación |
|-----|--------------|--------------|
| < 1,500 | Baja | Monitoreo anual |
| 1,500-2,500 | Moderada | Calificar proveedor alternativo |
| > 2,500 | Alta | **Acción inmediata**: dual source |

### Bullwhip Effect — Causas y remedios
```
Ratio = Var(órdenes emitidas) / Var(demanda del cliente)
```
| Causa | Remedio |
|-------|---------|
| Actualización de pronóstico | Compartir datos POS en tiempo real |
| Loteo de pedidos | Pedidos más frecuentes y pequeños |
| Fluctuación de precios | Precios estables, contratos marco |
| Shortage gaming | Asignación racional en escasez |

### Archivos clave
- `models/RiskModel.ts` — Taxonomía, matriz 5×5, HHI, bullwhip, EAL
- `domain/RiskRegister.ts` — Registro de riesgos con owner y acciones
- `domain/BusinessContinuityPlan.ts` — BCP por escenario de disrución
- `domain/CrisisEvent.ts` — Registro de eventos de crisis y respuesta
- `services/RiskMonitor.ts` — Monitoreo continuo y alertas
- `services/ScenarioAnalysis.ts` — Monte Carlo, análisis de escenarios

### Madureez de resiliencia (McKinsey Framework)
| Nivel | Descripción | Características |
|-------|-------------|----------------|
| **Basic** | Reactivo | No hay visibilidad tier-2+; respuesta ad hoc |
| **Managed** | Riesgos identificados | Playbooks de respuesta; monitoreo tier-1 |
| **Advanced** | Multi-tier visibility | Simulaciones; planes probados; KPIs en tiempo real |
| **Leading** | Predictivo | AI/ML; red dinámica; auto-corrección |

### Roles del departamento
- **Chief Risk Officer (CRO) / SC Risk Director** — Estrategia y gobierno
- **Supply Chain Risk Analyst** — Evaluación y registro
- **Business Continuity Manager** — BCP y pruebas
- **Regulatory Risk Specialist** — Riesgos de cumplimiento
- **Geopolitical Intelligence Analyst** — Monitoreo externo

### Referencias
- Chopra & Meindl Ch.12 "Managing Supply Chain Risk"
- MIT CTL — Supply Chain Resilience research
- McKinsey (2021) "Building Supply Chain Resilience"
- Lee, Padmanabhan & Whang (1997) MIT Sloan — The Bullwhip Effect
- Herfindahl-Hirschman Index — US DOJ merger guidelines
