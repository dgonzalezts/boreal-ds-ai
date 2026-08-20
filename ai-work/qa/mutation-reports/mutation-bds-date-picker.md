[32m23:57:31 (86829) INFO ProjectReader[39m Found 7 of 3610 file(s) to be mutated.
Browserslist: browsers data (caniuse-lite) is 7 months old. Please run:
  npx update-browserslist-db@latest
  Why you should do it regularly: https://github.com/browserslist/update-db#readme
[32m23:57:31 (86829) INFO Instrumenter[39m Instrumented 7 source file(s) with 198 mutant(s)
[32m23:57:32 (86829) INFO ConcurrencyTokenProvider[39m Creating 2 test runner process(es).
[32m23:57:33 (86829) INFO BroadcastReporter[39m Detected that current console does not support the "progress" reporter, downgrading to "progress-append-only" reporter
[32m23:57:34 (86829) INFO DryRunExecutor[39m Starting initial test run (jest test runner with "perTest" coverage analysis). This may take a while.
[32m23:57:38 (86829) INFO DryRunExecutor[39m Initial test run succeeded. Ran 85 tests in 3 seconds (net 843 ms, overhead 3111 ms).
Mutation testing 6% (elapsed: <1m, remaining: ~2m) 7/198 tested (0 survived, 0 timed out)
Mutation testing 11% (elapsed: <1m, remaining: ~2m) 13/198 tested (2 survived, 0 timed out)
Mutation testing 16% (elapsed: <1m, remaining: ~2m) 21/198 tested (2 survived, 0 timed out)
Mutation testing 21% (elapsed: <1m, remaining: ~2m) 28/198 tested (2 survived, 0 timed out)
[33m23:58:18 (86829) WARN ChildProcessProxy[39m Child process [pid 87192] exited unexpectedly with exit code 1 (without signal). Last part of stdout and stderr was:
	/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/components/overlays/bds-popover/bds-popover.tsx:350
	        trigger.setAttribute('part', 'popover-trigger');
	                ^
	
	TypeError: Cannot read properties of null (reading 'setAttribute')
	    at BdsPopover.subscribe (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/components/overlays/bds-popover/bds-popover.tsx:350:17)
	    at BdsPopover.setAnchorElement (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/components/overlays/bds-popover/bds-popover.tsx:506:14)
	    at /Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/node_modules/.pnpm/@stencil+core@4.42.1/node_modules/@stencil/core/internal/testing/index.js:5491:83
	    at processTicksAndRejections (node:internal/process/task_queues:105:5)
	
	Node.js v22.21.1
	 ChildProcessCrashedError: Child process [pid 87192] exited unexpectedly with exit code 1 (without signal). Last part of stdout and stderr was:
	/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/components/overlays/bds-popover/bds-popover.tsx:350
	        trigger.setAttribute('part', 'popover-trigger');
	                ^
	
	TypeError: Cannot read properties of null (reading 'setAttribute')
	    at BdsPopover.subscribe (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/components/overlays/bds-popover/bds-popover.tsx:350:17)
	    at BdsPopover.setAnchorElement (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/components/overlays/bds-popover/bds-popover.tsx:506:14)
	    at /Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/node_modules/.pnpm/@stencil+core@4.42.1/node_modules/@stencil/core/internal/testing/index.js:5491:83
	    at processTicksAndRejections (node:internal/process/task_queues:105:5)
	
	Node.js v22.21.1
	
    at ChildProcess.handleUnexpectedExit (file:///Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/node_modules/.pnpm/@stryker-mutator+core@10.0.0_@types+node@22.19.11/node_modules/@stryker-mutator/core/dist/src/child-proxy/child-process-proxy.js:180:31)
    at ChildProcess.emit (node:events:519:28)
    at maybeClose (node:internal/child_process:1101:16)
    at ChildProcess._handle.onexit (node:internal/child_process:304:5) {
  innerError: undefined,
  pid: 87192,
  exitCode: 1,
  signal: null
}
[33m23:58:20 (86829) WARN ChildProcessProxy[39m Child process [pid 90642] exited unexpectedly with exit code 1 (without signal). Last part of stdout and stderr was:
	/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/components/overlays/bds-popover/bds-popover.tsx:350
	        trigger.setAttribute('part', 'popover-trigger');
	                ^
	
	TypeError: Cannot read properties of null (reading 'setAttribute')
	    at BdsPopover.subscribe (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/components/overlays/bds-popover/bds-popover.tsx:350:17)
	    at BdsPopover.setAnchorElement (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/components/overlays/bds-popover/bds-popover.tsx:506:14)
	    at /Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/node_modules/.pnpm/@stencil+core@4.42.1/node_modules/@stencil/core/internal/testing/index.js:5491:83
	    at processTicksAndRejections (node:internal/process/task_queues:105:5)
	
	Node.js v22.21.1
	 ChildProcessCrashedError: Child process [pid 90642] exited unexpectedly with exit code 1 (without signal). Last part of stdout and stderr was:
	/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/components/overlays/bds-popover/bds-popover.tsx:350
	        trigger.setAttribute('part', 'popover-trigger');
	                ^
	
	TypeError: Cannot read properties of null (reading 'setAttribute')
	    at BdsPopover.subscribe (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/components/overlays/bds-popover/bds-popover.tsx:350:17)
	    at BdsPopover.setAnchorElement (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/components/overlays/bds-popover/bds-popover.tsx:506:14)
	    at /Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/node_modules/.pnpm/@stencil+core@4.42.1/node_modules/@stencil/core/internal/testing/index.js:5491:83
	    at processTicksAndRejections (node:internal/process/task_queues:105:5)
	
	Node.js v22.21.1
	
    at ChildProcess.handleUnexpectedExit (file:///Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/node_modules/.pnpm/@stryker-mutator+core@10.0.0_@types+node@22.19.11/node_modules/@stryker-mutator/core/dist/src/child-proxy/child-process-proxy.js:180:31)
    at ChildProcess.emit (node:events:519:28)
    at maybeClose (node:internal/child_process:1101:16)
    at Socket.<anonymous> (node:internal/child_process:456:11)
    at Socket.emit (node:events:519:28)
    at Pipe.<anonymous> (node:net:346:12) {
  innerError: undefined,
  pid: 90642,
  exitCode: 1,
  signal: null
}
[33m23:58:22 (86829) WARN ChildProcessProxy[39m Child process [pid 90800] exited unexpectedly with exit code 1 (without signal). Last part of stdout and stderr was:
	/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/components/overlays/bds-popover/bds-popover.tsx:350
	        trigger.setAttribute('part', 'popover-trigger');
	                ^
	
	TypeError: Cannot read properties of null (reading 'setAttribute')
	    at BdsPopover.subscribe (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/components/overlays/bds-popover/bds-popover.tsx:350:17)
	    at BdsPopover.setAnchorElement (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/components/overlays/bds-popover/bds-popover.tsx:506:14)
	    at /Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/node_modules/.pnpm/@stencil+core@4.42.1/node_modules/@stencil/core/internal/testing/index.js:5491:83
	    at processTicksAndRejections (node:internal/process/task_queues:105:5)
	
	Node.js v22.21.1
	 ChildProcessCrashedError: Child process [pid 90800] exited unexpectedly with exit code 1 (without signal). Last part of stdout and stderr was:
	/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/components/overlays/bds-popover/bds-popover.tsx:350
	        trigger.setAttribute('part', 'popover-trigger');
	                ^
	
	TypeError: Cannot read properties of null (reading 'setAttribute')
	    at BdsPopover.subscribe (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/components/overlays/bds-popover/bds-popover.tsx:350:17)
	    at BdsPopover.setAnchorElement (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/components/overlays/bds-popover/bds-popover.tsx:506:14)
	    at /Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/node_modules/.pnpm/@stencil+core@4.42.1/node_modules/@stencil/core/internal/testing/index.js:5491:83
	    at processTicksAndRejections (node:internal/process/task_queues:105:5)
	
	Node.js v22.21.1
	
    at ChildProcess.handleUnexpectedExit (file:///Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/node_modules/.pnpm/@stryker-mutator+core@10.0.0_@types+node@22.19.11/node_modules/@stryker-mutator/core/dist/src/child-proxy/child-process-proxy.js:180:31)
    at ChildProcess.emit (node:events:519:28)
    at maybeClose (node:internal/child_process:1101:16)
    at ChildProcess._handle.onexit (node:internal/child_process:304:5) {
  innerError: undefined,
  pid: 90800,
  exitCode: 1,
  signal: null
}
[33m23:58:24 (86829) WARN ChildProcessProxy[39m Child process [pid 90888] exited unexpectedly with exit code 1 (without signal). Last part of stdout and stderr was:
	/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/components/overlays/bds-popover/bds-popover.tsx:350
	        trigger.setAttribute('part', 'popover-trigger');
	                ^
	
	TypeError: Cannot read properties of null (reading 'setAttribute')
	    at BdsPopover.subscribe (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/components/overlays/bds-popover/bds-popover.tsx:350:17)
	    at BdsPopover.setAnchorElement (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/components/overlays/bds-popover/bds-popover.tsx:506:14)
	    at /Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/node_modules/.pnpm/@stencil+core@4.42.1/node_modules/@stencil/core/internal/testing/index.js:5491:83
	    at processTicksAndRejections (node:internal/process/task_queues:105:5)
	
	Node.js v22.21.1
	 ChildProcessCrashedError: Child process [pid 90888] exited unexpectedly with exit code 1 (without signal). Last part of stdout and stderr was:
	/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/components/overlays/bds-popover/bds-popover.tsx:350
	        trigger.setAttribute('part', 'popover-trigger');
	                ^
	
	TypeError: Cannot read properties of null (reading 'setAttribute')
	    at BdsPopover.subscribe (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/components/overlays/bds-popover/bds-popover.tsx:350:17)
	    at BdsPopover.setAnchorElement (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/components/overlays/bds-popover/bds-popover.tsx:506:14)
	    at /Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/node_modules/.pnpm/@stencil+core@4.42.1/node_modules/@stencil/core/internal/testing/index.js:5491:83
	    at processTicksAndRejections (node:internal/process/task_queues:105:5)
	
	Node.js v22.21.1
	
    at ChildProcess.handleUnexpectedExit (file:///Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/node_modules/.pnpm/@stryker-mutator+core@10.0.0_@types+node@22.19.11/node_modules/@stryker-mutator/core/dist/src/child-proxy/child-process-proxy.js:180:31)
    at ChildProcess.emit (node:events:519:28)
    at maybeClose (node:internal/child_process:1101:16)
    at ChildProcess._handle.onexit (node:internal/child_process:304:5) {
  innerError: undefined,
  pid: 90888,
  exitCode: 1,
  signal: null
}
Mutation testing 24% (elapsed: <1m, remaining: ~2m) 33/198 tested (3 survived, 0 timed out)
Mutation testing 30% (elapsed: ~1m, remaining: ~2m) 39/198 tested (4 survived, 0 timed out)
Mutation testing 33% (elapsed: ~1m, remaining: ~2m) 47/198 tested (4 survived, 0 timed out)
Mutation testing 36% (elapsed: ~1m, remaining: ~2m) 54/198 tested (4 survived, 0 timed out)
Mutation testing 38% (elapsed: ~1m, remaining: ~2m) 65/198 tested (4 survived, 0 timed out)
Mutation testing 39% (elapsed: ~1m, remaining: ~2m) 77/198 tested (5 survived, 0 timed out)
Mutation testing 39% (elapsed: ~1m, remaining: ~2m) 92/198 tested (7 survived, 0 timed out)
Mutation testing 42% (elapsed: ~2m, remaining: ~2m) 95/198 tested (8 survived, 0 timed out)
[33m23:59:43 (86829) WARN ChildProcessProxy[39m Child process [pid 87191] exited unexpectedly with exit code 1 (without signal). Last part of stdout and stderr was:
	/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/services/logger/Logger.ts:24
	        throw new Error(`[${component}]: ${message}`);
	              ^
	
	Error: [AnchoredMixin.show]: triggerSlot is required
	    at Logger.error (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/services/logger/Logger.ts:28:11)
	    at BdsPopover.onBeforeShow (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/mixins/anchored.mixin.ts:158:21)
	    at BdsPopover.show (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/mixins/floating.mixin.ts:169:17)
	    at BdsPopover.openPopover (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/components/overlays/bds-popover/bds-popover.tsx:580:10)
	    at /Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/node_modules/.pnpm/@stencil+core@4.42.1/node_modules/@stencil/core/internal/testing/index.js:5491:83
	    at processTicksAndRejections (node:internal/process/task_queues:105:5)
	
	Node.js v22.21.1
	 ChildProcessCrashedError: Child process [pid 87191] exited unexpectedly with exit code 1 (without signal). Last part of stdout and stderr was:
	/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/services/logger/Logger.ts:24
	        throw new Error(`[${component}]: ${message}`);
	              ^
	
	Error: [AnchoredMixin.show]: triggerSlot is required
	    at Logger.error (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/services/logger/Logger.ts:28:11)
	    at BdsPopover.onBeforeShow (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/mixins/anchored.mixin.ts:158:21)
	    at BdsPopover.show (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/mixins/floating.mixin.ts:169:17)
	    at BdsPopover.openPopover (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/components/overlays/bds-popover/bds-popover.tsx:580:10)
	    at /Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/node_modules/.pnpm/@stencil+core@4.42.1/node_modules/@stencil/core/internal/testing/index.js:5491:83
	    at processTicksAndRejections (node:internal/process/task_queues:105:5)
	
	Node.js v22.21.1
	
    at ChildProcess.handleUnexpectedExit (file:///Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/node_modules/.pnpm/@stryker-mutator+core@10.0.0_@types+node@22.19.11/node_modules/@stryker-mutator/core/dist/src/child-proxy/child-process-proxy.js:180:31)
    at ChildProcess.emit (node:events:519:28)
    at maybeClose (node:internal/child_process:1101:16)
    at ChildProcess._handle.onexit (node:internal/child_process:304:5) {
  innerError: undefined,
  pid: 87191,
  exitCode: 1,
  signal: null
}
[33m23:59:45 (86829) WARN ChildProcessProxy[39m Child process [pid 97034] exited unexpectedly with exit code 1 (without signal). Last part of stdout and stderr was:
	/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/services/logger/Logger.ts:24
	        throw new Error(`[${component}]: ${message}`);
	              ^
	
	Error: [AnchoredMixin.show]: triggerSlot is required
	    at Logger.error (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/services/logger/Logger.ts:28:11)
	    at BdsPopover.onBeforeShow (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/mixins/anchored.mixin.ts:158:21)
	    at BdsPopover.show (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/mixins/floating.mixin.ts:169:17)
	    at BdsPopover.openPopover (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/components/overlays/bds-popover/bds-popover.tsx:580:10)
	    at /Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/node_modules/.pnpm/@stencil+core@4.42.1/node_modules/@stencil/core/internal/testing/index.js:5491:83
	    at processTicksAndRejections (node:internal/process/task_queues:105:5)
	
	Node.js v22.21.1
	 ChildProcessCrashedError: Child process [pid 97034] exited unexpectedly with exit code 1 (without signal). Last part of stdout and stderr was:
	/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/services/logger/Logger.ts:24
	        throw new Error(`[${component}]: ${message}`);
	              ^
	
	Error: [AnchoredMixin.show]: triggerSlot is required
	    at Logger.error (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/services/logger/Logger.ts:28:11)
	    at BdsPopover.onBeforeShow (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/mixins/anchored.mixin.ts:158:21)
	    at BdsPopover.show (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/mixins/floating.mixin.ts:169:17)
	    at BdsPopover.openPopover (/Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/.stryker-tmp/sandbox-YJuSGn/src/components/overlays/bds-popover/bds-popover.tsx:580:10)
	    at /Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/node_modules/.pnpm/@stencil+core@4.42.1/node_modules/@stencil/core/internal/testing/index.js:5491:83
	    at processTicksAndRejections (node:internal/process/task_queues:105:5)
	
	Node.js v22.21.1
	
    at ChildProcess.handleUnexpectedExit (file:///Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/node_modules/.pnpm/@stryker-mutator+core@10.0.0_@types+node@22.19.11/node_modules/@stryker-mutator/core/dist/src/child-proxy/child-process-proxy.js:180:31)
    at ChildProcess.emit (node:events:519:28)
    at maybeClose (node:internal/child_process:1101:16)
    at ChildProcess._handle.onexit (node:internal/child_process:304:5) {
  innerError: undefined,
  pid: 97034,
  exitCode: 1,
  signal: null
}
Mutation testing 46% (elapsed: ~2m, remaining: ~2m) 99/198 tested (8 survived, 0 timed out)
Mutation testing 51% (elapsed: ~2m, remaining: ~2m) 105/198 tested (8 survived, 0 timed out)
Mutation testing 56% (elapsed: ~2m, remaining: ~1m) 111/198 tested (9 survived, 0 timed out)
Mutation testing 57% (elapsed: ~2m, remaining: ~1m) 125/198 tested (10 survived, 0 timed out)
Mutation testing 58% (elapsed: ~2m, remaining: ~1m) 136/198 tested (10 survived, 0 timed out)
Mutation testing 60% (elapsed: ~3m, remaining: ~1m) 149/198 tested (13 survived, 0 timed out)
Mutation testing 65% (elapsed: ~3m, remaining: ~1m) 154/198 tested (13 survived, 0 timed out)
Mutation testing 68% (elapsed: ~3m, remaining: ~1m) 157/198 tested (13 survived, 0 timed out)
Mutation testing 71% (elapsed: ~3m, remaining: ~1m) 161/198 tested (13 survived, 0 timed out)
Mutation testing 74% (elapsed: ~3m, remaining: ~1m) 164/198 tested (13 survived, 0 timed out)
Mutation testing 77% (elapsed: ~3m, remaining: ~1m) 167/198 tested (13 survived, 0 timed out)
Mutation testing 80% (elapsed: ~4m, remaining: <1m) 172/198 tested (13 survived, 0 timed out)
Mutation testing 82% (elapsed: ~4m, remaining: <1m) 177/198 tested (13 survived, 0 timed out)
Mutation testing 85% (elapsed: ~4m, remaining: <1m) 182/198 tested (13 survived, 0 timed out)
Mutation testing 88% (elapsed: ~4m, remaining: <1m) 185/198 tested (13 survived, 0 timed out)
Mutation testing 89% (elapsed: ~4m, remaining: <1m) 187/198 tested (13 survived, 0 timed out)
Mutation testing 95% (elapsed: ~4m, remaining: <1m) 193/198 tested (13 survived, 0 timed out)
Mutation testing 97% (elapsed: ~5m, remaining: <1m) 195/198 tested (13 survived, 0 timed out)
Mutation testing 99% (elapsed: ~5m, remaining: <1m) 197/198 tested (13 survived, 0 timed out)

All tests
  bds-date-picker.a11y.spec.ts
    ✓ bds-date-picker a11y — trigger field sets aria-haspopup="true" on the field container [line 12] (killed 8)
    ~ bds-date-picker a11y — trigger field sets aria-expanded="false" on the field container before the popover opens [line 18] (covered 94)
    ~ bds-date-picker a11y — trigger field flips aria-expanded to "true" once the popover opens [line 24] (covered 103)
    ~ bds-date-picker a11y — trigger field flips aria-expanded back to "false" once the popover closes [line 33] (covered 103)
    ~ bds-date-picker a11y — footer buttons exposes the Clean/Cancel/Apply buttons as focusable, non-disabled native buttons by default [line 50] (covered 94)
    ~ bds-date-picker a11y — footer buttons labels each footer button with its own visible, screen-reader-accessible text [line 60] (covered 94)
    ~ bds-date-picker a11y — footer buttons reflects custom labels through to each footer button visible text [line 70] (covered 94)
  bds-date-picker.basics.spec.ts
    ✓ bds-date-picker basics defaults name to an empty string when not provided [line 13] (killed 2)
    ~ bds-date-picker basics renders the slotted field and the popover [line 19] (covered 94)
    ✓ bds-date-picker basics clicking the trigger field opens the popover [line 27] (killed 3)
    ~ bds-date-picker basics clicking outside the open popover closes it [line 36] (covered 103)
    ~ bds-date-picker basics pressing Escape while the popover is open closes it [line 50] (covered 103)
    ✓ bds-date-picker basics disabled prevents the popover from opening on trigger click [line 62] (killed 1)
    ✓ bds-date-picker basics warns when no bds-text-field is slotted [line 73] (killed 9)
    ✓ bds-date-picker basics warns when the slotted field carries its own name [line 83] (killed 5)
    ✓ bds-date-picker basics does not warn about the slotted field when it is valid and name-less [line 94] (killed 4)
    ✓ bds-date-picker basics pushes selectable=true onto the slotted field [line 103] (killed 2)
    ✓ bds-date-picker basics pushes the initial disabled state onto the slotted field [line 109] (killed 1)
    ✓ bds-date-picker basics pushes a disabled prop change made after mount onto the slotted field [line 117] (killed 2)
    ✓ bds-date-picker basics shows the popover arrow when hideArrow is false (default) [line 127] (killed 1)
    ✓ bds-date-picker basics hides the popover arrow when hideArrow is true [line 133] (killed 1)
    ✓ bds-date-picker basics renders the popover with a closable header and a footer [line 141] (killed 3)
    ✓ bds-date-picker basics shows headerPlaceholder in the header title when nothing is selected or committed [line 149] (killed 4)
    ~ bds-date-picker basics shows a custom headerPlaceholder when provided [line 157] (covered 94)
    ✓ bds-date-picker basics updates the header title live to the drafted date as a day is clicked, before Apply [line 167] (killed 2)
    ~ bds-date-picker basics reflects the last committed value in the header after an abandoned draft is reopened, not the abandoned draft [line 182] (covered 106)
    ~ bds-date-picker basics shows headerPlaceholder after an abandoned draft is reopened when no value was ever committed [line 202] (covered 106)
  bds-date-picker.events.spec.ts
    ✓ bds-date-picker events — draft selection clicking a day updates the visible selected cell but not the public value [line 13] (killed 18)
    ~ bds-date-picker events — draft selection clicking a day does not emit bdsChange or valueChange [line 25] (covered 97)
    ✓ bds-date-picker events — draft selection month navigation updates the displayed month without affecting the draft or value [line 41] (killed 1)
    ~ bds-date-picker events — draft selection previous month navigation moves the displayed month backward [line 65] (covered 95)
    ✓ bds-date-picker events — draft selection reopening after an abandoned draft applies the last committed value, not the abandoned selection [line 83] (killed 25)
    ~ bds-date-picker events — draft selection opens showing the committed value's own month, independent of today's date [line 108] (covered 103)
    ✓ bds-date-picker events — footer actions Apply with a selected draft day commits the value and emits bdsChange/valueChange exactly once [line 126] (killed 5)
    ✓ bds-date-picker events — footer actions Apply closes the popover [line 147] (killed 4)
    ✓ bds-date-picker events — footer actions Apply with no draft selection does not change value and does not emit [line 161] (killed 2)
    ~ bds-date-picker events — footer actions Apply with no draft selection still closes the popover [line 178] (covered 100)
    ✓ bds-date-picker events — footer actions Cancel after a day click leaves value unchanged, emits nothing, and closes the popover [line 189] (killed 3)
    ✓ bds-date-picker events — footer actions Clean clears the value to an empty string and emits bdsChange/valueChange with it [line 210] (killed 5)
    ~ bds-date-picker events — footer actions Clean closes the popover [line 231] (covered 108)
    ~ bds-date-picker events — footer actions overrides the footer button text via the labels prop [line 242] (covered 94)
    ~ bds-date-picker events — footer actions falls back to the default English labels for fields not overridden [line 253] (covered 94)
    ✓ bds-date-picker events — slotted field synchronization reflects the committed value on the slotted field's own value after Apply [line 270] (killed 3)
    ✓ bds-date-picker events — slotted field synchronization clears the slotted field's own value after Clean [line 282] (killed 2)
    ~ bds-date-picker events — slotted field synchronization reflects an external value prop mutation on the slotted field's own value [line 295] (covered 111)
    ~ bds-date-picker events — slotted field synchronization does not double-fire valueChange on the host when the slotted field's own valueChange bubbles [line 305] (covered 125)
    ✓ bds-date-picker events — slotted field synchronization the slotted field's own clear (bdsClear) commits an empty value exactly like Clean [line 320] (killed 3)
    ~ bds-date-picker events — slotted field synchronization the slotted field's own bdsClear also closes the popover, matching the footer's Clean action [line 338] (covered 127)
  bds-date-picker.form.spec.ts
    ✓ bds-date-picker — form association registers the committed value with ElementInternals under the reflected name after Apply [line 24] (killed 3)
    ✓ bds-date-picker — form association calls formAssociatedCallback registers the current value and updates validity [line 41] (killed 2)
    ✓ bds-date-picker — form association formResetCallback clears the value and any open draft state [line 53] (killed 5)
    ✓ bds-date-picker — form association formResetCallback re-validates a required field back to invalid [line 69] (killed 8)
    ✓ bds-date-picker — form association formResetCallback deregisters the value from ElementInternals [line 84] (killed 1)
    ✓ bds-date-picker — form association formStateRestoreCallback restores a string state as the value [line 96] (killed 4)
    ~ bds-date-picker — form association formStateRestoreCallback registers the restored value with ElementInternals [line 106] (covered 118)
    ✓ bds-date-picker — form association formStateRestoreCallback re-validates a required field against the restored value [line 116] (killed 4)
    ✓ bds-date-picker — form association formStateRestoreCallback falls back to an empty value for non-string state [line 128] (killed 2)
    ✓ bds-date-picker — form association formDisabledCallback(true) disables the component and pushes disabled onto the slotted field [line 140] (killed 2)
    ~ bds-date-picker — form association formDisabledCallback(false) re-enables the slotted field [line 150] (covered 96)
    ✓ bds-date-picker — form association disconnectedCallback removes its listeners from the slotted field without throwing [line 162] (killed 5)
    ✓ bds-date-picker — required field validity marks the field invalid via setValidity when required and empty [line 181] (killed 1)
    ~ bds-date-picker — required field validity marks the field valid via setValidity when required and a value is committed [line 196] (covered 111)
    ✓ bds-date-picker — required field validity re-validates when the required prop changes after mount [line 208] (killed 3)
    ✓ bds-date-picker — required field validity re-validates when the committed value changes after mount [line 222] (killed 1)
    ✓ bds-date-picker — required field validity delegates checkValidity to ElementInternals [line 235] (killed 1)
    ✓ bds-date-picker — required field validity delegates reportValidity to ElementInternals [line 245] (killed 1)
  bds-date-picker.keyboard.spec.ts
    ✓ bds-date-picker keyboard keeps the trigger field input in the Tab order (not tabindex="-1") [line 12] (killed 1)
    ~ bds-date-picker keyboard marks the field input readOnly while remaining tab-reachable, since selectable pushes readOnly without pushing tabindex=-1 [line 20] (covered 94)
    ✓ bds-date-picker keyboard pressing Enter on the trigger field opens the popover [line 29] (killed 9)
    ✓ bds-date-picker keyboard pressing Space on the trigger field opens the popover [line 38] (killed 3)
    ~ bds-date-picker keyboard pressing Enter or Space on the field container (where the real input lives) also opens the popover [line 47] (covered 113)
    ✓ bds-date-picker keyboard prevents the default action when Enter opens the popover, so the field does not also submit a form [line 56] (killed 1)
    ✓ bds-date-picker keyboard pressing a key other than Enter/Space on the trigger field does not open the popover [line 66] (killed 1)
    ~ bds-date-picker keyboard pressing Escape while the popover is open still closes it, independent of the managed-mode KeyboardController gap [line 75] (covered 103)
  bds-date-picker.variants.spec.ts
    ✓ bds-date-picker variants — format formats the trigger field display using a custom format string [line 37] (killed 3)
    ~ bds-date-picker variants — format does not change the public value when the format prop changes [line 45] (covered 94)
    ~ bds-date-picker variants — format falls back to the default yyyy/MM/dd format when none is provided [line 53] (covered 94)
    ~ bds-date-picker variants — locale formats a month-name-bearing display format with the provided locale [line 67] (covered 94)
    ~ bds-date-picker variants — locale uses English month names by default when no locale is provided [line 73] (covered 94)
    ~ bds-date-picker variants — locale renders locale-correct month names in the calendar grid header [line 81] (covered 94)
    ✓ bds-date-picker variants — locale passes locale through to the calendar grid's own week-start convention, not just its labels [line 93] (killed 2)
    ~ bds-date-picker variants — disabled prevents the popover from opening when disabled [line 109] (covered 103)
    ~ bds-date-picker variants — disabled disables the slotted trigger field [line 120] (covered 94)
    ~ bds-date-picker variants — disabled disables all three footer buttons [line 128] (covered 94)
    ~ bds-date-picker variants — disabled passes disabled through to the popover so it cannot be shown programmatically either [line 140] (covered 94)

[Survived] BooleanLiteral
src/components/forms/bds-date-picker/bds-date-picker/bds-date-picker.tsx:95:38
-     @State() popoverVisible: boolean = false;
+     @State() popoverVisible: boolean = true;
Tests ran:
    bds-date-picker events — draft selection clicking a day updates the visible selected cell but not the public value
    bds-date-picker events — draft selection clicking a day does not emit bdsChange or valueChange
    bds-date-picker events — draft selection month navigation updates the displayed month without affecting the draft or value
  and 82 more tests!


[Survived] BooleanLiteral
src/components/forms/bds-date-picker/bds-date-picker/bds-date-picker.tsx:104:42
-     @State() private isDisabled: boolean = false;
+     @State() private isDisabled: boolean = true;
Tests ran:
    bds-date-picker events — draft selection clicking a day updates the visible selected cell but not the public value
    bds-date-picker events — draft selection clicking a day does not emit bdsChange or valueChange
    bds-date-picker events — draft selection month navigation updates the displayed month without affecting the draft or value
  and 82 more tests!


[Survived] OptionalChaining
src/components/forms/bds-date-picker/bds-date-picker/bds-date-picker.tsx:130:12
-         void this.bdsPopover?.setListenElement(inputContainer);
+         void this.bdsPopover.setListenElement(inputContainer);
Tests ran:
    bds-date-picker events — draft selection clicking a day updates the visible selected cell but not the public value
    bds-date-picker events — draft selection clicking a day does not emit bdsChange or valueChange
    bds-date-picker events — draft selection month navigation updates the displayed month without affecting the draft or value
  and 81 more tests!


[Survived] OptionalChaining
src/components/forms/bds-date-picker/bds-date-picker/bds-date-picker.tsx:131:12
-         void this.bdsPopover?.setAnchorElement(inputContainer);
+         void this.bdsPopover.setAnchorElement(inputContainer);
Tests ran:
    bds-date-picker events — draft selection clicking a day updates the visible selected cell but not the public value
    bds-date-picker events — draft selection clicking a day does not emit bdsChange or valueChange
    bds-date-picker events — draft selection month navigation updates the displayed month without affecting the draft or value
  and 81 more tests!


[Survived] CallExpression
src/components/forms/bds-date-picker/bds-date-picker/bds-date-picker.tsx:194:5
-       this.updateValidity();
+       ;
Tests ran:
    bds-date-picker — form association formResetCallback clears the value and any open draft state
    bds-date-picker — form association formResetCallback re-validates a required field back to invalid
    bds-date-picker — form association formResetCallback deregisters the value from ElementInternals


[Survived] CallExpression
src/components/forms/bds-date-picker/bds-date-picker/bds-date-picker.tsx:199:5
-       setFormValue(this.internals, this.value);
+       ;
Tests ran:
    bds-date-picker — form association formStateRestoreCallback restores a string state as the value
    bds-date-picker — form association formStateRestoreCallback registers the restored value with ElementInternals
    bds-date-picker — form association formStateRestoreCallback re-validates a required field against the restored value
  and 1 more test!


[Survived] CallExpression
src/components/forms/bds-date-picker/bds-date-picker/bds-date-picker.tsx:200:5
-       this.updateValidity();
+       ;
Tests ran:
    bds-date-picker — form association formStateRestoreCallback restores a string state as the value
    bds-date-picker — form association formStateRestoreCallback registers the restored value with ElementInternals
    bds-date-picker — form association formStateRestoreCallback re-validates a required field against the restored value
  and 1 more test!


[Survived] ConditionalExpression
src/components/forms/bds-date-picker/bds-date-picker/bds-date-picker.tsx:229:9
-       if (this.el !== null) {
+       if (true) {
Tests ran:
    bds-date-picker events — draft selection clicking a day updates the visible selected cell but not the public value
    bds-date-picker events — draft selection clicking a day does not emit bdsChange or valueChange
    bds-date-picker events — draft selection month navigation updates the displayed month without affecting the draft or value
  and 82 more tests!


[Survived] ConditionalExpression
src/components/forms/bds-date-picker/bds-date-picker/bds-date-picker.tsx:243:9
-       if (this.el !== null) {
+       if (true) {
Tests ran:
    bds-date-picker events — draft selection clicking a day updates the visible selected cell but not the public value
    bds-date-picker events — draft selection clicking a day does not emit bdsChange or valueChange
    bds-date-picker events — draft selection month navigation updates the displayed month without affecting the draft or value
  and 81 more tests!


[Survived] OptionalChaining
src/components/forms/bds-date-picker/bds-date-picker/bds-date-picker.tsx:254:10
-       void this.bdsPopover?.openPopover();
+       void this.bdsPopover.openPopover();
Tests ran:
    bds-date-picker events — draft selection reopening after an abandoned draft applies the last committed value, not the abandoned selection
    bds-date-picker events — draft selection opens showing the committed value's own month, independent of today's date
    bds-date-picker basics clicking the trigger field opens the popover
  and 15 more tests!


[Survived] OptionalChaining
src/components/forms/bds-date-picker/bds-date-picker/bds-date-picker.tsx:298:14
-           void this.bdsPopover?.closePopover();
+           void this.bdsPopover.closePopover();
Tests ran:
    bds-date-picker events — draft selection reopening after an abandoned draft applies the last committed value, not the abandoned selection
    bds-date-picker events — footer actions Apply with a selected draft day commits the value and emits bdsChange/valueChange exactly once
    bds-date-picker events — footer actions Apply closes the popover
  and 5 more tests!


[Survived] OptionalChaining
src/components/forms/bds-date-picker/bds-date-picker/bds-date-picker.tsx:302:14
-           void this.bdsPopover?.closePopover();
+           void this.bdsPopover.closePopover();
Tests ran:
    bds-date-picker events — footer actions Cancel after a day click leaves value unchanged, emits nothing, and closes the popover


[Survived] OptionalChaining
src/components/forms/bds-date-picker/bds-date-picker/bds-date-picker.tsx:307:14
-           void this.bdsPopover?.closePopover();
+           void this.bdsPopover.closePopover();
Tests ran:
    bds-date-picker events — footer actions Clean clears the value to an empty string and emits bdsChange/valueChange with it
    bds-date-picker events — footer actions Clean closes the popover
    bds-date-picker events — slotted field synchronization clears the slotted field's own value after Clean
  and 2 more tests!


Ran 45.16 tests per mutant on average.
--------------------------|------------------|----------|-----------|------------|----------|----------|
                          | % Mutation score |          |           |            |          |          |
File                      |  total | covered | # killed | # timeout | # survived | # no cov | # errors |
--------------------------|--------|---------|----------|-----------|------------|----------|----------|
All files                 |  93.33 |   93.33 |      182 |         0 |         13 |        0 |        3 |
 helpers                  | 100.00 |  100.00 |        8 |         0 |          0 |        0 |        0 |
  renderCalendarPanel.tsx | 100.00 |  100.00 |        2 |         0 |          0 |        0 |        0 |
  renderFooter.tsx        | 100.00 |  100.00 |        6 |         0 |          0 |        0 |        0 |
 utils                    | 100.00 |  100.00 |       28 |         0 |          0 |        0 |        0 |
  constants.ts            | 100.00 |  100.00 |        4 |         0 |          0 |        0 |        0 |
  draft-state.ts          | 100.00 |  100.00 |        9 |         0 |          0 |        0 |        0 |
  value-mapping.ts        | 100.00 |  100.00 |       15 |         0 |          0 |        0 |        0 |
 bds-date-picker.tsx      |  91.82 |   91.82 |      146 |         0 |         13 |        0 |        3 |
--------------------------|--------|---------|----------|-----------|------------|----------|----------|
[32m00:02:52 (86829) INFO HtmlReporter[39m Your report can be found at: file:///Users/dgonzalez/projects/src/boreal-ds/.worktrees/date-picker-mutation/packages/boreal-web-components/reports/mutation/mutation.html
[32m00:02:52 (86829) INFO MutationTestExecutor[39m Done in 5 minutes and 20 seconds.
