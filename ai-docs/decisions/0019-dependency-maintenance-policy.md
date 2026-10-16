# ADR 0019 — Dependency maintenance policy

**Date:** 2026-10-16
**Status:** Proposed

---

## Context

Boreal DS has no automation for dependency updates: no Renovate, no Dependabot, and no `.github/workflows`. Updates and vulnerability fixes happen ad hoc. Snapshot taken 2026-10-16:

- `pnpm outdated -r`: 83 entries (30 major, 42 minor, 11 patch). Majors include `typescript`, `vite`, `vitest` and `@vitest/*`, `jest`/`jest-cli`/`@types/jest`, `eslint`/`@eslint/js`, `puppeteer`, `chromatic`, `@chromatic-com/storybook`, `jsdom`, `lint-staged`, `chalk`, `execa` and `npm-run-all2`.
- `pnpm audit --prod`: 27 vulnerabilities (3 low, 7 moderate, 17 high). One example is `dompurify`, reached through `web-components`.
- Full `pnpm audit`: 155 vulnerabilities (14 low, 50 moderate, 82 high, 9 critical), including dev tooling.
- `caniuse-lite` 1.0.30001769 is about 9 months old. Every `web-components` build prints a Browserslist warning, and the repository has no browserslist config.
- Existing safeguards: pnpm 11 `minimumReleaseAge` (default 1440 minutes, 1 day) and the `allowBuilds` allow-list in `pnpm-workspace.yaml`.

Constraints:

- Dependabot works only on GitHub, so it cannot be used on Bitbucket Server.
- Renovate supports `platform=bitbucket-server` when self-hosted, using an HTTP access token for a bot account (docs.renovatebot.com/modules/platform/bitbucket-server). Limitations: no assignees, no labels, no issue creation (so no config-error issues), and `automergeStrategy` is not implemented.
- Mend for Bitbucket Data Center exists as a self-hosted option.
- A bot account and token need DevOps approval. That approval is not assumed.

## Decision

Adopt a dependency maintenance policy, rolled out in phases.

1. **Cadence.** A monthly dependency maintenance window, tracked as a recurring ticket. Security fixes happen outside the schedule.
2. **Triage.** Security findings rated high or critical are fixed within 2 weeks, with runtime and published dependencies ahead of dev tooling. Patch and minor updates are batched in one PR per window. Every major update gets its own PR and ticket per tool family: test tooling, lint, Vite/Storybook, TypeScript, Chromatic, utilities.
3. **Product-critical dependencies.** Stencil, Storybook, TypeScript, Node, pnpm and release-it require a changelog review and `validate:pack`.
4. **Gates before merge.** Lint, unit tests (at least 80% coverage), `pnpm validate:all` and the Storybook build. Majors of published dependencies also need a release-it dry run.
5. **Wrapper peer-dependency ranges.** A change to the React or Vue peer-dependency range is a public contract change and is treated as `feat` or breaking under the conventional-commit rules.
6. **Tooling phases.**
   - Phase 1: recurring ticket plus manual `pnpm outdated -r` and `pnpm audit --prod`.
   - Phase 2: scheduled Jenkins job, as part of the single multi-stage job, reporting outdated packages and audit results.
   - Phase 3: self-hosted Renovate in Jenkins, subject to DevOps approval.
7. **Browserslist data.** Run `npx update-browserslist-db@latest` in each window.
8. **Runtime review.** Review Node and pnpm quarterly. T24 (pnpm 12) and T26 (Node 24) from the EOA-18749 plan are the next ones.
9. **Supply-chain safeguards.** Keep `minimumReleaseAge` and `allowBuilds`. Consider `trustPolicy` no-downgrade and `blockExoticSubdeps` as a follow-up, verified against https://pnpm.io/supply-chain-security. To be confirmed.

## Options Considered

- **Dependabot:** rejected. GitHub-only.
- **Renovate now:** deferred. Needs a DevOps-approved bot account and token.
- **Do nothing / ad hoc:** rejected. The backlog and audit counts above are the result.
- **Always-latest with automerge:** rejected. Boreal DS is a published library, and a silent bump can change the public contract.
- **Chosen:** the phased policy above.

## Consequences

- A predictable monthly workload, and a visible backlog for the 30 majors.
- Phase 1 relies on discipline, with no automated backstop until Phase 2 or 3.
- Major updates split by family add PR overhead but isolate regressions.
- Wrapper peer-range changes can force a minor or major release of `boreal-react` and `boreal-vue`.
- Phase 3 depends on DevOps. Renovate on Bitbucket Server cannot label, assign or open config-error issues, so reviewers must watch the PR list.

## Risks

- DevOps may not approve a bot account or token. The policy stays at Phase 1 or 2 in that case.
- Majors of `typescript`, `vite` and `vitest` may break the Stencil, Storybook or test toolchain. Compatibility is To be confirmed per family.
- Audit counts include dev-only findings. Production exposure is lower than the full count suggests.

## Follow-ups

- Create the "Dependency maintenance baseline" Jira ticket and its sub-tasks (`ai-work/tickets/dependency-maintenance-baseline.md`).
- Update the `caniuse-lite` database and clear the Browserslist warning.
- Triage the 27 production audit findings, starting with high and critical.
- Decide on `trustPolicy` and `blockExoticSubdeps`.
- Evaluate Renovate on Bitbucket Server with DevOps. Owner and date: To be confirmed.

## Related

- `ai-work/plans/EOA-18749-release-process-remediation-patch-release-it.md` (T24 pnpm 12, T26 Node 24)
- ADR 0013 — Release tooling: release-it vs. changesets
