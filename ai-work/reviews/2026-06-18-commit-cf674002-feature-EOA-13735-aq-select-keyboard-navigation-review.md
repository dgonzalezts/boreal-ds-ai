# Code Review — EOA-13735: AQ Select Keyboard Navigation

**Branch:** `feature/EOA-13735-aq-select-keyboard-navigation`  
**Head commit:** `cf674002`  
**Date:** 2026-06-18  
**Effort:** medium (3+5 angles × 6 candidates → 1-vote verify → 6 findings)

---

## Summary

This branch introduces a new `KeyboardController` utility and wires it into `bds-select` for keyboard navigation. The architecture is solid — clean separation of focus strategies (roving-tabindex / aria-activedescendant), a fluent API, and AbortController-based cleanup. Six findings surfaced during review, three of which are correctness bugs that will cause wrong focus position or TypeErrors at runtime.

---

## Findings

### 1. 🔴 rAF-scheduled `focusInitialTarget` fires after `focusFromTriggerKey`, clobbering the arrow-key target

**File:** `packages/boreal-web-components/src/components/forms/bds-select/bds-select.tsx`  
**Lines:** 274–285

```ts
private async handleArrowNavigation(key: string) {
  if (!this.popoverVisible) {
    await this.handleManagedActivate();   // schedules focusInitialTarget via rAF
  }
  await this.bdsList?.focusFromTriggerKey(key);  // ← runs BEFORE the rAF fires
}

private handleManagedActivate = async (allowOpenWithText = false) => {
  if (!this.popoverVisible) {
    if (!this.searchable || this.value === '' || allowOpenWithText) {
      await this.bdsPopover?.openPopover();
      requestAnimationFrame(() => {              // ← fires AFTER focusFromTriggerKey
        void this.bdsList?.focusInitialTarget();
      });
    }
    return;
  }
};
```

**Failure scenario:** User presses ArrowUp on a closed select. `handleManagedActivate` opens the popover and queues `focusInitialTarget` in a rAF. `handleArrowNavigation` then calls `focusFromTriggerKey('ArrowUp')`, which correctly focuses the last item. One frame later the rAF fires, calling `focusInitialTarget` with no guard against an already-moved focus — snapping focus back to the first/active item. The arrow key intention is silently ignored every time the popover opens from a closed state.

**Fix:** Remove the `requestAnimationFrame` + `focusInitialTarget` call from `handleManagedActivate`. `handleArrowNavigation` already calls `focusFromTriggerKey`, which handles initial focus. For the Enter/Space path that calls `handleManagedActivate` without an arrow key, call `focusInitialTarget` directly after the `await openPopover()` without the rAF (or call it once inside `focusFromTriggerKey` as a fallback).

---

### 2. 🔴 `active-item` accumulates across multiple code paths — no single owner clears it before writing

**Files:** `packages/boreal-web-components/src/components/forms/bds-select/bds-select.tsx` (line 205) and `bds-list-menu` internals (`focusInitialTarget`, `refreshNavigationState`)  
**Confirmed via playground reproduction**

`active-item` is written in at least three independent paths, and **none of them** sweeps the list to remove the attribute from other items before setting it:

1. **Type-ahead `onMatch`** (`bds-select.tsx:205`) — sets `[active-item]` on the matched item.
2. **Popover close / Escape** — `resetChildren` → `refreshNavigationState` → `focusInitialTarget` inside `bds-list-menu` sets `[active-item]` on the first/selected item.
3. **`focusInitialTarget`** called on open — same issue.

**Observed sequence (playground):**

```
1. Focus field, press B  → Bolivia gets [active-item]   (path 1)
2. Press Escape          → Argentina gets [active-item]  (path 2, reset to first item)
3. Press C               → Chile gets [active-item]      (path 1)
Result: Argentina + Bolivia + Chile all carry [active-item]
4. Press ↓ to reopen    → focus lands on Argentina      (first DOM match wins querySelector)
```

**Root cause:** `active-item` behaves as a "cursor" attribute but has no single write point that enforces mutual exclusivity. Every new writer assumes it is the first one.

**Fix:** Add a private method inside `bds-list-menu` that owns all writes to `active-item`:

```ts
private _setActiveItem(item: HTMLElement | null): void {
  this.querySelectorAll('[active-item]')
    .forEach(el => el.removeAttribute('active-item'));
  item?.setAttribute('active-item', '');
}
```

Route every existing callsite (`focusInitialTarget`, `refreshNavigationState`, and the type-ahead `onMatch` in `bds-select`) through this method. Patching individual callsites is insufficient — the next new path will reintroduce the bug.

