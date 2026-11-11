# `eslint` passing does not mean the spec file is formatted

`prettier --check` and `eslint` are **not** the same gate in this repo. A new spec file can pass
`pnpm --filter @pxglobal/boreal-web-components exec eslint <file>` with exit `0` and still fail prettier —
verified 2026-10-26 on `bds-popover.click-outside.spec.ts` (import list and the `closeOnClickOutside` fixture
call both wrapped differently than prettier wants).

Prettier is enforced, just later than lint:

- `.lintstagedrc.js` runs `lint:fix` **and** `format` on `packages/boreal-web-components/src/**/*.{ts,tsx}`
  for every pre-commit.
- Every existing file in `src/components/overlays/**` already passes `prettier --check`, so "the neighbours are
  unformatted" is not an excuse — an unformatted new file is the outlier.

Do this before declaring a spec task done:

```bash
.agents/scripts/with-node.sh bash -c 'cd packages/boreal-web-components && npx prettier --check <spec path>'
# then, if warned:
.agents/scripts/with-node.sh bash -c 'cd packages/boreal-web-components && npx prettier --write <spec path>'
```

Note the `bash -c 'cd ...'` wrapper: `with-node.sh` `cd`s to the repo root before `exec`, so a bare relative
path passed from a package-relative shell resolves against the repo root and silently checks nothing useful
(same root cause as the "pass the package tsconfig absolutely" note in `MEMORY.md`).

Re-run the spec after `--write`; formatting-only changes are safe but the file is what CI will see.
