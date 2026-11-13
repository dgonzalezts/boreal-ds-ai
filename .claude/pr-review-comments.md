# PR review comments (drafts) — EOA-20193

Local drafts, not posted anywhere. Paste each comment on the anchor named in its heading (file, then the line or symbol). Commits are cited by subject, because hashes change if the branch is rebased again. The PR has 27 commits, roughly one per task, so reviewing commit by commit is the easiest way in.

Suggested order for reviewers: 0, then A (skim), then 1 to 4 (consumer-visible), then 5 to 9 (runtime and published output), then 10 to 14 (tooling and tests).

---

## 0. Review guide (general comment, or the first comment on the PR)

**How to read this PR (84 files, mostly mechanical).** About 2,300 of the changed lines are `pnpm-lock.yaml` and another 430 are new tests.

1. **Skim** the comment titled "Mechanical changes" (formatting and ESLint-driven edits): no behavior change.
2. **Review carefully** the three breaking changes listed in the description: Vue `BdsToggle` `v-model`, the `"false"` attribute string on form-associated components, and the narrowed type of `focusFromTriggerKey`.
3. **Review the runtime changes** that ship to consumers: `@colordx/core` 7, the `@tanstack/virtual-core` range, `@stencil/react-output-target` 1.8.1, the new `./components` export and the type-declaration fixes.
4. **Skim the tooling** (TypeScript 6, ESLint 10, Vitest 5, Vite 8, Storybook and Chromatic, pnpm 12): these affect contributors only.

Verification commands that passed on the final branch: `pnpm build` (7/7), `pnpm lint` (0 errors), `pnpm test` (378 suites, 4,967 tests), `pnpm validate:all`, `pnpm peers check`, `pnpm install --frozen-lockfile`.

---

## A. Mechanical changes (formatting and ESLint-driven): skim only

*Anchor: `apps/boreal-docs/src/components/story/FormDemo/FormDemo.ts` (first file of the reformat), or as a general comment.*

**Mechanical changes, no behavior change. You can skim these.**

1. **Prettier 3.9 reformat** (commit `style(multiple): reformat files with prettier 3.9`, 16 files): `FormDemo.ts` and 13 Storybook stories in `apps/boreal-docs`, plus `ITable.ts` and `bds-table.pin-offsets.spec.ts` in web-components. Line wrapping and whitespace only. Check: `pnpm format:check` passes in `boreal-docs` and `boreal-web-components`, or `git show -w <commit>` shows no non-whitespace change.
2. **`typescript-eslint` assertion cleanup** (commit `build(deps): update typescript-eslint and clear assertion errors`): 17 files in web-components lose casts the new rule flags as unnecessary (`this.el as HTMLElement`, `event as unknown as UIEvent`, `handler as EventListener`, `.filter(...) as HTMLElement[]`, `el as HTMLTableCellElement | undefined`). The expressions already have the target type, so the emitted code is identical. Files: `bds-button`, `bds-dropdown`, `bds-card`, `bds-pagination`, `bds-progress-bar`, `bds-tag`, `bds-color-picker`, `bds-calendar-grid`, `bds-date-picker`, `bds-file-picker`, `bds-radio-group`, `bds-select`, `bds-tag-field`, `bds-avatar`, `bds-grid-item`, `bds-tab-group` and `KeyboardController.ts`.
3. **The ESLint 10 upgrade itself** (commit `build(deps): upgrade eslint to 10`) changed only manifests and `pnpm-workspace.yaml`; no source needed editing.

**Not mechanical, with their own comments:** `bds-list-menu.tsx` (`hidden === false`), `bds-tree-menu-item.tsx` (type guard) and the `bds-select.tsx` typing change.

---

## 1. Breaking: Vue `BdsToggle` `v-model`

*Anchor: `packages/boreal-web-components/targets/vue-output-target.ts`, the new `bds-toggle` entry.*

`bds-toggle` was in the list of components whose model maps to `value`. A toggle keeps its state in `checked`, and its `value` is the string submitted with the form (`"on"` by default). So the bound model was a string, `true` set from code did not check the toggle, and a checked toggle submitted the model string instead of its `value`. The new entry maps the model to `checked`, read from `event.detail` because `checked` is a read-only prop for the wrapper.

**Breaking for Vue consumers** who compared the model to `"on"` or `""`; it is now `true` or `false`. Covered by `examples/vue-testapp/src/__tests__/v-model.spec.ts` (clicking gives `true` then `false`; setting the ref checks the toggle) and by the invariant in `component-models.spec.ts` (every component that emits `valueChange` has a wrapper model). I also confirmed it in a real browser through the pack-based Vue app.

