# npm Staged Publishing in the First Real Release

Source: first `@pxglobal` release (2026-10-09).

---

## What happened

- The four publishes were run with `release-it` (label `npm publish`, executed by `pnpm publish`) from a machine with npm `10.9.9` (the `npm stage` commands need `11.15`). The **registry** still held each publish: npm printed a link, and approving it in the browser with a passkey made the version installable.
- For each new package name npm created a public placeholder version `0.0.0-stage` ("Temporary Holding Version"). It stays in the version list, is never `latest`, and is not selected by `npm install`, `^0.14.0` or `*`. Deprecate it.
- Registry timeline (UTC): placeholders at 01:52:56, 01:54:36, 01:56:18, 01:57:37; real versions live at 01:53:51, 01:56:45, 01:57:34, 01:59:45.

## release-it does not wait for the approval

The release commit and tag were pushed 4 to 6 seconds after each placeholder, i.e. 49 to 125 seconds before the version was installable, and React started staging before web-components had been approved. Approve in dependency order (style-guidelines, web-components, React, Vue) and verify only afterwards.

## Not known yet

Whether the registry holds **every** publish of this account or only the first publish of a new package. npm's docs do not say. After the second release, record the answer in `RELEASING.md` ("Approving the publish": keep it or delete it).

## Rehearsals cannot show it

A local Verdaccio registry does not emulate staged publishing.
