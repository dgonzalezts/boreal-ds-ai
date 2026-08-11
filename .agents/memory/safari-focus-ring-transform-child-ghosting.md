# Safari native focus ring + CSS-transform child produces ghosted/duplicated render

Safari's native `outline` focus ring, when applied to an element containing a CSS `transform`-animated child (e.g. a chevron icon that rotates via `[aria-expanded='true'] { transform: rotate(180deg); }` with a `transition`), can render a ghosted/duplicated visual artifact — the icon appears to flicker between its pre- and post-rotation state, framed inside the native focus outline. Not reproducible in Chrome or Firefox.

Found on `bds-table`'s row-detail expand/collapse toggle button (`.bds-table__expand-toggle`) and confirmed as a missing-reset gap on `.bds-table__resize-handle` too.

**Root cause**: the element had a custom `:focus-visible { @include bds-focus-ring; }` box-shadow ring layered on **top of** Safari's still-active native `outline`, rather than replacing it. Safari's native outline appears to render on a separately composited layer that doesn't reliably invalidate when the underlying element's child undergoes a `transform` transition, producing the ghosting.

**Fix**: always pair `outline: none` with the custom `:focus-visible` box-shadow ring on the *same* element — this is already the established convention in `bds-button.scss`, `bds-checkbox.scss`, and `bds-button-group.scss`, but was missing on the two `bds-table` elements above. The fix is not Safari-specific CSS (no vendor hacks) — it's simply completing the existing reset-and-replace pattern everywhere it's used.

**Action for future components**: any interactive element with a custom `:focus-visible` ring must also declare `outline: none` on the same selector. Audit every new interactive/focusable element against this pairing before considering focus styling complete — especially if that element has any CSS-transform-animated child (icon rotation, chevron flip, etc.), since that combination is Safari's specific trigger for this bug.

**Source**: EOA-16000 `bds-table` v4 Safari QA session.
