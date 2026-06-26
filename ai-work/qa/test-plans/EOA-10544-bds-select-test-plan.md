# Test Plan: `bds-select` Component

## Context

`bds-select` is a composite form control that wraps `bds-text-field`, `bds-list-menu`, and `bds-popover` via named slots. It supports single-option selection, optional search/filter mode, form-field integration (hidden input + `name` prop), and full ARIA combobox semantics. Existing automated coverage is minimal (4 unit tests covering basic render and hidden input only), making a comprehensive manual test plan the fastest path to baseline confidence before the component ships to all brand consumers.

Figma design reference: https://www.figma.com/design/rtiE5zGA4aoOuxIQMgfD6h/-BOR--DSG-COMPONENTS-%E2%86%92-FORMS?node-id=125-11184
Figma spec frame (all states): `125:11180`
Component source: `packages/boreal-web-components/src/components/forms/bds-select/bds-select.tsx`
Brand theme in scope: **Proximus only**
Created: 2026-05-25

---

## Scope

**In scope:**

- Functional behaviour (selection, clear, search, events, form submission)
- Visual / Figma design validation (all 8 documented states)
- Accessibility / ARIA combobox semantics
- Regression smoke suite

**Out of scope:**

- Non-Proximus brand themes (Masiv, Telesign, BICS)
- Performance / load testing
- Automated e2e tests (manual execution only)
- `bds-text-field`, `bds-list-menu`, `bds-popover` internals (covered by their own plans)

---

## Environment

- Storybook: run `pnpm dev` from `apps/boreal-docs` and open the `bds-select` stories
- Browser: Chrome (latest stable)
- DevTools: open for ARIA inspection and computed-style checks
- Stories to use: `Default`, `Searchable`, `Disabled`, `Error`, `CombiningTextfieldAttributes`, `CombiningListMenuElements`, `FormIntegration`

---

## Entry Criteria

- [ ] `bds-select` stories render without console errors
- [ ] Storybook dev server running locally on the `release/current` branch
- [ ] DevTools accessibility panel available (Chrome ≥ 120)

## Exit Criteria

- [ ] All P0 test cases pass
- [ ] ≥ 90% of P1 test cases pass
- [ ] All Figma visual discrepancies documented
- [ ] All ARIA failures logged as bugs
- [ ] No open P0 bugs

---

## Risk Assessment

| Risk                                                             | Probability | Impact | Mitigation                                                                                                           |
| ---------------------------------------------------------------- | ----------- | ------ | -------------------------------------------------------------------------------------------------------------------- |
| Popover positions off-screen in small viewports                  | M           | M      | Test at 1280px and 1440px                                                                                            |
| Blur event resets field during keyboard navigation               | H           | H      | Test Tab/Escape sequences explicitly                                                                                 |
| ARIA `aria-controls` points to wrong ID after re-render          | M           | H      | Inspect DOM after each open/close cycle                                                                              |
| Search filter misses options with special chars                  | L           | M      | Include `é`, `ñ`, `&` in test data                                                                                   |
| Loading state not implemented in code                            | H           | L      | Flag as design debt if absent from stories                                                                           |
| Child events bubble up alongside host re-emissions (double-fire) | H           | H      | Use `monitorEvents` and count events per selection; `valueChange` carries different `detail` values from each source |

---

## Test Cases

### Functional

---

#### TC-FUNC-001: Default option selection

**Priority:** P0
**Story:** Default

**Preconditions:**

- [ ] Open the `Default` story (value pre-set to `option5`)
- [ ] Confirm dropdown is closed

**Steps:**

1. Observe the text field on load
   **Expected:** Field displays the label text for `option5`; hidden input has `value="option5"`

2. Click the text field
   **Expected:** Dropdown opens, `option5` is highlighted/selected in the list

3. Click a different option (e.g. `option2`)
   **Expected:** Dropdown closes; text field shows `option2` label

