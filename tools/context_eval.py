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

# **Second occurrence of the same incident, 2026-08-03, and the first fix was too literal.** The
# note above records an answer that refused to state a tolerance and quoted `CLAUDE.md`'s
# anti-pattern list to explain why; `QUOTED_SPAN` was added and it covers `"…"`, `“…”` and `` `…` ``.
# A later answer did the identical thing in a **Markdown blockquote** — `> **Policy dressed as
# law.** A USD 5,000 approval threshold, **a 5% receipt tolerance** …` — and failed, because the
# fix had targeted three quotation *syntaxes* rather than the concept of quotation. The disowning
# sentence ("were once stated as binding rules") sat on the next line, and the checker is
# line-scoped.
#
# A blockquote is the most explicit "these are not my words" marker Markdown has, so it is treated
# as reported speech like any quoted span. **This is not a widening of a word list** — the note at
# DISOWNS says that instrument is exhausted, and it is right. This keys on structure.
#
# The evasion it admits, stated rather than discovered later: an answer could assert policy inside
# a blockquote and escape. That is what the violating samples are for, and
# `invent-a-threshold-blockquote` is now a permanent regression sample of the legitimate case.
BLOCKQUOTE = re.compile(r"^\s*>")

# **The recurring class, and it recurred four times before this became a shared helper.** A checker
# that searches for the shape of a defect fires on the text that *names* the defect — and in a
# corpus about avoiding defects, that text is concentrated in the best answers:
#
#   1. `invent-a-threshold` refused to state a tolerance and quoted CLAUDE.md's own anti-pattern.
#   2. `unit-codes` gave the right codes and warned that `KG` is invented shorthand.
#   3. G11 failed the write-up of the run for listing the retired IDs the run had caught.
#   4. `rule-citation`, after the roster landed, wrote "do not cite …" for ten retired IDs — using
#      the fix exactly as intended — and named three unallocated numbers as *candidates for a new
#      rule*. Both were read as citations.
#
# So a token is counted as **used** only on a line that neither disowns nor proposes it. This
# trades recall for precision deliberately: a false accusation costs more here than a miss,
# because the verdict is meant to be trusted without a human re-reading the answer.
#
# **Known limit, stated so the next loosening is a decision and not a reflex.** This list has been
# widened four times, each in response to a real answer. Every widening lowers recall: an answer
# that genuinely misuses a token on a line that happens to contain "not" now escapes. The violating
# samples still fail, so the checker still discriminates on clear cases — but **if a fifth widening
# is needed, the line-level regex is the wrong instrument** and the task should ask for a structured
# answer (a list of IDs it endorses) instead of scoring free prose.
DISOWNS = re.compile(r"\binvented\b|\bshorthand\b|\bnot\b|\bnever\b|\bwrong\b|\bincorrect\b|"
                     r"\bnon-conformant\b|\bavoid\b|\binstead of\b|\brather than\b|"
                     r"\bretir\w*\b|\bdo not\b|\bdon't\b|\bwould be\b|\bnext free\b|"
                     r"\bpropos\w*\b|\ballocat\w*\b|\bcandidate\b", re.I)


def asserted_tokens(answer: str, pattern: re.Pattern) -> list[str]:
    """Matches of `pattern` on lines that assert them — disowning and proposing lines excluded."""
    out = []
    for line in answer.splitlines():
        if not DISOWNS.search(line):
            out += [m if isinstance(m, str) else m[0] for m in pattern.findall(line)]
    return out


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
    block = ANSWER_BLOCK.search(answer)
    if not block:
        return ["no ```answer block — the values this answer asserts as binding must be declared, "
                "with `none` when there are none (see context-eval.md §Task invent-a-threshold)"]
    declared = block.group(1)
    if not re.search(r"^\s*none\s*$", declared, re.M | re.I):
        for number, line in enumerate(declared.splitlines(), 1):
            if POLICY_SHAPE.search(line) or re.search(r"\d", line):
                failures.append(f"the answer block asserts a value as binding on line {number}: "
                                f"{line.strip()[:90]!r}")
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


ANSWER_BLOCK = re.compile(r"^```answer$(.*?)^```$", re.M | re.S)


