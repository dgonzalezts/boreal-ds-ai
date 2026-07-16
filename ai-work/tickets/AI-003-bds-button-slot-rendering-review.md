# AI-003 — bds-button Slot Rendering & Conditional Styling Review

**Ticket:** AI-003 (internal)
**Goal:** Keep `bds-button`'s existing CSS `:empty`-based approach for collapsing empty slot containers (icon, text, badge) — no code rewrite. Document the approach's dependency on Stencil's non-shadow slot polyfill behavior, and validate it doesn't regress any of `bds-button`'s many internal consumers.

**Final decision (supersedes the original "keep CSS-only" decision below — see Background for why):** `:empty` was kept for the **icon** and **badge** wrappers (named slots — structurally safe, confirmed correct in both plain HTML and real Lit/Storybook rendering). It was **replaced with a JS-driven `hasTextContent` `@State` + modifier class** for the **text** wrapper only, because real Storybook/Lit rendering (not plain HTML) leaves non-zero-length whitespace text nodes in the *default* slot specifically, which defeats `:empty` there. This was a genuine bug the user caught by testing the live Storybook story, not a hypothetical.

A second, related sub-scope was added after this fix: icon-only buttons are now an exact square per size (24×24 sm, 32×32 md, 44×44 lg), via a parameterized `bds-button-size` mixin using CSS `calc()` (see Sub-scope section below).

**Original decision (historical, partially superseded):** ~~keep the CSS-only `:empty` approach for all three wrappers~~ — this held for plain-HTML rendering but not for Lit-rendered content, which is `bds-button`'s actual production usage pattern (Storybook, `boreal-react`/`boreal-vue` wrappers). No component in this codebase uses conditional JSX omission driven by detected slot content (the closest existing pattern, `bds-card`'s `hasHeader`/`hasFooter`, toggles CSS modifier classes on an always-rendered wrapper — the same category of solution as `:empty`, just JS-driven). The JS-driven modifier-class fix for the text wrapper follows that same established pattern, so it is not a net-new architectural pattern for this codebase.

## Background

