import React, { useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useWallet } from '@/hooks/useWallet';
import { useToast } from '@/hooks/use-toast';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Loader2, Wallet, Mail, Lock, User, AlertTriangle } from 'lucide-react';

interface AuthModalProps {
  children: React.ReactNode;
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
}

export const AuthModal: React.FC<AuthModalProps> = ({ children, open, onOpenChange }) => {
  const { login, register, isLoading, error, clearError } = useAuth();
  const { 
    connectWallet, 
    signMessage, 
    switchToBaseNetwork,
    isConnected: isWalletConnected, 
    address: walletAddress, 
    isOnCorrectNetwork,
    isLoading: isWalletLoading,
    error: walletError,
    clearError: clearWalletError
  } = useWallet();
  const { toast } = useToast();
  const [isOpen, setIsOpen] = useState(open || false);
  const [activeTab, setActiveTab] = useState('login');
  const [isAuthenticating, setIsAuthenticating] = useState(false);

  // Login form state
  const [loginData, setLoginData] = useState({
    email: '',
    password: '',
    auth_method: 'traditional' as 'traditional' | 'wallet',
    wallet_address: '',
    signature: '',
    message: ''
  });

  // Register form state
  const [registerData, setRegisterData] = useState({
    email: '',
    password: '',
    name: '',
    auth_method: 'traditional' as 'traditional' | 'wallet',
    wallet_address: '',
    signature: '',
    message: ''
  });

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();

    try {
      await login(loginData);
      toast({
        title: "Login Successful!",
        description: "Welcome back to Nimo Platform.",
      });
      setIsOpen(false);
      // Reset form
      setLoginData({
        email: '',
        password: '',
        auth_method: 'traditional',
        wallet_address: '',
        signature: '',
        message: ''
      });
    } catch (err) {
      // Error is handled by useAuth and displayed in the modal
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();

    try {
      await register(registerData);
      toast({
        title: "Registration Successful!",
        description: "Welcome to Nimo Platform! You can now submit contributions.",
      });
      setIsOpen(false);
      // Reset form
      setRegisterData({
        email: '',
        password: '',
        name: '',
        auth_method: 'traditional',
        wallet_address: '',
        signature: '',
        message: ''
      });
    } catch (err) {
      // Error is handled by useAuth and displayed in the modal
    }
  };

  const handleWalletConnect = async () => {
    clearError();
    clearWalletError();
    
    if (!isWalletConnected) {
      await connectWallet();
      return;
    }
    
    // If connected but on wrong network, switch networks
    if (!isOnCorrectNetwork()) {
      const switched = await switchToBaseNetwork();
      if (!switched) return;
    }
    
    // Proceed with wallet authentication
    await handleWalletAuth();
  };

  const handleWalletAuth = async () => {
    if (!isWalletConnected || !walletAddress) {
      toast({
        title: "Wallet Not Connected",
        description: "Please connect your wallet first.",
        variant: "destructive",
      });
      return;
    }

    if (!isOnCorrectNetwork()) {
      toast({
        title: "Wrong Network",
        description: "Please switch to Base network to continue.",
        variant: "destructive",
      });
      return;
    }

    setIsAuthenticating(true);
    
    try {
      // Sign authentication message
      const signatureData = await signMessage();
      if (!signatureData) {
        setIsAuthenticating(false);
        return;
      }

      // Prepare authentication data
      const authData = {
        auth_method: 'wallet' as const,
        wallet_address: walletAddress,
        signature: signatureData.signature,
        message: signatureData.message,
      };

      // Try to login first
      if (activeTab === 'login') {
        await login(authData);
      } else {
        // Register requires additional information
        if (!registerData.name) {
          toast({
            title: "Name Required",
            description: "Please enter your name for registration.",
            variant: "destructive",
          });
          setIsAuthenticating(false);
          return;
        }

        await register({
          ...authData,
          name: registerData.name,
          email: registerData.email || `${walletAddress.toLowerCase()}@nimo.platform`,
          password: '', // Not required for wallet auth
        });
      }

      toast({
        title: `${activeTab === 'login' ? 'Login' : 'Registration'} Successful!`,
        description: `Welcome to Nimo Platform! Your wallet ${walletAddress.slice(0, 6)}...${walletAddress.slice(-4)} is now connected.`,
      });
      
      setIsOpen(false);
      resetForms();
    } catch (err) {
      console.error('Wallet authentication failed:', err);
      // Error handling is done by the auth hooks
    } finally {
      setIsAuthenticating(false);
    }
  };

  const resetForms = () => {
    setLoginData({
      email: '',
      password: '',
      auth_method: 'traditional',
      wallet_address: '',
      signature: '',
      message: ''
    });
    setRegisterData({
      email: '',
      password: '',
      name: '',
      auth_method: 'traditional',
      wallet_address: '',
      signature: '',
      message: ''
    });
  };

  return (
    <Dialog open={open !== undefined ? open : isOpen} onOpenChange={onOpenChange !== undefined ? onOpenChange : setIsOpen}>
      <DialogTrigger asChild>
        {children}
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="text-center text-2xl font-bold">
            Welcome to Nimo
          </DialogTitle>
        </DialogHeader>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="login">Sign In</TabsTrigger>
            <TabsTrigger value="register">Sign Up</TabsTrigger>
          </TabsList>

          <TabsContent value="login" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Sign In</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Network Warning */}
                {isWalletConnected && !isOnCorrectNetwork() && (
                  <div className="flex items-center gap-2 p-3 text-sm text-amber-600 bg-amber-50 rounded-md border border-amber-200">
                    <AlertTriangle className="w-4 h-4" />
                    <span>Please switch to Base network to continue</span>
                  </div>
                )}

                {/* Wallet Connection Status */}
                {isWalletConnected && walletAddress && (
                  <div className="p-3 bg-green-50 border border-green-200 rounded-md">
                    <div className="flex items-center gap-2 text-sm text-green-700">
                      <Wallet className="w-4 h-4" />
                      <span>Connected: {walletAddress.slice(0, 6)}...{walletAddress.slice(-4)}</span>
                    </div>
                  </div>
                )}

                <Button
                  variant="outline"
                  className="w-full"
                  onClick={handleWalletConnect}
                  disabled={isLoading || isWalletLoading || isAuthenticating}
                >
                  {isWalletLoading || isAuthenticating ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      {isWalletLoading ? 'Connecting...' : 'Authenticating...'}
                    </>
                  ) : isWalletConnected ? (
                    !isOnCorrectNetwork() ? (
                      <>
                        <AlertTriangle className="w-4 h-4 mr-2" />
                        Switch to Base Network
                      </>
                    ) : (
                      <>
                        <Wallet className="w-4 h-4 mr-2" />
                        Sign In with Wallet
                      </>
                    )
                  ) : (
                    <>
                      <Wallet className="w-4 h-4 mr-2" />
                      Connect Wallet
                    </>
                  )}
                </Button>

                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <span className="w-full border-t" />
                  </div>
                  <div className="relative flex justify-center text-xs uppercase">
                    <span className="bg-background px-2 text-muted-foreground">Or continue with</span>
                  </div>
                </div>

                <form onSubmit={handleLogin} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="login-email">Email</Label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="login-email"
                        type="email"
                        placeholder="Enter your email"
                        value={loginData.email}
                        onChange={(e) => setLoginData({...loginData, email: e.target.value})}
                        className="pl-10"
                        required
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="login-password">Password</Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="login-password"
                        type="password"
                        placeholder="Enter your password"
                        value={loginData.password}
                        onChange={(e) => setLoginData({...loginData, password: e.target.value})}
                        className="pl-10"
                        required
                      />
                    </div>
                  </div>

                  {(error || walletError) && (
                    <div className="p-3 text-sm text-destructive bg-destructive/10 rounded-md">
                      {error || walletError}
                    </div>
                  )}

                  <Button type="submit" className="w-full" disabled={isLoading || isAuthenticating}>
                    {isLoading || isAuthenticating ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Signing In...
                      </>
                    ) : (
                      'Sign In'
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="register" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Create Account</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Network Warning */}
                {isWalletConnected && !isOnCorrectNetwork() && (
                  <div className="flex items-center gap-2 p-3 text-sm text-amber-600 bg-amber-50 rounded-md border border-amber-200">
                    <AlertTriangle className="w-4 h-4" />
                    <span>Please switch to Base network to continue</span>
                  </div>
                )}

                {/* Wallet Connection Status */}
                {isWalletConnected && walletAddress && (
                  <div className="p-3 bg-green-50 border border-green-200 rounded-md">
                    <div className="flex items-center gap-2 text-sm text-green-700">
                      <Wallet className="w-4 h-4" />
                      <span>Connected: {walletAddress.slice(0, 6)}...{walletAddress.slice(-4)}</span>
                    </div>
                  </div>
                )}

                <Button
                  variant="outline"
                  className="w-full"
                  onClick={handleWalletConnect}
                  disabled={isLoading || isWalletLoading || isAuthenticating}
                >
                  {isWalletLoading || isAuthenticating ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      {isWalletLoading ? 'Connecting...' : 'Authenticating...'}
                    </>
                  ) : isWalletConnected ? (
                    !isOnCorrectNetwork() ? (
                      <>
                        <AlertTriangle className="w-4 h-4 mr-2" />
                        Switch to Base Network
                      </>
                    ) : (
                      <>
                        <Wallet className="w-4 h-4 mr-2" />
                        Create Account with Wallet
                      </>
                    )
                  ) : (
                    <>
                      <Wallet className="w-4 h-4 mr-2" />
                      Connect Wallet
                    </>
                  )}
                </Button>

                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <span className="w-full border-t" />
                  </div>
                  <div className="relative flex justify-center text-xs uppercase">
                    <span className="bg-background px-2 text-muted-foreground">Or continue with</span>
                  </div>
                </div>

                <form onSubmit={handleRegister} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="register-name">Full Name</Label>
                    <div className="relative">
                      <User className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="register-name"
                        type="text"
                        placeholder="Enter your full name"
                        value={registerData.name}
                        onChange={(e) => setRegisterData({...registerData, name: e.target.value})}
                        className="pl-10"
                        required
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="register-email">Email</Label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="register-email"
                        type="email"
                        placeholder="Enter your email"
                        value={registerData.email}
                        onChange={(e) => setRegisterData({...registerData, email: e.target.value})}
                        className="pl-10"
                        required
                      />
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="register-password">Password</Label>
                    <div className="relative">
                      <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                      <Input
                        id="register-password"
                        type="password"
                        placeholder="Create a password"
                        value={registerData.password}
                        onChange={(e) => setRegisterData({...registerData, password: e.target.value})}
                        className="pl-10"
                        required
                      />
                    </div>
                  </div>

                  {(error || walletError) && (
                    <div className="p-3 text-sm text-destructive bg-destructive/10 rounded-md">
                      {error || walletError}
                    </div>
                  )}

                  <Button type="submit" className="w-full" disabled={isLoading || isAuthenticating}>
                    {isLoading || isAuthenticating ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Creating Account...
                      </>
                    ) : (
                      'Create Account'
                    )}
                  </Button>
                </form>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
};