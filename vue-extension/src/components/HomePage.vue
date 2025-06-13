<template>
  <section>
    <!-- Show personalized greeting if logged in -->
    <h1 v-if="isAuthenticated">Welcome {{ user.name }}!</h1>
    <!-- Fallback for guests -->
    <h1 v-else>Welcome!</h1>

    <!-- This is the slot: anything you wrap inside <HomePage>…</HomePage> in App.vue
         will get injected right here. -->
    <slot></slot>
  </section>
</template>

<script setup>
import { useAuth0 } from '@auth0/auth0-vue'

// grab auth state
const { isAuthenticated, user } = useAuth0()
</script>

<style scoped>
/* Add any home-page specific styling here */
section {
  padding: 2rem;
  text-align: center;
}
</style>
