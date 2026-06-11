---
name: stencil-component-knowledge
description: Domain knowledge for implementing Stencil web components in Boreal DS. Covers FACE (Form-Associated Custom Elements), component API conventions, props, events, slots, SCSS tokens, and light DOM patterns. Load proactively when implementing or reviewing Stencil components.
---

# Stencil Component Knowledge — Boreal DS

Primary references (read before implementing):

- `ai-docs/guidelines/stencil-best-practices.md` — canonical implementation patterns (mixin architecture, FACE, SCSS, `IFormControl<T>` interface layering, API conventions)
- `ai-docs/guidelines/stencil-best-practices.md` — ESLint rules, token usage, JSDoc requirements

---

## Prop Validation: `validatePropValue` + `componentWillLoad` + Stacked `@Watch`

`@Watch()` fires only on runtime prop changes — it does NOT fire for the initial attribute value. Without `componentWillLoad()`, invalid initial attributes are silently accepted.

**Required pattern:**

```ts
componentWillLoad() {
  this.checkPropValues();
}

@Watch('type')
@Watch('color')
@Watch('variant')
@Watch('size')
checkPropValues() {
  validatePropValue(Object.values(BUTTON_TYPES) as ButtonTypes[], BUTTON_TYPES.BUTTON, this.el as HTMLElement, 'type');
  validatePropValue(Object.values(CORE_COLORS) as CoreColors[], CORE_COLORS.DEFAULT, this.el as HTMLElement, 'color');
}
```

`validatePropValue` location: `packages/boreal-web-components/src/utils/props/validatePropValue.ts`
Import via: `import { validatePropValue } from '@/utils'`

When the value is invalid the utility logs a warning and **mutates** `element[propName]` to the fallback. After `checkPropValues()` returns all validated props hold a valid value.

---

## `@Event()` Convention — Bare Decorator Only

```ts
// ✅ Correct
@Event() bdsChange!: EventEmitter<string>;
@Event() valueChange!: EventEmitter<string>;

// ❌ Wrong — options are irrelevant in light DOM
@Event({ bubbles: true, composed: true }) bdsChange!: EventEmitter<string>;
```

Bare `@Event()` with no `bubbles`, `composed`, or `cancelable` is the enforced convention, consistent with BEEQ and Aqua DS reference implementations (88 and 80 bare `@Event()` respectively). `composed` is irrelevant because Boreal DS uses light DOM throughout. See ADR `ai-docs/decisions/0003-event-options-convention.md`.

`valueChange` is reserved for Vue `v-model` integration. All other events use the `bds{Action}` naming pattern.

---

## Group Component Labels — Use `<bds-typography>`

Group components (e.g. `bds-radio-group`, `bds-checkbox-group`) that own a `label` and `helperText` must render them via `<bds-typography>`, not plain `<span>` elements.

- `variant="label"` — provides required indicator (`*`) and tooltip icon out of the box
- `variant="helper"` — handles error/disabled state coloring via its `state` prop; no custom SCSS needed

```tsx
render() {
  const labelId = `${this._id}-label`;
  const helperId = `${this._id}-helper`;
  const typographyState = this.disabled ? 'disabled' : this.error ? 'error' : 'default';

  return (
    <Host
      aria-labelledby={this.label ? labelId : undefined}
      aria-describedby={this.helperText ? helperId : undefined}
    >
      {this.label && (
        <bds-typography
          id={labelId}
          variant="label"
          state={typographyState}
          required={this.required}
          tooltipText={this.info !== '' ? this.info : undefined}
        >
          {this.label}
        </bds-typography>
      )}
      {this.helperText && (
        <bds-typography id={helperId} variant="helper" state={typographyState}>
          {this.helperText}
        </bds-typography>
      )}
    </Host>
  );
}
```

Key details:

- `private readonly _id = createId('bds-radio-group')` — unique ID per instance
- Tooltip API prop is named `info` (matches `bds-text-field`); mapped with empty-string guard: `tooltipText={this.info !== '' ? this.info : undefined}`
- `state` is computed once and passed to both label and helper elements
- Individual leaf labels (`bds-radio`, `bds-checkbox`) stay as plain `<span>` — only group-level labels use `bds-typography`

---

## FACE Components

For the full FACE implementation guide (attach-internals placement, proxy limits, constraint validation, formDisabledCallback, async rendering gotchas) see `ai-docs/guidelines/stencil-best-practices.md` §"FACE Components".

**Form control interface layering** — see `ai-docs/guidelines/stencil-best-practices.md` §"IFormControl<T> Interface Layering":

```typescript
export class BdsTextField
  extends Mixin(formAssociatedMixin)
  implements ITextField, IFormControl<string>
{
  @AttachInternals() internals!: ElementInternals;
  @Event() valueChange!: EventEmitter<string>;
}
```

`componentModels` in `vue-output-target.ts` must land in the same PR as the finished component.

---

## Composite Component Event Boundary

See `ai-docs/guidelines/stencil-best-practices.md` §"Composite Light DOM Event Boundary" for the full pattern and `stopPropagation()` guard requirement.

---

## mouseleave: relatedTarget vs target

`mouseleave` does not bubble. When using `addElementListener` to observe `mouseleave` on a child element, `event.relatedTarget` is the element the pointer is moving **to**, while `event.target` is always the element the listener was attached to — not the actual element the pointer left. Do not use `event.target` to distinguish which child triggered the leave event; use `event.relatedTarget` to determine destination.

Source: `.agents/memory/mouseleave-relatedtarget-vs-target.md`

---

## TypeScript: `declare global` is Redundant in `.d.ts` Files

When a type (e.g. `PopoverAPI`) is declared inside a `.d.ts` file that is already included in `tsconfig.json`, it is automatically globally available without `declare global { ... }`. Adding `declare global {}` in a `.d.ts` file is redundant and adds noise.

Source: `.agents/memory/typescript-popover-api-declare-global-redundant.md`
