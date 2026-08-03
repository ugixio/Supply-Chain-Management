#!/usr/bin/env python3
"""Doc gates — the executable form of docs/00-governance/knowledge-architecture.md §11.

Implements gates G1-G16 over the tracked knowledge tree (ADR-0012, from the ugixio context
skeleton ADR-0001/0004). Python 3, standard library only.

G8 (English-only) and G13 (`updated:` truthfulness) were both added on 2026-07-29, and both
because a file-by-file review found what the gates could not: one Spanish sentence sitting in
`20-product-model/node-model.md` since the file was written, and an `updated:` stamp that
disagreed with the file's real last change in 164 of 221 governed documents. Neither gate is
clever. Both close a hole that stayed open precisely because closing it needed no cleverness.

Exit status: 0 when every gate passes, 1 otherwise.
"""

from __future__ import annotations

import datetime
import fnmatch
import glob
import hashlib
import os
import re
import subprocess
import sys

# --- Configuration (instantiated for THIS repo; keep in sync with knowledge-arch §3/§8) --

DOCS_DIR = "docs"

TYPES = {
    "governance", "adr", "product-model", "concept", "context-spec", "rule", "skill",
    "engineering", "operations", "program", "how-to", "archive", "transient",
}
OWNERS = {"human", "orchestrator"}  # extend when agent lanes are formalized
STATUSES = {"draft", "active", "superseded", "deprecated", "archived"}
RELATION_TYPES = {
    "governed-by", "implements", "refines", "depends-on",
    "supersedes", "superseded-by", "traces-to", "part-of",
}

REQUIRED_FIELDS = ("id", "title", "type", "owner", "status", "since", "updated")
ID_PATTERN = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
# A definition ends in a colon; an inherited reference uses an em-dash and must NOT count as one,
# or G3 flags false duplicates (improvement-register #4).
#
# The first version required the colon to follow the ID immediately, and that read only half the
# estate: a rule titled `- **ENG-R10 — Rust core boundary (ADR-0035):**` puts an em-dash title
# between the two, so **ten live rules — ENG-R8..R11 and PLT-R1..R6 — were invisible to G3's
# uniqueness check** and a duplicate among them would have passed. Found by the first
# context-adherence run (ADR-0043), which flagged those ten as "not live" and was right about the
# parser and wrong about the estate.
#
# **The discriminator is where the bold span closes, not where the colon is.** A definition puts
# the colon INSIDE the bold — `- **SCM-R9:**`, `- **ENG-R10 — Rust core boundary (ADR-0035):**` —
# while an inherited reference closes the bold after the ID and lets prose follow:
# `- **SCM-R3** — orders, receipts and contracts are financial records: corrected, never erased`.
# Keying on "a colon somewhere after the ID" reads that reference as a definition and reports five
# false duplicates; that regression was written, run and caught here before it reached a commit.
# The unbolded alternative covers `templates/rule.md`, whose placeholders carry no emphasis.
RULE_ID_DEF = re.compile(r"^\s*-\s*(?:\*\*([A-Z]{2,4}-R\d+)(?:\s+—[^*\n]*)?:\*\*"
                         r"|([A-Z]{2,4}-R\d+)\s*:)")
ADR_HEADING = re.compile(r"^##\s+ADR-(\d{4})\b", re.M)

# The apex: the root contract has no front-matter but is a valid relation target.
VIRTUAL_IDS = {"governance-root"}

ROOT_INDEX_ID = "index-docs"  # G5 traversal root

# G9 — context budgets in WORDS (~ tokens / 1.33): always-loaded docs stay lean
# (ADR-0012). CLAUDE.md's budget assumes the U3 dedup pass; tuning a number is an ADR.
PATH_BUDGETS = (
    ("CLAUDE.md", 2600),                       # the root contract (shrinks with U3)
    ("docs/program/evaluation.md", 1200),
    ("docs/program/operating-model.md", 1200),
)
TYPE_BUDGETS = {"skill": 1500, "rule": 1000, "concept": 700, "how-to": 900}
ADR_INDEX_LINE = re.compile(r"^-\s+ADR-(\d{4})\s+—", re.M)

# --- G14 — load-set budgets (ADR-0041) ------------------------------------------------
#
# G9 prices a document. Nothing priced what a session opens *together*, which is the quantity
# the long-context evidence is actually about: degradation is continuous in total input, so
# fifteen individually-compliant documents can still put the middle of the window out of use.
# The manifest lives in prose because it is a statement about how this context is meant to be
# read; the gate parses one fenced block out of it so the declaration and the enforcement
# cannot drift apart.
LOAD_SETS_DOC = f"{DOCS_DIR}/program/load-sets.md"
LOAD_SET_FENCE = re.compile(r"^```load-sets$(.*?)^```$", re.M | re.S)
LOAD_SET_HEADER = re.compile(r"^(\S+)\s*=\s*(\d+)$")

