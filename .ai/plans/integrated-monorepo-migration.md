---
status: in progress
---

# Integrated Monorepo Migration Plan

## pnpm Workspaces + Turborepo + Root-Level Git Hooks + release-it

---

## What This Plan Does

Replaces the current per-package, npm-based, hook-less monorepo with a fully orchestrated setup. Fixes three problems at once:

1. **Cross-package hook failures** → hooks move to root, become package-aware
2. **`file:` tarball references that break npm publishing** → replaced with `workspace:*`
3. **No build orchestration/caching** → Turborepo manages task pipeline and caching

### Why all three at once?

The root `package.json` is being created from scratch anyway. Doing hooks-only first would require reopening and modifying that same file immediately for Turborepo. The `file:` → `workspace:*` migration is a prerequisite for both Turborepo's graph resolution and correct publishing. A single migration is cleaner than two.

---

## Actual Implementation — Deviations from Plan

This section documents every place the final implementation differs from the plan above. The plan text is preserved for historical context.

| Plan                                                                                        | Actual                                                                                                                  | Reason                                                                                                                                                                                                                                                                             |
| ------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `"packageManager": "pnpm@9.15.4"`                                                           | `"packageManager": "pnpm@10.7.1"`                                                                                       | 10.x was current at install time                                                                                                                                                                                                                                                   |
| `"engines": { "pnpm": ">=9" }`                                                              | `"engines": { "pnpm": ">=10" }`                                                                                         | Aligned with actual version constraint                                                                                                                                                                                                                                             |
| `"version": "0.0.0"`                                                                        | `"version": "0.0.1"`                                                                                                    | Existing convention in the monorepo                                                                                                                                                                                                                                                |
| No `"type": "module"` (explicitly warned against)                                           | `"type": "module"` present in root `package.json`                                                                       | Required: `.lintstagedrc.js` and `commitlint.config.js` use `export default` (ESM). Without `"type": "module"`, Node treats `.js` as CJS and throws a SyntaxError. The risk table entry is now moot — all root configs were audited and are ESM-compatible.                        |
| `test` task: `"cache": false`, no `inputs`, `"outputs": ["coverage/**"]`                    | `test`: `"cache": true`, `inputs` set, `"outputs": []`; separate `test:coverage` task with `"outputs": ["coverage/**"]` | Splitting test and coverage into separate tasks enables Turbo to cache clean test runs (which are fast on `pre-push`). Coverage is opt-in and expensive — it shouldn't run on every test invocation.                                                                               |
| `.husky/pre-commit` and `.husky/commit-msg` only                                            | Added `.husky/pre-push`                                                                                                 | Runs `pnpm turbo run test --filter=@boreal-ds/web-components` before every push, ensuring tests are green before remote receives the branch.                                                                                                                                       |
| `.lintstagedrc.js` boreal-web-components entry runs lint + format + **test** on `.ts` files | Test runner removed from pre-commit                                                                                     | Tests run on `pre-push`, not `pre-commit`. Running Stencil tests on every commit is too slow for commit-time UX.                                                                                                                                                                   |
| `commitizen` / `@commitlint/cz-commitlint` not in plan                                      | Added `commitizen`, `@commitlint/cz-commitlint`; `"commit": "cz"` script; `"config": { "commitizen": ... }`             | Interactive commit prompt (`pnpm commit`) reduces friction for the enforced ticket-format rule.                                                                                                                                                                                    |
| `pnpm.onlyBuiltDependencies` not in plan                                                    | Added `"pnpm": { "onlyBuiltDependencies": ["@parcel/watcher", "esbuild", "puppeteer"] }` at root                        | Required after clean install: pnpm v10 blocks build scripts by default. Moving this from `apps/boreal-docs/package.json` (per-package scope is ignored by pnpm) to root `package.json` resolves the warning.                                                                       |
| Changesets (`@changesets/cli`) as the release tool                                          | Replaced by **release-it** + `@release-it/conventional-changelog` + `@wc-toolkit/changelog`                             | Changesets fully removed (no `/.changeset/` dir, no `changeset`/`version-packages`/`release` scripts). Per-package `.release-it.json` configs drive automated versioning, changelog generation, git tagging, and npm publishing. See `.ai/plans/automated-changelog-&-release.md`. |
| `scripts-boreal` noted as superseded by Turborepo                                           | `scripts-boreal` is NOT superseded — it serves a distinct role                                                          | Turborepo orchestrates builds via workspace symlinks. `scripts-boreal` replaces those symlinks with real `.tgz` artifacts to validate `exports`, `files`, and `publishConfig` before publishing. See `.ai/guidelines/scripts-boreal.md`.                                           |
| `turbo.json` schema: `https://turborepo.dev/schema.json`                                    | `https://v2-8-7.turborepo.dev/schema.json`                                                                              | Intentionally pinned to the version-specific schema URL — not changed.                                                                                                                                                                                                             |

