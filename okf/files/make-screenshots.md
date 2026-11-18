---
type: File
title: make-screenshots.swift draws the README cup and menu images
sources:
  - resource: https://github.com/leok7v/Caffeinate/blob/main/scripts/make-screenshots.swift
generated: { by: claude/opus, at: 2026-11-18T08:30:00Z }
---

The script draws the four cup images and `menu.png` into the directory in its
first argument. The menu rows are a literal list, so a new menu item in
`Appdelegate.swift` needs a row here too. The output is deterministic: a run
over an unchanged script gives the committed PNGs byte for byte.
