-- =============================================================================
-- SCHEMA: risk_management
-- Department: 10 – Risk Management
-- Feeds Python: risk_model.py (calculate_risk_level, expected_annual_loss,
--               herfindahl_hirschman_index, bullwhip_ratio, monte_carlo_var,
--               validate_bcp_objectives)
-- Standards: ISO 31000:2018, ISO 22301:2019 (BCP: RTO/RPO/MTPD),
--            SCOR-DS Plan, NIST CSF (cyber risk), HHI (DOJ/FTC thresholds)
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS risk_management;

-- ---------------------------------------------------------------------------
-- TABLES
-- ---------------------------------------------------------------------------

CREATE TABLE risk_management.risk_items (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    risk_number         VARCHAR(50) NOT NULL UNIQUE,
    risk_category       VARCHAR(30) NOT NULL
                            CHECK (risk_category IN (
                                'SUPPLIER_DISRUPTION','DEMAND_VOLATILITY','LOGISTICS_DISRUPTION',
                                'GEOPOLITICAL','NATURAL_DISASTER','CYBER_SECURITY',
                                'REGULATORY_COMPLIANCE','FINANCIAL_CREDIT','QUALITY_FAILURE'
                            )),
    title               TEXT        NOT NULL,
    description         TEXT,
    probability_score   INTEGER     NOT NULL CHECK (probability_score BETWEEN 1 AND 5),
    impact_score        INTEGER     NOT NULL CHECK (impact_score BETWEEN 1 AND 5),
    risk_score          INTEGER     GENERATED ALWAYS AS (probability_score * impact_score) STORED,
    risk_level          VARCHAR(10) GENERATED ALWAYS AS (
                            CASE
                                WHEN probability_score * impact_score >= 20 THEN 'CRITICAL'
                                WHEN probability_score * impact_score >= 15 THEN 'HIGH'
                                WHEN probability_score * impact_score >= 9  THEN 'MEDIUM'
                                ELSE 'LOW'
                            END
                        ) STORED,
    financial_impact_cents BIGINT  CHECK (financial_impact_cents >= 0),
    eal_cents           BIGINT      CHECK (eal_cents >= 0),
    probability_annual  NUMERIC(6,4) CHECK (probability_annual BETWEEN 0 AND 1),
    owner_department    VARCHAR(100),
    owner_name          VARCHAR(200),
    mitigation_status   VARCHAR(25) NOT NULL DEFAULT 'IDENTIFIED'
                            CHECK (mitigation_status IN (
                                'IDENTIFIED','ASSESSED','MITIGATION_IN_PROGRESS',
                                'MITIGATED','ACCEPTED','TRANSFERRED','CLOSED'
                            )),
    review_date         DATE        NOT NULL,
    is_deleted          BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  risk_management.risk_items                     IS 'Risk register entries on the 5x5 risk matrix. risk_score and risk_level auto-computed from probability x impact. Feeds calculate_risk_level() and expected_annual_loss() in risk_model.py.';
COMMENT ON COLUMN risk_management.risk_items.probability_score   IS '1=Rare (<5%), 2=Unlikely (5-20%), 3=Possible (20-50%), 4=Likely (50-80%), 5=Almost Certain (>80%).';
COMMENT ON COLUMN risk_management.risk_items.impact_score        IS '1=Negligible, 2=Minor, 3=Moderate, 4=Major, 5=Catastrophic. Considers financial, reputational, and regulatory dimensions.';
COMMENT ON COLUMN risk_management.risk_items.risk_score          IS 'Auto-computed: probability_score * impact_score. Range 1-25. CRITICAL>=20, HIGH>=15, MEDIUM>=9, LOW<9.';
COMMENT ON COLUMN risk_management.risk_items.eal_cents           IS 'Expected Annual Loss in integer cents = financial_impact_cents * probability_annual. Computed by expected_annual_loss() in risk_model.py and stored here.';
COMMENT ON COLUMN risk_management.risk_items.probability_annual  IS 'Annual probability of occurrence (0.0 to 1.0). Used in Monte Carlo simulation and EAL calculation.';
COMMENT ON COLUMN risk_management.risk_items.mitigation_status   IS 'ISO 31000 risk treatment status. TRANSFERRED=insurance/contract, ACCEPTED=risk appetite decision documented.';


CREATE TABLE risk_management.hhi_snapshots (
    commodity_category  VARCHAR(100) NOT NULL,
    period_date         DATE         NOT NULL,
    supplier_count      INTEGER      NOT NULL CHECK (supplier_count > 0),
    hhi_score           NUMERIC(8,2) NOT NULL CHECK (hhi_score BETWEEN 0 AND 10000),
    risk_level          VARCHAR(15)  NOT NULL
                            CHECK (risk_level IN ('LOW','MODERATE','HIGH')),
    top_suppliers       JSONB        NOT NULL DEFAULT '[]',
    calculated_by       VARCHAR(100),
    created_at          TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    PRIMARY KEY (commodity_category, period_date)
);

COMMENT ON TABLE  risk_management.hhi_snapshots                IS 'Herfindahl-Hirschman Index snapshots by commodity category and period. Computed by herfindahl_hirschman_index() in risk_model.py. Feeds supplier concentration risk reporting.';
COMMENT ON COLUMN risk_management.hhi_snapshots.hhi_score      IS 'HHI = SUM(market_share_pct^2) across suppliers. DOJ/FTC thresholds: <1500=LOW (competitive), 1500-2500=MODERATE (moderately concentrated), >2500=HIGH (highly concentrated).';
COMMENT ON COLUMN risk_management.hhi_snapshots.risk_level     IS 'LOW: HHI<1500, MODERATE: 1500-2500, HIGH: >2500. HIGH indicates dangerous supplier concentration risk.';
COMMENT ON COLUMN risk_management.hhi_snapshots.top_suppliers  IS 'JSONB array of top suppliers by share: [{"supplier_id": UUID, "name": str, "share_pct": float}]. Snapshot for historical analysis.';


CREATE TABLE risk_management.bullwhip_metrics (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    sku_id              VARCHAR(50) NOT NULL,
    period_start        DATE        NOT NULL,
    period_end          DATE        NOT NULL,
    demand_variance     NUMERIC(18,6) NOT NULL CHECK (demand_variance >= 0),
    order_variance      NUMERIC(18,6) NOT NULL CHECK (order_variance >= 0),
    bullwhip_ratio      NUMERIC(10,4) GENERATED ALWAYS AS (
                            order_variance / NULLIF(demand_variance, 0)
                        ) STORED,
    risk_flag           BOOLEAN     GENERATED ALWAYS AS (
                            (order_variance / NULLIF(demand_variance, 0)) > 1.5
                        ) STORED,
    tier                VARCHAR(5)  NOT NULL
                            CHECK (tier IN ('T1','T2','T3')),
    calculated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT bullwhip_period_check CHECK (period_end > period_start),
    UNIQUE (sku_id, tier, period_start, period_end)
);

COMMENT ON TABLE  risk_management.bullwhip_metrics              IS 'Bullwhip effect metrics per SKU per supply chain tier. bullwhip_ratio = Var(orders)/Var(demand). Target approx 1.0. Feeds bullwhip_ratio() in risk_model.py.';
COMMENT ON COLUMN risk_management.bullwhip_metrics.bullwhip_ratio IS 'Auto-computed: order_variance / demand_variance. Bullwhip Ratio >1.5 triggers risk_flag. NULL when demand_variance = 0.';
COMMENT ON COLUMN risk_management.bullwhip_metrics.risk_flag    IS 'Auto-computed TRUE when bullwhip_ratio > 1.5. Indicates demand amplification requiring investigation (excess ordering, long lead times, price fluctuations, shortage gaming).';
COMMENT ON COLUMN risk_management.bullwhip_metrics.tier         IS 'Supply chain tier: T1=direct supplier, T2=tier-2 supplier, T3=tier-3 supplier. Bullwhip typically amplifies at each tier.';


CREATE TABLE risk_management.monte_carlo_results (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id              UUID        NOT NULL DEFAULT gen_random_uuid(),
    run_date            DATE        NOT NULL DEFAULT CURRENT_DATE,
    n_simulations       INTEGER     NOT NULL CHECK (n_simulations >= 1000),
    confidence_level    NUMERIC(4,3) NOT NULL CHECK (confidence_level BETWEEN 0.9 AND 0.9999),
    var_95_cents        BIGINT      NOT NULL CHECK (var_95_cents >= 0),
    var_99_cents        BIGINT      NOT NULL CHECK (var_99_cents >= 0),
    mean_loss_cents     BIGINT      NOT NULL CHECK (mean_loss_cents >= 0),
    std_loss_cents      BIGINT      NOT NULL CHECK (std_loss_cents >= 0),
    risk_ids            UUID[]      NOT NULL DEFAULT '{}',
    model_params        JSONB       NOT NULL DEFAULT '{}',
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  risk_management.monte_carlo_results                IS 'Value-at-Risk results from Monte Carlo simulations. Produced by monte_carlo_var() in risk_model.py. Each run covers a set of risk_items.';
COMMENT ON COLUMN risk_management.monte_carlo_results.n_simulations  IS 'Number of Monte Carlo iterations. Minimum 1,000; recommend 10,000+ for stable VaR estimates.';
COMMENT ON COLUMN risk_management.monte_carlo_results.confidence_level IS 'VaR confidence level (e.g. 0.950 = 95%, 0.990 = 99%). Both 95th and 99th percentile VaR stored.';
COMMENT ON COLUMN risk_management.monte_carlo_results.var_95_cents   IS 'Value-at-Risk at 95% confidence in integer cents. 5% of simulations exceed this loss amount.';
COMMENT ON COLUMN risk_management.monte_carlo_results.var_99_cents   IS 'Value-at-Risk at 99% confidence in integer cents. 1% of simulations exceed this loss amount.';
COMMENT ON COLUMN risk_management.monte_carlo_results.risk_ids       IS 'Array of risk_items.id UUIDs included in this simulation run.';
COMMENT ON COLUMN risk_management.monte_carlo_results.model_params   IS 'JSONB snapshot of model parameters used: correlation matrix, distribution assumptions, seed, etc. Required for audit reproducibility.';


CREATE TABLE risk_management.business_continuity_plans (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_number         VARCHAR(50) NOT NULL UNIQUE,
    title               TEXT        NOT NULL,
    scope               TEXT,
    status              VARCHAR(15) NOT NULL DEFAULT 'DRAFT'
                            CHECK (status IN ('DRAFT','APPROVED','ACTIVE','TESTED','ARCHIVED')),
    trigger_type        VARCHAR(50),
    escalation_level    INTEGER     NOT NULL DEFAULT 1
                            CHECK (escalation_level IN (1,2,3)),
    rto_hours           NUMERIC(10,2) NOT NULL CHECK (rto_hours > 0),
    rpo_hours           NUMERIC(10,2) NOT NULL CHECK (rpo_hours > 0),
    mtpd_hours          NUMERIC(10,2) NOT NULL CHECK (mtpd_hours > 0),
    approved_by         VARCHAR(100),
    approved_at         TIMESTAMPTZ,
    effective_date      DATE,
    review_date         DATE,
    is_deleted          BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT bcp_rto_le_mtpd CHECK (rto_hours <= mtpd_hours),
    CONSTRAINT bcp_rpo_le_rto  CHECK (rpo_hours <= rto_hours)
);

COMMENT ON TABLE  risk_management.business_continuity_plans        IS 'Business Continuity Plans per ISO 22301:2019. RTO/RPO/MTPD objectives validated by validate_bcp_objectives() in risk_model.py.';
COMMENT ON COLUMN risk_management.business_continuity_plans.escalation_level IS '1=Incident (local response), 2=Crisis (senior management), 3=Disaster (executive/board activation).';
COMMENT ON COLUMN risk_management.business_continuity_plans.rto_hours IS 'Recovery Time Objective: maximum acceptable downtime before resuming operations (ISO 22301 para 8.2.3).';
COMMENT ON COLUMN risk_management.business_continuity_plans.rpo_hours IS 'Recovery Point Objective: maximum acceptable data loss measured in time. Must be <= RTO (enforced by constraint).';
COMMENT ON COLUMN risk_management.business_continuity_plans.mtpd_hours IS 'Maximum Tolerable Period of Disruption: time beyond which consequences become unacceptable (ISO 22301 para 3.29). RTO must be <= MTPD (enforced by constraint).';
COMMENT ON COLUMN risk_management.business_continuity_plans.trigger_type IS 'Event class that activates this BCP (e.g. SUPPLIER_BANKRUPTCY, PORT_CLOSURE, RANSOMWARE, NATURAL_DISASTER).';


CREATE TABLE risk_management.bcp_actions (
    id                          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    bcp_id                      UUID        NOT NULL REFERENCES risk_management.business_continuity_plans(id),
    action_number               INTEGER     NOT NULL CHECK (action_number >= 1),
    sequence_number             INTEGER     NOT NULL CHECK (sequence_number >= 1),
    description                 TEXT        NOT NULL,
    owner_role                  VARCHAR(100) NOT NULL,
    timeframe_hours             NUMERIC(8,2) NOT NULL CHECK (timeframe_hours > 0),
    depends_on_action_ids       UUID[]      NOT NULL DEFAULT '{}',
    alternative_supplier_ids    UUID[]      NOT NULL DEFAULT '{}',
    stock_release_instructions  TEXT,
    is_deleted                  BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (bcp_id, action_number)
);

COMMENT ON TABLE  risk_management.bcp_actions                          IS 'Sequential response actions within a Business Continuity Plan. Dependency graph via depends_on_action_ids for parallel/sequential scheduling.';
COMMENT ON COLUMN risk_management.bcp_actions.sequence_number          IS 'Execution order within the BCP. Actions with the same sequence_number may execute in parallel.';
COMMENT ON COLUMN risk_management.bcp_actions.depends_on_action_ids    IS 'Array of bcp_actions.id UUIDs that must complete before this action starts.';
COMMENT ON COLUMN risk_management.bcp_actions.alternative_supplier_ids IS 'Pre-approved alternative supplier UUIDs to activate in supply disruption scenarios.';
COMMENT ON COLUMN risk_management.bcp_actions.stock_release_instructions IS 'Instructions for releasing safety/strategic stock to bridge supply gap during disruption.';


CREATE TABLE risk_management.bcp_tests (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    bcp_id          UUID        NOT NULL REFERENCES risk_management.business_continuity_plans(id),
    test_date       DATE        NOT NULL,
    test_type       VARCHAR(15) NOT NULL
                        CHECK (test_type IN ('TABLETOP','FUNCTIONAL','FULL_SCALE')),
    scenario_tested TEXT        NOT NULL,
    passed          BOOLEAN     NOT NULL,
    gaps_identified TEXT[]      NOT NULL DEFAULT '{}',
    next_test_date  DATE,
    tested_by       VARCHAR(100),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  risk_management.bcp_tests                IS 'BCP test exercise records per ISO 22301:2019 para 8.5. TABLETOP=discussion-based, FUNCTIONAL=limited activation, FULL_SCALE=complete simulation.';
COMMENT ON COLUMN risk_management.bcp_tests.gaps_identified IS 'Array of identified gaps or deficiencies discovered during testing. Each gap should generate a corrective action.';


CREATE TABLE risk_management.disruption_early_warnings (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    risk_category       VARCHAR(30) NOT NULL
                            CHECK (risk_category IN (
                                'SUPPLIER_DISRUPTION','DEMAND_VOLATILITY','LOGISTICS_DISRUPTION',
                                'GEOPOLITICAL','NATURAL_DISASTER','CYBER_SECURITY',
                                'REGULATORY_COMPLIANCE','FINANCIAL_CREDIT','QUALITY_FAILURE'
                            )),
    source              VARCHAR(50) NOT NULL,
    signal_text         TEXT        NOT NULL,
    severity            VARCHAR(10) NOT NULL
                            CHECK (severity IN ('LOW','MEDIUM','HIGH','CRITICAL')),
    affected_suppliers  UUID[]      NOT NULL DEFAULT '{}',
    affected_regions    TEXT[]      NOT NULL DEFAULT '{}',
    detected_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at         TIMESTAMPTZ,
    ml_confidence_score NUMERIC(5,4) CHECK (ml_confidence_score BETWEEN 0 AND 1),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  risk_management.disruption_early_warnings                IS 'ML-generated early warning signals for supply chain disruptions. Confidence score from NLP/news analysis models in risk_model.py.';
COMMENT ON COLUMN risk_management.disruption_early_warnings.source         IS 'Signal source: NEWS_NLP, SUPPLIER_MONITOR, PORT_TRACKER, WEATHER_API, FINANCIAL_FEED, MANUAL.';
COMMENT ON COLUMN risk_management.disruption_early_warnings.ml_confidence_score IS 'ML model confidence (0.0 to 1.0). Signals below 0.6 require human review before escalation.';
COMMENT ON COLUMN risk_management.disruption_early_warnings.affected_regions IS 'ISO 3166-1 alpha-2 country codes or region names affected by the disruption signal.';


-- ---------------------------------------------------------------------------
-- INDEXES
-- ---------------------------------------------------------------------------

CREATE INDEX idx_risk_items_category        ON risk_management.risk_items(risk_category) WHERE is_deleted = FALSE;
CREATE INDEX idx_risk_items_level           ON risk_management.risk_items(risk_level) WHERE is_deleted = FALSE;
CREATE INDEX idx_risk_items_score           ON risk_management.risk_items(risk_score DESC) WHERE is_deleted = FALSE;
CREATE INDEX idx_risk_items_review_date     ON risk_management.risk_items(review_date) WHERE is_deleted = FALSE;
CREATE INDEX idx_risk_items_mitigation      ON risk_management.risk_items(mitigation_status) WHERE is_deleted = FALSE;

CREATE INDEX idx_hhi_snapshots_period       ON risk_management.hhi_snapshots(period_date DESC);
CREATE INDEX idx_hhi_snapshots_risk_level   ON risk_management.hhi_snapshots(risk_level);

CREATE INDEX idx_bullwhip_sku_tier          ON risk_management.bullwhip_metrics(sku_id, tier, period_start DESC);
CREATE INDEX idx_bullwhip_risk_flag         ON risk_management.bullwhip_metrics(risk_flag) WHERE risk_flag = TRUE;
CREATE INDEX idx_bullwhip_ratio             ON risk_management.bullwhip_metrics(bullwhip_ratio DESC NULLS LAST);

CREATE INDEX idx_monte_carlo_run_date       ON risk_management.monte_carlo_results(run_date DESC);
CREATE INDEX idx_monte_carlo_run_id         ON risk_management.monte_carlo_results(run_id);

CREATE INDEX idx_bcp_status                 ON risk_management.business_continuity_plans(status) WHERE is_deleted = FALSE;
CREATE INDEX idx_bcp_review_date            ON risk_management.business_continuity_plans(review_date) WHERE is_deleted = FALSE;
CREATE INDEX idx_bcp_trigger                ON risk_management.business_continuity_plans(trigger_type) WHERE is_deleted = FALSE;
CREATE INDEX idx_bcp_actions_bcp            ON risk_management.bcp_actions(bcp_id, sequence_number);
CREATE INDEX idx_bcp_tests_bcp              ON risk_management.bcp_tests(bcp_id, test_date DESC);

CREATE INDEX idx_early_warnings_severity    ON risk_management.disruption_early_warnings(severity, detected_at DESC);
CREATE INDEX idx_early_warnings_unresolved  ON risk_management.disruption_early_warnings(detected_at DESC) WHERE resolved_at IS NULL;
CREATE INDEX idx_early_warnings_category    ON risk_management.disruption_early_warnings(risk_category, detected_at DESC);


-- ---------------------------------------------------------------------------
-- VIEWS
-- ---------------------------------------------------------------------------

-- Risk heatmap grouped by level with financial exposure
CREATE OR REPLACE VIEW risk_management.v_risk_heatmap AS
SELECT
    risk_level,
    risk_category,
    COUNT(*)                                        AS risk_count,
    SUM(financial_impact_cents)                     AS total_financial_exposure_cents,
    SUM(eal_cents)                                  AS total_eal_cents,
    AVG(probability_annual)                         AS avg_probability,
    MAX(risk_score)                                 AS max_risk_score,
    ARRAY_AGG(risk_number ORDER BY risk_score DESC) AS risk_numbers
FROM risk_management.risk_items
WHERE is_deleted = FALSE
  AND mitigation_status NOT IN ('CLOSED','TRANSFERRED')
GROUP BY risk_level, risk_category
ORDER BY
    CASE risk_level
        WHEN 'CRITICAL' THEN 1
        WHEN 'HIGH'     THEN 2
        WHEN 'MEDIUM'   THEN 3
        ELSE 4
    END,
    total_eal_cents DESC NULLS LAST;

COMMENT ON VIEW risk_management.v_risk_heatmap IS 'Risk heatmap: active risks grouped by level and category with aggregated financial exposure (EAL). CRITICAL and HIGH items with highest EAL require immediate mitigation attention.';


-- HHI concentration alerts (HHI > 2500 = highly concentrated)
CREATE OR REPLACE VIEW risk_management.v_hhi_concentration_alerts AS
SELECT
    h.commodity_category,
    h.period_date,
    h.supplier_count,
    h.hhi_score,
    h.risk_level,
    h.top_suppliers,
    h.calculated_by,
    CASE
        WHEN h.hhi_score >= 2500 THEN 'HIGHLY_CONCENTRATED'
        WHEN h.hhi_score >= 1500 THEN 'MODERATELY_CONCENTRATED'
        ELSE 'COMPETITIVE'
    END                     AS concentration_label
FROM risk_management.hhi_snapshots h
WHERE h.hhi_score >= 2500
  AND h.period_date = (
      SELECT MAX(h2.period_date)
      FROM risk_management.hhi_snapshots h2
      WHERE h2.commodity_category = h.commodity_category
  )
ORDER BY h.hhi_score DESC;

COMMENT ON VIEW risk_management.v_hhi_concentration_alerts IS 'Latest HHI snapshot per commodity category where HHI > 2500 (highly concentrated per DOJ/FTC guidelines). Triggers supplier diversification review.';


-- SKUs with bullwhip ratio exceeding 1.5
CREATE OR REPLACE VIEW risk_management.v_bullwhip_exceeding AS
SELECT
    sku_id,
    tier,
    period_start,
    period_end,
    demand_variance,
    order_variance,
    bullwhip_ratio,
    calculated_at,
    CASE
        WHEN bullwhip_ratio >= 3.0 THEN 'SEVERE'
        WHEN bullwhip_ratio >= 2.0 THEN 'HIGH'
        ELSE 'ELEVATED'
    END                     AS bullwhip_severity
FROM risk_management.bullwhip_metrics
WHERE risk_flag = TRUE
ORDER BY bullwhip_ratio DESC NULLS LAST, calculated_at DESC;

COMMENT ON VIEW risk_management.v_bullwhip_exceeding IS 'SKUs with bullwhip_ratio > 1.5 indicating demand amplification. SEVERE (>=3.0) requires immediate order policy review. Target bullwhip_ratio approx 1.0 (SCOR-DS Plan KPI).';


-- Risk items without an active, tested BCP
CREATE OR REPLACE VIEW risk_management.v_bcp_coverage_gaps AS
SELECT
    ri.id           AS risk_id,
    ri.risk_number,
    ri.risk_category,
    ri.title,
    ri.risk_level,
    ri.risk_score,
    ri.eal_cents,
    ri.mitigation_status,
    ri.review_date
FROM risk_management.risk_items ri
WHERE ri.is_deleted = FALSE
  AND ri.risk_level IN ('CRITICAL','HIGH')
  AND NOT EXISTS (
      SELECT 1
      FROM risk_management.bcp_tests bt
      JOIN risk_management.business_continuity_plans bcp ON bcp.id = bt.bcp_id
      WHERE bcp.status = 'ACTIVE'
        AND bcp.is_deleted = FALSE
        AND bcp.trigger_type = ri.risk_category
        AND bt.passed = TRUE
  )
ORDER BY ri.risk_score DESC, ri.eal_cents DESC NULLS LAST;

COMMENT ON VIEW risk_management.v_bcp_coverage_gaps IS 'CRITICAL and HIGH risk items not covered by a tested, active Business Continuity Plan. These represent unmitigated continuity exposure requiring BCP development or update.';