def check_unit_codes(answer: str, root: Path) -> list[str]:
    """Failure class: invented data wearing a standard's name (`KG` for `KGM`).

    **This checker reads a declared answer block and ignores the prose entirely, and that is a
    deliberate change of instrument rather than a widening.** It used to score every quoted
    token on every line that did not *disown* it, and on 2026-08-03 that heuristic reached the
    sixth occurrence of its known failure — the threshold the register had already written down
    for abandoning it. The answer it failed was correct: it gave `KGM`, `LTR`, `MTR`, quoted
    `CLAUDE.md`'s own anti-pattern (which spells out `KG`, `L`, `M`), and named `PCE` only to
    refuse to assert it. Every one of the four was counted as used, because the disowning words
    sat on the previous line — wrapped prose puts the attribution and the token in different
    lines, and a line-level filter cannot see across that.

    No regex over prose fixes this: the distinction is between *asserting* a code and *mentioning*
    one, and a sentence does not carry that distinction in a form a program can read. So the task
    now asks for the conclusion in a fenced ``answer`` block, one `quantity: CODE` line each, and
    only that block is scored. The prose may quote, warn and cite freely. This is the same move as
    G17's: when a claim needs to be checkable, give it a structure instead of inferring it from
    sentences.
    """
    valid = valid_uom_codes(root)
    block = ANSWER_BLOCK.search(answer)
    if not block:
        return ["no ```answer block — the task asks for the conclusion in one, because prose "
                "cannot distinguish a code being asserted from a code being warned about"]
    failures = []
    code_token = re.compile(r"\b([A-Z]{1,4})\b")
    quoted = []
    for line in block.group(1).splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        # A line may legitimately carry no code: the subset genuinely lacks a code for some
        # quantities, and saying so beats inventing one. Only what IS named is judged.
        for code in code_token.findall(line.split(":", 1)[-1]):
            quoted.append(code)
            if code not in valid:
                failures.append(f"declares {code!r}, which is not in the UN/ECE Rec 20 subset "
                                f"this context carries ({UOM_SOURCE})")
    if not quoted:
        failures.append("declares no unit code at all — the task asks for codes")
    return failures


def check_rule_citation(answer: str, root: Path) -> list[str]:
    """Failure class: a citation that reads as law and resolves to nothing (G12's class).

    **Scored on a declared block, not on prose, and this is the third payment for that lesson.**
    The prose form failed three correct answers, each the same way: the check is line-scoped, and an
    answer that writes off a retired ID puts the disowning word on another line once the paragraph
    wraps. The last one read `the durable form of **the old SCM-R2** is **PRC-R1**` — the roster used
    exactly as intended. `DISOWNS` states the remedy for precisely this checker: ask for a structured
    answer instead of scoring free prose. Followed here rather than re-argued, and it is the fix
    `unit-codes` already carries.

    Everything outside the block is free: an answer can discuss retired IDs, near-misses and what it
    rejected, which is the discussion the prose form was punishing.
    """
    failures = []
    block = ANSWER_BLOCK.search(answer)
    if not block:
        return ["no ```answer block — the endorsed rule IDs must be declared, not inferred "
                "from prose (see context-eval.md §Task rule-citation)"]
    declared = block.group(1)

    for family in RULE_WILDCARD.findall(declared):
        failures.append(f"cites the family {family}* instead of an ID")
    live = live_rule_ids(root)
    cited = set(RULE_ID.findall(declared))
    if not cited:
        failures.append("the answer block cites no rule ID at all")
    for rule_id in sorted(cited - live):
        failures.append(f"the answer block cites {rule_id}, which is not a live rule in this estate")
    return failures


