import { api } from '../boot/axios';

const contributionService = {
  /**
   * Get all contributions for current user
   * @returns {Promise} Promise with user contributions
   */
  getUserContributions() {
    return api.get('/contributions/user');
  },
  
  /**
   * Get all contributions that need verification
   * @returns {Promise} Promise with contributions that need verification
   */
  getContributionsForVerification() {
    return api.get('/contributions/verify');
  },
  
  /**
   * Get contribution details by ID
   * @param {Number|String} contributionId - The contribution ID
   * @returns {Promise} Promise with contribution details
   */
  getContributionById(contributionId) {
    return api.get(`/contributions/${contributionId}`);
  },
  
  /**
   * Create a new contribution
   * @param {Object} contributionData - The contribution data
   * @returns {Promise} Promise with created contribution
   */
  createContribution(contributionData) {
    const formData = new FormData();
    
    // Add text fields
    Object.keys(contributionData).forEach(key => {
      if (key !== 'evidence_files' && contributionData[key] !== null) {
        formData.append(key, contributionData[key]);
      }
    });
    
    // Add evidence files if any
    if (contributionData.evidence_files) {
      contributionData.evidence_files.forEach(file => {
        formData.append('evidence_files', file);
      });
    }
    
    return api.post('/contributions', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  },
  
  /**
   * Verify a contribution
   * @param {Number|String} contributionId - The contribution ID
   * @param {Object} verificationData - The verification data with status and comment
   * @returns {Promise} Promise with verification result
   */
  verifyContribution(contributionId, verificationData) {
    return api.post(`/contributions/${contributionId}/verify`, verificationData);
  },
  
  /**
   * Get contribution types
   * @returns {Promise} Promise with contribution types
   */
  getContributionTypes() {
    return api.get('/contributions/types');
  }
};

export default contributionService;