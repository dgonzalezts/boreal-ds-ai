# Boreal DS — Code Review Report

**Generated:** 2026-04-28T15:43:33
**Base ref:** `release/current`
**Repository:** `.`

## Affected Packages

- **boreal-docs (Storybook)** — checklist section(s): D
- **boreal-web-components (Stencil)** — checklist section(s): A

## Automated Findings

- 🟡 **[prop-mutable-form-attr]** Native form attribute prop should not use `mutable: true`. Use a `@State() private is<Prop>` mirror instead and write to it in `formDisabledCallback` / `@Watch`. See coding_standards.md. `packages/boreal-web-components/src/components/actions/bds-toggle/bds-toggle.tsx:78`
  - **Standard (coding_standards.md):** The `@State()` mirror pattern is required for any prop whose value can be written by a browser FACE lifecycle callback. Although this flag fires on `checked` (not `disabled`), the same architectural concern applies — the component writes `this.checked` directly in `toggle()`, `formResetCallback`, and `formStateRestoreCallback`. A `@State() private isChecked` mirror would decouple the external prop contract from the internal write path, eliminating the `mutable: true` entirely.
  - **Antipattern (common_antipatterns.md):** `mutable: true` on `disabled` creates two writers on the same reflected attribute — the component and the browser. While `checked` has no browser-side writer, the same principle of "one authoritative internal state" applies.
- 🔴 **[event-name-format]** @Event() name 'valueChange' does not follow the `bds{Action}` format. Custom events must start with `bds` followed by an uppercase letter (e.g. `bdsClose`, `bdsChange`). `packages/boreal-web-components/src/components/actions/bds-toggle/bds-toggle.tsx:103`
  - ⚠️ **FALSE POSITIVE** — `valueChange` is the documented exception to the `bds{Action}` naming rule. It is part of the `IFormValueEmitter<T>` interface declared in `form-associated.mixin.ts` and is the contract name consumed by `@stencil/vue-output-target`'s `componentModels` config to generate `v-model` support. See memory: `feedback_event_naming.md` and `stencil-form-control-interfaces.md`. **No change required here.**
- 🟡 **[face-reset-no-validity]** `formResetCallback` is defined but `updateValidity()` or `setValidity()` is not called — validity state may be stale after reset. `packages/boreal-web-components/src/components/actions/bds-toggle/bds-toggle.tsx`
  - **Standard (coding_standards.md):** `formResetCallback` and `formStateRestoreCallback` must call `updateValidity()` after restoring state. This also applies to `formStateRestoreCallback`, which is also missing the call in this component.
  - **Antipattern (common_antipatterns.md):** "Skipping `updateValidity()` after reset/restore: Leaves validity state reflecting the pre-reset value." Even for a component with no custom validators, the call ensures the validity state is deterministically cleared on form reset rather than depending on the prior run.
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/components/actions/bds-toggle/types/index.ts:1`
  - **Standard (coding_standards.md):** Prefer named re-exports (`export { X } from './X'`) over wildcard re-exports (`export * from './X'`). Applies to all 4 lines in `types/index.ts`.
  - **Antipattern (common_antipatterns.md):** "Wildcard re-exports in barrels: `export * from './X'` hides module edges from the bundler and can prevent tree-shaking."
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/components/actions/bds-toggle/types/index.ts:2`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/components/actions/bds-toggle/types/index.ts:3`
- 🟡 **[barrel-wildcard-export]** `export * from '...'` hides module edges from the bundler and can prevent tree-shaking. Use named re-exports: `export { X } from './X'`. `packages/boreal-web-components/src/components/actions/bds-toggle/types/index.ts:4`
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/helpers/bds-divider.tsx:3`
  - Out-of-scope for this review (different file). Track separately.
- 🟡 **[import-order]** Import order violation: framework imports must come first, then internal aliases (@/services → @/mixins → @/utils), then local/relative imports. `packages/boreal-web-components/src/components/helpers/bds-divider.tsx:6`
  - Out-of-scope for this review (different file). Track separately.
- 🟡 **[barrel-wildcard-export]** × 6 in `packages/boreal-web-components/src/types/index.ts` — Out-of-scope for this review (pre-existing). Track separately.
- 🔵 **[missing-changeset]** No changeset or CHANGELOG entry detected for package-level changes.
  - A changeset must be added before this PR can be released. Run `pnpm commit` with a `feat` type commit or manually add a changeset file under `.changeset/`.

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

- ✅ Every @Prop() has `readonly` and an adjacent JSDoc block
- ❌ Native form attrs (`disabled`, `checked`, `value`) use `@State()` mirror, not `mutable: true`
- ✅ `validatePropValue` + `componentWillLoad()` + `@Watch()` for enum-like props
- ❌ Custom events use the `bds{Action}` prefix pattern (e.g. `bdsClose`, not `bdsBannerClose`)
- ✅ Event names do not reuse native DOM events
- ✅ @AttachInternals() is on the class body, not in a mixin
- ✅ `checkValidity()` and `reportValidity()` exposed via @Method()
- ✅ Only ElementInternals.setValidity() manages validity
- ❌ `formResetCallback` and `formStateRestoreCallback` call updateValidity()
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
- ✅ Storybook aliasing intact for @telesign/boreal-web-components/css/\*
- ✅ Uses `dotenv --` and `--storybook-build-dir`

## Memory-Guided Review

### 1. FACE `disabled` pattern (`stencil-prop-patterns.md`)

✅ **No issues found.** The component correctly implements the `@State()` mirror pattern for `disabled`:

