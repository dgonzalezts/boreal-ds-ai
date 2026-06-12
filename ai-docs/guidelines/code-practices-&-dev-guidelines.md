# PxG CL Code Practices & Development Guidelines

## Overview

This document defines mandatory code practices, quality standards, and development workflows for all contributors to the Proximus Global (PxG) component library. It ensures:

- Code quality and consistency across teams
- Reduced review friction and faster merges
- Maintainable, accessible, and well-tested components
- Consistent developer experience

---

## 1. COMPONENT DEVELOPMENT GUIDELINES

Component development guidelines establish the foundational patterns and naming conventions for building components in the library. These standards ensure components are architecturally sound, follow clear inheritance patterns, use consistent naming across properties, events, slots, and CSS classes, maintain predictable code organization, and implement robust property and event APIs that integrate seamlessly with web standards and modern frameworks.

### 1.1 Component Architecture & Inheritance

Component architecture defines how shared behavior is distributed across components. Boreal DS uses **mixin-based composition** via Stencil's `Mixin()` factory rather than class inheritance chains. This keeps components flat and avoids the fragility of deep prototype hierarchies.

#### Mixin Architecture

Components extend at most one mixin using the `Mixin()` factory from `@stencil/core`. Plain components that need no shared behavior are bare Stencil classes.

| Mixin                 | Purpose                                                                                                                                             | Components using it                                                                                                                                 |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| `formAssociatedMixin` | FACE lifecycle callbacks (`formAssociatedCallback`, `formResetCallback`, `formStateRestoreCallback`), `ElementInternals` wiring, form participation | `BdsTextField`, `BdsCheckbox`, `BdsCheckboxButton`, `BdsCheckboxCard`, `BdsCheckboxGroup`, `BdsRadioGroup`, `BdsSlider`, `BdsTagField`, `BdsToggle` |
| `anchoredMixin`       | Floating UI positioning, anchor element resolution                                                                                                  | `BdsPopover`, `BdsTooltip`                                                                                                                          |
| `backdropMixin`       | Backdrop overlay management and focus trapping                                                                                                      | `BdsDialog`                                                                                                                                         |
| `floatingMixin`       | Base floating positioning (used internally by `anchoredMixin`)                                                                                      | Not used directly                                                                                                                                   |
| `WithLinks`           | Renders `<a>` or `<button>` depending on `href` presence                                                                                            | `BdsListMenuItem`                                                                                                                                   |

**Form component pattern:**

```typescript
import {
  AttachInternals,
  Component,
  Event,
  EventEmitter,
  Mixin,
  Prop,
  State,
  Watch,
} from "@stencil/core";
import { formAssociatedMixin, type IFormControl } from "@/mixins";

@Component({
  tag: "bds-my-field",
  styleUrl: "bds-my-field.scss",
  formAssociated: true,
})
export class BdsMyField
  extends Mixin(formAssociatedMixin)
  implements IMyField, IFormControl<string>
{
  @AttachInternals() internals!: ElementInternals;

  @Prop({ reflect: true }) readonly disabled: boolean = false;
  @State() private isDisabled: boolean = false;

  @Watch("disabled")
  onDisabledChange(next: boolean) {
    this.isDisabled = next;
  }

  @Prop({ mutable: true, reflect: true }) value: string = "";
  @Event() valueChange!: EventEmitter<string>;

  public formResetCallback(): void {
    this.value = "";
  }
}
```

**Plain component (no mixin):**

```typescript
@Component({ tag: "bds-button", styleUrl: "bds-button.scss" })
export class BdsButton implements IButton {
  // No extends — plain Stencil class
}
```

#### When to Add a New Mixin

Create a new mixin **only when two or more components share identical lifecycle logic that cannot be extracted into a utility function**. Typical cases:

- Browser API setup/teardown that must hook into Stencil lifecycle callbacks (`connectedCallback`, `disconnectedCallback`)
- DOM side effects that must run at specific component lifecycle moments

**Anti-patterns — do not create a mixin for:**

- ❌ Shared types or interfaces — use `types/` files instead
- ❌ Pure utility logic — use `@/utils/` instead
- ❌ Single-component behavior

**`@AttachInternals()` placement rule:** The `@AttachInternals()` decorator must appear on the component class body — never inside a mixin factory. Stencil resolves it at component registration time; placing it in a mixin factory produces a silent runtime failure. See [ADR 0001](../decisions/0001-attach-internals-must-be-on-component-class-not-in-mixin.md).

#### Why Base Class Architecture Doesn't Work in Stencil

Traditional object-oriented inheritance patterns using base classes are fundamentally incompatible with Stencil's decorator resolution model. This is not a design preference — it is a **technical constraint** imposed by Stencil's compile-time architecture.

**The Problem: Compile-Time Decorator Resolution**

Stencil decorators (`@Component`, `@Prop`, `@State`, `@Event`, `@Watch`, etc.) are resolved at **compile time** through static analysis of the component class body, not at runtime. The Stencil compiler reads the Abstract Syntax Tree (AST) to extract metadata directly from the decorated class before TypeScript transpiles it to JavaScript.

When decorators are placed in a base class:

1. **Decorator metadata is lost** — The compiler only analyzes the immediate class body annotated with `@Component()`. It does not traverse the prototype chain to collect decorators from parent classes.
2. **Props and state are not registered** — `@Prop()` and `@State()` decorators in base classes are invisible to the compiler's metadata collection phase.
3. **Silent runtime failures** — The component compiles without errors, but props and events defined in the base class simply don't work at runtime.

**Historical Context**

