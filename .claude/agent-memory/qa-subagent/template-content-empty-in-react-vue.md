# `<template>` authored via JSX/Vue-template children never populates `.content`

Confirmed live in both frameworks (`EOA-16000`, `bds-table` `slot="row-detail"`): `HTMLTemplateElement.content` (the hidden parser-only `DocumentFragment`) is populated by the browser **only** when its own HTML parser encounters the `<template>` tag in raw markup. React and Vue's virtual-DOM reconcilers create the element and append children via normal DOM operations (`appendChild`/`insertBefore`) — not parser semantics — so `.content` stays an empty `DocumentFragment` even though the framework visibly rendered children into the element's ordinary `childNodes`.

**Symptom:** any Boreal DS feature reading `someTemplateElement.content` (e.g. `bds-table` cloning `rowDetailTemplate.content`) renders its toggle/trigger correctly (presence-only checks pass) but the actual detail content is **silently empty** — no error, no console output, nothing to indicate why.

**Verified repro (do this first before assuming a bug in the component):**
```js
document.querySelector('template[slot="row-detail"]').content.childNodes.length
```
`0` despite visible JSX/Vue-template children = this bug, not a real defect elsewhere.

**The working fix, confirmed end-to-end in both frameworks:** populate `.content` imperatively via a ref/mounted-hook, setting `.innerHTML` — `.innerHTML` assignment DOES go through HTML-parser semantics and correctly populates `.content`, unlike appending JSX/Vue-template children.

- React: `useRef<HTMLTemplateElement>` + `useEffect(() => { ref.current.innerHTML = '...' }, [])`
- Vue: `ref<HTMLTemplateElement | null>(null)` + `onMounted(() => { ref.value.innerHTML = '...' })`

Raw web-component/vanilla-HTML usage (writing `<template>` directly in static markup) is entirely unaffected — this is specific to authoring through a framework's virtual-DOM compiler.

**Also confirmed:** a bare `<template>` with no `v-if`/`v-for`/`v-slot` in a Vue SFC does NOT get "unwrapped" by Vue's compiler (an initial worry that turned out to be unfounded) — Vue does render it as a genuine DOM `<template>` node, `ref` binds correctly, and `hasRowDetail`-style presence checks on `el.children` find it fine. Only the `.content` populate step is broken, not the element's existence.

`bds-table` now has a paired one-time dev-mode console warning (`applyRowDetail` detects `template.content.firstElementChild === null`) — if you don't see it despite empty content, the template may not exist at all yet (check presence separately) or the warning may have already fired once this session (it's a one-time guard, not per-attempt).

This is promoted at team level too: see `.agents/memory/template-element-content-empty-in-react-vue.md`. Any future Boreal DS feature reading `.content` will hit the exact same trap unless designed/documented around it up front.
