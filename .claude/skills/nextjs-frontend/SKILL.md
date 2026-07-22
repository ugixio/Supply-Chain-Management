---
description: >
  Next.js + React for apps/web — the octagon node-graph wiki (ADR-0026), App Router,
  Server vs Client Components, GraphQL data access, accessibility (WCAG), theming
  (light/dark), and performance. Use for any UI work in apps/web or the node-graph.
---

# Next.js frontend — the octagon node-graph wiki

> `apps/web` renders the governed knowledge graph (ADR-0024/0026). The UI is a *view of
> real governed data*, never a second copy of it. Visual spec and the accessibility floor
> are ADR-0026 — treat the a11y clauses as load-bearing, not optional.

## App Router & rendering

- **App Router** (`app/`). Default to **Server Components**; make a component a Client
  Component (`'use client'`) only when it needs interactivity/state/browser APIs — the
  graph canvas and the sidebar are client; the page shell and initial data fetch are server.
- Fetch GraphQL on the server where possible (no client secrets, smaller JS). Co-locate
  queries with the component; type them from `schema.gql`.
- Keep the client bundle lean: dynamic-import the heavy graph renderer; stream the shell.

## The octagon node-graph (ADR-0026)

- Three tiers: SCM **core** node (centre) → 14 **department** nodes (radial, connected as a
  circuit) → **CPT concept** sub-nodes on expand. A node click opens the **right sidebar**
  with the concept detail (formula, worked example, links) from the read model.
- **Octagon = stroke only, no fill**, LED-cyan with a soft glow, transparent over a dark
  base. Render as inline SVG/Canvas; the glow is decorative, never the only affordance.
- **Layout:** fixed radial for the core+departments; force-directed (or radial sub-layout)
  for concept expansion. Keep layout deterministic enough to be testable.

## Accessibility (ADR-0026 floor — non-negotiable)

- **Keyboard:** tab/arrow between nodes, Enter to open the sidebar, Esc to close; visible
  focus ring that meets contrast. The graph is operable without a mouse.
- **Semantics:** each node has an accessible name and role; the graph exposes a
  text/list alternative (the same data as a nav tree) so it isn't vision-only.
- **Contrast & motion:** cyan-on-dark checked for WCAG AA; `prefers-reduced-motion`
  disables the glow pulse. State (idle/hover/selected/dimmed) never relies on colour alone.
- **Theming:** light and dark both supported; the transparent-fill octagon must read on both.

## Quality & performance

- Components are small, typed, and match the design tokens (future `50-engineering/frontend/`).
- No business logic in the UI — it renders what GraphQL returns. Money/decimals arrive as
  strings; format for display only, never compute money in JS (ENG-R4).
- Performance: memoize expensive graph computations; virtualize large concept lists; avoid
  layout thrash on hover. Test with a large department (06 — 51 concepts).
- **Tests:** component tests for the sidebar and node states; an axe/a11y check in CI;
  keyboard-navigation test. `make verify-full` green.
