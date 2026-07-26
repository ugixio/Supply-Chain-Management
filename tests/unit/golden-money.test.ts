/**
 * U8 golden vectors — TypeScript side.
 *
 * Reads the SAME fixture file as `services/calc/tests/test_golden_money.py`
 * (`tests/golden/money.golden.json`). If the two languages ever disagree on a money
 * calculation, one of these suites goes red — that is the whole point (prevents another
 * a12c114-style silent divergence; ADR-0019 money, ADR-0020 wire).
 */
import { readFileSync } from 'fs';
import { join } from 'path';

import {
  multiplyCents,
  divideCents,
  netOfFeeCents,
  allocateMoney,
  money,
} from '@scm/shared';
import { calculateRefundCents } from '@scm/domain/13-order-management/domain/ReturnAuthorization';

type Golden = {
  multiply_cents: { cents: number; factor: string; expected: number; why: string }[];
  divide_cents: { cents: number; divisor: number; expected: number; why: string }[];
  net_of_fee_cents: { cents: number; fee_pct: string; expected: number; why: string }[];
  allocate_cents: { amount: number; weights: number[]; expected: number[]; why: string }[];
  refund_lines: {
    why: string;
    lines: { qty: number; unit_price_cents: number }[];
    fee_pct: string;
    expected_by_line: number[];
    expected_total: number;
    expected_fees: number;
  }[];
};

const golden: Golden = JSON.parse(
  readFileSync(join(__dirname, '..', 'golden', 'money.golden.json'), 'utf8'),
);

describe('golden vectors — multiplyCents', () => {
  golden.multiply_cents.forEach(v => {
    it(`${v.cents} × ${v.factor} = ${v.expected} (${v.why})`, () => {
      expect(multiplyCents(v.cents, v.factor)).toBe(v.expected);
    });
  });
});

describe('golden vectors — divideCents', () => {
  golden.divide_cents.forEach(v => {
    it(`${v.cents} ÷ ${v.divisor} = ${v.expected} (${v.why})`, () => {
      expect(divideCents(v.cents, v.divisor)).toBe(v.expected);
    });
  });
});

describe('golden vectors — netOfFeeCents', () => {
  golden.net_of_fee_cents.forEach(v => {
    it(`${v.cents} less ${v.fee_pct}% = ${v.expected} (${v.why})`, () => {
      expect(netOfFeeCents(v.cents, v.fee_pct)).toBe(v.expected);
    });
  });
});

describe('golden vectors — allocate (sum-preserving)', () => {
  golden.allocate_cents.forEach(v => {
    it(`${v.amount} over [${v.weights}] = [${v.expected}] (${v.why})`, () => {
      const parts = allocateMoney(money(v.amount, 'USD'), v.weights).map(p => p.amount);
      expect(parts).toEqual(v.expected);
      expect(parts.reduce((s, p) => s + p, 0)).toBe(v.amount);
    });
  });
});

describe('golden vectors — refund (canonical two-step quantization)', () => {
  golden.refund_lines.forEach((v, idx) => {
    it(`case ${idx + 1}: total ${v.expected_total} (${v.why})`, () => {
      const lines = v.lines.map((l, i) => ({
        lineId: `L${i}`,
        skuId: `SKU-${i}`,
        returnQty: l.qty,
        acceptedQty: l.qty,
        unitCreditCents: l.unit_price_cents,
        uom: 'EA' as const,
        reason: 'CUSTOMER_CHANGED_MIND' as const,
      }));
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const total = calculateRefundCents(lines as any, Number(v.fee_pct));
      expect(total).toBe(v.expected_total);
    });
  });
});
