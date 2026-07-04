[32m18:56:25 (54045) INFO ProjectReader[39m Found 1 of 792 file(s) to be mutated.
[32m18:56:25 (54045) INFO Instrumenter[39m Instrumented 1 source file(s) with 452 mutant(s)
[32m18:56:25 (54045) INFO ConcurrencyTokenProvider[39m Creating 10 test runner process(es).
[32m18:56:26 (54045) INFO BroadcastReporter[39m Detected that current console does not support the "progress" reporter, downgrading to "progress-append-only" reporter
[32m18:56:26 (54045) INFO DryRunExecutor[39m Starting initial test run (jest test runner with "perTest" coverage analysis). This may take a while.
[32m18:56:31 (54045) INFO DryRunExecutor[39m Initial test run succeeded. Ran 69 tests in 4 seconds (net 1183 ms, overhead 3233 ms).
Mutation testing 4% (elapsed: <1m, remaining: ~3m) 103/452 tested (8 survived, 0 timed out)
Mutation testing 9% (elapsed: <1m, remaining: ~3m) 117/452 tested (17 survived, 0 timed out)
Mutation testing 17% (elapsed: <1m, remaining: ~2m) 134/452 tested (28 survived, 0 timed out)
Mutation testing 21% (elapsed: <1m, remaining: ~2m) 156/452 tested (46 survived, 0 timed out)
Mutation testing 24% (elapsed: <1m, remaining: ~2m) 177/452 tested (61 survived, 0 timed out)
Mutation testing 24% (elapsed: ~1m, remaining: ~3m) 198/452 tested (71 survived, 0 timed out)
Mutation testing 25% (elapsed: ~1m, remaining: ~3m) 218/452 tested (87 survived, 0 timed out)
Mutation testing 25% (elapsed: ~1m, remaining: ~3m) 242/452 tested (93 survived, 0 timed out)
Mutation testing 28% (elapsed: ~1m, remaining: ~3m) 259/452 tested (95 survived, 0 timed out)
Mutation testing 34% (elapsed: ~1m, remaining: ~3m) 280/452 tested (96 survived, 0 timed out)
Mutation testing 38% (elapsed: ~1m, remaining: ~2m) 293/452 tested (99 survived, 0 timed out)
Mutation testing 44% (elapsed: ~2m, remaining: ~2m) 310/452 tested (108 survived, 0 timed out)
Mutation testing 48% (elapsed: ~2m, remaining: ~2m) 320/452 tested (115 survived, 0 timed out)
Mutation testing 55% (elapsed: ~2m, remaining: ~1m) 337/452 tested (126 survived, 0 timed out)
Mutation testing 60% (elapsed: ~2m, remaining: ~1m) 355/452 tested (144 survived, 0 timed out)
Mutation testing 64% (elapsed: ~2m, remaining: ~1m) 366/452 tested (149 survived, 0 timed out)
Mutation testing 69% (elapsed: ~2m, remaining: ~1m) 378/452 tested (157 survived, 0 timed out)
Mutation testing 73% (elapsed: ~3m, remaining: ~1m) 390/452 tested (160 survived, 0 timed out)
Mutation testing 77% (elapsed: ~3m, remaining: <1m) 399/452 tested (165 survived, 0 timed out)
Mutation testing 81% (elapsed: ~3m, remaining: <1m) 410/452 tested (170 survived, 0 timed out)
Mutation testing 86% (elapsed: ~3m, remaining: <1m) 421/452 tested (181 survived, 0 timed out)
Mutation testing 91% (elapsed: ~3m, remaining: <1m) 432/452 tested (187 survived, 0 timed out)
Mutation testing 96% (elapsed: ~3m, remaining: <1m) 443/452 tested (191 survived, 0 timed out)

All tests
  bds-search-bar.a11y.spec.ts
    ✓ bds-search-bar — a11y Should set aria-label on the input matching the placeholder [line 28] (killed 11)
    ✓ bds-search-bar — a11y Should expose aria-expanded="true" on the host when expanded (default variant) [line 39] (killed 1)
    ✓ bds-search-bar — a11y Should expose aria-expanded="false" on the host when minimized [line 48] (killed 1)
    ~ bds-search-bar — a11y Should give the trigger button tabIndex 0 when collapsed and enabled [line 57] (covered 162)
    ✓ bds-search-bar — a11y Should mark the search icon as aria-hidden [line 68] (killed 1)
    ✓ bds-search-bar — a11y Should update aria-label when placeholder prop changes [line 79] (killed 1)
  bds-search-bar.basics.spec.ts
    ~ bds-search-bar — basics Should render the host element [line 28] (covered 166)
    ✓ bds-search-bar — basics Should apply the bds-search-bar base class to the host [line 36] (killed 1)
    ~ bds-search-bar — basics Should render an internal bds-select in "list" mode by default [line 45] (covered 166)
    ~ bds-search-bar — basics Should render a bds-text-field inside the select [line 55] (covered 166)
    ~ bds-search-bar — basics Should render the trigger bds-button inside the field prefix [line 65] (covered 166)
    ~ bds-search-bar — basics Should not render a bds-select when mode="search" [line 75] (covered 155)
    ✓ bds-search-bar — basics Should render a bds-text-field directly when mode="search" [line 85] (killed 2)
    ~ bds-search-bar — basics Should forward the placeholder prop to the internal text field [line 95] (covered 166)
    ~ bds-search-bar — basics Should reflect the value prop on the host [line 106] (covered 168)
    ~ bds-search-bar — basics Should set the input value to match the value prop after load [line 115] (covered 168)
    ~ bds-search-bar — basics Should default to variant="default" [line 126] (covered 166)
    ~ bds-search-bar — basics Should reflect variant="static" via attribute [line 135] (covered 168)
    ~ bds-search-bar — basics Should render the list slot content as bds-list-menu-item elements [line 144] (covered 165)
    ~ bds-search-bar — basics Should not render a spinner by default [line 161] (covered 166)
  bds-search-bar.events.spec.ts
    ✓ bds-search-bar — events Should emit valueChange when the input value changes [line 30] (killed 1)
    ✓ bds-search-bar — events Should emit bdsInput immediately in search mode without waiting for debounce [line 50] (killed 1)
    ✓ bds-search-bar — events Should emit bdsClear when the field clear button fires bdsClear [line 70] (killed 10)
    ✓ bds-search-bar — events Should emit bdsSearch when Enter is pressed on the input [line 89] (killed 7)
    ✓ bds-search-bar — events Should emit bdsSearch when a suggestion is selected from the list (bdsChange on select) [line 109] (killed 4)
    ~ bds-search-bar — events Should update value when a suggestion is selected from the list [line 135] (covered 178)
    ✓ bds-search-bar — events Should not emit bdsSearch on Enter when value is from a non-string select change [line 157] (killed 2)
    ✓ bds-search-bar — events Should expand the search bar when focus lands directly on the input while collapsed [line 178] (killed 11)
    ✓ bds-search-bar — events Should be a no-op when focus lands on the input for variant="static" [line 199] (killed 1)
    ✓ bds-search-bar — events Should apply the no-transition modifier class to the select when focus expands it instantly [line 217] (killed 1)
    ✓ bds-search-bar — events Should remove the no-transition modifier class after the transition-suppression window elapses [line 235] (killed 3)
    ✓ bds-search-bar — events Should not apply the no-transition modifier class when the trigger button itself is focused [line 261] (killed 12)
  bds-search-bar.methods.spec.ts
    ✓ bds-search-bar — public methods Should expand the search bar when openSearchBar() is called [line 32] (killed 13)
    ✓ bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static" [line 45] (killed 1)
    ✓ bds-search-bar — public methods Should collapse the search bar when close() is called [line 59] (killed 7)
    ~ bds-search-bar — public methods Should be a no-op when close() is called on variant="static" [line 72] (covered 174)
    ~ bds-search-bar — public methods Should be a no-op when openSearchBar() is called while already open [line 85] (covered 172)
    ~ bds-search-bar — public methods Should be a no-op when close() is called while already collapsed [line 98] (covered 169)
    ✓ bds-search-bar — public methods Should reset the field container scrollLeft when closeSearchBar() is called [line 111] (killed 14)
    ✓ bds-search-bar — public methods Should not touch the field container scrollLeft when closeSearchBar() is a no-op on variant="static" [line 129] (killed 3)
    ✓ bds-search-bar — public methods Should resolve openSearchBar() immediately in mode="search", where no bds-select exists to transition [line 146] (killed 6)
    ✓ bds-search-bar — public methods Should resolve closeSearchBar() immediately in mode="search", where no bds-select exists to transition [line 160] (killed 1)
    ✓ bds-search-bar — public methods Should resolve openSearchBar() via the width transitionend listener, not the 250ms fallback timer [line 174] (killed 10)
    ✓ bds-search-bar — public methods Should ignore a transitionend for a property other than width while waiting to open [line 211] (killed 1)
    ✓ bds-search-bar — public methods Should not focus the input when openSearchBar() is a no-op because it is already open [line 247] (killed 2)
    ~ bds-search-bar — public methods Should not focus the input when openSearchBar() is a no-op on variant="static" [line 264] (covered 174)
    ✓ bds-search-bar — public methods Should still no-op openSearchBar() on variant="static" even with an inconsistent internal isOpen=false [line 281] (killed 1)
    ✓ bds-search-bar — public methods Should be a no-op when expandInstantly() is invoked directly while already open [line 305] (killed 3)
    ✓ bds-search-bar — public methods Should be a no-op when expandInstantly() is invoked directly on variant="static", even with an inconsistent internal isOpen=false [line 321] (killed 1)
  bds-search-bar.variants.spec.ts
    ✓ bds-search-bar — variants Should apply disabled class on the host when disabled prop is set [line 20] (killed 2)
    ~ bds-search-bar — variants Should disable the internal text field when disabled prop is set [line 29] (covered 167)
    ~ bds-search-bar — variants Should disable the trigger button when disabled prop is set [line 40] (covered 167)
    ~ bds-search-bar — variants Should apply loading class on the host when loading prop is set [line 51] (covered 166)
    ✓ bds-search-bar — variants Should not render a spinner when loading is set but the bar is not open and not asynch [line 60] (killed 2)
    ✓ bds-search-bar — variants Should render exactly one visible spinner in mode="list" when loading, async and expanded [line 70] (killed 5)
    ✓ bds-search-bar — variants Should render exactly one spinner with no wrapper div in mode="search" [line 84] (killed 10)
    ~ bds-search-bar — variants Should start collapsed when minimized is set on variant="default" [line 97] (covered 162)
    ~ bds-search-bar — variants Should start expanded when minimized is not set on variant="default" [line 106] (covered 166)
    ~ bds-search-bar — variants Should always be expanded when variant="static", ignoring minimized [line 115] (covered 168)
    ✓ bds-search-bar — variants Should apply the expanded modifier class to the select when open [line 125] (killed 2)
    ~ bds-search-bar — variants Should not apply the expanded modifier class to the select when minimized [line 136] (covered 162)
    ✓ bds-search-bar — variants Should apply the static modifier class to the select when variant="static" [line 147] (killed 2)
    ~ bds-search-bar — variants Should render the text field as outline variant when expanded [line 158] (covered 166)
    ✓ bds-search-bar — variants Should render the text field as plain variant when minimized [line 169] (killed 1)
    ✓ bds-search-bar — variants Should apply a custom width via the customWidth prop as a CSS variable [line 180] (killed 4)
    ✓ bds-search-bar — variants Should not set the custom width CSS variable when customWidth is empty [line 189] (killed 1)
    ✓ bds-search-bar — variants Should apply the expanded modifier class to the host on variant="default" when not minimized [line 198] (killed 1)
    ✓ bds-search-bar — variants Should not apply the expanded modifier class to the host on variant="default" when minimized [line 207] (killed 2)
    ~ bds-search-bar — variants Should apply the expanded modifier class to the host on variant="static" even when minimized [line 216] (covered 168)

[NoCoverage] BlockStatement
src/components/forms/bds-search-bar/bds-search-bar.tsx:145:28
-     onModeDepsChange(): void {
-       this.syncInputAccessibility();
-     }
+     onModeDepsChange(): void {}

[NoCoverage] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:155:40
-       updateElementAttr(this.bdsInputEl, 'value', next);
+       updateElementAttr(this.bdsInputEl, "", next);

[NoCoverage] ObjectLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:196:35
-         this.bdsInputDebounced.emit({ value });
+         this.bdsInputDebounced.emit({});

[NoCoverage] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:207:67
-       if (items === null || items === undefined || list === null || list === undefined) return;
+       if (items === null || items === undefined || list === null || false) return;

[NoCoverage] EqualityOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:207:67
-       if (items === null || items === undefined || list === null || list === undefined) return;
+       if (items === null || items === undefined || list === null || list !== undefined) return;

[NoCoverage] MethodExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:209:24
-       const normalized = query.toLowerCase();
+       const normalized = query.toUpperCase();

[NoCoverage] BlockStatement
src/components/forms/bds-search-bar/bds-search-bar.tsx:211:27
-       items.forEach(item => {
-         const value = item.getAttribute('value') ?? '';
-         const text = (item.textContent ?? '').toLowerCase();
-         const isVisible = text.includes(normalized) || value.toLowerCase().includes(normalized);
-         updateElementAttr(item, 'tabindex', isVisible ? '0' : '-1');
-         updateElementProp(item, 'hidden', !isVisible);
-       });
+       items.forEach(item => {});

[NoCoverage] LogicalOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:212:21
-         const value = item.getAttribute('value') ?? '';
+         const value = item.getAttribute('value') && '';

[NoCoverage] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:212:39
-         const value = item.getAttribute('value') ?? '';
+         const value = item.getAttribute("") ?? '';

[NoCoverage] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:212:51
-         const value = item.getAttribute('value') ?? '';
+         const value = item.getAttribute('value') ?? "Stryker was here!";

[NoCoverage] MethodExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:213:20
-         const text = (item.textContent ?? '').toLowerCase();
+         const text = (item.textContent ?? '').toUpperCase();

[NoCoverage] LogicalOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:213:21
-         const text = (item.textContent ?? '').toLowerCase();
+         const text = (item.textContent && '').toLowerCase();

[NoCoverage] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:213:41
-         const text = (item.textContent ?? '').toLowerCase();
+         const text = (item.textContent ?? "Stryker was here!").toLowerCase();

[NoCoverage] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:214:25
-         const isVisible = text.includes(normalized) || value.toLowerCase().includes(normalized);
+         const isVisible = true;

[NoCoverage] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:214:25
-         const isVisible = text.includes(normalized) || value.toLowerCase().includes(normalized);
+         const isVisible = false;

[NoCoverage] LogicalOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:214:25
-         const isVisible = text.includes(normalized) || value.toLowerCase().includes(normalized);
+         const isVisible = text.includes(normalized) && value.toLowerCase().includes(normalized);

[NoCoverage] MethodExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:214:54
-         const isVisible = text.includes(normalized) || value.toLowerCase().includes(normalized);
+         const isVisible = text.includes(normalized) || value.toUpperCase().includes(normalized);

[NoCoverage] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:216:31
-         updateElementAttr(item, 'tabindex', isVisible ? '0' : '-1');
+         updateElementAttr(item, "", isVisible ? '0' : '-1');

[NoCoverage] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:216:55
-         updateElementAttr(item, 'tabindex', isVisible ? '0' : '-1');
+         updateElementAttr(item, 'tabindex', isVisible ? "" : '-1');

[NoCoverage] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:216:61
-         updateElementAttr(item, 'tabindex', isVisible ? '0' : '-1');
+         updateElementAttr(item, 'tabindex', isVisible ? '0' : "");

[NoCoverage] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:217:31
-         updateElementProp(item, 'hidden', !isVisible);
+         updateElementProp(item, "", !isVisible);

[NoCoverage] BooleanLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:217:41
-         updateElementProp(item, 'hidden', !isVisible);
+         updateElementProp(item, 'hidden', isVisible);

[NoCoverage] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:220:48
-       const visibleItems = list.querySelectorAll('bds-list-menu-item:not([hidden])');
+       const visibleItems = list.querySelectorAll("");

[NoCoverage] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:221:29
-       updateElementProp(list, 'empty', visibleItems.length === 0);
+       updateElementProp(list, "", visibleItems.length === 0);

[NoCoverage] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:221:38
-       updateElementProp(list, 'empty', visibleItems.length === 0);
+       updateElementProp(list, 'empty', true);

[NoCoverage] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:221:38
-       updateElementProp(list, 'empty', visibleItems.length === 0);
+       updateElementProp(list, 'empty', false);

[NoCoverage] EqualityOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:221:38
-       updateElementProp(list, 'empty', visibleItems.length === 0);
+       updateElementProp(list, 'empty', visibleItems.length !== 0);

[NoCoverage] BlockStatement
src/components/forms/bds-search-bar/bds-search-bar.tsx:249:51
-     private listenKeydown = (event: Event): void => {
-       const keyEvent = event as KeyboardEvent;
-       if (keyEvent.key === KEYBOARD.Enter) {
-         this.emitSearch();
-       } else if (keyEvent.key === KEYBOARD.Escape) {
-         keyEvent.stopPropagation();
-         void this.bdsPopover?.closePopover();
-         if (this.value !== '') {
-           this.handleFieldClear();
-           updateElementAttr(this.bdsInputEl, 'value', '');
-         } else if (this.minimized && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
-           void this.closeSearchBar();
-         }
-       }
-     };
+     private listenKeydown = (event: Event): void => {};

[NoCoverage] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:251:9
-       if (keyEvent.key === KEYBOARD.Enter) {
+       if (true) {

[NoCoverage] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:251:9
-       if (keyEvent.key === KEYBOARD.Enter) {
+       if (false) {

[NoCoverage] EqualityOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:251:9
-       if (keyEvent.key === KEYBOARD.Enter) {
+       if (keyEvent.key !== KEYBOARD.Enter) {

[NoCoverage] BlockStatement
src/components/forms/bds-search-bar/bds-search-bar.tsx:251:42
-       if (keyEvent.key === KEYBOARD.Enter) {
-         this.emitSearch();
-       } else if (keyEvent.key === KEYBOARD.Escape) {
+       if (keyEvent.key === KEYBOARD.Enter) {} else if (keyEvent.key === KEYBOARD.Escape) {

[NoCoverage] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:253:16
-       } else if (keyEvent.key === KEYBOARD.Escape) {
+       } else if (true) {

[NoCoverage] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:253:16
-       } else if (keyEvent.key === KEYBOARD.Escape) {
+       } else if (false) {

[NoCoverage] EqualityOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:253:16
-       } else if (keyEvent.key === KEYBOARD.Escape) {
+       } else if (keyEvent.key !== KEYBOARD.Escape) {

[NoCoverage] BlockStatement
src/components/forms/bds-search-bar/bds-search-bar.tsx:253:50
-       } else if (keyEvent.key === KEYBOARD.Escape) {
-         keyEvent.stopPropagation();
-         void this.bdsPopover?.closePopover();
-         if (this.value !== '') {
-           this.handleFieldClear();
-           updateElementAttr(this.bdsInputEl, 'value', '');
-         } else if (this.minimized && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
-           void this.closeSearchBar();
-         }
-       }
+       } else if (keyEvent.key === KEYBOARD.Escape) {}

[NoCoverage] OptionalChaining
src/components/forms/bds-search-bar/bds-search-bar.tsx:255:12
-         void this.bdsPopover?.closePopover();
+         void this.bdsPopover.closePopover();

[NoCoverage] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:256:11
-         if (this.value !== '') {
+         if (true) {

[NoCoverage] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:256:11
-         if (this.value !== '') {
+         if (false) {

[NoCoverage] EqualityOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:256:11
-         if (this.value !== '') {
+         if (this.value === '') {

[NoCoverage] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:256:26
-         if (this.value !== '') {
+         if (this.value !== "Stryker was here!") {

[NoCoverage] BlockStatement
src/components/forms/bds-search-bar/bds-search-bar.tsx:256:30
-         if (this.value !== '') {
-           this.handleFieldClear();
-           updateElementAttr(this.bdsInputEl, 'value', '');
-         } else if (this.minimized && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
+         if (this.value !== '') {} else if (this.minimized && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {

[NoCoverage] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:258:44
-           updateElementAttr(this.bdsInputEl, 'value', '');
+           updateElementAttr(this.bdsInputEl, "", '');

[NoCoverage] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:258:53
-           updateElementAttr(this.bdsInputEl, 'value', '');
+           updateElementAttr(this.bdsInputEl, 'value', "Stryker was here!");

[NoCoverage] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:259:18
-         } else if (this.minimized && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
+         } else if (true) {

[NoCoverage] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:259:18
-         } else if (this.minimized && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
+         } else if (false) {

[NoCoverage] LogicalOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:259:18
-         } else if (this.minimized && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
+         } else if (this.minimized || this.variant !== SEARCH_BAR_VARIANTS.STATIC) {

[NoCoverage] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:259:36
-         } else if (this.minimized && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
+         } else if (this.minimized && true) {

[NoCoverage] EqualityOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:259:36
-         } else if (this.minimized && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
+         } else if (this.minimized && this.variant === SEARCH_BAR_VARIANTS.STATIC) {

[NoCoverage] BlockStatement
src/components/forms/bds-search-bar/bds-search-bar.tsx:259:81
-         } else if (this.minimized && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
-           void this.closeSearchBar();
-         }
+         } else if (this.minimized && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {}

[NoCoverage] BlockStatement
src/components/forms/bds-search-bar/bds-search-bar.tsx:268:59
-     private handleDocumentPointerDown = (e: Event): void => {
-       const path = e.composedPath();
-       this.isSelecting = path.some(el => {
-         return (
-           el instanceof HTMLElement &&
-           (el.tagName === VALID_ELEMENTS.LIST_MENU_ITEM ||
-             el.tagName === VALID_ELEMENTS.LIST_MENU ||
-             el.tagName === VALID_ELEMENTS.POPOVER ||
-             el.classList.contains('bds-search-bar__trigger'))
-         );
-       });
-     };
+     private handleDocumentPointerDown = (e: Event): void => {};

[NoCoverage] MethodExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:271:24
-       this.isSelecting = path.some(el => {
-         return (
-           el instanceof HTMLElement &&
-           (el.tagName === VALID_ELEMENTS.LIST_MENU_ITEM ||
-             el.tagName === VALID_ELEMENTS.LIST_MENU ||
-             el.tagName === VALID_ELEMENTS.POPOVER ||
-             el.classList.contains('bds-search-bar__trigger'))
-         );
-       });
+       this.isSelecting = path.every(el => {
+     return el instanceof HTMLElement && (el.tagName === VALID_ELEMENTS.LIST_MENU_ITEM || el.tagName === VALID_ELEMENTS.LIST_MENU || el.tagName === VALID_ELEMENTS.POPOVER || el.classList.contains('bds-search-bar__trigger'));
+   });

[NoCoverage] BlockStatement
src/components/forms/bds-search-bar/bds-search-bar.tsx:271:40
-       this.isSelecting = path.some(el => {
-         return (
-           el instanceof HTMLElement &&
-           (el.tagName === VALID_ELEMENTS.LIST_MENU_ITEM ||
-             el.tagName === VALID_ELEMENTS.LIST_MENU ||
-             el.tagName === VALID_ELEMENTS.POPOVER ||
-             el.classList.contains('bds-search-bar__trigger'))
-         );
-       });
+       this.isSelecting = path.some(el => {});

[NoCoverage] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:273:9
-           el instanceof HTMLElement &&
-           (el.tagName === VALID_ELEMENTS.LIST_MENU_ITEM ||
-             el.tagName === VALID_ELEMENTS.LIST_MENU ||
-             el.tagName === VALID_ELEMENTS.POPOVER ||
-             el.classList.contains('bds-search-bar__trigger'))
+           true

[NoCoverage] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:273:9
-           el instanceof HTMLElement &&
-           (el.tagName === VALID_ELEMENTS.LIST_MENU_ITEM ||
-             el.tagName === VALID_ELEMENTS.LIST_MENU ||
-             el.tagName === VALID_ELEMENTS.POPOVER ||
-             el.classList.contains('bds-search-bar__trigger'))
+           false

[NoCoverage] LogicalOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:273:9
-           el instanceof HTMLElement &&
-           (el.tagName === VALID_ELEMENTS.LIST_MENU_ITEM ||
-             el.tagName === VALID_ELEMENTS.LIST_MENU ||
-             el.tagName === VALID_ELEMENTS.POPOVER ||
-             el.classList.contains('bds-search-bar__trigger'))
+           el instanceof HTMLElement || el.tagName === VALID_ELEMENTS.LIST_MENU_ITEM || el.tagName === VALID_ELEMENTS.LIST_MENU || el.tagName === VALID_ELEMENTS.POPOVER || el.classList.contains('bds-search-bar__trigger')

[NoCoverage] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:274:10
-           (el.tagName === VALID_ELEMENTS.LIST_MENU_ITEM ||
-             el.tagName === VALID_ELEMENTS.LIST_MENU ||
-             el.tagName === VALID_ELEMENTS.POPOVER ||
-             el.classList.contains('bds-search-bar__trigger'))
+           (true)

[NoCoverage] LogicalOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:274:10
-           (el.tagName === VALID_ELEMENTS.LIST_MENU_ITEM ||
-             el.tagName === VALID_ELEMENTS.LIST_MENU ||
-             el.tagName === VALID_ELEMENTS.POPOVER ||
-             el.classList.contains('bds-search-bar__trigger'))
+           ((el.tagName === VALID_ELEMENTS.LIST_MENU_ITEM || el.tagName === VALID_ELEMENTS.LIST_MENU || el.tagName === VALID_ELEMENTS.POPOVER) && el.classList.contains('bds-search-bar__trigger'))

[NoCoverage] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:274:10
-           (el.tagName === VALID_ELEMENTS.LIST_MENU_ITEM ||
-             el.tagName === VALID_ELEMENTS.LIST_MENU ||
-             el.tagName === VALID_ELEMENTS.POPOVER ||
+           (false ||

[NoCoverage] LogicalOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:274:10
-           (el.tagName === VALID_ELEMENTS.LIST_MENU_ITEM ||
-             el.tagName === VALID_ELEMENTS.LIST_MENU ||
-             el.tagName === VALID_ELEMENTS.POPOVER ||
+           ((el.tagName === VALID_ELEMENTS.LIST_MENU_ITEM || el.tagName === VALID_ELEMENTS.LIST_MENU) && el.tagName === VALID_ELEMENTS.POPOVER ||

[NoCoverage] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:274:10
-           (el.tagName === VALID_ELEMENTS.LIST_MENU_ITEM ||
-             el.tagName === VALID_ELEMENTS.LIST_MENU ||
+           (false ||

[NoCoverage] LogicalOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:274:10
-           (el.tagName === VALID_ELEMENTS.LIST_MENU_ITEM ||
-             el.tagName === VALID_ELEMENTS.LIST_MENU ||
+           (el.tagName === VALID_ELEMENTS.LIST_MENU_ITEM && el.tagName === VALID_ELEMENTS.LIST_MENU ||

[NoCoverage] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:274:10
-           (el.tagName === VALID_ELEMENTS.LIST_MENU_ITEM ||
+           (false ||

[NoCoverage] EqualityOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:274:10
-           (el.tagName === VALID_ELEMENTS.LIST_MENU_ITEM ||
+           (el.tagName !== VALID_ELEMENTS.LIST_MENU_ITEM ||

[NoCoverage] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:275:11
-             el.tagName === VALID_ELEMENTS.LIST_MENU ||
+             false ||

[NoCoverage] EqualityOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:275:11
-             el.tagName === VALID_ELEMENTS.LIST_MENU ||
+             el.tagName !== VALID_ELEMENTS.LIST_MENU ||

[NoCoverage] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:276:11
-             el.tagName === VALID_ELEMENTS.POPOVER ||
+             false ||

[NoCoverage] EqualityOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:276:11
-             el.tagName === VALID_ELEMENTS.POPOVER ||
+             el.tagName !== VALID_ELEMENTS.POPOVER ||

[NoCoverage] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:277:33
-             el.classList.contains('bds-search-bar__trigger'))
+             el.classList.contains(""))

[NoCoverage] BlockStatement
src/components/forms/bds-search-bar/bds-search-bar.tsx:305:27
-       if (this.isSelecting) {
-         this.isSelecting = false;
-         return;
-       }
+       if (this.isSelecting) {}

[NoCoverage] BooleanLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:306:26
-         this.isSelecting = false;
+         this.isSelecting = true;

[NoCoverage] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:310:48
-       if (this.value === '' && this.minimized && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
+       if (this.value === '' && this.minimized && true) {

[NoCoverage] EqualityOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:310:48
-       if (this.value === '' && this.minimized && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
+       if (this.value === '' && this.minimized && this.variant === SEARCH_BAR_VARIANTS.STATIC) {

[NoCoverage] BlockStatement
src/components/forms/bds-search-bar/bds-search-bar.tsx:310:93
-       if (this.value === '' && this.minimized && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
-         void this.closeSearchBar();
-       }
+       if (this.value === '' && this.minimized && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {}

[NoCoverage] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:352:48
-       if (this.value === '' && this.minimized && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
+       if (this.value === '' && this.minimized && true) {

[NoCoverage] EqualityOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:352:48
-       if (this.value === '' && this.minimized && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
+       if (this.value === '' && this.minimized && this.variant === SEARCH_BAR_VARIANTS.STATIC) {

[NoCoverage] BlockStatement
src/components/forms/bds-search-bar/bds-search-bar.tsx:352:93
-       if (this.value === '' && this.minimized && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
-         void this.closeSearchBar();
-         return;
-       }
+       if (this.value === '' && this.minimized && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {}

[NoCoverage] BlockStatement
src/components/forms/bds-search-bar/bds-search-bar.tsx:373:70
-       if (this.variant !== SEARCH_BAR_VARIANTS.STATIC && !this.isOpen) {
-         void this.openSearchBar();
-         return;
-       }
+       if (this.variant !== SEARCH_BAR_VARIANTS.STATIC && !this.isOpen) {}

[NoCoverage] UnaryOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:565:28
-       return this.disabled ? -1 : 0;
+       return this.disabled ? +1 : 0;

[NoCoverage] BlockStatement
src/components/forms/bds-search-bar/bds-search-bar.tsx:586:21
-       if (this.async) {
-         return this.debounceDelay > 0 ? this.debounceDelay : 300;
-       }
+       if (this.async) {}

[NoCoverage] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:587:14
-         return this.debounceDelay > 0 ? this.debounceDelay : 300;
+         return true ? this.debounceDelay : 300;

[NoCoverage] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:587:14
-         return this.debounceDelay > 0 ? this.debounceDelay : 300;
+         return false ? this.debounceDelay : 300;

[NoCoverage] EqualityOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:587:14
-         return this.debounceDelay > 0 ? this.debounceDelay : 300;
+         return this.debounceDelay >= 0 ? this.debounceDelay : 300;

[NoCoverage] EqualityOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:587:14
-         return this.debounceDelay > 0 ? this.debounceDelay : 300;
+         return this.debounceDelay <= 0 ? this.debounceDelay : 300;

[NoCoverage] BlockStatement
src/components/forms/bds-search-bar/bds-search-bar.tsx:606:35
-     private removeListeners(): void {
-       removeElementListener(this.bdsInputEl, 'keydown', this.listenKeydown);
-       removeElementListener(this.bdsTriggerBtnEl, 'focus', this.handleTriggerFocus);
-       document.removeEventListener('pointerdown', this.handleDocumentPointerDown, true);
-     }
+     private removeListeners(): void {}

[NoCoverage] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:607:44
-       removeElementListener(this.bdsInputEl, 'keydown', this.listenKeydown);
+       removeElementListener(this.bdsInputEl, "", this.listenKeydown);

[NoCoverage] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:608:49
-       removeElementListener(this.bdsTriggerBtnEl, 'focus', this.handleTriggerFocus);
+       removeElementListener(this.bdsTriggerBtnEl, "", this.handleTriggerFocus);

[NoCoverage] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:609:34
-       document.removeEventListener('pointerdown', this.handleDocumentPointerDown, true);
+       document.removeEventListener("", this.handleDocumentPointerDown, true);

[NoCoverage] BooleanLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:609:81
-       document.removeEventListener('pointerdown', this.handleDocumentPointerDown, true);
+       document.removeEventListener('pointerdown', this.handleDocumentPointerDown, false);

[NoCoverage] BlockStatement
src/components/forms/bds-search-bar/bds-search-bar.tsx:628:32
-     disconnectedCallback(): void {
-       if (this.debounceTimer !== null) clearTimeout(this.debounceTimer);
-       this.virtualScroll.detach();
-       this.removeListeners();
-     }
+     disconnectedCallback(): void {}

[NoCoverage] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:629:9
-       if (this.debounceTimer !== null) clearTimeout(this.debounceTimer);
+       if (true) clearTimeout(this.debounceTimer);

[NoCoverage] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:629:9
-       if (this.debounceTimer !== null) clearTimeout(this.debounceTimer);
+       if (false) clearTimeout(this.debounceTimer);

[NoCoverage] EqualityOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:629:9
-       if (this.debounceTimer !== null) clearTimeout(this.debounceTimer);
+       if (this.debounceTimer === null) clearTimeout(this.debounceTimer);

[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:81:48
-     @Prop() readonly searchButtonLabel: string = 'Search';
+     @Prop() readonly searchButtonLabel: string = "";
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] BooleanLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:75:56
-     @Prop({ reflect: true }) readonly loading: boolean = false;
+     @Prop({ reflect: true }) readonly loading: boolean = true;
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:69:65
-     @Prop({ reflect: true }) readonly variant: SearchBarVariant = 'default';
+     @Prop({ reflect: true }) readonly variant: SearchBarVariant = "";
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:63:42
-     @Prop() readonly placeholder: string = '';
+     @Prop() readonly placeholder: string = "Stryker was here!";
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:60:59
-     @Prop({ mutable: true, reflect: true }) value: string = '';
+     @Prop({ mutable: true, reflect: true }) value: string = "Stryker was here!";
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] BooleanLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:50:25
-     private isSelecting = false;
+     private isSelecting = true;
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] BooleanLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:52:31
-     private skipNextValueSync = false;
+     private skipNextValueSync = true;
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:66:35
-     @Prop() readonly name: string = '';
+     @Prop() readonly name: string = "Stryker was here!";
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:93:59
-     @Prop({ reflect: true }) readonly mode: SearchBarMode = 'list';
+     @Prop({ reflect: true }) readonly mode: SearchBarMode = "";
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] BooleanLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:90:37
-     @Prop() readonly async: boolean = false;
+     @Prop() readonly async: boolean = true;
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] BlockStatement
src/components/forms/bds-search-bar/bds-search-bar.tsx:130:27
-     checkPropValues(): void {
-       validatePropValue(
-         Object.values(SEARCH_BAR_VARIANTS) as SearchBarVariant[],
-         SEARCH_BAR_VARIANTS.DEFAULT,
-         this.el as HTMLElement,
-         'variant',
-       );
-       validatePropValue(
-         Object.values(SEARCH_BAR_MODE) as SearchBarMode[],
-         SEARCH_BAR_MODE.LIST,
-         this.el as HTMLElement,
-         'mode',
-       );
-     }
+     checkPropValues(): void {}
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:135:7
-         'variant',
+         "",
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] BooleanLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:102:39
-     @State() private focused: boolean = false;
+     @State() private focused: boolean = true;
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:141:7
-         'mode',
+         "",
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] BooleanLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:99:38
-     @State() private isOpen: boolean = false;
+     @State() private isOpen: boolean = true;
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:168:9
-       if (this.bdsInputEl === null || this.bdsInputEl === undefined) return;
+       if (false) return;
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] LogicalOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:168:9
-       if (this.bdsInputEl === null || this.bdsInputEl === undefined) return;
+       if (this.bdsInputEl === null && this.bdsInputEl === undefined) return;
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:168:9
-       if (this.bdsInputEl === null || this.bdsInputEl === undefined) return;
+       if (false || this.bdsInputEl === undefined) return;
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:168:37
-       if (this.bdsInputEl === null || this.bdsInputEl === undefined) return;
+       if (this.bdsInputEl === null || false) return;
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:170:40
-       updateElementAttr(this.bdsInputEl, 'type', 'search');
+       updateElementAttr(this.bdsInputEl, "", 'search');
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:170:48
-       updateElementAttr(this.bdsInputEl, 'type', 'search');
+       updateElementAttr(this.bdsInputEl, 'type', "");
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:171:40
-       updateElementAttr(this.bdsInputEl, 'role', 'searchbox');
+       updateElementAttr(this.bdsInputEl, "", 'searchbox');
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:173:9
-       if (this.mode === SEARCH_BAR_MODE.LIST) {
+       if (true) {
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:171:48
-       updateElementAttr(this.bdsInputEl, 'role', 'searchbox');
+       updateElementAttr(this.bdsInputEl, 'role', "");
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] BlockStatement
src/components/forms/bds-search-bar/bds-search-bar.tsx:173:45
-       if (this.mode === SEARCH_BAR_MODE.LIST) {
-         updateElementAttr(this.bdsInputEl, 'aria-autocomplete', 'list');
-         updateElementAttr(this.bdsInputEl, 'aria-controls', this.bdsListMenuEl?.id ?? '');
-       } else {
+       if (this.mode === SEARCH_BAR_MODE.LIST) {} else {
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 60 more tests!


[Survived] EqualityOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:173:9
-       if (this.mode === SEARCH_BAR_MODE.LIST) {
+       if (this.mode !== SEARCH_BAR_MODE.LIST) {
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:173:9
-       if (this.mode === SEARCH_BAR_MODE.LIST) {
+       if (false) {
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:174:42
-         updateElementAttr(this.bdsInputEl, 'aria-autocomplete', 'list');
+         updateElementAttr(this.bdsInputEl, "", 'list');
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 60 more tests!


[Survived] BlockStatement
src/components/forms/bds-search-bar/bds-search-bar.tsx:176:12
-       } else {
-         updateElementAttr(this.bdsInputEl, 'aria-autocomplete', 'none');
-         this.bdsInputEl.removeAttribute('aria-controls');
-       }
+       } else {}
Tests ran:
    bds-search-bar — public methods Should resolve openSearchBar() immediately in mode="search", where no bds-select exists to transition
    bds-search-bar — public methods Should resolve closeSearchBar() immediately in mode="search", where no bds-select exists to transition
    bds-search-bar — events Should emit bdsInput immediately in search mode without waiting for debounce
  and 3 more tests!


[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:177:63
-         updateElementAttr(this.bdsInputEl, 'aria-autocomplete', 'none');
+         updateElementAttr(this.bdsInputEl, 'aria-autocomplete', "");
Tests ran:
    bds-search-bar — public methods Should resolve openSearchBar() immediately in mode="search", where no bds-select exists to transition
    bds-search-bar — public methods Should resolve closeSearchBar() immediately in mode="search", where no bds-select exists to transition
    bds-search-bar — events Should emit bdsInput immediately in search mode without waiting for debounce
  and 3 more tests!


[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:177:42
-         updateElementAttr(this.bdsInputEl, 'aria-autocomplete', 'none');
+         updateElementAttr(this.bdsInputEl, "", 'none');
Tests ran:
    bds-search-bar — public methods Should resolve openSearchBar() immediately in mode="search", where no bds-select exists to transition
    bds-search-bar — public methods Should resolve closeSearchBar() immediately in mode="search", where no bds-select exists to transition
    bds-search-bar — events Should emit bdsInput immediately in search mode without waiting for debounce
  and 3 more tests!


[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:175:42
-         updateElementAttr(this.bdsInputEl, 'aria-controls', this.bdsListMenuEl?.id ?? '');
+         updateElementAttr(this.bdsInputEl, "", this.bdsListMenuEl?.id ?? '');
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 60 more tests!


[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:178:39
-         this.bdsInputEl.removeAttribute('aria-controls');
+         this.bdsInputEl.removeAttribute("");
Tests ran:
    bds-search-bar — public methods Should resolve openSearchBar() immediately in mode="search", where no bds-select exists to transition
    bds-search-bar — public methods Should resolve closeSearchBar() immediately in mode="search", where no bds-select exists to transition
    bds-search-bar — events Should emit bdsInput immediately in search mode without waiting for debounce
  and 3 more tests!


[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:174:63
-         updateElementAttr(this.bdsInputEl, 'aria-autocomplete', 'list');
+         updateElementAttr(this.bdsInputEl, 'aria-autocomplete', "");
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 60 more tests!


[Survived] LogicalOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:175:59
-         updateElementAttr(this.bdsInputEl, 'aria-controls', this.bdsListMenuEl?.id ?? '');
+         updateElementAttr(this.bdsInputEl, 'aria-controls', this.bdsListMenuEl?.id && '');
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 60 more tests!


[Survived] BlockStatement
src/components/forms/bds-search-bar/bds-search-bar.tsx:185:50
-     private scheduleDebounced(value: string): void {
-       if (this.debounceTimer !== null) clearTimeout(this.debounceTimer);
-       this.debounceTimer = setTimeout(() => {
-         this.debounceTimer = null;
-         if (this.mode === SEARCH_BAR_MODE.LIST) {
-           this.searchOwnData(value);
-           this.value = value;
-           this.virtualScroll.refresh();
-           return;
-         }
-         this.bdsInputDebounced.emit({ value });
-       }, this.effectiveDebounceDelay);
-     }
+     private scheduleDebounced(value: string): void {}
Tests ran:
    bds-search-bar — events Should emit valueChange when the input value changes


[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:175:85
-         updateElementAttr(this.bdsInputEl, 'aria-controls', this.bdsListMenuEl?.id ?? '');
+         updateElementAttr(this.bdsInputEl, 'aria-controls', this.bdsListMenuEl?.id ?? "Stryker was here!");
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 57 more tests!


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:186:9
-       if (this.debounceTimer !== null) clearTimeout(this.debounceTimer);
+       if (true) clearTimeout(this.debounceTimer);
Tests ran:
    bds-search-bar — events Should emit valueChange when the input value changes


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:186:9
-       if (this.debounceTimer !== null) clearTimeout(this.debounceTimer);
+       if (false) clearTimeout(this.debounceTimer);
Tests ran:
    bds-search-bar — events Should emit valueChange when the input value changes


[Survived] EqualityOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:186:9
-       if (this.debounceTimer !== null) clearTimeout(this.debounceTimer);
+       if (this.debounceTimer === null) clearTimeout(this.debounceTimer);
Tests ran:
    bds-search-bar — events Should emit valueChange when the input value changes


[Survived] OptionalChaining
src/components/forms/bds-search-bar/bds-search-bar.tsx:238:23
-       const container = this.bdsFieldEl?.querySelector<HTMLElement>('.bds-text-field__container');
+       const container = this.bdsFieldEl.querySelector<HTMLElement>('.bds-text-field__container');
Tests ran:
    bds-search-bar — public methods Should collapse the search bar when close() is called
    bds-search-bar — public methods Should reset the field container scrollLeft when closeSearchBar() is called
    bds-search-bar — public methods Should resolve closeSearchBar() immediately in mode="search", where no bds-select exists to transition


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:239:9
-       if (container !== null && container !== undefined) container.scrollLeft = 0;
+       if (true) container.scrollLeft = 0;
Tests ran:
    bds-search-bar — public methods Should collapse the search bar when close() is called
    bds-search-bar — public methods Should reset the field container scrollLeft when closeSearchBar() is called
    bds-search-bar — public methods Should resolve closeSearchBar() immediately in mode="search", where no bds-select exists to transition


[Survived] BlockStatement
src/components/forms/bds-search-bar/bds-search-bar.tsx:227:39
-     private loadDefaultTextFieldProps() {
-       updateElementProp(this.bdsFieldEl, 'iconRight', '');
-     }
+     private loadDefaultTextFieldProps() {}
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:228:40
-       updateElementProp(this.bdsFieldEl, 'iconRight', '');
+       updateElementProp(this.bdsFieldEl, "", '');
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:239:9
-       if (container !== null && container !== undefined) container.scrollLeft = 0;
+       if (true && container !== undefined) container.scrollLeft = 0;
Tests ran:
    bds-search-bar — public methods Should collapse the search bar when close() is called
    bds-search-bar — public methods Should reset the field container scrollLeft when closeSearchBar() is called
    bds-search-bar — public methods Should resolve closeSearchBar() immediately in mode="search", where no bds-select exists to transition


[Survived] LogicalOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:239:9
-       if (container !== null && container !== undefined) container.scrollLeft = 0;
+       if (container !== null || container !== undefined) container.scrollLeft = 0;
Tests ran:
    bds-search-bar — public methods Should collapse the search bar when close() is called
    bds-search-bar — public methods Should reset the field container scrollLeft when closeSearchBar() is called
    bds-search-bar — public methods Should resolve closeSearchBar() immediately in mode="search", where no bds-select exists to transition


[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:228:53
-       updateElementProp(this.bdsFieldEl, 'iconRight', '');
+       updateElementProp(this.bdsFieldEl, 'iconRight', "Stryker was here!");
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:239:31
-       if (container !== null && container !== undefined) container.scrollLeft = 0;
+       if (container !== null && true) container.scrollLeft = 0;
Tests ran:
    bds-search-bar — public methods Should collapse the search bar when close() is called
    bds-search-bar — public methods Should reset the field container scrollLeft when closeSearchBar() is called
    bds-search-bar — public methods Should resolve closeSearchBar() immediately in mode="search", where no bds-select exists to transition


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:295:25
-       if (!this.isOpen && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
+       if (!this.isOpen && true) {
Tests ran:
    bds-search-bar — events Should expand the search bar when focus lands directly on the input while collapsed
    bds-search-bar — events Should apply the no-transition modifier class to the select when focus expands it instantly
    bds-search-bar — events Should remove the no-transition modifier class after the transition-suppression window elapses


[Survived] BooleanLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:303:20
-       this.focused = false;
+       this.focused = true;
Tests ran:
    bds-search-bar — public methods Should collapse the search bar when close() is called
    bds-search-bar — public methods Should reset the field container scrollLeft when closeSearchBar() is called
    bds-search-bar — public methods Should resolve closeSearchBar() immediately in mode="search", where no bds-select exists to transition


[Survived] BlockStatement
src/components/forms/bds-search-bar/bds-search-bar.tsx:302:36
-     private handleBlur = (): void => {
-       this.focused = false;
-       if (this.isSelecting) {
-         this.isSelecting = false;
-         return;
-       }
-       if (this.value === '' && this.minimized && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
-         void this.closeSearchBar();
-       }
-     };
+     private handleBlur = (): void => {};
Tests ran:
    bds-search-bar — public methods Should collapse the search bar when close() is called
    bds-search-bar — public methods Should reset the field container scrollLeft when closeSearchBar() is called
    bds-search-bar — public methods Should resolve closeSearchBar() immediately in mode="search", where no bds-select exists to transition


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:305:9
-       if (this.isSelecting) {
+       if (true) {
Tests ran:
    bds-search-bar — public methods Should collapse the search bar when close() is called
    bds-search-bar — public methods Should reset the field container scrollLeft when closeSearchBar() is called
    bds-search-bar — public methods Should resolve closeSearchBar() immediately in mode="search", where no bds-select exists to transition


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:305:9
-       if (this.isSelecting) {
+       if (false) {
Tests ran:
    bds-search-bar — public methods Should collapse the search bar when close() is called
    bds-search-bar — public methods Should reset the field container scrollLeft when closeSearchBar() is called
    bds-search-bar — public methods Should resolve closeSearchBar() immediately in mode="search", where no bds-select exists to transition


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:310:9
-       if (this.value === '' && this.minimized && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
+       if (true) {
Tests ran:
    bds-search-bar — public methods Should collapse the search bar when close() is called
    bds-search-bar — public methods Should reset the field container scrollLeft when closeSearchBar() is called
    bds-search-bar — public methods Should resolve closeSearchBar() immediately in mode="search", where no bds-select exists to transition


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:310:9
-       if (this.value === '' && this.minimized && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
+       if (false) {
Tests ran:
    bds-search-bar — public methods Should collapse the search bar when close() is called
    bds-search-bar — public methods Should reset the field container scrollLeft when closeSearchBar() is called
    bds-search-bar — public methods Should resolve closeSearchBar() immediately in mode="search", where no bds-select exists to transition


[Survived] LogicalOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:310:9
-       if (this.value === '' && this.minimized && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
+       if (this.value === '' && this.minimized || this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
Tests ran:
    bds-search-bar — public methods Should collapse the search bar when close() is called
    bds-search-bar — public methods Should reset the field container scrollLeft when closeSearchBar() is called
    bds-search-bar — public methods Should resolve closeSearchBar() immediately in mode="search", where no bds-select exists to transition


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:310:9
-       if (this.value === '' && this.minimized && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
+       if (true && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
Tests ran:
    bds-search-bar — public methods Should collapse the search bar when close() is called
    bds-search-bar — public methods Should reset the field container scrollLeft when closeSearchBar() is called
    bds-search-bar — public methods Should resolve closeSearchBar() immediately in mode="search", where no bds-select exists to transition


[Survived] LogicalOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:310:9
-       if (this.value === '' && this.minimized && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
+       if (this.value === '' || this.minimized && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
Tests ran:
    bds-search-bar — public methods Should collapse the search bar when close() is called
    bds-search-bar — public methods Should reset the field container scrollLeft when closeSearchBar() is called
    bds-search-bar — public methods Should resolve closeSearchBar() immediately in mode="search", where no bds-select exists to transition


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:310:9
-       if (this.value === '' && this.minimized && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
+       if (true && this.minimized && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
Tests ran:
    bds-search-bar — public methods Should collapse the search bar when close() is called
    bds-search-bar — public methods Should reset the field container scrollLeft when closeSearchBar() is called
    bds-search-bar — public methods Should resolve closeSearchBar() immediately in mode="search", where no bds-select exists to transition


[Survived] EqualityOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:310:9
-       if (this.value === '' && this.minimized && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
+       if (this.value !== '' && this.minimized && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
Tests ran:
    bds-search-bar — public methods Should collapse the search bar when close() is called
    bds-search-bar — public methods Should reset the field container scrollLeft when closeSearchBar() is called
    bds-search-bar — public methods Should resolve closeSearchBar() immediately in mode="search", where no bds-select exists to transition


[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:310:24
-       if (this.value === '' && this.minimized && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
+       if (this.value === "Stryker was here!" && this.minimized && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
Tests ran:
    bds-search-bar — public methods Should collapse the search bar when close() is called
    bds-search-bar — public methods Should reset the field container scrollLeft when closeSearchBar() is called
    bds-search-bar — public methods Should resolve closeSearchBar() immediately in mode="search", where no bds-select exists to transition


[Survived] BooleanLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:320:30
-       this.skipNextValueSync = true;
+       this.skipNextValueSync = false;
Tests ran:
    bds-search-bar — events Should emit bdsClear when the field clear button fires bdsClear
    bds-search-bar — events Should emit bdsSearch when a suggestion is selected from the list (bdsChange on select)
    bds-search-bar — events Should update value when a suggestion is selected from the list
  and 1 more test!


[Survived] BooleanLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:338:30
-       this.skipNextValueSync = true;
+       this.skipNextValueSync = false;
Tests ran:
    bds-search-bar — events Should emit valueChange when the input value changes
    bds-search-bar — events Should emit bdsInput immediately in search mode without waiting for debounce


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:340:9
-       if (this.mode === SEARCH_BAR_MODE.LIST) {
+       if (true) {
Tests ran:
    bds-search-bar — events Should emit valueChange when the input value changes
    bds-search-bar — events Should emit bdsInput immediately in search mode without waiting for debounce


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:340:9
-       if (this.mode === SEARCH_BAR_MODE.LIST) {
+       if (false) {
Tests ran:
    bds-search-bar — events Should emit valueChange when the input value changes
    bds-search-bar — events Should emit bdsInput immediately in search mode without waiting for debounce


[Survived] EqualityOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:340:9
-       if (this.mode === SEARCH_BAR_MODE.LIST) {
+       if (this.mode !== SEARCH_BAR_MODE.LIST) {
Tests ran:
    bds-search-bar — events Should emit valueChange when the input value changes
    bds-search-bar — events Should emit bdsInput immediately in search mode without waiting for debounce


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:343:11
-         if (this.async) this.scheduleDebounced(newValue);
+         if (true) this.scheduleDebounced(newValue);
Tests ran:
    bds-search-bar — events Should emit bdsInput immediately in search mode without waiting for debounce


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:343:11
-         if (this.async) this.scheduleDebounced(newValue);
+         if (false) this.scheduleDebounced(newValue);
Tests ran:
    bds-search-bar — events Should emit bdsInput immediately in search mode without waiting for debounce


[Survived] BlockStatement
src/components/forms/bds-search-bar/bds-search-bar.tsx:342:12
-       } else {
-         if (this.async) this.scheduleDebounced(newValue);
-       }
+       } else {}
Tests ran:
    bds-search-bar — events Should emit bdsInput immediately in search mode without waiting for debounce


[Survived] BlockStatement
src/components/forms/bds-search-bar/bds-search-bar.tsx:340:45
-       if (this.mode === SEARCH_BAR_MODE.LIST) {
-         this.scheduleDebounced(newValue);
-       } else {
+       if (this.mode === SEARCH_BAR_MODE.LIST) {} else {
Tests ran:
    bds-search-bar — events Should emit valueChange when the input value changes


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:352:9
-       if (this.value === '' && this.minimized && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
+       if (false) {
Tests ran:
    bds-search-bar — events Should emit bdsClear when the field clear button fires bdsClear


[Survived] LogicalOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:352:9
-       if (this.value === '' && this.minimized && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
+       if (this.value === '' || this.minimized && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
Tests ran:
    bds-search-bar — events Should emit bdsClear when the field clear button fires bdsClear


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:352:9
-       if (this.value === '' && this.minimized && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
+       if (true && this.minimized && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
Tests ran:
    bds-search-bar — events Should emit bdsClear when the field clear button fires bdsClear


[Survived] EqualityOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:352:9
-       if (this.value === '' && this.minimized && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
+       if (this.value !== '' && this.minimized && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
Tests ran:
    bds-search-bar — events Should emit bdsClear when the field clear button fires bdsClear


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:357:9
-       if (this.debounceTimer !== null) clearTimeout(this.debounceTimer);
+       if (false) clearTimeout(this.debounceTimer);
Tests ran:
    bds-search-bar — events Should emit bdsClear when the field clear button fires bdsClear


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:357:9
-       if (this.debounceTimer !== null) clearTimeout(this.debounceTimer);
+       if (true) clearTimeout(this.debounceTimer);
Tests ran:
    bds-search-bar — events Should emit bdsClear when the field clear button fires bdsClear


[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:352:24
-       if (this.value === '' && this.minimized && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
+       if (this.value === "Stryker was here!" && this.minimized && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
Tests ran:
    bds-search-bar — events Should emit bdsClear when the field clear button fires bdsClear


[Survived] EqualityOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:357:9
-       if (this.debounceTimer !== null) clearTimeout(this.debounceTimer);
+       if (this.debounceTimer === null) clearTimeout(this.debounceTimer);
Tests ran:
    bds-search-bar — events Should emit bdsClear when the field clear button fires bdsClear


[Survived] BooleanLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:358:30
-       this.skipNextValueSync = true;
+       this.skipNextValueSync = false;
Tests ran:
    bds-search-bar — events Should emit bdsClear when the field clear button fires bdsClear


[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:360:24
-       this.searchOwnData('');
+       this.searchOwnData("Stryker was here!");
Tests ran:
    bds-search-bar — events Should emit bdsClear when the field clear button fires bdsClear


[Survived] ObjectLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:366:24
-       this.bdsInput.emit({ value: '' });
+       this.bdsInput.emit({});
Tests ran:
    bds-search-bar — events Should emit bdsClear when the field clear button fires bdsClear


[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:363:18
-       this.value = '';
+       this.value = "Stryker was here!";
Tests ran:
    bds-search-bar — events Should emit bdsClear when the field clear button fires bdsClear


[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:367:27
-       this.valueChange.emit('');
+       this.valueChange.emit("Stryker was here!");
Tests ran:
    bds-search-bar — events Should emit bdsClear when the field clear button fires bdsClear


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:373:9
-       if (this.variant !== SEARCH_BAR_VARIANTS.STATIC && !this.isOpen) {
+       if (false) {
Tests ran:
    bds-search-bar — events Should emit bdsSearch when Enter is pressed on the input


[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:366:33
-       this.bdsInput.emit({ value: '' });
+       this.bdsInput.emit({ value: "Stryker was here!" });
Tests ran:
    bds-search-bar — events Should emit bdsClear when the field clear button fires bdsClear


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:373:9
-       if (this.variant !== SEARCH_BAR_VARIANTS.STATIC && !this.isOpen) {
+       if (true && !this.isOpen) {
Tests ran:
    bds-search-bar — events Should emit bdsSearch when Enter is pressed on the input


[Survived] EqualityOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:373:9
-       if (this.variant !== SEARCH_BAR_VARIANTS.STATIC && !this.isOpen) {
+       if (this.variant === SEARCH_BAR_VARIANTS.STATIC && !this.isOpen) {
Tests ran:
    bds-search-bar — events Should emit bdsSearch when Enter is pressed on the input


[Survived] OptionalChaining
src/components/forms/bds-search-bar/bds-search-bar.tsx:377:27
-       if (this.isOpen) void this.bdsPopover?.closePopover();
+       if (this.isOpen) void this.bdsPopover.closePopover();
Tests ran:
    bds-search-bar — events Should emit bdsSearch when Enter is pressed on the input


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:377:9
-       if (this.isOpen) void this.bdsPopover?.closePopover();
+       if (true) void this.bdsPopover?.closePopover();
Tests ran:
    bds-search-bar — events Should emit bdsSearch when Enter is pressed on the input


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:377:9
-       if (this.isOpen) void this.bdsPopover?.closePopover();
+       if (false) void this.bdsPopover?.closePopover();
Tests ran:
    bds-search-bar — events Should emit bdsSearch when Enter is pressed on the input


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:384:9
-       if (!this.isOpen && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
+       if (true) {
Tests ran:
    bds-search-bar — events Should not apply the no-transition modifier class when the trigger button itself is focused


[Survived] LogicalOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:384:9
-       if (!this.isOpen && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
+       if (!this.isOpen || this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
Tests ran:
    bds-search-bar — events Should not apply the no-transition modifier class when the trigger button itself is focused


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:384:25
-       if (!this.isOpen && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
+       if (!this.isOpen && true) {
Tests ran:
    bds-search-bar — events Should not apply the no-transition modifier class when the trigger button itself is focused


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:412:30
-         if (target === null || target === undefined) {
+         if (target === null || false) {
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should collapse the search bar when close() is called
    bds-search-bar — public methods Should reset the field container scrollLeft when closeSearchBar() is called
  and 3 more tests!


[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:418:36
-           target.removeEventListener('transitionend', onEnd);
+           target.removeEventListener("", onEnd);
Tests ran:
    bds-search-bar — public methods Should resolve openSearchBar() via the width transitionend listener, not the 250ms fallback timer
    bds-search-bar — public methods Should ignore a transitionend for a property other than width while waiting to open


[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:440:32
-           variant={this.isOpen ? 'outline' : 'plain'}
+           variant={this.isOpen ? "" : 'plain'}
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 56 more tests!


[Survived] OptionalChaining
src/components/forms/bds-search-bar/bds-search-bar.tsx:488:5
-       this.bdsInputEl?.blur();
+       this.bdsInputEl.blur();
Tests ran:
    bds-search-bar — public methods Should collapse the search bar when close() is called
    bds-search-bar — public methods Should reset the field container scrollLeft when closeSearchBar() is called
    bds-search-bar — public methods Should resolve closeSearchBar() immediately in mode="search", where no bds-select exists to transition


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:502:41
-         'bds-search-bar__select--static': this.variant === SEARCH_BAR_VARIANTS.STATIC,
+         'bds-search-bar__select--static': true,
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 60 more tests!


[Survived] BooleanLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:500:33
-         'bds-search-bar__select': true,
+         'bds-search-bar__select': false,
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 60 more tests!


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:515:35
-         'bds-search-bar--expanded': this.variant === SEARCH_BAR_VARIANTS.STATIC || this.isOpen,
+         'bds-search-bar--expanded': false || this.isOpen,
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:520:12
-       return this.customWidth !== '' ? { '--bds-search-bar-width': this.customWidth } : undefined;
+       return true ? { '--bds-search-bar-width': this.customWidth } : undefined;
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:520:33
-       return this.customWidth !== '' ? { '--bds-search-bar-width': this.customWidth } : undefined;
+       return this.customWidth !== "Stryker was here!" ? { '--bds-search-bar-width': this.customWidth } : undefined;
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] BlockStatement
src/components/forms/bds-search-bar/bds-search-bar.tsx:531:58
-     private get bdsPopover(): HTMLBdsPopoverElement | null {
-       if (this.el !== null) {
-         return (this.el as HTMLElement).querySelector('bds-popover');
-       }
-       return null;
-     }
+     private get bdsPopover(): HTMLBdsPopoverElement | null {}
Tests ran:
    bds-search-bar — public methods Should collapse the search bar when close() is called
    bds-search-bar — public methods Should reset the field container scrollLeft when closeSearchBar() is called
    bds-search-bar — public methods Should resolve closeSearchBar() immediately in mode="search", where no bds-select exists to transition
  and 1 more test!


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:532:9
-       if (this.el !== null) {
+       if (false) {
Tests ran:
    bds-search-bar — public methods Should collapse the search bar when close() is called
    bds-search-bar — public methods Should reset the field container scrollLeft when closeSearchBar() is called
    bds-search-bar — public methods Should resolve closeSearchBar() immediately in mode="search", where no bds-select exists to transition
  and 1 more test!


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:532:9
-       if (this.el !== null) {
+       if (true) {
Tests ran:
    bds-search-bar — public methods Should collapse the search bar when close() is called
    bds-search-bar — public methods Should reset the field container scrollLeft when closeSearchBar() is called
    bds-search-bar — public methods Should resolve closeSearchBar() immediately in mode="search", where no bds-select exists to transition
  and 1 more test!


[Survived] BlockStatement
src/components/forms/bds-search-bar/bds-search-bar.tsx:532:27
-       if (this.el !== null) {
-         return (this.el as HTMLElement).querySelector('bds-popover');
-       }
+       if (this.el !== null) {}
Tests ran:
    bds-search-bar — public methods Should collapse the search bar when close() is called
    bds-search-bar — public methods Should reset the field container scrollLeft when closeSearchBar() is called
    bds-search-bar — public methods Should resolve closeSearchBar() immediately in mode="search", where no bds-select exists to transition
  and 1 more test!


[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:533:53
-         return (this.el as HTMLElement).querySelector('bds-popover');
+         return (this.el as HTMLElement).querySelector("");
Tests ran:
    bds-search-bar — public methods Should collapse the search bar when close() is called
    bds-search-bar — public methods Should reset the field container scrollLeft when closeSearchBar() is called
    bds-search-bar — public methods Should resolve closeSearchBar() immediately in mode="search", where no bds-select exists to transition
  and 1 more test!


[Survived] EqualityOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:532:9
-       if (this.el !== null) {
+       if (this.el === null) {
Tests ran:
    bds-search-bar — public methods Should collapse the search bar when close() is called
    bds-search-bar — public methods Should reset the field container scrollLeft when closeSearchBar() is called
    bds-search-bar — public methods Should resolve closeSearchBar() immediately in mode="search", where no bds-select exists to transition
  and 1 more test!


[Survived] BlockStatement
src/components/forms/bds-search-bar/bds-search-bar.tsx:546:62
-     private get bdsListMenuEl(): HTMLBdsListMenuElement | null {
-       return this.el?.querySelector('.bds-list-menu__content') ?? null;
-     }
+     private get bdsListMenuEl(): HTMLBdsListMenuElement | null {}
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] LogicalOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:547:12
-       return this.el?.querySelector('.bds-list-menu__content') ?? null;
+       return this.el?.querySelector('.bds-list-menu__content') && null;
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] OptionalChaining
src/components/forms/bds-search-bar/bds-search-bar.tsx:547:12
-       return this.el?.querySelector('.bds-list-menu__content') ?? null;
+       return this.el.querySelector('.bds-list-menu__content') ?? null;
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:547:35
-       return this.el?.querySelector('.bds-list-menu__content') ?? null;
+       return this.el?.querySelector("") ?? null;
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] OptionalChaining
src/components/forms/bds-search-bar/bds-search-bar.tsx:551:12
-       return this.bdsFieldEl?.querySelector('bds-button') ?? null;
+       return this.bdsFieldEl.querySelector('bds-button') ?? null;
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:564:9
-       if (this.isOpen) return -1;
+       if (true) return -1;
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] BlockStatement
src/components/forms/bds-search-bar/bds-search-bar.tsx:563:41
-     private get triggerTabIndex(): number {
-       if (this.isOpen) return -1;
-       return this.disabled ? -1 : 0;
-     }
+     private get triggerTabIndex(): number {}
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:564:9
-       if (this.isOpen) return -1;
+       if (false) return -1;
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] UnaryOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:564:29
-       if (this.isOpen) return -1;
+       if (this.isOpen) return +1;
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 56 more tests!


[Survived] LogicalOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:571:12
-       return this.isOpen === true && this.loading === true && this.async;
+       return this.isOpen === true && this.loading === true || this.async;
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:571:12
-       return this.isOpen === true && this.loading === true && this.async;
+       return true && this.async;
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:571:12
-       return this.isOpen === true && this.loading === true && this.async;
+       return true;
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:571:12
-       return this.isOpen === true && this.loading === true && this.async;
+       return true && this.loading === true && this.async;
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] LogicalOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:571:12
-       return this.isOpen === true && this.loading === true && this.async;
+       return this.isOpen === true || this.loading === true && this.async;
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:571:36
-       return this.isOpen === true && this.loading === true && this.async;
+       return this.isOpen === true && true && this.async;
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 56 more tests!


[Survived] BlockStatement
src/components/forms/bds-search-bar/bds-search-bar.tsx:574:34
-     private get isEmpty(): boolean {
-       return this.value === '';
-     }
+     private get isEmpty(): boolean {}
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:575:27
-       return this.value === '';
+       return this.value === "Stryker was here!";
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:575:12
-       return this.value === '';
+       return true;
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] BlockStatement
src/components/forms/bds-search-bar/bds-search-bar.tsx:577:39
-     private get canShowClear(): boolean {
-       if (this.canShowLoader) return true;
-       if (this.variant === SEARCH_BAR_VARIANTS.STATIC && this.value === '') return true;
-       return false;
-     }
+     private get canShowClear(): boolean {}
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:575:12
-       return this.value === '';
+       return false;
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] EqualityOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:575:12
-       return this.value === '';
+       return this.value !== '';
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] BooleanLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:578:36
-       if (this.canShowLoader) return true;
+       if (this.canShowLoader) return false;
Tests ran:
    bds-search-bar — variants Should render exactly one visible spinner in mode="list" when loading, async and expanded
    bds-search-bar — variants Should render exactly one spinner with no wrapper div in mode="search"


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:578:9
-       if (this.canShowLoader) return true;
+       if (true) return true;
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:578:9
-       if (this.canShowLoader) return true;
+       if (false) return true;
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] EqualityOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:579:56
-       if (this.variant === SEARCH_BAR_VARIANTS.STATIC && this.value === '') return true;
+       if (this.variant === SEARCH_BAR_VARIANTS.STATIC && this.value !== '') return true;
Tests ran:
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should be a no-op when close() is called on variant="static"
    bds-search-bar — public methods Should not touch the field container scrollLeft when closeSearchBar() is a no-op on variant="static"
  and 8 more tests!


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:579:56
-       if (this.variant === SEARCH_BAR_VARIANTS.STATIC && this.value === '') return true;
+       if (this.variant === SEARCH_BAR_VARIANTS.STATIC && true) return true;
Tests ran:
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should be a no-op when close() is called on variant="static"
    bds-search-bar — public methods Should not touch the field container scrollLeft when closeSearchBar() is a no-op on variant="static"
  and 8 more tests!


[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:579:71
-       if (this.variant === SEARCH_BAR_VARIANTS.STATIC && this.value === '') return true;
+       if (this.variant === SEARCH_BAR_VARIANTS.STATIC && this.value === "Stryker was here!") return true;
Tests ran:
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should be a no-op when close() is called on variant="static"
    bds-search-bar — public methods Should not touch the field container scrollLeft when closeSearchBar() is a no-op on variant="static"
  and 8 more tests!


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:579:9
-       if (this.variant === SEARCH_BAR_VARIANTS.STATIC && this.value === '') return true;
+       if (true) return true;
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 64 more tests!


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:579:9
-       if (this.variant === SEARCH_BAR_VARIANTS.STATIC && this.value === '') return true;
+       if (false) return true;
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 64 more tests!


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:579:9
-       if (this.variant === SEARCH_BAR_VARIANTS.STATIC && this.value === '') return true;
+       if (true && this.value === '') return true;
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 64 more tests!


[Survived] LogicalOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:579:9
-       if (this.variant === SEARCH_BAR_VARIANTS.STATIC && this.value === '') return true;
+       if (this.variant === SEARCH_BAR_VARIANTS.STATIC || this.value === '') return true;
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 64 more tests!


[Survived] BooleanLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:579:82
-       if (this.variant === SEARCH_BAR_VARIANTS.STATIC && this.value === '') return true;
+       if (this.variant === SEARCH_BAR_VARIANTS.STATIC && this.value === '') return false;
Tests ran:
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should be a no-op when close() is called on variant="static"
    bds-search-bar — public methods Should not touch the field container scrollLeft when closeSearchBar() is a no-op on variant="static"
  and 8 more tests!


[Survived] EqualityOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:579:9
-       if (this.variant === SEARCH_BAR_VARIANTS.STATIC && this.value === '') return true;
+       if (this.variant !== SEARCH_BAR_VARIANTS.STATIC && this.value === '') return true;
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 64 more tests!


[Survived] BlockStatement
src/components/forms/bds-search-bar/bds-search-bar.tsx:585:48
-     private get effectiveDebounceDelay(): number {
-       if (this.async) {
-         return this.debounceDelay > 0 ? this.debounceDelay : 300;
-       }
-       return this.debounceDelay;
-     }
+     private get effectiveDebounceDelay(): number {}
Tests ran:
    bds-search-bar — events Should emit valueChange when the input value changes


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:586:9
-       if (this.async) {
+       if (true) {
Tests ran:
    bds-search-bar — events Should emit valueChange when the input value changes


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:586:9
-       if (this.async) {
+       if (false) {
Tests ran:
    bds-search-bar — events Should emit valueChange when the input value changes


[Survived] BooleanLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:580:12
-       return false;
+       return true;
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should collapse the search bar when close() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called while already open
  and 53 more tests!


[Survived] BooleanLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:601:78
-       document.addEventListener('pointerdown', this.handleDocumentPointerDown, true);
+       document.addEventListener('pointerdown', this.handleDocumentPointerDown, false);
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:599:41
-       addElementListener(this.bdsInputEl, 'keydown', this.listenKeydown);
+       addElementListener(this.bdsInputEl, "", this.listenKeydown);
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:601:31
-       document.addEventListener('pointerdown', this.handleDocumentPointerDown, true);
+       document.addEventListener("", this.handleDocumentPointerDown, true);
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:613:19
-       this.isOpen = this.variant === SEARCH_BAR_VARIANTS.STATIC || !this.minimized;
+       this.isOpen = false || !this.minimized;
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] BlockStatement
src/components/forms/bds-search-bar/bds-search-bar.tsx:619:28
-       if (this.value !== '') {
-         updateElementAttr(this.bdsInputEl, 'value', this.value);
-       }
+       if (this.value !== '') {}
Tests ran:
    bds-search-bar — events Should emit bdsClear when the field clear button fires bdsClear
    bds-search-bar — events Should emit bdsSearch when Enter is pressed on the input
    bds-search-bar — basics Should reflect the value prop on the host
  and 1 more test!


[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:620:42
-         updateElementAttr(this.bdsInputEl, 'value', this.value);
+         updateElementAttr(this.bdsInputEl, "", this.value);
Tests ran:
    bds-search-bar — events Should emit bdsClear when the field clear button fires bdsClear
    bds-search-bar — events Should emit bdsSearch when Enter is pressed on the input
    bds-search-bar — basics Should reflect the value prop on the host
  and 1 more test!


[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:619:24
-       if (this.value !== '') {
+       if (this.value !== "Stryker was here!") {
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] EqualityOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:619:9
-       if (this.value !== '') {
+       if (this.value === '') {
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:619:9
-       if (this.value !== '') {
+       if (true) {
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:619:9
-       if (this.value !== '') {
+       if (false) {
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] ObjectLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:622:51
-       this.virtualScroll.attach(this.bdsListMenuEl, {
-         itemSelector: 'bds-list-menu-item',
-         estimateSize: () => 28,
-         overscan: 2,
-       });
+       this.virtualScroll.attach(this.bdsListMenuEl, {});
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:623:21
-         itemSelector: 'bds-list-menu-item',
+         itemSelector: "",
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] ArrowFunction
src/components/forms/bds-search-bar/bds-search-bar.tsx:624:21
-         estimateSize: () => 28,
+         estimateSize: () => undefined,
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:635:24
-       const isExpanded = this.variant === SEARCH_BAR_VARIANTS.STATIC || this.isOpen;
+       const isExpanded = false || this.isOpen;
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:644:40
-           aria-disabled={this.disabled ? 'true' : undefined}
+           aria-disabled={this.disabled ? "" : undefined}
Tests ran:
    bds-search-bar — variants Should apply disabled class on the host when disabled prop is set
    bds-search-bar — variants Should disable the internal text field when disabled prop is set
    bds-search-bar — variants Should disable the trigger button when disabled prop is set


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:643:24
-           aria-haspopup={this.mode === SEARCH_BAR_MODE.LIST ? 'listbox' : undefined}
+           aria-haspopup={true ? 'listbox' : undefined}
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:643:24
-           aria-haspopup={this.mode === SEARCH_BAR_MODE.LIST ? 'listbox' : undefined}
+           aria-haspopup={false ? 'listbox' : undefined}
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] EqualityOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:643:24
-           aria-haspopup={this.mode === SEARCH_BAR_MODE.LIST ? 'listbox' : undefined}
+           aria-haspopup={this.mode !== SEARCH_BAR_MODE.LIST ? 'listbox' : undefined}
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 66 more tests!


[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:643:61
-           aria-haspopup={this.mode === SEARCH_BAR_MODE.LIST ? 'listbox' : undefined}
+           aria-haspopup={this.mode === SEARCH_BAR_MODE.LIST ? "" : undefined}
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 60 more tests!


[Survived] BooleanLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:652:25
-               searchable={true}
+               searchable={false}
Tests ran:
    bds-search-bar — public methods Should expand the search bar when openSearchBar() is called
    bds-search-bar — public methods Should be a no-op when openSearchBar() is called on variant="static"
    bds-search-bar — public methods Should collapse the search bar when close() is called
  and 60 more tests!


[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:151:9
-       if (this.skipNextValueSync) {
+       if (true) {
Ran all tests for this mutant.

[Survived] BlockStatement
src/components/forms/bds-search-bar/bds-search-bar.tsx:150:37
-     onValueChange(next: string): void {
-       if (this.skipNextValueSync) {
-         this.skipNextValueSync = false;
-         return;
-       }
-       updateElementAttr(this.bdsInputEl, 'value', next);
-     }
+     onValueChange(next: string): void {}
Ran all tests for this mutant.

[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:151:9
-       if (this.skipNextValueSync) {
+       if (false) {
Ran all tests for this mutant.

[Survived] BooleanLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:152:32
-         this.skipNextValueSync = false;
+         this.skipNextValueSync = true;
Ran all tests for this mutant.

[Survived] BlockStatement
src/components/forms/bds-search-bar/bds-search-bar.tsx:151:33
-       if (this.skipNextValueSync) {
-         this.skipNextValueSync = false;
-         return;
-       }
+       if (this.skipNextValueSync) {}
Ran all tests for this mutant.

[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:190:11
-         if (this.mode === SEARCH_BAR_MODE.LIST) {
+         if (true) {
Ran all tests for this mutant.

[Survived] BlockStatement
src/components/forms/bds-search-bar/bds-search-bar.tsx:187:43
-       this.debounceTimer = setTimeout(() => {
-         this.debounceTimer = null;
-         if (this.mode === SEARCH_BAR_MODE.LIST) {
-           this.searchOwnData(value);
-           this.value = value;
-           this.virtualScroll.refresh();
-           return;
-         }
-         this.bdsInputDebounced.emit({ value });
-       }, this.effectiveDebounceDelay);
+       this.debounceTimer = setTimeout(() => {}, this.effectiveDebounceDelay);
Ran all tests for this mutant.

[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:190:11
-         if (this.mode === SEARCH_BAR_MODE.LIST) {
+         if (false) {
Ran all tests for this mutant.

[Survived] EqualityOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:190:11
-         if (this.mode === SEARCH_BAR_MODE.LIST) {
+         if (this.mode !== SEARCH_BAR_MODE.LIST) {
Ran all tests for this mutant.

[Survived] BlockStatement
src/components/forms/bds-search-bar/bds-search-bar.tsx:190:47
-         if (this.mode === SEARCH_BAR_MODE.LIST) {
-           this.searchOwnData(value);
-           this.value = value;
-           this.virtualScroll.refresh();
-           return;
-         }
+         if (this.mode === SEARCH_BAR_MODE.LIST) {}
Ran all tests for this mutant.

[Survived] BlockStatement
src/components/forms/bds-search-bar/bds-search-bar.tsx:203:46
-     private searchOwnData(query: string): void {
-       const items = this.bdsSelectEl?.querySelectorAll<HTMLBdsListMenuItemElement>('bds-list-menu-item');
-       const list = this.bdsSelectEl?.querySelector<HTMLBdsListMenuElement>('bds-list-menu');
-       if (items === null || items === undefined || list === null || list === undefined) return;
-       const normalized = query.toLowerCase();
-       items.forEach(item => {
-         const value = item.getAttribute('value') ?? '';
-         const text = (item.textContent ?? '').toLowerCase();
-         const isVisible = text.includes(normalized) || value.toLowerCase().includes(normalized);
-         updateElementAttr(item, 'tabindex', isVisible ? '0' : '-1');
-         updateElementProp(item, 'hidden', !isVisible);
-       });
-       const visibleItems = list.querySelectorAll('bds-list-menu-item:not([hidden])');
-       updateElementProp(list, 'empty', visibleItems.length === 0);
-     }
+     private searchOwnData(query: string): void {}
Ran all tests for this mutant.

[Survived] OptionalChaining
src/components/forms/bds-search-bar/bds-search-bar.tsx:204:19
-       const items = this.bdsSelectEl?.querySelectorAll<HTMLBdsListMenuItemElement>('bds-list-menu-item');
+       const items = this.bdsSelectEl.querySelectorAll<HTMLBdsListMenuItemElement>('bds-list-menu-item');
Ran all tests for this mutant.

[Survived] OptionalChaining
src/components/forms/bds-search-bar/bds-search-bar.tsx:205:18
-       const list = this.bdsSelectEl?.querySelector<HTMLBdsListMenuElement>('bds-list-menu');
+       const list = this.bdsSelectEl.querySelector<HTMLBdsListMenuElement>('bds-list-menu');
Ran all tests for this mutant.

[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:205:74
-       const list = this.bdsSelectEl?.querySelector<HTMLBdsListMenuElement>('bds-list-menu');
+       const list = this.bdsSelectEl?.querySelector<HTMLBdsListMenuElement>("");
Ran all tests for this mutant.

[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:204:82
-       const items = this.bdsSelectEl?.querySelectorAll<HTMLBdsListMenuItemElement>('bds-list-menu-item');
+       const items = this.bdsSelectEl?.querySelectorAll<HTMLBdsListMenuItemElement>("");
Ran all tests for this mutant.

[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:207:9
-       if (items === null || items === undefined || list === null || list === undefined) return;
+       if (true) return;
Ran all tests for this mutant.

[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:207:9
-       if (items === null || items === undefined || list === null || list === undefined) return;
+       if (false || list === null || list === undefined) return;
Ran all tests for this mutant.

[Survived] LogicalOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:207:9
-       if (items === null || items === undefined || list === null || list === undefined) return;
+       if (items === null && items === undefined || list === null || list === undefined) return;
Ran all tests for this mutant.

[Survived] EqualityOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:207:9
-       if (items === null || items === undefined || list === null || list === undefined) return;
+       if (items !== null || items === undefined || list === null || list === undefined) return;
Ran all tests for this mutant.

[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:207:27
-       if (items === null || items === undefined || list === null || list === undefined) return;
+       if (items === null || false || list === null || list === undefined) return;
Ran all tests for this mutant.

[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:207:9
-       if (items === null || items === undefined || list === null || list === undefined) return;
+       if (false || items === undefined || list === null || list === undefined) return;
Ran all tests for this mutant.

[Survived] EqualityOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:207:27
-       if (items === null || items === undefined || list === null || list === undefined) return;
+       if (items === null || items !== undefined || list === null || list === undefined) return;
Ran all tests for this mutant.

[Survived] ConditionalExpression
src/components/forms/bds-search-bar/bds-search-bar.tsx:295:9
-       if (!this.isOpen && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
+       if (true) {
Ran all tests for this mutant.

[Survived] LogicalOperator
src/components/forms/bds-search-bar/bds-search-bar.tsx:295:9
-       if (!this.isOpen && this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
+       if (!this.isOpen || this.variant !== SEARCH_BAR_VARIANTS.STATIC) {
Ran all tests for this mutant.

[Survived] StringLiteral
src/components/forms/bds-search-bar/bds-search-bar.tsx:423:36
-           target.removeEventListener('transitionend', onEnd);
+           target.removeEventListener("", onEnd);
Ran all tests for this mutant.

[Survived] OptionalChaining
src/components/forms/bds-search-bar/bds-search-bar.tsx:481:5
-       this.bdsInputEl?.focus();
+       this.bdsInputEl.focus();
Ran all tests for this mutant.

[Survived] OptionalChaining
src/components/forms/bds-search-bar/bds-search-bar.tsx:539:12
-       return this.el?.querySelector('bds-text-field') ?? null;
+       return this.el.querySelector('bds-text-field') ?? null;
Ran all tests for this mutant.

[Survived] OptionalChaining
src/components/forms/bds-search-bar/bds-search-bar.tsx:543:12
-       return this.bdsFieldEl?.querySelector('input') ?? null;
+       return this.bdsFieldEl.querySelector('input') ?? null;
Ran all tests for this mutant.

Ran 32.09 tests per mutant on average.
--------------------|------------------|----------|-----------|------------|----------|----------|
                    | % Mutation score |          |           |            |          |          |
File                |  total | covered | # killed | # timeout | # survived | # no cov | # errors |
--------------------|--------|---------|----------|-----------|------------|----------|----------|
All files           |  36.73 |   46.24 |      166 |         0 |        193 |       93 |        0 |
 bds-search-bar.tsx |  36.73 |   46.24 |      166 |         0 |        193 |       93 |        0 |
--------------------|--------|---------|----------|-----------|------------|----------|----------|
[32m19:00:28 (54045) INFO HtmlReporter[39m Your report can be found at: file:///Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-search-bar/packages/boreal-web-components/reports/mutation/mutation.html
[32m19:00:28 (54045) INFO MutationTestExecutor[39m Done in 4 minutes and 2 seconds.
