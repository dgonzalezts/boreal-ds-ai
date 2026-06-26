# EOA-9606: Root-Level Hooks & Release Automation

**Branch:** `feature/EOA-9606_wc_baseline_config_p2_DG`
**Plans implemented:**
- `.ai/plans/root-level-hooks-migration.md`
- `.ai/plans/automated-changelog-&-release.md`

---

## What This Branch Delivers

### Root-Level Git Hooks (Plan 1)

Git hooks were previously scoped to `packages/boreal-web-components/.husky/`, which caused web-component-specific lint rules to fire on commits to unrelated packages (e.g. `apps/boreal-docs/`). This branch centralizes all hooks at the repo root.

**Files added / changed:**

| File | Description |
|------|-------------|
| `package.json` (root) | Added `prepare: husky` script + devDeps: `husky`, `commitlint`, `lint-staged`, `commitizen` |
| `commitlint.config.js` | Extends `@commitlint/config-conventional`; enforces ticket format (`EOA-XXXX` or `*` prefix) in all commit subjects; scope required at error level |
| `commitlint-custom-rules.js` | Custom rules with descriptive error messages for `type-required`, `scope-required`, `subject-required`, `ticket-format` |
| `.lintstagedrc.js` | Scoped to `boreal-web-components/src/**` and `apps/boreal-docs/**` using `pnpm --filter`; wrapper packages (react, vue, styleguidelines) intentionally excluded |
| `.husky/pre-commit` | Runs `pnpm lint-staged` |
| `.husky/commit-msg` | Runs `pnpm commitlint --edit "$1"` |
| `.husky/pre-push` | Runs `pnpm turbo run test --filter=@telesign/boreal-web-components` (enhancement beyond plan spec) |

**Git configuration:**
```
core.hooksPath = .husky/_
```

**Packages cleaned up** — `husky`, `commitlint`, and `lint-staged` removed from `packages/boreal-web-components/package.json` (no longer duplicated at package level).

---

### Automated Changelog & Release (Plan 2)

Changesets replaced with `release-it` + `@release-it/conventional-changelog`. Each publishable package has its own `.release-it.json` config.

**Files added / changed:**

| File | Description |
|------|-------------|
| `.changeset/` | **Deleted** — fully replaced by release-it |
| `packages/boreal-web-components/.release-it.json` | WC release config with CEM hook, `alpha` npm tag, `requireBranch: release/current` |
| `packages/boreal-react/.release-it.json` | React release config; `before:init` uses `--filter=@telesign/boreal-react...` to build deps first |
| `packages/boreal-vue/.release-it.json` | Vue release config; mirrors React pattern |
| `packages/boreal-styleguidelines/.release-it.json` | Style guidelines release config |
| `packages/boreal-web-components/CHANGELOG.md` | Initial stub |
| `packages/boreal-react/CHANGELOG.md` | Initial stub |
| `packages/boreal-vue/CHANGELOG.md` | Initial stub |
| `packages/boreal-web-components/stencil.config.ts` | Added `docs-custom-elements-manifest` output target → generates `custom-elements.json` |
| `turbo.json` | Added `custom-elements.json` to build task `outputs` |
| `packages/boreal-web-components/scripts/check-cem-changes.ts` | Compares published CEM (fetched from unpkg) against local build; reports breaking changes and new features |

**Root `package.json` release scripts:**
```json
"release:styles": "pnpm --filter @telesign/boreal-style-guidelines run release",
"release:wc":     "pnpm --filter @telesign/boreal-web-components run release",
"release:react":  "pnpm --filter @telesign/boreal-react run release",
"release:vue":    "pnpm --filter @telesign/boreal-vue run release",
"release:all":    "pnpm run release:styles && pnpm run release:wc && pnpm run release:react && pnpm run release:vue"
```

**Release order** (dependency-safe):
1. `style-guidelines` — no workspace deps
2. `web-components` — no workspace deps
3. `react` — depends on web-components
4. `vue` — depends on web-components

---

## Notable Enhancements Beyond Plan Spec

| Enhancement | Detail |
|-------------|--------|
| Pre-push hook | Runs turbo tests for `boreal-web-components` before any push — extra safety gate not in original plan |
| TypeScript CEM script | Implemented as `.ts` (via `tsx`) instead of the plan's `.mjs` — more consistent with codebase tooling |
| Stricter scope enforcement | `scope-enum` is level 2 (error) rather than the plan's suggested level 1 (warning) |
| `npm.tag: "alpha"` | Added to all release configs — publishes to `alpha` dist-tag on npm for pre-release safety |

---

## Commit Message Format

All commits must follow:
```
type(scope): EOA-XXXX description
```

Or for non-ticket commits (e.g. release automation):
```
type(scope): * description
```

**Valid types:** `feat`, `fix`, `test`, `chore`, `docs`, `build`, `ci`, `refactor`, `revert`, `style`, `perf`

**Valid scopes:** `react`, `vue`, `web-components`, `styles`, `docs`, `examples`, `scripts`, `workspace`, `ci`, `deps`, `release`, `multiple`

Use `pnpm commit` for an interactive prompt.

---

## Running a Release (Dry Run)

```bash
# From repo root — dry run won't publish, tag, or write files
pnpm run release:wc -- --dry-run
```

Expected sequence: `before:init` builds WC + runs CEM check → version prompt → changelog preview → exits without side effects.

---

## Pre-Merge Verification Checklist

```bash
# 1. Confirm no engine warnings
fnm use && pnpm install

# 2. Confirm commitlint blocks invalid messages
git commit --allow-empty -m "bad message"

# 3. Confirm commitlint passes valid messages
git commit --allow-empty -m "feat(workspace): EOA-0000 test"

# 4. Confirm WC release dry run completes without errors
pnpm run release:wc -- --dry-run
```
