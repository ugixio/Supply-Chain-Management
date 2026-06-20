/**
 * EUDR Assessment aggregate — EU Deforestation Regulation 2023/1115 due diligence,
 * as amended by EU Regulation 2025/2650 (December 2025).
 *
 * The EU Deforestation Regulation (EUDR) requires operators to ensure that
 * regulated commodities placed on the EU market have not caused deforestation
 * or forest degradation and were produced in compliance with the legislation
 * of the country of production.
 *
 * Key provisions implemented:
 *  - Art. 3   — Prohibition on placing non-compliant products on the EU market
 *  - Art. 3a  — Geolocation data requirements: GPS point (≥6 decimal places) for
 *               plots < 4 ha; polygon for plots ≥ 4 ha; submitted via TRACES NT
 *  - Art. 8   — Operator due diligence obligations
 *  - Art. 10  — Enhanced due diligence for high-risk countries
 *  - Art. 10(5) — 5-year document retention period
 *  - Art. 29  — Country benchmarking system (HIGH / STANDARD / LOW tiers) per
 *               Commission Delegated Regulation; determines compliance check rate
 *  - Annex I  — List of regulated commodities and derived products
 *
 * EUDR cutoff date: 31 December 2020 — land must not have been deforested
 * after this date. Products from land deforested after 2020-12-31 cannot
 * be imported/placed on the EU market.
 *
 * Effective dates (Reg. 2025/2650):
 *  - Large operators: 30 December 2026
 *  - SMEs:           30 June 2027
 *
 * Country benchmarking tiers (Art. 29):
 *  - HIGH:     9% compliance check rate — full due diligence required
 *  - STANDARD: 3% compliance check rate — full due diligence required
 *  - LOW:      1% compliance check rate — simplified due diligence
 *  - PENDING:  Not yet benchmarked by the Commission
 *
 * Due Diligence Statements (DDS) are submitted via TRACES NT.
 *
 * References:
 *  - EU Regulation 2023/1115 (EUDR)
 *  - EU Regulation 2025/2650 (amending EUDR — delay + benchmarking)
 *  - EU EUDR implementing guidance (2024)
 *  - Global Forest Watch deforestation data
 */

import { v4 as uuidv4 } from 'uuid';
import { ISODate, ISOTimestamp, nowUTC } from '../../../shared/types';

/** Regulated commodities under EUDR 2023/1115 Annex I */
export type EUDRCommodity =
  | 'CATTLE'
  | 'COCOA'
  | 'COFFEE'
  | 'PALM_OIL'
  | 'SOYA'
  | 'WOOD'
  | 'RUBBER'
  | 'MAIZE';

export type EUDRRiskLevel = 'NEGLIGIBLE' | 'LOW' | 'MEDIUM' | 'HIGH';

/**
 * Geolocation data for a production plot per EUDR Art. 3a.
 * Plots < 4 ha: single GPS point with ≥6 decimal places of precision.
 * Plots ≥ 4 ha: polygon describing the perimeter (GeoJSON or WKT format).
 * Submission via TRACES NT as part of the Due Diligence Statement (DDS).
 */
export type ProductionPlotType = 'GPS_POINT' | 'POLYGON';

export type ProductionPlot = {
  readonly plotId: string;
  readonly plotType: ProductionPlotType;
  /**
   * For GPS_POINT: 'lat,lon' string with ≥6 decimal places e.g. '12.345678,-45.678901'
   * For POLYGON: WKT polygon string e.g. 'POLYGON((lon lat, lon lat, ...))'
   */
  readonly coordinates: string;
  readonly areaHectares?: number;      // if known — determines GPS vs polygon requirement
  readonly parcelIdentifier?: string;  // national cadastre or farm ID
};

/**
 * Country benchmarking tier per EUDR Art. 29 and Commission Delegated Regulation.
 * HIGH:     9% compliance check rate — full due diligence required
 * STANDARD: 3% compliance check rate — full due diligence required (majority of countries)
 * LOW:      1% compliance check rate — simplified due diligence (information only)
 * PENDING:  Not yet benchmarked by Commission
 */
