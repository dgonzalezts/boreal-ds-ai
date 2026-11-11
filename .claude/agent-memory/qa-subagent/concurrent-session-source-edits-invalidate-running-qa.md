---
name: concurrent-session-source-edits-invalidate-running-qa
description: another subagent editing components mid-QA triggers stencil --watch rebuilds that hard-reload the page under test — guard with a load-id sentinel and re-verify after the last rebuild
metadata:
  type: project
---

When a QA run shares the repo with another active session (an implementation or testing subagent), `stencil build --dev --watch --serve` rebuilds on **their** file saves and the dev server's live-reload script **hard-reloads the page** in the middle of a check. Symptoms seen 2026-10-26 during the T30/T31 verification on `bds-search-bar`: right after a `mousedown`/`mouseup` the field read `""` and `value` read `""` (looked exactly like the blanking bug under test), and `window.__logs` suddenly contained page-load warnings again.

Detect and guard:

- Set a sentinel after any setup that matters: `window.__loadId = Math.random()`. Re-read it with every measurement; a changed/undefined value means a reload wiped your state — discard and redo that check.
- After a suspicious blank, check `performance.getEntriesByType('navigation')[0].type` (`"reload"`) and `tail` the dev-server log for `updated component:` / `rebuild finished` timestamps around the moment of the interaction.
- `git hash-object <file>` before and after the run: if the blob hash is unchanged, a rebuild was mtime-only and earlier results still stand. If it changed, re-verify everything measured against the old bundle.
- Do not attribute reload-induced blanks to the code under test.

A rebuild can also land *between* checks without a reload being obvious — treat the served bundle as fresh only after the last `rebuild finished` line.
