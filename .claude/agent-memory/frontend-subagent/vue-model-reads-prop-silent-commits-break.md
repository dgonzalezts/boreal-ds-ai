# Vue `v-model` reads the element property, so every silent prop commit breaks it (EOA-19597 T43)

`@stencil/vue-output-target`'s v-model directive resolves `update:modelValue` from `targetAttr` by
default (`resolvePath(e, 'target.value')`), i.e. the **element property**, not `e.detail`; an
`eventAttr` on the `componentModels` entry (for example `'detail'`) points it at the event instead, and
the entries discussed here do not set one. React wrappers are unaffected because `onValueChange` reads
`event.detail`. Team version of this note: `.agents/memory/vue-vmodel-reads-property-not-event-detail.md`.

Consequence: any component listed in `targets/vue-output-target.ts` → `componentModels` that assigns
its model prop *without* emitting `valueChange` leaves the consumer's bound ref stale (empty, or one
commit behind). `bds-search-bar`'s debounced commit (`applyQuery`) did exactly that: keystrokes emitted
`valueChange` with the typed text while `this.value` stayed at the old committed value (so the ref got
the stale property), and the blur/Tab commit assigned `value` with no emission at all.

Fix shape (T43 option A): assign + emit together, guarded by equality so a no-op commit stays silent.

```ts
if (this.value !== value) {
  this.value = value;
  this.valueChange.emit(value);
}
```

Audit rule: grep every `this.<modelProp> = ` in a `componentModels` component — each assignment needs a
matching `valueChange.emit`, and the event's JSDoc must describe both the interim (per-keystroke) and
committed emissions.

Double-emit check for search-bar specifically: `commitTypedQuery` early-returns unless a debounce is
still pending (`debounceTimer !== null`), and it cancels the timer before `applyQuery`, so blur/Enter-close
after an already-fired debounce cannot emit twice. Picks (`handleSelectChange`) and clears
(`handleFieldClear`) run `cancelDebounce()` first, so a pending commit cannot land after them.

Known spec that encodes the old no-emit contract (left for @testing-subagent, not edited):
`src/components/forms/bds-search-bar/__test__/bds-search-bar.events.spec.ts` →
"Should keep the field and the value aligned across repeated blur cycles" — its three
`expect(eventCounts()).toEqual(before…Blur)` assertions assume a blur commit adds zero events; it now
adds exactly one `valueChange` (the first two comparisons fail, the post-clear one still passes because
`typedText` is already `null` there).
