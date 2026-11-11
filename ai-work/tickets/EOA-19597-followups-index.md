# EOA-19597 follow-up tickets — status index

Single source of truth for what is still open after the EOA-19597 PR, so the same defect is not fixed twice.

| Ticket | Item | Status | Shipped in this PR |
| --- | --- | --- | --- |
| `-search-bar-items-toggle.md` | §1 pick after `items` toggle does not commit | **Fixed** | `fb4c9c2c`, specs `ca6da31f`, playground `24baff37` |
| `-search-bar-items-toggle.md` | §2 `itemsQuery` survives leaving items mode | Open — decision | — |
| `-search-bar-items-toggle.md` | §3 `mode` toggle does not clear the live region | Open — decision | related: `de1b0313` |
| `-bds-popover-hardening.md` | §1 consumer trigger-slot chrome dismisses | Open | — |
| `-bds-popover-hardening.md` | §2 `closeOnClickOutside: false` leak | Open | — |
| `-bds-popover-hardening.md` | §3 focus-outside ownership | Open — decide first | — |
| `-bds-popover-hardening.md` | §4 isolation coverage | Partial | `838b6600` (6 click-outside specs) |
| `-shared-components.md` | §1 reconnect loses listeners | Open — **fixes the root cause of the items-toggle workaround** | search-bar tolerance only |
| `-shared-components.md` | §2 Vue `modelvalue` leak | Open — decide option | shim prototyped + reverted |
| `-shared-components.md` | §3 re-click clears selection | Open | — |
| `-shared-components.md` | §4 date-picker a11y warnings | Open | — |
| `-shared-components.md` | §5 button info noise | Open | — |
| `-shared-components.md` | §6 disabled-field focus forward | Open — decision | guard itself shipped `605049af` |
| `-bds-tag-field-focus-guard.md` | unguarded focus forwarder | Open (latent) | pattern shipped `605049af` |
| `-search-bar-t51-residual.md` | unreproduced pick/focus race | Open — instrument first | T51 fix shipped `12850910` |

## Rules to avoid duplication

1. **One owner per root cause.** Listener rebinding belongs to `-shared-components.md` §1; do not add further tolerance layers in `bds-search-bar`.
2. **Do not rebuild reverted work.** The Vue `modelvalue` runtime shim was built, verified and reverted — reopen only with a recorded decision.
3. **Reuse shipped patterns.** The focus guard (`605049af`) is the reference for `bds-tag-field` and for `bds-text-field`'s `isDisabled` branch.
4. **Partial tickets say so.** `-bds-popover-hardening.md` §4 already carries 6 specs; only the remaining branches need coverage.
5. **Cross-check the failure-mode catalogs** in `ai-work/testing/failure-modes/` (each row lists `Covered by` specs) before writing a new test.
