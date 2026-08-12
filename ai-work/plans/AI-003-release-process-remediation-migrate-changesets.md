---
ticket: AI-003
status: pending
created: 2026-08-12
---

# Release Process Remediation — Option B: Migrate to `changesets`

**Note:** `AI-003` is a placeholder ticket prefix — rename this file (and the `ticket:` field above) to the real Jira ticket ID once one is assigned. See the sibling plan `AI-003-release-process-remediation-patch-release-it.md` for the alternative (Option A: patch `release-it` in place) and `ai-docs/decisions/0013-release-tooling-release-it-vs-changesets.md` for the ADR comparing both.

---

## Context

A 2026-08-12 audit of the release process implemented by `EOA-9609-automated-changelog-&-rp.md`, `EOA-9609-first-alpha-release.md`, and `EOA-9609-alpha-release-vue-react-storybook.md` against the current state of `CHANGELOG.md`/`package.json` across all four packages (`boreal-styleguidelines`, `boreal-web-components`, `boreal-react`, `boreal-vue`) found five real defects:

1. **Squash merges break changelog/version generation.** Bitbucket Server squash commits (e.g. `d3bb6f51` "Pull request #166...", `fab67bea` "Pull request #159...") have subject lines that don't match the `headerPattern` any `.release-it.json` uses, so `@release-it/conventional-changelog` silently drops them. 19+ `feat`/`fix` commits for `bds-table` v3/v4 are invisible in every changelog and never counted toward version bumps.
2. **No per-package path scoping.** All four `.release-it.json` files scan the full git log since their own last tag with no path filter — why `boreal-web-components`, `boreal-react`, `boreal-vue` changelogs are byte-for-byte identical for shared entries.
3. **Version base (`0.1.0`) never escalates**, independent of merge strategy. `release-it`'s "continuation" logic (`semver.inc(latestVersion, 'prerelease', 'alpha')`) triggers once a version's prerelease id already matches the configured `preReleaseId`, and this **ignores** the bump level conventional-changelog recommends. This directly violates the team's own documented standard (`feat`→MINOR, `fix`→PATCH) — confirming this is a real defect, not a debatable trade-off.
4. **Every commit link in every CHANGELOG.md is broken.** `@release-it/conventional-changelog`'s built-in "Bitbucket" URL formatter assumes Bitbucket Cloud, not self-hosted Bitbucket Server (this repo's actual host), which uses a different path scheme (`/projects/<KEY>/repos/<slug>/commits/<hash>`). `package.json` `repository.url` is also inconsistent across packages, and `boreal-web-components`'s is still the literal leftover Stencil-starter placeholder.
5. **Wrapper dependency-pin drift.** Confirmed directly (`pnpm pack` + tarball inspection): `boreal-react`/`boreal-vue`'s `"@telesign/boreal-web-components": "workspace:*"` gets replaced with a hard-pinned exact version at publish time. If `boreal-web-components` releases and the wrappers don't (correct behavior once path-scoping/#2 is fixed, since they'd have no own commits), their published tarballs keep pointing at the stale pinned version indefinitely — nothing currently detects or fixes this.

Two suspected issues were ruled out: `boreal-styleguidelines`'s "staleness" (zero commits touched it since its last tag — no release due) and the `0.1.0-alpha.N` scheme's shape (a legitimate pre-1.0 convention; only its lack of graduation, #3, is broken).

This plan migrates from `release-it` to `changesets`, matching TurboRepo's own documented recommendation (https://turborepo.dev/en/docs/guides/publishing-libraries). Of the five defects, **four (#1, #2, #3, #5) become structurally not-applicable** rather than requiring a bespoke patch, because changesets works fundamentally differently: a human explicitly authors a small markdown file per change (`pnpm changeset add`) stating which package(s) changed and at what bump level — nothing is inferred from commit messages or git history. Confirmed directly in `changesets`' source: its `determineDependents` function automatically detects when `boreal-react`/`boreal-vue`'s `workspace:*` pin on `boreal-web-components` falls out of range and auto-includes them in the same release with a patch bump and a changelog entry — solving defect #5 natively. Only defect #4 (broken Bitbucket Server links) still needs a custom fix — changesets' default changelog generator and `@changesets/changelog-github` are both GitHub-specific.

Trade-off: this requires a genuine workflow shift (a changeset file per PR, ideally bot-enforced via CI, which doesn't exist yet — a similar discipline risk to Option A's squash-merge-title enforcement), and a full rewrite of the release configuration (retiring `.release-it.json`, the custom `headerPattern`, `@release-it/conventional-changelog`).

Confirmed decisions for this plan:
- Keep squash merges — enforcement shifts from "PR title regex" to "PR must include a changeset file."
- Rename `packages/boreal-styleguidelines` → `packages/boreal-style-guidelines` (same as Option A, unaffected by tooling choice).
- Alpha-graduation policy: stay in `-alpha.N` until real-world feedback addressed; graduate straight to `1.0.0` when ready, regardless of the internal alpha counter.
- Keep full auto-generated `CHANGELOG.md` for all four packages, including wrappers.

---

## Fixes

### B1 — ADR
Create ADR 0013 at `ai-docs/decisions/0013-release-tooling-release-it-vs-changesets.md` (already created — update its Status to `Accepted` and fill in Option B once this plan is executed).

### B2 — Install and configure changesets
Fetch latest versions (`https://registry.npmjs.org/@changesets/cli/latest`) before installing. Run `pnpm changeset init` at workspace root. Configure `.changeset/config.json`:
- `"baseBranch": "release/current"`
- `"access": "public"`
- `"updateInternalDependencies": "patch"` (activates the dependency-pin-drift fix, defect #5)
- Independent per-package versioning (no `fixed`/`linked` groups).
- Custom `"changelog"` entry pointing at a new `changelog-bitbucket.cjs` implementing changesets' `ChangelogFunctions` interface (`getReleaseLine`/`getDependencyReleaseLine`) with the correct `/projects/DEV/repos/boreal-ds/commits/<hash>` URL scheme built in from the start.

### B3 — Enter prerelease mode
`pnpm changeset pre enter alpha` for the workspace, matching the existing `0.1.0-alpha.N` scheme so the transition is version-number-compatible with what's already published.

### B4 — Replace release scripts
Retire `pnpm release:styles`/`release:wc`/`release:react`/`release:vue`/`release:all` in favor of `changeset version` (applies pending changesets, bumps versions, writes changelogs, including auto-included dependents) + `changeset publish` (publishes to npm, tags) — changesets is inherently monorepo-aware, so this can become a single root-level orchestration rather than four sequential per-package invocations.

### B5 — Retire release-it
Remove all four `.release-it.json` files, `@release-it/conventional-changelog`, `release-it` itself, and the custom `headerPattern`/commitlint coupling built around it. Re-point `check-cem-changes.ts` (currently reads `npm.tag` from `.release-it.json`) at its new version source.

### B6 — Backfill, rename, create CONTRIBUTING.md
Backfill the missing `bds-table` v3/v4 changelog entries into `boreal-web-components/CHANGELOG.md` (changesets can't retroactively reconstruct history either) — one entry per PR. Same folder rename as Option A: `git mv packages/boreal-styleguidelines packages/boreal-style-guidelines`, regenerate lockfile, update the `copy-styles.js:8` comment and actively-used references.

Create `/CONTRIBUTING.md` at the workspace root (none exists today). **Fully self-contained — no references to `ai-docs/`/`ai-work/`, since those directories are untracked by git and not visible to the rest of the team.**

```markdown
# Contributing to Boreal DS

## How We Develop
We use Bitbucket Server to host code, track work via Jira, and review changes through pull requests.

## Branching
Boreal DS uses a trunk-based model with a single permanent integration/release branch, `release/current`. All work branches off it and merges back into it.

| Branch | Type | Description |
|---|---|---|
| `release/current` | Permanent | Default branch. Reflects the latest published or in-progress release. |
| `feature/` | Temporary | New feature or ticket work. |
| `fix/` / `bugfix/` | Temporary | Bug fixes. |
| `docs/` | Temporary | Documentation-only changes. |
| `chore/` | Temporary | Housekeeping/non-production changes. |

Branch naming: `type/TICKET-ID_short-description`, e.g. `feature/EOA-10057_add-text-field`. Keep PRs small and short-lived.

## Commit Messages
All commits follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) in the format **`type(scope): TICKET-ID description`**. Use `pnpm commit` for a guided prompt; commitlint validates every message via a git hook.

| Type | Changelog / SemVer impact |
|---|---|
| `feat` | New feature → **MINOR** |
| `fix` | Bug fix → **PATCH** |
| `BREAKING CHANGE:` footer or `!` suffix | → **MAJOR** |
| `build`, `chore`, `ci`, `docs`, `style`, `refactor`, `perf`, `test` | No SemVer impact |

## Pull Requests
- **Always use Squash and Merge.**
- PR description must state what changed, why, and link the Jira ticket (e.g. `Closes EOA-123`).
- Minimum 2 approvals (excluding the author), at least 1 from a core maintainer. All review comments must be resolved before merge.
- All CI checks (lint, tests, build) must pass; new/modified components need unit tests (≥ 90% coverage); bug fixes need a test that reproduces and validates the fix.

## Report a Bug
Open a Jira ticket in the project's bug-tracking board with: a clear summary, the affected component/feature, environment (browser/OS/Boreal version/framework), steps to reproduce, expected vs. actual behavior.

## Project Setup
See [README.md](README.md).

## Release & Versioning
- Packages release independently, each on its own `0.1.0-alpha.N` prerelease track, driven by `changesets`.
- **Every PR that changes a publishable package must include a changeset.** Run `pnpm changeset add`, select the affected package(s), pick a bump level (patch/minor/major), and write a one-line summary — this becomes the changelog entry, so write it for consumers, not just for reviewers. Commit the generated `.changeset/*.md` file as part of your PR.
- If your PR only touches a package that another package depends on via `workspace:*` (e.g. you changed `boreal-web-components` and `boreal-react` wraps it), you do **not** need to add a separate changeset for the dependent — `changesets` detects the out-of-range pin automatically and includes it in the same release with a patch bump.
- Alpha stays in effect until real-world usage feedback has been addressed — not tied to a specific version number. When ready, the package graduates directly to `1.0.0`, regardless of the internal alpha counter.
- [Once CI exists:] a bot check (`changeset status --since=release/current`) will flag PRs that change a publishable package without an accompanying changeset.
```

(Code of Conduct and Recommended IDE Extensions sections deliberately omitted: no `CODE_OF_CONDUCT.md` or extensions list exists anywhere in the tracked repo — flag as an open decision rather than inventing content or linking to something that doesn't exist.)

Update the PR template (development standards, PR Template section) to add a "Changeset included?" checklist item — flag this as a needed edit, not silently skip it.

---

## Task List

1. Create ADR 0013 (B1) — already created; update Status/Decision once this plan is executed.
2. Implement B2 (install + config + custom Bitbucket changelog formatter) — manual test: `pnpm changeset add` produces a valid changeset file; `pnpm changeset status` runs cleanly.
3. Implement B3 (prerelease mode) — manual test: confirm `changeset pre enter alpha` doesn't conflict with already-published `-alpha.N` tags/versions.
4. Implement B4 (release script replacement) — manual test: inspect the generated diff from a scratch changeset without publishing; confirm correct version bumps and changelog output, including dependency auto-inclusion for `boreal-react`/`boreal-vue`.
5. Implement B5 (retire release-it) — manual test: `check-cem-changes.ts` still runs correctly against the new version source.
6. Implement B6 (backfill, rename, CONTRIBUTING.md, PR template update) — manual test: `pnpm install` and a full build succeed from the new path; `changeset status --since=release/current` correctly flags an intentionally-changeset-less test PR.

## Verification

- All version/changelog changes validated via dry-run equivalents before any real publish.
- No package is actually released/published/tagged as part of this plan.
