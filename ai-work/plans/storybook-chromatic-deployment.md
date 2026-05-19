---
status: done
---

# Storybook Deployment — Chromatic

## Context

`apps/boreal-docs` is the Storybook documentation site for the Boreal Design System. It depends on two internal workspace packages via `workspace:*`:

- `@telesign/boreal-style-guidelines`
- `@telesign/boreal-web-components`

The goal is to publish the Storybook to **Chromatic** — a Storybook-native hosting and visual testing service — so the documentation is accessible to the alpha test audience without requiring a local development environment.

**Why Chromatic:**

- Purpose-built for Storybook; zero hosting configuration
- Free tier: 5,000 snapshots/month, unlimited collaborators, unlimited projects
- Works without any CI pipeline — the CLI publishes from any machine with the repo checked out
- Natively supports Bitbucket Pipelines when CI is needed (no GitHub required)
- Per-branch preview URLs at no extra cost
- `@chromatic-com/storybook` addon is already installed in `apps/boreal-docs`

**Architecture:** Turborepo owns the build step (`style-guidelines → web-components → boreal-docs`). Chromatic receives the pre-built `storybook-static/` output via `--storybook-build-dir` and handles only the upload and hosting. The two concerns are cleanly separated.

**Alpha prerequisite:** Alpha npm packages (`@telesign/boreal-style-guidelines`, `@telesign/boreal-web-components`) must be published at least once before the Chromatic deployment is meaningful to consumers. However, the Chromatic build itself resolves `workspace:*` locally — it does not require packages to be on npm.

---

## Alpha Tasks (Manual — No CI Required)

### Task 1 — Update `turbo.json`

**File:** [`turbo.json`](../../turbo.json)

Two changes:

**1a. Add `storybook-static/**`to`build` outputs:\*\*

```json
"build": {
  "dependsOn": ["^build"],
  "outputs": [
    "dist/**",
    "loader/**",
    "components-build/**",
    ".stencil/**",
    "custom-elements.json",
    "storybook-static/**"
  ],
  "cache": true
}
```

This ensures Turborepo's cache includes the Storybook static build. Without it, Turborepo cannot restore or invalidate the Storybook output correctly.

**1b. Add a `release` task:**

```json
"release": {
  "dependsOn": ["^build"],
  "cache": false,
  "outputs": []
}
```

This enforces that all upstream `build` tasks complete before any `release` command runs. Required by the ticket acceptance criteria.

---

### Task 2 — Install the `chromatic` CLI

Install scoped to `apps/boreal-docs` only (not the workspace root — it is a docs-only dependency):

```bash
fnm use
pnpm add -D --filter @telesign/boreal-docs chromatic
```

**File modified:** [`apps/boreal-docs/package.json`](../../apps/boreal-docs/package.json)

> Note: `@chromatic-com/storybook` (the Storybook UI addon) is already installed. The `chromatic` CLI is a separate package that handles publishing.

---

### Task 3 — Add `chromatic` script to `apps/boreal-docs/package.json`

**File:** [`apps/boreal-docs/package.json`](../../apps/boreal-docs/package.json)

Add to `"scripts"`:

```json
"chromatic": "chromatic --exit-zero-on-changes --storybook-build-dir=storybook-static"
```

**Flag explanations:**

| Flag                                     | Purpose                                                                                                                                                          |
| ---------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--storybook-build-dir=storybook-static` | Tells Chromatic to upload the pre-built output from Turborepo. Chromatic does not re-build Storybook.                                                            |
| `--exit-zero-on-changes`                 | CI/script does not fail when visual changes are detected. Appropriate for a docs publishing workflow. Remove this flag when visual regression gating is adopted. |

---

### Task 4 — Add `deploy:docs` script to root `package.json`

**File:** [`package.json`](../../package.json) (root)

Add to `"scripts"`:

```json
"deploy:docs": "turbo run build --filter=@telesign/boreal-docs... && dotenv -- pnpm --filter @telesign/boreal-docs run chromatic"
```

The `...` suffix on the Turborepo filter means "this package and all its upstream dependencies." Turborepo executes the build in correct dependency order: `style-guidelines → web-components → boreal-docs`. `dotenv --` loads `.env` from the repo root and injects all variables before the Chromatic upload step. The Chromatic upload runs after the build chain completes.

---

### Task 5 — Update root `.gitignore`

**File:** [`.gitignore`](../../.gitignore)

Add `.vercel/` to prevent Vercel's local project config from being accidentally committed if `vercel link` is ever run:

```
.vercel/
```

---

### Task 6 — Remove stale `apps/boreal-docs/pnpm-lock.yaml`

The current branch tracks `apps/boreal-docs/pnpm-lock.yaml`, which is a stale artifact that conflicts with the root lockfile. Remove it:

```bash
git rm apps/boreal-docs/pnpm-lock.yaml
```

---

### Task 7 — One-time Chromatic project setup (manual)

1. Go to [chromatic.com](https://www.chromatic.com) and sign in (GitHub, GitLab, Bitbucket, or email account)
2. Create a new project — link it to the repository or use a generic token (email signup works without a Git provider connection)
3. Copy the generated **project token**
4. In Chromatic project settings → **Configuration**, set the base branch to `release/current` so it is treated as the accepted visual baseline
5. Store the token securely (e.g., in your local `.env` or password manager — do **not** commit it)

---

### Task 8 — Manual deploy runbook (alpha)

Run from the `release/current` branch with a clean working directory, **after** running `pnpm release:all`:

```bash
git checkout release/current && git pull

# Build all upstream deps + Storybook in dependency order
fnm use
pnpm turbo run build --filter=@telesign/boreal-docs...

