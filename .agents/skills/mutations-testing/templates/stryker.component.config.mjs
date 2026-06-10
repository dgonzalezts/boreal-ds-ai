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
};
