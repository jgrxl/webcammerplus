<!-- src/components/AppFooter.vue -->
<template>
  <div class="app-footer">
    <!-- only show when not logged in -->
    <span
      v-if="!isAuthenticated"
      class="login-text"
      @click="showModal = true"
    >
      Login
    </span>

    <span class="help-icon" @click="handleHelp">?</span>
    <span class="feedback-icon" @click="handleFeedback">📝</span>

    <!-- account modal -->
    <AccountModal
      v-if="showModal"
      @close="showModal = false"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import AccountModal from './AccountModal.vue'
import { useAuth0 } from '@auth0/auth0-vue'

const showModal = ref(false)
const { isAuthenticated } = useAuth0()

function handleHelp() {
  window.location.href = 'https://jovanrlee.github.io/webcammerplus/index.html#support'
}

function handleFeedback() {
  window.location.href = 'https://jovanrlee.github.io/webcammerplus/index.html#support'
}
</script>

<style scoped>
.app-footer {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1rem;
  position: relative;
}
.login-text {
  color: #ff6b6b;
  cursor: pointer;
  transition: color .2s;
}
.login-text:hover {
  color: #ff4b4b;
  text-decoration: underline;
}
.help-icon,
.feedback-icon {
  margin: 0 1rem;
  font-size: 1.25rem;
  color: #777;
  cursor: pointer;
  transition: color .2s;
}
.help-icon:hover,
.feedback-icon:hover {
  color: #333;
}
</style>
