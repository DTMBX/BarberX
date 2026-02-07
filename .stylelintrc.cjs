module.exports = {
  extends: 'stylelint-config-standard',
  rules: {
    'at-rule-no-unknown': [true, {
      ignoreAtRules: ['tailwind', 'apply', 'variants', 'responsive', 'screen', 'layer']
    }],
    'declaration-block-single-line-max-declarations': null,
    'import-notation': null,
    'value-keyword-case': null
  },
  ignoreFiles: ['**/node_modules/**', '_site/**']
};
