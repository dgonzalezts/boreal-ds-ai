---
name: shared-dev-docs-server
description: When multiple agents run in the same team session, pnpm dev:docs may already be running on :6006 from another agent — check before starting a duplicate
metadata:
  type: feedback
---

Before running `pnpm dev:docs` to manually verify Storybook changes, check whether port 6006 is already serving (`curl -s -o /dev/null -w '%{http_code}' http://localhost:6006/`). In a multi-agent team session another agent (e.g. a parallel QA or docs task) may already have a live dev server up. Starting a second `dev:docs` triggers Storybook's "Port 6006 is not available, use 6007 instead?" prompt and duplicates the Stencil watch/build process for no benefit — the running instance already serves current `.stories.ts`/`.mdx` source via Vite, and Stencil's own build (which the shared instance's owner already ran) is what actually needs a restart, not Storybook itself.

**How to apply:** if :6006 is already up, kill only your own newly-spawned duplicate process (match on the exact PID/command you started, e.g. `pkill -f "storybook dev -p 6006"` only right after you observed a *new* invocation was still initializing and had not yet bound the port) and reuse the existing instance for Playwright verification instead. Never kill an instance you didn't just start without confirming via `ps aux` that it's the one you spawned this session — it likely belongs to a teammate agent.