---

## The `file:` Problem (Teammate's Concern — Addressed)

The current `"@boreal-ds/web-components": "file:boreal-ds-web-components-0.0.1.tgz"` reference in `boreal-react` and `boreal-vue` is published as-is to npm. Consumers who install `@boreal-ds/react` get a broken package because `file:` paths resolve on the publisher's machine, not the consumer's.

**The fix**: pnpm's `workspace:*` protocol resolves to the local workspace package during development, and is **automatically replaced by the real published version number** when `pnpm publish` / `changeset publish` runs. No manual steps needed.

---

## Critical Files

### Create (new)

| File                                               | Purpose                                                                                                                                |
| -------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `/pnpm-workspace.yaml`                             | Declares all workspace members                                                                                                         |
| `/package.json`                                    | Root orchestration hub (turbo, husky, release-it)                                                                                      |
| `/turbo.json`                                      | Task pipeline and caching config                                                                                                       |
| `/.husky/pre-commit`                               | Root pre-commit hook                                                                                                                   |
| `/.husky/commit-msg`                               | Root commit-msg hook                                                                                                                   |
| `/.lintstagedrc.js`                                | Package-aware lint-staged (uses `pnpm --filter`)                                                                                       |
| `/commitlint.config.js`                            | Migrated and expanded from `packages/boreal-web-components/` — imports custom rules plugin                                             |
| `/commitlint-custom-rules.js`                      | Custom commitlint plugin: `type-required`, `scope-required`, `subject-required`, `ticket-format` rules with descriptive error messages |
| `packages/boreal-web-components/.release-it.json`  | Per-package release-it config: tag format, changelog preset, CEM check hook                                                            |
| `packages/boreal-react/.release-it.json`           | Per-package release-it config                                                                                                          |
| `packages/boreal-vue/.release-it.json`             | Per-package release-it config                                                                                                          |
| `packages/boreal-styleguidelines/.release-it.json` | Per-package release-it config                                                                                                          |

### Modify (existing)

| File                                           | Change                                                                                                                   |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `packages/boreal-react/package.json`           | `file:` → `workspace:*`, `npm run` → `pnpm run`                                                                          |
| `packages/boreal-vue/package.json`             | Same + add missing `publishConfig`                                                                                       |
| `packages/boreal-web-components/package.json`  | Remove `prepare` + husky/lint-staged/commitlint devDeps, add `publishConfig`                                             |
| `packages/boreal-styleguidelines/package.json` | Add `publishConfig`, fix `npm run` → `pnpm run` (package is now a design token pipeline)                                 |
| `examples/react-testapp/package.json`          | `file:` → `workspace:*`                                                                                                  |
| `packages/boreal-vue/package.json`             | Fix `"test"` script (currently exits with code 1)                                                                        |
| `.gitignore`                                   | Add `.turbo/`                                                                                                            |
| `README.md`                                    | Replace `npm install` with `pnpm install`; document Turborepo scripts, commit format, workspace layout, release workflow |

### Delete

| Path                                                            |
| --------------------------------------------------------------- |
| `packages/boreal-web-components/.husky/` (entire dir)           |
| `packages/boreal-web-components/.lintstagedrc.json`             |
| `packages/boreal-web-components/commitlint.config.ts`           |
| `packages/boreal-react/boreal-ds-web-components-0.0.1.tgz`      |
| All `node_modules/` directories (reinstalled by pnpm from root) |
| All `package-lock.json` files                                   |

---

## Implementation Phases

### Phase 1 — Backup Current Config

```bash
mkdir -p .backup-hooks
cp -r packages/boreal-web-components/.husky .backup-hooks/
cp packages/boreal-web-components/.lintstagedrc.json .backup-hooks/
cp packages/boreal-web-components/commitlint.config.ts .backup-hooks/
cp packages/boreal-web-components/package.json .backup-hooks/package.json.bak
```

---

### Phase 2 — Create `pnpm-workspace.yaml`

**File:** `/pnpm-workspace.yaml`

```yaml
packages:
  - "packages/*"
  - "apps/*"
  - "examples/*"
  - "scripts-boreal"
```

> `"scripts-boreal"` is listed explicitly (not via glob) because it lives at the workspace root rather than inside a glob-covered directory.

---

### Phase 3 — Create Root `package.json`

**File:** `/package.json`

