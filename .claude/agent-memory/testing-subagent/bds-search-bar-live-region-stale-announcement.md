---
name: bds-search-bar-live-region-stale-announcement
description: "How the items-mode live region (`.bds-search-bar__status` / `resultsAnnouncement`) can go stale, and which trigger clears it; plus the pre-fix proof and current Stryker availability."
---

# `bds-search-bar` items-mode live region — stale-announcement mechanics

Measured 2026-10-28 on `fix/EOA-19598-search-bar-virtual-scroll-feature_DG` (stale live-region fix).

## State vs element

`resultsAnnouncement` is `@State()`; the `<span class="bds-search-bar__status" role="status" aria-live="polite">` is rendered only under `this.isItemsMode`. So `items = undefined` **unmounts the region without clearing the state** — re-assigning `items` re-mounts the span carrying the previous text, and `onItemsChange`'s query branch may then re-announce the still-applied `itemsQuery`. That is why the fix clears the state, not just the element.

Consequence for assertions: a `status` reference captured by `renderItemsPage` goes stale (detached) once items mode ends. Re-query `root.querySelector('.bds-search-bar__status')` after re-assigning `items`; assert the DOM removal *and* `(page.rootInstance as unknown as { resultsAnnouncement: string }).resultsAnnouncement === ''` while it is unmounted.

## Clears are per-trigger — enumerating them is the audit

- external `value` write (`onValueChange`, non-internal, non-typed-commit) → clears **before** the `!isItemsMode` guard and before `applyItemsQuery(next, false)`
- `items` change with `itemsQuery === ''` → `else this.resultsAnnouncement = ''` (complement of the announce branch)
- `items = undefined` (items mode ends) → clears before `closeSuggestionsWithoutList()`
- internal paths still announce: debounced commit, X / Escape clear (`applyItemsQuery('', true)`), an `items` update under an active query
- **not cleared** by a `mode` toggle — PD-07, open in `ai-work/testing/failure-modes/bds-search-bar.md`
- **not reset**: `itemsQuery` survives leaving items mode (PD-08), so a return can filter/announce under an `itemsQuery` the field no longer shows

## Proving a clear is needed (revert-and-restore, byte-exact)

`shasum -a 256` the fixed component into `$TMPDIR`, hand-revert only the added `resultsAnnouncement = ''` lines (plus the join of `if (isTypedCommit || this.isInternalValueWrite || !this.isItemsMode) return;`), run the spec, then `cp` the snapshot back and re-check the hash. A byte-exact restore is verifiable two ways: the hash matches **and** `git diff` is empty for a file whose whole diff is the fix (pre-fix state == HEAD). With the clears reverted the four announcement specs failed with `Expected: "" / Received: "11 results" | "1 result" | "30 results"`.

## Coverage / tooling

`pnpm --filter @pxglobal/boreal-web-components run test:coverage -- src/components/forms/bds-search-bar --collectCoverageFrom="src/components/forms/bds-search-bar/**/*.tsx" --coverageReporters=text --coverageReporters=text-summary` → 97.64% statements / 91.97% branches / 100% functions. Uncovered: `bds-search-bar.tsx:163-165` (mode watcher), `223-224`, `452`.

**Stryker is not installed anywhere in this workspace** (no `@stryker-mutator/*` in the root or package `node_modules`, no config, no `MUTATION_TESTING.md` at `packages/boreal-web-components/`). Running the mutation gate requires installing the runner (modifies `package.json`/lockfile) plus a per-component config — surface that to the orchestrator rather than silently skipping Phase 2, and never commit the artefacts. Candidate for `.agents/memory/`.
