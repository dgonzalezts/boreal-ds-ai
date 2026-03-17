# Publishing & Deployment Guide — Boreal DS (Alpha)

This guide covers the recurring alpha release workflow and Storybook deployment process for the Boreal Design System monorepo. It is intended for all team contributors who need to cut a release or publish updated documentation.

---

## Packages in Scope

| Package          | npm name                            | Role                       |
| ---------------- | ----------------------------------- | -------------------------- |
| Style Guidelines | `@telesign/boreal-style-guidelines` | Design tokens and base CSS |
| Web Components   | `@telesign/boreal-web-components`   | Stencil component library  |
| React wrapper    | `@telesign/boreal-react`            | React-native bindings      |
| Vue wrapper      | `@telesign/boreal-vue`              | Vue-native bindings        |

**Tooling stack:** `release-it` orchestrates versioning, changelogs, git tagging, and npm publish. `Turborepo` manages the build graph. `pnpm workspaces` handles inter-package dependencies. `Chromatic` hosts the Storybook documentation site.

---

## TL;DR — Quick Reference

For contributors already familiar with the process:

```bash
# Pre-conditions
fnm use
npm whoami && npm access list packages @telesign
git checkout release/current && git pull && git status

# Release web-components (if it has changes)
pnpm release:wc

# Release react
pnpm validate:pack:react && pnpm release:react

# Release vue
pnpm validate:pack:vue && pnpm release:vue

# Release style-guidelines (if it has changes, independent)
pnpm release:styles

# Deploy Storybook
pnpm deploy:docs   # requires CHROMATIC_PROJECT_TOKEN in .env
```

**Shortcut — release all packages + deploy in one command:**

```bash
pnpm release:publish   # styles → wc → validate:all → react → vue → deploy:docs
```

