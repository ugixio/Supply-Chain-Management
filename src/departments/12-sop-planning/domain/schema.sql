-- =============================================================================
-- S&OP PLANNING SCHEMA
-- Ref: Wallace & Stahl (2008) Sales & Operations Planning; APICS CPIM
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS sop;

-- S&OP cycles (monthly meeting cadence)
CREATE TABLE sop.sop_cycles (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cycle_month     DATE NOT NULL UNIQUE,   -- first day of month
    status          VARCHAR(20) NOT NULL DEFAULT 'OPEN' CHECK (status IN (
        'OPEN','DEMAND_REVIEW','SUPPLY_REVIEW','EXEC_REVIEW','APPROVED','LOCKED'
    )),
    facilitator     VARCHAR(100),
    approved_by     VARCHAR(100),
    approved_at     TIMESTAMPTZ,
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Demand review inputs (consensus forecast per SKU)
CREATE TABLE sop.demand_review_inputs (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sop_cycle_id        UUID NOT NULL REFERENCES sop.sop_cycles(id),
    sku_id              UUID NOT NULL REFERENCES inventory.sku_master(id),
    period_start        DATE NOT NULL,
    statistical_fcst    NUMERIC(18,4),    -- from forecasting.py
    sales_override      NUMERIC(18,4),
    marketing_lift      NUMERIC(18,4) DEFAULT 0,
    consensus_fcst      NUMERIC(18,4) NOT NULL,
    uom                 VARCHAR(10) NOT NULL DEFAULT 'EA',
    override_reason     TEXT,
    submitted_by        VARCHAR(100),
    submitted_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (sop_cycle_id, sku_id, period_start)
);

-- Supply review constraints
CREATE TABLE sop.supply_review_constraints (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sop_cycle_id        UUID NOT NULL REFERENCES sop.sop_cycles(id),
    constraint_type     VARCHAR(30) NOT NULL CHECK (constraint_type IN (
        'CAPACITY','MATERIAL','SUPPLIER','LOGISTICS','REGULATORY','BUDGET'
    )),
    description         VARCHAR(500) NOT NULL,
    sku_id              UUID REFERENCES inventory.sku_master(id),
    supplier_id         UUID REFERENCES procurement.suppliers(id),
    constrained_qty     NUMERIC(18,4),
    unconstrained_qty   NUMERIC(18,4),
    resolution          TEXT,
    resolved            BOOLEAN NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- S&OP scenarios (what-if analysis)
CREATE TABLE sop.sop_scenarios (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sop_cycle_id        UUID NOT NULL REFERENCES sop.sop_cycles(id),
    scenario_name       VARCHAR(200) NOT NULL,
    demand_upside_pct   NUMERIC(6,2) DEFAULT 0,
    demand_downside_pct NUMERIC(6,2) DEFAULT 0,
    cost_impact_cents   BIGINT,
    revenue_impact_cents BIGINT,
    is_selected         BOOLEAN NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Inventory targets set by S&OP
CREATE TABLE sop.inventory_targets (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sop_cycle_id        UUID NOT NULL REFERENCES sop.sop_cycles(id),
    sku_id              UUID NOT NULL REFERENCES inventory.sku_master(id),
    target_dos          NUMERIC(6,1) NOT NULL,   -- Days of Supply
    min_dos             NUMERIC(6,1),
    max_dos             NUMERIC(6,1),
    safety_stock_qty    NUMERIC(18,4),
    approved_at         TIMESTAMPTZ,
    UNIQUE (sop_cycle_id, sku_id)
);

-- Plan attainment tracking
CREATE TABLE sop.plan_attainment_log (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    period_month        DATE NOT NULL,
    sku_id              UUID NOT NULL REFERENCES inventory.sku_master(id),
    plan_qty            NUMERIC(18,4) NOT NULL,
    actual_qty          NUMERIC(18,4) NOT NULL,
    attainment_pct      NUMERIC(6,2) GENERATED ALWAYS AS (
        CASE WHEN plan_qty > 0 THEN ROUND(actual_qty / plan_qty * 100, 2) ELSE NULL END
    ) STORED,
    variance_qty        NUMERIC(18,4) GENERATED ALWAYS AS (actual_qty - plan_qty) STORED,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (period_month, sku_id)
);
COMMENT ON COLUMN sop.plan_attainment_log.attainment_pct IS 'World-class target ≥ 95%';

-- KPI view
CREATE OR REPLACE VIEW sop.sop_kpis AS
SELECT
    period_month,
    COUNT(*) AS sku_count,
    AVG(attainment_pct) AS avg_plan_attainment_pct,
    SUM(CASE WHEN attainment_pct >= 95 THEN 1 ELSE 0 END) AS skus_on_target
FROM sop.plan_attainment_log
GROUP BY period_month
ORDER BY period_month DESC;
