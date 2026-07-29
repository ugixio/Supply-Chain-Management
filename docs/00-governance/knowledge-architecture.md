---
id: knowledge-architecture
title: "Knowledge Architecture — governance rules (instantiated for this repo)"
type: governance
owner: orchestrator
status: active
since: 2026-07-19
updated: 2026-07-29
relations:
  - { type: part-of, target: index-governance }
  - { type: governed-by, target: governance-root }
---
# Knowledge Architecture

> **The official, self-contained governance document for this repo's knowledge.** It
> encodes the permanent rules that govern how every piece of knowledge is created,
> located, related, versioned and retired. Normative: each rule is checkable or
> procedural. The contract (`CLAUDE.md`) wins on any conflict (Tier 1). Adopted by
> ADR-0010 from the ugixio context skeleton.

---

## 1. The single-knowledge-repository rule

- **All project knowledge lives inside the `docs/` knowledge architecture or in an
  allowlisted home (§3).** There are no parallel or competing knowledge roots.
- Knowledge is organized by **business domain (the 14 departments), architecture and
  product evolution — never by implementation technology**.
- **Founding principles (permanent):** per-node justification (every division cites a
  reason); architecture before folders; total conservation (nothing discarded — classified
  and kept); references, never copies (§4); nothing isolated (every doc reachable and
  typed in the graph); only justified nodes materialized (that is why `50-engineering` /
  `60-operations` do not exist yet).

## 2. Authority ladder and tier map

Precedence runs highest to lowest; `governed-by` edges always point **up**.

```
Tier 1  governance          root CLAUDE.md                        (the contract; it wins)
Tier 2  10-decisions/       ADRs, incl. retroactive               (append-only)
Tier 3  20-product-model/   what the product is + glossary
Tier 4  30-foundation/*/rule.md + (future) 40-contexts/*/rule.md  hard rules, stable IDs
Tier 5  40-contexts/*/specs/                                      unit-of-work specs (future)
Tier 6  dept README/IMPLEMENTATION · .claude/skills/*/SKILL.md · docs/standards/   advisory know-how
meta / non-authority   00-governance/ (registries) · program/
```

- For every doc at Tier N, at least one `governed-by` target sits strictly above it (or
  the contract). Lower knowledge never governs higher (gate G6).
- The root `CLAUDE.md` (`governance-root`) is the unique apex.

## 3. The no-.md-outside rule and the allowlist

- **ABSOLUTE RULE.** Every tracked `.md` file is either inside `docs/` with valid
  front-matter, or on the ALLOWLIST below. A `.md` in neither set fails gate G1.
- **ALLOWLIST for this repo:**

  | Class | Members | Why exempt |
  |---|---|---|
  | Entry points | root `CLAUDE.md`, root `README.md` | tool-required / repo convention |
  | Agent tooling | `.claude/**` (skills, commands, settings) | tool-required; the SKILL.md files are the area-skill layer (Tier 6 by role) |
  | Component docs | `apps/*/README.md`, `packages/*/README.md`, `services/*/README.md` | live next to the code they document (Tier 6 by role; monorepo layout ADR-0023) |
  | Schema docs | `db/*/README.md` | operational instructions for whoever touches the DDL — retention values, the forward-only rule, how to run the gate. Useless one directory away from the migrations (ADR-0036, Phase M2) |
  | Grandfathered | `docs/standards/REGULATORY_FRAMEWORK.md` | predates the architecture; kept in place, referenced by ADR-0008; front-matter stamping is a WORKFLOW follow-up |
  | Untracked transient | personal/working files kept untracked | consolidated then deleted (§5) |

- Allowlisted entry points are **pointers plus their existing content**: from adoption
  onward, any NEW normative rule gets a stable ID in a `rule.md` and is cited, not
  restated. (The pre-existing restatements in `CLAUDE.md` are a recorded dedup follow-up
  in `program/WORKFLOW.md` — not a violation.)

## 4. Single source of truth (SSOT)

- Each fact, rule or decision has exactly one authoritative home; elsewhere it is
  **referenced, never copied** — a rule by its stable ID (e.g. `INV-R5`), a doc by its
  `id`, an ADR by its number.
