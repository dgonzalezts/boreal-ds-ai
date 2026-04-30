# Stencil — Async Rendering and Reflected DOM State Gotchas

## Stencil Batches DOM Updates Asynchronously

Reading a reflected DOM attribute in the same synchronous frame as a `@Prop()` setter call returns the previous value.

```typescript
tf.disabled = true;
console.log(tf.querySelector("input").disabled);
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

## Testing Events That Fire in `componentDidLoad`

`componentDidLoad` runs synchronously inside `newSpecPage()` before the call resolves. Any listener attached **after** `await newSpecPage(...)` will miss events fired during that lifecycle hook.

### Wrong — listener is attached too late

```typescript
const page = await newSpecPage({
  components: [BdsRadio],
  html: `<bds-radio label="A"></bds-radio>`,
});
// componentDidLoad already ran — bdsMount was already fired
const spy = jest.fn();
document.addEventListener("bdsMount", spy);
expect(spy).toHaveBeenCalledTimes(1); // ❌ 0 calls
```

### Correct — use `page.setContent()` after attaching the listener

```typescript
// 1. Create an empty page (no html → no componentDidLoad yet)
const page = await newSpecPage({ components: [BdsRadio], html: "" });

// 2. Attach the listener on the mocked document before mounting
const spy = jest.fn();
page.doc.addEventListener("bdsMount", spy);

// 3. Inject HTML — triggers componentDidLoad while listener is active
await page.setContent(`<bds-radio label="A"></bds-radio>`);

expect(spy).toHaveBeenCalledTimes(1); // ✅
```

`page.setContent(html)` is Stencil's official spec-page API: it sets `document.body.innerHTML` and calls `waitForChanges()` internally (official docs: stenciljs.com/docs/unit-testing).

This pattern applies to **any event emitted from `componentDidLoad`** (e.g. `bdsMount`, registration events, analytics pings). Always use `page.doc` as the listener target, not `document`, to stay within the mocked environment.
