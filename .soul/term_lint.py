#!/usr/bin/env python3
"""Fail when prose uses a word the lexicon rejects, or names in backticks
an identifier that is nowhere.

    term_lint.py [--root <project>] [--staged] [<file>...]
    term_lint.py [--root <project>] seed [<count>]

A lexicon is a markdown table with a `term` or `name` column; okf.conf
`lexicon` lists the files, default the lexicon rule, and SOUL.md
at the root counts when it exists. The keys of okf.conf are known
names too. Every phrase of a row's `not` column
found in prose is a fault that names the term; a quoted word is a
mention and is not checked, a link (its title and its target) is a
reference and is not checked, and a `**Why:**` block may name an
identifier of the repo its incident happened in. A backticked token
shaped like an identifier or a path must be a path under the project,
its bundle or this checkout, a file name in either, a lexicon term, name
or code entry, or text found in a covered source or in a fenced block
of any prose file.
`seed` splits the identifiers of the covered sources on case and
underscore and prints the words, ranked by the files they appear in,
that no lexicon row names.
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys

import okfconf
import ste_lint

ROOT = ste_lint.ROOT
HERE = pathlib.Path(__file__).resolve().parent.parent
CONF = ste_lint.CONF
LEXICON = okfconf.many(CONF, "lexicon", ("okf/rules/" + "lexicon.md",))
COVERED = okfconf.many(CONF, "covered")
SUFFIX = set(okfconf.many(CONF, "source_suffix"))
SHAPED = re.compile(r"^[A-Za-z_][\w.-]*(\(\))?$|^[\w~.-]*/[\w./~-]+$")
PATH = re.compile(r"^(\.{0,2}/|~/|okf/|bin/|scripts/|tmp/|template/|\.claude/|"
                  r"\.soul/|\.githooks/)|\.\w+$")
KEYWORDS = set("""
    and for the def else import not out return from len with none true
    false self int str list dict set print open path text line file name
    key value sub run main args argv sys get add all any one two""".split())
SPAN = re.compile(r"`([^`\n]+)`")
FENCE = re.compile(r"^```.*?^```", re.M | re.S)
CELL = re.compile(r"`([^`]+)`")
QUOTED = re.compile(r'"[^"]*"')
CAMEL = re.compile(r"(?<=[a-z0-9])(?=[A-Z])")
IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")


def tables(text):
    """Rows of every table whose header names `term` and `not` (or
    `use instead of`), as {column: cell}."""
    rows = []
    header = None
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")] \
            if line.strip().startswith("|") else []
        if cells and header is None and ("term" in cells or "name" in cells):
            header = cells
        elif cells and header and set(cells) <= {"---", ""}:
            pass
        elif cells and header and len(cells) == len(header):
            rows.append(dict(zip(header, cells)))
        elif not cells:
            header = None
    return rows


def lexicon():
    """(rejected, known): [(phrase, term)] and the set of terms and code
    tokens every lexicon declares, plus the keys of okf.conf."""
    rejected = []
    known = set(CONF)
    files = [ROOT / one for one in LEXICON] + [ROOT / "SOUL.md"]
    for path in (p for p in files if p.exists()):
        for row in tables(path.read_text()):
            term = row.get("term") or row.get("name") or ""
            avoid = row.get("not") or row.get("use instead of") or ""
            known.update(CELL.findall(term) or [term])
            known.update(t.strip() for t in term.split(","))
            known.update(CELL.findall(row.get("code", "")))
            for phrase in (p.strip() for p in avoid.split(",")):
                if phrase and phrase != "none":
                    rejected.append((phrase.strip("`"), term))
    return rejected, known


def corpus():
    """(text, names): every covered file's text, and every file name under
    the covered areas, both bundles, the project's .soul and .githooks,
    and this checkout's bin and scripts."""
    text = []
    names = set()
    roots = [ROOT / a for a in COVERED] + [HERE / "bin", HERE / "scripts",
                                           ROOT / ".soul", ROOT / ".githooks",
                                           ROOT / "okf", HERE / "okf"]
    tooling = {"bin", "scripts", ".soul", ".githooks"}
    for one in (p for root in roots if root.is_dir()
                for p in sorted(root.rglob("*"))
                if p.is_file() and not p.name.startswith(".")
                and "__pycache__" not in p.parts):
        names.add(one.name)
        if one.suffix in SUFFIX or one.parent.name in tooling:
            text.append(one.read_text(errors="replace"))
    return "\n".join(text), names


