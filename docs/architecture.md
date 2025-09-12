# Nimo Platform Architecture

## Overview

The Nimo Platform is a decentralized identity and automated reward system built on MeTTa language and Cardano blockchain. This document outlines the system architecture, focusing on the React + Material UI frontend implementation.

## System Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Blockchain    │
│   (React + MUI) │◄──►│   (Python/Flask)│◄──►│   (Cardano)     │
│                 │    │                 │    │                 │
│ - User Interface│    │ - API Services  │    │ - Smart Contracts│
│ - State Mgmt    │    │ - MeTTa Engine  │    │ - Token System   │
│ - Components    │    │ - Database      │    │ - Identity NFTs  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Frontend Architecture

### Technology Stack

- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite
- **UI Library**: Material UI (MUI) v6
- **State Management**: Zustand
- **Routing**: React Router v6
- **HTTP Client**: Axios
- **Testing**: Jest + React Testing Library
- **Code Quality**: ESLint + Prettier

### Project Structure

```
frontend/
├── public/                    # Static assets
├── src/
│   ├── components/           # Reusable UI components
│   │   ├── common/          # Generic components (Button, Input, etc.)
│   │   ├── layout/          # Layout components (Header, Sidebar, etc.)
│   │   ├── forms/           # Form components
│   │   ├── cards/           # Card components
│   │   └── modals/          # Modal components
│   ├── pages/               # Page components
│   │   ├── auth/            # Authentication pages
│   │   ├── dashboard/       # Dashboard pages
│   │   ├── profile/         # User profile pages
│   │   ├── contributions/   # Contribution pages
│   │   └── admin/           # Admin pages
│   ├── stores/              # Zustand stores
│   │   ├── auth.ts          # Authentication store
│   │   ├── user.ts          # User data store
│   │   ├── contributions.ts # Contributions store
│   │   ├── tokens.ts        # Token operations store
│   │   └── ui.ts            # UI state store
│   ├── hooks/               # Custom React hooks
│   │   ├── useAuth.ts       # Authentication hook
│   │   ├── useWallet.ts     # Wallet connection hook
│   │   ├── useContributions.ts # Contributions hook
│   │   └── useApi.ts        # API interaction hook
│   ├── services/            # API service layer
│   │   ├── api.ts           # Base API configuration
│   │   ├── auth.ts          # Authentication services
│   │   ├── user.ts          # User services
│   │   ├── contributions.ts # Contribution services
│   │   ├── tokens.ts        # Token services
│   │   └── cardano.ts       # Cardano integration services
│   ├── utils/               # Utility functions
│   │   ├── constants.ts     # Application constants
│   │   ├── helpers.ts       # Helper functions
│   │   ├── validation.ts    # Validation utilities
│   │   └── formatters.ts    # Data formatters
│   ├── types/               # TypeScript type definitions
│   │   ├── api.ts           # API response types
│   │   ├── user.ts          # User-related types
│   │   ├── contributions.ts # Contribution types
│   │   └── tokens.ts        # Token types
│   ├── theme/               # Material UI theme configuration
│   │   ├── index.ts         # Main theme export
│   │   ├── palette.ts       # Color palette
│   │   ├── typography.ts    # Typography settings
│   │   └── components.ts    # Component overrides
│   ├── App.tsx              # Main application component
│   ├── main.tsx             # Application entry point
│   └── index.css            # Global styles
├── tests/                   # Test files
│   ├── unit/               # Unit tests
│   ├── integration/        # Integration tests
│   └── e2e/                # End-to-end tests
├── docs/                   # Documentation
└── package.json            # Dependencies and scripts
```

### Component Architecture

#### Atomic Design Pattern

```
Atoms (Basic)
├── Button
├── Input
├── Icon
├── Typography
└── Avatar

Molecules (Composite)
├── FormField
├── Card
├── ListItem
├── NavigationItem
└── StatusBadge

Organisms (Complex)
├── Header
├── Sidebar
├── LoginForm
├── ContributionList
└── Dashboard

Templates (Page-level)
├── AuthTemplate
├── DashboardTemplate
├── ProfileTemplate
└── AdminTemplate

Pages (Complete)
├── LoginPage
├── DashboardPage
├── ProfilePage
└── AdminPage
```

