# Storybook + Vite Quirks

## Vite glob pattern limitation in package exports

Vite does not support glob patterns in `package.json` exports (e.g. `"./css/*": "./dist/css/*"`). This means `@telesign/boreal-web-components/css/*` cannot be resolved automatically.

**Workaround:** Two aliases are registered in `viteFinal`:
1. A variable `wcCssDir` is resolved to `packages/boreal-styleguidelines/dist/css`
2. A regex alias maps `@telesign/boreal-web-components/css/(.+)` → `${wcCssDir}/$1`

File: `apps/boreal-docs/.storybook/main.ts`

## esm-es5 dynamic import warnings

Storybook's Vite setup generates noisy warnings about dynamic imports of ESM modules (`esm-es5`). These are suppressed in two places:

1. **Development** — via a custom `createLogger` that filters `logger.warn` when the message includes both `'esm-es5'` and `'dynamic import'`
2. **Production build** — via `rollupOptions.onwarn`, filtering when `warning.plugin === 'vite:import-analysis'` and `warning.id` includes `'esm-es5'`

These warnings are harmless and suppressing them reduces noise in both dev and CI build output.

File: `apps/boreal-docs/.storybook/main.ts`
