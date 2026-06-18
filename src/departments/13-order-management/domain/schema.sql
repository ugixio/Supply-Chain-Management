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

-- =============================================================================
-- CREDIT CHECK — customer credit limit enforcement
-- Ref: APICS CPIM 9.0 — Order Management / Customer Credit
--      Chopra & Meindl Ch.14
-- =============================================================================

CREATE TABLE order_management.credit_checks (
    id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id             UUID        NOT NULL
                                REFERENCES order_management.customers(id),
    order_id                UUID        NOT NULL
                                REFERENCES order_management.sales_orders(id),

    -- Financial inputs (integer cents, no floats)
    credit_limit_cents      BIGINT      NOT NULL CHECK (credit_limit_cents >= 0),
    outstanding_ar_cents    BIGINT      NOT NULL CHECK (outstanding_ar_cents >= 0),
    new_order_value_cents   BIGINT      NOT NULL CHECK (new_order_value_cents >= 0),

    -- Derived: current_exposure = outstanding_ar + new_order_value
    current_exposure_cents  BIGINT GENERATED ALWAYS AS
                                (outstanding_ar_cents + new_order_value_cents) STORED,

    -- Derived: utilization_pct = current_exposure / credit_limit × 100
    utilization_pct         NUMERIC GENERATED ALWAYS AS (
                                ROUND(
                                    (outstanding_ar_cents + new_order_value_cents)::NUMERIC
                                    / NULLIF(credit_limit_cents, 0) * 100,
                                2)
                            ) STORED,

    -- Credit decision
    status                  VARCHAR(15) NOT NULL
                                CHECK (status IN ('APPROVED','CONDITIONAL','HOLD','BLOCKED')),
    checked_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    approved_by             VARCHAR(200),
    notes                   TEXT,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  order_management.credit_checks IS 'Customer credit evaluations per order. utilization_pct auto-computed. Status: APPROVED (≤80%), CONDITIONAL (80-100%), HOLD (>100%), BLOCKED (account blocked). HOLD and BLOCKED prevent shipment.';
COMMENT ON COLUMN order_management.credit_checks.current_exposure_cents IS 'Auto-computed: outstanding_ar_cents + new_order_value_cents. Total credit exposure if this order ships.';
COMMENT ON COLUMN order_management.credit_checks.utilization_pct        IS 'Auto-computed: current_exposure / credit_limit × 100. Rounded to 2 dp. NULL when credit_limit_cents = 0 (avoid division by zero).';
COMMENT ON COLUMN order_management.credit_checks.status                 IS 'APPROVED: utilization ≤ 80%, ship immediately. CONDITIONAL: 80-100%, flag for review, shipment not blocked. HOLD: >100%, hold order. BLOCKED: account administratively blocked.';

CREATE INDEX idx_credit_checks_customer  ON order_management.credit_checks(customer_id, checked_at DESC);
CREATE INDEX idx_credit_checks_order     ON order_management.credit_checks(order_id);
CREATE INDEX idx_credit_checks_status    ON order_management.credit_checks(status);


-- ---------------------------------------------------------------------------
-- VIEW: v_credit_exposure
-- Current AR + open orders per customer, utilization %, and credit status.
-- ---------------------------------------------------------------------------

CREATE OR REPLACE VIEW order_management.v_credit_exposure AS
SELECT
    c.id                                                        AS customer_id,
    c.customer_code,
    c.name                                                      AS customer_name,
    c.credit_limit_cents,
    -- Outstanding AR: sum of orders in SHIPPED or DELIVERED states
    COALESCE(SUM(
        CASE WHEN o.status IN ('SHIPPED','DELIVERED')
             THEN o.total_cents ELSE 0 END
    ), 0)                                                       AS outstanding_ar_cents,
    -- Open orders: DRAFT + CONFIRMED + PICKING not yet shipped
    COALESCE(SUM(
        CASE WHEN o.status IN ('DRAFT','CONFIRMED','PICKING')
             THEN o.total_cents ELSE 0 END
    ), 0)                                                       AS open_orders_cents,
    -- Total exposure
    COALESCE(SUM(
        CASE WHEN o.status IN ('DRAFT','CONFIRMED','PICKING','SHIPPED','DELIVERED')
             THEN o.total_cents ELSE 0 END
    ), 0)                                                       AS total_exposure_cents,
    -- Utilization
    ROUND(
        COALESCE(SUM(
            CASE WHEN o.status IN ('DRAFT','CONFIRMED','PICKING','SHIPPED','DELIVERED')
                 THEN o.total_cents ELSE 0 END
        ), 0)::NUMERIC
        / NULLIF(c.credit_limit_cents, 0) * 100,
    2)                                                          AS utilization_pct,
    c.payment_terms,
    -- Derived credit status based on utilization
    CASE
        WHEN c.credit_limit_cents = 0 THEN 'BLOCKED'
        WHEN COALESCE(SUM(
            CASE WHEN o.status IN ('DRAFT','CONFIRMED','PICKING','SHIPPED','DELIVERED')
                 THEN o.total_cents ELSE 0 END
        ), 0)::NUMERIC / NULLIF(c.credit_limit_cents, 0) * 100 > 100 THEN 'HOLD'
        WHEN COALESCE(SUM(
            CASE WHEN o.status IN ('DRAFT','CONFIRMED','PICKING','SHIPPED','DELIVERED')
                 THEN o.total_cents ELSE 0 END
        ), 0)::NUMERIC / NULLIF(c.credit_limit_cents, 0) * 100 > 80  THEN 'CONDITIONAL'
        ELSE 'APPROVED'
    END                                                         AS credit_status
FROM order_management.customers c
LEFT JOIN order_management.sales_orders o
       ON o.customer_id = c.id
      AND o.is_deleted = FALSE
WHERE c.is_deleted = FALSE
GROUP BY c.id, c.customer_code, c.name, c.credit_limit_cents, c.payment_terms
ORDER BY utilization_pct DESC NULLS LAST;

COMMENT ON VIEW order_management.v_credit_exposure IS 'Real-time credit exposure per customer: outstanding AR (shipped/delivered) + open orders (draft/confirmed/picking). credit_status mirrors CreditCheck.evaluate() logic from CreditCheck.ts.';


-- =============================================================================
-- REVERSE LOGISTICS / RETURNS
-- Ref: SCOR-DS "Return" process (SR/DR); Chopra & Meindl Ch.13
--      EU Consumer Rights Directive 2011/83/EU (14-day return window)
-- =============================================================================

-- RMA (Return Merchandise Authorization) headers
CREATE TABLE order_management.return_authorizations (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rma_number          VARCHAR(50) NOT NULL UNIQUE,
    original_order_id   UUID NOT NULL REFERENCES order_management.sales_orders(id),
    customer_id         UUID NOT NULL REFERENCES order_management.customers(id),
    status              VARCHAR(20) NOT NULL DEFAULT 'REQUESTED' CHECK (status IN (
        'REQUESTED','APPROVED','IN_TRANSIT','RECEIVED','INSPECTED','CLOSED','REJECTED'
    )),
    reason              VARCHAR(30) NOT NULL CHECK (reason IN (
        'DEFECTIVE','WRONG_ITEM','DAMAGED_IN_TRANSIT',
        'CUSTOMER_CHANGED_MIND','EXCESS_QUANTITY','QUALITY_ISSUE','NEAR_EXPIRY'
    )),
    -- Restocking fee: 0 for defective/damaged; 15% default for change-of-mind
    restocking_fee_pct  NUMERIC(5,2) NOT NULL DEFAULT 0 CHECK (restocking_fee_pct BETWEEN 0 AND 100),
    -- Refund
    refund_cents        BIGINT NOT NULL DEFAULT 0 CHECK (refund_cents >= 0),
    refund_status       VARCHAR(10) NOT NULL DEFAULT 'PENDING' CHECK (refund_status IN ('PENDING','ISSUED','DENIED')),
    rejection_reason    TEXT,
    -- Timeline
    requested_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    approved_at         TIMESTAMPTZ,
    received_at         TIMESTAMPTZ,
    is_deleted          BOOLEAN NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX ON order_management.return_authorizations (customer_id, requested_at DESC);
CREATE INDEX ON order_management.return_authorizations (status, reason);
CREATE INDEX ON order_management.return_authorizations (original_order_id);
COMMENT ON TABLE order_management.return_authorizations IS
    'RMA headers. restocking_fee_pct=0 for DEFECTIVE/DAMAGED; 15% for CUSTOMER_CHANGED_MIND default.';

-- RMA line items — one row per SKU being returned
CREATE TABLE order_management.rma_lines (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rma_id              UUID NOT NULL REFERENCES order_management.return_authorizations(id),
    order_line_id       UUID NOT NULL REFERENCES order_management.sales_order_lines(id),
    sku_id              UUID NOT NULL REFERENCES inventory.sku_master(id),
    return_qty          NUMERIC(18,4) NOT NULL CHECK (return_qty > 0),
    reason              VARCHAR(30) NOT NULL CHECK (reason IN (
        'DEFECTIVE','WRONG_ITEM','DAMAGED_IN_TRANSIT',
        'CUSTOMER_CHANGED_MIND','EXCESS_QUANTITY','QUALITY_ISSUE','NEAR_EXPIRY'
    )),
    disposition         VARCHAR(25) NOT NULL CHECK (disposition IN (
        'RESTOCK','QUARANTINE','SCRAP','RETURN_TO_SUPPLIER','DONATE','REFURBISH'
    )),
    -- Inspection results (populated after physical receipt and inspection)
    inspected_qty       NUMERIC(18,4),
    accepted_qty        NUMERIC(18,4) CHECK (accepted_qty >= 0),
    unit_credit_cents   INTEGER NOT NULL CHECK (unit_credit_cents >= 0),
    -- Computed: accepted_qty × unit_credit_cents × (1 − restocking_fee_pct/100)
    -- Calculated at RMA close time in application layer
    line_credit_cents   BIGINT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT rma_lines_accepted_lte_returned
        CHECK (accepted_qty IS NULL OR accepted_qty <= return_qty)
);
CREATE INDEX ON order_management.rma_lines (rma_id);
CREATE INDEX ON order_management.rma_lines (sku_id);
COMMENT ON COLUMN order_management.rma_lines.disposition IS
    'RESTOCK: serviceable; QUARANTINE: pending quality hold; SCRAP: destroy; '
    'RETURN_TO_SUPPLIER: vendor credit; DONATE: charitable; REFURBISH: repair loop.';

-- Refund issuance tracking — one record per refund payment event
CREATE TABLE order_management.refunds (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    rma_id              UUID NOT NULL REFERENCES order_management.return_authorizations(id),
    amount_cents        BIGINT NOT NULL CHECK (amount_cents > 0),
    currency            CHAR(3) NOT NULL DEFAULT 'USD',
    method              VARCHAR(20) NOT NULL CHECK (method IN ('CREDIT_NOTE','BANK_TRANSFER','STORE_CREDIT')),
    issued_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    reference_number    VARCHAR(100),      -- bank ref, credit note number, etc.
    issued_by           VARCHAR(200),      -- user/system that issued the refund
    notes               TEXT,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX ON order_management.refunds (rma_id);
COMMENT ON TABLE order_management.refunds IS
    'One record per refund payment event. method: CREDIT_NOTE (B2B), BANK_TRANSFER, STORE_CREDIT.';

-- View: returns dashboard — return rate by reason, by SKU, avg refund, monthly
CREATE OR REPLACE VIEW order_management.v_returns_dashboard AS
SELECT
    DATE_TRUNC('month', ra.requested_at)::DATE    AS month,
    ra.reason,
    rl.sku_id,
    COUNT(DISTINCT ra.id)                         AS return_count,
    SUM(rl.return_qty)                            AS total_return_qty,
    SUM(rl.accepted_qty)                          AS total_accepted_qty,
    AVG(ra.refund_cents)                          AS avg_refund_cents,
    SUM(ra.refund_cents)                          AS total_refund_cents,
    -- Return rate against shipped units in same month (join via original order)
    COUNT(DISTINCT ra.id)::NUMERIC /
        NULLIF(
            (SELECT COUNT(*)
             FROM order_management.sales_orders so2
             WHERE DATE_TRUNC('month', so2.created_at) = DATE_TRUNC('month', ra.requested_at)
               AND so2.is_deleted = FALSE
               AND so2.status IN ('SHIPPED','DELIVERED')),
            0
        ) * 100                                    AS return_rate_pct,
    -- Disposition breakdown (counts)
    COUNT(*) FILTER (WHERE rl.disposition = 'RESTOCK')            AS restock_lines,
    COUNT(*) FILTER (WHERE rl.disposition = 'QUARANTINE')         AS quarantine_lines,
    COUNT(*) FILTER (WHERE rl.disposition = 'SCRAP')              AS scrap_lines,
    COUNT(*) FILTER (WHERE rl.disposition = 'RETURN_TO_SUPPLIER') AS return_to_supplier_lines,
    COUNT(*) FILTER (WHERE rl.disposition = 'DONATE')             AS donate_lines,
    COUNT(*) FILTER (WHERE rl.disposition = 'REFURBISH')          AS refurbish_lines
FROM order_management.return_authorizations ra
JOIN order_management.rma_lines rl ON rl.rma_id = ra.id
WHERE ra.is_deleted = FALSE
GROUP BY 1, 2, 3;
