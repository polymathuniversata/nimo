# Nimo Design System

## Overview

The Nimo Design System provides a comprehensive set of design tokens, components, and guidelines for building consistent, accessible, and scalable user interfaces across the Nimo platform.

**Philosophy:** Cosmic elegance meets functional clarity - every element should feel both otherworldly and intuitive.

---

## 1. Design Tokens

### Colors

#### Primary Palette
```css
--nimo-primary: #6366f1;      /* Indigo - Main brand color */
--nimo-primary-50: #eef2ff;
--nimo-primary-100: #e0e7ff;
--nimo-primary-200: #c7d2fe;
--nimo-primary-300: #a5b4fc;
--nimo-primary-400: #818cf8;
--nimo-primary-500: #6366f1;   /* Base */
--nimo-primary-600: #4f46e5;
--nimo-primary-700: #4338ca;
--nimo-primary-800: #3730a3;
--nimo-primary-900: #312e81;
```

#### Secondary Palette
```css
--nimo-secondary: #8b5cf6;    /* Purple - Accents */
--nimo-secondary-50: #faf5ff;
--nimo-secondary-100: #f3e8ff;
--nimo-secondary-200: #e9d5ff;
--nimo-secondary-300: #d8b4fe;
--nimo-secondary-400: #c084fc;
--nimo-secondary-500: #8b5cf6; /* Base */
--nimo-secondary-600: #7c3aed;
--nimo-secondary-700: #6d28d9;
--nimo-secondary-800: #5b21b6;
--nimo-secondary-900: #4c1d95;
```

#### Accent Colors
```css
--nimo-accent: #06b6d4;       /* Cyan - CTAs */
--nimo-positive: #10b981;     /* Emerald - Success */
--nimo-negative: #ef4444;     /* Red - Error */
--nimo-warning: #f59e0b;      /* Amber - Warning */
--nimo-info: #3b82f6;         /* Blue - Info */
```

#### Neutral Palette
```css
/* Light Theme */
--nimo-grey-50: #f8fafc;
--nimo-grey-100: #f1f5f9;
--nimo-grey-200: #e2e8f0;
--nimo-grey-300: #cbd5e1;
--nimo-grey-400: #94a3b8;
--nimo-grey-500: #64748b;
--nimo-grey-600: #475569;
--nimo-grey-700: #334155;
--nimo-grey-800: #1e293b;
--nimo-grey-900: #0f172a;

/* Dark Theme (Cosmic) */
--nimo-cosmic-900: #0c0c0f;   /* Deep space */
--nimo-cosmic-800: #161622;   /* Dark nebula */
--nimo-cosmic-700: #1f1f2e;   /* Space blue */
--nimo-cosmic-600: #2a2a3e;   /* Stellar surface */
--nimo-cosmic-500: #3a3a54;   /* Asteroid belt */
--nimo-cosmic-400: #4a4a6a;   /* Distant planet */
--nimo-cosmic-300: #6a6a8a;   /* Galaxy arm */
--nimo-cosmic-200: #8a8aaa;   /* Nebula light */
--nimo-cosmic-100: #aaaacc;   /* Star cluster */
--nimo-cosmic-50: #ccccee;    /* Bright star */
```

### Typography

#### Font Families
```css
--nimo-font-primary: 'Space Grotesk', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--nimo-font-secondary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--nimo-font-mono: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
```

#### Font Scales
```css
/* Headings */
--nimo-text-h1: clamp(2.5rem, 5vw, 4rem);      /* 40-64px */
--nimo-text-h2: clamp(2rem, 4vw, 3rem);        /* 32-48px */
--nimo-text-h3: clamp(1.75rem, 3vw, 2.25rem);  /* 28-36px */
--nimo-text-h4: clamp(1.5rem, 2.5vw, 2rem);    /* 24-32px */
--nimo-text-h5: clamp(1.25rem, 2vw, 1.5rem);   /* 20-24px */
--nimo-text-h6: clamp(1.125rem, 1.5vw, 1.25rem); /* 18-20px */

/* Body Text */
--nimo-text-body1: 1rem;       /* 16px */
--nimo-text-body2: 0.875rem;   /* 14px */
--nimo-text-caption: 0.75rem;  /* 12px */
--nimo-text-overline: 0.625rem; /* 10px */

/* Font Weights */
--nimo-weight-light: 300;
--nimo-weight-regular: 400;
--nimo-weight-medium: 500;
--nimo-weight-semibold: 600;
--nimo-weight-bold: 700;
--nimo-weight-extrabold: 800;
```

