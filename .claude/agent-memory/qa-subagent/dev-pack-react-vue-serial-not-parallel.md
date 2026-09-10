---
name: dev-pack-react-vue-serial-not-parallel
description: dev:pack:react and dev:pack:vue each end by starting their own persistent vite dev server in the foreground — never chain them with && or run them concurrently as one command
metadata:
  type: project
---

Root `pnpm run dev:pack:react` / `dev:pack:vue` scripts are `turbo run build --filter=...@telesign/boreal-web-components && pnpm --filter scripts-boreal run dev:pack:<framework>`. The `scripts-boreal` half packs+installs the wrapper AND then runs `vite` in the target testapp as its final step — that `vite` process is long-running and never exits on its own.

**Why:** Chaining `dev:pack:react && dev:pack:vue` in one shell command hangs forever after react's step: the `&&` never proceeds past react's own persistent dev server. Running both scripts truly in parallel (two backgrounded commands started at the same instant) risks a race on the shared `boreal-web-components` turbo build/dist output since both scripts run the same `turbo run build --filter=...` step independently.

**How to apply:** Launch `dev:pack:react` as its own background task first, wait for its dev server's "ready" line (e.g. `VITE ... ready`, `Local: http://localhost:5173/`) in the task output, then launch `dev:pack:vue` as a second, separate background task. Vue's vite instance will auto-fall back to the next free port (`5174` observed) since 5173 is already taken by react's server. Do not `&&`-chain them, and do not fire both simultaneously in the same turn.

See [[qa-subagent-synthetic-click-vs-real-click]] for the companion interaction-testing gotcha found in the same session, and [[concurrent-dev-pack-builds-race-condition]] for the confirmed dist-corruption symptom and a third-party watcher variant of the same race.
