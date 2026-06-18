# Departamento 09 — Compliance & Regulatory Affairs
## Cumplimiento Normativo y Asuntos Regulatorios

### Misión
Garantizar que todas las actividades de la cadena de suministro cumplan con las
leyes internacionales, regulaciones sectoriales y estándares voluntarios aplicables,
protegiendo a la empresa de sanciones, pérdida de reputación y responsabilidad civil.

### Funciones principales
| Función | Descripción |
|---------|-------------|
| Due diligence CSDDD | Evaluación de impactos DDHH y ambientales |
| Cumplimiento UFLPA | Mapeo cadena de suministro XUAR, evidencia CBP |
| Gestión REACH | SVHCs, fichas de seguridad, notificación ECHA |
| Certificaciones AEO/C-TPAT | Mantenimiento y renovación |
| Ley Moderna Esclavitud | Declaraciones anuales §54 |
| Clasificación arancelaria | Códigos HS, reglas de origen |
| Export controls | ECCN, EAR, ITAR donde aplique |
| Auditorías de cumplimiento | Internas y de terceros |

### Marco regulatorio completo

#### Unión Europea
| Regulación | Ámbito | Umbral | Vigencia |
|-----------|--------|--------|---------|
| **CSDDD** (Dir. 2024/1760) | DDHH y medio ambiente | >5,000 emp. + €1.5bn | Fase 1: Jul 2027 |
| **EU REACH** (EC 1907/2006) | Sustancias químicas | >1 t/año | Vigente |
| **AEO** | Seguridad aduanal | Voluntario | Vigente |
| **EU Timber Reg.** (995/2010) | Madera ilegal | Toda importación | Vigente |
| **Conflict Minerals** (2017/821) | 3TG + cadena | Importadores UE | Vigente |

#### Estados Unidos
| Regulación | Ámbito | Vigencia |
|-----------|--------|---------|
| **UFLPA** (Pub.L.117-78) | Xinjiang forced labour | Jun 2022 |
| **C-TPAT** (CBP) | Seguridad supply chain | Voluntario |
| **FCPA** | Anti-corrupción | Vigente |
| **Dodd-Frank §1502** | Conflict minerals (3TG) | Vigente |
| **UCC Article 2** | Contratos de compraventa | Vigente |

#### Reino Unido
| Regulación | Ámbito | Umbral |
|-----------|--------|--------|
| **Modern Slavery Act 2015 §54** | Esclavitud y trata | ≥ £36m |
| **UK REACH** | Post-Brexit REACH | >1 t/año |
| **Bribery Act 2010** | Anti-corrupción | Universal |

#### Internacional
| Estándar / Convenio | Ámbito |
|---------------------|--------|
| **WTO TFA** Art.7 | Facilitación de comercio |
| **Convenio de Basilea** | Residuos peligrosos transfronterizos |
| **CITES** | Especies en peligro en comercio |
| **ISO 28000:2022** | Seguridad de la cadena de suministro |

### Proceso CSDDD — 6 pasos (Art.5)
```
1. Integrar en políticas corporativas
2. Identificar impactos adversos (DDHH + Medio Ambiente)
3. Prevenir/mitigar impactos potenciales
4. Remediar impactos actuales
5. Establecer mecanismo de quejas (Art.14)
6. Monitorear efectividad y reportar (Art.26 + Art.16)
```

> **Retención documentación**: mínimo **5 años** desde fecha de evaluación (Art.23 CSDDD)
> **Sanción máxima**: 5% del volumen de negocio neto mundial (Art.27)

### Proceso UFLPA
```
Recibir mercancía → ¿Origen XUAR? → SÍ → Detención CBP
                                      → Plazo 30 días para evidencia
                                      → "Clear and convincing evidence"
                                      → Resolución CBP
                                      → NO → Flujo normal
```

### REACH — Obligaciones por umbral
| Concentración SVHC | Obligación |
|-------------------|-----------|
| > 0.1% w/w | Comunicar a clientes B2B (Art.33) |
| > 0.1% w/w + > 1 t/año | Notificar a ECHA (Art.7.2) |
| En Annex XIV | Requiere autorización previa |
| En Annex XVII | Prohibido en usos específicos |

### Archivos clave
- `regulations/CSDDD.ts` — Directiva 2024/1760, due diligence, retención 5 años
- `regulations/UFLPA.ts` — Pub.L.117-78, evaluación por tiers, evidencia CBP
- `regulations/REACH.ts` — SVHCs, evaluación de artículos, notificación ECHA
- `domain/ComplianceRecord.ts` — Registro unificado de cumplimiento
- `domain/ExportControl.ts` — ECCN, EAR99, controles de exportación
- `domain/ConflictMinerals.ts` — 3TG due diligence (Dodd-Frank / EU 2017/821)
- `services/ComplianceService.ts` — Orquestador de evaluaciones
- `services/DueDiligenceService.ts` — Flujo CSDDD 6 pasos

### Roles del departamento
- **Chief Compliance Officer (CCO)** — Gobierno global
- **Trade Compliance Manager** — Importaciones/exportaciones
- **REACH Specialist** — Gestión de sustancias químicas
- **ESG Compliance Analyst** — CSDDD, UFLPA, esclavitud moderna
- **Customs Compliance Specialist** — AEO, C-TPAT, origen
- **Internal Auditor** — Verificación de controles

### Referencias
- EUR-Lex: Directiva (UE) 2024/1760 (CSDDD)
- US CBP: UFLPA Guidance — cbp.gov/trade/forced-labor/UFLPA
- ECHA: EU REACH — echa.europa.eu/regulations/reach
- legislation.gov.uk: Modern Slavery Act 2015 s.54
- ICC Incoterms® 2020 — Publication 723E