4. Open the Storybook **Actions panel** (bottom tab) and verify the logged entries
   **Expected:** Two entries — `bdsChange` and `valueChange` — each showing `detail: "option2"`

   > **Known behaviour (BUG-001):** Until the fix in `bds-select.tsx` is applied, the Actions panel shows **four** entries instead of two. `bds-list-menu` and `bds-text-field` are slotted into the light DOM, so their events bubble up to the host alongside `bds-select`'s own re-emissions. The second `valueChange` entry carries `detail: "Option 2"` (the display label) rather than the value key — see `ai-work/qa/bug-reports/BUG-001-bds-select-valuechange-double-fire.md`.

   <details>
   <summary>Alternative: DevTools <code>monitorEvents</code></summary>

   If the Actions panel is unavailable, select `<bds-select>` in the Elements panel (`$0`) and run in Console:

   ```javascript
   monitorEvents($0, ["bdsChange", "valueChange"]);
   ```

   Interact with the component, then run `unmonitorEvents($0)` to stop. This produces the same four entries described above, but `target` and `currentTarget` on each entry reveal which component emitted versus which was reached by bubbling.

   </details>

---

#### TC-FUNC-002: Popover open / close toggle

**Priority:** P0
**Story:** Default

**Steps:**

1. Click text field
   **Expected:** Dropdown list appears; chevron icon rotates to point up

2. Click anywhere outside the component
   **Expected:** Dropdown closes; chevron rotates back down; field retains last confirmed value

3. Click text field again, then press `Escape`
   **Expected:** Dropdown closes without changing selection

---

#### TC-FUNC-003: Clear button resets value

**Priority:** P0
**Story:** Default (with a selected value)

**Steps:**

1. Select any option to ensure a value is set
2. Click the clear (×) button on the text field
   **Expected:** Field shows placeholder; `value` prop becomes `""`; `bdsChange` fires with `""`; all list items return to visible/unselected

---

#### TC-FUNC-004: Searchable mode filters options

**Priority:** P1
**Story:** Searchable

**Steps:**

1. Click the text field to open dropdown
2. Type `"opt"` (partial match)
   **Expected:** Only options whose label or value contains `"opt"` remain visible; non-matching items are hidden

3. Clear the typed text
   **Expected:** All options become visible again

4. Type a string that matches nothing (e.g. `"zzz"`)
   **Expected:** All items hidden; list shows empty state

5. Type `"OPT"` (uppercase)
   **Expected:** Same results as step 2 (case-insensitive)

---

#### TC-FUNC-005: Searchable mode — label group visibility

**Priority:** P1
**Story:** CombiningListMenuElements

**Steps:**

1. Open searchable select with grouped options (labels as section headers)
2. Type a search term that matches an option under a specific label group
   **Expected:** The matching option AND its parent label item are visible; unrelated label groups are hidden

---

#### TC-FUNC-006: Pre-selected value via `value` prop

**Priority:** P1
**Story:** Default

**Steps:**

1. In Storybook controls, change `value` to a valid option key
   **Expected:** Text field immediately shows the label text for that option; no dropdown opens

2. Change `value` to `""`
   **Expected:** Field shows placeholder text

---

#### TC-FUNC-007: Blur resets field to confirmed value

**Priority:** P1
**Story:** Searchable

**Steps:**

1. Select an option (e.g. `option3`)
2. Click the field again and type partial text to filter
3. Press `Tab` to blur without selecting
   **Expected:** Field reverts to `option3` label text; search filter resets; focus moves into the list (dropdown stays open — Tab navigates into the listbox per Pattern 1)

---

#### TC-FUNC-008: Form integration — hidden input carries value

**Priority:** P0
**Story:** FormIntegration

**Steps:**

1. Open the `FormIntegration` story
2. Select an option from the dropdown
3. Click the form submit button
   **Expected:** Form submits with the selected option value included under the `name` key; console or network tab confirms the correct key/value pair

4. Without selecting anything, submit the form
   **Expected:** Hidden input value is `""` (empty string)

---

#### TC-FUNC-009: Disabled state blocks interaction

**Priority:** P1
**Story:** Disabled

**Steps:**

1. Attempt to click the text field
   **Expected:** Dropdown does not open; no events fired

2. Inspect the hidden input
   **Expected:** `value` matches the pre-set `option2`; field is visually styled as disabled

---

#### TC-FUNC-010: Error state display

**Priority:** P1
**Story:** Error

