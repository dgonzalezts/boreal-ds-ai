---
ticket: AI-003
status: pending
created: 2026-08-12
---

# Release Process Remediation — Option A: Patch `release-it` in place

**Note:** `AI-003` is a placeholder ticket prefix — rename this file (and the `ticket:` field above) to the real Jira ticket ID once one is assigned. See the sibling plan `AI-003-release-process-remediation-migrate-changesets.md` for the alternative (Option B: migrate to `changesets`) and `ai-docs/decisions/0013-release-tooling-release-it-vs-changesets.md` for the ADR comparing both.

---

## Context

A 2026-08-12 audit of the release process implemented by `EOA-9609-automated-changelog-&-rp.md`, `EOA-9609-first-alpha-release.md`, and `EOA-9609-alpha-release-vue-react-storybook.md` against the current state of `CHANGELOG.md`/`package.json` across all four packages (`boreal-styleguidelines`, `boreal-web-components`, `boreal-react`, `boreal-vue`) found five real defects:

1. **Squash merges break changelog/version generation.** Bitbucket Server squash commits (e.g. `d3bb6f51` "Pull request #166...", `fab67bea` "Pull request #159...") have subject lines that don't match the `headerPattern` any `.release-it.json` uses, so `@release-it/conventional-changelog` silently drops them. 19+ `feat`/`fix` commits for `bds-table` v3/v4 are invisible in every changelog and never counted toward version bumps. **Partial fix only:** a `headerPattern` regex adjustment (A3) can tolerate Bitbucket's `Pull request #N: ` prefix, but actual PR-title format compliance has no automated enforcement path (A1 is not viable — see below) and remains convention-only.
2. **No per-package path scoping.** All four `.release-it.json` files scan the full git log since their own last tag with no path filter — why `boreal-web-components`, `boreal-react`, `boreal-vue` changelogs are byte-for-byte identical for shared entries. **Native fix confirmed** (2026-08-13 doc review): `path` is a documented field on both `GitLogParams` (used by `gitRawCommitsOpts`, scopes the changelog) and `GetCommitsParams` (used by `commitsOpts`, scopes the bump recommendation) in `@conventional-changelog/git-client`'s official API — both need to be set; the original plan only specified the former.
3. **Version base (`0.1.0`) never escalates**, independent of merge strategy. `release-it`'s "continuation" logic (`semver.inc(latestVersion, 'prerelease', 'alpha')`) triggers once a version's prerelease id already matches the configured `preReleaseId`, and this **ignores** the bump level conventional-changelog recommends. This directly violates the team's own documented standard (`feat`→MINOR, `fix`→PATCH) — confirming this is a real defect, not a debatable trade-off. **Native fix confirmed** (2026-08-13 doc review): `@release-it/conventional-changelog`'s own README documents exactly this behavior and its opt-out — `"strictSemVer": true` — "Use `true` to strictly follow semver, also in consecutive pre-releases... The default behavior results in a `prerelease` bump." No custom wrapper script needed.
4. **Every commit link in every CHANGELOG.md is broken.** `@release-it/conventional-changelog`'s built-in "Bitbucket" URL formatter assumes Bitbucket Cloud, not self-hosted Bitbucket Server (this repo's actual host), which uses a different path scheme (`/projects/<KEY>/repos/<slug>/commits/<hash>`). `package.json` `repository.url` is also inconsistent across packages, and `boreal-web-components`'s is still the literal leftover Stencil-starter placeholder.
5. **Wrapper dependency-pin drift.** Confirmed directly (`pnpm pack` + tarball inspection): `boreal-react`/`boreal-vue`'s `"@telesign/boreal-web-components": "workspace:*"` gets replaced with a hard-pinned exact version at publish time. Under a selective per-package model, if `boreal-web-components` releases and wrappers do not, published wrapper tarballs keep pointing at the stale pinned WC version indefinitely. **No native selective-release fix exists** (2026-08-13 doc review): `@release-it/bumper` only reads/writes version values during a release already executing for that package. Under the adopted WC-stack orchestration model (A5), drift is avoided structurally by always releasing wrappers whenever `boreal-web-components` releases.

