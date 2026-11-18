# ADR 0021 — bds-text-editor value contract and field tokens

**Date:** 2026-11-17
**Status:** Proposed (EOA-18739)

---

## Context

`bds-text-editor` v1 is a message composer. Its `value` is what product apps store, send and later set back into the editor, so its format is a long-lived contract: changing it later breaks stored data, not just code.

The real applications show that consumers need plain text:

- SMS and WhatsApp counters ("Characters: 5/160", "equals 1 Msg.").
- WhatsApp-style formatting buttons, which act on text markers, not HTML.
- Subject lines.

They also insert **fields**: placeholders that the backend replaces at send time. Each product writes them differently:

| Product field | Format |
| --- | --- |
| WhatsApp templates | Numbered placeholders: `{{1}}`, `{{2}}` |
| Sender identification | Bracketed names: `[URL_Identify_Senders]` |
| Contact data | Dropdown labels: `DF-Name`, `DF-Email` |

Users must not be able to break a field by editing part of it, and the field must read as a name ("Name"), not as syntax ("{{1}}").

ProseMirror is the engine (ADR 0020), so the content is a schema-defined document that the component serialises to `value`.

---

## Non-Goals

- Does not define HTML output. v3 adds an HTML mode alongside this contract; plain text remains the default.
- Does not define how fields count towards the limit (ADR 0022).
- Does not resolve field values. Replacing tokens with real data stays a backend concern.

---

## Options Considered

### Value format

| Option | Assessment |
| --- | --- |
| **A1 — Plain text with `\n` between paragraphs** | Matches every message channel and the existing CKEditor 4 usage. Stores and diffs easily. Accepted. |
| A2 — HTML | Every consumer would have to strip tags before sending SMS or WhatsApp. Deferred to v3 as an opt-in mode. |
| A3 — ProseMirror JSON | Leaks the engine into consumer storage and couples stored data to our schema. Rejected. |

### Field token syntax

| Option | Assessment |
| --- | --- |
| B1 — One fixed syntax (for example `{{name}}`), mapped by each app | Every app would convert values on the way in and out. Rejected. |
| B2 — A consumer-supplied regex pattern | Error-prone, and it can match text the user typed by hand. Rejected. |
| **B3 — Each field declares its exact token** | `{ token, label, length? }`. Covers every format above with no configuration. Accepted. |

### Field representation while editing

| Option | Assessment |
| --- | --- |
| C1 — Highlighted raw token text | Can be partly deleted, and shows syntax instead of a name. Rejected. |
| C2 — The `bds-tag` element inside the text | Adds a focusable close button inside editable text, changes the line height, and costs a custom element per chip. Rejected. |
| **C3 — An atomic inline node** | Rendered as a lightweight chip styled with `bds-tag` tokens and showing `label`. Accepted. |

---

## Decision

- **`value` is a plain string.** Paragraphs are joined with `\n`; `\r\n` is normalised to `\n` on input. An empty editor is `''`.
- **Field definition:** `ITextEditorField = { token: string; label: string; length?: number }`, passed in the `fields` JS property.
- **Serialising:** a field is written as its exact `token`.
- **Parsing (on mount, when `value` changes, and when `fields` changes):**
  - Exact occurrences of configured tokens become field nodes.
  - The **longest token matches first**, so `{{10}}` is never read as `{{1}}` followed by `0`.
  - Text that is not a configured token stays plain text.
  - When `fields` changes, chips for removed fields turn back into plain token text.
- **Duplicate tokens:** the first definition wins, with a development warning.
- **Round trip:** `serialize(parse(x)) === normalise(x)` for every input. Unit tests enforce it.
- **Chip:** an inline, atomic, selectable ProseMirror node, rendered as a non-editable span styled with `bds-tag` tokens. It shows `label` with visually hidden prefix text (the `fieldPrefix` label, "Field: " by default). Backspace removes the whole chip.
- **Readonly and disabled:** the same chips render with editing off.

---

## Consequences

- **No conversion layer:** consumers keep their own token formats.
- **Unique tokens:** consumers must make tokens unique, and the documentation must say so.
- **Literal token text:** a user who types a configured token by hand gets a chip once the value is next parsed (on mount, when the value is set, or when `fields` changes). This is accepted: the stored value is identical either way.
- **v3 and beyond:** the HTML mode must keep this contract unchanged for plain-text consumers, so HTML becomes an opt-in format.
- **Migration from CKEditor 4:** if those values contain the same tokens, they load as-is. If they contain HTML, apps must strip it before setting `value` (until v3).
