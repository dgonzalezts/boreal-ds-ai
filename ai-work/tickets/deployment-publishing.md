## [original]

As a developer, when implementing the Boreal component library alpha test, I want to publish different packages to NPM and deploy the Storybook documentation so that I can ensure the component library is accessible for testing.

As a DevOps engineer, when setting up the deployment process, I want to replicate the existing Colibri implementation so that I can minimize the support needed and streamline the workflow.

### Context

The Boreal component library is undergoing an alpha test phase. To facilitate this, there is a need to implement the publishing of various packages to NPM and deploy the associated Storybook documentation. The approach chosen is to replicate the existing implementation from the Colibri project to reduce the need for extensive DevOps support.

### Acceptance criteria

- Wrappers scripts have been integrated with the Turbo Repo orchestration tool.
- Packages to be published have been defined in the Boreal CL monorepo.
- Deployment and publishing process with the Turbo Repo orchestrator tool has been verified.
- Access to @telesign organization in NPM is verified through an active Portal's user.
- NPM Granular access token is created with a proper expiration date (90 days).
- Jenkins Job to sync repos between Bitbucket and GitHub has been created or updated from the existing Colibri project (DevOps dependency - see Jenkins Job).
- `apps/boreal-docs` codebase has been replicated to Telesign GitHub account (DevOps dependency - see GitHub - TeleSign/colibri-docs: The Colibri Documentation System is built using Storybook, providing an interactive environment for documenting components, design guidelines, and usage patterns.).
- Sync process has been validated (DevOps dependency).
- GitHub Pages deployment workflow has been created in the Boreal monorepo at the root of the `apps/boreal-docs` folder and synced across both platforms (Bitbucket and GitHub).
- Deployment and publishing process is documented in Confluence.

---

## [enhanced]

### Summary

Deliver two production-ready capabilities for the Boreal DS alpha phase:

1. **npm publishing** — automate the release of all four publishable packages to the `@telesign` npm organisation under the `alpha` dist-tag using `release-it` + Turborepo.
2. **Storybook deployment** — automate the build and deployment of `apps/boreal-docs` to GitHub Pages via a GitHub Actions workflow, kept in sync with Bitbucket via the existing Jenkins job.

---

### Background and context

The monorepo already contains per-package `.release-it.json` configs and root-level `release:*` scripts. What is missing is:

- A `release` task in `turbo.json` that orchestrates the build pipeline before a release runs.
- A GitHub Actions workflow file (`.github/workflows/deploy-docs.yml`) that builds and deploys the Storybook static site.
- DevOps provisioning of the Jenkins Bitbucket→GitHub sync job pointing to the new `boreal-ds` GitHub repository.
- A verified npm granular access token stored as a GitHub Actions secret.

The release strategy is documented in `.ai/guidelines/release-process.md`. All alpha releases must run from the `release/current` branch, use the `--preRelease=alpha` flag, and publish under the `alpha` dist-tag.

---

### Publishable packages

| Package        | npm name                            | `.release-it.json` location                        |
| -------------- | ----------------------------------- | -------------------------------------------------- |
| Design tokens  | `@telesign/boreal-style-guidelines` | `packages/boreal-styleguidelines/.release-it.json` |
| Web Components | `@telesign/boreal-web-components`   | `packages/boreal-web-components/.release-it.json`  |
| React wrappers | `@telesign/boreal-react`            | `packages/boreal-react/.release-it.json`           |
| Vue wrappers   | `@telesign/boreal-vue`              | `packages/boreal-vue/.release-it.json`             |

`apps/boreal-docs` and `examples/react-testapp` are **never published to npm** — they are private development apps.

---

### Scope of work

#### 1. Turborepo integration for release pipeline (Developer)

Add a `release` task to `turbo.json` that enforces the correct build dependency order before any package is released. The task must be non-cacheable (releases are side-effectful) and must run after all upstream `build` tasks are complete.

**File to modify:** `turbo.json`

```json
// Add inside the "tasks" object:
"release": {
  "dependsOn": ["^build"],
  "cache": false,
  "outputs": []
}
```

> **Note:** `release-it` is an interactive CLI tool. The Turbo task only ensures the dependency graph is built before the release command runs. The actual release is triggered manually by an engineer via the root `release:*` scripts (see §4 — Release commands).

#### 2. Per-package `publishConfig` verification (Developer)

Confirm every publishable package declares `"publishConfig": { "access": "public" }` in its `package.json`. If any are missing, add the field.

**Files to check/modify:**

- `packages/boreal-styleguidelines/package.json`
- `packages/boreal-web-components/package.json`
- `packages/boreal-react/package.json`
- `packages/boreal-vue/package.json`

#### 3. GitHub Actions workflow — Storybook deployment (Developer)

Create a GitHub Actions workflow that builds `apps/boreal-docs` and deploys the `storybook-static/` output to GitHub Pages. The workflow is stored inside the monorepo so it is synced to GitHub via the Jenkins job.

**File to create:** `.github/workflows/deploy-docs.yml`