#### Line Heights
```css
--nimo-leading-tight: 1.25;
--nimo-leading-normal: 1.5;
--nimo-leading-relaxed: 1.75;
--nimo-leading-loose: 2;
```

### Spacing

#### Scale (8pt Grid System)
```css
--nimo-space-0: 0;
--nimo-space-1: 0.25rem;    /* 4px */
--nimo-space-2: 0.5rem;     /* 8px */
--nimo-space-3: 0.75rem;    /* 12px */
--nimo-space-4: 1rem;       /* 16px */
--nimo-space-5: 1.25rem;    /* 20px */
--nimo-space-6: 1.5rem;     /* 24px */
--nimo-space-7: 1.75rem;    /* 28px (added; existed in CSS tokens but missing here) */
--nimo-space-8: 2rem;       /* 32px */
--nimo-space-10: 2.5rem;    /* 40px */
--nimo-space-12: 3rem;      /* 48px */
--nimo-space-16: 4rem;      /* 64px */
--nimo-space-20: 5rem;      /* 80px */
--nimo-space-24: 6rem;      /* 96px */
--nimo-space-32: 8rem;      /* 128px */
```

#### SCSS Fluid Spacing (Authoring Layer)
The SCSS layer uses fluid clamp-based tokens (`$space-1` ... `$space-32`) defined in `src/css/quasar.variables.scss`. These scale responsively; CSS custom properties are fixed anchors for runtime stability. Example mapping:
```
$space-6  -> fluid 24→48px (clamp)    | --nimo-space-6 1.5rem (24px base)
$space-7  -> fluid 28→56px (clamp)    | --nimo-space-7 1.75rem (28px)
$space-8  -> fluid 32→64px (clamp)    | --nimo-space-8 2rem (32px)
```
Use `$space-*` inside component SCSS; use `var(--nimo-space-*)` in templates, utilities, Storybook, or inline styles.

#### Component Spacing
```css
--nimo-component-padding-sm: var(--nimo-space-3);
--nimo-component-padding-md: var(--nimo-space-4);
--nimo-component-padding-lg: var(--nimo-space-6);
--nimo-component-margin-sm: var(--nimo-space-2);
--nimo-component-margin-md: var(--nimo-space-4);
--nimo-component-margin-lg: var(--nimo-space-8);
```

### Border Radius
```css
--nimo-radius-none: 0;
--nimo-radius-sm: 0.125rem;   /* 2px (align with $radius-sm) */
--nimo-radius-base: 0.375rem; /* 6px (matches $radius-base) */
--nimo-radius-md: 0.5rem;     /* 8px */
--nimo-radius-lg: 0.75rem;    /* 12px */
--nimo-radius-xl: 1rem;       /* 16px */
--nimo-radius-2xl: 1.5rem;    /* 24px */
--nimo-radius-full: 9999px;   /* Pill */
```

Radius naming alignment: The SCSS system differentiates `$radius-base` and `$radius-md`; CSS variables now reflect both (`--nimo-radius-base`, `--nimo-radius-md`). Prefer semantic aliasing (e.g., cards use `--nimo-radius-lg`).

### Shadows
```css
--nimo-shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--nimo-shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
--nimo-shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
--nimo-shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
--nimo-shadow-glow: 0 0 20px rgba(99, 102, 241, 0.3);
--nimo-shadow-cosmic: 0 8px 32px rgba(99, 102, 241, 0.2), 0 4px 16px rgba(139, 92, 246, 0.15);
```

