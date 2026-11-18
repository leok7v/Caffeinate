---
type: File
title: make-app.sh builds an ad-hoc signed universal app with swiftc only
sources:
  - resource: https://github.com/leok7v/Caffeinate/blob/main/scripts/make-app.sh
generated: { by: claude/opus, at: 2026-11-18T08:30:00Z }
---

The script compiles the sources for arm64 and x86_64, joins them with `lipo`,
makes `AppIcon.icns` with `iconutil` and writes `Info.plist` by hand. The
result has no entitlements, so it is not sandboxed. The version is the
UTC time of the build, YY.MM.DD and YYMMDD.HHMM, the stamp of
`.github/workflows/dmg.yml`. The release DMG does not use this script.
