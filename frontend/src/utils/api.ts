// API utilities for contribution management
export interface Contribution {
  id: string;
  title: string;
  category: string;
  status: string;
  tokenReward: number;
  createdAt: string;
  feedback?: string;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

export const submitContribution = async (contribution: {
  title: string;
  description: string;
  category: string;
  evidence: string;
}): Promise<ApiResponse<Contribution>> => {
  // Placeholder implementation - in real app this would make API call
  return {
    success: true,
    data: {
      id: 'contrib_' + Date.now(),
      title: contribution.title,
      category: contribution.category,
      status: 'pending_verification',
      tokenReward: 0,
      createdAt: new Date().toISOString()
    }
  };
};

export const updateContributionStatus = async (
  contributionId: string,
  status: string,
  feedback?: string
): Promise<ApiResponse<Contribution>> => {
  // Placeholder implementation - in real app this would make API call
  return {
    success: true,
    data: {
      id: contributionId,
      title: 'Updated Contribution',
      category: 'coding',
      status,
      tokenReward: status === 'verified' ? 150 : 0,
      createdAt: new Date().toISOString(),
      feedback
    }
  };
};

export const getContributions = async (): Promise<ApiResponse<Contribution[]>> => {
  // Placeholder implementation - in real app this would make API call
  return {
    success: true,
    data: [
      {
        id: 'contrib_1',
        title: 'Open Source Project',
        category: 'coding',
        status: 'verified',
        tokenReward: 150,
        createdAt: '2024-01-15'
      },
      {
        id: 'contrib_2',
        title: 'Community Workshop',
        category: 'education',
        status: 'pending_verification',
        tokenReward: 0,
        createdAt: '2024-01-20'
      }
    ]
  };
};