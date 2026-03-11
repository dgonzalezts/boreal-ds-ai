# PR Title

feat(scripts): EOA-10230 add deployment publishing pipeline with pack validation

---

# PR Body

Introduces `scripts-boreal`, a new workspace package that implements a pack-based
publishing validation pipeline for Boreal DS artifacts.

Before this, there was no way to verify that `exports`, `files`, and `publishConfig`
were correctly wired before a release. Workspace symlinks mask these problems locally —
`pnpm pack` + install into the framework wrappers and demo app surfaces them the same
way a downstream consumer would see them. The `validate:pack` script enables CI to catch
broken package manifests before they reach npm; `dev:pack` lets contributors reproduce
the same environment locally without a full publish.

The pipeline packs each publishable package as a real `.tgz`, installs it into
`react-testapp` and the framework wrappers, and then runs a build against those
artifacts. Cleanup is handled via `git checkout HEAD` on `package.json` and
`pnpm-lock.yaml` to leave the working tree unmodified after a run.

Also adds a postbuild script that promotes generated CSS and SCSS files to the
`dist/` root of `boreal-web-components`, a JSDoc plugin for custom tag name handling
in Stencil, and a basic playground update to `react-testapp` for manual smoke-testing.

Refs EOA-10230
