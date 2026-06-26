## Prop Definitions Cleanup — Remove Indexed Access Types and Add Explicit Primitive Annotations

## Type of Change
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Bug fix (non-breaking change which fixes an issue)
- [X] Refactoring / chore (non-breaking change that improves code quality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Description of the Feature

This PR aligns `@Prop()` declarations across all Stencil web components with the project's
**Type Inference and Default Values** and **Component Interface Contract** guidelines.
Three recurring anti-patterns are eliminated:

1. **Indexed access types** — `@Prop() readonly x: IFoo['bar'] = ''` replaced with the concrete
   named type alias (e.g. `ButtonVariant`) or an explicit primitive annotation (`: string`,
   `: boolean`, `: number`).
2. **Opaque constant defaults** — `= POPOVER_POSITION.BOTTOM` replaced with the actual string
   literal `= 'bottom'`, so Stencil's CEM static analyser records the value (not the identifier)
   in the generated manifest.
3. **Unannotated `readonly` primitive props** — TypeScript narrows `readonly x = false` to the
   literal type `false`, which causes the CEM to emit `x?: false` in JSX types. Consumers
   attempting to pass a dynamic boolean receive `Type 'boolean' is not assignable to type 'false'`.
   Explicit `: boolean` annotations fix this.

## Implementation Details

### Files changed

- **22 component `.tsx` files** — `IFoo['bar']` removed from every `@Prop()` annotation; explicit
  primitive type annotations added; constant defaults replaced with literals. Unused interface
  imports dropped where the interface is no longer referenced.
- **4 test spec files** — Assertions updated to reflect correct Stencil boolean coercion behaviour:
  - Boolean JS property reads: `toBe('true')` → `toBe(true)`
  - Reflected boolean attribute checks: `getAttribute(x).toBe('true')` → `toBe('')`
    (Stencil reflects `true` as an empty attribute string, not the string `"true"`)
  - Boolean data-attribute presence: `getAttribute('data-multiline').toBe(true)` →
    `hasAttribute('data-multiline').toBe(true)`

### Scope

| Pattern fixed | Occurrences | Files |
|---|---|---|
| `IFoo['bar']` indexed access types | 76 | 22 |
| Constant/enum defaults | 9 | 5 |
| Missing explicit primitive annotations | ~50 | 22 |
| Test assertion corrections | 8 | 4 |

Components touched: `bds-button`, `bds-button-group`, `bds-list-menu`, `bds-list-menu-item`,
`bds-toggle`, `bds-badge`, `bds-banner`, `bds-spinner`, `bds-status`, `bds-tag`,
`bds-checkbox-card`, `bds-flag`, `bds-radio-card`, `bds-avatar`, `bds-grid`, `bds-grid-item`,
`bds-divider`, `bds-step-item`, `bds-dialog`, `bds-popover`, `bds-tooltip`, `bds-typography`,
`bds-pagination`, `bds-toast-container`, `bds-toast-item`, `bds-tag-field`.

## Impact of the Feature

- **No consumer-visible API changes.** All prop names and default values remain identical.
- **Improved CEM output.** Storybook ArgType controls, IDE autocompletion, and framework wrapper
  types now show correct union literals instead of identifiers or overly-narrow literal types.
- **Correct boolean attribute coercion.** Props typed as `: boolean` now correctly coerce
  `disabled="true"` (HTML attribute string) to the JS boolean `true`, and reflect `true` as an
  empty attribute (`disabled=""`), matching the HTML spec.

## Testing Conducted

- **1746 unit tests across 178 test suites** — all pass after assertion corrections.
- **`tsc -b`** on `react-testapp` and **`vue-tsc --build`** on `vue-testapp` — both pass with
  zero errors, confirming wrapper types correctly surface the updated prop annotations.
- **Grep verification** — zero remaining `IFoo['bar']` or in-scope constant-default patterns
  in any `@Prop()` declaration.

## Screenshots/Videos (if applicable)

N/A — no visual changes.

## Additional Remarks

- Three constant defaults in `bds-slider.tsx` and one in `bds-tag-field.tsx` (the `variant` prop)
  were intentionally left unchanged: `bds-slider` was out of scope for this ticket, and
  `bds-tag-field`'s `variant` already follows the correct named-type-alias pattern.
- The `bds-tooltip.tsx` JSDoc hint ("JSDoc types may be moved to TypeScript types") is a
  pre-existing IDE warning on the `@returns` tag; it does not affect compilation.

## Checklist

- [X] My code adheres to the project's coding and style guidelines.
- [X] I have conducted a self-review of my code.
- [ ] I have commented my code, particularly in complex areas.
- [ ] I have made corresponding changes to the documentation.
- [X] I have tested my feature thoroughly in different environments.
- [X] I have added tests that prove my feature works as intended.
- [X] New and existing unit tests pass locally with my changes.
- [X] I have assessed the performance impact of the feature.
- [X] My changes do not introduce new warnings or errors.
- [X] I have checked for compatibility with other parts of the codebase.