Two suspected issues were ruled out: `boreal-styleguidelines`'s "staleness" (zero commits touched it since its last tag — no release due) and the `0.1.0-alpha.N` scheme's shape (a legitimate pre-1.0 convention; only its lack of graduation, #3, is broken).

This plan keeps `release-it` and patches around its gaps rather than migrating to `changesets`. A 2026-08-13 review of `release-it`/`@release-it/conventional-changelog`/`@release-it/bumper`'s official documentation found that **two of the three tool-level defects (#2 path scoping, #3 version escalation) are native config flags on tools already installed, not bespoke patches** — meaningfully lowering this option's migration cost versus the original estimate. For #5 (dependency-pin drift), this plan now adopts a release-topology fix (A5: orchestrated WC stack releases) as the primary path instead of a custom drift-detector script.

Confirmed decisions for this plan:
- Keep squash merges. PR-title-format enforcement (originally A1) is **not viable**: it requires a server-side Bitbucket Server commit-message hook (e.g. YACC), and there is no pipeline/admin access and no release-team support available to install one. No client-side git hook (Husky) can substitute, because the squash commit is generated by the server at merge time, after local hooks have already run. This is accepted as a documented-convention-only gap with no automated backstop — matching BEEQ's own unsolved equivalent (confirmed directly in `ai-docs/lib/beeq.txt`: only two GitHub Actions workflows exist, `github-pages.yml`/`publish.yml`, neither validates PR titles; the `semanticCommits: "enabled"` Renovate setting only governs Renovate's own automated PRs).
- Rename `packages/boreal-styleguidelines` → `packages/boreal-style-guidelines` (low risk, confirmed no hardcoded folder-path references in `turbo.json`/`tsconfig*.json`/workspace deps).
- Alpha-graduation policy: stay in `-alpha.N` until real-world feedback addressed; graduate straight to `1.0.0` when ready, regardless of the internal alpha counter.
- Keep full auto-generated `CHANGELOG.md` for all four packages, including wrappers.
- CHANGELOG cleanup for already-published history is in scope (see A7) — tiers 1–2 required, tier 3 optional/flagged — not deferred as in the original ADR consequence note.
- Release topology is **orchestrated by default** for product packages: every `boreal-web-components` release must be followed by `boreal-react` and `boreal-vue` releases in the same flow (A5), so wrappers always repin to the newly-published WC version. `boreal-style-guidelines` remains independent and releases only when it changed. Selective per-package releases are retained only for wrapper-only maintenance cases (e.g., wrapper dependency/tooling updates with no WC changes).
- `release:all` is deprecated for decisioning because it over-releases unrelated packages (notably style-guidelines when unchanged). The default operational commands become `release:wc-stack` (WC + wrappers) and `release:styles` (styles only).

---

## Fixes

### A1 — Enforce squash-merge PR title format — NOT VIABLE
**Status: not viable, removed from scope.** Enforcement would require a server-side Bitbucket Server commit-message hook (e.g. YACC) on the squash-merge commit itself — no client-side git hook (Husky) can reach it, since the squash commit is generated by the server at merge time, after local hooks already ran. There is no pipeline/admin access and no release-team support to install such a hook. Accepted as a documented-convention-only gap (see CONTRIBUTING.md draft below), with no automated backstop — the same unsolved gap BEEQ (an actively-maintained comparison project) has today. The Bitbucket-generated `Pull request #N: ` prefix on squash commits is still handled separately, folded into A3 below (a cheap `headerPattern` regex adjustment, independent of title-format compliance). Backfill of the two already-broken squash entries (`bds-table` v3/v4) into `boreal-web-components/CHANGELOG.md`, one line per PR, is still required — see A7.

### A2 — Version-bump escalation via `strictSemVer`
Set `"strictSemVer": true` in each package's `@release-it/conventional-changelog` plugin config. This is a native, documented option (not a custom script): per the plugin's official README, the default behavior treats a pre-release as a simple counter continuation regardless of the recommended bump level; `strictSemVer: true` makes a `feat` commit produce a `preminor` bump (e.g. `0.1.0-alpha.5` → `0.2.0-alpha.0`) and a `fix` commit a `prepatch` bump, correctly escalating the base version while remaining in the alpha track (the alpha counter resets to 0 on each base-version escalation — expected, not a bug). No wrapper script needed.

### A3 — Path-scoped changelog generation and bump recommendation
Add `path` (the package's own directory) to **both** `commitsOpts` (scopes the version-bump recommendation — `GetCommitsParams.path` per `@conventional-changelog/git-client`'s API) **and** `gitRawCommitsOpts` (scopes the changelog text — `GitLogParams.path`) in each package's `.release-it.json`. Both are native, documented fields; setting only one (as originally scoped) would leave the bump calculation still reading the full repo log even after the changelog itself was correctly scoped. Also adjust `headerPattern` to tolerate the Bitbucket Server squash-merge prefix (`Pull request #<N>: `) ahead of the conventional `type(scope): subject` portion, so correctly-formatted PR titles parse even though title-format compliance itself remains unenforced (per A1).

