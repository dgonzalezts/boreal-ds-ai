Using Node v22.21.1
[32m14:33:30 (20211) INFO ProjectReader[39m Found 1 of 792 file(s) to be mutated.
[32m14:33:30 (20211) INFO Instrumenter[39m Instrumented 1 source file(s) with 395 mutant(s)
[32m14:33:30 (20211) INFO ConcurrencyTokenProvider[39m Creating 2 test runner process(es).
[32m14:33:31 (20211) INFO BroadcastReporter[39m Detected that current console does not support the "progress" reporter, downgrading to "progress-append-only" reporter
[32m14:33:31 (20211) INFO DryRunExecutor[39m Starting initial test run (jest test runner with "perTest" coverage analysis). This may take a while.
[32m14:33:33 (20211) INFO DryRunExecutor[39m Initial test run succeeded. Ran 72 tests in 1 second (net 205 ms, overhead 1641 ms).
Mutation testing 9% (elapsed: <1m, remaining: ~1m) 30/395 tested (8 survived, 0 timed out)
Mutation testing 18% (elapsed: <1m, remaining: ~1m) 50/395 tested (21 survived, 0 timed out)
Mutation testing 20% (elapsed: <1m, remaining: ~1m) 75/395 tested (35 survived, 0 timed out)
Mutation testing 21% (elapsed: <1m, remaining: ~2m) 101/395 tested (37 survived, 0 timed out)
Mutation testing 22% (elapsed: <1m, remaining: ~2m) 126/395 tested (44 survived, 0 timed out)
Mutation testing 27% (elapsed: ~1m, remaining: ~2m) 145/395 tested (50 survived, 0 timed out)
Mutation testing 35% (elapsed: ~1m, remaining: ~2m) 159/395 tested (51 survived, 0 timed out)
Mutation testing 38% (elapsed: ~1m, remaining: ~2m) 179/395 tested (55 survived, 0 timed out)
Mutation testing 42% (elapsed: ~1m, remaining: ~2m) 203/395 tested (63 survived, 0 timed out)
Mutation testing 47% (elapsed: ~1m, remaining: ~1m) 218/395 tested (65 survived, 0 timed out)
Mutation testing 52% (elapsed: ~1m, remaining: ~1m) 231/395 tested (67 survived, 0 timed out)
Mutation testing 58% (elapsed: ~2m, remaining: ~1m) 243/395 tested (69 survived, 0 timed out)
Mutation testing 61% (elapsed: ~2m, remaining: ~1m) 256/395 tested (74 survived, 0 timed out)
Mutation testing 66% (elapsed: ~2m, remaining: ~1m) 267/395 tested (78 survived, 0 timed out)
Mutation testing 71% (elapsed: ~2m, remaining: <1m) 279/395 tested (88 survived, 0 timed out)
Mutation testing 74% (elapsed: ~2m, remaining: <1m) 294/395 tested (95 survived, 0 timed out)
Mutation testing 78% (elapsed: ~2m, remaining: <1m) 302/395 tested (101 survived, 0 timed out)
Mutation testing 82% (elapsed: ~3m, remaining: <1m) 321/395 tested (114 survived, 0 timed out)
Mutation testing 85% (elapsed: ~3m, remaining: <1m) 334/395 tested (114 survived, 0 timed out)
Mutation testing 89% (elapsed: ~3m, remaining: <1m) 348/395 tested (117 survived, 0 timed out)
Mutation testing 91% (elapsed: ~3m, remaining: <1m) 367/395 tested (124 survived, 0 timed out)
Mutation testing 93% (elapsed: ~3m, remaining: <1m) 382/395 tested (128 survived, 0 timed out)
Mutation testing 97% (elapsed: ~3m, remaining: <1m) 391/395 tested (129 survived, 0 timed out)

All tests
  bds-table.basics.spec.ts
    ~ bds-table basics renders a table element [line 16] (covered 88)
    ✓ bds-table basics renders one th per bds-table-column child with the correct label text [line 27] (killed 4)
    ~ bds-table basics renders one tbody tr per item in the data prop [line 46] (covered 152)
    ✓ bds-table basics renders cell text from the matching colKey property on each row object [line 65] (killed 2)
    ~ bds-table basics uses rowKey to identify rows and defaults to id [line 86] (covered 127)
    ✓ bds-table basics renders the empty state when data is empty and no slot content is present [line 101] (killed 4)
    ~ bds-table basics renders a custom emptyMessage when data is empty [line 118] (covered 127)
    ✓ bds-table basics does not render the default empty text when a slot="empty-state" element is present [line 135] (killed 2)
    ~ bds-table basics renders the paginator slotted element in the host [line 151] (covered 127)
    ~ bds-table basics re-renders with updated rows after the data prop changes [line 168] (covered 152)
    ✓ bds-table basics renders a th with a column icon when the icon prop is set on the column [line 194] (killed 4)
    ✓ bds-table basics renders a th info span when the info prop is set on the column [line 210] (killed 4)
    ✓ bds-table basics applies --bds-table-max-height custom property when maxHeight is set [line 226] (killed 3)
    ✓ bds-table basics does not apply --bds-table-max-height when maxHeight is not set [line 237] (killed 1)
    ✓ bds-table basics adds bds-table__wrapper--empty class when data is empty [line 248] (killed 7)
    ✓ bds-table basics removes bds-table__wrapper--empty class when data has rows [line 261] (killed 1)
    ✓ bds-table basics spreads inherited aria attributes onto the table element [line 281] (killed 2)
  bds-table.extras.spec.ts
    ✓ bds-table extras renders a pinnable column with a pin icon in its th-actions area [line 21] (killed 8)
    ✓ bds-table extras adds data-pinned to the th after clicking the pin icon on a pinnable column [line 37] (killed 4)
    ✓ bds-table extras removes data-pinned from the th after clicking the pin icon a second time (toggle off) [line 58] (killed 1)
    ✓ bds-table extras renders a cell formatted by a column formatter function [line 82] (killed 13)
    ✓ bds-table extras deselects all rows and emits bdsSelect with empty ids when select-all checkbox is clicked while all are selected [line 106] (killed 7)
    ✓ bds-table extras clears selection and emits bdsSelect with empty ids when the bds-tag close fires bdsClose [line 140] (killed 4)
    ✓ bds-table extras triggers sort via keyboard Enter on a sortable th [line 174] (killed 10)
    ~ bds-table extras adds data-sortable to the th but not data-pinned when sortable-only column is rendered [line 200] (covered 156)
    ~ bds-table extras does not throw when the element is disconnected from the DOM [line 216] (covered 158)
    ✓ bds-table extras updates columns when the MutationObserver callback fires after a new bds-table-column is appended [line 233] (killed 2)
    ✓ bds-table extras adds data-pin-last to the th of the last pinned column [line 272] (killed 15)
  bds-table.selection.spec.ts
    ✓ bds-table selection does not render a checkbox column in the header when selectable is false [line 22] (killed 2)
    ✓ bds-table selection renders a checkbox column in the header and each data row when selectable is true [line 41] (killed 9)
    ✓ bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange [line 61] (killed 4)
    ✓ bds-table selection returns selected row objects from getSelectedRows after selecting a row [line 89] (killed 3)
    ✓ bds-table selection returns an empty array from getSelectedRows after clearSelection is called [line 114] (killed 1)
    ✓ bds-table selection shows the header checkbox with aria-checked mixed when some but not all rows are selected [line 141] (killed 3)
    ✓ bds-table selection shows the header checkbox with aria-checked true when all rows are selected via the header checkbox [line 166] (killed 13)
    ✓ bds-table selection adds bds-table--has-selection class to the host when a row is selected [line 191] (killed 4)
    ✓ bds-table selection clears selection and removes bds-table--has-selection when data prop changes [line 214] (killed 6)
    ✓ bds-table selection adds bds-table__row--selected class to a selected row tr [line 244] (killed 1)
    ✓ bds-table selection includes the colspan of the checkbox column in the empty state td when selectable is true [line 269] (killed 6)
    ✓ bds-table selection seeds selectedRowIds from the selectedRows prop before the first render [line 287] (killed 3)
    ~ bds-table selection reflects externally-seeded selectedRows in getSelectedRows on initial load [line 310] (covered 172)
    ✓ bds-table selection updates selectedRowIds and checkbox rendering when the selectedRows prop changes after mount [line 334] (killed 1)
    ✓ bds-table selection emits selectedRowsChange alongside bdsSelect with matching ids when a row checkbox fires bdsChange [line 364] (killed 1)
    ✓ bds-table selection emits selectedRowsChange alongside bdsSelect with all row ids when the header checkbox selects all rows [line 398] (killed 2)
    ✓ bds-table selection emits selectedRowsChange with an empty array (and no bdsSelect) when clearSelection is called [line 432] (killed 1)
    ✓ bds-table selection does not pre-select any rows when the selectedRows prop is left at its default [line 466] (killed 1)
  bds-table.sort.spec.ts
    ~ bds-table sort does not add data-sortable or role=button to a non-sortable th [line 16] (covered 127)
    ✓ bds-table sort adds data-sortable and role=button to a sortable th [line 34] (killed 2)
    ✓ bds-table sort emits bdsSort with direction asc when a sortable th is clicked for the first time [line 51] (killed 5)
    ✓ bds-table sort emits bdsSort with direction desc when the same sortable th is clicked a second time [line 77] (killed 2)
    ~ bds-table sort emits bdsSort with direction none when the same sortable th is clicked a third time [line 104] (covered 179)
    ✓ bds-table sort emits bdsSort with asc when a different sortable column is clicked while one is active [line 133] (killed 1)
    ✓ bds-table sort orders tbody rows ascending by string value after the first click on a sortable th [line 161] (killed 11)
    ✓ bds-table sort reverses the tbody row order descending after the second click on a sortable th [line 186] (killed 2)
    ~ bds-table sort restores the original row order after the third click resets sort to none [line 213] (covered 214)
    ✓ bds-table sort renders a neutral sort icon class on a sortable but unsorted th [line 242] (killed 9)
    ✓ bds-table sort changes the sort icon to bds-icon-chevron-up after the column is sorted ascending [line 259] (killed 6)
    ✓ bds-table sort changes the sort icon to bds-icon-chevron-down after the column is sorted descending [line 281] (killed 1)
  bds-table.toolbar.spec.ts
    ✓ bds-table toolbar does not render the toolbar when no subheading and no toolbar slots are present [line 21] (killed 8)
    ✓ bds-table toolbar renders the toolbar when subheading is set [line 36] (killed 12)
    ✓ bds-table toolbar renders the subheading text inside the toolbar when subheading prop is set [line 51] (killed 5)
    ✓ bds-table toolbar renders the subheading icon when subheading-icon is set alongside subheading [line 68] (killed 5)
    ~ bds-table toolbar renders a bds-typography element in the toolbar heading area when subheading is set [line 84] (covered 149)
    ✓ bds-table toolbar renders the toolbar when only the search-bar slot is filled and no subheading is set [line 100] (killed 2)
    ✓ bds-table toolbar renders the toolbar when only the toolbar-actions slot is filled and no subheading is set [line 116] (killed 2)
    ✓ bds-table toolbar does not render the row actions zone when no rows are selected [line 132] (killed 5)
    ✓ bds-table toolbar renders the row actions zone when rows are selected via checkbox bdsChange [line 150] (killed 4)
    ✓ bds-table toolbar emits bdsFilter when the filter button fires bdsClick [line 173] (killed 3)
    ✓ bds-table toolbar emits bdsTableLayout when the column visibility button fires bdsClick [line 196] (killed 2)
    ✓ bds-table toolbar emits bdsDelete with selectedIds when the delete button fires bdsClick after row selection [line 219] (killed 5)
    ✓ bds-table toolbar emits bdsEdit with selectedIds when the edit button fires bdsClick after row selection [line 252] (killed 4)
    ~ bds-table toolbar renders the selectionLabel text in the count tag when rows are selected [line 285] (covered 218)

[NoCoverage] BlockStatement
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:178:93
-           this.el.querySelectorAll<HTMLElement>(`td[data-col-key="${colKey}"]`).forEach(td => {
-             td.style.left = `${offset}px`;
-           });
+           this.el.querySelectorAll<HTMLElement>(`td[data-col-key="${colKey}"]`).forEach(td => {});

[NoCoverage] StringLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:179:27
-             td.style.left = `${offset}px`;
+             td.style.left = ``;

[NoCoverage] ObjectLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:335:36
-       const pinnedProps = isPinned ? { 'data-pinned': true, ...(isLastPinned ? { 'data-pin-last': true } : {}) } : {};
+       const pinnedProps = isPinned ? {} : {};

[NoCoverage] BooleanLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:335:53
-       const pinnedProps = isPinned ? { 'data-pinned': true, ...(isLastPinned ? { 'data-pin-last': true } : {}) } : {};
+       const pinnedProps = isPinned ? { 'data-pinned': false, ...(isLastPinned ? { 'data-pin-last': true } : {}) } : {};

[NoCoverage] ObjectLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:335:78
-       const pinnedProps = isPinned ? { 'data-pinned': true, ...(isLastPinned ? { 'data-pin-last': true } : {}) } : {};
+       const pinnedProps = isPinned ? { 'data-pinned': true, ...(isLastPinned ? {} : {}) } : {};

[NoCoverage] BooleanLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:335:97
-       const pinnedProps = isPinned ? { 'data-pinned': true, ...(isLastPinned ? { 'data-pin-last': true } : {}) } : {};
+       const pinnedProps = isPinned ? { 'data-pinned': true, ...(isLastPinned ? { 'data-pin-last': false } : {}) } : {};

[NoCoverage] BlockStatement
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:395:27
-       if (col.colKey == '') {
-         this.logger.warn(
-           'bds-table',
-           'A <bds-table-column> is missing the required colKey prop. Data binding, sorting, and pinning will not work for this column.',
-         );
-       }
+       if (col.colKey == '') {}

[NoCoverage] StringLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:397:9
-           'bds-table',
+           "",

[NoCoverage] StringLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:398:9
-           'A <bds-table-column> is missing the required colKey prop. Data binding, sorting, and pinning will not work for this column.',
+           "",

[NoCoverage] ObjectLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:432:49
-         <th scope="col" style={col.width !== '' ? { width: col.width } : undefined} {...sortableProps} {...pinnedProps}>
+         <th scope="col" style={col.width !== '' ? {} : undefined} {...sortableProps} {...pinnedProps}>

[Survived] StringLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:57:38
-     @State() private sortKey: string = '';
+     @State() private sortKey: string = "Stryker was here!";
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 69 more tests!


[Survived] ArrayDeclaration
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:45:59
-     @State() private columns: HTMLBdsTableColumnElement[] = [];
+     @State() private columns: HTMLBdsTableColumnElement[] = ["Stryker was here"];
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 69 more tests!


[Survived] BooleanLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:72:39
-     @Prop() readonly loading: boolean = false;
+     @Prop() readonly loading: boolean = true;
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 69 more tests!


[Survived] StringLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:102:45
-     @Prop() readonly selectionLabel: string = 'items';
+     @Prop() readonly selectionLabel: string = "";
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 69 more tests!


[Survived] StringLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:112:45
-     @Prop() readonly subheadingIcon: string = '';
+     @Prop() readonly subheadingIcon: string = "Stryker was here!";
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 69 more tests!


[Survived] StringLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:117:42
-     @Prop() readonly tooltipText: string = '';
+     @Prop() readonly tooltipText: string = "Stryker was here!";
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 69 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:121:9
-       if (this.selectedRowIds.size > 0) {
+       if (true) {
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 26 more tests!


[Survived] EqualityOperator
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:121:9
-       if (this.selectedRowIds.size > 0) {
+       if (this.selectedRowIds.size >= 0) {
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 26 more tests!


[Survived] StringLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:157:74
-       this.inheritedAttributes = inheritAttributes(this.el, ['aria-label', 'aria-describedby']);
+       this.inheritedAttributes = inheritAttributes(this.el, ['aria-label', ""]);
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 69 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:160:9
-       if (this.selectedRows.length > 0) {
+       if (true) {
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 69 more tests!


[Survived] EqualityOperator
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:160:9
-       if (this.selectedRows.length > 0) {
+       if (this.selectedRows.length >= 0) {
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 69 more tests!


[Survived] BlockStatement
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:165:24
-     componentDidRender() {
-       let offset = 0;
-       if (this.selectable) {
-         const checkboxTh = this.el.querySelector<HTMLElement>('th.bds-table__th-checkbox');
-         if (checkboxTh !== null) offset = checkboxTh.offsetWidth;
-       }
-       const pinnedThs = Array.from(this.el.querySelectorAll<HTMLElement>('th[data-pinned]'));
-       pinnedThs.forEach(th => {
-         th.style.left = `${offset}px`;
-         const colKey = th.getAttribute('data-col-key');
-         if (colKey !== null) {
-           this.el.querySelectorAll<HTMLElement>(`td[data-col-key="${colKey}"]`).forEach(td => {
-             td.style.left = `${offset}px`;
-           });
-         }
-         offset += th.offsetWidth;
-       });
-     }
+     componentDidRender() {}
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 69 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:168:9
-       if (this.selectable) {
+       if (true) {
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 69 more tests!


[Survived] BlockStatement
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:168:26
-       if (this.selectable) {
-         const checkboxTh = this.el.querySelector<HTMLElement>('th.bds-table__th-checkbox');
-         if (checkboxTh !== null) offset = checkboxTh.offsetWidth;
-       }
+       if (this.selectable) {}
Tests ran:
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
    bds-table selection returns selected row objects from getSelectedRows after selecting a row
  and 21 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:168:9
-       if (this.selectable) {
+       if (false) {
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 69 more tests!


[Survived] StringLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:169:61
-         const checkboxTh = this.el.querySelector<HTMLElement>('th.bds-table__th-checkbox');
+         const checkboxTh = this.el.querySelector<HTMLElement>("");
Tests ran:
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
    bds-table selection returns selected row objects from getSelectedRows after selecting a row
  and 21 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:170:11
-         if (checkboxTh !== null) offset = checkboxTh.offsetWidth;
+         if (true) offset = checkboxTh.offsetWidth;
Tests ran:
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
    bds-table selection returns selected row objects from getSelectedRows after selecting a row
  and 21 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:170:11
-         if (checkboxTh !== null) offset = checkboxTh.offsetWidth;
+         if (false) offset = checkboxTh.offsetWidth;
Tests ran:
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
    bds-table selection returns selected row objects from getSelectedRows after selecting a row
  and 21 more tests!


[Survived] EqualityOperator
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:170:11
-         if (checkboxTh !== null) offset = checkboxTh.offsetWidth;
+         if (checkboxTh === null) offset = checkboxTh.offsetWidth;
Tests ran:
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
    bds-table selection returns selected row objects from getSelectedRows after selecting a row
  and 21 more tests!


[Survived] BlockStatement
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:174:29
-       pinnedThs.forEach(th => {
-         th.style.left = `${offset}px`;
-         const colKey = th.getAttribute('data-col-key');
-         if (colKey !== null) {
-           this.el.querySelectorAll<HTMLElement>(`td[data-col-key="${colKey}"]`).forEach(td => {
-             td.style.left = `${offset}px`;
-           });
-         }
-         offset += th.offsetWidth;
-       });
+       pinnedThs.forEach(th => {});
Tests ran:
    bds-table extras adds data-pinned to the th after clicking the pin icon on a pinnable column
    bds-table extras removes data-pinned from the th after clicking the pin icon a second time (toggle off)
    bds-table extras adds data-pin-last to the th of the last pinned column


[Survived] StringLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:173:72
-       const pinnedThs = Array.from(this.el.querySelectorAll<HTMLElement>('th[data-pinned]'));
+       const pinnedThs = Array.from(this.el.querySelectorAll<HTMLElement>(""));
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 69 more tests!


[Survived] StringLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:175:23
-         th.style.left = `${offset}px`;
+         th.style.left = ``;
Tests ran:
    bds-table extras adds data-pinned to the th after clicking the pin icon on a pinnable column
    bds-table extras removes data-pinned from the th after clicking the pin icon a second time (toggle off)
    bds-table extras adds data-pin-last to the th of the last pinned column


[Survived] StringLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:176:38
-         const colKey = th.getAttribute('data-col-key');
+         const colKey = th.getAttribute("");
Tests ran:
    bds-table extras adds data-pinned to the th after clicking the pin icon on a pinnable column
    bds-table extras removes data-pinned from the th after clicking the pin icon a second time (toggle off)
    bds-table extras adds data-pin-last to the th of the last pinned column


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:177:11
-         if (colKey !== null) {
+         if (true) {
Tests ran:
    bds-table extras adds data-pinned to the th after clicking the pin icon on a pinnable column
    bds-table extras removes data-pinned from the th after clicking the pin icon a second time (toggle off)
    bds-table extras adds data-pin-last to the th of the last pinned column


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:177:11
-         if (colKey !== null) {
+         if (false) {
Tests ran:
    bds-table extras adds data-pinned to the th after clicking the pin icon on a pinnable column
    bds-table extras removes data-pinned from the th after clicking the pin icon a second time (toggle off)
    bds-table extras adds data-pin-last to the th of the last pinned column


[Survived] EqualityOperator
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:177:11
-         if (colKey !== null) {
+         if (colKey === null) {
Tests ran:
    bds-table extras adds data-pinned to the th after clicking the pin icon on a pinnable column
    bds-table extras removes data-pinned from the th after clicking the pin icon a second time (toggle off)
    bds-table extras adds data-pin-last to the th of the last pinned column


[Survived] BlockStatement
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:177:28
-         if (colKey !== null) {
-           this.el.querySelectorAll<HTMLElement>(`td[data-col-key="${colKey}"]`).forEach(td => {
-             td.style.left = `${offset}px`;
-           });
-         }
+         if (colKey !== null) {}
Tests ran:
    bds-table extras adds data-pinned to the th after clicking the pin icon on a pinnable column
    bds-table extras removes data-pinned from the th after clicking the pin icon a second time (toggle off)
    bds-table extras adds data-pin-last to the th of the last pinned column


[Survived] StringLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:178:47
-           this.el.querySelectorAll<HTMLElement>(`td[data-col-key="${colKey}"]`).forEach(td => {
+           this.el.querySelectorAll<HTMLElement>(``).forEach(td => {
Tests ran:
    bds-table extras adds data-pinned to the th after clicking the pin icon on a pinnable column
    bds-table extras removes data-pinned from the th after clicking the pin icon a second time (toggle off)
    bds-table extras adds data-pin-last to the th of the last pinned column


[Survived] AssignmentOperator
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:182:7
-         offset += th.offsetWidth;
+         offset -= th.offsetWidth;
Tests ran:
    bds-table extras adds data-pinned to the th after clicking the pin icon on a pinnable column
    bds-table extras removes data-pinned from the th after clicking the pin icon a second time (toggle off)
    bds-table extras adds data-pin-last to the th of the last pinned column


[Survived] ObjectLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:190:43
-       this._columnObserver.observe(this.el, { childList: true });
+       this._columnObserver.observe(this.el, {});
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 69 more tests!


[Survived] BooleanLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:190:56
-       this._columnObserver.observe(this.el, { childList: true });
+       this._columnObserver.observe(this.el, { childList: false });
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 69 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:193:11
-         if (th !== null) {
+         if (true) {
Tests ran:
    bds-table extras triggers sort via keyboard Enter on a sortable th


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:195:13
-           if (colKey !== null) this.handleSort(colKey);
+           if (true) this.handleSort(colKey);
Tests ran:
    bds-table extras triggers sort via keyboard Enter on a sortable th


[Survived] BlockStatement
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:200:26
-     disconnectedCallback() {
-       this._columnObserver?.disconnect();
-       this._keyboard.detach();
-     }
+     disconnectedCallback() {}
Tests ran:
    bds-table extras does not throw when the element is disconnected from the DOM


[Survived] OptionalChaining
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:201:5
-       this._columnObserver?.disconnect();
+       this._columnObserver.disconnect();
Tests ran:
    bds-table extras does not throw when the element is disconnected from the DOM


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:232:9
-       if (this.data.length > 0 && this.selectedRowIds.size === this.data.length) {
+       if (true && this.selectedRowIds.size === this.data.length) {
Tests ran:
    bds-table selection shows the header checkbox with aria-checked true when all rows are selected via the header checkbox
    bds-table selection emits selectedRowsChange alongside bdsSelect with all row ids when the header checkbox selects all rows
    bds-table extras deselects all rows and emits bdsSelect with empty ids when select-all checkbox is clicked while all are selected


[Survived] EqualityOperator
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:232:9
-       if (this.data.length > 0 && this.selectedRowIds.size === this.data.length) {
+       if (this.data.length >= 0 && this.selectedRowIds.size === this.data.length) {
Tests ran:
    bds-table selection shows the header checkbox with aria-checked true when all rows are selected via the header checkbox
    bds-table selection emits selectedRowsChange alongside bdsSelect with all row ids when the header checkbox selects all rows
    bds-table extras deselects all rows and emits bdsSelect with empty ids when select-all checkbox is clicked while all are selected


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:243:20
-       this.sortKey = this.sortDirection === SORT_DIRECTION.NONE ? '' : colKey;
+       this.sortKey = false ? '' : colKey;
Tests ran:
    bds-table extras triggers sort via keyboard Enter on a sortable th
    bds-table sort emits bdsSort with direction asc when a sortable th is clicked for the first time
    bds-table sort emits bdsSort with direction desc when the same sortable th is clicked a second time
  and 7 more tests!


[Survived] StringLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:243:65
-       this.sortKey = this.sortDirection === SORT_DIRECTION.NONE ? '' : colKey;
+       this.sortKey = this.sortDirection === SORT_DIRECTION.NONE ? "Stryker was here!" : colKey;
Tests ran:
    bds-table sort emits bdsSort with direction none when the same sortable th is clicked a third time
    bds-table sort restores the original row order after the third click resets sort to none


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:265:9
-       if (el == null || col.formatter === undefined) return;
+       if (false) return;
Tests ran:
    bds-table extras renders a cell formatted by a column formatter function


[Survived] LogicalOperator
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:265:9
-       if (el == null || col.formatter === undefined) return;
+       if (el == null && col.formatter === undefined) return;
Tests ran:
    bds-table extras renders a cell formatted by a column formatter function


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:265:9
-       if (el == null || col.formatter === undefined) return;
+       if (false || col.formatter === undefined) return;
Tests ran:
    bds-table extras renders a cell formatted by a column formatter function


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:265:23
-       if (el == null || col.formatter === undefined) return;
+       if (el == null || false) return;
Tests ran:
    bds-table extras renders a cell formatted by a column formatter function


[Survived] StringLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:266:20
-       el.innerHTML = '';
+       el.innerHTML = "Stryker was here!";
Tests ran:
    bds-table extras renders a cell formatted by a column formatter function


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:268:5
-       typeof result === 'string' ? (el.textContent = result) : el.appendChild(result);
+       true ? (el.textContent = result) : el.appendChild(result);
Tests ran:
    bds-table extras renders a cell formatted by a column formatter function


[Survived] BlockStatement
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:278:44
-     private get hasRowActionsSlot(): boolean {
-       return this.el.querySelector('[slot="row-actions"]') !== null;
-     }
+     private get hasRowActionsSlot(): boolean {}
Tests ran:
    bds-table toolbar renders the row actions zone when rows are selected via checkbox bdsChange
    bds-table toolbar emits bdsDelete with selectedIds when the delete button fires bdsClick after row selection
    bds-table toolbar emits bdsEdit with selectedIds when the edit button fires bdsClick after row selection
  and 2 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:279:12
-       return this.el.querySelector('[slot="row-actions"]') !== null;
+       return true;
Tests ran:
    bds-table toolbar renders the row actions zone when rows are selected via checkbox bdsChange
    bds-table toolbar emits bdsDelete with selectedIds when the delete button fires bdsClick after row selection
    bds-table toolbar emits bdsEdit with selectedIds when the edit button fires bdsClick after row selection
  and 2 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:279:12
-       return this.el.querySelector('[slot="row-actions"]') !== null;
+       return false;
Tests ran:
    bds-table toolbar renders the row actions zone when rows are selected via checkbox bdsChange
    bds-table toolbar emits bdsDelete with selectedIds when the delete button fires bdsClick after row selection
    bds-table toolbar emits bdsEdit with selectedIds when the edit button fires bdsClick after row selection
  and 2 more tests!


[Survived] EqualityOperator
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:279:12
-       return this.el.querySelector('[slot="row-actions"]') !== null;
+       return this.el.querySelector('[slot="row-actions"]') === null;
Tests ran:
    bds-table toolbar renders the row actions zone when rows are selected via checkbox bdsChange
    bds-table toolbar emits bdsDelete with selectedIds when the delete button fires bdsClick after row selection
    bds-table toolbar emits bdsEdit with selectedIds when the edit button fires bdsClick after row selection
  and 2 more tests!


[Survived] StringLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:279:34
-       return this.el.querySelector('[slot="row-actions"]') !== null;
+       return this.el.querySelector("") !== null;
Tests ran:
    bds-table toolbar renders the row actions zone when rows are selected via checkbox bdsChange
    bds-table toolbar emits bdsDelete with selectedIds when the delete button fires bdsClick after row selection
    bds-table toolbar emits bdsEdit with selectedIds when the edit button fires bdsClick after row selection
  and 2 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:286:7
-         this.el.querySelector('[slot="row-actions"]') !== null ||
+         false ||
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 56 more tests!


[Survived] StringLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:286:29
-         this.el.querySelector('[slot="row-actions"]') !== null ||
+         this.el.querySelector("") !== null ||
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 56 more tests!


[Survived] MethodExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:292:27
-       const pinnedInOrder = this.columns.filter(col => this.pinnedColKeys.has(col.colKey)).map(col => col.colKey);
+       const pinnedInOrder = this.columns.map(col => col.colKey);
Tests ran:
    bds-table extras adds data-pinned to the th after clicking the pin icon on a pinnable column
    bds-table extras removes data-pinned from the th after clicking the pin icon a second time (toggle off)
    bds-table extras adds data-pin-last to the th of the last pinned column


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:293:12
-       return pinnedInOrder.length > 0 && pinnedInOrder[pinnedInOrder.length - 1] === colKey;
+       return true && pinnedInOrder[pinnedInOrder.length - 1] === colKey;
Tests ran:
    bds-table extras adds data-pinned to the th after clicking the pin icon on a pinnable column
    bds-table extras removes data-pinned from the th after clicking the pin icon a second time (toggle off)
    bds-table extras adds data-pin-last to the th of the last pinned column


[Survived] EqualityOperator
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:293:12
-       return pinnedInOrder.length > 0 && pinnedInOrder[pinnedInOrder.length - 1] === colKey;
+       return pinnedInOrder.length >= 0 && pinnedInOrder[pinnedInOrder.length - 1] === colKey;
Tests ran:
    bds-table extras adds data-pinned to the th after clicking the pin icon on a pinnable column
    bds-table extras removes data-pinned from the th after clicking the pin icon a second time (toggle off)
    bds-table extras adds data-pin-last to the th of the last pinned column


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:301:9
-       if (this.sortDirection === SORT_DIRECTION.NONE || this.sortKey === '') return this.data;
+       if (false) return this.data;
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 29 more tests!


[Survived] LogicalOperator
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:301:9
-       if (this.sortDirection === SORT_DIRECTION.NONE || this.sortKey === '') return this.data;
+       if (this.sortDirection === SORT_DIRECTION.NONE && this.sortKey === '') return this.data;
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 29 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:301:9
-       if (this.sortDirection === SORT_DIRECTION.NONE || this.sortKey === '') return this.data;
+       if (false || this.sortKey === '') return this.data;
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 29 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:301:55
-       if (this.sortDirection === SORT_DIRECTION.NONE || this.sortKey === '') return this.data;
+       if (this.sortDirection === SORT_DIRECTION.NONE || false) return this.data;
Tests ran:
    bds-table sort orders tbody rows ascending by string value after the first click on a sortable th
    bds-table sort reverses the tbody row order descending after the second click on a sortable th
    bds-table sort restores the original row order after the third click resets sort to none


[Survived] StringLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:301:72
-       if (this.sortDirection === SORT_DIRECTION.NONE || this.sortKey === '') return this.data;
+       if (this.sortDirection === SORT_DIRECTION.NONE || this.sortKey === "Stryker was here!") return this.data;
Tests ran:
    bds-table sort orders tbody rows ascending by string value after the first click on a sortable th
    bds-table sort reverses the tbody row order descending after the second click on a sortable th
    bds-table sort restores the original row order after the third click resets sort to none


[Survived] LogicalOperator
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:310:9
-       if (this.sortKey !== colKey || this.sortDirection === SORT_DIRECTION.NONE) return ICONS.ChevronUpDown;
+       if (this.sortKey !== colKey && this.sortDirection === SORT_DIRECTION.NONE) return ICONS.ChevronUpDown;
Tests ran:
    bds-table extras renders a pinnable column with a pin icon in its th-actions area
    bds-table extras adds data-pinned to the th after clicking the pin icon on a pinnable column
    bds-table extras removes data-pinned from the th after clicking the pin icon a second time (toggle off)
  and 15 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:310:9
-       if (this.sortKey !== colKey || this.sortDirection === SORT_DIRECTION.NONE) return ICONS.ChevronUpDown;
+       if (false || this.sortDirection === SORT_DIRECTION.NONE) return ICONS.ChevronUpDown;
Tests ran:
    bds-table extras renders a pinnable column with a pin icon in its th-actions area
    bds-table extras adds data-pinned to the th after clicking the pin icon on a pinnable column
    bds-table extras removes data-pinned from the th after clicking the pin icon a second time (toggle off)
  and 15 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:310:36
-       if (this.sortKey !== colKey || this.sortDirection === SORT_DIRECTION.NONE) return ICONS.ChevronUpDown;
+       if (this.sortKey !== colKey || false) return ICONS.ChevronUpDown;
Tests ran:
    bds-table extras triggers sort via keyboard Enter on a sortable th
    bds-table sort emits bdsSort with direction asc when a sortable th is clicked for the first time
    bds-table sort emits bdsSort with direction desc when the same sortable th is clicked a second time
  and 7 more tests!


[Survived] StringLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:322:87
-                   <tr class={this.selectedRowIds.has(id) ? `${PREFIX}__row--selected` : ''}>
+                   <tr class={this.selectedRowIds.has(id) ? `${PREFIX}__row--selected` : "Stryker was here!"}>
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 29 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:334:26
-       const isLastPinned = isPinned && this.isLastPinnedColumn(col.colKey);
+       const isLastPinned = true;
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 29 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:334:26
-       const isLastPinned = isPinned && this.isLastPinnedColumn(col.colKey);
+       const isLastPinned = false;
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 29 more tests!


[Survived] LogicalOperator
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:334:26
-       const isLastPinned = isPinned && this.isLastPinnedColumn(col.colKey);
+       const isLastPinned = isPinned || this.isLastPinnedColumn(col.colKey);
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 29 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:378:20
-             checked={this.data.length > 0 && this.selectedRowIds.size === this.data.length}
+             checked={true}
Tests ran:
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
    bds-table selection returns selected row objects from getSelectedRows after selecting a row
  and 21 more tests!


[Survived] LogicalOperator
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:378:20
-             checked={this.data.length > 0 && this.selectedRowIds.size === this.data.length}
+             checked={this.data.length > 0 || this.selectedRowIds.size === this.data.length}
Tests ran:
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
    bds-table selection returns selected row objects from getSelectedRows after selecting a row
  and 21 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:378:20
-             checked={this.data.length > 0 && this.selectedRowIds.size === this.data.length}
+             checked={true && this.selectedRowIds.size === this.data.length}
Tests ran:
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
    bds-table selection returns selected row objects from getSelectedRows after selecting a row
  and 21 more tests!


[Survived] EqualityOperator
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:378:20
-             checked={this.data.length > 0 && this.selectedRowIds.size === this.data.length}
+             checked={this.data.length >= 0 && this.selectedRowIds.size === this.data.length}
Tests ran:
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
    bds-table selection returns selected row objects from getSelectedRows after selecting a row
  and 21 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:378:44
-             checked={this.data.length > 0 && this.selectedRowIds.size === this.data.length}
+             checked={this.data.length > 0 && true}
Tests ran:
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
    bds-table selection returns selected row objects from getSelectedRows after selecting a row
  and 20 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:379:26
-             indeterminate={this.selectedRowIds.size > 0 && this.selectedRowIds.size < this.data.length}
+             indeterminate={true && this.selectedRowIds.size < this.data.length}
Tests ran:
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
    bds-table selection returns selected row objects from getSelectedRows after selecting a row
  and 21 more tests!


[Survived] EqualityOperator
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:379:26
-             indeterminate={this.selectedRowIds.size > 0 && this.selectedRowIds.size < this.data.length}
+             indeterminate={this.selectedRowIds.size >= 0 && this.selectedRowIds.size < this.data.length}
Tests ran:
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
    bds-table selection returns selected row objects from getSelectedRows after selecting a row
  and 21 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:395:9
-       if (col.colKey == '') {
+       if (true) {
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 64 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:395:9
-       if (col.colKey == '') {
+       if (false) {
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 64 more tests!


[Survived] EqualityOperator
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:395:9
-       if (col.colKey == '') {
+       if (col.colKey != '') {
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 64 more tests!


[Survived] StringLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:395:23
-       if (col.colKey == '') {
+       if (col.colKey == "Stryker was here!") {
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 64 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:406:7
-         this.sortKey === col.colKey && this.sortDirection === SORT_DIRECTION.ASC
+         true
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 64 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:406:7
-         this.sortKey === col.colKey && this.sortDirection === SORT_DIRECTION.ASC
+         false
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 64 more tests!


[Survived] LogicalOperator
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:406:7
-         this.sortKey === col.colKey && this.sortDirection === SORT_DIRECTION.ASC
+         this.sortKey === col.colKey || this.sortDirection === SORT_DIRECTION.ASC
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 64 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:406:7
-         this.sortKey === col.colKey && this.sortDirection === SORT_DIRECTION.ASC
+         true && this.sortDirection === SORT_DIRECTION.ASC
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 64 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:406:38
-         this.sortKey === col.colKey && this.sortDirection === SORT_DIRECTION.ASC
+         this.sortKey === col.colKey && true
Tests ran:
    bds-table extras triggers sort via keyboard Enter on a sortable th
    bds-table sort emits bdsSort with direction asc when a sortable th is clicked for the first time
    bds-table sort emits bdsSort with direction desc when the same sortable th is clicked a second time
  and 7 more tests!


[Survived] EqualityOperator
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:406:7
-         this.sortKey === col.colKey && this.sortDirection === SORT_DIRECTION.ASC
+         this.sortKey !== col.colKey && this.sortDirection === SORT_DIRECTION.ASC
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 64 more tests!


[Survived] EqualityOperator
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:406:38
-         this.sortKey === col.colKey && this.sortDirection === SORT_DIRECTION.ASC
+         this.sortKey === col.colKey && this.sortDirection !== SORT_DIRECTION.ASC
Tests ran:
    bds-table extras triggers sort via keyboard Enter on a sortable th
    bds-table sort emits bdsSort with direction asc when a sortable th is clicked for the first time
    bds-table sort emits bdsSort with direction desc when the same sortable th is clicked a second time
  and 7 more tests!


[Survived] StringLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:407:11
-           ? 'ascending'
+           ? ""
Tests ran:
    bds-table extras triggers sort via keyboard Enter on a sortable th
    bds-table sort emits bdsSort with direction asc when a sortable th is clicked for the first time
    bds-table sort emits bdsSort with direction desc when the same sortable th is clicked a second time
  and 7 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:408:11
-           : this.sortKey === col.colKey && this.sortDirection === SORT_DIRECTION.DESC
+           : true
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 64 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:408:11
-           : this.sortKey === col.colKey && this.sortDirection === SORT_DIRECTION.DESC
+           : false
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 64 more tests!


[Survived] LogicalOperator
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:408:11
-           : this.sortKey === col.colKey && this.sortDirection === SORT_DIRECTION.DESC
+           : this.sortKey === col.colKey || this.sortDirection === SORT_DIRECTION.DESC
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 64 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:408:11
-           : this.sortKey === col.colKey && this.sortDirection === SORT_DIRECTION.DESC
+           : true && this.sortDirection === SORT_DIRECTION.DESC
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 64 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:408:42
-           : this.sortKey === col.colKey && this.sortDirection === SORT_DIRECTION.DESC
+           : this.sortKey === col.colKey && true
Tests ran:
    bds-table sort emits bdsSort with direction desc when the same sortable th is clicked a second time
    bds-table sort emits bdsSort with direction none when the same sortable th is clicked a third time
    bds-table sort reverses the tbody row order descending after the second click on a sortable th
  and 2 more tests!


[Survived] EqualityOperator
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:408:42
-           : this.sortKey === col.colKey && this.sortDirection === SORT_DIRECTION.DESC
+           : this.sortKey === col.colKey && this.sortDirection !== SORT_DIRECTION.DESC
Tests ran:
    bds-table sort emits bdsSort with direction desc when the same sortable th is clicked a second time
    bds-table sort emits bdsSort with direction none when the same sortable th is clicked a third time
    bds-table sort reverses the tbody row order descending after the second click on a sortable th
  and 2 more tests!


[Survived] StringLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:409:13
-             ? 'descending'
+             ? ""
Tests ran:
    bds-table sort emits bdsSort with direction desc when the same sortable th is clicked a second time
    bds-table sort emits bdsSort with direction none when the same sortable th is clicked a third time
    bds-table sort reverses the tbody row order descending after the second click on a sortable th
  and 2 more tests!


[Survived] EqualityOperator
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:408:11
-           : this.sortKey === col.colKey && this.sortDirection === SORT_DIRECTION.DESC
+           : this.sortKey !== col.colKey && this.sortDirection === SORT_DIRECTION.DESC
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 64 more tests!


[Survived] StringLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:410:13
-             : 'none';
+             : "";
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 64 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:432:30
-         <th scope="col" style={col.width !== '' ? { width: col.width } : undefined} {...sortableProps} {...pinnedProps}>
+         <th scope="col" style={false ? { width: col.width } : undefined} {...sortableProps} {...pinnedProps}>
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 64 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:432:30
-         <th scope="col" style={col.width !== '' ? { width: col.width } : undefined} {...sortableProps} {...pinnedProps}>
+         <th scope="col" style={true ? { width: col.width } : undefined} {...sortableProps} {...pinnedProps}>
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 64 more tests!


[Survived] EqualityOperator
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:432:30
-         <th scope="col" style={col.width !== '' ? { width: col.width } : undefined} {...sortableProps} {...pinnedProps}>
+         <th scope="col" style={col.width === '' ? { width: col.width } : undefined} {...sortableProps} {...pinnedProps}>
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 64 more tests!


[Survived] StringLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:432:44
-         <th scope="col" style={col.width !== '' ? { width: col.width } : undefined} {...sortableProps} {...pinnedProps}>
+         <th scope="col" style={col.width !== "Stryker was here!" ? { width: col.width } : undefined} {...sortableProps} {...pinnedProps}>
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 64 more tests!


[Survived] StringLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:433:22
-           <span class={`${PREFIX}__th-content`}>
+           <span class={``}>
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 64 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:442:9
-       if (!col.sortable && !col.pinnable) return null;
+       if (false) return null;
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 64 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:444:22
-       const isActive = this.sortKey === col.colKey && this.sortDirection !== SORT_DIRECTION.NONE;
+       const isActive = true;
Tests ran:
    bds-table extras renders a pinnable column with a pin icon in its th-actions area
    bds-table extras adds data-pinned to the th after clicking the pin icon on a pinnable column
    bds-table extras removes data-pinned from the th after clicking the pin icon a second time (toggle off)
  and 15 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:444:22
-       const isActive = this.sortKey === col.colKey && this.sortDirection !== SORT_DIRECTION.NONE;
+       const isActive = false;
Tests ran:
    bds-table extras renders a pinnable column with a pin icon in its th-actions area
    bds-table extras adds data-pinned to the th after clicking the pin icon on a pinnable column
    bds-table extras removes data-pinned from the th after clicking the pin icon a second time (toggle off)
  and 15 more tests!


[Survived] LogicalOperator
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:444:22
-       const isActive = this.sortKey === col.colKey && this.sortDirection !== SORT_DIRECTION.NONE;
+       const isActive = this.sortKey === col.colKey || this.sortDirection !== SORT_DIRECTION.NONE;
Tests ran:
    bds-table extras renders a pinnable column with a pin icon in its th-actions area
    bds-table extras adds data-pinned to the th after clicking the pin icon on a pinnable column
    bds-table extras removes data-pinned from the th after clicking the pin icon a second time (toggle off)
  and 15 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:444:22
-       const isActive = this.sortKey === col.colKey && this.sortDirection !== SORT_DIRECTION.NONE;
+       const isActive = true && this.sortDirection !== SORT_DIRECTION.NONE;
Tests ran:
    bds-table extras renders a pinnable column with a pin icon in its th-actions area
    bds-table extras adds data-pinned to the th after clicking the pin icon on a pinnable column
    bds-table extras removes data-pinned from the th after clicking the pin icon a second time (toggle off)
  and 15 more tests!


[Survived] EqualityOperator
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:444:22
-       const isActive = this.sortKey === col.colKey && this.sortDirection !== SORT_DIRECTION.NONE;
+       const isActive = this.sortKey !== col.colKey && this.sortDirection !== SORT_DIRECTION.NONE;
Tests ran:
    bds-table extras renders a pinnable column with a pin icon in its th-actions area
    bds-table extras adds data-pinned to the th after clicking the pin icon on a pinnable column
    bds-table extras removes data-pinned from the th after clicking the pin icon a second time (toggle off)
  and 15 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:444:53
-       const isActive = this.sortKey === col.colKey && this.sortDirection !== SORT_DIRECTION.NONE;
+       const isActive = this.sortKey === col.colKey && true;
Tests ran:
    bds-table extras triggers sort via keyboard Enter on a sortable th
    bds-table sort emits bdsSort with direction asc when a sortable th is clicked for the first time
    bds-table sort emits bdsSort with direction desc when the same sortable th is clicked a second time
  and 7 more tests!


[Survived] EqualityOperator
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:444:53
-       const isActive = this.sortKey === col.colKey && this.sortDirection !== SORT_DIRECTION.NONE;
+       const isActive = this.sortKey === col.colKey && this.sortDirection === SORT_DIRECTION.NONE;
Tests ran:
    bds-table extras triggers sort via keyboard Enter on a sortable th
    bds-table sort emits bdsSort with direction asc when a sortable th is clicked for the first time
    bds-table sort emits bdsSort with direction desc when the same sortable th is clicked a second time
  and 7 more tests!


[Survived] MethodExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:445:27
-       const sortIconClass = [this.sortIconClass(col.colKey), isActive ? `${PREFIX}__sort-icon--active` : '']
-         .filter(Boolean)
+       const sortIconClass = [this.sortIconClass(col.colKey), isActive ? `${PREFIX}__sort-icon--active` : '']
Tests ran:
    bds-table extras renders a pinnable column with a pin icon in its th-actions area
    bds-table extras adds data-pinned to the th after clicking the pin icon on a pinnable column
    bds-table extras removes data-pinned from the th after clicking the pin icon a second time (toggle off)
  and 15 more tests!


[Survived] StringLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:445:71
-       const sortIconClass = [this.sortIconClass(col.colKey), isActive ? `${PREFIX}__sort-icon--active` : '']
+       const sortIconClass = [this.sortIconClass(col.colKey), isActive ? `` : '']
Tests ran:
    bds-table extras triggers sort via keyboard Enter on a sortable th
    bds-table sort emits bdsSort with direction asc when a sortable th is clicked for the first time
    bds-table sort emits bdsSort with direction desc when the same sortable th is clicked a second time
  and 7 more tests!


[Survived] StringLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:445:104
-       const sortIconClass = [this.sortIconClass(col.colKey), isActive ? `${PREFIX}__sort-icon--active` : '']
+       const sortIconClass = [this.sortIconClass(col.colKey), isActive ? `${PREFIX}__sort-icon--active` : "Stryker was here!"]
Tests ran:
    bds-table extras renders a pinnable column with a pin icon in its th-actions area
    bds-table extras adds data-pinned to the th after clicking the pin icon on a pinnable column
    bds-table extras removes data-pinned from the th after clicking the pin icon a second time (toggle off)
  and 15 more tests!


[Survived] MethodExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:450:26
-       const pinIconClass = [isPinned ? ICONS.PinFill : ICONS.Pin, isPinned ? `${PREFIX}__pin-icon--active` : '']
-         .filter(Boolean)
+       const pinIconClass = [isPinned ? ICONS.PinFill : ICONS.Pin, isPinned ? `${PREFIX}__pin-icon--active` : '']
Tests ran:
    bds-table extras renders a pinnable column with a pin icon in its th-actions area
    bds-table extras adds data-pinned to the th after clicking the pin icon on a pinnable column
    bds-table extras removes data-pinned from the th after clicking the pin icon a second time (toggle off)
  and 15 more tests!


[Survived] StringLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:450:76
-       const pinIconClass = [isPinned ? ICONS.PinFill : ICONS.Pin, isPinned ? `${PREFIX}__pin-icon--active` : '']
+       const pinIconClass = [isPinned ? ICONS.PinFill : ICONS.Pin, isPinned ? `` : '']
Tests ran:
    bds-table extras adds data-pinned to the th after clicking the pin icon on a pinnable column
    bds-table extras removes data-pinned from the th after clicking the pin icon a second time (toggle off)
    bds-table extras adds data-pin-last to the th of the last pinned column


[Survived] StringLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:450:108
-       const pinIconClass = [isPinned ? ICONS.PinFill : ICONS.Pin, isPinned ? `${PREFIX}__pin-icon--active` : '']
+       const pinIconClass = [isPinned ? ICONS.PinFill : ICONS.Pin, isPinned ? `${PREFIX}__pin-icon--active` : "Stryker was here!"]
Tests ran:
    bds-table extras renders a pinnable column with a pin icon in its th-actions area
    bds-table extras adds data-pinned to the th after clicking the pin icon on a pinnable column
    bds-table extras removes data-pinned from the th after clicking the pin icon a second time (toggle off)
  and 15 more tests!


[Survived] StringLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:475:22
-           <span class={`${PREFIX}__th-label-text`}>{col.label}</span>
+           <span class={``}>{col.label}</span>
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 64 more tests!


[Survived] StringLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:497:19
-         <div class={`${PREFIX}__toolbar-left`}>
+         <div class={``}>
Tests ran:
    bds-table toolbar renders the toolbar when subheading is set
    bds-table toolbar renders the subheading text inside the toolbar when subheading prop is set
    bds-table toolbar renders the subheading icon when subheading-icon is set alongside subheading
  and 11 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:498:10
-           {this.subheading !== '' && (
+           {true && (
Tests ran:
    bds-table toolbar renders the toolbar when subheading is set
    bds-table toolbar renders the subheading text inside the toolbar when subheading prop is set
    bds-table toolbar renders the subheading icon when subheading-icon is set alongside subheading
  and 11 more tests!


[Survived] StringLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:498:30
-           {this.subheading !== '' && (
+           {this.subheading !== "Stryker was here!" && (
Tests ran:
    bds-table toolbar renders the toolbar when subheading is set
    bds-table toolbar renders the subheading text inside the toolbar when subheading prop is set
    bds-table toolbar renders the subheading icon when subheading-icon is set alongside subheading
  and 11 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:500:14
-               {this.subheadingIcon !== '' && <i class={this.subheadingIcon} aria-hidden="true" />}
+               {true && <i class={this.subheadingIcon} aria-hidden="true" />}
Tests ran:
    bds-table toolbar renders the toolbar when subheading is set
    bds-table toolbar renders the subheading text inside the toolbar when subheading prop is set
    bds-table toolbar renders the subheading icon when subheading-icon is set alongside subheading
  and 9 more tests!


[Survived] StringLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:500:38
-               {this.subheadingIcon !== '' && <i class={this.subheadingIcon} aria-hidden="true" />}
+               {this.subheadingIcon !== "Stryker was here!" && <i class={this.subheadingIcon} aria-hidden="true" />}
Tests ran:
    bds-table toolbar renders the toolbar when subheading is set
    bds-table toolbar renders the subheading text inside the toolbar when subheading prop is set
    bds-table toolbar renders the subheading icon when subheading-icon is set alongside subheading
  and 9 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:501:63
-               <bds-typography variant="subheading" tooltipText={this.tooltipText !== '' ? this.tooltipText : undefined}>
+               <bds-typography variant="subheading" tooltipText={true ? this.tooltipText : undefined}>
Tests ran:
    bds-table toolbar renders the toolbar when subheading is set
    bds-table toolbar renders the subheading text inside the toolbar when subheading prop is set
    bds-table toolbar renders the subheading icon when subheading-icon is set alongside subheading
  and 9 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:501:63
-               <bds-typography variant="subheading" tooltipText={this.tooltipText !== '' ? this.tooltipText : undefined}>
+               <bds-typography variant="subheading" tooltipText={false ? this.tooltipText : undefined}>
Tests ran:
    bds-table toolbar renders the toolbar when subheading is set
    bds-table toolbar renders the subheading text inside the toolbar when subheading prop is set
    bds-table toolbar renders the subheading icon when subheading-icon is set alongside subheading
  and 9 more tests!


[Survived] EqualityOperator
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:501:63
-               <bds-typography variant="subheading" tooltipText={this.tooltipText !== '' ? this.tooltipText : undefined}>
+               <bds-typography variant="subheading" tooltipText={this.tooltipText === '' ? this.tooltipText : undefined}>
Tests ran:
    bds-table toolbar renders the toolbar when subheading is set
    bds-table toolbar renders the subheading text inside the toolbar when subheading prop is set
    bds-table toolbar renders the subheading icon when subheading-icon is set alongside subheading
  and 9 more tests!


[Survived] StringLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:501:84
-               <bds-typography variant="subheading" tooltipText={this.tooltipText !== '' ? this.tooltipText : undefined}>
+               <bds-typography variant="subheading" tooltipText={this.tooltipText !== "Stryker was here!" ? this.tooltipText : undefined}>
Tests ran:
    bds-table toolbar renders the toolbar when subheading is set
    bds-table toolbar renders the subheading text inside the toolbar when subheading prop is set
    bds-table toolbar renders the subheading icon when subheading-icon is set alongside subheading
  and 9 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:524:14
-               {this.hasRowActionsSlot && <bds-divider orientation="vertical" />}
+               {true}
Tests ran:
    bds-table toolbar renders the row actions zone when rows are selected via checkbox bdsChange
    bds-table toolbar emits bdsDelete with selectedIds when the delete button fires bdsClick after row selection
    bds-table toolbar emits bdsEdit with selectedIds when the edit button fires bdsClick after row selection
  and 2 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:524:14
-               {this.hasRowActionsSlot && <bds-divider orientation="vertical" />}
+               {false}
Tests ran:
    bds-table toolbar renders the row actions zone when rows are selected via checkbox bdsChange
    bds-table toolbar emits bdsDelete with selectedIds when the delete button fires bdsClick after row selection
    bds-table toolbar emits bdsEdit with selectedIds when the edit button fires bdsClick after row selection
  and 2 more tests!


[Survived] LogicalOperator
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:524:14
-               {this.hasRowActionsSlot && <bds-divider orientation="vertical" />}
+               {this.hasRowActionsSlot || <bds-divider orientation="vertical" />}
Tests ran:
    bds-table toolbar renders the row actions zone when rows are selected via checkbox bdsChange
    bds-table toolbar emits bdsDelete with selectedIds when the delete button fires bdsClick after row selection
    bds-table toolbar emits bdsEdit with selectedIds when the edit button fires bdsClick after row selection
  and 2 more tests!


[Survived] StringLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:534:19
-         <div class={`${PREFIX}__toolbar-right`}>
+         <div class={``}>
Tests ran:
    bds-table toolbar renders the toolbar when subheading is set
    bds-table toolbar renders the subheading text inside the toolbar when subheading prop is set
    bds-table toolbar renders the subheading icon when subheading-icon is set alongside subheading
  and 11 more tests!


[Survived] ConditionalExpression
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:555:16
-           style={this.maxHeight !== '' ? { '--bds-table-max-height': this.maxHeight } : undefined}
+           style={true ? { '--bds-table-max-height': this.maxHeight } : undefined}
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 69 more tests!


[Survived] StringLiteral
src/components/data-visualization/bds-table/bds-table/bds-table.tsx:555:35
-           style={this.maxHeight !== '' ? { '--bds-table-max-height': this.maxHeight } : undefined}
+           style={this.maxHeight !== "Stryker was here!" ? { '--bds-table-max-height': this.maxHeight } : undefined}
Tests ran:
    bds-table selection does not render a checkbox column in the header when selectable is false
    bds-table selection renders a checkbox column in the header and each data row when selectable is true
    bds-table selection emits bdsSelect with the correct selectedIds when a row checkbox fires bdsChange
  and 69 more tests!


Ran 29.72 tests per mutant on average.
---------------|------------------|----------|-----------|------------|----------|----------|
               | % Mutation score |          |           |            |          |          |
File           |  total | covered | # killed | # timeout | # survived | # no cov | # errors |
---------------|--------|---------|----------|-----------|------------|----------|----------|
All files      |  64.56 |   66.23 |      255 |         0 |        130 |       10 |        0 |
 bds-table.tsx |  64.56 |   66.23 |      255 |         0 |        130 |       10 |        0 |
---------------|--------|---------|----------|-----------|------------|----------|----------|
[32m14:37:28 (20211) INFO HtmlReporter[39m Your report can be found at: file:///Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-table/packages/boreal-web-components/reports/mutation/mutation.html
[32m14:37:28 (20211) INFO MutationTestExecutor[39m Done in 3 minutes and 58 seconds.

---

## Accepted Mutation Survivors (Task 7 — `selectedRows` / `selectedRowsChange`)

Scoped to the lines Task 7 added: the `selectedRows` prop, its `@Watch`, the `componentWillLoad` seeding guard, and the three `selectedRowsChange.emit()` call sites. Task-7-scoped mutants: 29 total, 25 killed, 4 accepted survivors below (100% excluding these).

1. **`bds-table.tsx:160`** — `if (this.selectedRows.length > 0) { this.selectedRowIds = new Set(this.selectedRows); }`
   Mutants: `> 0` → `>= 0`, `> 0` → `true`.
   Equivalent: when `selectedRows` is empty, both the original guard (skip) and the mutated guard (always assign `new Set([])`) leave `selectedRowIds` logically empty (`new Set([])` vs. the untouched initial `new Set()`), which is not observable at the DOM level with this codebase's testing utilities.

2. **`bds-table.tsx:232`** (pre-existing, not part of Task 7's diff) — `if (this.data.length > 0 && this.selectedRowIds.size === this.data.length)`
   Mutants: `> 0` → `>= 0`, `> 0` → `true` (partial, combined with the `&&` clause).
   Equivalent for the same reason: when `data.length` is 0, `selectedRowIds.size === this.data.length` can only be true if `selectedRowIds` is also empty, so both branches collapse to the same "select all" no-op.

See `.agents/skills/testing-knowledge/SKILL.md` "Accepted Mutation Survivors" for the general convention.

---

## Task 8 follow-up — `selectedRows` mutable-prop mirroring (Vue v-model fix)

Task 8's manual test (driving `examples/vue-testapp` live) revealed that `@stencil/vue-output-target`'s `defineContainer` reads the v-model value off `event.target[modelProp]`, not `event.detail` — so `bds-table`'s `selectedRows` had to become a self-mirroring mutable prop (`@Prop({ mutable: true })`, matching `bds-checkbox`'s `checked` pattern) for `v-model="selection"` to work at all. This added `this.selectedRows = [...]` assignments in `handleRowSelect`, `handleSelectAll`, `clearSelection`, and `onDataChange`.

Two new mutants appeared as a result, both fixed:

1. **`bds-table.tsx:100`** — `@Prop({ mutable: true }) selectedRows: string[] = [];` default-value mutant (`[]` → `["Stryker was here"]`) started surviving again. Root cause: the existing "does not pre-select..." test set `data` via `html` template then assignment *after* mount, and the new `onDataChange` auto-clear (added for consistency — see below) wiped out the mutated seed before assertions ran. Fixed by rewriting the test to set `data` via `page.doc.createElement` before `appendChild`, matching the componentWillLoad-seed test's pattern (no `@Watch('data')` fires on the very first value).
2. **`bds-table.tsx:127`** — `this.selectedRowsChange.emit([]);` (added to `onDataChange` for v-model consistency when a data change auto-clears selection) had no event-spy assertion. Fixed by adding a `selectedRowsChange` spy to the "clears selection ... when data prop changes" test.

**Final score after both fixes:** 260 killed / 130 survived / 10 no-coverage (65.00% file-wide, up from 64.50%). Task-8-scoped new lines: fully killed, no new accepted survivors beyond the two already documented above (componentWillLoad guard and handleSelectAll guard equivalents, unaffected by this change).

---

## Task 12 — `bds-table` built-in search bar (`searchable`)

Scope: `@Prop() readonly searchable: boolean = false;` (line 92), the `hasToolbar` getter's `this.searchable ||` clause (line 298), and `renderToolbarRight()`'s `{this.searchable && <bds-search-bar mode="search" />}` conditional (lines 545-549).

Mid-session design correction: the initial implementation kept `slot="search-bar"` as an escape hatch (with a `hasSearchBarSlotContent` check and a `Logger.warn` when both `searchable` and the slot were populated simultaneously). A confirmed UX/UI decision removed the slot entirely — `searchable` is now the only way to add search; there is no dual-render guard, no warning, and no `[slot="search-bar"]` query anywhere in the component. Tests were rewritten accordingly (dropped the "both set → warns" and "slot renders when searchable=false" cases; added "no search element and no residual `<slot name=\"search-bar\">` renders when searchable=false"). One pre-existing test from before this task (`renders the toolbar when only the search-bar slot is filled...`) was now asserting dead behavior and was corrected to assert the toolbar does NOT render for stray `slot="search-bar"` content, since `hasToolbar` no longer checks for that slot.

Final suite: 91 tests across 6 spec files, 98.13% statement coverage on `bds-table.tsx` (all Task 12 lines exercised, confirmed via `lcov.info` DA hit-counts).

**Mutation run (second, against corrected implementation):** 401 mutants total, 262 killed, 129 survived, 10 no-coverage, 0 timeout (65.34% file-wide — consistent with the pre-existing low file-wide baseline noted in Tasks 7/8, driven by unrelated code: pinned-column offset calc, the `colKey`-missing warning, pin-props object literals, etc.).

**Task-12-scoped result: 100% — zero survivors, zero no-coverage.** Confirmed by grepping the survived/no-coverage sections of the mutation report for lines 92, 298, 545, and 548: no matches. All mutants Stryker generated on the `searchable` prop default, the `hasToolbar` boolean-or clause, and the `renderToolbarRight` conditional-render were killed by the `searchable` describe block in `bds-table.toolbar.spec.ts`. No accepted survivors to document for this task.

(Note: an earlier first Stryker run, executed before the slot-removal correction landed, is superseded and was not used for this scoring — re-run in full against the corrected code.)