Between Stencil v0.12 and v0.13 (2018-2019), the Stencil team [explicitly disabled class inheritance for components](https://github.com/stenciljs/core/issues/1060) and made it a **compiler error**. While later versions relaxed this restriction, [the underlying limitation remains](https://github.com/stenciljs/core/issues/1127): decorators in base classes are not processed, making traditional inheritance patterns unreliable and error-prone.

**Why Mixins Are the Solution**

The `Mixin()` factory pattern works because it operates at the **class definition level**, not the prototype chain level:

```typescript
// ❌ DOESN'T WORK — decorators in BaseComponent are ignored
class BaseComponent {
  @Prop() value: string; // Never registered
}

@Component({ tag: "my-field" })
class MyField extends BaseComponent {}

// ✅ WORKS — mixin injects members into the component class body
const myMixin = () => ({ value: "" });

@Component({ tag: "my-field" })
class MyField extends Mixin(myMixin) {
  @Prop() value: string; // Registered correctly
}
```

The `Mixin()` factory **copies properties directly into the component class** before the `@Component` decorator is processed. This ensures all lifecycle hooks, methods, and properties are visible to Stencil's compile-time analyzer as if they were written directly in the component class.

#### Rationale

1. **Flat prototype chain** — At most one level of shared behavior; no hidden ancestor logic to trace.
2. **No base class coupling** — Non-form components are plain classes with no shared ancestor.
3. **Explicit contracts** — `IFormControl<T>` and `IFormAssociatedCallbacks` are interface types, not base classes; TypeScript enforces the contract without dictating implementation.
4. **Stencil compatibility** — Stencil decorators are resolved at compile time from the class body; deep inheritance chains cause decorator resolution failures.

### 1.2 Component Naming Conventions

Consistent naming conventions across all component API surfaces ensure predictability, reduce cognitive load, and align with web standards. This section establishes naming patterns for custom elements, properties, methods, events, slots, CSS parts, and custom properties.

#### Naming Convention Reference

| Element                   | Format                        | Rules                                                                                                                                                                                   | Examples                                                                                |
| ------------------------- | ----------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| **Custom Element Tag**    | `prefix-component-name`       | - kebab-case<br/>- Must contain hyphen<br/>- Prefix to avoid conflicts<br/>- Lowercase only                                                                                             | `my-button`<br/>`app-dropdown`<br/>`ui-card`                                            |
| **Component Class**       | `PascalCase`                  | - PascalCase<br/>- Align with tag name<br/>- Descriptive, not generic                                                                                                                   | `MyButton`<br/>`AppDropdown`<br/>`UiCard`                                               |
| **Properties (JS)**       | `camelCase`                   | - camelCase<br/>- `@Prop()` booleans: plain adjectives, no prefix (`disabled`, not `isDisabled`)<br/>- `@State()` mirrors use `is*` prefix (`isDisabled`)<br/>- Avoid negative booleans | `disabled`<br/>`closable`<br/>`required`<br/>`maxLength`                                |
| **Attributes (HTML)**     | `kebab-case`                  | - kebab-case (auto-mapped from camelCase)<br/>- Explicit mapping for HTML standards                                                                                                     | `disabled`<br/>`max-length`<br/>`readonly` (explicit)                                   |
| **Public Methods**        | `camelCase`                   | - camelCase<br/>- Start with descriptive verb<br/>- Clear action intent                                                                                                                 | `open()`<br/>`close()`<br/>`validate()`<br/>`reset()`                                   |
| **Private Methods**       | `camelCase` or `#private`     | - Prefix with `_` or use `#` private fields<br/>- Not part of public API                                                                                                                | `_handleClick()`<br/>`#updateState()`                                                   |
| **Event Handlers**        | `handle*` or `on*`            | - Prefix: `handle*` or `on*`<br/>- Describe what is being handled                                                                                                                       | `handleClick()`<br/>`onInputChange()`<br/>`handleKeyDown()`                             |
| **Custom Events**         | `bds{Action}` (camelCase)     | - `bds` prefix + PascalCase action<br/>- Descriptive action<br/>- Lifecycle: `Opening`/`Closing` suffix for cancelable<br/>- `valueChange` reserved for Vue v-model                     | `bdsChange`<br/>`bdsClose`<br/>`bdsOpening` (cancelable)<br/>`bdsOpen` (non-cancelable) |
| **Slots**                 | `kebab-case`                  | - Default slot: unnamed<br/>- Named slots: kebab-case, descriptive                                                                                                                      | (unnamed default)<br/>`header`<br/>`footer`<br/>`prefix-icon`                           |
| **CSS Parts**             | `kebab-case`                  | - Not applicable — Boreal DS uses light DOM (`shadow: false`). CSS `::part()` selectors only work with shadow DOM; consumers style components directly via class selectors.             | N/A                                                                                     |
| **CSS Custom Properties** | `--prefix-component-property` | - Double dash prefix<br/>- kebab-case<br/>- Include component name<br/>- Descriptive modifier                                                                                           | `--my-button-bg-color`<br/>`--my-input-border-width`<br/>`--my-card-padding`            |

#### Interface File Naming

Component interface files must use `IComponent.ts` naming — not `IBdsComponent.ts`.

| Correct       | Wrong            |
| ------------- | ---------------- |
| `ITooltip.ts` | `IBdsTooltip.ts` |
| `IPopover.ts` | `IBdsPopover.ts` |
| `IBanner.ts`  | `IBdsBanner.ts`  |

The `Bds` prefix is reserved exclusively for custom element tag names (`bds-tooltip`) and Stencil component class names (`BdsTooltip`). Interface types live in a `types/` subdirectory alongside the component file.

#### Boolean Property Naming

Boolean properties require special attention to ensure they work correctly with HTML attributes:

| Pattern                                     | Status           | Reasoning                                                                                                        | Example                                              |
| ------------------------------------------- | ---------------- | ---------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| Positive boolean defaulting to `false`      | ✅ **Correct**   | Attribute presence = `true`. Can be set to `false` by omitting attribute.                                        | `disabled`, `readonly`, `required`                   |
| Negative boolean defaulting to `true`       | ❌ **Incorrect** | Cannot be set to `false` from HTML (attribute presence always = `true`).                                         | ~~`enabled`~~, ~~`editable`~~                        |
| `@Prop()` boolean with `is*`, `has*` prefix | ❌ **Not used**  | Boreal DS follows native HTML style (`disabled`, `required`). Prefixes are reserved for `@State()` mirrors only. | `isDisabled` (state mirror), `isOpen` (state mirror) |

**Example:**

```typescript
// ✅ CORRECT — @Prop() booleans use plain adjectives (native HTML style)
@Prop({ reflect: true }) readonly disabled: boolean = false;
@Prop({ reflect: true }) readonly closable: boolean = false;
@Prop({ reflect: true }) readonly required: boolean = false;

// ✅ CORRECT — @State() mirrors for internal tracking use is* prefix
@State() private isDisabled: boolean = false;

// ❌ INCORRECT — don't add is*/has* prefix on @Prop() booleans
@Prop() isOpen: boolean = false;   // should be `open`
@Prop() hasError: boolean = false; // should be `error`

// ❌ INCORRECT — negative booleans can't be set to false via HTML attributes
@Prop() enabled: boolean = true;
```

#### Custom Element Tag Naming

Custom element tags must follow web standards:

**Requirements:**

- Must contain at least one hyphen (`-`)
- Must be lowercase
- Should use a prefix to avoid conflicts with other libraries or future HTML elements
- Should be descriptive and self-documenting

**Pattern:**

```
<prefix>-<component-name>
```

**Examples:**

```html
<!-- ✅ GOOD -->
<my-button>Click me</my-button>
<app-dropdown options="..."></app-dropdown>
<ui-card-header>Title</ui-card-header>

<!-- ❌ BAD -->
<button>Click me</button>
<!-- No hyphen, conflicts with native element -->
<MyButton>Click me</MyButton>
<!-- Not lowercase -->
<card>Content</card>
<!-- No prefix, could conflict -->
```

#### Property and Attribute Mapping

Properties (JavaScript) and attributes (HTML) should map predictably:

| Property (JavaScript) | Attribute (HTML) | Explicit Mapping Needed?   |
| --------------------- | ---------------- | -------------------------- |
| `disabled`            | `disabled`       | No (single word)           |
| `maxLength`           | `max-length`     | No (auto-converted)        |
| `readOnly`            | `readonly`       | ✅ **Yes** (HTML standard) |
| `tabIndex`            | `tabindex`       | ✅ **Yes** (HTML standard) |
| `ariaLabel`           | `aria-label`     | ✅ **Yes** (ARIA standard) |

**Explicit Mapping Example:**

```typescript
// Explicit mapping for HTML standard attributes (Stencil syntax)
@Prop({ attribute: 'readonly', reflect: true }) readonly readOnly: boolean = false;

@Prop({ attribute: 'tabindex' }) readonly tabIndex: number = 0;

@Prop({ attribute: 'aria-label', reflect: true }) readonly ariaLabel: string;
```

#### Event Naming Patterns

Custom events should follow a consistent naming pattern:

**Format:**

```
bds{Action}        // Non-cancelable  e.g. bdsChange, bdsClose, bdsSelect
bds{Action}ing     // Cancelable lifecycle  e.g. bdsOpening, bdsClosing
```

All custom events in Boreal DS use the `bds` prefix followed by a PascalCase action verb. This makes event names instantly recognisable in consumer code and avoids collisions with native DOM events.

> **`valueChange` is reserved** for Vue `v-model` integration (see §1.6). Use `bds{Action}` names for all other events.

**Examples:**

| Event Type   | Event Name   | Cancelable | Usage                                |
| ------------ | ------------ | ---------- | ------------------------------------ |
| Value change | `bdsChange`  | No         | Fired after value changes            |
| Form submit  | `bdsSubmit`  | No         | Fired after form submits             |
| Opening      | `bdsOpening` | ✅ Yes     | Fired before opening (can prevent)   |
| Opened       | `bdsOpen`    | No         | Fired after opening (cannot prevent) |
| Closing      | `bdsClosing` | ✅ Yes     | Fired before closing (can prevent)   |
| Closed       | `bdsClose`   | No         | Fired after closing (cannot prevent) |

**Implementation Example:**

```typescript
// Non-cancelable event
@Event() bdsChange: EventEmitter<string>;

this.bdsChange.emit(newValue);

// Cancelable lifecycle event
@Event({ cancelable: true }) bdsOpening: EventEmitter<void>;
@Event() bdsOpen: EventEmitter<void>;

const evt = this.bdsOpening.emit();
if (!evt.defaultPrevented) {
  this.open = true;
  this.bdsOpen.emit();
}
```

#### Slot Naming

Slots provide content insertion points in components:

| Slot Type        | Naming                  | Example                                                                                                |
| ---------------- | ----------------------- | ------------------------------------------------------------------------------------------------------ |
| **Default slot** | Unnamed                 | `<slot></slot>`                                                                                        |
| **Named slots**  | kebab-case, descriptive | `<slot name="header"></slot>`<br/>`<slot name="footer"></slot>`<br/>`<slot name="prefix-icon"></slot>` |

**Usage Example:**

```html
<!-- Component definition -->
<div class="card">
  <slot name="header"></slot>
  <slot></slot>
  <!-- Default slot -->
  <slot name="footer"></slot>
</div>

<!-- Component usage -->
<my-card>
  <div slot="header">Card Title</div>
  <p>Default content goes here</p>
  <div slot="footer">Card Actions</div>
</my-card>
```

#### CSS Custom Properties Naming

CSS custom properties (CSS variables) enable theming and customization:

**Pattern:**

```
--<prefix>-<component>-<property>[-<modifier>]
```

**Structure:**

- `--prefix`: Library/app prefix
- `component`: Component name
- `property`: CSS property being customized
- `modifier`: Optional state/variant modifier

**Examples:**

```css
/* Component theming */
--my-button-bg-color
--my-button-text-color
--my-button-border-radius
--my-button-padding

/* State modifiers */
--my-button-bg-color-hover
--my-button-bg-color-active
--my-button-bg-color-disabled

/* Variant modifiers */
--my-button-primary-bg-color
--my-button-secondary-bg-color

/* Sizing */
--my-input-height
--my-input-padding-vertical
--my-input-padding-horizontal
```

#### Rationale

Consistent naming conventions provide several benefits:

1. **Predictability** — Developers can guess API names without consulting documentation
2. **Web Standards Alignment** — Follows HTML/CSS conventions (kebab-case for markup, camelCase for JavaScript)
3. **Conflict Avoidance** — Prefixes prevent conflicts with other libraries and future HTML elements
4. **Framework Compatibility** — Works seamlessly across vanilla JS, React, Vue, Angular, etc.
5. **Tooling Support** — IDEs, linters, and type checkers understand standard patterns
6. **Accessibility** — Proper ARIA attribute mapping ensures screen reader compatibility
7. **Maintainability** — Consistent patterns reduce cognitive load during code reviews and refactoring

### 1.3 Component Code Organization

Consistent code organization within component classes improves readability, maintainability, and code review efficiency. This section establishes the mandatory ordering of class members to ensure all components follow a predictable structure regardless of complexity.

#### Member Ordering Standard

All component classes must follow this member ordering:

| Order | Section                          | Description                                              | Examples                                                                  |
| ----- | -------------------------------- | -------------------------------------------------------- | ------------------------------------------------------------------------- |
| 1     | **Static members**               | Static properties and methods, including style constants | `static styles = css\`...\``                                              |
| 2     | **Private non-reactive members** | Private class properties that don't trigger re-renders   | `private helperInstance: Helper`<br/>`private cacheData: Map<>`           |
| 3     | **Element reference**            | Reference to the component's host element                | `@Element() el!: HTMLElement`                                             |
| 4     | **Internal reactive state**      | Private reactive properties (internal state)             | `@State() private isOpen = false`<br/>`@State() private count = 0`        |
| 5     | **Public reactive properties**   | Public properties that trigger re-renders when changed   | `@Prop() disabled = false`<br/>`@Prop() value: string`                    |
| 6     | **Property watchers**            | Handlers that run when specific properties change        | `@Watch('disabled')`<br/>`@Watch('value')`                                |
| 7     | **Event declarations**           | Custom events emitted by the component                   | `@Event() bdsChange: EventEmitter`<br/>`@Event() bdsSubmit: EventEmitter` |
| 8     | **Constructor**                  | Constructor (only if initialization logic is required)   | `constructor() { super(); }`                                              |
| 9     | **Lifecycle methods**            | Component lifecycle hooks in execution order             | `connectedCallback()`<br/>`componentWillLoad()`<br/>`componentDidLoad()`  |
| 10    | **Event listeners**              | Decorators for listening to DOM or custom events         | `@Listen('click')`<br/>`@Listen('myCustomEvent')`                         |
| 11    | **Event handlers**               | Private methods that handle events                       | `private handleClick()`<br/>`private onInputChange()`                     |
| 12    | **Public methods**               | Public API methods exposed to consumers                  | `async open()`<br/>`async close()`<br/>`async validate()`                 |
| 13    | **Internal methods**             | Private/protected helper methods                         | `private updateState()`<br/>`private calculateValue()`                    |
| 14    | **Render helpers**               | Private methods returning template fragments             | `private renderHeader()`<br/>`private renderFooter()`                     |
| 15    | **render() method**              | Main render method (always last)                         | `render() { return <Host>...</Host>; }`                                   |

#### Lifecycle Methods Ordering

Lifecycle methods within section 9 must follow their natural execution order based on when they are called during the component's lifecycle:

**Initial Load Cycle:**

| Order | Method                  | When It Runs                                                                                     |
| ----- | ----------------------- | ------------------------------------------------------------------------------------------------ |
| 1     | `connectedCallback()`   | Called every time component is connected to DOM (before `componentWillLoad` on first connection) |
| 2     | `componentWillLoad()`   | Called once, just after first connection to DOM. Good for async data loading.                    |
| 3     | `componentWillRender()` | Called before every `render()`                                                                   |
| 4     | `render()`              | Template rendering                                                                               |
| 5     | `componentDidRender()`  | Called after every `render()`                                                                    |
| 6     | `componentDidLoad()`    | Called once, just after first `render()` completes                                               |

**Update Cycle (triggered by prop/state changes):**

| Order | Method                    | When It Runs                                                               |
| ----- | ------------------------- | -------------------------------------------------------------------------- |
| 1     | `componentShouldUpdate()` | Called when prop/state changes. Returns boolean to allow/prevent rerender. |
| 2     | `componentWillUpdate()`   | Called before update render (never called on first render)                 |
| 3     | `componentWillRender()`   | Called before every `render()`                                             |
| 4     | `render()`                | Template rendering                                                         |
| 5     | `componentDidRender()`    | Called after every `render()`                                              |
| 6     | `componentDidUpdate()`    | Called after update render completes (never called on first render)        |

**Disconnection:**

| Order | Method                   | When It Runs                                                                        |
| ----- | ------------------------ | ----------------------------------------------------------------------------------- |
| 1     | `disconnectedCallback()` | Called every time component is disconnected from DOM (can be called multiple times) |

**Important Notes:**

- `connectedCallback()` can be called multiple times if element is moved in the DOM
- `componentWillLoad()` is only called once, even if element is reconnected
- Update lifecycle methods (`componentWillUpdate`, `componentDidUpdate`) are never called on first render
- Lifecycle methods bubble up from child to parent components

#### Alphabetical Ordering Within Sections

Within each section (except lifecycle methods), members should be ordered alphabetically:

```typescript
// ✅ GOOD - Alphabetical within section
@Prop() disabled: boolean;
@Prop() maxLength: number;
@Prop() value: string;

// ❌ BAD - Random ordering
@Prop() value: string;
@Prop() disabled: boolean;
@Prop() maxLength: number;
```

**Exception:** Lifecycle methods follow execution order, not alphabetical order.

#### Section Comments

Section comments are **optional** but encouraged for large components (more than ~150 lines). They make it easier to scan the file and locate specific member groups during code review.

Use clear section comments to separate major sections:

```typescript
@Component({ tag: "my-component" })
export class MyComponent {
  // =========================================================================
  // 1. Static members (e.g. static style constants, if any)
  // =========================================================================

  // =========================================================================
  // 2. Private non-reactive members
  // =========================================================================
  private cacheMap = new Map();

  // =========================================================================
  // 3. Element reference
  // =========================================================================
  @Element() el!: HTMLElement;

  // =========================================================================
  // 4. Internal reactive state
  // =========================================================================
  @State() private isOpen = false;

  // =========================================================================
  // 5. Public reactive properties
  // =========================================================================
  @Prop() disabled = false;
  @Prop() value = "";

  // =========================================================================
  // 6. Property watchers
  // =========================================================================
  @Watch("value")
  handleValueChange(newValue: string) {
    // ...
  }

  // =========================================================================
  // 7. Event declarations
  // =========================================================================
  @Event() bdsChange: EventEmitter;

  // =========================================================================
  // 8. Constructor (only if needed)
  // =========================================================================

  // =========================================================================
  // 9. Lifecycle methods
  // =========================================================================
  componentWillLoad() {
    // ...
  }

  // =========================================================================
  // 10. Event listeners
  // =========================================================================
  @Listen("click")
  onHostClick() {
    // ...
  }

  // =========================================================================
  // 11. Event handlers
  // =========================================================================
  private handleClick = () => {
    // ...
  };

  // =========================================================================
  // 12. Public methods
  // =========================================================================
  async open() {
    // ...
  }

  // =========================================================================
  // 13. Internal methods
  // =========================================================================
  private updateCache() {
    // ...
  }

  // =========================================================================
  // 14. Render helpers
  // =========================================================================
  private renderHeader() {
    // ...
  }

  // =========================================================================
  // 15. Render method
  // =========================================================================
  render() {
    // ...
  }
}
```

#### Well-Organized Component Example

```typescript
import { Component, Element, Prop, State, Watch, Event, EventEmitter, Listen, h, Host } from '@stencil/core';
import { validatePropValue } from '@/utils/helpers/validateProps';

/**
 * Example button component demonstrating proper 15-section member ordering
 */
@Component({
  tag: 'example-button',
  styleUrl: 'example-button.scss',
})
export class ExampleButton {
  // =========================================================================
  // 1. Static members
  // =========================================================================
  // (none for this component)

  // =========================================================================
  // 2. Private non-reactive members
  // =========================================================================
  private rippleInstance: any;

  // =========================================================================
  // 3. Element reference
  // =========================================================================
  @Element() el!: HTMLElement;

  // =========================================================================
  // 4. Internal reactive state
  // =========================================================================
  @State() private pressed = false;

  // =========================================================================
  // 5. Public reactive properties (alphabetical)
  // =========================================================================
  @Prop({ reflect: true }) disabled = false;
  @Prop({ reflect: true }) type: 'button' | 'submit' | 'reset' = 'button';
  @Prop({ reflect: true }) variant: 'primary' | 'secondary' = 'primary';

  // =========================================================================
  // 6. Property watchers
  // =========================================================================
  @Watch('disabled')
  handleDisabledChange(isDisabled: boolean) {
    this.el.setAttribute('aria-disabled', String(isDisabled));
  }

  @Watch('type')
  @Watch('variant')
  checkPropValues(): void {
    validatePropValue(['button', 'submit', 'reset'], 'button', this.el as HTMLElement, 'type');
    validatePropValue(['primary', 'secondary'], 'primary', this.el as HTMLElement, 'variant');
  }

  // =========================================================================
  // 7. Event declarations
  // =========================================================================
  /** Emitted when button is clicked */
  @Event() bdsClick: EventEmitter<HTMLElement>;

  /** Emitted when button receives focus */
  @Event() bdsFocus: EventEmitter<HTMLElement>;

  // =========================================================================
  // 8. Constructor (only if needed)
  // =========================================================================
  constructor() {
    this.handleClick = this.handleClick.bind(this);
  }

  // =========================================================================
  // 9. Lifecycle methods (execution order)
  // =========================================================================
  connectedCallback() {
    this.el.addEventListener('mousedown', this.handleMouseDown);
  }

  componentWillLoad() {
    this.checkPropValues();
  }

  disconnectedCallback() {
    this.el.removeEventListener('mousedown', this.handleMouseDown);
  }

  // =========================================================================
  // 10. Event listeners
  // =========================================================================
  @Listen('focus')
  onFocus() {
    this.bdsFocus.emit(this.el);
  }

  // =========================================================================
  // 11. Event handlers (alphabetical)
  // =========================================================================
  private handleClick = (event: MouseEvent) => {
    if (this.disabled) {
      event.preventDefault();
      return;
    }
    this.bdsClick.emit(this.el);
  }

  private handleMouseDown = () => {
    this.pressed = true;
    setTimeout(() => this.pressed = false, 200);
  }

  // =========================================================================
  // 12. Public methods (alphabetical, async)
  // =========================================================================
  async setFocus() {
    this.el.focus();
  }

  // =========================================================================
  // 13. Internal methods (alphabetical)
  // =========================================================================
  private getAriaLabel(): string {
    return this.disabled ? 'Disabled button' : undefined;
  }

  // =========================================================================
  // 14. Render helpers (alphabetical)
  // =========================================================================
  private renderIcon() {
    return <slot name="icon" />;
  }

  // =========================================================================
  // 15. Render method (always last)
  // =========================================================================
  render() {
    return (
      <Host>
        <button
          type={this.type}
          disabled={this.disabled}
          class={{
            'button': true,
            [`button--${this.variant}`]: true,
            'button--pressed': this.pressed,
          }}
          onClick={this.handleClick}
        >
          {this.renderIcon()}
          <slot />
        </button>
      </Host>
    );
  }
}
```

#### Enforcement Approaches

In order to enforce consistent code organization across the component library, the following approaches can be combined to ensure compliance at different stages of development:

| Approach                | Description                                          | Example                                                  | Benefits                                                                                                                                 |
| ----------------------- | ---------------------------------------------------- | -------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| **ESLint Rules**        | Automated linting rules that enforce member ordering | `"@typescript-eslint/member-ordering": ["error", {...}]` | - Automated checking in IDE and CI/CD<br/>- Auto-fix capability<br/>- Immediate feedback to developers<br/>- See Section 2.1 for details |
| **Component Templates** | CLI generators with pre-ordered structure            | `pnpm generate:component`                                | - Developers start with correct structure<br/>- Reduces manual setup<br/>- Consistent boilerplate                                        |
| **Pre-commit Hooks**    | Run linting before commits to block violations       | `husky` + `lint-staged` on `*.ts` files                  | - Prevents bad code from being committed<br/>- Forces compliance automatically<br/>- See Section 8.1 (Pre-commit Hooks)                  |
| **Code Snippets**       | IDE snippets for common patterns                     | VS Code snippets for component sections                  | - Quick insertion of properly ordered sections<br/>- Low overhead, no tooling needed<br/>- Developer convenience                         |

**Recommended Approach:**

Combine all approaches for maximum effectiveness:

1. **ESLint rules** as primary enforcement (catches violations automatically)
2. **Component templates** for new component creation (starts developers on the right path)
3. **Pre-commit hooks** as safety net (prevents violations from being committed)
4. **Code snippets** for developer convenience (speeds up development)

#### Rationale

Consistent code organization provides several benefits:

1. **Predictability** — Developers know exactly where to find specific members
2. **Faster Code Reviews** — Reviewers can quickly scan organized code
3. **Easier Navigation** — Jump to sections without scrolling through entire file
4. **Reduced Cognitive Load** — No mental overhead deciding where to place code
5. **Better Diffs** — Changes appear in logical sections, easier to understand in PRs
6. **Onboarding** — New developers learn structure once, apply everywhere
7. **Tool Support** — Linters and IDEs can enforce and auto-fix violations
8. **Consistency** — All components look similar, reducing surprises

#### Automated Component Generation

Component generators ensure CEM-compliant boilerplate from the start, reduce manual documentation errors, and maintain consistency across the codebase.

**Recommended Tools:**

| Tool                  | Template Engine | Customization         | Maintenance   | Best For                                  |
| --------------------- | --------------- | --------------------- | ------------- | ----------------------------------------- |
| **Plop.js** (Current) | Handlebars      | High (custom helpers) | Active (2025) | CEM-compliant templates, custom workflows |

**Plop.js Setup (Recommended):**

Plop.js offers the most flexibility with custom helpers and has active maintenance. It's ideal for creating CEM-compliant component templates.

```bash
pnpm add -D plop
```

**`plopfile.mjs`:**

```javascript
export default function (plop) {
  plop.setGenerator("component", {
    description: "Create a new Stencil component with CEM documentation",
    prompts: [
      {
        type: "input",
        name: "name",
        message: "Component name (e.g., my-button):",
      },
    ],
    actions: [
      {
        type: "add",
        path: "src/components/{{kebabCase name}}/{{kebabCase name}}.tsx",
        templateFile: "plop-templates/component.hbs",
      },
    ],
  });
}
```

**Usage:**

```bash
pnpm generate:component
```

The generator prompts for the component name, then scaffolds the full file structure: `*.tsx`, `*.scss`, `*.spec.tsx`, `*.stories.ts`, `*.mdx`, and type files. Run from the workspace root.

**Benefits:**

- Consistent component structure across the project
- CEM-compliant JSDoc documentation included by default
- Faster development workflow (30+ minutes saved per component)
- Reduced documentation errors and omissions

**See Also:** Section 5.6 for complete CEM documentation standards.

---

#### CEM-Compliant JSDoc Documentation

The Custom Elements Manifest (CEM) analyzer extracts component metadata from JSDoc comments to generate machine-readable documentation. All components must include comprehensive JSDoc annotations to ensure accurate manifest generation.

**Reference:** [Stencil — Generating Documentation in CEM format](https://stenciljs.com/docs/docs-custom-elements-manifest)

##### How the CEM is Generated

Stencil uses the `docs-custom-elements-manifest` output target (configured in `stencil.config.ts`). This runs the CEM analyzer with the Stencil plugin, which reads decorators directly from the TypeScript AST.

| Source                         | What the plugin generates automatically                                                                                          |
| ------------------------------ | -------------------------------------------------------------------------------------------------------------------------------- |
| `@Prop()` decorator            | `attributes[]` entry (kebab-case name) + `members[]` entry (camelCase name), with type, default, `readonly`, and cross-reference |
| Inline `/** */` on `@Prop()`   | `description` field in both entries                                                                                              |
| `@Event()` decorator           | `events[]` entry                                                                                                                 |
| Inline `/** */` on `@Event()`  | `description` field in the event entry                                                                                           |
| `@Method()` decorator          | `members[]` method entry                                                                                                         |
| Inline `/** */` on `@Method()` | `description` field                                                                                                              |
| `@slot` in class JSDoc         | `slots[]` entry                                                                                                                  |
| `@prop` comment in SCSS        | `cssProperties[]` entry                                                                                                          |

##### Core Rules

- **Every `@Prop()` must have inline JSDoc** (`/** */`) directly above the decorator — this is enforced by `stencil/required-jsdoc: 'error'`.
- **Do not use `@attr`, `@property`, `@fires`, `@summary`, `@method`, or `@element`** in the class-level JSDoc block. The Stencil plugin generates all of these from decorators. These tags are redundant and produce no additional output.
- **Do not use `@cssprop` in the TSX class JSDoc.** CSS custom properties must be documented with `@prop` comments in the SCSS file instead — that is where Stencil reads them from.
- **Do not use `@internal` on a component class JSDoc.** It silently removes the entire component from `custom-elements.json` and from generated React/Vue wrappers.
- **Use `@file` (not `@fileoverview`)** for module-level documentation.
- **Do not use `@part` (CSS Shadow Parts).** This project uses light DOM — there is no shadow boundary and no `part` attribute.

##### What Belongs in the Class JSDoc Block

The class-level JSDoc block has exactly two responsibilities:

1. **Component description** — the first paragraph becomes the `description` field in the manifest. Keep it concise.
2. **`@slot` tags** — the only tag the Stencil plugin cannot infer from the render function. Document every slot.

```typescript
/**
 * Banner component for displaying important messages with status variants.
 *
 * @slot - Default slot for the banner body content.
 * @slot title - Slot for the banner title text.
 * @slot actions - Slot for action buttons or links.
 */
@Component({
  tag: "bds-banner",
  styleUrl: "bds-banner.scss",
})
export class BdsBanner { ... }
```

Nothing else. No `@attr`, `@property`, `@cssprop`, `@fires`, `@summary`, `@method`.

##### Module-Level JSDoc

```typescript
/**
 * @file Entry point for the component package.
 *
 * Use this file to export utilities and types only.
 */
```

##### Prop JSDoc

**Required for every `@Prop()`.** Place inline JSDoc directly above the decorator:

```typescript
/** Visual style variant. */
@Prop({ reflect: true }) readonly variant: BannerVariant = 'info';

/** Shows a close button that allows users to dismiss the banner. */
@Prop() readonly enableClose: boolean = false;

/** Internal mutable prop for component-controlled state. */
@Prop({ mutable: true }) idComponent: string = '';
```

**Notes:**

- `readonly` is mandatory for `@Prop()` declarations.
- If `mutable: true` is used, mutate internally with a narrow cast instead of `as any`.
- **Type annotation is only required when there is no default value.** TypeScript infers the type from the initializer (`disabled = false` → `boolean`). Explicit annotations are needed only for required props (`name!: string`) and optional props with no default (`formId?: string`).

##### Event JSDoc

**Required for every `@Event()`.** Place inline JSDoc directly above the decorator:

```typescript
/** Emitted when the user closes the banner. */
@Event()
bdsClose!: EventEmitter<void>;
```

**Event Naming Rules:**

- Use the `bds{Action}` prefixed camelCase naming convention.
- Use bare `@Event()` for consumer-facing events — no explicit options required (see ADR 0003).
- **Exception:** events caught by a parent component via `@Listen()` must use `@Event({ bubbles: true })`. `@Listen()` relies on bubbling — without it the event never reaches the parent's listener.
- Do not reuse native DOM event names (`click`, `change`, `input`, etc.).

**Event Emission Rules:**

Events must only be emitted in response to **user interactions**, not programmatic changes. This prevents infinite loops and keeps data flow predictable.

| Scenario                          | Emit? | Reason                                    |
| --------------------------------- | ----- | ----------------------------------------- |
| User clicks / types / selects     | ✅    | Direct user interaction                   |
| Property changed programmatically | ❌    | Not user-initiated; emitting causes loops |
| Public `@Method()` called         | ❌    | API call, not a user action               |
| Internal state update             | ❌    | Implementation detail                     |
| Initialization / lifecycle hooks  | ❌    | Framework lifecycle, not a user action    |

**Cancelable Events:**

Cancelable events use the `-ing` suffix (before the action) paired with a plain name (after the action).

```typescript
/** Emitted before the dialog opens. Call `event.preventDefault()` to cancel. */
@Event({ cancelable: true })
bdsOpening!: EventEmitter<void>;

/** Emitted after the dialog has opened. */
@Event()
bdsOpen!: EventEmitter<void>;
```

Inside the handler, check `defaultPrevented` before proceeding:

```typescript
async open() {
  const event = this.bdsOpening.emit();
  if (event.defaultPrevented) return;
  this.isOpen = true;
  this.bdsOpen.emit();
}
```

| Event pair   | Cancelable | Suffix | When emitted                   |
| ------------ | ---------- | ------ | ------------------------------ |
| `bdsOpening` | ✅         | `ing`  | Before action (can be stopped) |
| `bdsOpen`    | ❌         | —      | After action (already done)    |
| `bdsClosing` | ✅         | `ing`  | Before action (can be stopped) |
| `bdsClose`   | ❌         | —      | After action (already done)    |

**Event Detail Typing:**

| Pattern             | When to use                 | Example                                                                            |
| ------------------- | --------------------------- | ---------------------------------------------------------------------------------- |
| Simple primitive    | Single scalar value         | `EventEmitter<string>`                                                             |
| Inline object       | Two or three related fields | `EventEmitter<{ id: string; label: string }>`                                      |
| Named interface     | Reusable or complex payload | `EventEmitter<SelectDetail>`                                                       |
| Element reference   | Exposing the source element | `EventEmitter<HTMLElement>`                                                        |
| Discriminated union | Multiple event variants     | `EventEmitter<{ type: 'success'; data: T } \| { type: 'error'; message: string }>` |

Only include relevant data in the detail — do not serialize the entire component state.

##### Method JSDoc

**Required for every `@Method()`.** Place inline JSDoc directly above the decorator:

```typescript
/**
 * Programmatically close the banner and emit `bdsBannerClose`.
 */
@Method()
async closeBanner(): Promise<void> {
  this.handleClose();
}
```

Do not add `@method` tags at the class level.

##### CSS Custom Properties — Document in SCSS, Not in TSX

Stencil reads CSS custom property documentation from `@prop` JSDoc comments **in the SCSS file**, not from `@cssprop` tags in the component class JSDoc. The comment must appear above the variable **declaration** inside the component's tag selector block.

```scss
/* ✅ Correct — Stencil reads this and generates cssProperties[] in the manifest */
bds-dialog {
  /**
   * @prop --bds-dialog-width: Custom width when no preset size is active.
   * @prop --bds-dialog-height: Custom height when no preset size is active.
   */
  --bds-dialog-width: auto;
  --bds-dialog-height: auto;
}
```

```typescript
/* ❌ Wrong — @cssprop in the TSX class JSDoc produces nothing in the manifest */
/**
 * @cssprop --bds-dialog-width - Custom width for the dialog.
 */
@Component({ tag: 'bds-dialog' })
export class BdsDialog { ... }
```

**Additional rules:**

- Declare the variable with its default value in the same block as the `@prop` comment. Do not scatter defaults as fallback values in `var(--name, default)` calls elsewhere.
- Internal implementation variables (e.g. `--_col-base`, `--_row-span`) must use the `--_` underscore prefix convention and must **not** have `@prop` documentation — they are not public API.

##### Complete Example

```typescript
/**
 * Checkbox component for boolean selection with three visual states.
 *
 * @slot - Label content when no `label` prop is provided.
 */
@Component({
  tag: "bds-checkbox",
  styleUrl: "bds-checkbox.scss",
  formAssociated: true,
})
export class BdsCheckbox {
  /** Whether the checkbox is selected. */
  @Prop({ mutable: true, reflect: true }) checked: boolean = false;

  /** Whether the checkbox is indeterminate. */
  @Prop({ mutable: true, reflect: true }) indeterminate: boolean = false;

  /** Value submitted with the form when checked. */
  @Prop() readonly value: string = "on";

  /** Label displayed next to the checkbox. */
  @Prop() readonly label: string = "";

  /** Emitted when the checked state changes (for 2-way binding / v-model). */
  @Event()
  bdsChange!: EventEmitter<{ checked: boolean; value: string }>;
}
```

##### Common Pitfalls to Avoid

- ❌ Using `@element`, `@method`, or class-level `@internal`.
- ❌ Omitting JSDoc on `@Prop()` or placing it below the decorator.
- ❌ Using `@fileoverview` instead of `@file`.
- ❌ Adding explicit `bubbles/composed/cancelable` to `@Event()` — bare `@Event()` is the convention.
- ❌ Naming events with native DOM names (`click`, `input`, `change`).
- ❌ Writing `@cssprop` in the TSX class JSDoc — use `@prop` in the SCSS file instead.
- ❌ Writing `@attr` or `@property` in the class JSDoc — the Stencil plugin generates both from `@Prop()` decorators.
- ❌ Documenting internal `--_*` CSS variables with `@prop` — they are not public API.
- ❌ Using fallback values in `var(--custom-prop, default)` instead of declaring the variable with its default in the tag selector block.

**See Also:** Section 5.6 for complete CEM setup, configuration, and integration with Storybook and IDEs.

---

### 1.4 Properties & Attributes

Properties and attributes define the public API for configuring component behavior and appearance. While naming conventions are covered in Section 1.2, this section focuses on property behavior—including reflection strategies, type handling, validation patterns, mutability, and reactive change handling.

#### Property Reflection Strategy

Property reflection controls whether property values sync back to HTML attributes. Reflection should be used sparingly for performance and only when necessary.

**When to Reflect:**

| Use Case                 | Reason                                                  | Example                          |
| ------------------------ | ------------------------------------------------------- | -------------------------------- |
| Accessibility attributes | Screen readers and assistive technology read attributes | `disabled`, `aria-label`, `role` |
| CSS styling selectors    | Allows CSS to style based on state                      | `variant`, `size`, `open`        |
| Simple primitive state   | Visual debugging in DevTools                            | `active`, `selected`             |

**When NOT to Reflect:**

| Use Case                        | Reason                                     | Example                    |
| ------------------------------- | ------------------------------------------ | -------------------------- |
| Complex objects/arrays          | Performance overhead, serialization issues | `data`, `config`, `items`  |
| Frequently changing values      | Excessive DOM updates                      | `currentValue`, `progress` |
| Internal implementation details | Not part of public API                     | `_cache`, `_state`         |

**Implementation:**

```typescript
// ✅ GOOD - Reflect primitives for a11y/styling
@Prop({ reflect: true }) disabled = false;
@Prop({ reflect: true }) variant: 'primary' | 'secondary' = 'primary';
@Prop({ reflect: true }) size: 'small' | 'medium' | 'large' = 'medium';

// ✅ GOOD - Don't reflect complex types
@Prop() data: Array<Item> = [];
@Prop() config: Configuration;

// ✅ GOOD - Don't reflect frequently changing values
@Prop() value: string;  // No reflect for input values
```

**Performance Note:** Every reflected property triggers a DOM mutation. Limit reflection to properties that genuinely need attribute sync.

#### Property Types & Coercion

Properties accept different types with specific coercion behavior:

| Type      | HTML Attribute Type | Coercion Behavior           | Example                             |
| --------- | ------------------- | --------------------------- | ----------------------------------- |
| `String`  | String              | Direct assignment           | `@Prop() label: string`             |
| `Number`  | String → Number     | Parsed via `Number()`       | `@Prop() count: number = 0`         |
| `Boolean` | Presence-based      | Attribute presence = `true` | `@Prop() disabled: boolean = false` |
| `Object`  | JSON string         | Parsed via `JSON.parse()`   | `@Prop() config: Config`            |
| `Array`   | JSON string         | Parsed via `JSON.parse()`   | `@Prop() items: Item[]`             |

**Type Inference and Default Values:**

When a prop has a default value, TypeScript infers its type automatically — no explicit annotation is needed:

```typescript
@Prop({ reflect: true }) readonly disabled = false;         // inferred boolean
@Prop({ reflect: true }) readonly orientation = 'vertical'; // inferred string
```

When there is no default, the type must be declared explicitly:

```typescript
@Prop({ reflect: true }) readonly name!: string;   // required, no default
@Prop({ reflect: true }) readonly formId?: string; // optional, no default
```

**Critical Rule: Never Use Constants as Default Values**

Always use string literals as default values — never constant or enum references. Stencil resolves `@Prop()` defaults at static analysis time (AST level). If you write `= ORIENTATIONS.VERTICAL`, the compiler records the identifier `ORIENTATIONS.VERTICAL` in `custom-elements.json` instead of the actual value `'vertical'`. This leaks internal implementation details into Storybook ArgTypes and consumer IDEs.

```typescript
// ✅ Correct — CEM records 'vertical'
@Prop() readonly orientation: Orientation = 'vertical';

// ❌ Wrong — CEM records 'ORIENTATIONS.VERTICAL'
@Prop() readonly orientation: Orientation = ORIENTATIONS.VERTICAL;
```

Constants may be used in logic (switch cases, class maps, `validatePropValue`) — just never as the `@Prop()` initializer.

**When to Use Default Values:**

| Use Case                | When to Use Default                      | When NOT to Use Default                                                    |
| ----------------------- | ---------------------------------------- | -------------------------------------------------------------------------- |
| **Behavioral props**    | Has sensible "off" state                 | —                                                                          |
| **Identity data**       | —                                        | `name!: string`, `value!: string` — required for form submission           |
| **Optional context**    | —                                        | `formId?: string` — `undefined` has meaning (no form association)          |
| **State toggles**       | `disabled = false`, `required = false`   | —                                                                          |
| **Component variants**  | `variant = 'primary'`, `size = 'medium'` | —                                                                          |
| **Optional references** | —                                        | `required?: boolean` — absence means not required, not the same as `false` |

**Rule of Thumb:**

| Declaration        | Meaning                                                            |
| ------------------ | ------------------------------------------------------------------ |
| `name!: string`    | Required, no default — component cannot function without it        |
| `formId?: string`  | Optional, no default — `undefined` is a valid and meaningful value |
| `disabled = false` | Has default — behavioral, always a valid fallback                  |

#### Property Validation

For any enum-typed `@Prop()` (variant, size, type, color, etc.), use the shared `validatePropValue` utility from `@/utils/helpers/validateProps` combined with stacked `@Watch()` decorators on a single `checkPropValues()` method. Always call `checkPropValues()` in `componentWillLoad()` — `@Watch()` alone does not fire for the initial attribute value set via an HTML attribute before the component mounts. Without the `componentWillLoad()` call, an invalid attribute on the initial render is silently accepted.

```typescript
import { Component, Element, Prop, Watch, h } from "@stencil/core";
import { validatePropValue } from "@/utils/helpers/validateProps";
import { BUTTON_TYPES, BUTTON_VARIANTS, BUTTON_SIZES } from "./types/enum";
import { ButtonTypes, ButtonVariant, ButtonSizes } from "./types/types";

@Component({ tag: "bds-button", styleUrl: "bds-button.scss" })
export class BdsButton {
  @Element() el!: HTMLBdsButtonElement;

  @Prop() readonly type: ButtonTypes = "button";
  @Prop() readonly variant: ButtonVariant = "default";
  @Prop() readonly size: ButtonSizes = "medium";

  // Section 6 — Property Watchers
  @Watch("type")
  @Watch("variant")
  @Watch("size")
  checkPropValues(): void {
    validatePropValue(
      Object.values(BUTTON_TYPES) as ButtonTypes[],
      "button",
      this.el as HTMLElement,
      "type",
    );
    validatePropValue(
      Object.values(BUTTON_VARIANTS) as ButtonVariant[],
      "default",
      this.el as HTMLElement,
      "variant",
    );
    validatePropValue(
      Object.values(BUTTON_SIZES) as ButtonSizes[],
      "medium",
      this.el as HTMLElement,
      "size",
    );
  }

  // Section 9 — Lifecycle methods
  componentWillLoad(): void {
    this.checkPropValues();
  }
}
```

**`validatePropValue` signature:**

```ts
validatePropValue<T extends string>(
  acceptedValues: readonly T[],
  fallbackValue: T,
  element: HTMLElement,
  propertyName: string,
): void
```

When the current prop value is not in `acceptedValues`, the utility resets `element[propertyName]` to `fallbackValue` and issues a `console.warn` naming the component tag, the invalid value, and the full list of valid options. This is a **mutation strategy** — after `checkPropValues()` returns, all validated props are guaranteed to hold a valid value.

**Rules:**

| Rule                           | Detail                                                                             |
| ------------------------------ | ---------------------------------------------------------------------------------- |
| Use `Object.values(ENUM)`      | Keeps the accepted-values array in sync with the enum automatically                |
| Pass `this.el as HTMLElement`  | Keeps `validatePropValue` generic — avoid casting to a specific element type       |
| No inline literals             | Enum values are the single source of truth; do not duplicate them as string arrays |
| `checkPropValues` in section 6 | The method carries `@Watch()` decorators so it belongs with Property Watchers      |
| Call in `componentWillLoad()`  | Required to cover the initial render — `@Watch()` alone does not fire on mount     |

#### Property Mutability

By default, properties are immutable (read-only from within the component). Use `mutable: true` only when the component needs to modify its own prop value.

**`mutable: true` on `disabled` produces a Stencil compiler warning — use a `@State()` mirror instead.**
`disabled` is a native reflected HTML attribute with browser-managed semantics (controlled externally via `formDisabledCallback`). Marking it `mutable: true` creates two writers on the same reflected attribute — the component and the browser — which can race. The `stencil/strict-mutable` ESLint rule flags every `mutable: true` as a warning on every build; this is intentional and accepted for other props that require internal mutation, but `disabled` is the one case where the `@State()` mirror is always preferred:

```typescript
/** Whether the component is disabled. */
@Prop({ reflect: true }) readonly disabled: boolean = false;
@State() private isDisabled: boolean = false;

@Watch('disabled')
onDisabledChange(next: boolean): void { this.isDisabled = next; }

componentWillLoad(): void { this.isDisabled = this.disabled; }

// In FACE components: also update via formDisabledCallback
formDisabledCallback(disabled: boolean): void { this.isDisabled = disabled; }
```

Render and toggle logic reads `this.isDisabled`. `@Prop()` remains `readonly` and externally owned.

**Never use constant references as `@Prop()` default values.** Stencil resolves `@Prop()` defaults at static analysis time (AST level). If you write `= ORIENTATIONS.VERTICAL`, the compiler records the identifier `ORIENTATIONS.VERTICAL` in `custom-elements.json` instead of the actual string `'vertical'`. This leaks internal implementation details into Storybook ArgTypes and consumer IDEs.

```typescript
// ✅ Correct — CEM records 'vertical'
@Prop() readonly orientation: Orientation = 'vertical';

// ❌ Wrong — CEM records 'ORIENTATIONS.VERTICAL'
@Prop() readonly orientation: Orientation = ORIENTATIONS.VERTICAL;
```

Constants may be used in logic (switch cases, class maps, `validatePropValue`) — just never as the `@Prop()` initializer.

**When to Use `mutable: true`:**

| Use Case                     | Reason                                     | Example                          |
| ---------------------------- | ------------------------------------------ | -------------------------------- |
| Controlled component pattern | Component normalizes/constrains values     | Input clamping values to min/max |
| Value normalization          | Component formats or validates input       | Formatting phone numbers         |
| Internal state sync          | Prop acts as both input and internal state | Accordion open state             |

**When NOT to Use `mutable: true`:**

| Use Case                 | Reason                               | Alternative            |
| ------------------------ | ------------------------------------ | ---------------------- |
| General state management | Props should be inputs, not state    | Use `@State()` instead |
| Temporary values         | Props are for external configuration | Use private properties |
| Computed values          | Derived from other properties        | Use getters            |

**Implementation:**

```typescript
// ✅ GOOD - Mutable for value normalization
@Prop({ mutable: true }) value: number = 0;

@Watch('value')
handleValueChange(newValue: number) {
  // Clamp value between min and max
  if (newValue < this.min) {
    this.value = this.min;
  } else if (newValue > this.max) {
    this.value = this.max;
  }
}

// ❌ BAD - Don't use mutable for internal state
@Prop({ mutable: true }) isOpen: boolean = false;  // Use @State instead

// ✅ GOOD - Use @State for internal state
@State() private isOpen: boolean = false;
```

#### Watch Decorators Pattern

`@Watch` decorators run when specific properties change. Use them for validation, side effects, or syncing state.

**Watch Pattern:**

```typescript
import { Prop, Watch } from "@stencil/core";

export class MyComponent {
  @Prop() disabled: boolean = false;

  @Watch("disabled")
  handleDisabledChange(newValue: boolean, oldValue: boolean) {
    // Update accessibility attributes
    this.el.setAttribute("aria-disabled", String(newValue));

    // Clear focus if disabled
    if (newValue && !oldValue) {
      this.el.blur();
    }
  }

  @Prop() value: string = "";

  @Watch("value")
  handleValueChange(newValue: string, oldValue: string) {
    // Emit change event
    this.bdsChange.emit({ value: newValue, previousValue: oldValue });

    // Validate new value
    this.validateValue(newValue);
  }
}
```

**Watch Best Practices:**

| Practice                      | Description                                       | Example                                         |
| ----------------------------- | ------------------------------------------------- | ----------------------------------------------- |
| **Name handlers clearly**     | Use `handle[PropName]Change` pattern              | `handleDisabledChange`, `handleValueChange`     |
| **Check old vs new**          | Avoid unnecessary work if value hasn't changed    | `if (newValue !== oldValue) { ... }`            |
| **Keep handlers focused**     | One responsibility per handler                    | Separate validation from event emission         |
| **Avoid infinite loops**      | Don't set the watched property inside its handler | Watch `value`, don't set `value` inside handler |
| **Use for side effects only** | Don't use for computed values (use getters)       | Update ARIA attributes, emit events             |

#### Common Patterns

**Pattern 1: Controlled vs Uncontrolled**

```typescript
// Controlled component (value managed externally)
@Prop() value: string;
@Event() bdsChange: EventEmitter<string>;

private handleInput(event: InputEvent) {
  const newValue = (event.target as HTMLInputElement).value;
  this.bdsChange.emit(newValue);  // Emit, don't update prop
}

// Uncontrolled component (internal state)
@State() private internalValue: string = '';
@Prop() defaultValue: string = '';

componentWillLoad() {
  this.internalValue = this.defaultValue;
}
```

**Pattern 2: Property with Fallback**

```typescript
@Prop() customLabel?: string;

get effectiveLabel(): string {
  return this.customLabel ?? 'Default Label';
}
```

**Pattern 3: Required Properties**

```typescript
@Prop() name!: string;  // TypeScript non-null assertion

componentWillLoad() {
  if (!this.name) {
    console.error('[my-component] Required property "name" is missing.');
  }
}
```

#### Rationale

Proper property design ensures:

1. **Performance** — Limiting reflection reduces DOM mutations
2. **Type Safety** — Explicit types prevent runtime errors
3. **Developer Experience** — Clear validation messages help debug issues
4. **Predictability** — Controlled mutability prevents unexpected behavior
5. **Maintainability** — Consistent patterns reduce cognitive load
6. **Accessibility** — Reflected properties enable assistive technology
7. **Framework Compatibility** — Well-designed properties work across frameworks

#### Component Interface Contract

`IComponent.ts` interfaces describe only what the **consumer configures** — the set of publicly settable `@Prop()` members.

The following must **not** be in `IComponent.ts`:

- **`@Event()` outputs** — `EventEmitter<T>` members are declared on the class body and documented via JSDoc. Adding them to the interface forces the type to reference an internal abstraction consumers never set.
- **Group-propagated props** — props the parent group component writes imperatively (e.g. `name`, `showDivider`, `isFirst`) are parent-child coordination details, not consumer API.
- **`@State()` mirrors** — internal reactive state (`isDisabled`, `isOpen`) is never part of the public API.

**Interface members must be optional when the prop has a default value.** A required interface member implies the consumer must always supply it explicitly. With optional members, bare-attribute patterns (`<bds-radio-group disabled>`) work as expected in React and HTML.

```typescript
// ✅ Correct — props with component-side defaults are optional in the interface
export interface IRadioGroup {
  name: string; // no default on component — required
  value?: string; // default = ''
  disabled?: boolean; // default = false
}

// ❌ Wrong — disabled has a default; marking it required is misleading
export interface IRadioGroup {
  name: string;
  disabled: boolean; // forces consumer to always pass disabled={false}
}
```

### 1.5 Custom Events

Custom events enable components to communicate state changes and user interactions to parent contexts. While event naming is covered in Section 1.2, this section focuses on event behavior—including emission patterns, event detail typing, bubbling/composition, cancelable events, and common event patterns.

#### Event Emission Rules

Events should only be emitted in response to **user interactions**, not programmatic changes. This prevents infinite loops and maintains predictable behavior.

**When to Emit Events:**

| Scenario                        | Emit Event? | Reason                      | Example                                  |
| ------------------------------- | ----------- | --------------------------- | ---------------------------------------- |
| User clicks button              | ✅ Yes      | Direct user interaction     | `bdsClick` event on button click         |
| User types in input             | ✅ Yes      | Direct user interaction     | `bdsInput` event on keystroke            |
| User selects option             | ✅ Yes      | Direct user interaction     | `bdsChange` event on selection           |
| Component opens via user action | ✅ Yes      | User-triggered state change | `bdsOpen` event after user clicks toggle |

**When NOT to Emit Events:**

| Scenario                          | Emit Event? | Reason                               | Example                                          |
| --------------------------------- | ----------- | ------------------------------------ | ------------------------------------------------ |
| Property changed programmatically | ❌ No       | Not user-initiated                   | Don't emit `bdsChange` when `value` prop changes |
| Public method called              | ❌ No       | API call, not user action            | Don't emit `bdsOpen` when `open()` method called |
| Internal state update             | ❌ No       | Implementation detail                | Don't emit on internal state changes             |
| Initialization/lifecycle          | ❌ No       | Framework lifecycle, not user action | Don't emit on `componentWillLoad`                |

**Implementation:**

```typescript
import { Event, EventEmitter, Method } from "@stencil/core";

export class MyComponent {
  @Event() bdsChange: EventEmitter<string>;

  // ✅ GOOD - Emit on user interaction
  private handleInputChange(event: InputEvent) {
    const value = (event.target as HTMLInputElement).value;
    this.bdsChange.emit(value);
  }

  // ❌ BAD - Don't emit on property change
  @Prop() value: string;

  @Watch("value")
  handleValueChange(newValue: string) {
    // ❌ Don't do this
    // this.bdsChange.emit(newValue);
  }

  // ❌ BAD - Don't emit on public method call
  @Method()
  async setValue(value: string) {
    this.value = value;
    // ❌ Don't do this
    // this.bdsChange.emit(value);
  }
}
```

**Rationale:**

| Rule                        | Benefit                                                                 |
| --------------------------- | ----------------------------------------------------------------------- |
| User interaction only       | Prevents infinite loops when parent updates props in response to events |
| No emission on prop changes | Maintains unidirectional data flow (props down, events up)              |
| No emission on method calls | API calls are already programmatic; emitting creates redundancy         |
| Predictable behavior        | Developers can trust events represent user actions                      |

#### Event Detail Typing

Event detail payloads should be strongly typed to provide clear contracts and enable type safety.

**Event Detail Patterns:**

```typescript
import { Event, EventEmitter } from '@stencil/core';

// Pattern 1: Simple value
@Event() bdsChange: EventEmitter<string>;

this.bdsChange.emit('new-value');

// Pattern 2: Object with multiple values
@Event() bdsSelect: EventEmitter<{ id: string; label: string }>;

this.bdsSelect.emit({ id: '123', label: 'Option 1' });

// Pattern 3: Event with metadata
@Event() bdsValidate: EventEmitter<{
  value: string;
  isValid: boolean;
  errors: string[];
}>;

this.bdsValidate.emit({
  value: 'test@example.com',
  isValid: true,
  errors: []
});

// Pattern 4: Element reference
@Event() bdsClick: EventEmitter<HTMLElement>;

this.bdsClick.emit(this.el);

// Pattern 5: Custom type
interface SubmitDetail {
  formData: Record<string, unknown>;
  timestamp: number;
  source: 'user' | 'api';
}

@Event() bdsSubmit: EventEmitter<SubmitDetail>;

this.bdsSubmit.emit({
  formData: { name: 'John' },
  timestamp: Date.now(),
  source: 'user'
});
```

**Type Definition Best Practices:**

| Practice                               | Description                                     | Example                                                              |
| -------------------------------------- | ----------------------------------------------- | -------------------------------------------------------------------- |
| **Use interfaces for complex details** | Define reusable types for event payloads        | `interface ChangeDetail { value: string; }`                          |
| **Include context when helpful**       | Add metadata that helps event handlers          | Previous value, validation state                                     |
| **Keep details focused**               | Only include relevant information               | Don't include entire component state                                 |
| **Use discriminated unions**           | Enable type narrowing for different event types | `{ type: 'success'; data: T } \| { type: 'error'; message: string }` |

#### Bubbling & Composition

Boreal DS uses **light DOM** (`shadow: false` or no `shadow` option). Because there is no shadow boundary, `composed: true` is irrelevant and `bubbles` is only needed when a parent component needs to delegate to a distant ancestor.

**Accepted convention: bare `@Event()`**

The project follows the same convention as BEEQ and Aqua DS — bare `@Event()` with no options. Consumers attach listeners directly to the component element; bubbling is not required. This is enforced by ADR 0003.

```typescript
// ✅ CORRECT — bare @Event() is the Boreal DS convention
@Event() bdsChange: EventEmitter<string>;

this.bdsChange.emit('new-value');

// Equivalent to:
this.dispatchEvent(new CustomEvent('bdsChange', {
  bubbles: false,
  composed: false,
  detail: 'new-value'
}));
```

**When to deviate:**

Add explicit options only when there is a documented architectural reason (e.g., a child-to-parent delegation pattern that requires bubbling). In that case, document the reason in a JSDoc comment on the `@Event()` line.

```typescript
// Explicit bubbles only when a parent component listens via event delegation
@Event({ bubbles: true }) bdsChange: EventEmitter<RadioChangeDetail>;
```

**Why `composed` is never needed:**

| Fact                                               | Implication                                            |
| -------------------------------------------------- | ------------------------------------------------------ |
| All components use light DOM                       | No shadow boundary to cross; `composed` has no effect  |
| Consumers listen on the component element directly | Bubbling is unnecessary for direct listeners           |
| Framework bindings (Vue, React) wrap the element   | They call `addEventListener` on the host, not a parent |

#### Cancelable Events Pattern

Cancelable events allow parent components to prevent default behavior. Use the `-ing` suffix pattern for cancelable lifecycle events (covered in Section 1.2).

**Cancelable Event Implementation:**

```typescript
import { Event, EventEmitter } from "@stencil/core";

export class BdsDialog {
  @State() private isOpen = false;

  // Cancelable event (before action)
  @Event({ cancelable: true }) bdsOpening: EventEmitter<void>;

  // Non-cancelable event (after action)
  @Event() bdsOpen: EventEmitter<void>;

  async open() {
    // Emit cancelable event before action
    const event = this.bdsOpening.emit();

    // Check if event was prevented
    if (event.defaultPrevented) {
      return; // Don't proceed
    }

    // Proceed with action
    this.isOpen = true;

    // Emit non-cancelable event after action
    this.bdsOpen.emit();
  }
}
```

**Consumer Usage:**

```html
<bds-dialog id="modal"></bds-dialog>

<script>
  const modal = document.getElementById("modal");

  // Prevent opening
  modal.addEventListener("bdsOpening", (event) => {
    if (someCondition) {
      event.preventDefault(); // Cancel the opening
    }
  });

  // React to opening (cannot prevent)
  modal.addEventListener("bdsOpen", () => {
    console.log("Dialog opened");
  });
</script>
```

**Cancelable Event Patterns:**

| Event Type      | Cancelable? | Suffix | When Emitted                          |
| --------------- | ----------- | ------ | ------------------------------------- |
| `bdsOpening`    | ✅ Yes      | `ing`  | Before action (can be prevented)      |
| `bdsOpen`       | ❌ No       | None   | After action (already happened)       |
| `bdsClosing`    | ✅ Yes      | `ing`  | Before action (can be prevented)      |
| `bdsClose`      | ❌ No       | None   | After action (already happened)       |
| `bdsSubmitting` | ✅ Yes      | `ing`  | Before form submit (can be prevented) |
| `bdsSubmit`     | ❌ No       | None   | After form submit (already happened)  |

#### Event Declaration Best Practices

**JSDoc Documentation:**

```typescript
export class MyComponent {
  /**
   * Emitted when the component value changes due to user interaction.
   * @event bdsChange
   */
  @Event() bdsChange: EventEmitter<string>;

  /**
   * Emitted before the component opens. Can be prevented by calling
   * `event.preventDefault()` to cancel the opening action.
   * @event bdsOpening
   */
  @Event({ cancelable: true }) bdsOpening: EventEmitter<void>;

  /**
   * Emitted when a selection is made.
   * @event bdsSelect
   */
  @Event() bdsSelect: EventEmitter<{
    /** The ID of the selected item */
    id: string;
    /** The label of the selected item */
    label: string;
  }>;
}
```

**Best Practices Table:**

| Practice                   | Description                              | Example                                        |
| -------------------------- | ---------------------------------------- | ---------------------------------------------- |
| **Document all events**    | Include JSDoc with clear description     | `@event bdsChange` tag                         |
| **Describe event detail**  | Explain payload structure and properties | Document each field in detail object           |
| **Note cancelable events** | Mention if/how event can be prevented    | "Can be prevented by calling preventDefault()" |
| **Specify trigger**        | Clarify what user action triggers event  | "Emitted when user clicks button"              |
| **Use consistent naming**  | Follow the `bds{Action}` pattern         | `bdsClick`, `bdsChange`, `bdsSubmit`           |

#### Common Event Patterns

**Form Events:**

```typescript
export class BdsTextField {
  @Event() bdsInput: EventEmitter<string>; // On each keystroke
  @Event() bdsChange: EventEmitter<string>; // On blur/enter
  @Event() bdsFocus: EventEmitter<void>; // On focus
  @Event() bdsBlur: EventEmitter<void>; // On blur

  private handleInput(event: InputEvent) {
    this.bdsInput.emit((event.target as HTMLInputElement).value);
  }

  private handleChange(event: Event) {
    this.bdsChange.emit((event.target as HTMLInputElement).value);
  }
}
```

**Lifecycle Events:**

```typescript
export class BdsDialog {
  @Event({ cancelable: true }) bdsOpening: EventEmitter<void>; // Cancelable
  @Event() bdsOpen: EventEmitter<void>; // Non-cancelable
  @Event({ cancelable: true }) bdsClosing: EventEmitter<void>; // Cancelable
  @Event() bdsClose: EventEmitter<void>; // Non-cancelable

  async open() {
    if (!this.bdsOpening.emit().defaultPrevented) {
      this.isOpen = true;
      this.bdsOpen.emit();
    }
  }

  async close() {
    if (!this.bdsClosing.emit().defaultPrevented) {
      this.isOpen = false;
      this.bdsClose.emit();
    }
  }
}
```

**Action Events:**

```typescript
export class BdsButton {
  @Event() bdsClick: EventEmitter<MouseEvent>;
  @Event() bdsFocus: EventEmitter<void>;

  private handleClick(event: MouseEvent) {
    if (!this.disabled) {
      this.bdsClick.emit(event);
    }
  }
}
```

**Selection Events:**

```typescript
export class BdsSelect {
  @Event() bdsSelect: EventEmitter<{ id: string; label: string }>;
  @Event() bdsDeselect: EventEmitter<{ id: string }>;

  private handleSelect(item: Item) {
    this.bdsSelect.emit({ id: item.id, label: item.label });
  }
}
```

#### Rationale

Proper event design ensures:

1. **Predictability** — Events represent user actions, not programmatic changes
2. **Framework Compatibility** — `valueChange` event wired to Vue `v-model` via `componentModels`
3. **Type Safety** — Typed event details catch errors at compile time
4. **Flexibility** — Cancelable events allow parent components to control behavior
5. **Debugging** — Clear event names and documentation aid troubleshooting
6. **Unidirectional Data Flow** — Props down, events up (standard pattern)
7. **Testability** — Predictable emission patterns make testing straightforward

---

### 1.6 Developing for Output Targets

Boreal DS ships framework output targets — currently **Vue** (via `@stencil/vue-output-target`) and **React** (via `@stencil/react-output-target`). Components built for the Web Components package must follow additional conventions so the generated framework wrappers work correctly.

#### Vue `v-model` Support

The Vue output target maps one `@Prop()` / `@Event()` pair to Vue's `v-model` directive per component. This is configured in `vue-output-target.ts` via the `componentModels` array.

**Registration requirement:**

Every form component that exposes a `value` prop **must** be registered in `componentModels` in the same PR as the component itself. Omitting registration means Vue consumers cannot use `v-model` on that component.

```typescript
// packages/boreal-web-components/targets/vue-output-target.ts
componentModels: [
  {
    elements: ['bds-text-field', 'bds-toggle', 'bds-checkbox', 'bds-radio-group'],
    event: 'valueChange',
    targetAttr: 'value',
  },
],
```

Multiple components sharing the same `event` + `targetAttr` pair can be listed together in one entry. The Vue proxy reads `$event.detail` directly from the flat primitive payload — no `eventAttr` field is needed.

**Form control interface layering:**

Three interface levels govern all Boreal DS form controls and must be implemented together:

| Interface                  | Location                   | Responsibility                                                                                         |
| -------------------------- | -------------------------- | ------------------------------------------------------------------------------------------------------ |
| `IFormAssociatedCallbacks` | `form-associated.mixin.ts` | Declares `formDisabledCallback`, `formResetCallback`, `formStateRestoreCallback` signatures            |
| `IFormValueEmitter<T>`     | `form-associated.mixin.ts` | Declares `valueChange: EventEmitter<T>` — enforces consistent event naming                             |
| `IFormControl<T>`          | `form-associated.mixin.ts` | Composite: `IFormAssociatedCallbacks & IFormValueEmitter<T>` — the single interface a class implements |

```typescript
export class BdsTextField
  extends Mixin(formAssociatedMixin)
  implements ITextField, IFormControl<string>
{
  @AttachInternals() internals!: ElementInternals;
  @Event() valueChange!: EventEmitter<string>;
}
```

The `componentModels` config in `vue-output-target.ts` **must land in the same PR** as the finished component. Never add it ahead of the component being complete — the Vue output target does not auto-generate `v-model` bindings from naming conventions.

**The `valueChange` event:**

All form components emit a dedicated `valueChange` event for Vue `v-model`. Use bare `@Event()` — no `bubbles` or `composed` options are needed because the project uses light DOM (see §1.5 and ADR 0003).

```typescript
// ✅ correct: bare @Event() with the reserved valueChange name
@Event() valueChange: EventEmitter<string>;

// ❌ avoid: adding options that are irrelevant in light DOM
@Event({ bubbles: true, composed: true }) valueChange: EventEmitter<string>;
```

> `valueChange` is reserved for Vue `v-model` integration. Use `bds{Action}` names for all other events (§1.2).

#### React Wrapper Compatibility

React wrappers are generated automatically from `@Prop()` and `@Event()` declarations. No additional registration is required; however:

- All `@Prop()` names should follow camelCase (the wrapper forwards them directly).
- `@Event()` names are forwarded as `on<EventName>` callback props (e.g., `bdsChange` → `onBdsChange`).

---

## 2. LINTING & FORMATTING STANDARDS

Code consistency is enforced through automated linting and formatting tools. These tools catch common errors before code review, maintain uniform code style across the entire codebase, and eliminate subjective style debates. All code must pass linting checks before being merged to ensure quality and readability.

### 2.1 ESLint Configuration

ESLint enforces code quality rules and catches common errors. The configuration uses ESLint's flat config format and extends recommended presets for Stencil and TypeScript projects.

**Required Dependencies:**

````bash
pnpm add -D @eslint/js typescript typescript-eslint @stencil/eslint-plugin eslint-plugin-jsdoc
```-

**Package-Level Configuration (`packages/boreal-web-components/eslint.config.ts`):**

Each package carries its own `eslint.config.ts`. The web-components config below is the canonical reference.

```typescript
// @ts-check
import { configs } from "@eslint/js";
import { defineConfig } from "eslint/config";
import tseslint from "typescript-eslint";
import stencil from "@stencil/eslint-plugin";
import jsdoc from "eslint-plugin-jsdoc";

export default defineConfig(
  configs.recommended,
  tseslint.configs.recommendedTypeChecked,
  stencil.configs.flat.recommended,
  {
    files: ["src/**/*.{ts,tsx}"],
  },
  {
    ignores: [
      "dist/",
      "www/",
      "coverage/",
      "targets",
      "components-build/",
      "loader",
      "scripts/",
      "eslint.config.ts",
      "stencil.config.ts",
      "src/**/*.d.ts",
      "*.config.ts",
      "*.config.mjs",
      "*.config.cjs",
    ],
  },
  {
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      parserOptions: {
        projectService: true,
        tsconfigRootDir: __dirname,
      },
    },
  },
  {
    plugins: { jsdoc },
    settings: {
      jsdoc: {
        tagNamePreference: {
          internal: false,
          ignore: false,
          function: "method",
          template: "typeParam",
        },
      },
    },
    rules: {
      "jsdoc/check-tag-names": [
        "error",
        {
          definedTags: [
            "slot",
            "csspart",
            "cssprop",
            "cssproperty",
            "cssState",
            "summary",
            "attr",
            "attribute",
            "fires",
            "event",
            "tag",
            "tagname",
            "default",
            "typeParam",
          ],
        },
      ],

      // TypeScript rules
      "@typescript-eslint/no-unused-vars": [
        "error",
        { argsIgnorePattern: "^_", varsIgnorePattern: "^_" },
      ],
      "@typescript-eslint/no-explicit-any": "warn",
      "@typescript-eslint/explicit-function-return-type": "off",
      "@typescript-eslint/no-unsafe-return": "off",
      "@typescript-eslint/require-await": "off",
      "@typescript-eslint/no-unused-expressions": [
        "warn",
        { allowTernary: true },
      ],

      // Stencil-specific rules
      "stencil/async-methods": "error",
      "stencil/ban-prefix": ["error", ["stencil", "stnl", "st"]],
      "stencil/decorators-context": "error",
      "stencil/decorators-style": [
        "error",
        {
          prop: "inline",
          state: "inline",
          element: "inline",
          event: "inline",
          method: "multiline",
          watch: "multiline",
          listen: "multiline",
        },
      ],
      "stencil/element-type": "error",
      "stencil/host-data-deprecated": "error",
      "stencil/methods-must-be-public": "error",
      "stencil/no-unused-watch": "error",
      "stencil/own-methods-must-be-private": "error",
      "stencil/own-props-must-be-private": "error",
      "stencil/prefer-vdom-listener": "error",
      "stencil/props-must-be-public": "error",
      "stencil/props-must-be-readonly": "error",
      "stencil/render-returns-host": "error",
      "stencil/required-jsdoc": "error",
      "stencil/reserved-member-names": "error",
      "stencil/single-export": "error",
      "stencil/strict-mutable": "warn",
      "stencil/strict-boolean-conditions": "warn",
      "react/jsx-no-bind": "off",
    },
  },
  {
    // Test files — relaxed rules
    files: ["**/*.test.{ts,tsx}", "**/*.spec.{ts,tsx}"],
    rules: {
      "@typescript-eslint/no-explicit-any": "off",
      "@typescript-eslint/no-unsafe-assignment": "off",
      "@typescript-eslint/no-unsafe-member-access": "off",
      "@typescript-eslint/no-unsafe-call": "off",
      "@typescript-eslint/no-unnecessary-type-assertion": "off",
      "@typescript-eslint/unbound-method": "off",
      "stencil/strict-boolean-conditions": "off",
    },
  },
  {
    // Type definition files
    files: ["**/*.d.ts"],
    rules: {
      "@typescript-eslint/no-unused-vars": "off",
      "stencil/strict-boolean-conditions": "off",
    },
  },
  {
    // Mixin files — constructors require `...args: any[]` to forward to the base class
    files: ["**/mixins/**/*.ts"],
    rules: {
      "@typescript-eslint/no-explicit-any": "off",
      "@typescript-eslint/no-unsafe-argument": "off",
    },
  },
  {
    // Component type files — enforce named exports only
    files: ["src/**/types/*.ts"],
    rules: {
      "no-restricted-syntax": [
        "error",
        {
          selector: "ExportDefaultDeclaration",
          message:
            "Default exports are forbidden in component type files. Use named exports so Stencil's declaration generator can resolve them in components.d.ts.",
        },
      ],
    },
  },
);
````

**Key Rules Explained:**

| Rule                                  | Enforcement | Rationale                                                                                       |
| ------------------------------------- | ----------- | ----------------------------------------------------------------------------------------------- |
| `stencil/async-methods`               | Error       | Ensures all public `@Method()` are async                                                        |
| `stencil/ban-prefix`                  | Error       | Prevents `stencil`, `stnl`, `st` prefixes on component tags                                     |
| `stencil/decorators-context`          | Error       | Validates decorators are used in the correct context                                            |
| `stencil/decorators-style`            | Error       | Enforces inline style for `@Prop`/`@State`/`@Event`; multiline for `@Watch`/`@Listen`/`@Method` |
| `stencil/element-type`                | Error       | Ensures `@Element()` has correct host element type                                              |
| `stencil/no-unused-watch`             | Error       | Catches unused `@Watch()` declarations                                                          |
| `stencil/methods-must-be-public`      | Error       | Methods with `@Method()` must be public                                                         |
| `stencil/props-must-be-readonly`      | Error       | Props should be readonly (unless `mutable: true`)                                               |
| `stencil/required-jsdoc`              | Error       | Enforces JSDoc on public APIs                                                                   |
| `stencil/strict-mutable`              | Warn        | Flags `mutable: true` props — allowed but discouraged in most cases                             |
| `stencil/strict-boolean-conditions`   | Warn        | Warns about non-boolean conditions in JSX                                                       |
| `stencil/own-methods-must-be-private` | Error       | Internal methods should be private; only `@Method()` is public                                  |
| `stencil/own-props-must-be-private`   | Error       | Internal state props should not leak as public properties                                       |
| `stencil/single-export`               | Error       | Each file exports only the component class                                                      |
| `@typescript-eslint/no-unused-vars`   | Error       | Prevents unused variables (ignore `_` prefix)                                                   |
| `@typescript-eslint/no-explicit-any`  | Warn        | Treat as error during review — no `any` on exported APIs                                        |
| `jsdoc/check-tag-names`               | Error       | Validates custom JSDoc tags (`@slot`, `@fires`, `@cssprop`, etc.)                               |

### 2.2 Prettier Configuration

Prettier handles code formatting automatically. The configuration prioritizes readability and consistency.

**Configuration (`.prettierrc.json`):**

```json
{
  "bracketSameLine": false,
  "jsxSingleQuote": false,
  "quoteProps": "as-needed",
  "printWidth": 120,
  "tabWidth": 2,
  "useTabs": false,
  "semi": true,
  "singleQuote": true,
  "trailingComma": "all",
  "bracketSpacing": true,
  "arrowParens": "avoid"
}
```

**Ignore Patterns (`.prettierignore` — per package):**

```
# Build outputs
dist
loader
www

# Dependencies
node_modules

# Generated files
*.d.ts
```

### 2.3 IDE Integration

**VSCode Settings (`.vscode/settings.json`):**

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": "always"
  },
  "eslint.validate": ["javascript", "typescript", "tsx"]
}
```

**Recommended Extensions:**

| Extension        | Purpose                    |
| ---------------- | -------------------------- |
| ESLint           | Real-time linting feedback |
| Prettier         | Code formatting            |
| Stencil Snippets | Code snippets for Stencil  |

### 2.4 Running Linters

**Scripts (`packages/boreal-web-components/package.json`):**

```json
{
  "scripts": {
    "lint": "eslint",
    "lint:fix": "eslint --fix",
    "format": "prettier --write 'src/**/*.{ts,tsx,css,scss,json}'",
    "format:check": "prettier --check 'src/**/*.{ts,tsx,css,scss,json}'"
  }
}
```

**Root workspace commands (delegate via Turborepo):**

```bash
# Run lint across all packages
pnpm lint

