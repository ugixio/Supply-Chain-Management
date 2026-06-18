# Departamento 03 — Demand Planning & Forecasting
## Planificación de Demanda y Pronósticos

### Misión
Anticipar con precisión la demanda futura de cada SKU para que la cadena de suministro
pueda posicionarse proactivamente, minimizando rupturas de stock y excesos de inventario.

### Funciones principales
| Función | Descripción |
|---------|-------------|
| Pronóstico estadístico | SMA, SES, Holt, Holt-Winters, ML |
| Demand sensing | Señales en tiempo real: POS, pedidos, clima |
| Gestión de inventario de seguridad | Cálculo de SS por método estadístico |
| Planificación EOQ | Cantidad económica de pedido |
| Colaboración con ventas/marketing | Consensus forecast y ajustes cualitativos |
| Análisis de errores de pronóstico | MAE, MAPE, RMSE por SKU |

### KPIs del departamento
| KPI | Benchmark mundial | Fuente |
|-----|------------------|--------|
| Forecast Accuracy (MAPE) | < 15% productos A | APICS CPIM |
| Bias | ≈ 0% (sin sesgo sistemático) | Best practice |
| Fill Rate | ≥ 98% | Chopra & Meindl Ch.11 |
| Stock-Out Rate | < 2% | Industry benchmark |
| Days of Inventory Outstanding | Varía por industria | Sector-specific |
| Safety Stock ÷ Avg Inventory | ≤ 20% | Lean SCM |

### Algoritmos implementados
| Algoritmo | Cuándo usar | Parámetros |
|-----------|-------------|-----------|
| SMA | Demanda estable, sin tendencia | Período |
| SES (Holt 1957) | Demanda estacionaria | α ∈ (0,1) |
| Holt's Linear | Tendencia sin estacionalidad | α, β |
| Holt-Winters (1960) | Tendencia + estacionalidad | α, β, γ, m |

> **Regla de selección**: CV < 10% → SES | con tendencia → Holt | estacional → Holt-Winters

### Segmentación XYZ
| Clase | CV | Política de pronóstico |
|-------|-----|----------------------|
| X | < 10% | Pronóstico estadístico — alta confianza |
| Y | 10-25% | Consenso estadístico + ajuste comercial |
| Z | > 25% | Planificación por escenarios, más SS |

### Archivos clave
- `algorithms/Forecasting.ts` — SMA, SES, Holt, Holt-Winters + métricas
- `algorithms/SafetyStock.ts` — 4 métodos SS, EOQ, ROP, DIO
- `domain/DemandPlan.ts` — Plan de demanda por SKU/período
- `domain/SOPCycle.ts` — Ciclo mensual S&OP (inputs/outputs)
- `services/ForecastingService.ts` — Orquestador de pronósticos

### Roles del departamento
- **Demand Planning Manager** — Estrategia y proceso S&OP
- **Demand Planner** — Pronósticos por categoría/región
- **Forecasting Analyst** — Modelos estadísticos y ML
- **S&OP Coordinator** — Reuniones y consenso

### Referencias
- Holt, C.C. (1957) — Exponentially weighted moving averages
- Winters, P.R. (1960) — Triple exponential smoothing
- Chopra & Meindl Ch.7 "Demand Forecasting in a Supply Chain"
- Ballou Ch.8 — Demand forecasting methods
- APICS CPIM 9.0 — Fundamentals of Demand Management
