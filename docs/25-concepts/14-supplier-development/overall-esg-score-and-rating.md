---
id: concept-overall-esg-score-and-rating
title: "Overall ESG Score & Rating (CPT-0133)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-14-supplier-development }
  - { type: governed-by, target: index-adr }
  - { type: depends-on, target: concept-esg-pillar-scoring }
---
# Overall ESG Score & Rating (CPT-0133)

> Blends the three pillar scores 40/40/20 and maps the result to an MSCI-style
> seven-letter rating.

## Formula

    overall = 0.40·E + 0.40·S + 0.20·G          (clip [0,100])
    AAA ≥ 90 · AA ≥ 80 · A ≥ 70 · BBB ≥ 60 · BB ≥ 50 · B ≥ 40 · CCC < 40

| Symbol | Meaning | Unit |
|---|---|---|
| E/S/G | pillar scores (CPT-0132) | 0–100 |

## Inputs and outputs

- **Inputs:** the three pillar scores.
- **Outputs:** blended score; rating literal (inclusive lower bounds).

## Assumptions and limits

- 40/40/20 reflects the repo's supplier-development emphasis (E and S dominate;
  G as hygiene) — investor frameworks weight differently per industry (SASB
  materiality); a chemicals supplier's E should arguably outweigh S. Weights are
  governed values.
- The letter scale borrows MSCI's *vocabulary*, not its methodology — MSCI rates
  industry-relative with key-issue weights; do not present these letters as MSCI
  ratings.
- Averaging lets a strong pillar mask a weak one (E 90 / S 40 / G 80 → 68 BBB);
  severe-issue vetoes must sit outside the average (CPT-0132 note).
- **Does not apply when:** comparing across industries without materiality
  adjustment.

## Worked example

E 81, S 60, G 80 → `0.4·81 + 0.4·60 + 0.2·80 = 72.4` → **A**.

## Governing rules

- **SDV-R4** — the rating records the evidence it rests on and when that evidence was gathered;
  **SDV-R5** — an unevidenced pillar is *unknown*, and must not be scored as adequate.
  **SCM-R3** — the record is corrected by a further entry, never destroyed.

## Related

- CPT-0138 Tier-2 cascade — extends this score upstream.
- CPT-0061 Supplier rating — the delivery/quality counterpart.

## References

- GRI/SASB weighting practice; MSCI ESG ratings methodology (vocabulary reference).
