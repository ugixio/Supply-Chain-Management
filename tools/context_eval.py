#!/usr/bin/env python3
"""Context-adherence evaluation — does an agent reading this context comply with it?

Fourteen gates verify that the estate is **internally consistent**. Nothing verified that an
agent reading it **produces something conforming to it**, which is the premise of the whole
repository. This runs five tasks whose success is decided by a program, never by a judge
model: the bias data against LLM-as-judge is recorded in ADR-0043, and a judge cannot be a
gate in an estate whose other checks are deterministic.

The subject is a **cold subagent** loaded only with the task's declared load set
(`docs/program/load-sets.md`). That is the only arrangement that isolates what the *context*
conveys: a session that just wrote a rule will cite it from memory, and score a meaningless
100 %. It also puts the load-set manifest itself under test — if the declared set is missing
something the task needs, the task fails and the manifest is what is wrong.

Usage
  python3 tools/context_eval.py --list                    show tasks and their exact prompts
  python3 tools/context_eval.py --prompt TASK             print one prompt to hand to a subagent
  python3 tools/context_eval.py --check TASK FILE         score one candidate answer
  python3 tools/context_eval.py --self-test               prove the checkers discriminate

`--self-test` is not optional decoration. A checker nobody tested is the exact hole ADR-0042
closed for the gates; each task carries a compliant and a violating sample, and the checker
must pass the first and fail the second.

Exit status: 0 when every requested check passes.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

EVAL_DOC = "docs/program/context-eval.md"
UOM_SOURCE = "packages/shared/src/types.ts"

# A rule citation naming a family rather than an ID (G12's shape, reused so the eval and the
# gate cannot disagree about what a bad citation looks like).
RULE_WILDCARD = re.compile(r"\*\*[^*]*\b((?:SCM|[A-Z]{3})-R)\\?\*\*\*")
RULE_ID = re.compile(r"\b((?:SCM|[A-Z]{3})-R\d+)\b")
CPT_ID = re.compile(r"\bCPT-\d{4}\b")

# Policy has a shape (CLAUDE.md): a number sitting next to a normative word. The eval looks for
# exactly that, and only outside quoted lines and worked examples — the context itself is
# allowed to *illustrate* a number, it is not allowed to *fix* one.
NORMATIVE = r"(?:threshold|tolerance|limit|target|maximum|minimum|at least|no more than|must not exceed|shall not exceed|acceptable)"
POLICY_SHAPE = re.compile(rf"(?:{NORMATIVE})[^.\n]{{0,40}}?\d+(?:\.\d+)?\s*(?:%|percent|USD|EUR|days?|hours?)"
                          rf"|\d+(?:\.\d+)?\s*(?:%|percent|USD|EUR|days?|hours?)[^.\n]{{0,40}}?(?:{NORMATIVE})",
                          re.I)
ILLUSTRATIVE = re.compile(r"illustrative|worked example|for example|e\.g\.|project must choose|"
                          r"project's own|nothing external fixes", re.I)

# Reported speech is not an assertion. The first real run (2026-08-02) failed an answer that
# **refused** to state a tolerance and, in explaining why, quoted `CLAUDE.md`'s own anti-pattern
# list — `names "a 5% receipt tolerance"`. The checker could not tell a citation of the defect
# from a commission of it, which is the mirror image of risk #11.
QUOTED_SPAN = re.compile(r"\"[^\"\n]*\"|“[^”\n]*”|`[^`\n]*`")

# The same class, for unit codes: an answer that warns `KG` is invented shorthand is doing the
# right thing. Only lines that do not disown the code are read as using it.
DISOWNS = re.compile(r"\binvented\b|\bshorthand\b|\bnot\b|\bnever\b|\bwrong\b|\bincorrect\b|"
                     r"\bnon-conformant\b|\bavoid\b|\binstead of\b|\brather than\b", re.I)


def repo_root() -> Path:
    return Path(subprocess.run(["git", "rev-parse", "--show-toplevel"],
                               capture_output=True, text=True).stdout.strip())


def live_rule_ids(root: Path) -> set[str]:
    """Rule IDs that are defined and not retired — the ones a citation may legitimately name."""
    defined, retired = set(), set()
    for path in subprocess.run(["git", "ls-files", "docs"], cwd=root,
                               capture_output=True, text=True).stdout.split():
        if not path.endswith("rule.md"):
            continue
        text = (root / path).read_text(encoding="utf-8")
        for line in text.splitlines():
            # Same shape as verify.py's RULE_ID_DEF, including the em-dash title: the first
            # version of this parser missed ENG-R8..R11 and PLT-R1..R6 and reported ten live
            # rules as dead, which is how G3's identical blind spot was found.
            match = re.match(r"^\s*-\s*(?:\*\*((?:SCM|[A-Z]{3})-R\d+)(?:\s+—[^*\n]*)?:\*\*"
                             r"|((?:SCM|[A-Z]{3})-R\d+)\s*:)", line)
            if match:
                defined.add(match.group(1) or match.group(2))
        if "## Retired rules" in text:
            table = text.split("## Retired rules", 1)[1]
            for stop in ("## Project decisions", "## Anti-states", "## Inherited rules"):
                table = table.split(stop, 1)[0]
            retired |= set(re.findall(r"^\|\s*\*\*((?:SCM|[A-Z]{3})-R\d+)\*\*\s*\|", table, re.M))
    return defined - retired


def valid_uom_codes(root: Path) -> set[str]:
    """The UN/ECE Rec 20 subset this context carries, read from its single source.

    Read rather than hardcoded on purpose: a copy here could drift from the module, and this
    task exists precisely because an invented shorthand (`KG` for `KGM`) once passed for a
    standard code.
    """
    text = (root / UOM_SOURCE).read_text(encoding="utf-8")
    block = text.split("export const UOM = {", 1)[1].split("} as const;", 1)[0]
    return set(re.findall(r"^\s*([A-Z]{2,3}):", block, re.M))


def prose_lines(answer: str) -> list[str]:
    """Lines outside fenced code blocks — where a claim is made rather than shown."""
    out, fenced = [], False
    for line in answer.splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if not fenced:
            out.append(line)
    return out


# --- the checks -----------------------------------------------------------------------
#
# Each returns a list of failures; empty means the answer complied. Every check is a program.
# Where a property cannot be decided mechanically it is left out and said so, rather than
# approximated — a false accusation costs more here than a miss, because the whole point is
# that this verdict can be trusted without a human re-reading it.

def check_invent_a_threshold(answer: str, root: Path) -> list[str]:
    """Failure class: policy dressed as law (ADR-0037, the defect that deleted 25,700 lines)."""
    failures = []
    for number, line in enumerate(prose_lines(answer), 1):
        asserted = QUOTED_SPAN.sub(" ", line)      # reported speech is not an assertion
        if POLICY_SHAPE.search(asserted) and not ILLUSTRATIVE.search(line):
            failures.append(f"line {number} states a value as a rule: {line.strip()[:90]!r}")
    if not (RULE_ID.search(answer) or CPT_ID.search(answer)):
        failures.append("names no existing rule or concept ID — a refusal has to say what "
                        "*does* constrain the decision, or it is just a refusal")
    return failures


def check_level_metric(answer: str, root: Path) -> list[str]:
    """Failure class: a level aggregated as a flow (risk #14)."""
    failures = []
    if "MSR-R2" not in answer:
        failures.append("does not cite MSR-R2 — the rule that fixes how a level may aggregate")
    if not re.search(r"\blevel\b", answer, re.I):
        failures.append("never classifies the measure as a level")
    if not re.search(r"\b(last|maximum|max|minimum|min|time-weighted)\b", answer, re.I):
        failures.append("names none of the aggregations valid for a level "
                        "(last, maximum, minimum, time-weighted average)")
    # Deliberately no regex for "did it sum?": a reliable one does not exist, and the three
    # positive checks above cannot all pass on an answer that treats the measure as a flow.
    return failures


def check_unit_codes(answer: str, root: Path) -> list[str]:
    """Failure class: invented data wearing a standard's name (`KG` for `KGM`)."""
    valid = valid_uom_codes(root)
    failures = []
    quoted, used = [], []
    for line in answer.splitlines():
        codes = re.findall(r"[`'\"]([A-Z]{1,4})[`'\"]", line)
        quoted += codes
        if not DISOWNS.search(line):           # a line warning against a code is not using it
            used += codes
    for code in sorted(set(used)):
        if code not in valid:
            failures.append(f"uses {code!r}, which is not in the UN/ECE Rec 20 subset this "
                            f"context carries ({UOM_SOURCE})")
    if not quoted:
        failures.append("quotes no unit code at all — the task asks for codes")
    return failures


def check_rule_citation(answer: str, root: Path) -> list[str]:
    """Failure class: a citation that reads as law and resolves to nothing (G12's class)."""
    failures = []
    for match in RULE_WILDCARD.finditer(answer):
        failures.append(f"cites the family {match.group(1)}* instead of an ID")
    live = live_rule_ids(root)
    cited = set(RULE_ID.findall(answer))
    if not cited:
        failures.append("cites no rule ID at all")
    for rule_id in sorted(cited - live):
        failures.append(f"cites {rule_id}, which is not a live rule in this estate")
    return failures


def check_new_concept_node(answer: str, root: Path) -> list[str]:
    """Failure class: structural non-conformance. Decided by the gates, not by this file.

    The candidate is placed in a throwaway worktree and `verify.py` must stay green. Reusing
    the gates rather than re-implementing their checks is the point: if G2/G9/G10 change, this
    task changes with them and cannot drift.
    """
    import shutil
    import tempfile
    slug = re.search(r"^id:\s*(\S+)", answer, re.M)
    if not slug:
        return ["no front-matter `id:` — the gates cannot even classify this as a document"]
    with tempfile.TemporaryDirectory(prefix="context-eval-") as tmp:
        worktree = Path(tmp) / "wt"
        subprocess.run(["git", "worktree", "add", "--detach", "--quiet", str(worktree), "HEAD"],
                       cwd=root, capture_output=True)
        try:
            for rel in subprocess.run(["git", "ls-files"], cwd=root,
                                      capture_output=True, text=True).stdout.splitlines():
                src = root / rel
                if src.exists():
                    (worktree / rel).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, worktree / rel)
            target = worktree / "docs/25-concepts/00-platform" / f"{slug.group(1)}.md"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(answer, encoding="utf-8")
            subprocess.run(["git", "add", "-A"], cwd=worktree, capture_output=True)
            done = subprocess.run([sys.executable, "tools/verify.py"], cwd=worktree,
                                  capture_output=True, text=True)
            if done.returncode == 0:
                return []
            return [line.strip() for line in done.stdout.splitlines()
                    if line.startswith("FAIL") or line.strip().startswith("- ")]
        finally:
            subprocess.run(["git", "worktree", "remove", "--force", str(worktree)],
                           cwd=root, capture_output=True)


