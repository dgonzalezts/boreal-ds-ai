# Stencil Best Practices

## Style Encapsulation: `scoped` vs `shadow` vs none

Stencil provides three style encapsulation modes. Choose the right one based on the component's requirements.

### How `scoped: true` works

`scoped: true` implements **synthetic CSS scoping** at compile time — no native Shadow DOM is used:

1. Stencil generates a unique hash for the component (e.g. `sc-bds-text-field`).
2. It appends a scoped class to every DOM node the component renders.
3. It rewrites every CSS selector to include that class, making styles target only nodes belonging to that component.

The compiled output at runtime looks like:

```html
<bds-text-field class="sc-bds-text-field-h">
  <input class="bds-text-field__control sc-bds-text-field" />
</bds-text-field>
```

```css
/* compiled CSS */
.bds-text-field__control.sc-bds-text-field { ... }
```

---

### The three encapsulation modes compared

|                                     | `shadow: true`                              | `scoped: true`                                 | neither                    |
| ----------------------------------- | ------------------------------------------- | ---------------------------------------------- | -------------------------- |
| **Mechanism**                       | Native browser Shadow DOM                   | Compile-time attribute scoping                 | None                       |
| **DOM type**                        | Shadow root (isolated)                      | Light DOM                                      | Light DOM                  |
| **Style leakage in**                | Blocked (CSS custom props still cross)      | Not fully blocked — specificity wins           | Unrestricted               |
| **Style leakage out**               | Blocked                                     | Blocked (scoped selectors don't match outside) | Unrestricted               |
| **`querySelector` from parent**     | Requires `el.shadowRoot.querySelector(...)` | `el.querySelector(...)` ✅                     | `el.querySelector(...)` ✅ |
| **`:host` selector**                | Works natively                              | Compiled to tag attribute selector             | N/A                        |
| **`::slotted()`**                   | Supported                                   | Not supported                                  | N/A                        |
| **`::part()`**                      | Supported                                   | Not supported                                  | N/A                        |
| **CSS custom props cross boundary** | Yes                                         | Yes                                            | Yes                        |

---

### When to use `scoped: true`

Use `scoped: true` when:

- You need to avoid Shadow DOM compatibility edge cases with browser form validation UI (native validation bubbles, autofill, password managers).
- The component must remain accessible to the document's accessibility tree without an encapsulation boundary.
- BEM class naming provides sufficient practical style isolation for your use case.

> **Boreal DS current practice:** No component uses `scoped: true`. All components use bare light DOM (no encapsulation option). This is a deliberate decision — see "Current project choice" below.

### When to use `shadow: true`

Use `shadow: true` when:

- Full style isolation is required — external stylesheets must not be able to reach internal elements.
- You need `::part()` or `::slotted()` for consumer customisation.
- The component renders complex subtrees where specificity conflicts with host page styles are likely.

### When to use neither (current project choice)

**Boreal DS uses no encapsulation for all components**, including FACE components. This is an intentional architectural decision:

- Global CSS and design token stylesheets apply directly to component internals — no `::part()` or CSS custom property tunnelling needed.
- The `:host` pseudo-class has no effect without a shadow boundary (per MDN). Use the component tag name directly as the root SCSS selector — see [Light DOM: direct tag selectors](#light-dom-direct-tag-selectors-not-host) below.
- `composed: true` on `@Event()` is irrelevant — there is no shadow boundary to cross. Bare `@Event()` is correct.
- Focus delegation in FACE components works via `el.querySelector('input')` directly, without any encapsulation workaround.
- If shadow DOM is ever introduced, ADR 0003 must be revisited.

---

### The key trade-off with `scoped: true`

Scoped CSS only prevents your styles from leaking **out**. External styles with sufficient specificity **can still override** component internals:

```css
/* This WILL affect a scoped component's input */
/* It would NOT with shadow: true */
input {
  background: red;
}
```

**Mitigation**: Always use specific BEM class selectors (e.g. `.bds-text-field__control`) in component SCSS. The extra specificity provides practical protection even without full Shadow DOM isolation.

---

### SSR behaviour

When Stencil serialises a scoped component server-side, it renders a light-DOM tree with a single `<style>` tag injected into `<head>`. Every selector carries the scoped attribute suffix. On hydration, no Shadow DOM attachment is needed — the client diffs against the existing light DOM directly.

---

### CSS custom properties always cross boundaries

Regardless of encapsulation mode, CSS custom properties (`var(--boreal-*)`) cross any Shadow DOM or scoped boundary. The Boreal theming system (set via `data-theme` on `<html>`) works identically with `scoped: true` and `shadow: true`.

---

## Light DOM: direct tag selectors, not `:host`

**In Boreal DS light DOM components, `:host` does not work.** From MDN: _"`:host` has no effect when used outside a shadow DOM."_ Without a shadow root, the pseudo-class matches nothing.

Use the component tag name directly as the root SCSS selector:

```scss
// ✅ Correct for light DOM
bds-button {
  display: inline-flex;
}
bds-button[disabled] {
  cursor: not-allowed;
  opacity: 0.6;
}
bds-checkbox:focus-visible .bds-checkbox__box {
  outline: 2px solid $boreal-stroke-focus;
}
bds-grid-item[col-span="full"] {
  grid-column: 1 / -1;
}

// ❌ Wrong — :host has no effect here, even if Stencil compiles it away
:host {
  display: inline-flex;
}
:host([disabled]) {
  cursor: not-allowed;
}
```

While Stencil technically compiles `:host` to the tag selector in light DOM components, the browser does not recognise `:host` as functional without a shadow boundary. Use direct tag selectors to make intent explicit and avoid relying on a compilation side-effect.

### Every selector must nest inside the root tag block — no top-level siblings

Stencil compiles a component's SCSS straight into that component's global stylesheet. There is no shadow boundary to contain a selector that sits *outside* the root tag block — it becomes a page-wide rule, matching that element anywhere in the document, in any other component's markup, the instant the stylesheet loads:

```scss
// ❌ Wrong — table/thead/th sit outside bds-table { }, so they match ANY
// <table>/<thead>/<th> on the page, including another component's
bds-table {
  display: flex;
}

table {
  width: 100%;
  table-layout: fixed;
}

thead th {
  padding-inline: $boreal-spatial-padding-m;
}
```

```scss
// ✅ Correct — nested under the root tag block, compiles to
// `bds-table table`, `bds-table thead th`, etc. — scoped descendant selectors
bds-table {
  display: flex;

  table {
    width: 100%;
    table-layout: fixed;
  }

  thead th {
    padding-inline: $boreal-spatial-padding-m;
  }
}
```

This is not a hypothetical: `bds-table.scss` and `bds-calendar-grid.scss` both shipped with exactly this mistake — top-level `table`/`thead`/`th` rules outside their host block — and once both components' stylesheets loaded on the same page (e.g. navigating between their Storybook docs pages in one session), each leaked its header-cell padding/width/alignment onto the other's table, corrupting `bds-calendar-grid`'s weekday header row. See `.agents/memory/stencil-light-dom-unscoped-selector-leak.md` for the full incident.

**Before finishing any component SCSS edit, verify every selector in the file is nested inside the root tag block** — a bare selector at the top level of the file (not indented under the component tag) is a scoping bug regardless of how correct its declarations are.

---

## Global SCSS Utilities (`_commons.scss` and `_interactions.scss`)

Two SCSS partial files in `packages/boreal-web-components/src/styles/` are injected globally into every component stylesheet via `injectGlobalPaths` in `stencil.config.ts`. No `@use` or `@import` is needed in component SCSS files — their contents are available everywhere.

### `_commons.scss` — layout placeholders

Defines `%flex-center` (`display: flex; align-items: center`). Use `@extend %flex-center` instead of repeating the two declarations inline.

```scss
// ✅ Correct
.bds-radio__content {
  @extend %flex-center;
  gap: $boreal-spacing-3xs;
}

// ❌ Avoid
.bds-radio__content {
  display: flex;
  align-items: center;
  gap: $boreal-spacing-3xs;
}
```

### `_interactions.scss` — interaction mixins and functions

Provides consistent interaction feedback across all components. Always prefer these over raw `box-shadow` or `transition` declarations:

| Symbol                                            | Type     | Use for                                                         |
| ------------------------------------------------- | -------- | --------------------------------------------------------------- |
| `bds-focus-ring($outer, $inner)`                  | mixin    | Keyboard focus ring (`box-shadow`)                              |
| `bds-focus-ring-value($outer, $inner)`            | function | Focus ring value when composing with other shadows              |
| `bds-hover-shadow($color)`                        | mixin    | Elevation shadow on hover                                       |
| `bds-shadow-inset($color)`                        | function | Inset shadow value for active/pressed states                    |
| `bds-active-shadow-inset($outer, $inner, $inset)` | mixin    | Combined focus ring + inset shadow for active/pressed           |
| `bds-transition-surface`                          | mixin    | Transition for `background-color`, `border-color`, `box-shadow` |
| `bds-transition-visibility`                       | mixin    | Transition for `opacity`                                        |
| `bds-transition-action`                           | mixin    | Transition for `color` and `opacity`                            |
| `bds-icon($size, $font-size)`                     | mixin    | Consistent sizing for `<em>` icon elements                      |

```scss
// ✅ Correct — use the shared mixins
.bds-radio__button {
  @include bds-transition-surface;
}

bds-radio:focus-visible .bds-radio__button {
  @include bds-focus-ring($boreal-stroke-focus, $boreal-ui-inverse);
}

bds-radio:hover:not(.--disabled) .bds-radio__button {
  @include bds-hover-shadow(rgba(19, 19, 22, 0.15));
}

// ❌ Avoid — raw declarations that duplicate shared logic
.bds-radio__button {
  transition:
    background-color 0.3s ease,
    border-color 0.3s ease,
    box-shadow 0.3s ease;
}
```

### Hover block consolidation

When hover applies to multiple child elements, nest them under a single `&:hover` parent rather than repeating the full selector chain:

```scss
// ✅ Correct — one selector block, multiple children
&:hover:not(.--disabled):not(.--checked) {
  .bds-radio__button { @include bds-hover-shadow(rgba(19, 19, 22, 0.15)); }
  .bds-radio__dot    { background-color: $boreal-ui-base-light; }
}

// ❌ Avoid — repeated selector
&:hover:not(.--disabled):not(.--checked) .bds-radio__button { ... }
&:hover:not(.--disabled):not(.--checked) .bds-radio__dot    { ... }
```

### SCSS `@use` constraints

`injectGlobalPaths` in `stencil.config.ts` prepends three files at the top of **every** component SCSS at build time: the `$boreal-*` token index, `_commons.scss`, and `_interactions.scss`. Three rules follow from this:

**Rule 1 — Component SCSS files must NOT `@use` the token package.** Tokens are already injected globally; adding a `@use` of the token package in a component file causes a Sass double-import / variable redefinition error. All component SCSS files start directly with selectors — no `@use` at the top.

**Rule 2 — SCSS partials `@use`d by components MUST `@use` the token package themselves.** Sass's module system gives each file its own isolated scope. `injectGlobalPaths` prepends token definitions into the component file only — it does not flow into any partials accessed via `@use`. Partials must declare their own imports:

```scss
// _selectable-button.scss (shared partial) — CORRECT
@use "@telesign/boreal-style-guidelines/dist/stencil/_index" as *;
@use "../../../styles/_interactions" as *;
```

```scss
// bds-radio-button.scss (component) — CORRECT, no @use of token package
@use "../../_shared/selectable-button" as *;
@include selectable-button("bds-radio-button");
```

**Rule 3 — Injected files must be self-contained.** Stencil compiles each injected file standalone during watch cycles. Any `$boreal-*` reference inside an injected partial will fail with "Undefined variable" unless the token file is also loaded by that partial via `@use '@telesign/boreal-style-guidelines/dist/stencil/_index' as *;`. Sass `@use` is idempotent — no double-definition errors.

---

## `@Prop()` Type Declaration and Default Value Rules

When a prop has a default value, TypeScript infers its type — no explicit annotation is needed:

```typescript
@Prop({ reflect: true }) readonly disabled = false;         // inferred boolean
@Prop({ reflect: true }) readonly orientation = 'vertical'; // inferred string
```

**Always use string literals as default values — never constant or enum references.**
Stencil resolves `@Prop()` defaults at static analysis time (AST level). If you write `= ORIENTATIONS.VERTICAL`, the compiler records the identifier `ORIENTATIONS.VERTICAL` in `custom-elements.json` instead of the actual value `'vertical'`. This leaks internal implementation details into the CEM, Storybook ArgTypes, and consumer IDEs.

```typescript
// ✅ Correct — CEM records 'vertical'
@Prop() readonly orientation: Orientation = 'vertical';

// ❌ Wrong — CEM records 'ORIENTATIONS.VERTICAL'
@Prop() readonly orientation: Orientation = ORIENTATIONS.VERTICAL;
```

Constants may still be used inside logic (switch cases, `validatePropValue`, class maps) — just never as the `@Prop()` initializer.

When there is no default, the type cannot be inferred and must be declared explicitly:

```typescript
@Prop({ reflect: true }) readonly name!: string;   // required, no default
@Prop({ reflect: true }) readonly formId?: string; // optional, no default
```

### When to use a default value

- The prop has a sensible "off" state that works without user input: `disabled = false`, `required = false`.
- There is always a valid fallback and the prop is purely behavioral.

### When NOT to use a default value

- **Identity data** — `name` and `value` on a leaf element are required (`!`). A default of `''` would silently submit invalid form data while passing HTML validation.
- **Optional context** — props like `formId?: string` and `required?: boolean` are optional because their _absence_ has meaning (no form association, not required). Defaulting them to `''` or `false` changes DOM attribute presence semantics.

### Rule of thumb

| Declaration        | Meaning                                                            |
| ------------------ | ------------------------------------------------------------------ |
| `name!: string`    | Required, no default — component cannot function without it        |
| `formId?: string`  | Optional, no default — `undefined` is a valid and meaningful value |
| `disabled = false` | Has default — behavioral, always a valid fallback                  |

> **Stencil + React/Vue wrappers**: for boolean props with `reflect: true`, Stencil strips the DOM attribute when the value is `false` — so `false` and `undefined` produce identical DOM output. The `required={false}` vs `required={undefined}` distinction that matters in plain HTML does not apply here.

---

## Prop and Event Naming Conventions

### Boolean prop naming

Boolean `@Prop()` declarations must use single descriptive adjectives — the same style as native HTML boolean attributes (`disabled`, `required`, `controls`, `muted`, `open`). Never prefix a boolean prop with `is`, `has`, or `show`.

| ❌ Avoid        | ✅ Use instead | Rationale                                               |
| --------------- | -------------- | ------------------------------------------------------- |
| `hasHeader`     | `header`       | `has` prefix — mirrors native HTML                      |
| `hasFooter`     | `footer`       | `has` prefix                                            |
| `showClose`     | `closable`     | `show` prefix                                           |
| `hasClear`      | `clearable`    | `has` prefix                                            |
| `showCharCount` | `counter`      | `show` prefix                                           |
| `isError`       | `error`        | `is` prefix                                             |
| `isDisabled`    | `disabled`     | `is` prefix — internal `@State()` may keep `isDisabled` |

This rule applies exclusively to public `@Prop()` declarations. Internal `@State()` names are not covered — `isVisible`, `isDisabled`, `isOpen` are valid for private reactive state.

### Custom event naming

All `@Event()` names must follow the pattern `bds{Action}` — camelCase, `bds` prefix, action verb only. Do not include the component noun between the prefix and the action.

```ts
// ✅ Correct
bdsClose;
bdsChange;
bdsInput;
bdsClick;

// ❌ Wrong — component noun in the name
bdsBannerClose;
bdsBannerChange;
bdsTextFieldInput;
```

The single exception is `valueChange`, which must remain as-is — it is the framework integration contract consumed by the Vue output target for `v-model` two-way binding.

**Never use a native DOM event name** (`click`, `change`, `input`, `focus`, etc.) as an `@Event()` name. Three distinct failures result:

1. **Type-contract violation** — consumers who write `element.addEventListener('click', handler)` expect a `MouseEvent`. A custom event named `click` delivers a `CustomEvent`, breaking any code that reads `MouseEvent`-specific properties (`clientX`, `button`, etc.).
2. **Duplicate dispatch** — the browser fires the native event AND Stencil fires the custom event. The listener receives two calls instead of one.
3. **Framework binding collision** — Vue and React bind their synthetic event system to native event names. An `@Event('change')` creates an ambiguous binding that conflicts with the framework's own `onChange`/`@change` wiring.

---

## FACE Components: `formAssociated: true`

All form-associated components use bare light DOM — no `shadow` or `scoped` option. The canonical pattern is:

```tsx
@Component({
  tag: 'bds-[name]',
  styleUrl: 'bds-[name].scss',
  formAssociated: true,
})
export class Bds[Name] extends Mixin(formAssociatedMixin) implements IFormControl<string> {
  @AttachInternals() internals!: ElementInternals;
  // ...
}
```

Key rules:

**`@AttachInternals()` placement — class body only, never inside a mixin factory.**
Stencil's compiler performs static analysis on the component class. Decorators inside factory functions are not visible to this analysis for `@AttachInternals()`. The result is `this.internals === undefined` at runtime — every FACE lifecycle callback that calls `this.internals.setFormValue()` or `this.internals.setValidity()` throws a `TypeError`. Other decorators (`@Prop()`, `@State()`, `@Watch()`, `@Method()`) do work inside mixin factories; `@AttachInternals()` is the single exception.

```typescript
// ✅ Correct — @AttachInternals() on the class body
@Component({ tag: "bds-my-field", formAssociated: true })
export class BdsMyField extends Mixin(formAssociatedMixin) {
  @AttachInternals() internals!: ElementInternals;
}

// ❌ Wrong — inside the mixin factory; internals === undefined at runtime
export const formAssociatedMixin = () =>
  class {
    @AttachInternals() internals!: ElementInternals; // not visible to static analysis
  };
```

**Native FACE prototype members are blocked by Stencil's element proxy — use `@Method()` wrappers.**
The browser's FACE spec adds `checkValidity()`, `reportValidity()`, and `validity` to the element's prototype. Stencil's proxy only forwards members declared with `@Prop()`, `@State()`, or `@Method()`. Accessing `bdsTextField.checkValidity()` from outside the component returns `undefined` without a wrapper:

```typescript
@Method()
async checkValidity(): Promise<boolean> {
  return this.internals.checkValidity();
}

@Method()
async reportValidity(): Promise<boolean> {
  return this.internals.reportValidity();
}
```

All FACE validation checks from outside the component (test harnesses, integration tests) must go through these `@Method()` wrappers.

**Constraint validation — avoid doubled validation events.**
If both `ElementInternals.setValidity()` and a native `<input required>` attribute handle validation simultaneously, the browser fires two validation events. The inner `<input>` without FACE focus handling causes an "invalid form control is not focusable" error on submit.

Required pattern:

1. Remove `required={this.required}` from the native `<input>` inside the component.
2. Handle all constraint validation exclusively via `ElementInternals.setValidity()`.
3. Add `tabIndex={this.disabled ? -1 : 0}` on `<Host>` so the browser can focus the custom element when validation fails.
4. Add `onFocus={() => this.el.querySelector<HTMLInputElement>('input')?.focus()}` on `<Host>` to delegate focus to the inner input.
5. Both `formResetCallback` and `formStateRestoreCallback` must call `updateValidity()` after restoring the value — failing to do so leaves validity reflecting the pre-reset state.

**Async rendering — `formDisabledCallback` trigger conditions.**

- `HTMLFormElement` has no native `disabled` property. Setting `form.disabled = true` does nothing.
- `formDisabledCallback` is only triggered by a `<fieldset disabled>` ancestor being toggled.
- In unit tests: set `component.disabled` directly. In integration tests: toggle a `<fieldset disabled>` ancestor.
- `HTMLButtonElement.prototype.checkValidity` shadows any global function named `checkValidity` when called from an HTML `onclick` attribute. Rename manual test harness functions to avoid collision (e.g. `testValidity` instead of `checkValidity`).

- Use `el.querySelector(...)` for all inner element access — no `shadowRoot` exists.

---

## Component Class Member Ordering

All component classes must follow this 15-section member ordering. Consistent ordering improves readability, code review efficiency, and navigation.

### The 15-section standard

| Order | Section                          | Description                                              | Examples                                                               |
| ----- | -------------------------------- | -------------------------------------------------------- | ---------------------------------------------------------------------- |
| 1     | **Static members**               | Static properties and methods                            | `static tagName = 'bds-button'`                                        |
| 2     | **Private non-reactive members** | Private class properties that don't trigger re-renders   | `private helperInstance: Helper`                                       |
| 3     | **Element reference**            | Reference to the component's host element                | `@Element() el!: HTMLElement`                                          |
| 4     | **Internal reactive state**      | Private reactive properties                              | `@State() private isOpen = false`                                      |
| 5     | **Public reactive properties**   | Public props that trigger re-renders when changed        | `@Prop() disabled = false`                                             |
| 6     | **Property watchers**            | Handlers that run when specific properties change        | `@Watch('disabled')`, `@Watch('value')`                                |
| 7     | **Event declarations**           | Custom events emitted by the component                   | `@Event() bdsChange: EventEmitter`                                     |
| 8     | **Constructor**                  | Constructor (only if initialization logic is required)   | `constructor() { super(); }`                                           |
| 9     | **Lifecycle methods**            | Component lifecycle hooks in execution order (see below) | `connectedCallback()`, `componentWillLoad()`, `disconnectedCallback()` |
| 10    | **Event listeners**              | `@Listen` decorators                                     | `@Listen('scroll', { target: 'window', passive: true })`               |
| 11    | **Event handlers**               | Private methods that handle events                       | `private handleClick = () => { ... }`                                  |
| 12    | **Public methods**               | `@Method()` — public API exposed to consumers            | `async open()`, `async checkValidity()`                                |
| 13    | **Internal methods**             | Private helper methods                                   | `private updateState()`                                                |
| 14    | **Render helpers**               | Private methods returning JSX fragments                  | `private renderLabel()`                                                |
| 15    | **render() method**              | Main render method — always last                         | `render() { return <Host>...</Host>; }`                                |

### Lifecycle methods ordering

Lifecycle methods in section 9 must appear in their natural execution order, not alphabetically. See the lifecycle flow diagram in [`development-standards.md §1.3`](./development-standards.md#13-component-code-organization).

### Alphabetical ordering within sections

Within each section (except lifecycle methods), members must be ordered alphabetically.

```ts
// ✅ Correct — alphabetical within @Prop() section
@Prop({ reflect: true }) disabled = false;
@Prop({ reflect: true }) required = false;
@Prop({ reflect: true }) value!: string;

// ❌ Wrong — unsorted
@Prop({ reflect: true }) value!: string;
@Prop({ reflect: true }) disabled = false;
@Prop({ reflect: true }) required = false;
```

This rule applies to `@Prop()`, `@State()`, `@Event()`, event handlers, internal methods, and render helpers. Stacked `@Watch` decorators that target the same handler stay together as a unit — sort by the handler method name, not the decorator.

---

## Guarding Reflected `@Prop` Writes Inside `@Watch` Call Chains

**Problem:** When a `@Watch` handler (or a method it calls) writes back to the same reflected `@Prop` that triggered the watch, Stencil emits:

```
The state/prop "active" changed during rendering. This can potentially lead to infinite-loops and other bugs.
```

This happens because:

1. The VDOM reconciler calls `setAttribute` on the host element to reflect the updated prop.
2. mock-doc fires `attributeChangedCallback` synchronously during that DOM patch.
3. `attributeChangedCallback` re-enters the reactive prop system while the render cycle is still running.
4. Any write to the same prop at this point is flagged as a write-during-render.

**Pattern:** Guard the assignment with an equality check so the write is skipped when the value is already correct:

```ts
// ❌ Always writes — triggers Stencil warning when called during a @Watch cycle
private transitionBeforeClose() {
  this.active = false;
}

// ✅ Guards the write — no-op if active is already false
private transitionBeforeClose() {
  if (this.active) this.active = false;
}
```

Apply this guard anywhere a method is called from a `@Watch` handler and writes back to a reflected `@Prop`.

**Test environment note:** Even with the component-level guard in place, Stencil's mock-doc re-entrancy (synchronous `attributeChangedCallback` during VDOM patching) can still produce the warning for the attribute reflection itself — not the component write. This residual noise is a test-environment artifact with no browser equivalent. Suppress it with `suppressConsoleWarn()` from `@/utils/testing/mocks/console` in the affected spec file.

---

## Reference-Stable State Updates

**Problem:** Stencil re-renders a component whenever a `@State()` field (or a mutable `@Prop()`) is reassigned to a *new reference* — regardless of whether the new value is deep-equal to the old one. The idiomatic immutable-update shape, `this.foo = { ...this.foo, x: y }`, always produces a new object, so if `y` happens to equal the existing value, the component still re-renders for nothing. Left unchecked, this shows up as flickering, lost scroll/focus, wasted work in expensive `render()` bodies, and animations restarting on a no-op interaction.

This bug shipped in `bds-date-picker`'s original implementation in two forms:

1. `selectDay()` (a plain reducer-style utility) unconditionally returned `{ ...draft, selectedDate: isoDate }`, even when `isoDate` already matched `draft.selectedDate` — reselecting the already-selected day produced a new `draft` reference and a redundant re-render.
2. `listenClickTrigger()` reset the draft and reopened the popover on every trigger click, including a second click while the popover was already open — an idempotency bug in the handler itself, not the state shape (see the companion pattern below).

**Pattern — guard the update with an early return of the existing reference:**

```ts
// ❌ Always creates a new reference, even when nothing changed
export function selectDay(draft: DatePickerDraftState, isoDate: string): DatePickerDraftState {
  return { ...draft, selectedDate: isoDate };
}

// ✅ Returns the exact same reference when the value is unchanged
export function selectDay(draft: DatePickerDraftState, isoDate: string): DatePickerDraftState {
  if (draft.selectedDate === isoDate) return draft;
  return { ...draft, selectedDate: isoDate };
}
```

Apply the same guard directly in a class method when the spread happens inline rather than through an extracted function:

```ts
// ✅ this.columnWidths keeps its reference when the resize didn't actually change anything
private setColumnWidth(id: string, width: number): void {
  if (this.columnWidths[id] === width) return;
  this.columnWidths = { ...this.columnWidths, [id]: width };
}
```

**Companion pattern — idempotent trigger handlers:** Guard event handlers that trigger an imperative action (open/close/navigate/toggle) against redundant invocation when already in the target state:

```ts
// ✅ Repeat clicks while already open don't reset draft state or reopen the popover
private listenClickTrigger = () => {
  if (this.popoverVisible) return;
  this.draft = cloneDraftFromValue(this.value);
  this.bdsPopover?.showPopover();
};
```

**Verifying the fix:** Reference-stability bugs have no visible symptom in a static screenshot — verify with a render-count instrumentation, not a snapshot. Add a temporary `console.count('render')` inside `render()`, exercise the repeat-interaction scenario in the browser (Playwright or manual), and confirm the count does *not* increment on the no-op repeat. Remove the instrumentation before committing.

A prototype-monkey-patch approach (patching `customElements.get('bds-x').prototype.render` to count renders) does **not** work — Stencil's compiled runtime does not dispatch through a dynamically-overridable prototype method. Use `console.count()` inside the source instead.

**Testing:** Cover this with a `.toBe()` reference-equality assertion (not `.toEqual()`) alongside any test for a reducer-style `@State()` setter — see `ai-docs/guidelines/testing-knowledge` / the `testing-knowledge` skill.

---

## Event Listener Placement: vDOM vs `@Listen` vs `addEventListener`

### Decision rule

Use **vDOM inline listeners** on `<Host />` or any rendered element for all events that reach the host via DOM bubbling. Use `@Listen` only when you need one of its exclusive options — otherwise you lose TypeScript type safety and trigger the `prefer-vdom-listener` ESLint rule.

| Dimension                              | vDOM inline (`onKeyDown={...}`) | `@Listen`                        | imperative `addEventListener` |
| -------------------------------------- | ------------------------------- | -------------------------------- | ----------------------------- |
| TypeScript type-safe                   | ✅ handler signature enforced   | ❌ event name is a plain string  | ✅                            |
| ESLint `prefer-vdom-listener`          | ✅ compliant                    | ⚠️ triggers rule without options | ✅ compliant                  |
| Target: `window` / `document` / `body` | ❌                              | ✅ via `{ target: '...' }`       | ✅                            |
| Capture phase                          | ❌                              | ✅ via `{ capture: true }`       | ✅                            |
| Passive listener                       | ❌                              | ✅ via `{ passive: true }`       | ✅                            |
| Lifecycle auto-managed                 | ✅                              | ✅                               | ❌ manual cleanup required    |

### vDOM listener (default)

```tsx
// ✅ Correct for component-scoped keyboard/pointer events
render() {
  return (
    <Host role="radiogroup" onKeyDown={this.handleKeyDown}>
      <slot />
    </Host>
  );
}
```

The handler is a class arrow function to preserve `this`:

```tsx
private handleKeyDown = (event: KeyboardEvent) => {
  // TypeScript enforces KeyboardEvent here — typos and wrong signatures are caught at compile time
};
```

### `@Listen` (only when required)

Use `@Listen` only for events outside the component's subtree, capture phase, or explicit passive requirements:

```tsx
// ✅ Correct — window-scoped, passive scroll listener
@Listen('scroll', { target: 'window', passive: true })
handleScroll(ev: Event) { ... }

// ❌ Wrong — no options, component-scoped; triggers prefer-vdom-listener, loses type safety
@Listen('keydown')
handleKeyDown(ev: KeyboardEvent) { ... }
```

The `prefer-vdom-listener` ESLint rule fires on bare `@Listen('keydown')` (no second argument). Passing `{}` or `{ passive: false }` silences the rule as a side-effect of the rule's condition, but that is a workaround — the right fix is to use a vDOM listener.

### `addEventListener` (avoid for component-scoped events)

Imperative `addEventListener` requires manual lifecycle wiring:

```tsx
connectedCallback() { this.el.addEventListener('keydown', this.handleKeyDown); }
disconnectedCallback() { this.el.removeEventListener('keydown', this.handleKeyDown); }
```

Omitting the `disconnectedCallback` cleanup is a common memory leak. Prefer vDOM listeners, which are managed by Stencil's reconciler automatically.

---

## Composite Light DOM Event Boundary

Any Stencil composite component that accepts child components via named slots and re-emits their events must call `event.stopPropagation()` before re-emitting. Without it, consumers receive each event twice — once from the bubbled child event and once from the host re-emission.

This happens because slotted child elements remain in the light DOM. Their events bubble naturally up to the composite host element. When the host also listens to the same event and re-emits its own version, both reach external listeners.

```typescript
// In the host listener that re-emits — always stop the child's event first
addElementListener(this.bdsList, "bdsChange", (event: Event) => {
  event.stopPropagation(); // prevent bds-list-menu's event reaching consumers
  const value = (event as CustomEvent<string | undefined>).detail ?? "";
  this.setValue(value);
});

// For every child event the host owns but does NOT re-emit — stop-only guard
addElementListener(this.bdsField, "valueChange", (event: Event) => {
  event.stopPropagation();
});
```

**Detecting duplicate events:** open the Storybook Actions panel, trigger a single interaction, and check the `from` field on each entry. Any entry where `from` is a child element name (not the host) is a leaked event — a `stopPropagation()` guard is missing.

**JSX-composed children:** the same boundary applies when a composite component composes a child directly in JSX (`<bds-select onBdsChange={...} onValueChange={...}>`) rather than wiring it imperatively via `addElementListener`. `event.stopPropagation()` must be called inside the inline handler itself, on every handler attached to the child — including ones that only guard and do not re-emit:

```tsx
function stopSelectEventPropagation(event: Event): void {
  event.stopPropagation();
}

<bds-select
  value={toTwoDigits(hour)}
  onBdsChange={(event: CustomEvent<string | string[]>) => {
    event.stopPropagation(); // stop bds-select's bdsChange before re-deriving the picker's own value
    onHourChange(Number(event.detail));
  }}
  onValueChange={stopSelectEventPropagation}
>
```

Confirmed second occurrence: `bds-date-picker`'s `renderTimeSelector.tsx` composes two `bds-select` instances for hour/minute entry (EOA-17138 Task 3). `bds-select` emits bare, bubbling `bdsChange`/`valueChange` events that share their name with `bds-date-picker`'s own public `@Event() bdsChange`/`@Event() valueChange` — without the inline `stopPropagation()` calls above, a consumer listening on the `bds-date-picker` host received a spurious extra `bdsChange` (the raw hour/minute string) ahead of the picker's own correctly-typed event.

---

## DOM API Gotchas

### `setAttribute` requires kebab-case for ARIA attributes

`setAttribute` always takes the HTML attribute name in kebab-case. Passing a camelCase property name writes a non-standard, unrecognised attribute to the DOM — no runtime error, but the attribute is invisible to screen readers.

```ts
// ✅ Correct
trigger.setAttribute("aria-describedby", "tooltip-content");

// ❌ Wrong — writes a non-standard attribute; screen readers ignore it
trigger.setAttribute("ariaDescribedBy", "tooltip-content");
```

The confusion arises because the DOM _property_ accessor uses camelCase (`element.ariaDescribedBy`), but `setAttribute` operates on the HTML _attribute_ name, which is always kebab-case for ARIA attributes. These are two different access paths to the same underlying value.

---

## Accessor and Boolean Expression Conventions

### Getter naming — no `get` prefix

A getter property named `getPlacement` is doubly redundant: the `get` keyword already marks it as a getter, and callers read it as `this.getPlacement`. Name getters after the value they return.

```ts
// ✅ Correct
get placement() { ... }
get floatingContent() { ... }

// ❌ Wrong
get getPlacement() { ... }
get getFloatingContent() { ... }
```

### `|| false` is always redundant

`!x || false` always evaluates to `!x`. The `|| false` tail adds no logical effect.

```ts
// ✅ Correct
return !this.floatingOptions.hideArrow;

// ❌ Wrong — the || false is dead code
return !this.floatingOptions.hideArrow || false;
```

---

## Mixin Architecture

Components extend at most one mixin using the `Mixin()` factory from `@stencil/core`. Plain components that need no shared behavior are bare Stencil classes.

| Mixin                 | Purpose                                                                                                                         | Components using it                                                                                                                                 |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| `formAssociatedMixin` | FACE lifecycle callbacks (`formAssociatedCallback`, `formResetCallback`, `formStateRestoreCallback`), `ElementInternals` wiring | `BdsTextField`, `BdsCheckbox`, `BdsCheckboxButton`, `BdsCheckboxCard`, `BdsCheckboxGroup`, `BdsRadioGroup`, `BdsSlider`, `BdsTagField`, `BdsToggle` |
| `anchoredMixin`       | Floating UI positioning and anchor element resolution                                                                           | `BdsPopover`, `BdsTooltip`                                                                                                                          |
| `backdropMixin`       | Backdrop overlay management and focus trapping                                                                                  | `BdsDialog`                                                                                                                                         |
| `floatingMixin`       | Base floating positioning — used internally by `anchoredMixin`, not consumed directly                                           | (internal)                                                                                                                                          |
| `WithLinks`           | Renders `<a>` or `<button>` depending on `href` presence                                                                        | `BdsListMenuItem`                                                                                                                                   |

### When to add a new mixin

Create a new mixin **only when two or more components share identical lifecycle logic that cannot be extracted into a utility function**. Typical qualifying cases:

- Browser API setup/teardown that must hook into Stencil lifecycle callbacks (`connectedCallback`, `disconnectedCallback`).
- DOM side effects that must run at a specific component lifecycle moment.

**Anti-patterns — do not create a mixin for:**

- ❌ Shared types or interfaces — use `types/` files instead.
- ❌ Pure utility logic — use `@/utils/` instead.
- ❌ Behavior required by only one component.

**`@AttachInternals()` placement rule:** The `@AttachInternals()` decorator must appear on the component class body, never inside a mixin factory. Stencil resolves it at registration time; placing it inside a mixin factory produces a silent runtime failure. See [ADR 0001](../decisions/0001-attach-internals-must-be-on-component-class-not-in-mixin.md).

---

## `IComponent.ts` Interface Contract

`IComponent.ts` interfaces describe only what the **consumer configures** — the set of publicly settable `@Prop()` members.

**Must NOT be in `IComponent.ts`:**

- `@Event()` outputs — `EventEmitter<T>` members are declared on the class body. Adding them to the interface forces the type to reference an internal abstraction consumers never set.
- Group-propagated props — props the parent group component writes imperatively (e.g. `name`, `showDivider`, `isFirst`) are parent-child coordination details, not consumer API.
- `@State()` mirrors — internal reactive state (`isDisabled`, `isOpen`) is never part of the public API.

**Interface members must be optional when the prop has a default value.** A required interface member implies the consumer must always supply it. With optional members, bare-attribute patterns (`<bds-radio-group disabled>`) work correctly in React and HTML.

```typescript
// ✅ Correct — props with component-side defaults are optional
export interface IRadioGroup {
  name: string; // no default on the component — required
  value?: string; // default = ''
  disabled?: boolean; // default = false
}

// ❌ Wrong — disabled has a default; marking it required is misleading
export interface IRadioGroup {
  name: string;
  disabled: boolean; // forces consumer to always pass disabled={false}
}
```

**Required members first, optional members last.** Once required-vs-optional is decided per the rule above, order the interface body so every required member (no `?`) appears before every optional member (`?`) — never interleaved. This applies to every interface in a component's `types/` directory, not only the `IComponent.ts` consumer-facing contract (event-detail interfaces, internal option objects, etc. follow the same rule whenever they mix required and optional fields).

```typescript
// ✅ Correct — required members grouped first, optional last
export interface ICalendarGrid {
  grid: MonthGrid;
  year: number;
  month: number;
  prevDisabled: boolean;
  nextDisabled: boolean;
  selectedDate?: string;
  locale?: DateEngineLocale;
}

// ❌ Wrong — selectedDate?/locale? interleaved between required members
export interface ICalendarGrid {
  grid: MonthGrid;
  selectedDate?: string;
  year: number;
  month: number;
  locale?: DateEngineLocale;
  prevDisabled: boolean;
  nextDisabled: boolean;
}
```

Within each group (required, then optional), preserve whatever order already existed — this rule only moves optional members past the required ones, it doesn't otherwise reorder.

---

## `IFormControl<T>` Interface Layering

Three interface levels govern all Boreal DS form controls and must be implemented together:

| Interface                  | Location                   | Responsibility                                                                                            |
| -------------------------- | -------------------------- | --------------------------------------------------------------------------------------------------------- |
| `IFormAssociatedCallbacks` | `form-associated.mixin.ts` | Declares `formDisabledCallback`, `formResetCallback`, `formStateRestoreCallback` signatures               |
| `IFormValueEmitter<T>`     | `form-associated.mixin.ts` | Declares `valueChange: EventEmitter<T>` — enforces consistent event naming across all form controls       |
| `IFormControl<T>`          | `form-associated.mixin.ts` | Composite: `IFormAssociatedCallbacks & IFormValueEmitter<T>` — the single interface a form class declares |

```typescript
export class BdsTextField
  extends Mixin(formAssociatedMixin)
  implements ITextField, IFormControl<string>
{
  @AttachInternals() internals!: ElementInternals;
  @Event() valueChange!: EventEmitter<string>;
}
```

**`valueChange` is reserved for Vue `v-model` integration.** Every form component that exposes a `value` prop must emit `valueChange` and register in `componentModels` in `vue-output-target.ts` in the same PR. Use bare `@Event()` — no `bubbles` or `composed` options are needed in light DOM. Use `bds{Action}` names for all other events.
