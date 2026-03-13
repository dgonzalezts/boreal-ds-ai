# Stencil Light DOM — `:host` vs Root Class Selector

## The Rule

| Component type | Use | Reason |
|---|---|---|
| Form controls and interactive components | `:host` | They have browser-managed states reflected as attributes or pseudo-classes on the element itself |
| Layout and feedback components (banner, card, modal) | Root class on inner `<div>` | No attribute-driven or pseudo-class-driven states at the element level |

## When to Use `:host`

Use `:host` as the root CSS selector when any of the following apply to the component:

- `[disabled]` is reflected as a prop and used as a CSS attribute selector
- `:hover`, `:focus-visible`, `:active`, or `:checked` must cascade from the host element outward to inner elements
- The host element itself needs state-dependent styling driven by a reflected attribute

All Boreal DS form controls (checkbox, text field, select, radio) must use `:host`. This is non-negotiable because:

- `[disabled]` is reflected and browser-managed via FACE semantics; you cannot write `div[disabled]` selectors — the attribute lives on the custom element host.
- `:focus-visible` and `:hover` must cascade outward from the element. A selector like `.bds-checkbox:focus-visible .bds-checkbox__box` is impossible without `:host` because there is no wrapping class on the custom element itself.

## When to Use a Root Class

Use a BEM root class (e.g. `.bds-banner`) on an inner wrapping `<div>` when the component has no attribute-driven or pseudo-class-driven states at the element level. `bds-banner` is the canonical example: it has no `[disabled]`, no `:focus-visible`, no `:hover` on the host — all state comes from a `variant` prop passed as a class modifier.

## Stencil Light DOM Compilation

In Stencil light DOM (no shadow DOM), `:host` compiles to the custom element tag name selector:

- `:host` → `bds-checkbox { ... }`
- `:host([disabled])` → `bds-checkbox[disabled] { ... }`
- `:host(.modifier) .inner-element` → `bds-checkbox.modifier .inner-element { ... }`

This means `:host` selectors in light DOM components are fully valid and globally scoped to the custom element tag. There is no encapsulation boundary — the compiled selector targets the element directly in the document.

## State-Dependent Inner Styles Pattern

To apply inner element styles based on a reflected attribute, use:

```scss
:host([disabled]) {
  .bds-checkbox__box {
    background-color: var(--boreal-bg-disabled, #e0e0e0);
    cursor: not-allowed;
  }
}

:host(:focus-visible) {
  .bds-checkbox__box {
    outline: 2px solid var(--boreal-focus-ring, #0066cc);
  }
}
```

This pattern cannot be replicated without `:host` in a light DOM component. It is the correct and only approach for form controls.