**Steps:**

1. Observe the component
   **Expected:** Text field renders with error styling (red border) as defined in `bds-text-field` error prop

2. Interact with the dropdown normally
   **Expected:** Error styling persists; selection still works; `bdsChange` fires correctly

---

#### TC-FUNC-011: Event emission — no double-fire per selection

**Priority:** P1
**Story:** Default

**Preconditions:**

- [ ] Open the `Default` story
- [ ] DevTools Console open

**Steps:**

1. Open the Storybook **Actions panel** (bottom tab) — clear any previous entries with the trash icon

2. Select a single option from the dropdown

3. Count the entries logged in the Actions panel
   **Expected (pass — after BUG-001 fix):** Exactly 2 entries — `bdsChange` and `valueChange` — both showing the value key (e.g. `"option2"`)
   **Expected (fail — current behaviour):** 4 entries — `bdsChange` ×2 and `valueChange` ×2; the fourth entry shows `"Option 2"` (the display label) instead of the value key

   > If the count is more than 2, this confirms **BUG-001** is open. Reference `ai-work/qa/bug-reports/BUG-001-bds-select-valuechange-double-fire.md`.

   <details>
   <summary>Alternative: DevTools <code>addEventListener</code> log</summary>

   For a precise count without Storybook, select `<bds-select>` as `$0` in the Elements panel and run:

   ```javascript
   let log = [];
   ["bdsChange", "valueChange"].forEach((n) =>
     $0.addEventListener(n, (e) =>
       log.push({ type: n, detail: e.detail, from: e.target.tagName }),
     ),
   );
   ```

   After selecting an option, run `log` to inspect the array. Expected: 2 entries. Actual (current): 4. Run `log = []` to reset between steps.

   </details>

---

### Visual / Figma Validation

Figma parent spec frame: `125:11180` — individual state nodes listed per test case.
Use DevTools **Computed** tab to inspect CSS custom property resolved values.
All tokens reference the **Proximus** theme.

---

#### TC-UI-001: Default / empty state (outline variant)

**Priority:** P1
**Figma node:** `125:11184`
**Story:** Default (clear any selection first)

| Property                      | Expected token (resolved value)                  | Actual | Pass? |
| ----------------------------- | ------------------------------------------------ | ------ | ----- |
| Background                    | `var(--ui-components-inverse, white)`            |        | [ ]   |
| Border                        | `1px solid var(--stroke-default-light, #e3e3e6)` |        | [ ]   |
| Border radius                 | `var(--radius-xs, 4px)`                          |        | [ ]   |
| Padding left                  | `var(--spacing-xs, 8px)`                         |        | [ ]   |
| Padding right / top / bottom  | `var(--spacing-1xs, 6px)`                        |        | [ ]   |
| Gap (prefix → body → options) | `var(--spacing-xs, 8px)`                         |        | [ ]   |
| Placeholder text color        | `var(--text-default-light, #8a8e96)`             |        | [ ]   |
| Placeholder font size         | `var(--typography-font-size-sm, 14px)`           |        | [ ]   |
| Placeholder font weight       | `var(--typography-font-weight-regular, 400)`     |        | [ ]   |
| Label (prefix) color          | `var(--text-default-darker, #131316)`            |        | [ ]   |
| Label font size               | `var(--typography-font-size-xs, 12px)`           |        | [ ]   |
| Label font weight             | `var(--typography-font-weight-semibold, 600)`    |        | [ ]   |
| Chevron icon size             | 20×20px                                          |        | [ ]   |
| Chevron direction             | pointing down (↓)                                |        | [ ]   |
| Drop shadow                   | none                                             |        | [ ]   |

---

#### TC-UI-002: Filled state (value selected)

**Priority:** P1
**Figma node:** `125:11336`
**Story:** Default (select any option)

