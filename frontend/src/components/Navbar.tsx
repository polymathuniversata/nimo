import React from 'react';
import { useAuth } from '@/hooks/useAuth';
import { AuthModal } from '@/components/AuthModal';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Wallet, Bell, Settings, Menu, LogOut, User } from 'lucide-react';

export const Navbar = () => {
  const { user, isAuthenticated, logout } = useAuth();

  const handleLogout = () => {
    logout();
  };

  return (
    <nav className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-8">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-gradient-primary flex items-center justify-center">
                <span className="text-white font-bold">N</span>
              </div>
              <h1 className="text-2xl font-bold bg-gradient-primary bg-clip-text text-transparent">
                Nimo
              </h1>
            </div>

            <div className="hidden md:flex items-center gap-6">
              <a href="#dashboard" className="text-muted-foreground hover:text-primary transition-colors">
                Dashboard
              </a>
              <a href="#contributions" className="text-muted-foreground hover:text-primary transition-colors">
                My Contributions
              </a>
              <button 
                onClick={(e) => {
                  e.preventDefault();
                  const marketplaceSection = document.getElementById('marketplace');
                  if (marketplaceSection) {
                    // Add a small delay to ensure any route changes complete
                    setTimeout(() => {
                      marketplaceSection.scrollIntoView({ behavior: 'smooth' });
                      // Focus for accessibility
                      marketplaceSection.setAttribute('tabindex', '-1');
                      marketplaceSection.focus();
                    }, 100);
                  }
                }}
                className="group flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-primary to-primary/90 text-white hover:from-primary/90 hover:to-primary/80 shadow-sm hover:shadow-md transition-all duration-200 transform hover:-translate-y-0.5"
              >
                <svg 
                  xmlns="http://www.w3.org/2000/svg" 
                  width="18" 
                  height="18" 
                  viewBox="0 0 24 24" 
                  fill="none" 
                  stroke="currentColor" 
                  strokeWidth="2" 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  className="w-4 h-4 group-hover:scale-110 transition-transform"
                >
                  <path d="M21 12V7H5a2 2 0 0 1 0-4h14v4"></path>
                  <path d="M3 5v14a2 2 0 0 0 2 2h16v-5"></path>
                  <path d="M18 12a2 2 0 1 0 0-4 2 2 0 0 0 0 4z"></path>
                </svg>
                <span className="font-medium">Explore Marketplace</span>
              </button>
              <a href="#governance" className="text-muted-foreground hover:text-primary transition-colors">
                Governance
              </a>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {isAuthenticated && user ? (
              <>
                <Badge variant="outline" className="hidden sm:flex items-center gap-2 border-token-gold text-token-gold">
                  <Wallet className="w-3 h-3" />
                  {user.name}
                </Badge>

                <Button variant="ghost" size="sm" className="relative">
                  <Bell className="w-4 h-4" />
                  <div className="absolute -top-1 -right-1 w-2 h-2 bg-primary rounded-full"></div>
                </Button>

                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                      <Avatar className="h-8 w-8">
                        <AvatarImage src="" alt={user.name} />
                        <AvatarFallback>
                          {user.name.charAt(0).toUpperCase()}
                        </AvatarFallback>
                      </Avatar>
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent className="w-56" align="end" forceMount>
                    <DropdownMenuItem className="flex flex-col items-start">
                      <div className="font-medium">{user.name}</div>
                      <div className="text-xs text-muted-foreground">{user.email}</div>
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem>
                      <User className="mr-2 h-4 w-4" />
                      <span>Profile</span>
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
              </>
            ) : (
              <AuthModal>
                <Button variant="outline" className="hidden sm:flex">
                  Sign In
                </Button>
              </AuthModal>
            )}

            <Button variant="ghost" size="sm" className="md:hidden">
              <Menu className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>
    </nav>
  );
};