```yaml
name: Deploy Storybook to GitHub Pages

on:
  push:
    branches:
      - release/current
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: true

jobs:
  build:
    name: Build Storybook
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version-file: .node-version

      - name: Setup pnpm
        uses: pnpm/action-setup@v4

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Build dependency packages
        run: pnpm turbo run build --filter=@telesign/boreal-docs...

      - name: Build Storybook
        run: pnpm --filter @telesign/boreal-docs run build

      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: apps/boreal-docs/storybook-static

  deploy:
    name: Deploy to GitHub Pages
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

**GitHub repository settings required (DevOps):**

- Enable GitHub Pages and set source to "GitHub Actions" (Settings → Pages → Source).
- Store the npm token as a repository secret named `NPM_TOKEN` (needed only if a future automated npm publish job is added to the workflow).

#### 4. Release commands reference (Developer, for documentation)

All releases must run from the `release/current` branch with a clean working directory:

```bash
git checkout release/current && git pull

# Dry-run first (always)
pnpm --filter @telesign/boreal-style-guidelines run release -- --dry-run --preRelease=alpha
pnpm --filter @telesign/boreal-web-components  run release -- --dry-run --preRelease=alpha
pnpm --filter @telesign/boreal-react           run release -- --dry-run --preRelease=alpha
pnpm --filter @telesign/boreal-vue             run release -- --dry-run --preRelease=alpha

# Real release (in dependency order)
pnpm release:all -- --preRelease=alpha
```

#### 5. npm access token (Engineer / DevOps)

- Go to [npmjs.com](https://www.npmjs.com) → Account → Access Tokens → Generate New Token.
- Select **Granular Access Token**.
- Set expiration to **90 days**.
- Scope: **Read and write** for the `@telesign` organisation.
- Store the token:
  - Locally in `~/.npmrc` as `//registry.npmjs.org/:_authToken=<token>` for manual releases.
  - As a GitHub Actions secret named `NPM_TOKEN` in the `boreal-ds` GitHub repository.

#### 6. Jenkins Bitbucket→GitHub sync (DevOps)

Replicate or update the existing Colibri sync job at:
[https://jenkins2.c11.telesign.com/job/Builds/job/Utilities/job/TS_DEV_github_sync/](https://jenkins2.c11.telesign.com/job/Builds/job/Utilities/job/TS_DEV_github_sync/)

The new job must:

- Mirror Bitbucket repository: `https://bitbucket.c11.telesign.com/scm/san/boreal-ds.git`
- Target GitHub repository: `https://github.com/TeleSign/boreal-ds` (to be created by DevOps; see [colibri-docs](https://github.com/TeleSign/colibri-docs) as a reference)
- Sync all branches (including `release/current`) and all tags.
- Trigger automatically on every Bitbucket push (webhook or polling).

#### 7. GitHub repository provisioning (DevOps)

Create a new GitHub repository under the `TeleSign` organisation:

- Repository name: `boreal-ds`
- Visibility: **Private** (sync only; GitHub Pages will be the only public surface)
- Enable GitHub Pages (source: GitHub Actions)
- Add `NPM_TOKEN` as a repository secret

---

### Acceptance criteria

All criteria are independently verifiable. Group by responsible party.

#### Developer

- [ ] `turbo.json` contains a `release` task with `"dependsOn": ["^build"]` and `"cache": false`.
- [ ] All four publishable `package.json` files declare `"publishConfig": { "access": "public" }`.
- [ ] `.github/workflows/deploy-docs.yml` exists at the monorepo root and its content matches the template in §3.
- [ ] Running `pnpm release:wc -- --dry-run --preRelease=alpha` from `release/current` prints a valid version bump preview and exits cleanly.
- [ ] Running `pnpm build` from the workspace root completes without errors and respects dependency order (styles → web-components → react/vue).

#### DevOps

- [ ] Jenkins sync job is running and has successfully pushed at least one commit from Bitbucket to `https://github.com/TeleSign/boreal-ds`.
- [ ] A push to `release/current` on Bitbucket triggers the Jenkins sync within 5 minutes, which in turn triggers the GitHub Actions workflow.
- [ ] The GitHub Actions `deploy-docs.yml` workflow completes successfully and the Storybook is accessible at the GitHub Pages URL.
- [ ] `NPM_TOKEN` repository secret is set in GitHub and the token grants write access to `@telesign` on npmjs.com.

#### Engineer (manual release verification)

- [ ] `pnpm release:all -- --preRelease=alpha` successfully publishes a new alpha version of all four packages to npmjs.com.
- [ ] Running `npm install @telesign/boreal-web-components@alpha` in a clean directory installs the newly published version.
- [ ] All four packages appear in the `@telesign` organisation on npmjs.com under the `alpha` dist-tag.

---

### Non-functional requirements

- **Security:** The npm token must have the narrowest possible scope (write access to `@telesign` only). Rotate every 90 days; set a calendar reminder at token creation.
- **Idempotency:** Re-running the deploy workflow on the same commit must produce the same GitHub Pages output without side effects.
- **Observability:** The GitHub Actions workflow must surface build errors in the PR/push check UI. Failed builds must not silently succeed.
- **Branch protection:** The `release/current` branch must require a passing CI check before any merge is allowed (configure in GitHub repository settings).

---

### Documentation

Update Confluence with:

1. The full alpha release runbook (commands, branch requirements, dry-run steps).
2. The GitHub Pages URL and how to access the deployed Storybook.
3. The npm token rotation procedure and the secret storage locations.
4. The Jenkins sync job URL and how to verify a successful sync.

Reference document: `.ai/guidelines/release-process.md` (already exists in the monorepo — keep it in sync with Confluence).
