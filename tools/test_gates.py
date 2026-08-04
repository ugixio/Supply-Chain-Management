#!/usr/bin/env python3
"""Mutation tests for the doc gates — does each gate still catch what it claims to?

Improvement-register #12 left the rule in writing: *a new gate is proven by planting a
violation in the environment CI uses, not by reading its code.* That proof was performed
once, by hand, for G13. Nothing repeated it. Thirteen gates governed 230 documents with
zero tests of their own, so the next edit to `verify.py` could break G4 in silence and the
estate would keep reporting GREEN.

This is that proof, automated. For each gate it plants exactly one violation and asserts
that **the gate fires and the others stay quiet**. A mutant that no gate catches is a hole;
a mutant that trips a gate it should not is a false positive, and both fail here.

Method — end-to-end, deliberately. The gates are not called as functions: `verify.py` is
executed as a subprocess against a real git worktree, because that is what CI does and
because the one time this repository trusted a gate's *code* over its *behaviour* it went
red three times (G13, shallow-clone parentage). The worktree is populated from the current
index, so the harness tests the gates you are about to commit, not the ones already merged.

Usage:  git add -A && python3 tools/test_gates.py
        make verify-full   (runs it as part of the merge gate)

Exit status: 0 when every mutant is caught by its own gate and only by its own gate.
"""

from __future__ import annotations

import datetime
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TODAY = datetime.date.today().isoformat()
STALE = "2020-01-01"          # a date no document could honestly carry
FAIL_LINE = re.compile(r"^FAIL (G\d+)", re.M)
DIGEST_BLOCK = re.compile(r"^```context-digest$(.*?)^```$", re.M | re.S)
UNMEASURED = "(unmeasured)"

# Documents the mutants operate on. Chosen for stability: each has been in the tree since
# before this harness and none is a gate-configuration file, so a mutation here exercises
# the gate rather than the gate's own inputs.
CONCEPT = "docs/25-concepts/06-warehouse-management/goods-receipt-throughput.md"
CONCEPT_B = "docs/25-concepts/06-warehouse-management/outbound-shipment-backlog.md"
STRAY = "stray-note.md"
MANIFEST = "docs/program/load-sets.md"
EVAL_RECORD = "docs/program/context-eval.md"
DEPT_RULE = "docs/40-contexts/06-warehouse-management/rule.md"
REGISTRY = "docs/00-governance/id-registry.md"
ADR_INDEX = "docs/10-decisions/README.md"
ARCH = "docs/00-governance/knowledge-architecture.md"
NODE_MODEL = "docs/20-product-model/node-model.md"
EXEMPLAR_SKILL = ".claude/skills/procurement/SKILL.md"
DEPT_INDEX = "docs/25-concepts/06-warehouse-management/_index.md"
UNLISTED_NODE = "docs/25-concepts/06-warehouse-management/__planted-node.md"
DOSSIER = "docs/program/state-of-the-project.md"
SOURCED_SKILL = ".claude/skills/demand-planning/SKILL.md"

# A well-formed concept node, so G18's fourth-claim mutant fires **G18 and nothing else**: valid
# front-matter (G2), reachable by `part-of` (G5), governed upward (G6), a cited source and no
# `## Implementations` (G10), inside the word budget (G9). CPT-0998 is reserved for this harness in
# the ID registry — improvement #26: a test draws identifiers from a pool the authority has reserved.
PLANTED_NODE = """---
id: concept-planted-by-the-gate-harness
title: "Planted Node (CPT-0998)"
type: concept
owner: orchestrator
status: active
updated: __TODAY__
since: __TODAY__
relations:
  - { type: part-of, target: index-concepts-06-warehouse-management }
  - { type: governed-by, target: index-adr }
---
# Planted Node (CPT-0998)

> Written by `tools/test_gates.py` to prove G18's index-completeness claim fires. It is well formed
> on every other axis on purpose: a mutant that trips four gates proves nothing about one of them.

## Formula

None. This node exists to occupy a directory slot.

## References

- ADR-0048 — the decision this planted node exercises.
"""
RETIRED_RULE_ID = "SCM-R1"    # retired by ADR-0037; declared in 30-foundation/scm-core

