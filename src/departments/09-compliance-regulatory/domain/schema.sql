-- =============================================================================
-- SCHEMA: compliance
-- Department: 09 – Compliance & Regulatory
-- Feeds Python: compliance.py (determine_csddd_phase, assess_uflpa_risk,
--               assess_reach_compliance, due_diligence_score)
-- Standards: EU CSDDD 2024/1760 (Art.23 5-yr retention), US UFLPA Pub.L.117-78,
--            EU REACH 1907/2006 (Art.7/31/33), LkSG (Germany 2023),
--            UK Modern Slavery Act 2015 §54, ISO 28000:2022
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS compliance;

-- ---------------------------------------------------------------------------
-- TABLES
-- ---------------------------------------------------------------------------

CREATE TABLE compliance.company_profiles (
    id                          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    legal_name                  VARCHAR(300) NOT NULL,
    employee_count              INTEGER     CHECK (employee_count >= 0),
    annual_turnover_eur         BIGINT      CHECK (annual_turnover_eur >= 0),
    net_eu_turnover_eur         BIGINT      CHECK (net_eu_turnover_eur >= 0),
    is_eu_company               BOOLEAN     NOT NULL DEFAULT FALSE,
    sectors                     TEXT[]      NOT NULL DEFAULT '{}',
    csddd_phase                 VARCHAR(15)
                                    CHECK (csddd_phase IN ('PHASE1','PHASE2','PHASE3','NOT_IN_SCOPE')),
    csddd_phase_determined_at   DATE,
    review_date                 DATE,
    is_deleted                  BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  compliance.company_profiles                   IS 'Entity profiles used to determine CSDDD phase applicability. Feeds determine_csddd_phase() in compliance.py.';
COMMENT ON COLUMN compliance.company_profiles.employee_count    IS 'Full-time equivalent employees globally. CSDDD Phase 1 threshold: >1000 employees (from 2027).';
COMMENT ON COLUMN compliance.company_profiles.annual_turnover_eur IS 'Global annual turnover in EUR cents. CSDDD Phase 1 threshold: >€450M. INTEGER cents, no floats.';
COMMENT ON COLUMN compliance.company_profiles.net_eu_turnover_eur IS 'Net turnover generated in EU in EUR cents. Relevant for non-EU companies entering CSDDD scope.';
COMMENT ON COLUMN compliance.company_profiles.csddd_phase       IS 'Determined applicability phase: PHASE1=from 2027 (large companies), PHASE2=from 2028 (mid-cap), PHASE3=from 2029 (SMEs in scope), NOT_IN_SCOPE.';
COMMENT ON COLUMN compliance.company_profiles.sectors           IS 'Business sectors per NACE classification. High-impact sectors may trigger lower thresholds under CSDDD.';


CREATE TABLE compliance.csddd_due_diligence (
    id                          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    record_number               VARCHAR(50) NOT NULL UNIQUE,
    supplier_id                 UUID,
    assessment_date             DATE        NOT NULL,
    retention_expiry_date       DATE        GENERATED ALWAYS AS
                                    ((assessment_date + INTERVAL '5 years')::DATE) STORED,
    assessor_id                 VARCHAR(100),
    csddd_phase                 VARCHAR(15)
                                    CHECK (csddd_phase IN ('PHASE1','PHASE2','PHASE3','NOT_IN_SCOPE')),
    adverse_impact_types        TEXT[]      NOT NULL DEFAULT '{}',
    has_forced_labour_risk      BOOLEAN     NOT NULL DEFAULT FALSE,
    has_env_impact              BOOLEAN     NOT NULL DEFAULT FALSE,
    has_child_labour_risk       BOOLEAN     NOT NULL DEFAULT FALSE,
    lksg_applicable             BOOLEAN     NOT NULL DEFAULT FALSE,
    lksg_employee_threshold_met BOOLEAN,
    remediation_plan            TEXT,
    grievance_mechanism_active  BOOLEAN     NOT NULL DEFAULT FALSE,
    monitoring_frequency        VARCHAR(20)
                                    CHECK (monitoring_frequency IN ('ANNUAL','SEMI_ANNUAL','QUARTERLY','MONTHLY')),
    due_diligence_score         NUMERIC(5,2) CHECK (due_diligence_score BETWEEN 0 AND 100),
    status                      VARCHAR(20) NOT NULL DEFAULT 'DRAFT'
                                    CHECK (status IN ('DRAFT','ACTIVE','REMEDIATION','CLOSED')),
    is_deleted                  BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  compliance.csddd_due_diligence                      IS 'Supply chain due diligence records per EU CSDDD 2024/1760. Minimum 5-year document retention per Art.23. Feeds due_diligence_score() in compliance.py.';
COMMENT ON COLUMN compliance.csddd_due_diligence.retention_expiry_date IS 'Auto-computed: assessment_date + 5 years. Art.23 CSDDD minimum retention period. Records must not be hard-deleted before this date.';
COMMENT ON COLUMN compliance.csddd_due_diligence.adverse_impact_types  IS 'Array of identified adverse impact categories per Annex I/II CSDDD (e.g. {''FORCED_LABOUR'',''DEFORESTATION'',''WATER_POLLUTION''}).';
COMMENT ON COLUMN compliance.csddd_due_diligence.lksg_applicable       IS 'German Supply Chain Due Diligence Act (LkSG) applicability flag. Required for companies with ≥1,000 employees in Germany from 2023.';
COMMENT ON COLUMN compliance.csddd_due_diligence.grievance_mechanism_active IS 'Art.9 CSDDD: companies must establish or participate in an effective grievance mechanism.';
COMMENT ON COLUMN compliance.csddd_due_diligence.due_diligence_score   IS 'Composite score 0-100 computed by due_diligence_score() in compliance.py. Considers coverage, remediation, and monitoring frequency.';


CREATE TABLE compliance.uflpa_assessments (
    id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    supplier_id             UUID        NOT NULL,
    assessment_date         DATE        NOT NULL,
    assessor_id             VARCHAR(100),
    risk_level              VARCHAR(15) NOT NULL
                                CHECK (risk_level IN ('PROHIBITED','HIGH','MEDIUM','LOW')),
    xuar_regions            TEXT[]      NOT NULL DEFAULT '{}',
    hs_codes                TEXT[]      NOT NULL DEFAULT '{}',
    on_entity_list          BOOLEAN     NOT NULL DEFAULT FALSE,
    clearance_document_ref  VARCHAR(500),
    tier2_xuar_exposure     BOOLEAN     NOT NULL DEFAULT FALSE,
    notes                   TEXT,
    valid_until             DATE,
    is_deleted              BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uflpa_clearance_doc_required CHECK (
        risk_level NOT IN ('PROHIBITED','HIGH') OR clearance_document_ref IS NOT NULL
    )
);

COMMENT ON TABLE  compliance.uflpa_assessments                      IS 'US UFLPA (Pub.L. 117-78) risk assessments. Suppliers with XUAR operations face rebuttable presumption of forced labour. Clearance documentation mandatory for HIGH/PROHIBITED risk.';
COMMENT ON COLUMN compliance.uflpa_assessments.risk_level           IS 'PROHIBITED=on UFLPA entity list, HIGH=significant XUAR exposure, MEDIUM=tier-2 exposure, LOW=no identified XUAR nexus.';
COMMENT ON COLUMN compliance.uflpa_assessments.xuar_regions         IS 'Xinjiang Uyghur Autonomous Region sub-regions with operations (e.g. {''URUMQI'',''KASHGAR''}). Drives risk scoring in assess_uflpa_risk().';
COMMENT ON COLUMN compliance.uflpa_assessments.on_entity_list       IS 'TRUE if supplier appears on UFLPA Entity List maintained by US DHS. Imports are presumptively prohibited.';
COMMENT ON COLUMN compliance.uflpa_assessments.clearance_document_ref IS 'Reference to rebuttal evidence package per UFLPA enforcement guidance. Required when risk_level IN (PROHIBITED, HIGH) per CLAUDE.md business rule 6.';
COMMENT ON COLUMN compliance.uflpa_assessments.tier2_xuar_exposure  IS 'TRUE if sub-tier (tier-2+) suppliers have XUAR operations even where direct supplier does not. Extends risk scope.';


CREATE TABLE compliance.reach_substances (
    id                          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    supplier_id                 UUID,
    sku_id                      VARCHAR(50),
    cas_number                  VARCHAR(15) NOT NULL,
    substance_name              VARCHAR(255) NOT NULL,
    concentration_ww            NUMERIC(10,6) NOT NULL CHECK (concentration_ww > 0),
    quantity_per_year_tonnes    NUMERIC(12,4) CHECK (quantity_per_year_tonnes >= 0),
    is_svhc                     BOOLEAN     NOT NULL DEFAULT FALSE,
    svhc_category               VARCHAR(50)
                                    CHECK (svhc_category IN (
                                        'CMR','PBT','vPvB','ENDOCRINE_DISRUPTOR',
                                        'RESPIRATORY_SENSITISER','OTHER_EQUIVALENT_CONCERN'
                                    ) OR svhc_category IS NULL),
    art7_notification_required  BOOLEAN     NOT NULL DEFAULT FALSE,
    art31_sds_required          BOOLEAN     NOT NULL DEFAULT FALSE,
    art33_notification_required BOOLEAN     NOT NULL DEFAULT FALSE,
    assessment_date             DATE        NOT NULL DEFAULT CURRENT_DATE,
    next_review_date            DATE,
    is_deleted                  BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  compliance.reach_substances                       IS 'EU REACH 1907/2006 substance records per article/mixture. Triggers Art.7/31/33 obligations. Feeds assess_reach_compliance() in compliance.py.';
COMMENT ON COLUMN compliance.reach_substances.cas_number            IS 'CAS Registry Number uniquely identifying the chemical substance (e.g. 7664-93-9 for sulfuric acid).';
COMMENT ON COLUMN compliance.reach_substances.concentration_ww      IS 'Weight/weight concentration as decimal fraction (e.g. 0.0025 = 0.25% w/w). SVHC Art.33 notification threshold: 0.1% w/w (0.001).';
COMMENT ON COLUMN compliance.reach_substances.is_svhc               IS 'Substance of Very High Concern per REACH Annex XIV/XVII or SVHC Candidate List (ECHA). Drives Art.33 notification duty.';
COMMENT ON COLUMN compliance.reach_substances.svhc_category         IS 'CMR=carcinogenic/mutagenic/reprotoxic, PBT=persistent/bioaccumulative/toxic, vPvB=very persistent/very bioaccumulative, ENDOCRINE_DISRUPTOR.';
COMMENT ON COLUMN compliance.reach_substances.art7_notification_required IS 'REACH Art.7: notification to ECHA required if SVHC > 0.1% w/w and >1 tonne/year.';
COMMENT ON COLUMN compliance.reach_substances.art31_sds_required    IS 'REACH Art.31: Safety Data Sheet (SDS) required for hazardous substances and mixtures.';
COMMENT ON COLUMN compliance.reach_substances.art33_notification_required IS 'REACH Art.33: Supplier must notify customer (and ECHA) of SVHC presence >0.1% w/w in articles.';


CREATE TABLE compliance.compliance_documents (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    document_type       VARCHAR(50) NOT NULL,
    supplier_id         UUID,
    reference_id        UUID,
    reference_table     VARCHAR(100),
    document_number     VARCHAR(100),
    issue_date          DATE,
    expiry_date         DATE,
    issuing_authority   VARCHAR(200),
    file_ref            VARCHAR(500),
    is_valid            BOOLEAN     NOT NULL DEFAULT TRUE,
    is_deleted          BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT compliance_doc_expiry_after_issue CHECK (
        expiry_date IS NULL OR issue_date IS NULL OR expiry_date >= issue_date
    )
);

COMMENT ON TABLE  compliance.compliance_documents              IS 'Centralised compliance document registry. Covers certifications, assessments, SDS sheets, clearance documents, and regulatory filings.';
COMMENT ON COLUMN compliance.compliance_documents.reference_id IS 'UUID of the parent record this document belongs to (e.g. uflpa_assessments.id or csddd_due_diligence.id).';
COMMENT ON COLUMN compliance.compliance_documents.reference_table IS 'Table name of the parent record for polymorphic association (e.g. ''compliance.uflpa_assessments'').';
COMMENT ON COLUMN compliance.compliance_documents.is_valid      IS 'FALSE if document has been superseded, revoked, or expired. Updated by scheduled compliance review job.';


CREATE TABLE compliance.regulatory_alerts (
    id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    regulation              VARCHAR(50) NOT NULL,
    alert_type              VARCHAR(50) NOT NULL,
    severity                VARCHAR(10) NOT NULL
                                CHECK (severity IN ('LOW','MEDIUM','HIGH','CRITICAL')),
    message                 TEXT        NOT NULL,
    affected_supplier_id    UUID,
    affected_sku            VARCHAR(50),
    triggered_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at             TIMESTAMPTZ,
    resolved_by             VARCHAR(100),
    resolution_notes        TEXT,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  compliance.regulatory_alerts                IS 'Automated regulatory compliance alerts. Generated by compliance.py when risk thresholds are breached or documents expire.';
COMMENT ON COLUMN compliance.regulatory_alerts.regulation     IS 'Regulation identifier: UFLPA, CSDDD, REACH, LKSG, MODERN_SLAVERY_ACT, ISO28000, etc.';
COMMENT ON COLUMN compliance.regulatory_alerts.alert_type     IS 'Alert classification: ENTITY_LIST_MATCH, SVHC_THRESHOLD_EXCEEDED, DOCUMENT_EXPIRING, RETENTION_BREACH, NEW_ADVERSE_IMPACT, etc.';
COMMENT ON COLUMN compliance.regulatory_alerts.severity       IS 'CRITICAL=immediate regulatory exposure, HIGH=action required within 5 days, MEDIUM=action within 30 days, LOW=informational.';


-- ---------------------------------------------------------------------------
-- INDEXES
-- ---------------------------------------------------------------------------

CREATE INDEX idx_company_profiles_csddd_phase       ON compliance.company_profiles(csddd_phase) WHERE is_deleted = FALSE;

CREATE INDEX idx_csddd_supplier                     ON compliance.csddd_due_diligence(supplier_id) WHERE supplier_id IS NOT NULL;
CREATE INDEX idx_csddd_status                       ON compliance.csddd_due_diligence(status) WHERE is_deleted = FALSE;
CREATE INDEX idx_csddd_retention_expiry             ON compliance.csddd_due_diligence(retention_expiry_date) WHERE is_deleted = FALSE;
CREATE INDEX idx_csddd_assessment_date              ON compliance.csddd_due_diligence(assessment_date DESC);

CREATE INDEX idx_uflpa_supplier                     ON compliance.uflpa_assessments(supplier_id);
CREATE INDEX idx_uflpa_risk_level                   ON compliance.uflpa_assessments(risk_level) WHERE is_deleted = FALSE;
CREATE INDEX idx_uflpa_entity_list                  ON compliance.uflpa_assessments(on_entity_list) WHERE on_entity_list = TRUE AND is_deleted = FALSE;
CREATE INDEX idx_uflpa_valid_until                  ON compliance.uflpa_assessments(valid_until) WHERE is_deleted = FALSE;

CREATE INDEX idx_reach_sku                          ON compliance.reach_substances(sku_id) WHERE sku_id IS NOT NULL;
CREATE INDEX idx_reach_svhc                         ON compliance.reach_substances(is_svhc) WHERE is_svhc = TRUE AND is_deleted = FALSE;
CREATE INDEX idx_reach_cas                          ON compliance.reach_substances(cas_number);
CREATE INDEX idx_reach_art33                        ON compliance.reach_substances(art33_notification_required) WHERE art33_notification_required = TRUE AND is_deleted = FALSE;

CREATE INDEX idx_compliance_docs_supplier           ON compliance.compliance_documents(supplier_id) WHERE supplier_id IS NOT NULL;
CREATE INDEX idx_compliance_docs_expiry             ON compliance.compliance_documents(expiry_date) WHERE is_deleted = FALSE AND is_valid = TRUE;
CREATE INDEX idx_compliance_docs_ref                ON compliance.compliance_documents(reference_id) WHERE reference_id IS NOT NULL;

CREATE INDEX idx_reg_alerts_severity                ON compliance.regulatory_alerts(severity, triggered_at DESC);
CREATE INDEX idx_reg_alerts_supplier                ON compliance.regulatory_alerts(affected_supplier_id) WHERE affected_supplier_id IS NOT NULL;
CREATE INDEX idx_reg_alerts_unresolved              ON compliance.regulatory_alerts(triggered_at DESC) WHERE resolved_at IS NULL;


-- ---------------------------------------------------------------------------
-- VIEWS
-- ---------------------------------------------------------------------------

-- CSDDD compliance status per supplier
CREATE OR REPLACE VIEW compliance.v_csddd_compliance_status AS
SELECT
    cd.id,
    cd.record_number,
    cd.supplier_id,
    cd.assessment_date,
    cd.retention_expiry_date,
    cd.retention_expiry_date - CURRENT_DATE  AS days_to_retention_expiry,
    cd.csddd_phase,
    cd.status,
    cd.due_diligence_score,
    cd.has_forced_labour_risk,
    cd.has_env_impact,
    cd.has_child_labour_risk,
    cd.grievance_mechanism_active,
    cd.monitoring_frequency,
    CASE
        WHEN cd.status = 'CLOSED'                          THEN 'COMPLIANT'
        WHEN cd.status = 'REMEDIATION'                     THEN 'REMEDIATION_IN_PROGRESS'
        WHEN cd.due_diligence_score >= 75                  THEN 'SATISFACTORY'
        WHEN cd.due_diligence_score >= 50                  THEN 'NEEDS_IMPROVEMENT'
        ELSE 'NON_COMPLIANT'
    END                                                     AS compliance_status
FROM compliance.csddd_due_diligence cd
WHERE cd.is_deleted = FALSE
ORDER BY cd.due_diligence_score ASC NULLS FIRST;

COMMENT ON VIEW compliance.v_csddd_compliance_status IS 'CSDDD due diligence status per supplier. Includes days to Art.23 retention expiry. Records must be retained min 5 years even after supplier offboarding.';


-- UFLPA high-risk suppliers
CREATE OR REPLACE VIEW compliance.v_uflpa_high_risk_suppliers AS
SELECT
    ua.id,
    ua.supplier_id,
    ua.assessment_date,
    ua.risk_level,
    ua.xuar_regions,
    ua.hs_codes,
    ua.on_entity_list,
    ua.clearance_document_ref,
    ua.tier2_xuar_exposure,
    ua.valid_until,
    CASE WHEN ua.valid_until < CURRENT_DATE THEN TRUE ELSE FALSE END AS assessment_expired
FROM compliance.uflpa_assessments ua
WHERE ua.risk_level IN ('PROHIBITED','HIGH')
  AND ua.is_deleted = FALSE
ORDER BY ua.risk_level DESC, ua.assessment_date DESC;

COMMENT ON VIEW compliance.v_uflpa_high_risk_suppliers IS 'Suppliers with PROHIBITED or HIGH UFLPA risk level. Imports from PROHIBITED suppliers are rebuttably presumed to violate the UFLPA and require immediate clearance documentation.';


-- REACH SVHC substances requiring regulatory action
CREATE OR REPLACE VIEW compliance.v_reach_svhc_alerts AS
SELECT
    rs.id,
    rs.supplier_id,
    rs.sku_id,
    rs.cas_number,
    rs.substance_name,
    rs.concentration_ww,
    rs.concentration_ww * 100                      AS concentration_pct,
    rs.svhc_category,
    rs.art7_notification_required,
    rs.art31_sds_required,
    rs.art33_notification_required,
    rs.assessment_date,
    rs.next_review_date,
    CASE WHEN rs.next_review_date < CURRENT_DATE THEN TRUE ELSE FALSE END AS review_overdue,
    CASE
        WHEN rs.art7_notification_required AND rs.art33_notification_required THEN 'ART7_AND_ART33'
        WHEN rs.art33_notification_required THEN 'ART33_ONLY'
        WHEN rs.art7_notification_required  THEN 'ART7_ONLY'
        WHEN rs.art31_sds_required          THEN 'ART31_SDS_ONLY'
        ELSE 'MONITORING'
    END                                             AS action_required
FROM compliance.reach_substances rs
WHERE rs.is_svhc = TRUE
  AND rs.is_deleted = FALSE
ORDER BY rs.concentration_ww DESC;

COMMENT ON VIEW compliance.v_reach_svhc_alerts IS 'SVHC substances requiring REACH Art.7/31/33 regulatory action. SVHC threshold for Art.33 notification: >0.1% w/w (concentration_ww > 0.001). Feeds assess_reach_compliance() in compliance.py.';


-- Compliance documents expiring within 90 days
CREATE OR REPLACE VIEW compliance.v_expiring_documents AS
SELECT
    cd.id,
    cd.document_type,
    cd.supplier_id,
    cd.document_number,
    cd.issue_date,
    cd.expiry_date,
    cd.expiry_date - CURRENT_DATE               AS days_until_expiry,
    cd.issuing_authority,
    cd.reference_table,
    cd.reference_id,
    CASE
        WHEN cd.expiry_date < CURRENT_DATE          THEN 'EXPIRED'
        WHEN cd.expiry_date < CURRENT_DATE + 30     THEN 'EXPIRING_30_DAYS'
        WHEN cd.expiry_date < CURRENT_DATE + 60     THEN 'EXPIRING_60_DAYS'
        ELSE 'EXPIRING_90_DAYS'
    END                                             AS expiry_urgency
FROM compliance.compliance_documents cd
WHERE cd.expiry_date <= CURRENT_DATE + INTERVAL '90 days'
  AND cd.is_valid = TRUE
  AND cd.is_deleted = FALSE
ORDER BY cd.expiry_date ASC;

COMMENT ON VIEW compliance.v_expiring_documents IS 'Compliance documents expiring within 90 days. Includes already-expired documents. Drives renewal workflow alerts. Urgency buckets: 30/60/90 days.';