export type EUDRCountryRiskTier = 'HIGH' | 'STANDARD' | 'LOW' | 'PENDING';

export type EUDRStatus =
  | 'NOT_STARTED'
  | 'IN_PROGRESS'
  | 'COMPLIANT'
  | 'NON_COMPLIANT'
  | 'PENDING_VERIFICATION';

/** EUDR cutoff date per Art. 2(1) — production must not cause deforestation after this date. */
const EUDR_CUTOFF_DATE: ISODate = '2020-12-31';

/** Commodities that carry inherently higher deforestation risk. */
const HIGH_RISK_COMMODITIES: ReadonlySet<EUDRCommodity> = new Set([
  'CATTLE',
  'PALM_OIL',
  'SOYA',
  'WOOD',
]);

export type EUDRAssessment = {
  readonly id: string;
  readonly supplierId: string;
  readonly commodity: EUDRCommodity;
  /** ISO 3166-1 alpha-2 country code */
  readonly countryOfOrigin: string;
  /**
   * WKT polygon or lat/lon coordinates of production area.
   * @deprecated Use `productionPlots` for structured geolocation per EUDR Art. 3a.
   */
  readonly geolocation?: string;
  readonly assessmentDate: ISODate;
  status: EUDRStatus;
  riskLevel: EUDRRiskLevel;
  /**
   * Production start date on the parcel of land.
   * Must be after EUDR_CUTOFF_DATE (2020-12-31) for EUDR compliance.
   * Undefined means date is unknown — triggers PENDING_VERIFICATION.
   */
  readonly productionStartDate?: ISODate;
  satelliteVerified: boolean;
  documentRef?: string;
  // Structured geolocation (replaces free-form geolocation field — both kept for migration)
  readonly productionPlots: ProductionPlot[];

  // EUDR country benchmarking tier (Reg. 2025/2650 Art. 29)
  readonly countryRiskTier: EUDRCountryRiskTier;

  // TRACES NT Due Diligence Statement reference number
  readonly ddsReference?: string;

  // Operator type determines compliance deadline
  readonly operatorType: 'LARGE_OPERATOR' | 'SME';

  // Effective date per operator type (Reg. 2025/2650):
  // LARGE_OPERATOR: 2026-12-30 | SME: 2027-06-30
  readonly complianceDeadline: ISODate;

  /**
   * Document retention deadline per EUDR Art. 10(5): assessmentDate + 5 years.
   * Pre-computed at creation time.
   */
  readonly retentionUntil: ISODate;
  readonly isDeleted: boolean;
  readonly createdAt: ISOTimestamp;
  updatedAt: ISOTimestamp;
};

// ---------------------------------------------------------------------------
// Business rule helpers
// ---------------------------------------------------------------------------

/** Adds years to an ISO date string and returns the resulting ISO date. */
function addYears(isoDate: ISODate, years: number): ISODate {
  const d = new Date(isoDate);
  d.setFullYear(d.getFullYear() + years);
  return d.toISOString().substring(0, 10);
}

/**
 * Validates the productionStartDate against the EUDR cutoff.
 * Returns true when the date is valid (after 2020-12-31), or when undefined
 * (date unknown — will remain PENDING_VERIFICATION).
 */
function isProductionDateCompliant(productionStartDate?: ISODate): boolean {
  if (productionStartDate === undefined) return true; // unknown — not auto-failed
  return productionStartDate > EUDR_CUTOFF_DATE;
}

function deriveInitialStatus(
  productionStartDate?: ISODate,
): EUDRStatus {
  if (productionStartDate === undefined) return 'PENDING_VERIFICATION';
  if (!isProductionDateCompliant(productionStartDate)) return 'NON_COMPLIANT';
  return 'IN_PROGRESS';
}

// ---------------------------------------------------------------------------
// Methods (implemented as namespace — same pattern as SalesOrder in this dept)
// ---------------------------------------------------------------------------