---

## 2. Breaking: the string `"false"` on form-associated components (Stencil 4.45.2)

*Anchor: `packages/boreal-web-components/package.json`, the `@stencil/core` line. Add short follow-ups on `apps/boreal-docs/src/stories/forms/bds-file-uploader/bds-file-uploader.mdx` and `.../bds-date-picker.stories.ts`.*

The 4.45.1 pin of the baseline existed because 4.45.2 reads the attribute string `"false"` as `true` on form-associated components, so `<bds-file-picker disabled="false">` now disables the control and excludes it from form data. Typed values and properties are unaffected. This is upstream behavior (stenciljs/core pull request 6908), not a Boreal change.

I fixed every place in this repository that relied on the old reading: the three `bds-file-picker` specs (`multiple="false"`, `error="false"`, `disabled` toggled with `'true'` and `'false'` now use attribute presence), the `bds-file-uploader` MDX example (`hide="false"` removed) and the date-picker story (`with-time=${...}` became `?with-time=${...}`). I scanned the sources, stories and READMEs for other `attr="false"` strings: what is left is ARIA states (`aria-pressed`, `aria-checked`...), the SVG `focusable` attribute and `loading` on `bds-pagination` (not form-associated), none affected.

Please say if you know of consumer code or docs outside this repository that writes `="false"` on a form control.

---

## 3. Breaking (types): `focusFromTriggerKey` of `bds-list-menu`

*Anchor: `packages/boreal-web-components/src/components/actions/bds-list-menu/bds-list-menu/types/types.ts` (`ListMenuTriggerKey`), with a second comment on `bds-select.tsx` (`handleArrowNavigation`).*

The generated `components.d.ts` used `typeof KEYBOARD.ArrowDown | typeof KEYBOARD.ArrowUp` without importing `KEYBOARD`, so the parameter was silently `any` for consumers (and a `skipLibCheck: false` error). `ListMenuTriggerKey = 'ArrowDown' | 'ArrowUp'` is a plain literal union (a `typeof` expression would need an import that does not survive in the declaration). Callers that pass a `string` stop compiling, which is the point.

In `bds-select.tsx`, `handleArrowNavigation(key: ListMenuTriggerKey)` receives `event.key as ListMenuTriggerKey` at its single call site, which is only reached for ArrowDown and ArrowUp (`.set([KEYBOARD.ArrowDown, KEYBOARD.ArrowUp], ...)`); before, it compiled only because of the `any`.

---

## 4. Published type declarations: why a few files use relative paths

*Anchor: `packages/boreal-web-components/src/components/forms/bds-number-field/types/enum.ts` (and mention the other three: text-field and tag-field `enum.ts`, tag-field `types.ts`).*

The rest of the code uses the `@/` alias, and that stays. These four files **re-export** (`export { X } from ...`), and Stencil rewrites the alias in emitted `import` declarations but not in `export ... from`, so `dist/types` kept `'@/components/forms/common'`, which consumers cannot resolve. Relative paths there are the minimal fix. Similarly, `ValidationChangePayload` is now imported from `@/utils/form` (color-picker, number-field) and `EVENTS` from `@/utils/constants` (toast types): the `@/utils` barrel re-exports `./testing`, which dragged test helper declarations (`jest` namespace) into every consumer's program.

Verified with a scratch consumer outside the repository (packed tarball installed with its dependencies, TypeScript 6.0.3, `skipLibCheck: false`, importing `Components` and `JSX`): **14 errors before, 0 after**. Side effect: the generated duplicate type export `ValidationChangePayload1` disappears. A guard in the pack pipeline is drafted as a follow-up, not included.

---

## 5. Behavior-sensitive: `bds-list-menu.tsx` `hidden === false`

*Anchor: `bds-list-menu.tsx`, the first changed condition.*

TypeScript 6 types `HTMLElement.hidden` as `boolean | "until-found"`, so `!item.hidden` no longer passed the new lint rule. The five conditions now read `item.hidden === false` (visible) and `item.hidden !== false` (skip). In browsers `hidden` is always a boolean or `"until-found"`, so the result is the same as before; an `undefined` would now count as hidden in the skip branch, which cannot happen for DOM elements. Because this is the one non-cosmetic edit of the lint cleanup, I added `bds-list-menu.hidden-items.spec.ts` (30 tests at run time): initial focus target (selected, first, last, ArrowUp), page moves and tab stops with visible items, then the same cases with a selected, leading, trailing or all-hidden item.

