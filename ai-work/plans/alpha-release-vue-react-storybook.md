---
status: in progress
---

# Alpha Release — Vue First Publish, React Re-publish, Storybook Deploy

**Branch required:** `release/current` (current branch ✅)
**Date:** 2026-03-16

---

## Context

The `boreal-vue` package was recently added to the monorepo and has never been published. It sits at version `0.0.1` with no git tag. The `boreal-react` package was last published at `0.1.0-alpha.2` and has one new commit since then (`feat(react): add README`). Storybook deployment to Chromatic is set up per the completed plan in `.ai/plans/storybook-chromatic-deployment.md` and needs to be triggered.

`boreal-web-components` also has unreleased changes since its last tag (`0.1.0-alpha.0`): the scaffold component was removed and a README was added. Publishing it first ensures vue and react tarballs pin a version of web-components that reflects the current codebase state.

---

## Does release-it auto-detect changes?

**No.** `release-it` always releases when you run it. The `@release-it/conventional-changelog` plugin reads commits since the last git tag to:

1. Infer the version bump type (patch / minor / major)
2. Populate `CHANGELOG.md`

But it does **not** skip or gate the release if there are no new commits. With `"preRelease": "alpha"` configured in every `.release-it.json`, running any `pnpm release:X` script always produces the next `-alpha.N` version — it is entirely your responsibility to decide which packages warrant a new publish.

**Vue is the exception**: it has no previous git tag, so `@release-it/conventional-changelog` would scan all commits, find `BREAKING CHANGE` footers from scaffolding history, and inflate the bump to major. The `--increment=minor` override is required. This flag cannot be forwarded through nested pnpm calls, so vue must be released directly from inside its package directory.

---

## Current State Summary

| Package                             | Last tag             | Package.json version | Changes since tag                                  |
|-------------------------------------|----------------------|----------------------|----------------------------------------------------|
| `@telesign/boreal-style-guidelines` | `0.1.0-alpha.0` ✅   | unknown              | None visible in git log — no release needed        |
| `@telesign/boreal-web-components`   | `0.1.0-alpha.0` ✅   | `0.1.0-alpha.0`      | 2 commits (scaffold removed, README added) + teammate's pending PR |
| `@telesign/boreal-react`            | `0.1.0-alpha.2` ✅   | `0.1.0-alpha.2`      | 1 commit (README added)                            |
| `@telesign/boreal-vue`              | ❌ none               | `0.0.1`              | All commits — first release                        |

---

## Release Sequence

### Step 1 — Pre-conditions ✅ DONE

> **Wait for teammate's WC changes to merge first.** A teammate has pending changes scoped to `boreal-web-components`. Wait for their PR to land on `release/current` before releasing that package — this folds all changes into a single `0.1.0-alpha.1` rather than burning an extra alpha counter. Vue and react are not blocked in the meantime. If the PR takes more than a day or two, proceed without it; their changes can land in `0.1.0-alpha.2` later.
>
> **When the teammate merges:** run `git pull origin release/current` to sync, then proceed to Step 2.

```bash
fnm use
npm whoami                          # must show your npm username
npm access list packages @telesign  # must show publish access
git pull origin release/current     # sync latest (including teammate's merged WC changes)
git status                          # must show: nothing to commit, working tree clean
```

No stash is needed — the `.release-it.json` changes that previously required stashing were already committed in `117db08`.

---

### Step 2 — Release `@telesign/boreal-web-components`

This is a **subsequent release** — a tag exists, so the simplified workflow applies from the workspace root.

```bash
pnpm release:wc
```

- release-it reads commits since `@telesign/boreal-web-components@0.1.0-alpha.0`
- Conventional commits: `feat` (README) + `refactor` (scaffold removal) + teammate's commits
- Expected version prompt: `0.1.0-alpha.1`
- The `before:init` hook runs `turbo run build --filter=@telesign/boreal-web-components` and `tsx scripts/check-cem-changes.ts` — **review the CEM report before confirming**

Verify:
```bash
npm dist-tag ls @telesign/boreal-web-components
# → alpha: 0.1.0-alpha.1
```

