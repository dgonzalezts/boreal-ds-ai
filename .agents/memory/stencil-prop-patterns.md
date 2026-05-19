# Stencil — `@Prop()` Declaration Patterns and TypeScript Narrowing

## ESLint Rules Are Errors, Not Warnings

`stencil/props-must-be-readonly: 'error'` and `stencil/required-jsdoc: 'error'` are both active in `eslint.config.ts`. Every `@Prop()` declaration in the codebase must satisfy both rules or the build fails.

Required for every `@Prop()`:

1. The TypeScript `readonly` keyword on the property declaration.
2. A JSDoc block comment (`/** */`) immediately above the decorator.

This applies to props declared inside mixin factories as well as on component class bodies.

## `mutable: true` on `disabled` Produces a Stencil Compiler Warning — Use `@State()` Mirror Instead

Stencil emits `@Prop() "disabled" should not be mutable` when `mutable: true` is applied to `disabled`. The warning exists because `disabled` is a native reflected HTML attribute with browser-managed semantics (controlled externally via `formDisabledCallback`). Marking it `mutable: true` creates two writers on the same reflected attribute — the component and the browser — which can race.

The correct pattern for any prop whose value is also written by a browser lifecycle callback (e.g. `formDisabledCallback`) is a `@State()` mirror:

```typescript
/** Whether the component is disabled. Reflects the disabled attribute. */
@Prop({ reflect: true }) readonly disabled: boolean = false;
@State() private isDisabled: boolean = false;

@Watch('disabled')
onDisabledChange(next: boolean): void {
  this.isDisabled = next;
}

componentWillLoad(): void {
  this.isDisabled = this.disabled;
}

formDisabledCallback(disabled: boolean): void {
  this.isDisabled = disabled;
}
```

Render and toggle logic reads `this.isDisabled`. `@Prop()` remains `readonly` and externally owned. `@State()` is the internal working copy — it can be written by both `@Watch` and `formDisabledCallback` without a cast or compiler warning.

`readonly` and `mutable: true` are orthogonal: `readonly` prevents external consumers from setting the prop after initialization; `mutable: true` allows the component to write the prop internally. For `disabled` specifically, the `@State()` mirror approach is preferred over `mutable: true` because it avoids the warning and removes the risk of racing with the browser's FACE lifecycle.

For non-FACE props that the component needs to write internally (e.g. `value` tracking internal selection state), use `@Prop({ mutable: true })` without a cast:

```typescript
/** Currently selected value. Updated internally when selection changes. */
@Prop({ mutable: true }) value = '';
```

The `stencil/strict-mutable` ESLint rule is set to `'warn'` — every `mutable: true` will flag a warning on every build. This is intentional and accepted for props that need internal mutation.

## Never Use Constant References as `@Prop()` Default Values

Stencil's compiler resolves `@Prop()` defaults at **static analysis time** (AST level), not at runtime. When you write:

```typescript
@Prop() readonly orientation: Orientation = ORIENTATIONS.VERTICAL;
```

The compiler sees the identifier `ORIENTATIONS.VERTICAL` — it does not follow the import and resolve it to `'vertical'`. This leaks into two places:

1. **Custom Elements Manifest** — `custom-elements.json` records `ORIENTATIONS.VERTICAL` as the default value, which is what Storybook's ArgTypes table and consumer IDEs display. They see an internal constant name rather than the actual string value.
2. **Component documentation** — same problem in any docs tooling that reads the manifest.

Always use the **string literal directly** as the default:

```typescript
// ✅ Correct — CEM records 'vertical'
@Prop() readonly orientation: Orientation = 'vertical';

// ❌ Wrong — CEM records 'ORIENTATIONS.VERTICAL'
@Prop() readonly orientation: Orientation = ORIENTATIONS.VERTICAL;
```

Constants may still be used in logic (e.g. `validatePropValue`, switch cases, class maps) — just never as the `@Prop()` initializer value.

When a prop has a default value, TypeScript infers its type — no explicit annotation is needed:

```typescript
@Prop({ reflect: true }) readonly disabled = false;         // inferred boolean
@Prop({ reflect: true }) readonly orientation = 'vertical'; // inferred string, narrowed by implements
```

Even when TypeScript would widen the inferred type (e.g. `'vertical'` → `string`), the `implements IComponent` clause catches mismatches at the class level. If the interface says `orientation: Orientation` (`'horizontal' | 'vertical'`) and the class infers `string`, TypeScript errors on the `implements` clause itself — not silently. No explicit annotation is needed on the prop.