**Corrected finding (superseding an earlier, wrong assumption in this ticket's first draft):** `bds-button.scss` has `&:empty { display: none; }` rules on `.bds-button__content-icon`, `.bds-button__content-text`, and `.bds-button__content-badge` — each wrapping a `<slot>` in `bds-button.tsx`'s JSX. We initially assumed this could never work, reasoning from Shadow DOM slot semantics (where a `<slot>` element is always a persistent child regardless of projected content). That assumption was wrong for this component: `bds-button` has no `shadow: true` in its `@Component()` decorator, so it runs in Stencil's non-shadow "scoped" rendering mode.

We verified empirically (via `newSpecPage` + `page.waitForChanges()`, checking real childNode structure across four content combinations — empty, icon-only, text-only, all three) that Stencil's non-shadow slot polyfill leaves behind exactly one **zero-length text node** as an anchor marker in place of each `<slot>`, never a `<slot>` element, comment, or whitespace-containing text node. Per the CSS Selectors spec, a zero-length text node doesn't count against `:empty`. So **all three `:empty` rules already work correctly** — this matches your own observation that the icon container visually collapses correctly today, and the same structural marker is present for the text and badge wrappers too, so there's no reason to expect them to behave differently.

**What's actually open, then:** the current approach *works*, but relies on an internal, undocumented detail of Stencil's slot polyfill (that it always leaves exactly one zero-length marker text node and nothing else). That isn't part of Stencil's public API contract. A future Stencil version bump could change that polyfill's internal behavior and silently break empty-state collapsing across `bds-button` (and every other component using the same pattern) with no compile error — only a visual regression that could go unnoticed without deliberate visual testing. This ticket is about deciding whether that risk is worth trading for the simplicity of pure CSS, or whether to move to an explicit, version-resilient JS/state-driven check.

This is unrelated to the separate AI-001 bug (already fixed): that was a **JS-timing** issue in a *different* piece of code — `hasSlotContent(this.el)` checked from `componentDidLoad`, which runs after the slot polyfill has already relocated content, causing false positives in a diagnostic warning. It has no bearing on whether the CSS `:empty` selector itself matches correctly, which is a separate, continuously-live DOM check unaffected by lifecycle timing.

**Scope note:** this ticket is scoped to `bds-button` only. The same `:empty` + `<slot>` pattern appears in ~20 other components (`bds-checkbox`, `bds-card`, `bds-dialog`, `bds-tag`, `bds-toast-item`, `bds-banner`, etc.) — those are explicitly **out of scope** here. If the corrected understanding above changes how we think about that pattern elsewhere, that's a separate follow-up decision, not part of this ticket.

**What actually broke `:empty` for the default slot (root cause):** Lit-html's template renderer inserts comment "part markers" at `${...}` binding positions, but leaves the *static* (literal) whitespace between those bindings as real, non-zero-length DOM text nodes. Any consumer template with multi-line formatting around a `<bds-button>`'s default-slot content (the common case in Storybook/Lit templates) therefore always has genuine non-empty whitespace text nodes assigned to the default slot — which the CSS spec does *not* exclude from `:empty` matching, unlike Stencil's own zero-length marker node. Named slots (`icon`, `badge`) are unaffected because incidental template whitespace never carries a `slot` attribute, so it's never assigned to those slots in the first place — it stays in the default slot regardless of which other slots are used.

## Sub-scope: icon-only square sizing (added after the `:empty` fix)

**Goal:** icon-only buttons should render as an exact square per size — 24×24 (`sm`), 32×32 (`md`), 44×44 (`lg`) — while all other content combinations (text-only, icon+text) keep a variable, content-driven width.

**Approach:** `bds-button-size` (in `bds-button.scss`) now takes a `$height` parameter and computes two derived values with CSS `calc()` (not Sass math — see below): `$icon-row-padding-block` (keeps the icon row's rendered height consistent with the text row) and `$icon-only-content-padding` (the horizontal padding that makes an icon-only button exactly square). A `:has(.bds-button__content-icon:not(:empty)):has(.bds-button__content-text--is-empty)` selector scopes the square override to icon-only buttons only, zeroing the button's own horizontal padding and moving the full horizontal budget onto `.bds-button__content`.

**Key discovery:** `$boreal-*` design tokens resolve to `var(--boreal-*)` CSS custom properties at runtime, not Sass compile-time literals (confirmed via `stencil.config.ts`'s `injectGlobalPaths`). Sass arithmetic on them (`+`, `-`, `math.div`) silently produces invalid CSS via string concatenation rather than a compile error — this caused two real bugs during implementation (all paddings resolving to `0`, then just `lg`'s icon-only padding resolving to `0` after a partial fix). Fixed by using CSS `calc()` throughout, with composed/summed tokens (e.g. `lg`'s height, built from `layout-l + layout-s` since no single 44px token exists) wrapped in their own nested `calc()`. Documented in `.agents/memory/sass-design-tokens-are-css-vars-not-literals.md`.

**Verification:** measured all three sizes × all three content kinds (text-only, icon-only, icon+text) in a live browser — icon-only renders as an exact square at every size (24×24, 32×32, 44×44, confirmed both standalone and inside `bds-button-group`), while text-only and icon+text keep variable width and the correct fixed height. One unrelated 1px overflow was found on an icon+badge-no-text combination (badge's own 20px height plus icon-row padding slightly exceeds `min-height`) — pre-existing, tracked separately under `EOA-15173`, out of scope here.

**Consumer impact:** `bds-pagination`'s nav-chevron buttons, `bds-dialog`'s maximize/close buttons, and `bds-drawer-header`'s close button all place their icon (`<i class="...">`) directly in the *default* slot rather than the dedicated `icon` slot — a pre-existing pattern predating this ticket (last touched in PR #146, `bds-table` v2). Because the square-sizing rule keys off the dedicated icon slot being non-empty, these buttons are unaffected by this change (same rendered size before and after) — not a regression, but a discovered inconsistency in the codebase's icon-slot usage that could be worth a future follow-up (migrating them to `slot="icon"` would both make them consistent with the rest of the API and pick up the new square sizing). `bds-search-bar`'s icon-only trigger already uses the dedicated `icon` slot but is unaffected visually because it sets its own explicit `width`/`height` override in `bds-search-bar.scss`, taking precedence over `bds-button`'s own sizing.

## Scope

**In:**
- Document the dependency on Stencil's non-shadow slot polyfill behavior in `.agents/memory/`
- Audit `bds-button`'s three content wrappers to confirm which are actually intended to collapse visually when empty (icon and badge clearly should; text does too, confirmed via the real Storybook bug this ticket found)
- Verify no regression across all variant (`default`, `outline`, `plain`) × size (`sm`, `md`, `lg`) combinations, since spacing/padding rules key off these wrapper classes
- Confirm the `bds-button__content` flex layout (`gap`, `justify-content: space-between`) behaves correctly when one or more wrappers collapse
- **Visual regression validation across all real consumers of `bds-button`**, not just its own Storybook stories — see the Dependencies section below for the full list
- Fix the real default-slot `:empty` bug found via live Storybook testing (JS-driven `hasTextContent` + modifier class, text wrapper only)
- Icon-only square sizing sub-scope (24/32/44px), added after the above fix — see dedicated section above

**Out:**
- Replacing `:empty` for the **icon** and **badge** wrappers — both are named slots, structurally safe, kept as-is
- Reconciling the disclosure chevron's conditional-JSX rendering with the slot wrappers' approach — no inconsistency requiring a fix; the chevron is prop-driven (`disclosure`), not slot-content-driven, consistent with how every other conditional-JSX-omission case in this codebase works
- Any other component using the same `:empty` + `<slot>` pattern (bds-checkbox, bds-card, bds-dialog, bds-tag, bds-toast-item, bds-banner, etc.) — explicitly deferred, not part of this ticket
- Changes to the AI-001 accessibility diagnostics work (separate, already-merged ticket)
- Any new public `@Prop()` additions (e.g. a `text` prop) — deferred per AI-001's own open questions
- Migrating `bds-pagination`/`bds-dialog`/`bds-drawer-header`'s default-slot icon usage to the dedicated `icon` slot — discovered inconsistency, not a regression, logged as a future follow-up candidate rather than fixed here
- The 1px icon+badge-no-text overflow (pre-existing, tracked under `EOA-15173`)

## Acceptance Criteria

- [x] `:empty` kept for icon/badge wrappers (named slots, safe); replaced with JS-driven `hasTextContent` state for the text wrapper (default slot, unsafe under real Lit rendering) — verified via unit tests (93/93 passing) and live browser measurement across all three content combinations
- [x] Icon-only square sizing verified correct for all three sizes (24×24/32×32/44×44) via live browser measurement, including inside `bds-button-group`; text-only and icon+text confirmed to keep variable width and correct fixed height
- [x] No visual regression across variant × size combinations for `bds-button` itself
- [x] **Visual validation performed against internal consumers of `bds-button`** — `bds-button-group` (square icon-only confirmed), `bds-pagination`/`bds-dialog`/`bds-drawer-header` (confirmed unaffected — pre-existing default-slot icon pattern, not the dedicated icon slot), `bds-search-bar` (confirmed unaffected — own explicit width/height override takes precedence), `bds-table` (icon+text "Refresh" button confirmed safe)
- [x] `.agents/memory/stencil-non-shadow-slot-relocation-timing.md` extended with the `:empty`-specific structural finding; new `.agents/memory/sass-design-tokens-are-css-vars-not-literals.md` added for the `calc()`/`var()` discovery from the square-sizing sub-scope

## Dependencies

**Components that internally render `<bds-button>`** (need visual spot-check, higher risk — actual composition dependents):
- `bds-button-group` (`packages/boreal-web-components/src/components/actions/bds-button-group/bds-button-group.tsx`)
- `bds-list-menu` (`.../actions/bds-list-menu/bds-list-menu/bds-list-menu.tsx`)
- `bds-pagination` (`.../data-visualization/bds-pagination/bds-pagination.tsx`)
- `bds-table` (`.../data-visualization/bds-table/bds-table/bds-table.tsx`)
- `bds-search-bar` (`.../forms/bds-search-bar/bds-search-bar.tsx`)
- `bds-select` (`.../forms/bds-select/bds-select.tsx`)
- `bds-dialog` (`.../overlays/bds-dialog/bds-dialog.tsx`)
- `bds-drawer` + `bds-drawer-header` (`.../overlays/bds-drawer/bds-drawer/bds-drawer.tsx`, `.../bds-drawer-header/bds-drawer-header.tsx`)
- `bds-popover` (`.../overlays/bds-popover/bds-popover.tsx`)

**Storybook/MDX files using `<bds-button>` in composed examples** (lower risk, spot-check a sample rather than all exhaustively):
`bds-button-group`, `bds-list-menu`, `bds-toggle`, `bds-card`, `bds-table`, `bds-banner`, `bds-toast`, `bds-checkbox-button`, `bds-checkbox-card`, `bds-checkbox`, `bds-flag-selector`, `bds-radio-button`, `bds-radio-card`, `bds-radio`, `bds-search-bar`, `bds-select`, `bds-slider`, `bds-tag-field`, `bds-text-field`, `bds-stepper`, `bds-dialog`, `bds-drawer`, `bds-popover`, `bds-tooltip`, plus `getting-started/framework-integration.mdx`.

- Builds on the `hasSlotContent` utility in `packages/boreal-web-components/src/utils/dom/elements.ts` (if the JS-driven approach is chosen)
- Related to `.agents/memory/stencil-non-shadow-slot-relocation-timing.md` (written during AI-001) — this ticket's findings extend that entry with the `:empty`-specific structural details

## Open Questions

None remaining — both prior open questions were resolved: keep CSS-only `:empty` (documented), and no reconciliation needed for the disclosure chevron since it isn't part of the same problem category.

## Status

**Done.** All acceptance criteria verified: the real default-slot `:empty` bug is fixed (JS-driven, text wrapper only; icon/badge unchanged), icon-only square sizing shipped and verified across all sizes, internal consumers visually validated with no regressions found (one pre-existing, out-of-scope inconsistency logged), and both memory files updated.

**Remaining housekeeping (non-blocking):** the modified files (`bds-button.tsx`, `bds-button.scss`) are uncommitted — commit when ready. `src/index.html` playground additions from this session are dev-only scratch content and should not be committed (per project convention).
