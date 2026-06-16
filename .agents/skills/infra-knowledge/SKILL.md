---
name: infra-knowledge
description: Domain knowledge for CI/CD, Turborepo pipelines, release workflows, build tooling, and framework wrapper validation in Boreal DS. Covers Turbo PTY hang, Stencil dist copy, SCSS paths, scripts-boreal pipeline, release-it, Chromatic deployment, GitHub Actions debugging, and the validate:pack consumer simulation workflow. Load proactively for build, CI, release, or wrapper validation tasks.
---

# Infra Knowledge — Boreal DS

## Primary Reference

[`ai-docs/guidelines/development-standards.md`](../../../ai-docs/guidelines/development-standards.md) is the project's primary rules document. Read §4 (testing standards, CI pipeline) and §6–8 (git workflow, PR process, CI/CD) before working on build, release, or CI tasks. This skill provides scope-specific patterns and gotchas that complement — not replace — those rules.

**Directional rule:** procedures and patterns (how to fix a Turbo hang, how to run validate:pack) → live here. Rules, rationale, and constraints (release ordering, CI requirements) → live in `development-standards.md`.

Also read before working on build/CI/release:

- `ai-docs/guidelines/release-process.md` — step-by-step release runbook
- `ai-docs/guidelines/scripts-boreal.md` — custom monorepo tooling
- `ai-docs/guidelines/cicd-dependency-installation.md` — CI dependency installation patterns

---

## Turborepo — `persistent: true` PTY Hang

`persistent: true` implies `"interactive": true` by default. In headless environments (GitHub Actions, Docker, any shell without a controlling TTY) and on Windows with a cold Turbo daemon, PTY allocation deadlocks silently — no output, no error, never starts.

**Fixes (apply both; they are complementary):**

1. Add `"interactive": false` to any persistent dev task in `turbo.json`:

```json
"dev": { "dependsOn": ["^build"], "persistent": true, "interactive": false, "cache": false }
```

2. Bypass Turbo for primary dev workflows in root `package.json`:

```json
"dev:components": "pnpm --filter=@telesign/boreal-style-guidelines build && pnpm --filter=@telesign/boreal-web-components dev"
```

**Race condition:** If a package's `dev` script is just an alias for `build` (e.g. `"dev": "rimraf dist && build"`), running `pnpm dev` in parallel causes the `rimraf dist` to run while another package's dev watcher reads from that dist. Remove the `dev` script from packages without a real watch process.

---

## Stencil `dist` Output Target — Namespace Subfolder Placement

Stencil places `copy` entries with a relative `dest` path inside `dist/<namespace>/`, not at `dist/`. For `boreal-web-components` the namespace is `"boreal-web-components"`, so `dest: 'css'` lands at `dist/boreal-web-components/css/` instead of `dist/css/`.

`packages/boreal-web-components/scripts/postbuild.js` corrects this via the `"postbuild"` npm lifecycle hook. **Never remove the `"postbuild"` key from `package.json` scripts** — a stale `dist/` from a previous build will mask the regression. Always run `rm -rf dist` before testing this path.

`scripts-boreal/bin/publish.js` packs already-built artifacts and performs no build step. Build orchestration belongs in root `package.json` via Turborepo.

---

## Wrapper Validation — Consumer Simulation Workflow

Run after every component is complete and before any release.

### Interactive validation (dev)

```bash
# React
pnpm dev:pack:react
# Add the component to examples/react-testapp/src/App.tsx
# Import from @telesign/boreal-react; render with default, all variants, disabled, event binding, slot usage
# Verify in browser under all four themes: data-theme = connect | engage | protect | proximus

# Vue (once available)
pnpm dev:pack:vue
# Add to examples/vue-testapp/src/App.vue; verify v-model binding when applicable
```

### CI validation (required before marking complete)

```bash
pnpm validate:pack:react && pnpm validate:pack:vue
```

Both must exit 0. These commands pack built artefacts into `.tgz` files, install them in the example apps, and run `pnpm build` to confirm the published package is consumable.

