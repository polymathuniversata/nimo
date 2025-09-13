# Frontend Components Documentation

**Nimo Platform - React + TypeScript Components - September 13, 2025**

## Overview

This document provides detailed documentation for the custom React components used in the Nimo platform frontend. All components are built with React 18.3.1, TypeScript, and Shadcn/ui for consistent design and accessibility.

## Core Components

### IdentityNftCard

**File:** `frontend/src/components/IdentityNftCard.tsx`

A card component that displays a user's identity NFT with their profile information, token balance, and reputation metrics.

#### Props
```typescript
interface IdentityNftCardProps {
  userName?: string;           // User's display name
  userId?: string;             // Unique user identifier
  tokenBalance?: number;       // Current NIMO token balance
  verifiedContributions?: number; // Number of verified contributions
  reputation?: string;         // User's reputation level/title
}
```

#### Features
- **NFT Visual**: Displays identity NFT image with glow effects
- **Token Balance**: Shows current NIMO token holdings
- **Contribution Stats**: Displays verified contribution count
- **Reputation Badge**: Shows user's reputation level
- **Responsive Design**: Adapts to mobile and desktop layouts
- **Accessibility**: Proper ARIA labels and keyboard navigation

#### Usage
```tsx
import { IdentityNftCard } from '@/components/IdentityNftCard';

<IdentityNftCard
  userName="Kwame Asante"
  userId="user-123"
  tokenBalance={320}
  verifiedContributions={12}
  reputation="Community Builder"
/>
```

---

### ContributionCard

**File:** `frontend/src/components/ContributionCard.tsx`

Displays individual contributions with verification status, evidence links, and reward information.

#### Props
```typescript
interface ContributionCardProps {
  id: string;
  title: string;
  description: string;
  category: string;
  status: 'pending' | 'verified' | 'rejected';
  evidenceUrls: string[];
  tokenReward?: number;
  adaReward?: number;
  submittedAt: Date;
  verifiedAt?: Date;
}
```

#### Features
- **Status Indicators**: Visual status badges (pending/verified/rejected)
- **Evidence Links**: Clickable links to supporting evidence
- **Reward Display**: Shows token and ADA rewards earned
- **Category Tags**: Color-coded contribution categories
- **Timestamp Information**: Submission and verification dates
- **Interactive Elements**: Expandable details and action buttons

#### Usage
```tsx
import { ContributionCard } from '@/components/ContributionCard';

<ContributionCard
  id="contrib-123"
  title="KRNL Hackathon Project"
  description="Built a decentralized identity system"
  category="coding"
  status="verified"
  evidenceUrls={["https://github.com/user/project"]}
  tokenReward={75}
  adaReward={1.25}
  submittedAt={new Date('2025-09-01')}
/>
```

---

### ImpactBondCard

**File:** `frontend/src/components/ImpactBondCard.tsx`

Card component for displaying impact bond opportunities with investment details and progress tracking.

#### Props
```typescript
interface ImpactBondCardProps {
  id: string;
  title: string;
  description: string;
  targetAmount: number;
  currentAmount: number;
  minimumInvestment: number;
  expectedReturn: number;
  duration: number; // in months
  category: string;
  location: string;
  status: 'active' | 'funded' | 'completed';
  deadline: Date;
}
```

#### Features
- **Progress Visualization**: Progress bar showing funding status
- **Investment Details**: Target amount, minimum investment, expected returns
- **Time Tracking**: Days remaining until deadline
- **Category and Location**: Tagged for easy filtering
- **Status Badges**: Active/funded/completed status indicators
- **Responsive Layout**: Optimized for all screen sizes

#### Usage
```tsx
import { ImpactBondCard } from '@/components/ImpactBondCard';

<ImpactBondCard
  id="bond-456"
  title="Solar Power for Rural School"
  description="Install solar panels for clean energy"
  targetAmount={50000}
  currentAmount={32000}
  minimumInvestment={100}
  expectedReturn={8.5}
  duration={24}
  category="renewable-energy"
  location="Kenya"
  status="active"
  deadline={new Date('2025-12-31')}
/>
```

---

### SubmitContribution

**File:** `frontend/src/components/SubmitContribution.tsx`

Form component for submitting new contributions with evidence upload and validation.

#### Features
- **Multi-step Form**: Guided contribution submission process
- **File Upload**: Support for multiple evidence types (GitHub, documents, images)
- **Category Selection**: Dropdown with predefined contribution categories
- **Real-time Validation**: Form validation with error messages
- **Evidence Preview**: Preview uploaded files and links
- **Progress Tracking**: Visual progress indicator
- **Accessibility**: Full keyboard navigation and screen reader support

