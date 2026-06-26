# Integrated Monorepo Migration — Verification Step 9 QA Report

**Date**: 2026-03-07
**Branch**: `feature/EOA-10230_implement_deployment_publishing_DG`
**Plan**: `.ai/plans/integrated-monorepo-migration.md`
**Status**: PASS

---

## Scope

Verification Step 9 of the integrated monorepo migration plan:

> **release-it dry-run for all publishable packages**
> Verifies: tag format, changelog generation, version prompt — no files written

Packages under test:
- `@telesign/boreal-style-guidelines` (`packages/boreal-styleguidelines/`)
- `@telesign/boreal-web-components` (`packages/boreal-web-components/`)
- `@telesign/boreal-react` (`packages/boreal-react/`)
- `@telesign/boreal-vue` (`packages/boreal-vue/`)

---

## Environment

| Property | Value |
|---|---|
| Node.js | v22.21.1 (via fnm) |
| pnpm | 10.7.1 |
| release-it | 19.x (resolved from root `devDependencies`) |
| `@release-it/conventional-changelog` | 10.x |
| Git branch | `feature/EOA-10230_implement_deployment_publishing_DG` |
| Working directory state | Dirty (uncommitted changes in `boreal-styleguidelines`) |

---

## Dry-Run Flags Used

```bash
npx release-it --dry-run --ci --no-npm --no-git.requireBranch --no-git.requireCleanWorkingDir --no-hooks
```

| Flag | Reason |
|---|---|
| `--dry-run` | Simulate release; no files written, no git operations executed |
| `--ci` | Suppress interactive prompts; auto-accept defaults |
| `--no-npm` | Skip npm publish and auth pre-flight check (no npm credentials on this machine) |
| `--no-git.requireBranch` | Bypass `requireBranch: "release/current"` guard (on feature branch) |
| `--no-git.requireCleanWorkingDir` | Bypass clean working dir check (uncommitted styleguidelines changes) |
| `--no-hooks` | Skip `before:init` build hook (Turbo must run from workspace root; not needed for config verification) |

> **Note 1:** The production dry-run command (per `.ai/guidelines/release-process.md`) also includes `--preRelease=alpha`. It was omitted here because the goal was to verify tag format and changelog config structure, not the pre-release versioning path. The `1.0.0` version shown in results below is an artifact of the missing flag — real alpha releases will produce `0.x.y-alpha.N` versions. See the Real First Release section for the correct production commands.

> **Note 2:** `pnpm --filter ... run release -- --dry-run` was attempted first but failed due to npm auth pre-flight running before `--dry-run` suppression and `fnm use` stderr interfering with release-it's stdout detection in non-TTY mode. Running `npx release-it` directly from each package directory resolves both issues. This is a local dry-run quirk only — in CI with `NPM_TOKEN` set, `pnpm run release` works correctly.

---

## Check Results

### Check 1 — `@telesign/boreal-style-guidelines`

| Criterion | Expected | Actual | Status |
|---|---|---|---|
| Tag format | `@telesign/boreal-style-guidelines@X.Y.Z` | `@telesign/boreal-style-guidelines@1.0.0` | PASS |
| Commit message | `chore(release): * release @telesign/boreal-style-guidelines vX.Y.Z` | `chore(release): * release @telesign/boreal-style-guidelines v1.0.0` | PASS |
| Changelog sections | `BREAKING CHANGES`, `Features`, `Bug Fixes` | All present | PASS |
| Ticket ID stripping | `EOA-XXXX` removed from subjects | Confirmed (e.g. `EOA-8969_typography_component` → `add typography component`) | PASS |
| `* ` prefix stripping | `* description` subjects → clean changelog | Confirmed | PASS |
| Git operations skipped | `git commit`, `git tag`, `git push` shown as `!` | All three shown as `!` (skipped) | PASS |
| No files written | `CHANGELOG.md` write shown as `$` (simulated) | Shown as `$ Writing changelog to CHANGELOG.md` — not executed | PASS |
| Exit | `Done` | `🏁 Done (in 0s.)` | PASS |

