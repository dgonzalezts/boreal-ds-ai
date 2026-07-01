# BUG: Tooltip anchors to form field container instead of trigger icon

**Severity:** Medium
**Priority:** P2
**Type:** UI / Positioning
**Status:** Fixed
**Component(s):** `bds-tooltip`, `anchoredMixin`, `bds-typography`, `bds-text-field`
**Fixed in:** `anchoredMixin.onBeforeLoad()` — removed `parent.closest(ANCHORED_TRIGGERS)` from trigger resolution chain
**Introduced by:** PR `fix/EOA-13922-popover-fixes` (expanded `ANCHORED_TRIGGERS` constant into the `closest()` call)

---

## Environment

- **Framework:** Stencil Web Components (`@telesign/boreal-web-components`)
- **Repro story:** `Forms / Text Field → WithLabel` (Storybook)
- **Affected files:**
  - `packages/boreal-web-components/src/mixins/anchored.mixin.ts` (root cause)
  - `packages/boreal-web-components/src/components/overlays/bds-tooltip/bds-tooltip.tsx`
  - `packages/boreal-web-components/src/components/titles-text/bds-typography/bds-typography.tsx`
  - `packages/boreal-web-components/src/components/forms/bds-text-field/bds-text-field.tsx`

---

## Description

When a `bds-tooltip` rendered via `bds-typography`'s `tooltipText` prop is placed inside a `bds-text-field` (or any component that adds a matching CSS class to its host), the tooltip positions itself relative to the **entire form field container** rather than the small info icon that should be its trigger.

The tooltip appears centered on the field container (visually pointing at the middle of the input area) instead of anchored to the `ⓘ` icon next to the label.

---

## Steps to Reproduce

1. Open Storybook (`pnpm dev:docs` from the monorepo root).
2. Navigate to **Forms → Text Field → WithLabel**.
3. Hover over the `ⓘ` info icon next to the **Email address** label.

**Expected:** Tooltip appears anchored to and pointing at the `ⓘ` icon.
**Actual:** Tooltip appears centered above the text field container, arrow pointing at roughly the horizontal center of the field.

---

## Root Cause

`anchoredMixin.onBeforeLoad()` (line 338 in `anchored.mixin.ts`) resolves the tooltip's trigger element using this chain:

```typescript
// BEFORE fix (broken):
const trigger: HTMLElement =
  parent.closest(ANCHORED_TRIGGERS) || parent.querySelector(ANCHORED_TRIGGERS) || parent;
```

`ANCHORED_TRIGGERS = '.bds-button, .bds-text-field, .bds-tag-field, button, input, select'`

When `bds-tooltip` is nested inside `bds-typography → bds-text-field`:

1. `parent` = the `bds-typography__info` span (the info icon wrapper).
2. `parent.closest(ANCHORED_TRIGGERS)` walks **up** the ancestor chain and finds the `bds-text-field` host element — which carries the CSS class `bds-text-field` via its own `classMap: { [PREFIX]: true }`.
3. The entire text field becomes `this.triggerSlot`, causing the tooltip to anchor to it instead of the small icon.

The same `bds-tooltip` renders correctly in other contexts (e.g., inside a table header) because those ancestor chains contain no element matching `ANCHORED_TRIGGERS`, so `closest()` returns `null`, `querySelector()` also returns `null`, and the resolution correctly falls back to `parent` (the info span).

### Why the regression was introduced

The PR `fix/EOA-13922-popover-fixes` replaced a bespoke selector list (`.bds-button, .bds-input, .bds-select`) with the shared `ANCHORED_TRIGGERS` constant. The constant includes `.bds-text-field`, which `bds-text-field` applies to its own host element — causing the `closest()` walk to overshoot to the field container.

---

## Fix Applied

```typescript
// AFTER fix (correct):
const trigger: HTMLElement =
  parent.closest<HTMLElement>('button, input, select') ??
  parent.querySelector<HTMLElement>(ANCHORED_TRIGGERS) ??
  parent;
```

`closest()` is now scoped to **native** HTML interactive elements only. This preserves the case where Stencil's slot polyfill physically moves a popover/tooltip inside a `<button>` element — `closest('button')` correctly walks up to it — while preventing the walker from reaching custom-element hosts like `<bds-text-field class="bds-text-field">` that carry BDS class names on the host itself.

`querySelector(ANCHORED_TRIGGERS)` handles sibling-trigger layouts (e.g. tooltip next to an `<input>`). The `?? parent` fallback covers cases where the parent itself is the trigger.

**Verified:** All 1,620 unit tests pass (`pnpm test` in `packages/boreal-web-components`).

### Impact assessment

| Scenario | Before fix | After fix | Risk |
|---|---|---|---|
| Tooltip inside `bds-typography` inside `bds-text-field` | Anchors to text field (BUG) | Anchors to info span | ✅ Fixed |
| Popover slotted inside `bds-button` (slot polyfill nests it inside `<button>`) | `closest('button')` found it | `closest('button, input, select')` finds it | ✅ None |
| Tooltip sibling to `<input>` inside a wrapper div | `querySelector` finds input | Same | ✅ None |
| Tooltip direct child of `<button>` | `?? parent` fallback = button | Same | ✅ None |
| Popover click-outside (`listenTarget`) detection | Uses `closest()` inside `bds-popover.subscribe()` — unaffected | Same | ✅ None |

`bds-popover.subscribe()` independently calls `trigger.closest(ANCHORED_TRIGGERS)` to resolve `this.listenTarget` for click-outside and focus-outside detection. That separate call operates on the already-resolved trigger element and is **not** affected by this fix.

---

## Visual Evidence

- **Bug:** Tooltip centered on the text field container (see `WithLabel` Storybook story before fix).
- **Working reference:** Same `bds-typography` tooltip rendered inside a table header renders correctly, confirming the issue is context-dependent.

---

## Regression Risk

Low. The `closest()` path only adds value in the unusual case where the tooltip's parent has no descendant interactive elements AND the tooltip itself is a grandchild of an interactive ancestor. The `|| parent` fallback correctly handles the common case where the tooltip's direct parent is (or is inside) the intended trigger element.

---

## Related

- `anchoredMixin` is also used by `bds-popover`; no popover regressions identified.
- Known separate bug, now fixed (2026-07-01): `mouseleave` "stay on hover" logic in `bds-tooltip.tsx` used `e.target` instead of `e.relatedTarget`. See `ai-work/qa/bug-reports/EOA-15147-bds-tooltip-bug-001.md` and `.agents/memory/mouseleave-relatedtarget-vs-target.md`.
