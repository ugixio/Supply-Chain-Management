-- =============================================================================
-- Schema: supply_planning
-- Aligns with: MaterialRequirement.ts
-- Feeds Python models:
--   python/04_supply_planning/mrp.py
--     -> run_mrp(sku_id, horizon)    uses mrp_buckets, bom, mps_master
--     -> explode_bom(parent_sku)     uses bill_of_materials
--   python/04_supply_planning/sop.py
--     -> rccp_load(work_center_id)   uses rccp_loads, work_centers
--     -> stability_index()           uses mps_master history
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS supply_planning;

-- ---------------------------------------------------------------------------
-- bill_of_materials
-- Single-level BOM. Multi-level explosion handled in mrp.py explode_bom().
-- lead_time_periods is in the same time bucket as MPS (weekly or monthly).
-- ---------------------------------------------------------------------------
CREATE TABLE supply_planning.bill_of_materials (
    id                  UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_sku          VARCHAR(50)   NOT NULL,
    component_sku       VARCHAR(50)   NOT NULL,
    quantity_per        NUMERIC(15,6) NOT NULL CHECK (quantity_per > 0),
    unit_of_measure     CHAR(3)       NOT NULL,   -- GS1 UOM code
    lead_time_periods   SMALLINT      NOT NULL DEFAULT 0 CHECK (lead_time_periods >= 0),
    -- Scrap / yield factor (1.0 = no scrap; 1.05 = 5% scrap allowance)
    scrap_factor        NUMERIC(6,4)  NOT NULL DEFAULT 1.0 CHECK (scrap_factor >= 1.0),
    -- BOM type
    bom_type            VARCHAR(15)   NOT NULL DEFAULT 'STANDARD'
                            CHECK (bom_type IN ('STANDARD','PHANTOM','CO_PRODUCT','BY_PRODUCT')),
    -- Effectivity dates for version control
    effective_from      DATE          NOT NULL DEFAULT '2000-01-01',
    effective_to        DATE,
    -- Substitution
    is_substitute_for   VARCHAR(50),     -- component_sku that this can replace
    is_active           BOOLEAN       NOT NULL DEFAULT TRUE,
    created_by          VARCHAR(100)  NOT NULL,
    created_at          TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    UNIQUE (parent_sku, component_sku, effective_from)
);

COMMENT ON TABLE supply_planning.bill_of_materials IS
    'Single-level Bill of Materials. Multi-level explosion is performed by '
    'python/04_supply_planning/mrp.py explode_bom(parent_sku) which recursively '
    'traverses this table. scrap_factor >= 1.0 inflates gross requirements. '
    'effective_from/to enables BOM engineering change control. '
    'PHANTOM bom_type components are not stocked — they pass requirements to their children.';

COMMENT ON COLUMN supply_planning.bill_of_materials.lead_time_periods IS
    'Procurement or manufacturing lead time in MPS time bucket units. '
    'Used by mrp.py to offset planned_release from planned_receipt by this many periods.';

COMMENT ON COLUMN supply_planning.bill_of_materials.scrap_factor IS
    '1.0 = no scrap. 1.05 = 5% scrap allowance. '
    'Gross requirement = net_req * quantity_per * scrap_factor.';

