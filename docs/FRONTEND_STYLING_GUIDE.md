# Frontend Styling Guide

This guide documents the Nimo frontend design system implementation and how to use tokens consistently across Vue (Quasar) components.

## Philosophy
We maintain a dual-token system:
- **SASS Tokens** in `src/css/quasar.variables.scss` used inside `<style lang="scss">` blocks for advanced component styling.
- **CSS Custom Properties & Utility Classes** in `src/styles/design-tokens.scss` and `src/styles/utilities.scss` used directly in templates and for global theming (supports dark mode & runtime theme adjustments).

Always prefer existing utility classes or CSS custom properties before introducing bespoke values. If a new scale step is required, add it to BOTH SASS tokens and CSS custom properties to keep parity.

## Spacing Scale
Primary spacing is an enhanced 4/8px fluid scale. Available SASS variables (clamp-based for responsive scaling):
```
$space-1  : clamp(0.25rem, 0.2rem + 0.25vw, 0.5rem);   // 4px → 8px
$space-2  : clamp(0.5rem, 0.4rem + 0.5vw, 1rem);       // 8px → 16px
$space-3  : clamp(0.75rem, 0.6rem + 0.75vw, 1.5rem);   // 12px → 24px
$space-4  : clamp(1rem, 0.8rem + 1vw, 2rem);           // 16px → 32px
$space-5  : clamp(1.25rem, 1rem + 1.25vw, 2.5rem);     // 20px → 40px
$space-6  : clamp(1.5rem, 1.2rem + 1.5vw, 3rem);       // 24px → 48px
$space-7  : clamp(1.75rem, 1.4rem + 1.75vw, 3.5rem);   // 28px → 56px (NEW - added for tablet padding parity)
$space-8  : clamp(2rem, 1.6rem + 2vw, 4rem);           // 32px → 64px
$space-10 : clamp(2.5rem, 2rem + 2.5vw, 5rem);         // 40px → 80px
$space-12 : clamp(3rem, 2.4rem + 3vw, 6rem);           // 48px → 96px
$space-16 : clamp(4rem, 3.2rem + 4vw, 8rem);           // 64px → 128px
$space-20 : clamp(5rem, 4rem + 5vw, 10rem);            // 80px → 160px
$space-24 : clamp(6rem, 4.8rem + 6vw, 12rem);          // 96px → 192px
$space-32 : clamp(8rem, 6.4rem + 8vw, 16rem);          // 128px → 256px
```

CSS Custom Property equivalents (fixed scale) live in `design-tokens.scss`:
```
--nimo-space-1: 0.25rem;   /* 4px */
--nimo-space-2: 0.5rem;    /* 8px */
--nimo-space-3: 0.75rem;   /* 12px */
--nimo-space-4: 1rem;      /* 16px */
--nimo-space-5: 1.25rem;   /* 20px */
--nimo-space-6: 1.5rem;    /* 24px */
--nimo-space-7: 1.75rem;   /* 28px */
--nimo-space-8: 2rem;      /* 32px */
... (continues)
```

### When to Use Which
- **Component SCSS (scoped)**: Use `$space-*` variables for responsive fluid spacing.
- **Template utility classes**: Use `.nimo-p-4`, `.nimo-mb-6`, etc., from `utilities.scss`.
- **Inline style bindings / JS-calculated spacing**: Prefer CSS vars: `style="padding: var(--nimo-space-6)"`.

### Adding a New Step
1. Add `$space-X` in `quasar.variables.scss` maintaining clamp progression.
2. Add `--nimo-space-X` in `design-tokens.scss` (fixed base value).
3. (Optional) Add utility classes if needed (`utilities.scss`).
4. Document it here with rationale.

## Breakpoints
Breakpoints exist in both SASS (`$breakpoint-md`) and CSS (`--nimo-breakpoint-md`). Keep naming consistent for readability. Use mobile-first media queries.

## Color & Gradients
Use semantic tokens (`$primary`, `$accent`, `$positive`) and avoid hard-coded hex values inside components unless generating dynamic gradients. For text or backgrounds in templates, use utility classes or CSS variables if available.

## Elevation & Shadows
Use `$shadow-*` tokens or `var(--nimo-shadow-*)`. Avoid mixing custom box-shadows unless part of a new pattern—then create a token.

## Motion & Accessibility
- Respect `prefers-reduced-motion` (already handled in components; keep patterns consistent).
- Limit large-scale animations to <800ms.