---

### 3. 🔴 `prevIndex` closure goes stale after dynamic list changes, passing `undefined` instead of `null` to `onItemActive`

**File:** `packages/boreal-web-components/src/utils/a11y/keyboard/navigation/linear-navigation.ts`  
**Lines:** 52, 81–83

```ts
let prevIndex = -1;

const move = (delta: 1 | -1 | NavBoundary, eventTarget?: HTMLElement) => {
  const items = resolveItems();   // re-evaluated on every keypress

  if (onItemActive != null && strategyType === FOCUS_STRATEGY.ARIA_ACTIVE_DESCENDANT) {
    const prevItem = prevIndex >= 0 ? items[prevIndex] : null;  // ← no bounds check
    onItemActive(items[next], prevItem);  // prevItem can be undefined
  }
  ...
  prevIndex = next;
};
```

**Failure scenario:** User navigates to index 8 in a 10-item searchable select (`prevIndex=8`), then types a character that filters the list to 3 visible items. On the next arrow key, `resolveItems()` returns 3 items; `items[8]` is `undefined`. The guard `prevIndex >= 0` passes (8 ≥ 0) but `items[8]` yields `undefined`, not `null`. Any `onItemActive` callback that calls `prevItem.getAttribute(...)` or `prevItem.removeAttribute(...)` throws `TypeError: Cannot read properties of undefined`.

**Fix:** Add a bounds check: `const prevItem = prevIndex >= 0 && prevIndex < items.length ? items[prevIndex] : null`.

---

### 4. 🟡 `setFocusTrap` uses `currentIndex <= 0` which conflates "focus on first item" with "focus outside the trap"

**File:** `packages/boreal-web-components/src/utils/a11y/keyboard/KeyboardController.ts`  
**Line:** 718

```ts
const nextIndex = reverse
  ? currentIndex <= 0          // ← -1 (not found) triggers same path as 0 (first item)
    ? items.length - 1
    : currentIndex - 1
  : currentIndex >= items.length - 1
    ? 0
    : currentIndex + 1;
```

**Failure scenario:** A dialog root element has `tabindex="0"` and holds focus when first opened. It does not appear in `FOCUSABLE_SELECTOR` items (it matches `[tabindex]:not([tabindex="-1"])` but the dialog element itself may have `[hidden]` descendants etc.). `currentIndex === -1`. Held Shift+Tab evaluates `(-1 <= 0) → true` → `items.length - 1` (last item). Held Tab evaluates `(-1 >= items.length - 1) → false` → `nextIndex = 0` (first item). The asymmetry disorients screen reader users: Shift+Tab jumps to the last item rather than the first.

**Fix:** Separate the two cases: `currentIndex < 0 ? 0 : currentIndex === 0 ? items.length - 1 : currentIndex - 1`.

---

### 5. 🟡 `wrap && items.length > 1` suppresses horizontal wrap for single-row grids

**File:** `packages/boreal-web-components/src/utils/a11y/keyboard/navigation/grid-navigation.ts`  
**Line:** 151

```ts
if (wrap && items.length > 1) {   // items.length is row count, not cell count
  // wrap to next/prev row
}
// else: clamp to edge cell — single-row grids never wrap
```

**Failure scenario:** A horizontal toolbar or radio group is implemented as a single-row grid (`items = [[btn1, btn2, btn3]]`, `items.length === 1`) with `wrap: true`. Pressing ArrowRight at `btn3` evaluates `wrap && 1 > 1 → false`, falls to the edge-clamp path, and stays on `btn3`. The ARIA APG roving-tabindex pattern requires arrow keys to cycle within the widget. Callers that pass `wrap: true` expecting end-to-start wrap will find the flag silently ignored for any single-row layout.

**Fix:** Remove the `items.length > 1` guard. `findRowWithCells` with a single-row grid and `wrap: true` safely returns row 0, causing the next cell to be `nextRowPositions[0]` — which is the correct wrap-to-start behavior.

---

### 6. 🟢 `isHTMLElement` type guard duplicated across three files

**Files:**
- `packages/boreal-web-components/src/utils/a11y/keyboard/focus/aria-activedescendant.ts:3`
- `packages/boreal-web-components/src/utils/a11y/keyboard/focus/roving-tabindex.ts:3`
- `packages/boreal-web-components/src/utils/a11y/keyboard/navigation/grid-navigation.ts:27`

All three define the identical function:
```ts
function isHTMLElement(cell: HTMLElement | null | undefined): cell is HTMLElement {
  return cell != null;
}
```

