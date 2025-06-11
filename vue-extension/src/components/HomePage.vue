<template>
    <section>
      <h1>Welcome Home!</h1>
  
      <!-- This is the slot: anything you wrap inside <HomePage>…</HomePage> in App.vue
           will get injected right here. -->
      <slot></slot>
    </section>
  </template>
  
  <script>
  export default {
    name: 'HomePage'
  }
  </script>
  