-- =============================================================================
-- Schema: supplier_mgmt
-- Aligns with: SupplierScorecard.ts
-- Feeds Python models:
--   python/02_supplier_management/scorecard.py
--     -> smooth_score(scores, alpha)          uses scorecard_history.total_score
--     -> calculate_ppm(defect_qty, sample_qty) uses quality_metrics_log.defect_qty
--     -> calculate_dpmo(defects, units, opp)  uses quality_metrics_log.defects_per_unit
--     -> calculate_otd(on_time, total)        uses delivery_metrics_log.on_time_deliveries
--     -> predict_rating(history_df)           uses scorecard_history for ML trend
-- Weighting: 40% Delivery (OTD 35% + OTIF 45% + RFT 20%)
--            30% Quality  (PPM 60% + NCR rate 40%)
--            20% Commercial (Invoice accuracy 70% + PO variance 30%)
--            10% Soft metrics
-- Rating thresholds: PREFERRED>=90 | APPROVED>=75 | CONDITIONAL>=60
--                    PROBATION>=45 | DISQUALIFIED<45
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS supplier_mgmt;

-- ---------------------------------------------------------------------------
-- supplier_scorecards
-- One record per supplier per scoring period (monthly or quarterly).
-- Composite score and rating are computed by scorecard.py and written back.
-- ---------------------------------------------------------------------------
CREATE TABLE supplier_mgmt.supplier_scorecards (
    id                        UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    -- References procurement.suppliers(id) — cross-schema FK (advisory only)
    supplier_id               UUID        NOT NULL,
    supplier_code             VARCHAR(20) NOT NULL,   -- denormalised for query performance
    period_start              DATE        NOT NULL,
    period_end                DATE        NOT NULL,
    period_type               VARCHAR(10) NOT NULL DEFAULT 'MONTHLY'
                                  CHECK (period_type IN ('MONTHLY','QUARTERLY','ANNUAL')),
    -- -----------------------------------------------------------------------
    -- Composite score (0-100) and rating written back by scorecard.py.
    -- Formula:
    --   delivery_score   = OTD*0.35 + OTIF*0.45 + RFT*0.20
    --   quality_score    = PPM_score*0.60 + NCR_rate_score*0.40
    --   commercial_score = invoice_accuracy*0.70 + po_variance_score*0.30
    --   total_score      = delivery_score*0.40 + quality_score*0.30
    --                    + commercial_score*0.20 + soft_score*0.10
    -- -----------------------------------------------------------------------
    delivery_score            NUMERIC(5,2) CHECK (delivery_score    BETWEEN 0 AND 100),
    quality_score             NUMERIC(5,2) CHECK (quality_score     BETWEEN 0 AND 100),
    commercial_score          NUMERIC(5,2) CHECK (commercial_score  BETWEEN 0 AND 100),
    soft_score                NUMERIC(5,2) CHECK (soft_score        BETWEEN 0 AND 100),
    total_score               NUMERIC(5,2) CHECK (total_score       BETWEEN 0 AND 100),
    -- Exponentially smoothed score written by smooth_score() in scorecard.py
    -- smooth_score(scores, alpha=0.3) = EWM of total_score over history
    smoothed_score            NUMERIC(5,2) CHECK (smoothed_score    BETWEEN 0 AND 100),
    rating                    VARCHAR(15)  CHECK (rating IN (
                                  'PREFERRED','APPROVED','CONDITIONAL','PROBATION','DISQUALIFIED'
                              )),
    previous_rating           VARCHAR(15)  CHECK (previous_rating IN (
                                  'PREFERRED','APPROVED','CONDITIONAL','PROBATION','DISQUALIFIED'
                              )),
    rating_changed            BOOLEAN      NOT NULL DEFAULT FALSE,
    -- Flags
    cap_required              BOOLEAN      NOT NULL DEFAULT FALSE,  -- rating < CONDITIONAL
    cap_id                    UUID,                                  -- FK set below
    notes                     TEXT,
    scored_by                 VARCHAR(100),                          -- 'SYSTEM' or user
    scored_at                 TIMESTAMPTZ,
    -- Record control
    is_deleted                BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at                TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at                TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_period_dates CHECK (period_end > period_start),
    UNIQUE (supplier_id, period_start, period_end, period_type)
);

