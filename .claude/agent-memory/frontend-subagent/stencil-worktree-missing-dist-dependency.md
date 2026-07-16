---
name: stencil-worktree-missing-dist-dependency
description: Fresh worktrees can fail `stencil build` with sass "Can't find stylesheet to import" because the linked @telesign/boreal-style-guidelines workspace package has no dist/ yet
metadata:
  type: project
---

In a freshly created git worktree, `pnpm --filter @telesign/boreal-web-components build` (or plain `stencil build` from that package dir) can fail across dozens of component SCSS files with sass errors like:

```
[ ERROR ] sass error: src/components/.../bds-x.scss:1:1
          Can't find stylesheet to import.
[ ERROR ] ENOENT: no such file or directory, stat
          '.../packages/boreal-web-components/node_modules/@telesign/boreal-style-guidelines/dist/css'
```

Root cause: `node_modules/@telesign/boreal-style-guidelines` is a symlink into the workspace package `packages/boreal-styleguidelines`, and that package's `dist/` is a build artifact — not checked into git. A brand-new worktree checkout has the workspace package's source but no `dist/`, since it was never built in that worktree.

**Why:** worktrees are created from git history, and `dist/` directories are gitignored build output, not committed. `pnpm install`/`fnm use` alone does not build workspace-linked packages.

**How to apply:** before trusting a `stencil build` failure as a real compile error inside a worktree, first run `pnpm --filter @telesign/boreal-style-guidelines build` (or the monorepo's full `pnpm build`) to populate `dist/css`, `dist/scss`, `dist/stencil`. Re-run the component build afterward. This is infrastructure bootstrapping, not a code defect — don't waste time debugging SCSS `@use` paths before ruling this out. See also [[stencil-sass-inject-global-paths-constraint]] in team memory for the related SCSS injection constraint.
