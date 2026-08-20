[32m23:27:08 (67716) INFO ProjectReader[39m Found 3 of 3610 file(s) to be mutated.
Browserslist: browsers data (caniuse-lite) is 7 months old. Please run:
  npx update-browserslist-db@latest
  Why you should do it regularly: https://github.com/browserslist/update-db#readme
[32m23:27:08 (67716) INFO Instrumenter[39m Instrumented 3 source file(s) with 76 mutant(s)
[32m23:27:09 (67716) INFO ConcurrencyTokenProvider[39m Creating 2 test runner process(es).
[32m23:27:10 (67716) INFO BroadcastReporter[39m Detected that current console does not support the "progress" reporter, downgrading to "progress-append-only" reporter
[32m23:27:11 (67716) INFO DryRunExecutor[39m Starting initial test run (jest test runner with "perTest" coverage analysis). This may take a while.
[32m23:27:13 (67716) INFO DryRunExecutor[39m Initial test run succeeded. Ran 47 tests in 1 second (net 34 ms, overhead 1851 ms).
Mutation testing 24% (elapsed: <1m, remaining: <1m) 35/76 tested (1 survived, 0 timed out)
Mutation testing 69% (elapsed: <1m, remaining: <1m) 53/76 tested (2 survived, 2 timed out)

All tests
  date-math.spec.ts
    ✓ addMonths advances the date by the given number of months and returns a Date with the expected fields [line 13] (killed 1)
    ✓ subMonths retreats the date by the given number of months and returns a Date with the expected fields [line 23] (killed 1)
    ✓ isSameDay treats two timestamps on the same calendar day as equal, regardless of time-of-day [line 33] (killed 1)
    ✓ isSameMonth treats two dates in the same calendar month as equal, regardless of day or time-of-day [line 42] (killed 1)
    ✓ toNaiveISODate formats a local date as zero-padded yyyy-MM-dd [line 51] (killed 2)
    ~ toNaiveISODate does not shift the date across a UTC day boundary [line 55] (covered 2)
    ~ toNaiveISODate does not shift the date near the opposite end of the local day [line 61] (covered 2)
    ✓ fromNaiveISODate round-trips with toNaiveISODate for a regular date [line 69] (killed 2)
    ~ fromNaiveISODate round-trips with toNaiveISODate for a leap day [line 75] (covered 4)
    ~ fromNaiveISODate parses the ISO string into the matching local calendar date fields [line 81] (covered 2)
    ✓ isWithinRange translates the positional (date, start, end) arguments into the { start, end } interval shape [line 91] (killed 2)
    ✓ compareDates returns exactly -1 when the first date is earlier than the second [line 100] (killed 7)
    ✓ compareDates returns exactly 0 when the dates represent the same instant [line 104] (killed 3)
    ✓ compareDates returns exactly 1 when the first date is later than the second [line 108] (killed 2)
  format.spec.ts
    ✓ formatDisplayDate respects a custom format string [line 5] (killed 1)
    ✓ formatDisplayDate produces locale-correct output for a non-English locale [line 9] (killed 1)
    ~ formatDisplayDate does not throw and produces a sensible default-locale result when no locale is given [line 13] (covered 2)
    ✓ getMonthYearLabel formats a normal month with the English default locale [line 20] (killed 2)
    ~ getMonthYearLabel reads the December label from a December month index without rolling over to January [line 24] (covered 2)
    ✓ getMonthYearLabel produces a locale-correct month name for a non-English locale [line 28] (killed 1)
    ~ getMonthYearLabel does not throw and produces a sensible default-locale label when no locale is given [line 32] (covered 2)
  grid.spec.ts
    ✓ generateMonthGrid produces a fixed 6x7 matrix for year 2026 month 0 [line 15] (killed 19)
    ~ generateMonthGrid produces a fixed 6x7 matrix for year 2026 month 1 [line 15] (covered 34)
    ~ generateMonthGrid produces a fixed 6x7 matrix for year 2024 month 1 [line 15] (covered 34)
    ~ generateMonthGrid produces a fixed 6x7 matrix for year 2023 month 1 [line 15] (covered 34)
    ~ generateMonthGrid produces a fixed 6x7 matrix for year 2025 month 11 [line 15] (covered 34)
    ✓ generateMonthGrid flags leading days from the previous month as not current, with the correct calendar date [line 24] (killed 3)
    ~ generateMonthGrid flags trailing days from the next month as not current, with the correct calendar date [line 35] (covered 34)
    ~ generateMonthGrid flags every day belonging to the requested month as current [line 47] (covered 34)
    ~ generateMonthGrid places the month's first day in the top-left cell when it already falls on the grid's start weekday [line 56] (covered 34)
    ✓ generateMonthGrid produces a fully-shaped DayCell for every position in the grid [line 64] (killed 2)
    ~ generateMonthGrid echoes the requested year and month and formats a matching English month label [line 75] (covered 34)
    ✓ generateMonthGrid formats the month label using the supplied locale [line 83] (killed 1)
    ~ generateMonthGrid marks the injected current date as today and no other cell [line 89] (covered 34)
    ~ generateMonthGrid marks no cell as today when the mocked current date falls outside the grid [line 100] (covered 34)
    ~ generateMonthGrid produces 29 current-month days for February in a leap year [line 110] (covered 34)
    ~ generateMonthGrid produces 28 current-month days for February in a non-leap year [line 118] (covered 34)
    ~ generateMonthGrid defaults to a Sunday-start grid when no locale or weekStartsOn is given [line 126] (covered 34)
    ✓ generateMonthGrid shifts the first column to Monday when weekStartsOn is explicitly 1 [line 132] (killed 5)
    ✓ generateMonthGrid defaults weekStartsOn to the supplied locale's own convention [line 138] (killed 1)
    ~ generateMonthGrid lets an explicit weekStartsOn override the locale default [line 144] (covered 32)
    ✓ generateMonthGrid falls back to Sunday without throwing when a locale has no options object [line 150] (killed 1)
    ~ generateMonthGrid does not mutate the passed-in locale option object [line 158] (covered 34)
    ✓ getWeekdayLabels returns 7 labels in Sunday-start display order by default [line 168] (killed 9)
    ✓ getWeekdayLabels returns 7 labels in Monday-start display order when weekStartsOn is 1 [line 176] (killed 1)
    ✓ getWeekdayLabels reflects a custom locale's day names [line 184] (killed 2)
    ~ getWeekdayLabels defaults to English day names without a locale [line 200] (covered 20)

[Survived] ConditionalExpression
src/services/date-engine/grid.ts:19:7
-     if (weekStartsOn !== undefined) {
+     if (true) {
Tests ran:
    generateMonthGrid produces a fixed 6x7 matrix for year 2026 month 0
    generateMonthGrid produces a fixed 6x7 matrix for year 2026 month 1
    generateMonthGrid produces a fixed 6x7 matrix for year 2024 month 1
  and 23 more tests!


[Survived] EqualityOperator
src/services/date-engine/grid.ts:50:23
-     for (let index = 0; index < GRID_CELL_COUNT; index += 1) {
+     for (let index = 0; index <= GRID_CELL_COUNT; index += 1) {
Tests ran:
    generateMonthGrid produces a fixed 6x7 matrix for year 2026 month 0
    generateMonthGrid produces a fixed 6x7 matrix for year 2026 month 1
    generateMonthGrid produces a fixed 6x7 matrix for year 2024 month 1
  and 19 more tests!


Ran 11.43 tests per mutant on average.
--------------|------------------|----------|-----------|------------|----------|----------|
              | % Mutation score |          |           |            |          |          |
File          |  total | covered | # killed | # timeout | # survived | # no cov | # errors |
--------------|--------|---------|----------|-----------|------------|----------|----------|
All files     |  97.37 |   97.37 |       71 |         3 |          2 |        0 |        0 |
 date-math.ts | 100.00 |  100.00 |       22 |         0 |          0 |        0 |        0 |
 format.ts    | 100.00 |  100.00 |        5 |         0 |          0 |        0 |        0 |
 grid.ts      |  95.92 |   95.92 |       44 |         3 |          2 |        0 |        0 |
--------------|--------|---------|----------|-----------|------------|----------|----------|
[32m23:27:38 (67716) INFO HtmlReporter[39m Your report can be found at: file:///Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/reports/mutation/mutation.html
[32m23:27:38 (67716) INFO MutationTestExecutor[39m Done in 30 seconds.
