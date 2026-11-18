#!/usr/bin/env python3
# Emit a line whenever this session's context crosses a 5-point band, so a
# long session learns of its own compaction instead of inferring it from a
# summary appearing. A band that DROPS is a compaction: re-read what the
# project's CLAUDE.md says to re-read.
#
#     ~/.claude/ctx-watch.py <transcript.jsonl|dir> [window] [unused] [seconds]
#
# The argument may be a transcript OR its directory. Either way the live
# transcript is re-resolved every poll as the newest .jsonl beside it,
# because a compaction can rotate the session to a new file -- and a watcher
# pinned to the old path reads its last pre-compaction value forever and
# never fires, which is the failure this exists to catch.
#
# A compaction is detected from its OWN marker, not from the token count. The
# count is written by an assistant turn, and a compaction writes none: until
# the compacted session speaks, the newest usage record is still the huge
# pre-compaction one. Watching the count alone can only fire AFTER the work
# it exists to interrupt has already started -- measured at 7.5 minutes late
# on 2026-08-31. `isCompactSummary` lands at compaction time instead.
#
# ONLY THE ACTIONABLE POINTS FIRE: 90%, 95%, 99%, and a compaction. Each mark
# announces once and re-arms after a compaction. A per-band ticker was the
# first version and it spent a whole session narrating moves nobody acts on,
# which is worse than silence: it trained the reader to skip the line that
# finally mattered.

import json
import os
import sys
import time

TAIL = 32 << 20


def newest(where):
    out = where
    d = where if os.path.isdir(where) else os.path.dirname(where)
    best = -1.0
    try:
        for name in os.listdir(d):
            if not name.endswith(".jsonl"):
                continue
            full = os.path.join(d, name)
            at = os.path.getmtime(full)
            if at > best:
                best = at
                out = full
    except Exception:
        pass
    return out


def compact_mark(path):
    out = None
    try:
        size = os.path.getsize(path)
        with open(path, "rb") as f:
            f.seek(max(0, size - TAIL))
            blob = f.read().decode("utf-8", "ignore")
        for line in blob.splitlines():
            if '"isCompactSummary":true' not in line:
                continue
            try:
                j = json.loads(line)
            except Exception:
                continue
            out = j.get("uuid") or j.get("timestamp") or out
    except Exception:
        pass
    return out


def used_tokens(path):
    out = None
    try:
        size = os.path.getsize(path)
        with open(path, "rb") as f:
            f.seek(max(0, size - TAIL))
            blob = f.read().decode("utf-8", "ignore")
        for line in blob.splitlines():
            if '"usage"' not in line:
                continue
            try:
                j = json.loads(line)
            except Exception:
                continue
            u = j.get("message", {}).get("usage")
            if u and "input_tokens" in u:
                out = (u.get("input_tokens", 0)
                       + u.get("cache_read_input_tokens", 0)
                       + u.get("cache_creation_input_tokens", 0))
    except Exception:
        pass
    return out


def main():
    where = sys.argv[1]
    window = int(sys.argv[2]) if len(sys.argv) > 2 else 1_000_000
    every = int(sys.argv[4]) if len(sys.argv) > 4 else 30
    marks = (90, 95, 99)
    said = set()
    blind = 0
    live = None
    mark = None
    seen = False
    tail = "COMPACTED -- re-read per CLAUDE.md before further work"
    while True:
        path = newest(where)
        live = path
        now_mark = compact_mark(path)
        if seen and now_mark is not None and now_mark != mark:
            print(f"ctx compact summary written: {tail}", flush=True)
            said = {0}
        mark = now_mark
        seen = True
        used = used_tokens(path)
        if used:
            blind = 0
            pct = used * 100 // max(window, 1)
            head = f"ctx {used // 1000}k {pct}%"
            if not said and pct < marks[0]:
                print(f"{head} (watching for {marks[0]}%)", flush=True)
                said.add(0)
            for level in marks:
                if pct >= level and level not in said:
                    said.add(level)
                    print(f"{head} -- past {level}%", flush=True)
            if pct < 10 and said - {0}:
                print(f"{head} {tail}", flush=True)
                said = {0}
        else:
            blind += 1
            if blind in (10, 60):
                print(f"ctx unreadable for {blind} polls: {path}", flush=True)
        time.sleep(every)


main()
