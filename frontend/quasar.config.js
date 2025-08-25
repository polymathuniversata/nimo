/*
 * This file runs in a Node context (it's NOT transpiled by Babel), so use only
 * the ES6 features that are supported by your Node version.
 */

const { configure } = require('@quasar/app-webpack');

module.exports = configure(function (ctx) {
  return {
    supportTS: false,
    boot: [
      'axios',
      'wallet',
    ],
    css: [
      'app.scss'
    ],
    extras: [
      'roboto-font',
      'material-icons',
    ],
    build: {
      vueRouterMode: 'history',
      chainWebpack(chain) {
        chain.plugin('eslint-webpack-plugin')
          .use(require('eslint-webpack-plugin'), [{ extensions: ['js', 'vue'] }]);
      },
    },
    devServer: {
      server: {
        type: 'http'
      },
      port: 9000,
      open: true,
      proxy: {
        '/api': {
          target: 'http://localhost:5000',
          changeOrigin: true,
          secure: false,
          logLevel: 'debug'
        }
      }
    },
    framework: {
      config: {},
      plugins: [
        'Notify',
        'Dialog',
        'Loading',
      ]
    },
    animations: [],
    ssr: {
      pwa: false,
      prodPort: 3000,
      middlewares: [
        'render'
      ]
    },
    pwa: {
      workboxPluginMode: 'GenerateSW',
      workboxOptions: {},
      manifest: {
        name: 'Nimo Platform',
        short_name: 'Nimo',
        description: 'Decentralized Youth Identity & Proof of Contribution Network',
        display: 'standalone',
        orientation: 'portrait',
        background_color: '#ffffff',
        theme_color: '#027be3',
        icons: [
          {
            src: 'icons/icon-128x128.png',
            sizes: '128x128',
            type: 'image/png'
          },
          {
            src: 'icons/icon-192x192.png',
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: 'icons/icon-256x256.png',
            sizes: '256x256',
            type: 'image/png'
          },
          {
            src: 'icons/icon-384x384.png',
            sizes: '384x384',
            type: 'image/png'
          },
          {
            src: 'icons/icon-512x512.png',
            sizes: '512x512',
            type: 'image/png'
          }
        ]
      }
    },
    cordova: {},
    capacitor: {
      hideSplashscreen: true
    },
    electron: {
      bundler: 'packager',
      packager: {},
      builder: {
        appId: 'com.nimo.app'
      }
    }
  };
});