# Code Review — `bds-pagination.tsx`

**Branch:** `feature/EOA-10580_pagination`
**File:** `packages/boreal-web-components/src/components/data-visualization/bds-pagination/bds-pagination.tsx`
**Date:** 2026-06-18
**Effort:** medium (8 angles × verify)

---

## Summary

3 confirmed bugs, 3 cleanup items. The most severe issue corrupts both `internalCurrentPage` and `internalItemsPerPage` silently on every `totalItems` prop change due to incorrect `@Watch` stacking. A second bug causes an uncaught `TypeError` when using the ellipsis navigator. Both need to be fixed before shipping.

---

## Findings (ranked by severity)

### 1. `@Watch('totalItems')` stacked on the wrong methods — state corruption on `totalItems` change

**File:** `bds-pagination.tsx` · **Lines:** 136, 141
**Severity:** Critical

```ts
@Watch('totalItems')
@Watch('currentPage')
onCurrentPageChange(newValue: number) {
  this.internalCurrentPage = this.normalizePage(newValue);  // newValue is totalItems, not currentPage!
}

@Watch('totalItems')
@Watch('itemsPerPage')
onItemsPerPageChange(newValue: number) {
  this.internalItemsPerPage = this.normalizeItemsPerPage(newValue);  // newValue is totalItems, not itemsPerPage!
}
```

**Problem:** In Stencil, stacking `@Watch` decorators means the method fires for _each_ watched prop. When `totalItems` changes, Stencil calls `onCurrentPageChange(newTotalItems)` — passing the new `totalItems` value (e.g., 300) as `newValue`. This is then fed to `normalizePage(300)`, which clamps it to `totalPages` (e.g., 30), silently jumping the user to the last page. Simultaneously, `onItemsPerPageChange(300)` fires and `normalizeItemsPerPage(300)` finds 300 not in `perPageOptions`, silently falling back to `options[0]` (10), resetting the user's page size.

**Consequence:** Every `totalItems` prop update (e.g., after a data fetch) corrupts both the current page and items-per-page, with no error thrown and no warning logged for the `currentPage` corruption.

**Fix:** Remove the `@Watch('totalItems')` decorators from `onCurrentPageChange` and `onItemsPerPageChange`. Add a single dedicated `@Watch('totalItems')` that re-normalizes `internalCurrentPage` using `this.currentPage` (not `newValue`):

```ts
@Watch('totalItems')
onTotalItemsChange(newValue: number) {
  this.internalTotalItems = this.normalizeTotalItems(newValue);
  this.internalCurrentPage = this.normalizePage(this.currentPage);     // re-clamp against new total
  this.internalItemsPerPage = this.normalizeItemsPerPage(this.itemsPerPage);
}

@Watch('currentPage')
onCurrentPageChange(newValue: number) {
  this.internalCurrentPage = this.normalizePage(newValue);
}

@Watch('itemsPerPage')
onItemsPerPageChange(newValue: number) {
  this.internalItemsPerPage = this.normalizeItemsPerPage(newValue);
}
```

---

### 2. `handleFocusNav` dereferences `querySelector` result without a null check

**File:** `bds-pagination.tsx` · **Lines:** 261–263
**Severity:** High

