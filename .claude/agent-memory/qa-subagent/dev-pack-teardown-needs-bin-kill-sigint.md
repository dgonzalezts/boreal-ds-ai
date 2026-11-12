---
name: dev-pack-teardown-needs-bin-kill-sigint
description: In this shell the `kill` builtin rejects `-INT`/`-s INT` ("illegal pid") and a bare kill of vite skips pack cleanup; use `/bin/kill -INT <publish.js pid>` so dev:pack restores package.json/lockfile.
metadata:
  type: project
---

To stop `pnpm run dev:pack:react|vue` cleanly, send SIGINT to the `node ./bin/publish.js <fw>` process with `/bin/kill -INT <pid>` (pgrep -f "bin/publish.js"). The shell's `kill -INT` / `kill -s INT` fails with `illegal pid`, and killing only the vite child (or the first attempt that ended SIGKILL, exit 137) leaves the wrapper/app `package.json`, `pnpm-lock.yaml` and generated tgz files dirty; the SIGINT path runs the script's `cleanup()` (git checkout HEAD of wrapper package.json, app package.json, pnpm-lock.yaml; removes tgz).

**Why:** the lead's intentional uncommitted lockfile diff gets reverted by cleanup, so it matters that cleanup runs once, deliberately.
**How to apply:** when only a stale-state recovery is needed after a 137 exit, `git checkout HEAD -- <wrapper>/package.json <app>/package.json pnpm-lock.yaml` and delete the `pxglobal-*.tgz` the run created (they are gitignored).

Also: test-app `src/App.tsx` / `App.vue` are clean tracked playgrounds, so scratch scenarios there are reverted with `git checkout -- <file>`. A raw-WC scratch page can be dropped into the gitignored `packages/boreal-web-components/www/` after `stencil build --dev` and served with `python3 -m http.server`, no tracked edits needed. `run-code` sandbox has no `process.env`.
