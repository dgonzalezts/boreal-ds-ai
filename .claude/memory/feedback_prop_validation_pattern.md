# Stencil — Prop Validation Pattern: `validatePropValue` + `componentWillLoad` + Stacked `@Watch`

## The Problem with `@Watch()` Alone

`@Watch()` fires only on runtime prop changes that occur after the component mounts. It does NOT fire for the initial prop value set via an HTML attribute (e.g. `<bds-button color="invalid-value">`). Without a `componentWillLoad()` call, invalid initial attribute values are silently accepted and rendered without correction.

## Required Pattern

Combine three things:

1. A shared `validatePropValue` utility that mutates the element property back to the fallback when the value is invalid.
2. Multiple `@Watch()` decorators stacked on a single `checkPropValues()` method.
3. A `componentWillLoad()` call to `checkPropValues()` to cover the initial render.

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
  validatePropValue(Object.values(BUTTON_VARIANTS) as ButtonVariant[], BUTTON_VARIANTS.DEFAULT, this.el as HTMLElement, 'variant');
  validatePropValue(Object.values(BUTTON_SIZES) as ButtonSizes[], BUTTON_SIZES.MEDIUM, this.el as HTMLElement, 'size');
}
```

## `validatePropValue` Utility

**Location:** `packages/boreal-web-components/src/utils/props/validatePropValue.ts`

**Exported from:**
- `packages/boreal-web-components/src/utils/props/index.ts`
- `packages/boreal-web-components/src/utils/index.ts` (re-exported)

**Behaviour:** When the current prop value is not in the valid set, the utility:
1. Logs a console warning naming the invalid value, the valid values, and the fallback being applied.
2. Mutates `element[propName]` directly to the fallback value so that `this.color` (etc.) reflects the actual applied value — not the invalid input.

This is a mutation strategy, not a warning-only strategy. After `checkPropValues()` returns, all validated props are guaranteed to hold a valid value.

## Source and Alignment

This pattern was adapted directly from the BEEQ reference implementation (`.ai/lib/endava-beeq.txt`), which also uses Stencil. It replaces the previous Boreal DS approach of individual per-prop `@Watch()` methods.