**Cost:** A fix (e.g., adding `instanceof HTMLElement` for cross-frame safety) applied to one copy will silently miss the other two.

**Fix:** Extract to `packages/boreal-web-components/src/utils/a11y/keyboard/utils.ts` and import from there.

---

## Checklist

| # | Severity | Status | File |
|---|----------|--------|------|
| 1 | 🔴 High | ✅ Fixed | `bds-select.tsx:284` — rAF clobbers arrow-key focus |
| 2 | 🔴 High | ✅ Fixed | `bds-list-menu` + `bds-select.tsx:205` — `active-item` accumulates across type-ahead, Escape, and open paths |
| 3 | 🔴 High | Open | `linear-navigation.ts:82` — `prevIndex` out-of-bounds → `undefined` to `onItemActive` |
| 4 | 🟡 Medium | Open | `KeyboardController.ts:718` — `setFocusTrap` asymmetry when focus outside trap |
| 5 | 🟡 Medium | Open | `grid-navigation.ts:151` — single-row grids with `wrap:true` don't wrap |
| 6 | 🟢 Low | Open | Three-file `isHTMLElement` duplication |

---

## Fixes Applied

### Fix #1 — rAF race condition (`bds-select.tsx`)

**Date:** 2026-06-18  
**Verified:** ✅ Playground confirmed — ArrowUp now correctly focuses last item (Venezuela) on first open.

**Changes:**

`handleManagedActivate` gained a `focusOnOpen` parameter (default `true`). The `requestAnimationFrame` wrapper was removed — `openPopover()` is already awaited so the DOM is ready when it resolves, making the rAF unnecessary. `handleArrowNavigation` now passes `(false, false)` to skip the open-focus entirely, letting `focusFromTriggerKey` own focus with no race.

```ts
// bds-select.tsx

// Before
private handleManagedActivate = async (allowOpenWithText = false) => {
  if (!this.popoverVisible) {
    if (!this.searchable || this.value === '' || allowOpenWithText) {
      await this.bdsPopover?.openPopover();
      requestAnimationFrame(() => {
        void this.bdsList?.focusInitialTarget();
      });
    }
    return;
  }
};

private async handleArrowNavigation(key: string) {
  if (!this.popoverVisible) {
    await this.handleManagedActivate();
  }
  await this.bdsList?.focusFromTriggerKey(key);
}

// After
private handleManagedActivate = async (allowOpenWithText = false, focusOnOpen = true) => {
  if (!this.popoverVisible) {
    if (!this.searchable || this.value === '' || allowOpenWithText) {
      await this.bdsPopover?.openPopover();
      if (focusOnOpen) {
        void this.bdsList?.focusInitialTarget();
      }
    }
    return;
  }
};

private async handleArrowNavigation(key: string) {
  if (!this.popoverVisible) {
    await this.handleManagedActivate(false, false);
  }
  await this.bdsList?.focusFromTriggerKey(key);
}
```

---

### Fix #2 — `active-item` accumulation (`bds-list-menu.tsx` + `bds-select.tsx`)

**Date:** 2026-06-18  
**Verified:** ✅ Playground confirmed — full B → Escape → C → Escape sequence now leaves exactly one `[active-item]` at all times. Previous behavior accumulated 3 items (Argentina + Bolivia + Chile).

**Root cause expanded during reproduction:** Not just the type-ahead `onMatch` path — also `refreshNavigationState` (called on Escape/close) and `moveFocusByPage` were writing `active-item` without clearing first.

**Changes:**

Added `_clearActiveItems()` private helper to `bds-list-menu` and called it before every `setAttribute('active-item', '')` write in `focusInitialTarget`, `refreshNavigationState`, and `moveFocusByPage`. In `bds-select.tsx`, the type-ahead `onMatch` rAF callback now removes the attribute from all items in the same loop that resets `tabIndex`.

```ts
// bds-list-menu.tsx — new helper
private _clearActiveItems(): void {
  this.el.querySelectorAll('[active-item]').forEach(el => el.removeAttribute('active-item'));
}

// Called before every setAttribute('active-item', '') in:
//   focusInitialTarget  (line ~118)
//   refreshNavigationState  (line ~142)
//   moveFocusByPage  (line ~175)

// bds-select.tsx — type-ahead onMatch (before)
el.setAttribute('active-item', '');
allItems.forEach(item => { item.tabIndex = item === el ? 0 : -1; });

// After
allItems.forEach(item => {
  item.removeAttribute('active-item');
  item.tabIndex = item === el ? 0 : -1;
});
el.setAttribute('active-item', '');
```
