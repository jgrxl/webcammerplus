<template>
  <div class="popover-backdrop" @click.self="$emit('close')">
    <div class="popover">
      <header>
        <strong>Settings</strong>
        <button class="close-btn" @click="$emit('close')">×</button>
      </header>

      <!-- Auth0-based user info -->
      <div v-if="isAuthenticated">
        <p class="user-name">Hello, {{ user.name }}</p>
        <ul>
          <li><a href="#">Profile</a></li>
          <li><a href="#">Account</a></li>
          <li><a href="#">Notifications</a></li>
          <li><a href="#">Appearance</a></li>
        </ul>
      </div>

      <div v-else>
        <button class="btn btn-login" @click="openLogin">
          Login
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuth0 } from '@auth0/auth0-vue'
// import { ref } from 'vue'

// Local state to track modal sub-mode if needed
const { isAuthenticated, user, loginWithRedirect } = useAuth0()

// If you need to re-open the AccountModal for choosing connection
// const isLoginMode = ref(true)

function openLogin() {
  // Trigger Auth0 Universal Login
  loginWithRedirect({ screen_hint: 'login' })
}
</script>

<style scoped>
.popover-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: calc(100vw - 100px);
  height: 100vh;
  background: rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: flex-end;
  align-items: flex-start;
  padding: 1rem;
  z-index: 1000;
}

.popover {
  background: #fff;
  border-radius: 0.5rem;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.2);
  width: 200px;
  overflow: hidden;
  margin-top: 3rem;
}

.popover header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 1rem;
  background: #fafafa;
  border-bottom: 1px solid #eee;
}

.popover .close-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
}

.popover .user-name {
  margin: 1rem;
  font-weight: 500;
}

.popover ul {
  list-style: none;
  margin: 0;
  padding: 0.5rem 0;
}

.popover ul li a {
  display: block;
  padding: 0.5rem 1rem;
  color: #333;
  text-decoration: none;
}

.popover ul li a:hover {
  background: #f0f0f0;
}

.btn-login {
  display: block;
  width: calc(100% - 2rem);
  margin: 1rem;
  padding: 0.5rem;
  background: #5c2dfd;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  text-align: center;
}

.btn-login:hover {
  background: #4a1cb0;
}
</style>