#### Component Patterns

##### Functional Components with Hooks

```typescript
// Custom hook for component logic
const useLoginForm = () => {
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(formData);
      // Success handling
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return {
    formData,
    setFormData,
    loading,
    error,
    handleSubmit
  };
};

// Component using the hook
const LoginForm: React.FC = () => {
  const { formData, setFormData, loading, error, handleSubmit } = useLoginForm();

  return (
    <Box component="form" onSubmit={handleSubmit}>
      <TextField
        label="Email"
        value={formData.email}
        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
        required
      />
      <TextField
        label="Password"
        type="password"
        value={formData.password}
        onChange={(e) => setFormData({ ...formData, password: e.target.value })}
        required
      />
      {error && <Alert severity="error">{error}</Alert>}
      <Button type="submit" disabled={loading}>
        {loading ? <CircularProgress size={20} /> : 'Login'}
      </Button>
    </Box>
  );
};
```

##### Higher-Order Components (HOCs)

```typescript
// Authentication HOC
const withAuth = <P extends object>(
  Component: React.ComponentType<P>
) => {
  const AuthenticatedComponent: React.FC<P> = (props) => {
    const { user, loading } = useAuth();

    if (loading) {
      return <CircularProgress />;
    }

    if (!user) {
      return <Navigate to="/login" replace />;
    }

    return <Component {...props} />;
  };

  return AuthenticatedComponent;
};

// Usage
const ProtectedDashboard = withAuth(Dashboard);
```

### State Management Architecture

#### Zustand Store Pattern

```typescript
// Auth store
interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  loading: boolean;
  error: string | null;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isAuthenticated: false,
  loading: false,
  error: null,

  login: async (credentials) => {
    set({ loading: true, error: null });
    try {
      const response = await api.login(credentials);
      set({
        user: response.user,
        isAuthenticated: true,
        loading: false
      });
    } catch (error) {
      set({
        error: error.message,
        loading: false
      });
    }
  },

  logout: () => {
    set({
      user: null,
      isAuthenticated: false,
      error: null
    });
  },

  clearError: () => {
    set({ error: null });
  }
}));
```

#### Store Composition Pattern

```typescript
// Combined store for related functionality
export const useContributionsStore = create((set, get) => ({
  contributions: [],
  loading: false,
  error: null,

  // Actions
  fetchContributions: async () => {
    set({ loading: true });
    try {
      const contributions = await api.getContributions();
      set({ contributions, loading: false });
    } catch (error) {
      set({ error: error.message, loading: false });
    }
  },

  addContribution: async (contribution) => {
    const newContribution = await api.createContribution(contribution);
    set(state => ({
      contributions: [...state.contributions, newContribution]
    }));
  },

  updateContribution: async (id, updates) => {
    const updatedContribution = await api.updateContribution(id, updates);
    set(state => ({
      contributions: state.contributions.map(c =>
        c.id === id ? updatedContribution : c
      )
    }));
  }
}));
```

### API Integration Layer

#### Service Layer Pattern

```typescript
// Base API service
class ApiService {
  protected api = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
    timeout: 10000,
  });

  constructor() {
    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor for auth
    this.api.interceptors.request.use((config) => {
      const token = localStorage.getItem('authToken');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Response interceptor for error handling
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
}

// Specific service extending base
export class ContributionService extends ApiService {
  async getContributions(params?: ContributionFilters) {
    const response = await this.api.get('/contributions', { params });
    return response.data;
  }

  async createContribution(contribution: CreateContributionData) {
    const response = await this.api.post('/contributions', contribution);
    return response.data;
  }

  async updateContribution(id: string, updates: UpdateContributionData) {
    const response = await this.api.patch(`/contributions/${id}`, updates);
    return response.data;
  }
}
```

### Routing Architecture

#### Protected Routes Pattern

