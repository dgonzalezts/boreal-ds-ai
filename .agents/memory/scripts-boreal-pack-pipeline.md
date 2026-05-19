# scripts-boreal — Pack and Validate Pipeline Architecture

## Build Guarantee via Turborepo Task Graph

`scripts-boreal/bin/publish.js` packs already-built artifacts. It performs no build step itself. The build guarantee is provided entirely by Turborepo through a `dependsOn` entry in `turbo.json`:

```json
"validate:pack:react": {
  "dependsOn": ["@telesign/boreal-web-components#build"]
}
```

This tells Turbo to run the `build` task in `@telesign/boreal-web-components` before executing `validate:pack:react` in `scripts-boreal`. The same `dependsOn` is declared for `validate:pack:vue` and `validate:pack:angular`. Turbo's cache means only one actual build runs even when `validate:all` invokes all three framework validations in sequence.

The root `package.json` script `dev:pack:react` handles the development variant differently — it explicitly invokes `turbo run build --filter=...@telesign/boreal-web-components` before delegating to `scripts-boreal`. Both approaches are correct; the Turbo `dependsOn` path is preferred for CI and `release:all` because it uses the task graph cache.

## Per-Framework Script Suffix Convention

All pack and validate scripts carry explicit framework suffixes (`:react`, `:vue`, `:angular`) at every layer of the stack. This makes the public API self-documenting and prevents ambiguity as additional framework wrappers are added.

Layer mapping after the EOA-10230 refactor:

| Layer | Script names |
|---|---|
| `turbo.json` | `validate:pack:react`, `validate:pack:vue`, `validate:pack:angular` |
| `scripts-boreal/package.json` | `validate:pack:react`, `dev:pack:react`, `validate:pack:vue`, `dev:pack:vue` (angular already carried suffixes) |
| Root `package.json` | `dev:pack:react`, `dev:pack:vue`, `validate:pack:react`, `validate:pack:vue`, `validate:pack:angular` |

## Aggregator Scripts

`validate:all` in root `package.json` sequences all per-framework validations. It currently runs `:react` and `:vue` — Angular is excluded until `examples/app-angular` is implemented. Extend it by appending `&& pnpm run validate:pack:angular` once that app exists.

`release:all` was updated to use `validate:all` instead of the former `validate:pack`. The full sequence is:

```
release:styles → release:wc → validate:all → release:react → release:vue
```

## Files Owning This Architecture

| File | Role |
|---|---|
| `turbo.json` | Declares task graph with `dependsOn` build guarantees |
| `scripts-boreal/package.json` | Per-framework pack and validate entry points for the packaging script |
| Root `package.json` | Public-facing script API consumed by developers and CI |
| `scripts-boreal/bin/publish.js` | Packaging implementation — packs artifacts, does not build |

Source: EOA-10230 deployment and publishing implementation session (2026-03-10).
