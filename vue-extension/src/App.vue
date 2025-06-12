<template>
  <div id="app" class="layout">
    <main class="main-content">
      <router-view />
    </main>

    <AppSidebar @open-settings="openSettings" />
  </div>


  <div style="position: fixed; bottom: 10px; left: 10px; background: white; padding: 4px; border: 1px solid red;">
    showSettings = {{ showSettings }}
  </div>

  <SettingsPopover 
    v-if="showSettings" 
    @close="showSettings = false" 
  />

  <AppFooter>
  <AccountModal />
</AppFooter>
</template>

<script>
import AppSidebar      from './components/AppSidebar.vue'
import SettingsPopover from './components/SettingsPopover.vue'
import AppFooter       from './components/AppFooter.vue'
import AccountModal    from './components/AccountModal.vue'

export default {
  components: { AppSidebar, SettingsPopover, AppFooter, AccountModal },
  data() {
    return { showSettings: false }
  },
  methods: {
    openSettings() {
      console.log('openSettings()')
      this.showSettings = true
    },
    closeSettings() {
      console.log('closeSettings()')
      this.showSettings = false
    }
  }
}
</script>

<style>
.layout {
  display: flex;
  height: 90vh;
  overflow: hidden;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
  background: #fff;
}

/* Popover styling lives in SettingsPopover.vue */
</style>
