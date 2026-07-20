/**
 * Unit tests — Safety Stock & Inventory calculations
 * Validated against Chopra & Meindl Ch.11 example values.
 */

import {
  safetyStockByDays,
  safetyStockAverageMax,
  safetyStockStatistical,
  safetyStockCombined,
  reorderPoint,
  economicOrderQuantity,
  coefficientOfVariation,
  classifyXYZ,
  inventoryTurnoverRatio,
  daysInventoryOutstanding,
  getZScore,
} from '@scm/domain/03-demand-planning/algorithms/SafetyStock';

describe('Safety Stock — Days on Hand method', () => {
  it('calculates safety stock correctly', () => {
    expect(safetyStockByDays(100, 5)).toBe(500);
    expect(safetyStockByDays(50.5, 3)).toBe(152); // ceil(151.5)
  });
});

describe('Safety Stock — Statistical Z-score method', () => {
  it('returns correct z-scores for standard service levels', () => {
    expect(getZScore(95)).toBeCloseTo(1.65, 2);
    expect(getZScore(99)).toBeCloseTo(2.33, 2);
    expect(getZScore(90)).toBeCloseTo(1.28, 2);
  });

  it('calculates safety stock at 95% service level', () => {
    // σ_D = 20 units/day, LT = 9 days, SL = 95%
    // ss = 1.65 × 20 × √9 = 1.65 × 20 × 3 = 99
    const ss = safetyStockStatistical(20, 9, 95);
    expect(ss).toBeCloseTo(99, 0);
  });
});

describe('Safety Stock — Combined demand+lead time variability', () => {
  it('handles zero lead time variance', () => {
    const ss = safetyStockCombined(100, 20, 7, 0, 95);
    // When σ_LT = 0, reduces to: z × σ_D × √LT
    const expected = Math.ceil(1.65 * 20 * Math.sqrt(7));
    expect(ss).toBe(expected);
  });

  it('increases with higher lead time variability', () => {
    const ss1 = safetyStockCombined(100, 20, 7, 0, 95);
    const ss2 = safetyStockCombined(100, 20, 7, 2, 95);
    expect(ss2).toBeGreaterThan(ss1);
  });
});

describe('Reorder Point', () => {
  it('calculates ROP correctly', () => {
    // avg demand 50/day, LT 4 days, SS 100
    // ROP = 50×4 + 100 = 300
    expect(reorderPoint(50, 4, 100)).toBe(300);
  });
});

describe('Economic Order Quantity (EOQ)', () => {
  it('calculates EOQ correctly', () => {
    // D=1000, S=$50 order cost, H=$5 holding cost
    // EOQ = √(2×1000×5000 / 500) = √(20000) ≈ 141.4 → ceil = 142
    const eoq = economicOrderQuantity(1000, 5000, 500);
    expect(eoq).toBeCloseTo(142, 0);
  });

  it('throws for zero holding cost', () => {
    expect(() => economicOrderQuantity(1000, 5000, 0)).toThrow();
  });
});

describe('ABC-XYZ classification', () => {
  it('classifies CV correctly', () => {
    expect(classifyXYZ(0.05)).toBe('X');  // CV < 10%
    expect(classifyXYZ(0.15)).toBe('Y');  // 10-25%
    expect(classifyXYZ(0.30)).toBe('Z');  // >25%
  });

  it('calculates CV correctly', () => {
    expect(coefficientOfVariation(10, 100)).toBeCloseTo(0.10, 5);
    expect(coefficientOfVariation(0, 50)).toBe(0);
  });
});

describe('Inventory Turnover & DIO', () => {
  it('calculates turnover ratio correctly', () => {
    // COGS $1,200,000 / avg inventory $200,000 = 6×
    expect(inventoryTurnoverRatio(120000000, 20000000)).toBeCloseTo(6, 5);
  });

  it('calculates DIO correctly', () => {
    // 365 / 6 ≈ 60.8 days
    expect(daysInventoryOutstanding(6)).toBeCloseTo(60.83, 1);
  });
});
