# Cally Library Usage in `bq-date-picker`

Research notes on how the [Cally](https://github.com/WickyNilliams/cally) calendar web component library is
used by `packages/beeq/src/components/date-picker/bq-date-picker.tsx`.

## 1. Dynamic script loading (not bundled)

Cally is not an npm dependency — it's lazy-loaded from a CDN at runtime via helpers imported from
`./libs/callyLibrary`:

```ts
import { isCallyLibraryLoaded, loadCallyLibrary } from './libs/callyLibrary';
```

In `componentWillLoad()`:

```ts
async componentWillLoad() {
  if (!isClient() || this.isCallyLoaded) return;
  try {
    await loadCallyLibrary();
    this.isCallyLoaded = isCallyLibraryLoaded();
  } catch (error) {
    console.error(error);
  }
}
```

`loadCallyLibrary()` (in `libs/callyLibrary.ts`) injects a `<script type="module">` tag pointing to
`https://unpkg.com/cally@0.9.0/dist/cally.js` with an SRI integrity hash, using a singleton-promise
pattern so concurrent component instances don't load it multiple times. Once loaded, it defines Cally's
web components (`calendar-date`, `calendar-range`, `calendar-multi`, `calendar-month`) as custom elements
globally.

The `isCallyLoaded` `@State()` flag gates all Cally-related rendering — nothing Cally-related renders
until the script has loaded.

## 2. Selecting the right Cally container element

`CALENDAR_TYPE_MAP` (from `./helper/constants.ts`) maps the component's `type` prop to the corresponding
Cally custom element tag:

```ts
const CALENDAR_TYPE_MAP = {
  single: 'calendar-date',
  multi: 'calendar-multi',
  range: 'calendar-range',
} as const;
```

The private getter `calendarType` resolves this, and in `render()` it's assigned to `CallyCalendar` and
used as a dynamic JSX tag:

```tsx
const CallyCalendar = this.calendarType;
...
{this.isCallyLoaded && (
  <CallyCalendar ...>
```

## 3. Rendering and configuring the Cally element

Inside `render()`, the Cally container (`calendar-date`/`calendar-range`/`calendar-multi`) is rendered
with props/attributes that map directly to Cally's API (per the `TCalendarDate` type): `firstDayOfWeek`,
`isDateDisallowed`, `locale`, `max`, `min`, `months`, `pageBy` (mapped from `monthsPerView`),
`showOutsideDays`, `tentative`, `value`, plus event handlers `onChange`, `onRangestart`, `onRangeend`.

It also nests Cally's expected children:

- `<bq-icon slot="previous">` / `<bq-icon slot="next">` for custom nav icons (Cally supports
  `previous`/`next` slots).
- One or more `<calendar-month>` children generated via `generateCalendarMonth`/`generateCalendarMonths`,
  each with an `offset` prop (Cally's way of showing multiple months in `range`/`multi` mode).

Shadow-DOM `exportparts` from constants (`CALENDAR_CONTAINER_EXPORT_PARTS`, `CALENDAR_MONTH_EXPORT_PARTS`)
re-expose Cally's internal shadow parts so BEEQ consumers can style them via CSS `::part()`.

## 4. Imperative ref access

A ref callback stores the actual Cally DOM element instance in `callyElem`:

```tsx
ref={(elem: TCalendarDate) => { this.callyElem = elem; }}
```

This typed ref (`TCalendarDate`, describing Cally's public element API) is used in `setFocusedDate()` to
imperatively set `callyElem.focusedDate` — done via the ref rather than as a JSX prop because "the Cally
element does not re-render" when passed as a prop, i.e., Cally's own re-render/property-observation cycle
doesn't pick up prop changes reliably from Stencil's JSX diffing for that particular field.

## 5. Handling Cally's events

Cally emits DOM events consumed by BEEQ:

- `onChange` → `handleCalendarChange`: syncs `value`, updates the display/input, closes the panel (unless
  `type === 'multi'`), emits `bqChange`.
- `onRangestart` → `handleCalendarRangeStart`: sets `tentative` to the event detail (the range start).
- `onRangeend` → `handleCalendarRangeEnd`: marks `hasRangeEnd = true`.

## 6. Summary

- **Loaded lazily/on-demand** from a CDN as a Web Component library (`libs/callyLibrary.ts`), not a
  build-time dependency.
- **Mapped by type** to one of three Cally custom elements (`calendar-date`, `calendar-multi`,
  `calendar-range`) via `CALENDAR_TYPE_MAP`.
- **Rendered conditionally**, only after the script finishes loading (`isCallyLoaded`).
- **Configured via props** that mirror Cally's public API (`TCalendarDate` type), including locale,
  min/max, disallowed dates, month count, etc.
- **Controlled imperatively** for `focusedDate` via an element ref, since JSX prop passing doesn't
  trigger Cally's internal update.
- **Wired for events** (`change`, `rangestart`, `rangeend`) to drive BEEQ's own value/state model and
  emit BEEQ's `bqChange`/related events.

---

## Date handling and internationalization

Cally handles i18n for the *calendar grid itself*, but all the text-input date parsing/formatting logic
is custom code written by BEEQ, not provided by Cally.

### What Cally provides

Cally is a calendar-grid web component, not a full date picker with a text input. It accepts a few
i18n-related props that `bq-date-picker.tsx` passes straight through:

- `locale` — used internally by Cally (via `Intl.DateTimeFormat`) to render localized month/weekday
  names and date labels in the calendar grid.
- `firstDayOfWeek` — controls which day starts the week (locale-dependent convention, e.g. Monday in
  `en-GB` vs Sunday in `en-US`), but BEEQ still has to pass the value in explicitly — Cally doesn't infer
  it from `locale`.
- `showOutsideDays`, `min`/`max`, `isDateDisallowed` — calendar behavior, not i18n per se.

So Cally's date handling is limited to: rendering a calendar of a given month/range using ISO date
strings (`value`, `tentative`, `min`, `max` are all plain `YYYY-MM-DD` strings) and localizing the
*displayed calendar labels*.

### What BEEQ implements itself

Everything related to the **text input** (parsing what the user types, formatting what's displayed,
converting to/from ISO) is hand-rolled in `shared/utils/date/`, imported into `bq-date-picker.tsx`, and
Cally has no involvement:

- **`dateFormatting.ts`**:
  - `formatDisplayValue` — formats the ISO value(s) for display in the input, locale-aware, using
    `Intl.DateTimeFormat` (including `.formatRange()` for `type="range"`). Caches formatter instances
    (`getDateFormatter`).
  - `extractFocusedDate`, `clampDateToRange` — helpers for calendar focus/min-max logic.
- **`dateParsing.ts`**:
  - `parseDateInput` — a locale-aware free-text parser (handles ISO, `"30 May 2024"`,
    `"May 30, 2024"`, `"30/05/2024"`, etc.), using `Intl.DateTimeFormat` to build a localized month-name
    lookup table (`getMonthNamesForLocale`) and a DD/MM vs MM/DD heuristic (`parseNumericDate`) based on
    locale (e.g. `en-US`/`en-CA` → MM/DD).
  - `toISODateString` / `getTodayISO` — convert `Date` → ISO string, using the fixed `fr-CA` locale as a
    trick to get `YYYY-MM-DD` formatting (`ISO_DATE_LOCALE`).
  - `isValidISODate` — strict ISO format + real-date validation.

These utilities are all built on the native `Intl` API — none of this comes from the Cally library.

### Summary table

| Concern | Handled by |
|---|---|
| Calendar grid rendering, localized month/weekday labels, first-day-of-week layout | **Cally** (via `locale`, `firstDayOfWeek` props) |
| Free-text input parsing (multiple formats, locale-aware) | **BEEQ** (`dateParsing.ts`) |
| Display-value formatting (single/multi/range) | **BEEQ** (`dateFormatting.ts`, via `Intl.DateTimeFormat`) |
| ISO conversion, date validation, clamping to min/max | **BEEQ** (`dateFormatting.ts` / `dateParsing.ts`) |

So Cally contributes calendar-level i18n (rendering), while all the "smart" date handling — parsing user
input in various formats and locale-aware formatting for the input field — is BEEQ's own implementation
layered on top of Cally.

---

## Date calculations and leap years

Neither BEEQ nor Cally implements leap-year math explicitly — there's **no custom leap-year algorithm
anywhere** in this component. All date/leap-year correctness comes for free from the native JavaScript
`Date` object, which both sides rely on.

### How leap years are actually handled

1. **No explicit leap-year logic exists.** A search for `leap`, `isLeapYear`, `daysInMonth` across
   `date-picker/` and `shared/utils/` turns up nothing in the implementation — only in the test file
   (`__tests__/date.spec.ts`), which verifies the *behavior* rather than testing a dedicated leap-year
   function.

2. **BEEQ's validation relies on `Date` object overflow/rollover.** In `dateParsing.ts`:

   ```ts
   const isDateValid = (day: number, month: number, year: number): boolean => {
     const date = new Date(year, month, day);
     return date.getDate() === day && date.getMonth() === month && date.getFullYear() === year;
   };
   ```

   `new Date(2024, 1, 29)` → Feb 29, 2024 stays Feb 29 (2024 is a leap year), so validation passes.
   `new Date(2023, 1, 29)` → JS rolls this over to March 1, 2023 (2023 isn't a leap year), so
   `getDate() === 29` fails and `getMonth() === 1` fails → correctly rejected. This is confirmed by the
   tests: `2024-02-29` → valid, and `2023-02-29` → invalid, `2023-02-28` → valid.

   The same trick invalidates non-existent dates in general (e.g. `isValidISODate('2024-02-30')` →
   `false`) — the JS engine's own Gregorian calendar math (which correctly implements the leap-year rule:
   divisible by 4, except century years unless divisible by 400) is the sole source of truth. BEEQ never
   encodes the leap-year rule itself; it just detects when `Date` silently "corrected" an invalid input.

3. **`toISODateString`/`getTodayISO`** also just delegate to `Date.prototype.toLocaleDateString`, so any
   date arithmetic (day/month/year rollover, leap days) is handled by the JS runtime's `Intl`/`Date`
   implementation, not custom code.

### Cally's side

Cally (the calendar-grid web component) must internally compute the number of days per month, including
Feb 28 vs 29, to render its grid correctly and to handle `offset`-based month navigation — but that logic
is entirely internal/opaque to BEEQ. BEEQ doesn't call into or duplicate Cally's calendar-math; it only
feeds Cally ISO date strings (`value`, `min`, `max`, `tentative`) and lets Cally render whatever calendar
layout is correct for that month/year.

### Summary table

| Aspect | Implementation |
|---|---|
| Leap-year rule itself | Not reimplemented anywhere — delegated to native JS `Date`/`Intl` engine |
| Input validation (e.g. rejecting Feb 30, Feb 29 in non-leap years) | BEEQ's `isDateValid`/`isValidISODate`, via `Date` rollover detection |
| Calendar grid rendering (correct days per month) | Handled internally by Cally, opaque to BEEQ |
| Date arithmetic (ISO conversion, "today") | Native `Date`/`Intl.DateTimeFormat`, no custom math |

Date calculations and leap-year correctness are **outsourced to the JavaScript `Date`/`Intl` APIs** on
both sides — BEEQ never hand-rolls calendar math, it just validates against what `Date` naturally does.
