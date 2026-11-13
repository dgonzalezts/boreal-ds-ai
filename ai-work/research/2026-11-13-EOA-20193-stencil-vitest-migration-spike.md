---
ticket: EOA-20193
component: boreal-web-components (test infrastructure)
status: concluded
date: 2026-11-13
---

# Spike: moving the web-components specs from Stencil's Jest runner to `@stencil/vitest`

Outcome: the migration is deferred to a follow-up (decision of 2026-11-13). This note keeps the evidence and the working configurations so the follow-up starts from facts. The original scratch files were lost when the session scratchpad was cleaned; everything below is reconstructed from the two spike reports (2026-11-12 and 2026-11-13) and was run on Stencil 4.45.2, Vitest 5.1.0, `@stencil/vitest` 1.16.1, Node 22.

## Why it exists

- Stencil's built-in runner (`stencil test --spec`) is deprecated since 4.43 and removed in Stencil 5. Every test run prints the deprecation notice.
- Jest 30 is not supported on Stencil 4, so `jest`, `jest-cli`, `@types/jest` and `puppeteer` cannot be upgraded in place. 19 of the 75 findings of a full `pnpm audit` (dev dependencies included) go through those packages.
- Stencil `5.0.0-rc.0` and `5.0.0-rc.1` were published on 2026-11-12; there is no official release date. `5.0.0-rc.1` still ships `newSpecPage` in `dist/testing/index.mjs` (the package contents were checked, not executed).

## Scale

377 spec files; 331 use `newSpecPage` (2,752 call sites); options in use are only `components` and `html` (plus `template` in 2 files). Never used: `supportsShadowDom`, `autoApplyChanges`, `hydrateClientSide`, `mockFetch`, `resetPlatform`. 146 files use `jest.fn`, 86 `jest.spyOn`; 14 files patch `HTMLElement.prototype`; 25 are `.spec.tsx`.

## What the official documentation says (checked on the pages)

`https://stenciljs.com/docs/testing-vitest-migration` and `.../testing-vitest-configuration` document only the dist route: a `vitest-setup.ts` that imports the built output (`await import('./dist/test-components/test-components.esm.js')`, "adjust according to your build output of choice"), `render()` instead of `newSpecPage`, the `stencil-test` CLI, test projects, and the DOM environments (`mock-doc` default, `jsdom`, `happy-dom`). They do not mention `stencilVitestPlugin`, coverage, aliases, mixins or inheritance, `newSpecPage` options, mocks, or a codemod. The plugin and its limits appear only in the package README.

## Three routes evaluated

| Route | Spec edits | Coverage | Result on the samples |
| --- | --- | --- | --- |
| A. Keep `newSpecPage`, run under Vitest 5 with a local transform plugin | none (plus one helper edit) | v8, mapped to `src` | 352 of 377 files green, 4,788 of 4,930 tests (97.1%); 25 files (142 tests) red |
| B1. `render()` with the plugin in source mode | convert every spec | v8, mapped to `src` | 5 sample files 125 of 125; regex codemod on 287 files: 207 green (72%), 2,412 of 3,047 tests |
| B2. `render()` on the documented dist route | convert every spec | 0% on component source | 5 sample files 125 of 125 (only with a dedicated test build config); regex codemod on the whole suite: 224 of 377 files green (59%), 3,080 of 3,966 tests that ran |

Jest on the same tree: 378 suites, 4,948 tests, 52.5 s wall. Vitest A: 54.4 s wall, about 50% more CPU time. Dist route: about 23 to 27 s for the suite plus a 5 s build.

Coverage of the three sample source files (`bds-badge`, `bds-checkbox`, `bds-pagination`), statements / branches / functions / lines: Jest (Istanbul) 86.93 / 88.63 / 81.81 / 88.34; B1 (v8) 89.66 / 92.5 / 85.18 / 90.58; A (v8) 88.84 / 92.5 / 84.14 / 89.68. One cell is lower: `bds-checkbox.tsx` branches 90.24 against 91.17. The checkbox goes through the Mixin fallback, which returns no source map, so its line mapping is unconfirmed. Providers count differently; `@vitest/coverage-istanbul` would give strict parity with the 80% thresholds.