### A4 — Fix commit/compare links for Bitbucket Server
Fix `repository.url` in all four `package.json` files to `https://bitbucket.c11.telesign.com/projects/DEV/repos/boreal-ds`. Add explicit `commitUrlFormat`/`compareUrlFormat` (or a `.release-it.js` with a `formatCommitUrl` override, depending on the installed `conventional-changelog-conventionalcommits` version) targeting `/projects/DEV/repos/boreal-ds/commits/<hash>`. This only fixes links generated going forward — the retroactive fix for already-published broken links is A7, tier 1.

### A5 — Orchestrated WC stack release flow (primary fix for wrapper repin drift)
Use release topology, not a drift-detector script, as the primary fix for defect #5:

1. Update root `package.json` scripts with explicit commands:
   - `release:react:sync`: `pnpm --filter @telesign/boreal-react exec release-it --ci --increment=prerelease --plugins.@release-it/conventional-changelog.ignoreRecommendedBump=true`
   - `release:vue:sync`: `pnpm --filter @telesign/boreal-vue exec release-it --ci --increment=prerelease --plugins.@release-it/conventional-changelog.ignoreRecommendedBump=true`
   - `release:wc-stack`: `pnpm run release:wc && pnpm run validate:all && pnpm run release:react:sync && pnpm run release:vue:sync`
2. Use `release:wc-stack` as the default path for any PR that changes `boreal-web-components` so wrappers publish even when they have no own commits in that PR.
3. Keep `release:react` and `release:vue` as selective exception paths for wrapper-only maintenance changes (e.g. wrapper dependency/tooling updates without WC changes).
4. Keep `release:styles` independent; style-guidelines is excluded from the WC-stack flow and only releases when changed.
5. Deprecate `release:all`/`release:publish` as operational defaults to avoid accidental style-guidelines releases without relevant changes.

This model guarantees that every WC release repins wrapper dependencies without requiring a custom drift-detection script.

### A6 — Rename folder, create CONTRIBUTING.md, document policies
`git mv packages/boreal-styleguidelines packages/boreal-style-guidelines`, regenerate lockfile, update the `copy-styles.js:8` comment and actively-used references (`.lintstagedrc.js`, `.agents/memory/MEMORY.md`, `.agents/copilot-instructions.md`, `README.md`; historical `ai-work/`/review files left as-is unless the team wants them rewritten).

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
- **Always use Squash and Merge.** Because PRs are squashed into a single commit, **the PR title itself becomes the changelog/version-bump source** — it MUST follow the same Conventional Commits format as above. **There is no automated check for this** (server-side hook enforcement was evaluated and found not viable — no pipeline/admin access available) — double-check your PR title before merging; an incorrectly formatted title will be silently dropped from the changelog and won't count toward the version bump.
- PR description must state what changed, why, and link the Jira ticket (e.g. `Closes EOA-123`).
- Minimum 2 approvals (excluding the author), at least 1 from a core maintainer. All review comments must be resolved before merge.
- All CI checks (lint, tests, build) must pass; new/modified components need unit tests (≥ 90% coverage); bug fixes need a test that reproduces and validates the fix.

## Report a Bug
Open a Jira ticket in the project's bug-tracking board with: a clear summary, the affected component/feature, environment (browser/OS/Boreal version/framework), steps to reproduce, expected vs. actual behavior.

## Project Setup
See [README.md](README.md).

