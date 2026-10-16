# Confluence edits to apply by hand (21f)

Read from the exported pages on 2026-10-15. Nothing has been changed in Confluence.

## ADR-0011 (release-it, 2026-01-30): add after "Status" (the Confluence ADR is numbered 0015; the repository file is `0013-...`)

Keep "Accepted" and add this line under it:

> Amended by ADR-0015 (2026-10): release-it is patched, not replaced by changesets. Squash-merge titles, path-scoped bumps, the `@pxglobal` scope, version-heading compare links and skipping packages with nothing to release were added. The release procedure is maintained in `RELEASING.md` at the repository root.

Two statements in "Compliance / Validation" are now imprecise:

- "`pnpm release:all` runs releases in dependency order: styles -> web-components -> `validate:all` -> react -> vue": the order is the same, but the pack validation now runs as a `prerelease` hook of each wrapper, and a package with no releasable commit is skipped.
- The "Component Library Impact" line "released in dependency order" stays true.

The "Considered Options" and "Decision Outcome" text needs no change (historical).

Also in ADR-0011: the Context says versions are derived "via conventional commits (ADR-0013)", while the Links list conventional commits as ADR-0012. That is an existing inconsistency; ADR-0013 in Confluence is not this ADR. Correct the reference to ADR-0012 if you agree.

## ADR-0009 (layered architecture): no change required

It mentions no scope, tag or publish detail. Its only release reference is "(see ADR-0012)" for versioning; versioning is covered by ADR-0011 and ADR-0015, so the reference could point there, but this is optional.

## CI/CD Pipeline Strategy page: already mostly updated; four points to re-check

1. Line "Secret Management: ... a granular npm automation token for `@pxglobal`": bypass-2FA tokens lose direct publishing around January 2027 (npm changelog of 2026-07-08), after which publishes are staged and need a person's approval. Suggested wording: "a granular npm token for `@pxglobal`; direct publishing with bypass-2FA tokens ends around January 2027, so the credential type (stage-only token with approval, or trusted publishing from CI) is to be decided with DevOps".
2. "Manual Release & Storybook Deploy Job" (ITOPS-63144): add that it needs push rights to `release/current` and an approval step for staged publishes, since release-it does not wait for npm.
3. The line "`release-it` with PR-title validation and independent per-package versioning (ADR 0013, Option A; Changesets evaluated and rejected)" must cite ADR-0015, the Confluence number of that decision.
4. The "Pending update" note about the embedded diagrams stays until the diagrams are replaced.

The `@telesign/colibri` rows describe a different product and stay.

## Notification for the owners of consumer pages (to send yourself)

Pages found by an earlier search (names as recorded in the plan; I could not re-check them): "Vue 3 + Boreal - Shared Migration Standards", "Vue 3 + Boreal Migration Plan: Navigator" and the Vue wrapper review page.

> Hi, the Boreal DS packages moved from `@telesign/boreal-*` to `@pxglobal/boreal-*` (public on npm, version `0.14.1`, `latest` tag). The old `@telesign` versions are deprecated with a message that points to the new names. Your Confluence page still mentions the old package names; please update them when you can: `@telesign/boreal-web-components` -> `@pxglobal/boreal-web-components`, and the same for `-react`, `-vue` and `-style-guidelines`. Install without a tag (`npm install @pxglobal/boreal-react`); the `alpha` tag no longer exists. What's new: <Storybook "What's new" link>.
