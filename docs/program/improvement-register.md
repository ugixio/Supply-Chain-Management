---
id: program-improvement-register
title: "Improvement Register — continuous improvement log"
type: program
owner: orchestrator
status: draft
since: 2026-07-19
updated: 2026-07-27
relations:
  - { type: part-of, target: index-program }
  - { type: governed-by, target: governance-root }
---
# Improvement Register

> The continuous-improvement loop, made a register (ADR-0012): when a task, incident or
> review teaches a **structural** lesson (about the process, the templates, the rules —
> not about one bug), it lands here and drives a change: a template edit, a new rule, an
> ADR, a gate. Rows are appended, never rewritten; a lesson without a resulting change is
> explicitly marked `accepted-as-is` with the reason.

## How to use

- A row is appended at task end (the self-review's "estimate honesty" and backlog
  follow-ups feed this register).
- The owner reviews open rows when planning; a row is closed only by the change it
  produced (link it) or by an explicit decision not to act.
- Lessons that change governing knowledge go through their normal path (ADR for
  decisions, supersession for rules) — this register points at the change, it is never
  the change itself.

## Register

| # | Date | Source | Lesson | Structural change | Status |
|---|---|---|---|---|---|
| 1 | 2026-07-19 | commit `a12c114` (pre-adoption) | the same formula duplicated in TS and Python silently diverged — duplicated logic without a shared oracle WILL drift | golden test vectors shared by both languages (backlog U8) | open |
| 2 | 2026-07-19 | first `npm install` of the repo (skeleton unification) | declared dev tooling was mutually uninstallable (`eslint ^9` + `@typescript-eslint ^7`) — nothing had ever verified the toolchain itself | dependency fix + committed lockfile + CI running the real commands (ADR-0013, U6) | done |
| 3 | 2026-07-19 | v0.2 skeleton audit | structural completeness ≠ model impact: exemplars, context budgets, recorded corrections and a fast gate move AI results more than added rules | ADR-0012 (exemplar, G9 budgets, pitfalls, verify split, handoff) | done |
| 4 | 2026-07-19 | cross-repo sync with the context-template skeleton | the instantiated gate script drifted from the skeleton's semantics: its rule-ID regex also matched the em-dash used by inherited-rule references (`templates/rule.md`), a latent G3 false-duplicate once per-department rule.md files land (U4) | regex aligned with the skeleton (definitions end in `:`); lesson: instantiate gate *configuration*, never gate *semantics* | done |
| 5 | 2026-07-27 | ADR-0037 (the owner stopping a wrong direction) | the estate had been building a *fictitious company* for weeks while every gate stayed green — because the gates checked internal consistency (links, IDs, symbol coverage) and nothing checked whether a statement was **externally fixed**. Green gates certified that the invented policy was well-organized. | the inclusion test at the head of `CLAUDE.md`; `SCM-R*` reclassified with a §Project decisions section; G10 rewritten from code coverage to **standards provenance**. Note the residual honestly: no gate can tell a standard from a plausible invention — that judgement is named as a reviewer's job, not automated away. | done |
| 6 | 2026-07-27 | PR #6 CI failure | `make verify-full` passed locally and CI failed on `pnpm install --frozen-lockfile`: a dependency was removed from a `package.json` without regenerating the lockfile, and the local gate never exercised the install step CI performs. **A gate that skips what CI does is not a gate.** | `deps-locked` target added to `verify-full`, running the exact CI invocation. Also removed two committed submodule gitlinks (`.claude/worktrees/…`) with no `.gitmodules`, which made every CI checkout emit a fatal error. | done |
| 7 | 2026-07-27 | Phase C4b (the skills/commands sweep) | **G11 shipped green while three retired rule IDs were cited in the skills tree** — it scanned only front-matter documents, and `.claude/**` is where the instructions that shape future work actually live. A gate over part of the estate certifies the part it can see, and the uncovered part is exactly where drift hides. Second lesson, from the same sweep: the two most-read files (`supply-chain-core/SKILL.md`, root `README.md`) were the two most stale — reading frequency and maintenance attention are unrelated. | G11 extended to `.claude/**` and `CLAUDE.md`; verified by planting a retired-ID citation. Both files rewritten. Dead Jest/eslint config and scripts removed rather than left declaring an estate that no longer exists. | done |
| 8 | 2026-07-27 | Phase C1d | **A statement attributed to two implementations escapes a policy sweep.** C1a searched for policy stated as policy; the same thresholds written as "PY bands / TS bands" passed, because a comparison reads as a description of code rather than a rule. When the implementations were then deleted, the numbers stayed — no longer describing anything, still reading as guidance. Second finding: `**FIN-R***` was cited 47 times as though it were a rule, invisible to every existing gate because it is not a broken link, not a duplicate and not a retired ID. | Both classes swept; **G12** added (a rule citation names an ID) and verified by planting a wildcard. Lesson for future sweeps: search for the *shape* of policy (a number next to a judgement) rather than for policy phrasing, and treat any comparison between implementations as a place where a decision is being deferred rather than recorded. | done |
