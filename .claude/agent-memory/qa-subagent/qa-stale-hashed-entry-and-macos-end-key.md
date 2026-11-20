---
name: qa-stale-hashed-entry-and-macos-end-key
description: Two QA-environment traps found during bds-text-editor T6/T13 re-run - a watch-mode www/ loader can reference a stale hashed p-*.entry.js, and Playwright on macOS makes End/Home scroll the page instead of moving the caret
metadata:
  type: project
---

1. A snapshot of `packages/boreal-web-components/www` taken while a `stencil build --dev --watch` is running can serve STALE component code: `boreal-web-components.esm.js` referenced `p-cff0b4a9.entry.js` (older build) while a newer friendly-named `bds-text-editor.entry.js` sat unused beside it. Symptom: DOM contradicted the source (aria-label "Insert field" on a text-mode trigger although the source computed "Fields").
   **Why:** the loader and the hashed entry only refresh on full rebuilds; incremental rebuilds write the friendly file.
   **How to apply:** before QA, grep the loader (`boreal-web-components.esm.js`) for the component's entry reference and grep THAT file for a string from the latest source change. If stale, run a one-shot `.agents/scripts/with-node.sh pnpm --filter=@pxglobal/boreal-web-components exec stencil build --dev` (about 15 s; `pnpm exec stencil` from inside the package fails, use `--filter ... exec`), then re-copy `www` to a scratch dir and serve it with `python3 -m http.server <port>` so other sessions' watchers cannot change it mid-run. Re-run every earlier check on the fresh bundle.

2. In Playwright on macOS, `keyboard.press('End')` / `'Home'` scroll the document (macOS binding) and do not move the caret; it looks like a "popover jumps off-screen" bug because floating popovers keep absolute coordinates. Use `Meta+ArrowRight` / `Meta+ArrowLeft` for caret movement. Reproduced with a plain `bds-text-field`, so not a component bug.

3. `playwright-cli run-code` output: filter with awk (`/^### Ran Playwright/{exit}`), macOS `sed` has no `\|`. A script that throws mid-way after state-changing steps leaves the page dirty; reload before re-running.
