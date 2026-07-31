# Documentation Subagent — Memory Index

## Topic Files

- [verification_storybook_dev_docs_port_conflict.md](verification_storybook_dev_docs_port_conflict.md) — `pnpm dev:docs` hangs on an interactive port-6006-conflict prompt if a prior instance is still running; check `lsof -i :6006` first and reuse it, verify via `iframe.html?id=...` and the `#storybook-preview-iframe`'s `contentDocument` through Playwright MCP.
- [bds-table-row-detail-timing-bugs.md](bds-table-row-detail-timing-bugs.md) — `bds-table`'s row-detail toggle can fail to render on first paint (slot-relocation race) and `bdsExpand` fires before its detail DOM exists (async render-commit gap); both are real implementation bugs, not docs issues — story workarounds documented, real fix belongs to frontend-subagent.
- [argtypes-name-collision-across-subcomponents.md](argtypes-name-collision-across-subcomponents.md) — `<ArgTypes include={[...]}>` filters by resolved `name` across the entire shared `meta.argTypes` object, not scoped per sub-component; two sub-components with a same-named prop (`bds-table-column`/`bds-table-column-group`'s `label`/`info`) need a CSF3 per-story `argTypes` override, not a `name:` override, to disambiguate. Moved here from the incorrectly-placed `packages/boreal-web-components/.claude/agent-memory/documentation-subagent/` on 2026-07-31.
