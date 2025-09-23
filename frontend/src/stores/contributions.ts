// src/stores/contributions.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'

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

export const useContributionsStore = defineStore('contributions', () => {
  // State
  const contributions = ref<Contribution[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Actions
  const fetchContributions = async (params?: {
    category?: string
    status?: string
    userId?: string
    limit?: number
    offset?: number
  }) => {
    loading.value = true
    error.value = null

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

      contributions.value = mockContributions

    } catch (err) {
      error.value = 'Failed to fetch contributions.'

      // Provide mock data as fallback
      contributions.value = [
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

      console.warn('Using mock contributions due to API failure')
    } finally {
      loading.value = false
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
    loading.value = true
    error.value = null

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
        userId: 'current-user' // TODO: Get from auth store
      }

      // Optimistically add to list
      contributions.value.unshift(newContribution)

      console.log('Contribution submitted successfully')

    } catch (err) {
      error.value = 'Failed to create contribution.'
      throw err
    } finally {
      loading.value = false
    }
  }

  const verifyContribution = async (contributionId: string, verificationData: {
    score: number
    explanation: string
    rewardTokens: number
  }) => {
    loading.value = true
    error.value = null

    try {
      // TODO: Replace with actual API call
      // const response = await api.post(`/contributions/${contributionId}/verify`, verificationData)

      // Update contribution in local state
      const contributionIndex = contributions.value.findIndex(c => c.id === contributionId)
      if (contributionIndex !== -1) {
        contributions.value[contributionIndex] = {
          ...contributions.value[contributionIndex],
          status: 'verified',
          verificationScore: verificationData.score,
          aiExplanation: verificationData.explanation,
          rewardTokens: verificationData.rewardTokens,
          verifierId: 'current-verifier', // TODO: Get from auth store
          updatedAt: new Date().toISOString()
        }
      }

      // Refresh contributions list
      await fetchContributions()

    } catch (err) {
      error.value = 'Failed to verify contribution.'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getContributionExplanation = async (contributionId: string) => {
    try {
      // TODO: Replace with actual API call
      // const response = await api.get(`/contributions/${contributionId}/explain`)

      const contribution = contributions.value.find(c => c.id === contributionId)
      return contribution?.aiExplanation || 'No explanation available'

    } catch (err) {
      error.value = 'Failed to get contribution explanation.'
      return 'Explanation not available'
    }
  }

  const getContributionsByCategory = (category: Contribution['category']) => {
    return contributions.value.filter(c => c.category === category)
  }

  const getVerifiedContributions = () => {
    return contributions.value.filter(c => c.status === 'verified')
  }

  const getPendingContributions = () => {
    return contributions.value.filter(c => c.status === 'pending')
  }

  return {
    // State
    contributions,
    loading,
    error,

    // Actions
    fetchContributions,
    createContribution,
    verifyContribution,
    getContributionExplanation,

    // Getters
    getContributionsByCategory,
    getVerifiedContributions,
    getPendingContributions
  }
})
