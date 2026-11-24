---
ticket: EOA-21589
component: bds-text-editor
status: pending
created: 2026-11-13
---

# bds-text-editor v2 (emoji, Short URL, hardening) Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use executing-plans to implement this plan task-by-task.

**Goal:** Complete `bds-text-editor` with a reusable `bds-emoji-picker` and the Emoji tool, Short URL support and the remaining accessibility work. Then verify it across browsers, wrappers, assistive technology and all four themes, and close the mutation-testing gate for v1 and v2.

**Ticket brief:** [`ai-work/tickets/EOA-21589-bds-text-editor-v2.md`](../tickets/EOA-21589-bds-text-editor-v2.md) · Previous version: [`EOA-18739-bds-text-editor-v1.md`](./EOA-18739-bds-text-editor-v1.md)

**Design:** [`ai-work/sessions/2026-11-13-bds-text-editor-design.md`](../sessions/2026-11-13-bds-text-editor-design.md) · Research: [`ai-work/research/2026-11-13-bds-text-editor-engine-spike.md`](../research/2026-11-13-bds-text-editor-engine-spike.md)

**Decisions:** ADR 0020 (engine), 0021 (value contract and field tokens), 0022 (counting and limits), 0023 (toolbar extension model), 0014 (localizable copy) — `ai-docs/decisions/`. All Proposed until review.

**Architecture:**
- **Picker.** `bds-emoji-picker` is a panel-only Molecule composed of `bds-search-bar`, `bds-tab-group` and `role="grid"` cells driven by `KeyboardController`. It lazy-loads a trimmed dataset generated from `emojibase-data`.
- **Editor additions.** The editor gains an Emoji tool (`bds-popover` + picker), `linkTransform`, and the remaining accessibility features on top of the v1 core.

**Tech Stack:** As v1, plus `emojibase-data` ^18.0.0 (dev only, used by the generator; re-verify the version), Stryker, and Chromatic.

**Branch:** create it from `release/current` after v1 (EOA-18739) merges.

**Working rules:** as the v1 plan (`fnm use`, Context7 or the official ProseMirror reference, no inline comments, tokens only, `index.html` never committed, no ticket IDs in tests, no version labels in consumer text, commits only after confirmation, no `Co-Authored-By`).

**Localizable copy (ADR 0014):**
- The picker has more than one string, so it exposes one `labels?: EmojiPickerLabels` object with `DEFAULT_EMOJI_PICKER_LABELS`, not flat props.
- Every new editor string is added as a key of the existing `TextEditorLabels`, never as a literal.
- **Prerequisite:** an ADR for strings with numbers or plurals (proposed as ADR 0025) must be accepted before T11 ships "N characters left". ADR 0014 requires it.

**JSDoc gate:** every task that declares a `@Prop`, `@Event` or `@Method` keeps JSDoc to 1–2 consumer-facing sentences, per `ai-docs/guidelines/jsdoc-template.md`.

**Wrapper parity:** the editor already ships from v1, so tasks that add editor behaviour (T9 to T11) re-check React and Vue in their own manual test. T16 is the full matrix.

---

## Files to create / modify

Paths are relative to `packages/boreal-web-components/` unless they start with `apps/`.

