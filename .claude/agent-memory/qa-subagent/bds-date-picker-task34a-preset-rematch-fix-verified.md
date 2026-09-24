---
name: bds-date-picker-task34a-preset-rematch-fix-verified
description: EOA-17662 Task 34a manual QA — matchPreset reverse-lookup on popover reopen confirmed working for exact match, false-positive avoidance, and with-time coverage-shift.
metadata:
  type: project
---

Task 34a fixed a bug where reopening `bds-date-picker`'s popover after applying a built-in preset always reset the presets sidebar to "Custom" instead of re-deriving the matching preset. Verified live via `playwright-cli` (webkit not needed — this is app-state logic, not rendering) against the existing `dp-presets-s1`/`s2`/`s4` scenarios in `packages/boreal-web-components/src/index.html`, dev server on port 3333.

All three checklist items pass, confirmed via actual DOM `className` on the preset `<button>` (`bds-date-picker__preset--selected`), not just visual/ARIA `pressed` state:

- `dp-presets-s1` (expanded, range): apply "Today" → close → reopen → `Today` button carries `bds-date-picker__preset--selected`.
- `dp-presets-s2` (basic, range): manually select Sept 8-12, 2026 (no built-in preset matches) → apply → reopen → `Custom` carries `--selected`, no false-positive match on any built-in preset.
- `dp-presets-s4` (expanded, range, `with-time`): apply "Last 7 days" (committed Start 2026/09/15 00:00, End 2026/09/22 00:00 — the +1-day coverage shift) → reopen → `Last 7 days` still carries `--selected`, confirming `matchPreset` correctly unshifts the coverage-shifted end before comparing.

Zero console errors throughout. Build was minified (dev server serves a Vite-bundled/minified `bds-date-picker.entry.js` even in dev mode for this project, so `grep matchPreset` on the built file finds nothing under its minified name) — freshness was instead confirmed by comparing `.tsx` source mtime vs. built-file mtime, not by grepping symbol names in the bundle.

Related: [[bds-date-picker-presets-s1-reopen-custom-mismatch]] (the original bug report that led to this fix).
