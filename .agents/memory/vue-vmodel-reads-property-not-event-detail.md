---
name: vue-vmodel-reads-property-not-event-detail
description: "By default the Vue output target's v-model reads the element property named by targetAttr; eventAttr makes it read a path on the event instead (for example detail). A componentModels component that assigns its model prop without emitting the paired event breaks v-model silently, and a state held outside the mapped property needs eventAttr."
---

# Vue `v-model` reads the element property by default — every silent model commit breaks it

`@stencil/vue-output-target`'s v-model directive emits `update:modelValue` with `resolvePath(e, modelUpdateEventAttribute ?? 'target.<targetAttr>')`. By default that is the **element property** named by `targetAttr` (for example `target.value`), not `event.detail`. The optional `eventAttr` of a `componentModels` entry replaces that path with a dot path on the event, so `eventAttr: 'detail'` reads the payload of the model event (checked in the runtime of 0.14.7). React wrappers read `event.detail` in their `onValueChange` and are unaffected by either mapping.

Consequence of the default path: any component listed in `packages/boreal-web-components/targets/vue-output-target.ts` → `componentModels` that assigns its model prop without emitting the paired event leaves the consumer's bound ref stale — empty, or one commit behind. The ref only catches up on the next event that happens to carry the right value, so a harness that tests only mouse picks and the clear button hides the bug.

Current mapping (2026-11): 12 components on `valueChange`/`value` (`bds-text-field`, `-radio-group`, `-checkbox-group`, `-select`, `-slider`, `-tag-field`, `-search-bar`, `-dropdown`, `-number-field`, `-progress-bar`, `-date-picker`, `-color-picker`), `bds-toggle` (`checked`, with `eventAttr: 'detail'`), `bds-file-picker` (`files`), `bds-checkbox`/`-card`/`-button` (`checked`) and `bds-table` (`selectedRows`, event `selectedRowsChange`). That is the 18 wrappers that expose `modelValue`.

**Fix shape** — assign and emit together, guarded so a no-op stays silent:

```ts
if (this.value !== value) {
  this.value = value;
  this.valueChange.emit(value);
}
```

**A state held outside the mapped property — the toggle case.** `bds-toggle` was mapped to `value`, but its on or off state is `checked` (which does not update on a click) and `value` is the string submitted with the form data when checked (default `"on"`, like a native checkbox). The wrapper therefore wrote the model into `value` and read it back from `value`: the bound ref became a string, a bound `true` never checked the toggle, a checked toggle would have submitted the model string, and the generated model type was `string`. The fix is `targetAttr: 'checked'` with `eventAttr: 'detail'` (EOA-20193 T7b, commit `3554eda5`), verified in a real browser before and after.

**Audit rules for any `componentModels` component:**
- grep `this.<modelProp> =`. Each assignment needs a matching `…Change.emit`, and the event's JSDoc must describe both the interim (per-keystroke) and committed emissions. `bds-search-bar`'s debounced commit assigned `value` silently while keystrokes emitted a value the property did not hold, so the ref received the stale property on every keystroke and nothing corrected it at blur (EOA-19597 T43).
- compare each entry's `targetAttr` with the payload type of its model event in `custom-elements.json`; when the payload is a boolean or other state that the mapped property does not track, the entry needs `eventAttr`. The toggle was the only mismatch among the 17 `valueChange` components.

**The invariant test** `examples/vue-testapp/src/__tests__/component-models.spec.ts` (run by `pnpm test`) fails naming a component that declares `valueChange` but has no `modelValue` wrapper, and a wrapper with a model whose component declares no model event. It checks that a component is listed, not that the right property is mapped, so a component whose state is not in `value` also needs a case in `v-model.spec.ts`. The contributor checklist is in the "Framework Wrappers" section of `packages/boreal-web-components/README.md`.

**Verifying:** compare event counts between React and Vue only after confirming the served bundle contains the fix — an identical count can also mean both ran pre-fix code (`turbo-cache-watcher-poisoned-dist.md`).

Regeneration mechanics: `vue-componentmodels-regeneration.md`.

**Source:** EOA-19597 T18 (found) and T43 (fixed, option A); toggle mapping: EOA-20193 T7b.