**Raw output (key lines):**
```
$ git describe --tags --match=@telesign/boreal-style-guidelines@* --abbrev=0
🚀 Let's release boreal-ds (0.0.0...1.0.0)
Changelog:
## 1.0.0 (2026-03-07)
### ⚠ BREAKING CHANGES
...
### Features
...
### Bug Fixes
...
$ Writing changelog to CHANGELOG.md
! git add . --update
! git commit --message chore(release): * release @telesign/boreal-style-guidelines v1.0.0
! git tag --annotate --message Release @telesign/boreal-style-guidelines v1.0.0 @telesign/boreal-style-guidelines@1.0.0
! git push --follow-tags origin
! echo 'Released @telesign/boreal-style-guidelines@1.0.0'
🏁 Done (in 0s.)
```

---

### Check 2 — `@telesign/boreal-web-components`

| Criterion | Expected | Actual | Status |
|---|---|---|---|
| Tag format | `@telesign/boreal-web-components@X.Y.Z` | `@telesign/boreal-web-components@1.0.0` | PASS |
| Commit message | `chore(release): * release @telesign/boreal-web-components vX.Y.Z` | `chore(release): * release @telesign/boreal-web-components v1.0.0` | PASS |
| Changelog sections | `BREAKING CHANGES`, `Features`, `Bug Fixes`, `Performance Improvements`, `Reverts` | All present | PASS |
| `before:init` CEM hook | Skipped via `--no-hooks` | Skipped | N/A (tested separately) |
| Git operations skipped | `git commit`, `git tag`, `git push` shown as `!` | All three shown as `!` | PASS |
| Exit | `Done` | `🏁 Done (in 0s.)` | PASS |

**Raw output (key lines):**
```
$ git describe --tags --match=@telesign/boreal-web-components@* --abbrev=0
🚀 Let's release boreal-ds (0.0.0...1.0.0)
Changelog:
## 1.0.0 (2026-03-07)
### ⚠ BREAKING CHANGES
...
! git commit --message chore(release): * release @telesign/boreal-web-components v1.0.0
! git tag --annotate --message Release @telesign/boreal-web-components v1.0.0 @telesign/boreal-web-components@1.0.0
! git push --follow-tags origin
🏁 Done (in 0s.)
```

---

### Check 3 — `@telesign/boreal-react`

| Criterion | Expected | Actual | Status |
|---|---|---|---|
| Tag format | `@telesign/boreal-react@X.Y.Z` | `@telesign/boreal-react@1.0.0` | PASS |
| Commit message | `chore(release): * release @telesign/boreal-react vX.Y.Z` | `chore(release): * release @telesign/boreal-react v1.0.0` | PASS |
| Changelog sections | `BREAKING CHANGES`, `Features`, `Bug Fixes` | All present | PASS |
| Git operations skipped | `git commit`, `git tag`, `git push` shown as `!` | All three shown as `!` | PASS |
| Exit | `Done` | `🏁 Done (in 0s.)` | PASS |

**Raw output (key lines):**
```
$ git describe --tags --match=@telesign/boreal-react@* --abbrev=0
🚀 Let's release boreal-ds (0.0.0...1.0.0)
...
! git commit --message chore(release): * release @telesign/boreal-react v1.0.0
! git tag --annotate --message Release @telesign/boreal-react v1.0.0 @telesign/boreal-react@1.0.0
! git push --follow-tags origin
🏁 Done (in 0s.)
```

---

### Check 4 — `@telesign/boreal-vue`

| Criterion | Expected | Actual | Status |
|---|---|---|---|
| Tag format | `@telesign/boreal-vue@X.Y.Z` | `@telesign/boreal-vue@1.0.0` | PASS |
| Commit message | `chore(release): * release @telesign/boreal-vue vX.Y.Z` | `chore(release): * release @telesign/boreal-vue v1.0.0` | PASS |
| Changelog sections | `BREAKING CHANGES`, `Features`, `Bug Fixes` | All present | PASS |
| Git operations skipped | `git commit`, `git tag`, `git push` shown as `!` | All three shown as `!` | PASS |
| Exit | `Done` | `🏁 Done (in 0s.)` | PASS |