# Auto-fix lint violations
pnpm lint:fix

# Check formatting
pnpm format:check

# Auto-format
pnpm format
```

**Pre-commit Integration:**

Linting runs automatically before commits via `lefthook` (see Section 8 — Automation & CI/CD).

**CI/CD Integration:**

All pull requests must pass linting checks before merge (see Section 8 — Automation & CI/CD).

#### CEM Validation

The Custom Elements Manifest (CEM) generation serves as a documentation quality check, ensuring all components have complete and accurate metadata.

**Validation Commands:**

```bash
# Run from web-components package to check for undocumented CEM changes
pnpm --filter boreal-web-components check:cem
```

**What to Validate:**

- ✅ `custom-elements.json` exists in project root
- ✅ All public components are documented in the manifest
- ✅ No errors or warnings from CEM analyzer output
- ✅ File contains valid JSON with expected schema structure

**Quality Gates:**

The CEM generation command should complete without errors. Common issues include:

- Missing JSDoc annotations on public APIs (`@Prop`, `@Event`, `@Method`)
- Malformed JSDoc tags (e.g., incorrect `@fires` syntax)
- TypeScript compilation errors in component files

**See Also:**

- Section 5.6 for CEM configuration and setup
- Section 8.2 (CI Pipeline & Automated Releases)

#### Rationale

Automated linting provides:

1. **Consistency** — Uniform code style across all contributors
2. **Error Prevention** — Catches bugs and Stencil-specific issues before code review
3. **Type Safety** — TypeScript rules prevent common type-related errors
4. **API Quality** — Required JSDoc ensures public APIs are documented
5. **Developer Experience** — Immediate feedback in IDE
6. **Code Review Efficiency** — Focuses review on logic, not style

---

## 3. TYPESCRIPT STANDARDS

TypeScript provides type safety and better tooling support for the component library. This section defines compiler settings, type safety requirements, and coding patterns to ensure predictable behavior, catch errors early, and maintain code that's easy to refactor and understand.

### 3.1 Compiler Configuration

TypeScript compiler settings are defined in `tsconfig.json`. The monorepo root carries a minimal legacy `tsconfig.json` (from the Stencil starter template). The authoritative configuration for the web-components package is at `packages/boreal-web-components/tsconfig.json`.

\*\*Package Configuration (`packages/boreal-web-components/tsconfig.json`):

```json
{
  "compilerOptions": {
    /* Language & Environment */
    "target": "es2020",
    "lib": ["es2020", "dom", "dom.iterable"],
    "experimentalDecorators": true,
    "useDefineForClassFields": false,

    /* Modules */
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "allowSyntheticDefaultImports": true,
    "esModuleInterop": true,

    /* JSX (Stencil) */
    "jsx": "react",
    "jsxFactory": "h",
    "jsxFragmentFactory": "h.Fragment",

    /* Type Checking */
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "forceConsistentCasingInFileNames": true,
    "allowUnreachableCode": false,
    "preserveConstEnums": true,

    /* Types */
    "types": ["node", "jest"],
    "typeRoots": ["./node_modules/@types", "./src/types"],

    /* Emit */
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "outDir": "./dist",

    /* Interop Constraints */
    "allowJs": true,
    "skipLibCheck": true,
    "skipDefaultLibCheck": true,

    /* Path Mapping */
    "baseUrl": "./src/",
    "paths": {
      "@/*": ["./*"]
    }
  },
  "include": ["scripts", "src", "__mocks__"],
  "exclude": ["node_modules", "dist"]
}
```

**Key Options Explained:**

| Option                    | Value     | Rationale                                                                    |
| ------------------------- | --------- | ---------------------------------------------------------------------------- |
| `experimentalDecorators`  | `true`    | **Required** for Stencil decorators (`@Component`, `@Prop`, `@State`, etc.)  |
| `useDefineForClassFields` | `false`   | Ensures decorators work correctly with class fields                          |
| `target`                  | `es2020`  | Stable ES version with broad browser support                                 |
| `module`                  | `esnext`  | Enables top-level await and latest module features for bundlers              |
| `moduleResolution`        | `bundler` | Aligns with Vite/Rollup resolution; supports `exports` field in package.json |
| `jsx`                     | `react`   | Required by Stencil — maps `h()` as the JSX factory                          |
| `declaration`             | `true`    | Generates `.d.ts` files for type definitions and autocomplete                |
| `declarationMap`          | `true`    | Maps `.d.ts` files back to source for IDE navigation                         |
| `sourceMap`               | `true`    | Enables debugging in original TypeScript source                              |
| `skipDefaultLibCheck`     | `true`    | Skips type checks on default lib `.d.ts` to reduce build time                |

**Monorepo Note:**

`composite` and `incremental` project reference options are not currently used in this monorepo. Turborepo handles incremental build caching at the pipeline level instead.

**Path Aliases:**

The `@/` alias maps to the package `src/` root via `baseUrl`:

```json
{
  "compilerOptions": {
    "baseUrl": "./src/",
    "paths": {
      "@/*": ["./*"]
    }
  }
}
```

With `baseUrl: "./src/"`, the alias `@/*` resolves to `./src/*`.

**Usage:**

```typescript
// Instead of:
import { formatDate } from "../../../utils/date";

// Use:
import { formatDate } from "@/utils/date";
```

**Note:** Stencil's `transformAliasedImportPaths` option (default: `true`) automatically resolves these aliases in the compiled output.

#### Rationale

Proper TypeScript configuration ensures:

1. **Decorator Support** — `experimentalDecorators` enables Stencil's core functionality
2. **Explicit error detection** — `noUnusedLocals`, `noImplicitReturns`, etc. catch common mistakes without requiring `strict: true`
3. **Developer Experience** — Source maps and declaration maps enable debugging and IDE navigation
4. **No implicit `any`** — The root `tsconfig.json` has `noImplicitAny: false` for legacy reasons; treat it as an error in code review. All exported API surfaces must have explicit types.
5. **Code Quality** — Unused variable checks prevent dead code

### 3.2 Type Safety Requirements

All components must follow strict type safety practices to ensure reliability and maintainability.

#### Avoid `Omit<>` for Component Props

Using TypeScript's `Omit<>` utility type to derive component props can break type inference and autocomplete.

❌ **DON'T:**

```typescript
interface BaseProps {
  value: string;
  disabled: boolean;
  onChange: (value: string) => void;
}

// Omit breaks prop reflection and type generation
@Component({ tag: "my-input" })
export class MyInput {
  @Prop() props: Omit<BaseProps, "onChange">;
}
```

✅ **DO:**

```typescript
@Component({ tag: "my-input" })
export class MyInput {
  @Prop() value: string;
  @Prop() disabled: boolean = false;
}
```

**Why:** Stencil generates type definitions from individual `@Prop()` decorators. Using `Omit<>` or other utility types prevents proper type generation and breaks IDE autocomplete for consumers.

#### Use `const` Enums or String Union Types

Enums can cause issues with tree-shaking and type generation. Prefer `const` enums or string union types.

❌ **DON'T:**

```typescript
export enum ButtonVariant {
  Primary = 'primary',
  Secondary = 'secondary',
  Danger = 'danger'
}

@Prop() variant: ButtonVariant;
```

✅ **DO (Option 1: String Union):**

```typescript
export type ButtonVariant = "primary" | "secondary" | "danger";

@Component({ tag: "my-button" })
export class MyButton {
  @Prop() variant: ButtonVariant = "primary";
}
```

✅ **DO (Option 2: const enum):**

```typescript
export const enum ButtonVariant {
  Primary = "primary",
  Secondary = "secondary",
  Danger = "danger",
}

@Component({ tag: "my-button" })
export class MyButton {
  @Prop() variant: ButtonVariant = ButtonVariant.Primary;
}
```

**Why:** Regular enums generate runtime code that can't be tree-shaken. String unions are type-only and have zero runtime cost. `const` enums are inlined at compile time.

#### Exposing Types to Consumers

Component types are automatically exposed through generated `.d.ts` files. Consumers can import types when needed.

**Automatic Type Export:**

```typescript
// my-button.tsx
export interface ButtonClickDetail {
  timestamp: number;
  value: string;
}

@Component({ tag: "bds-button" })
export class BdsButton {
  @Event() bdsClick: EventEmitter<ButtonClickDetail>;
}
```

**Consumer Usage:**

```typescript
// Consumer's code
import type { ButtonClickDetail } from "your-library";

const button = document.querySelector("bds-button");
button.addEventListener("bdsClick", (event: CustomEvent<ButtonClickDetail>) => {
  console.log(event.detail.timestamp);
});
```

**Guidelines:**

| Type                    | Export?              | Rationale                                      |
| ----------------------- | -------------------- | ---------------------------------------------- |
| Event detail interfaces | ✅ Yes               | Consumers need these for typed event handlers  |
| Public prop types       | ✅ Yes               | Useful for frameworks and type checking        |
| Internal state types    | ❌ No                | Implementation details, not part of public API |
| Utility types           | ✅ Yes (if reusable) | Only export if consumers would benefit         |

**Note:** Stencil automatically generates type definitions when `declaration: true` is set in `tsconfig.json` (see Section 3.1).

#### Rationale

Strict type safety provides:

1. **Autocomplete** — Proper types enable IDE autocomplete for component props and events
2. **Error Prevention** — Type errors caught at compile time, not runtime
3. **Refactoring Safety** — Changes to types are validated across the entire codebase
4. **Documentation** — Types serve as inline documentation for component APIs
5. **Framework Compatibility** — Proper type exports work with React, Vue, Angular type systems

### 3.3 Common Patterns & Best Practices

#### Common Types Organization

Shared types should be organized in a dedicated `types` directory for reusability and consistency.

**Directory Structure (Boreal DS convention):**

```
src/
├── components/
│   └── bds-button/
│       ├── bds-button.tsx
│       ├── bds-button.scss
│       ├── bds-button.spec.tsx
│       └── types/
│           ├── IButton.ts       ← interface (public props)
│           ├── enum.ts          ← BUTTON_VARIANTS, BUTTON_SIZES, …
│           └── types.ts         ← ButtonVariant, ButtonSize, …
└── utils/
    └── helpers/
        └── validateProps.ts
```

**Common Types (`src/types/common.ts`):**

```typescript
// Shared size variants
export type Size = "small" | "medium" | "large";

// Shared color variants
export type Variant =
  | "primary"
  | "secondary"
  | "success"
  | "warning"
  | "danger";

// Shared alignment
export type Alignment = "start" | "center" | "end";

// Shared component states
export type ComponentState = "idle" | "loading" | "error" | "success";
```

**⚠️ Avoid Barrel Files:**

Do NOT create `index.ts` files that re-export everything (`export * from`). Barrel files cause:

- Poor tree-shaking and bundle bloat
- Slow TypeScript compilation and IDE performance
- Hidden dependency coupling

❌ **DON'T:**

```typescript
// src/types/index.ts - AVOID THIS PATTERN
export * from "./common";
export * from "./events";
```

✅ **DO:**

```typescript
// Import directly from source files
import type { Size, Variant } from "../../types/common";
import type { ButtonClickDetail } from "./my-button.types";
```

#### Referencing Prop Types from the Component Interface

When a utility, helper, or sub-component needs the type of a single prop, use indexed access on the component's interface rather than duplicating the type or importing a separate alias.

```typescript
import type { IBdsButton } from "./types/IBdsButton";

function applyVariant(variant: IBdsButton["variant"]) {
  // typed directly from the interface — no duplication
}
```

This keeps prop types in one authoritative place (the `IComponent` interface) and propagates changes automatically.

#### Component Props Typing

Each component should define an explicit interface for its props, even when using decorators.

**Component-Specific Types (`types/IButton.ts` + `types/types.ts`):**

```typescript
import type { Variant, Size } from "../../types";

export interface IButton {
  variant?: Variant;
  size?: Size;
  disabled?: boolean;
  label?: string;
}

export interface ButtonClickDetail {
  buttonId: string;
  timestamp: number;
}
```

**Component Implementation (`bds-button.tsx`):**

```typescript
import { Component, Element, Prop, Event, EventEmitter, h } from '@stencil/core';
import type { IButton, ButtonClickDetail } from './types/IButton';
import type { Variant, Size } from '../../types';

@Component({
  tag: 'bds-button',
  styleUrl: 'bds-button.scss',
})
export class BdsButton implements IButton {
  @Element() el!: HTMLBdsButtonElement;

  @Prop({ reflect: true }) readonly variant: Variant = 'primary';
  @Prop({ reflect: true }) readonly size: Size = 'medium';
  @Prop({ reflect: true }) readonly disabled: boolean = false;
  @Prop() readonly label: string;

  @Event() bdsClick: EventEmitter<ButtonClickDetail>;

  private handleClick = () => {
    this.bdsClick.emit({
      buttonId: this.el.id,
      timestamp: Date.now(),
    });
  };

  render() {
    return (
      <button
        class={`button button--${this.variant} button--${this.size}`}
        disabled={this.disabled}
        onClick={this.handleClick}
      >
        {this.label}
      </button>
    );
  }
}
```

**Benefits:**

| Practice                | Benefit                                       |
| ----------------------- | --------------------------------------------- |
| Separate `types/` files | Clear separation of types from implementation |
| `implements` interface  | Ensures all props are declared                |
| Explicit prop types     | Better IDE support and autocomplete           |
| Direct imports          | Tree-shakeable; no barrel file overhead       |

#### Type Scaffolding Template

Use this template for new components (generated by `pnpm generate:component`):

```typescript
// src/components/bds-my-component/types/IMyComponent.ts

/**
 * Public props interface for BdsMyComponent
 */
