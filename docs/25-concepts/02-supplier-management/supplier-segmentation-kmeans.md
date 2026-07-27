---
id: concept-supplier-segmentation-kmeans
title: "Supplier Segmentation — K-means (CPT-0064)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-02-supplier-management }
  - { type: governed-by, target: index-adr }
---
# Supplier Segmentation — K-means (CPT-0064)

> Clusters the supplier base into performance segments (STRATEGIC / PERFORMER /
> DEVELOP / AT_RISK) from observed KPIs, so development effort goes where it pays.

## Formula

K-means (k = 4 default, `n_init = 10`, fixed seed 42) over standardized features
`[overall_score, ppm, otd_pct, spend]`; clusters ranked by centroid desirability:

    desirability = z(overall_score) + z(otd_pct) − z(ppm)

Best-ranked cluster → STRATEGIC, then PERFORMER, DEVELOP, AT_RISK (k = 4;
otherwise generic `SEGMENT_<rank>` labels).

| Symbol | Meaning | Unit |
|---|---|---|
| overall_score | scorecard result (CPT-0060) | 0–100 |
| ppm | defect rate | PPM |
| otd_pct | on-time delivery | percent |
| spend | annual spend | integer cents |

## Inputs and outputs

- **Inputs:** supplier dicts with the four features (missing keys default 0.0);
  at least k suppliers (raises otherwise). Requires scikit-learn (guarded import).
- **Output:** the input records augmented with `cluster` (int) and `segment` (name),
  order preserved.

## Assumptions and limits

- **Spend is standardized but not in the desirability ranking** — it shapes cluster
  geometry, not the label order; a high-spend low-performer still lands AT_RISK.
- K-means assumes roughly spherical clusters in z-space and is seed-sensitive despite
  the fixed seed at small n; re-run stability checks before re-labelling suppliers.
- Descriptive segmentation from performance data — **not** the Kraljic matrix
  (CPT-0031), which is a *strategy* grid on profit impact × supply risk; the two
  answer different questions and should not be conflated.
- **Does not apply when:** the base is small (< ~20 suppliers) — manual segmentation
  beats clustering noise.

## Worked example

12 suppliers, k = 4: the cluster whose centroid has the highest standardized
score/OTD and lowest PPM is labelled STRATEGIC; each supplier record returns with its
segment attached.

## Governing rules

- Advisory analytics; supplier status changes flow through the onboarding/scorecard
  lifecycles (SUP rules).

## Related

- CPT-0060 Scorecard — supplies `overall_score`.
- CPT-0031 Kraljic matrix — the strategic (not statistical) segmentation.

## References

- MacQueen (1967) — k-means; Chopra & Meindl (2016), Ch. 15; Kraljic (1983), *HBR*.
