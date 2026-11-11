# Stencil: a direct DOM write makes the next render a no-op for that property

**Verified against:** `@stencil/core@4.42.1`, `internal/client/index.js` (`setAccessor`, ~line 2349).

## The fact

For a **native** element (`tagName` without a `-`), Stencil's `setAccessor` compares the **live DOM
property**, not just the previous vdom value, before writing:

```js
if (!elm.tagName.includes('-')) {
  const n = newValue == null ? '' : newValue;
  if (memberName === 'list') { /* attribute */ }
  else if (oldValue == null || elm[memberName] !== n) {
    if (typeof elm.__lookupSetter__(memberName) === 'function') elm[memberName] = n;
    else elm.setAttribute(memberName, n);
  }
}
```

`oldValue === newValue` (previous vdom) still short-circuits first, but when the vdom value *did*
change and the component already wrote the same string to the DOM synchronously, the patch is
skipped entirely — no `input.value = …`, no attribute write.

## Why it matters

Assigning `input.value` (even the same string) resets the caret and clears any selection in Chrome
and Safari. A handler that writes text + `select()` synchronously and *then* lets Stencil render
therefore keeps the selection — the render does not stomp it. This is the mechanism that makes a
synchronous "write the label, focus, `setSelectionRange(0, len)`" in a pick handler survive the
following render.

Caveats:

- Only for native elements. Custom elements (`bds-*`) use `elm[memberName] = newValue` guarded by the
  property value, which is a different path.
- `oldValue == null` (first render of that property) bypasses the property comparison and writes
  unconditionally.
- In `mock-doc`, `patchPropAttributes` backs `input.value` with the attribute, so unit tests observe
  the same "already written" state; `setSelectionRange` is absent there and must be feature-checked
  (see `bds-search-bar/helpers/selectInputText.ts`).

## Where it was used

`bds-search-bar`'s `applyPickedFieldText()` (EOA-19597 T51) — writes the picked label into the input
and selects it inside the `bds-select` `bdsChange` handler so a keystroke in that same frame replaces
the label instead of being lost.
