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

If `mutable: true` is genuinely needed on a non-FACE prop (a prop only the component itself writes), use a narrow cast rather than `as any`:

```typescript
(this as { someInternalProp: string }).someInternalProp = nextValue;
```

In `custom-elements.json`, `mutable: true` causes Stencil to omit `"readonly": true` from the manifest entry. This is correct and intentional — it signals to consumers that the prop may change at runtime.

## `instanceof Element` Over `nodeType` Checks

`node.nodeType === Node.ELEMENT_NODE` does NOT trigger TypeScript's control-flow narrowing. After the check the variable's type remains `ChildNode`, requiring an explicit cast `(node as Element)` to access element properties.

`node instanceof Element` triggers TypeScript's narrowing automatically. The type becomes `Element` inside the if-block with no cast required.

Applied in `src/utils/dom/elements.ts`:

```typescript
export function hasSlotContent(el: HTMLElement, slotName?: string): boolean {
  if (slotName !== undefined) {
    return el.querySelector(`[slot="${slotName}"]`) !== null;
  }
  return Array.from(el.childNodes).some(node => {
    if (node instanceof Element) return node.slot === '';
    if (node.nodeType === Node.TEXT_NODE) return node.textContent?.trim() !== '';
    return false;
  });
}
```

Text nodes do not have an `instanceof` equivalent, so `nodeType === Node.TEXT_NODE` remains correct for those — but always prefer `instanceof` checks for element nodes.

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
