---
id: how-to-run-the-evaluation
title: "How to run the context-adherence evaluation"
type: how-to
owner: orchestrator
status: active
since: 2026-08-03
updated: 2026-08-03
relations:
  - { type: part-of, target: index-program }
  - { type: governed-by, target: index-adr }
---
# How to run the context-adherence evaluation

> **For whoever G15 has just turned red, or who changed something a task depends on.** The reasoning
> is in ADR-0043 and the record is `program/context-eval.md`; neither is restated here. This is the
> procedure, and the two ways it has been got wrong.

## 0. Know what it measures, or you will read the result wrong

Seventeen gates prove the estate is **internally consistent**. This proves something else and much
harder: that an agent **reading** the context produces something that conforms to it. That is the
repository's whole premise, and it was unmeasured until ADR-0043.

**The manifest is under test too.** If a task fails because its declared load set does not contain
what the task needs, the *manifest* is the defect — not the answer. This has happened, and the first
time it happened the wrong thing got fixed.

## 1. When it must be re-run

    python3 tools/verify.py        # G15 names every file whose digest moved

G15 keys freshness to a **content digest per file**, not to a date, because a shallow clone makes
`git log` report every file as freshly changed. Fourteen files are watched — every file in a task's
declared load set. Any one of them moving invalidates the measurement, **including cosmetically**;
that false-alarm rate is the accepted cost of a claim that can be checked at all.

## 2. Get the prompts, and give each one a cold subagent

    python3 tools/context_eval.py --list
    python3 tools/context_eval.py --prompt <task>

**The subject must be a cold subagent, loaded with the declared load set and nothing else.** This is
not ceremony. A session that just wrote the rule will cite it from memory and score a meaningless
100%: you would be measuring the session, not the context. Read the task's load set out of
`program/load-sets.md` and instruct the subagent, in as many words, to read *only* those files.

Write each answer to a file. Then:

    python3 tools/context_eval.py --check <task> <file>

## 3. Re-run the whole cycle, not the tasks you think changed

The first cycle scored five tasks against three different states of the tree and had to say so in
prose, because the digests cannot know that an edit was immaterial. Re-running everything costs a few
minutes and buys a record that means exactly what it says.

## 4. Record it — and record the failures, not just the score

In `program/context-eval.md`: the verdict per task, **what actually happened** in one line, and a
refreshed `context-digest` block:

    python3 -c "import hashlib,sys;print(hashlib.sha256(open(sys.argv[1],'rb').read()).hexdigest()[:12])" <file>

A `FAIL → PASS` row is worth more than a `PASS` row, because it names a defect and the fix that
closed it. Both cycles so far earned their keep through their failures, not their scores.

## 5. When a task fails, diagnose past the first cause

**Ask what the agent was given before asking what it did.** A failure that traces to an absent input
is a manifest defect wearing an agent's clothes, and the cheapest fix is usually to make a document
already in the set carry the missing fact rather than to add a document.

Then keep going. The `unit-codes` regression had **two** causes: a checker that could not tell a code
being asserted from a code being quoted, and a load set that could not answer the question. Fixing the
checker explained the symptom completely and would have left the real defect in place.

## 6. Changing a checker is a decision, not a patch

Every checker carries a **compliant and a violating sample** and must pass the first and fail the
second:

    python3 tools/context_eval.py --self-test

- A real miscall becomes a **permanent regression sample**, so a field-found error becomes a test
  rather than a patch nobody re-runs.
- **A checker that searches for the shape of a defect fires on text that names the defect** — and in
  this corpus that text concentrates in the *correct* answers. Prefer changing the document; weaken
  the check only when the document cannot say what it needs to.
- **When a heuristic has been widened enough times that a threshold was written down, honour it.**
  The prose-disowning filter reached its declared sixth occurrence and was replaced by a scored
  `answer` block, not widened a seventh time. Give a claim a structure instead of inferring it from
  sentences.

## When this is not the guide you want

- **Adding a task** — ask first what question the corpus *cannot* answer today. An evaluation built
  from past failures only tests the classes that already failed.
- **Testing a gate** rather than the context — `tools/test_gates.py` and ADR-0042.
- **A judge model** — no. The bias data is in ADR-0043, and a judge cannot be a gate in an estate
  whose other checks are deterministic.