# Every path any mutant may create or modify. The harness restores all of them between
# mutants, so this list must stay in step with the mutations below.
TOUCHABLE = (CONCEPT, CONCEPT_B, STRAY, MANIFEST, EVAL_RECORD, DEPT_RULE, REGISTRY,
             ADR_INDEX, ARCH, EXEMPLAR_SKILL, DEPT_INDEX, UNLISTED_NODE, NODE_MODEL,
             DOSSIER, SOURCED_SKILL)


# --- worktree plumbing ----------------------------------------------------------------

def git(*args: str, cwd: Path | None = None) -> str:
    """Run git and return stdout, raising with git's own message on failure."""
    done = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if done.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {done.stderr.strip()}")
    return done.stdout


def populate_from_index(repo: Path, worktree: Path) -> None:
    """Copy the repository's *staged* state into the worktree.

    The worktree starts at HEAD. Overlaying the index makes the harness test the gates as
    they will be committed — otherwise a gate added in this change would be tested in its
    absence, which is the failure mode this whole file exists to prevent. Untracked files
    are excluded on purpose: `git ls-files` is also what `verify.py` reads, so the two see
    the same estate.
    """
    tracked = set(git("ls-files", cwd=repo).splitlines())
    for rel in tracked:
        src, dst = repo / rel, worktree / rel
        if not src.exists():          # staged deletion
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    for existing in git("ls-files", cwd=worktree).splitlines():
        if existing not in tracked:
            (worktree / existing).unlink(missing_ok=True)
    git("add", "-A", cwd=worktree)


def measured_watch_set(worktree: Path) -> set[str]:
    """Watched context files carrying a REAL digest — the ones a mutation genuinely makes G15 fire on.

    **Derived, not declared, and that is the point.** The `also` column named G15 by hand for every
    mutant that edited a watched file, which is a hand-written mirror of a machine-readable list — the
    shape `known-pitfalls.md` says will drift. It drifted the day five digests went back to
    `(unmeasured)`: three declarations correct for a week became wrong in one commit, and the harness
    reported *gates failing to fire* when nothing about any gate had changed. A digest that reads
    `(unmeasured)` makes G15 skip, so touching that file is no longer collateral — and the harness now
    computes that instead of being told.
    """
    fence = DIGEST_BLOCK.search(read(worktree, EVAL_RECORD))
    if not fence:
        return set()
    measured = set()
    for line in fence.group(1).splitlines():
        parts = line.split()
        if len(parts) == 2 and not line.lstrip().startswith("#") and parts[1] != UNMEASURED:
            measured.add(parts[0])
    return measured


def run_gates(worktree: Path) -> tuple[set[str], str]:
    """Run verify.py inside the worktree; return the set of failing gate IDs and the output."""
    done = subprocess.run([sys.executable, "tools/verify.py"],
                          cwd=worktree, capture_output=True, text=True)
    output = done.stdout + done.stderr
    return set(FAIL_LINE.findall(output)), output


# --- mutation helpers -----------------------------------------------------------------

def read(worktree: Path, rel: str) -> str:
    return (worktree / rel).read_text(encoding="utf-8")


def write(worktree: Path, rel: str, text: str) -> None:
    (worktree / rel).write_text(text, encoding="utf-8")


def restamp(text: str, date: str = TODAY) -> str:
    """Set `updated:` so the mutation under test is the only violation in the file.

    Every mutant modifies a tracked document, which makes G13 expect today's date. Without
    this the G13 failure would ride along on all twelve other mutants and each assertion
    would be testing two gates at once.
    """
    return re.sub(r"^updated: .*$", f"updated: {date}", text, count=1, flags=re.M)


def set_field(worktree: Path, rel: str, field: str, value: str) -> None:
    text = re.sub(rf"^{field}: .*$", f"{field}: {value}", read(worktree, rel),
                  count=1, flags=re.M)
    write(worktree, rel, restamp(text))


# --- the mutants ----------------------------------------------------------------------
#
# One per gate. Each returns the paths it touched so the harness can restore them; a mutant
# that creates a file returns it too and the harness unlinks it.

