---
ticket: —
status: concluded
---

# Tree-shaking review — `@telesign/boreal-web-components` and the React/Vue wrappers

> Audience: engineers preparing the conversation with a future consumer team.
> Scope: review only. No library source, `package.json` or build config was changed. The only repo changes are the measurement harness and playground examples listed under "Artifacts".

## Verdict

**The library is built to be tree-shakable, but a consumer cannot get tree-shaking today through either wrapper.**

| Consumption path | Tree-shakes today? | Evidence |
| ---------------- | ------------------ | -------- |
| `@telesign/boreal-web-components/components/<tag>.js` (per-component subpath, direct) | **Yes** | `bds-button` 18.2 kB gzip vs. 223.5 kB for every component |
| `@telesign/boreal-react` named imports | **No** (one `BdsButton` ≈ whole library) | 284.3 kB gzip initial vs. 286.4 kB for all components |
| `@telesign/boreal-vue` named imports | **No**, and an unused import also ships everything | 253.5 kB gzip for one button, and for an unused import |
| `ToastService` via `@telesign/boreal-react` | **Yes** | 2.1 kB initial, 11.6 kB with its lazy chunk |
| `ToastService` via `@telesign/boreal-vue` | **No** | 232.4 kB gzip initial |
| Lazy loader (`defineCustomElements`, `dist/`) | n/a (runtime lazy loading, not tree-shaking) | ~6.6 kB gzip eager entry; components fetched on first use |

Two defects, both in packaging rather than in component code, and **both must be fixed together** (either alone changes nothing):

1. **`/*@__PURE__*/` annotations are stripped from the wrapper output.** The generated `lib/` sources carry them (`packages/boreal-react/lib/components/components.ts:176`), but the wrapper `tsconfig` extends the root config with `removeComments: true`, so `dist/` has 0 occurrences. Every `createComponent(...)` / `defineContainer(...)` call at module top level is therefore treated as a side effect and keeps its `defineBdsX` import alive. The Vue output target emits no annotation at all.
2. **No `sideEffects` field on `@telesign/boreal-web-components`** (and none on `@telesign/boreal-vue`; `@telesign/boreal-react` has `"sideEffects": false`). Without it, bundlers keep every imported `components/bds-*.js` module even when its exports are unused.

## How it was measured

- Harness: `examples/shared/measure-bundle.mjs`, driven per playground by `pnpm size` and `pnpm size:check`.
- Each scenario in `examples/{react,vue}-testapp/bundle-size/scenarios/` is built as its own Vite app entry (Vite 7.3.1 / Rollup 4.57.1, esbuild minify, `write: false`).
- Sizes are minified. "Initial" = entry chunk plus its static imports; "total" adds lazy chunks. gzip level 9; brotli is also printed.
- Built from the existing `dist/` and `components-build/` outputs (timestamps 2026-10-02; git tree clean). Re-run `pnpm build` first if the library changed since.
- Framework runtime is included in every number. Baselines: React 19 + react-dom = 58.6 kB gzip, Vue 3 = 23.6 kB gzip. **Library cost = scenario minus baseline.**
- Only Vite/Rollup was tested. Webpack, esbuild and Rspack behave the same in principle (they honor `sideEffects` and `#__PURE__`), but that is **not verified**.

## Results

### Current state — through the wrappers (gzip, initial)

| Scenario | React | Vue | Library share React / Vue |
| -------- | ----- | --- | ------------------------- |
| baseline (framework only) | 58.6 kB | 23.6 kB | — |
| unused `import { BdsButton }` | 58.6 kB | **253.5 kB** | 0 / 229.9 kB |
| `BdsButton` | 284.3 kB | 253.5 kB | 225.7 / 229.9 kB |
| `BdsButton` + `BdsBadge` + `BdsDivider` | 284.3 kB | 253.5 kB | 225.7 / 229.9 kB |
| `BdsDatePicker` | 284.3 kB | 253.5 kB | 225.7 / 229.9 kB |
| `BdsTable` | 284.3 kB | 253.5 kB | 225.7 / 229.9 kB |
| `ToastService` only | 2.1 kB (11.6 kB total) | 232.4 kB | — / 208.8 kB |
| every export (`import * as`) | 286.4 kB | 255.5 kB | 227.8 / 231.9 kB |

