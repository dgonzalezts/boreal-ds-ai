# Failure-Mode Catalog — `bds-search-bar`

Audited against `packages/boreal-web-components/src/components/forms/bds-search-bar/` as of 2026-10-26 (branch `fix/EOA-19598-search-bar-virtual-scroll-feature_DG`, HEAD `1e6e0f54`, after Tasks 9–14 of `EOA-19597` added the `items` mode). Rows are derived from reading `bds-search-bar.tsx`, `helpers/ItemsNavigationController.ts`, `helpers/navigationIndex.ts`, `bds-search-bar.scss` and the pre-existing spec suite — not from the plan's stated test list.

Scope of this first audit: the `items` mode added by EOA-19597 (windowing, data-side filtering, label/typing model, live region, keyboard) plus the slotted-mode invariants the new code touches. Pre-existing uncovered paths (`waitForSelectWidthTransition`, `expandInstantly` timing, loader/suffix behaviour) are exercised by the existing suite and were read only for cross-checking.

Rows marked `pending-decision` have no test; they are reported to the user and must be ruled on before any test or source change lands.

Second pass, same day, for T43 (the Vue `v-model` parity fix): audited `applyQuery`'s commit path and added FM-21 (confirmed by the user's option-A ruling) plus PD-04 (still open — the pick and clear emitters are not equality-guarded).

