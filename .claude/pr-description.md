# PR Title

feat(web-components): EOA-13695 add bds-tag-field component

---

# PR Body

Adds `bds-tag-field`, a form-associated web component that lets users enter and manage multiple discrete string values as removable chips, with built-in validation, keyboard accessibility, and full framework integration.

The component is a FACE (Form-Associated Custom Element) built on `formAssociatedMixin`. It serialises its `string[]` value as JSON for native form submission, supports constraint validation (`required`, `maxTags`), and exposes `checkValidity()` / `reportValidity()` methods. Tag entry is confirmed via Enter or comma; the last tag can be removed with Backspace when the input is empty. An overflow chip (`+N`) collapses tags beyond `maxVisibleTags`. The `clearable` prop shows a clear-all button when tags are present.

This PR also introduces shared form-field infrastructure reused across all field components in this category: `useFormField` (validation lifecycle utility), shared render helpers (`renderFieldLabel`, `renderFieldFooter`, `renderFieldSublabel`, `renderFieldActions`), a shared SCSS partial (`_field-shell.scss`), and the `KeyboardController` utility — a fluent, type-safe API for registering key bindings on any element. `bds-tag-field` is registered in `vue-output-target.ts` `componentModels` to support Vue `v-model` two-way binding.

The `KeyboardController` replaces ad-hoc `@Listen` / `addEventListener` patterns for key handling in this and future components. It manages its own listener lifecycle and is unit-tested independently.

Reviewers should pay close attention to the `handleFocusOut` / `handleFocus` pair: focus management in a composite control (container + multiple chip buttons + input) requires a `requestAnimationFrame` guard to distinguish intra-component focus moves from genuine blur events. The `effectiveMaxVisible` logic also has a deliberate precedence — `maxVisibleTags` > `maxTags - 1` > full list — which differs from what a literal reading of the prop docs might suggest.

Refs EOA-13695
