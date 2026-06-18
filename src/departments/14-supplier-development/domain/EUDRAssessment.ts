/**
 * EUDR Assessment aggregate — EU Deforestation Regulation 2023/1115 due diligence.
 *
 * The EU Deforestation Regulation (EUDR) requires operators to ensure that
 * regulated commodities placed on the EU market have not caused deforestation
 * or forest degradation and were produced in compliance with the legislation
 * of the country of production.
 *
 * Key provisions implemented:
 *  - Art. 3  — Prohibition on placing non-compliant products on the EU market
 *  - Art. 8  — Operator due diligence obligations
 *  - Art. 10 — Enhanced due diligence for high-risk countries
 *  - Art. 10(5) — 5-year document retention period
 *  - Annex I — List of regulated commodities and derived products
 *
 * EUDR cutoff date: 31 December 2020 — land must not have been deforested
 * after this date. Products from land deforested after 2020-12-31 cannot
 * be imported/placed on the EU market.
 *
 * References:
 *  - EU Regulation 2023/1115 (EUDR)
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
  /** WKT polygon or lat/lon coordinates of production area */
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
   */
  initiate(
    supplierId: string,
    commodity: EUDRCommodity,
    countryOfOrigin: string,
    assessmentDate: ISODate,
    productionStartDate?: ISODate,
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
};

// Export the HIGH_RISK_COMMODITIES set for use by other modules (e.g. Python interop, views)
export { HIGH_RISK_COMMODITIES, EUDR_CUTOFF_DATE };
