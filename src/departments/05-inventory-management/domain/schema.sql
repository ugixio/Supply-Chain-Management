-- =============================================================================
-- Schema: inventory
-- Aligns with: InventoryItem.ts, StockMovement.ts
-- Feeds Python models:
--   python/05_inventory_management/stock_balance.py
--     -> current_balance(sku_id, location_id) uses stock_movements (event log)
--     -> inventory_turnover(sku_id)            uses stock_movements + unit_cost
--     -> days_inventory_outstanding(sku_id)    uses turnover ratio
--   python/05_inventory_management/abc_analysis.py
--     -> classify_abc(sku_ids, annual_spend)   uses inventory_items + movements
--
-- CRITICAL RULES:
--   1. stock_movements is APPEND-ONLY (no UPDATE, no DELETE)
--   2. idempotency_key has UNIQUE constraint — safe to retry any movement insert
--   3. Partitioned by movement_date quarterly
--   4. The SOURCE OF TRUTH for inventory balance is SUM(stock_movements)
--      inventory_snapshots are performance aids only, NOT the source of truth
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS inventory;

-- ---------------------------------------------------------------------------
-- inventory_items
-- SKU master record with replenishment policy, compliance flags, and classification.
-- SKU codes are immutable once created (use status flags to retire).
-- ---------------------------------------------------------------------------
CREATE TABLE inventory.inventory_items (
    sku_id                VARCHAR(50)   PRIMARY KEY,           -- immutable once created
    gtin                  VARCHAR(14),                          -- GS1 GTIN (8/12/13/14 digits)
    description           VARCHAR(255)  NOT NULL,
    -- ABC classification (by annual consumption value: A=top 80%, B=next 15%, C=last 5%)
    abc_class             CHAR(1)       CHECK (abc_class IN ('A','B','C')),
    -- XYZ classification (from demand_planning.xyz_classification)
    xyz_class             CHAR(1)       CHECK (xyz_class IN ('X','Y','Z')),
    -- Costing (integer cents — NEVER float)
    unit_cost_cents       INTEGER       NOT NULL DEFAULT 0 CHECK (unit_cost_cents >= 0),
    currency              CHAR(3)       NOT NULL DEFAULT 'USD',
    -- GS1 UOM
    base_uom              CHAR(3)       NOT NULL,               -- GS1 UN/ECE Rec 20 code
    -- Storage requirements
    storage_condition     VARCHAR(20)   NOT NULL DEFAULT 'AMBIENT'
                              CHECK (storage_condition IN (
                                  'AMBIENT','CHILLED','FROZEN','CONTROLLED_TEMP',
                                  'HAZMAT','FLAMMABLE','CORROSIVE','DRY_STORE'
                              )),
    -- Lot tracking mandatory when storage_condition != AMBIENT or reach_svhc = TRUE
    lot_tracked           BOOLEAN       NOT NULL DEFAULT FALSE,
    shelf_life_days       INTEGER       CHECK (shelf_life_days > 0),   -- NULL = no expiry
    -- EU REACH 1907/2006 SVHC (Substance of Very High Concern)
    reach_svhc            BOOLEAN       NOT NULL DEFAULT FALSE,
    reach_svhc_substance  VARCHAR(255),    -- CAS number or SVHC name
    -- Hazmat
    is_hazmat             BOOLEAN       NOT NULL DEFAULT FALSE,
    hazmat_class          VARCHAR(10),     -- IMDG/ADR class (e.g. '3','8','6.1')
    un_number             VARCHAR(6),      -- UN number e.g. 'UN1263'
    -- Replenishment policy (updated from demand_planning.v_sku_replenishment_params)
    reorder_point         NUMERIC(15,4) DEFAULT 0 CHECK (reorder_point >= 0),
    safety_stock_qty      NUMERIC(15,4) DEFAULT 0 CHECK (safety_stock_qty >= 0),
    min_stock_qty         NUMERIC(15,4) DEFAULT 0 CHECK (min_stock_qty >= 0),
    max_stock_qty         NUMERIC(15,4),
    eoq                   NUMERIC(15,4) CHECK (eoq > 0),
    lead_time_days        SMALLINT      CHECK (lead_time_days >= 0),
    -- Backorder policy (business rule: negative inventory forbidden unless TRUE)
    backorder_allowed     BOOLEAN       NOT NULL DEFAULT FALSE,
    -- Status (SKU codes are immutable — use status to retire)
    status                VARCHAR(20)   NOT NULL DEFAULT 'ACTIVE'
                              CHECK (status IN ('ACTIVE','DISCONTINUED','BLOCKED','PHASE_OUT')),
    -- Soft delete
    is_deleted            BOOLEAN       NOT NULL DEFAULT FALSE,
    created_at            TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at            TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    -- Business rule: lot_tracked required when storage is non-ambient or reach_svhc
    CONSTRAINT chk_lot_tracking CHECK (
        lot_tracked = TRUE
        OR (storage_condition = 'AMBIENT' AND reach_svhc = FALSE)
    ),
    -- Business rule: hazmat requires hazmat_class
    CONSTRAINT chk_hazmat_class CHECK (
        NOT is_hazmat OR hazmat_class IS NOT NULL
    )
);