def mutate_g1(wt: Path) -> list[str]:
    """A tracked Markdown file outside docs/ and not allowlisted."""
    write(wt, STRAY, "# Stray\n\nA document with no home.\n")
    git("add", STRAY, cwd=wt)
    return [STRAY]


def mutate_g2(wt: Path) -> list[str]:
    """A front-matter type outside the closed vocabulary."""
    set_field(wt, CONCEPT, "type", "invention")
    return [CONCEPT]


def mutate_g3(wt: Path) -> list[str]:
    """Two documents claiming the same id."""
    other_id = re.search(r"^id: (.+)$", read(wt, CONCEPT_B), re.M).group(1)
    set_field(wt, CONCEPT, "id", other_id)
    return [CONCEPT]


def mutate_g3_rule(wt: Path) -> list[str]:
    """A rule ID defined twice — G3's *second* claim, which had no mutant.

    G3 asserts three separate things: unique document ids, unique rule IDs and unique ADR
    numbers. Only the first was planted, and the gap was not theoretical: its rule-ID parser
    could not see ten live rules and nothing noticed. One mutant per gate is not one mutant per
    claim.
    """
    write(wt, DEPT_RULE, restamp(read(wt, DEPT_RULE)) +
          "\n- **SCM-R9 — a second definition of an ID that already has one:** planted.\n")
    return [DEPT_RULE]


def mutate_g4(wt: Path) -> list[str]:
    """A relation pointing at an id that does not exist."""
    text = read(wt, CONCEPT).replace("target: index-adr", "target: index-of-nothing", 1)
    write(wt, CONCEPT, restamp(text))
    return [CONCEPT]


def mutate_g5(wt: Path) -> list[str]:
    """A document with no part-of edge — unreachable from the root index."""
    text = re.sub(r"^  - \{ type: part-of.*\}$", "", read(wt, CONCEPT), count=1, flags=re.M)
    write(wt, CONCEPT, restamp(text))
    return [CONCEPT]


def mutate_g6(wt: Path) -> list[str]:
    """Authority pointing sideways: governed-by a document in the same tier."""
    other_id = re.search(r"^id: (.+)$", read(wt, CONCEPT_B), re.M).group(1)
    text = read(wt, CONCEPT).replace(
        "  - { type: governed-by, target: index-adr }",
        f"  - {{ type: governed-by, target: {other_id} }}", 1)
    write(wt, CONCEPT, restamp(text))
    return [CONCEPT]


def mutate_g7(wt: Path) -> list[str]:
    """Superseded without saying by what."""
    set_field(wt, CONCEPT, "status", "superseded")
    return [CONCEPT]


def mutate_g8(wt: Path) -> list[str]:
    """Prose that is not English."""
    write(wt, CONCEPT, restamp(read(wt, CONCEPT)) +
          "\nEste nodo también describe la recepción de mercancía.\n")
    return [CONCEPT]


def mutate_g9(wt: Path) -> list[str]:
    """A concept node past its word budget."""
    write(wt, CONCEPT, restamp(read(wt, CONCEPT)) + "\n" + ("filler " * 800) + "\n")
    return [CONCEPT]


def mutate_g9_adr_orphan_entry(wt: Path) -> list[str]:
    """An ADR listed in the index with no decision body.

    G9's third claim, and the one that was missing: the check ran body -> entry only,
    so ADR-0045 and ADR-0046 shipped as index entries with no body while PLT-R7 and
    knowledge-selection.md cited them as their authority. Planting the reverse
    direction is what keeps that from happening silently again.
    """
    text = read(wt, ADR_INDEX)
    marker = "\n> **File map:**"
    entry = ("- ADR-9999 — **A decision summarised and never recorded:** planted by the "
             "gate mutation harness.\n")
    # Insert the index entry among the entries, leaving no matching `## ADR-9999` body.
    text = text.replace(marker, "\n" + entry + marker, 1)
    write(wt, ADR_INDEX, text)
    return [ADR_INDEX]


