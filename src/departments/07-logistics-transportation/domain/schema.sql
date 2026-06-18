-- =============================================================================
-- SCHEMA: logistics
-- Department: 07 – Logistics & Transportation
-- Feeds Python: logistics.py (calculate_co2_emissions, freight_cost,
--               customs_duty, clarke_wright_savings, otd_rate)
-- Standards: Incoterms® 2020 (ICC), GHG Protocol Scope 3 (Cat 4 & 9),
--            WTO TFA Art.7, C-TPAT (US CBP), AEO (EU), IMDG/ADR hazmat,
--            Basel Convention, ISO 28000:2022
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS logistics;

-- ---------------------------------------------------------------------------
-- TABLES
-- ---------------------------------------------------------------------------

CREATE TABLE logistics.carriers (
    id                          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    carrier_code                VARCHAR(20) NOT NULL UNIQUE,
    name                        VARCHAR(200) NOT NULL,
    transport_modes             TEXT[]      NOT NULL DEFAULT '{}',
    ctpat_certified             BOOLEAN     NOT NULL DEFAULT FALSE,
    aeo_certified               BOOLEAN     NOT NULL DEFAULT FALSE,
    co2_reporting_available     BOOLEAN     NOT NULL DEFAULT FALSE,
    default_transit_time_days   INTEGER     CHECK (default_transit_time_days > 0),
    transit_time_std_days       NUMERIC(6,2) CHECK (transit_time_std_days >= 0),
    insurance_policy_ref        VARCHAR(200),
    liability_limit_cents       BIGINT      CHECK (liability_limit_cents >= 0),
    is_deleted                  BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  logistics.carriers                        IS 'Approved carrier master. Includes security certifications (C-TPAT/AEO) and CO2 reporting capability for GHG Protocol Scope 3 tracking.';
COMMENT ON COLUMN logistics.carriers.transport_modes        IS 'Array of modes operated, e.g. {''ROAD'',''SEA''}. Validated at application layer against ROAD/SEA/AIR/RAIL/MULTIMODAL.';
COMMENT ON COLUMN logistics.carriers.ctpat_certified        IS 'US CBP C-TPAT (Customs-Trade Partnership Against Terrorism) certification status.';
COMMENT ON COLUMN logistics.carriers.aeo_certified          IS 'EU Authorised Economic Operator status per WTO TFA Art.7.';
COMMENT ON COLUMN logistics.carriers.transit_time_std_days  IS 'Standard deviation of transit time in days. Fed into safety stock lead-time variability model (Method 4).';


CREATE TABLE logistics.shipments (
    id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    shipment_number         VARCHAR(50) NOT NULL UNIQUE,
    carrier_id              UUID        NOT NULL REFERENCES logistics.carriers(id),
    transport_mode          VARCHAR(15) NOT NULL
                                CHECK (transport_mode IN ('ROAD','SEA','AIR','RAIL','MULTIMODAL')),
    status                  VARCHAR(20) NOT NULL DEFAULT 'BOOKED'
                                CHECK (status IN ('BOOKED','IN_TRANSIT','CUSTOMS_HOLD','DELIVERED','EXCEPTION','CANCELLED')),
    origin_location_code    VARCHAR(100) NOT NULL,
    destination_location_code VARCHAR(100) NOT NULL,
    incoterm                CHAR(3)     NOT NULL
                                CHECK (incoterm IN ('EXW','FCA','FAS','FOB','CFR','CIF','CPT','CIP','DAP','DPU','DDP')),
    estimated_departure     DATE,
    actual_departure        TIMESTAMPTZ,
    estimated_delivery      DATE,
    actual_delivery         TIMESTAMPTZ,
    is_on_time              BOOLEAN     GENERATED ALWAYS AS (
                                CASE
                                    WHEN actual_delivery IS NOT NULL AND estimated_delivery IS NOT NULL
                                    THEN actual_delivery::DATE <= estimated_delivery
                                    ELSE NULL
                                END
                            ) STORED,
    weight_kg               NUMERIC(12,3) CHECK (weight_kg > 0),
    volume_m3               NUMERIC(12,6) CHECK (volume_m3 > 0),
    chargeable_weight_kg    NUMERIC(12,3) CHECK (chargeable_weight_kg > 0),
    freight_cost_cents      INTEGER     CHECK (freight_cost_cents >= 0),
    fuel_surcharge_pct      NUMERIC(6,4) NOT NULL DEFAULT 0 CHECK (fuel_surcharge_pct >= 0),
    co2_kg                  NUMERIC(12,4) CHECK (co2_kg >= 0),
    aeo_shipper_certified   BOOLEAN     NOT NULL DEFAULT FALSE,
    is_deleted              BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  logistics.shipments                    IS 'Shipment header. One shipment may span multiple legs and lines. is_on_time is auto-computed for OTD KPI reporting.';
COMMENT ON COLUMN logistics.shipments.incoterm           IS 'Incoterms® 2020 rule (ICC). DPU replaces DAT from 2020. Determines risk/cost transfer point.';
COMMENT ON COLUMN logistics.shipments.is_on_time         IS 'TRUE if actual_delivery <= estimated_delivery. Auto-computed. NULL until delivery recorded. Feeds otd_rate() in logistics.py.';
COMMENT ON COLUMN logistics.shipments.chargeable_weight_kg IS 'Greater of actual weight and volumetric weight (volume_m3 * density factor). Basis for freight rating.';
COMMENT ON COLUMN logistics.shipments.co2_kg             IS 'Total CO2-equivalent emissions for this shipment. Aggregated from transport_legs. GHG Protocol Scope 3 Cat 4/9.';
COMMENT ON COLUMN logistics.shipments.freight_cost_cents IS 'Base freight cost in integer cents. No floats per project money rules.';


CREATE TABLE logistics.shipment_lines (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    shipment_id         UUID        NOT NULL REFERENCES logistics.shipments(id),
    po_id               UUID,
    sku_id              VARCHAR(50),
    quantity            NUMERIC(15,4) NOT NULL CHECK (quantity > 0),
    uom                 CHAR(3)     NOT NULL,
    hs_code             VARCHAR(10),
    sscc                VARCHAR(18),
    hazmat_class        VARCHAR(15)
                            CHECK (hazmat_class IN (
                                '1_EXPLOSIVES','2_GAS','3_FLAMMABLE','4_SOLID',
                                '5_OXIDIZER','6_TOXIC','7_RADIOACTIVE',
                                '8_CORROSIVE','9_MISC'
                            ) OR hazmat_class IS NULL),
    unit_value_cents    INTEGER     CHECK (unit_value_cents >= 0),
    line_value_cents    INTEGER     GENERATED ALWAYS AS (
                            CASE WHEN unit_value_cents IS NOT NULL
                                 THEN FLOOR(quantity * unit_value_cents)::INTEGER
                                 ELSE NULL END
                        ) STORED,
    country_of_origin   CHAR(2),
    is_deleted          BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  logistics.shipment_lines              IS 'Individual commodity lines within a shipment. HS code required for customs declaration. Hazmat class per IMDG/ADR codes.';
COMMENT ON COLUMN logistics.shipment_lines.hs_code      IS 'Harmonised System commodity code (6-digit WCO minimum, up to 10 for national tariff). Required for customs_duty() calculation.';
COMMENT ON COLUMN logistics.shipment_lines.sscc         IS 'GS1 Serial Shipping Container Code (18 digits). Identifies the logistic unit.';
COMMENT ON COLUMN logistics.shipment_lines.hazmat_class IS 'IMDG/ADR hazmat class. NULL for non-dangerous goods. Basel Convention applicable for class 6_TOXIC.';
COMMENT ON COLUMN logistics.shipment_lines.line_value_cents IS 'Auto-computed: floor(quantity * unit_value_cents). INTEGER cents, no floats.';


CREATE TABLE logistics.transport_legs (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    shipment_id         UUID        NOT NULL REFERENCES logistics.shipments(id),
    leg_number          INTEGER     NOT NULL CHECK (leg_number >= 1),
    mode                VARCHAR(15) NOT NULL
                            CHECK (mode IN ('ROAD','SEA','AIR','RAIL','MULTIMODAL')),
    carrier_id          UUID        REFERENCES logistics.carriers(id),
    origin              VARCHAR(100) NOT NULL,
    destination         VARCHAR(100) NOT NULL,
    estimated_departure DATE,
    actual_departure    TIMESTAMPTZ,
    estimated_arrival   DATE,
    actual_arrival      TIMESTAMPTZ,
    distance_km         NUMERIC(10,2) CHECK (distance_km > 0),
    co2_kg              NUMERIC(12,4) CHECK (co2_kg >= 0),
    is_deleted          BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (shipment_id, leg_number)
);

COMMENT ON TABLE  logistics.transport_legs             IS 'Individual legs of a multimodal shipment. CO2 per leg feeds calculate_co2_emissions() in logistics.py.';
COMMENT ON COLUMN logistics.transport_legs.leg_number  IS 'Sequential leg number starting at 1. Order is significant for multimodal route reconstruction.';
COMMENT ON COLUMN logistics.transport_legs.distance_km IS 'Great-circle or road distance in km. Used with emission factor for CO2 calculation.';


CREATE TABLE logistics.tracking_events (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    shipment_id     UUID        NOT NULL REFERENCES logistics.shipments(id),
    event_type      VARCHAR(30) NOT NULL
                        CHECK (event_type IN (
                            'PICKED_UP','IN_TRANSIT','CUSTOMS_CLEARED',
                            'OUT_FOR_DELIVERY','DELIVERED','EXCEPTION'
                        )),
    location        VARCHAR(200),
    event_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    notes           TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  logistics.tracking_events              IS 'Chronological tracking milestones for a shipment. Immutable once created — no soft-delete (audit trail).';
COMMENT ON COLUMN logistics.tracking_events.event_type   IS 'Standardised event codes. EXCEPTION triggers alert workflow; DELIVERED auto-updates shipment.actual_delivery.';


CREATE TABLE logistics.customs_documents (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    shipment_id         UUID        NOT NULL REFERENCES logistics.shipments(id),
    doc_type            VARCHAR(30) NOT NULL
                            CHECK (doc_type IN (
                                'COMMERCIAL_INVOICE','PACKING_LIST','BILL_OF_LADING',
                                'AIRWAYBILL','CERTIFICATE_OF_ORIGIN','PHYTOSANITARY',
                                'DANGEROUS_GOODS'
                            )),
    doc_number          VARCHAR(100),
    issued_date         DATE,
    issuing_authority   VARCHAR(200),
    file_ref            VARCHAR(500),
    is_valid            BOOLEAN     NOT NULL DEFAULT TRUE,
    is_deleted          BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  logistics.customs_documents              IS 'Customs and trade documents attached to a shipment. DANGEROUS_GOODS declaration required per IMDG/ADR when hazmat_class is set.';
COMMENT ON COLUMN logistics.customs_documents.doc_type     IS 'Document type per international trade conventions: Bill of Lading (sea), Airwaybill (air), CMR (road). Phytosanitary for agricultural goods.';
COMMENT ON COLUMN logistics.customs_documents.file_ref     IS 'Reference to document storage system (e.g. S3 key or DMS path). Max 500 chars.';


CREATE TABLE logistics.co2_emissions_log (
    id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    shipment_id             UUID        NOT NULL REFERENCES logistics.shipments(id),
    leg_id                  UUID        REFERENCES logistics.transport_legs(id),
    distance_km             NUMERIC(12,4) NOT NULL CHECK (distance_km > 0),
    weight_tonnes           NUMERIC(12,6) NOT NULL CHECK (weight_tonnes > 0),
    transport_mode          VARCHAR(15) NOT NULL
                                CHECK (transport_mode IN ('ROAD','SEA','AIR','RAIL','MULTIMODAL')),
    emission_factor         NUMERIC(12,8) NOT NULL CHECK (emission_factor > 0),
    co2_kg                  NUMERIC(14,4) GENERATED ALWAYS AS
                                (distance_km * weight_tonnes * emission_factor) STORED,
    ghg_protocol_category   VARCHAR(30) NOT NULL
                                CHECK (ghg_protocol_category IN ('SCOPE3_CAT4_UPSTREAM','SCOPE3_CAT9_DOWNSTREAM')),
    period_date             DATE        NOT NULL,
    methodology             VARCHAR(100) DEFAULT 'GLEC_FRAMEWORK_V3',
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  logistics.co2_emissions_log                   IS 'GHG Protocol Scope 3 CO2 emission records per shipment/leg. co2_kg auto-computed from distance, weight, and emission factor. Feeds calculate_co2_emissions() in logistics.py.';
COMMENT ON COLUMN logistics.co2_emissions_log.emission_factor   IS 'kg CO2e per tonne-km. Source: GLEC Framework v3 / DEFRA emission factors by mode. Must be updated annually.';
COMMENT ON COLUMN logistics.co2_emissions_log.co2_kg            IS 'Auto-computed: distance_km * weight_tonnes * emission_factor. Stored for query performance.';
COMMENT ON COLUMN logistics.co2_emissions_log.ghg_protocol_category IS 'SCOPE3_CAT4_UPSTREAM = inbound freight (supplier to warehouse); SCOPE3_CAT9_DOWNSTREAM = outbound freight (warehouse to customer).';
COMMENT ON COLUMN logistics.co2_emissions_log.methodology       IS 'Emission calculation methodology. Default GLEC Framework v3. Document any deviations.';


CREATE TABLE logistics.freight_invoices (
    id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    carrier_id              UUID        NOT NULL REFERENCES logistics.carriers(id),
    shipment_id             UUID        REFERENCES logistics.shipments(id),
    invoice_number          VARCHAR(100) NOT NULL UNIQUE,
    base_rate_cents         INTEGER     NOT NULL CHECK (base_rate_cents >= 0),
    fuel_surcharge_cents    INTEGER     NOT NULL DEFAULT 0 CHECK (fuel_surcharge_cents >= 0),
    accessorial_cents       INTEGER     NOT NULL DEFAULT 0 CHECK (accessorial_cents >= 0),
    total_cents             INTEGER     NOT NULL GENERATED ALWAYS AS
                                (base_rate_cents + fuel_surcharge_cents + accessorial_cents) STORED,
    currency                CHAR(3)     NOT NULL DEFAULT 'USD',
    invoice_date            DATE        NOT NULL,
    due_date                DATE,
    status                  VARCHAR(15) NOT NULL DEFAULT 'PENDING'
                                CHECK (status IN ('PENDING','MATCHED','DISPUTED','PAID','CANCELLED')),
    dispute_reason          TEXT,
    is_deleted              BOOLEAN     NOT NULL DEFAULT FALSE,
    created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  logistics.freight_invoices              IS 'Carrier freight invoices for 3-way matching against PO and shipment. All amounts in integer cents.';
COMMENT ON COLUMN logistics.freight_invoices.total_cents  IS 'Auto-computed: base + fuel surcharge + accessorials. No manual override.';
COMMENT ON COLUMN logistics.freight_invoices.status       IS 'PENDING=received, MATCHED=3-way match passed, DISPUTED=variance found, PAID=payment released.';


-- ---------------------------------------------------------------------------
-- INDEXES
-- ---------------------------------------------------------------------------

CREATE INDEX idx_shipments_carrier_status       ON logistics.shipments(carrier_id, status);
CREATE INDEX idx_shipments_status               ON logistics.shipments(status) WHERE is_deleted = FALSE;
CREATE INDEX idx_shipments_estimated_delivery   ON logistics.shipments(estimated_delivery) WHERE is_deleted = FALSE;
CREATE INDEX idx_shipments_actual_delivery      ON logistics.shipments(actual_delivery) WHERE is_deleted = FALSE;
CREATE INDEX idx_shipments_incoterm             ON logistics.shipments(incoterm);

CREATE INDEX idx_shipment_lines_shipment        ON logistics.shipment_lines(shipment_id);
CREATE INDEX idx_shipment_lines_po              ON logistics.shipment_lines(po_id) WHERE po_id IS NOT NULL;
CREATE INDEX idx_shipment_lines_sku             ON logistics.shipment_lines(sku_id);
CREATE INDEX idx_shipment_lines_hazmat          ON logistics.shipment_lines(hazmat_class) WHERE hazmat_class IS NOT NULL;

CREATE INDEX idx_transport_legs_shipment        ON logistics.transport_legs(shipment_id, leg_number);
CREATE INDEX idx_tracking_events_shipment_time  ON logistics.tracking_events(shipment_id, event_timestamp DESC);
CREATE INDEX idx_tracking_events_type           ON logistics.tracking_events(event_type);
CREATE INDEX idx_customs_docs_shipment          ON logistics.customs_documents(shipment_id);

CREATE INDEX idx_co2_log_shipment               ON logistics.co2_emissions_log(shipment_id);
CREATE INDEX idx_co2_log_period                 ON logistics.co2_emissions_log(period_date, transport_mode);
CREATE INDEX idx_co2_log_ghg_category           ON logistics.co2_emissions_log(ghg_protocol_category, period_date);

CREATE INDEX idx_freight_invoices_carrier       ON logistics.freight_invoices(carrier_id);
CREATE INDEX idx_freight_invoices_status        ON logistics.freight_invoices(status) WHERE is_deleted = FALSE;


-- ---------------------------------------------------------------------------
-- VIEWS
-- ---------------------------------------------------------------------------

-- OTD by carrier and route
CREATE OR REPLACE VIEW logistics.v_shipment_otd AS
SELECT
    s.carrier_id,
    c.name                                              AS carrier_name,
    s.transport_mode,
    s.origin_location_code,
    s.destination_location_code,
    s.incoterm,
    COUNT(*)                                            AS total_shipments,
    SUM(CASE WHEN s.is_on_time THEN 1 ELSE 0 END)      AS on_time_count,
    ROUND(
        SUM(CASE WHEN s.is_on_time THEN 1 ELSE 0 END)::NUMERIC /
        NULLIF(COUNT(*), 0) * 100, 2
    )                                                   AS otd_pct,
    AVG(
        EXTRACT(EPOCH FROM (s.actual_delivery - s.actual_departure)) / 86400.0
    )                                                   AS avg_actual_transit_days
FROM logistics.shipments s
JOIN logistics.carriers c ON c.id = s.carrier_id
WHERE s.actual_delivery IS NOT NULL
  AND s.is_deleted = FALSE
GROUP BY s.carrier_id, c.name, s.transport_mode, s.origin_location_code,
         s.destination_location_code, s.incoterm;

COMMENT ON VIEW logistics.v_shipment_otd IS 'On-Time Delivery rate by carrier/route. OTD world-class target ≥ 95%. Feeds otd_rate() in logistics.py.';


-- CO2 by transport mode and month
CREATE OR REPLACE VIEW logistics.v_co2_by_mode_period AS
SELECT
    transport_mode,
    ghg_protocol_category,
    DATE_TRUNC('month', period_date)    AS period_month,
    COUNT(*)                            AS leg_count,
    ROUND(SUM(distance_km), 2)          AS total_distance_km,
    ROUND(SUM(weight_tonnes), 4)        AS total_weight_tonnes,
    ROUND(SUM(co2_kg), 4)               AS total_co2_kg,
    ROUND(SUM(co2_kg) / NULLIF(SUM(distance_km * weight_tonnes), 0), 6) AS avg_emission_factor
FROM logistics.co2_emissions_log
GROUP BY transport_mode, ghg_protocol_category, DATE_TRUNC('month', period_date)
ORDER BY period_month DESC, total_co2_kg DESC;

COMMENT ON VIEW logistics.v_co2_by_mode_period IS 'Monthly CO2 emissions aggregated by transport mode and GHG Protocol category. Supports Scope 3 Cat 4/9 carbon reporting.';


-- Carrier performance scorecard
CREATE OR REPLACE VIEW logistics.v_carrier_performance AS
SELECT
    c.id                                                AS carrier_id,
    c.carrier_code,
    c.name                                              AS carrier_name,
    c.transport_modes,
    c.ctpat_certified,
    c.aeo_certified,
    COUNT(s.id)                                         AS total_shipments,
    ROUND(
        SUM(CASE WHEN s.is_on_time THEN 1 ELSE 0 END)::NUMERIC /
        NULLIF(COUNT(s.id), 0) * 100, 2
    )                                                   AS otd_pct,
    ROUND(AVG(
        CASE WHEN s.actual_departure IS NOT NULL AND s.actual_delivery IS NOT NULL
        THEN EXTRACT(EPOCH FROM (s.actual_delivery - s.actual_departure)) / 86400.0
        END
    ), 2)                                               AS avg_transit_days,
    ROUND(
        SUM(e.co2_kg) / NULLIF(SUM(e.distance_km * e.weight_tonnes), 0), 6
    )                                                   AS co2_per_tonne_km
FROM logistics.carriers c
LEFT JOIN logistics.shipments s
       ON s.carrier_id = c.id AND s.is_deleted = FALSE
LEFT JOIN logistics.co2_emissions_log e
       ON e.shipment_id = s.id
WHERE c.is_deleted = FALSE
GROUP BY c.id, c.carrier_code, c.name, c.transport_modes, c.ctpat_certified, c.aeo_certified;

COMMENT ON VIEW logistics.v_carrier_performance IS 'Carrier scorecard: OTD %, average transit days, CO2 per tonne-km. Feeds carrier selection in logistics.py clarke_wright_savings().';
