import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { CheckCircle, Clock, GitBranch, ExternalLink } from 'lucide-react';

interface ContributionCardProps {
  id: string;
  title: string;
  category: string;
  description: string;
  status: 'pending' | 'verified' | 'rejected';
  impact: 'low' | 'moderate' | 'significant';
  tokenReward: number;
  evidenceUrl?: string;
  verifierName?: string;
}

export const ContributionCard = ({
  id,
  title,
  category,
  description,
  status,
  impact,
  tokenReward,
  evidenceUrl,
  verifierName
}: ContributionCardProps) => {
  const statusConfig = {
    pending: { color: 'text-primary', bg: 'bg-primary/10', icon: Clock },
    verified: { color: 'text-verification-green', bg: 'bg-verification-green/10', icon: CheckCircle },
    rejected: { color: 'text-destructive', bg: 'bg-destructive/10', icon: Clock }
  };

  const impactConfig = {
    low: 'text-muted-foreground',
    moderate: 'text-primary',
    significant: 'text-token-gold'
  };

  const StatusIcon = statusConfig[status].icon;

  return (
    <Card className="shadow-card hover:shadow-glow transition-all duration-300">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg mb-2">{title}</CardTitle>
            <div className="flex items-center gap-2 mb-2">
              <Badge variant="secondary">{category}</Badge>
              <Badge 
                variant="outline" 
                className={`${statusConfig[status].color} ${statusConfig[status].bg} border-current`}
              >
                <StatusIcon className="w-3 h-3 mr-1" />
                {status}
              </Badge>
            </div>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold text-token-gold">{tokenReward}</p>
            <p className="text-xs text-muted-foreground">NIMO</p>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-muted-foreground mb-4">{description}</p>
        
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">Impact:</span>
            <span className={`text-sm font-semibold ${impactConfig[impact]}`}>
              {impact.charAt(0).toUpperCase() + impact.slice(1)}
            </span>
          </div>
          {verifierName && (
            <div className="text-sm text-muted-foreground">
              Verified by {verifierName}
            </div>
          )}
        </div>

        <div className="flex gap-2">
          {evidenceUrl && (
            <Button variant="outline" size="sm" asChild>
              <a href={evidenceUrl} target="_blank" rel="noopener noreferrer">
                <ExternalLink className="w-4 h-4 mr-1" />
                Evidence
              </a>
            </Button>
          )}
          <Button variant="outline" size="sm">
            <GitBranch className="w-4 h-4 mr-1" />
            Details
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};