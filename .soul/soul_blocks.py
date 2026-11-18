#!/usr/bin/env python3
"""Write every file block of SOUL-INSTALL.md into a repo, byte for byte.

    soul_blocks.py <SOUL-INSTALL.md> <repo root> [--skip <path> ...]

This file is the first block of the installer. The agent writes it by
hand, checks its line count and SHA-256, then runs it for the rest. A
verbatim block is written and checked against its marker. A seed-once
block is written only when its path is absent, with `<project>`
replaced by the name of the root. A file under `.githooks/` is made
executable. One line per block: written, kept, seeded, skipped, or
HASH MISS. Exit 1 on any miss.
"""

import hashlib
import pathlib
import re
import stat
import sys

HEAD = re.compile(r"^<!-- file: (\S+) \| (verbatim|seed-once)"
                  r"(?: \| (\d+) lines \| sha256 ([0-9a-f]{64}))? -->$")
FENCE = "````"


def blocks(text):
    """(path, kind, count, sha, body) per block, in file order."""
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        head = HEAD.match(lines[i])
        if head and i + 1 < len(lines) and lines[i + 1] == FENCE:
            j = i + 2
            while lines[j] != FENCE:
                j += 1
            body = "\n".join(lines[i + 2:j]) + "\n" if j > i + 2 else ""
            yield head.group(1), head.group(2), head.group(3), \
                head.group(4), body
            i = j + 1
        else:
            i += 1


def write(target, body):
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(body.encode())
    if ".githooks" in target.parts:
        target.chmod(target.stat().st_mode | stat.S_IXUSR)


def verbatim(target, body, count, sha):
    """Write the file and tell whether it matches its marker."""
    write(target, body)
    got = target.read_bytes()
    return got.count(b"\n") == count \
        and hashlib.sha256(got).hexdigest() == sha


def main(argv):
    text = pathlib.Path(argv[1]).read_bytes().decode().replace("\r\n", "\n")
    root = pathlib.Path(argv[2]).resolve()
    skip = set(argv[argv.index("--skip") + 1:]) if "--skip" in argv \
        else set()
    bad = 0
    for path, kind, count, sha, body in blocks(text):
        target = root / path
        if path in skip:
            line = f"skipped    {path}"
        elif kind == "verbatim":
            ok = verbatim(target, body, int(count), sha)
            bad += 0 if ok else 1
            line = f"{'written' if ok else 'HASH MISS'}    {path}"
        elif target.exists():
            line = f"kept       {path}"
        else:
            write(target, body.replace("<project>", root.name))
            line = f"seeded     {path}"
        print(line)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