```typescript
// Route configuration
const routes: RouteObject[] = [
  {
    path: '/',
    element: <AppLayout />,
    children: [
      {
        index: true,
        element: <Dashboard />
      },
      {
        path: 'profile',
        element: (
          <ProtectedRoute>
            <Profile />
          </ProtectedRoute>
        )
      },
      {
        path: 'contributions',
        element: (
          <ProtectedRoute>
            <Contributions />
          </ProtectedRoute>
        )
      },
      {
        path: 'admin',
        element: (
          <ProtectedRoute requiredRole="admin">
            <Admin />
          </ProtectedRoute>
        )
      }
    ]
  },
  {
    path: '/auth',
    element: <AuthLayout />,
    children: [
      {
        path: 'login',
        element: <Login />
      },
      {
        path: 'register',
        element: <Register />
      }
    ]
  }
];

// Protected route component
const ProtectedRoute: React.FC<{
  children: React.ReactNode;
  requiredRole?: string;
}> = ({ children, requiredRole }) => {
  const { user, loading } = useAuthStore();

  if (loading) {
    return <CircularProgress />;
  }

  if (!user) {
    return <Navigate to="/auth/login" replace />;
  }

  if (requiredRole && user.role !== requiredRole) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};
```

### Material UI Theme Architecture

#### Theme Configuration

```typescript
// Color palette
const colors = {
  primary: {
    main: '#1976d2',
    light: '#42a5f5',
    dark: '#1565c0',
    contrastText: '#ffffff'
  },
  secondary: {
    main: '#9c27b0',
    light: '#ba68c8',
    dark: '#7b1fa2',
    contrastText: '#ffffff'
  },
  success: {
    main: '#4caf50',
    light: '#81c784',
    dark: '#388e3c',
    contrastText: '#ffffff'
  },
  error: {
    main: '#f44336',
    light: '#e57373',
    dark: '#d32f2f',
    contrastText: '#ffffff'
  }
};

// Typography
const typography = {
  fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
  h1: {
    fontSize: '2.5rem',
    fontWeight: 600,
    lineHeight: 1.2
  },
  h2: {
    fontSize: '2rem',
    fontWeight: 600,
    lineHeight: 1.3
  },
  h3: {
    fontSize: '1.75rem',
    fontWeight: 600,
    lineHeight: 1.4
  },
  body1: {
    fontSize: '1rem',
    lineHeight: 1.5
  },
  body2: {
    fontSize: '0.875rem',
    lineHeight: 1.5
  }
};

// Component overrides
const components = {
  MuiButton: {
    styleOverrides: {
      root: {
        borderRadius: 8,
        textTransform: 'none',
        fontWeight: 500
      }
    }
  },
  MuiCard: {
    styleOverrides: {
      root: {
        borderRadius: 12,
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
      }
    }
  }
};

// Main theme
export const theme = createTheme({
  palette: colors,
  typography,
  components,
  shape: {
    borderRadius: 8
  }
});
```

### Performance Optimization

#### Code Splitting Strategy

```typescript
// Lazy loading for routes
const Dashboard = lazy(() => import('../pages/Dashboard'));
const Profile = lazy(() => import('../pages/Profile'));
const Contributions = lazy(() => import('../pages/Contributions'));

// Route configuration with lazy loading
const routes = [
  {
    path: '/',
    element: <Dashboard />
  },
  {
    path: '/profile',
    element: (
      <Suspense fallback={<PageSkeleton />}>
        <Profile />
      </Suspense>
    )
  }
];
```

#### Component Optimization

```typescript
// Memoized component
const ContributionCard = memo<ContributionCardProps>(({
  contribution,
  onEdit,
  onDelete
}) => {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6">
          {contribution.title}
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {contribution.description}
        </Typography>
        <Box sx={{ mt: 2 }}>
          <Button onClick={() => onEdit(contribution)}>
            Edit
          </Button>
          <Button onClick={() => onDelete(contribution.id)}>
            Delete
          </Button>
        </Box>
      </CardContent>
    </Card>
  );
});

// Custom hook for expensive computations
const useContributionsData = (contributions: Contribution[]) => {
  return useMemo(() => {
    const total = contributions.length;
    const completed = contributions.filter(c => c.status === 'completed').length;
    const pending = total - completed;

    return { total, completed, pending };
  }, [contributions]);
};
```

### Security Architecture

#### Input Validation