```ts
private handleFocusNav() {
  if (this.pageToFocus === undefined || this.pageToFocus === null) return;

  const el = this.el.querySelector(`#bds-pagination-page-${this.pageToFocus}`);
  const button = (el as HTMLElement).querySelector('button') as HTMLElement;  // throws if el is null
  button.focus();                                                              // throws if button is null
  this.pageToFocus = null;
}
```

**Problem:** `pageToFocus` is set in `handlePage` (line 288) to the _un-normalized_ page number:

```ts
private handlePage(pageNumber: number, autofocus: boolean = false) {
  if (pageNumber === this.internalCurrentPage) return;
  this.emitPageChange(pageNumber);   // normalizes internally; pageNumber itself is unchanged
  if (autofocus) {
    this.pageToFocus = pageNumber;   // ← stores the original, un-normalized value
    requestAnimationFrame(() => this.handleFocusNav());
  }
}
```

`emitPageChange` normalizes the page and updates `internalCurrentPage`, but `pageToFocus` is still the original argument. For example, `handleEllipsisClick` calls `handlePage(this.internalCurrentPage - this.effectiveChunk, true)`. If the user is on page 1 with `chunk=3`, this becomes `handlePage(-2, true)`. The emit normalizes -2 → 1, but `pageToFocus` is -2. The RAF fires, `querySelector('#bds-pagination-page--2')` returns `null`, and line 262 throws `TypeError: Cannot read properties of null (reading 'querySelector')`.

This also drops keyboard focus entirely, which is a WCAG regression.

**Fix:**

```ts
private handleFocusNav() {
  if (this.pageToFocus === undefined || this.pageToFocus === null) return;

  const el = this.el.querySelector(`#bds-pagination-page-${this.pageToFocus}`);
  const button = el?.querySelector('button') as HTMLElement | null;
  button?.focus();
  this.pageToFocus = null;
}
```

And set `pageToFocus` to the _normalized_ page:

```ts
if (autofocus) {
  const normalizedPage = this.normalizePage(pageNumber);
  this.pageToFocus = normalizedPage;
  requestAnimationFrame(() => this.handleFocusNav());
}
```

---

### 3. `normalizePage(0)` silently falls back without logging a warning

**File:** `bds-pagination.tsx` · **Line:** 233
**Severity:** Medium

```ts
private normalizePage(page: number) {
  if (!Number.isFinite(page)) {
    this.logger.warn('bds-pagination', `Invalid currentPage value "${page}". Falling back to page 1.`);
    return 1;
  }
  // ...
  const returnedPage = Math.min(Math.max(page || 1, 1), this.totalPages);
  //                                     ^^^^^^^^ 0 || 1 = 1, silently
  return returnedPage;
}
```

`Number.isFinite(0)` is `true`, so `normalizePage(0)` bypasses the warn branch entirely. The `page || 1` expression then silently coerces `0` to `1`. By contrast, `NaN`, `Infinity`, or `undefined` all trigger the explicit warning. Passing `currentPage=0` as a prop produces a silent fallback — inconsistent with the documented behavior ("Invalid values will fallback to `3`").

**Fix:** Add an explicit guard for `page < 1` (or `page <= 0`) before the `Math.min/max` call:

```ts
if (!Number.isFinite(page) || page < 1) {
  this.logger.warn(
    "bds-pagination",
    `Invalid currentPage value "${page}". Falling back to page 1.`,
  );
  return 1;
}
```

---

### 4. `safeItemsPerPageOptions` — dead `Array.isArray` guard

**File:** `bds-pagination.tsx` · **Lines:** 174–181
**Severity:** Low (cleanup)

```ts
private get safeItemsPerPageOptions() {
  const options = [...this.perPageOptions];       // spread always produces an array
  if (!Array.isArray(options) || options.length === 0) {
    return [10];                                  // this branch can never execute
  }
  return options.filter(n => Number.isFinite(n) && n > 0);
}
```

The spread `[...this.perPageOptions]` always returns an `Array`, so `!Array.isArray(options)` is always `false`. The defensive branch is dead code. If `this.perPageOptions` were ever passed as a non-array by a JS consumer, the spread would throw _before_ reaching the guard, making the check useless at the one moment it matters.

**Fix:** Guard `this.perPageOptions` directly before spreading:

```ts
private get safeItemsPerPageOptions() {
  if (!Array.isArray(this.perPageOptions) || this.perPageOptions.length === 0) return [10];
  return this.perPageOptions.filter(n => Number.isFinite(n) && n > 0);
}
```

---

### 5. `componentDidLoad()` is an empty no-op lifecycle hook

**File:** `bds-pagination.tsx` · **Line:** 127
**Severity:** Low (cleanup)

```ts
componentDidLoad() {}
```

Empty lifecycle hooks add noise and mislead readers into searching for side-effects that don't exist. The project memory rule (`feedback_todo_comments_on_stubs.md`) permits stubs only with an explicit `// TODO` comment explaining what's pending; no such comment is present here.