#### Form Fields
- **Title**: Contribution title (required, 1-100 characters)
- **Description**: Detailed description (required, max 500 characters)
- **Category**: Contribution category selection
- **Evidence**: Multiple evidence uploads/links
- **Tags**: Optional tags for better categorization

#### Validation Rules
```typescript
const contributionSchema = z.object({
  title: z.string().min(1, "Title is required").max(100, "Title too long"),
  description: z.string().max(500, "Description too long"),
  category: z.enum(["coding", "design", "research", "education", "activism", "other"]),
  evidenceUrls: z.array(z.string().url("Invalid URL")).min(1, "At least one evidence required"),
  tags: z.array(z.string()).optional()
});
```

#### Usage
```tsx
import { SubmitContribution } from '@/components/SubmitContribution';

function ContributionPage() {
  return (
    <div className="container mx-auto py-8">
      <SubmitContribution />
    </div>
  );
}
```

---

### Navbar

**File:** `frontend/src/components/Navbar.tsx`

Main navigation component with authentication state, wallet connection, and responsive design.

#### Features
- **Authentication State**: Login/logout buttons based on auth status
- **Wallet Integration**: Cardano wallet connection status
- **Responsive Navigation**: Mobile-friendly hamburger menu
- **Active Link Highlighting**: Current page indication
- **Dropdown Menus**: User menu with profile options
- **Accessibility**: Proper ARIA labels and keyboard navigation

#### Navigation Items
- **Home**: Landing page
- **Dashboard**: User dashboard (authenticated only)
- **Contributions**: Contribution management
- **Bonds**: Impact bond marketplace
- **Profile**: User profile settings

#### Usage
```tsx
import { Navbar } from '@/components/Navbar';

function AppLayout({ children }) {
  return (
    <div className="min-h-screen">
      <Navbar />
      <main>{children}</main>
    </div>
  );
}
```

---

### ProtectedRoute

**File:** `frontend/src/components/ProtectedRoute.tsx`

Route guard component that protects authenticated routes and handles redirects.

#### Props
```typescript
interface ProtectedRouteProps {
  children: React.ReactNode;
  requireAuth?: boolean;
  requireKyc?: boolean;
  redirectTo?: string;
}
```

#### Features
- **Authentication Check**: Redirects unauthenticated users
- **KYC Verification**: Optional KYC requirement for certain routes
- **Loading States**: Shows loading spinner during auth checks
- **Custom Redirects**: Configurable redirect destinations
- **Error Handling**: Graceful error handling for auth failures

#### Usage
```tsx
import { ProtectedRoute } from '@/components/ProtectedRoute';

<Route path="/dashboard" element={
  <ProtectedRoute requireAuth={true} requireKyc={true}>
    <DashboardPage />
  </ProtectedRoute>
} />
```

---

### ErrorBoundary

**File:** `frontend/src/components/ErrorBoundary.tsx`

React error boundary component for graceful error handling and user feedback.

#### Features
- **Error Catching**: Catches JavaScript errors in component tree
- **Fallback UI**: User-friendly error display
- **Error Reporting**: Optional error reporting to monitoring service
- **Recovery Options**: Retry button to attempt recovery
- **Development Mode**: Detailed error information in development

#### Usage
```tsx
import { ErrorBoundary } from '@/components/ErrorBoundary';

function App() {
  return (
    <ErrorBoundary>
      <AppContent />
    </ErrorBoundary>
  );
}
```

---

### ThemeToggle

**File:** `frontend/src/components/ThemeToggle.tsx`

Theme switching component that toggles between light and dark modes.

#### Features
- **Theme Persistence**: Saves theme preference to localStorage
- **System Preference**: Respects user's system theme preference
- **Smooth Transitions**: Animated theme transitions
- **Icon Indicators**: Visual indicators for current theme
- **Accessibility**: Proper ARIA labels and keyboard support

#### Usage
```tsx
import { ThemeToggle } from '@/components/ThemeToggle';

<ThemeToggle />
```

---

## Page Components

### LandingPage

**File:** `frontend/src/pages/LandingPage.tsx`

Main landing page with hero section, features, and call-to-action.

#### Sections
- **Hero**: Main value proposition and CTA
- **Features**: Key platform features showcase
- **How It Works**: Step-by-step user journey
- **Statistics**: Platform metrics and impact
- **Testimonials**: User success stories
- **Footer**: Links and contact information

### Dashboard Pages

