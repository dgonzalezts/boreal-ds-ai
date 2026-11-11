# Removing a focused element from the DOM fires `blur` in Chrome, not in WebKit

When a Stencil re-render swaps out a subtree that contains the currently focused `<input>` (e.g. a conditional branch that renders `div > bds-text-field` in one state and `bds-select > bds-text-field` in another), the field is destroyed and focus is lost. Whether the component's own `blur` handlers run for that loss is **engine-dependent**:

- **Chrome** fires the input's `blur` (and therefore the component's `onBlur`/`bdsBlur` path) during the removal.
- **WebKit (Playwright WebKit) fires nothing** — the handler never runs, so any state that handler would have reset stays stale.

Confirmed by direct reproduction on `bds-search-bar` (T52, EOA-19598): switching `mode="search"` → `mode="list"` cleared the field in Chrome (because `handleBlur` nulled the `typedText` override) and kept the typed text in WebKit (override survived and was re-applied by the next render from `fieldText`). `value` was `''` in both, which is what made it look like a "DOM text" bug rather than a missing-lifecycle-callback bug. Harness: chrome + `playwright-cli --browser=webkit` on the same page, reading `document.activeElement`, the input's `value`, and a `bdsBlur` listener.

**Rule for future work:** never let component state that a `blur` handler would clear depend on that handler running when a re-render destroys the focused node. Reset it explicitly at the state transition that causes the swap (a `@Watch` on the prop being changed), so both engines converge. The fix shape used by `bds-search-bar` is a private `@Watch('mode')` that, when the new mode is `list`, cancels any pending debounce, drops the typing override, and re-derives the "has value" flag from the committed prop — leaving the field to be rendered purely from committed state.

**Corollary (still engine-dependent, do not "fix" by guessing):** if the same `blur` path also triggers a *visible* action — `bds-search-bar` collapses a `minimized` bar when it blurs while empty — that action will fire in Chrome only. Treat it as a focus/visibility difference separate from field text; if it must be deterministic, drive it from the state transition, never from the removal `blur`.

Verified with Google Chrome (141) and Playwright WebKit; Playwright's WebKit is not Safari.app (see `playwright-webkit-is-not-safari.md`), so a macOS Safari.app confirmation is still a manual step.
