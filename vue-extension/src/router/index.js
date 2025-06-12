// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import HomePage     from '../components/HomePage.vue'
import AppTranslate from '../components/AppTranslate.vue'
import AppSettings  from '../components/AppSettings.vue'
import AppAccount from '../components/AppAccount.vue'
import EditPage from '@/components/EditPage.vue'

const routes = [
  { path: '/',           name: 'home',      component: HomePage    },
  { path: '/translate',  name: 'translate', component: AppTranslate },
  { path: '/settings',   name: 'settings',  component: AppSettings  },
  { path: '/account', name: 'account', component: AppAccount},
  { path: '/edit', name:'edit', component: EditPage}
]

export default createRouter({
  history: createWebHistory(),
  routes
})
