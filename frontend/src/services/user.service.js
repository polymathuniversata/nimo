import { api } from '../boot/axios';

const userService = {
  /**
   * Get current user profile
   * @returns {Promise} Promise with user profile
   */
  getUserProfile() {
    return api.get('/users/profile');
  },
  
  /**
   * Update user profile
   * @param {Object} profileData - User profile data to update
   * @returns {Promise} Promise with updated profile
   */
  updateUserProfile(profileData) {
    const formData = new FormData();
    
    // Add text fields
    Object.keys(profileData).forEach(key => {
      if (key !== 'profile_image' && profileData[key] !== null) {
        formData.append(key, profileData[key]);
      }
    });
    
    // Add profile image if any
    if (profileData.profile_image && profileData.profile_image instanceof File) {
      formData.append('profile_image', profileData.profile_image);
    }
    
    return api.put('/users/profile', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
  },
  
  /**
   * Get user's skills
   * @returns {Promise} Promise with user skills
   */
  getUserSkills() {
    return api.get('/users/skills');
  },
  
  /**
   * Add a new skill to user profile
   * @param {Object} skillData - Skill data to add
   * @returns {Promise} Promise with added skill
   */
  addUserSkill(skillData) {
    return api.post('/users/skills', skillData);
  },
  
  /**
   * Get user's activity feed
   * @param {Number} limit - Limit the number of results
   * @param {Number} offset - Offset for pagination
   * @returns {Promise} Promise with activity feed
   */
  getActivityFeed(limit = 10, offset = 0) {
    return api.get('/users/activity', {
      params: { limit, offset }
    });
  },
  
  /**
   * Get user's public profile by ID
   * @param {Number|String} userId - The user ID
   * @returns {Promise} Promise with user's public profile
   */
  getPublicProfile(userId) {
    return api.get(`/users/${userId}/public`);
  }
};

export default userService;