Every non-trivial scenario costs 99.1% of the full library. React's only win is that `unused-import` is free, thanks to `sideEffects: false` on `boreal-react`.

### What the library can do — direct per-component imports (gzip)

| Entry | gzip | Notes |
| ----- | ---- | ----- |
| `bds-badge` | 10.6 kB | Floor: Stencil runtime plus shared chunks |
| `bds-button` | 18.2 kB | |
| `ToastService` (`components/index.js`) | 11.6 kB | DOMPurify is a lazy chunk |
| `bds-date-picker` | 75.0 kB | date-fns, floating-ui, calendar grid |
| `bds-table` | 83.7 kB | Plus a lazy chunk; pulls nested children via recursive `defineCustomElement` |
| all 81 component entries | 223.5 kB | |

### Proof that the two defects are the whole cause

Same scenarios, re-bundled with the two fixes simulated at build time (a plugin that injects `/*@__PURE__*/` into the wrapper output, plus `moduleSideEffects: false` for the web-components package). Nothing in the repo was modified.

| Scenario | Current | PURE only | `sideEffects` only | Both |
| -------- | ------- | --------- | ------------------ | ---- |
| React `BdsButton` | 285.3 kB | 279.7 kB | 285.3 kB | **77.7 kB** (library share 19.1 kB) |
| React `BdsDatePicker` | 285.3 kB | 279.9 kB | 285.3 kB | **135.1 kB** (76.5 kB) |
| Vue `BdsButton` | 254.4 kB | — | — | **46.4 kB** (22.8 kB) |
| Vue `BdsDatePicker` | 254.4 kB | — | — | **103.4 kB** (79.8 kB) |

The "both" figures land within ~1 kB of the direct-import numbers above, so no third problem hides behind these two. Vue "PURE only" and "`sideEffects` only" columns were not run separately.

**Not verified: `BdsTable` with both fixes.** Rollup 4.57.1 crashes with `dependentEntriesByModule.get is not a function or its return value is not iterable` when `moduleSideEffects` is `false` for the web-components modules and `BdsTable` is imported through a wrapper. Direct `bds-table` with the same option builds fine, so the trigger is the table's dynamic import combined with the wrapper graph. Latest Rollup is 4.64.2; I did not test it. Treat this as a risk to check before shipping the fix, not as a conclusion about the cause.

## Strengths

1. **Per-component build output exists and is correct.** `dist-custom-elements` writes 81 `components-build/bds-*.js` files (plus 58 shared hashed chunks) with a `.d.ts` each, exposed through the `./components/*.js` subpath export. Each entry file is a one-line re-export from a shared hashed chunk.
2. **The underlying library tree-shakes well** when bypassing the wrappers (button 8% of the full bundle).
3. **Code splitting is already in place.** DOMPurify is a dynamic import, so `ToastService` and anything using the HTML handler defer it.
4. **ESM-only entry points for bundlers** (`import` condition and `module` field); no CommonJS path is needed for tree-shaking.
5. **React `ToastService` and unused imports already work**, which shows `sideEffects: false` on the wrapper is honored once annotations are fixed.
6. **Light DOM, styles compiled into each component chunk.** Component CSS is paid for per component, not per library.
7. **Alternative with a small eager cost exists:** the lazy loader path ships ~6.6 kB gzip eagerly and fetches each component (69 lazy entries, ~1 MB raw in total) on first render.

## Weaknesses and limits to communicate