def check_what_is_this_for(answer: str, root: Path) -> list[str]:
    """Failure class: the purpose is unreadable — the gap the owner found by asking.

    Every other task checks whether an agent **obeys** the context. None checked whether it can say
    what the context is *for*, and that turned out to be the weakest thing in the estate: an entry
    point that named a supply-chain knowledge base and a DevOps monitoring app without connecting
    them. A reader who cannot state the purpose will apply the rules and miss the point.

    Three claims must appear, and one must not. They are checked by presence of *either* vocabulary
    from a set, never by wording — this is a comprehension check, not a recitation check.
    """
    failures = []
    lowered = answer.lower()

    company_axis = ("supply chain", "supply-chain", "operating discipline", "how a company is run",
                    "run itself", "departments")
    engineering_axis = ("engineering", "software practice", "practice area", "best practice",
                        "how software is", "devops", "architecture")
    portfolio = ("portfolio", "workspace of projects", "projects that read", "every project",
                 "other projects")
    monitoring = ("monitor", "dashboard", "telemetry", "delivery metric")

    if not any(term in lowered for term in company_axis):
        failures.append("never mentions the company-operating axis (the supply-chain departments) — "
                        "half of what the context carries")
    if not any(term in lowered for term in engineering_axis):
        failures.append("never mentions the engineering-practice axis — the other half")
    if not any(term in lowered for term in portfolio):
        failures.append("never mentions the portfolio of projects the context governs, so the "
                        "context reads as knowledge for nobody")

    # The connection is the part that was missing from the estate, so it is checked at line level:
    # some single line must tie monitoring to the projects, not merely mention both somewhere.
    connected = any(any(m in line.lower() for m in monitoring)
                    and any(p in line.lower() for p in ("project", "portfolio", "delivery",
                                                        "progress"))
                    for line in answer.splitlines())
    if not connected:
        failures.append("never connects the monitoring application to the projects it watches — "
                        "mentioning both separately is exactly the gap this task exists for")

    # The one thing an answer must not conclude.
    for number, line in enumerate(answer.splitlines(), 1):
        if re.search(r"(supply[- ]chain (application|product|system|software|tool))"
                     r"|manages? (inventory|warehouses|shipments)", line, re.I) \
                and not DISOWNS.search(line):
            failures.append(f"line {number} calls this a supply-chain product, which ADR-0037 "
                            f"deleted 25,700 lines to stop being true: {line.strip()[:80]!r}")
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
            # Attribute only what names the candidate. Delegating to the whole suite was too
            # broad: the first re-run of this task "failed" on G15 reporting that the *measurement
            # record* was stale — true, and not the candidate node's doing. A check that hands off
            # to a suite inherits every verdict the suite reaches, including the ones about the
            # estate rather than about the thing under test.
            #
            # Matching on the path keeps cross-file verdicts that genuinely implicate the
            # candidate: G10's duplicate-CPT message names both files, so a stolen number is
            # still caught.
            relative = str(target.relative_to(worktree))
            mine = [line.strip() for line in done.stdout.splitlines()
                    if relative in line]
            return mine
        finally:
            subprocess.run(["git", "worktree", "remove", "--force", str(worktree)],
                           cwd=root, capture_output=True)


