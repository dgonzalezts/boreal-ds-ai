# ADR 0022 — Character counting and limits in bds-text-editor

**Date:** 2026-11-17
**Status:** Proposed (EOA-18739)

---

## Context

Message composers show a counter, and most have a limit (160, 1000, 4096). Notion's guidance:

- Show the counter as a ratio.
- Use it only when a limit exists.
- "Text exceeds the character limit" is an error case.

Three questions need a fixed answer:

1. **What counts as one character?** JavaScript's `string.length` counts UTF-16 code units. 😀 is 2 units, 🇨🇴 is 4, and 👨‍👩‍👧 is 8, while a person sees one character each.
2. **How do fields count?** The real applications count fields towards the limit ("the length of the message is approx. when replacement field used").
3. **What happens at the limit?** Block input, or allow overflow and show an error.

**Precedent:** `bds-text-field` counts with `value.length` (`bds-text-field.tsx`, `currentCharCount`) and enforces its limit through the native `maxLength`. That counts UTF-16 units and blocks typing. Nothing in the codebase uses `Intl.Segmenter` yet.

A later need is also known: SMS segment counting ("24/1000 equals 1 Msg.").

---

## Non-Goals

- Does not implement SMS segment counting.
- Does not change `bds-text-field` (see Consequences).
- Does not decide how number-based announcements such as "N characters left" are localised. ADR 0014 requires a separate ADR for that before such a string ships (planned as ADR 0025 for v2).

---

## Options Considered

### Unit of count

| Option | Assessment |
| --- | --- |
| A1 — UTF-16 code units, like `bds-text-field` | Consistent with the sibling component, but an emoji shows as 2 or more, which users read as a bug. Rejected for the editor. |
| **A2 — Graphemes (`Intl.Segmenter`, `granularity: 'grapheme'`)** | One user-perceived character counts as 1. Supported in all target browsers. Accepted. |

### Field weight

| Option | Assessment |
| --- | --- |
| B1 — Count the token's characters only | Wrong for numbered tokens: `{{1}}` is 5 characters but may expand to a 20-character name. |
| **B2 — The field's declared `length`, or its token's grapheme count when `length` is not set** | Lets consumers state the expected expansion. Accepted. |

### Behaviour at the limit

| Option | Assessment |
| --- | --- |
| **C1 — Hard block, like `bds-text-field`** | Typing past the limit is blocked; paste is cut to the space left at whole graphemes; a field or emoji that does not fit is not inserted, and its tool is disabled. Accepted. |
| C2 — Allow overflow with an error state | Friendlier for long drafts, but inconsistent with `bds-text-field`. Rejected. |
| C3 — Consumer choice through a prop | Extra API and test surface. Can be added later without a breaking change. Deferred. |

### Extension point for SMS

| Option | Assessment |
| --- | --- |
| **D1 — The counter is a pure strategy function `(doc, fields) => number`** | An SMS strategy (GSM-7 vs UCS-2 encodings, 160/153 and 70/67 per segment) can be added later without changing callers or the default. Accepted. |

---

## Decision

- **Count:** graphemes of the text, plus each field's weight (`length`, or its token's grapheme count), plus 1 for each paragraph break.
- **Limit:** `charCount` sets both the counter's maximum and a hard limit. `charCount <= 0` means no limit.
- **Enforcement:**
  - A ProseMirror plugin rejects user changes that would exceed the limit.
  - Paste is truncated to whole graphemes.
  - Insertions that do not fit return `false` and change nothing.
- **App-set values:** a `value` set by the app, or a form reset, may exceed the limit. It is kept, and the component reports `tooLong` validity and shows the error state. This covers the Notion "Text exceeds the character limit" case.
- **Code shape:** the count comes from one pure function, shaped as a strategy, so SMS segments can be added later as another strategy.
- **IME composition:** if rejecting changes during IME composition proves harmful (checked in v2), the plugin lets the composition finish and trims to the limit at `compositionend`. The observable rule, "never above the limit after an edit", does not change.

---

## Consequences

- **Two counting rules exist in the design system.** `bds-text-field` counts UTF-16 units, so "😀" counts as 2 there and 1 in `bds-text-editor`. This is accepted for now, because changing `bds-text-field` changes how its native `maxLength` behaves.
- **Follow-up for `bds-text-field`:** log a separate ticket to decide whether it adopts grapheme counting (which would require replacing native `maxLength` with its own limit logic).
- **Approximate counts:** field weights are estimates, so the count is approximate whenever fields are present. Product copy (helper text) should say so where it matters, as the real applications already do.
- **Testing:** counting is pure and table-tested (emoji sequences, flags, families, accented characters, field weights). It is part of the mutation-testing gate.
