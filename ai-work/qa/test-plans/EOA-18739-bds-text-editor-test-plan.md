# Test Plan: `bds-text-editor` Component (v1)

## Context

`bds-text-editor` is a form-associated (FACE) plain-text composer. A ProseMirror editing area (schema: paragraph, text, atomic `field` chip) sits inside a Boreal shell: label, a `bds-toolbar` (built-in Fields and Link tools plus a `toolbar` slot), the editable, and a footer with helper text and a grapheme-based counter. `value` is plain text: chips are written as their `token`, line breaks as `\n`. A hard limit (`charCount`) blocks typing, truncates paste and disables Fields options that no longer fit.

This plan covers everything v1 ships (EOA-18739 T1-T9, T13, T16, plus the T10 review-readiness checks). Unit specs already cover most logic; this plan targets what a spec cannot: real browser input, caret, focus, paste, IME, painting, cross-browser and wrapper behaviour.

Component sources:

- `packages/boreal-web-components/src/components/forms/bds-text-editor/bds-text-editor.tsx`, `bds-text-editor.scss`, `helpers/`
- Specs: `.../bds-text-editor/__test__/bds-text-editor.{basics,a11y,events,form,validation,toolbar,labels,counter,plugins,serializer,insertion}.spec.ts`
- Failure modes: `ai-work/testing/failure-modes/bds-text-editor.md` (FM-TE-01 to FM-TE-14, all `confirmed`)
- Decisions: `ai-docs/decisions/0020` to `0023`; plan: `ai-work/plans/EOA-18739-bds-text-editor-v1.md`
- Docs: `apps/boreal-docs/src/stories/forms/bds-text-editor/bds-text-editor.mdx`, `bds-text-editor.stories.ts`

Brand theme in scope: **engage** for functional cases; all four themes for TC-TE-47.
Created: 2026-11-20

---

## Scope

**In scope:** form association and validation; value format and chips; plain paste and the limit (counter, truncation, line breaks, fast typing, IME); Fields tool (insert, per-option disabling, focus, caret, `fieldsButton`, `labels`); Link tool; toolbar (order, slot, dividers, visibility, edge cases); variants and states; events; accessibility; dropdown item focus ring; cross-browser; themes; Vue and React wrapper checks; Storybook docs and stories.

**Out of scope:** v2 items (emoji picker, `linkTransform`, SMS segments, IME mitigation, HTML mode); localizable validation messages (T12, use `error-message`); `bds-button` accessible-name warnings (T14); link popover arrow (T15, hidden by design in v1); focus on `reportValidity()` (T17); Chromatic visual regression; mutation testing; performance.

---

## Environment

- **Playground:** `packages/boreal-web-components/src/index.html`, one `.section` per scenario, each headed with the TC IDs it covers. Never committed. Run `fnm use && pnpm dev:components`, or the isolated recipe under "Verification". After editing the file restart the dev server (it does not re-copy `index.html`).
- **Storybook:** `pnpm dev:docs` (TC-TE-50). **Wrappers:** `pnpm run dev:pack:vue` and `dev:pack:react` from the repo root, one at a time (TC-TE-48, 49).
- **Browsers** (from `apps/boreal-docs/src/stories/welcome.mdx` § Browser Support: Chrome/Edge >= 79, Firefox >= 67, Safari >= 14, desktop only): latest Chromium, Firefox and WebKit. Safari is mandatory here: the component relies on focus rings, slotted light-DOM toolbar content, form-associated custom elements, native contenteditable and flexbox layout. Playwright WebKit is not Safari.app: report it as "WebKit" and keep real Safari.app and VoiceOver as explicit manual steps. Versions older than the latest of each engine cannot be tested here; `Intl.Segmenter` is missing in Firefox < 125 and Safari < 14.1 (see TC-TE-13).
- **Real key presses:** `:focus-visible` checks (TC-TE-43) need real `Tab`; programmatic `.focus()` and a mouse click never set it in Chromium. In WebKit and Firefox on macOS `Tab` skips buttons unless full keyboard access is on, so focus a tool with the mouse and move with arrow keys.
- **DevTools:** console open for every case (warnings are part of several expected results), Accessibility pane for TC-TE-41, Rendering panel for forced colours.
- **`bds-button` emits `bdsClick`:** never listen for `click`.

## Entry Criteria

- [ ] `pnpm build` and `pnpm test` green on `feature/EOA-18739_text-editor-v1_DG` (T10 gates: 389 suites, 5,702 tests at `248a453f`)
- [ ] Playground loads with no console errors other than the two expected "Unknown toolbar tool" warnings from the TC-TE-32 matrix
- [ ] DevTools accessibility panel available
- [ ] Real Safari.app available for TC-TE-46 (otherwise WebKit stands in and the gap is recorded)

## Exit Criteria

