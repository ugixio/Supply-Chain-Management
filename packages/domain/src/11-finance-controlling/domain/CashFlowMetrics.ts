/**
 * Cash-to-Cash Cycle and working capital metrics for supply chain finance.
 *
 * Cash-to-Cash Cycle (C2C) = DIO + DSO - DPO
 *   DIO = Days Inventory Outstanding = 365 / Inventory Turnover
 *   DSO = Days Sales Outstanding = AR / (Revenue / 365)
 *   DPO = Days Payable Outstanding = AP / (COGS / 365)
 *
 * Negative C2C (e.g. Amazon, Dell) = business financed by suppliers
 *
 * References:
 *  - Chopra & Meindl Ch.1 — Supply chain performance metrics
 *  - Gartner SCM Top 25 Methodology (2026): 50% financial metrics weight
 *    - Fixed asset utilization (ROPA)
 *    - Working capital (inventory as % of revenue)
 *    - Profitable growth (revenue growth + gross margin)
 */

export type WorkingCapitalSnapshot = {
  periodEnd: string;     // ISO date
  // Balance sheet inputs (in cents)
  accountsReceivableCents: number;
  inventoryCents: number;
  accountsPayableCents: number;
  // P&L inputs
  revenueCents: number;
  cogsCents: number;
  // Calculated metrics
  dso: number;           // Days Sales Outstanding
  dio: number;           // Days Inventory Outstanding
  dpo: number;           // Days Payable Outstanding
  cashToCashDays: number;
  inventoryTurnover: number;
  grossMarginPct: number;
};

export function calculateWorkingCapitalMetrics(input: {
  periodEnd: string;
  accountsReceivableCents: number;
  inventoryCents: number;
  accountsPayableCents: number;
  revenueCents: number;
  cogsCents: number;
}): WorkingCapitalSnapshot {
  const {
    periodEnd, accountsReceivableCents, inventoryCents,
    accountsPayableCents, revenueCents, cogsCents,
  } = input;

  const dso = revenueCents === 0 ? 0
    : (accountsReceivableCents / revenueCents) * 365;

  const inventoryTurnover = inventoryCents === 0 ? 0
    : cogsCents / inventoryCents;

  const dio = inventoryTurnover === 0 ? 0 : 365 / inventoryTurnover;

  const dpo = cogsCents === 0 ? 0
    : (accountsPayableCents / cogsCents) * 365;

  const cashToCashDays = dio + dso - dpo;

  const grossMarginPct = revenueCents === 0 ? 0
    : ((revenueCents - cogsCents) / revenueCents) * 100;

  return {
    periodEnd, accountsReceivableCents, inventoryCents, accountsPayableCents,
    revenueCents, cogsCents, dso, dio, dpo, cashToCashDays, inventoryTurnover, grossMarginPct,
  };
}

export function classifyCashCycle(days: number): 'EXCELLENT' | 'GOOD' | 'AVERAGE' | 'POOR' {
  if (days < 0)  return 'EXCELLENT'; // Supplier-financed
  if (days < 20) return 'GOOD';
  if (days < 45) return 'AVERAGE';
  return 'POOR';
}