1. **Wrapper tree-shaking is broken (above).** Today, adopting React or Vue costs 226–230 kB gzip of library regardless of what is used. Vue is worse: an unused import and `ToastService` alone also pay it.
2. **No size guard existed before this review.** Nothing in CI would have caught the `removeComments` regression.
3. **Dependencies are bundled, not external.** `components-build` contains zero bare imports, so `date-fns`, `@floating-ui/dom`, `@tanstack/virtual-core`, `dompurify` and the Stencil runtime are copied in. A consumer that also uses `date-fns` or DOMPurify ships two copies, and `externalRuntime: false` means mixing the loader path with the per-component path (or another Stencil library) loads the runtime twice.
4. **Floor is ~10.6 kB gzip** for the smallest component, because the Stencil runtime is included. "Pay per component" is true only above that floor.
5. **`defineCustomElement` is recursive.** A composite component pulls its children (`bds-table` is 83.7 kB, `bds-date-picker` 75.0 kB), so heavy components cannot be trimmed further by the consumer.
6. **Global CSS does not tree-shake.** `boreal.css` is 7.8 kB gzip and includes every theme. `global.css` (4.8 kB) plus one `theme-*.css` (~1.7 kB) is the leaner pairing; the docs and playgrounds import `boreal.css`.
7. **Side-effect-free status needs care when fixed.** `sideEffects: false` is only safe if no module relies on import-time registration. The wrappers call `defineCustomElement` explicitly, but the lazy-loader bootstrap (`dist/boreal-web-components/boreal-web-components.esm.js`) and any `./css/*` import must stay listed in a `sideEffects` array. This was not tested.
8. **Install weight differs from bundle weight.** `dist/` is ~22 MB on disk (`buildEs5: 'prod'` emits a full `esm-es5` copy). This affects installs and CI caches, not bundles.
9. **Observation, unverified:** in the root `exports["."]` entry, `types` is listed after `import`/`require`. TypeScript reads conditions in order, so type resolution for that entry may be fragile. Check before relying on it.

## Recommended follow-ups (not done; each needs its own task)

| # | Change | Where | Expected effect |
| - | ------ | ----- | --------------- |
| 1 | Keep `/*@__PURE__*/` in wrapper output: set `removeComments: false` in the wrapper tsconfigs, and add the annotation to the Vue output target's emitted `defineContainer(...)` calls | `packages/boreal-react/tsconfig.json`, Vue target output | Prerequisite for any shaking |
| 2 | Add a `sideEffects` field to `boreal-web-components` (list the loader bootstrap and CSS) and to `boreal-vue` | `package.json` files | Prerequisite for any shaking |
| 3 | Re-test `BdsTable` with 1 and 2 applied, on current Rollup/Vite | `examples/*/bundle-size` | Resolves the open crash risk |
| 4 | Flip the `enforce: false` rules in `budgets.json` to `true` and tighten the scenario ceilings | `examples/*/bundle-size/budgets.json` | Locks the fix in |
| 5 | Run `size:check` in CI | CI pipeline | Prevents regression |
| 6 | Decide whether dependencies should be external, and document the loader vs. per-component split | Stencil config, consumer docs | Removes duplicate-copy risk |

## Talking points for the consumer team

- "Today you should expect ~225 kB gzip of library per app on React and ~230 kB on Vue, regardless of how many components you import. We know why and have the fix scoped."
- "If bundle size is a hard constraint right now, the loader path costs ~6.6 kB up front and loads components on demand; the cost is network requests at render time instead of build-time shaking."
- "After the fix, expect roughly 19–23 kB for a button and ~77–80 kB for a date picker, on top of the framework."
- "Use named imports from the package root; avoid `import * as`."

## Artifacts

- `examples/shared/measure-bundle.mjs` — harness (report and `--check` modes; `enforce: false` rules print as known gaps).
- `examples/react-testapp/bundle-size/` and `examples/vue-testapp/bundle-size/` — 8 scenarios each plus `budgets.json`. Scenario ceilings are the current numbers plus 2%, rounded up to 1 kB, so they act as regression guards. The ratio rules that describe the *target* state are `enforce: false`.
- `pnpm size` and `pnpm size:check` scripts in both playground `package.json` files.
- Playground `App.tsx` / `App.vue` render three components by named import and list the validation steps.

## Not verified

- Browser rendering of the new playground sections (typecheck passed; the pages were not opened).
- A deliberate budget breach to confirm `--check` exits non-zero.
- Webpack, esbuild, Rspack, or Angular builds.
- Runtime behavior after applying the fixes (only bundle size was measured).
