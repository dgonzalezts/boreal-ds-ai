# PR Title

feat(multiple)!: EOA-20193 update dependencies and fix wrapper typings and bds-toggle v-model

---

# PR Body

## ⚠️ BREAKING CHANGE Notice

**Type:**

- [x] Behavior change (same API, different behavior)
- [x] Build output change (package structure, exports)
- [ ] API change (prop/method/event renamed or removed)
- [ ] Component renamed or removed
- [ ] Minimum version requirement change (Node.js, browsers, dependencies)

**Impact Level:** **Medium**. It affects a subset of consumers and needs small code changes: Vue code that reads the `BdsToggle` `v-model` as a string, HTML that writes `"false"` as an attribute string on form-associated components, and TypeScript code that calls `focusFromTriggerKey` of `bds-list-menu` with a plain `string`.

**Merge order:** PR #208 (EOA-19635, production audit fixes and minor updates) is already merged. This PR is rebased on the resulting `release/current` and holds the 27 commits of EOA-20193 only. Use **Squash and merge** and keep the title above. Put the `BREAKING CHANGE:` footer from "Merge message" below in the last lines of the merge message, unindented.

---

## Description

Second delivery of the dependency maintenance work, continuing EOA-19635: it upgrades the major versions that the baseline left out (TypeScript 6, ESLint 10, Vitest 5, Vite 8, `@colordx/core` 7, Storybook's Chromatic stack, pnpm 12 and others), lifts all six holds recorded at the end of the baseline, and fixes three defects found while doing it (the `bds-toggle` `v-model` mapping in the Vue wrapper, the `@tanstack/virtual-core` test mock, and unresolved names in the published type declarations).

`pnpm outdated -r` went from **83 entries (30 major, 42 minor, 11 patch) to 31 (11 major, 9 minor, 11 patch)**. The production audit stays at 0 high or critical findings; one moderate `minimatch` finding is accepted with a recorded reason (below).

The test runner migration (Jest to `@stencil/vitest`) is **not** included: it was investigated and deferred. See "Not included".

---

## Justification for the breaking changes

- **`BdsToggle` `v-model` (Vue):** the wrapper mapped the model to the toggle's `value` property, so the bound value was a string and a bound `true` did not check the toggle. A checked toggle also submitted the model string (`"true"` or `"false"`) instead of its `value` (`"on"` by default). The model now binds `checked`, like `bds-checkbox`.
- **Stencil 4.45.2:** the first baseline pinned Stencil to 4.45.1 because 4.45.2 reads the attribute string `"false"` as `true` on form-associated components. The pin could not stay: Stencil 4.45.2 is the maintained line and Stencil 5 builds on it. The behavior is documented upstream (stenciljs/core pull request 6908).
- **Type declarations:** the published types failed a strict consumer check (14 errors with `skipLibCheck: false`) and silently typed some names as `any`. Fixing them makes `focusFromTriggerKey` a real type.

---

## Migration path

### Vue: `BdsToggle` with `v-model`

**Before:** the model was a string (the toggle's `value`) and `true` from code did not check the toggle.

```vue
<BdsToggle v-model="notifications" name="notifications" label="Notifications" />
<!-- notifications was "on" or "" after a click; setting it to true did nothing -->
```

**After:** the model is a boolean bound to `checked`.

```vue
<BdsToggle v-model="notifications" name="notifications" label="Notifications" />
<!-- notifications is true or false; setting it to true checks the toggle -->
```

Check what reads the model: code that compared it to `"on"` or `""` must compare it to `true` or `false`. `name` is now required by the generated wrapper type for `BdsToggle`. The `value` property keeps its meaning (the form value, `"on"` by default).

### All frameworks: `"false"` in an attribute on form-associated components

**Before:** `<bds-checkbox disabled="false">` was enabled.

**After:** the string `"false"` resolves to `true`, so the control is disabled and excluded from form data. Typed values and properties are unaffected.

```html
<!-- migrate: remove the attribute, or set the property -->
<bds-checkbox></bds-checkbox>
<script>
  document.querySelector("bds-checkbox").disabled = false;
</script>
```

In React and Vue bind a boolean (`disabled={false}`, `:disabled="false"`), not the string.

### TypeScript: `focusFromTriggerKey` of `bds-list-menu`

**Before:** the declaration referenced an unresolved name, so the parameter was effectively `any`.

**After:** the parameter is the exported type `ListMenuTriggerKey` (`'ArrowDown' | 'ArrowUp'`). Pass one of those literals; a `string` no longer compiles.

### Types that disappear

The generated duplicate alias `ValidationChangePayload1` is no longer exported from `components.d.ts`. Use `ValidationChangePayload`.

### Unverified

`@stencil/react-output-target` moves from 1.4.2 to 1.8.1, so the generated React wrapper declares more generic arguments for `StencilReactComponent`. The React pack app builds and a wrapper click handler fires exactly like the raw element, but consumers that reference those generics directly were not checked.

---

## Other consumer-visible changes (not breaking)

- **New export** `@pxglobal/boreal-web-components/components` (types and the custom elements index). Additive.
- **`@colordx/core` 5.6.0 to 7.3.0** (runtime dependency of `bds-color-picker`). A differential test of the surface the picker uses (26,667 hex strings, 22,695 HSV objects) found identical hex, RGB, HSL and HSV output for every valid input. Three small differences: uppercase or padded `transparent` is now accepted; for a color with saturation of about 0.01 the HSL hue is reported as 0 (the rule that already applied to pure greys); contrast values move by up to 0.02 in about 7.5% of colors, without crossing the swatch threshold in 100,000 random colors. The contrast helper now falls back to black for an invalid color, because v7 throws where v5 returned a value (a consumer-supplied `presetColors` entry would have crashed the render).
- **`@tanstack/virtual-core`** range widened from `>=3.17.1 <3.19.6` to `>=3.17.1 <3.20.0`. From 3.19.6 the library measures the scroll container with `clientHeight` and `clientWidth`; the 24 failing `bds-search-bar` specs were a gap in the test mock, not in the component. Verified in a real browser (Chromium and WebKit) on 3.19.11: windowing, scrolling, keyboard navigation, resize and filtering of the 1,000-item search bar, and a 5,000-row virtualized table. Consumers now resolve the newest 3.19.x.
- **Published type declarations:** a strict consumer check (`skipLibCheck: false`, TypeScript 6.0.3, packed tarball installed with its dependencies) went from 14 errors to 0, and no test helper declaration enters a consumer's program any more.

Tooling only (no consumer effect): TypeScript 6.0.3, ESLint 10 and its companions, `typescript-eslint` 8.72, Vitest 5.1.0 and jsdom 30, Vite 8.3.8 and `@vitejs/plugin-react` 6, Storybook 10.6.7 with the Chromatic CLI 18 and addon 5, `lint-staged` 17, `chalk` 6, `execa` 10, `npm-run-all2` 9, Prettier 3.9, pnpm 12.18.0, Turborepo `^2.11.10`.

---

## Tasks included

| Task                        | Commit                                                                 | Notes                                                                                                                                                                              |
| --------------------------- | ---------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Prettier 3.9                | `f9b1c273`, `f3b9400a`                                                 | The reformat is its own `style` commit                                                                                                                                             |
| ESLint 10                   | `3979e79a`                                                             | `eslint-plugin-react` peer handled with an override                                                                                                                                |
| Stencil 4.45.2              | `44c50357`                                                             | The 4.45.1 pin is removed; behavior change documented above                                                                                                                        |
| Dependency check docs       | `ed5badce`                                                             | `scripts-boreal` README                                                                                                                                                            |
| Vue wrapper tests           | `3b9d5ba0`                                                             | Compares `custom-elements.json` with the wrappers; the Vue test app has 14 tests today                                                                                             |
| `bds-toggle` `v-model`      | `1c0c4f0e`                                                             | Breaking, see above                                                                                                                                                                |
| Vue `v-model` contract docs | `bb6a708b`                                                             | Adds the how-to to the web-components README                                                                                                                                       |
| TypeScript 6.0.3            | `553f3be5`                                                             |                                                                                                                                                                                    |
| `typescript-eslint`         | `ca1dbe57`                                                             | Clears the type-assertion errors                                                                                                                                                   |
| Vitest 5 and jsdom 30       | `80cc113a`                                                             |                                                                                                                                                                                    |
| Vite 8 and plugin-react 6   | `30cfc14c`                                                             | React Compiler kept through `@rolldown/plugin-babel`                                                                                                                               |
| `./components` export       | `2a67a532`, `d375d88f`                                                 | Lifts the `@stencil/react-output-target` hold (now `^1.8.1`)                                                                                                                       |
| `virtual-core` range        | `0f403dd0`                                                             | Mock fix and range                                                                                                                                                                 |
| `@colordx/core` 7           | `a02d0704`                                                             | 110 new tests written before the upgrade                                                                                                                                           |
| Chromatic 18 and addon 5    | `5385a955`                                                             | Also refreshes Storybook within its range                                                                                                                                          |
| Utilities                   | `407b593d`, `6205af1a`                                                 | `lint-staged`, `chalk`, `execa`, `npm-run-all2`; Node floor raised                                                                                                                 |
| pnpm 12                     | `9db95b87`, `627d705a`                                                 | The lockfile rewrite is its own commit                                                                                                                                             |
| Housekeeping                | `49f9bf14`, `4d44cee6`, `57716cbb`, `2d53ab1a`, `4f5d25e2`, `4774509f` | Wrapper `dist` clean in the release hooks, `react` declared in the docs app, type declarations, Vue devtools peer overrides, verified Turborepo version, certificate documentation |

All six holds of the baseline are lifted (`@stencil/core`, `@stencil/react-output-target`, `typescript-eslint`, `@tanstack/virtual-core`, `@vitest/eslint-plugin`, `prettier`). The register for the next window is in the maintenance template.

---

## Not included (deferred, with reasons)

- **Test runner migration (Jest to `@stencil/vitest`).** Stencil's built-in runner is deprecated and removed in Stencil 5, and Jest 30 is not supported on Stencil 4, so `jest`, `jest-cli`, `@types/jest` and `puppeteer` stay on their current versions (19 of the 75 findings of a full `pnpm audit` go through them). Three routes were measured: keeping `newSpecPage` under Vitest 5 with a small local transform plugin (352 of 377 spec files green, 97.1% of tests, about 1 to 2 days of work); converting to `render()` with the plugin in source mode (coverage kept, about 6 to 9 days by a rough estimate); and converting on the documented dist route (works only with a dedicated test build, and reports 0% coverage on component source). It blocks the Stencil 5 upgrade (`5.0.0-rc.1` exists; no release date).
- **Dependency report script** and the **Jenkins job** (no owner, no DevOps agreement).
- **Follow-up tickets** (drafted by the author, not created in Jira): virtualized `bds-table` Tab focus loss, `bds-table` End/Home and wheel drift, an intermittent date-picker story rejection (`triggerSlot is required`) during the Storybook addon run, color picker details (HEX blur reset, 8-digit input, invalid presets), unit tests for the six style-guidelines generator files, a strict type check of the packed package in the pack pipeline, the test runner migration, and the Stencil 5 upgrade.

---

## Accepted finding

`pnpm audit --prod` reports one moderate `minimatch` advisory (GHSA-g3hv-75wg-m249, vulnerable below 11.0.1) through `boreal-react` > `@stencil/react-output-target` > `ts-morph` > `@ts-morph/common`. The newest published packages of that chain depend on `minimatch ^10`, so no clean fix exists; the published wrapper imports only the `/runtime` entry, which loads no `ts-morph`. `pnpm audit --prod --audit-level high` exits 0.

---

## Testing conducted

**Automated (final state, after rebasing on `release/current`):**

- `pnpm build` 7/7 (including the Storybook build and both test apps); `pnpm lint` 0 errors; `pnpm test` passes (web-components 378 suites and 4,967 tests; style-guidelines 33; `scripts-boreal` 45; Vue test app 14); web-components coverage 93.39 / 85.77 / 92.81 / 94.88 (statements, branches, functions, lines).
- `pnpm validate:all` (React and Vue pack pipelines) passes; `pnpm peers check` clean; frozen install passes; `pnpm audit --prod --audit-level high` exits 0.
- Release dry runs of the four packages exit 0 (a dry run prints the `before:init` hook but does not run it).
- Strict consumer type check of the packed web-components package: 0 errors.

**Manual (Chromium, and WebKit where noted):**

- Dev servers of the React, Vue and Storybook apps on Vite 8; the React Compiler is applied (A/B build).
- Search bar (1,000 items) and a 5,000-row virtualized table on `virtual-core` 3.19.11, Chromium and WebKit.
- Color picker: typed colors, drags, alpha and invalid presets against reference values computed with the old library.
- Pack-based React and Vue apps: wrapper click handlers match the raw element; Vue `v-model` on `BdsToggle`.
- The wrapper `dist` clean in the release hooks, tested with stray files.
- Certificate handling of `pnpm` 11.28.2 and 12.18.0 against a local registry with a private authority.

---

## Gates that cannot run here (recorded for the reviewers)

- [ ] **Windows (before contributors adopt pnpm 12):** someone runs `pnpm install`, `dev:pack:*` and `validate:pack:*` on Windows. Releases are not affected (`RELEASING.md`: release commands run on macOS or Linux). The two pnpm 12 commits are the last ones and can be reverted alone.
- [ ] **Company-network certificate (before the first release with pnpm 12):** pnpm 12 ignores `NODE_EXTRA_CA_CERTS` and reads `cafile` from `~/.npmrc`. On the company network, with the real root certificate and `strict-ssl` not disabled, the check in `RELEASING.md` must pass and a real publish of React and Vue must succeed.
- [x] **Chromatic upload:** the token holder ran one `pnpm deploy:docs` from this branch and reported that it ran successfully (the exit code, build URL and number of detected changes were not recorded).

---

## Contributor impact

pnpm 12.18.0 is pinned through Corepack and `engines.pnpm` is `>=12`; the root `engines.node` is `^22.22.2 || ^24.15.0 || >=26.0.0`. After pulling, run `pnpm install`. If the first `pnpm build` fails with `Property ... does not exist`, delete the generated `packages/boreal-web-components/src/components.d.ts` and rebuild (it also happened after the rebase of this branch).

---

## Merge message

Keep the title as is. Add this as the last lines of the merge message, unindented:

```
BREAKING CHANGE: In @pxglobal/boreal-vue, BdsToggle v-model now binds the checked state as a boolean (it bound the value string, so a bound true did not check the toggle and a checked toggle submitted the model string instead of its value). On form-associated web components the string "false" in an HTML attribute now resolves to true (Stencil 4.45.2), so disabled="false" disables the control. The focusFromTriggerKey method of bds-list-menu is typed 'ArrowDown' | 'ArrowUp' (it was effectively any), and the duplicate type export ValidationChangePayload1 is removed.
```

Release effect: each package that changes takes one minor bump (below 1.0); `release/current` already holds another breaking commit (`feat(web-components)!: EOA-19856 tech debt V5`), so the bump level does not change.

---

## References

Refs EOA-20193 (continues EOA-19635, merged as PR #208)
The per-task evidence is kept in the author's local plan; the numbers reviewers need are in this description.

---

## Checklist

### General

- [x] Follows conventional commit format with `!`: `type(scope)!: TICKET description`
- [x] BREAKING CHANGE footer prepared for the merge message
- [x] Ticket reference included
- [x] All tests pass
- [x] Self-reviewed for correctness

### Breaking Change Management

- [x] Breaking changes documented with before and after
- [x] Justification provided
- [x] Impact level assessed (medium)
- [x] Affected APIs documented
- [x] Migration path provided with examples

### Communication

- [ ] Reviewers notified of the three manual gates above
- [ ] Release notes mention the three breaking changes (the merge-message footer carries them)
- [ ] Consuming Vue teams told about the `BdsToggle` `v-model` change before the release

### Boreal DS Standards

- [x] Design tokens untouched
- [x] TypeScript types updated (`ListMenuTriggerKey`, relative re-exports, narrower imports)
- [x] Storybook builds with the upgraded addons
- [x] Documentation updated (`README.md`, `RELEASING.md`, web-components README)
