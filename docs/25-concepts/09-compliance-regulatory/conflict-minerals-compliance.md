---
id: concept-conflict-minerals-compliance
title: "Conflict Minerals Compliance — 3TG (CPT-0099)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-09-compliance-regulatory }
  - { type: governed-by, target: index-adr }
---
# Conflict Minerals Compliance — 3TG (CPT-0099)

> The Dodd-Frank §1502 / SEC Rule 13p-1 toolchain for tin, tantalum, tungsten and
> gold: survey response rates, source classification, filing deadlines, audit
> triggers and supplier coverage.

## Formula

    rcoi_response% = collected / requested × 100     (RMI adequacy bar: ≥ 75%)
    classify: all_recycled → RECYCLED_SCRAP
              any origin ∈ DRC-covered {CD,AO,BI,CF,RW,SS,TZ,UG,ZM} →
                NOT_FOUND_DRC_CONFLICT_FREE
              else → DRC_FREE
    Form SD deadline = May 31 of reporting_year + 1     (year ≥ 2012)
    IPSA required ⇔ classification = DRC_CONFLICT_FREE  (voluntary claim)
    coverage: <50% or any high-risk → HIGH · <75% → MEDIUM · else LOW (+ actions)

| Symbol | Meaning | Unit |
|---|---|---|
| CMRT | Conflict Minerals Reporting Template (RMI) | forms |
| DRC-covered | DRC + 9 adjoining countries (ISO 3166-1 α2) | codes |

## Inputs and outputs

- **Inputs:** counts (validated: collected ≤ requested, non-negative); origin country
  codes (validated 2-char uppercase); reporting year; classification string.
- **Outputs:** rate + gap + adequacy; classification literal; ISO deadline;
  boolean; coverage % + risk level + prioritized recommendations.

## Assumptions and limits

- `classify_mineral_source` is a *screening* pass: presence of a covered country
  yields NOT_FOUND_DRC_CONFLICT_FREE (undeterminable), not "conflict-affected" — the
  determination requires smelter-level due diligence (RMAP-conformant smelters can be
  DRC-sourced *and* conflict-free; not modelled).
- `ipsa_required` tests the literal `DRC_CONFLICT_FREE` — a value the classifier never
  emits (it is the *voluntary product claim*, a management assertion). The IPSA
  obligation attaches to the claim, not the screening result (also note: SEC 2017
  enforcement guidance suspended parts of this; the rule text stands).
- The covered-country set and May-31 deadline are statutory constants; the 75% bar is
  RMI practice guidance, not law.
- **Does not apply when:** minerals are out of 3TG scope (cobalt/mica are covered by
  the EU 2017/821 regime and voluntary schemes instead).

## Worked example

Requested 120 CMRTs, collected 84 → 70% (< 75%, inadequate; gap 36). One supplier
declares RW origin → NOT_FOUND_DRC_CONFLICT_FREE → enhanced due diligence; FY 2025
Form SD due **2026-05-31**.

## Governing rules

- **CMP-R*** — evidence retention (CPT-0096) applies to CMRTs and RCOI records.

## Related

- CPT-0098 Composite score — conflict minerals feed the "other" weight pool.

## References

- Dodd-Frank Act §1502; SEC Rule 13p-1 & Form SD; OECD Due Diligence Guidance (3TG);
  RMI CMRT/RMAP; EU Regulation 2017/821.