-- ---------------------------------------------------------------------------
-- work_centers
-- Production / processing capacity nodes.
-- Feeds rccp_load() in sop.py for Rough-Cut Capacity Planning.
-- ---------------------------------------------------------------------------
CREATE TABLE supply_planning.work_centers (
    id                      UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    work_center_code        VARCHAR(20)   NOT NULL UNIQUE,
    name                    VARCHAR(100)  NOT NULL,
    work_center_type        VARCHAR(20)   NOT NULL DEFAULT 'MANUFACTURING'
                                CHECK (work_center_type IN (
                                    'MANUFACTURING','ASSEMBLY','PACKAGING',
                                    'QUALITY','WAREHOUSE','OUTSOURCED'
                                )),
    -- Capacity parameters
    capacity_hours_per_day  NUMERIC(6,2)  NOT NULL DEFAULT 8.0 CHECK (capacity_hours_per_day > 0),
    working_days_per_period SMALLINT      NOT NULL DEFAULT 20 CHECK (working_days_per_period > 0),
    -- capacity_hours_per_period = capacity_hours_per_day * working_days_per_period
    efficiency_pct          NUMERIC(5,2)  NOT NULL DEFAULT 85.0
                                CHECK (efficiency_pct BETWEEN 1 AND 100),
    utilization_pct         NUMERIC(5,2)  NOT NULL DEFAULT 80.0
                                CHECK (utilization_pct BETWEEN 1 AND 100),
    -- Effective capacity = capacity_hours_per_period * (efficiency_pct/100) * (utilization_pct/100)
    -- Computed and cached by sop.py
    effective_capacity_hours NUMERIC(8,2),
    cost_per_hour_cents     INTEGER       CHECK (cost_per_hour_cents >= 0),
    warehouse_id            UUID,
    is_active               BOOLEAN       NOT NULL DEFAULT TRUE,
    created_at              TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE supply_planning.work_centers IS
    'Production work centres with capacity parameters. '
    'Feeds python/04_supply_planning/sop.py rccp_load(work_center_id, period_date). '
    'effective_capacity_hours = capacity_hours_per_day * working_days_per_period '
    '  * (efficiency_pct/100) * (utilization_pct/100). '
    'rccp_loads.overload_flag = TRUE when planned_load > effective_capacity_hours.';

COMMENT ON COLUMN supply_planning.work_centers.utilization_pct IS
    'Target utilisation rate (0-100%). Planned load should not exceed '
    'effective_capacity_hours. World-class manufacturing targets 85-90%.';

-- ---------------------------------------------------------------------------
-- mps_master
-- Master Production Schedule: what to make, when, in what quantity.
-- Feeds stability_index() and S&OP review in sop.py.
-- ---------------------------------------------------------------------------
CREATE TABLE supply_planning.mps_master (
    id                  UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    sku_id              VARCHAR(50)   NOT NULL,
    period_date         DATE          NOT NULL,    -- first day of period
    period_type         VARCHAR(10)   NOT NULL DEFAULT 'WEEKLY'
                            CHECK (period_type IN ('DAILY','WEEKLY','MONTHLY')),
    -- Planned = demand plan + inventory policy output
    planned_quantity    NUMERIC(15,4) NOT NULL DEFAULT 0 CHECK (planned_quantity >= 0),
    -- Confirmed = frozen within planning time fence
    confirmed_quantity  NUMERIC(15,4) NOT NULL DEFAULT 0 CHECK (confirmed_quantity >= 0),
    -- Actual = recorded production
    actual_quantity     NUMERIC(15,4) DEFAULT 0,
    -- ATP: Available-to-Promise = confirmed_quantity - open_customer_orders
    atp_quantity        NUMERIC(15,4),
    status              VARCHAR(20)   NOT NULL DEFAULT 'PLANNED'
                            CHECK (status IN ('PLANNED','FIRMED','IN_PRODUCTION','COMPLETED','CANCELLED')),
    -- Planning time fence: within this period changes are frozen
    within_time_fence   BOOLEAN       NOT NULL DEFAULT FALSE,
    work_center_id      UUID          REFERENCES supply_planning.work_centers(id),
    -- Revision tracking for stability_index()
    revision_number     SMALLINT      NOT NULL DEFAULT 1,
    previous_planned_qty NUMERIC(15,4),    -- stored for change magnitude calculation
    change_reason       TEXT,
    mrp_run_id          UUID,              -- FK set below
    created_by          VARCHAR(100)  NOT NULL,
    created_at          TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    UNIQUE (sku_id, period_date, period_type)
);

COMMENT ON TABLE supply_planning.mps_master IS
    'Master Production Schedule per SKU per period. '
    'confirmed_quantity is frozen within the planning time fence (within_time_fence=TRUE). '
    'planned_quantity changes outside the fence feed stability_index() in sop.py: '
    '  stability_index = 1 - (sum of |planned_qty - previous_planned_qty| / sum planned_qty). '
    'atp_quantity = confirmed_quantity - allocated customer orders; negative ATP triggers alert. '
    'Feeds mrp_buckets as the scheduled_receipt input for firmed production orders.';

COMMENT ON COLUMN supply_planning.mps_master.atp_quantity IS
    'Available-to-Promise. Negative ATP = overcommitted. '
    'Triggers exception in v_mrp_exceptions and escalation to sales planning.';

-- ---------------------------------------------------------------------------
-- mrp_runs
-- One row per MRP execution. Tracks horizon and status.
-- ---------------------------------------------------------------------------
CREATE TABLE supply_planning.mrp_runs (
    id                UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    run_code          VARCHAR(30) NOT NULL UNIQUE,
    run_date          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    horizon_periods   SMALLINT    NOT NULL CHECK (horizon_periods > 0),
    period_type       VARCHAR(10) NOT NULL DEFAULT 'WEEKLY'
                          CHECK (period_type IN ('DAILY','WEEKLY','MONTHLY')),
    regenerative      BOOLEAN     NOT NULL DEFAULT TRUE,   -- TRUE=full regen; FALSE=net change
    status            VARCHAR(15) NOT NULL DEFAULT 'RUNNING'
                          CHECK (status IN ('RUNNING','COMPLETED','FAILED','SUPERSEDED')),
    sku_filter        TEXT[],      -- NULL = all SKUs
    error_message     TEXT,
    run_duration_ms   INTEGER,
    created_by        VARCHAR(100) NOT NULL,
    completed_at      TIMESTAMPTZ
);

COMMENT ON TABLE supply_planning.mrp_runs IS
    'One record per MRP execution by python/04_supply_planning/mrp.py run_mrp(). '
    'regenerative=TRUE means a full recalculation from scratch (weekly). '
    'regenerative=FALSE means net-change MRP (recalculates only changed items, daily). '
    'All mrp_buckets and planned_orders reference a run_id so historical MRP runs '
    'can be compared and audited.';

-- ---------------------------------------------------------------------------
-- mrp_buckets
-- Core MRP output: time-phased material requirements.
-- PARTITIONED BY RANGE (period) for performance.
-- Classic MRP logic:
--   net_req = MAX(0, gross_req - projected_oh - scheduled_receipt)
--   projected_oh(t) = projected_oh(t-1) + scheduled_receipt(t) + planned_receipt(t) - gross_req(t)
-- ---------------------------------------------------------------------------
CREATE TABLE supply_planning.mrp_buckets (
    id                UUID          NOT NULL DEFAULT gen_random_uuid(),
    run_id            UUID          NOT NULL REFERENCES supply_planning.mrp_runs(id) ON DELETE CASCADE,
    sku_id            VARCHAR(50)   NOT NULL,
    period            DATE          NOT NULL,   -- first day of bucket period
    -- Classic MRP fields
    gross_req         NUMERIC(15,4) NOT NULL DEFAULT 0 CHECK (gross_req >= 0),
    scheduled_receipt NUMERIC(15,4) NOT NULL DEFAULT 0 CHECK (scheduled_receipt >= 0),
    projected_oh      NUMERIC(15,4) NOT NULL DEFAULT 0,   -- can be negative (shortage alert)
    net_req           NUMERIC(15,4) NOT NULL DEFAULT 0 CHECK (net_req >= 0),
    planned_receipt   NUMERIC(15,4) NOT NULL DEFAULT 0 CHECK (planned_receipt >= 0),
    planned_release   NUMERIC(15,4) NOT NULL DEFAULT 0 CHECK (planned_release >= 0),
    -- Safety stock requirement (from demand_planning.safety_stock_params)
    safety_stock_req  NUMERIC(15,4) NOT NULL DEFAULT 0,
    -- ATP this period
    atp_qty           NUMERIC(15,4),
    -- Lot sizing rule applied
    lot_sizing_rule   VARCHAR(15)   CHECK (lot_sizing_rule IN (
                          'L4L','FOQ','POQ','LUC','PPB','WAGNER_WHITIN'
                      )),
    created_at        TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    CONSTRAINT pk_mrp_buckets PRIMARY KEY (id, period)
) PARTITION BY RANGE (period);

COMMENT ON TABLE supply_planning.mrp_buckets IS
    'Time-phased MRP output per SKU per period per run. Partitioned by period quarter. '
    'Classic MRP logic (run by python/04_supply_planning/mrp.py): '
    '  gross_req    = dependent demand from BOM explosion + independent demand '
    '  projected_oh = prev_oh + scheduled_receipt + planned_receipt - gross_req '
    '  net_req      = MAX(0, gross_req + safety_stock_req - projected_oh - scheduled_receipt) '
    '  planned_receipt offset back by lead_time_periods -> planned_release. '
    'projected_oh < 0 flags a stock-out — captured in v_mrp_exceptions.';

COMMENT ON COLUMN supply_planning.mrp_buckets.lot_sizing_rule IS
    'L4L=Lot-for-Lot | FOQ=Fixed Order Qty | POQ=Periodic Order Qty | '
    'LUC=Least Unit Cost | PPB=Part Period Balancing | '
    'WAGNER_WHITIN=dynamic programming optimal lot size.';

-- Quarterly partitions for mrp_buckets
CREATE TABLE supply_planning.mrp_buckets_2024q1 PARTITION OF supply_planning.mrp_buckets FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');
CREATE TABLE supply_planning.mrp_buckets_2024q2 PARTITION OF supply_planning.mrp_buckets FOR VALUES FROM ('2024-04-01') TO ('2024-07-01');
CREATE TABLE supply_planning.mrp_buckets_2024q3 PARTITION OF supply_planning.mrp_buckets FOR VALUES FROM ('2024-07-01') TO ('2024-10-01');
CREATE TABLE supply_planning.mrp_buckets_2024q4 PARTITION OF supply_planning.mrp_buckets FOR VALUES FROM ('2024-10-01') TO ('2025-01-01');
CREATE TABLE supply_planning.mrp_buckets_2025q1 PARTITION OF supply_planning.mrp_buckets FOR VALUES FROM ('2025-01-01') TO ('2025-04-01');
CREATE TABLE supply_planning.mrp_buckets_2025q2 PARTITION OF supply_planning.mrp_buckets FOR VALUES FROM ('2025-04-01') TO ('2025-07-01');
CREATE TABLE supply_planning.mrp_buckets_2025q3 PARTITION OF supply_planning.mrp_buckets FOR VALUES FROM ('2025-07-01') TO ('2025-10-01');
CREATE TABLE supply_planning.mrp_buckets_2025q4 PARTITION OF supply_planning.mrp_buckets FOR VALUES FROM ('2025-10-01') TO ('2026-01-01');
CREATE TABLE supply_planning.mrp_buckets_2026q1 PARTITION OF supply_planning.mrp_buckets FOR VALUES FROM ('2026-01-01') TO ('2026-04-01');
CREATE TABLE supply_planning.mrp_buckets_2026q2 PARTITION OF supply_planning.mrp_buckets FOR VALUES FROM ('2026-04-01') TO ('2026-07-01');
CREATE TABLE supply_planning.mrp_buckets_2026q3 PARTITION OF supply_planning.mrp_buckets FOR VALUES FROM ('2026-07-01') TO ('2026-10-01');
CREATE TABLE supply_planning.mrp_buckets_2026q4 PARTITION OF supply_planning.mrp_buckets FOR VALUES FROM ('2026-10-01') TO ('2027-01-01');
CREATE TABLE supply_planning.mrp_buckets_default PARTITION OF supply_planning.mrp_buckets DEFAULT;

-- ---------------------------------------------------------------------------
-- planned_orders
-- Output of MRP: actionable purchase or production orders.
-- status=FIRM means manually confirmed (frozen). PLANNED = system generated.
-- ---------------------------------------------------------------------------
CREATE TABLE supply_planning.planned_orders (
    id               UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id           UUID          NOT NULL REFERENCES supply_planning.mrp_runs(id),
    sku_id           VARCHAR(50)   NOT NULL,
    order_type       VARCHAR(20)   NOT NULL CHECK (order_type IN ('PURCHASE','PRODUCTION','TRANSFER')),
    release_date     DATE          NOT NULL,
    receipt_date     DATE          NOT NULL,
    quantity         NUMERIC(15,4) NOT NULL CHECK (quantity > 0),
    uom              CHAR(3)       NOT NULL,
    lot_sizing_rule  VARCHAR(15)   CHECK (lot_sizing_rule IN (
                         'L4L','FOQ','POQ','LUC','PPB','WAGNER_WHITIN'
                     )),
    status           VARCHAR(20)   NOT NULL DEFAULT 'PLANNED'
                         CHECK (status IN ('PLANNED','FIRM','RELEASED','COMPLETED','CANCELLED')),
    supplier_id      UUID,             -- for PURCHASE orders
    work_center_id   UUID          REFERENCES supply_planning.work_centers(id),
    -- Pegging (traces order back to demand)
    demand_sku_id    VARCHAR(50),
    demand_period    DATE,
    -- Firming
    firmed_by        VARCHAR(100),
    firmed_at        TIMESTAMPTZ,
    is_deleted       BOOLEAN       NOT NULL DEFAULT FALSE,
    created_at       TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_planned_order_dates CHECK (receipt_date >= release_date)
);

COMMENT ON TABLE supply_planning.planned_orders IS
    'Actionable planned orders output from MRP. '
    'PLANNED orders are system-generated and may be changed by the next MRP run. '
    'FIRM orders are manually confirmed and protected from the next MRP run. '
    'PURCHASE orders trigger procurement.purchase_orders creation. '
    'PRODUCTION orders trigger work_center scheduling in rccp_loads. '
    'Pegging columns (demand_sku_id, demand_period) trace each order to its demand source.';

ALTER TABLE supply_planning.mps_master
    ADD CONSTRAINT fk_mps_mrp_run FOREIGN KEY (mrp_run_id)
        REFERENCES supply_planning.mrp_runs(id) ON DELETE SET NULL;

-- ---------------------------------------------------------------------------
-- rccp_loads
-- Rough-Cut Capacity Planning: planned vs available hours per work centre per period.
-- Feeds sop.py rccp_load(work_center_id, period_date).
-- overload_flag = TRUE when planned_load_hours > available_hours.
-- ---------------------------------------------------------------------------
CREATE TABLE supply_planning.rccp_loads (
    id                   UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id               UUID          NOT NULL REFERENCES supply_planning.mrp_runs(id) ON DELETE CASCADE,
    work_center_id       UUID          NOT NULL REFERENCES supply_planning.work_centers(id),
    period_date          DATE          NOT NULL,
    period_type          VARCHAR(10)   NOT NULL DEFAULT 'WEEKLY'
                             CHECK (period_type IN ('DAILY','WEEKLY','MONTHLY')),
    -- Capacity
    available_hours      NUMERIC(8,2)  NOT NULL CHECK (available_hours >= 0),
    -- Planned load from firmed MPS + planned production orders
    planned_load_hours   NUMERIC(8,2)  NOT NULL DEFAULT 0 CHECK (planned_load_hours >= 0),
    -- Utilisation
    utilisation_pct      NUMERIC(5,2) GENERATED ALWAYS AS (
                             CASE WHEN available_hours > 0
                                  THEN ROUND((planned_load_hours / available_hours * 100)::NUMERIC, 2)
                                  ELSE NULL
                             END
                         ) STORED,
    overload_flag        BOOLEAN NOT NULL GENERATED ALWAYS AS (
                             planned_load_hours > available_hours
                         ) STORED,
    -- Slack or deficit hours (positive = capacity available; negative = overload)
    slack_hours          NUMERIC(8,2) GENERATED ALWAYS AS (
                             available_hours - planned_load_hours
                         ) STORED,
    created_at           TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    UNIQUE (run_id, work_center_id, period_date)
);

COMMENT ON TABLE supply_planning.rccp_loads IS
    'Rough-Cut Capacity Planning loads per work centre per period. '
    'overload_flag (GENERATED) = TRUE when planned_load_hours > available_hours. '
    'utilisation_pct (GENERATED) = planned_load / available * 100. '
    'slack_hours (GENERATED) = available - planned (negative = overload). '
    'Feeds python/04_supply_planning/sop.py rccp_load() which aggregates loads '
    'and recommends overtime, subcontracting, or demand shaping.';

COMMENT ON COLUMN supply_planning.rccp_loads.overload_flag IS
    'TRUE when planned_load_hours > available_hours. '
    'GENERATED column - automatically set. Overloaded periods appear in v_mrp_exceptions.';

-- ---------------------------------------------------------------------------
-- Indexes
-- ---------------------------------------------------------------------------
CREATE INDEX idx_bom_parent     ON supply_planning.bill_of_materials(parent_sku)    WHERE is_active = TRUE;
CREATE INDEX idx_bom_component  ON supply_planning.bill_of_materials(component_sku) WHERE is_active = TRUE;
CREATE INDEX idx_bom_effective  ON supply_planning.bill_of_materials(parent_sku, effective_from, effective_to);

CREATE INDEX idx_mps_sku        ON supply_planning.mps_master(sku_id, period_date);
CREATE INDEX idx_mps_period     ON supply_planning.mps_master(period_date, status);
CREATE INDEX idx_mps_fence      ON supply_planning.mps_master(within_time_fence) WHERE within_time_fence = TRUE;

CREATE INDEX idx_mrp_buckets_sku_period ON supply_planning.mrp_buckets(sku_id, period);
CREATE INDEX idx_mrp_buckets_run        ON supply_planning.mrp_buckets(run_id);
CREATE INDEX idx_mrp_buckets_shortage   ON supply_planning.mrp_buckets(sku_id, period) WHERE projected_oh < 0;

CREATE INDEX idx_planned_orders_sku     ON supply_planning.planned_orders(sku_id, release_date);
CREATE INDEX idx_planned_orders_status  ON supply_planning.planned_orders(status)       WHERE is_deleted = FALSE;
CREATE INDEX idx_planned_orders_supplier ON supply_planning.planned_orders(supplier_id) WHERE order_type = 'PURCHASE';

CREATE INDEX idx_rccp_wc_period  ON supply_planning.rccp_loads(work_center_id, period_date);
CREATE INDEX idx_rccp_overload   ON supply_planning.rccp_loads(period_date, work_center_id) WHERE overload_flag = TRUE;

-- ---------------------------------------------------------------------------
-- VIEW: v_mrp_exceptions
-- Overloaded work centres and negative ATP / projected OH.
-- Primary alert list for the planning team.
-- ---------------------------------------------------------------------------
CREATE VIEW supply_planning.v_mrp_exceptions AS
-- Stock-out risk: projected_oh < 0 or net_req > 0 with no planned receipt
SELECT
    'STOCK_SHORTAGE'    AS exception_type,
    mb.sku_id,
    mb.period           AS period_date,
    NULL::UUID          AS work_center_id,
    NULL::VARCHAR(100)  AS work_center_name,
    mb.projected_oh     AS severity_value,
    mb.net_req          AS additional_value,
    run.run_code,
    run.run_date
FROM supply_planning.mrp_buckets mb
JOIN supply_planning.mrp_runs run ON mb.run_id = run.id
WHERE mb.projected_oh < 0
  AND run.status = 'COMPLETED'

UNION ALL

-- Capacity overload
SELECT
    'CAPACITY_OVERLOAD'  AS exception_type,
    NULL                 AS sku_id,
    rc.period_date,
    rc.work_center_id,
    wc.name              AS work_center_name,
    rc.planned_load_hours AS severity_value,
    rc.slack_hours        AS additional_value,
    run.run_code,
    run.run_date
FROM supply_planning.rccp_loads rc
JOIN supply_planning.work_centers wc ON rc.work_center_id = wc.id
JOIN supply_planning.mrp_runs run    ON rc.run_id         = run.id
WHERE rc.overload_flag = TRUE
  AND run.status = 'COMPLETED'

UNION ALL

-- Negative ATP in MPS
SELECT
    'NEGATIVE_ATP'      AS exception_type,
    mps.sku_id,
    mps.period_date,
    NULL                AS work_center_id,
    NULL                AS work_center_name,
    mps.atp_quantity    AS severity_value,
    mps.confirmed_quantity AS additional_value,
    NULL                AS run_code,
    mps.updated_at      AS run_date
FROM supply_planning.mps_master mps
WHERE mps.atp_quantity < 0

ORDER BY run_date DESC, exception_type, period_date;

COMMENT ON VIEW supply_planning.v_mrp_exceptions IS
    'Unified exception list for MRP planners. Three exception types: '
    'STOCK_SHORTAGE (projected_oh < 0), CAPACITY_OVERLOAD (rccp_loads.overload_flag), '
    'NEGATIVE_ATP (mps_master.atp_quantity < 0). '
    'severity_value carries the deficit quantity (negative = shortage) or overload hours. '
    'Consumed by sop.py and the planning dashboard for daily exception management.';

-- ---------------------------------------------------------------------------
-- VIEW: v_mps_stability
-- Tracks MPS revision history for stability_index calculation.
-- stability_index = 1 - sum(|change|) / sum(original_planned)
-- Target stability_index >= 0.85 (world-class S&OP).
-- ---------------------------------------------------------------------------
CREATE VIEW supply_planning.v_mps_stability AS
SELECT
    sku_id,
    period_date,
    period_type,
    planned_quantity,
    previous_planned_qty,
    confirmed_quantity,
    ABS(planned_quantity - COALESCE(previous_planned_qty, planned_quantity)) AS change_magnitude,
    CASE
        WHEN COALESCE(previous_planned_qty, planned_quantity) > 0
        THEN ABS(planned_quantity - COALESCE(previous_planned_qty, planned_quantity))
             / COALESCE(previous_planned_qty, planned_quantity) * 100
        ELSE 0
    END AS change_pct,
    revision_number,
    change_reason,
    within_time_fence,
    updated_at
FROM supply_planning.mps_master
ORDER BY sku_id, period_date;

COMMENT ON VIEW supply_planning.v_mps_stability IS
    'MPS revision tracking per SKU per period. '
    'change_magnitude and change_pct feed sop.py stability_index() calculation: '
    '  stability_index = 1 - SUM(change_magnitude) / SUM(original_planned_qty). '
    'Target stability_index >= 0.85. Changes within_time_fence=TRUE are especially '
    'disruptive and tracked separately for nervousness KPI reporting.';

-- ---------------------------------------------------------------------------
-- VIEW: v_bom_explosion_summary
-- One-level BOM view with effective quantities (including scrap).
-- mrp.py uses this for gross requirement calculation.
-- ---------------------------------------------------------------------------
CREATE VIEW supply_planning.v_bom_explosion_summary AS
SELECT
    b.parent_sku,
    b.component_sku,
    b.quantity_per,
    b.scrap_factor,
    ROUND((b.quantity_per * b.scrap_factor)::NUMERIC, 6) AS effective_qty_per,
    b.unit_of_measure,
    b.lead_time_periods,
    b.bom_type,
    b.effective_from,
    b.effective_to
FROM supply_planning.bill_of_materials b
WHERE b.is_active = TRUE
  AND b.effective_from <= CURRENT_DATE
  AND (b.effective_to IS NULL OR b.effective_to >= CURRENT_DATE);

COMMENT ON VIEW supply_planning.v_bom_explosion_summary IS
    'Active BOM lines with effective_qty_per = quantity_per * scrap_factor. '
    'python/04_supply_planning/mrp.py explode_bom() uses effective_qty_per '
    'to calculate gross requirements: gross_req = parent_net_req * effective_qty_per.';
