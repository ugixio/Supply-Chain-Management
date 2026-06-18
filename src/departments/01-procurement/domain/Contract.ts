/**
 * Contract aggregate — Supply agreements and frame contracts.
 *
 * Types of contracts:
 *  - FRAME_AGREEMENT: long-term master agreement with call-offs
 *  - BLANKET_PO: open PO with periodic releases
 *  - SPOT: one-time purchase
 *  - CONSIGNMENT: supplier-owned stock at buyer's premises
 *  - VMI: Vendor-Managed Inventory agreement
 *
 * References:
 *  - Chopra & Meindl Ch.14 "Sourcing Decisions"
 *  - US UCC Article 2 — contract requirements (quantity must be specified)
 *  - CIPS — Contract management best practice
 */

import { v4 as uuidv4 } from 'uuid';
import { Money, ISODate, ISOTimestamp, nowUTC, Incoterm } from '../../../shared/types';

export type ContractType =
  | 'FRAME_AGREEMENT'  // Master agreement with call-offs
  | 'BLANKET_PO'       // Blanket purchase order with releases
  | 'SPOT'             // One-time / spot purchase
  | 'CONSIGNMENT'      // Supplier owns stock at buyer's site
  | 'VMI'              // Vendor-Managed Inventory
  | 'LONG_TERM_SUPPLY';// Dedicated capacity contract

export type ContractStatus = 'DRAFT' | 'ACTIVE' | 'EXPIRING_SOON' | 'EXPIRED' | 'TERMINATED' | 'SUSPENDED';

export type PriceEscalationClause = {
  indexName: string;    // e.g. 'CPI', 'PPI', 'LME Copper'
  baseIndexValue: number;
  baseDate: ISODate;
  maxEscalationPct: number;   // cap per period
  reviewFrequency: 'MONTHLY' | 'QUARTERLY' | 'ANNUAL';
};

export type ContractLineItem = {
  lineId: string;
  sku: string;
  description: string;
  unitPriceCents: number;   // integer cents
  currency: string;
  minQuantity?: number;
  maxQuantity?: number;
  uom: string;
  leadTimeDays: number;
  qualitySpec?: string;     // spec document reference
};

export type SupplyContract = {
  readonly id: string;
  readonly contractNumber: string;
  readonly type: ContractType;
  readonly status: ContractStatus;
  readonly supplierId: string;
  readonly buyerId: string;
  readonly title: string;
  readonly description?: string;
  readonly effectiveDate: ISODate;
  readonly expiryDate: ISODate;
  readonly autoRenew: boolean;
  readonly renewalNoticeDays: number;   // days before expiry to trigger renewal alert
  readonly incoterm: Incoterm;
  readonly incotermLocation: string;
  readonly paymentTermsDays: number;    // Net 30, Net 60, etc.
  readonly currency: string;
  readonly totalContractValueCents: number;
  readonly lines: ContractLineItem[];
  readonly priceEscalation?: PriceEscalationClause;
  // SLA & penalties
  readonly otdTargetPct: number;         // min OTD in this contract
  readonly qualityTargetPpm: number;     // max PPM allowed
  readonly penaltyPerLateDayCents: number;  // penalty per day late
  readonly terminationForCause: string;  // grounds for immediate termination
  // Compliance
  readonly requiresModernSlaveryStatement: boolean;
  readonly requiresISO9001: boolean;
  readonly requiresCTPatOrAEO: boolean;
  readonly requiresCSDDDCompliance: boolean;
  readonly createdBy: string;
  readonly approvedBy?: string;
  readonly approvedAt?: ISOTimestamp;
  readonly createdAt: ISOTimestamp;
  readonly updatedAt: ISOTimestamp;
  readonly isDeleted: boolean;
};

export function createContract(
  input: Omit<SupplyContract, 'id' | 'contractNumber' | 'status' | 'createdAt' | 'updatedAt' | 'isDeleted'>
): SupplyContract {
  if (input.expiryDate <= input.effectiveDate) {
    throw new Error('Contract expiry must be after effective date');
  }
  if (input.lines.length === 0) {
    throw new Error('Contract must have at least one line item');
  }
  return {
    ...input,
    id: uuidv4(),
    contractNumber: `CTR-${Date.now().toString(36).toUpperCase()}`,
    status: 'DRAFT',
    createdAt: nowUTC(),
    updatedAt: nowUTC(),
    isDeleted: false,
  };
}

export function isExpiringSoon(contract: SupplyContract, daysThreshold = 90): boolean {
  const expiry = new Date(contract.expiryDate);
  const today = new Date();
  const daysLeft = (expiry.getTime() - today.getTime()) / (1000 * 60 * 60 * 24);
  return daysLeft <= daysThreshold && daysLeft > 0;
}

export function activateContract(contract: SupplyContract, approvedBy: string): SupplyContract {
  if (contract.status !== 'DRAFT') throw new Error('Only DRAFT contracts can be activated');
  return {
    ...contract,
    status: 'ACTIVE',
    approvedBy,
    approvedAt: nowUTC(),
    updatedAt: nowUTC(),
  };
}
