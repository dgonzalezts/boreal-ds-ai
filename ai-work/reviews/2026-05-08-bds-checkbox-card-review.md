# Boreal DS — Code Review Report

**Generated:** 2026-05-08T16:18:14  
**Base ref:** `release/current`  
**Repository:** `.`
**Component:** `bds-checkbox-card`

## Affected Packages

- **boreal-docs (Storybook)** — checklist section(s): D
- **boreal-web-components (Stencil)** — checklist section(s): A

## Automated Findings

- 🟡 **[prop-mutable-form-attr]** Native form attribute prop should not use `mutable: true`. Use a `@State() private is<Prop>` mirror instead and write to it in `formDisabledCallback` / `@Watch`. See coding_standards.md. `packages/boreal-web-components/src/components/forms/bds-checkbox-card/bds-checkbox-card.tsx:67` _(note: `@State()` mirrors already exist — see Memory-Guided Review)_
- 🔴 **[event-name-format]** @Event() name 'valueChange' does not follow the `bds{Action}` format. `packages/boreal-web-components/src/components/forms/bds-checkbox-card/bds-checkbox-card.tsx:80` _(false positive — Vue v-model reserved name; see Memory-Guided Review)_
- 🟡 **[face-reset-no-validity]** `formResetCallback` is defined but `updateValidity()` or `setValidity()` is not called — validity state may be stale after reset. `packages/boreal-web-components/src/components/forms/bds-checkbox-card/bds-checkbox-card.tsx`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/forms/bds-checkbox-card/bds-checkbox-card.tsx:2`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/forms/bds-checkbox-card/bds-checkbox-card.tsx:4`
- 🟡 **[prop-mutable-form-attr]** Pre-existing in `bds-checkbox.tsx:70` — outside this PR's scope.
- 🔴 **[event-name-format]** `valueChange` in `bds-checkbox.tsx:89` — same false positive as above.
- 🟡 **[face-reset-no-validity]** Pre-existing in `bds-checkbox.tsx` — outside this PR's scope.
- 🔵 **[missing-changeset]** No changeset or CHANGELOG entry detected for package-level changes.

## Review Checklist

### Universal

- ✅ Change has a clear purpose with minimal unrelated edits
- ✅ No `any` usage without justification
- ✅ Error paths and invalid inputs handled explicitly
- ✅ New logic is covered by tests
- ✅ Tests use `waitForChanges()` before DOM assertions
- ❌ Storybook/MDX/README updated when behavior or APIs change
- ✅ Public APIs, events, and props follow naming conventions

### A — Stencil (boreal-web-components)

- ❌ Every @Prop() has `readonly` and an adjacent JSDoc block
  - **Standard:** `stencil/props-must-be-readonly` is an ESLint error. `readonly` and `mutable: true` are orthogonal — both must be present on the same declaration.
  - **Antipattern:** `@Prop({ mutable: true, reflect: true }) checked` (line 67) and `@Prop({ mutable: true, reflect: true }) indeterminate` (line 70) are both missing `readonly`.
- ❌ Native form attrs (`disabled`, `checked`, `value`) use `@State()` mirror, not `mutable: true`
  - **Standard:** `checked` and `indeterminate` do correctly use `@State()` mirrors (`isChecked`, `isIndeterminate`) with `@Watch()` + `componentWillLoad()` sync — the architecture is right. The only residual issue is that `readonly` is missing from the `mutable` prop declarations (see above).
  - **Note:** `disabled` correctly uses `@State() private isDisabled` with `formDisabledCallback` override. No issue there.
- ✅ `validatePropValue` + `componentWillLoad()` + `@Watch()` for enum-like props
- ❌ Custom events use the `bds{Action}` prefix pattern (e.g. `bdsClose`, not `bdsBannerClose`)
  - **Exception (acceptable):** `valueChange` is the reserved name required by `IFormValueEmitter<boolean>` for Vue `v-model` support. The `event-name-format` finding is a **false positive**. No change needed.