Third pass, same day, for the ten behaviour fixes landed under T22/T24/T29/T32/T34/T35/T40/T45/T46/T47: added FM-22…FM-29 for the fixed contracts, closed PD-03 (T32: warn once, never de-duplicate) and PD-04 (T47: picks and clears always emit, documented in the event JSDoc) by user ruling, and opened PD-05 and PD-06 for two behaviours the fixes left ambiguous (a clear's extra `bdsSearch`, and `aria-controls` picking the hidden slotted list when `items` wins).

Fourth pass, same day: both rows were ruled on. PD-05 — a clear must not reach the pick path, so one interaction emits one event of each clear name and no `bdsSearch`; the `.agents` clear-name set is `bdsClear` + `bdsInput` + `valueChange`, with a pick unchanged. PD-06 — `listboxEl` resolves by mode, so `items` wins and `aria-controls` targets the active items listbox even when a slotted list is the first DOM match. Both rows are now `confirmed` and covered by the regression specs cited below.

Fifth pass, same day, for T51 (the same-frame keystroke lost after a mouse pick): added FM-33 for the synchronous picked-field application (`applyPickedFieldText()` plus the `isApplyingPickedFocus` guard on `selectCommittedText()`), `confirmed` against the plan's stated fix and the frontend headless-Chrome verification. No `pending-decision` rows opened; the fixture limits of asserting a caret selection in mock-doc are recorded inside the row.

Sixth pass, 2026-10-28, for the `items`-change scroll fix on `fix/EOA-19598-search-bar-virtual-scroll-feature_DG`: `onItemsChange` now receives `(next, previous)` and only calls `resetItemsScroll()` when the first entry's `value` changed. Added FM-34 (append keeps the scroll and the window) and FM-35 (prepend, replacement, first assignment and post-empty assignment still reset; leaving items mode never resets). Both `confirmed` against the user-supplied contract for this fix; no `pending-decision` rows opened.

Seventh pass, 2026-10-28, for the stale live-region fix on the same branch: `onValueChange` clears `resultsAnnouncement` before reconciling the filter for an external `items`-mode assignment, and `onItemsChange` clears it when items mode ends and when an update arrives with no active query. Added FM-36 (external writes never announce and never leave a stale count), FM-37 (an items update with no query clears the region) and FM-38 (leaving items mode clears it before the region can remount), all `confirmed` against the user-supplied contract; the previously `confirmed` FM-30 contract already required the silent external reconcile, and its one stale spec (asserting `11 results` after `el.value = ''`) has been corrected. Two adjacent behaviours the fix does not settle are opened as PD-07 (a `mode` toggle remounts the region with the previous text) and PD-08 (`itemsQuery` survives leaving items mode, so a return can resurrect a filter the field no longer shows); neither has a test.

Eighth pass, 2026-10-28, for the pick-after-`items`-toggle fix on the same branch: `handleSelectChange` now accepts a `bdsChange` whose target is the `bds-select` host **or** the component's own rendered `.bds-search-bar__list`, and closes the popover only for the own-list origin. The select binds its list listener once in `componentDidLoad`, so a list re-created by an `items` toggle bubbles its pick past the select and was being discarded by the old `e.target === e.currentTarget` guard. Added FM-39 (the rebuilt-list pick commits, announces and focuses), FM-40 (close ownership per origin, once each), FM-41 (the widened guard still rejects the text field's echo and a consumer list's own bubbled event) and FM-42 (a detail-less deselection commits `''`), all `confirmed` against the user-supplied contract. Verified by reverting the guard to HEAD bytes: FM-39 (both the pick and the `bdsClose` case) and FM-42 fail; FM-40 and FM-41 pass in both worlds — the select consumes the consumer list's raw event and re-emits its own `bdsChange`, and the text field's echo is stopped at the field — so they are recorded as anti-over-acceptance locks rather than reproductions. No `pending-decision` rows opened.

---

### FM-01 | `undefined` and `[]` select different modes

- **ID:** FM-01
- **Category:** null-empty
- **Risk:** functional — a consumer cannot express "items mode with no suggestions" if `[]` fell back to slotted mode; the empty state would never render.
- **Input that reveals it:** `items` omitted vs `items={[]}`.
- **Observed current behavior:** `isItemsMode` is `this.items !== undefined && mode !== 'search'` (`bds-search-bar.tsx:783-785`); with `[]` the internal list renders with `empty` true, with `undefined` the `slot="list"` path renders instead (`render()` line 983).
- **Recommended contract:** `undefined` = slotted mode; `[]` = items mode showing the list's empty state.
- **Contract status:** confirmed
- **Why it matters:** it is the documented prop contract (prop JSDoc, plan T8).
- **Covered by:** `src/components/forms/bds-search-bar/__test__/bds-search-bar.items.spec.ts::Should treat undefined items as slotted mode`; `…items.spec.ts::Should treat an empty items array as items mode showing the empty state`

---

### FM-02 | `items` combined with `mode="search"` renders nothing

- **ID:** FM-02
- **Category:** component-contract-bypass
- **Risk:** functional — `mode="search"` renders no list at all, so an accepted `items` prop would silently never appear.
- **Input that reveals it:** `items` set together with `mode="search"`.
- **Observed current behavior:** `isItemsMode` excludes search mode, `render()` emits no `bds-select`/list, and `warnItemsPrecedence()` logs one warning per instance (`bds-search-bar.tsx:437-450`).
- **Recommended contract:** `items` is ignored in `mode="search"` with exactly one warning per instance.
- **Contract status:** confirmed
- **Why it matters:** silent configuration mismatch is the failure the warning exists to prevent; duplicate warnings are noise.
- **Covered by:** `…items.spec.ts::Should ignore items in mode="search" and warn once`; `…items.spec.ts::Should warn only once about mode="search" across further renders`

---

### FM-03 | `items` and a consumer `slot="list"` both present

- **ID:** FM-03
- **Category:** equivalence
- **Risk:** functional/visual — two lists could be rendered or the wrong one used, and the consumer would not know which source is live.
- **Input that reveals it:** `items` plus a `<bds-list-menu slot="list">` child.
- **Observed current behavior:** the internal `.bds-search-bar__list` is rendered inside the select, `hasSlottedList` detects the consumer list, one warning is logged, and the SCSS hides the stale slotted element (`bds-search-bar.scss:113-116`).
- **Recommended contract:** `items` wins; the select contains exactly one list; warn once.
- **Contract status:** confirmed
- **Why it matters:** precedence must be unambiguous and announced.
- **Covered by:** `…items.spec.ts::Should prefer items over consumer slot="list" children and warn once`

---

### FM-04 | The window renders more than the visible entries

- **ID:** FM-04
- **Category:** boundary
- **Risk:** performance — the whole point of `items` is a bounded mounted element count; an unbounded window reintroduces the original bug.
- **Input that reveals it:** 1,000 entries with a 200 px list viewport.
- **Observed current behavior:** `VirtualWindow` is created with `count = filteredItems.length`, `estimateSize` 28 and overscan 5 (`bds-search-bar.tsx:452-471`); 13 items mount for 1,000 entries.
- **Recommended contract:** only the window plus overscan mounts, and the count stays bounded while scrolling.
- **Contract status:** confirmed
- **Why it matters:** the defect this plan fixes is 1,000 live custom elements.
- **Covered by:** `…items.spec.ts::Should mount only the visible window of a 1,000 entry list`; `…items.spec.ts::Should move the window and resize the spacers when the list scrolls`

---

### FM-05 | Spacers do not represent the skipped entries

- **ID:** FM-05
- **Category:** boundary
- **Risk:** visual — wrong leading/trailing heights make the scrollbar and scroll position lie, and the list jumps.
- **Input that reveals it:** windowed list at the top and after scrolling.
- **Observed current behavior:** leading = first item `start`, trailing = total − last `end` (`virtual-window.ts:26-41`), written as inline heights on the two spacer divs (`bds-search-bar.tsx:506-535`).
- **Recommended contract:** top height = leading size, bottom height = trailing size; both decorative.
- **Contract status:** confirmed
- **Why it matters:** spacers are the only thing preserving the total scroll height.
- **Covered by:** `…items.spec.ts::Should place the window between two aria-hidden spacers sized to the skipped entries`; `…items.spec.ts::Should render every suggestion when the list is shorter than the window`; `…a11y.spec.ts::Should mark both window spacers as decorative`

---

### FM-06 | Mounted suggestions report the wrong set size or position

- **ID:** FM-06
- **Category:** a11y
- **Risk:** a11y — screen readers announce "1 of 13" instead of "1 of 1000", or numbering restarts inside the window.
- **Input that reveals it:** 1,000 entries; then a query that narrows the list; then a scroll.
- **Observed current behavior:** `aria-setsize` is the filtered count and `aria-posinset` the absolute index + 1, set on each mounted `bds-list-menu-item` (`bds-search-bar.tsx:517-527`).
- **Recommended contract:** `aria-setsize` = filtered count, `aria-posinset` = absolute index + 1, both stable across scrolling.
- **Contract status:** confirmed
- **Why it matters:** it is the only position information assistive tech can read from a windowed listbox.
- **Covered by:** `…a11y.spec.ts::Should expose the filtered count and absolute position on every mounted suggestion`; `…a11y.spec.ts::Should keep the position of a suggestion absolute after the window scrolls`

---

### FM-07 | Filtering diverges from the slotted rule

- **ID:** FM-07
- **Category:** equivalence
- **Risk:** functional — items mode and slotted mode would match different suggestions for the same query.
- **Input that reveals it:** a mixed-case query matching a label only, and a query matching a value only.
- **Observed current behavior:** `itemsQuery` lowercased and matched against `label` **or** `value` (`bds-search-bar.tsx:791-805`), the same rule `searchOwnData` applies to slotted children (`bds-search-bar.tsx:313-332`).
- **Recommended contract:** case-insensitive match on label or value in both modes.
- **Contract status:** confirmed
- **Why it matters:** documented equivalence in T10/T13 result notes.
- **Covered by:** `…basics.spec.ts::Should filter the items case-insensitively on the label`; `…basics.spec.ts::Should filter the items case-insensitively on the value`; `…basics.spec.ts::Should keep filtering the slotted list through searchOwnData`

---

### FM-08 | Data filtering is bypassed or applied to the DOM in items mode

- **ID:** FM-08
- **Category:** component-contract-bypass
- **Risk:** functional/performance — DOM filtering cannot see unmounted entries, so only the window would filter.
- **Input that reveals it:** typing a query in items mode.
- **Observed current behavior:** `applyQuery` calls `applyItemsQuery` (data-side) when `isItemsMode`, and `searchOwnData` only in slotted mode (`bds-search-bar.tsx:270-278`).
- **Recommended contract:** `searchOwnData` never runs in items mode; filtering always uses the `items` array.
- **Contract status:** confirmed
- **Why it matters:** the whole architecture of `items` depends on it.
- **Covered by:** `…basics.spec.ts::Should filter from the items data instead of the DOM in items mode`

---

### FM-09 | The filtered list is recomputed on every render

- **ID:** FM-09
- **Category:** race-timing
- **Risk:** performance — an O(n) filter per render on a thousand-entry list, on every unrelated state change.
- **Input that reveals it:** an active query, then an unrelated render (e.g. `loading`).
- **Observed current behavior:** `filteredItems` caches on the `items` reference and query (`bds-search-bar.tsx:791-805`), `selectedSuggestion` caches on `items` and `value` (`842-851`).
- **Recommended contract:** the cached array/object is reused when neither input changed, replaced when either does.
- **Contract status:** confirmed
- **Why it matters:** the project requires a dedicated test for render-time memoization, not just output correctness.
- **Covered by:** `…items.spec.ts::Should memoize the filtered list until items or the query change`

---

### FM-10 | The live region announces stale or malformed counts

- **ID:** FM-10
- **Category:** a11y
- **Risk:** a11y — a polite region that announces on first paint, never announces, or says "1 results".
- **Input that reveals it:** first render; a query with 11 / 1 / 0 matches; replacing `items` while a query is active.
- **Observed current behavior:** `resultsAnnouncement` starts `''` (`bds-search-bar.tsx:158`), is written by `announceItemsCount()` with singular/plural handling (`298-302`), and re-run from `onItemsChange` when `itemsQuery !== ''` (`214-221`).
- **Recommended contract:** empty on first render; "N results"/"1 result"/"0 results" after a query change; re-announced when `items` changes under an active query.
- **Contract status:** confirmed
- **Why it matters:** it is the only feedback a screen-reader user gets for a filter that runs off-screen.
- **Covered by:** `…a11y.spec.ts::Should render an empty polite live region on the first render`; `…a11y.spec.ts::Should announce the plural result count after a query narrows the list`; `…a11y.spec.ts::Should announce a single result in the singular form`; `…a11y.spec.ts::Should announce zero results when no suggestion matches`; `…items.spec.ts::Should reset the scroll, the mounted window and the count when the items dataset is replaced during a query`; `…items.spec.ts::Should keep the scroll and the mounted window and announce the new count when an entry is appended during a query`

---

### FM-11 | A re-render overwrites the text the user is typing

- **ID:** FM-11
- **Category:** race-timing
- **Risk:** visual — a keystroke is swallowed or the caret jumps while typing over a committed label.
- **Input that reveals it:** `value` set to a labelled entry, then typing.
- **Observed current behavior:** `typedText` holds the raw keystroke text and `fieldText` returns it verbatim while non-null (`bds-search-bar.tsx:859-863`); the debounced commit of the same text leaves the override in place (watcher guard at `209-213`).
- **Recommended contract:** while typing the field shows exactly the typed string, including after the debounced commit of that same string.
- **Contract status:** confirmed
- **Why it matters:** T12 option B exists precisely to remove this defect.
- **Covered by:** `…events.spec.ts::Should render exactly the typed text over a committed label`; `…events.spec.ts::Should keep the typed text when the debounced query commits that same text`

---

### FM-12 | The committed value shows the raw value instead of its label

- **ID:** FM-12
- **Category:** functional
- **Risk:** visual — a consumer sees internal ids (`item-900`) instead of human labels.
- **Input that reveals it:** programmatic `value` for an entry outside the mounted window.
- **Observed current behavior:** `selectedSuggestion` resolves from the full `items` array, and `bds-select.loadValue` returns early when the option is unmounted (`bds-select.tsx:766-780`), so the search bar is the only label source (`bds-search-bar.tsx:842-863`).
- **Recommended contract:** the field always shows the label of a committed `value` that matches an entry, mounted or not; free text shows as typed.
- **Contract status:** confirmed
- **Why it matters:** windowing must not make label resolution window-dependent.
- **Covered by:** `…events.spec.ts::Should show the label of a programmatic value resolved from the full items list`; `…events.spec.ts::Should show free text as typed when the value matches no suggestion`; `…events.spec.ts::Should emit bdsSearch and valueChange with the picked entry value and show its label`

---

### FM-13 | The typing override survives a genuinely different committed value

- **ID:** FM-13
- **Category:** race-timing
- **Risk:** visual — an external `value` (e.g. a chip click or a `v-model` write) is invisible because the old typed text stays on screen.
- **Input that reveals it:** typing, then assigning a different `value`.
- **Observed current behavior:** `onValueChange` keeps `typedText` only when `typedText === next`, otherwise clears it (`bds-search-bar.tsx:209-213`).
- **Recommended contract:** the override is kept only for the commit of the same text.
- **Contract status:** confirmed
- **Why it matters:** this replaced the removed `skipNextValueSync` guard.
- **Covered by:** `…events.spec.ts::Should keep the typing override only while the committed value matches it`

---

### FM-14 | A pending query outlives the interaction that ended editing

- **ID:** FM-14
- **Category:** race-timing
- **Risk:** functional — an uncommitted debounce fires later and overwrites the value committed by a pick, or the field and `value` disagree after blur / popover close.
- **Input that reveals it:** type without waiting for the debounce, then pick / blur / close the popover.
- **Observed current behavior:** `handleSelectChange` cancels the debounce and clears the override (`bds-search-bar.tsx:544-552`); `handleBlur` and `handlePopoverClose` call `commitTypedQuery()` and drop the override (`413-435`, `280-285`).
- **Recommended contract:** a pick wins over a pending query; blur and popover close commit (not discard) a pending query exactly once.
- **Contract status:** confirmed
- **Why it matters:** it is the T10b/T12 root cause class.
- **Covered by:** `…events.spec.ts::Should not overwrite a pick with the query that was still pending`; `…events.spec.ts::Should commit a pending query on blur`; `…events.spec.ts::Should commit a pending query when the suggestions popover closes`

---

### FM-15 | Escape leaves a pending query behind or the native clear re-enters the component

- **ID:** FM-15
- **Category:** component-contract-bypass
- **Risk:** functional — a trusted native `type="search"` Escape fires an `input` event that re-pins the override and duplicates `bdsInput ""`/`valueChange ""` (T12 note).
- **Input that reveals it:** a pending (uncommitted) query, then Escape.
- **Observed current behavior:** `listenKeydown` calls `stopPropagation()`, `preventDefault()`, closes the popover and clears when `value !== ''` **or** `typedText !== null` (`bds-search-bar.tsx:359-374`).
- **Recommended contract:** Escape clears the pending query, clears the field, and prevents the native default.
- **Contract status:** confirmed
- **Why it matters:** documented in T12's implementation notes as a real double-emission fix.
- **Covered by:** `…events.spec.ts::Should clear the pending query on Escape and prevent the native default`

---

### FM-16 | Keyboard navigation cannot leave the mounted window

- **ID:** FM-16
- **Category:** component-contract-bypass
- **Risk:** a11y — the shared list navigation only sees mounted items, so a windowed list becomes unreachable past the first ~13 entries.
- **Input that reveals it:** ArrowDown/ArrowUp/Home/End/PageUp/PageDown over a 1,000-entry list, including window edges and wraparound.
- **Observed current behavior:** `ItemsNavigationController` intercepts the six keys on the host, computes targets over the filtered array (`navigationIndex.ts`), scrolls the window and focuses the mounted target (`ItemsNavigationController.ts:155-238`); disabled entries are skipped by index.
- **Recommended contract:** navigation spans the whole filtered list, wraps at the ends, skips disabled entries, and works across window boundaries.
- **Contract status:** confirmed
- **Why it matters:** T11's raison d'être.
- **Covered by:** `…keyboard.spec.ts::Should move focus past the mounted window and scroll the list`; `…keyboard.spec.ts::Should wrap from the last entry to the first on ArrowDown`; `…keyboard.spec.ts::Should wrap from the first entry to the last on ArrowUp`; `…keyboard.spec.ts::Should skip disabled entries by index`; `…keyboard.spec.ts::Should move to the first and last enabled entry on Home and End`; `…keyboard.spec.ts::Should page by the visible row count and clamp at the top`

---

### FM-17 | Opening the list from the keyboard focuses the wrong end

- **ID:** FM-17
- **Category:** component-contract-bypass
- **Risk:** a11y — `bds-select.focusFromTriggerKey` prefers the *last mounted* item, which at the window top is entry 13, not entry 1,000.
- **Input that reveals it:** closed popover, ArrowUp / ArrowDown on the input.
- **Observed current behavior:** `navigate()` opens the popover then targets `scanEnabled(list, 0, 1)` for ArrowDown or `scanEnabled(list, list.length - 1, -1)` for ArrowUp (`ItemsNavigationController.ts:197-216`).
- **Recommended contract:** ArrowDown focuses the first enabled entry; ArrowUp the last enabled entry of the full list.
- **Contract status:** confirmed
- **Why it matters:** the acceptance criterion in T11 is explicit about the full list.
- **Covered by:** `…keyboard.spec.ts::Should open the closed list on ArrowDown and focus the first entry`; `…keyboard.spec.ts::Should open the closed list on ArrowUp and focus the last entry of the full list`; `…keyboard.spec.ts::Should focus the last suggestion on ArrowUp from the input when nothing is focused`

---

### FM-18 | Focus is lost while the window shifts

- **ID:** FM-18
- **Category:** race-timing
- **Risk:** a11y — focus drops to `body` when the focused suggestion unmounts, stranding keyboard users.
- **Input that reveals it:** a jump that leaves the window; a mouse scroll that unmounts the focused entry.
- **Observed current behavior:** during a jump focus moves to `.bds-search-bar__list` (`ItemsNavigationController.ts:159`) and then to the mounted target; `recoverFocus()` returns focus to the input when the tracked entry is gone (`246-269`).
- **Recommended contract:** focus is never left on `body`; the anchor holds it while scrolling and the input receives it when the entry is unreachable.
- **Contract status:** confirmed
- **Why it matters:** T11 acceptance requires "no focus loss".
- **Covered by:** `…keyboard.spec.ts::Should focus the list anchor before the target of a jump that leaves the window`; `…keyboard.spec.ts::Should return focus to the input when scrolling unmounts the focused suggestion`

---

### FM-19 | Home/End on the input move focus into the list

- **ID:** FM-19
- **Category:** boundary
- **Risk:** a11y/usability — Home/End are caret keys while typing; hijacking them breaks editing.
- **Input that reveals it:** Home or End pressed while the input has focus.
- **Observed current behavior:** `handleKey` returns before `preventDefault` when the target is the input and the key is Home/End (`ItemsNavigationController.ts:101`).
- **Recommended contract:** Home/End from the input are left to the caret.
- **Contract status:** confirmed
- **Why it matters:** documented behaviour of the controller.
- **Covered by:** `…keyboard.spec.ts::Should ignore Home and End pressed on the input`

---

### FM-20 | Slotted mode inherits items-mode behaviour

- **ID:** FM-20
- **Category:** equivalence
- **Risk:** functional — slotted consumers (the pre-existing path, used by `bds-table`) would lose their working keyboard/list behaviour.
- **Input that reveals it:** slotted list, ArrowDown on the input.
- **Observed current behavior:** `isActive()` requires `isItemsMode` (`bds-search-bar.tsx:75`), so slotted mode keeps the `bds-select`/`bds-list-menu` path (first slotted item focused, no `aria-posinset`, no window).
- **Recommended contract:** slotted navigation is unchanged.
- **Contract status:** confirmed
- **Why it matters:** T13 explicitly kept the slotted path.
- **Covered by:** `…keyboard.spec.ts::Should leave the slotted list navigation to the select`

---

### FM-21 | A commit changes `value` without telling a 2-way binding

- **ID:** FM-21
- **Category:** component-contract-bypass
- **Risk:** functional — `valueChange` is the event the Vue `v-model` directive reads `target.value` from at commit time (`targets/vue-output-target.ts:componentModels`). A commit that writes `value` silently leaves the bound ref stale or one commit behind: typing free text then Tab updated the host property but never the Vue ref (T43 symptom).
- **Input that reveals it:** list mode, type a query and let the debounce fire (or blur / close the popover before it fires), on both `items` and slotted lists; then a commit whose query already equals `value`.
- **Observed current behavior:** `applyQuery` assigns `this.value = value` and emits `valueChange` only when the assignment actually changes the value (`bds-search-bar.tsx:273-284`, added for T43).
- **Recommended contract:** _(resolved 2026-10-26 — the user ruled option A in `ai-work/plans/EOA-19597-bds-search-bar-virtual-suggestions.md` task 43)_ every list-mode commit of a genuinely different query emits exactly one `valueChange` carrying the committed string, whether the commit comes from the debounce timer, `commitTypedQuery()` on blur, or `commitTypedQuery()` on popover close; a commit equal to the current `value` emits nothing; a cancelled debounce never produces a second event.
- **Contract status:** confirmed
- **Why it matters:** it is the picked fix for the only Vue wrapper parity failure in T18; the equality guard is what keeps it from duplicating the keystroke event when the debounce lands on unchanged text.
- **Covered by:** `…events.spec.ts::Should emit one valueChange with the typed text when the debounce commits the query`; `…events.spec.ts::Should emit one valueChange when blur commits a pending query before the debounce fires`; `…events.spec.ts::Should emit nothing when blur follows a debounce that already committed the query`; `…events.spec.ts::Should emit nothing when the committed query equals the current value`; `…events.spec.ts::Should emit one valueChange when the suggestions popover close commits a pending query`; `…events.spec.ts::Should emit an empty valueChange once when a pending erase-to-empty commits`; `…events.spec.ts::Should emit one valueChange with the typed text when the debounce commits the query in slotted mode`; `…events.spec.ts::Should keep the field and the value aligned across repeated blur cycles`

---

### PD-01 | First assignment of `items` after mount leaves the list empty until the next render

- **ID:** PD-01
- **Category:** race-timing
- **Risk:** functional — a consumer that fetches suggestions and assigns `items` after the component mounted sees an empty dropdown (the window is created but never mounted) until an unrelated re-render (typing, a new `items` array) happens.
- **Input that reveals it:** mount with `items === undefined`, then assign a populated array.
- **Observed current behavior:** `componentWillRender` creates the window; `mountVirtualWindow()` in `componentDidRender` bails when `.bds-list-menu__content` does not exist yet, which is the case on the render that first introduces the internal list (`bds-search-bar.tsx:452-481`). A second parent render mounts it. Assigning `items` before the first render (property set pre-upgrade, as React/Vue wrappers do) works — verified in `newSpecPage` with a `template`.
- **Recommended contract:** _(resolved 2026-10-26 — ruled by the user as plan task T30, fixed in `mountVirtualWindow()` by a bounded `requestAnimationFrame` retry)_ the window must mount once the list's scroll element appears, on a bounded retry loop (`ITEMS_MODE_MOUNT_MAX_FRAMES = 120`), mounted exactly once, and the pending retry must be cancelled and its frame budget restored when the window is disposed.
- **Contract status:** confirmed
- **Why it matters:** the async-data consumer path is common; the failure is silent.
- **Covered by:** `src/components/forms/bds-search-bar/__test__/bds-search-bar.items.spec.ts::Should mount the suggestion window when items are assigned after the component has mounted`; `…items.spec.ts::Should mount the window exactly once while the retry waits for the list content`; `…items.spec.ts::Should cancel a pending mount retry when items are cleared before it runs`; `…items.spec.ts::Should mount the window on the first render when items are set before the component mounts`

---

### PD-02 | Blurring after typing commits the value but blanks the field

- **ID:** PD-02
- **Category:** race-timing
- **Risk:** visual/functional — after typing free text and tabbing away, `value` holds the text while the visible field is empty.
- **Input that reveals it:** `items` mode, type a query that matches nothing (e.g. `Item 3x`) with the debounce still pending, then blur the input; the same happens on popover close and on Escape from a focused suggestion.
- **Observed current behavior:** `handleBlur` commits the pending query → `value` becomes the typed text; `bds-select.listenBlurInput` → `resetValueField()` then writes `''` into the field because the select's own `value` is still empty; the search bar's later render passes the same `fieldText` as before (`Item 3x`), so Stencil does not re-patch the child and the blank stays (`bds-search-bar.tsx:413-427`; `bds-select.tsx:684-691`).
- **Recommended contract:** _(resolved 2026-10-26 — ruled by the user as plan task T31, fixed by returning early from `bds-select.resetValueField()` when `managed`)_ the field must show the committed text after blur, popover close and Escape from an item: the label for a committed `value` that matches an entry, the typed text for free text, and never a blank while a value is committed.
- **Contract status:** confirmed
- **Why it matters:** it contradicts T12's accepted blur behaviour and is user-visible; the same text-not-patched shape could affect other child prop consumers.
- **Covered by:** commit half — `…events.spec.ts::Should commit a pending query on blur`, `…events.spec.ts::Should commit a pending query when the suggestions popover closes`; visible-text half — `…events.spec.ts::Should keep free text visible after blur commits it`, `…events.spec.ts::Should show the label of the matching suggestion after blur`, `…events.spec.ts::Should keep free text visible when the suggestions popover closes after typing`, `…events.spec.ts::Should show the label of the matching suggestion when the suggestions popover closes`, `…events.spec.ts::Should keep free text visible and return focus to the input when Escape closes a focused suggestion`, `…events.spec.ts::Should show the label of the matching suggestion when Escape closes a focused suggestion`, `…events.spec.ts::Should keep the field and the value aligned across repeated blur cycles`; root cause — `src/components/forms/bds-select/__test__/bds-select.basics.spec.ts::Should leave the field text untouched when a managed select resets an empty value`

---

### PD-03 | Duplicate `value`s produce duplicate window keys

- **ID:** PD-03
- **Category:** boundary
- **Risk:** visual — two entries with the same `value` share a vdom key and `bds-list-menu-item` identity, so reuse can show the wrong label and selection marks both.
- **Input that reveals it:** `items` containing two entries with the same `value`.
- **Observed current behavior:** `getItemKey` returns `filteredItems[index]?.value ?? index` (`bds-search-bar.tsx`), and `selected` is `item.value === this.value`, so both duplicates render selected.
- **Recommended contract:** _(resolved 2026-10-26 — ruled by the user as plan task T32)_ a repeated `value` is reported with exactly one console warning per instance and the list is left as assigned (no de-duplication); the warning is not repeated on a second `items` assignment, and never fires in `mode="search"`, where no list renders. The `items` JSDoc states the uniqueness requirement.
- **Contract status:** confirmed
- **Why it matters:** the prop is a flat v1 API with no other uniqueness signal; silently selecting the wrong entry is the failure the warning prevents.
- **Covered by:** `src/components/forms/bds-search-bar/__test__/bds-search-bar.items.spec.ts::Should warn once when items repeat a value`; `…items.spec.ts::Should keep every duplicated entry instead of de-duplicating the list`; `…items.spec.ts::Should not warn again when duplicate items are assigned a second time`; `…items.spec.ts::Should not warn about duplicate values in mode="search"`

---

### PD-04 | `valueChange` is equality-guarded on commit but not on pick or clear

- **ID:** PD-04
- **Category:** equivalence
- **Risk:** consumer-facing event asymmetry — a `v-model` consumer sees "at most one event per change" after a debounced commit but an unconditional event after a pick (`handleSelectChange`) and after a clear (`handleFieldClear`), including re-picking the already-selected suggestion or clearing an already-empty field.
- **Input that reveals it:** pick the same suggestion twice; fire `bdsClear` on a field whose `value` is already `''`.
- **Observed current behavior:** both handlers emit `valueChange` without comparing against the current value; `applyQuery` (FM-21) compares first.
- **Recommended contract:** _(resolved 2026-10-26 — ruled by the user as plan task T47)_ keep the asymmetry and document it: the keystroke, pick and clear emissions are user actions and always fire even when the reported value is unchanged, while the debounced commit is a state change and fires only when it moves `value`. The `valueChange` JSDoc states exactly that.
- **Contract status:** confirmed
- **Why it matters:** the event is the contract the React `onValueChange` and Vue `v-model` bindings read; documenting which emissions are unconditional keeps a guard from being "fixed" into the emitter later.
- **Covered by:** commit half — FM-21's seven specs; always-emit half — `src/components/forms/bds-search-bar/__test__/bds-search-bar.events.spec.ts::Should emit valueChange again when the same suggestion is picked twice`; `…events.spec.ts::Should emit valueChange when the field is cleared while it is already empty`

---

### FM-22 | One interaction delivers a child's event alongside the search bar's own

- **ID:** FM-22
- **Category:** component-contract-bypass
- **Risk:** consumer-facing event contract — a host listener counts two `bdsClear` (or two `valueChange`) for one clear and two `valueChange` for one pick, so a `v-model`/analytics consumer double-counts.
- **Input that reveals it:** an X-clear, a suggestion pick, and Escape with a committed value, in `items` and slotted mode.
- **Observed current behavior:** the composed `bds-text-field`'s `bdsClear`/`bdsChange`/`valueChange` and the `bds-select`'s `valueChange` are stopped at those children (`onBdsClear={this.handleFieldClear}` with `event?.stopPropagation()`, `onBdsChange`/`onValueChange={this.stopChildEventPropagation}`); only the search bar's own events reach the host.
- **Recommended contract:** one interaction delivers exactly one host event per name, and `event.target` is the search bar host for every event a host listener receives; typing still delivers one `bdsInput` per keystroke plus the single commit `valueChange`.
- **Contract status:** confirmed
- **Why it matters:** the component's JSDoc states that the composed children's events are stopped at those children; a leaked child event breaks that promise without changing `event.detail`, so it is invisible except by counting.
- **Covered by:** `…events.spec.ts::Should deliver exactly one bdsClear to a host listener when the clear button fires`; `…events.spec.ts::Should deliver exactly one bdsSearch and one valueChange to host listeners when a suggestion is picked`; `…events.spec.ts::Should deliver one bdsInput per keystroke plus a single commit valueChange`; `…events.spec.ts::Should deliver exactly one bdsClear to a host listener when Escape is pressed with text` (each parameterised over slotted and `items` mode)

---

### FM-23 | Slotted mode shows the raw value instead of the option label

- **ID:** FM-23
- **Category:** equivalence
- **Risk:** visual — a consumer sees internal ids (`s-21`) instead of human labels after a pick or a programmatic `value`, while `items` mode shows the label for the same interaction.
- **Input that reveals it:** slotted list, pick an option; assign `value` for a mounted option; assign free text; the same with `mode="search"`.
- **Observed current behavior:** `fieldText` returns `this.slottedLabel ?? this.value` outside `items` mode, where `slottedLabel` resolves the mounted option's rendered label first and then the label captured at pick time (`pickedLabel`), and returns `undefined` in `mode="search"`.
- **Recommended contract:** slotted mode shows the picked option's label, resolves a programmatic `value` against the mounted options, prefers the currently mounted label over the captured one, falls back to the captured label once the option is unmounted, keeps free text as assigned, and shows the raw value in `mode="search"`.
- **Contract status:** confirmed
- **Why it matters:** it is the T24 alignment between the two list modes, and label resolution must not depend on which option happens to be mounted.
- **Covered by:** `…events.spec.ts::Should show the picked option label instead of its raw value`; `…events.spec.ts::Should resolve the label of a mounted option for a programmatically assigned value`; `…events.spec.ts::Should keep free text exactly as assigned when no option matches`; `…events.spec.ts::Should show the raw value in mode="search", where no list is rendered`; `…events.spec.ts::Should prefer the mounted option label over the label captured at pick time`; `…events.spec.ts::Should fall back to the label captured at pick time once the option is unmounted`

---

### FM-24 | The trigger icon cannot reopen a closed suggestions popover

- **ID:** FM-24
- **Category:** component-contract-bypass
- **Risk:** functional — once the suggestions are closed while the field stays expanded, the only control that opened them cannot bring them back; the click silently degrades to a bare `bdsSearch`.
- **Input that reveals it:** an expanded bar with a list, popover open then closed, clicked again; the same with no list, in `mode="search"`, and while `disabled`.
- **Observed current behavior:** `handleTriggerClick` delegates to `toggleSuggestions()`, which closes a visible popover and otherwise opens one only when `canShowSuggestions` (list present, `mode="list"`, not disabled); it emits `bdsSearch` in every case.
- **Recommended contract:** with a list, the trigger closes an open popover and reopens a closed one, emitting exactly one `bdsSearch` either way; with no list, in `mode="search"`, or while disabled it never opens a popover and still emits one `bdsSearch`.
- **Contract status:** confirmed
- **Why it matters:** the trigger is the only explicit open gesture; a toggle that only closes leaves the suggestions unreachable after the first close.
- **Covered by:** `…events.spec.ts::Should close the open suggestions popover and emit one bdsSearch when the trigger is clicked`; `…events.spec.ts::Should reopen the closed suggestions popover and emit one bdsSearch when the trigger is clicked`; `…events.spec.ts::Should reopen the closed suggestions popover of a slotted list when the trigger is clicked`; `…events.spec.ts::Should not reopen the suggestions popover when no list is rendered`; `…events.spec.ts::Should not reopen anything in mode="search", which renders no popover`; `…events.spec.ts::Should not reopen the suggestions popover when the search bar is disabled`

---

### FM-25 | Leaving `items` mode leaves an open, empty suggestions popover

- **ID:** FM-25
- **Category:** null-empty
- **Risk:** visual — an empty floating box stays on screen with nothing to suggest and no way for the consumer to know the list vanished.
- **Input that reveals it:** `items` assigned with a list open, then set to `undefined`; the same on a bar that has a consumer `slot="list"`; `items = []`.
- **Observed current behavior:** `onItemsChange` calls `closeSuggestionsWithoutList()` when `isItemsMode` becomes false, which returns early for `hasSlottedList` and otherwise closes the select's popover; `[]` keeps items mode and renders the list's empty state.
- **Recommended contract:** leaving items mode closes the suggestions popover when there is no slotted list to take over, keeps it open when there is one, and `items = []` still shows the empty state without closing.
- **Contract status:** confirmed
- **Why it matters:** closing is the honest state when nothing can be suggested; closing while a slotted list exists would break a bar that still works.
- **Covered by:** `…items.spec.ts::Should close the suggestions popover when items become undefined and no list is slotted`; `…items.spec.ts::Should keep the suggestions popover open when items become undefined and a list is slotted`; `…items.spec.ts::Should still show the empty state when items become an empty array`

---

### FM-26 | The window-mount retry never gives up

- **ID:** FM-26
- **Category:** race-timing
- **Risk:** performance — an unbounded `requestAnimationFrame` retry keeps scheduling frames forever on a bar whose list content never appears (a list replaced by the consumer, a detached subtree), holding a frame slot per tick.
- **Input that reveals it:** `items` assigned after mount when the list's content element can never be resolved.
- **Observed current behavior:** `scheduleMountRetry()` returns once `mountRetryFrames >= ITEMS_MODE_MOUNT_MAX_FRAMES` (120), leaving `mountRetryFrame` null and `VirtualWindow.mount` uncalled; the budget is restored only by `cancelMountRetry()` on success or disposal.
- **Recommended contract:** after the frame budget is spent the retry stops scheduling frames and never mounts a window it cannot place.
- **Contract status:** confirmed
- **Why it matters:** the cap is what turns "keep trying until the child renders" into a bounded cost; without a test the give-up branch is only auditable by reading.
- **Covered by:** `…items.spec.ts::Should stop scheduling mount retries once the frame budget is spent`

---

### FM-27 | `aria-controls` promises a relationship it does not express

- **ID:** FM-27
- **Category:** a11y
- **Risk:** a11y — an empty `aria-controls` (or one aimed at the wrong element) tells assistive tech that the searchbox controls nothing, breaking the listbox relationship a combobox must expose.
- **Input that reveals it:** items mode, slotted mode, a re-render, and a bar with no list.
- **Observed current behavior:** `resolveListboxId()` reads `listboxEl` (`el.querySelector('bds-list-menu')`), assigns the search bar's own stable id when the list has none, and returns `''` when no list is rendered; `syncInputAccessibility` runs on load, on every render and on focus, and (since EOA-19597 T50) removes the attribute outright when the id resolves to `''` instead of writing an empty one.
- **Recommended contract:** in items and slotted mode `aria-controls` resolves through `getElementById` to the `bds-list-menu` that carries `role="listbox"`, stays the same across a re-render, is removed in `mode="search"`, and is **absent** (never `""`) when no list is rendered — a stale reference is removed when the listbox disappears.
- **Contract status:** confirmed
- **Why it matters:** `aria-haspopup="listbox"` is already advertised; the id reference is the other half of the same relationship. An empty `aria-controls` is ARIA-equivalent to absent but is invalid markup, and it is what the pre-T50 code emitted for a bar with no list.
- **Covered by:** `…a11y.spec.ts::Should point aria-controls at the listbox rendered for the items list`; `…a11y.spec.ts::Should point aria-controls at a consumer-slotted listbox`; `…a11y.spec.ts::Should keep aria-controls on the same listbox across a re-render`; `…a11y.spec.ts::Should set aria-autocomplete="list" and omit aria-controls when no list renders in mode="list"`; `…a11y.spec.ts::Should never write an empty aria-controls on a bar that has no list, even after focusing the input`; `…a11y.spec.ts::Should remove the aria-controls reference when the items list disappears`; `…a11y.spec.ts::Should remove the aria-controls reference when a slotted bar switches to mode="search"`

---

### FM-28 | A picked suggestion leaves the field without a clear action

- **ID:** FM-28
- **Category:** equivalence
- **Risk:** functional — a consumer that only ever picks (never types) cannot clear the committed value from the field, even with `clearable` set.
- **Input that reveals it:** `clearable` with a pick made without typing; a programmatic `value` assigned after mount in `mode="search"`; then a clear; `variant="static"`.
- **Observed current behavior:** `canShowClear` is `clearable && hasValue`, and `onValueChange` now mirrors a committed `value` into `hasValue`, so a pick or a programmatic value enables the action while a clear disables it; `variant="static"` keeps its own empty-value escape and otherwise still requires `clearable && hasValue`.
- **Recommended contract:** the clear action appears after a pick that involved no typing and after a programmatic `value`, disappears after the clear, and keeps `variant="static"`'s existing rules.
- **Contract status:** confirmed
- **Why it matters:** the two ways to reach a committed value without typing are the common consumer paths (selection-only and controlled), and both were un-clearable.
- **Covered by:** `src/components/forms/bds-search-bar/__test__/bds-search-bar.variants.spec.ts::Should show the clear action after a suggestion is picked without any typing`; `…variants.spec.ts::Should show the clear action when a value is assigned programmatically after mount`; `…variants.spec.ts::Should hide the clear action once the committed value is cleared`; `…variants.spec.ts::Should keep the variant="static" clear action rules unchanged`

---

### FM-29 | Typing after a pick appends to the displayed label

- **ID:** FM-29
- **Category:** component-contract-bypass
- **Risk:** usability — the field shows `Item 3` after a pick, so the next keystroke produces `Item 3x` instead of starting a new query; the user has to clear the label by hand.
- **Input that reveals it:** a pick (pointer or keyboard), then focus the field and type; the same after free text.
- **Observed current behavior:** `selectCommittedText()` runs on focus and on popover close, bails while `typedText !== null` and when no label resolves, and otherwise selects the whole input value on the next frame via `selectInputText()`; free text resolves no label and keeps its caret.
- **Recommended contract:** focusing the field after a pick or a committed label selects the whole label so the first keystroke replaces it; free text is not selected.
- **Contract status:** confirmed
- **Why it matters:** it is the only way a pick-then-refine flow works without manual erasing, and the deferred selection is easy to lose in a refactor.
- **Covered by:** `…events.spec.ts::Should select the whole label when the field is focused after a pick`; `…events.spec.ts::Should select the whole label when the field is focused after a pick made from the keyboard`; `…events.spec.ts::Should not select anything when the field is focused after free text was committed`

---

### PD-05 | A clear also emits `bdsSearch` (via the select's own `bdsChange`)

- **ID:** PD-05
- **Category:** equivalence
- **Risk:** consumer-facing event contract — an X-clear delivers `bdsClear`, `bdsInput ''`, two `valueChange ''` and a `bdsSearch {value: ''}`. The `bdsSearch` is defensible (a clear is a search reset) but it is produced as a side effect of `bds-select.listenClearInput → setValue('') → bdsChange → handleSelectChange`, which is the "pick" path.
- **Input that reveals it:** an X-clear in `items` or slotted mode; the same when the field is already empty.
- **Observed current behavior:** pre-fix, `handleFieldClear` (own `bdsClear`/`bdsInput`/`valueChange`) plus `handleSelectChange` (second `valueChange` and the `bdsSearch`) both fired for one clear; `bdsChange` itself was stopped at the select. Escape emitted only the first set, because it never reaches the select's clear listener. Fixed by `listenClearInput` returning after `resetChildren()` in `managed` mode (`bds-select.tsx:588-592`), so the clear never reaches `setValue` or the pick path; the list still resets its hidden state and roving tab stop.
- **Recommended contract:** a clear — from the X button or Escape — delivers exactly one `bdsClear`, one `bdsInput` with `{ value: '' }`, one `valueChange` with `''`, and **no** `bdsSearch`; a suggestion pick still delivers one `bdsSearch` and one `valueChange` and no clear events; typing and the debounced commit are unchanged.
- **Contract status:** confirmed — ruled by the user 2026-10-26 ("one X-clear = exactly one `bdsClear`, one `bdsInput ''`, one `valueChange ''`, zero `bdsSearch`; Escape-with-text matches; a pick still = one `bdsSearch` + one `valueChange`").
- **Why it matters:** T22's observation list called out duplicate `bdsClear`/`valueChange` on an X-clear; a consumer wiring analytics or a search request to `bdsSearch` would fire a search for every clear, and the second `valueChange` makes one user action look like two. Keeping the pick path emitting `bdsSearch` preserves the deliberate "pick = search" behaviour.
- **Covered by:** `src/components/forms/bds-search-bar/__test__/bds-search-bar.events.spec.ts::Should emit one bdsClear, one bdsInput and one valueChange and no bdsSearch when the clear button fires`; `…events.spec.ts::Should emit one bdsClear, one bdsInput and one valueChange and no bdsSearch when Escape clears text`; `…events.spec.ts::Should keep a suggestion pick as one bdsSearch and one valueChange with no clear events` — each in both the slotted and items `describe.each` block.

---

### PD-06 | `aria-controls` targets the hidden slotted list when `items` also wins

- **ID:** PD-06
- **Category:** a11y
- **Risk:** a11y — with `items` set and a consumer `slot="list"` also present, `items` wins and the consumer list is hidden but still in the DOM; the old `listboxEl` (`el.querySelector('bds-list-menu')`) returned the consumer list first, so `aria-controls` pointed at an element that is not the rendered listbox.
- **Input that reveals it:** a bar with both `items` and a `<bds-list-menu slot="list">` child.
- **Observed current behavior:** measured 2026-10-26, pre-fix: `aria-controls` = `bds-search-bar-list-<id>` assigned to the slotted `bds-list-menu` (not the rendered list) while the active list is the select's `.bds-search-bar__list` (`role="listbox"`). Fixed by resolving `listboxEl` by mode: `itemsListEl` (`.bds-search-bar__list`) in items mode, the consumer-slotted `bds-list-menu` otherwise, and nothing in `mode="search"` (`bds-search-bar.tsx:978-982`).
- **Recommended contract:** `aria-controls` resolves through `getElementById` to the active listbox carrying `role="listbox"`; in items mode that is the items list even when a consumer list is the first DOM match, in slotted mode it is the consumer list, it stays the same across a re-render, and it is absent in `mode="search"`.
- **Contract status:** confirmed — ruled by the user 2026-10-26 (resolve by mode: items list in `items` mode, consumer list in slotted mode, absent in `mode="search"`).
- **Why it matters:** FM-27's confirmed contract says `aria-controls` resolves to the element carrying `role="listbox"`; this combination violated it while passing the per-mode tests written for it, because those share a single list in the DOM.
- **Covered by:** `src/components/forms/bds-search-bar/__test__/bds-search-bar.a11y.spec.ts::Should keep aria-controls on the items listbox when a slotted list comes first in the DOM`; `…a11y.spec.ts::Should leave aria-controls absent in mode="search"`; the per-mode contract is additionally covered by `…a11y.spec.ts::Should point aria-controls at the listbox rendered for the items list`, `…a11y.spec.ts::Should point aria-controls at a consumer-slotted listbox` and `…a11y.spec.ts::Should keep aria-controls on the same listbox across a re-render`.


---

### FM-30 | An external `value` assignment leaves the items filter stale

- **ID:** FM-30
- **Category:** component-contract-bypass
- **Risk:** functional — a consumer that drives the bar from its own state (`el.value = ''`, a reset button, a router restoring an empty query) clears the field but leaves the previous `itemsQuery` applied, so the list still shows the old matches with no way to notice; the field and the list disagree about what the query is.
- **Input that reveals it:** an `items` bar filtered by typing, then `el.value = ''` assigned from script; the same with a non-empty external value.
- **Observed current behavior:** measured 2026-10-26, pre-fix: type `99` (19 results), assign `el.value = ''` — field clears, list still shows the 19 `Item 99…` matches. `onValueChange` only reset `typedText`/`hasValue`; it never touched `itemsQuery`. Fixed by reconciling the filter from the watcher (`applyItemsQuery(next, false)`, silent) for any `items`-mode assignment the component did not make itself.
- **Recommended contract:** an `items`-mode `value` assigned from outside is also the new query — the filter and the window scroll are reconciled with it (a `""` restores the full list) and no result count is announced, because an external assignment is not a user query. The reconcile is a no-op when the value already equals the applied query, so re-assigning the current query does not jerk the scroll.
- **Contract status:** confirmed — plan T48 acceptance criteria ("external `value` assignment updates the filter and scroll; X/Escape unchanged; no double announcement"), batch ruled 2026-10-26.
- **Why it matters:** consumers treat `value` as the single source of truth; a stale filter makes a programmatic reset look broken and leaves the next interaction starting from a hidden filter.
- **Covered by:** `…items.spec.ts::Should reset the items filter and the scroll without announcing when a value is cleared from outside`; `…items.spec.ts::Should apply an assigned query without announcing it`; `…items.spec.ts::Should keep the scroll position when an assigned value matches the query already applied`; `…events.spec.ts::Should filter the list to a programmatic value assigned after mount`; `…events.spec.ts::Should emit nothing when the committed query equals the current value`; `…items.spec.ts::Should leave a slotted list unfiltered when a value is assigned from outside`
- **Known fixture limitation:** when the assignment *is* what narrows the list, the matching item is created by that same render and `bds-select` (managed) has already found no mounted option to select, so the fresh `bds-list-menu-item` renders without `selected` even though `value` matches it. `…events.spec.ts::Should filter the list to a programmatic value assigned after mount` therefore asserts the window contents, `aria-setsize` and the resolved label, not the item's `selected` attribute.

---

### FM-31 | The component's own `value` writes re-filter the list

- **ID:** FM-31
- **Category:** component-contract-bypass
- **Risk:** functional — a suggestion pick commits a value that is not the query the user typed; if the pick is treated like an external assignment, the list collapses to the single picked entry (or to nothing) the moment the user selects.
- **Input that reveals it:** an `items` bar filtered by typing `Item 1`, then a pick of `item-5`; the same on clear.
- **Observed current behavior:** the three internal writes (debounced commit, pick, clear) go through `commitValue()`, which raises `isInternalValueWrite` for the assignment, and `onValueChange` returns on that flag. A pick therefore keeps `itemsQuery === 'Item 1'` (11 mounted) while `value` becomes `item-5`; a clear keeps its own `applyItemsQuery('', …)` and is not reset twice.
- **Recommended contract:** internal commits never reconcile the filter; the typed-query commit keeps the list filtered by that query, a pick keeps the query applied before it, and a clear resets the filter exactly once with its announcement.
- **Contract status:** confirmed — plan T48 ("keeping the internal paths unchanged").
- **Why it matters:** the pick path is the only place `value` and `itemsQuery` legitimately diverge, so it is the only observable proof the flag exists; without it the list collapses on every selection.
- **Covered by:** `…items.spec.ts::Should keep the applied query when a suggestion pick commits a different value`; `…items.spec.ts::Should keep the filtered list after the debounce commits the typed query`; `…items.spec.ts::Should restore the full list and announce the count when the clear action fires`

---

### FM-32 | Switching a live `items` bar to `mode="search"` re-renders into the wrong DOM

- **ID:** FM-32
- **Category:** race-timing
- **Risk:** functional — `mode` is a public reflected prop; a consumer that toggles it at runtime must end with the direct-text-field layout and no listbox wiring left over.
- **Input that reveals it:** an `items` bar with a mounted window, then `mode="search"`; then back to `mode="list"`.
- **Observed current behavior:** the production component transitions correctly (verified in headless Chromium against `dist`, 302 ms, no page errors, and switching back re-renders the select). Under `newSpecPage` the identical transition never settles: Stencil's testing runtime reverses slot relocation with a `nextSibling` walk, and mock-doc's getter returns the parent's first child instead of `null` for a node that is absent from `parentNode.childNodes` (Stencil keeps a parallel `__childNodes`), so the walk cycles. This is a mock-doc defect, not a component bug — no production change was made.
- **Recommended contract:** after the transition the `bds-select` and every `bds-list-menu` are gone, the field sits inside `.bds-search-bar__field-wrap`, the status live region is gone, `aria-controls` is absent and `aria-autocomplete` is `"none"`. The spec proves it with a **spec-local** `nextSibling` shim (never a global `setupFilesAfterEnv` change) that returns `null` only when the node is missing from `parentNode.childNodes`.
- **Contract status:** confirmed — plan T49, triaged as a mock-doc limitation (shim recipe in `.claude/agent-memory/frontend-subagent/mock-doc-nextsibling-slot-relocation-hang.md`).
- **Why it matters:** without the shim the regression cannot be asserted at all — a racing `setTimeout` never fires because timers are starved by the synchronous loop; with it, the final DOM is fully assertable.
- **Covered by:** `…items.spec.ts::Should render the direct text field once a live items bar switches to mode="search" (the spec-local nextSibling shim is needed because mock-doc slot relocation walks a cyclic chain)`

---

### FM-33 | The picked label appears and takes focus one frame after the pick

- **ID:** FM-33
- **Category:** race-timing
- **Risk:** input loss — after a mouse pick `document.activeElement` stayed `body` until the composed `bds-select` re-focused the input on `requestAnimationFrame`, so a keystroke typed in that frame was dropped and the deferred label paint then showed the label (measured: field `99` → `Item 199`, the `z` vanished).
- **Input that reveals it:** an `items` or slotted bar with the field focused, type `99`, pick a suggestion with the mouse, type `z` in the same frame.
- **Observed current behavior:** `handleSelectChange` calls `applyPickedFieldText()` right after `commitValue()` (`bds-search-bar.tsx:737`): guarded on `mode !== "list"`, `typedText !== null`, `!el.isConnected` and a missing input (`:459-461`), it writes `fieldText` into the input only when it differs, focuses the input synchronously under `isApplyingPickedFocus` (`:464-469`) and applies `selectInputText()` (`:470`). `selectCommittedText()` returns early while that flag is set (`:437`), so the focus event the pick causes cannot schedule a second, deferred selection. The deferred path on focus / popover close is unchanged.
- **Recommended contract:** after a pick in `mode="list"` the input holds the resolved label, is focused and carries the whole-label selection before `handleSelectChange` returns — in `items` mode (the matching suggestion's label) and slotted mode (the mounted option's label) alike; a programmatic `value` never moves focus and never applies a selection; exactly one selection call per pick, including after frames settle; nothing is applied in `mode="search"`.
- **Contract status:** confirmed — plan T51 (fix implemented by @frontend-subagent, verified in headless Chrome; the fix and its regression spec land together).
- **Why it matters:** a pick is the primary way to reach a committed value, and losing a same-frame keystroke both discards the user's input and makes a pick-then-refine flow feel broken.
- **Covered by:** `…events.spec.ts::Should focus the input and select the picked label before the pick handler returns`; `…events.spec.ts::Should leave focus and the selection untouched when a value is assigned programmatically`; `…events.spec.ts::Should apply the picked selection exactly once and never schedule a second one from the focus it causes`; `…events.spec.ts::Should hand the field the slotted option label before the pick handler returns`; `…events.spec.ts::Should never hand the field a picked text in mode="search"`
- **Known fixture limitation:** mock-doc's `HTMLInputElement` exposes no `setSelectionRange`, so the spec installs a per-element shim and asserts the call (`0`, label length) rather than the resulting selection range, which mock-doc does not model. The dropped keystroke itself is a browser-level race (real key delivery between the pick and the next frame) that `newSpecPage` cannot reproduce — the spec asserts its preconditions instead: focus, field text and selection all applied inside the pick handler. The `mode="search"` guard is unreachable through the DOM there (no `bds-select` is rendered), so that test drives `applyPickedFieldText()` on `rootInstance` directly, the established internal-member pattern.

---

### FM-34 | An appended page of suggestions throws the reader back to the top

- **ID:** FM-34
- **Category:** race-timing
- **Risk:** functional — paging results in (`items = [...items, ...nextPage]`) is the main reason a consumer drives this component; resetting the scroll on append makes infinite-scroll unusable, because every append snaps the list to the first entry and unmounts the window the reader was looking at, mid-read.
- **Input that reveals it:** an `items` bar with the list scrolled and a query applied, then `items` reassigned to a longer array whose first entry is the same object value.
- **Observed current behavior:** `onItemsChange` receives `(next, previous)` and calls `resetItemsScroll()` only when `previous?.[0]?.value !== next?.[0]?.value` (`bds-search-bar.tsx:143-153`); the count still updates (`virtualWindow.update`), and `announceItemsCount()` still re-announces when `itemsQuery !== ''`.
- **Recommended contract:** an append that preserves the first entry's `value` keeps `scrollTop`, keeps the mounted window's absolute positions (`aria-posinset` unchanged), updates `aria-setsize`, and — under an active query — re-announces the new count. With no query it stays silent, because an append is not a user query.
- **Contract status:** confirmed — user-supplied contract for the `items`-change scroll fix (EOA-19598).
- **Why it matters:** without the guard, every append is indistinguishable from a replacement, so the window's scroll position is destroyed on the one operation that should preserve it.
- **Covered by:** `…items.spec.ts::Should keep the scroll and the mounted window and announce the new count when an entry is appended during a query`; `…items.spec.ts::Should keep the scroll and stay silent when an entry is appended without a query`
- **Known fixture limitation:** mock-doc drives the window from an explicit `scroll` event and mocked geometry (`attachListScrollGeometry`), so the contract is asserted at `scrollTop`/`aria-posinset` level rather than against real layout.

---

### FM-35 | A new dataset inherits the old scroll offset, window and announcement

- **ID:** FM-35
- **Category:** null-empty
- **Risk:** functional — a prepended entry, a wholesale dataset swap, or the first data load leaves the list scrolled to an offset that belonged to a different list, so the reader lands mid-way through (or past the end of) suggestions they have never seen.
- **Input that reveals it:** a scrolled `items` bar whose list is then prepended to, replaced with an unrelated dataset, assigned for the first time, or populated after being `[]`.
- **Observed current behavior:** the `previous?.[0]?.value !== next?.[0]?.value` comparison is true for each of those (prepend changes the first entry, a replacement changes it, `undefined`/`[]` head reads as `undefined`), so `resetItemsScroll()` runs and the window returns to index 0; `items = undefined` returns earlier through `closeSuggestionsWithoutList()` and never resets.
- **Recommended contract:** prepending, replacing, the first assignment and an assignment after an empty list each reset `scrollTop` to `0` and the window to `aria-posinset` `"1"`; leaving `items` mode (`items = undefined`) closes the suggestions popover without calling `resetItemsScroll()`.
- **Contract status:** confirmed — user-supplied contract for the `items`-change scroll fix (EOA-19598).
- **Why it matters:** the guard is only correct if it still fires for the cases that genuinely invalidate the offset; a guard that resets too rarely is the same class of bug as one that resets too often.
- **Covered by:** `…items.spec.ts::Should reset the scroll, the mounted window and the count when the items dataset is replaced during a query`; `…items.spec.ts::Should reset the scroll when an entry is prepended during a query`; `…items.spec.ts::Should reset the scroll when the items dataset is replaced with an unrelated list`; `…items.spec.ts::Should reset the scroll when items are assigned after an empty list`; `…items.spec.ts::Should reset the scroll on the first items assignment after mount`; `…items.spec.ts::Should close the suggestions without resetting the scroll when items become undefined`

---

### FM-36 | An external `value` write leaves the previous result count in the live region

- **ID:** FM-36
- **Category:** a11y
- **Risk:** a11y — a controlled consumer's programmatic write (`el.value = ''` on a reset button, a router restoring an empty query, a chip click) is not a user query, but the polite region keeps the count from the last one: the user hears "11 results" while the field is empty and the full list is shown. A new external query is worse: the filter applies silently and the region still reads the *previous* query's count, so the heard number and the visible list describe different queries.
- **Input that reveals it:** an `items` bar filtered by typing `Item 1` (region `11 results`), then `el.value = ''`; the same with `el.value = 'Item 2'` instead of clearing.
- **Observed current behavior:** measured 2026-10-28 on `fix/EOA-19598…` with the fix reverted: `Expected: "" / Received: "11 results"` for the clear and `Received: "1 result"` for the new query. Pre-fix `onValueChange` returned after `!this.isItemsMode` and never wrote `resultsAnnouncement`; the external branch called `applyItemsQuery(next, false)`, which is silent by design (`bds-search-bar.tsx:177-188`). Fixed by writing `this.resultsAnnouncement = ''` on every non-internal, non-typed-commit assignment, before the mode guard and before the reconcile.
- **Recommended contract:** an external `items`-mode assignment never announces. Clearing returns the region to `''` even though the same assignment immediately restores the full list; assigning a new query leaves `''` while the filter and scroll reconcile (FM-30). The internal paths keep their announcements: the debounced commit, a pick (unchanged query, FM-31) and a clear (FM-37's counterpart).
- **Contract status:** confirmed — user-supplied contract for the EOA-19598 stale live-region fix ("programmatic writes must not announce, and must not leave a stale count").
- **Why it matters:** a live region is the only feedback a screen-reader user gets for an off-screen filter, so a count that survives a programmatic reset actively misreports the list.
- **Covered by:** `src/components/forms/bds-search-bar/__test__/bds-search-bar.items.spec.ts::Should reset the items filter and the scroll without announcing when a value is cleared from outside`; `…items.spec.ts::Should apply an assigned query without announcing it`

---

### FM-37 | An `items` update with no active query leaves the previous announcement standing

- **ID:** FM-37
- **Category:** a11y
- **Risk:** a11y — paging an entry in (`items = [...items, next]`) after a clear re-publishes the clear's count as if the update had produced it; the announced number and the mounted list disagree.
- **Input that reveals it:** type a query, clear the field with X (region `30 results`), then append an entry with no query applied.
- **Observed current behavior:** measured 2026-10-28 with the fix reverted: `Expected: "" / Received: "30 results"`. Pre-fix `onItemsChange` re-announced only when `itemsQuery !== ''` and otherwise left `resultsAnnouncement` untouched, so the previous announcement survived the update. Fixed by `else this.resultsAnnouncement = '';` (`bds-search-bar.tsx:153-154`).
- **Recommended contract:** an `items` update with no active query leaves the region empty, whatever it previously held; an update *with* an active query still announces the new count (FM-10, FM-34).
- **Contract status:** confirmed — user-supplied contract for the stale live-region fix.
- **Why it matters:** an append is not a user query, so it must not re-read a count the user did not ask for; the announcement half of the scroll fix (FM-34) depends on this branch being the exact complement of the query branch.
- **Covered by:** `…items.spec.ts::Should stay silent when an entry is appended after a clear announced the full count`; `…items.spec.ts::Should keep the scroll and stay silent when an entry is appended without a query`; announce half — `…items.spec.ts::Should announce the new count when entries are appended or prepended during an assigned query`

---

### FM-38 | Leaving items mode keeps the last announcement for the region that returns

- **ID:** FM-38
- **Category:** null-empty
- **Risk:** a11y — `items = undefined` unmounts the live region but not `resultsAnnouncement`; re-assigning `items` re-mounts the region carrying the count from the dataset that was thrown away, so a list that was never queried in the new data announces a number a screen reader cannot reconcile with anything on screen.
- **Input that reveals it:** an `items` bar filtered by typing (region `11 results`), then `items = undefined`, then `items` re-assigned.
- **Observed current behavior:** measured 2026-10-28 with the fix reverted: `Expected: "" / Received: "11 results"` on the internal state after the removal. Pre-fix the `!isItemsMode` branch called `closeSuggestionsWithoutList()` and returned, leaving `resultsAnnouncement` at `11 results`; the re-assignment then re-announced the still-applied query. Fixed by clearing before the close (`bds-search-bar.tsx:146-150`).
- **Recommended contract:** leaving items mode clears the announcement. On return the region is empty until either the still-applied query's count is announced by that `items` update or a new user query announces; an empty `itemsQuery` on return stays empty.
- **Contract status:** confirmed — user-supplied contract for the stale live-region fix ("clears it when items mode ends").
- **Why it matters:** the region is unmounted and remounted, so a stale value is not merely a leftover state field — it is the first thing the remounted live region publishes.
- **Covered by:** `…items.spec.ts::Should drop the announcement when items are removed and announce only the still-applied query on return`

---

### PD-07 | Toggling `mode` remounts the live region with the previous announcement

- **ID:** PD-07
- **Category:** a11y
- **Risk:** a11y — `mode` is a public reflected prop; `mode="search"` unmounts the status span but no watcher clears `resultsAnnouncement` (`onModeDepsChange` only re-syncs the input's ARIA, `onModeFieldTextChange` returns for anything but `list`, `onModeItemsChange` only warns). Switching back to `mode="list"` re-mounts the region already containing the previous count, so the first text that appears was produced by an interaction in the other mode. FM-36/37/38 each clear on their own trigger; a mode toggle is the one transition that clears nothing.
- **Input that reveals it:** an `items` bar, type `Item 1` (region `11 results`), `mode="search"`, then back to `mode="list"`.
- **Observed current behavior:** read from the source on 2026-10-28 — no `mode` watcher writes `resultsAnnouncement`, and the span is gated on `isItemsMode` in `render()` (`bds-search-bar.tsx:922-926`), so the state outlives the element. Not asserted in any spec; the FM-32 transition spec asserts only that the region is absent in `mode="search"`.
- **Recommended contract:** open — either a mode transition clears the announcement (consistent with FM-38, treating the remounted region as a fresh one), or the still-applied query's count is legitimately re-published in `mode="list"` and the current behaviour is correct. The answer also decides whether `mode` belongs in FM-38's trigger list.
- **Contract status:** pending-decision
- **Why it matters:** whichever is right, the choice is currently implicit; the three adjacent clears make "every transition that remounts the region clears it" the natural reading, but a `mode` toggle keeps the same list and query, so re-publishing is defensible.
- **Covered by:** _none — awaiting a ruling._

---

### PD-08 | `itemsQuery` survives leaving items mode, so a return can resurrect a filter the field no longer shows

- **ID:** PD-08
- **Category:** component-contract-bypass
- **Risk:** functional/a11y — `itemsQuery` is only written through `applyItemsQuery`, so an external `value` assignment made while the bar is *not* in items mode (the FM-36 branch returns before the reconcile) leaves the old query in place. Re-assigning `items` then filters to that stale query and announces its count while the field and `value` are empty: the field and the list disagree exactly as in FM-30, plus a count for a filter the consumer never re-applied.
- **Input that reveals it:** items mode, type `Item 1` (11 results), `items = undefined`, `el.value = ''` while out of items mode, then re-assign `items`.
- **Observed current behavior:** read from the source on 2026-10-28 — `onValueChange` clears the announcement and returns at `if (!this.isItemsMode) return;`, so `itemsQuery` keeps `Item 1`; on re-assignment `onItemsChange` filters by it and announces `11 results` (`bds-search-bar.tsx:153`, `531-541`). In the supported sequence (re-assigning `items` *without* an intervening external write) this is the intended "still-applied query's count", which FM-38 covers.
- **Recommended contract:** open — either leaving items mode (or any external `value` write made while out of it) resets `itemsQuery` to the current `value`, so a return never resurrects a filter the field does not show, or the applied query is deliberately retained across mode/`items` transitions and the divergence is accepted. The answer decides whether FM-38's "still-applied query" wording needs a precondition.
- **Contract status:** pending-decision
- **Why it matters:** the retained query is what makes FM-38's re-announcement meaningful; it is also the only path where a return can show a filtered list under an empty field.
- **Covered by:** _none — awaiting a ruling._

---

### FM-39 | A pick that bubbles from the rebuilt items list is dropped

- **ID:** FM-39
- **Category:** race-timing
- **Risk:** functional — after `items` is toggled (`undefined` → an array, or a new dataset), the internal `bds-list-menu` is a brand-new element. The `bds-select` bound its `bdsChange` listener to the *previous* list in `componentDidLoad` and never re-binds, so the pick bubbles straight past the select to the search bar's handler. Under the old origin guard (`e.target !== e.currentTarget`) that target is neither the select nor the handler's own element, so the pick was silently discarded: no commit, no `valueChange`, no `bdsSearch`, field unchanged.
- **Input that reveals it:** items mode with `items` set, `items = undefined`, then `items = [...]` again, then a `bdsChange` dispatched from (or clicked on) the re-rendered `.bds-search-bar__list`.
- **Observed current behavior:** `handleSelectChange` accepts the event when `e.target` is the `bds-select` host **or** `this.itemsListEl` (`bds-search-bar.tsx:336-350`, fix of 2026-10-28), so the rebuilt list's bubbled pick commits like any other pick.
- **Recommended contract:** a pick from the component's own rendered list commits exactly once with its `value` (one `valueChange`, one `bdsSearch`), records the label from the *current* dataset, moves focus into the input, and closes the suggestions popover once — even when the pick arrives from a list element the select never bound to.
- **Contract status:** confirmed
- **Why it matters:** a consumer that replaces `items` (pagination, a fresh search result set) could not select anything until an unrelated full remount of the search bar; the failure is silent, and the same interaction works before the `items` change.
- **Covered by:** `src/components/forms/bds-search-bar/__test__/bds-search-bar.events.spec.ts::Should commit a pick that bubbles from the items list re-rendered by the toggle`; `…events.spec.ts::Should neither commit nor emit again when the popover reports bdsClose after a pick`

---

### FM-40 | Closing the popover on a pick is owned by the select for select-emitted picks and by the search bar for its own list

- **ID:** FM-40
- **Category:** component-contract-bypass
- **Risk:** functional — the select's `listenListMenu` already closes the popover for a pick it consumes. If the search bar also closed it on every accepted pick, a select-emitted pick would close twice (re-entrant close, focus/hide churn). If the search bar closed it on none, an own-list pick would leave the popover open over the committed value, because the select never saw that event.
- **Input that reveals it:** a `bdsChange` dispatched from the `bds-select` host, versus one bubbling from the rebuilt items list.
- **Observed current behavior:** `if (fromOwnList) void this.bdsPopover?.closePopover();` — the close runs only for the own-list origin (`bds-search-bar.tsx:344`), and only that origin reaches the popover at all.
- **Recommended contract:** each origin closes the popover exactly once per pick: the select-emitted path leaves it to the select (no close from the search bar), the own-list path closes it from the search bar.
- **Contract status:** confirmed
- **Why it matters:** the two origins deliver the same visible result (a committed value and a hidden list); only the counting tells them apart, so a double close or a missing close is invisible to a DOM assertion that does not spy on `closePopover`.
- **Covered by:** `…events.spec.ts::Should commit a select-emitted pick without the search bar closing the popover`; `…events.spec.ts::Should commit a pick that bubbles from the items list re-rendered by the toggle`

---

### FM-41 | The widened origin guard must not accept a consumer list's or the text field's bubbled event

- **ID:** FM-41
- **Category:** component-contract-bypass
- **Risk:** consumer-facing event contract — the fix widens which `bdsChange` targets the search bar acts on. An identity check against its own rendered list is what keeps a consumer's `slot="list"` selection (which the select reports itself, after `stopPropagation`) and the composed text field's echo out of the pick path; a tag-based or "any list" widening would commit twice or commit typed text as a pick.
- **Input that reveals it:** in slotted mode, a `bdsChange` bubbling from the consumer's `bds-list-menu` (including one that replaced the element the select bound to, so the raw event really does reach the search bar), and a `bdsChange` with `{ value, event }` bubbling from the composed `bds-text-field`.
- **Observed current behavior:** the consumer list's raw event is consumed by the select, which re-emits its own `bdsChange` — one commit, one popover close; a consumer list the select never bound to reaches the search bar with `e.target` neither the select nor `.bds-search-bar__list`, and is dropped; the text field's `bdsChange` is stopped at the field by `onBdsChange={this.stopChildEventPropagation}`.
- **Recommended contract:** only the select host and the component's own rendered items list may start a pick; a consumer list contributes exactly one commit, through the select's re-emit, and never through its own bubbled event; a text-field echo commits nothing, emits nothing, and closes nothing.
- **Contract status:** confirmed
- **Why it matters:** it is the boundary the fix had to widen without crossing; the consumer-list and text-field cases pass with and without the fix (the select consumes them first), so they exist as locks against a future "accept any list" simplification rather than as reproductions of the bug.
- **Covered by:** `…events.spec.ts::Should ignore a bubbled bdsChange from a consumer list the select never bound to`; `…events.spec.ts::Should deliver a slotted consumer pick exactly once through the select re-emit`; `…events.spec.ts::Should ignore the bdsChange the text field forwards after the items list was re-rendered`

---

### FM-42 | A deselection reported with no detail commits an empty value

- **ID:** FM-42
- **Category:** null-empty
- **Risk:** functional — the own list can report a deselection (`detail` `undefined`, or an array for a multi-value list) on the path the fix newly accepts. Committing `undefined` would leave `value` a non-string and the field blank-but-uncommitted; the select's own healthy path normalises the same detail to `''`.
- **Input that reveals it:** a `bdsChange` with `detail: undefined` bubbling from the rebuilt items list while a value is committed.
- **Observed current behavior:** `const next = typeof e.detail === 'string' ? e.detail : ''` runs before the commit, so the pick path commits `''` and emits `{ value: '' }` (`bds-search-bar.tsx:341`), matching `listenListMenu`'s `(eventDetail as string) || ''` in `bds-select`.
- **Recommended contract:** a non-string detail from either origin commits `''`, emits one `valueChange` with `''` and one `bdsSearch` with `{ value: '' }`, clears the field text, and closes the popover once.
- **Contract status:** confirmed
- **Why it matters:** the fix made a second origin reach this coercion; a later "read `detail` directly" refactor would put `undefined` into a `@Prop() value: string` without any type error at the call site.
- **Covered by:** `…events.spec.ts::Should commit an empty value when the items list reports a deselection with no detail`


