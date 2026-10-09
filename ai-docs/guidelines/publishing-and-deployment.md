# Publishing & Deployment Guide — Boreal DS

How Boreal DS packages are published and how the Storybook site is deployed. The release **procedure** is maintained in the tracked `RELEASING.md` at the repository root; this guide keeps the internal context around it (Storybook deployment, example apps, reference, CI/CD plans). If this guide and `RELEASING.md` ever differ, `RELEASING.md` wins.

The previous manual alpha guide (`@telesign`, `alpha` dist-tag, `--preRelease=alpha`) is kept for history in `archive/publishing-and-deployment-alpha-telesign-2026-10.md`.

---

## Where to look

| You need…                                                                              | Go to                                                                  |
| -------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| To cut a release: preconditions, commands, verification, recovery, rehearsal           | `RELEASING.md`                                                         |
| The versioning and commit policy: commit types, what counts as breaking, PR title rule | `CONTRIBUTING.md` (Commit Messages, Pull Requests, Release & Versioning) |
| Why `release-it` and how the five audit defects were fixed                             | `ai-docs/decisions/0013-release-tooling-release-it-vs-changesets.md`   |
| The tooling that links changelog headings to Bitbucket                                 | `scripts-boreal/README.md` (Release helpers)                           |
| Deploying Storybook, testing wrappers with the example apps, CI/CD plans               | The sections below                                                     |

## Packages in Scope

| Package          | npm name                            | Role                       |
| ---------------- | ----------------------------------- | -------------------------- |
| Style Guidelines | `@pxglobal/boreal-style-guidelines` | Design tokens and base CSS |
| Web Components   | `@pxglobal/boreal-web-components`   | Stencil component library  |
| React wrapper    | `@pxglobal/boreal-react`            | React-native bindings      |
| Vue wrapper      | `@pxglobal/boreal-vue`              | Vue-native bindings        |

**Tooling stack:** `release-it` orchestrates versioning, changelogs, git tagging and npm publish. `Turborepo` manages the build graph. `pnpm workspaces` handles inter-package dependencies. `Chromatic` hosts the Storybook documentation site.

Packages are public on npm under the `@pxglobal` organization on plain `0.x` versions (alpha is a stated status, not a version suffix or dist-tag). The old `@telesign/*` packages are deprecated.

## Release at a glance

Run from `release/current`, clean, on macOS or Linux. Flags are passed without `--`.

```bash
pnpm release:all          # every package, in dependency order
pnpm release:wc-stack     # web-components, then React and Vue
pnpm release:styles       # style-guidelines only
```

A package with no releasable commit since its last tag is skipped. Each package gets one bump from the whole batch of commits, set by the highest level among them. Everything else — dry run, publish approval, verification, recovery — is in `RELEASING.md`.

---

## Manual Testing with Example Apps

The `examples/` directory contains two standalone apps for visually testing wrappers with packed artifacts, without publishing to npm.

| App           | Path                     | Wrapper under test       |
| ------------- | ------------------------ | ------------------------ |
| React sandbox | `examples/react-testapp` | `@pxglobal/boreal-react` |
| Vue sandbox   | `examples/vue-testapp`   | `@pxglobal/boreal-vue`   |

They are used at two points:

- **Before a release**: to confirm rendering, theming and props work with the local build (`pnpm dev:pack:react`, `pnpm dev:pack:vue`).
- **During a release**: the same apps are used by `validate:pack:*`, the automated gate that runs as a `prerelease` hook of each wrapper (a production build, not a dev server).

### Running the React sandbox

From the workspace root:

```bash
pnpm dev:pack:react
```

This packs `@pxglobal/boreal-web-components` and `@pxglobal/boreal-react` as real `.tgz` artifacts, installs them into `examples/react-testapp`, and starts the dev server. Open the URL printed in the terminal.

To add a component under test, edit `examples/react-testapp/src/App.tsx`:

```tsx
import { BdsTypography } from "@pxglobal/boreal-react";

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

```bash
pnpm dev:pack:vue
```

Same pack-and-install flow as React. Edit `examples/vue-testapp/src/App.vue` to add components under test.

> `validate:pack:*` restores the wrapper and test-app `package.json` files and the root `pnpm-lock.yaml` with `git checkout HEAD --` on exit, which discards uncommitted edits to them. Commit or stash those files first.

---

## Consumer Smoke Test

After a release, install the packages from a directory **outside** the monorepo:

```bash
mkdir /tmp/boreal-smoke && cd /tmp/boreal-smoke
npm install @pxglobal/boreal-web-components @pxglobal/boreal-react @pxglobal/boreal-style-guidelines
```

No version or tag is needed: `latest` is the newest version. The full verification checklist is in `RELEASING.md`.

---

## Storybook Deployment (Chromatic)

### How it works

The deployment is split across two tools with separate responsibilities:

- **Turborepo** builds `boreal-docs` in dependency order: `style-guidelines → web-components → boreal-docs`.
- **Chromatic CLI** receives the pre-built `storybook-static/` output and handles upload and hosting. It does not re-build Storybook.

Chromatic publishes two URLs per deploy:

| URL type       | Stability                                              | When to share                                         |
| -------------- | ------------------------------------------------------ | ----------------------------------------------------- |
| **Build URL**  | Permanent, tied to a specific git SHA                  | Linking to a specific snapshot                        |
| **Branch URL** | Always points to the latest build on `release/current` | Share with the alpha audience; stable across deploys |

Deploy after a release (so the Welcome page shows the new version and the "What's new" page lists the new entries) and after merging changes to the release tooling that affect the changelog pages.

### Setting up the Chromatic project token

The `CHROMATIC_PROJECT_TOKEN` is required to publish. To retrieve it:

1. Log in to [chromatic.com](https://www.chromatic.com) using the `portals.team@telesign.com` user from the "Shared Portals" folder in LastPass.
2. Go to **Manage → Configure**.
3. Copy the project token under the **Project** section.

Store it by copying `.env.example` to `.env` at the repo root and replacing the placeholder value:

```bash
cp .env.example .env
# Edit .env and set:
# CHROMATIC_PROJECT_TOKEN="<your-actual-token>"
```

The `.env` file is gitignored: never commit it. `pnpm deploy:docs` uses `dotenv-cli` to load it automatically.

### Running a deployment

```bash
pnpm deploy:docs
```

This executes `turbo run build --filter=@pxglobal/boreal-docs...` followed by the Chromatic upload. The Chromatic CLI prints the published Storybook URL.

### Forcing a fresh build

Two independent caching layers can each cause stale output:

| Layer         | What it caches                   | How to bypass                               |
| ------------- | -------------------------------- | ------------------------------------------- |
| **Turborepo** | Build output (input file hashes) | `turbo run build --force ...`               |
| **Chromatic** | Upload (git SHA match)           | `--force-rebuild` flag on the chromatic CLI |

If the deployed Storybook does not reflect your latest changes, the Turborepo cache is the most likely cause:

```bash
turbo run build --force --filter=@pxglobal/boreal-docs... \
  && pnpm --filter @pxglobal/boreal-docs run chromatic
