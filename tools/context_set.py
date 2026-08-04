#!/usr/bin/env python3
"""Assemble and price the context a session should open (ADR-0050).

**The problem this closes, measured before it was written.** The six load sets in
`docs/program/load-sets.md` name **17 of 241 governed documents**, and among those seventeen there
are **zero concept nodes** (of 167) and **zero department rule files** (of 14). A session authoring a
concept node was given the template and two foundation rule files and no example — while **559 typed
edges** in the front matter already state what every node depends on and traces to, read by nothing.

**What this does.** Given a task, it prints the files to open: the manifest's literal members, plus
whatever a `graph:` member expands to, plus — when a target node is named — that node's graph
neighbourhood. Then it prices the result, because G14 prices the *declaration* and nobody was pricing
the *session*.

**What it deliberately does not do.** No embedding, no similarity, no ranking, no cache, no model
call. At this corpus size exhaustive traversal is exact, cheap and auditable; ADR-0050 records the
condition under which that stops being true. It also never truncates: exceeding a ceiling is reported,
because the budget conversation is the point (ADR-0041).

Exit status is 0 unless the manifest or a target cannot be read — this is an assembler, not a gate.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys

DOCS = "docs"
LOAD_SETS = f"{DOCS}/program/load-sets.md"
FENCE = re.compile(r"^```load-sets$(.*?)^```$", re.M | re.S)
HEADER = re.compile(r"^(\S+)\s*=\s*(\d+)$")
RELATION = re.compile(r"\{\s*type:\s*([a-z-]+),\s*target:\s*([^\s}]+)\s*\}")
FRONT_ID = re.compile(r"^id:\s*(\S+)", re.M)

# Which edges pull context *in*. `part-of` reaches the department's front door, and `depends-on` /
# `traces-to` are the two that state "this node rests on that one" — the 72 edges the audit found
# unread. `governed-by` is deliberately excluded: it points at authority, which every node shares, so
# following it would drag the whole governance tier into every set and price it against every task.
PULL_EDGES = ("part-of", "depends-on", "traces-to", "refines")


def tracked() -> list[str]:
    out = subprocess.run(["git", "ls-files", "*.md"], capture_output=True, text=True)
    return out.stdout.split()


def front_matter(path: str) -> tuple[str, str]:
    """(id, front-matter block) for a governed document; ('', '') when it has none."""
    try:
        text = open(path, encoding="utf-8").read()
    except OSError:
        return "", ""
    if not text.startswith("---\n"):
        return "", ""
    block = text.split("---", 2)[1]
    match = FRONT_ID.search(block)
    return (match.group(1) if match else ""), block


def build_index() -> tuple[dict[str, str], dict[str, list[tuple[str, str]]]]:
    """id -> path, and path -> [(relation, target-id)] over the whole tracked estate."""
    by_id, edges = {}, {}
    for path in tracked():
        doc_id, block = front_matter(path)
        if not doc_id:
            continue
        by_id[doc_id] = path
        edges[path] = RELATION.findall(block)
    return by_id, edges


def parse_manifest() -> dict[str, tuple[int, list[str]]]:
    """set name -> (budget, members), from the one fenced block G14 also reads."""
    text = open(LOAD_SETS, encoding="utf-8").read()
    fence = FENCE.search(text)
    if not fence:
        raise SystemExit(f"{LOAD_SETS}: no ```load-sets block")
    sets, current = {}, None
    for line in fence.group(1).splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        header = HEADER.match(stripped)
        if header:
            current = header.group(1)
            sets[current] = (int(header.group(2)), [])
        elif current:
            sets[current][1].append(stripped)
    return sets


def expand_graph_member(member: str, by_id: dict[str, str]) -> list[str]:
    """`graph:<doc-id>` -> that document, plus every document it pulls in, one hop.

    One hop and not transitive closure: two hops from a department index reaches most of the estate,
    which would price every task against everything and defeat the manifest. Depth is a parameter of
    the *caller's* question, not of the member, so `--depth` carries it.
    """
    target_id = member.split(":", 1)[1]
    path = by_id.get(target_id)
    if not path:
        print(f"  ! graph:{target_id} resolves to no document", file=sys.stderr)
        return []
    return [path]


def neighbours(path: str, by_id: dict[str, str],
               edges: dict[str, list[tuple[str, str]]], depth: int) -> list[str]:
    """Documents reachable from `path` over PULL_EDGES, breadth-first, to `depth` hops."""
    seen, frontier = {path}, [path]
    for _ in range(depth):
        nxt = []
        for current in frontier:
            for relation, target in edges.get(current, []):
                if relation not in PULL_EDGES:
                    continue
                target_path = by_id.get(target)
                if target_path and target_path not in seen:
                    seen.add(target_path)
                    nxt.append(target_path)
        frontier = nxt
        if not frontier:
            break
    return [p for p in seen if p != path]


EXEMPLAR_FENCE = re.compile(r"^```exemplar$(.*?)^```$", re.M | re.S)
ARCH = f"{DOCS}/00-governance/knowledge-architecture.md"

# Tasks for which the exemplar is part of the answer. ADR-0048 declared a department the exemplar
# because *a model imitates a real example more reliably than it deduces from prose* — and then the
# exemplar sat in no load set, so no session could read it. Authoring is the task that needs it; a
# planning or quantity-recording session does not.
EXEMPLAR_TASKS = ("authoring-a-concept",)


def exemplar_department() -> str:
    """The department declared exemplar in knowledge-architecture §10b, or '' if none."""
    try:
        fence = EXEMPLAR_FENCE.search(open(ARCH, encoding="utf-8").read())
    except OSError:
        return ""
    if not fence:
        return ""
    declared = [line.strip() for line in fence.group(1).splitlines() if line.strip()]
    return declared[0] if declared else ""


def words(path: str) -> int:
    try:
        return len(open(path, encoding="utf-8").read().split())
    except OSError:
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("task", help="a load-set name from docs/program/load-sets.md")
    parser.add_argument("--target", help="a document the task is about; pulls its graph neighbourhood")
    parser.add_argument("--depth", type=int, default=1, help="graph hops from --target (default 1)")
    parser.add_argument("--paths-only", action="store_true", help="print paths and nothing else")
    parser.add_argument("--no-exemplar", action="store_true",
                        help="omit the exemplar department's index on an authoring task")
    args = parser.parse_args()

    sets = parse_manifest()
    if args.task not in sets:
        print(f"unknown load set '{args.task}'. Declared: {', '.join(sorted(sets))}", file=sys.stderr)
        return 2
    budget, members = sets[args.task]
    by_id, edges = build_index()

    declared, expanded = [], []
    for member in members:
        if member.startswith("graph:"):
            expanded += expand_graph_member(member, by_id)
        else:
            declared.append(member.split("#")[0])

    exemplar = []
    if args.task in EXEMPLAR_TASKS and not args.no_exemplar:
        dept = exemplar_department()
        index = f"{DOCS}/25-concepts/{dept}/_index.md" if dept else ""
        if index and os.path.exists(index):
            exemplar.append(index)

    pulled = []
    if args.target:
        if not os.path.exists(args.target):
            print(f"--target {args.target} does not exist", file=sys.stderr)
            return 2
        pulled = neighbours(args.target, by_id, edges, args.depth)
        if args.target not in declared:
            pulled.insert(0, args.target)

    seen, ordered = set(), []
    for path in declared + expanded + exemplar + pulled:
        if path not in seen:
            seen.add(path)
            ordered.append(path)

    if args.paths_only:
        print("\n".join(ordered))
        return 0

    total = 0
    for label, group in (("declared", declared), ("graph member", expanded),
                        ("exemplar (ADR-0048)", exemplar), ("pulled by target", pulled)):
        group = [p for p in group if p in seen]
        if not group:
            continue
        print(f"\n{label}:")
        for path in group:
            count = words(path)
            total += count
            print(f"  {count:6}  {path}")
    declared_total = sum(words(p) for p in declared)
    print(f"\n  {declared_total:6}  declared members — the quantity G14 governs, ceiling {budget}")
    print(f"  {total:6}  SESSION TOTAL for '{args.task}'"
          f"{f' + {args.target}' if args.target else ''}")
    # G14's ceiling governs the *declaration*; ADR-0050 split the two on purpose, so a session total
    # above it is information and not a violation. Saying "OVER" here would conflate the quantity the
    # gate polices with the one it deliberately does not.
    if declared_total > budget:
        print(f"\n  G14 WOULD FAIL: the declaration itself is {declared_total - budget} words over"
              f"\n  its ceiling. Take the structural exit the manifest records for this set.")
    elif total > budget:
        print(f"\n  The session reads {total - budget} words more than the declared ceiling — which is"
              f"\n  allowed and unpoliced (ADR-0050). Nothing is truncated; the number is the point,"
              f"\n  so the cost of reaching an example is a decision you make seeing it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
