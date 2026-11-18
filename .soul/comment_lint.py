#!/usr/bin/env python3
"""Fail when a diff adds prose to source instead of to okf/.

    comment_lint.py [--root <project>] [--staged]

okf.conf `comment_prefix // .py=#`: a bare value is the default and
`suffix=value` overrides it for that suffix, so `#` counts in Python
files and never on a C preprocessor line.
"""
import pathlib
import re
import subprocess
import sys

import okfconf

MAX_ADDED = 0
MAX_BLOCK = 4
MAX_RATIO = 0.25

ROOT = okfconf.root(sys.argv)
CONF = okfconf.read(ROOT)
DIRS = tuple(okfconf.many(CONF, "comment_dirs"))
SUFFIXES = tuple(okfconf.many(CONF, "comment_suffix"))
PREFIXES = okfconf.many(CONF, "comment_prefix", ("//",))
DEFAULT_PREFIX = next((p for p in PREFIXES if "=" not in p), "//")
PREFIX_BY_SUFFIX = dict(p.split("=", 1) for p in PREFIXES if "=" in p)

def prefix_for(path):
    suffix = pathlib.Path(path).suffix
    return PREFIX_BY_SUFFIX.get(suffix, DEFAULT_PREFIX)
# A generated file's banner is emitted, not written, so its comment lines are
# not a choice anyone made and the budget cannot be spent on them.
GENERATED = tuple(okfconf.many(CONF, "generated"))

# Words that only appear when a comment is telling the story of how the code
# came to be, rather than what it is.
NARRATION = [
    "measured", "measurement", "the sweep", "experiment", "turns out",
    "used to", "instead of the old", "we tried", "this session",
    "revert before", "was a ", "no longer", "previously", "originally",
    "which is why it works", "the whole reason",
]

def added_lines(staged):
    cmd = ["git", "diff", "--unified=0"]
    if staged:
        cmd.append("--staged")
    out = subprocess.run(cmd, capture_output=True, text=True,
                         cwd=ROOT).stdout
    path, rows = None, []
    for line in out.splitlines():
        if line.startswith("+++ b/"):
            path = line[6:]
        elif line.startswith("+") and not line.startswith("+++"):
            if path and path.endswith(SUFFIXES) \
                    and path not in GENERATED \
                    and any(path.startswith(d) for d in DIRS):
                rows.append((path, line[1:]))
    return rows

def main():
    rows = added_lines("--staged" in sys.argv)
    faults, comments, code, block, start = [], 0, 0, 0, None
    for path, text in rows:
        stripped = text.strip()
        prefix = prefix_for(path)
        if stripped.startswith(prefix) and not stripped.startswith("#!"):
            comments += 1
            block += 1
            start = start or (path, stripped)
            body = stripped.lstrip(prefix + " ").lower()
            for marker in NARRATION:
                if marker in body:
                    faults.append(f"{path}: narration ({marker!r}): {stripped}")
        else:
            if block > MAX_BLOCK and start:
                faults.append(
                    f"{start[0]}: {block}-line comment block, max {MAX_BLOCK}"
                    f" -- move the reasoning to ./okf/: {start[1]}")
            block, start = 0, None
            if stripped:
                code += 1
    if block > MAX_BLOCK and start:
        faults.append(f"{start[0]}: {block}-line comment block, max "
                      f"{MAX_BLOCK}: {start[1]}")
    ratio = comments / code if code else 0.0
    if comments > MAX_ADDED:
        faults.append(f"added {comments} comment line(s); the budget is "
                      f"{MAX_ADDED}. Delete them and write the prose as an "
                      f"./okf/ concept. Do NOT raise MAX_ADDED and do NOT "
                      f"stop to ask -- this fault is yours to clear.")
    if ratio > MAX_RATIO:
        faults.append(f"added {comments} comment lines against {code} of code"
                      f" ({ratio:.0%}, max {MAX_RATIO:.0%})")
    for fault in faults:
        print("comment-lint:", fault)
    print(f"comment-lint: {len(faults)} fault(s); +{comments} comment "
          f"/ +{code} code lines")
    sys.exit(1 if faults else 0)

main()