| File | Notes |
| --- | --- |
| `package.json`, root `pnpm-lock.yaml` | Modify — `emojibase-data` dev dependency (T2) |
| `src/components/forms/bds-emoji-picker/helpers/emojiManifest.ts` | New — generator, following `bds-flag/helpers/flagsManifest.ts` (T3) |
| `src/components/forms/bds-emoji-picker/generated/emoji-en.json`, `emoji-es.json` | New — generated, committed (T3) |
| `testing.config.ts` | Modify — exclude the generator and `generated/` from coverage (T3) |
| `src/components/forms/bds-emoji-picker/types/*` | New — T4 |
| `src/components/forms/bds-emoji-picker/utils/constants.ts` | New — `DEFAULT_EMOJI_PICKER_LABELS` (T4) |
| `src/components/forms/bds-text-editor/utils/constants.ts` | Modify — new `DEFAULT_TEXT_EDITOR_LABELS` keys (T9 to T11) |
| `ai-docs/decisions/0025-*.md` | New — ADR for strings with numbers or plurals (before T11) |
| `src/components/forms/bds-emoji-picker/helpers/emojiData.ts`, `emojiSearch.ts`, `flagSupport.ts` | New — T5 |
| `src/components/forms/bds-emoji-picker/bds-emoji-picker.tsx`, `.scss` | New — T4 to T7 |
| `src/components/forms/bds-emoji-picker/__test__/*.spec.ts` | New — T8 |
| `src/components/forms/bds-text-editor/bds-text-editor.tsx`, `types/*`, `helpers/plugins/limit.ts`, `bds-text-editor.scss` | Modify — T9 to T12 |
| `src/components/forms/bds-text-editor/__test__/*.spec.ts` | Modify — T13 |
| `apps/boreal-docs/src/stories/forms/bds-emoji-picker/*`, `forms/bds-text-editor/*` | New and modify — T15 |

---

## Progress

| Task | Status |
| --- | --- |
| T1 Design inputs: picker sign-off values and four-theme check of the editor | pending |
| T2 Add `emojibase-data` | pending |
| T3 Emoji data generator and datasets | pending |
| T4 Picker types and scaffold | pending |
| T5 Picker logic: loading, search, flag detection, selection | pending |
| T6 Picker render | pending |
| T7 Picker SCSS | pending |
| T8 Picker unit tests | pending |
| T9 Editor Emoji tool | pending |
| T10 Editor Short URL (`linkTransform`) | pending |
| T11 Editor accessibility extras (blocked until ADR 0025 is accepted) | pending |
| T12 IME composition at the limit | pending |
| T13 Editor unit tests for v2 additions | pending |
| T14 JSDoc audit (both components) | pending |
| T15 Complete stories and MDX (both components) | pending |
| T16 Full QA: browsers, React/Vue parity, screen readers | pending |
| T17 Bundle verification | pending |
| T18 Chromatic in all four brand themes | pending |
| T19 Consolidated mutation testing (v1 and v2 units) | pending |

---

### Task 1: Design inputs

**Status:** pending
**Executor:** main thread (no executor)
**Files:** this plan (values recorded under T7)

**Acceptance criteria:**

- Record the signed-off picker design: panel size, cell size, column count, tab icons, heading style, empty and error states. If the sign-off is still missing, the user decides whether T7 proceeds on tokens with the production picker as the reference.
- Pull the editor variants for the three brand themes v1 did not verify. Record any token differences for T18.
- Carried over from v1 (T7 research results): get design answers on these open points and record each one with its source node.
  - Plain frames that are Outline copies: only Default empty, Default populated and Disabled populated are specified for Plain. Confirm the intended Hover, Focus, Active and Error looks.
  - Counter colour: Figma shows it grey when the editor is populated with an error; the component shows it danger-coloured, like `bds-text-field`.
  - `max-height` of the editable: v1 uses 10 lines (about 212px), unapproved.
  - `--boreal-text-default-darker`: `#595d64` in the repo against `#131316` in Figma.
  - Text-only Fields button (`fieldsButton="text"` and `"icon-text"`): no Figma design exists; confirm the look or supply one.
- If any answer changes the component, log it as a new task in this plan.

**Manual test _(required — not waveable)_:** Non-visual task. Pass: values recorded with their sources.

**Commit:** none.

### Task 2: Add `emojibase-data`

**Status:** pending
**Executor:** main thread (no executor)
**Files:** `package.json`, `pnpm-lock.yaml`

**Acceptance criteria:**

- Re-fetch the latest version and respect `minimumReleaseAge`.
- Add it as a **dev** dependency. It is never imported at runtime.
- Frozen install, `pnpm peers check`, lockfile in the commit, and `pnpm validate:all` all pass.

**Manual test _(required — not waveable)_:** Pass: build and tests unchanged.

**Commit:** `build(deps): EOA-21589 add emojibase-data for the emoji dataset generator`

### Task 3: Emoji data generator and datasets