When there is no default, the type cannot be inferred and must be declared explicitly:

```typescript
@Prop({ reflect: true }) readonly name!: string;   // required — no default
@Prop({ reflect: true }) readonly formId?: string; // optional — undefined is meaningful
```

**When to use a default value:**

- The prop has a sensible "off" state: `disabled = false`, `required = false`, `checked = false`.
- There is always a valid fallback and the prop is purely behavioral.

**When NOT to use a default value:**

- **Identity data** (`name`, `value` on a leaf element) — these are required (`!`). A default of `''` would silently submit broken form data.
- **Optional context** (`formId?`, `required?`) — `undefined` means "absent", which is semantically different from `false` or `''`. Defaulting them changes DOM attribute presence.

| Declaration        | Meaning                                                        |
| ------------------ | -------------------------------------------------------------- |
| `name!: string`    | Required, no default — component cannot function without it    |
| `formId?: string`  | Optional, no default — `undefined` is a valid meaningful value |
| `disabled = false` | Has default — behavioral, always a valid fallback              |

> For boolean props with `reflect: true` in Stencil, `false` and `undefined` produce identical DOM output (attribute omitted). The `required={false}` vs `required={undefined}` distinction that matters in plain HTML or React does not apply here — Stencil strips the attribute in both cases.

---

## Never Use Indexed Access Types on `@Prop()` Declarations

Do **not** write `@Prop() readonly foo: IFoo['foo'] = ''`. TypeScript's indexed access types (e.g. `IFoo['propName']`) appear to work at editor time but produce an `error`-typed result in the Stencil compiler context. This causes `@typescript-eslint/no-unsafe-assignment` errors on every read of that prop (event emitter calls, JSX attributes, class map values, etc.).

The root cause: the Stencil decorator transform evaluates prop types before the full type-checker is available. When the source interface transitively references `@stencil/core/internal` types (e.g. `EventEmitter`), the indexed access degrades to `error`. Even after removing those transitively problematic members, the cached analysis may not update reliably.

**Rule**: always use concrete primitives directly on `@Prop()` declarations:

```typescript
// ✅ Correct
@Prop() readonly value: string = '';
@Prop({ reflect: true }) readonly disabled: boolean = false;

// ❌ Wrong — degrades to error type in Stencil decorator context
@Prop() readonly value: IFoo['value'] = '';
@Prop({ reflect: true }) readonly disabled: IFoo['disabled'] = false;
```

The `implements IFoo` clause on the class still enforces the structural contract — that is the correct role for the interface. The interface is the contract; the prop declaration is the implementation.

## `instanceof Element` Over `nodeType` Checks

`node.nodeType === Node.ELEMENT_NODE` does NOT trigger TypeScript's control-flow narrowing. After the check the variable's type remains `ChildNode`, requiring an explicit cast `(node as Element)` to access element properties.

`node instanceof Element` triggers TypeScript's narrowing automatically. The type becomes `Element` inside the if-block with no cast required.

Applied in `src/utils/dom/elements.ts`:

```typescript
export function hasSlotContent(el: HTMLElement, slotName?: string): boolean {
  if (slotName !== undefined) {
    return el.querySelector(`[slot="${slotName}"]`) !== null;
  }
  return Array.from(el.childNodes).some((node) => {
    if (node instanceof Element) return node.slot === "";
    if (node.nodeType === Node.TEXT_NODE)
      return node.textContent?.trim() !== "";
    return false;
  });
}
```

Text nodes do not have an `instanceof` equivalent, so `nodeType === Node.TEXT_NODE` remains correct for those — but always prefer `instanceof` checks for element nodes.

## `reflect: true` — When to Use It and When Not To

### The rule

Add `reflect: true` **only** when the prop value is directly referenced by a CSS **attribute selector** in the component SCSS. In every other case, do not reflect.

```ts
// ✅ Reflect — SCSS has bds-grid-item[col-span='full'] { grid-column: 1 / -1 }
@Prop({ reflect: true }) readonly colSpan: IGridItem['colSpan'] = 12;

// ✅ Reflect — SCSS has bds-badge[variant='info'] { ... }
@Prop({ reflect: true }) readonly variant: BannerVariant = 'info';

// ❌ Do NOT reflect — SCSS uses .bds-grid--fixed class, not [layout='fixed']
@Prop() readonly layout: IGrid['layout'] = GRID_LAYOUT.FLUID;

// ❌ Do NOT reflect — applied as inline style via Host style binding
@Prop() readonly rowGap: IGrid['rowGap'];
```

### Why this matters

