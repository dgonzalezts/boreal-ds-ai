# ADR 0013 — Release tooling: release-it vs. changesets

**Date:** 2026-08-12
**Status:** Proposed

---

## Context

The original 2026-05-19 plan (`EOA-9609-automated-changelog-&-rp.md`) replaced a prior Changesets setup with `release-it` + `@release-it/conventional-changelog`, recording only: "Changesets fully removed (no fallback)" — no comparative analysis, no stated reason (verified by reading that plan's full Context section, not just a keyword search; the session summary and `ai-work/research` add nothing further). A 2026-08-12 audit of the resulting release process found five real defects, several structural to how `release-it` + conventional-commit parsing behave in a monorepo:

1. **Squash merges break changelog/version generation.** Bitbucket Server squash commits (e.g. `d3bb6f51` "Pull request #166...", `fab67bea` "Pull request #159...") have subject lines that don't match the `headerPattern` any `.release-it.json` uses, so `@release-it/conventional-changelog` silently drops them. 19+ `feat`/`fix` commits for `bds-table` v3/v4 are invisible in every changelog and never counted toward version bumps.
2. **No per-package path scoping.** All four `.release-it.json` files scan the full git log since their own last tag with no path filter — why `boreal-web-components`, `boreal-react`, `boreal-vue` changelogs are byte-for-byte identical for shared entries.
3. **Version base (`0.1.0`) never escalates**, independent of merge strategy. `release-it`'s "continuation" logic (`semver.inc(latestVersion, 'prerelease', 'alpha')`) triggers once a version's prerelease id already matches the configured `preReleaseId`, and this **ignores** the bump level conventional-changelog recommends. This directly violates the team's own documented standard (`ai-docs/guidelines/development-standards.md` §6.2: `feat`→MINOR, `fix`→PATCH) — confirming this is a real defect, not a debatable trade-off.
4. **Every commit link in every CHANGELOG.md is broken.** `@release-it/conventional-changelog`'s built-in "Bitbucket" URL formatter assumes Bitbucket Cloud, not self-hosted Bitbucket Server (this repo's actual host), which uses a different path scheme (`/projects/<KEY>/repos/<slug>/commits/<hash>`). `package.json` `repository.url` is also inconsistent across packages, and `boreal-web-components`'s is still the literal leftover Stencil-starter placeholder.
5. **Wrapper dependency-pin drift.** Confirmed directly (`pnpm pack` + tarball inspection): `boreal-react`/`boreal-vue`'s `"@telesign/boreal-web-components": "workspace:*"` gets replaced with a hard-pinned exact version at publish time. If `boreal-web-components` releases and the wrappers don't (correct behavior once path-scoping/#2 is fixed, since they'd have no own commits), their published tarballs keep pointing at the stale pinned version indefinitely — nothing currently detects or fixes this.

Two suspected issues were ruled out: `boreal-styleguidelines`'s "staleness" (zero commits touched it since its last tag — no release due) and the `0.1.0-alpha.N` scheme's shape (a legitimate pre-1.0 convention; only its lack of graduation, #3, is broken).

**Precedent check — Endava's BEEQ (`ai-docs/lib/endava-beeq.txt`, Nx-based, `@beeq/core@1.9.0`, actively maintained):** its `nx.json` uses an explicit `type → changelog title + semverBump` table and `[skip ci]` release commits — a cleaner single-tool architecture worth borrowing ideas from without adopting Nx itself. But even BEEQ doesn't fully automate the trigger step: only two GitHub Actions workflows exist in the dump, and `publish.yml` fires on `release: types: [published]` — the actual `nx release version`/changelog-writing step runs manually/locally, same as Boreal DS today. BEEQ's `CONTRIBUTING.md` also mandates "always use Squash and merge" with a Conventional-Commit-formatted PR title, with no CI bot found enforcing that title format. Conclusion: Boreal DS's current manual-trigger and written-convention reliance aren't unusually primitive.

**Turborepo integration — verified directly against both tools' official docs:** TurboRepo's publishing guide never mentions release-it and gives equally shallow Turborepo-specific integration advice for either tool (a `turbo build` pre-step, no deep plugin, no dependency-graph-aware task type). Release-it's own official monorepo recipe confirms the same shallow pattern and points to `@release-it/bumper` for dependency auto-bumping — but release-it's own maintainer explicitly states "I did not test this with the conventional-changelog plugin," the exact plugin combination this repo needs. The differentiator is not Turborepo integration depth (equal for both) — it's that changesets' dependent-bumping (`determineDependents`, confirmed directly in its source) is a tested, first-class feature, while release-it's equivalent is an explicitly-unverified plugin combination.

## Options Considered

### Option A — Patch `release-it` in place
See `ai-work/plans/AI-003-release-process-remediation-patch-release-it.md`. Keep the current tool; add a version-bump-escalation wrapper, path-scoped changelog config, a Bitbucket Server URL formatter override, and either `@release-it/bumper` (spike required, untested combination) or a custom script for wrapper dependency-pin drift. Lower migration cost; each fix is a bespoke patch layered onto three separately-glued tools.

### Option B — Migrate to `changesets`
See `ai-work/plans/AI-003-release-process-remediation-migrate-changesets.md`. Matches TurboRepo's own documented recommendation. A human explicitly authors a small file per change stating affected package(s) and bump level — nothing inferred from commit messages or git history. Four of the five defects (#1, #2, #3, #5) become structurally not-applicable rather than requiring a patch. Only #4 (broken links) still needs a custom fix, same as Option A. Requires a workflow shift (a changeset file per PR, ideally CI-bot-enforced, which the repo doesn't have yet) and a full rewrite of the release configuration.

## Decision

Pending — see both linked plans for fully-speced task lists. Update this ADR's Status to `Accepted` and fill in the chosen option once decided.

## Consequences

- Whichever option is chosen, the missing `bds-table` v3/v4 changelog history must be manually backfilled — neither tool can retroactively reconstruct it.
- Whichever option is chosen, enforcement of the PR-level convention (title format for A, changeset-file presence for B) is a manual-discipline risk until CI exists — BEEQ has the same gap for its own PR-title convention.
- If Option A: revisit this ADR if the `@release-it/bumper` spike fails, since the fallback custom script is unaudited, ongoing maintenance surface.
- If Option B: the retired `.release-it.json` files, custom `headerPattern`, and `check-cem-changes.ts`'s coupling to `.release-it.json` must be fully removed, not left as dead config.