COMMENT ON TABLE inventory.inventory_items IS
    'SKU master. sku_id is immutable once created (business rule). '
    'Use status=DISCONTINUED or BLOCKED to retire. Never hard-delete. '
    'abc_class is computed by python/05_inventory_management/abc_analysis.py '
    '  classify_abc() from annual consumption value (COGS contribution). '
    'xyz_class is synced from demand_planning.xyz_classification. '
    'Combined ABC-XYZ drives replenishment strategy: AX=MRP/Kanban, CZ=buffer/VMI. '
    'lot_tracked MUST be TRUE when storage_condition != AMBIENT or reach_svhc = TRUE '
    '(FEFO picking, REACH traceability requirement).';

COMMENT ON COLUMN inventory.inventory_items.unit_cost_cents IS
    'Standard cost in integer cents. NEVER FLOAT. '
    'Updated from procurement (invoice) or standard cost revision. '
    'Used in ABC analysis: annual_value = unit_cost_cents * annual_demand.';

COMMENT ON COLUMN inventory.inventory_items.backorder_allowed IS
    'FALSE (default): system rejects stock movements that would cause negative inventory. '
    'TRUE: backorders permitted (demand fulfilment takes priority over stock balance).';

COMMENT ON COLUMN inventory.inventory_items.reach_svhc IS
    'TRUE if SKU contains an EU REACH Substance of Very High Concern. '
    'Forces lot_tracked=TRUE and triggers compliance/REACH.ts assessREACHCompliance().';

-- ---------------------------------------------------------------------------
-- stock_movements
-- APPEND-ONLY event log. This is the SOURCE OF TRUTH for inventory balances.
-- Balance = SUM(quantity) filtered by movement_type polarity.
-- PARTITIONED BY RANGE (movement_date) quarterly.
-- idempotency_key ensures safe retries without duplicate postings.
-- ---------------------------------------------------------------------------
CREATE TABLE inventory.stock_movements (
    id                UUID          NOT NULL DEFAULT gen_random_uuid(),
    -- Idempotency: unique per business event to allow safe retries
    idempotency_key   VARCHAR(100)  NOT NULL,
    movement_type     VARCHAR(30)   NOT NULL CHECK (movement_type IN (
                          -- INBOUND (increase stock)
                          'PURCHASE_RECEIPT',           -- goods received from supplier
                          'RETURN_FROM_CUSTOMER',       -- customer return (SCOR: Return)
                          'TRANSFER_IN',                -- warehouse transfer in
                          'PRODUCTION_RECEIPT',         -- finished goods from production
                          'POSITIVE_ADJUSTMENT',        -- inventory count surplus
                          'CONSIGNMENT_RECEIPT',        -- VMI consignment receipt
                          -- OUTBOUND (decrease stock)
                          'CUSTOMER_SHIPMENT',          -- outbound fulfilment
                          'RETURN_TO_SUPPLIER',         -- supplier return / debit note
                          'TRANSFER_OUT',               -- warehouse transfer out
                          'PRODUCTION_ISSUE',           -- raw material to production
                          'NEGATIVE_ADJUSTMENT',        -- inventory count deficit
                          'SCRAPPED',                   -- quality rejection / write-off
                          'SAMPLE_ISSUE',               -- QC sample
                          -- NEUTRAL (no balance change — reservation/release)
                          'RESERVATION',                -- soft allocation to order
                          'RESERVATION_RELEASE'         -- release of soft allocation
                      )),
    sku_id            VARCHAR(50)   NOT NULL REFERENCES inventory.inventory_items(sku_id),
    lot_id            UUID,          -- FK to stock_lots; NULL when not lot-tracked
    location_id       UUID          NOT NULL,   -- warehouse location
    warehouse_id      UUID          NOT NULL,
    -- Quantity: POSITIVE for INBOUND, NEGATIVE for OUTBOUND (stored as signed)
    quantity          NUMERIC(15,4) NOT NULL,
    uom               CHAR(3)       NOT NULL,
    unit_cost_cents   INTEGER       NOT NULL CHECK (unit_cost_cents >= 0),
    -- line_total_cents = |quantity| * unit_cost_cents (signed for GL)
    line_total_cents  BIGINT GENERATED ALWAYS AS (
                          ROUND(quantity * unit_cost_cents)::BIGINT
                      ) STORED,
    -- Reference to source business document
    reference_doc_id   VARCHAR(100),   -- PO number, SO number, transfer order ID, etc.
    reference_doc_type VARCHAR(30)  CHECK (reference_doc_type IN (
                           'PURCHASE_ORDER','SALES_ORDER','TRANSFER_ORDER',
                           'PRODUCTION_ORDER','INVENTORY_COUNT','QUALITY_ORDER',
                           'MANUAL','CONSIGNMENT_AGREEMENT'
                       )),
    -- GL double-entry (every movement generates a journal entry)
    debit_account     VARCHAR(20)   NOT NULL,    -- GL account code
    credit_account    VARCHAR(20)   NOT NULL,
    -- Cancelled movement (soft cancellation: insert reverse movement)
    cancelled_by_movement_id UUID,    -- ID of the reversing movement (NOT a delete)
    cancels_movement_id      UUID,    -- ID of the original movement being reversed
    -- Metadata
    movement_date     DATE          NOT NULL DEFAULT CURRENT_DATE,
    movement_ts       TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    created_by        VARCHAR(100)  NOT NULL,
    notes             TEXT,
    CONSTRAINT pk_stock_movements PRIMARY KEY (id, movement_date),
    -- Idempotency constraint ensures no duplicate movements for the same business event
    CONSTRAINT uq_idempotency UNIQUE (idempotency_key),
    -- Quantity sign convention check
    CONSTRAINT chk_quantity_sign CHECK (
        (movement_type IN (
            'PURCHASE_RECEIPT','RETURN_FROM_CUSTOMER','TRANSFER_IN',
            'PRODUCTION_RECEIPT','POSITIVE_ADJUSTMENT','CONSIGNMENT_RECEIPT'
         ) AND quantity > 0)
        OR (movement_type IN (
            'CUSTOMER_SHIPMENT','RETURN_TO_SUPPLIER','TRANSFER_OUT',
            'PRODUCTION_ISSUE','NEGATIVE_ADJUSTMENT','SCRAPPED','SAMPLE_ISSUE'
         ) AND quantity < 0)
        OR (movement_type IN ('RESERVATION','RESERVATION_RELEASE'))
        -- RESERVATION quantities can be positive or negative
    )
) PARTITION BY RANGE (movement_date);