```json
{
  "name": "boreal-ds",
  "version": "0.0.1",
  "private": true,
  "type": "module",
  "description": "Boreal Design System monorepo",
  "packageManager": "pnpm@10.7.1",
  "engines": {
    "node": ">=22",
    "pnpm": ">=10"
  },
  "scripts": {
    "build": "turbo run build",
    "test": "turbo run test",
    "lint": "turbo run lint",
    "lint:fix": "turbo run lint:fix",
    "format": "turbo run format",
    "format:check": "turbo run format:check",
    "dev": "turbo run dev",
    "dev:components": "turbo run dev --filter=@telesign/boreal-web-components",
    "dev:docs": "turbo run dev --filter=@telesign/boreal-docs",
    "clean:wc": "pnpm --filter @telesign/boreal-web-components exec -- rm -rf dist .stencil",
    "generate:component": "pnpm --filter @telesign/boreal-web-components run generate",
    "generate:story": "pnpm --filter @telesign/boreal-docs run generate:story",
    "rebuild:styles": "pnpm --filter @telesign/boreal-style-guidelines run build",
    "release:styles": "pnpm --filter @telesign/boreal-style-guidelines run release",
    "release:wc": "pnpm --filter @telesign/boreal-web-components run release",
    "release:react": "pnpm --filter @telesign/boreal-react run release",
    "release:vue": "pnpm --filter @telesign/boreal-vue run release",
    "release:all": "pnpm run release:styles && pnpm run release:wc && pnpm run release:react && pnpm run release:vue",
    "prepare": "husky",
    "commit": "cz",
    "validate:pack": "node scripts-boreal/bin/publish.js react --ci"
  },
  "devDependencies": {
    "@commitlint/cli": "^20.4.1",
    "@commitlint/config-conventional": "^20.4.1",
    "@commitlint/cz-commitlint": "^20.4.1",
    "@release-it/conventional-changelog": "^10.0.5",
    "@wc-toolkit/changelog": "^1.0.2",
    "commitizen": "^4.3.1",
    "husky": "^9.1.7",
    "lint-staged": "^16.2.7",
    "release-it": "^19.2.4",
    "turbo": "^2.8.7"
  },
  "config": {
    "commitizen": {
      "path": "@commitlint/cz-commitlint"
    }
  },
  "pnpm": {
    "onlyBuiltDependencies": ["@parcel/watcher", "esbuild", "puppeteer"]
  }
}
```

> `"type": "module"` — required because `.lintstagedrc.js` and `commitlint.config.js` use `export default`. Without it, Node treats `.js` as CJS and throws a SyntaxError when husky invokes them.
> `"private": true` prevents accidental root-level publishing.
> `"prepare": "husky"` auto-installs git hooks on `pnpm install`.
> `"commit": "cz"` — interactive prompt via Commitizen, driven by `@commitlint/cz-commitlint`.
> `pnpm.onlyBuiltDependencies` — pnpm v10 blocks all build scripts by default. This allowlist permits the three packages that require native compilation or postinstall steps.
> `release` excludes `@boreal-ds/docs` (private Storybook app, never published).

---

### Phase 4 — Create `turbo.json`

**File:** `/turbo.json`

```json
{
  "$schema": "https://v2-8-7.turborepo.dev/schema.json",
  "ui": "tui",
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", "loader/**", "components-build/**", ".stencil/**"],
      "cache": true
    },
    "test": {
      "dependsOn": ["build"],
      "inputs": ["src/**/*.ts", "src/**/*.tsx", "src/**/*.spec.ts"],
      "outputs": [],
      "cache": true
    },
    "test:coverage": {
      "dependsOn": ["build"],
      "inputs": ["src/**/*.ts", "src/**/*.tsx", "src/**/*.spec.ts"],
      "outputs": ["coverage/**"],
      "cache": true
    },
    "lint": { "outputs": [], "cache": true },
    "lint:fix": { "outputs": [], "cache": false },
    "format": { "outputs": [], "cache": false },
    "format:check": { "outputs": [], "cache": true },
    "dev": {
      "dependsOn": ["^build"],
      "persistent": true,
      "cache": false
    }
  }
}
```

> `"dependsOn": ["^build"]` on `build`: the `^` prefix means "build all workspace dependencies first."
> This guarantees `@boreal-ds/web-components` builds before `@boreal-ds/react` and `@boreal-ds/vue`.
> `test` uses `"dependsOn": ["build"]` (no `^`) — tests run after the local package builds,
> relying on the build chain having already resolved cross-package deps.
> `test` vs `test:coverage`: split into two tasks so `pnpm test` (used by `pre-push`) is fast and cacheable. Coverage is expensive and should be run explicitly via `pnpm test:coverage`. Stencil handles coverage via `stencil test --spec --coverage` — no additional tooling required.
> `lint`/`format:check` are cached; `lint:fix`/`format` are not (they modify files).
> `dev` is `persistent: true` for long-running Storybook/Vite servers.
> Schema URL pinned to `https://v2-8-7.turborepo.dev/schema.json` — intentionally version-specific.

