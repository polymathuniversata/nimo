import { boot } from 'quasar/wrappers';
import axios from 'axios';

// Create a custom axios instance
const api = axios.create({
  baseURL: process.env.API_URL || 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  timeout: 10000 // 10 seconds
});

// Request interceptor
api.interceptors.request.use(
  config => {
    // Get token from localStorage
    const token = localStorage.getItem('token');
    
    // If token exists, add to headers
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  response => {
    return response;
  },
  error => {
    // Handle authentication errors
    if (error.response && error.response.status === 401) {
      // Clear local auth data
      localStorage.removeItem('token');
      
      // Get current location
      const currentPath = window.location.pathname;
      
      // Only redirect to login if not already there
      if (!currentPath.includes('/auth/login')) {
        window.location.href = '/auth/login';
      }
    }
    
    return Promise.reject(error);
  }
);

export default boot(({ app, router }) => {
  // Set axios instance as a global property
  app.config.globalProperties.$axios = axios;
  
  // Set API instance as a global property
  app.config.globalProperties.$api = api;
  
  // Route navigation guard for authentication
  router.beforeEach((to, from, next) => {
    const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
    const isAuthenticated = localStorage.getItem('token') !== null;
    
    if (requiresAuth && !isAuthenticated) {
      next('/auth/login');
    } else {
      next();
    }
  });
});

export { api };