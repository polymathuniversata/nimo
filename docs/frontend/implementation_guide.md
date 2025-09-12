# Frontend Implementation Guide

## Overview

This guide provides implementation details for the Nimo Platform React frontend, focusing on best practices, performance optimization, and maintainable code structure.

## Technology Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **UI Library**: Material UI (MUI) v6
- **State Management**: Zustand
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **Testing**: Vitest + React Testing Library
- **Code Quality**: ESLint + Prettier

## Project Structure

```
frontend/
├── src/
│   ├── components/           # Reusable UI components
│   │   ├── common/          # Generic components
│   │   ├── layout/          # Layout components
│   │   └── forms/           # Form components
│   ├── pages/               # Page components
│   ├── stores/              # Zustand stores
│   ├── hooks/               # Custom React hooks
│   ├── services/            # API service layer
│   ├── utils/               # Utility functions
│   ├── types/               # TypeScript definitions
│   ├── theme/               # MUI theme configuration
│   ├── App.tsx              # Main app component
│   ├── main.tsx             # Entry point
│   └── router/              # Routing configuration
├── tests/                   # Test files
└── docs/                    # Documentation
```

## Quick Wins (Sprint 1)

### 1. Enable TypeScript Strict Mode

**File: `tsconfig.app.json`**
```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "exactOptionalPropertyTypes": true
  }
}
```

### 2. Add Security Headers

**File: `vite.config.ts`**
```typescript
export default defineConfig({
  server: {
    headers: {
      'X-Content-Type-Options': 'nosniff',
      'X-Frame-Options': 'DENY',
      'X-XSS-Protection': '1; mode=block',
      'Referrer-Policy': 'strict-origin-when-cross-origin'
    }
  }
})
```

### 3. Implement Error Boundaries

**File: `src/components/ErrorBoundary.tsx`**
```typescript
import React from 'react';

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
}

class ErrorBoundary extends React.Component<
  React.PropsWithChildren<{}>,
  ErrorBoundaryState
> {
  constructor(props: React.PropsWithChildren<{}>) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>Something went wrong</h2>
          <p>Please refresh the page or contact support</p>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
```

## Component Architecture (Sprint 2)

### 1. Atomic Design Pattern

**Atoms (Basic Components)**
```typescript
// src/components/common/Button.tsx
import React from 'react';
import { Button as MuiButton, ButtonProps } from '@mui/material';

interface CustomButtonProps extends ButtonProps {
  variant?: 'primary' | 'secondary' | 'outline';
}

export const Button: React.FC<CustomButtonProps> = ({
  variant = 'primary',
  children,
  ...props
}) => {
  return (
    <MuiButton
      variant={variant === 'outline' ? 'outlined' : 'contained'}
      color={variant === 'secondary' ? 'secondary' : 'primary'}
      {...props}
    >
      {children}
    </MuiButton>
  );
};
```

**Molecules (Composite Components)**
```typescript
// src/components/forms/LoginForm.tsx
import React, { useState } from 'react';
import { Box, TextField, Button } from '@mui/material';

interface LoginFormProps {
  onSubmit: (credentials: { email: string; password: string }) => void;
  loading?: boolean;
}

export const LoginForm: React.FC<LoginFormProps> = ({
  onSubmit,
  loading = false
}) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ email, password });
  };

  return (
    <Box component="form" onSubmit={handleSubmit}>
      <TextField
        label="Email"
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        required
        fullWidth
        margin="normal"
      />
      <TextField
        label="Password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        required
        fullWidth
        margin="normal"
      />
      <Button
        type="submit"
        variant="contained"
        fullWidth
        disabled={loading}
        sx={{ mt: 2 }}
      >
        {loading ? 'Logging in...' : 'Login'}
      </Button>
    </Box>
  );
};
```

### 2. Custom Hooks

**File: `src/hooks/useAuth.ts`**
```typescript
import { useState, useEffect } from 'react';
import { useAuthStore } from '../stores/auth';

export const useAuth = () => {
  const { user, login, logout, loading } = useAuthStore();
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    setIsAuthenticated(!!user);
  }, [user]);

  return {
    user,
    isAuthenticated,
    loading,
    login,
    logout
  };
};
```

## State Management (Sprint 3)

### Zustand Store Pattern

**File: `src/stores/auth.ts`**
```typescript
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  email: string;
  name: string;
  role: 'user' | 'admin';
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;

  login: (credentials: { email: string; password: string }) => Promise<void>;
  logout: () => void;
  setUser: (user: User) => void;
  setError: (error: string | null) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      loading: false,
      error: null,

      login: async (credentials) => {
        set({ loading: true, error: null });
        try {
          const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(credentials)
          });

          if (!response.ok) {
            throw new Error('Login failed');
          }

          const data = await response.json();
          set({
            user: data.user,
            token: data.token,
            isAuthenticated: true,
            loading: false
          });
        } catch (error) {
          set({
            error: error instanceof Error ? error.message : 'Login failed',
            loading: false
          });
        }
      },

      logout: () => {
        set({
          user: null,
          token: null,
          isAuthenticated: false,
          error: null
        });
      },

      setUser: (user) => set({ user }),
      setError: (error) => set({ error })
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated
      })
    }
  )
);
```

