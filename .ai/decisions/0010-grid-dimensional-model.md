# ADR 0010 — Grid dimensional model: responsive gutters and container width

**Date:** 2026-04-15
**Status:** Accepted

---

## Context

The ticket (`.ai/tickets/grid-system-&-component.md`) describes a 12-column grid with "fixed gutters as defined in boreal-styleguidelines" and a "max-width of 960px" for the fixed layout mode. The Figma source of truth (`7273:43888`) was reviewed and revealed two discrepancies that required decisions before implementation.

---

## Decision drivers

### Issue 1 — Figma specifies a 12px gutter at `$mobile` and `$tablet`

The Figma breakpoints table specifies a `relleno` (column padding) of **12px** at `$mobile` and `$tablet`, which produces a **24px total gutter**. This is the only value in the entire grid spec that does not fall on the 8px grid system used throughout the design system.

All other gutter values are on-grid: 16px (`$desktop`), 24px (`$widescreen`, `$fullhd`).

The ticket describes gutters as "fixed", which would lock the implementation to a non-standard 12px value that requires a one-off token not present in `primitives.json`.

### Issue 2 — The ticket's "max-width: 960px" is ambiguous

The Figma grid diagram shows the **960px as the column area width**, not the full container width. At `$desktop`, outer margins are 16px on each side, making the true container **992px**. Implementing `max-width: 960px` directly on the container would clip the outer margins at the desktop breakpoint.

---

## Decision

### Gutter: use 16px relleno at all breakpoints, including `$mobile` and `$tablet`

The 12px value in Figma is not intentional — it is the designer rounding to `1rem` in a context where the base font size was assumed to be 12px. Aligning to 16px:

- Keeps every gutter value on the 8px grid system
- Matches `$desktop` exactly, eliminating a visual jump at the 769px → 960px transition
- Uses `$boreal-spacing-m` (16px), a token that already exists in `primitives.json`

The gutter also **varies per breakpoint** — it is not "fixed" in the sense of a single static value:

| Breakpoint | Relleno (each side) | Total gutter |
|---|---|---|
| `$mobile` | 16px | 32px |
| `$tablet` | 16px | 32px |
| `$desktop` | 16px | 32px |
| `$widescreen` | 24px | 48px |
| `$fullhd` | 24px | 48px |

**Action required:** Notify design to update the Figma breakpoints table for `$mobile` and `$tablet` from 12px → 16px relleno.

### Container model: 960px is the column area, container includes outer margins

The `bds-grid` fixed layout is implemented as:

```scss
:host([layout="fixed"]) {
  max-width: calc(960px + 2 * var(--bds-grid-margin));
  padding-inline: var(--bds-grid-margin);
}
```

Where `--bds-grid-margin` is responsive (0 at mobile/tablet, 16px at desktop, 24px at widescreen, 32px at fullhd). This correctly produces a 992px container at `$desktop`.

---

## Consequences

**Positive:**
- All spacing values remain on the 8px grid — no one-off tokens needed
- Consistent gutter rhythm from mobile through widescreen
- Container model accurately reflects the Figma intent

**Constraint introduced:**
- The Figma file diverges from the implementation at `$mobile` and `$tablet` until design updates the source. The delta is small (12px → 16px) but should be tracked.

---

## References

- Figma node: `7273:43888` in file `htCJc5chrgNRK337cyc14K`
- Ticket: `.ai/tickets/grid-system-&-component.md`
- Plan: `.ai/plans/EOA-12029_grid_foundational_system.md`