Mutation testing: `@stryker-mutator/vitest-runner` 10.1.1 works with the source-mode config (a run on `bds-badge`: 14 of 15 mutants killed, 93.33%). Stryker is not installed in the repository; its skill and templates target Jest.

## Findings that decide the follow-up

1. The official `stencilVitestPlugin` throws `TypeError: Cannot read properties of undefined (reading 'text')` on every component declared with `extends Mixin(...)` on Stencil 4.45.2: 18 of 81 components (popover, dialog, tooltip, text-field, checkbox, date-picker...). The README says Stencil 5 fixes cross-file inheritance; this was not tested on Stencil 5.
2. `newSpecPage` needs a transform: without it `@Prop` throws "Prop is not a function". The official plugin emits metadata `newSpecPage` cannot read (`COMPILER_META` undefined).
3. `@stencil/vitest` replaces the global `HTMLElement` with a subclass of mock-doc's `MockHTMLElement` and restores Node's global `Event`; specs that patch `HTMLElement.prototype` (`focus`, `showModal`, `attachInternals`) or build events with global constructors break. Resetting `HTMLElement` to the base class fixed about 27 of 52 failing files.
4. Vitest 4 and 5 `vi.fn(() => x)` cannot be called with `new`; `jest.fn(() => ({ observe }))` used as a `ResizeObserver` constructor failed in 59 files until a constructable wrapper was added. `src/utils/testing/mocks/observers.ts` needs `mockImplementation(function () { return methods; })`.
5. Dist route only: `extras.experimentalSlotFixes: true` empties the component DOM under mock-doc (Jest's spec platform builds with it off), and `minifyJs: true` breaks `render().instance` because `$lazyInstance$` is renamed. Built as the guide says, the sample passes 27 of 125; with those two settings off it passes 125 of 125. `sourceMap`, the sass `globalStyle` and `buildEs5` make no difference.
6. `render().root` is the first element of the fixture, not the first registered component; `render('')` throws "Failed to render component" (17 files use `html: ''`).
7. DOM environments: mock-doc passes the samples; jsdom fails in the component constructor (`$instanceValues$` of undefined) and hangs; happy-dom gives 8 failures from the Node `Event` restore. Recommendation: mock-doc.
8. `stencil-test --spec` is rejected by Vitest (`CACError: Unknown option --spec`); the working form is `stencil-test --project spec --stencil-config <file>`. The CLI always runs `stencil build --dev` (or `--prod`) first.
9. The A-route residual failures (25 files): date-picker 5 files (about 90 tests, "The tag name provided (undefined) is not a valid name"), handlers not firing (about 45 tests, probably the `Event` restore), `bds-table` reorder and resize 12, others unclassified.

## Working configuration, path A (existing specs unchanged)

`packages/boreal-web-components/vitest.config.mts` (the `.mts` extension avoids Vite's "ESM syntax in CJS" warning because the package has no `"type": "module"`):

```ts
import { defineVitestConfig } from '@stencil/vitest/config';
import { resolve } from 'node:path';
import { stencilSpecCompatPlugin } from './vitest/stencil-spec-compat-plugin.mts';

export default defineVitestConfig({
  stencilConfig: './stencil.config.ts',
  resolve: {
    alias: {
      '@utils/test': resolve(import.meta.dirname, 'src/utils/testing'),
      '@': resolve(import.meta.dirname, 'src'),
    },
  },
  test: {
    globals: true,
    projects: [
      {
        extends: true,
        plugins: [stencilSpecCompatPlugin()],
        test: {
          name: 'spec',
          environment: 'stencil',
          include: ['src/**/*.spec.{ts,tsx}'],
          exclude: ['**/node_modules/**'],
          setupFiles: ['./vitest/jest-compat-setup.mts'],
        },
      },
    ],
  },
});
```

`vitest/stencil-spec-compat-plugin.mts` (about 55 lines; falls back to a CommonJS compile for the Mixin components and rewrites it to ESM):

```ts
import { transpileSync } from '@stencil/core/compiler';
import type { Plugin } from 'vite';

const STENCIL_DECORATORS = /@(Component|Prop|State|Event|Method|Watch|Listen)\b/;

const baseOptions = {
  componentExport: null,
  componentMetadata: 'compilerstatic',
  coreImportPath: '@stencil/core/internal/testing',
  proxy: null,
  style: null,
  styleImportData: 'queryparams',
  target: 'es2017',
  transformAliasedImportPaths: false,
  jsx: 2,
} as const;

function commonJsToEsm(code: string): string {
  const exportedNames = new Set<string>();
  const localExports = new Set<string>();
  const body = code
    .replace(/^"use strict";\s*/, '')
    .replace(/Object\.defineProperty\(exports, "__esModule", \{ value: true \}\);/, '')
    .replace(/^const \{([^}]+)\} = require\("([^"]+)"\);$/gm, (_match, names: string, source: string) => {
      const specifiers = names.split(',').map(name => name.trim().replace(/\s*:\s*/, ' as '));
      return `import { ${specifiers.join(', ')} } from "${source}";`;
    })
    .replace(/^const (\w+) = require\("([^"]+)"\);$/gm, 'import * as $1 from "$2";')
    .replace(/^exports\.(\w+) = void 0;$/gm, (_match, name: string) => {
      exportedNames.add(name);
      return '';
    })
    .replace(/^exports\.(\w+) = (\w+);$/gm, (match, name: string, value: string) => {
      if (name !== value) {
        return match;
      }
      localExports.add(name);
      return '';
    });
  const remaining = [...exportedNames].filter(name => !localExports.has(name));
  const exportsObject = remaining.length > 0 ? 'const exports = {};\n' : '';
  const localExportStatement = localExports.size > 0 ? `export { ${[...localExports].join(', ')} };\n` : '';
  const objectExports = remaining.map(name => `export const ${name} = exports.${name};`).join('\n');
  return `${exportsObject}${body}\n${localExportStatement}${objectExports}\n`;
}

export function stencilSpecCompatPlugin(): Plugin {
  return {
    name: 'stencil-spec-compat',
    enforce: 'pre',
    transform(code, id) {
      const file = id.split('?')[0];
      if (!/\.tsx?$/.test(file) || file.includes('/node_modules/') || !STENCIL_DECORATORS.test(code)) {
        return null;
      }
      const options = { ...baseOptions, file, currentDirectory: process.cwd() };
      const esm = transpileSync(code, { ...options, module: 'esm', sourceMap: true });
      if (!esm.diagnostics.some(d => d.level === 'error')) {
        return { code: esm.code, map: esm.map };
      }
      const cjs = transpileSync(code, { ...options, module: 'cjs', sourceMap: false });
      const errors = cjs.diagnostics.filter(d => d.level === 'error');
      if (errors.length > 0) {
        throw new Error(errors.map(d => String(d.messageText)).join('\n'));
      }
      return { code: commonJsToEsm(cjs.code), map: null };
    },
  };
}
```

Notes on that plugin: without `jsx: 2` the transpile returns the source unchanged; the transform must cover `.ts` as well as `.tsx` (the `src/mixins/*.mixin.ts` files carry decorators); `module: 'esm'` crashes on `extends Mixin(...)`, `module: 'cjs'` only warns.

`vitest/jest-compat-setup.mts`:

```ts
import '@stencil/vitest';
import { vi } from 'vitest';

const wrapper = globalThis.HTMLElement as unknown as { new (): HTMLElement };
const base = Object.getPrototypeOf(wrapper) as typeof wrapper;

Object.defineProperty(globalThis, 'HTMLElement', { configurable: true, writable: true, value: base });

const originalFn = vi.fn.bind(vi);

function asConstructable<T extends (...args: never[]) => unknown>(implementation: T): T {
  return function constructable(this: unknown, ...args: never[]) {
    return implementation.apply(this, args);
  } as unknown as T;
}

function constructableFn(implementation?: (...args: never[]) => unknown) {
  const mock = originalFn(implementation ? asConstructable(implementation) : undefined);
  const mockImplementation = mock.mockImplementation.bind(mock);
  mock.mockImplementation = (next: (...args: never[]) => unknown) => mockImplementation(asConstructable(next));
  return mock;
}

Object.assign(globalThis, { jest: Object.assign(Object.create(vi), { fn: constructableFn }) });
```

`import '@stencil/vitest'` registers the Stencil matchers (`toHaveClass`, `toEqualHtml`...). A Proxy that swaps `HTMLElement.prototype` broke 361 of 377 files; the plain reset above is the working form. Setting the global `Event` to mock-doc's `Event` made no difference.

Helper edit in `src/utils/testing/mocks/observers.ts`:

```diff
-  const mock = jest.fn().mockImplementation(() => methods);
+  const mock = jest.fn().mockImplementation(function () {
+    return methods;
+  });
```

`package.json` devDependencies: `@stencil/vitest` `1.16.1`, `vitest` `5.1.0`, `@vitest/coverage-v8` `5.1.0`. Scripts proposed, not run: `test:vitest` (`vitest run`), `test:vitest:coverage` (`vitest run --coverage`), `test:scripts` (`vitest run scripts/`). Jest still picks up any new Vitest-only spec files unless they use a separate glob and a `testPathIgnorePatterns` entry in `testing.config.ts`. Type-checking Vitest specs with `types: ["vitest/globals"]` needs `/// <reference types="vitest/globals" />` and `/// <reference types="@stencil/vitest/globals" />` in a `vitest-env.d.ts`, because the package `tsconfig.json` has a restrictive `typeRoots`; the shared helpers still use the `jest` namespace, so `@types/jest` stays until the last batch.

## Path B1 differences (source mode with `render()`)

Plugin options change to `componentExport: 'customelement'` and `componentMetadata: 'runtimestatic'`; the CJS-to-ESM rewrite renames exports (`const __export_X = exports.X; export { __export_X as X };`) because the class is a declaration. Specs import the component source as a side effect (`import '../bds-badge';`) so the component registers; an import used only as a type is elided and would leave it unregistered. Spec conversion: `newSpecPage({ components, html })` becomes `render(html)`, `page.rootInstance` becomes `page.instance`, `page.doc` becomes `document`, `page.body` becomes `document.body`, `jest.` becomes `vi.`, `jest.Mock` becomes `Mock` from `vitest`, `SpecPage` becomes `Awaited<ReturnType<typeof render>>`.

Regex codemod prototype (74.9% of 331 files fully handled under the hazard heuristics; replace with a ts-morph codemod):

```js
function convert(source) {
  let out = source;
  const componentIdentifiers = new Set();
  out = out.replace(/newSpecPage\(\{\s*components:\s*\[([^\]]*)\],\s*html(?::\s*(`[^`]*`|'[^'\n]*'|"[^"\n]*"))?,?\s*\}\)/g, (_m, comps, html) => {
    comps.split(',').map(s => s.trim()).filter(Boolean).forEach(c => componentIdentifiers.add(c));
    return `render(${html || 'html'})`;
  });
  out = out.replace(/import \{ newSpecPage(?:, SpecPage)? \} from '@stencil\/core\/testing';/, "import { render } from '@stencil/vitest';");
  out = out.replace(/page\.rootInstance/g, 'page.instance');
  out = out.replace(/page\.doc\b/g, 'document');
  out = out.replace(/page\.body\b/g, 'document.body');
  out = out.replace(/\bjest\./g, 'vi.');
  return { code: out, componentIdentifiers };
}
```

Hazards the regex does not handle: `HTMLElement.prototype` patches (29 files), `.spec.tsx` (25), residual `newSpecPage` in helpers or with dynamic html (30), `html: ''` (17), fake timers or `jest.mock` (4), `setContent` (3). Group by component category in about 8 batches of about 40 files and migrate each shared test utility with its first consumer.

## Working configuration, documented dist route (path B2)

Not recommended: native v8 coverage reports 0% on component source (with or without `sourceMap: true`), and `vitest-monocart-coverage` 5.0.0 does not map the `.tsx` files, so the 80% coverage gate and the per-component Stryker runs have no working route. Recorded for completeness.

`stencil.test.config.ts`:

```ts
import { Config } from '@stencil/core';
import { config as base } from './stencil.config';