- [ ] All P0 cases pass in Chromium, and the TC-TE-46 set passes in WebKit and Firefox
- [ ] >= 90% of P1 cases pass; every failure has a defect or an accepted ruling
- [ ] Findings F-01 to F-05 triaged (fix, ticket or accepted)
- [ ] TC-TE-14 (IME) and TC-TE-45 (screen reader) either run or recorded as "not verified" in the PR description
- [ ] No open P0 defect

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
| ---- | ----------- | ------ | ---------- |
| Limit plugin leaves native DOM out of sync during fast typing or IME | M | H | TC-TE-10 (fast typing, compare DOM text with `value`), TC-TE-14 (hand IME) |
| Caret not drawn or editor grows when a chip ends the line (global `img { display: block }` reset hit ProseMirror's separator `<img>`) | M | H | TC-TE-17 in all three engines |
| WebKit/Firefox contenteditable quirks (placeholder blocked typing, `:active` never matches) | M | H | TC-TE-46 runs typing on an empty editor with a placeholder, pressed state and chips in all engines |
| Spurious `bdsBlur`/`bdsChange`/validation when focus moves inside the composite | H | H | TC-TE-39 with event log; FM-TE-09 |
| Light-DOM CSS: host page `p`/`img` rules reach editor internals; editor rules leak to other components | M | M | TC-TE-37 (global rules); load another form component first when checking states |
| Chip indistinguishable without background colour (forced colours) | M | M | TC-TE-44 (F-03) |
| Child events (`bds-text-field`, `bds-dropdown`) leak out of the composite and double-fire `v-model` | M | H | TC-TE-40, TC-TE-48; FM-TE-08 |
| Toolbar keyboard model differs from the documented one | M | M | TC-TE-42 (F-02) |

---

## How to read the tables

- **Pri:** P0 blocks release, P1 should pass, P2 nice to have.
- **Auto:** `Yes` = the logic is already covered by the named spec (`file.spec` > describe block); the manual case confirms it in a real browser. `No` = manual only.
- **Playground:** the `.section` id in `index.html`; the numbered `<ol>` in that section holds the exact steps and the expected result of each step. The pass criteria below are what a tester signs off.
- **Pass?** checkboxes are filled in during a run.

---

## Summary

**50 test cases:** 24 P0, 20 P1, 6 P2. 35 are backed by unit specs (logic automated, real-browser confirmation manual) and 15 are manual only (TC-TE-06, 10, 14, 17, 19, 35, 37, 43, 44, 45, 46, 47, 48, 49, 50). 10 playground scenarios cover 44 of the cases; TC-TE-46 re-runs them per engine and TC-TE-48 to 50 use the wrapper testapps and Storybook.

---

## Test Cases

### A. Form association and validation

| ID | Case and pass criteria | Pri | Auto | Playground | Pass? |
| -- | ---------------------- | --- | ---- | ---------- | ----- |
| TC-TE-01 | Required blocks submit; FormData carries the plain text. Empty + Submit is blocked and shows "This field is required. Please fill it out."; `checkValidity()` and `reportValidity()` resolve `false`; after typing Hello the submit event fires with `{"message":"Hello"}` and the error clears. (`reportValidity()` does not move focus: T17, accepted.) | P0 | Yes: `form.spec` > form value; `validation.spec` > valueMissing, checkValidity and reportValidity | `#s1-form` steps 1-3 | [ ] |
| TC-TE-02 | Reset restores `default-value` and clears the error; `<fieldset disabled>` disables editor and tools, FormData has no `message` key, and re-enabling restores it. | P0 | Yes: `form.spec` > form reset, default value, form disabled callback, form state restore | `#s1-form` steps 4, 7 | [ ] |
| TC-TE-03 | `tooLong`: an app-set value above the limit is kept in full (30 of 20, counter 30/20), `checkValidity()` is `false`, after focus and blur the footer shows "Please shorten this text to 20 characters or fewer."; typing is blocked, deleting works; reset returns to the default. | P0 | Yes: `validation.spec` > tooLong, error visibility; `form.spec` > character limit | `#s1-form` step 5 | [ ] |
| TC-TE-04 | `error-message` replaces both built-in messages; `validation-timing` `input` shows the error while typing, `submit` only after Submit, `blur` and `change` only on leaving. | P1 | Yes: `validation.spec` > validation timing, native invalid event | `#s1-form` steps 6, 8 | [ ] |

### B. Value format and chips

| ID | Case and pass criteria | Pri | Auto | Playground | Pass? |
| -- | ---------------------- | --- | ---- | ---------- | ----- |
| TC-TE-05 | Setting `value` by script: configured tokens become chips; the longest token wins (`DF-Email-Work` before `DF-Email`); an unknown token (`{{9}}`) and a token with regex characters (`[URL_Identify_Senders]`) behave (text vs chip); `\r\n` gives two lines; `null` gives an empty editor and `''`. See F-01 for the `\r\n` value read-back. | P0 | Yes: `serializer.spec` > round trip, parse structure; `form.spec` > nullish values | `#s2-value` steps 1-2 | [ ] |
| TC-TE-06 | Atomic chip: Backspace right after it removes the whole chip in one press; clicking it selects it (ring, no caret) and Backspace removes it; ArrowLeft from after it selects the chip, a second ArrowLeft puts the caret before it, ArrowRight crosses it the other way; the caret is never inside the chip. | P0 | No (`a11y.spec` > field chips only checks `contenteditable=false`) | `#s2-value` steps 3-5 | [ ] |
| TC-TE-07 | Changing `fields` after mount re-reads the value: removing the Name field turns its chip into plain `{{1}}` text without changing `value`; restoring it turns the text back into a chip. | P1 | Yes: `form.spec` > fields | `#s2-value` step 6 | [ ] |
| TC-TE-08 | A token typed by hand stays plain text and the stored value is identical to a chip's; it becomes a chip the next time the value is read in. | P2 | Yes: `serializer.spec` > round trip | `#s2-value` step 7 | [ ] |

### C. Plain paste and limit

| ID | Case and pass criteria | Pri | Auto | Playground | Pass? |
| -- | ---------------------- | --- | ---- | ---------- | ----- |
| TC-TE-09 | Typing stops at `char-count` (26 typed, 20 kept); the counter reads 20/20 only when both `counter` and `char-count` are set; the editor without `counter` shows none but still stops. | P0 | Yes: `plugins.spec` > limit plugin; `basics.spec` > footer and counter | `#s3-limit` step 1 | [ ] |
| TC-TE-10 | Fast typing at the limit: one key per task with no delay, then typing fast by hand, leaves value `abcdefghijklmnopqrst`, 20 graphemes and "DOM text matches value: true" (no stuck or duplicated text). | P0 | No (mock-doc has no real input) | `#s3-limit` step 2 | [ ] |
| TC-TE-11 | Plain paste: rich HTML (bold, italic, emoji, `<br>`) pastes as plain text; a configured token becomes a chip; two lines stay two paragraphs; in the limited editor the result is exactly 20 graphemes, ends on a whole emoji (well-formed UTF-16) and the counter reads 20/20. | P0 | Yes: `plugins.spec` > buildPasteTransaction, createPlainPastePlugin | `#s3-limit` steps 3-4 | [ ] |
| TC-TE-12 | Each line break counts as 1 and the value uses `\n` (`a`, Enter, `b` is 3/20 and `"a\nb"`). | P1 | Yes: `counter.spec` > countCharacters; `plugins.spec` | `#s3-limit` step 5 | [ ] |
| TC-TE-13 | Grapheme counting: 😀, 🇨🇴 and 👨‍👩‍👧 count 1 each (3/20). Fallback note: without `Intl.Segmenter` (Firefox < 125, Safari < 14.1) the count falls back to code points, so ZWJ families and flags count as several; the limit still holds. The fallback is unit-tested only; run it manually only on such a browser. | P1 | Yes: `counter.spec` > countGraphemes, graphemeSlice, without Intl.Segmenter | `#s3-limit` step 6 | [ ] |
| TC-TE-14 | IME composition at the limit (hand test, real IME or mobile keyboard, 18 characters typed then a multi-character composition): after commit the value never exceeds 20 and nothing is stuck or duplicated. Record engine, IME and result. Deferred from T5/T2; status pending. | P1 | No | `#s3-limit` step 7 | [ ] |

### D. Fields tool

| ID | Case and pass criteria | Pri | Auto | Playground | Pass? |
| -- | ---------------------- | --- | ---- | ---------- | ----- |
| TC-TE-15 | Insert at cursor: with the caret mid-text, choosing Name inserts the chip there, the counter rises by 20 (11 to 31), focus returns to the editor with a collapsed caret after the chip, `value` is `Hello {{1}}world`. | P0 | Yes: `toolbar.spec` > inserting a field from the Fields tool, insertField method | `#s4-fields` step 1 | [ ] |
| TC-TE-16 | Per-option disabling by space left: with 5 left Name and Identify senders are disabled and Email enabled; at 24/25 all are disabled; an option is disabled exactly when its length exceeds the space. `insertField('{{1}}')`, `insertText('xyz')` and `insertField('nope')` resolve `false`, insert nothing, and the unknown token logs one console warning. | P0 | Yes: `toolbar.spec` > Fields tool options, insertField method, insertText method; `insertion.spec` > fitsWithinLimit (FM-TE-10, FM-TE-04) | `#s4-fields` steps 2-3 | [ ] |
| TC-TE-17 | Caret visible: a blinking caret clear of the border in an empty editor; after inserting a field at the end of a line the line stays one line tall (line height before = after), the caret sits right after the chip, typing continues on the same line; script `insertField` gives the same result; a disabled editor inserts nothing. Known: Chromium draws the caret about 4px inside the chip's right edge, WebKit after it (left as is, T7). | P0 | No | `#s4-fields` steps 4-5 | [ ] |
| TC-TE-18 | Keyboard path: Shift+Tab to the Fields trigger, Enter, ArrowDown, Enter inserts the chip and returns focus to the editor with the caret after the chip; Escape on the open menu closes it and returns focus to the trigger. | P1 | Yes (partial): `events.spec` > focus returning after an insertion | `#s4-fields` step 6 | [ ] |
| TC-TE-19 | Dropdown item focus ring: each keyboard-focused item in the Fields menu shows the standard focus ring (1px white, 3px focus colour) fully visible on all sides, not clipped by the list, also in a list that scrolls. Valid only once `release/current` is merged (default 4px list padding); before that the outer ring is clipped. Repeat on WebKit and Firefox. | P1 | No | `#s4-fields` step 7 | [ ] |
| TC-TE-20 | `fields-button`: `icon` shows icon and caret; `text` shows "Fields" and caret; `icon-text` both; same size, colour and variant as the Link tool; accessible name "Insert field" in `icon`, "Fields" in the other two; runtime toggle re-renders (back to `icon` stays about 8px wider: accepted, T13); an invalid value warns and falls back to `icon`. | P1 | Yes: `toolbar.spec` > Fields button display; `a11y.spec` > toolbar (FM-TE-13) | `#s5-labels` steps 1-3 | [ ] |
| TC-TE-21 | `labels`: a partial override changes only its keys (Insert field name and the invalid-URL error in Spanish, every other string English); `labels.fields` renders as the visible text and name; a full override changes toolbar name, button names, link form strings and chip prefix ("Campo: "); reassigning `undefined` restores English. | P1 | Yes: `labels.spec` (defaults, partial overrides, every key, reactive changes) | `#s5-labels` step 4 | [ ] |

### E. Link tool

| ID | Case and pass criteria | Pri | Auto | Playground | Pass? |
| -- | ---------------------- | --- | ---- | ---------- | ----- |
| TC-TE-22 | A valid URL is inserted as plain text at the cursor (normalised, `https://example.com` becomes `https://example.com/`), the popover closes, focus returns to the editor. A schemeless `foo` is inserted as is (accepted for v1). | P0 | Yes: `toolbar.spec` > link insertion | `#s6-link` step 1 | [ ] |
| TC-TE-23 | `javascript:alert(1)` shows "Enter a valid URL" and inserts nothing; editing the URL clears the error. | P0 | Yes: `toolbar.spec` > link insertion | `#s6-link` step 2 | [ ] |
| TC-TE-24 | A URL longer than the space left shows "This link is longer than the space left." and inserts nothing; editing clears it. | P1 | Yes: `toolbar.spec` > link insertion | `#s6-link` step 3 | [ ] |
| TC-TE-25 | Enter in the URL field inserts the link and does not submit the enclosing form (no `submit` event until Submit is pressed); the URL field has no `name`, so FormData holds only `message`. | P0 | Yes: `toolbar.spec` > Enter in the URL field, link field isolation | `#s6-link` step 4 | [ ] |
| TC-TE-26 | Escape closes the popover, returns the cursor to the editor, and logs no `bdsBlur`; reopening shows an empty URL field. | P1 | Yes: `events.spec` > Escape in the link popover | `#s6-link` step 5 | [ ] |
| TC-TE-27 | Insert is disabled while the URL is empty and no error shows; the popover has no arrow. Automated only (no manual step): double submit inserts once (FM-TE-12) and submit after the editor stops being editable inserts nothing (FM-TE-06). | P2 | Yes: `toolbar.spec` > link tool, link submission after the editor stops being editable | `#s6-link` step 6 | [ ] |

### F. Toolbar

| ID | Case and pass criteria | Pri | Auto | Playground | Pass? |
| -- | ---------------------- | --- | ---- | ---------- | ----- |
| TC-TE-28 | `toolbar="fields,link"` renders Fields then Link in one group; `link,fields` reverses; slotted tools follow the built-in ones after a divider. Changing `toolbar` after the first render (`fields,\|,link`, `fields,link`, `link,\|,fields`, `link,fields`, with `readonly` toggled in between) always renders the order written, slotted tools last; judge order on screen, not from `children`. | P0 | Yes: `basics.spec` > rendering order, toolbar parsing, toolbar order after updates inside bds-toolbar | `#s7-toolbar` steps 1, 6 and matrix | [ ] |
| TC-TE-29 | Slot-only (`toolbar=""`): only the slotted tools, no divider; a slotted `bds-button` calls `insertText('Hi ')` via `bdsClick` at the cursor and `insertField('{{1}}')` inserts the chip; a tool slotted after mount makes the toolbar appear; removing the last late tool hides the toolbar (`toolbar=""`) or its divider (built-in tools), repeatably. | P0 | Yes: `basics.spec` > slotted toolbar tools added after mount, slotted toolbar tools removed after mount; `toolbar.spec` > insertText, insertField | `#s7-toolbar` steps 1-3 | [ ] |
| TC-TE-30 | Divider rules: `fields,\|,link` one divider; leading and trailing `\|` render nothing; `fields,\|,\|,link` one divider; `fields,\|` none. | P1 | Yes: `basics.spec` > toolbar parsing | `#s7-toolbar` matrix | [ ] |
| TC-TE-31 | Visibility: no toolbar for `emoji` alone, `fields` with an empty `fields` array, or nothing to show; `emoji,link` (the default) shows only Link; `readonly` hides the toolbar and slotted tools; `disabled` keeps the tools, disabled. | P0 | Yes: `basics.spec` > toolbar visibility, editable state | `#s7-toolbar` matrix, step 5; `#s8-states` step 5 | [ ] |
| TC-TE-32 | Edge cases: an unknown id (`bogus`) warns once and is ignored; a repeated tool renders once; `fields\|link` is NOT a divider (F-04): the id is unknown and no toolbar renders; toggling `readonly` or setting `toolbar` to `''`, `fields`, `null` after mount throws no error and the link popover still anchors under the Link button afterwards. | P1 | Yes: `basics.spec` > toolbar parsing, lifecycle (FM-TE-01, FM-TE-05) | `#s7-toolbar` matrix, step 5 | [ ] |

### G. Variants and states

| ID | Case and pass criteria | Pri | Auto | Playground | Pass? |
| -- | ---------------------- | --- | ---- | ---------- | ----- |
| TC-TE-33 | `outline` shows the border; `plain` hides it at rest and keeps only the toolbar's bottom line; focus shows the ring and error the danger border in both; an invalid `variant` warns and falls back to `outline`; switching at runtime is live. Compare with the Figma frames (node `14:34765`) at 100%. | P1 | Yes: `basics.spec` > variant, state classes | `#s8-states` steps 1, 7 | [ ] |
| TC-TE-34 | Hover shows the medium shadow (`0 2px 4px`, 15% ink); focus draws the ring (1px white, 3px focus) around the whole container including the toolbar, border stays grey, no outline on the editable; pressing in the editable adds the inner pressed shadow, pressing a toolbar button does not. | P0 | Yes (class only): `events.spec` > pressed state (FM-TE-14) | `#s8-states` steps 2-3 | [ ] |
| TC-TE-35 | One focus indicator at a time: the container ring shows only while focus is in the editable. With focus on a toolbar tool, in the Fields menu or in the link form, only that element's ring shows; the ring returns when focus is back in the editable (after Escape or an insertion). No extra `bdsFocus`/`bdsBlur`. | P1 | Yes (class only): `events.spec` > editing state that scopes the container focus ring | `#s8-states` steps 2, 4 | [ ] |
| TC-TE-36 | Error: danger border, `error-message` replaces helper text, `aria-invalid="true"`. Disabled: grey toolbar and editor, dimmed tools, no error styling, no `aria-invalid`. Readonly: no border, no toolbar (slotted tool hidden), text flush left, no error styling, no `aria-invalid`. A slotted tool is NOT disabled for you. | P0 | Yes: `basics.spec` > state classes, editable state; `a11y.spec` > invalid state while not editable (FM-TE-03) | `#s8-states` steps 5-6 | [ ] |
| TC-TE-37 | Page CSS isolation: after a global `p { margin: 2em; color: red }` the editor text keeps margin 0 and its own colour (label, helper and counter come from `bds-typography` and are out of scope); 14 lines grow the editable to about 10 lines then scroll inside it while the toolbar stays; `custom-width="300px"` gives a 300px editor. | P1 | No | `#s8-states` steps 8, 10 | [ ] |

### H. Events

| ID | Case and pass criteria | Pri | Auto | Playground | Pass? |
| -- | ---------------------- | --- | ---- | ---------- | ----- |
| TC-TE-38 | Typing `ab` logs `bdsFocus` once, then `bdsInput` and `valueChange` per edit; leaving logs `bdsBlur`, then `bdsChange` (only if the value changed since focus), then `bdsValidationChange`. | P0 | Yes: `events.spec` > edits, focus entering and leaving the host | `#s9-events` steps 1, 5 | [ ] |
| TC-TE-39 | No spurious events: inserting a field, inserting a link, cancelling the popover with Escape and moving between editor, toolbar, menu and popover log no `bdsBlur`, `bdsChange` or second `bdsFocus`; clicking the label logs exactly one `bdsFocus`. | P0 | Yes: `events.spec` > focus leaving without a related target, focus returning after an insertion, label and host focus (FM-TE-09) | `#s9-events` steps 2-4 | [ ] |
| TC-TE-40 | App-set values: setting `value` by script logs only `valueChange` (no `bdsInput`, no `bdsChange`); focus, set while focused, blur logs `bdsFocus`, `valueChange`, `bdsBlur`, `bdsChange`; typing in the URL field and choosing from the Fields menu emit no extra editor events (FM-TE-02, FM-TE-07, FM-TE-08). | P1 | Yes: `events.spec` > values set by the app, valueChange for values set by the app, bdsChange for values set between focus and blur; `toolbar.spec` > link field isolation | `#s9-events` steps 2, 6 | [ ] |

### I. Accessibility

| ID | Case and pass criteria | Pri | Auto | Playground | Pass? |
| -- | ---------------------- | --- | ---- | ---------- | ----- |
| TC-TE-41 | Editable has `role=textbox`, `aria-multiline=true`, `aria-labelledby` (label), `aria-describedby` (helper and counter), `aria-required`, `aria-placeholder`; toolbar has `role=toolbar` named "Text editor tools"; the Accessibility pane shows a multiline textbox named by the label; clicking the label focuses the editable; the chip reads "Field: Name". | P0 | Yes: `a11y.spec` > textbox semantics, state attributes, label interaction, toolbar, field chips | `#s10-a11y` steps 1-2 | [ ] |
| TC-TE-42 | Tab order: toolbar first (Insert field, Insert link), then the editable, then leaves; Shift+Tab reverses. ArrowLeft/ArrowRight move between tools and wrap. See F-02 for the Tab-stop count after the first arrow key. | P0 | Yes (partial): `a11y.spec` > toolbar, keyboard | `#s10-a11y` steps 3-4 | [ ] |
| TC-TE-43 | `:focus-visible` with real `Tab` presses only: each toolbar button shows only its own ring, with no container ring; the editable shows the container ring and no outline of its own. | P1 | No | `#s10-a11y` step 5 | [ ] |
| TC-TE-44 | Forced colours (`forced-colors: active`): the chip is still distinguishable from the text (visible border). Currently fails: F-03. | P2 | No | `#s10-a11y` step 6 | [ ] |
| TC-TE-45 | Screen reader pass, VoiceOver (macOS Safari and Chrome) and NVDA (Windows Firefox and Chrome): label, role, multiline, required and helper announced on entering the editable; chip read as "Field: Name"; tool names; link errors read. **Pending, not yet run.** | P1 | No | `#s10-a11y` step 7 | [ ] |

### J. Cross-browser, themes, wrappers, docs

| ID | Case and pass criteria | Pri | Auto | Playground | Pass? |
| -- | ---------------------- | --- | ---- | ---------- | ----- |
| TC-TE-46 | Cross-browser smoke in Chromium, WebKit (Safari) and Firefox: repeat TC-TE-06, 10, 11, 15, 17, 19, 22, 25, 34, 36, 42, 43. Include typing into an EMPTY editor that has a placeholder and the pressed state (both were browser-specific defects, fixed in T7). Pressed uses a `--pressed` class (no `:has()` in the editor or the shared form shell), so older Safari needs no extra check beyond the latest WebKit. Record engine and version per run. | P0 | No | all sections | [ ] |
| TC-TE-47 | Themes: connect, engage, protect and proximus recolour text, borders and ring from tokens; no hard-coded colour; chip colours come from the theme-independent extended onyx tokens (observed: identical across themes). | P2 | No | `#s8-states` step 9 | [ ] |
| TC-TE-48 | Vue (`pnpm run dev:pack:vue`, throwaway view in `examples/vue-testapp`, not committed; no text-editor scenario exists there today): `v-model` updates when typing and when the model is set; `:fields` and `:labels` as props; the model does not lag one edit behind; a native form submit carries the value. | P1 | No (`validate:pack:vue` passes; two-way verified in Chromium at T9) | none (testapp) | [ ] |
| TC-TE-49 | React (`pnpm run dev:pack:react`, throwaway component in `examples/react-testapp`): `fields` and `labels` as props, `value`, form submit and events through the wrapper. Not verified at T10. | P2 | No | none (testapp) | [ ] |
| TC-TE-50 | Storybook (`pnpm dev:docs`, restart after component changes), Forms/Text Editor: Default controls work; Readonly, Disabled, Error, WithFields, ToolbarSlot (built-in plus slot, and slot-only), CounterAndLimit, PlainVariant, FieldsButtonModes and InteractiveFormExample render with no console errors (known `bds-button` accessible-name warnings are T14); previews show Fields before Link; MDX anchors work; the MDX `toolbar="fields\|link"` divider example is wrong (F-04). | P2 | No | none (Storybook) | [ ] |

---

## Failure-mode traceability

Every FM in `ai-work/testing/failure-modes/bds-text-editor.md` maps to a case here. "Auto only" means no manual step exists.

| FM | Contract | Covered by | Manual case |
| -- | -------- | ---------- | ----------- |
| FM-TE-01 | `readonly`/`toolbar` change after mount never throws; popover re-anchors | `basics.spec` (lifecycle cases) | TC-TE-32 |
| FM-TE-02 | `valueChange` fires for app-set values, `bdsInput`/`bdsChange` do not | `events.spec` > valueChange for values set by the app | TC-TE-40 |
| FM-TE-03 | `aria-invalid` only while editable | `a11y.spec` > invalid state while not editable | TC-TE-36 |
| FM-TE-04 | `insertText('')` and non-strings resolve `false` | `toolbar.spec` > insertText method; `insertion.spec` | TC-TE-16 (limit side), otherwise Auto only |
| FM-TE-05 | Repeated and nullish `toolbar` ids | `basics.spec` > toolbar parsing | TC-TE-32 |
| FM-TE-06 | Link submit after the editor stops being editable | `toolbar.spec` > link submission after the editor stops being editable | Auto only (TC-TE-27) |
| FM-TE-07 | App-set value between focus and blur fires `bdsChange` on blur | `events.spec` > bdsChange for values set between focus and blur | TC-TE-40 |
| FM-TE-08 | Child `bds-text-field` and `bds-dropdown` events do not leak | `toolbar.spec` > link field isolation | TC-TE-40 |
| FM-TE-09 | Blur decided from a null `relatedTarget` | `events.spec` > focus leaving without a related target | TC-TE-39 |
| FM-TE-10 | Limit boundary for insertions | `toolbar.spec`, `insertion.spec` | TC-TE-16 |
| FM-TE-11 | Nullish and non-array `fields`, nullish `value` | `form.spec` > nullish values, fields | TC-TE-05, TC-TE-07 |
| FM-TE-12 | Double submit of the link form | `toolbar.spec` (double Insert) | Auto only (TC-TE-27) |
| FM-TE-13 | Runtime change of `fieldsButton`, `labels`, `fields` | `toolbar.spec`, `labels.spec` | TC-TE-20, TC-TE-21 |
| FM-TE-14 | Pointer press state | `events.spec` > pressed state | TC-TE-34 |

---

## Playground scenarios

| Section (`id`) | Heading | Cases |
| -------------- | ------- | ----- |
| `#s1-form` | TC-TE-01 - TC-TE-04 · Form association and validation | 01, 02, 03, 04 |
| `#s2-value` | TC-TE-05 - TC-TE-08 · Value format and field chips | 05, 06, 07, 08 |
| `#s3-limit` | TC-TE-09 - TC-TE-14 · Limit, counter, paste and IME | 09, 10, 11, 12, 13, 14 |
| `#s4-fields` | TC-TE-15 - TC-TE-19 · Fields tool, caret and focus | 15, 16, 17, 18, 19 |
| `#s5-labels` | TC-TE-20 - TC-TE-21 · Fields button modes and labels | 20, 21 |
| `#s6-link` | TC-TE-22 - TC-TE-27 · Link tool | 22, 23, 24, 25, 26, 27 |
| `#s7-toolbar` | TC-TE-28 - TC-TE-32 · Toolbar order, slot, dividers and visibility | 28, 29, 30, 31, 32 |
| `#s8-states` | TC-TE-33 - TC-TE-37, TC-TE-47 · Variants, states, themes and page CSS | 33, 34, 35, 36, 37, 47 |
| `#s9-events` | TC-TE-38 - TC-TE-40 · Events | 38, 39, 40 |
| `#s10-a11y` | TC-TE-41 - TC-TE-45 · Accessibility | 41, 42, 43, 44, 45 |
| (none) | TC-TE-46 cross-browser (re-run the sections above), TC-TE-48/49 wrappers, TC-TE-50 Storybook | 46, 48, 49, 50 |

---

## Regression Smoke Suite

Run after any change to `bds-text-editor`, `bds-toolbar`, `bds-button-group`, `bds-dropdown`, `bds-popover`, the shared `forms/common` or `_shared/form-field-shell`. About 15 minutes in Chromium.

| #     | Check | Case | Expected | Pass? |
| ----- | ----- | ---- | -------- | ----- |
| S-001 | Playground loads, every section renders | all | No console errors beyond the 2 expected toolbar warnings | [ ] |
| S-002 | Required form blocks, then submits plain text | TC-TE-01 | Blocked when empty; FormData `{"message":"Hello"}` | [ ] |
| S-003 | Reset restores the default | TC-TE-02 | Editor shows "Reset me" | [ ] |
| S-004 | Limit and fast typing | TC-TE-09, 10 | 20/20, DOM matches value | [ ] |
| S-005 | Rich paste is plain, token becomes chip | TC-TE-11 | No formatting, chip, 20 graphemes | [ ] |
| S-006 | Chip atomic | TC-TE-06 | One Backspace removes it | [ ] |
| S-007 | Fields insert and caret | TC-TE-15, 17 | Chip at cursor, caret after it, one line | [ ] |
| S-008 | Link valid and invalid | TC-TE-22, 23 | Inserted; "Enter a valid URL" | [ ] |
| S-009 | Enter in URL field does not submit | TC-TE-25 | No submit event | [ ] |
| S-010 | Toolbar matrix matches captions | TC-TE-28, 30, 31 | Every editor as captioned | [ ] |
| S-011 | Focus ring on whole container, real Tab | TC-TE-34, 43 | Container ring, no editable outline | [ ] |
| S-012 | Event log has no spurious blur | TC-TE-39 | No `bdsBlur` on insert | [ ] |
| S-013 | ARIA dump | TC-TE-41 | textbox, labelled, described | [ ] |
| S-014 | Same checks on WebKit and Firefox | TC-TE-46 | Identical | [ ] |

---

## Findings from plan preparation

Observed while walking the playground at `9587e06a` (Chromium, plus a WebKit spot check). Not yet logged as bug reports.

| ID | Finding | Evidence | Suggested handling |
| -- | ------- | -------- | ------------------ |
| F-01 | `value` is not normalised for `\r\n`. Docs and ADR 0021 say Windows line breaks are normalised to `\n` when the value is set; the editor shows two lines but `editor.value` and the form value keep `\r\n` until the first edit. No component spec covers it (the serializer spec covers parse only). | `editor.value = 'a\r\nb'` reads back `"a\r\nb"`; after typing `!` it reads `"a\nb!"` | Frontend decision: normalise in `onValueChange`, or fix the docs. Add a form spec. |
| F-02 | Toolbar Tab stops change with use. Before any arrow key every tool is a Tab stop (docs describe this); after the first arrow key the toolbar switches to roving tabindex (one stop, the last tool used). | Tab from "Before": Insert field, Insert link, editable. After ArrowRight/ArrowLeft: Insert field has `tabindex=0`, Insert link `-1`; Tab goes tool, editable | Decide the intended model with design/a11y (shared `bds-toolbar`), then align docs and specs. |
| F-03 | No forced-colours styling: the chip has no border, so under `forced-colors: active` it is indistinguishable from the text (screenshot confirmed). | `getComputedStyle(chip).borderTopWidth` is `0px`; no `forced-colors` rule exists anywhere in `packages/boreal-web-components/src` | Add a transparent border or outline for the chip under forced colours. TC-TE-44 stays failing until then. |
| F-04 | The MDX Toolbar section shows `toolbar="fields\|link"` as a divider example. `toolbar` splits on commas only, so the id `fields\|link` is unknown: it warns and no toolbar renders. A divider is written `fields,\|,link`. | Matrix row `fields\|link` renders no toolbar and logs `Unknown toolbar tool "fields\|link" is ignored` | Fix the snippet (docs). |
| F-05 | `reportValidity()` and a blocked submit flag the editor but leave focus where it was (same as `bds-text-field`). Already logged as T17. | `#s1-form` step 2: focus stays on the button | Accepted for v1. |

---

## Known Design Gaps and accepted behaviour (flag to team)

| Item | Details |
| ---- | ------- |
| Text-only Fields button | Has no Figma design (T13); styled by our own criteria. Mention in the PR. |
| Plain variant | Specified in Figma for 3 of 24 states; the rest are copies of Outline (T7). |
| Max height | The 10-line `max-height` needs design sign-off (T7). |
| Counter colour with `error` | Figma shows grey when populated; the component follows `bds-text-field` (T7 ruling 3). |
| `--boreal-text-default-darker` | `#595d64` in the repo against `#131316` in Figma; the editor text looks lighter than the frames (token value). |
| Link popover arrow | Hidden by design in v1 (T15). |
| Toolbar and groups share one accessible name | `labels.toolbar` (accepted). |
| Two counting rules | `bds-text-field` counts UTF-16 units, the editor counts graphemes (ADR 0022). |

---

## Test Deliverables

- This document (`ai-work/qa/test-plans/EOA-18739-bds-text-editor-test-plan.md`)
- The playground (`packages/boreal-web-components/src/index.html`, dev only, never committed)
- Bug reports per defect: `.claude/skills/qa-test-planner/scripts/create_bug_report.sh ai-work/qa`
- Update **Pass?** checkboxes inline after each run

---

## Verification (how to run)

1. **Normal:** `fnm use && pnpm dev:components`, open the served `index.html`. Restart the server after editing the file.
2. **Isolated build (when another watcher owns 3333/3334):** from the repo root run `stencil build --dev` through `.agents/scripts/with-node.sh pnpm --filter boreal-web-components exec` with a temporary config that keeps only a `www` and a `dist` target pointed at a scratch directory, copy the `www` folder, serve it with `python3 -m http.server <port>`, and stop it afterwards.
3. Walk the sections in order (A to J). Each section's `<ol>` states the expected result per step.
4. Browsers: Chromium first, then the TC-TE-46 set on WebKit and Firefox (`playwright-cli -s=<name> open <url> --browser=webkit`).
5. ARIA: DevTools > Elements > Accessibility, or the section's "Dump ARIA" button. Computed styles: DevTools > Computed (`box-shadow`, `border`, `outline`).
6. Wrappers: `pnpm run dev:pack:vue` then, separately, `pnpm run dev:pack:react`. Never run them at once.
7. Log defects:
   ```bash
   .claude/skills/qa-test-planner/scripts/create_bug_report.sh ai-work/qa
   ```
