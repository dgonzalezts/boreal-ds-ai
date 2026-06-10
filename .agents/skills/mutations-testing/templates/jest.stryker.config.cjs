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
};
