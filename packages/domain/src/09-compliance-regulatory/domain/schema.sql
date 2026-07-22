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


-- =============================================================================
-- EXTENSION: Evidence Management, Grievance Mechanism, Exception Workflow
-- Added to support:
--   ComplianceEvidence.ts — regulatory document storage (CSDDD Art.23 5-yr retention)
--   GrievanceMechanism.ts — CSDDD Art.9 / LkSG §8 grievance tracking
--   ComplianceException.ts — exception approval workflow
-- =============================================================================

-- ---------------------------------------------------------------------------
-- EVIDENCE RECORDS
-- ---------------------------------------------------------------------------

CREATE TABLE compliance.evidence_records (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    supplier_id         UUID        NOT NULL,
    regulation_ref      VARCHAR(20) NOT NULL
                            CHECK (regulation_ref IN (
                                'CSDDD','UFLPA','REACH','LKSG','EUDR','UK_MSA','C_TPAT','ISO_28000'
                            )),
    evidence_type       VARCHAR(30) NOT NULL
                            CHECK (evidence_type IN (
                                'AUDIT_REPORT','SUPPLIER_DECLARATION','CERTIFICATE','CONTRACT',
                                'PHOTO','TEST_RESULT','THIRD_PARTY_ASSESSMENT',
                                'GRIEVANCE_RESPONSE','CORRECTIVE_ACTION','OTHER'
                            )),
    title               VARCHAR(300) NOT NULL,
    document_ref        VARCHAR(1000) NOT NULL,
    mime_type           VARCHAR(100),
    assessment_date     DATE        NOT NULL,
    -- Retention deadline computed per regulation:
    --   CSDDD/LKSG/EUDR: +5 years | UK_MSA: +3 years | others: +2 years
    -- Stored (not generated) to allow regulation-specific logic via application layer.
    retention_until     DATE        NOT NULL,
    uploaded_by         VARCHAR(100) NOT NULL,
    verified_by         VARCHAR(100),
    verified_at         TIMESTAMPTZ,
    is_deleted          BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT evidence_retention_minimum CHECK (
        retention_until >= assessment_date + INTERVAL '2 years'
    ),
    CONSTRAINT evidence_verified_requires_verifier CHECK (
        verified_at IS NULL OR verified_by IS NOT NULL
    )
);

COMMENT ON TABLE  compliance.evidence_records                    IS 'Regulatory defence documents. Minimum retention enforced per Art.23 CSDDD (5 years), EUDR Art.9 (5 years), UK MSA (3 years), others (2 years). Soft-delete only — never hard-delete before retention_until.';
COMMENT ON COLUMN compliance.evidence_records.document_ref       IS 'File system path, S3 key, SharePoint URL, or other external reference to the actual document.';
COMMENT ON COLUMN compliance.evidence_records.assessment_date    IS 'Date of the underlying assessment or document. Drives retention_until computation.';
COMMENT ON COLUMN compliance.evidence_records.retention_until    IS 'Minimum retention deadline. Must not be soft-deleted before this date. CSDDD/LKSG/EUDR: +5 yr; UK_MSA: +3 yr; others: +2 yr.';
COMMENT ON COLUMN compliance.evidence_records.verified_by        IS 'User who independently verified the document (e.g. second reviewer for CSDDD audit reports).';

