import React from 'react'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import {
  Users,
  Calendar,
  MessageSquare,
  ThumbsUp,
  ThumbsDown,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle
} from 'lucide-react'
import { useAuth } from '@/contexts/AuthContext'

export interface GovernanceProposal {
  id: string
  title: string
  description: string
  type: 'improvement' | 'feature' | 'bugfix' | 'policy' | 'budget' | 'emergency'
  status: 'active' | 'passed' | 'rejected' | 'expired' | 'draft'
  priority: 'low' | 'medium' | 'high' | 'critical'
  authorId: string
  authorName: string
  authorAvatar?: string
  createdAt: string
  endDate: string
  totalVotes: number
  yesVotes: number
  noVotes: number
  abstainVotes: number
  quorum: number
  requiredMajority: number
  tags: string[]
  category: 'technical' | 'governance' | 'financial' | 'social' | 'environmental'
  discussionLink?: string
  implementationCost?: number
  expectedImpact: string
  documents?: string[]
}

interface ProposalCardProps {
  proposal: GovernanceProposal
  onVote?: (proposalId: string, vote: 'yes' | 'no' | 'abstain') => void
  onViewDetails?: (proposalId: string) => void
  userVote?: 'yes' | 'no' | 'abstain'
  showVoteButtons?: boolean
}