export const EUDRAssessment = {
  /**
   * Factory — initiates a new EUDR assessment for a supplier/commodity pair.
   *
   * @param supplierId          - Supplier being assessed
   * @param commodity           - EUDR Annex I regulated commodity
   * @param countryOfOrigin     - ISO 3166-1 alpha-2 country code
   * @param assessmentDate      - Date assessment is conducted (ISO 8601)
   * @param productionStartDate - Production start date on the land parcel (optional)
   *                             Must be > 2020-12-31 for EUDR compliance (Art. 2(1)).
   *                             If undefined, status = PENDING_VERIFICATION.
   * @param productionPlots     - Structured geolocation data per EUDR Art. 3a (default: [])
   * @param countryRiskTier     - Country benchmarking tier per Reg. 2025/2650 Art. 29 (default: 'STANDARD')
   * @param ddsReference        - TRACES NT Due Diligence Statement reference number (optional)
   * @param operatorType        - Operator classification determining compliance deadline (default: 'LARGE_OPERATOR')
   */
  initiate(
    supplierId: string,
    commodity: EUDRCommodity,
    countryOfOrigin: string,
    assessmentDate: ISODate,
    productionStartDate?: ISODate,
    productionPlots: ProductionPlot[] = [],
    countryRiskTier: EUDRCountryRiskTier = 'STANDARD',
    ddsReference?: string,
    operatorType: 'LARGE_OPERATOR' | 'SME' = 'LARGE_OPERATOR',
  ): EUDRAssessment {
    if (!supplierId) throw new Error('supplierId is required.');
    if (!countryOfOrigin || countryOfOrigin.length !== 2) {
      throw new Error('countryOfOrigin must be a valid ISO 3166-1 alpha-2 code.');
    }
    if (!assessmentDate) throw new Error('assessmentDate is required.');

    // Business rule: productionStartDate must be after cutoff if provided
    if (
      productionStartDate !== undefined &&
      !isProductionDateCompliant(productionStartDate)
    ) {
      // Still create the record but mark NON_COMPLIANT
    }

    const complianceDeadline: ISODate =
      operatorType === 'LARGE_OPERATOR' ? '2026-12-30' : '2027-06-30';

    const now = nowUTC();
    return {
      id: uuidv4(),
      supplierId,
      commodity,
      countryOfOrigin: countryOfOrigin.toUpperCase(),
      assessmentDate,
      status: deriveInitialStatus(productionStartDate),
      riskLevel: 'LOW',     // will be set via flag()
      productionStartDate,
      satelliteVerified: false,
      productionPlots,
      countryRiskTier,
      ddsReference,
      operatorType,
      complianceDeadline,
      retentionUntil: addYears(assessmentDate, 5),  // EUDR Art. 10(5)
      isDeleted: false,
      createdAt: now,
      updatedAt: now,
    };
  },

  /**
   * Records satellite and documentary evidence, moves toward COMPLIANT/PENDING_VERIFICATION.
   *
   * @param satelliteData  - Whether remote-sensing / satellite data confirms no deforestation
   * @param documentRef    - Reference to due diligence documentation (e.g. DDS reference number)
   */
  verify(
    assessment: EUDRAssessment,
    satelliteData: boolean,
    documentRef: string,
  ): EUDRAssessment {
    if (assessment.status === 'CLOSED' as string) {
      throw new Error('Cannot verify a closed assessment.');
    }
    if (assessment.status === 'NON_COMPLIANT' && assessment.productionStartDate !== undefined) {
      throw new Error(
        'Assessment is NON_COMPLIANT due to productionStartDate before EUDR cutoff (2020-12-31). ' +
        'Cannot be verified compliant.',
      );
    }

    const newStatus: EUDRStatus =
      satelliteData && documentRef
        ? 'COMPLIANT'
        : 'PENDING_VERIFICATION';

    return {
      ...assessment,
      satelliteVerified: satelliteData,
      documentRef,
      status: newStatus,
      updatedAt: nowUTC(),
    };
  },

  /**
   * Sets or updates the risk level for this assessment.
   * HIGH/MEDIUM risk triggers a satellite verification requirement.
   */
  flag(assessment: EUDRAssessment, riskLevel: EUDRRiskLevel): EUDRAssessment {
    const newStatus: EUDRStatus =
      assessment.status === 'COMPLIANT' && (riskLevel === 'HIGH' || riskLevel === 'MEDIUM')
        ? 'PENDING_VERIFICATION'    // needs re-verification at higher risk level
        : assessment.status;

    return {
      ...assessment,
      riskLevel,
      status: newStatus,
      updatedAt: nowUTC(),
    };
  },

  // ---------------------------------------------------------------------------
  // Predicates
  // ---------------------------------------------------------------------------

  /**
   * Returns true when the assessment risk level is HIGH.
   * Typically used to trigger escalation and enhanced due diligence (Art. 10).
   */
  isHighRisk(assessment: EUDRAssessment): boolean {
    return assessment.riskLevel === 'HIGH';
  },

  /**
   * Satellite verification is required for HIGH and MEDIUM risk assessments
   * per EU EUDR enhanced due diligence obligations (Art. 10).
   */
  requiresSatelliteVerification(assessment: EUDRAssessment): boolean {
    return assessment.riskLevel === 'HIGH' || assessment.riskLevel === 'MEDIUM';
  },

  // ---------------------------------------------------------------------------
  // Reg. 2025/2650 additions
  // ---------------------------------------------------------------------------

  /**
   * Adds a production plot to an assessment per EUDR Art. 3a.
   *
   * Business rules:
   *  - If areaHectares ≥ 4, plotType must be 'POLYGON' (polygon perimeter required).
   *  - Compliant assessments cannot be modified — throws if status === 'COMPLIANT'.
   *  - A new plotId is generated (uuidv4).
   *
   * @throws if assessment.status === 'COMPLIANT'
   * @throws if areaHectares ≥ 4 and plotType !== 'POLYGON'
   */
  addProductionPlot(
    assessment: EUDRAssessment,
    plot: Omit<ProductionPlot, 'plotId'>,
  ): EUDRAssessment {
    if (assessment.status === 'COMPLIANT') {
      throw new Error('Cannot modify a COMPLIANT assessment. Re-open it first.');
    }
    if (plot.areaHectares !== undefined && plot.areaHectares >= 4 && plot.plotType !== 'POLYGON') {
      throw new Error(
        `Plot area is ${plot.areaHectares} ha (≥ 4 ha): plotType must be 'POLYGON' per EUDR Art. 3a.`,
      );
    }

    const newPlot: ProductionPlot = { plotId: uuidv4(), ...plot };
    return {
      ...assessment,
      productionPlots: [...assessment.productionPlots, newPlot],
      updatedAt: nowUTC(),
    };
  },

  /**
   * Records the TRACES NT Due Diligence Statement (DDS) reference number
   * obtained after submitting the DDS to the EU information system.
   *
   * @param ddsReference - Reference number assigned by TRACES NT
   */
  recordDDSSubmission(assessment: EUDRAssessment, ddsReference: string): EUDRAssessment {
    if (!ddsReference) throw new Error('ddsReference is required.');
    return {
      ...assessment,
      ddsReference,
      updatedAt: nowUTC(),
    };
  },

  /**
   * Returns true when the given date is past the assessment's compliance deadline
   * and the assessment has not yet reached COMPLIANT status.
   *
   * Uses string comparison of ISO dates (YYYY-MM-DD), which is lexicographically correct.
   *
   * @param asOf - The date to check against (ISO 8601, e.g. today's date)
   */
  isPastDeadline(assessment: EUDRAssessment, asOf: ISODate): boolean {
    if (assessment.status === 'COMPLIANT') return false;
    return asOf > assessment.complianceDeadline;
  },
};

// Export the HIGH_RISK_COMMODITIES set for use by other modules (e.g. Python interop, views)
export { HIGH_RISK_COMMODITIES, EUDR_CUTOFF_DATE };