See [§5.6 Automated release sequence](#56-automated-release-sequence-releaseall) for tradeoffs before choosing this path.

---

## 1. Alpha Versioning

### Version number anatomy

```
0  .  1  .  0  -  alpha  .  N
│     │     │             └── pre-release counter (resets on base bump)
│     │     └──────────────── patch
│     └────────────────────── minor
└──────────────────────────── major (0 = not yet stable)
```

Counter progression driven by conventional commits:

| Commits since last tag   | Version bump               | Example                           |
| ------------------------ | -------------------------- | --------------------------------- |
| `fix:` only              | patch (counter increments) | `0.1.0-alpha.0` → `0.1.0-alpha.1` |
| Any `feat:`              | minor (counter resets)     | `0.1.0-alpha.1` → `0.2.0-alpha.0` |
| `BREAKING CHANGE` footer | major (counter resets)     | `0.1.0-alpha.N` → `1.0.0-alpha.0` |

### npm dist-tag: `alpha`

All packages are published under `--tag alpha`, configured via `"tag": "alpha"` in each package's `.release-it.json`. Consumers install pre-release builds with:

```bash
npm install @telesign/boreal-web-components@alpha
```

The `latest` dist-tag is intentionally not moved to an alpha version — it will point to the first stable release.

---

## 2. Coordinating with the Team

Releasing is a shared, manual operation on a shared branch. A few simple practices prevent the most common coordination failures.

### Before you start

1. **Announce intent** — post a brief message in the team channel (e.g. "releasing WC + react now") so no one merges to `release/current` while your release is in progress.
2. **Check for open PRs** — confirm there are no pending PRs targeting `release/current` that should land before the release. A PR merged between two packages in your sequence will break the push step mid-run.
3. **Pull latest** — run `git pull origin release/current` immediately before starting, not minutes earlier.

### Built-in safety rails

release-it enforces two guards in every package's `.release-it.json` that catch common mistakes automatically:

| Guard                              | What it enforces                                              |
| ---------------------------------- | ------------------------------------------------------------- |
| `requireBranch: "release/current"` | release-it aborts if you are on any other branch              |
| `requireCleanWorkingDir: true`     | release-it aborts if the working tree has uncommitted changes |

These run at the very start of each release invocation — before any build, version prompt, or publish step.

### Mid-release push conflict

release-it commits and pushes to `release/current` after each individual package release. If a teammate merges between two packages in your sequence, the `git push` for the next package will fail with a non-fast-forward error — **after** npm publish for that package has already succeeded.

**Do not re-run release-it.** The npm publish cannot be undone. Recover the git state only:

```bash
git pull --rebase origin release/current
git push origin release/current
```

The rebase is safe — the release commit only modifies `package.json` and `CHANGELOG.md`. Then continue with the remaining packages in the sequence. See [§9 Troubleshooting](#9-troubleshooting) for more detail.

---

## 3. Prerequisites

### NPM authentication

Authenticate with npm using either interactive browser login or token-based authentication:

**Option 1: Interactive login (recommended)**

```bash
npm login --registry=https://registry.npmjs.org
```

This opens a browser prompt to enter your credentials. After completion, verify your session and scope access:

```bash
npm whoami                          # returns your npm username
npm access list packages @telesign  # lists all four packages with publish access
```

**Option 2: Token-based authentication**

For headless environments, add your npm token to `~/.npmrc`:

```bash
echo "//registry.npmjs.org/:_authToken=<your-token>" >> ~/.npmrc
npm whoami  # verify your username is returned
```

Your npm account must have publish access to the `@telesign` scope. If access is missing, request it from the account owner before proceeding.

```bash
npm login --registry=https://registry.npmjs.org
```

This opens a browser prompt. Once complete, verify the session and confirm scope access:

```bash
npm whoami                          # must return your username
npm access list packages @telesign  # must list all four packages with publish access
```

If you prefer token-based authentication (e.g. in a headless environment), add the token to `~/.npmrc` instead:

```bash
echo "//registry.npmjs.org/:_authToken=<your-token>" >> ~/.npmrc
npm whoami  # must return your username
```

### Commands to run

Run these checks before starting any release. All must pass.

| Check              | Command                              | Expected result                              |
| ------------------ | ------------------------------------ | -------------------------------------------- |
| Node.js version    | `fnm use`                            | Activates version from `.node-version`       |
| npm authentication | `npm whoami`                         | Your npm username                            |
| npm scope access   | `npm access list packages @telesign` | All four packages listed with publish access |
| Branch             | `git branch --show-current`          | `release/current`                            |
| Working tree       | `git status`                         | Nothing to commit, working tree clean        |
| Sync remote        | `git pull origin release/current`    | Up to date                                   |

> **Note on `fnm use` in scripts:** In non-interactive shells (e.g. CI or the Bash tool), `fnm use` alone does not activate the version. Prefix script commands with `eval "$(fnm env --shell bash)" && fnm use &&`.

![Pre-conditions check — npm whoami and access](./images/2026-03-16_13-58-00.png)

![Pre-conditions check — git status clean](./images/2026-03-16_13-58-19.png)

---

## 4. How release-it Behaves

Understanding this prevents the most common mistakes.

**release-it does not auto-detect changes by default.** It always runs when invoked — `git.requireCommits` can be configured to abort when there are no commits since the last tag, but it is intentionally not enabled here (see [§11](#11-future--cicd-pipeline) for why). Deciding which packages warrant a new version is the developer's responsibility. If you run `pnpm release:wc` with no new commits since the last tag, it will still produce a new `alpha.N` version.

**`@release-it/conventional-changelog` reads commits since the last git tag** to determine two things only:

1. The version bump type (patch / minor / major)
2. The content of `CHANGELOG.md`

It does not gate or skip the release.

**The `before:init` hook builds the package automatically** via Turborepo before the version prompt appears. No manual build step is required before running a release script.

---

## 5. Package Publishing

### 5.1 Why release order matters

`@telesign/boreal-react` and `@telesign/boreal-vue` declare their dependency on `@telesign/boreal-web-components` using pnpm's `workspace:*` protocol. At publish time, pnpm replaces `workspace:*` in the tarball with the **exact version currently published on npm**. This means:

- If `boreal-web-components` has unreleased changes, release it first — otherwise react and vue will pin the previous version.
- `boreal-style-guidelines` has no inter-package dependency and can be released at any time, in any order.

**Required order when web-components has changes:**

```
boreal-web-components  →  boreal-react  →  boreal-vue
```

> **Run all commands in this section from the workspace root** (`boreal-ds/`). The `pnpm release:*` and `pnpm validate:pack:*` scripts are defined in the root `package.json` and use pnpm's `--filter` flag internally to target each package. Running them from inside a package directory will produce a "missing script" error.

### 5.2 Releasing `@telesign/boreal-style-guidelines`

```bash
pnpm release:styles
```

**Verify:**

```bash
npm dist-tag ls @telesign/boreal-style-guidelines
# → alpha: <new-version>
```

### 5.3 Releasing `@telesign/boreal-web-components`

The `before:init` hook runs two steps before the version prompt:

1. **Build** — `turbo run build --filter=@telesign/boreal-web-components`
2. **CEM check** — `tsx scripts/check-cem-changes.ts` generates a Custom Elements Manifest diff report that surfaces breaking API changes automatically

Review the CEM report output before confirming the version prompt.

```bash
pnpm release:wc
```

![release-it version prompt and CEM report](./images/2026-03-16_13-59-30.png)

![release-it publishing to npm](./images/2026-03-16_13-59-45.png)

![web-components release complete](./images/2026-03-16_13-59-54.png)

**Verify:**

```bash
npm dist-tag ls @telesign/boreal-web-components
# → alpha: <new-version>
```

![npm dist-tag verification — web-components](./images/2026-03-16_14-00-56.png)

### 5.4 Releasing `@telesign/boreal-react`

A pre-publish artifact validation gate must pass before publishing. It packs a real `.tgz`, installs it into a test app, and runs a production Vite build — catching broken imports and missing exports before they reach npm.

**Stop if the gate fails. Do not proceed to publish.**

```bash
pnpm validate:pack:react
# Expected: ✅ Pipeline completed successfully — artifact validation passed

pnpm release:react
```

![react release complete](./images/2026-03-16_14-01-38.png)

**Verify:**

```bash
npm dist-tag ls @telesign/boreal-react
# → alpha: <new-version>
```

![npm dist-tag verification — react](./images/2026-03-16_14-01-57.png)

### 5.5 Releasing `@telesign/boreal-vue`

Same pattern as react — validation gate first.

**Stop if the gate fails. Do not proceed to publish.**

```bash
pnpm validate:pack:vue
# Expected: ✅ Pipeline completed successfully — artifact validation passed

pnpm release:vue
```

![vue release complete](./images/2026-03-16_14-02-07.png)

![vue publish to npm](./images/2026-03-16_14-02-29.png)

**Verify:**

```bash
npm dist-tag ls @telesign/boreal-vue
# → alpha: <new-version>
```

![npm dist-tag verification — vue](./images/2026-03-16_14-02-53.png)

### 5.6 Automated release sequence (`release:all`)

Two root scripts combine the per-package steps into a single command:

| Script                 | What it runs                                                               |
| ---------------------- | -------------------------------------------------------------------------- |
| `pnpm release:all`     | `release:styles → release:wc → validate:all → release:react → release:vue` |
| `pnpm release:publish` | Everything in `release:all`, then `deploy:docs`                            |

**`release:all` works correctly for the happy path** — the sequence is ordered correctly, validation gates are respected (the `&&` chain stops if `validate:all` fails), and `requireCleanWorkingDir` is not an issue because each individual release-it invocation commits and pushes its own changes before exiting.

Interactive version prompts still appear — one per package in sequence. You can still read the CEM report from the web-components `before:init` hook before confirming its prompt.

**Use `release:all` when:** all packages genuinely have new commits and you want to release them in one unattended sequence.

**Use the manual per-package process when:**

- Only a subset of packages have new commits — `release:all` always releases all four, burning an alpha counter on packages that haven't changed.
- The team is actively merging to `release/current` — a push conflict mid-chain is harder to recover from since you need to track exactly which packages were published before the failure.
- You want to carefully review the CEM diff for `boreal-web-components` before committing to a publish.

**Recovery if `release:all` fails mid-sequence:**

npm publish cannot be undone. If the chain stops after some packages have been published, do not re-run `release:all`. Identify which packages were published (check `npm dist-tag ls`) and run only the remaining ones manually.

---

## 6. Manual Testing with Example Apps

The `examples/` directory contains two standalone apps for visually testing wrappers with packed artifacts — without needing to publish to npm first.

| App           | Path                     | Wrapper under test       |
| ------------- | ------------------------ | ------------------------ |
| React sandbox | `examples/react-testapp` | `@telesign/boreal-react` |
| Vue sandbox   | `examples/vue-testapp`   | `@telesign/boreal-vue`   |

These apps are useful at two points in the workflow:

- **Before publishing** — to confirm that component rendering, theming, and props work correctly with the local build
- **After publishing** — the same apps are used by `validate:pack:*` for the automated artifact gate (production build, not dev server)

### Running the React sandbox

From the workspace root:

```bash
pnpm dev:pack:react
```

This packs `@telesign/boreal-web-components` and `@telesign/boreal-react` as real `.tgz` artifacts, installs them into `examples/react-testapp`, and starts the dev server. Open the URL printed in the terminal.

To add a component under test, edit `examples/react-testapp/src/App.tsx`:

```tsx
import { BdsTypography } from "@telesign/boreal-react";

function App() {
  return (
    <BdsTypography variant="heading" element="h1">
      Hello Boreal
    </BdsTypography>
  );
}
```

Available themes: set `data-theme` on `<body>` in `examples/react-testapp/index.html` to one of `proximus` | `connect` | `engage` | `protect`.

### Running the Vue sandbox

From the workspace root:

```bash
pnpm dev:pack:vue
```

Same artifact-pack-and-install flow as react. Edit `examples/vue-testapp/src/App.vue` to add components under test.

---

## 7. Post-release Verification

### Registry check

```bash
npm view @telesign/boreal-style-guidelines dist-tags
npm view @telesign/boreal-web-components dist-tags
npm view @telesign/boreal-react dist-tags
npm view @telesign/boreal-vue dist-tags
```

All released packages must show `alpha: <new-version>`.

### Consumer smoke test

Run this from a directory **outside** the monorepo to confirm the published packages install cleanly:

```bash
mkdir /tmp/boreal-alpha-test && cd /tmp/boreal-alpha-test
npm install @telesign/boreal-web-components@alpha
npm install @telesign/boreal-react@alpha
npm install @telesign/boreal-vue@alpha
```

All must complete without errors.

---

## 8. Storybook Deployment (Chromatic)

### How it works

The deployment is split across two tools with separate responsibilities:

- **Turborepo** builds `boreal-docs` in correct dependency order: `style-guidelines → web-components → boreal-docs`
- **Chromatic CLI** receives the pre-built `storybook-static/` output and handles upload and hosting — it does not re-build Storybook

Chromatic publishes two URLs per deploy:

| URL type       | Stability                                              | When to share                                           |
| -------------- | ------------------------------------------------------ | ------------------------------------------------------- |
| **Build URL**  | Permanent — tied to a specific git SHA                 | Linking to a specific snapshot                          |
| **Branch URL** | Always points to the latest build on `release/current` | Share with alpha audience — stays stable across deploys |

### Setting up the Chromatic project token

The `CHROMATIC_PROJECT_TOKEN` is required to publish. To retrieve it:

1. Log in to [chromatic.com](https://www.chromatic.com) using the `portals.team@telesign.com` user from the “Shared Portals” folder in LastPass
2. Go to **Manage → Configure**
3. Copy the project token under the **Project** section

Store it by copying `.env.example` to `.env` at the repo root and replacing the placeholder value:

```bash
cp .env.example .env
# Edit .env and set:
# CHROMATIC_PROJECT_TOKEN="<your-actual-token>"
```

The `.env` file is gitignored — never commit it. `pnpm deploy:docs` uses `dotenv-cli` to load it automatically.

### Running a deployment

```bash
pnpm deploy:docs
```

This executes `turbo run build --filter=@telesign/boreal-docs...` followed by the Chromatic upload. Expected output: Chromatic CLI prints the published Storybook URL.

![Chromatic deployment — CLI output and published URL](./images/2026-03-16_14-52-18.png)

### Forcing a fresh build

Two independent caching layers can each cause stale output:

| Layer         | What it caches                   | How to bypass                               |
| ------------- | -------------------------------- | ------------------------------------------- |
| **Turborepo** | Build output (input file hashes) | `turbo run build --force ...`               |
| **Chromatic** | Upload (git SHA match)           | `--force-rebuild` flag on the chromatic CLI |

If deployed Storybook does not reflect your latest changes, Turborepo cache is the most likely cause. Bypass it:

```bash
turbo run build --force --filter=@telesign/boreal-docs... \
  && pnpm --filter @telesign/boreal-docs run chromatic
```

`--force-rebuild` on Chromatic only re-uploads — it does not trigger a fresh Turborepo build.

---

## 9. Troubleshooting

### Push conflict during release (non-fast-forward)

If a teammate merges to `release/current` while release-it is mid-run and `git push` fails **after** npm publish has already succeeded:

```bash
# Do NOT re-run release-it — the npm publish already succeeded
git pull --rebase origin release/current
git push origin release/current
```

The rebase is safe — the release commit only modifies `package.json` and `CHANGELOG.md`. Then continue with the remaining packages in your sequence.

### npm access denied / 403 on publish

```bash
npm whoami                          # must return your username
npm access list packages @telesign  # must list all four packages
```

If your account is missing, request publish access to the `@telesign` scope from the account owner.

### Artifact validation failure

`pnpm validate:pack:react` or `pnpm validate:pack:vue` failing means a broken import, missing export, or dependency resolution error is present in the package. Do not publish — diagnose and fix the root cause first. Common causes:

- An export was renamed or removed without updating the package's `exports` field
- A `workspace:*` dependency version constraint is unsatisfiable against published npm versions
- A missing file in the `dist/` output (build step did not complete cleanly)

### `release:all` fails mid-sequence

Determine which packages were published before the failure:

```bash
npm dist-tag ls @telesign/boreal-style-guidelines
npm dist-tag ls @telesign/boreal-web-components
npm dist-tag ls @telesign/boreal-react
npm dist-tag ls @telesign/boreal-vue
```

Do not re-run `release:all`. Release only the remaining packages manually using the individual `pnpm release:*` scripts.

---

## 10. Reference

### Root npm scripts

| Script                     | What it does                                                            |
| -------------------------- | ----------------------------------------------------------------------- |
| `pnpm release:styles`      | Release `@telesign/boreal-style-guidelines`                             |
| `pnpm release:wc`          | Release `@telesign/boreal-web-components` (build + CEM check + publish) |
| `pnpm release:react`       | Release `@telesign/boreal-react`                                        |
| `pnpm release:vue`         | Release `@telesign/boreal-vue`                                          |
| `pnpm release:all`         | Release all packages in dependency order with validation gates          |
| `pnpm release:publish`     | `release:all` + Storybook deploy                                        |
| `pnpm validate:pack:react` | Pre-publish artifact validation gate for react                          |
| `pnpm validate:pack:vue`   | Pre-publish artifact validation gate for vue                            |
| `pnpm validate:all`        | Run both artifact validation gates                                      |
| `pnpm dev:pack:react`      | Start react example app with packed local artifacts                     |
| `pnpm dev:pack:vue`        | Start vue example app with packed local artifacts                       |
| `pnpm deploy:docs`         | Build Storybook via Turborepo + publish to Chromatic                    |

### Key configuration files

| File                                    | Role                                                                                       |
| --------------------------------------- | ------------------------------------------------------------------------------------------ |
| `packages/boreal-*/` `.release-it.json` | Per-package release config: version bump strategy, branch guard, npm dist-tag, build hooks |
| `turbo.json`                            | Build task graph: `release` depends on `^build`; `storybook-static/**` in build outputs    |
| `apps/boreal-docs/package.json`         | `chromatic` script with `--storybook-build-dir=storybook-static`                           |
| `.env.example`                          | Template for local environment variables — copy to `.env` and fill in values               |
| `.env` (root, gitignored)               | `CHROMATIC_PROJECT_TOKEN` for local Storybook deploys                                      |
| `examples/react-testapp/`               | React sandbox for manual component testing with packed artifacts                           |
| `examples/vue-testapp/`                 | Vue sandbox for manual component testing with packed artifacts                             |

---

## 11. Future — CI/CD Pipeline

The current process is entirely manual and runs from a developer's local machine. When CI becomes available, the manual deployment steps can be automated.

**Option A — Bitbucket Pipelines (preferred)**

Chromatic natively supports Bitbucket Pipelines. A pipeline triggered on push to `release/current` would run `pnpm deploy:docs` automatically and post build status back to pull requests. Requires DevOps to provision Docker pipeline runners on the on-prem Bitbucket instance.

**Option B — GitHub Actions via Jenkins mirror (fallback)**

If Bitbucket Pipelines runners are unavailable, the monorepo can be mirrored to GitHub via the existing Jenkins sync infrastructure. A GitHub Actions workflow triggers the Chromatic build on push to `release/current`. Requires DevOps to create the `TeleSign/boreal-ds` GitHub repository and configure the sync job.

Full pipeline YAML for both options is documented in `.ai/plans/storybook-chromatic-deployment.md`.

### Per-package change detection (recommended before adopting `requireCommits`)

Once CI runs `release:all` automatically on every merge to `release/current`, releasing all four packages unconditionally on every push becomes unsustainable. The natural solution appears to be enabling `git.requireCommits: true` in each `.release-it.json` — but this breaks the primary release scenario for `boreal-react` and `boreal-vue`, which are routinely released with zero new commits of their own solely to re-pin a new version of `boreal-web-components`.

The right approach is a **pre-release change detection script** that runs before `release-it` and decides per-package whether a release is warranted, accounting for both direct commits and dependency version changes. The logic per package would be:

```
has_commits        = git log <last-tag>..HEAD -- <package-path>  is non-empty
dep_version_bumped = last published WC version on npm
                     ≠ WC version pinned in the previous react/vue tarball

should_release = has_commits OR dep_version_bumped
```

In practice this can be implemented as a small shell or Node.js script that:

1. Resolves the last git tag for each package (`git describe --tags --match "@telesign/<pkg>@*"`)
2. Checks `git log <tag>..HEAD -- packages/<pkg>/` for new commits since that tag
3. For `boreal-react` and `boreal-vue` specifically, additionally compares the `@telesign/boreal-web-components` version in the previous published tarball against the version currently tagged on npm
4. Skips `release-it` for that package if neither condition is met

This keeps `requireCommits` out of the individual `.release-it.json` files — preserving the flexibility to release wrappers for dependency re-pinning — while still preventing no-op releases in an automated pipeline.
