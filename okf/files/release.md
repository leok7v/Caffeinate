---
type: File
title: release.sh zips the make-app.sh build as the upstream release asset
sources:
  - resource: https://github.com/leok7v/Caffeinate/blob/main/scripts/release.sh
generated: { by: claude/opus, at: 2026-11-18T08:30:00Z }
---

The script runs `make-app.sh` and writes `Caffeinate.app.zip` with `zip -X -y`,
the asset name upstream releases carry. The fork releases the DMG from
`.github/workflows/dmg.yml` instead.
