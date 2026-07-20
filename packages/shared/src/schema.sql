-- =============================================================================
-- SHARED SCHEMA — Cross-department reference tables & ML infrastructure
-- Ref: GS1 General Specifications v23; Vernon (2013) DDD
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS shared;

-- Audit log (append-only)
CREATE TABLE shared.audit_log (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type     VARCHAR(100) NOT NULL,
    entity_id       UUID NOT NULL,
    schema_name     VARCHAR(50) NOT NULL,
    table_name      VARCHAR(100) NOT NULL,
    action          VARCHAR(10) NOT NULL CHECK (action IN ('INSERT','UPDATE','DELETE','SOFT_DELETE')),
    old_data        JSONB,
    new_data        JSONB,
    changed_by      VARCHAR(100),
    changed_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
) PARTITION BY RANGE (changed_at);

CREATE TABLE shared.audit_log_2024 PARTITION OF shared.audit_log
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
CREATE TABLE shared.audit_log_2025 PARTITION OF shared.audit_log
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
CREATE TABLE shared.audit_log_2026 PARTITION OF shared.audit_log
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');
CREATE TABLE shared.audit_log_default PARTITION OF shared.audit_log DEFAULT;

CREATE INDEX ON shared.audit_log (entity_type, entity_id, changed_at DESC);

-- Currency exchange rates
CREATE TABLE shared.exchange_rates (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    base_currency   CHAR(3) NOT NULL DEFAULT 'USD',
    quote_currency  CHAR(3) NOT NULL,
    rate            NUMERIC(18,8) NOT NULL CHECK (rate > 0),
    rate_date       DATE NOT NULL,
    source          VARCHAR(50) DEFAULT 'ECB',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (base_currency, quote_currency, rate_date)
);

-- Country reference
CREATE TABLE shared.countries (
    iso_alpha2      CHAR(2) PRIMARY KEY,
    iso_alpha3      CHAR(3) NOT NULL UNIQUE,
    name            VARCHAR(200) NOT NULL,
    region          VARCHAR(100),
    is_high_risk    BOOLEAN NOT NULL DEFAULT FALSE,   -- UFLPA / FATF risk
    is_sanctioned   BOOLEAN NOT NULL DEFAULT FALSE,
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Incoterms 2020 reference
CREATE TABLE shared.incoterms_2020 (
    code            VARCHAR(5) PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    transport_modes VARCHAR(200),
    risk_transfer   VARCHAR(200),
    dat_replaces    BOOLEAN NOT NULL DEFAULT FALSE
);
INSERT INTO shared.incoterms_2020 VALUES
    ('EXW','Ex Works','Any','At seller premises',FALSE),
    ('FCA','Free Carrier','Any','Named place',FALSE),
    ('FAS','Free Alongside Ship','Sea/Inland','Alongside vessel',FALSE),
    ('FOB','Free On Board','Sea/Inland','On board vessel',FALSE),
    ('CFR','Cost and Freight','Sea/Inland','On board vessel',FALSE),
    ('CIF','Cost Insurance Freight','Sea/Inland','On board vessel',FALSE),
    ('CPT','Carriage Paid To','Any','Carrier handover',FALSE),
    ('CIP','Carriage Insurance Paid','Any','Carrier handover',FALSE),
    ('DAP','Delivered at Place','Any','Named destination',FALSE),
    ('DPU','Delivered at Place Unloaded','Any','After unloading',TRUE),
    ('DDP','Delivered Duty Paid','Any','Named destination',FALSE)
ON CONFLICT DO NOTHING;

-- ML Feature Store (cross-department)
CREATE TABLE shared.ml_feature_store (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type     VARCHAR(50) NOT NULL,   -- 'SKU','SUPPLIER','ORDER','SHIPMENT'
    entity_id       VARCHAR(100) NOT NULL,
    feature_date    DATE NOT NULL,
    feature_set     VARCHAR(100) NOT NULL,  -- e.g. 'demand_forecasting','supplier_risk'
    features        JSONB NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (entity_type, entity_id, feature_date, feature_set)
);
COMMENT ON TABLE shared.ml_feature_store IS 'Central feature store for all ML models. JSONB features keyed by feature_set name';
CREATE INDEX ON shared.ml_feature_store (entity_type, entity_id, feature_date DESC);
CREATE INDEX ON shared.ml_feature_store USING GIN (features);

-- ML Model Registry
CREATE TABLE shared.ml_model_registry (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    model_name      VARCHAR(200) NOT NULL,
    model_type      VARCHAR(50) NOT NULL CHECK (model_type IN (
        'FORECAST','CLASSIFICATION','REGRESSION','CLUSTERING','ANOMALY','REINFORCEMENT','NLP','COMPUTER_VISION'
    )),
    algorithm       VARCHAR(100) NOT NULL,  -- e.g. 'LightGBM','LSTM','Prophet','XGBoost'
    department      VARCHAR(50) NOT NULL,
    version         VARCHAR(20) NOT NULL,
    library         VARCHAR(50) NOT NULL,   -- e.g. 'lightgbm','torch','prophet'
    library_license VARCHAR(20) NOT NULL,   -- must be OSI
    artifact_path   TEXT,
    python_file     TEXT,                   -- e.g. 'python/03_demand_planning/forecasting.py'
    mae             NUMERIC(18,6),
    mape            NUMERIC(8,4),
    rmse            NUMERIC(18,6),
    f1_score        NUMERIC(6,4),
    auc_roc         NUMERIC(6,4),
    train_date      DATE,
    is_production   BOOLEAN NOT NULL DEFAULT FALSE,
    is_deprecated   BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (model_name, version)
);
COMMENT ON TABLE shared.ml_model_registry IS 'All ML model versions, metrics, and artifact paths. OSI libraries only';

-- Warehouses (shared reference)
CREATE TABLE shared.warehouses (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code            VARCHAR(20) NOT NULL UNIQUE,
    name            VARCHAR(200) NOT NULL,
    country_code    CHAR(2) NOT NULL REFERENCES shared.countries(iso_alpha2),
    address         TEXT,
    total_locations INTEGER NOT NULL DEFAULT 0,
    warehouse_type  VARCHAR(20) CHECK (warehouse_type IN ('DC','CROSS_DOCK','3PL','BONDED','COLD_STORE')),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- GL account chart (reference)
CREATE TABLE shared.gl_accounts (
    account_code    VARCHAR(20) PRIMARY KEY,
    account_name    VARCHAR(200) NOT NULL,
    account_type    VARCHAR(20) NOT NULL CHECK (account_type IN ('ASSET','LIABILITY','EQUITY','REVENUE','EXPENSE')),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE
);
