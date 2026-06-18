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

## Modelos Matemáticos Aplicados

1. **SMA — Simple Moving Average** — F_t = (1/n) × Σ D_{t-i} for i=1..n. Best for stable demand with no trend/season. n=3-6 periods typical.

2. **SES — Single Exponential Smoothing (Holt 1957)** — F_{t+1} = α×D_t + (1-α)×F_t. α∈(0,1). Low α=smooth (stable demand), high α=responsive. Best for stationary demand without trend.

3. **Holt's Linear Method (Double ES)** — Level: L_t = α×D_t + (1-α)×(L_{t-1}+T_{t-1}). Trend: T_t = β×(L_t - L_{t-1}) + (1-β)×T_{t-1}. Forecast: F_{t+h} = L_t + h×T_t. Best for trending demand.

4. **Holt-Winters Triple ES (1960)** — Additive: F_{t+h} = (L_t + h×T_t) + S_{t+h-m}. Parameters: α (level), β (trend), γ (seasonal), m (season length). Best for trend + seasonality. Ref: Holt (1957), Winters (1960).

5. **Safety Stock Method 4 (Combined)** — ss = z × √(LT×σ_D² + D̄²×σ_LT²). Accounts for both demand and lead time variability simultaneously. Most accurate. Ref: Chopra & Meindl Ch.11, Silver/Pyke/Peterson (1998).

6. **EOQ — Economic Order Quantity (Harris 1913)** — Q* = √(2×D×S/H). D=annual demand, S=ordering cost, H=holding cost per unit per year. Minimizes total inventory cost.

7. **MAE, MAPE, RMSE** — MAE=Σ|A-F|/n. MAPE=Σ|A-F|/A × 100/n. RMSE=√(Σ(A-F)²/n). Always compute all three for algorithm selection.

## Modelos de Machine Learning Recomendados

1. **Prophet (Facebook/Meta)** — Additive time-series model: y(t) = trend(t) + seasonality(t) + holidays(t) + ε. Handles missing data, outliers, multiple seasonalities. Best for: SKUs with holiday effects, promotions. Libraries: prophet (Python). Ref: Taylor & Letham (2018).

2. **LSTM / Seq2Seq para Pronóstico Multi-Step** — Recurrent neural network. Input: 52 weeks demand + external features (price, promotions, weather). Output: 12-week forecast horizon per SKU. Libraries: TensorFlow, PyTorch. Ref: Hochreiter & Schmidhuber (1997).

3. **LightGBM / XGBoost para Demand Sensing** — Gradient boosting trees. Features: lag features, rolling averages, day-of-week, promotions, price elasticity. Output: short-term (1-4 week) demand. Fast training, interpretable. Libraries: LightGBM, XGBoost.

4. **DeepAR (Amazon)** — Probabilistic RNN that outputs full demand distribution (P10/P50/P90). Trains jointly across all SKUs. Outputs prediction intervals for safety stock calculation. Libraries: GluonTS, SageMaker.

5. **Temporal Fusion Transformers (TFT)** — Attention-based model by Lim et al. (2021). Combines static metadata (SKU class, warehouse), time-varying known inputs (promotions), and observed inputs (sales). State-of-art for interpretable multi-horizon forecasting. Libraries: pytorch-forecasting. Ref: Lim et al. (2021) IJF.
