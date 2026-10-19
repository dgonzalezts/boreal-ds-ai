# EOA-19635 - Dependency maintenance baseline

## Summary

Establish a dependency maintenance baseline for Boreal DS: clear the current backlog, fix production vulnerabilities, and publish a recurring policy.

## Description

Boreal DS has no automation for dependency updates (no Renovate, no Dependabot, no `.github/workflows`). Snapshot 2026-10-16:

- `pnpm outdated -r`: 83 entries (30 major, 42 minor, 11 patch).
- Majors include typescript, vite, vitest and @vitest/\*, jest/jest-cli/@types/jest, eslint/@eslint/js, puppeteer, chromatic, @chromatic-com/storybook, jsdom, lint-staged, chalk, execa, npm-run-all2.
- `pnpm audit --prod`: 27 vulnerabilities (3 low, 7 moderate, 17 high), for example dompurify under web-components.
- Full `pnpm audit`: 155 (14 low, 50 moderate, 82 high, 9 critical), including dev tooling.
- caniuse-lite 1.0.30001769 is 9 months old; every web-components build prints a Browserslist warning and the repo has no browserslist config.
- Existing safeguards: pnpm 11 `minimumReleaseAge` (default 1 day) and the `allowBuilds` allow-list.

Policy proposal: ADR 0019 (`ai-docs/decisions/0019-dependency-maintenance-policy.md`) and its Confluence copy.

## Goal

Bring the repository to a known, maintained state and put a repeatable monthly process in place.

## Scope

- Production audit triage and fixes.
- Browserslist data update.
- Patch and minor updates.
- Planning of the 30 major updates by family.
- Publishing the policy.
- Evaluating Renovate on Bitbucket Server.

## Out of scope

- Executing the major updates (each gets its own ticket after planning).
- Node 24 and pnpm 12 upgrades (tracked as T26 and T24 in the EOA-18749 plan).
- Dev-only audit findings, unless they block a gate.

## Sub-tasks

### (a) Triage the 27 production audit findings

- List every `pnpm audit --prod` finding with package, path, severity and fix version, starting with high and critical (17 high).
- Include the `dompurify` finding under web-components.

Acceptance criteria:

- High and critical findings are fixed, overridden, or documented as accepted with a reason.
- Moderate and low findings have a recorded decision.
- `pnpm audit --prod` is re-run and the result is attached.

### (b) Update caniuse-lite and fix the Browserslist warning

- Run `npx update-browserslist-db@latest`.
- Decide whether a browserslist config is needed (To be confirmed).

Acceptance criteria:

- The web-components build no longer prints the Browserslist warning.
- Lockfile change is committed with the build green.

### (c) Apply pending patch and minor updates

- One PR covering the 42 minor and 11 patch entries from `pnpm outdated -r`.

Acceptance criteria:

- Lint, unit tests (at least 80% coverage), `pnpm validate:all` and Storybook build pass.
- Product-critical packages (Stencil, Storybook, TypeScript, release-it) have a reviewed changelog and `validate:pack` passes.

### (d) Plan the 30 major updates by family

One sub-task per family; each produces a plan and a follow-up ticket, not the upgrade itself.

- (d1) Test tooling: vitest, @vitest/\*, jest, jest-cli, @types/jest, jsdom, puppeteer.
- (d2) Lint: eslint, @eslint/js.
- (d3) Vite / Storybook: vite.
- (d4) TypeScript: typescript.
- (d5) Chromatic: chromatic, @chromatic-com/storybook.
- (d6) Utilities: lint-staged, chalk, execa, npm-run-all2.

Acceptance criteria (each):

- Exact current and target versions are listed, with breaking changes and compatibility notes.
- An order, effort estimate and gates are defined.
- A ticket exists for the upgrade.

Note: the families cover the majors named in the snapshot; the full list of 30 must be confirmed against `pnpm outdated -r`.

### (e) Publish the policy

Acceptance criteria:

- ADR 0019 is reviewed and its status updated.
- The Confluence page is created from `ai-work/confluence/adr-dependency-maintenance-policy.md` and linked.
- The recurring monthly ticket is created.

### (f) Evaluate Renovate on Bitbucket Server with DevOps

- Review `platform=bitbucket-server` self-hosted requirements and limitations (no assignees, labels or issue creation; `automergeStrategy` not implemented).
- Compare with Mend for Bitbucket Data Center.

Acceptance criteria:

- DevOps has answered on bot account, token and Jenkins hosting.
- A recommendation is recorded: proceed, defer or reject.

## Definition of Done

- All sub-tasks closed.
- `pnpm audit --prod` has no unresolved high or critical findings.
- Pending patch and minor updates are merged; all gates are green.
- Major updates are planned and ticketed.
- Policy is published and the monthly ticket exists.

## Risks

- Major updates (typescript, vite, vitest) may break the Stencil or Storybook toolchain.
- DevOps may not approve a bot account or token, which blocks automation.
- Fixes for production vulnerabilities may require major bumps of transitive packages.

## Dependencies

- T24 (pnpm 12) and T26 (Node 24) from the EOA-18749 plan.
- DevOps: bot account, token and Jenkins job for the Renovate evaluation.

## Suggested labels

`dependencies`, `security`, `maintenance`, `tooling`, `technical-debt`