- If two docs disagree, the higher-tier one wins and the lower is corrected or superseded.
- New content first checks whether an authoritative home already exists (§6).

## 5. Context management (conversation is never the source of truth)

- Every decision, rule or process born in conversation **must be consolidated** into an
  ADR, the product model, a `rule.md`, a spec or a registry before it is settled.
- Chat logs and transient working files are inputs, never authority.

## 6. Auto-organization procedure

1. **Does an authoritative home already exist?** Update it in place (living docs) or
   append a superseding record (append-only docs). No second home.
2. **If no home exists, create one in the correct tier**: `40-contexts/<dept>/` for a
   department concern; `30-foundation/<axis>/` for a cross-cutting one; the registries
   for cross-tier concerns. Never invent a directory outside the taxonomy.
3. **Stamp front-matter** (§8) and **wire the relations** (`part-of` up to the parent
   index; `governed-by` up the ladder).
4. **Allocate identifiers from `id-registry.md`** — never inline, never renumbered.
5. **Maintain the graph:** update the parent `_index.md`; no orphan, no broken link,
   no duplicate.

## 7. Prohibitions

- No tracked `.md` outside the architecture or the allowlist.
- No duplicated/parallel/contradictory documents; references only.
- No knowledge living only in conversation or transient files.
- No organization by technology; no speculative directories.
- No renumbering or reuse of stable IDs (rule IDs, ADR numbers, department keys).
- No `governed-by` pointing downward; no deletion of governing knowledge (supersede it).

## 8. Front-matter standard

Every non-allowlisted `.md` carries YAML front-matter:
- **Required:** `id`, `title`, `type`, `owner`, `status`, `since`, `updated`, `relations`.
- `type` ∈ `governance | adr | product-model | context-spec | rule | skill | engineering |
  operations | program | archive | transient`
- `owner` ∈ `human | orchestrator` (extend when agent lanes are formalized — see
  `program/operating-model.md`)
- `status` ∈ `draft | active | superseded | deprecated | archived`
- `relations[]`: `governed-by` · `implements` · `refines` · `depends-on` · `supersedes` /
  `superseded-by` · `traces-to` · `part-of`.
- `id` = `<type-slug>-<kebab-name>`; ADRs cited by number; unique estate-wide (gate G3).

## 9. Lifecycle and supersession

- `draft → active` (human/orchestrator accepts) · `active → superseded` (only by a new
  doc carrying `supersedes`; the old one is never rewritten) · `active → deprecated` ·
  `* → archived`.
- **Append-only records:** ADRs. **Living docs:** everything else — versioned in place,
  stable IDs append-only within the doc.
- Governing knowledge is never deleted.

## 10. Ownership

- Every document has exactly one owner. **human** owns the contract and final approvals;
  **orchestrator** owns program/process and (until lanes are formalized) the docs tree.

## 11. Enforcement (gates)

All thirteen are wired into `tools/verify.py` and run by `make verify` (ADR-0012):
- **G1** no stray docs · **G2** front-matter validity · **G3** ID uniqueness ·
  **G4** link integrity · **G5** no orphans (`part-of` traversal) · **G6** authority
  acyclicity · **G7** status/supersession integrity · **G8** English-only, screened for
  non-English function words (this repo's Language Policy, `CLAUDE.md`; ADR-0003) ·
  **G9** context budget and ADR disclosure · **G10** standards provenance · **G11** retired
  rules stay retired · **G12** a rule citation names an ID, never a family wildcard ·
  **G13** `updated:` matches the file's real last change.

**What a gate can and cannot certify.** Each of these is a *mechanical* property. None of them
can tell a standard from a plausible-looking invention — that is risk #11, it is open, and it is
how ADR-0037's defect began. G8 and G13 were added on 2026-07-29 after a file-by-file review
found a Spanish sentence and 164 stale `updated:` stamps that no gate was looking for; the
lesson recorded with them is that **a gate over part of the estate certifies only that part**,
which is why G8, G11, G12 and G13 read every tracked Markdown file, not only the governed tree.

## 12. Evolution of this document

Changes only through a new ADR accepted by the human; gate changes take the same path so
the doc and its enforcement never diverge. Companion registries: `id-registry.md`,
`out-of-scope.md`.
