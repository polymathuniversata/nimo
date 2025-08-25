import { api } from '../boot/axios';

const authService = {
  /**
   * Login user and set token in local storage
   * @param {Object} credentials - User credentials
   * @returns {Promise} Promise with user data and token
   */
  login(credentials) {
    return api.post('/auth/login', credentials)
      .then(response => {
        if (response.data.token) {
          localStorage.setItem('token', response.data.token);
        }
        return response.data;
      });
  },
  
  /**
   * Register new user
   * @param {Object} userData - User registration data
   * @returns {Promise} Promise with registered user
   */
  register(userData) {
    return api.post('/auth/register', userData);
  },
  
  /**
   * Logout user and remove token from local storage
   */
  logout() {
    localStorage.removeItem('token');
  },
  
  /**
   * Check if user is authenticated
   * @returns {Boolean} True if user is authenticated
   */
  isAuthenticated() {
    return !!localStorage.getItem('token');
  },
  
  /**
   * Get current authentication token
   * @returns {String|null} Current token or null
   */
  getToken() {
    return localStorage.getItem('token');
  },
  
  /**
   * Initialize auth from stored token
   */
  initAuth() {
    // No need to manually set headers, the axios interceptor handles this
    return this.isAuthenticated();
  },
  
  /**
   * Request password reset
   * @param {String} email - User's email address
   * @returns {Promise} Promise with reset status
   */
  requestPasswordReset(email) {
    return api.post('/auth/forgot-password', { email });
  },
  
  /**
   * Reset password with token
   * @param {Object} resetData - Reset token and new password
   * @returns {Promise} Promise with reset status
   */
  resetPassword(resetData) {
    return api.post('/auth/reset-password', resetData);
  }
};

export default authService;