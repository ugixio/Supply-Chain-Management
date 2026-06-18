-- =============================================================================
-- FINANCE & CONTROLLING SCHEMA
-- Ref: Chopra & Meindl (2016) Ch.2 (C2C); Bragg (2022) Controller's Guide
--      IFRS 15 (Revenue), IAS 2 (Inventories), IAS 39 (Financial Instruments)
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS finance;

-- Supplier invoices
CREATE TABLE finance.supplier_invoices (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_number      VARCHAR(100) NOT NULL UNIQUE,
    supplier_id         UUID NOT NULL REFERENCES procurement.suppliers(id),
    po_id               UUID REFERENCES procurement.purchase_orders(id),
    invoice_date        DATE NOT NULL,
    due_date            DATE NOT NULL,
    currency            CHAR(3) NOT NULL DEFAULT 'USD',
    subtotal_cents      BIGINT NOT NULL CHECK (subtotal_cents >= 0),
    tax_cents           BIGINT NOT NULL DEFAULT 0,
    total_cents         BIGINT NOT NULL,
    payment_terms       VARCHAR(50),   -- NET30, NET60, 2/10_NET30
    status              VARCHAR(20) NOT NULL DEFAULT 'RECEIVED' CHECK (status IN (
        'RECEIVED','MATCHING','APPROVED','DISPUTED','PAID','CANCELLED','WRITE_OFF'
    )),
    paid_at             TIMESTAMPTZ,
    payment_reference   VARCHAR(100),
    match_status        VARCHAR(20) CHECK (match_status IN ('PENDING','MATCHED','EXCEPTION','WAIVED')),
    is_deleted          BOOLEAN NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX ON finance.supplier_invoices (supplier_id, invoice_date DESC);
CREATE INDEX ON finance.supplier_invoices (status, due_date);

-- Invoice line items
CREATE TABLE finance.invoice_lines (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id          UUID NOT NULL REFERENCES finance.supplier_invoices(id),
    po_line_id          UUID,
    sku_id              UUID REFERENCES inventory.sku_master(id),
    description         VARCHAR(500) NOT NULL,
    quantity            NUMERIC(18,4) NOT NULL,
    unit_price_cents    INTEGER NOT NULL,
    line_total_cents    BIGINT GENERATED ALWAYS AS (ROUND(quantity * unit_price_cents)) STORED,
    tax_rate            NUMERIC(5,4) NOT NULL DEFAULT 0,
    gl_account          VARCHAR(20)
);

-- Goods Receipt Notes (for 3-way match)
CREATE TABLE finance.goods_receipt_notes (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    grn_number          VARCHAR(50) NOT NULL UNIQUE,
    po_id               UUID NOT NULL REFERENCES procurement.purchase_orders(id),
    supplier_id         UUID NOT NULL REFERENCES procurement.suppliers(id),
    received_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    warehouse_id        UUID,
    total_value_cents   BIGINT NOT NULL,
    is_deleted          BOOLEAN NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 3-way match results (PO ↔ GRN ↔ Invoice)
CREATE TABLE finance.three_way_match_results (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    invoice_id          UUID NOT NULL REFERENCES finance.supplier_invoices(id),
    po_id               UUID NOT NULL REFERENCES procurement.purchase_orders(id),
    grn_id              UUID NOT NULL REFERENCES finance.goods_receipt_notes(id),
    po_amount_cents     BIGINT NOT NULL,
    grn_amount_cents    BIGINT NOT NULL,
    invoice_amount_cents BIGINT NOT NULL,
    po_invoice_variance_cents BIGINT GENERATED ALWAYS AS (ABS(invoice_amount_cents - po_amount_cents)) STORED,
    grn_invoice_variance_cents BIGINT GENERATED ALWAYS AS (ABS(invoice_amount_cents - grn_amount_cents)) STORED,
    tolerance_pct       NUMERIC(5,2) NOT NULL DEFAULT 1.0,
    match_result        VARCHAR(20) NOT NULL CHECK (match_result IN ('MATCHED','EXCEPTION','APPROVED_EXCEPTION')),
    matched_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    matched_by          VARCHAR(100)
);
COMMENT ON TABLE finance.three_way_match_results IS '3-way match: PO ↔ GRN ↔ Invoice within 1% tolerance';

-- Working capital snapshots (for C2C calculation)
CREATE TABLE finance.working_capital_snapshots (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    snapshot_date       DATE NOT NULL UNIQUE,
    cogs_cents          BIGINT NOT NULL,
    avg_inventory_cents BIGINT NOT NULL,
    accounts_receivable_cents BIGINT NOT NULL,
    accounts_payable_cents    BIGINT NOT NULL,
    revenue_cents       BIGINT NOT NULL,
    itr                 NUMERIC(8,4) GENERATED ALWAYS AS (
        CASE WHEN avg_inventory_cents > 0 THEN ROUND(CAST(cogs_cents AS NUMERIC) / avg_inventory_cents, 4) ELSE 0 END
    ) STORED,
    dio_days            NUMERIC(8,2) GENERATED ALWAYS AS (
        CASE WHEN cogs_cents > 0 THEN ROUND(365.0 * avg_inventory_cents / NULLIF(cogs_cents,0), 2) ELSE NULL END
    ) STORED,
    dso_days            NUMERIC(8,2) GENERATED ALWAYS AS (
        CASE WHEN revenue_cents > 0 THEN ROUND(365.0 * accounts_receivable_cents / NULLIF(revenue_cents,0), 2) ELSE NULL END
    ) STORED,
    dpo_days            NUMERIC(8,2) GENERATED ALWAYS AS (
        CASE WHEN cogs_cents > 0 THEN ROUND(365.0 * accounts_payable_cents / NULLIF(cogs_cents,0), 2) ELSE NULL END
    ) STORED,
    c2c_days            NUMERIC(8,2),   -- populated by trigger: DIO + DSO - DPO
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON COLUMN finance.working_capital_snapshots.c2c_days IS 'C2C = DIO + DSO - DPO. Target <45 days for FMCG';

-- SC cost tracking
CREATE TABLE finance.sc_cost_tracking (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    period_month    DATE NOT NULL,
    cost_category   VARCHAR(50) NOT NULL CHECK (cost_category IN (
        'PROCUREMENT','WAREHOUSING','TRANSPORTATION','CUSTOMS','QUALITY','RETURN','OVERHEAD'
    )),
    amount_cents    BIGINT NOT NULL,
    revenue_cents   BIGINT NOT NULL,
    cost_pct        NUMERIC(6,2) GENERATED ALWAYS AS (
        ROUND(CAST(amount_cents AS NUMERIC) / NULLIF(revenue_cents, 0) * 100, 2)
    ) STORED,
    note            TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (period_month, cost_category)
);

-- Finance KPIs view
CREATE OR REPLACE VIEW finance.finance_kpis AS
SELECT
    snapshot_date,
    itr        AS inventory_turnover_ratio,
    dio_days,
    dso_days,
    dpo_days,
    c2c_days,
    ROUND(CAST(avg_inventory_cents AS NUMERIC) / 100, 2) AS avg_inventory_usd
FROM finance.working_capital_snapshots
ORDER BY snapshot_date DESC;

-- =============================================================================
-- BUDGET VARIANCE, PERIOD CLOSE, COST-TO-SERVE, ACCRUALS
-- Ref: Bragg "Controller's Handbook" (Wiley, 2022)
--      IAS 21 (FX), IAS 37 (Provisions / Accruals), IFRS 15 (Revenue)
--      Christopher (2022) Ch.4 — Customer Profitability / Cost-to-Serve
-- =============================================================================

-- Budget entries — planned spend per month per category
CREATE TABLE finance.budget_records (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    period_month    DATE NOT NULL,       -- first day of the fiscal month
    category        VARCHAR(20) NOT NULL CHECK (category IN (
        'PROCUREMENT','WAREHOUSING','TRANSPORTATION','CUSTOMS',
        'QUALITY','RETURNS','OVERHEAD','TOTAL'
    )),
    budget_cents    BIGINT NOT NULL CHECK (budget_cents >= 0),
    note            TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (period_month, category)
);
CREATE INDEX ON finance.budget_records (period_month DESC);

-- Budget variance — actual vs budget with GENERATED columns
CREATE TABLE finance.budget_variance (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    period_month    DATE NOT NULL,
    category        VARCHAR(20) NOT NULL CHECK (category IN (
        'PROCUREMENT','WAREHOUSING','TRANSPORTATION','CUSTOMS',
        'QUALITY','RETURNS','OVERHEAD','TOTAL'
    )),
    budget_cents    BIGINT NOT NULL CHECK (budget_cents >= 0),
    actual_cents    BIGINT NOT NULL CHECK (actual_cents >= 0),
    -- variance = actual - budget; negative = favorable
    variance_cents  BIGINT GENERATED ALWAYS AS (actual_cents - budget_cents) STORED,
    -- variance_pct rounded to 4 decimal places
    variance_pct    NUMERIC(10,4) GENERATED ALWAYS AS (
        CASE WHEN budget_cents = 0 THEN NULL
             ELSE ROUND(CAST(actual_cents - budget_cents AS NUMERIC) / budget_cents * 100, 4)
        END
    ) STORED,
    status          VARCHAR(12) GENERATED ALWAYS AS (
        CASE
            WHEN budget_cents = 0 THEN 'ON_BUDGET'
            WHEN ABS(CAST(actual_cents - budget_cents AS NUMERIC) / budget_cents * 100) < 2
                 THEN 'ON_BUDGET'
            WHEN actual_cents < budget_cents THEN 'FAVORABLE'
            ELSE 'UNFAVORABLE'
        END
    ) STORED,
    explanation     TEXT,
    action_required BOOLEAN GENERATED ALWAYS AS (
        budget_cents > 0 AND
        ABS(CAST(actual_cents - budget_cents AS NUMERIC) / budget_cents * 100) > 10
    ) STORED,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (period_month, category)
);
COMMENT ON TABLE finance.budget_variance IS
    'Budget vs actual per cost category. variance<0=favorable. |pct|>10 requires explanation.';
CREATE INDEX ON finance.budget_variance (period_month DESC, status);

-- Period-end close checklist and state
CREATE TABLE finance.period_close (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    period_month    DATE NOT NULL UNIQUE,   -- first day of the fiscal month
    fiscal_year     SMALLINT NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'OPEN' CHECK (status IN (
        'OPEN','IN_PROGRESS','PENDING_APPROVAL','APPROVED','CLOSED'
    )),
    checklist       JSONB NOT NULL DEFAULT '[]',
    -- Each element: {task: string, completed: boolean, completedBy?: string, completedAt?: timestamptz}
    opened_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    closed_at       TIMESTAMPTZ,
    approved_by     VARCHAR(100),
    approved_at     TIMESTAMPTZ,
    is_deleted      BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT period_close_approved_before_closed
        CHECK (closed_at IS NULL OR approved_at IS NOT NULL),
    CONSTRAINT period_close_closed_requires_approved
        CHECK (status != 'CLOSED' OR approved_by IS NOT NULL)
);
COMMENT ON TABLE finance.period_close IS
    'Period-end close checklist. All tasks must complete before approval; approval required before close.';
CREATE INDEX ON finance.period_close (fiscal_year, period_month DESC);

-- Cost-to-Serve — customer / SKU profitability
CREATE TABLE finance.cost_to_serve (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id             UUID,
    sku_id                  UUID,
    period_month            DATE NOT NULL,
    order_processing_cents  BIGINT NOT NULL DEFAULT 0 CHECK (order_processing_cents >= 0),
    picking_cents           BIGINT NOT NULL DEFAULT 0 CHECK (picking_cents >= 0),
    packing_cents           BIGINT NOT NULL DEFAULT 0 CHECK (packing_cents >= 0),
    transportation_cents    BIGINT NOT NULL DEFAULT 0 CHECK (transportation_cents >= 0),
    returns_cents           BIGINT NOT NULL DEFAULT 0 CHECK (returns_cents >= 0),
    customer_support_cents  BIGINT NOT NULL DEFAULT 0 CHECK (customer_support_cents >= 0),
    credit_risk_cents       BIGINT NOT NULL DEFAULT 0 CHECK (credit_risk_cents >= 0),
    total_cost_cents        BIGINT GENERATED ALWAYS AS (
        order_processing_cents + picking_cents + packing_cents +
        transportation_cents + returns_cents + customer_support_cents + credit_risk_cents
    ) STORED,
    revenue_cents           BIGINT NOT NULL CHECK (revenue_cents >= 0),
    gross_margin_cents      BIGINT GENERATED ALWAYS AS (
        revenue_cents - (
            order_processing_cents + picking_cents + packing_cents +
            transportation_cents + returns_cents + customer_support_cents + credit_risk_cents
        )
    ) STORED,
    gross_margin_pct        NUMERIC(8,4) GENERATED ALWAYS AS (
        CASE WHEN revenue_cents = 0 THEN NULL
             ELSE ROUND(
                 CAST(
                     revenue_cents - (
                         order_processing_cents + picking_cents + packing_cents +
                         transportation_cents + returns_cents + customer_support_cents + credit_risk_cents
                     ) AS NUMERIC
                 ) / revenue_cents * 100, 4)
        END
    ) STORED,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (customer_id, sku_id, period_month)
);
COMMENT ON TABLE finance.cost_to_serve IS
    'Customer/SKU cost-to-serve. Ref: Christopher (2022) Ch.4.';
CREATE INDEX ON finance.cost_to_serve (period_month DESC, gross_margin_pct);

-- Accruals and deferrals (IAS 37)
CREATE TABLE finance.accruals (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    period_month    DATE NOT NULL,          -- first day of the month the accrual belongs to
    description     VARCHAR(500) NOT NULL,
    amount_cents    BIGINT NOT NULL,        -- positive = expense accrual; negative = deferral credit
    accrual_type    VARCHAR(10) NOT NULL CHECK (accrual_type IN ('ACCRUAL', 'DEFERRAL')),
    gl_account      VARCHAR(20) NOT NULL,   -- General Ledger account code
    reversed_at     TIMESTAMPTZ,            -- when the reversing entry was posted
    is_reversed     BOOLEAN NOT NULL DEFAULT FALSE,
    created_by      VARCHAR(100),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT accruals_reversed_consistency
        CHECK (is_reversed = (reversed_at IS NOT NULL))
);
COMMENT ON TABLE finance.accruals IS
    'Accruals (expenses incurred not yet invoiced) and deferrals (cash received / paid not yet earned/expensed). Ref: IAS 37.';
CREATE INDEX ON finance.accruals (period_month DESC, is_reversed);

-- =============================================================================
-- VIEWS
-- =============================================================================

-- P&L summary by month: revenue, SC cost breakdown, margin
CREATE OR REPLACE VIEW finance.v_pl_summary AS
SELECT
    sc.period_month,
    SUM(CASE WHEN sc.cost_category = 'PROCUREMENT'    THEN sc.amount_cents ELSE 0 END) AS procurement_cents,
    SUM(CASE WHEN sc.cost_category = 'WAREHOUSING'    THEN sc.amount_cents ELSE 0 END) AS warehousing_cents,
    SUM(CASE WHEN sc.cost_category = 'TRANSPORTATION' THEN sc.amount_cents ELSE 0 END) AS transportation_cents,
    SUM(CASE WHEN sc.cost_category = 'QUALITY'        THEN sc.amount_cents ELSE 0 END) AS quality_cents,
    SUM(sc.amount_cents)                                                                  AS total_sc_cost_cents,
    MAX(sc.revenue_cents)                                                                 AS revenue_cents,
    MAX(sc.revenue_cents) - SUM(sc.amount_cents)                                         AS gross_margin_cents,
    ROUND(
        CAST(SUM(sc.amount_cents) AS NUMERIC) / NULLIF(MAX(sc.revenue_cents), 0) * 100, 2
    )                                                                                     AS sc_cost_pct_revenue
FROM finance.sc_cost_tracking sc
GROUP BY sc.period_month
ORDER BY sc.period_month DESC;
COMMENT ON VIEW finance.v_pl_summary IS
    'Monthly P&L summary: revenue, SC cost by category, gross margin, SC cost as % of revenue.';

-- Budget variance dashboard — current month, by category
CREATE OR REPLACE VIEW finance.v_budget_variance_dashboard AS
SELECT
    bv.period_month,
    bv.category,
    bv.budget_cents,
    bv.actual_cents,
    bv.variance_cents,
    bv.variance_pct,
    bv.status,
    bv.action_required,
    bv.explanation,
    CASE WHEN bv.status = 'FAVORABLE'   THEN TRUE
         WHEN bv.status = 'UNFAVORABLE' THEN FALSE
         ELSE NULL END                        AS is_favorable,
    bv.created_at
FROM finance.budget_variance bv
ORDER BY bv.period_month DESC, bv.status, ABS(bv.variance_pct) DESC NULLS LAST;
COMMENT ON VIEW finance.v_budget_variance_dashboard IS
    'Budget vs actual by category — current period. Flagged unfavorable and requires_explanation rows.';

-- Customer profitability ranking (gross margin % descending)
CREATE OR REPLACE VIEW finance.v_cost_to_serve_by_customer AS
SELECT
    cts.customer_id,
    cts.period_month,
    SUM(cts.revenue_cents)              AS total_revenue_cents,
    SUM(cts.total_cost_cents)           AS total_cost_cents,
    SUM(cts.gross_margin_cents)         AS total_gross_margin_cents,
    ROUND(
        CAST(SUM(cts.gross_margin_cents) AS NUMERIC)
        / NULLIF(SUM(cts.revenue_cents), 0) * 100, 4
    )                                   AS gross_margin_pct,
    SUM(cts.revenue_cents) > SUM(cts.total_cost_cents) AS is_profitable,
    COUNT(DISTINCT cts.sku_id)          AS sku_count
FROM finance.cost_to_serve cts
WHERE cts.customer_id IS NOT NULL
GROUP BY cts.customer_id, cts.period_month
ORDER BY gross_margin_pct DESC NULLS LAST;
COMMENT ON VIEW finance.v_cost_to_serve_by_customer IS
    'Customer profitability ranking by gross margin %. Ref: Christopher (2022) Ch.4.';

-- Period close status: checklist completion and blocking tasks
CREATE OR REPLACE VIEW finance.v_period_close_status AS
SELECT
    pc.id,
    pc.period_month,
    pc.fiscal_year,
    pc.status,
    pc.opened_at,
    pc.closed_at,
    pc.approved_by,
    pc.approved_at,
    jsonb_array_length(pc.checklist)                    AS total_tasks,
    (
        SELECT COUNT(*)
        FROM jsonb_array_elements(pc.checklist) AS item
        WHERE (item->>'completed')::boolean = TRUE
    )                                                   AS completed_tasks,
    ROUND(
        CAST(
            (SELECT COUNT(*) FROM jsonb_array_elements(pc.checklist) AS item
             WHERE (item->>'completed')::boolean = TRUE) AS NUMERIC
        ) / NULLIF(jsonb_array_length(pc.checklist), 0) * 100, 1
    )                                                   AS completion_pct,
    (
        SELECT jsonb_agg(item->>'task')
        FROM jsonb_array_elements(pc.checklist) AS item
        WHERE (item->>'completed')::boolean = FALSE
    )                                                   AS blocking_tasks
FROM finance.period_close pc
WHERE pc.is_deleted = FALSE
ORDER BY pc.period_month DESC;

-- =============================================================================
-- LANDED COST
-- Aligns with: LandedCost.ts
-- Rolls all import cost elements into a true per-unit landed cost (IAS 2 §10-11).
-- Recoverable VAT/GST is flagged is_recoverable=TRUE and excluded from the total.
-- =============================================================================

CREATE TABLE finance.landed_costs (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku_id                  VARCHAR(50) NOT NULL,
    po_id                   UUID REFERENCES procurement.purchase_orders(id),
    shipment_id             UUID,
    quantity                NUMERIC(18,4) NOT NULL CHECK (quantity > 0),
    currency                CHAR(3) NOT NULL DEFAULT 'USD',
    allocation_method       VARCHAR(20) NOT NULL DEFAULT 'BY_VALUE' CHECK (allocation_method IN (
        'BY_VALUE','BY_QUANTITY','BY_WEIGHT','BY_VOLUME'
    )),
    -- Computed totals (maintained from components by the application / compute())
    total_landed_cost_cents BIGINT NOT NULL DEFAULT 0 CHECK (total_landed_cost_cents >= 0),
    -- GENERATED: per-unit landed cost = round(total / quantity)
    unit_landed_cost_cents  BIGINT GENERATED ALWAYS AS (
        ROUND(total_landed_cost_cents::NUMERIC / NULLIF(quantity, 0))
    ) STORED,
    is_deleted              BOOLEAN NOT NULL DEFAULT FALSE,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX ON finance.landed_costs (sku_id) WHERE is_deleted = FALSE;
CREATE INDEX ON finance.landed_costs (po_id);
CREATE INDEX ON finance.landed_costs (shipment_id);
COMMENT ON TABLE finance.landed_costs IS
    'Per-SKU landed cost roll-up (goods + freight + insurance + duty + broker + '
    'handling + non-recoverable tax). unit_landed_cost_cents is GENERATED. '
    'Aligns with LandedCost.ts. Ref: IAS 2 §10-11 cost of purchase.';

-- Landed cost components (one row per cost element)
CREATE TABLE finance.landed_cost_components (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    landed_cost_id      UUID NOT NULL REFERENCES finance.landed_costs(id) ON DELETE CASCADE,
    component_type      VARCHAR(20) NOT NULL CHECK (component_type IN (
        'GOODS','FREIGHT','INSURANCE','DUTY','BROKER_FEE','HANDLING','TAX_NONRECOVERABLE','OTHER'
    )),
    amount_cents        BIGINT NOT NULL CHECK (amount_cents >= 0),
    -- Recoverable components (e.g. reclaimable VAT) are EXCLUDED from landed cost
    is_recoverable      BOOLEAN NOT NULL DEFAULT FALSE,
    description         VARCHAR(255),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX ON finance.landed_cost_components (landed_cost_id);
COMMENT ON TABLE finance.landed_cost_components IS
    'Individual import cost elements for a landed cost. Components with '
    'is_recoverable=TRUE (reclaimable VAT/GST) are excluded from the landed total.';

-- View: landed cost per SKU with duty/tax and freight-per-unit breakdown
CREATE OR REPLACE VIEW finance.v_landed_cost_by_sku AS
SELECT
    lc.id,
    lc.sku_id,
    lc.po_id,
    lc.shipment_id,
    lc.quantity,
    lc.currency,
    lc.allocation_method,
    lc.total_landed_cost_cents,
    lc.unit_landed_cost_cents,
    COALESCE(SUM(comp.amount_cents) FILTER (
        WHERE comp.component_type IN ('DUTY','TAX_NONRECOVERABLE')
        AND comp.is_recoverable = FALSE
    ), 0)                                       AS duty_and_tax_cents,
    COALESCE(SUM(comp.amount_cents) FILTER (
        WHERE comp.component_type = 'FREIGHT' AND comp.is_recoverable = FALSE
    ), 0)                                       AS freight_cents,
    ROUND(
        COALESCE(SUM(comp.amount_cents) FILTER (
            WHERE comp.component_type = 'FREIGHT' AND comp.is_recoverable = FALSE
        ), 0)::NUMERIC / NULLIF(lc.quantity, 0)
    )                                           AS freight_per_unit_cents
FROM finance.landed_costs lc
LEFT JOIN finance.landed_cost_components comp ON comp.landed_cost_id = lc.id
WHERE lc.is_deleted = FALSE
GROUP BY lc.id;
COMMENT ON VIEW finance.v_landed_cost_by_sku IS
    'Landed cost per SKU with duty+tax and freight-per-unit breakdown. '
    'Mirrors dutyAndTaxCents() and freightPerUnitCents() in LandedCost.ts.';
