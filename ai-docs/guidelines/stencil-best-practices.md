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
- The `:host` pseudo-class has no effect without a shadow boundary (per MDN). Use direct tag selectors instead: `bds-button { ... }`, `bds-checkbox:focus-visible { ... }`.
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

- `@AttachInternals()` must be declared directly on the component class body — never inside a mixin factory (see `.agents/memory/stencil-face-attach-internals.md`).
- Native FACE prototype members are blocked by Stencil's element proxy; expose them via `@Method()` wrappers (see `.agents/memory/stencil-face-element-proxy-limits.md`).
- Use `el.querySelector(...)` for all inner element access — no `shadowRoot` exists.

---

## Component Class Member Ordering

All component classes must follow this 15-section member ordering. Consistent ordering improves readability, code review efficiency, and navigation.

### The 15-section standard

| Order | Section                          | Description                                                          | Examples                                                                 |
| ----- | -------------------------------- | -------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| 1     | **Static members**               | Static properties and methods                                        | `static tagName = 'bds-button'`                                          |
| 2     | **Private non-reactive members** | Private class properties that don't trigger re-renders               | `private helperInstance: Helper`                                         |
| 3     | **Element reference**            | Reference to the component's host element                            | `@Element() el!: HTMLElement`                                            |
| 4     | **Internal reactive state**      | Private reactive properties                                          | `@State() private isOpen = false`                                        |
| 5     | **Public reactive properties**   | Public props that trigger re-renders when changed                    | `@Prop() disabled = false`                                               |
| 6     | **Property watchers**            | Handlers that run when specific properties change                    | `@Watch('disabled')`, `@Watch('value')`                                  |
| 7     | **Event declarations**           | Custom events emitted by the component                               | `@Event() bdsChange: EventEmitter`                                       |
| 8     | **Constructor**                  | Constructor (only if initialization logic is required)               | `constructor() { super(); }`                                             |
| 9     | **Lifecycle methods**            | Component lifecycle hooks in execution order (see below)             | `connectedCallback()`, `componentWillLoad()`, `disconnectedCallback()`   |
| 10    | **Event listeners**              | `@Listen` decorators                                                 | `@Listen('scroll', { target: 'window', passive: true })`                 |
| 11    | **Event handlers**               | Private methods that handle events                                   | `private handleClick = () => { ... }`                                    |
| 12    | **Public methods**               | `@Method()` — public API exposed to consumers                        | `async open()`, `async checkValidity()`                                  |
| 13    | **Internal methods**             | Private helper methods                                               | `private updateState()`                                                  |
| 14    | **Render helpers**               | Private methods returning JSX fragments                              | `private renderLabel()`                                                  |
| 15    | **render() method**              | Main render method — always last                                     | `render() { return <Host>...</Host>; }`                                  |

### Lifecycle methods ordering

Lifecycle methods in section 9 must appear in their natural execution order, not alphabetically.

**Initial load cycle:**

| Order | Method                  | When it runs                                                                                     |
| ----- | ----------------------- | ------------------------------------------------------------------------------------------------ |
| 1     | `connectedCallback()`   | Every time the element connects to the DOM (before `componentWillLoad` on first connection)      |
| 2     | `componentWillLoad()`   | Once, just after first connection — good for one-time async setup                                |
| 3     | `componentWillRender()` | Before every `render()`                                                                          |
| 4     | `render()`              | Template rendering (section 15, not here)                                                        |
| 5     | `componentDidRender()`  | After every `render()`                                                                           |
| 6     | `componentDidLoad()`    | Once, just after first `render()` completes                                                      |

**Update cycle (triggered by prop/state changes):**

| Order | Method                    | When it runs                                                               |
| ----- | ------------------------- | -------------------------------------------------------------------------- |
| 1     | `componentShouldUpdate()` | Returns boolean to allow/prevent the re-render                             |
| 2     | `componentWillUpdate()`   | Before update render (never called on first render)                        |
| 3     | `componentWillRender()`   | Before every `render()`                                                    |
| 4     | `componentDidRender()`    | After every `render()`                                                     |
| 5     | `componentDidUpdate()`    | After update render completes (never called on first render)               |

**Disconnection:**

| Method                   | When it runs                                                   |
| ------------------------ | -------------------------------------------------------------- |
| `disconnectedCallback()` | Every time the element disconnects from the DOM                |

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