---

### Phase 5 — Replace `file:` References with `workspace:*`

#### `packages/boreal-react/package.json`

Change in `dependencies`:

```json
"@boreal-ds/web-components": "workspace:*"
```

Also change: `"build": "pnpm run tsc"` (was `npm run tsc`).
`publishConfig` is already present — verify it reads `"access": "public"`.

#### `packages/boreal-vue/package.json`

Change in `dependencies`:

```json
"@boreal-ds/web-components": "workspace:*"
```

Also change: `"build": "pnpm run tsc"` (was `npm run tsc`).
Add missing `publishConfig`:

```json
"publishConfig": { "access": "public" }
```

Fix broken test script (currently exits code 1):

```json
"test": "echo 'No tests configured'"
```

#### `packages/boreal-web-components/package.json`

- Remove from `scripts`: `"prepare": "cd ../.. && husky packages/boreal-web-components/.husky"`
- Remove from `devDependencies`: `husky`, `lint-staged`, `@commitlint/cli`, `@commitlint/config-conventional`
- Add:

```json
"publishConfig": { "access": "public" }
```

#### `packages/boreal-styleguidelines/package.json`

Add:

```json
"publishConfig": { "access": "public" }
```

Also change `npm run` → `pnpm run` in three scripts (package has been significantly updated — it is now a design token pipeline, not a static guidelines package):

```json
"build": "pnpm run clean && pnpm run generate && pnpm run validate",
"dev": "pnpm run build",
"prepublishOnly": "pnpm run build"
```

> `dev` is intentionally left as a one-shot build alias for now. See **Future Stage: style-guidelines watch mode** below.

#### `examples/react-testapp/package.json`

Change `@boreal-ds/react` dependency:

```json
"@boreal-ds/react": "workspace:*"
```

#### Delete tarball file

```bash
rm packages/boreal-react/boreal-ds-web-components-0.0.1.tgz
```

---

### Phase 6 — Root Git Hooks

#### `/.husky/pre-commit`

```sh
pnpm lint-staged
```

#### `/.husky/commit-msg`

```sh
pnpm commitlint --edit "$1"
```

#### `/.husky/pre-push`

```sh
pnpm turbo run test --filter=@boreal-ds/web-components
```

> `pre-push` runs only web-components tests — the only package with a test suite. Tests run on push (not on commit) to keep commit-time UX fast. Turbo caches results: if source files haven't changed since the last run, the push completes immediately.

> Husky v9 hooks are minimal shell scripts — no `#!/bin/sh` header or `husky.sh` source line needed.

#### `/.lintstagedrc.js`

```js
/**
 * Root lint-staged configuration — Boreal DS monorepo.
 *
 * Uses () => 'command' functions (not plain strings) to prevent lint-staged
 * from appending matched file paths to `pnpm --filter` commands, which would
 * produce invalid CLI syntax. The package's own scripts handle file scope.
 *
 * Intentionally excluded: boreal-react, boreal-vue, boreal-styleguidelines
 * (no independent lint/format toolchain configured in those packages).
 *
 * Tests are intentionally NOT run on pre-commit. They run on pre-push via
 * .husky/pre-push, keeping commit-time UX fast.
 */
export default {
  // boreal-web-components: TypeScript/TSX — lint + format only
  "packages/boreal-web-components/src/**/*.{ts,tsx}": [
    () => "pnpm --filter @boreal-ds/web-components run lint:fix",
    () => "pnpm --filter @boreal-ds/web-components run format",
  ],

  // boreal-web-components: Styles — format only
  "packages/boreal-web-components/src/**/*.{css,scss}": [
    () => "pnpm --filter @boreal-ds/web-components run format",
  ],

  // boreal-docs: TypeScript/TSX — lint + format
  "apps/boreal-docs/**/*.{ts,tsx}": [
    () => "pnpm --filter @boreal-ds/docs run lint:fix",
    () => "pnpm --filter @boreal-ds/docs run format",
  ],

  // boreal-docs: Other assets — format only
  "apps/boreal-docs/**/*.{js,json,css,md,mdx}": [
    () => "pnpm --filter @boreal-ds/docs run format",
  ],
};
```

#### `/commitlint-custom-rules.js`

Custom commitlint plugin providing four rules with descriptive error messages:

