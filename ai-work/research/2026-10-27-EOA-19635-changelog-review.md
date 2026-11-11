# EOA-19635 — Changelog review for product-critical packages (Task 3)

**Reviewed:** 2026-10-29, against the upstream changelogs and release notes. Versions are the ones this branch ends on.

TypeScript did not change in Task 3 (its major update is planned in Task 7). Node and pnpm did not change (planned in Task 4, Runtimes).

## `@stencil/core` 4.42.1 → 4.45.1 (pinned exactly)

- **Breaking changes:** none marked, in any release from 4.43.0 to 4.45.2.
- **Relevant fixes:** reflected boolean attributes (4.44.1), reflected any-typed props (4.44.2), lazy getter/setter and pre-hydrate attribute handling (4.45.0, 4.45.1), several JSX and type fixes.
- **Browser data:** 4.45.0 is the first version whose bundled autoprefixer data no longer triggers the Browserslist "9 months old" warning; it is what cleared it (21 lines → 0).
- **Held at 4.45.1, not 4.45.2:** 4.45.2 lists "form-associated boolean attribute `"false"` parses as true" ([stenciljs/core#6908](https://github.com/stenciljs/core/issues/6908)). With 4.45.2, three `bds-file-picker` tests fail because `multiple="false"` and `error="false"` are now parsed as `true` on that form-associated component. The entry's wording is ambiguous, so the intended behavior needs to be read from the upstream issue before the pin is lifted (Task 14).
- **Deprecation to plan for:** 4.43.3 "testing: deprecate all integrated testing options". This repository runs `stencil test --spec` and a `TestingConfig` in `testing.config.ts`, which the IDE already flags as deprecated (TS 6385). Nothing breaks today (Task 21).
- **Verification:** 375 suites and 4,810 tests pass, coverage 93.2% statements / 92.7% functions, web-components build passes.

## Storybook 10.2.8 → 10.6.5 (`storybook`, 4 addons, `@storybook/web-components-vite`, `eslint-plugin-storybook`)

- **Scope:** 42 releases, 630 changelog entries, none labeled breaking.
- **Entries that touch this repository's setup:**
  - 10.2.10: websocket connections now require a token (dev server only).
  - 10.3.0: Vite 8 support, and simplified Addon-Vitest configuration without setup files. The repo is on Vite 7; Vite 8 is a major update (Task 6).
  - 10.5.0: `ExternalDocs` deprecated.
  - 10.6.0: experimental Playwright component-testing integration removed; `vue-docgen-api` deprecated.
- **Verification:** Storybook build passes, docs lint 0 errors with the same 9 warnings as before.

## `release-it` 21.1.0 → 21.1.1

- Patch release: a `undici` update (7.29.1, fixes upstream issue #1335), other dependency updates, and a `verkit` import migration. No behavior change documented.
- **Verification:** `validate:all` passes (it does not run a release). A release dry run is the check that matters before the next release and is part of ADR 0019's gates for published dependencies.

## Output targets (they generate the published wrappers)

- **`@stencil/react-output-target` 1.4.1 → 1.4.2 (held):** every version from 1.5.0 emits a type import from `@pxglobal/boreal-web-components/components`, which the package's `exports` map does not provide, so the React wrapper does not compile with 1.5.0 or later. Details and fix in Task 18.
- **`@stencil/vue-output-target` 0.11.8 (generator) and 0.13.1 (runtime) → 0.14.7:** the generated Vue proxies are identical apart from two added blank lines. The runtime diff (147 lines) rewrites host class merging (`syncElementClasses`), changes SSR prop handling and router-link handling, and leaves the `v-model`/event path untouched. Wrapper automated tests are proposed in Task 20.

## Other packages that moved or were held

| Package | Result |
| --- | --- |
| `typescript-eslint` 8.55 → 8.58.2 (capped `~8.58.2`) | 8.59.0 adds 38 `no-unnecessary-type-assertion` errors in 17 component files (Task 13) |
| `@tanstack/virtual-core` 3.17.1 → 3.19.5 (capped below 3.19.6) | 3.19.6+ fails 24 `bds-search-bar` items-mode tests (Task 16) |
| `@vitest/eslint-plugin` 1.6.11 → 1.6.27 (held) | 1.6.28 raises its optional TypeScript peer to `>=6.0.0` (Task 15) |
| `prettier` 3.8.0 / 3.8.1 (held) | 3.9.10 newly flags 16 files (Task 19) |
