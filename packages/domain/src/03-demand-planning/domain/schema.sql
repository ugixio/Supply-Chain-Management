-- =============================================================================
-- Schema: demand_planning
-- Aligns with: Forecasting.ts, SafetyStock.ts
-- Feeds Python models:
--   python/03_demand_planning/forecasting.py
--     -> sma(demand, period)                 uses sku_demand_history.actual_demand
--     -> ses(demand, alpha)                  uses sku_demand_history.actual_demand
--     -> holts_method(demand, alpha, beta)   uses sku_demand_history.actual_demand
--     -> holt_winters(demand, alpha, beta,   uses sku_demand_history.actual_demand
--                     gamma, m)
--   python/03_demand_planning/safety_stock.py
--     -> method3_ss(z, sigma_d, lt)          uses safety_stock_params
--     -> method4_ss(z, sigma_d, lt_avg,      uses safety_stock_params
--                   sigma_lt, d_avg)
--     -> eoq(annual_demand, order_cost,      uses safety_stock_params + demand_history
--            holding_cost)
--   python/03_demand_planning/demand_sensing.py (LightGBM / Prophet)
--     -> feature table: demand_sensing_features
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS demand_planning;

-- ---------------------------------------------------------------------------
-- sku_demand_history
-- Core time series: actual demand per SKU per period.
-- PARTITIONED BY RANGE (period_date) quarterly for performance.
-- Primary input for ALL forecasting algorithms:
--   SMA, SES (Holt 1957), Holt's Method, Holt-Winters (1960).
-- Holt-Winters requires >= 2 full years (2*m periods) of history.
-- ---------------------------------------------------------------------------
CREATE TABLE demand_planning.sku_demand_history (
    id                UUID          NOT NULL DEFAULT gen_random_uuid(),
    sku_id            VARCHAR(50)   NOT NULL,
    period_date       DATE          NOT NULL,    -- first day of period (month or week)
    period_type       VARCHAR(10)   NOT NULL DEFAULT 'MONTHLY'
                          CHECK (period_type IN ('DAILY','WEEKLY','MONTHLY','QUARTERLY')),
    actual_demand     NUMERIC(15,4) NOT NULL CHECK (actual_demand >= 0),
    uom               CHAR(3)       NOT NULL,   -- GS1 UOM code
    unit_cost_cents   INTEGER       NOT NULL CHECK (unit_cost_cents >= 0),
    -- Decomposition written back by forecasting.py seasonal_decompose()
    trend_component   NUMERIC(15,4),
    seasonal_component NUMERIC(15,4),
    residual_component NUMERIC(15,4),
    is_promotion_period   BOOLEAN   NOT NULL DEFAULT FALSE,
    is_new_product_period BOOLEAN   NOT NULL DEFAULT FALSE,
    data_source       VARCHAR(30)   DEFAULT 'ERP'
                          CHECK (data_source IN ('ERP','MANUAL','EDI','POINT_OF_SALE','FORECAST_SEEDED')),
    warehouse_id      UUID,
    created_at        TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_sku_demand_history PRIMARY KEY (id, period_date),
    CONSTRAINT uq_sku_period UNIQUE (sku_id, period_date, period_type, warehouse_id)
) PARTITION BY RANGE (period_date);

COMMENT ON TABLE demand_planning.sku_demand_history IS
    'Historical actual demand per SKU per period. Partitioned quarterly. '
    'Primary input for python/03_demand_planning/forecasting.py: '
    '  sma(), ses(), holts_method(), holt_winters(). '
    'Holt-Winters requires >= 2 full years of history (24 MONTHLY rows or 8 QUARTERLY). '
    'trend_component, seasonal_component, residual_component written back by '
    'forecasting.py seasonal_decompose(). '
    'Feeds demand_sensing_features (JOIN on sku_id + period_date) for LightGBM/Prophet.';

COMMENT ON COLUMN demand_planning.sku_demand_history.actual_demand IS
    'Confirmed historical demand quantity. is_promotion_period = TRUE flags rows '
    'that forecasting.py should treat as outliers in baseline modelling.';

COMMENT ON COLUMN demand_planning.sku_demand_history.unit_cost_cents IS
    'Standard cost in integer cents at period end. '
    'Used to compute working capital = actual_demand * unit_cost_cents.';

