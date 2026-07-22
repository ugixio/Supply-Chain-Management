/**
 * Unit tests — Supplier Scorecard KPI calculation
 */

import {
  calculateKPIs,
  createScorecard,
  DeliveryMetrics,
  QualityMetrics,
  CommercialMetrics,
} from '@scm/domain/02-supplier-management/domain/SupplierScorecard';

const perfectDelivery: DeliveryMetrics = {
  totalDeliveries: 100,
  onTimeDeliveries: 100,
  inFullDeliveries: 100,
  onTimeInFullDeliveries: 100,
  rightFirstTimeDeliveries: 100,
};

const goodDelivery: DeliveryMetrics = {
  totalDeliveries: 100,
  onTimeDeliveries: 95,
  inFullDeliveries: 97,
  onTimeInFullDeliveries: 93,
  rightFirstTimeDeliveries: 96,
};

const perfectQuality: QualityMetrics = {
  totalUnitsReceived: 10000,
  defectiveUnits: 0,
  ncrCount: 0,
  criticalDefects: 0,
};

const poorQuality: QualityMetrics = {
  totalUnitsReceived: 10000,
  defectiveUnits: 150,
  ncrCount: 5,
  criticalDefects: 2,
};

const perfectCommercial: CommercialMetrics = {
  totalInvoices: 50,
  accurateInvoices: 50,
  totalPOValue: 10000000,
  invoicedValue: 10000000,
  creditNotesRaised: 0,
};

describe('KPI calculations', () => {
  it('scores perfect supplier at 100', () => {
    const kpis = calculateKPIs(perfectDelivery, perfectQuality, perfectCommercial, 100);
    expect(kpis.otd).toBe(100);
    expect(kpis.otif).toBe(100);
    expect(kpis.ppm).toBe(0);
    expect(kpis.overallScore).toBeCloseTo(100, 0);
    expect(kpis.rating).toBe('PREFERRED');
  });

  it('calculates PPM correctly', () => {
    const kpis = calculateKPIs(goodDelivery, poorQuality, perfectCommercial, 80);
    // 150 defects / 10000 units × 1M = 15000 PPM
    expect(kpis.ppm).toBeCloseTo(15000, 0);
  });

  it('assigns PROBATION for low score', () => {
    const kpis = calculateKPIs(
      { ...goodDelivery, onTimeDeliveries: 50, onTimeInFullDeliveries: 40 },
      poorQuality,
      { ...perfectCommercial, accurateInvoices: 20 },
      30,
    );
    expect(['PROBATION', 'DISQUALIFIED']).toContain(kpis.rating);
  });

  it('flags corrective action plan when score < 75', () => {
    const card = createScorecard({
      supplierId: 'SUP-001',
      periodStart: '2026-01-01',
      periodEnd: '2026-03-31',
      delivery: { ...goodDelivery, onTimeDeliveries: 50, onTimeInFullDeliveries: 45 },
      quality: poorQuality,
      commercial: { ...perfectCommercial, accurateInvoices: 25 },
      softScore: 40,
      assessedBy: 'procurement@company.com',
    });
    expect(card.correctionActionPlanRequired).toBe(true);
  });
});