CHECKS = {
    "invent-a-threshold": check_invent_a_threshold,
    "level-metric": check_level_metric,
    "unit-codes": check_unit_codes,
    "rule-citation": check_rule_citation,
    "new-concept-node": check_new_concept_node,
}


def checker_for(sample_id: str):
    """The checker a self-test sample exercises.

    A sample key may name a **variant** of a task — `unit-codes-warning` is the `unit-codes`
    checker on a case the first real run got wrong. Variants exist so a false positive found in
    the field becomes a permanent regression sample rather than a fix nobody re-tests.
    """
    if sample_id in CHECKS:
        return CHECKS[sample_id]
    for task_id, check in CHECKS.items():
        if sample_id.startswith(f"{task_id}-"):
            return check
    raise KeyError(f"sample '{sample_id}' names no task or variant of one")


# --- self-test samples ----------------------------------------------------------------
#
# One compliant and one violating answer per task. The checker must pass the first and fail
# the second; a checker that passes both accuses nobody, and one that fails both accuses
# everybody. Same discipline as tools/test_gates.py, applied to this file.

SAMPLES = {
    "invent-a-threshold": (
        "Nothing external fixes an over-receipt tolerance, so this context cannot carry one. "
        "CPT-0027 names the decision and SCM-R10 fixes the unit the quantity travels in; the "
        "level itself follows from the supply agreement. Worked example, illustrative only: a "
        "5% band would accept a 105-unit delivery against a 100-unit order.",
        "Receipts are accepted within a tolerance of 5% over the ordered quantity; deliveries "
        "beyond that threshold are rejected.",
    ),
    "invent-a-threshold-quoting": (
        "This context must not state a tolerance. CLAUDE.md's anti-patterns already name "
        "\"a 5% receipt tolerance\" as a defect this repository paid for; SCM-R10 fixes the "
        "unit and CPT-0027 names the decision.",
        "Accept an over-delivery when it is within the tolerance of 5% of the ordered quantity.",
    ),
    "unit-codes-warning": (
        "Weight travels as `KGM` and volume as `LTR`. Note `KG` and `L` are invented shorthand, "
        "not Rec 20 codes.",
        "Weight travels as `KG` and volume as `L`.",
    ),
    "level-metric": (
        "Open work orders is a **level**, read at an instant. **MSR-R2** — valid aggregations "
        "are last, maximum, minimum or a time-weighted average, never the sum.",
        "Open work orders counts the orders outstanding and sums across adjacent periods to "
        "give the total for the month.",
    ),
    "unit-codes": (
        "Weight travels as `KGM`, volume as `LTR`, length as `MTR`, and discrete items as `EA`.",
        "Weight travels as `KG`, volume as `L`, and length as `M`.",
    ),
    "rule-citation": (
        "Governed by **SCM-R10** for units and **SCM-R9** for instants.",
        "Governed by **PRC-R*** and the finance family **FIN-R***.",
    ),
}


