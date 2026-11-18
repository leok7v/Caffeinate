---
type: File
title: CaffeinateApp.swift is the SwiftUI entry point and opens no window
sources:
  - resource: https://github.com/leok7v/Caffeinate/blob/main/Caffeinate/CaffeinateApp.swift
generated: { by: claude/opus, at: 2026-11-18T08:30:00Z }
---

The `@main` `App` hands the work to `AppDelegate` through
`NSApplicationDelegateAdaptor`. Its only scene is an empty `Settings` scene, so
launch opens no window. The app is `LSUIElement` and has no Dock icon.
