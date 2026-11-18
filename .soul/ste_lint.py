#!/usr/bin/env python3
"""Fail when prose breaks the writing rules of the bundle.

    ste_lint.py [--root <project>] [--staged] [--report] [<file>...]

Every sentence outside protected text (frontmatter, fenced and indented
blocks, tables, code spans, links, `>` quotations) is checked:
words over the limit, a semicolon, a hedge, a contraction, an -ing verb,
a perfect tense, an agentless passive, a bare pronoun that opens it. A
perfect after a modal ("could have failed") is a hedge and stands. A
sentence ends at `.`, `!` or `?` before a space, whatever follows, so an
identifier or a number may open the next one. A link counts as one
word, LINK, so a slug is never read as prose. A paragraph over 6
sentences, a
non-ASCII byte and a prose line over 79 columns are faults anywhere.
okf.conf `prose` lists the files and directories, default `okf CLAUDE.md`.
`--staged` checks only the staged files among them; `--report` prints
the counts per kind instead of every fault. A word in double quotes is
a mention, not a use. A caption that starts with WRONG or RIGHT has no
length limit. An agentless passive is counted and printed with
`--report`; it is a fault only with `--strict`, because the rule
permits the passive when the actor does not matter. `ascii_exempt` is a path
regex for a file whose non-ASCII is its subject; a dash glyph is a
fault there too. A list item is its own paragraph.
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys

import okfconf

ROOT = okfconf.root(sys.argv)
CONF = okfconf.read(ROOT)
PROSE = okfconf.many(CONF, "prose", ("okf", "CLAUDE.md"))
ASCII_EXEMPT = re.compile(okfconf.one(CONF, "ascii_exempt", r"(?!)"))
SKIP = {"log.md"}
INSTRUCTION, DESCRIPTION, PARAGRAPH, COLUMNS = 20, 25, 6, 79

HEDGE = re.compile(
    r"\b(usually|often|probably|almost always|sometimes|generally|"
    r"typically|basically|essentially|really|very|quite|perhaps|likely|"
    r"arguably|roughly|mostly|tends? to|seems?|e\.g\.|i\.e\.|etc\.?|"
    r"and/or)(?=\W|$)", re.I)
CONTRACTION = re.compile(
    r"\b(\w+n't|(it|that|there|what|let|here|who)'s|(we|you|they)'re|"
    r"(I|we|you|they)'ve|(I|you|we|they|it)'ll|I'm|"
    r"(I|you|we|they|he|she)'d)\b")
MODAL = re.compile(
    r"\b(MUST NOT|MUST|NEVER|ALWAYS|must not|must|never|always|do not|"
    r"Do not|Do NOT|DO NOT|should not|should)\b")
IMPERATIVE = re.compile(
    r"^(Do|Never|Always|Run|Read|Write|Keep|Use|Put|Stop|Ask|Tell|Make|"
    r"Check|Start|Open|Treat|Apply|Hold|Tick|Fix|Add|Delete|Remove|Cut|"
    r"Drop|Avoid|Chain|Name|Split|Decompose|Report|Show|State|Match|Pick|"
    r"Prefer|Say|Go|Let|Try|Find|Give|Take|Leave|Set|Compress|End|Reach|"
    r"Place|Count|Verify|Confirm|Test|Grep|Compare|Reduce|Edit|Commit|"
    r"Refresh|Record|Measure|List|Mark|Carry|Turn|Rewrite|Call|Pass|"
    r"Print|Wait|Answer|Replace|Re-read|Think|Look|Scan|Hunt|Describe|"
    r"Define|Fill|Change|Copy|Move|Pull|Push|Load|Point|Capture|Declare|"
    r"Expect|Spell|Quote|Collapse|Wrap|Align|Return|Judge|Store|Save|"
    r"Follow|Obey|Build|Gate|Trust|Derive|Insert|Separate|Group|Rerun|"
    r"Order|Walk|Raise|Lower|Prove|Resolve|Attach|Rename|Compute|"
    r"Collect|Install|Seed|Refuse|Convert|Flag|Classify|Bring|Create|"
    r"Omit|Link|Size|Front-load|Decide|Break|Pin|Strip|Restore|Discard|"
    r"Interleave|Cite|Note|Brief|Re-create|Trim|Sample|Delegate|Grow)\b")
PRONOUN = re.compile(
    r"^(This|That|These|Those|It) (is|was|are|were|has|have|had|does|"
    r"did|means|matters|holds|fails|includes|reads|signals|happens|"
    r"applies|works|grows|rots|prints|returns|reports|shows|says|runs|"
    r"exists|makes|keeps|gives|takes|stops|lets|tells|costs|sounds|looks|"
    r"counts|needs|lands|catches|covers|changes|differs|turns|stays|"
    r"names|describes|records|carries|feels|comes|goes|gets|leaves|cuts|"
    r"adds|puts|falls|moves|proves|starts|ends|allows|follows|requires|"
    r"depends|remains|serves|produces|forces|lies|wins|loses|hides|lives|"
    r"buys|earns|teaches|answers|opens|closes|hands|sits|lands)\b")
PASSIVE = re.compile(
    r"\b(is|are|was|were|be|been|being|get|gets|got)\b(\s+\w+ly)?\s+"
    r"(\w+(ed|en|wn|lt|pt|ught|uilt|ade|aid|eld|old|one|ung|ent|ost|"
    r"ut|et|it|ead))\b")
NOT_PASSIVE = set("""
    been being open even often golden hidden sudden wooden seen given
    taken written broken forgotten chosen frozen stolen woken spoken
    shown known grown thrown drawn done gone built kept sent lent bent
    spent meant left felt dealt lost cost cut put set hit let read made
    said held sold told found bound ground wound worth content silent
    present absent different fluent frequent recent current parent
    dependent independent evident patient transient urgent intent
    ancient decent latent potent agent moment comment argument document
    element segment statement equipment experiment incident not yet
    then when what that it out but just about right eight lit fit unit
    limit edit split audit explicit implicit merit exit quit hot shot
    lot got dot get met upset exempt unset unknown known""".split())
ING = re.compile(
    r"\b(is|are|was|were|be|been|being|by|while|when|without|before|"
    r"after|of|for|from|on|in|into|than|and|or|start|starts|started|stop|"
    r"stops|stopped|keep|keeps|kept|avoid|avoids|worth|not|to)\s+"
    r"([A-Za-z]+ing)\b(?!-)")
PERFECT = re.compile(
    r"\b(has|have|had)\s+(not\s+)?(been\s+)?(\w+(ed|en)|done|gone|seen|"
    r"taken|given|written|read|run|set|put|cut|kept|left|made|found|held|"
    r"built|sent|met|lost|got|gotten|begun|become|come|known|shown|grown|"
    r"thrown|fallen|broken|chosen|spoken|led|fed|said|told|sold|paid|"
    r"brought|bought|caught|taught|thought|stood|understood|struck|"
    r"stuck|won|worn|drawn|driven|risen|eaten|beaten|split|spread|hit|"
    r"let|shut|quit|lit|slid|dug|spun|hung|swung|bound|wound)\b")
NOT_PERFECT = set("""
    open even often golden hidden sudden wooden seven eleven oxygen
    children kitchen token listen happen red bed need seed feed speed
    indeed shed wed bred sled""".split())
MODAL_HAVE = re.compile(
    r"\b(may|might|could|should|would|must|can|will|shall)(\s+not)?\s*$")
CAPTION = re.compile(r"^(WRONG|RIGHT|BAD|GOOD)\b")
NOUN_ING = set("""
    nothing thing string strings warning warnings setting settings
    something anything everything during bring sing spring ring ping
    king wing swing timing heading headings morning evening meaning
    meanings ceiling building buildings finding findings listing
    listings reading readings writing writings encoding encodings naming
    padding spacing training indenting ordering opening closing mapping
    mappings logging binding bindings spelling wording booking shipping
    landing being existing remaining missing leading trailing pending
    underlying following according including sibling siblings nesting
    reasoning formatting""".split())
DASH = {0x2013: "en dash", 0x2014: "em dash"}
WORD = re.compile(r"[A-Za-z0-9][\w'./:-]*")
SPAN = re.compile(r"`[^`]*`")
LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
ITEM = re.compile(r"^\s*([-*]|\d+\.)\s+(\[[ x]\]\s+)?")
LEAD = re.compile(r"^\*\*[^*]+\*\*:?\s*")
ABBREV = re.compile(r"\b(vs|cf|approx|no|Dr|Mr|Fig|sec|min|al)\.")
QUOTED = re.compile(r'"[^"]*"')
SPLIT = re.compile(r"(?<=[.!?])[\"')]?\s+(?=\S)")


def prose_lines(text):
    """[(lineno, text)] with protected lines dropped; a blank, a heading,
    a table row or a protected block becomes a paragraph break."""
    out = []
    fenced = False
    front = text.startswith("---\n")
    indented = False
    for number, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if front:
            front = not (number > 1 and stripped == "---")
            out.append((number, ""))
        elif stripped.startswith("```"):
            fenced = not fenced
            out.append((number, ""))
        elif fenced or stripped.startswith(("|", ">", "<!--")):
            out.append((number, ""))
        elif stripped == "" or re.match(r"^#{1,6} ", line):
            indented = False
            out.append((number, ""))
        elif re.match(r"^ {4,}\S", line) and not ITEM.match(line) \
                and (indented or out[-1][1] == "" if out else True):
            indented = True
            out.append((number, ""))
        else:
            indented = False
            out.append((number, line))
    return out


def units(lines):
    """Paragraphs as lists of units; a list item is its own unit. A unit
    is (lineno, text) with code spans and links reduced."""
    paragraphs = []
    current = []
    for number, line in lines + [(0, "")]:
        text = LINK.sub("LINK", SPAN.sub("CODE", line)).strip()
        if text == "" and current:
            paragraphs.append(current)
            current = []
        elif text != "" and (ITEM.match(line) or not current):
            current.append([number, text])
        elif text != "":
            current[-1][1] += " " + text
    return paragraphs


def sentences(unit):
    """[(lineno, sentence)] out of one unit. A quoted mention is one
    token while the unit is split, so a period inside it ends nothing."""
    number, text = unit
    text = ITEM.sub("", text)
    text = LEAD.sub("", text)
    text = ABBREV.sub(r"\1<DOT>", text)
    text = re.sub(r"(\w)\.(\w)", r"\1<DOT>\2", text)
    text = text.replace("...", "<ELL>")
    quotes = QUOTED.findall(text)
    for index, quote in enumerate(quotes):
        text = text.replace(quote, f"<Q{index}>", 1)
    parts = SPLIT.split(text)
    out = []
    for part in parts:
        for index, quote in enumerate(quotes):
            part = part.replace(f"<Q{index}>", quote)
        part = part.replace("<DOT>", ".").replace("<ELL>", "...").strip()
        if part:
            out.append((number, part))
    return out


def sentence_faults(sentence):
    """The kinds one sentence fails; a passive is counted, not a fault,
    unless `--strict`."""
    kinds = []
    instruction = bool(MODAL.search(sentence) or IMPERATIVE.match(sentence))
    limit = INSTRUCTION if instruction else DESCRIPTION
    count = len(WORD.findall(sentence))
    mention = QUOTED.sub(" ", sentence)
    if count > limit and not CAPTION.match(sentence):
        kinds.append(f"{count} words, limit {limit}")
    if ";" in mention:
        kinds.append("semicolon")
    for found in PERFECT.finditer(mention):
        word = found.group(4).lower()
        if word not in NOT_PERFECT \
                and not MODAL_HAVE.search(mention[:found.start()]):
            kinds.append(f"perfect '{found.group(0)}'")
    for found in HEDGE.finditer(mention):
        kinds.append(f"hedge '{found.group(1)}'")
    for found in CONTRACTION.finditer(mention):
        kinds.append(f"contraction '{found.group(1)}'")
    for found in ING.finditer(mention):
        word = found.group(2)
        if word.lower() not in NOUN_ING and word[0].islower():
            kinds.append(f"-ing verb '{word}'")
    for found in PASSIVE.finditer(sentence):
        word = found.group(3).lower()
        tail = sentence[found.end():found.end() + 4]
        if word not in NOT_PASSIVE and not word.endswith("ent") \
                and not re.match(r"\s+by\b", tail):
            kinds.append(f"passive '{found.group(0)}'")
    if PRONOUN.match(sentence):
        kinds.append("a bare pronoun opens the sentence")
    return kinds


def line_faults(text, exempt_ascii):
    """Non-ASCII anywhere, a dash glyph even where the file is exempt; a
    prose line over the column limit."""
    faults = []
    fenced = False
    for number, line in enumerate(text.splitlines(), 1):
        for char in sorted(set(line)):
            if ord(char) in DASH or (ord(char) > 126 and not exempt_ascii):
                name = DASH.get(ord(char), f"U+{ord(char):04X}")
                faults.append((number, f"non-ASCII {name}"))
        stripped = line.strip()
        if stripped.startswith("```"):
            fenced = not fenced
        exempt = fenced or stripped.startswith("|") \
            or line.startswith("    ") or "http" in line or "](" in line
        if len(line) > COLUMNS and not exempt:
            faults.append((number, f"{len(line)} columns, limit {COLUMNS}"))
    return faults


def check(path):
    """[(lineno, kind, sentence)] for one file."""
    text = path.read_text(errors="replace")
    rel = path.relative_to(ROOT).as_posix() if path.is_relative_to(ROOT) \
        else path.as_posix()
    exempt = bool(ASCII_EXEMPT.search(rel))
    faults = [(n, kind, "") for n, kind in line_faults(text, exempt)]
    for unit in (u for paragraph in units(prose_lines(text))
                 for u in paragraph):
        found = sentences(unit)
        if len(found) > PARAGRAPH:
            faults.append((found[0][0], f"{len(found)} sentences in one "
                           f"paragraph, limit {PARAGRAPH}", ""))
        for number, sentence in found:
            for kind in sentence_faults(sentence):
                faults.append((number, kind, sentence))
    return sorted(faults)


def listed(argv):
    """The files to check: named ones, else the staged ones, else every
    .md under the prose roots."""
    named = [a for a in argv[1:] if not a.startswith("--")
             and argv[argv.index(a) - 1] != "--root"]
    if named:
        out = [pathlib.Path(a) for a in named]
    else:
        out = []
        for one in PROSE:
            root = ROOT / one
            out += sorted(root.rglob("*.md")) if root.is_dir() \
                else [root] if root.exists() else []
        if "--staged" in argv:
            run = subprocess.run(["git", "diff", "--staged", "--name-only",
                                  "--diff-filter=ACMR"], cwd=ROOT,
                                 capture_output=True, text=True)
            staged = {ROOT / p for p in run.stdout.split()}
            out = [p for p in out if p in staged]
    return [p for p in out if p.name not in SKIP]


def main(argv):
    total = 0
    kinds = {}
    files = listed(argv)
    strict = "--strict" in argv
    for path in files:
        for number, kind, sentence in check(path):
            key = kind.split(" '")[0].split(",")[0]
            key = re.sub(r"^\d+ ", "", key)
            kinds[key] = kinds.get(key, 0) + 1
            total += 1 if strict or key != "passive" else 0
            if "--report" not in argv and (strict or key != "passive"):
                where = path.relative_to(ROOT) if path.is_relative_to(ROOT) \
                    else path
                tail = f": {sentence[:70]}" if sentence else ""
                print(f"  {where}:{number}: {kind}{tail}")
    for key in sorted(kinds, key=kinds.get, reverse=True):
        if "--report" in argv:
            print(f"  {kinds[key]:5d}  {key}")
    print(f"ste: {total} fault(s) over {len(files)} file(s), "
          f"{kinds.get('passive', 0)} passive(s) counted")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