def resolves(token, text, names, known, fenced):
    """Whether a backticked token names something that exists."""
    plain = token.rstrip(":").removeprefix("~/.claude/").removeprefix("./")
    base = plain.split("/")[-1]
    bare = plain.removesuffix("()")
    inside = plain.lstrip("/")
    return (plain in known or token in known or base in names
            or (ROOT / plain).exists() or (HERE / plain).exists()
            or (ROOT / "okf" / inside).exists()
            or (HERE / "okf" / inside).exists()
            or bare in text or bare in fenced)


def why_lines(text):
    """The line numbers inside a `**Why:**` block, where an incident may
    name an identifier of another repo."""
    out = set()
    inside = False
    for number, line in enumerate(text.splitlines(), 1):
        if line.startswith("**Why:**"):
            inside = True
        elif line.startswith(("**", "## ", "- [ ]")):
            inside = False
        if inside:
            out.add(number)
    return out


def spans(text):
    """[(lineno, token)] for every backticked token outside a fence."""
    out = []
    fenced = False
    for number, line in enumerate(text.splitlines(), 1):
        if line.strip().startswith("```"):
            fenced = not fenced
        elif not fenced:
            out += [(number, t) for t in SPAN.findall(line)]
    return out


def shaped(token):
    """An identifier (an underscore, an inner capital, a call) or a path
    (a separator or a suffix); a flag, a placeholder or a phrase is not."""
    return bool(SHAPED.match(token)) and not token.startswith(("-", "#")) \
        and ("_" in token or "()" in token or CAMEL.search(token) is not None
             or PATH.search(token) is not None)


def check(path, rejected, known, text, names, fenced):
    """[(lineno, fault)] for one file."""
    faults = []
    raw = path.read_text(errors="replace")
    for number, line in ste_lint.prose_lines(raw):
        prose = QUOTED.sub(" ", ste_lint.SPAN.sub(" ", line))
        prose = ste_lint.LINK.sub(" ", prose)
        for phrase, term in rejected:
            if re.search(rf"\b{re.escape(phrase)}\b", prose, re.I):
                faults.append((number, f"'{phrase}' is not the term; "
                               f"the lexicon says {term}"))
    told = why_lines(raw)
    for number, token in spans(raw):
        if number not in told and shaped(token) \
                and not resolves(token, text, names, known, fenced):
            faults.append((number, f"`{token}` is not in the source, not a "
                           "path here or in the origin, and has no "
                           "lexicon row"))
    return sorted(faults)


def seed(count, known):
    """Identifier words of the covered sources by file count, minus the
    lexicon's."""
    files = {}
    text, _ = corpus()
    for one in (p for a in COVERED for p in sorted((ROOT / a).rglob("*"))
                if p.is_file() and p.suffix in SUFFIX):
        body = one.read_text(errors="replace")
        words = {w.lower() for ident in set(IDENT.findall(body))
                 for w in CAMEL.sub("_", ident).split("_")
                 if len(w) > 2 and w.lower() not in KEYWORDS}
        for word in words:
            files[word] = files.get(word, 0) + 1
    lower = {k.lower() for k in known}
    ranked = sorted((w for w in files if w not in lower),
                    key=lambda w: (-files[w], w))
    for word in ranked[:count]:
        print(f"  {files[word]:4d}  {word}")


def main(argv):
    status = 0
    rejected, known = lexicon()
    if "seed" in argv[1:]:
        rest = argv[argv.index("seed") + 1:]
        seed(int(rest[0]) if rest else 40, known)
    else:
        text, names = corpus()
        files = ste_lint.listed(argv)
        fenced = "\n".join(f for one in (ROOT / a for a in ste_lint.PROSE)
                            for p in (one.rglob("*.md") if one.is_dir()
                                      else [one] if one.exists() else [])
                            for f in FENCE.findall(p.read_text(errors="replace")))
        total = 0
        for path in files:
            for number, fault in check(path, rejected, known, text, names,
                                       fenced):
                total += 1
                where = path.relative_to(ROOT) if path.is_relative_to(ROOT) \
                    else path
                print(f"  {where}:{number}: {fault}")
        print(f"term: {total} fault(s) over {len(files)} file(s), "
              f"{len(rejected)} rejected phrase(s)")
        status = 1 if total else 0
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv))