```

`--force-rebuild` on Chromatic only re-uploads; it does not trigger a fresh Turborepo build.

---

## Troubleshooting

Release problems (a failed build or validation, a refused publish, a push that fails after the publish, a wrong version) are covered by the recovery table in `RELEASING.md` ("When something goes wrong"). Two Storybook-specific points:

- **Stale Storybook after a deploy:** see "Forcing a fresh build" above.
- **Chromatic upload fails:** check that `CHROMATIC_PROJECT_TOKEN` is set in the root `.env`. If packages were already released, retry with `pnpm deploy:docs`; there is no need to release again.

---

## Reference

### Root npm scripts

| Script                     | What it does                                                                                 |
| -------------------------- | -------------------------------------------------------------------------------------------- |
| `pnpm release:styles`      | Release `@pxglobal/boreal-style-guidelines`                                                  |
| `pnpm release:wc`          | Release `@pxglobal/boreal-web-components` (build + custom-elements check + publish)          |
| `pnpm release:react`       | Release `@pxglobal/boreal-react` (runs `validate:pack:react` first)                          |
| `pnpm release:vue`         | Release `@pxglobal/boreal-vue` (runs `validate:pack:vue` first)                              |
| `pnpm release:wc-stack`    | Release web-components and the wrappers built from it, in order                              |
| `pnpm release:all`         | Release every package in dependency order; packages with nothing to release are skipped      |
| `pnpm release:publish`     | `release:all` + Storybook deploy                                                             |
| `pnpm validate:pack:react` | Pre-publish artifact validation gate for React                                               |
| `pnpm validate:pack:vue`   | Pre-publish artifact validation gate for Vue                                                 |
| `pnpm validate:all`        | Run both artifact validation gates                                                           |
| `pnpm dev:pack:react`      | Start the React example app with packed local artifacts                                      |
| `pnpm dev:pack:vue`        | Start the Vue example app with packed local artifacts                                        |
| `pnpm deploy:docs`         | Build Storybook via Turborepo + publish to Chromatic                                         |

### Key configuration files

| File                                    | Role                                                                                                                            |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `packages/boreal-*/` `.release-it.json` | Per-package release config: bump rules (`preMajor`, path-scoped commits), tag format and `tagMatch`, `latest` dist-tag, hooks, release push without the `pre-push` hook |
| `turbo.json`                            | Build task graph: `release` depends on `^build`; `storybook-static/**` in build outputs                                         |
| `apps/boreal-docs/package.json`         | `chromatic` script with `--storybook-build-dir=storybook-static`                                                                |
| `.env.example`                          | Template for local environment variables: copy to `.env` and fill in values                                                     |
| `.env` (root, gitignored)               | `CHROMATIC_PROJECT_TOKEN` for local Storybook deploys                                                                           |
| `examples/react-testapp/`               | React sandbox for manual component testing with packed artifacts                                                                |
| `examples/vue-testapp/`                 | Vue sandbox for manual component testing with packed artifacts                                                                  |

---

## Future — CI/CD Pipeline

Today the release runs by hand from a maintainer's machine. When CI is available, the procedure in `RELEASING.md` maps onto a pipeline job that runs the same commands non-interactively (`--ci`). Open questions are tracked for the DevOps meeting (EOA-18870): whether to release on every merge or on a schedule or approval, who holds a non-personal npm publish credential, push rights to `release/current` for release commits, and how npm's staged-publishing approval is handled.

**Storybook deployment, option A — Bitbucket Pipelines (preferred).** Chromatic supports Bitbucket Pipelines natively. A pipeline triggered on push to `release/current` would run `pnpm deploy:docs` and post build status back to pull requests. Requires DevOps to provision Docker pipeline runners.

**Storybook deployment, option B — GitHub Actions via a Jenkins mirror (fallback).** If Bitbucket Pipelines runners are unavailable, the monorepo could be mirrored to GitHub through the existing Jenkins sync infrastructure and a GitHub Actions workflow could trigger the Chromatic build. Requires DevOps to create the mirror. The product code must not be pushed to an external GitHub repository without company security approval.

**Per-package change detection is built in.** The earlier idea of a pre-release script that decides per package whether to release is no longer needed: `release-it` skips a package that has no releasable commit since its own last tag (path-scoped), and the React and Vue packages follow web-components and style-guidelines. This was verified in the release rehearsal and the first real release.
