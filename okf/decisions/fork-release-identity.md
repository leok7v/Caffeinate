---
type: Decision
title: "The fork release: its own bundle id, macOS 13, tag as version"
description: Why the bundle id is io.github.leok7v.Caffeinate, why the
  deployment target went from 11.0 to 13.0, and why dmg.yml takes the
  version from the tag.
sources:
  - resource: https://github.com/leok7v/Caffeinate/blob/main/project.yml
  - resource: https://github.com/leok7v/Caffeinate/blob/main/.github/workflows/dmg.yml
  - resource: https://github.com/leok7v/Caffeinate/blob/main/scripts/make-app.sh
generated: { by: claude/opus, at: 2026-11-18T08:30:00Z }
---

The bundle id is `io.github.leok7v.Caffeinate`, the scheme of the
other leok7v apps. A Developer ID build under the upstream id
com.Lennard.Caffeinate would claim a name the fork does not own.
The cost: a user of the upstream build starts with default settings,
because the sandbox container follows the bundle id.

The deployment target is 13.0. Xcode 27 refuses 11.0, and
`make-app.sh` already built for 13.0. The cost: macOS 11 and 12 lose
the app. The login item needed 13.0 anyway.

The tag is the UTC time, vYYMMDD.HHMM, as in kataphasis.
`.github/workflows/dmg.yml` derives `MARKETING_VERSION` YY.MM.DD and
`CURRENT_PROJECT_VERSION` YYMMDD.HHMM from the tag, the ChatOKF stamp.
A tag cannot carry a stale version, and the cask version grows with
time. The project keeps a version for local builds only. The upstream
1.2.0 scheme ends here.

`project.yml` is the project, and xcodegen makes `Caffeinate.xcodeproj`,
which git ignores. The other leok7v apps work the same way. The cost:
an upstream change to the upstream `.xcodeproj` needs a port by hand
into `project.yml`. Before the switch, a build of each project gave the
same bundle files. The `Info.plist` differed only by the app category
key, added on purpose.
