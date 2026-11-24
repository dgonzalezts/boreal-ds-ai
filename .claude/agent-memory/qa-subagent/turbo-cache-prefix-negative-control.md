---
name: turbo-cache-prefix-negative-control
description: Get a pre-fix browser build without touching packages/ — pull it from an older Turbo cache artifact
metadata:
  type: project
---
EOA-18739 (2026-11-20): to prove a geometry-based harness really catches a slot-relocation order bug, grep `.turbo/cache/*-manifest.json` for `bds-<x>.entry.js`, pick an artifact older than the fix commit, `zstd -dc <hash>.tar.zst | tar -x` into scratch, then serve `packages/boreal-web-components/dist/boreal-web-components/` as `/build` (plus `css/` from any www build) with `python3 -m http.server`. The same qa.html/driver then runs against pre- and post-fix builds. Trying to build a pre-fix copy of `src` via `srcDir: '.qa-src'` fails (Rollup parse error on `export type * from './components.d.ts'`); don't retry.
Also: `.agents/scripts/with-node.sh node <driver.cjs>` that requires the repo's `node_modules/.pnpm/playwright@<v>/node_modules/playwright` runs all three engines in one script; install missing engines with that same copy's `cli.js install firefox webkit` (revision must match its browsers.json).