COMMENT ON TABLE inventory.stock_movements IS
    'APPEND-ONLY inventory event log. SOURCE OF TRUTH for stock balances. '
    'NEVER UPDATE or DELETE rows. Cancellations use insert of reverse movement '
    '(cancelled_by_movement_id / cancels_movement_id pair). '
    'idempotency_key UNIQUE constraint makes all inserts safely retryable. '
    'quantity is SIGNED: positive=inbound, negative=outbound. '
    'line_total_cents is GENERATED from quantity * unit_cost_cents. '
    'debit_account / credit_account implement double-entry GL per movement. '
    'Partitioned quarterly for performance. '
    'v_current_stock_balance SUM()s this table — never use inventory_snapshots as truth. '
    'Feeds python/05_inventory_management/stock_balance.py current_balance().';

COMMENT ON COLUMN inventory.stock_movements.idempotency_key IS
    'Business-level unique key (e.g. PO+line+receipt_date+sequence). '
    'UNIQUE constraint guarantees safe retry: inserting a duplicate key is a no-op. '
    'Format: "{doc_type}-{doc_id}-{line}-{seq}" e.g. "PO-2024-001-L1-R1".';

COMMENT ON COLUMN inventory.stock_movements.cancelled_by_movement_id IS
    'If this movement was reversed, this points to the reversing movement ID. '
    'The reversing movement has cancels_movement_id = this.id and opposite quantity sign. '
    'This preserves the full audit trail without hard deletes.';

COMMENT ON COLUMN inventory.stock_movements.debit_account IS
    'GL debit account code per movement type. Mapping: '
    'PURCHASE_RECEIPT: debit=Inventory(1300), credit=GoodsReceivedNotInvoiced(2100). '
    'CUSTOMER_SHIPMENT: debit=COGS(5000), credit=Inventory(1300). '
    'SCRAPPED: debit=ScrapExpense(6100), credit=Inventory(1300).';

