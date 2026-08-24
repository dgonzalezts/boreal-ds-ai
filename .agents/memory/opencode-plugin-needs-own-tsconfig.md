# `.opencode/` Needs Its Own `tsconfig.json` for `@types/node` to Resolve

## The Problem

`.opencode/plugins/check-node-version.ts` imports `node:child_process` and needs `@types/node`. Installing `@types/node` into `.opencode/node_modules/` (via `.opencode/package.json` + `npm install`, the pattern OpenCode's own docs show for local plugin dependencies) does **not** fix the editor's `Cannot find name 'node:child_process'` diagnostic, no matter how many times it's reinstalled.

Root cause: TypeScript's automatic `@types` discovery (when no `typeRoots` is explicitly configured) is computed from the tsconfig file's own directory — or, with no tsconfig at all, from wherever `tsc` is invoked. There was no `tsconfig.json` inside `.opencode/`, so the nearest tsconfig an editor's TS server would find, walking up from `.opencode/plugins/check-node-version.ts`, was the repo root's `tsconfig.json`. Automatic typeRoots resolution is anchored to *that* file's directory, not to `.opencode/`, so `.opencode/node_modules/@types/node` was never in the search path regardless of whether the package was actually installed there.

Confirmed via `tsc --noEmit` run directly (bypassing the editor, to rule out a stale-cache explanation): the error reproduces with the CLI too, proving it's a real config-resolution issue, not an IDE cache artifact.

## The Fix

Add a dedicated `.opencode/tsconfig.json`:

```json
{
  "compilerOptions": {
    "target": "es2022",
    "module": "esnext",
    "moduleResolution": "bundler",
    "types": ["node"],
    "strict": true,
    "skipLibCheck": true,
    "noEmit": true
  },
  "include": ["**/*.ts"],
  "exclude": ["node_modules"]
}
```

This anchors `.opencode/` as its own TypeScript project root, so `.opencode/node_modules/@types/node` is correctly on the typeRoots search path. Verified with `cd .opencode && npx tsc --noEmit --project tsconfig.json` — zero errors.

## How to Verify a Fix Like This Actually Works

Don't trust the editor's live diagnostic alone — it can be stale from a prior state and give a false sense of "still broken" or "now fixed." Confirm with the compiler directly: `npx tsc --noEmit --project <path>/tsconfig.json` from outside the editor. If that passes, any remaining editor complaint is a TS-server-restart issue, not a real one.

## Source

AI-005 (OpenCode facade plan), post-completion follow-up. Discovered when the diagnostic recurred after a `node_modules` cleanup and reinstall didn't resolve it.
