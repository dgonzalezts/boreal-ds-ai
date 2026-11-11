# bds-search-bar Task 13 — slotted lists fully mounted (VirtualScrollController removed)

Verified 2026-10-26 on `fix/EOA-19598-search-bar-virtual-scroll-feature_DG` (stencil dev server on port 3388, Chrome).

Facts worth reusing:

- **Slotted filtering is label-OR-value, not value-only.** `bds-search-bar.searchOwnData()` matches
  `item.textContent` OR `item.getAttribute('value')` (same OR rule as `bds-select.searcherElement()`), so a
  query like `Slot 1` matches `Slot 1, Slot 10…Slot 19` (11 items), not 0. `index.html`'s T10-D doc block and
  older checklist wording both claim "value only" — that claim is wrong, but the code path is untouched by the
  Task 13 diff, so it is not a regression. Design fixtures where value and label share digits (d-N / Slot N) so
  value-vs-label matching cannot be distinguished; use `t10-f` (`f-N` / `Base N`) or query a bare label word.
- **The slotted `bds-list-menu` loses its authored `id`.** `bds-select` rewrites it to `bds-select-list-bds-<rand>`,
  so `#t10-d-menu` no longer resolves. Scope by the bar instead: `#t10-d bds-select bds-list-menu`.
- **Scroll container is `.bds-list-menu__content`** (`max-height: var(--bds-list-menu-max-height, 240px)`,
  `overflow-y: auto`). The `bds-list-menu` host itself reports `scrollHeight == clientHeight` (240) even with 30
  items mounted — measuring the host falsely looks like a clipping bug. Measure the `__content` child:
  30 items → `clientHeight 240`, `scrollHeight 848`.
- **`window.__logs` in `src/index.html` is a console interceptor**, not just an event log — reassigning it to `[]`
  refills with `warn:`/`log:` lines, so event assertions must be filtered (`.filter(l => l.includes('bdsSearch'))`).
- **`t10-f` has no event listeners wired** (`['a','b','d','e']` only), so `bdsSearch` is invisible there; attach a
  temp listener before asserting. `t12-s` *is* wired.
- **A `bdsClear` listener on the bar host fires twice per X click** — once bubbled from `bds-text-field`, once from
  the bar's own `@Event()`. Not a double-emit bug; filter with `e.target === bar` (target=SELF) before counting.
