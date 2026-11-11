---
name: stencil-ref-null-on-removal-defeats-undefined-guard
description: Stencil calls a vnode's ref callback with null (not undefined) when the element is removed, so `if (el !== undefined) this.refs[i] = el` stores null and later `=== undefined` guards dereference null
metadata:
  type: project
---

Stencil's `ref={el => { if (el !== undefined) this.x = el; }}` still runs on removal with `el === null`, so conditionally-rendered refs end up `null`, and downstream `=== undefined` guards miss it. Verified in `bds-slider`: switching `tooltip` focus -> never at runtime throws `TypeError: Cannot set properties of null (setting 'textContent')` from `syncTooltip` (catalog row FM-SL-43). Probe it with `newSpecPage`: set the prop, `await page.waitForChanges()`, wrap in try/catch.

**Why:** the throw surfaces in `componentDidUpdate`, so unit tests that only mount once never see it.
**How to apply:** when auditing a component that stores refs for conditionally rendered nodes, add a runtime prop-toggle row to the failure-mode catalog and check the ref guard uses `!= null` / `=== null`. Candidate for `.agents/memory/`.
