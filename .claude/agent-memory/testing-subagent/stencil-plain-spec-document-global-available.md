---
name: stencil-plain-spec-document-global-available
description: document.createElement works in .spec.ts files that never call newSpecPage, for constructing Node fixtures in pure-logic unit tests
metadata:
  type: project
---

A `.spec.ts` file that only imports plain TS classes/functions (no `newSpecPage`, e.g. `bds-table.utils.spec.ts` testing `CellContentCache`, `compareValues`, etc.) still runs under Stencil's Jest testing environment, which provides a working `document` global. `document.createElement('span')` is usable directly as a `Node` fixture without any `newSpecPage`/mock-doc setup.

**Why:** confirmed while adding direct `CellContentCache` tests (EOA-16000 Task 1) — needed real `Node` values for `.set(key, row, node)`/`.get(key, row)` assertions in a file with no `newSpecPage` boilerplate. Cross-checked against sibling non-`newSpecPage` spec files already doing this: `src/utils/a11y/keyboard/__test__/KeyboardController.spec.ts`, `focus.spec.ts`, `navigation.spec.ts`, `src/utils/helpers/__test__/validateProps.spec.ts`.

**How to apply:** when writing direct unit tests for a plain utility/class that happens to operate on DOM `Node`/`Element` types, don't reach for `newSpecPage` just to get a `Node` — `document.createElement(...)` works standalone in this repo's Jest config (`packages/boreal-web-components/testing.config.ts`, no `testEnvironment` override, no explicit jsdom setup needed).
