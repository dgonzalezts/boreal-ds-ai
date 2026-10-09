# Fresh Git Worktrees Need `@pxglobal/boreal-style-guidelines` Built First

## The Constraint

`pnpm install` in a freshly created git worktree (`git worktree add`) links `node_modules/@pxglobal/boreal-style-guidelines` as a symlink into the workspace package `packages/boreal-style-guidelines`, but that package's `dist/` is a gitignored build artifact — never checked into git and never built in the new worktree.

Any subsequent `stencil build` (or `pnpm --filter @pxglobal/boreal-web-components build`) on a package that consumes the style guidelines fails with unrelated-looking Sass errors such as:

```
[ ERROR ] sass error: src/components/.../bds-x.scss:1:1
          Can't find stylesheet to import.
[ ERROR ] ENOENT: no such file or directory, stat
          '.../packages/boreal-web-components/node_modules/@pxglobal/boreal-style-guidelines/dist/css'
```

The error surfaces per-component-SCSS-file and looks like a Sass path/config regression, but the root cause is upstream: the style guidelines package has never been built in this checkout.

## Fix

Before trusting a `stencil build` failure inside a fresh worktree as a real compile error, run the style guidelines build once first:

```
pnpm --filter @pxglobal/boreal-style-guidelines build
```

This populates `dist/css`, `dist/scss`, and `dist/stencil`. Re-run the dependent package build afterward.

## Why It Recurs

Worktrees do not share `node_modules`/`dist` build state with the main checkout or with each other. This will affect every future worktree-based task (frontend, testing, release work alike) until the style guidelines package is built in that specific worktree.

## Related

- `stencil-sass-inject-global-paths-constraint.md` (personal auto-memory) covers the separate constraint that `injectGlobalPaths` files must be self-contained and component SCSS must not `@use` the token package — a different failure mode from this one, but easy to conflate since both surface as Sass import errors.
- The `fnm use` non-interactive-shell activation pattern (`eval "$(fnm env --shell bash)" && fnm use && ...`) is already handled centrally by `.agents/scripts/with-node.sh` — no separate memory entry needed for that part of this discovery.

Source: AI-001 `bds-button` accessibility diagnostics session, encountered when bootstrapping a fresh worktree for parallel subagent work.
