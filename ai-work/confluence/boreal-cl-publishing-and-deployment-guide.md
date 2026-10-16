# Boreal CL - Publishing & Deployment Guide

# Overview

This guide covers the recurring release workflow and the Storybook deployment process for the Boreal Design System monorepo. It is intended for all team contributors who need to cut a release or publish updated documentation.

Packages are public on npm under the `@pxglobal` organization and are released on plain `0.x` versions: alpha is a stated status of the library, not a version suffix or a dist-tag. The old `@telesign/boreal-*` packages are deprecated, and each version says where the package moved.

The release procedure is also maintained in the `RELEASING.md` file at the root of the `boreal-ds` repository (the versioning and commit rules are in `CONTRIBUTING.md`). If this page and `RELEASING.md` ever differ, `RELEASING.md` wins.

# Stakeholders

| **Name** | **Role** |
| --- | --- |
| @Daniel Cubides | Engineering Manager |
| @JP Benedict | Sr Mgr Product Management |
| @Santiago Vergez (Deactivated) | Product Owner |
| @Daniel Ceron | Release Engineer |
| @Fernando Yara | Software Engineer |
| @Jhoy Berrocal | Senior Frontend Developer |
| @Gary Choque | Software Engineer |
| @Mateo Aponte | Software Engineer |
| @Laura Cuellar (Deactivated) | Software Engineer |

# Packages in Scope

| Package | npm name | Role |
| --- | --- | --- |
| Style Guidelines | `@pxglobal/boreal-style-guidelines` | Design tokens and base CSS |
| Web Components | `@pxglobal/boreal-web-components` | Stencil component library |
| React wrapper | `@pxglobal/boreal-react` | React-native bindings |
| Vue wrapper | `@pxglobal/boreal-vue` | Vue-native bindings |

**Tooling stack:** `release-it` orchestrates versioning, changelogs, git tagging, and npm publish. `Turborepo` manages the build graph. `pnpm workspaces` handles inter-package dependencies. `Chromatic` hosts the Storybook documentation site.

# TL;DR - Quick Reference

For contributors already familiar with the process:

```bash
# Pre-conditions
fnm use
pnpm install --frozen-lockfile
npm whoami && npm org ls pxglobal
git switch release/current && git pull && git status --short

# Dry run of one package (changes nothing)
pnpm --filter @pxglobal/boreal-web-components exec release-it --dry-run --ci \
  --no-git.requireBranch --no-git.requireCleanWorkingDir --no-git.requireUpstream --no-npm.publish

# Release
pnpm release:all          # every package, in dependency order
pnpm release:wc-stack     # web-components, then react and vue
pnpm release:styles       # style-guidelines only

# Verify
npm view @pxglobal/boreal-web-components version dist-tags

# Deploy Storybook
pnpm deploy:docs   # requires CHROMATIC_PROJECT_TOKEN in .env
```

**Shortcut - release all packages + deploy in one command:**

```bash
pnpm release:publish   # release:all, then deploy:docs
```

A package with no releasable commit since its last tag prints "No new version to release" and is skipped, so `release:all` is safe to run when only some packages have changes.

# Versioning

## Version number anatomy

```
0  .  14  .  1
│      │     └── patch
│      └──────── minor
└─────────────── major (0 = not yet stable)
```

There is no pre-release suffix and no counter: every release is a normal version. The bump is derived from the conventional commits since the package's own last tag:

| Commits since last tag | Version bump (while below 1.0) | Example |
| --- | --- | --- |
| `fix:`, `perf:`, `revert:` | patch | `0.14.0` → `0.14.1` |
| `feat:` | patch | `0.14.0` → `0.14.1` |
| `BREAKING CHANGE:` footer or `!` after the type | minor; never moves the library to 1.0 on its own | `0.14.1` → `0.15.0` |
| `build`, `chore`, `ci`, `docs`, `style`, `refactor`, `test` | no release on their own; shipped with the next releasable change | |

Each package takes **one** bump for the whole batch of commits since its last release, set by the **highest** level among them: ten fixes make one patch, and a single breaking commit among them makes the minor bump. Graduation to `1.0.0` is a deliberate release decided by the maintainers (see "Forcing a specific version").

A **breaking change** is any change after which code or styles that work today stop working or behave differently without the consumer changing anything. It must carry the `!` in the pull-request title (`feat(scope)!: ...`): Bitbucket writes the squashed commits into the merge message indented, and release-it ignores a `BREAKING CHANGE:` line inside that list, so without the `!` the change would be released as a plain feature. The full definition and the three questions to ask are in `CONTRIBUTING.md`.

