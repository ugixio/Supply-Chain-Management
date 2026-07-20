/**
 * Conflict Minerals Compliance — Dodd-Frank Wall Street Reform Act §1502
 *
 * SEC Rule 13p-1 (Release No. 34-67716, 2012).
 * SEC Form SD filed annually by May 31 (covers prior calendar year).
 * Applies to: SEC-reporting issuers that manufacture/contract-to-manufacture
 * products where 3TG minerals (tin/tantalum/tungsten/gold derived from
 * cassiterite/columbite-tantalite/wolframite) are necessary for functionality
 * or production.
 * 3TG from recycled/scrap sources → simplified Form SD, no CMR required.
 * RCOI (Reasonable Country of Origin Inquiry): determine if minerals originated
 * in DRC or adjoining countries (Angola, Burundi, CAR, DRC, Rwanda, South Sudan,
 * Tanzania, Uganda, Zambia).
 * CMR (Conflict Minerals Report): required if RCOI cannot rule out DRC-origin.
 * IPSA (Independent Private Sector Audit): only if company declares "DRC Conflict Free".
 * Standard tool: CMRT (Conflict Minerals Reporting Template) collected from suppliers.
 */

import { v4 as uuidv4 } from 'uuid';
import { ISODate, ISOTimestamp, nowUTC } from '@scm/shared/types';

export type ConflictMineral = 'TIN' | 'TANTALUM' | 'TUNGSTEN' | 'GOLD'; // 3TG

export type MineralSource =
  | 'RECYCLED_SCRAP'                // simplified filing — no CMR needed
  | 'DRC_FREE'                      // origin confirmed outside DRC + adjoining countries
  | 'DRC_CONFLICT_FREE'             // full IPSA completed; declared DRC Conflict Free
  | 'NOT_FOUND_DRC_CONFLICT_FREE'   // cannot confirm conflict-free
  | 'DRC_CONFLICT_UNDETERMINABLE';  // cannot determine origin

export type FormSDStatus =
  | 'NOT_STARTED'
  | 'RCOI_IN_PROGRESS'          // collecting CMRT from suppliers
  | 'RCOI_COMPLETE'
  | 'CMR_REQUIRED'              // RCOI couldn't rule out DRC origin
  | 'CMR_IN_PROGRESS'
  | 'IPSA_IN_PROGRESS'          // if pursuing "DRC Conflict Free" declaration
  | 'FORM_SD_FILED'             // submitted to SEC EDGAR
  | 'CLOSED';

// The 9 DRC Covered Countries per Rule 13p-1
export const DRC_COVERED_COUNTRIES: ReadonlySet<string> = new Set([
  'CD', // DRC
  'AO', // Angola
  'BI', // Burundi
  'CF', // Central African Republic
  'RW', // Rwanda
  'SS', // South Sudan
  'TZ', // Tanzania
  'UG', // Uganda
  'ZM', // Zambia
]);

export type SmelterRefiner = {
  readonly smelterRefinerId: string;
  readonly name: string;
  readonly country: string;       // ISO 3166-1 alpha-2
  readonly mineral: ConflictMineral;
  readonly isRCGIListed: boolean; // Responsible Minerals Initiative validated smelter
  readonly countryOfOrigin?: string; // country where ore was mined
};

export type ConflictMineralsDisclosure = {
  readonly id: string;
  readonly filingNumber: string;    // CMS-YYYY-NNN
  readonly reportingYear: number;   // calendar year covered
  readonly filingDeadline: ISODate; // Always May 31 of (reportingYear + 1)
  readonly status: FormSDStatus;

  // RCOI
  readonly rcoiMethod: string;      // description of RCOI process used
  readonly cmrtsCollected: number;  // number of CMRTs received from suppliers
  readonly cmrtsRequested: number;  // number of CMRTs requested
  readonly responseRatePct: number; // cmrtsCollected / cmrtsRequested × 100

  // Minerals in scope
  readonly mineralsInScope: ConflictMineral[];
  readonly sourceClassification: MineralSource;

  // Smelters/refiners identified
  readonly smeltersRefiners: SmelterRefiner[];
  readonly countriesOfOrigin: string[]; // ISO codes of mineral origin countries
  readonly involvesDRCCoveredCountries: boolean; // whether any covered country in supply chain

  // CMR (if required)
  readonly cmrRequired: boolean;
  readonly dueDiligenceStandard?: string; // e.g. 'OECD Due Diligence Guidance 3rd Ed.'
  readonly riskMitigationSteps?: string;

  // IPSA (if pursuing Conflict Free declaration)
  readonly ipsaRequired: boolean;
  readonly ipsaFirm?: string;
  readonly ipsaCompletedDate?: ISODate;

  // Filing
  readonly edgarFilingRef?: string;       // SEC EDGAR accession number
  readonly websitePublicationUrl?: string; // must be posted on company website per Rule 13p-1
  readonly filedAt?: ISOTimestamp;

  // Audit
  readonly isDeleted: boolean;
  readonly createdAt: ISOTimestamp;
  readonly updatedAt: ISOTimestamp;
};

