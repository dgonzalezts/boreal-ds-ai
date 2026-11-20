---
name: bds-text-editor-core-spec-mechanics
description: How the bds-text-editor core helper specs (serializer/counter/plugins) run in Stencil jest without an EditorView
metadata:
  type: project
---

Pure-state ProseMirror specs work in Stencil's jest env with no `newSpecPage`: `EditorState.create`, `state.applyTransaction(tr).transactions.length === 0` proves a `filterTransaction` rejection. Plugin props are callable via `plugin.props.handlePaste?.call(plugin, viewStub, eventStub, slice)` with `{ state, dispatch } as unknown as EditorView`; a keymap stub view must use an arrow-function `dispatch` (prosemirror-keymap calls `view.dispatch` unbound).

- `navigator.platform` is `"MacIntel"` in mock-doc and the getter is configurable: `jest.spyOn(navigator, 'platform', 'get')` works for `createTextEditorPlugins`' Apple check, but prosemirror-keymap decides `Mod` once at import, so compute the Mod modifier at module top.
- `Intl.Segmenter` fallback: cached lazily, so set `Intl.Segmenter` undefined with `Object.defineProperty` *before* `jest.isolateModules(() => jest.requireActual(...))` and keep it undefined while calling; restore in `afterEach`.
- Widget decoration DOM: `(decoration as unknown as { type: { toDOM: () => HTMLElement } }).type.toDOM()` works.
- `NodeType.create()` with a required attr and no attrs does NOT throw; use `node.textContent` (honours `leafText`), not `textBetween(0, nodeSize)`, on a leaf.
- Observed paste behaviour left untested (contract undecided): `buildPasteTransaction` can keep a paragraph break and drop the next line's text, leaving a dangling empty paragraph (`'a\nb\nc'`, max 4 gives `'a\nb\n'`).
