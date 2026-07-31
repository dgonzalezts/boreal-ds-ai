---
name: stencil-dev-server-direct-invocation
description: How to start a package-scoped Stencil dev server via with-node.sh without triggering the whole monorepo's turbo dev pipeline
metadata:
  type: project
---

`pnpm dev` from a package directory actually runs the root Turborepo `dev` pipeline (builds `boreal-style-guidelines`, starts Storybook, both testapps, etc.) — too heavy for a quick manual-verification loop, and Storybook's interactive "port already in use, use 6007 instead?" prompt hangs a non-interactive shell.

`.agents/scripts/with-node.sh` always `cd`s to the **repo root** (via `git rev-parse --show-toplevel`) before exec'ing its argument, so `with-node.sh pnpm exec stencil ...` or `with-node.sh node_modules/.bin/stencil ...` run from within a package directory fail (`stencil` not found / relative path not found) — the cd happens after the shell already resolved relative paths in some cases, and pnpm's own cwd detection gets confused too.

Working invocation for a scoped, non-interactive Stencil dev server:
```bash
nohup .agents/scripts/with-node.sh bash -c 'cd packages/boreal-web-components && exec node_modules/.bin/stencil build --dev --watch --serve --port 3333' > /tmp/stencil-dev.log 2>&1 &
```
The `bash -c 'cd ... && exec ...'` wrapper re-does the `cd` *after* with-node.sh's own `cd` to repo root, so the relative `node_modules/.bin/stencil` path resolves correctly. Kill via the `stencil build --dev --watch` process (find with `ps aux | grep`), not the parent bash/nohup wrapper.
