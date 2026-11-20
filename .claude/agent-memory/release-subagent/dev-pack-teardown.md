---
name: dev-pack-teardown
description: Stopping pnpm dev:pack:vue/react from a background shell does not run the pipeline cleanup; how to restore the repo
metadata:
  type: project
---

`pnpm dev:pack:vue` first runs `turbo build --filter=...@pxglobal/boreal-web-components`, which also builds the react/vue test apps and the boreal-docs Storybook, so it takes several minutes before vite prints `Local: http://localhost:5173/`.

When the pipeline was stopped by signalling its processes from a Bash call (not Ctrl+C in a terminal), the `publish.js` cleanup did not run: `examples/vue-testapp/package.json`, `packages/boreal-vue/package.json` and `pnpm-lock.yaml` stayed modified and the freshly packed `.tgz` files stayed (gitignored).

**How to apply:** after stopping, run `git checkout HEAD -- examples/vue-testapp/package.json packages/boreal-vue/package.json pnpm-lock.yaml`, delete the new `.tgz` files from `examples/vue-testapp` and `packages/boreal-vue`, then `pnpm install --frozen-lockfile` to relink the workspace symlinks. The Playwright MCP also leaves an untracked `.playwright-mcp/` directory at the repo root; remove it.
