---
name: bds-date-picker-task52-quickpicker-wrapper-parity
description: EOA-17662 Task 52 — Phase 9 quick-picker parity across React/Vue wrappers verified. Records the one testapp-handler divergence (Clear), plus reusable playwright-cli selector/click gotchas found driving the date-picker popover.
metadata:
  type: project
---

# Task 52 (React/Vue quick-picker wrapper parity) — verified 2026-09-25

React vs Vue deep-equality on the Phase 9 month/year quick-picker, via the pack
pipeline (react first, teardown, then vue). All 7 checklist areas matched across
both wrappers except for one **testapp-handler** divergence (see below). Zero new
runtime console errors in either wrapper.

## The one divergence: Clear's empty-string payload vs the Vue testapp guard

- `bds-date-picker` Clear emits `bdsChange` **and** `valueChange` with
  `detail === ""` (empty string, `typeof === 'string'`) — even for a **range**
  picker. Identical payload through both wrappers.
- `examples/vue-testapp/src/App.vue`'s `onTask52S2Change` guards
  `if (typeof e.detail !== 'string') task52S2Value.value = e.detail`, so it
  **silently ignores** Clear's `""` and the displayed `s2` value stays stale.
- `examples/react-testapp/src/App.tsx`'s `onBdsChange` sets unconditionally, so
  React's `s2` output becomes `""`.
- Net: the *component event is identical*; the *recorded value differs* purely
  because of the Vue testapp's mode-detection guard. Not a wrapper/component
  divergence — flagged to the orchestrator as a testapp (and arguably
  "Clear emits a string not null in range mode") follow-up.

## playwright-cli / popover-harness gotchas (reusable)

- **`click "A >> nth=0 >> B"` silently matches nothing.** The `>> nth=0` chained
  selector form is unreliable here; the click no-ops with no visible error when
  stdout is redirected. Use real CSS `:nth-of-type(n)` scoping instead
  (`bds-date-picker[...] bds-calendar-grid:nth-of-type(2) ...`).
- **`:text-is("Apply")` does NOT match a `bds-button`'s inner native `<button>`** —
  `:text-is` reports "does not match any elements". Use positional
  `... .bds-date-picker__footer-buttons bds-button:nth-of-type(3) button`
  (Clear=1, Cancel=2, Apply=3).
- **The popover footer buttons can sit below the viewport** (Vite page is long).
  `locator.click()` retries and finally errors `element is outside of the
  viewport`; JS `.click()` no-ops on `bds-button` (`detail===0` guard). Fix:
  `playwright-cli resize 1280 1600` (do this at session open) and/or
  `locator.scrollIntoViewIfNeeded()` + `boundingBox()` + `page.mouse.click(cx,cy)`
  via `run-code`.
- **`bds-date-picker` popover/calendar is light DOM** but `el.children`/`childNodes`
  read as length 1 while `querySelector(':scope > bds-popover')` finds it — do not
  trust `children` for traversal; use `querySelector(All)` + ancestor-depth.
- `mouse move X Y` is wrong — the command is `mousemove X Y`.
- In `run-code` scripts, `process` is not defined (can't pass selectors via env) —
  write the selector into the script file.

## WebKit spot-check note

Tab traversal in Playwright-WebKit only reached the text input and the roving day
cell — **buttons (Close/prev/label) were never in the Tab order**, unlike
Chromium. Programmatic `.focus()` on the label + `Enter` still opens the picker,
and Escape/overlay geometry/paging all matched. This is the macOS WebKit
"keyboard access to buttons" platform behavior, not a component/wrapper defect —
but it means "Tab to the label" cannot be verified in Playwright-WebKit as driven.
