---
name: feedback_jsdoc_sync_on_change
description: Re-audit JSDoc whenever a change touches the public API surface — @slot tags in the class JSDoc are the highest-risk drift point because the CEM plugin cannot infer them from render()
metadata:
  type: feedback
---

After any change that adds, removes, or renames a prop, event, method, or slot, re-audit the JSDoc in the same task — never leave it for a later pass.

**Why:** JSDoc drift ships straight into the published API docs. Prop/event/method JSDoc sits directly on the member, so deleting the member deletes its doc — low risk. `@slot` tags are different: they live in the class-level JSDoc block, far from the `render()` code that changes, and they are the one tag the Stencil CEM plugin cannot infer or validate from the AST. A stale `@slot` therefore flows silently into `custom-elements.json` as a phantom slot. Real incident (EOA-14935, 2026-07-14): `bds-table`'s `search-bar` slot was replaced by the built-in `searchable` prop, but the class JSDoc kept `@slot search-bar` for several commits until it was caught manually.

**How to apply:** Before finishing any edit to a component `.tsx`, diff the class-level JSDoc against reality: every `@slot` tag must have a matching `<slot>` / `<slot name="...">` in `render()` (or its render helpers), and every rendered slot must have a tag. Also re-read the leading prose description — it often names props or behaviors that the change just altered. The `code-reviewer` skill's `class-jsdoc-stale-slot` check catches the named-slot case mechanically; the prose description still needs a human read.

**See also:** [[feedback_no_jsdoc_summary_tag]], [[feedback_no_jsdoc_default]] — same family: JSDoc that duplicates or contradicts the authoritative source of truth.
