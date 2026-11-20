# PR Title

feat(web-components): EOA-18739 add bds-text-editor component

---

# PR Body

> Draft PR. It targets `chore/EOA-20193_dependency-upgrades-followup_DG` and will be retargeted to `release/current` after EOA-20193 merges. Only the EOA-18739 commits are in this diff.

## Description

Adds `bds-text-editor`, a form-associated plain-text composer for messages and templates. It has inline field chips, a Link tool, a hard character limit with a counter, a localizable `labels` object and an extensible toolbar slot. The value is plain text, with each field written as its token (for example `Hi {{1}}`), so it can be submitted with a native form and bound with `v-model`.

The editing engine is raw ProseMirror, which owns only the editable area. Everything else (label, toolbar, footer, validation, form association) is composed from existing Boreal components.

## Implementation Details

- **Engine and value contract:** raw ProseMirror with a small schema (paragraphs, text and an atomic `field` node). The serializer and parser are plain TypeScript modules tested without a DOM. See ADRs 0020 to 0023 in `ai-docs/decisions/`.
- **Fields:** each field has a token, a label and an optional declared `length` that counts towards `charCount`. Chips are atomic: one Backspace removes the whole chip.
- **Limit and counter:** a hard limit enforced by a transaction filter, counted in graphemes through `Intl.Segmenter`, with a code-point fallback (Firefox below 125 and Safari below 14.1 count ZWJ emoji families and flags as several characters). Paste is reduced to plain text and truncated at the limit.
- **Form association:** `formAssociatedMixin` and `useFormField`, with `required`, `charCount` and `customValidators` validation, `errorMessage` overriding the built-in messages, and reset to `defaultValue`.
- **Toolbar:** `bds-toolbar` with `bds-button-group`, a Fields `bds-dropdown`, a Link `bds-popover` and a `toolbar` slot for consumer tools. `toolbar` lists tool ids in render order. A `fieldsButton` prop switches the Fields trigger between icon, text and icon with text.
- **Localizable copy (ADR 0014):** one `labels` object with English defaults.
- **Styling:** matches the Figma frames for Outline and Plain across default, hover, focus, active, disabled, readonly and error. Plain is specified for only 3 of the 24 frames, so the others follow the Plain rule.
- **Shared change:** `bds-button-group` now accepts a `bds-dropdown` child (own commit, with specs).
- **Build config:** `stencil.config.ts` declares `bds-text-editor` as its own lazy bundle (own commit), so Stencil's automatic grouping does not merge it with `bds-button`, `bds-dropdown`, `bds-popover` and the other components it uses.

## Impact Analysis

- New component. The only change to an existing component is the `bds-button-group` commit above, which stops warning for a `bds-dropdown` child and gives its trigger the joined styling. Existing buttons are unchanged.
- Adds six `prosemirror-*` runtime dependencies to `@pxglobal/boreal-web-components`.
- The Vue output target maps `bds-text-editor` to `v-model` through `valueChange`. React needs no change.
- **Lockfile:** `pnpm-lock.yaml` was rewritten in pnpm 12.18's compact format by the dependency commit, so its diff is about 14,000 lines. The only content change is 10 new packages: the six `prosemirror-*` packages plus `orderedmap`, `prosemirror-transform`, `rope-sequence` and `w3c-keyname`. `package.json` in the web-components package also has cosmetic reordering and indentation fixes from the same command.

## Testing Conducted

**Automated:**

- [x] Unit tests for the core helpers (serializer, counter, plugins) and the component (basics, form, validation, events, toolbar, labels, a11y, insertion): 11 suites for the editor, 728 tests.
- [x] Coverage of at least 80% on every new file (lines 100% on all helpers, `bds-text-editor.tsx` 100% lines and about 94% branches).
- [x] A failure-mode catalog (`FM-TE-01` to `FM-TE-07`) with the contracts decided and covered.
- [x] `pnpm lint` (0 errors), `pnpm test` (389 suites, 5,702 tests), `pnpm build` and `pnpm validate:all` pass.

**Manual:**

- [x] Smoke QA in Chromium: required form submit and reset, chips, character limit with paste and bursts, Fields and Link tools, Enter and Esc in the link popover, real Tab order and `:focus-visible`.
- [x] Form, limit, link and focus checks also pass in WebKit and Firefox (Playwright builds).
- [x] Styling compared with the Figma frames at 100% in Chromium, WebKit and Firefox; computed-style comparison after the SCSS refactor shows no differences.
- [x] `v-model` verified in both directions with `pnpm dev:pack:vue`.
- [ ] Real IME and mobile keyboards, Safari itself, and VoiceOver or NVDA are not verified.

## Bundle size and dependencies

Six `prosemirror-*` packages are added as runtime dependencies of `@pxglobal/boreal-web-components`. They pull in four small transitive packages. All ten are MIT licensed, from the ProseMirror project, and have no dependencies outside the ProseMirror family. The engine choice and the alternatives considered (a rich-text framework, a from-scratch editable) are in ADR 0020 (`ai-docs/decisions/`).

| Package | Version | Role |
| --- | --- | --- |
| `prosemirror-model`, `-state`, `-view` | ~1.25.13, ~1.4.4, ~1.42.9 | Schema, editor state and the editable view |
| `prosemirror-history`, `-keymap`, `-commands` | ~1.5.1, ~1.2.3, ~1.7.2 | Undo and redo, key bindings, base editing commands |
| `prosemirror-transform`, `orderedmap`, `rope-sequence`, `w3c-keyname` | transitive | Used by the six above |

**Impact on the library** (measured on this branch against its base; sizes are minified gzip unless stated):

