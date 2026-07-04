# BUG-001: `bds-search-bar` — duplicate loading spinner, over-broad style overrides, distorted spinner, and non-resolving width

**Severity:** Medium
**Priority:** P2
**Type:** UI / Functional
**Status:** Fixed (2026-07-03 — spinner delegated to `bds-select`, SCSS overrides narrowed, `flex-shrink` added, width resolution moved to host; verified via `testing-subagent` — 53/53 `bds-search-bar` tests, 119/119 `bds-select` tests — and live Playwright verification against Storybook)
**Component:** `bds-search-bar` (composition of `bds-select` + `bds-text-field` + `bds-button`)
**Discovered during:** QA session on Storybook `forms-search-bar--overview` (`#loading`, `#search-mode` sections) (2026-07-03)
**Affects:** All consumers of `bds-search-bar` in `mode="list"` (loading state) and any consumer relying on default/`customWidth` expansion behaviour

---

## Environment

- **Component:** `bds-search-bar` (`packages/boreal-web-components/src/components/forms/bds-search-bar/bds-search-bar.tsx`, `.scss`)
- **Related components:** `bds-select` (`packages/boreal-web-components/src/components/forms/bds-select/bds-select.tsx`, `.scss`), `bds-text-field`
- **Story:** Forms → Search Bar → Overview (Storybook), sections `Loading`, `Basic usage`, `SearchMode`
- **Browser:** Chrome (latest stable, via Playwright MCP)
- **URL:** `http://localhost:6006/?path=/docs/forms-search-bar--overview`

---

## Description

Four related layout/behaviour defects were found in `bds-search-bar`, all traced to the same underlying pattern: the component re-implements behaviour its child components (`bds-select`, `bds-text-field`) already handle correctly, instead of delegating to them. Two further defects (spinner distortion, non-resolving width) surfaced during verification of the first fix pass and share a root cause with the flex-layout changes made to address it.

---

## Steps to Reproduce

### Defect 1 — Duplicate spinner
1. Open Storybook → Forms → Search Bar → Overview → **Loading** section (`mode="list"`, `loading`, `async`, `minimized`)
2. Inspect the DOM inside `bds-select`'s `suffix` slot region while the story is in its loading window
3. Observe two spinner-related nodes: `bds-select`'s own `.bds-select__spinner` (permanently `hidden` because `bds-search-bar` never forwards `loading` to `<bds-select>`) and `bds-search-bar`'s own `.bds-search-bar__spinner`, wrapped in a `.bds-search-bar__loading` div

### Defect 2 — Unnecessary wrapper / over-broad overrides
1. Inspect `.bds-search-bar__loading` in DevTools
2. Compare against `bds-select`'s bare `<span class="bds-select__spinner">` (no wrapper) dropped directly into the already-`flex` `.bds-text-field__actions` container
3. Inspect `.bds-search-bar .bds-text-field__container` computed padding — all sides zeroed (`padding: 0px`), with a compensating `margin-right` bolted onto `.bds-text-field__actions` elsewhere in the same file

### Defect 3 — Spinner distortion
1. Open the **Loading** section and observe the visible spinner shape
2. Measure `getBoundingClientRect()` on the spinner node — width and height differ (non-circular)

### Defect 4 — Width not resolving to 100%/`customWidth`
1. Open **Basic usage** (default `bds-search-bar`, no `customWidth`) inside a wide container
2. Measure `getComputedStyle(host).width` — resolves to a fixed pixel value far short of the parent's width, instead of 100%
3. Set `customWidth="480px"` — value is still not honoured at the host level

---

## Expected Behaviour

- Exactly one spinner node exists per loading state, and it is the one actually visible.
- `bds-search-bar` delegates spinner rendering to `bds-select`'s existing `injectSuffix()` / `onLoadingChange()` mechanism whenever `bds-select` is present (`mode="list"`); it only owns a spinner itself when there is no `bds-select` to delegate to (`mode="search"`).
- Style overrides on child component internals (`.bds-text-field__container`, `.bds-text-field__actions`) touch only what is actually needed — a single-purpose `padding-left: 0` — with no compensating overrides required elsewhere.
- The spinner renders as a perfect circle regardless of its position in a flex container.
- The component's expanded width resolves to 100% of its containing block by default, and to `customWidth` when set — matching the convention already used by `bds-text-field`/`bds-select` (`width: var(--prefix-width, 100%)` resolved directly on the component's own host).

