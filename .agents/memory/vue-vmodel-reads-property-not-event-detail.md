---
name: vue-vmodel-reads-property-not-event-detail
description: "The Vue output target's v-model resolves targetAttr from the element property, never event.detail, so any componentModels component that assigns its model prop without emitting the paired event breaks v-model silently."
---

# Vue `v-model` reads the element property — every silent model commit breaks it

`@stencil/vue-output-target`'s v-model directive emits `update:modelValue` with `resolvePath(e, 'target.value')`, i.e. the **element property**, never `event.detail`. React wrappers are unaffected: their `onValueChange` reads `event.detail`.

Consequence: any component listed in `packages/boreal-web-components/targets/vue-output-target.ts` → `componentModels` that assigns its model prop without emitting the paired event leaves the consumer's bound ref stale — empty, or one commit behind. The ref only catches up on the next event that happens to carry the right value, so a harness that tests only mouse picks and the clear button hides the bug.

Current mapping (2026-10): 13 components on `valueChange`/`value`, plus `bds-file-picker` (`files`), `bds-checkbox`/`-card`/`-button` (`checked`), and `bds-table` (`selectedRows`).

**Fix shape** — assign and emit together, guarded so a no-op stays silent:

```ts
if (this.value !== value) {
  this.value = value;
  this.valueChange.emit(value);
}
```

**Audit rule for any `componentModels` component:** grep `this.<modelProp> =`. Each assignment needs a matching `…Change.emit`, and the event's JSDoc must describe both the interim (per-keystroke) and committed emissions. `bds-search-bar`'s debounced commit assigned `value` silently while keystrokes emitted a value the property did not hold, so the ref received the stale property on every keystroke and nothing corrected it at blur (EOA-19597 T43).

**Verifying:** compare event counts between React and Vue only after confirming the served bundle contains the fix — an identical count can also mean both ran pre-fix code (`turbo-cache-watcher-poisoned-dist.md`).

Regeneration mechanics: `vue-componentmodels-regeneration.md`.

**Source:** EOA-19597 T18 (found) and T43 (fixed, option A).