export interface IMyComponent {
  variant?: 'primary' | 'secondary';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  label?: string;
}

/**
 * Event detail emitted by BdsMyComponent
 */
export interface MyComponentChangeDetail {
  value: string;
}

// src/components/bds-my-component/bds-my-component.tsx
import { Component, Element, Prop, Event, EventEmitter, h } from '@stencil/core';
import type { IMyComponent, MyComponentChangeDetail } from './types/IMyComponent';

@Component({
  tag: 'bds-my-component',
  styleUrl: 'bds-my-component.scss',
})
export class BdsMyComponent implements IMyComponent {
  @Element() el!: HTMLBdsMyComponentElement;

  @Prop({ reflect: true }) readonly variant: IMyComponent['variant'] = 'primary';
  @Prop({ reflect: true }) readonly size: IMyComponent['size'] = 'medium';
  @Prop({ reflect: true }) readonly disabled: boolean = false;
  @Prop() readonly label: string;

  @Event() bdsChange: EventEmitter<MyComponentChangeDetail>;

  render() {
    return <div>Component content</div>;
  }
}
```

#### Library Distribution with Package Exports

For optimal tree-shaking and consumer experience, configure package subpath exports in `package.json`. Use wildcard patterns to avoid listing every component individually.

```json
{
  "name": "@your-org/component-library",
  "type": "module",
  "exports": {
    ".": {
      "import": "./dist/index.js",
      "types": "./dist/types/components.d.ts"
    },
    "./loader": {
      "import": "./loader/index.js",
      "types": "./loader/index.d.ts"
    },
    "./components/*": {
      "import": "./components/*"
    },
    "./types": {
      "import": "./dist/types/common.js",
      "types": "./dist/types/common.d.ts"
    },
    "./constants": {
      "import": "./dist/constants/index.js",
      "types": "./dist/types/constants/index.d.ts"
    }
  }
}
```

**Export Paths Explained:**

| Export             | Purpose                          | Consumer Usage                                       |
| ------------------ | -------------------------------- | ---------------------------------------------------- |
| `"."`              | Main bundle (all components)     | `import { Button } from '@lib'`                      |
| `"./loader"`       | Lazy-loading helper (Stencil)    | `import { defineCustomElements } from '@lib/loader'` |
| `"./components/*"` | Individual components (wildcard) | `import { Button } from '@lib/components/button'`    |
| `"./types"`        | Shared type definitions          | `import type { Size } from '@lib/types'`             |
| `"./constants"`    | Shared constants/enums           | `import { SIZES } from '@lib/constants'`             |

**Consumer Usage:**

```typescript
// Option 1: Quick start (imports full bundle)
import { Button, Input, Form } from "@your-org/component-library";

