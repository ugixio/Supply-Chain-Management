-- =============================================================================
-- SCHEMA: warehouse
-- Department: 06 – Warehouse Management
-- Feeds Python: slotting.py (fefo_sort, calculate_cpoi, assign_abc_velocity_zones,
--               s_shape_travel_distance)
-- Standards: GS1 Gen. Specs v23, ISO 9001:2015 §8.5.2 (FEFO), SCOR-DS Deliver
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS warehouse;

-- ---------------------------------------------------------------------------
-- TABLES
-- ---------------------------------------------------------------------------

CREATE TABLE warehouse.warehouses (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    warehouse_code      VARCHAR(20) NOT NULL UNIQUE,
    name                VARCHAR(200) NOT NULL,
    type                VARCHAR(20)  NOT NULL
                            CHECK (type IN ('AMBIENT','COLD_CHAIN','HAZMAT','BONDED','CROSS_DOCK')),
    address_line1       VARCHAR(200),
    address_line2       VARCHAR(200),
    city                VARCHAR(100),
    country_code        CHAR(2),
    postal_code         VARCHAR(20),
    total_locations     INTEGER      NOT NULL CHECK (total_locations > 0),
    total_area_m2       NUMERIC(12,2) NOT NULL CHECK (total_area_m2 > 0),
    status              VARCHAR(20)  NOT NULL DEFAULT 'ACTIVE'
                            CHECK (status IN ('ACTIVE','INACTIVE','UNDER_MAINTENANCE')),
    is_deleted          BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  warehouse.warehouses                IS 'Physical warehouse facilities. Each warehouse may have multiple zones and locations.';
COMMENT ON COLUMN warehouse.warehouses.warehouse_code IS 'Unique facility code, e.g. WH-001. Immutable after creation.';
COMMENT ON COLUMN warehouse.warehouses.type           IS 'Storage regime: AMBIENT=standard, COLD_CHAIN=temperature-controlled, HAZMAT=ADR/IMDG compliant, BONDED=customs bonded, CROSS_DOCK=flow-through.';
COMMENT ON COLUMN warehouse.warehouses.total_area_m2  IS 'Total gross floor area in square metres.';


CREATE TABLE warehouse.warehouse_zones (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    warehouse_id    UUID        NOT NULL REFERENCES warehouse.warehouses(id),
    zone_code       VARCHAR(20) NOT NULL,
    zone_type       VARCHAR(20) NOT NULL
                        CHECK (zone_type IN ('PRIMARY','SECONDARY','BULK','RECEIVING','DISPATCH','QUARANTINE')),
    aisle_depth_m   NUMERIC(8,2) CHECK (aisle_depth_m > 0),
    temperature_min_c NUMERIC(6,2),
    temperature_max_c NUMERIC(6,2),
    is_deleted      BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (warehouse_id, zone_code)
);

COMMENT ON TABLE  warehouse.warehouse_zones           IS 'Logical zones within a warehouse. Zone type drives putaway rules and slotting assignments.';
COMMENT ON COLUMN warehouse.warehouse_zones.zone_type IS 'PRIMARY=fast-moving pick face, SECONDARY=replenishment reserve, BULK=pallet storage, RECEIVING=inbound staging, DISPATCH=outbound staging, QUARANTINE=hold area.';
COMMENT ON COLUMN warehouse.warehouse_zones.aisle_depth_m IS 'Depth of aisles in metres; used by s_shape_travel_distance() in slotting.py.';


CREATE TABLE warehouse.warehouse_locations (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    zone_id         UUID        NOT NULL REFERENCES warehouse.warehouse_zones(id),
    warehouse_id    UUID        NOT NULL REFERENCES warehouse.warehouses(id),
    location_code   VARCHAR(50) NOT NULL UNIQUE,
    aisle           VARCHAR(10) NOT NULL,
    rack            VARCHAR(10) NOT NULL,
    level           INTEGER     NOT NULL CHECK (level >= 0),
    bin             VARCHAR(10),
    max_weight_kg   NUMERIC(10,3) CHECK (max_weight_kg > 0),
    max_volume_cm3  BIGINT        CHECK (max_volume_cm3 > 0),
    location_type   VARCHAR(10)   NOT NULL
                        CHECK (location_type IN ('PICK','BULK','RESERVE')),
    is_active       BOOLEAN     NOT NULL DEFAULT TRUE,
    is_deleted      BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  warehouse.warehouse_locations              IS 'Individual storage locations (bins/slots) within zones. Basis for slotting optimisation.';
COMMENT ON COLUMN warehouse.warehouse_locations.location_code IS 'Human-readable GS1 SGLNs-compatible address, e.g. WH001-A-01-3-B. Immutable once assigned.';
COMMENT ON COLUMN warehouse.warehouse_locations.level         IS 'Vertical level: 0=floor, 1=first rack beam, etc.';
COMMENT ON COLUMN warehouse.warehouse_locations.location_type IS 'PICK=active pick face, BULK=full-pallet storage, RESERVE=overflow/replenishment.';


CREATE TABLE warehouse.slotting_assignments (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    sku_id              VARCHAR(50) NOT NULL,
    location_id         UUID        NOT NULL REFERENCES warehouse.warehouse_locations(id),
    warehouse_id        UUID        NOT NULL REFERENCES warehouse.warehouses(id),
    zone_type           VARCHAR(20) NOT NULL
                            CHECK (zone_type IN ('PRIMARY','SECONDARY','BULK','RECEIVING','DISPATCH','QUARANTINE')),
    cpoi                NUMERIC(12,6) NOT NULL CHECK (cpoi >= 0),
    velocity_rank       INTEGER     NOT NULL CHECK (velocity_rank >= 1),
    abc_velocity_zone   VARCHAR(10) NOT NULL
                            CHECK (abc_velocity_zone IN ('PRIMARY','SECONDARY','BULK')),
    assigned_date       DATE        NOT NULL DEFAULT CURRENT_DATE,
    review_date         DATE        NOT NULL,
    assigned_by         VARCHAR(100),
    is_deleted          BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (sku_id, warehouse_id, assigned_date)
);

COMMENT ON TABLE  warehouse.slotting_assignments              IS 'Optimal slot assignments produced by slotting.py assign_abc_velocity_zones(). Reviewed periodically.';
COMMENT ON COLUMN warehouse.slotting_assignments.cpoi         IS 'Cubic-Picks-per-Order-Index = (picks/day * unit_volume). Higher CPOI = closer to dispatch. Computed by calculate_cpoi() in slotting.py.';
COMMENT ON COLUMN warehouse.slotting_assignments.velocity_rank IS 'Rank 1 = highest velocity. Used for s-shape travel distance optimisation.';
COMMENT ON COLUMN warehouse.slotting_assignments.abc_velocity_zone IS 'Mapped from velocity_rank: PRIMARY=A-class, SECONDARY=B-class, BULK=C-class.';
COMMENT ON COLUMN warehouse.slotting_assignments.review_date  IS 'Next scheduled slotting review date. Recommended every 90 days for A-class SKUs.';


CREATE TABLE warehouse.lot_inventory (
    id                    UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    lot_id                UUID        NOT NULL,
    sku_id                VARCHAR(50) NOT NULL,
    location_id           UUID        NOT NULL REFERENCES warehouse.warehouse_locations(id),
    warehouse_id          UUID        NOT NULL REFERENCES warehouse.warehouses(id),
    quantity_available    NUMERIC(15,4) NOT NULL DEFAULT 0 CHECK (quantity_available >= 0),
    quantity_reserved     NUMERIC(15,4) NOT NULL DEFAULT 0 CHECK (quantity_reserved >= 0),
    expiry_date           DATE,
    receipt_date          DATE        NOT NULL DEFAULT CURRENT_DATE,
    supplier_lot_number   VARCHAR(100),
    status                VARCHAR(15) NOT NULL DEFAULT 'AVAILABLE'
                              CHECK (status IN ('AVAILABLE','RESERVED','QUARANTINE','EXPIRED')),
    is_deleted            BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at            TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  warehouse.lot_inventory                   IS 'On-hand stock by lot, location, and warehouse. Negative quantity_available is prohibited by CHECK constraint. Feeds fefo_sort() in slotting.py.';
COMMENT ON COLUMN warehouse.lot_inventory.lot_id            IS 'References inventory lot master. Lot tracking mandatory when storage_condition != AMBIENT or reach_svhc = true (CLAUDE.md rule 5).';
COMMENT ON COLUMN warehouse.lot_inventory.quantity_reserved IS 'Units allocated to open picking tasks but not yet picked.';
COMMENT ON COLUMN warehouse.lot_inventory.expiry_date       IS 'Best-before / expiry date. NULL for non-perishable items. Used by FEFO sort.';


CREATE TABLE warehouse.picking_tasks (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id            UUID        NOT NULL,
    warehouse_id        UUID        NOT NULL REFERENCES warehouse.warehouses(id),
    status              VARCHAR(15) NOT NULL DEFAULT 'PENDING'
                            CHECK (status IN ('PENDING','IN_PROGRESS','COMPLETED','CANCELLED')),
    picker_id           VARCHAR(100),
    started_at          TIMESTAMPTZ,
    completed_at        TIMESTAMPTZ,
    total_lines         INTEGER     NOT NULL DEFAULT 0 CHECK (total_lines >= 0),
    lines_completed     INTEGER     NOT NULL DEFAULT 0 CHECK (lines_completed >= 0),
    travel_distance_m   NUMERIC(10,2) CHECK (travel_distance_m >= 0),
    is_deleted          BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT picking_tasks_lines_check CHECK (lines_completed <= total_lines)
);

COMMENT ON TABLE  warehouse.picking_tasks                   IS 'Wave or discrete pick tasks assigned to warehouse operators. Travel distance computed by s_shape_travel_distance() in slotting.py.';
COMMENT ON COLUMN warehouse.picking_tasks.travel_distance_m IS 'Estimated travel distance in metres from s_shape_travel_distance(). Actual may differ; recorded on completion.';


CREATE TABLE warehouse.picking_task_lines (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id             UUID        NOT NULL REFERENCES warehouse.picking_tasks(id),
    sku_id              VARCHAR(50) NOT NULL,
    lot_id              UUID,
    location_id         UUID        NOT NULL REFERENCES warehouse.warehouse_locations(id),
    quantity_requested  NUMERIC(15,4) NOT NULL CHECK (quantity_requested > 0),
    quantity_picked     NUMERIC(15,4) NOT NULL DEFAULT 0 CHECK (quantity_picked >= 0),
    pick_sequence       INTEGER     NOT NULL CHECK (pick_sequence >= 1),
    fefo_expiry_date    DATE,
    is_deleted          BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  warehouse.picking_task_lines                  IS 'Individual line items within a picking task. Sequence determined by FEFO + s-shape travel path.';
COMMENT ON COLUMN warehouse.picking_task_lines.pick_sequence    IS 'Walk sequence order for the picker, optimised to minimise travel distance.';
COMMENT ON COLUMN warehouse.picking_task_lines.fefo_expiry_date IS 'Expiry date of the lot selected by fefo_sort(). Earliest expiry picked first.';


CREATE TABLE warehouse.cycle_count_tasks (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    warehouse_id    UUID        NOT NULL REFERENCES warehouse.warehouses(id),
    location_id     UUID        NOT NULL REFERENCES warehouse.warehouse_locations(id),
    scheduled_date  DATE        NOT NULL,
    count_date      DATE,
    expected_qty    NUMERIC(15,4),
    counted_qty     NUMERIC(15,4),
    variance_qty    NUMERIC(15,4) GENERATED ALWAYS AS (counted_qty - expected_qty) STORED,
    status          VARCHAR(20) NOT NULL DEFAULT 'SCHEDULED'
                        CHECK (status IN ('SCHEDULED','IN_PROGRESS','COMPLETED','PENDING_APPROVAL','ADJUSTED')),
    counter_id      VARCHAR(100),
    variance_pct    NUMERIC(8,4) GENERATED ALWAYS AS
                        (CASE WHEN expected_qty IS NULL OR expected_qty = 0 THEN NULL
                              ELSE ((counted_qty - expected_qty) / expected_qty) * 100 END) STORED,
    is_deleted      BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  warehouse.cycle_count_tasks              IS 'Scheduled and completed cycle counts by location. Variance drives inventory adjustment transactions.';
COMMENT ON COLUMN warehouse.cycle_count_tasks.variance_qty IS 'Counted minus expected. Negative = shrinkage, positive = surplus. Auto-computed.';
COMMENT ON COLUMN warehouse.cycle_count_tasks.variance_pct IS 'Percentage variance from expected. Auto-computed. Triggers investigation when |variance_pct| > threshold.';


CREATE TABLE warehouse.inbound_receipts (
    id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    po_id                   UUID,
    warehouse_id            UUID        NOT NULL REFERENCES warehouse.warehouses(id),
    receipt_date            DATE        NOT NULL DEFAULT CURRENT_DATE,
    dock_in_time            TIMESTAMPTZ,
    put_away_complete_time  TIMESTAMPTZ,
    dock_to_stock_hours     NUMERIC(8,2) GENERATED ALWAYS AS (
                                EXTRACT(EPOCH FROM (put_away_complete_time - dock_in_time)) / 3600.0
                            ) STORED,
    supplier_id             UUID,
    total_lines             INTEGER     NOT NULL DEFAULT 0 CHECK (total_lines >= 0),
    total_units             NUMERIC(15,4) NOT NULL DEFAULT 0 CHECK (total_units >= 0),
    status                  VARCHAR(20) NOT NULL DEFAULT 'PENDING'
                                CHECK (status IN ('PENDING','RECEIVING','PUT_AWAY','COMPLETED','EXCEPTION')),
    exception_notes         TEXT,
    is_deleted              BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  warehouse.inbound_receipts                     IS 'Goods receipt records against Purchase Orders. dock_to_stock_hours is a key SCOR KPI (target ≤ 24 hours).';
COMMENT ON COLUMN warehouse.inbound_receipts.dock_to_stock_hours IS 'Auto-computed: hours from dock-in to put-away completion. KPI target ≤ 24h. NULL until put_away_complete_time is set.';


-- ---------------------------------------------------------------------------
-- INDEXES
-- ---------------------------------------------------------------------------

CREATE INDEX idx_warehouse_zones_warehouse_id       ON warehouse.warehouse_zones(warehouse_id);
CREATE INDEX idx_warehouse_locations_zone_id        ON warehouse.warehouse_locations(zone_id);
CREATE INDEX idx_warehouse_locations_warehouse_id   ON warehouse.warehouse_locations(warehouse_id);
CREATE INDEX idx_warehouse_locations_aisle_rack     ON warehouse.warehouse_locations(warehouse_id, aisle, rack);

CREATE INDEX idx_slotting_sku_warehouse             ON warehouse.slotting_assignments(sku_id, warehouse_id);
CREATE INDEX idx_slotting_cpoi                      ON warehouse.slotting_assignments(cpoi DESC) WHERE is_deleted = FALSE;
CREATE INDEX idx_slotting_review_date               ON warehouse.slotting_assignments(review_date) WHERE is_deleted = FALSE;

CREATE INDEX idx_lot_inventory_sku_warehouse        ON warehouse.lot_inventory(sku_id, warehouse_id);
CREATE INDEX idx_lot_inventory_lot_id               ON warehouse.lot_inventory(lot_id);
CREATE INDEX idx_lot_inventory_expiry               ON warehouse.lot_inventory(expiry_date ASC) WHERE status = 'AVAILABLE' AND expiry_date IS NOT NULL;
CREATE INDEX idx_lot_inventory_status               ON warehouse.lot_inventory(status) WHERE is_deleted = FALSE;

CREATE INDEX idx_picking_tasks_warehouse_status     ON warehouse.picking_tasks(warehouse_id, status);
CREATE INDEX idx_picking_tasks_picker               ON warehouse.picking_tasks(picker_id) WHERE status IN ('PENDING','IN_PROGRESS');
CREATE INDEX idx_picking_task_lines_task            ON warehouse.picking_task_lines(task_id);
CREATE INDEX idx_picking_task_lines_sequence        ON warehouse.picking_task_lines(task_id, pick_sequence);

CREATE INDEX idx_cycle_count_warehouse_scheduled    ON warehouse.cycle_count_tasks(warehouse_id, scheduled_date);
CREATE INDEX idx_cycle_count_status                 ON warehouse.cycle_count_tasks(status) WHERE is_deleted = FALSE;

CREATE INDEX idx_inbound_receipts_warehouse         ON warehouse.inbound_receipts(warehouse_id, receipt_date);
CREATE INDEX idx_inbound_receipts_po                ON warehouse.inbound_receipts(po_id) WHERE po_id IS NOT NULL;
CREATE INDEX idx_inbound_receipts_status            ON warehouse.inbound_receipts(status) WHERE is_deleted = FALSE;


-- ---------------------------------------------------------------------------
-- VIEWS
-- ---------------------------------------------------------------------------

-- FEFO-ordered available lots (input to fefo_sort() in slotting.py)
CREATE OR REPLACE VIEW warehouse.v_fefo_available_lots AS
SELECT
    li.lot_id,
    li.sku_id,
    li.location_id,
    wl.location_code,
    li.warehouse_id,
    li.quantity_available,
    li.expiry_date,
    li.receipt_date,
    li.supplier_lot_number,
    li.status
FROM warehouse.lot_inventory li
JOIN warehouse.warehouse_locations wl ON wl.id = li.location_id
WHERE li.status = 'AVAILABLE'
  AND li.quantity_available > 0
  AND li.is_deleted = FALSE
ORDER BY li.sku_id, li.expiry_date ASC NULLS LAST, li.receipt_date ASC;

COMMENT ON VIEW warehouse.v_fefo_available_lots IS 'FEFO-ordered available lots for pick execution. Earliest expiry first (ISO 9001:2015 §8.5.2). NULL expiry dates sorted last. Input to fefo_sort() in slotting.py.';


-- SKUs ranked by CPOI for slotting review
CREATE OR REPLACE VIEW warehouse.v_slotting_by_cpoi AS
SELECT
    sa.sku_id,
    sa.warehouse_id,
    w.warehouse_code,
    sa.location_id,
    wl.location_code,
    wl.aisle,
    wl.rack,
    wl.level,
    sa.cpoi,
    sa.velocity_rank,
    sa.abc_velocity_zone,
    sa.assigned_date,
    sa.review_date,
    CASE WHEN sa.review_date < CURRENT_DATE THEN TRUE ELSE FALSE END AS review_overdue
FROM warehouse.slotting_assignments sa
JOIN warehouse.warehouses w             ON w.id  = sa.warehouse_id
JOIN warehouse.warehouse_locations wl   ON wl.id = sa.location_id
WHERE sa.is_deleted = FALSE
ORDER BY sa.warehouse_id, sa.cpoi DESC;

COMMENT ON VIEW warehouse.v_slotting_by_cpoi IS 'All active slotting assignments ranked by CPOI descending. Used by assign_abc_velocity_zones() to identify re-slotting candidates.';


-- Storage utilisation per warehouse
CREATE OR REPLACE VIEW warehouse.v_storage_utilization AS
SELECT
    w.id                                                AS warehouse_id,
    w.warehouse_code,
    w.name                                              AS warehouse_name,
    w.total_locations,
    COUNT(wl.id)                                        AS configured_locations,
    SUM(CASE WHEN wl.is_active THEN 1 ELSE 0 END)      AS active_locations,
    COUNT(li.id)                                        AS occupied_locations,
    ROUND(
        COUNT(li.id)::NUMERIC / NULLIF(COUNT(wl.id), 0) * 100, 2
    )                                                   AS utilization_pct
FROM warehouse.warehouses w
LEFT JOIN warehouse.warehouse_locations wl
       ON wl.warehouse_id = w.id AND wl.is_deleted = FALSE
LEFT JOIN (
    SELECT DISTINCT location_id
    FROM warehouse.lot_inventory
    WHERE status = 'AVAILABLE' AND quantity_available > 0 AND is_deleted = FALSE
) li ON li.location_id = wl.id
WHERE w.is_deleted = FALSE
GROUP BY w.id, w.warehouse_code, w.name, w.total_locations;

COMMENT ON VIEW warehouse.v_storage_utilization IS 'Storage utilisation per warehouse: occupied vs configured locations. Supports capacity planning.';


-- Picker productivity: lines per hour per picker
CREATE OR REPLACE VIEW warehouse.v_picking_productivity AS
SELECT
    pt.picker_id,
    pt.warehouse_id,
    DATE_TRUNC('day', pt.started_at)                   AS shift_date,
    COUNT(DISTINCT pt.id)                               AS tasks_completed,
    SUM(pt.lines_completed)                             AS total_lines_picked,
    ROUND(SUM(pt.travel_distance_m), 2)                 AS total_travel_m,
    ROUND(
        EXTRACT(EPOCH FROM SUM(pt.completed_at - pt.started_at)) / 3600.0, 4
    )                                                   AS total_hours,
    ROUND(
        SUM(pt.lines_completed)::NUMERIC /
        NULLIF(EXTRACT(EPOCH FROM SUM(pt.completed_at - pt.started_at)) / 3600.0, 0), 2
    )                                                   AS lines_per_hour
FROM warehouse.picking_tasks pt
WHERE pt.status = 'COMPLETED'
  AND pt.picker_id IS NOT NULL
  AND pt.started_at IS NOT NULL
  AND pt.completed_at IS NOT NULL
  AND pt.is_deleted = FALSE
GROUP BY pt.picker_id, pt.warehouse_id, DATE_TRUNC('day', pt.started_at);

COMMENT ON VIEW warehouse.v_picking_productivity IS 'Picker productivity aggregated by person and shift day. Key WMS KPI: lines-per-hour. Supports labour planning and performance management.';
