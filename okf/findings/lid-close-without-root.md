---
type: Finding
title: The clamshell sleep call keeps a closed Mac awake, no root, sandboxed
description: kPMSetClamshellSleepState (selector 12) on the
  RootDomainUserClient returns KERN_SUCCESS for a user process and for a
  sandboxed app, and a closed lid on battery then does not sleep.
sources:
  - resource: https://github.com/leok7v/Caffeinate/blob/main/Caffeinate/Appdelegate.swift
generated: { by: claude/opus, at: 2026-11-18T08:30:00Z }
---

`IOServiceOpen` on `IOPMrootDomain`, then
`IOConnectCallScalarMethod` with selector 12 and input 1 or 0.
`pmset disablesleep` needs root, and this call does not. The functions
are public IOKit, and the SDK header `IOPMLibDefs.h` defines selector
12 as `kPMSetClamshellSleepState`. No document describes the selector.

- As a user process, not root: open 0x0, call 0x0.
- As an app bundle with `Caffeinate.entitlements`, signed with an
  Apple Development identity, its container created: open 0x0, call
  0x0.
- The `AppleClamshellCausesSleep` property did not change after the
  call. The property updates on a lid event only, so it proves nothing
  either way.

Conditions: 2026-11-18, macOS 26.7.1, Mac15,13 (Apple Silicon
MacBook Air) on AC. A sandboxed bare executable with no bundle stops with
exit 133 before main, so the sandbox test needs a `.app`.

The state lives in the kernel, not in the client. A crash leaves the
lid sleep disabled, so `applicationDidFinishLaunching` clears it.

Lid test, 2026-11-18, same Mac, battery at 100 percent, no external
display, the Developer ID build of 72dd7f1, the lid option on. The lid
closed at about 08:15:20 PST, and powerd wrote `lidopen` at 08:17:59.
`pmset -g log` has no Sleep line and no Wake line in that window, and
other assertion events went on at 08:16:53, 08:17:12 and 08:17:21.
The test is one run with no control arm.

Lid test of the AC-only option, 2026-11-23, same Mac, macOS 26.7.1,
battery at 100 percent, no external display. The build is `main` with
the AC-only change. Caffeinate held `-i` and `-m` in each arm, and the
lid option added `-s`. Evidence is `pmset -g log` and a clock line
every 5 s.

- A, AC, option off: `Clamshell Sleep` at 00:58:59, about 10 s after
  the lid closed. This arm is the control.
- B, AC, option on: lid closed 01:02:26 to 01:04:22, no gap in the
  clock, no sleep entry.
- C, battery, option on, the app launched on battery: `Clamshell
  Sleep` at 01:08:08, about 5 s after the lid closed.
- D, option on: plugged in, lid closed at 01:10:08, awake on AC.
  Unplugged at 01:10:43 with the lid closed, `Clamshell Sleep` in the
  same second. The power source notification works in the sandbox in
  both directions.

`AppleClamshellCausesSleep` is not a proof of the override state. On
battery it read `0` after the selector set 0, then 1, then 0, each
call `KERN_SUCCESS`. Use a lid close and `pmset -g log` instead.

A MacBookAir5,2 on macOS 15.8.3 through OpenCore is no test machine.
With Caffeinate quit, it did not sleep with the lid closed. The
internal keyboard and trackpad sent a user activity event within 1 s of each
display off, every 22 s. The cause is not known.