-- Quarterly partitions 2022-2026
CREATE TABLE demand_planning.sku_demand_history_2022q1 PARTITION OF demand_planning.sku_demand_history FOR VALUES FROM ('2022-01-01') TO ('2022-04-01');
CREATE TABLE demand_planning.sku_demand_history_2022q2 PARTITION OF demand_planning.sku_demand_history FOR VALUES FROM ('2022-04-01') TO ('2022-07-01');
CREATE TABLE demand_planning.sku_demand_history_2022q3 PARTITION OF demand_planning.sku_demand_history FOR VALUES FROM ('2022-07-01') TO ('2022-10-01');
CREATE TABLE demand_planning.sku_demand_history_2022q4 PARTITION OF demand_planning.sku_demand_history FOR VALUES FROM ('2022-10-01') TO ('2023-01-01');
CREATE TABLE demand_planning.sku_demand_history_2023q1 PARTITION OF demand_planning.sku_demand_history FOR VALUES FROM ('2023-01-01') TO ('2023-04-01');
CREATE TABLE demand_planning.sku_demand_history_2023q2 PARTITION OF demand_planning.sku_demand_history FOR VALUES FROM ('2023-04-01') TO ('2023-07-01');
CREATE TABLE demand_planning.sku_demand_history_2023q3 PARTITION OF demand_planning.sku_demand_history FOR VALUES FROM ('2023-07-01') TO ('2023-10-01');
CREATE TABLE demand_planning.sku_demand_history_2023q4 PARTITION OF demand_planning.sku_demand_history FOR VALUES FROM ('2023-10-01') TO ('2024-01-01');
CREATE TABLE demand_planning.sku_demand_history_2024q1 PARTITION OF demand_planning.sku_demand_history FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');
CREATE TABLE demand_planning.sku_demand_history_2024q2 PARTITION OF demand_planning.sku_demand_history FOR VALUES FROM ('2024-04-01') TO ('2024-07-01');
CREATE TABLE demand_planning.sku_demand_history_2024q3 PARTITION OF demand_planning.sku_demand_history FOR VALUES FROM ('2024-07-01') TO ('2024-10-01');
CREATE TABLE demand_planning.sku_demand_history_2024q4 PARTITION OF demand_planning.sku_demand_history FOR VALUES FROM ('2024-10-01') TO ('2025-01-01');
CREATE TABLE demand_planning.sku_demand_history_2025q1 PARTITION OF demand_planning.sku_demand_history FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');
CREATE TABLE demand_planning.sku_demand_history_2025q2 PARTITION OF demand_planning.sku_demand_history FOR VALUES FROM ('2025-04-01') TO ('2025-07-01');
CREATE TABLE demand_planning.sku_demand_history_2025q3 PARTITION OF demand_planning.sku_demand_history FOR VALUES FROM ('2025-07-01') TO ('2025-10-01');
CREATE TABLE demand_planning.sku_demand_history_2025q4 PARTITION OF demand_planning.sku_demand_history FOR VALUES FROM ('2025-10-01') TO ('2026-01-01');
CREATE TABLE demand_planning.sku_demand_history_2026q1 PARTITION OF demand_planning.sku_demand_history FOR VALUES FROM ('2026-01-01') TO ('2026-04-01');
CREATE TABLE demand_planning.sku_demand_history_2026q2 PARTITION OF demand_planning.sku_demand_history FOR VALUES FROM ('2026-04-01') TO ('2026-07-01');
CREATE TABLE demand_planning.sku_demand_history_2026q3 PARTITION OF demand_planning.sku_demand_history FOR VALUES FROM ('2026-07-01') TO ('2026-10-01');
CREATE TABLE demand_planning.sku_demand_history_2026q4 PARTITION OF demand_planning.sku_demand_history FOR VALUES FROM ('2026-10-01') TO ('2027-01-01');
CREATE TABLE demand_planning.sku_demand_history_default PARTITION OF demand_planning.sku_demand_history DEFAULT;

