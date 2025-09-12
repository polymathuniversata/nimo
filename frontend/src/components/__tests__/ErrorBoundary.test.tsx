import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ErrorBoundary } from '../ErrorBoundary';

// Mock console.error to avoid noise in test output
const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

// Component that throws an error
const ErrorComponent = () => {
  throw new Error('Test error');
};

// Component that doesn't throw
const SafeComponent = () => <div>Safe component</div>;

describe('ErrorBoundary', () => {
  beforeEach(() => {
    consoleErrorSpy.mockClear();
  });

  afterEach(() => {
    consoleErrorSpy.mockRestore();
  });

  it('should render children when no error occurs', () => {
    render(
      <ErrorBoundary>
        <SafeComponent />
      </ErrorBoundary>
    );

    expect(screen.getByText('Safe component')).toBeInTheDocument();
  });

  it('should render error UI when an error occurs', () => {
    render(
      <ErrorBoundary>
        <ErrorComponent />
      </ErrorBoundary>
    );

    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    expect(screen.getByText('Try Again')).toBeInTheDocument();
    expect(screen.getByText('Go Home')).toBeInTheDocument();
  });

  it('should show error details in development mode', () => {
    // Mock development environment
    const originalEnv = import.meta.env.DEV;
    import.meta.env.DEV = true;

    render(
      <ErrorBoundary>
        <ErrorComponent />
      </ErrorBoundary>
    );

    expect(screen.getByText('Test error')).toBeInTheDocument();

    // Restore original environment
    import.meta.env.DEV = originalEnv;
  });

  it('should not show error details in production mode', () => {
    // Mock production environment
    const originalEnv = import.meta.env.PROD;
    import.meta.env.PROD = true;

    render(
      <ErrorBoundary>
        <ErrorComponent />
      </ErrorBoundary>
    );

    expect(screen.queryByText('Test error')).not.toBeInTheDocument();

    // Restore original environment
    import.meta.env.PROD = originalEnv;
  });

  it('should call onError callback when provided', () => {
    const onErrorMock = vi.fn();

    render(
      <ErrorBoundary onError={onErrorMock}>
        <ErrorComponent />
      </ErrorBoundary>
    );

    expect(onErrorMock).toHaveBeenCalledWith(
      expect.any(Error),
      expect.any(Object)
    );
  });

  it('should reset error state when Try Again is clicked', () => {
    const { rerender } = render(
      <ErrorBoundary>
        <ErrorComponent />
      </ErrorBoundary>
    );

    expect(screen.getByText('Something went wrong')).toBeInTheDocument();

    // Click Try Again
    fireEvent.click(screen.getByText('Try Again'));

    // Rerender with safe component
    rerender(
      <ErrorBoundary>
        <SafeComponent />
      </ErrorBoundary>
    );

    expect(screen.getByText('Safe component')).toBeInTheDocument();
  });

  it('should render custom fallback when provided', () => {
    const CustomFallback = ({ error, resetError }: { error?: Error; resetError: () => void }) => (
      <div>
        <p>Custom Error: {error?.message}</p>
        <button onClick={resetError}>Reset</button>
      </div>
    );

    render(
      <ErrorBoundary fallback={CustomFallback}>
        <ErrorComponent />
      </ErrorBoundary>
    );

    expect(screen.getByText('Custom Error: Test error')).toBeInTheDocument();
    expect(screen.getByText('Reset')).toBeInTheDocument();
  });

  it('should log errors to console', () => {
    render(
      <ErrorBoundary>
        <ErrorComponent />
      </ErrorBoundary>
    );

    expect(consoleErrorSpy).toHaveBeenCalledWith(
      'Error caught by ErrorBoundary:',
      expect.any(Error),
      expect.any(Object)
    );
  });
});