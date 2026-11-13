# `stencilVitestPlugin` throws on every component declared with `extends Mixin(...)`

Verified on Stencil 4.45.2, `@stencil/vitest` 1.16.1, Vitest 5.1.0 (EOA-20193 spike, 2026-11-13). Full evidence and working configurations: `ai-work/research/2026-11-13-EOA-20193-stencil-vitest-migration-spike.md`.

## The Problem

The official `stencilVitestPlugin` fails with `TypeError: Cannot read properties of undefined (reading 'text')` on every component whose class is `extends Mixin(...)`: 18 of 81 components (popover, dialog, tooltip, text-field, checkbox, date-picker and others). The plugin's README says Stencil 5 fixes cross-file inheritance; that claim was NOT tested.

## The Fix (fallback that worked)

A local Vite transform plugin calling `transpileSync` from `@stencil/core/compiler`:

- Try `module: 'esm'` first; on error retry with `module: 'cjs'` (it only warns) and rewrite the CommonJS output to ESM with a small regex function.
- Pass `jsx: 2`, otherwise the transpile returns the source unchanged.
- Cover `.ts` as well as `.tsx`: the `src/mixins/*.mixin.ts` files carry decorators.

The full plugin source (about 55 lines) is in the spike document.

## How to verify

Run any spec of a Mixin component (for example `bds-checkbox`) under Vitest with the official plugin alone: it throws. With the fallback it renders.

Related: [[stencil-vitest-migration-newspecpage-and-dist-route]], [[stencil-vitest-replaces-global-htmlelement-and-event]], [[vitest-vi-fn-not-constructable]].
