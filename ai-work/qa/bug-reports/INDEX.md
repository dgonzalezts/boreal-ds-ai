# QA Bug Reports Index

## Open

| File | Ticket | Component | Severity | Priority | Title |
| ---- | ------ | --------- | -------- | -------- | ----- |
| [2026-07-06-bds-search-bar-bug-001.md](2026-07-06-bds-search-bar-bug-001.md) | — | `bds-search-bar`, `VirtualScrollController` | Medium | P2 | `bds-search-bar`/`bds-select` suggestion-list "virtualization" only repositions DOM nodes — it does not reduce mounted component count |

## Fixed

| File | Ticket | Component | Severity | Priority | Title |
| ---- | ------ | --------- | -------- | -------- | ----- |
| [EOA-10544-bds-select-bug-001.md](EOA-10544-bds-select-bug-001.md) | EOA-10544 | `bds-select` | High | P1 | `bds-select` — `valueChange` and `bdsChange` fire twice per selection with inconsistent `detail` values |
| [EOA-10544-bds-select-bug-002.md](EOA-10544-bds-select-bug-002.md) | EOA-10544 | `bds-select` | High | P1 | `bds-select` — Popover does not close after item selection |
| [EOA-10544-bds-select-bug-003.md](EOA-10544-bds-select-bug-003.md) | EOA-10544 | `bds-select` | High | P1 | `bds-select[multiselect]` — `max-tags` limit on slotted `bds-tag-field` is not enforced for list selections |
| [EOA-10062-bds-tooltip-bug-001.md](EOA-10062-bds-tooltip-bug-001.md) | EOA-10062 | `bds-tooltip`, `anchoredMixin`, `bds-typography`, `bds-text-field` | Medium | P2 | Tooltip anchors to form field container instead of trigger icon |
| [EOA-14605-bds-search-bar-bug-001.md](EOA-14605-bds-search-bar-bug-001.md) | EOA-14605 | `bds-search-bar` | Medium | P2 | `bds-search-bar` — duplicate loading spinner, over-broad style overrides, distorted spinner, and non-resolving width |
| [EOA-15147-bds-tooltip-bug-001.md](EOA-15147-bds-tooltip-bug-001.md) | EOA-15147 | `bds-tooltip` | Medium | P2 | `stayOnHover` never keeps the tooltip open, and the Storybook controls for `hideArrow`/`stayOnHover` have no effect |
| [2026-07-29-bds-dialog-bug-001.md](2026-07-29-bds-dialog-bug-001.md) | EOA-16315 | `bds-dialog` | High | P1 | `bds-dialog` closes when clicking anywhere inside its own content, not just the backdrop |
| [2026-08-06-bds-button-accessible-name-remaining.md](2026-08-06-bds-button-accessible-name-remaining.md) | EOA-17133 | `bds-pagination`, `bds-dialog`, `bds-drawer`, `bds-popover` | Low | P3 | Remaining `[BorealDS Button] No accessible name found` sources — pagination numbered/ellipsis controls and closable overlay buttons |
| [2026-08-18-bds-popover-bug-001.md](2026-08-18-bds-popover-bug-001.md) | EOA-17085 | `bds-popover`, `bds-tooltip` | Low | P3 | `data-hidearrow` attribute name is inverted from its actual meaning (present when the arrow IS shown) |
| [2026-08-19-shared-field-error-message-bug-001.md](2026-08-19-shared-field-error-message-bug-001.md) | EOA-17093 | `bds-text-field`, `bds-tag-field`, `bds-number-field` | Medium | P2 | `errorMessage` never overrides the built-in validation message unless `error` is also manually forced `true` |
