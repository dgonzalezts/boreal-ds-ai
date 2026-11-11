# PR Title

fix(deps): EOA-19635 resolve production audit findings and apply dependency updates

---

# PR Body

## Description

First code delivery of the dependency maintenance baseline (EOA-19635, sub-tasks 1 to 3): it fixes the production audit findings, refreshes the browser data and applies the pending patch and minor updates. Major version updates are out of scope; they are planned separately.

**Why `fix(deps)` and not `chore`:** the PR changes runtime dependencies of the published packages (`dompurify`, `@stencil/vue-output-target`, `@tanstack/virtual-core`). Consumers must receive the security fix, and a `chore` does not release.

---

## Security fixes

`pnpm audit --prod` went from **29 advisories (1 critical, 17 high, 7 moderate, 4 low) to 0** ("No known vulnerabilities found"). All advisories are public GitHub advisories; no coordinated disclosure is needed.

| Package | Advisories | Reached through | Fixed in |
| --- | --- | --- | --- |
| `dompurify` | 8 (1 critical `GHSA-cg2g-xh64-v4q7`, 1 high, 2 moderate, 4 low) | `boreal-web-components`, direct runtime dependency (HTML sanitizer) | 3.4.17: range raised to `^3.4.17` |
| `brace-expansion`, `minimatch`, `picomatch` | 12 (9 high, 3 moderate) | `boreal-react` → `@stencil/react-output-target` → `ts-morph` | lockfile re-resolved within the existing ranges |
| `nanoid`, `postcss`, `source-map-js`, `@vue/server-renderer` | 9 (7 high, 2 moderate) | `boreal-vue` and `vue-testapp` through `vue` | lockfile re-resolved (`vue` 3.5.44) |

Exposure: `dompurify` is reachable at runtime through the library's sanitizer. The rest are transitive dependencies on tooling and server-rendering paths; they are fixed regardless. Only the `dompurify` range changed in a manifest; no overrides and no major bumps were needed.

---

## What changed

- **Manifests (6 files):** `dompurify` `^3.4.17`; `@stencil/core` exact `4.45.1`; `@stencil/react-output-target` exact `1.4.2` (web-components and `boreal-react`); `@stencil/vue-output-target` `^0.14.7` (web-components and `boreal-vue`); `@tanstack/virtual-core` capped at `>=3.17.1 <3.19.6`; `typescript-eslint` `~8.58.2`; docs, `react-testapp` and `vue-testapp` dev-tool ranges (`oxlint`, `eslint-plugin-oxlint`, `eslint-plugin-vue`, `eslint-plugin-react-refresh`, `prettier` pin).
- **`pnpm-lock.yaml`:** re-resolved; 42 of the 48 packages with pending minor or patch updates now sit on the latest version (the other 6 are listed below).
- **`caniuse-lite`** 1.0.30001769 → 1.0.30001819. The Browserslist "9 months old" warning was printed by data bundled inside `@stencil/core`, so the Stencil update is what cleared it (21 warning lines → 0 in the build).
- **`boreal-web-components/testing.config.ts`:** the generated `bds-flag/helpers/generatedFlags.ts` (542 lazy-import functions) is excluded from coverage. It dropped Functions coverage to 77% on `release/current`; without it the figure is 92.7%.
- **`release/current` merged twice** (the EOA-19436 and EOA-19597 breaking commits, then the 0.15.0 and 0.16.0 releases and the `prebuild` removal).

---

## Updates held back (6)

Each hold was found by testing. The sub-task asked for every pending update, so these deviate from it on purpose; each has a tracked follow-up.

