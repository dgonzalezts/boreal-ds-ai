---
name: playwright-cli-macos-select-all-keybinding
description: On macOS, page.keyboard.press('Control+a') inside a text input does not select all text via CDP — use 'Meta+a' instead. Silent failure (selectionStart/End stay at 0), not an error.
metadata:
  type: project
---

When driving text-field editing via `playwright-cli press`/`run-code` (`page.keyboard.press(...)`)
on a macOS host, `Control+a` inside a native `<input>`/`<textarea>` does **not** select the field's
text — the browser's real macOS keybinding for select-all is Cmd+A (`Meta+a`), and CDP-driven
`Control+a` doesn't trigger the OS-level Emacs-style "move to start of line" binding some macOS
text fields honor either. The failure is silent: no error, no exception — `selectionStart`/
`selectionEnd` both just stay `0` (cursor placed at start, nothing selected), so a subsequent
`page.keyboard.type(...)` inserts before the existing text instead of replacing it, producing
confusing, hard-to-diagnose "my typed value didn't take" results in QA automation.

**Fix:** always use `Meta+a` for select-all in text-input editing scripts, regardless of what a
Linux/Windows-authored snippet might show. Verified concretely during EOA-17362 (`bds-color-picker`
HEX/opacity field editing) — `Control+a` left `selectionStart === selectionEnd === 0`; `Meta+a`
correctly produced `selectionStart: 0, selectionEnd: <full length>`.

This is a host-OS/CDP-keybinding fact, not a Boreal DS component bug — applies to any text-field
editing across any component's manual QA on a macOS runner.