**Status:** pending
**Executor:** @frontend-subagent
**Files:** `helpers/emojiManifest.ts`, `generated/emoji-en.json`, `generated/emoji-es.json` (create); `testing.config.ts` (modify)

**Acceptance criteria:**

- Follow the `flagsManifest.ts` precedent: a Node script run by hand that writes committed output, with the same `eslint-disable stencil/ban-side-effects` header.
- **Input:** `emojibase-data/<locale>/compact.json` and `messages.json` for `en` and `es`.
- **Output:** groups in emojibase order, without "Component". Each group has a localised name and its emoji; each emoji has `unicode`, `label`, `tags` and `version`. No skin variants.
- The output is deterministic (byte-identical on a re-run). Record the gzipped size per file (estimate 20–35 kB).
- Exclude the generator and `generated/` from coverage, as for `generatedFlags.ts`.

**Manual test _(required — not waveable)_:** Pass: two runs produce identical files, and both parse with the expected group count.

**Commit:** `feat(web-components): EOA-21589 generate trimmed emoji datasets`

### Task 4: Picker types and scaffold

**Status:** pending
**Executor:** @frontend-subagent
**Files:** `types/IEmojiPicker.ts`, `types.ts`, `index.ts`, `utils/constants.ts`, `bds-emoji-picker.tsx` (create)

**Acceptance criteria:**

- Tag `bds-emoji-picker`, light DOM.
- Props: `locale: 'en' | 'es' = 'en'`, `labels?: EmojiPickerLabels` (JS property, reactive).
- `EmojiPickerLabels` keys: `searchPlaceholder` ("Search emoji"), `noResults` ("No emoji found"), `loadError` ("Emoji couldn't load"), `retry` ("Retry"). The defaults live in `DEFAULT_EMOJI_PICKER_LABELS: Required<EmojiPickerLabels>`, merged as in `bds-date-picker` (ADR 0014).
- Category names come from the dataset's `locale`, not from `labels`.
- Event: `bdsEmojiSelect` → `{ emoji, label }`. Method: `setFocus()`.
- Stub `<Host />`. JSDoc gate applies.
- `TextEditorLocale` in the editor's types reuses this locale type; it is not duplicated.

**Manual test _(required — not waveable)_:** Pass: the build registers the tag, and `components.d.ts` lists the API.

**Commit:** `feat(web-components): EOA-21589 scaffold bds-emoji-picker`

### Task 5: Picker logic

**Status:** pending
**Executor:** @frontend-subagent
**Files:** `helpers/emojiData.ts`, `helpers/emojiSearch.ts`, `helpers/flagSupport.ts` (create); `bds-emoji-picker.tsx` (modify)

**Utility discovery:** use `KeyboardController.setGridNavigation` and `rovingTabindex` (`src/utils/a11y/keyboard`), following `bds-calendar-grid`'s grid semantics. Use `createId`. No local arrow-key handling.

**Acceptance criteria:**

- **Loading:**
  - Dynamic `import()` of `generated/emoji-<locale>.json`, cached per locale.
  - States `loading`, `ready` and `error`, with a retry.
  - A `locale` change reloads.
- **Search:**
  - `searchEmoji(groups, query)` matches `label` and `tags`, ignoring case and diacritics (`NFD`).
  - An empty query returns `null`, meaning "show the tabs".
  - Results keep dataset order.
- **Flags:**
  - `supportsFlagEmoji()` compares a canvas drawing of 🇨🇴 with the separate regional letters.
  - Cached; no user-agent sniffing.
  - When unsupported, Flags is removed from the tabs and from results.
- **Selection and focus:** a click, `Enter` or `Space` emits `bdsEmojiSelect`. `setFocus()` focuses the search.

**Manual test _(required — not waveable)_:**

Playground: an en picker and an es picker, each logging `bdsEmojiSelect`.

- [ ] Given "heart" (en) and "corazon" or "corazón" (es), then heart emoji are listed. Pass: both locales, with and without accents.
- [ ] Given a click on an emoji, then the log shows `{ emoji, label }`. Pass: correct.
- [ ] Given the network tab, then the JSON is requested only when the picker mounts. Pass: lazy.

