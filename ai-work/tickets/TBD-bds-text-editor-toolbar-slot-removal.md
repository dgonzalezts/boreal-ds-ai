# TBD — bds-text-editor: stale divider after a slotted toolbar tool is removed

**Ticket:** TBD
**Status:** Fixed in a9194ada on feature/EOA-18739_text-editor-v1_DG (no separate ticket needed)
**Goal:** Hide the toolbar-slot divider, and the toolbar itself when nothing else is left, as soon as the last slotted tool is removed.

## Jira fields (copy when creating)

- **Summary:** Text Editor: divider stays visible after the last slotted toolbar tool is removed
- **Type:** Bug
- **Links:** found during EOA-18739 (v1), while fixing the toolbar order after runtime updates

## Problem

When a consumer removes the last tool from the `toolbar` slot after the first render, the editor keeps a trailing divider. With `toolbar=""` the empty toolbar also stays visible.

Steps to reproduce:

1. Render `<bds-text-editor toolbar="fields,link">` with fields set.
2. After it renders, append `<bds-button slot="toolbar">X</bds-button>` to the editor. The toolbar shows `fields+link | divider | X`.
3. Remove that button (`editor.removeChild(button)`, or a React or Vue conditional render).

Expected: `fields+link`. Actual: `fields+link | divider`.

Reproduced in Storybook and in standalone builds with Stencil 4.45.2 and 4.45.5, with or without the `.bds-text-editor__tools` wrapper.

## Cause

`hasToolbarSlot` is only recomputed by the `MutationObserver` in `observeToolbarSlot()`. It observes the host with `{ childList: true }`, so it only sees changes to the host's direct children.

Stencil's light-DOM slot handling moves a slotted tool from the host into the toolbar (inside `.bds-text-editor__tools`). Removing it later changes the wrapper's children, not the host's, so the observer never fires. `hasToolbarSlot` stays `true` and `renderToolbar` keeps rendering `divider-slot`.

## Proposed fix

- Also observe `.bds-text-editor__tools` with `{ childList: true }` (re-attach when the toolbar is re-created, for example after `readOnly` toggles), and run `syncToolbarSlot` from it.
- Do not use `subtree: true` on the host: it would fire on every keystroke in the editable area.

## Acceptance Criteria

- [ ] Removing the last slotted tool removes `divider-slot`.
- [ ] With `toolbar=""`, removing the last slotted tool hides the toolbar.
- [ ] Removing one of two slotted tools keeps the divider.
- [ ] Adding a tool again after removal shows the divider again, in the right place.
- [ ] Works when the editor toggles `readOnly` between the changes.
- [ ] Verified in Storybook (Toolbar Slot story) and in the React and Vue wrappers.

## Tests

- Spec in `bds-text-editor.basics.spec.ts` under "toolbar order after updates inside bds-toolbar" (it registers `BdsToolbar` so the slot relocation happens): mount with a slotted tool, remove it, trigger the wrapper observer, expect no `bds-divider`.
- Update "observes only direct child changes of the host", which asserts a single observer.
