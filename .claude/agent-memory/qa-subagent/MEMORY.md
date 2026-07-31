# QA Subagent — Per-Scope Memory Index

- [dev:pack:react / dev:pack:vue pipeline](dev-pack-pipeline-commands.md) — never use a plain `vite` server against a workspace-built `boreal-web-components`; use the dedicated pack pipeline, know it installs a tarball snapshot (re-run to pick up component changes), exact commands and cleanup
- [`<template>` content empty in React/Vue](template-content-empty-in-react-vue.md) — JSX/Vue-template children never populate `.content`; the working ref+`.innerHTML` fix, confirmed in both frameworks; also promoted to team memory
- [React/Vue Bds* event-detail typing](react-vue-event-detail-typing.md) — never hand-roll event-detail types; derive from the component's own prop signature (React) or the real generic `RowData` shape (Vue); `vue-tsc` CLI can be clean while the IDE still flags a real error
- [`vue/no-useless-template-attributes` false positive](vue-eslint-no-useless-template-attributes-false-positive.md) — verified false positive on a directive-less passthrough `<template ref slot>`; suppress with a scoped eslint-disable, don't restructure working code
- [Playwright + bds-button conventions](playwright-and-bds-button-conventions.md) — shared-browser tab isolation, `bdsClick` vs `click`, `index.html`/testapp playground scenario-accumulation convention