def mutate_g18_no_exemplar(wt: Path) -> list[str]:
    """The exemplar block naming a department that does not exist (G18's first claim)."""
    text = restamp(read(wt, ARCH))
    write(wt, ARCH, re.sub(r"(?m)^```exemplar$\n.*?\n```$",
                           "```exemplar\n99-nonexistent\n```", text, count=1, flags=re.S))
    return [ARCH]


def mutate_g18_no_pitfalls(wt: Path) -> list[str]:
    """The exemplar's SKILL.md with its pitfall section gone (G18's third claim).

    ADR-0012 clause 4 as narrowed by ADR-0048: the exemplar is the one department required to
    carry the list, so its absence there is the whole of the remaining obligation.
    """
    text = read(wt, EXEMPLAR_SKILL)
    write(wt, EXEMPLAR_SKILL, re.sub(r"(?mi)^##+ .*pitfall.*$", "## Removed by the harness",
                                     text, count=1))
    return [EXEMPLAR_SKILL]


def mutate_g18_unlisted_node(wt: Path) -> list[str]:
    """A node in a department directory that its `_index.md` does not list (G18's fourth claim).

    Planted in warehouse rather than the exemplar because this claim covers all fourteen: the
    reader arriving at any department's front door must find everything behind it.
    """
    write(wt, UNLISTED_NODE, PLANTED_NODE.replace("__TODAY__", TODAY))
    return [UNLISTED_NODE]


def mutate_g19_unanswerable_task(wt: Path) -> list[str]:
    """A task whose declared set cannot reach what the task must reach (ADR-0051).

    Improvement #34's class, made mechanical: `unit-codes` was scored against a set carrying no unit
    codes, and two correct answers were failed before the manifest was identified as the defect. The
    planted token is deliberately absurd so the mutant tests the *check*, not a real coverage gap.
    """
    text = restamp(read(wt, EVAL_RECORD))
    write(wt, EVAL_RECORD, text.replace(
        "**Must reach:** `MSR-R2`",
        "**Must reach:** `MSR-R2` · `a-token-no-member-carries`", 1))
    return [EVAL_RECORD]


def mutate_g20_dead_relation(wt: Path) -> list[str]:
    """A relation type declared, used by nothing, and not declared reserved (ADR-0051).

    This is how `implements` outlived ADR-0037: a legal edge type letting a node point at code long
    after nodes stopped owning any, which is the affordance that let ENG-R10.7 contradict G10 for six
    weeks. The harness plants the same shape rather than the same name.
    """
    text = restamp(read(wt, ARCH))
    write(wt, ARCH, text.replace("```reserved-relations\n",
                                 "```reserved-relations\n", 1))
    # Reserve a type that IS in use: reserved-and-used is the contradiction the gate must catch.
    write(wt, ARCH, read(wt, ARCH).replace(
        "supersedes      G7 needs it",
        "part-of         planted by the harness: reserved while every document uses it\n"
        "supersedes      G7 needs it", 1))
    return [ARCH]


def mutate_g10(wt: Path) -> list[str]:
    """A concept node that cites no source."""
    text = restamp(read(wt, CONCEPT))
    write(wt, CONCEPT, text.split("## References")[0] + "## References\n")
    return [CONCEPT]


def mutate_g11(wt: Path) -> list[str]:
    """A citation to a rule that was retired and never reassigned."""
    write(wt, CONCEPT, restamp(read(wt, CONCEPT)) +
          f"\n- **{RETIRED_RULE_ID}** — cited as though it were still law.\n")
    return [CONCEPT]


def mutate_g12(wt: Path) -> list[str]:
    """A rule citation naming a family instead of an ID."""
    write(wt, CONCEPT, restamp(read(wt, CONCEPT)) +
          "\n- **WHS-R*** — a family wildcard is not a citation.\n")
    return [CONCEPT]


def mutate_g13(wt: Path) -> list[str]:
    """A real change carrying a stamp that predates it."""
    text = restamp(read(wt, CONCEPT), STALE) + "\nAn edit the stamp does not admit to.\n"
    write(wt, CONCEPT, text)
    return [CONCEPT]


