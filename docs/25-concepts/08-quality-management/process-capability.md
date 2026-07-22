---
id: concept-process-capability
title: "Process Capability — Cp/Cpk (CPT-0053)"
type: concept
owner: orchestrator
status: active
since: 2026-07-22
updated: 2026-07-22
relations:
  - { type: part-of, target: index-concepts-08-quality-management }
  - { type: governed-by, target: index-adr }
---
# Process Capability — Cp/Cpk (CPT-0053)

> How comfortably a process fits inside its specification limits: Cp measures the
> *potential* (spread only), Cpk the *actual* (spread + centring).

## Formula

    Cp  = (USL − LSL) / 6σ
    Cpu = (USL − μ) / 3σ · Cpl = (μ − LSL) / 3σ
    Cpk = min(Cpu, Cpl)

| Symbol | Meaning | Unit |
|---|---|---|
| USL / LSL | upper / lower specification limit | measurement unit |
| μ, σ | sample mean, sample std (ddof = 1) | measurement unit |

Targets: **Cpk ≥ 1.33** capable (4σ) · **≥ 1.67** highly capable (safety-critical).

## Inputs and outputs

- **Inputs:** measurement list (n ≥ 2 for a finite σ), spec limits.
- **Output:** `{Cp, Cpk, Cpu, Cpl, mean, std, within_spec_pct}` (4–6 dp). σ = 0 →
  `Cp = Cpk = ∞`, within-spec 100% — a degenerate all-identical sample, not proof of
  capability.
- The TS SPC chart computes Cp/Cpk incrementally inside `addSubgroup` using
  σ̂ = R̄/d₂ — the *within-subgroup* estimate; the PY function uses total sample σ.

## Assumptions and limits

- Normality and statistical control first: capability indices on an out-of-control or
  non-normal process are fiction (run CPT-0056/0058 checks before quoting Cpk).
- PY's overall σ mixes within- and between-subgroup variation → closer to **Pp/Ppk**
  (performance) than textbook Cp/Cpk; the TS R̄/d₂ path is the classical short-term
  estimate. The difference is the reported divergence, not an error.
- Two-sided specs only; one-sided specs use Cpu or Cpl alone (exposed in the output).
- **Does not apply when:** the characteristic is attribute (pass/fail) — use p-charts
  (CPT-0057) and PPM (CPT-0051).

## Worked example

Spec 10.0 ± 0.3 (LSL 9.7, USL 10.3); sample μ = 10.05, σ = 0.075 →
`Cp = 0.6/0.45 = 1.333` · `Cpu = 0.25/0.225 = 1.111` · `Cpl = 0.35/0.225 = 1.556` →
**Cpk = 1.111** — potentially capable, but off-centre eats the margin.

## Implementations

- PY: [`process_capability`](../../../services/calc/08_quality_management/quality.py)

## Governing rules

- Advisory analytics; acting on capability (blocking a supplier line) flows through NCR
  and inspection lifecycles (QMS rules).

## Related

- CPT-0056 X̄-R limits — supplies the in-control verdict and σ̂ = R̄/d₂.
- CPT-0052 DPMO — Cpk ↔ sigma-level conversions share the normal model.

## References

- Montgomery (2013), Ch. 6; AIAG SPC Reference Manual 2nd Ed.; Kane (1986) *JQT* 18(1).
