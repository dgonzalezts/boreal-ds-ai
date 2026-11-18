# Fix: npx-based MCP servers fail to connect (Playwright, Context7)

## Symptom

Any MCP server launched through `npx` fails at startup or on reconnect:

```
Failed to reconnect to playwright: -32000
context7: ✘ Failed to connect — CONNECTION_CLOSED: Connection closed
playwright: ✘ Failed to connect — CONNECTION_CLOSED: Connection closed
```

Running the server by hand shows the real error:

```
npm error code ENOTEMPTY
npm error syscall rename
npm error path /Users/<user>/.npm/_npx/<hash>/node_modules/<pkg>
npm error ENOTEMPTY: directory not empty, rename '.../<pkg>' -> '.../.<pkg>-XXXX'
```

## Root Cause

`npx` installs each package into `~/.npm/_npx/<hash>/`. If that folder is left half-written, every later start fails the same way until it is deleted. The server process exits and Claude Code reports `-32000` or `CONNECTION_CLOSED`.

Common triggers:

- **Concurrent starts**: Claude Code launches all stdio MCP servers at session start. Two sessions, or a session plus an IDE or CLI health check, can install into the same `_npx/<hash>` folder at once and race on renames.
- **Interrupted installs**: closing the session or terminal, or hitting the startup timeout during a download, leaves a partial `node_modules`.
- **`@latest` tags**: each new release invalidates the cache and forces a reinstall, which makes the first two cases more likely. Packages without a tag (Context7) are less exposed.

## Fix

**Step 1 — Diagnose (optional):** run the failing server by hand and look for `ENOTEMPTY`:

```bash
npx -y @upstash/context7-mcp </dev/null
npx -y @playwright/mcp@latest --version
```

**Step 2 — Clear the npx cache:**

```bash
rm -rf ~/.npm/_npx
```

To remove only the broken entries, delete the `<hash>` folders named in the error paths.

**Step 3 — Re-fetch the packages:**

```bash
npx -y @upstash/context7-mcp </dev/null
npx -y @playwright/mcp@latest --version
```

Expected output:

```
Context7 Documentation MCP Server vX.X.X running on stdio
Version X.X.X
```

**Step 4 — Verify and reconnect:**

```bash
claude mcp list
```

Both servers should show `✔ Connected`. Then run `/mcp` in Claude Code to reconnect, or restart the session. Connections already marked failed in a running session do not recover on their own.

## Prevention

- Pin versions instead of `@latest` (e.g. `@playwright/mcp@0.0.85`) so the cache stays valid between releases.
- Install globally and point the config at the binary, so nothing is installed at startup: `npm i -g @upstash/context7-mcp @playwright/mcp`.

## Notes

- MCP config lives in `~/.claude.json` under `mcpServers`.
- Context7 needs `CONTEXT7_API_KEY` in the environment; a missing key is a separate failure from this one.
- Playwright browser binaries are cached separately at `~/Library/Caches/ms-playwright/` and are unaffected by this fix.
