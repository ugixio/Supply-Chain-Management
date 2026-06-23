# Department 03 — Demand Planning & Forecasting
## Demand Planning and Forecasting

### Mission
Accurately anticipate the future demand of each SKU so that the supply chain
can position itself proactively, minimizing stockouts and excess inventory.

### Main Functions
| Function | Description |
|---------|-------------|
| Statistical forecasting | SMA, SES, Holt, Holt-Winters, ML |
| Demand sensing | Real-time signals: POS, orders, weather |
| Safety stock management | SS calculation using statistical methods |
| EOQ planning | Economic order quantity |
| Collaboration with sales/marketing | Consensus forecast and qualitative adjustments |
| Forecast error analysis | MAE, MAPE, RMSE per SKU |

### Department KPIs
| KPI | World Benchmark | Source |
|-----|------------------|--------|
| Forecast Accuracy (MAPE) | < 15% A-items | APICS CPIM |
| Bias | ≈ 0% (no systematic bias) | Best practice |
| Fill Rate | ≥ 98% | Chopra & Meindl Ch.11 |
| Stock-Out Rate | < 2% | Industry benchmark |
| Days of Inventory Outstanding | Varies by industry | Sector-specific |
| Safety Stock ÷ Avg Inventory | ≤ 20% | Lean SCM |

### Implemented Algorithms
| Algorithm | When to use | Parameters |
|-----------|-------------|-----------|
| SMA | Stable demand, no trend | Period |
| SES (Holt 1957) | Stationary demand | α ∈ (0,1) |
| Holt's Linear | Trend without seasonality | α, β |
| Holt-Winters (1960) | Trend + seasonality | α, β, γ, m |

> **Selection rule**: CV < 10% → SES | with trend → Holt | seasonal → Holt-Winters

### XYZ Segmentation
| Class | CV | Forecast Policy |
|-------|-----|----------------------|
| X | < 10% | Statistical forecast — high confidence |
| Y | 10-25% | Statistical consensus + commercial adjustment |
| Z | > 25% | Scenario planning, higher SS |

### Key Files
- `algorithms/Forecasting.ts` — SMA, SES, Holt, Holt-Winters + metrics
- `algorithms/SafetyStock.ts` — 4 SS methods, EOQ, ROP, DIO
- `domain/DemandPlan.ts` — Demand plan per SKU/period
- `domain/SOPCycle.ts` — Monthly S&OP cycle (inputs/outputs)
- `services/ForecastingService.ts` — Forecasting orchestrator

### Department Roles
- **Demand Planning Manager** — Strategy and S&OP process
- **Demand Planner** — Forecasts by category/region
- **Forecasting Analyst** — Statistical and ML models
- **S&OP Coordinator** — Meetings and consensus

### References
- Holt, C.C. (1957) — Exponentially weighted moving averages
- Winters, P.R. (1960) — "Forecasting Sales by Exponentially Weighted Moving Averages", *Management Science* 6(3)
- Hyndman, R.J. & Athanasopoulos, G. (2021) — *Forecasting: Principles and Practice* (3rd ed., OTexts) https://otexts.com/fpp3/
- Chopra & Meindl Ch.7 "Demand Forecasting in a Supply Chain"
- Ballou Ch.8 — Demand forecasting methods
- APICS/ASCM Supply Chain Dictionary (17th ed., 2024) — *forecast*, *demand management*, *order backlog*
- APICS CPIM 9.0 — Fundamentals of Demand Management

## Applied Mathematical Models

1. **SMA — Simple Moving Average** — F_t = (1/n) × Σ D_{t-i} for i=1..n. Best for stable demand with no trend/season. n=3-6 periods typical.

2. **SES — Single Exponential Smoothing (Holt 1957)** — F_{t+1} = α×D_t + (1-α)×F_t. α∈(0,1). Low α=smooth (stable demand), high α=responsive. Best for stationary demand without trend.

3. **Holt's Linear Method (Double ES)** — Level: L_t = α×D_t + (1-α)×(L_{t-1}+T_{t-1}). Trend: T_t = β×(L_t - L_{t-1}) + (1-β)×T_{t-1}. Forecast: F_{t+h} = L_t + h×T_t. Best for trending demand.

