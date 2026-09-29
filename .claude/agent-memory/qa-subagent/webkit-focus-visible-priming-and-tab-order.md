---
name: webkit-focus-visible-priming-and-tab-order
description: In Playwright WebKit, Tab skips buttons (macOS Safari default full-keyboard-access off) and programmatic .focus() only yields :focus-visible after a non-modifier keypress; plus the 0.1s outline-width transition that makes an early ring read look like a false negative
metadata:
  type: project
---

Two WebKit-only gotchas hit while verifying `bds-calendar-grid` quick-picker focus rings (EOA-17662, 2026-09-28). Both produce **false negatives** if missed — a real, working focus ring reads as `outlineWidth: 0px`.

**1. `page.keyboard.press('Tab')` skips buttons in WebKit** (macOS Safari's default "Tab highlights each item" accessibility setting is off). From the calendar header's prev-month `<button>`, a `Tab` press does not move to the adjacent `.bds-calendar-grid__label-button` or the next-month button — it jumps to the first `[tabindex="0"]` element (a day cell) and then out to the text-field `<input>`s, eventually `BODY`. So the Chromium technique "programmatically focus the element before the target, then press Tab" does **not** reach a `<button>` target in WebKit.

**2. `:focus-visible` on a programmatically-focused element needs a non-modifier keypress to establish keyboard modality.** After a mouse click (pointer modality), `el.focus()` yields `focusVisible: false`. Pressing a **modifier-only** key (`Shift`, `Alt` alone) does **not** flip the modality. Pressing a non-modifier key (`ArrowDown`, `ArrowUp`, even `Alt` exercised via a prior non-modifier press) does — from then on, programmatically-focused controls match `:focus-visible`. Practical sequence that works on WebKit buttons/cells: focus the target, `keyboard.press('ArrowDown')` once (harmless when the target ignores it), then read. This is the WebKit analogue of the Chromium "press Tab first" trick already noted in [[bds-date-picker-task31-presets-focus-selected-specificity-bug]].

**3. The focus ring animates in over 100ms** — `bds-calendar-day-interaction-transition` includes `outline-width 0.1s` and `box-shadow 0.1s`. Reading `getComputedStyle` ~60ms after the focus change catches mid-transition values (`outlineWidth: 2px`, `boxShadow: rgba(255,255,255,0.804) 0 0 0 0.8px`) that look like a partial/broken ring. Wait **≥300ms** after each focus move before reading, or the result is a false negative on both Chromium and WebKit.

**Confirmed-good settled ring values for `bds-calendar-grid` (both Chromium and WebKit):** `outlineWidth: 3px`, `outlineStyle: solid`, `outlineColor: rgb(158, 197, 255)` (`$boreal-focus`), `boxShadow: rgb(255, 255, 255) 0px 0px 0px 1px` (`$boreal-white`). Identical on `.bds-calendar-grid__day` (reference), `.bds-calendar-grid__label-button`, `--picker-cell--month`, and `--picker-cell--year`. Disabled picker cells: `tabindex="-1"`, `aria-disabled="true"`, `outlineWidth: 0px`, `boxShadow: none`, skipped by arrow nav (note: `tabindex="-1"` means a programmatic `el.focus()` *can* still move focus to them — they are keyboard-unreachable, not programmatically-unfocusable).

**How to apply:** when the checklist demands a visible `:focus-visible` ring, never read it straight off a mouse-clicked or bare programmatically-focused element; prime keyboard modality with a real non-modifier keypress, then wait past the ring transition. In WebKit, don't rely on Tab to reach buttons.