### Transitions
```css
--nimo-transition-fast: 150ms ease-in-out;         /* maps to $transition-fast */
--nimo-transition-normal: 200ms ease-in-out;       /* maps to $transition-base */
--nimo-transition-slow: 300ms ease-in-out;         /* maps to $transition-slow */
--nimo-transition-slower: 500ms ease-in-out;       /* maps to $transition-slower */
--nimo-transition-expo: 250ms cubic-bezier(0.16, 1, 0.3, 1); /* alias for $ease-out-expo */
```

### Token Layer Mapping (Canonical Reference)
| Domain | SCSS Token | CSS Variable | Purpose |
|--------|------------|--------------|---------|
| Color (brand) | `$primary` | `--nimo-primary` | Brand base color |
| Color (semantic) | `$positive` | `--nimo-positive` | Success state |
| Spacing | `$space-6` | `--nimo-space-6` | Component padding medium |
| Radius | `$radius-lg` | `--nimo-radius-lg` | Card corners |
| Shadow | `$shadow-md` | `--nimo-shadow-md` | Medium elevation |
| Transition | `$transition-base` | `--nimo-transition-normal` | Standard motion |
| Easing | `$ease-out-expo` | `--nimo-transition-expo` | Enhanced emphasis motion |

Rules:
1. SCSS tokens drive authored component styling; CSS vars enable dynamic theming/runtime overrides.
2. Introducing a new scale requires updating both layers + this table.
3. If conflict ever arises, THIS document + `quasar.variables.scss` define the source of truth.

> NOTE: Previous omissions (e.g., `--nimo-space-7`) have been reconciled to prevent future drift.

---

## 2. Layout System

### Grid System
```css
.nimo-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--nimo-space-4);
}

.nimo-grid {
  display: grid;
  gap: var(--nimo-space-4);
}

.nimo-grid-2 { grid-template-columns: repeat(2, 1fr); }
.nimo-grid-3 { grid-template-columns: repeat(3, 1fr); }
.nimo-grid-4 { grid-template-columns: repeat(4, 1fr); }
.nimo-grid-auto { grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); }
```

### Responsive Breakpoints
```css
/* Mobile First */
--nimo-breakpoint-sm: 640px;   /* Small devices */
--nimo-breakpoint-md: 768px;   /* Tablets */
--nimo-breakpoint-lg: 1024px;  /* Laptops */
--nimo-breakpoint-xl: 1280px;  /* Desktops */
--nimo-breakpoint-2xl: 1536px; /* Large screens */
```

---

## 3. Component Library

### Button System

#### Base Button
```vue
<template>
  <button 
    :class="buttonClasses"
    :disabled="disabled || loading"
    v-bind="$attrs"
  >
    <q-circular-progress v-if="loading" :size="iconSize" />
    <q-icon v-else-if="icon" :name="icon" :size="iconSize" />
    <span v-if="$slots.default"><slot /></span>
  </button>
</template>
```

#### Button Variants
- **Primary:** Main actions (CTAs, submit)
- **Secondary:** Secondary actions
- **Outline:** Alternative actions
- **Ghost:** Subtle actions
- **Danger:** Destructive actions

#### Button Sizes
- **xs:** 24px height, 12px padding
- **sm:** 32px height, 16px padding
- **md:** 40px height, 20px padding (default)
- **lg:** 48px height, 24px padding
- **xl:** 56px height, 28px padding

### Card System

#### Base Card
```scss
.nimo-card {
  background: var(--nimo-card-bg);
  border: 1px solid var(--nimo-card-border);
  border-radius: var(--nimo-radius-lg);
  padding: var(--nimo-space-6);
  box-shadow: var(--nimo-shadow-md);
  transition: var(--nimo-transition-normal);
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--nimo-shadow-lg);
  }
}

.nimo-card-glass {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}
```

### Form Components

