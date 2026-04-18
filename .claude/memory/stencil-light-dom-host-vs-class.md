# Stencil Light DOM — Direct Tag Selectors, Not `:host`

## The Critical Rule

**In Boreal DS light DOM components, `:host` does NOT work.** Use the component tag name directly as the root CSS selector.

## Why `:host` Doesn't Work

From [MDN](https://developer.mozilla.org/en-US/docs/Web/CSS/:host):

> The `:host` CSS pseudo-class selects the shadow host of the **shadow DOM** containing the CSS it is used inside
>
> **Note: This has no effect when used outside a shadow DOM.**

Boreal DS components use light DOM (`@Component` decorators omit `shadow: true`). Without a shadow root, the `:host` pseudo-class matches nothing.

## Correct Pattern for Light DOM

Use the component tag name directly:

```scss
// ✅ Correct for light DOM
bds-button {
  display: inline-flex;
  position: relative;
}

bds-button[disabled] {
  cursor: not-allowed;
  opacity: 0.6;
}

bds-checkbox {
  display: inline-flex;
  cursor: pointer;
}

bds-checkbox:focus-visible .bds-checkbox__box {
  outline: 2px solid $boreal-stroke-focus;
}

bds-grid-item[col-span="full"] {
  grid-column: 1 / -1;
}
```

## What About Stencil's Compilation?

While Stencil technically compiles `:host` to the tag name selector in light DOM components, the browser **does not recognize `:host` as a functional pseudo-class** without a shadow boundary. The resulting CSS works, but only because Stencil transformed it—not because `:host` is valid in this context.

Using direct tag selectors makes the intent clear and avoids relying on a compilation quirk.

## Verified Codebase Pattern

Every component in Boreal DS uses direct tag selectors:

- `bds-button { ... }` ([bds-button.scss](../../packages/boreal-web-components/src/components/actions/bds-button/bds-button.scss))
- `bds-checkbox { ... }` ([bds-checkbox.scss](../../packages/boreal-web-components/src/components/forms/bds-checkbox/bds-checkbox.scss))
- `bds-grid { ... }` ([bds-grid.scss](../../packages/boreal-web-components/src/components/layout/bds-grid/grid/bds-grid.scss))
- `bds-grid-item[col-span='full'] { ... }` ([bds-grid-item.scss](../../packages/boreal-web-components/src/components/layout/bds-grid/grid-item/bds-grid-item.scss))

No component uses `:host` in its SCSS.

## Scoping and Naming

These selectors are **globally scoped**. To prevent collisions:

- All components use the `bds-` tag prefix
- Inner elements follow BEM naming: `.bds-button__content`, `.bds-checkbox__box`, `.bds-grid-item__inner`
- Modifier classes follow BEM: `.bds-button--primary`, `.bds-checkbox--checked`

## Reflection Pattern

Props need `reflect: true` when:

1. The prop value is referenced in a CSS **attribute selector** (e.g., `bds-grid-item[col-span='full']`)
2. The prop must remain observable as an HTML attribute at runtime (e.g., `disabled`)

**Do not reflect** props that are only used in inline styles or class modifiers—reflection adds DOM overhead.

Example:

```tsx
// ✅ Reflect — used in attribute selector
@Prop({ reflect: true }) colSpan: 'full' | number = 12;
// CSS: bds-grid-item[col-span='full'] { ... }

// ❌ Don't reflect — handled via inline style
@Prop() offset: number = 0;
// JS: <Host style={{ 'grid-column-start': this.offset + 1 }}>
```