**Commit:** `feat(web-components): EOA-21589 add emoji picker data, search and flag detection`

### Task 6: Picker render

**Status:** pending
**Executor:** @frontend-subagent, @qa-subagent (manual test)
**Files:** `bds-emoji-picker.tsx` (modify)

**Acceptance criteria:**

- **Structure:** `bds-search-bar` (`mode="search"`, `clearable`) above a `bds-tab-group`. Each `bds-tab` has an `aria-label` on its host and an icon in its icon slot. Each `bds-tab-content` has a `bds-typography` heading and a `role="grid"` of native `<button>` cells (with `aria-label`; the glyph is `aria-hidden`).
- **Search:** an active query replaces the tabs with one results grid, or the `noResults` label. The result count is announced through `bds-search-bar`'s status region only.
- **States:** loading shows a `bds-spinner`; error shows the `loadError` label and a `bds-button` with the `retry` label. Every string comes from the merged labels.
- **Grid:** one tab stop per grid. Only one category is rendered at a time, so there is no virtualisation.

**Manual test _(required — not waveable)_:**

Playground: T5's scenarios plus a picker inside a `bds-popover`.

- [ ] Given arrow keys, `Home` and `End` in the grid, then focus moves cell by cell with one tab stop. Pass: visible focus.
- [ ] Given Chrome on Windows (or forced unsupported), then there is no Flags tab. On macOS, Flags shows. Pass: both.
- [ ] Given the JSON request blocked in DevTools, then the error and Retry show, and Retry recovers after unblocking. Pass: recovery.
- [ ] Given the popover scenario, when an emoji is picked, then the host receives `bdsEmojiSelect`. Pass: received.

**Commit:** `feat(web-components): EOA-21589 render bds-emoji-picker`

### Task 7: Picker SCSS

**Status:** pending
**Executor:** @frontend-subagent (implementation), @qa-subagent (manual test)
**Files:** `bds-emoji-picker.scss` (create)

**Figma research pass (complete before writing any SCSS):** use T1's recorded values. A row without a recorded value is marked *(pending sign-off)* and uses tokens only.

- [ ] Panel — padding, width, scroll-area max height
- [ ] Search row and tab row — spacing only (owned by `bds-search-bar` and `bds-tab-group`)
- [ ] Section heading — default
- [ ] Grid cell — default, hover, focus-visible, active
- [ ] Cell hover + focus-visible
- [ ] Empty and error states
- [ ] Dimensions — cell size and column count; grid width equals search row width

**Acceptance criteria:**

- Every row is recorded before the first SCSS line is written.
- Tokens only; no `@use` of the token package.
- Every state has a rule or a "no difference" note.
- Cells reset native button styles. `:focus-visible` shows the Boreal focus ring, and `:focus:not(:focus-visible)` shows no outline.
- The scroll area scrolls vertically only, never horizontally.
- Host styles use the `bds-emoji-picker` element selector.
- Checked against the compiled CSS.

**Manual test _(required — not waveable)_:**
- [ ] Given all four themes, then colours come from tokens. Pass: no hard-coded colours.
- [ ] Given keyboard navigation, then hover never hides the focus ring. Pass: distinguishable.

**Commit:** `style(web-components): EOA-21589 style bds-emoji-picker`

### Task 8: Picker unit tests

**Status:** pending
**Executor:** @testing-subagent
**Files:** `bds-emoji-picker/__test__/bds-emoji-picker.basics.spec.ts`, `.search.spec.ts`, `.data.spec.ts`, `.a11y.spec.ts`, `.keyboard.spec.ts` (create)

**Unit tests to cover:**

- **`basics`:** rendering and defaults; `setFocus`; `labels` defaults, partial override and reactive change.
- **`search`:** labels and tags, case and diacritics, `null` for an empty query, order, Flags excluded when unsupported.
- **`data`:** loader states, retry, per-locale cache, locale switch; flag detection with a mocked canvas.
- **`a11y`:** grid, row and cell roles and labels; `aria-hidden` glyphs; tab labels; no-results text.
- **`keyboard`:** grid moves through `KeyboardController`; `Enter` and `Space` select.
- Assert on rendered DOM. Coverage-phase only (≥ 80%); mutation testing is T19.