| Property               | Expected token (resolved value)                                 | Actual | Pass? |
| ---------------------- | --------------------------------------------------------------- | ------ | ----- |
| Background             | `var(--ui-components-inverse, white)`                           |        | [ ]   |
| Border                 | `1px solid var(--stroke-default-light, #e3e3e6)`                |        | [ ]   |
| Drop shadow            | `drop-shadow(0px 2px 4px rgba(19,19,22,0.15))` (`Box shadow/s`) |        | [ ]   |
| Clear (×) icon visible | yes, 12×12px                                                    |        | [ ]   |
| Chevron direction      | pointing down (↓)                                               |        | [ ]   |
| Value text color       | `var(--text-default-darker, #131316)`                           |        | [ ]   |
| Value font size        | `var(--typography-font-size-sm, 14px)`                          |        | [ ]   |

---

#### TC-UI-003: Focused / typing state

**Priority:** P1
**Figma node:** `125:11412`
**Story:** Searchable (click field to focus)

| Property                | Expected token (resolved value)                 | Actual | Pass? |
| ----------------------- | ----------------------------------------------- | ------ | ----- |
| Focus ring (outer)      | `0 0 0 3px var(--stroke-focus, #9ec5ff)`        |        | [ ]   |
| Focus ring (white gap)  | `0 0 0 1px var(--ui-components-inverse, white)` |        | [ ]   |
| Text cursor             | I-beam visible                                  |        | [ ]   |
| Text color while typing | `var(--text-default-darker, #131316)`           |        | [ ]   |
| Clear (×) icon visible  | yes                                             |        | [ ]   |
| Drop shadow             | none (focus ring replaces it)                   |        | [ ]   |

---

#### TC-UI-004: Active / open state

**Priority:** P0
**Figma node:** `125:11488`
**Story:** Default (click to open)

| Property               | Expected token (resolved value)                                  | Actual | Pass? |
| ---------------------- | ---------------------------------------------------------------- | ------ | ----- |
| Focus ring             | same as TC-UI-003 (`stroke/focus, #9ec5ff`)                      |        | [ ]   |
| Inner (pressed) shadow | `inset 0 1px 2px 0 var(--depth-color-base, rgba(19,19,22,0.15))` |        | [ ]   |
| Chevron direction      | pointing up (↑)                                                  |        | [ ]   |
| Popover width          | matches trigger field width (`width="full"`)                     |        | [ ]   |
| List menu appears      | immediately below field, no visible gap                          |        | [ ]   |

---

#### TC-UI-005: Disabled state

**Priority:** P1
**Figma node:** `125:11564`
**Story:** Disabled

| Property                  | Expected token (resolved value)                  | Actual | Pass? |
| ------------------------- | ------------------------------------------------ | ------ | ----- |
| Background                | `var(--ui-components-default-lighter, #f7f7f8)`  |        | [ ]   |
| Border                    | `1px solid var(--stroke-default-light, #e3e3e6)` |        | [ ]   |
| Label (prefix) color      | `var(--text-disabled, #b6b8be)`                  |        | [ ]   |
| Value / placeholder color | `var(--text-disabled, #b6b8be)`                  |        | [ ]   |
| Chevron icon              | not rendered (Options area hidden)               |        | [ ]   |
| Clear icon                | not rendered                                     |        | [ ]   |
| Cursor on hover           | `default` or `not-allowed` (not `pointer`)       |        | [ ]   |
| Focus ring on click       | absent                                           |        | [ ]   |

---

#### TC-UI-006: Loading state

**Priority:** P2
**Figma node:** `125:11716`
**Note:** This state is specified in Figma but has no corresponding `loading` prop in `ISelect.ts` or Storybook story. Flag as design debt if absent.

| Property                    | Expected token (resolved value)          | Actual | Pass? |
| --------------------------- | ---------------------------------------- | ------ | ----- |
| Background                  | `var(--ui-components-disabled, #f7f7f8)` |        | [ ]   |
| Label color                 | `var(--text-disabled, #b6b8be)`          |        | [ ]   |
| Chevron replaced by spinner | 16×16px loading indicator                |        | [ ]   |
| Interaction                 | blocked (no click-to-open)               |        | [ ]   |

---

#### TC-UI-007: Error state

**Priority:** P0
**Figma node:** `125:11870`
**Story:** Error

