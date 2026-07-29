# /scm-review — Supply Chain Correctness Review

Runs a domain-aware review of the current changes: **a project's implementation** against what this
context fixes, or a change to the context itself against the inclusion test.

## What this checks

Against the context (things fixed outside this repository, so a violation is a defect):
- **Money** — minor units, exact arithmetic, quantization only at defined boundaries, ties to even
  (SCM-R14, ENG-R4/R5). No float carries money anywhere, including over a wire.
- **Dates and instants** — ISO 8601-1:2019, UTC, unambiguous (SCM-R9).
- **Identifiers** — GS1 keys with a valid check digit; UN/ECE Rec 20 unit codes in the standard's
  spelling, `KGM`/`LTR`/`MTR` (SCM-R10).
- **Trade terms** — Incoterms® 2020 as the eleven rules are: DPU replaced DAT, four are sea-only.
- **Traceability and retention** where law applies — CSDDD ≥ 5 years (SCM-R7), UFLPA's rebuttable
  presumption (SCM-R6), REACH above 0.1% w/w (CMP-R3).
- **Quantity stated** on a sale of goods (UCC Article 2).

Against the inclusion test (a change to this repository):
- **Is every new statement fixed outside this repository?** A standards body, a regulator, or an
  arithmetic identity. If an organization could reasonably choose it, it is policy and does not
  belong here — name the decision and the standard that constrains it, then stop.
- **Policy has a shape:** a threshold, a target, a tolerance, a weighting, a rating band, a service
  level, or a mandate to use one legitimate method over another. Look for the shape, not the
  phrasing — the defect that caused ADR-0037 was numbers attributed to two implementations, which
  read as description rather than as rules.
- **A default in a signature is the worst form**, because it is inherited without anyone deciding.
- **A textbook figure is not a specification.** "World-class OTD ≥ 95%" is an illustration.

## Usage
Type `/scm-review` to run this over the current diff.

Report per finding: what it violates, the file and line, and whether it is a defect or a project
decision that needs confirming. Do not supply a value the project is supposed to choose.