| Package | Now | Latest | Why it is held |
| --- | --- | --- | --- |
| `@stencil/core` | 4.45.1 (exact) | 4.45.2 | 4.45.2 parses the string attribute `"false"` as `true` on form-associated components; 3 `bds-file-picker` tests fail. The upstream intent needs confirming. |
| `@stencil/react-output-target` | 1.4.2 (exact) | 1.6.5 | From 1.5.0 the generated React wrapper imports types from `@pxglobal/boreal-web-components/components`, which the package `exports` map does not provide (`TS2307` in `boreal-react`). |
| `typescript-eslint` | ~8.58.2 | 8.72.1 | 8.59.0 adds 38 `no-unnecessary-type-assertion` errors in 17 component files. |
| `@tanstack/virtual-core` | below 3.19.6 | 3.19.8 | 3.19.6 and later fail 24 `bds-search-bar` items-mode tests (3.19.5 passes all 305). |
| `@vitest/eslint-plugin` | 1.6.27 (lockfile) | 1.6.28 | 1.6.28 raises its optional TypeScript peer to `>=6.0.0`; the repository is on 5.9.3. |
| `prettier` | 3.8.0 / 3.8.1 | 3.9.10 | 3.9 newly flags 16 files that need reformatting. |

---

## Impact

- **Not a breaking change** under CONTRIBUTING.md: no public API, token, tag, prop, event or entry point changed, and no component source was edited.
- **Behaviour-changing in edge cases (upstream fixes):** `dompurify` 3.4.17 sanitization fixes; the Vue runtime (`@stencil/vue-output-target` 0.14.7) rewrites host class merging and no longer intercepts modifier-key clicks on router links; the Stencil 4.45.1 compiler output.
- **Published dependency ranges changed:** `dompurify` minimum raised, `virtual-core` capped, `@stencil/vue-output-target` raised in `boreal-vue`.
- **Release effect:** a `fix` touching `boreal-web-components`, `boreal-react` and `boreal-vue` releases those three packages; `boreal-style-guidelines` is untouched.

---

## Testing

Automated, on this branch:

- `pnpm lint`: 0 errors, same warning counts as before the update.
- Unit tests: 375 suites, 4,810 tests pass; coverage 93.2% statements, 85.6% branches, 92.7% functions, 94.8% lines (threshold 80%).
- Builds pass for web-components, Storybook, the React and Vue wrappers and both test apps.
- `pnpm validate:all` passes (React and Vue pack pipelines) and leaves a clean tree; `pnpm peers check` and `pnpm install --frozen-lockfile` are clean.

Manual, in a real browser (Chromium, packed artifacts through `dev:pack:vue`), Vue wrapper:

- Host class merging held through repeated toggling of a consumer `:class` and the component's own `error` state, with no stale or duplicated classes.
- `v-model` worked in both directions on `bds-text-field` and `bds-checkbox`.
- Console: 0 errors.

---

## Notes for reviewers

- **The lockfile diff is about 5,400 changed lines, but only resolved-version moves are real.** The rest is pnpm 11 rewriting peer-dependency suffixes such as `(supports-color@8.1.1)` and the quote style. Review the 6 manifests (about 30 changed lines) and the version moves.
- **Please confirm two choices that reach the published manifests:** the `@tanstack/virtual-core` cap and the exact `@stencil/react-output-target` pin. There are no consumers yet; the follow-ups lift both once the causes are fixed.
- **Merge message:** keep the title as written; no `BREAKING CHANGE:` footer is needed. Squash and merge.
- The branch contains two merge commits from `release/current`.

---

## References

Closes EOA-20014
Closes EOA-20015
Refs EOA-20016
Refs EOA-19635

---

## Checklist

- [x] The audit findings are addressed and `pnpm audit --prod` reports no vulnerabilities
- [x] No new vulnerabilities introduced
- [x] All existing tests pass and coverage stays above 80%
- [x] No component source or public API changed
- [x] Lint, builds, `validate:all` and the peers check pass
- [x] Follows the conventional commit format (`fix(deps)`) and includes the ticket
- [x] Lockfile changes are consistent with the manifests (`--frozen-lockfile` passes)
- [x] Held-back updates are documented with reasons and tracked follow-ups
- [ ] Reviewer confirms the `virtual-core` cap and the `@stencil/react-output-target` pin for the published manifests
