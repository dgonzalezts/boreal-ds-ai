# Test Spec File Organisation

## The Five Spec File Types

Unit tests for a Stencil component are split across up to five spec files, each covering one functional concern. The naming convention is `{bds-component}.{type}.spec.ts`.

| File                             | Create when…                                                                                                                                                                         |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `bds-component.a11y.spec.ts`     | The component renders ARIA attributes, roles, or manages focus. Always required for interactive components.                                                                          |
| `bds-component.basics.spec.ts`   | The component has props, CSS classes, or render output that can be verified in isolation. Always required.                                                                           |
| `bds-component.variants.spec.ts` | The component has a `variant`, `size`, `color`, `type`, or equivalent enum prop that changes rendered output. Create only when the permutations are not already covered by `basics`. |
| `bds-component.events.spec.ts`   | The component emits one or more custom events, or reacts to DOM events from child elements.                                                                                          |
| `bds-component.slots.spec.ts`    | The slot itself has testable observable behaviour beyond what other spec files already cover. See criteria below.                                                                    |

## When to Create `slots.spec.ts`

Create the file **only** when at least one of these is true:

1. The component has **named slots** and their presence or absence changes rendered output or component state.
2. A `slotchange` handler updates component state or the DOM in a way that can be independently asserted.
3. A slot renders **conditionally** based on props (e.g. shown only when a certain prop is set).

**Do not create** `slots.spec.ts` for a bare unnamed passthrough slot (`<slot />`) whose only side-effect is a CSS layout variable (e.g. `--layout-count`). That slot is already exercised incidentally by any test that passes child elements, and the CSS variable has no observable behaviour to assert.

## Structure Rules

- One `describe` block per spec file.
- One `it` per distinct behaviour — not per line of code.
- Test descriptions must read as specifications: `"renders as disabled when the disabled prop is true"` — not `"disabled test"`.
- Utility functions in `src/utils/` are tested separately with Vitest and must have their own `.spec.ts` files.
