---
type: Rule
title: The project lexicon, one term with one meaning, for this repo only
description: Every term this repo uses with a special meaning, the phrases
  it rejects for that meaning, and the identifier or file that implements
  it. term_lint.py reads this table with the one in SOUL.md section 0.
generated: { by: claude/opus, at: 2026-11-18T08:30:00Z }
---

Use the word in the `term` column. Do not use a phrase from the `not`
column for that meaning. A row lands in the same commit as the code
that gives an idea a name, and when Human corrects a word. The `code`
column names the identifier or file that implements the term, or says
"no code yet". `python3 .soul/term_lint.py --root . seed` ranks the
identifier words of the covered sources that no row names.

| term | meaning | not | code |
|---|---|---|---|
| release DMG | the signed, notarized and stapled disk image a `v*` tag publishes | none | `Caffeinate.dmg` in `.github/workflows/dmg.yml` |
| digest | the SHA-256 of the release DMG, published beside it; the tap reads it into the cask | checksum | `Caffeinate.dmg.sha256` |
| lid option | the menu item that disables clamshell sleep while Caffeinate is active | closed-display mode | `preventLidSleep`, `setLidSleepDisabled` |
| tap | `leok7v/homebrew-tap`, the Homebrew repo that holds the cask | none | `Casks/caffeinate.rb` in the tap |
| `MARKETING_VERSION`, `CURRENT_PROJECT_VERSION` | the Xcode build settings for `CFBundleShortVersionString` and `CFBundleVersion` | none | `project.yml` |
| `AppleClamshellCausesSleep` | the `IOPMrootDomain` registry property that says if a lid close sleeps the Mac | none | `ioreg -r -k AppleClamshellState` |
| `IOPMLibDefs.h`, `kPMSetClamshellSleepState` | the public SDK header of the `IOPMrootDomain` user client selectors, and selector 12 in it, the lid option | none | `setLidSleepDisabled` |