export function ProposalCard({
  proposal,
  onVote,
  onViewDetails,
  userVote,
  showVoteButtons = true
}: ProposalCardProps) {
  const { hasRole } = useAuth()
  // const isAdmin = hasRole('admin') // TODO: Implement admin features for proposal management

  const yesPercentage = proposal.totalVotes > 0 ? (proposal.yesVotes / proposal.totalVotes) * 100 : 0
  const noPercentage = proposal.totalVotes > 0 ? (proposal.noVotes / proposal.totalVotes) * 100 : 0
  const abstainPercentage = proposal.totalVotes > 0 ? (proposal.abstainVotes / proposal.totalVotes) * 100 : 0

  const daysRemaining = Math.ceil((new Date(proposal.endDate).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))

  const getStatusColor = (status: GovernanceProposal['status']) => {
    switch (status) {
      case 'active': return 'bg-green-500'
      case 'passed': return 'bg-blue-500'
      case 'rejected': return 'bg-red-500'
      case 'expired': return 'bg-yellow-500'
      case 'draft': return 'bg-gray-500'
      default: return 'bg-gray-500'
    }
  }

  const getStatusIcon = (status: GovernanceProposal['status']) => {
    switch (status) {
      case 'active': return <Clock className="w-4 h-4" />
      case 'passed': return <CheckCircle className="w-4 h-4" />
      case 'rejected': return <XCircle className="w-4 h-4" />
      case 'expired': return <AlertCircle className="w-4 h-4" />
      case 'draft': return <MessageSquare className="w-4 h-4" />
      default: return <MessageSquare className="w-4 h-4" />
    }
  }

  const getPriorityColor = (priority: GovernanceProposal['priority']) => {
    switch (priority) {
      case 'critical': return 'text-red-600 bg-red-50 border-red-200'
      case 'high': return 'text-orange-600 bg-orange-50 border-orange-200'
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      case 'low': return 'text-green-600 bg-green-50 border-green-200'
      default: return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  const getTypeColor = (type: GovernanceProposal['type']) => {
    switch (type) {
      case 'emergency': return 'text-red-600 bg-red-50 border-red-200'
      case 'budget': return 'text-blue-600 bg-blue-50 border-blue-200'
      case 'feature': return 'text-purple-600 bg-purple-50 border-purple-200'
      case 'improvement': return 'text-green-600 bg-green-50 border-green-200'
      case 'bugfix': return 'text-orange-600 bg-orange-50 border-orange-200'
      case 'policy': return 'text-indigo-600 bg-indigo-50 border-indigo-200'
      default: return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }

  return (
    <Card className="p-6 hover:shadow-lg transition-all duration-300 group">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h3 className="font-semibold text-lg line-clamp-2">{proposal.title}</h3>
            <div className="flex items-center gap-2">
              <Badge className={`${getStatusColor(proposal.status)} text-white`}>
                {getStatusIcon(proposal.status)}
                <span className="ml-1">{proposal.status.toUpperCase()}</span>
              </Badge>
            </div>
          </div>

          <div className="flex items-center gap-2 mb-3">
            <Badge variant="outline" className={getTypeColor(proposal.type)}>
              {proposal.type.toUpperCase()}
            </Badge>
            <Badge variant="outline" className={getPriorityColor(proposal.priority)}>
              {proposal.priority.toUpperCase()}
            </Badge>
            <Badge variant="secondary">
              {proposal.category}
            </Badge>
          </div>
        </div>
      </div>

      {/* Description */}
      <p className="text-sm text-muted-foreground mb-4 line-clamp-3">
        {proposal.description}
      </p>

      {/* Voting Progress */}
      <div className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium">Voting Progress</span>
          <span className="text-sm text-muted-foreground">
            {proposal.totalVotes} votes • {daysRemaining > 0 ? `${daysRemaining} days left` : 'Expired'}
          </span>
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="text-green-600 font-medium">Yes ({Math.round(yesPercentage)}%)</span>
            <span className="text-red-600 font-medium">No ({Math.round(noPercentage)}%)</span>
            <span className="text-gray-600 font-medium">Abstain ({Math.round(abstainPercentage)}%)</span>
          </div>
          <div className="flex gap-1 h-2">
            <div
              className="bg-green-500 rounded-l"
              style={{ width: `${yesPercentage}%` }}
            />
            <div
              className="bg-red-500"
              style={{ width: `${noPercentage}%` }}
            />
            <div
              className="bg-gray-400 rounded-r"
              style={{ width: `${abstainPercentage}%` }}
            />
          </div>
        </div>

        {/* Quorum Progress */}
        <div className="mt-2">
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-muted-foreground">Quorum ({proposal.quorum}% required)</span>
            <span className="text-xs text-muted-foreground">
              {Math.round((proposal.totalVotes / 100) * 100)}%
            </span>
          </div>
          <Progress
            value={(proposal.totalVotes / 100) * 100}
            className="h-1"
          />
        </div>
      </div>

      {/* Author & Date */}
      <div className="flex items-center justify-between mb-4 text-sm text-muted-foreground">
        <div className="flex items-center gap-2">
          <Users className="w-4 h-4" />
          <span>By {proposal.authorName}</span>
        </div>
        <div className="flex items-center gap-2">
          <Calendar className="w-4 h-4" />
          <span>{new Date(proposal.createdAt).toLocaleDateString()}</span>
        </div>
      </div>

      {/* Tags */}
      <div className="flex flex-wrap gap-1 mb-4">
        {proposal.tags.slice(0, 5).map((tag, index) => (
          <Badge key={index} variant="outline" className="text-xs">
            {tag}
          </Badge>
        ))}
        {proposal.tags.length > 5 && (
          <Badge variant="outline" className="text-xs">
            +{proposal.tags.length - 5} more
          </Badge>
        )}
      </div>

      {/* Action Buttons */}
      <div className="flex gap-2">
        {showVoteButtons && proposal.status === 'active' && onVote && (
          <>
            <Button
              size="sm"
              variant={userVote === 'yes' ? 'default' : 'outline'}
              onClick={() => onVote(proposal.id, 'yes')}
              className="flex-1"
            >
              <ThumbsUp className="w-4 h-4 mr-2" />
              Yes ({proposal.yesVotes})
            </Button>
            <Button
              size="sm"
              variant={userVote === 'no' ? 'default' : 'outline'}
              onClick={() => onVote(proposal.id, 'no')}
              className="flex-1"
            >
              <ThumbsDown className="w-4 h-4 mr-2" />
              No ({proposal.noVotes})
            </Button>
          </>
        )}

        {onViewDetails && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => onViewDetails(proposal.id)}
            className="flex-1"
          >
            <MessageSquare className="w-4 h-4 mr-2" />
            Details
          </Button>
        )}
      </div>

      {/* Discussion Link */}
      {proposal.discussionLink && (
        <div className="mt-3 pt-3 border-t">
          <a
            href={proposal.discussionLink}
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm text-primary hover:underline flex items-center gap-2"
          >
            <MessageSquare className="w-4 h-4" />
            Join Discussion
          </a>
        </div>
      )}
    </Card>
  )
}
