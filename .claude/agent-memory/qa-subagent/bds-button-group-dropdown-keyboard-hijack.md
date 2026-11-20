---
name: bds-button-group-dropdown-keyboard-hijack
description: bds-button-group/bds-toolbar roving keydown handler hijacks bds-dropdown menu keys (Left/Right/Home/End in menu; ArrowDown/Up on trigger in vertical group), browser-order-dependent; plus late-children and run-code QA recipe
metadata:
  type: project
---

Verified 2026-11-20 on Chromium, Playwright WebKit and Firefox against the dev build of the EOA-18739 branch.

- Group/toolbar `setLinearNavigation` handlers sit on the host in the bubble phase with `preventDefault` and no target filter, so keys from inside an open `bds-dropdown` menu reach them. With focus on a list item `resolveCurrentIndex` is -1, so ArrowLeft/Right/Home/End jump focus to a group button and the menu closes (horizontal group and toolbar).
- In a vertical group ArrowDown/Up on the trigger fires both the dropdown open handler and the group move. Chromium/WebKit: menu opens, focus goes to Alpha, then the group steals it to the next button and the popover closes. Firefox: the order inverts (focus bounces to next button, then to Alpha, menu stays open). Arrow keys inside the menu are hijacked either way; Enter/Space on the trigger and Tab into the menu still work.
- `bds-button-group` only propagates size/color/variant and validates children at `componentDidLoad`; children appended later get no props, no `tabindex=-1` (extra Tab stops) and no warning.

**Why:** the group's keyboard setup has no awareness of dropdown menus; the dropdown's ArrowDown/Up handler does not stop propagation.
**How to apply:** when QAing any component nested in a roving-tabindex container (group, toolbar, tab-group), press the container's own axis keys while focus is inside the nested popup, not just on the trigger.

QA recipe: `playwright-cli -s=x run-code --filename=file.js` with `async page => {...}` and real `page.keyboard.press`; read result under `### Result`. Generate step scripts with a small python template to avoid shell-quote bugs. macOS `sed -i` needs `''` (a failed `&&` chain silently skips later `cat > file`).