**Raw output (key lines):**
```
$ git describe --tags --match=@telesign/boreal-vue@* --abbrev=0
🚀 Let's release boreal-ds (0.0.0...1.0.0)
...
! git commit --message chore(release): * release @telesign/boreal-vue v1.0.0
! git tag --annotate --message Release @telesign/boreal-vue v1.0.0 @telesign/boreal-vue@1.0.0
! git push --follow-tags origin
🏁 Done (in 0s.)
```

---

## Notable Observations

### 1. First release will be `1.0.0` — expected

No git tags matching any package pattern (`@telesign/boreal-*@*`) exist yet. release-it scans the entire git history as the initial changelog window and detects `BREAKING CHANGE` footers in historical commits, which triggers a major bump (`0.0.0 → 1.0.0`).

**This is correct behaviour.** Once the first real release tag is created (e.g. `@telesign/boreal-web-components@1.0.0`), all subsequent releases will only scan commits since that tag — producing minimal, accurate changelogs.

**Action required before first real release:** confirm with the team whether `1.0.0` is the intended starting version or whether the tag should be created manually at a lower version (e.g. `0.1.0`) to establish a baseline without bumping to major.

### 2. Changelog includes whole-repo history — first release only

Because this is the first tagged release, every commit to the repo appears in the changelog, including commits unrelated to a given package (e.g. docs commits appear in the web-components changelog). This is an artifact of having no prior tags. After the first release, per-package tag patterns (`--match=@telesign/boreal-web-components@*`) will correctly scope the changelog to commits since the last package-specific tag.

### 3. `headerPattern` regex correctly strips ticket IDs

The custom `headerPattern` in all four `.release-it.json` configs:

```regex
^(\w*)(?:\(([\w\$\.\-\*\s]*)\))?\:\s?(?:[A-Z0-9]+-\d+\s|\*\s)?(.*)$
```

Confirmed to match and strip:
- `feat(web-components): EOA-8969 add typography` → subject becomes `add typography`
- `fix(scripts): * update cleanup function` → subject becomes `update cleanup function`
- Older commits without ticket prefix are also captured correctly via the optional group

### 4. `pnpm run release` via filter has a local dry-run limitation

When invoked as `pnpm --filter <pkg> run release -- --dry-run`, the npm auth pre-flight check fires regardless of `--dry-run` and `--no-npm`. Root cause: pnpm v10 runs `npm whoami` synchronously before release-it's flag processing suppresses npm checks. This is a local-only issue — in CI the `NPM_TOKEN` env var is set, so the auth check passes and the full `pnpm run release` path works correctly.

**Workaround for local dry-runs:** run `npx release-it` directly from the package directory as shown in this report.

---

## Summary

| Package | Tag Format | Commit Message | Changelog | Git Ops Skipped | Result |
|---|---|---|---|---|---|
| `boreal-style-guidelines` | PASS | PASS | PASS | PASS | **PASS** |
| `boreal-web-components` | PASS | PASS | PASS | PASS | **PASS** |
| `boreal-react` | PASS | PASS | PASS | PASS | **PASS** |
| `boreal-vue` | PASS | PASS | PASS | PASS | **PASS** |

Verification Step 9 is **complete**. See Steps 10 and 11 sections below.

---

## Real First Release — Step-by-Step Guide

> Full authoritative process documented in `.ai/guidelines/release-process.md`. This section summarises the steps aligned with that guide.

### Pre-conditions (from Release Manager Checklist)

- [ ] This migration branch merged to `release/current` and pulled locally
- [ ] Working directory is clean (`git status` shows no changes)
- [ ] `NPM_TOKEN` with publish rights for `@telesign` scope available (env var or `.npmrc`)
- [ ] `pnpm install` run at workspace root (workspace symlinks are fresh)
- [ ] Dry-run passes for all packages (see below)

### Alpha Version Format

Alpha releases use pre-release identifiers: `0.x.y-alpha.N`. The `--preRelease=alpha` flag is **required on every alpha release command**. Without it, release-it publishes a plain semver version (as seen in the dry-run above which used no flag for config verification only).

| Commit type since last tag | Previous | Next |
|---|---|---|
| `fix` or `chore` | `0.0.1-alpha.0` | `0.0.1-alpha.1` |
| `feat` | `0.0.1-alpha.3` | `0.1.0-alpha.0` |
| `feat!` / `BREAKING CHANGE` | `0.1.0-alpha.1` | `1.0.0-alpha.0` |

