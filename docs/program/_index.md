---
id: index-program
title: "Program — workflow, operating model, templates"
type: program
owner: orchestrator
status: active
since: 2026-07-19
updated: 2026-07-29
relations:
  - { type: part-of, target: index-docs }
  - { type: governed-by, target: governance-root }
---
# program

- **Belongs here:** how the work is RUN (non-authority over the product).
- **Exists today:**
  - [WORKFLOW.md](WORKFLOW.md) — the ordered backlog: unification follow-ups + gaps
    surfaced by the adoption audit.
  - [state-of-the-project.md](state-of-the-project.md) — regenerated status snapshot:
    completion by layer, best-practice scorecard, security posture, and the chosen
    improvement route (references the authorities; non-authority itself).
  - [operating-model.md](operating-model.md) — how AI-driven work is executed here
    (knowledge layers; the repo already implements the area-skill layer via
    `.claude/skills/`; §4 communication contract).
  - [evaluation.md](evaluation.md) — reasoning protocol, decision ladder, self-review
    checklist (ADR-0012).
  - [review-protocol.md](review-protocol.md) — how a body of documents is reviewed:
    enumerate the estate, name the finding classes, mark every item, consolidate, close the
    loop. Invoked for any review of any document type.
  - [improvement-register.md](improvement-register.md) — append-only
    continuous-improvement log (ADR-0012).
  - [templates/](templates/) — task · adr · spec · rule · skill · agent profile ·
    manifest.
