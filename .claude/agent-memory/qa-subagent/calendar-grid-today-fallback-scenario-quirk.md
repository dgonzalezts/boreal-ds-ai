---
name: calendar-grid-today-fallback-scenario-quirk
description: index.html's buildMonthGrid() helper (Task 9/10 bds-calendar-grid scenarios) falls back to comparing against the real system date for isToday when no override is given, so the real current day's cell also gets --today styling alongside any deliberately forced date
metadata:
  type: project
---

`buildMonthGrid()` in `packages/boreal-web-components/src/index.html` computes each cell's `isToday` as `override.isToday ?? date.toDateString() === now.toDateString()`. The Task 10 `#calendar-grid-states` scenario overrides only `2026-08-15` to force `isToday: true`, but every OTHER cell still falls back to a real `now` comparison — so on any day the real system date happens to be inside the displayed August 2026 grid (e.g. the real date was 2026-08-14 during this QA run), that cell ALSO renders with the `--today` dashed-ring styling, contradicting the scenario's own doc comment ("reproducible on any day this page is loaded"). Confirmed via `[...grid.querySelectorAll('td')].filter(td => td.className.includes('--today'))` returning both Aug 14 and Aug 15.

This is a test-fixture quirk, not a `bds-calendar-grid` component bug — the component correctly renders `--today` for whichever cells the `grid` prop marks `isToday: true`; the scenario script's fallback logic is what leaks the real date in. It also affects Task 9's `#calendar-grid-selected` scenario (Aug 14, "NOT today, selected") whenever real-today coincides with Aug 14 — that cell picks up an extra `--today` white dashed border on top of the selected-blue fill, which is harmless (SCSS already handles `--selected.--today` combination) but means "confirm plain solid-blue Selected" checks should tolerate an extra dashed border if run on 2026-08-14.

**How to apply:** When re-running these scenarios, always disambiguate target cells by `aria-label` (exact date text) rather than by `--today`/`--selected` class alone, since class-based `.find()` can silently grab the wrong cell if the real date coincides with an in-grid date. If this scenario script is ever touched for other reasons, consider flagging to remove the real-date fallback entirely (always `false` unless explicitly overridden) so the scenario is truly day-independent as documented.