---

## 6. Runtime dependency: `@colordx/core` 5 to 7 and the guard in `color-utils.ts`

*Anchor: `packages/boreal-web-components/src/components/forms/bds-color-picker/helpers/color-utils.ts` (`resolveBackground`).*

The only source change. v7 throws a `RangeError` from `contrast()` on an invalid color where v5 returned a value, and `presetColors` is consumer-supplied, so an invalid entry would have crashed the render. `resolveBackground` falls back to `#000000`, which reproduces the v5 result (contrast 21 and 1, swatch margin `0px`).

How the upgrade was checked: a differential run of both published versions over the surface the picker uses (26,667 hex strings, 22,695 HSV objects): identical hex, RGB, HSL and HSV output for every valid input. Differences: uppercase or padded `transparent` is now accepted (matches `isValidColorValue`), HSL hue 0 for saturation of about 0.01, contrast moves by up to 0.02 without crossing the 1.12 swatch threshold in 100,000 random colors. The 110 new tests (`color-utils.behavior.spec.ts` and `bds-color-picker.preset-colors.spec.ts`) were written and passing on 5.6.0 first; the six that changed were the intentional differences above. Please focus on `resolveBackground` and the updated expectations.

---

## 7. `@tanstack/virtual-core`: range widened, fix is in the test mock only

*Anchor: `packages/boreal-web-components/src/utils/testing/mocks/layout.ts` (the two new `client*` lines), with a note on the `package.json` range.*

From 3.19.6 the library measures the scroll container with `clientHeight` and `clientWidth` (3.19.5 read `offsetHeight` and `offsetWidth`). The mock only defined `offset*`, so under Stencil's mock DOM the viewport was `NaN` and the window collapsed to its overscan; that is what failed 24 `bds-search-bar` specs. The component and `virtual-window.ts` are unchanged. The range goes from `>=3.17.1 <3.19.6` to `>=3.17.1 <3.20.0`, so consumers now resolve 3.19.x. Checked on 3.19.11 in real browsers (Chromium and WebKit): windowing, scrolling, keyboard, resize and filtering of a 1,000-item search bar, and a 5,000-row virtualized table. Not covered: iOS devices.

---

## 8. New public export: `./components`

*Anchor: `packages/boreal-web-components/package.json`, `exports["./components"]`.*

Additive. `@stencil/react-output-target` 1.5 and later generate `import type { Components } from '@pxglobal/boreal-web-components/components'`, which needs a bare `./components` entry (the map only had `./components/*.js`). It points at `components-build/index.js` and `components-build/index.d.ts`, both already in the published `files`. This is what lifts the hold on the output target (now `^1.8.1`, in `boreal-react` and in the generator in web-components). Checked from the packed artifacts in the React and Vue pack apps: types resolve and a wrapper click handler fires like the raw element. Unverified: consumers that reference the wrapper's `StencilReactComponent` generics directly.

---

## 9. TypeScript 6 configuration

*Anchor: `packages/boreal-web-components/tsconfig.json`, with short notes on `packages/boreal-react/tsconfig.json`, `packages/boreal-vue/tsconfig.json` and `apps/boreal-docs/tsconfig.json`.*

TypeScript 6 deprecates `baseUrl` and changes defaults. web-components: `baseUrl` removed and `paths` becomes `"@/*": ["./src/*"]`, and `strict: false` is now explicit so the existing behavior is kept (Stencil builds with its own bundled TypeScript; this config also drives lint and editor checks). `boreal-react` and `boreal-vue` get `rootDir: ./lib`, which the new defaults need so `dist` keeps its layout. `boreal-docs` drops its unused `baseUrl`. `bds-tree-menu-item.tsx` has a small type guard `isTreeMenuItem` because Stencil's bundled compiler does not narrow after `element.matches(...)`.

---

## 10. Workspace overrides, pnpm 12 and the lockfile

*Anchor: `pnpm-workspace.yaml` (overrides), then `package.json` (`packageManager`, `engines`), then `pnpm-lock.yaml`.*

