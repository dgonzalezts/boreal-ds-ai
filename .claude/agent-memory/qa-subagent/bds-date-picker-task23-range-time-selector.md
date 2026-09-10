---
name: bds-date-picker-task23-range-time-selector
description: EOA-17662 Task 23 range-mode time selector manual QA found two blocking bugs (mouse-click-closes-popover on time selects; range+withTime Apply commits nothing) and one confirmed pass (auto-format header).
metadata:
  type: project
---

EOA-17662 Task 23 (`bds-date-picker` range-mode time selector, single-shared under `basic` / dual under `expanded`) manual QA against the 4 playground scenarios in `packages/boreal-web-components/src/index.html` (`dp-task23-s1`..`s4b`) found two blocking bugs and one confirmed pass:

1. **Blocking — mouse click on any time-selector `bds-select` option closes the entire date-picker popover**, discarding the in-progress selection. Reproduced in both range mode (`expanded`+`range`+`withTime`) and single-date mode (`basic`+`withTime`, Scenario 3) — not range-specific. Keyboard interaction (click to open, ArrowDown to highlight, Enter to select) does **not** trigger this — the popover stays open and the value commits correctly. Strongly suggests an outside-click/blur handler on the popover doesn't recognize a mouse click landing inside the nested `bds-select` listbox (likely portaled outside the popover's DOM subtree) as "inside," but a keyboard-driven selection never fires that handler path. This blocks the primary (mouse) interaction path for every `withTime` scenario, not just Task 23's new range ones.

2. **Blocking — `range && withTime` Apply commits nothing.** After selecting valid start/end dates (with or without touching time, calendarType `expanded` or `basic`) and clicking Apply, the popover closes but `bds-date-picker.value` stays `""` and the field shows no text — no console error/exception. Reproduced identically for both `calendarType='expanded'` and `calendarType='basic'`. This matches exactly what the plan's own grounding-check note flagged as unfinished: `bds-date-picker.tsx:402-405`'s Apply-commit path needs to call `combineDateTimeToUTC` per bound for range+time but apparently doesn't do so correctly (or bails silently). Single-date `withTime` (Scenario 3, non-range) commits correctly (`"2026-09-09T00:00:00.000-05:00"`), confirming the bug is specific to the range value-contract path Task 23 was supposed to implement.

3. **Confirmed pass**: the `expanded` labeled `Start:`/`End:` popover header live-updates to include `HH:mm` with no explicit `format` prop set (e.g. `2026/09/03 07:00`), satisfying Scenario 4a's acceptance criterion — verified independent of the Apply-commit bug above, since the header renders live during selection before Apply is clicked.

Both blocking bugs need to go back to @frontend-subagent before Task 23 can be marked done — this is not a QA-environment artifact, reproduced cleanly with fresh refs/screenshots each time. See [[qa-subagent-synthetic-click-vs-real-click]] — this is a different failure mode (a *real* Playwright click, not a synthetic one, still closes the popover), so that existing memory's guidance doesn't apply here as a workaround.
