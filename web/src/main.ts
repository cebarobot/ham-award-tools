import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { createI18n } from 'vue-i18n'
import { createRouter, createWebHashHistory } from 'vue-router'
import App from './App.vue'
import './style.css'

import zh from './locales/zh.json'
import en from './locales/en.json'
import ja from './locales/ja.json'

const i18n = createI18n({
  legacy: false,
  locale: 'zh',
  fallbackLocale: 'en',
  messages: { zh, en, ja },
})

const pinia = createPinia()

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    { path: '/', component: App },
  ],
})

const app = createApp(App)
app.use(i18n)
app.use(pinia)
app.use(router)
app.mount('#app')
