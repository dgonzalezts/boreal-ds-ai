# ADR 0019 — Dependency maintenance policy

**Date:** 2026-10-16
**Status:** Accepted on 2026-10-30. Amended on 2026-11-13 (EOA-20193): see "Amendment 1" and the notes marked 2026-11-13.

---

## Context

Boreal DS has no automation for dependency updates: no Renovate, no Dependabot, and no `.github/workflows`. Updates and vulnerability fixes happen ad hoc. Snapshot taken 2026-10-16:

- `pnpm outdated -r`: 83 entries (30 major, 42 minor, 11 patch). Majors include `typescript`, `vite`, `vitest` and `@vitest/*`, `jest`/`jest-cli`/`@types/jest`, `eslint`/`@eslint/js`, `puppeteer`, `chromatic`, `@chromatic-com/storybook`, `jsdom`, `lint-staged`, `chalk`, `execa` and `npm-run-all2`.
- `pnpm audit --prod`: 27 vulnerabilities (3 low, 7 moderate, 17 high). One example is `dompurify`, reached through `web-components`. Re-run on 2026-10-28 during the triage: 29 (4 low, 7 moderate, 17 high, 1 critical), because a new critical `dompurify` advisory and one low one had been published.
- Full `pnpm audit`: 155 vulnerabilities (14 low, 50 moderate, 82 high, 9 critical), including dev tooling.
- `caniuse-lite` 1.0.30001769 is about 9 months old. Every `web-components` build prints a Browserslist warning, and the repository has no browserslist config.
- Existing safeguards: pnpm `minimumReleaseAge` (default 1440 minutes, 1 day, as documented for pnpm 11; the pnpm 12 default is not re-verified, and `pnpm config get` does not show it) and the `allowBuilds` allow-list in `pnpm-workspace.yaml`. Since pnpm 12 an install also prints "Lockfile passes supply-chain policies"; which policies it enforces is not verified.
- Result after EOA-20193 (2026-11-13, state of the working branch; its pull request was open and pending approval): `pnpm outdated -r` 31 entries (11 major, 9 minor, 11 patch); `pnpm audit --prod` 1 moderate finding, accepted (Amendment 1, item 2), and no high or critical; full `pnpm audit` 72 (6 low, 25 moderate, 37 high, 4 critical).

Constraints:

- Dependabot works only on GitHub, so it cannot be used on Bitbucket Server.
- Renovate supports `platform=bitbucket-server` when self-hosted, using an HTTP access token for a bot account (docs.renovatebot.com/modules/platform/bitbucket-server). Limitations: no assignees, no labels, no issue creation (so no config-error issues), and `automergeStrategy` is not implemented.
- Mend for Bitbucket Data Center exists as a self-hosted option.
- A bot account and token need DevOps approval. That approval is not assumed.

## Decision

Adopt a dependency maintenance policy, rolled out in phases.

1. **Cadence.** A monthly dependency maintenance window, tracked as a recurring ticket. Security fixes happen outside the schedule.
2. **Triage.** Security findings rated high or critical are fixed within 2 weeks, with runtime and published dependencies ahead of dev tooling. Patch and minor updates are batched in one PR per window. Every major update gets its own PR and ticket per tool family: test tooling, lint, Vite/Storybook, TypeScript, Chromatic, utilities. When a backlog of majors has built up, they may be delivered as one consolidated catch-up PR with one commit per task and one ticket with a sub-task per family (EOA-20193 did this for about 20 majors); security fixes are never part of it (Amendment 1, item 5).
3. **Product-critical dependencies.** Stencil, Storybook, TypeScript, Node, pnpm and release-it require a changelog review and `validate:pack`.
4. **Gates before merge.** Lint, unit tests (at least 80% coverage), `pnpm peers check`, the Storybook build and `pnpm validate:all`. Run `pnpm validate:all` after committing: it restores the wrapper and test-app manifests and the lockfile to the committed state on exit, so it discards uncommitted edits to them. After each commit, check that the commit holds the lockfile change (`git show HEAD:pnpm-lock.yaml`) and that `pnpm install --frozen-lockfile` passes, before validating and pushing: `validate:all` does not catch a lockfile missing from a commit (it happened twice in EOA-20193). Majors of published dependencies also need a release-it dry run; a dry run prints the `before:init` hook without running it, so it validates configuration, proposed versions and the changelog, not the build. A gate that cannot run in CI (for example Windows, or the company-network certificate for publishing) is named in the PR description with an owner and a deadline (before adoption or before the next release).
5. **Wrapper peer-dependency ranges.** A change to the React or Vue peer-dependency range is a public contract change and is treated as `feat` or breaking under the conventional-commit rules.
6. **Tooling phases.**
   - Phase 1: recurring ticket plus manual `pnpm outdated -r` and `pnpm audit --prod`.
   - Phase 2: scheduled Jenkins job, as part of the single multi-stage job, reporting outdated packages and audit results.
   - Phase 3: self-hosted Renovate in Jenkins, subject to DevOps approval.
