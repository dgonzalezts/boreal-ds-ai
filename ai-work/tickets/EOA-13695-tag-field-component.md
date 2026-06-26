# Ticket — `bds-tag-field` Component

## 1. Clear and Concise Title
**Implement `bds-tag-field` Form Component**

## 2. Detailed Description

### Purpose
Deliver a Tag Field form component that lets users enter and remove multiple discrete values inside a single form control. The Tag Field renders a bordered (or plain) container — visually consistent with `bds-text-field` — that holds a wrapping row of `bds-tag` chips and an inline free-text input.

`bds-tag` already exists at `packages/boreal-web-components/src/components/feedback/bds-tag/`. This ticket covers only **`bds-tag-field`**, which composes `bds-tag` internally.

> **Pending UX/UI confirmation:** Before starting SCSS work, confirm with the UX/UI team whether the visual shell (container, label, helper text, footer) should share tokens with `bds-text-field` by duplicating only the structural differences, or directly compose the component. The recommendation is to **share tokens and duplicate the structural CSS** — keeping the two components independently evolvable — rather than extending `bds-text-field`'s class hierarchy.

---

### Existing `bds-tag` — Relevant API

The existing chip component at `feedback/bds-tag/` provides the following surface that `bds-tag-field` depends on:

| Prop / Event     | Type / Payload                          | Notes |
|------------------|-----------------------------------------|-------|
| `color`          | `'gray' \| 'cyan' \| 'cobalt' \| ...`  | Default color for field-rendered tags should be `'gray'` (`$boreal-extended-onyx-light` fill). |
| `readonly`       | `boolean`                               | Set `true` to hide the close button (used for disabled field state). |
| `disabled`       | `boolean`                               | Reduces opacity and blocks interaction. |
| `closeButtonLabel` | `string`                              | Must be set to `'Remove {label}'` per tag for accessible labelling. |
| `bdsClose`       | `{ id: string, selected: boolean, el: HTMLElement }` | Fired when the user dismisses a tag. The field listens to this event and correlates `id` to its internal value list. |

> **Implementation note:** `bds-tag` emits `{ id }` (its internal generated ID), not `{ value }`. `bds-tag-field` must maintain a map of `id → value` (or keep tags in insertion order and match by DOM position) to know which value to remove when `bdsClose` fires.

---

### `bds-tag-field` — Visual Anatomy

```
bds-tag-field (Host)
├── bds-typography[variant="label"]     (optional — rendered when `label` prop is set)
├── .bds-tag-field__container
│   ├── bds-tag × N                     (one per committed value, color="gray", closeButtonLabel="Remove {label}")
│   ├── <input>                         (inline free-text entry, grows to fill remaining space)
│   └── .bds-tag-field__actions
│       └── Clear button                (optional — visible when `clearable` and values.length > 0)
└── .bds-tag-field__footer
    ├── bds-typography[variant="helper"] (helper text or error message)
    └── .bds-tag-field__tag-count        (optional tag counter)
```

**Container layout differences from `bds-text-field`:**
- Height is dynamic (hugs content) — not fixed at `$boreal-layout-l`.
- Content wraps (`flex-wrap: wrap`) to accommodate multiple tag rows.
- Minimum height matches `bds-text-field` container height for visual consistency when empty.
- `overflow` must be `visible` (not `hidden`) to allow wrapped rows.

---

### Props

| Prop                | Type                                        | Default      | Description |
|---------------------|---------------------------------------------|--------------|-------------|
| `name`              | `string`                                    | `''`         | Submitted form field name. |
| `values`            | `string[]`                                  | `[]`         | Current list of committed tag values (mutable). |
| `disabled`          | `boolean`                                   | `false`      | Disables the field and all inner `bds-tag` instances. |
| `required`          | `boolean`                                   | `false`      | Marks the field as required; at least one tag must be present to pass validation. |
| `error`             | `boolean`                                   | `false`      | Forces the error visual state independently of validation. |
| `errorMessage`      | `string`                                    | `''`         | Shown in the footer when `error` is `true`. Replaces `helperText`. |
| `helperText`        | `string`                                    | `''`         | Assistive text shown in the footer when there is no error. |
| `label`             | `string`                                    | `''`         | Label text rendered above the container via `bds-typography[variant="label"]`. |
| `info`              | `string`                                    | `''`         | Tooltip content attached to the label (forwarded as `tooltipText` to `bds-typography`). |
| `placeholder`       | `string`                                    | `''`         | Native `placeholder` forwarded to the inner `<input>`. Hidden once at least one tag exists. |
| `variant`           | `'outline' \| 'plain'`                      | `'outline'`  | Visual style — `outline` shows a border; `plain` hides it at rest. |
| `clearable`         | `boolean`                                   | `false`      | Shows a clear-all action button when at least one tag exists. |
| `customValidators`  | `IFormValidator[]`                          | `[]`         | Additional validators merged with the built-in rules. |
| `validationTiming`  | `'blur' \| 'input' \| 'submit' \| 'change'`| `'blur'`     | When built-in validation runs. |
| `customWidth`       | `string`                                    | `''`         | Sets `--bds-tag-field-width` CSS custom property. |
| `allowDuplicates`   | `boolean`                                   | `false`      | When `false`, adding a value already in the list is silently ignored. |
| `maxTags`           | `number`                                    | `0`          | Maximum number of tags allowed. `0` means no limit. When the limit is reached, the input is hidden. |

