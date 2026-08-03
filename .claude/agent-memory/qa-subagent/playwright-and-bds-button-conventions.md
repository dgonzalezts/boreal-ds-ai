# Browser-automation conventions for this repo's manual QA

## Use playwright-cli (Bash), not the Playwright MCP — it's disabled

The Playwright MCP server is disabled (high token consumption). Drive the browser via
the `playwright-cli` CLI over Bash instead (`@playwright/cli`, already installed
globally). Use a named session per surface — `playwright-cli -s=web-components open ...`,
`-s=react-app`, `-s=vue-app` — rather than a single shared browser instance. Sessions are
separate browser processes, so there's no risk of the user's own manual browsing (e.g. a
Storybook tab they have open) interfering with a run — no dedicated-tab workaround needed.
Never assume a tab you didn't just navigate is still on the page you expect; re-check
`Page URL` in every command's output, or run `playwright-cli -s=<name> tab-list`.

## `bds-button` swallows native `click`

`bds-button.tsx`'s internal handler calls `event.stopPropagation()` on the native DOM `click` and re-emits its own `bdsClick` custom event instead. Any vanilla-JS/`src/index.html` playground scenario wiring up a `bds-button` must listen for `bdsClick`, never `click` — a plain `addEventListener('click', ...)` on the host silently never fires. (React/Vue consumers are typically unaffected since they bind through the framework wrapper's own event props, which already map to `bdsClick` correctly — this is specific to raw/vanilla usage.)

## `index.html` playground gotchas (apply the same lessons to React/Vue testapp scenarios)

- The Stencil dev server (`stencil build --dev --watch --serve`) does **not** re-copy an edited `src/index.html` to `www/` on save — a running server keeps serving a stale copy indefinitely with no warning. Kill it (`lsof -ti:<port> | xargs kill`) and restart after any `index.html` edit before trusting what the browser shows.
- Never delete a previous task's scenario from `index.html` (or from `App.tsx`/`App.vue` for the React/Vue playgrounds) after verifying it — append new sections/scenarios instead, so any of them can be re-checked later without reconstructing from memory. Document QA steps as visible on-page markup (`<h2>` + `<ol>` steps + pass criteria), not HTML/code comments.
