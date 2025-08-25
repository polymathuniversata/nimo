import { api } from '../boot/axios';

const tokenService = {
  /**
   * Get current user's token balance
   * @returns {Promise} Promise with token balance
   */
  getTokenBalance() {
    return api.get('/tokens/balance');
  },

  /**
   * Get token transaction history for current user
   * @param {Object} params - Optional filter parameters
   * @returns {Promise} Promise with transaction history
   */
  getTransactionHistory(params = {}) {
    return api.get('/tokens/transactions', { params });
  },

  /**
   * Get token statistics for current user
   * @returns {Promise} Promise with token stats by category
   */
  getTokenStats() {
    return api.get('/tokens/stats');
  },

  /**
   * Get available token usage options
   * @returns {Promise} Promise with available options
   */
  getTokenUsageOptions() {
    return api.get('/tokens/usage-options');
  }
};

export default tokenService;