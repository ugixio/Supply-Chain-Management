-- =============================================================================
-- SCHEMA: quality
-- Department: 08 – Quality Management
-- Feeds Python: quality.py (get_aql_sample, lot_disposition, calculate_ppm,
--               calculate_dpmo, process_capability, copq, first_pass_yield)
-- Standards: ISO 9001:2015 (§8.4, §8.5.2, §8.6, §8.7), ISO 2859-1:1999 (AQL),
--            Automotive <500 PPM, Food ≤1000 PPM, GS1 GTIN traceability
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS quality;

-- ---------------------------------------------------------------------------
-- TABLES
-- ---------------------------------------------------------------------------

CREATE TABLE quality.inspection_plans (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    sku_id              VARCHAR(50) NOT NULL,
    supplier_id         UUID,
    inspection_type     VARCHAR(20) NOT NULL
                            CHECK (inspection_type IN ('INCOMING','IN_PROCESS','FINAL','DOCK_AUDIT')),
    aql_level           NUMERIC(4,2) NOT NULL DEFAULT 1.0
                            CHECK (aql_level IN (0.065,0.1,0.15,0.25,0.4,0.65,1.0,1.5,2.5,4.0,6.5)),
    inspection_level    VARCHAR(10) NOT NULL DEFAULT 'NORMAL'
                            CHECK (inspection_level IN ('NORMAL','TIGHTENED','REDUCED')),
    sampling_method     VARCHAR(20) NOT NULL DEFAULT 'AQL_ISO2859'
                            CHECK (sampling_method IN ('AQL_ISO2859','HUNDRED_PCT','SKIP_LOT')),
    critical_dimensions TEXT[]      NOT NULL DEFAULT '{}',
    is_active           BOOLEAN     NOT NULL DEFAULT TRUE,
    effective_date      DATE        NOT NULL DEFAULT CURRENT_DATE,
    expiry_date         DATE,
    created_date        DATE        NOT NULL DEFAULT CURRENT_DATE,
    is_deleted          BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  quality.inspection_plans                IS 'Inspection plans defining AQL levels, sampling method, and critical dimensions per SKU/supplier. Drives get_aql_sample() in quality.py.';
COMMENT ON COLUMN quality.inspection_plans.aql_level      IS 'Acceptable Quality Level per ISO 2859-1 Table 1. Valid AQL levels: 0.065, 0.1, 0.15, 0.25, 0.4, 0.65, 1.0, 1.5, 2.5, 4.0, 6.5.';
COMMENT ON COLUMN quality.inspection_plans.inspection_level IS 'ISO 2859-1 switching rules: NORMAL=default, TIGHTENED=after failures, REDUCED=after consecutive passes.';
COMMENT ON COLUMN quality.inspection_plans.sampling_method IS 'AQL_ISO2859=statistical sampling, HUNDRED_PCT=100% inspection, SKIP_LOT=periodic sampling for proven suppliers.';
COMMENT ON COLUMN quality.inspection_plans.critical_dimensions IS 'Array of dimension names requiring measurement during inspection (e.g. {''thread_pitch'',''outer_diameter''}).';


CREATE TABLE quality.inspection_records (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    record_number       VARCHAR(50) NOT NULL UNIQUE,
    plan_id             UUID        REFERENCES quality.inspection_plans(id),
    lot_id              UUID,
    supplier_id         UUID,
    po_id               UUID,
    sku_id              VARCHAR(50) NOT NULL,
    inspection_date     DATE        NOT NULL DEFAULT CURRENT_DATE,
    inspector_id        VARCHAR(100) NOT NULL,
    lot_size            INTEGER     NOT NULL CHECK (lot_size > 0),
    sample_size         INTEGER     NOT NULL CHECK (sample_size > 0),
    acceptance_number   INTEGER     NOT NULL CHECK (acceptance_number >= 0),
    rejection_number    INTEGER     NOT NULL CHECK (rejection_number > 0),
    defects_found       INTEGER     NOT NULL DEFAULT 0 CHECK (defects_found >= 0),
    disposition         VARCHAR(15) NOT NULL
                            CHECK (disposition IN ('ACCEPT','REJECT','CONDITIONAL','SORT_100PCT')),
    ppm                 NUMERIC(12,4) GENERATED ALWAYS AS (
                            CASE WHEN lot_size > 0
                            THEN (defects_found::NUMERIC / lot_size) * 1000000
                            ELSE NULL END
                        ) STORED,
    dpmo                NUMERIC(12,4),
    notes               TEXT,
    ncr_number          VARCHAR(50),
    is_deleted          BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT sample_le_lot CHECK (sample_size <= lot_size),
    CONSTRAINT reject_gt_accept CHECK (rejection_number > acceptance_number)
);

COMMENT ON TABLE  quality.inspection_records              IS 'Incoming / in-process / final inspection results per lot. PPM auto-computed from defects_found/lot_size. DPMO requires opportunity count from quality.py calculate_dpmo().';
COMMENT ON COLUMN quality.inspection_records.ppm          IS 'Parts Per Million defective = (defects_found / lot_size) * 1,000,000. Auto-computed. Target: automotive <500 PPM, food ≤1000 PPM.';
COMMENT ON COLUMN quality.inspection_records.dpmo         IS 'Defects Per Million Opportunities. Requires number of defect opportunities per unit; computed by calculate_dpmo() in quality.py and stored here.';
COMMENT ON COLUMN quality.inspection_records.disposition  IS 'Lot disposition per ISO 9001:2015 §8.7: ACCEPT=release, REJECT=return to supplier, CONDITIONAL=use as-is with deviation, SORT_100PCT=100% sort and rework.';
COMMENT ON COLUMN quality.inspection_records.ncr_number   IS 'Reference to ncr_records.ncr_number when disposition is REJECT or CONDITIONAL.';


CREATE TABLE quality.defects_found (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    inspection_id       UUID        NOT NULL REFERENCES quality.inspection_records(id),
    defect_code         VARCHAR(20) NOT NULL,
    defect_description  TEXT,
    defect_category     VARCHAR(10) NOT NULL
                            CHECK (defect_category IN ('CRITICAL','MAJOR','MINOR')),
    quantity            INTEGER     NOT NULL CHECK (quantity > 0),
    defect_location     TEXT,
    photo_ref           VARCHAR(500),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  quality.defects_found                  IS 'Individual defect records within an inspection. Supports Pareto analysis by defect_code and defect_category.';
COMMENT ON COLUMN quality.defects_found.defect_category  IS 'CRITICAL=safety/regulatory risk (zero tolerance), MAJOR=functional failure, MINOR=cosmetic/non-functional. Drives AQL switching rules.';
COMMENT ON COLUMN quality.defects_found.photo_ref        IS 'Reference path to photographic evidence in document management system.';


CREATE TABLE quality.ncr_records (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    ncr_number          VARCHAR(50) NOT NULL UNIQUE,
    inspection_id       UUID        REFERENCES quality.inspection_records(id),
    supplier_id         UUID,
    sku_id              VARCHAR(50) NOT NULL,
    status              VARCHAR(25) NOT NULL DEFAULT 'OPEN'
                            CHECK (status IN ('OPEN','UNDER_REVIEW','DISPOSITION_PENDING','CLOSED','ESCALATED')),
    severity            VARCHAR(10) NOT NULL
                            CHECK (severity IN ('CRITICAL','MAJOR','MINOR')),
    root_cause          TEXT,
    corrective_action   TEXT,
    preventive_action   TEXT,
    opened_date         DATE        NOT NULL DEFAULT CURRENT_DATE,
    target_close_date   DATE        NOT NULL,
    closed_date         DATE,
    days_open           INTEGER     GENERATED ALWAYS AS (
                            COALESCE(closed_date, CURRENT_DATE) - opened_date
                        ) STORED,
    is_deleted          BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT ncr_closed_date_check CHECK (closed_date IS NULL OR closed_date >= opened_date)
);

COMMENT ON TABLE  quality.ncr_records              IS 'Non-Conformance Records raised against inspection failures. Tracks 8D/CAPA lifecycle per ISO 9001:2015 §8.7.';
COMMENT ON COLUMN quality.ncr_records.days_open    IS 'Auto-computed: days from opened_date to closed_date (or today if open). Feeds v_ncr_aging view.';
COMMENT ON COLUMN quality.ncr_records.corrective_action IS 'Immediate corrective action taken to address nonconformity (ISO 9001:2015 §10.2.1a).';
COMMENT ON COLUMN quality.ncr_records.preventive_action IS 'Systemic preventive action to eliminate root cause recurrence (ISO 9001:2015 §10.2.1b).';


CREATE TABLE quality.spc_measurements (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    sku_id          VARCHAR(50) NOT NULL,
    dimension_name  VARCHAR(100) NOT NULL,
    uom             VARCHAR(20) NOT NULL,
    usl             NUMERIC(18,6) NOT NULL,
    lsl             NUMERIC(18,6) NOT NULL,
    nominal         NUMERIC(18,6),
    measured_value  NUMERIC(18,6) NOT NULL,
    measurement_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    machine_id      VARCHAR(100),
    operator_id     VARCHAR(100),
    shift           INTEGER     CHECK (shift IN (1,2,3)),
    cp              NUMERIC(8,4),
    cpk             NUMERIC(8,4),
    within_spec     BOOLEAN     GENERATED ALWAYS AS (
                        measured_value BETWEEN lsl AND usl
                    ) STORED,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT usl_gt_lsl CHECK (usl > lsl)
);

COMMENT ON TABLE  quality.spc_measurements              IS 'Statistical Process Control measurement data. Cp/Cpk computed by process_capability() in quality.py and stored here for trend analysis.';
COMMENT ON COLUMN quality.spc_measurements.usl          IS 'Upper Specification Limit per engineering drawing or customer specification.';
COMMENT ON COLUMN quality.spc_measurements.lsl          IS 'Lower Specification Limit per engineering drawing or customer specification.';
COMMENT ON COLUMN quality.spc_measurements.cp           IS 'Process Capability index = (USL-LSL)/(6*sigma). Target: Cp ≥ 1.33. Computed by process_capability() in quality.py.';
COMMENT ON COLUMN quality.spc_measurements.cpk          IS 'Process Capability index adjusted for centering = min((USL-mean),(mean-LSL))/(3*sigma). Target: Cpk ≥ 1.33.';
COMMENT ON COLUMN quality.spc_measurements.within_spec  IS 'Auto-computed: TRUE if lsl <= measured_value <= usl. Used for First Pass Yield calculation.';
COMMENT ON COLUMN quality.spc_measurements.shift        IS '1=morning, 2=afternoon, 3=night. Used for SPC control chart stratification.';


CREATE TABLE quality.quality_kpi_monthly (
    sku_id                  VARCHAR(50)  NOT NULL,
    supplier_id             UUID         NOT NULL,
    period_month            DATE         NOT NULL,
    total_units_inspected   INTEGER      NOT NULL DEFAULT 0 CHECK (total_units_inspected >= 0),
    total_defectives        INTEGER      NOT NULL DEFAULT 0 CHECK (total_defectives >= 0),
    ppm                     NUMERIC(12,4) GENERATED ALWAYS AS (
                                CASE WHEN total_units_inspected > 0
                                THEN (total_defectives::NUMERIC / total_units_inspected) * 1000000
                                ELSE 0 END
                            ) STORED,
    dpmo                    NUMERIC(12,4),
    ncr_count               INTEGER      NOT NULL DEFAULT 0 CHECK (ncr_count >= 0),
    fpy_pct                 NUMERIC(8,4) CHECK (fpy_pct BETWEEN 0 AND 100),
    copq_cents              BIGINT       NOT NULL DEFAULT 0 CHECK (copq_cents >= 0),
    created_at              TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    PRIMARY KEY (sku_id, supplier_id, period_month)
);

COMMENT ON TABLE  quality.quality_kpi_monthly                IS 'Monthly quality KPI rollup per SKU/supplier. Aggregated from inspection_records. PPM auto-computed; DPMO and FPY provided by quality.py.';
COMMENT ON COLUMN quality.quality_kpi_monthly.period_month   IS 'First day of the month (DATE_TRUNC(''month'', ...)). Composite PK ensures one record per SKU/supplier/month.';
COMMENT ON COLUMN quality.quality_kpi_monthly.ppm            IS 'Auto-computed PPM from rollup totals. Cross-check against individual inspection_records.ppm values.';
COMMENT ON COLUMN quality.quality_kpi_monthly.fpy_pct        IS 'First Pass Yield % = units passing inspection on first attempt / total units inspected * 100. Computed by first_pass_yield() in quality.py.';
COMMENT ON COLUMN quality.quality_kpi_monthly.copq_cents     IS 'Cost of Poor Quality in integer cents. Includes appraisal, internal failure, and external failure costs. Computed by copq() in quality.py.';


-- ---------------------------------------------------------------------------
-- INDEXES
-- ---------------------------------------------------------------------------

CREATE INDEX idx_inspection_plans_sku           ON quality.inspection_plans(sku_id);
CREATE INDEX idx_inspection_plans_supplier      ON quality.inspection_plans(supplier_id) WHERE supplier_id IS NOT NULL;
CREATE INDEX idx_inspection_plans_active        ON quality.inspection_plans(is_active) WHERE is_deleted = FALSE;

CREATE INDEX idx_inspection_records_sku         ON quality.inspection_records(sku_id, inspection_date DESC);
CREATE INDEX idx_inspection_records_supplier    ON quality.inspection_records(supplier_id, inspection_date DESC) WHERE supplier_id IS NOT NULL;
CREATE INDEX idx_inspection_records_lot         ON quality.inspection_records(lot_id) WHERE lot_id IS NOT NULL;
CREATE INDEX idx_inspection_records_disposition ON quality.inspection_records(disposition) WHERE is_deleted = FALSE;
CREATE INDEX idx_inspection_records_ppm         ON quality.inspection_records(ppm DESC NULLS LAST) WHERE is_deleted = FALSE;

CREATE INDEX idx_defects_found_inspection       ON quality.defects_found(inspection_id);
CREATE INDEX idx_defects_found_code_cat         ON quality.defects_found(defect_code, defect_category);

CREATE INDEX idx_ncr_status_severity            ON quality.ncr_records(status, severity) WHERE is_deleted = FALSE;
CREATE INDEX idx_ncr_supplier                   ON quality.ncr_records(supplier_id) WHERE supplier_id IS NOT NULL;
CREATE INDEX idx_ncr_days_open                  ON quality.ncr_records(days_open DESC) WHERE status != 'CLOSED' AND is_deleted = FALSE;

CREATE INDEX idx_spc_sku_dimension_date         ON quality.spc_measurements(sku_id, dimension_name, measurement_date DESC);
CREATE INDEX idx_spc_cpk                        ON quality.spc_measurements(cpk ASC NULLS LAST) WHERE cpk IS NOT NULL;
CREATE INDEX idx_spc_out_of_spec                ON quality.spc_measurements(sku_id, measurement_date) WHERE within_spec = FALSE;

CREATE INDEX idx_quality_kpi_supplier_month     ON quality.quality_kpi_monthly(supplier_id, period_month DESC);
CREATE INDEX idx_quality_kpi_ppm                ON quality.quality_kpi_monthly(ppm DESC NULLS LAST);


-- ---------------------------------------------------------------------------
-- VIEWS
-- ---------------------------------------------------------------------------

-- Latest PPM/DPMO/FPY per supplier per SKU
CREATE OR REPLACE VIEW quality.v_quality_dashboard AS
SELECT
    kpi.sku_id,
    kpi.supplier_id,
    kpi.period_month,
    kpi.total_units_inspected,
    kpi.total_defectives,
    kpi.ppm,
    kpi.dpmo,
    kpi.ncr_count,
    kpi.fpy_pct,
    kpi.copq_cents,
    CASE
        WHEN kpi.ppm IS NULL     THEN 'NO_DATA'
        WHEN kpi.ppm < 500       THEN 'AUTOMOTIVE_COMPLIANT'
        WHEN kpi.ppm < 1000      THEN 'FOOD_COMPLIANT'
        WHEN kpi.ppm < 10000     THEN 'WARNING'
        ELSE 'ACTION_REQUIRED'
    END                                                     AS ppm_status
FROM quality.quality_kpi_monthly kpi
WHERE kpi.period_month = (
    SELECT MAX(k2.period_month)
    FROM quality.quality_kpi_monthly k2
    WHERE k2.sku_id = kpi.sku_id AND k2.supplier_id = kpi.supplier_id
)
ORDER BY kpi.ppm DESC NULLS LAST;

COMMENT ON VIEW quality.v_quality_dashboard IS 'Latest-month quality KPIs per SKU/supplier. PPM status benchmarked against automotive (<500 PPM) and food (≤1000 PPM) thresholds.';


-- Latest Cp/Cpk per SKU/dimension with capability status
CREATE OR REPLACE VIEW quality.v_spc_capability AS
SELECT DISTINCT ON (sku_id, dimension_name)
    sku_id,
    dimension_name,
    uom,
    usl,
    lsl,
    nominal,
    cp,
    cpk,
    measurement_date,
    machine_id,
    CASE
        WHEN cpk IS NULL     THEN 'NO_DATA'
        WHEN cpk >= 1.67     THEN 'SIX_SIGMA'
        WHEN cpk >= 1.33     THEN 'CAPABLE'
        WHEN cpk >= 1.0      THEN 'MONITOR'
        ELSE 'ACTION_REQUIRED'
    END                      AS capability_status
FROM quality.spc_measurements
WHERE cpk IS NOT NULL
ORDER BY sku_id, dimension_name, measurement_date DESC;

COMMENT ON VIEW quality.v_spc_capability IS 'Latest Cp/Cpk per SKU/dimension. capability_status: CAPABLE=Cpk≥1.33 (ISO standard), MONITOR=Cpk 1.0-1.33, ACTION_REQUIRED=Cpk<1.0.';


-- Open NCRs bucketed by age
CREATE OR REPLACE VIEW quality.v_ncr_aging AS
SELECT
    ncr_number,
    supplier_id,
    sku_id,
    severity,
    status,
    opened_date,
    target_close_date,
    days_open,
    CASE
        WHEN days_open <= 7   THEN '0-7_DAYS'
        WHEN days_open <= 14  THEN '8-14_DAYS'
        WHEN days_open <= 30  THEN '15-30_DAYS'
        WHEN days_open <= 60  THEN '31-60_DAYS'
        ELSE 'OVER_60_DAYS'
    END                       AS aging_bucket,
    CASE WHEN target_close_date < CURRENT_DATE THEN TRUE ELSE FALSE END AS is_overdue
FROM quality.ncr_records
WHERE status NOT IN ('CLOSED')
  AND is_deleted = FALSE
ORDER BY days_open DESC;

COMMENT ON VIEW quality.v_ncr_aging IS 'Open NCRs by aging bucket. CRITICAL severity NCRs over 7 days should trigger supplier escalation. Feeds supplier scorecard NCR rate KPI.';
