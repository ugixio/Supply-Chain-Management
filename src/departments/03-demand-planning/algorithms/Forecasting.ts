/**
 * Demand forecasting algorithms.
 *
 * Algorithms:
 *  1. Simple Moving Average (SMA)
 *  2. Weighted Moving Average (WMA)
 *  3. Single Exponential Smoothing (SES) — Holt 1957
 *  4. Double Exponential Smoothing / Holt's method — trend-adjusted
 *  5. Triple Exponential Smoothing / Holt-Winters — trend + seasonality
 *
 * Accuracy metrics: MAE, MAPE, RMSE (standard forecasting KPIs)
 *
 * References:
 *  - Holt, C.C. (1957) "Forecasting seasonals and trends by exponentially weighted averages"
 *  - Winters, P.R. (1960) "Forecasting sales by exponentially weighted moving averages"
 *  - Chopra & Meindl Ch.7 "Demand Forecasting in a Supply Chain"
 *  - Ballou Ch.8 — demand forecasting methods
 *  - APICS CPIM 9.0 — Fundamentals of Demand Management
 */

export type ForecastResult = {
  fitted: number[];      // in-sample fitted values
  forecast: number[];    // out-of-sample forecast
  mae: number;
  mape: number;
  rmse: number;
  algorithm: string;
  parameters: Record<string, number>;
};

// ─── Accuracy metrics ────────────────────────────────────────────────────────
export function meanAbsoluteError(actual: number[], fitted: number[]): number {
  if (actual.length !== fitted.length || actual.length === 0) throw new Error('Length mismatch');
  return actual.reduce((s, a, i) => s + Math.abs(a - fitted[i]), 0) / actual.length;
}

export function meanAbsolutePercentageError(actual: number[], fitted: number[]): number {
  const nonZero = actual.filter((_, i) => actual[i] !== 0);
  if (nonZero.length === 0) return NaN;
  const sum = actual.reduce((s, a, i) => {
    if (a === 0) return s;
    return s + Math.abs((a - fitted[i]) / a);
  }, 0);
  return (sum / nonZero.length) * 100;
}

export function rootMeanSquaredError(actual: number[], fitted: number[]): number {
  const mse = actual.reduce((s, a, i) => s + Math.pow(a - fitted[i], 2), 0) / actual.length;
  return Math.sqrt(mse);
}

function buildMetrics(actual: number[], fitted: number[], algorithm: string, params: Record<string, number>): ForecastResult {
  return {
    fitted,
    forecast: [],
    mae: meanAbsoluteError(actual, fitted),
    mape: meanAbsolutePercentageError(actual, fitted),
    rmse: rootMeanSquaredError(actual, fitted),
    algorithm,
    parameters: params,
  };
}

// ─── 1. Simple Moving Average ─────────────────────────────────────────────────
export function simpleMovingAverage(
  data: number[],
  period: number,
  horizon = 1,
): ForecastResult {
  if (period > data.length) throw new Error('Period cannot exceed data length');
  const fitted: number[] = new Array(period - 1).fill(NaN);
  for (let i = period - 1; i < data.length; i++) {
    const window = data.slice(i - period + 1, i + 1);
    fitted.push(window.reduce((s, v) => s + v, 0) / period);
  }
  const validActual = data.slice(period - 1);
  const validFitted = fitted.slice(period - 1);

  const lastWindow = data.slice(-period);
  const nextForecast = lastWindow.reduce((s, v) => s + v, 0) / period;
  const forecast = new Array(horizon).fill(nextForecast);

  const base = buildMetrics(validActual, validFitted, 'SMA', { period });
  return { ...base, fitted, forecast };
}

// ─── 2. Single Exponential Smoothing (SES) ───────────────────────────────────
// F_t+1 = α · A_t + (1 - α) · F_t
// α ∈ (0,1); higher α = more weight on recent observations
export function singleExponentialSmoothing(
  data: number[],
  alpha: number,
  horizon = 1,
): ForecastResult {
  if (alpha <= 0 || alpha >= 1) throw new Error('Alpha must be in (0,1)');
  const fitted: number[] = [data[0]];
  for (let i = 1; i < data.length; i++) {
    fitted.push(alpha * data[i - 1] + (1 - alpha) * fitted[i - 1]);
  }
  const lastF = alpha * data[data.length - 1] + (1 - alpha) * fitted[fitted.length - 1];
  const forecast = new Array(horizon).fill(lastF);

  const base = buildMetrics(data.slice(1), fitted.slice(1), 'SES', { alpha });
  return { ...base, fitted, forecast };
}

