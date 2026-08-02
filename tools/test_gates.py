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

# Documents the mutants operate on. Chosen for stability: each has been in the tree since
# before this harness and none is a gate-configuration file, so a mutation here exercises
# the gate rather than the gate's own inputs.
CONCEPT = "docs/25-concepts/06-warehouse-management/goods-receipt-throughput.md"
CONCEPT_B = "docs/25-concepts/06-warehouse-management/outbound-shipment-backlog.md"
STRAY = "stray-note.md"
MANIFEST = "docs/program/load-sets.md"
RETIRED_RULE_ID = "SCM-R1"    # retired by ADR-0037; declared in 30-foundation/scm-core

# Every path any mutant may create or modify. The harness restores all of them between
# mutants, so this list must stay in step with the mutations below.
TOUCHABLE = (CONCEPT, CONCEPT_B, STRAY, MANIFEST)


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


def mutate_g14(wt: Path) -> list[str]:
    """A load set that reads far more than it declares."""
    text = restamp(read(wt, MANIFEST)).replace(
        "  docs/program/evaluation.md\n\n# \"What should I do next?\"",
        "  docs/program/evaluation.md\n  docs/10-decisions/README.md\n\n# \"What should I do next?\"", 1)
    write(wt, MANIFEST, text)
    return [MANIFEST]


MUTANTS = [
    ("G1", "tracked .md outside docs/", mutate_g1, set()),
    ("G2", "type outside the vocabulary", mutate_g2, set()),
    ("G3", "duplicate document id", mutate_g3, set()),
    ("G4", "relation to an unknown id", mutate_g4, set()),
    ("G5", "no part-of edge (orphan)", mutate_g5, set()),
    ("G6", "governed-by pointing sideways", mutate_g6, set()),
    ("G7", "superseded with no superseded-by", mutate_g7, set()),
    ("G8", "non-English prose", mutate_g8, set()),
    ("G9", "over the concept word budget", mutate_g9, set()),
    ("G10", "concept node citing no source", mutate_g10, set()),
    ("G11", "citation to a retired rule", mutate_g11, set()),
    ("G12", "rule family wildcard as a citation", mutate_g12, set()),
    ("G13", "change stamped with an old date", mutate_g13, set()),
    ("G14", "load set reading past its budget", mutate_g14, set()),
]
# The `also` column declares collateral that is real rather than tolerated, and it is empty
# today. It exists because the first version of this file predicted that a duplicated id
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

            failures = []
            for gate, description, mutate, also in MUTANTS:
                mutate(worktree)
                git("add", "-A", cwd=worktree)
                caught, output = run_gates(worktree)

                expected = {gate} | also
                if caught == expected:
                    extra = f" (+{'+'.join(sorted(also))} as declared)" if also else ""
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
