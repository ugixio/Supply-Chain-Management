import { v4 as uuidv4 } from 'uuid';
import { ISOTimestamp, nowUTC } from '@scm/shared/types';

export type ScenarioType = 'BASE' | 'UPSIDE' | 'DOWNSIDE' | 'STRESS_TEST';

export type SOPScenario = {
  readonly id: string;
  readonly sopCycleId: string;
  readonly name: string;
  readonly type: ScenarioType;
  readonly demandUpsidePct: number;
  readonly demandDownsidePct: number;
  readonly costImpactCents: number;
  readonly revenueImpactCents: number;
  readonly isSelected: boolean;
  readonly assumptions: string[];
  readonly createdAt: ISOTimestamp;
};

export namespace SOPScenario {
  export function create(params: {
    sopCycleId: string;
    name: string;
    type: ScenarioType;
    demandUpsidePct: number;
    demandDownsidePct: number;
    costImpactCents: number;
    revenueImpactCents: number;
    assumptions?: string[];
  }): SOPScenario {
    return {
      id: uuidv4(),
      sopCycleId: params.sopCycleId,
      name: params.name,
      type: params.type,
      demandUpsidePct: params.demandUpsidePct,
      demandDownsidePct: params.demandDownsidePct,
      costImpactCents: params.costImpactCents,
      revenueImpactCents: params.revenueImpactCents,
      isSelected: false,
      assumptions: params.assumptions ?? [],
      createdAt: nowUTC(),
    };
  }

  export function select(scenario: SOPScenario): SOPScenario {
    return { ...scenario, isSelected: true };
  }

  export function deselect(scenario: SOPScenario): SOPScenario {
    return { ...scenario, isSelected: false };
  }

  export function applyToForecast(scenario: SOPScenario, baseQty: number): number {
    const upside = baseQty * (scenario.demandUpsidePct / 100);
    const downside = baseQty * (scenario.demandDownsidePct / 100);
    return baseQty + upside - downside;
  }
}
