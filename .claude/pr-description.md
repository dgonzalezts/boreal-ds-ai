# PR Title

docs(docs): EOA-16692 add bds-date-picker Phase 1 Storybook documentation

---

# PR Body

## Description of Changes

Adds the Task 21 (Phase 1) Storybook story and MDX documentation for `bds-date-picker`, following `bds-select.stories.ts`/`.mdx` as the structural template. Also includes three small fixes to shared `boreal-docs` infrastructure, each discovered and required while getting this specific documentation to render/behave correctly.

**New files:**

- `apps/boreal-docs/src/stories/forms/bds-date-picker/bds-date-picker.stories.ts` — 9 stories (`Default`, `PreselectedValue`, `CustomFormat`, `CustomLocale`, `HideArrow`, `Disabled`, `CustomFooterLabels`, `InteractiveFormExample`), full `argTypes` coverage for every `bds-date-picker` prop/event plus the internal `bds-calendar-grid` fields it composes.
- `apps/boreal-docs/src/stories/forms/bds-date-picker/bds-date-picker.mdx` — full narrative docs: composition, preview, states, footer labels, form integration (including the complementary field-level `required` pattern and the slotted-field constraints table), accessibility, and a `Properties` section split into `### bds-date-picker` / `### bds-calendar-grid` sub-tables (mirroring `bds-table.mdx`'s `bds-table`/`bds-table-column`/`bds-table-column-group` split).

**Modified (shared `boreal-docs` infrastructure):**

- `apps/boreal-docs/package.json` (+`pnpm-lock.yaml`) — added `date-fns@^4.4.0` as a devDependency, required so the `CustomLocale` story can import and render a real French locale (`import { fr } from 'date-fns/locale'`) instead of only showing static, unexecuted example code.
- `apps/boreal-docs/src/components/story/FormDemo/FormDemo.ts` — added an `invalid` event listener (capture phase) so a blocked form submission (e.g. a required field left empty) surfaces "Form submission blocked by validation" in the demo's output panel. Previously, `FormDemo`'s `submit` handler assumed `event.defaultPrevented` would be reachable to show this message — but the browser never dispatches `submit` at all when a required field is invalid, so that branch was dead code and the output panel silently did nothing. Affects every story using `<form-demo>`, not just `bds-date-picker`'s.
- `apps/boreal-docs/src/components/docs/KeyboardDocs/KeyboardDocs.module.css` — fixed the shared `KeyboardDocs` component's table shrinking to its content width (as low as ~230px) instead of filling the available space. A global `.sbdocs-content table { display: block; width: fit-content }` rule (intended to let genuinely wide tables scroll instead of squishing) was beating the component's own `.table { width: 100% }` on CSS specificity. Verified this also fixes `bds-table.mdx`'s own `Keyboard interaction` table, with no regression elsewhere.
- `apps/boreal-docs/.storybook/styles/preview.css` — added a new `.bds-doc__wide-table` opt-in utility class (same pattern as the existing `bds-doc__canvas--with-background`), so a plain Markdown table can be wrapped in `<div className="bds-doc__wide-table">` to opt out of the fit-content shrink rule above, without needing raw JSX/inline styles per table. Used by the two small reference tables in `bds-calendar-grid`'s Properties sub-section.

## Motivation

- Task 21 of the `bds-date-picker` v1 plan (`ai-work/plans/EOA-16692-bds-date-picker-v1.md`) requires Storybook documentation before the component can be considered feature-complete for this release.
- The three infrastructure fixes were each blocking issues found live while verifying the new docs against a running Storybook instance (not theoretical) — none are cosmetic-only.

## Relevant Sections Updated

- **`apps/boreal-docs/src/stories/forms/bds-date-picker/`** — new story/MDX pair (see above).
- **`apps/boreal-docs/src/components/story/FormDemo/FormDemo.ts`** — `invalid` event handling.
- **`apps/boreal-docs/src/components/docs/KeyboardDocs/KeyboardDocs.module.css`** — table width fix.
- **`apps/boreal-docs/.storybook/styles/preview.css`** — new `bds-doc__wide-table` utility class.
- **`apps/boreal-docs/package.json`** — new `date-fns` devDependency.

## Type of Documentation Change

- [x] New documentation (guide, tutorial, reference)
- [ ] Updated existing documentation (corrections, clarifications, expansions)
- [ ] Removed outdated documentation
- [ ] Restructured documentation (improved organization, navigation)
- [x] Added code examples or demos
- [ ] Fixed typos, grammar, or formatting

## Review Considerations

- **Form integration section**: verify the `required`/optional field distinction in `InteractiveFormExample` reads clearly — only "Appointment date" is required (both component-level via `ElementInternals` and field-level for the visible asterisk); "Follow-up date" is genuinely optional and submits as an empty string in `FormData` when left blank.
- **Slotted-field constraints**: confirm the `pattern`/`name`/`clearable` guidance matches the actual verified behavior described in the plan's Task 21 status notes.
- **`locale` vs `labels` prop demonstration**: `CustomLocale` uses a Lit property binding plus a `docs.source.code` override (the `date-fns` `Locale` object can't be inlined as `<script>`-tag JSON, and a `<script type="module">import(...)</script>` tag doesn't resolve bare specifiers in this unbundled preview context — confirmed via live reproduction). `CustomFooterLabels` uses a real `<script>` tag with `document.querySelector('#id').labels = {...}`, matching `bds-table.stories.ts`'s `data`/`rows` pattern, since `labels` is plain serializable data. Worth a second pair of eyes on whether this split is clear enough as-is or needs an inline comment.
- **Properties section split**: `bds-calendar-grid`'s props/events are documented under their own `### bds-calendar-grid` sub-heading (internal-only, `control: false`, no live story) rather than a separate top-level narrative section — mirrors `bds-table.mdx`'s `bds-table-column`/`bds-table-column-group` convention.
- **Shared-file fixes**: the `KeyboardDocs.module.css` and `FormDemo.ts` changes affect every other component's docs using those shared pieces (`bds-table.mdx`'s own Keyboard interaction table, any story using `<form-demo>`) — verified no regressions on `bds-table.mdx` specifically, but worth a broader smoke-check if reviewers know of other heavy `<form-demo>` consumers.