- **Published package:** the JavaScript, type and manifest files in `dist` grow from 26.7 MB to 28.2 MB (+1.45 MB, +5.4%), and the `components-build` folder from 3.8 MB to 4.1 MB (+0.24 MB, +6.3%). The ten ProseMirror packages add about 2.5 MB unpacked to an install, because they are declared as dependencies like the other bundled libraries (`date-fns`, `@floating-ui/dom`, `dompurify`).
- **Apps that use the React or Vue wrappers:** the team's October tree-shaking review found that the wrappers do not tree-shake today, so every app already pays for the whole library (about 223 to 230 KB). Until that is fixed, the editor adds about 72 to 75 KB to every React and Vue app, used or not (bundling every component entry with and without the editor gave +75 KB, about +7% in that measurement). The review's follow-ups 1 and 2 (keep `/*@__PURE__*/` in the wrapper output and add `sideEffects` to the packages) would make that cost apply only to apps that use the editor. They are outside this PR.
- **Apps that import components directly or use the lazy loader:** nothing changes unless the editor is used. `bds-button` stays at 19.25 KB through direct import and 5.2 KB as a lazy entry, and `bds-date-picker` at 76.8 KB.
- **When the editor is used:** ProseMirror alone is about 64 KB (208 KB raw), and `bds-text-editor` bundled on its own, with the Stencil runtime and the components it composes, is about 123 KB. The lazy entry is about 144 KB gzip (607 KB raw), larger because the published lazy entries are not minified.

**Grouping effect:** Stencil's automatic grouping merged the editor with 12 components it shares dependencies with (`bds-button`, `bds-button-group`, `bds-checkbox`, `bds-divider`, `bds-dropdown`, `bds-list-menu`, `bds-list-menu-item`, `bds-popover`, `bds-text-field`, `bds-toolbar`, `bds-tooltip` and `bds-typography`) into one lazy entry, `bds-button_13`, of 860 KB raw and 197 KB gzip, so a page that used only a `bds-button` would download it instead of the 5.2 KB entry. This PR declares the editor as its own bundle in `stencil.config.ts` (`bundles: [{ components: ['bds-text-editor'] }]`), which keeps those components in their small entries and loads the editor only when used.

## Related Changes

- **boreal-docs:** story with controls and static examples (including a toolbar slot and an interactive form example) and MDX documentation.
- **boreal-vue:** `v-model` mapping in the Vue output target.
- **No changes to** `boreal-style-guidelines`; existing tokens are reused.

## Additional Remarks

- **Design:** the field chip and the link popover are not in the Figma frame; design validated both looks. The text-only Fields trigger has no Figma design and is styled with the existing button and tokens.
- **Docs:** the Do and Don't cards in the MDX come from the ADRs and the component, because the Notion guidance was not available. A reviewer who knows that guidance should read them. The MDX is not Prettier-clean, like two existing MDX files.
- **Known limitations:**
  - The `emoji` toolbar id is accepted and renders nothing yet.
  - Built-in validation messages are English only and can be replaced with `errorMessage`.
  - A runtime switch of `fieldsButton` back to `icon` can leave the trigger slightly wider because `bds-button` does not re-detect removed slot text.
  - Slotted toolbar content removed after mount is not detected.
  - The link popover hides its arrow; with the arrow on it points to the right of the Link button because `bds-popover` hardcodes its offset for start placements.
- **Follow-ups not in this PR:** a `bds-button` accessible-name warning for text-only buttons whose text is slotted, the `bds-popover` arrow offset, `reportValidity()` not moving focus (shared `useFormField`), localizable validation messages across form components (needs an ADR for strings with numbers), the wrapper tree-shaking fixes from the team's October review (its own branch and PR).
- **Next version:** the Emoji tool and picker, `linkTransform`, keyboard and announcement support, IME at the limit and full browser and screen reader QA.
- **Merge message:** keep the PR title as the squash commit title.

## References

Refs EOA-18739

---

## Checklist

### General

- [x] Follows conventional commit format: `feat(scope): TICKET-ID description`
- [x] Ticket reference included (`Refs` EOA-18739)
- [x] Code adheres to TypeScript strict mode, no `any` or implicit types
- [x] Self-reviewed code for quality, readability, and correctness
- [x] All tests pass locally

### Boreal DS: Component Standards

- [x] Design tokens used exclusively, no hard-coded colors, spacing, or radii
- [x] Component tag uses `bds-` prefix
- [x] All props have explicit TypeScript types
- [x] Events use bare `@Event()`
- [x] SCSS follows the `@use` pattern
- [x] Light DOM patterns documented

### Boreal DS: Form Components

- [x] Uses formAssociatedMixin for FACE boilerplate
- [x] Implements IFormControl<T> interface
- [x] Includes @Method() wrappers for checkValidity() and reportValidity()
- [x] Validation tested with built-in and custom validators

### Testing

- [x] Unit test coverage of at least 80%
- [x] Tests cover happy path, error cases, and edge cases
- [ ] Accessibility verified with screen readers (accessibility tree and keyboard verified; VoiceOver and NVDA pending)
- [ ] Manual testing completed in all supported browsers (Chromium, WebKit and Firefox done; Safari itself pending)

### Documentation

- [x] JSDoc added to all public APIs (props, events, methods)
- [x] Storybook story created with usage examples
- [x] Storybook MDX documentation added (usage, API, examples)

### Performance and Compatibility

- [x] No new console warnings or errors from the component
- [x] Bundle size impact assessed (see Bundle size and dependencies)
- [x] No regression in existing functionality
