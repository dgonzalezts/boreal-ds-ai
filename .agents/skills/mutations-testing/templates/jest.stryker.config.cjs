const { getJestPreset } = require("@stencil/core/testing");

const { testRegex: _dropped, ...preset } = getJestPreset();

module.exports = {
  ...preset,
  moduleNameMapper: {
    ...preset.moduleNameMapper,
    "^@/(.*)$": "<rootDir>/src/$1",
    "@utils/test": "<rootDir>/src/utils/__test__",
  },
  // TODO: update to the target component's __test__ directory
  testMatch: [
    "<rootDir>/src/components/<category>/<component>/__test__/**/*.spec.tsx",
  ],
  // Prevents each Stryker worker from also parallelizing internally, which multiplies
  // total process count far past Stryker's own concurrency cap. Pair with
  // `concurrency: 2` in stryker.component.config.mjs.
  maxWorkers: 1,
};
