---
name: stencil-search-bar-scroll-clip-bug
description: bds-search-bar collapse-on-blur icon-clipping bug (EOA-15204) — root cause and exact fix location in bds-search-bar.tsx.
metadata:
  type: project
---

Fixed 2026-07-03 (EOA-15204): `bds-search-bar`'s minimized trigger rendered a clipped/squished icon and misaligned layout after collapsing back from expanded state via keyboard blur.

Root cause: `handleFocus` (bound to `onBdsFocus` at the Host, the composite-event-boundary re-emission of the internal `bds-text-field`'s focus) only set `this.focused = true` — it never called `openSearchBar()`. The leading icon trigger button's `tabIndex` is conditionally managed (`triggerTabIndex` getter), but the wrapped `<input>` is not, so Shift+Tab could focus the `<input>` directly while `isOpen` was still `false`. See [[feedback-scroll-into-view-collapsed-focusable]] for the general pattern.

Fix applied in `packages/boreal-web-components/src/components/forms/bds-search-bar/bds-search-bar.tsx`:
- `handleFocus` now also calls `void this.openSearchBar()` when `!this.isOpen && variant !== 'static'`.
- `closeSearchBar()` now awaits the width transition (renamed `waitForExpandTransition` → `waitForSelectWidthTransition`, reused for both directions) and then calls a new `resetFieldScroll()` helper that zeroes `.bds-text-field__container`'s `scrollLeft` — defensive belt-and-suspenders in case any other path leaves a residual scroll offset.

Verified live via Playwright against the `InteractiveMethodsExample` story (`forms-search-bar--interactive-methods-example`) across repeated Tab/Shift+Tab expand-collapse cycles — `scrollLeft` stayed 0 and the icon rendered as a clean magnifying glass every time, including the Shift+Tab-direct-to-input path that reproduced the bug pre-fix.

Full unit test suite (192 suites / 1903 tests) passed after the change (`pnpm --filter=@telesign/boreal-web-components exec stencil test --spec`). Note: `--testPathPattern <name>` on this repo's Stencil/Jest test runner does not scope correctly — the hyphenated pattern gets treated as a character-alternation regex (`b|d|s|-|s|...`), so it silently runs the *entire* suite instead of just the target component. This is a testing-invocation quirk worth flagging to `testing-subagent`/`.claude/agent-memory/testing-subagent/` if not already recorded there.

**Follow-up (same session):** fixing the Shift+Tab bug above reused the animated `openSearchBar()` inside `handleFocus`, which made the pre-existing 200ms width-grow transition fire for a case where it previously never ran at all (input silently gained focus with no visual change). The user correctly flagged this as a new, jarring "movement" — the field visibly grows *after* focus has already landed, which reads differently than the deliberate icon-click/trigger-focus open (where growth happens *before* focus moves into the field). Confirmed via `getBoundingClientRect()` that the icon's position relative to its container is identical in both collapsed and expanded rest states (no actual positioning bug) — the perceived movement is exactly the width transition, now correctly triggered where it used to silently no-op.

Fix: added `expandInstantly()` + a `suppressExpandTransition` `@State`, wired to a new `.bds-search-bar__select--no-transition { transition: none; }` SCSS modifier. `handleFocus` now calls `expandInstantly()` (sets `isOpen = true` with the transition suppressed for two nested `requestAnimationFrame` ticks) instead of `openSearchBar()`. The deliberate open path (`handleTriggerFocus` → `openSearchBar()`) is untouched and still animates. Verified via `transitionrun`/`transitionend` event listeners on the `bds-select` element: the trigger-focus path fires `width` transition events; the Shift+Tab/direct-input-focus path fires none for `width` (only unrelated `border-color`/`box-shadow` from the `--focused` class).

General lesson: reusing an existing "open" method to fix a missing-state-transition bug can silently import that method's side effects (like an animation) into a context where they don't semantically belong. When a fix makes a previously-inert code path suddenly perform a *visible* action for the first time, check whether that action's styling (transition, animation) was designed around the assumption of a specific trigger (deliberate click) that no longer strictly holds for the new caller.