7. **Browserslist data.** Refresh the data in each window with `pnpm update -r --lockfile-only --depth 9999 caniuse-lite baseline-browser-mapping`; `npx update-browserslist-db@latest` changes nothing under pnpm 11 (not re-checked on pnpm 12). `minimumReleaseAge` can hold back a release younger than one day. The Browserslist warning printed by the `web-components` build comes from data bundled inside `@stencil/core`, so Stencil updates clear it, not this command.
8. **Runtime review.** Review Node and pnpm quarterly. The pnpm 12 upgrade is done (12.18.0, pinned through Corepack on 2026-11-13). The Node upgrade is next: target 26 with 24 as the fallback (decision of 2026-11-11); the root `engines.node` is `^22.22.2 || ^24.15.0 || >=26.0.0` (the highest floor among the build and hook utilities).
9. **Supply-chain safeguards.** Keep `minimumReleaseAge` and `allowBuilds`. Consider `trustPolicy` no-downgrade and `blockExoticSubdeps` as a follow-up, verified against https://pnpm.io/supply-chain-security. To be confirmed (2026-11-13: still open).

## Amendment 1 — 2026-11-13 (EOA-20193)

Rules that the dependency catch-up of EOA-20193 showed to be missing. The procedures that go with them are in the monthly ticket template.

1. **Hold register.** A package that cannot be updated is held with an explicit range cap in its manifest (a hold kept only in the lockfile does not survive re-resolution) and a row in the hold register: version held, latest, reason, how to re-test, next review. Every hold is re-tested in each window. A major that is blocked by another family stays a hold with the unblocking task named (Jest and Puppeteer wait for the test runner migration, and Stencil 5 waits for that migration).
2. **Accepted findings.** A production finding whose chain has no published fix, or whose fix would force an untested major into a code generator, may be accepted with a recorded reason (path, who executes the vulnerable code, the upstream block) and a re-check trigger. A pnpm `overrides` entry only changes this workspace's lockfile: it never reaches the installs of consumers of a published package, so it is not a fix for a finding inside a runtime dependency of a published package. EOA-20193 accepted one moderate `minimatch` finding this way (through `@stencil/react-output-target`, which `boreal-react` ships as a runtime dependency).
3. **Runtime dependencies of published packages.** Before bumping one, check its behavior, not only the gates: a differential run of the old and new versions over the surface the code uses, and characterization tests written against the old version first (`@colordx/core` 7 throws on invalid colors where 5 returned a value); a real-browser check when the library touches layout or events (`@tanstack/virtual-core`); a browser smoke test of a wrapper when a wrapper runtime library or generator changes.
4. **Pull request typing.** A dependency change that alters what consumers observe is typed under the conventional-commit rules like any other change. Behavior changes of Stencil, of a runtime dependency or of a wrapper (for example how attributes are parsed, or what a `v-model` binds) are breaking: the PR title carries the `!` and the merge message ends with an unindented `BREAKING CHANGE:` footer. A squash merge leaves one changelog line per PR, so the detail lives in the description and the footer.
5. **Security fixes ship separately.** Production audit fixes and minor updates go in their own PR and are merged and releasable before any major catch-up PR, so a breaking change never delays them and a revert never takes them with it.
6. **Version adoption.** Pin the version that the stable dist-tag points to (for pnpm, `latest-12`; newer versions can sit on `next-12`). `minimumReleaseAge` is a floor: for a product-critical tool, defer a release whose notes show cache, hashing, parsing or output changes until it has been used for a window (Turborepo 2.11.11 was deferred at 2 days old for that reason).
7. **pnpm majors.** The lockfile rewrite is its own commit, `peerDependencyRules` entries become `:peer` overrides, and two checks are named in the PR description as gates: install and the pack scripts on Windows (before contributors adopt it), and publishing behind the company proxy (before the next release). TLS behavior changed between pnpm 11 and 12 (pnpm 12 reads `cafile` and ignores `NODE_EXTRA_CA_CERTS`); see `RELEASING.md`.
8. **Release hooks and published output.** A change to what is packed (build output, `dist` folders, exports, generated types) is verified from the packed artifacts: the wrapper `dist` folders are removed in the release hooks (a Turborepo cache hit does not clear them), and the packed web-components package is type-checked by a consumer with `skipLibCheck: false` (drafted as a pipeline guard, not automated yet).
9. **Phase 2 status.** The Jenkins report script is not started; its design is drafted in the EOA-20193 follow-up tickets (exit 0 clean, 1 for unresolved high or critical production findings, 2 when the check could not run or parse).

