-- =============================================================================
-- SUPPLIER DEVELOPMENT SCHEMA (ESG, Scope 3, LTIFR, Deforestation)
-- Ref: GHG Protocol (2011) Scope 3 Standard; GRI Standards (2021)
--      ISO 45001:2018; EU CSDDD 2024/1760
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS supplier_development;

-- Supplier sustainability records (annual ESG)
CREATE TABLE supplier_development.sustainability_records (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    supplier_id         UUID NOT NULL REFERENCES procurement.suppliers(id),
    reporting_year      INTEGER NOT NULL CHECK (reporting_year BETWEEN 2000 AND 2100),
    -- Environmental (40% of ESG score)
    env_score           NUMERIC(5,2) CHECK (env_score BETWEEN 0 AND 100),
    ghg_reduction_pct   NUMERIC(6,2),
    renewable_energy_pct NUMERIC(5,2),
    water_intensity     NUMERIC(12,4),    -- m³/revenue unit
    waste_diverted_pct  NUMERIC(5,2),
    -- Social (40%)
    social_score        NUMERIC(5,2) CHECK (social_score BETWEEN 0 AND 100),
    ltifr               NUMERIC(10,4),   -- Lost Time Injury Frequency Rate
    living_wage_compliant BOOLEAN,
    gender_pay_gap_pct  NUMERIC(5,2),
    community_investment_cents BIGINT DEFAULT 0,
    -- Governance (20%)
    governance_score    NUMERIC(5,2) CHECK (governance_score BETWEEN 0 AND 100),
    anti_corruption_certified BOOLEAN DEFAULT FALSE,
    supplier_code_of_conduct  BOOLEAN DEFAULT FALSE,
    esg_reporting_standard VARCHAR(30), -- GRI, SASB, CDP, TCFD
    -- Composite ESG score: E(40%) + S(40%) + G(20%)
    esg_score           NUMERIC(5,2) GENERATED ALWAYS AS (
        ROUND(COALESCE(env_score,0)*0.4 + COALESCE(social_score,0)*0.4 + COALESCE(governance_score,0)*0.2, 2)
    ) STORED,
    esg_rating          VARCHAR(10) GENERATED ALWAYS AS (
        CASE WHEN COALESCE(env_score,0)*0.4 + COALESCE(social_score,0)*0.4 + COALESCE(governance_score,0)*0.2 >= 80 THEN 'LEADER'
             WHEN COALESCE(env_score,0)*0.4 + COALESCE(social_score,0)*0.4 + COALESCE(governance_score,0)*0.2 >= 60 THEN 'ADVANCED'
             WHEN COALESCE(env_score,0)*0.4 + COALESCE(social_score,0)*0.4 + COALESCE(governance_score,0)*0.2 >= 40 THEN 'PROGRESSING'
             ELSE 'LAGGING' END
    ) STORED,
    is_deleted          BOOLEAN NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (supplier_id, reporting_year)
);
COMMENT ON COLUMN supplier_development.sustainability_records.ltifr IS 'LTIFR = (LTIs × 1,000,000) / hours worked. ISO 45001';
COMMENT ON COLUMN supplier_development.sustainability_records.esg_score IS 'E(40%) + S(40%) + G(20%). Ref: GRI Standards (2021)';

