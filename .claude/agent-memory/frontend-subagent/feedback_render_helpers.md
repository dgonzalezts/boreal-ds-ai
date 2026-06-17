---
name: feedback_render_helpers
description: Extract private render helper methods when render() has multiple structural sections — keeps each method focused and testable
metadata:
  type: feedback
---

When a component's `render()` produces multiple independent structural regions (header, body, empty state, toolbar, etc.), extract each region into a private method (e.g. `renderHeader()`, `renderBody()`, `renderCell()`).

**Why:** A single monolithic `render()` with many conditional branches becomes hard to read and hard to reason about in isolation. Helper methods give each region a clear name, a clear return type (`JSX.Element`), and a natural boundary for future changes. The `bds-table` component uses this pattern: `render()` calls `renderHeader()` and `renderBody()`, which in turn calls `renderCell()`.

**How to apply:** When `render()` grows beyond ~20 lines or contains more than one `if`/ternary for structural variation, extract the regions. Name helpers `render{Region}()`. Keep them `private` — they are not part of the component's public API.
