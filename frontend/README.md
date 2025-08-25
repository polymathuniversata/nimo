# Nimo Frontend

Vue.js + Quasar frontend application for the Nimo decentralized identity platform.

## Technology Stack

- **Vue.js 3**: Progressive JavaScript framework
- **Quasar Framework**: Vue.js based UI framework
- **Pinia**: State management for Vue 3
- **Axios**: HTTP client for API communication
- **Vue Router**: Client-side routing

## Project Structure

```
src/
├── components/        # Reusable Vue components
│   └── bonds/        # Bond-related components
├── layouts/          # Page layout templates
│   ├── AuthLayout.vue    # Layout for auth pages
│   └── MainLayout.vue    # Main application layout
├── pages/            # Application pages
│   ├── auth/         # Authentication pages
│   ├── BondsPage.vue
│   ├── ContributionsPage.vue
│   ├── IndexPage.vue
│   ├── ProfilePage.vue
│   └── TokensPage.vue
├── services/         # API service layer
├── stores/           # Pinia stores (state management)
└── router/           # Vue Router configuration
```

## Getting Started

### Prerequisites
- Node.js 16+ and npm

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Lint code
npm run lint
```

## Development

### Adding New Pages

1. Create a new Vue component in `src/pages/`
2. Add the route to `src/router/routes.js`
3. Update navigation if needed

### State Management

Use Pinia stores for global state management:

```javascript
// stores/user.js
import { defineStore } from 'pinia'

export const useUserStore = defineStore('user', {
  state: () => ({
    currentUser: null,
    tokenBalance: 0
  }),
  
  actions: {
    async fetchUserProfile() {
      // API call logic
    }
  }
})
```

### API Integration

API services are located in `src/services/`:

```javascript
// services/contribution.service.js
import api from './index.js'

export default {
  getContributions() {
    return api.get('/contributions')
  },
  
  addContribution(data) {
    return api.post('/contributions', data)
  }
}
```

### Component Guidelines

- Use Quasar components for consistent UI
- Follow Vue 3 Composition API patterns
- Keep components focused and reusable
- Add proper TypeScript types if using TS

## Quasar Framework

Key Quasar components used:
- `q-layout`, `q-page-container`, `q-page` for layouts
- `q-card`, `q-btn`, `q-input` for UI elements
- `q-table` for data display
- `q-dialog` for modals

Refer to [Quasar documentation](https://quasar.dev/) for component APIs.

## Environment Configuration

Create `.env` files for different environments:

```bash
# .env.development
VUE_APP_API_URL=http://localhost:5000/api

# .env.production
VUE_APP_API_URL=https://api.nimo.org/api
```

## Build and Deployment

```bash
# Build for production
npm run build

# Built files will be in dist/spa/
# Deploy the dist/spa/ directory to your web server
```