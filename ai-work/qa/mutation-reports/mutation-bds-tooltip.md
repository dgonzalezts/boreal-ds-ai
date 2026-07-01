[32m17:07:19 (75285) INFO ProjectReader[39m Found 1 of 779 file(s) to be mutated.
[32m17:07:19 (75285) INFO Instrumenter[39m Instrumented 1 source file(s) with 109 mutant(s)
[32m17:07:20 (75285) INFO ConcurrencyTokenProvider[39m Creating 10 test runner process(es).
[32m17:07:20 (75285) INFO BroadcastReporter[39m Detected that current console does not support the "progress" reporter, downgrading to "progress-append-only" reporter
[32m17:07:21 (75285) INFO DryRunExecutor[39m Starting initial test run (jest test runner with "perTest" coverage analysis). This may take a while.
[32m17:07:23 (75285) INFO DryRunExecutor[39m Initial test run succeeded. Ran 50 tests in 2 seconds (net 137 ms, overhead 2407 ms).
[33m17:07:25 (75285) WARN ChildProcessProxy[39m Child process [pid 75511] exited unexpectedly with exit code 1 (without signal). Last part of stdout and stderr was:
	/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/packages/boreal-web-components/.stryker-tmp/sandbox-DciDFB/src/mixins/anchored.mixin.ts:201
	                placement: options.placement,
	                                   ^
	
	TypeError: Cannot read properties of undefined (reading 'placement')
	    at BdsTooltip.updatePosition (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/packages/boreal-web-components/.stryker-tmp/sandbox-DciDFB/src/mixins/anchored.mixin.ts:201:36)
	    at sync (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/packages/boreal-web-components/.stryker-tmp/sandbox-DciDFB/src/mixins/anchored.mixin.ts:224:27)
	    at BdsTooltip.startAutoUpdate (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/packages/boreal-web-components/.stryker-tmp/sandbox-DciDFB/src/mixins/anchored.mixin.ts:226:13)
	    at BdsTooltip.showElement (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/packages/boreal-web-components/.stryker-tmp/sandbox-DciDFB/src/mixins/anchored.mixin.ts:110:18)
	    at BdsTooltip.show (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/packages/boreal-web-components/.stryker-tmp/sandbox-DciDFB/src/mixins/floating.mixin.ts:146:18)
	    at MockHTMLElement.<anonymous> (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/packages/boreal-web-components/.stryker-tmp/sandbox-DciDFB/src/components/overlays/bds-tooltip/bds-tooltip.tsx:282:181)
	    at /Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/node_modules/.pnpm/@stencil+core@4.42.1/node_modules/@stencil/core/mock-doc/index.cjs:709:26
	    at Array.forEach (<anonymous>)
	    at triggerEventListener (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/node_modules/.pnpm/@stencil+core@4.42.1/node_modules/@stencil/core/mock-doc/index.cjs:707:15)
	    at triggerEventListener (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/node_modules/.pnpm/@stencil+core@4.42.1/node_modules/@stencil/core/mock-doc/index.cjs:724:5)
	    at dispatchEvent (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/node_modules/.pnpm/@stencil+core@4.42.1/node_modules/@stencil/core/mock-doc/index.cjs:741:3)
	    at HostElement.dispatchEvent (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/node_modules/.pnpm/@stencil+core@4.42.1/node_modules/@stencil/core/mock-doc/index.cjs:6968:12)
	    at Object.<anonymous> (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/packages/boreal-web-components/.stryker-tmp/sandbox-DciDFB/src/components/overlays/bds-tooltip/__test__/bds-tooltip-events.spec.ts:15:14)
	    at processTicksAndRejections (node:internal/process/task_queues:105:5)
	
	Node.js v22.21.1
	 ChildProcessCrashedError: Child process [pid 75511] exited unexpectedly with exit code 1 (without signal). Last part of stdout and stderr was:
	/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/packages/boreal-web-components/.stryker-tmp/sandbox-DciDFB/src/mixins/anchored.mixin.ts:201
	                placement: options.placement,
	                                   ^
	
	TypeError: Cannot read properties of undefined (reading 'placement')
	    at BdsTooltip.updatePosition (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/packages/boreal-web-components/.stryker-tmp/sandbox-DciDFB/src/mixins/anchored.mixin.ts:201:36)
	    at sync (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/packages/boreal-web-components/.stryker-tmp/sandbox-DciDFB/src/mixins/anchored.mixin.ts:224:27)
	    at BdsTooltip.startAutoUpdate (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/packages/boreal-web-components/.stryker-tmp/sandbox-DciDFB/src/mixins/anchored.mixin.ts:226:13)
	    at BdsTooltip.showElement (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/packages/boreal-web-components/.stryker-tmp/sandbox-DciDFB/src/mixins/anchored.mixin.ts:110:18)
	    at BdsTooltip.show (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/packages/boreal-web-components/.stryker-tmp/sandbox-DciDFB/src/mixins/floating.mixin.ts:146:18)
	    at MockHTMLElement.<anonymous> (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/packages/boreal-web-components/.stryker-tmp/sandbox-DciDFB/src/components/overlays/bds-tooltip/bds-tooltip.tsx:282:181)
	    at /Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/node_modules/.pnpm/@stencil+core@4.42.1/node_modules/@stencil/core/mock-doc/index.cjs:709:26
	    at Array.forEach (<anonymous>)
	    at triggerEventListener (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/node_modules/.pnpm/@stencil+core@4.42.1/node_modules/@stencil/core/mock-doc/index.cjs:707:15)
	    at triggerEventListener (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/node_modules/.pnpm/@stencil+core@4.42.1/node_modules/@stencil/core/mock-doc/index.cjs:724:5)
	    at dispatchEvent (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/node_modules/.pnpm/@stencil+core@4.42.1/node_modules/@stencil/core/mock-doc/index.cjs:741:3)
	    at HostElement.dispatchEvent (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/node_modules/.pnpm/@stencil+core@4.42.1/node_modules/@stencil/core/mock-doc/index.cjs:6968:12)
	    at Object.<anonymous> (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/packages/boreal-web-components/.stryker-tmp/sandbox-DciDFB/src/components/overlays/bds-tooltip/__test__/bds-tooltip-events.spec.ts:15:14)
	    at processTicksAndRejections (node:internal/process/task_queues:105:5)
	
	Node.js v22.21.1
	
    at ChildProcess.handleUnexpectedExit (file:///Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/node_modules/.pnpm/@stryker-mutator+core@9.6.1_@types+node@22.19.11/node_modules/@stryker-mutator/core/dist/src/child-proxy/child-process-proxy.js:180:31)
    at ChildProcess.emit (node:events:519:28)
    at maybeClose (node:internal/child_process:1101:16)
    at Socket.<anonymous> (node:internal/child_process:456:11)
    at Socket.emit (node:events:519:28)
    at Pipe.<anonymous> (node:net:346:12) {
  innerError: undefined,
  pid: 75511,
  exitCode: 1,
  signal: null
}
[33m17:07:29 (75285) WARN ChildProcessProxy[39m Child process [pid 76262] exited unexpectedly with exit code 1 (without signal). Last part of stdout and stderr was:
	/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/packages/boreal-web-components/.stryker-tmp/sandbox-DciDFB/src/mixins/anchored.mixin.ts:201
	                placement: options.placement,
	                                   ^
	
	TypeError: Cannot read properties of undefined (reading 'placement')
	    at BdsTooltip.updatePosition (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/packages/boreal-web-components/.stryker-tmp/sandbox-DciDFB/src/mixins/anchored.mixin.ts:201:36)
	    at sync (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/packages/boreal-web-components/.stryker-tmp/sandbox-DciDFB/src/mixins/anchored.mixin.ts:224:27)
	    at BdsTooltip.startAutoUpdate (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/packages/boreal-web-components/.stryker-tmp/sandbox-DciDFB/src/mixins/anchored.mixin.ts:226:13)
	    at BdsTooltip.showElement (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/packages/boreal-web-components/.stryker-tmp/sandbox-DciDFB/src/mixins/anchored.mixin.ts:110:18)
	    at BdsTooltip.show (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/packages/boreal-web-components/.stryker-tmp/sandbox-DciDFB/src/mixins/floating.mixin.ts:146:18)
	    at MockHTMLElement.<anonymous> (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/packages/boreal-web-components/.stryker-tmp/sandbox-DciDFB/src/components/overlays/bds-tooltip/bds-tooltip.tsx:282:181)
	    at /Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/node_modules/.pnpm/@stencil+core@4.42.1/node_modules/@stencil/core/mock-doc/index.cjs:709:26
	    at Array.forEach (<anonymous>)
	    at triggerEventListener (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/node_modules/.pnpm/@stencil+core@4.42.1/node_modules/@stencil/core/mock-doc/index.cjs:707:15)
	    at triggerEventListener (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/node_modules/.pnpm/@stencil+core@4.42.1/node_modules/@stencil/core/mock-doc/index.cjs:724:5)
	    at dispatchEvent (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/node_modules/.pnpm/@stencil+core@4.42.1/node_modules/@stencil/core/mock-doc/index.cjs:741:3)
	    at HostElement.dispatchEvent (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/node_modules/.pnpm/@stencil+core@4.42.1/node_modules/@stencil/core/mock-doc/index.cjs:6968:12)
	    at Object.<anonymous> (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/packages/boreal-web-components/.stryker-tmp/sandbox-DciDFB/src/components/overlays/bds-tooltip/__test__/bds-tooltip-basics.spec.ts:20:10)
	    at processTicksAndRejections (node:internal/process/task_queues:105:5)
	
	Node.js v22.21.1
	 ChildProcessCrashedError: Child process [pid 76262] exited unexpectedly with exit code 1 (without signal). Last part of stdout and stderr was:
	/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/packages/boreal-web-components/.stryker-tmp/sandbox-DciDFB/src/mixins/anchored.mixin.ts:201
	                placement: options.placement,
	                                   ^
	
	TypeError: Cannot read properties of undefined (reading 'placement')
	    at BdsTooltip.updatePosition (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/packages/boreal-web-components/.stryker-tmp/sandbox-DciDFB/src/mixins/anchored.mixin.ts:201:36)
	    at sync (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/packages/boreal-web-components/.stryker-tmp/sandbox-DciDFB/src/mixins/anchored.mixin.ts:224:27)
	    at BdsTooltip.startAutoUpdate (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/packages/boreal-web-components/.stryker-tmp/sandbox-DciDFB/src/mixins/anchored.mixin.ts:226:13)
	    at BdsTooltip.showElement (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/packages/boreal-web-components/.stryker-tmp/sandbox-DciDFB/src/mixins/anchored.mixin.ts:110:18)
	    at BdsTooltip.show (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/packages/boreal-web-components/.stryker-tmp/sandbox-DciDFB/src/mixins/floating.mixin.ts:146:18)
	    at MockHTMLElement.<anonymous> (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/packages/boreal-web-components/.stryker-tmp/sandbox-DciDFB/src/components/overlays/bds-tooltip/bds-tooltip.tsx:282:181)
	    at /Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/node_modules/.pnpm/@stencil+core@4.42.1/node_modules/@stencil/core/mock-doc/index.cjs:709:26
	    at Array.forEach (<anonymous>)
	    at triggerEventListener (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/node_modules/.pnpm/@stencil+core@4.42.1/node_modules/@stencil/core/mock-doc/index.cjs:707:15)
	    at triggerEventListener (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/node_modules/.pnpm/@stencil+core@4.42.1/node_modules/@stencil/core/mock-doc/index.cjs:724:5)
	    at dispatchEvent (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/node_modules/.pnpm/@stencil+core@4.42.1/node_modules/@stencil/core/mock-doc/index.cjs:741:3)
	    at HostElement.dispatchEvent (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/node_modules/.pnpm/@stencil+core@4.42.1/node_modules/@stencil/core/mock-doc/index.cjs:6968:12)
	    at Object.<anonymous> (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/packages/boreal-web-components/.stryker-tmp/sandbox-DciDFB/src/components/overlays/bds-tooltip/__test__/bds-tooltip-basics.spec.ts:20:10)
	    at processTicksAndRejections (node:internal/process/task_queues:105:5)
	
	Node.js v22.21.1
	
    at ChildProcess.handleUnexpectedExit (file:///Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/node_modules/.pnpm/@stryker-mutator+core@9.6.1_@types+node@22.19.11/node_modules/@stryker-mutator/core/dist/src/child-proxy/child-process-proxy.js:180:31)
    at ChildProcess.emit (node:events:519:28)
    at maybeClose (node:internal/child_process:1101:16)
    at Socket.<anonymous> (node:internal/child_process:456:11)
    at Socket.emit (node:events:519:28)
    at Pipe.<anonymous> (node:net:346:12) {
  innerError: undefined,
  pid: 76262,
  exitCode: 1,
  signal: null
}
Mutation testing 21% (elapsed: <1m, remaining: <1m) 19/109 tested (1 survived, 0 timed out)
Mutation testing 35% (elapsed: <1m, remaining: <1m) 44/109 tested (2 survived, 0 timed out)
Mutation testing 54% (elapsed: <1m, remaining: <1m) 67/109 tested (2 survived, 0 timed out)
Mutation testing 76% (elapsed: <1m, remaining: <1m) 86/109 tested (2 survived, 0 timed out)
Mutation testing 91% (elapsed: <1m, remaining: <1m) 102/109 tested (2 survived, 0 timed out)

All tests
  bds-tooltip-a11.spec.ts
    ~ bds-tooltip accessibility testing role and aria attributes Should have role="tooltip" on content element [line 8] (covered 83)
    ~ bds-tooltip accessibility testing role and aria attributes Should return null when trigger is not activated [line 21] (covered 53)
    ~ bds-tooltip accessibility testing role and aria attributes Should have "tooltip" class on host [line 31] (covered 53)
  bds-tooltip-basics.spec.ts
    ✓ bds-tooltip core testing Basic render whitout any floating modification [line 10] (killed 11)
    ✓ bds-tooltip core testing Should render with disabled prop and hide the tooltip on hover [line 34] (killed 2)
    ✓ bds-tooltip core testing Should apply floatingOptions with placement top and hideArrow [line 61] (killed 1)
    ~ bds-tooltip core testing should apply floatingOptions with placement bottom and stayOnHover [line 78] (covered 82)
    ~ bds-tooltip core testing Should return correct options from getter when floatingOptions overridden [line 101] (covered 54)
    ✓ bds-tooltip core testing Should resolve the internal positioning "options" getter with a fixed strategy and default placement [line 116] (killed 1)
  bds-tooltip-events.spec.ts
    ✓ bds-tooltip floating hooks Should call mocked showPopover when show is shown [line 14] (killed 9)
    ✓ bds-tooltip floating hooks Should call mocked hidePopover when show is hidden [line 25] (killed 1)
    ~ bds-tooltip floating hooks Should call custom afterShow Hook when tooltip if shown [line 39] (covered 83)
    ~ bds-tooltip floating hooks Should call custom beforeShow Hook when tooltip if shown [line 53] (covered 83)
    ~ bds-tooltip floating hooks Should call custom afterHide Hook when tooltip if hidden [line 67] (covered 90)
    ~ bds-tooltip floating hooks Should call custom beforeHide Hook when tooltip if hidden [line 83] (covered 90)
    ~ bds-tooltip floating hooks Should call custom mount Hook when tooltip if hidden [line 113] (covered 90)
    ~ bds-tooltip floating hooks Should call mocked hooks in order [line 130] (covered 90)
    ✓ bds-tooltip validateHide stayOnHover guard keeps the tooltip visible when stayOnHover is true and the pointer moves onto a descendant of the floating content [line 159] (killed 10)
    ~ bds-tooltip validateHide stayOnHover guard keeps the tooltip visible when stayOnHover is true and the pointer moves directly onto the floating content element [line 180] (covered 98)
    ~ bds-tooltip validateHide stayOnHover guard hides the tooltip when stayOnHover is true but the pointer moves to an unrelated, unconnected element [line 201] (covered 92)
    ✓ bds-tooltip validateHide stayOnHover guard hides the tooltip when stayOnHover is true but the pointer moves to an unrelated element that is connected to the document [line 222] (killed 3)
    ✓ bds-tooltip validateHide stayOnHover guard hides the tooltip when stayOnHover is false even if the pointer moves into the floating content [line 244] (killed 1)
    ~ bds-tooltip validateHide stayOnHover guard hides the tooltip when stayOnHover is unset (default) even if the pointer moves into the floating content [line 265] (covered 90)
    ✓ bds-tooltip validateHide stayOnHover guard hides the tooltip when stayOnHover is true and hide is triggered without a relatedTarget [line 283] (killed 2)
    ✓ bds-tooltip onPositionUpdate hook (handlePosition/setArrowPosition) applies data-placement and arrow x/y styles when middleware data, disabled and arrow connection are all favorable [line 307] (killed 21)
    ✓ bds-tooltip onPositionUpdate hook (handlePosition/setArrowPosition) falls back to empty left/top styles when the arrow x/y coordinates are null [line 329] (killed 4)
    ✓ bds-tooltip onPositionUpdate hook (handlePosition/setArrowPosition) skips the arrow style update (without throwing) when disabled is true [line 349] (killed 4)
    ✓ bds-tooltip onPositionUpdate hook (handlePosition/setArrowPosition) skips the arrow style update (without throwing) when middlewareData itself is undefined [line 369] (killed 1)
    ~ bds-tooltip onPositionUpdate hook (handlePosition/setArrowPosition) skips the arrow style update (without throwing) when middlewareData is present but has no arrow entry [line 389] (covered 62)
    ✓ bds-tooltip onPositionUpdate hook (handlePosition/setArrowPosition) skips the arrow style update (without throwing) when the arrow is hidden and never connected to the DOM [line 409] (killed 2)
    ✓ bds-tooltip subscribeToTrigger guard does not throw and does not attach listeners when subscribe is called without a trigger element [line 432] (killed 1)
  bds-tooltip-keyboard.spec.ts
    ✓ bds-tooltip keyboard should show tooltip on focusin of trigger [line 11] (killed 5)
    ✓ bds-tooltip keyboard should hide tooltip on focusout when focus leaves the trigger [line 24] (killed 4)
    ✓ bds-tooltip keyboard should not hide tooltip on focusout when focus moves within the trigger [line 41] (killed 1)
    ✓ bds-tooltip keyboard should hide tooltip on Escape key while tooltip is visible [line 60] (killed 1)
    ~ bds-tooltip keyboard should remain hidden on Escape when tooltip was not shown [line 77] (covered 53)
    ~ bds-tooltip keyboard should not respond to unrelated keys [line 92] (covered 53)
    ✓ bds-tooltip keyboard should not call preventDefault on the Escape keydown event, per WCAG 1.4.13 (content must be dismissible without side effects) [line 107] (killed 2)
    ✓ bds-tooltip keyboard should set aria-describedby on trigger pointing to tooltip-content [line 124] (killed 2)
    ✓ bds-tooltip keyboard should set part="tooltip-trigger" on trigger [line 133] (killed 2)
    ✓ bds-tooltip keyboard should detach the keyboard controller when disconnectedCallback runs [line 143] (killed 1)
  bds-tooltip-variants.spec.ts
    ~ bds-tooltip variants placement, arrow, multiline and disabled Should apply floatingOptions with placement left [line 9] (covered 53)
    ~ bds-tooltip variants placement, arrow, multiline and disabled Should apply floatingOptions with placement right [line 23] (covered 53)
    ✓ bds-tooltip variants placement, arrow, multiline and disabled Should render arrow by default [line 37] (killed 1)
    ✓ bds-tooltip variants placement, arrow, multiline and disabled should NOT render arrow when hideArrow is true [line 47] (killed 5)
    ~ bds-tooltip variants placement, arrow, multiline and disabled Should render with multiline prop the height should be greather than 32px [line 65] (covered 53)
    ✓ bds-tooltip variants placement, arrow, multiline and disabled Should resolve hasMultiline to true when multiline is true [line 76] (killed 5)
    ✓ bds-tooltip variants placement, arrow, multiline and disabled Should resolve hasMultiline to false when multiline is left at its default (false) [line 88] (killed 2)
    ✓ bds-tooltip variants placement, arrow, multiline and disabled Should resolve hasMultiline to false (not undefined) when multiline is explicitly set to undefined [line 100] (killed 1)

[Survived] OptionalChaining
src/components/overlays/bds-tooltip/bds-tooltip.tsx:62:25
-         offset: getOffset(this.floatingOptions?.hideArrow, this.floatingOptions.offset, OFFSET),
+         offset: getOffset(this.floatingOptions.hideArrow, this.floatingOptions.offset, OFFSET),
Tests ran:
    bds-tooltip floating hooks Should call mocked showPopover when show is shown
    bds-tooltip floating hooks Should call mocked hidePopover when show is hidden
    bds-tooltip floating hooks Should call custom afterShow Hook when tooltip if shown
  and 21 more tests!


[Survived] ConditionalExpression
src/components/overlays/bds-tooltip/bds-tooltip.tsx:113:72
-         const goingToFloating = this.floatingContent.contains(target) || this.floatingContent === target;
+         const goingToFloating = this.floatingContent.contains(target) || false;
Tests ran:
    bds-tooltip validateHide stayOnHover guard hides the tooltip when stayOnHover is true but the pointer moves to an unrelated element that is connected to the document


Ran 33.02 tests per mutant on average.
-----------------|------------------|----------|-----------|------------|----------|----------|
                 | % Mutation score |          |           |            |          |          |
File             |  total | covered | # killed | # timeout | # survived | # no cov | # errors |
-----------------|--------|---------|----------|-----------|------------|----------|----------|
All files        |  98.15 |   98.15 |      106 |         0 |          2 |        0 |        1 |
 bds-tooltip.tsx |  98.15 |   98.15 |      106 |         0 |          2 |        0 |        1 |
-----------------|--------|---------|----------|-----------|------------|----------|----------|
[32m17:08:14 (75285) INFO HtmlReporter[39m Your report can be found at: file:///Users/dgonzalez/projects/src/boreal-ds/.worktrees/mutation-bds-tooltip/packages/boreal-web-components/reports/mutation/mutation.html
[32m17:08:14 (75285) INFO MutationTestExecutor[39m Done in 55 seconds.