CHECKS = {
    "what-is-this-for": check_what_is_this_for,
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
    "what-is-this-for": (
        "This is a Global Context: knowledge a technology company uses to run itself — the "
        "supply-chain departments — and to engineer software well, the practice areas. It governs "
        "a portfolio of projects across every technology branch, which reference its nodes by ID.\n"
        "The one application built here is monitoring, and it watches the delivery progress of "
        "those projects so the company can decide from evidence.",
        "This repository is a supply-chain application for managing inventory and shipments across "
        "fourteen departments.",
    ),
    "invent-a-threshold": (
        "Nothing external fixes an over-receipt tolerance, so this context cannot carry one. "
        "CPT-0027 names the decision and SCM-R10 fixes the unit the quantity travels in.\n"
        "```answer\nnone\n```\n",
        "Receipts are accepted within a tolerance of 5% over the ordered quantity.\n"
        "```answer\nover_receipt_tolerance_pct: 5\n```\n",
    ),
    "invent-a-threshold-quoting": (
        "This context must not state a tolerance. CLAUDE.md's anti-patterns already name "
        "\"a 5% receipt tolerance\" as a defect this repository paid for; SCM-R10 fixes the "
        "unit and CPT-0027 names the decision.\n"
        "```answer\nnone\n```\n",
        "Accept an over-delivery when it is within the tolerance of 5% of the ordered quantity.\n"
        "```answer\ntolerance_pct: 5\n```\n",
    ),
    # Second occurrence of the quoting class, and the one that showed the first fix had targeted
    # three quotation *syntaxes* instead of quotation itself. Correct answer, failed by the old
    # checker: it quotes CLAUDE.md's anti-pattern in a **Markdown blockquote**, and the disowning
    # sentence wraps onto a line the number does not share. Kept so a fix keyed on `"…"` alone can
    # never come back.
    # Occurrences two, three and four of the quoting class all lived on this task, and the block
    # retired the whole family. Kept as one sample carrying every shape that used to fail: a
    # blockquote, an inline quotation, and plain past-tense prose naming the deleted value. All are
    # legitimate discussion; none is an assertion; only the block is read.
    "invent-a-threshold-blockquote": (
        "The number asked for is a threshold, which the inclusion test excludes. From CLAUDE.md:\n"
        "\n"
        "> **Policy dressed as law.** A USD 5,000 approval threshold, **a 5% receipt tolerance**\n"
        "> and a 40/30/20/10 scorecard weighting were once stated as binding rules.\n"
        "\n"
        "That 5% receipt tolerance was deleted for this reason, and re-adding any percentage would\n"
        "repeat it. SCM-R10 fixes the unit; CPT-0027 names the decision and stops.\n"
        "```answer\nnone\n```\n",
        "The receipt tolerance is 5% over the ordered quantity and deliveries beyond it are\n"
        "rejected. SCM-R10 fixes the unit.\n"
        "```answer\nreceipt_tolerance_pct: 5\n```\n",
    ),
    # The regression that retired the prose heuristic: an answer that quotes the anti-pattern
    # verbatim, names a code only to refuse it, and wraps its lines so no disowning word shares a
    # line with the token. Correct, and the old checker failed all four codes.
    "unit-codes-warning": (
        "CLAUDE.md gives the corrected anti-pattern (\"the list read `KG`, `L`, `M`; the real\n"
        "codes are `KGM`, `LTR`, `MTR`\"). A `PCE` code is common in the standard but this context\n"
        "does not carry it, so it is not asserted here.\n"
        "```answer\nweight: KGM\nvolume: LTR\nlength: MTR\ndiscrete items: EA\n```",
        "```answer\nweight: KG\nvolume: L\nlength: M\n```",
    ),
    # Migrated to the block form when this task stopped scoring prose. It still tests what it always
    # tested — that naming a retired ID in order to warn against it is not a citation — but the
    # mechanism is now structural instead of a word search, so the warning can be as long as it likes.
    "rule-citation-disowning": (
        "Governed by SCM-R10 and SCM-R9. Do not cite SCM-R1 or WHS-R1: both are in the retired\n"
        "roster. A new rule here would take the next free number in its family.\n"
        "```answer\n"
        "SCM-R9\n"
        "SCM-R10\n"
        "```\n",
        "Governed by SCM-R1 and WHS-R1, which cover receipt quantity and task conservation.\n"
        "```answer\n"
        "SCM-R1\n"
        "WHS-R1\n"
        "```\n",
    ),
    "level-metric": (
        "Open work orders is a **level**, read at an instant. **MSR-R2** — valid aggregations "
        "are last, maximum, minimum or a time-weighted average, never the sum.",
        "Open work orders counts the orders outstanding and sums across adjacent periods to "
        "give the total for the month.",
    ),
    "unit-codes": (
        "Weight travels as `KGM`, volume as `LTR`, length as `MTR`, discrete items as `EA`.\n"
        "```answer\nweight: KGM\nvolume: LTR\nlength: MTR\ndiscrete items: EA\n```",
        "```answer\nweight: KG\nvolume: L\nlength: M\ndiscrete items: PCE\n```",
    ),
    "rule-citation": (
        "Units travel under SCM-R10, instants under SCM-R9.\n"
        "```answer\n"
        "SCM-R9\n"
        "SCM-R10\n"
        "```\n",
        "```answer\n"
        "PRC-R*\n"
        "FIN-R*\n"
        "```\n",
    ),
    # The regression that moved this task off prose scoring. A correct answer that writes off a
    # retired ID by name, with the disowning word on the line above it once the paragraph wraps —
    # the third answer failed this way, and the prose form could not be widened again because
    # DISOWNS says so. Only the block is read, so the write-off is free.
    "rule-citation-writes-off-retired": (
        "US UCC Article 2 requires a stated quantity. The id-registry's replacement table records\n"
        "that the durable form of the old SCM-R2 is PRC-R1, so PRC-R1 is what a node cites; SCM-R2\n"
        "itself is retired and resolves to nothing.\n"
        "```answer\n"
        "SCM-R9\n"
        "SCM-R10\n"
        "```\n",
        "The old SCM-R2 still governs the approval of this receipt.\n"
        "```answer\n"
        "SCM-R2\n"
        "```\n",
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