// ─── 3. Double Exponential Smoothing / Holt's Linear Method ─────────────────
// L_t = α · A_t + (1 - α)(L_{t-1} + T_{t-1})
// T_t = β(L_t - L_{t-1}) + (1 - β) T_{t-1}
// F_{t+h} = L_t + h · T_t
export function holtsLinearMethod(
  data: number[],
  alpha: number,
  beta: number,
  horizon = 3,
): ForecastResult {
  if (alpha <= 0 || alpha >= 1) throw new Error('Alpha must be in (0,1)');
  if (beta <= 0 || beta >= 1) throw new Error('Beta must be in (0,1)');

  let level = data[0];
  let trend = data[1] - data[0];
  const fitted: number[] = [level + trend];

  for (let i = 1; i < data.length; i++) {
    const prevLevel = level;
    level = alpha * data[i] + (1 - alpha) * (prevLevel + trend);
    trend = beta * (level - prevLevel) + (1 - beta) * trend;
    fitted.push(level + trend);
  }

  const forecast = Array.from({ length: horizon }, (_, h) => level + (h + 1) * trend);
  const base = buildMetrics(data.slice(1), fitted.slice(1), 'Holts', { alpha, beta });
  return { ...base, fitted, forecast };
}

// ─── 4. Holt-Winters Triple Exponential Smoothing ───────────────────────────
// Additive model:
//   L_t = α(A_t - S_{t-m}) + (1-α)(L_{t-1} + T_{t-1})
//   T_t = β(L_t - L_{t-1}) + (1-β)T_{t-1}
//   S_t = γ(A_t - L_t) + (1-γ)S_{t-m}
//   F_{t+h} = L_t + h·T_t + S_{t-m+((h-1) mod m)+1}
export function holtWinters(
  data: number[],
  alpha: number,
  beta: number,
  gamma: number,
  seasonalPeriod: number,  // m: 12 = monthly, 4 = quarterly, 52 = weekly
  horizon = seasonalPeriod,
): ForecastResult {
  if (data.length < 2 * seasonalPeriod) {
    throw new Error(`Holt-Winters requires at least ${2 * seasonalPeriod} data points`);
  }

  // Initialize seasonal indices from first full season average
  const firstSeasonAvg = data.slice(0, seasonalPeriod).reduce((s, v) => s + v, 0) / seasonalPeriod;
  const seasonalIndices: number[] = data
    .slice(0, seasonalPeriod)
    .map(v => v - firstSeasonAvg);

  let level = firstSeasonAvg;
  let trend = (
    data.slice(seasonalPeriod, 2 * seasonalPeriod).reduce((s, v) => s + v, 0) -
    data.slice(0, seasonalPeriod).reduce((s, v) => s + v, 0)
  ) / (seasonalPeriod * seasonalPeriod);

  const fitted: number[] = new Array(seasonalPeriod).fill(NaN);
  const allSeasonals: number[] = [...seasonalIndices];

  for (let i = seasonalPeriod; i < data.length; i++) {
    const prevLevel = level;
    const s = allSeasonals[i - seasonalPeriod];
    level = alpha * (data[i] - s) + (1 - alpha) * (prevLevel + trend);
    trend = beta * (level - prevLevel) + (1 - beta) * trend;
    const newS = gamma * (data[i] - level) + (1 - gamma) * s;
    allSeasonals.push(newS);
    fitted.push(level + trend + s);
  }

  const forecast: number[] = [];
  for (let h = 1; h <= horizon; h++) {
    const sIdx = allSeasonals[allSeasonals.length - seasonalPeriod + ((h - 1) % seasonalPeriod)];
    forecast.push(level + h * trend + sIdx);
  }

  const validActual = data.slice(seasonalPeriod);
  const validFitted = fitted.slice(seasonalPeriod);

  const base = buildMetrics(validActual, validFitted, 'Holt-Winters Additive', { alpha, beta, gamma, seasonalPeriod });
  return { ...base, fitted, forecast };
}

// ─── Algorithm selector ───────────────────────────────────────────────────────
export type ForecastAlgorithm = 'SMA' | 'SES' | 'HOLTS' | 'HOLT_WINTERS';

export function selectAlgorithm(
  data: number[],
  hasTrend: boolean,
  hasSeasonality: boolean,
  seasonalPeriod?: number,
): ForecastAlgorithm {
  if (hasSeasonality && seasonalPeriod && data.length >= 2 * seasonalPeriod) {
    return 'HOLT_WINTERS';
  }
  if (hasTrend) return 'HOLTS';
  if (data.length >= 3) return 'SES';
  return 'SMA';
}
