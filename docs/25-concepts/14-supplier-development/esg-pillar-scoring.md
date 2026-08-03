---
id: concept-esg-pillar-scoring
title: "ESG Pillar Scoring — E/S/G (CPT-0132)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-08-03
relations:
  - { type: part-of, target: index-concepts-14-supplier-development }
  - { type: governed-by, target: index-adr }
---
# ESG Pillar Scoring — E/S/G (CPT-0132)

> Rule-based 0–100 scores per ESG pillar from supplier evidence: environmental
> commitments and waste, social/labour practice, governance controls.

## Definition

Each pillar is a **composite over evidence items**, clipped to the reported scale:

    pillar = clip( base + Σ credits − Σ penalties , 0, 100 )

**What this node fixes is which evidence is admissible per pillar, and where each item's authority
comes from** — not the points. The three pillars and their evidence classes:

| Pillar | Evidence classes | External anchor |
|---|---|---|
| Environmental | emissions target, net-zero commitment, renewable share, recycling rate, deforestation status, geo-traceability, hazardous waste | SBTi; EUDR 2023/1115; GRI 306 |
| Social | forced-labour policy and import status, OH&S system, injury rate, wage adequacy, working hours | UFLPA; ISO 45001:2018; ILO C1/C30 |
| Governance | code of conduct, anti-bribery programme, whistleblower channel, certification, report, third-party assurance | ISO 37001; GRI 2; SASB |

**The base, every credit, every penalty and every band is the project's.** A scheme copied from
another organization imports its judgement about what an ESG score means.

## Inputs and outputs

- **Inputs:** per-pillar evidence — booleans for a policy or certificate, rates for a measured
  quantity, counts for incidents. Each item carries its evidence reference and date (**SDV-R4**).
- **Outputs:** three pillar scores on the reported scale → CPT-0133 blends them.

## Project-chosen inputs

| Decision | Why the context cannot fix it |
|---|---|
| The base score, and therefore what a no-evidence supplier scores | A base above zero says absence of evidence is not absence of practice; a base of zero says the opposite. Both are defensible positions and neither is a standard. |
| Every credit and penalty magnitude | A weighting is a statement of what the organization cares about. Nothing external ranks a whistleblower channel against a renewable share. |
| Whether a penalty is un-earnable-back within a period | ISO 45001 treats a fatality as categorically different; how a *score* reflects that is policy. |
| The rate thresholds triggering a credit or penalty | A cut-off is a target; CPT-0135 states the injury rate without setting a bar. |
| Whether an exclusionary condition vetoes the score | The UFLPA entity list is a legal fact; veto rather than deduction is a design choice (CPT-0061). |

## Assumptions and limits

- **Policy-presence scoring is the central limitation.** Credits reward evidence of *controls* — a
  policy, a certificate — not outcomes, so a supplier can score highly on a forced-labour policy
  while violations go undetected. Audits (CPT-0138) are the outcome check.
- **A non-zero base makes a no-evidence supplier score mid-range**, which converts silence into
  adequacy. Whatever base is chosen, read a low-evidence score as *unknown*, not as average
  (cf. CPT-0068's no-news caveat) — **SDV-R5** states this as law.
- Changing any weight re-bases history; apply forward or the series is not comparable.
- **Does not apply when:** an exclusionary condition exists (UFLPA entity list) —
  vetoes override scores (CPT-0061 pattern).

## Worked example

**Points chosen for the illustration, not carried by this node** — base 50, major credit 10, minor 5,
fatality −25:

E: 50 + 10 + 6 + 10 + 5 + 5 − 5 = **81**. S: 50 + 10 + 10 + 10 + 5 − 25 = **60**.
G: 40 + four at 10 = **80**. The insight is the *shape* — one fatality dominating the S pillar —
which holds for any severity-weighted scheme.

## Governing rules

- **SDV-R4/R5** — evidence and dating, and unknown is not compliant: a pillar with no submission
  scored at a mid-range default converts silence into adequacy. **SCM-R6** — UFLPA documentation feeds
  the S pillar input.

## Related

- CPT-0133 Overall score & rating · CPT-0135 LTIFR · CPT-0136 living wage ·
  CPT-0137 EUDR — the pillar inputs.

## References

- GRI Standards; SASB; ISO 45001:2018; ISO 37001; SBTi Corporate Manual v2.0.
