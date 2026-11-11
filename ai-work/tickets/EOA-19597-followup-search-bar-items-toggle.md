# Follow-up ticket from EOA-19597 — `bds-search-bar` `items` toggle transitions

**Source:** EOA-19597 review follow-ups (2026-10-28)
**Suggested project:** EOA · type: Task · components: `bds-search-bar`, `bds-select`

**Status (2026-10-28):** partially addressed by the EOA-19597 PR — **§1 fixed**, §2–§3 open.
**Already shipped (do not re-implement):** §1. `bds-search-bar.handleSelectChange` now accepts a bubbled `bdsChange` from the bar's own rendered items list and closes the popover for that path (commits `fb4c9c2c`, `ca6da31f`); playground `T61` covers it.
**Overlaps:** the root cause (list listener bound once in `bds-select` and never re-bound) is `EOA-19597-followup-shared-components.md` §1 — fix it **there once**; do not add another tolerance layer in the search bar. §3 is the same live-region contract as `resultsAnnouncement` work shipped in `de1b0313`.


## 1. ~~Picking a suggestion stops committing after `items = undefined` → array~~ — FIXED in EOA-19597

Resolved in the PR by widening `bds-search-bar.handleSelectChange`: it now accepts a bubbled `bdsChange` whose target is the search bar's own rendered items list (and closes the popover for that path), not only one emitted by the `bds-select` itself. Root cause remains in `bds-select` (see `EOA-19597-followup-shared-components.md` §1: the list listener is bound once and never re-bound), so that ticket still covers the general case.

## 2. `itemsQuery` survives leaving items mode — OPEN (decision + doc)

Type `Item 1` → `items = undefined` → re-assign `items` → the list re-applies the old filter and announces `11 results` under an empty field. Self-consistent (count matches list) but undocumented.

**Decision needed:** reset `itemsQuery` when items mode ends, or keep the retained query and document it.

## 3. `mode` toggle does not clear the live region — OPEN (PD-07)

`mode="search"` unmounts the status span but no watcher clears `resultsAnnouncement`, so switching back to `mode="list"` remounts it with the previous count.

**Decision needed:** clear on mode transition (consistent with leaving items mode) or treat the still-applied query's count as correct. Note: if the query survives the toggle, the count is truthful.
