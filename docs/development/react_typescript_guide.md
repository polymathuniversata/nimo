# Frontend React/TypeScript Development Guide

**Nimo Platform - September 13, 2025**

## Overview

This guide covers the React 18.3.1 + TypeScript frontend implementation for the Nimo decentralized identity and proof of contribution platform. The frontend integrates with Cardano blockchain and MeTTa AI reasoning for autonomous verification.

## Technology Stack

### Core Framework
- **React 18.3.1** - Latest React with concurrent features
- **TypeScript 5.8.3** - Type-safe development
- **Vite 5.4.19** - Fast build tool and dev server

### UI & Styling
- **Shadcn/ui** - Modern component library built on Radix UI
- **Tailwind CSS 3.4.17** - Utility-first CSS framework
- **Radix UI** - Accessible, unstyled UI primitives
- **Lucide React** - Beautiful icon library

### State Management & Data
- **TanStack Query 5.83.0** - Powerful data synchronization
- **React Hook Form 7.61.1** - Performant forms with validation
- **Zod 3.25.76** - TypeScript-first schema validation
- **Context API** - React's built-in state management

### Testing & Quality
- **Vitest 1.6.1** - Fast unit testing framework
- **React Testing Library 14.3.1** - Component testing utilities
- **Playwright 1.55.0** - End-to-end testing
- **ESLint 9.32.0** - Code linting and formatting

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── ui/             # Shadcn/ui components
│   │   ├── forms/          # Form components
│   │   ├── layout/         # Layout components
│   │   └── pages/          # Page-specific components
│   ├── pages/              # Route components
│   │   ├── auth/           # Authentication pages
│   │   ├── dashboard/      # Dashboard pages
│   │   ├── profile/        # User profile pages
│   │   └── admin/          # Admin pages
│   ├── hooks/              # Custom React hooks
│   │   ├── useAuth.ts      # Authentication hook
│   │   ├── useWallet.ts    # Cardano wallet hook
│   │   └── useApi.ts       # API interaction hook
│   ├── lib/                # Utility libraries
│   │   ├── utils.ts        # General utilities
│   │   ├── api.ts          # API client
│   │   ├── validations.ts  # Zod schemas
│   │   └── constants.ts    # Application constants
│   ├── contexts/           # React contexts
│   │   ├── AuthContext.tsx # Authentication context
│   │   └── ThemeContext.tsx# Theme context
│   ├── types/              # TypeScript type definitions
│   │   ├── api.ts          # API response types
│   │   ├── user.ts         # User-related types
│   │   └── index.ts        # Type exports
│   ├── App.tsx             # Main application component
│   ├── main.tsx            # Application entry point
│   └── index.css           # Global styles
├── public/                 # Static assets
├── tests/                  # Test files
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── e2e/               # End-to-end tests
└── docs/                  # Component documentation
```

## Component Architecture

### Atomic Design Pattern

The frontend follows atomic design principles with Shadcn/ui components:

#### Atoms (Basic Components)
```typescript
// Button component using Shadcn/ui
import { Button } from "@/components/ui/button"

export const SubmitButton = ({ children, onClick }) => (
  <Button onClick={onClick} className="w-full">
    {children}
  </Button>
)
```

#### Molecules (Composite Components)
```typescript
// Form field molecule
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

export const FormField = ({ label, type, ...props }) => (
  <div className="space-y-2">
    <Label htmlFor={props.id}>{label}</Label>
    <Input type={type} {...props} />
  </div>
)
```

#### Organisms (Complex Components)
```typescript
// Login form organism
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { loginSchema } from "@/lib/validations"

export const LoginForm = () => {
  const form = useForm({
    resolver: zodResolver(loginSchema)
  })

  const onSubmit = (data) => {
    // Handle login
  }

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      <FormField
        label="Email"
        type="email"
        {...form.register("email")}
      />
      <FormField
        label="Password"
        type="password"
        {...form.register("password")}
      />
      <SubmitButton>Login</SubmitButton>
    </form>
  )
}
```

## State Management

### TanStack Query for Server State

```typescript
// API query hook
import { useQuery } from "@tanstack/react-query"