-- ---------------------------------------------------------------------------
-- forecast_runs
-- One row per execution of a forecasting algorithm.
-- ---------------------------------------------------------------------------
CREATE TABLE demand_planning.forecast_runs (
    id                UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    run_code          VARCHAR(30) NOT NULL UNIQUE,
    algorithm         VARCHAR(20) NOT NULL
                          CHECK (algorithm IN ('SMA','SES','HOLTS','HOLT_WINTERS',
                                               'ARIMA','SARIMA','PROPHET','LIGHTGBM',
                                               'LSTM','ENSEMBLE')),
    -- Hyperparameters as JSONB:
    -- SMA:          {"period":12}
    -- SES:          {"alpha":0.3}
    -- HOLTS:        {"alpha":0.3,"beta":0.1}
    -- HOLT_WINTERS: {"alpha":0.3,"beta":0.1,"gamma":0.2,"m":12}
    -- PROPHET:      {"changepoint_prior_scale":0.05,"seasonality_mode":"multiplicative"}
    hyperparameters   JSONB,
    horizon_periods   SMALLINT    NOT NULL CHECK (horizon_periods > 0),
    period_type       VARCHAR(10) NOT NULL DEFAULT 'MONTHLY'
                          CHECK (period_type IN ('DAILY','WEEKLY','MONTHLY','QUARTERLY')),
    history_start     DATE,
    history_end       DATE,
    sku_filter        TEXT[],      -- NULL = all SKUs
    status            VARCHAR(15) NOT NULL DEFAULT 'RUNNING'
                          CHECK (status IN ('RUNNING','COMPLETED','FAILED','SUPERSEDED')),
    error_message     TEXT,
    run_duration_ms   INTEGER,
    created_by        VARCHAR(100) NOT NULL,
    created_at        TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    completed_at      TIMESTAMPTZ
);

COMMENT ON TABLE demand_planning.forecast_runs IS
    'One record per forecasting algorithm execution. hyperparameters JSONB stores '
    'algorithm-specific tuning (alpha/beta/gamma/m for Holt-Winters; period for SMA; '
    'seasonality_mode for Prophet). Linked to forecast_results and forecast_accuracy. '
    'status=SUPERSEDED when a newer run of the same algorithm replaces this one.';

COMMENT ON COLUMN demand_planning.forecast_runs.hyperparameters IS
    'JSONB algorithm parameters. SMA:{"period":12} | SES:{"alpha":0.3} | '
    'HOLTS:{"alpha":0.3,"beta":0.1} | '
    'HOLT_WINTERS:{"alpha":0.3,"beta":0.1,"gamma":0.2,"m":12}. '
    'Stored as JSONB to accommodate arbitrary future algorithms without schema changes.';

-- ---------------------------------------------------------------------------
-- forecast_results
-- One row per SKU per future period per forecast run.
-- ---------------------------------------------------------------------------
CREATE TABLE demand_planning.forecast_results (
    id               UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id           UUID          NOT NULL REFERENCES demand_planning.forecast_runs(id) ON DELETE CASCADE,
    sku_id           VARCHAR(50)   NOT NULL,
    period_date      DATE          NOT NULL,
    forecast_value   NUMERIC(15,4) NOT NULL CHECK (forecast_value >= 0),
    lower_ci_80      NUMERIC(15,4),
    upper_ci_80      NUMERIC(15,4),
    lower_ci_95      NUMERIC(15,4),
    upper_ci_95      NUMERIC(15,4),
    trend_component  NUMERIC(15,4),
    seasonal_index   NUMERIC(8,4),     -- Holt-Winters multiplicative factor
    forecast_value_cents BIGINT,       -- forecast_value * unit_cost_cents
    uom              CHAR(3)       NOT NULL,
    created_at       TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    UNIQUE (run_id, sku_id, period_date)
);

COMMENT ON TABLE demand_planning.forecast_results IS
    'Forward-looking forecast per SKU per period. '
    'lower_ci_95/upper_ci_95: 95% prediction intervals. '
    'For SMA/SES: CIs derived via residual std. For Holt-Winters: analytic formula. '
    'For Prophet/LightGBM: model quantile outputs. '
    'seasonal_index is the Holt-Winters gamma-smoothed multiplicative factor.';

