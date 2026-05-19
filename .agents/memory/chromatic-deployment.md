# Chromatic Deployment — Mechanics and Gotchas

Source: EOA-10749 Storybook Chromatic deployment session (2026-03-11).

---

## pnpm does NOT auto-load `.env` files

pnpm is a package manager only — it has no built-in `.env` loading for script execution. The confusion arises from frameworks like Create React App and Vite that load `.env` files natively inside their own dev server and build tool processes.

**Verified via:** Official pnpm docs at https://pnpm.io/cli/run and https://pnpm.io/npmrc — neither mentions `.env` loading.

**Fix:** Prefix any script that requires env vars from `.env` with `dotenv --` via `dotenv-cli` (already installed at workspace root as `dotenv-cli`).

```json
"deploy:docs": "turbo run build --filter=@telesign/boreal-docs... && dotenv -- pnpm --filter @telesign/boreal-docs run chromatic"
```

The `dotenv --` only wraps the command it immediately precedes. The Turborepo build step before the `&&` runs without `.env` loading, which is correct — it does not need the token.

---

## Two-actor model: dotenv-cli and the Chromatic CLI

`dotenv-cli` and the Chromatic CLI have distinct, non-overlapping responsibilities:

| Actor | Role |
|---|---|
| `dotenv --` (dotenv-cli) | Loads ALL variables from `.env` into the child process environment |
| `chromatic` CLI | Reads `process.env.CHROMATIC_PROJECT_TOKEN` specifically from that environment |

pnpm is not aware of the variable name. It is the Chromatic CLI that knows to look for `CHROMATIC_PROJECT_TOKEN` in `process.env`.

---

## Chromatic CLI: `--storybook-build-dir` vs `--build-script-name`

These two flags represent entirely different workflows:

| Flag | Behavior |
|---|---|
| `--build-script-name=<name>` | Chromatic invokes the named npm script to build Storybook itself before uploading |
| `--storybook-build-dir=<dir>` | Chromatic skips the build entirely and uploads the pre-existing directory |

**Pattern used in Boreal DS:** `--storybook-build-dir=storybook-static`

Turborepo owns the build step (enforcing correct dependency order: `style-guidelines` → `web-components` → `boreal-docs`). Chromatic only uploads the pre-built output. Using `--build-script-name` would bypass Turborepo's dependency chain and risk uploading a Storybook built against un-built upstream packages.

The `chromatic` script in `apps/boreal-docs/package.json`:

```json
"chromatic": "chromatic --exit-zero-on-changes --storybook-build-dir=storybook-static"
```

Note: The Storybook build script in `apps/boreal-docs` is named `"build"`, not `"build-storybook"` (the Chromatic default). This is why `--build-script-name` would require an explicit name argument if the Chromatic-builds approach were ever adopted — but it is not.

---

## Turborepo: `storybook-static/**` must be declared as a build output

`storybook-static/**` was added to the `build` task outputs in `turbo.json`. Without this declaration:

- Turborepo cannot save the Storybook build artifact to its cache.
- On a CI cache hit, Turborepo skips the build step but does not restore the directory.
- The subsequent `chromatic` upload step fails because `storybook-static/` does not exist.

The outputs entry in `turbo.json`:

```json
"outputs": ["dist/**", "storybook-static/**"]
```

---

## Token storage pattern for local manual deploys

Three files govern token handling:

| File | Purpose | Committed? |
|---|---|---|
| `.env` (repo root) | Holds `CHROMATIC_PROJECT_TOKEN=<real-token>` | No — gitignored |
| `.env.example` (repo root) | Documents the variable with retrieval instructions | Yes |
| `.gitignore` | Ignores `.env` and `.env.local` | Yes |

`.env.example` content:

```dotenv
# Chromatic project token — required for `pnpm deploy:docs`
# To retrieve:
#   1. Log in to https://www.chromatic.com
#   2. Go to Manage → Configure
#   3. Copy the project token under the "Project" section
CHROMATIC_PROJECT_TOKEN="your-chromatic-project-token-here"
```

---

## Chromatic quickstart pattern is NOT suitable for ongoing use

Chromatic's quickstart instructs: `npx chromatic --project-token=<token>`. This is appropriate only for one-off account verification. It is wrong for ongoing use because:

- Chromatic invokes `build-storybook` (or a named script) itself, bypassing Turborepo entirely.
- Upstream packages (`style-guidelines`, `web-components`) may not be built when the build runs.
- The dependency chain that Turborepo enforces is the single source of truth for build correctness.

The correct ongoing workflow is always: **Turborepo builds → Chromatic uploads.**

---

## Affected files (EOA-10749)

| File | Change |
|---|---|
| `turbo.json` | Added `storybook-static/**` to `build` outputs; added `release` task |
| `apps/boreal-docs/package.json` | Added `chromatic` script |
| `package.json` (root) | Added `deploy:docs` script using `dotenv --` prefix |
| `.gitignore` | Added `.env` and `.env.local` entries |
| `.env.example` | Created with token retrieval instructions |
| `.ai/plans/storybook-chromatic-deployment.md` | Status set to done; runbook updated |
| `.ai/plans/INDEX.md` | Plan row moved to Done section |