#### Input Field
```vue
<template>
  <div class="nimo-input-group">
    <label v-if="label" :for="inputId" class="nimo-label">{{ label }}</label>
    <div class="nimo-input-wrapper">
      <q-icon v-if="prefixIcon" :name="prefixIcon" class="nimo-input-icon-prefix" />
      <input
        :id="inputId"
        :class="inputClasses"
        :type="type"
        :placeholder="placeholder"
        :disabled="disabled"
        v-model="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
      />
      <q-icon v-if="suffixIcon" :name="suffixIcon" class="nimo-input-icon-suffix" />
    </div>
    <div v-if="error" class="nimo-input-error">{{ error }}</div>
    <div v-else-if="hint" class="nimo-input-hint">{{ hint }}</div>
  </div>
</template>
```

### Navigation Components

#### Nav Item
```vue
<template>
  <router-link
    :to="to"
    :class="navItemClasses"
    :aria-current="isActive ? 'page' : undefined"
  >
    <q-icon :name="icon" class="nimo-nav-icon" />
    <span class="nimo-nav-label">{{ label }}</span>
    <q-badge v-if="badge" :label="badge" class="nimo-nav-badge" />
  </router-link>
</template>
```

---

## 4. Theme System

### Light Theme
```css
:root {
  --nimo-bg-primary: #ffffff;
  --nimo-bg-secondary: #f8fafc;
  --nimo-text-primary: #0f172a;
  --nimo-text-secondary: #475569;
  --nimo-border-color: #e2e8f0;
  --nimo-card-bg: #ffffff;
  --nimo-card-border: #e2e8f0;
}
```

### Dark Theme (Cosmic)
```css
[data-theme="dark"] {
  --nimo-bg-primary: #0c0c0f;
  --nimo-bg-secondary: #161622;
  --nimo-text-primary: #f8fafc;
  --nimo-text-secondary: #cbd5e1;
  --nimo-border-color: #2a2a3e;
  --nimo-card-bg: rgba(30, 30, 46, 0.8);
  --nimo-card-border: rgba(255, 255, 255, 0.1);
}
```

### Glassmorphism Effects
```css
.nimo-glass {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.nimo-glass-dark {
  background: rgba(12, 12, 15, 0.8);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
}
```

---

## 5. Animation System

### Keyframes
```css
@keyframes nimo-fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes nimo-slide-up {
  from { 
    opacity: 0; 
    transform: translateY(20px); 
  }
  to { 
    opacity: 1; 
    transform: translateY(0); 
  }
}

@keyframes nimo-pulse-glow {
  0%, 100% { 
    box-shadow: 0 0 20px rgba(99, 102, 241, 0.3); 
  }
  50% { 
    box-shadow: 0 0 30px rgba(99, 102, 241, 0.6); 
  }
}

@keyframes nimo-float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-10px); }
}
```

### Animation Classes
```css
.nimo-animate-fade-in { animation: nimo-fade-in var(--nimo-transition-normal); }
.nimo-animate-slide-up { animation: nimo-slide-up var(--nimo-transition-normal); }
.nimo-animate-pulse-glow { animation: nimo-pulse-glow 2s ease-in-out infinite; }
.nimo-animate-float { animation: nimo-float 3s ease-in-out infinite; }

/* Hover Transforms */
.nimo-hover-lift:hover { transform: translateY(-4px); }
.nimo-hover-scale:hover { transform: scale(1.05); }
.nimo-hover-glow:hover { box-shadow: var(--nimo-shadow-glow); }
```

---

## 6. Accessibility Guidelines

### Color Contrast
- **Normal text:** Minimum 4.5:1 contrast ratio
- **Large text:** Minimum 3:1 contrast ratio
- **Interactive elements:** Minimum 3:1 contrast ratio

### Focus Management
```css
.nimo-focus-ring:focus-visible {
  outline: 2px solid var(--nimo-primary);
  outline-offset: 2px;
  border-radius: var(--nimo-radius-sm);
}

/* Remove default focus for non-keyboard users */
.nimo-focus-ring:focus:not(:focus-visible) {
  outline: none;
}
```

