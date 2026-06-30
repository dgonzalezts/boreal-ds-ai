# Fix: Playwright MCP "Failed to reconnect" (-32000)

## Symptom

Running `/mcp` in Claude Code returns:

```
Failed to reconnect to playwright: -32000
```

## Root Cause

The `-32000` JSON-RPC error means the Playwright MCP server process crashed or is in a bad state. When the config uses `@playwright/mcp@latest`, `npx` caches the resolved package — a stale or corrupt cache entry causes the server to fail on reconnect.

## Fix

**Step 1 — Clear the npx cache:**

```bash
rm -rf ~/.npm/_npx
```

**Step 2 — Re-fetch the Playwright MCP package:**

```bash
npx @playwright/mcp@latest --version
```

This forces npx to download a fresh copy. You should see output like:

```
npm warn exec The following package was not found and will be installed: @playwright/mcp@x.x.x
Version x.x.x
```

**Step 3 — Reconnect in Claude Code:**

Run `/mcp` — the server should reconnect successfully.

## Notes

- The MCP config lives in `~/.claude.json` under `mcpServers.playwright`.
- Pinning to a specific version (e.g. `@playwright/mcp@0.0.77`) avoids surprise stale resolutions from the `@latest` dist-tag.
- Playwright browser binaries are cached separately at `~/Library/Caches/ms-playwright/` and are unaffected by this fix.
