import React from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Wallet, Bell, Settings, Menu } from 'lucide-react';

export const Navbar = () => {
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
              <a href="#dashboard" className="text-foreground hover:text-primary transition-colors">
                Dashboard
              </a>
              <a href="#contributions" className="text-muted-foreground hover:text-primary transition-colors">
                Contributions
              </a>
              <a href="#marketplace" className="text-muted-foreground hover:text-primary transition-colors">
                Marketplace
              </a>
              <a href="#governance" className="text-muted-foreground hover:text-primary transition-colors">
                Governance
              </a>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <Badge variant="outline" className="hidden sm:flex items-center gap-2 border-token-gold text-token-gold">
              <Wallet className="w-3 h-3" />
              320 NIMO
            </Badge>
            
            <Button variant="ghost" size="sm" className="relative">
              <Bell className="w-4 h-4" />
              <div className="absolute -top-1 -right-1 w-2 h-2 bg-primary rounded-full"></div>
            </Button>
            
            <Button variant="ghost" size="sm">
              <Settings className="w-4 h-4" />
            </Button>
            
            <Button variant="outline" className="hidden sm:flex">
              Connect Wallet
            </Button>
            
            <Button variant="ghost" size="sm" className="md:hidden">
              <Menu className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>
    </nav>
  );
};