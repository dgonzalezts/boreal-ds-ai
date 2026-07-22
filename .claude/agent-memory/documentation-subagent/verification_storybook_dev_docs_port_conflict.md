---
name: verification-storybook-dev-docs-port-conflict
description: pnpm dev:docs hangs on an interactive port-conflict prompt when port 6006 is already in use; check for an existing instance first
metadata:
  type: project
---

Running `.agents/scripts/with-node.sh pnpm dev:docs` to visually verify a story/MDX change can hang
indefinitely with no error — it starts a fresh Stencil build, then Storybook's CLI prints "Port 6006
is not available. Would you like to run Storybook on port 6007 instead?" and blocks on stdin, which
a backgrounded/piped shell command never answers.

**Why:** another `pnpm dev:docs` or `pnpm dev:components` process (often from an earlier session or
subagent) is frequently still alive and already serving on 6006.

**How to apply:** before starting a new dev server for verification, check first:

```bash
lsof -i :6006 -sTCP:LISTEN -P
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:6006
```

If something is already listening and returns 200, reuse it directly — Vite/Storybook HMR picks up
`.stories.ts`/`.mdx` changes automatically, no restart needed (this is separate from the Stencil
component hot-reload limitation in `feedback_dev_server_restart.md`, which only applies to `.tsx`/
`.scss` component source). Navigate straight to
`http://localhost:6006/iframe.html?id=<story-id>&viewMode=story` (bare story) or
`http://localhost:6006/?path=/docs/<title>--overview` (full MDX docs page, inside the
`#storybook-preview-iframe` — query `iframe.contentDocument`, not `document`, when using
`browser_evaluate` against the docs page) via Playwright MCP tools to verify rendering.

If you do need to start a fresh instance and it hits the port prompt, kill the new duplicate
process (`kill` the backgrounded job / `pkill` matching the dispatcher script) rather than trying to
answer the interactive prompt programmatically — it's not designed to be scripted.
