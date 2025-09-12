import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ProtectedRoute } from '../ProtectedRoute';

// Mock useAuth hook
const mockUseAuth = vi.fn();
vi.mock('@/hooks/useAuth', () => ({
  useAuth: mockUseAuth,
}));

// Test wrapper component
const TestWrapper = ({ children }: { children: React.ReactNode }) => (
  <BrowserRouter>
    {children}
  </BrowserRouter>
);

// Test content component
const TestContent = () => React.createElement('div', { 'data-testid': 'protected-content' }, 'Protected Content');

describe('ProtectedRoute', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Loading State', () => {
    it('should show loading spinner when authentication is loading', () => {
      mockUseAuth.mockReturnValue({
        user: null,
        isAuthenticated: false,
        isLoading: true,
        walletConnected: false,
        logout: vi.fn(),
      });

      render(
        <TestWrapper>
          <ProtectedRoute>
            <TestContent />
          </ProtectedRoute>
        </TestWrapper>
      );

      expect(screen.getByText('Loading...')).toBeInTheDocument();
    });
  });

  describe('Unauthenticated State', () => {
    beforeEach(() => {
      mockUseAuth.mockReturnValue({
        user: null,
        isAuthenticated: false,
        isLoading: false,
        walletConnected: false,
        logout: vi.fn(),
      });
    });

    it('should not render protected content when not authenticated', () => {
      render(
        <TestWrapper>
          <ProtectedRoute>
            <TestContent />
          </ProtectedRoute>
        </TestWrapper>
      );

      expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument();
    });
  });

  describe('Authenticated State - No Requirements', () => {
    beforeEach(() => {
      mockUseAuth.mockReturnValue({
        user: {
          id: '1',
          email: 'test@example.com',
          name: 'Test User',
          walletAddress: null,
          authMethod: 'traditional',
          isKycVerified: false,
          kycStatus: 'not_started',
          reputationScore: 85,
          tokenBalance: 1000,
          createdAt: '2024-01-01',
          skills: ['coding'],
          location: 'Accra',
          bio: 'Test bio',
        },
        isAuthenticated: true,
        isLoading: false,
        walletConnected: false,
        logout: vi.fn(),
      });
    });

    it('should render protected content when authenticated with no requirements', () => {
      render(
        <TestWrapper>
          <ProtectedRoute>
            <TestContent />
          </ProtectedRoute>
        </TestWrapper>
      );

      expect(screen.getByTestId('protected-content')).toBeInTheDocument();
    });
  });
});