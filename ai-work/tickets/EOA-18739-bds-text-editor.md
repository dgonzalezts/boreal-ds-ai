# EOA-18739 — bds-text-editor v1

**Ticket:** EOA-18739
**Status:** In Progress
**Goal:** Deliver version 1 of `bds-text-editor`: a form-associated plain-text message composer with field chips, links and a hard character limit, matching the Figma states.

## Scope

**In:**

- `bds-text-editor` built on ProseMirror, with plain-text output (`\n` between paragraphs).
- Fields: consumer-declared `{ token, label, length? }`, inserted from a Fields dropdown and shown as chips. The value contains the token.
- Link: a URL entered in a popover, checked for safety and inserted as text.
- Character counter (graphemes plus field length) with a hard limit for typing, paste and insertion.
- `toolbar` prop (tool order and dividers), `toolbar` slot for custom tools, and the `insertText()` and `insertField()` methods.
- States: Default, Hover, Focus, Active, Disabled, Readonly, Error, Populated.
- Form association: value, required, `tooLong`, custom validators, reset, disabled fieldset.
- Core accessibility: textbox semantics, label association, chip names, keyboard focus order.
- Localizable copy: every visible and screen-reader string comes from a `labels` object with English defaults (ADR-0008).
- Vue `v-model` mapping.
- One Storybook story and a basic documentation page.
- Unit tests at ≥ 80% coverage.

**Out:**

- Emoji picker and Emoji tool, Short URL, keyboard shortcut to the toolbar, counter announcements, full browser and screen-reader QA, mutation testing, complete documentation (moved to the v2 ticket, ID pending).
- Rich text and HTML output.
- SMS segment counting.
- Auto-growing height.

## Acceptance Criteria

- [ ] Matches Figma node `14-34766` in every state (default brand theme).
- [ ] `value` is plain text; fields are written as their token and read back as chips.
- [ ] Typing, paste and insertion never exceed `charCount`. A value set above the limit shows the error state.
- [ ] Fields and Link insert at the cursor and return focus to the editor.
- [ ] Inside a native form, the editor submits its value, blocks submit when invalid, resets, and follows a disabled fieldset.
- [ ] A partial `labels` object overrides only its own strings; the rest stay in English.
- [ ] Vue `v-model` works in both directions.
- [ ] Unit test coverage ≥ 80%.
- [ ] Review-ready as a draft PR.

## Dependencies

- EOA-20193 (dependency upgrades) must merge before this work can merge.
- Design sign-off for the field chip and the link popover (no Figma design yet).

## Decisions

- ADR-0017: Adopt Raw ProseMirror as the Editing Engine for the Text Editor
- ADR-0018: Text Editor Value Contract and Field Tokens
- ADR-0019: Character Counting and Limits in the Text Editor
- ADR-0020: Toolbar Extension Model for the Text Editor
- ADR-0008: Prop Shape for Localizable UI Copy

## Notes

- Delivery for this ticket is review-ready (draft PR). Merging follows EOA-20193.
- Remaining scope continues under the v2 ticket (draft: `EOA-21589-bds-text-editor-v2.md`).