### Motion Preferences
```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

### Screen Reader Support
- Use semantic HTML elements
- Provide ARIA labels for complex components
- Announce dynamic content changes
- Implement skip navigation links

---

## 7. Implementation Guidelines

### CSS Architecture
```
src/
├── styles/
│   ├── tokens/
│   │   ├── colors.css
│   │   ├── typography.css
│   │   ├── spacing.css
│   │   └── shadows.css
│   ├── components/
│   │   ├── button.scss
│   │   ├── card.scss
│   │   ├── input.scss
│   │   └── navigation.scss
│   ├── layouts/
│   │   ├── grid.scss
│   │   └── container.scss
│   ├── themes/
│   │   ├── light.css
│   │   ├── dark.css
│   │   └── cosmic.css
│   └── globals/
│       ├── reset.css
│       ├── animations.css
│       └── utilities.css
```

### Component Naming
- Use BEM methodology: `.nimo-component__element--modifier`
- Prefix all classes with `nimo-`
- Use semantic naming over visual naming

### Development Workflow
1. Design tokens first
2. Build atomic components
3. Compose larger components
4. Test accessibility
5. Document in Storybook

---

## 8. Usage Examples

### Button Implementation
```vue
<template>
  <button 
    class="nimo-button nimo-button--primary nimo-button--md"
    :class="{
      'nimo-button--loading': loading,
      'nimo-button--disabled': disabled
    }"
  >
    <span class="nimo-button__content">
      <q-icon v-if="icon" :name="icon" class="nimo-button__icon" />
      <slot />
    </span>
  </button>
</template>

<style lang="scss">
.nimo-button {
  // Base styles using design tokens
  font-family: var(--nimo-font-primary);
  font-weight: var(--nimo-weight-medium);
  border-radius: var(--nimo-radius-md);
  transition: var(--nimo-transition-normal);
  
  // Size variants
  &--sm { 
    padding: var(--nimo-space-2) var(--nimo-space-4);
    font-size: var(--nimo-text-body2);
  }
  
  &--md { 
    padding: var(--nimo-space-3) var(--nimo-space-6);
    font-size: var(--nimo-text-body1);
  }
  
  // Color variants
  &--primary {
    background: var(--nimo-primary);
    color: white;
    
    &:hover {
      background: var(--nimo-primary-600);
      transform: translateY(-1px);
    }
  }
}
</style>
```

### Card Implementation
```vue
<template>
  <div :class="cardClasses">
    <header v-if="$slots.header" class="nimo-card__header">
      <slot name="header" />
    </header>
    <main class="nimo-card__content">
      <slot />
    </main>
    <footer v-if="$slots.actions" class="nimo-card__actions">
      <slot name="actions" />
    </footer>
  </div>
</template>

<style lang="scss">
.nimo-card {
  background: var(--nimo-card-bg);
  border: 1px solid var(--nimo-card-border);
  border-radius: var(--nimo-radius-lg);
  box-shadow: var(--nimo-shadow-md);
  overflow: hidden;
  
  &__header {
    padding: var(--nimo-space-6) var(--nimo-space-6) 0;
    border-bottom: 1px solid var(--nimo-border-color);
  }
  
  &__content {
    padding: var(--nimo-space-6);
  }
  
  &__actions {
    padding: 0 var(--nimo-space-6) var(--nimo-space-6);
    display: flex;
    gap: var(--nimo-space-3);
    justify-content: flex-end;
  }
  
  &--glass {
    @extend .nimo-glass;
  }
  
  &--hoverable {
    transition: var(--nimo-transition-normal);
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: var(--nimo-shadow-lg);
    }
  }
}
</style>
```

---

## 9. Design System Governance

### Version Control
- Semantic versioning for design system releases
- Changelog for breaking changes
- Migration guides for major updates

### Documentation Standards
- All components must have usage examples
- Accessibility guidelines for each component
- Do's and don'ts for proper usage
- Performance considerations

### Review Process
1. Design review for new components
2. Accessibility audit
3. Performance testing
4. Documentation completeness
5. Cross-browser testing

---

This design system serves as the foundation for creating consistent, accessible, and beautiful user interfaces across the Nimo platform. It should be treated as a living document that evolves with the product and user needs.

For interactive examples and component playground, see the Storybook documentation at `/storybook/`.