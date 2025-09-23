import React from 'react'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import {
  MapPin,
  Calendar,
  Users,
  Target,
  DollarSign,
  TrendingUp,
  Heart,
  ExternalLink
} from 'lucide-react'
import { useTokens } from '@/contexts/TokenContext'

export interface ImpactBond {
  id: string
  title: string
  description: string
  category: 'education' | 'health' | 'environment' | 'community' | 'technology' | 'agriculture'
  targetAmount: number
  raisedAmount: number
  minInvestment: number
  expectedReturn: number
  duration: number // in months
  riskLevel: 'low' | 'medium' | 'high'
  location: {
    country: string
    region?: string
    city?: string
  }
  beneficiaries: number
  expectedImpact: string
  status: 'active' | 'funded' | 'completed' | 'cancelled'
  creatorId: string
  creatorName: string
  createdAt: string
  endDate: string
  tags: string[]
  images?: string[]
  documents?: string[]
  milestones: {
    id: string
    title: string
    description: string
    targetDate: string
    completed: boolean
    completedDate?: string
  }[]
}

interface BondCardProps {
  bond: ImpactBond
  onInvest?: (bondId: string) => void
  onViewDetails?: (bondId: string) => void
  showProgress?: boolean
}

export function BondCard({ bond, onInvest, onViewDetails, showProgress = true }: BondCardProps) {
  const { formatADA } = useTokens()

  const progressPercentage = (bond.raisedAmount / bond.targetAmount) * 100
  const daysRemaining = Math.ceil((new Date(bond.endDate).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))

  const getStatusColor = (status: ImpactBond['status']) => {
    switch (status) {
      case 'active': return 'bg-green-500'
      case 'funded': return 'bg-blue-500'
      case 'completed': return 'bg-purple-500'
      case 'cancelled': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  const getStatusText = (status: ImpactBond['status']) => {
    switch (status) {
      case 'active': return 'Active'
      case 'funded': return 'Fully Funded'
      case 'completed': return 'Completed'
      case 'cancelled': return 'Cancelled'
      default: return 'Unknown'
    }
  }

  const getRiskColor = (risk: ImpactBond['riskLevel']) => {
    switch (risk) {
      case 'low': return 'text-green-600 bg-green-50 border-green-200'
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      case 'high': return 'text-red-600 bg-red-50 border-red-200'
      default: return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  return (
    <Card className="p-6 hover:shadow-lg transition-all duration-300 group">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="font-semibold text-lg mb-2 line-clamp-2">{bond.title}</h3>
          <div className="flex items-center gap-2 mb-3">
            <Badge variant="outline" className={getRiskColor(bond.riskLevel)}>
              {bond.riskLevel.toUpperCase()} RISK
            </Badge>
            <Badge
              className={`${getStatusColor(bond.status)} text-white`}
            >
              {getStatusText(bond.status)}
            </Badge>
          </div>
        </div>
        {bond.images && bond.images[0] && (
          <div className="w-16 h-16 rounded-lg overflow-hidden flex-shrink-0">
            <img
              src={bond.images[0]}
              alt={bond.title}
              className="w-full h-full object-cover"
            />
          </div>
        )}
      </div>

      {/* Description */}
      <p className="text-sm text-muted-foreground mb-4 line-clamp-3">
        {bond.description}
      </p>

      {/* Location & Duration */}
      <div className="flex items-center gap-4 mb-4 text-sm text-muted-foreground">
        <div className="flex items-center gap-1">
          <MapPin className="w-4 h-4" />
          <span>{bond.location.city ? `${bond.location.city}, ` : ''}{bond.location.country}</span>
        </div>
        <div className="flex items-center gap-1">
          <Calendar className="w-4 h-4" />
          <span>{bond.duration} months</span>
        </div>
      </div>

      {/* Progress */}
      {showProgress && bond.status === 'active' && (
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">Funding Progress</span>
            <span className="text-sm text-muted-foreground">
              {formatADA(bond.raisedAmount)} / {formatADA(bond.targetAmount)}
            </span>
          </div>
          <Progress value={progressPercentage} className="h-2 mb-2" />
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>{Math.round(progressPercentage)}% funded</span>
            <span>{daysRemaining > 0 ? `${daysRemaining} days left` : 'Expired'}</span>
          </div>
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="text-center p-3 bg-muted/30 rounded-lg">
          <div className="text-lg font-semibold text-primary">{bond.beneficiaries}</div>
          <div className="text-xs text-muted-foreground">Beneficiaries</div>
        </div>
        <div className="text-center p-3 bg-muted/30 rounded-lg">
          <div className="text-lg font-semibold text-secondary">{bond.expectedReturn}%</div>
          <div className="text-xs text-muted-foreground">Expected Return</div>
        </div>
      </div>

      {/* Impact Statement */}
      <div className="mb-4 p-3 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
        <div className="flex items-start gap-2">
          <Target className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
          <p className="text-sm text-blue-800 dark:text-blue-200">
            {bond.expectedImpact}
          </p>
        </div>
      </div>

      {/* Tags */}
      <div className="flex flex-wrap gap-1 mb-4">
        {bond.tags.slice(0, 4).map((tag, index) => (
          <Badge key={index} variant="secondary" className="text-xs">
            {tag}
          </Badge>
        ))}
        {bond.tags.length > 4 && (
          <Badge variant="secondary" className="text-xs">
            +{bond.tags.length - 4} more
          </Badge>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex gap-2">
        {onInvest && bond.status === 'active' && (
          <Button
            onClick={() => onInvest(bond.id)}
            className="flex-1"
            disabled={bond.raisedAmount >= bond.targetAmount}
          >
            <DollarSign className="w-4 h-4 mr-2" />
            Invest
          </Button>
        )}
        {onViewDetails && (
          <Button
            variant="outline"
            onClick={() => onViewDetails(bond.id)}
            className="flex-1"
          >
            <ExternalLink className="w-4 h-4 mr-2" />
            Details
          </Button>
        )}
      </div>

      {/* Creator Info */}
      <div className="mt-4 pt-4 border-t flex items-center justify-between text-xs text-muted-foreground">
        <div className="flex items-center gap-2">
          <Users className="w-3 h-3" />
          <span>By {bond.creatorName}</span>
        </div>
        <span>{new Date(bond.createdAt).toLocaleDateString()}</span>
      </div>
    </Card>
  )
}