COMMENT ON TABLE supplier_mgmt.supplier_scorecards IS
    'Supplier performance scorecard per period. '
    'total_score and rating are computed by python/02_supplier_management/scorecard.py. '
    'smoothed_score uses smooth_score(scores, alpha=0.3) exponential weighted mean '
    'to reduce noise in volatile periods. '
    'rating < CONDITIONAL triggers cap_required = TRUE and creates a corrective_action_plan.';
COMMENT ON COLUMN supplier_mgmt.supplier_scorecards.total_score IS
    'Composite score 0-100. Weights: Delivery 40%, Quality 30%, Commercial 20%, Soft 10%. '
    'Thresholds: PREFERRED>=90, APPROVED>=75, CONDITIONAL>=60, PROBATION>=45, DISQUALIFIED<45.';
COMMENT ON COLUMN supplier_mgmt.supplier_scorecards.smoothed_score IS
    'EWM-smoothed total_score (alpha=0.3). Written by scorecard.py smooth_score(). '
    'Used as ML feature in predict_rating() LightGBM model to reduce score volatility impact.';

-- ---------------------------------------------------------------------------
-- delivery_metrics_log
-- Raw delivery KPI data per period per supplier.
-- Feeds calculate_otd(), calculate_otif() in scorecard.py.
-- OTD: world-class >= 95%; OTIF Walmart standard = 98%.
-- ---------------------------------------------------------------------------
CREATE TABLE supplier_mgmt.delivery_metrics_log (
    id                     UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    scorecard_id           UUID          NOT NULL REFERENCES supplier_mgmt.supplier_scorecards(id) ON DELETE CASCADE,
    supplier_id            UUID          NOT NULL,
    period_start           DATE          NOT NULL,
    period_end             DATE          NOT NULL,
    -- Raw counts (inputs to calculate_otd / calculate_otif)
    total_deliveries       INTEGER       NOT NULL CHECK (total_deliveries >= 0),
    on_time_deliveries     INTEGER       NOT NULL CHECK (on_time_deliveries >= 0),
    in_full_deliveries     INTEGER       NOT NULL CHECK (in_full_deliveries >= 0),
    on_time_in_full        INTEGER       NOT NULL CHECK (on_time_in_full >= 0),
    right_first_time       INTEGER       NOT NULL CHECK (right_first_time >= 0),
    -- Derived rates (0-1) written back by scorecard.py
    -- calculate_otd(on_time_deliveries, total_deliveries)
    otd_rate               NUMERIC(6,4)  CHECK (otd_rate  BETWEEN 0 AND 1),
    -- calculate_otif(on_time_in_full, total_deliveries)
    otif_rate              NUMERIC(6,4)  CHECK (otif_rate BETWEEN 0 AND 1),
    -- RFT: right first time (no re-work / re-delivery required)
    rft_rate               NUMERIC(6,4)  CHECK (rft_rate  BETWEEN 0 AND 1),
    -- Average lead time variability (feeds safety stock σ_LT)
    avg_lead_time_days     NUMERIC(6,2),
    lead_time_std_days     NUMERIC(6,2),
    created_at             TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_delivery_counts CHECK (
        on_time_deliveries <= total_deliveries
        AND in_full_deliveries <= total_deliveries
        AND on_time_in_full <= total_deliveries
        AND right_first_time <= total_deliveries
    )
);

COMMENT ON TABLE supplier_mgmt.delivery_metrics_log IS
    'Raw delivery counts per supplier per period. '
    'on_time_deliveries / total_deliveries feeds scorecard.py calculate_otd(). '
    'on_time_in_full / total_deliveries feeds calculate_otif(). '
    'avg_lead_time_days and lead_time_std_days are exported to demand-planning '
    'safety_stock_params as lead time inputs for Method 4: ss = z*sqrt(LT*σ_D² + D̄²*σ_LT²).';
