# 10 — Risk Management

## Overview

Gestiona los riesgos de la cadena de suministro mediante matriz 5×5 (probabilidad × impacto), concentración de proveedores (HHI), efecto bullwhip, pérdida anual esperada (EAL), y planes de continuidad de negocio (BCP) alineados con ISO 22301:2019 (RTO/RPO/MTPD).

---

## KPIs del Departamento

| KPI | Objetivo | Fuente |
|-----|----------|--------|
| Bullwhip Ratio | ≈ 1.0 (target) | Lee et al. (1997) |
| HHI por commodity | < 1,500 (competitivo) | US DOJ |
| Riesgos CRITICAL sin mitigar | 0 | ISO 31000 |
| BCP tests completados / año | ≥ 1 por BCP activo | ISO 22301 |
| RTO achievement % | 100% vs. compromisos | ISO 22301 |
| EAL total portfolio | Monitoreo trimestral | Interno |

---

## Estándares

| Estándar | Alcance |
|----------|---------|
| ISO 31000:2018 | Marco de gestión de riesgos |
| ISO 22301:2019 | Business Continuity Management |
| McKinsey SC Resilience Framework (2021) | Playbook de resiliencia |
| MIT CTL Supply Chain Resilience | Investigación académica |

---

## Archivos del Departamento

| Archivo | Responsabilidad |
|---------|----------------|
| `models/RiskModel.ts` | RiskCategory (9 tipos), calculateRiskLevel() 5×5, RiskItem, herfindahlHirschmanIndex(), bullwhipRatio(), expectedAnnualLoss(), DisruptionScenario |
| `domain/BusinessContinuityPlan.ts` | ISO 22301: RTO/RPO/MTPD, BCPAction (secuenciado con dependencias), BCPTest (TABLETOP/FUNCTIONAL/FULL_SCALE), createBCP(), addTestResult() |

---

## Categorías de Riesgo (9)

`SUPPLIER_DISRUPTION` · `DEMAND_VOLATILITY` · `LOGISTICS_DISRUPTION` · `GEOPOLITICAL` · `NATURAL_DISASTER` · `CYBER_SECURITY` · `REGULATORY_COMPLIANCE` · `FINANCIAL_CREDIT` · `QUALITY_FAILURE`

---

## Modelos Matemáticos Aplicados

### 1. Risk Matrix 5×5 (ISO 31000)

```
Risk_Score = Probability(1-5) × Impact(1-5)

Niveles:
   1 –  8 → LOW      (verde)
   9 – 14 → MEDIUM   (amarillo)
  15 – 19 → HIGH     (naranja)
  20 – 25 → CRITICAL (rojo)

Probabilidad: 1=Raro(<5%), 2=Improbable(5-20%), 3=Posible(20-50%),
              4=Probable(50-80%), 5=Casi_seguro(>80%)
Impacto: 1=Insignificante, ..., 5=Catastrófico
```

Ref: ISO 31000:2018 Annex A.

---

### 2. EAL — Expected Annual Loss

```
EAL_i = P_annual_i × Financial_impact_i

EAL_total = Σ EAL_i  (todos los riesgos del portfolio)

Prioridad de mitigación = EAL_i / Mitigation_cost_i  (ROI de control)
```

---

### 3. HHI — Herfindahl-Hirschman Index

```
HHI = Σ (market_share_i)² × 10,000    [i = proveedor de commodity X]

HHI < 1,500   → concentración baja (competitivo)
1,500–2,500   → concentración moderada
HHI > 2,500   → concentración alta → riesgo de monopolio proveedor
```

Usado para detectar dependencia excesiva en un proveedor por commodity. Ref: US DOJ Merger Guidelines.

---

### 4. Bullwhip Effect Ratio (Lee, Padmanabhan & Whang 1997)

```
BWE = Var(orders_upstream) / Var(demand_downstream)

BWE ≈ 1.0 → SC eficiente (sin amplificación)
BWE > 1.5 → señal de alarma
BWE > 2.0 → distorsión severa → revisión de políticas de orden

Causas: batching, fluctuación de precios, shortage gaming, error de forecast
```

Ref: Lee, Padmanabhan & Whang (1997) *MIT Sloan Management Review*.

---

### 5. RTO / RPO / MTPD (ISO 22301)

