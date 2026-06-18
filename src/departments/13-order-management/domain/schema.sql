-- =============================================================================
-- ORDER MANAGEMENT SCHEMA
-- Ref: APICS CPIM; Chopra & Meindl (2016) Ch.14 (ATP)
--      Walmart OTIF standard 98%
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS order_management;

-- Customer master
CREATE TABLE order_management.customers (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_code   VARCHAR(50) NOT NULL UNIQUE,
    name            VARCHAR(300) NOT NULL,
    country_code    CHAR(2) NOT NULL,
    segment         VARCHAR(30) CHECK (segment IN ('RETAIL','WHOLESALE','ECOMMERCE','B2B','DISTRIBUTOR')),
    credit_limit_cents BIGINT NOT NULL DEFAULT 0,
    payment_terms   VARCHAR(50),
    otif_target_pct NUMERIC(5,2) NOT NULL DEFAULT 98.0,
    is_deleted      BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Sales orders
CREATE TABLE order_management.sales_orders (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_number        VARCHAR(50) NOT NULL UNIQUE,
    customer_id         UUID NOT NULL REFERENCES order_management.customers(id),
    order_date          DATE NOT NULL,
    requested_ship_date DATE NOT NULL,
    confirmed_ship_date DATE,
    status              VARCHAR(20) NOT NULL DEFAULT 'DRAFT' CHECK (status IN (
        'DRAFT','CONFIRMED','PICKING','SHIPPED','DELIVERED','CANCELLED','RETURNED'
    )),
    incoterm            VARCHAR(5) CHECK (incoterm IN ('EXW','FCA','FAS','FOB','CFR','CIF','CPT','CIP','DAP','DPU','DDP')),
    currency            CHAR(3) NOT NULL DEFAULT 'USD',
    total_cents         BIGINT NOT NULL DEFAULT 0,
    shipped_at          TIMESTAMPTZ,
    delivered_at        TIMESTAMPTZ,
    is_on_time          BOOLEAN,
    is_in_full          BOOLEAN,
    is_deleted          BOOLEAN NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX ON order_management.sales_orders (customer_id, order_date DESC);
CREATE INDEX ON order_management.sales_orders (status, requested_ship_date);

-- Sales order lines
CREATE TABLE order_management.sales_order_lines (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id        UUID NOT NULL REFERENCES order_management.sales_orders(id),
    sku_id          UUID NOT NULL REFERENCES inventory.sku_master(id),
    quantity        NUMERIC(18,4) NOT NULL CHECK (quantity > 0),
    uom             VARCHAR(10) NOT NULL DEFAULT 'EA',
    unit_price_cents INTEGER NOT NULL CHECK (unit_price_cents >= 0),
    line_total_cents BIGINT GENERATED ALWAYS AS (ROUND(quantity * unit_price_cents)) STORED,
    qty_shipped     NUMERIC(18,4) NOT NULL DEFAULT 0,
    qty_backorder   NUMERIC(18,4) GENERATED ALWAYS AS (GREATEST(quantity - qty_shipped, 0)) STORED,
    fill_rate_pct   NUMERIC(6,2) GENERATED ALWAYS AS (
        CASE WHEN quantity > 0 THEN ROUND(qty_shipped / quantity * 100, 2) ELSE 0 END
    ) STORED
);

-- ATP (Available to Promise) reservations
CREATE TABLE order_management.atp_reservations (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku_id          UUID NOT NULL REFERENCES inventory.sku_master(id),
    order_line_id   UUID NOT NULL REFERENCES order_management.sales_order_lines(id),
    reserved_qty    NUMERIC(18,4) NOT NULL CHECK (reserved_qty > 0),
    promise_date    DATE NOT NULL,
    source_type     VARCHAR(20) NOT NULL CHECK (source_type IN ('STOCK','PLANNED_ORDER','PRODUCTION')),
    status          VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','CONSUMED','CANCELLED')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE order_management.atp_reservations IS 'ATP: commit qty = on_hand + planned receipts - prior commitments. P95 = μ+1.645σ';

-- OTIF daily KPI
CREATE TABLE order_management.otif_daily_kpi (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    kpi_date            DATE NOT NULL,
    customer_id         UUID REFERENCES order_management.customers(id),
    total_order_lines   INTEGER NOT NULL,
    on_time_lines       INTEGER NOT NULL,
    in_full_lines       INTEGER NOT NULL,
    otif_lines          INTEGER NOT NULL,
    otd_pct             NUMERIC(6,2) GENERATED ALWAYS AS (
        CASE WHEN total_order_lines > 0 THEN ROUND(CAST(on_time_lines AS NUMERIC) / total_order_lines * 100, 2) ELSE 0 END
    ) STORED,
    infull_pct          NUMERIC(6,2) GENERATED ALWAYS AS (
        CASE WHEN total_order_lines > 0 THEN ROUND(CAST(in_full_lines AS NUMERIC) / total_order_lines * 100, 2) ELSE 0 END
    ) STORED,
    otif_pct            NUMERIC(6,2) GENERATED ALWAYS AS (
        CASE WHEN total_order_lines > 0 THEN ROUND(CAST(otif_lines AS NUMERIC) / total_order_lines * 100, 2) ELSE 0 END
    ) STORED,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (kpi_date, customer_id)
);
COMMENT ON COLUMN order_management.otif_daily_kpi.otif_pct IS 'Walmart OTIF standard: 98%. World-class OTD ≥ 95%';

-- Backorder log
CREATE TABLE order_management.backorder_log (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_line_id   UUID NOT NULL REFERENCES order_management.sales_order_lines(id),
    sku_id          UUID NOT NULL REFERENCES inventory.sku_master(id),
    backorder_qty   NUMERIC(18,4) NOT NULL,
    backorder_date  DATE NOT NULL,
    expected_clear_date DATE,
    cleared_at      TIMESTAMPTZ,
    root_cause      VARCHAR(50) CHECK (root_cause IN ('STOCKOUT','SUPPLIER_DELAY','QUALITY_HOLD','FORECAST_ERROR','OTHER')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- View: order performance dashboard
CREATE OR REPLACE VIEW order_management.order_performance AS
SELECT
    DATE_TRUNC('month', o.order_date) AS month,
    c.segment,
    COUNT(*) AS total_orders,
    AVG(EXTRACT(EPOCH FROM (o.delivered_at - o.requested_ship_date::TIMESTAMPTZ)) / 86400) AS avg_delay_days,
    SUM(CASE WHEN o.is_on_time THEN 1 ELSE 0 END)::NUMERIC / COUNT(*) * 100 AS otd_pct,
    SUM(CASE WHEN o.is_in_full THEN 1 ELSE 0 END)::NUMERIC / COUNT(*) * 100 AS infull_pct,
    SUM(CASE WHEN o.is_on_time AND o.is_in_full THEN 1 ELSE 0 END)::NUMERIC / COUNT(*) * 100 AS otif_pct
FROM order_management.sales_orders o
JOIN order_management.customers c ON c.id = o.customer_id
WHERE o.status IN ('SHIPPED','DELIVERED') AND o.is_deleted = FALSE
GROUP BY 1, 2;