| Rule               | Enforces                                                                       |
| ------------------ | ------------------------------------------------------------------------------ |
| `type-required`    | Type must be present and non-empty                                             |
| `scope-required`   | Scope must be present when header matches `type(scope):` pattern               |
| `subject-required` | Subject must be non-empty after the colon                                      |
| `ticket-format`    | Subject must start with `EOA-1234 description` OR `* description` (non-ticket) |

#### `/commitlint.config.js`

Expanded from `packages/boreal-web-components/commitlint.config.ts`. Key differences from the original plan:

- Imports `commitlint-custom-rules.js` as a plugin — both files must exist together
- `type-enum`: removed `chore` and `ticket`, added `test`
- `scope-enum` enforced — scope is now **required** and must be one of 13 defined values
- Built-in `type-empty`, `scope-empty`, `subject-empty` rules **disabled** in favour of custom equivalents with better error messages
- `prompt` config added for `@commitlint/cz-commitlint` interactive mode

**Enforced commit format:**

```
type(scope): TICKET-123 description
type(scope): * description   ← for non-ticket changes
```

**Valid types:** `feat`, `fix`, `test`, `docs`, `build`, `ci`, `refactor`, `revert`, `style`, `perf`

**Valid scopes:** `react`, `vue`, `web-components`, `styles`, `docs`, `examples`, `scripts`, `workspace`, `ci`, `deps`, `release`, `multiple`

> Both files use `export default` (ESM syntax). commitlint v20 loads configs via dynamic `import()`, so this works correctly even without `"type": "module"` in the root `package.json`.

---

### Phase 7 — Release Tooling Setup (release-it)

> **Note:** Changesets was originally planned here but was fully replaced by release-it before implementation. There is no `/.changeset/` directory in the repo. See `.ai/plans/automated-changelog-&-release.md` for the complete release-it implementation plan.

**Tool stack:**

- `release-it` — version bump, git tag, npm publish, CHANGELOG generation
- `@release-it/conventional-changelog` — reads commit history using the project's conventional commit format
- `@wc-toolkit/changelog` — CEM-based breaking change detection for `@boreal-ds/web-components`

**Per-package config:** Each publishable package has its own `.release-it.json`. Key settings common to all:

- `requireBranch: "release/current"` — blocks release from any other branch
- `github.release: false` — no GitHub API calls (Bitbucket on-prem)
- `headerPattern` strips ticket IDs (e.g. `EOA-9606`) from subjects before they appear in changelogs
- `commitMessage` uses `* ` prefix — passes the project's `ticket-format` commitlint rule

**Publishing workflow:**

```bash
# Per-package release (run in dependency order):
pnpm release:styles      # → release-it in boreal-styleguidelines (independent)
pnpm release:wc          # → release-it in boreal-web-components (independent)
                         #   includes CEM breaking change report before version prompt
pnpm validate:pack       # Pre-publish gate: packs real .tgz artifacts, installs into
                         # react-testapp, builds — validates exports/files/publishConfig
                         # before anything reaches npm. Runs in CD Job 5d.
pnpm release:react       # → release-it in boreal-react (after web-components)
pnpm release:vue         # → release-it in boreal-vue (after web-components)

# Or release all in one command (sequential, dependency order):
pnpm release:all         # styles → wc → react → vue
```

> `validate:pack` is the gate between `wc` and the wrapper packages (`react`, `vue`) — it validates the packed web-components artifact before the wrappers publish against it. If it fails, the publish is aborted. See `.ai/guidelines/scripts-boreal.md`.
>
> `workspace:*` in `boreal-react` and `boreal-vue` is automatically replaced with the real published version number by pnpm when `release-it` triggers `npm publish`.

---

### Phase 8 — Cleanup Package-Level Hooks

```bash
rm -rf packages/boreal-web-components/.husky
rm packages/boreal-web-components/.lintstagedrc.json
rm packages/boreal-web-components/commitlint.config.ts
```

---

### Phase 9 — Clean Install

```bash
# Remove all old npm artifacts
find . -name "node_modules" -type d -prune -exec rm -rf {} \;
find . -name "package-lock.json" -delete

# Single root install — resolves all workspaces, runs prepare (→ husky)
pnpm install
```

---

### Phase 10 — Update `.gitignore`

Add to existing `.gitignore`:

```
# Turborepo
.turbo/
```

> Do NOT add `pnpm-lock.yaml` to `.gitignore` — the root lock file must be committed to git.

---

### Phase 11 — Update `README.md`

The existing README references `npm install` and documents none of the new tooling. Replace it to reflect the migrated monorepo.

**Sections to include:**

1. **Prerequisites** — Node.js 22+ (fnm recommended), pnpm 10+
2. **Installation** — `pnpm install` (not `npm install`); explain that `prepare` auto-installs git hooks
3. **Project structure** — workspace layout (`packages/`, `apps/`, `examples/`)
4. **Available scripts** — document all root scripts and what they do:

| Script                | What it does                                                           |
| --------------------- | ---------------------------------------------------------------------- |
| `pnpm build`          | Builds all packages in topological order via Turborepo                 |
| `pnpm test`           | Runs tests across all packages (after build)                           |
| `pnpm lint`           | Lints all packages (cached)                                            |
| `pnpm lint:fix`       | Fixes lint issues across all packages                                  |
| `pnpm format`         | Formats all files with Prettier                                        |
| `pnpm format:check`   | Checks formatting without writing                                      |
| `pnpm dev`            | Starts all dev servers concurrently (Storybook + Stencil watch)        |
| `pnpm validate:pack`  | Pre-publish gate: packs artifacts, installs into react-testapp, builds |
| `pnpm release:styles` | Releases `@boreal-ds/style-guidelines` via release-it                  |
| `pnpm release:wc`     | Releases `@boreal-ds/web-components` via release-it                    |
| `pnpm release:react`  | Releases `@boreal-ds/react` via release-it                             |
| `pnpm release:vue`    | Releases `@boreal-ds/vue` via release-it                               |
| `pnpm release:all`    | Releases all packages in dependency order                              |

5. **Commit format** — document the enforced convention (enforced by husky + commitlint):

```
type(scope): TICKET-123 description
type(scope): * description   ← non-ticket changes
```

