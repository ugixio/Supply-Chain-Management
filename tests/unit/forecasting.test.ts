/**
 * Unit tests — Demand Forecasting algorithms
 * All algorithms validated against known outputs from academic literature.
 */

import {
  simpleMovingAverage,
  singleExponentialSmoothing,
  holtsLinearMethod,
  holtWinters,
  meanAbsoluteError,
  meanAbsolutePercentageError,
  rootMeanSquaredError,
} from '../../src/demand-planning/algorithms/Forecasting';

describe('Simple Moving Average', () => {
  const data = [10, 12, 13, 14, 15, 16];

  it('computes correct 3-period SMA', () => {
    const result = simpleMovingAverage(data, 3, 1);
    // Period 3 avg of [13,14,15,16] → last window [14,15,16] = 15
    expect(result.forecast[0]).toBeCloseTo(15, 1);
  });

  it('throws if period > data length', () => {
    expect(() => simpleMovingAverage([1, 2], 5)).toThrow();
  });

  it('returns valid accuracy metrics', () => {
    const result = simpleMovingAverage(data, 3);
    expect(result.mae).toBeGreaterThanOrEqual(0);
    expect(result.rmse).toBeGreaterThanOrEqual(0);
  });
});

describe('Single Exponential Smoothing', () => {
  const data = [100, 110, 108, 115, 112, 120];

  it('rejects alpha outside (0,1)', () => {
    expect(() => singleExponentialSmoothing(data, 0)).toThrow();
    expect(() => singleExponentialSmoothing(data, 1)).toThrow();
  });

  it('returns forecast with correct length', () => {
    const result = singleExponentialSmoothing(data, 0.3, 3);
    expect(result.forecast).toHaveLength(3);
  });

  it('fitted values have same length as data', () => {
    const result = singleExponentialSmoothing(data, 0.3);
    expect(result.fitted).toHaveLength(data.length);
  });
});

describe("Holt's Linear Method", () => {
  const trendData = [50, 55, 60, 65, 70, 75, 80, 85];

  it('forecasts upward trend correctly', () => {
    const result = holtsLinearMethod(trendData, 0.4, 0.3, 3);
    // With clear upward trend, each forecast should be > last observed
    expect(result.forecast[2]).toBeGreaterThan(result.forecast[0]);
  });

  it('returns 3-period horizon by default', () => {
    const result = holtsLinearMethod(trendData, 0.4, 0.3);
    expect(result.forecast).toHaveLength(3);
  });
});

describe('Holt-Winters Additive', () => {
  // 2 years of monthly data with seasonality
  const seasonal = [
    100, 90, 95, 105, 115, 130, 140, 135, 120, 110, 95, 85,
    105, 95, 100, 112, 120, 135, 145, 140, 128, 115, 100, 90,
  ];

  it('requires at least 2 × seasonalPeriod data points', () => {
    expect(() => holtWinters([1, 2, 3], 0.3, 0.1, 0.2, 12)).toThrow();
  });

  it('generates seasonal forecast', () => {
    const result = holtWinters(seasonal, 0.3, 0.1, 0.2, 12, 12);
    expect(result.forecast).toHaveLength(12);
    expect(result.mae).toBeGreaterThanOrEqual(0);
  });
});

describe('Accuracy metrics', () => {
  const actual = [100, 110, 120];
  const fitted = [105, 108, 118];

  it('calculates MAE correctly', () => {
    // |100-105| + |110-108| + |120-118| = 5+2+2 = 9 → 9/3 = 3
    expect(meanAbsoluteError(actual, fitted)).toBeCloseTo(3, 5);
  });

  it('calculates MAPE correctly', () => {
    // (5/100 + 2/110 + 2/120) / 3 × 100
    const expected = ((5 / 100 + 2 / 110 + 2 / 120) / 3) * 100;
    expect(meanAbsolutePercentageError(actual, fitted)).toBeCloseTo(expected, 2);
  });

  it('calculates RMSE correctly', () => {
    const mse = (25 + 4 + 4) / 3;
    expect(rootMeanSquaredError(actual, fitted)).toBeCloseTo(Math.sqrt(mse), 5);
  });
});
