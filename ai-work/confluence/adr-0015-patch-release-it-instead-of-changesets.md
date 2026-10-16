# ADR-0015: Patch release-it in Place (Squash-Merge Releases, `@pxglobal` Scope, Compare Links) Instead of Migrating to Changesets

## Status

Accepted. Implemented 2026-10-08; first real `@pxglobal` release 2026-10-09 (`0.14.0`); second release 2026-10-13 (`0.14.1`). Amends ADR-0011.

## Date

2026-10-01 (decision). Audit and options analysis: 2026-08-12 and 2026-08-13.

## Deciders

Proximus Global Design System / Component Library Core Team

## Context and Problem Statement

The original release plan (2026-05-19) replaced a prior Changesets setup with `release-it` + `@release-it/conventional-changelog` (ADR-0011), recording only "Changesets fully removed (no fallback)": there was no comparative analysis and no stated reason. A 2026-08-12 audit of the resulting release process found five real defects, several of them structural to how `release-it` and conventional-commit parsing behave in a monorepo:

1. **Squash merges break changelog and version generation.** Bitbucket Server squash commits (for example "Pull request #166...") have subject lines that do not match the `headerPattern` any `.release-it.json` uses, so `@release-it/conventional-changelog` silently drops them. Their `feat` and `fix` changes are invisible in every changelog and are never counted toward version bumps.
2. **No per-package path scoping.** All four `.release-it.json` files scan the full git log since their own last tag with no path filter, which is why the `boreal-web-components`, `boreal-react` and `boreal-vue` changelogs were identical for shared entries.
3. **The version base (`0.1.0`) never escalates**, independent of the merge strategy. `release-it`'s "continuation" logic (`semver.inc(latestVersion, 'prerelease', 'alpha')`) triggers once a version's prerelease id already matches the configured `preReleaseId`, and it **ignores** the bump level that conventional-changelog recommends. This violates the team's own documented standard (`feat` → MINOR, `fix` → PATCH), so it is a real defect and not a debatable trade-off.
4. **Every commit link in every `CHANGELOG.md` is broken.** The built-in "Bitbucket" URL formatter of `@release-it/conventional-changelog` assumes Bitbucket Cloud, not the self-hosted Bitbucket Server this repository lives on, which uses a different path scheme (`/projects/<KEY>/repos/<slug>/commits/<hash>`). The `repository.url` field of `package.json` was also inconsistent across packages, and in `boreal-web-components` it was still the Stencil-starter placeholder.
5. **Wrapper dependency-pin drift.** Confirmed with `pnpm pack` and tarball inspection: the `workspace:*` dependency of `boreal-react` and `boreal-vue` on `boreal-web-components` is replaced with a hard-pinned exact version at publish time. If `boreal-web-components` releases and the wrappers do not (the correct behavior once path scoping is fixed, since they would have no commits of their own), their published tarballs keep pointing at the stale pinned version indefinitely, and nothing detects or fixes that.

Two suspected issues were ruled out: the "staleness" of `boreal-style-guidelines` (no commit touched it since its last tag, so no release was due) and the shape of the `0.1.0-alpha.N` scheme (a legitimate pre-1.0 convention; only its lack of graduation, defect 3, was broken).

**Precedent check, Endava's BEEQ** (Nx-based, `@beeq/core`, actively maintained): its `nx.json` uses an explicit `type → changelog title + semverBump` table and `[skip ci]` release commits, which is a cleaner single-tool architecture worth borrowing ideas from without adopting Nx. But even BEEQ does not fully automate the trigger step: its publish workflow fires on a published GitHub release, and the step that writes the version and changelog runs manually, the same as Boreal DS today. Its `CONTRIBUTING.md` also mandates "always use Squash and merge" with a Conventional-Commit PR title and no bot found enforcing that title. Conclusion: the manual trigger and the reliance on a written convention are not unusually primitive.