Valid types, valid scopes, examples. See [Angular Commit Message Guidelines](https://github.com/angular/angular/blob/22b96b9/CONTRIBUTING.md#-commit-message-guidelines) for the convention this format is based on.

6. **Release workflow** — per-package release-it flow: `pnpm release:wc` → `pnpm validate:pack` → `pnpm release:react` / `pnpm release:vue`, or `pnpm release:all` for all packages in order

7. **Adding a new package** — note that `pnpm-workspace.yaml` globs pick up new dirs in `packages/*`, `apps/*`, `examples/*` automatically

**Note:** Remove the `npm install` instruction entirely — running npm in this repo will not install workspace deps correctly and will create a `package-lock.json` which is gitignored.

---

## Verification Steps

```bash
# 1. Workspace links (symlinks, not tarballs)
ls -la packages/boreal-react/node_modules/@boreal-ds/web-components
# → symlink pointing to ../../boreal-web-components

# 2. Build pipeline (web-components builds first)
pnpm build
# → web-components completes before react/vue start

# 3. Turborepo cache (second run near-instant)
pnpm build
# → "cache hit" messages for unchanged packages

# 4. Git hooks installed
ls -la .husky/
# → pre-commit, commit-msg, and pre-push exist and are executable

# 5. Pre-commit: web-components files only trigger web-components lint
touch packages/boreal-web-components/src/temp.ts
git add packages/boreal-web-components/src/temp.ts
git commit -m "test: verify hook"
# → lint+format+test run for web-components ONLY
# Cleanup: git reset HEAD~1 && rm packages/boreal-web-components/src/temp.ts

# 6. Pre-commit: docs files do NOT trigger web-components lint
touch apps/boreal-docs/src/stories/temp.ts
git add apps/boreal-docs/src/stories/temp.ts
git commit -m "test: verify docs hook isolation"
# → lint+format run for docs ONLY

# 7. commitlint rejects bad messages
git commit --allow-empty -m "bad commit message"
# → commitlint error (missing type, scope, and ticket format)

git commit --allow-empty -m "feat: add something"
# → commitlint error (missing scope)

git commit --allow-empty -m "feat(web-components): add something"
# → commitlint error (subject must start with ticket ID or '* ')

# 8. commitlint accepts valid messages
git commit --allow-empty -m "feat(web-components): EOA-9606 test commitlint"
# → success (ticket format)

git commit --allow-empty -m "chore(workspace): * update turbo config"
# → success (non-ticket format with '* ' prefix)

# 9. release-it dry-run for all publishable packages
#    Verifies: tag format, changelog generation, version prompt — no files written
pnpm --filter @boreal-ds/style-guidelines run release -- --dry-run
pnpm --filter @boreal-ds/web-components run release -- --dry-run
pnpm --filter @boreal-ds/react run release -- --dry-run
pnpm --filter @boreal-ds/vue run release -- --dry-run
# → Each should show: correct tag format (e.g. @boreal-ds/web-components@X.Y.Z)
# → Changelog preview generated from conventional commit history
# → No commits, tags, or publishes created

# 10. Verify workspace:* is replaced on pack
#     This is the definitive test for the teammate's concern:
#     "does workspace:* get replaced with a real version before publishing?"
cd packages/boreal-react
pnpm pack --dry-run
# → MUST show real version number for @boreal-ds/web-components, NOT "workspace:*"
cd ../..

# 11. scripts-boreal integration test
pnpm validate:pack
# → Packs web-components and boreal-react as real .tgz artifacts
# → Installs into react-testapp (replacing workspace symlinks)
# → Runs pnpm build in react-testapp
# → Pass: build succeeds; Fail: missing export/file/publishConfig issue caught
```

---

## Future Stages

### Future Stage: `@boreal-ds/style-guidelines` watch mode

**Context:** `boreal-styleguidelines` is a design token pipeline — it reads JSON token files and generates `dist/css/`, `dist/scss/`, and `dist/stencil/` outputs via `tsx`. Its `dev` script is currently a one-shot build alias (`pnpm run build`), which means `turbo run dev` builds it once and exits. This is semantically misaligned with `"persistent": true` in `turbo.json`.

**Goal:** Make `dev` a true file-watcher that re-runs token generation whenever any `.json` token file changes.

**Implementation (single file change):**

`packages/boreal-styleguidelines/package.json`:

```json
"dev": "tsx watch src/generators/generate.ts"
```

`tsx` is already a devDependency — no new packages required. `tsx watch` restarts the script on any imported file change, which includes the JSON token files read via `readFile` in `generate.ts`.

**Root script addition** (`package.json`):

```json
"watch:css": "turbo run dev --filter=@boreal-ds/style-guidelines"
```

This gives developers a focused alias for token hot-reload without starting the full dev pipeline.

**Verification:**

```bash
pnpm watch:css
# → tsx starts watching
# Edit src/tokens/theme/proximus.json (e.g. change a color value)
# → generator re-runs automatically
# → dist/css/theme-proximus.css updates with new value
```

**Pre-conditions before implementing:**

- Confirm `tsx watch` detects changes to `.json` files read via Node's `fs/promises.readFile` (not statically imported — needs a quick smoke test)
- If `readFile` changes are not detected, use `tsx watch --ignore '**/*.css' src/generators/generate.ts` with `chokidar` wrapping the entry point instead

---

### Future Stage: Connect `@boreal-ds/style-guidelines` to consumers (full hot-reload pipeline)

**Context:** `apps/boreal-docs/src/.storybook/preview.ts` line 12–13 contains an explicit TODO:

```ts
//TODO: Replace next line with Boreal design tokens when available and remove `tokens-fallback.css` file
import "@/styles/tokens-fallback.css";
```

This confirms that consuming `@boreal-ds/style-guidelines` as a workspace package is the planned path — not a path alias or direct file import. `react-testapp` will follow the same pattern when it integrates real tokens.

**Why workspace:\* is the only correct approach:**

- The package has `publishConfig`, `exports`, and `files` — it is designed to be published to npm
- `workspace:*` gets replaced with a real version on `pnpm publish` / `changeset publish`
- Direct path imports break for any consumer outside the monorepo

**Step 1 — Declare workspace dependency in each consumer**

`apps/boreal-docs/package.json`:

```json
"dependencies": {
  "@boreal-ds/style-guidelines": "workspace:*"
}
```

`examples/react-testapp/package.json` (when ready):

```json
"dependencies": {
  "@boreal-ds/style-guidelines": "workspace:*"
}
```

Run `pnpm install` after each addition to create the workspace symlink.

**Step 2 — Replace the TODO in `preview.ts`**

```ts
// Remove:
import "@/styles/tokens-fallback.css";

// Add:
import "@boreal-ds/style-guidelines/css/global";
import "@boreal-ds/style-guidelines/css/theme-telesign";
// (add other themes as toolbar items are added)
```

**Step 3 — Configure Vite to watch the symlinked dist files**

Vite ignores `node_modules` file changes by default — including workspace symlinks. One override in `.storybook/main.ts` opts in:

```ts
viteFinal: async (config) => ({
  ...config,
  server: {
    watch: {
      ignored: ['!**/node_modules/@boreal-ds/style-guidelines/dist/**'],
    },
  },
}),
```

Apply the same override in `react-testapp/vite.config.ts` when the time comes.

**Step 4 — Run the full pipeline**

```bash
pnpm dev
# Turborepo starts all persistent dev tasks concurrently:
# → boreal-styleguidelines: tsx watch (regenerates dist/ on token JSON change)
# → boreal-docs: storybook dev (Vite HMR picks up dist/ changes via Step 3 config)
# → react-testapp: vite dev (same, when configured)
```

**Pre-conditions before implementing:**

- The `tsx watch` future stage above must be completed first (generator must be persistent)
- `boreal-styleguidelines` build must be stable and generating correct output
- `tokens-fallback.css` can be deleted once the real tokens are verified in Storybook

---

## Out of Scope

### `scripts-boreal/` directory — ✅ now integrated

Originally out of scope (`chore/create-local-pack` branch). Merged to `release/current` and fully migrated on `feature/EOA-10230_implement_deployment_publishing_DG`:

- `npm` → `pnpm` throughout (`cmd.js`, `install.js`, `publish.js`)
- `testWebComponents()` and `buildWebComponent()` deleted (Turborepo handles these in CI)
- `--ci` flag added — runs `pnpm build` on `react-testapp` instead of `pnpm dev`
- Registered in `pnpm-workspace.yaml`
- `validate:pack` script added to root `package.json`
- 27/27 unit tests passing

**Role:** Pre-publish gate — runs between `pnpm version-packages` and `pnpm release` in CD Job 5d. Packs real `.tgz` artifacts, installs them into `react-testapp` replacing workspace symlinks, and builds. If it fails, the publish is aborted. See `.ai/guidelines/scripts-boreal.md`.

### Future packages referenced in `scripts-boreal/lib/conf.js`

`conf.js` references `packages/boreal-angular`, `examples/app-vue-vite`, and `examples/app-angular` — **none of these exist yet**. The `pnpm-workspace.yaml` glob patterns (`packages/*`, `examples/*`) will pick them up automatically when created. No plan changes needed.

---

## Risks & Gotchas

| Risk                                                                                                  | Mitigation                                                                                                                                                                                                  |
| ----------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `boreal-vue` test script exits code 1 — Turborepo `pnpm test` fails                                   | Fixed in Phase 5: change to `"test": "echo 'No tests configured'"`                                                                                                                                          |
| lint-staged appends file paths to `pnpm --filter` commands                                            | Fixed by using `() => 'command'` function pattern in `.lintstagedrc.js`                                                                                                                                     |
| ESLint `projectService: true` fails when invoked from repo root                                       | Fixed by using package scripts (not per-file ESLint calls) in lint-staged                                                                                                                                   |
| Commit message validation now covers ALL packages (team habit change)                                 | Communicate to team before merging — scope and ticket format are now required                                                                                                                               |
| `scope-enum` enforcement — all commits must use a declared scope                                      | Scopes: `react`, `vue`, `web-components`, `styles`, `docs`, `examples`, `scripts`, `workspace`, `ci`, `deps`, `release`, `multiple`. Add new scopes to `commitlint.config.js` when new packages are created |
| `ticket-format` rule — subjects must start with `EOA-1234 desc` or `* desc`                           | Non-ticket changes must use `* ` prefix (e.g., `chore(deps): * bump turbo`)                                                                                                                                 |
| `commitlint.config.js` depends on `commitlint-custom-rules.js` at the same path                       | Both files must exist at the repo root — deleting one breaks the other                                                                                                                                      |
| Both commitlint files use `export default` — only works with correct module format                    | ✅ Resolved: `"type": "module"` was added to root `package.json`. All root configs (`.lintstagedrc.js`, `commitlint.config.js`, `commitlint-custom-rules.js`) use `export default` and are ESM-compatible.  |
| Stencil output targets write to `../boreal-react/lib/` — must build `web-components` first            | Handled automatically by `"dependsOn": ["^build"]` in `turbo.json`                                                                                                                                          |
| `packages/boreal-react/lib/` is in `.gitignore` — generated proxies not tracked                       | Correct and intentional; Turborepo + workspace link ensures they are generated before wrappers build                                                                                                        |
| No CI/CD exists yet                                                                                   | When adding CI, use `pnpm install --frozen-lockfile` + `pnpm build` + `pnpm test` + `pnpm lint`                                                                                                             |
| `boreal-styleguidelines` `dev` exits immediately — misaligned with `persistent: true` in `turbo.json` | Turbo won't crash (it marks the task complete), but the semantic is wrong. Tracked in **Future Stage: style-guidelines watch mode**                                                                         |

---

## Rollback Strategy

```bash
# 1. Remove root-level artifacts
rm /package.json /pnpm-workspace.yaml /turbo.json /.lintstagedrc.js /commitlint.config.js /commitlint-custom-rules.js
rm -rf /.husky /node_modules

# 2. Restore package-level config
cp .backup-hooks/package.json packages/boreal-web-components/package.json
cp -r .backup-hooks/.husky packages/boreal-web-components/
cp .backup-hooks/.lintstagedrc.json packages/boreal-web-components/
cp .backup-hooks/commitlint.config.ts packages/boreal-web-components/

# 3. Restore file: references in wrappers manually
# (boreal-react and boreal-vue package.json)

# 4. Reinstall at package level
cd packages/boreal-web-components && npm install
```
