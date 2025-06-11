<!-- src/App.vue -->
<template>
  <div id="app">
     <HomePage>
      <AppSidebar/>
      <MainScreen />
      <AppFooter />
     </HomePage>
    <main class="main-content">
      <router-view /> 
    </main>
  </div>
</template>

<script>
import HomePage from './components/HomePage.vue'
import AppSidebar from './components/AppSidebar.vue'
import MainScreen from './components/MainScreen.vue'
import AppFooter from './components/AppFooter.vue'


export default {
  name: 'App',
  components: { HomePage,
    AppSidebar,
    MainScreen,
    AppFooter

   }
}
</script>

<style>
#app {
  display: flex;
}

</style>
