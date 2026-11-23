---
type: Reference
title: The task list, the record of every task open and closed
description: Open tasks with their state, what they wait on and their next
  step; closed tasks one line each. The harness task list is a view of this
  file, and tmp/STATE.md is the resume thread.
generated: { by: claude/opus, at: 2026-11-18T08:30:00Z }
---

This file is the record. The harness task list (the Task tools, the
TUI) is a view of it, per session and per host, and a `/clear` empties
it. A session re-creates every open task there, the number first in the
subject. A task that opens, moves or closes changes this file in the
same commit. Numbering continues from the highest number in the file.

`tmp/STATE.md` is the resume thread: gitignored, host-local, the
in-flight detail (waiter ids, pids, markers, log paths). Read it on the
trigger when it exists. Keep it current before every long wait, so a
compaction loses nothing.

## Open

In the order to work them. Per task a `### #NN subject` heading, then
a `Status:` paragraph, a `Waits on:` line and a `Next step:` line.

### #3 Mac App Store submission

Status: app record 6836422884. Build 26.11.18 is uploaded. The store
text is in `appstore/en-US/`, the privacy page in `docs/`.

Waits on: Human says "submit". The release type MUST stay manual.

Next step: set free, Data Not Collected, the URLs and the text, attach
the build, then show the submission to Human.

### #4 Lid test of the AC-only lid option, then PR 7

Status: the lid option applies only on AC power and locks the `-s`
item on. The lid test passed on 2026-11-23, arms A to D, per
`okf/findings/lid-close-without-root.md`. The code is in `main`, not
committed, and in the PR branch in `tmp/pr7`, not pushed.

Waits on: Human says "push".

Next step: push the PR branch, update the description with the test,
and reply in the 2 open threads.

## Closed

| # | subject | closed |
|---|---|---|
| 1 | Prove the lid option on a closed lid | 2026-11-18 |
| 2 | First signed release, v261118.1618, in the tap | 2026-11-18 |
