---
id: concept-herfindahl-hirschman-index
title: "Herfindahl–Hirschman Index — Supply Concentration (CPT-0073)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-10-risk-management }
  - { type: governed-by, target: index-adr }
---
# Herfindahl–Hirschman Index — Supply Concentration (CPT-0073)

> How concentrated the spend (or supply) is across suppliers: the sum of squared
> shares. The antitrust metric, repurposed as single-point-of-failure detection.

## Formula

    HHI = Σ share_i² × 10,000        (shares as fractions — PY)
    HHI = Σ share_i²                  (shares as percent 0–100 — TS; same 0–10,000 scale)
    < 1,500 LOW · 1,500–2,500 MODERATE · > 2,500 HIGH

| Symbol | Meaning | Unit |
|---|---|---|
| share_i | supplier i's fraction of category spend | fraction (PY) / percent (TS) |

## Inputs and outputs

- **PY:** non-negative shares; if they don't sum to ~1 they are **normalized
  gracefully**, so raw spend values are accepted directly.
- **TS:** `Record<supplierId, sharePct>`; also returns the top supplier and its share;
  empty input → HHI 0/LOW.
- Output scale 0–10,000 in both (monopoly = 10,000; n equal suppliers = 10,000/n).

## Assumptions and limits

- Thresholds are the US DOJ/FTC merger guidelines applied by analogy — supply-risk
  tolerance may differ (a category with HHI 1,400 and one qualified alternate is
  riskier than 2,600 with instant substitutes). Pair with substitutability judgment.
- **Input-unit divergence (recorded):** PY fractions vs TS percent. Feeding TS-style
  percents to PY triggers normalization (harmless); feeding PY-style fractions to TS
  yields HHI ≈ 0 (silently wrong). U8 golden vectors should pin this.
- Shares must cover the whole category — omitting the tail overstates concentration.
- **Does not apply when:** measuring *network* fragility (use CPT-0069 GNN) or
  geographic concentration (compute HHI over regions instead — same formula).

## Worked example

Spend shares 50%/30%/20% → `2500 + 900 + 400 = 3800` → **HIGH** — the 50% supplier is
a structural dependency; dual-sourcing to 35/35/30 drops HHI to 3350… still HIGH:
concentration falls slowly, which is the point of the squared term.

## Governing rules

- **RSK-R*** — concentration findings feed the risk register with owner + strategy.

## Related

- CPT-0065 Composite supplier risk — single-source flag is the per-supplier echo.
- Kraljic (CPT-0031) — strategy response to bottleneck concentration.

## References

- US DOJ & FTC Horizontal Merger Guidelines (2010, thresholds retained in 2023) —
  HHI bands; Herfindahl (1950), Hirschman (1945).
