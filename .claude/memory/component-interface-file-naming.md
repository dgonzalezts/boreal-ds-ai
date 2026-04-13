# Component Interface File Naming Convention

Interface files for web components must use `IComponent.ts` naming, not `IBdsComponent.ts`.

**Correct:** `ITooltip.ts`, `IPopover.ts`, `IBanner.ts`
**Wrong:** `IBdsTooltip.ts`, `IBdsPopover.ts`, `IBdsBanner.ts`

The `Bds` prefix is reserved exclusively for:
- Custom element tag names (`bds-tooltip`)
- Stencil component class names (`BdsTooltip`)

Interface types live in a `types/` subdirectory alongside the component file. This convention was confirmed by renaming `IBdsTooltip.ts` → `ITooltip.ts` during the overlay component review pass.
