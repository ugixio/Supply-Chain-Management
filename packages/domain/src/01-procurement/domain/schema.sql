-- =============================================================================
-- Schema: procurement
-- Aligns with: PurchaseOrder.ts, Supplier.ts, Contract.ts, RFQ.ts
-- Feeds Python models:
--   python/01_procurement/kraljic.py         -> supply_risk_score, profit_impact_score, kraljic_quadrant
--   python/01_procurement/rfq_evaluator.py   -> rfq_quotes scores, evaluate_rfq()
--   python/01_procurement/tco.py             -> tco_analysis, calculate_tco()
--   python/01_procurement/contract_pricing.py-> contracts escalation fields, adjusted_price()
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS procurement;

-- ---------------------------------------------------------------------------
-- suppliers
-- Master supplier record. Kraljic segmentation scores are written back by
-- kraljic.py after each scoring run. UFLPA / CSDDD compliance fields are
-- maintained by the compliance module and read here for PO gating.
-- ---------------------------------------------------------------------------
CREATE TABLE procurement.suppliers (
    id                                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    supplier_code                       VARCHAR(20) NOT NULL UNIQUE,
    legal_name                          VARCHAR(255) NOT NULL,
    country_code                        CHAR(2)     NOT NULL,   -- ISO 3166-1 alpha-2
    currency                            CHAR(3)     NOT NULL,   -- ISO 4217
    -- -----------------------------------------------------------------------
    -- Kraljic Matrix segmentation
    -- Columns read by kraljic.py to place supplier in quadrant.
    -- supply_risk_score  : 0-10 composite of single-source risk, geo-political
    --                      risk, switching cost, market concentration (HHI)
    -- profit_impact_score: 0-10 composite of spend share, margin sensitivity
    -- kraljic_quadrant   : derived label written back by kraljic.py
    -- -----------------------------------------------------------------------
    supply_risk_score                   NUMERIC(4,2) CHECK (supply_risk_score BETWEEN 0 AND 10),
    profit_impact_score                 NUMERIC(4,2) CHECK (profit_impact_score BETWEEN 0 AND 10),
    kraljic_quadrant                    VARCHAR(20)  CHECK (kraljic_quadrant IN (
                                            'STRATEGIC', 'LEVERAGE', 'BOTTLENECK', 'NON_CRITICAL'
                                        )),
    -- -----------------------------------------------------------------------
    -- Security certifications (ISO 28000:2022, C-TPAT, AEO)
    -- -----------------------------------------------------------------------
    iso28000_certified                  BOOLEAN     NOT NULL DEFAULT FALSE,
    iso28000_expiry_date                DATE,
    ctpat_certified                     BOOLEAN     NOT NULL DEFAULT FALSE,
    ctpat_expiry_date                   DATE,
    aeo_certified                       BOOLEAN     NOT NULL DEFAULT FALSE,
    aeo_certificate_number              VARCHAR(50),
    aeo_expiry_date                     DATE,
    -- -----------------------------------------------------------------------
    -- UFLPA (Uyghur Forced Labor Prevention Act, Pub.L. 117-78)
    -- has_xuar_operations = TRUE triggers rebuttable presumption check.
    -- clearance_document_ref is mandatory when has_xuar_operations = TRUE.
    -- -----------------------------------------------------------------------
    has_xuar_operations                 BOOLEAN     NOT NULL DEFAULT FALSE,
    uflpa_risk_level                    VARCHAR(15)  CHECK (uflpa_risk_level IN (
                                            'PROHIBITED', 'HIGH', 'MEDIUM', 'LOW'
                                        )),
    clearance_document_ref              VARCHAR(255),
    -- -----------------------------------------------------------------------
    -- UK Modern Slavery Act 2015 §54
    -- Required for suppliers with turnover >= GBP 36 million.
    -- -----------------------------------------------------------------------
    modern_slavery_statement_published  BOOLEAN     NOT NULL DEFAULT FALSE,
    modern_slavery_statement_year       SMALLINT    CHECK (modern_slavery_statement_year >= 2015),
    modern_slavery_statement_url        TEXT,
    -- -----------------------------------------------------------------------
    -- CSDDD 2024/1760 due diligence status
    -- -----------------------------------------------------------------------
    csddd_assessment_date               DATE,
    csddd_next_review_date              DATE,
    lksg_compliant                      BOOLEAN,    -- German Supply Chain Act (LkSG)
    -- -----------------------------------------------------------------------
    -- Contact & operational
    -- -----------------------------------------------------------------------
    payment_terms_days                  SMALLINT    DEFAULT 30 CHECK (payment_terms_days >= 0),
    lead_time_days                      SMALLINT    CHECK (lead_time_days >= 0),
    incoterm_preference                 CHAR(3)     CHECK (incoterm_preference IN (
                                            'EXW','FCA','CPT','CIP','DAP','DPU','DDP',
                                            'FAS','FOB','CFR','CIF'
                                        )),
    website_url                         TEXT,
    contact_email                       VARCHAR(255),
    -- -----------------------------------------------------------------------
    -- Record control
    -- -----------------------------------------------------------------------
    status                              VARCHAR(20) NOT NULL DEFAULT 'ACTIVE'
                                            CHECK (status IN ('ACTIVE','INACTIVE','BLOCKED','PENDING_AUDIT')),
    is_deleted                          BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at                          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE procurement.suppliers IS
    'Master supplier record. Kraljic scores (supply_risk_score, profit_impact_score) '
    'are inputs and outputs of python/01_procurement/kraljic.py. '
    'UFLPA fields gate PO creation: a PO cannot be APPROVED when uflpa_risk_level = PROHIBITED. '
    'ISO 28000 / C-TPAT / AEO fields are read by the logistics module for shipment risk scoring.';

COMMENT ON COLUMN procurement.suppliers.supply_risk_score IS
    'Kraljic supply risk axis (0=no risk, 10=extreme). '
    'Inputs to kraljic.py: market_concentration_hhi, single_source_flag, geo_risk_index, switching_cost_index.';
COMMENT ON COLUMN procurement.suppliers.profit_impact_score IS
    'Kraljic profit impact axis (0=no impact, 10=extreme). '
    'Inputs to kraljic.py: spend_share_pct, margin_sensitivity, volume_criticality.';
COMMENT ON COLUMN procurement.suppliers.has_xuar_operations IS
    'TRUE if supplier has manufacturing/sourcing in Xinjiang Uyghur Autonomous Region. '
    'Triggers UFLPA rebuttable-presumption workflow. clearance_document_ref becomes mandatory.';

-- ---------------------------------------------------------------------------
-- supplier_hs_codes
-- HS codes per supplier for UFLPA high-priority screening and customs duty calculation.
-- ---------------------------------------------------------------------------
CREATE TABLE procurement.supplier_hs_codes (
    id                   UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    supplier_id          UUID        NOT NULL REFERENCES procurement.suppliers(id) ON DELETE RESTRICT,
    hs_code              VARCHAR(10) NOT NULL,  -- 6-10 digit HS/HTS code
    commodity_description TEXT,
    is_uflpa_high_priority BOOLEAN   NOT NULL DEFAULT FALSE,  -- CBP UFLPA Entity List flag
    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (supplier_id, hs_code)
);

COMMENT ON TABLE procurement.supplier_hs_codes IS
    'HS/HTS codes per supplier. is_uflpa_high_priority flags codes on the CBP UFLPA Entity List '
    '(cotton, polysilicon, tomatoes, etc.). Read by compliance/UFLPA.ts assessUFLPARisk().';

-- ---------------------------------------------------------------------------
-- purchase_orders
-- Partitioned by created_at year for archival performance.
-- Business rule: total_amount_cents >= PO_APPROVAL_THRESHOLD_CENTS (500000 = $5,000)
--   -> status must pass through PENDING_APPROVAL before APPROVED.
-- ---------------------------------------------------------------------------
CREATE TABLE procurement.purchase_orders (
    id                       UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    po_number                VARCHAR(30) NOT NULL UNIQUE,
    supplier_id              UUID        NOT NULL REFERENCES procurement.suppliers(id) ON DELETE RESTRICT,
    contract_id              UUID,                   -- FK set after table creation (see below)
    rfq_id                   UUID,                   -- FK set after table creation
    status                   VARCHAR(25) NOT NULL DEFAULT 'DRAFT'
                                CHECK (status IN (
                                    'DRAFT', 'PENDING_APPROVAL', 'APPROVED', 'SENT',
                                    'ACKNOWLEDGED', 'PARTIALLY_RECEIVED',
                                    'FULLY_RECEIVED', 'CANCELLED', 'CLOSED'
                                )),
    incoterm                 CHAR(3)     NOT NULL
                                CHECK (incoterm IN (
                                    'EXW','FCA','CPT','CIP','DAP','DPU','DDP',
                                    'FAS','FOB','CFR','CIF'
                                )),
    incoterm_location        VARCHAR(100),           -- Named place / port (Incoterms 2020)
    currency                 CHAR(3)     NOT NULL,
    total_amount_cents       BIGINT      NOT NULL CHECK (total_amount_cents >= 0),
    -- Approval workflow (PO_APPROVAL_THRESHOLD_CENTS = 500000, i.e. $5,000)
    requires_approval        BOOLEAN     NOT NULL DEFAULT FALSE,
    approved_by              VARCHAR(100),
    approved_at              TIMESTAMPTZ,
    rejected_by              VARCHAR(100),
    rejected_at              TIMESTAMPTZ,
    rejection_reason         TEXT,
    -- Delivery
    requested_delivery_date  DATE        NOT NULL,
    confirmed_delivery_date  DATE,
    actual_delivery_date     DATE,
    warehouse_id             UUID,
    -- UN/EDIFACT message tracking
    edifact_orders_ref       VARCHAR(50),  -- ORDERS message reference
    edifact_ordrsp_ref       VARCHAR(50),  -- ORDRSP (order response) reference
    -- Hazmat
    contains_hazmat          BOOLEAN     NOT NULL DEFAULT FALSE,
    -- Shipping & insurance
    freight_cost_cents       INTEGER     DEFAULT 0 CHECK (freight_cost_cents >= 0),
    insurance_cost_cents     INTEGER     DEFAULT 0 CHECK (insurance_cost_cents >= 0),
    -- Record control
    special_instructions     TEXT,
    is_deleted               BOOLEAN     NOT NULL DEFAULT FALSE,
    created_by               VARCHAR(100) NOT NULL,
    created_at               TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at               TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    -- Constraint: approved POs must have approver recorded
    CONSTRAINT chk_approval_fields CHECK (
        (status NOT IN ('APPROVED') OR (approved_by IS NOT NULL AND approved_at IS NOT NULL))
    )
) PARTITION BY RANGE (created_at);

COMMENT ON TABLE procurement.purchase_orders IS
    'Purchase order header. Partitioned by created_at year. '
    'Soft-delete only (is_deleted). Never hard-delete — financial record. '
    'total_amount_cents >= 500000 (USD 5,000) forces requires_approval = TRUE. '
    'UFLPA check runs on APPROVED transition via supplier.has_xuar_operations.';
COMMENT ON COLUMN procurement.purchase_orders.total_amount_cents IS
    'Always integer cents. Sum of po_lines.line_total_cents. Currency in currency column.';
COMMENT ON COLUMN procurement.purchase_orders.incoterm IS
    'Incoterms 2020 three-letter code. DPU replaces DAT from 2020. '
    'Drives insurance responsibility and risk transfer point in logistics module.';

-- Yearly partitions (2023-2028 covers typical planning horizon)
CREATE TABLE procurement.purchase_orders_2023 PARTITION OF procurement.purchase_orders
    FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');
CREATE TABLE procurement.purchase_orders_2024 PARTITION OF procurement.purchase_orders
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');
CREATE TABLE procurement.purchase_orders_2025 PARTITION OF procurement.purchase_orders
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');
CREATE TABLE procurement.purchase_orders_2026 PARTITION OF procurement.purchase_orders
    FOR VALUES FROM ('2026-01-01') TO ('2027-01-01');
CREATE TABLE procurement.purchase_orders_2027 PARTITION OF procurement.purchase_orders
    FOR VALUES FROM ('2027-01-01') TO ('2028-01-01');
CREATE TABLE procurement.purchase_orders_default PARTITION OF procurement.purchase_orders DEFAULT;

-- ---------------------------------------------------------------------------
-- po_lines
-- Line items within a PO. line_total_cents is a generated column.
-- ---------------------------------------------------------------------------
CREATE TABLE procurement.po_lines (
    id                 UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    po_id              UUID          NOT NULL REFERENCES procurement.purchase_orders(id) ON DELETE RESTRICT,
    line_number        SMALLINT      NOT NULL CHECK (line_number > 0),
    sku_id             VARCHAR(50)   NOT NULL,
    description        TEXT,
    quantity_value     NUMERIC(15,4) NOT NULL CHECK (quantity_value > 0),
    quantity_uom       CHAR(3)       NOT NULL,   -- GS1 UOM code (e.g. 'EA','KGM','LTR','MTR')
    unit_price_cents   INTEGER       NOT NULL CHECK (unit_price_cents >= 0),
    -- Generated: avoids drift between header and lines
    line_total_cents   BIGINT        GENERATED ALWAYS AS (
                           ROUND(quantity_value * unit_price_cents)::BIGINT
                       ) STORED,
    received_qty       NUMERIC(15,4) NOT NULL DEFAULT 0 CHECK (received_qty >= 0),
    cancelled_qty      NUMERIC(15,4) NOT NULL DEFAULT 0 CHECK (cancelled_qty >= 0),
    -- Lot / batch reference (populated on receipt)
    lot_id             UUID,
    -- Hazmat classification (IMDG / ADR class)
    hazmat_class       VARCHAR(10),
    un_number          VARCHAR(6),               -- UN hazmat number e.g. 'UN1263'
    created_at         TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    UNIQUE (po_id, line_number)
);

COMMENT ON TABLE procurement.po_lines IS
    'PO line items. line_total_cents is a GENERATED column (quantity * unit_price). '
    'Never float for money: unit_price_cents and line_total_cents are integer cents. '
    'received_qty feeds the PARTIALLY_RECEIVED / FULLY_RECEIVED status transitions.';
COMMENT ON COLUMN procurement.po_lines.quantity_uom IS
    'GS1 UN/ECE Rec 20 UOM code. Examples: EA=Each, KGM=Kilogram, LTR=Litre, MTR=Metre.';

-- ---------------------------------------------------------------------------
-- contracts
-- Frame agreements and blanket POs. Price escalation clause feeds
-- python/01_procurement/contract_pricing.py adjusted_price().
-- ---------------------------------------------------------------------------
CREATE TABLE procurement.contracts (
    id                     UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    contract_number        VARCHAR(30) NOT NULL UNIQUE,
    supplier_id            UUID        NOT NULL REFERENCES procurement.suppliers(id) ON DELETE RESTRICT,
    contract_type          VARCHAR(20) NOT NULL
                               CHECK (contract_type IN (
                                   'FRAME_AGREEMENT', 'BLANKET_PO', 'VMI', 'CONSIGNMENT'
                               )),
    status                 VARCHAR(20) NOT NULL DEFAULT 'DRAFT'
                               CHECK (status IN ('DRAFT','ACTIVE','EXPIRED','TERMINATED')),
    start_date             DATE        NOT NULL,
    end_date               DATE        NOT NULL,
    currency               CHAR(3)     NOT NULL,
    total_value_cents      BIGINT      CHECK (total_value_cents >= 0),
    minimum_order_value_cents BIGINT   DEFAULT 0,
    -- -----------------------------------------------------------------------
    -- Price escalation clause
    -- Feeds adjusted_price(base_price, cpi_now, ppi_now, base_cpi, base_ppi,
    --                       material_weight, labor_weight) in contract_pricing.py.
    -- Formula: P_adj = P_base * (material_weight*(CPI_t/CPI_0) + labor_weight*(PPI_t/PPI_0))
    -- -----------------------------------------------------------------------
    has_price_escalation   BOOLEAN     NOT NULL DEFAULT FALSE,
    escalation_index       VARCHAR(50),            -- 'CPI', 'PPI', 'CUSTOM'
    material_weight        NUMERIC(5,4) CHECK (material_weight BETWEEN 0 AND 1),
    labor_weight           NUMERIC(5,4) CHECK (labor_weight   BETWEEN 0 AND 1),
    base_cpi               NUMERIC(10,4),          -- CPI at contract signing
    base_ppi               NUMERIC(10,4),          -- PPI at contract signing
    escalation_cap_pct     NUMERIC(5,2),            -- max allowed increase %
    -- Incoterms
    incoterm               CHAR(3)     CHECK (incoterm IN (
                               'EXW','FCA','CPT','CIP','DAP','DPU','DDP',
                               'FAS','FOB','CFR','CIF'
                           )),
    incoterm_location      VARCHAR(100),
    -- Review / renewal
    review_date            DATE,
    auto_renewal           BOOLEAN     NOT NULL DEFAULT FALSE,
    renewal_notice_days    SMALLINT    DEFAULT 90,
    -- Record control
    is_deleted             BOOLEAN     NOT NULL DEFAULT FALSE,
    created_by             VARCHAR(100) NOT NULL,
    created_at             TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at             TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_contract_dates CHECK (end_date > start_date),
    CONSTRAINT chk_escalation_weights CHECK (
        NOT has_price_escalation
        OR (material_weight IS NOT NULL AND labor_weight IS NOT NULL
            AND (material_weight + labor_weight) <= 1.0001)  -- float tolerance
    )
);

COMMENT ON TABLE procurement.contracts IS
    'Supplier contracts including frame agreements, blanket POs, VMI, and consignment. '
    'Price escalation columns (material_weight, labor_weight, base_cpi, base_ppi) feed '
    'python/01_procurement/contract_pricing.py adjusted_price() which implements '
    'the standard price adjustment formula: '
    'P_adj = P_base * (mat_w * (CPI_t/CPI_0) + lab_w * (PPI_t/PPI_0)).';
COMMENT ON COLUMN procurement.contracts.material_weight IS
    'Fraction of price driven by material cost (0-1). With labor_weight must sum <= 1. '
    'Used in adjusted_price() escalation formula.';

-- ---------------------------------------------------------------------------
-- rfq
-- Request for Quotation / Proposal / Information / Invitation to Tender.
-- Evaluation weights feed evaluate_rfq() in Python: weighted_score =
--   price*weight_price + quality*weight_quality + ...
-- ---------------------------------------------------------------------------
CREATE TABLE procurement.rfq (
    id                    UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    rfq_number            VARCHAR(30) NOT NULL UNIQUE,
    rfq_type              VARCHAR(5)  NOT NULL CHECK (rfq_type IN ('RFQ','RFP','RFI','ITT')),
    status                VARCHAR(20) NOT NULL DEFAULT 'DRAFT'
                              CHECK (status IN ('DRAFT','ISSUED','CLOSED','AWARDED','CANCELLED')),
    issue_date            DATE,
    closing_date          DATE        NOT NULL,
    awarded_supplier_id   UUID        REFERENCES procurement.suppliers(id),
    awarded_at            TIMESTAMPTZ,
    currency              CHAR(3)     NOT NULL,
    -- -----------------------------------------------------------------------
    -- Evaluation weights — must sum to 100 (enforced at application layer and by CHECK).
    -- These are read by python/01_procurement/rfq_evaluator.py evaluate_rfq()
    -- to compute weighted_total_score for each rfq_quote.
    -- -----------------------------------------------------------------------
    weight_price          NUMERIC(5,2) NOT NULL DEFAULT 40.00,
    weight_quality        NUMERIC(5,2) NOT NULL DEFAULT 25.00,
    weight_delivery       NUMERIC(5,2) NOT NULL DEFAULT 25.00,
    weight_sustainability NUMERIC(5,2) NOT NULL DEFAULT 10.00,
    description           TEXT,
    created_by            VARCHAR(100) NOT NULL,
    created_at            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_rfq_weights_sum CHECK (
        ABS((weight_price + weight_quality + weight_delivery + weight_sustainability) - 100) < 0.01
    ),
    CONSTRAINT chk_rfq_dates CHECK (closing_date >= COALESCE(issue_date, closing_date))
);

COMMENT ON TABLE procurement.rfq IS
    'RFQ/RFP/RFI/ITT header. Evaluation weights must sum to 100 (CHECK constraint). '
    'python/01_procurement/rfq_evaluator.py evaluate_rfq(rfq_id) reads these weights '
    'and computes weighted_total_score for all rfq_quotes, then writes back rank.';

-- ---------------------------------------------------------------------------
-- rfq_quotes
-- One row per supplier per RFQ. Scores written by rfq_evaluator.py.
-- ---------------------------------------------------------------------------
CREATE TABLE procurement.rfq_quotes (
    id                   UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    rfq_id               UUID          NOT NULL REFERENCES procurement.rfq(id) ON DELETE RESTRICT,
    supplier_id          UUID          NOT NULL REFERENCES procurement.suppliers(id) ON DELETE RESTRICT,
    unit_price_cents     INTEGER       NOT NULL CHECK (unit_price_cents >= 0),
    lead_time_days       SMALLINT      NOT NULL CHECK (lead_time_days >= 0),
    minimum_order_qty    NUMERIC(15,4),
    validity_date        DATE          NOT NULL,
    -- -----------------------------------------------------------------------
    -- Individual criterion scores 0-100.
    -- Written back by python/01_procurement/rfq_evaluator.py after scoring.
    -- price_score    : normalised relative to lowest bid
    -- quality_score  : from supplier scorecard PPM / DPMO
    -- delivery_score : OTD rate * 100
    -- sustainability : ESG / carbon score
    -- -----------------------------------------------------------------------
    price_score          NUMERIC(5,2)  CHECK (price_score        BETWEEN 0 AND 100),
    quality_score        NUMERIC(5,2)  CHECK (quality_score      BETWEEN 0 AND 100),
    delivery_score       NUMERIC(5,2)  CHECK (delivery_score     BETWEEN 0 AND 100),
    sustainability_score NUMERIC(5,2)  CHECK (sustainability_score BETWEEN 0 AND 100),
    -- Composite score and rank written back by evaluate_rfq()
    weighted_total_score NUMERIC(5,2)  CHECK (weighted_total_score BETWEEN 0 AND 100),
    rank                 SMALLINT      CHECK (rank > 0),
    disqualified         BOOLEAN       NOT NULL DEFAULT FALSE,
    disqualification_reason TEXT,
    notes                TEXT,
    received_at          TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    UNIQUE (rfq_id, supplier_id)
);

COMMENT ON TABLE procurement.rfq_quotes IS
    'Supplier quotes for an RFQ. price_score / quality_score / delivery_score / '
    'sustainability_score and weighted_total_score are computed and written back by '
    'python/01_procurement/rfq_evaluator.py evaluate_rfq(). '
    'rank is the final position after scoring (1 = best).';

-- ---------------------------------------------------------------------------
-- tco_analysis
-- Total Cost of Ownership per supplier/SKU combination.
-- All cost fields are integer cents. Python computes total_tco_cents and writes back.
-- ---------------------------------------------------------------------------
CREATE TABLE procurement.tco_analysis (
    id                              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    rfq_id                          UUID        REFERENCES procurement.rfq(id),
    supplier_id                     UUID        NOT NULL REFERENCES procurement.suppliers(id) ON DELETE RESTRICT,
    sku_id                          VARCHAR(50) NOT NULL,
    annual_demand                   INTEGER     NOT NULL CHECK (annual_demand > 0),
    unit_price_cents                INTEGER     NOT NULL CHECK (unit_price_cents >= 0),
    -- -----------------------------------------------------------------------
    -- Cost components read by python/01_procurement/tco.py calculate_tco().
    -- TCO = unit_price + transport_per_unit + (ordering_cost * annual_demand/EOQ)
    --       + inspection_cost_rate * unit_price + risk_premium_rate * unit_price
    --       + tooling_cost / annual_demand + ...
    -- -----------------------------------------------------------------------
    ordering_cost_cents             INTEGER     NOT NULL CHECK (ordering_cost_cents >= 0),
    transport_cost_per_unit_cents   INTEGER     NOT NULL CHECK (transport_cost_per_unit_cents >= 0),
    inspection_cost_rate            NUMERIC(6,4) NOT NULL CHECK (inspection_cost_rate >= 0),
    risk_premium_rate               NUMERIC(6,4) NOT NULL CHECK (risk_premium_rate >= 0),
    tooling_amortisation_cents      INTEGER     DEFAULT 0,
    warranty_cost_cents             INTEGER     DEFAULT 0,
    payment_terms_discount_rate     NUMERIC(6,4) DEFAULT 0,
    -- Outputs written back by calculate_tco()
    total_tco_cents                 BIGINT,
    tco_per_unit_cents              INTEGER,
    eoq_units                       INTEGER,    -- EOQ computed alongside TCO
    analysis_date                   DATE        NOT NULL DEFAULT CURRENT_DATE,
    created_at                      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE procurement.tco_analysis IS
    'Total Cost of Ownership analysis per supplier/SKU. '
    'All monetary columns are integer cents. '
    'python/01_procurement/tco.py calculate_tco() reads the cost-component columns '
    'and writes back total_tco_cents, tco_per_unit_cents, eoq_units. '
    'Used by sourcing team to compare suppliers on fully-loaded cost, not unit price alone.';
COMMENT ON COLUMN procurement.tco_analysis.inspection_cost_rate IS
    'Fraction of unit price spent on incoming inspection (AQL sampling). '
    'Typical range: 0.005 (0.5%) to 0.02 (2%).';
COMMENT ON COLUMN procurement.tco_analysis.risk_premium_rate IS
    'Fraction of unit price representing supply risk cost (UFLPA, geopolitical, '
    'quality risk). Derived from Kraljic uflpa_risk_level and scorecard rating.';

-- ---------------------------------------------------------------------------
-- Foreign keys added after both tables exist
-- ---------------------------------------------------------------------------
ALTER TABLE procurement.purchase_orders
    ADD CONSTRAINT fk_po_contract FOREIGN KEY (contract_id)
        REFERENCES procurement.contracts(id) ON DELETE SET NULL;

ALTER TABLE procurement.purchase_orders
    ADD CONSTRAINT fk_po_rfq FOREIGN KEY (rfq_id)
        REFERENCES procurement.rfq(id) ON DELETE SET NULL;

-- ---------------------------------------------------------------------------
-- Indexes
-- ---------------------------------------------------------------------------
CREATE INDEX idx_suppliers_country        ON procurement.suppliers(country_code)    WHERE is_deleted = FALSE;
CREATE INDEX idx_suppliers_kraljic        ON procurement.suppliers(kraljic_quadrant) WHERE is_deleted = FALSE AND status = 'ACTIVE';
CREATE INDEX idx_suppliers_uflpa          ON procurement.suppliers(uflpa_risk_level) WHERE has_xuar_operations = TRUE;
CREATE INDEX idx_suppliers_status         ON procurement.suppliers(status)           WHERE is_deleted = FALSE;

CREATE INDEX idx_po_supplier              ON procurement.purchase_orders(supplier_id);
CREATE INDEX idx_po_status                ON procurement.purchase_orders(status)      WHERE is_deleted = FALSE;
CREATE INDEX idx_po_delivery              ON procurement.purchase_orders(requested_delivery_date);
CREATE INDEX idx_po_contract              ON procurement.purchase_orders(contract_id) WHERE contract_id IS NOT NULL;

CREATE INDEX idx_po_lines_po              ON procurement.po_lines(po_id);
CREATE INDEX idx_po_lines_sku             ON procurement.po_lines(sku_id);

CREATE INDEX idx_contracts_supplier       ON procurement.contracts(supplier_id)       WHERE is_deleted = FALSE;
CREATE INDEX idx_contracts_status         ON procurement.contracts(status, end_date)  WHERE is_deleted = FALSE;

CREATE INDEX idx_rfq_quotes_rfq           ON procurement.rfq_quotes(rfq_id);
CREATE INDEX idx_rfq_quotes_supplier      ON procurement.rfq_quotes(supplier_id);

CREATE INDEX idx_tco_supplier_sku         ON procurement.tco_analysis(supplier_id, sku_id);
CREATE INDEX idx_tco_date                 ON procurement.tco_analysis(analysis_date);

-- ---------------------------------------------------------------------------
-- VIEW: v_kraljic_portfolio
-- Used by kraljic.py and dashboard to display supplier segmentation.
-- ---------------------------------------------------------------------------
CREATE VIEW procurement.v_kraljic_portfolio AS
SELECT
    s.id,
    s.supplier_code,
    s.legal_name,
    s.country_code,
    s.supply_risk_score,
    s.profit_impact_score,
    s.kraljic_quadrant,
    s.ctpat_certified,
    s.iso28000_certified,
    s.aeo_certified,
    s.uflpa_risk_level,
    s.has_xuar_operations,
    s.status,
    -- Spend summary from open POs
    COALESCE(po.open_po_count, 0)          AS open_po_count,
    COALESCE(po.open_po_value_cents, 0)    AS open_po_value_cents
FROM procurement.suppliers s
LEFT JOIN (
    SELECT supplier_id,
           COUNT(*)           AS open_po_count,
           SUM(total_amount_cents) AS open_po_value_cents
    FROM procurement.purchase_orders
    WHERE status NOT IN ('CANCELLED','CLOSED') AND is_deleted = FALSE
    GROUP BY supplier_id
) po ON po.supplier_id = s.id
WHERE s.is_deleted = FALSE AND s.status = 'ACTIVE';

COMMENT ON VIEW procurement.v_kraljic_portfolio IS
    'Active supplier Kraljic segmentation view. Includes open PO spend. '
    'Primary input for kraljic.py visualisation and strategic sourcing decisions.';

-- ---------------------------------------------------------------------------
-- VIEW: v_open_po_summary
-- Working capital exposure by supplier. Fed into cash flow models.
-- ---------------------------------------------------------------------------
CREATE VIEW procurement.v_open_po_summary AS
SELECT
    s.supplier_code,
    s.legal_name,
    s.country_code,
    s.currency,
    po.status,
    COUNT(po.id)                        AS po_count,
    SUM(po.total_amount_cents)          AS total_value_cents,
    MIN(po.requested_delivery_date)     AS earliest_delivery,
    MAX(po.requested_delivery_date)     AS latest_delivery,
    SUM(po.freight_cost_cents)          AS total_freight_cents
FROM procurement.purchase_orders po
JOIN procurement.suppliers s ON po.supplier_id = s.id
WHERE po.is_deleted = FALSE
  AND po.status NOT IN ('CANCELLED', 'CLOSED', 'FULLY_RECEIVED')
GROUP BY s.supplier_code, s.legal_name, s.country_code, s.currency, po.status;

COMMENT ON VIEW procurement.v_open_po_summary IS
    'Open PO working capital exposure per supplier and status. '
    'Used by finance module for accounts-payable forecasting and DPO calculation.';

-- ---------------------------------------------------------------------------
-- VIEW: v_rfq_scoreboard
-- Leaderboard per RFQ showing weighted scores. Used by procurement team
-- to make award decisions and by rfq_evaluator.py to confirm rankings.
-- ---------------------------------------------------------------------------
CREATE VIEW procurement.v_rfq_scoreboard AS
SELECT
    r.rfq_number,
    r.rfq_type,
    r.status          AS rfq_status,
    r.closing_date,
    s.supplier_code,
    s.legal_name,
    q.unit_price_cents,
    q.lead_time_days,
    q.price_score,
    q.quality_score,
    q.delivery_score,
    q.sustainability_score,
    q.weighted_total_score,
    q.rank,
    q.disqualified,
    (s.id = r.awarded_supplier_id) AS is_awarded
FROM procurement.rfq_quotes q
JOIN procurement.rfq r       ON q.rfq_id     = r.id
JOIN procurement.suppliers s ON q.supplier_id = s.id
ORDER BY r.rfq_number, q.rank NULLS LAST;

COMMENT ON VIEW procurement.v_rfq_scoreboard IS
    'Ranked supplier quotes per RFQ. weighted_total_score and rank are populated '
    'by python/01_procurement/rfq_evaluator.py. is_awarded flags the winner.';

-- ---------------------------------------------------------------------------
-- VIEW: v_contracts_expiring_soon
-- Alerts for contracts approaching expiry (within next 90 days).
-- ---------------------------------------------------------------------------
CREATE VIEW procurement.v_contracts_expiring_soon AS
SELECT
    c.contract_number,
    c.contract_type,
    s.supplier_code,
    s.legal_name,
    c.start_date,
    c.end_date,
    c.total_value_cents,
    c.review_date,
    c.auto_renewal,
    (c.end_date - CURRENT_DATE) AS days_until_expiry
FROM procurement.contracts c
JOIN procurement.suppliers s ON c.supplier_id = s.id
WHERE c.is_deleted = FALSE
  AND c.status = 'ACTIVE'
  AND c.end_date BETWEEN CURRENT_DATE AND (CURRENT_DATE + INTERVAL '90 days')
ORDER BY c.end_date;

COMMENT ON VIEW procurement.v_contracts_expiring_soon IS
    'Contracts expiring within 90 days. Triggers renewal workflow in procurement module. '
    'auto_renewal = TRUE contracts are renewed automatically; others require manual action.';

-- ---------------------------------------------------------------------------
-- goods_receipts (GRN / UN/EDIFACT RECADV)
-- Receiving record against a purchase order. The "GR" leg of the 3-way match
-- (PO ↔ GRN ↔ Invoice). Aligns with GoodsReceipt.ts.
-- Soft-delete only (is_deleted) — feeds the 3-way match, a financial control.
-- Status flow: DRAFT → RECEIVED → INSPECTION_PENDING → POSTED → CLOSED
--                                                    ↘ REVERSED
-- Note: finance.goods_receipt_notes is a downstream AP read-model; this table
--       is the system-of-record receiving document owned by procurement.
-- ---------------------------------------------------------------------------
CREATE TABLE procurement.goods_receipts (
    id                  UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    grn_number          VARCHAR(30)  NOT NULL UNIQUE,
    po_id               UUID         NOT NULL REFERENCES procurement.purchase_orders(id) ON DELETE RESTRICT,
    supplier_id         UUID         NOT NULL REFERENCES procurement.suppliers(id) ON DELETE RESTRICT,
    warehouse_id        UUID         NOT NULL,
    status              VARCHAR(20)  NOT NULL DEFAULT 'RECEIVED'
                            CHECK (status IN (
                                'DRAFT', 'RECEIVED', 'INSPECTION_PENDING',
                                'POSTED', 'CLOSED', 'REVERSED'
                            )),
    received_date       DATE         NOT NULL DEFAULT CURRENT_DATE,
    received_by         VARCHAR(100) NOT NULL,
    -- UN/EDIFACT RECADV / shipping references
    carrier_ref         VARCHAR(50),
    packing_slip_ref    VARCHAR(50),
    -- Reversal (POSTED -> REVERSED) requires a reason
    reversal_reason     TEXT,
    -- Record control
    is_deleted          BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    -- Reversed GRNs must carry a reason
    CONSTRAINT chk_grn_reversal CHECK (
        status <> 'REVERSED' OR reversal_reason IS NOT NULL
    )
);

COMMENT ON TABLE procurement.goods_receipts IS
    'Goods Receipt Note (GRN) header — maps to UN/EDIFACT RECADV. '
    'The GR leg of the 3-way match (PO ↔ GRN ↔ Invoice). Soft-delete only. '
    'POSTED transition writes stock movements (inventory module) and feeds '
    'finance 3-way match. Partial receipts allowed: a PO line may be received '
    'across multiple GRNs (see v_open_receipts for remaining quantity).';
COMMENT ON COLUMN procurement.goods_receipts.status IS
    'DRAFT → RECEIVED → INSPECTION_PENDING → POSTED → CLOSED, or REVERSED. '
    'Cannot reach POSTED until every line is inspected (accepted_qty set).';

-- ---------------------------------------------------------------------------
-- goods_receipt_lines
-- Line items within a GRN. over_receipt_pct is a GENERATED column.
-- CHECK enforces accepted_qty + rejected_qty <= received_qty.
-- ---------------------------------------------------------------------------
CREATE TABLE procurement.goods_receipt_lines (
    id                 UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    grn_id             UUID          NOT NULL REFERENCES procurement.goods_receipts(id) ON DELETE RESTRICT,
    po_line_id         UUID          NOT NULL REFERENCES procurement.po_lines(id) ON DELETE RESTRICT,
    sku_id             VARCHAR(50)   NOT NULL,
    ordered_qty        NUMERIC(15,4) NOT NULL CHECK (ordered_qty > 0),
    received_qty       NUMERIC(15,4) NOT NULL CHECK (received_qty > 0),
    -- Inspection outcome (set during INSPECTION_PENDING; NULL = not yet inspected)
    accepted_qty       NUMERIC(15,4) CHECK (accepted_qty >= 0),
    rejected_qty       NUMERIC(15,4) CHECK (rejected_qty >= 0),
    quantity_uom       CHAR(3)       NOT NULL,   -- GS1 UN/ECE Rec 20 UOM code
    -- Lot / batch (required for non-ambient storage or REACH SVHC items)
    lot_number         VARCHAR(50),
    expiry_date        DATE,
    -- Generated: drift-free over-receipt percentage vs ordered qty
    over_receipt_pct   NUMERIC(7,2)  GENERATED ALWAYS AS (
                           ROUND((received_qty - ordered_qty) / ordered_qty * 100, 2)
                       ) STORED,
    -- Over-receipt beyond tolerance (default 5%) flags approval requirement
    requires_approval  BOOLEAN       NOT NULL DEFAULT FALSE,
    unit_price_cents   INTEGER       NOT NULL CHECK (unit_price_cents >= 0),
    created_at         TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    -- accepted + rejected may not exceed received; once inspected they must equal
    -- received_qty (enforced at the application layer in GoodsReceipt.ts).
    CONSTRAINT chk_grn_line_inspection CHECK (
        COALESCE(accepted_qty, 0) + COALESCE(rejected_qty, 0) <= received_qty
    )
);

COMMENT ON TABLE procurement.goods_receipt_lines IS
    'GRN line items. over_receipt_pct is a GENERATED column '
    '((received - ordered)/ordered * 100). unit_price_cents is integer cents. '
    'accepted_qty + rejected_qty <= received_qty (CHECK); when inspected they '
    'equal received_qty. requires_approval flags over-receipt beyond tolerance.';
COMMENT ON COLUMN procurement.goods_receipt_lines.over_receipt_pct IS
    'GENERATED: percentage received above (positive) or below (negative) ordered. '
    'requires_approval = TRUE when over the 5% over-receipt tolerance band.';
COMMENT ON COLUMN procurement.goods_receipt_lines.quantity_uom IS
    'GS1 UN/ECE Rec 20 UOM code. Examples: EA=Each, KGM=Kilogram, LTR=Litre.';

-- ---------------------------------------------------------------------------
-- Indexes
-- ---------------------------------------------------------------------------
CREATE INDEX idx_grn_po                ON procurement.goods_receipts(po_id);
CREATE INDEX idx_grn_supplier          ON procurement.goods_receipts(supplier_id);
CREATE INDEX idx_grn_status            ON procurement.goods_receipts(status)        WHERE is_deleted = FALSE;
CREATE INDEX idx_grn_received_date     ON procurement.goods_receipts(received_date);
CREATE INDEX idx_grn_lines_grn         ON procurement.goods_receipt_lines(grn_id);
CREATE INDEX idx_grn_lines_po_line     ON procurement.goods_receipt_lines(po_line_id);
CREATE INDEX idx_grn_lines_sku         ON procurement.goods_receipt_lines(sku_id);

-- ---------------------------------------------------------------------------
-- VIEW: v_open_receipts
-- GRNs (and PO lines) with remaining quantity still to be received.
-- Partial receipts leave a PO line open until cumulative received >= ordered.
-- ---------------------------------------------------------------------------
CREATE VIEW procurement.v_open_receipts AS
SELECT
    pol.id                              AS po_line_id,
    po.id                               AS po_id,
    po.po_number,
    po.supplier_id,
    pol.sku_id,
    pol.quantity_value                  AS ordered_qty,
    COALESCE(rcv.received_qty, 0)       AS received_qty,
    (pol.quantity_value - COALESCE(rcv.received_qty, 0)) AS remaining_qty,
    pol.quantity_uom
FROM procurement.po_lines pol
JOIN procurement.purchase_orders po ON pol.po_id = po.id
LEFT JOIN (
    SELECT grl.po_line_id,
           SUM(grl.received_qty) AS received_qty
    FROM procurement.goods_receipt_lines grl
    JOIN procurement.goods_receipts grn ON grl.grn_id = grn.id
    WHERE grn.is_deleted = FALSE
      AND grn.status NOT IN ('REVERSED')
    GROUP BY grl.po_line_id
) rcv ON rcv.po_line_id = pol.id
WHERE po.is_deleted = FALSE
  AND po.status NOT IN ('CANCELLED', 'CLOSED')
  AND pol.quantity_value > COALESCE(rcv.received_qty, 0);

COMMENT ON VIEW procurement.v_open_receipts IS
    'PO lines with quantity still outstanding (ordered > cumulative received). '
    'Drives expediting and PARTIALLY_RECEIVED status. REVERSED GRNs are excluded '
    'from received totals so reversed receipts re-open the line.';

-- ---------------------------------------------------------------------------
-- VIEW: v_three_way_match_exceptions
-- GRN lines whose received quantity diverges from the ordered quantity beyond
-- tolerance, or that are flagged for over-receipt approval. Feeds the AP
-- 3-way match (PO ↔ GRN ↔ Invoice) in the finance module and
-- python/01_procurement/receiving.py three_way_match_status().
-- ---------------------------------------------------------------------------
CREATE VIEW procurement.v_three_way_match_exceptions AS
SELECT
    grn.grn_number,
    grn.po_id,
    po.po_number,
    grn.supplier_id,
    s.supplier_code,
    grl.sku_id,
    grl.ordered_qty,
    grl.received_qty,
    grl.accepted_qty,
    grl.rejected_qty,
    grl.over_receipt_pct,
    grl.requires_approval,
    grl.unit_price_cents,
    ROUND((grl.received_qty - grl.ordered_qty) * grl.unit_price_cents)::BIGINT
                                        AS qty_variance_value_cents,
    grn.status                          AS grn_status,
    CASE
        WHEN grl.requires_approval               THEN 'OVER_RECEIPT'
        WHEN grl.received_qty < grl.ordered_qty  THEN 'SHORT_RECEIPT'
        WHEN grl.rejected_qty > 0                THEN 'QUALITY_REJECTION'
        ELSE 'OTHER'
    END                                 AS exception_type
FROM procurement.goods_receipt_lines grl
JOIN procurement.goods_receipts grn ON grl.grn_id = grn.id
JOIN procurement.purchase_orders po ON grn.po_id = po.id
JOIN procurement.suppliers s        ON grn.supplier_id = s.id
WHERE grn.is_deleted = FALSE
  AND grn.status NOT IN ('REVERSED')
  AND (
        grl.requires_approval
     OR grl.received_qty <> grl.ordered_qty
     OR COALESCE(grl.rejected_qty, 0) > 0
      );

COMMENT ON VIEW procurement.v_three_way_match_exceptions IS
    'GRN lines that break the 3-way match: over-receipts requiring approval, '
    'short receipts, or quality rejections. Read by the finance AP module and '
    'python/01_procurement/receiving.py three_way_match_status() to hold payment '
    'until the discrepancy is cleared. qty_variance_value_cents is integer cents.';
