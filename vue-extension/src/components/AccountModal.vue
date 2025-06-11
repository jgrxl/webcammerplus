<template>
    <div class="modal-backdrop" @click.self="$emit('close')">
      <div class="modal-container">
        <button class="close-btn" @click="$emit('close')">×</button>
  
        <!-- Logo -->
        <div class="logo">
          <!-- Replace with your SVG or <img src="…"> -->
          <svg width="48" height="48" viewBox="0 0 24 24">
            <!-- example brain icon -->
            <path fill="url(#grad)" d="M12 2C8 2 5 5 5 9v6c0 4 3 7 7 7s7-3 7-7V9c0-4-3-7-7-7z"/>
            <defs>
              <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#ff8a00"/>
                <stop offset="100%" stop-color="#e52e71"/>
              </linearGradient>
            </defs>
          </svg>
        </div>
  
        <!-- Title & subtitle -->
        <h2>{{ isLogin ? 'Log in' : 'Welcome' }}</h2>
        <p v-if="!isLogin" class="subtitle">
          Sign up to get <strong>30 free</strong> credits every day
        </p>
  
        <!-- OAuth buttons -->
        <button class="btn btn-google" @click="handleGoogle">
          <span class="icon">G</span>
          Continue with Google
        </button>
        <button class="btn btn-apple" @click="handleApple">
          <span class="icon"></span>
          Continue with Apple
        </button>
  
        <!-- Phone only for login -->
        <button
          v-if="isLogin"
          class="btn btn-phone"
          @click="handlePhone"
        >
          <span class="icon">📱</span>
          Continue with Phone
        </button>
  
        <!-- toggle link -->
        <p class="toggle-link">
          <span v-if="isLogin">
            Don’t have an account?
            <a @click.prevent="toggleMode">Create an account</a>
          </span>
          <span v-else>
            Already have an account?
            <a @click.prevent="toggleMode">Log in</a>
          </span>
        </p>
  
        <!-- legal disclaimers -->
        <p class="small">🔒 Your data is never shared. No spam messages.</p>
        <p class="tiny">
          By continuing, you agree to the
          <a href="/privacy" @click="$emit('close')">Privacy Policy</a>
          &amp;
          <a href="/terms" @click="$emit('close')">Terms of Use</a>
        </p>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: "AccountModal",
    data() {
      return {
        isLogin: true,
      };
    },
    methods: {
      toggleMode() {
        this.isLogin = !this.isLogin;
      },
      handleGoogle() {
        if (this.isLogin) {
          // TODO: login with Google
          console.log("Google login");
        } else {
          // TODO: signup with Google
          console.log("Google signup");
        }
      },
      handleApple() {
        if (this.isLogin) {
          // TODO: login with Apple
          console.log("Apple login");
        } else {
          // TODO: signup with Apple
          console.log("Apple signup");
        }
      },
      handlePhone() {
        // TODO: phone login flow
        console.log("Phone login");
      },
    },
  };
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
  