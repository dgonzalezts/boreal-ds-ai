---
title: Integrate @telesign/boreal-vue and vue-testapp into monorepo
status: done
created: 2026-03-12
---

## Context

The `feature/2-way-binding` branch contains two logically distinct commits:

1. **`chore(vue): * create vue test app`** — 38-file scaffold for `examples/vue-testapp` (Vue 3 + Vite + Vitest). This is the one we want.
2. **`feat(web-components): * created 2-way binding for the banner`** — refactors `bds-banner` (`isOpen` prop, `toggle` event, `componentModels` in vue-output-target). **This is NOT being merged.**

`packages/boreal-vue/` has **zero diffs** between `main` and `feature/2-way-binding` — the wrapper was never regenerated with `componentModels`. The `v-model` in `App.vue` is therefore a **silent no-op** on the current codebase (Vue binds `modelValue`/`update:modelValue`, the banner ignores both, no errors). A straight cherry-pick of `examples/vue-testapp/` is safe — no adaptation of `App.vue` required beyond removing boilerplate scaffold components.

**Wrapper-level bug discovered:** `@stencil/vue-output-target` is classified as `devDependencies` in `packages/boreal-vue/package.json`, but `dist/components.js` contains `import { defineContainer } from '@stencil/vue-output-target/runtime'` — a **runtime import** that consumers need resolved. This mirrors how `boreal-react` correctly places `@stencil/react-output-target` in `dependencies`. This must be fixed before publishing.

Once the testapp is in place and the dependency bug is fixed, `@telesign/boreal-vue` (currently `0.0.1`, never released) can be published. `first-alpha-release.md` (status `done`) must be extended with Vue release steps.

---

## Level of Effort

| Task | Effort | Reason |
|---|---|---|
| Port vue-testapp scaffold (38 files) | **Low** | Straight cherry-pick — wrapper unchanged, no App.vue surgery needed |
| Strip scaffold boilerplate from `App.vue` | **Low** | Remove HelloWorld/TheWelcome imports; keep BdsBanner + BdsTypography |
| Fix `@stencil/vue-output-target` dependency classification | **Low** | Move from `devDependencies` → `dependencies` in `packages/boreal-vue/package.json` |
| Remove `MyComponent` stub from `boreal-vue` | **Low** | Drop stub from `lib/components.ts`, rebuild dist |
| Wire `validate:pack:vue` pipeline | **Medium** | Mirror `validate:pack:react` pattern — scripts in testapp + turbo task verification |
| Update `first-alpha-release.md` | **Low** | Additive steps; clear pattern from existing React release steps |

**Overall: Low — estimated 1–2 hours**

---

## Critical Files

| File | Action |
|---|---|
| `examples/vue-testapp/` (38 files) | Port from `feature/2-way-binding` via `git checkout` |
| `examples/vue-testapp/src/App.vue` | Strip HelloWorld/scaffold imports; keep BdsBanner + BdsTypography |
| `examples/vue-testapp/src/components/` | Delete — boilerplate scaffold, not needed |
| `examples/vue-testapp/package.json` | Add `validate:pack:vue` script (mirror react-testapp) |
| `packages/boreal-vue/package.json` | Move `@stencil/vue-output-target` → `dependencies` |
| `packages/boreal-vue/lib/components.ts` | Remove `MyComponent` stub export |
| `packages/boreal-vue/lib/index.ts` | Verify no re-export of `MyComponent` |
| `turbo.json` | Verify `validate:pack:vue` task config matches `validate:pack:react` |
| `package.json` (root) | Verify or add `"validate:pack:vue": "turbo run validate:pack:vue"` |
| `.ai/plans/first-alpha-release.md` | Extend with Vue release steps (Steps 9–11) |
| `.ai/plans/INDEX.md` | Update `first-alpha-release.md` row back to In Progress |

---

## Implementation Steps

### Step 1 — Port the vue-testapp scaffold

Cherry-pick only the `vue-testapp` files from the branch:

```bash
git checkout feature/2-way-binding -- examples/vue-testapp/
```

> **Before committing:** Fetch latest versions for all dev dependencies from the npm registry (per CLAUDE.md rules) and align to verified versions.

### Step 2 — Strip scaffold boilerplate from `App.vue`

The `v-model="showBanner"` is harmless (silent no-op — wrapper has no `componentModels`). The only cleanup needed:

- Remove any imports of Vue CLI scaffold components (HelloWorld, TheWelcome, WelcomeItem, icon SVGs from `src/components/`)
- Delete `examples/vue-testapp/src/components/` directory entirely
- Keep BdsBanner + BdsTypography usage as-is

**Pass criterion:** dev server starts, both components render without console errors.

### Step 3 — Fix `@stencil/vue-output-target` dependency classification

In `packages/boreal-vue/package.json`:

- Move `@stencil/vue-output-target` from `devDependencies` → `dependencies`
- This matches the pattern established by `boreal-react` (`@stencil/react-output-target` is in `dependencies`)
- Required because `dist/components.js` contains a runtime `import { defineContainer } from '@stencil/vue-output-target/runtime'` that consumers must resolve

> Fetch the latest version from npm registry before writing the version string.

### Step 4 — Remove `MyComponent` stub from `packages/boreal-vue`

1. Read `packages/boreal-vue/lib/components.ts` — confirm `MyComponent` is present
2. Remove the `MyComponent` `defineContainer` call and its `defineCustomElement` import
3. Read `packages/boreal-vue/lib/index.ts` — verify it only re-exports from `./components` and `./plugin` (no direct `MyComponent` export)
4. Rebuild: `pnpm build --filter=@telesign/boreal-vue` to regenerate `dist/`

### Step 5 — Wire `validate:pack:vue` in the monorepo

1. Read `examples/react-testapp/package.json` — identify the `validate:pack:react` script pattern
2. Add equivalent `validate:pack:vue` script to `examples/vue-testapp/package.json`
3. Read `turbo.json` — verify `validate:pack:vue` task has correct `dependsOn`, `inputs`, `outputs` (mirror `validate:pack:react`)
4. Read root `package.json` — verify or add `"validate:pack:vue": "turbo run validate:pack:vue"`

### Step 6 — Update `first-alpha-release.md`

1. Change `status: done` → `status: in progress`
2. Add after the existing Step 8 (React release):

**Step 9 — Pre-publish gate: validate Vue artifact**
Run `pnpm validate:pack:vue`. Packs `@telesign/boreal-vue` into `.tgz`, installs into `examples/vue-testapp`, builds. Pass criteria: exit 0, no import resolution errors.

**Step 10 — Release `@telesign/boreal-vue`**
From `packages/boreal-vue`, run `release-it --increment=minor --tag alpha`. Publishes `0.1.0-alpha.0` to npm under `@telesign` scope.

**Step 11 — Post-release verification**
Install from npm: `npm install @telesign/boreal-vue@alpha`. Confirm `BdsBanner` and `BdsTypography` imports resolve and types are correct.

3. Move `first-alpha-release.md` row in `INDEX.md` from **Done** → **In Progress**.

---

## Verification

| Check | Command | Pass Criteria |
|---|---|---|
| Full workspace build | `pnpm build` | `boreal-vue` builds after `boreal-web-components` — exit 0 |
| Vue testapp dev server | `pnpm dev --filter=vue-testapp` | BdsBanner + BdsTypography render, no console errors |
| Validate pipeline | `pnpm validate:pack:vue` | Tarball installs, testapp builds — exit 0 |
| Unit tests | `pnpm test --filter=vue-testapp` | Vitest spec passes |
