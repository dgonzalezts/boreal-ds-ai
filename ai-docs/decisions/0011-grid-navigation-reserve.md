# ADR 0011 — Grid navigation reserve: CSS custom property over component prop

**Date:** 2026-04-15
**Status:** Accepted

---

## Context

The ticket requires the grid to account for a **Global Navigation** reserve (min 64px) and a **Container Navigation** reserve (min 230px) on the left. The ticket proposes an `"offset"` or `"sidebar-reserve"` prop on `bds-grid` to handle this.

The Figma guideline confirms the two navigation widths (64px and 64px + 230px = 294px) as visual context for the grid structure diagram, but does not specify a component API for them.

---

## Decision drivers

A component prop approach (`sidebar-reserve="64"`) creates tight coupling between the grid component and the host application's navigation state:

- Navigation width is runtime state controlled by the application shell, not a design-time constant
- A prop requires a Stencil re-render whenever the navigation collapses or expands
- It leaks application layout concerns into a layout primitive that should be context-agnostic
- It is not composable — a prop accepts one value, but applications may need to mix global nav + container nav widths dynamically

CSS custom properties are the correct primitive for this pattern:
- They cascade from the host application into the shadow DOM naturally
- Changing them does not require a component re-render (CSS-only update)
- The consuming application owns the value and can compute it dynamically (`calc(64px + 230px)`)
- The grid component remains ignorant of what is causing the offset

---

## Decision

Expose `--bds-grid-nav-offset` as a CSS custom property on the `bds-grid` host element. The component applies it as a `margin-inline-start` (or equivalent) offset:

```scss
:host {
  margin-inline-start: var(--bds-grid-nav-offset, 0px);
}
```

Consuming applications set the value at the application level:

```css
/* Global nav only */
bds-grid { --bds-grid-nav-offset: 64px; }

/* Global nav + container nav */
bds-grid { --bds-grid-nav-offset: 294px; }

/* Collapsed state */
bds-grid { --bds-grid-nav-offset: 64px; }
```

The component does not ship with any `sidebar-reserve` or `offset` prop. No pre-defined navigation width constants are baked into the component.

---

## Consequences

**Positive:**
- Grid component is decoupled from application navigation state
- No re-render cost when navigation expands/collapses
- Applications can animate the offset via CSS transitions without touching the component
- Works identically in all framework wrappers (React, Vue, vanilla)

**Constraint introduced:**
- The consuming application is responsible for computing the correct offset value. This should be documented clearly in the Storybook story and MDX docs with the two canonical values (64px, 294px).

---

## References

- Figma node: `7273:43888` in file `htCJc5chrgNRK337cyc14K`
- Ticket: `.ai/tickets/grid-system-&-component.md`
- Plan: `.ai/plans/EOA-12029_grid_foundational_system.md`
