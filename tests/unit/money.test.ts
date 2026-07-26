/**
 * Unit tests — Money core (P5 slice 1, ADR-0019 / ENG-R4 / SCM-R8).
 *
 * Proves the Decimal-backed money helpers: ROUND_HALF_EVEN multiplication (retiring the
 * old `Math.round(amount * factor)` float bug) and sum-preserving allocation.
 */
import {
  money,
  addMoney,
  subtractMoney,
  multiplyMoney,
  allocateMoney,
} from '@scm/shared';

describe('money() construction', () => {
  it('accepts integer minor units', () => {
    expect(money(1250, 'USD')).toEqual({ amount: 1250, currency: 'USD' });
  });
  it('rejects non-integer minor units', () => {
    expect(() => money(12.5, 'USD')).toThrow(/integer cents/);
  });
});

describe('add / subtract', () => {
  it('adds same-currency amounts', () => {
    expect(addMoney(money(1000, 'USD'), money(250, 'USD')).amount).toBe(1250);
  });
  it('subtracts same-currency amounts (credits go negative)', () => {
    expect(subtractMoney(money(1000, 'USD'), money(1500, 'USD')).amount).toBe(-500);
  });
  it('throws on currency mismatch', () => {
    expect(() => addMoney(money(100, 'USD'), money(100, 'EUR'))).toThrow(/mismatch/);
  });
});

describe('multiplyMoney — ROUND_HALF_EVEN, no float drift', () => {
  it('rounds half to even (banker\'s rounding), not half-up', () => {
    // 2.5 -> 2 (even), 3.5 -> 4 (even). Math.round would give 3 and 4.
    expect(multiplyMoney(money(5, 'USD'), 0.5).amount).toBe(2);
    expect(multiplyMoney(money(7, 'USD'), 0.5).amount).toBe(4);
  });
  it('computes a tax rate exactly from a string factor', () => {
    // 19_99 cents * 0.0825 = 164.9175 -> 165 (HALF_EVEN)
    expect(multiplyMoney(money(1999, 'USD'), '0.0825').amount).toBe(165);
  });
  it('avoids the classic 0.1 * 3 float error', () => {
    // 70 * 0.1 = 7 exactly (float would flirt with 7.000000001)
    expect(multiplyMoney(money(70, 'USD'), 0.1).amount).toBe(7);
  });
  it('handles negative amounts (credit notes) symmetrically', () => {
    expect(multiplyMoney(money(-5, 'USD'), 0.5).amount).toBe(-2); // HALF_EVEN toward even
  });
});

describe('allocateMoney — sum-preserving (no lost cents)', () => {
  it('splits 100 three ways with no remainder lost', () => {
    const parts = allocateMoney(money(100, 'USD'), [1, 1, 1]);
    expect(parts.map(p => p.amount)).toEqual([34, 33, 33]);
    expect(parts.reduce((s, p) => s + p.amount, 0)).toBe(100);
  });
  it('allocates by weight and still sums to the whole', () => {
    const parts = allocateMoney(money(1000, 'USD'), [3, 1]); // 750 / 250
    expect(parts.map(p => p.amount)).toEqual([750, 250]);
    expect(parts.reduce((s, p) => s + p.amount, 0)).toBe(1000);
  });
  it('gives leftover units to the largest fractional remainders', () => {
    // 10 across [1,1,1]: raw 3.33 each; floors 3,3,3; leftover 1 -> first share
    const parts = allocateMoney(money(10, 'USD'), [1, 1, 1]);
    expect(parts.map(p => p.amount)).toEqual([4, 3, 3]);
    expect(parts.reduce((s, p) => s + p.amount, 0)).toBe(10);
  });
  it('preserves the sum for negative totals (credits)', () => {
    const parts = allocateMoney(money(-10, 'USD'), [1, 1, 1]);
    expect(parts.reduce((s, p) => s + p.amount, 0)).toBe(-10);
  });
  it('rejects empty, negative, or zero-sum weights', () => {
    expect(() => allocateMoney(money(100, 'USD'), [])).toThrow();
    expect(() => allocateMoney(money(100, 'USD'), [-1, 2])).toThrow();
    expect(() => allocateMoney(money(100, 'USD'), [0, 0])).toThrow();
  });
});
