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

1. **Squash merges break changelog/version generation.** Bitbucket Server squash commits (e.g. `d3bb6f51` "Pull request #166...", `fab67bea` "Pull request #159...") have subject lines that don't match the `headerPattern` any `.release-it.json` uses, so `@release-it/conventional-changelog` silently drops them. 19+ `feat`/`fix` commits for `bds-table` v3/v4 are invisible in every changelog and never counted toward version bumps.
2. **No per-package path scoping.** All four `.release-it.json` files scan the full git log since their own last tag with no path filter — why `boreal-web-components`, `boreal-react`, `boreal-vue` changelogs are byte-for-byte identical for shared entries.
3. **Version base (`0.1.0`) never escalates**, independent of merge strategy. `release-it`'s "continuation" logic (`semver.inc(latestVersion, 'prerelease', 'alpha')`) triggers once a version's prerelease id already matches the configured `preReleaseId`, and this **ignores** the bump level conventional-changelog recommends. This directly violates the team's own documented standard (`feat`→MINOR, `fix`→PATCH) — confirming this is a real defect, not a debatable trade-off.
4. **Every commit link in every CHANGELOG.md is broken.** `@release-it/conventional-changelog`'s built-in "Bitbucket" URL formatter assumes Bitbucket Cloud, not self-hosted Bitbucket Server (this repo's actual host), which uses a different path scheme (`/projects/<KEY>/repos/<slug>/commits/<hash>`). `package.json` `repository.url` is also inconsistent across packages, and `boreal-web-components`'s is still the literal leftover Stencil-starter placeholder.
5. **Wrapper dependency-pin drift.** Confirmed directly (`pnpm pack` + tarball inspection): `boreal-react`/`boreal-vue`'s `"@telesign/boreal-web-components": "workspace:*"` gets replaced with a hard-pinned exact version at publish time. If `boreal-web-components` releases and the wrappers don't (correct behavior once path-scoping/#2 is fixed, since they'd have no own commits), their published tarballs keep pointing at the stale pinned version indefinitely — nothing currently detects or fixes this.

Two suspected issues were ruled out: `boreal-styleguidelines`'s "staleness" (zero commits touched it since its last tag — no release due) and the `0.1.0-alpha.N` scheme's shape (a legitimate pre-1.0 convention; only its lack of graduation, #3, is broken).

This plan keeps `release-it` and patches around its gaps rather than migrating to `changesets` — lower migration cost, but each fix below is a bespoke patch layered onto three separately-glued tools (`release-it`, `@release-it/conventional-changelog`, a custom `headerPattern` regex) rather than something the tool does natively.

Confirmed decisions for this plan:
- Keep squash merges — enforce conventional-commit-formatted PR titles instead (needs verification: does `bitbucket.c11.telesign.com` have a commit-message-checking hook like YACC installed?).
- Rename `packages/boreal-styleguidelines` → `packages/boreal-style-guidelines` (low risk, confirmed no hardcoded folder-path references in `turbo.json`/`tsconfig*.json`/workspace deps).
- Alpha-graduation policy: stay in `-alpha.N` until real-world feedback addressed; graduate straight to `1.0.0` when ready, regardless of the internal alpha counter.
- Keep full auto-generated `CHANGELOG.md` for all four packages, including wrappers.

---

## Fixes

### A1 — Enforce squash-merge PR title format
Verify whether `bitbucket.c11.telesign.com` has a commit-message-checking hook (e.g. YACC) installed; if so, configure a regex hook on `release/current` matching `type(scope): TICKET-ID subject`. If not, document-only convention (manual-discipline risk). Backfill the two already-broken squash entries (`bds-table` v3/v4) into `boreal-web-components/CHANGELOG.md`, one line per PR.

### A2 — Explicit version-bump escalation wrapper
Add `scripts/release-with-bump.ts` that runs `conventional-recommended-bump` before invoking `release-it`, then passes the result explicitly (`--increment=minor`/`--increment=major`) instead of relying on default continuation behavior. Wire into each package's `release` npm script.

### A3 — Path-scoped changelog generation
Add `gitRawCommitsOpts.path` (verify exact key/wiring via `--dry-run`) to each package's `.release-it.json`, scoping its own directory only.

### A4 — Fix commit/compare links for Bitbucket Server
Fix `repository.url` in all four `package.json` files to `https://bitbucket.c11.telesign.com/projects/DEV/repos/boreal-ds`. Add explicit `commitUrlFormat`/`compareUrlFormat` (or a `.release-it.js` with a `formatCommitUrl` override, depending on the installed `conventional-changelog-conventionalcommits` version) targeting `/projects/DEV/repos/boreal-ds/commits/<hash>`. Decide separately whether to bulk-fix already-published broken links.

### A5 — Dependency re-pin detection for wrappers
1. Spike `@release-it/bumper` + `@release-it/conventional-changelog` together first (explicitly untested combination per release-it's own maintainer) — verify it actually triggers a release for `boreal-react`/`boreal-vue` with zero own commits and produces a sane changelog entry.
2. Fall back to a custom script if the spike fails: detect when the pinned `@telesign/boreal-web-components` version is behind the latest tag, force a release with a synthetic `### Dependencies` changelog entry.

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
- **Always use Squash and Merge.** Because PRs are squashed into a single commit, **the PR title itself becomes the changelog/version-bump source** — it MUST follow the same Conventional Commits format as above. [If a Bitbucket hook (YACC or equivalent) was confirmed available per task A1: this is validated automatically at merge time. If not: there is currently no automated check — double-check your PR title before merging.]
- PR description must state what changed, why, and link the Jira ticket (e.g. `Closes EOA-123`).
- Minimum 2 approvals (excluding the author), at least 1 from a core maintainer. All review comments must be resolved before merge.
- All CI checks (lint, tests, build) must pass; new/modified components need unit tests (≥ 90% coverage); bug fixes need a test that reproduces and validates the fix.

## Report a Bug
Open a Jira ticket in the project's bug-tracking board with: a clear summary, the affected component/feature, environment (browser/OS/Boreal version/framework), steps to reproduce, expected vs. actual behavior.

## Project Setup
See [README.md](README.md).

## Release & Versioning
- Packages release independently, each on its own `0.1.0-alpha.N` prerelease track, driven by `release-it` + Conventional Commits.
- Alpha stays in effect until real-world usage feedback has been addressed — not tied to any specific accumulated version number. When ready, the package graduates directly to `1.0.0` (dropping the `-alpha.N` suffix), regardless of what the internal alpha counter reached.
- Each package's `CHANGELOG.md` is scoped to commits/PRs that touched its own files; a wrapper package (`boreal-react`/`boreal-vue`) may also show a release with no functional changes of its own — a `### Dependencies` entry — when its pinned `@telesign/boreal-web-components` version needed to move forward.
```

(Code of Conduct and Recommended IDE Extensions sections deliberately omitted: no `CODE_OF_CONDUCT.md` or extensions list exists anywhere in the tracked repo — flag as an open decision rather than inventing content or linking to something that doesn't exist.)

---

## Task List

0. Create ADR 0013 at `ai-docs/decisions/0013-release-tooling-release-it-vs-changesets.md` (already created — update its Status to `Accepted` and fill in Option A once this plan is executed).
1. Verify Bitbucket Server hook capability (gates A1's mechanism).
2. Implement A1 (enforcement + backfill).
3. Implement A2 (bump wrapper) — manual test: dry-run against current git state, confirm it would have recommended a minor bump for the backfilled `bds-table` work.
4. Implement A3 (path scoping) — manual test: `--dry-run` per package, confirm no cross-package leakage.
5. Implement A5 (spike `@release-it/bumper`; fall back to custom script if it fails) — manual test: simulate a `boreal-web-components` release, confirm drift detection and a correct changelog note.
6. Implement A4 (link fixes) — manual test: `--dry-run`, open a generated URL in a browser, confirm it resolves.
7. Implement A6 (rename, CONTRIBUTING.md, policy docs) — manual test: `pnpm install` and a full build succeed from the new path; CONTRIBUTING.md renders correctly and its links resolve.

## Verification

- Each `.release-it.json`/wrapper-script change validated via `--dry-run` (never actually publishes or tags).
- No package is actually released/published/tagged as part of this plan.
