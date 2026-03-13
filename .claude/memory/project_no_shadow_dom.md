# Boreal DS — Light DOM Only, No Shadow DOM

## Verified Fact

All components in `packages/boreal-web-components` use light DOM. No `@Component` decorator in the codebase has `shadow: true` or `scoped: true`. Example from `bds-button`:

```ts
@Component({
  tag: 'bds-button',
  styleUrl: 'bds-button.scss',
  formAssociated: true,
})
```

## Implications

- **Styling:** Global CSS and design token stylesheets apply directly to component internals without needing `::part()` selectors or CSS custom properties to cross a Shadow Root boundary.
- **Event `composed` flag:** `composed: true` is a no-op in light DOM. Boreal DS uses bare `@Event()` with no options — this aligns with BEEQ and Aqua DS (see ADR `.ai/decisions/0003-event-options-convention.md`). If Shadow DOM is ever introduced, this ADR should be revisited.
- **FACE (`formAssociated: true`):** Form-associated components work via `@AttachInternals()`, which is independent of Shadow DOM mode.
- **BEEQ difference:** The BEEQ reference implementation (`.ai/lib/endava-beeq.txt`) uses Shadow DOM. Any BEEQ patterns that involve `::part()`, CSS custom property tunnelling, or `ElementInternals` shadow-mode behavior do not apply directly — they must be adapted for light DOM before adoption.

## Note on Future Shadow DOM Adoption

If Shadow DOM is introduced, ADR `.ai/decisions/0003-event-options-convention.md` must be revisited. Events with bare `@Event()` do not cross shadow boundaries. The documented consumer pattern (direct element attachment) would also need to be re-evaluated.