- ✅ Event names do not reuse native DOM events
- ✅ @AttachInternals() is on the class body, not in a mixin
- ❌ `checkValidity()` and `reportValidity()` exposed via @Method()
  - **Standard:** FACE components must expose `checkValidity()` and `reportValidity()` via `@Method()` so consumers and tests can call them through Stencil's element proxy.
  - **Finding:** `bds-checkbox-card` is `formAssociated: true` but has no `@Method() async checkValidity()` or `@Method() async reportValidity()` declarations. The `formAssociatedMixin` does not provide these. The checklist's ✅ was a **false negative** in the automated script. Unlike `bds-radio-group` (which explicitly declares both), this component leaves them inaccessible.
- ✅ Only ElementInternals.setValidity() manages validity
- ❌ `formResetCallback` and `formStateRestoreCallback` call updateValidity()
  - **Standard:** Both callbacks must call `internals.setValidity(...)` to keep the ElementInternals validity object in sync with the restored state.
  - **`formResetCallback` (line 143):** Resets `isChecked` and sets form value to `null` but does not call `setValidity`. If the component is `required`, after reset the value is absent and should become invalid — but `ElementInternals` validity is never updated.
  - **`formStateRestoreCallback` (line 149):** Calls `syncFormValue()` (which sets the form value) but also does not call `setValidity`. Same risk on session restore.
- ✅ JSDoc changes preserve custom-elements.json generation accuracy
- ✅ Boolean @Prop() names use no `is`/`has`/`show` prefix
- ✅ Props declared on component class, not inside mixin factory
- ✅ No no-op constructor in mixin factory (use ESLint override instead)
- ✅ ARIA attribute names passed to `setAttribute` are kebab-case
- ✅ No dead `declare global` Popover API blocks (redundant since TS 5.2)
- ✅ Interface files named `IComponent.ts`, not `IBdsComponent.ts`
- ✅ Getter accessors carry no redundant `get` prefix

### D — Docs (Storybook)