---

### Events

| Event                 | Payload                                                               | When |
|-----------------------|-----------------------------------------------------------------------|------|
| `valueChange`         | `string[]`                                                            | Emitted on every change; used for framework 2-way binding. |
| `bdsTagAdd`           | `{ value: string }`                                                   | A new tag was committed. |
| `bdsTagRemove`        | `{ value: string }`                                                   | A tag was removed. |
| `bdsClear`            | `void`                                                                | All tags were cleared via the clear button. |
| `bdsFocus`            | `{ event: FocusEvent }`                                               | The inner input gained focus. |
| `bdsBlur`             | `{ event: FocusEvent }`                                               | The inner input lost focus. |
| `bdsValidationChange` | `{ valid: boolean, validity: ValidityState, value: string[], touched: boolean, dirty: boolean }` | After each validation run. |

---

### Methods

| Method          | Signature                  | Description |
|-----------------|----------------------------|-------------|
| `checkValidity` | `() => Promise<boolean>`   | Delegates to `ElementInternals.checkValidity()`. |
| `reportValidity`| `() => Promise<boolean>`   | Delegates to `ElementInternals.reportValidity()`. |

---

### Keyboard Interactions

| Key           | Behaviour |
|---------------|-----------|
| `Enter` / `,` | Commits the current input text as a new tag (trims whitespace; ignores empty strings). |
| `Backspace`   | When the input is empty, removes the last tag in the list. |
| `Escape`      | Clears the current input text without committing. |

---

### Built-in Validation Rules

| Key              | Rule                                                  | Default message |
|------------------|-------------------------------------------------------|-----------------|
| `valueMissing`   | `required === true` and `values.length === 0`         | `'At least one tag is required.'` |
| `rangeOverflow`  | `maxTags > 0` and `values.length > maxTags`           | `'Maximum of {maxTags} tags allowed.'` |

---

### Variant Behaviour

- **`outline`** (default): container has a visible border (`$boreal-stroke-default-light`), focus ring on focus, error border on error — matching `bds-text-field` outline semantics.
- **`plain`**: border is transparent at rest; border and focus ring appear on focus, matching `bds-text-field--plain` semantics. Intended for dense layouts and inline filter bars.

---

### Form Integration (FACE)

- Uses `@AttachInternals()` and `formAssociated: true`.
- `setFormValue` is called with `JSON.stringify(values)` on every change. This is intentional: `ElementInternals.setFormValue()` accepts only a string or `FormData`, not an array. Document this in the JSDoc.
- Implements `formResetCallback`, `formStateRestoreCallback`, and `formDisabledCallback` via `formAssociatedMixin`.
- `formDisabledCallback` must propagate `disabled` down to all rendered `bds-tag` children.
- Register `bds-tag-field` in `vue-output-target.ts` `componentModels` for Vue `v-model` support. This must land in the same PR as the component.

---

### File Structure

```
packages/boreal-web-components/src/components/forms/bds-tag-field/
├── bds-tag-field.tsx
├── bds-tag-field.scss
├── types/
│   ├── ITagField.ts
│   ├── enum.ts
│   ├── types.ts
│   └── index.ts
└── __test__/
    ├── bds-tag-field-basics.spec.ts
    ├── bds-tag-field-events.spec.ts
    ├── bds-tag-field-keyboard.spec.ts
    ├── bds-tag-field-validation.spec.ts
    ├── bds-tag-field-form.spec.ts
    └── bds-tag-field-a11y.spec.ts
```

The existing `bds-tag` at `feedback/bds-tag/` requires **no changes** for this ticket.

---

### Out of Scope (Future Enhancements)