export const useContributions = (userId) => {
  return useQuery({
    queryKey: ["contributions", userId],
    queryFn: () => api.getContributions(userId),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Usage in component
const { data: contributions, isLoading } = useContributions(userId)
```

### Context API for Client State

```typescript
// Auth context
import { createContext, useContext, useState } from "react"

const AuthContext = createContext()

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  const login = async (credentials) => {
    const response = await api.login(credentials)
    setUser(response.user)
    setIsAuthenticated(true)
  }

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, login }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
```

## API Integration

### API Client Setup

```typescript
// lib/api.ts
import { QueryClient } from "@tanstack/react-query"

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 3,
      staleTime: 5 * 60 * 1000,
    },
  },
})

// API client with interceptors
class ApiClient {
  private baseURL = import.meta.env.VITE_API_URL

  async get(endpoint: string) {
    const response = await fetch(`${this.baseURL}${endpoint}`)
    return response.json()
  }

  async post(endpoint: string, data: any) {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
    return response.json()
  }
}

export const api = new ApiClient()
```

### Custom API Hooks

```typescript
// hooks/useApi.ts
import { useMutation, useQueryClient } from "@tanstack/react-query"

export const useCreateContribution = () => {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: (data) => api.post("/contributions", data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["contributions"] })
    },
  })
}
```

## Form Handling

### React Hook Form with Zod Validation

```typescript
// Validation schema
import { z } from "zod"

export const contributionSchema = z.object({
  title: z.string().min(1, "Title is required").max(100, "Title too long"),
  description: z.string().max(500, "Description too long"),
  category: z.enum(["coding", "design", "research", "other"]),
  evidence: z.array(z.string().url("Invalid URL")),
})

// Form component
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"

export const ContributionForm = () => {
  const form = useForm({
    resolver: zodResolver(contributionSchema),
  })

  const createContribution = useCreateContribution()

  const onSubmit = (data) => {
    createContribution.mutate(data)
  }

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      {/* Form fields with validation */}
    </form>
  )
}
```

## Cardano Integration

### Wallet Connection Hook

```typescript
// hooks/useWallet.ts
import { useState, useEffect } from "react"

export const useWallet = () => {
  const [wallet, setWallet] = useState(null)
  const [address, setAddress] = useState("")
  const [balance, setBalance] = useState(0)

  const connectWallet = async (walletName) => {
    // Cardano wallet connection logic
    const walletApi = await window.cardano[walletName].enable()
    const addresses = await walletApi.getUsedAddresses()
    setAddress(addresses[0])
    setWallet(walletApi)
  }

  return { wallet, address, balance, connectWallet }
}
```

### Transaction Handling

```typescript
// Transaction submission
const submitTransaction = async (tx) => {
  const signedTx = await wallet.signTx(tx)
  const txHash = await wallet.submitTx(signedTx)
  return txHash
}
```

## Testing Strategy

### Unit Testing with Vitest

```typescript
// Component test
import { render, screen } from "@testing-library/react"
import { expect, test } from "vitest"
import { Button } from "./Button"

test("renders button with text", () => {
  render(<Button>Click me</Button>)
  expect(screen.getByText("Click me")).toBeInTheDocument()
})
```

### Integration Testing

```typescript
// API integration test
import { render, waitFor } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { ContributionsList } from "./ContributionsList"

const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: { retry: false },
  },
})

test("loads and displays contributions", async () => {
  const queryClient = createTestQueryClient()
  render(
    <QueryClientProvider client={queryClient}>
      <ContributionsList />
    </QueryClientProvider>
  )

  await waitFor(() => {
    expect(screen.getByText("My Contribution")).toBeInTheDocument()
  })
})
```

### End-to-End Testing with Playwright

```typescript
// e2e test
import { test, expect } from "@playwright/test"

test("user can create contribution", async ({ page }) => {
  await page.goto("/dashboard")
  await page.click("text=New Contribution")
  await page.fill("[name=title]", "Test Contribution")
  await page.fill("[name=description]", "Test description")
  await page.click("text=Submit")

  await expect(page.locator("text=Contribution created")).toBeVisible()
})
```

## Performance Optimization

### Code Splitting

```typescript
// Lazy loading pages
import { lazy } from "react"

const Dashboard = lazy(() => import("./pages/Dashboard"))
const Profile = lazy(() => import("./pages/Profile"))