```
RTO  = Recovery Time Objective   (tiempo máximo para restaurar operaciones)
RPO  = Recovery Point Objective  (pérdida máxima de datos aceptable)
MTPD = Maximum Tolerable Period of Disruption

Restricción BCP: recovery_time ≤ RTO ≤ MTPD
```

---

### 6. Monte Carlo para Distribución de Pérdidas

```
Para cada simulación s (1..100,000):
  1. Sample p_i ~ Beta(α_i, β_i)          [probabilidad de disruption i]
  2. Sample impact_i ~ LogNormal(μ_i, σ_i) [impacto financiero]
  3. loss_s = Σ p_i × impact_i

VaR_95 = percentile(losses, 95)
VaR_99 = percentile(losses, 99)
```

Ref: Chopra & Meindl (2016) Ch.12.

---

## Modelos de Machine Learning Recomendados

### 1. LSTM — Predicción de Disrupciones

**Tipo**: Serie temporal supervisada  
**Funcionamiento**: Input: 36 meses de indicadores macro (PMI manufacturero, Baltic Dry Index, precios commodity, índices geopolíticos GPR, eventos climáticos). Output: P(disruption) por categoría de riesgo en próximos 30/90 días.  
**Output**: `{risk_category, horizon_days, probability, confidence_interval}`  
**Librería**: TensorFlow, Prophet, FRED API (datos macro)  
**Ref**: Hochreiter & Schmidhuber (1997).

---

### 2. NLP — Early Warning System

**Tipo**: NLP + clasificación de texto  
**Funcionamiento**: Monitorea 50+ fuentes (noticias Reuters/Bloomberg, Twitter/X, GDELT, registros regulatorios). Detecta keywords contextualizados: huelga, inundación, sanción, incendio fabrica, cierre puerto. Calcula severity score por proveedor/región.  
**Output**: alerta en tiempo real con `{supplier_id, risk_type, severity, source_url}`.  
**Librería**: HuggingFace, GDELT API, spaCy  
**Ref**: Radford et al. (2019) GPT-2, OpenAI.

---

### 3. Graph Neural Networks — Riesgo en Cascada

**Tipo**: GNN (Message Passing)  
**Funcionamiento**: Modela la SC como grafo dirigido. Propagación de mensajes simula cómo una falla en Tier-2 se propaga a Tier-1 y ensamblaje final. Identifica single points of failure (nodos con alto betweenness centrality).  
**Output**: mapa de criticidad de nodos; `cascade_risk_score` por proveedor.  
**Librería**: PyTorch Geometric, NetworkX  
**Ref**: Kipf & Welling (2017) ICLR *Semi-Supervised Classification with GCN*.

---

### 4. Bayesian Networks — Interdependencia de Riesgos

**Tipo**: Modelo probabilístico gráfico  
**Funcionamiento**: Modela dependencias condicionales entre riesgos (un evento geopolítico aumenta simultáneamente P(supplier_failure) y P(logistics_disruption)). Calcula distribución de probabilidad conjunta del portfolio de riesgos.  
**Output**: P(escenario combinado) — informa decisiones de cobertura y buffer stock.  
**Librería**: pgmpy, pomegranate, bnlearn (R)  
**Ref**: Pearl (1988) *Probabilistic Reasoning in Intelligent Systems*, Morgan Kaufmann.

---

### 5. RL — Optimización de BCP Response

**Tipo**: Reinforcement Learning (simulación)  
**Funcionamiento**: Agente ejecuta acciones BCP en entorno de disruption simulado. Estado: `(disruption_type, severity, time_elapsed, resources_remaining)`. Acción: siguiente `BCPAction` a ejecutar. Recompensa: `-downtime - cost + customer_satisfaction`. Aprende secuencia óptima de respuesta que minimiza RTO.  
**Output**: política de respuesta optimizada por tipo de disruption.  
**Librería**: Ray RLlib, SimPy (simulación de eventos discretos)  
**Ref**: Ambulkar, Blackhurst & Grawe (2015) *Journal of Operations Management*.

---

## Referencias

- ISO 31000:2018 *Risk Management — Guidelines*
- ISO 22301:2019 *Business Continuity Management Systems*
- Lee, H.L., Padmanabhan, V. & Whang, S. (1997) *The Bullwhip Effect in Supply Chains*, MIT Sloan Management Review
- Chopra, S. & Meindl, P. (2016) *Supply Chain Management*, 6th Ed. Ch.12
- US DOJ/FTC (2010) *Horizontal Merger Guidelines*
