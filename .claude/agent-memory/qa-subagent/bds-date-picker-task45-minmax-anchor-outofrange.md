---
name: bds-date-picker-task45-minmax-anchor-outofrange
description: EOA-17662 Task 45 — bds-date-picker with min/max anchors its roving cell on today even when today is outside the range, so keyboard focus lands on a disabled cell and arrows no-op; identical on raw/React/Vue/WebKit (pre-existing, not a wrapper bug)
metadata:
  type: project
---

# Task 45 (React/Vue wrapper parity) — S3 min/max finding

Five Task 45 scenarios (`task45-s1..s5` in `examples/{react,vue}-testapp`) were replayed through
the pack pipeline. React vs Vue vs the raw `src/index.html` `dp-keyboard-s1/s2/s3` baseline were
**byte-identical for all five scenarios**, zero console errors. WebKit replaying the same script
against raw was also byte-identical.

## The one real (pre-existing) defect found — Task 40 Scenario 3, min/max narrowing

`calendar-type="default" min="2026-09-10" max="2026-09-20"`, evaluated while today was
`2026-09-24` (outside the range):

- **Closed** popover: the roving `td[tabindex="0"]` is correctly clamped to a valid cell
  (`Thursday, September 10th, 2026`, the min).
- **On open**: the roving cell is re-anchored to *today* → `Thursday, September 24th, 2026`,
  which carries `aria-disabled="true"` and `--today --disabled`.
- Tabbing into the grid (natural keyboard entry, from the trigger input) lands focus directly on
  that **disabled** cell. Arrow keys from there are a **complete no-op** — focus is stuck
  (`ArrowRight/Left/Up/Down` all leave `document.activeElement` on `Sep 24`, repeatedly verified).
  Tabbing again leaves the grid entirely (`BODY` → trigger `INPUT`).

This directly contradicts Task 40 S3's stated pass criterion ("disabled and adjacent-month cells
are never a keyboard focus stop — traversal skips over them entirely"). It reproduces **identically
on the raw web component**, so it is **not** a Task 45 wrapper divergence — it is a pre-existing
`bds-date-picker`/`bds-calendar-grid` behavior defect worth its own fix task.

**Date-relative trap:** this only shows because today (Sep 24) is *after* `max` (Sep 20). A future
QA run on a different day may not reproduce it; pin/aware the evaluation date when re-checking.
The scenario also uses `timezone="UTC"` in the wrappers but no `timezone` in raw — both still showed
September 2026, so it did not affect this run.

## Environment gotchas hit this run

- A **pre-existing** `pnpm dev:components` stencil server (another session, PID tree under
  `multishell 89627`) was already holding **3333**. Do not kill it — my fresh
  `stencil ... --serve --port 3333` simply fell back to **3334** automatically. Verified both served
  current `index.html`.
- **`grep -c` on the served playground HTML is a false staleness signal**: the dev server minifies
  the whole page onto one line, so `grep -c "dp-keyboard"` returns `1` regardless of how many
  scenarios exist. Use `grep -o ... | sort | uniq -c` (occurrences, not lines) when checking whether
  a served copy is stale.
- `playwright-cli run-code` scripts run **without Node timers** — `setTimeout` is not defined. Use
  `page.waitForTimeout(ms)` instead of a `new Promise(setTimeout)` sleep helper.
- React and Vue packs both bind 5173 (sequential): SIGTERM to `publish.js <framework>` cleanly takes
  down its vite child and frees the port.
