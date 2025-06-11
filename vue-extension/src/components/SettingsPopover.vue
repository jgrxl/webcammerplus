<template>
  <!-- backdrop covers only up to the sidebar’s left edge -->
  <div class="popover-backdrop" @click.self="$emit('close')">
    <div class="popover">
      <header>
        <strong>Settings</strong>
        <button class="close-btn" @click="$emit('close')">×</button>
      </header>
      <ul>
        <li><a href="#">Profile</a></li>
        <li><a href="#">Account</a></li>
        <li><a href="#">Notifications</a></li>
        <li><a href="#">Appearance</a></li>
      </ul>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SettingsPopover'
}
</script>

<style scoped>
.popover-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  /* STOP the backdrop at the sidebar’s left edge (100px in your layout) */
  width: calc(100vw - 100px);
  height: 100vh;
  background: rgba(0, 0, 0, 0.1);

  /* flex container so we can align the popover */
  display: flex;
  justify-content: flex-end; /* push popover to the right edge of the backdrop */
  align-items: flex-end;     /* push popover to the bottom of the backdrop */

  /* give a little room so the popover isn’t flush against the screen edge */
  padding: 1rem;
  z-index: 1000;
}

.popover {
  background: #fff;
  border-radius: 0.5rem;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.2);
  width: 200px;
  overflow: hidden;
}

/* header with close button */
.popover header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  background: #fafafa;
  border-bottom: 1px solid #eee;
}

.popover .close-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
}

/* list of settings */
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