---

## Actual Behaviour

1. **Duplicate spinner:** two DOM nodes exist for one loading concept (`.bds-select__spinner[hidden]` + `.bds-search-bar__spinner`); only the search-bar-owned one is ever visible, since `loading` was never forwarded to `<bds-select>`.
2. **Unnecessary wrapper:** `.bds-search-bar__loading` duplicated centering/sizing (`height:100%; min-width:...; margin-right:...; flex-center`) that the ancestor flex container already provides, and carried a dead `--closable` sub-rule tied only to itself.
3. **Over-broad padding reset:** `.bds-text-field__container` had all padding zeroed (`padding: 0px; padding-left: 0px`) instead of only `padding-left`, requiring a compensating (and now redundant) `margin-right` on `.bds-text-field__actions`.
4. **Spinner distortion:** `.bds-select__spinner` / `.bds-search-bar__spinner` were flex items of a `display:flex` container with no `flex-shrink: 0`, so the spinner shrank from 12px to ~9.3px in width while height stayed 12px (measured via Playwright `getBoundingClientRect()`).
5. **Width not resolving:** `var(--bds-search-bar-width, 100%)` was applied on `.bds-search-bar__select--expanded`, a flex item nested inside `.bds-search-bar`'s `inline-flex` (shrink-to-fit) host. Percentages have no definite containing block in that position, so the value silently collapsed to a fixed content-based width (207px/364px observed) instead of 100% or the configured `customWidth`.

---

## Visual Evidence

Verified live via Playwright MCP against the running Storybook dev server (`http://localhost:6006`):
- Pre-fix spinner `getBoundingClientRect()`: `{ width: 9.32, height: 12 }` (distorted ellipse)
- Post-fix spinner `getBoundingClientRect()`: `{ width: 16.6, height: 16.6 }` (circle; larger due to `box-sizing: border-box` including the 2px border)
- Pre-fix default-story host width: 207–364px (observed at different points in the investigation) against a 1480px-wide parent
- Post-fix default-story host width: `1480px`, matching `parentWidth: 1480px`
- Post-fix `customWidth="480px"` story: host resolves to exactly `480px`
- Post-fix collapsed/minimized story: stays at `32px`, no `--expanded` class — confirms no regression to the compact-toolbar use case

No console errors were introduced by any of the fixes.

---

## Root Cause

- **Spinner duplication:** `bds-select` always creates its own spinner (`injectSuffix()`, `bds-select.tsx:495-515`) and toggles it via `hidden`, tied to its own `loading` `@Prop` (`onLoadingChange`, `bds-select.tsx:121-129`). `bds-search-bar` never forwarded `loading` into `<bds-select>`, so that spinner sat permanently hidden while `bds-search-bar`'s own `renderTextField()` rendered a second, independently-gated spinner.
- **Wrapper/padding overrides:** `bds-search-bar.scss` reset the entirety of `.bds-text-field__container`'s padding (sourced from the shared `form-field-shell` mixin) instead of only the left inset needed to remove space before the prefix search-icon trigger, then patched the resulting missing right-inset with a `margin-right` on `.bds-text-field__actions`.
- **Spinner distortion:** neither `.bds-select__spinner` nor `.bds-search-bar__spinner` declared `flex-shrink: 0`, so they were compressed as ordinary flex items whenever their container ran short on space.
- **Width resolution:** the CSS variable driving expanded width was applied on a nested flex item (`.bds-search-bar__select--expanded`) rather than on the component's own host element, which is `display: inline-flex` and therefore shrink-wraps to content — an ancestor with no definite width can never resolve a percentage on a descendant.

---

## Suggested Fix Direction (implemented)

