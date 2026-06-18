/**
 * DemandSensingRun — aggregate tracking each demand sensing model execution.
 *
 * Demand sensing uses short-horizon ML models (LightGBM, Prophet) to refine
 * the 1–4 week forecast with real-time signals. One DemandSensingRun is created
 * per algorithm execution per SKU; the best-performing model is marked via
 * isSelected.
 *
 * Corresponds to: python/03_demand_planning/demand_sensing.py
 * SQL table:       demand_planning.forecast_runs  (algorithm IN ('LIGHTGBM','PROPHET','ENSEMBLE'))
 *
 * References:
 *  - Gilliland (2010) The Business Forecasting Deal
 *  - Chopra & Meindl (2016) Ch.7 — Demand Management
 *  - Taylor & Letham (2018) The American Statistician 72(1)
 *  - Timmermann (2006) Handbook of Economic Forecasting — ensemble methods
 */

import { v4 as uuidv4 } from 'uuid';
import { ISOTimestamp, nowUTC } from '../../../shared/types';

// ─── Status ───────────────────────────────────────────────────────────────────

export type DemandSensingRunStatus =
  | 'RUNNING'    // model is being trained / predicting
  | 'COMPLETE'   // successfully produced a forecast
  | 'FAILED';    // model execution failed (see errorMessage)

// ─── Algorithm ───────────────────────────────────────────────────────────────

export type DemandSensingAlgorithm =
  | 'LIGHTGBM'      // gradient-boosted trees with lag + calendar features
  | 'PROPHET'       // Facebook Prophet — trend + seasonality + regressors
  | 'ENSEMBLE'      // weighted blend: LightGBM(40%) + Prophet(35%) + stat(25%)
  | 'HOLT_WINTERS'; // statistical baseline (from Forecasting.ts / forecasting.py)

// ─── Aggregate type ───────────────────────────────────────────────────────────

export type DemandSensingRun = {
  readonly id: string;
  readonly skuId: string;
  readonly algorithm: DemandSensingAlgorithm;
  /**
   * Number of forward weeks this run is forecasting (1-4).
   * Short-horizon demand sensing per Gilliland (2010) and SCOR-DS Plan process.
   */
  readonly horizonWeeks: number;
  readonly runAt: ISOTimestamp;

  // ── Accuracy metrics (populated on COMPLETE) ──────────────────────────────
  /**
   * Mean Absolute Percentage Error (%). Mandatory per CLAUDE.md KPI standards.
   * World-class demand sensing MAPE target: < 10% for fast-moving SKUs.
   */
  readonly mape?: number;
  /** Mean Absolute Error in demand units. */
  readonly mae?: number;
  /** Root Mean Squared Error. */
  readonly rmse?: number;

  // ── Forecast output ───────────────────────────────────────────────────────
  /**
   * Per-period forecast quantities (length === horizonWeeks on COMPLETE).
   * All values are non-negative. Units follow the SKU's GS1 UOM code.
   */
  readonly forecast: number[];

  /**
   * LightGBM feature importance scores (gain) by feature name.
   * Only populated when algorithm === 'LIGHTGBM' or 'ENSEMBLE'.
   * Key: feature name (e.g. "lag_1", "rolling_mean_4").
   * Value: gain score (higher = more predictive).
   */
  readonly featureImportance?: Record<string, number>;

  // ── Lifecycle ─────────────────────────────────────────────────────────────
  readonly status: DemandSensingRunStatus;
  /** Error message when status === 'FAILED'. */
  readonly errorMessage?: string;
  /**
   * True when this run is the selected best model for this SKU.
   * Only one run per (skuId, horizonWeeks) should have isSelected = true.
   * select() enforces this at the aggregate level; the calling service must
   * unset previous selections in the repository.
   */
  readonly isSelected: boolean;

  readonly createdAt: ISOTimestamp;
};

// ─── Factory & Methods (namespace pattern) ────────────────────────────────────

export namespace DemandSensingRun {
  /**
   * Create a new DemandSensingRun in RUNNING status.
   * Call complete() or fail() after the Python model execution returns.
   */
  export function create(
    skuId: string,
    algorithm: DemandSensingAlgorithm,
    horizonWeeks: number,
  ): DemandSensingRun {
    if (horizonWeeks < 1 || horizonWeeks > 4) {
      throw new Error(
        `horizonWeeks must be 1–4 for short-horizon demand sensing, got ${horizonWeeks}`,
      );
    }

    const now = nowUTC();
    return {
      id: uuidv4(),
      skuId,
      algorithm,
      horizonWeeks,
      runAt: now,
      forecast: [],
      status: 'RUNNING',
      isSelected: false,
      createdAt: now,
    };
  }

  /**
   * Transition to COMPLETE, recording forecast output and accuracy metrics.
   *
   * @param run     - The run in RUNNING status.
   * @param forecast - Per-period predicted quantities (must have horizonWeeks entries).
   * @param mape    - Mean Absolute Percentage Error from holdout evaluation.
   * @param mae     - Mean Absolute Error from holdout evaluation.
   * @param rmse    - Root Mean Squared Error (optional; from holdout evaluation).
   * @param featureImportance - LightGBM gain scores per feature (optional).
   */
  export function complete(
    run: DemandSensingRun,
    forecast: number[],
    mape: number,
    mae: number,
    rmse?: number,
    featureImportance?: Record<string, number>,
  ): DemandSensingRun {
    if (run.status !== 'RUNNING') {
      throw new Error(
        `Cannot complete a run in status ${run.status} — must be RUNNING`,
      );
    }
    if (forecast.length !== run.horizonWeeks) {
      throw new Error(
        `Forecast length (${forecast.length}) must equal horizonWeeks (${run.horizonWeeks})`,
      );
    }
    if (forecast.some(v => v < 0)) {
      throw new Error('Forecast values must be non-negative');
    }
    if (mape < 0) {
      throw new Error(`mape must be non-negative, got ${mape}`);
    }
    if (mae < 0) {
      throw new Error(`mae must be non-negative, got ${mae}`);
    }

    return {
      ...run,
      status: 'COMPLETE',
      forecast: forecast.map(v => Math.round(v * 100) / 100), // 2 d.p.
      mape,
      mae,
      ...(rmse !== undefined ? { rmse } : {}),
      ...(featureImportance ? { featureImportance } : {}),
    };
  }

  /**
   * Transition to FAILED, recording the error reason.
   * Forecast remains empty; metrics are not set.
   */
  export function fail(run: DemandSensingRun, errorMessage: string): DemandSensingRun {
    if (run.status !== 'RUNNING') {
      throw new Error(
        `Cannot fail a run in status ${run.status} — must be RUNNING`,
      );
    }
    if (!errorMessage.trim()) {
      throw new Error('errorMessage must not be empty');
    }

    return {
      ...run,
      status: 'FAILED',
      errorMessage,
    };
  }

  /**
   * Mark this run as the selected best model for its SKU + horizonWeeks.
   * The calling service must ensure no other run for the same (skuId, horizonWeeks)
   * has isSelected = true (enforce via repository upsert or SQL partial index).
   */
  export function select(run: DemandSensingRun): DemandSensingRun {
    if (run.status !== 'COMPLETE') {
      throw new Error(
        `Cannot select a run in status ${run.status} — only COMPLETE runs may be selected`,
      );
    }

    return {
      ...run,
      isSelected: true,
    };
  }

  /**
   * Deselect a previously selected run (called before selecting a newer run).
   */
  export function deselect(run: DemandSensingRun): DemandSensingRun {
    return {
      ...run,
      isSelected: false,
    };
  }
}