-- Quarterly partitions for stock_movements
CREATE TABLE inventory.stock_movements_2023q1 PARTITION OF inventory.stock_movements FOR VALUES FROM ('2023-01-01') TO ('2023-04-01');
CREATE TABLE inventory.stock_movements_2023q2 PARTITION OF inventory.stock_movements FOR VALUES FROM ('2023-04-01') TO ('2023-07-01');
CREATE TABLE inventory.stock_movements_2023q3 PARTITION OF inventory.stock_movements FOR VALUES FROM ('2023-07-01') TO ('2023-10-01');
CREATE TABLE inventory.stock_movements_2023q4 PARTITION OF inventory.stock_movements FOR VALUES FROM ('2023-10-01') TO ('2024-01-01');
CREATE TABLE inventory.stock_movements_2024q1 PARTITION OF inventory.stock_movements FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');
CREATE TABLE inventory.stock_movements_2024q2 PARTITION OF inventory.stock_movements FOR VALUES FROM ('2024-04-01') TO ('2024-07-01');
CREATE TABLE inventory.stock_movements_2024q3 PARTITION OF inventory.stock_movements FOR VALUES FROM ('2024-07-01') TO ('2024-10-01');
CREATE TABLE inventory.stock_movements_2024q4 PARTITION OF inventory.stock_movements FOR VALUES FROM ('2024-10-01') TO ('2025-01-01');
CREATE TABLE inventory.stock_movements_2025q1 PARTITION OF inventory.stock_movements FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');
CREATE TABLE inventory.stock_movements_2025q2 PARTITION OF inventory.stock_movements FOR VALUES FROM ('2025-04-01') TO ('2025-07-01');
CREATE TABLE inventory.stock_movements_2025q3 PARTITION OF inventory.stock_movements FOR VALUES FROM ('2025-07-01') TO ('2025-10-01');
CREATE TABLE inventory.stock_movements_2025q4 PARTITION OF inventory.stock_movements FOR VALUES FROM ('2025-10-01') TO ('2026-01-01');
CREATE TABLE inventory.stock_movements_2026q1 PARTITION OF inventory.stock_movements FOR VALUES FROM ('2026-01-01') TO ('2026-04-01');
CREATE TABLE inventory.stock_movements_2026q2 PARTITION OF inventory.stock_movements FOR VALUES FROM ('2026-04-01') TO ('2026-07-01');
CREATE TABLE inventory.stock_movements_2026q3 PARTITION OF inventory.stock_movements FOR VALUES FROM ('2026-07-01') TO ('2026-10-01');
CREATE TABLE inventory.stock_movements_2026q4 PARTITION OF inventory.stock_movements FOR VALUES FROM ('2026-10-01') TO ('2027-01-01');
CREATE TABLE inventory.stock_movements_default PARTITION OF inventory.stock_movements DEFAULT;

-- ---------------------------------------------------------------------------
-- stock_lots
-- Lot/batch master. Required when inventory_items.lot_tracked = TRUE.
-- FEFO picking: expiry_date drives lot selection (First Expired First Out).
-- ---------------------------------------------------------------------------
CREATE TABLE inventory.stock_lots (
    id                  UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    lot_number          VARCHAR(50)   NOT NULL,
    sku_id              VARCHAR(50)   NOT NULL REFERENCES inventory.inventory_items(sku_id),
    supplier_id         UUID,          -- advisory FK to procurement.suppliers
    -- Receipt
    receipt_date        DATE          NOT NULL,
    purchase_order_ref  VARCHAR(30),
    -- Expiry (mandatory for lot_tracked items with shelf_life_days set)
    manufacture_date    DATE,
    expiry_date         DATE,
    best_before_date    DATE,
    -- Quantities
    quantity_received   NUMERIC(15,4) NOT NULL CHECK (quantity_received > 0),
    quantity_available  NUMERIC(15,4) NOT NULL DEFAULT 0 CHECK (quantity_available >= 0),
    quantity_quarantined NUMERIC(15,4) NOT NULL DEFAULT 0 CHECK (quantity_quarantined >= 0),
    quantity_scrapped   NUMERIC(15,4) NOT NULL DEFAULT 0 CHECK (quantity_scrapped >= 0),
    uom                 CHAR(3)       NOT NULL,
    -- Quality status
    status              VARCHAR(20)   NOT NULL DEFAULT 'RELEASED'
                            CHECK (status IN (
                                'QUARANTINE','RELEASED','REJECTED','RECALLED',
                                'EXPIRED','PARTIALLY_USED','FULLY_CONSUMED'
                            )),
    -- Inspection reference (from quality module)
    inspection_record_id UUID,
    aql_result          VARCHAR(10)   CHECK (aql_result IN ('ACCEPT','REJECT','CONDITIONAL')),
    -- REACH SVHC traceability (required when reach_svhc=TRUE on the item)
    reach_declaration_ref VARCHAR(100),
    -- Storage location
    warehouse_id        UUID,
    location_id         UUID,
    -- Soft delete
    is_deleted          BOOLEAN       NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    UNIQUE (lot_number, sku_id),
    CONSTRAINT chk_lot_expiry CHECK (
        expiry_date IS NULL OR expiry_date >= receipt_date
    ),
    CONSTRAINT chk_lot_quantities CHECK (
        quantity_available + quantity_quarantined + quantity_scrapped <= quantity_received
    )
);

