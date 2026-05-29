# Research: `bds-select` Multiselect Extension via `bds-tag-field`

**Date:** 2026-05-28
**Scope:** `bds-select` · `bds-text-field` · `bds-tag-field` (EOA-13695)
**Question:** How would `bds-select` be extended to support multiselect once `bds-tag-field` exists, and what does the slot-based composition architecture buy us?

---

## Background

`bds-select` uses a named-slot architecture for its trigger field (`slot="field"`) and its option list (`slot="list"`). Today the trigger is always a `bds-text-field`. The `bds-tag-field` component being built in EOA-13695 makes it possible to swap the trigger without touching `bds-select`'s render method.

---

## Slot composition — the core advantage

`bds-select`'s render method requires **zero changes** for multiselect:

```tsx
// bds-select render() — today and after the multiselect extension
render() {
  return (
    <Host role="none">
      <slot name="field"></slot>   {/* ← consumer decides: text-field or tag-field */}
      <input type="hidden" value={this.value} name={this.name} />
      <bds-popover width="full">
        <slot name="list"></slot>
      </bds-popover>
    </Host>
  );
}
```

Every multiselect-specific UI concern — tag rendering, overflow badge, `maxVisibleTags`, `maxTagLength`, `tagColor` — is configured directly on `bds-tag-field` by the consumer. `bds-select` stays scoped to popover orchestration only. No multiselect prop cluster needed on the orchestrator.

---

## Usage comparison

### Single select (current — unchanged)

```html
<bds-select>
  <bds-text-field slot="field" placeholder="Select..."></bds-text-field>
  <bds-list-menu slot="list">
    <bds-list-menu-item value="1">Option 1</bds-list-menu-item>
    <bds-list-menu-item value="2">Option 2</bds-list-menu-item>
  </bds-list-menu>
</bds-select>
```

Visual — closed:
```
┌──────────────────────────────────────┐
│  Option 1                        [↓] │
└──────────────────────────────────────┘
```

### Multiselect (proposed — swap the slot content)

```html
<bds-select multiselect>
  <bds-tag-field slot="field" placeholder="Add..." max-visible-tags="3"></bds-tag-field>
  <bds-list-menu slot="list">
    <bds-list-menu-item value="1" checkable>Option 1</bds-list-menu-item>
    <bds-list-menu-item value="2" checkable>Option 2</bds-list-menu-item>
    <bds-list-menu-item value="3" checkable>Option 3</bds-list-menu-item>
  </bds-list-menu>
</bds-select>
```

Visual — closed (2 options selected):
```
┌──────────────────────────────────────────────────────────────┐
│  [Option 1 ×]  [Option 2 ×]  Add...                     [↓] │
└──────────────────────────────────────────────────────────────┘
```

Visual — open:
```
┌──────────────────────────────────────────────────────────────┐
│  [Option 1 ×]  [Option 2 ×]  Add...                     [↓] │
├──────────────────────────────────────────────────────────────┤
│  ☑  Option 1                                                 │
│  ☑  Option 2                                                 │
│  ☐  Option 3                                                 │
└──────────────────────────────────────────────────────────────┘
```

Dropdown **stays open** after each selection — closing only on Escape, click-outside, or an explicit confirm action.

---

## Internal wiring changes needed in `bds-select`

The `multiselect` boolean prop on `bds-select` is still needed — not to drive UI, but to signal which **event contract** to operate under. The changes are surgical.

### Critical constraint to fix first

```typescript
// bds-select.tsx line 113 — today
private get bdsField(): HTMLBdsTextFieldElement | null {
  return this.el.querySelector('bds-text-field');   // ← hardcoded tag name
}
```

Must become:
```typescript
private get bdsField(): HTMLBdsTextFieldElement | HTMLBdsTagFieldElement | null {
  return this.el.querySelector('bds-text-field, bds-tag-field');
}
```

This is the only structural change needed. All other methods already address `this.bdsField` generically.

### Full change surface

| Area | Change | Approx. lines |
|---|---|---|
| `bdsField` getter | `querySelector('bds-text-field, bds-tag-field')` | 1 |
| `multiselect` prop | New `@Prop() readonly multiselect: boolean = false` | 1 |
| `value` / `values` | Add `@Prop({ mutable: true }) values: string[] = []` for multiselect state | ~5 |
| `listenListMenu` | Toggle value in `values[]` instead of replacing `value`; keep popover open | ~12 |
| `listenClearInput` | Handle both `bdsClear` (tag-field) and existing clear path | ~5 |
| `listenBlurInput` | Skip blur-close logic when focus moves to list (multiselect stays open) | ~5 |
| `loadValue` | Handle `string[]` — call `bdsList.setSelectedValues` with array | ~15 |
| New: `listenTagRemove` | On `bdsTagRemove` from tag-field, deselect the matching option in bdsList | ~8 |
| `assignListeners` | Conditionally wire `bdsTagRemove` listener when `multiselect` is true | ~3 |

**Total: ~55 lines of change** inside `bds-select.tsx`. No changes to `bds-select.scss` or `bds-list-menu`.

---

## Event contract comparison

| Event | Single select | Multiselect |
|---|---|---|
| User picks option | `bdsChange` → `setValue(val)` → close popover | `bdsChange` → `toggleValue(val)` → keep open |
| User clears trigger | `bdsClear` → `setValue('')` | `bdsClear` → `setValues([])` |
| Tag removed | N/A | `bdsTagRemove` → deselect option in list |
| Blur trigger | Close popover if focus left component | Same |
| Escape key | Close popover | Close popover |

---

## `bds-list-menu` — required changes

`bds-list-menu-item` already has a `checkable` prop that renders a checkbox indicator. No new prop is needed. The only required change is ensuring `setSelectedValues` accepts a `string[]` and marks multiple items as selected simultaneously — this needs verification against the current `setSelectedValues` API when the multiselect ticket begins.

---

## Form serialisation

| Mode | `bds-select` emits | Submitted value |
|---|---|---|
| Single | `valueChange: string` | `<input type="hidden" value="option1">` |
| Multiselect | `valueChange: string[]` | `JSON.stringify(values)` in the hidden input, OR one hidden input per value using `FormData` |

The serialisation strategy for multiselect should be decided at the multiselect ticket level. Both approaches are valid; the `FormData` approach matches native `<select multiple>` semantics.

---

## Out of scope for EOA-13695 (tag-field ticket)

- The multiselect wiring in `bds-select` — separate ticket.
- `bds-tag-field` free-text mode vs. selection-only mode (for use inside `bds-select`, free-text entry should probably be disabled; a `freeText: boolean` prop may be needed).
- Keyboard navigation within the open multiselect dropdown (arrow keys between checkable items).
- "Select all / clear all" affordance inside the list.

---

## Conclusion

The slot-based architecture of `bds-select` means the multiselect extension is a minimal orchestration change (~55 lines), not a new component. The full visual layer is delivered by `bds-tag-field` from EOA-13695. Independent evolution of the two components is preserved — improving `bds-tag-field` (e.g. adding `maxTagLength`, `tagColor`) automatically benefits the multiselect select without any changes to `bds-select`.
