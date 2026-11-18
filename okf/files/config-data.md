---
type: File
title: ConfigData.swift is the persisted settings record and its JSON shape
sources:
  - resource: https://github.com/leok7v/Caffeinate/blob/main/Caffeinate/Settings/ConfigData.swift
generated: { by: claude/opus, at: 2026-11-18T08:30:00Z }
---

`ConfigData` holds the flags, the lid option, the login item state and the
auto-off timer. `decodeIfPresent` with a default keeps an older JSON file
readable when a key is added. Add a new field to `==`, `CodingKeys`, both
initializers and `init(copy:)`. A field missing from one of them never reaches
the file.