- **Autocomplete / suggestions dropdown:** Free-text entry only in this iteration. A future `suggestions` prop could wire up a floating listbox; track as a separate ticket to avoid a premature dependency on a popover layer.
- **Async tag resolution:** Loading tags from a remote source.
- **Drag-to-reorder tags.**
- **Color variants per tag:** All tags inside the field default to `'gray'`. Exposing per-tag color is a future enhancement.

---

## 3. Acceptance Criteria

- Renders an `outline` container (bordered, matching `bds-text-field` visual) holding zero or more `bds-tag` chips and an inline input.
- `plain` variant renders without a border at rest; border appears on focus.
- Pressing `Enter` or `,` commits non-empty trimmed input as a new tag; input clears afterward.
- Pressing `Backspace` on an empty input removes the last tag.
- Pressing `Escape` clears the input text without committing.
- Duplicate values are silently ignored when `allowDuplicates` is `false`.
- When `maxTags` is reached, the input is hidden and no further tags can be added.
- Clicking a tag's close button removes that tag from `values` and emits `bdsTagRemove`.
- `clearable` shows a clear-all button when `values.length > 0`; clicking emits `bdsClear` and empties `values`.
- `required` validation fails when `values.length === 0`; error message `'At least one tag is required.'` appears in the footer.
- `maxTags` validation error message appears in the footer when the limit is exceeded.
- `error` prop forces the error visual state independently of validation.
- `label` renders via `bds-typography[variant="label"]` with `required` indicator and optional tooltip.
- `helperText` and `errorMessage` render via `bds-typography[variant="helper"]`.
- `formResetCallback` clears all tags and resets `dirty`/`touched` state.
- Form serialises `values` as `JSON.stringify(values)` for native form submission.
- Vue `v-model` binds correctly after `componentModels` registration.
- All keyboard interactions listed above pass automated tests.
- Each `bds-tag`'s `closeButtonLabel` is set to `'Remove {label}'` for screen reader accessibility.
- `aria-invalid` is set on the container when the field is in an error state.
- `aria-required` is set on the inner input when `required` is `true`.

### Tests
- **basics:** renders tags from initial `values`, adds a tag on Enter/comma, ignores empty input, ignores duplicates when `allowDuplicates=false`.
- **keyboard:** Backspace on empty input removes last tag, Escape clears input, Enter with whitespace-only input is ignored.
- **events:** `bdsTagAdd`, `bdsTagRemove`, `bdsClear`, `valueChange`, `bdsFocus`, `bdsBlur` fire with correct payloads.
- **validation:** `valueMissing` fires on blur when required and empty; `rangeOverflow` fires when `maxTags` exceeded; custom validators merge correctly; `validationTiming` modes respected.
- **form:** `formResetCallback` clears state; `formDisabledCallback` disables all tags; `setFormValue` called with JSON-serialised values.
- **a11y:** `aria-invalid` present in error state; `aria-required` on inner input; `closeButtonLabel` on each tag matches `'Remove {label}'`.

---

## 4. Comments and Notes

- **UX/UI sign-off required** before SCSS work begins: confirm token-sharing vs. direct composition approach with `bds-text-field`.
- `bds-tag` emits `{ id }` in `bdsClose`, not `{ value }`. `bds-tag-field` must maintain an internal `id → value` map, built when tags are rendered, to resolve which value to remove on close.
- All tags inside the field use `color="gray"` by default — this aligns with the Figma `extended/onyx-light` fill already used by `bds-tag--gray`.
- The `Close` button inside `bds-tag` is already `type="button"` — no change needed there.
- Estimated effort: ~3–4 developer days (1–1.5 days for core logic + rendering, 1 day for SCSS + states, 1 day for tests, 0.5 day for Vue `componentModels` + smoke test).

---

## 5. Links or References

- [Figma spec — Tag Field](https://www.figma.com/design/rtiE5zGA4aoOuxIQMgfD6h/-BOR--DSG-COMPONENTS-%E2%86%92-FORMS?node-id=117-107271&m=dev)
- [Existing `bds-tag` component](packages/boreal-web-components/src/components/feedback/bds-tag/bds-tag.tsx)
- [Existing `bds-text-field` component](packages/boreal-web-components/src/components/forms/bds-text-field/bds-text-field.tsx)
- [FACE / form-associated mixin](.agents/memory/stencil-face-attach-internals.md)
- [FACE element proxy limits](.agents/memory/stencil-face-element-proxy-limits.md)
- [Component interface file naming convention](memory/component-interface-file-naming.md)
- [Group component label conventions](.agents/memory/component-bds-typography-group-labels.md)
- [Stencil form control interfaces](.agents/memory/stencil-form-control-interfaces.md)
