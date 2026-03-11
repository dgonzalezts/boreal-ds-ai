# Stencil — Async Rendering and Reflected DOM State Gotchas

## Stencil Batches DOM Updates Asynchronously

Reading a reflected DOM attribute in the same synchronous frame as a `@Prop()` setter call returns the previous value.

```typescript
tf.disabled = true;
console.log(tf.querySelector('input').disabled);
```

The inner input's `disabled` is still `false` until the next render tick.

## Rules for Tests and Harnesses

- In unit tests: use `await page.waitForChanges()` before reading reflected DOM attributes.
- In manual harnesses: read prop values directly (not reflected DOM state) for immediate assertions.
- Never write test assertions that depend on synchronous DOM reflection of a prop that was just set.

## `formDisabledCallback` is Triggered by `<fieldset disabled>`, Not `form.disabled`

`HTMLFormElement` has no native `disabled` property. Setting `form.disabled = true` does nothing. `formDisabledCallback` is only triggered by a `<fieldset disabled>` ancestor being toggled.

For unit tests: set `component.disabled` directly. For integration tests: toggle a `<fieldset disabled>` ancestor.

## `HTMLButtonElement.prototype.checkValidity` Naming Collision

A globally-defined function named `checkValidity` in the page's `<script>` is shadowed by `HTMLButtonElement.prototype.checkValidity` when called from an HTML `onclick` attribute. The button's native method takes precedence in the scope chain.

Rename global test harness functions to avoid collision with native HTML element method names (e.g., use `testValidity` instead of `checkValidity`).