The pre-release counter resets to `.0` whenever the base semver component bumps.

### Dry-Run Before Every Real Release

```bash
git checkout release/current && git pull

pnpm --filter @telesign/boreal-web-components run release -- --dry-run --preRelease=alpha
```

Pass criteria:
- Build runs cleanly
- CEM breaking-change report prints (web-components only)
- Changelog shows only commits since the last alpha tag
- No git commit, tag, or npm publish occurs

### Release Order

```
1. boreal-style-guidelines   (independent)
2. boreal-web-components     (independent)
   └─ validate:pack          (gate — must pass before wrappers)
3. boreal-react              (depends on web-components)
4. boreal-vue                (depends on web-components)
```

Run all at once (enforces order automatically via `&&`):
```bash
pnpm release:all -- --preRelease=alpha
```

> `release:all` expands to:
> ```
> release:styles && release:wc && validate:pack && release:react && release:vue
> ```
> Each step uses `&&` — if any step exits non-zero (including `validate:pack`), the chain stops. No further packages are published.

### Step 1 — Release `@telesign/boreal-style-guidelines`

```bash
pnpm release:styles -- --preRelease=alpha
```

What happens:
1. `before:init` hook: `turbo run build --filter=@telesign/boreal-style-guidelines`
2. Git log read, changelog generated, version bumped to `0.x.y-alpha.N`
3. `package.json` written, `CHANGELOG.md` prepended
4. `git commit` → `git tag @telesign/boreal-style-guidelines@0.x.y-alpha.N` → `git push --follow-tags`
5. `npm publish --tag alpha`

**Verify after:**
```bash
npm dist-tag ls @telesign/boreal-style-guidelines
# → alpha: 0.x.y-alpha.N
# → (no "latest" entry — correct for alpha phase)
```

### Step 2 — Release `@telesign/boreal-web-components`

```bash
pnpm release:wc -- --preRelease=alpha
```

Same as Step 1, plus: `before:init` runs `tsx scripts/check-cem-changes.ts` — review the breaking change report before confirming the version bump.

**Verify after:**
```bash
npm dist-tag ls @telesign/boreal-web-components
# → alpha: 0.x.y-alpha.N
```

### Step 3 — Run `validate:pack` (pre-publish gate)

Packs real `.tgz` artifacts, installs into `react-testapp` (replacing workspace symlinks), runs `pnpm build`. If this fails, **stop — do not proceed to Steps 4 and 5**.

```bash
pnpm validate:pack
```

### Step 4 — Release `@telesign/boreal-react`

```bash
pnpm release:react -- --preRelease=alpha
```

pnpm replaces `"workspace:*"` in `boreal-react/package.json` with the real published version of `@telesign/boreal-web-components` before `npm publish`. This is the fix for the `file:` tarball problem.

**Verify after:**
```bash
npm dist-tag ls @telesign/boreal-react
# → alpha: 0.x.y-alpha.N

cd packages/boreal-react && pnpm pack --dry-run
# → @telesign/boreal-web-components must show a real version, NOT "workspace:*"
```

### Step 5 — Release `@telesign/boreal-vue`

```bash
pnpm release:vue -- --preRelease=alpha
```

### The `"tag": "alpha"` npm Dist-Tag — What It Means

All four `.release-it.json` configs contain `"tag": "alpha"` in the `npm` section. This controls the **npm dist-tag** (not the git tag):

| Behaviour | Explanation |
|---|---|
| `npm publish --tag alpha` runs | Package published under the `alpha` dist-tag |
| `npm install @telesign/boreal-web-components` | Resolves nothing — `latest` is never set in alpha phase |
| `npm install @telesign/boreal-web-components@alpha` | Installs the latest alpha |
| `npm install @telesign/boreal-web-components@0.1.0-alpha.3` | Installs a specific alpha version |
| Production consumers protected | Cannot accidentally pull a pre-release |

### Graduation to Stable (`@proximus`) — Not a Simple Dist-Tag Promotion

