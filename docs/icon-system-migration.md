# Nimo Icon System Migration Guide

## Overview

This document outlines the progressive migration from Material Design icons to custom Nimo SVG icons for better branding, performance, and visual consistency.

## Architecture

### Components

1. **NimoIcon.vue** - Smart icon component that automatically chooses between custom SVGs and Material Design fallbacks
2. **useCustomIcons.ts** - Composable managing icon mappings and replacement logic
3. **Custom SVG Assets** - Hand-crafted SVG icons in `/src/assets/icons/`

### Migration Strategy

**Phase 1: High Priority Icons** ✅ **IN PROGRESS**
- Navigation icons (menu, home, settings)
- Financial icons (wallet, send, savings) 
- Action icons (refresh, edit, check)
- Social icons (star, thumbs-up, comment)

**Phase 2: Medium Priority Icons**
- Communication icons (help, info, warning, error)
- Navigation arrows and chevrons
- Basic action icons (plus, minus, copy)

**Phase 3: Low Priority Icons**
- Specialized domain icons (keep Material Design for now)
- Less frequently used interface elements

## Implementation Progress

### ✅ Completed

**Custom SVG Icons Created:**
- `menu.svg` - Hamburger menu icon
- `home.svg` - House icon for navigation
- `settings.svg` - Gear icon for preferences
- `wallet.svg` - Wallet icon for financial features
- `refresh.svg` - Refresh/reload icon
- `edit.svg` - Pencil edit icon
- `check.svg` - Checkmark icon
- `check-circle.svg` - Checkmark in circle
- `star.svg` - Star rating icon
- `send.svg` - Send/transfer icon
- `savings.svg` - Savings/deposit icon
- `thumbs-up.svg` - Like/approval icon
- `comment.svg` - Comment/chat icon

**Infrastructure:**
- `NimoIcon.vue` component with intelligent fallback
- `useCustomIcons.ts` mapping system
- Icon categorization and priority system

**Component Updates:**
- `MainLayout.vue` - Updated menu, home, and settings icons to use NimoIcon

### 🔄 In Progress

**Icon Replacement:**
- Converting remaining high-priority icons in components
- Testing icon display across different themes
- Ensuring accessibility compliance

### 📋 Next Steps

1. **Finish High Priority Icons**
   - Update all high-priority icon usages in components
   - Test icon performance and visual consistency
   - Validate accessibility with screen readers

2. **Create Medium Priority Icons**
   - Design and implement medium-priority SVG icons
   - Update icon mappings in useCustomIcons.ts
   - Test fallback behavior

3. **Performance Optimization**
   - Implement icon bundling/sprites for better loading
   - Add icon preloading for critical icons
   - Measure bundle size impact

## Usage

### Basic Usage

```vue
<template>
  <!-- Automatically uses custom SVG if available, falls back to Material Design -->
  <NimoIcon name="home" size="24px" color="primary" />
  
  <!-- Force Material Design usage -->
  <NimoIcon name="home" :use-custom="false" />
  
  <!-- Standard Quasar icon (unchanged) -->
  <q-icon name="home" />
</template>
```

### Icon Mapping

```typescript
// Check if custom icon exists
import { hasCustomIcon, getCustomIcon } from '@/composables/useCustomIcons';

const hasCustom = hasCustomIcon('home'); // true
const customName = getCustomIcon('home'); // 'home'
```

### Component Registration

The `NimoIcon` component should be globally registered or imported where needed:

```typescript
// In main.ts or component
import NimoIcon from '@/components/NimoIcon.vue';
```

## Development Guidelines

### Creating New Icons

1. **Design Principles:**
   - 24x24px base size for scalability
   - 2px stroke width for consistency
   - Use `currentColor` for theming support
   - Minimal, clean design matching cosmic theme

2. **File Naming:**
   - Use kebab-case: `check-circle.svg`
   - Descriptive names: `thumbs-up.svg` not `like.svg`
   - Match Material Design names where applicable

3. **SVG Standards:**
   - Include `viewBox="0 0 24 24"`
   - Use `stroke="currentColor"` and `fill="none"`
   - Add `stroke-linecap="round"` for smooth lines
   - Optimize for accessibility

### Testing Icons

1. **Visual Testing:**
   - Test in light and dark themes
   - Verify scaling at different sizes
   - Check alignment with text

2. **Accessibility Testing:**
   - Screen reader compatibility
   - High contrast mode support
   - Keyboard navigation focus

3. **Performance Testing:**
   - Bundle size impact
   - Loading performance
   - Icon switching smoothness

## Icon Categories

### Navigation (High Priority)
- `menu` - Main navigation toggle
- `home` - Home/dashboard navigation
- `settings` - Settings/preferences
- `arrow-*` - Directional navigation
- `chevron-*` - Dropdown/expansion indicators

### Financial (High Priority)
- `wallet` - Wallet/account management
- `send` - Transfer/send money
- `savings` - Deposits/savings
- `tokens` - Token management

### Actions (High Priority)
- `refresh` - Reload/refresh actions
- `edit` - Edit/modify content
- `check` - Confirmation/success
- `check-circle` - Completed states

### Social (High Priority)
- `star` - Ratings/favorites
- `thumbs-up` - Likes/approval
- `comment` - Comments/discussions

### Communication (Medium Priority)
- `help` - Help/support
- `info` - Information/details
- `warning` - Warnings/alerts
- `error` - Error states

## Migration Checklist

### Per Component
- [ ] Identify all icon usages (`q-icon`, `icon=` props)
- [ ] Replace high-priority icons with `NimoIcon`
- [ ] Test visual appearance and functionality
- [ ] Validate accessibility compliance
- [ ] Update component documentation

### Per Icon
- [ ] Design custom SVG following guidelines
- [ ] Add to `/src/assets/icons/`
- [ ] Update `useCustomIcons.ts` mapping
- [ ] Test in `NimoIcon` component
- [ ] Document usage examples

## Performance Considerations

### Bundle Size
- Custom SVGs are tree-shakeable (only used icons are bundled)
- Material Design icons come as part of Quasar bundle
- Monitor bundle size growth with each icon addition

### Loading Performance
- SVG icons load faster than icon fonts
- Consider icon sprites for heavy usage
- Implement critical icon preloading

### Runtime Performance
- Icon switching is component-level (no global re-renders)
- Caching implemented for repeated icon usage
- Minimal JavaScript overhead

## Rollback Strategy

If issues arise, components can quickly revert to Material Design icons:

```vue
<!-- Quick rollback by disabling custom icons -->
<NimoIcon name="home" :use-custom="false" />

<!-- Or revert to standard Quasar icons -->
<q-icon name="home" />
```

The system is designed for incremental adoption and easy rollback if needed.