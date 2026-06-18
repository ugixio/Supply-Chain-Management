/**
 * EU REACH Regulation (EC) No 1907/2006
 * Registration, Evaluation, Authorisation and Restriction of Chemicals
 *
 * Supply chain obligations:
 *  - Registration threshold: >1 metric tonne/year per substance (Art.5-24)
 *  - Safety Data Sheets (SDS) must pass through entire supply chain (Art.31)
 *  - SVHC in articles >0.1% w/w must be communicated to recipients (Art.33)
 *  - SVHC >0.1% w/w in articles must be notified to ECHA (Art.7(2))
 *  - Candidate List: ECHA publishes SVHCs — updated twice yearly
 *  - Authorisation List (Annex XIV): restricted substances require authorisation
 *  - Restriction List (Annex XVII): prohibited in certain applications
 *
 * Non-EU manufacturers: not directly regulated — EU importers bear full responsibility
 * Penalties: Member state jurisdiction; can include market withdrawal + criminal liability
 *
 * References:
 *  - ECHA: https://echa.europa.eu/regulations/reach/understanding-reach
 *  - EUR-Lex: https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02006R1907-20140410
 */

import { ISODate, ISOTimestamp, nowUTC } from '../../shared/types';

// Substance of Very High Concern classifications (Art.57 REACH)
export type SVHCCategory =
  | 'CMR'           // Carcinogenic, Mutagenic, Reprotoxic (Art.57a/b/c)
  | 'PBT'           // Persistent, Bioaccumulative, Toxic (Art.57d)
  | 'vPvB'          // very Persistent, very Bioaccumulative (Art.57e)
  | 'ENDOCRINE'     // Endocrine disrupting (Art.57f)
  | 'EQUIVALENT_CONCERN'; // Case-by-case (Art.57f)

export type REACHSubstance = {
  id: string;
  casNumber: string;          // CAS Registry Number
  ecNumber?: string;          // EC number (EINECS/ELINCS)
  name: string;
  isSVHC: boolean;
  svhcCategory?: SVHCCategory;
  candidateListDate?: ISODate; // when added to ECHA Candidate List
  isOnAuthorisationList: boolean;   // Annex XIV — requires authorisation
  isOnRestrictionList: boolean;     // Annex XVII — prohibited in certain uses
  registrationThresholdTonnes: number; // usually 1
};

export type ArticleREACHAssessment = {
  id: string;
  articleSku: string;
  assessmentDate: ISODate;
  substancesPresent: {
    substance: REACHSubstance;
    concentrationPctWW: number;   // % weight/weight
    presentInArticle: boolean;
    intentionalRelease: boolean;
  }[];
  // Compliance status
  containsSVHCAboveThreshold: boolean;  // any SVHC >0.1% w/w
  sdsRequired: boolean;
  echaNotificationRequired: boolean;    // Art.7(2): SVHC >0.1% + volume >1 tonne/year
  supplyChainCommunicationRequired: boolean;  // Art.33: B2B communication
  annualVolumeKg: number;
  isCompliant: boolean;
  complianceNotes: string;
  assessedBy: string;
  createdAt: ISOTimestamp;
};

export function assessREACHCompliance(
  input: Omit<ArticleREACHAssessment, 'id' | 'createdAt' | 'containsSVHCAboveThreshold' | 'sdsRequired' | 'echaNotificationRequired' | 'supplyChainCommunicationRequired' | 'isCompliant' | 'complianceNotes'>
): ArticleREACHAssessment {
  const svhcAbove = input.substancesPresent.filter(
    s => s.substance.isSVHC && s.concentrationPctWW > 0.1,
  );

  const containsSVHCAboveThreshold = svhcAbove.length > 0;
  const annualVolumeTonnes = input.annualVolumeKg / 1000;

  // Art.31: SDS required if substance is dangerous, PBT/vPvB, SVHC, or mixture
  const sdsRequired = containsSVHCAboveThreshold ||
    input.substancesPresent.some(s => s.substance.isOnAuthorisationList);

  // Art.7(2): ECHA notification if SVHC >0.1% AND annual volume >1 tonne
  const echaNotificationRequired = containsSVHCAboveThreshold && annualVolumeTonnes > 1;

  // Art.33: must communicate to downstream B2B customers
  const supplyChainCommunicationRequired = containsSVHCAboveThreshold;

  const hasRestrictedSubstances = input.substancesPresent.some(
    s => s.substance.isOnRestrictionList,
  );

  const isCompliant = !hasRestrictedSubstances &&
    (!echaNotificationRequired || input.isCompliant);

  const notes: string[] = [];
  if (containsSVHCAboveThreshold) {
    notes.push(`${svhcAbove.length} SVHC(s) found above 0.1% w/w threshold.`);
  }
  if (echaNotificationRequired) notes.push('ECHA notification required (Art.7(2)).');
  if (supplyChainCommunicationRequired) notes.push('Supply chain communication required (Art.33).');
  if (hasRestrictedSubstances) notes.push('WARNING: Article contains Annex XVII restricted substance(s).');

  return {
    ...input,
    id: crypto.randomUUID(),
    containsSVHCAboveThreshold,
    sdsRequired,
    echaNotificationRequired,
    supplyChainCommunicationRequired,
    isCompliant,
    complianceNotes: notes.join(' ') || 'REACH compliant.',
    createdAt: nowUTC(),
  };
}
