# web  (scaffold — Next.js)

Presentation only (ENG-R8): it talks to `apps/api` and to nothing else — no database, no direct
telemetry access, no business logic.

No code yet — this is **Phase M4**. What lands here first is the monitoring dashboards: real-time
delivery metrics over a project's development progress (ADR-0031/0034/0036), reading the rollups in
`db/clickhouse` through the GraphQL gateway.

**Open decision affecting this directory.** ADR-0026 specifies the octagon node-graph wiki over the
governed knowledge — SCM core node, department nodes, CPT sub-nodes, LED-cyan outlines, right
sidebar — as backlog P4. It is **specified, not scheduled**: ADR-0037 makes monitoring the one
application built here, and whether the wiki is also built is an owner decision, recorded as ⚠ in
`docs/program/WORKFLOW.md` §Triage. The design tokens stand either way.
