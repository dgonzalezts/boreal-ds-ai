# Stencil FACE — Constraint Validation Pattern

## Problem: Doubled Validation Events

If both `ElementInternals.setValidity()` and a native `<input required>` attribute handle validation simultaneously, the browser fires two validation events. The inner `<input>` without the FACE focus handling causes an "invalid form control is not focusable" error on submit — the browser tries to focus the inner `<input>` rather than the custom element.

## Required Pattern

1. Remove `required={this.required}` from the native `<input>` inside the component.
2. Handle all constraint validation exclusively via `ElementInternals.setValidity()`.
3. Add `tabIndex={this.disabled ? -1 : 0}` on `<Host>` so the browser can focus the custom element when validation fails.
4. Add `onFocus={() => this.el.querySelector<HTMLInputElement>('input')?.focus()}` on `<Host>` to delegate focus to the inner input for UX.

## Summary

The custom element (`<Host>`) owns the validity state and is the browser's focus target for validation errors. The inner `<input>` is a presentational element only — it must not carry any native constraint attributes (`required`, `pattern`, `minlength`, `maxlength`).

## `formResetCallback` and `formStateRestoreCallback`

Both callbacks must call `updateValidity()` after restoring the value. Failing to do so leaves the validity state reflecting the pre-reset value.

## `IFormValidator` and `customValidators` Prop

Built-in validators live in the component class. Consumer-provided validators are accepted via a `customValidators: IFormValidator[]` prop, appended after built-ins at runtime. `@Watch('customValidators')` triggers `updateValidity()` when a new array is assigned.

`IFormValidator.key` maps to native `ValidityStateFlags` keys, enabling `:valid` / `:invalid` CSS pseudo-class interoperability.

```typescript
private get validators(): IFormValidator[] {
  return [
    {
      key: 'valueMissing',
      isValid: el => !(el as HTMLBdsTextFieldElement).required || (el as HTMLBdsTextFieldElement).value !== '',
      message: 'This field is required. Please fill it out.',
    },
    ...this.customValidators,
  ];
}
```
