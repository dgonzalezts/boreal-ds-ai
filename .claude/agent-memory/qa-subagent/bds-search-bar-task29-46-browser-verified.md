---
name: bds-search-bar-task29-46-browser-verified
description: EOA-19597/98 T24/T29/T32/T33/T34/T40/T45/T46 verified live (Chrome + Playwright WebKit 2368) — findings worth reusing (stale itemsQuery on external value reset, aria-controls="" with no list, disabled trigger emits nothing)
metadata:
  type: project
---

Verified 2026-10-26 against the raw `src/index.html` playground (own stencil dev server on port 3401, so the
shared 3333 server another session owned was never touched). All checklist items passed on Chrome and on
Playwright WebKit; the non-obvious facts below are what a re-run should know.

**Stale `itemsQuery` when a consumer resets `value` programmatically (candidate bug, not in the checklist).**
In `items` mode the filter text lives in `@State() itemsQuery`, which is only reset by the internal clear paths
(`handleFieldClear` → `applyItemsQuery('')`). Assigning `bar.value = ''` from outside clears the field and the
committed value but leaves the query, so the next open shows the *previous* filter's results (repro: `#t10-a`,
type `99` → 19 results, then `el.value = ''`, reopen → still Item 99/199/… with an empty field and empty X).
`Escape`/X do reset it, so a scripted re-test must clear through the component (Escape or the X), never by
assigning `value`, or the following steps inherit a filtered list — this also breaks "pick item-199 after
scrolling" style steps (0 mounted items ⇒ locator timeout).

**`aria-controls` is an empty attribute (`""`) when no listbox exists**, e.g. a `mode="list"` bar with neither
`items` nor a slotted list: `resolveListboxId()` returns `''` and the code still writes the attribute. Harmless
but invalid; removing the attribute in that branch would be cleaner.

**A disabled bar's trigger emits nothing at all** — `bds-button disabled` stops pointer events reaching the
button (hit test lands on the parent `bds-text-field`), so no `bdsSearch` and no popover. The playground prose
("with no list, and in mode=search / disabled, the trigger only emits bdsSearch") over-promises for `disabled`;
the empty-popover half is correct. Playwright's `click` cannot even target a disabled button — use
`mousemove`+`mousedown`+`mouseup` at the button's `getBoundingClientRect()` centre.

**Playwright WebKit build pinning.** `playwright-cli open --browser=webkit` needs the build its own
playwright-core wants (here `webkit-2368`); the cache only had `webkit-2342`/`2358`, and the download from
`cdn.playwright.dev` stalls for minutes at a time. `playwright-cli install-browser webkit` does eventually
finish (≈5 min, retried); a hand-made `ln -s webkit-2358 webkit-2368` *does* launch and can be used as a
stopgap, but the installer replaces that symlink with the real build, so re-launch the session afterwards and
say which build produced which evidence.

**`playwright-cli run-code` prints its return value under a `### Result` heading** — piping the output through
`tail -5` hides it; use `grep -A2 "### Result"`. Inside a run-code script, `page.waitForTimeout` is unreliable —
use `page.evaluate(ms => new Promise(r => setTimeout(r, ms)), ms)`.

**Event-record bookkeeping.** Re-attaching the same `addEventListener` recorder to the same element across
several `eval` calls silently doubles every count; tag each recorded event with a timestamp (`t`) at push time
and filter on it, or scope each run to one attach.
