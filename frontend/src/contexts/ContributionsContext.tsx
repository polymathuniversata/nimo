// src/contexts/ContributionsContext.tsx
import React, { createContext, useContext, useReducer } from 'react'

export interface Contribution {
  id: string
  title: string
  description: string
  category: 'community' | 'education' | 'environment' | 'health' | 'technology' | 'arts'
  impact: string
  evidence: string[]
  status: 'pending' | 'verified' | 'rejected'
  verificationScore?: number
  aiExplanation?: string
  rewardTokens: number
  createdAt: string
  updatedAt: string
  userId: string
  verifierId?: string
  tags: string[]
  location?: {
    country: string
    city?: string
  }
}

interface ContributionsState {
  contributions: Contribution[]
  loading: boolean
  error: string | null
}

type ContributionsAction =
  | { type: 'FETCH_CONTRIBUTIONS_START' }
  | { type: 'FETCH_CONTRIBUTIONS_SUCCESS'; payload: Contribution[] }
  | { type: 'FETCH_CONTRIBUTIONS_ERROR'; payload: string }
  | { type: 'CREATE_CONTRIBUTION_START' }
  | { type: 'CREATE_CONTRIBUTION_SUCCESS'; payload: Contribution }
  | { type: 'CREATE_CONTRIBUTION_ERROR'; payload: string }
  | { type: 'VERIFY_CONTRIBUTION'; payload: { contributionId: string; verificationData: any } }
  | { type: 'CLEAR_ERROR' }

const initialState: ContributionsState = {
  contributions: [],
  loading: false,
  error: null
}

function contributionsReducer(state: ContributionsState, action: ContributionsAction): ContributionsState {
  switch (action.type) {
    case 'FETCH_CONTRIBUTIONS_START':
    case 'CREATE_CONTRIBUTION_START':
      return { ...state, loading: true, error: null }
    case 'FETCH_CONTRIBUTIONS_SUCCESS':
      return { ...state, contributions: action.payload, loading: false, error: null }
    case 'CREATE_CONTRIBUTION_SUCCESS':
      return {
        ...state,
        contributions: [action.payload, ...state.contributions],
        loading: false,
        error: null
      }
    case 'FETCH_CONTRIBUTIONS_ERROR':
    case 'CREATE_CONTRIBUTION_ERROR':
      return { ...state, loading: false, error: action.payload }
    case 'VERIFY_CONTRIBUTION':
      return {
        ...state,
        contributions: state.contributions.map(contrib =>
          contrib.id === action.payload.contributionId
            ? { ...contrib, ...action.payload.verificationData }
            : contrib
        )
      }
    case 'CLEAR_ERROR':
      return { ...state, error: null }
    default:
      return state
  }
}

interface ContributionsContextType {
  state: ContributionsState
  fetchContributions: (params?: {
    category?: string
    status?: string
    userId?: string
    limit?: number
    offset?: number
  }) => Promise<void>
  createContribution: (contributionData: {
    title: string
    description: string
    category: Contribution['category']
    impact: string
    evidence: string[]
    tags: string[]
    location?: Contribution['location']
  }) => Promise<void>
  verifyContribution: (contributionId: string, verificationData: {
    score: number
    explanation: string
    rewardTokens: number
  }) => Promise<void>
  getContributionExplanation: (contributionId: string) => Promise<string>
  getContributionsByCategory: (category: Contribution['category']) => Contribution[]
  getVerifiedContributions: () => Contribution[]
  getPendingContributions: () => Contribution[]
  clearError: () => void
}

const ContributionsContext = createContext<ContributionsContextType | undefined>(undefined)

