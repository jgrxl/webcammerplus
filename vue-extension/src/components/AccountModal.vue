<template>
  <div class="modal-backdrop" @click.self="$emit('close')">
    <div class="modal-container">
      <button class="close-btn" @click="$emit('close')">×</button>
      <div class="logo">
        <!-- … your SVG or <img> … -->
      </div>
      <h2>{{ isLogin ? 'Log in' : 'Sign up' }}</h2>
      <p v-if="!isLogin" class="subtitle">
        Sign up to get <strong>30 free</strong> credits every day
      </p>
      
      <!-- Auth0 buttons -->
      <button class="btn btn-google" @click="handleAuth('google-oauth2')">
        <span class="icon">G</span>
        {{ isLogin ? 'Log in' : 'Sign up' }} with Google
      </button>
      <button class="btn btn-apple" @click="handleAuth('apple')">
        <span class="icon"></span>
        {{ isLogin ? 'Log in' : 'Sign up' }} with Apple
      </button>
      <button
        v-if="isLogin"
        class="btn btn-phone"
        @click="handleAuth('sms')"
      >
        <span class="icon">📱</span>
        Continue with Phone
      </button>
      
      <p class="toggle-link">
        <span v-if="isLogin">
          Don’t have an account?
          <a @click.prevent="toggleMode">Create one</a>
        </span>
        <span v-else>
          Already have an account?
          <a @click.prevent="toggleMode">Log in</a>
        </span>
      </p>
      
      <p class="small">🔒 Your data is never shared. No spam.</p>
      <p class="tiny">
        By continuing, you agree to our
        <a href="/privacy" @click="$emit('close')">Privacy Policy</a>
        &amp;
        <a href="/terms" @click="$emit('close')">Terms of Use</a>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuth0 } from '@auth0/auth0-vue'
// import { emit } from 'vue'

// local state
const isLogin = ref(true)

// pull the Auth0 methods we need
const { loginWithRedirect } = useAuth0()

function toggleMode() {
  isLogin.value = !isLogin.value
}

function handleAuth(connection) {
  loginWithRedirect({
    connection,
    screen_hint: isLogin.value ? 'login' : 'signup'
  })
}
</script>
  
  <style scoped>
  .modal-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }
  .modal-container {
    background: #fff;
    border-radius: 8px;
    padding: 1.5rem;
    width: 320px;
    text-align: center;
    position: relative;
  }
  .close-btn {
    position: absolute;
    top: .5rem;
    right: .5rem;
    background: transparent;
    border: none;
    font-size: 1.25rem;
    cursor: pointer;
  }
  .logo {
    margin-bottom: 1rem;
  }
  h2 {
    margin: 0;
    font-size: 1.5rem;
  }
  .subtitle {
    margin: .5rem 0 1rem;
    font-size: .95rem;
    color: #555;
  }
  
  .btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    padding: .5rem;
    margin: .4rem 0;
    border-radius: 4px;
    font-weight: 500;
    cursor: pointer;
    border: none;
  }
  .btn .icon {
    margin-right: .5rem;
    font-size: 1.2rem;
  }
  .btn-google {
    background: #5c2dfd;
    color: #fff;
  }
  .btn-apple,
  .btn-phone {
    background: #fff;
    border: 1px solid #ccc;
    color: #000;
  }
  
  .toggle-link {
    margin: 1rem 0 .5rem;
  }
  .toggle-link a {
    color: #5c2dfd;
    cursor: pointer;
    text-decoration: none;
  }
  .toggle-link a:hover {
    text-decoration: underline;
  }
  
  .small {
    font-size: .85rem;
    margin-bottom: .25rem;
  }
  .tiny {
    font-size: .75rem;
    color: #666;
  }
  .tiny a {
    color: #5c2dfd;
    text-decoration: none;
  }
  </style>
  