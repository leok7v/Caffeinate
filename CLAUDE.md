# Caffeinate

A macOS menu bar app that holds IOKit power assertions, the flags of
`caffeinate(8)`, while its cup is full. The repo is the fork
`leok7v/Caffeinate` of the upstream repo, LennardKittner/Caffeinate.
The fork adds a Developer ID release DMG, the cask in the tap, and the
lid option. The open work is in `okf/tasks.md`.

<!-- soul -->
## Session start, and after any compaction or clear (HARD)

The trigger is a fresh session, a compaction, a `/clear`, a summary
above, or Human says "compacted". On the trigger, first start the
context watcher if it does not run:

    Monitor(command: "python3 .soul/ctx-watch.py <transcript.jsonl> 1000000 5 30",
            description: "context usage band changes and compaction",
            persistent: true)

Then read `SOUL.md` whole, one Read call, before any task work. That
file is the whole discipline: code, comments, the bundle, how to work
with Human, long runs, gates, writing. Then the rest of tier 1, whole,
one file per Read call: `okf/index.md` and the seam files
`okf/procedures/read-by-tier.md` lists. Then every concept that
`grep -rl <basename> okf/` returns for the files the task names.

The cost is PLANNED. Do not trim it or delegate it. Tier 2 and tier 3
are in `read-by-tier.md`.

Then read `okf/tasks.md`, and `tmp/STATE.md` when it exists, and
re-create the open tasks in the harness task list, the number first in
the subject. Then `python3 .soul/ctx_cost.py --root . update
<transcript.jsonl>` refreshes the token table from what the reads
cost.

## The bundle is in okf/

Everything this repo knows that its source cannot tell you is in
`okf/`, an Open Knowledge Format v0.2 bundle kept with the code.
Start at `okf/index.md`. A concept binds to a file through `sources:`
URLs into this repo. `grep -rl <basename> okf/` answers "what do we know
about this file".

Rationale, measurements and dead ends go in the bundle, NOT in a
comment. A concept changes in the same COMMIT as the code it describes.
That rule is the whole staleness mechanism.

`SOUL.md` and the gates in `.soul/` come from the origin,
`github.com/leok7v/agentic.devs`, through `SOUL-INSTALL.md`. Edit them
there, then refresh here. The pre-commit hook in `.githooks/` runs
`okf_lint.py`, the staged `comment_lint.py`, `ste_lint.py` and
`term_lint.py`. Write every concept and reply per `SOUL.md` section 10,
with the words of its section 0 and of `okf/rules/lexicon.md`.

## Hard rules

READ EVERY FILE YOU EDIT, IN FULL, BEFORE YOU EDIT IT. No exception for
"I grepped it a moment ago", none for a file the context summary
describes, none for a one-line change. `grep` and `sed` LOCATE a symbol.
They never justify an edit. `SOUL.md` section 4.

Show a fix Human can SEE on screen before you commit it: build it, say
what changed, stop. Commit after Human looks, or when Human asks.
NEVER publish (push to a public remote, sync a public mirror) unless
Human asks in that session. `SOUL.md` section 7.

## Comments (HARD, checked)

Before you declare ANY source edit done, run
`python3 .soul/comment_lint.py --root .` and get exit 0. The gate fails
on any added comment line, a comment block over 4 lines, a
comment-to-code ratio over 25 percent, or a narration marker.
A fault is NEVER a reason to stop and ask. `MAX_ADDED = 0` is absolute.

The prose goes to a concept in `okf/`. Then CONSULT what you wrote:
`grep -rl <basename> okf/` before you touch a file. `SOUL.md` section 6.

## Task tracking

`okf/tasks.md` is the task list, the record. The file holds the open
tasks with their state, what they wait on and their next step, and the
closed tasks one line each. The harness task list is a view of it, per
session and per host, and a `/clear` empties it. Load the Task tools
once per session with
`ToolSearch("select:TaskList,TaskGet,TaskUpdate,TaskCreate")`.
Then re-create the open tasks there, the number first in the subject. A
task that opens, moves or closes changes `okf/tasks.md` in the same
commit.

`tmp/STATE.md` is the resume thread: gitignored, host-local, the
in-flight detail (waiter ids, pids, markers, log paths). Keep it current
before every long wait. After a compaction, trust the file, not the
summary. The SessionStart hook in `.claude/settings.json` prints the
brief of the open tasks and the tail of `tmp/STATE.md`. The rule stands
when the hook does not run.
<!-- /soul -->

## Build

    xcodegen generate          # project.yml -> Caffeinate.xcodeproj
    xcodebuild -project Caffeinate.xcodeproj -scheme Caffeinate \
        -configuration Release -derivedDataPath tmp/dd build
    ./scripts/make-app.sh      # swiftc only, ad-hoc signed, repo root

A `v*` tag runs `.github/workflows/dmg.yml`: the release DMG and its
digest. `bin/secrets` sets the five Actions secrets it needs. There are
no tests.

## Layout

    Caffeinate/           the app sources, the asset catalog, the entitlements
    project.yml           the Xcode project source; the .xcodeproj is generated
    scripts/              make-app.sh, release.sh, icon and screenshot makers
    Images/               README images from make-screenshots.swift
    bin/secrets           sets the Actions secrets of dmg.yml
    .github/workflows/    dmg.yml

    SOUL.md        the discipline, from the origin; do not edit here
    .soul/         the gates, from the origin; do not edit here
    .githooks/     the pre-commit hook; git config core.hooksPath .githooks
    okf/tasks.md   the task list (the record)
    tmp/STATE.md   the resume thread (gitignored, host-local)

## Conventions

Swift 5, AppKit with a SwiftUI `App` shell, macOS 13 deployment
target, universal arm64 and x86_64. The app is sandboxed. The upstream
sources keep their own style and comments. New code follows `SOUL.md`
section 5 and adds no comment.
