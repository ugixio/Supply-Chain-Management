/**
 * Safety stock and reorder point calculation algorithms.
 *
 * Methods implemented (in order of sophistication):
 *  1. Days-on-hand method (simple, fast)
 *  2. Average-Max method
 *  3. Statistical Z-score method (recommended — accounts for service level)
 *  4. Combined demand + lead time variability method (most accurate)
 *
 * Formulas from:
 *  - Chopra & Meindl Ch.11 "Safety Inventory Determination"
 *    Formula: ss = z_α · σ_LT where σ_LT = σ_D · √LT (demand std dev × sqrt lead time)
 *  - APICS CPIM 9.0 — Inventory Management module
 *  - Silver, Pyke & Peterson "Inventory Management and Production Planning"
 */

// ─── Service level z-scores (standard normal distribution) ───────────────────
export const SERVICE_LEVEL_Z_SCORES: Record<number, number> = {
  80: 0.84,
  85: 1.04,
  90: 1.28,
  91: 1.34,
  92: 1.41,
  93: 1.48,
  94: 1.55,
  95: 1.65,
  96: 1.75,
  97: 1.88,
  98: 2.05,
  99: 2.33,
  99.5: 2.58,
  99.9: 3.09,
};

export function getZScore(serviceLevelPercent: number): number {
  const z = SERVICE_LEVEL_Z_SCORES[serviceLevelPercent];
  if (z === undefined) {
    // Linear interpolation for non-standard service levels
    const levels = Object.keys(SERVICE_LEVEL_Z_SCORES).map(Number).sort((a, b) => a - b);
    const lower = levels.filter(l => l <= serviceLevelPercent).at(-1);
    const upper = levels.find(l => l > serviceLevelPercent);
    if (!lower || !upper) throw new Error(`Service level ${serviceLevelPercent}% out of supported range`);
    const ratio = (serviceLevelPercent - lower) / (upper - lower);
    return SERVICE_LEVEL_Z_SCORES[lower] + ratio * (SERVICE_LEVEL_Z_SCORES[upper] - SERVICE_LEVEL_Z_SCORES[lower]);
  }
  return z;
}

// ─── Method 1: Days-on-Hand ───────────────────────────────────────────────────
export function safetyStockByDays(avgDailyDemand: number, safetyDays: number): number {
  return Math.ceil(avgDailyDemand * safetyDays);
}

// ─── Method 2: Average-Max ────────────────────────────────────────────────────
export function safetyStockAverageMax(
  maxLeadTimeDays: number,
  maxDailyDemand: number,
  avgLeadTimeDays: number,
  avgDailyDemand: number,
): number {
  return Math.ceil(
    maxLeadTimeDays * maxDailyDemand - avgLeadTimeDays * avgDailyDemand,
  );
}

// ─── Method 3: Statistical Z-score (demand variability only) ─────────────────
// Formula: ss = z · σ_D · √LT
// Assumption: lead time is constant; only demand varies
export function safetyStockStatistical(
  demandStdDev: number,       // σ_D standard deviation of daily demand
  avgLeadTimeDays: number,    // LT in days
  serviceLevelPercent: number,
): number {
  const z = getZScore(serviceLevelPercent);
  return Math.ceil(z * demandStdDev * Math.sqrt(avgLeadTimeDays));
}

// ─── Method 4: Combined demand + lead time variability (recommended) ──────────
// Formula: ss = z · √(LT · σ_D² + D_avg² · σ_LT²)
// Source: Chopra & Meindl, Chapter 11, Equation 11.5
export function safetyStockCombined(
  avgDailyDemand: number,
  demandStdDev: number,       // σ_D
  avgLeadTimeDays: number,    // avg LT
  leadTimeStdDev: number,     // σ_LT (variability of lead time)
  serviceLevelPercent: number,
): number {
  const z = getZScore(serviceLevelPercent);
  const variance =
    avgLeadTimeDays * Math.pow(demandStdDev, 2) +
    Math.pow(avgDailyDemand, 2) * Math.pow(leadTimeStdDev, 2);
  return Math.ceil(z * Math.sqrt(variance));
}

// ─── Reorder Point ────────────────────────────────────────────────────────────
// ROP = (avg daily demand × avg lead time days) + safety stock
export function reorderPoint(
  avgDailyDemand: number,
  avgLeadTimeDays: number,
  safetyStock: number,
): number {
  return Math.ceil(avgDailyDemand * avgLeadTimeDays) + safetyStock;
}

// ─── Economic Order Quantity (EOQ) ────────────────────────────────────────────
// Formula: EOQ = √(2·D·S / H)
// D = annual demand, S = order cost, H = annual holding cost per unit
// Source: Harris (1913), popularized by Wilson (1934)
export function economicOrderQuantity(
  annualDemand: number,
  orderCostCents: number,   // cost per order placed
  holdingCostCents: number, // annual holding cost per unit
): number {
  if (holdingCostCents <= 0) throw new Error('Holding cost must be positive');
  return Math.ceil(Math.sqrt((2 * annualDemand * orderCostCents) / holdingCostCents));
}

// ─── Coefficient of Variation (demand predictability) ────────────────────────
export function coefficientOfVariation(stdDev: number, mean: number): number {
  if (mean === 0) return Infinity;
  return stdDev / mean;
}

export function classifyXYZ(cv: number): 'X' | 'Y' | 'Z' {
  if (cv < 0.10) return 'X'; // stable
  if (cv < 0.25) return 'Y'; // moderate
  return 'Z';                 // erratic
}

// ─── Inventory Turnover & DIO ─────────────────────────────────────────────────
// Source: Chopra & Meindl Ch.1 — supply chain performance metrics
export function inventoryTurnoverRatio(cogsAnnualCents: number, avgInventoryCents: number): number {
  if (avgInventoryCents === 0) return 0;
  return cogsAnnualCents / avgInventoryCents;
}

export function daysInventoryOutstanding(turnoverRatio: number): number {
  if (turnoverRatio === 0) return Infinity;
  return 365 / turnoverRatio;
}