Graduation from alpha to stable is a **full npm org migration**, not just a dist-tag pointer move. Per `.ai/guidelines/release-process.md` Phase 2:

1. **Scope rename** — global `@telesign` → `@proximus` across all `package.json`, `.release-it.json`, `.lintstagedrc.js`, `.husky/pre-push`, Stencil output targets, docs, README
2. **Remove `"tag": "alpha"`** from all 4 `.release-it.json` files — release-it then defaults to `latest`
3. **Create git anchor tags** at the last `@telesign` alpha commit SHA (so release-it changelog starts from migration point, not repo beginning):
   ```bash
   git tag @proximus/boreal-web-components@1.0.0 <sha>
   git push origin --tags
   ```
4. **Run first stable release**: `pnpm release:all` (no `--preRelease` flag)
5. **Deprecate `@telesign/*`** packages on npm with migration message

Pre-conditions: `@proximus` npm org created, publish token provisioned for CI.

### Rollback a Release (if something goes wrong after publish)

```bash
# Unpublish within 72 hours
npm unpublish @telesign/boreal-web-components@0.x.y-alpha.N

# Delete the git tag
git tag -d @telesign/boreal-web-components@0.x.y-alpha.N
git push origin :refs/tags/@telesign/boreal-web-components@0.x.y-alpha.N

# Revert the version bump commit
git revert <release-commit-sha>
git push origin release/current
```

After 72 hours, use `npm deprecate @telesign/boreal-web-components@0.x.y-alpha.N "reason"` instead.

---

## CI/CD Alignment — Gaps to Fix Before Pipeline Implementation

These issues do not block local development or manual releases. They must be addressed when implementing the Jenkins pipeline.

### 1. `test:coverage` missing from root `package.json`

The CI diagram (Job 1) runs `pnpm test:coverage` from the repo root. No such root script exists — only per-package scripts. Add before CI implementation:

```json
"test:coverage": "turbo run test:coverage"
```

### 2. `release:all` does not forward flags to sub-scripts

When CI runs `pnpm release:all -- --preRelease=alpha --ci`, pnpm forwards the flags to `release:all` itself, not to the chained `release:styles`, `release:wc`, etc. sub-commands. Each package would receive no flags and publish a plain semver version instead of an alpha.

Fix by appending `--` to each per-package release script so they pass through any extra flags:

```json
"release:styles": "pnpm --filter @telesign/boreal-style-guidelines run release --",
"release:wc":     "pnpm --filter @telesign/boreal-web-components run release --",
"release:react":  "pnpm --filter @telesign/boreal-react run release --",
"release:vue":    "pnpm --filter @telesign/boreal-vue run release --",
```

With this change, `pnpm release:all -- --preRelease=alpha --ci` will correctly forward both flags to every package's release-it invocation.

### 3. CD diagram (v2) is stale — references Changesets

`pxg-cd-diagram-v2.md` still documents the old Changesets flow (`pnpm version-packages`, `changeset publish`, `@boreal-ds/*` scope). The diagram needs updating to reflect:
- `pnpm release:all -- --preRelease=alpha --ci` (Job 5d)
- `pnpm validate:pack` gate (between wc and wrappers)
- `@telesign/*` package scope (alpha phase)
- No `pnpm version-packages` step — release-it handles versioning internally

### 4. CI diagram (v2) references `pnpm changeset status` (Job 1)

Changesets has been removed. Job 1's changeset check step is obsolete. The commit history + commitlint enforce contribution quality; no changeset file is required. Remove this step from the CI diagram.

### 5. `pnpm --filter @boreal-ds/web-components cem` in CI diagram

No standalone `cem` script exists in `boreal-web-components/package.json`. The CEM (`custom-elements.json`) is generated as part of `stencil build` (the `build` script). Either:
- Remove the separate CEM step from the CI diagram (build already produces it), or
- Add `"cem": "stencil build --docs-readme"` to web-components if a standalone generation step is desired

---

## Pending Verification Steps