## Common Patterns
| Pattern | Recommended Approach |
|---------|---------------------|
| Card internal padding | `$space-6` desktop, `$space-4` mobile, `$space-7` tablet (if needed for layout breathing room) |
| Section vertical spacing | `$space-20` or `var(--nimo-space-section)` |
| Badge / micro element gap | `$space-1` or `$space-2` |
| Icon + label gap | `$space-2` |

## Recent Change Log
- 2025-09-07: Added `$space-7` to align SCSS with existing CSS custom property `--nimo-space-7` and fix build error in `StellarFeatureCard.vue`.
- 2025-09-07: Introduced `$space-scale` map, `space($n)` helper, and `@mixin padding()/margin()` utilities.
- 2025-09-07: Added Stylelint rules to discourage raw pixel spacing usage.
- 2025-09-07: Added Storybook story `Design Tokens/Spacing Scale` for visual QA.

## Linting & Consistency Tips
- Search for raw `padding:` / `margin:` values like `16px` and replace with tokens.
- Avoid mixing `$space-*` and `var(--nimo-space-*)` in a single rule unless absolutely necessary.

## Future Enhancements
- Potentially add negative spacing tokens via helper if needed in layout algorithms.
- Add dark-mode adaptive elevation tokens.

## SCSS Helper & Mixins
We now expose a programmatic API for spacing:
```
$space-scale: (1: $space-1, 2: $space-2, 3: $space-3, 4: $space-4, 5: $space-5, 6: $space-6, 7: $space-7, 8: $space-8, 10: $space-10, 12: $space-12, 16: $space-16, 20: $space-20, 24: $space-24, 32: $space-32);
@function space($n) { @return map-get($space-scale, $n); }
```
Use:
```
.example { padding: space(6); }
.example-alt { @include padding(4 6); }
```
The `@mixin padding()` and `@mixin margin()` accept either one value or up to four numeric keys matching the scale.

## Lint Rules (Stylelint)
Configured in `.stylelintrc.cjs`:
- Disallows raw `px` usage in margin/padding/gap/inset-related properties via `declaration-property-value-disallowed-list`.
- Encourages use of SASS variables for color, font-size, z-index with `stylelint-declaration-use-variable` plugin.

Run manually (after installing new devDependencies):
```
npm install --save-dev stylelint stylelint-config-standard-scss stylelint-config-recommended-vue stylelint-declaration-use-variable postcss-html
npx stylelint "src/**/*.{vue,scss,css}" --fix
```
Suggested script addition (if not already present): `"lint:styles": "stylelint \"src/**/*.{vue,scss,css}\" --fix"`.

## Storybook Spacing Visualization
Story file: `src/stories/SpacingScale.stories.ts`.
Purpose: Visual regression & education for spacing tokens. Each row maps `space-n` to its CSS var and renders a gradient block whose height equals the token.
Run Storybook:
```
npm run storybook
```
Use this when proposing additions to ensure visual rhythm consistency.

## Canonical Source & Mapping
The definitive token inventory (spacing, radius, motion, color semantic mapping) now lives in `docs/design-system.md`. This guide focuses on HOW to apply them. When adding or renaming a token:
1. Update `design-system.md` (canonical values & rationale)
2. Update `quasar.variables.scss` (SASS variables / maps)
3. Update `design-tokens.scss` (CSS custom properties)
4. Update this guide ONLY if usage patterns change

### SCSS ↔ CSS Token Mapping (Excerpt)
| Purpose | SCSS Variable | CSS Custom Property | Utility Class Example |
|---------|---------------|---------------------|-----------------------|
| Spacing 16px base | `$space-4` | `--nimo-space-4` | `.nimo-p-4` |
| Spacing 28px base | `$space-7` | `--nimo-space-7` | `.nimo-mb-7` (if generated) |
| Section vertical | `$space-20` | `--nimo-space-20` | `.nimo-py-20` |
| Radius sm | `$radius-sm` | `--nimo-radius-sm` | (apply via class `.radius-sm` if added) |
| Transition fast | `$transition-fast` | `--nimo-transition-fast` | N/A (used in SCSS) |

For the complete, versioned mapping see `design-system.md`.

## Drift Prevention Checklist
Before merging a PR that touches styles:
- [ ] No raw pixel spacing added without justification
- [ ] If a new scale step was added it appears in BOTH SASS + CSS vars
- [ ] `design-system.md` updated first (Docs First)
- [ ] Storybook spacing story still renders correctly
- [ ] Stylelint passes (`npm run lint:styles`)

---
Last extended: 2025-09-07 (Added canonical reference + mapping excerpt)
