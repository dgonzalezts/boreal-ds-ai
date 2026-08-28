---
name: component-interface-required-optional-field-ordering
description: Component types/ interfaces must group required members (no ?) before optional members (?), never interleaved
---

Every interface in a component's `types/` directory — `IComponent.ts` and any other interface mixing required and optional fields (event-detail interfaces, internal option objects) — must list all required members (no `?`) before all optional members (`?`). Never interleave them.

Within each group, preserve whatever order already existed; this rule only moves optional members past the required ones.

```typescript
// ✅ Correct
export interface ICalendarGrid {
  grid: MonthGrid;
  year: number;
  month: number;
  prevDisabled: boolean;
  nextDisabled: boolean;
  selectedDate?: string;
  locale?: DateEngineLocale;
}

// ❌ Wrong — selectedDate?/locale? interleaved between required members
export interface ICalendarGrid {
  grid: MonthGrid;
  selectedDate?: string;
  year: number;
  month: number;
  locale?: DateEngineLocale;
  prevDisabled: boolean;
  nextDisabled: boolean;
}
```

**Source:** user manually reordered `bds-date-picker` v2's types this way during EOA-17138 and asked for the rule to be validated across every date-picker-related type file and enforced going forward. Found and fixed one violation: `ICalendarGrid.ts` (`selectedDate?` and `locale?` were interleaved between required fields). `IDatePicker.ts` and every other date-picker/date-engine interface already conformed.

**Enforcement:** documented in full (with the worked example above) in `ai-docs/guidelines/stencil-best-practices.md` → "`IComponent.ts` Interface Contract"; referenced from `@frontend-subagent`'s Working Principles (`.agents/agents/frontend-subagent.md`). No ESLint rule enforces this automatically — it's a manual-review convention, checked the same way the adjacent "optional when the prop has a default" rule in that same section is checked.
