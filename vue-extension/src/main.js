import { createApp } from 'vue'
import App from './App.vue'
import router from './router';
import { createAuth0 } from '@auth0/auth0-vue';

createApp(App)
.use(router)
.use(createAuth0({
    domain: "dev-4xh5xi1xfh7w7y2n.us.auth0.com",
    clientId: "57sIYSODLSDddlyQVokooAFjTEHDNRYo",
    authorizationParams: {
      redirect_uri: window.location.origin
    }
  }))
.mount('#app')