## npm dist-tag: `latest`

All packages are published under the default `latest` tag, configured with `"tag": "latest"` in each package's `.release-it.json`. Consumers install the newest version with:

```bash
npm install @pxglobal/boreal-web-components
```

There is no `alpha` tag any more. Use the default caret range (for example `^0.14.0`) to receive fixes and features automatically; while the library is below 1.0, breaking changes bump the minor version, which that range does not accept automatically.

# Coordinating with the Team

Releasing is a shared, manual operation on a shared branch. A few simple practices prevent the most common coordination failures.

## Before you start

1. **Announce intent** - post a brief message in the team channel (e.g. "releasing WC + react now") so no one merges to `release/current` while your release is in progress.
2. **Check for open PRs** - confirm there are no pending PRs targeting `release/current` that should land before the release. A PR merged between two packages in your sequence will break the push step mid-run.
3. **Pull latest** - run `git pull origin release/current` immediately before starting, not minutes earlier.

## Built-in safety rails

`release-it` enforces two guards in every package's `.release-it.json` that catch common mistakes automatically:

| Guard | What it enforces |
| --- | --- |
| `requireBranch: "release/current"` | `release-it` aborts if you are on any other branch |
| `requireCleanWorkingDir: true` | `release-it` aborts if the working tree has uncommitted changes |

These run at the very start of each release invocation - before any build, version prompt, or publish step.

## Mid-release push conflict

`release-it` commits and pushes to `release/current` after each individual package release, and it publishes to npm **before** it commits, tags and pushes. If a teammate merges between two packages in your sequence, the `git push` for the next package fails with a non-fast-forward error - **after** the npm publish for that package has already succeeded.

**Do not re-run release-it for that package.** The npm publish cannot be undone. Recover the git state only, then continue with the remaining packages. See "Troubleshooting" below.

## Releasing by hand and from a pipeline

A release from a maintainer's machine is how releases are made today. A pipeline-based release is planned (see "Future - CI/CD Pipeline"), and when it exists the manual path stays available for these cases:

| Case | Why the pipeline is not the right tool |
| --- | --- |
| The pipeline is down or blocked (outage, expired credential, no runner) | A release must not depend on one system being healthy |
| An urgent fix | It cannot wait for a trigger, a schedule or a queue |
| Finishing a partial release | One package was published and the next failed; re-running by hand with the fix is the shortest way |
| Forcing a version or special steps | The first stable `1.0.0`, a release candidate or `--increment=...` needs a person's judgement |
| Rehearsals and dry runs | They are local by nature, and they are how release tooling changes are tested before merging |
| Debugging a failed release | Full terminal output on your own machine is easier to work with than job logs |

Do not use it as the routine way to release once a pipeline exists: two releases from the same branch can race and create duplicate release commits and tags. Tell the team and check that no pipeline run is active before you start.

# Prerequisites

## NPM authentication

Publishing needs either 2FA on your npm account or a token that bypasses it. Check your account on npmjs.com, Account, Two-Factor Authentication: it must show "Enabled for authorization and publishing" with a security key or an authenticator app. An emailed login code is not a 2FA factor.

**Option 1: Interactive login (recommended)** - for accounts with 2FA

```bash
npm login --registry=https://registry.npmjs.org
```

After completing the browser prompt, verify your session and your access to the organization:

```bash
npm whoami            # returns your npm username
npm org ls pxglobal   # lists you as a member of the organization
```

Run the release **without** `--ci` so release-it can ask for the approval. Each publish is held until you approve it in the browser with your security key.

**Option 2: Granular token** - for accounts without 2FA, or for unattended runs

Create the token on npmjs.com (granular tokens cannot be created from the command line), then store it in your npm configuration:

```bash
npm config set //registry.npmjs.org/:_authToken=<your-token>
npm whoami  # verify your username is returned
```

| Token setting | Value |
| --- | --- |
| Packages and scopes | Scope `@pxglobal` (not your personal scope), **read and write (publish and stage)** |
| Organizations | No access (the field only covers organization settings, teams and members; it is not needed to publish) |
| Bypass two-factor authentication | **Checked** |
| Expiration | Short |

Afterwards, remove it: `npm config delete //registry.npmjs.org/:_authToken`, revoke the token on npmjs.com and remove the command from your shell history. Never paste a token in a chat, a ticket or a commit, never put it in the repository, and use one token per person.

A token created on the website is **not** installed on your machine until you store it: until then npm sends no valid credentials and answers with `E404`.