# Publish to Chromatic
CHROMATIC_PROJECT_TOKEN=<your-token> pnpm --filter @telesign/boreal-docs run chromatic
```

Or using the root shortcut (Task 4), with the token stored in `.env` at the repo root:

```bash
pnpm deploy:docs
```

Chromatic outputs:

- A **build URL** unique to this commit (permanent)
- A **branch URL** that always points to the latest build on `release/current`

Share the branch URL with the alpha audience — it stays stable across deploys.

---

## Acceptance Criteria (Alpha)

- [ ] `turbo.json` has `release` task with `"dependsOn": ["^build"]` and `"cache": false`
- [ ] `turbo.json` `build` outputs include `storybook-static/**`
- [ ] `apps/boreal-docs/package.json` has `chromatic` in `devDependencies` and a `chromatic` script
- [ ] Root `package.json` has `deploy:docs` script
- [ ] `pnpm turbo run build --filter=@telesign/boreal-docs...` completes without errors from `release/current`
- [ ] `pnpm deploy:docs` (with token set) completes and outputs a Chromatic URL
- [ ] Storybook renders correctly at the published Chromatic URL

---

## Next Steps — CI Pipeline Integration

When CI becomes available (Bitbucket Pipelines runners provisioned, or a GitHub mirror is set up), the manual deploy runbook can be replaced by an automated pipeline. Two options are described below in priority order.

---

### Option A — Bitbucket Pipelines (preferred, no GitHub required)

Chromatic natively supports Bitbucket Pipelines. Add a `bitbucket-pipelines.yml` at the monorepo root:

```yaml
image: node:22

definitions:
  caches:
    pnpm: $HOME/.local/share/pnpm/store

pipelines:
  branches:
    release/current:
      - step:
          name: Publish Storybook to Chromatic
          caches:
            - node
            - pnpm
          script:
            - corepack enable
            - fnm use || true
            - pnpm install --frozen-lockfile
            - pnpm turbo run build --filter=@telesign/boreal-docs...
            - pnpm --filter @telesign/boreal-docs run chromatic
```

**Secret storage:** In Bitbucket repository settings → **Repository variables**, add:

| Variable                  | Value                                  | Secured |
| ------------------------- | -------------------------------------- | ------- |
| `CHROMATIC_PROJECT_TOKEN` | Project token from Chromatic dashboard | Yes     |

The Chromatic CLI reads `CHROMATIC_PROJECT_TOKEN` automatically — no flag needed.

**Prerequisites for this option:**

- Bitbucket Pipelines runners (Docker agents) must be provisioned on the on-prem instance. Verify with DevOps.
- The Bitbucket repository must be linked to the Chromatic project (for PR status checks to appear in Bitbucket). This is configured in Chromatic project settings → Git provider.

**What this enables:**

- Auto-deploy on every push to `release/current`
- PR status checks in Bitbucket showing Chromatic build pass/fail
- Per-branch preview URLs for every feature branch

---

### Option B — GitHub Actions via Jenkins sync (fallback)

If Bitbucket Pipelines is not available, mirror the monorepo to GitHub via the existing Jenkins sync job and trigger Chromatic from GitHub Actions.

**File to create:** `.github/workflows/chromatic.yml`

```yaml
name: Publish Storybook to Chromatic

on:
  push:
    branches:
      - release/current
  workflow_dispatch:

jobs:
  chromatic:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version-file: .node-version

      - name: Setup pnpm
        uses: pnpm/action-setup@v4

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Build Storybook via Turborepo
        run: pnpm turbo run build --filter=@telesign/boreal-docs...

      - name: Publish to Chromatic
        run: pnpm --filter @telesign/boreal-docs run chromatic
        env:
          CHROMATIC_PROJECT_TOKEN: ${{ secrets.CHROMATIC_PROJECT_TOKEN }}
```

> `fetch-depth: 0` is required — Chromatic walks the full git history to power TurboSnap change detection. Shallow clones (`fetch-depth: 1`, the default) break this.

**Secret storage:** In the GitHub repository settings → Secrets → Actions, add `CHROMATIC_PROJECT_TOKEN`.

**DevOps dependencies for this option:**

| Item                                                                   | Owner     |
| ---------------------------------------------------------------------- | --------- |
| `TeleSign/boreal-ds` GitHub repository creation                        | DevOps    |
| Jenkins Bitbucket→GitHub sync job (mirror of the existing Colibri job) | DevOps    |
| `CHROMATIC_PROJECT_TOKEN` GitHub Actions secret                        | Developer |

---

## Files Summary

| File                                                                   | Action                                                      | Phase         |
| ---------------------------------------------------------------------- | ----------------------------------------------------------- | ------------- |
| [`turbo.json`](../../turbo.json)                                       | Add `release` task + `storybook-static/**` to build outputs | Alpha         |
| [`apps/boreal-docs/package.json`](../../apps/boreal-docs/package.json) | Add `chromatic` devDependency + `chromatic` script          | Alpha         |
| [`package.json`](../../package.json)                                   | Add `deploy:docs` root script                               | Alpha         |
| [`.gitignore`](../../.gitignore)                                       | Add `.vercel/`                                              | Alpha         |
| `apps/boreal-docs/pnpm-lock.yaml`                                      | Remove from git tracking (`git rm`)                         | Alpha         |
| `pnpm-lock.yaml` (root)                                                | Auto-updated by pnpm after chromatic install                | Alpha         |
| `bitbucket-pipelines.yml`                                              | Create at repo root                                         | CI — Option A |
| `.github/workflows/chromatic.yml`                                      | Create                                                      | CI — Option B |
