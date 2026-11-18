---
type: File
title: ConfigHandler.swift persists the settings and the login item
sources:
  - resource: https://github.com/leok7v/Caffeinate/blob/main/Caffeinate/Settings/ConfigHandler.swift
generated: { by: claude/opus, at: 2026-11-18T08:30:00Z }
---

`ConfigHandler` loads `CONF_FILE` from Application Support inside the sandbox
container and writes it from a Combine sink on `conf`. `ConfigData` is a class,
so a change goes through `mutateConfig`, which assigns a copy and so calls the
sink. `setAtLogin` registers `SMAppService.mainApp` and stores what the system
reports.
