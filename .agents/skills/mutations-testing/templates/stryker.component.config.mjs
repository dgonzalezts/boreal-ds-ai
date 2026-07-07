/** @type {import('@stryker-mutator/api/core').PartialStrykerOptions} */
export default {
  packageManager: "pnpm",
  reporters: ["html", "clear-text", "progress"],
  testRunner: "jest",
  plugins: ["@stryker-mutator/jest-runner"],
  jest: {
    projectType: "custom",
    configFile: "jest.stryker.config.cjs",
    enableFindRelatedTests: true,
  },
  // TODO: update to the target component(s)
  mutate: ["src/components/<category>/<component>/<component>.tsx"],
  coverageAnalysis: "perTest",
  timeoutMS: 30000,
  // Caps parallel Jest instances Stryker spawns. Without this, Stryker defaults to
  // ~(CPUs - 1) workers, each booting a full Jest+ts-jest process — verified to OOM
  // an 11-CPU/18GB machine (10 workers spawned, machine ran out of memory before
  // completion; timeouts reported for otherwise-fast mutants were OOM artifacts, not
  // real slowness). Raise only if the machine has memory to spare.
  concurrency: 2,
};