## Release & Versioning
- Packages release independently, each on its own `0.1.0-alpha.N` prerelease track, driven by `release-it` + Conventional Commits.
- Default flow for any PR that changes `@telesign/boreal-web-components`: run `release:wc-stack` so `@telesign/boreal-react` and `@telesign/boreal-vue` are republished in the same cycle and repin to the new WC version.
- `@telesign/boreal-style-guidelines` remains independent: release it only when its own files changed (`release:styles`).
- `release:all` is deprecated for routine use because it can publish unchanged packages (especially style-guidelines).
- Alpha stays in effect until real-world usage feedback has been addressed — not tied to any specific accumulated version number. When ready, the package graduates directly to `1.0.0` (dropping the `-alpha.N` suffix), regardless of what the internal alpha counter reached.
- Each package's `CHANGELOG.md` is scoped to commits/PRs that touched its own files; a wrapper package (`boreal-react`/`boreal-vue`) may also show a release with no functional changes of its own — a `### Dependencies` entry — when its pinned `@telesign/boreal-web-components` version needed to move forward.
```

(Code of Conduct and Recommended IDE Extensions sections deliberately omitted: no `CODE_OF_CONDUCT.md` or extensions list exists anywhere in the tracked repo — flag as an open decision rather than inventing content or linking to something that doesn't exist.)

### A7 — CHANGELOG cleanup (retroactive, already-published history)
Split into three tiers so effort is visible up front; tiers 1–2 are required for this plan, tier 3 is optional and must be explicitly decided, not silently skipped:

1. **Link rewrite (required, low effort).** Mechanical regex rewrite of every existing commit/compare URL across all four `CHANGELOG.md` files, from the current broken scheme (confirmed: `bitbucket.c11.telesign.com/7999/dev/boreal-ds/commit/<hash>`) to the correct Bitbucket Server path (`/projects/DEV/repos/boreal-ds/commits/<hash>`). Scriptable — no editorial judgment needed.
2. **Cross-package de-duplication (recommended, medium effort).** Review and reconcile the near-identical multi-hundred-line blocks currently duplicated verbatim across `boreal-web-components`/`boreal-react`/`boreal-vue` `CHANGELOG.md` files (confirmed present across the `0.1.0-alpha.0`–`alpha.3` sections). Requires a judgment call on canonical ownership per historical entry — cosmetic/historical, not functionally broken, so this can slip if deprioritized, but should be an explicit decision.
3. **Editorial noise cleanup (optional, high effort — flag as open decision, do not silently skip).** Existing changelogs contain low-signal entries that leaked in under the current tooling (e.g. `remove test cases from index.html`, `Fix adjusments on PR`, `JSdocs lint fix`). Cleaning these up is a genuine manual-review effort across ~2,500+ lines total; present to the team as a "do we want to invest in this" decision rather than bundling it into this plan by default.

---

## Task List

0. Create ADR 0013 at `ai-docs/decisions/0013-release-tooling-release-it-vs-changesets.md` (already created — update its Status to `Accepted` and fill in Option A once this plan is executed).
1. Backfill the two already-broken squash entries (`bds-table` v3/v4) into `boreal-web-components/CHANGELOG.md`, one line per PR (part of A1's scope, still required despite enforcement being not viable).
2. Implement A2 (`strictSemVer: true` config flag) — manual test: `--dry-run` against current git state, confirm a `feat`-containing history now recommends a `preminor` bump (base version escalates) rather than a plain `prerelease` continuation.
3. Implement A3 (path scoping on both `commitsOpts` and `gitRawCommitsOpts`, plus squash-prefix regex tolerance) — manual test: `--dry-run` per package, confirm no cross-package leakage in either the changelog text or the recommended bump, and that a correctly-formatted PR title with the `Pull request #N: ` prefix parses.
4. Implement A5 in root `package.json` scripts (`release:react:sync`, `release:vue:sync`, `release:wc-stack`, and deprecation notes for `release:all`/`release:publish`) — manual test: dry-run a WC-only change and confirm `boreal-web-components`, `boreal-react`, and `boreal-vue` would all release in sequence while `boreal-style-guidelines` does not.
5. Implement A4 (link fixes, forward-only) — manual test: `--dry-run`, open a generated URL in a browser, confirm it resolves.
6. Implement A7 (CHANGELOG cleanup, tiers 1–2 required) — manual test: spot-check rewritten links resolve in a browser; confirm de-duplicated sections still contain every original entry.
7. Implement A6 (rename, CONTRIBUTING.md, policy docs) — manual test: `pnpm install` and a full build succeed from the new path; CONTRIBUTING.md renders correctly and its links resolve.
8. Add selective exception validation for wrappers-only maintenance: dry-run a wrapper-only dependency/tooling change and confirm only the intended wrapper package releases when using the selective command.

## Verification

- Each `.release-it.json` change (A2, A3, A4) validated via `--dry-run` (never actually publishes or tags).
- A5 orchestration validated via dry-run for two scenarios: (1) WC-only change triggers WC + both wrappers, excludes style-guidelines, and uses `release:wc-stack`; (2) wrapper-only maintenance change can release only the targeted wrapper via `release:react` or `release:vue`.
- No package is actually released/published/tagged as part of this plan.