export const config: Config = {
  ...base,
  minifyJs: false,
  extras: { experimentalScopedSlotChanges: true },
  testing: undefined,
};
```

`vitest.config.mts`: `defineVitestConfig({ stencilConfig: './stencil.config.ts', test: { projects: [{ test: { name: 'spec', include: ['src/**/*.spec.{ts,tsx}'], environment: 'stencil', setupFiles: ['./vitest-setup.ts'] } }] } })`. `vitest-setup.ts`: the constructable `jest.fn` shim, then `await import('./dist/boreal-web-components/boreal-web-components.esm.js');`. Run with `stencil-test --project spec --stencil-config stencil.test.config.ts`. A fresh checkout needs `pnpm --filter @pxglobal/boreal-style-guidelines run build` first or the Sass build fails; a stale `dist/` silently gives wrong results when `vitest` runs without the CLI. The `dist-custom-elements` variant (`buildDist: true`, `import.meta.glob('./components-build/bds-*.js')` plus `defineCustomElement()`) also gives 125 of 125 on the samples but builds in 12 s and passes fewer files on the whole suite.

Mixin components work on this route (checkbox 39 of 39, text-field 104 of 104, dialog 25 of 25, popover activation 25 of 25) because Stencil compiles them itself.

## Other consumers of the Jest runner (to update in the follow-up)

- `.husky/pre-push` runs `cd packages/boreal-web-components && pnpm exec stencil test --spec`; it is the only gate on tests (no Jenkinsfile and no GitHub workflow in this repository).
- `turbo.json` `test` and `test:coverage` inputs list only `*.ts`, `*.tsx`, `*.spec.ts`; they need the Vitest config and setup files.
- `testing.config.ts` references the `jest-junit` reporter, which is installed nowhere and produces no `junit.xml`; the `test:scripts` script may already be unreliable under Stencil's CLI.
- Stryker: the skill `mutations-testing`, its templates (`stryker.component.config.mjs`, `jest.stryker.config.cjs`) and `.agents/memory/mutation-testing-*.md`.
- Files naming the runner: `.agents/agents/testing-subagent.md`, `.opencode/agent/testing-subagent.md`, `.agents/skills/testing-knowledge/SKILL.md`, `.agents/memory/stencil-scoped-test-invocation.md`, `.agents/memory/stencil-focus-spy-recursion-and-global-tracker-masking.md`, about 30 notes under `.claude/agent-memory/testing-subagent/`, `CONTRIBUTING.md`.

## Open decisions for the follow-up

1. Path A (cheapest, 1 to 2 days, depends on Stencil 5 final keeping `newSpecPage`), path B1 (6 to 9 days by the spike agent's rough estimate; the per-file figure of about 10 minutes is an assumption), or path A first and B1 afterwards (the plugin machinery is shared).
2. Own the plugin fork until Stencil 5 fixes the Mixin problem, or re-run the spike on Stencil 5 final first.
3. v8 coverage with a one-time threshold reset, or `@vitest/coverage-istanbul` for strict parity.
4. Mock-doc as the DOM environment (recommended).
5. Schedule it together with the Stencil 5 upgrade (the built-in runner is removed there).
