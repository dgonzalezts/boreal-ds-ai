# PR Title

feat(web-components): EOA-12334 add radio and radio-group form components

---

# PR Body

Implements `bds-radio` and `bds-radio-group` as form-associated custom elements with full keyboard navigation, ARIA support, and native form integration.

The radio group component orchestrates single-selection across child `bds-radio` elements using roving tabindex, arrow key navigation, and FACE (Form-Associated Custom Elements) lifecycle callbacks. Both components integrate with native forms via `ElementInternals`, supporting `FormData`, form reset, and state restoration.

Key implementation details:

- **Form integration**: Uses `formAssociatedMixin` with `@AttachInternals()` on the component class. The group component registers in `componentModels` for Vue `v-model` two-way binding support.
- **Keyboard navigation**: Arrow keys (Up/Down/Left/Right) navigate between enabled radios with automatic selection, following ARIA Authoring Practices Guide patterns.
- **Error state management**: Supports both controlled error state (via `error` prop) and native validation error state (via `invalid` event and `isInvalid` @State), propagating error styling to all child radios.
- **Accessibility**: Full ARIA implementation with `role="radiogroup"`, `aria-checked`, `aria-labelledby`, `aria-describedby`, `aria-invalid`, and `aria-required`. Roving tabindex ensures only one radio is in the tab sequence at a time.
- **Label infrastructure**: Uses `<bds-typography>` for group label and helper text, with `variant="label"` and `variant="helper"` plus dynamic `state` prop (default/error/disabled).

Test coverage includes five spec files per component covering accessibility, basics, variants, events, form integration, and keyboard interaction, exceeding the 90% statement coverage requirement.

Refs [EOA-12334](https://telesign.atlassian.net/browse/EOA-12334)
