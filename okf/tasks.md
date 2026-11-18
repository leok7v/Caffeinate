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

### #2 First signed release

Status: `.github/workflows/dmg.yml` is written. The Actions secrets
are set, 2026-11-18.

Waits on: nothing.

Next step: tag vYYMMDD.HHMM, then tag the tap caffeinate-vYYMMDD.HHMM.

## Closed

| # | subject | closed |
|---|---|---|
| 1 | Prove the lid option on a closed lid | 2026-11-18 |
