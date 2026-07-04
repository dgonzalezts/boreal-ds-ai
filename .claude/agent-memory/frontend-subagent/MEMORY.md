# Frontend Subagent — Per-Scope Memory Index

- [No shadow: false in decorator](feedback_no_shadow_false.md) — Omit `shadow` from `@Component` entirely; Stencil defaults to light DOM without it
- [No @default tags in JSDoc](feedback_no_jsdoc_default.md) — TypeScript initializers are the authoritative default; `@default` tags duplicate them and can drift
- [Render helper methods](feedback_render_helpers.md) — Extract `renderRegion()` private methods when `render()` has multiple structural sections
- [Utils in a dedicated folder](feedback_utils_folder.md) — Place component-local utilities in a `utils/` subfolder, not inline in the `.tsx` file
- [slotchange: two patterns](feedback_slotchange_listener.md) — Use `<slot onSlotchange>` for slotted children; use imperative `addEventListener` for unslotted direct DOM children read via `querySelectorAll`
- [No @summary in JSDoc](feedback_no_jsdoc_summary_tag.md) — Stencil CEM compiler silently discards @summary; leading prose before any @ tag is the sole source of the "description" field in custom-elements.json
- [Prop-or-slot pattern](feedback_prop_or_slot_pattern.md) — avoid slot-fb DOM noise: use {prop.length > 0 ? <el> : <slot />} not slot fallback children
- [PREFIX constant](feedback_prefix_constant.md) — declare `const PREFIX = 'bds-tag' as const` at the top of every component; use in all class template literals
- [classMap getter](feedback_classmap_getter.md) — use `private get classMap(): StyleModifiers` for conditional classes; never inline ternaries in JSX class bindings
- [SCSS BEM nesting](feedback_scss_bem_nesting.md) — nest all `&__element` rules inside the block selector; never write flat `.bds-component__element` selectors
- [Component code organization](component-code-organization-bds-table.md) — `@Element()` before `@State()`; lifecycle section 9 follows execution order (`componentDidRender` before `componentDidLoad`); section comments omitted by team preference; `@State()` JSDoc is optional
- [Collapsed-trigger focus/scroll bug pattern](feedback_scroll_into_view_collapsed_focusable.md) — manage tabindex on every internal focusable, not just the visible trigger, or reverse Tab can bypass the expand handler and corrupt scrollLeft on overflow:hidden containers
- [bds-search-bar scroll-clip fix (EOA-15204)](stencil-search-bar-scroll-clip-bug.md) — root cause + fix location; also notes `--testPathPattern` doesn't scope correctly in this repo's test runner
