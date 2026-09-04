# Boreal DS — Code Review Report

**Component:** `bds-tree-menu` (EOA-17159)
**Generated:** 2026-09-04
**Base ref:** `release/current`
**Branch:** `feature/EOA-17159_bsd-tree-menu_doc`
**Scope:** 2 components — `bds-tree-menu.tsx` (root coordinator) + `bds-tree-menu-item.tsx` (leaf)

---

## Affected Components

| Component | Role |
|-----------|------|
| `bds-tree-menu` | Root coordinator — manages item registry, keyboard navigation, event aggregation |
| `bds-tree-menu-item` | Leaf item — handles selection, checkbox state, expand/collapse, rendering |

---

## Findings

### 1. HIGH — `bdsChange` silently drops `checked` state for checkable items

**Location:** `bds-tree-menu.tsx:91-95`

```tsx
handleItemCheck(e: CustomEvent<{ item: HTMLBdsTreeMenuItemElement; checked: boolean }>) {
  if (this.disabled || e.detail.item.disabled) return;
  this.bdsChange.emit({ item: e.detail.item });   // checked is discarded
}
```

**Problem:** The leaf event `bdsTreeMenuItemCheck` (at `bds-tree-menu-item.tsx:68-71`) carries `{ item, checked }`, but the root's re-emit via `bdsChange` drops the `checked` boolean entirely.

**Impact:** A consumer listening to `bdsChange` on `bds-tree-menu` cannot tell whether a checkbox item became checked or unchecked. The `checked` state lives only in a private `@State() boxChecked` (`bds-tree-menu-item.tsx:46`) — not a `@Prop`, not exposed via `@Method`, and not reflected to any attribute. Confirmed against `ITreeMenuItem.ts`: the public interface is only `label/expanded/disabled/selected/checkable/icon` — no `checked`.

**Consumer workaround:** None via supported public API. The only path is unsupported DOM digging: `item.querySelector('bds-checkbox').hasAttribute('checked')`.

**Validation:**
- **Frontend subagent:** CONFIRMED — real bug, payload thrown away, no supported read-back path.
- **Testing subagent:** CONFIRMED — zero tests exercise a checkable item through the root; `bds-tree-menu.events.spec.tsx` never mentions "checkable"/"checked".
- **Documentation subagent:** CONFIRMED — JSDoc ("Emitted when a tree menu item becomes selected") and Storybook argTypes both fail to mention checkbox toggles. No story wires a listener to a checkable tree.

**Recommended fix:** Forward `checked` in `bdsChange`'s detail for the check path, or expose a public way to read it. Correct the JSDoc + Storybook argTypes wording to mention checkbox toggles.

---

### 2. MEDIUM — Selecting any non-checkable item clears `aria-selected` on every checkable item in the tree

**Location:** `bds-tree-menu.tsx:84-86`

```tsx
handleItemSelect(e: CustomEvent<...>) {
  ...
  this.items.forEach(item => { item.selected = false; });  // no checkable filter
  e.detail.item.selected = true;
  ...
}
```

**Problem:** The deselect-all sweep unconditionally clears `selected` on every registered item, including checkable ones. Since `selected` is `@Prop({reflect:true})` (`bds-tree-menu-item.tsx:37`), this directly rewrites the DOM attribute on every checkable item.

**Impact:** At render time, `aria-selected` (`bds-tree-menu-item.tsx:416`) is always `${this.selected}` regardless of `checkable`, while the visible CSS "selected" class correctly branches on `checkable ? boxChecked : selected`. Net effect: selecting any non-checkable item anywhere in the tree silently flips `aria-selected="false"` (and the `selected` attribute) on every checked checkable item, while its checkbox stays visually checked (`boxChecked` untouched). Screen reader state and visual state diverge.

**Validation:**
- **Frontend subagent:** CONFIRMED — direct attribute rewrite, not just an aria mismatch.
- **Testing subagent:** CONFIRMED — no mixed-tree spec exists; a regression test is trivial and would fail today.
- **Documentation subagent:** CONFIRMED — no story mixes checkable + non-checkable items; MDX accessibility section silent on this cross-item side effect.

**Recommended fix:** Either exclude checkable items from the deselect-all sweep in `handleItemSelect`, or explicitly document that `selected`/`aria-selected` and `checked` are two independent state channels for checkable items.

---

### 3. LOW — `handleDisabledChange` skips the ownership filter used elsewhere

**Location:** `bds-tree-menu.tsx:41-47`

```tsx
handleDisabledChange() {
  ...
  this.el.querySelectorAll('bds-tree-menu-item').forEach(item => { ... });
}
```

**Problem:** Uses a plain `querySelectorAll('bds-tree-menu-item')` with no check that each item's `closest('bds-tree-menu')` is `this.el`, unlike `_setupKeyboard` (`bds-tree-menu.tsx:113`), which explicitly filters `itemEl.closest('bds-tree-menu') !== this.el`.

