import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { AlertTriangle, RefreshCw, Home } from 'lucide-react';

interface ErrorBoundaryState {
  hasError: boolean;
  error?: Error;
  errorInfo?: React.ErrorInfo;
}

interface ErrorBoundaryProps {
  children: React.ReactNode;
  fallback?: React.ComponentType<{ error?: Error; resetError: () => void }>;
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('Error caught by ErrorBoundary:', error, errorInfo);

    // Store error details for debugging
    this.setState({ errorInfo });

    // Call optional error handler
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // In production, you might want to send this to an error reporting service
    // Example: Sentry, LogRocket, etc.
    if (import.meta.env.PROD) {
      // TODO: Send to error monitoring service
      // reportError(error, errorInfo);
    }
  }

  resetError = () => {
    this.setState({ hasError: false, error: undefined, errorInfo: undefined });
  };

  render() {
    if (this.state.hasError) {
      // Use custom fallback if provided
      if (this.props.fallback) {
        const FallbackComponent = this.props.fallback;
        return <FallbackComponent error={this.state.error} resetError={this.resetError} />;
      }

      // Default error UI
      return (
        <div className="min-h-screen bg-background flex items-center justify-center p-4">
          <Card className="w-full max-w-md shadow-lg">
            <CardHeader className="text-center">
              <div className="w-12 h-12 rounded-full bg-destructive/10 flex items-center justify-center mx-auto mb-4">
                <AlertTriangle className="w-6 h-6 text-destructive" />
              </div>
              <CardTitle className="text-xl">Something went wrong</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-muted-foreground text-center text-sm">
                We encountered an unexpected error. This has been reported to our team.
              </p>

              {import.meta.env.DEV && this.state.error && (
                <div className="bg-muted p-3 rounded-md">
                  <p className="text-xs font-mono text-destructive">
                    {this.state.error.message}
                  </p>
                </div>
              )}

              <div className="flex gap-2">
                <Button
                  onClick={this.resetError}
                  className="flex-1"
                  variant="outline"
                >
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Try Again
                </Button>
                <Button
                  onClick={() => window.location.href = '/'}
                  className="flex-1"
                >
                  <Home className="w-4 h-4 mr-2" />
                  Go Home
                </Button>
              </div>

              <div className="text-center">
                <p className="text-xs text-muted-foreground">
                  If this problem persists, please contact support.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      );
    }

    return this.props.children;
  }
}

// Convenience wrapper for route-level error boundaries
export const RouteErrorBoundary: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ErrorBoundary
    onError={(error, errorInfo) => {
      // Log route-specific errors
      console.error('Route error:', error, errorInfo);
    }}
  >
    {children}
  </ErrorBoundary>
);

// Convenience wrapper for component-level error boundaries
export const ComponentErrorBoundary: React.FC<{
  children: React.ReactNode;
  name?: string;
}> = ({ children, name }) => (
  <ErrorBoundary
    onError={(error, errorInfo) => {
      console.error(`Component error${name ? ` in ${name}` : ''}:`, error, errorInfo);
    }}
    fallback={({ error, resetError }) => (
      <Card className="p-4 border-destructive/20">
        <div className="flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-destructive flex-shrink-0" />
          <div className="flex-1">
            <p className="font-medium text-sm">Component Error</p>
            <p className="text-xs text-muted-foreground">
              {name && `${name} failed to load. `}
              {error?.message || 'An unexpected error occurred.'}
            </p>
          </div>
          <Button size="sm" variant="outline" onClick={resetError}>
            Retry
          </Button>
        </div>
      </Card>
    )}
  >
    {children}
  </ErrorBoundary>
);

// Hook for handling async errors in functional components
// eslint-disable-next-line react-refresh/only-export-components
export const useErrorHandler = () => {
  return React.useCallback((error: Error) => {
    console.error('Async error:', error);
    // In a real app, you might want to show a toast or modal here
    // For now, we'll just log it
  }, []);
};