4. **Holt-Winters Triple ES (1960)** — Additive: F_{t+h} = (L_t + h×T_t) + S_{t+h-m}. Parameters: α (level), β (trend), γ (seasonal), m (season length). Best for trend + seasonality. Ref: Holt (1957), Winters (1960).

5. **Safety Stock Method 4 (Combined)** — ss = z × √(LT×σ_D² + D̄²×σ_LT²). Accounts for both demand and lead time variability simultaneously. Most accurate. Ref: Chopra & Meindl Ch.11, Silver/Pyke/Peterson (1998).

6. **EOQ — Economic Order Quantity (Harris 1913)** — Q* = √(2×D×S/H). D=annual demand, S=ordering cost, H=holding cost per unit per year. Minimizes total inventory cost.

7. **MAE, MAPE, RMSE** — MAE=Σ|A-F|/n. MAPE=Σ|A-F|/A × 100/n. RMSE=√(Σ(A-F)²/n). Always compute all three for algorithm selection.

8. **Projected Order Intake** — The authoritative forward-looking measure of orders expected to be received. Combines firm open-order backlog (SAP VBAP) with the statistical demand forecast (Holt-Winters): `Projected Intake = Open Order Value (firm) + ŷₜ₊ₕ × avg_net_price − backlog due to ship`. This is the answer to "how much are we going to receive?" — not the backlog (past) and not the forecast alone (future), but both together. Ref: APICS/ASCM Dictionary — *demand forecast*, *order backlog*; Chopra & Meindl Ch. 7.

9. **Backtesting (Walk-Forward Holdout)** — Mandatory verification step for any forecast. Hold out the last h periods (typically 12 for m=12), fit the model on training data only, project h periods, compute MAPE/WMAPE/RMSE/Bias vs holdout actuals. A model is only deployable when backtest MAPE is within threshold and |Bias| ≈ 0. Without backtesting, a projection is an unvalidated estimate. Ref: Hyndman & Athanasopoulos, *Forecasting: Principles and Practice* (3rd ed., OTexts 2021) §5.8.

10. **Backlog Identity (Audit Control)** — `Ending Backlog = Beginning Backlog + Order Intake − Shipments`. This accounting identity must hold to the cent each period. If it does not, there is a data error (duplicate, gap, or SAP mismatch). It is the supply-chain equivalent of a bank reconciliation. Ref: APICS/ASCM Dictionary — *backlog*; ASC 606 / IFRS 15 revenue recognition.

## Recommended Machine Learning Models

1. **Prophet (Facebook/Meta)** — Additive time-series model: y(t) = trend(t) + seasonality(t) + holidays(t) + ε. Handles missing data, outliers, multiple seasonalities. Best for: SKUs with holiday effects, promotions. Libraries: prophet (Python). Ref: Taylor & Letham (2018).

2. **LSTM / Seq2Seq for Multi-Step Forecasting** — Recurrent neural network. Input: 52 weeks demand + external features (price, promotions, weather). Output: 12-week forecast horizon per SKU. Libraries: TensorFlow, PyTorch. Ref: Hochreiter & Schmidhuber (1997).

3. **LightGBM / XGBoost for Demand Sensing** — Gradient boosting trees. Features: lag features, rolling averages, day-of-week, promotions, price elasticity. Output: short-term (1-4 week) demand. Fast training, interpretable. Libraries: LightGBM, XGBoost.

4. **DeepAR (Amazon)** — Probabilistic RNN that outputs full demand distribution (P10/P50/P90). Trains jointly across all SKUs. Outputs prediction intervals for safety stock calculation. Libraries: GluonTS, SageMaker.

5. **Temporal Fusion Transformers (TFT)** — Attention-based model by Lim et al. (2021). Combines static metadata (SKU class, warehouse), time-varying known inputs (promotions), and observed inputs (sales). State-of-art for interpretable multi-horizon forecasting. Libraries: pytorch-forecasting. Ref: Lim et al. (2021) IJF.
