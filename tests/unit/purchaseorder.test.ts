/**
 * Unit tests — Purchase Order domain rules
 */

import {
  createPurchaseOrder,
  approvePurchaseOrder,
  rejectPurchaseOrder,
  sendPurchaseOrderToSupplier,
  cancelPurchaseOrder,
  calculatePOTotal,
  PO_APPROVAL_THRESHOLD_CENTS,
} from '../../src/procurement/domain/PurchaseOrder';

const baseLine = {
  sku: 'SKU-001',
  description: 'Test Widget',
  quantity: { value: 100, uom: 'EA' as const },
  unitPrice: { amount: 1000, currency: 'USD' }, // $10.00 each
  deliveryDate: '2026-08-01',
  warehouseId: 'WH-001',
  lotRequired: false,
};

const baseInput = {
  supplierId: 'SUP-001',
  buyerId: 'ORG-001',
  lines: [baseLine],
  currency: 'USD',
  incoterm: 'FCA' as const,
  incotermLocation: 'Chicago, IL',
  requestedDeliveryDate: '2026-08-01',
  createdBy: 'user@example.com',
};

describe('PurchaseOrder creation', () => {
  it('creates PO below threshold as APPROVED directly', () => {
    const po = createPurchaseOrder({ ...baseInput, approvalThresholdCents: 50_000_00 });
    // 100 × $10 = $1,000 < $50,000 threshold → auto-approved
    expect(po.status).toBe('APPROVED');
  });

  it('creates PO above threshold as PENDING_APPROVAL', () => {
    const bigLine = { ...baseLine, quantity: { value: 1000, uom: 'EA' as const } };
    // 1000 × $10 = $10,000 > $5,000 threshold → pending
    const po = createPurchaseOrder({ ...baseInput, lines: [bigLine] });
    expect(po.status).toBe('PENDING_APPROVAL');
  });

  it('throws on empty lines', () => {
    expect(() => createPurchaseOrder({ ...baseInput, lines: [] })).toThrow();
  });

  it('assigns unique PO numbers', () => {
    const po1 = createPurchaseOrder({ ...baseInput });
    const po2 = createPurchaseOrder({ ...baseInput });
    expect(po1.poNumber).not.toBe(po2.poNumber);
  });

  it('stores monetary values as integer cents', () => {
    const po = createPurchaseOrder(baseInput);
    po.lines.forEach(line => {
      expect(Number.isInteger(line.unitPrice.amount)).toBe(true);
    });
  });
});

describe('PurchaseOrder approval workflow', () => {
  const pendingPO = (() => {
    const bigLine = { ...baseLine, quantity: { value: 1000, uom: 'EA' as const } };
    return createPurchaseOrder({ ...baseInput, lines: [bigLine] });
  })();

  it('approves a PENDING_APPROVAL PO', () => {
    const approved = approvePurchaseOrder(pendingPO, 'manager@example.com');
    expect(approved.status).toBe('APPROVED');
    expect(approved.approvedBy).toBe('manager@example.com');
    expect(approved.approvedAt).toBeDefined();
  });

  it('rejects a PENDING_APPROVAL PO', () => {
    const rejected = rejectPurchaseOrder(pendingPO, 'manager@example.com', 'Over budget');
    expect(rejected.status).toBe('REJECTED');
    expect(rejected.rejectionReason).toBe('Over budget');
  });

  it('throws when approving non-pending PO', () => {
    const approved = approvePurchaseOrder(pendingPO, 'mgr@example.com');
    expect(() => approvePurchaseOrder(approved, 'mgr@example.com')).toThrow();
  });
});

describe('PurchaseOrder lifecycle', () => {
  it('can only be sent to supplier when APPROVED', () => {
    const po = createPurchaseOrder({ ...baseInput, approvalThresholdCents: 1_000_00 });
    expect(po.status).toBe('APPROVED');
    const sent = sendPurchaseOrderToSupplier(po);
    expect(sent.status).toBe('SENT_TO_SUPPLIER');
  });

  it('can cancel a DRAFT or APPROVED PO', () => {
    const po = createPurchaseOrder({ ...baseInput, approvalThresholdCents: 1_000_00 });
    const cancelled = cancelPurchaseOrder(po, 'No longer needed');
    expect(cancelled.status).toBe('CANCELLED');
  });
});
