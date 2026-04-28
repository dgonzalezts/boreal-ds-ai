# PR Title

refactor(styleguidelines): synchronize all theme and usage tokens with Figma standards

---

# PR Body

Standardizes all brand themes (Proximus, Protect, Engage, Connect) and semantic usage tokens to align with W3C DTCG standards and the latest Figma exports, while improving the robustness of documentation token extraction.

This update synchronizes the local repository with the current Figma source of truth, ensuring consistent naming, hierarchy, and key ordering across all themes. By stripping `$extensions` metadata and reordering keys to match the design source, we reduce file noise and improve maintainability for downstream generators.

N/A

Notes for reviewers:
- **Full Sync**: All 4 theme JSON files and the `colors-themes.json` usage file have been updated, sorted, and cleaned of `$extensions`.
- **Infrastructure**: `tokens-helper.ts` in `boreal-docs` has been updated to support `$value` detection and integrated sanitization to ensure perfect alignment with CSS variable output.
- **Pending**: The new Node.js synchronization scripts and the standardized Figma export documentation are not included in this push and remain pending for the next iteration.

Refs [token-synchronization-and-cleanup.md](.ai/plans/token-synchronization-and-cleanup.md)
