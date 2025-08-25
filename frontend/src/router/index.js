import { createRouter, createMemoryHistory, createWebHistory } from 'vue-router';
import routes from './routes';

export default createRouter({
  scrollBehavior: () => ({ left: 0, top: 0 }),
  routes,
  
  // Use web history for clean URLs (requires server configuration)
  history: process.env.SERVER
    ? createMemoryHistory(process.env.VUE_ROUTER_BASE)
    : createWebHistory(process.env.VUE_ROUTER_BASE)
});