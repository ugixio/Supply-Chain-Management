---
id: program-manifest-template
title: "Unit Manifest Template (machine-readable contract)"
type: program
owner: orchestrator
status: draft
since: 2026-07-19
updated: 2026-07-19
relations:
  - { type: part-of, target: index-program }
  - { type: governed-by, target: governance-root }
---
# Unit manifest template

> The machine-readable half of a unit spec (spec template §6) — ADR-0012. One manifest
> per unit of work, at `docs/40-contexts/<department>/specs/<key>.manifest.yaml`. The
> manifest is the surface lanes and modules synchronize on: the implementation delivers
> exactly what it declares; nothing consumes a capability or event that is not declared
> here. The WHAT lane owns it; `verify` may cross-check it against the spec as specs
> materialize.

```yaml
key: <snake_case unit key>        # allocated in id-registry §4; names the spec and module
department: <NN-department>       # the owning department (ADR-0004 taxonomy)
maturity: declared                # declared | spec-only | implemented

depends_on: []                    # unit keys that must exist first

provides: []                      # capabilities offered to other units
consumes: []                      # capabilities required from other units

events:
  publishes: []                   # e.g. the src/shared/events.ts catalog entries
  subscribes: []

permissions: []                   # permissions this unit introduces
```

**Coherence rules**

- Every entry mirrors a section of the spec; the spec explains, the manifest declares.
  Divergence between them is a defect of the unit, found at review.
- `depends_on` / `consumes` name declared contracts only — a manifest may never encode a
  dependency on another department's internals.
- The manifest changes only together with its spec (WHAT lane), never unilaterally during
  implementation.