## Options Considered

- **Dependabot:** rejected. GitHub-only.
- **Renovate now:** deferred. Needs a DevOps-approved bot account and token.
- **Do nothing / ad hoc:** rejected. The backlog and audit counts above are the result.
- **Always-latest with automerge:** rejected. Boreal DS is a published library, and a silent bump can change the public contract.
- **One PR per family, with no exception:** kept as the norm; a large backlog may be delivered as one consolidated catch-up PR (decision 2, 2026-11-13).
- **Chosen:** the phased policy above.

## Consequences

- A predictable monthly workload, and a visible backlog for the majors (30 at the snapshot, 11 after EOA-20193).
- A consolidated catch-up PR keeps the detail in its description and merge message, because the squash leaves one changelog line.
- Phase 1 relies on discipline, with no automated backstop until Phase 2 or 3.
- Major updates split by family add PR overhead but isolate regressions.
- Wrapper peer-range changes can force a minor or major release of `boreal-react` and `boreal-vue`.
- Phase 3 depends on DevOps. Renovate on Bitbucket Server cannot label, assign or open config-error issues, so reviewers must watch the PR list.

## Risks

- DevOps may not approve a bot account or token. The policy stays at Phase 1 or 2 in that case.
- Majors of `typescript`, `vite` and `vitest` may break the Stencil, Storybook or test toolchain. Checked in EOA-20193: TypeScript 6.0.3, ESLint 10 (with a peer override), Vitest 5, Vite 8, Chromatic 18 and the build utilities work. Not adopted: TypeScript 7 (waits for Stencil's bundled compiler and `typescript-eslint`) and Jest 30 (not supported on Stencil 4).
- Held packages accumulate: Jest, `jest-cli`, `@types/jest` and Puppeteer are held until the test runner migration, which also blocks Stencil 5; 19 of the 75 findings of a full audit went through them.
- A pnpm major can change install, lockfile and TLS behavior; Windows and publishing behind the proxy are checked by people, not by CI.
- Audit counts include dev-only findings. Production exposure is lower than the full count suggests.

## Follow-ups

- Done (EOA-19635): create the "Dependency maintenance baseline" Jira ticket and its sub-tasks.
- Done (EOA-20015): update the `caniuse-lite` database and clear the Browserslist warning.
- Done (EOA-20014): triage the 27 production audit findings, starting with high and critical.
- Done (EOA-20193): the dependency catch-up (83 to 31 outdated entries, all six holds of the baseline lifted, pnpm 12). Its pull request was open and pending approval on 2026-11-13.
- Decide on `trustPolicy` and `blockExoticSubdeps`, and verify the pnpm 12 defaults of the supply-chain settings.
- Follow-ups drafted in EOA-20193 (not in Jira): the test runner migration, the Stencil 5 upgrade, the Phase 2 report script, and a strict consumer type check of the packed package. The Confluence copy of this ADR (ADR-0016, page 2412085321, version 6) and of the monthly template (page 2469101953, version 2) were updated on 2026-11-13.
- Evaluate Renovate on Bitbucket Server with DevOps. Owner and date: To be confirmed.

## Related

- Confluence: ADR-0016 - Dependency Maintenance Policy (https://telesign.atlassian.net/wiki/spaces/SENG/pages/2412085321). The numbering differs between the two copies by decision (2026-10-30: left as is).
- Monthly ticket template: `ai-docs/templates/dependency-maintenance-ticket.md`
- `ai-work/plans/EOA-18749-release-process-remediation-patch-release-it.md` (T24 pnpm 12, T26 Node 24)
- `ai-work/plans/EOA-20193-dependency-upgrades-followup.md`, with the follow-up drafts in `ai-work/tickets/EOA-20193-follow-up-tickets.md`
- `RELEASING.md` (certificate section) and `CONTRIBUTING.md` (what counts as a breaking change)
- ADR 0013 — Release tooling: release-it vs. changesets
