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
