import { api } from '../boot/axios';
import authService from './auth.service';
import userService from './user.service';
import contributionService from './contribution.service';
import tokenService from './token.service';
import bondService from './bond.service';

// Initialize auth on app start
authService.initAuth();

// Export all services
export {
  api, // Export api instance for direct use
  authService,
  userService,
  contributionService,
  tokenService,
  bondService
};