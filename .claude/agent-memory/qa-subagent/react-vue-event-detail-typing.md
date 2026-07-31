# Typing Bds* event handlers in React/Vue playground scenarios

Never hand-roll the event-detail type for a `Bds*` custom event (e.g. `bdsExpand`, `bdsSelect`). The library's real event-detail types use the generic `RowData = Record<string, unknown>` (or similarly generic shapes) — a hand-written type like `CustomEvent<{ row: OrderRow }>` (a concrete app-specific shape) does **not** structurally satisfy the real `BdsTableCustomEvent<BdsExpandEventDetail>` (`row: RowData`), producing a genuine TS error on the event-binding prop:

```
Type '(e: CustomEvent<{ row: OrderRow }>) => void' is not assignable to type '(event: BdsTableCustomEvent<BdsExpandEventDetail>) => void'.
  ...
    Type 'RowData' is missing the following properties from type 'OrderRow': id, name, tier, history
```

## Neither `@telesign/boreal-react` nor `@telesign/boreal-vue` re-export the underlying event-detail types

`BdsExpandEventDetail`, `BdsTableCustomEvent`, etc. are NOT exported from either wrapper package's top level — only their own generated `BdsTableEvents`-style aggregate types are. Importing them directly (`import { BdsExpandEventDetail } from '@telesign/boreal-react'`) fails with `TS2614`/`TS2724`.

## React fix — derive the handler type from the component's own prop signature

```tsx
import { type ComponentProps } from 'react';
import { BdsTable } from '@telesign/boreal-react';

type BdsExpandEvent = Parameters<NonNullable<ComponentProps<typeof BdsTable>['onBdsExpand']>>[0];
type BdsExpandEventDetail = BdsExpandEvent['detail'];

const handleExpand = (e: BdsExpandEvent) => {
  const row = e.detail.row as OrderRow; // safe narrowing where concrete fields are actually used
  const table = e.target; // already typed as HTMLBdsTableElement on the real event type — no `as HTMLElement` cast needed
  ...
};
```
This can never drift from the library's actual contract since it's derived, not duplicated.

## Vue fix — type against the real generic shape, cast where used

Vue's wrapper doesn't expose an equivalent `ComponentProps`-style extraction path as cleanly. Simplest robust fix: define a local type matching the library's actual generic contract exactly, then cast:

```ts
type RowData = Record<string, unknown>;
type BdsExpandEventDetail = { rowId: string; expanded: boolean; row: RowData };

const handleExpand = (e: CustomEvent<BdsExpandEventDetail>) => {
  const row = e.detail.row as OrderRow;
  ...
};
```

## `vue-tsc --noEmit` (CLI) can be clean while the IDE still flags the same error

Confirmed this session: running `npx vue-tsc --noEmit` from the terminal reported zero errors for an `App.vue` that the user's actual IDE (Vue/Volar language server) correctly flagged with the exact type mismatch above. Don't treat a clean CLI `vue-tsc` run as proof the binding type-checks — the IDE's template-binding strictness can differ from the CLI's default config. Always re-verify by reading the file fresh and reasoning through the actual structural type match, not just trusting one tool's silence.
