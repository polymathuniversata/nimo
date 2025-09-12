# Vue to React Migration Guide

This document provides practical guidelines for migrating Vue components to React in the Nimo project. It works in conjunction with the comprehensive `migration-assessment.md` document.

## Quick Start

1. **Check Migration Status**
   ```bash
   node scripts/track-migration-progress.js
   ```
   This will update the migration statistics in `docs/migration-assessment.md`.

2. **Select a Component to Migrate**
   Choose an unmigrated component from the Pages Migration Status table in `docs/migration-assessment.md`.

3. **Create the React Equivalent**
   Follow the Component Migration Workflow described in `docs/migration-assessment.md`.

4. **Delete the Vue Component**
   Once migration is verified complete, delete the Vue component:
   ```bash
   # Preview which files would be deleted
   node scripts/cleanup-vue-files.js --dry-run
   
   # Delete the Vue files with confirmation
   node scripts/cleanup-vue-files.js
   ```

## Migration Checklist

For each component migration, follow this checklist:

- [ ] Create React component (.tsx) file
- [ ] Implement component logic using React hooks
- [ ] Convert template to JSX
- [ ] Update state management from Pinia to Zustand
- [ ] Add TypeScript interfaces for props and state
- [ ] Write tests for the component
- [ ] Verify integration with parent components
- [ ] Update imports in dependent components
- [ ] Run the tracking script to update migration status
- [ ] Delete the Vue component using the cleanup script

## Common Vue to React Conversion Patterns

### Template to JSX

```vue
<!-- Vue -->
<template>
  <div class="card">
    <h2>{{ title }}</h2>
    <p v-if="description">{{ description }}</p>
    <button @click="handleClick">{{ buttonText }}</button>
  </div>
</template>
```

```tsx
// React
const Card = ({ title, description, buttonText }) => {
  return (
    <div className="card">
      <h2>{title}</h2>
      {description && <p>{description}</p>}
      <button onClick={handleClick}>{buttonText}</button>
    </div>
  );
};
```

### Props

```vue
<!-- Vue -->
<script setup lang="ts">
const props = defineProps({
  title: String,
  description: String,
  buttonText: { type: String, default: 'Click Me' }
});
</script>
```

```tsx
// React
interface CardProps {
  title: string;
  description?: string;
  buttonText?: string;
}

const Card: React.FC<CardProps> = ({ 
  title, 
  description, 
  buttonText = 'Click Me' 
}) => {
  // Component code
};
```

### Reactive Data to Hooks

```vue
<!-- Vue -->
<script setup lang="ts">
import { ref, computed } from 'vue';

const count = ref(0);
const doubleCount = computed(() => count.value * 2);

const increment = () => {
  count.value++;
};
</script>
```

```tsx
// React
import { useState, useMemo } from 'react';

const Counter = () => {
  const [count, setCount] = useState(0);
  const doubleCount = useMemo(() => count * 2, [count]);

  const increment = () => {
    setCount(count + 1);
  };
};
```

### Lifecycle Hooks

```vue
<!-- Vue -->
<script setup lang="ts">
import { onMounted, onUnmounted, watch } from 'vue';

onMounted(() => {
  console.log('Component mounted');
});

onUnmounted(() => {
  console.log('Component unmounted');
});

watch(someRef, (newValue, oldValue) => {
  console.log('Value changed', newValue, oldValue);
});
</script>
```

```tsx
// React
import { useEffect } from 'react';

const MyComponent = () => {
  useEffect(() => {
    console.log('Component mounted');
    
    return () => {
      console.log('Component unmounted');
    };
  }, []);

  useEffect(() => {
    console.log('Value changed', someValue);
  }, [someValue]);
};
```

### Event Handlers

```vue
<!-- Vue -->
<template>
  <button @click="handleClick">Click Me</button>
</template>

<script setup lang="ts">
const emit = defineEmits(['click']);

const handleClick = (event) => {
  emit('click', event);
};
</script>
```

```tsx
// React
interface ButtonProps {
  onClick: (event: React.MouseEvent) => void;
}

const Button: React.FC<ButtonProps> = ({ onClick }) => {
  const handleClick = (event: React.MouseEvent) => {
    onClick(event);
  };

  return <button onClick={handleClick}>Click Me</button>;
};
```

### Slots to Children

```vue
<!-- Vue -->
<template>
  <div class="card">
    <div class="header">
      <slot name="header">Default Header</slot>
    </div>
    <div class="body">
      <slot>Default Content</slot>
    </div>
  </div>
</template>
```

```tsx
// React
interface CardProps {
  header?: React.ReactNode;
  children?: React.ReactNode;
}

const Card: React.FC<CardProps> = ({ header = 'Default Header', children = 'Default Content' }) => {
  return (
    <div className="card">
      <div className="header">
        {header}
      </div>
      <div className="body">
        {children}
      </div>
    </div>
  );
};
```

### Store (Pinia to Zustand)

```ts
// Vue with Pinia
import { defineStore } from 'pinia';

export const useCounterStore = defineStore('counter', {
  state: () => ({
    count: 0
  }),
  getters: {
    doubleCount: (state) => state.count * 2
  },
  actions: {
    increment() {
      this.count++;
    }
  }
});
```

```ts
// React with Zustand
import create from 'zustand';

interface CounterState {
  count: number;
  doubleCount: number;
  increment: () => void;
}

export const useCounterStore = create<CounterState>((set, get) => ({
  count: 0,
  doubleCount: 0,
  increment: () => set((state) => ({ 
    count: state.count + 1,
    doubleCount: (state.count + 1) * 2
  }))
}));
```

## Additional Tips

1. **Material UI Components**: When migrating from Vue's UI library to Material UI, refer to the [Material UI documentation](https://mui.com/getting-started/usage/) for equivalent components.

2. **CSS Handling**: Consider using CSS modules or styled-components instead of Vue's scoped styles.

3. **Testing**: Use React Testing Library instead of Vue Test Utils.

4. **Routing**: Replace Vue Router with React Router.

5. **Forms**: Consider using React Hook Form or Formik instead of Vue's v-model approach.

6. **Error Handling**: Implement error boundaries in React components.

## Troubleshooting

### Common Issues

1. **JSX Conditional Rendering**: Remember that JSX requires `&&` or ternary operators for conditional rendering instead of Vue's `v-if`.

2. **Event Handling**: React uses camelCase for event handlers (onClick) while Vue uses kebab-case (@click).

3. **Form Inputs**: React uses controlled components pattern instead of Vue's v-model.

4. **CSS Classes**: Use `className` instead of `class` in React.

5. **Async Data Fetching**: Use `useEffect` for data fetching instead of Vue's lifecycle hooks.

For additional help, refer to the comprehensive `migration-assessment.md` document and the React documentation.