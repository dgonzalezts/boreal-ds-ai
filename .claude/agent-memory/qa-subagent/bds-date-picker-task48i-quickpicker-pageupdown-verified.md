---
name: bds-date-picker-task48i-quickpicker-pageupdown-verified
description: EOA-17662 Task 48i — quick-picker PageUp/PageDown paging verified live (all 5 items PASS, Chromium + WebKit). Captures the stale-lazy-chunk misdiagnosis, the year-window focus-loss gotcha, and the year-picker header-button click technique.
metadata:
  type: project
---

Task 48i routes `handlePageUp`/`handlePageDown` per `view` in `bds-calendar-grid.tsx`:
`months` → prev/next **year** (`handlePickerPrevYear`/`handlePickerNextYear`),
`years` → prev/next **decade window** (±10, `handleYearWindowPrev`/`handleYearWindowNext`),
`days` → unchanged prev/next-month `bdsMonthNavigate`.

**Result (2026-09-24): all 5 checklist items PASS**, Chromium (3344) + WebKit spot-check.
- Month view (`#dp-quickpicker-s1`): PageDown 2026→2027; PageUp ×2 →2026→2025; real header-button clicks produced identical steps. Paging does **not** emit `bdsMonthNavigate` (correct — only day view does).
- Year view: window `2020 – 2031` → PageDown `2030 – 2041` (+10) → PageUp back; real mouse header clicks identical.
- Bounds (`#dp-quickpicker-s3`, `min=2026-06-01 max=2027-03-31`): PageUp at 2026 no-op (2025 fully out of range, `prevYearDisabled=true`); PageDown →2027 (partial, 3 months enabled); PageDown again at 2027 no-op (2028 out, `nextYearDisabled=true`); year window 2020–2031 both directions no-op (`prevYears/nextYearsDisabled=true`, only 2026/2027 enabled).
- Day view: PageDown Sept→Oct emits `{year:2026,month:9,direction:'next'}`; PageUp Oct→Sept emits `{2026,8,'prev'}`.
- `expanded` (`#dp-quickpicker-s2`): left months picker PageDown 2026→2027, right day grid unaffected (still its own month, no picker); right picker opened independently pages alone.

**Stale lazy chunk — this exact task's trap.** `:3333` (long-running watcher) served the friendly `bds-calendar-grid.entry.js` with the NEW routing, but the browser actually loaded `p-b8382c98.entry.js` (mtime 8 min older) still containing the OLD code `PageDown=()=>{"days"===this.view&&this.handleNextClick()}`. Symptom was identical to a real regression: PageDown/PageUp did nothing in month/year view while Arrow keys and day-view paging worked. **Tell:** `playwright-cli -s=<s> requests --static` shows the loaded `/build/p-<hash>.entry.js`, then `curl` it and grep the `PageDown=()=>{...}` body. **Resolution here:** starting a *new* server process on a fresh port (`stencil build --dev --watch --serve --port 3344`) fully regenerated `www/build` (old signature gone from every file) — no manual `rm -rf .stencil www` was needed in this instance. This is a slightly weaker failure mode than `.agents/memory/stencil-dev-server-stale-lazy-chunk.md` describes ("plain restart insufficient"); worth promoting as a nuance — always check the *actually-loaded* hashed chunk before concluding a picker/overlay routing change failed.

**Year-window paging loses focus (observation, not a Task 48i failure).** Year cells are keyed by `cell.year`, so a ±10 window shift unmounts the focused cell and focus falls to `document.body`; a second PageUp/PageDown then doesn't reach the grid. Month cells are keyed by month (0–11) and persist across year changes, so month-view paging *retains* focus. When QA-ing year-window paging, re-focus a year cell between presses. Not reported as a bug (checklist is routing-only), but a candidate a11y follow-up.

**Header-button click technique in the year picker.** A real `playwright-cli`/`locator.click()` on the year-picker "Next years" button failed `element is outside of the viewport` (and `force:true` too). `page.locator(...).boundingBox()` + `page.mouse.click(box.x+w/2, box.y+h/2)` worked. And as always, programmatic `el.click()` no-ops on any `bds-button` (`event.detail === 0` guard — see [[bds-button-programmatic-click-detail-zero-gotcha]]).