## Additional Remarks

- All 9 stories, both MDX Properties sub-tables, the `CustomLocale`/`CustomFooterLabels` code-snippet rendering, and the `InteractiveFormExample` required/optional/blocked-submission flow were verified live via a running `pnpm dev:docs` instance (Playwright-driven), not just reviewed as source — see the plan's Task 21 status note for the full verification log.
- `bds-doc__wide-table` is a general-purpose utility, not specific to this component — any future narrow-content reference table elsewhere in the docs site can opt into it the same way.
- Out of scope, flagged but not fixed here: several of `bds-table.mdx`'s own plain-Markdown tables (measured 419–563px) are subject to the same underlying fit-content shrink and could also benefit from `bds-doc__wide-table`, but weren't touched since they're outside this PR's purpose.
- Also out of scope, flagged but not fixed here: a visible blinking caret on `bds-date-picker`'s (and likely `bds-select`'s, in non-multiselect mode) read-only trigger field — `bds-text-field.scss`'s `--selectable` modifier is missing the `caret-color: transparent` that its sibling `bds-tag-field.scss`'s identical modifier already has. Confirmed via live computed styles; not fixed in this PR since it touches component source, not docs.

## References

Refs EOA-16692

---

## Checklist

### General

- [x] Follows conventional commit format: `docs(scope): TICKET-ID description`
- [x] Ticket reference included
- [x] Self-reviewed for clarity and correctness
- [x] No broken links or references

### Documentation Quality

- [x] Content is clear, concise, and grammatically correct
- [x] Technical terms are explained or linked to definitions
- [x] Code examples are correct and tested
- [x] Examples follow Boreal DS conventions
- [x] Tone and style match existing documentation

### Accuracy

- [x] Information is technically accurate
- [x] Code examples run without errors
- [x] API signatures match actual implementation
- [ ] Version numbers are correct (if mentioned)
- [x] Links point to current, valid URLs

### Completeness

- [x] Covers the intended topic thoroughly
- [x] Includes common use cases and examples
- [x] Addresses known pain points or FAQs
- [x] Cross-referenced from related documentation
- [x] Table of contents updated (if applicable)

### Boreal DS Specifics

- [x] Design token usage documented correctly
- [x] Component props/events/methods match JSDoc
- [x] Stencil patterns (FACE, mixins, etc.) explained accurately
- [ ] Framework wrapper usage shown (React/Vue) if applicable — deferred to Task 22 (React/Vue wrapper parity check)
- [x] Accessibility guidance included for component docs

### Formatting & Structure

- [x] Markdown formatting is correct
- [x] Headings follow proper hierarchy (h1 → h2 → h3)
- [x] Code blocks use correct syntax highlighting
- [x] Lists, tables, and images render properly
- [x] File structure is logical and navigable

### Testing

- [x] Documentation renders correctly in target platform (Storybook/GitHub/README)
- [x] All code examples tested and verified working
- [x] Links tested and valid
- [x] Images load correctly
- [x] No broken formatting or rendering issues