```typescript
// Validation schema
const contributionSchema = z.object({
  title: z.string().min(1, 'Title is required').max(100, 'Title too long'),
  description: z.string().max(500, 'Description too long'),
  amount: z.number().positive('Amount must be positive'),
  category: z.enum(['development', 'design', 'research', 'other'])
});

// Validation hook
const useFormValidation = <T extends z.ZodSchema>(
  schema: T,
  data: z.infer<T>
) => {
  const [errors, setErrors] = useState<Partial<z.infer<T>>>({});

  const validate = useCallback(() => {
    const result = schema.safeParse(data);
    if (!result.success) {
      const fieldErrors: Partial<z.infer<T>> = {};
      result.error.errors.forEach((error) => {
        const path = error.path.join('.');
        fieldErrors[path as keyof z.infer<T>] = error.message;
      });
      setErrors(fieldErrors);
      return false;
    }
    setErrors({});
    return true;
  }, [data, schema]);

  return { errors, validate };
};
```

#### Authentication & Authorization

#### Authentication Methods
- **Traditional Email/Password**: Standard registration with email verification
- **Wallet Authentication**: Cardano wallet signature-based authentication
- **JWT Tokens**: Secure session management with automatic expiration
- **Multi-Factor Authentication**: Required for administrative actions

#### KYC Verification System
- **Document Upload**: Government ID, proof of address, biometric data
- **Automated Review**: AI-powered document verification
- **Manual Review**: Human verification for complex cases
- **Blockchain Verification**: Wallet ownership verification via signatures
- **Compliance Tracking**: Audit trail of all verification processes

#### KYC Process Flow
```typescript
// KYC verification workflow
const KYCVerificationFlow = {
  stages: [
    'document_upload',
    'automated_review',
    'manual_review',
    'wallet_verification',
    'approval'
  ],
  
  requiredDocuments: [
    'government_id',
    'proof_of_address',
    'biometric_photo'
  ],
  
  verificationMethods: [
    'ai_document_analysis',
    'human_review',
    'blockchain_signature_verification'
  ]
};
```

#### Access Control
```
Public Routes:
├── Landing page ✓
├── Platform information ✓
├── Basic browsing ✓

Protected Routes (Authentication Required):
├── User Dashboard ✓
├── Contribution Management ✓
├── Token Operations ✓
├── Profile Management ✓

KYC-Protected Routes (Full Verification Required):
├── Impact Bond Creation ✓
├── Investment Operations ✓
├── Advanced Features ✓
└── Administrative Functions ✓
```

#### Security Architecture
- **Rate Limiting**: Prevents brute force attacks and spam
- **Input Validation**: Comprehensive data sanitization
- **Audit Logging**: All authentication attempts logged
- **Session Management**: Secure token handling with expiration
- **Encryption**: End-to-end encryption for sensitive data

### Testing Architecture

#### Unit Testing Pattern

```typescript
// Component test
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ContributionForm } from './ContributionForm';

const mockOnSubmit = jest.fn();

describe('ContributionForm', () => {
  beforeEach(() => {
    mockOnSubmit.mockClear();
  });

  it('renders form fields correctly', () => {
    render(<ContributionForm onSubmit={mockOnSubmit} />);

    expect(screen.getByLabelText(/title/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/amount/i)).toBeInTheDocument();
  });

  it('submits form with valid data', async () => {
    render(<ContributionForm onSubmit={mockOnSubmit} />);

    fireEvent.change(screen.getByLabelText(/title/i), {
      target: { value: 'Test Contribution' }
    });
    fireEvent.change(screen.getByLabelText(/amount/i), {
      target: { value: '100' }
    });
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        title: 'Test Contribution',
        amount: 100
      });
    });
  });
});
```

#### Integration Testing

```typescript
// API integration test
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import { render, screen, waitFor } from '@testing-library/react';
import { ContributionsPage } from './ContributionsPage';

const server = setupServer(
  rest.get('/api/contributions', (req, res, ctx) => {
    return res(ctx.json([
      { id: '1', title: 'Test Contribution', status: 'pending' }
    ]));
  })
);

describe('ContributionsPage', () => {
  beforeAll(() => server.listen());
  afterEach(() => server.resetHandlers());
  afterAll(() => server.close());

  it('loads and displays contributions', async () => {
    render(<ContributionsPage />);

    expect(screen.getByText(/loading/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('Test Contribution')).toBeInTheDocument();
    });
  });
});
```

