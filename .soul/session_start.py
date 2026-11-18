#!/usr/bin/env python3
"""SessionStart hook for a project: the brief of the open tasks in
okf/tasks.md and the last 12 lines of tmp/STATE.md. Two prints, no
logic, under 5 KB; the harness moves a larger print to a file. The root
is CLAUDE_PROJECT_DIR, else the cwd.
"""

from __future__ import annotations

import os
import pathlib
import sys

BRIEF = ("### #", "Status:", "Waits on:", "Next step:")
TAIL = 12


def brief(tasks):
    """The lines of every open task that say what it is and waits on."""
    out = []
    inside = False
    for line in tasks.read_text().splitlines():
        if line.startswith("## Open"):
            inside = True
        elif line.startswith("## Closed"):
            inside = False
        elif inside and line.startswith(BRIEF):
            out.append(line)
    return out


def main():
    root = pathlib.Path(os.environ.get("CLAUDE_PROJECT_DIR") or ".")
    tasks = root / "okf" / "tasks.md"
    state = root / "tmp" / "STATE.md"
    lines = []
    if tasks.exists():
        lines.append("== okf/tasks.md, the open tasks in brief; "
                     "read the file whole ==")
        lines += brief(tasks)
    if state.exists():
        lines.append("== tmp/STATE.md, the last 12 lines; "
                     "the resume thread ==")
        lines += state.read_text().splitlines()[-TAIL:]
    else:
        lines.append("== tmp/STATE.md is absent on this host ==")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