**Impact:** If a `bds-tree-menu` ever ends up nested inside another one's slotted content, toggling `disabled` on the outer tree would incorrectly cascade into the inner tree's items.

**Validation:**
- **Frontend subagent:** CONFIRMED as a real inconsistency.
- **Testing subagent:** REJECTED as a testing gap / non-issue — the component design has no concept of nested trees; no stories/tests reference this pattern.

**Recommended fix:** Optional — add the same ownership guard for consistency/defense-in-depth, even though nesting isn't a supported use case today.

---

### 4. LOW (Maintainability) — Two sources of truth for tree membership

**Location:** `bds-tree-menu.tsx` — `this.items` Map vs. keyboard controller's `items()` callback

**Problem:** `this.items` (a `Map<string, HTMLElement>` built via `register()`/`unregister()` `@Method()` calls) is used only for `handleItemSelect`'s deselect-all and the registration-time duplicate-selected warning. The keyboard controller's `items()` callback independently re-queries the DOM via `querySelectorAll` on each key event.

**Impact:** Two different, not-obviously-related sources of truth for "what items exist in this tree." No concrete bug found, but a maintainability smell — future changes could easily update one without the other.

---

## Documentation Gaps

### JSDoc / Storybook argTypes

| Location | Issue |
|----------|-------|
| `bds-tree-menu.tsx:26` — `bdsChange` JSDoc | "Emitted when a tree menu item becomes selected" — doesn't mention checkbox toggles |
| `bds-tree-menu.stories.ts:124-133` — `onBdsChange` argTypes | Repeats the same incomplete wording |
| `bds-tree-menu.mdx:178` — events table | Accurate ("selected, or a checkable item's checkbox is toggled") but doesn't warn that detail can't distinguish checked from unchecked |

### Story coverage

| Story | Gap |
|-------|-----|
| `WithCheckboxes` | Wires no event listeners — never demonstrates `bdsChange` from a checkbox toggle |
| `Events`, `FileExplorer` | Only use non-checkable items |
| (none) | No story mixes checkable + non-checkable items in the same tree |

### MDX accessibility section

Silent on the fact that `aria-selected` on checkable items can flip independently of the visible checked state whenever selection changes elsewhere in the tree.

### `selected` prop documentation

Technically true but slightly misleading for checkable items: it only seeds `boxChecked` once at `componentWillLoad` (`bds-tree-menu-item.tsx:134-136`); afterward `selected` and `boxChecked` diverge completely. Docs don't state this divergence anywhere.

---

## Test Coverage Gaps

| Gap | Severity |
|-----|----------|
| Zero tests for checkable items through the root `bds-tree-menu` | HIGH |
| `bds-tree-menu.events.spec.tsx` never mentions "checkable"/"checked" | HIGH |
| No mixed-tree spec (checkable + non-checkable siblings) | MEDIUM |
| No test verifying `aria-selected` behavior on checkable items when selection changes elsewhere | MEDIUM |

---

## Summary

| # | Finding | Severity | Status |
|---|---------|----------|--------|
| 1 | `bdsChange` drops `checked` state for checkable items | HIGH | CONFIRMED by all 3 subagents |
| 2 | Selecting non-checkable item clears `aria-selected` on checkable items | MEDIUM | CONFIRMED by all 3 subagents |
| 3 | `handleDisabledChange` skips ownership filter | LOW | Real inconsistency, non-issue in practice |
| 4 | Two sources of truth for tree membership | LOW | Maintainability smell, no concrete bug |

### Critical path to merge (must fix)

1. Forward `checked` in `bdsChange`'s detail for the check path (or expose a public way to read it)
2. Correct the JSDoc + Storybook argTypes wording to mention checkbox toggles

### Should fix before merge

3. Either exclude checkable items from the deselect-all sweep, or document the `selected`/`checked` independence
4. Add a story demonstrating checkable items with event listeners

### Nice to fix

5. Add ownership guard to `handleDisabledChange` for consistency
6. Add a mixed-tree spec (checkable + non-checkable) to catch regression of finding #2
7. Document the `selected` vs `checked` divergence in MDX

---

## Subagent Validation Summary

| Subagent | Finding 1 | Finding 2 | Finding 3 | New Findings |
|----------|-----------|-----------|-----------|--------------|
| Frontend | CONFIRMED | CONFIRMED | CONFIRMED (real inconsistency) | Dual sources of truth for tree membership |
| Testing | CONFIRMED (no test coverage) | CONFIRMED (no mixed-tree spec) | REJECTED (non-issue, no nesting design) | — |
| Documentation | CONFIRMED (JSDoc/argTypes wrong) | CONFIRMED (doc gap) | Accurate with nuance | `selected` prop docs don't mention divergence from `checked` |
