<template>
  <aside class="sidebar">
    <nav>
      <ul>
        <!-- top section -->
        <li><router-link to="/">🏠 Home</router-link></li>
        <li><router-link to="/translate">🌐 Translate</router-link></li>
        <li><router-link to="/">🖊️ Edit</router-link></li>
        <li><router-link to="/">❓ Help</router-link></li>

        <!-- bottom-pinned -->
        <li class="bottom">
          <button @click="$emit('open-settings')" class="settings-btn">
            ⚙️
          </button>
        </li>
      </ul>
    </nav>
  </aside>
</template>

<script setup>
import { useAuth0 } from '@auth0/auth0-vue'

// Destructure inside setup — these are refs, so use .value in JS,
// but in the template Vue unwraps them automatically.
const { isAuthenticated, user  } = useAuth0()

// Optional: debug in console
console.log('logged in?', isAuthenticated.value)
console.log('user profile', user.value)
</script>

<style scoped>
.sidebar {
  position: fixed;
  top: 0;
  right: 0;
  height: 100vh;
  width: 100px;
  background: #f5f5f5;
  box-shadow: -2px 0 6px rgba(0,0,0,0.1);
  padding: 1rem 0;

  display: flex;
  flex-direction: column;
}

/* nav fills all available space */
.sidebar nav {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin: 0;
  padding: 0;
}

/* UL spans full height and stacks items */
.sidebar nav ul {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin: 0;
  padding: 0;
  list-style: none;
}

/* all links centered */
.sidebar nav ul li {
  text-align: center;
  margin: 0.75rem 0;
}

/* push this one to the bottom */
.sidebar nav ul li.bottom {
  margin-top: auto;
}
</style>
