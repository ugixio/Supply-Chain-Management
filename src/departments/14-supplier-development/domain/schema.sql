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