**Cleanup:** Remove test component usage from `App.tsx` and `App.vue` before committing. Example apps are blank playgrounds, not persistent demos. `package.json` and `pnpm-lock.yaml` are auto-restored on pipeline exit — verify with `git status` before committing.

**Pipeline mechanics:** `scripts-boreal/README.md` is the authoritative reference.

### Turborepo task graph

`validate:pack:react` has `"dependsOn": ["@telesign/boreal-web-components#build"]` in `turbo.json` — Turbo ensures the build runs first. The cache means only one actual build runs even when `validate:all` invokes all three framework validations.

`release:all` sequence: `release:styles → release:wc → validate:all → release:react → release:vue`

---

## SCSS Paths — Windows Backslash Fix

`path.resolve` returns OS-native separators — backslashes on Windows. Sass treats backslashes as escape characters and fails silently with `Can't find stylesheet to import at line 1:1` (line 1:1 = the `injectGlobalPaths` prepend — that error location is the diagnostic signal).

Always apply `.map(p => p.replace(/\\/g, '/'))` to path arrays in Stencil/Sass config:

```typescript
injectGlobalPaths: [
  resolve(styleGuidelinesDir, 'stencil/_index.scss'),
  resolve(__dirname, 'src/styles/_commons.scss'),
  resolve(__dirname, 'src/styles/_interactions.scss'),
].map(p => p.replace(/\\/g, '/')),
```

Also: `require.resolve()` is unreliable in pnpm workspaces on Windows/Linux CI — use `path.resolve` relative to a `__dirname` anchor instead.

---

## release-it + pnpm publish

`publishCommand` is **not** a valid release-it option — it is silently ignored and falls back to `npm publish`, bypassing pnpm and leaking `workspace:*` into the tarball.

**Correct npm block:**

```json
"npm": {
  "publish": true,
  "publishPath": ".",
  "tag": "alpha",
  "publishPackageManager": "pnpm",
  "publishArgs": ["--no-git-checks"]
}
```

`workspace:*` is resolved by pnpm at tarball creation time only — the `package.json` on disk is never modified. If `npm publish` runs instead, the raw `workspace:*` string leaks into the published tarball and the registry rejects it with a 400 error.

---

## Chromatic Deployment

pnpm does not auto-load `.env` files. Prefix the deploy script with `dotenv --` via `dotenv-cli`:

```json
"deploy:docs": "turbo run build --filter=@telesign/boreal-docs... && dotenv -- pnpm --filter @telesign/boreal-docs run chromatic"
```

Use `--storybook-build-dir=storybook-static` (not `--build-script-name`) — Turborepo owns the build step, enforcing the correct dependency order (`style-guidelines → web-components → boreal-docs`). Chromatic only uploads the pre-built output.

`storybook-static/**` must be declared as a build output in `turbo.json` or Turbo will not cache/restore it correctly.

---

## GitHub Actions — Windows/Linux Debug Technique

When a bug is Windows/Linux-only, create a temporary `workflow_dispatch` workflow directly via the GitHub web UI (not committed locally). Key options:

- `timeout-minutes: 1` on persistent/watch commands — lets them run long enough to observe startup behavior, then terminates cleanly
- `continue-on-error: true` — allows subsequent diagnostic steps to run

Add the workflow file to `.git/info/exclude` (not `.gitignore`) to keep it off local branches. Delete via GitHub web UI once diagnosed.

---

## Node.js Signal Handlers in Pipeline Scripts

Use `spawnSync` (not `execSync` or `async/await`) for cleanup in `SIGINT`/`SIGTERM` handlers — `async` handlers are unreachable once the event loop begins tearing down:

```js
import { spawnSync } from "node:child_process";
process.once("SIGINT", () => {
  spawnSync("git", ["checkout", "HEAD", "--", ...paths], {
    cwd: root,
    stdio: "pipe",
  });
  process.exit(1);
});
process.once("SIGTERM", () => {
  spawnSync("git", ["checkout", "HEAD", "--", ...paths], {
    cwd: root,
    stdio: "pipe",
  });
  process.exit(1);
});
```

If the pipeline is force-killed (`SIGKILL`), run `pnpm install` from the workspace root to relink workspace package symlinks. No other recovery step is needed.