### Deployment Architecture

#### Build Configuration

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import { visualizer } from 'rollup-plugin-visualizer';

export default defineConfig({
  plugins: [
    react(),
    visualizer({
      filename: 'dist/stats.html',
      open: true,
      gzipSize: true,
      brotliSize: true
    })
  ],

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
          utils: ['axios', 'zustand', 'zod']
        }
      }
    }
  },

  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  }
});
```

#### Environment Configuration

```typescript
// Environment variables
interface Config {
  apiUrl: string;
  cardanoNetwork: 'mainnet' | 'testnet';
  ipfsGateway: string;
  enableAnalytics: boolean;
}

const config: Config = {
  apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:5000',
  cardanoNetwork: (import.meta.env.VITE_CARDANO_NETWORK as any) || 'testnet',
  ipfsGateway: import.meta.env.VITE_IPFS_GATEWAY || 'https://gateway.ipfs.io',
  enableAnalytics: import.meta.env.VITE_ENABLE_ANALYTICS === 'true'
};

export default config;
```

## Backend Integration

### API Communication Pattern

```typescript
// API client with error handling
class ApiClient {
  private axiosInstance = axios.create({
    baseURL: config.apiUrl,
    timeout: 10000
  });

  constructor() {
    this.setupInterceptors();
  }

  private setupInterceptors() {
    this.axiosInstance.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          useAuthStore.getState().logout();
        }
        throw new ApiError(error);
      }
    );
  }

  async get<T>(url: string, params?: any): Promise<T> {
    const response = await this.axiosInstance.get(url, { params });
    return response.data;
  }

  async post<T>(url: string, data?: any): Promise<T> {
    const response = await this.axiosInstance.post(url, data);
    return response.data;
  }

  async put<T>(url: string, data?: any): Promise<T> {
    const response = await this.axiosInstance.put(url, data);
    return response.data;
  }

  async delete(url: string): Promise<void> {
    await this.axiosInstance.delete(url);
  }
}

export const apiClient = new ApiClient();
```

### Real-time Communication

```typescript
// WebSocket integration for real-time updates
import { io, Socket } from 'socket.io-client';

class WebSocketService {
  private socket: Socket | null = null;

  connect() {
    this.socket = io(config.apiUrl, {
      auth: {
        token: localStorage.getItem('authToken')
      }
    });

    this.socket.on('contribution:updated', (data) => {
      useContributionsStore.getState().updateContribution(data.id, data);
    });

    this.socket.on('token:awarded', (data) => {
      useTokensStore.getState().addTokens(data.amount);
    });
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }

  emit(event: string, data: any) {
    if (this.socket) {
      this.socket.emit(event, data);
    }
  }
}

export const wsService = new WebSocketService();
```

## Monitoring & Analytics

### Performance Monitoring

```typescript
// Performance tracking
const usePerformanceTracking = () => {
  const trackPageView = useCallback((pageName: string) => {
    // Track page view
    if (config.enableAnalytics) {
      // Send to analytics service
    }
  }, []);

  const trackEvent = useCallback((eventName: string, properties?: any) => {
    // Track custom events
    if (config.enableAnalytics) {
      // Send to analytics service
    }
  }, []);

  return { trackPageView, trackEvent };
};
```

### Error Tracking

```typescript
// Error boundary for React components
class ErrorBoundary extends React.Component<
  { children: React.ReactNode; fallback?: React.ComponentType<any> },
  { hasError: boolean; error?: Error }
> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log error to monitoring service
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      const FallbackComponent = this.props.fallback || DefaultErrorFallback;
      return <FallbackComponent error={this.state.error} />;
    }

    return this.props.children;
  }
}
```

## Conclusion

This architecture provides a solid foundation for the Nimo Platform frontend, emphasizing:

- **Scalability**: Modular component structure and efficient state management
- **Maintainability**: Clear separation of concerns and comprehensive testing
- **Performance**: Optimized rendering and resource management
- **Security**: Input validation and secure API communication
- **User Experience**: Consistent Material UI design and responsive layout

The architecture is designed to evolve with the platform's growth while maintaining code quality and developer productivity.

---

**Last Updated**: September 10, 2025  
**Version**: 1.0  
**Authors**: Nimo Development Team