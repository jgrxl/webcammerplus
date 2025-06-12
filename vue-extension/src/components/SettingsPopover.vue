<template>
  <!-- backdrop covers from the right edge of your sidebar to the window edge -->
  <div class="popover-backdrop" @click.self="$emit('close')">
    <div class="popover">
      <header>
        <strong>Settings</strong>
        <button class="close-btn" @click="$emit('close')">×</button>
      </header>

      <div v-if="!isLoggedIn">
        <button>Login</button>
      </div>

      <div v-else>
        <ul>
          <li><a href="#">Profile</a></li>
          <li><a href="#">Account</a></li>
          <li><a href="#">Notifications</a></li>
          <li><a href="#">Appearance</a></li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SettingsPopover',
  data() {
    return {
      isLoggedIn: false
    }
  }
}
</script>

<style scoped>
.popover-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  width: calc(100vw - 100px); /* stops at sidebar’s right edge */
  height: 100vh;
  background: rgba(0, 0, 0, 0.1);

  display: flex;
  justify-content: flex-end;  /* push popover to the right */
  align-items: flex-start;    /* pin to the top, not bottom */
  padding: 1rem;
  z-index: 1000;
}

.popover {
  background: #fff;
  border-radius: 0.5rem;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.2);
  width: 200px;
  overflow: hidden;
  margin-top: 3rem;           /* drop it below your gear icon */
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
</style>