**Turborepo integration**, verified against both tools' official documentation: Turborepo's publishing guide never mentions `release-it` and gives equally shallow advice for either tool (a `turbo build` pre-step, no deep plugin, no dependency-graph-aware task type). `release-it`'s own monorepo recipe confirms the same shallow pattern and points to `@release-it/bumper` for dependency auto-bumping, but its maintainer states the recipe was not tested with the conventional-changelog plugin, the exact combination this repository needs. The differentiator is therefore not Turborepo integration depth. It is that changesets has tested, first-class dependent bumping (`determineDependents`), while `release-it` reaches the same practical result only through release topology (always release the dependent workspaces in the same flow) or custom project logic.

**No CI/pipeline access constraint (confirmed 2026-08-13):** neither a Bitbucket Server admin or pipeline configuration path nor release-team support is available to this effort. This rules out any server-side enforcement mechanism, specifically a PR-title commit hook for `release-it`, which is now marked not viable. Client-side git hooks (Husky, already used for commitlint) cannot replace it, because Bitbucket Server generates the squash-merge commit itself at merge time, after any local hook has run. Changesets does not have this problem (a changeset file can be checked against the PR's own branch diff), but without a pipeline that check would also be only a PR-template checklist item plus reviewer responsibility. Both options therefore land on the same class of unenforced, convention-only PR-level gate, so this is not a differentiator between them.

**`release-it` tool-capability review (2026-08-13)** of `release-it`, `@release-it/conventional-changelog`, `@release-it/bumper` and the underlying `conventional-recommended-bump` and `@conventional-changelog/git-client` documentation found that two of the three tool-level fixes are native configuration, not bespoke patches: (1) `strictSemVer` on `@release-it/conventional-changelog` addresses defect 3; (2) `path` scoping for defect 2 is a documented field of both `gitRawCommitsOpts` (scopes the changelog) and `commitsOpts` (scopes the bump recommendation), and both must be set. Defect 5 is not natively solved by any documented plugin in a selective per-package model, since `@release-it/bumper` only reads and writes versions during a release already running for that package. The fix therefore has to be release topology: release `boreal-web-components`, then both wrappers, in the same flow.

## Decision Drivers

- Fix the five audited defects without disrupting a team already used to `release-it`
- Stay aligned with the team's documented release process and versioning standard (`feat` → minor, `fix` → patch)
- Lowest delivery risk within PI9
- No CI/pipeline access: no server-side enforcement is possible, so the fix must not depend on it
- Wrapper packages must never be installable against a stale `boreal-web-components` pin

## Considered Options

- **Option A:** patch `release-it` in place
- **Option B:** migrate to `changesets`

## Decision Outcome

Chosen option: **Option A, patch `release-it` in place** (decided 2026-10-01, Jira EOA-18749).

Option A keeps the current tool and adds: a custom parser that accepts the Bitbucket squash-merge prefix; path-scoped changelog and bump configuration; a version-bump escalation setting; a `context` block that builds Bitbucket Server URLs; and an orchestrated release topology for the web-components product stack (`boreal-web-components` → `boreal-react` → `boreal-vue`) so that wrapper pin drift is prevented by the flow and not detected after the fact. `boreal-style-guidelines` stays independent and releases only when changed. A selective per-package release remains available only as an exception path. PR-title enforcement is not viable given the no-pipeline-access constraint, so defect 1 is only partially addressed: the parser tolerates Bitbucket's squash-merge prefix, but compliance with the title format has no automated backstop.

The options were scored with a rubric (A 73, B 68 with the default weights): minimal friction for a team already used to `release-it`, near one-to-one alignment with the documented release process, and the lowest delivery risk within PI9. Option B's structural advantages are acknowledged, and the result flips toward B if guideline alignment is weighted down.

**Revisit triggers:** (1) a merged `feat` or `fix` PR is missing from a generated changelog more than once in a PI; (2) EOA-18870 grants CI/pipeline access; (3) the `1.0.0` graduation is scheduled (EOA-18867), which is the cheapest point to adopt changesets.

## Pros and Cons of the Options

### Option A - Patch `release-it` in place

- Good, because the team keeps a tool it already knows, and the change is incremental
- Good, because two of the three tool-level fixes are native configuration flags, not custom code
- Good, because it aligns almost one to one with the documented release process
- Good, because it has the lowest delivery risk within PI9
- Bad, because defect 5 (wrapper pin drift) is controlled by release topology and operational discipline, not by tooling: if a team bypasses the orchestrated flow, the drift risk returns
- Bad, because PR-title format compliance has no automated backstop

### Option B - Migrate to `changesets`

- Good, because it matches Turborepo's own documented recommendation
- Good, because a human explicitly states the affected package(s) and bump level in a small file per change, so nothing is inferred from commit messages or git history
- Good, because four of the five defects (1, 2, 3 and 5) become structurally not applicable instead of needing a patch
- Bad, because defect 4 (broken links) still needs a custom fix, the same as Option A
- Bad, because it requires a workflow change (a changeset file per PR) enforced only by a PR-template checklist and reviewer responsibility, and a full rewrite of the release configuration
- Bad, because the retired `.release-it.json` files, the custom `headerPattern` and the coupling of `check-cem-changes.ts` to `.release-it.json` would have to be removed completely

## Consequences

- Whichever option is chosen, the existing published `CHANGELOG.md` history needed remediation, in three tiers: (1) required, low effort: rewrite already-broken commit and compare links to the correct Bitbucket Server URL scheme; (2) recommended, medium effort: de-duplicate near-identical cross-package entries; (3) optional, high effort: editorial cleanup of low-signal entries that leaked in under the previous tooling.
- Whichever option is chosen, enforcement of the PR-level convention (title format for A, changeset-file presence for B) has no automated backstop. Both rely on a PR-template checklist and reviewer discipline. BEEQ has the same gap for its own PR-title convention.
- Wrapper pin drift is controlled operationally by making the web-components stack orchestration the default (`boreal-web-components` followed by both wrappers). If teams bypass it and release a wrapper selectively outside the documented exceptions, the drift risk returns and needs additional manual safeguards.
- Releases are manual and in batches, and each package takes one bump from all its commits since its last release, set by the highest level among them.
- npm's staged publishing can hold a publish, and `release-it` does not wait for it, so a tag can exist before its version is installable (see the release guide).

## Component Library Impact

- **Breaking change:** No for the library's API. The packages moved from `@telesign/boreal-*` to `@pxglobal/boreal-*`, which consumers must adopt by changing the package names.
- **Versioning:** Plain `0.x` versions starting at `0.14.0` under the `latest` dist-tag; alpha is a stated status instead of a version suffix. While below 1.0, a breaking change bumps the minor version (`preMajor`) and no commit reaches 1.0 on its own; graduation to `1.0.0` is a deliberate release. A package with no releasable commit since its last tag is not released.
- **Accessibility impact:** None identified
- **Migration path for consumers:** Install `@pxglobal/boreal-*` instead of `@telesign/boreal-*`. The old `@telesign` versions are deprecated, not unpublished, and each deprecation message names the new package. Install without a tag; the `alpha` tag no longer exists.

## Compliance / Validation

- Breaking changes must carry the `!` in the pull-request title; Bitbucket writes the squashed commits indented, and `release-it` ignores a `BREAKING CHANGE:` line inside that list
- Releases run from the `release/current` branch, from a maintainer's machine, with the procedure in the Publishing & Deployment Guide and `RELEASING.md` in the repository
- Tooling and documentation commits that touch package folders use a non-releasing type (`build`, `chore`, `docs`, `test`, `ci`)
- Release commands are unsupported on Windows (verification bypassed 2026-10-08, risk accepted)
- Verified in two real releases: `0.14.0` (2026-10-09, all four packages) and `0.14.1` (2026-10-13, web-components published from a teammate's machine, React and Vue after a TLS fix); the compare-link hook produced a working link on the second

## Implementation outcome (2026-10-08)

Corrections to the context above, re-verified against `release/current`:

- Defect 1: there are 8 `Pull request #N:` squash commits, 5 of them carrying user-facing changes that were missing from the changelogs (6 entries were backfilled). The 19-commit loss first estimated for `bds-table` v3/v4 was overstated: v4 landed as a conventional commit and is in the changelog. The other 103 `Pull request #` commits are true merges whose branch commits parse normally.
- The Bitbucket Server project key is `DEV`: commits live at `/projects/DEV/repos/boreal-ds/commits/<hash>`.

What Option A became in practice:

| Defect | Resolution |
| --- | --- |
| 1 Squash titles | Custom `parserOpts` (`headerPattern`, `breakingHeaderPattern`) accept the `Pull request #N:` prefix and strip ticket IDs |
| 2 No path scoping | `commitsOpts.path` (bump) and `gitRawCommitsOpts.path` (changelog) per package; web-components also counts style-guidelines, wrappers also count web-components |
| 3 Version never escalates | `preMajor` (breaking → minor, no commit reaches 1.0 alone). `strictSemVer` was used while on `-alpha.N` and removed with the suffix |
| 4 Broken links | `context` block (the preset dropped `commitUrlFormat`), `repository` field removed from the four manifests, about 2,560 historical links rewritten |
| 5 Wrapper pin drift | pnpm-native orchestration (`release:wc-stack`, `release:all`) plus a `prerelease` hook on each wrapper running `validate:pack:*`; no new dependency (Turborepo and `npm-run-all2` were compared and rejected) |
| New: empty releases | A package is skipped when it has no releasable commit since its last tag |
| New: compare links | A hook links each new changelog heading to the Bitbucket compare page between the previous and the new tag |

Also done: Node 22.23.3, pnpm 11.28.2, `release-it` 21.1.0, `@release-it/conventional-changelog` 12.0.2, commitlint 21; two maintained changelogs (web-components and style-guidelines) with pointers from React and Vue and a Storybook "What's new" page; `CONTRIBUTING.md` and `RELEASING.md`; the folder renamed `boreal-style-guidelines`.

**Scope move:** the packages moved to `@pxglobal` (`@proximus` was taken), starting at plain `0.14.0` under `latest`. `@telesign/*` is deprecated (not unpublished); its tags are kept, and `git.tagMatch` makes the first `@pxglobal` changelog start at the last `@telesign` tag. Revisit trigger 3 was evaluated when the move was planned (2026-10-02): Option A was kept, and changesets remains the documented alternative.

**First real release (2026-10-09):** the four packages were published at `0.14.0` under `@pxglobal` with `latest`, tagged and pushed, and verified (wrapper pins, changelogs, tarballs, default install). npm's staged publishing held each publish for a browser approval and created a `0.0.0-stage` placeholder per new package, which were then deprecated; `release-it` did not wait for the approval, so the tags were pushed up to about two minutes before the versions were installable. All 44 `@telesign` versions were deprecated, and Storybook was redeployed.

**Second release (2026-10-13):** web-components `0.14.1` published from a teammate's machine with a granular token with bypass 2FA (a validating state of some minutes, no approval), then React and Vue `0.14.1`. The release exposed the authentication and TLS-proxy issues now documented in the release guide.

## Links / Related Decisions

- ADR-0011: Adopt release-it for Independent, Dependency-Ordered Package Releases with Pre-Publish Pack Validation (amended by this ADR)
- ADR-0012: Enforce Conventional Commits via Commitlint, Husky, and Commitizen
- ADR-0008: Use Jenkins with a Two-Stage Environment Strategy for CI/CD
- ADR-0009: Layered Package Architecture (Style Guidelines → Web Components → Framework Wrappers)
- Jira: EOA-18749 (release process hardening), EOA-18867 (stable package strategy), EOA-18870 (DevOps meeting, CI/CD access)