# A member may name a **slice** of a file as `path#selector`, priced instead of the whole file.
# One selector exists and it is not a general mechanism: `adr-index` prices the one-line-per-decision
# entries of the ADR index and not the decision bodies. That is how the file is actually read — the
# index is scanned, a body is looked up by ID — and the difference is 1,950 words against 20,200.
# The owner rejected splitting the bodies into files (backlog X3, it would collide with planned work),
# so the honest alternative is to price the unit a session really loads rather than the file it sits
# in. A selector nobody implements is a hard failure: a manifest that silently prices the wrong thing
# is worse than one that names a file it cannot find.
SLICES = {"adr-index": ADR_INDEX_LINE}

# --- G15 — the context-adherence measurement is not stale (ADR-0043) ------------------
#
# The estate checks its own consistency; G15 checks that somebody checked whether an agent
# *reading* it complies. The measurement is recorded with a digest per context-defining file,
# and the gate fails when any of them has changed since — a rule rewritten after the last
# measurement invalidates it.
#
# Digests rather than dates on purpose. `git log -1 -- <path>` is the obvious way to ask when
# a file last changed and it is wrong here for the reason G13 already paid for: at a shallow
# clone's boundary git reports the graft, so every file looks freshly changed and the gate
# would fire on everything in CI. A content hash needs no history at all.
CONTEXT_EVAL_DOC = f"{DOCS_DIR}/program/context-eval.md"
DIGEST_FENCE = re.compile(r"^```context-digest$(.*?)^```$", re.M | re.S)
DIGEST_UNMEASURED = "(unmeasured)"

# --- G16 — the retired roster is complete and true (ADR-0043 follow-up) ---------------
#
# The retirement tables live in fifteen `rule.md` files. A session changing a rule loads the
# id-registry and the engineering rules — not those fifteen — so nothing it could read told it
# which IDs are dead. The first context-adherence run failed exactly there, citing six retired
# rules it had no way to recognise.
#
# The registry now carries the complete roster, and this gate asserts it equals the union of the
# tables **in both directions**: a roster that quietly falls behind, or that claims a retirement
# that never happened, is worse than no roster because it would be believed.
ID_REGISTRY = f"{DOCS_DIR}/00-governance/id-registry.md"
ROSTER_FENCE = re.compile(r"^```retired-roster$(.*?)^```$", re.M | re.S)
ROSTER_LINE = re.compile(r"^([A-Z]{3}):\s*([\d ]+)$")

# --- G10 — standards provenance (ADR-0015 as narrowed by ADR-0037) --------------------
#
# G10 used to assert that every public symbol in the application code had a concept node.
# ADR-0037 deleted that application: this repository is a *standards context*, not a
# supply-chain product, so there is no code for the gate to police. What matters now is that
# each concept node is traceable to something fixed outside this repository, and that no node
# claims to own an implementation (a link into project code would invert the one-way rule,
# ADR-0024).
CONCEPTS_DIR = f"{DOCS_DIR}/25-concepts"
# A node's CPT number, taken from its title: `# Title (CPT-0026)`.
CPT_IN_TITLE = re.compile(r"^#\s+.*\((CPT-\d{4})\)", re.M)
# Sections a concept node must have, and must not have.
REFERENCES_HEADING = "## References"
IMPLEMENTATIONS_HEADING = "## Implementations"

# --- G11 — retired rules stay retired -------------------------------------------------
#
# ADR-0037 retired 52 rule IDs that stated policy or an implementation detail. A retired ID is
# never reassigned, so a citation of one is not a broken link that G4 can see — it silently
# points at nothing, and a reader takes it as law. The retirement tables in the rule files are
# the machine-readable source: only the FIRST column of a table row declares a retirement (an
# ID named in the "why retired" prose is a live rule being pointed at, not a retired one).
RETIRED_ROW = re.compile(r"^\|\s*\*\*((?:SCM|[A-Z]{3})-R\d+)\*\*\s*\|", re.M)
RULE_ID = re.compile(r"\b((?:SCM|[A-Z]{3})-R\d+)\b")
RETIRED_HEADING = "## Retired rules"

# G12 — a rule citation names an ID, never a family wildcard. `**FIN-R***` reads as law and
# resolves to nothing: it survived every other gate because it is not a broken link, not a
# duplicate, and not a retired ID. 47 of them were citing lifecycle rules that had been retired
# with the deleted application, so the wildcard was hiding exactly what it looked like it covered.
#
# What it flags is the **bold citation form** — `**FIN-R***` — which is how a rule is cited as law
# in a Governing-rules bullet. Naming a family as a set is legitimate ("the SCM-R* family", a
# layout tree, a rule file's own title) and is plain text, so it is not flagged.
#
# `[^*]*` before the family matters: the first version required `**` immediately before it and so
# missed `**SCM-R7 / CMP-R***`, where the bold span opened on the *other* rule in the sentence.
RULE_WILDCARD = re.compile(r"\*\*[^*]*\b((?:SCM|[A-Z]{3})-R)\\?\*\*\*")

