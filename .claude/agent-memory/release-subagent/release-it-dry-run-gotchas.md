---
name: release-it-dry-run-gotchas
description: Non-obvious failures when running release-it 21 / plugin 12 dry-runs and validate:all in this pnpm monorepo
metadata:
  type: project
---

1. `pnpm validate:all` (scripts-boreal `publish.js` cleanup) runs `git checkout HEAD -- package.json pnpm-lock.yaml` on exit, so uncommitted root lockfile edits are silently reverted. Save a copy of any uncommitted `pnpm-lock.yaml` before running it, and re-check `git status` after.

2. pnpm rewrites `pnpm-lock.yaml` with single quotes; the committed file is prettier-formatted (double quotes). After `pnpm add`, run `packages/boreal-web-components/node_modules/.bin/prettier --write pnpm-lock.yaml` to avoid a ~14k-line formatting diff.

3. `@release-it/conventional-changelog@12` fails with `headerPartial is not a function` when two `conventional-changelog-conventionalcommits` versions are installed: `conventional-changelog-preset-loader` does a bare `import()` and pnpm's `.pnpm/node_modules` hoist picked 9.1.0 (from `@commitlint/config-conventional@20`). Fixed by upgrading all three `@commitlint/*` packages to 21.x (they depend on 10.x), leaving a single 10.4.0. After the upgrade, run `rm -rf node_modules && pnpm install --frozen-lockfile`: an in-place install leaves a stale 9.1.0 dir in the virtual store and drops the hoist link, so the preset is not resolvable until node_modules is rebuilt. A `packageExtensions` workaround did not apply under pnpm 11.1.1.

4. Dry-run recipe needs extra flags on a branch without upstream and without npm auth: `--no-git.requireUpstream --no-npm.publish`. release-it 21 rejects unknown flags (strict parsing).

5. First `pnpm build` after a dependency refresh can fail with `defaultValue` JSX type errors in `bds-color-format`/`bds-color-picker` because the git-ignored `src/components.d.ts` is stale; a second `pnpm build` passes.

6. Path-scoped `commitsOpts.path` / `gitRawCommitsOpts.path` (relative to the package dir, arrays accepted) count any `fix`/`feat` commit touching the package folder, including edits to its own `.release-it.json`. To test the hidden-types-only "No new version to release" case, pass a copy of the config via `--config` with `":(exclude).release-it.json"` appended to both path arrays. Scratch commits for path-scoped tests must touch a real file; use `git reset --mixed HEAD~1` (not `--hard`) to keep uncommitted config edits.

7. With `infile: false` the plugin skips the CHANGELOG write; dry-run still prints a cosmetic "Writing changelog to false" line.

8. pnpm forwards extra CLI args only to the last command of an `&&` chain, and `pnpm run x -- --flag` forwards a literal `--` so `release-it -- --dry-run ...` fails with "Unexpected positional argument". Pass flags WITHOUT `--`: `pnpm run release:all --dry-run --ci ...`. Root `release:all` / `release:wc-stack` use `pnpm --filter ... --workspace-concurrency=1 run release` (no extra dependency); react/vue have a `prerelease` script running `pnpm -w run validate:pack:<fw>`.

9. pnpm filter semantics: `name...` = package + its DEPENDENCIES, `...name` = package + its DEPENDENTS. Dependents of web-components include boreal-docs and the example apps, so exclude `./apps/*` and `./examples/*`.

10. `scripts-boreal/bin/publish.js` restores only `<wrapper>/package.json`, `<app>/package.json` and the root `pnpm-lock.yaml` via `git checkout HEAD --` (not the root package.json). When testing uncommitted script edits in react/vue package.json, commit them on the scratch branch first or the gate reverts them.
