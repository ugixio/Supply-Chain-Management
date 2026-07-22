/**
 * Material Requirements Planning (MRP) domain model.
 *
 * MRP calculates:
 *  - Gross requirements (from MPS/demand)
 *  - Scheduled receipts (open POs)
 *  - Projected on-hand inventory
 *  - Net requirements
 *  - Planned order releases
 *
 * Formula: Net Requirement = Gross Requirement - Projected On-Hand - Scheduled Receipts
 *
 * References:
 *  - Orlicky, J. "Material Requirements Planning" 3rd Ed. (McGraw-Hill, 2022)
 *  - APICS CPIM 9.0 — Plan Supply module
 *  - Chopra & Meindl Ch.10 "Coordinating Supply and Demand"
 */

import { v4 as uuidv4 } from 'uuid';
import { ISODate, ISOTimestamp, nowUTC } from '@scm/shared/types';

export type MRPBucket = {
  period: ISODate;            // week or day (ISO date of period start)
  grossRequirement: number;   // demand from MPS / SO
  scheduledReceipts: number;  // open POs due in this period
  projectedOnHand: number;    // ending inventory after netting
  netRequirement: number;     // Max(0, grossReq - projectedOH - scheduledRec)
  plannedOrderReceipt: number;// planned receipt in this period
  plannedOrderRelease: number;// planned PO to release (= receipt shifted by LT)
};

export type MRPRecord = {
  readonly id: string;
  readonly sku: string;
  readonly lotSize: number;         // minimum order quantity (MOQ) or EOQ
  readonly leadTimeDays: number;
  readonly safetyStockUnits: number;
  readonly openingStock: number;
  readonly buckets: MRPBucket[];
  readonly runDate: ISOTimestamp;
  readonly plannedBy: string;
};

/**
 * Run MRP netting logic for a single SKU over a time horizon.
 * @param sku Item code
 * @param openingStock Current stock on hand
 * @param safetyStock Minimum stock to maintain
 * @param leadTimeDays Replenishment lead time
 * @param lotSize Minimum / fixed order quantity
 * @param grossRequirements Array of [period, demand] tuples
 * @param scheduledReceipts Array of [period, qty] tuples (open POs)
 */
export function runMRP(
  sku: string,
  openingStock: number,
  safetyStock: number,
  leadTimeDays: number,
  lotSize: number,
  grossRequirements: { period: ISODate; qty: number }[],
  scheduledReceipts: { period: ISODate; qty: number }[],
  plannedBy: string,
): MRPRecord {
  const periods = [...new Set(grossRequirements.map(r => r.period))].sort();
  let projectedOH = openingStock;
  const buckets: MRPBucket[] = [];

  for (const period of periods) {
    const grossReq = grossRequirements.filter(r => r.period === period).reduce((s, r) => s + r.qty, 0);
    const schedRec = scheduledReceipts.filter(r => r.period === period).reduce((s, r) => s + r.qty, 0);

    const available = projectedOH + schedRec;
    const netReq = Math.max(0, grossReq + safetyStock - available);

    // Round up to lot size
    const plannedOrderReceipt = netReq > 0 ? Math.ceil(netReq / lotSize) * lotSize : 0;
    projectedOH = available - grossReq + plannedOrderReceipt;

    // Planned order release = planned receipt offset by lead time
    const releaseDate = new Date(period);
    releaseDate.setDate(releaseDate.getDate() - leadTimeDays);
    const releasePeriod = releaseDate.toISOString().substring(0, 10);

    buckets.push({
      period,
      grossRequirement: grossReq,
      scheduledReceipts: schedRec,
      projectedOnHand: projectedOH,
      netRequirement: netReq,
      plannedOrderReceipt,
      plannedOrderRelease: plannedOrderReceipt, // simplified: same qty, earlier date
    });
  }

  return {
    id: uuidv4(),
    sku,
    lotSize,
    leadTimeDays,
    safetyStockUnits: safetyStock,
    openingStock,
    buckets,
    runDate: nowUTC(),
    plannedBy,
  };
}
