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
| μ | process mean | measurement unit |
| σ | the standard deviation — **and which one decides what you have computed** (below) | measurement unit |

**Which σ you use is not a detail — it changes the index.**

| σ estimate | Index it produces | What it describes |
|---|---|---|
| **Within-subgroup**, σ̂ = R̄/d₂ | **Cp / Cpk** | Short-term *capability*: what the process could hold if it stayed centred |
| **Total sample**, over all observations | **Pp / Ppk** | Long-term *performance*: what it actually delivered, drift included |

Total-sample σ absorbs between-subgroup variation too, so it is the larger whenever the process has
drifted. The two carry different names for exactly this reason (AIAG SPC manual): computing one and
labelling it the other is an error, not a variant.

**Capability minima are project-chosen** — a customer requirement, never a property of the
arithmetic. This node supplies none.

## Inputs and outputs

- **Inputs:** measurement list (n ≥ 2 for a finite σ), spec limits.
- **Output:** the indices, the mean and σ, and the percentage within spec. **Report which σ
  estimate was used** — without it the number cannot be interpreted, and two systems reporting
  "Cpk" from different estimates disagree while both being right about their own index.
- σ = 0 gives an infinite index and 100% within spec: a degenerate all-identical sample, which is
  a measurement-resolution problem far more often than a perfect process.

## Assumptions and limits

- Normality and statistical control first: capability indices on an out-of-control or
  non-normal process are fiction (run CPT-0056/0058 checks before quoting Cpk).
- **Cp without Cpk is a half-truth.** Cp ignores centring entirely, so a badly off-centre process
  can post a comfortable Cp while producing out-of-spec parts. Quote them together.
- Two-sided specs only; one-sided specs use Cpu or Cpl alone — Cp is undefined without both
  limits, so a single-limit characteristic has no Cp to report.
- **Does not apply when:** the characteristic is attribute (pass/fail) — use p-charts
  (CPT-0057) and PPM (CPT-0051).

## Worked example

Spec 10.0 ± 0.3 (LSL 9.7, USL 10.3); μ = 10.05, σ = 0.075 →
`Cp = 0.6/0.45 = 1.333` · `Cpu = 0.25/0.225 = 1.111` · `Cpl = 0.35/0.225 = 1.556` →
**Cpk = 1.111**.

The gap between Cp and Cpk is the whole message: the spread would fit, but the process sits above
centre and the off-centring eats a sixth of the margin. Re-centring is usually the cheap fix;
narrowing the spread is not. Whether 1.111 is acceptable is the customer's requirement.

## Project-chosen inputs

| Input | Why the project must choose it |
|---|---|
| The minimum acceptable index | A customer requirement or an internal risk decision; safety-critical characteristics attract stricter ones |
| Which index is contractually reported (Cp/Cpk or Pp/Ppk) | They answer different questions; a contract that names neither invites the flattering one |
| Subgroup size and sampling frequency | They define what "within-subgroup" means, hence σ̂ itself |

## Governing rules

- **QMS-R6** — a passed inspection is evidence, not a guarantee; a capability index computed from
  sample data inherits that limit. No rule fixes a capability target.

## Related

- CPT-0056 X̄-R limits — supplies the in-control verdict and the within-subgroup σ̂ = R̄/d₂.
- CPT-0052 DPMO — Cpk ↔ sigma-level conversions share the normal model.

## References

- Montgomery (2013), Ch. 6; AIAG SPC Reference Manual 2nd Ed.; Kane (1986) *JQT* 18(1).
