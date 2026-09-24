---
name: bds-date-picker-task34a2-shift-hydration-fix-verified
description: Task 34a-2 correctHydratedRangeEnd fix confirmed live — no more double-shift/highlight/drift bug on range+with-time reopen, across expanded-preset, basic-manual, and expanded-manual scenarios.
metadata:
  type: project
---

EOA-17662 Task 34a-2 manual QA: all 5 checklist items pass. Verified `correctHydratedRangeEnd` (added in `bds-date-picker.tsx`, called from both `listenClickTrigger` and the `CANCEL` footer branch after `matchPreset` runs) via live DOM inspection, not just visual glance.

- `dp-presets-s4` (`expanded`+with-time), "Today" preset: after Apply, committed `{start: Sept21, end: Sept22}` (one shift, correct). Reopen: calendar highlights only Sept21 (`range-start`+`range-end` on the single cell), Sept22 has no highlight classes. Header `End: 2026/09/22 00:00` matches field text exactly (no double shift to Sept23). Re-Apply with no changes across 3 consecutive cycles: `bdsChange.end` stays `2026-09-22` every time — no snowball drift.
- `dp-presets-s2` (`basic`+with-time, added `with-time` attribute to this scenario in `index.html` per the plan's instruction — it was missing before this task): manual 5-day selection (Sept5-Sept10) commits `{start: Sept5, end: Sept11}` (unconditional basic shift). Reopen: day10 has `range-end` class, day11 has none. Header/field agree exactly. Reopen→Apply-again: value unchanged (`Sept11`), no drift.
- `dp-presets-s4` manual non-preset `expanded` selection (Sept9-Sept14, no shift since expanded-manual is never shifted at commit): reopen shows header/field/highlights all consistent with the committed value, unaffected by the fix (regression check) — `matchPreset` returns null so `correctHydratedRangeEnd` leaves draft untouched, exactly as designed.

Zero console errors across the whole session (57 pre-existing INFO-level icon-only-button warnings unrelated to this fix).

See [[bds-date-picker-presets-s1-reopen-custom-mismatch]] and [[bds-date-picker-task34a-preset-rematch-fix-verified]] for related earlier preset-reopen QA passes in this same area.