**Manual test:** N/A. Validated with `pnpm test` and the coverage report.

**Commit:** `test(web-components): EOA-21589 cover bds-emoji-picker`

### Task 9: Editor Emoji tool

**Status:** pending
**Executor:** @frontend-subagent, @qa-subagent (manual test)
**Files:** `bds-text-editor.tsx`, `types/ITextEditor.ts` (modify)

**Integration research pass:**
- [ ] `toolbar` parsing from v1 treats `emoji` as valid but renders nothing. It now renders the tool; no default changes (`'emoji,link'`).
- [ ] The shared v1 `insert()` path is reused unchanged.
- [ ] `bds-popover` outside-click with a nested `bds-tab-group` and `bds-search-bar`: confirm that clicks inside the picker do not close the popover.

**Acceptance criteria:**

- New prop `emojiLocale` (the picker's locale type, default `'en'`). JSDoc gate applies.
- New `TextEditorLabels` key `insertEmoji` ("Insert emoji") in `DEFAULT_TEXT_EDITOR_LABELS`.
- A `bds-button` with an icon and `disclosure`, labelled with `insertEmoji`, opens a `bds-popover` with `bds-emoji-picker`, which gets `setFocus()` on open.
- A pick inserts at the preserved cursor through `insert()`, closes the popover and refocuses the editor. `Esc` closes the popover and restores the cursor.
- The button is disabled when no space is left.

**Manual test _(required — not waveable)_:**
- [ ] Given the cursor mid-text, when an emoji is picked, then it is inserted there and focus returns. Pass: caret after the emoji.
- [ ] Given 0 characters left, then the Emoji button is disabled. Pass: disabled.
- [ ] Given the same scenario through `dev:pack:react` and `dev:pack:vue`, then the behaviour matches. Pass: no divergence.

**Commit:** `feat(web-components): EOA-21589 add emoji tool to bds-text-editor`

### Task 10: Editor Short URL (`linkTransform`)

**Status:** pending
**Executor:** @frontend-subagent, @qa-subagent (manual test)
**Files:** `bds-text-editor.tsx`, `types/ITextEditor.ts` (modify)

**Integration research pass:**
- [ ] The v1 Link flow (sanitise → too-long check → insert) is extended. The transform runs after sanitising, and the too-long check applies to the transformed URL.
- [ ] Default: without `linkTransform`, the behaviour is exactly as in v1.

**Acceptance criteria:**

- New optional JS property `linkTransform: (url: string) => Promise<string>`. JSDoc gate applies.
- While the transform is pending, the Insert button shows `loading` and further clicks are ignored.
- A rejection shows the `linkTransformError` label ("Couldn't shorten this link. Try again or insert it as is.") and a secondary button with the `insertLinkAsIs` label ("Insert as is") that inserts the sanitised original. Both keys are added to `TextEditorLabels`.
- The too-long error applies to the transformed URL.

**Manual test _(required — not waveable)_:**
- [ ] Given a transform resolving to `https://sho.rt/x` after 800 ms, then loading shows and the short URL is inserted. Pass: inserted.
- [ ] Given a rejecting transform, then the error and "Insert as is" show; "Insert as is" inserts the original. Pass: both.
- [ ] Given React and Vue (pack pipelines), then the behaviour matches. Pass: no divergence.

**Commit:** `feat(web-components): EOA-21589 add short url support to bds-text-editor`

### Task 11: Editor accessibility extras

**Status:** pending
**Executor:** @frontend-subagent, @qa-subagent (manual test)
**Files:** `bds-text-editor.tsx`, `bds-text-editor.scss` (modify)

**Acceptance criteria:**

- `Alt+F10` from the editable focuses the first enabled toolbar control, through `KeyboardController`.
- **Blocked until ADR 0025 (strings with numbers or plurals) is accepted.** Its decision sets the shape of the remaining-characters label, for example a function label `(remaining: number) => string` or an ICU-style template.
- New `TextEditorLabels` keys: `limitReached` ("Character limit reached") and the remaining-characters label in the shape ADR 0025 sets.
- A visually hidden `aria-live="polite"` region announces the remaining-characters label once when crossing to ≤ 20, and `limitReached` when an input is blocked. No per-keystroke announcements.
- Chips keep a visible border under `@media (forced-colors: active)`.

**Manual test _(required — not waveable)_:**
- [ ] Given `Alt+F10` in the text, then focus moves to the first tool. Pass: correct target.
- [ ] Given VoiceOver, when crossing 20 characters left, then the message is announced once. Pass: announced once.
- [ ] Given DevTools forced-colours emulation, then the chip border is visible. Pass: visible.

**Commit:** `feat(web-components): EOA-21589 add text editor keyboard and announcement support`

### Task 12: IME composition at the limit

**Status:** pending
**Executor:** @qa-subagent (verification), @frontend-subagent (fix if needed)
**Files:** `helpers/plugins/limit.ts` (modify only if needed)

**Acceptance criteria:**

- Compose Japanese and Chinese input (Chromium CDP `Input.imeSetComposition`, plus a real OS input method in Safari by hand) at the limit, in Chromium, Firefox and WebKit.
- If rejecting mid-composition breaks the composition, change the limit plugin: allow composition transactions, then trim to the limit at `compositionend` with an `external` transaction.
- Record the result in this task's status line.

**Manual test _(required — not waveable)_:**
- [ ] Given 2 characters left, when a 4-character Japanese word is composed, then composition completes and the text ends at the limit. Pass: no stuck composition, and the count equals the limit.

**Commit:** `fix(web-components): EOA-21589 keep ime composition working at the text editor limit` (only if changed)

### Task 13: Editor unit tests for v2 additions

**Status:** pending
**Executor:** @testing-subagent
**Files:** extend `bds-text-editor.toolbar.spec.ts`, `.a11y.spec.ts`, `.plugins.spec.ts`

**Unit tests to cover:**

- **`toolbar`:** the emoji tool renders when listed, inserts at the cursor, closes and refocuses, and is disabled at the limit. `linkTransform` success, pending loading, rejection with "Insert as is", and too-long after the transform.
- **`a11y`:** `Alt+F10` target; live-region messages at the threshold and the limit, announced once; new `labels` keys (`insertEmoji`, `linkTransformError`, `insertLinkAsIs`, `limitReached`, remaining-characters) override correctly.
- **`plugins`:** composition handling per T12's outcome.
- **v1 gap (carried over):** `\r\n` is normalised on every value path at component level. Cover the `value` prop at mount, a later `value` change, `defaultValue`, form reset, `insertText` and paste, each asserting one paragraph break per `\r\n` and the serialised `value` containing `\n` only. The serializer and plugin specs already cover parse and paste in isolation; the component-level paths have no spec.
- Coverage-phase only (≥ 80%).

**Manual test:** N/A. Validated with `pnpm test` and the coverage report.

**Commit:** `test(web-components): EOA-21589 cover text editor emoji, short url and announcements`

### Task 14: JSDoc audit (both components)

**Status:** pending
**Executor:** @frontend-subagent
**Files:** `bds-text-editor.tsx`, `bds-emoji-picker.tsx` (modify)

**Acceptance criteria:**

- Every member of both components is re-read and meets the JSDoc gate.
- The class-level JSDoc lists the `toolbar` slot.
- No version labels or ticket IDs in consumer-facing text.
- `pnpm check:cem` reflects the API.

**Manual test _(required — not waveable)_:** Pass: lint is clean, and every member has a description in `custom-elements.json`.

**Commit:** `docs(web-components): EOA-21589 audit text editor and emoji picker jsdoc`

### Task 15: Complete stories and MDX (both components)

**Status:** pending
**Executor:** @documentation-subagent
**Files:** `apps/boreal-docs/src/stories/forms/bds-text-editor/*` (modify), `apps/boreal-docs/src/stories/forms/bds-emoji-picker/*` (create)

**Acceptance criteria:**

- **Editor stories:** every Figma state, the toolbar configurations (Minimal, Extended with emoji and fields, Custom), `linkTransform`, and inside a form.
- **Editor MDX:** the full sections from the design (usage, how to use, value format, counter rules, keyboard map including `Alt+F10`, React and Vue snippets).
- **Picker:** a story and MDX for standalone use in a `bds-popover`, `bdsEmojiSelect`, locale, and a contributor note on regenerating the datasets.
- Every claim is checked against the code.

**Manual test _(required — not waveable)_:** Run `pnpm dev:docs`. Pass: renders without console errors, and the snippets are correct.

**Commit:** `docs(docs): EOA-21589 complete text editor and emoji picker docs`

### Task 16: Full QA — browsers, React/Vue parity, screen readers

**Status:** pending
**Executor:** @qa-subagent
**Files:** none

**Acceptance criteria:**

- Re-run the key scenarios of v1 (T5 and T6) and v2 (T5, T6, T9 to T12):
  - in Chromium, Firefox and WebKit, and in Safari by hand
  - through the raw component and the React and Vue **pack** pipelines
  - including a real `<form>` submit and `v-model`
- NVDA (Windows Chrome and Firefox) and VoiceOver (macOS Safari and Chrome): textbox name and description, chips, announcements, picker grid.
- `:focus-visible` checks use real `Tab` presses.
- **Carried over from v1 (not verified there):**
  - The Fields menu: the standard 3px focus ring on menu items is not clipped by the 4px list padding in Chromium, WebKit and Firefox, including with a scrolling list. `release/current` now has the `bds-dropdown` padding change from EOA-18734, so this can be checked on the real base.
  - The field chip and readonly scenarios in WebKit and Firefox, and the caret after a chip at the end of a line in Firefox.
  - A real OS or mobile IME and Safari.app (the IME part is T12).
  - React and Vue wrappers in a browser through the pack pipelines.
- Defects are logged as new tasks.

**Manual test (required):**
- [ ] Given every scenario in each surface and browser, then the behaviour matches. Pass: no divergence, or every divergence is logged.
- [ ] Given each screen reader, then the announcements match the design. Pass: all announced.

**Commit:** none.

### Task 17: Bundle verification

**Status:** pending
**Executor:** main thread (no executor)
**Files:** none

**Acceptance criteria:**

- After `pnpm build`, ProseMirror appears only in the `bds-text-editor` chunks, emoji JSON only in its own lazy chunks, and no other component's chunk grew.
- Record the gzipped sizes.

**Manual test _(required — not waveable)_:** Pass: `grep` for `EditorView` across the other chunks finds nothing, and the sizes are recorded.

**Commit:** none.

### Task 18: Chromatic in all four brand themes

**Status:** pending
**Executor:** @documentation-subagent (story theme variants), @qa-subagent (review)
**Files:** story files from T15 (modify, if theme variants are needed)

**Acceptance criteria:**

- Chromatic snapshots cover every editor state and the picker in all four brand themes, using the T1 differences.
- Visual diffs are reviewed and accepted, or logged as defects.

**Manual test _(required — not waveable)_:** Pass: the Chromatic build is approved with no unexplained diffs.

**Commit:** `docs(docs): EOA-21589 add brand theme snapshots for text editor and emoji picker` (only if stories changed)

### Task 19: Consolidated mutation testing (v1 and v2 units)

**Status:** pending
**Executor:** @testing-subagent
**Files:** one local Stryker config per unit (never pushed); existing spec files when a survivor needs a test

**Acceptance criteria:**

- Load the `mutations-testing` skill.
- Run Stryker on `serializer.ts`, `counter.ts`, `plugins/limit.ts`, `plugins/plain-paste.ts`, `emojiSearch.ts`, `bds-text-editor.tsx` and `bds-emoji-picker.tsx`.
- Score ≥ 90% per unit.
- Survivors are closed by extending the existing spec files. Record the scores.

**Manual test:** N/A. Pass: the reports show ≥ 90% per unit.

**Commit:** `test(web-components): EOA-21589 close mutation testing gaps` (only if specs changed)