COMMENT ON COLUMN supplier_mgmt.delivery_metrics_log.otd_rate IS
    'On-Time Delivery rate. World-class target >= 0.95 (95%). '
    'Computed by calculate_otd(on_time_deliveries, total_deliveries).';
COMMENT ON COLUMN supplier_mgmt.delivery_metrics_log.otif_rate IS
    'On-Time In-Full rate. Walmart standard = 0.98 (98%). '
    'Computed by calculate_otif(on_time_in_full, total_deliveries).';

-- ---------------------------------------------------------------------------
-- quality_metrics_log
-- Raw quality KPI data per period per supplier.
-- Feeds calculate_ppm(), calculate_dpmo() in scorecard.py.
-- Automotive PPM target < 500; food <= 1000 PPM.
-- ---------------------------------------------------------------------------
CREATE TABLE supplier_mgmt.quality_metrics_log (
    id                     UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    scorecard_id           UUID          NOT NULL REFERENCES supplier_mgmt.supplier_scorecards(id) ON DELETE CASCADE,
    supplier_id            UUID          NOT NULL,
    period_start           DATE          NOT NULL,
    period_end             DATE          NOT NULL,
    -- Raw counts for PPM / DPMO
    -- calculate_ppm(defect_qty, sample_qty) = (defect_qty / sample_qty) * 1_000_000
    units_inspected        INTEGER       NOT NULL CHECK (units_inspected >= 0),
    defect_qty             INTEGER       NOT NULL CHECK (defect_qty >= 0),
    -- calculate_dpmo(total_defects, units, opportunities_per_unit)
    --   = (total_defects / (units * opportunities_per_unit)) * 1_000_000
    total_defects          INTEGER       NOT NULL DEFAULT 0,
    opportunities_per_unit INTEGER       NOT NULL DEFAULT 1 CHECK (opportunities_per_unit >= 1),
    -- NCR (Non-Conformance Reports)
    ncr_count              INTEGER       NOT NULL DEFAULT 0 CHECK (ncr_count >= 0),
    ncr_closed_count       INTEGER       NOT NULL DEFAULT 0,
    -- Derived metrics written back by scorecard.py
    ppm                    NUMERIC(10,2) CHECK (ppm >= 0),    -- parts per million
    dpmo                   NUMERIC(10,2) CHECK (dpmo >= 0),   -- defects per million opportunities
    ncr_rate               NUMERIC(8,4)  CHECK (ncr_rate >= 0), -- NCR per 1000 units
    sigma_level            NUMERIC(4,2),                       -- Six Sigma level (1-6)
    -- AQL inspection level used (ISO 2859-1)
    aql_level              VARCHAR(5),    -- e.g. '1.0', '2.5', '4.0'
    aql_sample_size        INTEGER,
    aql_result             VARCHAR(10)    CHECK (aql_result IN ('ACCEPT','REJECT','CONDITIONAL')),
    created_at             TIMESTAMPTZ    NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_quality_counts CHECK (
        defect_qty <= units_inspected
        AND ncr_closed_count <= ncr_count
    )
);

COMMENT ON TABLE supplier_mgmt.quality_metrics_log IS
    'Raw quality counts per supplier per period. '
    'scorecard.py calculate_ppm(defect_qty, units_inspected) computes ppm. '
    'calculate_dpmo(total_defects, units_inspected, opportunities_per_unit) computes dpmo. '
    'sigma_level = NORM.INV(1 - dpmo/1e6) + 1.5 (short-term shift). '
    'AQL columns feed python/08_quality/aql_sampling.py for incoming inspection planning.';
COMMENT ON COLUMN supplier_mgmt.quality_metrics_log.ppm IS
    'Parts Per Million defect rate. Automotive target <500 PPM; food/pharma <=1000 PPM. '
    'Computed by calculate_ppm(defect_qty, units_inspected).';
COMMENT ON COLUMN supplier_mgmt.quality_metrics_log.dpmo IS
    'Defects Per Million Opportunities. 3.4 DPMO = Six Sigma. '
    'Computed by calculate_dpmo(total_defects, units_inspected, opportunities_per_unit).';