// Option 2: Optimal tree-shaking (per-component imports)
import { Button } from "@your-org/component-library/components/button";
import { Input } from "@your-org/component-library/components/input";

// Framework integration (lazy loading)
import { defineCustomElements } from "@your-org/component-library/loader";
defineCustomElements();

// Shared types
import type { Size, Variant } from "@your-org/component-library/types";
```

**Benefits:**

| Approach                    | Bundle Size | TypeScript Performance | Tree-Shaking | Scalability  |
| --------------------------- | ----------- | ---------------------- | ------------ | ------------ |
| Barrel imports (`export *`) | ❌ Large    | ❌ Slow                | ❌ Poor      | ❌ Manual    |
| Wildcard subpath exports    | ✅ Minimal  | ✅ Fast                | ✅ Excellent | ✅ Automatic |

**Note:** The wildcard pattern (`"./components/*"`) automatically scales as you add components—no need to update `package.json` for each new component.

#### Rationale

Organized types ensure:

1. **Bundle Efficiency** — Direct imports enable proper tree-shaking (avoid barrel files)
2. **Performance** — TypeScript resolves only what's imported, not entire module graphs
3. **Consistency** — Shared types enforce consistent prop names across components
4. **Type Safety** — `implements` ensures all interface props are declared
5. **Documentation** — Interfaces serve as contracts for component APIs
6. **Maintainability** — Explicit imports reveal true dependencies between modules

---

## 4. TESTING STANDARDS

Comprehensive testing ensures components work reliably across different scenarios and browsers. This section outlines the testing philosophy, required coverage levels, and specific approaches for unit, integration, visual regression, and accessibility testing to maintain high quality standards.

### 4.1 Test Runner & Philosophy

**Test Runner**

Use Stencil's built-in test runner (Jest) for unit tests:

- **Integrated tooling** — Works seamlessly with the Stencil compiler and build pipeline
- **Chrome-based testing** — Aligns with Chromatic (Chrome-only visual testing)
- **Stencil-optimized helpers** — `newSpecPage()` for unit tests

**Commands:**

```bash
# Run unit tests (from workspace root)
pnpm test

# Run unit tests in watch mode
pnpm --filter boreal-web-components test:watch

# Run with coverage
pnpm --filter boreal-web-components test:coverage
```

**Note on Multi-Browser Testing:**

Multi-browser functional testing via [@web/test-runner](https://modern-web.dev/docs/test-runner/overview/) provides minimal additional coverage for modern web components. Modern browsers have consistent JavaScript/DOM API implementations. If cross-browser issues arise, prioritize upgrading Chromatic to Starter tier ($179/month) for multi-browser **visual** testing, which catches 80% of browser-specific issues compared to ~5% from functional tests.

---

**Testing Philosophy**

**Test behavior, not implementation.** Focus on what the component does from a user's perspective, not how it does it internally.

**Core Principles:**

| Principle                         | Description                                      | Example                                                                |
| --------------------------------- | ------------------------------------------------ | ---------------------------------------------------------------------- |
| **Behavior over implementation**  | Test user-visible outcomes, not internal methods | ✅ Test error message display<br>❌ Test `validateInput()` method call |
| **Integration over dependencies** | Trust external libraries, test your integration  | ✅ Test validation styling applied<br>❌ Test email validator logic    |
| **Quality over quantity**         | Meaningful tests beat 100% coverage              | ✅ Edge cases and error scenarios<br>❌ Trivial getter/setter tests    |
| **Independence**                  | Each test should stand alone                     | ✅ Self-contained test setup<br>❌ Tests dependent on execution order  |

**What to Test:**

- ✅ User-visible behavior changes
- ✅ Different property/state combinations
- ✅ Error scenarios and edge cases
- ✅ Accessibility features (keyboard navigation, ARIA)
- ✅ Custom event emission and payloads

**What NOT to Test:**

- ❌ Internal method implementations
- ❌ External library functionality
- ❌ Trivial getters/setters without logic
- ❌ Implementation details that may change
- ❌ Code already tested indirectly

---

**Test Structure: AAA Pattern**

Use the **Arrange-Act-Assert (AAA)** pattern for all test types. This structure applies to unit, integration, E2E, visual, and accessibility tests:

```typescript
it("should emit event when button clicked", async () => {
  // ARRANGE - Set up the test environment
  const page = await newSpecPage({
    components: [BdsButton],
    html: `<bds-button label="Click me"></bds-button>`,
  });
  const button = page.root;
  const eventSpy = jest.fn();
  button.addEventListener("bdsClick", eventSpy);

  // ACT - Perform the action being tested
  button.click();
  await page.waitForChanges();

  // ASSERT - Verify expected outcome
  expect(eventSpy).toHaveBeenCalledTimes(1);
  expect(eventSpy).toHaveBeenCalledWith(
    expect.objectContaining({ detail: { label: "Click me" } }),
  );
});
```

**Benefits:**

- **Readability** — Clear separation of setup, action, and verification
- **Maintainability** — Easy to identify what's being tested
- **Consistency** — Same pattern across all test types
- **Debugging** — Quickly locate which phase failed

### 4.2 Unit Testing

Unit tests verify individual component behavior in isolation using Stencil's testing utilities.

#### Scaffolding: by functionality

Create different files for the following types of component functionality when applicable:

- A11y (Accessibility).
- Basics.
- Variants.
- Events.
- Slots.

The naming convention should follow the rule `{bds-component}.functionality.spec.tsx`. Example:

- `bds-component.a11y.spec.tsx`
- `bds-component.basics.spec.tsx`
- `bds-component.variants.spec.tsx`
- `bds-component.events.spec.tsx`
- `bds-component.slots.spec.tsx`

**Basic Structure:**

```typescript
import { newSpecPage } from "@stencil/core/testing";
import { BdsButton } from "./bds-button";

describe("bds-button", () => {
  it("should render with default props", async () => {
    const page = await newSpecPage({
      components: [BdsButton],
      html: `<bds-button>Click me</bds-button>`,
    });

    expect(page.root).toEqualHtml(`
      <bds-button>
        <button class="button button--primary">
          Click me
        </button>
      </bds-button>
    `);
  });

  it("should emit custom event on click", async () => {
    // ARRANGE
    const page = await newSpecPage({
      components: [BdsButton],
      html: `<bds-button>Click me</bds-button>`,
    });
    const spy = jest.fn();
    page.root.addEventListener("bdsClick", spy);

    // ACT
    const button = page.root.querySelector("button");
    button.click();
    await page.waitForChanges();

    // ASSERT
    expect(spy).toHaveBeenCalledWith(
      expect.objectContaining({
        detail: expect.objectContaining({ timestamp: expect.any(Number) }),
      }),
    );
  });
});
```

**Testing Guidelines:**

| Scenario             | Approach                                                           |
| -------------------- | ------------------------------------------------------------------ |
| **Property changes** | Set prop, wait for changes, assert rendered output                 |
| **Custom events**    | Add event listener, trigger action, verify event detail            |
| **Child elements**   | Use `root.querySelector()` — no shadow DOM, no `shadowRoot` needed |
| **Async behavior**   | Use `await page.waitForChanges()` after state updates              |
| **Error states**     | Test invalid inputs and error message rendering                    |

**Package scripts (`packages/boreal-web-components/package.json`):**

```json
{
  "scripts": {
    "test": "stencil test --spec",
    "test:watch": "stencil test --spec --watchAll",
    "test:coverage": "stencil test --spec --coverage"
  }
}
```

### 4.3 Integration Testing

Integration tests verify components work correctly together and with the DOM using end-to-end testing tools.

**Recommended Tools:**

| Tool            | Use Case                    | Benefits                        |
| --------------- | --------------------------- | ------------------------------- |
| **Playwright**  | E2E testing, cross-browser  | Fast, reliable, great debugging |
| **Stencil E2E** | Built-in E2E with Puppeteer | Integrated with Stencil build   |

**Example (Stencil E2E):**

```typescript
import { newE2EPage } from "@stencil/core/testing";

describe("form integration", () => {
  it("should validate and submit form", async () => {
    // ARRANGE
    const page = await newE2EPage();
    await page.setContent(`
      <bds-form>
        <bds-text-field name="email" required></bds-text-field>
        <bds-button type="submit">Submit</bds-button>
      </bds-form>
    `);
    const input = await page.find("bds-text-field");
    const button = await page.find("bds-button");

    // ACT - Submit without filling (should show error)
    await button.click();
    await page.waitForChanges();

    // ASSERT
    const error = await page.find("bds-text-field .error");
    expect(error).not.toBeNull();

    // ACT - Fill input (error should clear)
    await input.type("test@example.com");
    await page.waitForChanges();

    // ASSERT
    const errorAfter = await page.find("bds-text-field .error");
    expect(errorAfter).toBeNull();
  });
});
```

### 4.4 Visual Regression Testing

Visual regression testing catches unintended UI changes by comparing screenshots. For Storybook-based projects, **Chromatic** is the recommended approach.

#### Chromatic (Recommended)

Chromatic automatically captures screenshots of all Storybook stories and compares them against baselines without requiring test code.

**Setup:**

```bash
pnpm add -D chromatic
```

**Configuration (`package.json`):**

```json
{
  "scripts": {
    "chromatic": "chromatic --project-token=<your-project-token>"
  }
}
```

**Storybook Integration:**

Chromatic automatically tests every story in your Storybook. No additional test code needed:

```typescript
// button.stories.tsx - Chromatic captures these automatically
export default {
  title: "Components/Button",
  component: "my-button",
};

export const Primary = () =>
  `<bds-button variant="primary">Primary</bds-button>`;
export const Secondary = () =>
  `<bds-button variant="secondary">Secondary</bds-button>`;
export const Disabled = () => `<bds-button disabled>Disabled</bds-button>`;
```

**Snapshot Calculation & Cost Planning:**

Chromatic charges based on snapshots. Calculate your usage to determine if the free tier is sufficient:

```
Snapshots per run = Stories × Viewports × Browsers

Components: Number of components in your library
States: Average states per component (default, hover, error, disabled, loading, etc.)
Stories: Components × States
Viewports: Desktop, tablet, mobile (typically 3)
Browsers: Chrome, Firefox, Safari, Edge (choose based on support requirements)
```

**Example Calculation:**

| Scenario               | Components | Avg States | Stories | Viewports | Browsers | Snapshots/Run |
| ---------------------- | ---------- | ---------- | ------- | --------- | -------- | ------------- |
| **Small Library**      | 20         | 2          | 40      | 3         | 1        | 120           |
| **Medium Library**     | 50         | 3          | 150     | 3         | 2        | 900           |
| **Large Library**      | 100        | 3          | 300     | 3         | 2        | 1,800         |
| **Enterprise Library** | 200        | 4          | 800     | 4         | 3        | 9,600         |

**Monthly Usage Estimate:**

```
PRs per month: ~20 (1 per workday)
Snapshots per PR: 900 (medium library)
Monthly snapshots: 20 × 900 = 18,000 snapshots

Chromatic Free Tier: 5,000 snapshots/month
Result: Exceeds free tier, need paid plan
```

**Cost Optimization Strategies:**

| Strategy                                | Snapshot Reduction | Trade-off                    |
| --------------------------------------- | ------------------ | ---------------------------- |
| Test 1 browser instead of 2             | 50% reduction      | Less cross-browser coverage  |
| Test 2 viewports instead of 3           | 33% reduction      | Miss tablet/mobile issues    |
| Run on `main` + critical PRs only       | ~70% reduction     | May miss issues earlier      |
| Group related states into single story  | 20-30% reduction   | Less granular diffs          |
| Use TurboSnap (changed components only) | 60-80% reduction   | Requires Chromatic paid tier |

**Pricing Tiers:**

- **Free**: $0/month - 5,000 snapshots, Chrome only
- **Starter**: $179/month - 35,000 snapshots, multi-browser (Safari, Firefox, Edge), extra snapshots $0.008 each
- **Pro**: $399/month - 85,000 snapshots, multi-browser, custom domain, extra snapshots $0.008 each
- **Enterprise**: Custom pricing - includes TurboSnap, SSO, priority support, custom data retention

**Benefits:**

| Feature                   | Benefit                                      |
| ------------------------- | -------------------------------------------- |
| **Zero test code**        | Automatically tests all Storybook stories    |
| **Cross-browser testing** | Chrome, Firefox, Safari, Edge support        |
| **Cloud baselines**       | No Git bloat from committed screenshots      |
| **Review UI**             | Web-based approval workflow for stakeholders |
| **Parallel execution**    | Fast testing, doesn't block CI pipeline      |
| **Collaboration**         | Designers approve visual changes without Git |

**When to Use Chromatic:**

- ✅ Projects using Storybook for documentation
- ✅ Teams needing visual approval workflows
- ✅ Medium to large component libraries (50+ components)
- ✅ Budget available for paid tier (or usage fits free tier)
- ✅ Multi-browser testing requirements

#### Alternative: Stencil Screenshot Testing

For projects without Storybook, tight budgets, or needing self-hosted solutions, use Stencil's built-in screenshot testing.

**Example:**

```typescript
import { newE2EPage } from "@stencil/core/testing";

describe("visual regression", () => {
  it("should match button variants screenshot", async () => {
    const page = await newE2EPage();
    await page.setContent(`
      <div>
        <bds-button variant="primary">Primary</bds-button>
        <bds-button variant="secondary">Secondary</bds-button>
        <bds-button variant="danger">Danger</bds-button>
      </div>
    `);

    await page.compareScreenshot("button-variants");
  });
});
```

**Configuration (`stencil.config.ts`):**

```typescript
export const config: Config = {
  testing: {
    screenshotConnector: "./screenshot-connector.js",
  },
};
```

**When to Use Stencil Screenshots:**

- ✅ No Storybook setup
- ✅ Tight budget (completely free)
- ✅ Self-hosted requirements
- ✅ Simple component library (< 30 components)
- ❌ Need cross-browser testing (Stencil uses Chromium only)
- ❌ Need team approval workflows

#### Recommendation Summary

**Choose Chromatic if:**

- You have Storybook
- Monthly snapshots < 5,000 OR budget for paid tier
- Need cross-browser testing
- Need stakeholder visual approval workflow

**Choose Stencil Screenshots if:**

- No Storybook
- Zero budget for tooling
- Self-hosted requirement
- Small component library

### 4.5 Accessibility Testing

Accessibility testing ensures components work for all users, including those using assistive technologies. A comprehensive accessibility strategy combines automated testing, interactive testing, and manual verification.

#### Automated Accessibility Testing (Chromatic + Storybook)

**Chromatic automatically runs axe-core accessibility tests** on every Storybook story when integrated in your CI pipeline. This eliminates the need for writing separate jest-axe test code.

**How it works:**

1. **During development** - Storybook's [A11y addon](https://storybook.js.org/docs/writing-tests/accessibility-testing) runs axe-core locally:
   - Shows all violations in real-time
   - Highlights violating elements in the canvas
   - Provides detailed error descriptions and fix guidance

2. **In CI** - Chromatic runs axe-core on all stories:
   - Component-level testing (not page-level)
   - Regression tracking (flags only NEW violations)
   - Baseline management (accept existing debt, prevent new debt)
   - Multi-viewport support (tests across breakpoints)

**What Chromatic Tests:**

| Category                   | Examples                                                        |
| -------------------------- | --------------------------------------------------------------- |
| **Semantic HTML**          | Missing ARIA labels, invalid roles, improper heading hierarchy  |
| **Form accessibility**     | Missing labels, fieldset/legend issues, invalid autocomplete    |
| **Color contrast**         | Text contrast ratios (WCAG AA: 4.5:1 normal, 3:1 large text)    |
| **Images**                 | Missing alt text, decorative images without role="presentation" |
| **Interactive elements**   | Missing accessible names, invalid ARIA attributes               |
| **Keyboard accessibility** | Missing tabindex where needed, keyboard traps (structural only) |

**What Chromatic Does NOT Test:**

- ❌ Interactive keyboard behavior (Tab order, focus trapping, Enter/Space handling)
- ❌ Screen reader announcements and live regions
- ❌ Focus management during dynamic content changes
- ❌ Multi-browser accessibility (Chrome only)

**Setup:**

No additional test code required if Chromatic is integrated. Ensure Storybook A11y addon is installed:

```bash
pnpm add -D @storybook/addon-a11y
```

**.storybook/main.ts:**

```typescript
export default {
  addons: ["@storybook/addon-a11y"],
};
```

#### Interactive Accessibility Testing

Automated tools catch ~40-60% of accessibility issues. Test interactive behavior with E2E tests:

```typescript
import { newE2EPage } from "@stencil/core/testing";

describe("keyboard accessibility", () => {
  it("should support keyboard navigation", async () => {
    // ARRANGE
    const page = await newE2EPage();
    await page.setContent(`
      <my-modal>
        <button>Close</button>
        <input type="text" />
      </my-modal>
    `);

    // ACT - Tab through focusable elements
    await page.keyboard.press("Tab");
    let focusedElement = await page.evaluate(
      () => document.activeElement.tagName,
    );

    // ASSERT - First focusable element receives focus
    expect(focusedElement.toLowerCase()).toBe("button");

    // ACT - Continue tabbing
    await page.keyboard.press("Tab");
    focusedElement = await page.evaluate(() => document.activeElement.tagName);

    // ASSERT - Focus moves to input
    expect(focusedElement.toLowerCase()).toBe("input");

    // ACT - Activate with keyboard
    await page.keyboard.press("Escape");
    await page.waitForChanges();

    // ASSERT - Modal closes on Escape
    const modal = await page.find("my-modal");
    expect(await modal.getProperty("open")).toBe(false);
  });

  it("should trap focus within modal", async () => {
    // ARRANGE
    const page = await newE2EPage();
    await page.setContent(`
      <div>
        <button id="outside">Outside</button>
        <my-modal open>
          <button id="inside">Inside</button>
        </my-modal>
      </div>
    `);

    // ACT - Tab from last modal element
    const insideButton = await page.find("#inside");
    await insideButton.focus();
    await page.keyboard.press("Tab");

    // ASSERT - Focus stays within modal
    const focusedId = await page.evaluate(() => document.activeElement.id);
    expect(focusedId).not.toBe("outside");
  });
});
```

#### Manual Testing Checklist

Automated tools and E2E tests don't catch everything. Perform manual testing for critical components:

| Category                | Test                                                                                            | Tools                                             |
| ----------------------- | ----------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| **Keyboard Navigation** | Tab through all interactive elements, Enter/Space to activate, Escape to close modals/dropdowns | Browser only                                      |
| **Screen Reader**       | Component announces correctly, live regions update properly, labels are descriptive             | VoiceOver (macOS), NVDA (Windows), JAWS (Windows) |
| **Focus Management**    | Visible focus indicators, logical tab order, focus returns after modals close                   | Browser + keyboard                                |
| **Zoom & Scaling**      | Layout doesn't break at 200% zoom, text remains readable                                        | Browser zoom (Cmd/Ctrl +)                         |
| **Color Blindness**     | Information not conveyed by color alone                                                         | Browser extensions (Colorblindly)                 |

#### When to Use jest-axe

Only use jest-axe if you're **NOT using Chromatic**. If Chromatic is integrated, it already runs axe-core automatically.

**Without Chromatic:**

```typescript
import { newSpecPage } from "@stencil/core/testing";
import { axe } from "jest-axe";