- **`overrides`:** four `:peer` entries. `eslint-plugin-react>eslint` exists because `@stencil/eslint-plugin` loads its optional peer `eslint-plugin-react` unconditionally and that package does not declare ESLint 10 (hence the new devDependency `eslint-plugin-react` 7.37.5 in web-components); the three `vite-*>vite` entries accept Vite 8 for the Vue devtools helper packages, which run fine on it (Vue app smoke test). They replace the previous `peerDependencyRules` entry and make `pnpm peers check` print "No peer dependency issues found". Remove each when the package declares the newer range.
- **`packageManager`:** pnpm 12.18.0 (the `latest-12` tag; 12.19 and 12.20 were on `next-12`), `engines.pnpm` is `>=12` and `engines.node` is `^22.22.2 || ^24.15.0 || >=26.0.0` (the highest floor among `lint-staged` 17, `chalk` 6, `execa` 10 and `npm-run-all2` 9). **Pre-adoption gate:** the Windows check is pending (`pnpm install`, `dev:pack:*`, `validate:pack:*`); the two pnpm commits are the last on the branch and can be reverted alone.
- **`pnpm-lock.yaml` (about 2,200 lines):** you do not need to read it. It holds the dependency bumps of this PR; the pnpm 12 rewrite changed only the environment section (pnpm 12.18.0), the `overrides` section, 17 `@inquirer/*` packages that disappeared (the only real change: `inquirer` for `@commitlint/cz-commitlint` resolves 9.3.8 instead of 12.11.1, inside its declared range) and peer-variant keys. To check: `pnpm install --frozen-lockfile` passes.

---

## 11. Release tooling: wrapper `dist` clean and certificate documentation

*Anchor: `packages/boreal-react/.release-it.json` (`hooks["before:init"]`), then `RELEASING.md`.*

- A Turborepo cache hit restores outputs over an existing `dist` without clearing it, so a stray file in a wrapper's `dist` survives `pnpm build` and ends up in `pnpm pack` (`dist` is git-ignored, so `git status` cannot show it). The hook now removes `dist` with a Node call (no `rm`, so it is portable) before the Turbo build, which then restores a clean one. Same change in `boreal-vue`. Tested by running the hook command with stray files present. Note that `release-it --dry-run` prints this hook and does not run it.
- `RELEASING.md` (TLS section) is rewritten from tested behavior: pnpm 12 ignores `NODE_EXTRA_CA_CERTS` and honors `cafile` in `~/.npmrc` for `view` and `publish`; pnpm 11 was the opposite for `publish`. **Pre-release gate:** the real company-network publish is untested; it needs the company root certificate and `strict-ssl` not disabled.

---

## 12. New Vue wrapper tests (about 430 lines)

*Anchor: `examples/vue-testapp/src/__tests__/component-models.spec.ts`.*

Not part of the published output. `component-models.spec.ts` compares the components that declare `valueChange` in `custom-elements.json` with the wrappers that expose `modelValue`, so a new component with a model fails with its name (the how-to is in the web-components README). `v-model.spec.ts` drives `BdsTextField`, `BdsCheckbox` and `BdsToggle` through the real wrappers in jsdom, and `class-merging.spec.ts` checks that consumer classes and the component's own host classes stay together on first render, through a sequence of class changes and when the readonly and error states toggle. `setup.ts` and `settle.ts` are the shared jsdom shim and a wait helper. The React half was deliberately dropped.

---

## 13. Tooling bumps that need no review beyond the build

*Anchor: `apps/boreal-docs/package.json` and `examples/react-testapp/vite.config.ts`.*

- **Docs:** Storybook 10.6.7 (lockfile only, ranges unchanged), Chromatic CLI 18 and addon 5 (a real `pnpm deploy:docs` was run from this branch and reported successful), Vitest 5, Vite 8, TypeScript 6, and `react` and `react-dom` declared as devDependencies: they were imported but undeclared, which left the Storybook vitest addon run failing with unresolved imports (it now passes 606 tests in about 11 seconds, but is not part of any gate yet because one date-picker story raises an intermittent unhandled rejection; drafted as a follow-up).
- **`react-testapp/vite.config.ts`:** `@vitejs/plugin-react` 6 removed its `babel` option, so the React Compiler now runs through `@rolldown/plugin-babel` and `reactCompilerPreset()`. Verified with an A/B build (the compiled component is present in the bundle only with the plugin).

---

## 14. Documentation additions

*Anchor: `packages/boreal-web-components/README.md` and `scripts-boreal/README.md`.*

Docs only. The web-components README gains "Adding `v-model` to a component (Vue)" (the `componentModels` list, `eventAttr: 'detail'` for read-only props, the invariant spec, and why a boolean component maps to `checked`). The `scripts-boreal` README gains "Dependency checks" (the audit, outdated and peers commands and the stage rules). `scripts-boreal/.gitignore` now ignores the `.vitest/` folder that Vitest 5's HTML reporter writes.