1. **`bds-search-bar.tsx`** — split `renderTextField()` to take an `ownsSpinner: boolean` parameter: `mode="list"` passes `false` and forwards `loading={this.canShowLoader}` into `<bds-select>`, fully delegating to its existing mechanism; `mode="search"` passes `true` and keeps owning an unwrapped `<span slot="suffix" class="bds-search-bar__spinner" aria-hidden="true">`. Added a host-level `bds-search-bar--expanded` modifier class (`variant === 'static' || isOpen`) to `searchBarClassMap`.
2. **`bds-search-bar.scss`** — narrowed `.bds-text-field__container` override to `padding-left: 0` only; removed the now-unnecessary `margin-right` on `.bds-text-field__actions` and the dead `.bds-search-bar__loading` wrapper block (including its `--closable` sub-rule); moved `width: var(--bds-search-bar-width, 100%)` onto the new host-level `&--expanded` selector, matching the `form-field-shell` convention (`_form-field-shell.scss:9`); added `flex-shrink: 0` to `.bds-search-bar__spinner`.
3. **`bds-select.scss`** (touched with explicit authorization, after confirming it was the correct owner of the fix rather than overriding from the parent) — added `flex-shrink: 0` to `.bds-select__spinner`, matching the same distortion fix at its source.
4. **Test updates** — `bds-search-bar.basics.spec.ts` / `bds-search-bar.variants.spec.ts`: corrected two pre-existing assertions that queried a `bds-spinner` tag the component never rendered (always a `<span>`), added coverage for exactly-one-visible-spinner in both `mode="list"` and `mode="search"`, and added three tests for the new `bds-search-bar--expanded` host class (default expanded, default-minimized not expanded, `variant="static"` always expanded).

---

## Verification (post-fix)

1. **Loading story** (`mode="list"`, `loading`, `async`, `minimized`): exactly one visible spinner (`bds-select`'s own, no longer `hidden`), zero `.bds-search-bar__loading`/`.bds-search-bar__spinner` nodes in the DOM, no chevron flash when toggling `loading` via Storybook controls.
2. **Search mode** (`mode="search"`, `loading`, `async`): exactly one `.bds-search-bar__spinner`, no wrapper div, renders as a perfect circle.
3. **Padding**: `.bds-search-bar .bds-text-field__container` computed `padding-left` is `0px`; other sides retain the shared mixin's non-zero value; no visual clipping or extra gap versus a plain `bds-select` instance.
4. **Width**: default story host resolves to 100% of parent (`1480px` measured against a `1480px` parent); `customWidth="480px"` resolves to exactly `480px`; minimized/collapsed story remains `32px` with no `--expanded` class.
5. **Automated regression**: `testing-subagent` run twice — 53/53 `bds-search-bar` tests pass, 119/119 `bds-select` tests pass, no regressions.
6. **Keyboard/focus regression pass**: tab into collapsed trigger, Enter/Space to expand, type a query, Escape to clear, Escape again to collapse — unchanged (fix touched only slot content, SCSS, and a new class map key, not focus/keyboard handlers).

---

## Known Follow-ups (not fixed in this pass)

- `bds-select`'s `loadDefaultTextFieldProps()` unconditionally sets `clearable = !this.static` on the shared field, which may already override `bds-search-bar`'s own `clearable={this.canShowClear}` computation in `mode="list"` — pre-existing, unrelated to the defects above, flagged for separate investigation.
- The MDX doc's description of the loading state ("replaces the leading search icon with a `bds-spinner`") remains inaccurate — the component renders a bare styled `<span>`, not the real `<bds-spinner>` component. Left as-is pending a decision on whether to adopt `<bds-spinner>` consistently across `bds-search-bar` and `bds-select`.
- The `SearchMode` story (`mode="search"`, `minimized: true`) does not currently demonstrate the expanded/100%-width state — confirmed via Playwright that expansion works correctly once triggered (`openSearchBar()` applies `bds-search-bar--expanded` and resolves to 100% of the parent), but the static Storybook canvas only shows the collapsed icon. Candidate for a documentation-only follow-up (new story or interactive toggle), pending confirmation.

---

## Related

- Plan source: `/Users/dgonzalez/.claude/plans/i-m-seeing-some-layout-vast-crystal.md`
- Story source: `apps/boreal-docs` — Forms / Search Bar → Overview (`Loading`, `Basic usage`, `SearchMode` sections)
- Recent commits: `2460f08f`, `f4b64699`, `dbe2edd4`, `2158bd24` (`fix(web-components): EOA-14605 ...`)
