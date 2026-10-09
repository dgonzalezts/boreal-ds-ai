# release-it Hooks: Names, Timing and Dry Runs

Source: the `@pxglobal` release rehearsal and first real release (2026-10-09), release-it `21.1.0`, `@release-it/conventional-changelog` `12.0.2`.

---

## Hook names use the plugin's full package name

Hooks are `before|after:<step>` for every plugin, and `before|after:<plugin>:<step>` for one plugin. The namespace of an external plugin is its **full package name**, so the key is `after:@release-it/conventional-changelog:beforeRelease`, not `after:conventional-changelog:beforeRelease` (that one silently never fires).

## The changelog is written in `beforeRelease`, after `bump`

- `after:bump` runs **before** the changelog file exists. A script that edits the newest heading finds nothing there.
- In `beforeRelease` the external plugin (changelog) runs first, then the internal ones; the git plugin stages the files (`git add . --update`) in its own `beforeRelease`. A hook after the changelog plugin therefore edits the file **before git stages it**, and the edit ends up in the release commit. `after:beforeRelease` (after the last plugin) is too late: the file would be left modified and unstaged.
- In the `release` stage the npm plugin runs before the git plugin: publish first, then commit, tag and push.

## Hooks do not run in a dry run

`--dry-run` prints the hook but does not execute it. Test a hook with a real release in a scratch clone (`--no-npm.publish`, throwaway git remote), as in the rehearsal recipe of `RELEASING.md`.

## A failing hook before the publish aborts the release safely

Nothing is published or committed. A hook that must never block a release should catch its own errors and exit 0 (see `scripts-boreal/bin/link-changelog-heading.js`).