describe("accessibility", () => {
  it("should have no axe violations", async () => {
    // ARRANGE
    const page = await newSpecPage({
      components: [BdsButton],
      html: `<bds-button>Click me</bds-button>`,
    });

    // ACT
    const results = await axe(page.root);

    // ASSERT
    expect(results).toHaveNoViolations();
  });
});
```

#### Recommendation Summary

**With Chromatic (Recommended):**

- ✅ Chromatic handles automated axe-core testing
- ✅ Storybook A11y addon for dev feedback
- ✅ E2E tests for keyboard/focus behavior
- ✅ Manual testing for screen readers
- ❌ Skip jest-axe (redundant)

**Without Chromatic:**

- ✅ jest-axe in unit tests
- ✅ Storybook A11y addon for dev feedback
- ✅ E2E tests for keyboard/focus behavior
- ✅ Manual testing for screen readers

### 4.6 Running Tests

**Command Reference:**

```bash
# Run all tests (from workspace root)
pnpm test

# Run specific test file
pnpm --filter boreal-web-components test -- --testPathPattern=bds-button

# Watch mode
pnpm --filter boreal-web-components test:watch

# Coverage report
pnpm --filter boreal-web-components test:coverage

# Single test case (use .only in test file)
it.only('should render correctly', async () => { ... });
```

**CI/CD Integration:**

All tests must pass before merging (see Section 8.2 — CI Pipeline & Automated Releases).

#### Rationale

Comprehensive testing ensures:

1. **Reliability** — Components work as expected across scenarios
2. **Regression Prevention** — New changes don't break existing functionality
3. **Documentation** — Tests serve as living usage examples
4. **Confidence** — Developers can refactor without fear
5. **Accessibility** — All users can interact with components
6. **Quality** — Bugs caught early in development, not production

---

## 5. DOCUMENTATION STANDARDS

Clear documentation enables developers to use components correctly and efficiently while providing non-technical stakeholders with accessible, navigable component information. This section establishes a dual-documentation strategy combining technical documentation (Storybook) for developers with user-friendly documentation (Notion/Confluence) for designers, product managers, and cross-team collaboration.

### 5.1 Documentation Strategy Overview

The component library uses a **two-tier documentation system** to serve different audiences effectively:

**1. Technical Documentation (Storybook)** - Developer-focused interactive documentation
**2. User-Friendly Documentation (Notion/Confluence)** - Design and cross-team collaboration hub

#### Why Both?

| Audience             | Tool               | Purpose                                                               |
| -------------------- | ------------------ | --------------------------------------------------------------------- |
| **Developers**       | Storybook          | Props, events, methods, code examples, API reference, live playground |
| **UX/UI Designers**  | Notion/Confluence  | Component gallery, design rationale, usage guidelines, "when to use"  |
| **Product Managers** | Notion/Confluence  | Component overview, status, roadmap, adoption tracking                |
| **QA/Testing Teams** | Storybook + Notion | Test scenarios, accessibility notes, edge cases                       |
| **All Teams**        | Notion → Storybook | Notion as "front door", Storybook for deep technical details          |

#### Benefits of Dual Documentation

- **Reduced friction** - Non-technical teams don't need to navigate Storybook's technical interface
- **Improved discovery** - Visual component gallery with search and categorization
- **Better collaboration** - Comments, feedback, and discussions in one place
- **Design alignment** - UX rationale and guidelines live alongside technical docs
- **Faster onboarding** - New team members start with high-level overview before diving deep
- **Cross-team visibility** - Everyone sees component status, roadmap, and adoption

---

### 5.2 Code Documentation (JSDoc/TSDoc)

Document component source code with JSDoc/TSDoc for inline documentation and IDE autocomplete.

#### Required Documentation

- Component class description
- All public `@Prop()`, `@State()`, `@Event()`, `@Method()` declarations
- Complex methods with parameters and return types
- Non-obvious behavior or edge cases

#### Example

```typescript
/**
 * A customizable button component with multiple variants and states.
 *
 * @slot - Default slot for button content (text or icons)
 * @slot icon-start - Optional icon displayed before button text
 * @slot icon-end - Optional icon displayed after button text
 */
@Component({
  tag: "bds-button",
  styleUrl: "bds-button.scss",
})
export class BdsButton {
  /**
   * The visual style variant of the button.
   * @default 'primary'
   */
  @Prop() variant: "primary" | "secondary" | "danger" = "primary";

  /**
   * Disables the button and prevents interaction.
   */
  @Prop() disabled: boolean = false;

  /**
   * Emitted when the button is clicked.
   */
  @Event() bdsClick: EventEmitter<{ timestamp: number }>;

  /**
   * Programmatically focuses the button.
   * Useful for accessibility and keyboard navigation scenarios.
   */
  @Method()
  async setFocus() {
    this.buttonElement?.focus();
  }

  /**
   * Validates the button's internal state.
   * @internal
   */
  private validateState() {
    // Implementation
  }
}
```

#### JSDoc Best Practices

| Practice            | Example                                         |
| ------------------- | ----------------------------------------------- |
| **Use `@default`**  | `@default 'primary'` for prop defaults          |
| **Document slots**  | `@slot icon-start - Icon before text`           |
| **Event details**   | `@event bdsClick - Emitted with { timestamp }`  |
| **Mark internals**  | `@internal` for private implementation details  |
| **Parameter types** | `@param {string} value - The input value`       |
| **Return types**    | `@returns {Promise<boolean>} Validation result` |

---

### 5.3 Technical Documentation (Storybook)

Storybook provides interactive component documentation for developers with live code examples, prop controls, and framework-specific usage.

#### Setup

```bash
pnpm add -D @storybook/web-components @storybook/addon-docs @storybook/addon-a11y
```

#### Story Structure

Each component should have its own directory containing both story definitions (`.stories.tsx`) and documentation (`.mdx`). This separation allows stories to define interactive examples while MDX files provide narrative documentation.

**File Organization:**

```
components/
├── bds-button/
│   ├── bds-button.stories.ts    # Story definitions and interactive examples
│   └── bds-button.mdx            # Documentation narrative and layout
├── bds-text-field/
│   ├── bds-text-field.stories.ts
│   └── bds-text-field.mdx
└── bds-select/
    ├── bds-select.stories.ts
    └── bds-select.mdx
```

**Why This Structure?**

- ✅ **Separation of concerns** — Stories focus on interactive examples, MDX focuses on documentation narrative
- ✅ **Maintainability** — Changes to component behavior only require updating `.stories.tsx`
- ✅ **Discoverability** — All component documentation lives in one directory
- ✅ **Reusability** — Stories can be referenced from MDX using `<Canvas of={Stories.Example} />`

---

**Why Use Lit for Stories?**

Stories use Lit's `html` tagged template literal for rendering, even though components are built with Stencil:

```typescript
import { html } from "lit";
```

**Rationale:**

- ✅ **Framework-agnostic** — Lit is a rendering library, not a framework. Stories demonstrate components as standard web components.
- ✅ **Storybook compatibility** — `@storybook/web-components` uses Lit under the hood for rendering.
- ✅ **Property binding** — Lit's `.property=${value}` syntax binds JavaScript values directly to component properties (not HTML attributes).
- ✅ **Event handling** — Declarative event binding with `@eventName=${handler}`.
- ✅ **Conditional rendering** — `${condition ? html`...` : nothing}` for dynamic templates.

**Important:** Using Lit in stories does NOT mean components depend on Lit. Stencil components remain standalone web components that work in any framework or vanilla JavaScript.

---

**Documentation Approach: MDX Over `autodocs`**

**❌ Do NOT use `tags: ['autodocs']`**

Instead, create a dedicated `.mdx` file for each component.

**Why MDX?**

| Concern             | `autodocs` (Auto-generated) | `.mdx` (Manual)                                                            |
| ------------------- | --------------------------- | -------------------------------------------------------------------------- |
| **Customization**   | Limited layout control      | Full control over structure, headings, narrative                           |
| **User experience** | Generic API reference       | Tailored guidance: "When to use", usage examples, design rationale         |
| **Discoverability** | Props listed alphabetically | Organized by user workflows (installation → usage → properties → examples) |
| **Narrative**       | None                        | Explains "why" and "how", not just "what"                                  |
| **Interactivity**   | Basic Canvas blocks         | Custom Canvas placement, interactive demos, embedded links                 |

**MDX File Structure:**

Each component's `.mdx` file serves as the primary documentation page, combining narrative content with interactive examples. The structure follows a consistent pattern that guides users from installation through usage examples to API reference, ensuring developers can quickly find the information they need.

```mdx
// component-name.mdx

{/* Import Storybook documentation blocks */}
import { ArgTypes, Canvas, Meta, Subtitle, Title } from '@storybook/blocks';
import LinkTo from '@storybook/addon-links/react';
import { Callout } from '@/\_storybook/components';

{/* Import all stories from the corresponding .stories file */}
import \* as ComponentStories from './component-name.stories';

{/* Link this MDX file to the stories */}

<Meta of={ComponentStories} />

{/* Component title and brief description */}

<Title>Component Name</Title>
Brief 1-2 sentence description of the component and its primary purpose.

{/* Table of Contents - Optional for simple components, recommended for complex ones */}

<Subtitle>Table of contents</Subtitle>- How to use it - Framework integration -
When to use it - Component preview - States - Form integration - JavaScript API
- CSS custom properties - Accessibility - Properties - Interact with the
component - Related components

{/* Installation and basic setup */}

<Subtitle>How to use it</Subtitle>
Installation steps, import statements, registration, and basic HTML usage
example.

{/* Framework-specific integration examples - Conditional section */}

<Subtitle>Framework integration</Subtitle>
Examples showing how to use the component in different frameworks (Vanilla JS,
React, Vue, Angular). Include property binding, event handling, and
framework-specific patterns.

{/* Usage guidelines and use cases */}

<Subtitle>When to use it</Subtitle>- **Use Case 1**: Description of when to use
this component - **Use Case 2**: Another common scenario

**Best practices:**

- Best practice guidance

**Avoid using when:**

- Scenario where alternative approaches are better

{/* Live interactive examples */}

<Subtitle>Component preview</Subtitle>

<Callout variant="tip" icon="💡">
  You can click on the "Show code" button to see how to use the component.
</Callout>

Basic usage examples with Canvas blocks showcasing different variants and configurations.

<Canvas of={ComponentStories.Default} />
<Canvas of={ComponentStories.Variant} />

{/* Component states - Conditional section */}

<Subtitle>States</Subtitle>
Documentation of different interaction states (disabled, readonly, error,
loading, etc.).

<Canvas of={ComponentStories.Disabled} />
<Canvas of={ComponentStories.Error} />

{/* Form integration - Conditional section for form components */}

<Subtitle>Form integration</Subtitle>
How the component works with HTML forms, validation, and submission. Include
examples of form association and validation patterns.

{/* JavaScript API - Conditional section for components with events/methods */}

<Subtitle>JavaScript API</Subtitle>

**Events:**
List of events the component emits with their payloads.

**Methods:**
Public methods available for programmatic control.

Code examples showing event listeners and method calls.

{/* CSS customization - Conditional section */}

<Subtitle>CSS custom properties</Subtitle>
List of CSS custom properties (CSS variables) available for styling
customization. Include default values and usage examples.

{/* Accessibility considerations */}

<Subtitle>Accessibility</Subtitle>- **ARIA attributes**: Roles and attributes
used - **Keyboard navigation**: Supported keyboard interactions - **Screen
reader support**: How the component is announced - **Focus management**: Focus
indicators and tab order - **Best practices**: Recommendations for accessible
usage

{/* API reference - auto-generated */}

<Subtitle>Properties</Subtitle>
<ArgTypes of={ComponentStories} />

{/* Link to interactive story */}

<Subtitle>Interact with the component</Subtitle>
To interact with the component, test actions, verify accessibility compliance,
and perform visual testing, navigate to the
<LinkTo title={ComponentStories.default.title} story="default">
  Default
</LinkTo>
section.

{/* Cross-references - Optional section */}

<Subtitle>Related components</Subtitle>
See also:
<LinkTo title="Components/Category/RelatedComponent">Related Component</LinkTo>
```

**Benefits of MDX:**

- ✅ **Tailored user experience** — Guide users through installation, usage, and examples.
- ✅ **Design rationale** — Explain "when to use" and "why" the component exists.
- ✅ **Cross-linking** — Use `LinkTo` for navigation between related components.
- ✅ **Custom layout** — Control visual hierarchy with custom CSS classes.

---

**Story File Structure:**

Story files define interactive examples and control configurations for components. They export story objects that render component variations, configure controls for the Storybook UI, and provide live examples that can be referenced from MDX documentation pages. Each story serves as both an interactive demo and a reusable code example.

```typescript
// my-button.stories.tsx

// Import custom Storybook types for type safety
import type { BorealStoryMeta, BorealStory } from "@/types/stories";

// Import Lit for rendering templates
import { html, nothing } from "lit";

// Define all args that will be available in stories
type StoryArgs = {
  variant: "primary" | "secondary" | "danger";
  disabled: boolean;
  size: "sm" | "md" | "lg";
};

// Meta configuration - applies to all stories in this file
const meta = {
  title: "Components/Actions/Button", // Storybook sidebar location
  component: "bds-button", // Web component tag name

  // Define controls for the Storybook UI
  argTypes: {
    variant: {
      control: "select",
      options: ["primary", "secondary", "danger"],
      description: "Visual style variant of the button",
      table: {
        category: "Core", // Group related controls together
        type: { summary: `'primary' | 'secondary' | 'danger'` },
        defaultValue: { summary: "primary" },
      },
    },
    disabled: {
      control: "boolean",
      description: "Disables button interaction",
      table: {
        category: "Core",
        type: { summary: "boolean" },
        defaultValue: { summary: "false" },
      },
      if: { arg: "disabled", neq: false }, // Hide control when false
    },
  },

  // Default values for all stories
  args: {
    variant: "primary",
    disabled: false,
  },
} satisfies BorealStoryMeta<StoryArgs>;

export default meta;
type Story = BorealStory<StoryArgs>;

/**
 * Default button story - appears first in Storybook
 */
export const Default: Story = {
  render: (args) => html`
    <bds-button variant=${args.variant} ?disabled=${args.disabled}>
      Click me
    </bds-button>
  `,
};

/**
 * Interactive example demonstrating event emission
 */
export const WithEvent: Story = {
  render: () => {
    // Event handler defined inside render function
    const handleClick = (e: CustomEvent) => {
      console.log("Button clicked:", e.detail);
    };

    return html`
      <bds-button @bdsClick=${handleClick}> Click to see event </bds-button>
    `;
  },
  parameters: {
    docs: {
      description: {
        // Additional context shown in the docs
        story:
          "Demonstrates the `bdsClick` event emission. Check browser console.",
      },
    },
  },
};
```

**Key Story Patterns:**

| Pattern                   | Usage                                                                                     | Example                                                                  |
| ------------------------- | ----------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ |
| **Property binding**      | Use `${value}` for strings, `?${boolean}` for booleans, `.${property}` for objects/arrays | `variant=${args.variant}` `?disabled=${args.disabled}`                   |
| **Conditional rendering** | Import `nothing` from Lit for conditional slots                                           | `${args.icon ? html`<col-icon name=${args.icon}></col-icon>` : nothing}` |
| **Event handling**        | Use `@eventName=${handler}` for declarative event binding                                 | `@buttonClick=${handleClick}`                                            |
| **Story-specific code**   | Override generated code with `parameters.docs.source.code` for clarity                    | See `col-toast.stories.tsx:204-224`                                      |
| **Hidden stories**        | Use `tags: ['!dev']` to hide internal/demo stories from navigation                        | `tags: ['!dev']` (story still accessible via MDX `LinkTo`)               |

#### Required Stories Per Component

Create comprehensive stories covering all component states and use cases:

| Story Type        | Purpose                                | Example                                 |
| ----------------- | -------------------------------------- | --------------------------------------- |
| **Default**       | Component with default props           | `Primary.args = { variant: 'primary' }` |
| **All Variants**  | All visual variants/states in one view | Grid of all button variants             |
| **Interactive**   | Demonstrates events and interactivity  | Button with click handler logging       |
| **With Content**  | Different content scenarios            | Long text, icons, empty state           |
| **Accessibility** | Focus states, keyboard navigation      | Tab order, keyboard activation demo     |
| **Edge Cases**    | Boundary conditions                    | Extremely long text, overflow handling  |
| **Responsive**    | Different viewport sizes               | Mobile, tablet, desktop layouts         |

#### TypeScript Type Safety

Use custom Storybook types for enhanced type checking and consistency:

```typescript
import type { BorealStoryMeta, BorealStory } from "@/types/stories";

// Define story arguments type
type StoryArgs = {
  variant: "primary" | "secondary" | "danger";
  disabled: boolean;
  size: "sm" | "md" | "lg";
};

// Type-safe meta object
const meta: BorealStoryMeta<StoryArgs> = {
  title: "Components/Actions/Button",
  component: "bds-button",
  argTypes: {
    // Fully typed argTypes
  },
};

export default meta;

// Type-safe story definition
type Story = BorealStory<StoryArgs>;
```

**Benefits:**

- ✅ Full TypeScript autocomplete for args
- ✅ Compile-time error detection
- ✅ Consistent typing across all stories
- ✅ IDE IntelliSense support

---

#### ArgTypes Organization

**Control Order:**

The order of controls in Storybook's controls panel is determined by the **order of properties in `argTypes`**, not by categories. Manually arrange properties for desired order:

```typescript
argTypes: {
  // Core properties first
  variant: { /* ... */ table: { category: 'Core' } },
  disabled: { /* ... */ table: { category: 'Core' } },

  // Appearance properties second
  size: { /* ... */ table: { category: 'Appearance' } },

  // Storybook-only controls last
  iconVisible: { /* ... */ table: { category: 'Storybook Controls' } },
}
```

**Category Configuration:**

```typescript
argTypes: {
  variant: {
    control: 'select',
    options: ['primary', 'secondary'],
    description: 'Visual style variant',
    table: {
      type: { summary: 'string' },
      defaultValue: { summary: 'primary' },
      category: 'Core',  // Groups related controls
    },
  },
}
```

**Storybook-Only Controls:**

For controls that don't represent component props (slots, visual toggles):

```typescript
argTypes: {
  // Real component props first...
  variant: { /* ... */ },

  // Storybook-only controls last
  iconVisible: {
    control: 'boolean',
    description: 'Toggles icon slot visibility. **Storybook control only, not a component prop.**',
    table: {
      category: 'Storybook Controls',
      disable: true,  // Hide from docs table, show in Canvas controls
    },
  },
  iconName: {
    control: 'select',
    options: ['search', 'user', 'settings'],
    description: 'Icon name for slot. **Storybook control only, not a component prop.**',
    if: { arg: 'iconVisible' },  // Conditional visibility
    table: { category: 'Storybook Controls' },
  },
},
args: {
  variant: 'primary',
  // Storybook-only controls at end
  iconVisible: false,
  iconName: 'search',
}
```

**Key Rules:**

- Always add note: `**Storybook control only, not a component prop.**`
- Use `table.disable: true` to hide from docs but keep in Canvas
- Place at end of `args` object
- Use separate category: `Storybook Controls` or `Slots`

---

#### Conditional Controls with `if` Property

Show/hide controls based on other control values for cleaner controls panel:

**Implementation:**

```typescript
// 1. Set "hidden" defaults in args
args: {
  label: '',           // Empty = hidden
  helper: '',          // Empty = hidden
  disabled: false,     // False = hidden
  maxLength: 0,        // Zero = hidden
}

// 2. Add conditional logic in argTypes
argTypes: {
  label: {
    control: 'text',
    description: 'Label text for the input',
    if: { arg: 'label', neq: '' },  // Only show when not empty
    table: { category: 'Core' },
  },
  helper: {
    control: 'text',
    description: 'Helper text below input',
    if: { arg: 'helper', neq: '' },
    table: { category: 'Core' },
  },
  disabled: {
    control: 'boolean',
    description: 'Disables the input',
    if: { arg: 'disabled', neq: false },  // Only show when true
    table: { category: 'State' },
  },
  maxLength: {
    control: 'number',
    description: 'Maximum character count',
    if: { arg: 'maxLength', neq: 0 },
    table: { category: 'Validation' },
  },
}

// 3. Override in individual stories
export const WithLabel: Story = {
  args: {
    label: 'Username',  // Shows label control
  },
};

export const Disabled: Story = {
  args: {
    disabled: true,  // Shows disabled control
  },
};
```

**Supported Conditions:**

- `eq` - equals value
- `neq` - not equals value
- `truthy` - is truthy
- `exists` - property exists

**Benefits:**

- ✅ Cleaner controls panel
- ✅ Focused documentation
- ✅ Reduced cognitive load
- ✅ Better UX for story exploration

---

#### Layout Parameter Configuration

Control how stories are positioned in Storybook's Canvas:

**Available Layouts:**

| Layout         | Use Case                 | Example                                 |
| -------------- | ------------------------ | --------------------------------------- |
| `'centered'`   | Small components         | Buttons, badges, icons                  |
| `'fullscreen'` | Full-width components    | Navigation, headers, dashboards         |
| `'padded'`     | Default, most components | Standard components with breathing room |

**Implementation Levels:**

```typescript
// Global (in .storybook/preview.js)
const preview = {
  parameters: {
    layout: "centered", // Default for all stories
  },
};

// Component level (in meta)
const meta: Meta = {
  title: "Organisms/Site Menu",
  component: "bds-site-menu",
  parameters: {
    layout: "fullscreen", // Override for this component
  },
};

// Individual story level
export const MobileView: Story = {
  parameters: {
    layout: "fullscreen", // Override for this story
  },
};
```

**When to Use:**

- **`fullscreen`**: Navigation, site menus, headers, sidebars, dashboards
- **`centered`**: Buttons, badges, inputs, small UI elements
- **`padded`**: General-purpose components (default)

---

#### Property Binding vs HTML Attributes

For components with `reflect: true` properties, use **HTML attribute syntax** instead of property binding to ensure code snippets appear in documentation:

```typescript
// ✅ CORRECT - Shows in generated code snippets
const renderComponent: Story["render"] = (args) => html`
  <bds-select value=${args.value || nothing} label=${args.label || nothing}>
  </bds-select>
`;

// ❌ INCORRECT - Doesn't appear in code snippets
const renderComponent: Story["render"] = (args) => html`
  <bds-select
    .value=${args.value}      // Property binding hidden from docs
    .label=${args.label}      // Property binding hidden from docs
  >
  </bds-select>
`;
```

**Why This Matters:**

- **Code snippet generation** - `formatCodeString()` only shows HTML attributes
- **Documentation clarity** - Developers see actual HTML syntax
- **`reflect: true` compatibility** - Works because properties sync to attributes
- **Consistency** - Matches other attribute usage patterns

---

#### Hiding Stories from Navigation

Use `tags: ['!dev']` to hide stories from sidebar while keeping them available for MDX documentation:

```typescript
export const InternalExample: Story = {
  args: {
    variant: "internal",
  },
  render: renderComponent,
  tags: ["!dev"], // Hidden from navigation, available for MDX
};
```

**When to Use:**

- Stories meant only for MDX embedding
- Reducing sidebar clutter
- Internal/example stories not for standalone viewing

**In MDX:**

```mdx
import * as ButtonStories from "./button.stories";

## Internal Example

<Canvas of={ButtonStories.InternalExample} />
```

---

#### Excluding Non-Story Exports

Use `excludeStories` to prevent template functions and utilities from being treated as stories:

```typescript
const meta: Meta = {
  title: "Components/Grid",
  component: "bds-grid",
  excludeStories: [
    "GridTemplates", // Template functions
    "MockData", // Mock data objects
    "renderHelper", // Utility functions
  ],
};

// Not treated as a story
export const GridTemplates = {
  twoColumn: () => renderGrid({ cols: "2" }),
  threeColumn: () => renderGrid({ cols: "3" }),
};

