import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { useAuth } from '@/hooks/useAuth';
import {
  Mail,
  Lock,
  Wallet,
  Sparkles,
  AlertCircle,
  CheckCircle,
  Loader2,
  ExternalLink
} from 'lucide-react';
import {
  detectCardanoWallets,
  connectWallet as connectWalletUtil,
  signMessage,
  hasCardanoWallets,
  getWalletInstallationUrls,
  getWalletTroubleshootingInfo,
  type WalletInfo
} from '@/lib/utils';

const LoginPage = () => {
  const navigate = useNavigate();
  const { login, isLoading } = useAuth();

  // Traditional login state
  const [traditionalForm, setTraditionalForm] = useState({
    email: '',
    password: '',
  });

  // Wallet login state
  const [walletForm, setWalletForm] = useState({
    walletAddress: '',
    signature: '',
    message: '',
  });

  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isWalletConnecting, setIsWalletConnecting] = useState(false);
  const [availableWallets, setAvailableWallets] = useState<WalletInfo[]>([]);
  const [selectedWallet, setSelectedWallet] = useState<string>('');

  // Detect available wallets on component mount
  useEffect(() => {
    const wallets = detectCardanoWallets();
    setAvailableWallets(wallets);
    if (wallets.length > 0) {
      setSelectedWallet(wallets[0].id);
    }
  }, []);

  const handleTraditionalLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    // Require wallet connection for all logins
    if (!walletForm.walletAddress) {
      setError('Please connect your Cardano wallet to sign in');
      return;
    }

    try {
      await login({
        email: traditionalForm.email,
        password: traditionalForm.password,
        authMethod: 'traditional',
      });

      setSuccess('Login successful! Redirecting...');
      setTimeout(() => navigate('/dashboard/user'), 1500);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Login failed. Please try again.');
    }
  };

  const handleWalletLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      await login({
        walletAddress: walletForm.walletAddress,
        signature: walletForm.signature,
        message: walletForm.message,
        authMethod: 'wallet',
      });

      setSuccess('Wallet login successful! Redirecting...');
      setTimeout(() => navigate('/dashboard/user'), 1500);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Wallet login failed. Please try again.');
    }
  };

  const connectWallet = async () => {
    const walletToConnect = selectedWallet;
    if (!walletToConnect) {
      setError('Please select a wallet to connect');
      return;
    }

    setIsWalletConnecting(true);
    setError('');

    try {
      const { wallet, address } = await connectWalletUtil(walletToConnect);

      // Generate a challenge message
      const message = `Sign this message to authenticate with Nimo: ${Date.now()}`;
      const signature = await signMessage(wallet, address, message);

      setWalletForm({
        walletAddress: address,
        signature: signature,
        message,
      });

      setSuccess('Wallet connected successfully! Please sign the authentication message.');
    } catch (err: unknown) {
      let errorMessage = 'Failed to connect wallet';

      if (err instanceof Error) {
        if (err.message.includes('not available')) {
          errorMessage = `Wallet extension not found. Please install ${getWalletName(walletToConnect)} and refresh the page.`;
        } else if (err.message.includes('rejected')) {
          errorMessage = 'Wallet connection was rejected. Please try again and approve the connection.';
        } else if (err.message.includes('enable')) {
          errorMessage = 'Failed to enable wallet. Please make sure the wallet extension is unlocked and try again.';
        } else if (err.message.includes('No addresses found')) {
          errorMessage = `${err.message}\n\n${getWalletTroubleshootingInfo(walletToConnect)}`;
        } else {
          errorMessage = err.message;
        }
      }

      setError(errorMessage);
    } finally {
      setIsWalletConnecting(false);
    }
  };

  // Helper function to get wallet name
  const getWalletName = (walletId: string): string => {
    const wallet = availableWallets.find(w => w.id === walletId);
    return wallet?.name || walletId;
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-primary/5 via-background to-secondary/5 flex items-center justify-center p-4" role="main">
      <div className="w-full max-w-md">
        {/* Header */}
        <header className="text-center mb-8">
          <div className="flex items-center justify-center space-x-2 mb-4">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-primary to-secondary flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-white" aria-hidden="true" />
            </div>
            <h1 className="text-3xl font-bold text-primary">Nimo</h1>
          </div>
          <h2 className="text-2xl font-semibold text-foreground mb-2">Welcome Back</h2>
          <p className="text-muted-foreground">Sign in to access your decentralized identity</p>
        </header>

        {/* Login Form */}
        <Card className="shadow-lg border-0 bg-white/95 backdrop-blur-sm">
          <CardHeader className="space-y-1">
            <CardTitle className="text-xl text-center">Sign In</CardTitle>
            <CardDescription className="text-center">
              Connect your wallet and choose your authentication method
            </CardDescription>
          </CardHeader>
          <CardContent>
            {/* Wallet Connection Required Notice */}
            {!walletForm.walletAddress && (
              <Alert className="mb-4 border-amber-200 bg-amber-50">
                <Wallet className="h-4 w-4 text-amber-600" />
                <AlertDescription className="text-amber-800">
                  {availableWallets.length === 0 ? (
                    <div className="space-y-2">
                      <p>Wallet connection is required to access Nimo.</p>
                      <p className="text-sm">Please install a Cardano wallet extension and refresh this page.</p>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      <p>Wallet connection is required to access Nimo.</p>
                      <p className="text-sm">Select and connect your Cardano wallet from the options below.</p>
                    </div>
                  )}
                </AlertDescription>
              </Alert>
            )}

            <Tabs defaultValue="traditional" className="w-full" aria-label="Authentication method selection">
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="traditional" className="flex items-center space-x-2">
                  <Mail className="w-4 h-4" aria-hidden="true" />
                  <span>Email</span>
                </TabsTrigger>
                <TabsTrigger value="wallet" className="flex items-center space-x-2">
                  <Wallet className="w-4 h-4" aria-hidden="true" />
                  <span>Wallet</span>
                </TabsTrigger>
              </TabsList>

              {/* Traditional Login */}
              <TabsContent value="traditional" className="space-y-4">
                <form onSubmit={handleTraditionalLogin} className="space-y-4" aria-labelledby="traditional-login">
                  <fieldset>
                    <legend id="traditional-login" className="sr-only">Email and Password Login</legend>
                    <div className="space-y-2">
                      <Label htmlFor="email">Email</Label>
                      <div className="relative">
                        <Mail className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" aria-hidden="true" />
                        <Input
                          id="email"
                          type="email"
                          placeholder="Enter your email"
                          value={traditionalForm.email}
                          onChange={(e) => setTraditionalForm(prev => ({ ...prev, email: e.target.value }))}
                          className="pl-10"
                          required
                          aria-describedby="email-help"
                        />
                        <span id="email-help" className="sr-only">Enter your registered email address</span>
                      </div>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="password">Password</Label>
                      <div className="relative">
                        <Lock className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" aria-hidden="true" />
                        <Input
                          id="password"
                          type="password"
                          placeholder="Enter your password"
                          value={traditionalForm.password}
                          onChange={(e) => setTraditionalForm(prev => ({ ...prev, password: e.target.value }))}
                          className="pl-10"
                          required
                          aria-describedby="password-help"
                        />
                        <span id="password-help" className="sr-only">Enter your account password</span>
                      </div>
                    </div>

                    <Button type="submit" className="w-full" disabled={isLoading || !walletForm.walletAddress}>
                      {isLoading ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" aria-hidden="true" />
                          Signing In...
                        </>
                      ) : (
                        'Sign In'
                      )}
                    </Button>
                  </fieldset>
                </form>
              </TabsContent>

              {/* Wallet Login */}
              <TabsContent value="wallet" className="space-y-4">
                <div className="text-center space-y-4">
                  {availableWallets.length === 0 ? (
                    // No wallets detected
                    <div className="p-4 border-2 border-dashed border-muted-foreground/25 rounded-lg">
                      <AlertCircle className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                      <p className="text-sm text-muted-foreground mb-4">
                        No Cardano wallet extensions detected
                      </p>
                      <div className="space-y-3">
                        <div className="text-left">
                          <p className="text-xs text-muted-foreground mb-2">Recommended wallets:</p>
                          <div className="grid grid-cols-1 gap-2">
                            {Object.entries(getWalletInstallationUrls()).slice(0, 4).map(([id, url]) => (
                              <Button
                                key={id}
                                variant="outline"
                                size="sm"
                                onClick={() => window.open(String(url), '_blank')}
                                className="justify-start text-xs"
                              >
                                <span className="mr-2">
                                  {availableWallets.find(w => w.id === id)?.icon || '👛'}
                                </span>
                                Install {getWalletName(id)}
                                <ExternalLink className="w-3 h-3 ml-auto" />
                              </Button>
                            ))}
                          </div>
                        </div>
                        <div className="pt-2 border-t">
                          <p className="text-xs text-muted-foreground mb-2">After installation:</p>
                          <ol className="text-xs text-muted-foreground space-y-1 text-left">
                            <li>1. Refresh this page</li>
                            <li>2. Click "Connect Wallet"</li>
                            <li>3. Approve the connection in your wallet</li>
                            <li>4. Make sure your wallet has at least one address</li>
                          </ol>
                          <p className="text-xs text-muted-foreground mt-2">
                            <strong>Troubleshooting:</strong> If you see "No addresses found", make sure your wallet is properly set up and has at least one address created.
                          </p>
                        </div>
                      </div>
                      <Button
                        onClick={() => window.location.reload()}
                        variant="outline"
                        className="w-full mt-4"
                      >
                        Refresh Page
                      </Button>
                    </div>
                  ) : (
                    // Wallets available
                    <div className="p-4 border-2 border-dashed border-muted-foreground/25 rounded-lg">
                      <Wallet className="w-8 h-8 text-muted-foreground mx-auto mb-2" />
                      <p className="text-sm text-muted-foreground mb-4">
                        Select your Cardano wallet to connect
                      </p>

                      {/* Wallet Selection */}
                      <div className="space-y-2 mb-4">
                        <Label className="text-sm font-medium">Available Wallets:</Label>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                          {availableWallets.map((wallet) => (
                            <Button
                              key={wallet.id}
                              variant={selectedWallet === wallet.id ? "default" : "outline"}
                              size="sm"
                              onClick={() => setSelectedWallet(wallet.id)}
                              className="flex items-center justify-center space-x-2 h-12"
                            >
                              <span className="text-lg">{wallet.icon}</span>
                              <span className="text-sm font-medium">{wallet.name}</span>
                            </Button>
                          ))}
                        </div>
                        <p className="text-xs text-muted-foreground">
                          Don't see your wallet? Make sure it's installed and enabled.
                        </p>
                      </div>

                      <Button
                        onClick={connectWallet}
                        disabled={isWalletConnecting || !selectedWallet}
                        className="w-full"
                      >
                        {isWalletConnecting ? (
                          <>
                            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                            Connecting...
                          </>
                        ) : (
                          <>
                            <Wallet className="mr-2 h-4 w-4" />
                            Connect {selectedWallet ? getWalletName(selectedWallet) : 'Wallet'}
                          </>
                        )}
                      </Button>
                    </div>
                  )}

                  {walletForm.walletAddress && (
                    <div className="space-y-4">
                      <div className="p-3 bg-muted/50 rounded-lg">
                        <div className="flex items-center space-x-2 mb-2">
                          <CheckCircle className="w-4 h-4 text-green-500" />
                          <span className="text-sm font-medium">Wallet Connected</span>
                        </div>
                        <p className="text-xs text-muted-foreground font-mono">
                          {walletForm.walletAddress.slice(0, 8)}...{walletForm.walletAddress.slice(-8)}
                        </p>
                      </div>

                      <form onSubmit={handleWalletLogin} className="space-y-4">
                        <div className="space-y-2">
                          <Label htmlFor="message">Message to Sign</Label>
                          <textarea
                            id="message"
                            placeholder="Authentication message will appear here"
                            value={walletForm.message}
                            readOnly
                            className="w-full p-3 text-sm border rounded-md bg-muted/50 font-mono"
                            rows={3}
                          />
                        </div>

                        <div className="space-y-2">
                          <Label htmlFor="signature">Signature</Label>
                          <Input
                            id="signature"
                            placeholder="Enter signature from wallet"
                            value={walletForm.signature}
                            onChange={(e) => setWalletForm(prev => ({ ...prev, signature: e.target.value }))}
                            required
                          />
                        </div>

                        <Button type="submit" className="w-full" disabled={isLoading}>
                          {isLoading ? (
                            <>
                              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                              Signing In...
                            </>
                          ) : (
                            'Sign In with Wallet'
                          )}
                        </Button>
                      </form>
                    </div>
                  )}
                </div>
              </TabsContent>
            </Tabs>

            {/* Error/Success Messages */}
            {error && (
              <Alert className="mt-4 border-red-200 bg-red-50">
                <AlertCircle className="h-4 w-4 text-red-600" />
                <AlertDescription className="text-red-800">{error}</AlertDescription>
              </Alert>
            )}

            {success && (
              <Alert className="mt-4 border-green-200 bg-green-50">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <AlertDescription className="text-green-800">{success}</AlertDescription>
              </Alert>
            )}

            {/* Footer */}
            <div className="mt-6 text-center space-y-2">
              <p className="text-sm text-muted-foreground">
                Don't have an account?{' '}
                <Link to="/register" className="text-primary hover:underline font-medium">
                  Sign up here
                </Link>
              </p>
              <div className="flex items-center justify-center space-x-4 text-xs text-muted-foreground">
                <Badge variant="secondary" className="text-xs">
                  🔐 Secure Authentication
                </Badge>
                <Badge variant="secondary" className="text-xs">
                  🛡️ KYC Required
                </Badge>
                <Badge variant="secondary" className="text-xs">
                  🌍 Decentralized Identity
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </main>
  );
};

export default LoginPage;