def mutate_g17(wt: Path) -> list[str]:
    """A table row one cell short of its header.

    The mutant is a three-column table whose second row supplies two cells. Rendered, that row
    simply shows an empty third cell — which is exactly why the real instance survived two days in
    the improvement register and fourteen consecutive rows deep.
    """
    write(wt, CONCEPT, restamp(read(wt, CONCEPT)) +
          "\n| Term | Unit | Source |\n|---|---|---|\n| a | b | c |\n| d | e |\n")
    return [CONCEPT]


def mutate_g14(wt: Path) -> list[str]:
    """A load set that reads far more than it declares."""
    text = restamp(read(wt, MANIFEST)).replace(
        "  docs/program/evaluation.md\n\n# \"What should I do next?\"",
        "  docs/program/evaluation.md\n  docs/10-decisions/README.md\n\n# \"What should I do next?\"", 1)
    write(wt, MANIFEST, text)
    return [MANIFEST]


def mutate_g14_bad_graph_member(wt: Path) -> list[str]:
    """A `graph:` member naming an id no document declares (ADR-0050's selector).

    The selector lets a set say *what* it needs rather than *where* it lives, so the failure it
    must catch is a dangling id — the same class G4 catches for relations, at the manifest layer.
    """
    text = restamp(read(wt, MANIFEST))
    write(wt, MANIFEST, text.replace("every-task = 3400",
                                     "every-task = 3400\n  graph:no-such-document-id", 1))
    return [MANIFEST]


def mutate_g15(wt: Path) -> list[str]:
    """A recorded measurement that describes a context which has since changed.

    Corrupting the recorded digest is equivalent to changing the file it describes, and it is the
    safer direction to plant: the alternative — editing `CLAUDE.md` — would trip G9's path budget
    as well and stop testing G15 alone.

    This mutant was rewritten once. While every digest still read `(unmeasured)` it worked by
    *supplying* one; the moment a real measurement was recorded, that substring was gone and the
    mutation silently became a no-op. The harness reported it immediately, which is the case for
    asserting that a mutant fires rather than assuming a planted violation landed.
    """
    text = restamp(read(wt, EVAL_RECORD))
    corrupted = re.sub(r"^(CLAUDE\.md\s+)\S+$", r"\g<1>000000000000", text, count=1, flags=re.M)
    if corrupted == text:
        raise RuntimeError("G15 mutant planted nothing: no CLAUDE.md digest line to corrupt")
    write(wt, EVAL_RECORD, corrupted)
    return [EVAL_RECORD]


def mutate_g16_missing(wt: Path) -> list[str]:
    """A roster that has fallen behind the retirement tables."""
    text = restamp(read(wt, REGISTRY))
    write(wt, REGISTRY, text.replace("WHS: 1 2 3 4", "WHS: 1 2 3", 1))
    return [REGISTRY]


def mutate_g16_extra(wt: Path) -> list[str]:
    """A roster claiming a retirement no rule file declares — the other direction.

    Both directions are planted because the gate promises both, and a check that only looks
    one way lets the roster grow claims nobody made. G3's rule-ID hole came from exactly this:
    a gate asserting three things with one of them tested.
    """
    text = restamp(read(wt, REGISTRY))
    write(wt, REGISTRY, text.replace("WHS: 1 2 3 4", "WHS: 1 2 3 4 99", 1))
    return [REGISTRY]


def mutate_g21_drift(wt: Path) -> list[str]:
    """A counted fact the estate has moved away from — the failure the dossier had for six days.

    `concept-nodes` is decremented rather than incremented so the mutation cannot accidentally
    become true: the count only ever grows.
    """
    text = restamp(read(wt, DOSSIER))
    drifted = re.sub(r"^(concept-nodes\s+)(\d+)$",
                     lambda m: f"{m.group(1)}{int(m.group(2)) - 1}", text, count=1, flags=re.M)
    if drifted == text:
        raise RuntimeError("G21 drift mutant planted nothing: no 'concept-nodes' line to move")
    write(wt, DOSSIER, drifted)
    return [DOSSIER]


