import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { TrendingUp, MapPin, Calendar, Target } from 'lucide-react';

interface ImpactBondCardProps {
  id: string;
  title: string;
  description: string;
  location: string;
  targetAmount: number;
  currentAmount: number;
  deadline: string;
  category: string;
  impactMetrics: string[];
}

export const ImpactBondCard = ({
  id,
  title,
  description,
  location,
  targetAmount,
  currentAmount,
  deadline,
  category,
  impactMetrics
}: ImpactBondCardProps) => {
  const progress = (currentAmount / targetAmount) * 100;
  const daysLeft = Math.ceil((new Date(deadline).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24));

  return (
    <Card className="shadow-card hover:shadow-glow transition-all duration-300">
      <CardHeader>
        <div className="flex items-start justify-between mb-2">
          <Badge variant="secondary">{category}</Badge>
          <div className="flex items-center gap-1 text-sm text-muted-foreground">
            <Calendar className="w-3 h-3" />
            {daysLeft}d left
          </div>
        </div>
        <CardTitle className="text-lg mb-2">{title}</CardTitle>
        <div className="flex items-center gap-1 text-sm text-muted-foreground">
          <MapPin className="w-3 h-3" />
          {location}
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-muted-foreground mb-4 text-sm line-clamp-2">{description}</p>
        
        <div className="mb-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm font-semibold">Funding Progress</span>
            <span className="text-sm text-muted-foreground">
              ${currentAmount.toLocaleString()} / ${targetAmount.toLocaleString()}
            </span>
          </div>
          <Progress value={progress} className="h-2" />
          <p className="text-xs text-muted-foreground mt-1">{progress.toFixed(1)}% funded</p>
        </div>

        <div className="mb-4">
          <div className="flex items-center gap-1 text-sm font-semibold mb-2">
            <Target className="w-3 h-3" />
            Impact Metrics
          </div>
          <div className="flex flex-wrap gap-1">
            {impactMetrics.map((metric, index) => (
              <Badge key={index} variant="outline" className="text-xs border-impact-blue text-impact-blue">
                {metric}
              </Badge>
            ))}
          </div>
        </div>

        <div className="flex gap-2">
          <Button variant="default" size="sm" className="flex-1">
            <TrendingUp className="w-4 h-4 mr-1" />
            Invest
          </Button>
          <Button variant="outline" size="sm" className="flex-1">
            Learn More
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};