- `@Prop({ reflect: true }) readonly disabled` — externally owned, `readonly`
- `@State() private isDisabled: boolean = false` — internal working copy
- `@Watch('disabled') onDisabledChange(next)` — syncs on external prop changes
- `formDisabledCallback(disabled)` — syncs when a parent `<fieldset>` is toggled
- All render and guard logic reads `this.isDisabled` — no race possible

### 2. `valueChange` event naming (`feedback_event_naming.md`, `stencil-form-control-interfaces.md`)

⚠️ **Scanner false positive — `valueChange` is intentional.** The `[event-name-format]` error for `valueChange` should be suppressed or annotated in the scanner config.

The `valueChange: EventEmitter<boolean>` declaration satisfies the `IFormValueEmitter<T>` interface from `form-associated.mixin.ts`. This name is the contract consumed by `@stencil/vue-output-target`'s `componentModels` to generate `v-model` support. It must remain `valueChange` — renaming it to `bdsChange` would silently break Vue v-model.

`bdsChange` is correctly named and serves a different role (carries the full `IToggleEventChange` payload for consumer logic).

### 3. `componentModels` registration for Vue v-model (`stencil-form-control-interfaces.md`)

🔴 **MISSING — `bds-toggle` is not registered in `componentModels`.** Inspecting `packages/boreal-web-components/targets/vue-output-target.ts`, only `bds-text-field` is listed:

```ts
componentModels: [
  {
    elements: ['bds-text-field'],
    event: 'valueChange',
    targetAttr: 'value',
  },
],
```

`bds-toggle` must be added **in this same PR**. Without it, Vue consumers cannot use `v-model` on the component — the output target does not auto-derive bindings from event names. The entry should be:

```ts
{
  elements: ['bds-toggle'],
  event: 'valueChange',
  targetAttr: 'checked',
}
```

Note `targetAttr: 'checked'` (not `'value'`) — the mirrored prop that holds the current state is `checked`.

### 4. `formResetCallback` / `formStateRestoreCallback` validity (`stencil-face-constraint-validation-pattern.md`)

❌ **Both callbacks are missing `updateValidity()` / `setValidity()` calls.** Confirmed by the automated scanner. Even for a component without custom validators, skipping the call leaves validity state in whatever condition it was in before the reset — which could show stale error state to the user after a form reset.

Minimum fix:

```ts
formResetCallback(): void {
  this.checked = false;
  setFormValue(this.internals, null);
  this.internals.setValidity({});   // clear any prior invalid state
}

formStateRestoreCallback(state: unknown, _mode: string): void {
  this.checked = state === this.value;
  this.syncFormValue();
  this.internals.setValidity({});   // re-sync validity after restore
}
```

If the toggle gains `required` validation in the future, replace `setValidity({})` with a proper `updateValidity()` call.

### 5. `@AttachInternals()` placement (`stencil-face-attach-internals.md`)

✅ **No issues found.** `@AttachInternals() internals!: ElementInternals` is declared on the `BdsToggle` class body, not inside the mixin factory.

### 6. `IFormControl<T>` composite interface (`stencil-form-control-interfaces.md`)

✅ **No issues found.** The class implements `IFormControl<boolean>`, which is the correct composite interface (`IFormAssociatedCallbacks & IFormValueEmitter<boolean>`). The `valueChange!: EventEmitter<boolean>` declaration satisfies `IFormValueEmitter<boolean>`.

### 7. Light DOM / no Shadow DOM (`project_no_shadow_dom.md`)

✅ **No issues found.** No `shadow: true` or `scoped: true` in the `@Component` decorator. The SCSS uses direct tag selectors (`bds-toggle { ... }`, `bds-toggle[disabled] { ... }`). No `::part()` or `composed` event flags.

### 8. Bare `@Event()` options convention (`feedback_event_options_explicit.md`)

✅ **No issues found.** Both `@Event() valueChange` and `@Event() bdsChange` use bare `@Event()` with no explicit `bubbles`, `composed`, or `cancelable`. Aligns with ADR 0003.

### 9. `checked` prop with `mutable: true` (`stencil-prop-patterns.md`)

🟡 **Architectural concern — low priority.** The `checked` prop is declared with `mutable: true` and no `readonly`, allowing the component to write `this.checked` directly in `toggle()`, `formResetCallback`, and `formStateRestoreCallback`. This works at runtime, but it mixes the prop (external contract) with internal state, which makes the data-flow harder to follow and prevents consumers from reliably binding to a stable read-only signal.

The pattern aligned with Boreal DS conventions would be:

```ts
@Prop({ reflect: true }) readonly checked: boolean = false;
@State() private isChecked: boolean = false;

@Watch('checked')
onCheckedChange(next: boolean) {
  this.isChecked = next;
  this.syncFormValue();
}

componentWillLoad() {
  this.isChecked = this.checked;
  ...
}
```

And all writes go to `this.isChecked` (toggle, reset, restore). This is a refactor suggestion — not a blocker for this PR if the current approach is intentional and the ESLint rule is not firing.

---

### Memory topic files consulted

- `stencil-prop-patterns.md` — `mutable: true` on form attrs, `@State()` mirror pattern
- `feedback_event_naming.md` — `bds{Action}` format, `valueChange` exception
- `stencil-form-control-interfaces.md` — `IFormControl<T>`, `componentModels`, `valueChange` contract
- `stencil-face-constraint-validation-pattern.md` — `formResetCallback` + `updateValidity()`
- `stencil-face-attach-internals.md` — `@AttachInternals()` placement rule
- `project_no_shadow_dom.md` — light DOM verification
- `feedback_event_options_explicit.md` — bare `@Event()` convention

---

**Result: 23 passed · 4 failed**

_Generated by [review_report_generator.py](.claude/skills/code-reviewer/scripts/review_report_generator.py)_