-- Scope 3 emissions detail (Category 1: Purchased goods & services)
CREATE TABLE supplier_development.scope3_emissions_detail (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    supplier_id         UUID NOT NULL REFERENCES procurement.suppliers(id),
    sku_id              UUID REFERENCES inventory.sku_master(id),
    reporting_year      INTEGER NOT NULL,
    category            INTEGER NOT NULL CHECK (category BETWEEN 1 AND 15),  -- GHG Protocol Cat 1-15
    category_name       VARCHAR(100),
    spend_cents         BIGINT,
    spend_based_ef      NUMERIC(18,6),   -- kgCO2e per $ spend
    physical_qty        NUMERIC(18,4),
    physical_ef         NUMERIC(18,6),   -- kgCO2e per unit
    emissions_tco2e     NUMERIC(18,4) NOT NULL,
    methodology         VARCHAR(20) CHECK (methodology IN ('SPEND_BASED','SUPPLIER_SPECIFIC','AVERAGE_DATA','HYBRID')),
    data_quality        INTEGER CHECK (data_quality BETWEEN 1 AND 5),   -- 1=primary supplier data, 5=estimate
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON COLUMN supplier_development.scope3_emissions_detail.category IS 'GHG Protocol Scope 3 categories 1-15';

-- Living wage benchmarks
CREATE TABLE supplier_development.living_wage_benchmarks (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    country_code    CHAR(2) NOT NULL,
    region          VARCHAR(100),
    reference_year  INTEGER NOT NULL,
    living_wage_monthly_cents BIGINT NOT NULL,
    minimum_wage_monthly_cents BIGINT,
    gap_cents       BIGINT GENERATED ALWAYS AS (
        GREATEST(living_wage_monthly_cents - COALESCE(minimum_wage_monthly_cents, 0), 0)
    ) STORED,
    source          VARCHAR(100),    -- Anker Methodology, MIT Living Wage Calculator
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (country_code, region, reference_year)
);

-- ESG development programs for suppliers
CREATE TABLE supplier_development.esg_development_programs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    supplier_id     UUID NOT NULL REFERENCES procurement.suppliers(id),
    program_name    VARCHAR(300) NOT NULL,
    focus_area      VARCHAR(30) NOT NULL CHECK (focus_area IN ('CARBON','WATER','WASTE','SOCIAL','GOVERNANCE','SAFETY','BIODIVERSITY')),
    start_date      DATE NOT NULL,
    end_date        DATE,
    target_metric   VARCHAR(200),
    baseline_value  NUMERIC(18,4),
    target_value    NUMERIC(18,4),
    current_value   NUMERIC(18,4),
    status          VARCHAR(20) NOT NULL DEFAULT 'PLANNED' CHECK (status IN ('PLANNED','ACTIVE','COMPLETED','CANCELLED')),
    is_deleted      BOOLEAN NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Deforestation risk log (EUDR compliance)
CREATE TABLE supplier_development.deforestation_risk_log (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    supplier_id     UUID NOT NULL REFERENCES procurement.suppliers(id),
    sku_id          UUID REFERENCES inventory.sku_master(id),
    commodity       VARCHAR(50) CHECK (commodity IN ('SOYA','CATTLE','PALM_OIL','WOOD','COCOA','COFFEE','RUBBER','MAIZE')),
    country_code    CHAR(2) NOT NULL,
    geolocation     TEXT,      -- WKT polygon or GeoJSON
    assessment_date DATE NOT NULL,
    risk_level      VARCHAR(20) CHECK (risk_level IN ('LOW','MEDIUM','HIGH','VERY_HIGH')),
    eudr_compliant  BOOLEAN,
    satellite_verified BOOLEAN DEFAULT FALSE,
    document_ref    VARCHAR(200),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE supplier_development.deforestation_risk_log IS 'EU Deforestation Regulation (EUDR) 2023/1115 due diligence records';

-- =============================================================================
-- EU DEFORESTATION REGULATION (EUDR) 2023/1115 — DUE DILIGENCE ASSESSMENTS
-- Ref: EU Reg. 2023/1115 Art. 3, 8, 10(5) and Annex I
--      EUDR cutoff: production must not cause deforestation after 2020-12-31
-- =============================================================================

CREATE TABLE supplier_development.eudr_assessments (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    supplier_id             UUID NOT NULL REFERENCES procurement.suppliers(id),
    commodity               VARCHAR(20) NOT NULL CHECK (commodity IN (
        'CATTLE','COCOA','COFFEE','PALM_OIL','SOYA','WOOD','RUBBER','MAIZE'
    )),
    country_of_origin       CHAR(2) NOT NULL,               -- ISO 3166-1 alpha-2
    geolocation             TEXT,                            -- WKT polygon or coordinates
    assessment_date         DATE NOT NULL,
    status                  VARCHAR(25) NOT NULL DEFAULT 'NOT_STARTED' CHECK (status IN (
        'NOT_STARTED','IN_PROGRESS','COMPLIANT','NON_COMPLIANT','PENDING_VERIFICATION'
    )),
    risk_level              VARCHAR(15) NOT NULL DEFAULT 'LOW' CHECK (risk_level IN (
        'NEGLIGIBLE','LOW','MEDIUM','HIGH'
    )),
    -- EUDR Art. 2(1): production must not have deforested land after 2020-12-31
    production_start_date   DATE,
    CONSTRAINT eudr_cutoff_check
        CHECK (production_start_date IS NULL OR production_start_date > '2020-12-31'),
    satellite_verified      BOOLEAN NOT NULL DEFAULT FALSE,
    document_ref            VARCHAR(300),
    -- EUDR Art. 10(5): document retention 5 years from assessment date — stored column
    retention_until         DATE GENERATED ALWAYS AS (assessment_date + INTERVAL '5 years') STORED,
    is_deleted              BOOLEAN NOT NULL DEFAULT FALSE,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX ON supplier_development.eudr_assessments (supplier_id, assessment_date DESC);
CREATE INDEX ON supplier_development.eudr_assessments (commodity, country_of_origin, status);
COMMENT ON TABLE supplier_development.eudr_assessments IS
    'EUDR 2023/1115 due diligence assessments. Cutoff: production_start_date > 2020-12-31. '
    'Retention: assessment_date + 5 years (Art. 10(5)).';
COMMENT ON COLUMN supplier_development.eudr_assessments.production_start_date IS
    'Land production start date. Must be after 2020-12-31 (EUDR Art. 2(1) cutoff). '
    'NULL = unknown — triggers PENDING_VERIFICATION status.';
COMMENT ON COLUMN supplier_development.eudr_assessments.retention_until IS
    'Minimum document retention: assessmentDate + 5 years per EUDR Art. 10(5).';

-- =============================================================================
-- TIER 2 ESG CASCADE
-- Ref: EU CSDDD 2024/1760 Art. 7-9 (indirect business relationships)
--      GHG Protocol Scope 3 Standard Cat. 1 (2011); SBTi Corporate Manual v2.0
-- =============================================================================

CREATE TABLE supplier_development.tier2_esg_cascade (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tier1_supplier_id       UUID NOT NULL REFERENCES procurement.suppliers(id),
    -- Tier 2 may be initially unknown (discovered via Tier 1)
    tier2_supplier_id       UUID REFERENCES procurement.suppliers(id),
    tier2_supplier_name     VARCHAR(300) NOT NULL,
    tier2_country           CHAR(2) NOT NULL,               -- ISO 3166-1 alpha-2
    commodity               VARCHAR(100),
    spend_cents             BIGINT CHECK (spend_cents IS NULL OR spend_cents >= 0),
    status                  VARCHAR(20) NOT NULL DEFAULT 'PENDING' CHECK (status IN (
        'PENDING','SENT','ACKNOWLEDGED','DATA_RECEIVED','ASSESSED','ESCALATED'
    )),
    -- Timeline
    requested_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    acknowledged_at         TIMESTAMPTZ,
    data_received_at        TIMESTAMPTZ,
    -- ESG data received from Tier 2
    esg_score               NUMERIC(5,2) CHECK (esg_score IS NULL OR esg_score BETWEEN 0 AND 100),
    risk_level              VARCHAR(10) CHECK (risk_level IN ('LOW','MEDIUM','HIGH','CRITICAL')),
    scope3_emissions_tco2e  NUMERIC(18,4) CHECK (scope3_emissions_tco2e IS NULL OR scope3_emissions_tco2e >= 0),
    -- CSDDD Art. 8 — mandatory action plan for HIGH/CRITICAL risk
    action_required         TEXT,
    is_deleted              BOOLEAN NOT NULL DEFAULT FALSE,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT t2_esg_high_risk_requires_action
        CHECK (
            risk_level NOT IN ('HIGH','CRITICAL')
            OR action_required IS NOT NULL
        )
);
CREATE INDEX ON supplier_development.tier2_esg_cascade (tier1_supplier_id, status);
CREATE INDEX ON supplier_development.tier2_esg_cascade (tier2_country, risk_level);
COMMENT ON TABLE supplier_development.tier2_esg_cascade IS
    'Tracks ESG data requests cascaded from Tier 1 to Tier 2 suppliers. '
    'Ref: EU CSDDD Art. 7-9; GHG Protocol Scope 3 Cat. 1.';
COMMENT ON COLUMN supplier_development.tier2_esg_cascade.action_required IS
    'Mandatory under EU CSDDD Art. 8 when risk_level is HIGH or CRITICAL.';

-- View: EUDR compliance status — by commodity, country, compliance rate, pending count
CREATE OR REPLACE VIEW supplier_development.v_eudr_compliance_status AS
SELECT
    ea.commodity,
    ea.country_of_origin,
    COUNT(*)                                                                AS total_assessments,
    COUNT(*) FILTER (WHERE ea.status = 'COMPLIANT')                         AS compliant_count,
    COUNT(*) FILTER (WHERE ea.status = 'NON_COMPLIANT')                     AS non_compliant_count,
    COUNT(*) FILTER (WHERE ea.status IN ('NOT_STARTED','IN_PROGRESS','PENDING_VERIFICATION'))
                                                                            AS pending_count,
    ROUND(
        COUNT(*) FILTER (WHERE ea.status = 'COMPLIANT')::NUMERIC
        / NULLIF(COUNT(*), 0) * 100, 2
    )                                                                       AS compliance_rate_pct,
    COUNT(*) FILTER (WHERE ea.risk_level = 'HIGH')                          AS high_risk_count,
    COUNT(*) FILTER (WHERE ea.satellite_verified = TRUE)                    AS satellite_verified_count
FROM supplier_development.eudr_assessments ea
WHERE ea.is_deleted = FALSE
GROUP BY ea.commodity, ea.country_of_origin;

-- View: Tier 2 ESG coverage — % of Tier 2 spend with ESG data, gaps by Tier 1 supplier
CREATE OR REPLACE VIEW supplier_development.v_tier2_esg_coverage AS
SELECT
    t2.tier1_supplier_id,
    COUNT(*)                                                                AS total_tier2_relationships,
    COUNT(*) FILTER (WHERE t2.status = 'DATA_RECEIVED' OR t2.status = 'ASSESSED' OR t2.status = 'ESCALATED')
                                                                            AS with_esg_data,
    COUNT(*) FILTER (WHERE t2.status IN ('PENDING','SENT','ACKNOWLEDGED'))  AS pending_data,
    SUM(t2.spend_cents)                                                     AS total_spend_cents,
    SUM(t2.spend_cents) FILTER (
        WHERE t2.status IN ('DATA_RECEIVED','ASSESSED','ESCALATED')
    )                                                                       AS spend_with_esg_cents,
    ROUND(
        SUM(t2.spend_cents) FILTER (
            WHERE t2.status IN ('DATA_RECEIVED','ASSESSED','ESCALATED')
        )::NUMERIC
        / NULLIF(SUM(t2.spend_cents), 0) * 100, 2
    )                                                                       AS esg_spend_coverage_pct,
    AVG(t2.esg_score) FILTER (WHERE t2.esg_score IS NOT NULL)              AS avg_tier2_esg_score,
    COUNT(*) FILTER (WHERE t2.risk_level IN ('HIGH','CRITICAL'))            AS high_critical_risk_count,
    COUNT(*) FILTER (
        WHERE t2.risk_level IN ('HIGH','CRITICAL') AND t2.action_required IS NULL
    )                                                                       AS missing_action_plans
FROM supplier_development.tier2_esg_cascade t2
WHERE t2.is_deleted = FALSE
GROUP BY t2.tier1_supplier_id;

-- KPI view
CREATE OR REPLACE VIEW supplier_development.esg_kpis AS
SELECT
    s.supplier_id,
    s.reporting_year,
    s.esg_score,
    s.esg_rating,
    s.env_score,
    s.social_score,
    s.governance_score,
    s.ltifr,
    s.ghg_reduction_pct,
    SUM(e.emissions_tco2e) AS total_scope3_tco2e
FROM supplier_development.sustainability_records s
LEFT JOIN supplier_development.scope3_emissions_detail e
    ON e.supplier_id = s.supplier_id AND e.reporting_year = s.reporting_year
GROUP BY s.supplier_id, s.reporting_year, s.esg_score, s.esg_rating,
         s.env_score, s.social_score, s.governance_score, s.ltifr, s.ghg_reduction_pct;