-- ---------------------------------------------------------------------------
-- commercial_metrics_log
-- Invoice accuracy and PO variance per period.
-- Feeds commercial_score in scorecard.py.
-- ---------------------------------------------------------------------------
CREATE TABLE supplier_mgmt.commercial_metrics_log (
    id                         UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    scorecard_id               UUID          NOT NULL REFERENCES supplier_mgmt.supplier_scorecards(id) ON DELETE CASCADE,
    supplier_id                UUID          NOT NULL,
    period_start               DATE          NOT NULL,
    period_end                 DATE          NOT NULL,
    -- Invoice accuracy: fraction of invoices with zero discrepancy
    total_invoices             INTEGER       NOT NULL CHECK (total_invoices >= 0),
    accurate_invoices          INTEGER       NOT NULL CHECK (accurate_invoices >= 0),
    -- PO price variance: abs(actual_price - agreed_price) / agreed_price
    total_po_lines             INTEGER       NOT NULL CHECK (total_po_lines >= 0),
    po_lines_with_variance     INTEGER       NOT NULL DEFAULT 0,
    total_variance_amount_cents BIGINT       DEFAULT 0,  -- sum of absolute price variances
    -- Derived (written by scorecard.py)
    invoice_accuracy_rate      NUMERIC(6,4)  CHECK (invoice_accuracy_rate BETWEEN 0 AND 1),
    po_price_variance_rate     NUMERIC(6,4)  CHECK (po_price_variance_rate >= 0),
    -- commercial_score = invoice_accuracy*0.70 + (1-po_variance_rate)*0.30
    commercial_score           NUMERIC(5,2)  CHECK (commercial_score BETWEEN 0 AND 100),
    created_at                 TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_commercial_counts CHECK (
        accurate_invoices <= total_invoices
        AND po_lines_with_variance <= total_po_lines
    )
);

COMMENT ON TABLE supplier_mgmt.commercial_metrics_log IS
    'Commercial performance metrics per supplier per period. '
    'commercial_score = invoice_accuracy_rate*0.70 + (1 - po_price_variance_rate)*0.30. '
    'Read by scorecard.py to compute the 20% commercial weighting in total_score.';

