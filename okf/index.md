---
okf_version: "0.2"
---

# Caffeinate knowledge bundle

Everything about this code that the source cannot tell you.
Measurements with their conditions, dead ends with their reasons,
invariants no gate checks. Also how to work with Human in this repo.

The bundle is committed with the code, in the same commit as the code
it describes. That commit rule is the staleness mechanism. A concept
binds to a file through `sources:` URLs into this repo, so
`grep -rl <basename> okf/` answers "what do we know about this file".
`python3 .soul/okf_lint.py --root .` says whether the bundle is well
formed. The pre-commit hook runs it.

The discipline itself is `SOUL.md` at the repo root, from the origin,
`github.com/leok7v/agentic.devs`, through `SOUL-INSTALL.md`. Edit it
there first, then refresh here. The areas below hold what is true of
this repo only.

# Areas

* [constraints](constraints/) - invariants and platform behaviour no gate checks
* [decisions](decisions/) - why a path was taken, and what it cost
* [feedback](feedback/) - how to work with Human, in this repo
* [files](files/) - what each source file is for, one paragraph each
* [findings](findings/) - measurements and dead ends
* [procedures](procedures/) - how to run something whose steps are not derivable
* [references](references/) - pointers outside this repo
* [rules](rules/) - the project lexicon and the rules of this repo only
