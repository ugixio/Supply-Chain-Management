/**
 * Period-End Close — checklist and state management.
 *
 * Implements a standard financial period-close workflow with gated
 * approval: all checklist items must be complete before the period
 * can be approved, and approval is required before closing.
 *
 * Standard checklist tasks (per IFRS / GAAP close procedures):
 *  1. 3-way match complete
 *  2. Accruals posted
 *  3. Inventory valued
 *  4. FX revaluation
 *  5. Intercompany eliminations
 *  6. Management reports distributed
 *
 * References:
 *  - Bragg, S.M. "Closing the Books" 5th Ed. (Wiley, 2021)
 *  - IAS 1 — Presentation of Financial Statements
 *  - IAS 21 — Effects of Changes in Foreign Exchange Rates
 */

import { v4 as uuidv4 } from 'uuid';
import { ISOTimestamp, nowUTC } from '../../../shared/types';

export type CloseStatus =
  | 'OPEN'
  | 'IN_PROGRESS'
  | 'PENDING_APPROVAL'
  | 'APPROVED'
  | 'CLOSED';

export type CloseCheckItem = {
  task: string;
  completed: boolean;
  completedBy?: string;
  completedAt?: ISOTimestamp;
};

export type PeriodClose = {
  readonly id: string;
  /** First day of the fiscal month — YYYY-MM-DD */
  readonly periodMonth: string;
  readonly fiscalYear: number;
  readonly status: CloseStatus;
  readonly checklist: CloseCheckItem[];
  readonly openedAt: ISOTimestamp;
  readonly closedAt?: ISOTimestamp;
  readonly approvedBy?: string;
  readonly approvedAt?: ISOTimestamp;
  readonly isDeleted: boolean;
  readonly createdAt: ISOTimestamp;
};

const STANDARD_TASKS: string[] = [
  '3-way match complete',
  'Accruals posted',
  'Inventory valued',
  'FX revaluation',
  'Intercompany eliminations',
  'Management reports distributed',
];

export const PeriodClose = {
  /**
   * Factory: open a new period-close record with the standard checklist,
   * all items incomplete.
   */
  open(periodMonth: string, fiscalYear: number): PeriodClose {
    const now = nowUTC();
    const checklist: CloseCheckItem[] = STANDARD_TASKS.map(task => ({ task, completed: false }));
    return {
      id: uuidv4(),
      periodMonth,
      fiscalYear,
      status: 'OPEN',
      checklist,
      openedAt: now,
      isDeleted: false,
      createdAt: now,
    };
  },

  /**
   * Mark a checklist task as complete.
   * Advances status to IN_PROGRESS on first completion.
   * If all tasks are now complete, advances to PENDING_APPROVAL.
   */
  completeTask(periodClose: PeriodClose, task: string, by: string): PeriodClose {
    const now = nowUTC();
    const checklist = periodClose.checklist.map(item =>
      item.task === task
        ? { ...item, completed: true, completedBy: by, completedAt: now }
        : item,
    );

    const allDone = checklist.every(i => i.completed);
    let status: CloseStatus = periodClose.status;

    if (status === 'OPEN') status = 'IN_PROGRESS';
    if (allDone) status = 'PENDING_APPROVAL';

    return { ...periodClose, checklist, status };
  },

  /**
   * Approve the period close.
   * Business rule: all checklist items must be complete before approving.
   */
  approve(periodClose: PeriodClose, by: string): PeriodClose {
    const incomplete = periodClose.checklist.filter(i => !i.completed);
    if (incomplete.length > 0) {
      throw new Error(
        `PeriodClose.approve: ${incomplete.length} checklist task(s) still incomplete — ` +
        incomplete.map(i => `"${i.task}"`).join(', '),
      );
    }
    return {
      ...periodClose,
      status: 'APPROVED',
      approvedBy: by,
      approvedAt: nowUTC(),
    };
  },

  /**
   * Close the period.
   * Business rule: period must be APPROVED before it can be CLOSED.
   */
  close(periodClose: PeriodClose): PeriodClose {
    if (periodClose.status !== 'APPROVED') {
      throw new Error(
        `PeriodClose.close: period must be APPROVED before closing (current: ${periodClose.status})`,
      );
    }
    return {
      ...periodClose,
      status: 'CLOSED',
      closedAt: nowUTC(),
    };
  },
};

/** Percentage of checklist items that have been completed (0–100). */
export function completionPct(periodClose: PeriodClose): number {
  const { checklist } = periodClose;
  if (checklist.length === 0) return 100;
  const done = checklist.filter(i => i.completed).length;
  return Math.round((done / checklist.length) * 100);
}
