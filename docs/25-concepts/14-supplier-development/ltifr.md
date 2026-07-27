---
id: concept-ltifr
title: "Lost Time Injury Frequency Rate (CPT-0135)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-14-supplier-development }
  - { type: governed-by, target: index-adr }
---
# Lost Time Injury Frequency Rate (CPT-0135)

> Occupational-safety frequency: lost-time injuries per million hours worked — the
> standard OHS comparability metric.

## Formula

    LTIFR = lost_time_injuries × 1,000,000 / hours_worked

| Symbol | Meaning | Unit |
|---|---|---|
| lost_time_injuries | injuries causing ≥ 1 lost shift/day | count |
| hours_worked | total exposure hours (> 0) | hours |

## Inputs and outputs

- **Output:** rate per 1M hours. World-class < 1.0 (feeds the +5 bonus in
  CPT-0132's S pillar; ≥ 5.0 costs −10).

## Assumptions and limits

- **Definition discipline:** "lost time" must be counted consistently (≥ 1 full
  shift is common; some regimes count ≥ 1 day) and the 1M-hour base distinguishes
  LTIFR from OSHA's TRIR (per 200,000 hours ≈ 100 FTE-years) — a factor-of-5 trap
  when comparing US suppliers.
- Frequency, not severity: one sprain and one amputation weigh equally — pair with
  severity rate (lost days per hour) for the full picture; fatalities are scored
  separately (CPT-0132).
- Small-hours denominators swing wildly — annualize small suppliers or use pooled
  multi-year hours.
- Under-reporting is the metric's known failure mode; audits validate.
- **Does not apply when:** contractor hours are excluded while contractor injuries
  occur on site — define the boundary (ISO 45001 §4.3 scope).

## Worked example

3 lost-time injuries over 2,400,000 hours → `3 × 10⁶ / 2.4 × 10⁶ = 1.25` — above
world-class, below the penalty band.

## Governing rules

- **SDV-R*** — safety metrics on the sustainability record; audit verification.

## Related

- CPT-0132 S pillar — consumes the bands.

## References

- ISO 45001:2018; ILO OSH statistics conventions; GRI 403-9.
