# A Turborepo cache hit leaves stray files in `dist`, and they end up in `pnpm pack`

Verified on Turborepo 2.11.10 and pnpm 12.18.0 in `packages/boreal-react` and `packages/boreal-vue` (EOA-20193, 2026-11-13).

## The Problem

A cache hit restores the cached outputs over an existing `dist` folder without clearing it. A stray file in `packages/boreal-react/dist` or `packages/boreal-vue/dist` therefore survives `pnpm build` and the Turbo build, and is packed by `pnpm pack`. `dist` is gitignored, so `git status` cannot show it. Cleaning inside the `build` script does not help on a cache hit, because the script does not run.

## The Fix

The `before:init` release hook of the two wrappers removes `dist` first, then builds:

```bash
node -e "require('fs').rmSync('dist', { recursive: true, force: true })" && turbo run build ...
```

Tested with stray files placed in both `dist` folders before the hook.

## How to verify

Create `dist/stray.txt`, run the hook command (see [[release-it-hook-names-and-timing]] for how to run it, since a dry run does not), then `pnpm pack --dry-run` or list the tarball: the file must be gone.

Related: [[turbo-cache-watcher-poisoned-dist]] (a different way the cache keeps wrong bytes), [[scripts-boreal-pack-pipeline]].
