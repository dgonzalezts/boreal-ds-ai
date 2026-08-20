[32m23:29:12 (84336) INFO ProjectReader[39m Found 1 of 3610 file(s) to be mutated.
Browserslist: browsers data (caniuse-lite) is 7 months old. Please run:
  npx update-browserslist-db@latest
  Why you should do it regularly: https://github.com/browserslist/update-db#readme
[32m23:29:12 (84336) INFO Instrumenter[39m Instrumented 1 source file(s) with 43 mutant(s)
[32m23:29:12 (84336) INFO ConcurrencyTokenProvider[39m Creating 2 test runner process(es).
[32m23:29:14 (84336) INFO BroadcastReporter[39m Detected that current console does not support the "progress" reporter, downgrading to "progress-append-only" reporter
[32m23:29:14 (84336) INFO DryRunExecutor[39m Starting initial test run (jest test runner with "perTest" coverage analysis). This may take a while.
[32m23:29:17 (84336) INFO DryRunExecutor[39m Initial test run succeeded. Ran 25 tests in 2 seconds (net 99 ms, overhead 1990 ms).
Mutation testing 24% (elapsed: <1m, remaining: <1m) 20/43 tested (0 survived, 0 timed out)
Mutation testing 93% (elapsed: <1m, remaining: <1m) 41/43 tested (1 survived, 0 timed out)

All tests
  bds-calendar-grid.a11y.spec.ts
    ~ bds-calendar-grid a11y exposes the day grid to assistive technology as a grid role, with column-scoped weekday headers [line 33] (covered 29)
    ✓ bds-calendar-grid a11y gives each day cell an accessible name matching the full display date, not just the visible day number [line 46] (killed 3)
    ✓ bds-calendar-grid a11y gives the previous/next month navigation controls a descriptive accessible name via the label prop, not icon-only [line 55] (killed 1)
    ✓ bds-calendar-grid a11y announces today's cell distinctly from other cells via aria-current [line 64] (killed 4)
    ✓ bds-calendar-grid a11y announces the selected cell distinctly from other cells via aria-selected [line 77] (killed 5)
    ~ bds-calendar-grid a11y arrow-key keyboard navigation between day cells is out of scope for this accessibility spec file — deferred to a later phase (Phase 8) [line 88] (covered 1)
  bds-calendar-grid.basics.spec.ts
    ✓ bds-calendar-grid basics renders the day grid as a native table with role="grid" [line 18] (killed 1)
    ✓ bds-calendar-grid basics renders a thead and a tbody inside the grid table [line 24] (killed 1)
    ✓ bds-calendar-grid basics renders exactly 42 day cells in the tbody [line 33] (killed 1)
    ✓ bds-calendar-grid basics renders weekday header cells as th scope="col" in the expected order [line 40] (killed 1)
    ✓ bds-calendar-grid basics renders the month/year label matching the given year and month [line 52] (killed 1)
    ✓ bds-calendar-grid basics renders the header container with its expected class [line 60] (killed 1)
    ✓ bds-calendar-grid basics renders every day cell as untabbable, regardless of selection state [line 67] (killed 1)
    ✓ bds-calendar-grid basics marks a cell disabled via its dedicated class when the grid flags it as such [line 76] (killed 1)
    ~ bds-calendar-grid basics renders no internal state, so identical props produce identical output [line 89] (covered 29)
  bds-calendar-grid.events.spec.ts
    ✓ bds-calendar-grid events emits bdsDayClick with the clicked cell's ISO date [line 23] (killed 7)
    ✓ bds-calendar-grid events emits bdsMonthNavigate with the rolled-over year/month/direction across the December to January boundary [line 38] (killed 3)
    ✓ bds-calendar-grid events emits bdsMonthNavigate with the rolled-over year/month/direction across the January to December boundary [line 53] (killed 3)
    ~ bds-calendar-grid events does not change its own year/month props after a nav click, since it is controlled by its parent [line 68] (covered 31)
  bds-calendar-grid.variants.spec.ts
    ✓ bds-calendar-grid variants marks exactly one cell as selected when selectedDate matches a cell in the grid [line 33] (killed 4)
    ~ bds-calendar-grid variants marks no cell as selected when selectedDate is not set [line 41] (covered 29)
    ~ bds-calendar-grid variants marks exactly the current-date cell as today [line 48] (covered 29)
    ~ bds-calendar-grid variants marks no cell as today when the mocked current date falls outside the displayed month [line 57] (covered 28)
    ~ bds-calendar-grid variants renders leading/trailing adjacent-month cells with the outside class [line 65] (covered 28)
    ✓ bds-calendar-grid variants does not emit bdsDayClick when an outside-month cell is clicked [line 72] (killed 4)

[Survived] StringLiteral
src/components/forms/bds-date-picker/bds-calendar-grid/bds-calendar-grid.tsx:127:31
-             <tr role="row" key={`week-${weekIndex}`}>
+             <tr role="row" key={``}>
Tests ran:
    bds-calendar-grid a11y exposes the day grid to assistive technology as a grid role, with column-scoped weekday headers
    bds-calendar-grid a11y gives each day cell an accessible name matching the full display date, not just the visible day number
    bds-calendar-grid a11y gives the previous/next month navigation controls a descriptive accessible name via the label prop, not icon-only
  and 21 more tests!


Ran 17.09 tests per mutant on average.
-----------------------|------------------|----------|-----------|------------|----------|----------|
                       | % Mutation score |          |           |            |          |          |
File                   |  total | covered | # killed | # timeout | # survived | # no cov | # errors |
-----------------------|--------|---------|----------|-----------|------------|----------|----------|
All files              |  97.67 |   97.67 |       42 |         0 |          1 |        0 |        0 |
 bds-calendar-grid.tsx |  97.67 |   97.67 |       42 |         0 |          1 |        0 |        0 |
-----------------------|--------|---------|----------|-----------|------------|----------|----------|
[32m23:29:37 (84336) INFO HtmlReporter[39m Your report can be found at: file:///Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/reports/mutation/mutation.html
[32m23:29:37 (84336) INFO MutationTestExecutor[39m Done in 25 seconds.
