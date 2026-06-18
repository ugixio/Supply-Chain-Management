/**
 * Business Continuity Plan (BCP) for supply chain disruptions.
 *
 * Covers:
 *  - Disruption scenarios with trigger conditions
 *  - Response playbooks with time-bound actions
 *  - Recovery Time Objective (RTO) and Recovery Point Objective (RPO)
 *  - Alternative supplier / routing activations
 *  - Communication trees
 *
 * References:
 *  - ISO 22301:2019 — Business continuity management systems
 *  - McKinsey Supply Chain Resilience Framework (2021)
 *  - MIT CTL Supply Chain Resilience research program
 *  - Chopra & Meindl Ch.12 "Managing Supply Chain Risk"
 */

import { v4 as uuidv4 } from 'uuid';
import { ISODate, ISOTimestamp, nowUTC } from '../../../shared/types';

export type BCPStatus = 'DRAFT' | 'APPROVED' | 'ACTIVE' | 'TESTED' | 'ARCHIVED';

export type DisruptionTrigger = {
  triggerType: 'SUPPLIER_FAILURE' | 'NATURAL_DISASTER' | 'CYBER_ATTACK' |
               'GEOPOLITICAL' | 'LOGISTICS_DISRUPTION' | 'PANDEMIC' | 'QUALITY_RECALL';
  thresholdDescription: string;  // e.g. "Supplier cannot fulfill >30% of demand"
  escalationLevel: 1 | 2 | 3;   // 1=minor, 2=significant, 3=critical
};

export type BCPAction = {
  actionId: string;
  sequenceNumber: number;
  description: string;
  owner: string;            // role / department
  timeframeHours: number;   // time to execute from trigger
  dependsOn: string[];      // actionIds that must complete first
  alternativeSupplierIds?: string[];
  alternativeRoutes?: string[];
  stockReleaseInstructions?: string;
};

export type BCPTest = {
  testId: string;
  testDate: ISODate;
  testType: 'TABLETOP' | 'FUNCTIONAL' | 'FULL_SCALE';
  scenarioTested: string;
  passed: boolean;
  gapsIdentified: string[];
  nextTestDate: ISODate;
  testedBy: string;
};

export type BusinessContinuityPlan = {
  readonly id: string;
  readonly planNumber: string;
  readonly status: BCPStatus;
  readonly title: string;
  readonly scope: string;          // which products/regions/suppliers covered
  readonly trigger: DisruptionTrigger;
  // Recovery objectives (ISO 22301)
  readonly rtoHours: number;       // Recovery Time Objective
  readonly rpoHours: number;       // Recovery Point Objective
  readonly mtpdHours: number;      // Max Tolerable Period of Disruption
  // Response actions
  readonly immediateActions: BCPAction[];    // 0-4 hours
  readonly shortTermActions: BCPAction[];   // 4-72 hours
  readonly longTermActions: BCPAction[];    // 72h+
  // Communication
  readonly escalationContacts: {
    role: string; name: string; email: string; phone: string;
  }[];
  // Testing
  readonly tests: BCPTest[];
  readonly lastTestedDate?: ISODate;
  readonly nextTestDate: ISODate;
  readonly approvedBy?: string;
  readonly effectiveDate: ISODate;
  readonly reviewDate: ISODate;     // annual review
  readonly createdBy: string;
  readonly createdAt: ISOTimestamp;
  readonly updatedAt: ISOTimestamp;
};

export function createBCP(
  input: Omit<BusinessContinuityPlan, 'id' | 'planNumber' | 'status' | 'tests' | 'createdAt' | 'updatedAt'>
): BusinessContinuityPlan {
  return {
    ...input,
    id: uuidv4(),
    planNumber: `BCP-${Date.now().toString(36).toUpperCase()}`,
    status: 'DRAFT',
    tests: [],
    createdAt: nowUTC(),
    updatedAt: nowUTC(),
  };
}

export function addTestResult(bcp: BusinessContinuityPlan, test: Omit<BCPTest, 'testId'>): BusinessContinuityPlan {
  const testWithId: BCPTest = { ...test, testId: uuidv4() };
  return {
    ...bcp,
    tests: [...bcp.tests, testWithId],
    lastTestedDate: test.testDate,
    status: 'TESTED',
    updatedAt: nowUTC(),
  };
}
