---
ticket: EOA-18870
status: in progress
created: 2026-10-19
updated: 2026-10-19
---

# CI/CD Pipeline and Release Automation (work in progress)

> Work in progress. Tasks are not detailed yet: DevOps is building the first version of the pipelines, and the conversations continue once it exists. This plan collects what moved out of the EOA-18749 plan so that plan can close.

**Goal:** Automate quality checks and the package release in Jenkins, publishing to CodeArtifact first. CodeArtifact replaces the public npm registry as the publishing target once the pipeline is implemented by DevOps. Until then, releases stay manual (`RELEASING.md`).

**Parent plan:** [`EOA-18749-release-process-remediation-patch-release-it.md`](./EOA-18749-release-process-remediation-patch-release-it.md) (T14, T15, T28; agenda in "T14 agenda" and "Follow-up meeting")

## Decisions already taken (meeting 2026-10-16)

- CodeArtifact is the internal sharing registry. Versions are the same as today; no prerelease scheme, no change to `preMajor`, `strictSemVer` or changelog rules.
- Direction confirmed 2026-10-19: CodeArtifact replaces public npm as the publishing target, but only once DevOps has implemented the pipeline. Until then the manual release in `RELEASING.md` stays valid.
- One Jenkins job with several stages (quality, lint, tests, build, release). How much fits in Q4 depends on complexity.
- Out of Q4: Storybook deployment (stays manual with `pnpm deploy:docs` and Chromatic), S3 bucket provisioning for static assets, and the CDN upload.

## Progress

| Task | Description | Status |
|---|---|---|
| P1 | Wait for DevOps' first pipeline version and agree the stage order (ITOPS-63109, 63110, 63111, 72071; CodeArtifact publish ITOPS-72204) | pending (blocked on DevOps) |
| P2 | Answer the open follow-up questions: credentials for CodeArtifact and git, read access and origin controls for `@pxglobal/*` (dependency confusion), `.npmrc` at run time vs template, test repository for a `--dry-run --ci` rehearsal, failed-publish ownership and rollback | pending |
| P3 | Configure the codebase for CodeArtifact: `.npmrc` written by Jenkins (no URL hardcoded in the four `package.json`), `npm.skipChecks: true` in the four `.release-it.json`, verify with `release-it --dry-run --ci` on the Linux agent | pending (after P1, P2) |
| P4 | PR-title validation and squash-only merges in Bitbucket, requiring `!` for breaking changes (agenda item 1) | pending |
| P5 | Former T15: CI gate that fails when React or Vue wrappers cannot be generated from web-components, plus a drift smoke test (EOA-18749 AC 3-4). Runs `pnpm validate:all` and the CEM breaking-change report on every PR | pending (blocked on pipeline access) |
| P6 | Release job on `release/current`: manual trigger or approval gate, service account allowed to push the release commit and tags, full clone with tags, `[skip ci]` in release commits, `release:all --ci` | pending |
| P7 | Fill the "Release from Jenkins" section of `RELEASING.md` (trigger, credential, approval, job requirements, re-run) and update the authentication sections that assume public npm | pending (after P6) |
| P8 | Former T28: replace the two embedded diagrams on the Confluence page "CI/CD Pipeline Strategy for Proximus Global Component Library" (SENG 1303773297) with `ai-docs/diagrams/pxg-ci-diagram-v3.md` and `pxg-cd-diagram-v3.md`, after P1 and P6 settle the runner, credential and approval step | pending |
| P9 | Jenkins agent checks: Node version and policy (feeds the Node 24 ticket), Corepack and pnpm support (feeds the pnpm 12 ticket), Windows agent for the Windows checklist, Linux agent OS | pending |
| P10 | Update ADR-0015 (repo ADR 0013) when the revisit trigger fires: Jenkins pipeline live, or promotion to public npm decided. Also decide when to publish to public npm and in which order if both registries are used | pending |
| P11 | Revoke the owner's one-off npm token and set the interim backup publisher once the pipeline publishes; keep 2FA on every `@pxglobal` member | pending |

## Related tickets

- Jira: EOA-18870 (DevOps meeting), ITOPS-63109, 63110, 63111, 63144, 72071, 72203, 72204, 72205.
- Separate tickets: dependency baseline EOA-19635; Node 24 and pnpm 12 upgrades; pack cleanup (`validate:pack`); browser build for the Library CDN. Drafts in `ai-work/tickets/EOA-18749-followup-tickets.md`.

## Close-out

Done when P1-P11 are completed or re-scoped into their own tickets with the user's confirmation.
