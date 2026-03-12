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
- **Event `composed` flag:** `composed: true` on `@Event()` is currently a no-op. Events do not need to cross any Shadow Root boundary today. The flag is set defensively in all events so that if Shadow DOM is ever adopted, events will not silently disappear at the boundary.
- **FACE (`formAssociated: true`):** Form-associated components work via `@AttachInternals()`, which is independent of Shadow DOM mode.
- **BEEQ difference:** The BEEQ reference implementation (`.ai/lib/endava-beeq.txt`) uses Shadow DOM. Any BEEQ patterns that involve `::part()`, CSS custom property tunnelling, or `ElementInternals` shadow-mode behavior do not apply directly — they must be adapted for light DOM before adoption.

## Risk to Track

If Shadow DOM is introduced in future, the following will break silently without the `composed: true` guard already in place on events:
- Any event listener attached above the custom element in the host application's DOM tree.
- React and Angular bindings for those events (they rely on the event bubbling to the document or framework root).