def load_tasks(root: Path) -> dict[str, dict[str, str]]:
    """Task declarations, read from the governed document so prose and code cannot drift."""
    text = (root / EVAL_DOC).read_text(encoding="utf-8")
    tasks = {}
    for block in re.finditer(r"^### Task `([a-z-]+)`\s*$(.*?)(?=^### |\Z)", text, re.M | re.S):
        task_id, body = block.group(1), block.group(2)
        load_set = re.search(r"\*\*Load set:\*\*\s*`([^`]+)`", body)
        failure = re.search(r"\*\*Failure class:\*\*\s*(.+)", body)
        prompt = re.search(r"^```prompt$(.*?)^```$", body, re.M | re.S)
        tasks[task_id] = {
            "load_set": load_set.group(1) if load_set else "",
            "failure": failure.group(1).strip() if failure else "",
            "prompt": prompt.group(1).strip() if prompt else "",
        }
    return tasks


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--prompt", metavar="TASK")
    parser.add_argument("--check", nargs=2, metavar=("TASK", "FILE"))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    root = repo_root()
    tasks = load_tasks(root)

    declared, implemented = set(tasks), set(CHECKS)
    if declared != implemented:
        for task_id in sorted(declared - implemented):
            print(f"RED — task '{task_id}' is declared in {EVAL_DOC} with no checker")
        for task_id in sorted(implemented - declared):
            print(f"RED — checker '{task_id}' has no declaration in {EVAL_DOC}")
        return 1

    if args.list:
        for task_id, task in sorted(tasks.items()):
            print(f"{task_id:22} load set: {task['load_set']:22} {task['failure']}")
        return 0

    if args.prompt:
        task = tasks.get(args.prompt)
        if not task:
            print(f"unknown task '{args.prompt}'")
            return 1
        print(f"# Load the set '{task['load_set']}' and nothing else, then:\n")
        print(task["prompt"])
        return 0

    if args.check:
        task_id, path = args.check
        if task_id not in CHECKS:
            print(f"unknown task '{task_id}'")
            return 1
        failures = CHECKS[task_id](Path(path).read_text(encoding="utf-8"), root)
        if failures:
            print(f"FAIL {task_id} — {tasks[task_id]['failure']}")
            for failure in failures:
                print(f"  - {failure}")
            return 1
        print(f"PASS {task_id}")
        return 0

    if args.self_test:
        problems = 0
        for task_id, (good, bad) in SAMPLES.items():
            check = checker_for(task_id)
            on_good = check(good, root)
            on_bad = check(bad, root)
            if on_good:
                print(f"  FAIL  {task_id:22} rejects a compliant answer: {on_good}")
                problems += 1
            elif not on_bad:
                print(f"  FAIL  {task_id:22} accepts a violating answer — the check discriminates "
                      f"nothing")
                problems += 1
            else:
                print(f"  ok    {task_id:22} passes the compliant sample, catches the violation")
        missing = sorted(set(CHECKS) - set(SAMPLES))
        for task_id in missing:
            print(f"  note  {task_id:22} has no inline sample — it is decided by the gates, "
                  f"which carry their own mutants (ADR-0042)")
        print()
        if problems:
            print(f"RED — {problems} checker(s) do not discriminate")
            return 1
        print(f"GREEN — {len(SAMPLES)} checkers discriminate; "
              f"{len(missing)} delegated to the gates")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
