# Typed JSX variables trip `no-unsafe-assignment` in this package

`const row: JSX.Element = <tr />` inside a `helpers/*.tsx` module reports
`Unsafe assignment of an error typed value` (`@typescript-eslint/no-unsafe-assignment`), and
`Array.from({ length: n }, (_, i) => <tr />)` is typed `any[]` — so assigning it to a
`JSX.Element[]`-typed variable (or an interface property) fails lint, even though `tsc -p
tsconfig.json` is completely clean for the same code.

Cause is the ESLint side, not the code: `eslint.config.ts` uses `parserOptions.projectService`, and
the JSX expression type comes back as an error type / `any` there. Every existing helper avoids it
by never binding JSX to a typed variable — `renderSkeletonRows` and `renderFooter` both `return
Array.from(...)` / return an array literal straight from a function whose declared return type is
`JSX.Element[]` (and `no-unsafe-return` is off in that config).

Pattern that lints clean and keeps an exact rendered height to the caller:

```tsx
export function renderPlaceholderRows(options: Options, gapSize: number): PlaceholderRows {
  return { height: gap, rows: buildRows(options, rowSize, fullRowCount, remainder) }; // private fn, JSX.Element[] return type
}

function buildRows(...): JSX.Element[] {
  return Array.from({ length: limit }, (_, index) => (…)); // never assigned to a typed variable
}
```

Also note: an `Array.from({ length }, cb)` whose callback returns JSX yields `any[]` even when the
callback's return type is annotated, because the callback value is `any` — annotate/channel through
a function return type instead.
