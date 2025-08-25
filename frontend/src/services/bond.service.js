import { api } from '../boot/axios';

const bondService = {
  /**
   * Get all active bonds
   * @returns {Promise} Promise with bonds data
   */
  getActiveBonds() {
    return api.get('/bonds/active');
  },

  /**
   * Get bonds created by the current user
   * @returns {Promise} Promise with user's bonds
   */
  getUserBonds() {
    return api.get('/bonds/user');
  },

  /**
   * Get all investments made by current user
   * @returns {Promise} Promise with user's investments
   */
  getUserInvestments() {
    return api.get('/bonds/investments');
  },

  /**
   * Create a new bond
   * @param {Object} bondData - The bond data
   * @returns {Promise} Promise with created bond
   */
  createBond(bondData) {
    return api.post('/bonds', bondData);
  },

  /**
   * Get bond details by ID
   * @param {Number|String} bondId - The bond ID
   * @returns {Promise} Promise with bond details
   */
  getBondById(bondId) {
    return api.get(`/bonds/${bondId}`);
  },

  /**
   * Invest in a bond
   * @param {Number|String} bondId - The bond ID
   * @param {Number} amount - Investment amount in tokens
   * @returns {Promise} Promise with investment details
   */
  investInBond(bondId, amount) {
    return api.post(`/bonds/${bondId}/invest`, { amount });
  },

  /**
   * Add a milestone to a bond
   * @param {Number|String} bondId - The bond ID
   * @param {Object} milestone - Milestone details with description and optional evidence URL
   * @returns {Promise} Promise with updated bond
   */
  addMilestone(bondId, milestone) {
    return api.post(`/bonds/${bondId}/milestones`, milestone);
  },

  /**
   * Get NFT certificate for an investment
   * @param {Number|String} investmentId - The investment ID
   * @returns {Promise} Promise with NFT certificate details
   */
  getNftCertificate(investmentId) {
    return api.get(`/bonds/investments/${investmentId}/certificate`);
  }
};

export default bondService;