## API Integration (Sprint 4)

### Service Layer Pattern

**File: `src/services/api.ts`**
```typescript
import axios, { AxiosInstance, AxiosResponse } from 'axios';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000/api',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor
    this.api.interceptors.request.use((config) => {
      const token = localStorage.getItem('authToken');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Response interceptor
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Handle unauthorized
          useAuthStore.getState().logout();
        }
        return Promise.reject(error);
      }
    );
  }

  async get<T>(url: string, params?: any): Promise<T> {
    const response: AxiosResponse<T> = await this.api.get(url, { params });
    return response.data;
  }

  async post<T>(url: string, data?: any): Promise<T> {
    const response: AxiosResponse<T> = await this.api.post(url, data);
    return response.data;
  }

  async put<T>(url: string, data?: any): Promise<T> {
    const response: AxiosResponse<T> = await this.api.put(url, data);
    return response.data;
  }

  async delete(url: string): Promise<void> {
    await this.api.delete(url);
  }
}

export const apiService = new ApiService();
```

## Testing Strategy (Sprint 5)

### Unit Testing

**File: `src/components/common/Button.test.tsx`**
```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('renders children correctly', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('handles click events', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('applies correct variant styles', () => {
    render(<Button variant="outline">Outline</Button>);
    const button = screen.getByText('Outline');
    expect(button).toHaveClass('MuiButton-outlined');
  });
});
```

### Integration Testing

**File: `src/pages/LoginPage.test.tsx`**
```typescript
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { LoginPage } from './LoginPage';

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('LoginPage', () => {
  it('submits login form successfully', async () => {
    renderWithRouter(<LoginPage />);

    fireEvent.change(screen.getByLabelText(/email/i), {
      target: { value: 'test@example.com' }
    });
    fireEvent.change(screen.getByLabelText(/password/i), {
      target: { value: 'password123' }
    });
    fireEvent.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(screen.getByText(/login successful/i)).toBeInTheDocument();
    });
  });
});
```

## Performance Optimization (Sprint 6)

### Code Splitting

**File: `src/router/reactRoutes.tsx`**
```typescript
import { lazy, Suspense } from 'react';
import { RouteObject } from 'react-router-dom';

const Dashboard = lazy(() => import('../pages/Dashboard'));
const Profile = lazy(() => import('../pages/Profile'));
const Contributions = lazy(() => import('../pages/Contributions'));

const routes: RouteObject[] = [
  {
    path: '/',
    element: <App />,
    children: [
      {
        index: true,
        element: (
          <Suspense fallback={<div>Loading...</div>}>
            <Dashboard />
          </Suspense>
        )
      },
      {
        path: 'profile',
        element: (
          <Suspense fallback={<div>Loading...</div>}>
            <Profile />
          </Suspense>
        )
      },
      {
        path: 'contributions',
        element: (
          <Suspense fallback={<div>Loading...</div>}>
            <Contributions />
          </Suspense>
        )
      }
    ]
  }
];

export default routes;
```

### Component Optimization

**File: `src/components/ContributionCard.tsx`**
```typescript
import React, { memo } from 'react';
import { Card, CardContent, Typography, Button, Box } from '@mui/material';

interface Contribution {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'completed';
}

interface ContributionCardProps {
  contribution: Contribution;
  onEdit: (contribution: Contribution) => void;
  onDelete: (id: string) => void;
}

export const ContributionCard = memo<ContributionCardProps>(({
  contribution,
  onEdit,
  onDelete
}) => {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6" component="h2">
          {contribution.title}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {contribution.description}
        </Typography>
        <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
          <Button
            size="small"
            onClick={() => onEdit(contribution)}
          >
            Edit
          </Button>
          <Button
            size="small"
            color="error"
            onClick={() => onDelete(contribution.id)}
          >
            Delete
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
});
```

## Deployment Guide

### Build Configuration

**File: `vite.config.ts`**
```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  build: {
    target: 'esnext',
    minify: 'terser',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          router: ['react-router-dom'],
          ui: ['@mui/material', '@mui/icons-material'],
          utils: ['axios', 'zustand']
        }
      }
    }
  }
});
```

### Environment Variables

**File: `.env.production`**
```env
VITE_API_URL=https://api.nimo-platform.com
VITE_CARDANO_NETWORK=mainnet
VITE_ENABLE_ANALYTICS=true
```

### Deployment Commands

```bash
# Build for production
npm run build

# Preview production build
npm run preview

# Deploy to production
npm run deploy
```

## Success Metrics

- [x] TypeScript strict mode enabled
- [x] Security headers implemented
- [x] Error boundaries added
- [x] Component architecture established
- [x] State management implemented
- [x] API integration complete
- [x] Testing strategy in place
- [x] Performance optimizations applied
- [x] Deployment pipeline configured

## Next Steps

1. **Accessibility**: Add ARIA labels and keyboard navigation
2. **Internationalization**: Implement i18n support
3. **Progressive Web App**: Add service worker and offline support
4. **Monitoring**: Set up error tracking and performance monitoring
5. **Documentation**: Complete API documentation and user guides

---

**Last Updated**: September 10, 2025
**Version**: 2.0
**Authors**: Nimo Development Team