-- ---------------------------------------------------------------------------
-- forecast_accuracy
-- Backtesting accuracy metrics per SKU per run.
-- MAE, MAPE, RMSE are mandatory per project standards.
-- ---------------------------------------------------------------------------
CREATE TABLE demand_planning.forecast_accuracy (
    id               UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id           UUID          NOT NULL REFERENCES demand_planning.forecast_runs(id) ON DELETE CASCADE,
    sku_id           VARCHAR(50)   NOT NULL,
    -- MAE  = mean(|actual - forecast|)
    -- MAPE = mean(|actual - forecast| / actual) * 100  [percent]
    -- RMSE = sqrt(mean((actual - forecast)^2))
    mae              NUMERIC(15,4) CHECK (mae  >= 0),
    mape             NUMERIC(8,4)  CHECK (mape >= 0),   -- e.g. 5.3 = 5.3%
    rmse             NUMERIC(15,4) CHECK (rmse >= 0),
    bias             NUMERIC(15,4),    -- mean(forecast - actual); positive = over-forecast
    tracking_signal  NUMERIC(8,4),     -- cumulative_error / MAD; alert if |TS| > 4
    mad              NUMERIC(15,4),
    eval_start       DATE          NOT NULL,
    eval_end         DATE          NOT NULL,
    eval_periods     SMALLINT      NOT NULL,
    naive_mae        NUMERIC(15,4),    -- naive baseline MAE
    skill_score      NUMERIC(8,4),     -- (1 - MAE/naive_MAE)*100; positive = beats naive
    created_at       TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    UNIQUE (run_id, sku_id, eval_start, eval_end)
);

COMMENT ON TABLE demand_planning.forecast_accuracy IS
    'Backtesting accuracy metrics per SKU per forecast run. '
    'MAE, MAPE, RMSE are mandatory (CLAUDE.md). '
    'tracking_signal > 4 or < -4 signals systematic bias -> triggers re-tuning. '
    'skill_score > 0 means the model beats the naive baseline. '
    'Used by forecasting.py auto_select_algorithm() to pick best model per SKU family.';

COMMENT ON COLUMN demand_planning.forecast_accuracy.mape IS
    'Mean Absolute Percentage Error in percent. '
    'Reliable only when actual_demand > 0; intermittent demand SKUs use MAE instead.';

COMMENT ON COLUMN demand_planning.forecast_accuracy.tracking_signal IS
    'Cumulative Forecast Error / MAD. Alert threshold: |TS| > 4 signals persistent bias.';

