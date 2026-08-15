---
name: playwright-cli-stale-nvm-shim
description: bare `playwright-cli` on PATH can resolve to a broken nvm-node20 global install instead of the correct fnm-node22 one
metadata:
  type: project
---

`which -a playwright-cli` on this machine returns `/Users/dgonzalez/.nvm/versions/node/v20.12.2/bin/playwright-cli` before the fnm-managed shims. That nvm copy throws `Cannot find module 'playwright-core/lib/tools/cli-client/program'` on any invocation — a broken/mismatched install, not a real environment problem to fix.

**Why:** discovered during EOA-16692 Task 9 QA (2026-08-14) — first `playwright-cli` call failed immediately with a MODULE_NOT_FOUND error before any browser session was even created.

**How to apply:** always run `.agents/scripts/with-node.sh playwright-cli ...` (per this subagent's own Node.js Environment convention) rather than a bare `playwright-cli` call — this was already the documented rule, but the failure mode here specifically was a *different* stale binary shadowing the correct one on PATH, not just the wrong Node version running a correct binary. Same fix either way.
