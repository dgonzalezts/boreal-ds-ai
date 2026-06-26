## Description

As a Proximus Frontend Developer, I want to use a standardized, 12-column grid system component (bds-grid), So that I can align UI elements consistently across all global products, following the approved Boreal design tokens and responsive breakpoints.

### Technical Requirements

- 12-Column Layout: A center-aligned 12-column adaptive layout.
- Layout Modes: Support for both Fixed (max-width: 960px for long-form content) and Fluid (full-screen for data-heavy portals).
- Navigation Reserves: The grid must account for Global Navigation (min 64px) and Container Navigation (min 230px) on the left.
- Breakpoint System: (Reference the "Standard Breakpoints" table in the PDF) for responsive behavior.
- Implementation Strategy: Use a "Compound Component" pattern:
  - <bds-grid>: The main container managing gutters and max-widths.
  - <bds-grid-item>: The child component managing column spans and offsets.

### Notes for Developers

- Use CSS Grid for the modern implementation, but provide a Flexbox fallback if the browser support matrix requires it (per PI 7 guidelines).
- While the grid is horizontal, the component should not interfere with the 4:3 aspect ratio logic for internal elements (as mentioned on page 5 of the PDF).
- Do not include margin/padding within the grid-item that cannot be overridden; use slots to ensure the grid only manages position, not content styling.

## Acceptance Criteria

[ ] The grid must default to a 12-column structure.
[ ] Support for fluid (width: 100%) and fixed (max-width: 960px) properties.
[ ] Implementation of fixed gutters between columns as defined in boreal-styleguidelines.
[ ] The grid must automatically adjust based on the viewport: - Mobile: 4 columns. - Tablet: 8 columns. - Desktop: 12 columns.
[ ] bds-grid-item must accept responsive props (e.g., cols-sm="4", cols-md="8", cols-lg="12").
[ ] The grid must allow for an "offset" or "sidebar-reserve" to accommodate the 64px or 230px navigation panels without breaking the 12-column alignment.
[ ] Zero Hardcoding: All spacings and widths must use CSS Custom Properties from boreal-styleguidelines.
[ ] Shadow DOM: Must use Stencil's Shadow DOM to prevent global style leakage.
[ ] Documentation: Storybook story including "Grid Overlay" toggle to visualize column alignment during development.
[ ] Testing: Unit tests verifying that column math calculates correctly across different screen widths.

---

## Implementation Notes (2026-04-15)

This ticket was reviewed against Figma node `7273:43888` and the Colibri reference implementation before implementation began. Several acceptance criteria above diverge from the agreed implementation. The active plan is the source of truth:

**Plan**: `.ai/plans/EOA-12029_grid_foundational_system.md`
**ADRs**: `.ai/decisions/0010-grid-dimensional-model.md`, `0011-grid-navigation-reserve.md`, `0012-grid-no-flexbox-fallback.md`

### Corrections to original AC

| Original | Correction | Reason |
|---|---|---|
| 3 breakpoints (mobile / tablet / desktop) | **5 breakpoints**: $mobile (320px), $tablet (769px), $desktop (960px), $widescreen (1152px), $fullhd (1344px) | Figma defines 5; $widescreen and $fullhd were omitted from the ticket |
| "Fixed gutters" | **Responsive gutters**: 16px at $mobile–$desktop, 24px at $widescreen–$fullhd | Figma gutters vary per breakpoint; "fixed" was misleading |
| max-width: 960px | **960px is the column area**; true container at $desktop = 992px (960 + 2×16px outer margin) | Figma diagram confirmed margin is additive |
| Shadow DOM required | **Removed** — Boreal DS uses light DOM throughout; Stencil's tag-name scoping prevents style leakage without a shadow boundary | Contradicts project convention |
| `sidebar-reserve` prop | **`--bds-grid-nav-offset` CSS custom property** on the host element | Decouples the grid from application navigation state (see ADR-0011) |
| Flexbox fallback | **Removed** — CSS Grid has ~98% global support; PI 7 browser matrix was not found (see ADR-0012) | |
| `cols-sm`, `cols-md`, `cols-lg` props | **`col-span-mobile`, `col-span-tablet`, `col-span-desktop`, `col-span-widescreen`, `col-span-fullhd`** | Aligned to Figma token names; `col-span` distinguishes item spanning from container column count |