// ─── Module-level sequence counter ───────────────────────────────────────────

let _seq = 0;

// ─── Functions ────────────────────────────────────────────────────────────────

function create(
  reportingYear: number,
  mineralsInScope: ConflictMineral[],
  rcoiMethod: string,
): ConflictMineralsDisclosure {
  if (reportingYear < 2012) {
    throw new Error(
      `reportingYear must be >= 2012 (SEC Rule 13p-1 effective date). Got ${reportingYear}.`,
    );
  }
  if (mineralsInScope.length === 0) {
    throw new Error('mineralsInScope must contain at least one mineral.');
  }

  _seq += 1;
  const filingNumber = `CMS-${reportingYear}-${String(_seq).padStart(3, '0')}`;
  const now = nowUTC();

  return {
    id: uuidv4(),
    filingNumber,
    reportingYear,
    filingDeadline: `${reportingYear + 1}-05-31` as ISODate,
    status: 'RCOI_IN_PROGRESS',
    rcoiMethod,
    cmrtsCollected: 0,
    cmrtsRequested: 0,
    responseRatePct: 0,
    mineralsInScope,
    sourceClassification: 'DRC_CONFLICT_UNDETERMINABLE',
    smeltersRefiners: [],
    countriesOfOrigin: [],
    involvesDRCCoveredCountries: false,
    cmrRequired: false,
    ipsaRequired: false,
    isDeleted: false,
    createdAt: now,
    updatedAt: now,
  };
}

function recordRCOIProgress(
  disclosure: ConflictMineralsDisclosure,
  cmrtsRequested: number,
  cmrtsCollected: number,
): ConflictMineralsDisclosure {
  const allowedStatuses: FormSDStatus[] = ['RCOI_IN_PROGRESS', 'RCOI_COMPLETE'];
  if (!allowedStatuses.includes(disclosure.status)) {
    throw new Error(
      `recordRCOIProgress requires status RCOI_IN_PROGRESS or RCOI_COMPLETE. Got '${disclosure.status}'.`,
    );
  }
  if (cmrtsRequested < 0 || cmrtsCollected < 0) {
    throw new Error('cmrtsRequested and cmrtsCollected must be non-negative integers.');
  }
  if (cmrtsCollected > cmrtsRequested) {
    throw new Error('cmrtsCollected cannot exceed cmrtsRequested.');
  }

  const responseRatePct =
    cmrtsRequested > 0 ? (cmrtsCollected / cmrtsRequested) * 100 : 0;

  return {
    ...disclosure,
    cmrtsRequested,
    cmrtsCollected,
    responseRatePct,
    updatedAt: nowUTC(),
  };
}

function completeRCOI(
  disclosure: ConflictMineralsDisclosure,
  sourceClassification: MineralSource,
  countriesOfOrigin: string[],
): ConflictMineralsDisclosure {
  const allowedStatuses: FormSDStatus[] = ['RCOI_IN_PROGRESS', 'RCOI_COMPLETE'];
  if (!allowedStatuses.includes(disclosure.status)) {
    throw new Error(
      `completeRCOI requires status RCOI_IN_PROGRESS or RCOI_COMPLETE. Got '${disclosure.status}'.`,
    );
  }

  const noCMRNeeded =
    sourceClassification === 'RECYCLED_SCRAP' || sourceClassification === 'DRC_FREE';
  const status: FormSDStatus = noCMRNeeded ? 'RCOI_COMPLETE' : 'CMR_REQUIRED';
  const cmrRequired = status === 'CMR_REQUIRED';
  const involvesDRCCoveredCountries = countriesOfOrigin.some(c =>
    DRC_COVERED_COUNTRIES.has(c),
  );

  return {
    ...disclosure,
    status,
    sourceClassification,
    countriesOfOrigin,
    involvesDRCCoveredCountries,
    cmrRequired,
    updatedAt: nowUTC(),
  };
}