# G8's screen (see the gate for why this list is function words only). Kept short on purpose: a
# long list buys nothing and starts colliding with proper nouns and standards titles.
NON_ENGLISH_FUNCTION_WORDS = (
    "está", "están", "también", "según", "así", "más", "porque", "aunque", "desde",
    "siempre", "cada", "debe", "hacer", "mismo", "usuario", "sino", "hasta", "entonces",
    "puede", "sobre todo", "es decir", "sin embargo", "todo está",
)

TODAY = datetime.date.today().isoformat()


def section_body(text: str, heading: str) -> str:
    """The lines under `heading` up to the next same-or-higher-level heading."""
    lines = text.splitlines()
    try:
        start = next(i for i, ln in enumerate(lines) if ln.strip() == heading)
    except StopIteration:
        return ""
    out = []
    for line in lines[start + 1:]:
        if line.startswith("## "):
            break
        out.append(line)
    return "\n".join(out)


def is_allowlisted(path: str) -> bool:
    """Knowledge-architecture §3 — this repo's instantiated allowlist."""
    if path in ("CLAUDE.md", "README.md",
                "docs/standards/REGULATORY_FRAMEWORK.md"):
        return True
    if path.startswith(".claude/") or path.startswith(".github/"):
        return True
    # App/package/service scaffolds may carry their own README (framework convention).
    if re.fullmatch(r"(apps|packages|services)/[^/]+/README\.md", path):
        return True
    # Schema directories carry their own README next to the migrations: the retention values, the
    # forward-only discipline and the compose invocation are operational instructions for whoever
    # touches the DDL, and they are useless one directory away from it (ADR-0036 / Phase M2).
    if re.fullmatch(r"db/[^/]+/README\.md", path):
        return True
    return False


# --- Front-matter parsing (constrained format, §8) ------------------------------------

KEY_LINE = re.compile(r"^([A-Za-z_-]+):\s*(.*)$")
RELATION_LINE = re.compile(
    r"^\s+-\s*\{\s*type:\s*([A-Za-z-]+)\s*,\s*target:\s*([A-Za-z0-9-]+)\s*\}\s*$"
)


def parse_front_matter(text: str):
    """Return (meta dict, error). meta['relations'] is a list of (type, target)."""
    if not text.startswith("---\n"):
        return None, "missing front-matter"
    end = text.find("\n---\n", 3)
    if end == -1:
        return None, "unterminated front-matter"
    meta, relations, in_relations = {}, [], False
    for line in text[4:end].splitlines():
        if not line.strip():
            continue
        rel = RELATION_LINE.match(line)
        if in_relations and rel:
            relations.append((rel.group(1), rel.group(2)))
            continue
        key = KEY_LINE.match(line)
        if key:
            in_relations = key.group(1) == "relations"
            if not in_relations:
                meta[key.group(1)] = key.group(2).strip().strip('"')
            continue
        return None, f"unparseable front-matter line: {line.strip()!r}"
    meta["relations"] = relations
    return meta, None


# --- Content helpers ------------------------------------------------------------------

def strip_code(text: str) -> str:
    """Remove fenced blocks and inline code before scanning for links."""
    out, fenced = [], False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if not fenced:
            out.append(re.sub(r"`[^`]*`", "", line))
    return "\n".join(out)


LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")


def path_links(text: str):
    for target in LINK.findall(strip_code(text)):
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        if "<" in target:  # template placeholder
            continue
        yield target.split("#", 1)[0]


# --- Gate engine ----------------------------------------------------------------------

class Gates:
    def __init__(self):
        self.failures = {}
        self.notes = []

    def fail(self, gate: str, message: str):
        self.failures.setdefault(gate, []).append(message)

    def note(self, message: str):
        """A gate reporting that it could not check, which is not the same as passing."""
        self.notes.append(message)

    def report(self, docs_count: int) -> int:
        names = {
            "G1": "no stray docs", "G2": "front-matter validity",
            "G3": "ID uniqueness", "G4": "link integrity", "G5": "no orphans",
            "G6": "authority acyclicity", "G7": "status & supersession",
            "G9": "context budget & disclosure",
            "G10": "standards provenance (source cited, no owned code)",
            "G11": "retired rules stay retired",
            "G12": "rule citations name an ID",
            "G8": "English-only (screened)",
            "G13": "`updated:` matches the real last change",
            "G14": "load-set budgets (what is read together)",
            "G15": "the context-adherence measurement is not stale",
            "G16": "the retired roster is complete and true",
        }
        ok = True
        for gate in sorted(names, key=lambda name: int(name[1:])):
            issues = self.failures.get(gate, [])
            if issues:
                ok = False
                print(f"FAIL {gate} ({names[gate]}):")
                for issue in issues:
                    print(f"  - {issue}")
            else:
                print(f"PASS {gate} ({names[gate]})")
        print("INFO G8 screens for non-English function words; judging whether prose reads as "
              "English is still a reviewer's job (knowledge-architecture §11)")
        for note in self.notes:
            print(f"INFO {note}")
        print(f"{'GREEN' if ok else 'RED'} — {docs_count} governed docs checked")
        return 0 if ok else 1