-- ---------------------------------------------------------------------------
-- scorecard_history
-- Append-only historical record of all scorecard scores.
-- Primary ML training dataset for predict_rating() in scorecard.py.
-- Never update, never delete. Immutable time series.
-- ---------------------------------------------------------------------------
CREATE TABLE supplier_mgmt.scorecard_history (
    id               UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    supplier_id      UUID          NOT NULL,
    supplier_code    VARCHAR(20)   NOT NULL,
    scorecard_id     UUID          NOT NULL REFERENCES supplier_mgmt.supplier_scorecards(id),
    period_start     DATE          NOT NULL,
    period_end       DATE          NOT NULL,
    -- All score components for ML feature engineering
    delivery_score   NUMERIC(5,2),
    quality_score    NUMERIC(5,2),
    commercial_score NUMERIC(5,2),
    soft_score       NUMERIC(5,2),
    total_score      NUMERIC(5,2),
    smoothed_score   NUMERIC(5,2),
    rating           VARCHAR(15),
    -- Snapshot of raw KPIs at time of scoring (features for LightGBM predict_rating)
    otd_rate         NUMERIC(6,4),
    otif_rate        NUMERIC(6,4),
    rft_rate         NUMERIC(6,4),
    ppm              NUMERIC(10,2),
    dpmo             NUMERIC(10,2),
    ncr_rate         NUMERIC(8,4),
    invoice_accuracy_rate   NUMERIC(6,4),
    po_price_variance_rate  NUMERIC(6,4),
    -- Contextual features
    total_deliveries INTEGER,
    units_inspected  INTEGER,
    cap_active       BOOLEAN       NOT NULL DEFAULT FALSE,
    recorded_at      TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE supplier_mgmt.scorecard_history IS
    'Immutable time series of all scorecard scores. APPEND-ONLY — no UPDATE or DELETE. '
    'This is the primary training dataset for python/02_supplier_management/scorecard.py '
    'predict_rating() LightGBM model. Features: smoothed_score trend, ppm trend, '
    'otd_rate trend, delivery volatility (std of recent scores). '
    'Target label: next period rating (classification: 5 classes).';

-- ---------------------------------------------------------------------------
-- corrective_action_plans
-- Triggered automatically when supplier rating drops below CONDITIONAL (score < 60).
-- CSDDD Art.23: documentation retained minimum 5 years.
-- ---------------------------------------------------------------------------
CREATE TABLE supplier_mgmt.corrective_action_plans (
    id                    UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    cap_number            VARCHAR(20) NOT NULL UNIQUE,
    scorecard_id          UUID        NOT NULL REFERENCES supplier_mgmt.supplier_scorecards(id),
    supplier_id           UUID        NOT NULL,
    supplier_code         VARCHAR(20) NOT NULL,
    -- Trigger details
    trigger_rating        VARCHAR(15) NOT NULL CHECK (trigger_rating IN ('CONDITIONAL','PROBATION','DISQUALIFIED')),
    trigger_score         NUMERIC(5,2),
    trigger_date          DATE        NOT NULL DEFAULT CURRENT_DATE,
    -- Root cause and action
    root_cause_category   VARCHAR(30) CHECK (root_cause_category IN (
                              'DELIVERY', 'QUALITY', 'COMMERCIAL', 'CAPACITY',
                              'COMPLIANCE', 'COMMUNICATION', 'OTHER'
                          )),
    root_cause_description TEXT,
    corrective_actions    TEXT        NOT NULL,
    target_score          NUMERIC(5,2) CHECK (target_score BETWEEN 0 AND 100),
    -- Timeline
    due_date              DATE        NOT NULL,
    extended_due_date     DATE,
    -- Resolution
    status                VARCHAR(20) NOT NULL DEFAULT 'OPEN'
                              CHECK (status IN ('OPEN','IN_PROGRESS','CLOSED','ESCALATED','OVERDUE')),
    closed_date           DATE,
    closure_verified_by   VARCHAR(100),
    effectiveness_score   NUMERIC(5,2),  -- score at next review after closure
    -- CSDDD Art.23: retain 5 years from trigger_date
    retention_until       DATE GENERATED ALWAYS AS (trigger_date + INTERVAL '5 years') STORED,
    -- Record control
    is_deleted            BOOLEAN     NOT NULL DEFAULT FALSE,
    created_by            VARCHAR(100) NOT NULL,
    created_at            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at            TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- Back-fill FK from scorecards to CAPs
ALTER TABLE supplier_mgmt.supplier_scorecards
    ADD CONSTRAINT fk_scorecard_cap FOREIGN KEY (cap_id)
        REFERENCES supplier_mgmt.corrective_action_plans(id) ON DELETE SET NULL;

COMMENT ON TABLE supplier_mgmt.corrective_action_plans IS
    'Corrective Action Plans triggered when supplier rating < CONDITIONAL (score < 60). '
    'retention_until is auto-computed as trigger_date + 5 years per CSDDD Art.23 '
    'document retention requirement. '
    'status = OVERDUE is set by a scheduled job when due_date < CURRENT_DATE and status = OPEN.';

-- ---------------------------------------------------------------------------
-- Indexes
-- ---------------------------------------------------------------------------
CREATE INDEX idx_scorecards_supplier     ON supplier_mgmt.supplier_scorecards(supplier_id);
CREATE INDEX idx_scorecards_period       ON supplier_mgmt.supplier_scorecards(period_start, period_end);
CREATE INDEX idx_scorecards_rating       ON supplier_mgmt.supplier_scorecards(rating) WHERE is_deleted = FALSE;
CREATE INDEX idx_scorecards_total_score  ON supplier_mgmt.supplier_scorecards(total_score);

CREATE INDEX idx_delivery_log_supplier   ON supplier_mgmt.delivery_metrics_log(supplier_id, period_start);
CREATE INDEX idx_quality_log_supplier    ON supplier_mgmt.quality_metrics_log(supplier_id, period_start);
CREATE INDEX idx_commercial_log_supplier ON supplier_mgmt.commercial_metrics_log(supplier_id, period_start);

CREATE INDEX idx_history_supplier        ON supplier_mgmt.scorecard_history(supplier_id, period_start);
CREATE INDEX idx_history_rating          ON supplier_mgmt.scorecard_history(rating, recorded_at);
CREATE INDEX idx_history_total_score     ON supplier_mgmt.scorecard_history(total_score, period_start);

CREATE INDEX idx_cap_supplier            ON supplier_mgmt.corrective_action_plans(supplier_id);
CREATE INDEX idx_cap_status              ON supplier_mgmt.corrective_action_plans(status) WHERE is_deleted = FALSE;
CREATE INDEX idx_cap_due_date            ON supplier_mgmt.corrective_action_plans(due_date) WHERE status IN ('OPEN','IN_PROGRESS');

-- ---------------------------------------------------------------------------
-- VIEW: v_supplier_scorecard_latest
-- Latest scorecard per supplier. Primary dashboard view.
-- ---------------------------------------------------------------------------
CREATE VIEW supplier_mgmt.v_supplier_scorecard_latest AS
SELECT DISTINCT ON (sc.supplier_id)
    sc.supplier_id,
    sc.supplier_code,
    sc.period_start,
    sc.period_end,
    sc.period_type,
    sc.delivery_score,
    sc.quality_score,
    sc.commercial_score,
    sc.soft_score,
    sc.total_score,
    sc.smoothed_score,
    sc.rating,
    sc.previous_rating,
    sc.rating_changed,
    sc.cap_required,
    -- KPIs from linked logs
    dm.otd_rate,
    dm.otif_rate,
    dm.rft_rate,
    dm.avg_lead_time_days,
    qm.ppm,
    qm.dpmo,
    qm.ncr_rate,
    cm.invoice_accuracy_rate,
    cm.po_price_variance_rate
FROM supplier_mgmt.supplier_scorecards sc
LEFT JOIN supplier_mgmt.delivery_metrics_log  dm ON dm.scorecard_id = sc.id
LEFT JOIN supplier_mgmt.quality_metrics_log   qm ON qm.scorecard_id = sc.id
LEFT JOIN supplier_mgmt.commercial_metrics_log cm ON cm.scorecard_id = sc.id
WHERE sc.is_deleted = FALSE
ORDER BY sc.supplier_id, sc.period_start DESC;

COMMENT ON VIEW supplier_mgmt.v_supplier_scorecard_latest IS
    'Latest scorecard per supplier with all KPI drill-down columns. '
    'Primary source for the supplier management dashboard and Kraljic update trigger.';

-- ---------------------------------------------------------------------------
-- VIEW: v_suppliers_at_risk
-- Suppliers rated PROBATION or DISQUALIFIED — requires immediate escalation.
-- ---------------------------------------------------------------------------
CREATE VIEW supplier_mgmt.v_suppliers_at_risk AS
SELECT
    sc.supplier_id,
    sc.supplier_code,
    sc.period_start,
    sc.period_end,
    sc.total_score,
    sc.smoothed_score,
    sc.rating,
    sc.previous_rating,
    COALESCE(cap.status, 'NO_CAP') AS cap_status,
    cap.cap_number,
    cap.due_date                   AS cap_due_date,
    cap.trigger_date               AS cap_trigger_date,
    -- Trend: score delta vs previous period
    sh_prev.total_score            AS prev_period_score,
    (sc.total_score - sh_prev.total_score) AS score_delta
FROM supplier_mgmt.v_supplier_scorecard_latest sc
LEFT JOIN supplier_mgmt.corrective_action_plans cap
    ON cap.supplier_id = sc.supplier_id
   AND cap.status IN ('OPEN', 'IN_PROGRESS', 'OVERDUE')
   AND cap.is_deleted = FALSE
LEFT JOIN LATERAL (
    SELECT total_score
    FROM supplier_mgmt.scorecard_history
    WHERE supplier_id = sc.supplier_id
    ORDER BY period_start DESC
    LIMIT 1 OFFSET 1          -- second most recent period
) sh_prev ON TRUE
WHERE sc.rating IN ('PROBATION', 'DISQUALIFIED');

COMMENT ON VIEW supplier_mgmt.v_suppliers_at_risk IS
    'Suppliers rated PROBATION or DISQUALIFIED. Includes CAP status and score trend delta. '
    'Used by procurement to trigger dual-source qualification and by risk module '
    'to elevate supply concentration risk score.';

-- ---------------------------------------------------------------------------
-- VIEW: v_scorecard_trend
-- 12-period rolling history per supplier for trend analysis and ML feature prep.
-- Consumed by scorecard.py smooth_score() and predict_rating().
-- ---------------------------------------------------------------------------
CREATE VIEW supplier_mgmt.v_scorecard_trend AS
SELECT
    supplier_id,
    supplier_code,
    period_start,
    total_score,
    smoothed_score,
    rating,
    otd_rate,
    otif_rate,
    ppm,
    dpmo,
    -- Rolling 3-period average for ML feature
    AVG(total_score) OVER (
        PARTITION BY supplier_id
        ORDER BY period_start
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS score_3p_avg,
    -- Score standard deviation over trailing 6 periods (volatility feature)
    STDDEV(total_score) OVER (
        PARTITION BY supplier_id
        ORDER BY period_start
        ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
    ) AS score_6p_std,
    -- Rank within period (for relative benchmarking)
    RANK() OVER (
        PARTITION BY period_start
        ORDER BY total_score DESC
    ) AS rank_in_period,
    ROW_NUMBER() OVER (PARTITION BY supplier_id ORDER BY period_start) AS period_seq
FROM supplier_mgmt.scorecard_history
ORDER BY supplier_id, period_start;

COMMENT ON VIEW supplier_mgmt.v_scorecard_trend IS
    'Rolling scorecard history with derived trend features. '
    'score_3p_avg and score_6p_std are direct ML features for LightGBM predict_rating(). '
    'rank_in_period enables percentile-based benchmarking across the supply base.';


-- ---------------------------------------------------------------------------
-- supplier_onboarding — supplier qualification workflow
-- One record per supplier qualification lifecycle. Aligns with
-- SupplierOnboarding.ts. The qualification checklist lives in the child table
-- supplier_mgmt.onboarding_checklist_items.
-- ---------------------------------------------------------------------------
CREATE TABLE supplier_mgmt.supplier_onboarding (
    id                  UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    -- References procurement.suppliers(id) — cross-schema FK (advisory only)
    supplier_id         UUID         NOT NULL,
    status              VARCHAR(20)  NOT NULL DEFAULT 'INITIATED'
                            CHECK (status IN (
                                'INITIATED','DOCUMENTATION','ASSESSMENT',
                                'APPROVAL_PENDING','APPROVED','REJECTED','ON_HOLD'
                            )),
    qualification_score NUMERIC(5,2) CHECK (qualification_score IS NULL
                                            OR qualification_score BETWEEN 0 AND 100),
    approved_by         VARCHAR(100),
    approved_date       DATE,
    rejection_reason    TEXT,
    hold_reason         TEXT,
    is_deleted          BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    CONSTRAINT onboarding_approved_requires_approver
        CHECK (status <> 'APPROVED' OR (approved_by IS NOT NULL AND qualification_score IS NOT NULL))
);

COMMENT ON TABLE  supplier_mgmt.supplier_onboarding                     IS 'Supplier qualification workflow lifecycle. One record per supplier onboarding. Aligns with SupplierOnboarding.ts. Required checklist items must all be completed before status APPROVAL_PENDING/APPROVED.';
COMMENT ON COLUMN supplier_mgmt.supplier_onboarding.qualification_score IS 'Final qualification score 0-100, set at approval. May be seeded from scorecard.py supplier_risk_score / segment_suppliers outputs.';
COMMENT ON COLUMN supplier_mgmt.supplier_onboarding.status             IS 'Workflow state: INITIATED→DOCUMENTATION→ASSESSMENT→APPROVAL_PENDING→APPROVED/REJECTED. ON_HOLD pauses pending external audit.';


-- ---------------------------------------------------------------------------
-- onboarding_checklist_items — qualification checklist (one row per item)
-- Standard items generated on initiate(): legal, financial, quality,
-- compliance, technical, ESG. Required items gate submission for approval.
-- ---------------------------------------------------------------------------
CREATE TABLE supplier_mgmt.onboarding_checklist_items (
    id              UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    onboarding_id   UUID         NOT NULL REFERENCES supplier_mgmt.supplier_onboarding(id) ON DELETE CASCADE,
    item_code       VARCHAR(50)  NOT NULL,
    category        VARCHAR(15)  NOT NULL
                        CHECK (category IN ('LEGAL','FINANCIAL','QUALITY','COMPLIANCE','TECHNICAL','ESG')),
    description     TEXT         NOT NULL,
    required        BOOLEAN      NOT NULL DEFAULT TRUE,
    completed       BOOLEAN      NOT NULL DEFAULT FALSE,
    completed_date  DATE,
    document_ref    VARCHAR(500),
    verified_by     VARCHAR(100),
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    CONSTRAINT onboarding_item_unique UNIQUE (onboarding_id, item_code),
    CONSTRAINT onboarding_item_completed_requires_evidence
        CHECK (completed = FALSE OR (document_ref IS NOT NULL AND verified_by IS NOT NULL))
);

COMMENT ON TABLE  supplier_mgmt.onboarding_checklist_items             IS 'Qualification checklist items per onboarding. Standard set generated on initiate(): business registration, tax ID, financial statements, ISO 9001, insurance, CSDDD self-assessment, UFLPA declaration, NDA, code of conduct, bank details, sample approval.';
COMMENT ON COLUMN supplier_mgmt.onboarding_checklist_items.required    IS 'TRUE if the item must be completed before submitForApproval(). Required-incomplete items block approval.';
COMMENT ON COLUMN supplier_mgmt.onboarding_checklist_items.document_ref IS 'Reference to the supporting document in the DMS. Mandatory when completed=TRUE (see onboarding_item_completed_requires_evidence).';


CREATE INDEX idx_onboarding_supplier        ON supplier_mgmt.supplier_onboarding(supplier_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_onboarding_status          ON supplier_mgmt.supplier_onboarding(status) WHERE is_deleted = FALSE;
CREATE INDEX idx_onboarding_items_onboarding ON supplier_mgmt.onboarding_checklist_items(onboarding_id);
CREATE INDEX idx_onboarding_items_pending   ON supplier_mgmt.onboarding_checklist_items(onboarding_id) WHERE required = TRUE AND completed = FALSE;


-- Onboarding status with checklist completion progress
CREATE OR REPLACE VIEW supplier_mgmt.v_onboarding_status AS
SELECT
    o.id                                                         AS onboarding_id,
    o.supplier_id,
    o.status,
    o.qualification_score,
    o.approved_by,
    o.approved_date,
    COUNT(i.id)                                                  AS total_items,
    COUNT(i.id) FILTER (WHERE i.completed)                       AS completed_items,
    COUNT(i.id) FILTER (WHERE i.required)                        AS required_items,
    COUNT(i.id) FILTER (WHERE i.required AND NOT i.completed)    AS pending_required_items,
    ROUND(
        CASE WHEN COUNT(i.id) = 0 THEN 100
        ELSE COUNT(i.id) FILTER (WHERE i.completed)::NUMERIC / COUNT(i.id) * 100 END
    , 2)                                                         AS completion_pct,
    CASE
        WHEN COUNT(i.id) FILTER (WHERE i.required AND NOT i.completed) = 0
        THEN TRUE ELSE FALSE
    END                                                          AS ready_for_approval,
    o.created_at,
    o.updated_at
FROM supplier_mgmt.supplier_onboarding o
LEFT JOIN supplier_mgmt.onboarding_checklist_items i ON i.onboarding_id = o.id
WHERE o.is_deleted = FALSE
GROUP BY o.id
ORDER BY o.updated_at DESC;

COMMENT ON VIEW supplier_mgmt.v_onboarding_status IS 'Supplier onboarding lifecycle with checklist completion progress. ready_for_approval=TRUE when all required items are complete (mirrors submitForApproval() gate in SupplierOnboarding.ts).';
