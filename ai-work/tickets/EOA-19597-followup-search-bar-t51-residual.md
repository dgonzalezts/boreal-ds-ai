# Follow-up ticket from EOA-19597 — `bds-search-bar` pick/focus race (T51 residual)

**Source plan:** `ai-work/plans/EOA-19597-bds-search-bar-virtual-suggestions.md` (task T54)
**Suggested project:** EOA · type: Task · component: `bds-search-bar`

**Status (2026-10-28):** open, unreproduced. Do not "fix" it blind.
**Already shipped (do not re-implement):** the T51 fix itself is in EOA-19597 (`12850910`, specs `5b0ff0b6`) — `applyPickedFieldText()` focuses the input, writes the label and selects it synchronously. This ticket is only the 1-in-23 residual, not the original defect.
**Overlaps:** if a root cause is found, check `EOA-19597-followup-shared-components.md` §1 first (stale list listeners can produce a pick that does not commit, which looks similar).


## Summary

After the T51 fix (focus and select the picked label synchronously), one Chrome attempt out of 23 still showed the old symptom: `value` committed to the picked item while the field kept the typed text (`99`, caret `[2,2]`), and the next keystroke appended (`99z`). That is the shape of `applyPickedFieldText()` taking its `typedText !== null` early return.

Nineteen further attempts — including five verbatim replays of the failing sequence — passed, so there is no root cause yet.

## Next step

Instrument `typedText` across a pick with a state/`console.count` tracer, specifically when:
- the assigned value equals the current query, and
- the debounce commit that would clear the override is a no-op.

If reproducible, make the early return impossible during a pick (e.g. clear the typing override before the pick path evaluates it) and add a spec.

## Acceptance criteria

- Either a deterministic reproduction with a fix and a regression spec, or
- a documented argument that the state is unreachable from the public path, plus a guard that prevents the early return during a pick.