**Important:** direct publishing with bypass-2FA tokens ends around January 2027 (npm changelog of 2026-07-08). After that, a publish made with such a token is staged and a person approves it with 2FA. npm's documented alternatives are a stage-only token and trusted publishing from CI.

Both web-components and the wrappers read the same `~/.npmrc`. web-components publishes through npm; React and Vue publish through pnpm.

## Commands to run

Run these checks before starting any release. All must pass.

| Check | Command | Expected result |
| --- | --- | --- |
| Node.js version | `fnm use` | Activates the version from `.node-version` |
| Dependencies | `pnpm install --frozen-lockfile` | Passes |
| npm authentication | `npm whoami` | Your npm username (on `E401`, run `npm login`) |
| Organization access | `npm org ls pxglobal` | Lists you |
| 2FA or token | See "NPM authentication" | 2FA enabled for authorization and publishing, or a token with the settings above |
| Company network | `pnpm view @pxglobal/boreal-react version` | Prints a version (see "TLS error behind the company proxy") |
| Branch | `git branch --show-current` | `release/current` |
| Working tree | `git status --short` | Prints nothing |
| Sync remote | `git pull origin release/current` | Up to date |
| Push rights | Confirm the branch permissions beforehand | You can push commits and tags to `release/current`; a protected branch makes the push fail after the package is published |
| Last tag found | `git describe --tags --abbrev=0 --match '@*/boreal-web-components@*'` | Prints a tag |
| Storybook deploy | `CHROMATIC_PROJECT_TOKEN` in `.env` | Set it yourself; never commit it |

**Note on `fnm use` in scripts:** In non-interactive shells (e.g. CI or the Bash tool), `fnm use` alone does not activate the version. Prefix script commands with `eval "$(fnm env --shell bash)" && fnm use &&`.

Release commands run on macOS or Linux. They are not supported on Windows; use WSL2 or CI. Pass release-it flags directly, without `--` (for example `pnpm release:all --increment=1.0.0`).

# How `release-it` Behaves

Understanding this prevents the most common mistakes.

For each package, `release-it` runs these steps in order:

1. **Build** the package (`before:init` hook, through Turborepo). web-components also runs the custom-elements breaking-change check (`tsx scripts/check-cem-changes.ts`). No manual build step is required.
2. `git fetch`.
3. **Bump the version** and, for web-components and style-guidelines, write the changelog. A hook then links the new changelog heading to the Bitbucket compare page between the previous and the new tag.
4. **`npm publish`**, which npm may hold for your approval or validate for a few minutes (see "Waiting for the publish").
5. `git commit`, `git tag` and `git push --follow-tags`.

Publishing happens **before** the commit, tag and push. The push skips the repository's `pre-push` hook (`--no-verify` in `git.pushArgs`), because the tests already ran on the pull request and a hook failure after the publish would leave a package on npm without its commit and tag.

- `@release-it/conventional-changelog` reads the commits since the package's own last git tag (`git.tagMatch` finds it under any npm scope) to determine the version bump (patch / minor / major) and the content of the `CHANGELOG.md`.
- **A package with no releasable commit since its last tag is skipped.** It prints "No new version to release" and nothing is changed. Releasable commits are `feat`, `fix`, `perf`, `revert` and breaking changes. React and Vue are released when they, or the package they are built from, have a releasable commit.
- Only the changelogs of web-components and style-guidelines exist; React and Vue have none. The wrappers' release commits only change `package.json`.
- The React and Vue packages run a pack validation (`validate:pack:react` / `validate:pack:vue`) as a `prerelease` hook before every attempt, even when the package is then skipped. It takes about a minute each.
- `release-it` does **not wait** for npm: it continues with the commit, tag and push while the new version is still hidden.
- Interactive confirmation prompts (publish, release commit, tag, push) still appear unless `--ci` is passed.

# Package Publishing

## Why release order matters

`@pxglobal/boreal-react` and `@pxglobal/boreal-vue` declare their dependency on `@pxglobal/boreal-web-components` using pnpm's `workspace:*` protocol. At publish time, pnpm replaces `workspace:*` in the tarball with the **exact version currently published on npm**. This means:

- If `boreal-web-components` has unreleased changes, release it first - otherwise react and vue will pin the previous version.
- `boreal-style-guidelines` has no inter-package dependency and can be released at any time, in any order.

**Required order when web-components has changes:**

```
boreal-web-components  →  boreal-react  →  boreal-vue
```