| Property                        | Expected token (resolved value)                      | Actual | Pass? |
| ------------------------------- | ---------------------------------------------------- | ------ | ----- |
| Border                          | `1px solid var(--stroke-danger-base, #c7242b)` (red) |        | [ ]   |
| Background                      | `var(--ui-components-inverse, white)` (unchanged)    |        | [ ]   |
| Helper text visible below field | yes                                                  |        | [ ]   |
| Helper text color               | `var(--text-danger-base, #c7242b)`                   |        | [ ]   |
| Helper text font size           | `var(--typography-font-size-xs, 12px)` Regular       |        | [ ]   |
| Char counter color              | `var(--text-danger-base, #c7242b)` right-aligned     |        | [ ]   |
| Layout shift vs default         | none (same field height; footer row added below)     |        | [ ]   |

---

#### TC-UI-008: Plain variant (no border)

**Priority:** P2
**Figma node:** `125:12024`
**How to set up:** `bds-select` has no `variant` prop. The plain appearance is controlled by setting `variant="plain"` on the `bds-text-field` placed in the `field` slot. `bds-text-field` applies `bds-text-field--plain` via its `classMap` getter (`bds-text-field.tsx:439`) which removes the border at rest.

| Property      | Expected                                                | Actual | Pass? |
| ------------- | ------------------------------------------------------- | ------ | ----- |
| Border        | absent at rest (`bds-text-field--plain` removes border) |        | [ ]   |
| Background    | `var(--ui-components-inverse, white)`                   |        | [ ]   |
| Padding / gap | same as outline variant                                 |        | [ ]   |
| Chevron       | present, same size / direction                          |        | [ ]   |

---

#### TC-UI-009: Badge counter (anatomy item 7)

**Priority:** P1
**Figma node:** `125:11038` (anatomy diagram, item 7 — `Badge/Default`)
**Note:** The Figma anatomy specifies a `bds-badge variant="default"` positioned **between** the body text and the disclosure chevron. This badge is not currently rendered in `bds-select.tsx` — it is a **design gap**. This test case should be executed once the badge is implemented.

**Expected implementation:** A `<bds-badge>` element rendered inside the field row, between `valueType/Body` and the `Options` container, showing a numeric counter value.

| Property                                      | Expected token (resolved value)                | Actual | Pass? |
| --------------------------------------------- | ---------------------------------------------- | ------ | ----- |
| Badge visible in field                        | yes, between body text and chevron             |        | [ ]   |
| Badge background                              | `var(--ui-components-base-light, #e3e3e6)`     |        | [ ]   |
| Badge text color                              | `var(--text-base, #272a2f)`                    |        | [ ]   |
| Badge font size                               | `var(--typography-font-size-xs, 12px)` Regular |        | [ ]   |
| Badge size                                    | min 20×20px                                    |        | [ ]   |
| Badge border radius                           | `var(--radius-xs, 4px)`                        |        | [ ]   |
| Badge `variant` prop                          | `"default"`                                    |        | [ ]   |
| Badge `disabled` prop when select is disabled | `true`                                         |        | [ ]   |

---

#### TC-UI-010: Required label indicator

**Priority:** P2
**Story:** CombiningTextfieldAttributes

- [ ] Required asterisk `*` color: `var(--text-danger-base, #c7242b)`
- [ ] Asterisk placed immediately after label text with gap `var(--spacing-3xs, 2px)`

---

---

### Accessibility (ARIA)

Use DevTools → Accessibility panel or axe DevTools extension.

---

#### TC-ACC-001: Combobox role on input

**Priority:** P0

**Steps:**

1. Open the `Default` story
2. Inspect the `<input>` element inside `bds-text-field`
3. Verify attributes:
   - [ ] `role="combobox"`
   - [ ] `aria-haspopup="listbox"`
   - [ ] `aria-expanded="false"` (closed state)
   - [ ] `aria-autocomplete="none"` (non-searchable mode)
   - [ ] `aria-controls="bds-select-list-[id]"` pointing to the list menu element

---

#### TC-ACC-002: aria-expanded updates on open/close

**Priority:** P0

**Steps:**

1. Confirm `aria-expanded="false"` before opening
2. Click field to open dropdown
   **Expected:** `aria-expanded="true"` on the `<input>` AND on the `<bds-select>` host element
