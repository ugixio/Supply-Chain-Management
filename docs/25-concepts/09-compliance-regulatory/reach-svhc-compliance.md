---
id: concept-reach-svhc-compliance
title: "REACH SVHC Compliance Assessment (CPT-0095)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-09-compliance-regulatory }
  - { type: governed-by, target: index-adr }
---
# REACH SVHC Compliance Assessment (CPT-0095)

> Per-substance obligations under EU REACH when a Substance of Very High Concern
> exceeds the 0.1% w/w concentration threshold in an article.

## Formula

    above ⇔ is_svhc ∧ concentration_ww > 0.001        (0.1% w/w)
    Art.7(2) notify ECHA  ⇔ above ∧ quantity > 1 t/yr
    Art.31  SDS           ⇔ above
    Art.33  inform downstream recipient ⇔ above
    status = ACTION_REQUIRED if any obligation else COMPLIANT

| Symbol | Meaning | Unit |
|---|---|---|
| concentration_ww | SVHC share of the article | w/w fraction (0.001 = 0.1%) |
| quantity_per_year_tonnes | SVHC tonnage per producer/importer per year | t/yr |

## Inputs and outputs

- **Inputs:** `REACHSubstance(cas_number, name, concentration_ww,
  quantity_per_year_tonnes, is_svhc)` list.
- **Output:** dict by CAS number with per-article flags, obligations text and status.

## Assumptions and limits

- **0.1% is per-article** (ECJ C-106/14 "once an article, always an article"): the
  denominator is each article as produced/assembled, not the finished complex product —
  a compliant assembly can hide a non-compliant component; assess at component level.
- The **Art.31 SDS** obligation strictly attaches to *substances and mixtures*
  supplied, not articles; applying it to article SVHC content (as here) is a
  conservative simplification — the article-specific duties are Art. 33 (inform) and
  Art. 7(2) (notify). Recorded fidelity note.
- Art. 7(2) notification is waived when exposure can be excluded or the use is already
  registered — not modelled (conservative: always required above thresholds; the U11b
  note about ECHA-notification tracking stands).
- The Candidate List grows every ~6 months — `is_svhc` must come from a current list
  (SCIP database duty under WFD also attaches; not modelled).
- **Does not apply when:** the substance is on Annex XIV (authorisation) or Annex XVII
  (restriction) — stricter regimes than notification.

## Worked example

DEHP (CAS 117-81-7), 0.3% w/w in cable sheathing, 2.4 t/yr → above threshold →
notify ECHA + inform downstream + (conservative) SDS → ACTION_REQUIRED.

## Governing rules

- **CMP-R3** — a Candidate List substance above 0.1% w/w triggers REACH duties; **CMP-R*** — evidence retention.

## Related

- CPT-0098 Composite compliance score — REACH is one of its inputs; the weighting is
  project-chosen.

## References

- EU Regulation 1907/2006 (REACH), Art. 7(2), 31, 33; ECHA Candidate List;
  ECJ C-106/14 (article-level 0.1%).
