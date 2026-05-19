# Boreal DS — Code Review Report

**Generated:** 2026-05-08T15:30:00  
**Base ref:** `release/current`  
**Repository:** `.`

## Affected Packages

- **boreal-docs (Storybook)** — checklist section(s): D
- **boreal-web-components (Stencil)** — checklist section(s): A

## Automated Findings

- 🟡 **[prop-mutable-form-attr]** Native form attribute prop should not use `mutable: true`. Use a `@State() private is<Prop>` mirror instead and write to it in `formDisabledCallback` / `@Watch`. See coding_standards.md. `packages/boreal-web-components/src/components/forms/bds-radio-card/bds-radio-card.tsx:48`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/forms/bds-radio-card/bds-radio-card.tsx:2`
- 🟡 **[prop-mutable-form-attr]** Native form attribute prop should not use `mutable: true`. Use a `@State() private is<Prop>` mirror instead and write to it in `formDisabledCallback` / `@Watch`. See coding_standards.md. `packages/boreal-web-components/src/components/forms/bds-radio-group/bds-radio-group.tsx:80`
- 🔴 **[event-name-format]** @Event() name 'valueChange' does not follow the `bds{Action}` format. Custom events must start with `bds` followed by an uppercase letter (e.g. `bdsClose`, `bdsChange`). `packages/boreal-web-components/src/components/forms/bds-radio-group/bds-radio-group.tsx:112` _(see Memory-Guided Review — false positive)_
- 🟡 **[prop-mutable-form-attr]** Native form attribute prop should not use `mutable: true`. Use a `@State() private is<Prop>` mirror instead and write to it in `formDisabledCallback` / `@Watch`. See coding_standards.md. `packages/boreal-web-components/src/components/forms/bds-radio/bds-radio.tsx:21`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/forms/bds-radio/bds-radio.tsx:3`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/types/index.ts:1`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/types/index.ts:2`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/types/index.ts:3`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/types/index.ts:4`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/types/index.ts:5`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/types/index.ts:6`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/types/index.ts:7`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/types/index.ts:8`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/types/index.ts:9`
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
  - **Standard:** `stencil/props-must-be-readonly` is enforced as an ESLint error. Every prop must carry the `readonly` TypeScript keyword, even when `mutable: true` is also set — the two are orthogonal.
  - **Antipattern:** `@Prop({ mutable: true, reflect: true }) checked: boolean` — missing `readonly`. Correct form: `@Prop({ mutable: true, reflect: true }) readonly checked: boolean`. Affects `bds-radio-card.tsx:48` and `bds-radio.tsx:21`.
- ❌ Native form attrs (`disabled`, `checked`, `value`) use `@State()` mirror, not `mutable: true`
  - **Standard (FACE components):** `disabled` and `value` on a `formAssociated: true` component must use `@State() private isDisabled / internalValue` written by both `@Watch` and `formDisabledCallback`. Using `mutable: true` creates two writers on the same reflected attribute and produces a Stencil compiler warning.
  - **Standard (leaf components):** `checked` on non-FACE leaf components (`bds-radio`, `bds-radio-card`) can legitimately use `mutable: true` since the parent group writes to it directly — but `readonly` must still be present on the declaration.
  - **Antipattern:** `@Prop({ mutable: true }) value: string` on `bds-radio-group` (FACE) — `value` is written internally on every selection, which races with external prop bindings. Use `@State() private internalValue`.
- ✅ `validatePropValue` + `componentWillLoad()` + `@Watch()` for enum-like props
- ❌ Custom events use the `bds{Action}` prefix pattern (e.g. `bdsClose`, not `bdsBannerClose`)
  - **Standard:** All `@Event()` names must start with `bds` followed by an uppercase letter.
  - **Exception (acceptable):** `valueChange` is the **reserved name** required by `IFormValueEmitter<T>` for Vue `v-model` integration — the `event-name-format` script finding is a **false positive**. See `stencil-form-control-interfaces.md` and `componentModels` config in `vue-output-target.ts`. No change needed.
- ✅ Event names do not reuse native DOM events
- ✅ @AttachInternals() is on the class body, not in a mixin
- ✅ `checkValidity()` and `reportValidity()` exposed via @Method()
- ✅ Only ElementInternals.setValidity() manages validity
- ❌ `formResetCallback` and `formStateRestoreCallback` call updateValidity()
  - **Standard:** Both callbacks must call `updateFormValidity()` (or equivalent) after restoring state so that the ElementInternals validity object reflects the restored value.
  - **Antipattern found:** `formStateRestoreCallback` in `bds-radio-group.tsx:159` restores `this.value` and calls `setFormValue()` but does **not** call `updateFormValidity()`. If the group is required and state is restored to `''`, the component will appear valid when it should not. `formResetCallback` correctly calls `updateFormValidity()` (line 155); `formStateRestoreCallback` must match.
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

### 1. Indexed Access Types on `@Prop()` — `bds-radio-card.tsx` (all props) 🔴

**Source:** `.claude/memory/stencil-prop-patterns.md` — "Never Use Indexed Access Types on @Prop() Declarations"

Every `@Prop()` in `bds-radio-card.tsx` uses the `IRadioCard['propName']` indexed access syntax:

```tsx
@Prop({ reflect: true }) readonly value: IRadioCard['value'] = 'on';
@Prop() readonly info: IRadioCard['info'] = '';
@Prop() readonly name: IRadioCard['name'] = '';
// ... all 7 props
```

This is a systematic violation. TypeScript's indexed access types degrade to an `error` type in the Stencil decorator transform context (which evaluates prop types before the full type-checker is available), causing `@typescript-eslint/no-unsafe-assignment` errors on every read of the prop.

**Fix:** Replace every `IRadioCard['propName']` with the concrete primitive type:

```tsx
@Prop({ reflect: true }) readonly value: string = 'on';
@Prop() readonly info: string = '';
@Prop() readonly name: string = '';
@Prop() readonly label: string = '';
@Prop({ mutable: true, reflect: true }) readonly checked: boolean = false;
@Prop({ reflect: true }) readonly disabled: boolean = false;
@Prop({ reflect: true }) readonly error: boolean = false;
```

The `implements IRadioCard` clause on the class still enforces the structural contract — the interface is the contract, the prop declaration is the implementation.

---

### 2. `checked` prop missing `readonly` on leaf components 🔴

**Source:** `.claude/memory/stencil-prop-patterns.md` — "`readonly` and `mutable: true` are orthogonal"

- `bds-radio-card.tsx:48`: `@Prop({ mutable: true, reflect: true }) checked` — missing `readonly`
- `bds-radio.tsx:21`: `@Prop({ mutable: true, reflect: true }) checked` — missing `readonly`

`mutable: true` allows the component to write the prop internally (and the parent to write it via direct property assignment). `readonly` prevents external consumers from assigning it declaratively in templates after initialization. Both must be present. The `stencil/props-must-be-readonly` ESLint rule will flag these.

**Fix:** Add `readonly` to both declarations:
```tsx
@Prop({ mutable: true, reflect: true }) readonly checked: boolean = false;
```

---

### 3. `formStateRestoreCallback` missing `updateFormValidity()` — `bds-radio-group.tsx:159` 🔴

**Source:** `.claude/memory/stencil-face-constraint-validation-pattern.md`

```tsx
formStateRestoreCallback(state: unknown, _mode: string): void {
  const val = typeof state === 'string' ? state : '';
  this.value = val;
  this.internals.setFormValue(val !== '' ? val : null);
  // ❌ Missing: updateFormValidity()
}
```

`formResetCallback` correctly calls `this.updateFormValidity()` after resetting state (line 155), but `formStateRestoreCallback` does not. If the group is `required` and session state is restored to an empty string, `ElementInternals` validity remains from the previous interaction — the component will appear valid when it is not (or invalid when it is). The browser restores form state during back-navigation and autofill; leaving validity stale here is a silent regression.

**Fix:**
```tsx
formStateRestoreCallback(state: unknown, _mode: string): void {
  const val = typeof state === 'string' ? state : '';
  this.value = val;
  this.internals.setFormValue(val !== '' ? val : null);
  this.updateFormValidity(); // ← add this
}
```

---

### 4. `@Event()` explicit `bubbles`/`composed` options — `bds-radio-card.tsx:63` and `bds-radio.tsx:42` 🟡

**Source:** `.claude/memory/feedback_event_options_explicit.md` — "Bare `@Event()` with no options is the accepted convention. See ADR 0003."

- `bds-radio-card.tsx:63`: `@Event({ bubbles: true, composed: true }) bdsChange` — has both options
- `bds-radio.tsx:42`: `@Event({ bubbles: true }) bdsChange` — has one option

The project convention (ADR 0003) mandates bare `@Event()`. However, `bds-radio-group` uses `@Listen('bdsChange')` which requires the event to bubble from child to parent host in light DOM. Stencil's default for `bubbles` is `false`, meaning without `bubbles: true` the `@Listen` in the group would silently not fire.

The `composed: true` on `bds-radio-card` is unnecessary (Boreal uses light DOM only — no shadow boundaries). The `bubbles: true` on both components appears to be a functional requirement for the `@Listen` pattern to work.

**Recommendation:** Confirm ADR 0003 scope — if it covers events that drive cross-component communication via `@Listen`, document the exception. Otherwise remove `composed: true` from `bds-radio-card` at minimum and verify the listener still fires.

---

### 5. `value` prop `mutable: true` on FACE component — `bds-radio-group.tsx:80` 🟡

**Source:** `.claude/memory/stencil-prop-patterns.md`

`bds-radio-group` is a `formAssociated: true` component. Its `value` prop:

```tsx
@Prop({ mutable: true }) value: string = '';
```

The component writes `this.value = event.detail.value` in `handleRadioChange` and `navigateTo`. On a FACE component the `@State()` mirror pattern is preferred because:
1. `mutable: true` on a reflected prop creates a race with the browser's form restore lifecycle.
2. It also means the prop is not `readonly`, violating `stencil/props-must-be-readonly`.

The correct pattern (consistent with `bds-radio-group`'s own `isDisabled` mirror):
```tsx
@Prop({ reflect: true }) readonly value: string = '';
@State() private internalValue: string = '';