**Run all commands in this section from the workspace root** (`boreal-ds/`). The `pnpm release:*` and `pnpm validate:pack:*` scripts are defined in the root `package.json` and use pnpm's `--filter` flag internally to target each package. Running them from inside a package directory will produce a "missing script" error.

## Dry run (changes nothing)

Check what a release would do before running it, per package:

```bash
pnpm --filter @pxglobal/boreal-web-components exec release-it --dry-run --ci \
  --no-git.requireBranch --no-git.requireCleanWorkingDir --no-git.requireUpstream --no-npm.publish
```

Check the proposed version, the tag `@pxglobal/<package>@<version>` and the changelog preview. If the version is not what you expect, find the commit that caused it before releasing.

## Releasing `@pxglobal/boreal-style-guidelines`

```bash
pnpm release:styles
```

**Verify:**

```bash
npm view @pxglobal/boreal-style-guidelines version dist-tags
# → latest: <new-version>
```

## Releasing `@pxglobal/boreal-web-components`

The `before:init` hook runs two steps before the version is decided:

1. **Build** - `turbo run build --filter=@pxglobal/boreal-web-components`
2. **CEM check** - `tsx scripts/check-cem-changes.ts` generates a Custom Elements Manifest diff report that surfaces breaking API changes automatically

Review the CEM report output before confirming the prompts.

```bash
pnpm release:wc
```

Prompts you will see, in order: confirm publishing (and the 2FA approval request, with an interactive login), then confirm the release commit, the release tag and the push of the changes. The output ends with the "Released @pxglobal/boreal-web-components@<version>" line.

**Verify:**

```bash
npm view @pxglobal/boreal-web-components version dist-tags
# → latest: <new-version>
```

## Releasing `@pxglobal/boreal-react`

A pre-publish artifact validation gate must pass before publishing. It packs a real `.tgz`, installs it into a test app, and runs a production Vite build - catching broken imports and missing exports before they reach npm. It also runs automatically as the `prerelease` hook of `pnpm release:react`.

**Stop if the gate fails. Do not proceed to publish.**

```bash
pnpm validate:pack:react
# Expected: ✅ Pipeline completed successfully — artifact validation passed

pnpm release:react
```

**Verify:**

```bash
npm view @pxglobal/boreal-react version dist-tags
# → latest: <new-version>
npm view @pxglobal/boreal-react@<new-version> dependencies
# → @pxglobal/boreal-web-components at an exact version, not workspace:*
```

## Releasing `@pxglobal/boreal-vue`

Same pattern as react - validation gate first.

**Stop if the gate fails. Do not proceed to publish.**

```bash
pnpm validate:pack:vue
# Expected: ✅ Pipeline completed successfully — artifact validation passed

pnpm release:vue
```

**Verify:**

```bash
npm view @pxglobal/boreal-vue version dist-tags
# → latest: <new-version>
```

## Automated release sequence (`release:all`)

Root scripts combine the per-package steps into a single command:

| Script | What it runs |
| --- | --- |
| `pnpm release:all` | Every package, one at a time, in dependency order (style-guidelines, web-components, react, vue) |
| `pnpm release:wc-stack` | web-components, then react and vue |
| `pnpm release:publish` | Everything in `release:all`, then `deploy:docs` |

The sequence is ordered correctly, the pack validation runs before each wrapper, and `requireCleanWorkingDir` is not an issue because each individual release-it invocation commits and pushes its own changes before exiting.

Packages with nothing to release are skipped, so `release:all` no longer burns a version on packages that have not changed. Interactive prompts still appear for the packages that are released, and you can still read the CEM report from the web-components hook before confirming.

**Use `release:all` for a normal release.** Use the per-package scripts when:

- You want to carefully review the CEM diff for `boreal-web-components` before committing to a publish.
- The team is actively merging to `release/current` - a push conflict mid-chain is harder to recover from, so releasing one package at a time makes it easier to track which ones were published.
- You are forcing a version with `--increment` (see "Forcing a specific version").

**Recovery if `release:all` fails mid-sequence:**

npm publish cannot be undone. Check which packages were published (`npm view <package> version`) and read `git status` and `git log -3`. Without `--increment`, running `pnpm release:all` again is safe: finished packages are skipped and only the remaining ones are released.

## Waiting for the publish

`release-it` does not wait for npm. Before starting the next package, run `npm view <package>@<version> version` until it prints the version. What you see depends on how you authenticate:

- **Interactive login:** npm holds the publish for a maintainer's approval ([staged publishing](https://docs.npmjs.com/staged-publishing)). It prints a link, and the version becomes installable after you approve it in the browser with your security key (or with `npm stage approve` on npm 11.15 or newer).
- **Token with bypass 2FA:** the version stays in a validating state for a few minutes and then becomes available, with no approval.

If a publish is held:

- Approve the packages in dependency order (style-guidelines, web-components, React, Vue), so a wrapper is never installable before the web-components version it pins.
- Verify only after every approval; until then `npm view` does not show the new version.

## Forcing a specific version

The version normally comes from the commits. To set it explicitly, for example for the `1.0.0` graduation or the first release of a new package, pass an increment:

```bash
pnpm release:all --increment=1.0.0
```

- The version is forced even when a package has no releasable commit.
- A package already at that version fails with `Version not changed` (nothing changed), and inside `release:all` that failure stops the chain at that package. After the first package has been released with `--increment`, release the remaining ones one at a time (`release:styles`, `release:wc`, `release:react`, `release:vue`, each with the same `--increment`), and go back to plain `pnpm release:all` afterwards.
- The first publish of a brand-new package name also creates a public placeholder version `0.0.0-stage` while the real version waits for approval. Deprecate it, because it stays in the version list: `npm deprecate "@pxglobal/boreal-<package>@0.0.0-stage" "Placeholder created by npm staged publishing; use <version> or later"`.

# Manual Testing with Example Apps

The `examples/` directory contains two standalone apps for visually testing wrappers with packed artifacts - without needing to publish to npm first.

| App | Path | Wrapper under test |
| --- | --- | --- |
| React sandbox | `examples/react-testapp` | `@pxglobal/boreal-react` |
| Vue sandbox | `examples/vue-testapp` | `@pxglobal/boreal-vue` |

These apps are useful at two points in the workflow:

- **Before publishing** - to confirm that component rendering, theming, and props work correctly with the local build
- **During a release** - the same apps are used by `validate:pack:*` for the automated artifact gate (production build, not dev server)

## Running the React sandbox

From the workspace root:

```bash
pnpm dev:pack:react
```

This packs `@pxglobal/boreal-web-components` and `@pxglobal/boreal-react` as real `.tgz` artifacts, installs them into `examples/react-testapp`, and starts the dev server. Open the URL printed in the terminal.

To add a component under test, edit `examples/react-testapp/src/App.tsx`:

```tsx
import { BdsTypography } from '@pxglobal/boreal-react';

function App() {
  return <BdsTypography variant="heading" element="h1">Hello Boreal</BdsTypography>;
}
```

Available themes: set `data-theme` on `<body>` in `examples/react-testapp/index.html` to one of `proximus` | `connect` | `engage` | `protect`.

## Running the Vue sandbox

From the workspace root:

```bash
pnpm dev:pack:vue
```

Same artifact-pack-and-install flow as react. Edit `examples/vue-testapp/src/App.vue` to add components under test.

**Note:** `validate:pack:*` restores the wrapper and test-app `package.json` files and the root `pnpm-lock.yaml` with `git checkout HEAD --` on exit, which discards uncommitted edits to them. Commit or stash those files first. If a run is interrupted, those files can stay modified (they point to local `.tgz` files); restore them with `git checkout -- <file>` before releasing.

# Post-release Verification

## Verification checklist

- Every staged version is approved (nothing is left in the "Staged Packages" tab or in `npm stage list`).
- `npm view @pxglobal/boreal-<package> version dist-tags` shows the new version with `latest`, for every released package.
- `npm view @pxglobal/boreal-react@<version> dependencies` (and Vue) shows `@pxglobal/boreal-web-components` at an exact version, not `workspace:*`.
- The tags `@pxglobal/<package>@<version>` and the `chore(release)` commits are on Bitbucket.
- The web-components and style-guidelines changelogs gained a section for the version, with working Bitbucket compare links; React and Vue have none.
- No tarball holds a `CHANGELOG.md` or an internal link (`npm pack --dry-run`, and a search of the packed README).
- A scratch project installs the new packages from npm and builds.
- After the Storybook deploy, the Welcome page and the "What's new" page show the new version.

## Registry check

```bash
npm view @pxglobal/boreal-style-guidelines version dist-tags
npm view @pxglobal/boreal-web-components version dist-tags
npm view @pxglobal/boreal-react version dist-tags
npm view @pxglobal/boreal-vue version dist-tags
```

All released packages must show `latest: <new-version>`.

## Consumer smoke test

Run this from a directory **outside** the monorepo to confirm the published packages install cleanly:

```bash
mkdir /tmp/boreal-smoke && cd /tmp/boreal-smoke
npm install @pxglobal/boreal-web-components
npm install @pxglobal/boreal-react
npm install @pxglobal/boreal-vue
```

All must complete without errors. No version or tag is needed: `latest` is the newest version.

# Storybook Deployment (Chromatic)

## How it works

The deployment is split across two tools with separate responsibilities:

- **Turborepo** builds `boreal-docs` in correct dependency order: `style-guidelines → web-components → boreal-docs`
- **Chromatic CLI** receives the pre-built `storybook-static/` output and handles upload and hosting - it does not re-build Storybook

Chromatic publishes two URLs per deploy:

| URL type | Stability | When to share |
| --- | --- | --- |
| **Build URL** | Permanent - tied to a specific git SHA | Linking to a specific snapshot |
| **Branch URL** | Always points to the latest build on `release/current` ([visit url here](https://release-current--69b97decd1e136e932e6446b.chromatic.com/)) | Share with the alpha audience - stays stable across deploys |

Deploy after a release, so the Welcome page shows the new version and the "What's new" page lists the new entries, and after merging changes to the release tooling or the changelogs that affect those pages.

## Setting up the Chromatic project token

The `CHROMATIC_PROJECT_TOKEN` is required to publish. To retrieve it:

1. Log in to [chromatic.com](https://www.chromatic.com) using the `portals.team@telesign.com` user from the "Shared Portals" folder in LastPass
2. Go to **Manage → Configure**
3. Copy the project token under the **Project** section

Store it by copying `.env.example` to `.env` at the repo root and replacing the placeholder value:

```bash
cp .env.example .env
# Edit .env and set:
# CHROMATIC_PROJECT_TOKEN="<your-actual-token>"
```

The `.env` file is gitignored - never commit it. `pnpm deploy:docs` uses `dotenv-cli` to load it automatically.

## Running a deployment

```bash
pnpm deploy:docs
```

This executes `turbo run build --filter=@pxglobal/boreal-docs...` followed by the Chromatic upload. Expected output: Chromatic CLI prints the published Storybook URL.

## Forcing a fresh build

Two independent caching layers can each cause stale output:

| Layer | What it caches | How to bypass |
| --- | --- | --- |
| **Turborepo** | Build output (input file hashes) | `turbo run build --force ...` |
| **Chromatic** | Upload (git SHA match) | `--force-rebuild` flag on the chromatic CLI |

If the deployed Storybook does not reflect your latest changes, the Turborepo cache is the most likely cause. Bypass it:

```bash
turbo run build --force --filter=@pxglobal/boreal-docs... \
  && pnpm --filter @pxglobal/boreal-docs run chromatic
```

`--force-rebuild` on Chromatic only re-uploads - it does not trigger a fresh Turborepo build.

# Troubleshooting

## Where it stopped

| Where it stopped | State | What to do |
| --- | --- | --- |
| Build, breaking-change check or pack validation fails | Nothing of that package published or committed | Fix the cause, then run the release again. With an explicit `--increment`, release the **remaining** packages one at a time |
| The publish was staged but never approved (or rejected) | The release commit and tag are already pushed; the version is not installable | Approve it (or reject it, then release a corrected patch). A tag without an installable version is expected until the approval. If it was rejected, the tag points at a version that does not exist: do not reuse the number, release the next patch |
| `npm publish` fails (login, one-time password, permission, network) | Nothing committed or tagged for that package; the tree is restored | Fix the cause (see the errors below) and continue as above |
| The publish succeeded, then the push fails | The package is on npm; the commit and tag exist **locally** | Do not release that package again. Push the commit and tag (see "Push conflict during release"), then continue with the remaining packages |
| A wrong version was published | Published on npm | Never `npm unpublish`. Deprecate that version and release a corrected patch |

After any interruption, read `git status`, `git log -3` and `npm view <package> version` before running anything again.

## Push conflict during release (non-fast-forward)

If a teammate merges to `release/current` while release-it is mid-run and `git push` fails **after** npm publish has already succeeded:

```bash
# Do NOT re-run release-it for that package - the npm publish already succeeded
git pull --no-rebase origin release/current
git push --follow-tags origin release/current
```

Pulling with a merge keeps the release commit and its tag intact. (Rebasing rewrites the release commit, and the local tag would still point to the old one; if you rebase, move the tag to the new commit before pushing.) This recovery has not been exercised in a real release yet. Then continue with the remaining packages in your sequence.

## npm errors on publish

| Symptom | Cause | Fix |
| --- | --- | --- |
| `E401` | You are logged out or the token is invalid | `npm login`, or store a valid token (see "NPM authentication") |
| `E403` "Two-factor authentication or granular access token with bypass 2fa enabled is required" | Your account has no 2FA, or the token has no bypass, or the token's scope is not `@pxglobal` | Enable 2FA and use `npm login`, or create the token with the settings in "NPM authentication" |
| `E404` on `PUT` for a version that does not exist yet | The registry received no valid credentials: a token created on the website is not installed on your machine until you store it | `npm whoami`, then log in again or store the token |
| `SELF_SIGNED_CERT_IN_CHAIN` on react or vue while web-components publishes | The company network re-signs HTTPS traffic; pnpm 11 ignores the CA setting in `.npmrc` | See "TLS error behind the company proxy" |

If `npm org ls pxglobal` does not list you, request publish access to the `@pxglobal` organization from the account owner.

## TLS error behind the company proxy

The company network re-signs HTTPS traffic with its own certificate authority. npm accepts the CA configured in `.npmrc`, but pnpm 11 reads only authentication and registry settings from `.npmrc`, so react and vue (published through pnpm) fail with `SELF_SIGNED_CERT_IN_CHAIN` while web-components (published through npm) works.

1. Ask IT for the company root certificate (PEM, public) and keep it outside the repository, for example `~/.certs/company-root.pem`.
2. Add `export NODE_EXTRA_CA_CERTS=~/.certs/company-root.pem` to `~/.zshrc` and open a new terminal.
3. Check without releasing anything: `pnpm view @pxglobal/boreal-react version` prints a version.

Do not set `strict-ssl=false` or `NODE_TLS_REJECT_UNAUTHORIZED=0`: they turn off certificate checks for every request, including the one that sends your publish credentials.

## Artifact validation failure

`pnpm validate:pack:react` or `pnpm validate:pack:vue` failing means a broken import, missing export, or dependency resolution error is present in the package. Do not publish - diagnose and fix the root cause first. Common causes:

- An export was renamed or removed without updating the package's `exports` field
- A `workspace:*` dependency version constraint is unsatisfiable against published npm versions
- A missing file in the `dist/` output (build step did not complete cleanly)

## `release:all` fails mid-sequence

Determine which packages were published before the failure:

```bash
npm view @pxglobal/boreal-style-guidelines version
npm view @pxglobal/boreal-web-components version
npm view @pxglobal/boreal-react version
npm view @pxglobal/boreal-vue version
```

Without `--increment`, run `pnpm release:all` again: packages that are already released are skipped and only the remaining ones are released. With `--increment`, release only the remaining packages one at a time using the individual `pnpm release:*` scripts, because a package already at that version fails with `Version not changed` and stops the chain.

## Pull-request titles and handles

A breaking change must carry the `!` in the pull-request title (`feat(scope)!: ...`), as explained in "Versioning". A bare `@name` in a commit or pull-request title becomes a link to `https://bitbucket.c11.telesign.com/name` in the changelog, which does not exist: wrap handles and scopes in backticks, as in `@pxglobal`, or avoid them. Names containing a slash, such as `@pxglobal/boreal-react`, are left alone. Tooling and documentation commits that touch package folders must use a non-releasing type (`build`, `chore`, `docs`, `test`, `ci`).

## Rehearsing a release

Rehearse before a first or risky release: a copy of the repository with a local bare remote and a local npm registry (Verdaccio), so nothing reaches Bitbucket or npm. The steps and the scenarios to try are in `RELEASING.md`, "Rehearsing a release". A local registry does not emulate npm's staged publishing, so a rehearsal cannot show the approval step.

# Reference

## Root npm scripts

| Script | What it does |
| --- | --- |
| `pnpm release:styles` | Release `@pxglobal/boreal-style-guidelines` |
| `pnpm release:wc` | Release `@pxglobal/boreal-web-components` (build + CEM check + publish) |
| `pnpm release:react` | Release `@pxglobal/boreal-react` (runs `validate:pack:react` first) |
| `pnpm release:vue` | Release `@pxglobal/boreal-vue` (runs `validate:pack:vue` first) |
| `pnpm release:wc-stack` | Release web-components and the wrappers built from it, in order |
| `pnpm release:all` | Release all packages in dependency order; packages with nothing to release are skipped |
| `pnpm release:publish` | `release:all` + Storybook deploy |
| `pnpm validate:pack:react` | Pre-publish artifact validation gate for react |
| `pnpm validate:pack:vue` | Pre-publish artifact validation gate for vue |
| `pnpm validate:all` | Run both artifact validation gates |
| `pnpm dev:pack:react` | Start react example app with packed local artifacts |
| `pnpm dev:pack:vue` | Start vue example app with packed local artifacts |
| `pnpm deploy:docs` | Build Storybook via Turborepo + publish to Chromatic |

## Key configuration files

| File | Role |
| --- | --- |
| `packages/boreal-*/.release-it.json` | Per-package release config: version bump strategy (`preMajor`, path-scoped commits), branch guard, tag format and `tagMatch`, `latest` dist-tag, build hooks, release push without the `pre-push` hook |
| `scripts-boreal/bin/link-changelog-heading.js` | Hook that links a new changelog heading to its Bitbucket compare page (web-components and style-guidelines) |
| `turbo.json` | Build task graph: `release` depends on `^build`; `storybook-static/**` in build outputs |
| `apps/boreal-docs/package.json` | `chromatic` script with `--storybook-build-dir=storybook-static` |
| `.env.example` | Template for local environment variables - copy to `.env` and fill in values |
| `.env` (root, gitignored) | `CHROMATIC_PROJECT_TOKEN` for local Storybook deploys |
| `examples/react-testapp/` | React sandbox for manual component testing with packed artifacts |
| `examples/vue-testapp/` | Vue sandbox for manual component testing with packed artifacts |

# Future - CI/CD Pipeline

Today a release is made from a developer's local machine. Automating it depends on the decisions below, some of which constrain which pipeline architecture is viable. When a pipeline exists, the manual process described in this guide stays available as the exception path (see "Releasing by hand and from a pipeline").

## Decisions

| # | Decision | Status | Options on the table | Notes / next step |
| --- | --- | --- | --- | --- |
| 1 | **NPM registry allocation & strategy** | **Resolved** | Public npm registry, `@pxglobal` organization | All four packages publish publicly (`publishConfig.access: public`) under `@pxglobal`. The old `@telesign` versions are deprecated. |
| 2 | **Icons distribution strategy** | Open - blocked | Replicate icon assets into a team-owned S3 bucket (Phase 1 of [ITOPS-67974](https://telesign.atlassian.net/browse/ITOPS-67974)) | Icons are currently served from an S3 bucket outside the team's AWS account - no write access, no policy control. ITOPS-67974 proposes replicating assets into a new team-owned bucket (`boreal-ds-static-assets`) with the old URL kept alive in parallel. The ticket is closed/unresolved: DevOps requested an architecture write-up (account strategy, AWS Organization structure, cost/governance model) before proceeding, and that documentation was never supplied. **Next step:** produce that write-up and get sign-off before Phase 1 work resumes. |
| 3 | **CI/CD pipeline runner** | Open | Bitbucket Pipelines · GitHub Actions via Jenkins mirror · Jenkins running the pipeline directly | Jenkins is the direction. Requires DevOps provisioning regardless of choice: Docker pipeline runners on the on-prem Bitbucket instance (Bitbucket Pipelines), a real GitHub org repo + Jenkins sync job (GitHub Actions), or Jenkins credentials/job definitions (direct Jenkins). Product code must not be pushed to an external GitHub repository without company security approval. This decision also constrains decision 6. |
| 4 | **Non-personal npm credential** | Open | Stage-only granular token with a person approving · Trusted publishing from CI · Bypass-2FA token | A bypass-2FA token loses direct publishing around January 2027 and then only stages a publish. Which CI providers npm supports for trusted publishing is to be confirmed. |
| 5 | **Release push rights and approval** | Open | Service account with push rights to `release/current` · Approval step for staged publishes | The job must push release commits and tags (the push skips the `pre-push` hook). `release-it` does not wait for npm's approval, so the job needs a way to wait or to be re-run. |
| 6 | **Storybook deployment target** | Open | Keep Chromatic (current manual workflow) · Self-hosted AWS S3 + CloudFront | Chromatic is already working today via `pnpm deploy:docs` - automating it is the lowest-effort path since no new infrastructure is required, but it means keeping a third-party SaaS dependency. Moving to S3 + CloudFront requires new AWS infra (buckets, distributions, IAM roles) and loses Chromatic's built-in visual regression testing and per-branch preview URLs unless replaced. |

**Per-package change detection is built in.** `release-it` skips a package that has no releasable commit since its own last tag, and the React and Vue packages follow web-components and style-guidelines, so no separate pre-release script is needed.
