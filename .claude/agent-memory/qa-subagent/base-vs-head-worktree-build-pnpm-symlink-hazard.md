---
name: base-vs-head-worktree-build-pnpm-symlink-hazard
description: Building a base-commit git worktree with symlinked node_modules - never call pnpm there (it rewrites the MAIN repo's node_modules links); working recipe and the button-group/dropdown keyboard baseline result
metadata:
  type: project
---

2026-11-20. Worktree of base 4774509f with root/package `node_modules` symlinked to the main repo: running `with-node.sh pnpm ... exec stencil` in it makes pnpm 12 auto-run `pnpm install` THROUGH the symlinks and rewrites ~1130 links (and .bin shims' NODE_PATH) in the main repo's node_modules to point into the worktree (breaks main when the worktree is removed). Recovery that worked: unlink the worktree symlinks, `pnpm install --frozen-lockfile --offline` in main, then a python pass rewriting remaining `*wt*`-pointing links under `node_modules/.pnpm/**` (the hoisted `.pnpm/node_modules` dir is not fixed by the install).

**How to apply:** build in a worktree with `with-node.sh node <main>/packages/boreal-web-components/node_modules/@stencil/core/bin/stencil build --dev --root $PWD --config $PWD/stencil.x.config.ts` (with-node.sh cds to the git toplevel of cwd, so pass absolute paths). Throwaway config must keep a `dist` target (to any scratch dir) or TS fails with `declarationMap ... declaration`; `www` target dir can be absolute scratch path. Never run pnpm there.

Finding: group/toolbar keyboard code (KeyboardController roving) is byte-identical at base and HEAD, so dropdown-in-group/toolbar keyboard hijack defects are pre-existing; only the allow-list warning, joined radii/overlap CSS differ. See [[bds-button-group-dropdown-keyboard-hijack]].
