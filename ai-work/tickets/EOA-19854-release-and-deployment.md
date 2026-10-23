# EOA-19854 — release-and-deployment

**Ticket:** [EOA-19854](https://telesign.atlassian.net/browse/EOA-19854) — Release and Deployment (standing ticket)
**Goal:** Publish every package with releasable changes to npm under `@pxglobal`, push the release commits and tags to `release/current`, deploy the updated Storybook, validate it, and notify the team.

Jira holds the published text. This file mirrors it, with working checkboxes. Update Jira first, then this file.

Procedure sources: `RELEASING.md` (source of truth) and the Confluence guide [Boreal CL - Publishing & Deployment Guide](https://telesign.atlassian.net/wiki/spaces/SENG/pages/1692827661). Only the manual process is in scope.

## Packages in scope

Release order matters, because a wrapper must never be installable before the web-components version it pins:

1. `@pxglobal/boreal-style-guidelines`
2. `@pxglobal/boreal-web-components`
3. `@pxglobal/boreal-react`
4. `@pxglobal/boreal-vue`

## Prerequisites

- Publish access to the `@pxglobal` npm organization. It should already be in place, but confirm it before the release date (`npm whoami`, `npm org ls pxglobal`).
- npm account with 2FA, or a granular token scoped to `@pxglobal` with bypass-2FA enabled.
- Permission to push commits and tags to `release/current`. A protected branch makes the push fail after the package is already published.
- Node trusting the company root certificate on the company network, so React and Vue publish without a `SELF_SIGNED_CERT_IN_CHAIN` error.
- `CHROMATIC_PROJECT_TOKEN` set in the local `.env`. Never commit it.
- Local checkout on `release/current`, up to date and clean, using the Node version from `.node-version`.
- Local tags up to date (`git fetch origin --tags`). A missing tag makes the dry run propose a wrong version.

## Dry run command

Run once per package, replacing `<package>` with `style-guidelines`, `web-components`, `react` and `vue`, in that order:

```bash
pnpm --filter @pxglobal/boreal-<package> exec release-it --dry-run --ci --no-git.requireBranch --no-git.requireCleanWorkingDir --no-git.requireUpstream --no-npm.publish
```

## Tasks (per release cycle)

- [ ] Announce in the team channel that a release is starting, and check that no other release is running.
- [ ] Run `pnpm install --frozen-lockfile`.
- [ ] Dry run each package with the command above.
- [ ] Compare the version proposed by each dry run (the `npm version <version>` line) with the current `version` in the package's `package.json`. Check that the bump matches the highest commit level since the package's last tag (breaking, `feat`, `fix`), and that packages without releasable commits print "No new version to release". If a version looks wrong, find the commit that caused it before continuing.
- [ ] Release with `pnpm release:all`.
- [ ] Wait for each publish to become installable: approve the staged packages in dependency order, or wait for validation if a token is used. Check with `npm view <package>@<version> version`.
- [ ] Complete the verification checklist in the acceptance criteria.
- [ ] Deploy Storybook with `pnpm deploy:docs`.
- [ ] Validate the Storybook "What's new" page: the content matches the released versions and changelog entries, and every generated link opens the right destination (no 404s, no links to internal or non-existent pages).
- [ ] Notify the team in the Teams channel (see "Team notification").
- [ ] Record the released versions in a comment on this ticket.

## Team notification

Post in the Teams channel once the release and Storybook validation are complete. The message includes:

- Published version of each released package (and which packages were skipped as "No new version").
- Storybook link, and the link to the "What's new" page.
- Action required: update local `release/current` (`git switch release/current && git pull && git fetch origin --tags`). Branches that sync from it need to be rebased or merged.
- Release commits and tags pushed (`chore(release)` and `@pxglobal/<package>@<version>`).
- Breaking changes included in the release, if any, with a pointer to the changelog.
- Known issues or follow-ups found during verification, if any.
- A link to this ticket.

## Acceptance criteria

- [ ] Every staged version is approved, and nothing is left in `npm stage list`.
- [ ] `npm view @pxglobal/boreal-<package> version dist-tags` shows the new version as `latest` for every released package.
- [ ] For every released package, the `version` in `package.json`, the version on npm (`latest`) and the tag `@pxglobal/<package>@<version>` are the same.
- [ ] The React and Vue packages pin `@pxglobal/boreal-web-components` at an exact version, not `workspace:*`.
- [ ] The tags `@pxglobal/<package>@<version>` and the `chore(release)` commits are on Bitbucket.
- [ ] The web-components and style-guidelines changelogs have a new section with working Bitbucket links.
- [ ] A scratch project installs the new packages from npm and builds.
- [ ] Storybook is deployed, and the Welcome page shows the new version.
- [ ] The "What's new" page shows the content for the new version, and every link on it works.
- [ ] The Teams notification is posted with all the items listed under "Team notification".

## Risks and notes

- Publish happens before commit, tag and push. If the push fails after a publish, do not release that package again. Run `git push --follow-tags origin release/current` and continue.
- Never `npm unpublish`. For a wrong version, deprecate it and release a corrected patch.
- Breaking changes need the `!` in the PR title, for example `feat(scope)!: …`. Without it the change is released as a plain feature.
- Forced versions (`--increment`) stop `release:all` at the first package already at that version. Release the remaining packages one at a time in that case.
- Failures: see the "When something goes wrong" table in `RELEASING.md`. After any interruption, read `git status`, `git log -3` and `npm view <package> version` before running anything again.

## References

- `RELEASING.md` in the `boreal-ds` repository
- Boreal CL - Publishing & Deployment Guide (Confluence, SENG space)