def mutate_g21_stale_snapshot(wt: Path) -> list[str]:
    """A snapshot date older than the content it claims to describe.

    `restamp` sets `updated:` to today, so G13 is satisfied and the *only* inconsistency left is
    between the stamp and the snapshot — which is the claim under test.
    """
    text = restamp(read(wt, DOSSIER))
    write(wt, DOSSIER, re.sub(r"^(snapshot\s+)\S+$", rf"\g<1>{STALE}", text, count=1, flags=re.M))
    return [DOSSIER]


def mutate_g21_unmeasurable_key(wt: Path) -> list[str]:
    """A fact declared in the gated block that no gate can recompute.

    This is the load-set manifest's lesson transplanted: an unimplemented selector prices the wrong
    thing silently, and a dossier that may declare unverifiable numbers launders interpretation as
    measurement. Planting it proves the gate refuses rather than ignores.
    """
    text = restamp(read(wt, DOSSIER))
    write(wt, DOSSIER, re.sub(r"^(snapshot\s+\S+)$", r"\1\nvelocity         42",
                              text, count=1, flags=re.M))
    return [DOSSIER]


def mutate_g21_missing_key(wt: Path) -> list[str]:
    """A measurable fact left out of the block — the other direction.

    Both directions are planted for G16's reason: a roster checked one way becomes a place to omit
    the inconvenient entry, and G3's rule-ID hole came from a gate asserting three things with one
    of them tested.
    """
    text = restamp(read(wt, DOSSIER))
    stripped = re.sub(r"^load-sets\s+\d+\n", "", text, count=1, flags=re.M)
    if stripped == text:
        raise RuntimeError("G21 missing-key mutant planted nothing: no 'load-sets' line to remove")
    write(wt, DOSSIER, stripped)
    return [DOSSIER]


def mutate_g22_undeclared(wt: Path) -> list[str]:
    """A URL in the body that the provenance block does not vouch for.

    The carrier of T1 memory poisoning: content arriving from outside with nothing recording where it
    came from. `.claude/**` is the target on purpose — it is loaded into every session's working set,
    and it is where the estate's one real external URL actually lives.
    """
    text = read(wt, SOURCED_SKILL)
    write(wt, SOURCED_SKILL,
          text + "\n- An undeclared source: https://example.invalid/planted-by-the-harness\n")
    return [SOURCED_SKILL]


def mutate_g22_uncited(wt: Path) -> list[str]:
    """A provenance record for a URL the document no longer cites — the other direction.

    Planted for G16's reason: a roster checked one way becomes a place where a stale entry survives,
    and a declaration that vouches for nothing is exactly that.
    """
    text = read(wt, SOURCED_SKILL)
    broken = text.replace("3rd ed. OTexts. https://otexts.com/fpp3/", "3rd ed. OTexts.", 1)
    if broken == text:
        raise RuntimeError("G22 uncited mutant planted nothing: the body citation was not found")
    write(wt, SOURCED_SKILL, broken)
    return [SOURCED_SKILL]


def mutate_g22_future_date(wt: Path) -> list[str]:
    """A retrieval date in the future (G22's third claim).

    The date is the half of the declaration that does the work — it is what makes risk #12's staleness
    visible — so a date nobody could have retrieved on makes the record worth less than no record.
    """
    text = read(wt, SOURCED_SKILL)
    dated = text.replace("https://otexts.com/fpp3/  2026-08-04",
                         "https://otexts.com/fpp3/  2099-01-01", 1)
    if dated == text:
        raise RuntimeError("G22 date mutant planted nothing: no declared date to move")
    write(wt, SOURCED_SKILL, dated)
    return [SOURCED_SKILL]


