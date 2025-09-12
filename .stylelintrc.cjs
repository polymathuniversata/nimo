/**
 * Stylelint configuration for Nimo Frontend
 * Enforces design token usage (spacing, colors) and discourages raw pixel values.
 */
module.exports = {
  extends: [
    'stylelint-config-standard-scss',
    'stylelint-config-recommended-vue'
  ],
  plugins: [
    'stylelint-declaration-use-variable'
  ],
  rules: {
    // Require variables for color, font-size, z-index where practical
    'sh-waqar/declaration-use-variable': [
      ['/color/', 'font-size', 'z-index', {
        ignoreValues: ['transparent', 'inherit', 'currentColor']
      }]
    ],
    // Disallow raw pixel spacing (margin/padding) to encourage tokens
    'declaration-property-value-disallowed-list': {
      '/^(margin|padding|gap|inset|top|right|bottom|left)$/': [/\\d+px/]
    },
    // Allow small pixel borders & shadows
    'unit-disallowed-list': [
      // Disallow px except where explicitly ignored by property-specific rule above
      // We'll allow px globally but enforce via property value disallowed list
    ],
    'color-named': 'never',
    'no-empty-source': null,
    'scss/dollar-variable-pattern': '^[a-z0-9\-]+$',
    'scss/at-function-pattern': '^[a-z0-9\-]+$',
    'scss/at-mixin-pattern': '^[a-z0-9\-]+$'
  },
  overrides: [
    {
      files: ['**/*.vue'],
      customSyntax: 'postcss-html'
    }
  ]
};
