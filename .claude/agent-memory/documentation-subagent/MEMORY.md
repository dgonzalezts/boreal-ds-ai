# Documentation Subagent — Memory Index

## Topic Files

- [verification_storybook_dev_docs_port_conflict.md](verification_storybook_dev_docs_port_conflict.md) — `pnpm dev:docs` hangs on an interactive port-6006-conflict prompt if a prior instance is still running; check `lsof -i :6006` first and reuse it, verify via `iframe.html?id=...` and the `#storybook-preview-iframe`'s `contentDocument` through Playwright MCP.
