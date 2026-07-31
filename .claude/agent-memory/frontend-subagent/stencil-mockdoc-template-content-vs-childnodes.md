---
name: stencil-mockdoc-template-content-vs-childnodes
description: How to reproduce the real-browser "template.content stays empty when children are appended via appendChild instead of innerHTML/parsing" behavior inside Stencil's mock-doc test environment
metadata:
  type: project
---

Stencil's `mock-doc` (`@stencil/core/mock-doc`, `MockTemplateElement`) faithfully reproduces the real `HTMLTemplateElement` quirk: `appendChild` (inherited from `MockHTMLElement`) always writes to the template's normal `childNodes`, never to `.content`. Only the `innerHTML` setter (`set innerHTML(html) { this.content.innerHTML = html; }`) populates `.content`.

**Why this matters:** it lets a unit test simulate the exact React/Vue "framework appends `<template>` children via DOM ops, so `.content` never populates" bug without a real browser — just build the template with `page.doc.createElement('template')` + manual `appendChild(childEl)`, and never touch `.innerHTML`. `template.content.firstElementChild` will be `null`, `template.childNodes` will have the real content. This is the fixture used to test `bds-table`'s `applyRowDetail` empty-`.content` warning path (`bds-table.expand.spec.ts`, describe block "row-detail template with empty .content").

**How to apply:** any future test needing to assert on `<template>` content-population edge cases (light-DOM row-detail/slot patterns, React/Vue interop bugs) should use this `appendChild`-without-`innerHTML` technique rather than trying to fake it with real jsdom or `template.innerHTML = ''` (which would just produce a template with `.content` correctly empty AND no childNodes — not the same bug shape).

Related: [[stencil-mockdoc-no-scope-selector]] (mock-doc quirks generally), [[stencil-table-detail-row-collapse-inner-wrapper-fix]] (same `applyRowDetail`/detail-row rendering area of `bds-table`).
