---
type: File
title: Appdelegate.swift owns the menu, the timer and the assertions
sources:
  - resource: https://github.com/leok7v/Caffeinate/blob/main/Caffeinate/Appdelegate.swift
generated: { by: claude/opus, at: 2026-11-18T08:30:00Z }
---

`AppDelegate` makes the status item and its menu. A left click toggles
`hasCoffee`, and a right click or a Control click opens the menu.
`createAssertions` holds one `IOPMAssertionID` per flag in `activeAssertions`.
`setLidSleepDisabled` sets the clamshell sleep state of `IOPMrootDomain`, and
`syncLidSleep` keeps it equal to `hasCoffee && preventLidSleep`. The auto-off
timer is `expiryDate` and `tickTimer`. The file stops at persistence, which is
`ConfigHandler`.
