import { createApp } from 'vue';
import { createPinia } from 'pinia';
import { Quasar } from 'quasar';

// Import Quasar CSS
import 'quasar/src/css/index.sass';

// Import icon libraries
import '@quasar/extras/material-icons/material-icons.css';

// Import app CSS
import './css/app.scss';

// Import app root component
import App from './App.vue';
import router from './router';

// Create app instance
const app = createApp(App);

// Configure Pinia
app.use(createPinia());

// Configure Quasar
app.use(Quasar, {
  plugins: {}, // import Quasar plugins individually
  config: {
    brand: {
      primary: '#5c6bc0',
      secondary: '#26a69a',
      accent: '#9c27b0',
      
      dark: '#1d1d1d',
      
      positive: '#21ba45',
      negative: '#c10015',
      info: '#31ccec',
      warning: '#f2c037'
    }
  }
});

// Configure router
app.use(router);

// Mount the app
app.mount('#app');