CREATE INDEX idx_evidence_supplier         ON compliance.evidence_records(supplier_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_evidence_regulation       ON compliance.evidence_records(regulation_ref) WHERE is_deleted = FALSE;
CREATE INDEX idx_evidence_retention_until  ON compliance.evidence_records(retention_until) WHERE is_deleted = FALSE;
CREATE INDEX idx_evidence_assessment_date  ON compliance.evidence_records(assessment_date DESC);


-- ---------------------------------------------------------------------------
-- GRIEVANCE RECORDS
-- ---------------------------------------------------------------------------

CREATE TABLE compliance.grievance_records (
    id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    reference_number        VARCHAR(30) NOT NULL UNIQUE,
    supplier_id             UUID,
    category                VARCHAR(30) NOT NULL
                                CHECK (category IN (
                                    'FORCED_LABOUR','CHILD_LABOUR','DISCRIMINATION',
                                    'UNSAFE_CONDITIONS','ENVIRONMENTAL','LAND_RIGHTS',
                                    'CORRUPTION','SUPPLY_CHAIN_DISRUPTION','OTHER'
                                )),
    severity                VARCHAR(10) NOT NULL
                                CHECK (severity IN ('LOW','MEDIUM','HIGH','CRITICAL')),
    status                  VARCHAR(20) NOT NULL DEFAULT 'RECEIVED'
                                CHECK (status IN (
                                    'RECEIVED','ACKNOWLEDGED','INVESTIGATING',
                                    'REMEDIATION','RESOLVED','CLOSED','ESCALATED'
                                )),
    description             TEXT        NOT NULL,
    reporter_anonymous      BOOLEAN     NOT NULL DEFAULT FALSE,
    reporter_contact        VARCHAR(500),
    received_at             TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    acknowledged_at         TIMESTAMPTZ,
    target_resolution_date  DATE,
    resolved_at             TIMESTAMPTZ,
    resolution_summary      TEXT,
    regulation_refs         TEXT[]      NOT NULL DEFAULT '{}',
    escalated_to            VARCHAR(200),
    root_cause              TEXT,
    -- CSDDD Art.9 / LkSG §8: CRITICAL grievances must be acknowledged within 24 hours.
    overdue_acknowledgement BOOLEAN GENERATED ALWAYS AS (
        severity = 'CRITICAL'
        AND acknowledged_at IS NULL
        AND received_at < NOW() - INTERVAL '24 hours'
    ) STORED,
    is_deleted              BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT grievance_resolution_requires_summary CHECK (
        status NOT IN ('RESOLVED','CLOSED') OR resolution_summary IS NOT NULL
    ),
    CONSTRAINT grievance_anonymous_contact CHECK (
        reporter_anonymous = FALSE OR reporter_contact IS NULL
    ),
    CONSTRAINT grievance_non_anonymous_requires_contact CHECK (
        reporter_anonymous = TRUE OR reporter_contact IS NOT NULL
    )
);

COMMENT ON TABLE  compliance.grievance_records                        IS 'Grievance records per CSDDD Art.9 and LkSG §8. Accessible to affected persons and their representatives. Anonymous submissions supported.';
COMMENT ON COLUMN compliance.grievance_records.overdue_acknowledgement IS 'Auto-computed: TRUE when a CRITICAL grievance has not been acknowledged within 24 hours (CSDDD Art.9 SLA).';
COMMENT ON COLUMN compliance.grievance_records.regulation_refs        IS 'Array of regulation identifiers relevant to this grievance (e.g. {''CSDDD'',''LKSG''}).';
COMMENT ON COLUMN compliance.grievance_records.resolution_summary     IS 'Mandatory when status is RESOLVED or CLOSED. Must describe remediation taken and outcome (CSDDD Art.9).';

CREATE INDEX idx_grievance_supplier     ON compliance.grievance_records(supplier_id) WHERE supplier_id IS NOT NULL;
CREATE INDEX idx_grievance_status       ON compliance.grievance_records(status) WHERE is_deleted = FALSE;
CREATE INDEX idx_grievance_severity     ON compliance.grievance_records(severity) WHERE is_deleted = FALSE;
CREATE INDEX idx_grievance_received_at  ON compliance.grievance_records(received_at DESC);
CREATE INDEX idx_grievance_overdue      ON compliance.grievance_records(overdue_acknowledgement)
    WHERE overdue_acknowledgement = TRUE AND is_deleted = FALSE;


-- ---------------------------------------------------------------------------
-- GRIEVANCE ACTIONS (audit log per grievance)
-- ---------------------------------------------------------------------------

CREATE TABLE compliance.grievance_actions (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    grievance_id    UUID        NOT NULL REFERENCES compliance.grievance_records(id),
    action_type     VARCHAR(50) NOT NULL,
    description     TEXT        NOT NULL,
    performed_by    VARCHAR(100) NOT NULL,
    performed_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  compliance.grievance_actions              IS 'Immutable audit log of all actions taken on a grievance (acknowledgements, status changes, evidence added, remediation steps).';
COMMENT ON COLUMN compliance.grievance_actions.action_type  IS 'E.g. ACKNOWLEDGED, INVESTIGATION_STARTED, REMEDIATION_ASSIGNED, ESCALATED, RESOLVED, EVIDENCE_ADDED.';

CREATE INDEX idx_grievance_actions_grievance ON compliance.grievance_actions(grievance_id, performed_at DESC);


-- ---------------------------------------------------------------------------
-- EXCEPTION RECORDS
-- ---------------------------------------------------------------------------

CREATE TABLE compliance.exception_records (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    supplier_id     UUID        NOT NULL,
    regulation_ref  VARCHAR(20) NOT NULL
                        CHECK (regulation_ref IN (
                            'CSDDD','UFLPA','REACH','LKSG','EUDR','UK_MSA','C_TPAT','ISO_28000'
                        )),
    description     TEXT        NOT NULL,
    justification   TEXT        NOT NULL,
    risk            VARCHAR(15) NOT NULL
                        CHECK (risk IN ('ACCEPTABLE','CONDITIONAL','UNACCEPTABLE')),
    requested_by    VARCHAR(100) NOT NULL,
    requested_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    approved_by     VARCHAR(100),
    approved_at     TIMESTAMPTZ,
    valid_until     DATE,
    conditions      TEXT[],
    status          VARCHAR(10) NOT NULL DEFAULT 'PENDING'
                        CHECK (status IN ('PENDING','APPROVED','REJECTED','EXPIRED')),
    is_deleted      BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    -- Business rule: UNACCEPTABLE risk cannot be approved
    CONSTRAINT exception_unacceptable_not_approved CHECK (
        risk <> 'UNACCEPTABLE' OR status NOT IN ('APPROVED')
    ),
    -- Approved exceptions must have a validity date and approver
    CONSTRAINT exception_approval_requires_fields CHECK (
        status <> 'APPROVED'
        OR (approved_by IS NOT NULL AND valid_until IS NOT NULL AND approved_at IS NOT NULL)
    ),
    -- valid_until must be after requested_at date
    CONSTRAINT exception_valid_until_future CHECK (
        valid_until IS NULL OR valid_until > requested_at::DATE
    )
);

COMMENT ON TABLE  compliance.exception_records                IS 'Time-bound exception approvals for compliance deviations. UNACCEPTABLE risk exceptions are blocked from approval at DB and application layers.';
COMMENT ON COLUMN compliance.exception_records.risk           IS 'ACCEPTABLE=low residual risk, CONDITIONAL=approved with mandatory conditions, UNACCEPTABLE=cannot be approved — must remediate.';
COMMENT ON COLUMN compliance.exception_records.conditions     IS 'Array of conditions the requester must satisfy for the exception to remain valid (e.g. {''Monthly audit required'', ''Clearance doc submitted within 30 days''}).';
COMMENT ON COLUMN compliance.exception_records.valid_until    IS 'Exception expires on this date. Application layer should set status=EXPIRED after this date and re-assess compliance.';

CREATE INDEX idx_exception_supplier     ON compliance.exception_records(supplier_id) WHERE is_deleted = FALSE;
CREATE INDEX idx_exception_regulation   ON compliance.exception_records(regulation_ref) WHERE is_deleted = FALSE;
CREATE INDEX idx_exception_status       ON compliance.exception_records(status) WHERE is_deleted = FALSE;
CREATE INDEX idx_exception_valid_until  ON compliance.exception_records(valid_until) WHERE status = 'APPROVED' AND is_deleted = FALSE;


-- ---------------------------------------------------------------------------
-- ADDITIONAL VIEWS
-- ---------------------------------------------------------------------------

-- Evidence records approaching end of retention period (within 90 days)
CREATE OR REPLACE VIEW compliance.v_evidence_expiring_soon AS
SELECT
    er.id,
    er.supplier_id,
    er.regulation_ref,
    er.evidence_type,
    er.title,
    er.document_ref,
    er.assessment_date,
    er.retention_until,
    er.retention_until - CURRENT_DATE   AS days_to_expiry,
    er.uploaded_by,
    er.verified_by,
    CASE
        WHEN er.retention_until < CURRENT_DATE              THEN 'EXPIRED'
        WHEN er.retention_until < CURRENT_DATE + 30         THEN 'EXPIRING_30_DAYS'
        WHEN er.retention_until < CURRENT_DATE + 60         THEN 'EXPIRING_60_DAYS'
        ELSE 'EXPIRING_90_DAYS'
    END                                                     AS expiry_urgency
FROM compliance.evidence_records er
WHERE er.retention_until < CURRENT_DATE + INTERVAL '90 days'
  AND er.is_deleted = FALSE
ORDER BY er.retention_until ASC;

COMMENT ON VIEW compliance.v_evidence_expiring_soon IS 'Evidence records whose retention_until is within 90 days (or already past). Drives archival/renewal workflow. Buckets: EXPIRED, 30/60/90 days.';


-- Open grievances with overdue flag and days open
CREATE OR REPLACE VIEW compliance.v_open_grievances AS
SELECT
    gr.id,
    gr.reference_number,
    gr.supplier_id,
    gr.category,
    gr.severity,
    gr.status,
    gr.received_at,
    gr.acknowledged_at,
    gr.target_resolution_date,
    gr.regulation_refs,
    gr.escalated_to,
    gr.overdue_acknowledgement,
    EXTRACT(DAY FROM (NOW() - gr.received_at))::INTEGER     AS days_open,
    CASE
        WHEN gr.target_resolution_date IS NOT NULL
             AND gr.target_resolution_date < CURRENT_DATE   THEN TRUE
        ELSE FALSE
    END                                                     AS resolution_overdue
FROM compliance.grievance_records gr
WHERE gr.status NOT IN ('CLOSED')
  AND gr.is_deleted = FALSE
ORDER BY
    gr.severity DESC,
    gr.received_at ASC;

COMMENT ON VIEW compliance.v_open_grievances IS 'All non-closed grievances. Includes days_open, overdue_acknowledgement (CRITICAL 24-h SLA), and resolution_overdue flags. Used for CSDDD Art.9 / LkSG §8 monitoring.';


-- Compliance dashboard: counts by regulation and status
CREATE OR REPLACE VIEW compliance.v_compliance_dashboard AS
SELECT
    'EVIDENCE'          AS domain,
    er.regulation_ref,
    COUNT(*)            AS total_records,
    COUNT(*) FILTER (WHERE er.retention_until >= CURRENT_DATE)  AS active_count,
    COUNT(*) FILTER (WHERE er.retention_until < CURRENT_DATE)   AS expired_count,
    NULL::BIGINT        AS pending_count,
    NULL::BIGINT        AS critical_count
FROM compliance.evidence_records er
WHERE er.is_deleted = FALSE
GROUP BY er.regulation_ref

UNION ALL

SELECT
    'GRIEVANCE'         AS domain,
    unnest(gr.regulation_refs) AS regulation_ref,
    COUNT(*)            AS total_records,
    COUNT(*) FILTER (WHERE gr.status NOT IN ('CLOSED','RESOLVED')) AS active_count,
    COUNT(*) FILTER (WHERE gr.status IN ('CLOSED','RESOLVED'))     AS expired_count,
    COUNT(*) FILTER (WHERE gr.status = 'RECEIVED')                 AS pending_count,
    COUNT(*) FILTER (WHERE gr.severity = 'CRITICAL' AND gr.status NOT IN ('CLOSED','RESOLVED')) AS critical_count
FROM compliance.grievance_records gr
WHERE gr.is_deleted = FALSE
GROUP BY unnest(gr.regulation_refs)

UNION ALL

SELECT
    'EXCEPTION'         AS domain,
    ex.regulation_ref,
    COUNT(*)            AS total_records,
    COUNT(*) FILTER (WHERE ex.status = 'APPROVED' AND ex.valid_until >= CURRENT_DATE)  AS active_count,
    COUNT(*) FILTER (WHERE ex.status IN ('REJECTED','EXPIRED')
                        OR (ex.status = 'APPROVED' AND ex.valid_until < CURRENT_DATE)) AS expired_count,
    COUNT(*) FILTER (WHERE ex.status = 'PENDING')                                      AS pending_count,
    COUNT(*) FILTER (WHERE ex.risk = 'UNACCEPTABLE')                                   AS critical_count
FROM compliance.exception_records ex
WHERE ex.is_deleted = FALSE
GROUP BY ex.regulation_ref

ORDER BY domain, regulation_ref;

COMMENT ON VIEW compliance.v_compliance_dashboard IS 'Aggregated compliance dashboard across evidence, grievances, and exceptions. Groups by domain and regulation_ref with active/expired/pending/critical breakdowns.';
