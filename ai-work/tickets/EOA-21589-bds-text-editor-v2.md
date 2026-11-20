# EOA-21589 — bds-text-editor v2

**Ticket:** [EOA-21589](https://telesign.atlassian.net/browse/EOA-21589)
**Status:** Draft
**Goal:** Complete `bds-text-editor` with an emoji picker, Short URL support and the remaining accessibility work, verified across browsers, frameworks, screen readers and brand themes.

## Jira fields (copy when creating)

- **Summary:** Implement Text Editor v2: emoji picker, Short URL and accessibility hardening
- **Type:** Story
- **Links:** follows EOA-18739 (v1)

## Scope

**In:**

- `bds-emoji-picker`, a reusable component:
  - category tabs and search in English and Spanish
  - full keyboard navigation of the emoji grid
  - flags hidden on devices that can't display them
  - emoji data loaded only when the picker opens
- Emoji tool in `bds-text-editor`: inserts at the cursor, respects the limit, and closes after a pick.
- Short URL: an optional consumer-supplied transform for links, with loading and error handling ("Insert as is").
- Accessibility:
  - keyboard shortcut from the text to the toolbar (`Alt+F10`)
  - announcements near and at the character limit
  - chip borders in high-contrast mode
- Input-method (Japanese, Chinese, Korean) typing at the character limit.
- Full QA: Chromium, Firefox, WebKit and Safari; React and Vue wrappers; NVDA and VoiceOver.
- Visual checks in all four brand themes, bundle-size verification, mutation testing (≥ 90%), and complete documentation for both components.

**Out:**

- Rich text and HTML output (a later version).
- SMS segment counting.
- Auto-growing height.

## Acceptance Criteria

- [ ] The emoji picker matches the signed-off design in all four themes. Search works in English and Spanish, with or without accents.
- [ ] The Emoji tool inserts at the cursor, respects the limit and returns focus to the editor.
- [ ] Short URL success, failure and too-long cases behave as designed.
- [ ] Input-method typing completes correctly at the character limit.
- [ ] Keyboard and screen-reader behaviour matches the design on NVDA and VoiceOver.
- [ ] React and Vue behaviour matches the web component, including `v-model` and form submit.
- [ ] Editor and emoji code load only where used (bundle check).
- [ ] Coverage ≥ 80% and mutation score ≥ 90%.

## Dependencies

- EOA-18739 (v1) merged.
- Design sign-off for the emoji picker (the current production picker is the reference).

## Notes

- Plan: `ai-work/plans/EOA-21589-bds-text-editor-v2.md`.
