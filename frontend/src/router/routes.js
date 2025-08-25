const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('pages/IndexPage.vue') },
      { 
        path: 'profile', 
        component: () => import('pages/ProfilePage.vue'),
        meta: { requiresAuth: true }
      },
      { 
        path: 'contributions', 
        component: () => import('pages/ContributionsPage.vue'),
        meta: { requiresAuth: true }
      },
      { 
        path: 'tokens', 
        component: () => import('pages/TokensPage.vue'),
        meta: { requiresAuth: true }
      },
      { 
        path: 'bonds', 
        component: () => import('pages/BondsPage.vue'),
        meta: { requiresAuth: true }
      },
    ],
  },
  {
    path: '/auth',
    component: () => import('layouts/AuthLayout.vue'),
    children: [
      { path: 'login', component: () => import('pages/auth/LoginPage.vue') },
      { path: 'register', component: () => import('pages/auth/RegisterPage.vue') },
    ],
  },
  
  // Always leave this as last one
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue'),
  },
];

export default routes;