def tier_of(path: str, doc_type: str):
    """Authority tier from location (knowledge-architecture §2). None = meta."""
    parts = path.split("/")
    if len(parts) < 2 or parts[0] != DOCS_DIR:
        return None
    top = parts[1]
    if top in ("00-governance", "program", "standards", "_source"):
        return None
    tiers = {"10-decisions": 2, "20-product-model": 3, "25-concepts": 3,
             "30-foundation": 4, "40-contexts": 4,
             "50-engineering": 6, "60-operations": 6}
    tier = tiers.get(top)
    if tier is None:
        return None
    if top in ("30-foundation", "40-contexts") and doc_type == "skill":
        return 6
    if top == "40-contexts" and doc_type == "context-spec":
        return 5
    return tier


def main() -> int:
    root = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True
    ).stdout.strip()
    if not root:
        print("RED — not a git repository; the gates run over the tracked tree")
        return 1
    os.chdir(root)
    tracked = subprocess.run(
        ["git", "ls-files"], capture_output=True, text=True
    ).stdout.splitlines()

    gates = Gates()
    docs = {}  # path -> (meta, body text)

    # G1 + G2 — classification, front-matter presence and validity.
    for path in tracked:
        if not path.endswith(".md") or is_allowlisted(path):
            continue
        if not path.startswith(f"{DOCS_DIR}/"):
            gates.fail("G1", f"{path}: tracked .md outside {DOCS_DIR}/ and not allowlisted")
            continue
        try:
            text = open(path, encoding="utf-8").read()
        except OSError as exc:
            gates.fail("G1", f"{path}: unreadable ({exc})")
            continue
        meta, err = parse_front_matter(text)
        if err:
            gates.fail("G1", f"{path}: {err}")
            continue
        docs[path] = (meta, text)
        for field in REQUIRED_FIELDS:
            if not meta.get(field):
                gates.fail("G2", f"{path}: missing required field '{field}'")
        checks = (("type", TYPES), ("owner", OWNERS), ("status", STATUSES))
        for field, vocab in checks:
            value = meta.get(field)
            if value and value not in vocab:
                gates.fail("G2", f"{path}: {field} '{value}' not in vocabulary")
        doc_id = meta.get("id", "")
        if doc_id and not ID_PATTERN.match(doc_id):
            gates.fail("G2", f"{path}: id '{doc_id}' does not match the id pattern")
        for field in ("since", "updated"):
            value = meta.get(field, "")
            if value and not DATE_PATTERN.match(value):
                gates.fail("G2", f"{path}: {field} '{value}' is not YYYY-MM-DD")
        for rel_type, _ in meta["relations"]:
            if rel_type not in RELATION_TYPES:
                gates.fail("G2", f"{path}: relation type '{rel_type}' not in vocabulary")

    # G3 — uniqueness across doc ids, rule IDs and ADR numbers.
    by_id = {}
    for path, (meta, text) in docs.items():
        doc_id = meta.get("id")
        if not doc_id:
            continue
        if doc_id in by_id:
            gates.fail("G3", f"duplicate id '{doc_id}': {by_id[doc_id]} and {path}")
        else:
            by_id[doc_id] = path
    seen_rules = {}
    for path, (meta, text) in docs.items():
        if meta.get("type") != "rule":
            continue
        for line in text.splitlines():
            match = RULE_ID_DEF.match(line)
            if match:
                rule_id = match.group(1) or match.group(2)
                if rule_id in seen_rules:
                    gates.fail("G3", f"duplicate rule ID '{rule_id}': "
                                     f"{seen_rules[rule_id]} and {path}")
                else:
                    seen_rules[rule_id] = path
    seen_adrs = {}
    for path, (meta, text) in docs.items():
        if meta.get("type") != "adr":
            continue
        for number in ADR_HEADING.findall(text):
            if number in seen_adrs:
                gates.fail("G3", f"duplicate ADR-{number} in {path}")
            else:
                seen_adrs[number] = path

    # G4 — every relation target and every path link resolves.
    known_ids = set(by_id) | VIRTUAL_IDS
    for path, (meta, text) in docs.items():
        for rel_type, target in meta["relations"]:
            if target not in known_ids:
                gates.fail("G4", f"{path}: relation {rel_type} -> unknown id '{target}'")
        base = os.path.dirname(path)
        for link in path_links(text):
            resolved = os.path.normpath(os.path.join(base, link))
            if not os.path.exists(resolved):
                gates.fail("G4", f"{path}: broken link '{link}'")

    # G5 — traversal via part-of reaches every doc from the root index.
    parent = {}
    for path, (meta, _) in docs.items():
        targets = [t for rel, t in meta["relations"] if rel == "part-of"]
        if targets:
            parent[meta.get("id")] = targets[0]
        elif meta.get("id") != ROOT_INDEX_ID:
            gates.fail("G5", f"{path}: no part-of relation (orphan)")
    for doc_id in parent:
        seen, current = set(), doc_id
        while current in parent and current not in seen:
            seen.add(current)
            current = parent[current]
        if current != ROOT_INDEX_ID:
            gates.fail("G5", f"{by_id.get(doc_id, doc_id)}: part-of chain does not "
                             f"reach '{ROOT_INDEX_ID}' (stops at '{current}')")

    # G6 — authority direction and acyclicity.
    edges = {}
    for path, (meta, _) in docs.items():
        doc_id = meta.get("id")
        doc_tier = tier_of(path, meta.get("type", ""))
        for rel_type, target in meta["relations"]:
            if rel_type in ("governed-by", "supersedes", "depends-on"):
                edges.setdefault(doc_id, []).append(target)
            if rel_type == "governed-by" and target in by_id:
                target_meta, _ = docs[by_id[target]]
                target_tier = tier_of(by_id[target], target_meta.get("type", ""))
                if doc_tier is not None and target_tier is not None \
                        and target_tier >= doc_tier:
                    gates.fail("G6", f"{path}: governed-by '{target}' does not point "
                                     f"up (tier {doc_tier} -> {target_tier})")
    state = {}  # 0 visiting, 1 done

    def has_cycle(node, stack):
        state[node] = 0
        for nxt in edges.get(node, []):
            if state.get(nxt) == 0:
                gates.fail("G6", "authority cycle: " + " -> ".join(stack + [nxt]))
                return True
            if nxt not in state and has_cycle(nxt, stack + [nxt]):
                return True
        state[node] = 1
        return False

    for node in list(edges):
        if node not in state:
            has_cycle(node, [node])

    # G9 — context budgets and decision-index completeness (ADR-0012).
    for path in tracked:
        if not path.endswith(".md"):
            continue
        for pattern, budget in PATH_BUDGETS:
            if fnmatch.fnmatch(path, pattern):
                try:
                    words = len(open(path, encoding="utf-8").read().split())
                except OSError:
                    break
                if words > budget:
                    gates.fail("G9", f"{path}: {words} words exceeds its always-loaded "
                                     f"budget of {budget}")
                break
    for path, (meta, text) in docs.items():
        budget = TYPE_BUDGETS.get(meta.get("type", ""))
        if budget:
            words = len(text.split())
            if words > budget:
                gates.fail("G9", f"{path}: {words} words exceeds the "
                                 f"{meta['type']}-type budget of {budget}")
        if meta.get("type") == "adr":
            indexed = set(ADR_INDEX_LINE.findall(text))
            for number in ADR_HEADING.findall(text):
                if number not in indexed:
                    gates.fail("G9", f"{path}: ADR-{number} has no one-line entry in "
                                     f"the decision index")

    # G7 — supersession integrity.
    for path, (meta, _) in docs.items():
        if meta.get("status") != "superseded":
            continue
        successors = [t for rel, t in meta["relations"] if rel == "superseded-by"]
        if not successors:
            gates.fail("G7", f"{path}: superseded without a superseded-by edge")
            continue
        for target in successors:
            target_path = by_id.get(target)
            if target_path:
                target_status = docs[target_path][0].get("status")
                if target_status not in ("active", "archived"):
                    gates.fail("G7", f"{path}: superseded-by '{target}' has status "
                                     f"'{target_status}' (needs active/archived)")

    # G10 — standards provenance (ADR-0015 as narrowed by ADR-0037).
    #
    # A concept node earns its place by being traceable to something fixed outside this
    # repository, and by NOT claiming to own code. Three checks:
    #   1. one CPT number, one node — two files claiming an ID is how a concept silently forks;
    #   2. every node cites a source (`## References`, non-empty);
    #   3. no node carries an `## Implementations` section — implementations are a project's,
    #      and a link into project code would invert the one-way rule (ADR-0024).
    cpt_owner = {}
    for path, (meta, text) in docs.items():
        if meta.get("type") != "concept" or not path.startswith(f"{CONCEPTS_DIR}/"):
            continue
        if path.endswith("_index.md"):
            continue

        numbers = CPT_IN_TITLE.findall(text)
        if not numbers:
            gates.fail("G10", f"{path}: title carries no CPT number "
                              f"(expected '# Title (CPT-NNNN)')")
        for cpt in numbers:
            if cpt in cpt_owner:
                gates.fail("G10", f"{path}: {cpt} is already claimed by "
                                  f"{cpt_owner[cpt]} — one concept, one node "
                                  f"(id-registry §1)")
            else:
                cpt_owner[cpt] = path

        if not section_body(text, REFERENCES_HEADING).strip():
            gates.fail("G10", f"{path}: no '{REFERENCES_HEADING}' content — a node must cite "
                              f"the standard, regulation or identity that fixes it (ADR-0037)")

        if IMPLEMENTATIONS_HEADING in text:
            gates.fail("G10", f"{path}: carries '{IMPLEMENTATIONS_HEADING}' — the context "
                              f"defines concepts, it does not own their code (ADR-0037)")

    # G11 — a retired rule ID is never cited as law (ADR-0037).
    retired, retirement_home = {}, {}
    for path, (_meta, text) in docs.items():
        if RETIRED_HEADING not in text:
            continue
        table = text.split(RETIRED_HEADING, 1)[1]
        for stop in ("## Project decisions", "## Anti-states", "## Inherited rules"):
            table = table.split(stop, 1)[0]
        for rule_id in RETIRED_ROW.findall(table):
            retired[rule_id] = path
            retirement_home[rule_id] = path
    # Three homes may name a retired ID, because naming it there is the opposite of citing
    # it as law: the rule file that declares the retirement, the id-registry (the allocation
    # authority — a retirement is an allocation fact), and the ADRs (append-only history;
    # rewriting an old decision to remove an ID would falsify the record).
    declaring = {"docs/00-governance/id-registry.md"}
    # EVERY tracked Markdown file is checked, not only the governed tree. G11 first shipped over
    # front-matter documents alone and reported green while the skills tree cited three retired
    # rules: a gate over part of the estate certifies only the part it can see. `.claude/**` is
    # the worst place to leave uncovered, because those files instruct the next session's work.
    checked = dict(docs)
    for path in tracked:
        if path in checked or not path.endswith(".md"):
            continue
        try:
            checked[path] = ({}, open(path, encoding="utf-8").read())
        except OSError:
            continue
    for path, (meta, text) in checked.items():
        if path in declaring or meta.get("type") == "adr":
            continue
        for number, line in enumerate(text.splitlines(), 1):
            for rule_id in set(RULE_ID.findall(line)):
                if rule_id not in retired:
                    continue
                if retirement_home[rule_id] == path:
                    continue        # the file that declares the retirement may name it
                gates.fail("G11", f"{path}:{number} cites retired rule {rule_id} — it was "
                                  f"retired in {retirement_home[rule_id]} and is never "
                                  f"reassigned, so the citation resolves to nothing "
                                  f"(ADR-0037)")

    # G16 — the registry's roster equals the union of the retirement tables (both directions).
    try:
        registry = open(ID_REGISTRY, encoding="utf-8").read()
    except OSError:
        gates.fail("G16", f"{ID_REGISTRY} is missing — it is the allocation authority")
    else:
        fence = ROSTER_FENCE.search(registry)
        if not fence:
            gates.fail("G16", f"{ID_REGISTRY}: no ```retired-roster block to read")
        else:
            rostered = set()
            for line in fence.group(1).splitlines():
                if not line.strip() or line.lstrip().startswith("#"):
                    continue
                entry = ROSTER_LINE.match(line.strip())
                if not entry:
                    gates.fail("G16", f"{ID_REGISTRY}: '{line.strip()}' is not '<FAM>: <n> <n> …'")
                    continue
                rostered |= {f"{entry.group(1)}-R{n}" for n in entry.group(2).split()}
            for rule_id in sorted(set(retired) - rostered):
                gates.fail("G16", f"{rule_id} is retired in {retired[rule_id]} but missing from "
                                  f"the roster — a session reading only the registry would take "
                                  f"it for a live rule")
            for rule_id in sorted(rostered - set(retired)):
                gates.fail("G16", f"the roster lists {rule_id} as retired and no rule file "
                                  f"retires it — the roster is claiming something untrue")

    # G12 — a rule citation names an ID. Same estate as G11, and the rule files themselves are
    # included: a family wildcard is no more meaningful in a rule than in a concept node.
    #
    # A wildcard inside a code span is a **mention**, not a citation — the same declaring-versus-
    # citing distinction G11 draws. The gate itself has to be documented somewhere, and the three
    # records that explain why it exists quote the pattern in backticks.
    for path, (_meta, text) in checked.items():
        for number, line in enumerate(text.splitlines(), 1):
            line = re.sub(r"`[^`]*`", "", line)
            for family in set(RULE_WILDCARD.findall(line)):
                gates.fail("G12", f"{path}:{number} cites {family}* — a family wildcard is not a "
                                  f"citation: it reads as law and resolves to no rule. Name the "
                                  f"live ID, or say plainly that no rule fixes this")

    # G8 — English only (ADR-0003), screened. A word list cannot certify that prose reads as
    # English, so this gate does not claim to: it catches the *carrier* of the failure this
    # repository actually had, which is a sentence written in the author's other language and
    # never noticed. The list holds function words only. A content word can be a legitimate
    # quotation ("Incoterms", a standard's French title, a supplier's name); a function word
    # cannot — `está` and `desde` do not appear in an English sentence by accident.
    for path, (_meta, text) in checked.items():
        for number, line in enumerate(text.splitlines(), 1):
            stripped = strip_code(line).lower()
            for word in NON_ENGLISH_FUNCTION_WORDS:
                if re.search(rf"(?<![\w-]){re.escape(word)}(?![\w-])", stripped):
                    gates.fail("G8", f"{path}:{number} contains the non-English function word "
                                     f"'{word}' — ADR-0003 makes English the single working "
                                     f"language for every artifact in this repository")
                    break

    # G13 — `updated:` tells the truth. The field is only worth having if it moves when the file
    # does, and a reader who cannot trust it will not read it: a 2026-07-19 stamp on a file
    # rewritten this week is worse than no stamp, because it is evidence for a false conclusion.
    #
    # Scope is the CURRENT change, not the whole history — the moment the stamp is written is the
    # only moment it can be written honestly. Getting that scope right took two attempts, and the
    # first one was RED in CI three times while the local gate was green:
    #
    #   * `git show --name-only HEAD` needs HEAD's parent to compute a diff. `actions/checkout`
    #     clones at **depth 1**, which grafts HEAD into a parentless boundary — so git reports the
    #     whole tree as added and the gate demanded today's date on all 222 documents.
    #   * On a `pull_request` event, checkout uses the synthetic **merge ref**. Its first parent is
    #     the base branch, so HEAD's diff is everything the branch changes against base — every
    #     file of every commit in the PR, not the one commit being stamped.
    #
    # So the scope is computed from what is actually knowable, and the gate says out loud when it
    # cannot check rather than inventing an answer. The lesson is the one already in the register:
    # verify the gate against the environment that runs it, not only the one that wrote it.
    dirty = {
        line[3:].strip().strip('"')
        for line in subprocess.run(["git", "status", "--porcelain"],
                                   capture_output=True, text=True).stdout.splitlines()
        if line[:2] != "??"
    }
    skip_reason = None
    if dirty:
        # Authoring time: the stamp is being written now, so it must say now.
        changed, expected, why = dirty, TODAY, "is modified in the working tree"
    else:
        lineage = subprocess.run(["git", "rev-list", "--parents", "-n", "1", "HEAD"],
                                 capture_output=True, text=True).stdout.split()
        parents = lineage[1:]
        parent_present = bool(parents) and subprocess.run(
            ["git", "cat-file", "-e", f"{parents[0]}^{{commit}}"],
            capture_output=True).returncode == 0
        shallow = subprocess.run(["git", "rev-parse", "--is-shallow-repository"],
                                 capture_output=True, text=True).stdout.strip() == "true"
        if len(parents) > 1:
            # A merge commit changes no file of its own; each side was gated when it was authored.
            skip_reason = "HEAD is a merge commit, which stamps no file of its own"
        elif not parents:
            # git honours `.git/shallow`: at the boundary HEAD reports NO parents, so its diff is
            # the entire tree. This is the exact shape that turned the gate red in CI.
            skip_reason = ("HEAD has no parent to diff against — "
                           + ("this clone is shallow, so fetch-depth must be at least 2"
                              if shallow else "HEAD is the repository's root commit"))
        elif not parent_present:
            skip_reason = ("HEAD's parent commit is not in this clone, so its diff would name "
                           "every tracked file — fetch-depth must be at least 2")
        if skip_reason:
            changed, expected, why = set(), TODAY, ""
        else:
            head = subprocess.run(["git", "show", "--pretty=format:%ad", "--date=short",
                                   "--name-only", "HEAD"], capture_output=True, text=True).stdout
            head_lines = head.splitlines()
            expected = head_lines[0].strip() if head_lines else TODAY
            changed = {line for line in head_lines[1:] if line.strip()}
            why = "was changed by HEAD"
    for path in sorted(changed & docs.keys()):
        stamped = docs[path][0].get("updated", "")
        if stamped != expected:
            gates.fail("G13", f"{path}: front-matter says updated: {stamped or '(none)'} but the "
                              f"file {why} ({expected}) — stamp the change or do not claim a date")
    if skip_reason:
        gates.note(f"G13 checked nothing: {skip_reason}. The stamp was gated when the change was "
                   f"authored (dirty tree) and on the branch push (single parent, depth 2)")

    # G14 — a load set is priced as a whole (ADR-0041). The largest set is printed on every run
    # whether or not it passes: the failure mode this gate exists for is growth nobody noticed,
    # and a number seen once a day is what stops that.
    try:
        manifest = open(LOAD_SETS_DOC, encoding="utf-8").read()
    except OSError:
        gates.fail("G14", f"{LOAD_SETS_DOC} is missing — the load-set manifest is the gate's input")
    else:
        fence = LOAD_SET_FENCE.search(manifest)
        if not fence:
            gates.fail("G14", f"{LOAD_SETS_DOC}: no ```load-sets block to read")
        else:
            sets, name, budget = {}, None, 0
            for line in fence.group(1).splitlines():
                if not line.strip() or line.lstrip().startswith("#"):
                    continue
                header = LOAD_SET_HEADER.match(line.strip())
                if header and not line.startswith((" ", "\t")):
                    name, budget = header.group(1), int(header.group(2))
                    sets[name] = (budget, [])
                elif name:
                    sets[name][1].append(line.strip())
                else:
                    gates.fail("G14", f"{LOAD_SETS_DOC}: '{line.strip()}' precedes any set header")
            measured = {}
            for name, (budget, members) in sets.items():
                total = 0
                for member in members:
                    target, _, selector = member.partition("#")
                    if selector and selector not in SLICES:
                        gates.fail("G14", f"load set '{name}' names slice '{selector}', which no "
                                          f"selector implements — known: "
                                          f"{', '.join(sorted(SLICES))}")
                        continue
                    matches = sorted(glob.glob(target, recursive=True))
                    if not matches:
                        gates.fail("G14", f"load set '{name}' names '{target}', which matches no "
                                          f"file — a manifest pointing at nothing prices nothing")
                        continue
                    for path in matches:
                        text = open(path, encoding="utf-8").read()
                        if selector:
                            kept = SLICES[selector].findall(text)
                            if not kept:
                                gates.fail("G14", f"load set '{name}': slice '{selector}' selects "
                                                  f"nothing in {path}")
                            total += sum(len(line.split()) for line in
                                         [ln for ln in text.splitlines()
                                          if SLICES[selector].match(ln)])
                        else:
                            total += len(text.split())
                measured[name] = total
                if total > budget:
                    gates.fail("G14", f"load set '{name}': {total} words read together exceeds its "
                                      f"budget of {budget} — split the set or move the budget in "
                                      f"an ADR, but do not let it drift")
            if measured:
                worst = max(measured, key=measured.get)
                gates.note(f"G14 largest load set is '{worst}' at {measured[worst]:,} words "
                           f"(~{int(measured[worst] * 1.33):,} tokens); "
                           + " · ".join(f"{n} {w:,}" for n, w in sorted(measured.items())))

    # G15 — the context-adherence measurement still describes this context (ADR-0043).
    try:
        record = open(CONTEXT_EVAL_DOC, encoding="utf-8").read()
    except OSError:
        gates.fail("G15", f"{CONTEXT_EVAL_DOC} is missing — the measurement record is the input")
    else:
        fence = DIGEST_FENCE.search(record)
        if not fence:
            gates.fail("G15", f"{CONTEXT_EVAL_DOC}: no ```context-digest block to read")
        else:
            unmeasured, checked = [], 0
            for line in fence.group(1).splitlines():
                if not line.strip() or line.lstrip().startswith("#"):
                    continue
                parts = line.split()
                if len(parts) != 2:
                    gates.fail("G15", f"{CONTEXT_EVAL_DOC}: '{line.strip()}' is not "
                                      f"'<path> <digest>'")
                    continue
                path, recorded = parts
                if not os.path.exists(path):
                    gates.fail("G15", f"the record names '{path}', which does not exist — a "
                                      f"measurement over a file nobody kept measures nothing")
                    continue
                if recorded == DIGEST_UNMEASURED:
                    unmeasured.append(path)
                    continue
                actual = hashlib.sha256(open(path, "rb").read()).hexdigest()[:12]
                checked += 1
                if actual != recorded:
                    gates.fail("G15", f"{path} has changed since the context-adherence "
                                      f"measurement (recorded {recorded}, now {actual}) — re-run "
                                      f"`tools/context_eval.py` and record the result, or the "
                                      f"estate is claiming a result about a context it no "
                                      f"longer has")
            if unmeasured:
                gates.note(f"G15 checked {checked} of {checked + len(unmeasured)} context files: "
                           f"{len(unmeasured)} still read {DIGEST_UNMEASURED}, so no measurement "
                           f"exists to be stale ({', '.join(unmeasured)}). This is a skip, not a "
                           f"pass — see {CONTEXT_EVAL_DOC} §Last measurement")

    return gates.report(len(docs))


if __name__ == "__main__":
    sys.exit(main())
