# Agents — the formalized agent layer (ADR-0027)

The second knowledge layer (`operating-model.md` §1), realized as 7 least-privilege subagent
profiles. The **main Claude Code session is the orchestrator** — it decomposes, assigns and
gates; there is no orchestrator agent. Each profile follows `docs/program/templates/agent.md`
and **references** the governance (`CLAUDE.md`, ADRs, `rule.md`, `CPT` nodes, `evaluation.md`,
`operating-model.md` §4) — it never restates it.

| Agent | Lane | Owns | Write access | Draws on skills |
|---|---|---|---|---|
| [architect](architect.md) | WHAT/plan | ADRs, specs, decomposition | docs only | — (planning) |
| [domain-knowledge](domain-knowledge.md) | WHAT | `docs/25-concepts`, `rule.md`, extraction | docs only | 15 domain skills |
| [backend-engineer](backend-engineer.md) | HOW | `apps/api`, `packages/{application,infrastructure}` | yes | clean-architecture, nestjs-graphql, engineering-standards, testing-quality |
| [frontend-engineer](frontend-engineer.md) | HOW | `apps/web` | yes | nextjs-frontend, engineering-standards, testing-quality |
| [data-engineer](data-engineer.md) | HOW | Postgres schema, migrations, read model | yes | postgresql-data, clean-architecture, testing-quality |
| [calc-engineer](calc-engineer.md) | HOW/SPECIALTY | `services/calc`, `proto/` | yes | python-precision-grpc, testing-quality, engineering-standards + domain skills |
| [quality-reviewer](quality-reviewer.md) | verify | the verdict (gates, review, security) | **none (read-only critic)** | testing-quality, engineering-standards, clean-architecture |

## How they work together (per-unit flow, operating-model §3)

```
architect       → spec + gated task list (+ ADR if load-bearing)
domain-knowledge → the CPT/rule the work implements or tests against
HOW engineer(s) → branch → test-first implementation → make verify green
quality-reviewer → independent gates + review + security → verdict (no fixes)
owner           → reviews → merges (agents never merge)
```

The proven reasoning techniques (read-before-write, plan⇄context, plan→act→verify with a
gate per layer, test-per-rule-ID, decision ladder, generator/critic separation, grounding,
explicit uncertainty, known-pitfalls memory) are the repo's existing protocols
(`evaluation.md`, `operating-model.md` §4) — encoded into the profiles, not reinvented.

## Technology skills (the HOW-lane skill layer, `.claude/skills/`)

`engineering-standards` · `clean-architecture` · `nestjs-graphql` · `nextjs-frontend` ·
`postgresql-data` · `python-precision-grpc` · `testing-quality` — parallel to the 15 domain
(WHAT-lane) skills. Practice lives in skills (one home); identity lives in profiles.
