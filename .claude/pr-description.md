# PR Title

refactor(web-components): EOA-14257 migrate bds-text-field to shared form-field infrastructure

---

# PR Body

Refactor `bds-text-field` to consume the shared form-field render helpers, SCSS mixins, and the `useFormField` lifecycle helper, reducing the component's bespoke surface and aligning it with the rest of the form stack.

The component previously held its own copies of label, sublabel, footer, and counter rendering logic. These are now delegated to `renderFieldLabel`, `renderFieldSublabel`, `renderFieldFooter`, and `deriveFieldRenderState` from `@/components/forms/common`. The SCSS has been trimmed accordingly by pulling shared interaction and layout patterns from `_interactions.scss` — component-specific rules only remain. The `ITextField` interface and `enum.ts` types were thinned to remove entries already covered by the shared `IFormFieldProps` contract.

A `suffix` slot was added to the input container at the same time. The slot sits between the `<input>` and the built-in actions area, allowing composite parents (e.g. `bds-select`) to inject inline content such as a loading spinner or badge without a prop-driven API.

The `bds-spinner` animation was extracted as a reusable mixin in `_interactions.scss` and consumed by `bds-button`, removing the duplicated keyframe declaration from `bds-button.scss`.

No public API removals. The `readOnly` and `counterClass` parameters added to the render helpers are additive and backward-compatible. Existing `bds-select` tests were updated to reflect the new markup structure; no behavioral changes were made to `bds-select`.

Refs EOA-14257