**Fix:** Delete the method entirely.

---

### 6. `hasOverflow()` has a self-defeating measurement and a potential oscillation loop

**File:** `bds-pagination.tsx` · **Lines:** 314–321, 324, 332
**Severity:** Medium (logic flaw with visible rendering artifact)

#### The circular dependency

`hasOverflow()` measures `itemsInfoEl` to decide whether to show it — but `itemsInfoEl` only exists in the DOM when it is being shown:

```ts
// hasOverflow reads itemsInfoEl (line 318)
private hasOverflow() {
  if (this.itemsInfoEl === undefined || this.itemsInfoEl === null) return false;  // ← null guard
  const contentWidth = this.itemsInfoEl.getBoundingClientRect().width;
  const parentWidth  = this.pageControlsEl.getBoundingClientRect().width;
  return parentWidth + contentWidth > this.containerWidth;
}

// itemsInfoEl is only assigned when showItemsPerPage is true (line 324, 332)
private getItemsPerPage() {
  const showItemsPerPage = ... && !this.hasOverflow();
  return (
    showItemsPerPage && (
      <div ref={el => (this.itemsInfoEl = el as HTMLElement)}>  {/* ref only fires when rendered */}
        ...
      </div>
    )
  );
}
```

When `showItemsPerPage` transitions from `true` to `false`, Stencil calls the `ref` callback with `null`, setting `this.itemsInfoEl = null`. On the very next render, `hasOverflow()` hits the null guard and immediately returns `false` — which means `showItemsPerPage` becomes `true` again, the element re-renders, `itemsInfoEl` is re-assigned, and the real `getBoundingClientRect` measurement fires. If the container is still at the overflow threshold, `hasOverflow` returns `true` again, hiding the element, nulling the ref, and the cycle repeats.

**Concrete trigger:** Container width sits exactly at the boundary where the items-info block causes overflow. The component will visibly flicker — showing and hiding the items-per-page selector on every resize or state update until the container width moves decisively past the threshold.

#### The synchronous layout flush

`getBoundingClientRect()` forces the browser to complete any pending style/layout work before returning. Called twice per render (lines 318–319) from inside `render()`, this adds a forced synchronous reflow to every state update (page change, prop change, `containerWidth` tick from `ResizeObserver`).

#### The fix

Compute and cache overflow as a `@State` boolean, updated only where layout is already being measured — the `ResizeObserver` callback:

```ts
@State() private isOverflow: boolean = false;

private setupResizeObserver() {
  this.resizeObserver = new ResizeObserver(entries => {
    const entry = entries[0];
    if (!entry) return;
    const width = entry.contentRect.width;
    if (width > 0 && width !== this.containerWidth) {
      this.containerWidth = width;
      this.isOverflow = this.computeOverflow();  // measure once, here
    }
  });
  this.resizeObserver.observe(this.el);
}

private computeOverflow(): boolean {
  if (!this.itemsInfoEl || !this.pageControlsEl) return false;
  return (
    this.itemsInfoEl.getBoundingClientRect().width +
    this.pageControlsEl.getBoundingClientRect().width >
    this.containerWidth
  );
}
```

Then in `getItemsPerPage()`:

```ts
const showItemsPerPage =
  this.size !== PAGINATION_SIZES.SMALL && !this.compact && !this.isOverflow;
```

This eliminates the circular dependency (overflow is computed at resize time, not at render time when `itemsInfoEl` may be null), removes the per-render layout flushes, and prevents the oscillation loop.

---

## Verified Non-Issues

- **`handleEllipsisClick` direction logic** — `getVisiblePages` mathematically guarantees `internalCurrentPage` is always present in the returned array, so `findIndex` never returns -1. Verified by tracing the window-clamping algorithm in `utils/index.ts`.
- **`@Watch` execution order** — Stencil fires watchers in declaration order via a synchronous `.map()`. `onTotalItemsChange` is always first, so the stale-`totalPages` race does not occur. (The _value_ corruption in finding #1 is still real.)