#### ContributorDashboard
**File:** `frontend/src/pages/ContributorDashboard.tsx`

Dashboard for individual contributors showing their contributions, rewards, and progress.

#### OrganizationDashboard
**File:** `frontend/src/pages/OrganizationDashboard.tsx`

Dashboard for organizations managing multiple contributors and projects.

#### DiasporaDashboard
**File:** `frontend/src/pages/DiasporaDashboard.tsx`

Dashboard for diaspora investors interested in impact bonds and community projects.

### Authentication Pages

#### LoginPage
**File:** `frontend/src/pages/LoginPage.tsx`

User login page with email/password and wallet authentication options.

#### RegisterPage
**File:** `frontend/src/pages/RegisterPage.tsx`

Multi-step registration page with KYC document upload and verification.

---

## Custom Hooks

### useAuth

**File:** `frontend/src/hooks/useAuth.ts`

Authentication hook providing login, logout, and user state management.

```typescript
const { user, isAuthenticated, login, logout, loading } = useAuth();
```

### useWallet

**File:** `frontend/src/hooks/useWallet.ts`

Cardano wallet connection and management hook.

```typescript
const { wallet, address, balance, connectWallet, disconnectWallet } = useWallet();
```

### useApi

**File:** `frontend/src/hooks/useApi.ts`

API interaction hook with error handling and loading states.

```typescript
const { data, error, loading, refetch } = useApi('/api/contributions');
```

---

## Utility Functions

### API Client

**File:** `frontend/src/lib/api.ts`

Centralized API client with request/response interceptors and error handling.

### Form Validation

**File:** `frontend/src/lib/validations.ts`

Zod schemas for form validation across the application.

### Constants

**File:** `frontend/src/lib/constants.ts`

Application-wide constants and configuration values.

---

## Styling and Theming

### CSS Variables

The application uses CSS custom properties for consistent theming:

```css
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --primary: 221.2 83.2% 53.3%;
  --secondary: 210 40% 96%;
  /* ... more variables */
}
```

### Tailwind Configuration

**File:** `frontend/tailwind.config.ts`

Custom Tailwind configuration with design tokens and component variants.

### Shadcn/ui Theme

**File:** `frontend/src/lib/theme.ts`

Theme configuration for Shadcn/ui components with custom colors and typography.

---

## Performance Considerations

### Code Splitting
- Route-based code splitting for faster initial load
- Component lazy loading for non-critical components
- Bundle analysis and optimization

### Image Optimization
- Lazy loading for images below the fold
- WebP format with fallbacks
- Responsive image sizing

### Caching Strategy
- API response caching with React Query
- Static asset caching with appropriate headers
- Service worker for offline functionality

---

## Accessibility Features

### ARIA Support
- Proper ARIA labels on all interactive elements
- Screen reader announcements for dynamic content
- Keyboard navigation support throughout

### Focus Management
- Visible focus indicators
- Logical tab order
- Focus trapping in modals

### Color and Contrast
- WCAG AA compliance for color contrast
- Support for high contrast mode
- Reduced motion preferences respected

---

## Testing

### Component Testing
```typescript
import { render, screen } from '@testing-library/react';
import { IdentityNftCard } from './IdentityNftCard';

test('displays user information correctly', () => {
  render(<IdentityNftCard userName="Test User" />);
  expect(screen.getByText('Test User')).toBeInTheDocument();
});
```

### Integration Testing
```typescript
import { render, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ContributionsPage } from './ContributionsPage';

test('loads contributions from API', async () => {
  const queryClient = new QueryClient();
  render(
    <QueryClientProvider client={queryClient}>
      <ContributionsPage />
    </QueryClientProvider>
  );

  await waitFor(() => {
    expect(screen.getByText('My Contribution')).toBeInTheDocument();
  });
});
```

---

## Conclusion

The Nimo frontend components provide a comprehensive, accessible, and performant user interface for the decentralized identity and contribution platform. Built with modern React patterns and TypeScript, the components ensure type safety, maintainability, and excellent user experience.

**Key Characteristics:**
- **Modular Design**: Reusable components with clear interfaces
- **Type Safety**: Full TypeScript coverage with proper typing
- **Accessibility**: WCAG AA compliant with comprehensive ARIA support
- **Performance**: Optimized with code splitting and lazy loading
- **Consistency**: Unified design system with Shadcn/ui
- **Testing**: Comprehensive test coverage for reliability

For more detailed information about specific components or implementation details, refer to the individual component files and their inline documentation.</content>
<parameter name="filePath">e:\Polymath Universata\Projects\Nimo\docs\frontend\components-documentation.md