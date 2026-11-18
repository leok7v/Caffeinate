---
type: Decision
title: Why the knowledge lives in an OKF bundle, what belongs in it, and
  the fixed vocabulary of types
description: Rationale, measurements and dead ends are knowledge, not
  source. They live here in a typed bundle bound to the code by URL, and
  the eight types are fixed so one lint reads them from this one table.
generated: { by: claude/fable, at: 2026-10-22T22:00:00Z }
---

## Why this bundle exists

Knowledge about this code used to live in agent memories that travelled
with no repo. OKF is an open format: markdown with YAML frontmatter, no
SDK, readable without tools. So the bundle travels with the code under
`okf/`, and every agent and human reads the same files.

The second reason is the source itself. Rationale, measurements, what
was tried and rejected are KNOWLEDGE, not source. `SOUL.md` section 6
sends them here, so that a professional who reads a file gets code
rather than the story of how it got there. A reader who wants the story
can still find it.

## What belongs here

Only what the source cannot tell you. If the code could regenerate a
concept, the concept does not belong. Per-FUNCTION description is out of
scope: the compiler enforces the signature and a prose copy of it rots.
Per-FILE description is IN scope, one paragraph.

## Type vocabulary

Fixed, because an unpinned vocabulary becomes Perf, Performance and
Measurement after three writing sessions. `okf_lint.py` reads this
table rather than a copy of its own.

| type | what qualifies |
|---|---|
| `Finding` | a measurement, or a dead end, with the conditions that produced it |
| `Decision` | a path taken, what was rejected, what it costs |
| `Constraint` | an invariant or platform behaviour no gate can check |
| `Procedure` | how to run something whose steps are not derivable |
| `Rule` | discipline every agent applies when writing code |
| `Feedback` | how to work with Human |
| `Reference` | a pointer to something outside the repo |
| `File` | what one source file is for, and where it stops |

The discipline itself, the rules, the working-method feedback and the
general procedures, is `SOUL.md` at the repo root, from the origin,
`github.com/leok7v/agentic.devs`, through `SOUL-INSTALL.md`. Edit it
there first, then refresh here. The gates in `.soul/` come the same
way, byte for byte, and read this repo's `okf.conf`. They too are
edited only at the origin.

## How concepts bind and link

A concept names the code it describes in `sources:`, as OKF v0.2
specifies: each entry is `- resource: <URL>` into this repo. So
`grep -rl <basename>` over this bundle answers "what do we know about
this file", and the lint can check that the file exists. A source file
carries no pointer back into the bundle.

Concepts link to each other with markdown links whose target is a
bundle-absolute path such as `/decisions/why-this-bundle-exists.md`.
A concept nothing
links to is not a defect. Concepts are found by search and by their
`sources:` binding. A link is only a reading order.

## What does not go anywhere else

`log.md` is written by the pre-commit hook and read by nobody in git.
No `inbox/`: a file without frontmatter fails the bundle's own lint.
