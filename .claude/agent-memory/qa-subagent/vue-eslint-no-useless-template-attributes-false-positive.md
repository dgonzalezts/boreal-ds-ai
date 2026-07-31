# `vue/no-useless-template-attributes` false-positives on a real passthrough `<template>`

`eslint-plugin-vue`'s `no-useless-template-attributes` rule assumes any bare `<template>` (no `v-if`/`v-for`/`v-slot`) is always Vue's own invisible grouping construct and therefore never becomes a real DOM node — so it flags attributes like `ref`/`slot` on it as pointless.

This is a **verified false positive** for the pattern used to work around the `.content`-population bug (see `template-content-empty-in-react-vue.md`): a directive-less `<template ref="templateRef" slot="row-detail">` genuinely IS rendered as a real DOM `<template>` element by Vue in this case (confirmed live: `ref` binds correctly, the element is discoverable in `el.children`, `slot` reaches the light DOM as expected by the consuming web component).

**Fix applied:** suppress with a scoped directive, not a code restructure:
```html
<!-- eslint-disable-next-line vue/no-useless-template-attributes -- verified: no v-if/v-for/v-slot means Vue renders this as a real <template> DOM node, so ref/slot are not useless here -->
<template ref="templateRef" slot="row-detail"></template>
```

Don't try to "fix" this by removing `ref`/`slot` or restructuring — the working code is correct; the lint rule's assumption doesn't hold for this specific web-component-interop pattern.
