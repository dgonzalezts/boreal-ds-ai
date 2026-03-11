# Node.js — Signal Handler and Process Cleanup Patterns

## Use `spawnSync` for Cleanup Logic in SIGINT / SIGTERM Handlers

When a Node.js script needs to perform cleanup (e.g. restoring files, reverting `package.json` changes) in response to SIGINT (Ctrl+C) or SIGTERM, the handler must be fully synchronous. An `async` handler will not reliably complete because the event loop begins tearing down at the same time the signal fires — async microtasks are queued but never drained.

The correct pattern is a synchronous `cleanup()` function that calls `spawnSync` for any shell operations:

```js
import { spawnSync } from 'node:child_process';

function cleanup(filePaths, root) {
  spawnSync('git', ['checkout', 'HEAD', '--', ...filePaths], {
    cwd: root,
    stdio: 'pipe',
  });
}

function handleSignal(filePaths, root) {
  cleanup(filePaths, root);
  process.exit(1);
}

process.once('SIGINT', () => handleSignal(filePaths, root));
process.once('SIGTERM', () => handleSignal(filePaths, root));
```

Key points:

- `spawnSync` blocks until the child process exits, regardless of event loop state.
- `stdio: 'pipe'` prevents the child process (git) from receiving the same SIGINT that triggered the handler.
- `process.once()` (not `process.on()`) prevents the handler from firing more than once if multiple signals arrive in quick succession.
- SIGTERM covers VS Code's integrated terminal stop button and process managers — always register both SIGINT and SIGTERM handlers sharing the same implementation.

Applied in `scripts-boreal/bin/publish.js` (EOA-10230).

### Why Not `execSync` or `async/await`

- `execSync` spawns a shell, which may also forward the SIGINT signal to its child — this can cause git to abort before completing the restore.
- `async` signal handlers are unreachable from the microtask queue once Node begins teardown. `fs.writeFileSync` works in that context but `await`-based calls do not.

## `pnpm install` Recovery After a Force-Killed Pipeline

`git checkout HEAD -- <paths>` restores `package.json` file content but does not repair `node_modules` symlinks. If the `scripts-boreal/bin/publish.js` pipeline is killed with SIGKILL (`kill -9`) — which is not catchable by any userland handler — the workspace may be left with `node_modules/@telesign/boreal-web-components` in `boreal-react` still pointing at a tgz store entry rather than the workspace symlink.

Symptom: `dist/css` is missing from the resolved package path, causing import errors.

Recovery: run `pnpm install` from the workspace root. This relinks all workspace package symlinks and clears the stale tgz reference. No other manual step is needed.

```bash
pnpm install
```

This is the only recovery step required after a force-kill. It is documented in `scripts-boreal/README.md` as well.
