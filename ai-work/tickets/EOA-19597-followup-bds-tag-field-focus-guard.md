# Follow-up ticket from EOA-19597 — `bds-tag-field` unguarded focus forwarder

**Source plan:** `ai-work/plans/EOA-19597-bds-search-bar-virtual-suggestions.md` (task T59)
**Suggested project:** EOA · type: Task · component: `bds-tag-field`

**Status (2026-10-28):** open (latent — no suite currently triggers it).
**Already shipped (do not re-implement):** the same guard already exists in `bds-text-field` (`605049af`) with a regression spec; copy that shape rather than designing a new one.
**Overlaps:** shares the `focus`-forwarder pattern with `EOA-19597-followup-shared-components.md` §6; if that decision lands (`isDisabled` handling), apply the same rule here.


## Summary

`bds-tag-field.tsx` (~line 448) forwards host focus to its inner input with the same unguarded `onFocus` that caused a mock-doc stack overflow in `bds-text-field` (fixed in EOA-19597, commit `605049af`).

It is currently **latent**: no tag-field spec calls `input.focus()`, so the suite logs no overflow. The first spec that does will hit `RangeError: Maximum call stack size exceeded`, caught by mock-doc and printed via `console.error` — the suite stays green, hiding it.

## Fix

Apply the same guard as `bds-text-field`:

```tsx
onFocus={(e: FocusEvent) =>
  e.target === e.currentTarget && !this.isDisabled && input?.focus()
}
```

## Acceptance criteria

- A spec that focuses the inner input produces no `Maximum call stack size exceeded` output and asserts the host forwarder ran once.
- A spec asserts a bubbled `focus` from the input does not forward again.
- Real-browser check: clicking the field's padding/label still focuses the input once.