---

### Step 3 — Validate react artifact (pre-publish gate)

```bash
pnpm validate:pack:react
```

Expected: `✅ Pipeline completed successfully — artifact validation passed`

**Stop here if this fails.**

---

### Step 4 — Release `@telesign/boreal-react`

Subsequent release — run from workspace root:

```bash
pnpm release:react
```

- release-it reads commits since `@telesign/boreal-react@0.1.0-alpha.2`
- 1 conventional commit: `feat(react): add README`
- Expected version prompt: `0.1.0-alpha.3`
- `pnpm` replaces `"workspace:*"` with the exact published web-components version (`0.1.0-alpha.1`) in the tarball

Verify:
```bash
npm dist-tag ls @telesign/boreal-react
# → alpha: 0.1.0-alpha.3
```

---

### Step 5 — Validate vue artifact (pre-publish gate)

```bash
pnpm validate:pack:vue
```

Expected: `✅ Pipeline completed successfully — artifact validation passed`

**Stop here if this fails.**

---

### Step 6 — Release `@telesign/boreal-vue` (FIRST RELEASE)

Must be run from inside the package directory — `--increment=minor` cannot be forwarded through root pnpm scripts:

```bash
cd packages/boreal-vue
eval "$(fnm env)" && npx release-it --increment=minor
```

- No previous tag → `--increment=minor` overrides the inflated major bump
- Expected version prompt: `0.1.0-alpha.0`
- The `before:init` hook runs `turbo run build --filter=@telesign/boreal-vue...`
- `pnpm` replaces `"workspace:*"` with the exact published web-components version (`0.1.0-alpha.1`) in the tarball
- npm will set both `latest` and `alpha` to `0.1.0-alpha.0` on first publish — this is expected (see key concepts in `first-alpha-release.md`)

```bash
cd ../..   # return to workspace root
```

Verify:
```bash
npm dist-tag ls @telesign/boreal-vue
# → alpha: 0.1.0-alpha.0
# → latest: 0.1.0-alpha.0  (expected on first publish)
```

---

### Step 7 — Deploy Storybook to Chromatic

```bash
pnpm deploy:docs
```

This runs `turbo run build --filter=@telesign/boreal-docs...` then `chromatic --exit-zero-on-changes --storybook-build-dir=storybook-static`.

Requires the `CHROMATIC_PROJECT_TOKEN` environment variable to be set:

```bash
# Either export it in your shell, or use a .env file with dotenv-cli
export CHROMATIC_PROJECT_TOKEN=<your-token>
pnpm deploy:docs
```

Expected: Chromatic CLI prints the published Storybook URL.

---

## Push-conflict recovery (if teammate merges while you are mid-release)

If `git push` fails with "non-fast-forward" after release-it has already published to npm:

```bash
# DO NOT re-run release-it — the npm publish already succeeded
git pull --rebase origin release/current
git push origin release/current
```

The rebase is safe — the release commit only touches `package.json` and `CHANGELOG.md`.

---

## Post-release Verification

```bash
npm view @telesign/boreal-web-components dist-tags
npm view @telesign/boreal-react dist-tags
npm view @telesign/boreal-vue dist-tags
```

Consumer smoke test (outside monorepo):
```bash
mkdir /tmp/vue-alpha-test && cd /tmp/vue-alpha-test
npm install @telesign/boreal-vue@alpha
# must install without error
```

---

## Critical Files

| File | Role |
|------|------|
| `packages/boreal-vue/.release-it.json` | Vue release config (`tag: alpha`, `preRelease: alpha`, `publishPackageManager: pnpm`) |
| `packages/boreal-react/.release-it.json` | React release config |
| `packages/boreal-web-components/.release-it.json` | WC release config (CEM check hook) |
| `package.json` (root) | `release:wc`, `release:react`, `release:vue`, `validate:pack:*`, `deploy:docs` scripts |
| `.ai/plans/first-alpha-release.md` | Canonical release runbook with key concepts |
| `.ai/plans/storybook-chromatic-deployment.md` | Chromatic setup (status: done) |
