# bds-search-bar `items` append keeps scroll (EOA-19597 follow-up) — verified harness facts

Fix under test: `onItemsChange(next, previous)` in `bds-search-bar.tsx` only calls `resetItemsScroll()`
when `previous?.[0]?.value !== next?.[0]?.value`. Verified 2026-10-28 on Chrome (playwright-cli default)
and Playwright WebKit against the `#t9-s1` playground scenario (1,000 entries, row height 28 px,
`scrollHeight` 28,008, 14–20 mounted, scrollTop 14,000 → mounted `Item 496`–`Item 514`).

## Isolated dev-server harness (works alongside another session's watcher)

- `stencil build --dev` writes **friendly-named** chunks (`www/build/bds-search-bar.entry.js`) *and* a
  ES5 aggregate (`www/build/p-<hash>.system.entry.js`). A modern browser loads only
  `bds-<component>.entry.js`, so grepping the `.system.entry.js` bundle for a fix marker is a
  **false-negative generator** — two files contain the same component code, only one is served.
  Confirm the fix in the file the page actually loads
  (`performance.getEntriesByType('resource')` → `.../build/bds-search-bar.entry.js`) or `curl` that exact path.
- One-shot build + `cp -R www <tmpdir>` + `python3 -m http.server <own port>` gives a frozen snapshot,
  so neither a second session's `--watch` rebuild nor its source edits can change what you measured.
  (A source file it edited mid-run — `__test__/bds-search-bar.items.spec.ts` — had zero effect on results.)
- `python3 -m http.server` 404s `/favicon.ico`, which surfaces as the *only* console error. The project's
  stencil dev server returns 200 for it, so do not report that 404 as a page error.

## Playground driving gotchas (`src/index.html` T9 scenarios)

- `#t9-s1 input` is ambiguous (hidden `bds-select` input + field input) — always target
  `#t9-s1 bds-text-field input`, or both clicks and `eval` silently hit the wrong element.
- ArrowDown **from the field** while the list is scrolled mid-list focuses `Item 1` and scrolls to 0
  (entering the list starts at the first entry). Keyboard-continuity checks must start with focus on a
  list row (`items[items.length-1].focus({ preventScroll: true })`), never on the input.
- `items = undefined` closes the popover (focus stays in the field when it was in the field) and
  **does not auto-reopen** on reassignment — "reopens at the top" means after a user click.
- Same-head truncation (`items.slice(0, 500)`) keeps the offset, clamped to the new max scroll
  (14,000 → 13,768) — inherent to the first-entry comparison, not a regression.

## Measured deltas (usable as expectations)

| Action (1,000 items, scrollTop 14,000) | scrollTop | mounted    | setsize | scrollHeight |
| -------------------------------------- | --------- | ---------- | ------- | ------------ |
| baseline                               | 14,000    | 496–514    | 1000    | 28,008       |
| append 1                               | 14,000    | 496–514    | 1001    | 28,036       |
| append 20                              | 14,000    | 496–514    | 1021    | 28,596       |
| prepend 1                              | 0         | 1–14 (new) | 1022    | 28,624       |
| replace (new head)                     | 0         | 1–14 (new) | 300     | 8,408        |

Filtered append with query `99` (19 results): `scrollTop` 260 held, `aria-setsize` 19 → 20 on adding
`item-1990`, live region `19 results` → `20 results`; a non-matching append leaves 260 / 20 / `20 results`.
