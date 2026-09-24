---
name: bds-date-picker-task31-presets-focus-selected-specificity-bug
description: EOA-17662 Task 31 presets sidebar styling QA found a real CSS-specificity bug where a selected preset button loses its primary background on keyboard focus-visible (but not on hover/active, which have explicit selected overrides) — reported, not fixed. Also documents a general CSS-specificity failure pattern worth checking on any future state×modifier matrix.
metadata:
  type: project
---

EOA-17662 Task 31 (Phase 6 presets sidebar Figma styling pass, `bds-date-picker.scss` `.bds-date-picker__preset`) was QA'd against the pulled Figma state matrix (Default/Hover/Focus-visible/Active × Selected/not-selected × Disabled). 9 of 10 combinations pass. One fails:

**Focus-visible + selected**: dispatcher's brief said this should show the primary background "unchanged" from Default/selected, with only the shadow added — described as deliberate/confirmed-correct. What actually renders is NOT unchanged — it falls back to the same light-gray tint used for non-selected hover/focus (`rgb(247,247,248)`), not primary blue at any shade. Confirmed via `getComputedStyle` + `.matches()` (`:focus-visible` true, `--selected` class present, but `background-color` is the wrong token) and visually via screenshot after real Tab-key navigation (not programmatic `.focus()` — see below).

**Root cause — a general pattern, not a one-off typo:** the base (non-selected) block declares background for `:hover`/`:focus-visible`/`:active` together, unscoped to selection state:
```scss
&:hover:not(:disabled), &:focus-visible, &:active:not(:disabled) {
  background-color: $boreal-ui-default-lighter;
}
```
The `&--selected` block only re-declares background for `:hover`/`:active` (specificity (0,3,0), correctly beats the base rule's (0,3,0) by source order) — it has **no** `:focus-visible` override. So for focus-visible alone, the base rule's `.preset:focus-visible` selector (specificity (0,2,0)) beats the plain `.preset--selected` rule (specificity (0,1,0)), and the selected button's background silently reverts to the base hover/focus token.

**Prevention checklist for any future State × Selected(-like modifier) SCSS matrix in this codebase:** whenever a "selected"/"active"/"checked" modifier class needs to survive an interaction pseudo-class (`:hover`, `:focus-visible`, `:active`) that the *base* unmodified selector also styles, the modifier block must explicitly re-declare (or explicitly opt out of) **every** pseudo-class the base declares — not just the ones that happen to need a different value. Silently omitting one (here: `:focus-visible`, because it "shouldn't change" so no override felt necessary) leaves it exposed to the base rule's specificity, which is usually *higher* than the plain modifier class alone. This is invisible from reading the SCSS source or from `newSpecPage`/unit tests — only a live per-state computed-style check catches it.

**Testing methodology gotcha (not a bug, but easy to misdiagnose as one):** `bds-transition-surface` (`_interactions.scss`) puts a 0.3s `background-color`/`box-shadow` transition on these buttons. Reading `getComputedStyle` immediately after a Playwright `.hover()`/`.focus()`/`mouse.down()` call — even in a single combined `run-code` script — can catch the transition at t≈0, returning the *pre*-interaction value and looking like a missing-style bug. Always `page.waitForTimeout(300+)` after triggering a hover/focus/active change before reading computed styles on these preset buttons (and generally on anything using `bds-transition-surface`). Cost me two false-bug diagnoses (hover/selected momentarily reading as unchanged, disabled+selected momentarily reading as transparent) before I added the wait.

**Also learned:** programmatic `locator.focus()` in Chromium does NOT set `:focus-visible` to true (confirmed `el.matches(':focus-visible')` false immediately after `.focus()`). Real `page.keyboard.press('Tab')` / `Shift+Tab` navigation is required to get an authentic `:focus-visible` state for this kind of test — `.focus()` alone is insufficient and will silently under-test the focus-visible state.

See [[qa-subagent-synthetic-click-vs-real-click]] for a related "must use real input, not programmatic/synthetic" gotcha in this same component family.
