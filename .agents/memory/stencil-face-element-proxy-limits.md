# Stencil FACE — Element Proxy Blocks Native FACE Prototype Members

## Discovery

The browser's FACE spec (Form-Associated Custom Elements) adds `checkValidity()`, `reportValidity()`, and `validity` to the element's prototype. Stencil's element proxy only forwards members declared with `@Prop()`, `@State()`, or `@Method()`. Accessing `bdsTextField.checkValidity()` or `bdsTextField.internals` from outside the component returns `undefined`.

## Fix

Wrap FACE validation methods as `@Method()` on the component class:

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

## Testing Implication

All FACE validation checks from outside the component (test harnesses, unit tests, integration tests) must go through `@Method()` wrappers. Accessing `internals` directly from outside is also blocked by the proxy and will return `undefined`.

## Applies To

Every Boreal DS FACE component: `bds-text-field`, `bds-select`, `bds-checkbox`, `bds-radio`, `bds-textarea`, `bds-switch`, `bds-number-input`, `bds-range`.
