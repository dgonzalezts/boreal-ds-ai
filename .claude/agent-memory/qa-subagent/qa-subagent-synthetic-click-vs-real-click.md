---
name: qa-subagent-synthetic-click-vs-real-click
description: Calling .click() directly on bds-button's internal native <button> (or dispatching a synthetic MouseEvent) does not reliably trigger the component's real click-handling/bdsClick re-emission — use a real Playwright locator click instead
metadata:
  type: project
---

During `bds-date-picker` QA (EOA-17138 PR-comment follow-up, 2026-09-07), calling `innerBtn.click()` (the raw native `<button>` Stencil renders inside `bds-button`'s light DOM) via `playwright-cli eval` fired a directly-attached `addEventListener('click', ...)` test listener (confirmed via a manual listener + counter) but never triggered `bds-button`'s own internal click handler — `bdsClick` never re-emitted, and the calendar's month-navigation state never advanced across three retries with increasing wait times. Same result whether targeting the raw `<button>` or dispatching a `new MouseEvent('click', {bubbles:true})` at the `bds-text-field` trigger to open a popover (that one happened to work for *opening*, but not for driving nav-button state changes reliably).

Switching to a real Playwright interaction — either `playwright-cli click <ref>` from a snapshot, or `page.locator(...).click()` inside `playwright-cli run-code` — fixed it immediately and produced the expected state changes every time.

**Why:** Not fully root-caused (Stencil's JSX `onClick` binding, event trust/pointer-type checks, or some interaction-guard timing may be involved), but the failure is consistent and silent — no exception, no console warning, the click event listener you attach yourself still fires, only the component's own internal reaction doesn't happen. This is a strictly worse failure mode than an error: it looks like the interaction registered.

**How to apply:** For any QA scenario driving a `bds-button`-based control (nav arrows, Apply/Cancel/Clean, popover triggers, chevrons) via `playwright-cli`, always use a real click (`playwright-cli click <ref>` or `page.locator(...).click()` in `run-code`) — never `element.click()` or a synthetic `dispatchEvent` via `eval`. Reserve `eval`/`run-code`'s `page.evaluate` for state *inspection* (computed styles, prop/attribute reads) and *programmatic prop mutation* (`.value =`, `.required =`, `.min =`) — those work fine synthetically since they don't route through the click-handling path at all. See [[dev-pack-react-vue-serial-not-parallel]] for the companion pipeline gotcha found in the same session.