Stencil **always** observes every `@Prop()` as a DOM attribute (converting camelCase → kebab-case). This means:

- **HTML attribute → JS prop** works for free, without `reflect: true`.
- `reflect: true` only enables the reverse: **JS prop change → DOM attribute update**.

Without reflection, a programmatic change like `el.layout = 'fixed'` updates the Stencil prop and triggers a re-render, but `el.getAttribute('layout')` stays `null`. This is correct behaviour when the CSS strategy uses a class or inline style rather than an attribute selector.

### The `'full'` sentinel value pattern

When a prop has a `'full'` sentinel that triggers a `grid-column: 1 / -1` CSS rule, there are two valid approaches:

**Current pattern (reflect + CSS attribute selector):**

```scss
bds-grid-item[col-span="full"] {
  grid-column: 1 / -1;
}
```

```ts
@Prop({ reflect: true }) readonly colSpan: IGridItem['colSpan'] = 12;
```

**Alternative (pure JS — no reflection needed):**

```ts
private getHostStyles() {
  if (this.colSpan === 'full') return { 'grid-column': '1 / -1' };
  return { '--_col-base': String(this.colSpan) };
}
```

Trade-offs:

|                               | Reflect + CSS selector | Pure JS getter                   |
| ----------------------------- | ---------------------- | -------------------------------- |
| `reflect: true` required      | Yes                    | No                               |
| DOM attribute mirrors JS prop | Yes                    | No                               |
| `getHostStyles()` complexity  | Simpler                | More verbose (branches per prop) |
| CSS selector strategy         | Attribute              | None                             |

Both are valid. The reflect + CSS selector approach is the current convention in this codebase.

### Attribute direction is always free

```
HTML attribute  →  Stencil prop   ✅ free (always)
JS prop change  →  DOM attribute  ✅ only with reflect: true
```

`<bds-grid layout="fixed">` in HTML always works — no reflection required. The DOM fires `attributeChangedCallback` and Stencil maps it back to the prop.

---

## JSDoc and `custom-elements.json`

The project generates `custom-elements.json` via the `docs-custom-elements-manifest` output target in `stencil.config.ts`. JSDoc descriptions on `@Prop()` declarations feed directly into the manifest's `description` fields for each member. Missing JSDoc means missing manifest descriptions, which affects any tooling (e.g. IDEs, Storybook argTypes auto-generation) that consumes the manifest.

## `@internal` on a Component Class JSDoc Silently Excludes the Component from the CEM

The Custom Elements Manifest (CEM) analyzer honours the `@internal` JSDoc tag as a signal to exclude that symbol from the public API. If `@internal` appears anywhere in the **class-level JSDoc block** of a Stencil component, the entire component is omitted from `custom-elements.json`.

Reference: https://custom-elements-manifest.open-wc.org/analyzer/getting-started/#supported-jsdoc

Consequences:

- The component is absent from the manifest, so the Stencil React/Vue output target never generates a wrapper for it.
- No build error is thrown — the component simply disappears silently from generated wrappers and Storybook argTypes.

Confirmed on `bds-banner`: adding `@internal` to the class JSDoc caused `BdsBanner` to vanish from `boreal-react`'s generated `components.ts`. Removing the tag restored it.

**Rule:** Never use `@internal` in a Stencil component's class-level JSDoc. If a component should be excluded from consumers, remove it from `package.json` `exports` instead.

## Non-Standard JSDoc Tags on Class Bodies Are Silently Ignored by the CEM Analyzer

Tags such as `@element` and `@method` are not part of the CEM spec. When written in a class-level JSDoc block the analyzer reads and discards them without error or warning. The data they attempt to describe is already captured from decorators:

- `@element bds-banner` is redundant — the analyzer reads the tag name from `@Component({ tag: '...' })`.
- `@method closeBanner` is redundant — the analyzer reads public methods from the `@Method()` decorator on the method declaration itself.

Writing these tags creates a false sense of documentation completeness while producing no actual output in `custom-elements.json`.

**Rule:** Do not write `@element` or `@method` in class-level JSDoc blocks. Trust the decorators. If a method needs a description, put the JSDoc block directly on the method, not on the class.

### `@file` vs `@fileoverview`

`@fileoverview` is not a standard JSDoc tag — `@file` is the correct equivalent. The `jsdoc/check-tag-names` ESLint rule (`eslint-plugin-jsdoc@62.7.1`, installed in `boreal-web-components`) will flag `@fileoverview` as an unknown tag. Use `@file` in all module-level JSDoc blocks (e.g. `src/index.ts`).