COMMENT ON TABLE inventory.stock_lots IS
    'Lot/batch master for lot-tracked SKUs. '
    'Required when inventory_items.lot_tracked = TRUE (storage != AMBIENT or reach_svhc). '
    'expiry_date drives FEFO picking in warehouse module: '
    '  SELECT lot_id ORDER BY expiry_date ASC NULLS LAST. '
    'quantity_available is maintained by stock_movements (not a source of truth — '
    'it is a denormalised cache updated by triggers for WMS performance). '
    'status=RECALLED triggers a reverse movement (RETURN_TO_SUPPLIER or SCRAPPED) '
    'and NCR creation in the quality module.';

COMMENT ON COLUMN inventory.stock_lots.expiry_date IS
    'Best-before or use-by date. Drives FEFO lot selection. '
    'Lots within 30 days of expiry generate a slow-mover alert via v_expiry_risk view.';

-- ---------------------------------------------------------------------------
-- gl_journal_entries
-- Double-entry accounting entries mirroring stock_movements.
-- One row per debit and one per credit (two rows per movement).
-- ---------------------------------------------------------------------------
CREATE TABLE inventory.gl_journal_entries (
    id                UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    movement_id       UUID        NOT NULL,    -- references stock_movements.id
    movement_date     DATE        NOT NULL,    -- duplicate for partition alignment
    journal_date      DATE        NOT NULL DEFAULT CURRENT_DATE,
    -- GL posting
    account_code      VARCHAR(20) NOT NULL,
    entry_type        CHAR(2)     NOT NULL CHECK (entry_type IN ('DR','CR')),
    amount_cents      BIGINT      NOT NULL CHECK (amount_cents > 0),   -- always positive; DR/CR from entry_type
    currency          CHAR(3)     NOT NULL DEFAULT 'USD',
    -- Reference
    sku_id            VARCHAR(50),
    movement_type     VARCHAR(30),
    reference_doc_id  VARCHAR(100),
    -- Period
    accounting_period VARCHAR(7)  NOT NULL,   -- YYYY-MM
    fiscal_year       SMALLINT    NOT NULL,
    -- Posting status
    posted            BOOLEAN     NOT NULL DEFAULT FALSE,
    posted_at         TIMESTAMPTZ,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE inventory.gl_journal_entries IS
    'Double-entry GL journal entries derived from stock_movements. '
    'Each stock_movement generates exactly one DEBIT and one CREDIT row here. '
    'amount_cents is always positive; entry_type (DR/CR) carries the sign. '
    'Business rule: debit_total = credit_total per movement_id (enforced by app layer). '
    'posted=TRUE means the entry has been transferred to the ERP general ledger. '
    'Feeds python/05_inventory_management/stock_balance.py inventory_valuation() '
    'and finance/controlling module working capital reports.';

-- ---------------------------------------------------------------------------
-- inventory_snapshots
-- Periodic point-in-time balance snapshots for dashboard performance.
-- WARNING: NOT the source of truth. v_current_stock_balance (from movements) is truth.
-- Snapshots become stale immediately after any movement.
-- ---------------------------------------------------------------------------
CREATE TABLE inventory.inventory_snapshots (
    id                UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    sku_id            VARCHAR(50)   NOT NULL REFERENCES inventory.inventory_items(sku_id),
    location_id       UUID          NOT NULL,
    warehouse_id      UUID          NOT NULL,
    snapshot_date     DATE          NOT NULL,
    snapshot_ts       TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    quantity_on_hand  NUMERIC(15,4) NOT NULL DEFAULT 0,
    quantity_reserved NUMERIC(15,4) NOT NULL DEFAULT 0,
    quantity_available NUMERIC(15,4) GENERATED ALWAYS AS (
                           quantity_on_hand - quantity_reserved
                       ) STORED,
    quantity_on_order NUMERIC(15,4) NOT NULL DEFAULT 0,
    unit_cost_cents   INTEGER       NOT NULL DEFAULT 0,
    total_value_cents BIGINT GENERATED ALWAYS AS (
                          ROUND(quantity_on_hand * unit_cost_cents)::BIGINT
                      ) STORED,
    uom               CHAR(3)       NOT NULL,
    -- Source of truth verification
    verified_against_movements BOOLEAN NOT NULL DEFAULT FALSE,
    variance_qty      NUMERIC(15,4),    -- snapshot vs sum(movements) discrepancy
    created_at        TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    UNIQUE (sku_id, location_id, snapshot_date)
);

COMMENT ON TABLE inventory.inventory_snapshots IS
    'Performance snapshots of stock balances — NOT the source of truth. '
    'The source of truth is SUM(stock_movements.quantity) per sku/location. '
    'Snapshots are generated nightly by stock_balance.py take_snapshot() '
    'to accelerate dashboard queries. Use v_current_stock_balance for accuracy. '
    'variance_qty flags discrepancies between snapshot and movement sum for reconciliation.';

-- ---------------------------------------------------------------------------
-- Indexes
-- ---------------------------------------------------------------------------
CREATE INDEX idx_items_abc              ON inventory.inventory_items(abc_class)        WHERE is_deleted = FALSE;
CREATE INDEX idx_items_xyz              ON inventory.inventory_items(xyz_class)        WHERE is_deleted = FALSE;
CREATE INDEX idx_items_status           ON inventory.inventory_items(status)           WHERE is_deleted = FALSE;
CREATE INDEX idx_items_lot_tracked      ON inventory.inventory_items(lot_tracked)      WHERE lot_tracked = TRUE;
CREATE INDEX idx_items_reach_svhc       ON inventory.inventory_items(reach_svhc)       WHERE reach_svhc = TRUE;
CREATE INDEX idx_items_storage          ON inventory.inventory_items(storage_condition);

-- stock_movements indexes (created on partition parent — inherited by children)
CREATE INDEX idx_movements_sku_date     ON inventory.stock_movements(sku_id, movement_date);
CREATE INDEX idx_movements_location     ON inventory.stock_movements(location_id, sku_id, movement_date);
CREATE INDEX idx_movements_lot          ON inventory.stock_movements(lot_id)           WHERE lot_id IS NOT NULL;
CREATE INDEX idx_movements_type         ON inventory.stock_movements(movement_type, movement_date);
CREATE INDEX idx_movements_ref          ON inventory.stock_movements(reference_doc_id, reference_doc_type);
CREATE INDEX idx_movements_warehouse    ON inventory.stock_movements(warehouse_id, movement_date);
-- Partial index for active (non-cancelled) movements
CREATE INDEX idx_movements_active       ON inventory.stock_movements(sku_id, movement_date)
    WHERE cancelled_by_movement_id IS NULL;

CREATE INDEX idx_lots_sku               ON inventory.stock_lots(sku_id, status)        WHERE is_deleted = FALSE;
CREATE INDEX idx_lots_expiry            ON inventory.stock_lots(expiry_date, sku_id)   WHERE status = 'RELEASED';
CREATE INDEX idx_lots_supplier          ON inventory.stock_lots(supplier_id)           WHERE supplier_id IS NOT NULL;

CREATE INDEX idx_gl_movement            ON inventory.gl_journal_entries(movement_id);
CREATE INDEX idx_gl_period              ON inventory.gl_journal_entries(accounting_period, account_code);
CREATE INDEX idx_gl_unposted            ON inventory.gl_journal_entries(journal_date)  WHERE posted = FALSE;

CREATE INDEX idx_snapshots_sku          ON inventory.inventory_snapshots(sku_id, snapshot_date);
CREATE INDEX idx_snapshots_warehouse    ON inventory.inventory_snapshots(warehouse_id, snapshot_date);

-- ---------------------------------------------------------------------------
-- VIEW: v_current_stock_balance
-- SOURCE OF TRUTH balance per SKU per location.
-- Sums ALL non-cancelled stock_movements.
-- RESERVATION movements are separated to show available vs on_hand.
-- ---------------------------------------------------------------------------
CREATE VIEW inventory.v_current_stock_balance AS
SELECT
    sm.sku_id,
    sm.location_id,
    sm.warehouse_id,
    ii.description,
    ii.base_uom,
    ii.abc_class,
    ii.xyz_class,
    ii.unit_cost_cents,
    ii.backorder_allowed,
    ii.reorder_point,
    ii.safety_stock_qty,
    ii.min_stock_qty,
    ii.max_stock_qty,
    -- On-hand: sum of all inbound/outbound movements (excluding RESERVATION types)
    COALESCE(SUM(
        CASE WHEN sm.movement_type NOT IN ('RESERVATION','RESERVATION_RELEASE')
             THEN sm.quantity
             ELSE 0
        END
    ), 0)                                           AS quantity_on_hand,
    -- Reserved: net of RESERVATION - RESERVATION_RELEASE
    COALESCE(SUM(
        CASE WHEN sm.movement_type = 'RESERVATION'        THEN sm.quantity
             WHEN sm.movement_type = 'RESERVATION_RELEASE' THEN sm.quantity  -- already negative
             ELSE 0
        END
    ), 0)                                           AS quantity_reserved,
    -- Available = on_hand - reserved
    COALESCE(SUM(
        CASE WHEN sm.movement_type NOT IN ('RESERVATION','RESERVATION_RELEASE')
             THEN sm.quantity
             WHEN sm.movement_type = 'RESERVATION'        THEN -sm.quantity
             WHEN sm.movement_type = 'RESERVATION_RELEASE' THEN -sm.quantity
             ELSE 0
        END
    ), 0)                                           AS quantity_available,
    -- Inventory value
    COALESCE(SUM(
        CASE WHEN sm.movement_type NOT IN ('RESERVATION','RESERVATION_RELEASE')
             THEN sm.line_total_cents
             ELSE 0
        END
    ), 0)                                           AS total_value_cents,
    -- Stockout indicator
    COALESCE(SUM(
        CASE WHEN sm.movement_type NOT IN ('RESERVATION','RESERVATION_RELEASE')
             THEN sm.quantity ELSE 0 END
    ), 0) <= 0                                      AS is_stockout,
    -- Below safety stock
    COALESCE(SUM(
        CASE WHEN sm.movement_type NOT IN ('RESERVATION','RESERVATION_RELEASE')
             THEN sm.quantity ELSE 0 END
    ), 0) < COALESCE(ii.safety_stock_qty, 0)        AS below_safety_stock,
    -- Reorder trigger
    COALESCE(SUM(
        CASE WHEN sm.movement_type NOT IN ('RESERVATION','RESERVATION_RELEASE')
             THEN sm.quantity ELSE 0 END
    ), 0) <= COALESCE(ii.reorder_point, 0)           AS reorder_triggered,
    MAX(sm.movement_ts)                              AS last_movement_ts
FROM inventory.stock_movements sm
JOIN inventory.inventory_items ii ON sm.sku_id = ii.sku_id
WHERE sm.cancelled_by_movement_id IS NULL   -- exclude cancelled movements
GROUP BY
    sm.sku_id, sm.location_id, sm.warehouse_id,
    ii.description, ii.base_uom, ii.abc_class, ii.xyz_class,
    ii.unit_cost_cents, ii.backorder_allowed,
    ii.reorder_point, ii.safety_stock_qty, ii.min_stock_qty, ii.max_stock_qty;

COMMENT ON VIEW inventory.v_current_stock_balance IS
    'SOURCE OF TRUTH current stock balance per SKU per location. '
    'SUM()s all non-cancelled stock_movements. '
    'RESERVATION/RESERVATION_RELEASE movements are separated to compute quantity_available. '
    'quantity_on_hand can be negative only when backorder_allowed=TRUE on the item. '
    'is_stockout, below_safety_stock, reorder_triggered are computed flags for dashboards. '
    'python/05_inventory_management/stock_balance.py current_balance() calls this view. '
    'Do NOT use inventory_snapshots as truth — they are stale performance caches.';

-- ---------------------------------------------------------------------------
-- VIEW: v_abc_xyz_matrix
-- Shows replenishment strategy per SKU from combined ABC + XYZ classification.
-- ---------------------------------------------------------------------------
CREATE VIEW inventory.v_abc_xyz_matrix AS
SELECT
    ii.sku_id,
    ii.description,
    ii.abc_class,
    ii.xyz_class,
    ii.abc_class || ii.xyz_class                    AS abc_xyz_segment,
    ii.unit_cost_cents,
    ii.reorder_point,
    ii.safety_stock_qty,
    ii.eoq,
    ii.lot_tracked,
    ii.storage_condition,
    ii.backorder_allowed,
    ii.status,
    -- Recommended replenishment strategy per ABC-XYZ segment
    CASE ii.abc_class || ii.xyz_class
        WHEN 'AX' THEN 'MRP / Kanban — tight control, frequent review'
        WHEN 'AY' THEN 'MRP with safety stock buffer — weekly review'
        WHEN 'AZ' THEN 'VMI or consignment — high safety stock, daily review'
        WHEN 'BX' THEN 'Periodic review (2-week) — standard EOQ'
        WHEN 'BY' THEN 'Periodic review (monthly) — moderate safety stock'
        WHEN 'BZ' THEN 'Buffer stock — quarterly review, dual source'
        WHEN 'CX' THEN 'Min-Max / two-bin — minimal management'
        WHEN 'CY' THEN 'Min-Max — annual review'
        WHEN 'CZ' THEN 'On-demand / VMI — no stock holding recommended'
        ELSE 'Not classified'
    END                                             AS replenishment_strategy
FROM inventory.inventory_items ii
WHERE ii.is_deleted = FALSE;

COMMENT ON VIEW inventory.v_abc_xyz_matrix IS
    'ABC-XYZ segmentation matrix per SKU with recommended replenishment strategy. '
    'AX (high value, predictable) = MRP/Kanban. CZ (low value, volatile) = VMI/on-demand. '
    'Used by procurement and planning to set review frequency and safety stock levels. '
    'abc_class from python/05_inventory_management/abc_analysis.py classify_abc(). '
    'xyz_class synced from demand_planning.xyz_classification.';

-- ---------------------------------------------------------------------------
-- VIEW: v_stock_movements_gl
-- Joins stock_movements with gl_journal_entries for accounting reconciliation.
-- ---------------------------------------------------------------------------
CREATE VIEW inventory.v_stock_movements_gl AS
SELECT
    sm.id                   AS movement_id,
    sm.movement_date,
    sm.movement_type,
    sm.sku_id,
    sm.quantity,
    sm.unit_cost_cents,
    sm.line_total_cents,
    sm.reference_doc_id,
    sm.reference_doc_type,
    sm.idempotency_key,
    -- Debit leg
    dr.account_code         AS debit_account,
    dr.amount_cents         AS debit_amount_cents,
    -- Credit leg
    cr.account_code         AS credit_account,
    cr.amount_cents         AS credit_amount_cents,
    -- Balance check (should always be 0)
    (dr.amount_cents - cr.amount_cents) AS balance_check,
    dr.accounting_period,
    dr.fiscal_year,
    dr.posted                AS is_posted,
    sm.created_by,
    sm.movement_ts
FROM inventory.stock_movements sm
LEFT JOIN inventory.gl_journal_entries dr
    ON dr.movement_id = sm.id AND dr.entry_type = 'DR'
LEFT JOIN inventory.gl_journal_entries cr
    ON cr.movement_id = sm.id AND cr.entry_type = 'CR'
WHERE sm.cancelled_by_movement_id IS NULL;

COMMENT ON VIEW inventory.v_stock_movements_gl IS
    'Stock movements with their double-entry GL journal legs side-by-side. '
    'balance_check should always be 0 (debit = credit). '
    'Non-zero balance_check rows indicate a posting error requiring investigation. '
    'Used by finance/controlling module for inventory valuation reconciliation '
    'and by stock_balance.py inventory_valuation() to produce period-end GL balances.';

-- ---------------------------------------------------------------------------
-- VIEW: v_lot_fefo_priority
-- FEFO-ordered lots available for picking per SKU per warehouse.
-- Used by WMS module for FEFO lot selection.
-- ---------------------------------------------------------------------------
CREATE VIEW inventory.v_lot_fefo_priority AS
SELECT
    sl.sku_id,
    sl.warehouse_id,
    sl.location_id,
    sl.id                   AS lot_id,
    sl.lot_number,
    sl.expiry_date,
    sl.best_before_date,
    sl.receipt_date,
    sl.quantity_available,
    sl.uom,
    sl.status,
    ii.abc_class,
    ii.storage_condition,
    -- Days remaining before expiry
    CASE
        WHEN sl.expiry_date IS NOT NULL THEN (sl.expiry_date - CURRENT_DATE)
        ELSE NULL
    END                     AS days_to_expiry,
    -- Alert: expiry within 30 days
    (sl.expiry_date IS NOT NULL AND sl.expiry_date <= CURRENT_DATE + 30) AS expiry_alert,
    -- FEFO rank: 1 = pick first (earliest expiry)
    RANK() OVER (
        PARTITION BY sl.sku_id, sl.warehouse_id
        ORDER BY sl.expiry_date ASC NULLS LAST, sl.receipt_date ASC
    )                       AS fefo_rank
FROM inventory.stock_lots sl
JOIN inventory.inventory_items ii ON sl.sku_id = ii.sku_id
WHERE sl.status = 'RELEASED'
  AND sl.quantity_available > 0
  AND sl.is_deleted = FALSE;

COMMENT ON VIEW inventory.v_lot_fefo_priority IS
    'FEFO-ranked available lots per SKU per warehouse. fefo_rank=1 = pick first. '
    'expiry_alert=TRUE flags lots expiring within 30 days for proactive disposition. '
    'Used by warehouse module FEFO picking algorithm and python/06_warehouse/fefo.py. '
    'Mandatory for lot-tracked SKUs with shelf_life_days set (chilled, frozen, pharma).';