3. Close dropdown
   **Expected:** Both reset to `aria-expanded="false"`

---

#### TC-ACC-003: List menu role

**Priority:** P0

**Steps:**

1. Open dropdown and inspect `bds-list-menu`
   **Expected:** `menu-role` attribute / rendered `role="listbox"` on the list container
2. Inspect `bds-list-menu` element for `id` attribute
   **Expected:** `id` matches the value in `aria-controls` from TC-ACC-001

---

#### TC-ACC-004: Searchable mode ARIA autocomplete

**Priority:** P1
**Story:** Searchable

**Steps:**

1. Inspect the `<input>` element
   **Expected:** `aria-autocomplete="list"` (not `"none"`)

---

#### TC-ACC-005: Keyboard navigation — open and close

**Priority:** P1

**Steps:**

1. Tab to the select field
   **Expected:** Focus ring visible on text field input
2. Press `Enter` or `Space`
   **Expected:** Dropdown opens; `aria-expanded="true"`
3. Press `Escape`
   **Expected:** Dropdown closes; focus returns to input
4. Press `Tab` while dropdown is open
   **Expected:** Focus moves to the first focusable item inside the list; dropdown stays open (Pattern 1 — Tab navigates into the listbox, not past the component)

---

#### TC-ACC-006: Keyboard navigation — option selection

**Priority:** P1

**Steps:**

1. Open dropdown via keyboard
2. Press `ArrowDown` twice
   **Expected:** Second option is visually focused
3. Press `Enter`
   **Expected:** Option selected; dropdown closes; `bdsChange` fires; field shows selected label

---

### Regression Smoke Suite

Run after any change to `bds-select.tsx`, `bds-text-field`, `bds-list-menu`, or `bds-popover`.

| #     | Check                                    | Story           | Expected                        | Pass? |
| ----- | ---------------------------------------- | --------------- | ------------------------------- | ----- |
| S-001 | Component renders without console errors | Default         | No errors in DevTools console   | [ ]   |
| S-002 | Selecting an option updates field text   | Default         | Label text shown after click    | [ ]   |
| S-003 | Clearing resets to placeholder           | Default         | Placeholder visible after clear | [ ]   |
| S-004 | Searchable mode filters list             | Searchable      | Options hide on typed input     | [ ]   |
| S-005 | Disabled state blocks click              | Disabled        | Dropdown stays closed           | [ ]   |
| S-006 | Form submit includes value               | FormIntegration | Correct key/value in submit     | [ ]   |
| S-007 | aria-expanded toggles correctly          | Default         | Attribute changes on open/close | [ ]   |

---

## Known Design Gaps (flag to team)

| Gap                    | Details                                                                                                                                                                                                                                            |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Badge counter**      | Anatomy item 7 in Figma (`125:11038`) specifies a `bds-badge variant="default"` between body text and chevron, showing a numeric count. `bds-select.tsx` renders no badge element — the prop, rendering logic, and Storybook story are all absent. |
| **Loading state**      | Designed in Figma (`125:11716`) but no `loading` prop in `ISelect.ts` or Storybook story.                                                                                                                                                          |
| **Plain variant path** | `bds-select` has no `variant` prop. Plain appearance requires setting `variant="plain"` on the slotted `bds-text-field` directly — this is not documented in Storybook or the component's JSDoc.                                                   |

---

## Test Deliverables

- This document (`ai-work/qa/bds-select-test-plan.md`)
- Bug reports per defect: `create_bug_report.sh ai-work/qa`
- Update **Pass?** checkboxes inline after each test run

---

## Verification (how to run)

1. **Start Storybook:**
   ```bash
   fnm use && pnpm dev --filter boreal-docs
   ```
2. Open `http://localhost:6006` → Forms → bds-select
3. Execute test cases in order: Functional → Visual → Accessibility → Regression
4. ARIA inspection: DevTools → Elements → Accessibility tab (or axe DevTools extension)
5. Computed styles: DevTools → Elements → Computed tab, filter by `padding`, `border`, `color`, `box-shadow`
6. Log defects:
   ```bash
   .claude/skills/qa-test-planner/scripts/create_bug_report.sh ai-work/qa
   ```
