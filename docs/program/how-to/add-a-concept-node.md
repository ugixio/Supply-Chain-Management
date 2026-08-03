---
id: how-to-add-a-concept-node
title: "How to add a concept node"
type: how-to
owner: orchestrator
status: active
since: 2026-08-03
updated: 2026-08-03
relations:
  - { type: part-of, target: index-program }
  - { type: governed-by, target: index-adr }
---
# How to add a concept node

> **For someone who already knows the domain and needs the node to pass.** The rules are elsewhere
> and are not restated here: `CLAUDE.md` for the inclusion test, `knowledge-architecture.md` for the
> gates, `program/templates/concept.md` for the shape. This is the order of operations and the traps
> that have actually caught people.

## 0. Decide whether it belongs at all

Apply the inclusion test **before** writing anything. If the thing you want to add is a threshold, a
target, a tolerance, a weighting, a rating band, a service level, or a mandate to use one legitimate
method over another, **stop** — it is a project's choice and it does not go here. Name the decision
and the standard that constrains it, then stop.

A node that survives this states a **meaning**, and where one exists a **formula**, and nothing an
organization could reasonably choose differently.

## 1. Allocate the number first

Take the next free `CPT-NNNN` from `00-governance/id-registry.md` §Concept IDs and **record the
allocation in the same commit that uses it**. Numbers are never reused and never renumbered. Two
nodes claiming one number is a G10 failure and the second author is the one who has to unpick it.

## 2. Copy the template, do not improvise the shape

`program/templates/concept.md`. The sections a node must have, and the one it must not:

- `## References` **with content** — the source that fixes the statement. A node citing nothing fails
  G10, and "everyone knows this" is not a source.
- **No `## Implementations`.** A node links to no code (ADR-0037). G10 fails it.
- `## Governing rules` cites **rule IDs**, never a family wildcard. `**PRC-R***` fails G12; it reads
  as law and resolves to nothing.
- Check the ID is **live** before citing it: `00-governance/id-registry.md` §The retired roster is the
  complete list of dead IDs. Citing a retired one fails G11.

## 3. Count the words before you finish, not after

**The budget is 700 words and it is the single most common way a well-written node fails.** The first
context-adherence run produced a node that was structurally perfect at **806 words** — it had read
the budget and overran it anyway (`program/context-eval.md`).

    wc -w docs/25-concepts/<dept>/<slug>.md

Do this while writing, not at the end. **Trim the node; do not raise the budget** — the budget is an
ADR-0012 decision and moving it needs its own decision. What to cut, in order: prose restating a rule
you already cited by ID, a second worked example, and adjectives.

## 4. Wire it into the graph

- `part-of` its department's `_index.md`, or G5 reports an orphan.
- Add the row to that `_index.md` table, so a reader arriving at the department finds it.
- `depends-on` any node whose identity yours rests on — Little's Law, an MSR identity — rather than
  restating the argument.

## 5. Run the gates and read what they say

    make verify

Every failure names the file, the line and what to do. If G13 complains about `updated:`, the stamp
must say today; if G14 complains, the load set your node sits in is over budget and the node is the
newest thing in it.

## When this is not the guide you want

- **Changing an existing node's meaning** — that is a plan⇄context change (ADR-0010): the model, the
  ADR and the rules move first, then the node.
- **Adding a rule** rather than a concept — a rule states a constraint, a node states a meaning. A
  rule goes to a family file and needs an ID from the registry.
- **Recording a number a project must choose** — that is the `Project-chosen inputs` table, and it
  names the decision without answering it.
