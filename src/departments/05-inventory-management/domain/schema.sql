-- =============================================================================
-- INVENTORY MANAGEMENT SCHEMA (Event Sourcing)
-- Ref: Vernon (2013) Implementing Domain-Driven Design
--      Chopra & Meindl (2016) Ch.11
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS inventory;

-- SKU master (shared reference table)
CREATE TABLE inventory.sku_master (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku_code            VARCHAR(50) NOT NULL UNIQUE,
    name                VARCHAR(500) NOT NULL,
    description         TEXT,
    uom                 VARCHAR(10) NOT NULL DEFAULT 'EA',
    unit_cost_cents     INTEGER NOT NULL CHECK (unit_cost_cents >= 0),
    abc_class           CHAR(1) CHECK (abc_class IN ('A','B','C')),
    xyz_class           CHAR(1) CHECK (xyz_class IN ('X','Y','Z')),
    lot_tracked         BOOLEAN NOT NULL DEFAULT FALSE,
    shelf_life_days     INTEGER,
    storage_condition   VARCHAR(30) CHECK (storage_condition IN ('AMBIENT','CHILLED','FROZEN','CONTROLLED','HAZMAT')),
    reach_svhc          BOOLEAN NOT NULL DEFAULT FALSE,
    backorder_allowed   BOOLEAN NOT NULL DEFAULT FALSE,
    status              VARCHAR(20) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE','DISCONTINUED','BLOCKED','PENDING')),
    is_deleted          BOOLEAN NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE inventory.sku_master IS 'Immutable SKU codes once created; use status flags. Ref: GS1 Gen Specs v23';
COMMENT ON COLUMN inventory.sku_master.unit_cost_cents IS 'Integer cents only — never float';

-- Stock movements (immutable event log)
CREATE TABLE inventory.stock_movements (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    idempotency_key     VARCHAR(100) NOT NULL UNIQUE,
    sku_id              UUID NOT NULL REFERENCES inventory.sku_master(id),
    warehouse_id        UUID,
    lot_id              VARCHAR(100),
    movement_type       VARCHAR(40) NOT NULL CHECK (movement_type IN (
        'PURCHASE_RECEIPT','SALE_SHIPMENT','TRANSFER_IN','TRANSFER_OUT',
        'ADJUSTMENT_POSITIVE','ADJUSTMENT_NEGATIVE','RETURN_FROM_CUSTOMER',
        'RETURN_TO_SUPPLIER','PRODUCTION_CONSUMPTION','PRODUCTION_OUTPUT',
        'SCRAP','WRITE_OFF','CYCLE_COUNT_ADJUSTMENT','QUARANTINE_IN','QUARANTINE_RELEASE'
    )),
    quantity            NUMERIC(18,6) NOT NULL CHECK (quantity > 0),
    unit_cost_cents     INTEGER NOT NULL,
    total_cost_cents    INTEGER GENERATED ALWAYS AS (ROUND(quantity * unit_cost_cents)) STORED,
    reference_doc       VARCHAR(100),   -- PO number, SO number, etc.
    reference_line      INTEGER,
    gl_debit_account    VARCHAR(20),
    gl_credit_account   VARCHAR(20),
    timestamp           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by          VARCHAR(100),
    is_deleted          BOOLEAN NOT NULL DEFAULT FALSE
) PARTITION BY RANGE (timestamp);
COMMENT ON TABLE inventory.stock_movements IS 'Append-only event log — never update or hard-delete';
COMMENT ON COLUMN inventory.stock_movements.idempotency_key IS 'Safe to retry — duplicate writes ignored';

-- Partitions by quarter
CREATE TABLE inventory.stock_movements_2024_q1 PARTITION OF inventory.stock_movements
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');
CREATE TABLE inventory.stock_movements_2024_q2 PARTITION OF inventory.stock_movements
    FOR VALUES FROM ('2024-04-01') TO ('2024-07-01');
CREATE TABLE inventory.stock_movements_2024_q3 PARTITION OF inventory.stock_movements
    FOR VALUES FROM ('2024-07-01') TO ('2024-10-01');
CREATE TABLE inventory.stock_movements_2024_q4 PARTITION OF inventory.stock_movements
    FOR VALUES FROM ('2024-10-01') TO ('2025-01-01');
CREATE TABLE inventory.stock_movements_2025_q1 PARTITION OF inventory.stock_movements
    FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');
CREATE TABLE inventory.stock_movements_2025_q2 PARTITION OF inventory.stock_movements
    FOR VALUES FROM ('2025-04-01') TO ('2025-07-01');
CREATE TABLE inventory.stock_movements_default PARTITION OF inventory.stock_movements DEFAULT;

CREATE INDEX ON inventory.stock_movements (sku_id, timestamp DESC);
CREATE INDEX ON inventory.stock_movements (movement_type, timestamp DESC);

-- Projected stock balance (materialized view, refreshed periodically)
CREATE MATERIALIZED VIEW inventory.stock_balance AS
SELECT
    sku_id,
    SUM(CASE WHEN movement_type IN (
        'PURCHASE_RECEIPT','TRANSFER_IN','ADJUSTMENT_POSITIVE',
        'RETURN_FROM_CUSTOMER','PRODUCTION_OUTPUT','CYCLE_COUNT_ADJUSTMENT','QUARANTINE_RELEASE'
    ) THEN quantity ELSE 0 END)
    -
    SUM(CASE WHEN movement_type IN (
        'SALE_SHIPMENT','TRANSFER_OUT','ADJUSTMENT_NEGATIVE',
        'RETURN_TO_SUPPLIER','PRODUCTION_CONSUMPTION','SCRAP','WRITE_OFF','QUARANTINE_IN'
    ) THEN quantity ELSE 0 END) AS on_hand_qty,
    MAX(timestamp) AS last_movement_at
FROM inventory.stock_movements
WHERE is_deleted = FALSE
GROUP BY sku_id;
CREATE UNIQUE INDEX ON inventory.stock_balance (sku_id);

-- Lot/batch tracking
CREATE TABLE inventory.lots (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku_id          UUID NOT NULL REFERENCES inventory.sku_master(id),
    lot_number      VARCHAR(100) NOT NULL,
    supplier_lot    VARCHAR(100),
    manufacture_date DATE,
    expiry_date     DATE,
    quarantine      BOOLEAN NOT NULL DEFAULT FALSE,
    is_deleted      BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (sku_id, lot_number)
);

-- ABC-XYZ classification history
CREATE TABLE inventory.abc_xyz_classifications (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku_id          UUID NOT NULL REFERENCES inventory.sku_master(id),
    classified_at   DATE NOT NULL DEFAULT CURRENT_DATE,
    abc_class       CHAR(1) NOT NULL CHECK (abc_class IN ('A','B','C')),
    xyz_class       CHAR(1) NOT NULL CHECK (xyz_class IN ('X','Y','Z')),
    annual_consumption_value_cents BIGINT NOT NULL,
    cv              NUMERIC(8,4),
    UNIQUE (sku_id, classified_at)
);

-- Inventory KPIs
CREATE OR REPLACE VIEW inventory.inventory_kpis AS
SELECT
    s.sku_id,
    sk.sku_code,
    s.on_hand_qty,
    sk.unit_cost_cents,
    s.on_hand_qty * sk.unit_cost_cents AS inventory_value_cents,
    sk.abc_class,
    sk.xyz_class
FROM inventory.stock_balance s
JOIN inventory.sku_master sk ON sk.id = s.sku_id
WHERE sk.is_deleted = FALSE;
