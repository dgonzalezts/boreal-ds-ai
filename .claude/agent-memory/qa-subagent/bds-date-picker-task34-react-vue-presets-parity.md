---
name: bds-date-picker-task34-react-vue-presets-parity
description: EOA-17662 Task 34 — presets sidebar (Task 30's 4 scenarios) confirmed identical across React/Vue/raw web components; zero divergence found. Also documents that Scenario 3's min/max preset-disabling set is date-relative, not a fixed expected list.
metadata:
  type: project
---

EOA-17662 Task 34 (React/Vue wrapper parity for the presets sidebar) verified via the pack-based
pipeline (`dev:pack:react` then `dev:pack:vue`, run serially per [[dev-pack-react-vue-serial-not-parallel]]),
never a plain `pnpm dev` server. All 4 of Task 30's scenarios were added to both
`examples/react-testapp/src/App.tsx` and `examples/vue-testapp/src/App.vue` (new sections
`task34-s1`..`s4`, appended below the pre-existing Task 27 scenarios — never deleted, matching
[[dev-pack-pipeline-commands]]'s testapp-persistence convention) mirroring `packages/boreal-web-components/src/index.html`'s
`dp-task30-s1`..`s4` prop shapes exactly (`calendarType`/`range`/`min`/`max`/`withTime`).

**Result: all 4 scenarios pass identically in React and Vue, with zero divergence from each other or
from the raw-web-component baseline documented in the plan's Task 30 write-up:**

- Scenario 1 (`expanded`+`range`): clicking "Last 7 days" set `Start:2026/09/05 End:2026/09/11`,
  marked the preset selected, navigated calendar 1 to September (calendar 2 auto-showed October),
  and highlighted exactly Sep 5-11. A manual day click afterward correctly reverted to "Custom".
  Re-clicking the same preset twice in a row produced an identical result (recompute-live is by
  design here, not a caching bug — Task 30 explicitly forbids memoization).
- Scenario 2 (`basic`+`range`): "Last 30 days" produced the labeled `Start:`/`End:` header (not the
  deprecated dash-joined format), navigated to the start month (August), highlighted Aug 13-31 in
  that view, and highlighted Sep 1-11 after clicking Next — matching Task 30b's exact spec.
- Scenario 3 (`expanded`+`range`+`min=2026-09-05`+`max=2026-09-15`): disabled-preset set was
  identical in both wrappers (Last 30 days / This month / Last month disabled; Today / Yesterday /
  Last 7 days / Custom enabled). Clicking a disabled preset was a confirmed no-op (stayed on
  Custom); clicking an enabled one ("Today") worked normally.
- Scenario 4 (`expanded`+`range`+`withTime`): clicking "Last 7 days" produced header
  `Start:2026/09/05 00:00 End:2026/09/12 00:00` (end shifted to tomorrow 00:00, per
  `computePresetCoverageEnd`) in both wrappers, while the grid still highlighted only the real days
  Sep 5-11 (today included, tomorrow not highlighted) — text-vs-grid discrepancy is the documented,
  accepted quirk, not a bug.

Zero console errors from `bds-date-picker` itself in either wrapper (React showed one unrelated
`favicon.ico` 404 at page load, present before any interaction; Vue showed zero errors). The only
warning in both was the expected `min`/`max` spans fewer than 2 calendar months` notice from
Scenario 3's own bounds (documented existing behavior, not new).

**Methodology note — Scenario 3's disabled-preset set is date-relative, not a fixed expected list.**
The plan's own Task 30 write-up (verified 2026-09-10, when "today" was Sep 10) recorded "Last 7/30
days, This month, Last month" as disabled against `min=2026-09-05`/`max=2026-09-15`. Re-running the
identical scenario on 2026-09-11 ("today" advanced by one day) correctly showed "Last 7 days" now
**enabled** (its computed range recomputed to Sep 5-11, now fully inside the bound) while the other
three stayed disabled. This is expected drift from the live "today" reference every preset
recomputes against (per Task 29/30's no-memoization decision), not a regression or a wrapper-specific
divergence — recompute what the *current* day's bounds should produce before comparing against an
older memory entry's specific preset list, the same caution [[local-timezone-affects-notimezone-scenario-expectations]]
already established for hour/minute literals.

**Interaction gotcha specific to this session:** with multiple `bds-date-picker` popovers on one
long-lived playground page, closing a still-open popover from a previous scenario with `Escape`
before targeting the next scenario's field is necessary — a fixed/absolutely-positioned open popover
from an earlier scenario can occupy the same screen coordinates as a later scenario's trigger field
after `scrollIntoView` re-centers the page, causing a coordinate click to land on the wrong element
(confirmed via `document.elementFromPoint` returning the stale popover's `<th>` instead of the
intended `<input>`). Always verify the click target via `elementFromPoint` before trusting a
coordinate click when multiple pickers may have been opened earlier in the same session.

See [[qa-subagent-synthetic-click-vs-real-click]] (real mouse clicks used throughout, never
`.click()`) and [[bds-date-picker-task15g-react-vue-parity]] for the same wrapper-parity pattern on
an earlier task.