MUTANTS = [
    ("G1", "tracked .md outside docs/", mutate_g1, set()),
    ("G2", "type outside the vocabulary", mutate_g2, set()),
    ("G3", "duplicate document id", mutate_g3, set()),
    ("G3", "duplicate rule ID (G3's second claim)", mutate_g3_rule, set()),
    ("G4", "relation to an unknown id", mutate_g4, set()),
    # G21 fires too, and honestly: removing a `part-of` edge lowers the edge count the dossier
    # declares. A gate that counts the graph is collateral for every mutation that changes it.
    ("G5", "no part-of edge (orphan)", mutate_g5, {"G21"}),
    ("G6", "governed-by pointing sideways", mutate_g6, set()),
    ("G7", "superseded with no superseded-by", mutate_g7, set()),
    ("G8", "non-English prose", mutate_g8, set()),
    ("G9", "over the concept word budget", mutate_g9, set()),
    ("G9", "ADR indexed with no body (G9's third claim)", mutate_g9_adr_orphan_entry, set()),
    ("G10", "concept node citing no source", mutate_g10, set()),
    ("G11", "citation to a retired rule", mutate_g11, set()),
    ("G12", "rule family wildcard as a citation", mutate_g12, set()),
    ("G13", "change stamped with an old date", mutate_g13, set()),
    # G15 fires on both, and NOT for the digest reason the derivation covers: G15's second claim is
    # that every member of every evaluation task's load set is watched. Both mutants add a member to
    # the manifest, so a file appears in a scored set that the digest block does not watch. That
    # coupling holds whether or not `load-sets.md` itself is currently measured, which is exactly why
    # it stays a declaration while the digest half became derived.
    ("G14", "load set reading past its budget", mutate_g14, {"G15"}),
    ("G14", "graph: member naming an undeclared id", mutate_g14_bad_graph_member, {"G15"}),
    ("G15", "measurement recorded against a changed context", mutate_g15, set()),
    ("G16", "roster fallen behind the retirement tables", mutate_g16_missing, set()),
    ("G16", "roster claiming a retirement nobody declared", mutate_g16_extra, set()),
    ("G17", "table row one cell short of its header", mutate_g17, set()),
    # G15 fires too: knowledge-architecture.md is a watched context file, so touching it invalidates
    # the recorded measurement. That is the gate working, not collateral damage.
    ("G18", "exemplar block naming no real department", mutate_g18_no_exemplar, set()),
    ("G18", "exemplar SKILL.md with no pitfall list (G18's third claim)",
     mutate_g18_no_pitfalls, set()),
    # ...and G21, because planting a node moves two counted facts at once (governed-docs, graph-edges).
    ("G18", "a node its department index does not list (G18's fourth claim)",
     mutate_g18_unlisted_node, {"G21"}),
    # G15 does not fire: its digest block lists other files, not `context-eval.md` itself.
    ("G19", "task must-reach token no member carries", mutate_g19_unanswerable_task, set()),
    # G14 fires too, and the reason is worth leaving visible: `knowledge-architecture.md` sits in
    # `authoring-a-concept`, which ADR-0051 left at 8,195 of 8,200. Any line added to that file
    # breaks the ceiling — the append-only roster pressure the manifest already records.
    # ...and G15, because that file is also a watched context file: touching it invalidates the
    # recorded measurement. Both are the gates working, not collateral damage.
    ("G20", "a relation type reserved while in use", mutate_g20_dead_relation, set()),
    # The dossier sits in no load set and in no digest block, so these four fire G21 alone — which is
    # what makes it the cheapest gate in the harness to plant against, and worth saying because the
    # coupling that drags G14 and G15 into other mutants is not a law, it is a property of the file.
    ("G21", "a counted fact the estate has moved away from", mutate_g21_drift, set()),
    ("G21", "a snapshot older than the content (G21's second claim)",
     mutate_g21_stale_snapshot, set()),
    ("G21", "a declared fact no gate can recompute (G21's third claim)",
     mutate_g21_unmeasurable_key, set()),
    ("G21", "a measurable fact left undeclared (the other direction)",
     mutate_g21_missing_key, set()),
    # `.claude/**` carries no front matter, so these three trip neither G13 nor G21: the skill files
    # are outside the governed tree that the counted facts describe, and inside every session's
    # working set. That combination is why G22's scope is every tracked file (risk #13).
    ("G22", "a URL the provenance block does not vouch for", mutate_g22_undeclared, set()),
    ("G22", "a declaration citing nothing (the other direction)", mutate_g22_uncited, set()),
    ("G22", "a retrieval date in the future (G22's third claim)", mutate_g22_future_date, set()),
]
# The `also` column declares collateral that is real rather than tolerated. G14's and G16's mutants
# edit `load-sets.md` and `id-registry.md`, both of which the context-adherence measurement is
# recorded against (ADR-0043) — so changing either genuinely invalidates that measurement and G15 is
# right to fire. The gates agreeing is the system working; what the column forbids is an *undeclared*
# second failure, which means the mutation is testing something other than its gate. Expect this
# column to grow as G15's watched set grows: every context-defining file a mutant touches drags G15
# with it, and that coupling is the point of the gate rather than a nuisance. It exists because the first version of this file predicted that a duplicated id
# would drag G5 with it — the reasoning being that the losing document's part-of chain would
# resolve to a node no longer answering to that name. The harness said otherwise on its first
# green run: both documents carry part-of to the same index, so the chain resolves either way
# and G5 stays quiet. The prediction was plausible and wrong, which is the whole argument for
# running the mutants instead of reasoning about them. An unexplained second failure means the
# mutation is testing something other than its gate; an unexplained *absence* means the
# author guessed.