export function ContributionsProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(contributionsReducer, initialState)

  const fetchContributions = async (_params?: {
    category?: string
    status?: string
    userId?: string
    limit?: number
    offset?: number
  }) => {
    dispatch({ type: 'FETCH_CONTRIBUTIONS_START' })

    try {
      // TODO: Replace with actual API call
      // const response = await api.get('/contributions', { params })

      // Mock contributions data for development
      const mockContributions: Contribution[] = [
        {
          id: '1',
          title: 'Community Health Initiative',
          description: 'Organized free health screenings for 200+ community members',
          category: 'health',
          impact: 'Improved healthcare access for underserved populations',
          evidence: ['event_photos.jpg', 'attendance_sheet.pdf'],
          status: 'verified',
          verificationScore: 85,
          aiExplanation: 'AI analysis confirms community impact through photo evidence and attendance records',
          rewardTokens: 150,
          createdAt: new Date(Date.now() - 86400000 * 30).toISOString(),
          updatedAt: new Date(Date.now() - 86400000 * 7).toISOString(),
          userId: 'user1',
          verifierId: 'verifier1',
          tags: ['healthcare', 'community', 'impact'],
          location: {
            country: 'Kenya',
            city: 'Nairobi'
          }
        },
        {
          id: '2',
          title: 'Youth Coding Bootcamp',
          description: 'Taught programming skills to 50 young people',
          category: 'education',
          impact: 'Empowered youth with valuable technical skills',
          evidence: ['course_materials.pdf', 'certificates.pdf', 'testimonials.docx'],
          status: 'pending',
          rewardTokens: 200,
          createdAt: new Date(Date.now() - 86400000 * 14).toISOString(),
          updatedAt: new Date(Date.now() - 86400000 * 14).toISOString(),
          userId: 'user2',
          tags: ['education', 'programming', 'youth'],
          location: {
            country: 'Kenya',
            city: 'Mombasa'
          }
        },
        {
          id: '3',
          title: 'Environmental Cleanup Drive',
          description: 'Led cleanup of local river and surrounding areas',
          category: 'environment',
          impact: 'Removed 2 tons of waste from waterways',
          evidence: ['before_after_photos.jpg', 'waste_manifest.pdf', 'volunteer_list.xlsx'],
          status: 'verified',
          verificationScore: 92,
          aiExplanation: 'Satellite imagery and waste documentation confirm significant environmental impact',
          rewardTokens: 120,
          createdAt: new Date(Date.now() - 86400000 * 60).toISOString(),
          updatedAt: new Date(Date.now() - 86400000 * 10).toISOString(),
          userId: 'user3',
          verifierId: 'verifier2',
          tags: ['environment', 'cleanup', 'sustainability'],
          location: {
            country: 'Kenya',
            city: 'Kisumu'
          }
        }
      ]

      dispatch({ type: 'FETCH_CONTRIBUTIONS_SUCCESS', payload: mockContributions })

    } catch (err) {
      dispatch({ type: 'FETCH_CONTRIBUTIONS_ERROR', payload: 'Failed to fetch contributions.' })

      // Provide mock data as fallback
      const fallbackContributions: Contribution[] = [
        {
          id: 'mock-1',
          title: 'Sample Contribution',
          description: 'A sample contribution for development',
          category: 'community',
          impact: 'Sample impact description',
          evidence: ['sample_evidence.pdf'],
          status: 'pending',
          rewardTokens: 50,
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          userId: 'sample-user',
          tags: ['sample', 'development']
        }
      ]

      dispatch({ type: 'FETCH_CONTRIBUTIONS_SUCCESS', payload: fallbackContributions })
      console.warn('Using mock contributions due to API failure')
    }
  }

  const createContribution = async (contributionData: {
    title: string
    description: string
    category: Contribution['category']
    impact: string
    evidence: string[]
    tags: string[]
    location?: Contribution['location']
  }) => {
    dispatch({ type: 'CREATE_CONTRIBUTION_START' })

    try {
      // TODO: Replace with actual API call
      // const response = await api.post('/contributions', contributionData)

      // Create new contribution object
      const newContribution: Contribution = {
        id: Date.now().toString(),
        ...contributionData,
        status: 'pending',
        rewardTokens: 0, // Will be calculated by AI verification
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        userId: 'current-user' // TODO: Get from auth context
      }

      dispatch({ type: 'CREATE_CONTRIBUTION_SUCCESS', payload: newContribution })

    } catch (err) {
      dispatch({ type: 'CREATE_CONTRIBUTION_ERROR', payload: 'Failed to create contribution.' })
      throw err
    }
  }

  const verifyContribution = async (contributionId: string, verificationData: {
    score: number
    explanation: string
    rewardTokens: number
  }) => {
    try {
      // TODO: Replace with actual API call
      // const response = await api.post(`/contributions/${contributionId}/verify`, verificationData)

      // Update contribution in local state
      dispatch({
        type: 'VERIFY_CONTRIBUTION',
        payload: {
          contributionId,
          verificationData: {
            status: 'verified',
            verificationScore: verificationData.score,
            aiExplanation: verificationData.explanation,
            rewardTokens: verificationData.rewardTokens,
            verifierId: 'current-verifier', // TODO: Get from auth context
            updatedAt: new Date().toISOString()
          }
        }
      })

      // Refresh contributions list
      await fetchContributions()

    } catch (err) {
      dispatch({ type: 'FETCH_CONTRIBUTIONS_ERROR', payload: 'Failed to verify contribution.' })
      throw err
    }
  }

  const getContributionExplanation = async (contributionId: string) => {
    try {
      // TODO: Replace with actual API call
      // const response = await api.get(`/contributions/${contributionId}/explain`)

      const contribution = state.contributions.find(c => c.id === contributionId)
      return contribution?.aiExplanation || 'No explanation available'

    } catch (err) {
      dispatch({ type: 'FETCH_CONTRIBUTIONS_ERROR', payload: 'Failed to get contribution explanation.' })
      return 'Explanation not available'
    }
  }

  const getContributionsByCategory = (category: Contribution['category']) => {
    return state.contributions.filter(c => c.category === category)
  }

  const getVerifiedContributions = () => {
    return state.contributions.filter(c => c.status === 'verified')
  }

  const getPendingContributions = () => {
    return state.contributions.filter(c => c.status === 'pending')
  }

  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' })
  }

  return (
    <ContributionsContext.Provider
      value={{
        state,
        fetchContributions,
        createContribution,
        verifyContribution,
        getContributionExplanation,
        getContributionsByCategory,
        getVerifiedContributions,
        getPendingContributions,
        clearError
      }}
    >
      {children}
    </ContributionsContext.Provider>
  )
}

export function useContributions() {
  const context = useContext(ContributionsContext)
  if (context === undefined) {
    throw new Error('useContributions must be used within a ContributionsProvider')
  }
  return context
}