-- ---------------------------------------------------------------------------
-- safety_stock_params
-- Safety stock and replenishment parameters per SKU.
-- Method 3: ss = z * sigma_D * sqrt(LT)
-- Method 4: ss = z * sqrt(LT * sigma_D^2 + D_bar^2 * sigma_LT^2)
-- EOQ:      sqrt(2 * D * S / H)
-- ---------------------------------------------------------------------------
CREATE TABLE demand_planning.safety_stock_params (
    id                    UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    sku_id                VARCHAR(50)   NOT NULL,
    ss_method             SMALLINT      NOT NULL DEFAULT 3 CHECK (ss_method BETWEEN 1 AND 4),
    service_level_pct     NUMERIC(5,2)  NOT NULL DEFAULT 95.00
                              CHECK (service_level_pct BETWEEN 50 AND 99.99),
    -- z-score (e.g. 1.645 for 95%, 2.054 for 98%, 2.326 for 99%)
    z_score               NUMERIC(6,4)  NOT NULL CHECK (z_score > 0),
    demand_mean           NUMERIC(15,4) NOT NULL CHECK (demand_mean >= 0),
    demand_std            NUMERIC(15,4) NOT NULL CHECK (demand_std  >= 0),
    demand_cv             NUMERIC(8,4)  CHECK (demand_cv >= 0),
    -- Lead time from supplier_mgmt.delivery_metrics_log
    lead_time_avg_days    NUMERIC(6,2)  NOT NULL CHECK (lead_time_avg_days >= 0),
    lead_time_std_days    NUMERIC(6,2)  NOT NULL DEFAULT 0 CHECK (lead_time_std_days >= 0),
    -- Outputs written by safety_stock.py
    safety_stock_qty      NUMERIC(15,4) CHECK (safety_stock_qty >= 0),
    reorder_point         NUMERIC(15,4) CHECK (reorder_point >= 0),
    -- EOQ inputs: sqrt(2 * annual_demand * ordering_cost_cents / holding_cost_per_unit_cents)
    annual_demand         NUMERIC(15,4),
    ordering_cost_cents   INTEGER,
    holding_cost_rate     NUMERIC(6,4),   -- fraction of unit cost per year
    eoq                   NUMERIC(15,4) CHECK (eoq >= 0),
    min_stock_qty         NUMERIC(15,4) DEFAULT 0,
    max_stock_qty         NUMERIC(15,4),
    period_days           SMALLINT      NOT NULL DEFAULT 30 CHECK (period_days > 0),
    calculation_date      DATE          NOT NULL DEFAULT CURRENT_DATE,
    valid_until           DATE,
    source_run_id         UUID          REFERENCES demand_planning.forecast_runs(id),
    is_current            BOOLEAN       NOT NULL DEFAULT TRUE,
    created_at            TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at            TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE demand_planning.safety_stock_params IS
    'Safety stock and replenishment parameters per SKU. '
    'ss_method 1=fixed days | 2=ss=z*sigma_D | 3=ss=z*sigma_D*sqrt(LT) (recommended) | '
    '4=ss=z*sqrt(LT*sigma_D^2+D_bar^2*sigma_LT^2) (use when lead_time_std_days > 0). '
    'eoq = sqrt(2*D*S/H) per Harris (1913). '
    'demand_mean/demand_std sourced from sku_demand_history stats. '
    'lead_time_avg_days/lead_time_std_days from supplier_mgmt.delivery_metrics_log.';

COMMENT ON COLUMN demand_planning.safety_stock_params.ss_method IS
    'Method 1: Fixed days supply. Method 2: ss=z*sigma_D (ignores LT variability). '
    'Method 3: ss=z*sigma_D*sqrt(LT) (Chopra & Meindl Ch.11, recommended). '
    'Method 4: ss=z*sqrt(LT*sigma_D^2+D_bar^2*sigma_LT^2) (most accurate).';

-- ---------------------------------------------------------------------------
-- demand_sensing_features
-- ML feature store for short-horizon demand sensing (1-4 weeks).
-- PRIMARY feature table for LightGBM demand_sensing.py and Prophet regressors.
-- ---------------------------------------------------------------------------
CREATE TABLE demand_planning.demand_sensing_features (
    id                  UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    sku_id              VARCHAR(50)   NOT NULL,
    feature_date        DATE          NOT NULL,
    -- Price features
    unit_price_cents    INTEGER       NOT NULL CHECK (unit_price_cents >= 0),
    price_vs_avg_30d    NUMERIC(8,4),    -- current / 30-day MA
    price_vs_avg_90d    NUMERIC(8,4),    -- current / 90-day MA
    -- Promotional features
    promotion_flag      BOOLEAN       NOT NULL DEFAULT FALSE,
    promotion_type      VARCHAR(20)   CHECK (promotion_type IN (
                            'PRICE_DISCOUNT','BUNDLED','BOGO','SEASONAL','CLEARANCE', NULL
                        )),
    discount_pct        NUMERIC(5,2)  DEFAULT 0,
    -- Calendar features
    holiday_flag        BOOLEAN       NOT NULL DEFAULT FALSE,
    holiday_name        VARCHAR(50),
    day_of_week         SMALLINT      CHECK (day_of_week BETWEEN 1 AND 7),
    week_of_year        SMALLINT      CHECK (week_of_year BETWEEN 1 AND 53),
    month_of_year       SMALLINT      CHECK (month_of_year BETWEEN 1 AND 12),
    quarter             SMALLINT      CHECK (quarter BETWEEN 1 AND 4),
    is_month_end        BOOLEAN       NOT NULL DEFAULT FALSE,
    is_quarter_end      BOOLEAN       NOT NULL DEFAULT FALSE,
    -- External / macro features
    weather_index       NUMERIC(8,4),    -- composite weather severity (0=normal, >1=severe)
    pmi_manufacturing   NUMERIC(5,2),
    fuel_price_index    NUMERIC(8,4),
    -- Market features
    competitor_oos_flag BOOLEAN       NOT NULL DEFAULT FALSE,
    market_share_pct    NUMERIC(5,2),
    -- Lagged demand (computed from sku_demand_history by ETL, cached for training speed)
    demand_lag_1        NUMERIC(15,4),   -- demand t-1
    demand_lag_2        NUMERIC(15,4),   -- demand t-2
    demand_lag_4        NUMERIC(15,4),   -- demand t-4
    demand_lag_12       NUMERIC(15,4),   -- demand t-12 (same period last year for monthly)
    demand_rolling_4w   NUMERIC(15,4),   -- 4-period rolling average
    demand_rolling_13w  NUMERIC(15,4),   -- 13-period rolling average
    -- Target variable (filled after actuals available)
    actual_demand       NUMERIC(15,4),
    created_at          TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    UNIQUE (sku_id, feature_date)
);

COMMENT ON TABLE demand_planning.demand_sensing_features IS
    'ML feature store for short-horizon demand sensing. '
    'PRIMARY input for python/03_demand_planning/demand_sensing.py LightGBM model '
    'and Prophet exogenous regressors (promotion_flag, holiday_flag, weather_index). '
    'demand_lag_* columns pre-computed by ETL from sku_demand_history to avoid '
    'repeated window-function computation during training. '
    'actual_demand populated after period closes; used as training label. '
    'Also consumed by statsforecast MFLES and NHITS models.';

COMMENT ON COLUMN demand_planning.demand_sensing_features.weather_index IS
    'Composite weather severity (0=normal, >1=severe). '
    'Source: ECMWF ERA5 via rasterio/geopandas pipeline (OSI-licensed).';

COMMENT ON COLUMN demand_planning.demand_sensing_features.demand_lag_12 IS
    'Demand 12 periods ago (same month/quarter last year). Critical seasonal feature. '
    'Cached from sku_demand_history by ETL for training speed.';

-- ---------------------------------------------------------------------------
-- xyz_classification
-- XYZ demand variability classification per SKU.
-- X: CV < 0.10 | Y: 0.10-0.25 | Z: > 0.25
-- ---------------------------------------------------------------------------
CREATE TABLE demand_planning.xyz_classification (
    id                 UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    sku_id             VARCHAR(50) NOT NULL,
    cv                 NUMERIC(8,4) NOT NULL CHECK (cv >= 0),
    xyz_class          CHAR(1)     NOT NULL CHECK (xyz_class IN ('X','Y','Z')),
    window_start       DATE        NOT NULL,
    window_end         DATE        NOT NULL,
    periods_used       SMALLINT    NOT NULL,
    demand_mean        NUMERIC(15,4),
    demand_std         NUMERIC(15,4),
    previous_xyz_class CHAR(1)    CHECK (previous_xyz_class IN ('X','Y','Z')),
    class_changed      BOOLEAN     NOT NULL DEFAULT FALSE,
    reclassified_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_current         BOOLEAN     NOT NULL DEFAULT TRUE,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE demand_planning.xyz_classification IS
    'Demand variability (XYZ) classification per SKU. cv = std / mean. '
    'X: CV<0.10 (stable) | Y: 0.10-0.25 (moderate) | Z: >0.25 (volatile). '
    'Combined with ABC class from inventory_items to form ABC-XYZ matrix. '
    'AX = high-value predictable (MRP/kanban) | CZ = low-value volatile (buffer stock). '
    'SKUs with cv > 0.5 switch to Method 4 safety stock (demand_sensing.py flag).';

-- ---------------------------------------------------------------------------
-- Indexes
-- ---------------------------------------------------------------------------
CREATE INDEX idx_demand_hist_sku     ON demand_planning.sku_demand_history(sku_id, period_date);
CREATE INDEX idx_demand_hist_period  ON demand_planning.sku_demand_history(period_date, period_type);

CREATE INDEX idx_runs_algo           ON demand_planning.forecast_runs(algorithm, status);
CREATE INDEX idx_runs_date           ON demand_planning.forecast_runs(created_at);

CREATE INDEX idx_results_run         ON demand_planning.forecast_results(run_id, sku_id);
CREATE INDEX idx_results_sku         ON demand_planning.forecast_results(sku_id, period_date);

CREATE INDEX idx_accuracy_run        ON demand_planning.forecast_accuracy(run_id);
CREATE INDEX idx_accuracy_sku        ON demand_planning.forecast_accuracy(sku_id, mae);

CREATE INDEX idx_ss_sku_current      ON demand_planning.safety_stock_params(sku_id) WHERE is_current = TRUE;
CREATE INDEX idx_ss_method           ON demand_planning.safety_stock_params(ss_method, calculation_date);

CREATE INDEX idx_dsf_sku_date        ON demand_planning.demand_sensing_features(sku_id, feature_date);
CREATE INDEX idx_dsf_date            ON demand_planning.demand_sensing_features(feature_date);
CREATE INDEX idx_dsf_promo           ON demand_planning.demand_sensing_features(feature_date) WHERE promotion_flag = TRUE;

CREATE INDEX idx_xyz_sku_current     ON demand_planning.xyz_classification(sku_id) WHERE is_current = TRUE;
CREATE INDEX idx_xyz_class           ON demand_planning.xyz_classification(xyz_class) WHERE is_current = TRUE;

-- ---------------------------------------------------------------------------
-- VIEW: v_forecast_vs_actual
-- ---------------------------------------------------------------------------
CREATE VIEW demand_planning.v_forecast_vs_actual AS
SELECT
    fr.sku_id,
    fr.period_date,
    fr.forecast_value,
    fr.lower_ci_95,
    fr.upper_ci_95,
    dh.actual_demand,
    (fr.forecast_value - dh.actual_demand)                         AS forecast_error,
    ABS(fr.forecast_value - dh.actual_demand)                      AS abs_error,
    CASE
        WHEN dh.actual_demand > 0
        THEN ABS(fr.forecast_value - dh.actual_demand) / dh.actual_demand * 100
        ELSE NULL
    END                                                             AS abs_pct_error,
    (dh.actual_demand BETWEEN fr.lower_ci_95 AND fr.upper_ci_95)   AS within_95ci,
    run.algorithm,
    run.run_code,
    run.status AS run_status
FROM demand_planning.forecast_results fr
JOIN demand_planning.forecast_runs run      ON fr.run_id      = run.id
JOIN demand_planning.sku_demand_history dh
    ON dh.sku_id = fr.sku_id AND dh.period_date = fr.period_date
WHERE run.status = 'COMPLETED';

COMMENT ON VIEW demand_planning.v_forecast_vs_actual IS
    'Forecast vs actuals per SKU per period for accuracy dashboard. '
    'abs_pct_error is the per-row MAPE component. '
    'within_95ci tracks prediction interval calibration (target ~95% coverage). '
    'Consumed by forecasting.py to populate forecast_accuracy.';

-- ---------------------------------------------------------------------------
-- VIEW: v_sku_replenishment_params
-- ---------------------------------------------------------------------------
CREATE VIEW demand_planning.v_sku_replenishment_params AS
SELECT
    sp.sku_id,
    sp.ss_method,
    sp.service_level_pct,
    sp.z_score,
    sp.demand_mean,
    sp.demand_std,
    sp.demand_cv,
    sp.lead_time_avg_days,
    sp.lead_time_std_days,
    sp.safety_stock_qty,
    sp.reorder_point,
    sp.eoq,
    sp.min_stock_qty,
    sp.max_stock_qty,
    sp.calculation_date,
    sp.valid_until,
    xyz.xyz_class,
    xyz.cv AS xyz_cv
FROM demand_planning.safety_stock_params sp
LEFT JOIN demand_planning.xyz_classification xyz
    ON xyz.sku_id = sp.sku_id AND xyz.is_current = TRUE
WHERE sp.is_current = TRUE;

COMMENT ON VIEW demand_planning.v_sku_replenishment_params IS
    'Current replenishment parameters per SKU (safety stock + XYZ class). '
    'Consumed by inventory module to set min_stock/reorder_point in inventory_items. '
    'Also read by WMS slotting algorithm to adjust buffer quantities by storage zone.';

-- ---------------------------------------------------------------------------
-- VIEW: v_algorithm_comparison
-- ---------------------------------------------------------------------------
CREATE VIEW demand_planning.v_algorithm_comparison AS
SELECT
    fa.sku_id,
    run.algorithm,
    fa.eval_start,
    fa.eval_end,
    fa.eval_periods,
    fa.mae,
    fa.mape,
    fa.rmse,
    fa.bias,
    fa.tracking_signal,
    fa.skill_score,
    RANK() OVER (PARTITION BY fa.sku_id, fa.eval_start ORDER BY fa.mae)  AS rank_by_mae,
    RANK() OVER (PARTITION BY fa.sku_id, fa.eval_start ORDER BY fa.mape) AS rank_by_mape,
    RANK() OVER (PARTITION BY fa.sku_id, fa.eval_start ORDER BY fa.rmse) AS rank_by_rmse
FROM demand_planning.forecast_accuracy fa
JOIN demand_planning.forecast_runs run ON fa.run_id = run.id
WHERE run.status = 'COMPLETED';

COMMENT ON VIEW demand_planning.v_algorithm_comparison IS
    'Side-by-side MAE/MAPE/RMSE comparison across algorithms per SKU and evaluation window. '
    'rank_by_mae=1 = best performing algorithm by MAE. '
    'Used by forecasting.py select_best_algorithm() to auto-assign algorithm per SKU family.';