// Route configuration
<Route path="/dashboard" element={
  <Suspense fallback={<div>Loading...</div>}>
    <Dashboard />
  </Suspense>
} />
```

### Bundle Analysis

```bash
# Analyze bundle size
npm run build
npx vite-bundle-analyzer dist
```

### Image Optimization

```typescript
// Optimized image component
import { useState } from "react"

export const OptimizedImage = ({ src, alt, ...props }) => {
  const [loaded, setLoaded] = useState(false)

  return (
    <img
      src={src}
      alt={alt}
      loading="lazy"
      onLoad={() => setLoaded(true)}
      className={loaded ? "loaded" : "loading"}
      {...props}
    />
  )
}
```

## Security Best Practices

### Input Validation

```typescript
// Sanitize user inputs
import DOMPurify from "dompurify"

const sanitizeInput = (input: string) => {
  return DOMPurify.sanitize(input, { ALLOWED_TAGS: [] })
}
```

### Secure Token Storage

```typescript
// Use httpOnly cookies for sensitive tokens
// Avoid localStorage for auth tokens
const storeToken = (token: string) => {
  document.cookie = `auth-token=${token}; secure; httpOnly; sameSite=strict`
}
```

### CSRF Protection

```typescript
// Include CSRF token in requests
const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content')

const apiRequest = async (endpoint, data) => {
  return fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRF-Token": csrfToken,
    },
    body: JSON.stringify(data),
  })
}
```

## Development Workflow

### Development Server

```bash
# Start development server
npm run dev

# Start with host binding for mobile testing
npm run dev:host
```

### Code Quality

```bash
# Run linting
npm run lint

# Run tests
npm run test

# Run e2e tests
npm run test:e2e
```

### Build Process

```bash
# Production build
npm run build

# Preview production build
npm run preview
```

## Deployment

### Environment Configuration

```typescript
// Environment variables
const config = {
  apiUrl: import.meta.env.VITE_API_URL,
  cardanoNetwork: import.meta.env.VITE_CARDANO_NETWORK,
  enableAnalytics: import.meta.env.VITE_ENABLE_ANALYTICS === "true",
}
```

### Build Optimization

```typescript
// vite.config.ts
import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"

export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ["react", "react-dom"],
          ui: ["@radix-ui/react-dialog", "@radix-ui/react-dropdown-menu"],
          utils: ["zod", "date-fns"],
        },
      },
    },
  },
})
```

## Accessibility

### ARIA Labels and Roles

```typescript
// Accessible form
<form role="form" aria-labelledby="login-form">
  <h2 id="login-form">Login to your account</h2>
  <label htmlFor="email">Email address</label>
  <input
    id="email"
    type="email"
    aria-describedby="email-help"
    aria-invalid={errors.email ? "true" : "false"}
  />
  <div id="email-help">We'll use this to identify your account</div>
</form>
```

### Keyboard Navigation

```typescript
// Focus management
import { useEffect, useRef } from "react"

export const Modal = ({ isOpen, onClose, children }) => {
  const modalRef = useRef()

  useEffect(() => {
    if (isOpen) {
      modalRef.current.focus()
    }
  }, [isOpen])

  const handleKeyDown = (e) => {
    if (e.key === "Escape") {
      onClose()
    }
  }

  return (
    <div
      ref={modalRef}
      tabIndex={-1}
      onKeyDown={handleKeyDown}
      role="dialog"
      aria-modal="true"
    >
      {children}
    </div>
  )
}
```

## Conclusion

This React/TypeScript frontend provides a solid foundation for the Nimo platform with:

- **Modern Architecture**: React 18 + TypeScript + Vite
- **Performance**: Optimized with code splitting and lazy loading
- **Accessibility**: WCAG compliant with proper ARIA support
- **Testing**: Comprehensive unit, integration, and e2e testing
- **Security**: Input validation, CSRF protection, secure token handling
- **Scalability**: Modular component architecture with clear separation of concerns

The frontend integrates seamlessly with the Cardano blockchain and MeTTa AI system, providing users with a modern, secure, and performant experience for decentralized identity and reputation management.

---

**Last Updated:** September 13, 2025
**React Version:** 18.3.1
**TypeScript Version:** 5.8.3</content>
<parameter name="filePath">e:\Polymath Universata\Projects\Nimo\docs\development\react_typescript_guide.md