function addSmelter(
  disclosure: ConflictMineralsDisclosure,
  smelterData: Omit<SmelterRefiner, 'smelterRefinerId'>,
): ConflictMineralsDisclosure {
  if (disclosure.status === 'CLOSED') {
    throw new Error('Cannot add smelter to a CLOSED disclosure.');
  }
  if (disclosure.sourceClassification === 'RECYCLED_SCRAP') {
    throw new Error(
      'Smelter tracking is not required for RECYCLED_SCRAP source classification.',
    );
  }

  const smelter: SmelterRefiner = {
    smelterRefinerId: uuidv4(),
    ...smelterData,
  };

  return {
    ...disclosure,
    smeltersRefiners: [...disclosure.smeltersRefiners, smelter],
    updatedAt: nowUTC(),
  };
}

function startCMR(
  disclosure: ConflictMineralsDisclosure,
  dueDiligenceStandard: string,
): ConflictMineralsDisclosure {
  if (disclosure.status !== 'CMR_REQUIRED') {
    throw new Error(
      `startCMR requires status CMR_REQUIRED. Got '${disclosure.status}'.`,
    );
  }

  return {
    ...disclosure,
    status: 'CMR_IN_PROGRESS',
    dueDiligenceStandard,
    updatedAt: nowUTC(),
  };
}

function completeCMR(
  disclosure: ConflictMineralsDisclosure,
  riskMitigationSteps: string,
): ConflictMineralsDisclosure {
  if (disclosure.status !== 'CMR_IN_PROGRESS') {
    throw new Error(
      `completeCMR requires status CMR_IN_PROGRESS. Got '${disclosure.status}'.`,
    );
  }

  const status: FormSDStatus = disclosure.ipsaRequired
    ? 'IPSA_IN_PROGRESS'
    : 'FORM_SD_FILED';

  return {
    ...disclosure,
    status,
    riskMitigationSteps,
    updatedAt: nowUTC(),
  };
}

function declareConflictFree(
  disclosure: ConflictMineralsDisclosure,
  ipsaFirm: string,
): ConflictMineralsDisclosure {
  if (!disclosure.cmrRequired) {
    throw new Error(
      'Cannot declare conflict-free without a completed CMR (cmrRequired must be true).',
    );
  }

  return {
    ...disclosure,
    ipsaRequired: true,
    status: 'IPSA_IN_PROGRESS',
    sourceClassification: 'DRC_CONFLICT_FREE',
    ipsaFirm,
    updatedAt: nowUTC(),
  };
}

function completeIPSA(
  disclosure: ConflictMineralsDisclosure,
  ipsaCompletedDate: ISODate,
): ConflictMineralsDisclosure {
  if (disclosure.status !== 'IPSA_IN_PROGRESS') {
    throw new Error(
      `completeIPSA requires status IPSA_IN_PROGRESS. Got '${disclosure.status}'.`,
    );
  }

  return {
    ...disclosure,
    status: 'FORM_SD_FILED',
    ipsaCompletedDate,
    updatedAt: nowUTC(),
  };
}

function file(
  disclosure: ConflictMineralsDisclosure,
  edgarFilingRef: string,
  websitePublicationUrl: string,
): ConflictMineralsDisclosure {
  const allowedStatuses: FormSDStatus[] = ['FORM_SD_FILED', 'RCOI_COMPLETE'];
  if (!allowedStatuses.includes(disclosure.status)) {
    throw new Error(
      `file requires status FORM_SD_FILED or RCOI_COMPLETE. Got '${disclosure.status}'.`,
    );
  }

  const now = nowUTC();
  return {
    ...disclosure,
    edgarFilingRef,
    websitePublicationUrl,
    filedAt: now,
    status: 'CLOSED',
    updatedAt: now,
  };
}

function isOverdue(disclosure: ConflictMineralsDisclosure, asOf: ISODate): boolean {
  return disclosure.status !== 'CLOSED' && disclosure.filingDeadline < asOf;
}

function softDelete(disclosure: ConflictMineralsDisclosure): ConflictMineralsDisclosure {
  if (disclosure.status === 'CLOSED') {
    throw new Error('Cannot soft-delete a CLOSED disclosure.');
  }

  return {
    ...disclosure,
    isDeleted: true,
    updatedAt: nowUTC(),
  };
}

export const ConflictMinerals = {
  create,
  recordRCOIProgress,
  completeRCOI,
  addSmelter,
  startCMR,
  completeCMR,
  declareConflictFree,
  completeIPSA,
  file,
  isOverdue,
  softDelete,
  DRC_COVERED_COUNTRIES,
};
