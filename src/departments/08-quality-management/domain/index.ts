export * from './InspectionRecord';
export * from './NCR';
// NCR and SCAR share lifecycle verb names; SCAR's are aliased so the barrel stays
// unambiguous (each module's namespace const still carries its own set).
export {
  SCAR_SLA, SCAR, issue, acknowledge, submitContainment, submitRootCause,
  submitCorrectiveAction, verify, escalate, reject,
  isAcknowledgementOverdue, isResponseOverdue, completedDisciplineCount,
  close as closeSCAR, daysOpen as daysOpenSCAR, softDelete as softDeleteSCAR,
  type SCARStatus, type SCARSeverity, type EightDDiscipline, type EightDStep,
  type SCARSla,
} from './SCAR';
export * from './SPCChart';
export * from './QualityKPI';
