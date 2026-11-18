"""The one reader of okf.conf, shared by every script beside it."""

from __future__ import annotations

import pathlib


def root(argv):
    """The project root: `--root <path>` in argv, else the cwd. Scripts
    run from the agentic.devs checkout against any project."""
    out = pathlib.Path.cwd()
    if "--root" in argv:
        out = pathlib.Path(argv[argv.index("--root") + 1])
    return out.resolve()


def read(root):
    """{key: [values]} from <root>/okf.conf; a missing file is empty.
    A comment is a whole line, so a value may contain `#`."""
    out = {}
    path = pathlib.Path(root) / "okf.conf"
    lines = path.read_text().splitlines() if path.exists() else []
    for line in lines:
        text = line.strip()
        if text and not text.startswith("#"):
            key, _, value = text.partition(" ")
            out[key.strip()] = value.split()
    return out


def one(conf, key, default=""):
    values = conf.get(key) or []
    return values[0] if values else default


def many(conf, key, default=()):
    return list(conf.get(key) or default)
