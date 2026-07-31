# Browser-automation conventions for this repo's manual QA

## The Playwright browser instance may be shared with the user's own manual browsing

Always call `mcp__playwright__browser_tabs` with `action: "list"` **first**, before navigating or asserting anything. If a tab unexpectedly changes URL between your own actions, it's very likely the user browsing concurrently in the same shared browser (e.g. checking a Storybook story you just built), not a bug in what you're testing. Open a **dedicated new tab** via `action: "new"` and do all verification work in that one tab for the rest of the session — never assume a tab you didn't just navigate is still on the page you expect; re-check `Page URL` in every tool result.

## `bds-button` swallows native `click`

`bds-button.tsx`'s internal handler calls `event.stopPropagation()` on the native DOM `click` and re-emits its own `bdsClick` custom event instead. Any vanilla-JS/`src/index.html` playground scenario wiring up a `bds-button` must listen for `bdsClick`, never `click` — a plain `addEventListener('click', ...)` on the host silently never fires. (React/Vue consumers are typically unaffected since they bind through the framework wrapper's own event props, which already map to `bdsClick` correctly — this is specific to raw/vanilla usage.)

## `index.html` playground gotchas (apply the same lessons to React/Vue testapp scenarios)

- The Stencil dev server (`stencil build --dev --watch --serve`) does **not** re-copy an edited `src/index.html` to `www/` on save — a running server keeps serving a stale copy indefinitely with no warning. Kill it (`lsof -ti:<port> | xargs kill`) and restart after any `index.html` edit before trusting what the browser shows.
- Never delete a previous task's scenario from `index.html` (or from `App.tsx`/`App.vue` for the React/Vue playgrounds) after verifying it — append new sections/scenarios instead, so any of them can be re-checked later without reconstructing from memory. Document QA steps as visible on-page markup (`<h2>` + `<ol>` steps + pass criteria), not HTML/code comments.
