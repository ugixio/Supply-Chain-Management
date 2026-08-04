---
id: governance-gates
title: "The Gates — what each one checks, and what none of them can"
type: governance
owner: orchestrator
status: active
since: 2026-08-04
updated: 2026-08-04
relations:
  - { type: part-of, target: index-governance }
  - { type: refines, target: knowledge-architecture }
  - { type: governed-by, target: governance-root }
---
# The gates — what each one checks

> **Why this is its own document, and why that took five occurrences to see.** The roster is
> **append-only**: a gate ID is fixed forever and a retired gate would stay listed exactly as a retired
> rule does (`id-registry.md` §6). It lived in two places at once — `CLAUDE.md` as names, and
> knowledge-architecture §11 in full — and **both** of those files sit inside load sets, so **every
> gate added cost two sets twice**. `load-sets.md` records the collision five times and named the exit
> as *"§11 keeps the descriptions, CLAUDE.md keeps only the names"*. That exit was taken when G21 was
> added, and the set was still 17 words over — because the exit halved the copies and the growth was in
> the surviving one.
>
> **So the roster moved out of every load set instead.** `CLAUDE.md` keeps the names because a session
> must know what runs; knowledge-architecture §11 keeps a pointer; the descriptions live here, in a file
> no load set carries, where they can grow for as many gates as this estate ever has. That is the
> difference between paying a budget down and removing the term from the equation — and it is the
> answer the *rule* eventually gave, not the gate: **a set is a ceiling if any part of any member grows
> by design**, and the fix for a growing part is to move the part, not to raise the number.

## The roster

All twenty-two are wired into `tools/verify.py` and run by `make verify` (ADR-0012) — the count read
"sixteen" while seventeen existed, the same range-versus-count blind spot the ID registry had, and
since ADR-0052 the roster is `GATE_NAMES` at module scope and G21 recomputes its length:

- **G1** no stray docs · **G2** front-matter validity · **G3** ID uniqueness ·
  **G4** link integrity · **G5** no orphans (`part-of` traversal) · **G6** authority
  acyclicity · **G7** status/supersession integrity · **G8** English-only, screened for
  non-English function words (this repo's Language Policy, `CLAUDE.md`; ADR-0003) ·
  **G9** context budget and ADR disclosure · **G10** standards provenance · **G11** retired
  rules stay retired · **G12** a rule citation names an ID, never a family wildcard ·
  **G13** `updated:` matches the file's real last change · **G14** a load set is priced as a
  whole — what a session reads *together*, declared in `docs/program/load-sets.md` (ADR-0041) ·
  **G15** the context-adherence measurement is not stale (`docs/program/context-eval.md`; ADR-0043) ·
  **G16** the ID registry's retired roster equals the union of the retirement tables, both ways ·
  **G17** every Markdown table row carries the cell count its header declares — a short row renders
  as an empty cell, so a missing field is invisible (fourteen register rows lost their status that
  way, and a catalogue column with an empty heading went unfilled by fourteen of fifteen rows) ·
  **G19** every evaluation task can be answered from its declared load set — the `Must reach:`
  tokens must appear in a member, so a manifest that stops covering its own question reddens before a
  cold subagent is spent misreading the result (ADR-0051; improvement #34 found this class by
  accident) · **G20** the relation vocabulary is **exercised or declared reserved** — an unused edge
  type is an affordance for the defect it was written for, which is how `implements` outlived ADR-0037
  (ADR-0051) · **G18** the exemplar department (knowledge-architecture §10b) is whole — declared once,
  its `rule.md` carrying a live rule, its `SKILL.md` carrying the pitfall list, and every department's
  `_index.md` listing every node in its directory (ADR-0048; the last claim covers all fourteen
  because measurement showed they already comply, so a true and unguarded property became guarded at
  no cost).

**G21 — the dossier's counted facts are true (ADR-0052).** `docs/program/state-of-the-project.md`
declares eleven quantities in a fenced `` ```dossier `` block and the gate recomputes every one. Four
claims, four planted mutants:

1. a declared quantity must equal the measured one — the trigger is **drift, never wall-clock age**,
   because a calendar check reddens correct work during a quiet week and a gate that reddens correct
   work gets disabled rather than obeyed;
2. `snapshot` must equal `updated:`, which G13 already proves is the real last change, so the date can
   be neither backdated nor postdated;
3. a declared key the gate cannot recompute **fails** — the load-set manifest's unimplemented-selector
   lesson, so interpretation cannot be published in the typography of a measurement;
4. a measurable key left undeclared fails too — G16's both-directions rule, so the block cannot omit
   the inconvenient number.

Percentages, grades and verdicts are deliberately **not** declarable: a gate over a judgement would
only make the judgement look official.

**G22 — an external source is declared with its date, or absent (ADR-0054).** Any `http(s)` URL in a
tracked Markdown file must appear in that file's fenced `` ```external-sources `` block as
`<url> <YYYY-MM-DD> <what it is>`. Three claims, three planted mutants: an undeclared URL fails, a
declaration the document cites nowhere fails (G16's both-directions rule — a provenance record for
something no one references is drift), and a malformed or future retrieval date fails, because the date
is the half that does the work. **It guards an absence:** measured before it was written, the governed
estate had zero external URLs and the whole tracked tree had one, so the gate cost no sweep and was
green on the day it landed. What it deliberately does **not** check is whether a session was
*redirected* by something it read — that is a judgement, and four prose heuristics have already failed
here by firing on text that merely names a defect. Scope is every tracked file because `.claude/**`
holds the one real URL and is loaded into every session's working set (risk #13).

## A gate that cannot check must say so

`tools/verify.py` distinguishes *passed* from *could not run*: where a check depends on the
environment — G13 needs HEAD's parent present to diff against — it prints an INFO line naming the
reason instead of letting a skip read as a pass. G13 was RED in CI three times before this, because a
shallow checkout made its scope meaningless while the local run stayed green (improvement-register
#12). **A new gate is proven by planting a violation in the environment CI uses, not by reading its
code.** Since ADR-0042 that proof is automated rather than remembered: `tools/test_gates.py` plants
one violation per **claim** in a throwaway worktree and requires that gate — and no other — to fire.
It runs in `make verify-full`, and it contradicted its own author on its first green run.

## What a gate can and cannot certify

Each of these is a *mechanical* property. None of them can tell a standard from a plausible-looking
invention — that is risk #11, it is open, and it is how ADR-0037's defect began. G8 and G13 were added
on 2026-07-29 after a file-by-file review found a Spanish sentence and 164 stale `updated:` stamps that
no gate was looking for; the lesson recorded with them is that **a gate over part of the estate
certifies only that part**, which is why G8, G11, G12 and G13 read every tracked Markdown file, not
only the governed tree.

## References

- ADR-0012 (the gates as the enforcement mechanism) · ADR-0041 (load sets) · ADR-0042 (the gates are
  themselves tested) · ADR-0043 (context-adherence measurement) · ADR-0048 · ADR-0051 · ADR-0052.
- `docs/00-governance/id-registry.md` §6 — gate ID allocation, and why the roster is append-only.
- `docs/program/load-sets.md` — the manifest whose five recorded collisions produced this document.