def main() -> int:
    repo = Path(git("rev-parse", "--show-toplevel").strip())

    unstaged = [line for line in git("status", "--porcelain", cwd=repo).splitlines()
                if line[:2] not in ("??",) and line[1] != " "]
    if unstaged:
        print("NOTE — unstaged changes are not tested; the harness reads the index.\n"
              "       Run `git add -A` first if you meant to include them.\n")

    with tempfile.TemporaryDirectory(prefix="gate-mutants-") as tmp:
        worktree = Path(tmp) / "wt"
        git("worktree", "add", "--detach", "--quiet", str(worktree), "HEAD", cwd=repo)
        try:
            populate_from_index(repo, worktree)

            baseline, output = run_gates(worktree)
            if baseline:
                print("RED — the unmutated estate does not pass; nothing below is meaningful")
                print(output)
                return 1
            print(f"baseline GREEN — {len(MUTANTS)} mutants to plant\n")

            # Snapshot every file a mutant can touch BEFORE the loop. Taking it after the
            # mutation would capture the damage and "restore" it, so mutations would stack
            # and each mutant after the first would be tested against a corrupted estate.
            pristine = {rel: (worktree / rel).read_bytes() if (worktree / rel).exists()
                        else None for rel in TOUCHABLE}

            measured = measured_watch_set(worktree)

            failures = []
            for gate, description, mutate, also in MUTANTS:
                touched = set(mutate(worktree) or ())
                git("add", "-A", cwd=worktree)
                caught, output = run_gates(worktree)

                derived = {"G15"} if touched & measured else set()
                expected = {gate} | also | derived
                if caught == expected:
                    notes = [f"+{one} as declared" for one in sorted(also)]
                    notes += [f"+{one} derived from the digest block" for one in sorted(derived)]
                    extra = f" ({', '.join(notes)})" if notes else ""
                    print(f"  ok    {gate:<4} caught: {description}{extra}")
                else:
                    missed = expected - caught
                    spurious = caught - expected
                    detail = []
                    if missed:
                        detail.append(f"did NOT fire: {', '.join(sorted(missed))}")
                    if spurious:
                        detail.append(f"unexpected: {', '.join(sorted(spurious))}")
                    print(f"  FAIL  {gate:<4} {description} — {'; '.join(detail)}")
                    failures.append((gate, description, output))

                for rel, blob in pristine.items():
                    if blob is None:
                        (worktree / rel).unlink(missing_ok=True)
                    else:
                        (worktree / rel).write_bytes(blob)
                git("add", "-A", cwd=worktree)

            print()
            if failures:
                for gate, description, output in failures:
                    print(f"--- {gate} ({description}) full gate output ---\n{output}")
                print(f"RED — {len(failures)} of {len(MUTANTS)} gates did not behave as claimed")
                return 1
            print(f"GREEN — {len(MUTANTS)} gates each caught their own violation and no other")
            return 0
        finally:
            subprocess.run(["git", "worktree", "remove", "--force", str(worktree)],
                           cwd=repo, capture_output=True)


if __name__ == "__main__":
    raise SystemExit(main())
