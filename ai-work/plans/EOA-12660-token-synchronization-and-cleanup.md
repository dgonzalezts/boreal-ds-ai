---
ticket: EOA-12660
status: pending
created: 2026-05-19
---

# Token Synchronization and Cleanup Plan

This plan captures the progress made in aligning the Boreal Design System tokens with Figma standards and outlines the remaining steps for full system synchronization.

## Phase 1: Infrastructure & Semantic Alignment (Completed / To be Pushed)

- [x] **Documentation Helper Robustness**: Updated `apps/boreal-docs/src/utils/tokens-helper.ts` to use `$value` for leaf detection and integrated a `sanitizeKey` utility to match generator output.
- [x] **Semantic Mapping Update**: Updated `packages/boreal-styleguidelines/src/tokens/usage/colors-themes.json` to fix typos (`nuetral`, `tael`) and align UI component mappings with Figma's new standard.
- [x] **Semantic Cleanup**: Stripped `$extensions` from `colors-themes.json`.
- [x] **Initial Theme Sync**: Updated and cleaned `packages/boreal-styleguidelines/src/tokens/theme/proximus.json`.

## Phase 2: Tooling & Documentation (Stashed for v2)

- [ ] **Unified Theme Script**: Deploy `update_tokens_scripts.cjs` to the monorepo root. This script handles:
  - Hex-to-Primitive path mapping.
  - Resolving ambiguities using Figma alias data.
  - Deep sorting to match Figma's key sequence.
  - Recursive removal of `$extensions`.
- [ ] **Unified Usage Script**: Deploy `update_usage_tokens.cjs` to sync and sort semantic tokens.
- [ ] **Maintenance Guide**: Deploy `TOKEN_UPDATE_GUIDE.md` containing end-to-end instructions for Figma Dev Mode exports and script execution.

## Phase 3: System-wide Synchronization (Upcoming)

- [ ] **Protect Theme Sync**: Run `update_tokens_scripts.cjs` for `protect.json`.
- [ ] **Engage Theme Sync**: Run `update_tokens_scripts.cjs` for `engage.json`.
- [ ] **Connect Theme Sync**: Run `update_tokens_scripts.cjs` for `connect.json`.
- [ ] **Final Validation**: Execute `pnpm build` and `pnpm validate` within `packages/boreal-styleguidelines` to ensure all generated CSS/SCSS files are correct.

## Phase 4: Maintenance Integration (Future)

- [ ] **Relocate Scripts**: Move utility scripts from the root to `packages/boreal-styleguidelines/scripts/`.
- [ ] **NPM Commands**: Add helper scripts to `package.json` (e.g., `pnpm tokens:sync`).
- [ ] **Relocate Docs**: Move the update guide to `packages/boreal-styleguidelines/docs/TOKENS.md`.