- ✅ Component behavior changes reflected in stories and MDX
- ✅ Storybook aliasing intact for @telesign/boreal-web-components/css/*
- ✅ Uses `dotenv --` and `--storybook-build-dir`

## Memory-Guided Review

### 1. Indexed Access Types on `@Prop()` and `@Event()` — `bds-checkbox-card.tsx` (all declarations) 🔴

**Source:** `.claude/memory/stencil-prop-patterns.md` — "Never Use Indexed Access Types on @Prop() Declarations"

Every `@Prop()` and both `@Event()` declarations use the `ICheckboxCard['member']` indexed access form:

```tsx
@Prop({ reflect: true }) readonly name!: ICheckboxCard['name'];
@Prop({ reflect: true }) readonly disabled: ICheckboxCard['disabled'] = false;
// ... all 8 props

@Event() valueChange!: ICheckboxCard['valueChange'];
@Event() bdsChange!: ICheckboxCard['bdsChange'];
```

The root cause is especially significant here: `ICheckboxCard` extends `ICheckbox`, and `ICheckbox.ts` imports `EventEmitter` from `@stencil/core/internal` (the non-public internal path):

```typescript
// ICheckbox.ts — line 1
import type { EventEmitter } from '@stencil/core/internal';
```

When the Stencil decorator transform encounters `ICheckboxCard['valueChange']`, it traces through `ICheckbox['valueChange']` → `EventEmitter<boolean>` from `@stencil/core/internal`. That path is not available at transform time, causing the type to degrade to `error`. This affects `no-unsafe-assignment` on every subsequent read of those props/events.

**Fix — two steps:**

1. Change `ICheckbox.ts` line 1 to import from the public path:
   ```typescript
   import type { EventEmitter } from '@stencil/core';
   ```

2. Replace every indexed access type with the concrete primitive on `bds-checkbox-card.tsx` props:
   ```tsx
   @Prop({ reflect: true }) readonly name!: string;
   @Prop({ reflect: true }) readonly disabled: boolean = false;
   @Prop({ reflect: true }) readonly required: boolean = false;
   @Prop({ reflect: true }) readonly value: string = 'on';
   @Prop() readonly label: string = '';
   @Prop({ mutable: true, reflect: true }) readonly checked: boolean = false;
   @Prop({ mutable: true, reflect: true }) readonly indeterminate: boolean = false;
   @Prop({ reflect: true }) readonly error: boolean = false;
   ```

3. Declare `@Event()` types concretely (the `implements IFormControl<boolean>` clause already enforces the contract):
   ```tsx
   @Event() valueChange!: EventEmitter<boolean>;
   @Event() bdsChange!: EventEmitter<CheckboxChangeDetail>;
   ```

---

### 2. `checked` and `indeterminate` missing `readonly` — `bds-checkbox-card.tsx:67,70` 🔴

**Source:** `.claude/memory/stencil-prop-patterns.md`

Both mutable props are missing the `readonly` keyword:

```tsx
// ❌ Current
@Prop({ mutable: true, reflect: true }) checked: ICheckboxCard['checked'] = false;
@Prop({ mutable: true, reflect: true }) indeterminate: ICheckboxCard['indeterminate'] = false;

// ✅ Correct
@Prop({ mutable: true, reflect: true }) readonly checked: boolean = false;
@Prop({ mutable: true, reflect: true }) readonly indeterminate: boolean = false;
```

The `@State()` mirror architecture (`isChecked`, `isIndeterminate`) is correct. The only missing piece is `readonly` on the prop declarations.

---

### 3. `checkValidity()` and `reportValidity()` not exposed — false negative in checklist 🔴

**Source:** `.claude/memory/stencil-face-element-proxy-limits.md`

The automated checklist marked this as ✅ but the component does **not** declare these methods. `formAssociatedMixin` only provides `formDisabledCallback` — it does not provide `checkValidity()` or `reportValidity()`. The component has no `@Method()` wrappers.

Without these, consumers and test specs cannot call `element.checkValidity()` through Stencil's element proxy — the call is silently dropped (proxy blocks native FACE prototype members).

**Fix:** Add to the component class:
```tsx
@Method()
async checkValidity(): Promise<boolean> {
  return this.internals.checkValidity();
}

@Method()
async reportValidity(): Promise<boolean> {
  return this.internals.reportValidity();
}
```

---

### 4. `formResetCallback` and `formStateRestoreCallback` missing validity sync 🔴

**Source:** `.claude/memory/stencil-face-constraint-validation-pattern.md`

The component has a `required` prop. After a reset or state restore, if the component ends up unchecked and is `required`, the browser form validation state is stale.

**`formResetCallback` (line 143) fix:**
```tsx
formResetCallback(): void {
  this.isChecked = false;
  this.isIndeterminate = false;
  setFormValue(this.internals, null);
  if (this.required) {
    this.internals.setValidity({ valueMissing: true }, 'Please check this field.');
  } else {
    this.internals.setValidity({});
  }
}
```

**`formStateRestoreCallback` (line 149) fix:**
```tsx
formStateRestoreCallback(state: unknown, _mode: string): void {
  this.isChecked = state === this.value;
  this.syncFormValue();
  if (this.required && !this.isChecked) {
    this.internals.setValidity({ valueMissing: true }, 'Please check this field.');
  } else {
    this.internals.setValidity({});
  }
}
```

---

### 5. `ICheckboxCard` interface declares `helperText` not implemented by the component 🟡

`ICheckboxCard.ts` declares `helperText: string` as a required member:
```typescript
export interface ICheckboxCard extends ComponentInterface, ICheckbox {
  name: string;
  disabled: boolean;
  required: boolean;
  helperText: string;  // ← not implemented in BdsCheckboxCard
}
```

`BdsCheckboxCard` does not have a `helperText` prop, which should produce a TypeScript `implements` error. This appears to be a copy-paste artifact from a group component interface. Either:
- Remove `helperText` from `ICheckboxCard` if the standalone card is not expected to display helper text, or
- Add `helperText` as a `@Prop()` and render it (consistent with `bds-text-field` and `bds-radio-group` patterns)

---

### 6. Class-level `@property` JSDoc tags are non-standard and duplicate `@Prop()` JSDoc 🟡

**Source:** `.claude/memory/stencil-prop-patterns.md` — non-standard class-level JSDoc tags are silently ignored by the CEM analyzer

Lines 16–27 use `@property {type} name - description` syntax in the component class JSDoc. The CEM analyzer does not recognize `@property` — it reads prop descriptions from the JSDoc blocks directly above each `@Prop()` decorator. These create duplicate documentation that diverges when a prop is updated.

Additionally, the `@fires` tags on lines 25–26 are similarly ignored by the CEM (event documentation comes from `@Event()` JSDoc). These tags belong in a developer wiki or changelog, not the component class JSDoc.

**Fix:** Remove the `@property` and `@fires` lines from the class-level JSDoc. The individual `@Prop()` and `@Event()` JSDoc blocks already provide the correct documentation surface.

---

### 7. Section divider comments violate project comment policy 🟡

Lines 42–45, 57–60, and 75–78 use section divider comment blocks:
```tsx
// ---------------------------------------------------------------------------
// Props
// ---------------------------------------------------------------------------
```

Per CLAUDE.md: "Not allowed: Section divider comments (e.g. `// --- helpers ---`)." These add visual noise but provide no information a reader couldn't derive from the code structure. Remove them.

---

### 8. Import order violations 🟡

**Source:** `.claude/memory` (import order convention)

Current order (lines 1–4):
```tsx
import { formAssociatedMixin, IFormControl } from '@/mixins';   // @/mixins first ❌
import { AttachInternals, ... } from '@stencil/core';           // framework second ❌
import { ICheckboxCard } from './types/ICheckboxCard';
import { setFormValue } from '@/utils';                         // @/utils last ❌
```

Required order:
```tsx
import { AttachInternals, ... } from '@stencil/core';           // 1. framework
import { formAssociatedMixin, IFormControl } from '@/mixins';   // 2. @/mixins
import { setFormValue } from '@/utils';                         // 3. @/utils
import { ICheckboxCard } from './types/ICheckboxCard';          // 4. local
```

---

### 9. `valueChange` event naming — false positive ✅

**Source:** `.claude/memory/stencil-form-control-interfaces.md`

Same exception as `bds-radio-group` and all FACE components in this codebase. `valueChange` is the required name enforced by `IFormValueEmitter<boolean>` for Vue `v-model` support. No change needed.

---

### 10. `aria-label` fallback to `name` prop 🟡

`render()` line 166:
```tsx
aria-label={this.label || this.name || undefined}
```

When neither `label` prop nor default slot content is provided, the component falls back to `this.name` (the form control name, e.g. `"agreement"`) as the accessible label. A form field name is an identifier, not a human-readable description. This fallback may not meet WCAG 2.1 SC 1.1.1 in all usage contexts. Consider documenting in MDX that consumers must always provide either a `label` prop or slot content.

---

### Memory topic files consulted

| File | Applied to |
|------|-----------|
| `stencil-prop-patterns.md` | indexed access types, mutable/readonly, `@stencil/core/internal` import |
| `stencil-face-element-proxy-limits.md` | missing `checkValidity`/`reportValidity` `@Method()` wrappers |
| `stencil-face-constraint-validation-pattern.md` | `formResetCallback`/`formStateRestoreCallback` validity sync |
| `stencil-form-control-interfaces.md` | `valueChange` false positive, `IFormControl<T>` |
| `feedback_event_naming.md` | event name convention |
| `component-interface-content-rule.md` | `helperText` in `ICheckboxCard` |
| `mouseleave-relatedtarget-vs-target.md` | not applicable |

---

**Result: 18 passed · 7 failed** _(3 additional failures found in memory-guided pass; 2 automated false positives resolved; 1 automated false negative corrected)_

_Generated by [review_report_generator.py](.claude/skills/code-reviewer/scripts/review_report_generator.py)_