// Actual story
export const Default: Story = {
  render: GridTemplates.twoColumn,
};
```

**Benefits:**

- ✅ Reusable template functions
- ✅ Cleaner navigation
- ✅ Better performance
- ✅ Organization without clutter

---

#### Dynamic Story Links in MDX

Use `LinkTo` component for dynamic, type-safe links that auto-update:

```mdx
import LinkTo from "@storybook/addon-links/react";
import * as ButtonStories from "./button.stories";

## See Also

Navigate to the <LinkTo title={ButtonStories.default.title} story="primary">Primary Button</LinkTo> story.

<!-- Cross-component links -->

import DrawerMeta from '../drawer/drawer.stories';
<LinkTo title={DrawerMeta.title} story="default">Drawer component</LinkTo

>
```

**Benefits:**

- ✅ Auto-updates when story titles change
- ✅ TypeScript catches broken references
- ✅ No manual URL management
- ✅ Consistent linking approach

**Avoid:**

- ❌ Hardcoded markdown links: `[Button](/story/button--primary)`
- ❌ Manual URL construction

---

#### Form Component Story Patterns

For form components, demonstrate real-world integration with `<form>` elements and interactive examples.

**Basic Form Integration:**

```typescript
export const FormIntegration: Story = {
  render: (args) => {
    const handleSubmit = (event: Event) => {
      // Check if FormValidationController prevented submission
      if (event.defaultPrevented) {
        console.log("Form submission blocked by validation");
        return;
      }

      event.preventDefault();

      // Process form data only if validation passed
      const form = event.target as HTMLFormElement;
      const formData = new FormData(form);
      const data = Object.fromEntries(formData.entries());
      console.log("Form submitted:", data);
    };

    return html`
      <form @submit=${handleSubmit}>
        <bds-text-field
          name="username"
          label="Username"
          required
          .value=${args.value}
        ></bds-text-field>

        <bds-button type="submit">Submit</bds-button>
      </form>
    `;
  },
};
```

---

**Advanced Interactive Form Example:**

Create comprehensive form examples with code highlighting and live output display:

```typescript
import { html } from "lit";
import { action } from "@storybook/addon-actions";
import hljs from "highlight.js/lib/core";
import type { ColibriStoryMeta, ColibriStory } from "@/types/storybook";

export const InteractiveFormExample: Story = {
  name: "Interactive Form Example",
  parameters: {
    controls: { disable: true },
    docs: {
      source: {
        // Transform the code snippet to show only the form HTML
        transform: (code: string) => {
          // Extract only the <form> element from the full story code
          const formMatch = code.match(
            /<form[^>]*slot="form"[^>]*>[\s\S]*?<\/form>/,
          );
          return formatCodeString(formMatch?.[0] || "");
        },
      },
    },
  },
  render: () => {
    const formId = "text-field-form-example";
    const outputId = "text-field-form-output";

    // Detect if story is in docs mode vs story mode
    const isInDocs = window.location.search.includes("viewMode=docs");

    // Highlight JavaScript code snippet for display
    const codeSnippet = hljs.highlightAuto(`
      // Handle form submit with FormValidationController
      form.addEventListener('submit', (event) => {
        // Check if validation was already prevented
        if (event.defaultPrevented) {
          console.log('Form submission blocked by validation');
          return;
        }

        // Prevent page reload
        event.preventDefault();

        // Process form data only if validation passed
        const formData = new FormData(form);
        const formValues = Object.fromEntries(formData.entries());
        console.log('Form submitted successfully:', formValues);
      });

      // Handle form reset - FormResetController handles component reset automatically
      form.addEventListener('reset', (event) => {
        // Only handle UI cleanup - components reset automatically
        console.log('Form reset completed');
      });
    `).value;

    return html`
      <form-demo
        form-id="${formId}"
        output-id="${outputId}"
        title="Login Form"
        code-snippet="${codeSnippet}"
        code-theme="dark"
      >
        <form slot="form" id="${formId}" class="form-container">
          <bds-text-field
            id="username"
            name="username"
            label="Username"
            value="John Doe"
            helper="Your public display name."
            required
            min-length="3"
            custom-width="100%"
          ></bds-text-field>

          <bds-text-field
            id="password"
            name="password"
            label="Password"
            input-type="password"
            value="password123"
            required
            min-length="8"
            helper="Must be at least 8 characters long."
            custom-width="100%"
          ></bds-text-field>

          <bds-text-field
            id="email"
            name="email"
            label="Email (Optional)"
            input-type="text"
            value="john.doe@example.com"
            pattern="^\\S+@\\S+\\.\\S+$"
            error-message="Please enter a valid email address."
            validation-timing="input"
            helper="We will use this to contact you."
            custom-width="100%"
          ></bds-text-field>

          <bds-button-group>
            <!-- Disable buttons in docs mode to prevent form submission -->
            <bds-button type="submit" ?disabled=${isInDocs}>Submit</bds-button>
            <bds-button type="reset" ?disabled=${isInDocs}>Reset</bds-button>
          </bds-button-group>
        </form>
      </form-demo>
    `;
  },
};
```

**Key Techniques:**

1. **Code Snippet Transformation (`parameters.docs.source.transform`)**
   - Extracts only relevant code (form HTML) from full story
   - Uses regex to match `<form>` element with `slot="form"`
   - Shows clean, focused code in MDX documentation
   - Hides story boilerplate (IDs, wrapper components)

2. **Syntax Highlighting with highlight.js**
   - Import: `import hljs from 'highlight.js/lib/core'`
   - Use `hljs.highlightAuto(code)` for automatic language detection
   - Returns highlighted HTML in `.value` property
   - Pass to custom `<form-demo>` component for display
   - **Alternative**: Import specific language for smaller bundle:
     ```typescript
     import hljs from "highlight.js/lib/core";
     import javascript from "highlight.js/lib/languages/javascript";
     hljs.registerLanguage("javascript", javascript);
     ```

3. **Docs vs Story Mode Detection (`isInDocs`)**
   - Check: `window.location.search.includes('viewMode=docs')`
   - Returns `true` when story is rendered in MDX docs page
   - Returns `false` when story is rendered in interactive canvas
   - Use to disable interactive elements in docs (prevent form submission screenshots)
   - Apply with boolean attribute: `?disabled=${isInDocs}`

4. **Custom Demo Components**
   - Create reusable `<form-demo>` wrapper component
   - Displays form + code snippet + live output side-by-side
   - Accepts props: `form-id`, `output-id`, `title`, `code-snippet`, `code-theme`
   - Slots: `<form slot="form">` for form content

**Two-Event-Handler Pattern:**

Form validation uses capture phase (FormValidationController) + bubble phase (custom handler):

1. **FormValidationController** (capture phase):
   - Validates all fields before submission
   - Calls `event.preventDefault()` if validation fails

2. **Custom handler** (bubble phase):
   - Checks `event.defaultPrevented` to detect blocked submission
   - Processes data only if validation passed

**Best Practices:**

- ✅ Always use real `<form>` elements
- ✅ Check `event.defaultPrevented` before processing form data
- ✅ Use `parameters.docs.source.transform` to show clean code in MDX
- ✅ Disable interactive buttons in docs mode with `isInDocs` check
- ✅ Highlight code snippets with `hljs.highlightAuto()` for better readability
- ✅ Demonstrate validation states (required, pattern, min-length, error messages)
- ✅ Show accessibility features (labels, helper text, error messages)
- ✅ Include form reset handling (FormResetController handles component reset automatically)

---

#### Story Styling Best Practices

Use Lit's `css` template literal to define reusable, scoped styles for stories. This avoids inline styles and improves maintainability.

**Why Use `css` from Lit?**

- ✅ **Scoped styles** — Styles are isolated to story examples, won't affect other components
- ✅ **Reusability** — Define styles once, reuse across multiple stories
- ✅ **Type safety** — TypeScript autocomplete for CSS properties
- ✅ **Performance** — Lit optimizes CSS templates for efficient rendering
- ✅ **CSS variables** — Leverage design tokens and theme variables

**Pattern:**

```typescript
import { html, css } from "lit";
import type { ColibriStoryMeta, ColibriStory } from "@/types/storybook";

// Define styles using Lit's css template literal
const styles = css`
  .demo-container {
    padding: 16px;
    border-radius: 4px;
    background: var(--my-theme-background);
    font-family: var(--my-typography-font-family);
  }

  .grid-item {
    padding: 12px;
    text-align: center;
    color: var(--my-theme-text-primary);
    background: var(--my-theme-primary-base);
    border: 1px solid var(--my-theme-primary-lighter);
  }

  .story-section {
    margin-bottom: 2rem;
  }

  .info-text {
    font-size: 0.875rem;
    color: var(--my-theme-text-secondary);
    margin-bottom: 1rem;
  }
`;

// Reusable render function that includes styles
const renderGrid = (args: GridArgs, items: TemplateResult[]) => html`
  <!-- Inject styles into the story -->
  <style>
    ${styles}
  </style>

  <!-- Use CSS classes defined above -->
  <div class="demo-container">
    <bds-grid cols=${args.cols} gap=${args.gap}>
      ${items.map((item) => html`<div class="grid-item">${item}</div>`)}
    </bds-grid>
  </div>
`;

export const Default: Story = {
  render: (args) =>
    renderGrid(args, [html`Item 1`, html`Item 2`, html`Item 3`, html`Item 4`]),
};

export const WithInfo: Story = {
  render: (args) => html`
    <style>
      ${styles}
    </style>
    <div class="story-section">
      <p class="info-text">
        This example demonstrates responsive grid behavior
      </p>
      ${renderGrid(args, [html`A`, html`B`, html`C`])}
    </div>
  `,
};
```

**Key Benefits:**

| Approach           | Issues                                       | `css` Method Approach         |
| ------------------ | -------------------------------------------- | ----------------------------- |
| Inline styles      | Hard to maintain, repetitive, no reusability | Centralized, reusable, scoped |
| `<style>` strings  | No syntax highlighting, error-prone          | Type-safe, autocomplete       |
| External CSS files | Global scope pollution, hard to track usage  | Scoped to stories only        |
| Style props        | Component-specific, verbose for demos        | Clean separation of concerns  |

**Best Practices:**

- ✅ Use CSS custom properties (design tokens) for theming
- ✅ Keep styles scoped to story examples (don't style actual components)
- ✅ Group related styles by story section (`.grid-item`, `.demo-container`, etc.)
- ✅ Inject styles in render function using `<style>${styles}</style>`
- ✅ Share style definitions across multiple stories in the same file
- ❌ Don't use inline `style=""` attributes for complex styling
- ❌ Don't define global styles that affect components outside stories

---

#### Reusable Story Patterns

Create shared render functions and styles to reduce duplication:

```typescript
// Shared styles for all button stories
const styles = css`
  .button-demo {
    display: flex;
    gap: 1rem;
    padding: 1rem;
    background: var(--demo-background);
  }
`;

// Shared render function
const renderButton: Story["render"] = (args) => html`
  <style>
    ${styles}
  </style>
  <div class="button-demo">
    <my-button
      variant=${args.variant}
      ?disabled=${args.disabled}
      size=${args.size || nothing}
    >
      ${args.label}
      ${args.iconName
        ? html`<my-icon slot="icon-start" name=${args.iconName}></my-icon>`
        : nothing}
    </my-button>
  </div>
`;

// Reuse across stories
export const Primary: Story = {
  args: { variant: "primary", label: "Primary" },
  render: renderButton,
};

export const WithIcon: Story = {
  args: { variant: "primary", label: "Save", iconName: "save" },
  render: renderButton,
};
```

**Reusability Strategies:**

1. **Shared render functions** — Extract common rendering logic (see "Story Styling Best Practices" for style handling)
2. **Template collections** — Export reusable template objects for complex stories
3. **Helper functions** — Create utilities for generating grid items, form fields, etc.
4. **Style definitions** — Use `css` template literal for scoped, reusable styles
5. **Reusable Storybook components** — See "Reusable Storybook Components" section below

---

#### Reusable Storybook Components

Create specialized components for documentation and story examples. Understanding the distinction between React and Lit components is crucial for proper usage.

**Two Component Types:**

| Type                         | Technology           | Usage                        | Location                      | Import Pattern                                      |
| ---------------------------- | -------------------- | ---------------------------- | ----------------------------- | --------------------------------------------------- |
| **Documentation Components** | React (TSX)          | MDX files only               | `_storybook/components/*.tsx` | `import { Callout } from '@/_storybook/components'` |
| **Story Components**         | Lit (Web Components) | Story files (`.stories.tsx`) | `_storybook/components/*.ts`  | `import '@/_storybook/components/CodeBlock'`        |

**Why Two Types?**

- **MDX files** use React for rendering documentation blocks (Storybook's MDX renderer is React-based)
- **Story files** use Lit for rendering interactive examples (aligned with Storybook web components default library)

---

**React Components (for MDX Documentation):**

Use React components for custom documentation elements in `.mdx` files.

**Example: Callout Component**

```tsx
// _storybook/components/Callout/Callout.tsx
import React from "react";
import styles from "./Callout.module.css";

export interface CalloutProps {
  variant: "info" | "tip" | "warning" | "error";
  icon?: string;
  children: React.ReactNode;
}

/**
 * A React component for highlighting important information in MDX documentation
 *
 * Usage: MDX files only (not compatible with story files)
 */
export const Callout: React.FC<CalloutProps> = ({
  variant,
  icon,
  children,
}) => {
  return (
    <div className={`${styles.callout} ${styles[variant]}`}>
      {icon && <div className={styles.icon}>{icon}</div>}
      <div className={styles.content}>{children}</div>
    </div>
  );
};
```

**Usage in MDX:**

```mdx
// my-button.mdx
import { Callout } from '@/\_storybook/components';

<Callout variant="info" icon="ℹ️">
  This component requires a minimum width of 48px for accessibility.
</Callout>

<Callout variant="warning" icon="⚠️">
  <p>Warning: This action cannot be undone.</p>
</Callout>

<Callout variant="tip" icon="💡">
  Pro tip: Use the `variant` prop to match your design system.
</Callout>
```

---

**Lit Components (for Story Files):**

Use Lit web components for interactive elements within story examples.

**Example: CodeBlock Component**

```typescript
// _storybook/components/CodeBlock/CodeBlock.ts
import { LitElement, html, css } from "lit";
import { customElement, property } from "lit/decorators.js";
import { unsafeHTML } from "lit/directives/unsafe-html.js";

/**
 * A Lit web component for syntax-highlighted code blocks in story examples
 *
 * Usage: Story files (.stories.tsx) only
 */
@customElement("code-block")
export class CodeBlock extends LitElement {
  static styles = css`
    .code-block-container {
      background: var(--code-background);
      border-radius: 4px;
      padding: 1rem;
    }
  `;

  @property({ type: String })
  code = "";

  @property({ type: String, attribute: "code-theme" })
  codeTheme = "dark";

  @property({ type: String })
  language = "";

  @property({ type: String })
  title = "";

  render() {
    return html`
      <div class="code-block-container">
        ${this.title ? html`<h3>${this.title}</h3>` : ""}
        <pre><code class="language-${this.language}">${unsafeHTML(
          this.code,
        )}</code></pre>
      </div>
    `;
  }
}

// TypeScript declaration for better IDE support
declare global {
  interface HTMLElementTagNameMap {
    "code-block": CodeBlock;
  }
}
```

**Usage in Stories:**

```typescript
// my-button.stories.tsx
import { html } from "lit";
import "@/_storybook/components/CodeBlock";

export const WithCodeExample: Story = {
  render: () => html`
    <code-block
      code="const example = 'Hello World';"
      language="javascript"
      code-theme="dark"
      title="JavaScript Example"
    ></code-block>
  `,
};
```

---

**Component Organization:**

```
_storybook/
├── components/
│   ├── Callout/               # React component for MDX
│   │   ├── Callout.tsx
│   │   ├── Callout.module.css
│   │   └── index.ts
│   ├── CodeBlock/             # Lit component for stories
│   │   ├── CodeBlock.ts
│   │   ├── CodeBlock.styles.ts
│   │   └── index.ts
│   ├── FormDemo/              # Lit component for stories
│   │   ├── FormDemo.ts
│   │   └── index.ts
│   └── index.ts               # Central export
```

**Best Practices:**

- ✅ **React for MDX** — Use React components for custom documentation blocks, callouts, cards
- ✅ **Lit for stories** — Use Lit components for interactive demo wrappers, layout helpers
- ✅ **Clear naming** — Name components descriptively (e.g., `FormDemo`, `CodeBlock`, `Callout`)
- ✅ **Type declarations** — Add global `HTMLElementTagNameMap` for Lit components
- ✅ **JSDoc comments** — Document usage restrictions (MDX vs story files)
- ✅ **Central exports** — Export all components from `_storybook/components/index.ts`
- ❌ **Don't mix** — Never import React components in story files or Lit components in MDX files
- ❌ **Avoid complexity** — Keep reusable components simple and focused on one purpose

---

#### Story Organization Best Practices

**Story Organization:**

1. **Group by feature domain** - `Components/Actions/Button`, `Components/Forms/TextField`
2. **Use descriptive titles** - Clear hierarchy in sidebar navigation
3. **Tag with `autodocs`** - Automatic API documentation generation
4. **Document story purpose** - Use JSDoc comments and `parameters.docs.description.story`

**Example:**

```typescript
/**
 * Primary button variant for main call-to-action.
 * Limit to one primary button per screen or section.
 */
export const Primary: Story = {
  args: { variant: "primary" },
  render: renderButton,
  parameters: {
    docs: {
      description: {
        story: "Use primary buttons for the main action on a page or section.",
      },
    },
  },
};
```

---

### 5.4 User-Friendly Documentation (Notion/Confluence)

Complement Storybook with high-level, navigable documentation for non-technical teams.

#### Recommended Approach: Notion

**Why Notion:**

- ✅ Beautiful, intuitive UI (designer-friendly)
- ✅ Excellent embedding (Storybook iframes, Figma, videos)
- ✅ Great navigation (sidebar, breadcrumbs, backlinks, search)
- ✅ Inline comments and collaboration
- ✅ Public sharing for external stakeholders
- ✅ Database views for component tracking
- ✅ Proven pattern ([Aqua DS example](https://masivapp.notion.site/Components-2011de3976b9801388eadaacd389ee67))

**Pricing:**

| Tier           | Cost           | Features                              | Recommendation                   |
| -------------- | -------------- | ------------------------------------- | -------------------------------- |
| **Free**       | $0             | 10 guests, limited blocks             | Small teams (<5 users)           |
| **Plus**       | $10/user/month | Unlimited blocks, 100 guests          | Growing teams                    |
| **Business**   | $18/user/month | SSO, 250 guests, advanced permissions | **← Recommended for enterprise** |
| **Enterprise** | $25/user/month | SAML SSO, unlimited guests, audit log | Large organizations              |

**Estimated Cost:** ~$1,440/year for 6-8 UX/dev leads with edit access (unlimited read-only guests)

**Setup Instructions:**

1. Create Notion workspace: "PxG Component Library"
2. Use database view for component gallery
3. Embed Storybook iframes for live previews
4. Link to full Storybook for technical details
5. Set up page templates for consistency

**Recommended Structure:**

```
📚 PxG Component Library (Home)
├── 🆕 Quick Start
│   ├── Installation
│   ├── Getting Started
│   └── Migration Guide
├── 🔧 Framework Implementation
│   ├── Web Components
│   ├── Vue 3
│   ├── React
│   └── Angular
├── ⚛️ Components (Database View)
│   ├── 🏃 Actions
│   │   ├── Button
│   │   ├── Dropdown
│   │   └── Toggle
│   ├── 📝 Forms
│   │   ├── TextField
│   │   ├── Checkbox
│   │   └── Radio
│   ├── 🔔 Feedback
│   │   ├── Badge
│   │   ├── Banner
│   │   └── Toast
│   ├── 🗂️ Data
│   │   ├── Card
│   │   ├── Table
│   │   └── Pagination
│   └── 🧭 Navigation
│       ├── Tabs
│       ├── Breadcrumb
│       └── Steps
├── 🎨 Theming & Customization
│   ├── Design Tokens
│   ├── Custom Styles
│   └── Dark Mode
├── 💾 Icons
├── ♿ Accessibility Guidelines
├── ⏲️ Changelog
└── ⁉️ FAQ
```

**Component Page Template:**

For each component (e.g., Button), follow this structure:

```markdown
# Button Component

## Overview

Brief description of the button component and its primary purpose.
2-3 sentences maximum.

## When to Use

✅ Triggering immediate actions (submit, cancel, save)
✅ Navigation to other pages or sections
✅ Opening modals or dialogs

❌ Don't use for text links (use Link component)
❌ Don't use for toggle actions (use Toggle component)

## Design Rationale

Explanation of design decisions:

- Why this component exists
- UX principles applied
- Design system alignment
- Accessibility considerations

## Live Preview

[Embedded Storybook iframe showing interactive button variants]

<iframe src="https://storybook.example.com/iframe.html?id=button--all-variants" />

## Variants

### Primary

- **Purpose:** Main call-to-action
- **Usage:** Limit to one per screen/section
- **Example:** "Save Changes", "Submit Form"

### Secondary

- **Purpose:** Less prominent actions
- **Usage:** Supporting actions alongside primary
- **Example:** "Cancel", "Go Back"

### Danger

- **Purpose:** Destructive or irreversible actions
- **Usage:** Confirmation dialogs, delete operations
- **Example:** "Delete Account", "Remove Item"

## Usage Guidelines

### Do's

- ✅ Use clear, action-oriented labels ("Save Changes" not "OK")
- ✅ Provide visual feedback on hover/press
- ✅ Include loading states for async actions
- ✅ Ensure sufficient color contrast (4.5:1 minimum)

### Don'ts

- ❌ Don't use multiple primary buttons on same screen
- ❌ Don't use vague labels ("Click here", "Submit")
- ❌ Don't remove focus indicators
- ❌ Don't use danger variant for non-destructive actions

## Accessibility

**Keyboard Navigation:**

- `Tab` - Focus button
- `Enter` or `Space` - Activate button
- `Escape` - Close if button opens modal

**Screen Reader:**

- Announces as "Button"
- Reads label and state (pressed, disabled)
- Supports aria-label for icon-only buttons

**Focus Management:**

- Visible focus indicator (2px outline)
- Logical tab order
- Disabled buttons removed from tab order

**WCAG Compliance:** Level AA

## Technical Documentation

