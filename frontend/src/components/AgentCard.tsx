import React from 'react'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Progress } from '@/components/ui/progress'
import {
  Users,
  TrendingUp,
  Target,
  Award,
  Calendar,
  MapPin,
  ExternalLink,
  MoreHorizontal
} from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'

export interface Agent {
  id: string
  name: string
  description: string
  category: 'verification' | 'governance' | 'analysis' | 'coordination'
  healthScore: number
  totalDecisions: number
  recentDecisions: number
  accuracy: number
  avatar?: string
  status: 'active' | 'training' | 'maintenance'
  lastActive: string
  capabilities: string[]
}

interface AgentCardProps {
  agent: Agent
  onOverride?: (agentId: string) => void
  onViewDetails?: (agentId: string) => void
}

export function AgentCard({ agent, onOverride, onViewDetails }: AgentCardProps) {
  const { hasRole } = useAuth()
  const isAdmin = hasRole('admin')

  const getStatusColor = (status: Agent['status']) => {
    switch (status) {
      case 'active': return 'bg-green-500'
      case 'training': return 'bg-yellow-500'
      case 'maintenance': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  const getCategoryIcon = (category: Agent['category']) => {
    switch (category) {
      case 'verification': return <Award className="w-4 h-4" />
      case 'governance': return <Users className="w-4 h-4" />
      case 'analysis': return <TrendingUp className="w-4 h-4" />
      case 'coordination': return <Target className="w-4 h-4" />
      default: return <Target className="w-4 h-4" />
    }
  }

  return (
    <Card className="p-6 hover:shadow-lg transition-all duration-300 group">
      <div className="flex items-start gap-4">
        {/* Agent Avatar */}
        <div className="relative">
          <Avatar className="w-12 h-12">
            <AvatarImage src={agent.avatar} alt={agent.name} />
            <AvatarFallback className="bg-gradient-to-br from-primary to-secondary text-white">
              {agent.name.substring(0, 2).toUpperCase()}
            </AvatarFallback>
          </Avatar>
          <div className={`absolute -bottom-1 -right-1 w-4 h-4 rounded-full border-2 border-white ${getStatusColor(agent.status)}`} />
        </div>

        {/* Agent Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="font-semibold text-lg truncate">{agent.name}</h3>
              <p className="text-sm text-muted-foreground mt-1 line-clamp-2">
                {agent.description}
              </p>
            </div>
            {isAdmin && onOverride && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onOverride(agent.id)}
                className="opacity-0 group-hover:opacity-100 transition-opacity"
              >
                <MoreHorizontal className="w-4 h-4" />
              </Button>
            )}
          </div>

          {/* Category Badge */}
          <div className="flex items-center gap-2 mt-2">
            {getCategoryIcon(agent.category)}
            <Badge variant="secondary" className="text-xs">
              {agent.category}
            </Badge>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-4 mt-4">
            <div className="text-center">
              <div className="text-lg font-semibold">{agent.totalDecisions}</div>
              <div className="text-xs text-muted-foreground">Total Decisions</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold">{agent.accuracy}%</div>
              <div className="text-xs text-muted-foreground">Accuracy</div>
            </div>
            <div className="text-center">
              <div className="text-lg font-semibold">{agent.recentDecisions}</div>
              <div className="text-xs text-muted-foreground">This Week</div>
            </div>
          </div>

          {/* Health Score */}
          <div className="mt-4">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium">Health Score</span>
              <span className="text-sm text-muted-foreground">{agent.healthScore}%</span>
            </div>
            <Progress value={agent.healthScore} className="h-2" />
          </div>

          {/* Capabilities */}
          <div className="mt-3 flex flex-wrap gap-1">
            {agent.capabilities.slice(0, 3).map((capability, index) => (
              <Badge key={index} variant="outline" className="text-xs">
                {capability}
              </Badge>
            ))}
            {agent.capabilities.length > 3 && (
              <Badge variant="outline" className="text-xs">
                +{agent.capabilities.length - 3} more
              </Badge>
            )}
          </div>

          {/* Last Active */}
          <div className="mt-3 flex items-center gap-2 text-xs text-muted-foreground">
            <Calendar className="w-3 h-3" />
            <span>Last active: {new Date(agent.lastActive).toLocaleDateString()}</span>
          </div>
        </div>
      </div>

      {/* View Details Button */}
      {onViewDetails && (
        <div className="mt-4 pt-4 border-t">
          <Button
            variant="outline"
            size="sm"
            onClick={() => onViewDetails(agent.id)}
            className="w-full"
          >
            <ExternalLink className="w-4 h-4 mr-2" />
            View Details
          </Button>
        </div>
      )}
    </Card>
  )
}