@Watch('value')
onValueChangeProp(val: string) { this.internalValue = val; }

componentWillLoad() { this.internalValue = this.value; }
```
All internal writes then target `this.internalValue`. External consumers and `v-model` continue to bind to `value` via the prop.

---

### 6. `valueChange` event naming — false positive ✅

**Source:** `.claude/memory/stencil-form-control-interfaces.md`

The script flagged `valueChange` at `bds-radio-group.tsx:112` as violating the `bds{Action}` format. This is a **false positive**. `valueChange` is the reserved name enforced by `IFormValueEmitter<T>` in `form-associated.mixin.ts` for Vue `v-model` support. It is already registered in `componentModels` in `vue-output-target.ts`. No change needed.

---

### 7. Group label and helper text rendering — `bds-radio-group.tsx` ✅

**Source:** `.claude/memory/component-bds-typography-group-labels.md`

`bds-radio-group` correctly uses `<bds-typography variant="label">` for the group label (with `required` and `tooltipText` props) and `<bds-typography variant="helper" state={typographyState}>` for helper/error text. The `_id`-based `aria-labelledby`/`aria-describedby` wiring is also correct. No issues.

---

### 8. `mouseleave` handler check — not applicable ✅

Neither `bds-radio-card` nor `bds-radio-group` implement `mouseleave`/stayOnHover logic. No issues.

---

### Memory topic files consulted

| File | Applied to |
|------|-----------|
| `stencil-prop-patterns.md` | indexed access types, mutable/readonly, FACE disabled mirror |
| `stencil-face-constraint-validation-pattern.md` | `formStateRestoreCallback` validity re-sync |
| `stencil-form-control-interfaces.md` | `valueChange` false positive, `IFormControl<T>` |
| `feedback_event_naming.md` | event name convention |
| `feedback_event_options_explicit.md` | bare `@Event()` convention |
| `component-bds-typography-group-labels.md` | group label/helper rendering |
| `project_no_shadow_dom.md` | `composed: true` relevance |
| `mouseleave-relatedtarget-vs-target.md` | not applicable |

---

**Result: 21 passed · 6 failed** _(3 additional failures found in memory-guided pass; 1 automated false positive resolved)_

_Generated by [review_report_generator.py](.claude/skills/code-reviewer/scripts/review_report_generator.py)_