🔗 [View full API documentation in Storybook →](https://storybook.example.com/?path=/docs/button)

**Quick Reference:**

- **Props:** `variant`, `disabled`, `size`, `type`
- **Events:** `buttonClick`
- **Methods:** `setFocus()`
- **Slots:** `default`, `icon-start`, `icon-end`

## Related Components

- **ButtonGroup** - Group multiple buttons together
- **IconButton** - Button with icon only (no text)
- **Link** - Text links for navigation
- **Toggle** - On/off state switching

## Status

- **Version:** 2.1.0
- **Status:** ✅ Stable
- **Last Updated:** 2025-01-15
- **Breaking Changes:** None since v2.0

## Changelog

- **2.1.0** - Added `size` prop with sm/md/lg options
- **2.0.0** - Renamed `theme` prop to `variant`
- **1.5.0** - Added loading state support
```

#### Fallback: Confluence

**If Notion license not approved**, use Confluence (included in Atlassian license):

**Why Confluence:**

- ✅ Zero additional cost (existing license)
- ✅ Familiar to enterprise teams
- ✅ Jira integration for component requests/issues
- ✅ Page hierarchy and templates
- ✅ Inline comments and @mentions
- ✅ Content versioning

**Trade-offs:**

- ❌ Dated UI (less designer-friendly than Notion)
- ❌ Slower performance with large pages
- ❌ Less intuitive navigation
- ❌ Limited embedding capabilities

**Setup Instructions:**

1. Create Confluence space: "PxG Component Library"
2. Use page tree for component organization
3. Create page template (same structure as Notion template above)
4. Embed Storybook using iframe macro: `{iframe:url=https://storybook.example.com}`
5. Use labels for categorization (actions, forms, feedback, etc.)

**Confluence-Specific Tips:**

- Use **"Content by Label"** macro for dynamic component lists
- Use **"Excerpt"** macro for component summaries on index pages
- Use **"Panel"** macro for callouts (When to Use, Warnings)
- Use **"Code Block"** macro with language highlighting for examples
- Use **"Table of Contents"** macro for navigation within long pages
- Use **"Children Display"** macro to list all component pages

---

### 5.5 Accessibility Documentation

Document accessibility features comprehensively in both Storybook and Notion/Confluence.

#### Required in Storybook

**Accessibility Story:**

```typescript
export const AccessibilityDemo: Story = {
  render: () => html`
    <my-button aria-label="Close dialog" aria-expanded="false">
      <span aria-hidden="true">×</span>
    </my-button>
  `,
  parameters: {
    docs: {
      description: {
        story: `
**Keyboard Navigation:**
- Tab: Focus button
- Enter/Space: Activate button
- Escape: Close (if button controls dialog)

**Screen Reader:**
- Announces as "Close dialog, button"
- aria-expanded communicates dialog state
- Icon hidden from screen readers (aria-hidden)

**WCAG Compliance:**
- Level AA compliant
- 4.5:1 color contrast ratio
- Visible focus indicator (2px outline)
- Touch target size 44×44px minimum

**Testing:**
- Automated: axe-core via Chromatic
- Manual: Keyboard navigation verified
- Screen reader: Tested with VoiceOver, NVDA
        `,
      },
    },
    a11y: {
      config: {
        rules: [
          {
            id: "button-name",
            enabled: true,
          },
          {
            id: "color-contrast",
            enabled: true,
          },
        ],
      },
    },
  },
};
```

#### Required in Notion/Confluence

Document high-level accessibility for non-technical stakeholders:

**Accessibility Page Template:**

```markdown
# Accessibility Guidelines

## Component Accessibility Summary

### Keyboard Navigation

All components support keyboard navigation:

- **Tab**: Move focus between interactive elements
- **Enter/Space**: Activate buttons and controls
- **Escape**: Close modals, dropdowns, menus
- **Arrow Keys**: Navigate within lists, menus, tabs

### Screen Reader Support

Components include proper ARIA attributes:

- Semantic HTML elements (button, input, nav)
- ARIA labels for icon-only controls
- ARIA roles for custom widgets
- Live regions for dynamic content

### Visual Accessibility

- **Color Contrast**: WCAG AA (4.5:1) or AAA (7:1)
- **Focus Indicators**: Visible 2px outline
- **Text Sizing**: Scalable with browser zoom
- **Touch Targets**: Minimum 44×44px

### Testing Requirements

✅ Automated testing via Chromatic (axe-core)
✅ Keyboard navigation verification
✅ Screen reader testing (VoiceOver, NVDA, JAWS)
✅ Color contrast validation
✅ Zoom testing (up to 200%)

## Common Pitfalls to Avoid

❌ Using `<div>` instead of `<button>` for clickable elements
❌ Missing alt text on images
❌ Removing focus outlines for aesthetic reasons
❌ Color-only information (use icons + color)
❌ Insufficient color contrast
❌ Keyboard traps in modals/dropdowns
```

---

### 5.6 Custom Elements Manifest (CEM)

The Custom Elements Manifest is a machine-readable JSON file format that describes custom elements in your project. It provides metadata about components including properties, methods, attributes, events, slots, CSS Shadow Parts, and CSS custom properties.

#### Benefits

- **IDE Integration** - Enables autocomplete, IntelliSense, and inline documentation in VS Code and JetBrains IDEs
- **Storybook Auto-Documentation** - Automatically generates controls, args, and API tables
- **Framework Integration** - Enables automated generation of React wrappers and framework-specific bindings
- **API Validation** - Detects breaking changes in component APIs during minor/patch version updates
- **Component Cataloging** - Powers component discovery and registry systems
- **Enhanced Linting** - Enables context-aware validation of component usage

CEM is a [community standard](https://github.com/webcomponents/custom-elements-manifest) maintained by the web components community with participation from Google, Adobe, Microsoft, and other industry stakeholders.

#### Installation

```bash
# Install the core analyzer and type expansion plugin
pnpm add -D @custom-elements-manifest/analyzer cem-plugin-expanded-types

# Optional: IDE integration helpers
pnpm add -D custom-element-vs-code-integration custom-element-jet-brains-integration
```

#### Configuration

Create a `cem.config.mjs` file in your project root:

```javascript
import { expandTypesPlugin } from "cem-plugin-expanded-types";

export default {
  globs: ["src/components/**/*.tsx"],
  exclude: ["src/**/*.spec.ts", "src/**/*.stories.ts", "src/**/*.css.ts"],
  stencil: true, // Enable Stencil framework support
  outdir: ".",
  packagejson: true,
  plugins: [expandTypesPlugin({ hideLogs: true })],
};
```

#### Storybook Integration

Enable automatic controls and documentation in Storybook:

```typescript
// .storybook/preview.ts
import { setCustomElementsManifest } from "@storybook/web-components";
import customElements from "../custom-elements.json";

setCustomElementsManifest(customElements);
```

See Section 5.3 for complete Storybook configuration.

#### IDE Integration

Enable autocomplete and inline documentation in VS Code:

**`.vscode/settings.json`**

```json
{
  "html.customData": ["./custom-elements.json"]
}
```

See Section 2.3 for additional IDE integration details.

#### Package Configuration

Declare the manifest location in `package.json`:

```json
{
  "customElements": "custom-elements.json"
}
```

#### Build Integration

Add CEM generation to your build scripts:

```json
{
  "scripts": {
    "cem": "cem analyze --config cem.config.mjs",
    "cem:watch": "cem analyze --config cem.config.mjs --watch",
    "build": "pnpm cem && stencil build",
    "start": "concurrently \"pnpm cem:watch\" \"pnpm dev\""
  }
}
```

**See Also:**

- Section 1.3.X for CEM-compliant JSDoc authoring standards
- Section 8.2 (CI Pipeline & Automated Releases)
- Section 2.4.X for CEM validation in the linting workflow

---

#### Wrapper Package Publishing Standards

These rules apply to `boreal-react` and `boreal-vue` — the Stencil output-target wrapper packages.

**`files` field:** Publish only `dist/`. Never include `lib/` or any other source directory — `lib/` contains auto-generated Stencil proxy files that are TypeScript source and must not be shipped to consumers.

```json
"files": ["dist"]
```

**`sideEffects` field:** Declare `"sideEffects": false` on both wrapper packages. Component proxy modules are pure factories with no module-level side effects. Without this field, webpack 5 bundlers cannot tree-shake unused component exports.

```json
"sideEffects": false
```

If a future pattern emerges where consumers import CSS as a bare side-effect (e.g. `import '@telesign/boreal-react/dist/css/index.css'`), update to `["dist/css/**", "dist/scss/**"]`.

**`types` and `exports.types` paths:** Declaration files must be co-located with JS files in `dist/`. Do not use `declarationDir` in the tsconfig — it splits declarations into a subdirectory that breaks the expected resolution path.

```json
"types": "dist/index.d.ts",
"exports": {
  ".": {
    "import": "./dist/index.js",
    "types": "./dist/index.d.ts"
  }
}
```

**See also:** [ADR 0004](./../decisions/0004-boreal-react-dist-structure.md), [ADR 0008](./../decisions/0008-sideeffects-false-wrapper-packages.md)

---

### 5.7 Changelog Conventions

Maintain a changelog to track component updates, breaking changes, and deprecations.

#### Format

Follow [Keep a Changelog](https://keepachangelog.com/) conventions with semantic versioning.

**Categories:**

| Category       | Purpose                           | Example                                      |
| -------------- | --------------------------------- | -------------------------------------------- |
| **Added**      | New features                      | New `size` prop added                        |
| **Changed**    | Changes to existing functionality | `variant` prop now defaults to 'primary'     |
| **Deprecated** | Soon-to-be-removed features       | `theme` prop deprecated (use `variant`)      |
| **Removed**    | Removed features                  | `legacy` variant removed                     |
| **Fixed**      | Bug fixes                         | Focus ring now visible in high contrast mode |
| **Security**   | Security fixes                    | XSS vulnerability in link sanitization       |

#### Example (CHANGELOG.md)

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [2.1.0] - 2025-01-15

### Added

- **Button**: New `size` prop with 'sm', 'md', 'lg' options
- **TextField**: `maxLength` prop with character counter display
- **Dropdown**: `searchable` prop for filterable options
- **All components**: Support for CSS custom properties for theming

### Changed

- **Button**: `variant` prop now defaults to 'primary' (was 'default')
- **TextField**: Focus border width increased from 1px to 2px for visibility
- **Badge**: Updated color palette to match new design tokens

### Deprecated

- **Dropdown**: `expanded` prop deprecated in favor of `open` (will be removed in v3.0)
- **TextField**: `error-message` attribute deprecated (use `errorMessage` prop)

### Fixed

- **Checkbox**: Focus ring now visible in Windows high contrast mode
- **Table**: Fixed horizontal scroll behavior on mobile viewports
- **Modal**: Escape key now properly closes modal in all browsers
- **Badge**: Resolved color contrast issue in danger variant

### Security

- **Link**: Added URL sanitization to prevent javascript: and data: URLs

## [2.0.0] - 2024-12-01

### Breaking Changes

- **All components**: Updated to Stencil 4.0 (requires Node 18+)
- **Button**: Removed `theme` prop (use `variant` instead)
- **TextField**: `type` property renamed to `inputType` to avoid conflicts
- **Badge**: Removed `legacy` variant (use `secondary` instead)

### Migration Guide

See [Migration Guide v1 → v2](./MIGRATION.md) for detailed upgrade instructions.

## [1.5.0] - 2024-11-01

### Added

- **Button**: Loading state with spinner animation
- **TextField**: Clear button for quick value reset
- **Toast**: Auto-dismiss timeout configuration

### Fixed

- **Dropdown**: Keyboard navigation now properly cycles through options
- **Checkbox**: Click event no longer fires twice
```

#### Update Locations

Maintain changelog in three places:

1. **Root `CHANGELOG.md`** - Comprehensive technical changelog for developers
2. **Notion/Confluence Changelog Page** - User-friendly version with visual examples
3. **Storybook "What's New" Page** - Interactive demos of new features

---

### 5.8 Documentation Maintenance

Establish clear ownership and review cadence to keep documentation accurate and up-to-date.

#### Review Cadence

| Frequency          | Action                                                  | Owner                 |
| ------------------ | ------------------------------------------------------- | --------------------- |
| **Every PR**       | Update Storybook stories for component changes          | Developer (PR author) |
| **Every PR**       | Update JSDoc for API changes                            | Developer (PR author) |
| **Weekly**         | Review and triage Notion/Confluence comments            | UX Lead               |
| **Monthly**        | Audit Notion/Confluence content for accuracy            | Tech Writer / UX Lead |
| **Quarterly**      | Full documentation completeness audit                   | Tech Lead + UX Lead   |
| **Major Releases** | Update all examples, migration guides, breaking changes | Tech Lead             |

#### Ownership

| Documentation Type                       | Primary Owner            | Reviewer        |
| ---------------------------------------- | ------------------------ | --------------- |
| **JSDoc/TSDoc**                          | Component Developer      | Tech Lead       |
| **Storybook Stories**                    | Component Developer      | Tech Lead       |
| **Notion/Confluence - Design Rationale** | UX/UI Team               | Design Lead     |
| **Notion/Confluence - Usage Guidelines** | UX/UI Team + Developer   | Product Owner   |
| **Accessibility Docs**                   | Accessibility Specialist | QA Lead         |
| **Changelog**                            | Tech Lead                | Release Manager |

#### Quality Checklist

Before merging component changes, verify:

- [ ] JSDoc comments updated for all public APIs
- [ ] Storybook stories cover all variants and states
- [ ] Accessibility story includes keyboard/screen reader notes
- [ ] Notion/Confluence page updated (if design/usage changes)
- [ ] Changelog entry added (for user-facing changes)
- [ ] Migration notes written (for breaking changes)
- [ ] Related components cross-referenced

#### Stale Content Detection

Set up alerts for outdated documentation:

- **Notion**: Use "Last Edited" date in database view, flag pages >90 days old
- **Confluence**: Use "Content by Label" macro with "stale-docs" label
- **Storybook**: Add console warnings for deprecated stories
- **Automated**: GitHub Actions to detect missing stories for new components

---

## 6. GIT & VERSION CONTROL

Effective version control practices enable smooth collaboration across multiple teams. This section defines branching strategies, commit message conventions, and merge strategies to maintain a clean, traceable repository history.

### 6.1 Branching Strategy

Boreal DS uses a simplified **trunk-based** model with a single permanent integration and release branch. All development flows through short-lived branches that target `release/current`:

| Branch            | Type      | Description                                                           |
| ----------------- | --------- | --------------------------------------------------------------------- |
| `release/current` | Permanent | Default branch. Reflects the latest published or in-progress release. |
| `feature/`        | Temporal  | Isolated work for a new feature or ticket.                            |
| `fix/`            | Temporal  | Bug fixes.                                                            |
| `bugfix/`         | Temporal  | Fixes for errors found before reaching production.                    |
| `docs/`           | Temporal  | Documentation-only changes.                                           |
| `chore/`          | Temporal  | Housekeeping and non-production changes.                              |

**Branch naming convention:** `type/TICKET-ID_short-description` — e.g. `feature/EOA-10057_add-text-field`.

**Recommendations:**

- All PRs target `release/current`.
- Keep pull requests small and focused — short-lived branches minimise merge conflicts.
- Merge feature branches promptly; do not let them diverge from `release/current` for extended periods.

### 6.2 Commit Message Conventions

All commits must follow [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/). This standard produces a machine-readable history that drives automated changelog generation and SemVer version bumping.

**Core types and their SemVer impact:**

| Type              | Impact                                                                                     | SemVer    |
| ----------------- | ------------------------------------------------------------------------------------------ | --------- |
| `fix`             | Patch or bug fix                                                                           | **PATCH** |
| `feat`            | New feature                                                                                | **MINOR** |
| `BREAKING CHANGE` | Incompatible public API change. Use `BREAKING CHANGE:` footer or `!` suffix on type/scope. | **MAJOR** |

**Additional types (no SemVer impact):**

| Type       | Purpose                                                   |
| ---------- | --------------------------------------------------------- |
| `build`    | Build system or dependency changes                        |
| `chore`    | Housekeeping changes not touching production or test code |
| `ci`       | CI configuration changes                                  |
| `docs`     | Documentation-only changes                                |
| `style`    | Formatting changes (no logic change)                      |
| `refactor` | Code change that neither fixes a bug nor adds a feature   |
| `perf`     | Performance improvements                                  |
| `test`     | Adding or correcting tests                                |

**Examples:**

```
feat: allow provided config object to extend other configs

BREAKING CHANGE: `extends` key in config file is now used for extending other config files
```

```
feat!: send an email to the customer when a product is shipped
```

### 6.3 Merge Strategies

**Squash and merge** is the default for all PRs merging into `release/current`. This keeps the branch history clean: one commit per completed feature or bugfix, formatted as a Conventional Commit, which simplifies changelog generation and reversion.

| Source Branch                          | Target Branch     | Strategy         | Purpose                              |
| -------------------------------------- | ----------------- | ---------------- | ------------------------------------ |
| `feature/`, `fix/`, `bugfix/`, `docs/` | `release/current` | Squash and Merge | Clean, functionally-oriented history |

---

## 7. PULL REQUEST STANDARDS

Pull requests are the primary mechanism for code review and quality assurance. This section establishes PR template requirements, review processes, and approval criteria.

### 7.1 PR Template

The PR template communicates the purpose of the change clearly to reviewers.

| Field             | Content                                                                                                 | Required                             |
| ----------------- | ------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| Title             | Must follow Conventional Commits format                                                                 | Required                             |
| Description       | Brief overview of what's added, its intended purpose (the why), and potential impact on the application | Required                             |
| Task correlation  | Link to the Jira ticket using auto-closing keywords (e.g., `Closes BDS-123`)                            | Required                             |
| Testing           | Specifies tests added or modified for the affected components                                           | Required if component added/modified |
| Quality checklist | Completed against the template checklist                                                                | Required                             |

### 7.2 Review Requirements

**Approval setup:**

- Minimum **2 approvals** (excluding PR author) required for merges into `release/current`.
- At least **1 reviewer must be a core maintainer** (Senior front-end architect or equivalent) to ensure library stability.
- Reviewers must inspect for gaps in accessibility, design tokens, and component adherence.
- All comments must be resolved before merge.

**Reviewer focus areas:**

| Priority        | Review Area          | Key Question                                                                                    |
| --------------- | -------------------- | ----------------------------------------------------------------------------------------------- |
| High (CRITICAL) | CI/CD Integrity      | Did all checks (tests, linter, build) pass without errors?                                      |
| High (CRITICAL) | Testing & Regression | Were unit/integration tests added? Does the PR break existing tests on other components?        |
| High (CRITICAL) | Public API / SemVer  | If a public prop or method changed or was removed, is it flagged as a `BREAKING CHANGE`?        |
| Medium          | Component Adherence  | Are existing DS components and design tokens reused? Does code follow the design specification? |
| Medium          | Performance / DOM    | Is the HTML/DOM markup semantic and efficient? Risk of excessive re-renders?                    |
| Low             | Documentation        | Is the PR template complete? Is Storybook/Confluence updated if applicable?                     |
| Low             | Style and Naming     | Does code follow naming and style standards?                                                    |

### 7.3 Approval Criteria

A PR is only eligible for merge once all of the following are satisfied:

**Technical:**

1. All CI checks pass: linting, unit and integration tests, quality gates, and build.
2. No console errors or warnings during QA review (locally in Storybook or in an app).
3. Code abides by linting and formatting rules.

**Code quality:**

1. All new or modified components include unit/integration tests.
2. Bug fixes include a test that reproduces and validates the fix.

**Documentation and conventions:**

1. PR template is fully completed per §7.1.
2. Storybook and user documentation are updated where applicable.
3. All review requirements (§7.2) are met.

---

## 8. AUTOMATION & CI/CD

Automation reduces manual errors and accelerates development velocity. This section covers pre-commit hooks and continuous integration pipelines that enforce quality gates.

### 8.1 Pre-commit Hooks

Three tools work together to run quality checks before a commit reaches the repository:

| Tool        | Function                                               | Git Hook                   |
| ----------- | ------------------------------------------------------ | -------------------------- |
| Husky       | Git hook manager                                       | `pre-commit`, `commit-msg` |
| lint-staged | Runs tasks only on staged files                        | `pre-commit`               |
| commitlint  | Validates commit messages against Conventional Commits | `commit-msg`               |

**Automated flow:**

1. `pre-commit` — Husky runs lint-staged; only staged files pass through Prettier and ESLint.
2. `commit-msg` — Husky runs commitlint to verify the message follows Conventional Commits.
3. If both hooks pass, the commit completes. If either fails, the commit is aborted.

**Setup:**

Husky and lint-staged are already configured at the workspace root. No per-package setup is needed.

**Workspace root `.husky/pre-commit`:**

```bash
pnpm lint-staged
```

**Workspace root `.husky/commit-msg`:**

```bash
pnpm commitlint --edit "$1"
```

**Workspace root `.lintstagedrc.js`:**

```javascript
export default {
  "packages/boreal-web-components/src/**/*.{ts,tsx}": [
    () => "pnpm --filter @telesign/boreal-web-components run lint:fix",
    () => "pnpm --filter @telesign/boreal-web-components run format",
  ],
  "packages/boreal-web-components/src/**/*.{css,scss}": [
    () => "pnpm --filter @telesign/boreal-web-components run format",
  ],
  "apps/boreal-docs/**/*.{ts,tsx}": [
    () => "pnpm --filter @telesign/boreal-docs run lint:fix",
    () => "pnpm --filter @telesign/boreal-docs run format",
  ],
  "apps/boreal-docs/**/*.{js,json,css,md,mdx}": [
    () => "pnpm --filter @telesign/boreal-docs run format",
  ],
};
```

> **Note:** Functions (not plain strings) are used as lint-staged task values to prevent lint-staged from appending matched file paths to `pnpm --filter` commands, which would produce invalid CLI syntax.

### 8.2 CI Pipeline & Automated Releases

The CI pipeline is the final mandatory quality gate after local pre-commit validations. It executes the full test suite, coverage checks, and security scans on every pull request into permanent branches.

The CD workflow automates delivery of validated artifacts to development and production stages. Boreal DS manages deployment of separate packages rather than a centralized monorepo approach.

For the full CI/CD pipeline specification, refer to the [CI/CD Pipeline Strategy](https://telesign.atlassian.net/wiki/spaces/SENG/pages/1303773297) Confluence page.

---

## 9. APPENDICES

### B. Troubleshooting Common Issues

#### B.1 pnpm virtual store resolves stale package after workspace source changes

**Symptom:** After modifying `boreal-web-components` source or `package.json`, builds in `boreal-react` or `boreal-vue` continue to fail as if the changes were not applied. TypeScript errors reference a module shape that should no longer exist.

**Cause:** pnpm's virtual store may have `boreal-react/node_modules/@telesign/boreal-web-components` resolved from a cached `.tgz` snapshot rather than the live workspace symlink. This can happen after branch switches, cherry-picks, or install failures.

**Fix:**

```bash
# From the workspace root
pnpm install
```

This reconciles all workspace symlinks and flushes stale virtual store entries. A full `pnpm install` is fast when the lockfile has not changed; it does not re-download packages.

---

#### B.2 Wrapper package build fails: `Cannot find module '@telesign/boreal-web-components/components/bds-X.js'`

**Symptom:** TypeScript emits `Cannot find module` errors for component subpath imports when building `boreal-react` or `boreal-vue`.

**Cause:** The `exports` map in `boreal-web-components/package.json` is missing the `types` condition on the `./components/*.js` entry. Without it, `moduleResolution: bundler` cannot locate the `.d.ts` file for the subpath.

**Expected shape:**

```json
"./components/*.js": {
  "import": "./components-build/*.js",
  "types": "./components-build/*.d.ts"
}
```

**See also:** [ADR 0005](./../decisions/0005-exports-map-types-condition-component-subpaths.md)

---

#### B.3 Stencil `components.d.ts` fails to compile: `Cannot find name 'IFoo'` or `BdsFooCustomEvent` not found

**Symptom:** After Stencil builds `components.d.ts`, TypeScript compilation of `boreal-react` or `boreal-vue` fails with errors about an interface (`IButton`, `IFoo`, etc.) or event type (`BdsFooCustomEvent`) being undefined.

**Cause:** The interface file in the component's `types/` subdirectory uses `export default interface` instead of `export interface`. Stencil's declaration generator only tracks named exports when building the global `Components` namespace in `components.d.ts`. With a default export, the interface is referenced but not imported, breaking the entire component's namespace and all derived types.

**Fix:** Convert to a named export throughout:

```ts
// types/IFoo.ts — WRONG
export default interface IFoo { ... }

// types/IFoo.ts — CORRECT
export interface IFoo { ... }
```

Update the import in the component file:

```ts
// bds-foo.tsx — WRONG
import IFoo from "./types/IFoo";

// bds-foo.tsx — CORRECT
import { IFoo } from "./types/IFoo";
```

**See also:** [ADR 0006](./../decisions/0006-stencil-interface-files-named-exports-only.md)
