<!-- src/components/AccountModal.vue -->
<template>
    <div class="modal-backdrop" @click.self="$emit('close')">
      <div class="modal-container">
        <button class="close-btn" @click="$emit('close')">×</button>
        <div class="logo"><!-- your logo SVG or <img> here --></div>
        <h2>Log in</h2>
        <button class="btn btn-google">
          <span class="icon">G</span>
          Continue with Google
        </button>
        <button class="btn btn-apple">
          <span class="icon"></span>
          Continue with Apple
        </button>
        <button class="btn btn-phone">
          <span class="icon">📱</span>
          Continue with Phone
        </button>
        <p class="create">
          Don’t have an account?
          <a href="/signup" @click="$emit('close')">Create an account</a>
        </p>
        <p class="small">
          🔒 Your data is never shared. No spam messages.
        </p>
        <p class="tiny">
          By continuing, you agree to the
          <a href="/privacy" @click="$emit('close')">Privacy Policy</a> &
          <a href="/terms" @click="$emit('close')">Terms of Use</a>
        </p>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: "AccountModal",
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
    background: white;
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
    /* put your logo styles here */
  }
  .modal-container h2 {
    margin-bottom: 1rem;
  }
  .btn {
    display: flex;
    align-items: center;
    width: 100%;
    padding: .5rem;
    margin: .5rem 0;
    border-radius: 4px;
    font-weight: 500;
    cursor: pointer;
    border: none;
  }
  .btn .icon {
    margin-right: .5rem;
    font-size: 1.2rem;
  }
  /* you can refine these colors to match your branding */
  .btn-google {
    background: #5c2dfd;
    color: white;
  }
  .btn-apple {
    background: white;
    border: 1px solid #ccc;
    color: #000;
  }
  .btn-phone {
    background: white;
    border: 1px solid #ccc;
    color: #000;
  }
  .create {
    margin: 1rem 0 .5rem;
  }
  .create a {
    color: #5c2dfd;
    text-decoration: none;
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
  