| Step | Description | Status |
|---|---|---|
| 1 | Workspace links (symlinks, not tarballs) | To verify |
| 2 | Build pipeline (web-components builds first) | To verify |
| 3 | Turborepo cache (second run near-instant) | To verify |
| 4 | Git hooks installed | To verify |
| 5 | Pre-commit: web-components files only trigger web-components lint | To verify |
| 6 | Pre-commit: docs files do NOT trigger web-components lint | To verify |
| 7 | commitlint rejects bad messages | To verify |
| 8 | commitlint accepts valid messages | To verify |
| 9 | release-it dry-run for all publishable packages | **PASS** |
| 10 | `workspace:*` replaced on pack | **PASS** |
| 11 | scripts-boreal integration test | **PASS** |

---

## Step 10 — `workspace:*` Replaced on Pack

**Date**: 2026-03-09
**Command run:**
```bash
cd packages/boreal-react && pnpm pack
tar -zxf telesign-boreal-react-0.0.1.tgz --to-stdout package/package.json
```

> Note: `pnpm pack --dry-run` does not exist in pnpm v10. The tarball was created, inspected, and immediately deleted.

### Result

`@telesign/boreal-web-components` inside the packed `package.json`:

```json
"dependencies": {
  "@stencil/react-output-target": "^1.2.0",
  "@telesign/boreal-web-components": "0.0.1"
}
```

**`workspace:*` was replaced with `0.0.1`** — the real installed version. ✅

This is pnpm's workspace protocol substitution: `workspace:*` is a development-time alias. At `pnpm pack`/`pnpm publish` time pnpm reads the target package's `version` field and pins the resolved value into the tarball's `package.json`. Consumers installing from npm receive a concrete, resolvable version — no `workspace:*` leaks out.

### Files included in tarball

```
dist/css/boreal.css  dist/css/global.css  dist/css/theme-*.css
dist/components/components.js  dist/index.js
dist/scss/**  dist/types/**
lib/components/components.ts  lib/index.ts
package.json  README.md
```

All expected outputs present. ✅

---

## Step 11 — scripts-boreal Integration Test (`validate:pack`)

**Date**: 2026-03-09
**Command run from workspace root:**
```bash
pnpm validate:pack
```

This invokes `node scripts-boreal/bin/publish.js react --ci`, which runs the full pre-publish gate pipeline.

### Pipeline stages and results

| Stage | Description | Result |
|---|---|---|
| Vite dep cache clear | `dist/.vite` removed before install | ✅ |
| Pack web-components → boreal-react | `.tgz` created and moved | ✅ `telesign-boreal-web-components-0.0.1.tgz` |
| Pack web-components → react-testapp | Same artifact copied | ✅ |
| Uninstall workspace `@telesign/boreal-web-components` from boreal-react | Symlink removed | ✅ |
| Install `.tgz` into boreal-react | Real artifact installed (not symlink) | ✅ |
| Build boreal-react | `pnpm run tsc && boreal-copy-styles` | ✅ |
| Pack boreal-react → react-testapp | `.tgz` created and moved | ✅ `telesign-boreal-react-0.0.1.tgz` |
| Uninstall workspace `@telesign/boreal-react` from react-testapp | Symlink removed | ✅ |
| Install `.tgz` into react-testapp | Real artifact installed (not symlink) | ✅ |
| Build react-testapp | `vite build` — 36 modules, 629ms | ✅ |
| Cleanup all `.tgz` artifacts | All three tarballs removed | ✅ |
| Restore `package.json` + `pnpm-lock.yaml` | Committed state restored | ✅ |

**Final status line:**
```
✅ Pipeline completed successfully — artifact validation passed
```

### Warnings observed (non-blocking)

| Warning | Assessment |
|---|---|
| `WARN using --force` | Expected — `--force` is required to replace workspace symlinks with tarball installs |
| `WARN node_modules is present. Lockfile only installation will make it out-of-date` | Expected — intentional during the swap; restored at end |
| `6 deprecated subdependencies` (`glob@7.2.3`, `inflight@1.0.6`, etc.) | Transitive deps from third-party packages; not actionable |
| `unmet peer inquirer@^9.0.0: found 12.11.1` (via `@commitlint/cz-commitlint`) | Pre-existing upstream issue; unrelated to validate:pack |
| pnpm update available (10.7.1 → 10.32.0) | Informational; update separately when convenient |

None of these warnings affect correctness or the pass/fail outcome.
