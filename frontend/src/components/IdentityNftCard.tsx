import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Wallet, Users, Trophy, Zap } from 'lucide-react';
import identityNft from '@/assets/identity-nft.jpg';

interface IdentityNftCardProps {
  userName: string;
  userId: string;
  tokenBalance: number;
  verifiedContributions: number;
  reputation: string;
}

export const IdentityNftCard = ({
  userName = "Kwame Asante",
  userId = "user-123",
  tokenBalance = 320,
  verifiedContributions = 12,
  reputation = "Community Builder"
}: IdentityNftCardProps) => {
  return (
    <Card className="relative overflow-hidden bg-gradient-nft shadow-nft animate-pulse-glow">
      <div className="absolute inset-0 bg-gradient-to-br from-nft-glow/20 to-transparent" />
      <CardContent className="p-6 relative z-10">
        <div className="flex items-center gap-4 mb-4">
          <div className="w-16 h-16 rounded-lg overflow-hidden border-2 border-nft-glow/50">
            <img 
              src={identityNft} 
              alt="Identity NFT"
              className="w-full h-full object-cover animate-float"
            />
          </div>
          <div className="flex-1">
            <h3 className="text-xl font-bold text-foreground">{userName}</h3>
            <p className="text-muted-foreground text-sm">ID: {userId}</p>
            <Badge variant="outline" className="mt-1 border-nft-glow text-nft-glow">
              {reputation}
            </Badge>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="flex items-center gap-2">
            <Wallet className="w-4 h-4 text-token-gold" />
            <div>
              <p className="text-2xl font-bold text-token-gold">{tokenBalance}</p>
              <p className="text-xs text-muted-foreground">NIMO Tokens</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Trophy className="w-4 h-4 text-verification-green" />
            <div>
              <p className="text-2xl font-bold text-verification-green">{verifiedContributions}</p>
              <p className="text-xs text-muted-foreground">Verified</p>
            </div>
          </div>
        </div>

        <div className="flex gap-2">
          <Button variant="default" size="sm" className="flex-1">
            <Zap className="w-4 h-4 mr-1" />
            Stake Tokens
          </Button>
          <Button variant="outline" size="sm" className="flex-1">
            <Users className="w-4 h-4 mr-1" />
            Connect
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};