import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet';
import { ThemeToggle } from '@/components/ThemeToggle';
import { useAuth } from '@/hooks/useAuth';
import {
  Wallet,
  Bell,
  Settings,
  Menu,
  User,
  LogOut,
  Shield,
  CheckCircle,
  Clock,
  XCircle,
  Home,
  Users,
  Building,
  Globe
} from 'lucide-react';

export const Navbar = () => {
  const navigate = useNavigate();
  const { user, isAuthenticated, logout, walletConnected } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const getKycStatusIcon = () => {
    if (!user) return null;

    switch (user.kycStatus) {
      case 'approved':
        return <CheckCircle className="w-3 h-3 text-green-500" />;
      case 'pending':
        return <Clock className="w-3 h-3 text-yellow-500" />;
      case 'rejected':
        return <XCircle className="w-3 h-3 text-red-500" />;
      default:
        return <Shield className="w-3 h-3 text-muted-foreground" />;
    }
  };

  const getKycStatusText = () => {
    if (!user) return '';

    switch (user.kycStatus) {
      case 'approved':
        return 'Verified';
      case 'pending':
        return 'Pending KYC';
      case 'rejected':
        return 'KYC Rejected';
      default:
        return 'KYC Required';
    }
  };

  return (
    <nav className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-8">
            <Link to="/" className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-primary flex items-center justify-center">
                <span className="text-white font-bold">N</span>
              </div>
              <h1 className="text-2xl font-bold bg-gradient-primary bg-clip-text text-transparent">
                Nimo
              </h1>
            </Link>

            {isAuthenticated && (
              <div className="hidden md:flex items-center gap-6">
                <Link to="/dashboard/user" className="text-foreground hover:text-primary transition-colors">
                  Dashboard
                </Link>
                <Link to="/dashboard/contributor" className="text-muted-foreground hover:text-primary transition-colors">
                  Contributions
                </Link>
                <Link to="/dashboard/diaspora" className="text-muted-foreground hover:text-primary transition-colors">
                  Marketplace
                </Link>
                <Link to="/dashboard/organization" className="text-muted-foreground hover:text-primary transition-colors">
                  Governance
                </Link>
              </div>
            )}
          </div>

          <div className="flex items-center gap-4">
            {/* User Info & Token Balance */}
            {isAuthenticated && user && (
              <>
                <Badge variant="outline" className="hidden sm:flex items-center gap-2 border-token-gold text-token-gold">
                  <Wallet className="w-3 h-3" />
                  {user.tokenBalance} NIMO
                </Badge>

                {/* KYC Status */}
                <Badge
                  variant="outline"
                  className={`hidden sm:flex items-center gap-2 ${
                    user.kycStatus === 'approved'
                      ? 'border-green-500 text-green-700'
                      : user.kycStatus === 'pending'
                      ? 'border-yellow-500 text-yellow-700'
                      : 'border-red-500 text-red-700'
                  }`}
                >
                  {getKycStatusIcon()}
                  {getKycStatusText()}
                </Badge>
              </>
            )}

            {/* Notifications */}
            {isAuthenticated && (
              <Button variant="ghost" size="sm" className="relative">
                <Bell className="w-4 h-4" />
                <div className="absolute -top-1 -right-1 w-2 h-2 bg-primary rounded-full"></div>
              </Button>
            )}

            {/* User Menu */}
            {isAuthenticated && user ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                    <Avatar className="h-8 w-8">
                      <AvatarImage src="" alt={user.name} />
                      <AvatarFallback>
                        {user.name.split(' ').map(n => n[0]).join('').toUpperCase()}
                      </AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent className="w-56" align="end" forceMount>
                  <DropdownMenuLabel className="font-normal">
                    <div className="flex flex-col space-y-1">
                      <p className="text-sm font-medium leading-none">{user.name}</p>
                      <p className="text-xs leading-none text-muted-foreground">
                        {user.email}
                      </p>
                      {user.walletAddress && (
                        <p className="text-xs leading-none text-muted-foreground font-mono">
                          {user.walletAddress.slice(0, 6)}...{user.walletAddress.slice(-4)}
                        </p>
                      )}
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={() => navigate('/dashboard/user')}>
                    <User className="mr-2 h-4 w-4" />
                    <span>Dashboard</span>
                  </DropdownMenuItem>
                  <DropdownMenuItem>
                    <Settings className="mr-2 h-4 w-4" />
                    <span>Settings</span>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem onClick={handleLogout}>
                    <LogOut className="mr-2 h-4 w-4" />
                    <span>Log out</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              /* Auth Buttons for Unauthenticated Users */
              <div className="hidden sm:flex items-center gap-2">
                <Button variant="ghost" asChild>
                  <Link to="/login">Sign In</Link>
                </Button>
                <Button asChild>
                  <Link to="/register">Sign Up</Link>
                </Button>
              </div>
            )}

            {/* Theme Toggle - Visible on all screen sizes */}
            <div className="flex items-center ml-2">
              <ThemeToggle />
            </div>

            {/* Wallet Connection Status */}
            {walletConnected && (
              <Badge variant="outline" className="hidden sm:flex items-center gap-2 border-green-500 text-green-700">
                <Wallet className="w-3 h-3" />
                Wallet Connected
              </Badge>
            )}

            {/* Mobile Menu */}
            <Sheet open={mobileMenuOpen} onOpenChange={setMobileMenuOpen}>
              <SheetTrigger asChild>
                <Button variant="ghost" size="sm" className="md:hidden">
                  <Menu className="w-5 h-5" />
                  <span className="sr-only">Toggle menu</span>
                </Button>
              </SheetTrigger>
              <SheetContent side="right" className="w-[300px] sm:w-[400px]">
                <SheetHeader>
                  <SheetTitle className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-gradient-primary flex items-center justify-center">
                      <span className="text-white font-bold">N</span>
                    </div>
                    Nimo
                  </SheetTitle>
                  <SheetDescription>
                    Navigate your decentralized identity platform
                  </SheetDescription>
                </SheetHeader>

                <div className="flex flex-col gap-4 mt-6">
                  {isAuthenticated && (
                    <>
                      <div className="space-y-2">
                        <h3 className="font-medium text-sm text-muted-foreground uppercase tracking-wide">Dashboard</h3>
                        <div className="space-y-1">
                          <Button variant="ghost" className="w-full justify-start" onClick={() => { navigate('/dashboard/user'); setMobileMenuOpen(false); }}>
                            <Home className="w-4 h-4 mr-3" />
                            Dashboard
                          </Button>
                          <Button variant="ghost" className="w-full justify-start" onClick={() => { navigate('/dashboard/contributor'); setMobileMenuOpen(false); }}>
                            <Users className="w-4 h-4 mr-3" />
                            Contributions
                          </Button>
                          <Button variant="ghost" className="w-full justify-start" onClick={() => { navigate('/dashboard/diaspora'); setMobileMenuOpen(false); }}>
                            <Globe className="w-4 h-4 mr-3" />
                            Marketplace
                          </Button>
                          <Button variant="ghost" className="w-full justify-start" onClick={() => { navigate('/dashboard/organization'); setMobileMenuOpen(false); }}>
                            <Building className="w-4 h-4 mr-3" />
                            Governance
                          </Button>
                        </div>
                      </div>

                      <div className="border-t pt-4">
                        <div className="flex items-center gap-3 mb-4">
                          <Avatar className="h-10 w-10">
                            <AvatarImage src="" alt={user?.name} />
                            <AvatarFallback>
                              {user?.name.split(' ').map(n => n[0]).join('').toUpperCase()}
                            </AvatarFallback>
                          </Avatar>
                          <div className="flex-1 min-w-0">
                            <p className="font-medium text-sm truncate">{user?.name}</p>
                            <p className="text-xs text-muted-foreground truncate">
                              {user?.email}
                            </p>
                          </div>
                        </div>

                        <div className="space-y-2">
                          <Button variant="ghost" className="w-full justify-start" onClick={() => { navigate('/dashboard/user'); setMobileMenuOpen(false); }}>
                            <User className="w-4 h-4 mr-3" />
                            Profile
                          </Button>
                          <Button variant="ghost" className="w-full justify-start">
                            <Settings className="w-4 h-4 mr-3" />
                            Settings
                          </Button>
                          <Button variant="ghost" className="w-full justify-start text-destructive hover:text-destructive" onClick={handleLogout}>
                            <LogOut className="w-4 h-4 mr-3" />
                            Sign Out
                          </Button>
                        </div>
                      </div>
                    </>
                  )}

                  {!isAuthenticated && (
                    <div className="space-y-2">
                      <Button variant="ghost" className="w-full justify-start" asChild>
                        <Link to="/login" onClick={() => setMobileMenuOpen(false)}>Sign In</Link>
                      </Button>
                      <Button className="w-full" asChild>
                        <Link to="/register" onClick={() => setMobileMenuOpen(false)}>Sign Up</Link>
                      </Button>
                    </div>
                  )}

                  {/* Theme Toggle in Mobile Menu */}
                  <div className="mt-4 border-t pt-4">
                    <h3 className="font-medium text-sm text-muted-foreground uppercase tracking-wide mb-2">Theme</h3>
                    <div className="flex justify-start">
                      <ThemeToggle />
                    </div>
                  </div>
                </div>
              </SheetContent>
            </Sheet>
          </div>
        </div>
      </div>
    </nav>
  );
};