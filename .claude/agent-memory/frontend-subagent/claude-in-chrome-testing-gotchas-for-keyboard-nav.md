---
name: claude-in-chrome-testing-gotchas-for-keyboard-nav
description: Two claude-in-chrome/macOS testing artifacts that look like real bugs but aren't - clicking a native button doesn't focus it on macOS Chrome, and in-page setTimeout waits evaluated via javascript_tool don't reliably observe a Stencil re-render.
metadata:
  type: project
---

Found while manually verifying `bds-calendar-grid` keyboard traversal (Task 40, EOA-17662)
live via the `claude-in-chrome` MCP tools, on macOS.

**1. Clicking a native `<button>` does not give it keyboard focus on macOS Chrome by
default.** This is a real, long-standing macOS system behavior (tied to "Use keyboard
navigation to move focus between controls" being off by default), not specific to this
codebase or to `bds-button`. After `computer.left_click` (or a JS `.click()`) on a button,
`document.activeElement` can legitimately be `document.body` — this is NOT a sign that the
click failed to register or that the button is broken. Verify the click's actual EFFECT
(state change, emitted event, re-render) rather than asserting `document.activeElement` after
clicking a plain button in this environment.

**2. A page-context `await new Promise(r => setTimeout(r, N))` inside
`javascript_tool`'s evaluated script is NOT a reliable way to wait for a Stencil re-render to
land**, even at 300-500ms. Multiple real state changes (confirmed later, after other actions
forced a visible re-render) were invisible to a same-script `setTimeout`-based wait
immediately following the triggering action — the DOM read up to several stacked updates
"behind" what had actually already happened. The reliable pattern instead: trigger the action,
then use the `computer` tool's own `action: "wait"` (which pauses at the automation/extension
layer, not inside the page's own JS execution) for at least 1 full second, THEN read state
with a fresh `javascript_tool` call. Don't trust a same-call `setTimeout` wait to prove
something did NOT happen — it may simply not have been observed yet.

Both artifacts caused real confusion mid-session (looked like `bdsMonthNavigate`/click wiring
was broken) before being root-caused as tooling/environment quirks, not component bugs.
