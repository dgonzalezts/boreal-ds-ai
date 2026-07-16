# AI-001 — bds-button Accessibility & Documentation Improvements

**Ticket:** AI-001 (internal)
**Goal:** Improve bds-button accessibility guarantees and clarify documentation around the `label` prop vs visible text.

## Scope

**In:**
- Add development-mode warning when `label` prop is provided without visible text (icon-only button scenario)
- Add development-mode warning when button has no accessible name (no label prop, no visible text, no icon slot with aria-label)
- Clarify JSDoc on `label` prop to explicitly state it's for accessibility only, not visible text
- Add Storybook stories demonstrating proper icon-only button usage with `label` prop
- Update MDX documentation with accessibility guidance for icon-only buttons

**Out:**
- Changing `label` prop to render visible text (breaking change)
- Adding new props for visible text (separate concern)
- Changes to bds-button.scss (SCSS changes not needed for this issue)

## Acceptance Criteria

- [ ] Development warning logs when `label` provided but default slot is empty AND icon slot is used (valid icon-only button)
- [ ] Development warning logs when button has NO accessible name (no label, no default slot content, no icon with aria-label)
- [ ] JSDoc on `label` prop explicitly states "For accessibility only - does not render visible text"
- [ ] Storybook story: "Icon-only button with accessibility label"
- [ ] MDX docs include accessibility section for icon-only buttons
- [ ] Unit tests cover the warning logic

## Dependencies

- None

## Open Questions

- Should we add a separate `text` prop for visible text? (Out of scope for this ticket, but worth documenting as future consideration)
- Should we use `console.warn` in development only, or a custom dev warning utility if one exists?