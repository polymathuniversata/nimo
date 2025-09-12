import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Shield,
  Lock,
  CheckCircle,
  Clock,
  XCircle,
  Sparkles,
  ArrowRight
} from 'lucide-react';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requireKyc?: boolean;
  requireWallet?: boolean;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  requireKyc = false,
  requireWallet = false,
}) => {
  const { user, isAuthenticated, isLoading, walletConnected } = useAuth();
  const location = useLocation();

  // Show loading spinner while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary/5 via-background to-secondary/5 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center mx-auto mb-4">
            <Sparkles className="w-6 h-6 text-white animate-spin" />
          </div>
          <p className="text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check wallet requirement
  if (requireWallet && !walletConnected) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary/5 via-background to-secondary/5 flex items-center justify-center p-4">
        <Card className="w-full max-w-md shadow-lg border-0 bg-white/95 backdrop-blur-sm">
          <CardHeader className="text-center">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center mx-auto mb-4">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <CardTitle className="text-xl">Wallet Required</CardTitle>
            <CardDescription>
              You need to connect your Cardano wallet to access this feature
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Alert>
              <Shield className="h-4 w-4" />
              <AlertDescription>
                This feature requires a connected Cardano wallet for security and verification purposes.
              </AlertDescription>
            </Alert>
            <Button className="w-full" asChild>
              <a href="/login">Connect Wallet</a>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  // Check KYC requirement
  if (requireKyc && user && user.kycStatus !== 'approved') {
    const getKycStatusInfo = () => {
      switch (user.kycStatus) {
        case 'pending':
          return {
            icon: <Clock className="w-5 h-5 text-yellow-500" />,
            title: 'KYC Verification Pending',
            description: 'Your KYC verification is being reviewed. This usually takes 24-48 hours.',
            actionText: 'Check Status',
          };
        case 'rejected':
          return {
            icon: <XCircle className="w-5 h-5 text-red-500" />,
            title: 'KYC Verification Rejected',
            description: 'Your KYC verification was not approved. Please contact support for assistance.',
            actionText: 'Contact Support',
          };
        default:
          return {
            icon: <Shield className="w-5 h-5 text-primary" />,
            title: 'KYC Verification Required',
            description: 'Complete your KYC verification to access this feature.',
            actionText: 'Start KYC',
          };
      }
    };

    const kycInfo = getKycStatusInfo();

    return (
      <div className="min-h-screen bg-gradient-to-br from-primary/5 via-background to-secondary/5 flex items-center justify-center p-4">
        <Card className="w-full max-w-md shadow-lg border-0 bg-white/95 backdrop-blur-sm">
          <CardHeader className="text-center">
            <div className="flex items-center justify-center w-12 h-12 rounded-xl bg-muted mx-auto mb-4">
              {kycInfo.icon}
            </div>
            <CardTitle className="text-xl">{kycInfo.title}</CardTitle>
            <CardDescription>{kycInfo.description}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-center space-x-4">
              <Badge variant="outline" className="flex items-center space-x-2">
                <Lock className="w-3 h-3" />
                <span>Verification Required</span>
              </Badge>
            </div>

            <Alert>
              <Shield className="h-4 w-4" />
              <AlertDescription>
                KYC verification ensures the security and integrity of the Nimo platform.
                All users must complete this process before accessing advanced features.
              </AlertDescription>
            </Alert>

            <div className="space-y-2">
              {user.kycStatus === 'pending' && (
                <Button variant="outline" className="w-full">
                  {kycInfo.actionText}
                </Button>
              )}

              {user.kycStatus === 'rejected' && (
                <Button variant="outline" className="w-full">
                  {kycInfo.actionText}
                </Button>
              )}

              {(!user.kycStatus || user.kycStatus === 'not_started') && (
                <Button className="w-full">
                  {kycInfo.actionText}
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              )}

              <Button variant="ghost" className="w-full" asChild>
                <a href="/dashboard/user">Go to Dashboard</a>
              </Button>
            </div>

            <div className="text-center">
              <p className="text-xs text-muted-foreground">
                Need help? Contact our support team
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  // All checks passed, render the protected content
  return <>{children}</>;
};

// Convenience wrapper for routes that require full verification
export const VerifiedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ProtectedRoute requireKyc={true} requireWallet={true}>
    {children}
  </ProtectedRoute>
);

// Convenience wrapper for routes that require wallet but not necessarily KYC
export const WalletRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ProtectedRoute requireWallet={true}>
    {children}
  </ProtectedRoute>
);