/**
 * Tier 2 ESG Cascade — propagating ESG requirements to supplier's suppliers.
 *
 * Many sustainability risks and Scope 3 emissions reside in Tier 2 and beyond.
 * This aggregate tracks the cascade of ESG data requests from a Tier 1 supplier
 * (directly contracted) down to their Tier 2 suppliers (indirectly contracted).
 *
 * Supported frameworks:
 *  - EU CSDDD 2024/1760 Art. 7–9 — indirect business relationships
 *  - GHG Protocol Scope 3 Cat. 1 — purchased goods from Tier 2 suppliers
 *  - Science Based Targets initiative (SBTi) — value chain engagement
 *  - CDP Supply Chain Program — engagement and data collection
 *
 * Business context:
 *  Tier 2 identity may be unknown initially (supplierId = undefined).
 *  The cascade request is sent via Tier 1 who forwards it downstream.
 *  Coverage rate (% of Tier 2 spend with ESG data) is a key KPI.
 *
 * References:
 *  - EU CSDDD Art. 7 (actual adverse impact) & Art. 8 (mitigation)
 *  - GHG Protocol Scope 3 Standard (2011) Ch. 5 — Data Quality
 *  - SBTi Corporate Manual v2.0 — Value chain engagement
 *  - CDP Guidance for Companies — Supply Chain Module
 */

import { v4 as uuidv4 } from 'uuid';
import { ISOTimestamp, nowUTC } from '@scm/shared/types';

export type CascadeStatus =
  | 'PENDING'
  | 'SENT'
  | 'ACKNOWLEDGED'
  | 'DATA_RECEIVED'
  | 'ASSESSED'
  | 'ESCALATED';

export type Tier2ESGCascade = {
  readonly id: string;
  readonly tier1SupplierId: string;
  /** May be undefined when Tier 2 identity is unknown — discovered via Tier 1. */
  readonly tier2SupplierId?: string;
  readonly tier2SupplierName: string;
  readonly tier2Country: string;
  readonly commodity?: string;
  /** Annual spend with this Tier 2 supplier in integer cents. */
  readonly spendCents?: number;
  status: CascadeStatus;
  readonly requestedAt: ISOTimestamp;
  acknowledgedAt?: ISOTimestamp;
  dataReceivedAt?: ISOTimestamp;
  /** ESG score supplied by Tier 2 (0–100). */
  esgScore?: number;
  riskLevel?: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  /** GHG Scope 3 emissions in tonnes CO2e — reported by Tier 2. */
  scope3EmissionsTco2e?: number;
  /** Action plan required when riskLevel is HIGH or CRITICAL. */
  actionRequired?: string;
  readonly isDeleted: boolean;
  readonly createdAt: ISOTimestamp;
  updatedAt: ISOTimestamp;
};

// ---------------------------------------------------------------------------
// Factory + state transitions (namespace pattern, consistent with other domains)
// ---------------------------------------------------------------------------

export const Tier2ESGCascade = {
  /**
   * Initiates a new Tier 2 ESG cascade request.
   *
   * @param tier1SupplierId   - Tier 1 supplier responsible for forwarding
   * @param tier2SupplierName - Name of the Tier 2 supplier (may be the only known identifier)
   * @param tier2Country      - Country where Tier 2 supplier operates (ISO 3166-1 alpha-2)
   * @param commodity         - Commodity or category procured from Tier 2 (optional)
   */
  initiate(
    tier1SupplierId: string,
    tier2SupplierName: string,
    tier2Country: string,
    commodity?: string,
  ): Tier2ESGCascade {
    if (!tier1SupplierId) throw new Error('tier1SupplierId is required.');
    if (!tier2SupplierName) throw new Error('tier2SupplierName is required.');
    if (!tier2Country) throw new Error('tier2Country is required.');

    const now = nowUTC();
    return {
      id: uuidv4(),
      tier1SupplierId,
      tier2SupplierName,
      tier2Country,
      commodity,
      status: 'PENDING',
      requestedAt: now,
      isDeleted: false,
      createdAt: now,
      updatedAt: now,
    };
  },

  // ---------------------------------------------------------------------------
  // State transitions
  // ---------------------------------------------------------------------------

  /**
   * Records acknowledgment from Tier 2 supplier (via Tier 1 intermediary).
   * Transitions SENT → ACKNOWLEDGED.
   */
  acknowledge(cascade: Tier2ESGCascade): Tier2ESGCascade {
    if (cascade.status !== 'SENT' && cascade.status !== 'PENDING') {
      throw new Error(
        `Cannot acknowledge cascade in status ${cascade.status}. Expected PENDING or SENT.`,
      );
    }
    return {
      ...cascade,
      status: 'ACKNOWLEDGED',
      acknowledgedAt: nowUTC(),
      updatedAt: nowUTC(),
    };
  },

  /**
   * Records receipt of ESG data from Tier 2 supplier.
   *
   * @param esgScore          - Self-reported ESG score (0–100)
   * @param scope3EmissionsTco2e - Reported Scope 3 emissions in tonnes CO2e (optional)
   *
   * Transitions ACKNOWLEDGED → DATA_RECEIVED.
   */
  receiveData(
    cascade: Tier2ESGCascade,
    esgScore: number,
    scope3EmissionsTco2e?: number,
  ): Tier2ESGCascade {
    if (cascade.status !== 'ACKNOWLEDGED') {
      throw new Error(
        `Cannot receive data for cascade in status ${cascade.status}. Expected ACKNOWLEDGED.`,
      );
    }
    if (esgScore < 0 || esgScore > 100) {
      throw new Error(`esgScore must be between 0 and 100, got ${esgScore}.`);
    }

    return {
      ...cascade,
      status: 'DATA_RECEIVED',
      esgScore,
      scope3EmissionsTco2e,
      dataReceivedAt: nowUTC(),
      updatedAt: nowUTC(),
    };
  },

  /**
   * Records the assessment outcome after reviewing Tier 2 ESG data.
   *
   * @param riskLevel      - Assessed risk level for this Tier 2 relationship
   * @param actionRequired - Remediation plan required for HIGH/CRITICAL risk (optional)
   *
   * Transitions DATA_RECEIVED → ASSESSED (or ESCALATED for CRITICAL risk).
   */
  assess(
    cascade: Tier2ESGCascade,
    riskLevel: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL',
    actionRequired?: string,
  ): Tier2ESGCascade {
    if (cascade.status !== 'DATA_RECEIVED' && cascade.status !== 'ACKNOWLEDGED') {
      throw new Error(
        `Cannot assess cascade in status ${cascade.status}. Expected DATA_RECEIVED or ACKNOWLEDGED.`,
      );
    }
    if ((riskLevel === 'HIGH' || riskLevel === 'CRITICAL') && !actionRequired) {
      throw new Error(
        `actionRequired must be provided when riskLevel is ${riskLevel} (EU CSDDD Art. 8 — mitigation obligation).`,
      );
    }

    const newStatus: CascadeStatus = riskLevel === 'CRITICAL' ? 'ESCALATED' : 'ASSESSED';
    return {
      ...cascade,
      status: newStatus,
      riskLevel,
      actionRequired,
      updatedAt: nowUTC(),
    };
  },
};
